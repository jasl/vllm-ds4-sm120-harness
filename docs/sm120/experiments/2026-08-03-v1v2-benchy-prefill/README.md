# V1 vs V2 model runner: prefill and decode throughput

Status: **complete** — V2 is faster on prefill (all 6 cells REAL, Holm-corrected)
Date: 2026-08-03 (first attempt) / 2026-08-04 (final)
Head: **`54e0ebf330`** — the merged head. The first attempt ran at
`2fb22567c5`; those blocks are recorded below but not pooled, being a
different build.

> Everything above the "Results" heading was written **before any arm finished**,
> and the analysis code was committed before the runs started
> (`5546f62` -> `364467d` -> `9a3bdb7` -> `b4d45bf`). The point is that the
> decision rule cannot be tuned to the answer. On 2026-08-02 a single arthur
> c=12 sample, read against a band recorded on a different configuration,
> shipped a wrong default to two public branches; this experiment is the same
> comparison done with the sampling it needed.

## Question

Two things were never measured, on either runner:

1. **Q1** — does the V2 GPU model runner differ from V1 on prefill throughput?
   The 2026-08-02 A/B covered KV headroom, draft acceptance, GSM8K, tool-calling,
   #19 and long-context recall. It never pointed benchy at either runner.
2. **Q2** — prefill numbers for the baseline of record at `2fb22567c5`, which
   has none.

## Profile

2x GB10 (sm_121) TP=2, `deepseek-ai/DeepSeek-V4-Flash-0731`, DSpark nst=5
probabilistic, fp8 KV, prefix cache on, mml 49152, util 0.85, mnbt 8192,
block-size 256. Every knob comes from the pinned
`scripts/run_gb10_llama_benchy_standard.sh` (pp2048 tg128, depths
8192/16384/32768, C=1, runs 3, `--enable-prefix-caching`), so the V1 rows stay
comparable to the recorded history. **The runner is the only variable.**

## Design

Two node pairs, A = `.116`/`.119` and B = `.117`/`.118`, running concurrently.

```
          round 1              round 2
Pair A    v1 v2 v1 v2          v2 v1 v2 v1      blocks 1-4
Pair B    v2 v1 v2 v1          v1 v2 v1 v2      blocks 1-4
                                                + solo v1 (block 101)
```

**Both arms run inside the same pair, interleaved.** A *block* is one adjacent
V1/V2 couple on one pair; pair identity and slow drift cancel exactly inside it.
The pairs are not interchangeable — they disagreed sharply on an unrelated recall
gate (A 22/18/19 needles vs B 6-13) and their worktree binaries differ by a few
bytes — so assigning an arm to a pair would let a pair effect read as a runner
effect. Cross-pair is replication, never the comparison.

Ordering is balanced by construction: V1 and V2 each sit at mean slot 4.5 on
each pair, so within-session drift cannot favour either arm. Every slot has
exactly one V1 and one V2 on the shared CRS804 fabric, so cross-pair contention
is symmetric across arms.

**Assertions before an arm's numbers are kept** — SHA, speculator is dspark,
the "Model Runner V2" log line, and the available-KV figure. The last is an
*independent* check on the runner: V2 has consistently shown ~+4.7 GiB, so a
"V2" arm reading V1-like KV would mean the env var never reached the worker.
A failed assertion voids the arm.

**Solo control.** Every archived benchy run was a single pair on the CRS804;
these run two pairs at once. That cancels for Q1 but not for Q2, so one extra
V1 invocation runs with the other pair idle, and *that* is the band-legal
baseline-of-record row.

## Pre-registered analysis

`scripts/benchy_ab_compare.py`, committed before the runs.

**Threshold.** Not the 12-run historical band. Those runs span different SHAs, a
model change (pre-0731 -> 0731) and a speculator change (MTP2 -> DSpark), so
their spread is build + model + pair + drift + repeat noise. This A/B holds all
of that fixed and only has to beat the boot-to-boot repeat term. Pooling the
archive's three same-build repeat sets (df=4):

