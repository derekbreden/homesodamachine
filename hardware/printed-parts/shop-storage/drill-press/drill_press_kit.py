"""Drill-press job kit.

Frame: world +Z is up, world +Y is the operator-facing front, and world +X is the
operator's right.  Every storey is a stock cq-gridfinity body built with its bottom at
Z=0; `_kit.stack_seats` places it in the kit frame.

The kit is the bench job at the WEN 4208T: chamfer the port holes, tap 1/4"-18 NPT,
drill the rod register.  The top storey is a job rack whose sockets read left to right
in that order — countersinks, taps and their guide, then the register drills — and the
storey under it is an open bin for the hole-saw set.

Every stored thing is an envelope taken from a public dimension.  A dimension the maker
and the listing both leave unstated is a named `_generous` envelope, larger than the
tool can be.
"""

import sys
from math import pi, radians, tan
from pathlib import Path

import cadquery as cq
from cqgridfinity.constants import GR_TOPSIDE_H

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import _kit  # noqa: E402
from _kit import substitute_md  # noqa: E402


# ============================================================
# THE KIT'S FOOTPRINT AND ITS STOREYS
# ============================================================

kit_units_x = 3
kit_units_y = 3
kit_nominal_footprint = kit_units_x * _kit.grid_unit

saw_storey_u = 6
rack_storey_u = 6

storey_floor_z = _kit.bin_floor_z
saw_cavity_depth = _kit.cavity_depth(saw_storey_u)

saw_inner_x = _kit.inner_size(kit_units_x)
saw_inner_y = _kit.inner_size(kit_units_y)
saw_cell_depth = _kit.cell_span(kit_units_y, 1)
saw_cell_center_y = _kit.cell_centers(kit_units_y, 1)[1]

rack_plateau_half = _kit.plateau_half(kit_units_x)
rack_plateau_span = 2.0 * rack_plateau_half
rack_top_z = _kit.top_reference_z(rack_storey_u)

#: Every rack socket is this much wider than the envelope it holds, on every side.
rack_socket_clearance = 2.0
#: The plastic left between one socket and the next, and between a socket and the
#: plateau's edge.
rack_socket_wall = 3.0
rack_socket_floor_z = 10.0
rack_socket_depth = rack_top_z - rack_socket_floor_z
rack_pocket_radius = 3.0

#: A tool's envelope rides this far off its socket floor, so a fit check reads the
#: socket walls rather than the floor it stands on.
tool_stand_off_z = 0.5
tool_bottom_z = rack_socket_floor_z + tool_stand_off_z


def socket_size(envelope_size):
    return envelope_size + 2.0 * rack_socket_clearance


def stacked_centers(sizes, gap=rack_socket_wall, center=0.0):
    """Centers of `sizes` laid end to end with `gap` between, the run centered."""
    run = sum(sizes) + gap * (len(sizes) - 1)
    edge = center - run / 2.0
    centers = []
    for size in sizes:
        centers.append(edge + size / 2.0)
        edge += size + gap
    return centers


# ============================================================
# PUBLIC ENVELOPES — WHAT THE KIT HOLDS
# ============================================================

inch = 25.4

# LingGan M35 (B0D7HM5R3C), Drill America DWT64006 (B01DZD1Y9Y) and the tap in the
# Drill America tap-and-die kit (B0DXN1LDKT) are one ANSI 1/4"-18 NPT taper pipe tap.
tap_length = 2.44 * inch
tap_shank_diameter = 0.5625 * inch
tap_square_across_flats = 0.421 * inch
tap_square_across_corners = tap_square_across_flats * 2.0**0.5
tap_thread_length = 1.06 * inch
tap_thread_major_diameter = 0.5348 * inch
tap_square_length = 0.25 * inch
tap_envelope_diameter = max(tap_shank_diameter, tap_square_across_corners)
tap_socket_diameter = socket_size(tap_envelope_diameter)
tap_count = 3

