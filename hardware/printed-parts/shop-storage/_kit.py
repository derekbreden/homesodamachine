"""The Gridfinity vocabulary the holders are cut from.

Frame: world +Z is up, +Y is the operator-facing front, and +X is the operator's right.
Every holder is built in its print orientation with its bottom at Z=0. Every one of them
is a stock cq-gridfinity body on the 42 mm grid: an open bin, a solid lipped blank a comb
or an index is cut from, or the baseplate they all dock on. The library's label ledge
stands on the +Y wall, so a bin built here already faces the operator.

[`_holder.py`](_holder.py) is the layer above: the four shapes, and the rule about which
figures each of them is allowed to read.
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

#: The lip ring on a lipped body, measured in from its outer wall. Inside it, a solid
#: blank's top is a flat plateau at the body's top reference, and every slot and bore is
#: cut from that plateau.
lip_inset = 2.6

#: One of the library's own bins, kept for the figures it derives rather than the body
#: it renders.
_stock_bin = GridfinityBox(1, 2, 1, labels=True, width_div=1)

wall_thickness = GR_WALL
divider_thickness = GR_DIV_WALL

#: A bin's interior floor, where a content stands: the base profile's whole depth and
#: the library's own floor are under it.
bin_floor_z = GR_BOT_H

#: The label strip the ledge is drawn for and the face it is drawn at: 12 mm label
#: tape on a 10 mm overhang, before the library compensates either for the lip.
label_tape_width = _stock_bin.label_width
label_tape_height = _stock_bin.label_height

kit_color = M_PETG_BLACK


def outer_size(units):
    """The outside of a holder across `units` grid cells."""
    return units * grid_unit - grid_clearance


def inner_size(units):
    """The clear inside of a bin across `units` grid cells, wall to wall."""
    return outer_size(units) - 2.0 * wall_thickness


def top_reference_z(height_u):
    """The stacking reference of a holder `height_u` units tall; its lip rises above it."""
    return height_u * height_unit


def plateau_half(units):
    """Half the flat top of a lipped blank across `units` cells: where a cut may open."""
    return outer_size(units) / 2.0 - lip_inset


def interior_ceiling_z(height_u):
    """A bin's interior ceiling: the shelf its stacking lip stands on.

    The cavity runs on past it to the top reference, into the pocket a stacked body's
    base foot drops into. A content that stops below this ceiling is clear of anything
    stacked on top of the tub; one that stands past it is crushed by it."""
    return bin_floor_z + GridfinityBox(1, 2, height_u).int_height


# ============================================================
# COMPARTMENTS AND LAYOUT
# ============================================================

def cell_span(units, divisions):
    """One compartment's clear run across `units` cells split by `divisions` dividers.

    The library's own division formula, read without rendering a body to measure."""
    return (inner_size(units) - divider_thickness * divisions) / (divisions + 1)


# ============================================================
# STOREY BODIES
# ============================================================

def bin_body(x_u, y_u, height_u, **features):
    """An open bin with its stacking lip: a tub. `features` are the library's own:
    length_div, width_div, labels, scoops, scoop_rad, label_width, wall_th."""
    return GridfinityBox(x_u, y_u, height_u, **features).render()


def blank_body(x_u, y_u, height_u):
    """A solid lipped blank: what a comb and an index are cut from."""
    return GridfinityBox(x_u, y_u, height_u, solid=True).render()


def dock_body(x_u, y_u):
    """The bench dock: a baseplate on a solid slab."""
    return GridfinityBaseplate(
        x_u, y_u, ext_depth=dock_extra_depth, straight_bottom=True
    ).render()


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
    """A cutter for a rectangular well, open 0.2 mm past `top_z`."""
    return placed_prism(
        width, depth, top_z - floor_z + 0.2, center_x, center_y, z_bottom=floor_z, radius=radius
    )


def round_pocket(diameter, center_x, center_y, floor_z, top_z):
    """A cutter for a bore, open 0.2 mm past `top_z`."""
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


# ============================================================
# EXPORT
# ============================================================

def export_parts(out_dir, parts, color=kit_color):
    """One coloured STEP per printed part, `parts` being {file stem: shape}."""
    for name, shape in parts.items():
        out = Path(out_dir) / f"{name}.step"
        export_assembly(one_body(shape, name, color), str(out))
        print(f"-> {out.name}")


def export_assembly_step(out_dir, name, assembly):
    """One STEP for a witness assembly: a holder with what it holds beside it."""
    out = Path(out_dir) / f"{name}.step"
    export_assembly(assembly, str(out))
    print(f"-> {out.name}")


# ============================================================
# SELFTEST
# ============================================================

def selftest():
    """Every figure this module derives, against the body the library actually renders."""
    units_x, units_y, height_u = 2, 2, 3
    length_div = width_div = 1

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
    yield f"cell_span reads {span_x:.2f} x {span_y:.2f} mm, the library's own division"

    ceiling = interior_ceiling_z(height_u)
    if not bin_floor_z < ceiling < top_reference_z(height_u):
        raise AssertionError(
            f"the interior ceiling at {ceiling:.4f} mm is not under the "
            f"{top_reference_z(height_u):.4f} mm top reference"
        )
    yield (
        f"the interior ceiling stands {top_reference_z(height_u) - ceiling:.2f} mm under "
        "the top reference"
    )


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]:
        for line in selftest():
            print(" ", line)
        print("_kit selftest OK")
    else:
        sys.exit("usage: _kit.py selftest")
