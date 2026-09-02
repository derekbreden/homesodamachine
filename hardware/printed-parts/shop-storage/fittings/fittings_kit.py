"""Fittings job kit: the plastic tube and fittings bench on one Gridfinity footprint.

Frame: world +Z is up, world +Y is the operator-facing front, and world +X is the
operator's right. Every storey is a stock `cq-gridfinity` body built with its bottom at
Z=0, and `_kit.stack_seats` places it on the storey below. Five divided labelled bins
carry the stock; a job rack closes the column.

A compartment's contents are one fill block whose volume is the pack count times the
piece's public bounding envelope, spread over the compartment's floor, and one witness
piece — the compartment's longest — resting in that fill. Each storey is as many height
units tall as its deepest fill needs.
"""

import re
import sys
from pathlib import Path

import cadquery as cq
from cqgridfinity import GridfinityBox
from cqgridfinity.constants import GR_BASE_HEIGHT, GR_DIV_WALL

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import _kit
from _kit import substitute_md


# ============================================================
# FOOTPRINT, COMPARTMENT DEPTH AND THE FILL MODEL
# ============================================================

footprint_x_u = 3
footprint_y_u = 3


def _box(height_u, length_div=0, width_div=0):
    return GridfinityBox(
        footprint_x_u, footprint_y_u, height_u,
        length_div=length_div, width_div=width_div, labels=True,
    )


#: A bin's interior floor: the Gridfinity base plus the library's own floor.
bin_floor_z = _box(1).floor_h + GR_BASE_HEIGHT

#: The library rounds a compartment's floor into its walls at this radius, so a content
#: standing on that floor has to clear the fillet before it clears the wall.
interior_fillet = _box(1).safe_fillet_rad

#: Kept between a modelled content and every wall, divider and label ledge around it.
content_clearance = max(1.0, interior_fillet)

content_corner_radius = 4.0

#: A fitting's body is round, so its envelope is drawn with this much of its narrow face
#: taken off each vertical corner — enough that it reads as a fitting, not as a brick.
piece_corner_ratio = 0.24


def label_ledge_drop(height_u):
    """How far the library's label ledge hangs into the +Y end of a compartment. A fill
    block stops below it rather than under it, so no content reaches past its lip. The
    ledge on the +Y wall is the deeper of the two the library draws, and every
    compartment is sized to it."""
    return _box(height_u).safe_label_height(backwall=True)


def fill_depth(height_u):
    """How deep a fill block may stand in a bin `height_u` units tall."""
    return (
        _kit.top_reference_z(height_u)
        - bin_floor_z
        - label_ledge_drop(height_u)
        - content_clearance
    )


#: The deepest a fill may stand as a fraction of its compartment, so a pack that grows
#: a little still closes its storey.
compartment_fill_limit = 0.95


def cell_span(length_div, width_div):
    """One compartment's inside length and width, the library's own division formula."""
    probe = _box(1)
    return (
        (probe.inner_l - GR_DIV_WALL * length_div) / (length_div + 1),
        (probe.inner_w - GR_DIV_WALL * width_div) / (width_div + 1),
    )


def cell_floor_area(length_div, width_div):
    span_x, span_y = cell_span(length_div, width_div)
    return (span_x - 2.0 * content_clearance) * (span_y - 2.0 * content_clearance)


# ============================================================
# THE STOCK AND ITS PUBLIC ENVELOPES
# ============================================================

class Piece:
    """One stocked thing: its public bounding envelope, in the pose it is stored in,
    and how many of it the shop holds."""

    def __init__(self, key, name, count, length, width, height, color):
        self.key = key
        self.name = name
        self.count = count
        self.length = length
        self.width = width
        self.height = height
        self.color = color

    @property
    def envelope_volume(self):
        return self.length * self.width * self.height

    @property
    def bulk_volume(self):
        return self.count * self.envelope_volume

    @property
    def longest(self):
        return max(self.length, self.width, self.height)

    def lying(self):
        """The piece flat, its long axis along the compartment's own long axis."""
        return (self.length, self.width, self.height)

    def across(self):
        return (self.width, self.length, self.height)

    def standing(self):
        return (self.width, self.height, self.length)