# The kit's 1-1/2" OD round adjustable NPT die (B0DXN1LDKT). Its thickness is nowhere
# public; the MOTOKU handle the ledger pairs it with states a 38 x 14 mm die capacity.
die_diameter = 1.5 * inch
die_thickness_generous = 18.0
die_bore_diameter = 0.75 * inch
die_pocket_diameter = socket_size(die_diameter)
die_pocket_depth = 12.0
die_pocket_floor_z = rack_top_z - die_pocket_depth

# JNB Pro 82 degree countersinks (B09C4X5R8F), five bodies on one 1/4" shank. The
# listing gives the head sizes and the shank; the bodies' length is nowhere public.
countersink_head_diameters = (0.25 * inch, 0.375 * inch, 0.5 * inch, 0.625 * inch, 0.75 * inch)
countersink_shank_diameter = 0.25 * inch
countersink_length_generous = 70.0
countersink_included_angle = 82.0
countersink_socket_diameters = tuple(
    socket_size(diameter) for diameter in countersink_head_diameters
)

# Drill Hulk 9/64" M35 cobalt jobber drills, a 12-pack (B07XNNNC5Y).
drill_diameter = 9.0 / 64.0 * inch
drill_length = 2.875 * inch
drill_flute_length = 1.75 * inch
drill_count = 12
drill_socket_diameter = socket_size(drill_diameter)

# Bosch DSB1013 Daredevil spade bit (B001NGPAA0), 1" x 6" on a 1/4" hex shank.
spade_cut_diameter = 1.0 * inch
spade_length = 6.0 * inch
spade_paddle_length = 3.0 * inch
spade_paddle_thickness_generous = 2.5
spade_shank_across_flats = 0.25 * inch
spade_shank_across_corners = spade_shank_across_flats * 2.0 / 3.0**0.5
spade_slot_width = socket_size(spade_cut_diameter)
spade_slot_depth = spade_paddle_thickness_generous + 2.0 * rack_socket_wall

# Brown & Sharpe 599-792-30 spring tap guide (B005317ZMC): a 1/2" case-hardened body.
# Its overall length is nowhere public.
guide_body_diameter = 0.5 * inch
guide_length_generous = 115.0
guide_point_diameter = 8.0
guide_point_length = 12.0
guide_socket_diameter = socket_size(guide_body_diameter)

# Noga NG8150 (B001O62V56): the NogaGrip-1 handle, 125 mm x 28 mm, blade down. What
# the S10 blade holder adds past the handle is nowhere public.
noga_handle_length = 125.0
noga_handle_diameter = 28.0
noga_blade_length_generous = 30.0
noga_blade_diameter = 10.0
#: The rubber band up the handle's top end, in the listing photograph.
noga_grip_length = 40.0
noga_length = noga_handle_length + noga_blade_length_generous
noga_well_diameter = socket_size(noga_handle_diameter)

# Mollom hole-saw set (B0BZQ4J5B1): a 124 mm bi-metal saw, its arbor and two pilot
# drills. The listing gives the cut, the cut depth and the 11 mm arbor shank; the
# arbor's flange and length, and the pilot drills, are nowhere public.
hole_saw_cut_diameter = 4.875 * inch
hole_saw_cut_depth = 38.0
arbor_shank_across_flats = 11.0
arbor_shank_across_corners = arbor_shank_across_flats * 2.0 / 3.0**0.5
arbor_shank_length_generous = 45.0
arbor_flange_diameter_generous = 30.0
arbor_flange_length_generous = 25.0
arbor_pilot_diameter = 0.25 * inch
arbor_pilot_stickout_generous = 45.0
arbor_length = (
    arbor_shank_length_generous + arbor_flange_length_generous + arbor_pilot_stickout_generous
)
pilot_drill_diameter_generous = 6.5
pilot_drill_length_generous = 95.0
pilot_drill_count = 2

# Left at the press or on the shelf, and sized here so the README can say why.
tap_magic_bottle_diameter = 2.75 * inch
tap_magic_bottle_height = 8.0 * inch
tap_magic_well_diameter = socket_size(tap_magic_bottle_diameter)
tap_wrench_length = 19.0 * inch
die_handle_length = 315.0


