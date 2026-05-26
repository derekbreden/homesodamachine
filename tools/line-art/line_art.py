"""
Line-art drawing library.

A small DSL for declarative line-art drawings of boxy 3D objects projected
to isometric view. Built for the home-soda-machine quick-start illustrations.

Coordinate convention (right-handed):
- +x is to the right (width)
- +y is to the back (depth)
- +z is up (height)

Two canonical iso views, selected by Scene(view=...):

- 'front' (default): viewer at +x, -y, +z. Visible faces: front (y=0),
  right side (x=W), top (z=H). Layout: front face in the right half of
  the image, right side in the left half, top at the top.

- 'back': viewer at +x, +y, +z. Visible faces: back (y=D), right side
  (x=W), top (z=H). Layout: back face in the LEFT half of the image,
  right side in the right half, top at the top.

Public API:

    Scene(view='front'|'back') — collects boxes, renders to SVG
    Box(W, D, H) — an axis-aligned rectangular box with named faces
    box.front / .back / .top / .bottom / .left_side / .right_side — faces
    face.add_circle(at=(a, b), d=...) — circle in face-local 2D coords
    face.add_rectangle(at=(a, b), w=..., h=...) — rectangle, centered at `at`
    face.add_knob(at=(a, b), d=..., protrusion=...) — cylinder protruding outward
        (optional axis_3d= for a tilted axis, e.g. an angled dispense tip)
    face.add_rectangular_protrusion(at=(a, b), w=..., h=..., protrusion=...)
        — rectangular box protruding outward from the face

Face-local 2D coords (a, b) mean horizontal-from-left and vertical-from-bottom
as you look directly at the face.
"""

import math
from typing import Callable, List, Tuple


# ---------------------------------------------------------------------------
# Isometric projection
# ---------------------------------------------------------------------------

ISO_ANGLE = math.radians(30)
COS30 = math.cos(ISO_ANGLE)
SIN30 = math.sin(ISO_ANGLE)


def project_front(x: float, y: float, z: float) -> Tuple[float, float]:
    """Projection for the 'front' view (viewer at +x, -y, +z).

    Front face (y=0) ends up in the right half of the image, right side
    (x=W) in the left half, top (z=H) at the top. Closest-to-camera corner
    is (W, 0, H), which projects to the image center.
    """
    X = -(x + y) * COS30
    Y = (x - y) * SIN30 - z
    return X, Y


def project_back(x: float, y: float, z: float) -> Tuple[float, float]:
    """Projection for the 'back' view (viewer at +x, +y, +z).

    Back face (y=D) ends up in the LEFT half of the image, right side
    (x=W) in the right half, top (z=H) at the top. Closest-to-camera corner
    is (W, D, H), which projects to the image center.
    """
    X = (x - y) * COS30
    Y = (x + y) * SIN30 - z
    return X, Y


_PROJECTIONS = {
    "front": project_front,
    "back": project_back,
}


def project(x: float, y: float, z: float) -> Tuple[float, float]:
    """Default projection — kept for backward compatibility. Equivalent to
    project_front(x, y, z)."""
    return project_front(x, y, z)


# ---------------------------------------------------------------------------
# SVG element emitters
# ---------------------------------------------------------------------------

DEFAULT_STROKE = "black"
DEFAULT_STROKE_WIDTH = 1.5


def _svg_line(p1: Tuple[float, float], p2: Tuple[float, float]) -> str:
    return (
        f'  <line x1="{p1[0]:.3f}" y1="{p1[1]:.3f}" '
        f'x2="{p2[0]:.3f}" y2="{p2[1]:.3f}" '
        f'stroke="{DEFAULT_STROKE}" stroke-width="{DEFAULT_STROKE_WIDTH}" '
        f'fill="none" stroke-linecap="round" />'
    )


def _svg_polygon(points: List[Tuple[float, float]]) -> str:
    d = "M " + " L ".join(f"{p[0]:.3f},{p[1]:.3f}" for p in points) + " Z"
    return (
        f'  <path d="{d}" stroke="{DEFAULT_STROKE}" '
        f'stroke-width="{DEFAULT_STROKE_WIDTH}" '
        f'fill="none" stroke-linecap="round" stroke-linejoin="round" />'
    )


