"""JST crimping job tower.

Frame: world +Z is up, world +Y is the operator-facing front, and world
+X is the operator's right.  Every printed body is built in its own print
orientation with its bottom at Z=0.  Assembly translations place those
bodies in the shared tower frame.

The tower uses a 3 x 3 Gridfinity footprint at both ends: a Gridfinity bin
base docks the carcass, and a removable Gridfinity baseplate carries the
job-specific tool rack.  The spool is supported from its outer rim rather
than from an assumed hub bore.
"""

import math
import sys
from functools import lru_cache
from pathlib import Path

import cadquery as cq
from cqgridfinity import GridfinityBaseplate, GridfinityBox
from cqgridfinity.constants import GR_BASE_CLR

_here = Path(__file__).resolve()
_repo_root = next(
    p for p in _here.parents if (p / "tools" / "docgen").is_dir()
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "scripts"),
)
sys.path.insert(0, str(_repo_root / "tools"))

from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, one_body
from docgen import substitute_md


# ============================================================
# SHARED GRID AND PRINTER ENVELOPES
# ============================================================

grid_unit = 42.0
grid_units_x = 3
grid_units_y = 3
grid_nominal_x = grid_units_x * grid_unit
grid_nominal_y = grid_units_y * grid_unit
grid_bin_outer_x = grid_nominal_x - 0.5
grid_bin_outer_y = grid_nominal_y - 0.5
grid_bin_half_x = grid_bin_outer_x / 2.0

h2c_build_x = 325.0
h2c_build_y = 320.0
h2c_build_z = 320.0

grid_bin_height_u = 2
grid_height_unit = 7.0
grid_bin_top_ref_z = grid_bin_height_u * grid_height_unit
grid_baseplate_extra_depth = 6.0
grid_dock_z = grid_baseplate_extra_depth - GR_BASE_CLR


# ============================================================
# TOWER CARCASS
# ============================================================

tower_wall = 4.0
tower_inner_half_x = grid_bin_half_x - tower_wall
tower_shelf_z = 158.0
tower_wall_overlap_z = 14.0

tower_window_half_span = 45.0
tower_window_bottom_z = 58.0
tower_window_shoulder_z = 100.0
tower_window_apex_z = (
    tower_window_shoulder_z + tower_window_half_span
)

tower_pin_x = grid_bin_half_x - tower_wall / 2.0
tower_pin_y = 50.0
tower_pin_x_size = 2.8
tower_pin_y_size = 8.0
tower_pin_height = 3.2
tower_pin_socket_clearance = 0.35
tower_pin_socket_depth = tower_pin_height + 0.5

spool_shelf_z = 47.0
spool_ledge_inner_x = tower_inner_half_x - 4.5
spool_ledge_slope_bottom_z = spool_shelf_z - 4.5
spool_ledge_depth = 114.0


# ============================================================
# CONSUMABLES DRAWER
# ============================================================

drawer_width = 115.0
drawer_depth = 114.0
drawer_height = 24.0
drawer_floor = 2.4
drawer_outer_wall = 3.0
drawer_divider = 2.4
drawer_corner_radius = 3.0
drawer_pocket_radius = 1.5
drawer_z = grid_bin_top_ref_z
drawer_thumb_radius = 11.0

drawer_columns = 3
drawer_rows = 3
drawer_cell_width = (
    drawer_width
    - 2.0 * drawer_outer_wall
    - (drawer_columns - 1) * drawer_divider
) / drawer_columns
drawer_cell_depth = (
    drawer_depth
    - 2.0 * drawer_outer_wall
    - (drawer_rows - 1) * drawer_divider
) / drawer_rows
drawer_cell_pitch_x = drawer_cell_width + drawer_divider
drawer_cell_pitch_y = drawer_cell_depth + drawer_divider
drawer_egress_width = 2.0 * tower_inner_half_x
drawer_egress_depth = 6.5
drawer_egress_height = 5.0


# ============================================================
# BNTECHGO B06Y2PNW41 SPOOL ENVELOPE
# ============================================================

spool_diameter = 3.9 * 25.4
spool_radius = spool_diameter / 2.0
spool_width = 3.5 * 25.4
spool_flange_thickness_reference = 3.0
spool_flange_center_x = (
    spool_width - spool_flange_thickness_reference
) / 2.0
spool_winding_radius_reference = 43.0
spool_winding_width_reference = spool_width - 2.0 * spool_flange_thickness_reference

