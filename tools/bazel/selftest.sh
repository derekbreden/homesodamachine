#!/bin/sh
# Run one module's `selftest`. `gen_build.py` writes a target per module that defines one, and
# what the module's selftest was watched reading is the target's data — so a selftest whose
# inputs have not moved is one `bazel test` does not run again.
#
# WHERE THESE WERE ALWAYS RUN IS THE TREE. `_realized.selftest` lays a temp package inside the
# repo root to walk imports across a real path, which a read-only runfiles tree refuses. What
# the test is cached on is still its declared data; what it runs in is the workspace.
set -e
cd /Users/derekbredensteiner/Developer/homesodamachine
exec ./tools/cad-venv/bin/python "$1" selftest
