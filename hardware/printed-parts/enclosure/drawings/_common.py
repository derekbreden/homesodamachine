"""
Shared constants and helpers for the enclosure isometric drawings.

Enclosure outer width + depth come from `_enclosure_dimensions` (which
derives them from foam-shell + condenser dimensions); pump-door +
hopper-lid dimensions come from the pump-case CAD constants; and
`add_top_face_features` adds the GFCI band + pump door + hopper lid
to a Box — which both the front-view and back-view drawings call, since
both views show the top face.

substitute_py_comments rewrites the [value](NAME) links in this file's
comments on every run via refresh_comments(), which the drawing scripts
call from their main().
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[3]
sys.path.insert(0, str(_REPO_ROOT / "tools"))
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "printed-parts" / "flavor" / "pump-case"))
sys.path.insert(0, str(_HERE.parent))

from docgen import substitute_py_comments
from pump_case import case_outer_x, case_outer_z
from _enclosure_dimensions import APPLIANCE_W, APPLIANCE_D


# ---------------------------------------------------------------------------
# Enclosure outer height
# Working value; not yet derived. Width + depth come from
# _enclosure_dimensions above.
# ---------------------------------------------------------------------------

APPLIANCE_H = 280.0


# ---------------------------------------------------------------------------
# Pump-cartridge access door — portrait orientation
# Two pump cases insert side-by-side along the appliance's depth axis;
# each case lays on its side so case_outer_z (its CAD-frame height)
# becomes the door's width and 2 × case_outer_x (two cases sharing the
# "75 mm" edge) becomes the door's depth.
# ---------------------------------------------------------------------------

PUMP_SIDE_BY_SIDE_CLEARANCE = 15.0
PUMP_CASE_DEPTH_CLEARANCE = 10.0

# [145.5 mm](PUMP_DOOR_W) — single-case depth + clearance, along the appliance width.
pump_door_w = case_outer_z + PUMP_CASE_DEPTH_CLEARANCE

# [165.0 mm](PUMP_DOOR_D) — two cases side-by-side + clearance, along the appliance depth.
pump_door_d = 2 * case_outer_x + PUMP_SIDE_BY_SIDE_CLEARANCE


# ---------------------------------------------------------------------------
# Hopper lid + top-face layout
# ---------------------------------------------------------------------------

FRONT_MARGIN = 10.0
SIDE_MARGIN = 10.0
DOOR_GAP = 10.0

# [107.5 mm](HOPPER_DOOR_W) — APPLIANCE_W − 2 × SIDE_MARGIN − pump_door_w − DOOR_GAP.
hopper_door_w = APPLIANCE_W - 2 * SIDE_MARGIN - pump_door_w - DOOR_GAP

# [165.0 mm](HOPPER_DOOR_D) — matches pump door depth.
hopper_door_d = pump_door_d


def add_top_face_features(appliance) -> None:
    """Add the GFCI access band, pump cartridge access door, and hopper lid
    to the top face of an appliance Box. Shared between the front-view and
    back-view drawings."""

    # GFCI access band — 27 × 18 mm exposed band centered on the 42 × 67
    # mm Legrand 1597 body underneath. Tucked into the back-right corner
    # with the body's tall axis (67 mm) along the appliance width. Body
    # sits flush against the back and right edges with 5 mm yoke clearance,
    # so the body center is 38.5 mm from the right edge (5 + 67/2) and
    # 26 mm from the back edge (5 + 42/2). On the top face the band is
    # 18 along a (width) × 27 along b (depth) — a tall-narrow band, not
    # a wide-flat one.
    appliance.top.add_rectangle(
        at=(APPLIANCE_W - 38.5, APPLIANCE_D - 26),
        w=18, h=27,
        label="GFCI access band",
    )

    # Pump-cartridge access door (left).
    pump_door_a = SIDE_MARGIN + pump_door_w / 2
    pump_door_b = FRONT_MARGIN + pump_door_d / 2
    appliance.top.add_rectangle(
        at=(pump_door_a, pump_door_b),
        w=pump_door_w, h=pump_door_d,
        label="pump cartridge access door",
    )

    # Hopper lid (right), with a SIDE_MARGIN to the right edge mirroring
    # the left-side gap of the pump door.
    hopper_door_a = APPLIANCE_W - SIDE_MARGIN - hopper_door_w / 2
    hopper_door_b = FRONT_MARGIN + hopper_door_d / 2
    appliance.top.add_rectangle(
        at=(hopper_door_a, hopper_door_b),
        w=hopper_door_w, h=hopper_door_d,
        label="hopper lid",
    )


def refresh_comments() -> None:
    """Refresh the [value](NAME) markdown links in this file's comments
    against current computed values. Called by each drawing script's main()
    so the comments stay live whichever drawing you regenerated."""
    substitute_py_comments(
        Path(__file__),
        variables={
            "PUMP_DOOR_W": f"{pump_door_w:.1f} mm",
            "PUMP_DOOR_D": f"{pump_door_d:.1f} mm",
            "HOPPER_DOOR_W": f"{hopper_door_w:.1f} mm",
            "HOPPER_DOOR_D": f"{hopper_door_d:.1f} mm",
        },
        expected_counts={
            "PUMP_DOOR_W": 1,
            "PUMP_DOOR_D": 1,
            "HOPPER_DOOR_W": 1,
            "HOPPER_DOOR_D": 1,
        },
    )


if __name__ == "__main__":
    refresh_comments()
    print(f"-> updated comments in {Path(__file__).name}")
