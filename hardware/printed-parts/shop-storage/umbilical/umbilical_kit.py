"""Umbilical job kit.

The job is one cable terminated at both ends: the EZYUMM 6P4C plug crimped onto
the BNTECHGO 28 AWG ribbon at `assembly/faucet-and-umbilical.md` §2, and the J3
loom punched onto the RiteAV keystone's 110 IDC at `assembly/wiring.md`.

Frame: world +Z is up, +Y is the operator-facing front, +X is the operator's
right.  Every storey is a stock cq-gridfinity body built with its bottom at
Z = 0; `_kit.stack_seats` puts each one on the storey below.  Contents are
public-dimension envelopes built in their own storey's frame and asserted
against the void that holds them.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
from cqgridfinity import GridfinityBox

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import _kit  # noqa: E402
from _kit import substitute_md  # noqa: E402


# ============================================================
# FOOTPRINT AND STOREYS
# ============================================================

kit_x_u = 2
kit_y_u = 3

footprint_x = kit_x_u * _kit.grid_unit
footprint_y = kit_y_u * _kit.grid_unit

#: The library's own figures for a box of this footprint, read off one rather
#: than copied out of it.
_stock_box = GridfinityBox(kit_x_u, kit_y_u, 1)

interior_half_x = _kit.outer_size(kit_x_u) / 2.0 - _stock_box.wall_th
interior_half_y = _kit.outer_size(kit_y_u) / 2.0 - _stock_box.wall_th

#: A bin's interior floor stands one height unit over the storey's own bottom:
#: the base profile's whole depth is under it.
storey_floor_z = _kit.height_unit

#: The label ledge roofs the +Y end of every compartment, and `bin_cavity`
#: leaves it out of the void — so a content standing taller than
#: `top - ledge_height` has to keep `ledge_width` clear of that wall.
label_ledge_width = _stock_box.label_width
label_ledge_height = _stock_box.label_height

ribbon_height_u = 11
stand_height_u = 7
terminations_height_u = 7
#: Deep enough that the longest tool's head is buried rather than perched: the
#: Klein 11057 stands 190.5 mm out of a socket that has to be its whole footing.
rack_height_u = 8

wall_clearance_min = 1.0


def usable_height(height_u):
    """How deep a bin storey's compartments run, floor to top reference."""
    return _kit.top_reference_z(height_u) - storey_floor_z


# ============================================================
# BNTECHGO 28 AWG 4-CONDUCTOR RIBBON, 50 FT (B07PNPHWMG)
# ============================================================

#: The listing's parcel envelope, 8.1 x 7.7 x 6.8 cm.  No maker figure states
#: the reel itself, so the kit reserves the parcel: the reel is inside it by
#: whatever the packer padded.
ribbon_parcel_x = 77.0
ribbon_parcel_y = 81.0
ribbon_parcel_z = 68.0

ribbon_section_w = 4.0
ribbon_section_t = 1.2
ribbon_length = 50.0 * 12.0 * 25.4

reel_padding = 2.5
reel_flange_diameter = min(ribbon_parcel_x, ribbon_parcel_y) - 2.0 * reel_padding
reel_width = ribbon_parcel_z - 2.0 * reel_padding
reel_hub_diameter = 30.0
reel_flange_thickness = 2.5
#: The wound ribbon, as a cylinder of the wind's own volume between hub and
#: flange — 50 ft of a 1.2 x 4 mm section, at the packing a flat ribbon takes.
reel_wind_packing = 0.8
reel_wind_volume = ribbon_length * ribbon_section_w * ribbon_section_t / reel_wind_packing
reel_wind_width = reel_width - 2.0 * reel_flange_thickness
reel_wind_diameter = 2.0 * (
    (reel_wind_volume / (math.pi * reel_wind_width) + (reel_hub_diameter / 2.0) ** 2) ** 0.5
)

ribbon_parcel_center_y = 0.0


# ============================================================
# CABLE MATTERS 180056 KEYSTONE PUNCH-DOWN STAND (B00MHWRYMQ)
# ============================================================

stand_x = 2.7 * 25.4
stand_y = 4.3 * 25.4
stand_z = 1.1 * 25.4
stand_corner_radius = 4.0


# ============================================================
# RITEAV RJ11 6P4C KEYSTONE JACK (10-PACK) AND EZYUMM 6P4C PLUG (20-PACK)
# ============================================================

