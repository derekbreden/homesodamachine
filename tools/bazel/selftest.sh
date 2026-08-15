#!/bin/sh
# Run one module's `selftest`. `gen_build.py` writes a target per module that defines one, and
# what that selftest was watched reading is the target's data — so one whose inputs have not
# moved is one `bazel test` does not run again.
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
set -e
cd /Users/derekbredensteiner/Developer/homesodamachine
TMPDIR=$(mktemp -d "${TMPDIR:-/tmp}/hsm-selftest.XXXXXX")
export TMPDIR
trap 'rm -rf "$TMPDIR"' EXIT
exec ./tools/cad-venv/bin/python "$1" selftest