def _svg_polyline(points: List[Tuple[float, float]]) -> str:
    """Open polyline (path without Z). Used for arcs that are not closed."""
    if not points:
        return ""
    d = "M " + " L ".join(f"{p[0]:.3f},{p[1]:.3f}" for p in points)
    return (
        f'  <path d="{d}" stroke="{DEFAULT_STROKE}" '
        f'stroke-width="{DEFAULT_STROKE_WIDTH}" '
        f'fill="none" stroke-linecap="round" stroke-linejoin="round" />'
    )


# ---------------------------------------------------------------------------
# Face — one face of a Box, with its own 2D local coord system
# ---------------------------------------------------------------------------


class Face:
    """A single face of a Box.

    Features (circles, rectangles) are placed in face-local 2D coords (a, b),
    where `a` is horizontal-from-left and `b` is vertical-from-bottom as you
    look directly at the face. The face knows how to map (a, b) back to the
    parent box's 3D coord system.
    """

    def __init__(self, parent: "Box", name: str):
        self.parent = parent
        self.name = name
        self.features: List = []

    def _local_to_3d(self, point_2d: Tuple[float, float]) -> Tuple[float, float, float]:
        a, b = point_2d
        W, D, H = self.parent.W, self.parent.D, self.parent.H
        if self.name == "front":
            return (a, 0, b)
        if self.name == "back":
            return (W - a, D, b)
        if self.name == "top":
            return (a, b, H)
        if self.name == "bottom":
            return (a, b, 0)
        if self.name == "right_side":
            return (W, a, b)
        if self.name == "left_side":
            return (0, D - a, b)
        raise ValueError(f"Unknown face: {self.name}")

    def _basis_3d(self):
        """The unit vectors spanning the face's 2D plane, in 3D.

        First vector is the `a` axis (horizontal as you look at the face);
        second is the `b` axis (vertical).
        """
        if self.name == "front":
            return ((1, 0, 0), (0, 0, 1))
        if self.name == "back":
            return ((-1, 0, 0), (0, 0, 1))
        if self.name == "top":
            return ((1, 0, 0), (0, 1, 0))
        if self.name == "bottom":
            return ((1, 0, 0), (0, 1, 0))
        if self.name == "right_side":
            return ((0, 1, 0), (0, 0, 1))
        if self.name == "left_side":
            return ((0, -1, 0), (0, 0, 1))
        raise ValueError(f"Unknown face: {self.name}")

    def _outward_normal_3d(self) -> Tuple[float, float, float]:
        """Unit vector pointing outward from the face, in the parent box's
        3D coord system."""
        if self.name == "front":
            return (0, -1, 0)
        if self.name == "back":
            return (0, 1, 0)
        if self.name == "top":
            return (0, 0, 1)
        if self.name == "bottom":
            return (0, 0, -1)
        if self.name == "right_side":
            return (1, 0, 0)
        if self.name == "left_side":
            return (-1, 0, 0)
        raise ValueError(f"Unknown face: {self.name}")

    def add_circle(self, at: Tuple[float, float], d: float, label: str = None):
        """Add a circle on this face. `at` is the center in face-local coords;
        `d` is the diameter in mm. The circle is rendered as the projected
        ellipse in the isometric view."""
        self.features.append(_FaceCircle(face=self, at=at, d=d, label=label))

    def add_rectangle(
        self, at: Tuple[float, float], w: float, h: float, label: str = None
    ):
        """Add a rectangle centered at `at` in face-local coords, with width
        `w` (along the face's a-axis) and height `h` (along the b-axis)."""
        self.features.append(_FaceRectangle(face=self, at=at, w=w, h=h, label=label))

    def add_knob(
        self,
        at: Tuple[float, float],
        d: float,
        protrusion: float,
        axis_3d: Tuple[float, float, float] = None,
        label: str = None,
    ):
        """Add a cylindrical knob protruding outward from this face. `at`
        is the center on the face plane in face-local coords; `d` is the
        cylinder's diameter (cross-section perpendicular to its axis);
        `protrusion` is the axial length.

        `axis_3d` is the cylinder's axis direction in the parent box's 3D
        coords. Defaults to the face's outward normal (perpendicular knob).
        Pass a tilted vector for an angled spout: the cylinder's lateral
        surface intersects the face plane in an ellipse, and the line art
        draws that ellipse's visible arc where the cylinder meets the host
        face."""
        self.features.append(
            _FaceKnob(
                face=self, at=at, d=d, protrusion=protrusion,
                axis_3d=axis_3d, label=label,
            )
        )

    def add_rectangular_protrusion(
        self,
        at: Tuple[float, float],
        w: float,
        h: float,
        protrusion: float,
        label: str = None,
    ):
        """Add a rectangular box protruding outward from this face along
        the face's outward normal. `at` is the center in face-local coords;
        `w` is width along the face's a-axis; `h` is height along the
        b-axis; `protrusion` is how far the box sticks out from the face.

        Visibility currently assumes the +a and +b side faces of the
        protrusion are toward the camera (i.e., the protrusion is on the
        front face in the 'front' iso view, or any face whose face-local
        +a and +b axes both have a positive component toward the camera).
        Other face/view combos would need extra logic to pick the right
        hidden edges."""
        self.features.append(
            _FaceRectangularProtrusion(
                face=self, at=at, w=w, h=h, protrusion=protrusion, label=label,
            )
        )


