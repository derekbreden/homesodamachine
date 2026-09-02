"""Fastener job stack.

Frame: world +Z is up, world +Y is the operator-facing front, and world +X is
the operator's right. Every storey is a stock cq-gridfinity bin built in its
own print orientation with its bottom at Z=0; `_kit` seats them into the kit
frame on the bench dock.

Every bin of this kit is the same body: a 3 x 3 open bin divided lengthwise
into troughs that run front to back, with the library's label ledge along the
+Y wall over their open ends. One trough per SKU in the three stock storeys,
and the trough count is what separates one storey from the next.

A compartment's contents are one block of loose fill, its footprint the trough
inside the hand clearance and clear of the label ledge, its height whatever the
pack's solid volume needs at the loose-fill fraction below.
"""

import math
import sys
from pathlib import Path

import cadquery as cq
from cqgridfinity import GridfinityBox
from cqgridfinity.constants import GR_BOT_H, GR_DIV_WALL, GR_FILLET, GR_WALL

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import _kit  # noqa: E402
from _kit import substitute_md  # noqa: E402


# ============================================================
# FOOTPRINT AND TROUGHS
# ============================================================

footprint_x_u = 3
footprint_y_u = 3

trough_span = _kit.outer_size(footprint_x_u) - 2.0 * GR_WALL
trough_half_span = trough_span / 2.0
bin_floor_z = GR_BOT_H
interior_fillet_radius = GR_FILLET


def stock_bin(height_u=1, **features):
    """The library's own box, for the dimensions it derives rather than the body."""
    return GridfinityBox(footprint_x_u, footprint_y_u, height_u, **features)


def trough_width(troughs):
    """The clear width of one trough of a storey divided into `troughs` of them."""
    return (trough_span - GR_DIV_WALL * (troughs - 1)) / troughs


def trough_center_x(index, troughs):
    """The centre of trough `index`, counted from -X."""
    return (index - (troughs - 1) / 2.0) * (trough_width(troughs) + GR_DIV_WALL)


def interior_ceiling_z(height_u):
    """The bin's interior ceiling, under the stacking lip's own shelf. A fill stops
    below it, so the base foot of the storey above never meets the fill."""
    return bin_floor_z + stock_bin(height_u).int_height


#: How far the label ledge reaches inboard of the +Y wall: the library's label strip
#: plus the lip its width is compensated for. The ledge is a wedge under that reach,
#: so a fill that stops this far short of the wall stands clear of it at any height.
label_ledge_reach = stock_bin().label_width + _kit.lip_inset

content_clearance = 2.0
wall_clearance = 1.0
fill_headroom = 1.0

fill_y_max = trough_half_span - label_ledge_reach
fill_y_min = -trough_half_span + content_clearance
fill_depth = fill_y_max - fill_y_min
fill_center_y = (fill_y_max + fill_y_min) / 2.0
fill_corner_radius = 2.0


def fill_width(troughs):
    return trough_width(troughs) - 2.0 * content_clearance


def trough_capacity(troughs, height_u):
    """All the fill one trough of that storey can take."""
    depth = interior_ceiling_z(height_u) - bin_floor_z
    return fill_width(troughs) * fill_depth * depth


#: Loose fasteners tipped into a trough stand off each other: the heap is the pack's
#: solid volume over this fraction.
loose_fill_fraction = 0.45


# ============================================================
# PUBLIC PIECE ENVELOPES
# ============================================================

def cylinder_volume(diameter, height):
    return math.pi * (diameter / 2.0) ** 2 * height


def screw_volume(head_diameter, head_height, thread_diameter, length):
    """A socket head cap screw: its head over its shank, the length under the head."""
    return cylinder_volume(head_diameter, head_height) + cylinder_volume(
        thread_diameter, length
    )


def washer_volume(outer_diameter, inner_diameter, thickness):
    return cylinder_volume(outer_diameter, thickness) - cylinder_volume(
        inner_diameter, thickness
    )


m2_thread_diameter = 2.0
m3_thread_diameter = 3.0
m5_thread_diameter = 5.0

din912_m2_head_diameter = 3.80
din912_m2_head_height = 2.00
din912_m3_head_diameter = 5.50
din912_m3_head_height = 3.00
din912_m5_head_diameter = 8.50
din912_m5_head_height = 5.00

# McMaster publishes no head dimension for the 91223A ultra-low-profile family; this
# head is generous against every published ultra-low M3 head.
ulp_m3_head_diameter = 6.0
ulp_m3_head_height = 1.5