# A content is drawn a shade up from the PETG black of the kit around it, so a black
# polypropylene fitting inside a black bin still reads in a picture.
jg_black = cq.Color(0.32, 0.33, 0.37)
acetal_grey = cq.Color(0.52, 0.53, 0.55)
white_pp = cq.Color(0.86, 0.86, 0.83)
stainless = cq.Color(0.66, 0.68, 0.70)
brass = cq.Color(0.74, 0.60, 0.30)
aluminium = cq.Color(0.78, 0.79, 0.80)
tool_black = cq.Color(0.28, 0.29, 0.32)
nickel_tape = cq.Color(0.80, 0.81, 0.82)

PP0208E = Piece("PP0208E", "John Guest PP0208E union tee", 30, 39.1, 16.3, 29.2, jg_black)
PP0308E = Piece("PP0308E", "John Guest PP0308E union elbow", 40, 28.5, 16.3, 28.5, jg_black)
PP2308E = Piece("PP2308E", "John Guest PP2308E two-way divider", 20, 35.7, 16.3, 31.2, jg_black)
PP1208E = Piece("PP1208E", "John Guest PP1208E bulkhead union", 10, 34.6, 22.9, 22.9, jg_black)
PI1208S = Piece("PI1208S", "John Guest PI1208S bulkhead union", 2, 34.9, 22.2, 22.2, acetal_grey)
PI010822S = Piece("PI010822S", "John Guest PI010822S male connector", 10, 38.0, 20.0, 20.0, acetal_grey)
PP010822E = Piece("PP010822E", "John Guest PP010822E male connector", 10, 24.3, 18.9, 18.9, jg_black)
PP010821WP = Piece("PP010821WP", "John Guest PP010821WP male connector", 10, 25.4, 19.1, 19.1, white_pp)
PP450822E = Piece("PP450822E", "John Guest PP450822E female adapter", 10, 32.2, 24.0, 24.0, jg_black)
PP061208W = Piece("PP061208W", "John Guest PP061208W reducer stem", 10, 38.1, 15.9, 15.9, white_pp)
PI4512F6S = Piece("PI4512F6S", "John Guest PI4512F6S flare adapter", 10, 38.1, 22.2, 22.2, acetal_grey)
MI4508F4SLF = Piece("MI4508F4SLF", "John Guest MI4508F4SLF brass flare connector", 10, 45.0, 18.0, 18.0, brass)

ABU44E = Piece("ABU44E", "neoFit ABU44-E acetal bulkhead", 10, 40.0, 26.0, 26.0, jg_black)
PURESEC = Piece("PURESEC", "PureSec elbow bulkhead", 5, 45.0, 30.0, 30.0, white_pp)
TAILONZ = Piece("TAILONZ", "TAILONZ 1/4 x 1/8 NPT male connector", 10, 34.0, 16.0, 16.0, jg_black)
MALIDA = Piece("MALIDA", "MALIDA 1/8 NPT elbows and straights", 10, 35.0, 32.0, 18.0, jg_black)
DERPIPE = Piece("DERPIPE", "DERPIPE 5/16 x 1/4 NPT male connector", 5, 40.0, 20.0, 20.0, jg_black)
NEOFIT_BALL = Piece("NEOFIT_BALL", "NeoFit push-fit ball valve", 5, 50.8, 20.3, 33.0, white_pp)

GASHER = Piece("GASHER", "GASHER 1/4 NPT check valve", 6, 60.0, 26.0, 26.0, stainless)
CHILLWAVES_SPLIT = Piece("CHILLWAVES_SPLIT", "ChillWaves split check valve", 1, 65.0, 26.0, 26.0, stainless)
CHILLWAVES_SIAMESE = Piece("CHILLWAVES_SIAMESE", "ChillWaves siamese check valve", 1, 65.0, 26.0, 26.0, stainless)
LTW_BARB = Piece("LTW_BARB", "LTWFITTING 316 SS 1/4 barb adapter", 5, 50.0, 16.0, 16.0, stainless)
MAACFLOW = Piece("MAACFLOW", "MAACFLOW 3/8 barb adapter", 4, 50.0, 18.0, 18.0, stainless)
TAISHER = Piece("TAISHER", "TAISHER 316L street elbow", 4, 40.0, 40.0, 22.0, stainless)
GAGIRA = Piece("GAGIRA", "GAGIRA 316L reducing coupling", 5, 35.0, 25.0, 25.0, stainless)
LTW_COUPLING = Piece("LTW_COUPLING", "LTWFITTING brass reducing coupling", 5, 32.0, 24.0, 24.0, brass)
SV125 = Piece("SV125", "Control Devices SV-125 relief valve", 1, 65.0, 30.0, 22.0, brass)
WR1110 = Piece("WR1110", "Interstate Pneumatics WR1110 regulator", 1, 90.0, 32.0, 32.0, aluminium)

