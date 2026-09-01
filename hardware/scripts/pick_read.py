"""Pick reader — what the printed mesh holds where Derek clicked.

`pick_text.py` composes pick text from CadQuery geometry, pointing a person at an
edge. This is the other direction: pick text pasted back in, answered from the STL
beside the `.step` the `file:` line names. The STL is the tessellated geometry the
slicer reads, so a feature present here is a feature in the print.

Every point the pick carries is probed — the click, both edge endpoints, and any
`thru`/`near` face point — and each answer is the set of distinct planes the mesh
holds inside the window, by normal and offset, with the facet count on each.

    tools/cad-venv/bin/python hardware/scripts/pick_read.py <<'EOF'
    file: hardware/printed-parts/enclosure/enclosure/enclosure-front-bottom.step
    click: x=-98.391 y=54.300 z=159.800
    EOF

    tools/cad-venv/bin/python hardware/scripts/pick_read.py pick.txt --radius 2.0

`--radius` sets the window (default 1.0 mm).
"""

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import trimesh

_PT = re.compile(r"x=(-?[\d.]+)\s+y=(-?[\d.]+)\s+z=(-?[\d.]+)")
#: Normals within this many degrees of each other are one plane.
_NORMAL_DEG = 5.0
#: Offsets within this distance along a shared normal are one plane.
_OFFSET_MM = 0.02


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
    """The mesh path the `file:` line names, and the `.step` beside it."""
    for line in text.splitlines():
        if line.strip().startswith("file:"):
            named = Path(line.split(":", 1)[1].strip())
            break
    else:
        raise SystemExit("no file: line in the pick")
    root = Path(__file__).resolve().parent.parent.parent
    step = named if named.is_absolute() else root / named
    if not step.exists():
        raise SystemExit(f"{step} is not in the tree")
    return step


def planes(mesh, point, radius):
    """The distinct planes `mesh` holds within `radius` of `point`.

    Returns (normal, offset, facet count, span) per plane, densest first. `span` is the
    window-local extent of the plane's vertices, which separates a full face from a sliver.
    """
    # A facet reaches the window when its own extent does. One long triangle spanning a
    # whole land has its centre far from any click on it, so centres do not select.
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
        v = mesh.vertices[mesh.faces[g["f"]].ravel()]
        out.append((g["n"], float(g["o"]), len(g["f"]), v.max(axis=0) - v.min(axis=0)))
    out.sort(key=lambda r: -r[2])
    return out


def fmt(n, o, count, span):
    return (f"    n x={n[0]:+.3f} y={n[1]:+.3f} z={n[2]:+.3f} · thru {o:+.4f}"
            f" · {count} facets · span {span[0]:.3f} × {span[1]:.3f} × {span[2]:.3f}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pick", nargs="?", help="file holding pick text (default: stdin)")
    ap.add_argument("--radius", type=float, default=1.0, help="window radius in mm")
    args = ap.parse_args(argv)

    text = Path(args.pick).read_text() if args.pick else sys.stdin.read()
    step = source(text)
    probes = points(text)
    if not probes:
        raise SystemExit("no coordinates in the pick")

    stl = step.with_suffix(".stl")
    if not stl.exists():
        raise SystemExit(f"no STL beside {step.name}")
    mesh = trimesh.load(stl, process=False)
    print(f"{stl.name} · {len(mesh.faces)} printed facets · window {args.radius:g} mm")

    for label, p in probes:
        print(f"\n  {label} x={p[0]:.3f} y={p[1]:.3f} z={p[2]:.3f}")
        got = planes(mesh, p, args.radius)
        if not got:
            print("    no surface in the window")
        for row in got:
            print(fmt(*row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
