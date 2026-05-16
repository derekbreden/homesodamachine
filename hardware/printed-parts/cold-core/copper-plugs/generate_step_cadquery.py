"""Copper-line plugs — three small PETG pieces that slide down into
the shared ⌀6.5 port in the outer_shell +Z wall and seal the gaps
between (and above) the three pass-throughs that share that port.

Pass-throughs that pierce the +Z outer wall through the shared port,
ordered low → high in Y:

  • lowest copper  (cold-side evaporator inlet)  at y = hole_shift_from_edge
                                                   + wall_and_floor_thickness
                                                   + below_tank_elbows_height
                                                   = 47.0 mm  (at 2 mm wall)
  • highest copper (warm-side evaporator outlet) at y = tank_copper_shell_height
                                                   − hole_shift_from_edge
                                                   − wall_and_floor_thickness
                                                   − above_tank_elbows_height
                                                   = 166.4 mm
  • water inlet                                   at y = tank_copper_shell_height
                                                   − hole_shift_from_edge
                                                   = 198.4 mm

Three plugs in the stack:
  • copper-plug-lower:  fills the Y span between the lowest-copper
                        and highest-copper pass-throughs.
  • copper-plug-middle: fills the Y span between the highest-copper
                        and water-inlet pass-throughs.
  • copper-plug-upper:  fills the Y span above the water inlet, up
                        to (just below) the +Y top face of the
                        outer_shell.

Cross-section (looking along −Y; X horizontal, Z vertical) — a
true I-beam: a thin 2 mm-tall web fills the slot's X range at the
wall's Z range, sandwiched between two 1 mm-tall full-X-width
flanges that sit immediately above and below the wall:

    ████████████████████      ← top flange (full plug X, 1 mm Z;
                                  z = wall_outer .. wall_outer + 1)
         ██████████            ← web (slot X, 2 mm Z;
                                  z = wall_inner .. wall_outer)
    ████████████████████      ← bottom flange (full plug X, 1 mm Z;
                                  z = wall_inner − 1 .. wall_inner)
    ←──── 8.5 mm plug X ────→
         ←─6.5 mm slot─→

The flanges grip the +Z wall edge like a binder clip: the 2 mm Z
air gap between the top and bottom flanges (at x = ±slot_half ..
±plug_half_outer, i.e. the 1 mm of flange overhang past the web on
each side) is exactly where the wall sits when the plug is dropped
into the slot.

Built as three boxes (web + top flange + bottom flange) unioned
into a single solid. The web's top face shares a 2D 6.5 × y_height
contact patch with the top flange's bottom face at z = wall_outer
(and similarly with the bottom flange at z = wall_inner), so OCCT
merges all three into one contiguous body.

Plug ends that abut a tube have a half-circle cutout (diameter =
tube clearance, ⌀6.5) centered on x=0 in the end face and arched
into the plug body, so the plug seats gently around the tube
running through the slot below/above it. The arch is Z-tall enough
to span the full plug Z envelope (z = bottom_flange_inner ..
top_flange_outer), so the flanges don't block tubes from seating.

  • LOWER plug:  arch on BOTTOM (over lowest copper), arch on TOP
                 (under highest copper).
  • MIDDLE plug: arch on BOTTOM (over highest copper), arch on TOP
                 (under water inlet).
  • UPPER plug:  arch on BOTTOM (over water inlet), TOP stays FLAT
                 (it's the top end of the stack).
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _cold_core_interface import (
    xz_plane_y_up,
    xy_plane_z_up,
    wall_and_floor_thickness,
    hole_shift_from_edge,
    below_tank_elbows_height,
    above_tank_elbows_height,
    tank_copper_shell_height,
    outer_shell_z_length,
)

# ───────────────────────────────────────────────────────
# Slot + plug geometry constants
# ───────────────────────────────────────────────────────

# Slot width in X equals the port's ⌀6.5 (matches the punch in
# cut_slot_for_copper_and_water_inlet).
slot_width_x = 6.5
slot_half_width_x = slot_width_x / 2.0

# Tube clearance diameter at each pass-through (all three pass-throughs
# share the same ⌀6.5 slot punch from cut_slot_for_copper_and_water_inlet).
tube_clearance_diameter = 6.5
tube_clearance_radius   = tube_clearance_diameter / 2.0

# Z range of the +Z outer_shell wall. The web of each plug fills this
# Z range exactly (2 mm thick at 2 mm wall), and the two flanges sit
# 1 mm above and 1 mm below it.
outer_wall_outer_z = outer_shell_z_length / 2.0
outer_wall_inner_z = outer_wall_outer_z - wall_and_floor_thickness
wall_z_center      = (outer_wall_inner_z + outer_wall_outer_z) / 2.0

# Flange dimensions.
#   rail_x_extension: how far each flange extends in X past the slot
#                     on each side (so total plug X span = slot_width_x
#                     + 2 × rail_x_extension).
#   rail_z_thickness: Z thickness of each flange (1 mm above the wall
#                     for the top flange, 1 mm below for the bottom).
# Together these form a binder-clip cross-section that grips the wall
# edge: the 2 mm gap between the two flanges (at the wall's Z range,
# outside the web's X range) is exactly where the wall slides in.
rail_x_extension = 1.0
rail_z_thickness = 1.0

# Full plug Z envelope, including the two flanges.
plug_z_outer  = outer_wall_outer_z + rail_z_thickness     # 91.5 at 2 mm wall
plug_z_inner  = outer_wall_inner_z - rail_z_thickness     # 87.5 at 2 mm wall

# Full plug X envelope. Flanges run the full plug X width; the web
# is narrower, sitting only in the slot's X range.
plug_half_x_outer = slot_half_width_x + rail_x_extension  # 4.25
plug_full_x       = 2 * plug_half_x_outer                 # 8.5

# Pass-through Y positions (centers).
y_lowest_copper  = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
y_highest_copper = tank_copper_shell_height - hole_shift_from_edge - wall_and_floor_thickness - above_tank_elbows_height
y_water_inlet    = tank_copper_shell_height - hole_shift_from_edge

# Plug end faces meet AT the tube pass-through centers. The arch
# cutout at each tube-facing end (radius = tube_clearance_radius)
# accommodates exactly HALF of the adjacent tube: each tube sits with
# its upper half seated inside the plug ABOVE it (in that plug's
# bottom arch) and its lower half seated inside the plug BELOW it
# (in that plug's top arch).  Together, three plugs + three split-
# arch pairs fill the slot from y_lowest_copper to the wall top
# exactly — no linear gaps between plugs, the tube IS the gap.
#
# The upper plug's top face is flush with the wall top (y =
# tank_copper_shell_height); the upper plug has no top arch since
# nothing sits above it.
plug_y_ranges = {
    "lower":  (y_lowest_copper,  y_highest_copper),
    "middle": (y_highest_copper, y_water_inlet),
    "upper":  (y_water_inlet,    tank_copper_shell_height),
}

# Which plug ends get a half-circle arch cutout (sits against a tube).
# True = arch cutout, False = flat end. UPPER's top is flat (top of
# the stack); every other end-against-a-tube arches around its tube.
plug_arch_ends = {
    "lower":  {"bottom": True,  "top": True},
    "middle": {"bottom": True,  "top": True},
    "upper":  {"bottom": True,  "top": False},
}

# Razor-edge mitigation for the web at each arched plug end.
# ----------------------------------------------------------
# The arch's half-disc (radius = tube_clearance_radius) is tangent to
# the web's outer X edge at (x = ±slot_half_width_x, y = at_y).  For
# Y just inside the plug from the arch center, the web survives as a
# sliver of width (slot_half_width_x − sqrt(R² − (y−at_y)²)).  That
# sliver narrows to zero at y = at_y, which is a razor-thin edge that
# FDM printers can't resolve.
#
# Solution: don't print web where its sliver is thinner than
# `min_printable_thickness` mm.  The web's Y range is inset from each
# arched plug end by `web_arch_buffer`, the Y distance at which the
# arch's X reach has narrowed enough for the web's outer-X sliver to
# be exactly `min_printable_thickness` wide.  At the inset Y the web
# starts abruptly with two 1 mm-wide strips at x = ±(slot_half −
# 1)..±slot_half; both strips grow toward full ±slot_half_width_x
# width as Y moves further from the arch center.  Flanges are
# unchanged — their 1 mm-thick × 1 mm-wide tabs at x = ±slot_half..
# ±plug_half_x_outer were already at the print-resolution limit at the
# arch tangent and don't get thinner.
min_printable_thickness = 1.0
web_arch_buffer = math.sqrt(
    tube_clearance_radius ** 2
    - (slot_half_width_x - min_printable_thickness) ** 2
)  # ≈ 2.345 mm with tube_clearance_radius = slot_half_width_x = 3.25,
   # min_printable_thickness = 1.0


# ───────────────────────────────────────────────────────
# Plug builder
# ───────────────────────────────────────────────────────

# Full plug Z thickness (4 mm at 2 mm wall) — bottom flange + web +
# top flange, all stacked face-to-face with no Z gap inside |x| ≤
# slot_half_width_x.
plug_z_thickness = plug_z_outer - plug_z_inner


def _build_web(y_bottom, y_height):
    """The 2 mm-tall web of the I-beam: fills the slot's X range and
    the wall's Z range. Same as the pre-refactor plate body."""
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, wall_z_center))
        .rect(slot_width_x, wall_and_floor_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )


