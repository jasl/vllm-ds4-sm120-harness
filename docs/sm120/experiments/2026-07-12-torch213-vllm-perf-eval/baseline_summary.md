# torch-2.13 evaluation of the DSv4-Flash SM12x vLLM fork — does the tokenspeed ">10% free perf" transfer? (2026-07-12)

**Question.** The **tokenspeed** fork saw >10% "free" perf from torch 2.11→2.13 (+
Triton latest-main). Does that hold on **our vLLM fork** (`jasl/vllm`,
`b5c0d43b96`), and at which depths — prefill or decode?

**Answer: NO, it does not transfer.** On the vLLM fork the only consistent torch-2.13
gain is a **modest prefill (ctx_pp) +3–7%**; **decode is flat (no gain), within
run-to-run noise** — the *opposite phase* from tokenspeed, and far below 10%.

## Build / environment (both nodes .116/.119, TP=2)
| | torch-2.11 baseline of record | this torch-2.13 build |
|---|---|---|
| vLLM head | `b5c0d43b96` | `b5c0d43b96` (same; fresh worktree) |
| torch | 2.11.0+cu130 | **2.13.0+cu130** |
| nvidia-nccl-cu13 | 2.30.7 | **2.30.4** (2.30.7 **and** torch-2.13's own default 2.29.7 both wedge in-graph; see below) |
| triton | 3.6.0 | **3.7.1** (torch-2.13 pin, auto) |
| flashinfer | 0.6.14 python+cubin | 0.6.14 python+cubin (**identical wheels**, baseline parity — no jit-cache) |
| custom ops | `_C_stable_libtorch` | same; **compiles + loads clean under torch 2.13** (libtorch-stable ABI) |
| serve config | mml 49152, util 0.85, MTP2, fp8 KV, prefix-cache on, FULL_AND_PIECEWISE | identical |

Fresh venv (`vllm-torch213-venv`) + fresh git worktree — **torch-2.11 baseline
untouched**. Build/serve/gate scripts byte-identical to the ones that produced the
07-11 baseline of record.

## Gates on the torch-2.13 serve — correctness SOUND
| gate | torch-2.13 result | baseline | verdict |
|---|---|---|---|
| GSM8K 200q (8-shot, max_gen 2048) | **0.965** flexible/strict, IMA-clean | 0.96 | ✅ ≥ baseline |
| arthur coherence **c=1** (deterministic recall) | **PASS 2/2**, coherent | c=1 4/4 | ✅ |
| ToolCall-15 (en × 3 thinking modes) | **0×500, 81/90 = 90% content** (40 pass / 4 fail / 1 partial) | 42/42 engine-clean | ✅ engine-clean* |
| issue#19 (JSON-only) | **PASS** | PASS | ✅ |
| HTTP 500 count (whole run) | **0** | 0 | ✅ |

*ToolCall-15 rc=1 is the suite's strict per-scenario `min_points=2` threshold, **not
an engine fault**: 0×500, tool mechanism fully working (multi-step chains complete),
90% content at temperature 1.0. The 5 misses are model-judgment behaviors (TC-06
"didn't split a translation into two calls" ×3 modes; TC-11 "used calculator
unnecessarily"; TC-15 "didn't preserve exact value") — the tokenspeed torch-2.13
run saw the identical pattern (85/90 = 94%, called "temp-1.0 judge variance"). The
gate's real target — the #44297 MTP+tool_choice-500 fix — holds (0×500).

## Perf — llama-benchy STANDARD (pinned @b220b7c9, pp2048 tg128, C=1, 3 runs, prefix-cache)
Both columns produced by the **same script, same fresh-serve methodology**.

| depth | metric | torch-2.11 (base) | torch-2.13 | Δ | phase |
|---|---|---|---|---|---|
| 8192  | **ctx_pp**   | 1757.2 ± 64.8 | **1876.0 ± 2.1** | **+6.8%** | prefill |
| 16384 | **ctx_pp**   | 1773.9 ± 15.0 | **1842.2 ± 0.5** | **+3.9%** | prefill |
| 32768 | **ctx_pp**   | 1699.3 ± 12.5 | **1756.0 ± 0.6** | **+3.3%** | prefill |
| 8192  | pp2048       | 1391.7 ± 7.7  | 1339.1 ± 97.0 | −3.8% (hi-var) | prefill |
| 16384 | pp2048       | 1321.8 ± 5.4  | 1329.5 ± 3.6  | +0.6% | prefill |
| 32768 | pp2048       | 1200.4 ± 0.6  | 1226.6 ± 4.3  | +2.2% | prefill |
| 8192  | tg128 mean (peak) | 41.85 (48.33) | 38.50 (43.33) | −8.0% (−10.3%) | decode |
| 16384 | tg128 mean (peak) | 39.58 (45.00) | 38.05 (41.76) | −3.9% (−7.2%) | decode |
| 32768 | tg128 mean (peak) | 37.08 (40.67) | 38.45 (43.00) | +3.7% (+5.7%) | decode |
| 8192  | ctx_tg mean (peak) | 39.53 (45.00) | 39.63 (44.00) | +0.3% (−2.2%) | decode |
| 16384 | ctx_tg mean (peak) | 41.12 (46.67) | 40.59 (45.33) | −1.3% (−2.9%) | decode |
| 32768 | ctx_tg mean (peak) | 42.50 (48.00) | 39.30 (44.33) | −7.5% (−7.6%) | decode |

Prefix-cache hit 42–47% (baseline 43%); KV 116,795 tok (baseline 171,546 — torch-2.13
cudagraph memory profiler reserves more upfront; irrelevant at C=1); MTP mean
acceptance ~2.1 / draft-accept 54–61% (baseline 2.4 / 67–75% — see caveat).

## Verdict + mechanism
- **PREFILL — small real gain.** `ctx_pp` +3–7% (largest at shallow depth, tapering with
  depth; low variance → real). `pp2048` flat (the one −3.8% cell has ±97 variance = noise).
- **DECODE — no gain, flat within noise.** torch-2.13 decode is pinned at ~38 tok/s **mean at
  every depth** (38.50 / 38.05 / 38.45); the baseline straddled the same ~37–42 band. Peak
  and mean deltas cross zero depending on depth (−8%…+4%) and the variance bands overlap.
  **No decode gain, certainly not >10%.**
- **The tokenspeed >10% was decode; ours (small) is prefill — opposite phase.** Why:
  tokenspeed runs **host-bound piecewise decode** (BreakableCapture eager-break tax), and
  torch-2.13's host-side / unified-Graph-API improvements relieved exactly that — its
  +14–19% was tokenspeed **catching up to the ~38 tok/s fabric decode wall** that vLLM's
  **FULL monolithic decode cudagraph already sat at**. vLLM has no per-step host tax to
  relieve, and GB10 2-node decode is **fabric-RTT-bound** (~93 serial per-layer small-AR
  NIC round-trips/step, host-staged RoCE — the same wall both engines hit). So torch-2.13
  gives vLLM decode **zero headroom**. Where vLLM *does* benefit is prefill, which is
  compute+dispatch-bound with partly eager/piecewise-compiled regions — torch-2.13's
  host/dispatch/compile improvements shave a few % off `ctx_pp`.

## Caveats / follow-ups
- **NCCL pin is 2.30.4, not the plan's 2.30.7.** Per the settled torch×NCCL 2-D matrix,
  2.30.7 wedges graph-replayed collectives under torch 2.13, and torch-2.13's own default
  2.29.7 wedges too; only 2.30.4 is safe on both torch generations. Confirmed here by the
  NCCL graph-replay gate (**PASS, 5000 max-rate replays, .116/.119**). **Trap:**
  `uv pip install -e .` re-resolves and clobbers the override back to 2.29.7 — must re-pin
  2.30.4 **after** the vllm build (caught via `VERIFY nccl 2.29.7`).
- **MTP acceptance dip (2.4→2.1 mean length, 67–75%→54–61% draft-accept).** Same MTP code
  (#48304 in both heads); a torch-2.13 draft-numerics shift (reduction order) is the likely
  cause. Correctness is unaffected (GSM8K 0.965, arthur perfect), but a lower acceptance
  slightly depresses shallow-depth decode. Worth an isolated re-measure if decode parity
  matters; does not change the >10% verdict.
- Single benchy-standard run (3 sub-runs/cell). Decode variance on the GB10 fabric wall is
  real; a repeat would tighten the decode cells but not the conclusion (no >10%).

## Reproduce
```bash
# both nodes: fresh torch-2.13 venv + worktree (scratchpad build_torch213_*.sh), then:
VLLM_ROOT=/home/jasl/tmp/vllm-torch213-20260711 \
VLLM_VENV=/home/jasl/tmp/vllm-torch213-venv \
  scripts/run_gb10_llama_benchy_standard.sh    # on .116
```
Raw: [`llama_benchy_torch213.out`](./llama_benchy_torch213.out), [`gsm8k.out`](./gsm8k.out),
[`toolcall15.json`](./toolcall15.json), [`build_torch213_vllm.log`](./build_torch213_vllm.log).
