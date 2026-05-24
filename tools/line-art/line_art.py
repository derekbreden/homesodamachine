"""
Line-art drawing library.

A small DSL for declarative line-art drawings of boxy 3D objects projected
to isometric view. Built for the home-soda-machine quick-start illustrations.

Coordinate convention (right-handed):
- +x is to the right (width)
- +y is to the back (depth)
- +z is up (height)
- Viewer is at +x, -y, +z direction, so the front face (y=0), right side
  (x=W), and top (z=H) are visible.

Isometric projection to SVG (Y grows downward):
- X_svg = (x - y) * cos(30°)
- Y_svg = (x + y) * sin(30°) - z

Public API:

    Scene() — collects boxes, renders to SVG
    Box(W, D, H) — an axis-aligned rectangular box with named faces
    box.front / .back / .top / .bottom / .left_side / .right_side — faces
    face.add_circle(at=(a, b), d=...) — circle in face-local 2D coords
    face.add_rectangle(at=(a, b), w=..., h=...) — rectangle, centered at `at`

Face-local 2D coords (a, b) mean horizontal-from-left and vertical-from-bottom
as you look directly at the face. So on `box.front`, (a, b) = (x, z) in 3D.
On `box.top`, (a, b) = (x, y). On `box.right_side`, (a, b) = (y, z).

Usage:

    from line_art import Scene, Box

    scene = Scene()
    box = scene.add(Box(W=269, D=280, H=280))
    box.front.add_circle(at=(80, 220), d=25)
    box.front.add_rectangle(at=(135, 150), w=30, h=8)
    scene.render('output.svg')
"""

import math
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Isometric projection
# ---------------------------------------------------------------------------

ISO_ANGLE = math.radians(30)
COS30 = math.cos(ISO_ANGLE)
SIN30 = math.sin(ISO_ANGLE)


def project(x: float, y: float, z: float) -> Tuple[float, float]:
    """Project a 3D point to 2D SVG coords."""
    X = (x - y) * COS30
    Y = (x + y) * SIN30 - z
    return X, Y


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

    def svg(self) -> str:
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
            points.append(project(*p_3d))
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

    def svg(self) -> str:
        cx, cy = self.at
        corners_2d = [
            (cx - self.w / 2, cy - self.h / 2),
            (cx + self.w / 2, cy - self.h / 2),
            (cx + self.w / 2, cy + self.h / 2),
            (cx - self.w / 2, cy + self.h / 2),
        ]
        corners_3d = [self.face._local_to_3d(p) for p in corners_2d]
        return _svg_polygon([project(*p) for p in corners_3d])


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

    def visible_edges(self):
        """The 9 unique edges visible from the isometric viewer (+x, -y, +z).

        Front face contributes 4. The top face's back edge and left edge are
        new (its front edge is shared with the top of the front face, its
        right edge is shared with the top of the right side). The right side
        contributes its bottom and back-vertical edges as new. The right-edge
        of the top is the shared boundary between top and right side and is
        drawn once.
        """
        W, D, H = self.W, self.D, self.H
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


# ---------------------------------------------------------------------------
# Scene
# ---------------------------------------------------------------------------


class Scene:
    """Top-level container. Holds boxes, renders to SVG."""

    def __init__(self, padding: float = 30):
        self.items: List[Box] = []
        self.padding = padding

    def add(self, item: Box) -> Box:
        self.items.append(item)
        return item

    def render(self, path: str) -> None:
        elements: List[str] = []

        # Box outlines first (so feature shapes sit on top of them)
        for item in self.items:
            for edge in item.visible_edges():
                p1 = project(*edge[0])
                p2 = project(*edge[1])
                elements.append(_svg_line(p1, p2))

        # Feature shapes
        for item in self.items:
            for face in item.all_faces():
                for feature in face.features:
                    elements.append(feature.svg())

        # Compute viewbox from projected edge endpoints
        pts: List[Tuple[float, float]] = []
        for item in self.items:
            for edge in item.visible_edges():
                pts.append(project(*edge[0]))
                pts.append(project(*edge[1]))
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
