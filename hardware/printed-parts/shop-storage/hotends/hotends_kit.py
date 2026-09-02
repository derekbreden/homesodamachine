"""Hotend job kit.

Frame: world +Z is up, world +Y is the operator-facing front, and world +X is the
operator's right.  Every storey is a stock cq-gridfinity body built with its bottom at
Z=0; `_kit.stack_seats` places it in the kit frame.

The kit is the H2C hotend swap.  The top storey is a job rack split down the middle:
the operator's left holds the standard hotends the H2C's lifting nozzle takes, and the
operator's right holds the induction hotends only an H2C's right nozzle takes.  A
hotend of one family is never a part for the other, so the two zones hold their
hotends differently and read apart at a glance — the left hangs nozzle-down from its
heatsink, the right stands head-down with its nozzle up.  Under the rack an open bin
carries the silicone socks and the swap well.

Bambu publishes one dimension of a hotend, its length.  Every cross-section here is a
`_generous` envelope read off the maker's own product photograph at that published
length and rounded up.
"""

import sys
from pathlib import Path

import cadquery as cq
from cqgridfinity.constants import GR_BASE_HEIGHT

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import _kit  # noqa: E402
from _kit import substitute_md  # noqa: E402


# ============================================================
# THE KIT'S FOOTPRINT AND ITS STOREYS
# ============================================================

kit_units_x = 3
kit_units_y = 3
kit_nominal_footprint = kit_units_x * _kit.grid_unit

swap_storey_u = 5
rack_storey_u = 6

exploded_lift = 90.0


# ============================================================
# PUBLIC HOTEND ENVELOPES
# ============================================================

#: Bambu's published length for the standard hotend (H2/P2S/X2D, and the H2C's left
#: nozzle): the whole assembly, quick-swap knob to nozzle tip.
standard_length = 49.2
#: Where the finned heatsink ends and the bare shank begins, as a fraction of that
#: length read off the product photograph.
standard_head_height = 19.1
standard_shank_length = standard_length - standard_head_height
standard_head_across_generous = 22.0
standard_shank_diameter_generous = 9.0

#: Bambu's published length for the H2C induction hotend (Right), SKU FAH050.
induction_length = 56.2
#: The knob, its carrier board and the slotted coil bracket, down to where the coil
#: barrel begins.
induction_head_height = 23.0
induction_barrel_length = induction_length - induction_head_height
induction_head_across_generous = 16.0
#: The barrel and the nozzle boss below it, the boss being the wider of the two.
induction_barrel_diameter_generous = 13.0


# ============================================================
# THE JOB RACK
# ============================================================

rack_plateau_half = _kit.plateau_half(kit_units_x)
rack_plateau_span = 2.0 * rack_plateau_half
rack_top_z = _kit.top_reference_z(rack_storey_u)

#: Every rack socket is this much wider than the envelope it holds, on every side, and
#: this much deeper than the length of it the socket swallows.
rack_socket_clearance = 2.0
rack_pocket_radius = 3.0
reference_corner_radius = 1.5

#: A hanging hotend's heatsink lands on the plateau; its shank hangs in the bore, and
#: the nozzle at the end of the shank never reaches the bore's floor.
standard_bore_diameter = standard_shank_diameter_generous + 2.0 * rack_socket_clearance
standard_bore_depth = standard_shank_length + rack_socket_clearance
standard_bore_floor_z = rack_top_z - standard_bore_depth

#: A standing hotend's head drops to the pocket floor; its barrel and its nozzle rise
#: above the plateau.
induction_pocket_across = induction_head_across_generous + 2.0 * rack_socket_clearance
induction_pocket_depth = induction_head_height + rack_socket_clearance
induction_pocket_floor_z = rack_top_z - induction_pocket_depth
induction_stands_proud = (
    induction_pocket_floor_z + induction_head_height + induction_barrel_length
    - rack_top_z
)