spool_shelf_width = 115.0
spool_shelf_depth = 114.0
spool_shelf_frame = 5.0
spool_shelf_thickness = 4.0
spool_support_x = spool_width / 2.0 - spool_flange_thickness_reference
spool_support_y = 28.0
spool_support_half_span = 4.0
spool_support_pad_width = 8.0
spool_support_rise = 5.0
spool_support_contact_z = spool_shelf_thickness + spool_support_rise
spool_center_z = spool_support_contact_z + math.sqrt(
    spool_radius**2 - spool_support_y**2
)
spool_bottom_z = spool_center_z - spool_radius
spool_top_z = spool_center_z + spool_radius

spool_axial_clearance = 2.0
spool_guide_inner_x = (spool_width + spool_axial_clearance) / 2.0
spool_guide_width = 5.0
spool_guide_depth = 8.0
spool_guide_height = 11.0


# ============================================================
# TOOL RACK AND PUBLIC TOOL ENVELOPES
# ============================================================

tool_rack_ring_bottom_z = 12.0
tool_rack_ring_top_z = 52.0
tool_rack_pocket_floor_z = 7.0
tool_rack_socket_wall = 3.0

sn2549_length = 190.0
sn2549_head_thickness = 27.9
sn2549_head_width = 65.0
sn2549_head_height = 47.0
sn2549_pocket_width = 32.5
sn2549_pocket_depth = 71.0
sn2549_socket_x = -31.0
sn2549_socket_y = -8.0

klein_11063w_length = 167.0
klein_head_thickness_reference = 25.0
klein_head_width_reference = 69.0
klein_head_height_reference = 54.0
klein_pocket_width = 32.0
klein_pocket_depth = 76.0
klein_socket_x = 31.0
klein_socket_y = -8.0

tweezer_length = 127.0
tweezer_slot_width = 10.5
tweezer_slot_depth = 5.2
tweezer_slot_floor_z = 10.0
tweezer_socket_centers_x = (-15.0, 0.0, 15.0)
tweezer_socket_y = 49.0
tweezer_block_width = 46.0
tweezer_block_depth = 13.0
tweezer_block_top_z = 45.0

flush_cutter_length_reference = 127.0
flush_cutter_pocket_width = 22.0
flush_cutter_pocket_depth = 14.0
flush_cutter_socket_x = -46.0
flush_cutter_socket_y = 49.0
flush_cutter_socket_floor_z = 9.0
flush_cutter_socket_top_z = 42.0

parts_cup_x = 45.0
parts_cup_y = 49.0
parts_cup_width = 27.0
parts_cup_depth = 23.0
parts_cup_top_z = 28.0
parts_cup_floor_z = grid_bin_top_ref_z
parts_cup_divider = 2.4
parts_cup_inner_margin = 2.5
parts_cup_inner_depth = parts_cup_depth - 2.0 * parts_cup_inner_margin
parts_cup_inner_width = (
    parts_cup_width - 2.0 * parts_cup_inner_margin - parts_cup_divider
) / 2.0


# ============================================================
# ASSEMBLY PLACEMENT AND DISPLAY COLOURS
# ============================================================

tower_base_z = grid_dock_z
top_shelf_z = tower_base_z + tower_shelf_z
tool_rack_z = top_shelf_z + grid_dock_z
drawer_presentation_y = 72.0

tool_metal_color = cq.Color(0.22, 0.23, 0.25)
tool_orange_color = cq.Color(0.92, 0.30, 0.06)
tool_blue_color = cq.Color(0.08, 0.28, 0.62)
tool_grip_color = cq.Color(0.08, 0.08, 0.09)
steel_color = cq.Color(0.58, 0.60, 0.62)
wire_color = cq.Color(0.035, 0.035, 0.04)
spool_color = cq.Color(0.82, 0.82, 0.80)


def _rounded_prism(width, depth, height, z_bottom=0.0, radius=0.0):
    """A centered XY prism with only its vertical corners rounded."""
    shape = (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(True, True, False))
        .translate((0.0, 0.0, z_bottom))
    )
    if radius > 0.0:
        shape = shape.edges("|Z").fillet(radius)
    return shape


def _translated_rounded_prism(
    width,
    depth,
    height,
    center_x,
    center_y,
    z_bottom=0.0,
    radius=0.0,
):
    return _rounded_prism(width, depth, height, z_bottom, radius).translate(
        (center_x, center_y, 0.0)
    )


@lru_cache(maxsize=1)
def build_gridfinity_bin_blank():
    """The standard 3 x 3 Gridfinity bin foot and solid two-unit body."""
    return GridfinityBox(
        grid_units_x,
        grid_units_y,
        grid_bin_height_u,
        solid=True,
        no_lip=True,
    ).render()