# ---------------------------------------------------------------------------
# Feature primitives
# ---------------------------------------------------------------------------


class _FaceCircle:
    """A circle on a face. Renders as an ellipse in isometric projection."""

    def __init__(self, face: Face, at: Tuple[float, float], d: float, label: str = None):
        self.face = face
        self.at = at
        self.d = d
        self.label = label

    def svg(self, proj: Callable) -> str:
        r = self.d / 2
        cx_3d = self.face._local_to_3d(self.at)
        u_3d, v_3d = self.face._basis_3d()
        n = 64
        points = []
        for i in range(n):
            theta = 2 * math.pi * i / n
            c, s = math.cos(theta), math.sin(theta)
            p_3d = (
                cx_3d[0] + r * (c * u_3d[0] + s * v_3d[0]),
                cx_3d[1] + r * (c * u_3d[1] + s * v_3d[1]),
                cx_3d[2] + r * (c * u_3d[2] + s * v_3d[2]),
            )
            points.append(proj(*p_3d))
        return _svg_polygon(points)


class _FaceRectangle:
    """A rectangle on a face, centered at `at`. Renders as a parallelogram
    in isometric projection."""

    def __init__(
        self,
        face: Face,
        at: Tuple[float, float],
        w: float,
        h: float,
        label: str = None,
    ):
        self.face = face
        self.at = at
        self.w = w
        self.h = h
        self.label = label

    def svg(self, proj: Callable) -> str:
        cx, cy = self.at
        corners_2d = [
            (cx - self.w / 2, cy - self.h / 2),
            (cx + self.w / 2, cy - self.h / 2),
            (cx + self.w / 2, cy + self.h / 2),
            (cx - self.w / 2, cy + self.h / 2),
        ]
        corners_3d = [self.face._local_to_3d(p) for p in corners_2d]
        return _svg_polygon([proj(*p) for p in corners_3d])


