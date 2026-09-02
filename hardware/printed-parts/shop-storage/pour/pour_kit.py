"""Pour kit — the cold core's two PU foam pours and the funnel's silicone pour.

Frame: world +Z is up, +Y is the operator-facing front, +X is the operator's
right.  Every storey is built in its own print orientation with its bottom at
Z=0, and the kit frame stacks them by their seats.

Three storeys on one 3 x 3 Gridfinity footprint: an open bin for the stirring
stock, an open bin for the oven thermometer, and a job rack whose wells stand
the nested cup column and the mould rods.  Every storey body is a stock
cq-gridfinity body; the rack's wells are the only cut geometry.
"""

import json
import math
import subprocess
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(_here.parents[1]))

import _kit  # noqa: E402
from _kit import substitute_md  # noqa: E402


# ============================================================
# FOOTPRINT
# ============================================================

grid_units = 3

#: cq-gridfinity's GridfinityBox wall thickness and floor height. `validate`
#: reads both back off a rendered cavity and refuses a mismatch.
bin_wall_thickness = 1.0
bin_floor_z = 7.0

bin_cavity_half = _kit.outer_size(grid_units) / 2.0 - bin_wall_thickness
plateau_half = _kit.plateau_half(grid_units)

#: A stored thing keeps this much to a bin wall and this much to its neighbour.
content_wall_clearance = 1.0
content_gap = 2.0

#: A rack socket is this much larger than its content on every side, and its
#: rim keeps this much of plateau outside it.
socket_clearance = 2.0
rack_rim = 2.0

#: Free height a bin keeps over its tallest content.
storey_headroom = 6.0


# ============================================================
# WHAT THE KIT HOLDS
# ============================================================

# Pouring Masters 5 oz cups, B08JHH1DBF. The 50-pack ships as one nested column
# beside its 25 mixing sticks: the pack's height is the column's diameter and
# the pack's length is the column's length.
cup_pack_length = 8.94 * 25.4
cup_pack_width = 5.55 * 25.4
cup_pack_height = 3.23 * 25.4
cup_count = 50
cup_column_diameter = cup_pack_height
cup_column_length = cup_pack_length

# JMU 6" tongue depressors, B09H6ZP447 — 6 x 11/16 in blades, individually
# wrapped. The sleeve is what stacks, so the bundle is sized on it.
depressor_count = 100
depressor_length = 6.0 * 25.4
depressor_blade_width = 11.0 / 16.0 * 25.4
depressor_sleeve_margin_along = 8.0
depressor_sleeve_margin_across = 2.5
depressor_sleeve_length = depressor_length + depressor_sleeve_margin_along
depressor_sleeve_width = depressor_blade_width + depressor_sleeve_margin_across
depressor_sleeve_thickness = 2.4
depressor_columns = 5
depressor_rows = math.ceil(depressor_count / depressor_columns)
depressor_bundle_width = depressor_columns * depressor_sleeve_width
depressor_bundle_depth = depressor_rows * depressor_sleeve_thickness
depressor_bundle_height = depressor_sleeve_length

# BBDINO black silicone pigment 150 g, B0BVR3R58V — a square pump bottle.
pigment_width = 2.5 * 25.4
pigment_height = 3.5 * 25.4

# Rubbermaid Commercial FGTHO550, B005KDEIZ0. The listing gives the base depth
# and the span across dial and hanging hook; the dial's own width is not
# published, so the envelope is generous across it.
thermometer_base_depth = 2.0 * 25.4
thermometer_span = 4.55 * 25.4
thermometer_dial_width = 100.0

# POWERTEC 71476 ground dowel pins, B086DCHYQK — the funnel mould's spout bore,
# one pin per mould, ten to a pack.
dowel_count = 10
dowel_diameter = 0.25 * 25.4
dowel_length = 2.0 * 25.4


# ============================================================
# WHAT THE FOOTPRINT DOES NOT TAKE
# ============================================================
# The pour bench's remaining stock, at its public envelope. `validate` refuses
# any of these that would in fact fit, so the contents map cannot drift away
# from the footprint that decides it.

# TCP Global 32 oz cups, B08HNCGY4N: the 25-cup box is 13.58 x 5.59 x 5.28 in,
# and its smallest cross-section bounds the cup.
batch_cup_pack_length = 13.58 * 25.4
batch_cup_pack_width = 5.59 * 25.4
batch_cup_diameter = 5.28 * 25.4

