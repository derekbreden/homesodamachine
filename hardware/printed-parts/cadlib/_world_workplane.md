# WorldWorkplane and WorldProfile

Defined in `world_workplane.py`. Lets generator code be written in
**world coordinates** on any face of an axis-aligned box, with the
same code shape regardless of which face. Two adjacent blocks of
geometry — one on the top face, one on the back face — read
identically: same constructor pattern, same chained methods,
positive numbers meaning positive in the world direction the user
expects. Read `../cold-core/_reed_channels.md` first for the
surrounding methodology.

## Box-face planes

Six module-level singletons, one per face of an axis-aligned box.
Identity is meaningful — `WorldWorkplane` looks up its frame
transform by `is` comparison, so do not construct your own copies;
import these.

| plane              | normal | xDir | extrude(+h) goes |
|--------------------|--------|------|------------------|
| `xy_plane_z_up`    | +Z     | +X   | +Z (out of top face)        |
| `xy_plane_z_down`  | -Z     | +X   | -Z (out of bottom face)     |
| `xz_plane_y_up`    | +Y     | +X   | +Y (out of back face)       |
| `xz_plane_y_down`  | -Y     | +X   | -Y (out of front face)      |
| `yz_plane_x_up`    | +X     | +Y   | +X (out of right face)      |
| `yz_plane_x_down`  | -X     | +Y   | -X (out of left face)       |

For each, `.workplane(offset=h)` shifts the sketch plane along the
normal by `h` (positive `h` = positive normal direction); `.extrude(h)`
sweeps the sketch along the normal by `h`. Positive numbers mean
positive in the world direction the face's name implies.

Three of the six (`xy_plane_z_down`, `xz_plane_y_up`,
`yz_plane_x_down`) have local-y that points in the negative world
direction the user thinks of as "up" looking at the face. Sketching
chirality (CCW vs CW arcs) and 2D coordinate semantics need a flip
on those. `WorldWorkplane`'s registered frame transforms make the API
hide it — the user writes world coordinates and CCW means CCW.

## WorldWorkplane

Drop-in `cq.Workplane` wrapper. Accepts `(a, b)` tuples directly
(no `*` unpacking) for `.moveTo`, `.lineTo`, `.radiusArc`,
`.threePointArc`, `.pushPoints`, `.polyline`. Applies the plane's
registered frame transform to those points, and negates radii when
the frame inverts chirality. Everything else (`.workplane`, `.extrude`,
`.cut`, `.union`, `.circle`, `.faces`, `.shell`, `.close`, ...) passes
through to the underlying `cq.Workplane`, with returned Workplanes
re-wrapped so the frame persists through the chain.

For non-chirality-flipped planes (`xy_plane_z_up`, `xz_plane_y_down`,
`yz_plane_x_up`) the wrapper's transforms are identity, so wrapping
is optional — `cq.Workplane(plane)` and `WorldWorkplane(plane)` are
equivalent. Use the wrapper anyway when you want the tuple calling
convention or when style consistency across two adjacent blocks of
code matters.

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
- `xy_plane_z_down` → `point=flip_y`, `radius=lambda r: -r`
  (world (x, y) → local (x, -y))
- `xz_plane_y_up`   → `point=flip_z`, `radius=lambda r: -r`
  (world (x, z) → local (x, -z))
- `yz_plane_x_down` → `point=flip_z`, `radius=lambda r: -r`
  (world (y, z) → local (y, -z))

The other three planes (`xy_plane_z_up`, `xz_plane_y_down`,
`yz_plane_x_up`) default to identity via `_lookup_frame` — no
registration needed.

To add a new workplane (e.g., tilted face, oblique cut) with a
non-identity frame: define the plane, then call
`_register_frame(plane, point=..., radius=...)`.

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

Currently overridden in `world_workplane.py`: `moveTo`, `lineTo`,
`radiusArc`, `threePointArc`, `pushPoints`, `polyline`, `center`,
`profile`. These all run the frame transform; on a flipped plane
they negate the second tuple component (and negate radii where
relevant).

Latent gaps (no consumer hits these today, but worth knowing):

- `.sketch().arc(...)`, `.tangentArcPoint(...)`, `.hLineTo(...)`,
  `.vLineTo(...)`, `.mirrorY()`, `.mirrorX()` — chirality-sensitive
- `.transformed(offset=(x, y, z))` — affects subsequent point
  interpretation
- `.slot2D(angle=...)` — angles aren't transformed (the `radius`
  lambda only handles signed scalars for `radiusArc`)
- `.placeSketch(sketch)` — points inside a pre-built `cq.Sketch`
  are not transformed when the sketch is placed onto a flipped
  plane. Authors who need a world-coord sketch on a flipped plane
  must either (a) write the sketch points in the plane's local
  frame, or (b) build the equivalent polyline + arcs inline via
  `WorldWorkplane` methods that ARE overridden.

Fix shape when any of these bite: add a named override that calls
`self._point` / `self._radius` on the relevant args. Same pattern as
`pushPoints` and `polyline`.

## When to use which

- **Inline single-point case** (e.g., `.moveTo(pt).circle(r)`): use
  `WorldWorkplane` methods directly inside the chain.
- **Polyline-with-arcs that wants a named profile**: build a
  `WorldProfile`, pass it to `.profile(prof)`.
- **Pure polyline (no arcs)**: use the canonical
  `.polyline([list of points])` — see `../cold-core/_reed_channels.md`'s
  `missing_wall_profile` example.
