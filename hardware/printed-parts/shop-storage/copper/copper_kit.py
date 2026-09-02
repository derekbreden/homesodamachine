"""Copper job kit — the tube bench.

The job is 1/4" ACR copper: straighten off the 50 ft roll, cut square, wind on
the coil mandrel, flare the purge stub, pinch-swage the coil inlet onto the
capillary (`assembly/cold-core.md` §1, `assembly/refrigerant-loop.md` §3 and
§5).

Frame: world +Z is up, +Y is the operator-facing front, +X is the operator's
right.  Every storey is a stock cq-gridfinity body built with its bottom at
Z = 0; `_kit.stack_seats` puts each one on the storey below.  Every stored
thing is a public-envelope reference built in its storey's own frame and
asserted against the void or the socket that holds it.

Nothing on this bench lies down.  The shortest tool here is longer than a
3 x 3 storey is wide, so the three that reach past a rack stand head-down in
one, and the four that do not stand inside a quiver deep enough to close over
them.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
from cqgridfinity import GridfinityBox
from cqgridfinity.constants import GR_DIV_WALL

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import _kit  # noqa: E402
from _kit import substitute_md  # noqa: E402


# ============================================================
# FOOTPRINT AND STOREYS
# ============================================================

kit_x_u = 3
kit_y_u = 3

footprint_x = kit_x_u * _kit.grid_unit
footprint_y = kit_y_u * _kit.grid_unit

bin_wall = GridfinityBox(kit_x_u, kit_y_u, 1).wall_th
interior_half_x = _kit.outer_size(kit_x_u) / 2.0 - bin_wall
interior_half_y = _kit.outer_size(kit_y_u) / 2.0 - bin_wall

#: A bin's interior floor stands one height unit over the storey's own bottom:
#: the base profile's whole depth is under it.
storey_floor_z = _kit.height_unit

#: The library's label ledge roofs this much of a compartment's +Y end, and
#: `bin_cavity` leaves it out of the void: a content tall enough to reach the
#: ledge's underside keeps out of the strip altogether.
label_ledge_width = 12.0

quiver_height_u = 27
service_height_u = 11
fittings_height_u = 5
rack_height_u = 7


def cavity_depth(height_u):
    """Floor to top reference: how tall a thing standing in the storey may be."""
    return _kit.top_reference_z(height_u) - storey_floor_z


def compartment_span(interior_half, divisions):
    """One compartment's width when `divisions` dividers split the interior."""
    return (2.0 * interior_half - divisions * GR_DIV_WALL) / (divisions + 1)


def compartment_centres(interior_half, divisions):
    """Each compartment's centre, low side first."""
    pitch = compartment_span(interior_half, divisions) + GR_DIV_WALL
    return [(index - divisions / 2.0) * pitch for index in range(divisions + 1)]


#: Clear of the library's 1.1 mm floor fillet, so a content standing on a
#: compartment floor touches nothing at its bottom corners.
content_wall_clearance = 1.5

#: Between two contents standing in one compartment, and between two sockets
#: cut from one plateau.
content_gap = 3.0

reference_corner_radius = 2.0


# ============================================================
# PUBLIC TOOL AND PART ENVELOPES
# ============================================================

#: Klein's own catalogue page for the 51006: 10.5 x 2.9 x 2.7 in overall.
klein_51006_length = 266.7
klein_51006_shoe_height = 73.7
klein_51006_shoe_width = 68.6

#: The B0009W6T8G listing's product envelope: 7.5 x 3.5 x 1.5 in.
ridgid_150_length = 190.5
ridgid_150_width = 88.9
ridgid_150_thickness = 38.1

#: MASTERCOOL publishes no dimensions for the 70025 and the listing carries a
#: carton, so this is a generous envelope for a 104 g hand nipper.
mastercool_70025_length = 220.0
mastercool_70025_width = 65.0
mastercool_70025_thickness = 18.0

#: KNIPEX's own catalogue figures for the 86 01 180.
knipex_860180_length = 180.0
knipex_860180_head_width = 46.0
knipex_860180_thickness = 15.0

#: The B0F6BPTW3T listing carries only a 178 x 153 x 77 mm package, so this is
#: a generous envelope inside it.
wisscool_length = 170.0
wisscool_width = 100.0
wisscool_thickness = 65.0