ruthex_m2_diameter = 3.6
ruthex_m2_length = 4.0
ruthex_m3_short_diameter = 4.6
ruthex_m3_short_length = 4.0
ruthex_m5_diameter = 7.1
ruthex_m5_length = 9.5

fender_washer_outer_diameter = 25.0
fender_washer_inner_diameter = 5.0
# The listing gives the two diameters and not the thickness; a fender washer this wide
# is 1.2 mm to 1.5 mm of 304, and the generous end is what the compartment is sized on.
fender_washer_thickness = 1.5

magnet_diameter = 3.0
magnet_thickness = 1.0

membrane_diameter = 13.0
# The listing gives the diameter and the 0.45 µm pore and not the thickness; a supported
# PTFE membrane disc runs 0.05 mm to 0.15 mm, and the generous end sizes the fill.
membrane_thickness = 0.15


# ============================================================
# CONTENT COLOURS
# ============================================================

brass_color = cq.Color(0.72, 0.56, 0.24)
black_oxide_color = cq.Color(0.24, 0.23, 0.22)
stainless_color = cq.Color(0.63, 0.65, 0.67)
nickel_color = cq.Color(0.82, 0.84, 0.87)
ptfe_color = cq.Color(0.93, 0.93, 0.90)


# ============================================================
# THE COMPARTMENTS
# ============================================================

class Content:
    """One SKU's compartment: the pack on hand, and the solid volume of one piece."""

    def __init__(self, key, name, count, piece_volume, color):
        self.key = key
        self.name = name
        self.count = count
        self.piece_volume = piece_volume
        self.color = color

    @property
    def fill_volume(self):
        return self.count * self.piece_volume / loose_fill_fraction

    def fill_height(self, troughs):
        return self.fill_volume / (fill_width(troughs) * fill_depth)


m5_storey_height_u = 6
m5_contents = (
    Content(
        "M5X10",
        "MewuDecor M5 x 10 SHCS",
        100,
        screw_volume(
            din912_m5_head_diameter, din912_m5_head_height, m5_thread_diameter, 10.0
        ),
        black_oxide_color,
    ),
    Content(
        "M5WASHER",
        "M5 x 25 fender washers",
        60,
        washer_volume(
            fender_washer_outer_diameter,
            fender_washer_inner_diameter,
            fender_washer_thickness,
        ),
        stainless_color,
    ),
    Content(
        "RUTHEXM5",
        "ruthex M5 inserts",
        50,
        cylinder_volume(ruthex_m5_diameter, ruthex_m5_length),
        brass_color,
    ),
)

m3_storey_height_u = 5
m3_contents = (
    Content(
        "M3X25",
        "BNUOK M3 x 25 black oxide",
        60,
        screw_volume(
            din912_m3_head_diameter, din912_m3_head_height, m3_thread_diameter, 25.0
        ),
        black_oxide_color,
    ),
    Content(
        "M3X12SS",
        "BNUOK M3 x 12 304 SS",
        120,
        screw_volume(
            din912_m3_head_diameter, din912_m3_head_height, m3_thread_diameter, 12.0
        ),
        stainless_color,
    ),
    Content(
        "M3X12",
        "BNUOK M3 x 12 black oxide",
        120,
        screw_volume(
            din912_m3_head_diameter, din912_m3_head_height, m3_thread_diameter, 12.0
        ),
        black_oxide_color,
    ),
    Content(
        "M3X10",
        "BNUOK M3 x 10 black oxide",
        120,
        screw_volume(
            din912_m3_head_diameter, din912_m3_head_height, m3_thread_diameter, 10.0
        ),
        black_oxide_color,
    ),
    Content(
        "M3X8",
        "BNUOK M3 x 8 black oxide",
        120,
        screw_volume(
            din912_m3_head_diameter, din912_m3_head_height, m3_thread_diameter, 8.0
        ),
        black_oxide_color,
    ),
)

