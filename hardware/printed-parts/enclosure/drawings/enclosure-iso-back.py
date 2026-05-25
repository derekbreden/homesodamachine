"""
Isometric line-art view of the home-soda-machine enclosure — BACK.

Canonical iso layout: top of enclosure at top of image, back face (y=D) at
lower-right, left side face (x=0) at lower-left.

Companion drawing: enclosure-iso-front.py (front face + right side + top).

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/enclosure-iso-back.py

Source for the feature inventory:
hardware/printed-parts/enclosure/back-panel/README.md
hardware/printed-parts/enclosure/nameplate/README.md
"""

import math
import sys
from pathlib import Path

# tools/line-art/ for the drawing library.
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[3]
sys.path.insert(0, str(_REPO_ROOT / "tools" / "line-art"))

from line_art import Scene, Box


# ---------------------------------------------------------------------------
# Enclosure outer dimensions — matched to enclosure-iso-front.py.
# ---------------------------------------------------------------------------

APPLIANCE_W = 269.0
APPLIANCE_D = 280.0
APPLIANCE_H = 280.0


# ---------------------------------------------------------------------------
# Umbilical port — three Ø17 mm John Guest PP1208E bulkheads in a tangent
# triangular cluster on the back panel. Blue accent ring on the top-vertex
# bulkhead (the carbonated-water line). Sits high on the back panel where
# the umbilical comes down through the countertop from the under-cabinet
# faucet. Per hardware/printed-parts/enclosure/back-panel/README.md
# "Bulkhead array arrangement" + "Umbilical port — tube identification".
# ---------------------------------------------------------------------------

UMBILICAL_BULKHEAD_D = 17.0  # Ø17 mm panel hole per the back-panel README

# Equilateral triangle with side = bulkhead diameter (tangent circles). All
# three centers sit at distance s/√3 from the cluster centroid.
_S = UMBILICAL_BULKHEAD_D
TRIANGLE_VERTEX_OFFSET = _S / math.sqrt(3)        # 9.81 mm — centroid to apex
TRIANGLE_BASE_HALF_WIDTH = _S / 2                  # 8.5 mm — half of triangle base
TRIANGLE_BASE_OFFSET = _S * math.sqrt(3) / 6       # 4.91 mm — centroid to base midpoint

UMBILICAL_CLUSTER_A = APPLIANCE_W / 2              # centered horizontally on the back face
UMBILICAL_CLUSTER_B = APPLIANCE_H - 50             # 50 mm down from the top of the back face


# ---------------------------------------------------------------------------
# C14 AC inlet — IEC 60320 panel-mount receptacle cutout (~28 × 20 mm).
# Sits in the upper portion of the back face, off to one side of the
# umbilical cluster, where the electronics shelf is. Per back-panel
# README §1 "AC inlet" + finish-pack-ship cord-housing recess.
# ---------------------------------------------------------------------------

C14_CUTOUT_W = 28.0
C14_CUTOUT_H = 20.0
C14_A = 70.0
C14_B = APPLIANCE_H - 50


# ---------------------------------------------------------------------------
# Nameplate plaque — serialized rear-face plate per
# hardware/printed-parts/enclosure/nameplate/README.md. Size and exact
# position aren't locked in that doc; using a working 60 × 40 mm placed
# lower-right of the back face as a first pass.
# ---------------------------------------------------------------------------

NAMEPLATE_W = 60.0
NAMEPLATE_H = 40.0
NAMEPLATE_A = 200.0
NAMEPLATE_B = 60.0


def main() -> None:
    scene = Scene(view="back")
    appliance = scene.add(Box(W=APPLIANCE_W, D=APPLIANCE_D, H=APPLIANCE_H))

    # Umbilical cluster — three bulkheads in a tangent equilateral triangle.
    # Top-vertex bulkhead is the carbonated-water (blue) line; the two
    # bottom-vertex bulkheads are the flavor lines.
    appliance.back.add_circle(
        at=(UMBILICAL_CLUSTER_A, UMBILICAL_CLUSTER_B + TRIANGLE_VERTEX_OFFSET),
        d=UMBILICAL_BULKHEAD_D,
        label="umbilical: carbonated water (blue ring)",
    )
    appliance.back.add_circle(
        at=(UMBILICAL_CLUSTER_A - TRIANGLE_BASE_HALF_WIDTH,
            UMBILICAL_CLUSTER_B - TRIANGLE_BASE_OFFSET),
        d=UMBILICAL_BULKHEAD_D,
        label="umbilical: flavor A",
    )
    appliance.back.add_circle(
        at=(UMBILICAL_CLUSTER_A + TRIANGLE_BASE_HALF_WIDTH,
            UMBILICAL_CLUSTER_B - TRIANGLE_BASE_OFFSET),
        d=UMBILICAL_BULKHEAD_D,
        label="umbilical: flavor B",
    )

    # C14 AC inlet cutout.
    appliance.back.add_rectangle(
        at=(C14_A, C14_B), w=C14_CUTOUT_W, h=C14_CUTOUT_H,
        label="C14 AC inlet",
    )

    # Nameplate plaque.
    appliance.back.add_rectangle(
        at=(NAMEPLATE_A, NAMEPLATE_B), w=NAMEPLATE_W, h=NAMEPLATE_H,
        label="nameplate",
    )

    output_path = _HERE / "enclosure-iso-back.svg"
    scene.render(str(output_path))
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