# ============================================================
# RACK LAYOUT — LEFT TO RIGHT IS PV-01, PV-02, PV-03
# ============================================================

countersink_column_x = -45.5
countersink_socket_centers_y = stacked_centers(countersink_socket_diameters)
widest_countersink_socket = max(countersink_socket_diameters)

tap_row_y = 47.0
tap_row_x_start = (
    countersink_column_x + widest_countersink_socket / 2.0 + rack_socket_wall
)
tap_socket_centers_x = [
    tap_row_x_start + tap_socket_diameter / 2.0 + index * (tap_socket_diameter + rack_socket_wall)
    for index in range(tap_count)
]
guide_socket_x = (
    tap_socket_centers_x[-1]
    + tap_socket_diameter / 2.0
    + rack_socket_wall
    + guide_socket_diameter / 2.0
)
guide_socket_y = tap_row_y

die_pocket_x = -4.0
die_pocket_y = -10.0

spade_slot_x = die_pocket_x
spade_slot_y = -45.0

noga_well_x = 41.0
noga_well_y = -41.0

drill_index_x = 42.0
drill_index_y = -1.0
drill_index_columns = 3
drill_index_rows = drill_count // drill_index_columns
drill_index_pitch = drill_socket_diameter + rack_socket_wall
drill_socket_centers = [
    (center_x, center_y)
    for center_x in _kit.centered_run(drill_index_columns, drill_index_pitch, drill_index_x)
    for center_y in _kit.centered_run(drill_index_rows, drill_index_pitch, drill_index_y)
]


def _round_socket_footprints():
    """(name, center_x, center_y, diameter, floor_z) for every round socket in the rack."""
    footprints = [
        ("die pocket", die_pocket_x, die_pocket_y, die_pocket_diameter, die_pocket_floor_z),
        (
            "tap guide socket",
            guide_socket_x,
            guide_socket_y,
            guide_socket_diameter,
            rack_socket_floor_z,
        ),
        (
            "deburr-tool well",
            noga_well_x,
            noga_well_y,
            noga_well_diameter,
            rack_socket_floor_z,
        ),
    ]
    for index, (diameter, center_y) in enumerate(
        zip(countersink_socket_diameters, countersink_socket_centers_y), 1
    ):
        footprints.append(
            (f"countersink socket {index}", countersink_column_x, center_y, diameter,
             rack_socket_floor_z)
        )
    for index, center_x in enumerate(tap_socket_centers_x, 1):
        footprints.append(
            (f"tap socket {index}", center_x, tap_row_y, tap_socket_diameter, rack_socket_floor_z)
        )
    for index, (center_x, center_y) in enumerate(drill_socket_centers, 1):
        footprints.append(
            (f"drill socket {index}", center_x, center_y, drill_socket_diameter,
             rack_socket_floor_z)
        )
    return footprints


def _rectangular_socket_footprints():
    """(name, center_x, center_y, width, depth, floor_z) for every rectangular socket."""
    return [
        (
            "spade-bit slot",
            spade_slot_x,
            spade_slot_y,
            spade_slot_width,
            spade_slot_depth,
            rack_socket_floor_z,
        )
    ]


# ============================================================
# BIN LAYOUT — THE HOLE-SAW SET
# ============================================================

arbor_axis_y = -saw_cell_center_y
arbor_axis_z = storey_floor_z + arbor_flange_diameter_generous / 2.0

pilot_drill_spacing = 12.0
pilot_drill_axis_y = tuple(
    _kit.centered_run(pilot_drill_count, pilot_drill_spacing, saw_cell_center_y)
)
pilot_drill_axis_z = storey_floor_z + pilot_drill_diameter_generous / 2.0


# ============================================================
# STOREY BODIES
# ============================================================

def build_dock():
    return _kit.dock_body(kit_units_x, kit_units_y)


def build_saw_storey():
    """Open bin, one divider: the hole-saw arbor aft, its pilot drills forward."""
    return _kit.bin_body(
        kit_units_x,
        kit_units_y,
        saw_storey_u,
        labels=True,
        scoops=True,
        width_div=1,
    )


