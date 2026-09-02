"""Shared vocabulary of the shop-storage job kits.

Frame: world +Z is up, +Y is the operator-facing front, and +X is the operator's right.
Every storey is built in its own print orientation with its bottom at Z=0, and the kit
frame places it on the storey below by its seat. Every storey is a stock cq-gridfinity
body on the 42 mm grid: an open bin, a solid lipped blank a rack is cut from, or the
baseplate the kit docks on. The library's label ledge stands on the +Y wall, so a bin
built here already faces the operator.
"""

import sys
from pathlib import Path

import cadquery as cq
from cqgridfinity import GridfinityBaseplate, GridfinityBox
from cqgridfinity.constants import (
    GR_BASE_CLR,
    GR_BOT_H,
    GR_DIV_WALL,
    GR_TOL,
    GR_WALL,
    GRHU,
    GRU,
)

_here = Path(__file__).resolve()
_repo_root = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(0, str(_repo_root / "tools"))

from _cadq_export import export_assembly  # noqa: E402
from _materials import M_PETG_BLACK, one_body  # noqa: E402
from docgen import substitute_md  # noqa: E402,F401


# ============================================================
# GRID AND PRINTER ENVELOPE
# ============================================================

grid_unit = GRU
height_unit = GRHU
grid_clearance = GR_TOL
seat_clearance = GR_BASE_CLR

h2c_build_x = 325.0
h2c_build_y = 320.0
h2c_build_z = 320.0

dock_extra_depth = 6.0
dock_seat_z = dock_extra_depth - seat_clearance

#: The lip ring on a lipped storey, measured in from its outer wall. Inside it, a solid
#: blank's top is a flat plateau at the storey's top reference, and a rack's sockets are
#: cut from that plateau.
lip_inset = 2.6

#: One of the library's own bins, kept for the figures it derives rather than the body
#: it renders. A kit's bin carries a label ledge and may carry dividers, and both of
#: those change what the library thinks is safe to fillet.
_stock_bin = GridfinityBox(1, 2, 1, labels=True, width_div=1)

wall_thickness = GR_WALL
divider_thickness = GR_DIV_WALL

#: A bin's interior floor, where a content stands: the base profile's whole depth and
#: the library's own floor are under it.
bin_floor_z = GR_BOT_H

#: The radius the library rolls into every interior corner of a compartment — floor
#: into wall, and wall into wall. A content standing on the floor clears the fillet
#: before it clears the wall, so clearance is measured from above it.
interior_fillet = _stock_bin.safe_fillet_rad

#: The label strip the ledge is drawn for and the face it is drawn at: 12 mm label
#: tape on a 10 mm overhang, before the library compensates either for the lip.
label_tape_width = _stock_bin.label_width
label_tape_height = _stock_bin.label_height

kit_color = M_PETG_BLACK


def outer_size(units):
    """The outside of a storey across `units` grid cells."""
    return units * grid_unit - grid_clearance


def inner_size(units):
    """The clear inside of a bin across `units` grid cells, wall to wall."""
    return outer_size(units) - 2.0 * wall_thickness


def top_reference_z(height_u):
    """The stacking reference of a storey `height_u` units tall; its lip rises above it."""
    return height_u * height_unit


def seat_on_bin_z(height_u):
    """Where the next storey's Z=0 lands on an open bin of `height_u`.

    A bin's label ledge and its dividers rise to its top reference, and the storey
    above stands on them. A bin with neither seats the next storey on its lip chamfer,
    0.35 mm lower, and `assert_stack_seated` refuses it: every bin in a kit carries a
    ledge or a divider."""
    return top_reference_z(height_u)


def seat_on_blank_z(height_u):
    """Where the next storey's Z=0 lands on a solid lipped blank of `height_u`."""
    return top_reference_z(height_u)


def plateau_half(units):
    """Half the flat top of a lipped blank across `units` cells: where sockets may open."""
    return outer_size(units) / 2.0 - lip_inset


