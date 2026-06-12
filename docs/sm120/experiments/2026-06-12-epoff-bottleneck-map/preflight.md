# Preflight

Run this checklist before the first EP-off bottleneck experiment or after any
branch, dependency, driver, or machine reboot change.

## 1. Preserve Branch Isolation

- Keep the PR stable preview, backend-parity diagnostic base, and current
  code-bearing dev checkout separate from disposable reproduction work.
- Use `codex/ds4-sm120-min-enable` / stable preview `f32247a5a6` as the
  control. Use `codex/ds4-sm120-pr3395-packed-dev-20260613` for current
  opt-in diagnostics, sparse-prefill prototypes, and backend experiments.
- Use a worktree or clean clone for black-benediction reproduction.
- Do not run optimization experiments directly on the PR branch unless the
  candidate is already narrow and reversible.

Read-only state checks:

```bash
git status --short --branch
git -C vllm status --short --branch
git -C flashinfer status --short --branch
git -C b12x status --short --branch
git -C vllm rev-parse --verify sm120-pr-41834-stable-preview-20260612075245
git -C vllm rev-parse --verify sm120-pr-41834-fallback-before-replacement-20260612053720
git -C vllm rev-parse --verify codex/ds4-sm120-min-enable
git -C vllm rev-parse --verify codex/ds4-sm120-backend-parity-dev-20260612
git -C vllm rev-parse --verify codex/ds4-sm120-pr3395-packed-dev-20260613
git -C vllm merge-base --is-ancestor codex/ds4-sm120-min-enable \
  codex/ds4-sm120-backend-parity-dev-20260612
git -C vllm merge-base --is-ancestor codex/ds4-sm120-backend-parity-dev-20260612 \
  codex/ds4-sm120-pr3395-packed-dev-20260613
```

## 2. Confirm Frozen External References

This phase is pinned to the current reference set. Do not refresh remote heads
before every experiment; that makes same-phase comparisons noisy. Confirm local
freeze tags before using any head value in a new artifact note:

```bash
git -C vllm rev-parse sm120-freeze-vllm-upstream-main-20260612^{}
git -C vllm rev-parse sm120-freeze-vllm-pr45277-20260612^{}
git -C vllm rev-parse sm120-freeze-black-benediction-20260612^{}
git -C flashinfer rev-parse sm120-freeze-flashinfer-main-20260612^{}
git -C flashinfer rev-parse sm120-freeze-flashinfer-pr3395-20260612^{}
git -C b12x rev-parse sm120-freeze-b12x-master-20260612^{}
```

Refresh public refs only during an explicit upstream-change review:

```bash
git -C vllm ls-remote https://github.com/local-inference-lab/vllm.git \
  refs/heads/dev/black-benediction
git -C vllm ls-remote https://github.com/vllm-project/vllm.git \
  refs/pull/45277/head refs/heads/main
git -C flashinfer ls-remote https://github.com/flashinfer-ai/flashinfer.git \
  refs/heads/main refs/pull/3395/head
git -C b12x ls-remote https://github.com/lukealonso/b12x.git \
  refs/heads/master
```

If a head changed and the change is relevant, fetch it, update the freeze tag
or create a new dated freeze tag, and update the relevant experiment
`evidence.md` before comparing new numbers with old notes.

## 3. Prepare RTX / SM120 Environment

The RTX host should have:

- the harness checkout and target vLLM checkout on the same filesystem or with
  paths exported explicitly;
- vLLM installed in the target venv;
- `lm_eval` installed in the same venv if GSM8K will run;
- model access already working for `deepseek-ai/DeepSeek-V4-Flash`;
- no stale vLLM server on the target API port;
- enough free artifact space for serve logs, summaries, and sparse stats.

Use explicit path overrides. The examples use relative paths for public-safe
documentation, but a real run can export private absolute paths in the shell or
an ignored local note:

```bash
export SM120_VLLM_REPO=./vllm
export SM120_VLLM_VENV=./vllm/.venv
export SM120_PYTHON=./vllm/.venv/bin/python
export SM120_VLLM_BIN=./vllm/.venv/bin/vllm
export VLLM_ROOT="${SM120_VLLM_REPO}"
export PYTHON="${SM120_PYTHON}"
export VLLM_BIN="${SM120_VLLM_BIN}"
```

`B200_VLLM_REPO` and `B200_VLLM_VENV` remain accepted by older harness scripts
as compatibility aliases only. New SM120 / RTX PRO 6000 instructions should use
the `SM120_*` names. GB10 / SM121 remote scripts continue to use
`VLLM_ROOT` / `VLLM_VENV` because those values point at the remote two-node
checkout.

Quick local checks:

```bash
"${PYTHON}" -V
"${PYTHON}" - <<'PY'
import importlib.util

for name in ("vllm", "lm_eval"):
    spec = importlib.util.find_spec(name)
    print(f"{name}: {'ok' if spec else 'missing'}")
PY
PYTHON="${PYTHON}" scripts/run_b12x_stack_probe.sh
```

The b12x stack probe records dependency availability only. A pass does not mean
the route is active in vLLM serving; endpoint logs must still prove dispatch.

## 4. Prepare GB10 / SM121 Environment

GB10 scripts require machine-specific variables. Keep their values outside
tracked docs:

- `HEAD_HOST`
- `WORKER_HOST`
- `HEAD_ROCE_IP`
- `WORKER_ROCE_IP`
- `ROCE_IFACE`
- `NCCL_IB_HCA`
- `VLLM_ROOT`
- `VLLM_VENV`

Use remote absolute paths in ignored local config. Do not write literal
`$HOME/...` for `VLLM_ROOT` or `VLLM_VENV` in `.env`: the harness sources
`.env` on the local machine before building SSH commands, so `$HOME` would
expand to the local user's home rather than the GB10 node's home. If a handoff
uses `$HOME/...`, resolve it with `ssh HEAD_HOST 'printf %s "$HOME"'` and store
the resulting remote absolute path in ignored local config.

Preflight checks should confirm:

- both nodes can run the target vLLM venv Python;
- the remote harness root is reachable from the head node;
- no stale vLLM serve process is running on either node;
- driver health is clean before the run;
- the context guard in `scripts/run_gb10_forum53_multi_user_gate.sh` is not
  bypassed unless the run is explicitly destructive pressure testing.

## 5. First Run Order

Use this order for a new candidate:

1. RTX EP-off sparse attribution control.
2. RTX EP-on comparison only if MoE/EP balance is part of the hypothesis.
3. RTX GSM8K limit-200 if the route affects sparse-MLA, MoE, DFlash,
   speculative decode, scheduler, or attention helpers.
4. RTX local quality expansion after a positive attribution signal.
5. GB10 sparse attribution confirmation.
6. GB10 forum53 / MTP2 MoE TP gates if the candidate touches scheduler, KV,
   MoE, MTP, prefix-cache, or memory pressure.

Stop early if GSM8K fails, `FULL_AND_PIECEWISE` startup fails, sparse
attribution does not explain the endpoint gain, or GB10 driver-health signals
appear.
