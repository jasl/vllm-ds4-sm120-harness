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
# REFRESH_TREE=1 is required whenever the source tree was REBUILT -- any change
# to a .cu/.cpp/CMakeLists. `git reset --hard` below updates tracked files only,
# and the build outputs (*.so, generated .py, vllm_flash_attn/, triton_kernels/)
# are untracked, so without this an existing install takes the new Python and
# keeps the OLD binaries. That combination does not error; it just runs the
# wrong kernels. The artifact check at the end refuses to let it pass silently.
if [ ! -e "$PROD/vllm/.git" ] || [ "${REFRESH_TREE:-0}" = "1" ]; then
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
# REFRESH_VENV=1 is required whenever the source venv's packages moved -- a
# FlashInfer bump, a torch bump, anything. Without it this block is skipped for
# an existing install, and production ends up running new code against the old
# runtime: no error, just a mismatch nobody looks for. The tree SHA check below
# passes either way, which is exactly why it cannot be the only gate.
if [ ! -x "$PROD/venv/bin/python" ] || [ "${REFRESH_VENV:-0}" = "1" ]; then
  rm -rf "$PROD/venv"
  cp -a "$SRC_VENV" "$PROD/venv"
  echo "    venv copied from $SRC_VENV"
else
  echo "    venv kept (set REFRESH_VENV=1 if the source venv's packages moved)"
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

# Do the binaries in production match the ones that were built and tested?
# Comparing the tree SHA cannot answer this -- the SHA is a property of tracked
# files, and the binaries are untracked. Hash them.
src_h=$(find "$SRC_TREE" -name '*.so' -type f -exec sha256sum {} + 2>/dev/null |
  sed "s|$SRC_TREE/||" | sort | sha256sum | cut -c1-16)
prod_h=$(find "$PROD/vllm" -name '*.so' -type f -exec sha256sum {} + 2>/dev/null |
  sed "s|$PROD/vllm/||" | sort | sha256sum | cut -c1-16)
printf "    artifact digest : src=%s prod=%s\n" "$src_h" "$prod_h"
if [ "$src_h" != "$prod_h" ]; then
  echo "FAIL: production's compiled artifacts differ from the built tree."
  echo "      Re-run with REFRESH_TREE=1 -- a git reset does not replace untracked build outputs."
  exit 1
fi

# The digest above only proves prod matches ITS OWN source tree on THIS node.
# It says nothing about whether that source was ever updated and rebuilt: on a
# node whose SRC_TREE is stale, src and prod agree perfectly and both are old.
# That happened on 2026-08-12 -- two of four nodes took the new tracked files
# and kept binaries from the previous SHA, and the digest check passed.
#
# vllm.__version__ comes from the generated _version.py, a BUILD output, so it
# encodes the SHA the artifacts were compiled at rather than the one checked
# out. Comparing it to the SHA being promoted is what catches a stale source.
built_at=$("$PROD/venv/bin/python" -c "
import sys
sys.path.insert(0, '$PROD/vllm')
import vllm; print(vllm.__version__)
" 2>/dev/null | tail -1)
printf "    built at        : %s\n" "$built_at"
case "$built_at" in
  *"${SHA:0:9}"*) : ;;
  *)
    echo "FAIL: the artifacts were built at '$built_at', which does not carry ${SHA:0:9}."
    echo "      SRC_TREE ($SRC_TREE) was not updated and rebuilt on this node."
    exit 1
    ;;
esac

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

# The tree SHA says nothing about the runtime the tree runs against. Print the
# versions that actually decide behaviour so a stale venv is visible here
# rather than in a serve three steps later.
"$PROD/venv/bin/python" - 2>&1 <<'PYV' | sed 's/^/    /'
import importlib.metadata as m
ks = ["torch", "nvidia-nccl-cu13", "flashinfer-python", "flashinfer-cubin",
      "apache-tvm-ffi", "tilelang"]
for k in ks:
    try:
        print(f"runtime {k:<20} {m.version(k)}")
    except Exception:
        pass
PYV

echo "=== $(hostname) done ==="