def build_tower_base():
    """Gridfinity-footed U carcass with shelf ledges and locating pins."""
    wall_height = tower_shelf_z - tower_wall_overlap_z
    wall_center_z = tower_wall_overlap_z + wall_height / 2.0
    side_wall = cq.Workplane("XY").box(
        tower_wall,
        grid_bin_outer_y,
        wall_height,
        centered=(True, True, True),
    )
    left_wall = side_wall.translate((-tower_pin_x, 0.0, wall_center_z))
    right_wall = side_wall.translate((tower_pin_x, 0.0, wall_center_z))
    back_wall = (
        cq.Workplane("XY")
        .box(
            grid_bin_outer_x - 2.0 * tower_wall,
            tower_wall,
            wall_height,
            centered=(True, True, True),
        )
        .translate((0.0, -tower_pin_x, wall_center_z))
    )

    left_ledge_profile = [
        (-tower_inner_half_x, spool_ledge_slope_bottom_z),
        (-tower_inner_half_x, spool_shelf_z),
        (-spool_ledge_inner_x, spool_shelf_z),
    ]
    right_ledge_profile = [
        (tower_inner_half_x, spool_ledge_slope_bottom_z),
        (tower_inner_half_x, spool_shelf_z),
        (spool_ledge_inner_x, spool_shelf_z),
    ]
    left_ledge = (
        cq.Workplane("XZ")
        .polyline(left_ledge_profile)
        .close()
        .extrude(spool_ledge_depth / 2.0, both=True)
    )
    right_ledge = (
        cq.Workplane("XZ")
        .polyline(right_ledge_profile)
        .close()
        .extrude(spool_ledge_depth / 2.0, both=True)
    )

    pin = cq.Workplane("XY").box(
        tower_pin_x_size,
        tower_pin_y_size,
        tower_pin_height,
        centered=(True, True, False),
    )
    pins = None
    for x in (-tower_pin_x, tower_pin_x):
        for y in (-tower_pin_y, tower_pin_y):
            placed = pin.translate((x, y, tower_shelf_z))
            pins = placed if pins is None else pins.union(placed)

    carcass = (
        build_gridfinity_bin_blank()
        .union(left_wall)
        .union(right_wall)
        .union(back_wall)
        .union(left_ledge)
        .union(right_ledge)
        .union(pins)
        .clean()
    )

    gable_profile = [
        (-tower_window_half_span, tower_window_bottom_z),
        (tower_window_half_span, tower_window_bottom_z),
        (tower_window_half_span, tower_window_shoulder_z),
        (0.0, tower_window_apex_z),
        (-tower_window_half_span, tower_window_shoulder_z),
    ]
    side_windows = (
        cq.Workplane("YZ")
        .polyline(gable_profile)
        .close()
        .extrude(grid_bin_outer_x / 2.0 + 1.0, both=True)
    )
    back_window = (
        cq.Workplane("XZ")
        .polyline(gable_profile)
        .close()
        .extrude(tower_wall / 2.0 + 1.0, both=True)
        .translate((0.0, -tower_pin_x, 0.0))
    )
    drawer_egress = (
        cq.Workplane("XY")
        .box(
            drawer_egress_width,
            drawer_egress_depth,
            drawer_egress_height,
            centered=(True, True, False),
        )
        .translate(
            (
                0.0,
                grid_bin_outer_y / 2.0 - drawer_egress_depth / 2.0 + 0.5,
                grid_bin_top_ref_z,
            )
        )
    )
    return (
        carcass
        .cut(side_windows)
        .cut(back_window)
        .cut(drawer_egress)
        .clean()
    )


def build_gridfinity_shelf():
    """Removable 3 x 3 Gridfinity baseplate keyed to the carcass top."""
    shelf = GridfinityBaseplate(
        grid_units_x,
        grid_units_y,
        ext_depth=grid_baseplate_extra_depth,
        straight_bottom=True,
    ).render()
    socket_width = tower_pin_x_size + 2.0 * tower_pin_socket_clearance
    socket_depth = tower_pin_y_size + 2.0 * tower_pin_socket_clearance
    socket = cq.Workplane("XY").box(
        socket_width,
        socket_depth,
        tower_pin_socket_depth + 0.1,
        centered=(True, True, False),
    ).translate((0.0, 0.0, -0.1))
    for x in (-tower_pin_x, tower_pin_x):
        for y in (-tower_pin_y, tower_pin_y):
            shelf = shelf.cut(socket.translate((x, y, 0.0)))
    return shelf.clean()


