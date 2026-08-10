#!/usr/bin/env bash
# Build an isolated production install on the node this runs on:
#
#   $PROD/vllm   standalone git repo, pinned to one SHA, with all build outputs
#   $PROD/venv   its own venv, repointed at that tree
#
# Run it on every node, with the same SHA.
#
#   SRC_TREE=... SRC_REPO=... ./make_prod_install.sh <sha>
#
# Why this exists: before it, production ran Python and compiled extensions from
# a git WORKTREE whose gitdir lived inside a development repo, using a venv that
# lived inside that same development tree, whose editable install pointed back at
# the worktree. Rebuilding or `uv pip install`-ing in the development tree would
# have changed what production imports, with nothing to signal it.
set -euo pipefail

SHA="${1:?usage: make_prod_install.sh <sha>}"
SRC_TREE="${SRC_TREE:?path to the BUILT tree (has the .so files)}"
SRC_REPO="${SRC_REPO:?path to the git repo to fetch from}"
SRC_VENV="${SRC_VENV:-$SRC_REPO/.venv}"
PROD="${PROD:-$HOME/prod}"
# The pinned SHA must be reachable from this ref in SRC_REPO.
REF="${REF:-refs/remotes/origin/codex/ds4-sm120-min-enable}"
PYVER="${PYVER:-python3.12}"

echo "=== $(hostname) : building $PROD at $SHA ==="
mkdir -p "$PROD"

# --- 1. code + every build output ----------------------------------------
# The whole built tree is copied rather than cherry-picking artifacts. A first
# version copied only *.so and produced a tree that imported but warned
# "No module named 'vllm._version'": the build also emits ~14 generated .py
# files and whole directories (vllm_flash_attn, third_party/triton_kernels).
# Enumerating what a build produces is a losing game.
if [ ! -e "$PROD/vllm/.git" ]; then
  rm -rf "$PROD/vllm"
  cp -a "$SRC_TREE" "$PROD/vllm"
  # The copied .git is a FILE pointing into the development repo's worktrees
  # directory. Left alone, production's git metadata still depends on that
  # repo -- and a broken pointer makes the launcher's tree-parity check print
  # "not a git tree" and SKIP, which reads like a check that ran.
  rm -rf "$PROD/vllm/.git"
  git -C "$PROD/vllm" init -q
  git -C "$PROD/vllm" remote add origin "$SRC_REPO"
fi

# Fetch by REF, not by raw SHA: `fetch origin <sha>` needs the serving side to
# allow arbitrary SHA-1s in want, which a local repo does not by default
# ("couldn't find remote ref"). --depth=1 because the source repo is itself
# shallow -- a full fetch dies with "shallow roots are not allowed to be
# updated" and never lands the commit. Production needs one tree, not history.
git -C "$PROD/vllm" fetch -q --depth=1 --no-tags origin "+$REF:refs/heads/prod"
# --hard updates tracked files; untracked build outputs are left alone.
git -C "$PROD/vllm" reset -q --hard refs/heads/prod

got=$(git -C "$PROD/vllm" rev-parse --short=10 HEAD)
# The ref is a moving target; the SHA is the contract. This check is what makes
# naming a branch above safe.
[ "$got" = "${SHA:0:10}" ] || { echo "FAIL: $REF is at $got, wanted ${SHA:0:10}"; exit 1; }

# --- 2. venv --------------------------------------------------------------
if [ ! -x "$PROD/venv/bin/python" ]; then
  rm -rf "$PROD/venv"
  cp -a "$SRC_VENV" "$PROD/venv"
fi

# Repoint the editable install. The launcher also sets PYTHONPATH, which would
# shadow this anyway -- but two mechanisms pointing at different trees is the
# kind of disagreement that stays invisible until it matters.
SP="$PROD/venv/lib/$PYVER/site-packages"
while IFS= read -r -d '' f; do
  if grep -q "$SRC_TREE" "$f" 2>/dev/null; then
    sed -i "s|$SRC_TREE|$PROD/vllm|g" "$f"
    echo "    repointed $(basename "$f")"
  fi
done < <(find "$SP" -maxdepth 1 \( -name '__editable__*' -o -name '*.pth' \) -type f -print0 2>/dev/null)

while IFS= read -r f; do
  sed -i "1s|^#\!$SRC_VENV|#!$PROD/venv|" "$f"
done < <(grep -rl "^#\!$SRC_VENV" "$PROD/venv/bin" 2>/dev/null || true)
sed -i "s|$SRC_VENV|$PROD/venv|g" "$PROD/venv/pyvenv.cfg" 2>/dev/null || true

# --- 3. verify ------------------------------------------------------------
echo "    --- verification ---"
printf "    sha             : %s\n" "$(git -C "$PROD/vllm" rev-parse --short=10 HEAD)"
printf "    dirty           : %s\n" "$(git -C "$PROD/vllm" status --porcelain --untracked-files=no | wc -l)"
printf "    standalone repo : %s\n" "$([ -d "$PROD/vllm/.git" ] && echo yes || echo NO)"
printf "    build artifacts : %s .so\n" "$(find "$PROD/vllm" -name '*.so' | wc -l)"

# Import with the launcher's PYTHONPATH, and again without it: both must land
# in production, or only one of them is really being exercised. stderr is kept
# -- the missing _version.py showed up only as a RuntimeWarning.
PYTHONPATH="$PROD/vllm" "$PROD/venv/bin/python" - 2>&1 <<PY | sed 's/^/    /'
import importlib, vllm
print("with PYTHONPATH   :", vllm.__file__)
print("version           :", vllm.__version__)
print("compiled ext      :", importlib.import_module("vllm._C_stable_libtorch").__file__)
PY

"$PROD/venv/bin/python" -c "import vllm; print('without PYTHONPATH:', vllm.__file__)" 2>&1 | sed 's/^/    /'

echo "=== $(hostname) done ==="