#: The plastic left between one heatsink and the next, and between one pocket and the
#: next.  A heatsink rests on the plateau rather than in a socket, so what it needs
#: from its neighbour is finger room, not a wall.
rack_socket_gap = 1.5
rack_pocket_gap = 1.5
rack_edge_margin = 1.5
rack_wall_min = 1.5


def spread_pitch(count, size):
    """The pitch that spreads `count` features of `size` over the plateau's depth."""
    return _kit.spread_pitch(count, size, rack_plateau_span - 2.0 * rack_edge_margin)


standard_columns = 3
standard_rows = 4
standard_column_pitch = standard_head_across_generous + rack_socket_gap
standard_row_pitch = spread_pitch(standard_rows, standard_head_across_generous)

induction_columns = 2
induction_rows = 5
induction_column_pitch = induction_pocket_across + rack_pocket_gap
induction_row_pitch = spread_pitch(induction_rows, induction_pocket_across)

standard_zone_span = _kit.run_span(
    standard_columns, standard_column_pitch, standard_head_across_generous
)
induction_zone_span = _kit.run_span(
    induction_columns, induction_column_pitch, induction_pocket_across
)
#: What the two zones leave between them once both have their edge margins: the band
#: the split groove is cut into.
split_band_width = (
    rack_plateau_span
    - 2.0 * rack_edge_margin
    - standard_zone_span
    - induction_zone_span
)

standard_zone_x0 = -rack_plateau_half + rack_edge_margin
standard_zone_x1 = standard_zone_x0 + standard_zone_span
induction_zone_x0 = standard_zone_x1 + split_band_width
induction_zone_x1 = induction_zone_x0 + induction_zone_span

standard_column_x = _kit.centered_run(
    standard_columns,
    standard_column_pitch,
    (standard_zone_x0 + standard_zone_x1) / 2.0,
)
standard_row_y = _kit.centered_run(standard_rows, standard_row_pitch, 0.0)
induction_column_x = _kit.centered_run(
    induction_columns,
    induction_column_pitch,
    (induction_zone_x0 + induction_zone_x1) / 2.0,
)
induction_row_y = _kit.centered_run(induction_rows, induction_row_pitch, 0.0)

split_groove_center_x = (standard_zone_x1 + induction_zone_x0) / 2.0
split_groove_width = 3.0
split_groove_depth = 4.0
split_groove_radius = split_groove_width / 3.0
split_groove_half_length = rack_plateau_half - 2.0 * rack_edge_margin
split_groove_floor_z = rack_top_z - split_groove_depth
split_groove_wall = (split_band_width - split_groove_width) / 2.0


# ============================================================
# WHAT STANDS IN EACH SOCKET
# ============================================================

#: The eleven standard hotends, front row first and smallest nozzle first, three to a
#: row.  The last row is short by one: eleven hotends in twelve places.
standard_sockets = (
    "0.4 TC (Bambu)",
    "0.4 HS (Bambu)",
    "0.4 HS (Bambu)",
    "0.4 HF (ENOMAKER)",
    "0.6 TC SF (Bambu)",
    "0.6 TC (DUROZZLE)",
    "0.6 PCD (DUROZZLE)",
    "0.8 PCD (DUROZZLE)",
    "0.8 PCD (DUROZZLE)",
    "0.8 HF (ENOMAKER)",
    "0.8 TC HF (Bambu)",
)

#: The ten induction hotends, front row first and smallest nozzle first, two to a row.
induction_sockets = (
    "0.2 SS",
    "0.2 SS",
    "0.2 SS",
    "0.4 HS",
    "0.4 HS",
    "0.4 HS",
    "0.4 HS",
    "0.6 HS",
    "0.8 HS",
    "0.8 HF HS",
)


def zone_places(column_x, row_y, count):
    """Socket centers, front row first, left to right within a row."""
    places = []
    for y in reversed(row_y):
        for x in column_x:
            if len(places) < count:
                places.append((x, y))
    return places


standard_places = zone_places(standard_column_x, standard_row_y, len(standard_sockets))
induction_places = zone_places(
    induction_column_x, induction_row_y, len(induction_sockets)
)


