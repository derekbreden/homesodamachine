"""Snap-fit test case: tongue-and-groove on a simple box shell."""

from pathlib import Path
import sys

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "cadlib"))
from snap import apply_tongue, apply_groove, WALL_THICKNESS, OVERCUT

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

for wall_id, (face, sign, plane) in WALLS.items():
    bottom = apply_tongue(
        bottom, face, sign, plane,
        extrude_start=-ZONE_WIDTH / 2,
        zone_width=ZONE_WIDTH,
        wall_base=BASE_PLATE,
        wall_height=WALL_HEIGHT,
    )
    top = apply_groove(
        top, face, sign, plane,
        extrude_start=-ZONE_WIDTH / 2,
        zone_width=ZONE_WIDTH,
        wall_base=BASE_PLATE,
        wall_height=WALL_HEIGHT,
    )

OUTPUT_DIR = Path(__file__).resolve().parent
cq.exporters.export(bottom, str(OUTPUT_DIR / "case-snaps-bottom.step"))
cq.exporters.export(top, str(OUTPUT_DIR / "case-snaps-top.step"))
print("Exported → case-snaps-bottom.step + case-snaps-top.step")
