# Upstream merge (31 commits) + the DSpark out-of-vocab IMA fix

Status: **validation in progress**
Date: 2026-08-03
Head: vLLM `54e0ebf330` (branch `wip/merge-31-oov-fix`)

## What landed

| commit | what |
|---|---|
| `e171c51036` | **fix(dspark): fused Markov sampler emitted an out-of-vocab token id** |
| `3df857ba50` | adopt upstream #50844 (alexbi29): bound `token_id` before the `tid2eid` gather |
| `ce574ecee8` | merge PR #37 (alexbi29): tuned FP8 W8A8 config for N=4096,K=12288 |
| `54e0ebf330` | merge `upstream/main`, 31 commits, no conflicts |

## The bug that motivated this

Reported from production as an illegal memory access on every TP rank
(vllm-project/vllm#41834). The reporter traced it to the **V2** gumbel/rejection samplers
and filed #50843. That is a real defect, but it is not the one that reaches this branch's
default — V1 is the default here, and the V1 producer is our own kernel:

`_dspark_markov_probs_blocks_kernel` stores `vocab_size` as the filler when a block has
no active lane (`dspark_triton.py:451-454,464`). On a fully-masked row — every candidate
`-inf` — **no** block has an active lane, so every block stores the filler; the reduce
kernel then finds all blocks tied at `-inf` and returns that filler verbatim as the
sampled token (`:519-521`). Downstream, the runner clamped `input_ids` with `min=0` only
and the DSv4 hash-MoE router indexes `tid2eid[token_id * 6 + lane]` on a
`[vocab_size, 6]` table with no bound of its own.

**Why no gate caught it.** `dspark_sampling.py:235-240` falls back to the bounded eager
sampler when `all_greedy` or any seeded generator is present, so the fused kernel only
runs for a batch carrying an unseeded `temperature>0` request. arthur and GSM8K are
greedy and are structurally incapable of reaching it. Second time this branch has shipped
a defect its gates could not execute; the new regression test is explicitly non-greedy.

Red/green on 2× GB10 (SM121): the unfixed tree fails with
`out-of-vocab token id 4096 >= vocab_size 4096`; fixed passes; full `test_dspark.py` green.

**Not fixed, and stated so:** on such a row `row_z == 0` → `row_invz = inf`, so the
`draft_probs` handed to the rejection sampler are still garbage. The clamp makes the id
addressable, not meaningful.

## Upstream triage

- **#50844 adopted** — zero offset, runner-agnostic C++, defence in depth. Earns its
  place because the kernel should not trust an id is in range and `prompt_token_ids` reach
  it directly under `--skip-tokenizer-init`.
- **#50843 not taken** — V2-tree only, inert on our default, and carrying it guarantees a
  conflict when upstream lands it. Opt-in `VLLM_USE_V2_MODEL_RUNNER=1` users stay exposed
  until then.
- **#50845 not taken — verified correctness defect.** It adds
  `expert_id >= num_experts -> skip` unconditionally to `moe_sum_pad_aware_skip` but
  sources `num_experts` only inside `if (expert_map.has_value())`. The pad-aware path is
  entered on `topk_ids.has_value()` alone (`moe_align_sum_kernels.cu:779`) and the schema
  declares them independently (`torch_bindings.cpp:31`), so
  `moe_sum(input, out, topk_ids, None)` gives `num_experts == 0`, the check degenerates to
  `expert_id >= 0`, every slot is skipped, and the output is **silently all zeros**. All
  four tests it adds pass a non-None `expert_map`.

## Two environment defects this run exposed

Neither is a code regression; both would have silently degraded a future run.

**1. A malformed tag broke the build on one pair only.** `git describe` resolved to
`sm120-pr-41834-stable-preview-20260802d`; the trailing letter makes `20260802d`
un-parseable as PEP440, so `vcs_versioning` raised and `setup.py build_ext` exited 1 —
leaving a **stale `.so` behind new Python**, which is exactly the shape that produced a
bogus mass-red suite on 07-27. The other pair had the newer `-20260803` tag and built
fine. Our `YYYYMMDD[letter]` tag convention is a latent build breaker.

**2. `tenacity` was missing on all four nodes**, so every GSM8K run failed with
`ModuleNotFoundError: ... required packages ['tenacity']` out of lm-eval's API-model path.
The 08-02 archive proves it worked then, so it was dropped in between. Worth noting the
diagnosis: the first hypothesis — that lm-eval 0.4.12 now requires a `run` subcommand,
which its usage string suggests — was **wrong**, and the archived 08-02 run using the
identical bare invocation is what refuted it. The real cause only appeared in
`stderr.log` inside the run directory, which the harness's summary JSON does not surface.

## Results

_pending_