# ============================================================
# THE SWAP STOREY
# ============================================================

storey_floor_z = _kit.bin_floor_z
swap_cavity_depth = _kit.cavity_depth(swap_storey_u)

swap_inner_x = _kit.inner_size(kit_units_x)
swap_inner_y = _kit.inner_size(kit_units_y)
swap_cell_depth = _kit.cell_span(kit_units_y, 1)
swap_cell_center_y = _kit.cell_centers(kit_units_y, 1)[1]

#: The library's label ledge roofs the +Y end of every compartment, so a content
#: standing full height keeps this far off that end.
label_ledge_width = _kit.label_tape_width
swap_content_margin = 2.0

#: DUROZZLE ships two silicone socks with each of its four L-side hotends. Nothing
#: public states a sock's size; this is a generous envelope for one, laid flat.
sock_length_generous = 26.0
sock_across_generous = 16.0
sock_count = 8
sock_block_columns = 4
sock_block_rows = sock_count // sock_block_columns
sock_block_x = sock_block_columns * sock_length_generous
sock_block_y = sock_block_rows * sock_across_generous
sock_block_z = sock_across_generous

sock_cell_center_y = -swap_cell_center_y
sock_cell_back_y = sock_cell_center_y - swap_cell_depth / 2.0
sock_cell_ledge_y = sock_cell_center_y + swap_cell_depth / 2.0 - label_ledge_width
sock_block_center_y = sock_cell_back_y + swap_content_margin + sock_block_y / 2.0

#: The two H2Cs carry four hotends between them; a swap lays every one it pulls here.
in_play_standard_count = 2
in_play_induction_count = 2

well_cell_center_y = swap_cell_center_y
well_cell_back_y = well_cell_center_y - swap_cell_depth / 2.0
well_cell_ledge_y = well_cell_center_y + swap_cell_depth / 2.0 - label_ledge_width
well_standard_center_y = (
    well_cell_back_y + swap_content_margin + standard_head_across_generous / 2.0
)
well_induction_center_y = (
    well_standard_center_y
    + standard_head_across_generous / 2.0
    + swap_content_margin
    + induction_head_across_generous / 2.0
)
well_standard_x = _kit.centered_run(
    in_play_standard_count, standard_length + swap_content_margin, 0.0
)
well_induction_x = _kit.centered_run(
    in_play_induction_count, induction_length + swap_content_margin, 0.0
)


# ============================================================
# DISPLAY COLOURS
# ============================================================

heatsink_color = cq.Color(0.13, 0.13, 0.15)
shank_color = cq.Color(0.70, 0.71, 0.73)
coil_bracket_color = cq.Color(0.20, 0.21, 0.24)
coil_barrel_color = cq.Color(0.09, 0.09, 0.10)
sock_color = cq.Color(0.16, 0.36, 0.70)


# ============================================================
# PRINTED PARTS
# ============================================================

def build_dock():
    return _kit.dock_body(kit_units_x, kit_units_y)


def build_swap_storey():
    """One divided open bin: socks behind the divider, the swap well in front of it."""
    return _kit.bin_body(
        kit_units_x, kit_units_y, swap_storey_u, width_div=1, labels=True
    )


def build_rack():
    """The lipped blank, its bores and pockets, and the groove that splits the zones."""
    rack = _kit.blank_body(kit_units_x, kit_units_y, rack_storey_u)
    for center_x, center_y in standard_places:
        rack = rack.cut(
            _kit.round_pocket(
                standard_bore_diameter,
                center_x,
                center_y,
                standard_bore_floor_z,
                rack_top_z,
            )
        )
    for center_x, center_y in induction_places:
        rack = rack.cut(
            _kit.pocket(
                induction_pocket_across,
                induction_pocket_across,
                center_x,
                center_y,
                induction_pocket_floor_z,
                rack_top_z,
                radius=rack_pocket_radius,
            )
        )
    rack = rack.cut(
        _kit.pocket(
            split_groove_width,
            2.0 * split_groove_half_length,
            split_groove_center_x,
            0.0,
            split_groove_floor_z,
            rack_top_z,
            radius=split_groove_radius,
        )
    )
    return rack.clean()