def build_index_storey():
    """The job rack: a lipped blank with the tap-and-bit index cut from its plateau."""
    rack = _kit.blank_body(kit_units_x, kit_units_y, rack_storey_u)

    for _, center_x, center_y, diameter, floor_z in _round_socket_footprints():
        rack = rack.cut(
            _kit.round_pocket(diameter, center_x, center_y, floor_z, rack_top_z)
        )
    for _, center_x, center_y, width, depth, floor_z in _rectangular_socket_footprints():
        rack = rack.cut(
            _kit.pocket(
                width,
                depth,
                center_x,
                center_y,
                floor_z,
                rack_top_z,
                radius=min(rack_pocket_radius, depth / 2.0 - 0.5),
            )
        )
    return rack.clean()


# ============================================================
# CONTENT REFERENCES
# ============================================================

tool_steel_color = cq.Color(0.60, 0.62, 0.65)
tap_tin_color = cq.Color(0.82, 0.66, 0.22)
tool_black_color = cq.Color(0.11, 0.11, 0.12)
bosch_blue_color = cq.Color(0.05, 0.30, 0.58)
noga_grip_color = cq.Color(0.22, 0.64, 0.86)
noga_body_color = cq.Color(0.87, 0.85, 0.79)


def _square_prism(across_flats, height, center_x, center_y, z_bottom):
    return (
        cq.Workplane("XY")
        .rect(across_flats, across_flats)
        .extrude(height)
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 45.0)
        .translate((center_x, center_y, z_bottom))
    )


def build_tap_reference(center_x, center_y, steel_color):
    """A 1/4"-18 NPT taper tap standing shank down, its taper threads up."""
    shank_length = tap_length - tap_thread_length - tap_square_length
    square = _square_prism(
        tap_square_across_flats, tap_square_length, center_x, center_y, tool_bottom_z
    )
    shank = _kit.cylinder(
        tap_shank_diameter, shank_length, center_x, center_y, tool_bottom_z + tap_square_length
    )
    threads = _kit.cone(
        tap_thread_major_diameter,
        tap_thread_major_diameter * 0.72,
        tap_thread_length,
        center_x,
        center_y,
        tool_bottom_z + tap_square_length + shank_length,
    )
    return {
        "square": (square, steel_color),
        "shank": (shank, steel_color),
        "threads": (threads, steel_color),
        "fit": _kit.cylinder(tap_envelope_diameter, tap_length, center_x, center_y, tool_bottom_z),
    }


def build_countersink_reference(head_diameter, center_x, center_y):
    """One 82 degree countersink standing head down, its 1/4" shank up."""
    cone_height = (head_diameter / 2.0) / tan(radians(countersink_included_angle / 2.0))
    body_length = 8.0
    tip = _kit.cone(1.0, head_diameter, cone_height, center_x, center_y, tool_bottom_z)
    body = _kit.cylinder(
        head_diameter, body_length, center_x, center_y, tool_bottom_z + cone_height
    )
    shank = _kit.cylinder(
        countersink_shank_diameter,
        countersink_length_generous - cone_height - body_length,
        center_x,
        center_y,
        tool_bottom_z + cone_height + body_length,
    )
    return {
        "tip": (tip, tool_black_color),
        "body": (body, tool_black_color),
        "shank": (shank, tap_tin_color),
        "fit": _kit.cylinder(
            head_diameter, countersink_length_generous, center_x, center_y, tool_bottom_z
        ),
    }


def build_drill_reference(center_x, center_y):
    """One 9/64" jobber drill standing point down."""
    shape = _kit.cylinder(drill_diameter, drill_length, center_x, center_y, tool_bottom_z)
    return {"drill": (shape, tool_steel_color), "fit": shape}


def build_die_reference():
    """The 1-1/2" OD round die lying flat in its pocket."""
    disc = _kit.cylinder(
        die_diameter, die_thickness_generous, die_pocket_x, die_pocket_y, die_pocket_floor_z + tool_stand_off_z
    )
    bore = _kit.cylinder(
        die_bore_diameter,
        die_thickness_generous + 1.0,
        die_pocket_x,
        die_pocket_y,
        die_pocket_floor_z,
    )
    return {"die": (disc.cut(bore), tool_steel_color), "fit": disc}