def build_consumables_drawer():
    """Nine-cell drawer for XH housings, contacts, and pre-crimp leads."""
    drawer = _rounded_prism(
        drawer_width,
        drawer_depth,
        drawer_height,
        radius=drawer_corner_radius,
    )
    for column in range(drawer_columns):
        center_x = (column - 1) * drawer_cell_pitch_x
        for row in range(drawer_rows):
            center_y = (row - 1) * drawer_cell_pitch_y
            pocket = _translated_rounded_prism(
                drawer_cell_width,
                drawer_cell_depth,
                drawer_height - drawer_floor + 0.2,
                center_x,
                center_y,
                z_bottom=drawer_floor,
                radius=drawer_pocket_radius,
            )
            drawer = drawer.cut(pocket)

    thumb_notch = (
        cq.Workplane("XZ")
        .circle(drawer_thumb_radius)
        .extrude(drawer_outer_wall + 1.0, both=True)
        .translate((0.0, drawer_depth / 2.0, drawer_height))
    )
    return drawer.cut(thumb_notch).clean()


def _spool_support_wedge(center_x, center_y):
    profile = [
        (center_y - spool_support_half_span, spool_shelf_thickness),
        (center_y, spool_support_contact_z),
        (center_y + spool_support_half_span, spool_shelf_thickness),
    ]
    return (
        cq.Workplane("YZ")
        .polyline(profile)
        .close()
        .extrude(spool_support_pad_width / 2.0, both=True)
        .translate((center_x, 0.0, 0.0))
    )


def build_spool_shelf():
    """Open frame with four outer-rim supports for the wire spool."""
    outer = _rounded_prism(
        spool_shelf_width,
        spool_shelf_depth,
        spool_shelf_thickness,
        radius=3.0,
    )
    inner = _rounded_prism(
        spool_shelf_width - 2.0 * spool_shelf_frame,
        spool_shelf_depth - 2.0 * spool_shelf_frame,
        spool_shelf_thickness + 0.2,
        z_bottom=-0.1,
        radius=2.0,
    )
    shelf = outer.cut(inner)

    front_inner_y = spool_shelf_depth / 2.0 - spool_shelf_frame
    support_arm_inner_y = spool_support_y - spool_support_half_span
    for x_sign in (-1.0, 1.0):
        support_x = x_sign * spool_support_x
        for y_sign in (-1.0, 1.0):
            support_y = y_sign * spool_support_y
            arm_center_y = y_sign * (front_inner_y + support_arm_inner_y) / 2.0
            arm_depth = front_inner_y - support_arm_inner_y
            arm = _translated_rounded_prism(
                spool_support_pad_width,
                arm_depth,
                spool_shelf_thickness,
                support_x,
                arm_center_y,
                radius=1.0,
            )
            wedge = _spool_support_wedge(support_x, support_y)
            shelf = shelf.union(arm).union(wedge)

            guide_center_x = x_sign * (
                spool_guide_inner_x + spool_guide_width / 2.0
            )
            guide = _translated_rounded_prism(
                spool_guide_width,
                spool_guide_depth,
                spool_guide_height,
                guide_center_x,
                support_y,
                radius=1.0,
            )
            shelf = shelf.union(guide)
    return shelf.clean()


def _socket_ring(
    pocket_width,
    pocket_depth,
    center_x,
    center_y,
    bottom_z,
    top_z,
    wall=tool_rack_socket_wall,
    radius=5.0,
):
    outer = _translated_rounded_prism(
        pocket_width + 2.0 * wall,
        pocket_depth + 2.0 * wall,
        top_z - bottom_z,
        center_x,
        center_y,
        z_bottom=bottom_z,
        radius=radius,
    )
    inner = _translated_rounded_prism(
        pocket_width,
        pocket_depth,
        top_z - bottom_z + 0.2,
        center_x,
        center_y,
        z_bottom=bottom_z - 0.1,
        radius=max(radius - wall, 1.0),
    )
    return outer.cut(inner)


def _tool_pocket(width, depth, center_x, center_y, floor_z, top_z, radius=3.0):
    return _translated_rounded_prism(
        width,
        depth,
        top_z - floor_z + 0.2,
        center_x,
        center_y,
        z_bottom=floor_z,
        radius=radius,
    )