# BBDINO 40A silicone kit, B0FHHBGSQK: two bottles, 8.25 x 4.33 x 5.51 in.
silicone_kit_length = 8.25 * 25.4
silicone_kit_width = 4.33 * 25.4
silicone_kit_height = 5.51 * 25.4

# Fiberglass Supply Depot 2 lb pour foam, B08R7TX8QJ: a quart kit is one pint of
# A and one pint of B. No can dimension is published; a US 1-pint round can is
# the generous envelope.
foam_can_diameter = 87.3
foam_can_height = 98.4

# Mann Ease Release 200, B002YEBO1O: 8.5 x 2.75 x 2.75 in.
release_can_diameter = 2.75 * 25.4
release_can_height = 8.5 * 25.4

# Krylon K01303, B00023JE7K: 8 x 3 x 3 in.
clear_can_diameter = 3.0 * 25.4
clear_can_height = 8.0 * 25.4

# Smart Weigh Pro pocket scale, B00IZ1YHZK: 5 x 4 x 0.6 in.
scale_length = 5.0 * 25.4
scale_width = 4.0 * 25.4
scale_height = 0.6 * 25.4


# ============================================================
# STOREY 1 — THE STIRRING STOCK
# ============================================================

mix_height_u = math.ceil(
    (bin_floor_z + depressor_bundle_height + storey_headroom) / _kit.height_unit
)
mix_top_z = _kit.top_reference_z(mix_height_u)

depressor_center_x = 0.0
depressor_center_y = -(
    bin_cavity_half - content_wall_clearance - depressor_bundle_depth / 2.0
)
depressor_far_y = depressor_center_y + depressor_bundle_depth / 2.0

pigment_center_x = -(bin_cavity_half - content_wall_clearance - pigment_width / 2.0)
pigment_center_y = depressor_far_y + content_gap + pigment_width / 2.0


# ============================================================
# STOREY 2 — THE OVEN THERMOMETER
# ============================================================

gauge_height_u = math.ceil(
    (bin_floor_z + thermometer_base_depth + storey_headroom) / _kit.height_unit
)
gauge_top_z = _kit.top_reference_z(gauge_height_u)

thermometer_center_x = 0.0
thermometer_center_y = -(
    bin_cavity_half - content_wall_clearance - thermometer_dial_width / 2.0
)


# ============================================================
# STOREY 3 — THE JOB RACK
# ============================================================

cup_well_diameter = cup_column_diameter + 2.0 * socket_clearance
cup_well_radius = cup_well_diameter / 2.0
cup_well_floor_z = 14.0
cup_well_depth = 42.0

rack_height_u = math.ceil((cup_well_floor_z + cup_well_depth) / _kit.height_unit)
rack_top_z = _kit.top_reference_z(rack_height_u)

cup_well_center_x = -(plateau_half - rack_rim - cup_well_radius)
cup_well_center_y = cup_well_center_x
cup_column_proud = cup_well_floor_z + cup_column_length - rack_top_z

rod_hole_diameter = dowel_diameter + 2.0 * socket_clearance
rod_hole_radius = rod_hole_diameter / 2.0
rod_hole_depth = 30.0
rod_hole_floor_z = rack_top_z - rod_hole_depth
rod_hole_columns = 2
rod_hole_rows = dowel_count // rod_hole_columns
rod_hole_pitch_x = 14.0
rod_hole_pitch_y = 13.0
rod_hole_outer_x = plateau_half - rack_rim - rod_hole_radius
rod_hole_bottom_y = -(plateau_half - rack_rim - rod_hole_radius)
dowel_proud = rod_hole_floor_z + dowel_length - rack_top_z

parts_well_near_y = cup_well_center_y + cup_well_radius + rack_rim
parts_well_far_y = plateau_half - rack_rim
parts_well_center_y = (parts_well_near_y + parts_well_far_y) / 2.0
parts_well_depth_y = parts_well_far_y - parts_well_near_y
parts_well_width = 2.0 * (plateau_half - rack_rim)
parts_well_depth_z = 30.0
parts_well_floor_z = rack_top_z - parts_well_depth_z


def rod_hole_centers():
    """The rod index, read down the rack's +X edge, outer column first."""
    centers = []
    for row in range(rod_hole_rows):
        y = rod_hole_bottom_y + row * rod_hole_pitch_y
        for column in range(rod_hole_columns):
            centers.append((rod_hole_outer_x - column * rod_hole_pitch_x, y))
    return centers


# ============================================================
# THE STACK
# ============================================================

storey_lift = 110.0