#: The body a 110-punchdown Cat3 keystone carries behind the module standard's
#: 14.5 x 16.0 mm face — the same figures `reference/riteav-keystone/` builds
#: the wall's receptacle against.
jack_body_w = 14.9
jack_body_h = 24.4
jack_body_depth = 30.0
jack_count = 10
jack_columns = 5
jack_rows = jack_count // jack_columns
jack_gap = 1.0
#: The jacks stand on their punchdown blocks, ports up: the mating axis is the
#: tall one, so ten of them lie in one layer instead of two.
jack_array_x = jack_columns * jack_body_w + (jack_columns - 1) * jack_gap
jack_array_y = jack_rows * jack_body_h + (jack_rows - 1) * jack_gap

plug_body_w = 9.65
plug_body_h = 7.0
plug_latch_h = 3.2
plug_height = plug_body_h + plug_latch_h
plug_length = 13.54
plug_count = 20
#: Twenty plugs go into their compartment as a heap, not a rank, so the fill is
#: one block of their own volume at the packing loose mouldings take.
plug_loose_packing = 0.55
plug_fill_volume = plug_count * plug_body_w * plug_height * plug_length / plug_loose_packing
plug_fill_margin = 4.0


# ============================================================
# THE JOB RACK AND ITS TOOLS
# ============================================================

rack_plateau_half_x = _kit.plateau_half(kit_x_u)
rack_plateau_half_y = _kit.plateau_half(kit_y_u)
rack_top_z = _kit.top_reference_z(rack_height_u)
#: Every socket floor stands clear of the storey below: the rack's base profile
#: is whole under all three.
rack_socket_floor_z = 8.0
rack_socket_depth = rack_top_z - rack_socket_floor_z
#: Loose, like the JST tower's: a head-down socket is a receiver, not a fit.
socket_slip = 2.5
socket_radius = 3.0

#: VCE GJ668BL, the modular crimper.  vcelink states 7.28 x 4.13 in over the
#: whole tool; the head that drops into the socket is a generous reference.
crimper_length = 7.28 * 25.4
crimper_open_width = 4.13 * 25.4
crimper_head_width_reference = 50.0
crimper_head_thickness_reference = 26.0
crimper_head_height_reference = 58.0
crimper_socket_width = crimper_head_width_reference + 2.0 * socket_slip
crimper_socket_depth = crimper_head_thickness_reference + 2.0 * socket_slip
crimper_socket_y = -38.0
crimper_grip_root_drop = 10.0
crimper_grip_root_inset = 4.0
crimper_grip_thickness = crimper_head_thickness_reference - 6.0

#: Klein VDV427-300, the impact punchdown.  6 x 1.5 x 1 in on Klein's page, and
#: the barrel holds that section its whole length, so the tool is its envelope.
punchdown_length = 6.0 * 25.4
punchdown_width = 1.5 * 25.4
punchdown_thickness = 1.0 * 25.4
punchdown_blade_length = 30.0
punchdown_socket_width = punchdown_width + 2.0 * socket_slip
punchdown_socket_depth = punchdown_thickness + 2.0 * socket_slip
punchdown_socket_y = 2.0

#: Klein 11057, the 20-30 AWG stripper.  Klein states 7.5 in overall and no
#: section, so head and grips are generous references.
stripper_length = 7.5 * 25.4
stripper_head_width_reference = 56.0
stripper_head_thickness_reference = 16.0
stripper_head_height_reference = 46.0
stripper_open_width_reference = 70.0
stripper_socket_width = stripper_head_width_reference + 2.0 * socket_slip
stripper_socket_depth = stripper_head_thickness_reference + 2.0 * socket_slip
stripper_socket_y = 44.0
stripper_grip_root_drop = 8.0
stripper_grip_root_inset = 8.0
stripper_grip_thickness = stripper_head_thickness_reference - 3.0

tool_seat_z = rack_socket_floor_z + 0.5


# ============================================================
# PRESENTATION
# ============================================================