def build_tool_rack():
    """Gridfinity tool rack for crimper, stripper, tweezers, and cutter."""
    rack = build_gridfinity_bin_blank()

    rack = rack.union(
        _socket_ring(
            sn2549_pocket_width,
            sn2549_pocket_depth,
            sn2549_socket_x,
            sn2549_socket_y,
            tool_rack_ring_bottom_z,
            tool_rack_ring_top_z,
        )
    )
    rack = rack.union(
        _socket_ring(
            klein_pocket_width,
            klein_pocket_depth,
            klein_socket_x,
            klein_socket_y,
            tool_rack_ring_bottom_z,
            tool_rack_ring_top_z,
        )
    )

    tweezer_block = _translated_rounded_prism(
        tweezer_block_width,
        tweezer_block_depth,
        tweezer_block_top_z - tool_rack_ring_bottom_z,
        0.0,
        tweezer_socket_y,
        z_bottom=tool_rack_ring_bottom_z,
        radius=3.0,
    )
    rack = rack.union(tweezer_block)

    cutter_ring = _socket_ring(
        flush_cutter_pocket_width,
        flush_cutter_pocket_depth,
        flush_cutter_socket_x,
        flush_cutter_socket_y,
        tool_rack_ring_bottom_z,
        flush_cutter_socket_top_z,
        radius=3.0,
    )
    rack = rack.union(cutter_ring)

    parts_cup = _translated_rounded_prism(
        parts_cup_width,
        parts_cup_depth,
        parts_cup_top_z - tool_rack_ring_bottom_z,
        parts_cup_x,
        parts_cup_y,
        z_bottom=tool_rack_ring_bottom_z,
        radius=3.0,
    )
    rack = rack.union(parts_cup)

    rack = rack.cut(
        _tool_pocket(
            sn2549_pocket_width,
            sn2549_pocket_depth,
            sn2549_socket_x,
            sn2549_socket_y,
            tool_rack_pocket_floor_z,
            tool_rack_ring_top_z + 0.2,
        )
    )
    rack = rack.cut(
        _tool_pocket(
            klein_pocket_width,
            klein_pocket_depth,
            klein_socket_x,
            klein_socket_y,
            tool_rack_pocket_floor_z,
            tool_rack_ring_top_z + 0.2,
        )
    )

    for center_x in tweezer_socket_centers_x:
        rack = rack.cut(
            _tool_pocket(
                tweezer_slot_width,
                tweezer_slot_depth,
                center_x,
                tweezer_socket_y,
                tweezer_slot_floor_z,
                tweezer_block_top_z + 0.2,
                radius=1.5,
            )
        )

    rack = rack.cut(
        _tool_pocket(
            flush_cutter_pocket_width,
            flush_cutter_pocket_depth,
            flush_cutter_socket_x,
            flush_cutter_socket_y,
            flush_cutter_socket_floor_z,
            flush_cutter_socket_top_z + 0.2,
            radius=2.0,
        )
    )

    cup_inner_center_offset = (
        parts_cup_inner_width + parts_cup_divider
    ) / 2.0
    for x_sign in (-1.0, 1.0):
        rack = rack.cut(
            _tool_pocket(
                parts_cup_inner_width,
                parts_cup_inner_depth,
                parts_cup_x + x_sign * cup_inner_center_offset,
                parts_cup_y,
                parts_cup_floor_z,
                parts_cup_top_z + 0.2,
                radius=1.5,
            )
        )
    return rack.clean()


# ============================================================
# FIT REFERENCES
# ============================================================

def _yz_prism(profile, thickness, center_x):
    plane = cq.Plane(
        origin=(center_x, 0.0, 0.0),
        xDir=(0.0, 1.0, 0.0),
        normal=(1.0, 0.0, 0.0),
    )
    return (
        cq.Workplane(plane)
        .polyline(profile)
        .close()
        .extrude(thickness / 2.0, both=True)
    )


def build_sn2549_reference():
    """Public 190 x 65 x 27.9 mm envelope as head and splayed grips."""
    bottom_z = tool_rack_pocket_floor_z + 0.5
    head = _translated_rounded_prism(
        sn2549_head_thickness,
        sn2549_head_width,
        sn2549_head_height,
        sn2549_socket_x,
        sn2549_socket_y,
        z_bottom=bottom_z,
        radius=5.0,
    )
    grip_bottom_z = bottom_z + sn2549_head_height - 12.0
    grip_top_z = bottom_z + sn2549_length
    grips = []
    for y_sign in (-1.0, 1.0):
        profile = [
            (sn2549_socket_y + y_sign * 11.0, grip_bottom_z),
            (sn2549_socket_y + y_sign * 24.0, grip_top_z),
            (sn2549_socket_y + y_sign * 37.0, grip_top_z),
            (sn2549_socket_y + y_sign * 19.0, grip_bottom_z),
        ]
        grips.append(_yz_prism(profile, 16.0, sn2549_socket_x))
    return {
        "head": head,
        "left-grip": grips[0],
        "right-grip": grips[1],
        "fit": head.union(grips[0]).union(grips[1]).clean(),
    }


