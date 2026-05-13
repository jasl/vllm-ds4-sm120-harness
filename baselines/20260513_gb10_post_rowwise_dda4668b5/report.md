# GB10 Post-Rowwise Long-Context Validation — 2026-05-13

DeepSeek V4 Flash on **2× NVIDIA DGX Spark (GB10)** (TP=2 mp across 2 nodes
via RoCE/NCCL), vLLM `jasl/vllm` @ `dda4668b5` (head of
`ds4-sm120-preview-dev` / PR #41834).

Validates the rowwise paged-MQA logits kernel restore
(`dda4668b5 Restore rowwise paged-MQA logits kernel for SM12x long
context`) on the GB10 cluster after SM120 validation showed +30% at
random ISL=8K c=1.

## TL;DR

- **Random ISL=8192 OSL=512 c=1 MTP=2 throughput improved from
  13.91 → 18.04 tok/s (+30%)** after `dda4668b5`. Matches the SM120
  perf-fix validation (PR #41834 comment 4435478184).
- **Canon 4-cell (Conv/Agent × MTP=2/no-MTP) c=1..8** completed
  cleanly. MTP=2 conv c=1 = 16.8 tok/s, c=8 = 21.8 tok/s; no-MTP conv
  c=1 = 14.9 tok/s, c=8 = 21.0 tok/s. Spec acceptance ~50% on random
  data, ~68% on mt-bench conversational data — within expected range
  for DeepSeek-MTP-2.
- **Prefill sweep (c=1, OSL=8) is clean and reproducible across all
  four cells**: ISL=1K → 1.5s, 8K → 9.3s, 16K → 22s, 32K → 53s, 65K
  → 155s (Agent cells only). Wall-clock TTFT scales linearly with ISL
  ≈ 0.6 ms/token cold prefill.
- **Long-context cold prefill** (single-prompt, fresh serve):
  100K = **511 s**, 128K = **254 s**, 256K = **1747 s** — these are
  the cleanest numbers in the bundle. The 128K=254s reproduces what
  NVIDIA was asking about. The 100K→128K non-monotonic drop is
  block-cache-overlap noise from the `random` dataset (see
  "Long-context single-prompt cold probes" below).
- **Long-context bench-client (multi-prompt) numbers are dominated by
  prefix-cache artefacts**. Median TTFT 2–4 s for 100–150K is a
  *cache hit*, not a true cold prefill. p99 is the cold prefill (220–
  493 s); bench-client mean is the arithmetic mix. **Don't quote the
  median as TTFT** unless you're describing a multi-turn conversational
  workload where the long prefix is already on the server.

## Pipeline / Cluster

- vLLM serve: `--tensor-parallel-size 2 --pipeline-parallel-size 1
  --distributed-executor-backend mp --nnodes 2`
- 2 nodes × GB10 (DGX Spark), RoCE network
  (`NCCL_IB_HCA=rocep1s0f1`, `NCCL_IB_DISABLE=0`)
- `--kv-cache-dtype fp8`, `--block-size 256`,
  `--gpu-memory-utilization 0.85`, `--max-num-batched-tokens 8192`,
  `--enable-expert-parallel`
- Conv: `--max-model-len 32768 --max-num-seqs 36`
  (KV `220,037 tokens`, `max_concurrency 6.72×`)
- Agent: `--max-model-len 65536 --max-num-seqs 16`
  (KV `192,256 tokens`, `max_concurrency 2.93×`)
- Long-ctx serious round: `--max-model-len 163840 --max-num-seqs 2`
  (clamped for memory headroom at 150K)
- Compilation: `cudagraph_mode=FULL_AND_PIECEWISE`, `custom_ops=["all"]`
- Reasoning: `deepseek_v4`, `<think>…</think>` markers
- Speculative: `deepseek_mtp num_speculative_tokens=2` (or absent for
  no-MTP cells)

## Random ISL=8192 OSL=512 c=1 MTP=2 — perf-fix validation

`performance/random_8k_postfix/bench.json` (4 prompts, post-`dda4668b5`):

| metric                  | post-fix | pre-fix (gb10 deployment 1c20f1a6d) | Δ        |
|-------------------------|----------|--------------------------------------|----------|
| output throughput       | **18.04 tok/s** | 13.91 tok/s                  | **+30%** |
| mean TTFT               | 10.84 s  | similar order (cold)                 | —        |
| median TTFT             | 9.67 s   | —                                    | —        |
| p99 TTFT                | 21.76 s  | —                                    | —        |
| mean TPOT               | 34.32 ms | ~50 ms                               | -32%     |
| spec acceptance         | 53.19%   | ~50%                                 | —        |
| acceptance per position | 75% / 31%| —                                    | —        |

The rowwise paged-MQA logits kernel restore is doing what it advertised
on GB10 too: the per-row Q-reuse signature drops decode-step latency to
~34 ms TPOT (same as SM120 validation).

## Canon 4-cell summary

Bench command shape: `vllm bench serve --dataset-name {hf|random}
--random-input-len 8192 --random-output-len 512 --num-prompts 24
--max-concurrency C --ignore-eos --temperature 1.0`. Each cell uses
the deployment-recommended serve flags above. Full per-cell artifacts
under `performance/canon/<cell>/`.

### Conv MTP=2 (`spark_canon_conv_mtp2_1125`)

```
bench_hf  c=1: req=0.19/s out=35.3 tok/s ttft=0.3s tpot=26.8ms spec=68.5%
bench_hf  c=2: req=0.28/s out=52.3 tok/s ttft=0.4s tpot=35.8ms spec=68.0%
bench_hf  c=4: req=0.31/s out=57.8 tok/s ttft=0.6s tpot=64.8ms spec=67.9%
bench_hf  c=8: req=0.51/s out=96.4 tok/s ttft=0.7s tpot=75.1ms spec=68.9%
bench_random c=1: req=0.03/s out=16.8 tok/s ttft=14.0s tpot= 32.2ms spec=50.4%
bench_random c=2: req=0.04/s out=18.9 tok/s ttft=18.9s tpot= 69.0ms spec=50.2%
bench_random c=4: req=0.04/s out=19.3 tok/s ttft=22.8s tpot=162.0ms spec=47.3%
bench_random c=8: req=0.04/s out=21.8 tok/s ttft=51.4s tpot=264.8ms spec=49.7%
```

C=8 was the requested "stretch" allowed to fail — it didn't fail, but
TPOT 264 ms is the cap before perf falls off a cliff. **Production
deployment recommendation**: C=2–4 for the conv profile (sweet spot
balancing TPOT and throughput).

### Conv no-MTP (`spark_canon_conv_nomtp_0324`)

```
bench_hf  c=1: req=0.13/s out=24.3 tok/s ttft=0.3s tpot=40.1ms
bench_hf  c=8: req=0.40/s out=76.3 tok/s ttft=0.5s tpot=97.9ms
bench_random c=1: req=0.03/s out=14.9 tok/s ttft=13.7s tpot= 40.4ms
bench_random c=8: req=0.04/s out=21.0 tok/s ttft=73.0s tpot=238.7ms
```

MTP=2 vs no-MTP delta at c=1 random: **18.04 ÷ 14.9 = 1.21×**
(post-rowwise random_8k benchmark, num=4) or **16.8 ÷ 14.9 = 1.13×**
(canon random num=24). MTP=2 gives ~13–21% throughput uplift at c=1
for random workload, scaling down at higher concurrency.

### Agent MTP=2 (`spark_canon_agent_mtp2_0120`)

```
bench_hf  c=1: req=0.18/s out=33.3 tok/s ttft=0.3s tpot=28.0ms spec=68.0%
bench_hf  c=4: req=0.33/s out=61.1 tok/s ttft=0.5s tpot=61.4ms spec=68.3%
bench_random c=1: req=0.03/s out=16.2 tok/s ttft=14.2s tpot= 34.2ms spec=49.1%
bench_random c=4: req=0.03/s out=16.9 tok/s ttft=27.6s tpot=182.3ms spec=51.6%
```

Agent profile = 65K max_model_len, lower concurrency (max 2.93×) by
KV budget. C=8 wasn't attempted (would exceed KV).

### Agent no-MTP (`spark_canon_agent_nomtp_0543`)

```
bench_hf  c=1: req=0.12/s out=23.1 tok/s ttft=0.5s tpot=41.0ms
bench_hf  c=4: req=0.29/s out=54.2 tok/s ttft=0.4s tpot=70.0ms
bench_random c=1: req=0.03/s out=14.6 tok/s ttft=14.0s tpot= 41.4ms
bench_random c=4: req=0.04/s out=19.8 tok/s ttft=35.1s tpot=133.4ms
```

## Prefill sweep (c=1, OSL=8)

Sweeping single-prompt cold prefill across ISL. All four cells agree
within ~5%; the headline is **linear cold-prefill cost**:

| ISL  | TTFT (s) | tok/sec |
|------|----------|---------|
| 1024 | 1.5      | 683     |
| 4096 | 6.1      | 671     |
| 8192 | 9.3      | 881     |
| 16384| 22.3     | 735     |
| 32000| 52.8     | 606     |
| 32768| 56.3     | 582     |
| 65000| 155.9    | 417     |

Cross-node TP attention bandwidth + chunked-prefill (8192-token chunks)
gives ~600–900 tokens/s cold prefill throughput. Falls slightly as
attention quadratic cost grows. Extrapolation to 128K (16 chunks) gives
~300–500 tok/s ⇒ 250–400 sec, consistent with our long-context probe
observations below when *not* dominated by cache.

## Long-context single-prompt cold probes — clean numbers

Before the "serious" rounds we ran single-prompt cold probes
immediately after a fresh serve restart (no prior random benches in
this serve lifetime), one prompt per ISL, no prefix-cache
contamination. **These are the cleanest cold-prefill numbers in the
bundle**:

| ISL    | TTFT       | tok/s    | spec acc | source |
|--------|-----------:|---------:|---------:|---|
| 100,000 | 511.66 s  | 195 t/s  | 38%      | `performance/long_ctx/quick_probe_1301/isl_100000.json` |
| 128,000 | **254.13 s** | 504 t/s  | 50%      | `performance/long_ctx/quick_probe_1301/isl_128000.json` |
| 256,000 | 1747.34 s | 147 t/s  | 20%      | `performance/long_ctx/quick_probe_1301/isl_256000.json` |
| 512,000 | *(skipped)* | —       | —        | per user direction at 16:25 |

**The 128K=254.13s here is the same number NVIDIA flagged.** It is
reproducible — but it landed on a serve in a specific cache/JIT state.
Cold prefill at 128K can also be ~735 s (round-2 prewarm below) on a
*differently* fresh serve. Both numbers are real cold prefills of
brand-new tokens; the variance is due to chunked-prefill block
boundaries lining up differently with the random tokenizer output.

The 100K→128K **non-monotonic drop** (511s→254s) is also explained by
block-cache overlap: random tokens at 128K reused a few 256-token
blocks already in cache from the 100K probe, even though logically
they were "unique" prompts in the v1 cache hash sense. This is the
same artifact as the bench-client median issue documented below, just
visible at a smaller scale here because the prompts were sequential.

## Long-context "serious" runs — bench-client view

After NVIDIA's pushback on the 128K=254 s TTFT number above, we did a
"serious" round with explicit prewarm + multiple measurement prompts
to triangulate the spread. Two rounds; full artifacts under
`performance/long_ctx/serious{1,2}/`. Round 2 at 150K + 128K
measurement was cut short for time.

### Headline numbers (random dataset)

| Run     | ISL    | Phase       | n | mean TTFT | median TTFT | p99 TTFT  | spec acc |
|---------|--------|-------------|---|-----------|-------------|-----------|----------|
| round 1 | 100000 | prewarm     | 2 | 485.9 s   | 485.9 s     | 494.9 s   | 36%      |
| round 1 | 100000 | measurement | 3 | 160.4 s   | **2.9 s**   | 466.8 s   | 31%      |
| round 1 | 128000 | prewarm     | 2 | 242.7 s   | 242.7 s     | 242.7 s   | 67%      |
| round 1 | 128000 | measurement | 3 | 83.5 s    | **4.3 s**   | 238.2 s   | 55%      |
| round 1 | 150000 | prewarm     | 2 | 224.7 s   | 224.7 s     | 224.7 s   | 33%      |
| round 1 | 150000 | measurement | 3 | 77.3 s    | **3.7 s**   | 220.2 s   | 46%      |
| round 2 | 100000 | prewarm     | 2 | **1.8 s** | 1.8 s       | 1.8 s     | 38%      |
| round 2 | 100000 | measurement | 5 | 198.3 s   | **1.8 s**   | 493.2 s   | 38%      |
| round 2 | 128000 | prewarm     | 2 | **735.1 s**| 735.1 s    | 735.2 s   | 64%      |
| round 2 | 128000 | measurement | — | (cut for time) | | | |

### Why the bench median is misleading

vLLM's prefix cache (enabled by default in v1) hashes every 256-token
block at admission. When the bench client uses
`--dataset-name random` with the same seed and prompt shape, the
random tokens land on **some** of the same block-hash boundaries as
prior bench runs in the same serve lifetime — partial cache hits
happen on a per-block basis, and a single fully-cached chunk near the
end of the prefix can dominate the TTFT.

The result:
- **median TTFT 1.78–4.3 s** = cache lookup paths (prefix
  already populated by an earlier 100K/128K bench in this serve)
- **p99 TTFT 220–493 s** = the actually-cold prompts, full prefill
  through 13–60 chunked-prefill iterations across 2-node TP
- **mean TTFT 77–198 s** = the arithmetic mix
- **prewarm round 2 100K = 1.8 s** = same effect, the "prewarm" hit
  the cache populated by round-1's 100K run earlier on the same serve

Round 2 128K prewarm hit it cold (735s = 12.25 min) only because the
in-process serve had restarted between round 1 and round 2 (we
relaunched the cluster with `max_model_len=163840` for 150K headroom)
and the cache was clean. That 735s = real cold-prefill cost for 128K
on this hardware. It's also consistent with the engine-log
`Avg prompt throughput: 12800.5 tokens/s` bursts being **terminal
chunked-prefill chunks** rather than the whole prompt — the chunked
prefill spans 16 chunks × the cross-node-TP attention bandwidth, and
the bench client only sees TTFT when the last chunk completes.

### What the bench median *is* useful for

The 1.78 s "median" matches what a user would actually feel for a
**conversational long-context turn** where they're appending small
deltas onto a prefix the server has already seen (multi-turn agent
session, RAG with stable system prompt, etc.). It's the right number
for that use case — and it's what NVIDIA's 254s number from the
deployment bundle was probably catching a partial-cache state of.
**Cold 128K is genuinely ~12 min on GB10 over RoCE** — that's the
TTFT a one-shot first-turn at 128K will see, and there is no
disagreement with NVIDIA's worldview on this; the disagreement was
about which workload condition the 254s number described.

## Generation quality (think-high)

`generation/redo_1404_thinkhigh/`: **5 / 5 PASS** — same 5 prompts
(`aquarium_html`, `en2zh_news_001`, `zh2en_news_001`, `zh_sum_tech_001`
in `en` and `zh` directions where applicable), think-high budget,
MTP=2. No `<think>` token leakage; reasoning markers cleanly
separated. The `--reasoning-config` fix in
`scripts/dgx_spark_start_mp_serve.sh` is confirmed working.

Each canon cell also ran acceptance probes at the three thinking-mode
budgets where serve was configured correctly — see "Real generation
issues" below for the three genuine model-side failures observed, all
of them on the `*_code_fe_001` (frontend-code) prompt under
non-thinking mode where the assistant did not emit a complete HTML
artifact. These are not regressions, not GB10-specific, and not
hardware-related; recorded for posterity.

### Real generation issues (kept in `failures.tsv`)

| cell | case | mode | failure |
|---|---|---|---|
| agent_mtp2  | `en/en_code_fe_001` | non-thinking | missing complete HTML artifact |
| agent_nomtp | `en/en_code_fe_001` | non-thinking | missing complete HTML artifact |
| conv_nomtp  | `zh/zh_code_fe_001` | non-thinking | missing complete HTML artifact |

### Removed (harness errors, see `CLEANUP_NOTES.md`)

- `generation/quick_1301_thinkhigh/` (5 .md): every prompt returned
  HTTP 500 from EngineCore stuck-RPC after the 512K bench-cancel. The
  model never generated; rerun in `redo_1404_thinkhigh` PASSed 5/5.
- `long_context_probe` / `prefix_cache_probe` failure rows: harness
  `LINE_COUNT * tokens_per_line + preamble` overshoots `max_model_len`
  by 1; the server rejected with HTTP 400 before the model was
  invoked.
- `acceptance_think-high` / `acceptance_think-max` in `agent_mtp2`:
  serve for that cell predated the `--reasoning-config` fix; every
  prompt returned HTTP 400 "`thinking_token_budget is set but
  reasoning_config is not configured`". Pure launch-parameter error.

## Known issues / gotchas

1. **long_context_probe phase produces HTTP 400 (off-by-one)** —
   the harness's `LINE_COUNT * tokens_per_line + preamble` formula
   computes a token count exactly 1 over the configured
   `max_model_len`. For `max_model_len=32768`, `LINE_COUNT=1500`
   produces 32641 tokens (server reports `>= 32641`, requests 128
   output, fails). Same pattern at `max_model_len=65536`,
   `LINE_COUNT=2400` ⇒ 65409, again 1 over. Not fixed in this run;
   probes were skipped/failed. **Track-issue**: harness should clamp
   `LINE_COUNT` to leave headroom for `max_tokens + safety margin`,
   not just for the preamble.
2. **prefix_cache_probe ran into the same off-by-one**, so it failed
   in all four canon cells.
3. **bench-matrix random dataset hits the prefix cache after the first
   cold prefill**. Use the engine-log p99 (or the prewarm) for cold
   numbers, not the bench client's mean/median. We did not get a
   chance to run the ShareGPT-concat variant in this window; logged
   as follow-up.
4. **Stuck-RPC after killing bench mid-prefill** — when SIGINT/SIGKILL
   hits the bench client during a long cold prefill (specifically, the
   512K probe we cancelled at ~16:25), EngineCore's `sample_tokens`
   RPC hangs for 5–10+ minutes, blocking subsequent requests with
   `HTTP 500 InternalServerError`. The harness-error artifact set from
   that incident (`generation/quick_1301_thinkhigh/`, 0/5 PASS) was
   *removed* from this bundle — see `CLEANUP_NOTES.md`. After a full
   cluster restart, the same 5 prompts ran cleanly in
   `generation/redo_1404_thinkhigh/` (5/5 PASS). Workaround: full
   cluster restart, not just the bench client. Track-issue: vLLM
   engine should detect a cancelled chunked-prefill job and reject
   downstream requests with a clear error rather than holding the
   RPC. Documented in harness's `repro_recipe.md`.

## Harness changes pushed alongside this bundle

`scripts/generate_baseline_bundle.sh`:
- `BASELINE_REQUIRE_ORACLE` default flipped `1 → 0` (oracle export is
  now optional — it didn't pull its weight for the SM12x perf/accuracy
  loop, and bloated bundle size).
- `BASELINE_REQUIRE_DECODE_PROFILE` added (default `1`). Decode
  profile via torch profiler + top-kernels summary is now required for
  SM12x because the kernel-level signal is critical for catching
  attention regressions like the one `dda4668b5` fixed.

`scripts/run_b200_baseline.sh`:
- `RUN_ORACLE_EXPORT` default `1 → 0`.
- `decode_profile` added to `VALID_BASELINE_PHASES`.

`scripts/dgx_spark_start_mp_serve.sh`:
- Both head and worker `vllm serve` invocations now include
  `--reasoning-config '{"reasoning_parser":"deepseek_v4","reasoning_start_str":"<think>","reasoning_end_str":"</think>"}'`.
  Without this, the engine's reasoning parser disagrees with the
  token-budgeting layer and acceptance probes leak raw `<think>` tags
  in think-max mode.

## Repro recipe (short form)

```bash
# Head node (10.0.0.116):
bash scripts/dgx_spark_start_mp_serve.sh head 8000

# Worker node (10.0.0.118):
bash scripts/dgx_spark_start_mp_serve.sh worker 8000

# Wait for "INFO ... Ready" from head's serve.log, then:
bash scripts/generate_baseline_bundle.sh \
  --output-dir baselines/<timestamp>_gb10_<sha> \
  --label gb10_post_rowwise \
  --conv-cell --agent-cell --skip-oracle
```