reel_color = cq.Color(0.86, 0.86, 0.84)
ribbon_color = cq.Color(0.05, 0.05, 0.06)
stand_color = cq.Color(0.30, 0.31, 0.34)
jack_color = cq.Color(0.16, 0.17, 0.19)
plug_color = cq.Color(0.90, 0.82, 0.55)
steel_color = cq.Color(0.58, 0.60, 0.62)
crimper_grip_color = cq.Color(0.08, 0.30, 0.66)
klein_yellow_color = cq.Color(0.95, 0.72, 0.05)
klein_grip_color = cq.Color(0.72, 0.10, 0.10)

#: How far apart the open assembly sets the storeys: over the tallest storey, so
#: every compartment is looked into rather than past.
storey_lift = 95.0


# ============================================================
# STOREY BODIES
# ============================================================

def build_ribbon_bin():
    """One deep compartment, the ribbon reel lying in it flange down."""
    return _kit.bin_body(kit_x_u, kit_y_u, ribbon_height_u, labels=True)


def build_stand_bin():
    """One shallow compartment the length of the keystone stand."""
    return _kit.bin_body(kit_x_u, kit_y_u, stand_height_u, labels=True)


def build_terminations_bin():
    """Two compartments across the depth: jacks behind, plugs in front."""
    return _kit.bin_body(kit_x_u, kit_y_u, terminations_height_u, labels=True, width_div=1)


def build_rack():
    """The lipped blank with three head-down sockets cut down its centre line."""
    rack = _kit.blank_body(kit_x_u, kit_y_u, rack_height_u)
    for width, depth, center_y in rack_sockets():
        rack = rack.cut(
            _kit.pocket(
                width,
                depth,
                0.0,
                center_y,
                rack_socket_floor_z,
                rack_top_z,
                radius=socket_radius,
            )
        )
    return rack.clean()


def rack_sockets():
    """Each socket as `(width, depth, center_y)`, back to front."""
    return (
        (crimper_socket_width, crimper_socket_depth, crimper_socket_y),
        (punchdown_socket_width, punchdown_socket_depth, punchdown_socket_y),
        (stripper_socket_width, stripper_socket_depth, stripper_socket_y),
    )


def build_dock():
    return _kit.dock_body(kit_x_u, kit_y_u)


# ============================================================
# CONTENT REFERENCES
# ============================================================

def build_ribbon_reference():
    """The reel flange-down on the bin floor, inside the listing's parcel."""
    on_the_floor = (0.0, ribbon_parcel_center_y, storey_floor_z)
    flange = _kit.cylinder(reel_flange_diameter, reel_flange_thickness)
    reel = (
        flange.union(flange.translate((0.0, 0.0, reel_width - reel_flange_thickness)))
        .union(_kit.cylinder(reel_hub_diameter, reel_width))
        .clean()
    )
    wind = _kit.cylinder(
        reel_wind_diameter, reel_wind_width, z_bottom=reel_flange_thickness
    ).cut(_kit.cylinder(reel_hub_diameter, reel_wind_width, z_bottom=reel_flange_thickness))
    return {
        "reel": reel.translate(on_the_floor),
        "wind": wind.translate(on_the_floor),
        "fit": _kit.placed_prism(
            ribbon_parcel_x,
            ribbon_parcel_y,
            ribbon_parcel_z,
            0.0,
            ribbon_parcel_center_y,
            z_bottom=storey_floor_z,
            radius=3.0,
        ),
    }


def build_stand_reference():
    return _kit.placed_prism(
        stand_x, stand_y, stand_z, 0.0, 0.0, z_bottom=storey_floor_z, radius=stand_corner_radius
    )


def compartments(cavity):
    """The void's compartments as their own workplanes, back to front."""
    return [
        cq.Workplane("XY").newObject([solid])
        for solid in sorted(cavity.solids().vals(), key=lambda s: s.BoundingBox().ymin)
    ]


def compartment_span(compartment):
    """One compartment's `(centre y, depth)`."""
    bounds = _kit.bbox(compartment)
    return bounds.center.y, bounds.ylen


def build_jack_references(cell_center_y):
    """Ten keystone jacks in one layer, ports up, backed off the label ledge."""
    jacks = []
    for column in range(jack_columns):
        center_x = (column - (jack_columns - 1) / 2.0) * (jack_body_w + jack_gap)
        for row in range(jack_rows):
            center_y = cell_center_y + (row - (jack_rows - 1) / 2.0) * (jack_body_h + jack_gap)
            jacks.append(
                _kit.placed_prism(
                    jack_body_w,
                    jack_body_h,
                    jack_body_depth,
                    center_x,
                    center_y,
                    z_bottom=storey_floor_z,
                    radius=1.0,
                )
            )
    return jacks