def cavity_depth(height_u):
    """Floor to top reference: the whole void `bin_cavity` returns, and how tall a thing
    standing in a storey `height_u` units tall may be."""
    return top_reference_z(height_u) - bin_floor_z


def interior_ceiling_z(height_u):
    """A bin's interior ceiling: the shelf its stacking lip stands on.

    `bin_cavity` runs on past it to the top reference, into the pocket the next storey's
    base foot drops into. A content that stops below this ceiling meets nothing when the
    kit closes; one that passes containment above it is crushed by the storey above."""
    return bin_floor_z + GridfinityBox(1, 2, height_u).int_height


def label_ledge_drop(height_u, divider=False):
    """How far the library's label ledge hangs below a storey's top reference.

    The ledge on the bin's own +Y wall is the deeper of the two the library draws; the
    one along a divider is shallower, having no lip to clear. `bin_cavity` leaves both
    out of the void, so a compartment's top is shorter at its +Y end than at the other."""
    return GridfinityBox(1, 2, height_u, labels=True).safe_label_height(
        backwall=not divider
    )


def label_ledge_reach(divider=False):
    """How far inboard that ledge reaches: the label strip, and on the +Y wall the lip
    its width is compensated for.

    The ledge the library draws stops a wall's thickness short of this, so a content
    that keeps this much off the +Y end stands clear of the ledge at any height."""
    return label_tape_width + (0.0 if divider else lip_inset)


# ============================================================
# COMPARTMENTS AND LAYOUT
# ============================================================

def centered_run(count, pitch, center=0.0):
    """The centres of `count` features at `pitch`, the run centred on `center`."""
    run = (count - 1) * pitch
    return [center - run / 2.0 + index * pitch for index in range(count)]


def run_span(count, pitch, size):
    """Edge to edge across `count` features of `size` at `pitch`."""
    return (count - 1) * pitch + size


def spread_pitch(count, size, span):
    """The pitch that spreads `count` features of `size` evenly over `span`."""
    return (span - size) / (count - 1)


def cell_span(units, divisions):
    """One compartment's clear run across `units` cells split by `divisions` dividers.

    The library's own division formula, read without rendering a body to measure."""
    return (inner_size(units) - divider_thickness * divisions) / (divisions + 1)


def cell_centers(units, divisions):
    """Each compartment's centre across `units` cells, low side first."""
    return centered_run(divisions + 1, cell_span(units, divisions) + divider_thickness)


def cell_floor_area(x_u, y_u, length_div=0, width_div=0, margin=0.0):
    """The floor one compartment offers, inside `margin` of air at each of its walls."""
    return (cell_span(x_u, length_div) - 2.0 * margin) * (
        cell_span(y_u, width_div) - 2.0 * margin
    )


# ============================================================
# STOREY BODIES
# ============================================================

def bin_body(x_u, y_u, height_u, **features):
    """An open bin with its stacking lip. `features` are the library's own: length_div,
    width_div, labels, scoops, scoop_rad, label_width, wall_th."""
    return GridfinityBox(x_u, y_u, height_u, **features).render()


def blank_body(x_u, y_u, height_u):
    """A solid lipped blank: rack stock, and a seat for the storey above."""
    return GridfinityBox(x_u, y_u, height_u, solid=True).render()


def dock_body(x_u, y_u):
    """The bench dock: a baseplate on a solid slab."""
    return GridfinityBaseplate(
        x_u, y_u, ext_depth=dock_extra_depth, straight_bottom=True
    ).render()


def bin_cavity(bin_shape, x_u, y_u, height_u):
    """The void a bin holds below its top reference: what its contents must fit inside.

    One void per compartment, so a divided bin returns one solid per cell. A bin
    built with `labels=True` carries a label ledge over the +Y end of every
    compartment, and the ledge is not in the void: the top of a cell is shorter
    at that end than at the other. A tall thing centred in its cell reads as
    standing outside it, and the answer is the content's own place — back off +Y,
    or stand lower — not a wider cavity.
    """
    stock = GridfinityBox(x_u, y_u, height_u, solid=True, no_lip=True).render()
    below_top = cq.Workplane("XY").box(
        outer_size(x_u) + 1.0,
        outer_size(y_u) + 1.0,
        top_reference_z(height_u),
        centered=(True, True, False),
    )
    return stock.cut(bin_shape).intersect(below_top)


