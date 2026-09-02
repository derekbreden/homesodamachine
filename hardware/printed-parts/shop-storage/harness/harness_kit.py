"""Harness job kit — the crimp bench's stock and tools on one 3 x 3 Gridfinity stack.

Frame: world +Z is up, +Y is the operator-facing front, +X is the operator's right.
Every storey is a stock cq-gridfinity body built with its bottom at Z = 0, and the kit
frame stacks each on the seat of the one below.

Loose stock is modelled as the heap its pack makes: one piece's envelope from public
dimensions, times the pack count, over the fraction of a compartment a poured heap
fills. A heap stands clear of its compartment's walls and steps back under the label
ledge, which leans into the +Y end of every compartment.

The rack's tool sockets are cut from the plateau inside the lip, open upward, with
their floors above the storey below, and each takes its tool head-down.
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hardware = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_here.parents[1]))
sys.path.insert(0, str(_hardware / "reference" / "wago-221"))

import _kit  # noqa: E402
import wago_221  # noqa: E402
from _kit import substitute_md  # noqa: E402


# ============================================================
# FOOTPRINT AND THE HEAP MODEL
# ============================================================

kit_x_u = 3
kit_y_u = 3

cavity_floor_z = _kit.bin_floor_z

#: The fraction of the space it occupies that a poured heap of loose parts fills.
heap_packing = 0.62

#: Air a heap keeps to its compartment's walls, past the library's floor fillet.
heap_wall_clear = 1.5

#: Headroom over the largest heap in a storey, before its height rounds up a unit.
heap_margin = 1.15

#: How far below a compartment's top reference the label ledge starts to lean in.
#: The ledge on the bin's own +Y wall is the deeper of the two the library draws.
ledge_drop_z = 11.75

#: How far that ledge overhangs its compartment at the top reference.
ledge_reach_y = 13.4


def compartment_capacity(width, depth, height_u):
    """The heap a compartment `width` x `depth` holds in a bin `height_u` tall.

    Full section from the floor to where the ledge starts, backed off +Y above it."""
    clear_width = width - 2.0 * heap_wall_clear
    clear_depth = depth - 2.0 * heap_wall_clear
    ledge_free_z = _kit.top_reference_z(height_u) - ledge_drop_z
    return clear_width * (
        clear_depth * (ledge_free_z - cavity_floor_z)
        + (clear_depth - ledge_reach_y) * ledge_drop_z
    )


def storey_height_u(width, depth, heaps):
    """The height units a bin of these compartments needs for its largest heap."""
    wanted = heap_margin * max(heaps)
    return next(
        units
        for units in range(2, 24)
        if compartment_capacity(width, depth, units) >= wanted
    )


class Stock:
    """One compartment's contents: `count` pieces the size of `piece`."""

    def __init__(self, name, count, piece, color):
        self.name = name
        self.count = count
        self.piece = piece
        self.color = color

    @property
    def heap(self):
        return self.count * self.piece.val().Volume() / heap_packing


def cell_ledge(cell):
    """Where this compartment's label ledge starts, and how far in it reaches on top."""
    bounds = cell.val().BoundingBox()
    corners = cell.vertices().vals()
    full_depth_z = [c.Z for c in corners if abs(c.Y - bounds.ymax) < 0.05]
    top_y = [c.Y for c in corners if abs(c.Z - bounds.zmax) < 0.05]
    return max(full_depth_z), bounds.ymax - max(top_y)