| metric | within-build CV | 12-run CV | blocking gain |
|---|---|---|---|
| ctx_pp | 0.39–0.57% | 1.07–2.33% | 2.8–4.4x |
| pp2048 | 1.01–1.31% | 1.22–3.39% | 1.2–2.8x |
| ctx_tg | 2.30–3.46% | 3.39–8.28% | 1.0–3.6x |
| tg128 | 3.99–7.85% | 5.20–6.62% | 0.8–1.6x |

So ctx_pp resolves ~1.3%, not the 4–10% a historical-band rule would demand.

**tg128 is declared NOT RESOLVABLE up front, in either direction.** Its
within-build CV equals its entire historical spread — essentially pure
boot-to-boot noise with no structure for blocking to remove. No affordable n
rescues it, so "V1 and V2 are at parity on tg128" is a claim this design cannot
make and will not make.

**Decisive statistic.** Paired log-ratio per block, `log(V2/V1)`, with an
**exact sign-flip permutation test** — under no runner effect each block's sign
is exchangeable, so enumerating all 2^B assignments is exact and needs no
distributional assumption at df=3. **Holm-corrected across the six prefill
cells**, the primary family. Decode cells are reported uncorrected and labelled
exploratory; they cannot be promoted to findings.

The exact test has a floor: the smallest attainable p is 2/2^B. B=4 cannot beat
0.125, so **B=8 is required** for any cell to clear Holm. That is why the run
collects 8 blocks.

**Per-pair reporting** tests direction *agreement*, not per-pair significance
(each pair holds half the blocks and can never clear Holm alone). If the pairs
point opposite ways, the pooled effect is withheld as an artefact.

**Validation.** The estimator was checked on synthetic data built from a real
archived table with a known +2% V2 prefill effect injected: it recovered ctx_pp
at +2.12/+2.06/+1.66% where the range test said UNDERPOWERED, and pp2048 was
correctly *not* recovered (CI ±3.7–4.9%, consistent with its ~3% floor). That
same check produced one spurious decode effect from 12 uncorrected tests, which
is what motivated the Holm correction.

## Pre-flight

All four nodes at `2fb22567c5`, clean worktrees; torch 2.13.0+cu130, FlashInfer
0.6.16 uniform; `scripts/flashinfer_symbol_contract.py` PASS on all four (a
silently-False probe would reroute DSv4 off the SM120 kernels and read as an
enormous pair effect); stale serves torn down on both pairs before the start.

## First attempt: half the blocks were self-contaminated, and the assertions could not see it

The first run of this design produced 8 blocks. **Four are void.** A follow-up chain that
had been killed — or so I verified, with `pgrep` patterns that did not match the
survivor — ran a second round CONCURRENTLY with the intended one on Pair A. Two serves
fought over port 8000 on the same pair.

Every per-arm assertion passed anyway. SHA, speculator, runner log line and available-KV
were all correct, because each serve really did boot. Only the numbers gave it away:

```
tg128  @ d8192   20.10     (normal ~40)
ctx_tg @ d32768   5.60     (normal ~40)
```

Detection, after the fact, is one line — any run tag appearing twice means concurrent
invocations:

```
grep -oE "tag=[^ ]+" benchy_A.log | sort | uniq -c    # count > 1 == void
```

Discarded: Pair A blocks 3, 4 and the solo control. Kept: Pair B blocks 1–4 and Pair A
blocks 1–2, six clean blocks, which showed every prefill cell with V2 ahead (ctx_pp
+1.02–1.64%, pp2048 +3.75–4.52%, all six blocks agreeing in sign, exact p=0.0312 — the
floor at B=6, short of the 0.0083 Holm needs).

**Those six are not pooled into the final result.** They were measured at `2fb22567c5`;
the run below is at the merged head `54e0ebf330`, a different build. They inform
expectation only.

Three fixes, all in `fulltest.sh`:
1. **`flock`, not `pgrep`, for single-instance.** A `pgrep -f <script>` guard also matches
   `bash -n` syntax checks, the `setsid`/`nohup` wrapper, and the ssh command line that
   launched it. It let the duplicate live, and later it aborted a legitimate start by
   matching itself.