mix_seat_z = _kit.dock_seat_z
gauge_seat_z = mix_seat_z + mix_top_z
rack_seat_z = gauge_seat_z + gauge_top_z
kit_seats = (mix_seat_z, gauge_seat_z, rack_seat_z)


# ============================================================
# DISPLAY COLOURS
# ============================================================

cup_color = cq.Color(0.88, 0.89, 0.90)
wood_color = cq.Color(0.79, 0.64, 0.41)
pigment_color = cq.Color(0.42, 0.30, 0.52)
steel_color = cq.Color(0.58, 0.60, 0.62)


# ============================================================
# BODIES
# ============================================================

def build_mix_storey():
    """Open bin for the stirring stock: the depressor bundle and the pigment."""
    return _kit.bin_body(grid_units, grid_units, mix_height_u, labels=True)


def build_gauge_storey():
    """Open bin the oven thermometer lies flat in."""
    return _kit.bin_body(grid_units, grid_units, gauge_height_u, labels=True)


def build_rack():
    """Lipped blank with the cup well, the rod index and the active-parts well."""
    body = _kit.blank_body(grid_units, grid_units, rack_height_u)
    body = body.cut(
        _kit.round_pocket(
            cup_well_diameter,
            cup_well_center_x,
            cup_well_center_y,
            cup_well_floor_z,
            rack_top_z,
        )
    )
    for x, y in rod_hole_centers():
        body = body.cut(
            _kit.round_pocket(rod_hole_diameter, x, y, rod_hole_floor_z, rack_top_z)
        )
    body = body.cut(
        _kit.pocket(
            parts_well_width,
            parts_well_depth_y,
            0.0,
            parts_well_center_y,
            parts_well_floor_z,
            rack_top_z,
        )
    )
    return body.clean()


def build_dock():
    return _kit.dock_body(grid_units, grid_units)


# ============================================================
# CONTENT ENVELOPES
# ============================================================

def build_depressor_bundle():
    return _kit.placed_prism(
        depressor_bundle_width,
        depressor_bundle_depth,
        depressor_bundle_height,
        depressor_center_x,
        depressor_center_y,
        z_bottom=bin_floor_z,
        radius=1.5,
    )


def build_pigment_bottle():
    return _kit.placed_prism(
        pigment_width,
        pigment_width,
        pigment_height,
        pigment_center_x,
        pigment_center_y,
        z_bottom=bin_floor_z,
        radius=6.0,
    )


def build_thermometer():
    return _kit.placed_prism(
        thermometer_span,
        thermometer_dial_width,
        thermometer_base_depth,
        thermometer_center_x,
        thermometer_center_y,
        z_bottom=bin_floor_z,
        radius=14.0,
    )


def build_cup_column():
    return _kit.cylinder(
        cup_column_diameter,
        cup_column_length,
        cup_well_center_x,
        cup_well_center_y,
        cup_well_floor_z,
    )


def build_dowel_pins():
    return [
        _kit.cylinder(dowel_diameter, dowel_length, x, y, rod_hole_floor_z)
        for x, y in rod_hole_centers()
    ]


# ============================================================
# VALIDATION
# ============================================================

def _assert_library_cavity(name, cavity):
    """The wall and floor this file places contents against are the library's."""
    bounds = _kit.bbox(cavity)
    half = bounds.xlen / 2.0
    if abs(half - bin_cavity_half) > 1e-6:
        raise ValueError(
            f"{name}: cavity half-extent {half:.3f} mm is not {bin_cavity_half:.3f} mm"
        )
    if abs(bounds.zmin - bin_floor_z) > 1e-6:
        raise ValueError(
            f"{name}: cavity floor {bounds.zmin:.3f} mm is not {bin_floor_z:.3f} mm"
        )
    print(f"   {name}: {2 * half:.1f} mm square over a floor at {bounds.zmin:.1f} mm")


def _assert_bundle_holds(name, count, columns, rows):
    if columns * rows < count:
        raise ValueError(f"{name}: {columns} x {rows} bundle holds fewer than {count}")
    print(f"   {name}: {columns} x {rows} holds {count}")


def _assert_socket_count(name, centers, count):
    if len(centers) != count:
        raise ValueError(f"{name}: {len(centers)} sockets for {count}")
    print(f"   {name}: {len(centers)} sockets")


def _assert_stands_proud(name, proud):
    if proud <= 0.0:
        raise ValueError(f"{name}: {proud:.1f} mm proud of the rack")
    print(f"   {name}: {proud:.1f} mm proud")


