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

DEFLECTION_PER_PIECE = 0.3

OUTPUT_DIR = Path(__file__).resolve().parent

# ── Coordinate system ──
# XZ workplane.  CadQuery XZ normal = -Y, so:
#   workplane(offset=-d) positions at world Y = +d
#   extrude(-d)          extends d further in +Y
# Y = 0 is the top surface; +Y is deeper into the part.

# Each wall: (inner_face_position, outward_sign, perpendicular_axis)
#   "z" → wall face perpendicular to Z, runs along X, profile in YZ plane
#   "x" → wall face perpendicular to X, runs along Z, profile in XY plane
WALLS = {
    "+z": (INNER_FACE_OFFSET, +1, "z"),
    "-z": (-INNER_FACE_OFFSET, -1, "z"),
    "+x": (INNER_FACE_OFFSET, +1, "x"),
    "-x": (-INNER_FACE_OFFSET, -1, "x"),
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
    total_depth = BASE_PLATE_THICKNESS + PLAIN_WALL_HEIGHT
    inner_dimension = FOOTPRINT - 2 * WALL_THICKNESS
    inner_corner_radius = max(CORNER_RADIUS - WALL_THICKNESS, 0.01)
    outer_block = (
        cq.Workplane("XZ")
        .sketch()
        .rect(FOOTPRINT, FOOTPRINT)
        .vertices()
        .fillet(CORNER_RADIUS)
        .finalize()
        .extrude(-total_depth)
    )
    inner_cavity = (
        cq.Workplane("XZ")
        .workplane(offset=-BASE_PLATE_THICKNESS)
        .sketch()
        .rect(inner_dimension, inner_dimension)
        .vertices()
        .fillet(inner_corner_radius)
        .finalize()
        .extrude(-(PLAIN_WALL_HEIGHT + OVERCUT))
    )
    return outer_block.cut(inner_cavity)


def max_profile_height(profile):
    return max(h for _, h in profile)


def cut_plain_wall_at_snap_zone(solid, wall_id, profile_y_start, cut_height):
    inner_face_pos, outward_sign, perp_axis = WALLS[wall_id]
    outer_face_pos = inner_face_pos + outward_sign * WALL_THICKNESS
    cut_lo = min(inner_face_pos, outer_face_pos) - OVERCUT
    cut_hi = max(inner_face_pos, outer_face_pos) + OVERCUT
    cut_center_on_perp = (cut_lo + cut_hi) / 2
    cut_span_on_perp = cut_hi - cut_lo

    if perp_axis == "z":
        cutter = (
            cq.Workplane("XZ")
            .workplane(offset=-(profile_y_start - OVERCUT))
            .center(0, cut_center_on_perp)
            .rect(SNAP_ZONE_WIDTH, cut_span_on_perp)
            .extrude(-(cut_height + 2 * OVERCUT))
        )
    else:
        cutter = (
            cq.Workplane("XZ")
            .workplane(offset=-(profile_y_start - OVERCUT))
            .center(cut_center_on_perp, 0)
            .rect(cut_span_on_perp, SNAP_ZONE_WIDTH)
            .extrude(-(cut_height + 2 * OVERCUT))
        )
    return solid.cut(cutter)


def union_snap_cross_section(solid, wall_id, profile, profile_y_start):
    inner_face_pos, outward_sign, perp_axis = WALLS[wall_id]
    half_zone = SNAP_ZONE_WIDTH / 2

    world_pairs = [
        (inner_face_pos + outward_sign * outward, profile_y_start + height)
        for outward, height in profile
    ]

    if perp_axis == "z":
        yz_points = [(y, perp) for perp, y in world_pairs]
        feature = (
            cq.Workplane("YZ")
            .workplane(offset=-half_zone)
            .polyline(yz_points).close()
            .extrude(SNAP_ZONE_WIDTH)
        )
    else:
        xy_points = [(perp, y) for perp, y in world_pairs]
        feature = (
            cq.Workplane("XY")
            .workplane(offset=-half_zone)
            .polyline(xy_points).close()
            .extrude(SNAP_ZONE_WIDTH)
        )
    return solid.union(feature)


def build_part_with_snap_profile(profile):
    solid = make_box_shell()
    profile_y_start = BASE_PLATE_THICKNESS
    cut_height = max_profile_height(profile)
    for wall_id in WALLS:
        solid = cut_plain_wall_at_snap_zone(solid, wall_id, profile_y_start, cut_height)
        solid = union_snap_cross_section(solid, wall_id, profile, profile_y_start)
    return solid


bottom = build_part_with_snap_profile(bottom_tongue_profile(DEFLECTION_PER_PIECE))
top = build_part_with_snap_profile(top_groove_profile(DEFLECTION_PER_PIECE))

cq.exporters.export(bottom, str(OUTPUT_DIR / "case-snaps-bottom.step"))
cq.exporters.export(top, str(OUTPUT_DIR / "case-snaps-top.step"))
print("Exported -> case-snaps-bottom.step + case-snaps-top.step")
