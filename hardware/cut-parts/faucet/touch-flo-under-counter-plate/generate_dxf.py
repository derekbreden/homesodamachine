"""
Touch-Flo under-counter plate — sheet-metal plate that sits beneath the
countertop, between the countertop's underside and the under-counter
nut/washer that clamps the entire faucet stack from below.

KEYHOLE DESIGN — ONE PIECE WITH TWO OPEN-EDGE SLOTS
====================================================
The plate is a single rigid disc with two narrow open-edge slots cut
into it. Each slot is a terminal pocket (sized to receive its cylinder
snugly) plus a straight channel of the same cross-section extending to
the rim. The customer slides the plate laterally onto the dangling
umbilical from below the countertop, both cylinders entering through
their channel mouths at the rim and seating in their terminal pockets.
Single piece, single slide motion, no two-half alignment, no flex
required.

WHY KEYHOLE OVER SPLIT-HALVES
=============================
The faucet + umbilical leaves
`/Users/derekbredensteiner/Developer/homesodamachine/hardware/assembly/faucet-and-umbilical.md`
as one permanently-attached sub-assembly — the LLDPE tubes are clamped
to the Westbrass body's compression ports at the bench and never
separated again. A solid one-piece disc would force the customer to
thread already-attached tubes through the pill slot from below. The
split-halves design (one earlier iteration) avoids that but requires
the customer to hold two pieces in alignment against the countertop
underside while also threading the nut — three hands or contortion.
The keyhole design avoids both: the customer slides one piece on, the
cylinders sit in the channels (so the plate cannot drift back out of
alignment under gravity), the customer threads the nut one-handed.

The cylinders in their narrow channels also provide built-in
anti-rotation: any attempt at rotation under nut clamping load presses
the cylinders against the channel walls. No silicone bumpers needed.

INTERNAL COORDINATE LAYOUT
==========================
For the two horizontal channels to exit the rim at different points
(and not merge), the shank hole and pill slot must be at different Y
positions in plate coordinates. The body's geometry fixes the
*magnitude* of the shank-to-pill distance (18.925 mm) and the
perpendicular orientation of the pill's long axis to that distance,
but lets the plate's coordinate frame be chosen freely. The mounting
plate and gasket above the countertop describe these features along
their own X axis (shank at (0, 0), pill at (18.925, 0)). The
under-counter plate's DXF describes them along its own Y axis (shank
at (0, 0), pill at (0, 18.925)) — the same physical features in a
90°-rotated coordinate system. The customer doesn't see coordinate
frames; they just orient the plate to fit the cylinders, same as they
would with any plate. The choice of axis is purely a DXF-description
convenience that makes the two channels naturally extend in +X to two
different Y points on the rim.

GEOMETRY
========
- Disc Ø 54.35 mm, centered at (0, 0) — at the shank. The shank sits
  at the disc's geometric center; the pill at (0, 18.925) sits near
  the upper rim. Shank rim margin ~21 mm; pill rim margin ~4.6 mm at
  its closest corner to the rim (the top-left corner of the pill
  rectangle at (-3.175, 22.35)) — tight but well within 0.060" 304
  SS structural capacity under nut clamping load.
- Shank terminal: Ø 12.6 mm semicircular pocket on the mating side of
  the channel, at (0, 0).
- Shank channel: 12.6 mm tall (Y from -6.3 to +6.3), extending from
  the shank pocket rightward to the right rim. Channel mouth on the
  rim spans Y = -6.3 (rim X = 22.14) to Y = +6.3 (rim X = 26.99).
- Pill terminal: stadium 13.2 mm long × 6.85 mm wide, long axis along
  X (the channel direction), centered at (0, 18.925). The pill's
  *right* cap is replaced by the channel; the *left* cap remains as
  the boundary at the pill's leftmost extent.
- Pill channel: 6.85 mm tall (Y from 15.5 to 22.35), extending from
  the pill's right rectangle edge (X = +3.175) rightward to the
  right rim. Channel mouth on the rim spans Y = 15.5 (rim X = 26.49)
  to Y = 22.35 (rim X = 23.92).

INSTALL SEQUENCE
================
1. Drop the faucet+umbilical assembly into the 1-3/8" countertop hole
   from above. The TPU mounting gasket (already on the shank from the
   factory bench) compresses against the countertop top surface.
2. From below: hold the plate horizontally against the countertop
   underside, oriented with the channel mouths facing the umbilical.
3. Slide the plate laterally past the cylinders. Both cylinders enter
   through their channel mouths at the rim and travel along the
   channels into their terminal pockets — the shank into its
   Ø 12.6 pocket at (0, 0), the two tubes into the pill at (0, 18.925).
4. Slide a washer onto the shank from below, against the plate.
5. Thread the factory shank nut onto the shank and tighten. The
   nut + washer clamp the plate flat against the countertop underside.

PURPOSE (unchanged from prior iterations)
==========================================
- Distributes the under-counter nut's clamping force across a wide
  area so the nut doesn't dish or crush the countertop bottom.
- Provides a flat reference surface for the nut to bear against.
- Hole pattern matches the upper mounting plate and TPU gasket
  (rotated 90° in the description, but the same physical features) —
  shank passes through, two flavor tubes pass through.

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
- Order quantity: 1 per appliance (this is a single-piece design;
  unlike the split-halves it superseded, no qty 2 needed).

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

# Disc — centered on the shank at (0, 0). The shank is at the disc's
# geometric center; the pill is offset upward to (0, 18.925).
disc_diameter = 54.35
disc_radius = disc_diameter / 2.0
disc_cx = 0.0
disc_cy = 0.0

# Shank terminal (at the disc-center side of the layout).
shank_cx = 0.0
shank_cy = 0.0
shank_diameter = 12.6
shank_radius = shank_diameter / 2.0

# Pill terminal — long axis along X (the channel direction).
pill_cx = 0.0
pill_cy = 18.925
pill_long_x = 13.2       # along channel direction
pill_short_y = 6.85      # perpendicular to channel
pill_half_long = pill_long_x / 2.0       # 6.6
pill_half_short = pill_short_y / 2.0     # 3.425
pill_cap_radius = pill_half_short        # 3.425 — cap is a semicircle of the short width
pill_left_cap_x = pill_cx - (pill_half_long - pill_cap_radius)    # -3.175
pill_right_cap_x = pill_cx + (pill_half_long - pill_cap_radius)   # +3.175
pill_top_y = pill_cy + pill_half_short    # 22.35
pill_bot_y = pill_cy - pill_half_short    # 15.5


def rim_x_at(y):
    """Positive X on the disc rim at the given Y."""
    return math.sqrt(disc_radius ** 2 - (y - disc_cy) ** 2)


def angle_at(point):
    """Polar angle in degrees around the disc center for a point on the rim."""
    return math.degrees(math.atan2(point[1] - disc_cy, point[0] - disc_cx))


def ccw_arc(msp, center, radius, start_pt, end_pt):
    """Emit an arc on the disc rim going CCW from start_pt to end_pt."""
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
    top_of_disc = (disc_cx, disc_cy + disc_radius)                  # (0, 36.6375)

    shank_bot_mouth = (rim_x_at(shank_cy - shank_radius),
                       shank_cy - shank_radius)                     # (~22.14, -6.3)
    shank_bot_pocket = (shank_cx, shank_cy - shank_radius)          # (0, -6.3)
    shank_top_pocket = (shank_cx, shank_cy + shank_radius)          # (0, +6.3)
    shank_top_mouth = (rim_x_at(shank_cy + shank_radius),
                       shank_cy + shank_radius)                     # (~26.99, +6.3)

    pill_bot_mouth = (rim_x_at(pill_bot_y), pill_bot_y)             # (~26.49, 15.5)
    pill_rect_bot_left = (pill_left_cap_x, pill_bot_y)              # (-3.175, 15.5)
    pill_rect_top_left = (pill_left_cap_x, pill_top_y)              # (-3.175, 22.35)
    pill_top_mouth = (rim_x_at(pill_top_y), pill_top_y)             # (~23.92, 22.35)

    disc_center = (disc_cx, disc_cy)

    # 1. Long rim arc CCW from top of disc to the shank channel's bottom mouth.
    #    Spans the entire left side and bottom of the disc.
    ccw_arc(msp, disc_center, disc_radius, top_of_disc, shank_bot_mouth)

    # 2. Shank channel bottom wall.
    msp.add_line(shank_bot_mouth, shank_bot_pocket)

    # 3. Shank's left semicircle — the pocket that captures the shank.
    #    CCW from 90° to 270° around the shank center passes through 180°
    #    (the leftmost point), giving the LEFT half of the shank circle.
    msp.add_arc((shank_cx, shank_cy), shank_radius, start_angle=90.0, end_angle=270.0)

    # 4. Shank channel top wall.
    msp.add_line(shank_top_pocket, shank_top_mouth)

    # 5. Short rim arc CCW from the shank channel top mouth to the pill
    #    channel bottom mouth.
    ccw_arc(msp, disc_center, disc_radius, shank_top_mouth, pill_bot_mouth)

    # 6. Pill channel bottom wall + pill rectangle bottom edge, one
    #    continuous line at Y = pill_bot_y.
    msp.add_line(pill_bot_mouth, pill_rect_bot_left)

    # 7. Pill's left cap — the pocket that captures the leftmost tube.
    #    CCW from 90° to 270° around the left-cap center gives the LEFT
    #    half of the cap (the pill's leftmost boundary).
    msp.add_arc((pill_left_cap_x, pill_cy), pill_cap_radius,
                start_angle=90.0, end_angle=270.0)

    # 8. Pill rectangle top edge + pill channel top wall, one continuous
    #    line at Y = pill_top_y.
    msp.add_line(pill_rect_top_left, pill_top_mouth)

    # 9. Short rim arc CCW from the pill channel top mouth back to the
    #    top of the disc.
    ccw_arc(msp, disc_center, disc_radius, pill_top_mouth, top_of_disc)

    out_dir = Path(__file__).resolve().parent
    out_name = "touch-flo-under-counter-plate"
    out = out_dir / f"{out_name}.dxf"
    doc.saveas(str(out))
    return out


if __name__ == "__main__":
    out = make_dxf()
    print("Touch-Flo under-counter plate — keyhole design (one piece, two open-edge slots)")
    print(f"  Outline:        Ø {disc_diameter} mm disc, centered at ({disc_cx}, {disc_cy})")
    print(f"  Shank pocket:   Ø {shank_diameter} mm at ({shank_cx}, {shank_cy})")
    print(f"  Shank channel:  {shank_diameter} mm tall, +X to the rim")
    print(f"  Pill pocket:    {pill_long_x} × {pill_short_y} mm stadium at ({pill_cx}, {pill_cy})")
    print(f"  Pill channel:   {pill_short_y} mm tall, +X to the rim")
    print(f"  Units in DXF:   mm (DXF $INSUNITS = 4)")
    print(f"  Material spec:  0.060\" (1.524 mm) 304 stainless, laser-cut, qty 1 per appliance")
    print(f"-> {out.name}")
