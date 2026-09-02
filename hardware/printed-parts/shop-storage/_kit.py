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
from cqgridfinity.constants import GR_BASE_CLR, GR_TOL, GRHU, GRU

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

kit_color = M_PETG_BLACK


def outer_size(units):
    """The outside of a storey across `units` grid cells."""
    return units * grid_unit - grid_clearance


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
    """The void a bin holds below its top reference: what its contents must fit inside."""
    stock = GridfinityBox(x_u, y_u, height_u, solid=True, no_lip=True).render()
    below_top = cq.Workplane("XY").box(
        outer_size(x_u) + 1.0,
        outer_size(y_u) + 1.0,
        top_reference_z(height_u),
        centered=(True, True, False),
    )
    return stock.cut(bin_shape).intersect(below_top)


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