class _FaceKnob:
    """A cylindrical knob protruding outward from a face. Renders as:

    1. The projected ellipse of the protruded front face (closed polygon).
    2. Two silhouette tangent lines from the back rim to the front rim.
    3. The visible (far-side) half of the back rim — the arc where the
       cylinder meets the host face. The near-side half of the back rim
       sits behind the cylinder body in projection and is not drawn,
       keeping the line art visible-outlines-only.

    The axis can be either the face's outward normal (a perpendicular
    knob — back rim is a circle in the face plane) or a tilted vector
    (an angled spout — back rim is the cylinder's elliptical intersection
    with the face plane). Same algorithm handles both: the back rim is
    sampled by the t(θ) formula that walks each lateral surface line
    from the front rim down the axis until it hits the face plane.
    """

    def __init__(
        self,
        face: Face,
        at: Tuple[float, float],
        d: float,
        protrusion: float,
        axis_3d: Tuple[float, float, float] = None,
        label: str = None,
    ):
        self.face = face
        self.at = at
        self.d = d
        self.protrusion = protrusion
        self.axis_3d = axis_3d
        self.label = label

    def svg(self, proj: Callable) -> str:
        r = self.d / 2
        L = self.protrusion
        face_center_3d = self.face._local_to_3d(self.at)
        n_3d = self.face._outward_normal_3d()

        # Cylinder axis — default to face's outward normal.
        if self.axis_3d is None:
            axis = n_3d
        else:
            axis = self.axis_3d
        axis_mag = math.sqrt(axis[0] ** 2 + axis[1] ** 2 + axis[2] ** 2)
        axis = (axis[0] / axis_mag, axis[1] / axis_mag, axis[2] / axis_mag)

        # Perpendicular basis (u, v) to the cylinder axis. Pick a helper
        # direction not parallel to axis, then cross-product. Result is
        # u ⊥ axis and v = axis × u ⊥ both.
        helper = (1, 0, 0) if abs(axis[0]) < 0.9 else (0, 1, 0)
        u_x = axis[1] * helper[2] - axis[2] * helper[1]
        u_y = axis[2] * helper[0] - axis[0] * helper[2]
        u_z = axis[0] * helper[1] - axis[1] * helper[0]
        u_mag = math.sqrt(u_x * u_x + u_y * u_y + u_z * u_z)
        u = (u_x / u_mag, u_y / u_mag, u_z / u_mag)
        v = (
            axis[1] * u[2] - axis[2] * u[1],
            axis[2] * u[0] - axis[0] * u[2],
            axis[0] * u[1] - axis[1] * u[0],
        )

        # Dot products against the face's outward normal. The back rim's
        # axial position t(θ) = -r·(cos θ·(u·n) + sin θ·(v·n)) / (axis·n)
        # — where the lateral surface line at angle θ crosses the face
        # plane. When axis = n, axis·n = 1 and u·n = v·n = 0, so t = 0
        # and the back rim is a circle in the face plane.
        u_dot_n = u[0] * n_3d[0] + u[1] * n_3d[1] + u[2] * n_3d[2]
        v_dot_n = v[0] * n_3d[0] + v[1] * n_3d[1] + v[2] * n_3d[2]
        axis_dot_n = axis[0] * n_3d[0] + axis[1] * n_3d[1] + axis[2] * n_3d[2]

        front_center_3d = (
            face_center_3d[0] + L * axis[0],
            face_center_3d[1] + L * axis[1],
            face_center_3d[2] + L * axis[2],
        )

        # Sample back-rim and front-rim points around the cylinder.
        n_samples = 64
        back_2d: List[Tuple[float, float]] = []
        front_2d: List[Tuple[float, float]] = []
        for i in range(n_samples):
            theta = 2 * math.pi * i / n_samples
            c, s = math.cos(theta), math.sin(theta)
            # Front rim — circle of radius r perpendicular to axis.
            front_pt_3d = (
                front_center_3d[0] + r * (c * u[0] + s * v[0]),
                front_center_3d[1] + r * (c * u[1] + s * v[1]),
                front_center_3d[2] + r * (c * u[2] + s * v[2]),
            )
            # Back rim — intersection of lateral surface line at angle θ
            # with the face plane.
            t_back = -r * (c * u_dot_n + s * v_dot_n) / axis_dot_n
            back_pt_3d = (
                face_center_3d[0] + r * (c * u[0] + s * v[0]) + t_back * axis[0],
                face_center_3d[1] + r * (c * u[1] + s * v[1]) + t_back * axis[1],
                face_center_3d[2] + r * (c * u[2] + s * v[2]) + t_back * axis[2],
            )
            back_2d.append(proj(*back_pt_3d))
            front_2d.append(proj(*front_pt_3d))

        # Projected cylinder-axis direction (back center → front center).
        # Silhouette tangent points are the back-rim samples whose offset
        # from the back center has the most extreme component perpendicular
        # to this projected axis.
        back_center_2d = proj(*face_center_3d)
        front_center_2d = proj(*front_center_3d)
        axis_dx = front_center_2d[0] - back_center_2d[0]
        axis_dy = front_center_2d[1] - back_center_2d[1]
        perp_dx = -axis_dy
        perp_dy = axis_dx

        def perp_score(i: int) -> float:
            dx = back_2d[i][0] - back_center_2d[0]
            dy = back_2d[i][1] - back_center_2d[1]
            return dx * perp_dx + dy * perp_dy

        def axis_score(i: int) -> float:
            dx = back_2d[i][0] - back_center_2d[0]
            dy = back_2d[i][1] - back_center_2d[1]
            return dx * axis_dx + dy * axis_dy

        i_max = max(range(n_samples), key=perp_score)
        i_min = min(range(n_samples), key=perp_score)

        # Visible back-rim arc — walk from i_max to i_min through the half
        # of the rim with axis_score < 0 (the far side, away from the
        # protrusion direction in projection). The near-side half sits
        # behind the cylinder body and is not drawn.
        forward = (i_max + 1) % n_samples
        direction = 1 if axis_score(forward) <= 0 else -1
        arc_indices: List[int] = [i_max]
        i = (i_max + direction) % n_samples
        while i != i_min:
            arc_indices.append(i)
            i = (i + direction) % n_samples
        arc_indices.append(i_min)
        back_arc_2d = [back_2d[i] for i in arc_indices]

        parts = [
            _svg_polygon(front_2d),
            _svg_line(back_2d[i_max], front_2d[i_max]),
            _svg_line(back_2d[i_min], front_2d[i_min]),
            _svg_polyline(back_arc_2d),
        ]
        return "\n".join(parts)