#: RIDGID publishes only the 345's 2.75 lb; distributors publish a 6-1/4 in
#: overall length. Bar and yoke are generous envelopes on that length.
ridgid_345_bar_length = 160.0
ridgid_345_bar_width = 45.0
ridgid_345_bar_thickness = 30.0

ridgid_345_yoke_height = 130.0
ridgid_345_yoke_width = 70.0
ridgid_345_yoke_thickness = 40.0

#: The B00DM8KGXS listing states the drier's size in its title: 1.5 x 2.5 x 3.5 in.
supco_d111_length = 88.9
supco_d111_standing_height = 63.5
supco_d111_depth = 38.1

#: Distributor spec tables for the BPV31: 2 x 2 x 1-3/4 in.
supco_bpv31_width = 50.8
supco_bpv31_depth = 50.8
supco_bpv31_height = 44.45

#: A 1/4" SAE 45° flare nut on a 7/16"-20 thread; the pack is five.
joywayus_flare_nut_across_corners = 20.0
joywayus_flare_nut_length = 20.0
joywayus_flare_nut_count = 5
joywayus_flare_nut_columns = 2
joywayus_flare_nut_rows = 3

#: The B0FH549N6D listing states 6.3 mm bore, 16 mm long, 0.6 mm wall.
slip_coupling_bore = 6.3
slip_coupling_wall = 0.6
slip_coupling_outside_diameter = slip_coupling_bore + 2.0 * slip_coupling_wall
slip_coupling_length = 16.0
slip_coupling_count = 10
slip_coupling_columns = 5
slip_coupling_rows = 2

fill_block_pitch = 1.3


# ============================================================
# THE QUIVER — TOOLS THAT CLOSE UNDER THE STOREY ABOVE
# ============================================================

quiver_cavity_depth = cavity_depth(quiver_height_u)
quiver_back_row_y = -interior_half_y + content_wall_clearance
quiver_front_row_y = quiver_back_row_y + wisscool_thickness + content_gap

wisscool_x = -interior_half_x + content_wall_clearance + wisscool_width / 2.0
wisscool_y = quiver_back_row_y + wisscool_thickness / 2.0

knipex_quiver_x = interior_half_x - content_gap - knipex_860180_thickness / 2.0
knipex_quiver_y = quiver_back_row_y + knipex_860180_head_width / 2.0

yoke_x = -interior_half_x + content_wall_clearance + ridgid_345_yoke_width / 2.0
yoke_y = quiver_front_row_y + ridgid_345_yoke_thickness / 2.0

bar_x = yoke_x + ridgid_345_yoke_width / 2.0 + content_gap + ridgid_345_bar_width / 2.0
bar_y = quiver_front_row_y + ridgid_345_bar_thickness / 2.0


def build_quiver():
    """One open cell deep enough to close over the straightener, the flaring
    set and the pliers wrench, all of them standing."""
    return _kit.bin_body(kit_x_u, kit_y_u, quiver_height_u, labels=True)


