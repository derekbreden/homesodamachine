"""Pick reader — what each of the machine's surfaces holds where Derek clicked.

`pick_text.py` composes pick text from CadQuery geometry, pointing a person at an edge. This is
the other direction: pick text pasted back in, answered from the files the `file:` line names.

THERE ARE THREE SURFACES AND THEY ARE NOT THE SAME SURFACE.

    authored   `<piece>.step`        the solid the CadQuery script built
    printed    `<piece>.stl`         the tessellation a slicer reads, flutes cut in
    drawn      `<piece>.step.mesh`   the payload the viewer draws, printed collapsed to a budget

Under `pack.BUNDLED_PAYLOAD_DIRS` a picture is drawn off the payload, so a pick is taken off the
payload, and the payload is the print reduced as far as it goes while staying inside a
deflection budget (`flute_payload.simplify_within`). A budget is a DISTANCE bound. It cannot
preserve a feature shorter than itself: a 0.25 mm pad is collapsed into its wall and bridged
with long skinny triangles, and the reading never leaves budget while that happens. So a
coordinate can be real on one surface, real on all three, or on the payload alone — and every
one of those is a different question.

WHERE A THING MANIFESTS IS NOT WHETHER IT IS REAL. This reader says which surfaces hold the
window and how far each stands from the probe. That is a location, and it is where the
investigation starts. It is never a verdict that somebody clicking the viewer saw nothing:
a payload-only reading is the payload reporting a feature it could not draw, and what could
not be drawn at that scale is usually a feature that could not be printed at that scale either.

Every point the pick carries is probed — the click, both edge endpoints, and any `thru`/`near`
face point — and each surface answers with what it holds inside the window, NEAREST FIRST, each
row carrying a point on it and the distance to that point.

    tools/cad-venv/bin/python hardware/scripts/pick_read.py <<'EOF'
    file: hardware/printed-parts/enclosure/enclosure/enclosure-back-top.step.mesh
    click: x=98.373 y=244.482 z=257.216
    EOF

    tools/cad-venv/bin/python hardware/scripts/pick_read.py pick.txt --radius 2.0
    tools/cad-venv/bin/python hardware/scripts/pick_read.py selftest

`--radius` sets the window (default 1.0 mm). `--surfaces` limits which are read, for a piece
whose solid is slow to open or whose payload has not been cut.
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import flute_payload                                                     # noqa: E402
import _mesh_payload                                                     # noqa: E402

_PT = re.compile(r"x=(-?[\d.]+)\s+y=(-?[\d.]+)\s+z=(-?[\d.]+)")
#: Normals within this many degrees of each other are one plane.
_NORMAL_DEG = 5.0
#: Offsets within this distance along a shared normal are one plane.
_OFFSET_MM = 0.02
#: The surfaces, in the order a reading is easiest to compare across.
SURFACES = ("authored", "printed", "drawn")


def points(text):
    """Every probe point in `text`, as (label, xyz), in the order the lines carry them.

    A pick line carries positions and directions in the same `x= y= z=` shape, and the
    word in front of one is what separates them: `n`, `dir` and `axis` introduce a
    direction, which is nowhere.
    """
    found = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("file:", "solid:")):
            continue
        tag = line.split(":", 1)[0] if ":" in line else "?"
        seen = 0
        for m in _PT.finditer(line):
            lead = line[:m.start()].rstrip().rsplit(" ", 1)[-1].strip("·").strip()
            if lead in ("n", "dir", "axis"):
                continue
            seen += 1
            label = tag if seen == 1 else f"{tag} →" if tag == "edge" else f"{tag} {seen}"
            found.append((label, np.array([float(m.group(1)), float(m.group(2)),
                                           float(m.group(3))])))
    return found


def source(text):
    """The three surfaces the `file:` line points at, as {name: path or None}.

    The line names the bytes that were DRAWN, which for a bundled payload is the `.step.mesh`,
    and it carries that payload's readings after a `·`. Either way the piece is the same piece,
    so the name is taken back to its stem and all three surfaces are looked for beside it."""
    for line in text.splitlines():
        if line.strip().startswith("file:"):
            named = line.split(":", 1)[1].split("·")[0].strip()
            break
    else:
        raise SystemExit("no file: line in the pick")
    named = Path(named)
    if named.suffix == ".mesh":
        named = named.with_suffix("")
    root = Path(__file__).resolve().parent.parent.parent
    step = named if named.is_absolute() else root / named
    if not step.exists():
        raise SystemExit(f"{step} is not in the tree")
    payload = step.with_name(step.name + ".mesh")
    stl = step.with_suffix(".stl")
    return {"authored": step,
            "printed": stl if stl.exists() else None,
            "drawn": payload if payload.exists() else None}


# --- the tessellated surfaces: printed and drawn ---

def load_mesh(path, kind):
    """The printed STL, or the payload's triangles, as one trimesh."""
    if kind == "printed":
        return trimesh.load(str(path), process=False)
    meshes = flute_payload.read_payload(path)
    if not meshes:
        return None
    m = meshes[0]
    return trimesh.Trimesh(np.asarray(m["pos"], dtype=float).reshape(-1, 3),
                           np.asarray(m["idx"], dtype=np.int64).reshape(-1, 3),
                           process=False)


