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

Cross-section (looking along −Y; X horizontal, Z vertical):

    ╔══╗            ╔══╗      ← top prongs (1 mm Z, at z = wall_top .. wall_top + 1)
    ║  ╠════════════╣  ║      ← plate body fills the wall Z range (2 mm, z = wall_inner .. wall_outer)
    ║  ╠════════════╣  ║
    ╔══╗            ╔══╗      ← bottom prongs (1 mm Z, at z = wall_bottom − 1 .. wall_bottom)
    ←──→            ←──→
   1 mm            1 mm
   rail            rail

The plate body in the slot's X range (±3.25 = slot_width_x / 2) is
2 mm thick in Z and fills the wall Z range exactly. At each X edge,
1 mm-thick prongs branch out 1 mm further in X, one above the wall
and one below the wall. The 2 mm Z gap between the top and bottom
prongs is where the wall material slides in — that's how the plug
grips the +Z wall edge like a binder clip, instead of "floating" in
the middle of the wall.

Built as five separate boxes (plate + four prongs) unioned into a
single solid. Each prong extends inward past the plate's X edge by
`rail_plate_overlap` (a 0.01 mm hair, well below print resolution)
so it shares a 2D face with the plate's top or bottom face rather
than just touching at a 1D corner edge — that's what lets OCCT
merge them into a single contiguous solid. Without the overlap,
1×1 prongs at the plate corners share only a corner POINT in 2D
(= 1D edge in 3D) with the plate, and OCCT's union leaves them as
disconnected pieces (the failure mode from f8e4c0c).

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
#   rail_x_extension: how far each prong extends in X past the plate
#                     edge (so total plug X span = slot_width_x + 2 mm).
#   rail_z_thickness: Z thickness of each prong (1 mm above and 1 mm
#                     below the wall).
# Together these form a binder-clip cross-section that grips the wall
# edge instead of floating in the middle of it (see module docstring).
rail_x_extension = 1.0
rail_z_thickness = 1.0

# Full plug Z envelope, including the rail prongs.
plug_z_outer  = outer_wall_outer_z + rail_z_thickness     # 91.5 at 2 mm wall
plug_z_inner  = outer_wall_inner_z - rail_z_thickness     # 87.5 at 2 mm wall

# Full plug X envelope, including the rail prongs.
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

# Tiny overlap that each rail prong extends INWARD past the plate's
# X edge, so the prong's bottom (or top) face shares a real 2D area
# with the plate's top (or bottom) face — not just a 1D corner edge.
# Without this overlap, OCCT's union leaves the prongs as separate
# solids (the failure mode from f8e4c0c). 0.01 mm is well below
# print resolution (~0.2 mm layer height) so it has no physical
# effect on fit or strength.
rail_plate_overlap = 0.01


def _build_plate_block(y_bottom, y_height):
    return (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, wall_z_center))
        .rect(slot_width_x, wall_and_floor_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )


def _build_rail_prong(x_sign, z_side, y_bottom, y_height):
    """One of the four rail prongs (1 mm thick in Z, 1 mm extending
    out past the plate in X), at the corner picked by x_sign in X and
    z_side ("top" / "bottom") in Z. The prong's inner-X edge overlaps
    the plate by rail_plate_overlap so the prong shares a 2D face
    with the plate's top-or-bottom face (instead of meeting at a 1D
    edge only) — that's what lets OCCT merge them into a single
    solid.

    Both top and bottom prongs sit at positive Z (just outside the
    wall on either Z face); the wall is at z = outer_wall_inner_z
    (88.5) to outer_wall_outer_z (90.5). The top prong wraps over
    the wall's outer face (z = 90.5..91.5); the bottom prong wraps
    under the wall's inner face (z = 87.5..88.5).
    """
    inner_x = x_sign * (slot_half_width_x - rail_plate_overlap)
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
    """Single solid plug with the binder-clip cross-section described
    in the module docstring, extending y_bottom..y_top in Y. Half-
    circle cutouts (diameter = tube_clearance_diameter) at the ends
    that sit against a tube; the cutouts span the full Z envelope so
    they pass through both the plate body and the rail prongs."""
    y_height = y_top - y_bottom

    plug = _build_plate_block(y_bottom, y_height)
    for x_sign in (-1, 1):
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
        plug_z_thickness = plug_z_outer - plug_z_inner   # 4.0 at 2 mm wall
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


def main():
    for name, (y_bottom, y_top) in plug_y_ranges.items():
        plug = build_plug(name, y_bottom, y_top)
        out = _here / f"copper-plug-{name}.step"
        export_step(plug, str(out))
        # Sanity report: count of solids should be 1 (OCCT merged
        # everything into a single contiguous body — no floating
        # rails), and the bounding box should match the binder-clip
        # envelope.
        solids = plug.solids().vals()
        bb = solids[0].BoundingBox() if solids else None
        bb_str = (
            f"X[{bb.xmin:6.2f}..{bb.xmax:6.2f}] "
            f"Y[{bb.ymin:6.2f}..{bb.ymax:6.2f}] "
            f"Z[{bb.zmin:6.2f}..{bb.zmax:6.2f}]"
            if bb else "(no solid)"
        )
        vol = solids[0].Volume() if solids else 0.0
        print(
            f"-> copper-plug-{name}.step  "
            f"y {y_bottom:.2f} -> {y_top:.2f} "
            f"(h {y_top - y_bottom:.2f} mm)  "
            f"solids={len(solids)}  "
            f"bbox {bb_str}  "
            f"vol {vol:.1f} mm^3"
        )


if __name__ == "__main__":
    main()