def lip_riser_height(bin_shape, height_u):
    """The stacking lip's vertical riser on a wall that carries no label ledge.

    It stands on the lip-inset plane and tops out at the storey's own top
    reference, and it is the face the storey above seats against."""
    top = _kit.top_reference_z(height_u)
    for face in bin_shape.faces().vals():
        bounds = face.BoundingBox()
        if (
            abs(bounds.ymin + plateau_half) < 1e-3
            and abs(bounds.ymax + plateau_half) < 1e-3
            and abs(bounds.zmax - top) < 1e-3
        ):
            return bounds.zlen
    raise ValueError("no stacking-lip riser on the -Y wall")


def _cavity_span():
    """The widest a single upright content may be across a bin cavity."""
    return 2.0 * (bin_cavity_half - content_wall_clearance)


def _pair_diagonal_slack(first_diameter, second_diameter):
    """What is left over when two upright cylinders take a cavity's diagonal."""
    first_reach = bin_cavity_half - content_wall_clearance - first_diameter / 2.0
    second_reach = bin_cavity_half - content_wall_clearance - second_diameter / 2.0
    return (
        (first_reach + second_reach) * math.sqrt(2.0)
        - (first_diameter + second_diameter) / 2.0
        - content_gap
    )


def _assert_over_span(name, width):
    if width <= _cavity_span():
        raise ValueError(f"{name}: {width:.1f} mm fits {_cavity_span():.1f} mm")
    print(f"   {name}: {width:.1f} mm over a {_cavity_span():.1f} mm cavity")


def _assert_pair_over_cavity(name, first_diameter, second_diameter):
    slack = _pair_diagonal_slack(first_diameter, second_diameter)
    if slack >= 0.0:
        raise ValueError(f"{name}: the pair fits with {slack:.1f} mm to spare")
    print(f"   {name}: the pair is {-slack:.1f} mm over the cavity diagonal")


def _assert_seats_agree(name, seats):
    if any(abs(a - b) > 1e-6 for a, b in zip(seats, kit_seats)):
        raise ValueError(f"{name}: {seats} is not {list(kit_seats)}")
    print(f"   {name}: {', '.join(f'{z:.2f}' for z in seats)} mm")


def validate(parts, storeys, seats, cavities, references):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    _assert_library_cavity("mix cavity", cavities["mix"])
    _assert_library_cavity("gauge cavity", cavities["gauge"])
    _assert_seats_agree("storey seats", seats)

    _kit.assert_stack_seated(parts["pour-dock"], storeys, seats)

    _kit.assert_contained(
        "tongue depressors", references["depressors"], cavities["mix"]
    )
    _kit.assert_contained("pigment bottle", references["pigment"], cavities["mix"])
    _kit.assert_contained(
        "oven thermometer", references["thermometer"], cavities["gauge"]
    )

    _kit.assert_clear("cup column", parts["pour-rack"], references["cups"])
    for index, pin in enumerate(references["dowels"], 1):
        _kit.assert_clear(f"dowel pin {index}", parts["pour-rack"], pin)

    _assert_bundle_holds(
        "depressor bundle", depressor_count, depressor_columns, depressor_rows
    )
    _assert_socket_count("rod index", rod_hole_centers(), dowel_count)
    _assert_stands_proud("cup column", cup_column_proud)
    _assert_stands_proud("dowel pins", dowel_proud)

    mix_riser = lip_riser_height(parts["pour-mix"], mix_height_u)
    gauge_riser = lip_riser_height(parts["pour-gauge"], gauge_height_u)
    if abs(mix_riser - gauge_riser) > 1e-6:
        raise ValueError(f"lip riser: {mix_riser:.3f} mm and {gauge_riser:.3f} mm")
    print(f"   lip riser: {mix_riser:.1f} mm on both bins")

    _assert_over_span("32 oz mixing cup", batch_cup_diameter)
    _assert_over_span("BBDINO 40A silicone kit", silicone_kit_length)
    _assert_over_span("Smart Weigh scale", scale_length)
    _assert_pair_over_cavity("PU foam cans", foam_can_diameter, foam_can_diameter)
    _assert_pair_over_cavity(
        "release and clear aerosols", release_can_diameter, clear_can_diameter
    )


# ============================================================
# ASSEMBLY AND EXPORT
# ============================================================

