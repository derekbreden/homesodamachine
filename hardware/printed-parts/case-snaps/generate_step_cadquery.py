"""Snap-fit test case: ramp_out_first and ramp_in_first on a simple box shell."""

from pathlib import Path
import sys

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cadlib"))
from snap import apply_ramp_out_first, apply_ramp_in_first, WALL_THICKNESS, OVERCUT

FOOTPRINT = 40.0
CORNER_RADIUS = 6.0
BASE_PLATE = 3.0
WALL_HEIGHT = 9.0
ZONE_WIDTH = 20.0

HALF = FOOTPRINT / 2
INNER = HALF - WALL_THICKNESS


def make_box_shell():
    inner_dim = FOOTPRINT - 2 * WALL_THICKNESS
    inner_r = max(CORNER_RADIUS - WALL_THICKNESS, 0.01)
    outer = (
        cq.Workplane("XY").sketch()
        .rect(FOOTPRINT, FOOTPRINT).vertices().fillet(CORNER_RADIUS)
        .finalize().extrude(BASE_PLATE + WALL_HEIGHT)
    )
    cavity = (
        cq.Workplane("XY").workplane(offset=BASE_PLATE).sketch()
        .rect(inner_dim, inner_dim).vertices().fillet(inner_r)
        .finalize().extrude(WALL_HEIGHT + OVERCUT)
    )
    return outer.cut(cavity)


WALLS = {
    "+y": (INNER, +1, "YZ"),
    "-y": (-INNER, -1, "YZ"),
    "+x": (INNER, +1, "XZ"),
    "-x": (-INNER, -1, "XZ"),
}

bottom = make_box_shell()
top = make_box_shell()

for wall_id, (inner_face, orientation_outward_sign, orientation_plane) in WALLS.items():
    bottom = apply_ramp_out_first(
        solid=bottom,
        coordinate_inner_wall=inner_face,
        coordinate_zone_start=-ZONE_WIDTH / 2,
        coordinate_zone_end=ZONE_WIDTH / 2,
        coordinate_lowest_possible_snap_base_in_wall=BASE_PLATE,
        coordinate_top_of_wall=BASE_PLATE + WALL_HEIGHT,
        orientation_outward_sign=orientation_outward_sign,
        orientation_plane=orientation_plane,
        deflection_distance=2.0,
    )
    top = apply_ramp_in_first(
        solid=top,
        coordinate_inner_wall=inner_face,
        coordinate_zone_start=-ZONE_WIDTH / 2,
        coordinate_zone_end=ZONE_WIDTH / 2,
        coordinate_lowest_possible_snap_base_in_wall=BASE_PLATE,
        coordinate_top_of_wall=BASE_PLATE + WALL_HEIGHT,
        orientation_outward_sign=orientation_outward_sign,
        orientation_plane=orientation_plane,
        deflection_distance=2.0,
    )

OUTPUT_DIR = Path(__file__).resolve().parent
cq.exporters.export(bottom, str(OUTPUT_DIR / "case-snaps-bottom.step"))
cq.exporters.export(top, str(OUTPUT_DIR / "case-snaps-top.step"))
print("Exported → case-snaps-bottom.step + case-snaps-top.step")
