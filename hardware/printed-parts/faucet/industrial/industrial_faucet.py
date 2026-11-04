"""Industrial faucet: cylindrical base stages with the shared gooseneck and hardware.

FRAME: X lateral, −Y toward the glass, +Z up; Z=0 is the mounting plate top.

The kernel cuts the pieces (`industrial_faucet.rs`, beside this module) from the numbers
`numbers()` writes for it (`hardware/scripts/_rust_part.py`). `lower_cavities` draws the
base's cavities in CadQuery for the geometry check that reads them.
"""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
HARDWARE = next(parent for parent in HERE.parents if parent.name == "hardware")
for directory in (HARDWARE / "scripts", FAUCET, FAUCET / "faucet-shell",
                  FAUCET / "above-counter-plate", FAUCET / "above-counter-gasket"):
    sys.path.insert(0, str(directory))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq

from _materials import M_TPU_BLACK, linear
import faucet_shell as shell
import above_counter_plate as plate
import above_counter_gasket as gasket
import flute_payload

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


def _data(*, include_recipe=False):
    payload = {"op": "industrial-body", "shell": {key: getattr(shell, key) for key in _SHELL_FIELDS}}
    if include_recipe:
        import industrial_display_cover as cover
        payload.update(shell_numbers=shell.numbers(), cover_numbers=cover.numbers(),
                       plate=plate._data()["datums"], gasket=gasket._data()["datums"],
                       gasket_color=list(linear(M_TPU_BLACK)))
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


def numbers():
    """The Rust scalar program composes the shared geometry and round-body recipe."""
    return _data(include_recipe=True)["numbers"]


def main():
    # A run cuts the pieces; an import of this module is a reader of its builders and numbers.
    import _rust_part

    said = _rust_part.cut("faucet", "industrial-faucet", numbers(), HERE)
    print("-> " + ", ".join(said["files"]))
    for name in PIECES.values():
        step = HERE / f"{name}.step"
        flute_payload.cut(step, step.with_suffix(".stl"), preserve_print_triangles=True)


if __name__ == "__main__":
    main()