class _FaceRectangularProtrusion:
    """A rectangular box protruding outward from a face. Drawn as the
    box's 9 visible edges in iso projection: the 4 edges of the front
    (protruded) rectangle, plus the 2 visible back-rectangle edges (top
    and right, where the protrusion meets the host face), plus the 3
    side connector edges from back rim to front rim (top-left, top-right,
    bottom-right corners).

    See Face.add_rectangular_protrusion for the visibility assumption
    (+a and +b sides of the protrusion are toward the camera)."""

    def __init__(
        self,
        face: Face,
        at: Tuple[float, float],
        w: float,
        h: float,
        protrusion: float,
        label: str = None,
    ):
        self.face = face
        self.at = at
        self.w = w
        self.h = h
        self.protrusion = protrusion
        self.label = label

    def svg(self, proj: Callable) -> str:
        u_3d, v_3d = self.face._basis_3d()
        n_3d = self.face._outward_normal_3d()
        face_center_3d = self.face._local_to_3d(self.at)

        def corner(da: int, db: int, dp: int) -> Tuple[float, float, float]:
            return (
                face_center_3d[0]
                + da * (self.w / 2) * u_3d[0]
                + db * (self.h / 2) * v_3d[0]
                + dp * self.protrusion * n_3d[0],
                face_center_3d[1]
                + da * (self.w / 2) * u_3d[1]
                + db * (self.h / 2) * v_3d[1]
                + dp * self.protrusion * n_3d[1],
                face_center_3d[2]
                + da * (self.w / 2) * u_3d[2]
                + db * (self.h / 2) * v_3d[2]
                + dp * self.protrusion * n_3d[2],
            )

        # Back rectangle corners (dp=0) and front rectangle corners (dp=1).
        # Naming: B = back rect, F = front rect; L=-a, R=+a; B=-b, T=+b.
        BBL = proj(*corner(-1, -1, 0))
        BBR = proj(*corner(+1, -1, 0))
        BTR = proj(*corner(+1, +1, 0))
        BTL = proj(*corner(-1, +1, 0))
        FBL = proj(*corner(-1, -1, 1))
        FBR = proj(*corner(+1, -1, 1))
        FTR = proj(*corner(+1, +1, 1))
        FTL = proj(*corner(-1, +1, 1))

        # 9 visible edges (assuming +a and +b side faces are visible):
        # the hidden corner is BBL (back-bottom-left) and the 3 hidden
        # edges all touch it (BBL-BBR, BBL-BTL, BBL-FBL); the other 9
        # are the ones we draw.
        edges = [
            # Front rectangle outline.
            (FTL, FTR), (FTR, FBR), (FBR, FBL), (FBL, FTL),
            # Visible back rectangle edges (top and right of back rect).
            (BTL, BTR), (BTR, BBR),
            # Side connectors from back rim to front rim, at the 3
            # visible back corners (top-left, top-right, bottom-right).
            (BTL, FTL), (BTR, FTR), (BBR, FBR),
        ]
        return "\n".join(_svg_line(p1, p2) for p1, p2 in edges)


# ---------------------------------------------------------------------------
# Box
# ---------------------------------------------------------------------------