def build_spade_reference():
    """The Bosch spade bit standing paddle down, hex shank up."""
    paddle = _kit.placed_prism(
        spade_cut_diameter,
        spade_paddle_thickness_generous,
        spade_paddle_length,
        spade_slot_x,
        spade_slot_y,
        z_bottom=tool_bottom_z,
    )
    shank = _kit.cylinder(
        spade_shank_across_corners,
        spade_length - spade_paddle_length,
        spade_slot_x,
        spade_slot_y,
        tool_bottom_z + spade_paddle_length,
    )
    return {
        "paddle": (paddle, bosch_blue_color),
        "shank": (shank, tool_steel_color),
        "fit": paddle.union(shank),
    }


def build_guide_reference():
    """The spring tap guide standing shank down, its centring point up."""
    body = _kit.cylinder(
        guide_body_diameter,
        guide_length_generous - guide_point_length,
        guide_socket_x,
        guide_socket_y,
        tool_bottom_z,
    )
    point = _kit.cone(
        guide_point_diameter,
        1.5,
        guide_point_length,
        guide_socket_x,
        guide_socket_y,
        tool_bottom_z + guide_length_generous - guide_point_length,
    )
    return {
        "body": (body, tool_steel_color),
        "point": (point, tool_black_color),
        "fit": body.union(point),
    }


def build_noga_reference():
    """The deburr tool standing blade down, its grip up."""
    blade = _kit.cylinder(
        noga_blade_diameter, noga_blade_length_generous, noga_well_x, noga_well_y, tool_bottom_z
    )
    handle = _kit.cylinder(
        noga_handle_diameter,
        noga_handle_length - noga_grip_length,
        noga_well_x,
        noga_well_y,
        tool_bottom_z + noga_blade_length_generous,
    )
    grip = _kit.cylinder(
        noga_handle_diameter,
        noga_grip_length,
        noga_well_x,
        noga_well_y,
        tool_bottom_z + noga_blade_length_generous + noga_handle_length - noga_grip_length,
    )
    return {
        "blade": (blade, tool_steel_color),
        "handle": (handle, noga_body_color),
        "grip": (grip, noga_grip_color),
        "fit": blade.union(handle).union(grip),
    }


def build_arbor_reference():
    """The hole-saw arbor lying across the aft cell, pilot drill fitted."""
    shank = _kit.lying_cylinder(
        arbor_shank_across_corners,
        arbor_shank_length_generous,
        arbor_axis_y,
        arbor_axis_z,
        center_x=-(arbor_length - arbor_shank_length_generous) / 2.0,
    )
    flange = _kit.lying_cylinder(
        arbor_flange_diameter_generous,
        arbor_flange_length_generous,
        arbor_axis_y,
        arbor_axis_z,
        center_x=(arbor_shank_length_generous + arbor_flange_length_generous) / 2.0
        - arbor_length / 2.0,
    )
    pilot = _kit.lying_cylinder(
        arbor_pilot_diameter,
        arbor_pilot_stickout_generous,
        arbor_axis_y,
        arbor_axis_z,
        center_x=(arbor_length - arbor_pilot_stickout_generous) / 2.0,
    )
    return {
        "shank": (shank, tool_black_color),
        "flange": (flange, tool_steel_color),
        "pilot": (pilot, tool_steel_color),
        "fit": shank.union(flange).union(pilot),
    }


def build_pilot_drill_reference(center_y):
    shape = _kit.lying_cylinder(
        pilot_drill_diameter_generous,
        pilot_drill_length_generous,
        center_y,
        pilot_drill_axis_z,
    )
    return {"pilot-drill": (shape, tool_steel_color), "fit": shape}


