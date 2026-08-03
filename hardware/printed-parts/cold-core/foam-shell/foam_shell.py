"""Foam shell — the PETG enclosure for the cold core's pressure
vessel + copper evaporator coil + flavor reservoir pockets. See
README.md."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_step
from _foam_shell import build_full_shell
from _cold_core_interface import (
    above_tank_elbows_height,
    bag_pocket_corner_inner_radius,
    bag_pocket_far_inner_x,
    bag_pocket_outermost_x,
    bag_pocket_width,
    bag_pocket_y_inner_max,
    coil_radial_clearance,
    tank_coil_envelope_radius,
    corner_round_radius,
    foam_cap_interior_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_shell_outer_height,
    gasket_strip_width,
    gasket_thickness,
    insert_pocket_depth,
    bag_pocket_floor_top_z,
    front_port_order,
    front_port_z,
    front_wall_x,
    mid_screw_x_offset,
    outer_shell_foam_gap,
    port_lane_inner_y,
    port_lane_mid_y,
    port_lane_outer_y,
    west_lane_mid_y,
    outer_shell_x_length,
    outer_shell_y_length,
    pocket_centerward_arc_outer_radius,
    port_hole_radius,
    reservoir_clearance,
    screw_boss_size,
    support_ring_radial_width,
    tank_height,
    tank_outer_radius,
    tank_support_ring_height,
    wall_and_floor_thickness,
)
from _reservoir_pocket_walls import (
    pocket_centerward_arc_transition_y,
    transition_tank_r,
)
from _port_cuts import (
    co2_inlet_xyz,
    flavor_line_hole_x,
)
from _reed_channels import cable_hole_offset_from_bulkhead_hole_x
from _cold_core_interface import reservoir_bulkhead_port_x
from _cold_core_interface import (
    cap_screw_beyond_face,
    cap_screw_length,
    head_cbore_radius,
    head_pad_height,
    insert_length,
    screw_head_height,
)
from docgen import substitute_md

sys.path.insert(0, str(_here.parent / "copper-plugs"))
from copper_plugs import plug_specs  # noqa: E402


def _report_front_ports(shell):
    """Every penetration is on the front face, and the lane is what gets it there —
    so both are measured, not assumed.

    Two claims, and the shell is judged on them at every build. (1) THE LANE RUNS
    CLEAR: the strip inboard of every attachment boss, from one corner round to the
    other, above the floor slab, holds nothing. That is what lets a line leave a
    fitting anywhere in the shell, turn west and climb to its own station. (2) EVERY
    STATION IS OPEN: a probe one clearance inside each bore, run from outside the −X
    face through the wall, meets no material.

    The lane is measured between the CORNER ROUNDS, not wall to wall: the rounds'
    inner arcs are concentric one wall inboard of the exterior ones, so each bulges
    into the lane's outboard edge as it approaches a ±X wall, pinching it to about a
    bore's width at the very corner. That pinch is not an obstruction — it is the
    material each station's bore is cut through, and (2) is what proves the bore goes
    through it. What (1) has to establish is the run BETWEEN the corners, which is
    where a line travels free.

    A station that reads closed is a port that is not there; a lane that reads
    blocked is a port with nothing behind it. Neither shows up in a bounding box, and
    the whole edition's width rests on this face working."""
    solid = shell.val() if hasattr(shell, "val") else shell
    lane_w = port_lane_inner_y - port_lane_outer_y
    free_x = front_wall_x + corner_round_radius
    lane = cq.Solid.makeBox(
        2.0 * abs(free_x), lane_w, foam_shell_outer_height - bag_pocket_floor_top_z,
        cq.Vector(free_x, port_lane_outer_y, bag_pocket_floor_top_z))
    spill = lane.intersect(solid).Volume()
    print(f"  port lane:        y {port_lane_outer_y:.4g} .. {port_lane_inner_y:.4g} "
          f"({lane_w:.4g} mm), x {free_x:.4g} .. {-free_x:.4g}, "
          f"z {bag_pocket_floor_top_z:.4g} .. {foam_shell_outer_height:.4g} — "
          f"{spill:.3f} mm³ of material in it")
    assert spill <= 1.0, (
        f"the port lane holds {spill:.3f} mm³ of material — a line cannot reach the front "
        f"face along it. Every attachment boss must stand at least "
        f"{-port_lane_outer_y:.4g} mm out in y (see attachment_xy_positions)")

    # (1b) The WEST LANE, the +Y band's own, and the one reservoir B's line climbs. It is
    # measured the same way but over the full height, because what runs in it is a RISER and
    # not a traverse: the line crosses the pocket wall low, comes about here, and goes up this
    # strip to the cap's `reservoir-b` conduit. A blocked reading is a riser with a floor
    # somewhere in it, which no bounding box shows and no station check would catch.
    west = cq.Solid.makeBox(
        2.0 * abs(free_x), lane_w, foam_shell_outer_height - bag_pocket_floor_top_z,
        cq.Vector(free_x, west_lane_mid_y - lane_w / 2.0, bag_pocket_floor_top_z))
    spill = west.intersect(solid).Volume()
    print(f"  west lane:        y {west_lane_mid_y - lane_w / 2.0:.4g} .. "
          f"{west_lane_mid_y + lane_w / 2.0:.4g} ({lane_w:.4g} mm), x {free_x:.4g} .. "
          f"{-free_x:.4g}, z {bag_pocket_floor_top_z:.4g} .. {foam_shell_outer_height:.4g} — "
          f"{spill:.3f} mm³ of material in it")
    assert spill <= 1.0, (
        f"the west lane holds {spill:.3f} mm³ of material — reservoir B's line cannot climb "
        f"it to the cap's conduit")

    clear = port_hole_radius - 0.25            # the probe, one clearance inside the bore
    stations = [(n, front_port_z(n)) for n in front_port_order]
    stations += [(f"slot:{n}", spec.z_range[0]) for n, spec in plug_specs.items()]
    for name, z in stations:
        probe = cq.Solid.makeCylinder(
            clear, wall_and_floor_thickness + 2.0,
            cq.Vector(front_wall_x - 1.0, port_lane_mid_y, z), cq.Vector(1, 0, 0))
        blocked = probe.intersect(solid).Volume()
        assert blocked <= 1e-3, (
            f"the front-face station {name} at z {z:.4g} is blocked by {blocked:.4f} mm³ — "
            f"the bore does not go through")
    print(f"  front port field: {len(stations)} stations on x {front_wall_x:.4g}, "
          f"y {port_lane_mid_y:.4g}, all open — "
          + ", ".join(f"{n} {z:.4g}" for n, z in stations))


