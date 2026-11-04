"""Line-art reference solid of the 1/4" push-to-connect through-wall
(bulkhead) union — the McMaster-Carr 51055K3 (gray acetal, NSF/ANSI 61
for drinking water), reduced to coaxial cylinders: a wide body, a
release ring, and the tube port — three concentric circles, which is
all of it a line drawing of the rear face can show.

Real-world dimensions (mm):
  Flange / collet body OD: 22.86 (0.90")
  Release ring OD: 11.43
  Threading / panel pass-through OD: 17.14 (0.67" mounting hole)
  Tube port bore: 6.35 (1/4" tube OD)
  Overall length: 34.29 (1.36")

Coordinate convention:
  Y = tube-flow axis. +Y = outward (toward the proud body's release ring
      and tube port). -Y = inward (threading and the far end).
  Origin = the body's panel-seating face (its inner face). The body and
      everything beyond it sit at y ≥ 0; the threading and far end sit
      at y < 0.
  +Z = up. X completes the right-handed frame.

Run:
    tools/cad-venv/bin/python hardware/reference/jg-bulkhead-union/jg_bulkhead_union.py

Geometry is held in the frozen STEP and fine payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from __future__ import annotations

import sys
from pathlib import Path


_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "printed-parts" / "cadlib"),
)

BODY_D = 22.86       # flange + collet barrel
RING_D = 11.43       # release ring
THREAD_D = 17.14     # threading / panel pass-through
PORT_D = 6.35        # 1/4" tube port bore

# Body + release ring at each end, threading spanning the middle; the
# segments sum to the 34.29 overall length.
BODY_LEN = 5.0
RING_LEN = 4.5
THREAD_LEN = 15.29
PORT_DEPTH = 4.0     # bore recess into each release-ring end face

# Length standing proud of the seating face (one body + release ring),
# clearing the mounting panel.
PROUD_LENGTH = BODY_LEN + RING_LEN

# Seating planes along Y where the coaxial segments meet. The near end
# stands at y ≥ 0; the threading and far end sit at y ≤ 0, mirrored
# about Y = -THREAD_LEN/2.
near_body_to_ring_y = BODY_LEN
near_ring_face_y = PROUD_LENGTH
far_thread_to_body_y = -THREAD_LEN
far_body_to_ring_y = -THREAD_LEN - BODY_LEN
far_ring_face_y = -THREAD_LEN - BODY_LEN - RING_LEN


# --- What a panel owes this fitting -----------------------------------------
# The union clamps THROUGH a wall, so a panel carrying one owes it two things and they are
# different sizes: a hole the THREADING passes through, and face room for the NUT that clamps
# on it. The nut is the wider by half again, so a row spaced to the holes fouls on the metal.

def panel_hole_d(clearance: float) -> float:
    """The through-hole diameter, given the slip a panel wants around the threading."""
    return THREAD_D + clearance


def panel_footprint() -> tuple:
    """`(width, height)` the clamping nut takes on the panel FACE. Round, so one figure
    twice — and it is what crowds a neighbour, a wall or a ceiling."""
    return (BODY_D, BODY_D)


def flange_footprint() -> float:
    """What the OUTBOARD flange covers, and so what a bulkhead ring has to reach past to show.
    The flange and the collet barrel are one diameter on this fitting."""
    return BODY_D


def port(side: float) -> tuple:
    """One of the two 1/4" tube ports: `(position, outward axis)`, `side` picking the near
    (+Y, outboard) or far (−Y, inboard) end. The bore is recessed into the release ring's own
    face, and a tube is pushed in to that face."""
    face = near_ring_face_y if side > 0 else far_ring_face_y
    return ((0.0, face, 0.0), (0.0, 1.0 if side > 0 else -1.0, 0.0))


_FROZEN_DIR = Path(__file__).resolve().parent
STEP_PATH = _FROZEN_DIR / 'jg-bulkhead-union.step'
PAYLOAD_PATH = _FROZEN_DIR / 'jg-bulkhead-union.step.mesh'
ASSET_MANIFEST_PATH = _FROZEN_DIR / "frozen-asset.json"


def main():
    print('jg-bulkhead-union frozen reference')
    print(f"  STEP: {STEP_PATH}")
    print(f"  Fine/display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
