"""
Isometric line-art view of the home-soda-machine enclosure — FRONT.

Canonical iso layout: top of enclosure at top of image, front face (y=0) at
lower-right, right side face (x=W) at lower-left.

Companion drawing: enclosure-iso-back.py (back face + left side + top).
Shared top-face features (GFCI band, pump door, hopper lid) and the
enclosure outer dimensions live in _common.py; both view scripts use them.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/enclosure-iso-front.py

Source for the feature inventory:
hardware/printed-parts/enclosure/README.md
"""

import math
import sys
from pathlib import Path

# tools/line-art/ for the drawing library; _HERE for the local _common
# module that carries the enclosure dimensions + shared top-face features.
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[3]
sys.path.insert(0, str(_REPO_ROOT / "tools" / "line-art"))
sys.path.insert(0, str(_HERE))

from line_art import Scene, Box
import _common as common


# Dispense tip — reuses the under-counter faucet's tip section. The
# faucet's gooseneck path bends 30° + 110° = 140° from vertical
# (gn_bend1_sweep_rad + gn_bend2_sweep_rad in
# hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py), so
# the tip ends at 180° - 140° = 40° from straight down. In the
# appliance frame the tip's axis has no horizontal-width component
# (it sits on the front face's center line under the S3), so the
# axis is purely (out-of-face, down) at that 40° tilt.
TIP_ANGLE_FROM_VERTICAL_DEG = 40.0
_tip_theta = math.radians(TIP_ANGLE_FROM_VERTICAL_DEG)
TIP_AXIS_3D = (0.0, -math.sin(_tip_theta), -math.cos(_tip_theta))

# Cylinder length matches gn_tip_straight_len in the faucet shell;
# diameter is the faucet shell's tube-shell outer envelope rounded
# (the actual cross-section is a stadium ~21 × 24 mm — water bore +
# flavor pill side-by-side).
TIP_LENGTH = 25.0
TIP_DIAMETER = 20.0

# Push button — large rectangular protrusion below the dispense tip.
# Sized so a glass rim raised to the dispense level can press it; wide
# enough that a finger can also press it.
BUTTON_W = 80.0
BUTTON_H = 20.0
BUTTON_PROTRUSION = 10.0

# Front-face vertical (b) positions on the centerline (a = hopper_door_a):
#   S3 at 235 (already placed).
#   Tip's back rim center at 200 — leaves the elliptical back rim
#     clear of the S3 above and exits the cylinder at b ≈ 181 mm above
#     the counter, leaving room for a tall glass underneath.
#   Push button at 170 — at the glass-rim height when the glass is
#     raised under the spout. The tip and button overlap in this 2D
#     iso projection but not in 3D: the tip sits in front of the
#     button physically, and a proper hidden-line removal would
#     occlude the button behind the tip. The wireframe line art
#     here doesn't do that.
TIP_AT = (None, 200.0)  # a filled in from common.hopper_door_a in main()
BUTTON_AT = (None, 170.0)


def main() -> None:
    scene = Scene(view="front")
    appliance = scene.add(Box(W=common.APPLIANCE_W, D=common.APPLIANCE_D, H=common.APPLIANCE_H))

    # Front face: ESP32-S3 rotary display (~32 mm OD), protruding 19 mm
    # so its sides can be gripped to turn it. Placed high on the front
    # face and horizontally aligned with the hopper lid above so the
    # funnel — not the pump cartridge — sits behind it. The funnel's
    # geometry leaves a small amount of interior depth at this height;
    # the pump cartridge would not, since its case fills the volume
    # below its door right up to the FRONT_MARGIN buffer.
    appliance.front.add_knob(
        at=(common.hopper_door_a, 235), d=32, protrusion=19, label="ESP32-S3"
    )

    # Front face: dispense tip — same tip section as the under-counter
    # faucet (see TIP_* module constants above for the angle / length /
    # diameter math). The cylinder's axis is tilted, so the line art
    # draws an elliptical back rim where the tip meets the front face.
    appliance.front.add_knob(
        at=(common.hopper_door_a, TIP_AT[1]),
        d=TIP_DIAMETER,
        protrusion=TIP_LENGTH,
        axis_3d=TIP_AXIS_3D,
        label="dispense tip",
    )

    # Front face: push button — receives a glass rim or a finger press
    # to start dispensing. Mounted just below the tip.
    appliance.front.add_rectangular_protrusion(
        at=(common.hopper_door_a, BUTTON_AT[1]),
        w=BUTTON_W,
        h=BUTTON_H,
        protrusion=BUTTON_PROTRUSION,
        label="dispense button",
    )

    # Top face: shared features (GFCI band, pump door, hopper lid).
    common.add_top_face_features(appliance)

    output_path = _HERE / "enclosure-iso-front.svg"
    scene.render(str(output_path))
    print(f"Wrote {output_path}")

    # Keep _common.py's [value](NAME) link comments in sync with current values.
    common.refresh_comments()
    print(f"-> updated comments in _common.py")


if __name__ == "__main__":
    main()
