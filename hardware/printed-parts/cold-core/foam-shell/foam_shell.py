"""Foam shell — the PET-GF enclosure for the cold core's pressure
carbonator + copper evaporator coil + flavor reservoir pockets. See
README.md."""

import argparse
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

from _materials import C_FOAM_SHELL
from _foam_shell import build_full_shell
from _cold_core_interface import (
    above_carbonator_elbows_height,
    attachment_xy_positions,
    casing_foil_land,
    seam_channel_depth,
    seam_channel_land,
    seam_channel_width,
    bag_pocket_corner_inner_radius,
    bag_pocket_far_inner_x,
    bag_pocket_outermost_x,
    bag_pocket_width,
    bag_pocket_y_inner_max,
    coil_radial_clearance,
    carbonator_coil_envelope_radius,
    corner_round_radius,
    forward_band_width,
    outer_shell_wall,
    pour_band_pocket_side_y,
    pour_band_shell_side_y,
    foam_cap_interior_height,
    cap_shell_clearance,
    cap_lid_clearance,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_shell_outer_height,
    foam_shell_rim_z,
    insert_pocket_depth,
    front_wall_x,
    mid_screw_x_offset,
    outer_shell_foam_gap,
    port_lane_inner_y,
    port_lane_mid_y,
    port_lane_outer_y,
    outer_shell_x_length,
    outer_shell_y_length,
    pocket_centerward_arc_outer_radius,
    port_hole_radius,
    reservoir_clearance,
    screw_boss_size,
    support_ring_radial_width,
    carbonator_height,
    carbonator_outer_radius,
    carbonator_support_ring_height,
    wall_and_floor_thickness,
    wall_thickness,
)
from _reservoir_pocket_walls import (
    pocket_centerward_arc_transition_y,
    transition_outer_r,
)
from _port_cuts import co2_inlet_xyz
from _cold_core_interface import (
    cap_screw_beyond_face,
    cap_screw_length,
    head_cbore_radius,
    head_pad_height,
    insert_length,
    screw_head_height,
)
from docgen import substitute_md

from _copper_ports import evap_cross_z, hole_radius as copper_hole_radius, stations