def heap_block(cell, volume):
    """The block a heap of `volume` makes in `cell`, clear of walls and label ledge."""
    bounds = cell.val().BoundingBox()
    ledge_start_z, ledge_reach = cell_ledge(cell)
    x_min = bounds.xmin + heap_wall_clear
    x_max = bounds.xmax - heap_wall_clear
    y_min = bounds.ymin + heap_wall_clear
    y_max = bounds.ymax - heap_wall_clear
    ledge_free_z = ledge_start_z - heap_wall_clear
    width = x_max - x_min
    under_ledge_depth = bounds.ymax - ledge_reach - heap_wall_clear - y_min

    lower_depth = y_max - y_min
    lower_full = width * lower_depth * (ledge_free_z - bounds.zmin)
    if volume <= lower_full:
        return _kit.placed_prism(
            width,
            lower_depth,
            volume / (width * lower_depth),
            (x_min + x_max) / 2.0,
            (y_min + y_max) / 2.0,
            z_bottom=bounds.zmin,
            radius=2.0,
        )

    lower = _kit.placed_prism(
        width,
        lower_depth,
        ledge_free_z - bounds.zmin,
        (x_min + x_max) / 2.0,
        (y_min + y_max) / 2.0,
        z_bottom=bounds.zmin,
        radius=2.0,
    )
    upper = _kit.placed_prism(
        width,
        under_ledge_depth,
        (volume - lower_full) / (width * under_ledge_depth),
        (x_min + x_max) / 2.0,
        y_min + under_ledge_depth / 2.0,
        z_bottom=ledge_free_z,
        radius=2.0,
    )
    return lower.union(upper).clean()


# ============================================================
# STOCK ENVELOPES
# ============================================================

wago_body_color = cq.Color(0.86, 0.87, 0.89)

# Crimp-terminal insulation is colour-coded by conductor range: red 22-16 AWG,
# blue 16-14, yellow 12-10.
red_sleeve_color = cq.Color(0.74, 0.10, 0.12)
blue_sleeve_color = cq.Color(0.10, 0.30, 0.68)
yellow_sleeve_color = cq.Color(0.90, 0.71, 0.12)

# A ferrule's collar is colour-coded by cross-section, DIN 46228-4.
ferrule_colors = {
    0.34: cq.Color(0.18, 0.66, 0.66),
    0.5: cq.Color(0.92, 0.92, 0.92),
    0.75: cq.Color(0.62, 0.63, 0.65),
    1.0: cq.Color(0.74, 0.10, 0.12),
    1.5: cq.Color(0.30, 0.31, 0.33),
    2.5: cq.Color(0.10, 0.30, 0.68),
}

shrink_color = cq.Color(0.52, 0.54, 0.57)
tie_color = cq.Color(0.38, 0.39, 0.42)


def crimp_terminal(barrel_diameter, barrel_length, head_length, head_width, head_thickness):
    """An insulated crimp terminal lying along +X: sleeve at −X, its head at +X."""
    barrel = _kit.cylinder(
        barrel_diameter, barrel_length, z_bottom=0.0
    ).rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
    barrel = barrel.translate((0.0, 0.0, barrel_diameter / 2.0))
    head = _kit.placed_prism(
        head_length,
        head_width,
        head_thickness,
        barrel_length + head_length / 2.0,
        0.0,
        z_bottom=barrel_diameter / 2.0 - head_thickness / 2.0,
        radius=head_thickness / 2.5,
    )
    return barrel.union(head).clean()


