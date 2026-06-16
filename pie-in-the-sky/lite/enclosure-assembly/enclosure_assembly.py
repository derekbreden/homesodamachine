"""Lite Edition enclosure assembly — the shell wrapped around the contents.

Combines `../enclosure/enclosure.step` with the placed parts from
`_contents.build()` in their shared coordinates. The contents keep their
per-part colors; the shell is translucent so the arrangement reads through it.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_py_comments
import _contents as contents

SHELL_STEP = _repo / "pie-in-the-sky" / "lite" / "enclosure" / "enclosure.step"
SHELL_COLOR = cq.Color(0.85, 0.92, 1.00, 0.22)  # transparent PETG


def build():
    placed = contents.build()
    shell = cq.importers.importStep(str(SHELL_STEP)).val()

    assy = cq.Assembly(name="lite-enclosure-assembly")
    assy.add(shell, name="enclosure", color=SHELL_COLOR)
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    return assy


def main():
    assy = build()
    out = _here.parent / "enclosure-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")

    # Pin the hand-typed reservoir-wall coordinates in _contents.py's prose.
    substitute_py_comments(
        Path(contents.__file__),
        variables={
            "RES_X_FRONT": f"{contents.RES_X_FRONT:g}",
            "RES_Y_FRONT": f"{contents.RES_Y_FRONT:g}",
            "RES_Y_BACK": f"{contents.RES_Y_BACK:+g}",
        },
        expected_counts={
            "RES_X_FRONT": 1,
            "RES_Y_FRONT": 1,
            "RES_Y_BACK": 1,
        },
    )
    print("-> _contents.py")


if __name__ == "__main__":
    main()