def build_plug_fill_reference(cell_center_y, cell_depth):
    """Twenty 6P4C plugs as the block their loose volume fills."""
    width = 2.0 * interior_half_x - 2.0 * plug_fill_margin
    depth = cell_depth - 2.0 * plug_fill_margin
    return _kit.placed_prism(
        width,
        depth,
        plug_fill_volume / (width * depth),
        0.0,
        cell_center_y,
        z_bottom=storey_floor_z,
        radius=2.0,
    )


grip_root_width = 9.0
grip_tip_width = 13.0


def _splayed_grips(center_y, root_z, tip_z, root_half_x, tip_half_x, thickness):
    """A plier tool's two handles, opening in X from its head to their ends.

    The XZ workplane maps a drawn `(a, b)` to world `(a, 0, b)`, so the pair is
    drawn in the tool's own plane and swept through its thickness."""
    grips = []
    for x_sign in (-1.0, 1.0):
        outline = [
            (x_sign * root_half_x, root_z),
            (x_sign * tip_half_x, tip_z),
            (x_sign * (tip_half_x - grip_tip_width), tip_z),
            (x_sign * (root_half_x - grip_root_width), root_z),
        ]
        grips.append(
            cq.Workplane("XZ")
            .polyline(outline)
            .close()
            .extrude(thickness / 2.0, both=True)
            .translate((0.0, center_y, 0.0))
        )
    return grips


def build_crimper_reference():
    """VCE GJ668BL: the die head in its socket, the ratchet handles above it."""
    head = _kit.placed_prism(
        crimper_head_width_reference,
        crimper_head_thickness_reference,
        crimper_head_height_reference,
        0.0,
        crimper_socket_y,
        z_bottom=tool_seat_z,
        radius=5.0,
    )
    head_top_z = tool_seat_z + crimper_head_height_reference
    grips = _splayed_grips(
        center_y=crimper_socket_y,
        root_z=head_top_z - crimper_grip_root_drop,
        tip_z=tool_seat_z + crimper_length,
        root_half_x=crimper_head_width_reference / 2.0 - crimper_grip_root_inset,
        tip_half_x=crimper_open_width / 2.0,
        thickness=crimper_grip_thickness,
    )
    return {
        "head": head,
        "left-grip": grips[0],
        "right-grip": grips[1],
        "fit": head.union(grips[0]).union(grips[1]).clean(),
    }


def build_punchdown_reference():
    """Klein VDV427-300: blade down, the barrel holding one section all the way up."""
    blade = _kit.placed_prism(
        punchdown_width,
        punchdown_thickness,
        punchdown_blade_length,
        0.0,
        punchdown_socket_y,
        z_bottom=tool_seat_z,
        radius=3.0,
    )
    barrel = _kit.placed_prism(
        punchdown_width,
        punchdown_thickness,
        punchdown_length - punchdown_blade_length,
        0.0,
        punchdown_socket_y,
        z_bottom=tool_seat_z + punchdown_blade_length,
        radius=6.0,
    )
    return {
        "blade": blade,
        "barrel": barrel,
        "fit": blade.union(barrel).clean(),
    }


def build_stripper_reference():
    """Klein 11057: the stripping nose in its socket, the Kurve grips above it."""
    head = _kit.placed_prism(
        stripper_head_width_reference,
        stripper_head_thickness_reference,
        stripper_head_height_reference,
        0.0,
        stripper_socket_y,
        z_bottom=tool_seat_z,
        radius=4.0,
    )
    head_top_z = tool_seat_z + stripper_head_height_reference
    grips = _splayed_grips(
        center_y=stripper_socket_y,
        root_z=head_top_z - stripper_grip_root_drop,
        tip_z=tool_seat_z + stripper_length,
        root_half_x=stripper_head_width_reference / 2.0 - stripper_grip_root_inset,
        tip_half_x=stripper_open_width_reference / 2.0,
        thickness=stripper_grip_thickness,
    )
    return {
        "head": head,
        "left-grip": grips[0],
        "right-grip": grips[1],
        "fit": head.union(grips[0]).union(grips[1]).clean(),
    }


# ============================================================
# FIT CHECKS
# ============================================================

