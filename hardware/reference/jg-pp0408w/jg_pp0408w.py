"""Line-art reference solid of the John Guest PP0408W 1/4" inline union — the
push-to-connect fitting that joins two lengths of 1/4" OD tube end to end.

White acetal copolymer, rotationally symmetric about the flow axis. In profile
it is a barbell: two collet-ring bodies with a narrower centre barrel between
them, and a release sleeve standing proud of each end face. A tube pushes in
until it bottoms; a thumb on the sleeve lets it back out. Every figure below is
photo-measured off the part in hand —
`hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`
is the measurement, and this is the solid struck from it.

A White faucet joins each flavour tube's white run to its black one with it
(`hardware/faucet-layout/`), and the collet press is shaped around it
(`hardware/printed-parts/collet-press/`).

Coordinate convention:
  Z = tube-flow axis, +Z toward the near port.
  Origin = the union's own mid-plane. The fitting is symmetric about it, so
      both ports stand at ±`OVERALL / 2` and neither end is the special one.

Geometry is in the frozen STEP and display payload beside this module.
`frozen-asset.json` records their bytes and source snapshot.
"""

from pathlib import Path

_here = Path(__file__).resolve()
STEP_PATH = _here.parent / "jg-pp0408w.step"
PAYLOAD_PATH = _here.parent / "jg-pp0408w.step.mesh"
ASSET_MANIFEST_PATH = _here.parent / "frozen-asset.json"

STEP = _here.parent / "jg-pp0408w.step"

# --- the measurement --------------------------------------------------------


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('jg_pp0408w')
globals().update({name: _reference_values[name] for name in ('RING_D', 'RING_LEN', 'BARREL_D', 'BARREL_LEN', 'COLLET_D', 'COLLET_WALL', 'PORT_D', 'BODY_LEN', 'OVERALL', 'OVERALL_PRESSED', 'INSERTION', 'COLLET_BORE', 'COLLET_PROUD', 'COLLET_TRAVEL', 'BORE_D', 'barrel_face_z', 'ring_face_z', 'port_face_z')})


# What one sleeve stands proud of its own body end face, extended, and the travel a thumb
# takes out of that before the teeth let go.
# The through passage standing between the two tube ends, at the bore of the tube itself.

# Seating planes along Z, from the mid-plane out. The far end mirrors these.


def port(side: float):
    'One of the two 1/4" tube ports: `(position, outward axis)`, `side` picking the near\n    (+Z) or far (−Z) end. The station is the RELEASE SLEEVE\'S own outer face — the plane a\n    tube crosses to enter, and runs `INSERTION` beyond.'
    return _reference_data('jg_pp0408w', 'port', (side,), {})


def envelope():
    '`(diameter, length)` the fitting takes, sleeves extended — what crowds a neighbour.'
    return _reference_data('jg_pp0408w', 'envelope', (), {})


def reach():
    'Mid-plane to port face — half the envelope, and how far the fitting hangs below a\n    body seated on its upper port.'
    return _reference_data('jg_pp0408w', 'reach', (), {})


def main():
    print("John Guest PP0408W")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
