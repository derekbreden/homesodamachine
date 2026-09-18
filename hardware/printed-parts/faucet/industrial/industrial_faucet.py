"""Industrial faucet: cylindrical base stages with the shared gooseneck and hardware.

FRAME: X lateral, −Y toward the glass, +Z up; Z=0 is the mounting plate top.
"""

from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
HARDWARE = next(parent for parent in HERE.parents if parent.name == "hardware")
for directory in (HARDWARE / "scripts", FAUCET, FAUCET / "faucet-shell",
                  FAUCET / "above-counter-plate", FAUCET / "above-counter-gasket"):
    sys.path.insert(0, str(directory))

from _cadq_export import export_assembly, import_step
from _materials import C_FAUCET_BLACK, M_TPU_BLACK, one_body
import faucet_shell as shell
import above_counter_plate as plate
import above_counter_gasket as gasket
import flute_payload

wall = shell.wall_thickness_min
foot_radius = max(shell.foot_width, shell.foot_depth) / 2.0
foot_top = 14.0
body_center_y = 5.4
body_radius = shell.westbrass_bore_diameter / 2.0 + body_center_y + wall
body_top = shell.zone4_z_top
neck_center_y = shell.soda_faucet_tube_y + shell.tube_shell_center_y
neck_radius = shell.tube_shell_outer_r
neck_join_z = shell.zone5_z_top
neck_join_overlap = 0.2


def cylinder(radius, center_y, z_bottom, z_top):
    return cq.Solid.makeCylinder(radius, z_top - z_bottom,
                                 cq.Vector(0.0, center_y, z_bottom))


def build_lower_outer():
    foot = cylinder(foot_radius, 0.0, 0.0, foot_top)
    body = cylinder(body_radius, body_center_y, foot_top, body_top)
    neck = cylinder(neck_radius, neck_center_y, body_top,
                    neck_join_z + neck_join_overlap)
    return cq.Workplane(obj=foot.fuse(body, neck).clean())


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
        "water": shell.build_lower_soda_inner_cut(),
        "flavor": shell.build_flavor_transition_inner_cut(),
        "signal": shell.build_signal_transition_inner_cut(),
        "neck": shell._tube_shell_inner_section(
            neck_join_z, neck_join_overlap + 0.1),
    }


def build_shell_base():
    lower = build_lower_outer().val()
    for cavity in lower_cavities().values():
        lower = lower.cut(cavity.val())
    shared = import_step(FAUCET / "faucet-shell" / "faucet-shell-base.step").val()
    upper = shared.intersect(cq.Solid.makeBox(
        200.0, 400.0, 400.0, cq.Vector(-100.0, -200.0, neck_join_z)))
    return cq.Workplane(obj=lower.fuse(upper).clean())


def build_above_counter_plate():
    z0, z1 = plate.plate_z_range
    body = cq.Workplane(obj=cylinder(foot_radius, 0.0, z0, z1))
    for center in shell.base_pod_centers:
        pedestal = plate.vertical_cylinder(
            center, shell.base_pedestal_dia / 2.0,
            (0.0, shell.base_pedestal_height))
        body = body.union(pedestal.edges(">Z").chamfer(shell.base_pedestal_chamfer))
        body = body.cut(plate.vertical_cylinder(
            center, shell.base_pod_shank_dia / 2.0,
            (z0, shell.base_pedestal_height)))
        body = body.cut(plate.vertical_cylinder(
            center, shell.base_pod_counterbore_dia / 2.0,
            (z0, z0 + shell.base_screw_counterbore_depth)))
    body = body.cut(plate.vertical_cylinder(
        plate.shank_hole_center, plate.shank_hole_radius, plate.plate_z_range))
    return body.cut(plate.vertical_x_slot(
        plate.pill_slot_center, plate.pill_length_x, plate.pill_width_y,
        plate.plate_z_range)).cut(shell.build_lower_signal_lane())


def build_above_counter_gasket():
    z0, z1 = gasket.gasket_z_range
    body = cq.Workplane(obj=cylinder(foot_radius, 0.0, z0, z1))
    body = body.cut(plate.vertical_cylinder(
        plate.shank_hole_center, plate.shank_hole_radius, gasket.gasket_z_range))
    return body.cut(plate.vertical_x_slot(
        plate.pill_slot_center, plate.pill_length_x, plate.pill_width_y,
        gasket.gasket_z_range)).cut(shell.build_lower_signal_lane())


def export_piece(name, shape, color=C_FAUCET_BLACK):
    solid = shape.val()
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise ValueError(f"{name}: expected one valid printable solid")
    step = HERE / f"{name}.step"
    export_assembly(one_body(shape, name, color), str(step))
    shell.write_bed_file(shape, step.with_suffix(".stl"))
    flute_payload.cut(step, step.with_suffix(".stl"), preserve_print_triangles=True)


def main():
    from industrial_display_cover import build_display_cover

    for name, builder, material in (
        ("industrial-shell-base", build_shell_base, C_FAUCET_BLACK),
        ("industrial-display-cover", build_display_cover, C_FAUCET_BLACK),
        ("industrial-above-counter-plate", build_above_counter_plate, C_FAUCET_BLACK),
        ("industrial-above-counter-gasket", build_above_counter_gasket, M_TPU_BLACK),
    ):
        print(f"Building {name}", flush=True)
        export_piece(name, builder(), material)


if __name__ == "__main__":
    main()
