"""
Isometric line-art view of the home-soda-machine enclosure.

Canonical iso layout: top of enclosure at top of image, front face (y=0) at
lower-right, right side face (x=W) at lower-left.

Run from the repo root:

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/drawings/enclosure-iso.py

Source for the feature inventory:
hardware/printed-parts/enclosure/README.md
"""

import sys
from pathlib import Path

# tools/line-art/ for the drawing library; tools/ for docgen;
# hardware/printed-parts/flavor/pump-case/ for the pump-case constants
# (case_outer_x, case_outer_z) we derive the pump-door size from.
_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[3]
sys.path.insert(0, str(_REPO_ROOT / "tools" / "line-art"))
sys.path.insert(0, str(_REPO_ROOT / "tools"))
sys.path.insert(0, str(_REPO_ROOT / "hardware" / "printed-parts" / "flavor" / "pump-case"))

from line_art import Scene, Box
from docgen import substitute_py_comments
from generate_step_cadquery import case_outer_x, case_outer_z


# ---------------------------------------------------------------------------
# Enclosure outer dimensions
# Working values per the enclosure README; replace with derived values when
# we wire foam-shell + Zone B/D heights.
# ---------------------------------------------------------------------------

APPLIANCE_W = 269.0
APPLIANCE_D = 280.0
APPLIANCE_H = 280.0


# ---------------------------------------------------------------------------
# Pump-cartridge access door — portrait orientation
# Two pump cases insert side-by-side along the appliance's depth axis;
# each case lays on its side so case_outer_z (its CAD-frame height)
# becomes the door's width and 2 × case_outer_x (two cases sharing the
# "75 mm" edge) becomes the door's depth. Clearance: 10 mm in the
# single-case-depth direction, 15 mm in the side-by-side direction.
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

# [103.5 mm](HOPPER_DOOR_W) — APPLIANCE_W − SIDE_MARGIN − pump_door_w − DOOR_GAP.
hopper_door_w = APPLIANCE_W - SIDE_MARGIN - pump_door_w - DOOR_GAP

# [165.0 mm](HOPPER_DOOR_D) — matches pump door depth for visual alignment.
hopper_door_d = pump_door_d


def main() -> None:
    scene = Scene()
    appliance = scene.add(Box(W=APPLIANCE_W, D=APPLIANCE_D, H=APPLIANCE_H))

    # Front face: ESP32-S3 rotary display (~32 mm OD).
    appliance.front.add_circle(at=(135, 140), d=32, label="ESP32-S3")

    # Top face: GFCI access band — 27 × 18 mm exposed band centered on the
    # 42 × 67 mm Legrand 1597 body underneath. Tucked into the back-right
    # corner with the body's tall axis along the appliance width. The body
    # sits flush against the back and right edges (5 mm clearance for the
    # mounting yoke); the band on the top face is 18 along a (width) × 27
    # along b (depth).
    appliance.top.add_rectangle(at=(230.5, 254), w=18, h=27, label="GFCI access band")

    # Top face: pump-cartridge access door (left), [145.5 mm](PUMP_DOOR_W) ×
    # [165.0 mm](PUMP_DOOR_D), pushed to the front of the top face.
    pump_door_a = SIDE_MARGIN + pump_door_w / 2
    pump_door_b = FRONT_MARGIN + pump_door_d / 2
    appliance.top.add_rectangle(
        at=(pump_door_a, pump_door_b),
        w=pump_door_w, h=pump_door_d,
        label="pump cartridge access door",
    )

    # Top face: hopper lid (right), [103.5 mm](HOPPER_DOOR_W) ×
    # [165.0 mm](HOPPER_DOOR_D), flush against the right edge.
    hopper_door_a = APPLIANCE_W - hopper_door_w / 2
    hopper_door_b = FRONT_MARGIN + hopper_door_d / 2
    appliance.top.add_rectangle(
        at=(hopper_door_a, hopper_door_b),
        w=hopper_door_w, h=hopper_door_d,
        label="hopper lid",
    )

    output_path = _HERE / "enclosure-iso.svg"
    scene.render(str(output_path))
    print(f"Wrote {output_path}")

    substitute_py_comments(
        Path(__file__),
        variables={
            "PUMP_DOOR_W": f"{pump_door_w:.1f} mm",
            "PUMP_DOOR_D": f"{pump_door_d:.1f} mm",
            "HOPPER_DOOR_W": f"{hopper_door_w:.1f} mm",
            "HOPPER_DOOR_D": f"{hopper_door_d:.1f} mm",
        },
        expected_counts={
            "PUMP_DOOR_W": 2,
            "PUMP_DOOR_D": 2,
            "HOPPER_DOOR_W": 2,
            "HOPPER_DOOR_D": 2,
        },
    )
    print(f"-> updated comments in {Path(__file__).name}")


if __name__ == "__main__":
    main()
