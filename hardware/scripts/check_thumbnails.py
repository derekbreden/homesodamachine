#!/usr/bin/env python3
"""Which tracked solids have a picture older than themselves.

`/3d` serves `<file>.step.png` for the catalog grid and docs embed the same file, so a
thumbnail is what a reader sees when they do not open the model. It is drawn beside the STEP
by whatever run exported it — `_cadq_export` queues one and `tools/render/render-thumbnails.js`
draws the batch at process exit — and a bazel action draws none, because it holds no `tools/`
and the picture is in no step's `outs`.

So a STEP that reaches the tree by any other road arrives with the picture it had before. The
comparison is the one `_cadq_export._current` makes: a picture older than the solid beside it
was made from bytes that have since moved.

Naming them costs a stat each and nothing else. Drawing them costs a browser, which is a
follow-up commit's work:

    node tools/render/render-thumbnails.js <step>...
"""
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]


def stale(root: Path, tracked: list) -> list:
    """Every tracked `.step` whose `.step.png` is older than it, by name."""
    out = []
    for rel in tracked:
        if not rel.endswith(".step"):
            continue
        step, png = root / rel, root / (rel + ".png")
        try:
            if png.stat().st_mtime_ns < step.stat().st_mtime_ns:
                out.append(rel)
        except OSError:
            continue
    return sorted(out)


def selftest() -> int:
    import tempfile
    import os

    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "a.step").write_text("x")
        (root / "a.step.png").write_text("p")
        os.utime(root / "a.step.png", ns=(2_000_000_000_000_000_000,) * 2)
        os.utime(root / "a.step", ns=(1_000_000_000_000_000_000,) * 2)
        hold("a picture newer than its solid is not named", stale(root, ["a.step"]), [])

        os.utime(root / "a.step", ns=(3_000_000_000_000_000_000,) * 2)
        hold("a picture older than its solid is named", stale(root, ["a.step"]), ["a.step"])

        (root / "b.step").write_text("x")
        hold("a solid with no picture at all is not named", stale(root, ["b.step"]), [])
        hold("a file that is not a solid is not named", stale(root, ["a.step.png"]), [])

    print(f"check_thumbnails selftest {holds}/4")
    return 0 if holds == 4 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    tracked = subprocess.run(["git", "ls-files"], cwd=_ROOT,
                             capture_output=True, text=True).stdout.split()
    behind = stale(_ROOT, tracked)
    if not behind:
        return 0
    print(f"{len(behind)} solid(s) carry a picture older than themselves:")
    for rel in behind[:12]:
        print(f"    {rel}.png")
    if len(behind) > 12:
        print(f"    … and {len(behind) - 12} more")
    print("  drawing them is a follow-up commit's work:")
    print(f"    node tools/render/render-thumbnails.js {' '.join(behind[:3])}"
          + (" …" if len(behind) > 3 else ""))
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