def build_references():
    """Every stored thing, keyed by the name a fit check prints."""
    references = {}
    tap_names = ("LingGan M35 tap", "Drill America DWT64006 tap", "tap-and-die kit tap")
    tap_colors = (tap_tin_color, tool_steel_color, tool_steel_color)
    for name, center_x, steel_color in zip(tap_names, tap_socket_centers_x, tap_colors):
        references[name] = build_tap_reference(center_x, tap_row_y, steel_color)
    for head_diameter, center_y in zip(countersink_head_diameters, countersink_socket_centers_y):
        references[f"countersink {head_diameter / inch:.3f} in"] = build_countersink_reference(
            head_diameter, countersink_column_x, center_y
        )
    for index, (center_x, center_y) in enumerate(drill_socket_centers, 1):
        references[f"9/64 in drill {index}"] = build_drill_reference(center_x, center_y)
    references["1-1/2 in round die"] = build_die_reference()
    references["Bosch spade bit"] = build_spade_reference()
    references["B&S tap guide"] = build_guide_reference()
    references["Noga NG8150"] = build_noga_reference()
    references["hole-saw arbor"] = build_arbor_reference()
    for index, center_y in enumerate(pilot_drill_axis_y, 1):
        references[f"pilot drill {index}"] = build_pilot_drill_reference(center_y)
    return references


rack_reference_names = tuple(
    name
    for name in (
        "LingGan M35 tap",
        "Drill America DWT64006 tap",
        "tap-and-die kit tap",
        *[f"countersink {d / inch:.3f} in" for d in countersink_head_diameters],
        *[f"9/64 in drill {index}" for index in range(1, drill_count + 1)],
        "1-1/2 in round die",
        "Bosch spade bit",
        "B&S tap guide",
        "Noga NG8150",
    )
)
saw_reference_names = ("hole-saw arbor", "pilot drill 1", "pilot drill 2")


# ============================================================
# FIT CHECKS
# ============================================================

def assert_sockets_on_plateau(footprints, rectangles):
    """No socket reaches past the flat top a lipped blank offers."""
    reach = 0.0
    for _, center_x, center_y, diameter, _floor_z in footprints:
        reach = max(reach, max(abs(center_x), abs(center_y)) + diameter / 2.0)
    for _, center_x, center_y, width, depth, _floor_z in rectangles:
        reach = max(reach, abs(center_x) + width / 2.0, abs(center_y) + depth / 2.0)
    _kit.assert_inside_plateau(
        "rack sockets on plateau",
        reach,
        reach,
        kit_units_x,
        kit_units_y,
        margin=rack_socket_wall / 2.0,
    )


def assert_socket_walls(footprints, rectangles, minimum=rack_socket_wall - 0.5):
    """The thinnest plastic anywhere between two sockets."""
    boxes = [
        (name, center_x - diameter / 2.0, center_x + diameter / 2.0,
         center_y - diameter / 2.0, center_y + diameter / 2.0)
        for name, center_x, center_y, diameter, _floor_z in footprints
    ] + [
        (name, center_x - width / 2.0, center_x + width / 2.0,
         center_y - depth / 2.0, center_y + depth / 2.0)
        for name, center_x, center_y, width, depth, _floor_z in rectangles
    ]
    thinnest = None
    for index, first in enumerate(boxes):
        for second in boxes[index + 1:]:
            gap_x = max(first[1] - second[2], second[1] - first[2])
            gap_y = max(first[3] - second[4], second[3] - first[4])
            gap = max(gap_x, gap_y)
            if thinnest is None or gap < thinnest[0]:
                thinnest = (gap, first[0], second[0])
    if thinnest[0] < minimum:
        raise ValueError(
            f"socket wall: {thinnest[0]:.2f} mm between {thinnest[1]} and {thinnest[2]}"
        )
    print(
        f"   rack socket walls: {thinnest[0]:.2f} mm thinnest, "
        f"{thinnest[1]} to {thinnest[2]}"
    )
    return thinnest[0]


def assert_socket_floors_above_base(name, floor_z, base_height=_kit.dock_extra_depth):
    """A socket floor stands on the rack's own material, never on the storey below."""
    if floor_z < base_height:
        raise ValueError(f"{name}: socket floor at {floor_z:.2f} mm cuts into the base profile")
    print(f"   {name}: {floor_z:.2f} mm socket floor, {floor_z - base_height:.2f} mm over the base")


