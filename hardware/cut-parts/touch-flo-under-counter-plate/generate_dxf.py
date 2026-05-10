"""
Touch-Flo under-counter plate — sheet-metal disc that sits beneath the
countertop, between the countertop's underside and the under-counter
nut/washer that clamps the entire faucet stack from below.

PURPOSE
=======
- Distributes the under-counter nut's clamping force across a wide
  area so the nut doesn't dish or crush the countertop bottom.
- Provides a flat reference surface for the nut to bear against.
- Same hole pattern as the upper mounting plate and TPU gasket —
  shank passes through, two flavor tubes pass through to reach the
  peristaltic pumps below.

STACK-UP (top → bottom, world-Z range in faucet-assembly coords):
- Mounting plate (PETG-CF), Z = [-4, 0]
- TPU gasket (90A black),    Z = [-6, -4]
- Countertop                  (varies — laminate ~32 mm, granite ~38 mm)
- *** Under-counter plate (THIS PART) ***
- Washer + nut on the threaded Touch-Flo shank

FACTORY ANALOG
==============
The Touch-Flo ships with a similar sheet-metal plate (close to 1/16"
zinc-plated steel) plus 4 small stamped dimples on the top face that
bite into the countertop's underside and prevent the plate from
rotating when the under-counter nut is tightened. Our DXF is the
flat-disc portion only — the dimples are out-of-scope for SendCutSend
(their dimple forming has a 12.7 mm minimum diameter, way bigger than
the ~3 mm factory bumps). No quick-turn shop offers the small bumps
as a stock service.

ANTI-ROTATION DURING INSTALL (since we're skipping the dimples)
================================================================
Without the bumps, the plate could rotate as the nut is tightened —
which can shift the pill slot off the flavor tubes (the slot is sized
with only ~0.25 mm of clearance per side around the two tubes). At
install time, EITHER hold the plate from below to prevent rotation,
OR glue 4 small silicone bumpers to the top face before install.
Silicone has high friction against laminate / wood / stone and locks
the plate without modifying the countertop. If after a season this
proves inadequate, options for v2: dome-press 4 dimples by hand using
a punch + steel ball + bench vise, or send the part to a small
sheet-metal shop that does custom embossing.

GEOMETRY (matches the mounting plate / gasket exactly)
======================================================
- Ø 54.35 mm outline, centered at (3.175, 0).
- Shank hole Ø 12.6 mm at (0, 0).
- Flavor-tube pill slot 13.2 mm × 6.85 mm at (18.925, 0), Y-oriented.

THICKNESS / MATERIAL (specified at order time, not in the DXF)
==============================================================
- Recommended: 0.060" (1.524 mm) 304 stainless. SendCutSend stocks
  this exact gauge in both 304 and 316; 304 is plenty for an
  under-counter location not in food contact and runs cheaper.
  Single piece ~$10; qty 5 ~$5 each. Combine with other small SCS
  orders to clear their $39 free-shipping threshold.

UNITS
=====
Drawing is in mm with $INSUNITS = 4. SendCutSend's uploader confirms
units in the quoting UI; mm is supported alongside inches.

REGENERATE
==========
    tools/cad-venv/bin/python generate_dxf.py

(No CadQuery dependency — uses ezdxf directly, matching the pattern
used by the carbonator end-cap DXF generators in this repo.)
"""

from pathlib import Path

import ezdxf


# ── Dimensions (mm) — mirrored from the mounting plate / gasket ──

PLATE_DIAMETER  = 54.35
PLATE_R         = PLATE_DIAMETER / 2.0
PLATE_CENTER_X  = 3.175
PLATE_CENTER_Y  = 0.0

SHANK_HOLE_DIAMETER = 12.6
SHANK_HOLE_R        = SHANK_HOLE_DIAMETER / 2.0
SHANK_HOLE_X        = 0.0
SHANK_HOLE_Y        = 0.0

PILL_SLOT_LENGTH_Y = 13.2     # along Y (long axis)
PILL_SLOT_WIDTH_X  = 6.85     # along X (short axis)
PILL_SLOT_X        = 18.925
PILL_SLOT_Y        = 0.0

OUT_DIR  = Path(__file__).resolve().parent
OUT_NAME = "touch-flo-under-counter-plate"


def add_pill_slot_y_axis(msp, cx, cy, length, width):
    """Y-oriented pill (rounded rectangle / stadium): two vertical
    lines connected by semicircular caps top and bottom.

    `length` = total Y extent. `width` = X extent. Both ends rounded
    with radius = width / 2.

    Drawn as 2 lines + 2 arcs — same approach as the carbonator
    racetrack end-cap DXFs in this repo. SendCutSend imports the
    closed contour fine even though it's not a single polyline.
    """
    half_len = length / 2.0
    half_wid = width / 2.0

    # Centers of the two semicircular caps (on the slot's Y axis).
    top_center = (cx, cy + half_len - half_wid)
    bot_center = (cx, cy - half_len + half_wid)

    # Two straight sides at x = cx ± half_wid, joining the cap centers.
    msp.add_line((cx - half_wid, top_center[1]),
                 (cx - half_wid, bot_center[1]))
    msp.add_line((cx + half_wid, top_center[1]),
                 (cx + half_wid, bot_center[1]))

    # Top cap arc: from (cx + half_wid, top_y) CCW around the top to
    # (cx - half_wid, top_y) — angles 0° to 180°.
    msp.add_arc(top_center, half_wid, start_angle=0, end_angle=180)
    # Bottom cap arc: angles 180° to 360°.
    msp.add_arc(bot_center, half_wid, start_angle=180, end_angle=360)


def make_dxf():
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 4   # 4 = millimeters
    msp = doc.modelspace()

    # Outer disc.
    msp.add_circle((PLATE_CENTER_X, PLATE_CENTER_Y), PLATE_R)
    # Shank hole.
    msp.add_circle((SHANK_HOLE_X, SHANK_HOLE_Y), SHANK_HOLE_R)
    # Flavor-tube pill slot.
    add_pill_slot_y_axis(msp, PILL_SLOT_X, PILL_SLOT_Y,
                          PILL_SLOT_LENGTH_Y, PILL_SLOT_WIDTH_X)

    out = OUT_DIR / f"{OUT_NAME}.dxf"
    doc.saveas(str(out))
    return out


if __name__ == "__main__":
    out = make_dxf()
    print("Touch-Flo under-counter plate")
    print(f"  Outline:        Ø {PLATE_DIAMETER} mm at "
          f"({PLATE_CENTER_X}, {PLATE_CENTER_Y})")
    print(f"  Shank hole:     Ø {SHANK_HOLE_DIAMETER} mm at "
          f"({SHANK_HOLE_X}, {SHANK_HOLE_Y})")
    print(f"  Pill slot:      {PILL_SLOT_LENGTH_Y} × {PILL_SLOT_WIDTH_X} mm "
          f"at ({PILL_SLOT_X}, {PILL_SLOT_Y}), Y-oriented")
    print(f"  Units in DXF:   mm (DXF $INSUNITS = 4)")
    print(f"  Material spec:  0.060\" (1.524 mm) 304 stainless, laser-cut")
    print(f"-> {out.name}")
