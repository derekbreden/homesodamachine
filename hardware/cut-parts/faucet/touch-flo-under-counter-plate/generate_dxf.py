"""
Touch-Flo under-counter plate — sheet-metal plate that sits beneath the
countertop, between the countertop's underside and the under-counter
nut/washer that clamps the entire faucet stack from below.

KEYHOLE DESIGN — ONE PIECE WITH TWO OPEN-EDGE SLOTS
====================================================
The plate is a single rigid disc with the same Ø 54.35 mm outline,
same disc center, and the same shank-hole and pill-slot positions as
the upper printed mounting plate and the TPU gasket above the
countertop. The under-counter plate adds two narrow open-edge
channels — one from each cylinder pocket to the rim — so the customer
can slide the plate laterally onto the dangling umbilical from below
the countertop. Both cylinders enter through their channel mouths at
the rim and seat in their terminal pockets. Single piece, single slide
motion, no two-half alignment, no flex required, no closed pill slot
to thread tubes through at install.

HOLE POSITIONS MATCH THE TPU GASKET EXACTLY
============================================
The mounting plate, TPU gasket, and under-counter plate all sit on the
same shank with the same flavor tubes passing through the same pill
slot. Their hole patterns are identical: disc center at (3.175, 0),
shank hole at (0, 0), pill slot at (18.925, 0) with long axis along Y
(13.4 mm long, 7.05 mm wide; per _touch_flo_interface — was 13.2 × 6.85
prior to the 2026-05-25 clearance unification). The under-counter plate adds channels
without changing the hole positions, so it stacks naturally below
the gasket and the mounting plate without rotation or coordinate
translation.

CHANNEL DIRECTION
=================
Both channels extend in −Y from their cylinder pockets to the rim:
- Shank channel: from the shank's bottom semicircle (the lower half
  of the shank circle, Y < 0) downward to the rim. Width 12.6 mm in
  X (X from -6.3 to +6.3, matching the shank diameter).
- Pill channel: from the pill's bottom rectangle edge (Y = -3.175,
  replacing the bottom cap of the pill stadium) downward to the rim.
  Width 7.05 mm in X (X from 15.4 to 22.45, matching the pill's
  short axis).

Because the shank is at X = 0 and the pill is at X = 18.925, the two
channels are at different X ranges (X = [-6.3, +6.3] vs X = [15.4,
22.45]) and do not overlap. They exit the rim at different points on
the lower arc of the disc.

CHANNEL-MOUTH FILLETS
=====================
Each of the four corners where a channel wall meets the disc rim is
rounded with a small tangent arc (radius `fillet_radius`, default
1.5 mm). Each corner is geometrically acute — the rim and the wall
intersect at less than 90° — so without the fillet the part has four
sharp pointy tips on its lower edge. The fillets serve three
purposes: (a) remove the sharp tips for handling safety while the
plate is loose in the install bag; (b) create a lead-in funnel at
each channel mouth so the cylinders slide into the channel a little
more forgivingly during the lateral install motion; (c) eliminate the
laser's natural corner artifact (small dross blob at the inside of an
acute external corner). The clamping surface area lost to a 1.5 mm
fillet is negligible compared to the Ø 54 mm disc.

INSTALL SEQUENCE
================
1. Drop the faucet+umbilical assembly into the 1-3/8" countertop hole
   from above. The TPU mounting gasket (already on the shank from the
   factory bench) compresses against the countertop top surface.
2. From below: hold the plate horizontally against the countertop
   underside, oriented with the channel mouths facing the umbilical.
3. Slide the plate laterally past the cylinders. Both the shank and
   the tube bundle enter through their channel mouths at the rim and
   travel along the channels into their terminal pockets — the shank
   into its Ø 12.6 pocket at (0, 0), the two tubes into the pill at
   (18.925, 0).
4. Slide a washer onto the shank from below, against the plate.
5. Thread the factory shank nut onto the shank and tighten. The
   nut + washer clamp the plate flat against the countertop underside.

ANTI-ROTATION
=============
Built in. With the cylinders seated in their narrow channels at two
different X positions (one at X = 0, one at X = 18.925), any rotation
of the plate around the shank would force the pill to swing through
an arc — but the pill is held by the tube bundle in its channel,
which resists that arc. The two cylinders at different X provide a
moment arm that resists rotation. No silicone bumpers needed (unlike
the prior solid-disc design that this iteration supersedes).

PURPOSE (unchanged from prior iterations)
==========================================
- Distributes the under-counter nut's clamping force across a wide
  area so the nut doesn't dish or crush the countertop bottom.
- Provides a flat reference surface for the nut to bear against.
- Hole pattern matches the upper mounting plate and TPU gasket
  exactly — shank passes through, two flavor tubes pass through.

STACK-UP (top → bottom, world-Z range in faucet-assembly coords):
- Mounting plate (PETG-CF), Z = [-4, 0]
- TPU gasket (90A black),    Z = [-6, -4]
- Countertop                  (varies — laminate ~32 mm, granite ~38 mm)
- *** Under-counter plate (THIS PART — keyhole, one piece) ***
- Washer + factory shank nut on the threaded Touch-Flo shank

DESIGNS RULED OUT
=================
- "Split halves" (two D-shaped pieces clamped flat under the nut):
  works, but requires the customer to hold two pieces in alignment
  against the countertop underside while threading the nut.
  Three-hand install or contortion. Cylinders-in-channels of the
  keyhole design hold the plate in alignment passively.
- "Living hinge + snap latch" (single piece with a thin-bridge hinge
  joining two halves, latch on the opposite mating edge):
  304 SS yield strain ~0.1-0.2 %; a single 180° fold at 0.060" puts
  outer-fiber strain near 2 %. Fracture-on-install risk.
- "C-clip" (single piece with a 5 mm rim gap that the customer flexes
  open to slip around the umbilical):
  ~9 % diameter strain needed to open a Ø 54 mm ring by 5 mm. Two
  orders of magnitude past 304 SS elastic limit. Would plastically
  deform open and not spring back.
- "Tab-and-slot interlock between two halves": feasible at SCS minima
  (tab ≥ 0.060", slot ≥ tab + 0.010") but SCS does not guarantee
  press-fit tolerances, and the interlock buys nothing that the
  keyhole design's nut clamping doesn't already do.

THICKNESS / MATERIAL (specified at order time, not in the DXF)
==============================================================
- Recommended: 0.060" (1.524 mm) 304 stainless. SendCutSend stocks
  this exact gauge in 304; runs cheaper than 316 and is plenty for an
  under-counter location not in food contact.
- Order quantity: 1 per appliance.

UNITS
=====
Drawing is in mm with $INSUNITS = 4. SendCutSend's uploader confirms
units in the quoting UI; mm is supported alongside inches.

REGENERATE
==========
    tools/cad-venv/bin/python generate_dxf.py

(No CadQuery dependency — uses ezdxf directly.)
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
# _touch_flo_interface lives over in hardware/printed-parts/faucet/ — it
# defines the canonical pill / shank geometry shared by the upper
# mounting plate, the TPU gasket, the touch-flo shell, and this
# under-counter plate. Walk up to `hardware/`, then sideways into
# printed-parts/faucet/ so the import resolves.
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts" / "faucet"),
)
from docgen import substitute_py_comments
from _touch_flo_interface import (
    flavor_tube_x,
    pill_length_y,
    pill_width_x,
    shank_hole_diameter,
)

# Dimensions in mm. DXF $INSUNITS = 4 (millimeters).
# Hole positions match the TPU gasket and the upper mounting plate
# exactly. The disc is also unchanged in size and center.

# [54.35 mm](PLATE_D) disc OD — matches the upper mounting plate and
# the TPU gasket for a stacked, identically-sized disc footprint.
disc_diameter = 54.35
disc_radius = disc_diameter / 2.0
disc_cx = 3.175
disc_cy = 0.0

shank_cx = 0.0
shank_cy = 0.0
# [12.6 mm](SHANK_HOLE_D) shank pocket — matches the gasket / mounting
# plate (the threaded shank passes through all three discs). Imported
# from _touch_flo_interface.
shank_diameter = shank_hole_diameter
shank_radius = shank_diameter / 2.0

# Pill is Y-oriented (matching the gasket): long axis along Y, short
# axis along X. Geometry imported from _touch_flo_interface (single
# source of truth across the stack-up — was 13.2 × 6.85 mm here until
# 2026-05-25, when the gasket / mounting plate / this plate were all
# bumped up to the shell's print-validated 13.4 × 7.05 mm).
# [18.925 mm](FLAVOR_TUBE_X) +X offset of pill center from the shank —
# shared with the shell / gasket / mounting plate for stacked alignment.
pill_cx = flavor_tube_x
pill_cy = 0.0
# [13.4 mm](PILL_L) pill long axis (Y) — matches the gasket's pill.
pill_long_y = pill_length_y
# [7.05 mm](PILL_W) pill short axis (X) — matches the gasket's pill.
pill_short_x = pill_width_x
pill_half_long = pill_long_y / 2.0       # 6.7
pill_half_short = pill_short_x / 2.0     # 3.525
pill_cap_radius = pill_half_short        # 3.525
pill_top_cap_cy = pill_cy + (pill_half_long - pill_cap_radius)   # +3.175
pill_bot_cap_cy = pill_cy - (pill_half_long - pill_cap_radius)   # -3.175
pill_left_x = pill_cx - pill_half_short     # 15.4
pill_right_x = pill_cx + pill_half_short    # 22.45

# [1.5 mm](FILLET_R) fillet radius at the four channel-mouth corners
# where a vertical channel wall meets the disc rim. See the module
# docstring.
fillet_radius = 1.5


def rim_y_lower(x):
    """Lower Y on the disc rim at the given X (the bottom of the disc)."""
    return disc_cy - math.sqrt(disc_radius ** 2 - (x - disc_cx) ** 2)


def channel_corner_fillet(wall_x, material_side, r=None):
    """
    Compute fillet geometry for a corner where a vertical channel wall
    at x = wall_x meets the lower disc rim. material_side = -1 if the
    material lies at x < wall_x (left walls), +1 if material lies at
    x > wall_x (right walls).

    The fillet is a circular arc of radius r, tangent to both the wall
    and the rim. Its center sits inside the material — distance r from
    the wall, and distance r inside the rim arc (i.e. at distance
    R - r from the disc center).

    Returns (fillet_center, wall_tangent_pt, rim_tangent_pt).
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
    """Emit a CCW arc on the disc rim from start_pt to end_pt."""
    start_angle = math.degrees(math.atan2(start_pt[1] - center[1], start_pt[0] - center[0]))
    end_angle = math.degrees(math.atan2(end_pt[1] - center[1], end_pt[0] - center[0]))
    if end_angle <= start_angle:
        end_angle += 360.0
    msp.add_arc(center, radius, start_angle=start_angle, end_angle=end_angle)


