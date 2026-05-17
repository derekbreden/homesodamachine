# _support_ring.py — notes specific to this file

Companion to `_support_ring.py`. Strictly file-specific content not
already in `_reed_channels.md`. Read that first; this file only
captures what's new.

## Profile-then-revolve

The only cold-core module using `.revolve(...)` instead of
`.extrude(...)`. The 2D profile lives on the XY plane with **x
interpreted as radius**, then revolves around the world +Y axis.
This means the profile's local coordinates are `(r, y)`, not the
world `(x, y)` other modules use.

```python
def revolve_rect(r_range, y_range, angle=360):
    """Revolve a rectangular (r, y) profile around the Y axis."""
    r_min, r_max = min(r_range), max(r_range)
    y_min, y_max = min(y_range), max(y_range)
    return (
        cq.Workplane(xy_plane_z_up)
        .moveTo(r_min, y_min)
        ...
        .close()
        .revolve(angle)
    )
```

Same signature shape as `_reed_channels.py:make_box(x_range, y_range,
z_range)` — a range-tuple-taking solid builder. The dimensional-ladder
principle (named ranges, not flood-of-scalars at call sites) carries
across the extrude/revolve boundary.

## Slots as overflowing partial revolves

A 30°-wide slot cut out of the ring could be built by extruding a
chord-bounded prism and cutting. The slot's radial boundaries would
then be flat chords, leaving wedge slivers of ring material between
each chord and the ring's cylindrical faces.

Instead the slot is a partial revolve of the same (r, y) rect, with a
**radial margin** padding the profile on each side. The slot's radial
boundaries are now cylinders concentric with the ring faces — but
offset outward by `slot_radial_margin`, so the boolean cut isn't
asked to subtract coincident faces (a degenerate condition that
itself leaves slivers from numerical noise).

```python
slot_r_range = (r_inner - slot_radial_margin, r_outer + slot_radial_margin)
slot_template = revolve_rect(slot_r_range, ring_y_range, slot_angular_width)
```

The margin (1 mm here) only needs to exceed numerical noise on the
boolean; the value is documentary, not load-bearing.

## Template + rotate pattern

Slot geometry is identical at every position, so the slot is built
once as a θ=0 template and rotated to each position before cutting:

```python
slot_template = revolve_rect(slot_r_range, ring_y_range, slot_angular_width)
for i in range(slot_count):
    slot_center_angle = slot_spacing_angle * (i + 0.5)
    slot_start_angle = slot_center_angle - slot_angular_width / 2
    slot = slot_template.rotate((0, 0, 0), (0, 1, 0), slot_start_angle)
    ring = ring.cut(slot)
```

`(i + 0.5)` rather than `i + 0` puts the slot center at the midpoint
of each equal-arc segment (45°, 135°, 225°, 315° for slot_count=4).
`cq.Workplane.rotate` returns a new Workplane — the template isn't
mutated, so it's safe to reuse across iterations.

## Critical domain nouns

- `ring` — the full annular solid.
- `slot` — an angular cut-out through the ring.
- `r_inner` / `r_outer` — the ring's inner and outer cylindrical faces.
  Radii, not world X coordinates — the file lives in (r, y) profile
  space throughout.
- `template` — a θ=0 slot built once and rotated to each position.
- `angular_width` vs `radial_margin` — the two dimensions of a slot's
  oversize relative to the ring it cuts.

## See also

For `make_box` (the profile-then-extrude analog of `revolve_rect`)
and the dimensional-ladder principle that motivates the range-tuple
signature, see [`_reed_channels.md`](_reed_channels.md).
