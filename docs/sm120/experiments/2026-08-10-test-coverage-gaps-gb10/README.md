# Two test gaps on GB10, and why neither is a code defect

Date: 2026-08-10. Tree `d44e224ab9`. These are the two non-green results in the
[acceptance run](../2026-08-09-runner-arbitration-786582103a/README.md) for the
DeepSeek-V4 SM12x branch. Both are hardware/harness limits, established by
measurement rather than assumed.

## 1. `test_async_scheduling_pp_allows_rescheduling_with_output_placeholders`

Fails at construction, before any scheduling logic runs:

```
ValidationError: 1 validation error for ParallelConfig
  Value error, World size (2) is larger than the number of available GPUs (1)
  in this node.
```

The case builds a `ParallelConfig` with `pipeline_parallel_size=2`. **A GB10 node
has exactly one GPU** (`nvidia-smi -L` → `GPU 0: NVIDIA GB10`), so PP=2 within a
node cannot be constructed here.

It is the **only** case in `tests/v1/core` that needs more than one GPU — the
other 509 pass. It fails identically on the pre-merge tree `4ebd1fb698`, so it
predates this work and will keep failing on this hardware regardless of what the
branch does. Not a defect, not fixable here.

## 2. `tests/v1/spec_decode` wedges — cumulatively, not on any one case

Under a 30-minute bound the suite never finishes: it wedges on the merged head
and on `4ebd1fb698` alike, stopping at different points (≈54% and ≈83%).

Narrowed to `test_max_len.py`, then measured two ways:

| how it is run | result |
|---|---|
| whole file, one pytest process | **wedges after ~7 min, 5 of 11 done** |
| each case in its own pytest process | **11 of 11 PASS**, free memory steady at 117 GiB |

So no individual case is broken. Each case stands up a full engine, and
repeatedly creating and tearing one down **inside a single process** does not
release resources fast enough on a single-GPU unified-memory node; by roughly the
sixth engine the process stops making progress.

That also explains the two things that were previously confusing:

- **Both trees wedge** — it is the environment, not the code.
- **They stop at different points** — where it stalls depends on the memory state
  at the start of the run, not on which test is "bad".

### What this means for the branch

`tests/v1/spec_decode` is **unverified coverage on this hardware, not a passing
check**. The acceptance run reports it as a blocker for exactly that reason. To
get real signal from it here, run it one process per case:

```bash
pytest tests/v1/spec_decode -q --collect-only 2>/dev/null | grep '::' | \
  while read t; do pytest "$t" -q -p no:cacheprovider || echo "FAILED $t"; done
```

That is slow (an engine start per case) but it produces a verdict instead of a
hang. `pytest-forked` or `-p xdist --forked` would achieve the same if added to
the harness.

## Method note

★ **"Individually fine, collectively wedged" is invisible to a whole-suite run.**
The suite reports a timeout, which reads as "something in here is broken" and
invites a hunt for the broken thing. There is no broken thing. The discriminator
that settled it — same cases, one process each — took ten minutes and should have
been the first move once single cases passed.
