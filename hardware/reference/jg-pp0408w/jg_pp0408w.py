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

RING_D = 15.10          # collet-ring body OD — the fitting's widest section, at both ends
RING_LEN = 12.08        # that body's length, per end
BARREL_D = 9.31         # centre barrel OD — the narrowest section
BARREL_LEN = 12.16      # its length
COLLET_D = 9.57         # release sleeve OD
COLLET_WALL = 1.44      # its wall — the annular face a release plate or a thumb bears on
PORT_D = 6.35           # 1/4" tube OD, the bore each end accepts
BODY_LEN = 36.32        # ring + barrel + ring, collets excluded
OVERALL = 41.80         # collets in their default EXTENDED position — the envelope to space to
OVERALL_PRESSED = 39.13  # the same with both sleeves pushed fully in
INSERTION = 16.0        # how far a tube runs into each end before it bottoms

COLLET_BORE = COLLET_D - 2.0 * COLLET_WALL      # 6.69 — the tube passes with 0.35 of slip
# What one sleeve stands proud of its own body end face, extended, and the travel a thumb
# takes out of that before the teeth let go.
COLLET_PROUD = (OVERALL - BODY_LEN) / 2.0
COLLET_TRAVEL = (OVERALL - OVERALL_PRESSED) / 2.0
# The through passage standing between the two tube ends, at the bore of the tube itself.
BORE_D = 4.32           # 1/4" LLDPE ID

# Seating planes along Z, from the mid-plane out. The far end mirrors these.
barrel_face_z = BARREL_LEN / 2.0
ring_face_z = barrel_face_z + RING_LEN
port_face_z = ring_face_z + COLLET_PROUD


def port(side: float) -> tuple:
    """One of the two 1/4" tube ports: `(position, outward axis)`, `side` picking the near
    (+Z) or far (−Z) end. The station is the RELEASE SLEEVE'S own outer face — the plane a
    tube crosses to enter, and runs `INSERTION` beyond."""
    s = 1.0 if side > 0 else -1.0
    return ((0.0, 0.0, s * port_face_z), (0.0, 0.0, s))


def envelope() -> tuple:
    """`(diameter, length)` the fitting takes, sleeves extended — what crowds a neighbour."""
    return (RING_D, OVERALL)


def reach() -> float:
    """Mid-plane to port face — half the envelope, and how far the fitting hangs below a
    body seated on its upper port."""
    return port_face_z


def main():
    print("John Guest PP0408W")
    print(f"  STEP: {STEP_PATH}")
    print(f"  Display payload: {PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
