# _reservoir_pocket_walls.py — notes specific to this file

Companion to `_reservoir_pocket_walls.py`. Strictly file-specific
content not already in `_reed_channels.md`. Read that first; this
file only captures what's new.

## Solid composition: outer.cut(cavity), per side, mirrored

```python
plus_x_pocket = outer_perimeter.cut(cavity_perimeter)
return plus_x_pocket.union(plus_x_pocket.mirror("YZ")).unwrap()
```

Different from the worked example's `total_envelope.cut(total_cavity)`
single-expression composition. Here the two perimeters are built as
separate extrusions and the +X pocket carved before mirroring across
YZ to make both sides.

## Dense 2D anchor naming

16 named anchor points declared before any polyline is built. Each
polyline visits only named anchors (no inline tuples except the
on-axis apexes like `(arc_tank_r, 0)` where naming adds nothing).
This is the dimensional-ladder principle from the playbook pushed
further than the worked example demonstrates.

Naming convention: `<region>_<face>_<sign>_z` where
- region: `middle_tank` / `middle_cavity` / `transition_tank` /
  `transition_cavity` / `far_wall` / `side_wall`
- face: `handoff` / `terminus` / `outer` / `cavity`
- sign: `plus_z` / `minus_z` (literal world Z sign — the coordinates
  carry positive/negative as written, no hidden negation)

## transition_apex(z_sign, r) — anchor-as-function

Inner function returning a parameterized 2D anchor, called with
different radii by `outer_profile` and `cavity_profile`. The pattern
when one geometric concept (a transition-arc apex) varies along a
known axis: factor it into a function that returns an anchor.

## Critical domain nouns

- `pocket` / `wall` — the four-walled enclosure and its sides
- `centerward` vs `far` — wall facing the cold-core axis vs away
- `middle` vs `transition` — segments of the centerward arc
- `tank` vs `cavity` — the two faces of the centerward wall
  (tank-side is inboard toward the tank+coil, cavity-side is
  outboard toward the pocket interior)
- `outer` vs `cavity` — the two perimeter polylines (outer = the
  wall's outboard face; cavity = the wall's inboard face)

`tank` here ≠ any noun in the worked example. Each file's domain
vocabulary describes its own geometry. The playbook's
critical-noun-consistency principle applies: each noun must carry
exactly one meaning everywhere in this file.

## See also

For `WorldProfile` / `WorldWorkplane` (the abstractions this file
uses heavily, including the world-coord anchor convention and the
profile-then-extrude split): [`_world_workplane.md`](_world_workplane.md).