def numbers():
    """The shell's native mating profile, standing stock and open passages."""
    import fits
    import _cold_core_interface as core
    import _reservoir_pocket_walls as pockets
    import _support_ring as support
    import _reed_channels as reeds
    import _reed_b_outlet as outlet
    import _internal_routes as routes
    import _reservoir_b_fill as b_fill
    import _above_core_mounts as mounts
    from _foam_cap import top_cap_height
    from _materials import linear

    def box(x, y, z):
        return [list(x), list(y), list(z)]

    envelopes, cavities, openings, upper_backs, roofs = [], [], [], [], []
    for side in (1, -1):
        x = side * core.reed_channel_inner_x
        envelopes.append(box((x, x + side * (core.reed_x_depth + core.wall_thickness)),
                             reeds.reed_envelope_y_range, reeds.reed_envelope_z_range))
        cavities.append(box((x, x + side * core.reed_x_depth),
                            reeds.reed_cavity_y_range, reeds.reed_cavity_z_range))
        openings.append(box((side * core.bag_pocket_far_inner_x,
                             side * core.bag_pocket_outermost_x),
                            reeds.reed_cavity_y_range,
                            (core.wall_and_floor_thickness, core.foam_shell_outer_height)))
        upper_backs.append(box((side * core.bag_pocket_far_inner_x,
                               side * core.reed_channel_inner_x),
                              reeds.reed_envelope_y_range,
                              (core.foam_shell_outer_height, core.foam_shell_rim_z)))
        x0, x1 = sorted((side * core.bag_pocket_far_inner_x,
                         side * core.bag_pocket_outermost_x))
        y0, y1 = reeds.reed_cavity_y_range
        z = core.foam_shell_outer_height
        roofs.append({
            "section": [(y0, z), (y1, z),
                        (reeds.reed_y_center, z + 2.0 * core.reed_y_half_w)],
            "start_x": x0, "depth": x1 - x0,
        })

    def world_to_shell(point):
        x, y, z = mounts.above_core.world_to_cap(point)
        return (-x, -y, z + core.foam_shell_outer_height + top_cap_height)

    origin = world_to_shell((0.0, 0.0, 0.0))
    axes = [tuple(b - a for a, b in zip(origin, world_to_shell(axis)))
            for axis in ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))]
    b_passage = b_fill.passage()
    b_end = b_passage['bend_end_world_mm']
    return {
        "height": core.foam_shell_rim_z,
        "pocket_height": core.foam_shell_outer_height,
        "floor": core.wall_and_floor_thickness,
        "wall": core.wall_thickness, "outer_wall": core.outer_shell_wall,
        "width": core.outer_shell_x_length, "depth": core.outer_shell_y_length,
        "corner_radius": core.corner_round_radius,
        "pocket": {
            "middle_x": pockets.middle_cavity_x, "inner_y": pockets.y_inner,
            "far_x": core.bag_pocket_far_inner_x,
            "corner_radius": core.bag_pocket_corner_inner_radius,
            "transition_y": pockets.pocket_centerward_arc_transition_y,
            "transition_x": pockets.transition_center_x - pockets.transition_cavity_r,
            "transition_mid_y": pockets.transition_center_y,
            "arc_radius": pockets.arc_cavity_r,
        },
        "support": {
            "outer_radius": core.carbonator_coil_envelope_radius,
            "inner_radius": core.carbonator_coil_envelope_radius - core.support_ring_radial_width,
            "bottom": core.wall_and_floor_thickness,
            "top": core.wall_and_floor_thickness + core.carbonator_support_ring_height,
            "slots": support.slot_count, "slot_angle": support.slot_angular_width,
            "slot_clock": support.slot_clock, "slot_margin": support.slot_radial_margin,
        },
        "host_radius": core.screw_guard_diameter / 2.0,
        "attachment_stations": [{"xy": xy, "wall": wall}
                                for xy, wall in core.attachment_stations],
        "insert_radius": core.insert_pocket_radius,
        "insert_depth": core.insert_pocket_depth,
        "tail_radius": core.screw_clearance_radius,
        "bottom_tail_depth": core.bottom_screw_bore_depth,
        "top_tail_depth": core.top_screw_bore_depth,
        "bottom_tapers": [
            {"bottom": core.insert_pocket_depth + fits.supported_surface,
             "lower_radius": core.insert_pocket_radius,
             "upper_radius": core.screw_clearance_radius,
             "height": 2.0 * (core.insert_pocket_radius - core.screw_clearance_radius)},
            {"bottom": core.bottom_screw_bore_depth + fits.supported_surface,
             "lower_radius": core.screw_clearance_radius, "upper_radius": 0.0,
             "height": 2.0 * core.screw_clearance_radius},
        ],
        "supported_surface": fits.supported_surface,
        "seam_depth": core.seam_channel_depth, "seam_width": core.seam_channel_width,
        "reed_envelopes": envelopes, "reed_cavities": cavities,
        "reed_openings": openings, "reed_upper_backs": upper_backs,
        "reed_roofs": roofs,
        "reed_b_outlet": outlet.datums(),
        "vent_route": routes.routes["prv-vent"], "vent_bend": routes.route_bend_radius,
        "vent_radius": core.port_hole_radius,
        "copper_radius": copper_hole_radius,
        "copper_origins": [point for point, _axis in stations().values()],
        "copper_names": list(stations()),
        "b_fill": {
            "bend_radius": b_fill.BEND_RADIUS,
            "channel_centre": b_fill.CHANNEL_CENTRE,
            "channel_radius": b_fill.CHANNEL_RADIUS,
            "mouth": b_fill.MOUTH,
            "mouth_start_y": -0.3,
            "mouth_end_y": b_fill.MOUTH + 0.05,
            "mouth_start_radius": b_fill.CHANNEL_RADIUS + b_fill.MOUTH + 0.3,
            "mouth_end_radius": b_fill.CHANNEL_RADIUS - 0.05,
            "inlet_leg": b_end[1] - b_fill.BEND_RADIUS - b_passage['entry_world_mm'][1],
            "bend_end_world": b_end,
            "roof_allowance": b_passage['supported_roof_allowance_mm'],
            "world_to_shell_origin": origin,
            "world_to_shell_axes": axes,
        },
        "color": list(linear(C_FOAM_SHELL)),
    }



