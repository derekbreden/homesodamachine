#!/bin/sh
# Run one module's `selftest`. `gen_build.py` writes a target per module that defines one, and
# what that selftest was watched reading is the target's data — so one whose inputs have not
# moved is one `bazel test` does not run again.
#
# WHAT THESE HOLD IS A RULE AND NOT A DIMENSION. A seat does the same thing to a point, a
# direction and the metal; a clearance only ever removes poses; a station stands on the solid
# it was measured off; a chip fits the fitting it rings; a card's authored text survives a
# build handed stale figures. Each is answered against a fixture the selftest builds itself,
# and not one asserts a number the machine states.
#
# WHERE THESE WERE ALWAYS RUN IS THE TREE. `_realized.selftest` lays a temp package inside the
# repo root to walk imports across a real path, which a read-only runfiles tree refuses. What
# the test is cached on is still its declared data; what it runs in is the workspace.
#
# AND ITS TMPDIR IS ITS OWN, so what a selftest leaves in one goes when the test does. A hold
# that reads the world reads it under `lanes.snapshot(exact=True)`, which answers with the
# snapshot this tree's own sources name and stands the machine when there is none — the
# eight-minute build, kept in `.cache/lanes/` where the next reader finds it.
#
# AND THE TREE IT RUNS IN IS THE TREE BAZEL STAGED. The path below names one checkout, while
# a worktree of this repo is a second one that bazel serves from its own workspace — where
# `cd` lands on the first, and every hold reports on geometry the run was never handed. The
# module in the runfiles is what bazel staged; the module at that path is what is about to be
# read. Same bytes, same tree.
set -e
WORKSPACE=/Users/derekbredensteiner/Developer/homesodamachine
staged=$TEST_SRCDIR/${TEST_WORKSPACE:-_main}/$1
if [ -f "$staged" ] && ! cmp -s "$staged" "$WORKSPACE/$1"; then
  echo "selftest: $1 in $WORKSPACE is not the file bazel staged — this is another checkout" >&2
  exit 1
fi
cd "$WORKSPACE"
TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/hsm-selftest.XXXXXX")
export TMPDIR
trap 'rm -rf "$TMPDIR"' EXIT
exec ./tools/cad-venv/bin/python "$1" selftest
