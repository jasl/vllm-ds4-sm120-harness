# SM12x acceptance

`run_sm12x_acceptance.sh` answers one question with evidence: **is the SHA we are
about to publish actually good?** It prints `CHECK <name> :: PASS|FAIL|TIMEOUT ::
<evidence>` lines and tallies them, treating anything that is not PASS as a
blocker — including a checklist that came out shorter than expected, because a
run that stops early must not read as a run that passed.

Set `EXPECT` to the SHA being accepted; it aborts if the tree is anywhere else.

## What it covers

- **A** every node clean at that exact SHA
- **B** `tests/v1/core` in full, and `tests/v1/spec_decode` under a 30-minute bound
- **C** a serve with **nothing set** — the configuration a user actually gets:
  boots, runner, guard state read back from the engine log, no NameError, then
  arthur c=12 ×3 and c=1, issue19, GSM8K, multi-needle, benchy
- **D** both escape hatches, each as a real serve: `VLLM_USE_V2_MODEL_RUNNER=0`
  and `VLLM_ALLOW_SPEC_DEC_SAME_STEP_PREFIX_HIT=0`

## Why it is shaped this way

Each rule below exists because its absence cost hours on 2026-08-08/09.

- **Bound every GPU suite.** An unbounded check in a sequential chain does not
  fail — it stops everything after it. `tests/v1/spec_decode` wedged for ten
  hours and phases C and D never ran.
- **Count non-PASS, not FAIL.** A `TIMEOUT` verdict counted as neither, so the
  tally would have printed ACCEPTED with a blocker present.
- **Read conditions back from the engine.** "I set the env var" is not evidence
  the guard is on: with the flag set, DeepSeek-V4 reported `2/5 managers active`
  because upstream gates on `use_eagle` and only the sliding-window groups carry
  it. The startup log line is what caught that.
- **Test the default with nothing set.** Two separately-sound changes (V2 as the
  default runner; the guard defaulting off) composed into the worst configuration
  measured. Every measurement arm set both variables explicitly, so nothing saw it.
- **Never `rm -f` the lock file.** Deleting it leaves the old holder locking a
  deleted inode while the next process locks a new one, so two instances run.
  That caused two concurrent builds and an OOM kill. Truncate with `: >` instead.
- **Check `settle` worked.** A `VLLM::Worker` survived teardown holding 108 of
  121 GiB, which OOM-killed a rebuild (`exit 137`).

## Known gaps on GB10

`tests/v1/spec_decode` does not complete in one process on a single-GPU node, and
one `tests/v1/core` case needs PP=2. Both are hardware limits, not defects —
see `docs/sm120/experiments/2026-08-10-test-coverage-gaps-gb10/`. To get a real
verdict from spec_decode here, run one process per case.

`spec_decode_attribution_control.sh` runs the same suite on a pre-merge SHA under
the same bound, so a timeout can be attributed instead of guessed at.