def _report_front_ports(shell):
    """Every penetration is on the front face, so each station is measured, not assumed.

    EVERY STATION IS OPEN: a probe one clearance inside each bore, run from outside the −X
    face through the wall, meets no material. A station that reads closed is a port that is
    not there; that does not show up in a bounding box, and the whole edition's width rests
    on this face working."""
    import cadquery as cq
    solid = shell.val() if hasattr(shell, "val") else shell

    # EVERY STATION ON EITHER LANE, probed on its own lane's y — the two lanes each
    # carry one of the evaporator's coppers, so a check that read them all on the port
    # lane would report the west lane's as blocked and the port lane's slot as its bore.
    clear = copper_hole_radius - 0.25
    ports = stations()
    for name, ((sx, sy, sz), _axis) in sorted(ports.items(), key=lambda kv: kv[1][0][2]):
        probe = cq.Solid.makeCylinder(
            clear, wall_and_floor_thickness + 2.0,
            cq.Vector(sx - 1.0, sy, sz), cq.Vector(1, 0, 0))
        blocked = probe.intersect(solid).Volume()
        assert blocked <= 1e-3, (
            f"the front-face station {name} at y {sy:.4g} z {sz:.4g} is blocked by "
            f"{blocked:.4f} mm³ — the bore does not go through")
    print(f"  front face:       {len(ports)} stations on x {front_wall_x:.4g}, all open — "
          + ", ".join(f"{n} y {p[1]:.4g} z {p[2]:.4g}"
                      for n, (p, _a) in sorted(ports.items(), key=lambda kv: kv[1][0][2])))


def native_main(output=_here):
    from _cadq_export import export_assembly
    from _materials import one_body
    from _show_skin import write_bed_file

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    foam_shell = build_full_shell()
    export_assembly(one_body(foam_shell, "foam-shell", C_FOAM_SHELL),
                    str(output / "foam-shell.step"))
    print("-> foam-shell.step")
    # STEP and print mesh carry the same smooth casing surface.
    write_bed_file(foam_shell, output / "foam-shell.stl")

    _report_front_ports(foam_shell)

    solid = foam_shell.val()
    bbox = solid.BoundingBox()
    volume = solid.Volume()
    centroid = solid.Center()
    if (output / "README.md").is_file():
        update_readme(output, volume, bbox, centroid)


