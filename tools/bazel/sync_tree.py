#!/usr/bin/env python3
"""Carry what the build cut into the tree that commits it.

    tools/cad-venv/bin/python tools/bazel/sync_tree.py            # what differs
    tools/cad-venv/bin/python tools/bazel/sync_tree.py --write    # and copy it in

Bazel cuts into `bazel-bin/`, and this repo commits its solids and its docs, because a reader
at `/3d` and a shop printing a part both take them off the tree rather than off a build. So the
two live side by side: the build is what decides the bytes, and this is what hands them over.

WHAT DIFFERS IS THE READING. A tree that comes back with nothing to copy is a tree holding the
artifacts its sources make, which is the same question `verify_clean` used to ask by running
every generator — asked here for the cost of a comparison, because the build already ran.
"""

import argparse
import filecmp
import json
import shutil
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
BAZEL_BIN = _ROOT / "bazel-bin" / "out"


def _targets() -> dict:
    """`{bazel output path: tracked path}` — read off the BUILD file's own outs."""
    q = subprocess.run(["bazel", "cquery", "//...", "--output=files"],
                       cwd=str(_ROOT), capture_output=True, text=True)
    tracked = {Path(f).name: f for f in subprocess.run(
        ["git", "-C", str(_ROOT), "ls-files"],
        capture_output=True, text=True, check=True).stdout.split()}
    out = {}
    for line in q.stdout.split():
        p = Path(line)
        if not p.name:
            continue
        # `out/<target>/<name>` and `out/<target>/doc/<name>` both land on the tracked file
        # of that name; a name the tree does not carry is a build-only artifact.
        hit = tracked.get(p.name)
        if hit:
            out[str(_ROOT / line)] = hit
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="copy what differs into the tree")
    args = ap.parse_args()

    pairs = _targets()
    if not pairs:
        print("  nothing built — run `bazel build //...` first")
        return 1

    differs, missing = [], []
    for built, tracked in sorted(pairs.items()):
        b, t = Path(built), _ROOT / tracked
        if not b.is_file():
            missing.append(tracked)
        elif not t.is_file() or not filecmp.cmp(b, t, shallow=False):
            differs.append((b, t, tracked))

    for _b, _t, rel in differs[:20]:
        print(f"  {rel}")
    if len(differs) > 20:
        print(f"  …and {len(differs) - 20} more")

    if args.write:
        for b, t, _rel in differs:
            shutil.copy2(b, t)
        print(f"{len(differs)} carried into the tree")
    else:
        print(f"{len(pairs) - len(differs) - len(missing)}/{len(pairs)} artifacts in the tree "
              f"are the ones the build cut"
              + (f", {len(missing)} not built" if missing else ""))
    return 0 if not differs else 1


if __name__ == "__main__":
    raise SystemExit(main())
