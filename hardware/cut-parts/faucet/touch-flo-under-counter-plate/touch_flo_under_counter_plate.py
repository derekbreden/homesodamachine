"""
Touch-Flo under-counter plate — sheet-metal plate that sits beneath
the countertop, between the countertop's underside and the
under-counter nut/washer that clamps the entire faucet stack from
below.

Disc with two open-edge channels — one for the shank, one for the
umbilical's flavor-tube bundle — and a shank pocket and a pill
pocket at the channels' inner ends. At install the plate slides
laterally from below onto the dangling umbilical; each cylinder
enters through its channel mouth and seats in its terminal pocket.
Washer and nut then clamp the plate flat against the countertop.
See `../../../assembly/faucet-and-umbilical.md` for the full install
motion.

HOLE POSITIONS MATCH THE TPU GASKET AND UPPER MOUNTING PLATE
============================================================
The mounting plate, TPU gasket, and under-counter plate share the
same disc center, shank-hole position, and pill-slot position. The
under-counter plate adds the two open-edge channels at those hole
positions.

CHANNEL DIRECTION
=================
Both channels extend in −Y of the DXF frame from their cylinder
pockets to the rim (= +Y in world, toward the back of the appliance):
- Shank channel: from the shank's bottom semicircle (DXF Y < 0)
  downward to the rim, matching the shank diameter in X.
- Pill channel: from the pill's bottom rectangle edge downward to
  the rim, matching the pill's short axis in X.

The shank pocket sits at X = 0 and the pill pocket sits at the
flavor-tube X offset; the two channels exit the rim at different
points on the lower arc.

CHANNEL-MOUTH FILLETS
=====================
Each of the four wall-meets-rim corners is rounded with a tangent
arc of the fillet radius.

STACK-UP (top → bottom, world-Z range in faucet-assembly coords):
- Mounting plate (PETG-CF), Z = [-4, 0]
- TPU gasket (90A black),    Z = [-6, -4]
- Countertop                  (varies — laminate ~32 mm, granite ~38 mm)
- Under-counter plate (this part)
- Washer + factory shank nut on the threaded Touch-Flo shank

THICKNESS / MATERIAL
====================
0.060" (1.524 mm) 304 stainless, SendCutSend. Order qty 1 per
appliance.

UNITS
=====
Drawing is in mm with $INSUNITS = 4.
"""

import sys
import math
from pathlib import Path

import ezdxf

_here = Path(__file__).resolve()
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
# _touch_flo_interface — the shared pill / shank geometry — lives in
# hardware/printed-parts/faucet/.
_hardware_dir = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware_dir / "printed-parts" / "faucet"))
sys.path.insert(0, str(_hardware_dir / "scripts"))
from docgen import substitute_py_comments
from _cadq_export import export_dxf
from _touch_flo_interface import (
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
)

# Dimensions in mm. DXF $INSUNITS = 4 (millimeters).
# Hole positions and disc center match the TPU gasket and the upper
# mounting plate.

# Disc center. A plain disc — a below-counter load-spreader and pull-out
# backing — sharing its center, shank, and pill positions with the upper
# mounting plate and TPU gasket, but not their (shell-foot) outline. The OD is
# derived below, once the pill (the farthest deck feature) is in hand.
disc_cx = 3.175
disc_cy = 0.0

shank_cx = 0.0
shank_cy = 0.0
# [12.6 mm](SHANK_HOLE_D) shank pocket — matches the gasket / mounting
# plate (the threaded shank passes through all three discs).
shank_diameter = shank_hole_diameter
shank_radius = shank_diameter / 2.0

# Pill is Y-oriented (matching the gasket): long axis along Y, short
# axis along X.
# DXF axes are the plate's own laser-cut frame: this DXF X is the
# depth-magnitude offset from the shank in world coords (the pill sits
# at world +Y relative to the body axis); this DXF Y is the lateral
# (world X) axis. Channels open in DXF -Y (lateral).
# [18.93 mm](FLAVOR_TUBE_X) DXF +X offset of pill center from the shank
# (= depth magnitude shared with the shell / gasket / mounting plate).
pill_cx = flavor_tube_depth
pill_cy = 0.0
# [13.4 mm](PILL_L) pill long axis in DXF Y (= world-lateral X) —
# matches the gasket's pill.
pill_long_y = pill_length_x
# [7.05 mm](PILL_W) pill short axis in DXF X (= world-depth Y) —
# matches the gasket's pill.
pill_short_x = pill_width_y
pill_half_long = pill_long_y / 2.0       # [6.7 mm](PILL_HALF_LONG)
pill_half_short = pill_short_x / 2.0     # [3.525 mm](PILL_HALF_SHORT)
pill_cap_radius = pill_half_short        # [3.525 mm](PILL_CAP_R)
pill_top_cap_cy = pill_cy + (pill_half_long - pill_cap_radius)   # [3.175 mm](PILL_TOP_CAP_CY)
pill_bot_cap_cy = pill_cy - (pill_half_long - pill_cap_radius)   # [-3.175 mm](PILL_BOT_CAP_CY)
pill_left_x = pill_cx - pill_half_short     # [15.4 mm](PILL_LEFT_X)
pill_right_x = pill_cx + pill_half_short    # [22.45 mm](PILL_RIGHT_X)