def planes(mesh, point, radius):
    """The distinct planes `mesh` holds within `radius` of `point`, nearest first.

    Each row is (normal, nearest point ON the surface, distance to it, facet count, span).

    A facet reaches the window when its own extent does. One long triangle spanning a whole
    land has its centre far from any click on it, so centres do not select — and one bridging
    a collapsed feature spans further still, which is exactly the row worth seeing.

    THE POINT REPORTED IS ON THE SURFACE AND NEAREST THE PROBE. A plane's offset along its own
    normal is a projection, not a place: on a tilted normal it reads as a coordinate tens of
    millimetres from the facet it describes, and two planes at one spot report as two planes
    far apart. Distance to the probe is what orders them, because that is the question a click
    asks."""
    tri = mesh.triangles
    lo, hi = point - radius, point + radius
    near = (tri.min(axis=1) <= hi).all(axis=1) & (tri.max(axis=1) >= lo).all(axis=1)
    if not near.any():
        return []
    idx = np.flatnonzero(near)
    nrm = mesh.face_normals[idx]
    off = np.einsum("ij,ij->i", nrm, mesh.triangles_center[idx])

    groups = []
    cos_tol = np.cos(np.radians(_NORMAL_DEG))
    for i, (n, o) in enumerate(zip(nrm, off)):
        for g in groups:
            if float(np.dot(g["n"], n)) >= cos_tol and abs(g["o"] - o) <= _OFFSET_MM:
                g["f"].append(idx[i])
                break
        else:
            groups.append({"n": n, "o": o, "f": [idx[i]]})

    out = []
    for g in groups:
        faces = np.asarray(g["f"])
        tris = mesh.triangles[faces]
        on = trimesh.triangles.closest_point(tris, np.tile(point, (len(tris), 1)))
        d = np.linalg.norm(on - point, axis=1)
        k = int(np.argmin(d))
        v = mesh.vertices[mesh.faces[faces].ravel()]
        out.append((g["n"], on[k], float(d[k]), len(faces), v.max(axis=0) - v.min(axis=0)))
    out.sort(key=lambda r: r[2])
    return out


# --- the authored surface: the solid itself ---

def solid_faces(step_path):
    """Every face of the solid at `step_path`."""
    import cadquery as cq
    return cq.importers.importStep(str(step_path)).val().Faces()


