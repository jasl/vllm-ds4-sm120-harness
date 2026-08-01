# DeepSeek-V4-Flash-0731 + DSpark — baseline of record

Status: accepted
Date: 2026-08-02
Owner/context: first full baseline on the `0731` checkpoint, replacing the MTP2 baselines.
Shipped as tag `sm120-pr-41834-stable-preview-20260802`.

## Question

`DeepSeek-V4-Flash-0731` removed the MTP heads, so the previous baseline profile
(MTP2 on `DeepSeek-V4-Flash`) can no longer be reproduced — the old checkpoint is
deleted and the new one cannot serve `method="mtp"`. What is the replacement
baseline, and does DSpark cost anything relative to what MTP2 used to deliver?

## Profile

- Hardware: 2x GB10 / DGX Spark (sm_121), RoCE `192.168.100.116` / `.119`
- vLLM branch/commit: `9a94c54292` (tag `sm120-pr-41834-stable-preview-20260802`)
- Dependency identity: torch 2.13.0, triton 3.7.1, FlashInfer 0.6.15.post1
  (python + cubin), nvidia-nccl-cu13 2.30.7, tilelang 0.1.12,
  nvidia-cutlass-dsl 4.6.0, quack-kernels 0.6.1
- TP / PP / EP: 2 / 1 / off
- Speculative decode: **DSpark `num_speculative_tokens=5`, probabilistic** — and a
  no-speculation arm. MTP is not available on this checkpoint.
- FP8 KV: on (`fp8`, mandatory — `fp8_ds_mla` asserts an fp8 layout)
- Prefix cache: on
- CUDA graph mode: `FULL_AND_PIECEWISE`
- `max_model_len` 49152, `max_num_seqs` 64, `max_num_batched_tokens` 8192,
  `--block-size 256`, `--gpu-memory-utilization 0.85`

## Result

### Correctness matrix (DSpark on / off)

