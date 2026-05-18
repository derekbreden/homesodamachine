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
(13.2 mm long, 6.85 mm wide). The under-counter plate adds channels
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
  Width 6.85 mm in X (X from 15.5 to 22.35, matching the pill's
  short axis).

Because the shank is at X = 0 and the pill is at X = 18.925, the two
channels are at different X ranges (X = [-6.3, +6.3] vs X = [15.5,
22.35]) and do not overlap. They exit the rim at different points on
the lower arc of the disc.

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

import math
from pathlib import Path

import ezdxf

# Dimensions in mm. DXF $INSUNITS = 4 (millimeters).
# Hole positions match the TPU gasket and the upper mounting plate
# exactly. The disc is also unchanged in size and center.

disc_diameter = 54.35
disc_radius = disc_diameter / 2.0
disc_cx = 3.175
disc_cy = 0.0

shank_cx = 0.0
shank_cy = 0.0
shank_diameter = 12.6
shank_radius = shank_diameter / 2.0

# Pill is Y-oriented (matching the gasket): long axis along Y, short
# axis along X.
pill_cx = 18.925
pill_cy = 0.0
pill_long_y = 13.2
pill_short_x = 6.85
pill_half_long = pill_long_y / 2.0       # 6.6
pill_half_short = pill_short_x / 2.0     # 3.425
pill_cap_radius = pill_half_short        # 3.425
pill_top_cap_cy = pill_cy + (pill_half_long - pill_cap_radius)   # +3.175
pill_bot_cap_cy = pill_cy - (pill_half_long - pill_cap_radius)   # -3.175
pill_left_x = pill_cx - pill_half_short     # 15.5
pill_right_x = pill_cx + pill_half_short    # 22.35


def rim_y_lower(x):
    """Lower Y on the disc rim at the given X (the bottom of the disc)."""
    return disc_cy - math.sqrt(disc_radius ** 2 - (x - disc_cx) ** 2)


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
    shank_left_wall_rim = (shank_left_wall_x,
                           rim_y_lower(shank_left_wall_x))             # (-6.3, ~-25.47)
    shank_right_wall_rim = (shank_right_wall_x,
                            rim_y_lower(shank_right_wall_x))           # (+6.3, ~-27.00)

    # Pill channel — extends in -Y from the pill rectangle's bottom
    # edge (Y = pill_bot_cap_cy = -3.175, replacing the bottom cap) to
    # the rim, width 6.85 mm in X.
    pill_left_wall_top = (pill_left_x, pill_bot_cap_cy)                # (15.5, -3.175)
    pill_right_wall_top = (pill_right_x, pill_bot_cap_cy)              # (22.35, -3.175)
    pill_left_wall_rim = (pill_left_x, rim_y_lower(pill_left_x))       # (15.5, ~-24.22)
    pill_right_wall_rim = (pill_right_x, rim_y_lower(pill_right_x))    # (22.35, ~-19.25)

    pill_rect_top_left = (pill_left_x, pill_top_cap_cy)                # (15.5, +3.175)
    pill_rect_top_right = (pill_right_x, pill_top_cap_cy)              # (22.35, +3.175)

    disc_center = (disc_cx, disc_cy)

    # 1. Long rim arc CCW from top of disc to the shank channel's left
    #    wall meeting point (going around the left side and bottom-left
    #    of the disc).
    ccw_arc(msp, disc_center, disc_radius, top_of_disc, shank_left_wall_rim)

    # 2. Shank channel left wall, going UP from the rim to the shank
    #    pocket's left side.
    msp.add_line(shank_left_wall_rim, shank_left_wall_top)

    # 3. Shank's upper semicircle — the pocket that captures the shank.
    #    CCW from 0° to 180° around the shank center passes through 90°
    #    (the top), giving the UPPER half of the shank circle.
    msp.add_arc((shank_cx, shank_cy), shank_radius,
                start_angle=0.0, end_angle=180.0)

    # 4. Shank channel right wall, going DOWN from the shank pocket's
    #    right side to the rim.
    msp.add_line(shank_right_wall_top, shank_right_wall_rim)

    # 5. Short rim arc CCW from the shank channel's right wall meeting
    #    point to the pill channel's left wall meeting point.
    ccw_arc(msp, disc_center, disc_radius, shank_right_wall_rim, pill_left_wall_rim)

    # 6. Pill channel left wall + pill rectangle left edge, one
    #    continuous line at X = pill_left_x, going UP from the rim to
    #    the top of the pill rectangle.
    msp.add_line(pill_left_wall_rim, pill_rect_top_left)

    # 7. Pill's top cap — the cap that captures the top of the pill.
    #    CCW from 180° to 0° around the top cap center passes through
    #    90° (the top), but we want CCW from 0° to 180° through 90° to
    #    get the upper half (above the cap center).
    msp.add_arc((pill_cx, pill_top_cap_cy), pill_cap_radius,
                start_angle=0.0, end_angle=180.0)

    # 8. Pill rectangle right edge + pill channel right wall, one
    #    continuous line at X = pill_right_x, going DOWN from the top
    #    of the rectangle to the rim.
    msp.add_line(pill_rect_top_right, pill_right_wall_rim)

    # 9. Short rim arc CCW from the pill channel's right wall meeting
    #    point back to the top of the disc.
    ccw_arc(msp, disc_center, disc_radius, pill_right_wall_rim, top_of_disc)

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
