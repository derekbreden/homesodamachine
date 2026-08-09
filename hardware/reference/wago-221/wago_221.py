"""Reference solids for the WAGO 221 COMPACT lever nuts this machine splices in —
221-413, 221-415 and 221-420.

Each is a free connector with no mounting hole, so a printed press-fit well is the
whole mount (`enclosure._side_wells`) and the solid here is the body envelope plus
the closed levers.

Coordinate frame
----------------
- X = width (the lever-hinge axis), Y = depth (wire-entry axis), Z = height up from
  the base. Origin at the body-footprint center; Z = 0 the seating plane.
- Wires enter the +Y face. The 413 and 415 carry one row of levers, flipping up on
  the +Z face. The 420 carries two rows on one busbar: five levers on +Z and five on
  −Z, with all ten ports on the same +Y face.
- The levers sit within the closed envelope; `lever_open` is what one reaches
  swung fully back off the face it hinges on.
- The rear half of the depth is blank on every face — the levers and ports live in
  the front half, which is what a well grips.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

# --- Datasheet geometry ----------------------------------------------------
# width (X) × height (Z) × depth (Y), poles, rows of levers
SIZES = {
    "413": {"width": 18.8, "height": 8.4, "depth": 18.6, "poles": 3, "rows": 1},
    "415": {"width": 30.0, "height": 8.4, "depth": 18.6, "poles": 5, "rows": 1},
    "420": {"width": 29.8, "height": 15.8, "depth": 18.3, "poles": 10, "rows": 2},
}
lever_open = 15.25     # measured on a 221-413, levers fully up off the seating plane
lever_swing = lever_open - SIZES["413"]["height"]      # 6.85, off the hinging face

groove_w = 3.0         # X per lever-indicating groove
groove_d = 9.0         # Y reach of a groove — the front half; the rear half is blank
groove_h = 0.6

# The 221-413's own numbers, for the callers that only ever wanted the one size.
width = SIZES["413"]["width"]
depth = SIZES["413"]["depth"]
height = SIZES["413"]["height"]
poles = SIZES["413"]["poles"]


def build(size="413"):
    s = SIZES[size]
    w, h, d = s["width"], s["height"], s["depth"]
    body = cq.Workplane("XY").box(w, d, h, centered=(True, True, False))
    per_row = s["poles"] // s["rows"]
    pitch = w / per_row
    faces = (h - groove_h,) if s["rows"] == 1 else (h - groove_h, 0.0)
    for z in faces:
        for i in range(per_row):
            cx = -w / 2.0 + pitch * (i + 0.5)
            groove = (
                cq.Workplane("XY")
                .box(groove_w, groove_d, groove_h, centered=(True, True, False))
                .translate((cx, d / 2.0 - groove_d / 2.0, z))
            )
            body = body.cut(groove)
    return body


def main():
    for size in SIZES:
        out = _here.parent / f"wago-221-{size}.step"
        export_step(build(size), str(out))
        print(f"-> {out.name}")


if __name__ == "__main__":
    main()