# Disc OD = reach to the pill's outer edge (pill_right_x, the farthest deck
# feature from the disc center) + a margin. That margin is set by the blind
# slide-on install — channel runway plus solid steel around the pockets — NOT
# by bearing: the shank nut is hand-tightened (~1-4 kN of clamp), which this
# disc spreads to ~2 MPa on the counter (about 5x under particleboard, ~100x
# under stone), so the counter never governs the size. [54.55 mm](PLATE_D) disc.
disc_reach_margin = 8.0
disc_radius = (pill_right_x - disc_cx) + disc_reach_margin
disc_diameter = 2.0 * disc_radius

# [1.5 mm](FILLET_R) fillet radius at the four channel-mouth corners
# where a vertical channel wall meets the disc rim.
fillet_radius = 1.5


def rim_y_lower(x):
    """Lower Y on the disc rim at the given X (the bottom of the disc)."""
    return disc_cy - math.sqrt(disc_radius ** 2 - (x - disc_cx) ** 2)


def channel_corner_fillet(wall_x, material_side, r=None):
    """
    (fillet_center, wall_tangent_pt, rim_tangent_pt) for an arc of
    radius r tangent to both the channel wall at x = wall_x and the
    lower disc rim. material_side = -1 when material lies at x < wall_x
    (left walls), +1 when material lies at x > wall_x (right walls).
    """
    if r is None:
        r = fillet_radius
    x_c = wall_x + material_side * r
    dx = x_c - disc_cx
    inner_r = disc_radius - r
    # Lower-half intersection — channels exit the rim at y < 0.
    y_c = disc_cy - math.sqrt(inner_r * inner_r - dx * dx)
    fillet_center = (x_c, y_c)
    wall_tangent = (wall_x, y_c)
    ux = (x_c - disc_cx) / inner_r
    uy = (y_c - disc_cy) / inner_r
    rim_tangent = (disc_cx + disc_radius * ux,
                   disc_cy + disc_radius * uy)
    return fillet_center, wall_tangent, rim_tangent


def ccw_arc(msp, center, radius, start_pt, end_pt):
    """CCW arc about center, from start_pt to end_pt."""
    start_angle = math.degrees(math.atan2(start_pt[1] - center[1], start_pt[0] - center[0]))
    end_angle = math.degrees(math.atan2(end_pt[1] - center[1], end_pt[0] - center[0]))
    if end_angle <= start_angle:
        end_angle += 360.0
    msp.add_arc(center, radius, start_angle=start_angle, end_angle=end_angle)


def make_dxf():
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 4   # 4 = millimeters
    msp = doc.modelspace()

    top_of_disc = (disc_cx, disc_cy + disc_radius)                     # ([3.175 mm](DISC_CX), [27.27 mm](TOP_OF_DISC_Y))

    # Shank channel — extends in -Y from the shank's bottom semicircle
    # to the rim, width [12.6 mm](SHANK_HOLE_D) in X.
    shank_left_wall_x = shank_cx - shank_radius                        # [-6.3 mm](SHANK_LEFT_WALL_X)
    shank_right_wall_x = shank_cx + shank_radius                       # [6.3 mm](SHANK_RIGHT_WALL_X)
    shank_left_wall_top = (shank_left_wall_x, shank_cy)                # ([-6.3 mm](SHANK_LEFT_WALL_X), 0)
    shank_right_wall_top = (shank_right_wall_x, shank_cy)              # ([6.3 mm](SHANK_RIGHT_WALL_X), 0)
    # Pill channel — extends in -Y from the pill rectangle's bottom
    # edge (Y = pill_bot_cap_cy = [-3.175 mm](PILL_BOT_CAP_CY)) to the rim,
    # width [7.05 mm](PILL_W) in X.
    pill_left_wall_top = (pill_left_x, pill_bot_cap_cy)                # ([15.4 mm](PILL_LEFT_X), [-3.175 mm](PILL_BOT_CAP_CY))
    pill_right_wall_top = (pill_right_x, pill_bot_cap_cy)              # ([22.45 mm](PILL_RIGHT_X), [-3.175 mm](PILL_BOT_CAP_CY))

    pill_rect_top_left = (pill_left_x, pill_top_cap_cy)                # ([15.4 mm](PILL_LEFT_X), [3.175 mm](PILL_TOP_CAP_CY))
    pill_rect_top_right = (pill_right_x, pill_top_cap_cy)              # ([22.45 mm](PILL_RIGHT_X), [3.175 mm](PILL_TOP_CAP_CY))

    disc_center = (disc_cx, disc_cy)

    # Fillets at the four channel-mouth corners.
    sl_c, sl_wt, sl_rt = channel_corner_fillet(shank_left_wall_x, -1)
    sr_c, sr_wt, sr_rt = channel_corner_fillet(shank_right_wall_x, +1)
    pl_c, pl_wt, pl_rt = channel_corner_fillet(pill_left_x, -1)
    pr_c, pr_wt, pr_rt = channel_corner_fillet(pill_right_x, +1)

    ccw_arc(msp, disc_center, disc_radius, top_of_disc, sl_rt)

    ccw_arc(msp, sl_c, fillet_radius, sl_rt, sl_wt)

    msp.add_line(sl_wt, shank_left_wall_top)

    # Upper semicircle — the pocket half that captures the shank.
    msp.add_arc((shank_cx, shank_cy), shank_radius,
                start_angle=0.0, end_angle=180.0)

    msp.add_line(shank_right_wall_top, sr_wt)

    ccw_arc(msp, sr_c, fillet_radius, sr_wt, sr_rt)

    # Rim arc across the strip of material between the two channels.
    ccw_arc(msp, disc_center, disc_radius, sr_rt, pl_rt)

    ccw_arc(msp, pl_c, fillet_radius, pl_rt, pl_wt)

    msp.add_line(pl_wt, pill_rect_top_left)

    # Upper semicircle — the pocket half that captures the pill.
    msp.add_arc((pill_cx, pill_top_cap_cy), pill_cap_radius,
                start_angle=0.0, end_angle=180.0)

    msp.add_line(pill_rect_top_right, pr_wt)

    ccw_arc(msp, pr_c, fillet_radius, pr_wt, pr_rt)

    ccw_arc(msp, disc_center, disc_radius, pr_rt, top_of_disc)

    out_dir = Path(__file__).resolve().parent
    out_name = "touch-flo-under-counter-plate"
    out = out_dir / f"{out_name}.dxf"
    export_dxf(doc, str(out))
    return out


