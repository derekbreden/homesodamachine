"""Touch-Flo mounting plate — printed PETG disc that supports the
harvested Touch-Flo faucet body, the two flavor tubes that pass
alongside it, and (eventually) the shell that wraps around the
assembly. See README.md for geometry, hole positions, joinery
history, and the rationale for the current dimensions."""

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
sys.path.insert(0, str(_here.parent))  # for _touch_flo_interface
from _cadq_export import export_step
from _touch_flo_interface import (
    flavor_tube_od,
    flavor_tube_hole_clearance as flavor_hole_clearance,
    flavor_tube_hole_dia as flavor_tube_hole_diameter,
    flavor_tube_x,
    flavor_tube_y_offset,
    pill_length_y as pill_slot_length_y,
    pill_width_x as pill_slot_width_x,
    shank_hole_diameter,
)
from docgen import substitute_md, substitute_py_comments


# Plate — [54.35 mm](PLATE_D) OD leaves a [5 mm](PLATE_TO_SHELL_GAP)
# radial gap to the shell base (Ø [44.35 mm](SHELL_OUTER_D)).
plate_radius = 54.35 / 2
# Plate thickness — was [5 mm](PREV_PLATE_T); trimmed [1 mm](PLATE_TRIM)
# to [4 mm](PLATE_T) to free shank thread engagement for the
# under-counter nut once the [2 mm](GASKET_T) TPU gasket is in the stack.
plate_thickness = 4.0
previous_plate_thickness = 5.0
plate_trim = previous_plate_thickness - plate_thickness
gasket_thickness = 2.0
# Top face flush with the deck plane (Z=0); plate hangs below.
plate_z_range = (-plate_thickness, 0.0)
# Plate center: midpoint of the assembly footprint with 1/4" flavor
# tubes; matches SHELL_CENTER_X for concentric stack-up.
# [3.175 mm](PLATE_X) X offset, Z = 0.
plate_center = (3.175, 0.0)


# Shell base outer diameter — the printed touch-flo-shell sits on top
# of this plate, concentric with it. The plate is [5 mm](PLATE_TO_SHELL_GAP)
# wider in radius so its edge is visible past the shell base.
plate_to_shell_gap = 5.0
shell_outer_radius = plate_radius - plate_to_shell_gap
shell_outer_diameter = 2 * shell_outer_radius


# Shank — clearance for the [11 mm](SHANK_OD) threaded shank.
# [12.6 mm](SHANK_HOLE_D) matches the factory mounting plate
# (~[14.5%](SHANK_CLEARANCE_PCT) diametric clearance).
# shank_hole_diameter imported from _touch_flo_interface (single source
# of truth — same Ø12.6 used by the gasket and under-counter plate).
shank_diameter_nominal = 11.0
shank_hole_radius = shank_hole_diameter / 2
shank_hole_center = (0.0, 0.0)
shank_clearance_pct = (shank_hole_diameter - shank_diameter_nominal) / shank_diameter_nominal


