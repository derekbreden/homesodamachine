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

wall = shell.wall_thickness_min
foot_radius = max(shell.foot_width, shell.foot_depth) / 2.0
foot_top = 14.0
body_center_y = 5.4
# The lower signal turn requires 1.0 mm beyond the donor-based radius.
# The native cylindrical-face reading checks its complete two-millimetre wall.
signal_turn_stock_allowance = 1.0
body_radius = (shell.westbrass_bore_diameter / 2.0 + body_center_y
               + wall + signal_turn_stock_allowance)
body_top = shell.zone4_z_top
neck_center_y = shell.soda_faucet_tube_y + shell.tube_shell_center_y
neck_radius = shell.tube_shell_outer_r
neck_join_z = shell.zone5_z_top
neck_join_overlap = 0.2


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


# The printed pieces, each one solid.
PIECES = {"base": "industrial-shell-base", "cover": "industrial-display-cover",
          "plate": "industrial-above-counter-plate", "gasket": "industrial-above-counter-gasket"}


def numbers():
    """What `industrial_faucet.rs` cuts the pieces from: the shell's numbers, for the gooseneck
    and the cutters the Industrial shares, with its own stock, lever opening, plate, gasket and
    display cover."""
    import industrial_display_cover as cover

    return {
        **shell.numbers(),
        **cover.numbers(),
        "name": "industrial-faucet",
        "names": {**PIECES, "seated": cover.SEATED_STEP.stem},
        "gasket_color": [float(v) for v in linear(M_TPU_BLACK)],
        # The round foot, the body over the Westbrass, and the neck standing on it past the seam.
        "foot_radius": foot_radius, "foot_top": foot_top,
        "body_radius": body_radius, "body_center_y": body_center_y, "body_top": body_top,
        "neck_radius": neck_radius, "neck_center_y": neck_center_y,
        "neck_join_overlap": neck_join_overlap,
        # The plate's pedestals and screw bores, and the holes through plate and gasket.
        "plate_z": list(plate.plate_z_range), "gasket_z": list(gasket.gasket_z_range),
        "base_pedestal_dia": shell.base_pedestal_dia,
        "base_pedestal_height": shell.base_pedestal_height,
        "base_pedestal_chamfer": shell.base_pedestal_chamfer,
        "base_pod_shank_dia": shell.base_pod_shank_dia,
        "base_pod_counterbore_dia": shell.base_pod_counterbore_dia,
        "base_screw_counterbore_depth": shell.base_screw_counterbore_depth,
        "shank_hole_center": list(plate.shank_hole_center),
        "shank_hole_radius": plate.shank_hole_radius,
        "pill_slot_center": list(plate.pill_slot_center),
    }


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