WC316SS = Piece("WC316SS", "WC-316SS-06 SAE #6 hose clamp", 10, 34.0, 26.0, 16.0, stainless)
YDS = Piece("YDS", "YDS 10-16 mm hose clamp", 10, 42.0, 25.0, 20.0, stainless)
SIPTENK = Piece("SIPTENK", "Siptenk 1/4 tube stiffener", 100, 15.0, 7.0, 7.0, brass)

MUDDER = Piece("MUDDER", "Mudder tubing cutter", 1, 24.0, 34.0, 80.0, tool_black)
MILLROSE_DIAMETER = 53.0
MILLROSE_THICKNESS = 15.0


# ============================================================
# COMPARTMENTS AND STOREYS
# ============================================================

class Compartment:
    """One cell of a divided bin and the pieces it holds."""

    def __init__(self, label, pieces):
        self.label = label
        self.pieces = pieces

    @property
    def volume(self):
        return sum(piece.bulk_volume for piece in self.pieces)

    @property
    def witness(self):
        """The piece whose fit the compartment's size actually turns on."""
        return max(self.pieces, key=lambda piece: piece.longest)


class BinStorey:
    """A divided labelled bin, as many height units tall as its deepest fill needs."""

    def __init__(self, name, length_div, width_div, compartments):
        self.name = name
        self.length_div = length_div
        self.width_div = width_div
        self.compartments = compartments
        self.span_x, self.span_y = cell_span(length_div, width_div)
        self.floor_area = cell_floor_area(length_div, width_div)
        self.height_u = self._height_u()
        self.shape = _kit.bin_body(
            footprint_x_u,
            footprint_y_u,
            self.height_u,
            length_div=length_div,
            width_div=width_div,
            labels=True,
        )
        self.cells = _cells(self.shape, self.height_u)
        self.storey = _kit.Storey(name, self.shape, self.height_u, kind="bin")

    def _height_u(self):
        """The shortest storey whose compartments take their fills at the fill limit."""
        deepest = (
            max(c.volume for c in self.compartments)
            / self.floor_area
            / compartment_fill_limit
        )
        height_u = 1
        while fill_depth(height_u) < deepest:
            height_u += 1
        return height_u

    @property
    def depth(self):
        return fill_depth(self.height_u)


def _cells(bin_shape, height_u):
    """Every compartment void of a divided bin, front row first, left to right."""
    cavity = _kit.bin_cavity(bin_shape, footprint_x_u, footprint_y_u, height_u)
    solids = cavity.solids().vals()
    solids.sort(key=lambda s: (-round(s.BoundingBox().center.y, 1),
                               round(s.BoundingBox().center.x, 1)))
    return [cq.Workplane(obj=s) for s in solids]


def build_storeys():
    """The five bins, bottom to top: the metal first because it is the heaviest, and
    the manifold's junctions last because the job reaches for them most."""
    return [
        BinStorey("fittings-npt", 1, 1, [
            Compartment("check valves",
                        [GASHER, CHILLWAVES_SPLIT, CHILLWAVES_SIAMESE]),
            Compartment("reducing couplings and street elbows",
                        [GAGIRA, LTW_COUPLING, TAISHER]),
            Compartment("barb and flare connectors",
                        [LTW_BARB, MAACFLOW, MI4508F4SLF]),
            Compartment("regulator and relief valve", [WR1110, SV125]),
        ]),
        BinStorey("fittings-bulkheads", 1, 1, [
            Compartment("John Guest bulkhead unions", [PP1208E, PI1208S]),
            Compartment("neoFit acetal bulkheads", [ABU44E]),
            Compartment("PureSec elbow bulkheads", [PURESEC]),
            Compartment("ball valves", [NEOFIT_BALL]),
        ]),
        BinStorey("fittings-stock", 1, 0, [
            Compartment("two-way dividers", [PP2308E]),
            Compartment("hose clamps and tube stiffeners", [YDS, WC316SS, SIPTENK]),
        ]),
        BinStorey("fittings-adapters", 1, 1, [
            Compartment("male connectors", [PI010822S, PP010822E, PP010821WP]),
            Compartment("female adapters", [PP450822E]),
            Compartment("flare adapters and reducer stems", [PI4512F6S, PP061208W]),
            Compartment("pneumatic push-fit", [MALIDA, TAILONZ, DERPIPE]),
        ]),
        BinStorey("fittings-junctions", 1, 0, [
            Compartment("union tees", [PP0208E]),
            Compartment("union elbows", [PP0308E]),
        ]),
    ]


