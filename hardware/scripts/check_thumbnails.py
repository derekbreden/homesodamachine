#!/usr/bin/env python3
"""Which tracked solids have a picture older than themselves.

`/3d` serves `<file>.step.png` for the catalog grid and docs embed the same file, so a
thumbnail is what a reader sees when they do not open the model. It is drawn beside the STEP
by whatever run exported it — `_cadq_export` queues one and `tools/render/render-thumbnails.js`
draws the batch at process exit. A bazel action holds the render tool, which `graph.json`
declares for every step that cuts a `.step`, and draws the picture inside its sandbox; the
picture is in no step's `outs`, so nothing carries it out and the tree keeps the one it had.

So a STEP that reaches the tree by any road arrives with the picture it had before. The
comparison is the one `_cadq_export._current` makes: a picture older than the solid beside it
was made from bytes that have since moved. A solid the deploy fetched reads as older than every
picture — the bundle carries no mtime — which is the answer, the picture in the index having been
drawn against the bytes the lock names.

Naming them costs a stat each and nothing else. Drawing them costs a browser, which is a
follow-up commit's work:

    node tools/render/render-thumbnails.js <step>...
"""
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _solids import solids as _solids


def stale(root: Path, named: list) -> list:
    """Every named `.step` whose `.step.png` is older than it, by name."""
    out = []
    for rel in named:
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
    behind = stale(_ROOT, _solids())
    if not behind:
        return 0
    print(f"{len(behind)} solid(s) carry a picture older than themselves:")
    for rel in behind[:12]:
        print(f"    {rel}.png")
    if len(behind) > 12:
        print(f"    … and {len(behind) - 12} more")
    # ZSH DOES NOT WORD-SPLIT AN UNQUOTED PARAMETER EXPANSION, so a list held in a variable
    # arrives as one argument and the tool answers "not a .step under a known content root"
    # for a path that is fine — the shell's doing, read as the tool's. This form splits.
    print("  drawing them is a follow-up commit's work:")
    print("    printf '%s\\n' \\")
    for rel in behind:
        print(f"      {rel} \\")
    print("      | tr '\\n' '\\0' | xargs -0 node tools/render/render-thumbnails.js")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