# ============================================================
# CONTENT ENVELOPES
# ============================================================

def standard_hotend(center_x, center_y, plateau_z):
    """A standard hotend hanging: heatsink on the plateau, shank in the bore."""
    head = _kit.placed_prism(
        standard_head_across_generous,
        standard_head_across_generous,
        standard_head_height,
        center_x,
        center_y,
        z_bottom=plateau_z,
        radius=reference_corner_radius,
    )
    shank = _kit.cylinder(
        standard_shank_diameter_generous,
        standard_shank_length,
        center_x,
        center_y,
        plateau_z - standard_shank_length,
    )
    return {"head": head, "shank": shank, "fit": head.union(shank).clean()}


def induction_hotend(center_x, center_y, floor_z):
    """An induction hotend standing: bracket in the pocket, barrel and nozzle up."""
    head = _kit.placed_prism(
        induction_head_across_generous,
        induction_head_across_generous,
        induction_head_height,
        center_x,
        center_y,
        z_bottom=floor_z,
        radius=reference_corner_radius,
    )
    barrel = _kit.cylinder(
        induction_barrel_diameter_generous,
        induction_barrel_length,
        center_x,
        center_y,
        floor_z + induction_head_height,
    )
    return {"head": head, "barrel": barrel, "fit": head.union(barrel).clean()}


def laid_hotend(length, across, center_x, center_y, floor_z):
    """A hotend lying on its side in the swap well, its axis along X."""
    return _kit.placed_prism(
        length,
        across,
        across,
        center_x,
        center_y,
        z_bottom=floor_z,
        radius=reference_corner_radius,
    )


def build_references():
    standard = [
        standard_hotend(center_x, center_y, rack_top_z)
        for center_x, center_y in standard_places
    ]
    induction = [
        induction_hotend(center_x, center_y, induction_pocket_floor_z)
        for center_x, center_y in induction_places
    ]
    socks = _kit.placed_prism(
        sock_block_x,
        sock_block_y,
        sock_block_z,
        0.0,
        sock_block_center_y,
        z_bottom=storey_floor_z,
        radius=reference_corner_radius,
    )
    in_play = []
    for center_x in well_standard_x:
        in_play.append(
            (
                "standard",
                laid_hotend(
                    standard_length,
                    standard_head_across_generous,
                    center_x,
                    well_standard_center_y,
                    storey_floor_z,
                ),
            )
        )
    for center_x in well_induction_x:
        in_play.append(
            (
                "induction",
                laid_hotend(
                    induction_length,
                    induction_head_across_generous,
                    center_x,
                    well_induction_center_y,
                    storey_floor_z,
                ),
            )
        )
    return {
        "standard": standard,
        "induction": induction,
        "socks": socks,
        "in-play": in_play,
    }


# ============================================================
# VALIDATION
# ============================================================

def assert_gap(name, clearance, minimum):
    """A gap this rack's layout leaves is at least the minimum the job wants."""
    if clearance < minimum - 1e-9:
        raise ValueError(f"{name}: {clearance:.2f} mm, under the {minimum:.2f} mm floor")
    print(f"   {name}: {clearance:.2f} mm")


def assert_inside_plateau(name, half_extent):
    return _kit.assert_inside_plateau(name, half_extent, half_extent, kit_units_x)


