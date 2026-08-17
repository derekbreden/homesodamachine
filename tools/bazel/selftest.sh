#!/bin/sh
# Run one module's `selftest`. `gen_build.py` writes a target per module that defines one, and
# what that selftest was watched reading is the target's data — so one whose inputs have not
# moved is one `bazel test` does not run again.
#
# WHAT THESE HOLD IS A RULE AND NOT A DIMENSION. A seat does the same thing to a point, a
# direction and the metal; a clearance only ever removes poses; a station stands on the solid
# it was measured off; a chip fits the fitting it rings; a card's authored text survives a
# build handed stale figures. Each is answered against a fixture the selftest builds itself,
# and not one asserts a number the machine states — those move, and what is pinned to them is
# re-pinned by hand every time they do. If you reach for a selftest on a module that holds no
# such rule, ask why first.
#
# WHERE THESE WERE ALWAYS RUN IS THE TREE. `_realized.selftest` lays a temp package inside the
# repo root to walk imports across a real path, which a read-only runfiles tree refuses. What
# the test is cached on is still its declared data; what it runs in is the workspace.
#
# AND ITS TMPDIR IS ITS OWN. `lanes.py` keeps a snapshot of the standing machine under
# `tempfile.gettempdir()` and `held()` hands back ANY `hsm-lanes-*.json` there, newest first —
# so a test reading one is reading a file nobody declared, which may describe a machine that
# has since moved. It prints `TAKEN BEFORE … MOVED` and passes or fails without reading its
# own warning. A directory of its own means it finds nothing and builds what it measures.
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