def solid_near(faces, point, radius):
    """The solid's faces within `radius` of `point`, nearest first.

    Each row is (kind, params, nearest point ON the face, distance). The vocabulary is the
    picker's own (`pick-format.js` formatFace), so a row here and a `faceA:` line off the
    viewer describe the same thing in the same words."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepBndLib import BRepBndLib
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.Bnd import Bnd_Box
    from OCP.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
    from OCP.gp import gp_Pnt

    probe = gp_Pnt(float(point[0]), float(point[1]), float(point[2]))
    vertex = BRepBuilderAPI_MakeVertex(probe).Vertex()

    out = []
    for f in faces:
        box = Bnd_Box()
        BRepBndLib.Add_s(f.wrapped, box, False)
        if box.IsVoid() or box.Distance(_point_box(point)) > radius:
            continue
        dss = BRepExtrema_DistShapeShape(vertex, f.wrapped)
        if not dss.IsDone() or dss.NbSolution() < 1:
            continue
        d = float(dss.Value())
        if d > radius:
            continue
        p = dss.PointOnShape2(1)
        on = np.array([p.X(), p.Y(), p.Z()])
        surf = BRepAdaptor_Surface(f.wrapped)
        kind = surf.GetType()
        if kind == GeomAbs_Plane:
            import cadquery as cq
            n = f.normalAt(cq.Vector(*on))
            out.append(("plane", f"n x={n.x:+.3f} y={n.y:+.3f} z={n.z:+.3f}", on, d))
        elif kind == GeomAbs_Cylinder:
            cyl = surf.Cylinder()
            axd = cyl.Position().Direction()
            out.append(("cylinder",
                        f"r={cyl.Radius():.3f} · dir x={axd.X():+.3f} y={axd.Y():+.3f}"
                        f" z={axd.Z():+.3f}", on, d))
        else:
            out.append(("curved", "", on, d))
    out.sort(key=lambda r: r[3])
    return out


def _point_box(point):
    """A degenerate Bnd_Box at `point`, for the cheap face prefilter."""
    from OCP.Bnd import Bnd_Box
    from OCP.gp import gp_Pnt
    b = Bnd_Box()
    b.Add(gp_Pnt(float(point[0]), float(point[1]), float(point[2])))
    return b


# --- reporting ---

def fmt_mesh(n, on, d, count, span):
    return (f"n x={n[0]:+.3f} y={n[1]:+.3f} z={n[2]:+.3f}"
            f" · thru x={on[0]:.3f} y={on[1]:.3f} z={on[2]:.3f} · d {d:.3f}"
            f" · {count} facets · span {span[0]:.3f} × {span[1]:.3f} × {span[2]:.3f}")


def fmt_solid(kind, params, on, d):
    head = f"{kind} · {params}" if params else kind
    return f"{head} · thru x={on[0]:.3f} y={on[1]:.3f} z={on[2]:.3f} · d {d:.3f}"


def where(held):
    """One line naming which surfaces hold the window — a location, never a verdict.

    `held` is {surface: nearest distance or None}."""
    have = [s for s in SURFACES if held.get(s) is not None]
    if not have:
        return "no surface within the window on any of the three"
    parts = " · ".join(f"{s} {held[s]:.3f}" for s in have)
    missing = [s for s in SURFACES if s not in have]
    if not missing:
        return f"all three hold surface here — {parts}"
    return f"{'/'.join(have)} only, not {'/'.join(missing)} — {parts}"


#: Said once, when a window stood in the payload and in neither the solid nor the print.
DRAWN_ONLY_NOTE = """
  A reading that stands in the drawn payload alone is the payload reporting geometry it could
  not draw. The payload is the print collapsed inside a deflection budget, and a budget is a
  distance bound — a feature shorter than it is erased and bridged with long triangles while
  the reading never leaves budget. That places the manifestation. It does not settle the cause,
  and it is not a finding that the click was noise: what a payload cannot draw at that scale is
  usually a feature the printer cannot lay down at that scale either. Go and find what the
  payload could not draw here.