def assert_socket_in_plateau(name, width, depth, center_y):
    """A socket opens inside the blank's flat top, clear of its stacking lip."""
    if width / 2.0 > rack_plateau_half_x or abs(center_y) + depth / 2.0 > rack_plateau_half_y:
        raise ValueError(f"{name}: socket reaches outside the rack's plateau")
    edge_y = rack_plateau_half_y - (abs(center_y) + depth / 2.0)
    print(f"   {name} socket: {rack_plateau_half_x - width / 2.0:.1f} mm to the lip in x, "
          f"{edge_y:.1f} mm in y")


def assert_socket_slip(name, socket_width, socket_depth, head_width, head_depth):
    """A head-down socket stands 1.5 to 3 mm off its tool on every side."""
    slips = (
        (socket_width - head_width) / 2.0,
        (socket_depth - head_depth) / 2.0,
    )
    if any(slip < 1.5 or slip > 3.0 for slip in slips):
        raise ValueError(f"{name}: socket slip {slips} is outside 1.5-3 mm")
    print(f"   {name} slip: {slips[0]:.1f} mm across, {slips[1]:.1f} mm through")


def assert_clear_of_walls(name, reference, half_x, center_y, half_y):
    """A content keeps `wall_clearance_min` off its compartment's four walls."""
    bounds = _kit.bbox(reference)
    gaps = (
        half_x - bounds.xmax,
        bounds.xmin + half_x,
        (center_y + half_y) - bounds.ymax,
        bounds.ymin - (center_y - half_y),
    )
    if min(gaps) < wall_clearance_min:
        raise ValueError(f"{name}: {min(gaps):.2f} mm to a compartment wall")
    print(f"   {name}: {min(gaps):.1f} mm minimum wall clearance")


def assert_under_label_ledge(name, reference, height_u, cell_max_y):
    """A content either stands below the ledge or keeps its width clear of +Y."""
    bounds = _kit.bbox(reference)
    ledge_underside_z = _kit.top_reference_z(height_u) - label_ledge_height
    if bounds.zmax <= ledge_underside_z:
        print(f"   {name}: {ledge_underside_z - bounds.zmax:.1f} mm under the label ledge")
        return
    clear_y = cell_max_y - label_ledge_width - bounds.ymax
    if clear_y < wall_clearance_min:
        raise ValueError(f"{name}: stands into the label ledge by {-clear_y:.2f} mm")
    print(f"   {name}: {clear_y:.1f} mm short of the label ledge in y")


def validate(parts, storeys, seats, cavities, references):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    _kit.assert_stack_seated(parts["umbilical-dock"], storeys, seats)

    ribbon_cavity = cavities["umbilical-ribbon"]
    _kit.assert_contained("ribbon reel", references["ribbon"]["fit"], ribbon_cavity)
    assert_clear_of_walls(
        "ribbon reel", references["ribbon"]["fit"], interior_half_x, 0.0, interior_half_y
    )
    assert_under_label_ledge(
        "ribbon reel", references["ribbon"]["fit"], ribbon_height_u, interior_half_y
    )

    stand_cavity = cavities["umbilical-stand"]
    _kit.assert_contained("keystone stand", references["stand"], stand_cavity)
    assert_clear_of_walls(
        "keystone stand", references["stand"], interior_half_x, 0.0, interior_half_y
    )
    assert_under_label_ledge(
        "keystone stand", references["stand"], stand_height_u, interior_half_y
    )

    jack_cell, plug_cell = compartments(cavities["umbilical-terminations"])
    jack_cell_y, jack_cell_depth = compartment_span(jack_cell)
    plug_cell_y, plug_cell_depth = compartment_span(plug_cell)
    jack_block = _union(references["jacks"])
    _kit.assert_contained("keystone jacks", jack_block, jack_cell)
    assert_clear_of_walls(
        "keystone jacks", jack_block, interior_half_x, jack_cell_y, jack_cell_depth / 2.0
    )
    assert_under_label_ledge(
        "keystone jacks", jack_block, terminations_height_u, jack_cell_y + jack_cell_depth / 2.0
    )
    _kit.assert_contained("6P4C plugs", references["plugs"], plug_cell)
    assert_clear_of_walls(
        "6P4C plugs", references["plugs"], interior_half_x, plug_cell_y, plug_cell_depth / 2.0
    )
    assert_under_label_ledge(
        "6P4C plugs", references["plugs"], terminations_height_u, plug_cell_y + plug_cell_depth / 2.0
    )

    rack = parts["umbilical-rack"]
    for name, (width, depth, center_y) in zip(
        ("VCE crimper", "Klein VDV427-300", "Klein 11057"), rack_sockets()
    ):
        assert_socket_in_plateau(name, width, depth, center_y)
    assert_socket_slip(
        "VCE crimper",
        crimper_socket_width,
        crimper_socket_depth,
        crimper_head_width_reference,
        crimper_head_thickness_reference,
    )
    assert_socket_slip(
        "Klein VDV427-300",
        punchdown_socket_width,
        punchdown_socket_depth,
        punchdown_width,
        punchdown_thickness,
    )
    assert_socket_slip(
        "Klein 11057",
        stripper_socket_width,
        stripper_socket_depth,
        stripper_head_width_reference,
        stripper_head_thickness_reference,
    )
    for name, key in (
        ("VCE crimper", "crimper"),
        ("Klein VDV427-300", "punchdown"),
        ("Klein 11057", "stripper"),
    ):
        _kit.assert_clear(name, rack, references[key]["fit"])

    if rack_socket_floor_z <= 0.0:
        raise ValueError("a socket floor reaches the storey below")
    print(f"   socket floors: {rack_socket_floor_z:.1f} mm of rack under every tool, "
          f"{rack_socket_depth:.1f} mm of socket over it")


