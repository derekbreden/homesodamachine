"""Reference solid for the WAGO 221-413 — 3-conductor COMPACT lever-nut
splicing connector, used 3x (H / N / G) as the AC distribution block on the
power tray.

Geometry from the official WAGO 221-413 datasheet. It is a free connector with
no mounting holes — the power tray retains it in a printed snap pocket, so the
solid here is the body envelope plus the three orange levers (modeled closed).

Coordinate frame
----------------
- X = width (18.8 mm, the lever-hinge axis), Y = depth (18.6 mm, wire-entry
  axis), Z = height up from the base. Origin at the body-footprint center;
  Z = 0 the seating plane.
- Wires enter the -Y face; levers flip up on the +Z face. Closed height 8.4 mm;
  a lever flipped fully open reaches ~15.25 mm (measured) — size pockets to clear
  it if the levers must be worked in place.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

# --- Measured / datasheet geometry ----------------------------------------
width = 18.8           # X (lever-hinge axis)
depth = 18.6           # Y (wire-entry axis)
height = 8.4           # Z, closed body
lever_open_z = 15.25   # measured height with a lever flipped fully open
poles = 3
groove_w = 3.0         # X per lever-indicating groove
groove_d = 9.0         # Y reach of a groove on the top face
groove_h = 0.6         # shallow, indicative only — closed levers stay within 8.4


def build():
    body = cq.Workplane("XY").box(width, depth, height, centered=(True, True, False))
    # Three shallow grooves on the top face mark the closed levers (no added
    # height — the 8.4 mm envelope already includes the levers down).
    pitch = width / poles
    for i in range(poles):
        cx = -width / 2.0 + pitch * (i + 0.5)
        groove = (
            cq.Workplane("XY")
            .box(groove_w, groove_d, groove_h, centered=(True, True, False))
            .translate((cx, depth / 2.0 - groove_d / 2.0, height - groove_h))
        )
        body = body.cut(groove)
    return body


def main():
    export_step(build(), str(_here.parent / "wago-221-413.step"))
    print("-> wago-221-413.step")


if __name__ == "__main__":
    main()