def content_references(references):
    placed = [
        ("tongue-depressors", references["depressors"], wood_color, 0),
        ("pigment-bottle", references["pigment"], pigment_color, 0),
        ("oven-thermometer", references["thermometer"], steel_color, 1),
        ("cup-column", references["cups"], cup_color, 2),
    ]
    for index, pin in enumerate(references["dowels"], 1):
        placed.append((f"dowel-pin-{index}", pin, steel_color, 2))
    return placed


def render_pictures(out_dir, repo_root):
    jobs = [
        {
            "step": f"printed-parts/shop-storage/pour/{name}.step",
            "out": str(Path(out_dir) / f"{name}.png"),
            "cam": cam,
            "up": up,
            "solid": True,
            "trim": True,
            "size": "1400x1400",
        }
        for name, cam, up in (
            ("pour-kit", [1.0, 1.4, 0.9], [0.0, 0.0, 1.0]),
            ("pour-kit-open", [0.75, 1.0, 1.5], [0.0, 0.0, 1.0]),
            ("pour-rack", [0.5, 0.9, 1.1], [0.0, 0.0, 1.0]),
        )
    ]
    manifest = Path(out_dir) / "_render-jobs.json"
    manifest.write_text(json.dumps(jobs))
    subprocess.run(
        ["node", "tools/render/render-step-posed.js", "--jobs", str(manifest)],
        cwd=repo_root,
        check=True,
    )
    manifest.unlink()