def _union(shapes):
    result = shapes[0]
    for shape in shapes[1:]:
        result = result.union(shape)
    return result.clean()


# ============================================================
# PRESENTATION
# ============================================================

def content_references(references, storey_index):
    """Every content envelope of the kit, as `kit_assembly` takes them."""
    ribbon, stand, terminations, rack = storey_index
    placed = [
        ("ribbon-reel", references["ribbon"]["reel"], reel_color, ribbon),
        ("ribbon-wind", references["ribbon"]["wind"], ribbon_color, ribbon),
        ("keystone-stand", references["stand"], stand_color, stand),
        ("6p4c-plugs", references["plugs"], plug_color, terminations),
    ]
    for index, jack in enumerate(references["jacks"], 1):
        placed.append((f"keystone-jack-{index}", jack, jack_color, terminations))
    placed.extend(rack_references(references, rack))
    return placed


def rack_references(references, rack):
    return [
        ("crimper-head", references["crimper"]["head"], steel_color, rack),
        ("crimper-left-grip", references["crimper"]["left-grip"], crimper_grip_color, rack),
        ("crimper-right-grip", references["crimper"]["right-grip"], crimper_grip_color, rack),
        ("punchdown-blade", references["punchdown"]["blade"], steel_color, rack),
        ("punchdown-barrel", references["punchdown"]["barrel"], klein_yellow_color, rack),
        ("stripper-head", references["stripper"]["head"], steel_color, rack),
        ("stripper-left-grip", references["stripper"]["left-grip"], klein_grip_color, rack),
        ("stripper-right-grip", references["stripper"]["right-grip"], klein_grip_color, rack),
    ]


# ============================================================
# BUILD AND EXPORT
# ============================================================

