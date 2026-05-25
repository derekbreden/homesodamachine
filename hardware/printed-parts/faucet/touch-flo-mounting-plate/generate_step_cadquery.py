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
No plate-to-shell retention or alignment features. The plate is a
clean disc with only the shank hole + pill slot through it; the
shell's bottom face is similarly clean. Earlier revisions tried
screws+heat-set retention and then printed-boss press-fit
alignment; both were abandoned (see the joinery history in
ASSEMBLY.md). The plate is held to the shell by gravity during
sub-assembly handling and by the shank-nut clamp (body → plate →
TPU gasket → countertop) once the under-counter install finishes.

REGENERATE
==========
    tools/cad-venv/bin/python generate_step_cadquery.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware")),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from _cadq_export import export_step
from docgen import substitute_py_comments


# Plate — [54.35 mm](PLATE_D) OD leaves a 5 mm radial gap to the shell base (Ø 44.35).
# Thickness was 5 mm; trimmed 1 mm to free shank thread engagement for
# the under-counter nut once the 2 mm TPU gasket is in the stack.
plate_radius = 54.35 / 2
plate_thickness = 4.0
# Top face flush with the deck plane (Z=0); plate hangs below.
plate_z_range = (-plate_thickness, 0.0)
# Plate center: midpoint of the assembly footprint with 1/4" flavor
# tubes; matches SHELL_CENTER_X for concentric stack-up.
plate_center = (3.175, 0.0)


# Shank — clearance for the 11 mm threaded shank. [12.6 mm](SHANK_HOLE_D)
# matches the factory mounting plate (~14.5% diametric clearance).
shank_hole_radius = 12.6 / 2
shank_hole_center = (0.0, 0.0)


# Flavor-tube pill slot. The two 1/4" ([6.35 mm](FLAVOR_TUBE_OD)) LLDPE
# tubes are tangent in Y at centers ±flavor_tube_y_offset (separation
# = [6.35 mm](TUBE_CENTER_Y) center-to-center); per-tube circles would
# overlap by ~0.5 mm, so we model the combined opening as a single
# Y-oriented pill (rounded-rectangle).
flavor_tube_od = 6.35
# [6.85 mm](FLAVOR_HOLE_D) per-tube hole diameter = OD + 0.5 mm clearance.
flavor_tube_hole_diameter = flavor_tube_od + 0.5
flavor_tube_y_offset = 3.175
# [18.925 mm](PLATE_FLAVOR_X) +X offset of pill slot center from plate's
# body-bore axis at world origin — matches the shell's flavor_tube_x for
# the cross-coupled stack-up.
pill_slot_center = (18.925, 0.0)
# [13.2 mm](PLATE_PILL_L) pill long axis (Y) = 2 × y_offset + hole_d.
pill_slot_length_y = 2 * flavor_tube_y_offset + flavor_tube_hole_diameter
# [6.85 mm](PLATE_PILL_W) pill short axis (X) = hole_d.
pill_slot_width_x = flavor_tube_hole_diameter


# No plate-to-shell retention or alignment features on this plate.
# Earlier revisions tried screws+heat-set inserts (4677b88), then
# integral-boss press-fit dowels (e5aa8a1), then loose dowels as an
# alignment placeholder (e4568dba). The press-fit bosses snapped at
# the layer-line interface where they joined the plate top face
# (vertically-extruded bosses are weak in shear at their base in FDM
# prints — any sideways force during insertion separates the layers).
# Loose dowels still snapped under any insertion force. Gave up on
# the dowel approach entirely on 2026-05-22. Retention is now
# gravity-only during sub-assembly handling; shank-nut clamping
# (body → plate → TPU gasket → countertop) takes over once the
# under-counter install finishes. See ASSEMBLY.md for the full
# joinery history.


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
    """Build the disc with shank hole, flavor-tube pill slot, and
    top-outer-edge fillet. No bosses, no holes for retention — see
    the comment block above for the joinery-history reasoning.

    The top-outer fillet is applied BEFORE any holes are cut, so the
    outer circle is the only top-face edge at that moment and no
    selector trickery is needed. Through-cuts use the full plate Z
    range."""
    plate = vertical_cylinder(plate_center, plate_radius, plate_z_range)
    plate = plate.faces(">Z").edges().fillet(top_outer_fillet_r)

    plate = plate.cut(vertical_cylinder(shank_hole_center, shank_hole_radius, plate_z_range))
    plate = plate.cut(vertical_y_slot(pill_slot_center, pill_slot_length_y, pill_slot_width_x, plate_z_range))

    return plate


def main():
    plate = build_mounting_plate()

    out = _here / "touch-flo-mounting-plate.step"
    export_step(plate, str(out))

    print("Touch-Flo mounting plate")
    print(f"  Disc:           Ø{2 * plate_radius} mm × {plate_thickness} mm thick")
    print(f"  Center:         {plate_center}")
    print(f"  Z range:        {plate_z_range[0]} → {plate_z_range[1]}")
    print(f"  Shank hole:     Ø{2 * shank_hole_radius} mm at {shank_hole_center}")
    print(f"  Flavor pill:    {pill_slot_length_y} × {pill_slot_width_x} mm "
          f"at {pill_slot_center}, Y-oriented")
    print(f"  Top outer R:    {top_outer_fillet_r} mm fillet")
    print(f"-> {out.name}")

    variables = {
        "PLATE_D": f"{2 * plate_radius:g} mm",
        "SHANK_HOLE_D": f"{2 * shank_hole_radius:g} mm",
        "FLAVOR_TUBE_OD": f"{flavor_tube_od:g} mm",
        "TUBE_CENTER_Y": f"{2 * flavor_tube_y_offset:g} mm",
        "FLAVOR_HOLE_D": f"{flavor_tube_hole_diameter:g} mm",
        "PLATE_FLAVOR_X": f"{pill_slot_center[0]:g} mm",
        "PLATE_PILL_L": f"{pill_slot_length_y:g} mm",
        "PLATE_PILL_W": f"{pill_slot_width_x:g} mm",
    }

    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "SHANK_HOLE_D": 1,
            "FLAVOR_TUBE_OD": 1,
            "TUBE_CENTER_Y": 1,
            "FLAVOR_HOLE_D": 1,
            "PLATE_FLAVOR_X": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
