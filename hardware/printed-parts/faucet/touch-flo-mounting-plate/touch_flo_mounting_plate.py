"""Touch-Flo mounting plate — printed PET-CF plate that supports the
harvested Touch-Flo faucet body and the two flavor tubes beside it, and
carries the three screw bosses that bolt up into the shell. Its footprint
matches the shell foot exactly (foot circle + two lateral teardrop pods +
front D-pod), reusing the shell's own geometry. See README.md."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(0, str(_here.parent))  # for _touch_flo_interface
sys.path.insert(0, str(_here.parent / "touch-flo-shell"))  # for the shared footprint
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
from _cadq_export import export_step
from _touch_flo_interface import (
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
)
from touch_flo_shell import (
    shell_outer_cyl,
    _base_pod_teardrops,
    _base_pod_front,
    base_pod_centers,
    base_pod_boss_dia,
    base_pod_counterbore_dia,
    base_pod_shank_dia,
    base_pod_hole_depth,
)
from docgen import substitute_md, substitute_py_comments
from world_workplane import WorldWorkplane, xy_plane_z_up


# [4 mm](PLATE_T) thick.
plate_thickness = 4.0
# Top face flush with the deck plane (Z=0); plate hangs below.
plate_z_range = (-plate_thickness, 0.0)
# Footprint center at world (0, +[3.175 mm](PLATE_Y)); body axis at (0, 0).
plate_center = (0.0, +3.175)


# [11 mm](SHANK_OD) threaded shank clearance.
shank_diameter_nominal = 11.0
shank_hole_radius = shank_hole_diameter / 2
shank_hole_center = (0.0, 0.0)


# Flavor-tube pill slot — two 1/4" tubes [6.35 mm](TUBE_CENTER_X) apart,
# combined into one X-oriented pill at world (0, +[18.93 mm](PLATE_FLAVOR_Y)):
# [13.4 mm](PLATE_PILL_L) long (X) × [7.05 mm](PLATE_PILL_W) wide (Y).
pill_slot_center = (0.0, +flavor_tube_depth)


# Screw bosses — one per pod center, rising from the plate top into the
# shell's boss holes. [11.55 mm](BOSS_D) OD, [7 mm](BOSS_H) tall (tops out
# shy of the hole floor — the gap absorbs the hole ceiling's bridge sag,
# insert squeeze-out, and layer-1 lips, so the plate seats on the foot, not
# the boss), with a [0.6 mm](BOSS_CHAMFER) × 45° lead-in chamfer on the top
# rim easing all three pins into their holes at once. Each bored for an
# M3x12 SHCS: a [5.55 mm](CBORE_D) counterbore through the full plate (head
# recess — the head bears on the boss base and stays clear of the gasket)
# and a [3.9 mm](SHANK_D) shank clearance up to the shell's heat-set insert.
boss_seat_clearance = 1.0
boss_height = base_pod_hole_depth - boss_seat_clearance
boss_chamfer = 0.6


def vertical_cylinder(center, radius, z_range):
    """+Z-axis cylinder: world (x, y) center tuple, radius, and Z extent."""
    z_min, z_max = z_range
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_min)
        .moveTo(center)
        .circle(radius)
        .extrude(z_max - z_min)
        .unwrap()
    )


def vertical_x_slot(center, length_x, width_y, z_range):
    """+Z-axis pill (rounded-rectangle) prism with long axis along world X."""
    z_min, z_max = z_range
    return (
        WorldWorkplane(xy_plane_z_up)
        .workplane(offset=z_min)
        .moveTo(center)
        .slot2D(length_x, width_y, angle=0)
        .extrude(z_max - z_min)
        .unwrap()
    )


def build_mounting_plate() -> cq.Workplane:
    """Shell-foot footprint (foot circle + two teardrops + front D-pod) as a
    plate_thickness slab, three screw bosses rising from the top, each
    counterbored (full plate) and shank-bored, plus the shank hole and the
    flavor-tube pill."""
    z0 = plate_z_range[0]
    foot = shell_outer_cyl(z0, plate_thickness).val()
    teardrops = _base_pod_teardrops(z0, plate_thickness).val()
    front = _base_pod_front(z0, plate_thickness).val()
    plate = cq.Workplane(obj=foot.fuse(teardrops, front))

    for center in base_pod_centers:
        boss = vertical_cylinder(center, base_pod_boss_dia / 2, (0.0, boss_height))
        plate = plate.union(boss.edges(">Z").chamfer(boss_chamfer))

    for center in base_pod_centers:
        plate = plate.cut(
            vertical_cylinder(center, base_pod_counterbore_dia / 2, (z0, 0.0))
        )
        plate = plate.cut(
            vertical_cylinder(center, base_pod_shank_dia / 2, (0.0, boss_height))
        )

    plate = plate.cut(vertical_cylinder(shank_hole_center, shank_hole_radius, plate_z_range))
    plate = plate.cut(vertical_x_slot(pill_slot_center, pill_length_x, pill_width_y, plate_z_range))
    return plate


def main():
    plate = build_mounting_plate()

    out = _here / "touch-flo-mounting-plate.step"
    export_step(plate, str(out))
    print(f"-> {out.name}")

    variables = {
        "PLATE_T": f"{plate_thickness:.4g} mm",
        "PLATE_Z_BOTTOM": f"{plate_z_range[0]:.4g}",
        "PLATE_Y": f"{plate_center[1]:.4g} mm",
        "BOSS_D": f"{base_pod_boss_dia:.4g} mm",
        "BOSS_H": f"{boss_height:.4g} mm",
        "BOSS_CHAMFER": f"{boss_chamfer:.4g} mm",
        "CBORE_D": f"{base_pod_counterbore_dia:.4g} mm",
        "SHANK_D": f"{base_pod_shank_dia:.4g} mm",
        "SHANK_HOLE_D": f"{2 * shank_hole_radius:.4g} mm",
        "SHANK_OD": f"{shank_diameter_nominal:.4g} mm",
        "TUBE_CENTER_X": f"{pill_length_x - pill_width_y:.4g} mm",
        "PLATE_FLAVOR_Y": f"{pill_slot_center[1]:.4g} mm",
        "PLATE_PILL_L": f"{pill_length_x:.4g} mm",
        "PLATE_PILL_W": f"{pill_width_y:.4g} mm",
    }

    substitute_md(
        _here / "README.md",
        variables=variables,
        expected_counts={
            "PLATE_T": 1,
            "PLATE_Z_BOTTOM": 1,
            "PLATE_Y": 1,
            "BOSS_D": 1,
            "BOSS_H": 1,
            "BOSS_CHAMFER": 1,
            "CBORE_D": 1,
            "SHANK_D": 1,
            "SHANK_HOLE_D": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_X": 1,
            "PLATE_FLAVOR_Y": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
        },
    )
    print("-> README.md")

    substitute_py_comments(
        Path(__file__),
        variables=variables,
        expected_counts={
            "PLATE_T": 1,
            "PLATE_Y": 1,
            "SHANK_OD": 1,
            "TUBE_CENTER_X": 1,
            "PLATE_FLAVOR_Y": 1,
            "PLATE_PILL_L": 1,
            "PLATE_PILL_W": 1,
            "BOSS_D": 1,
            "BOSS_H": 1,
            "BOSS_CHAMFER": 1,
            "CBORE_D": 1,
            "SHANK_D": 1,
        },
    )
    print(f"-> {Path(__file__).name}")


if __name__ == "__main__":
    main()