def validate(parts, references, cavities):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    storeys = [
        _kit.Storey("hotends-swap", parts["hotends-swap"], swap_storey_u, kind="bin"),
        _kit.Storey("hotends-rack", parts["hotends-rack"], rack_storey_u, kind="blank"),
    ]
    seats = _kit.stack_seats(storeys)
    _kit.assert_stack_seated(parts["hotends-dock"], storeys, seats)

    rack = parts["hotends-rack"]
    for label, reference in zip(standard_sockets, references["standard"]):
        _kit.assert_clear(f"standard {label}", rack, reference["fit"])
    for label, reference in zip(induction_sockets, references["induction"]):
        _kit.assert_clear(f"induction {label}", rack, reference["fit"])

    assert_gap(
        "standard nozzle over its bore floor",
        rack_top_z - standard_shank_length - standard_bore_floor_z,
        rack_socket_clearance,
    )
    assert_gap(
        "induction head under the plateau",
        rack_top_z - induction_pocket_floor_z - induction_head_height,
        rack_socket_clearance,
    )
    assert_gap(
        "bore floor over the rack's Gridfinity base",
        standard_bore_floor_z - GR_BASE_HEIGHT,
        rack_wall_min,
    )
    assert_gap(
        "pocket floor over the rack's Gridfinity base",
        induction_pocket_floor_z - GR_BASE_HEIGHT,
        rack_wall_min,
    )
    assert_gap(
        "plateau either side of the split groove",
        split_groove_wall,
        rack_wall_min,
    )
    assert_gap(
        "heatsink to heatsink across a row",
        standard_column_pitch - standard_head_across_generous,
        rack_socket_gap,
    )
    assert_gap(
        "heatsink to heatsink down a column",
        standard_row_pitch - standard_head_across_generous,
        rack_socket_gap,
    )
    assert_gap(
        "pocket to pocket across a row",
        induction_column_pitch - induction_pocket_across,
        rack_wall_min,
    )
    assert_gap(
        "pocket to pocket down a column",
        induction_row_pitch - induction_pocket_across,
        rack_wall_min,
    )
    assert_inside_plateau(
        "standard bores",
        abs(standard_column_x[0]) + standard_bore_diameter / 2.0,
    )
    assert_inside_plateau(
        "induction pockets",
        induction_column_x[-1] + induction_pocket_across / 2.0,
    )
    assert_inside_plateau(
        "heatsinks over the plateau",
        abs(standard_row_y[0]) + standard_head_across_generous / 2.0,
    )

    well_cavity, sock_cavity = cavities
    _kit.assert_contained("silicone socks", references["socks"], sock_cavity)
    for index, (family, reference) in enumerate(references["in-play"], 1):
        _kit.assert_contained(
            f"swap well {family} {index}", reference, well_cavity
        )
    assert_gap(
        "socks clear of their label ledge",
        sock_cell_ledge_y - (sock_block_center_y + sock_block_y / 2.0),
        swap_content_margin,
    )
    assert_gap(
        "swap well clear of its label ledge",
        well_cell_ledge_y
        - (well_induction_center_y + induction_head_across_generous / 2.0),
        swap_content_margin,
    )

    return storeys, seats


# ============================================================
# PRESENTATION
# ============================================================

def socket_slug(zone, index, label):
    body = label.lower().replace(".", "p")
    for junk in "()":
        body = body.replace(junk, "")
    return f"{zone}-{index:02d}-{body.replace(' ', '-')}"


def build_kit_assembly(name, parts, storeys, seats, references):
    contents = []
    for index, (label, reference) in enumerate(
        zip(standard_sockets, references["standard"]), 1
    ):
        slug = socket_slug("standard", index, label)
        contents.append((f"{slug}-heatsink", reference["head"], heatsink_color, 1))
        contents.append((f"{slug}-shank", reference["shank"], shank_color, 1))
    for index, (label, reference) in enumerate(
        zip(induction_sockets, references["induction"]), 1
    ):
        slug = socket_slug("induction", index, label)
        contents.append((f"{slug}-bracket", reference["head"], coil_bracket_color, 1))
        contents.append((f"{slug}-barrel", reference["barrel"], coil_barrel_color, 1))
    contents.append(("silicone-socks", references["socks"], sock_color, 0))
    return _kit.kit_assembly(name, parts["hotends-dock"], storeys, seats, contents)


# ============================================================
# BUILD
# ============================================================

