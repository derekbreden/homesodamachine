"""Pick-text composer — the CAD side of the step viewer's pick channel.

The viewer's edge picker copies geometry as pick text (file / solid /
edge / faceA / faceB / click lines), and its Find box accepts the same
format pasted back: it opens the file a `file:` line names, highlights
every recognizable pick, and frames the camera on them. This module
composes those lines from CadQuery geometry, so an agent pointing a
person at an edge or face emits text the person pastes straight into
the Find box.

Format truth lives in web/public/js/viewer/pick-format.js (the
viewer's parser + matcher); web/tests/pick-format.test.js round-trips
this module's demo output through that parser.

Compose from geometry:

    import sys
    from pathlib import Path
    sys.path.insert(
        0,
        str(next(p for p in Path(__file__).resolve().parents if p.name == "hardware") / "scripts"),
    )
    from pick_text import from_edge, from_face, file_line, click

    print(file_line(step_path))                      # which STEP to open
    print(from_edge(solid.edges(">Z").vals()[0]))    # edge: …
    print(from_face(solid.faces(">Z").vals()[0]))    # face: …
    print(click(cq.Vector(1, 2, 3)))                 # click: … (point marker)

Or from raw numbers via straight() / arc_line() / circle_line() /
plane_face() / cylinder_face(). Demo (also the round-trip test
fixture):

    tools/cad-venv/bin/python hardware/scripts/pick_text.py
"""

from pathlib import Path


# --- number / point formatting (mirrors pick-format.js fnum/fpt) ---

def fnum(v: float) -> str:
    s = f"{v:.3f}"
    return "0.000" if s == "-0.000" else s


def fpt(p) -> str:
    """Format a point/vector with .x/.y/.z (cq.Vector qualifies)."""
    return f"x={fnum(p.x)} y={fnum(p.y)} z={fnum(p.z)}"


# --- raw-number composers ---

def straight(a, b, label: str = "edge") -> str:
    d = _normalized(_sub(b, a))
    return (
        f"{label}: {fpt(a)} → {fpt(b)} · len {_dist(a, b):.3f}"
        f" · straight · dir {fpt(d)}"
    )


def arc_line(a, b, center, axis, r: float, length: float, label: str = "edge") -> str:
    return (
        f"{label}: {fpt(a)} → {fpt(b)} · len {length:.3f}"
        f" · arc r={r:.3f} · center {fpt(center)} · axis {fpt(axis)}"
    )


def circle_line(center, d: float, axis, circumference: float, label: str = "edge") -> str:
    return (
        f"{label}: circle ⌀{d:.3f} · center {fpt(center)}"
        f" · circumference {circumference:.3f} · axis {fpt(axis)}"
    )


def plane_face(n, thru, label: str = "face") -> str:
    return f"{label}: plane · n {fpt(n)} · thru {fpt(thru)}"


def cylinder_face(r: float, axis_point, direction, label: str = "face") -> str:
    return f"{label}: cylinder · r={r:.3f} · axis {fpt(axis_point)} · dir {fpt(direction)}"


def curved_face(near, label: str = "face") -> str:
    return f"{label}: curved · near {fpt(near)}"


def click(p) -> str:
    return f"click: {fpt(p)}"


def solid_line(name: str) -> str:
    return f"solid: {name}"


def file_line(step_path) -> str:
    """Repo-root-relative file line — the Find box opens this file before
    matching, so paths must carry the repo prefix the viewer's copy blobs
    use (hardware/…)."""
    p = Path(step_path).resolve()
    for parent in p.parents:
        if (parent / ".git").exists():
            return f"file: {p.relative_to(parent)}"
    return f"file: {step_path}"


# --- CadQuery composers ---
# Classify through OCP's BRepAdaptor so the line carries the same
# parameters the viewer reconstructs from the mesh.