def main():
    out_dir = Path(__file__).resolve().parent

    bodies = {
        "umbilical-ribbon": build_ribbon_bin(),
        "umbilical-stand": build_stand_bin(),
        "umbilical-terminations": build_terminations_bin(),
        "umbilical-rack": build_rack(),
    }
    parts = dict(bodies)
    parts["umbilical-dock"] = build_dock()

    storeys = [
        _kit.Storey("umbilical-ribbon", bodies["umbilical-ribbon"], ribbon_height_u),
        _kit.Storey("umbilical-stand", bodies["umbilical-stand"], stand_height_u),
        _kit.Storey(
            "umbilical-terminations", bodies["umbilical-terminations"], terminations_height_u
        ),
        _kit.Storey("umbilical-rack", bodies["umbilical-rack"], rack_height_u, kind="blank"),
    ]
    seats = _kit.stack_seats(storeys)

    cavities = {
        "umbilical-ribbon": _kit.bin_cavity(
            bodies["umbilical-ribbon"], kit_x_u, kit_y_u, ribbon_height_u
        ),
        "umbilical-stand": _kit.bin_cavity(
            bodies["umbilical-stand"], kit_x_u, kit_y_u, stand_height_u
        ),
        "umbilical-terminations": _kit.bin_cavity(
            bodies["umbilical-terminations"], kit_x_u, kit_y_u, terminations_height_u
        ),
    }

    jack_cell, plug_cell = compartments(cavities["umbilical-terminations"])
    jack_cell_y, _ = compartment_span(jack_cell)
    plug_cell_y, plug_cell_depth = compartment_span(plug_cell)
    references = {
        "ribbon": build_ribbon_reference(),
        "stand": build_stand_reference(),
        "jacks": build_jack_references(jack_cell_y),
        "plugs": build_plug_fill_reference(plug_cell_y, plug_cell_depth),
        "crimper": build_crimper_reference(),
        "punchdown": build_punchdown_reference(),
        "stripper": build_stripper_reference(),
    }

    validate(parts, storeys, seats, cavities, references)

    _kit.export_parts(out_dir, parts)

    rack_index = len(storeys) - 1
    _kit.export_kit(
        out_dir,
        "umbilical-kit",
        _kit.kit_assembly(
            "umbilical-kit",
            parts["umbilical-dock"],
            storeys,
            seats,
            references=rack_references(references, rack_index),
        ),
    )
    open_seats = _kit.exploded_seats(seats, storey_lift)
    _kit.export_kit(
        out_dir,
        "umbilical-kit-open",
        _kit.kit_assembly(
            "umbilical-kit-open",
            parts["umbilical-dock"],
            storeys,
            open_seats,
            references=content_references(references, range(len(storeys))),
        ),
    )

    printed_height = seats[-1] + _kit.bbox(parts["umbilical-rack"]).zlen
    populated_height = seats[-1] + tool_seat_z + stripper_length
    tallest = max(_kit.bbox(shape).zlen for shape in parts.values())
    variables = {
        "FOOTPRINT": f"{footprint_x:.0f} mm x {footprint_y:.0f} mm",
        "PRINTED_HEIGHT": f"{printed_height:.1f} mm",
        "POPULATED_HEIGHT": f"{populated_height:.1f} mm",
        "TALLEST_PART": f"{tallest:.1f} mm",
        "H2C_ENVELOPE": (
            f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x {_kit.h2c_build_z:.0f} mm"
        ),
        "RIBBON_PARCEL": f"{ribbon_parcel_x:.0f} x {ribbon_parcel_y:.0f} x {ribbon_parcel_z:.0f} mm",
        "RIBBON_CAVITY": f"{usable_height(ribbon_height_u):.0f} mm",
        "REEL_ENVELOPE": (
            f"diameter {reel_flange_diameter:.0f} mm x {reel_width:.0f} mm"
        ),
        "STAND_ENVELOPE": f"{stand_x:.1f} x {stand_y:.1f} x {stand_z:.1f} mm",
        "JACK_ENVELOPE": f"{jack_body_w:.1f} x {jack_body_h:.1f} x {jack_body_depth:.0f} mm",
        "JACK_ARRAY": f"{jack_array_x:.1f} mm x {jack_array_y:.1f} mm",
        "PLUG_ENVELOPE": f"{plug_body_w:.2f} x {plug_height:.1f} x {plug_length:.2f} mm",
        "PLUG_FILL": f"{plug_fill_volume / 1000.0:.1f} cm^3",
        "CRIMPER_ENVELOPE": f"{crimper_length:.1f} mm x {crimper_open_width:.1f} mm",
        "PUNCHDOWN_ENVELOPE": (
            f"{punchdown_length:.1f} x {punchdown_width:.1f} x {punchdown_thickness:.1f} mm"
        ),
        "STRIPPER_ENVELOPE": f"{stripper_length:.1f} mm",
        "SOCKET_DEPTH": f"{rack_socket_depth:.0f} mm",
        "SOCKET_FLOOR": f"{rack_socket_floor_z:.0f} mm",
        "SOCKET_SLIP": f"{socket_slip:.1f} mm",
        "CELL_DEPTH": f"{plug_cell_depth:.1f} mm",
    }
    variables.update(
        {
            f"{name.split('-')[1].upper()}_PART": _kit.size_text(shape)
            for name, shape in parts.items()
        }
    )
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