def main():
    out_dir = Path(__file__).resolve().parent
    parts = {
        "hotends-dock": build_dock(),
        "hotends-swap": build_swap_storey(),
        "hotends-rack": build_rack(),
    }
    cavities = _kit.bin_cells(
        _kit.bin_cavity(parts["hotends-swap"], kit_units_x, kit_units_y, swap_storey_u)
    )
    references = build_references()

    storeys, seats = validate(parts, references, cavities)

    _kit.export_parts(out_dir, parts)
    _kit.export_kit(
        out_dir,
        "hotends-kit",
        build_kit_assembly("hotends-kit", parts, storeys, seats, references),
    )
    _kit.export_kit(
        out_dir,
        "hotends-kit-open",
        build_kit_assembly(
            "hotends-kit-open",
            parts,
            storeys,
            _kit.exploded_seats(seats, exploded_lift),
            references,
        ),
    )

    rack_seat_z = seats[1]
    printed_height = rack_seat_z + _kit.bbox(parts["hotends-rack"]).zlen
    populated_height = (
        rack_seat_z
        + induction_pocket_floor_z
        + induction_head_height
        + induction_barrel_length
    )
    variables = {
        "FOOTPRINT": f"{kit_nominal_footprint:.0f} mm x {kit_nominal_footprint:.0f} mm",
        "PRINTED_HEIGHT": f"{printed_height:.1f} mm",
        "POPULATED_HEIGHT": f"{populated_height:.1f} mm",
        "H2C_ENVELOPE": (
            f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x {_kit.h2c_build_z:.0f} mm"
        ),
        "TALLEST_PART": f"{_kit.bbox(parts['hotends-rack']).zlen:.1f} mm",
        "DOCK_ENVELOPE": _kit.size_text(parts["hotends-dock"]),
        "SWAP_ENVELOPE": _kit.size_text(parts["hotends-swap"]),
        "RACK_ENVELOPE": _kit.size_text(parts["hotends-rack"]),
        "SOCKET_COUNT": f"{len(standard_sockets) + len(induction_sockets)}",
        "STANDARD_COUNT": f"{len(standard_sockets)}",
        "INDUCTION_COUNT": f"{len(induction_sockets)}",
        "RACK_PLATEAU": f"{rack_plateau_span:.1f} mm x {rack_plateau_span:.1f} mm",
        "SOCKET_CLEARANCE": f"{rack_socket_clearance:.1f} mm",
        "STANDARD_ENVELOPE": (
            f"{standard_head_across_generous:.0f} x {standard_head_across_generous:.0f}"
            f" x {standard_length:.1f} mm"
        ),
        "STANDARD_LENGTH": f"{standard_length:.1f} mm",
        "STANDARD_HEAD": f"{standard_head_height:.1f} mm",
        "STANDARD_BORE": (
            f"{standard_bore_diameter:.0f} mm x {standard_bore_depth:.1f} mm"
        ),
        "INDUCTION_ENVELOPE": (
            f"{induction_head_across_generous:.0f} x {induction_head_across_generous:.0f}"
            f" x {induction_length:.1f} mm"
        ),
        "INDUCTION_LENGTH": f"{induction_length:.1f} mm",
        "INDUCTION_HEAD": f"{induction_head_height:.1f} mm",
        "INDUCTION_POCKET": (
            f"{induction_pocket_across:.0f} x {induction_pocket_across:.0f}"
            f" x {induction_pocket_depth:.0f} mm"
        ),
        "INDUCTION_STANDS_PROUD": f"{induction_stands_proud:.1f} mm",
        "SPLIT_GROOVE": f"{split_groove_width:.0f} mm x {split_groove_depth:.0f} mm",
        "SWAP_CELL": (
            f"{swap_inner_x:.1f} x {swap_cell_depth:.1f} x {swap_cavity_depth:.1f} mm"
        ),
        "SOCK_COUNT": f"{sock_count}",
        "SOCK_ENVELOPE": (
            f"{sock_length_generous:.0f} x {sock_across_generous:.0f}"
            f" x {sock_across_generous:.0f} mm"
        ),
        "IN_PLAY_COUNT": f"{in_play_standard_count + in_play_induction_count}",
    }
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