# ============================================================
# CONTENT REFERENCES
# ============================================================

def cell_place(cell):
    """The rectangle a content may stand on inside one compartment, and its floor."""
    b = _kit.bbox(cell)
    return (
        b.xlen - 2.0 * content_clearance,
        b.ylen - 2.0 * content_clearance,
        b.center.x,
        b.center.y,
        b.zmin,
    )


def fill_block(cell, volume):
    """The pack's loose fill, spread over its compartment's floor."""
    width, depth, center_x, center_y, floor_z = cell_place(cell)
    return _kit.placed_prism(
        width,
        depth,
        volume / (width * depth),
        center_x,
        center_y,
        z_bottom=floor_z,
        radius=content_corner_radius,
    )


def witness_pose(piece, width, depth, standing_room):
    """The first pose the compartment takes the piece in: flat along its long axis,
    flat across it, or stood on end."""
    for pose in (piece.lying(), piece.across(), piece.standing()):
        if pose[0] <= width and pose[1] <= depth and pose[2] <= standing_room:
            return pose
    raise ValueError(
        f"{piece.name}: {piece.length:.0f} x {piece.width:.0f} x {piece.height:.0f} mm "
        f"lies in no pose inside a {width:.0f} x {depth:.0f} x {standing_room:.0f} mm "
        "compartment"
    )


def witness_block(compartment, cell, storey_depth):
    """The compartment's longest piece, resting on the fill or sunk in it."""
    piece = compartment.witness
    width, depth, center_x, center_y, floor_z = cell_place(cell)
    pose = witness_pose(piece, width, depth, storey_depth)
    fill_top = compartment.volume / (width * depth)
    rest_z = floor_z + min(fill_top, storey_depth - pose[2])
    return piece, _kit.placed_prism(
        pose[0], pose[1], pose[2], center_x, center_y,
        z_bottom=rest_z, radius=min(pose[0], pose[1]) * piece_corner_ratio,
    )


def storey_references(storey):
    """(name, shape, colour, cell) for every modelled content of one bin."""
    references = []
    for compartment, cell in zip(storey.compartments, storey.cells):
        references.append((
            f"{compartment.label} fill",
            fill_block(cell, compartment.volume),
            compartment.pieces[0].color,
            cell,
        ))
        piece, block = witness_block(compartment, cell, storey.depth)
        references.append((piece.name, block, piece.color, cell))
    return references


# ============================================================
# THE JOB RACK
# ============================================================

rack_height_u = 8
rack_top_z = _kit.top_reference_z(rack_height_u)
rack_plateau_half = _kit.plateau_half(footprint_x_u)

socket_clearance = 2.5

cutter_socket_width = MUDDER.length + 2.0 * socket_clearance
cutter_socket_depth = MUDDER.width + 2.0 * socket_clearance
cutter_socket_x = -38.0
cutter_socket_y = -33.0
cutter_socket_floor_z = 8.0

tape_well_diameter = MILLROSE_DIAMETER + 2.0 * socket_clearance
tape_well_center_x = 30.0
tape_well_center_y = 28.5
tape_well_lip = 7.0
tape_well_floor_z = rack_top_z - (MILLROSE_THICKNESS + tape_well_lip)

play_well_width = 64.0
play_well_depth = 44.0
play_well_x = 22.0
play_well_y = -33.0
play_well_floor_z = 26.0


def build_rack():
    """A solid lipped blank cut with the cutter's socket, two tape wells and a work well."""
    rack = _kit.blank_body(footprint_x_u, footprint_y_u, rack_height_u)
    rack = rack.cut(_kit.pocket(
        cutter_socket_width, cutter_socket_depth,
        cutter_socket_x, cutter_socket_y,
        cutter_socket_floor_z, rack_top_z, radius=4.0,
    ))
    for x in (-tape_well_center_x, tape_well_center_x):
        rack = rack.cut(_kit.round_pocket(
            tape_well_diameter, x, tape_well_center_y, tape_well_floor_z, rack_top_z
        ))
    rack = rack.cut(_kit.pocket(
        play_well_width, play_well_depth,
        play_well_x, play_well_y,
        play_well_floor_z, rack_top_z, radius=6.0,
    ))
    return rack.clean()


