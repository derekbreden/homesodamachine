"""
Touch-Flo under-counter plate — sheet-metal plate that sits beneath the
countertop, between the countertop's underside and the under-counter
nut/washer that clamps the entire faucet stack from below.

SPLIT DESIGN — TWO IDENTICAL D-SHAPED HALVES
=============================================
The plate is cut along Y = 0 (the horizontal line passing through both
the shank hole and the pill slot), producing two semicircular D-shaped
halves. The original disc was symmetric across Y = 0 (all three features
— disc center, shank hole, pill slot — sit on the X-axis), so the two
halves are identical pieces; the customer flips one of them 180° around
the split line and mates them at install.

WHY SPLIT
=========
The faucet + umbilical leaves
`/Users/derekbredensteiner/Developer/homesodamachine/hardware/assembly/faucet-and-umbilical.md`
as one permanently-attached sub-assembly: the LLDPE tubes are clamped to
the Westbrass body's compression ports at the bench and never separated
again. A solid one-piece under-counter plate would force the customer to
thread the already-attached tubes through the pill slot from below at
countertop install, which is fiddly. The split eliminates that step:
the customer clips one half against the umbilical from one side, the
other half from the other side, and the two meet along their straight
mating edges around the shank + tube bundle.

INSTALL SEQUENCE
================
1. Drop the faucet+umbilical assembly into the 1-3/8" countertop hole
   from above. The TPU mounting gasket (already on the shank from the
   factory bench) compresses against the countertop top surface.
2. From below: place one half-plate against the underside of the
   countertop, with its mating edge oriented along the centerline of the
   shank+tube bundle. The shank-hole indentation in the half's mating
   edge wraps around the shank from one side; the pill-slot indentation
   wraps around the tube bundle.
3. Place the second half-plate from the opposite side, mating along the
   straight edge with the first half. The two halves now form the full
   disc, with the shank passing through the central shank hole and the
   tubes passing through the pill slot.
4. Slide a washer onto the shank from below, against the two half-plates.
5. Thread the factory shank nut onto the shank and tighten. The nut +
   washer clamp both half-plates flat against the countertop's underside;
   the halves do not need to be interlocked because the nut's clamping
   force provides all retention.

PURPOSE (unchanged from the one-piece version)
===============================================
- Distributes the under-counter nut's clamping force across a wide
  area so the nut doesn't dish or crush the countertop bottom.
- Provides a flat reference surface for the nut to bear against.
- Hole pattern matches the upper mounting plate and TPU gasket —
  shank passes through, two flavor tubes pass through.

STACK-UP (top → bottom, world-Z range in faucet-assembly coords):
- Mounting plate (PETG-CF), Z = [-4, 0]
- TPU gasket (90A black),    Z = [-6, -4]
- Countertop                  (varies — laminate ~32 mm, granite ~38 mm)
- *** Under-counter plate (THIS PART — split, two halves) ***
- Washer + factory shank nut on the threaded Touch-Flo shank

ANTI-ROTATION DURING INSTALL
============================
Same concern as the one-piece version: as the nut is tightened, the
plate could rotate, with the small (~0.25 mm/side) pill-slot clearance
shifting onto the flavor tubes. With the split design there is one
additional failure mode — the two halves could shift relative to each
other in-plane before the nut fully clamps them. Mitigation, same as
before: glue four small silicone bumpers to the top face of each half
(eight total, two per half). Silicone has high friction against
laminate / wood / stone and locks each half against the countertop
underside as soon as the nut starts to tighten.

The clamping force from the nut + washer is the only required retention
between the two halves — no tab-and-slot or hinge interlocking is
needed. Per SendCutSend's published capability:
- Multi-piece DXFs are supported for pure flat parts (non-touching
  contours of the same material/thickness).
- ±0.005" tolerance, kerf compensated, no DXF offset needed.
- 0.060" 304 SS is stocked; same SKU as the previous one-piece version.

DESIGNS RULED OUT
=================
- "Living hinge + snap latch": 304 SS yield strain is ~0.1-0.2 %;
  a single 180° fold at 0.060" puts outer-fiber strain near 2 % —
  fracture risk on the install fold, not just fatigue.
- "C-clip" (single piece with a 5 mm gap that the customer flexes open
  to slip around the umbilical): opening a Ø 54 mm ring by 5 mm requires
  ~9 % diameter strain — two orders of magnitude past 304's elastic
  limit. The clip would plastically deform open and not spring back.
- "Tab-and-slot interlock": feasible at SendCutSend's minima (tab ≥
  0.060", slot ≥ tab + 0.010") but SCS does not guarantee press-fit
  tolerances; the interlock buys nothing the nut isn't already doing.

GEOMETRY (matches the one-piece version exactly except for the split)
=====================================================================
- Ø 54.35 mm outline, centered at (3.175, 0).
- Shank hole Ø 12.6 mm at (0, 0).
- Flavor-tube pill slot 13.2 mm × 6.85 mm at (18.925, 0), Y-oriented.
- Split along Y = 0 — passes through both the shank hole and the pill
  slot, so each half has a half-shank-hole indent and a half-pill-slot
  indent on its mating edge.

DXF LAYOUT
==========
Two identical half-plates emitted side-by-side in the DXF, separated by
a small Y-gap. Both halves are drawn as "upper halves" (split line on
the bottom, disc curving up); the customer flips one of them 180° at
install. SendCutSend's nesting docs explicitly allow this for pure flat
multi-piece parts.

THICKNESS / MATERIAL (specified at order time, not in the DXF)
==============================================================
- Recommended: 0.060" (1.524 mm) 304 stainless. SendCutSend stocks
  this exact gauge in 304; runs cheaper than 316 and is plenty for an
  under-counter location not in food contact.
- Qty 2 per appliance (one full set).

UNITS
=====
Drawing is in mm with $INSUNITS = 4. SendCutSend's uploader confirms
units in the quoting UI; mm is supported alongside inches.

REGENERATE
==========
    tools/cad-venv/bin/python generate_dxf.py

(No CadQuery dependency — uses ezdxf directly.)
"""

