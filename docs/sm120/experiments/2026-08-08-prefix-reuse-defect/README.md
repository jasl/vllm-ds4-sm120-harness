# The c=12 recall loss is a prefix-cache **reuse** defect, and V2 is the heavy casualty

Status: **open defect, mechanism narrowed to the reuse path, root cause not yet located.**
Date: 2026-08-08. Tree `4ebd1fb698` (branch head).
Replaces the framing in
[`../2026-08-07-v2-runner-recall-reclassification/`](../2026-08-07-v2-runner-recall-reclassification/README.md),
whose two central claims this run refutes.

## The result

`runner × prefix-cache`, three arthur c=12 runs per arm, one fresh serve per
arm, each condition read back from the serve log and checked against its
negative control:

| | prefix cache ON | prefix cache OFF |
|---|---|---|
| **V1** | 22 / 22 / 22 | **24 / 24 / 24** |
| **V2** | **3 / 4 / 5** | **24 / 24 / 24** |

Discrimination checks both passed: runner markers V1=0 / V2=3, prefix hit rate
on=95.4% / off=0.0%. The conditions were genuinely in effect.

**With prefix caching off, both runners are perfect and indistinguishable.**
Turning reuse on costs V1 two needles and costs V2 nearly everything.

## What the failure actually looks like

Not partial recall. A failing request loses **all three** sentinels at once and
answers *coherently*, reporting the filler content at the document's first,
middle and final lines. The filler is invertible — line `i` carries
`checksum=(i*37)%1009`, `subsystem=i%17`, `shard=i%29` — so the reported values
decode to actual line numbers:

| failing request | reported checksums | decodes to lines | sentinels are at |
|---|---|---|---|
| gate idx 0 | 0037 / 0543 / 0568 | 1 / 451 / 888 | 17 / 450 / 887 |
| gate idx 4 | 0037 / 0467 / 0568 | 1 / 858 / 888 | 17 / 450 / 887 |

So the model is reading real document content and reporting it fluently — it
simply does not see the sentinel lines. This was in the per-request JSON from
the first run onward; only the summary `passed=N/24` line was ever read.

## It is two defects, not one

Holding the serve fixed and varying only whether a live writer is present
(`COLD` = N concurrent against an empty cache, `SOLO` = one lone request
against a fully written cache, `WARM` = N concurrent against a fully written
cache):

| | COLD (12 conc) | SOLO (1, warm) | WARM (12 conc) |
|---|---|---|---|
| **V1** | 11/12 | **1/1** | **12/12** |
| **V2** | 0/12 | **0/1** | 1/12 |

V2 also fails 0/5 COLD and 0/5 WARM at concurrency 5, so depth is not involved.

**Defect A — mild, visible on V1.** V1 fails only in the *cold concurrent*
batch, roughly one request in twelve, and is perfectly clean both solo and
warm. That is the publish-before-write race signature exactly, and it accounts
for V1's gate score: 22/24 = two failures, all of them in the first wave
(indices 0–11), none ever at index ≥12. The race hypothesis was dismissed too
broadly below — it is wrong for V2, but it remains the best explanation for V1.

**Defect B — catastrophic, V2 only.** V2 fails whenever the cache holds
anything: cold, warm, concurrent, or a single serial request. Concurrency is
irrelevant. This is a separate and far larger fault in how V2 consumes a
reused prefix, and it subsumes V2's cold-batch failures.

## Five hypotheses killed, in order

| hypothesis | killed by | cost |
|---|---|---|
| KV capacity / preemption pressure | `preempt_lines=0`, KV peaks at 36% | free (read the log) |
| V1-only `prev_step_scheduled_req_ids` resync that V2 skips | that path only runs for *resumed* requests; there are none | free (read the log) |
| batch depth | V2 fails identically at c=5 **and at c=1** | 1 serve |
| writer race (readers racing the prefix writer) | **a lone serial request against a fully written cache fails: SOLO 0/1** | 1 serve |
| per-needle retrieval margin ("gamma-only, batch numerics") | all three sentinels lost, and only ever with reuse | 4 serves |

The writer race deserves a note: `allocate_slots` publishes blocks into
`cached_block_hash_to_block` at *scheduling* time, counting
`total_computed_tokens + num_new_tokens` — i.e. including tokens this step has
not computed yet. That looked like a textbook publish-before-write race and it
predicted the first-wave-only failure pattern seen on V1. It is not the
mechanism: concurrency is not required at all.

## Where that leaves it

The fault is gated entirely on **whether a request reads a populated prefix
cache**, and not at all on concurrency. Two candidates remain, and they need
different fixes:

- **(a) the bookkeeping is wrong** — the wrong blocks are matched, or hashes are
  stale, so the cached content itself is bad;
- **(b) the bookkeeping is right and V2 mis-consumes it** — block table,
  `num_computed_tokens`, or slot mapping for the reused span is built wrong.

**Evidence favours (b):** V1 reads the same cache at the same 95.4% hit rate and
is nearly fine. If the cached content were bad, V1 would break with it.

Both known prefix-cache race fixes are already in this tree — upstream #50432
(`cross-block race on num_accepted in MRv2 align prefix cache`) and the fork's
own `c601168d0f` (`clear stale prefix-cache block hashes on reuse`). This is not
a missing upstream patch. Note that `c601168d0f` means the fork has already been
bitten once by stale prefix-cache state; this is the second time in the same
neighbourhood.

## Consequences

- **V1 stays the default, and now for a concrete reason**: V2 loses long-context
  recall whenever prefix caching is on, which is the production configuration.
- **V1 is not clean either.** 22/24 versus 24/24 is a real, reproducible loss on
  the default runner in the default configuration. That deserves its own fix,
  not just a note.
- The long-standing "V2 recall is bimodal by serve instance" story is explained:
  serve KV varies ~1 GiB run to run, which moves how much of the prompt the
  cache can hold and therefore how much reuse a serve achieves.

## Next

An offset probe (`ds4_harness/offset_probe.py`) asks for the checksum at six
known line numbers and decodes which line was actually read, cold versus warm,
on both runners. A constant shift points at block-table arithmetic on the reused
span; scattered values point at content corruption. The cold arm is the control
and the probe reports itself uninformative rather than producing a number if the
control is inaccurate.
