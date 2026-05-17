# _port_cuts.py — notes specific to this file

Companion to `_port_cuts.py`. Strictly file-specific content not
already in `_reed_channels.md`. Read that first; this file only
captures what's new.

## Utility-cut-function shape

Three top-level functions, each `foam_shell -> foam_shell.cut(...)`.
No solid builders, no `build_*` returns. Module-scope holds shared
anchors (Y, Z, and the three named circular-port (x, y, z) tuples)
that the consumers reuse. Different from `_foam_cap.py`'s
"build_*-with-shared-helpers" shape and `_reed_channels.py`'s
"build + cut_openings" pair.

## Named anchors over a hole table

Three circular port holes — water outlet, +X bulkhead, −X bulkhead —
each named as a module-scope `*_xyz` triple. `cut_circular_port_holes`
iterates over the three names; no positional table of magic tuples.
The ±X bulkhead anchors stay separately named (rather than
constructed from a sign loop) so call-site readers see both X polarities
explicitly.

## The doorway = bore + slot composite

`cut_co2_inlet` builds two cut tools that share `doorway_z` (the
pocket-side face of the bag-pocket −Z wall): a round bore at
`bore_y` and a rect slot below it of the same X-width as the bore.
`doorway_z` is the only Z anchor in the function — both the bore
extrusion start and the slot's workplane reference it.

## Shared port anchors at the interface level

`reservoir_bulkhead_port_z` was added to `_cold_core_interface.py`
alongside the existing `_port_x` / `_port_y`. The bulkhead port has
an (x, y, z); all three rungs of the dimensional ladder live where
the bulkhead geometry is defined. `_reed_channels.py:cut_reed_cable_holes`
still inlines `bag_pocket_width / 2 - 10` for the same Z (the cable
hole sits at the same Z as its side's bulkhead hole, by design) —
adopting the import there is a future cross-file pass.

## workplane(origin=..., offset=...) double-positioning

`build_a_hole_punch` and `build_a_slot_punch` (in `_cold_core_interface.py`)
pass `origin=origin, offset=origin[2]` — the Z component of `origin`
is silently ignored by `cq.Workplane(xy_plane_z_up).workplane(...)`;
only `offset` shifts the workplane along its normal. The redundancy
is harmless and idiomatic for this codebase, so the inline workplane
in `cut_co2_inlet` follows the same `origin=..., offset=...` convention.

## Critical domain nouns

- `port` — any passage through the foam shell.
- `hole` — a round (cylindrical) port cut.
- `bore` — the round part of the CO2 doorway only.
- `slot` — Y-elongated cut. Two shapes share the word: the CO2
  doorway's rect slot (no rounded ends) and the copper/water
  inlet's rounded-end slot (built by `build_a_slot_punch`).
- `doorway` — the bore+slot composite at the CO2 inlet.
- `bulkhead` — the bag pocket's pass-through fitting (port to which
  the inside-to-outside tube connects).
- `plug` — the printed solids that drop into the copper/water slot
  (copper-line plug, water-inlet plug).

## See also

For build_a_hole_punch's 40 mm overshoot rationale (and why exact-
reach extrude heights leave slivers at the CO2 inlet's
support-ring tangent), see `_cold_core_interface.py:build_a_hole_punch`.
