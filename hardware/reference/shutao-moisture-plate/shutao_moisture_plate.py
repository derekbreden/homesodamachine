"""Shutao water/moisture sensor — the interdigitated FR-4 probe plate half of
the two-board LM393 module, the appliance's `moisture-sensor`. It lies flat in
the drip pan under the Multiplex atmospheric vent (which hovers ~0.4 mm above
it); the comparator board mounts off elsewhere.

External envelope only. A flat FR-4 rectangle — the interdigitated comb is
flush copper with no height — with two solder holes at the -X edge where the
leads land.

Frame: plate in the XY plane, underside at Z = 0; the two solder holes near the
-X edge. Origin centered on the plate.

Run:
    tools/cad-venv/bin/python hardware/reference/shutao-moisture-plate/shutao_moisture_plate.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

PLATE_X, PLATE_Y, PLATE_T = 54.0, 40.0, 1.6
HOLE_D = 1.2                 # lead solder holes
HOLE_INSET = 3.0            # from the -X edge
HOLE_PITCH = 2.54


def build():
    """Flat FR-4 plate with two lead-solder holes near the -X edge."""
    plate = cq.Workplane("XY").box(PLATE_X, PLATE_Y, PLATE_T, centered=(True, True, False))
    hx = -PLATE_X / 2.0 + HOLE_INSET
    y0 = -HOLE_PITCH / 2.0
    for i in range(2):
        hole = (
            cq.Workplane("XY")
            .circle(HOLE_D / 2.0)
            .extrude(PLATE_T)
            .translate((hx, y0 + i * HOLE_PITCH, 0))
        )
        plate = plate.cut(hole)
    return plate


def main():
    part = build()
    bb = part.val().BoundingBox()
    print("Shutao interdigitated moisture probe plate")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Plate {PLATE_X}×{PLATE_Y}×{PLATE_T}; 2 lead holes Ø{HOLE_D} at the -X edge")
    out = _here.parent / "shutao-moisture-plate.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