def _build_flange(z_side, y_bottom, y_height):
    """One of the two I-beam flanges. Both run the full plug X width
    (plug_full_x = 8.5 mm) and are rail_z_thickness mm tall in Z.

      • z_side = "top":    z = outer_wall_outer_z .. outer_wall_outer_z
                             + rail_z_thickness (91.5 at 2 mm wall).
                           Sits directly on the +Z outer face of the
                           wall; shares a 6.5 × y_height contact patch
                           with the web at z = outer_wall_outer_z.
      • z_side = "bottom": z = outer_wall_inner_z − rail_z_thickness
                             .. outer_wall_inner_z (87.5..88.5).
                           Sits directly on the −Z inner face of the
                           wall; shares a 6.5 × y_height contact patch
                           with the web at z = outer_wall_inner_z.

    The 1 mm of flange that overhangs the web in X on each side
    (x = ±slot_half .. ±plug_half_outer) leaves a 2 mm Z air gap
    between the top and bottom flanges where the wall slides in —
    that's the binder-clip mechanism."""
    if z_side == "top":
        flange_z_center = outer_wall_outer_z + rail_z_thickness / 2.0   # 91.0
    elif z_side == "bottom":
        flange_z_center = outer_wall_inner_z - rail_z_thickness / 2.0   # 88.0
    else:
        raise ValueError(f"z_side must be 'top' or 'bottom', got {z_side!r}")
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, flange_z_center))
        .rect(plug_full_x, rail_z_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )


def build_plug(name, y_bottom, y_top):
    """Single solid plug with the I-beam cross-section described in
    the module docstring, extending y_bottom..y_top in Y. Half-
    circle cutouts (diameter = tube_clearance_diameter) at the ends
    that sit against a tube; the cutouts span the full Z envelope so
    they pass through both flanges and the web."""
    y_height = y_top - y_bottom

    arches = plug_arch_ends[name]

    # Web and TOP FLANGE share the same Y range, inset from each
    # arched plug end by `web_arch_buffer`.  Two reasons combine:
    #   • Web razor edge — see razor-edge note above; web's outer-X
    #     sliver narrows to zero at y=at_y at each arched end.
    #   • Top-flange hanging-tab — the plug prints with its XY face
    #     on the bed (Z = print-vertical), so the top flange is in
    #     the LAST layers, sitting 2 mm above the bottom flange
    #     across an air gap.  At each arched end the top flange's
    #     ±X tab regions plus its inner razor strips (which form
    #     between the arch cut at x = ±√(R²−(y−at_y)²) and the
    #     flange edges at x = ±plug_half_x_outer) all print mangled.
    # The simplest fix covers both: the top flange has the same
    # shortened Y range as the web, so neither exists in
    # y = at_y..at_y + web_arch_buffer at each arched end — exactly
    # the missing region from e678489, extended in Z from the web
    # band (z = outer_wall_inner_z..outer_wall_outer_z) into the
    # top flange band (z = outer_wall_outer_z..plug_z_outer).
    #
    # Bottom flange keeps its full Y range — those tabs print fine
    # because they're on the print bed.  The binder-clip grip on
    # the wall's −Z face is intact at every arched end; the +Z
    # grip is intact everywhere outside the arched-end Y bands.
    web_y_bottom = y_bottom + (web_arch_buffer if arches["bottom"] else 0)
    web_y_top    = y_top    - (web_arch_buffer if arches["top"]    else 0)
    web_y_height = web_y_top - web_y_bottom

    plug = _build_web(web_y_bottom, web_y_height)
    plug = plug.union(_build_flange("top",    web_y_bottom, web_y_height))
    plug = plug.union(_build_flange("bottom", y_bottom,     y_height))

    # Half-circle cutouts. The arch is a cylinder (radius =
    # tube_clearance_radius, axis along Z so it pierces the slab face-
    # to-face) centered on x=0 at the plug's end y. Because the
    # cylinder is centered ON the end face, only the half that
    # overlaps the plug body (arching INTO the body) actually removes
    # material. The cylinder is built tall enough to span the full
    # plug Z envelope (z_inner .. z_outer including both flanges) so
    # the cut goes through both flanges and the web — without this,
    # the flanges would block tubes from seating.
    def _arch_cylinder(at_y):
        # Workplane at z = wall_z_center, extruded ±plug_z_thickness
        # so it covers the full envelope from z_inner to z_outer.
        return (
            cq.Workplane(xy_plane_z_up)
            .workplane(origin=(0, at_y, wall_z_center), offset=wall_z_center)
            .circle(tube_clearance_radius)
            .extrude(plug_z_thickness, both=True)
        )

    if arches["bottom"]:
        plug = plug.cut(_arch_cylinder(y_bottom))
    if arches["top"]:
        plug = plug.cut(_arch_cylinder(y_top))

    return plug


