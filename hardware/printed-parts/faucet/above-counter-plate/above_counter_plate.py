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

from _rust_data import request


def _data():
    return request("faucet-data", "faucet-data", {
        "op": "above-counter-plate", "color": list(linear(C_FAUCET_BLACK)),
        "shell": {
            'foot_width': foot_width,
            'foot_depth': foot_depth,
            'foot_center_y': foot_center_y,
            'base_pod_centers': base_pod_centers,
            'base_pedestal_dia': base_pedestal_dia,
            'base_pedestal_height': base_pedestal_height,
            'base_pedestal_chamfer': base_pedestal_chamfer,
            'base_pod_shank_dia': base_pod_shank_dia,
            'base_pod_counterbore_dia': base_pod_counterbore_dia,
            'base_screw_counterbore_depth': base_screw_counterbore_depth,
            'base_plate_seat_thickness': base_plate_seat_thickness,
            'base_screw_length': base_screw_length,
            'signal_lower_exit_x': signal_lower_exit_x,
            'signal_lower_exit_y': signal_lower_exit_y,
        },
        "lower_bundle": lower_bundle_numbers(),
    })


globals().update(_data()["datums"])
plate_z_range = tuple(plate_z_range)
plate_center = tuple(plate_center)
shank_hole_center = tuple(shank_hole_center)
pill_slot_center = tuple(pill_slot_center)


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
    """The Rust scalar program supplies the countertop stack recipe."""
    return _data()["numbers"]


def main():
    # A run cuts the plate; an import of this module is a reader of its builder and numbers.
    import _rust_part

    said = _rust_part.cut("faucet", "above-counter-plate", numbers(), _here)
    print("-> " + ", ".join(said["files"]))
    variables = _data()["variables"]

    substitute_md(_here / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
