"""Copper-line plugs — three small PETG pieces that slide down into
the shared ⌀6.5 port in the outer_shell +Z wall and seal the gaps
between (and above) the three pass-throughs that share that port.

Pass-throughs that pierce the +Z outer wall through the shared port,
ordered low → high in Y:

  • lowest copper  (cold-side evaporator inlet)  at y = hole_shift_from_edge
                                                   + wall_and_floor_thickness
                                                   + below_tank_elbows_height
                                                   = 46.0 mm
  • highest copper (warm-side evaporator outlet) at y = tank_copper_shell_height
                                                   − hole_shift_from_edge
                                                   − wall_and_floor_thickness
                                                   − above_tank_elbows_height
                                                   = 166.4 mm
  • water inlet                                   at y = tank_copper_shell_height
                                                   − hole_shift_from_edge
                                                   = 197.4 mm

The previously-removed copper-plug pair was T-shaped, threading
through three nested walls (tank_copper_shell, bag_pocket_support
shell, outer_shell). With the cylinder wall opened at ±Z, the
support shell ±Z walls gapped at x=0, and the three pass-throughs
sharing a single ⌀6.5 port at x=0 in the outer_shell +Z wall, the
plugs now only need to seal one wall — so each plug is just a thin
slab matching the wall thickness, with four rails per plug that
clip onto both faces of the wall like a binder clip.

Three plugs in the stack:
  • copper-plug-lower:  fills the Y span between the lowest-copper
                        and highest-copper pass-throughs.
  • copper-plug-middle: fills the Y span between the highest-copper
                        and water-inlet pass-throughs.
  • copper-plug-upper:  fills the Y span above the water inlet, up
                        to (just below) the +Y top face of the
                        outer_shell.

Each plug slides DOWN (along −Y) from above into the port; the four
rails (one per X-edge × wall-face combination) hug the inner and
outer faces of the +Z outer_shell wall on both sides of the slot to
capture the plug laterally so it stays seated without adhesive."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(0, str(_here.parent))

from _cadq_export import export_step
from _foam_bag_geometry import (
    xz_plane_y_up,
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

# Z range of the +Z outer_shell wall — the only wall the port pierces.
outer_wall_outer_z = outer_shell_z_length / 2.0                      # 88.5
outer_wall_inner_z = outer_wall_outer_z - wall_and_floor_thickness   # 87.5

# Pass-through Y positions (centers).
y_lowest_copper  = hole_shift_from_edge + wall_and_floor_thickness + below_tank_elbows_height
y_highest_copper = tank_copper_shell_height - hole_shift_from_edge - wall_and_floor_thickness - above_tank_elbows_height
y_water_inlet    = tank_copper_shell_height - hole_shift_from_edge

# Pass-through clearance in Y: each pass-through is ⌀6.5, so its
# center-to-edge clearance is slot_half_width_x. Plug ends sit at the
# pass-through edge; a small extra gap prevents the plug from
# fouling the tube as the plug slides past.
pass_through_clearance = slot_half_width_x + 0.5

# Plug Y ranges:
#   lower:  above lowest copper, below highest copper
#   middle: above highest copper, below water inlet
#   upper:  above water inlet, up to (just under) the +Y top face
plug_y_ranges = {
    "lower":  (y_lowest_copper  + pass_through_clearance, y_highest_copper - pass_through_clearance),
    "middle": (y_highest_copper + pass_through_clearance, y_water_inlet    - pass_through_clearance),
    "upper":  (y_water_inlet    + pass_through_clearance, tank_copper_shell_height - wall_and_floor_thickness),
}

# Rail dimensions: 1 mm protrusion off the slot edge in X, 1 mm
# thickness in Z (so each rail laps onto its wall face by 1 mm).
rail_x_protrusion = 1.0
rail_z_thickness  = 1.0


# ───────────────────────────────────────────────────────
# Plug builder
# ───────────────────────────────────────────────────────

def build_plug(y_bottom, y_top):
    """A single plug: a 1 mm-thick (Z) × 6.5 mm-wide (X) web that
    fills the slot through the +Z outer_shell wall, plus four 1×1
    rails (Y_height tall) at the four X-edge × wall-face corners
    that clip onto both faces of the wall to capture the plug
    laterally."""
    y_height = y_top - y_bottom
    y_center = (y_bottom + y_top) / 2.0
    wall_z_center = (outer_wall_inner_z + outer_wall_outer_z) / 2.0

    # Central web: fills the slot proper (between the wall's two
    # faces, spanning the slot's X width).
    web = (
        cq.Workplane(xz_plane_y_up)
        .workplane(origin=(0, 0, wall_z_center))
        .rect(slot_width_x, wall_and_floor_thickness)
        .extrude(y_height)
        .translate((0, y_bottom, 0))
    )

    plug = web

    # Four rails, one per (x_sign, side_sign) combination. side_sign
    # = +1 is the rail on the outer face of the wall (z > wall outer
    # face), side_sign = −1 is the rail on the inner face. Each rail
    # is a 1×1 mm cross-section column extending the full Y height
    # of the plug.
    for x_sign in (+1, -1):
        for side_sign in (+1, -1):
            rail_x_center = x_sign * (slot_half_width_x + rail_x_protrusion / 2.0)
            if side_sign == +1:
                rail_z_center = outer_wall_outer_z + rail_z_thickness / 2.0
            else:
                rail_z_center = outer_wall_inner_z - rail_z_thickness / 2.0
            rail = (
                cq.Workplane(xz_plane_y_up)
                .workplane(origin=(rail_x_center, 0, rail_z_center))
                .rect(rail_x_protrusion, rail_z_thickness)
                .extrude(y_height)
                .translate((0, y_bottom, 0))
            )
            plug = plug.union(rail)

    return plug


def main():
    for name, (y_bottom, y_top) in plug_y_ranges.items():
        plug = build_plug(y_bottom, y_top)
        out = _here / f"copper-plug-{name}.step"
        export_step(plug, str(out))
        print(f"-> copper-plug-{name}.step  (y {y_bottom:.2f} -> {y_top:.2f}, height {y_top - y_bottom:.2f} mm)")


if __name__ == "__main__":
    main()
