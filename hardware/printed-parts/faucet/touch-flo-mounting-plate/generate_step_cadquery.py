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
3. Press-fit dowel pin bosses (×2, mirrored across Y=0) — Ø 4.0 mm
   solid cylindrical bosses extruded UP 5 mm from the plate's TOP
   face, with a 0.5 mm × 45° chamfer at the tip. Located at
   θ = ±45° about the body center, r = 20 from body center (world
   (14.142, ±14.142)) — same XY as the matching Ø 4.05 × 6 mm
   press-fit pockets in the shell's bottom face. The 0.05 mm
   diametric CAD clearance is overrun by FDM tolerances (boss prints
   slightly oversize, pocket prints slightly undersize) to produce
   a real press fit when assembled. No screws, no heat-set inserts
   on this joint — the plate slides up onto the shell, the bosses
   self-align into the pockets, and friction holds the sub-assembly
   together. The harvested faucet body's shank nut (below the
   under-counter plate) carries all the structural load; the
   press-fit dowels only need to keep the plate stuck to the shell
   during sub-assembly handling.

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


# Press-fit dowel bosses — two solid cylindrical pins extruded UP
# from the plate's top face into matching pockets on the shell's
# bottom face. Mirrored across Y=0; placed in the shell's "rear
# shoulder" wall material between the body bore and the shell outer
# cylinder, well clear of the pill slot.
#
# Replaces the earlier screw + heat-set insert retention (last seen
# in commit 4677b88, M3 × 6 mm ULH SHCS McMaster 91223A412 +
# ruthex M3 short Amazon B09ZHSGHXD). The screws were expensive
# ($4-6 each, McMaster-only), fiddly (Ø 5.5 × 1.0 head, 2 mm hex
# strips easily under the torque needed to seat in PET-CF), and
# always retention-only — the structural clamping came from the
# shank nut below the under-counter plate. Press-fit dowels do the
# same retention with zero fasteners and zero hardware cost.
#
# Boss / pocket spec — boss Ø 4.0 × 5 mm tall + 0.5 mm × 45° tip
# chamfer; matching shell pocket Ø 4.05 × 6 mm deep. 0.05 mm
# diametric CAD clearance is overrun by FDM tolerances (positive
# features print oversize, negative features print undersize) to
# create a real press fit when assembled. 1 mm of empty pocket
# above the boss tip accommodates FDM bottom-layer flatness
# variance in the shell pocket.

dowel_pin_radius = 4.0 / 2       # Ø 4.0 mm bosses (matches Ø 4.05 shell pocket nominal — FDM tolerance closes the gap)
dowel_pin_height = 5.0           # 5 mm tall above plate top face
dowel_pin_tip_chamfer = 0.5      # 0.5 mm × 45° chamfer at the boss tip for self-alignment

# Dowel positions: θ = ±45° about the body center (0, 0), r = 20 mm —
# the shell's "rear shoulder" wall material. At this point all four
# wall margins to other shell features hold ≥ 2 mm:
#   - to body bore (Ø 31.5 cyl @ origin):       2.25 mm
#   - to shell outer (Ø 44.35 cyl @ +X 3.175):  2.28 mm
#   - to pill slot (Y top edge at +6.6):        5.54 mm
#   - between the two bosses (Y separation):    24.28 mm
dowel_r_from_body = 20.0
dowel_theta_deg = 45.0
dowel_x = dowel_r_from_body * math.cos(math.radians(dowel_theta_deg))
dowel_y_offset = dowel_r_from_body * math.sin(math.radians(dowel_theta_deg))
dowel_centers = [(dowel_x, +dowel_y_offset), (dowel_x, -dowel_y_offset)]


# Fillet on the top outer edge — softens the visible ring around the
# body once the plate is installed. 2 mm on a 4 mm plate (50% of
# thickness — half-bullnose, half-flat side) reads as an intentional
# finished edge without eating the flat landing area the body and
# shell sit on.
top_outer_fillet_r = 2.0


def vertical_cylinder(center, radius, z_range):
    """Z-axis cylinder: 2D center, radius, and Z extent."""
    z_min, z_max = z_range
    return (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(*center)
        .circle(radius)
        .extrude(z_max - z_min)
    )


def vertical_y_slot(center, length_y, width_x, z_range):
    """Z-axis pill (rounded-rectangle) prism with long axis along Y."""
    z_min, z_max = z_range
    return (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .moveTo(*center)
        .slot2D(length_y, width_x, angle=90)
        .extrude(z_max - z_min)
    )


def build_mounting_plate() -> cq.Workplane:
    """Build the disc with shank hole, flavor-tube pill slot, dowel-pin
    bosses, and top-outer-edge fillet.

    The top-outer fillet is applied BEFORE any holes are cut, so the
    outer circle is the only top-face edge at that moment and no
    selector trickery is needed. Through-cuts use the full plate Z
    range; the dowel bosses are extruded UP from the plate top, with
    a 45° chamfer on the top edge for self-alignment into the
    matching shell pocket."""
    plate = vertical_cylinder(plate_center, plate_radius, plate_z_range)
    plate = plate.faces(">Z").edges().fillet(top_outer_fillet_r)

    plate = plate.cut(vertical_cylinder(shank_hole_center, shank_hole_radius, plate_z_range))
    plate = plate.cut(vertical_y_slot(pill_slot_center, pill_slot_length_y, pill_slot_width_x, plate_z_range))

    boss_z_range = (plate_z_range[1], plate_z_range[1] + dowel_pin_height)
    for dowel_center in dowel_centers:
        boss = vertical_cylinder(dowel_center, dowel_pin_radius, boss_z_range)
        # Chamfer the top edge of this boss (lead-in for self-alignment
        # into the shell pocket). Select the boss's top edge by
        # picking the topmost edge — at this Z it's the only one.
        boss = boss.faces(">Z").edges().chamfer(dowel_pin_tip_chamfer)
        plate = plate.union(boss)

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
    print(f"  Dowel bosses:   Ø{2 * dowel_pin_radius} × {dowel_pin_height} mm tall "
          f"(top {dowel_pin_tip_chamfer} mm × 45° chamfer) at "
          f"({dowel_x:.3f}, ±{dowel_y_offset:.3f}) "
          f"[θ=±{dowel_theta_deg}°, r={dowel_r_from_body} from body]")
    print(f"  Top outer R:    {top_outer_fillet_r} mm fillet")
    print(f"-> {out.name}")
