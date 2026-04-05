from pathlib import Path

import cadquery as cq

FOOTPRINT = 40.0
CORNER_RADIUS = 6.0
BASE_PLATE_THICKNESS = 3.0
WALL_THICKNESS = 3.0
PLAIN_WALL_HEIGHT = 9.0
SNAP_ZONE_WIDTH = 20.0
OVERCUT = 0.1

HALF_FOOTPRINT = FOOTPRINT / 2
INNER_FACE_OFFSET = HALF_FOOTPRINT - WALL_THICKNESS

TONGUE_GROWTH_BEYOND_WALL = 2.0
FLEXING_SECTION_WIDTH = 2.0
ENGAGEMENT_LENGTH = 2.0
CHANNEL_FLOOR_HEIGHT = 6.0
OUTER_RAMP_START_HEIGHT = 4.0
TOP_INITIAL_RIB_HEIGHT = 5.0

CHANNEL_WIDTH = WALL_THICKNESS + TONGUE_GROWTH_BEYOND_WALL
TONGUE_OUTER_FACE_OUTWARD = CHANNEL_WIDTH

DEFLECTION_PER_PIECE_VARIANTS = [0.5, 0.4, 0.3]

OUTPUT_DIR = Path(__file__).resolve().parent

WALLS = {
    "+y": (INNER_FACE_OFFSET, +1, "YZ"),
    "-y": (-INNER_FACE_OFFSET, -1, "YZ"),
    "+x": (INNER_FACE_OFFSET, +1, "XZ"),
    "-x": (-INNER_FACE_OFFSET, -1, "XZ"),
}


def interlocking_section_width(deflection_per_piece):
    return CHANNEL_WIDTH / 2 + deflection_per_piece


def zigzag_ramp_height_at_45_degrees(deflection_per_piece):
    return interlocking_section_width(deflection_per_piece) - FLEXING_SECTION_WIDTH


def bottom_tongue_profile(deflection_per_piece):
    interlock_width = interlocking_section_width(deflection_per_piece)
    ramp_height = zigzag_ramp_height_at_45_degrees(deflection_per_piece)

    tongue_face_at_interlock = CHANNEL_WIDTH - interlock_width
    tongue_face_at_flex = CHANNEL_WIDTH - FLEXING_SECTION_WIDTH

    floor = CHANNEL_FLOOR_HEIGHT
    first_narrow_start = floor + ramp_height
    first_narrow_end = first_narrow_start + ENGAGEMENT_LENGTH
    first_bulge_start = first_narrow_end + ramp_height
    first_bulge_end = first_bulge_start + ENGAGEMENT_LENGTH
    tongue_tip = first_bulge_end + ramp_height

    return [
        (0, 0),
        (0, floor),
        (tongue_face_at_interlock, floor),
        (tongue_face_at_flex, first_narrow_start),
        (tongue_face_at_flex, first_narrow_end),
        (tongue_face_at_interlock, first_bulge_start),
        (tongue_face_at_interlock, first_bulge_end),
        (tongue_face_at_flex, tongue_tip),
        (TONGUE_OUTER_FACE_OUTWARD, tongue_tip),
        (TONGUE_OUTER_FACE_OUTWARD, floor),
        (WALL_THICKNESS, OUTER_RAMP_START_HEIGHT),
        (WALL_THICKNESS, 0),
    ]


def top_groove_profile(deflection_per_piece):
    interlock_width = interlocking_section_width(deflection_per_piece)
    ramp_height = zigzag_ramp_height_at_45_degrees(deflection_per_piece)

    wall_face_at_interlock = interlock_width
    wall_face_at_flex = FLEXING_SECTION_WIDTH

    initial_rib_top = TOP_INITIAL_RIB_HEIGHT
    first_groove_start = initial_rib_top + ramp_height
    first_groove_end = first_groove_start + ENGAGEMENT_LENGTH
    second_rib_start = first_groove_end + ramp_height
    second_rib_end = second_rib_start + ENGAGEMENT_LENGTH
    total_height = second_rib_end + ramp_height

    return [
        (0, 0),
        (0, total_height),
        (wall_face_at_flex, total_height),
        (wall_face_at_interlock, second_rib_end),
        (wall_face_at_interlock, second_rib_start),
        (wall_face_at_flex, first_groove_end),
        (wall_face_at_flex, first_groove_start),
        (wall_face_at_interlock, initial_rib_top),
        (wall_face_at_interlock, 0),
    ]