def bin_cells(cavity):
    """`bin_cavity`'s compartments in reading order: the front row first, and left to
    right within a row.

    The cavity carries one solid per compartment and no order of its own, so a content
    checked against the whole of it reads only as standing in some cell. Checked against
    its own cell, it reads as standing in the one the contents map gives it."""
    solids = sorted(
        cavity.solids().vals(),
        key=lambda solid: (
            -round(solid.BoundingBox().center.y, 1),
            round(solid.BoundingBox().center.x, 1),
        ),
    )
    return [cq.Workplane(obj=solid) for solid in solids]


# ============================================================
# ENVELOPES, SOCKETS AND WELLS
# ============================================================

def rounded_prism(width, depth, height, z_bottom=0.0, radius=0.0):
    """A centered XY prism with only its vertical corners rounded."""
    shape = (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(True, True, False))
        .translate((0.0, 0.0, z_bottom))
    )
    if radius > 0.0:
        shape = shape.edges("|Z").fillet(radius)
    return shape


def placed_prism(width, depth, height, center_x, center_y, z_bottom=0.0, radius=0.0):
    return rounded_prism(width, depth, height, z_bottom, radius).translate(
        (center_x, center_y, 0.0)
    )


def cylinder(diameter, height, center_x=0.0, center_y=0.0, z_bottom=0.0):
    return (
        cq.Workplane("XY")
        .circle(diameter / 2.0)
        .extrude(height)
        .translate((center_x, center_y, z_bottom))
    )


def lying_cylinder(diameter, length, center_y=0.0, center_z=0.0, center_x=0.0):
    """A cylinder on its side, axis along X, centred on the point given: how a rod, a
    drill or a length of stock lies in a bin."""
    return (
        cylinder(diameter, length)
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), 90.0)
        .translate((center_x - length / 2.0, center_y, center_z))
    )


def cone(bottom_diameter, top_diameter, height, center_x=0.0, center_y=0.0, z_bottom=0.0):
    """A frustum standing on its bottom face: a drill point, a tap's taper threads, a
    countersink head, a centring point."""
    return (
        cq.Workplane("XY")
        .circle(bottom_diameter / 2.0)
        .workplane(offset=height)
        .circle(top_diameter / 2.0)
        .loft()
        .translate((center_x, center_y, z_bottom))
    )


def pocket(width, depth, center_x, center_y, floor_z, top_z, radius=3.0):
    """A cutter for a rectangular socket or well, open 0.2 mm past `top_z`."""
    return placed_prism(
        width, depth, top_z - floor_z + 0.2, center_x, center_y, z_bottom=floor_z, radius=radius
    )


def round_pocket(diameter, center_x, center_y, floor_z, top_z):
    """A cutter for a round socket or well, open 0.2 mm past `top_z`."""
    return cylinder(diameter, top_z - floor_z + 0.2, center_x, center_y, floor_z)


def socket_ring(pocket_width, pocket_depth, center_x, center_y, bottom_z, top_z, wall=3.0, radius=5.0):
    """A standing collar around a head-down tool socket, for a tower's rack."""
    outer = placed_prism(
        pocket_width + 2.0 * wall,
        pocket_depth + 2.0 * wall,
        top_z - bottom_z,
        center_x,
        center_y,
        z_bottom=bottom_z,
        radius=radius,
    )
    inner = placed_prism(
        pocket_width,
        pocket_depth,
        top_z - bottom_z + 0.2,
        center_x,
        center_y,
        z_bottom=bottom_z - 0.1,
        radius=max(radius - wall, 1.0),
    )
    return outer.cut(inner)


# ============================================================
# THE STACK
# ============================================================

