"""
Touch-Flo mounting plate — printed disc that supports the harvested
Touch-Flo faucet body, the two flavor tubes that pass alongside it,
and (eventually) the shell that wraps around the assembly.

GEOMETRY
========
- Ø 54.35 mm, 4 mm thick disc — sized so the plate's edge sits 5 mm
  out from the shell base's outer cylinder (Ø 44.35 = SHELL_OUTER_R
  × 2). 5 mm matches the standard wall / margin elsewhere in the
  shell. Factory plate was Ø 44.5; this is bigger.
- Plate spans Z = [-4, 0] in world coords; top face flush with the
  deck plane (= body bottom in the faucet-assembly).
- Plate center at world (3.175, 0) — the midpoint of the assembly's
  lateral footprint at Z = 0 with 1/4" flavor tubes:
    -X edge: body cylindrical base at X = -15.75
    +X edge: outer wall of the +X flavor tube at X = +22.10
    midpoint: +3.175
  This puts the body at world (0, 0) shifted -3.175 mm in X relative
  to the plate center, by design. Plate center matches the shell's
  SHELL_CENTER_X for concentric stack-up.

HOLES
=====
1. Shank hole — Ø 12.6 mm at world (0, 0). Matches the factory
   mounting plate's clearance for the 11 mm threaded shank
   (~14.5% diametric clearance).
2. Flavor-tube pill slot — at world (18.925, 0), oriented along Y.
   Per-tube Ø would be 6.85 mm (= 6.35 OD + 0.5 mm clearance applied
   to the 1/4" flavor tubes), but the two tubes are only 6.35 mm
   apart center-to-center, so the per-tube circles overlap by
   ~0.5 mm. We model the combined opening as a single pill
   (rounded-rectangle) slot for cleaner printability:
     - Length (Y, end-to-end): 13.2 mm
     - Width (X):              6.85 mm
3. Screw clearance holes (×2, mirrored across Y=0) — Ø 3.9 mm
   through, with Ø 5.7 × 1.25 mm counterbore on the BOTTOM face for
   the screw head. Located at θ = ±45° about the body center, r = 20
   from body center (world (14.142, ±14.142)) — the shell's "rear
   shoulder" wall material. Hosts M3 × 8 mm 316 SS ultra-low-profile
   socket cap screws (McMaster 91223A413) that thread into M3 brass
   heat-set inserts (ruthex short, Amazon B09ZHSGHXD) pressed into
   the shell above. Head Ø 5.5 × 1.0 tall sits 0.25 mm below the
   plate's bottom face; Ø 3.8 unthreaded shoulder under the head
   passes through the Ø 3.9 clearance with 0.05 mm/side fit.

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(
    0,
    str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware")),
)
from _cadq_export import export_step


# Plate — Ø 54.35 leaves a 5 mm radial gap to the shell base (Ø 44.35).
# Thickness was 5 mm; trimmed 1 mm to free shank thread engagement for
# the under-counter nut once the 2 mm TPU gasket is in the stack.
plate_radius = 54.35 / 2
plate_thickness = 4.0
# Top face flush with the deck plane (Z=0); plate hangs below.
plate_z_range = (-plate_thickness, 0.0)
# Plate center: midpoint of the assembly footprint with 1/4" flavor
# tubes; matches SHELL_CENTER_X for concentric stack-up.
plate_center = (3.175, 0.0)


# Shank — clearance for the 11 mm threaded shank. 12.6 mm matches the
# factory mounting plate (~14.5% diametric clearance).
shank_hole_radius = 12.6 / 2
shank_hole_center = (0.0, 0.0)


# Flavor-tube pill slot. The two 1/4" (6.35 mm) LLDPE tubes are tangent
# in Y at centers ±flavor_tube_y_offset; per-tube circles would overlap
# by ~0.5 mm, so we model the combined opening as a single Y-oriented
# pill (rounded-rectangle).
flavor_tube_od = 6.35
flavor_tube_hole_diameter = flavor_tube_od + 0.5
flavor_tube_y_offset = 3.175
pill_slot_center = (18.925, 0.0)
pill_slot_length_y = 2 * flavor_tube_y_offset + flavor_tube_hole_diameter
pill_slot_width_x = flavor_tube_hole_diameter


# Two M3 socket-cap screws come up from below the plate, pass through
# clearance + counterbore, and thread into M3 brass heat-set inserts
# pressed into the touch-flo-shell above. Mirrored across Y=0; placed
# in the shell's "rear shoulder" wall material between the body bore
# and the shell outer cylinder, well clear of the pill slot.
#
# Screw — McMaster 91223A413: 316 SS ultra-low-profile socket head,
#   M3 × 0.5 × 8 mm, head Ø 5.5 × 1.0 mm tall, 2 mm hex socket,
#   Ø 3.8 unthreaded shoulder under the head.
# Insert — ruthex M3 short (Amazon B09ZHSGHXD): Ø 4.6 knurl OD /
#   Ø 3.9 body / 4 mm length, recommended install hole Ø 4.0.

# Clearance for the Ø 3.8 shoulder under the head (0.05 mm/side).
# Tight by intent — close fit aids screw alignment. If FDM print
# comes in undersize for this hole, drill out with a #29 (3.9 mm)
# bit before trying to install screws.
screw_clearance_radius = 3.9 / 2

# Clearance for the Ø 5.5 head (0.1 mm/side). 1.25 mm deep =
# 1.0 mm head height + 0.25 mm clearance, so the head sits 0.25 mm
# below the bottom face. Plate material remaining above the
# counterbore (Z = -2.75 to 0): 2.75 mm.
screw_counterbore_radius = 5.7 / 2
screw_counterbore_depth = 1.25

# Screw positions: θ = ±45° about the body center (0, 0), r = 20 mm —
# the shell's "rear shoulder" wall material. At this point all four
# wall margins hold ≥ 2 mm:
#   - to body bore (Ø 31.5 cyl @ origin):       2.25 mm
#   - to shell outer (Ø 44.35 cyl @ +X 3.175):  2.28 mm
#   - to pill slot (Y top edge at +6.6):        5.54 mm
#   - between the two screws (Y separation):    24.28 mm
screw_r_from_body = 20.0
screw_theta_deg = 45.0
screw_x = screw_r_from_body * math.cos(math.radians(screw_theta_deg))
screw_y_offset = screw_r_from_body * math.sin(math.radians(screw_theta_deg))
screw_centers = [(screw_x, +screw_y_offset), (screw_x, -screw_y_offset)]


# Fillet on the top outer edge — softens the visible ring around the
# body once the plate is installed. 2 mm on a 4 mm plate (50% of
# thickness — half-bullnose, half-flat side) reads as an intentional
# finished edge without eating the flat landing area the body and
# shell sit on.
top_outer_fillet_r = 2.0


def build_mounting_plate() -> cq.Workplane:
    """Build the disc with shank hole, flavor-tube pill slot, and
    top-outer-edge fillet.

    Order of operations:
      1. Solid disc.
      2. Fillet the top outer edge — applied BEFORE the holes so the
         outer circle is the only top-face edge at that moment, no
         selector trickery needed.
      3. Cut the shank and pill holes (these stay sharp-edged).

    All cuts pass through the full 4 mm thickness.
    """
    z_min, z_max = plate_z_range
    plate = (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(*plate_center)
        .circle(plate_radius)
        .extrude(z_max - z_min)
    )

    # Fillet the single top edge (the outer circle) before any holes
    # introduce additional top-face edges.
    plate = plate.faces(">Z").edges().fillet(top_outer_fillet_r)

    shank_hole = (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(*shank_hole_center)
        .circle(shank_hole_radius)
        .extrude(z_max - z_min)
    )
    plate = plate.cut(shank_hole)

    pill_slot = (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(*pill_slot_center)
        .slot2D(pill_slot_length_y, pill_slot_width_x, angle=90)
        .extrude(z_max - z_min)
    )
    plate = plate.cut(pill_slot)

    # Two screw clearance holes (through) + counterbores (bottom face),
    # mirrored across Y=0.
    for screw_center in screw_centers:
        clear = (
            cq.Workplane("XY")
            .workplane(offset=z_min)
            .moveTo(*screw_center)
            .circle(screw_clearance_radius)
            .extrude(z_max - z_min)
        )
        plate = plate.cut(clear)

        cbore = (
            cq.Workplane("XY")
            .workplane(offset=z_min)
            .moveTo(*screw_center)
            .circle(screw_counterbore_radius)
            .extrude(screw_counterbore_depth)
        )
        plate = plate.cut(cbore)

    return plate


if __name__ == "__main__":
    plate = build_mounting_plate()

    out = Path(__file__).resolve().parent / "touch-flo-mounting-plate.step"
    export_step(plate, str(out))

    print("Touch-Flo mounting plate")
    print(f"  Disc:           Ø{2 * plate_radius} mm × {plate_thickness} mm thick")
    print(f"  Center:         {plate_center}")
    print(f"  Z range:        {plate_z_range[0]} → {plate_z_range[1]}")
    print(f"  Shank hole:     Ø{2 * shank_hole_radius} mm at {shank_hole_center}")
    print(f"  Flavor pill:    {pill_slot_length_y} × {pill_slot_width_x} mm "
          f"at {pill_slot_center}, Y-oriented")
    print(f"  Screw clear:    Ø{2 * screw_clearance_radius} mm at "
          f"({screw_x:.3f}, ±{screw_y_offset:.3f}) "
          f"[θ=±{screw_theta_deg}°, r={screw_r_from_body} from body]")
    print(f"  Screw cbore:    Ø{2 * screw_counterbore_radius} × "
          f"{screw_counterbore_depth} mm deep, bottom face")
    print(f"  Top outer R:    {top_outer_fillet_r} mm fillet")
    print(f"-> {out.name}")