from pathlib import Path

import ezdxf

# Dimensions in mm, identical to the prior one-piece version.
# DXF $INSUNITS = 4 (millimeters).

plate_diameter = 54.35
plate_radius = plate_diameter / 2.0
plate_center_natural = (3.175, 0.0)

shank_hole_diameter = 12.6
shank_hole_radius = shank_hole_diameter / 2.0
shank_hole_center_natural = (0.0, 0.0)

# Pill slot is Y-oriented in the natural geometry: long axis along Y.
pill_slot_length_y = 13.2
pill_slot_width_x = 6.85
pill_slot_center_natural = (18.925, 0.0)

# Layout spacing between the two half-plates in the DXF (Y direction).
# SendCutSend requires non-touching contours; a 5 mm gap is plenty and
# keeps the parts visually close so the mating relationship is clear
# at a glance.
inter_half_gap = 5.0


def add_upper_half(msp, y_off):
    """Draw one upper-half plate, with its split line along Y = y_off.

    The half occupies Y in [y_off, y_off + plate_radius * 2]. Disc
    curves upward; shank-hole and pill-slot indentations sit on the
    bottom (split-line) edge.

    Boundary is emitted as separate entities (lines + arcs) that
    together form a single closed contour — same pattern the prior
    one-piece DXF used. SendCutSend's importer reassembles the
    contour from disjoint entities.
    """
    # All natural-frame coordinates are offset by y_off in Y.
    plate_center = (plate_center_natural[0], plate_center_natural[1] + y_off)
    shank_center = (shank_hole_center_natural[0], shank_hole_center_natural[1] + y_off)
    pill_center = (pill_slot_center_natural[0], pill_slot_center_natural[1] + y_off)

    # X positions along the split line (Y = y_off):
    disc_left_x = plate_center_natural[0] - plate_radius
    disc_right_x = plate_center_natural[0] + plate_radius
    shank_left_x = shank_hole_center_natural[0] - shank_hole_radius
    shank_right_x = shank_hole_center_natural[0] + shank_hole_radius
    pill_left_x = pill_slot_center_natural[0] - pill_slot_width_x / 2.0
    pill_right_x = pill_slot_center_natural[0] + pill_slot_width_x / 2.0

    y = y_off

    # 1. Disc outer upper semicircle (CCW from rightmost to leftmost).
    msp.add_arc(plate_center, plate_radius, start_angle=0, end_angle=180)

    # 2. Split-line segments along Y = y_off, broken by the holes.
    msp.add_line((disc_left_x, y), (shank_left_x, y))
    msp.add_line((shank_right_x, y), (pill_left_x, y))
    msp.add_line((pill_right_x, y), (disc_right_x, y))

    # 3. Shank hole — upper semicircle (the lower half is part of the
    #    mating half-plate; here we cut into the half-plate from the
    #    split-line edge).
    msp.add_arc(shank_center, shank_hole_radius, start_angle=0, end_angle=180)

    # 4. Pill slot — upper portion. The pill slot's long axis is along
    #    Y; we render the upper rectangle-plus-top-cap portion.
    half_length = pill_slot_length_y / 2.0
    cap_radius = pill_slot_width_x / 2.0
    top_cap_center = (pill_center[0], pill_center[1] + half_length - cap_radius)

    # Left vertical side of the pill slot, from split line up to the
    # top cap's center height.
    msp.add_line((pill_left_x, y), (pill_left_x, top_cap_center[1]))
    # Top cap arc (semicircular).
    msp.add_arc(top_cap_center, cap_radius, start_angle=0, end_angle=180)
    # Right vertical side of the pill slot, from top cap back down to
    # the split line.
    msp.add_line((pill_right_x, top_cap_center[1]), (pill_right_x, y))


def make_dxf():
    doc = ezdxf.new(dxfversion="R2010")
    doc.header["$INSUNITS"] = 4  # 4 = millimeters
    msp = doc.modelspace()

    # First half at natural position (split line at Y = 0).
    add_upper_half(msp, y_off=0.0)

    # Second half offset above the first by (plate_radius + gap) so the
    # second half's split line sits inter_half_gap mm above the first
    # half's top (Y = plate_radius), keeping the contours non-touching
    # but visually close to show the mating relationship at a glance.
    second_y_offset = plate_radius + inter_half_gap
    add_upper_half(msp, y_off=second_y_offset)

    out_dir = Path(__file__).resolve().parent
    out_name = "touch-flo-under-counter-plate"
    out = out_dir / f"{out_name}.dxf"
    doc.saveas(str(out))
    return out


if __name__ == "__main__":
    out = make_dxf()
    print("Touch-Flo under-counter plate — SPLIT design (two identical halves)")
    print(f"  Outline:        Two D-shaped halves of Ø {plate_diameter} mm disc")
    print(f"  Shank hole:     Ø {shank_hole_diameter} mm at natural origin "
          f"(split between halves at Y = 0)")
    print(f"  Pill slot:      {pill_slot_length_y} × {pill_slot_width_x} mm "
          f"at {pill_slot_center_natural} (split between halves at Y = 0)")
    print(f"  Inter-half gap: {inter_half_gap} mm in DXF (non-touching contours)")
    print(f"  Units in DXF:   mm (DXF $INSUNITS = 4)")
    print(f"  Material spec:  0.060\" (1.524 mm) 304 stainless, laser-cut, "
          f"qty 2 halves per appliance")
    print(f"-> {out.name}")