def validate(parts, references, cavities):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    storeys = [
        _kit.Storey("drill-press-saw", parts["drill-press-saw"], saw_storey_u, kind="bin"),
        _kit.Storey("drill-press-index", parts["drill-press-index"], rack_storey_u, kind="blank"),
    ]
    seats = _kit.stack_seats(storeys)
    _kit.assert_stack_seated(parts["drill-press-dock"], storeys, seats)

    assert_sockets_on_plateau(_round_socket_footprints(), _rectangular_socket_footprints())
    thinnest_wall = assert_socket_walls(
        _round_socket_footprints(), _rectangular_socket_footprints()
    )
    assert_socket_floors_above_base("tool sockets", rack_socket_floor_z)
    assert_socket_floors_above_base("die pocket", die_pocket_floor_z)

    for name in rack_reference_names:
        _kit.assert_clear(name, parts["drill-press-index"], references[name]["fit"])

    forward_cavity, aft_cavity = cavities
    _kit.assert_contained("hole-saw arbor", references["hole-saw arbor"]["fit"], aft_cavity)
    for index in (1, 2):
        _kit.assert_contained(
            f"pilot drill {index}", references[f"pilot drill {index}"]["fit"], forward_cavity
        )

    if hole_saw_cut_diameter <= saw_inner_x - 2.0:
        raise ValueError("the hole saw fits a 3 x 3 cell: give it the storey the README denies it")
    print(
        f"   hole saw stays out: {hole_saw_cut_diameter:.1f} mm cut against a "
        f"{saw_inner_x:.1f} mm cell"
    )

    return storeys, seats, thinnest_wall


# ============================================================
# ASSEMBLY AND EXPORT
# ============================================================

exploded_lift = 240.0


def reference_pieces(references, names, storey_index):
    """(name, shape, color, storey index) for `kit_assembly`, one per coloured piece."""
    pieces = []
    for name in names:
        for piece, drawn in references[name].items():
            if piece == "fit":
                continue
            shape, color = drawn
            pieces.append((f"{name} {piece}", shape, color, storey_index))
    return pieces


def build_kit_assembly(name, parts, storeys, seats, references):
    return _kit.kit_assembly(
        name,
        parts["drill-press-dock"],
        storeys,
        seats,
        references=(
            reference_pieces(references, saw_reference_names, 0)
            + reference_pieces(references, rack_reference_names, 1)
        ),
    )