def build_klein_reference():
    """Official 167 mm length with a conservative public-photo head envelope."""
    bottom_z = tool_rack_pocket_floor_z + 0.5
    head = _translated_rounded_prism(
        klein_head_thickness_reference,
        klein_head_width_reference,
        klein_head_height_reference,
        klein_socket_x,
        klein_socket_y,
        z_bottom=bottom_z,
        radius=6.0,
    )
    grip_bottom_z = bottom_z + klein_head_height_reference - 14.0
    grip_top_z = bottom_z + klein_11063w_length
    grips = []
    for y_sign in (-1.0, 1.0):
        profile = [
            (klein_socket_y + y_sign * 12.0, grip_bottom_z),
            (klein_socket_y + y_sign * 22.0, grip_top_z),
            (klein_socket_y + y_sign * 32.0, grip_top_z),
            (klein_socket_y + y_sign * 19.0, grip_bottom_z),
        ]
        grips.append(_yz_prism(profile, 15.0, klein_socket_x))
    return {
        "head": head,
        "left-grip": grips[0],
        "right-grip": grips[1],
        "fit": head.union(grips[0]).union(grips[1]).clean(),
    }


def build_tweezer_references():
    references = []
    bottom_z = tweezer_slot_floor_z + 0.5
    for center_x in tweezer_socket_centers_x:
        reference = _translated_rounded_prism(
            8.0,
            3.0,
            tweezer_length,
            center_x,
            tweezer_socket_y,
            z_bottom=bottom_z,
            radius=1.0,
        )
        references.append(reference)
    return references


def build_flush_cutter_reference():
    bottom_z = flush_cutter_socket_floor_z + 0.5
    head = _translated_rounded_prism(
        17.0,
        10.0,
        flush_cutter_socket_top_z - bottom_z + 0.5,
        flush_cutter_socket_x,
        flush_cutter_socket_y,
        z_bottom=bottom_z,
        radius=2.0,
    )
    grip_bottom_z = flush_cutter_socket_top_z + 0.5
    grip_top_z = bottom_z + flush_cutter_length_reference
    grips = []
    for x_sign in (-1.0, 1.0):
        center_x = flush_cutter_socket_x + x_sign * 9.0
        grip = _translated_rounded_prism(
            9.0,
            8.0,
            grip_top_z - grip_bottom_z,
            center_x,
            flush_cutter_socket_y,
            z_bottom=grip_bottom_z,
            radius=3.0,
        )
        grips.append(grip)
    return {
        "head": head,
        "left-grip": grips[0],
        "right-grip": grips[1],
        "fit": head.union(grips[0]).union(grips[1]).clean(),
    }


def build_spool_reference():
    flange = (
        cq.Workplane("XY")
        .circle(spool_radius)
        .extrude(spool_flange_thickness_reference)
        .translate((0.0, 0.0, -spool_flange_thickness_reference / 2.0))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    )
    right_flange = flange.translate((spool_flange_center_x, 0.0, spool_center_z))
    left_flange = flange.translate((-spool_flange_center_x, 0.0, spool_center_z))
    winding = (
        cq.Workplane("XY")
        .circle(spool_winding_radius_reference)
        .extrude(spool_winding_width_reference)
        .translate((0.0, 0.0, -spool_winding_width_reference / 2.0))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
        .translate((0.0, 0.0, spool_center_z))
    )
    envelope = (
        cq.Workplane("XY")
        .circle(spool_radius)
        .extrude(spool_width)
        .translate((0.0, 0.0, -spool_width / 2.0))
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
        .translate((0.0, 0.0, spool_center_z))
    )
    return {
        "right-flange": right_flange,
        "left-flange": left_flange,
        "winding": winding,
        "fit": envelope,
    }


# ============================================================
# VALIDATION AND EXPORT
# ============================================================

def _bbox(shape):
    return shape.val().BoundingBox()


def _assert_one_solid(name, shape):
    count = len(shape.solids().vals())
    if count != 1:
        raise ValueError(f"{name}: expected one solid, found {count}")


def _assert_h2c_fit(name, shape):
    bounds = _bbox(shape)
    size = (bounds.xlen, bounds.ylen, bounds.zlen)
    limits = (h2c_build_x, h2c_build_y, h2c_build_z)
    if any(part > limit + 1e-6 for part, limit in zip(size, limits)):
        raise ValueError(f"{name}: {size} exceeds H2C left-nozzle envelope {limits}")
    print(f"   {name}: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")


def _intersection_volume(a, b):
    return a.intersect(b).val().Volume()