def _analytical_volume(name, y_bottom, y_top):
    """Closed-form volume of the plug from its three boxes minus the
    arch cutouts. Used as a cross-check on the OCCT boolean result —
    if they don't agree to within 0.01 mm^3, the union dropped or
    duplicated material somewhere.

    The web, top flange, and bottom flange occupy disjoint Z bands
    (web at wall_inner..wall_outer, top flange at wall_outer..
    wall_outer+1, bottom flange at wall_inner-1..wall_inner), so no
    overlap term is needed — their volumes simply add.

    Bottom-flange Y range = plug Y range (full y_height).
    Web AND top-flange Y range are both inset by `web_arch_buffer`
    at each arched end (razor + hanging-tab fix).

    Arch cutout per arched end: a Z-axis cylinder of radius
    tube_clearance_radius centered at (x=0, y=at_y).  The cut volume
    splits across the three Z bands:
      • Bottom flange (full Y range): half-disc × rail_z_thickness
      • Web AND top flange (Y range only past the buffer):
        (half-disc − buffer cap) × Z-thickness-of-that-band,
        where the buffer cap is the area of the half-disc from
        y=at_y to y=at_y+web_arch_buffer.
    """
    y_height = y_top - y_bottom

    arches = plug_arch_ends[name]
    n_arches = sum(1 for v in arches.values() if v)

    web_y_height   = y_height - n_arches * web_arch_buffer
    vol_web        = slot_width_x * wall_and_floor_thickness * web_y_height
    vol_top_flange = plug_full_x  * rail_z_thickness         * web_y_height
    vol_bot_flange = plug_full_x  * rail_z_thickness         * y_height

    r = tube_clearance_radius
    b = web_arch_buffer
    half_disc_area  = 0.5 * math.pi * r ** 2
    # Area of the half-disc from y=0 to y=b (the "buffer cap" near
    # the diameter — where the web AND top flange are both absent
    # in the new design).
    buffer_cap_area = b * math.sqrt(r ** 2 - b ** 2) + r ** 2 * math.asin(b / r)
    inset_in_arch_area = half_disc_area - buffer_cap_area
    vol_arch_per_end = (
        rail_z_thickness          * half_disc_area      # bottom flange (full Y)
        + rail_z_thickness        * inset_in_arch_area  # top flange (inset Y)
        + wall_and_floor_thickness * inset_in_arch_area # web (inset Y)
    )
    vol_arch_total = n_arches * vol_arch_per_end

    return vol_web + vol_top_flange + vol_bot_flange - vol_arch_total


