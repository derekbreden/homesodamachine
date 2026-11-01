"""PET-GF15 above-counter plate with three recessed M3 seats and locating pedestals.

The kernel cuts the plate (`above_counter_plate.rs`, beside this module) from the numbers
`numbers()` writes for it (`hardware/scripts/_rust_part.py`). `build_above_counter_plate` draws it
in CadQuery for the faucet assembly's CadQuery assembly, which reads it.
"""

from __future__ import annotations

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(_here.parent / "faucet-shell"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq  # noqa: E402
from _materials import C_FAUCET_BLACK, linear
from _faucet_interface import (
    above_counter_plate_thickness,
    flavor_tube_depth,
    pill_length_x,
    pill_width_y,
    shank_hole_diameter,
    bundle_slot_length_x,
    bundle_slot_center_x,
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
    lower_bundle_numbers,
    signal_lower_exit_x,
    signal_lower_exit_y,
)
from docgen import substitute_md
from world_workplane import WorldWorkplane, xy_plane_z_up

plate_thickness = above_counter_plate_thickness
plate_z_range = (-plate_thickness, 0.0)
plate_center = (0.0, foot_center_y)
shank_diameter_nominal = 11.0
shank_hole_radius = shank_hole_diameter / 2.0
shank_hole_center = (0.0, 0.0)
pill_slot_center = (bundle_slot_center_x, flavor_tube_depth)


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
    return (plate.cut(vertical_x_slot(pill_slot_center, bundle_slot_length_x, pill_width_y, plate_z_range))
            .cut(build_lower_signal_lane()))


def numbers() -> dict:
    """What `above_counter_plate.rs` cuts the plate from: its oval foot, the pedestals and screw
    seats over the mounting pods, and the holes through it."""
    return {
        "name": "above-counter-plate", "color": [float(v) for v in linear(C_FAUCET_BLACK)],
        "foot_width": foot_width, "foot_depth": foot_depth, "foot_center_y": foot_center_y,
        "plate_z": list(plate_z_range),
        "base_pod_centers": [[float(v) for v in center] for center in base_pod_centers],
        "base_pedestal_dia": base_pedestal_dia, "base_pedestal_height": base_pedestal_height,
        "base_pedestal_chamfer": base_pedestal_chamfer,
        "base_pod_shank_dia": base_pod_shank_dia,
        "base_pod_counterbore_dia": base_pod_counterbore_dia,
        "base_screw_counterbore_depth": base_screw_counterbore_depth,
        "shank_hole_center": list(shank_hole_center), "shank_hole_radius": shank_hole_radius,
        "pill_slot_center": list(pill_slot_center), "pill_length_x": bundle_slot_length_x,
        "pill_width_y": pill_width_y,
        **lower_bundle_numbers(),
    }


def main():
    # A run cuts the plate; an import of this module is a reader of its builder and numbers.
    import _rust_part

    said = _rust_part.cut("faucet", "above-counter-plate", numbers(), _here)
    print("-> " + ", ".join(said["files"]))
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
        "PLATE_FLAVOR_X": f"{bundle_slot_center_x:.4g} mm",
        "PLATE_RIBBON_X": f"{signal_lower_exit_x:.4g} mm",
        "PLATE_RIBBON_Y": f"{signal_lower_exit_y:.6g} mm",
        "PLATE_PILL_L": f"{bundle_slot_length_x:.4g} mm",
        "PLATE_PILL_W": f"{pill_width_y:.4g} mm",
    }
    substitute_md(_here / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