class Storey:
    """One stacked body: `kind` is "bin" (open, lipped) or "blank" (solid, lipped)."""

    def __init__(self, name, shape, height_u, kind="bin"):
        if kind not in ("bin", "blank"):
            raise ValueError(f"{name}: storey kind {kind!r} is not bin or blank")
        self.name = name
        self.shape = shape
        self.height_u = height_u
        self.kind = kind

    def seat_above(self):
        """Where the next storey's Z=0 lands, in this storey's own frame."""
        if self.kind == "bin":
            return seat_on_bin_z(self.height_u)
        return seat_on_blank_z(self.height_u)


def stack_seats(storeys):
    """The kit-frame Z of each storey, bottom to top, the first on the dock at Z=0."""
    seats = []
    z = dock_seat_z
    for storey in storeys:
        seats.append(z)
        z += storey.seat_above()
    return seats


def exploded_seats(seats, lift):
    """The same storeys lifted apart by `lift` per storey, the bottom one staying put."""
    return [z + lift * index for index, z in enumerate(seats)]


def kit_assembly(name, dock, storeys, seats, references=(), color=kit_color):
    """The kit in its own frame. `references` are (name, shape, color, storey_index)
    envelopes of what the kit holds, each riding with its storey."""
    assembly = cq.Assembly(name=name)
    assembly.add(dock, name=f"{name}-dock", color=color)
    for storey, z in zip(storeys, seats):
        assembly.add(
            storey.shape,
            name=storey.name,
            loc=cq.Location(cq.Vector(0.0, 0.0, z)),
            color=color,
        )
    for ref_name, shape, ref_color, storey_index in references:
        assembly.add(
            shape,
            name=ref_name,
            loc=cq.Location(cq.Vector(0.0, 0.0, seats[storey_index])),
            color=ref_color,
        )
    return assembly


# ============================================================
# FIT CHECKS
# ============================================================

def bbox(shape):
    return shape.val().BoundingBox()


def size_text(shape):
    b = bbox(shape)
    return f"{b.xlen:.1f} x {b.ylen:.1f} x {b.zlen:.1f} mm"


def assert_one_solid(name, shape):
    count = len(shape.solids().vals())
    if count != 1:
        raise ValueError(f"{name}: expected one solid, found {count}")


def assert_h2c_fit(name, shape):
    b = bbox(shape)
    size = (b.xlen, b.ylen, b.zlen)
    limits = (h2c_build_x, h2c_build_y, h2c_build_z)
    if any(part > limit + 1e-6 for part, limit in zip(size, limits)):
        raise ValueError(f"{name}: {size} exceeds H2C left-nozzle envelope {limits}")
    print(f"   {name}: {size[0]:.1f} x {size[1]:.1f} x {size[2]:.1f} mm")


def overlap_volume(a, b):
    return a.intersect(b).val().Volume()


def assert_seated(name, lower, upper, upper_z, max_overlap=0.05, max_gap=0.02):
    """`upper` at `upper_z` in `lower`'s frame touches it and enters it nowhere."""
    placed = upper.translate((0.0, 0.0, upper_z))
    overlap = overlap_volume(lower, placed)
    gap = lower.val().distance(placed.val())
    if overlap > max_overlap:
        raise ValueError(f"{name}: {overlap:.3f} mm^3 interface overlap")
    if gap > max_gap:
        raise ValueError(f"{name}: {gap:.3f} mm interface gap")
    print(f"   {name}: {overlap:.4f} mm^3 overlap, {gap:.4f} mm gap")


def assert_stack_seated(dock, storeys, seats):
    """Every interface of a kit: the dock under the first storey, each storey under the next."""
    assert_seated(f"dock to {storeys[0].name}", dock, storeys[0].shape, seats[0])
    for lower, upper, lower_z, upper_z in zip(storeys, storeys[1:], seats, seats[1:]):
        assert_seated(
            f"{lower.name} to {upper.name}", lower.shape, upper.shape, upper_z - lower_z
        )


def assert_clear(name, body, reference, max_overlap=0.02):
    """A stored thing's envelope enters the printed body nowhere."""
    overlap = overlap_volume(body, reference)
    if overlap > max_overlap:
        raise ValueError(f"{name}: {overlap:.3f} mm^3 intersects the printed body")
    print(f"   {name}: {overlap:.4f} mm^3 body overlap")