def _plug_span(name):
    """"low → high" Z span of one copper plug, as the README's table reads it."""
    z_bottom, z_top = plug_specs[name].z_range
    return f"{z_bottom:.4g} → {z_top:.4g}"


def main():
    foam_shell = build_full_shell()
    export_step(foam_shell, str(_here / "foam-shell.step"))
    print("-> foam-shell.step")

    _report_front_ports(foam_shell)

    solid = foam_shell.val()
    bbox = solid.BoundingBox()
    volume = solid.Volume()
    centroid = solid.Center()

    substitute_md(
        _here / "README.md",
        variables={
            "OUTER_H": f"{foam_shell_outer_height:.4g} mm",
            "OUTER_X": f"{outer_shell_x_length:.4g} mm",
            "FSHELL_OUTER_Y": f"{outer_shell_y_length:.4g}",
            "OUTER_GAP": f"{outer_shell_foam_gap:.4g} mm",
            "FSHELL_WALL_T": f"{wall_and_floor_thickness:.4g} mm",
            "TANK_H": f"{tank_height:.4g} mm",
            "TANK_R": f"{tank_outer_radius:.4g} mm",
            "POCKET_ARC_R": f"{pocket_centerward_arc_outer_radius:.4g} mm",
            "POCKET_ARC_INNER_R": f"{pocket_centerward_arc_outer_radius - wall_and_floor_thickness:.4g} mm",
            "POCKET_Y_OUTER": f"{bag_pocket_width / 2:.4g} mm",
            "POCKET_Y_INNER": f"{bag_pocket_y_inner_max:.4g} mm",
            "POCKET_ARC_TRANSITION_Y": f"{pocket_centerward_arc_transition_y:.4g} mm",
            "TRANSITION_ARC_R": f"{transition_tank_r:.4g} mm",
            "COIL_GAP": f"{coil_radial_clearance:.4g} mm",
            "ELBOW_ENV": f"{above_tank_elbows_height:.4g} mm",
            "RESERVOIR_GAP": f"{reservoir_clearance:.4g} mm",
            "POCKET_CORNER_R": f"{bag_pocket_corner_inner_radius:.4g} mm",
            "POCKET_X_OUTER": f"{bag_pocket_outermost_x:.4g} mm",
            "POCKET_X_INNER": f"{bag_pocket_far_inner_x:.4g} mm",
            "SUPPORT_RING_H": f"{tank_support_ring_height:.4g} mm",
            "SUPPORT_RING_W": f"{support_ring_radial_width:.4g} mm",
            "SUPPORT_RING_INNER_R": f"{tank_coil_envelope_radius - support_ring_radial_width:.4g} mm",
            "TUBE_HOLE_D": f"{port_hole_radius * 2:.4g} mm",
            "CORNER_ROUND_R": f"{corner_round_radius:.4g} mm",
            "BOSS_D": f"{screw_boss_size:.4g} mm",
            "CAP_H": f"{foam_cap_interior_height:.4g} mm",
            "POUR_D": f"{foam_cap_lid_pour_radius * 2:.4g} mm",
            "LID_VENT_D": f"{foam_cap_lid_vent_radius * 2:.4g} mm",
            "GASKET_T": f"{gasket_thickness:.4g} mm",
            "GASKET_W": f"{gasket_strip_width:.4g} mm",
            "MID_BOSS_OFFSET": f"{mid_screw_x_offset:.4g} mm",
            "INSERT_DEPTH": f"{insert_pocket_depth:.4g} mm",
            "SCREW_LEN": f"{cap_screw_length:.4g}",
            "SCREW_HEAD_H": f"{screw_head_height:.4g} mm",
            "HEAD_CBORE_D": f"{head_cbore_radius * 2:.4g} mm",
            "HEAD_PAD_H": f"{head_pad_height:.4g} mm",
            "SCREW_REACH": f"{cap_screw_beyond_face:.4g} mm",
            "INSERT_LEN": f"{insert_length:.4g} mm",
            "TIP_CLEAR": f"{insert_pocket_depth - cap_screw_beyond_face:.4g} mm",
            # CO2 inlet — the Y the bore starts at (the vessel bottom plate's own
            # port axis) and the Z it shares with the water outlet.
            "CO2_BORE_Y": f"{co2_inlet_xyz[1]:.4g}",
            "CO2_BORE_Z": f"{co2_inlet_xyz[2]:.4g}",
            # Front pass-throughs — each is two bores that do not meet: the
            # pocket-side one beside the bulkhead, and a station on the front
            # field, joined by a run along the port lane.
            "FLAVOR_POCKET_X": f"{flavor_line_hole_x:.4g} mm",
            "CABLE_POCKET_X": f"{reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x:.4g} mm",
            # The front face and its port lane.
            "LANE_Y": f"{port_lane_outer_y:.4g} to {port_lane_inner_y:.4g}",
            "LANE_W": f"{port_lane_inner_y - port_lane_outer_y:.4g} mm",
            "LANE_MID_Y": f"{port_lane_mid_y:.4g}",
            "FIELD_Z": ", ".join(f"{n} {front_port_z(n):.4g}" for n in front_port_order),
            # The three the slot carries, named for the LINE rather than the plug
            # whose bottom end lands on each — the stack tiles the slot, so a
            # pass-through center IS a plug boundary.
            "SLOT_Z": ", ".join(
                f"{line} {plug_specs[plug].z_range[0]:.4g}" for line, plug in (
                    ("evaporator inlet", "lower"), ("evaporator outlet", "middle"),
                    ("PRV vent", "top"))),
            # How far up the wall the whole column reaches — the slot's highest line,
            # which is the top plug's bottom end because that plug fills the rest.
            "COLUMN_TOP": f"{plug_specs['top'].z_range[0]:.4g} mm",
            # Copper-plug Z spans — the plugs tile the slot end-to-end, each
            # end face landing on a pass-through center.
            "PLUG_SPAN_LOWER": _plug_span("lower"),
            "PLUG_SPAN_MIDDLE": _plug_span("middle"),
            "PLUG_SPAN_TOP": _plug_span("top"),
            "FSHELL_VOLUME": f"{volume:.3f} mm³",
            "FSHELL_BBOX_X": f"{bbox.xmin:.3f} to {bbox.xmax:.3f} mm",
            "FSHELL_BBOX_Y": f"{bbox.ymin:.3f} to {bbox.ymax:.3f} mm",
            "FSHELL_BBOX_Z": f"{bbox.zmin:.3f} to {bbox.zmax:.3f} mm",
            "CENTROID": f"({centroid.x:.6f}, {centroid.y:.6f}, {centroid.z:.6f}) mm",
        },
        expected_counts={
            "OUTER_H": 3,
            "OUTER_X": 1,
            "FSHELL_OUTER_Y": 1,
            "OUTER_GAP": 3,
            "FLAVOR_POCKET_X": 1,
            "CABLE_POCKET_X": 1,
            "LANE_Y": 1,
            "LANE_W": 1,
            "LANE_MID_Y": 1,
            "FIELD_Z": 1,
            "SLOT_Z": 1,
            "COLUMN_TOP": 1,
            "FSHELL_WALL_T": 3,
            "CAP_H": 1,
            "POUR_D": 1,
            "LID_VENT_D": 1,
            "GASKET_T": 1,
            "GASKET_W": 1,
            "TANK_H": 1,
            "TANK_R": 2,
            "POCKET_ARC_R": 1,
            "POCKET_ARC_INNER_R": 1,
            "POCKET_Y_OUTER": 4,
            "POCKET_Y_INNER": 2,
            "POCKET_ARC_TRANSITION_Y": 2,
            "TRANSITION_ARC_R": 2,
            "COIL_GAP": 2,
            "ELBOW_ENV": 1,
            "RESERVOIR_GAP": 2,
            "POCKET_CORNER_R": 1,
            "POCKET_X_OUTER": 1,
            "POCKET_X_INNER": 1,
            "SUPPORT_RING_H": 1,
            "SUPPORT_RING_W": 1,
            "SUPPORT_RING_INNER_R": 1,
            "TUBE_HOLE_D": 11,
            "CORNER_ROUND_R": 1,
            "BOSS_D": 5,
            "MID_BOSS_OFFSET": 2,
            "INSERT_DEPTH": 1,
            "SCREW_LEN": 1,
            "SCREW_HEAD_H": 1,
            "HEAD_CBORE_D": 1,
            "HEAD_PAD_H": 1,
            "SCREW_REACH": 1,
            "INSERT_LEN": 1,
            "TIP_CLEAR": 1,
            "CO2_BORE_Y": 3,
            "CO2_BORE_Z": 2,
            "PLUG_SPAN_LOWER": 1,
            "PLUG_SPAN_MIDDLE": 1,
            "PLUG_SPAN_TOP": 1,
            "FSHELL_VOLUME": 1,
            "FSHELL_BBOX_X": 1,
            "FSHELL_BBOX_Y": 1,
            "FSHELL_BBOX_Z": 1,
            "CENTROID": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