2. **No chained successors.** Each phase is launched explicitly. Chained waiters are
   invisible once detached and survive sloppy kills.
3. **Refuse to start on a dirty pair** — abort if any serve process is alive on either
   node, or if the worktree is not at the expected SHA.

## Results

10 complete blocks at `54e0ebf330` (8 on Pair A, 2 on Pair B). Raw tables in
`runs/`, full tool output in `verdict.txt`.

**V2 is faster on prefill. Every prefill cell is real and survives Holm.**

| metric | V2/V1 | 95% CI | exact p | verdict |
|---|---|---|---|---|
| ctx_pp @ d8192 | **+1.18%** | [+0.82, +1.53] | 0.0020 | REAL |
| ctx_pp @ d16384 | **+1.11%** | [+0.35, +1.87] | 0.0137 | REAL |
| ctx_pp @ d32768 | **+1.61%** | [+1.17, +2.04] | 0.0020 | REAL |
| pp2048 @ d8192 | **+4.18%** | [+3.28, +5.09] | 0.0020 | REAL |
| pp2048 @ d16384 | **+4.18%** | [+3.36, +5.00] | 0.0020 | REAL |
| pp2048 @ d32768 | **+4.33%** | [+3.56, +5.11] | 0.0020 | REAL |

Both pairs agree in direction on every cell (`jasl-spark-1` vs `jasl-spark-3`:
ctx_pp +1.14/+1.33, +1.27/+0.47, +1.61/+1.58; pp2048 +4.00/+4.94, +4.46/+3.07,
+4.23/+4.72), so the pooled effect is not an artefact of one pair.

**Decode is not resolved, in either direction.**

- `tg128` — **NOT RESOLVABLE**, as declared before the run. Effects read +2.36%,
  −0.03%, +3.76% with CIs spanning ±10%. Recorded, not claimed.
- `ctx_tg` — +6.19%, +8.35%, +8.67%. Exploratory and uncorrected; it is not part
  of the pre-registered family and is not a finding. Worth a properly powered
  look later, since the direction matches prefill.

### The two analyses disagree, and that is the point

The coarse range screen returns **9× UNDERPOWERED, 3× NOT RESOLVABLE** — it finds
nothing at all. The paired block estimator finds six real effects on the same 10
blocks. That gap is the 2.5–4× that the variance decomposition predicted blocking
would buy on prefill, and it is why the paired test was made decisive *before* any
data existed. Had the range screen been the decisive statistic, this experiment
would have concluded "no measurable difference" and been wrong.

### Why B≥8 was not negotiable

The exact sign-flip test's smallest attainable p is `2/2^B`. At B=4 that is
0.125, at B=7 it is 0.0156, both above the 0.0083 that Holm across six cells
requires; only at B=8 (0.0078) can any cell clear it. Ten blocks put the floor at
0.0020, which is why five of six cells sit exactly there — every block agrees in
sign.

### Cost of getting 10 clean blocks

24 invocations, of which 2 were lost to distinct transient failures:

- `rc=3` "existing vLLM process" — the previous arm's teardown had not settled.
  Fixed with a per-arm barrier that waits for both nodes to show zero serve
  processes; zero recurrences afterwards.
- `rc=255` — ssh transport failure during startup. Not fixed, absorbed by
  over-provisioning arms.

Both produced an orphaned half-block (`v1_b4`, `v2_b6`), dropped by detecting
missing partners rather than assuming pairs are complete.

## What this changes

The 2026-08-02 A/B concluded V2 was ahead on KV headroom and draft acceptance and
level on correctness, and the c=12 re-sampling then showed it loses more than half
the long-context needles under concurrency, which is why V1 remains the default.
Prefill was the one axis never measured. It is now: **V2 is also ahead there**,
by ~1.1–1.6% on ctx_pp and ~4.2% on pp2048.

That does not reopen the default — losing half the needles is not worth 4% of
prefill — but it does mean the case for revisiting V2 whenever upstream moves the
runner is stronger than the KV and acceptance numbers alone suggested.