def _assert_docked(name, lower, upper, upper_z):
    placed = upper.translate((0.0, 0.0, upper_z))
    overlap = _intersection_volume(lower, placed)
    gap = lower.val().distance(placed.val())
    if overlap > 0.05:
        raise ValueError(f"{name}: {overlap:.3f} mm^3 interface overlap")
    if gap > 0.02:
        raise ValueError(f"{name}: {gap:.3f} mm interface gap")
    print(f"   {name}: {overlap:.4f} mm^3 overlap, {gap:.4f} mm gap")


def validate(parts, references):
    print("Fit checks")
    for name, shape in parts.items():
        _assert_one_solid(name, shape)
        _assert_h2c_fit(name, shape)

    _assert_docked(
        "bench dock to tower",
        parts["gridfinity-shelf"],
        parts["tower-base"],
        grid_dock_z,
    )
    _assert_docked(
        "tower pins to top shelf",
        parts["tower-base"],
        parts["gridfinity-shelf"],
        tower_shelf_z,
    )
    _assert_docked(
        "tower deck to drawer",
        parts["tower-base"],
        parts["consumables-drawer"],
        drawer_z,
    )
    _assert_docked(
        "tower ledges to spool shelf",
        parts["tower-base"],
        parts["spool-shelf"],
        spool_shelf_z,
    )
    _assert_docked(
        "top shelf to tool rack",
        parts["gridfinity-shelf"],
        parts["tool-rack"],
        grid_dock_z,
    )

    rack = parts["tool-rack"]
    rack_clearances = {
        "SN-2549": references["sn2549"]["fit"],
        "Klein 11063W": references["klein"]["fit"],
        "flush cutter": references["flush-cutter"]["fit"],
    }
    for index, tweezer in enumerate(references["tweezers"], 1):
        rack_clearances[f"tweezer {index}"] = tweezer
    for name, reference in rack_clearances.items():
        overlap = _intersection_volume(rack, reference)
        if overlap > 0.02:
            raise ValueError(f"{name}: {overlap:.3f} mm^3 intersects tool rack")
        print(f"   {name}: {overlap:.4f} mm^3 rack overlap")

    drawer_path_overlaps = []
    for y in (0.0, 24.0, 48.0, drawer_presentation_y, 96.0):
        placed = parts["consumables-drawer"].translate((0.0, y, drawer_z))
        drawer_path_overlaps.append(_intersection_volume(parts["tower-base"], placed))
    drawer_path_overlap = max(drawer_path_overlaps)
    if drawer_path_overlap > 0.05:
        raise ValueError(
            f"drawer travel: {drawer_path_overlap:.3f} mm^3 intersects tower"
        )
    print(f"   drawer travel: {drawer_path_overlap:.4f} mm^3 maximum overlap")

    shelf_overlap = _intersection_volume(
        parts["spool-shelf"], references["spool"]["fit"]
    )
    if shelf_overlap > 0.05:
        raise ValueError(
            f"spool envelope: {shelf_overlap:.3f} mm^3 intersects spool shelf"
        )
    print(f"   spool envelope: {shelf_overlap:.4f} mm^3 shelf overlap")

    spool_global_top = spool_shelf_z + spool_top_z
    spool_global_bottom = spool_shelf_z + spool_bottom_z
    drawer_global_top = drawer_z + drawer_height
    if spool_global_bottom <= drawer_global_top:
        raise ValueError("spool envelope reaches the consumables drawer")
    if spool_global_top >= tower_shelf_z:
        raise ValueError("spool envelope reaches the removable Gridfinity shelf")
    print(
        "   spool clearances: "
        f"{spool_global_bottom - drawer_global_top:.1f} mm over drawer, "
        f"{tower_shelf_z - spool_global_top:.1f} mm under top shelf"
    )