class Box:
    """An axis-aligned rectangular box. Width along x, Depth along y, Height
    along z. Six named faces, each carrying its own feature list.
    """

    def __init__(self, W: float, D: float, H: float):
        self.W = W
        self.D = D
        self.H = H
        self.front = Face(self, "front")
        self.back = Face(self, "back")
        self.top = Face(self, "top")
        self.bottom = Face(self, "bottom")
        self.right_side = Face(self, "right_side")
        self.left_side = Face(self, "left_side")

    def all_faces(self) -> List[Face]:
        return [
            self.front,
            self.back,
            self.top,
            self.bottom,
            self.right_side,
            self.left_side,
        ]

    def visible_edges(self, view: str = "front"):
        """The 9 unique edges visible from the given isometric view.

        For 'front' (viewer at +x, -y, +z): edges of front (y=0), top (z=H),
        and right side (x=W).
        For 'back' (viewer at +x, +y, +z): edges of back (y=D), top (z=H),
        and right side (x=W) — back face appears on the LEFT half of image,
        right side on the right half.
        """
        W, D, H = self.W, self.D, self.H
        if view == "front":
            return [
                # Front face
                ((0, 0, 0), (W, 0, 0)),         # front bottom
                ((W, 0, 0), (W, 0, H)),         # front right vertical
                ((W, 0, H), (0, 0, H)),         # front top
                ((0, 0, H), (0, 0, 0)),         # front left vertical
                # Top face (back and left edges; front and right are shared)
                ((W, D, H), (0, D, H)),         # back top
                ((0, 0, H), (0, D, H)),         # top left (along y)
                # Right side (bottom and back-vertical; top is shared, front is shared)
                ((W, 0, 0), (W, D, 0)),         # right side bottom (along y)
                ((W, D, 0), (W, D, H)),         # back right vertical
                # Shared top-right edge (boundary between top and right side)
                ((W, 0, H), (W, D, H)),
            ]
        if view == "back":
            return [
                # Back face
                ((0, D, 0), (W, D, 0)),         # back bottom (along x)
                ((W, D, 0), (W, D, H)),         # back right vertical (shared with right side)
                ((W, D, H), (0, D, H)),         # back top
                ((0, D, H), (0, D, 0)),         # back left vertical
                # Right side (bottom and front-vertical; top is shared, back is shared)
                ((W, 0, 0), (W, D, 0)),         # right side bottom (along y)
                ((W, 0, 0), (W, 0, H)),         # right side front vertical
                # Top face (front and left edges; back is shared with back face,
                # right is shared with right side)
                ((0, 0, H), (W, 0, H)),         # top front (along x)
                ((0, 0, H), (0, D, H)),         # top left (along y)
                # Shared top-right edge (boundary between top and right side)
                ((W, 0, H), (W, D, H)),
            ]
        raise ValueError(f"Unknown view: {view!r}. Options: {list(_PROJECTIONS.keys())}")


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------


class Scene:
    """Top-level container. Holds boxes, renders to SVG."""

    def __init__(self, view: str = "front", padding: float = 30):
        if view not in _PROJECTIONS:
            raise ValueError(
                f"Unknown view: {view!r}. Options: {list(_PROJECTIONS.keys())}"
            )
        self.view = view
        self.items: List[Box] = []
        self.padding = padding

    def add(self, item: Box) -> Box:
        self.items.append(item)
        return item

    def render(self, path: str) -> None:
        proj = _PROJECTIONS[self.view]
        elements: List[str] = []

        # Box outlines first (so feature shapes sit on top of them)
        for item in self.items:
            for edge in item.visible_edges(self.view):
                p1 = proj(*edge[0])
                p2 = proj(*edge[1])
                elements.append(_svg_line(p1, p2))

        # Feature shapes
        for item in self.items:
            for face in item.all_faces():
                for feature in face.features:
                    elements.append(feature.svg(proj))

        # Compute viewbox from projected edge endpoints
        pts: List[Tuple[float, float]] = []
        for item in self.items:
            for edge in item.visible_edges(self.view):
                pts.append(proj(*edge[0]))
                pts.append(proj(*edge[1]))
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x_min = min(xs) - self.padding
        y_min = min(ys) - self.padding
        x_max = max(xs) + self.padding
        y_max = max(ys) + self.padding
        width = x_max - x_min
        height = y_max - y_min

        with open(path, "w") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(
                f'<svg xmlns="http://www.w3.org/2000/svg" '
                f'viewBox="{x_min:.3f} {y_min:.3f} {width:.3f} {height:.3f}" '
                f'width="{width:.3f}mm" height="{height:.3f}mm">\n'
            )
            for el in elements:
                f.write(el + "\n")
            f.write("</svg>\n")