def update_readme(output, volume, bbox, centroid):

    substitute_md(
        output / "README.md",
        variables={
            "OUTER_H": f"{foam_shell_rim_z:.4g} mm",
            "SHELL_OUTER_X": f"{outer_shell_x_length:.4g} mm",
            "FSHELL_OUTER_Y": f"{outer_shell_y_length:.4g}",
            "OUTER_GAP": f"{outer_shell_foam_gap:.4g} mm",
            "FSHELL_WALL_T": f"{wall_thickness:.4g} mm",
            "FSHELL_FLOOR_T": f"{wall_and_floor_thickness:.4g} mm",
            "TANK_H": f"{carbonator_height:.4g} mm",
            "TANK_R": f"{carbonator_outer_radius:.4g} mm",
            "POCKET_ARC_R": f"{pocket_centerward_arc_outer_radius:.4g} mm",
            "POCKET_ARC_INNER_R": f"{pocket_centerward_arc_outer_radius - wall_thickness:.4g} mm",
            "POCKET_Y_OUTER": f"{bag_pocket_width / 2:.4g} mm",
            "POCKET_Y_INNER": f"{bag_pocket_y_inner_max:.4g} mm",
            "POCKET_ARC_TRANSITION_Y": f"{pocket_centerward_arc_transition_y:.4g} mm",
            "TRANSITION_ARC_R": f"{transition_outer_r:.4g} mm",
            "COIL_GAP": f"{coil_radial_clearance:.4g} mm",
            "ELBOW_ENV": f"{above_carbonator_elbows_height:.4g} mm",
            "RESERVOIR_GAP": f"{reservoir_clearance:.4g} mm",
            "POCKET_CORNER_R": f"{bag_pocket_corner_inner_radius:.4g} mm",
            "POCKET_X_OUTER": f"{bag_pocket_outermost_x:.4g} mm",
            "POCKET_X_INNER": f"{bag_pocket_far_inner_x:.4g} mm",
            "SUPPORT_RING_H": f"{carbonator_support_ring_height:.4g} mm",
            "SUPPORT_RING_W": f"{support_ring_radial_width:.4g} mm",
            "SUPPORT_RING_INNER_R": f"{carbonator_coil_envelope_radius - support_ring_radial_width:.4g} mm",
            "TUBE_HOLE_D": f"{port_hole_radius * 2:.4g} mm",
            "COPPER_HOLE_D": f"{2.0 * copper_hole_radius:.4g} mm",
            "CORNER_ROUND_R": f"{corner_round_radius:.4g} mm",
            "FOIL_LAND": f"{casing_foil_land:.4g} mm",
            "SEAM_CHANNEL_W": f"{seam_channel_width:.4g} mm",
            "SEAM_CHANNEL_D": f"{seam_channel_depth:.4g} mm",
            "SEAM_CHANNEL_LAND": f"{seam_channel_land:.4g} mm",
            "FSHELL_OUTER_WALL": f"{outer_shell_wall:.4g} mm",
            "FSHELL_POUR_BAND": f"{abs(pour_band_shell_side_y - pour_band_pocket_side_y):.4g} mm",
            "FSHELL_FORWARD_BAND": f"{forward_band_width:.4g} mm",
            "BOSS_D": f"{screw_boss_size:.4g} mm",
            "CAP_H": f"{foam_cap_interior_height - cap_shell_clearance - cap_lid_clearance:.4g} mm",
            # The top cup pours shallower by the band its lid's solid plate stands in.
            "CAP_H_TOP": f"{foam_cap_interior_height - head_pad_height - cap_shell_clearance - cap_lid_clearance:.4g} mm",
            "POUR_D": f"{foam_cap_lid_pour_radius * 2:.4g} mm",
            "LID_VENT_D": f"{foam_cap_lid_vent_radius * 2:.4g} mm",
            "MID_BOSS_OFFSET": f"{mid_screw_x_offset:.4g} mm",
            # The station count, and what it costs in hardware. One insert per station per
            # face, one screw per insert — so a station added anywhere carries all three.
            "BOSS_COUNT": f"{len(attachment_xy_positions):g}",
            "FACE_SCREWS": f"{len(attachment_xy_positions):g}",
            "STACK_INSERTS": f"{2 * len(attachment_xy_positions):g}",
            "INSERT_DEPTH": f"{insert_pocket_depth:.4g} mm",
            "CAP_SCREW_LEN": f"{cap_screw_length:.4g}",
            "SCREW_HEAD_H": f"{screw_head_height:.4g} mm",
            "HEAD_CBORE_D": f"{head_cbore_radius * 2:.4g} mm",
            "HEAD_PAD_H": f"{head_pad_height:.4g} mm",
            "CAP_SCREW_REACH": f"{cap_screw_beyond_face:.4g} mm",
            "INSERT_LEN": f"{insert_length:.4g} mm",
            "TIP_CLEAR": f"{insert_pocket_depth - cap_screw_beyond_face:.4g} mm",
            # CO2 inlet — the Y the bore starts at (the carbonator bottom plate's own
            # port axis) and the Z it shares with the water outlet.
            "CO2_BORE_Y": f"{co2_inlet_xyz[1]:.4g}",
            "CO2_BORE_Z": f"{co2_inlet_xyz[2]:.4g}",
            # The front face and its port lane.
            "LANE_Y": f"{port_lane_outer_y:.4g} to {port_lane_inner_y:.4g}",
            "LANE_W": f"{port_lane_inner_y - port_lane_outer_y:.4g} mm",
            "LANE_MID_Y": f"{port_lane_mid_y:.4g}",
            "COPPER_Z": f"{evap_cross_z:.4g} mm",
            "FSHELL_VOLUME": f"{volume:.3f} mm³",
            "FSHELL_BBOX_X": f"{bbox.xmin:.3f} to {bbox.xmax:.3f} mm",
            "FSHELL_BBOX_Y": f"{bbox.ymin:.3f} to {bbox.ymax:.3f} mm",
            "FSHELL_BBOX_Z": f"{bbox.zmin:.3f} to {bbox.zmax:.3f} mm",
            "CENTROID": f"({centroid.x:.6f}, {centroid.y:.6f}, {centroid.z:.6f}) mm",
        },
    )
    print("-> README.md")


def main(output=_here):
    import _rust_part

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    readings = _rust_part.cut("cold-core", "foam-shell", numbers(), output)["bodies"][0]
    ports = readings["front_ports"]
    print(f"  front face:       {len(ports)} stations on x {front_wall_x:.4g}, all open — "
          + ", ".join(f"{p['name']} y {p['origin'][1]:.4g} z {p['origin'][2]:.4g}" for p in ports))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true", help="Run the retained native builder")
    parser.add_argument("--output", type=Path, default=_here)
    args = parser.parse_args()
    (native_main if args.native else main)(args.output)