def from_edge(edge, label: str = "edge") -> str:
    """Pick line for a cq.Edge: straight, arc, full circle, or curve."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GeomAbs import GeomAbs_Line, GeomAbs_Circle

    a, b = edge.startPoint(), edge.endPoint()
    length = edge.Length()
    curve = BRepAdaptor_Curve(edge.wrapped)
    kind = curve.GetType()

    if kind == GeomAbs_Line:
        return straight(a, b, label)
    if kind == GeomAbs_Circle:
        circ = curve.Circle()
        loc, axd = circ.Location(), circ.Axis().Direction()
        center = _vec(loc.X(), loc.Y(), loc.Z())
        axis = _vec(axd.X(), axd.Y(), axd.Z())
        r = circ.Radius()
        if _dist(a, b) < 1e-6:  # closed — a full circle
            return circle_line(center, 2.0 * r, axis, length, label)
        return arc_line(a, b, center, axis, r, length, label)
    return f"{label}: {fpt(a)} → {fpt(b)} · len {length:.3f} · curve"


def from_face(face, label: str = "face") -> str:
    """Pick line for a cq.Face: plane, cylinder, or curved-with-a-point."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder

    center = face.Center()
    surf = BRepAdaptor_Surface(face.wrapped)
    kind = surf.GetType()

    if kind == GeomAbs_Plane:
        return plane_face(face.normalAt(center), center, label)
    if kind == GeomAbs_Cylinder:
        cyl = surf.Cylinder()
        loc, axd = cyl.Position().Location(), cyl.Position().Direction()
        return cylinder_face(
            cyl.Radius(),
            _vec(loc.X(), loc.Y(), loc.Z()),
            _vec(axd.X(), axd.Y(), axd.Z()),
            label,
        )
    return curved_face(center, label)


# --- small vector helpers (work on anything with .x/.y/.z) ---

def _vec(x, y, z):
    class _V:
        __slots__ = ("x", "y", "z")

        def __init__(self):
            self.x, self.y, self.z = x, y, z

    return _V()


def _sub(a, b):
    return _vec(a.x - b.x, a.y - b.y, a.z - b.z)


def _dist(a, b) -> float:
    d = _sub(a, b)
    return (d.x * d.x + d.y * d.y + d.z * d.z) ** 0.5


def _normalized(v):
    n = (v.x * v.x + v.y * v.y + v.z * v.z) ** 0.5 or 1.0
    return _vec(v.x / n, v.y / n, v.z / n)


# --- demo: one line of each kind off a small solid ---
# Doubles as the round-trip fixture: web/tests/pick-format.test.js runs
# this and feeds the output through the viewer's parser.

def _demo() -> str:
    import cadquery as cq

    solid = (
        cq.Workplane("XY")
        .box(20, 10, 4)
        .edges("|Z and >X and >Y")
        .fillet(3)
        .faces(">Z")
        .workplane()
        .hole(4)
    )
    lines = []

    kinds_wanted = {"straight", "arc", "circle"}
    for e in solid.val().Edges():
        line = from_edge(e)
        kind = "circle" if "circle" in line else ("arc" if " arc " in line else ("straight" if "straight" in line else "curve"))
        if kind in kinds_wanted:
            kinds_wanted.discard(kind)
            lines.append(line)
        if not kinds_wanted:
            break

    face_labels = iter(["faceA", "faceB"])
    face_kinds_wanted = {"plane", "cylinder"}
    for f in solid.val().Faces():
        kind_line = from_face(f)
        kind = "plane" if "plane" in kind_line else ("cylinder" if "cylinder" in kind_line else "curved")
        if kind in face_kinds_wanted:
            face_kinds_wanted.discard(kind)
            lines.append(from_face(f, label=next(face_labels)))
        if not face_kinds_wanted:
            break

    lines.append(click(_vec(1.0, -2.5, 3.75)))
    return "\n".join(lines)


if __name__ == "__main__":
    print(_demo())
