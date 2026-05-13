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
sideways I-beam: a thin horizontal web fills the central X range
of the slot (only 2 mm tall in Z, the wall Z range), with 4 mm-
tall flanges ("wings") at the outer X edges of the slot, then
1 mm rail prongs extending past the slot in X to grip the wall:

    ╔══╤══╗            ╔══╤══╗      ← top prongs + top of wing
    ║  │  ║            ║  │  ║         (1 mm Z, z = wall_top .. wall_top + 1)
    ╠══╪══╬════════════╬══╪══╣      ← plate body web fills the wall Z range
    ║  │  ║   (web)    ║  │  ║         (2 mm Z, z = wall_inner .. wall_outer);
    ╠══╪══╬════════════╬══╪══╣         wings overlap the web here on each side
    ║  │  ║            ║  │  ║      ← bottom of wing + bottom prong
    ╚══╧══╝            ╚══╧══╝         (1 mm Z, z = wall_bottom − 1 .. wall_bottom)
    ←─→←─→              ←─→←─→
   1 mm 1 mm           1 mm 1 mm
   prong wing          wing prong
        ←─── 6.5 mm slot in X ───→

The plate-body web spans the full slot X range (±slot_half =
±3.25) and is 2 mm thick in Z (fills the wall Z range exactly).
Each wing sits at the outer 1 mm strip of the slot X range
(±2.25 .. ±3.25) and spans the FULL plug Z envelope (4 mm tall:
wall_bottom − 1 to wall_top + 1). Wings fit through the slot in
X (because the slot is at ±3.25 in X), and their extra Z height
above and below the wall is in open air on either Z face of the
wall — the slot itself doesn't constrain Z. The 1 mm rail prongs
extend outside the slot in X (±3.25 .. ±4.25), at the top-prong
and bottom-prong Z ranges only; the 2 mm Z gap between top and
bottom prongs (at ±3.25 .. ±4.25, the wall's Z range) is where
the wall slides in — that's how the plug grips the +Z wall edge
like a binder clip.

The wings are the load-bearing "I-beam flange" between the web
and the prongs. Without the wings (the pre-cb3693e+ design), the
prongs touched the plate only along a 1D corner edge (or the
0.01 mm rail_plate_overlap hack at f8e4c0c), and the XZ cross-
section read as a disconnected "space invader" at the viewer's
zoom level. With the wings, each prong shares a full 1 mm Z ×
y_height 2D face with its wing at x = ±slot_half, and each wing
shares a full 2 mm Z × y_height 2D face with the plate body web
at x = ±(slot_half − wing_x_width) — visibly continuous in every
CAD view.

Built as seven boxes (web + 2 wings + 4 prongs) unioned into a
single solid. The web's outer-X regions overlap the wings'
middle-Z bands; OCCT collapses the overlap cleanly during the
union.

Plug ends that abut a tube have a half-circle cutout (diameter =
tube clearance, ⌀6.5) centered on x=0 in the end face and arched
into the plug body, so the plug seats gently around the tube
running through the slot below/above it. The arch is Z-tall enough
to span the full plug Z envelope (z = wall_bottom − 1 to wall_top + 1),
so the prongs don't block tubes from seating.

  • LOWER plug:  arch on BOTTOM (over lowest copper), arch on TOP
                 (under highest copper).
  • MIDDLE plug: arch on BOTTOM (over highest copper), arch on TOP
                 (under water inlet).
  • UPPER plug:  arch on BOTTOM (over water inlet), TOP stays FLAT
                 (it's the top end of the stack).
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_bag_geometry import (
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

# Z range of the +Z outer_shell wall. The plate body of each plug
# fills this Z range exactly (2 mm thick at 2 mm wall), and the rail
# prongs branch out 1 mm above and 1 mm below it.
outer_wall_outer_z = outer_shell_z_length / 2.0
outer_wall_inner_z = outer_wall_outer_z - wall_and_floor_thickness
wall_z_center      = (outer_wall_inner_z + outer_wall_outer_z) / 2.0

# Rail prong dimensions.
#   rail_x_extension: how far each prong extends in X past the wing's
#                     outer edge (so total plug X span = slot_width_x
#                     + 2 × wing_x_width + 2 × rail_x_extension).
#   rail_z_thickness: Z thickness of each prong (1 mm above and 1 mm
#                     below the wall).
# Together these form a binder-clip cross-section that grips the wall
# edge instead of floating in the middle of it (see module docstring).
rail_x_extension = 1.0
rail_z_thickness = 1.0

# Wing dimensions. Each wing sits just outside the slot X range at
# x = ±slot_half .. ±(slot_half + wing_x_width) and spans the FULL
# plug Z envelope (plug_z_inner .. plug_z_outer). It bridges the
# plate-body web (2 mm Z in the slot) to the rail prongs (1 mm Z
# above and below the wall), giving an I-beam cross-section with
# visible 2D-face contact at every interface instead of the
# 0.01 mm rail_plate_overlap hair from the f8e4c0c+566a3a8 design.
# 1 mm matches rail_x_extension, so the X-edge "4 mm Z column" is
# symmetric in X — 1 mm of wing plus 1 mm of prong on the outer
# side of x = ±slot_half.
wing_x_width = 1.0

# Full plug Z envelope, including the rail prongs.
plug_z_outer  = outer_wall_outer_z + rail_z_thickness     # 91.5 at 2 mm wall
plug_z_inner  = outer_wall_inner_z - rail_z_thickness     # 87.5 at 2 mm wall

# Full plug X envelope, including the rail prongs. The wings sit
# INSIDE the slot's X range (at ±(slot_half − wing_x_width) ..
# ±slot_half), so they don't widen the plug X envelope; only the
# rail prongs do.
plug_half_x_outer = slot_half_width_x + rail_x_extension  # 4.25

# Pass-through Y positions (centers).
y_lowest_copper  = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
y_highest_copper = tank_copper_shell_height - hole_shift_from_edge - wall_and_floor_thickness - above_tank_elbows_height
y_water_inlet    = tank_copper_shell_height - hole_shift_from_edge

# Pass-through clearance in Y: each pass-through is ⌀6.5, so its
# center-to-edge clearance is tube_clearance_radius. Plug ends sit at
# the pass-through edge; a small extra gap prevents the plug from
# fouling the tube as the plug slides past.
pass_through_clearance = tube_clearance_radius + 0.5

# Plug Y ranges:
#   lower:  above lowest copper, below highest copper
#   middle: above highest copper, below water inlet
#   upper:  above water inlet, up to (just under) the +Y top face
plug_y_ranges = {
    "lower":  (y_lowest_copper  + pass_through_clearance, y_highest_copper - pass_through_clearance),
    "middle": (y_highest_copper + pass_through_clearance, y_water_inlet    - pass_through_clearance),
    "upper":  (y_water_inlet    + pass_through_clearance, tank_copper_shell_height - wall_and_floor_thickness),
}

# Which plug ends get a half-circle arch cutout (sits against a tube).
# True = arch cutout, False = flat end. UPPER's top is flat (top of
# the stack); every other end-against-a-tube arches around its tube.
plug_arch_ends = {
    "lower":  {"bottom": True,  "top": True},
    "middle": {"bottom": True,  "top": True},
    "upper":  {"bottom": True,  "top": False},
}


# ───────────────────────────────────────────────────────
# Plug builder
# ───────────────────────────────────────────────────────

# Full plug Z thickness (4 mm at 2 mm wall) — the wings span this
# range, and the four prongs sit in the top and bottom 1 mm bands
# of it.
plug_z_thickness = plug_z_outer - plug_z_inner
plug_z_center    = (plug_z_outer + plug_z_inner) / 2.0   # = wall_z_center


def _build_plate_block(y_bottom, y_height):
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, wall_z_center))
        .rect(slot_width_x, wall_and_floor_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )


def _build_wing_block(x_sign, y_bottom, y_height):
    """One of the two I-beam-flange wings, at x_sign · (slot_half −
    wing_x_width) .. x_sign · slot_half, spanning the full plug Z
    envelope. The wings sit at the OUTER 1 mm strip of the slot's
    X range — inside the slot in X (so the wing's 4 mm Z thickness
    still fits through the slot, because the slot is wide open in
    Z above and below the wall), but at the outer edge of the
    slot's X range, where they touch the rail prongs.

    Each wing shares:
      • a 2 mm Z × y_height Y face with the plate-body web on its
        INNER-X side (at x = ±(slot_half − wing_x_width)), where
        the wing's middle 2 mm Z band overlaps the web.
      • a 1 mm Z × y_height Y face with each of the two rail
        prongs (top and bottom) on its OUTER-X side (at x =
        ±slot_half), where the wing's top/bottom 1 mm Z bands
        share a face with the prong.

    Those shared faces let OCCT merge all seven boxes into a
    single contiguous solid."""
    inner_x_abs = slot_half_width_x - wing_x_width
    outer_x_abs = slot_half_width_x
    wing_x_center = x_sign * (inner_x_abs + outer_x_abs) / 2.0
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(wing_x_center, 0, plug_z_center))
        .rect(wing_x_width, plug_z_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )


def _build_rail_prong(x_sign, z_side, y_bottom, y_height):
    """One of the four rail prongs (1 mm thick in Z, 1 mm extending
    out past the slot in X), at the corner picked by x_sign in X and
    z_side ("top" / "bottom") in Z. The prong's inner-X edge sits at
    x = ±slot_half — the wing's outer-X face — so the prong shares
    a 1 mm Z × y_height Y face with its wing (instead of the
    pre-wing 1D corner-edge / 0.01 mm hair). That shared 2D face is
    what lets OCCT merge prongs into the same solid as the wings
    and plate body.

    Both top and bottom prongs sit just outside the wall on either
    Z face; the wall is at z = outer_wall_inner_z (88.5) to
    outer_wall_outer_z (90.5). The top prong wraps over the wall's
    outer face (z = 90.5..91.5); the bottom prong wraps under the
    wall's inner face (z = 87.5..88.5).
    """
    inner_x = x_sign * slot_half_width_x
    outer_x = x_sign * plug_half_x_outer
    if z_side == "top":
        rail_z_center = outer_wall_outer_z + rail_z_thickness / 2.0   # 91.0
    elif z_side == "bottom":
        rail_z_center = outer_wall_inner_z - rail_z_thickness / 2.0   # 88.0
    else:
        raise ValueError(f"z_side must be 'top' or 'bottom', got {z_side!r}")
    rail_x_center = (inner_x + outer_x) / 2.0
    rail_x_size   = abs(outer_x - inner_x)
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(rail_x_center, 0, rail_z_center))
        .rect(rail_x_size, rail_z_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )


def build_plug(name, y_bottom, y_top):
    """Single solid plug with the I-beam cross-section described in
    the module docstring, extending y_bottom..y_top in Y. Half-
    circle cutouts (diameter = tube_clearance_diameter) at the ends
    that sit against a tube; the cutouts span the full Z envelope so
    they pass through the plate-body web, the wings, and the rail
    prongs."""
    y_height = y_top - y_bottom

    plug = _build_plate_block(y_bottom, y_height)
    for x_sign in (-1, 1):
        plug = plug.union(_build_wing_block(x_sign, y_bottom, y_height))
        for z_side in ("top", "bottom"):
            plug = plug.union(_build_rail_prong(x_sign, z_side, y_bottom, y_height))

    arches = plug_arch_ends[name]

    # Half-circle cutouts. The arch is a cylinder (radius =
    # tube_clearance_radius, axis along Z so it pierces the slab face-
    # to-face) centered on x=0 at the plug's end y. Because the
    # cylinder is centered ON the end face, only the half that
    # overlaps the plug body (arching INTO the body) actually removes
    # material. The cylinder is built tall enough to span the full
    # plug Z envelope (z_inner .. z_outer including the rail prongs)
    # so the cut goes through both the plate and the prongs — without
    # this, the prongs would block tubes from seating.
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
    """Closed-form volume of the plug from its seven boxes minus the
    arch cutouts. Used as a cross-check on the OCCT boolean result —
    if they don't agree to within 0.01 mm^3, the union dropped or
    duplicated material somewhere.

    Wings sit INSIDE the slot's X range (at ±(slot_half −
    wing_x_width) .. ±slot_half), spanning the full plug Z envelope
    — so the wing's middle 2 mm Z band overlaps the plate-body web's
    Z range (the wall's Z range). The naïve sum web + wings double-
    counts that overlap. Account for it by adding only the wing's
    OUT-OF-WEB material: 2 × wing_x_width × (plug_z_thickness −
    wall_and_floor_thickness) × y_height = 4 mm² × y_height per mm
    of plug Y at 2 mm wall.

    Equivalent breakdown (no overlap between terms):
      Web slot-center: (slot_width_x − 2·wing_x_width) ×
                       wall_and_floor_thickness × y_height
      Wings (full):    2 × wing_x_width × plug_z_thickness × y_height
      Prongs:          4 × rail_x_extension × rail_z_thickness ×
                       y_height
    Both forms give 21 mm² × y_height at 2 mm wall.

    Arches (each end with an arch cutout): a cylinder of radius
    tube_clearance_radius and axis along Z, centered on x=0 at the
    plug's end Y. The cylinder is taller than the plug Z envelope
    (it's extruded ±plug_z_thickness via `both=True`) and extends
    in Y from y_end to ±plug_z_thickness — so the chunk that
    overlaps the plug body is a half-disk in the XY plane × the
    plug-body Z thickness at each (x, y) in the disk.

    Half-disk radius equals slot_half_width_x exactly. So every
    (x, y) in the half-disk has |x| ≤ slot_half_width_x, where the
    plug body in Z is:
      • the 2 mm web within |x| ≤ slot_half_width_x − wing_x_width
      • the 4 mm-tall wing within slot_half_width_x − wing_x_width
        ≤ |x| ≤ slot_half_width_x
    Integrating over the half-disk:
      vol_arch_per_end = wall_and_floor_thickness × A_inner
                       + plug_z_thickness        × A_wing_in_disk
    where A_inner is the half-disk area inside |x| ≤ slot_half −
    wing_x_width, and A_wing_in_disk = half_disk_area − A_inner.

    A_inner is half of a chord-of-a-circle area: for a disk of
    radius r and a vertical strip |x| ≤ d (with d < r), the strip
    area inside the disk is 2 × (d × √(r² − d²) + r² × arcsin(d/r));
    the half-disk (top half only) area inside the strip is half
    that.
    """
    y_height = y_top - y_bottom
    import math as _math

    vol_web    = slot_width_x * wall_and_floor_thickness * y_height
    # Wings overlap the web within the wall's Z range; only the
    # wing's OUT-OF-WEB volume is new material.
    vol_wings_extra = (
        2 * wing_x_width
        * (plug_z_thickness - wall_and_floor_thickness)
        * y_height
    )
    vol_prongs = 4 * rail_x_extension * rail_z_thickness * y_height

    arches = plug_arch_ends[name]
    n_arches = sum(1 for v in arches.values() if v)
    r = tube_clearance_radius
    d = slot_half_width_x - wing_x_width
    if d >= r:
        A_inner_full = _math.pi * r ** 2
    elif d <= 0:
        A_inner_full = 0.0
    else:
        A_inner_full = 2 * (d * _math.sqrt(r ** 2 - d ** 2)
                            + r ** 2 * _math.asin(d / r))
    A_inner_half = A_inner_full / 2.0
    half_disk_area = 0.5 * _math.pi * r ** 2
    A_wing_in_half_disk = half_disk_area - A_inner_half
    vol_arch_per_end = (
        wall_and_floor_thickness * A_inner_half
        + plug_z_thickness       * A_wing_in_half_disk
    )
    vol_arch_total = n_arches * vol_arch_per_end

    return vol_web + vol_wings_extra + vol_prongs - vol_arch_total


def main():
    for name, (y_bottom, y_top) in plug_y_ranges.items():
        plug = build_plug(name, y_bottom, y_top)
        out = _here / f"copper-plug-{name}.step"
        export_step(plug, str(out))
        # Sanity report: count of solids should be 1 (OCCT merged
        # everything into a single contiguous body — no floating
        # rails), and the bounding box should match the I-beam
        # envelope X[−4.25..4.25] × Z[87.5..91.5] at 2 mm wall.
        # Analytical volume (closed-form from the seven boxes minus
        # arch cutouts) must match the OCCT-computed volume to
        # within 0.01 mm^3.
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
        assert abs(vol_diff) < 0.01, (
            f"plug {name}: OCCT volume {vol:.4f} differs from analytical "
            f"{vol_analytical:.4f} by {vol_diff:+.4f} mm^3 (> 0.01 tolerance)"
        )


if __name__ == "__main__":
    main()