def bootlace_ferrule(collar_diameter, collar_length, barrel_diameter, barrel_length):
    """An insulated cord-end ferrule lying along +X: collar at −X, barrel at +X."""
    collar = _kit.cylinder(collar_diameter, collar_length).rotate(
        (0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0
    )
    barrel = (
        _kit.cylinder(barrel_diameter, barrel_length)
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
        .translate((collar_length, 0.0, 0.0))
    )
    return collar.union(barrel).translate((0.0, 0.0, collar_diameter / 2.0)).clean()


shrink_cut_length = 44.5


def shrink_wall(diameter):
    """A 2:1 sleeve's wall as supplied, over the diameters an assortment carries."""
    return 0.25 + 0.035 * diameter


def shrink_piece(diameter):
    """One cut sleeve as it lies in the bin: flattened, its length along +Y."""
    return _kit.rounded_prism(
        math.pi * diameter / 2.0,
        shrink_cut_length,
        2.0 * shrink_wall(diameter),
        radius=0.4,
    )


def zip_tie(length, strap_width, strap_thickness, head, runs=1):
    """A cable tie lying flat along +X, doubled into `runs` parallel runs.

    A tie longer than its compartment lies doubled back on itself; `runs` is how
    many times over, so the strap's own volume is unchanged."""
    head_length, head_width, head_height = head
    run_length = length / runs
    run_pitch = strap_width + 0.5
    body = _kit.placed_prism(
        head_length, head_width, head_height, head_length / 2.0, 0.0, radius=1.0
    )
    for center_y in _kit.centered_run(runs, run_pitch):
        body = body.union(
            _kit.placed_prism(
                run_length,
                strap_width,
                strap_thickness,
                head_length + run_length / 2.0,
                center_y,
                radius=0.4,
            )
        )
    return body.clean()


# --- Wire ends -------------------------------------------------------------
# Cut lengths and strap widths are the listings'; strap thickness is not published
# and is the generous figure for the width.
tie_4in_length = 4.0 * 25.4
tie_6in_length = 6.0 * 25.4
tie_8in_length = 8.0 * 25.4
tie_narrow_width = 0.1 * 25.4
tie_wide_width = 0.19 * 25.4
tie_narrow_thickness = 1.0
tie_wide_thickness = 1.1

tie_narrow_head = (5.0, 3.6, 2.8)
tie_wide_head = (7.5, 5.5, 4.0)

ties_stock = (
    Stock(
        '4" zip tie, 18 lb',
        200,
        zip_tie(tie_4in_length, tie_narrow_width, tie_narrow_thickness, tie_narrow_head),
        tie_color,
    ),
    Stock(
        '6" zip tie, 18 lb',
        100,
        zip_tie(
            tie_6in_length, tie_narrow_width, tie_narrow_thickness, tie_narrow_head, runs=2
        ),
        tie_color,
    ),
    Stock(
        '8" zip tie, 50 lb',
        100,
        zip_tie(
            tie_8in_length, tie_wide_width, tie_wide_thickness, tie_wide_head, runs=2
        ),
        tie_color,
    ),
)

shrink_diameters = (2.4, 3.2, 4.8, 6.4, 9.5, 12.7)
shrink_counts = (250, 110, 60, 40, 25, 15)

shrink_stock = tuple(
    Stock(
        f"heat-shrink 2:1, {diameter} mm",
        count,
        shrink_piece(diameter),
        shrink_color,
    )
    for diameter, count in zip(shrink_diameters, shrink_counts)
)

# --- Push-ons and rings ----------------------------------------------------
# The listings give an overall length and the tab the terminal mates; none gives an
# insulation diameter, so each sleeve is the generous cylinder for its conductor range.
faston_63_piece = crimp_terminal(
    barrel_diameter=4.3,
    barrel_length=11.0,
    head_length=10.0,
    head_width=8.2,
    head_thickness=4.6,
)
faston_48_piece = crimp_terminal(
    barrel_diameter=4.0,
    barrel_length=10.0,
    head_length=9.0,
    head_width=6.8,
    head_thickness=4.0,
)
ring_m3_piece = crimp_terminal(
    barrel_diameter=4.0,
    barrel_length=10.0,
    head_length=8.0,
    head_width=6.4,
    head_thickness=1.0,
)
male_28_piece = crimp_terminal(
    barrel_diameter=3.8,
    barrel_length=10.0,
    head_length=8.0,
    head_width=2.8,
    head_thickness=0.8,
)

# The two Baomain single-gauge packs and the smseace rings stay whole; the three
# mixed-size kits decant into the size cells beside them.
terminals_stock = (
    Stock("6.3 mm female, red", 100, faston_63_piece, red_sleeve_color),
    Stock("4.8 mm female, red", 100, faston_48_piece, red_sleeve_color),
    Stock("#4 ring, red", 150, ring_m3_piece, red_sleeve_color),
    Stock("6.3 mm female, assorted", 123, faston_63_piece, blue_sleeve_color),
    Stock("4.8 mm female, assorted", 123, faston_48_piece, yellow_sleeve_color),
    Stock("2.8 mm male", 214, male_28_piece, red_sleeve_color),
)

# --- Ferrules --------------------------------------------------------------
#: DIN 46228-4 per cross-section: collar outside diameter, total length over the collar,
#: barrel outside diameter, barrel length. Compartment order, the two the machine lands
#: first.
ferrule_geometry = {
    0.34: (2.0, 12.5, 1.3, 8.0),
    1.5: (3.4, 14.5, 2.3, 8.0),
    0.5: (2.6, 14.0, 1.4, 8.0),
    0.75: (2.8, 14.0, 1.7, 8.0),
    1.0: (3.0, 14.0, 1.9, 8.0),
    2.5: (4.2, 15.5, 2.9, 8.0),
}
ferrule_counts = {0.34: 250, 1.5: 250, 0.5: 150, 0.75: 100, 1.0: 100, 2.5: 100}

ferrules_stock = tuple(
    Stock(
        f"{section} mm² ferrule",
        ferrule_counts[section],
        bootlace_ferrule(collar_d, total_l - barrel_l, barrel_d, barrel_l),
        ferrule_colors[section],
    )
    for section, (collar_d, total_l, barrel_d, barrel_l) in ferrule_geometry.items()
)

# --- Lever nuts ------------------------------------------------------------
lever_sizes = ("413", "415", "420")
lever_counts = (50, 25, 15)

levers_stock = tuple(
    Stock(f"WAGO 221-{size}", count, wago_221.build(size), wago_body_color)
    for size, count in zip(lever_sizes, lever_counts)
)


# ============================================================
# THE STOREYS
# ============================================================

class BinStorey:
    """One open storey: its dividers, what fills it, and the height that takes.

    `length_div` splits the interior across X into columns and `width_div` across Y
    into rows, so a compartment is named by its row from the front and its column
    from the left."""

    def __init__(self, name, length_div, width_div, stock):
        self.name = name
        self.length_div = length_div
        self.width_div = width_div
        self.stock = stock
        self.cell_x = _kit.cell_span(kit_x_u, length_div)
        self.cell_y = _kit.cell_span(kit_y_u, width_div)
        self.height_u = storey_height_u(
            self.cell_x, self.cell_y, [item.heap for item in stock]
        )

    def body(self):
        return _kit.bin_body(
            kit_x_u,
            kit_y_u,
            self.height_u,
            length_div=self.length_div,
            width_div=self.width_div,
            labels=True,
        )


#: The column bottom to top, from the stock a build touches twice to the stock it
#: touches at every conductor.
bin_storeys = (
    BinStorey("harness-levers", 0, 2, levers_stock),
    BinStorey("harness-ties", 0, 2, ties_stock),
    BinStorey("harness-terminals", 2, 1, terminals_stock),
    BinStorey("harness-ferrules", 2, 1, ferrules_stock),
    BinStorey("harness-shrink", 2, 1, shrink_stock),
)

rack_name = "harness-rack"
rack_storey_index = len(bin_storeys)
dock_name = "harness-dock"


# ============================================================
# THE JOB RACK
# ============================================================

rack_socket_floor_z = 8.0
rack_socket_clear = 2.5
rack_socket_wall = 4.0

#: The grip a socket keeps on the head of a tool standing in it.
rack_socket_depth = 34.0

rack_height_u = math.ceil(
    (rack_socket_floor_z + rack_socket_depth) / _kit.height_unit
)
rack_top_z = _kit.top_reference_z(rack_height_u)
rack_plateau_half = _kit.plateau_half(kit_x_u)

well_floor_z = 22.0

#: Tool head-down in a socket: the head clears the socket floor by this much.
tool_stand_clear = 0.5

# Preciva ferrule crimper B0DS622GKN — the kit listing's 240 x 48 mm tool; the head's
# thickness and its share of the length are not published and are generous.
preciva_length = 240.0
preciva_head_width = 48.0
preciva_head_thickness = 32.0
preciva_head_height = 60.0

# haisstronica HS-9327 B08F3JKDD3 — 230.1 x 59.9 mm listed; thickness generous.
haisstronica_length = 230.1
haisstronica_head_width = 59.9
haisstronica_head_thickness = 30.0
haisstronica_head_height = 55.0

# Klein 11063W B00CXKOEQ6 — 167.5 mm on Klein's datasheet; the head is the JST
# tower's public-photo envelope.
klein_length = 167.5
klein_head_width = 69.0
klein_head_thickness = 25.0
klein_head_height = 54.0

# KATA micro flush cutter B0BBML9M2V — 127 mm named in the listing; head generous.
kata_length = 127.0
kata_head_width = 10.0
kata_head_thickness = 17.0
kata_head_height = 36.0


def socket_span(size):
    return size + 2.0 * rack_socket_clear


preciva_socket_x = socket_span(preciva_head_thickness)
preciva_socket_y = socket_span(preciva_head_width)
haisstronica_socket_x = socket_span(haisstronica_head_thickness)
haisstronica_socket_y = socket_span(haisstronica_head_width)
klein_socket_x = socket_span(klein_head_thickness)
klein_socket_y = socket_span(klein_head_width)
kata_socket_x = socket_span(kata_head_thickness)
kata_socket_y = socket_span(kata_head_width)

#: The three crimper sockets share the plateau's width, two walls between them and
#: an equal wall at each end.
rack_edge_wall = (
    2.0 * rack_plateau_half
    - (preciva_socket_x + haisstronica_socket_x + klein_socket_x)
    - 2.0 * rack_socket_wall
) / 2.0

_crimper_row_x0 = -rack_plateau_half + rack_edge_wall
preciva_center_x = _crimper_row_x0 + preciva_socket_x / 2.0
haisstronica_center_x = (
    _crimper_row_x0 + preciva_socket_x + rack_socket_wall + haisstronica_socket_x / 2.0
)
klein_center_x = (
    _crimper_row_x0
    + preciva_socket_x
    + haisstronica_socket_x
    + 2.0 * rack_socket_wall
    + klein_socket_x / 2.0
)

_crimper_row_y0 = -rack_plateau_half + rack_socket_wall
preciva_center_y = _crimper_row_y0 + preciva_socket_y / 2.0
haisstronica_center_y = _crimper_row_y0 + haisstronica_socket_y / 2.0
klein_center_y = _crimper_row_y0 + klein_socket_y / 2.0

_front_row_y0 = _crimper_row_y0 + klein_socket_y + rack_socket_wall
_front_row_y1 = rack_plateau_half - rack_socket_wall
front_row_center_y = (_front_row_y0 + _front_row_y1) / 2.0

kata_center_x = -rack_plateau_half + rack_edge_wall + kata_socket_x / 2.0

#: The well takes the rest of the front strip, past the cutter and inside the lip.
_well_x0 = kata_center_x + kata_socket_x / 2.0 + 2.0 * rack_socket_wall
_well_x1 = rack_plateau_half - rack_edge_wall
parts_well_x = _well_x1 - _well_x0
parts_well_y = _front_row_y1 - _front_row_y0
parts_well_center_x = (_well_x0 + _well_x1) / 2.0


def build_rack():
    """A lipped blank with a head-down socket per tool and one open parts well."""
    rack = _kit.blank_body(kit_x_u, kit_y_u, rack_height_u)
    for width, depth, center_x, center_y in (
        (preciva_socket_x, preciva_socket_y, preciva_center_x, preciva_center_y),
        (
            haisstronica_socket_x,
            haisstronica_socket_y,
            haisstronica_center_x,
            haisstronica_center_y,
        ),
        (klein_socket_x, klein_socket_y, klein_center_x, klein_center_y),
        (kata_socket_x, kata_socket_y, kata_center_x, front_row_center_y),
    ):
        rack = rack.cut(
            _kit.pocket(
                width, depth, center_x, center_y, rack_socket_floor_z, rack_top_z
            )
        )
    rack = rack.cut(
        _kit.pocket(
            parts_well_x,
            parts_well_y,
            parts_well_center_x,
            front_row_center_y,
            well_floor_z,
            rack_top_z,
        )
    )
    return rack.clean()


# ============================================================
# TOOL REFERENCES
# ============================================================

tool_body_color = cq.Color(0.22, 0.23, 0.25)
tool_orange_color = cq.Color(0.92, 0.30, 0.06)
tool_blue_color = cq.Color(0.08, 0.28, 0.62)
tool_grip_color = cq.Color(0.08, 0.08, 0.09)
tool_steel_color = cq.Color(0.58, 0.60, 0.62)


def _grip_pair(center_x, center_y, thickness, bottom_z, top_z, inner_half, outer_half):
    """The two handles of a head-down tool, splayed in Y as they rise."""
    grips = []
    for side in (-1.0, 1.0):
        profile = [
            (center_y + side * inner_half, bottom_z),
            (center_y + side * outer_half, top_z),
            (center_y + side * (outer_half + thickness), top_z),
            (center_y + side * (inner_half + thickness), bottom_z),
        ]
        plane = cq.Plane(
            origin=(center_x, 0.0, 0.0), xDir=(0.0, 1.0, 0.0), normal=(1.0, 0.0, 0.0)
        )
        grips.append(
            cq.Workplane(plane).polyline(profile + profile[:1]).wire()
            .extrude(thickness, both=True)
        )
    return grips


def head_down_tool(
    length,
    head_width,
    head_thickness,
    head_height,
    center_x,
    center_y,
    grip_thickness,
    grip_inner_half,
    grip_outer_half,
):
    """A tool standing head-down: its head in the socket, its handles over the rack."""
    head_bottom_z = rack_socket_floor_z + tool_stand_clear
    head = _kit.placed_prism(
        head_thickness,
        head_width,
        head_height,
        center_x,
        center_y,
        z_bottom=head_bottom_z,
        radius=4.0,
    )
    grip_bottom_z = max(head_bottom_z + head_height - 10.0, rack_top_z + 0.5)
    left, right = _grip_pair(
        center_x,
        center_y,
        grip_thickness,
        grip_bottom_z,
        head_bottom_z + length,
        grip_inner_half,
        grip_outer_half,
    )
    return {"head": head, "left-grip": left, "right-grip": right}


def tool_fit(tool):
    return tool["head"].union(tool["left-grip"]).union(tool["right-grip"]).clean()


def build_tool_references():
    return {
        "preciva": head_down_tool(
            preciva_length,
            preciva_head_width,
            preciva_head_thickness,
            preciva_head_height,
            preciva_center_x,
            preciva_center_y,
            14.0,
            8.0,
            20.0,
        ),
        "haisstronica": head_down_tool(
            haisstronica_length,
            haisstronica_head_width,
            haisstronica_head_thickness,
            haisstronica_head_height,
            haisstronica_center_x,
            haisstronica_center_y,
            14.0,
            9.0,
            22.0,
        ),
        "klein": head_down_tool(
            klein_length,
            klein_head_width,
            klein_head_thickness,
            klein_head_height,
            klein_center_x,
            klein_center_y,
            13.0,
            10.0,
            20.0,
        ),
        "kata": head_down_tool(
            kata_length,
            kata_head_width,
            kata_head_thickness,
            kata_head_height,
            kata_center_x,
            front_row_center_y,
            7.0,
            2.0,
            7.0,
        ),
    }


tool_colors = {
    "preciva": (tool_body_color, tool_orange_color),
    "haisstronica": (tool_body_color, tool_blue_color),
    "klein": (tool_steel_color, cq.Color(0.25, 0.52, 0.86)),
    "kata": (tool_steel_color, tool_grip_color),
}


# ============================================================
# THE KIT
# ============================================================

def build_kit():
    """The dock, the storeys in stacking order, and every printed part by output name."""
    dock = _kit.dock_body(kit_x_u, kit_y_u)
    storeys = [
        _kit.Storey(storey.name, storey.body(), storey.height_u)
        for storey in bin_storeys
    ]
    storeys.append(_kit.Storey(rack_name, build_rack(), rack_height_u, kind="blank"))
    parts = {storey.name: storey.shape for storey in storeys}
    parts[dock_name] = dock
    return dock, storeys, parts


def storey_contents(bin_shape, height_u, stock_row, storey_index):
    """Every compartment's heap and the one piece resting on it, with its cell."""
    cells = _kit.bin_cells(_kit.bin_cavity(bin_shape, kit_x_u, kit_y_u, height_u))
    if len(cells) != len(stock_row):
        raise ValueError(
            f"{len(cells)} compartments for {len(stock_row)} kinds of stock"
        )
    contents = []
    for cell, stock in zip(cells, stock_row):
        heap = heap_block(cell, stock.heap)
        heap_top_z = heap.val().BoundingBox().zmax
        cell_bounds = cell.val().BoundingBox()
        ledge_start_z, ledge_reach = cell_ledge(cell)
        piece_bounds = stock.piece.val().BoundingBox()
        under_ledge_y = (
            cell_bounds.ymax
            - ledge_reach
            - heap_wall_clear
            - piece_bounds.ylen / 2.0
        )
        centred_y = (cell_bounds.ymin + cell_bounds.ymax) / 2.0
        piece = stock.piece.translate(
            (
                (cell_bounds.xmin + cell_bounds.xmax) / 2.0 - piece_bounds.center.x,
                (
                    min(centred_y, under_ledge_y)
                    if heap_top_z + piece_bounds.zlen > ledge_start_z
                    else centred_y
                )
                - piece_bounds.center.y,
                heap_top_z,
            )
        )
        contents.append(
            {
                "name": stock.name,
                "count": stock.count,
                "color": stock.color,
                "cell": cell,
                "heap": heap,
                "piece": piece,
                "storey": storey_index,
            }
        )
    return contents


def build_contents(parts):
    contents = []
    for index, storey in enumerate(bin_storeys):
        contents.extend(
            storey_contents(
                parts[storey.name], storey.height_u, storey.stock, index
            )
        )
    return contents


def kit_references(contents, tools):
    """Coloured envelopes of everything the kit holds, each with its storey index."""
    references = []
    for item in contents:
        references.append(
            (f"{item['name']} x{item['count']}", item["heap"], item["color"], item["storey"])
        )
        references.append((f"{item['name']}", item["piece"], item["color"], item["storey"]))
    for name, tool in tools.items():
        body_color, grip_color = tool_colors[name]
        for part, shape in tool.items():
            references.append(
                (
                    f"{name}-{part}",
                    shape,
                    body_color if part == "head" else grip_color,
                    rack_storey_index,
                )
            )
    return references


# ============================================================
# FIT CHECKS
# ============================================================

def validate(dock, storeys, parts, contents, tools):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    seats = _kit.stack_seats(storeys)
    _kit.assert_stack_seated(dock, storeys, seats)

    for item in contents:
        _kit.assert_contained(
            f"{item['name']} x{item['count']} heap", item["heap"], item["cell"]
        )
        _kit.assert_contained(f"{item['name']} piece", item["piece"], item["cell"])

    rack = parts[rack_name]
    for name, tool in tools.items():
        _kit.assert_clear(name, rack, tool_fit(tool))

    for name, center_x, socket_x, center_y, socket_y in (
        ("preciva socket", preciva_center_x, preciva_socket_x, preciva_center_y, preciva_socket_y),
        (
            "haisstronica socket",
            haisstronica_center_x,
            haisstronica_socket_x,
            haisstronica_center_y,
            haisstronica_socket_y,
        ),
        ("klein socket", klein_center_x, klein_socket_x, klein_center_y, klein_socket_y),
        ("kata socket", kata_center_x, kata_socket_x, front_row_center_y, kata_socket_y),
        (
            "parts well",
            parts_well_center_x,
            parts_well_x,
            front_row_center_y,
            parts_well_y,
        ),
    ):
        _kit.assert_inside_plateau(
            name,
            abs(center_x) + socket_x / 2.0,
            abs(center_y) + socket_y / 2.0,
            kit_x_u,
            kit_y_u,
        )

    if rack_socket_floor_z <= 0.0:
        raise ValueError("rack socket floors are not above the storey below")
    print(f"   rack socket floors: {rack_socket_floor_z:.1f} mm over the storey below")

    return seats


# ============================================================
# EXPORT
# ============================================================

exploded_lift = 60.0


def main():
    out_dir = _here.parent
    dock, storeys, parts = build_kit()
    contents = build_contents(parts)
    tools = build_tool_references()
    seats = validate(dock, storeys, parts, contents, tools)

    _kit.export_parts(out_dir, parts)

    references = kit_references(contents, tools)
    _kit.export_kit(
        out_dir,
        "harness-kit",
        _kit.kit_assembly("harness-kit", dock, storeys, seats, references),
    )
    _kit.export_kit(
        out_dir,
        "harness-kit-open",
        _kit.kit_assembly(
            "harness-kit-open",
            dock,
            storeys,
            _kit.exploded_seats(seats, exploded_lift),
            references,
        ),
    )

    printed_height = seats[-1] + rack_top_z
    populated_height = seats[-1] + rack_socket_floor_z + tool_stand_clear + preciva_length
    tallest = max(_kit.bbox(shape).zlen for shape in parts.values())
    envelopes = {
        f"{_figure_key(name)}_ENVELOPE": _kit.size_text(shape)
        for name, shape in parts.items()
    }
    compartments = {}
    for storey in bin_storeys:
        key = _figure_key(storey.name)
        compartments[f"{key}_CELL"] = (
            f"{storey.cell_x:.1f} mm x {storey.cell_y:.1f} mm"
        )
        compartments[f"{key}_HEIGHT"] = f"{storey.height_u}U"
    substitute_md(
        out_dir / "README.md",
        variables={
            **envelopes,
            "FOOTPRINT": f"{kit_x_u * _kit.grid_unit:.0f} mm x {kit_y_u * _kit.grid_unit:.0f} mm",
            "PRINTED_HEIGHT": f"{printed_height:.1f} mm",
            "POPULATED_HEIGHT": f"{populated_height:.1f} mm",
            "TALLEST_PART": f"{tallest:.1f} mm",
            "H2C_ENVELOPE": (
                f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x {_kit.h2c_build_z:.0f} mm"
            ),
            "HEAP_PACKING": f"{heap_packing:.2f}",
            "HEAP_CLEAR": f"{heap_wall_clear:.1f} mm",
            **compartments,
            "RACK_HEIGHT": f"{rack_height_u}U",
            "SOCKET_CLEAR": f"{rack_socket_clear:.1f} mm",
            "SOCKET_DEPTH": f"{rack_top_z - rack_socket_floor_z:.1f} mm",
            "SOCKET_FLOOR": f"{rack_socket_floor_z:.0f} mm",
            "DIVIDER_WALL": f"{_kit.divider_thickness:.1f} mm",
            "FERRULE_22AWG": _ferrule_text(0.34),
            "FERRULE_16AWG": _ferrule_text(1.5),
            "TIE_NARROW_WIDTH": f"{tie_narrow_width:.1f} mm",
            "TIE_WIDE_WIDTH": f"{tie_wide_width:.1f} mm",
            "TIE_THICKNESS": (
                f"{tie_narrow_thickness:.1f} mm and {tie_wide_thickness:.1f} mm"
            ),
            "PRECIVA_ENVELOPE": f"{preciva_length:.0f} x {preciva_head_width:.0f} mm",
            "HAISSTRONICA_ENVELOPE": (
                f"{haisstronica_length:.1f} x {haisstronica_head_width:.1f} mm"
            ),
            "KLEIN_LENGTH": f"{klein_length:.1f} mm",
            "KATA_LENGTH": f"{kata_length:.0f} mm",
            "WAGO_413": _wago_text("413"),
            "WAGO_415": _wago_text("415"),
            "WAGO_420": _wago_text("420"),
            "SHRINK_CUT": f"{shrink_cut_length:.1f} mm",
            "TIE_6_LENGTH": f"{tie_6in_length:.1f} mm",
            "TIE_8_LENGTH": f"{tie_8in_length:.1f} mm",
            "WIRE_KIT_PACKAGE": "317 x 184 x 77 mm",
        },
    )
    print("-> README.md")


def _figure_key(part_name):
    return part_name.split("-")[1].upper()


def _wago_text(size):
    entry = wago_221.SIZES[size]
    return f"{entry['width']} x {entry['depth']} x {entry['height']} mm"


def _ferrule_text(section):
    collar_d, total_l, _barrel_d, _barrel_l = ferrule_geometry[section]
    return f"collar {collar_d} mm over {total_l} mm"


if __name__ == "__main__":
    main()
