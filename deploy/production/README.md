# Isolated production install

Production serves from `$PROD` (default `~/prod`) and reads nothing from any
development tree.

```
$PROD/vllm    standalone git repo, pinned to one SHA, with all build outputs
$PROD/venv    its own venv, editable install repointed at $PROD/vllm
$PROD/run/    per-replica logs
```

## Why

Before this, production ran from a git **worktree** whose gitdir lived inside a
development repo, using a venv that lived inside that same development tree,
whose editable install pointed back at the worktree:

```
prod tree .git ──▶ dev-repo/.git/worktrees/…
prod venv      ──▶ lives inside dev-repo/.venv
venv editable  ──▶ points at the prod tree
```

A rebuild or `uv pip install` in the development tree would have changed what
production imports, with nothing to signal it. The three links are now cut.

**What proves it is cut**: the serving process's memory maps contain zero
references to the development paths.

```bash
p=$(pgrep -f 'vllm.entrypoints' | head -1); grep -c '/tmp/' /proc/$p/maps
```

## Bring-up

Run on every node, with the same SHA:

```bash
SRC_TREE=<built tree> SRC_REPO=<git repo> ./make_prod_install.sh <sha>
```

Then on each replica's head node:

```bash
HARNESS=<harness checkout> HEAD_HOST=… WORKER_HOST=… \
  HEAD_ROCE_IP=… WORKER_ROCE_IP=… LABEL=replicaA ./launch_replica.sh
```

## Notes that cost time to learn

**Copy the whole built tree; do not cherry-pick artifacts.** A first version
copied only `*.so` and produced a tree that imported but warned
`No module named 'vllm._version'`. The build also emits ~14 generated `.py`
files and whole directories (`vllm_flash_attn`, `third_party/triton_kernels`).

**Do not rebuild to pin a new SHA if the delta is Python-only.** Check first:

```bash
git diff --name-only <built-sha> <target-sha> | grep -v '\.py$'
```

Empty means the existing artifacts are valid. Rebuilding takes hours and risks
producing something other than what was accepted.

**Fetch by ref, verify by SHA.** `git fetch origin <sha>` needs the serving side
to allow arbitrary SHA-1s in want, which a local repo does not
("couldn't find remote ref"). And the source repo here is shallow, so a full
fetch dies with "shallow roots are not allowed to be updated". `--depth=1` on a
named ref works; the SHA assertion afterwards is what makes naming a ref safe.

**Replace the worktree `.git` with a real repo.** The launcher's tree-parity
check runs `git rev-parse`; on a broken gitdir pointer it prints
"not a git tree" and **skips**, which reads like a check that ran.

**Stopping is harder than it looks** — see the comments in `stop_replica.sh`.
Four separate attempts failed on 2026-08-10, including a `pkill -f` pattern that
matched the killing shell's own command line and killed it first.
