"""World-coordinate CadQuery interface.

CadQuery's `cq.Workplane` reads coordinates in the workplane's *local*
frame. For half the named planes the local frame happens to match
world coordinates; for the other half it doesn't — e.g.
`cq.Workplane("XZ")` has a -Y normal, so `extrude(h)` with positive
`h` moves in world -Y, AND its local y-direction is +Z which differs
from the local-y of some other plane orientations. Combined with the
chirality inversion CadQuery introduces on flipped planes (radii
flip sign on `radiusArc`), mixing "world thinking" with cq's raw API
quietly produces sign-flipped geometry.

This module pins explicit single-axis-aligned workplanes for each of
the six box faces and a thin wrapper that lets call sites write
coordinates as `(world_a, world_b)` tuples — with positive numbers
meaning positive on the world axes — regardless of which face the
sketch lives on. Two blocks of code authoring on different faces
read the same way: same constructor shape, same method chain, same
positive-direction semantics for `.workplane(offset=...)`,
`.extrude(...)`, `.moveTo(...)`, `.circle/.rect/.slot2D`.

Box-face planes
---------------
Six module-level singletons, one per face of an axis-aligned box.
Identity is meaningful — `WorldWorkplane` looks up its frame
transform by `is` comparison, so do not construct your own copies;
import these.

  xy_plane_z_up    — XY plane, +Z normal.  Top face.
  xy_plane_z_down  — XY plane, -Z normal.  Bottom face.
  xz_plane_y_up    — XZ plane, +Y normal.  Back face.
  xz_plane_y_down  — XZ plane, -Y normal.  Front face.
  yz_plane_x_up    — YZ plane, +X normal.  Right face.
  yz_plane_x_down  — YZ plane, -X normal.  Left face.

For each, sketching on the plane and extruding with a positive
distance moves into the box (or out from the named face, depending
on which side of the face the box is on — the plane is just an
orientation, you choose by `.workplane(offset=...)` and the sign of
`.extrude(h)`).

Three of the six have a chirality inversion baked into the cross
product between their normal and xDir: `xy_plane_z_down`,
`xz_plane_y_up`, and `yz_plane_x_down`. On those planes, the local
y-direction points in the negative world direction of what the user
naturally thinks of as "up" looking at the face. `WorldWorkplane`'s
registered frame transforms (`flip_y` / `flip_z`) make the API hide
this — the user writes world coordinates and CCW means CCW.

WorldWorkplane
--------------
A cq.Workplane wrapper. Accepts (a, b) world-coord tuples directly
(no `*` unpacking) for `.moveTo`, `.lineTo`, `.radiusArc`,
`.threePointArc`, `.pushPoints`, `.polyline`. Applies the plane's
registered frame transform to those points and negates radii when
the frame inverts chirality. Other Workplane methods (`.workplane`,
`.extrude`, `.cut`, `.union`, `.circle`, `.faces`, `.shell`,
`.close`, ...) pass through via `__getattr__` delegation, with
returned Workplanes re-wrapped so the frame persists.

For non-chirality-flipped planes (xy_plane_z_up, xz_plane_y_down,
yz_plane_x_up) the wrapper's transforms are identity, so wrapping is
optional — `cq.Workplane(plane)` and `WorldWorkplane(plane)` are
equivalent. Use the wrapper anyway when you want the (a, b) tuple
calling convention or when style consistency across two adjacent
blocks of code matters.

WorldProfile
------------
A recipe-recorder for polyline-with-arcs profiles. Records the same
methods WorldWorkplane has (`moveTo`, `lineTo`, `radiusArc`,
`threePointArc`). Doesn't touch any workplane. Played back via
`WorldWorkplane.profile(prof)`. Gives polyline-with-arcs the same
"profile as a named noun" treatment that `.polyline([list of
points])` already gives pure polylines.

Current limitations
-------------------
`__getattr__` delegation is *silently incomplete*. It unwraps
WorldWorkplane args but doesn't traverse other arg shapes to apply
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
`pushPoints` and `polyline`.
"""

import cadquery as cq


# Box-face planes. xDir is the natural "right" direction for a viewer
# looking AT the face from outside the box; normal is the face's
# outward direction.
xy_plane_z_up    = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0,  1))
xy_plane_z_down  = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, 0, -1))
xz_plane_y_up    = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0,  1, 0))
xz_plane_y_down  = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
yz_plane_x_up    = cq.Plane(origin=(0, 0, 0), xDir=(0, 1, 0), normal=( 1, 0, 0))
yz_plane_x_down  = cq.Plane(origin=(0, 0, 0), xDir=(0, 1, 0), normal=(-1, 0, 0))


def flip_y(world_xy):
    """World (x, y) → (x, -y). For planes whose local y-direction is the
    negative world Y axis (xy_plane_z_down)."""
    x, y = world_xy
    return (x, -y)


def flip_z(world_ab):
    """World (a, z) → (a, -z). For planes whose local y-direction is the
    negative world Z axis (xz_plane_y_up, yz_plane_x_down). The first
    component is whichever world axis the plane's xDir lies on."""
    a, z = world_ab
    return (a, -z)


