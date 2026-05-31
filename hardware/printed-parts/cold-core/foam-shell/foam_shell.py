"""Foam shell — the PETG enclosure for the cold core's pressure
vessel + copper evaporator coil + flavor reservoir pockets. See
README.md."""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "printed-parts") / "cadlib"))
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))
sys.path.insert(0, str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"))

from _cadq_export import export_step
from _foam_shell import build_full_shell
from _cold_core_interface import (
    above_tank_elbows_height,
    bag_pocket_corner_inner_radius,
    bag_pocket_far_inner_x,
    bag_pocket_outermost_x,
    coil_radial_clearance,
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
from _corner_gussets import gusset_thickness, gusset_height
from docgen import substitute_md


def main():
    foam_shell = build_full_shell()
    export_step(foam_shell, str(_here / "foam-shell.step"))
    print("-> foam-shell.step")

    solid = foam_shell.val()
    bbox = solid.BoundingBox()
    volume = solid.Volume()
    centroid = solid.Center()

    # Short names scoped to this README. Units live inside the value so the
    # script controls them — change a unit in source and the markdown follows.
    substitute_md(
        _here / "README.md",
        variables={
            # Outer shell footprint + height (substituted into the design prose).
            "OUTER_H": f"{foam_shell_outer_height:.4g} mm",
            "OUTER_X": f"{outer_shell_x_length:.4g} mm",
            "OUTER_Y": f"{outer_shell_y_length:.4g}",  # unit implied from OUTER_X
            "OUTER_GAP": f"{outer_shell_foam_gap:.4g} mm",
            # Tank, coil, pocket, ring.
            "WALL_T": f"{wall_and_floor_thickness:.4g} mm",
            "TANK_H": f"{tank_height:.4g} mm",
            "TANK_R": f"{tank_outer_radius:.4g} mm",
            "POCKET_ARC_R": f"{pocket_centerward_arc_outer_radius:.4g} mm",
            "POCKET_ARC_INNER_R": f"{pocket_centerward_arc_outer_radius - wall_and_floor_thickness:.4g} mm",
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
            "SUPPORT_RING_INNER_R": f"{pocket_centerward_arc_outer_radius - wall_and_floor_thickness - support_ring_radial_width:.4g} mm",
            "PORT_D": f"{port_hole_radius * 2:.4g} mm",
            "CORNER_ROUND_R": f"{corner_round_radius:.4g} mm",
            "BOSS_D": f"{screw_boss_size:.4g} mm",
            # Corner anti-warp gussets.
            "GUSSET_T": f"{gusset_thickness:.4g} mm",
            "GUSSET_H": f"{gusset_height:.4g} mm",
            # Foam-cap, foam-cap-lid, foam-cap-gasket.
            "CAP_H": f"{foam_cap_interior_height:.4g} mm",
            "POUR_D": f"{foam_cap_lid_pour_radius * 2:.4g} mm",
            "VENT_D": f"{foam_cap_lid_vent_radius * 2:.4g} mm",
            "GASKET_T": f"{gasket_thickness:.4g} mm",
            "GASKET_W": f"{gasket_strip_width:.4g} mm",
            # Cap-to-outer-shell joinery.
            "MID_BOSS_OFFSET": f"{mid_screw_x_offset:.4g} mm",
            "INSERT_DEPTH": f"{insert_pocket_depth:.4g} mm",
            # Regression baseline (computed from the actual STEP geometry).
            "VOLUME": f"{volume:.3f} mm³",
            "BBOX_X": f"{bbox.xmin:.3f} to {bbox.xmax:.3f} mm",
            "BBOX_Y": f"{bbox.ymin:.3f} to {bbox.ymax:.3f} mm",
            "BBOX_Z": f"{bbox.zmin:.3f} to {bbox.zmax:.3f} mm",
            "CENTROID": f"({centroid.x:.6f}, {centroid.y:.6f}, {centroid.z:.6f}) mm",
        },
        expected_counts={
            "OUTER_H": 2,
            "OUTER_X": 1,
            "OUTER_Y": 1,
            "OUTER_GAP": 2,
            "WALL_T": 2,
            "TANK_H": 1,
            "TANK_R": 2,
            "POCKET_ARC_R": 4,
            "POCKET_ARC_INNER_R": 3,
            "POCKET_ARC_TRANSITION_Y": 2,
            "TRANSITION_ARC_R": 2,
            "COIL_GAP": 2,
            "ELBOW_ENV": 1,
            "RESERVOIR_GAP": 1,
            "POCKET_CORNER_R": 1,
            "POCKET_X_OUTER": 1,
            "POCKET_X_INNER": 1,
            "SUPPORT_RING_H": 1,
            "SUPPORT_RING_W": 1,
            "SUPPORT_RING_INNER_R": 1,
            "PORT_D": 8,
            "CORNER_ROUND_R": 1,
            "BOSS_D": 3,
            "GUSSET_T": 1,
            "GUSSET_H": 1,
            "CAP_H": 2,
            "POUR_D": 2,
            "VENT_D": 2,
            "GASKET_T": 2,
            "GASKET_W": 1,
            "MID_BOSS_OFFSET": 2,
            "INSERT_DEPTH": 1,
            "VOLUME": 1,
            "BBOX_X": 1,
            "BBOX_Y": 1,
            "BBOX_Z": 1,
            "CENTROID": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
