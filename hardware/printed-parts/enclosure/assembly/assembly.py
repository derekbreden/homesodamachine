"""Kitchen Edition enclosure assembly — the shell wrapped around the contents.

Combines `../shell/shell.step` with the placed parts from
`../contents-assembly/contents_assembly.build()` in their shared coordinates.
The contents keep their per-part colors; the shell is translucent so the
arrangement reads through it.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware"))
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "contents-assembly"))
from _cadq_export import export_assembly
import contents_assembly as contents

SHELL_STEP = _repo / "hardware" / "printed-parts" / "enclosure" / "shell" / "shell.step"
SHELL_COLOR = cq.Color(0.85, 0.92, 1.00, 0.22)  # transparent PETG


def build():
    _contents_assy, placed = contents.build()
    shell = cq.importers.importStep(str(SHELL_STEP)).val()

    assy = cq.Assembly(name="kitchen-edition-enclosure-assembly")
    assy.add(shell, name="shell", color=SHELL_COLOR)
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    return assy


def main():
    assy = build()
    out = _here.parent / "assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