def build_quiver_references():
    floor = storey_floor_z
    return {
        "wisscool-straightener": _kit.placed_prism(
            wisscool_width,
            wisscool_thickness,
            wisscool_length,
            wisscool_x,
            wisscool_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
        "ridgid-345-yoke": _kit.placed_prism(
            ridgid_345_yoke_width,
            ridgid_345_yoke_thickness,
            ridgid_345_yoke_height,
            yoke_x,
            yoke_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
        "ridgid-345-bar": _kit.placed_prism(
            ridgid_345_bar_width,
            ridgid_345_bar_thickness,
            ridgid_345_bar_length,
            bar_x,
            bar_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
        "knipex-86-01-180": _kit.placed_prism(
            knipex_860180_thickness,
            knipex_860180_head_width,
            knipex_860180_length,
            knipex_quiver_x,
            knipex_quiver_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
    }


# ============================================================
# THE SERVICE STOREY — DRIER AND PIERCING VALVE
# ============================================================

service_cavity_depth = cavity_depth(service_height_u)
service_compartment_span = compartment_span(interior_half_y, 1)
service_back_y, service_front_y = compartment_centres(interior_half_y, 1)

#: The drier stands taller than the label ledge's underside, so it backs off
#: the +Y end of its own compartment by the ledge's whole width.
d111_y = (
    service_back_y
    + service_compartment_span / 2.0
    - label_ledge_width
    - content_wall_clearance
    - supco_d111_depth / 2.0
)
bpv31_y = service_front_y


def build_service():
    """Two full-width compartments: the drier spare and the piercing valve."""
    return _kit.bin_body(
        kit_x_u, kit_y_u, service_height_u, width_div=1, labels=True
    )


def build_service_references():
    floor = storey_floor_z
    return {
        "supco-d111-drier": _kit.placed_prism(
            supco_d111_length,
            supco_d111_depth,
            supco_d111_standing_height,
            0.0,
            d111_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
        "supco-bpv31-valve": _kit.placed_prism(
            supco_bpv31_width,
            supco_bpv31_depth,
            supco_bpv31_height,
            0.0,
            bpv31_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
    }


# ============================================================
# THE FITTINGS STOREY — FLARE NUTS AND SLIP COUPLINGS
# ============================================================

fittings_cavity_depth = cavity_depth(fittings_height_u)
fittings_nut_x, fittings_coupling_x = compartment_centres(interior_half_x, 1)

flare_nut_pitch = joywayus_flare_nut_across_corners + fill_block_pitch
flare_nut_fill_x = joywayus_flare_nut_columns * flare_nut_pitch
flare_nut_fill_y = joywayus_flare_nut_rows * flare_nut_pitch

coupling_pitch = slip_coupling_outside_diameter + fill_block_pitch
coupling_fill_x = slip_coupling_columns * coupling_pitch
coupling_fill_y = slip_coupling_rows * coupling_pitch

#: Both fills stand clear of the label ledge's strip at the +Y end.
fittings_fill_y = -label_ledge_width / 2.0


def build_fittings():
    """Two full-depth compartments for the two packs of small brass and copper."""
    return _kit.bin_body(
        kit_x_u, kit_y_u, fittings_height_u, length_div=1, labels=True
    )


def build_fittings_references():
    floor = storey_floor_z
    return {
        "joywayus-flare-nuts": _kit.placed_prism(
            flare_nut_fill_x,
            flare_nut_fill_y,
            joywayus_flare_nut_length,
            fittings_nut_x,
            fittings_fill_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
        "slip-couplings": _kit.placed_prism(
            coupling_fill_x,
            coupling_fill_y,
            slip_coupling_length,
            fittings_coupling_x,
            fittings_fill_y,
            z_bottom=floor,
            radius=reference_corner_radius,
        ),
    }


# ============================================================
# THE JOB RACK — TOOLS THAT STAND PROUD OF THE KIT
# ============================================================

rack_top_z = _kit.top_reference_z(rack_height_u)

#: Every socket floor stands clear above the storey below: the blank is solid
#: under it, base profile and all.
rack_socket_floor_z = 9.0
rack_plateau_half = _kit.plateau_half(kit_x_u)
rack_socket_clearance = 1.5
socket_gap = 4.0
plateau_margin = 1.5
tool_seat_z = rack_socket_floor_z + 0.5

#: The bender goes in with its shoe's height across +X, so its socket takes the
#: least of the plateau's +Y run and leaves the front strip whole for the cutter.
klein_socket_x_size = klein_51006_shoe_height + 2.0 * rack_socket_clearance
klein_socket_y_size = klein_51006_shoe_width + 2.0 * rack_socket_clearance
klein_socket_x = -rack_plateau_half + plateau_margin + klein_socket_x_size / 2.0
klein_socket_y = -rack_plateau_half + plateau_margin + klein_socket_y_size / 2.0

ridgid_150_socket_x_size = ridgid_150_width + 2.0 * rack_socket_clearance
ridgid_150_socket_y_size = ridgid_150_thickness + 2.0 * rack_socket_clearance
ridgid_150_socket_x = (
    -rack_plateau_half + plateau_margin + ridgid_150_socket_x_size / 2.0
)
ridgid_150_socket_y = (
    klein_socket_y + klein_socket_y_size / 2.0 + socket_gap + ridgid_150_socket_y_size / 2.0
)

mastercool_socket_x_size = mastercool_70025_thickness + 2.0 * rack_socket_clearance
mastercool_socket_y_size = mastercool_70025_width + 2.0 * rack_socket_clearance
#: Centred in the column of plateau the bender's socket leaves at +X.
mastercool_socket_x = (
    klein_socket_x + klein_socket_x_size / 2.0 + rack_plateau_half
) / 2.0
mastercool_socket_y = -rack_plateau_half + plateau_margin + mastercool_socket_y_size / 2.0

parts_well_x_size = 20.0
parts_well_y_size = 36.0
parts_well_depth = 20.0
parts_well_x = (
    ridgid_150_socket_x
    + ridgid_150_socket_x_size / 2.0
    + socket_gap
    + parts_well_x_size / 2.0
)
parts_well_y = ridgid_150_socket_y
parts_well_floor_z = rack_top_z - parts_well_depth

rack_sockets = (
    ("klein-51006-bender", klein_socket_x_size, klein_socket_y_size,
     klein_socket_x, klein_socket_y, rack_socket_floor_z),
    ("ridgid-150-cutter", ridgid_150_socket_x_size, ridgid_150_socket_y_size,
     ridgid_150_socket_x, ridgid_150_socket_y, rack_socket_floor_z),
    ("mastercool-70025-cutter", mastercool_socket_x_size, mastercool_socket_y_size,
     mastercool_socket_x, mastercool_socket_y, rack_socket_floor_z),
    ("parts-well", parts_well_x_size, parts_well_y_size,
     parts_well_x, parts_well_y, parts_well_floor_z),
)


def build_rack():
    """A solid lipped blank with three head-down tool sockets and one well."""
    rack = _kit.blank_body(kit_x_u, kit_y_u, rack_height_u)
    for _, x_size, y_size, centre_x, centre_y, floor_z in rack_sockets:
        rack = rack.cut(
            _kit.pocket(x_size, y_size, centre_x, centre_y, floor_z, rack_top_z)
        )
    return rack.clean()


grip_fraction_of_head = 0.42

klein_head_top_z = rack_top_z + 40.0
ridgid_150_body_top_z = rack_top_z + 55.0
mastercool_head_top_z = rack_top_z + 35.0


def _standing_tool(head_x, head_y, head_top_z, length, centre_x, centre_y):
    """A head-down tool: its head in the socket, two grips rising off the rack.

    The grips part along the head's wider axis, so a tool reads as a tool from
    every side its socket does not hide."""
    head = _kit.placed_prism(
        head_x,
        head_y,
        head_top_z - tool_seat_z,
        centre_x,
        centre_y,
        z_bottom=tool_seat_z,
        radius=reference_corner_radius,
    )
    parts_along_x = head_x >= head_y
    split_span = head_x if parts_along_x else head_y
    grip_span = split_span * grip_fraction_of_head
    grip_offset = (split_span - grip_span) / 2.0
    grip_x = grip_span if parts_along_x else head_x
    grip_y = head_y if parts_along_x else grip_span
    grips = []
    for sign in (-1.0, 1.0):
        grips.append(
            _kit.placed_prism(
                grip_x,
                grip_y,
                tool_seat_z + length - head_top_z,
                centre_x + (sign * grip_offset if parts_along_x else 0.0),
                centre_y + (0.0 if parts_along_x else sign * grip_offset),
                z_bottom=head_top_z,
                radius=min(grip_x, grip_y) / 3.0,
            )
        )
    return {"head": head, "left-grip": grips[0], "right-grip": grips[1]}


def build_rack_references():
    klein = _standing_tool(
        klein_51006_shoe_height,
        klein_51006_shoe_width,
        klein_head_top_z,
        klein_51006_length,
        klein_socket_x,
        klein_socket_y,
    )
    ridgid_150_body = _kit.placed_prism(
        ridgid_150_width,
        ridgid_150_thickness,
        ridgid_150_body_top_z - tool_seat_z,
        ridgid_150_socket_x,
        ridgid_150_socket_y,
        z_bottom=tool_seat_z,
        radius=reference_corner_radius,
    )
    ridgid_150_knob = _kit.cylinder(
        ridgid_150_thickness,
        tool_seat_z + ridgid_150_length - ridgid_150_body_top_z,
        ridgid_150_socket_x,
        ridgid_150_socket_y,
        ridgid_150_body_top_z,
    )
    mastercool = _standing_tool(
        mastercool_70025_thickness,
        mastercool_70025_width,
        mastercool_head_top_z,
        mastercool_70025_length,
        mastercool_socket_x,
        mastercool_socket_y,
    )
    return {
        "klein-51006-bender": klein,
        "ridgid-150-cutter": {"body": ridgid_150_body, "knob": ridgid_150_knob},
        "mastercool-70025-cutter": mastercool,
    }


# ============================================================
# DISPLAY COLOURS
# ============================================================

klein_orange = cq.Color(0.93, 0.42, 0.05)
ridgid_grey = cq.Color(0.74, 0.75, 0.77)
tool_black = cq.Color(0.09, 0.09, 0.10)
tool_red = cq.Color(0.74, 0.11, 0.12)
steel_color = cq.Color(0.58, 0.60, 0.62)
brass_color = cq.Color(0.76, 0.60, 0.24)
copper_color = cq.Color(0.72, 0.42, 0.26)
aluminum_color = cq.Color(0.80, 0.81, 0.83)


# ============================================================
# THE KIT
# ============================================================

exploded_lift = 70.0


def build_storeys():
    return [
        _kit.Storey("copper-quiver", build_quiver(), quiver_height_u),
        _kit.Storey("copper-service", build_service(), service_height_u),
        _kit.Storey("copper-fittings", build_fittings(), fittings_height_u),
        _kit.Storey("copper-rack", build_rack(), rack_height_u, kind="blank"),
    ]


def content_references(quiver, service, fittings, rack):
    """(name, shape, colour, storey index) for every stored thing."""
    references = [
        ("wisscool-straightener", quiver["wisscool-straightener"], tool_black, 0),
        ("ridgid-345-yoke", quiver["ridgid-345-yoke"], steel_color, 0),
        ("ridgid-345-bar", quiver["ridgid-345-bar"], steel_color, 0),
        ("knipex-86-01-180", quiver["knipex-86-01-180"], tool_red, 0),
        ("supco-d111-drier", service["supco-d111-drier"], copper_color, 1),
        ("supco-bpv31-valve", service["supco-bpv31-valve"], aluminum_color, 1),
        ("joywayus-flare-nuts", fittings["joywayus-flare-nuts"], brass_color, 2),
        ("slip-couplings", fittings["slip-couplings"], copper_color, 2),
    ]
    klein_colors = {"head": klein_orange, "left-grip": klein_orange, "right-grip": klein_orange}
    for part, shape in rack["klein-51006-bender"].items():
        references.append((f"klein-51006-{part}", shape, klein_colors[part], 3))
    references.append(("ridgid-150-body", rack["ridgid-150-cutter"]["body"], ridgid_grey, 3))
    references.append(("ridgid-150-knob", rack["ridgid-150-cutter"]["knob"], tool_black, 3))
    for part, shape in rack["mastercool-70025-cutter"].items():
        references.append(
            (f"mastercool-70025-{part}", shape, tool_black if part == "head" else tool_red, 3)
        )
    return references


def rack_fit_shapes(rack):
    return {
        "Klein 51006 bender": (
            rack["klein-51006-bender"]["head"]
            .union(rack["klein-51006-bender"]["left-grip"])
            .union(rack["klein-51006-bender"]["right-grip"])
        ),
        "RIDGID 150 cutter": rack["ridgid-150-cutter"]["body"].union(
            rack["ridgid-150-cutter"]["knob"]
        ),
        "Mastercool 70025 cutter": (
            rack["mastercool-70025-cutter"]["head"]
            .union(rack["mastercool-70025-cutter"]["left-grip"])
            .union(rack["mastercool-70025-cutter"]["right-grip"])
        ),
    }


def assert_inside_plateau(name, x_size, y_size, centre_x, centre_y):
    """A socket opens inside the blank's flat top, never through its lip."""
    reach_x = abs(centre_x) + x_size / 2.0
    reach_y = abs(centre_y) + y_size / 2.0
    if max(reach_x, reach_y) > rack_plateau_half:
        raise ValueError(
            f"{name}: socket reaches {max(reach_x, reach_y):.2f} mm, "
            f"past the {rack_plateau_half:.2f} mm plateau"
        )
    print(f"   {name}: {rack_plateau_half - max(reach_x, reach_y):.2f} mm inside the plateau")


def validate(parts, storeys, seats, quiver, service, fittings, rack):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    _kit.assert_stack_seated(parts["copper-dock"], storeys, seats)

    for name, x_size, y_size, centre_x, centre_y, _ in rack_sockets:
        assert_inside_plateau(name, x_size, y_size, centre_x, centre_y)

    quiver_cavity = _kit.bin_cavity(
        parts["copper-quiver"], kit_x_u, kit_y_u, quiver_height_u
    )
    for name, shape in quiver.items():
        _kit.assert_contained(name, shape, quiver_cavity)

    service_cavity = _kit.bin_cavity(
        parts["copper-service"], kit_x_u, kit_y_u, service_height_u
    )
    for name, shape in service.items():
        _kit.assert_contained(name, shape, service_cavity)

    fittings_cavity = _kit.bin_cavity(
        parts["copper-fittings"], kit_x_u, kit_y_u, fittings_height_u
    )
    for name, shape in fittings.items():
        _kit.assert_contained(name, shape, fittings_cavity)

    for name, shape in rack_fit_shapes(rack).items():
        _kit.assert_clear(name, parts["copper-rack"], shape)


def populated_height(seats):
    return seats[3] + tool_seat_z + klein_51006_length


def main():
    out_dir = Path(__file__).resolve().parent

    storeys = build_storeys()
    seats = _kit.stack_seats(storeys)
    dock = _kit.dock_body(kit_x_u, kit_y_u)

    parts = {"copper-dock": dock}
    parts.update({storey.name: storey.shape for storey in storeys})

    quiver = build_quiver_references()
    service = build_service_references()
    fittings = build_fittings_references()
    rack = build_rack_references()

    validate(parts, storeys, seats, quiver, service, fittings, rack)

    references = content_references(quiver, service, fittings, rack)
    _kit.export_parts(out_dir, parts)
    _kit.export_kit(
        out_dir,
        "copper-kit",
        _kit.kit_assembly("copper-kit", dock, storeys, seats, references),
    )
    _kit.export_kit(
        out_dir,
        "copper-kit-open",
        _kit.kit_assembly(
            "copper-kit-open",
            dock,
            storeys,
            _kit.exploded_seats(seats, exploded_lift),
            references,
        ),
    )

    printed_height = seats[3] + rack_top_z
    variables = {
        "FOOTPRINT": f"{footprint_x:.0f} mm x {footprint_y:.0f} mm",
        "PRINTED_HEIGHT": f"{printed_height:.1f} mm",
        "POPULATED_HEIGHT": f"{populated_height(seats):.1f} mm",
        "H2C_ENVELOPE": (
            f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x {_kit.h2c_build_z:.0f} mm"
        ),
        "STOREY_OUTER": f"{_kit.outer_size(kit_x_u):.1f} mm x {_kit.outer_size(kit_y_u):.1f} mm",
        "QUIVER_DEPTH": f"{quiver_cavity_depth:.0f} mm",
        "SERVICE_DEPTH": f"{service_cavity_depth:.0f} mm",
        "FITTINGS_DEPTH": f"{fittings_cavity_depth:.0f} mm",
        "QUIVER_HEIGHT": f"{_kit.top_reference_z(quiver_height_u):.0f} mm",
        "SERVICE_HEIGHT": f"{_kit.top_reference_z(service_height_u):.0f} mm",
        "FITTINGS_HEIGHT": f"{_kit.top_reference_z(fittings_height_u):.0f} mm",
        "RACK_HEIGHT": f"{rack_top_z:.0f} mm",
        "QUIVER_CELL": f"{2 * interior_half_x:.1f} mm x {2 * interior_half_y:.1f} mm",
        "SERVICE_CELL": (
            f"{2 * interior_half_x:.1f} mm x {service_compartment_span:.1f} mm"
        ),
        "FITTINGS_CELL": (
            f"{compartment_span(interior_half_x, 1):.1f} mm x {2 * interior_half_y:.1f} mm"
        ),
        "SOCKET_CLEARANCE": f"{rack_socket_clearance:.1f} mm",
        "SOCKET_DEPTH": f"{rack_top_z - rack_socket_floor_z:.0f} mm",
        "KLEIN_SOCKET": f"{klein_socket_x_size:.1f} x {klein_socket_y_size:.1f} mm",
        "RIDGID_150_SOCKET": (
            f"{ridgid_150_socket_x_size:.1f} x {ridgid_150_socket_y_size:.1f} mm"
        ),
        "MASTERCOOL_SOCKET": (
            f"{mastercool_socket_x_size:.1f} x {mastercool_socket_y_size:.1f} mm"
        ),
        "PARTS_WELL": (
            f"{parts_well_x_size:.0f} x {parts_well_y_size:.0f} mm,"
            f" {parts_well_depth:.0f} mm deep"
        ),
        "DOCK_PART": _kit.size_text(dock),
        "QUIVER_PART": _kit.size_text(parts["copper-quiver"]),
        "SERVICE_PART": _kit.size_text(parts["copper-service"]),
        "FITTINGS_PART": _kit.size_text(parts["copper-fittings"]),
        "RACK_PART": _kit.size_text(parts["copper-rack"]),
        "KLEIN_ENVELOPE": (
            f"{klein_51006_length:.1f} x {klein_51006_shoe_height:.1f}"
            f" x {klein_51006_shoe_width:.1f} mm"
        ),
        "RIDGID_150_ENVELOPE": (
            f"{ridgid_150_length:.1f} x {ridgid_150_width:.1f} x {ridgid_150_thickness:.1f} mm"
        ),
        "MASTERCOOL_ENVELOPE": (
            f"{mastercool_70025_length:.0f} x {mastercool_70025_width:.0f}"
            f" x {mastercool_70025_thickness:.0f} mm"
        ),
        "KNIPEX_ENVELOPE": (
            f"{knipex_860180_length:.0f} x {knipex_860180_head_width:.0f}"
            f" x {knipex_860180_thickness:.0f} mm"
        ),
        "WISSCOOL_ENVELOPE": (
            f"{wisscool_length:.0f} x {wisscool_width:.0f} x {wisscool_thickness:.0f} mm"
        ),
        "WISSCOOL_PACKAGE": "178 x 153 x 77 mm",
        "BAR_ENVELOPE": (
            f"{ridgid_345_bar_length:.0f} x {ridgid_345_bar_width:.0f}"
            f" x {ridgid_345_bar_thickness:.0f} mm"
        ),
        "YOKE_ENVELOPE": (
            f"{ridgid_345_yoke_height:.0f} x {ridgid_345_yoke_width:.0f}"
            f" x {ridgid_345_yoke_thickness:.0f} mm"
        ),
        "D111_ENVELOPE": (
            f"{supco_d111_length:.1f} x {supco_d111_standing_height:.1f}"
            f" x {supco_d111_depth:.1f} mm"
        ),
        "BPV31_ENVELOPE": (
            f"{supco_bpv31_width:.1f} x {supco_bpv31_depth:.1f} x {supco_bpv31_height:.2f} mm"
        ),
        "COUPLING_ENVELOPE": (
            f"{slip_coupling_outside_diameter:.1f} mm OD x {slip_coupling_length:.0f} mm"
        ),
        "FLARE_NUT_COUNT": f"{joywayus_flare_nut_count}",
        "COUPLING_COUNT": f"{slip_coupling_count}",
        "SUD8358_LENGTH": "222 mm",
        "WISSCOOL_STANDING": f"{wisscool_length:.0f} mm",
        "KNIPEX_STANDING": f"{knipex_860180_length:.0f} mm",
        "YOKE_STANDING": f"{ridgid_345_yoke_height:.0f} mm",
        "BAR_STANDING": f"{ridgid_345_bar_length:.0f} mm",
        "CAVITY_DIAGONAL": f"{math.hypot(2 * interior_half_x, 2 * interior_half_y):.1f} mm",
        "LABEL_TAPE": f"{label_ledge_width:.0f} mm",
    }
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