def main():
    for name, (y_bottom, y_top) in plug_y_ranges.items():
        plug = build_plug(name, y_bottom, y_top)
        out = _here / f"copper-plug-{name}.step"
        export_step(plug, str(out))
        # Sanity report: count of solids should be 1 (OCCT merged
        # web + 2 flanges into a single contiguous body — no
        # floating flanges), and the bounding box should match the
        # I-beam envelope X[−4.25..4.25] × Z[87.5..91.5] at 2 mm
        # wall. Analytical volume (closed-form from the three boxes
        # minus arch cutouts) must match the OCCT-computed volume
        # to within 0.01 mm^3.
        solids = plug.solids().vals()
        bb = solids[0].BoundingBox() if solids else None
        bb_str = (
            f"X[{bb.xmin:6.2f}..{bb.xmax:6.2f}] "
            f"Y[{bb.ymin:6.2f}..{bb.ymax:6.2f}] "
            f"Z[{bb.zmin:6.2f}..{bb.zmax:6.2f}]"
            if bb else "(no solid)"
        )
        vol = solids[0].Volume() if solids else 0.0
        vol_analytical = _analytical_volume(name, y_bottom, y_top)
        vol_diff = vol - vol_analytical
        print(
            f"-> copper-plug-{name}.step  "
            f"y {y_bottom:.2f} -> {y_top:.2f} "
            f"(h {y_top - y_bottom:.2f} mm)  "
            f"solids={len(solids)}  "
            f"bbox {bb_str}  "
            f"vol {vol:.3f} mm^3  "
            f"analytical {vol_analytical:.3f} mm^3  "
            f"diff {vol_diff:+.4f} mm^3"
        )
        assert len(solids) == 1, f"plug {name}: expected 1 solid, got {len(solids)}"
        assert abs(bb.xmin - (-plug_half_x_outer)) < 1e-6 and abs(bb.xmax - plug_half_x_outer) < 1e-6, (
            f"plug {name}: X bbox {bb.xmin:.4f}..{bb.xmax:.4f} expected "
            f"{-plug_half_x_outer:.4f}..{plug_half_x_outer:.4f}"
        )
        assert abs(bb.zmin - plug_z_inner) < 1e-6 and abs(bb.zmax - plug_z_outer) < 1e-6, (
            f"plug {name}: Z bbox {bb.zmin:.4f}..{bb.zmax:.4f} expected "
            f"{plug_z_inner:.4f}..{plug_z_outer:.4f}"
        )
        assert abs(vol_diff) < 0.01, (
            f"plug {name}: OCCT volume {vol:.4f} differs from analytical "
            f"{vol_analytical:.4f} by {vol_diff:+.4f} mm^3 (> 0.01 tolerance)"
        )


if __name__ == "__main__":
    main()