def rack_references():
    cutter = _kit.placed_prism(
        MUDDER.length, MUDDER.width, MUDDER.height,
        cutter_socket_x, cutter_socket_y,
        z_bottom=cutter_socket_floor_z + content_clearance, radius=5.0,
    )
    rolls = [
        (f"Millrose 70894 roll {index + 1}",
         _kit.cylinder(MILLROSE_DIAMETER, MILLROSE_THICKNESS, x, tape_well_center_y,
                       tape_well_floor_z + content_clearance),
         nickel_tape)
        for index, x in enumerate((-tape_well_center_x, tape_well_center_x))
    ]
    play = _kit.placed_prism(
        play_well_width - 2.0 * content_clearance,
        play_well_depth - 2.0 * content_clearance,
        rack_top_z - play_well_floor_z - content_clearance,
        play_well_x, play_well_y,
        z_bottom=play_well_floor_z + content_clearance,
        radius=content_corner_radius,
    )
    return [("Mudder tubing cutter", cutter, tool_black)] + rolls + [
        ("fittings in play", play, jg_black)
    ]


def assert_sockets_on_plateau():
    """Every socket opens inside the lip ring, so nothing is cut through the rack's side."""
    reach = max(
        abs(cutter_socket_x) + cutter_socket_width / 2.0,
        abs(cutter_socket_y) + cutter_socket_depth / 2.0,
        tape_well_center_x + tape_well_diameter / 2.0,
        tape_well_center_y + tape_well_diameter / 2.0,
        abs(play_well_x) + play_well_width / 2.0,
        abs(play_well_y) + play_well_depth / 2.0,
    )
    if reach > rack_plateau_half:
        raise ValueError(
            f"rack sockets reach {reach:.1f} mm, past the "
            f"{rack_plateau_half:.1f} mm plateau"
        )
    print(f"   rack sockets: {reach:.1f} of {rack_plateau_half:.1f} mm plateau")


# ============================================================
# VALIDATION
# ============================================================

def validate(parts, storeys, rack_witnesses):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    bodies = [s.storey for s in storeys] + [
        _kit.Storey("fittings-rack", parts["fittings-rack"], rack_height_u, kind="blank")
    ]
    seats = _kit.stack_seats(bodies)
    _kit.assert_stack_seated(parts["fittings-dock"], bodies, seats)

    for storey in storeys:
        if len(storey.compartments) != len(storey.cells):
            raise ValueError(
                f"{storey.name}: {len(storey.compartments)} compartments in "
                f"{len(storey.cells)} cells"
            )
        for name, shape, _, cell in storey_references(storey):
            _kit.assert_contained(f"{storey.name}: {name}", shape, cell)

    assert_sockets_on_plateau()
    for name, shape, _ in rack_witnesses:
        _kit.assert_clear(name, parts["fittings-rack"], shape)
    return bodies, seats


def report_fills(storeys):
    print("Compartment fills")
    for storey in storeys:
        for compartment, cell in zip(storey.compartments, storey.cells):
            width, depth, _, _, _ = cell_place(cell)
            height = compartment.volume / (width * depth)
            print(f"   {storey.name}/{compartment.label}: "
                  f"{compartment.volume / 1000.0:.0f} cm^3, "
                  f"{height:.0f} of {storey.depth:.0f} mm")


# ============================================================
# ASSEMBLY AND EXPORT
# ============================================================

exploded_lift = 80.0


def main():
    out_dir = Path(__file__).resolve().parent
    storeys = build_storeys()

    parts = {storey.name: storey.shape for storey in storeys}
    parts["fittings-rack"] = build_rack()
    parts["fittings-dock"] = _kit.dock_body(footprint_x_u, footprint_y_u)

    rack_witnesses = rack_references()
    bodies, seats = validate(parts, storeys, rack_witnesses)
    report_fills(storeys)

    references = []
    for index, storey in enumerate(storeys):
        references += [(f"{storey.name}-{name}", shape, color, index)
                       for name, shape, color, _ in storey_references(storey)]
    references += [(name, shape, color, len(storeys))
                   for name, shape, color in rack_witnesses]

    _kit.export_parts(out_dir, parts)
    _kit.export_kit(out_dir, "fittings-kit", _kit.kit_assembly(
        "fittings-kit", parts["fittings-dock"], bodies, seats, references))
    _kit.export_kit(out_dir, "fittings-kit-open", _kit.kit_assembly(
        "fittings-kit-open", parts["fittings-dock"], bodies,
        _kit.exploded_seats(seats, exploded_lift), references))

    variables = figures(storeys, parts, seats)
    assert_markers_owned(out_dir / "README.md", variables)
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


