"""PET-GF15 above-counter plate with three recessed M3 seats and locating pedestals."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(_here.parent / "faucet-shell"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK, one_body
from _faucet_interface import (
    above_counter_plate_thickness,
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
)
from faucet_shell import (
    build_foot_outline,
    foot_width,
    foot_depth,
    foot_center_y,
    base_pod_centers,
    base_pod_counterbore_dia,
    base_pod_shank_dia,
    base_screw_counterbore_depth,
    base_screw_length,
    base_plate_seat_thickness,
    base_pedestal_dia,
    base_pedestal_height,
    base_pedestal_chamfer,
    build_lower_signal_lane,
    write_bed_file,
)
from docgen import substitute_md
from world_workplane import WorldWorkplane, xy_plane_z_up

plate_thickness = above_counter_plate_thickness
plate_z_range = (-plate_thickness, 0.0)
plate_center = (0.0, foot_center_y)
shank_diameter_nominal = 11.0
shank_hole_radius = shank_hole_diameter / 2.0
shank_hole_center = (0.0, 0.0)
pill_slot_center = (0.0, flavor_tube_depth)


def vertical_cylinder(center, radius, z_range):
    """Cylinder parallel to world Z, with a named XY center and bottom/top."""
    z_min, z_max = z_range
    return (WorldWorkplane(xy_plane_z_up).workplane(offset=z_min)
            .moveTo(center).circle(radius).extrude(z_max - z_min).unwrap())


def vertical_x_slot(center, length_x, width_y, z_range):
    """The flavor pair's X-oriented pill through a world-Z interval."""
    z_min, z_max = z_range
    return (WorldWorkplane(xy_plane_z_up).workplane(offset=z_min)
            .moveTo(center).slot2D(length_x, width_y, angle=0)
            .extrude(z_max - z_min).unwrap())


def build_above_counter_plate() -> cq.Workplane:
    """Oval plate with three locating pedestals over recessed screw seats."""
    z0, z1 = plate_z_range
    plate = build_foot_outline(z0, plate_thickness)
    for center in base_pod_centers:
        pedestal = vertical_cylinder(center, base_pedestal_dia / 2.0, (0.0, base_pedestal_height))
        plate = plate.union(pedestal.edges(">Z").chamfer(base_pedestal_chamfer))
        plate = plate.cut(vertical_cylinder(center, base_pod_shank_dia / 2.0, (z0, base_pedestal_height)))
        plate = plate.cut(vertical_cylinder(
            center, base_pod_counterbore_dia / 2.0,
            (z0, z0 + base_screw_counterbore_depth)))
    plate = plate.cut(vertical_cylinder(shank_hole_center, shank_hole_radius, plate_z_range))
    return (plate.cut(vertical_x_slot(pill_slot_center, pill_length_x, pill_width_y, plate_z_range))
            .cut(build_lower_signal_lane()))


def main():
    plate = build_above_counter_plate()
    out = _here / "above-counter-plate.step"
    export_assembly(one_body(plate, out.stem, C_FAUCET_BLACK), str(out))
    print(f"-> {out.name}")
    stl = out.with_suffix(".stl")
    write_bed_file(plate, stl)
    variables = {
        "PLATE_T": f"{plate_thickness:.4g} mm",
        "PLATE_Z_BOTTOM": f"{plate_z_range[0]:.4g}",
        "PLATE_Y": f"{foot_center_y:.4g} mm",
        "FOOT_WIDTH": f"{foot_width:.4g} mm",
        "FOOT_DEPTH": f"{foot_depth:.4g} mm",
        "PEDESTAL_CHAMFER": f"{base_pedestal_chamfer:.4g} mm",
        "CBORE_D": f"{base_pod_counterbore_dia:.4g} mm",
        "CBORE_DEPTH": f"{base_screw_counterbore_depth:.4g} mm",
        "SEAT_T": f"{base_plate_seat_thickness:.4g} mm",
        "PEDESTAL_D": f"{base_pedestal_dia:.4g} mm",
        "PEDESTAL_H": f"{base_pedestal_height:.4g} mm",
        "SCREW_LENGTH": f"{base_screw_length:.4g} mm",
        "SHANK_D": f"{base_pod_shank_dia:.4g} mm",
        "SHANK_HOLE_D": f"{shank_hole_diameter:.4g} mm",
        "PLATE_FLAVOR_Y": f"{flavor_tube_depth:.4g} mm",
        "PLATE_PILL_L": f"{pill_length_x:.4g} mm",
        "PLATE_PILL_W": f"{pill_width_y:.4g} mm",
    }
    substitute_md(_here / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
