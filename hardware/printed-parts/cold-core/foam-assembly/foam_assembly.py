"""Cold-core foam assembly — the foam shell with its thin top lid seated as in
the finished build, so the lid fit and the CO2 pass-through alignment can be
checked before printing.

Coordinate frame is the foam shell's (Z+ up, floor on z=0): the foam-shell spans
z = 0 .. 213.4 — floor closed at the bottom, open at the top where the body foam
is poured. The lid seats on the shell's top edge, covering the cured foam as the
most-+Z layer. There is no bottom cap; the shell's own floor closes the underside.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
_cold_core = _hw / "printed-parts" / "cold-core"
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_cold_core))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
from _cadq_export import export_assembly

SHELL_STEP = _cold_core / "foam-shell" / "foam-shell.step"
LID_STEP = _cold_core / "foam-lid" / "foam-lid.step"

SHELL_COLOR = cq.Color(0.62, 0.78, 0.95, 0.25)  # translucent, the lid reads through
LID_COLOR = cq.Color(0.90, 0.66, 0.32)          # amber


def _load(path):
    return cq.importers.importStep(str(path)).val()


def build():
    shell = _load(SHELL_STEP)
    shell_bb = shell.BoundingBox()
    lid = _load(LID_STEP)
    lid_bb = lid.BoundingBox()
    lid = lid.translate((0, 0, shell_bb.zmax - lid_bb.zmin))  # lid floor on shell top

    placed = {
        "foam-shell": (shell, SHELL_COLOR),
        "foam-lid": (lid, LID_COLOR),
    }
    assy = cq.Assembly(name="foam-assembly")
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    return assy, placed


def _report(placed):
    print("  part          X range            Y range            Z range")
    for name, (shape, _c) in placed.items():
        b = shape.BoundingBox()
        print(
            "  %-12s [%7.1f,%7.1f]  [%7.1f,%7.1f]  [%7.1f,%7.1f]"
            % (name, b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)
        )
    names = list(placed)
    clash = placed[names[0]][0].intersect(placed[names[1]][0]).Volume()
    print("  shell/lid mate at zero volume  OK" if clash < 1e-3
          else "  ** SHELL/LID CLASH %.2f mm^3 **" % clash)


def main():
    assy, placed = build()
    out = _here.parent / "foam-assembly.step"
    export_assembly(assy, str(out))
    print("-> foam-assembly.step")
    _report(placed)


if __name__ == "__main__":
    main()