"""


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pick", nargs="?", help="file holding pick text (default: stdin)")
    ap.add_argument("--radius", type=float, default=1.0, help="window radius in mm")
    ap.add_argument("--surfaces", default=",".join(SURFACES),
                    help="comma-separated subset of authored,printed,drawn")
    ap.add_argument("--rows", type=int, default=6,
                    help="how many of a surface's nearest rows to print (0 for all)")
    args = ap.parse_args(argv)

    if args.pick == "selftest":
        return selftest()

    text = Path(args.pick).read_text() if args.pick else sys.stdin.read()
    want = [s.strip() for s in args.surfaces.split(",") if s.strip()]
    paths = source(text)
    probes = points(text)
    if not probes:
        raise SystemExit("no coordinates in the pick")

    loaded, header = {}, []
    for s in SURFACES:
        p = paths.get(s)
        if s not in want or p is None:
            header.append(f"  {s:<9} —")
            continue
        if s == "authored":
            faces = solid_faces(p)
            loaded[s] = faces
            header.append(f"  {s:<9} {p.name}  {len(faces)} faces")
        else:
            m = load_mesh(p, s)
            if m is None:
                header.append(f"  {s:<9} {p.name}  unreadable")
                continue
            loaded[s] = m
            note = ""
            if s == "drawn":
                cut = _mesh_payload.read_cut(p)
                src = _mesh_payload.read_source(p)
                note = ("  · decimated %.3f of %.3f mm" % (cut["dev"], cut["bound"])
                        if cut else "  · decimation unstated")
                if src:
                    note += f" · src {str(src)[:8]}"
            header.append(f"  {s:<9} {p.name}  {len(m.faces)} facets{note}")

    print(f"{paths['authored'].stem} · window {args.radius:g} mm")
    print("\n".join(header))

    drawn_only = False
    for label, p in probes:
        print(f"\n  {label} x={p[0]:.3f} y={p[1]:.3f} z={p[2]:.3f}")
        held = {}
        for s in SURFACES:
            if s not in loaded:
                continue
            if s == "authored":
                rows = solid_near(loaded[s], p, args.radius)
                held[s] = rows[0][3] if rows else None
                shown = rows if args.rows <= 0 else rows[:args.rows]
                for r in shown:
                    print(f"    {s:<9} {fmt_solid(*r)}")
            else:
                rows = planes(loaded[s], p, args.radius)
                held[s] = rows[0][2] if rows else None
                shown = rows if args.rows <= 0 else rows[:args.rows]
                for r in shown:
                    print(f"    {s:<9} {fmt_mesh(*r)}")
            if not rows:
                print(f"    {s:<9} nothing in the window")
            elif len(shown) < len(rows):
                # A fluted field splits into a great many one-facet groups whose normals
                # sweep. They are the same surface said many times, and past the nearest few
                # they stop being a reading; the count keeps them from being a surprise.
                far = rows[-1][3 if s == "authored" else 2]
                print(f"    {' ':<9} … {len(rows) - len(shown)} more, out to d {far:.3f}")
        print(f"    {'where':<9} {where(held)}")
        if held.get("drawn") is not None and not any(
                held.get(s) is not None for s in ("authored", "printed")):
            drawn_only = True

    if drawn_only:
        print(DRAWN_ONLY_NOTE.rstrip())
    return 0


# --- selftest ----------------------------------------------------------------
#
# What is protected is that a reading names a PLACE and an ORDER. A plane reported by its
# offset along its own normal is a number that looks like a coordinate and is not one, and a
# window sorted by facet count buries the thing under the cursor beneath whatever is largest
# near it. Both are how a reader is told the wrong thing without being told anything false.

def selftest():
    def check(name, got, want):
        ok = got == want
        print(f"{'ok  ' if ok else 'FAIL'} {name}: {got!r}" + ("" if ok else f" != {want!r}"))
        return ok

    passed = True

    # A step: a big land at x=0 and a small pad standing 0.25 mm off it, which is the shape
    # the east bosses make and the shape a deflection budget cannot keep.
    land = trimesh.creation.box(extents=(1.0, 40.0, 40.0))
    land.apply_translation((-0.5, 0, 0))
    pad = trimesh.creation.box(extents=(0.25, 7.0, 7.0))
    pad.apply_translation((0.125, 0, 0))
    mesh = trimesh.util.concatenate([land, pad])

    probe = np.array([0.30, 0.0, 0.0])
    rows = planes(mesh, probe, 1.0)
    passed &= check("a window holds more than one plane", len(rows) > 1, True)

    # NEAREST FIRST. The pad's face at x=0.25 is 0.05 mm from the probe; the land's at x=0 is
    # 0.30. Facet count would have put the land first — it is the bigger box.
    passed &= check("nearest plane leads", round(rows[0][2], 3), 0.05)
    passed &= check("and it is the pad's face", round(float(rows[0][1][0]), 3), 0.25)
    passed &= check("distances ascend", [round(r[2], 3) for r in rows]
                    == sorted(round(r[2], 3) for r in rows), True)

    # THE POINT IS ON THE SURFACE, not a projection. A tilted plane through the origin has
    # offset 0 along its normal, which as a coordinate is nowhere near it.
    tilt = trimesh.creation.box(extents=(20.0, 20.0, 0.5))
    tilt.apply_transform(trimesh.transformations.rotation_matrix(np.radians(30), (1, 0, 0)))
    tilt.apply_translation((0, 50.0, 0))
    near = planes(tilt, np.array([0.0, 50.0, 1.0]), 2.0)
    passed &= check("a tilted face reports a point beside the probe",
                    bool(near) and abs(float(near[0][1][1]) - 50.0) < 2.0, True)

    # `where` states a location and names the surfaces, and never renders a verdict.
    line = where({"authored": None, "printed": None, "drawn": 0.004})
    passed &= check("drawn-only reads as drawn-only", line.startswith("drawn only, not"), True)
    passed &= check("and says nothing about noise", "noise" in line.lower(), False)
    passed &= check("all three reads as all three",
                    where({"authored": 0.1, "printed": 0.1, "drawn": 0.1}).startswith("all three"),
                    True)

    # A FILE LINE NAMING THE PAYLOAD RESOLVES TO THE SAME PIECE as one naming the solid, and
    # the readings the picker puts after the path are not part of the path. Held against a
    # file this makes, so the reading is of the rule and not of what the tree happens to hold.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        stem = Path(tmp) / "piece.step"
        stem.write_text("")
        a = source(f"file: {stem}\nclick: x=0 y=0 z=0")
        b = source(f"file: {stem}.mesh · decimated 0.221 of 0.226 mm · src 6c1cb0a5\n"
                   f"click: x=0 y=0 z=0")
        passed &= check("payload and solid file lines name one piece",
                        a["authored"] == b["authored"] == stem, True)
        passed &= check("a surface with no file beside it reads as absent",
                        (a["printed"], a["drawn"]), (None, None))

    print("PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
