"""Foam shell — the PETG enclosure for the cold core's pressure
vessel + copper evaporator coil + flavor reservoir pockets. See
README.md."""

import sys
from pathlib import Path

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
    mid_screw_x_offset,
    outer_shell_foam_gap,
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
    co2_doorway_y,
    co2_inlet_bore_radius,
    co2_inlet_bore_z,
)
from _cold_core_interface import co2_inlet_y
from docgen import substitute_md

sys.path.insert(0, str(_here.parent / "copper-plugs"))
from copper_plugs import plug_specs  # noqa: E402


def _plug_span(name):
    """"low → high" Z span of one copper plug, as the README's table reads it."""
    z_bottom, z_top = plug_specs[name].z_range
    return f"{z_bottom:.4g} → {z_top:.4g}"


def main():
    foam_shell = build_full_shell()
    export_step(foam_shell, str(_here / "foam-shell.step"))
    print("-> foam-shell.step")

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
            # CO2 elbow doorway — bore, the +Y wall face it is cut from, and
            # the tube's Y through the cap stack above it. The cap is authored
            # with its bore on −Y and installs rotated 180°, so the tube comes
            # down at −co2_inlet_y, on the doorway's side.
            "CO2_BORE_D": f"⌀{2 * co2_inlet_bore_radius:.4g}",
            "CO2_DOORWAY_Y": f"+{co2_doorway_y:.4g}",
            "CO2_BORE_Z": f"{co2_inlet_bore_z:.4g}",
            "CO2_CAP_HOLE_Y": f"+{-co2_inlet_y:.4g}",
            # Copper-plug Z spans — the plugs tile the slot end-to-end, each
            # end face landing on a pass-through center.
            "PLUG_SPAN_LOWER": _plug_span("lower"),
            "PLUG_SPAN_MIDDLE": _plug_span("middle"),
            "PLUG_SPAN_UPPER": _plug_span("upper"),
            "PLUG_SPAN_TOP": _plug_span("top"),
            "FSHELL_VOLUME": f"{volume:.3f} mm³",
            "FSHELL_BBOX_X": f"{bbox.xmin:.3f} to {bbox.xmax:.3f} mm",
            "FSHELL_BBOX_Y": f"{bbox.ymin:.3f} to {bbox.ymax:.3f} mm",
            "FSHELL_BBOX_Z": f"{bbox.zmin:.3f} to {bbox.zmax:.3f} mm",
            "CENTROID": f"({centroid.x:.6f}, {centroid.y:.6f}, {centroid.z:.6f}) mm",
        },
        expected_counts={
            "OUTER_H": 2,
            "OUTER_X": 1,
            "FSHELL_OUTER_Y": 1,
            "OUTER_GAP": 2,
            "FSHELL_WALL_T": 2,
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
            "TUBE_HOLE_D": 8,
            "CORNER_ROUND_R": 1,
            "BOSS_D": 3,
            "MID_BOSS_OFFSET": 2,
            "INSERT_DEPTH": 1,
            "CO2_BORE_D": 3,
            "CO2_DOORWAY_Y": 2,
            "CO2_BORE_Z": 1,
            "CO2_CAP_HOLE_Y": 1,
            "PLUG_SPAN_LOWER": 1,
            "PLUG_SPAN_MIDDLE": 1,
            "PLUG_SPAN_UPPER": 1,
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