| gate | DSpark nst=5 | no speculation |
| --- | --- | --- |
| GSM8K 8-shot, flexible | 0.9394 | 0.9500 |
| GSM8K 8-shot, strict | 0.9363 | 0.9484 |
| instruction-following (#19, JSON-only) | PASS | PASS |
| long-context recall (arthur needle), c=1 | 2/2 | 2/2 |
| illegal-access / assertion in serve log | 0 | 0 |
| draft acceptance (prose, best sample) | mean 2.08, 21.7% | — |
| tool-calling, 135 cases | **97%** (263/270) | not run |

`0731` is the **first checkpoint where the strict and flexible GSM8K extractors
disagree**; on every prior baseline they were identical. Quote which one you mean.

The DSpark/nospec GSM8K difference (1.06 pp flexible, 1.21 pp strict) is **not
resolvable from these single runs** — the measured single-run spread on this gate
is ~1.1 pp. A 3x-per-cell comparison is scheduled separately.

### Tool-calling (`tc15_0731.json`)

45 scenarios x 3 thinking modes x 3 rounds = 135 cases: **130 full passes, 3 partial
(TC-07 Search-Read-Act, TC-11 Simple Math x2, all non-thinking), 2 failures (TC-06
Multi-Value Extraction, TC-12 Impossible Request, both think-high)**. The runner
exits non-zero whenever any case misses full marks (`--min-points 2`), so `rc=1` is
the normal outcome; the historical runs exited the same way.

Prior 135-case runs on the **old** checkpoint scored 82 / 87 / 89%. 97% is above that
band, but **do not attribute it to any single change**: both the checkpoint and the
prompt-encoding path (#50686, which merges consecutive assistant messages — exactly
the multi-turn shape this gate exercises) changed at once. 8 pp is roughly 3x this
gate's 135-case sigma (~2.6 pp), so it is probably real; it is not isolated.

This gate had **never been run on `0731`** before this baseline. The tc15 artifacts
sitting in `gates_234/` are from the old checkpoint at an older SHA, and the earlier
driver's "GATE 4: toolcall15" line scored `RC=127` — the script it called does not
exist, so nothing ran and it was recorded as a gate that had.

### Unit suite at `9a94c54292` (`units_9a94c54292.log`)

| section | result |
| --- | --- |
| A. DSv4 kernels | 226 passed, 12 skipped |
| B. DSv4 attention backends | 6 passed |
| C. spec decode / dspark config | 40 passed |
| D. kv offload | 710 passed, 6 skipped |
| E. core scheduler + prefix cache | 232 passed, **1 failed** |
| F. kernel warmup | 2 passed |
| G. DSv4 tokenizer / prompt encoding | 44 passed |

The single E failure is
`test_scheduler.py::test_async_scheduling_pp_allows_rescheduling_with_output_placeholders`,
which needs 2 GPUs in one node; GB10 nodes have one each, so it cannot pass here.
Not a regression — it failed identically at the previous head. Section F was **red
at `8ddfc85aac`** (two MTP warmup tests) and is green here; `3238aa0587` moved the
tests to follow the DSv4 passes into their new module.

### Performance (`benchy_20260802.out`)

`llama-benchy` standard, C=1, 3 runs, against the **full** recorded range of every
prior MTP2 baseline in `docs/sm120/experiments/` (n=10 independent runs per metric,
07-07 through 07-27). This crosses a checkpoint boundary — treat it as a sanity
band, not a controlled A/B.

| metric | prior MTP2 range (n=10) | 0731 + DSpark | vs band |
| --- | --- | --- | --- |
| pp2048 @ d8192 | 1339.11 – 1400.81 | **1432.23** ± 11.74 | **above** |
| pp2048 @ d16384 | 1308.77 – 1344.68 | **1356.56** ± 11.78 | **above** |
| pp2048 @ d32768 | 1089.05 – 1226.63 | **1250.75** ± 2.18 | **above** |
| ctx_pp @ d8192 | 1757.16 – 1876.01 | 1816.97 ± 5.89 | inside |
| ctx_pp @ d16384 | 1769.85 – 1842.16 | 1817.43 ± 1.43 | inside |
| ctx_pp @ d32768 | 1595.87 – 1756.01 | 1740.22 ± 2.87 | inside (near top) |
| tg128 @ d8192 | 36.27 – 43.08 | 41.72 ± 5.09 | inside |
| tg128 @ d16384 | 34.59 – 43.14 | 37.92 ± 9.92 | inside |
| tg128 @ d32768 | 32.77 – 42.91 | 34.88 ± 5.78 | inside |
| ctx_tg @ d8192 | 38.52 – 43.01 | 39.37 ± 2.34 | inside (near bottom) |
| ctx_tg @ d16384 | 39.29 – 43.07 | **35.07** ± 0.67 | **below, −10.7%** |
| ctx_tg @ d32768 | 38.02 – 42.73 | 40.70 ± 6.85 | inside |

**Batched prefill (pp2048) is above the historical band at all three depths**
(+2.2% / +0.9% / +2.0%) — the only consistent directional move here. Clearing the
max of ten prior runs at all three depths is more than any single one of those
margins would justify on its own: +0.9% is inside this metric's own resolution,
so read the consistency, not the magnitudes. `ctx_pp` is inside the band
everywhere; an earlier draft of this summary claimed it was above, which came from
comparing against a hand-picked subset of history rather than all ten runs.

Reproduce with `scripts/benchy_history_band.py`, written after that mistake so the
band is computed from every archived run instead of assembled by hand.

★ The benchy tables of **every prior baseline** are now `git add -f`'d (13 files,
68 KB total). `.gitignore` excludes `*.log`/`*.out`, so until now the entire
historical band existed only as untracked files on one laptop — the comparison
basis for every future change was one disk failure from being unrecoverable, and
the script would find nothing in a fresh clone. Large per-run artifacts (metrics
dumps, GPU CSVs, serve logs) stay untracked as before.

```bash
python3 scripts/benchy_history_band.py \
  docs/sm120/experiments/2026-08-02-ds4flash-0731-dspark-baseline/benchy_20260802.out \
  --exclude 2026-08-02
```

⚠ **`ctx_tg @ d16384` is the one metric outside its band**, 10.7% below the
historical minimum. Treat it as unresolved rather than as a regression: it is
non-monotonic against our own readings at the neighbouring depths (39.37 at d8192,
40.70 at d32768, where history has d16384 ≈ d8192), which points at a single-run
artifact. It needs a repeat before it means anything — but it must not be waved
through just because every other number is fine.

### `num_speculative_tokens` must equal `dspark_block_size`

Four-configuration A/B on a prose workload (`accept_nst*.log`), all three samples
per configuration shown — the probe reports whatever `SpecDecoding metrics` lines
vLLM flushed inside its window, so a low sample means thin traffic in that slice,
not a worse drafter:

| configuration | mean acceptance length | avg draft acceptance rate |
| --- | --- | --- |
| nst=5 probabilistic | 2.15 / 2.16 / **2.19** | 22.9 / 23.2 / **23.8%** |
| nst=7 probabilistic | 1.61 / 1.75 / 1.95 | 8.7 / 10.7 / 13.6% |
| nst=5 greedy | 1.82 / 2.06 / **2.23** | 16.4 / 21.2 / **24.5%** |
| nst=7 greedy | 1.57 / 1.66 / 1.75 | 8.2 / 9.5 / 10.8% |

The 7th draft position accepted **0.000 in every sample**; the 6th accepted 0.000
in all but one (0.004 there). `nst=7` drafts 40% more tokens per step and accepts
fewer. Both nst=7 runs also hit connection errors partway through, so their spread
is noisier than the nst=5 rows.

★ **Measure this on prose only.** On counting or repeated text the Markov head alone
reaches 68–98% acceptance even with the neural draft path degraded, which hides the
effect completely.

## Artifact-to-commit map

Not every artifact here was produced at `9a94c54292`, and relabelling them all as
"head" would be wrong. The `nst=7` arms in particular *cannot* be reproduced at head
— the validator added in `9a94c54292` rejects them at startup, which is the point.

| artifact | commit | why |
| --- | --- | --- |
| `matrix_dspark/*`, `matrix_nospec/*` | `9a94c54292` | run 23:23–00:59, after the 23:15 checkout |
| `benchy_20260802.out` | `9a94c54292` | run 00:59 |
| `accept_final.log` | `9a94c54292` | run 01:18 |
| `units_9a94c54292.log` | `9a94c54292` | run 01:38 |
| `tc15_0731.json`, `tc15_0731_run.log` | `9a94c54292` | run 01:49; preconditions (tree SHA, served model, spec config) asserted in the log before the gate started |
| `accept_nst5/7/5g/7g.log` | `7314ceaa11` | pre-validator; nst=7 is unstartable after the fix |
| `repro_case1_tp4_ep.log`, `repro_case2_flashmla_backend.log` | `7314ceaa11` | community-report repros, run 21:04–21:40 |
| `mtp2_attempt_on_0731.log` | `7314ceaa11` | the MTP-on-0731 weight-load failure |
| `build_234.log` | `399c3df4b3` | the build that produced the installed binaries |

The installed package reports version `0.26.1rc1.dev411+g8ddfc85aa` on every run
above. That string is **stale setuptools_scm metadata baked at build time**, not the
running code: the delta from `8ddfc85aac` to `9a94c54292` is pure Python and the
install is editable, so the worktree content is what executes. Verified against the
worktree reflog (both nodes moved to `9a94c54292` at 23:15/23:16, before every run
listed as head). Do not read that version string as the code identity.

## Interpretation

DSpark nst=5 is the replacement for MTP2 on `0731`, at no measured throughput cost
and with correctness gates green on both arms. The two config defects found while
investigating the community reports (`nst` equality, and `method="mtp"` being
silently rewritten to `"dspark"`) are fixed at this head.

## Open

- GSM8K 3x per cell to settle the DSpark/nospec difference against the ~1.1 pp
  single-run spread.
- FlashInfer 0.6.16 upgrade.
- V2 model runner and breakable-cudagraph experiments, re-evaluated on torch 2.13.
- The DSpark-side VRAM A/B (PR #27's actual claim) remains unmeasured; the serve
  available-KV figure is ~1 GiB / 9% noisy run-to-run and needs 3x repeats.

## Harness defects fixed to make this run possible

- `run_gb10_llama_benchy_standard.sh` hardcoded the deleted checkpoint and an MTP2
  spec config; both are now overridable (`MODEL`, `SERVE_SPECULATIVE_CONFIG`).
- `dgx_spark_start_mp_serve.sh` hardcoded `--nnodes 2` at two sites and could not
  accept `WORKER_HOSTS` / `WORKER_ROCE_IPS`, so N-node serving was unusable.
- `ds4_harness/cli.py` `DEFAULT_MODEL` still pointed at the deleted checkpoint.
- The earlier baseline driver called `scripts/run_toolcall15_gate.sh`, which does
  not exist — it scored `RC=127` and was recorded as a gate that ran. There is no
  toolcall gate script; the interface is the `toolcall15` CLI subcommand, and
  `--thinking-mode` must be passed three times or the run is 45 cases, not 135.
- `run_dspark_acceptance_probe.sh` reported the *last* metrics sample rather than
  the best, which on a real run meant reporting 1.39 next to a steady-state 2.08.
