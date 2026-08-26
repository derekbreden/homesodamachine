#!/usr/bin/env python3
"""Whether BUILD.bazel is what the graph would write.

`graph.json` is the reading `trace_inputs.py` takes and `gen_build.py` renders BUILD.bazel
from it. The two are one answer in two files, and an action holds what its target names —
so a graph naming a source no target carries is a module the sandbox does not have, and the
step fails with `ModuleNotFoundError` on a file tracked and committed in the tree.

`check_declared_imports.py` cannot see this one: it reads the graph, and the graph is right.

IT REPORTS AND HOLDS NOTHING, which is the whole of why it is a `check_` here rather than a
gate. `gen_build.py --check` is the same reading and `.githooks/pre-commit` names its checks
one at a time — this is not one of them. Several sessions share the graph and one of them is
often part-way through moving it, so this row goes red while that is true and green on the
next reading; a red row is a thing to look at, not a thing to stop for.

    tools/cad-venv/bin/python tools/bazel/gen_build.py     writes it
"""
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]


def main() -> int:
    run = subprocess.run(
        [sys.executable, str(_HERE.parent / "gen_build.py"), "--check"],
        cwd=str(_ROOT), capture_output=True, text=True)
    if run.returncode == 0:
        print("check_build_file: BUILD.bazel is what the graph writes")
        return 0
    body = (run.stdout + run.stderr).strip().splitlines()
    print("BUILD.bazel is not what the graph would write now:")
    for line in body[:20]:
        print(f"  {line}")
    if len(body) > 20:
        print(f"  … {len(body) - 20} more line(s)")
    print("    tools/cad-venv/bin/python tools/bazel/gen_build.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
