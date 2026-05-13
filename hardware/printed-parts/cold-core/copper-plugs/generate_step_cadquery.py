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

Each plug is a single solid block, 6.5 mm wide in X (matching the
slot), 3 mm thick in Z (centered on the +Z outer_shell wall — the
3 mm thickness IS the lateral capture; no separate rails), and
extending in Y to fill the gap between (or above) the pass-throughs
it sits between.

Plug ends that abut a tube have a half-circle cutout (diameter =
tube clearance, ⌀6.5) centered on x=0 in the end face and arched
into the plug body, so the plug seats gently around the tube
running through the slot below/above it:

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
# cut_hole_for_copper_and_water_inlet).
slot_width_x = 6.5
slot_half_width_x = slot_width_x / 2.0

# Tube clearance diameter at each pass-through (all three pass-throughs
# share the same ⌀6.5 hole punch from cut_hole_for_copper_and_water_inlet).
tube_clearance_diameter = 6.5
tube_clearance_radius   = tube_clearance_diameter / 2.0

# Z thickness of each plug — a flat 3 mm slab centered on the +Z
# outer_shell wall, so the plug body itself straddles the wall and
# captures the plug laterally without separate rails. Per user
# direction: exactly 3 mm regardless of wall thickness.
plug_z_thickness = 3.0

# Z range of the +Z outer_shell wall (used only to center the plug
# slab on the wall — the slab's own thickness, not the wall's, sets
# how far the plug protrudes on either face).
outer_wall_outer_z = outer_shell_z_length / 2.0
outer_wall_inner_z = outer_wall_outer_z - wall_and_floor_thickness
wall_z_center      = (outer_wall_inner_z + outer_wall_outer_z) / 2.0

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

def build_plug(name, y_bottom, y_top):
    """Single solid plug block, slot_width_x wide in X,
    plug_z_thickness thick in Z (centered on the +Z outer_shell wall),
    extending y_bottom..y_top in Y. Half-circle cutouts (diameter =
    tube_clearance_diameter) at the ends that sit against a tube."""
    y_height = y_top - y_bottom
    y_center = (y_bottom + y_top) / 2.0

    block = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, wall_z_center))
        .rect(slot_width_x, plug_z_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )

    arches = plug_arch_ends[name]

    # Half-circle cutouts. The arch is a full cylinder (radius =
    # tube_clearance_radius, axis along Z so it pierces the slab face-
    # to-face), centered on x=0 at the plug's end y. The arch is
    # subtracted from the block; since the cylinder is centered ON the
    # end face, only the half that overlaps the block (arching INTO
    # the body) actually removes material.
    if arches["bottom"]:
        cutout_bottom = (
            cq.Workplane(xy_plane_z_up)
            .workplane(origin=(0, y_bottom, wall_z_center), offset=wall_z_center)
            .circle(tube_clearance_radius)
            .extrude(plug_z_thickness, both=True)
        )
        block = block.cut(cutout_bottom)

    if arches["top"]:
        cutout_top = (
            cq.Workplane(xy_plane_z_up)
            .workplane(origin=(0, y_top, wall_z_center), offset=wall_z_center)
            .circle(tube_clearance_radius)
            .extrude(plug_z_thickness, both=True)
        )
        block = block.cut(cutout_top)

    return block


def main():
    for name, (y_bottom, y_top) in plug_y_ranges.items():
        plug = build_plug(name, y_bottom, y_top)
        out = _here / f"copper-plug-{name}.step"
        export_step(plug, str(out))
        print(f"-> copper-plug-{name}.step  (y {y_bottom:.2f} -> {y_top:.2f}, height {y_top - y_bottom:.2f} mm)")


if __name__ == "__main__":
    main()