def make_dxf():
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 4   # 4 = millimeters
    msp = doc.modelspace()

    # Key points on the plate boundary (going CCW from the top of the disc):
    top_of_disc = (disc_cx, disc_cy + disc_radius)                     # (3.175, +27.175)

    # Shank channel — extends in -Y from the shank's bottom semicircle
    # to the rim, width 12.6 mm in X.
    shank_left_wall_x = shank_cx - shank_radius                        # -6.3
    shank_right_wall_x = shank_cx + shank_radius                       # +6.3
    shank_left_wall_top = (shank_left_wall_x, shank_cy)                # (-6.3, 0)
    shank_right_wall_top = (shank_right_wall_x, shank_cy)              # (+6.3, 0)
    # Pill channel — extends in -Y from the pill rectangle's bottom
    # edge (Y = pill_bot_cap_cy = -3.175, replacing the bottom cap) to
    # the rim, width 7.05 mm in X.
    pill_left_wall_top = (pill_left_x, pill_bot_cap_cy)                # (15.4, -3.175)
    pill_right_wall_top = (pill_right_x, pill_bot_cap_cy)              # (22.45, -3.175)

    pill_rect_top_left = (pill_left_x, pill_top_cap_cy)                # (15.4, +3.175)
    pill_rect_top_right = (pill_right_x, pill_top_cap_cy)              # (22.45, +3.175)

    disc_center = (disc_cx, disc_cy)

    # Fillets at the four channel-mouth corners. Each fillet replaces
    # the sharp wall-meets-rim corner with a tangent arc; the wall
    # shortens to the wall-tangent point, and the rim arc terminates
    # at the rim-tangent point.
    sl_c, sl_wt, sl_rt = channel_corner_fillet(shank_left_wall_x, -1)
    sr_c, sr_wt, sr_rt = channel_corner_fillet(shank_right_wall_x, +1)
    pl_c, pl_wt, pl_rt = channel_corner_fillet(pill_left_x, -1)
    pr_c, pr_wt, pr_rt = channel_corner_fillet(pill_right_x, +1)

    #  1. Long rim arc CCW from top of disc to the shank channel's
    #     left-wall rim-tangent point (around the left/bottom-left).
    ccw_arc(msp, disc_center, disc_radius, top_of_disc, sl_rt)

    #  2. Shank-left fillet (rounds the sharp corner where the rim
    #     meets the shank channel's left wall).
    ccw_arc(msp, sl_c, fillet_radius, sl_rt, sl_wt)

    #  3. Shank channel left wall, going UP from the wall-tangent
    #     point to the shank pocket's left side.
    msp.add_line(sl_wt, shank_left_wall_top)

    #  4. Shank's upper semicircle — the pocket that captures the
    #     shank. CCW from 0° to 180° gives the UPPER half.
    msp.add_arc((shank_cx, shank_cy), shank_radius,
                start_angle=0.0, end_angle=180.0)

    #  5. Shank channel right wall, going DOWN from the shank pocket
    #     to the right-wall tangent point.
    msp.add_line(shank_right_wall_top, sr_wt)

    #  6. Shank-right fillet.
    ccw_arc(msp, sr_c, fillet_radius, sr_wt, sr_rt)

    #  7. Short rim arc CCW from the shank channel's right-wall rim
    #     tangent to the pill channel's left-wall rim tangent (across
    #     the strip of material between the two channels).
    ccw_arc(msp, disc_center, disc_radius, sr_rt, pl_rt)

    #  8. Pill-left fillet.
    ccw_arc(msp, pl_c, fillet_radius, pl_rt, pl_wt)

    #  9. Pill channel left wall + pill rectangle left edge, one
    #     continuous line at X = pill_left_x, going UP from the wall
    #     tangent to the top of the pill rectangle.
    msp.add_line(pl_wt, pill_rect_top_left)

    # 10. Pill's top cap — CCW from 0° to 180° through 90° gives the
    #     upper half (above the cap center).
    msp.add_arc((pill_cx, pill_top_cap_cy), pill_cap_radius,
                start_angle=0.0, end_angle=180.0)

    # 11. Pill rectangle right edge + pill channel right wall, going
    #     DOWN to the right-wall tangent point.
    msp.add_line(pill_rect_top_right, pr_wt)

    # 12. Pill-right fillet.
    ccw_arc(msp, pr_c, fillet_radius, pr_wt, pr_rt)

    # 13. Final rim arc CCW from the pill channel's right-wall rim
    #     tangent back to the top of the disc.
    ccw_arc(msp, disc_center, disc_radius, pr_rt, top_of_disc)

    out_dir = Path(__file__).resolve().parent
    out_name = "touch-flo-under-counter-plate"
    out = out_dir / f"{out_name}.dxf"
    doc.saveas(str(out))
    return out