def assert_contained(name, reference, cavity, max_outside=0.05):
    """A stored thing's envelope lies wholly inside the void that holds it."""
    outside = reference.cut(cavity).val().Volume()
    if outside > max_outside:
        raise ValueError(f"{name}: {outside:.3f} mm^3 stands outside its compartment")
    print(f"   {name}: {outside:.4f} mm^3 outside its compartment")


def assert_clearance(name, reference, cavity, margin, max_outside=0.05):
    """A stored thing keeps `margin` of air to its compartment on every side.

    `assert_contained` says a thing is inside; this says how much room is around it.
    The probe is the thing's own footprint grown by `margin`, run from above the floor
    fillet and carrying the compartment's own corner radius: the library rolls the floor
    into the walls and the walls into each other, and a probe that ignores either reads
    as outside a cavity the thing stands well inside."""
    bounds = bbox(reference)
    floor_z = max(bounds.zmin, bbox(cavity).zmin + interior_fillet)
    probe = placed_prism(
        bounds.xlen + 2.0 * margin,
        bounds.ylen + 2.0 * margin,
        bounds.zmax - floor_z,
        bounds.center.x,
        bounds.center.y,
        z_bottom=floor_z,
        radius=interior_fillet,
    )
    outside = probe.cut(cavity).val().Volume()
    if outside > max_outside:
        raise ValueError(
            f"{name}: {outside:.3f} mm^3 of a {margin:.1f} mm clearance stands outside "
            "its compartment"
        )
    print(f"   {name}: {margin:.1f} mm clear of its compartment")


def assert_under_ceiling(name, shape, height_u, headroom=0.0):
    """A stored thing stops `headroom` clear of the bin's interior ceiling.

    Containment does not say this on its own: `bin_cavity` runs up into the lip pocket
    the storey above lands its base foot in."""
    gap = interior_ceiling_z(height_u) - bbox(shape).zmax
    if gap < headroom:
        raise ValueError(
            f"{name}: {gap:.2f} mm under the interior ceiling, "
            f"wanted {headroom:.2f} mm"
        )
    print(f"   {name}: {gap:.2f} mm under the interior ceiling")
    return gap


def assert_inside_plateau(name, reach_x, reach_y, x_u, y_u=None, margin=0.0):
    """A socket cut from a rack opens inside the plateau, never through the lip ring.

    `reach_x` and `reach_y` are how far the socket runs from the storey's centre line.
    Past the plateau a socket opens into the stacking lip, and the storey above loses
    the ring it seats on."""
    half_x = plateau_half(x_u)
    half_y = plateau_half(x_u if y_u is None else y_u)
    slack = min(half_x - reach_x, half_y - reach_y)
    if slack < margin:
        raise ValueError(
            f"{name}: reaches {reach_x:.2f} x {reach_y:.2f} mm of a "
            f"{half_x:.2f} x {half_y:.2f} mm plateau"
        )
    print(f"   {name}: {slack:.2f} mm inside the plateau")
    return slack


# ============================================================
# EXPORT
# ============================================================

def export_parts(out_dir, parts, color=kit_color):
    """One coloured STEP per printed part, `parts` being {file stem: shape}."""
    for name, shape in parts.items():
        out = Path(out_dir) / f"{name}.step"
        export_assembly(one_body(shape, name, color), str(out))
        print(f"-> {out.name}")


def export_kit(out_dir, name, assembly):
    out = Path(out_dir) / f"{name}.step"
    export_assembly(assembly, str(out))
    print(f"-> {out.name}")


# ============================================================
# SELFTEST
# ============================================================

def _refuses(call):
    """`call` raises rather than passing the thing it is asked to refuse."""
    try:
        call()
    except ValueError:
        return True
    return False


