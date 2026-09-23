#!/usr/bin/env python3
"""check_tracked.py — whether the record beside each artifact is in the index.

A doc's figures and a picture's provenance each live in a file beside the thing they describe.
The pair is what any of the other checks read, and either half can leave the index on its own:
`git add -A` in a tree where one is missing records an absence nobody made.

    python3 hardware/scripts/check_tracked.py     (0 = paired, 1 = a record is not tracked)

`git ls-files` IS THE READING, and not the directory. A file the index does not hold is a file
a fresh clone does not have, however plainly it sits on this disk — and a directory listing
that finds it there is reading someone else's leftovers.
"""

import re
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_root = _hw.parent
sys.path.insert(0, str(_root / "tools"))
from check_paths import _pinned_copies  # noqa: E402

_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Z_][A-Z0-9_]*)\)")
FIGURES_SUFFIX = ".figures.json"
SCENE_SUFFIX = ".scene.json"


def _tracked() -> set:
    """Every path the index holds under `hardware/`, repo-relative."""
    out = subprocess.run(["git", "-C", str(_root), "ls-files", "hardware"],
                         capture_output=True, text=True, check=True).stdout
    return set(out.splitlines())


def main() -> int:
    tracked = _tracked()
    missing = []

    # A COPY A PACKAGE MANIFEST PINS BY BYTES QUOTES ITS DOC, figures and all. No generator
    # fills it, so no sidecar is owed for it — the rule `check_paths` reads such a copy by.
    pinned = _pinned_copies(tracked)
    for rel in sorted(t for t in tracked if t.endswith(".md") and t not in pinned):
        doc = _root / rel
        try:
            text = doc.read_text()
        except OSError:
            continue
        if "## Sources" not in text or not _LINK_RE.search(text):
            continue
        sidecar = rel[:-len(".md")] + FIGURES_SUFFIX
        if sidecar not in tracked:
            here = " (it is on this disk, untracked)" if (_root / sidecar).is_file() else ""
            missing.append(f"{sidecar} — the figures of {rel}{here}")

    for rel in sorted(t for t in tracked if t.endswith(".png") and "/scene-" in t):
        sidecar = rel + SCENE_SUFFIX
        if sidecar not in tracked:
            here = " (it is on this disk, untracked)" if (_root / sidecar).is_file() else ""
            missing.append(f"{sidecar} — what drew {rel}{here}")

    for m in missing:
        print(f"  {m}")
    if missing:
        print(f"\n  git add {' '.join(m.split(' — ')[0] for m in missing[:8])}")
    pairs = sum(1 for t in tracked
                if t.endswith(FIGURES_SUFFIX) or t.endswith(SCENE_SUFFIX)) + len(missing)
    print(f"{pairs - len(missing)}/{pairs} artifacts have their record in the index")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