def make_box_shell():
    total_height = BASE_PLATE_THICKNESS + PLAIN_WALL_HEIGHT
    inner_dimension = FOOTPRINT - 2 * WALL_THICKNESS
    inner_corner_radius = max(CORNER_RADIUS - WALL_THICKNESS, 0.01)

    outer_block = (
        cq.Workplane("XY")
        .sketch()
        .rect(FOOTPRINT, FOOTPRINT)
        .vertices()
        .fillet(CORNER_RADIUS)
        .finalize()
        .extrude(total_height)
    )
    inner_cavity = (
        cq.Workplane("XY")
        .workplane(offset=BASE_PLATE_THICKNESS)
        .sketch()
        .rect(inner_dimension, inner_dimension)
        .vertices()
        .fillet(inner_corner_radius)
        .finalize()
        .extrude(PLAIN_WALL_HEIGHT + OVERCUT)
    )
    return outer_block.cut(inner_cavity)


def cut_plain_wall_at_snap_zone(solid, wall_id):
    inner_face_pos, outward_sign, plane = WALLS[wall_id]
    outer_face_pos = inner_face_pos + outward_sign * WALL_THICKNESS
    cut_lo = min(inner_face_pos, outer_face_pos) - OVERCUT
    cut_hi = max(inner_face_pos, outer_face_pos) + OVERCUT
    cut_center = (cut_lo + cut_hi) / 2
    cut_span = cut_hi - cut_lo

    if plane == "YZ":
        cutter = (
            cq.Workplane("XY")
            .workplane(offset=BASE_PLATE_THICKNESS - OVERCUT)
            .center(0, cut_center)
            .rect(SNAP_ZONE_WIDTH, cut_span)
            .extrude(PLAIN_WALL_HEIGHT + 2 * OVERCUT)
        )
    else:
        cutter = (
            cq.Workplane("XY")
            .workplane(offset=BASE_PLATE_THICKNESS - OVERCUT)
            .center(cut_center, 0)
            .rect(cut_span, SNAP_ZONE_WIDTH)
            .extrude(PLAIN_WALL_HEIGHT + 2 * OVERCUT)
        )
    return solid.cut(cutter)


def union_snap_cross_section(solid, wall_id, profile):
    inner_face_pos, outward_sign, plane = WALLS[wall_id]
    half_zone = SNAP_ZONE_WIDTH / 2

    world_points = [
        (inner_face_pos + outward_sign * outward, BASE_PLATE_THICKNESS + height)
        for outward, height in profile
    ]

    feature = (
        cq.Workplane(plane)
        .workplane(offset=-half_zone)
        .polyline(world_points)
        .close()
        .extrude(SNAP_ZONE_WIDTH)
    )
    return solid.union(feature)


def build_part_with_snap_profile(profile):
    solid = make_box_shell()
    for wall_id in WALLS:
        solid = cut_plain_wall_at_snap_zone(solid, wall_id)
        solid = union_snap_cross_section(solid, wall_id, profile)
    return solid


for deflection in DEFLECTION_PER_PIECE_VARIANTS:
    bottom_profile = bottom_tongue_profile(deflection)
    top_profile = top_groove_profile(deflection)

    bottom = build_part_with_snap_profile(bottom_profile)
    top = build_part_with_snap_profile(top_profile)

    tag = f"{deflection:.1f}mm-deflection"
    cq.exporters.export(bottom, str(OUTPUT_DIR / f"case-snaps-bottom-{tag}.step"))
    cq.exporters.export(top, str(OUTPUT_DIR / f"case-snaps-top-{tag}.step"))
    print(f"Exported -> bottom + top @ {deflection} mm deflection per piece")
