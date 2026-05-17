# _cold_core_interface.py — notes specific to this file

Companion to `_cold_core_interface.py`. Strictly file-specific
content not already in `_reed_channels.md` or `_world_workplane.md`.
Read both first; this file only captures what's new.

## Foundational-vocabulary shape

No `build_*` solid producers. Every other cold-core module is
either a builder (`_outer_shell`, `_foam_cap`, `_reservoir_pocket_walls`,
`_support_ring`) or a cutter (`_port_cuts`, `_reed_channels`) that
imports its dimensional vocabulary from here. This file is pure
vocabulary plus three small punch-builder helpers and the
`WorldWorkplane` / `WorldProfile` abstractions.

The two `cq.Plane` singletons (`xz_plane_y_up`, `xy_plane_z_up`)
are the workplane vocabulary. The 50+ module-scope scalars are
the dimensional vocabulary. The three punch builders are
shape-of-cut vocabulary.

## Derivation chains, not raw scalars

Most constants are derivations of three primitives —
`wall_and_floor_thickness`, `tank_outer_radius`, `tank_height` —
plus a handful of clearances. The chain reads as the part's
sizing story:

```
tank_outer_radius + coil_radial_clearance + wall_and_floor_thickness
   = pocket_centerward_arc_outer_radius
       ↳ bag_pocket_width = 2 * arc_outer_radius
           ↳ outer_shell_z_length = 2 * (… + foam_gap + wall)
```

A reader changing the tank diameter doesn't have to chase
intermediate magic numbers — the geometry expressions show what
each constant is made of.

## Punch-builder origin convention

The three `build_a_*_punch` helpers all take `origin=(x, y, z)`
in world coordinates. Internally they split the tuple so the
workplane offset goes on the plane's normal axis, not into the
`workplane(origin=…)` arg (which silently ignores the normal
component). The split is invisible at the call site; the API
stays a clean 3-tuple in world coordinates.

`build_a_hole_punch` and `build_a_slot_punch` extrude along +Z
(`xy_plane_z_up`). `build_a_y_axis_hole_punch` extrudes along
+Y (`xz_plane_y_up`). Same shape, two aiming directions.

The 40 mm default extrude height is documented in
`build_a_hole_punch`'s docstring — looks like an obvious refactor
to per-call exact-reach values, but the CO2 inlet's tangency to
the support ring's curved face is the corner case that justifies
the overshoot for all callers.

## Critical domain nouns

- `tank` — the 4 L LDPE keg under the cold core. Source of
  `tank_outer_radius`, `tank_height`, `tank_support_ring_height`.
- `pocket` — used in two senses, always disambiguated by prefix:
  - `bag_pocket_*` — the major rectangular cavity in the foam
    shell for each reservoir (the dominant feature).
  - `bulkhead_pocket_diameter`, `insert_pocket_*` — generic
    "recess" sense (the nut cavity and the heat-set insert hole).
- `centerward` — facing the cold-core (Y) axis. Opposite of
  `far` or `outermost`. `pocket_centerward_arc_outer_radius`
  is the radius of the bag pocket's curved (centerward) wall.
- `bulkhead` — the bag pocket's pass-through fitting. Has an
  axis, a nut cavity, and a port (the through-hole). All three
  Y/X/Z anchors live here so consumers don't redo the algebra.
- `attachment` — the 6 screw positions where outer-shell bosses,
  foam-cap bosses, gasket pads, and lid clearances all align.
  `foam_cap_attachment_xz_positions` is the canonical list.
- `boss` — an 8×8 mm square pillar at one attachment position
  (always a screw boss; "pin" boss is not used here).
- `screw` / `insert` — the cap-to-shell fastener pair: M3 SHCS
  threading into a ruthex M3 heat-set insert.

## See also

For `WorldWorkplane` / `WorldProfile` / `flip_z` / the frame
registry: [`_world_workplane.md`](_world_workplane.md). For the
methodology these abstractions and the vocabulary structure
follow: [`_reed_channels.md`](_reed_channels.md).
