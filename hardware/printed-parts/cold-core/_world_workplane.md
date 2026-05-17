# WorldWorkplane and WorldProfile

Defined in `_cold_core_interface.py`. Let cold-core geometry code be
written in **world coordinates**, with profiles named as separable
nouns. Read `_reed_channels.md` first for the surrounding methodology.

## WorldWorkplane

Drop-in `cq.Workplane` wrapper. Accepts `(x, y)` tuples directly
(no `*` unpacking) for `.moveTo`, `.lineTo`, `.radiusArc`,
`.threePointArc`, `.pushPoints`, `.polyline`. Applies the plane's
registered frame transform to those points, and negates radii when
the frame inverts chirality. Everything else (`.workplane`, `.extrude`,
`.cut`, `.union`, `.circle`, `.faces`, `.shell`, `.close`, ...) passes
through to the underlying `cq.Workplane`, with returned Workplanes
re-wrapped so the frame persists through the chain.

```python
outer_perimeter = (
    WorldWorkplane(xz_plane_y_up)
    .workplane(offset=0)
    .moveTo(point_in_world_coords)
    .lineTo(another_world_point)
    .radiusArc(arc_end_world, radius)  # positive radius — wrapper handles chirality
    .close()
    .extrude(height)
    .unwrap()  # if handing off to a consumer that wants raw cq.Workplane
)
```

## WorldProfile

A recipe-recorder for polyline-with-arcs profiles. Records the same
methods WorldWorkplane has (`moveTo`, `lineTo`, `radiusArc`,
`threePointArc`). Doesn't touch any workplane. Played back via
`WorldWorkplane.profile(prof)`. The point: gives polyline-with-arcs
the same "profile as a named noun" treatment that
`.polyline([list of points])` already gives pure polylines.

```python
outer_profile = (
    WorldProfile()
    .moveTo(...)
    .lineTo(...)
    .radiusArc(...)
    .threePointArc(...)
)
outer_perimeter = (
    WorldWorkplane(xz_plane_y_up)
    .workplane(offset=0)
    .profile(outer_profile).close()
    .extrude(height)
)
```

## Frames

`_register_frame(plane, point=..., radius=...)` associates a coordinate
transform pair with a plane. Lookup is by identity (`is`).

Currently registered:
- `xz_plane_y_up` → `point=flip_z`, `radius=lambda r: -r`
  (world (x, z) → local (x, -z); arc chirality inverts, so radius negates)
- `xy_plane_z_up` → identity (no registration needed)

To add a new workplane with a non-identity frame: define the plane,
then call `_register_frame(plane, point=..., radius=...)`.

## .unwrap()

Returns the underlying `cq.Workplane`. Needed at boundaries where
the consumer type-checks on `cq.Workplane`:

- `cq.exporters.export(model.unwrap(), path)`
- Binary ops where the *other* operand is raw (e.g., `raw.cut(wrapped)` —
  the reverse, `wrapped.cut(raw)`, works via `__getattr__`'s arg-unwrap)
- `.val().Volume()` for sieve checks

## Current limitations

`__getattr__` delegation is *silently incomplete*. It unwraps
WorldWorkplane args, but doesn't traverse other arg shapes to apply
the frame. Any cadquery method that takes coordinates and isn't
explicitly overridden will silently bypass the frame on a flipped
plane.

Latent gaps (no consumer hits these today, but worth knowing):

- `.sketch().arc(...)`, `.tangentArcPoint(...)`, `.hLineTo(...)`,
  `.vLineTo(...)`, `.mirrorY()`, `.mirrorX()` — chirality-sensitive
- `.center(x, y)`, `.transformed(offset=(x, y, z))` — affect
  subsequent point interpretation
- `.slot2D(angle=...)` — angles aren't transformed (the `radius`
  lambda only handles signed scalars for `radiusArc`)

Fix shape when any of these bite: add a named override that calls
`self._point` / `self._radius` on the relevant args. Same pattern as
`pushPoints` and `polyline`, which were added retroactively in
commit `08b8d09` after consumers hit the gap.

## When to use which

- **Inline single-point case** (e.g., `.moveTo(pt).circle(r)`): use
  `WorldWorkplane` methods directly inside the chain.
- **Polyline-with-arcs that wants a named profile**: build a
  `WorldProfile`, pass it to `.profile(prof)`.
- **Pure polyline (no arcs)**: use the canonical
  `.polyline([list of points])` — see `_reed_channels.md`'s
  `missing_wall_profile` example.