def main():
    out_dir = Path(__file__).resolve().parent
    parts = {
        "drill-press-dock": build_dock(),
        "drill-press-saw": build_saw_storey(),
        "drill-press-index": build_index_storey(),
    }
    cavities = _kit.bin_cells(
        _kit.bin_cavity(parts["drill-press-saw"], kit_units_x, kit_units_y, saw_storey_u)
    )
    references = build_references()

    storeys, seats, thinnest_wall = validate(parts, references, cavities)

    _kit.export_parts(out_dir, parts)
    _kit.export_kit(
        out_dir,
        "drill-press-kit",
        build_kit_assembly("drill-press-kit", parts, storeys, seats, references),
    )
    _kit.export_kit(
        out_dir,
        "drill-press-kit-open",
        build_kit_assembly(
            "drill-press-kit-open",
            parts,
            storeys,
            _kit.exploded_seats(seats, exploded_lift),
            references,
        ),
    )

    rack_seat_z = seats[1]
    printed_height = rack_seat_z + _kit.bbox(parts["drill-press-index"]).zlen
    populated_height = rack_seat_z + tool_bottom_z + noga_length
    socket_count = len(_round_socket_footprints()) + len(_rectangular_socket_footprints())
    variables = {
        "FOOTPRINT": f"{kit_nominal_footprint:.0f} mm x {kit_nominal_footprint:.0f} mm",
        "SOCKET_COUNT": f"{socket_count}",
        "DOCK_ENVELOPE": _kit.size_text(parts["drill-press-dock"]),
        "SAW_ENVELOPE": _kit.size_text(parts["drill-press-saw"]),
        "INDEX_ENVELOPE": _kit.size_text(parts["drill-press-index"]),
        "PRINTED_HEIGHT": f"{printed_height:.1f} mm",
        "POPULATED_HEIGHT": f"{populated_height:.1f} mm",
        "H2C_ENVELOPE": (
            f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x {_kit.h2c_build_z:.0f} mm"
        ),
        "TALLEST_PART": f"{_kit.bbox(parts['drill-press-index']).zlen:.1f} mm",
        "RACK_PLATEAU": f"{rack_plateau_span:.1f} mm x {rack_plateau_span:.1f} mm",
        "SOCKET_CLEARANCE": f"{rack_socket_clearance:.1f} mm",
        "SOCKET_DEPTH": f"{rack_socket_depth:.1f} mm",
        "MIN_SOCKET_WALL": f"{thinnest_wall:.1f} mm",
        "SAW_CELL": f"{saw_inner_x:.1f} x {saw_cell_depth:.1f} x {saw_cavity_depth:.1f} mm",
        "SAW_CELL_WIDTH": f"{saw_inner_x:.1f} mm",
        "DIE_PROUD": f"{die_thickness_generous - die_pocket_depth:.1f} mm",
        "TAP_MAGIC_HEIGHT": f"{tap_magic_bottle_height:.1f} mm",
        "LIP_SHELF": f"{GR_TOPSIDE_H:.1f} mm",
        "TAP_ENVELOPE": f"{tap_length:.1f} mm long on a {tap_shank_diameter:.2f} mm shank",
        "DIE_ENVELOPE": f"{die_diameter:.1f} mm OD x {die_thickness_generous:.0f} mm",
        "COUNTERSINK_HEADS": " / ".join(
            f"{diameter:.2f}" for diameter in countersink_head_diameters
        )
        + " mm",
        "COUNTERSINK_LENGTH": f"{countersink_length_generous:.0f} mm",
        "DRILL_ENVELOPE": f"{drill_diameter:.2f} mm x {drill_length:.1f} mm",
        "DRILL_FLUTE": f"{drill_flute_length:.1f} mm",
        "HOLE_SAW_DEPTH": f"{hole_saw_cut_depth:.0f} mm",
        "SPADE_ENVELOPE": f"{spade_cut_diameter:.1f} mm x {spade_length:.1f} mm",
        "SPADE_PADDLE": f"{spade_paddle_thickness_generous:.1f} mm",
        "NOGA_NOSE": f"{noga_blade_length_generous:.0f} mm",
        "GUIDE_ENVELOPE": f"{guide_body_diameter:.2f} mm x {guide_length_generous:.0f} mm",
        "NOGA_ENVELOPE": f"{noga_handle_diameter:.0f} mm x {noga_handle_length:.0f} mm",
        "ARBOR_ENVELOPE": (
            f"{arbor_flange_diameter_generous:.0f} mm x {arbor_length:.0f} mm"
        ),
        "PILOT_ENVELOPE": (
            f"{pilot_drill_diameter_generous:.1f} mm x {pilot_drill_length_generous:.0f} mm"
        ),
        "HOLE_SAW_CUT": f"{hole_saw_cut_diameter:.1f} mm",
        "HOLE_SAW_SHORTFALL": f"{hole_saw_cut_diameter + 2.0 - saw_inner_x:.1f} mm",
        "TAP_MAGIC_ENVELOPE": (
            f"{tap_magic_bottle_diameter:.1f} mm x {tap_magic_bottle_height:.1f} mm"
        ),
        "TAP_MAGIC_WELL_SHARE": (
            f"{100.0 * pi * (tap_magic_well_diameter / 2.0) ** 2 / rack_plateau_span ** 2:.0f} %"
        ),
        "TAP_WRENCH_LENGTH": f"{tap_wrench_length:.0f} mm",
        "DIE_HANDLE_LENGTH": f"{die_handle_length:.0f} mm",
    }
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