if __name__ == "__main__":
    out = make_dxf()
    print("Touch-Flo under-counter plate")
    print(f"  Outline:        Ø {disc_diameter} mm disc, centered at ({disc_cx}, {disc_cy})")
    print(f"  Shank pocket:   Ø {shank_diameter} mm at ({shank_cx}, {shank_cy})")
    print(f"  Shank channel:  {shank_diameter} mm wide in X, -Y to the rim")
    print(f"  Pill pocket:    {pill_long_y} × {pill_short_x} mm Y-oriented stadium "
          f"at ({pill_cx}, {pill_cy})")
    print(f"  Pill channel:   {pill_short_x} mm wide in X, -Y to the rim")
    print(f"  Units in DXF:   mm (DXF $INSUNITS = 4)")
    print(f"  Material spec:  0.060\" (1.524 mm) 304 stainless, laser-cut, qty 1 per appliance")
    print(f"-> {out.name}")

    variables = {
        "PLATE_D": f"{disc_diameter:.4g} mm",
        "DISC_CX": f"{disc_cx:.4g} mm",
        "TOP_OF_DISC_Y": f"{disc_cy + disc_radius:.4g} mm",
        "SHANK_HOLE_D": f"{shank_diameter:.4g} mm",
        "SHANK_LEFT_WALL_X": f"{shank_cx - shank_radius:.4g} mm",
        "SHANK_RIGHT_WALL_X": f"{shank_cx + shank_radius:.4g} mm",
        "FLAVOR_TUBE_X": f"{pill_cx:.4g} mm",
        "PILL_L": f"{pill_long_y:.4g} mm",
        "PILL_W": f"{pill_short_x:.4g} mm",
        "PILL_HALF_LONG": f"{pill_half_long:.4g} mm",
        "PILL_HALF_SHORT": f"{pill_half_short:.4g} mm",
        "PILL_CAP_R": f"{pill_cap_radius:.4g} mm",
        "PILL_TOP_CAP_CY": f"{pill_top_cap_cy:.4g} mm",
        "PILL_BOT_CAP_CY": f"{pill_bot_cap_cy:.4g} mm",
        "PILL_LEFT_X": f"{pill_left_x:.4g} mm",
        "PILL_RIGHT_X": f"{pill_right_x:.4g} mm",
        "FILLET_R": f"{fillet_radius:.4g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "DISC_CX": 1,
            "TOP_OF_DISC_Y": 1,
            "SHANK_HOLE_D": 2,
            "SHANK_LEFT_WALL_X": 2,
            "SHANK_RIGHT_WALL_X": 2,
            "FLAVOR_TUBE_X": 1,
            "PILL_L": 1,
            "PILL_W": 2,
            "PILL_HALF_LONG": 1,
            "PILL_HALF_SHORT": 1,
            "PILL_CAP_R": 1,
            "PILL_TOP_CAP_CY": 3,
            "PILL_BOT_CAP_CY": 4,
            "PILL_LEFT_X": 3,
            "PILL_RIGHT_X": 3,
            "FILLET_R": 1,
        },
    )
    print(f"-> {Path(__file__).name}")