def selftest():
    """Every figure this module derives, against the body the library actually renders."""
    units_x, units_y, height_u = 2, 2, 3
    length_div = width_div = 1

    if centered_run(4, 10.0, 5.0) != [-10.0, 0.0, 10.0, 20.0]:
        raise AssertionError("centered_run does not centre its run")
    if abs(run_span(4, 10.0, 6.0) - 36.0) > 1e-9:
        raise AssertionError("run_span is not edge to edge")
    if abs(spread_pitch(5, 8.0, 100.0) - 23.0) > 1e-9:
        raise AssertionError("spread_pitch does not fill its span")
    yield "centered_run, run_span and spread_pitch agree with arithmetic"

    box = GridfinityBox(
        units_x, units_y, height_u, labels=True,
        length_div=length_div, width_div=width_div,
    )
    span_x, span_y = cell_span(units_x, length_div), cell_span(units_y, width_div)
    library_span_x = (box.inner_l - divider_thickness * length_div) / (length_div + 1)
    library_span_y = (box.inner_w - divider_thickness * width_div) / (width_div + 1)
    if abs(span_x - library_span_x) > 1e-9 or abs(span_y - library_span_y) > 1e-9:
        raise AssertionError(
            f"cell_span reads {span_x:.4f} x {span_y:.4f} mm against the library's "
            f"{library_span_x:.4f} x {library_span_y:.4f} mm"
        )
    if abs(cell_floor_area(units_x, units_y, length_div, width_div) - span_x * span_y) > 1e-9:
        raise AssertionError("cell_floor_area is not its two spans multiplied")
    if abs(cell_centers(units_y, width_div)[0] + (span_y + divider_thickness) / 2.0) > 1e-9:
        raise AssertionError("cell_centers does not pitch a compartment by its divider")
    yield f"cell_span reads {span_x:.2f} x {span_y:.2f} mm, the library's own division"

    shape = bin_body(
        units_x, units_y, height_u, labels=True,
        length_div=length_div, width_div=width_div,
    )
    cavity = bin_cavity(shape, units_x, units_y, height_u)
    cells = bin_cells(cavity)
    if len(cells) != (length_div + 1) * (width_div + 1):
        raise AssertionError(
            f"{len(cells)} cells out of a bin divided into "
            f"{(length_div + 1) * (width_div + 1)}"
        )
    wanted = [
        (x, y)
        for y in reversed(cell_centers(units_y, width_div))
        for x in cell_centers(units_x, length_div)
    ]
    found = [(bbox(cell).center.x, bbox(cell).center.y) for cell in cells]
    if any(
        abs(a - b) > 0.05
        for place, want in zip(found, wanted)
        for a, b in zip(place, want)
    ):
        raise AssertionError(
            f"bin_cells reads {found} rather than the {wanted} the division formula gives"
        )
    yield f"bin_cells reads {len(cells)} compartments front row first, left to right"

    front, back = cells[0], cells[-1]
    for cell, divider, side in ((front, False, "+Y wall"), (back, True, "divider")):
        bounds = bbox(cell)
        corners = cell.vertices().vals()
        full_depth_z = max(c.Z for c in corners if abs(c.Y - bounds.ymax) < 0.05)
        top_y = max(c.Y for c in corners if abs(c.Z - bounds.zmax) < 0.05)
        drop = top_reference_z(height_u) - full_depth_z
        reach = bounds.ymax - top_y
        if not 0.0 < drop <= label_ledge_drop(height_u, divider) + 1e-6:
            raise AssertionError(
                f"the {side} ledge drops {drop:.4f} mm, past the "
                f"{label_ledge_drop(height_u, divider):.4f} mm the reader allows"
            )
        if not 0.0 < reach <= label_ledge_reach(divider) + 1e-6:
            raise AssertionError(
                f"the {side} ledge reaches {reach:.4f} mm, past the "
                f"{label_ledge_reach(divider):.4f} mm the reader allows"
            )
        yield f"the {side} ledge drops {drop:.2f} mm and reaches {reach:.2f} mm, inside the reader"

    ceiling = interior_ceiling_z(height_u)
    if not bin_floor_z < ceiling < top_reference_z(height_u):
        raise AssertionError(
            f"the interior ceiling at {ceiling:.4f} mm is not under the "
            f"{top_reference_z(height_u):.4f} mm top reference"
        )
    if abs(cavity_depth(height_u) - (top_reference_z(height_u) - bin_floor_z)) > 1e-9:
        raise AssertionError("cavity_depth is not floor to top reference")
    if abs(bbox(cavity).zmax - top_reference_z(height_u)) > 1e-6:
        raise AssertionError(
            "bin_cavity does not run to the top reference, so containment does not "
            "reach into the lip pocket and this check has nothing to catch"
        )
    front_y = bbox(front).center.y
    to_ceiling = cylinder(8.0, ceiling - bin_floor_z, 0.0, front_y, bin_floor_z)
    assert_under_ceiling("a content stopped at the ceiling", to_ceiling, height_u)
    to_top = cylinder(8.0, cavity_depth(height_u), 0.0, front_y, bin_floor_z)
    if not _refuses(
        lambda: assert_under_ceiling("a content standing to the top", to_top, height_u)
    ):
        raise AssertionError(
            "assert_under_ceiling passed a content that stands into the lip pocket"
        )
    yield (
        f"the interior ceiling stands {top_reference_z(height_u) - ceiling:.2f} mm under "
        "the top reference the cavity reaches"
    )

    bounds = bbox(front)
    sitter = placed_prism(
        span_x - 6.0,
        bounds.ylen - label_ledge_reach() - 6.0,
        6.0,
        bounds.center.x,
        bounds.ymin + (bounds.ylen - label_ledge_reach()) / 2.0,
        z_bottom=bin_floor_z,
    )
    assert_clearance("a content with room around it", sitter, front, 2.0)
    if not _refuses(lambda: assert_clearance("a content with none", sitter, front, 6.0)):
        raise AssertionError("assert_clearance passed a content with no room around it")
    floor_probe = placed_prism(
        span_x, bounds.ylen - label_ledge_reach(), 6.0,
        bounds.center.x,
        bounds.ymin + (bounds.ylen - label_ledge_reach()) / 2.0,
        z_bottom=bin_floor_z,
    )
    if floor_probe.cut(front).val().Volume() <= 0.05:
        raise AssertionError(
            "a full-width block reads as contained at the floor — the floor fillet this "
            "check is built around is not there"
        )
    yield f"assert_clearance measures room around a content past the {interior_fillet:.2f} mm floor fillet"

    half = plateau_half(units_x)
    assert_inside_plateau("a socket on the plateau", half - 2.0, half - 2.0, units_x)
    if not _refuses(
        lambda: assert_inside_plateau("a socket through the lip", half + 0.1, 0.0, units_x)
    ):
        raise AssertionError("assert_inside_plateau passed a socket cut through the lip")
    if not _refuses(
        lambda: assert_inside_plateau("a socket short of its margin", half - 1.0, 0.0,
                                      units_x, margin=2.0)
    ):
        raise AssertionError("assert_inside_plateau ignored its margin")
    yield f"assert_inside_plateau holds sockets inside a {half:.2f} mm plateau half-span"

    frustum = bbox(cone(10.0, 4.0, 8.0, 1.0, 2.0, 3.0))
    if abs(frustum.xlen - 10.0) > 1e-6 or abs(frustum.zlen - 8.0) > 1e-6:
        raise AssertionError("cone does not stand on its wide end")
    rod = bbox(lying_cylinder(6.0, 40.0, 2.0, 5.0))
    if abs(rod.xlen - 40.0) > 1e-6 or abs(rod.zlen - 6.0) > 1e-6:
        raise AssertionError("lying_cylinder does not lie along X")
    if abs(rod.center.y - 2.0) > 1e-6 or abs(rod.center.z - 5.0) > 1e-6:
        raise AssertionError("lying_cylinder is not centred on the point it is given")
    yield "cone stands on its wide end and lying_cylinder lies along X"


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]:
        for line in selftest():
            print(" ", line)
        print("_kit selftest OK")
    else:
        sys.exit("usage: _kit.py selftest")