def main(pictures=True):
    out_dir = _here.parent
    repo_root = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())

    parts = {
        "pour-mix": build_mix_storey(),
        "pour-gauge": build_gauge_storey(),
        "pour-rack": build_rack(),
        "pour-dock": build_dock(),
    }
    storeys = [
        _kit.Storey("pour-mix", parts["pour-mix"], mix_height_u, kind="bin"),
        _kit.Storey("pour-gauge", parts["pour-gauge"], gauge_height_u, kind="bin"),
        _kit.Storey("pour-rack", parts["pour-rack"], rack_height_u, kind="blank"),
    ]
    seats = _kit.stack_seats(storeys)
    cavities = {
        "mix": _kit.bin_cavity(parts["pour-mix"], grid_units, grid_units, mix_height_u),
        "gauge": _kit.bin_cavity(
            parts["pour-gauge"], grid_units, grid_units, gauge_height_u
        ),
    }
    references = {
        "depressors": build_depressor_bundle(),
        "pigment": build_pigment_bottle(),
        "thermometer": build_thermometer(),
        "cups": build_cup_column(),
        "dowels": build_dowel_pins(),
    }

    validate(parts, storeys, seats, cavities, references)

    _kit.export_parts(out_dir, parts)
    placed = content_references(references)
    _kit.export_kit(
        out_dir,
        "pour-kit",
        _kit.kit_assembly("pour-kit", parts["pour-dock"], storeys, seats, placed),
    )
    _kit.export_kit(
        out_dir,
        "pour-kit-open",
        _kit.kit_assembly(
            "pour-kit-open",
            parts["pour-dock"],
            storeys,
            _kit.exploded_seats(seats, storey_lift),
            placed,
        ),
    )

    printed_height = rack_seat_z + _kit.bbox(parts["pour-rack"]).zlen
    populated_height = rack_seat_z + cup_well_floor_z + cup_column_length

    substitute_md(
        str(out_dir / "README.md"),
        {
            "FOOTPRINT": f"{grid_units * _kit.grid_unit:.0f} mm x "
            f"{grid_units * _kit.grid_unit:.0f} mm",
            "H2C_ENVELOPE": f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x "
            f"{_kit.h2c_build_z:.0f} mm",
            "PRINTED_HEIGHT": f"{printed_height:.1f} mm",
            "POPULATED_HEIGHT": f"{populated_height:.1f} mm",
            "MIX_HEIGHT": f"{mix_top_z:.0f} mm",
            "GAUGE_HEIGHT": f"{gauge_top_z:.0f} mm",
            "RACK_HEIGHT": f"{rack_top_z:.0f} mm",
            "BIN_CAVITY": f"{2 * bin_cavity_half:.1f} mm x {2 * bin_cavity_half:.1f} mm",
            "PLATEAU": f"{2 * plateau_half:.1f} mm x {2 * plateau_half:.1f} mm",
            "CUP_COLUMN": f"diameter {cup_column_diameter:.1f} mm x "
            f"{cup_column_length:.1f} mm",
            "CUP_COUNT": f"{cup_count}",
            "DEPRESSOR_COUNT": f"{depressor_count}",
            "DOWEL_COUNT": f"{dowel_count}",
            "CUP_PACK": f"{cup_pack_length:.1f} x {cup_pack_width:.1f} x "
            f"{cup_pack_height:.1f} mm",
            "CUP_WELL": f"diameter {cup_well_diameter:.1f} mm x {cup_well_depth:.0f} mm",
            "CUP_PROUD": f"{cup_column_proud:.1f} mm",
            "DEPRESSOR_BUNDLE": f"{depressor_bundle_width:.1f} x "
            f"{depressor_bundle_depth:.1f} x {depressor_bundle_height:.1f} mm",
            "DEPRESSOR_GRID": f"{depressor_columns} x {depressor_rows}",
            "PIGMENT_ENVELOPE": f"{pigment_width:.1f} x {pigment_width:.1f} x "
            f"{pigment_height:.1f} mm",
            "THERMOMETER_ENVELOPE": f"{thermometer_span:.1f} x "
            f"{thermometer_dial_width:.1f} x {thermometer_base_depth:.1f} mm",
            "THERMOMETER_DIAL": f"{thermometer_dial_width:.1f} mm",
            "DOWEL_ENVELOPE": f"diameter {dowel_diameter:.2f} mm x {dowel_length:.1f} mm",
            "ROD_HOLE": f"diameter {rod_hole_diameter:.2f} mm x {rod_hole_depth:.0f} mm",
            "DOWEL_PROUD": f"{dowel_proud:.1f} mm",
            "PARTS_WELL": f"{parts_well_width:.1f} x {parts_well_depth_y:.1f} x "
            f"{parts_well_depth_z:.0f} mm",
            "MIX_ENVELOPE": _kit.size_text(parts["pour-mix"]),
            "GAUGE_ENVELOPE": _kit.size_text(parts["pour-gauge"]),
            "RACK_ENVELOPE": _kit.size_text(parts["pour-rack"]),
            "DOCK_ENVELOPE": _kit.size_text(parts["pour-dock"]),
            "SOCKET_CLEARANCE": f"{socket_clearance:.1f} mm",
            "CAVITY_SPAN": f"{_cavity_span():.1f} mm",
            "BATCH_CUP_PACK": f"{batch_cup_pack_length:.1f} x "
            f"{batch_cup_pack_width:.1f} x {batch_cup_diameter:.1f} mm",
            "BATCH_CUP_DIAMETER": f"{batch_cup_diameter:.1f} mm",
            "SILICONE_KIT_PACK": f"{silicone_kit_length:.1f} x "
            f"{silicone_kit_width:.1f} x {silicone_kit_height:.1f} mm",
            "FOAM_CAN": f"diameter {foam_can_diameter:.1f} mm x {foam_can_height:.1f} mm",
            "FOAM_PAIR_OVER": f"{-_pair_diagonal_slack(foam_can_diameter, foam_can_diameter):.1f} mm",
            "RELEASE_CAN": f"diameter {release_can_diameter:.1f} mm x "
            f"{release_can_height:.1f} mm",
            "CLEAR_CAN": f"diameter {clear_can_diameter:.1f} mm x "
            f"{clear_can_height:.1f} mm",
            "AEROSOL_PAIR_OVER": f"{-_pair_diagonal_slack(release_can_diameter, clear_can_diameter):.1f} mm",
            "SCALE_ENVELOPE": f"{scale_length:.1f} x {scale_width:.1f} x "
            f"{scale_height:.1f} mm",
            "SCALE_LENGTH": f"{scale_length:.1f} mm",
            "LIP_RISER": f"{lip_riser_height(parts['pour-mix'], mix_height_u):.1f} mm",
            "BATCH_CUP_COLUMN": f"{batch_cup_pack_length:.1f} mm",
            "SILICONE_KIT_WIDTH": f"{silicone_kit_length:.1f} mm",
            "CONTENT_WALL_CLEARANCE": f"{content_wall_clearance:.0f} mm",
            "CONTENT_GAP": f"{content_gap:.0f} mm",
            "SLEEVE_MARGIN_ACROSS": f"{depressor_sleeve_margin_across:.1f} mm",
            "SLEEVE_MARGIN_ALONG": f"{depressor_sleeve_margin_along:.0f} mm",
            "SLEEVE_THICKNESS": f"{depressor_sleeve_thickness:.1f} mm",
        },
    )

    if pictures:
        render_pictures(out_dir, repo_root)


if __name__ == "__main__":
    main(pictures="--no-pictures" not in sys.argv)
