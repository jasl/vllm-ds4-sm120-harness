#!/usr/bin/env bash
# Attribution control for tests/v1/spec_decode: does it wedge on the PRE-merge
# tree too? Without this, a timeout on the final head is unattributable -- it
# could be the merge, our changes, or the box. Same bound, same command.
set -uo pipefail
H=/home/jasl/tmp/ds4-sm120-harness
WT=/home/jasl/tmp/vllm-merge-20260711
PY=$H/vllm/.venv/bin/python
OUT=/home/jasl/tmp/spec_control; mkdir -p "$OUT"
exec 9>/home/jasl/tmp/.topo.lock
flock -w 21600 9 || { echo "ABORT: topo lock"; exit 9; }
cd "$WT"
here=$(git rev-parse --short=10 HEAD)
echo "=== spec_decode attribution control  $(date -Is) ==="
echo "  will test pre-merge 4ebd1fb698, then restore $here"
git stash -u >/dev/null 2>&1
git checkout --force 4ebd1fb698 >/dev/null 2>&1
echo "  on: $(git rev-parse --short=10 HEAD)"
timeout 1800 $PY -m pytest tests/v1/spec_decode -q -p no:cacheprovider > "$OUT/premerge.log" 2>&1
rc=$?
pkill -9 -f "[p]ytest tests/v1/spec_decode" 2>/dev/null; pkill -9 -f "[V]LLM::" 2>/dev/null; sleep 3
if [ "$rc" = "124" ]; then
  echo "  PRE-MERGE RESULT: TIMEOUT -- the wedge predates this work"
else
  echo "  PRE-MERGE RESULT: completed rc=$rc :: $(grep -aoE '[0-9]+ (passed|failed)' "$OUT/premerge.log" | tr '\n' ' ')"
  grep -aE "^FAILED" "$OUT/premerge.log" | head -6 | sed 's/^/    /'
fi
git checkout --force "$here" >/dev/null 2>&1
git stash pop >/dev/null 2>&1
find . -name "._*" -delete 2>/dev/null
echo "  restored to: $(git rev-parse --short=10 HEAD)  dirty=$(git status --porcelain --untracked-files=no|wc -l)"
echo "=== SPEC_CONTROL_DONE $(date -Is) ==="