def build_presentation_assembly(parts, references):
    assembly = cq.Assembly(name="jst-crimping-job-tower")
    assembly.add(
        parts["gridfinity-shelf"],
        name="optional-bench-dock",
        color=M_PETGF_BLACK,
    )
    assembly.add(
        parts["tower-base"],
        name="tower-base",
        loc=cq.Location(cq.Vector(0.0, 0.0, tower_base_z)),
        color=M_PETGF_BLACK,
    )
    assembly.add(
        parts["consumables-drawer"],
        name="consumables-drawer-open",
        loc=cq.Location(
            cq.Vector(0.0, drawer_presentation_y, tower_base_z + drawer_z)
        ),
        color=M_PETGF_BLACK,
    )
    assembly.add(
        parts["spool-shelf"],
        name="outer-rim-spool-shelf",
        loc=cq.Location(cq.Vector(0.0, 0.0, tower_base_z + spool_shelf_z)),
        color=M_PETGF_BLACK,
    )

    spool_location = cq.Location(
        cq.Vector(0.0, 0.0, tower_base_z + spool_shelf_z)
    )
    assembly.add(
        references["spool"]["right-flange"],
        name="spool-right-flange-reference",
        loc=spool_location,
        color=spool_color,
    )
    assembly.add(
        references["spool"]["left-flange"],
        name="spool-left-flange-reference",
        loc=spool_location,
        color=spool_color,
    )
    assembly.add(
        references["spool"]["winding"],
        name="22awg-wire-reference",
        loc=spool_location,
        color=wire_color,
    )

    assembly.add(
        parts["gridfinity-shelf"],
        name="removable-top-shelf",
        loc=cq.Location(cq.Vector(0.0, 0.0, top_shelf_z)),
        color=M_PETGF_BLACK,
    )
    assembly.add(
        parts["tool-rack"],
        name="jst-tool-rack",
        loc=cq.Location(cq.Vector(0.0, 0.0, tool_rack_z)),
        color=M_PETGF_BLACK,
    )

    rack_location = cq.Location(cq.Vector(0.0, 0.0, tool_rack_z))
    for name, shape in references["sn2549"].items():
        if name == "fit":
            continue
        assembly.add(
            shape,
            name=f"sn2549-{name}-reference",
            loc=rack_location,
            color=tool_metal_color if name == "head" else tool_orange_color,
        )
    for name, shape in references["klein"].items():
        if name == "fit":
            continue
        assembly.add(
            shape,
            name=f"klein-{name}-reference",
            loc=rack_location,
            color=tool_grip_color if name == "head" else tool_blue_color,
        )
    for index, shape in enumerate(references["tweezers"], 1):
        assembly.add(
            shape,
            name=f"tweezer-{index}-reference",
            loc=rack_location,
            color=tool_grip_color,
        )
    for name, shape in references["flush-cutter"].items():
        if name == "fit":
            continue
        assembly.add(
            shape,
            name=f"flush-cutter-{name}-reference",
            loc=rack_location,
            color=steel_color if name == "head" else tool_blue_color,
        )
    return assembly


def main():
    out_dir = Path(__file__).resolve().parent
    parts = {
        "tower-base": build_tower_base(),
        "consumables-drawer": build_consumables_drawer(),
        "spool-shelf": build_spool_shelf(),
        "gridfinity-shelf": build_gridfinity_shelf(),
        "tool-rack": build_tool_rack(),
    }
    references = {
        "sn2549": build_sn2549_reference(),
        "klein": build_klein_reference(),
        "tweezers": build_tweezer_references(),
        "flush-cutter": build_flush_cutter_reference(),
        "spool": build_spool_reference(),
    }
    validate(parts, references)

    for name, shape in parts.items():
        out = out_dir / f"{name}.step"
        export_assembly(one_body(shape, name, M_PETGF_BLACK), str(out))
        print(f"-> {out.name}")

    assembly_out = out_dir / "jst-crimping-tower.step"
    export_assembly(build_presentation_assembly(parts, references), str(assembly_out))
    print(f"-> {assembly_out.name}")

    populated_height = tool_rack_z + tool_rack_pocket_floor_z + 0.5 + sn2549_length
    printed_tower_height = tool_rack_z + tool_rack_ring_top_z
    variables = {
        "FOOTPRINT": f"{grid_nominal_x:.0f} mm x {grid_nominal_y:.0f} mm",
        "PRINTED_TOWER_HEIGHT": f"{printed_tower_height:.1f} mm",
        "POPULATED_HEIGHT": f"{populated_height:.1f} mm",
        "TALLEST_PART": f"{_bbox(parts['tower-base']).zlen:.1f} mm",
        "SPOOL_ENVELOPE": f"diameter {spool_diameter:.1f} mm x {spool_width:.1f} mm",
        "DRAWER_CELL": f"{drawer_cell_width:.1f} mm x {drawer_cell_depth:.1f} mm",
        "SPOOL_DRAWER_CLEAR": (
            f"{spool_shelf_z + spool_bottom_z - (drawer_z + drawer_height):.1f} mm"
        ),
        "SPOOL_TOP_CLEAR": f"{tower_shelf_z - (spool_shelf_z + spool_top_z):.1f} mm",
        "H2C_ENVELOPE": f"{h2c_build_x:.0f} x {h2c_build_y:.0f} x {h2c_build_z:.0f} mm",
    }
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