if __name__ == "__main__":
    out = make_dxf()
    print("Touch-Flo under-counter plate — keyhole (gasket-matched hole positions)")
    print(f"  Outline:        Ø {disc_diameter} mm disc, centered at ({disc_cx}, {disc_cy})")
    print(f"  Shank pocket:   Ø {shank_diameter} mm at ({shank_cx}, {shank_cy})")
    print(f"  Shank channel:  {shank_diameter} mm wide in X, -Y to the rim")
    print(f"  Pill pocket:    {pill_long_y} × {pill_short_x} mm Y-oriented stadium "
          f"at ({pill_cx}, {pill_cy})")
    print(f"  Pill channel:   {pill_short_x} mm wide in X, -Y to the rim")
    print(f"  Units in DXF:   mm (DXF $INSUNITS = 4)")
    print(f"  Material spec:  0.060\" (1.524 mm) 304 stainless, laser-cut, qty 1 per appliance")
    print(f"-> {out.name}")

    # Short names scoped to this part. Units live inside the value so
    # the script controls them — change a unit in source and every
    # dynamic-comment marker follows. NAMES are shared with the
    # touch-flo-shell / mounting-gasket / mounting-plate generators so
    # the same key refers to the same dimension across the stack-up.
    variables = {
        "PLATE_D": f"{disc_diameter:g} mm",
        "SHANK_HOLE_D": f"{shank_diameter:g} mm",
        "FLAVOR_TUBE_X": f"{pill_cx:g} mm",
        "PILL_L": f"{pill_long_y:g} mm",
        "PILL_W": f"{pill_short_x:g} mm",
        "FILLET_R": f"{fillet_radius:g} mm",
    }
    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "SHANK_HOLE_D": 1,
            "FLAVOR_TUBE_X": 1,
            "PILL_L": 1,
            "PILL_W": 1,
            "FILLET_R": 1,
        },
    )
    print(f"-> {Path(__file__).name}")
