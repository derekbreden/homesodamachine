"""Industrial faucet: cylindrical base stages with the shared gooseneck and hardware.

FRAME: X lateral, −Y toward the glass, +Z up; Z=0 is the mounting plate top.

`industrial_faucet.rs` cuts the pieces from their numbers crate (`numbers.rs`). This module is
for the readers that still take them from Python: `lower_cavities` draws the base's cavities in
CadQuery for the geometry check.
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
HARDWARE = next(parent for parent in HERE.parents if parent.name == "hardware")
for directory in (HARDWARE / "scripts", FAUCET, FAUCET / "faucet-shell"):
    sys.path.insert(0, str(directory))
import cadquery as cq

import faucet_shell as shell

from _rust_data import request

_SHELL_FIELDS = (
    'wall_thickness_min',
    'foot_width',
    'foot_depth',
    'westbrass_bore_diameter',
    'zone4_z_top',
    'soda_faucet_tube_y',
    'tube_shell_center_y',
    'tube_shell_outer_r',
    'zone5_z_top',
    'base_pedestal_dia',
    'base_pedestal_height',
    'base_pedestal_chamfer',
    'base_pod_shank_dia',
    'base_pod_counterbore_dia',
    'base_screw_counterbore_depth',
)


def _data():
    payload = {"op": "industrial-body", "shell": {key: getattr(shell, key) for key in _SHELL_FIELDS}}
    return request("faucet-data", "faucet-data", payload)


globals().update(_data()["datums"])


def cylinder(radius, center_y, z_bottom, z_top):
    return cq.Solid.makeCylinder(radius, z_top - z_bottom,
                                 cq.Vector(0.0, center_y, z_bottom))


def build_lever_opening():
    opening = cq.Solid.makeBox(
        2.0 * shell.lever_clearance_x_half,
        shell.fill_y_min - shell.lever_insertion_front_y,
        body_top - shell.lever_rest_top_z,
        cq.Vector(-shell.lever_clearance_x_half,
                  shell.lever_insertion_front_y, shell.lever_rest_top_z))
    return shell.build_lever_clearance().union(cq.Workplane(obj=opening))


def lower_cavities():
    return {
        "donor-cylinder": shell.build_zone1_inner_cut(),
        "mount-sockets": shell.build_base_pod_holes(),
        "donor-body": shell.build_zone2_inner_cut(),
        "donor-arches": shell.build_zone3_inner_cut(),
        "lever": build_lever_opening(),
        "lower-signal": shell.build_lower_signal_lane(),
    }


PIECES = _data()["pieces"]
