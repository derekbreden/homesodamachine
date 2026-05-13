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
into the slot. Same Z geometry as the prior X-wing design (commit
b8f6fa5), but the four corner prongs are now extended in X across
the full plug width to form two continuous flanges instead.

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

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_shell_geometry import (
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

    plug = _build_web(y_bottom, y_height)
    for z_side in ("top", "bottom"):
        plug = plug.union(_build_flange(z_side, y_bottom, y_height))

    arches = plug_arch_ends[name]

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

    Per-mm-of-Y at 2 mm wall:
      web         = slot_width_x × wall_and_floor_thickness = 13 mm²
      top flange  = plug_full_x  × rail_z_thickness         =  8.5 mm²
      bot flange  = plug_full_x  × rail_z_thickness         =  8.5 mm²
      total                                                 = 30 mm² × y_height

    Arch cutout per end: a cylinder of radius tube_clearance_radius
    (3.25) and axis along Z, centered on x=0 at the plug's end Y.
    Since tube_clearance_radius == slot_half_width_x exactly, the
    cylinder's footprint in XY is the disk |(x, Δy)| ≤ r, which has
    its full |x| ≤ slot_half_width_x range INSIDE the web's X span.
    So at every (x, y) in the half-disk that overlaps the plug body,
    the plug stack in Z is contiguous (bottom flange + web + top
    flange = plug_z_thickness, no gaps inside |x| ≤ slot_half).

    Volume per arched end:
      vol_arch_per_end = plug_z_thickness × half_disk_area
                       = plug_z_thickness × (π × r²) / 2
    """
    y_height = y_top - y_bottom
    import math as _math

    vol_web        = slot_width_x * wall_and_floor_thickness * y_height
    vol_top_flange = plug_full_x  * rail_z_thickness         * y_height
    vol_bot_flange = plug_full_x  * rail_z_thickness         * y_height

    arches = plug_arch_ends[name]
    n_arches = sum(1 for v in arches.values() if v)
    r = tube_clearance_radius
    half_disk_area = 0.5 * _math.pi * r ** 2
    vol_arch_per_end = plug_z_thickness * half_disk_area
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
