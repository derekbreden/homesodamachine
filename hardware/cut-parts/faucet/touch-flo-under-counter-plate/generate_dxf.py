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

# Dimensions in mm, mirrored from the mounting plate / gasket;
# DXF $INSUNITS = 4 (millimeters).

plate_diameter = 54.35
plate_radius = plate_diameter / 2.0
plate_center = (3.175, 0.0)

shank_hole_diameter = 12.6
shank_hole_radius = shank_hole_diameter / 2.0
shank_hole_center = (0.0, 0.0)

# Pill slot is Y-oriented: long axis along Y, short axis along X.
pill_slot_length_y = 13.2
pill_slot_width_x = 6.85
pill_slot_center = (18.925, 0.0)

out_dir = Path(__file__).resolve().parent
out_name = "touch-flo-under-counter-plate"


def add_pill_slot_y_axis(msp, center, length, width):
    """Pill / stadium with its long axis on Y: two vertical sides
    joined by semicircular caps at top and bottom, end-cap radius =
    width / 2.

    Drawn as 2 lines + 2 arcs — same approach as the carbonator
    racetrack end-cap DXFs in this repo. SendCutSend imports the
    closed contour fine even though it's not a single polyline.
    """
    cx, cy = center
    half_length = length / 2.0
    cap_radius = width / 2.0

    top_cap_center = (cx, cy + half_length - cap_radius)
    bottom_cap_center = (cx, cy - half_length + cap_radius)

    for side in (-1, +1):
        side_x = cx + side * cap_radius
        msp.add_line((side_x, top_cap_center[1]), (side_x, bottom_cap_center[1]))

    msp.add_arc(top_cap_center, cap_radius, start_angle=0, end_angle=180)
    msp.add_arc(bottom_cap_center, cap_radius, start_angle=180, end_angle=360)


def make_dxf():
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 4   # 4 = millimeters
    msp = doc.modelspace()

    msp.add_circle(plate_center, plate_radius)
    msp.add_circle(shank_hole_center, shank_hole_radius)
    add_pill_slot_y_axis(msp, pill_slot_center, pill_slot_length_y, pill_slot_width_x)

    out = out_dir / f"{out_name}.dxf"
    doc.saveas(str(out))
    return out


if __name__ == "__main__":
    out = make_dxf()
    print("Touch-Flo under-counter plate")
    print(f"  Outline:        Ø {plate_diameter} mm at {plate_center}")
    print(f"  Shank hole:     Ø {shank_hole_diameter} mm at {shank_hole_center}")
    print(f"  Pill slot:      {pill_slot_length_y} × {pill_slot_width_x} mm "
          f"at {pill_slot_center}, Y-oriented")
    print(f"  Units in DXF:   mm (DXF $INSUNITS = 4)")
    print(f"  Material spec:  0.060\" (1.524 mm) 304 stainless, laser-cut")
    print(f"-> {out.name}")