def assert_markers_owned(readme, variables):
    """Every [value](NAME) in the README's prose is a figure this generator writes.

    The `## Sources` block docgen maintains at the end carries the marker syntax itself,
    so the scan stops at it."""
    prose = readme.read_text().split("\n## Sources", 1)[0]
    names = set(re.findall(r"\]\(([A-Z_][A-Z0-9_]*)\)", prose))
    orphans = sorted(names - set(variables))
    if orphans:
        raise ValueError(f"README markers no figure owns: {', '.join(orphans)}")
    print(f"   README markers: {len(names)} owned")


def figures(storeys, parts, seats):
    printed_height = seats[-1] + _kit.bbox(parts["fittings-rack"]).zlen
    populated_height = (
        seats[-1] + cutter_socket_floor_z + content_clearance + MUDDER.height
    )
    stock_volume = sum(c.volume for s in storeys for c in s.compartments)
    tallest = max(_kit.bbox(shape).zlen for shape in parts.values())
    variables = {
        "FOOTPRINT": f"{footprint_x_u * _kit.grid_unit:.0f} mm x "
                     f"{footprint_y_u * _kit.grid_unit:.0f} mm",
        "PRINTED_HEIGHT": f"{printed_height:.1f} mm",
        "POPULATED_HEIGHT": f"{populated_height:.1f} mm",
        "STOCK_VOLUME": f"{stock_volume / 1e6:.1f} litres",
        "COMPARTMENTS": f"{sum(len(s.compartments) for s in storeys)}",
        "FOOTPRINT_AREA": f"{_box(1).inner_l * _box(1).inner_w:,.0f} mm^2",
        "CONTENT_CLEARANCE": f"{content_clearance:.0f} mm",
        "H2C_ENVELOPE": f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x "
                        f"{_kit.h2c_build_z:.0f} mm",
        "TALLEST_PART": f"{tallest:.1f} mm",
        "LEDGE_DROP": f"{label_ledge_drop(storeys[0].height_u):.1f} mm",
        "FILL_LIMIT": f"{compartment_fill_limit * 100:.0f} %",
        "CUTTER_SOCKET": f"{cutter_socket_width:.0f} x {cutter_socket_depth:.0f} mm",
        "CUTTER_SOCKET_DEPTH": f"{rack_top_z - cutter_socket_floor_z:.0f} mm",
        "TAPE_WELL": f"{tape_well_diameter:.0f} mm",
        "PLAY_WELL": f"{play_well_width:.0f} x {play_well_depth:.0f} x "
                     f"{rack_top_z - play_well_floor_z:.0f} mm",
        "RACK_HEIGHT": f"{rack_top_z:.0f} mm",
        "MILLROSE_ENV": f"{MILLROSE_DIAMETER:.0f} mm diameter x "
                        f"{MILLROSE_THICKNESS:.0f} mm",
    }
    for storey in storeys:
        stem = storey.name.upper().replace("-", "_")
        variables[stem + "_H"] = f"{storey.height_u * _kit.height_unit:.0f} mm"
        variables[stem + "_CELL"] = (
            f"{storey.span_x:.0f} mm x {storey.span_y:.0f} mm x {storey.depth:.0f} mm"
        )
        variables[stem + "_ENV"] = _kit.size_text(storey.shape)
        for compartment, cell in zip(storey.compartments, storey.cells):
            width, depth, _, _, _ = cell_place(cell)
            key = _marker(compartment.label)
            variables[key + "_FILL"] = f"{compartment.volume / 1000.0:.0f} cm3"
            variables[key + "_DEPTH"] = (
                f"{compartment.volume / (width * depth):.0f} mm"
            )
    for shape_name in ("fittings-rack", "fittings-dock"):
        variables[shape_name.upper().replace("-", "_") + "_ENV"] = _kit.size_text(
            parts[shape_name]
        )
    for piece in _every_piece(storeys) + [MUDDER]:
        variables[piece.key + "_ENV"] = (
            f"{piece.length:.1f} x {piece.width:.1f} x {piece.height:.1f} mm"
        )
        variables[piece.key + "_N"] = f"{piece.count}"
    return variables


def _marker(label):
    return "".join(
        character if character.isalnum() else "_" for character in label.upper()
    )


def _every_piece(storeys):
    seen = []
    for storey in storeys:
        for compartment in storey.compartments:
            for piece in compartment.pieces:
                if piece not in seen:
                    seen.append(piece)
    return seen


if __name__ == "__main__":
    main()