_world_frames = []


def _register_frame(plane, point=lambda p: p, radius=lambda r: r):
    """Associate a coordinate transform pair with a workplane.

    point: maps an (a, b) tuple to the (x, y) tuple cadquery expects
        for this plane's local coordinates.
    radius: maps a signed .radiusArc radius under the same transform.
        Must negate when `point` flips one axis (chirality inversion).
    """
    _world_frames.append((plane, dict(point=point, radius=radius)))


def _lookup_frame(plane):
    for p, frame in _world_frames:
        if p is plane:
            return frame
    return dict(point=lambda p: p, radius=lambda r: r)


class WorldProfile:
    """A profile recipe: records a sequence of moveTo/lineTo/radiusArc/
    threePointArc operations in world coordinates. Doesn't touch any
    workplane. Applied via WorldWorkplane.profile(prof)."""

    def __init__(self):
        self._ops = []

    def moveTo(self, p):
        self._ops.append(('moveTo', p))
        return self

    def lineTo(self, p):
        self._ops.append(('lineTo', p))
        return self

    def radiusArc(self, p, r):
        self._ops.append(('radiusArc', p, r))
        return self

    def threePointArc(self, m, e):
        self._ops.append(('threePointArc', m, e))
        return self


class WorldWorkplane:
    """A cq.Workplane wrapper that accepts (x, y) tuples directly (not
    unpacked scalars) and applies the plane's registered frame transform
    to points and radii. Other Workplane methods (.workplane, .extrude,
    .cut, .union, .polyline, .circle, .faces, .shell, .close, etc.) pass
    through unchanged via __getattr__ delegation, re-wrapping any
    Workplane returned so the frame persists through the chain."""

    def __init__(self, plane_or_wp, point=None, radius=None):
        if isinstance(plane_or_wp, cq.Workplane):
            self._wp = plane_or_wp
            plane = plane_or_wp.plane
        else:
            self._wp = cq.Workplane(plane_or_wp)
            plane = plane_or_wp
        frame = _lookup_frame(plane)
        self._point = point if point is not None else frame['point']
        self._radius = radius if radius is not None else frame['radius']

    def _wrap(self, wp):
        return WorldWorkplane(wp, point=self._point, radius=self._radius)

    def unwrap(self):
        """Return the underlying cq.Workplane for handing off to APIs
        that type-check on Workplane (cq.exporters.export, .cut/.union
        operand checks, etc.)."""
        return self._wp

    def moveTo(self, p):
        return self._wrap(self._wp.moveTo(*self._point(p)))

    def lineTo(self, p):
        return self._wrap(self._wp.lineTo(*self._point(p)))

    def radiusArc(self, p, r):
        return self._wrap(self._wp.radiusArc(self._point(p), self._radius(r)))

    def threePointArc(self, m, e):
        return self._wrap(self._wp.threePointArc(self._point(m), self._point(e)))

    def pushPoints(self, points):
        return self._wrap(self._wp.pushPoints([self._point(p) for p in points]))

    def polyline(self, points):
        return self._wrap(self._wp.polyline([self._point(p) for p in points]))

    def center(self, x, y):
        """Shift the workplane's local origin by world (x, y). Frame-flips
        the y component to match the chirality of the underlying plane
        (on xz_plane_y_up, the second argument is world Z, not local)."""
        return self._wrap(self._wp.center(*self._point((x, y))))

    def profile(self, prof):
        """Play back a WorldProfile's recorded ops on this workplane,
        applying the frame transforms."""
        wp = self._wp
        for op in prof._ops:
            kind = op[0]
            if kind == 'moveTo':
                wp = wp.moveTo(*self._point(op[1]))
            elif kind == 'lineTo':
                wp = wp.lineTo(*self._point(op[1]))
            elif kind == 'radiusArc':
                wp = wp.radiusArc(self._point(op[1]), self._radius(op[2]))
            elif kind == 'threePointArc':
                wp = wp.threePointArc(self._point(op[1]), self._point(op[2]))
        return self._wrap(wp)

    def __getattr__(self, name):
        attr = getattr(self._wp, name)
        if not callable(attr):
            return attr
        def wrapper(*args, **kwargs):
            args = tuple(a._wp if isinstance(a, WorldWorkplane) else a for a in args)
            kwargs = {k: (v._wp if isinstance(v, WorldWorkplane) else v) for k, v in kwargs.items()}
            result = attr(*args, **kwargs)
            return self._wrap(result) if isinstance(result, cq.Workplane) else result
        return wrapper


# Three of the six box-face planes have local y opposite the world
# axis the user thinks of as "up" looking at that face. Register the
# corresponding flip transforms; the other three default to identity
# via `_lookup_frame`.
_register_frame(xy_plane_z_down, point=flip_y, radius=lambda r: -r)
_register_frame(xz_plane_y_up,   point=flip_z, radius=lambda r: -r)
_register_frame(yz_plane_x_down, point=flip_z, radius=lambda r: -r)
