"""Solder kit — the solder and heat-set bench on one 3 x 3 Gridfinity footprint.

Frame: world +Z is up, world +Y is the operator-facing front, and world +X is
the operator's right.  Every storey is built in its own print orientation with
its bottom at Z = 0; the kit frame seats each storey on the one below.

A job stack: two divided bins under a job rack whose plateau is a tip index.
The bins carry the bench's consumables and unstack onto the mat; the rack
stands the twenty T18 tips point-up beside the tools that share the bench.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
from cqgridfinity.constants import GR_BOT_H, GR_DIV_WALL, GR_WALL

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from _kit import (  # noqa: E402
    Storey,
    assert_clear,
    assert_contained,
    assert_h2c_fit,
    assert_one_solid,
    assert_stack_seated,
    bbox,
    bin_body,
    bin_cavity,
    blank_body,
    cylinder,
    dock_body,
    export_kit,
    export_parts,
    exploded_seats,
    grid_unit,
    h2c_build_x,
    h2c_build_y,
    h2c_build_z,
    kit_assembly,
    outer_size,
    placed_prism,
    plateau_half,
    pocket,
    round_pocket,
    stack_seats,
    substitute_md,
    top_reference_z,
)


# ============================================================
# FOOTPRINT AND STOREYS
# ============================================================

kit_units_x = 3
kit_units_y = 3
footprint_x = kit_units_x * grid_unit
footprint_y = kit_units_y * grid_unit

stock_storey_u = 12
rework_storey_u = 7
rack_u = 6


# ============================================================
# BIN CELLS
# ============================================================

#: A divided bin's void, in the storey's own frame: the library's floor at
#: GR_BOT_H, its walls GR_WALL in from the outside, and one divider GR_DIV_WALL
#: wide on the storey's centre line.
cavity_floor_z = GR_BOT_H
cavity_half_span = outer_size(kit_units_x) / 2.0 - GR_WALL
cell_width = (2.0 * cavity_half_span - GR_DIV_WALL) / 2.0
cell_center_x = GR_DIV_WALL / 2.0 + cell_width / 2.0

#: The vertical fillet the library rounds every interior corner with. A thing
#: as wide as its cell only clears where the cell runs at full width, past it.
cell_corner_radius = 4.0

#: The fillet the library rolls into the join of a cell's floor and its walls.
cell_floor_fillet = 1.1

stock_cavity_top_z = top_reference_z(stock_storey_u)
rework_cavity_top_z = top_reference_z(rework_storey_u)

#: What a stored thing keeps to the wall or divider beside it, and the margin
#: the fit checks grow its envelope by before asking whether it is contained.
content_margin = 1.0
content_clearance = 1.0

#: The longest thing a cell of this kit holds: its own diagonal, less a
#: content margin at every wall.
cell_diagonal = (
    (cell_width - 2.0 * content_margin) ** 2
    + (2.0 * cavity_half_span - 2.0 * content_margin) ** 2
) ** 0.5


#: What a thing standing on a cell floor keeps to the wall behind it: its own
#: margin, the millimetre the fit check grows it by, and the floor fillet.
floor_standoff = content_margin + content_clearance + cell_floor_fillet


def cell_back_y(depth):
    """The centre of a thing `depth` deep pushed to the -Y end of a cell."""
    return -cavity_half_span + floor_standoff + depth / 2.0


def next_y(front_y, depth):
    """The centre of a thing `depth` deep set in front of something ending at `front_y`."""
    return front_y + content_margin + depth / 2.0


# ============================================================
# JOB RACK: THE TIP INDEX
# ============================================================

rack_plateau_z = top_reference_z(rack_u)
rack_reach = plateau_half(kit_units_x)

#: A tool socket is loose: this much larger than the tool's envelope per side.
socket_clearance = 2.5

tip_socket_bore = 11.0
tip_socket_floor_z = 20.0
tip_socket_pitch = 14.0
tip_index_columns = 5
tip_index_rows = 4
tip_index_center_x = -22.0
tip_index_center_y = 31.0

tip_socket_columns_x = tuple(
    tip_index_center_x + (column - (tip_index_columns - 1) / 2.0) * tip_socket_pitch
    for column in range(tip_index_columns)
)
tip_socket_rows_y = tuple(
    tip_index_center_y + ((tip_index_rows - 1) / 2.0 - row) * tip_socket_pitch
    for row in range(tip_index_rows)
)

#: The twenty tips the index holds, front row first and left to right in each
#: row: the seven heat-set insert tips, the three genuine Hakko chisels, then
#: the VECO-T assortment across the two back rows.
tip_index_roster = (
    ("M2 insert", "insert"),
    ("M2.5 insert", "insert"),
    ("M3 insert", "insert"),
    ("M4 insert", "insert"),
    ("M5 insert", "insert"),
    ("M6 insert", "insert"),
    ("M8 insert", "insert"),
    ("T18-D08", "hakko"),
    ("T18-D12", "hakko"),
    ("T18-D16", "hakko"),
    ("T18-LB", "veco"),
    ("T18-BR02", "veco"),
    ("T18-D16 (VECO-T)", "veco"),
    ("T18-D32", "veco"),
    ("T18-B", "veco"),
    ("T18-K", "veco"),
    ("T18-C2", "veco"),
    ("T18-C5", "veco"),
    ("T18-I", "veco"),
    ("T18-S3", "veco"),
)

tip_socket_centers = tuple(
    (x, y) for y in tip_socket_rows_y for x in tip_socket_columns_x
)


# ============================================================
# JOB RACK: THE TOOL SOCKETS
# ============================================================

heat_gun_well_floor_z = 7.0
heat_gun_well_x = -27.0
heat_gun_well_y = -28.0

brush_quiver_floor_z = 7.0
brush_quiver_x = 33.0
brush_quiver_y = -31.0

tweezer_slot_width = 10.5
tweezer_slot_depth = 5.2
tweezer_slot_floor_z = 15.0
tweezer_slot_y = 50.0
tweezer_slot_centers_x = (25.0, 38.0, 51.0)

cutter_socket_width = 22.0
cutter_socket_depth = 14.0
cutter_socket_floor_z = 12.0
cutter_socket_x = 38.0
cutter_socket_y = 27.0


# ============================================================
# PUBLIC ENVELOPES: WHAT THE RACK HOLDS
# ============================================================

#: A T18 tip is the 900M-T format: a 6.5 mm barrel 40 to 44 mm long, carrying
#: the working face the tip's own name gives — 14.5 mm of it on every chisel.
t18_barrel_diameter = 6.5
t18_tip_length = 44.0
t18_working_length = 14.5
t18_working_diameter = 2.5
t18_barrel_length = t18_tip_length - t18_working_length

#: The seven heat-set insert tips ship in one 35 x 35 x 20 mm package, so
#: an 8 mm x 35 mm cylinder — half of a seventh of that box — is a generous tip.
insert_tip_package_length = 35.0
insert_tip_length = insert_tip_package_length
insert_tip_diameter = 8.0

tweezer_length = 127.0
tweezer_width = 8.0
tweezer_thickness = 3.0

cutter_length = 5.0 * 25.4
cutter_head_width = 17.0
cutter_head_thickness = 10.0

#: Thirty-six acid brushes, 6 in long on 3/8 in ferrules. Standing on end they
#: pack the way loose sticks do, filling about seven tenths of what they stand in.
flux_brush_count = 36
flux_brush_length = 6.0 * 25.4
flux_brush_ferrule_width = 25.4 * 3.0 / 8.0
flux_brush_ferrule_thickness = 3.0
flux_brush_packing_fraction = 0.7
flux_brush_bundle_diameter = (
    4.0
    * flux_brush_count
    * flux_brush_ferrule_width
    * flux_brush_ferrule_thickness
    / (math.pi * flux_brush_packing_fraction)
) ** 0.5

#: The QWORK gun's listing package, read as a barrel: nothing in the box is
#: fatter than the box's short side or longer than its long side.
heat_gun_length = 9.88 * 25.4
heat_gun_diameter = 2.05 * 25.4

heat_gun_well_diameter = heat_gun_diameter + 2.0 * socket_clearance
brush_quiver_diameter = flux_brush_bundle_diameter + 2.0 * socket_clearance

#: Every socket the rack cuts, as the half-span it takes in X and in Y. None of
#: them may reach past the plateau into the lip the storey above would seat on.
rack_socket_extents = (
    *(
        ("tip socket", x, y, tip_socket_bore / 2.0, tip_socket_bore / 2.0)
        for x, y in tip_socket_centers
    ),
    (
        "heat-gun well",
        heat_gun_well_x,
        heat_gun_well_y,
        heat_gun_well_diameter / 2.0,
        heat_gun_well_diameter / 2.0,
    ),
    (
        "brush quiver",
        brush_quiver_x,
        brush_quiver_y,
        brush_quiver_diameter / 2.0,
        brush_quiver_diameter / 2.0,
    ),
    *(
        (
            "tweezer slot",
            x,
            tweezer_slot_y,
            tweezer_slot_width / 2.0,
            tweezer_slot_depth / 2.0,
        )
        for x in tweezer_slot_centers_x
    ),
    (
        "cutter socket",
        cutter_socket_x,
        cutter_socket_y,
        cutter_socket_width / 2.0,
        cutter_socket_depth / 2.0,
    ),
)


# ============================================================
# PUBLIC ENVELOPES: WHAT THE BINS HOLD
# ============================================================

#: The Kester 1 lb roll's listing package, 2.5 x 2.3 x 2.3 in, read as a spool
#: lying on its rim with its axis front to back.
solder_spool_diameter = 2.3 * 25.4
solder_spool_width = 2.5 * 25.4

#: The pocket pack's 48 ft of 0.020 in wire is a 31 mm coil on a 25 mm core;
#: the pack that dispenses it gets a generous disc around that.
fine_solder_pack_diameter = 45.0
fine_solder_pack_height = 20.0

#: Soder-Wick on its ESD bobbin: the listing's 1.75 x 1.75 x 0.25 in.
braid_bobbin_diameter = 1.75 * 25.4
braid_bobbin_thickness = 0.25 * 25.4

#: Four polyimide rolls, 1/8, 1/4, 1/2 and 1 in wide. Each is 108 ft of 0.05 mm
#: film — 1646 mm^2 of wound section, a 52.4 mm roll on a 1 in core.
tape_roll_widths = (25.4, 12.7, 25.4 / 4.0, 25.4 / 8.0)
tape_roll_diameter = 56.0
tape_stack_height = sum(tape_roll_widths)

#: A 50 mL jar and a 30 mL squeeze bottle, generous: neither maker publishes a
#: size, and the listing gives only the fill.
flux_jar_diameter = 52.0
flux_jar_height = 45.0
flux_bottle_diameter = 32.0
flux_bottle_height = 75.0

#: Four 10 cc syringes, generous: the listing publishes the volume, not a size.
flux_syringe_diameter = 20.0
flux_syringe_length = 85.0
flux_syringe_columns = 2
flux_syringe_layers = 2

#: Left out of the kit: the 3M Virtua CCS's published frame width and the FAST
#: CHIP alloy's published piece length, both longer than a cell's diagonal. Laid
#: on the diagonal of an undivided cavity instead, the glasses would have to
#: fold to a depth 3M does not publish.
safety_glasses_frame_width = 138.0
removal_alloy_piece_length = 6.5 * 25.4
undivided_cavity_diagonal = (
    2.0 * cavity_half_span - 2.0 * content_margin
) * 2.0**0.5
safety_glasses_folded_depth_budget = (
    undivided_cavity_diagonal - safety_glasses_frame_width
)


# ============================================================
# CONTENT PLACEMENT
# ============================================================

solder_spool_x = -cell_center_x
solder_spool_y = (
    -cavity_half_span
    + cell_corner_radius
    + content_margin
    + content_clearance
    + solder_spool_width / 2.0
)

flux_bottle_x = -cell_center_x
flux_bottle_y = next_y(
    solder_spool_y + solder_spool_width / 2.0, flux_bottle_diameter
)

tape_stack_x = cell_center_x
tape_stack_y = cell_back_y(tape_roll_diameter)

flux_jar_x = cell_center_x
flux_jar_y = next_y(tape_stack_y + tape_roll_diameter / 2.0, flux_jar_diameter)

flux_syringe_x = -cell_center_x
flux_syringe_y = cell_back_y(flux_syringe_length)
flux_syringe_pitch = flux_syringe_diameter

fine_solder_x = cell_center_x
fine_solder_y = cell_back_y(fine_solder_pack_diameter)

braid_bobbin_x = cell_center_x
braid_bobbin_y = next_y(
    fine_solder_y + fine_solder_pack_diameter / 2.0, braid_bobbin_diameter
)


# ============================================================
# DISPLAY COLOURS
# ============================================================

copper_tip_color = cq.Color(0.72, 0.45, 0.20)
brass_tip_color = cq.Color(0.85, 0.72, 0.35)
steel_color = cq.Color(0.58, 0.60, 0.62)
tool_grip_color = cq.Color(0.10, 0.10, 0.12)
heat_gun_color = cq.Color(0.78, 0.12, 0.12)
brush_color = cq.Color(0.76, 0.58, 0.32)
solder_spool_color = cq.Color(0.66, 0.67, 0.70)
fine_solder_color = cq.Color(0.78, 0.24, 0.20)
braid_color = cq.Color(0.26, 0.54, 0.32)
tape_color = cq.Color(0.86, 0.45, 0.10)
flux_jar_color = cq.Color(0.20, 0.40, 0.70)
flux_bottle_color = cq.Color(0.95, 0.85, 0.35)
syringe_color = cq.Color(0.92, 0.93, 0.95)


# ============================================================
# PRINTED BODIES
# ============================================================

def build_stock_bin():
    """The bulk storey: one divider, a label ledge over each cell."""
    return bin_body(
        kit_units_x, kit_units_y, stock_storey_u, length_div=1, labels=True
    )


def build_rework_bin():
    """The fine-consumable storey, on the same divider and ledges."""
    return bin_body(
        kit_units_x, kit_units_y, rework_storey_u, length_div=1, labels=True
    )


def build_tip_rack():
    """A lipped blank with the tip index and the bench's tool sockets cut from
    its plateau. Every socket opens upward and nothing overhangs."""
    rack = blank_body(kit_units_x, kit_units_y, rack_u)

    for center_x, center_y in tip_socket_centers:
        rack = rack.cut(
            round_pocket(
                tip_socket_bore,
                center_x,
                center_y,
                tip_socket_floor_z,
                rack_plateau_z,
            )
        )

    rack = rack.cut(
        round_pocket(
            heat_gun_well_diameter,
            heat_gun_well_x,
            heat_gun_well_y,
            heat_gun_well_floor_z,
            rack_plateau_z,
        )
    )
    rack = rack.cut(
        round_pocket(
            brush_quiver_diameter,
            brush_quiver_x,
            brush_quiver_y,
            brush_quiver_floor_z,
            rack_plateau_z,
        )
    )

    for center_x in tweezer_slot_centers_x:
        rack = rack.cut(
            pocket(
                tweezer_slot_width,
                tweezer_slot_depth,
                center_x,
                tweezer_slot_y,
                tweezer_slot_floor_z,
                rack_plateau_z,
                radius=1.5,
            )
        )

    rack = rack.cut(
        pocket(
            cutter_socket_width,
            cutter_socket_depth,
            cutter_socket_x,
            cutter_socket_y,
            cutter_socket_floor_z,
            rack_plateau_z,
            radius=2.0,
        )
    )
    return rack.clean()


def build_dock():
    return dock_body(kit_units_x, kit_units_y)


# ============================================================
# FIT REFERENCES
# ============================================================

def build_solder_spool(clearance=0.0):
    """The 1 lb roll on its rim, axis front to back."""
    diameter = solder_spool_diameter + 2.0 * clearance
    return (
        cq.Workplane("XZ")
        .circle(diameter / 2.0)
        .extrude((solder_spool_width + 2.0 * clearance) / 2.0, both=True)
        .translate((solder_spool_x, solder_spool_y, cavity_floor_z + diameter / 2.0))
    )


def build_flux_bottle(clearance=0.0):
    return cylinder(
        flux_bottle_diameter + 2.0 * clearance,
        flux_bottle_height + clearance,
        flux_bottle_x,
        flux_bottle_y,
        cavity_floor_z,
    )


def build_tape_rolls(clearance=0.0):
    """Four rolls stacked widest first, on one axis."""
    if clearance:
        return cylinder(
            tape_roll_diameter + 2.0 * clearance,
            tape_stack_height + clearance,
            tape_stack_x,
            tape_stack_y,
            cavity_floor_z,
        )
    rolls = None
    z = cavity_floor_z
    for width in tape_roll_widths:
        roll = cylinder(tape_roll_diameter, width, tape_stack_x, tape_stack_y, z)
        rolls = roll if rolls is None else rolls.union(roll)
        z += width
    return rolls


def build_flux_jar(clearance=0.0):
    return cylinder(
        flux_jar_diameter + 2.0 * clearance,
        flux_jar_height + clearance,
        flux_jar_x,
        flux_jar_y,
        cavity_floor_z,
    )


def build_flux_syringes(clearance=0.0):
    """Four 10 cc barrels lying front to back, two across in two layers."""
    if clearance:
        return placed_prism(
            flux_syringe_columns * flux_syringe_pitch + 2.0 * clearance,
            flux_syringe_length + 2.0 * clearance,
            flux_syringe_layers * flux_syringe_diameter + clearance,
            flux_syringe_x,
            flux_syringe_y,
            z_bottom=cavity_floor_z,
            radius=2.0,
        )
    syringes = None
    for column in range(flux_syringe_columns):
        center_x = flux_syringe_x + (
            column - (flux_syringe_columns - 1) / 2.0
        ) * flux_syringe_pitch
        for layer in range(flux_syringe_layers):
            axis_z = (
                cavity_floor_z
                + flux_syringe_diameter / 2.0
                + layer * flux_syringe_diameter
            )
            barrel = (
                cq.Workplane("XZ")
                .circle(flux_syringe_diameter / 2.0)
                .extrude(flux_syringe_length / 2.0, both=True)
                .translate((center_x, flux_syringe_y, axis_z))
            )
            syringes = barrel if syringes is None else syringes.union(barrel)
    return syringes


def build_fine_solder_pack(clearance=0.0):
    return cylinder(
        fine_solder_pack_diameter + 2.0 * clearance,
        fine_solder_pack_height + clearance,
        fine_solder_x,
        fine_solder_y,
        cavity_floor_z,
    )


def build_braid_bobbin(clearance=0.0):
    return cylinder(
        braid_bobbin_diameter + 2.0 * clearance,
        braid_bobbin_thickness + clearance,
        braid_bobbin_x,
        braid_bobbin_y,
        cavity_floor_z,
    )


def build_tip_reference(kind, center_x, center_y):
    """One tip standing point-up on its socket floor."""
    stand_z = tip_socket_floor_z + 0.5
    if kind == "insert":
        return cylinder(
            insert_tip_diameter, insert_tip_length, center_x, center_y, stand_z
        )
    barrel = cylinder(
        t18_barrel_diameter, t18_barrel_length, center_x, center_y, stand_z
    )
    working = cylinder(
        t18_working_diameter,
        t18_working_length,
        center_x,
        center_y,
        stand_z + t18_barrel_length,
    )
    return barrel.union(working)


def build_tip_index_references():
    """The twenty tips, keyed by kind so the picture reads brass from copper."""
    references = {"insert": None, "hakko": None, "veco": None}
    for (_, kind), (center_x, center_y) in zip(
        tip_index_roster, tip_socket_centers
    ):
        tip = build_tip_reference(kind, center_x, center_y)
        references[kind] = tip if references[kind] is None else references[kind].union(tip)
    return references


def build_tweezer_references():
    tweezers = None
    for center_x in tweezer_slot_centers_x:
        tweezer = placed_prism(
            tweezer_width,
            tweezer_thickness,
            tweezer_length,
            center_x,
            tweezer_slot_y,
            z_bottom=tweezer_slot_floor_z + 0.5,
            radius=1.0,
        )
        tweezers = tweezer if tweezers is None else tweezers.union(tweezer)
    return tweezers


def build_cutter_reference():
    return placed_prism(
        cutter_head_width,
        cutter_head_thickness,
        cutter_length,
        cutter_socket_x,
        cutter_socket_y,
        z_bottom=cutter_socket_floor_z + 0.5,
        radius=2.0,
    )


def build_brush_bundle_reference():
    return cylinder(
        flux_brush_bundle_diameter,
        flux_brush_length,
        brush_quiver_x,
        brush_quiver_y,
        brush_quiver_floor_z + 0.5,
    )


def build_heat_gun_reference():
    return cylinder(
        heat_gun_diameter,
        heat_gun_length,
        heat_gun_well_x,
        heat_gun_well_y,
        heat_gun_well_floor_z + 0.5,
    )


# ============================================================
# THE STACK
# ============================================================

def build_kit():
    parts = {
        "solder-dock": build_dock(),
        "solder-stock": build_stock_bin(),
        "solder-rework": build_rework_bin(),
        "solder-tips": build_tip_rack(),
    }
    storeys = [
        Storey("solder-stock", parts["solder-stock"], stock_storey_u, kind="bin"),
        Storey("solder-rework", parts["solder-rework"], rework_storey_u, kind="bin"),
        Storey("solder-tips", parts["solder-tips"], rack_u, kind="blank"),
    ]
    return parts, storeys


stock_contents = (
    ("Kester 24-6337-0027 1 lb spool", build_solder_spool, solder_spool_color),
    ("BEEYUIHF 30 mL flux bottle", build_flux_bottle, flux_bottle_color),
    ("ELEGOO polyimide tape, 4 rolls", build_tape_rolls, tape_color),
    ("MG Chemicals 8341 49 g jar", build_flux_jar, flux_jar_color),
)

rework_contents = (
    ("flux syringes, 4 x 10 cc", build_flux_syringes, syringe_color),
    ("Kester 44 0.020 in pocket pack", build_fine_solder_pack, fine_solder_color),
    ("Soder-Wick bobbin", build_braid_bobbin, braid_color),
)


def kit_references():
    """Every stored thing, riding on the storey that holds it."""
    tips = build_tip_index_references()
    references = []
    for label, builder, color in stock_contents:
        references.append((label, builder(), color, 0))
    for label, builder, color in rework_contents:
        references.append((label, builder(), color, 1))
    references.append(("heat-set insert tips", tips["insert"], brass_tip_color, 2))
    references.append(("Hakko T18 chisels", tips["hakko"], copper_tip_color, 2))
    references.append(("VECO-T T18 assortment", tips["veco"], copper_tip_color, 2))
    references.append(("iFixit tweezers", build_tweezer_references(), tool_grip_color, 2))
    references.append(("KATA flush cutter", build_cutter_reference(), steel_color, 2))
    references.append(("flux brushes", build_brush_bundle_reference(), brush_color, 2))
    references.append(("QWORK heat gun", build_heat_gun_reference(), heat_gun_color, 2))
    return references


# ============================================================
# VALIDATION
# ============================================================

def validate(parts, storeys, seats):
    print("Fit checks")
    for name, shape in parts.items():
        assert_one_solid(name, shape)
        assert_h2c_fit(name, shape)

    assert_stack_seated(parts["solder-dock"], storeys, seats)

    rack = parts["solder-tips"]
    socket_reach = 0.0
    for label, center_x, center_y, half_x, half_y in rack_socket_extents:
        reach = max(abs(center_x) + half_x, abs(center_y) + half_y)
        if reach > rack_reach:
            raise ValueError(f"{label}: reaches {reach:.2f} mm, past the rack plateau")
        socket_reach = max(socket_reach, reach)
    print(
        f"   rack sockets reach {socket_reach:.2f} mm of the "
        f"{rack_reach:.2f} mm plateau half-span"
    )

    tips = build_tip_index_references()
    assert_clear("heat-set insert tips in the index", rack, tips["insert"])
    assert_clear("Hakko T18 chisels in the index", rack, tips["hakko"])
    assert_clear("VECO-T assortment in the index", rack, tips["veco"])
    assert_clear("iFixit tweezers in their slots", rack, build_tweezer_references())
    assert_clear("KATA flush cutter in its socket", rack, build_cutter_reference())
    assert_clear("flux brushes in the quiver", rack, build_brush_bundle_reference())
    assert_clear("QWORK heat gun in its well", rack, build_heat_gun_reference())

    stock_cavity = bin_cavity(
        parts["solder-stock"], kit_units_x, kit_units_y, stock_storey_u
    )
    for label, builder, _ in stock_contents:
        assert_contained(
            f"{label} + {content_clearance:.0f} mm",
            builder(content_clearance),
            stock_cavity,
        )

    rework_cavity = bin_cavity(
        parts["solder-rework"], kit_units_x, kit_units_y, rework_storey_u
    )
    for label, builder, _ in rework_contents:
        assert_contained(
            f"{label} + {content_clearance:.0f} mm",
            builder(content_clearance),
            rework_cavity,
        )

    for label, length in (
        ("3M Virtua CCS", safety_glasses_frame_width),
        ("FAST CHIP alloy", removal_alloy_piece_length),
    ):
        if length < cell_diagonal:
            raise ValueError(f"{label} now fits a cell: give it a compartment")
        print(
            f"   {label} left out: {length:.1f} mm over the "
            f"{cell_diagonal:.1f} mm cell diagonal"
        )


# ============================================================
# EXPORT
# ============================================================

def printed_height(seats, parts):
    return seats[-1] + bbox(parts["solder-tips"]).zlen


def populated_height(seats):
    return seats[-1] + heat_gun_well_floor_z + 0.5 + heat_gun_length


def main():
    out_dir = Path(__file__).resolve().parent
    parts, storeys = build_kit()
    seats = stack_seats(storeys)
    references = kit_references()

    validate(parts, storeys, seats)

    export_parts(out_dir, parts)
    export_kit(
        out_dir,
        "solder-kit",
        kit_assembly(
            "solder-kit", parts["solder-dock"], storeys, seats, references
        ),
    )
    export_kit(
        out_dir,
        "solder-kit-open",
        kit_assembly(
            "solder-kit-open",
            parts["solder-dock"],
            storeys,
            exploded_seats(seats, 70.0),
            references,
        ),
    )

    variables = {
        "FOOTPRINT": f"{footprint_x:.0f} mm x {footprint_y:.0f} mm",
        "PRINTED_HEIGHT": f"{printed_height(seats, parts):.1f} mm",
        "POPULATED_HEIGHT": f"{populated_height(seats):.1f} mm",
        "H2C_ENVELOPE": f"{h2c_build_x:.0f} x {h2c_build_y:.0f} x {h2c_build_z:.0f} mm",
        "STOCK_STOREY": f"{top_reference_z(stock_storey_u):.0f} mm",
        "REWORK_STOREY": f"{top_reference_z(rework_storey_u):.0f} mm",
        "RACK_STOREY": f"{top_reference_z(rack_u):.0f} mm",
        "CELL": f"{cell_width:.2f} mm x {2.0 * cavity_half_span:.1f} mm",
        "STOCK_CELL_DEPTH": f"{stock_cavity_top_z - cavity_floor_z:.0f} mm",
        "REWORK_CELL_DEPTH": f"{rework_cavity_top_z - cavity_floor_z:.0f} mm",
        "TIP_SOCKET": f"{tip_socket_bore:.0f} mm",
        "TIP_SOCKET_DEPTH": f"{rack_plateau_z - tip_socket_floor_z:.0f} mm",
        "TIP_SOCKET_COUNT": f"{len(tip_socket_centers)}",
        "TIP_PITCH": f"{tip_socket_pitch:.0f} mm",
        "T18_BARREL": f"{t18_barrel_diameter:.1f} mm x {t18_tip_length:.0f} mm",
        "INSERT_TIP": f"{insert_tip_diameter:.0f} mm x {insert_tip_length:.0f} mm",
        "HEAT_GUN": f"{heat_gun_diameter:.1f} mm x {heat_gun_length:.1f} mm",
        "HEAT_GUN_WELL": f"{heat_gun_well_diameter:.1f} mm",
        "HEAT_GUN_WELL_DEPTH": f"{rack_plateau_z - heat_gun_well_floor_z:.0f} mm",
        "BRUSH_QUIVER": f"{brush_quiver_diameter:.0f} mm",
        "BRUSH_BUNDLE": f"{flux_brush_bundle_diameter:.0f} mm x {flux_brush_length:.1f} mm",
        "SPOOL_ENVELOPE": f"{solder_spool_diameter:.1f} mm x {solder_spool_width:.1f} mm",
        "TAPE_ROLL": f"{tape_roll_diameter:.0f} mm",
        "TAPE_STACK": f"{tape_stack_height:.1f} mm",
        "BRAID_BOBBIN": f"{braid_bobbin_diameter:.1f} mm x {braid_bobbin_thickness:.2f} mm",
        "FLUX_JAR": f"{flux_jar_diameter:.0f} mm x {flux_jar_height:.0f} mm",
        "FLUX_BOTTLE": f"{flux_bottle_diameter:.0f} mm x {flux_bottle_height:.0f} mm",
        "FLUX_SYRINGE": f"{flux_syringe_diameter:.0f} mm x {flux_syringe_length:.0f} mm",
        "FINE_SOLDER_PACK": f"{fine_solder_pack_diameter:.0f} mm x {fine_solder_pack_height:.0f} mm",
        "CELL_DIAGONAL": f"{cell_diagonal:.0f} mm",
        "GLASSES_WIDTH": f"{safety_glasses_frame_width:.0f} mm",
        "GLASSES_DEPTH_BUDGET": f"{safety_glasses_folded_depth_budget:.0f} mm",
        "ALLOY_PIECE": f"{removal_alloy_piece_length:.1f} mm",
        "CONTENT_CLEARANCE": f"{content_clearance:.0f} mm",
        "SOCKET_CLEARANCE": f"{socket_clearance:.1f} mm",
        "PLATEAU_REACH": f"{rack_reach:.2f} mm",
        "DOCK_HEIGHT": f"{bbox(parts['solder-dock']).zlen:.1f} mm",
        "TALLEST_PART": f"{bbox(parts['solder-stock']).zlen:.1f} mm",
    }
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