small_storey_height_u = 4
small_contents = (
    Content(
        "RUTHEXM3",
        "ruthex M3 short inserts",
        100,
        cylinder_volume(ruthex_m3_short_diameter, ruthex_m3_short_length),
        brass_color,
    ),
    Content(
        "RUTHEXM2",
        "ruthex M2 inserts",
        70,
        cylinder_volume(ruthex_m2_diameter, ruthex_m2_length),
        brass_color,
    ),
    Content(
        "M2X6",
        "Sutemribor M2 x 6 black oxide",
        105,
        screw_volume(
            din912_m2_head_diameter, din912_m2_head_height, m2_thread_diameter, 6.0
        ),
        black_oxide_color,
    ),
    Content(
        "ULPM3X6",
        "McMaster 91223A412 M3 x 6 ultra-low-profile",
        100,
        screw_volume(
            ulp_m3_head_diameter, ulp_m3_head_height, m3_thread_diameter, 6.0
        ),
        stainless_color,
    ),
    Content(
        "ULPM3X8",
        "McMaster 91223A413 M3 x 8 ultra-low-profile",
        100,
        screw_volume(
            ulp_m3_head_diameter, ulp_m3_head_height, m3_thread_diameter, 8.0
        ),
        stainless_color,
    ),
    Content(
        "MAGNET",
        "neodymium 3 x 1 discs",
        100,
        cylinder_volume(magnet_diameter, magnet_thickness),
        nickel_color,
    ),
    Content(
        "MEMBRANE",
        "LVDALAB PTFE membranes ø13",
        100,
        cylinder_volume(membrane_diameter, membrane_thickness),
        ptfe_color,
    ),
)

#: The tray stands empty between jobs: what it holds is drawn from the storeys under
#: it while they are set out on the bench.
tray_storey_height_u = 2
tray_troughs = 3

storey_contents = (
    ("fasteners-m5", m5_storey_height_u, m5_contents),
    ("fasteners-m3", m3_storey_height_u, m3_contents),
    ("fasteners-small", small_storey_height_u, small_contents),
)

exploded_lift = 62.0


# ============================================================
# BODIES
# ============================================================

def build_trough_bin(height_u, troughs):
    """A storey: an open 3 x 3 bin cut into `troughs` front-to-back troughs, each
    with the label ledge over its +Y end."""
    return _kit.bin_body(
        footprint_x_u, footprint_y_u, height_u, length_div=troughs - 1, labels=True
    )


def build_fill(content, index, troughs):
    """The heap of one pack, standing on its trough's floor."""
    return _kit.placed_prism(
        fill_width(troughs),
        fill_depth,
        content.fill_height(troughs),
        trough_center_x(index, troughs),
        fill_center_y,
        z_bottom=bin_floor_z,
        radius=fill_corner_radius,
    )


def build_trough_probe(index, troughs, height_u):
    """The fill footprint grown across by the wall clearance, run from over the
    trough's floor fillet to the highest a fill in that storey may stand. Contained,
    it says every fill this trough can hold clears the walls, the dividers and the
    label ledge by that much."""
    probe_floor_z = bin_floor_z + interior_fillet_radius
    probe_top_z = interior_ceiling_z(height_u) - fill_headroom
    return _kit.placed_prism(
        fill_width(troughs) + 2.0 * wall_clearance,
        fill_depth + 2.0 * wall_clearance,
        probe_top_z - probe_floor_z,
        trough_center_x(index, troughs),
        fill_center_y,
        z_bottom=probe_floor_z,
        radius=fill_corner_radius,
    )


# ============================================================
# FIT CHECKS
# ============================================================

def assert_under_ceiling(name, fill, height_u):
    """A fill stops clear of the bin's interior ceiling. `bin_cavity` runs on up into
    the lip, where the storey above's base foot lands, so containment alone does not
    say this."""
    ceiling = interior_ceiling_z(height_u)
    top = _kit.bbox(fill).zmax
    headroom = ceiling - top
    if headroom < fill_headroom:
        raise ValueError(
            f"{name}: {headroom:.2f} mm under the interior ceiling, "
            f"wanted {fill_headroom:.2f} mm"
        )
    print(f"   {name}: {headroom:.2f} mm under the interior ceiling")


def validate(parts, cavities):
    print("Fit checks")
    for name, shape in parts.items():
        _kit.assert_one_solid(name, shape)
        _kit.assert_h2c_fit(name, shape)

    storeys, seats = build_stack(parts)
    _kit.assert_stack_seated(parts["fasteners-dock"], storeys, seats)

    for storey_name, height_u, contents in storey_contents:
        cavity = cavities[storey_name]
        troughs = len(contents)
        for index in range(troughs):
            _kit.assert_contained(
                f"{storey_name} trough {index + 1} clearance",
                build_trough_probe(index, troughs, height_u),
                cavity,
            )
        for index, content in enumerate(contents):
            fill = build_fill(content, index, troughs)
            _kit.assert_contained(f"{content.name} fill", fill, cavity)
            assert_under_ceiling(f"{content.name} headroom", fill, height_u)


# ============================================================
# THE KIT
# ============================================================

def build_stack(parts):
    storeys = [
        _kit.Storey(name, parts[name], height_u)
        for name, height_u, _ in storey_contents
    ] + [_kit.Storey("fasteners-tray", parts["fasteners-tray"], tray_storey_height_u)]
    return storeys, _kit.stack_seats(storeys)