# Flavor-tube pill slot. The two 1/4" ([6.35 mm](FLAVOR_TUBE_OD)) LLDPE
# tubes are tangent in Y at centers ±flavor_tube_y_offset (separation
# = [6.35 mm](TUBE_CENTER_Y) center-to-center); per-tube circles would
# overlap by ~[0.7 mm](TUBE_OVERLAP), so we model the combined opening
# as a single Y-oriented pill (rounded-rectangle).
#
# flavor_tube_od / flavor_hole_clearance / flavor_tube_hole_diameter /
# flavor_tube_y_offset / pill_slot_length_y / pill_slot_width_x all
# imported from _touch_flo_interface (single source of truth for the
# stack-up — was 0.5 mm clearance here until 2026-05-25; promoted to the
# shell's print-validated 0.7 mm).
# [7.05 mm](FLAVOR_HOLE_D) per-tube hole diameter = OD + [0.7 mm](FLAVOR_HOLE_CLEARANCE) clearance.
tube_overlap = flavor_tube_hole_diameter - 2 * flavor_tube_y_offset
# [18.93 mm](PLATE_FLAVOR_X) +X offset of pill slot center from plate's
# body-bore axis at world origin — matches the shell's flavor_tube_x for
# the cross-coupled stack-up.
pill_slot_center = (flavor_tube_x, 0.0)
# [13.4 mm](PLATE_PILL_L) pill long axis (Y) = 2 × y_offset + hole_d.
# [7.05 mm](PLATE_PILL_W) pill short axis (X) = hole_d.


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
# body once the plate is installed. [2 mm](TOP_FILLET_R) on a
# [4 mm](PLATE_T) plate ([50%](FILLET_RATIO) of thickness —
# half-bullnose, half-flat side) reads as an intentional finished edge
# without eating the flat landing area the body and shell sit on.
top_outer_fillet_r = 2.0
fillet_ratio = top_outer_fillet_r / plate_thickness


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
        # Disc
        "PLATE_D": f"{2 * plate_radius:.4g} mm",
        "PLATE_T": f"{plate_thickness:.4g} mm",
        "PLATE_X": f"{plate_center[0]:.4g} mm",
        "PLATE_Z_BOTTOM": f"{plate_z_range[0]:.4g}",
        "PREV_PLATE_T": f"{previous_plate_thickness:.4g} mm",
        "PLATE_TRIM": f"{plate_trim:.4g} mm",
        # Shell + cross-coupling
        "PLATE_TO_SHELL_GAP": f"{plate_to_shell_gap:.4g} mm",
        "SHELL_OUTER_D": f"{shell_outer_diameter:.4g} mm",
        "GASKET_T": f"{gasket_thickness:.4g} mm",
        # Shank
        "SHANK_HOLE_D": f"{2 * shank_hole_radius:.4g} mm",
        "SHANK_OD": f"{shank_diameter_nominal:.4g} mm",
        "SHANK_CLEARANCE_PCT": f"{shank_clearance_pct * 100:.1f}%",
        # Flavor tubes / pill slot
        "FLAVOR_TUBE_OD": f"{flavor_tube_od:.4g} mm",
        "TUBE_CENTER_Y": f"{2 * flavor_tube_y_offset:.4g} mm",
        "FLAVOR_HOLE_D": f"{flavor_tube_hole_diameter:.4g} mm",
        "FLAVOR_HOLE_CLEARANCE": f"{flavor_hole_clearance:.4g} mm",
        "TUBE_OVERLAP": f"{tube_overlap:.4g} mm",
        "PLATE_FLAVOR_X": f"{pill_slot_center[0]:.4g} mm",
        "PLATE_PILL_L": f"{pill_slot_length_y:.4g} mm",
        "PLATE_PILL_W": f"{pill_slot_width_x:.4g} mm",
        # Top-outer fillet
        "TOP_FILLET_R": f"{top_outer_fillet_r:.4g} mm",
        "FILLET_RATIO": f"{fillet_ratio * 100:.4g}%",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "PLATE_T": 3,
            "PLATE_X": 3,
            "PLATE_Z_BOTTOM": 1,
            "PREV_PLATE_T": 1,
            "PLATE_TRIM": 1,
            "PLATE_TO_SHELL_GAP": 2,
            "SHELL_OUTER_D": 1,
            "GASKET_T": 1,
            "SHANK_HOLE_D": 1,
            "SHANK_OD": 1,
            "SHANK_CLEARANCE_PCT": 1,
            "FLAVOR_TUBE_OD": 1,
            "TUBE_CENTER_Y": 1,
            "FLAVOR_HOLE_D": 1,
            "FLAVOR_HOLE_CLEARANCE": 1,
            "TUBE_OVERLAP": 1,
            "PLATE_FLAVOR_X": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
            "TOP_FILLET_R": 2,
            "FILLET_RATIO": 1,
        },
    )
    print("-> README.md")

    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "PLATE_T": 2,
            "PLATE_X": 1,
            "PREV_PLATE_T": 1,
            "PLATE_TRIM": 1,
            "PLATE_TO_SHELL_GAP": 2,
            "SHELL_OUTER_D": 1,
            "GASKET_T": 1,
            "SHANK_HOLE_D": 1,
            "SHANK_OD": 1,
            "SHANK_CLEARANCE_PCT": 1,
            "FLAVOR_TUBE_OD": 1,
            "TUBE_CENTER_Y": 1,
            "FLAVOR_HOLE_D": 1,
            "FLAVOR_HOLE_CLEARANCE": 1,
            "TUBE_OVERLAP": 1,
            "PLATE_FLAVOR_X": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
            "TOP_FILLET_R": 1,
            "FILLET_RATIO": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
