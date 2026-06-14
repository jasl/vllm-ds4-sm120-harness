# RTX LLM Decode Bench

Status: observation

## Scope

Community `llm_decode_bench.py` integration and RTX / SM120 run using the
current aggressive EP-off MTP profile.

The benchmark script is the public
`local-inference-lab/llm-inference-bench` `main` branch
`llm_decode_bench.py`, version `0.4.24`, SHA256
`39fa85c5971f2d35ca92c53eea7bc92db11b7691d5fadae84a78e034f6d7a625`.

## Configuration

- Hardware: 2x RTX PRO 6000 Blackwell Workstation Edition, SM120.
- vLLM branch: `codex/ds4-sm120-epoff-sparse-prefill-dev-20260613`.
- vLLM identity: `20260613.dev132+g576043461`.
- TP: 2.
- EP: off.
- MTP: 2 speculative tokens.
- KV cache: FP8, block size 256.
- Prefix cache: on.
- CUDA graph: `FULL_AND_PIECEWISE`, breakable CUDA graph auto-enabled by vLLM.
- `max_model_len`: 131072.
- `max_num_seqs`: 128.
- `max_num_batched_tokens`: 8192.
- GPU memory utilization: 0.90.
- Benchmark decode contexts: `0,16k,32k,64k,124k`.
- Benchmark concurrency: `1,2,4,8,16,32,64,128`.
- Benchmark max output tokens: 4096.
- Benchmark per-cell duration: 30 seconds.
- Benchmark KV budget: 186268 tokens.

Local-safe artifact identifier:

```text
branch=codex/ds4-sm120-epoff-sparse-prefill-dev-20260613
gpu=2x_nvidia_rtx_pro_6000_blackwell_workstation_edition
label=rtx_llm_decode_bench_aggressive_mtp_epoff_124k_kvbudget
timestamp=20260614074832
variant=mtp
```

## Result

The valid KV-budgeted run completed with `llm_decode_bench` phase exit code 0.
There were no benchmark stderr messages and no vLLM `ERROR`, `Traceback`,
OOM, HTTP 400, or HTTP 500 entries in the serve log.

The community-report-aligned ctx0 follow-up also completed with phase exit code
0, but did not close the high-concurrency gap versus the published Lucifer TP2
MTP probabilistic numbers. With `max_model_len=262144`, `max_num_seqs=64`,
`max_tokens=2048`, `skip_prefill`, graph cap 192, and scheduler full-ISL reserve
disabled, the C64 result was 1954.8 tok/s versus the community report's 2815.4
tok/s.

After rebooting the RTX host, three additional ctx0 ablations completed. Auto
versus 192 CUDA graph cap and default versus disabled full-ISL reserve changed
the C64 result only within the 1954.8 to 1986.8 tok/s band. These knobs do not
explain the Lucifer high-concurrency decode advantage.

A follow-up FlashInfer CUTLASS MoE-only probe isolated one Lucifer mechanism
without the PR3395 sparse-MLA wrapper. A conversion-only attempt was invalid:
it selected the FlashInfer CUTLASS MoE backend but collapsed MTP draft
acceptance because GPT-OSS-only alpha/beta/clamp defaults were still active.
After matching the DeepSeek-V4 expert-wrapper semantics, GSM8K limit-200
5-shot passed at 0.945 / 0.945 flexible/strict and ctx0 decode improved only
modestly, from -1.0% at C1 to +4.9% at C16. This is a small gated dev
candidate, not the main explanation for the C8-C64 gap.

A separate DeepGEMM FP8-linear-only probe also passed GSM8K limit-200 5-shot
at 0.955 / 0.940 flexible/strict. It improved the ctx0 row by only +1.0% to
+4.8% depending on concurrency and still lagged the local Lucifer+PR3395 row by
11-28% from C8 through C64. The signal is positive, but it is not the primary
high-concurrency decode gap. It also adds startup/JIT deployment cost that
needs a warmup fix before promotion.

Combining DeepGEMM FP8 linear with the corrected FlashInfer CUTLASS MoE route
did not stack. The combined row was at best +4.8% versus current and was weaker
than one or both single-backend probes at C1/C4/C32/C64. This points the next
decode-scaling work back toward attention/runtime mechanisms, especially the
PR3395 sparse-MLA route, rather than a naive linear+MoE backend swap.

A same-session 2x2 attribution pass (Lucifer vs current, MTP on/off) then
isolated the root cause. The runtime-resolved configs are identical on
compile/cudagraph, all-reduce, sampler, FP8 linear, and MTP acceptance
(`~2.25` length, `~63%` draft); the only backend differences are the MoE
backend (`+5%`) and the decode attention kernel. The C8-C64 gap is the
FlashInfer packed SM120 sparse-MLA decode kernel
(`sparse_mla_sm120_decode_dsv4_autotune`), which the current branch never
reintegrated -- it ported only the packed prefill kernel
(`sparse_mla_sm120_paged_attention`). The kernel's advantage is concentrated in
the MTP speculative-verify multi-query (`q_len=3`) decode shape: the MTP
throughput multiplier at C64 is `1.42x` on Lucifer versus `1.17x` on current
despite equal acceptance, which also explains the isolated C4 crossover (the
packed kernel's fixed overhead loses at small batch). See the
"Decode-Kernel Attribution (same-session 2x2)" section of evidence.md.

A PR3395 packed-prefill reintegration check showed two different prefill
signals. The attribution gate improved 16K/65K cold prefill by about +22% and
cut the isolated sparse stage sharply ON THE STALE PRE-REBASE BASE. This is
SUPERSEDED: a 2026-06-15 per-feature re-measurement on the authoritative
`531807c` (warm, repeated, pure C=1 OSL=1) found packed only `-1.7%` end-to-end
(the `-91%` `sparse_accumulate` is stage-relocation into
`flashinfer_packed_attention`, not a speedup) and D512-multi inactive at C=1 /
memory-infeasible multi-request on 2x RTX, so both prefill feature pairs were
DROPPED -- the rebased base already enables indexed-D512 prefill by default. See
the "Phase 3b" section in [evidence.md](evidence.md). However, the
community-shaped
`llm_decode_bench.py --prefill-only --prefill-contexts 8k,64k,128k` scout only
improved the warm reintegrated branch by `+0.8% / +1.2% / +8.3%` versus gate
off and still lagged the published Lucifer TP2 MTP-on prefill row by
`27-35%`. Treat the packed route as useful but not yet sufficient for prefill
parity.

The result is an observation baseline, not a promotion gate. It is useful for
community-facing decode comparisons and for checking whether future decode
changes regress practical capacity-aware throughput.

The evidence package also records the run pitfalls that should not be reused as
performance data: the `128k + 4096` context-window mismatch, missing KV budget
behavior, GPU reset after an intermediate run, Lucifer public-stack failure
without PR3395, sanitized `PYTHONPATH` / `PATH` requirements, the discarded
timeout-killed reintegration run, measured-phase JIT contamination in the first
packed-prefill scout, and the Lucifer+PR3395 prefill-only startup failure.

See [evidence.md](evidence.md) for the extracted tables and run notes.