def build_references():
    references = []
    for storey_index, (_, _, contents) in enumerate(storey_contents):
        troughs = len(contents)
        for index, content in enumerate(contents):
            references.append(
                (
                    f"{content.key.lower()}-fill",
                    build_fill(content, index, troughs),
                    content.color,
                    storey_index,
                )
            )
    return references


def build_kit_assembly(parts, name, exploded):
    storeys, seats = build_stack(parts)
    if exploded:
        seats = _kit.exploded_seats(seats, exploded_lift)
    return _kit.kit_assembly(
        name, parts["fasteners-dock"], storeys, seats, references=build_references()
    )


def printed_height(parts):
    """The closed stack's own height, dock foot to the tray's lip."""
    storeys, seats = build_stack(parts)
    return seats[-1] + _kit.bbox(storeys[-1].shape).zlen


def main():
    out_dir = Path(__file__).resolve().parent
    parts = {
        "fasteners-m5": build_trough_bin(m5_storey_height_u, len(m5_contents)),
        "fasteners-m3": build_trough_bin(m3_storey_height_u, len(m3_contents)),
        "fasteners-small": build_trough_bin(small_storey_height_u, len(small_contents)),
        "fasteners-tray": build_trough_bin(tray_storey_height_u, tray_troughs),
        "fasteners-dock": _kit.dock_body(footprint_x_u, footprint_y_u),
    }
    cavities = {
        name: _kit.bin_cavity(parts[name], footprint_x_u, footprint_y_u, height_u)
        for name, height_u, _ in storey_contents
    }
    validate(parts, cavities)

    _kit.export_parts(out_dir, parts)
    _kit.export_kit(
        out_dir, "fasteners-kit", build_kit_assembly(parts, "fasteners-kit", False)
    )
    _kit.export_kit(
        out_dir,
        "fasteners-kit-open",
        build_kit_assembly(parts, "fasteners-kit-open", True),
    )

    variables = {
        "FOOTPRINT": (
            f"{footprint_x_u * _kit.grid_unit:.0f} mm"
            f" x {footprint_y_u * _kit.grid_unit:.0f} mm"
        ),
        "PRINTED_HEIGHT": f"{printed_height(parts):.1f} mm",
        "H2C_ENVELOPE": (
            f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x {_kit.h2c_build_z:.0f} mm"
        ),
        "TALLEST_PART": f"{_kit.bbox(parts['fasteners-m5']).zlen:.1f} mm",
        "TROUGH_LENGTH": f"{trough_span:.1f} mm",
        "FILL_FOOTPRINT_DEPTH": f"{fill_depth:.1f} mm",
        "LABEL_LEDGE_REACH": f"{label_ledge_reach:.1f} mm",
        "LOOSE_FILL_FRACTION": f"{loose_fill_fraction * 100:.0f} %",
        "CONTENT_CLEARANCE": f"{content_clearance:.0f} mm",
        "WALL_CLEARANCE": f"{wall_clearance:.0f} mm",
        "FILL_HEADROOM": f"{fill_headroom:.0f} mm",
        "SKU_COUNT": f"{sum(len(c) for _, _, c in storey_contents)}",
        "DEEPEST_TROUGH": "%.0f cm³" % (
            max(trough_capacity(len(c), h) for _, h, c in storey_contents) / 1000.0
        ),
    }
    for storey_name, height_u, contents in storey_contents:
        stem = storey_name.replace("fasteners-", "").upper()
        variables[f"{stem}_TROUGHS"] = f"{len(contents)}"
        variables[f"{stem}_TROUGH_WIDTH"] = f"{trough_width(len(contents)):.1f} mm"
        variables[f"{stem}_DEPTH"] = (
            f"{interior_ceiling_z(height_u) - bin_floor_z:.1f} mm"
        )
        variables[f"{stem}_ENVELOPE"] = _kit.size_text(parts[storey_name])
        for content in contents:
            variables[f"{content.key}_COUNT"] = f"{content.count}"
            variables[f"{content.key}_FILL"] = (
                f"{content.fill_height(len(contents)):.1f} mm"
            )
    variables["TRAY_TROUGH_WIDTH"] = f"{trough_width(tray_troughs):.1f} mm"
    variables["TRAY_DEPTH"] = (
        f"{interior_ceiling_z(tray_storey_height_u) - bin_floor_z:.1f} mm"
    )
    variables["TRAY_ENVELOPE"] = _kit.size_text(parts["fasteners-tray"])
    variables["DOCK_ENVELOPE"] = _kit.size_text(parts["fasteners-dock"])
    substitute_md(out_dir / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
