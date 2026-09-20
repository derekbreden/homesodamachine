#!/usr/bin/env python3
"""Compare local fore/aft bending sections of the printed tee-carrier mesh.

Run with tools/cad-venv/bin/python. The default baseline is the committed carrier
before the springs moved into its grips. This reads meshes, not nominal boxes;
it does not establish whole-part rigidity, joint slip or printed material strength.
"""

import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess

import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union
import trimesh


ROOT = Path(__file__).resolve().parents[2]
PART = "hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-right.stl"
BASELINE = "583b5e2a32ed9c6b7a546e954510b3aa0a5cd71f"
SECTIONS = (
    (20.07, "inner tee centre"),
    (28.57, "inner tie slot"),
    (40.0, "inner web and shelf"),
    (49.945, "previous spring station"),
    (60.0, "outer web"),
    (71.32, "outer tie slot"),
    (79.82, "outer tee centre"),
    (90.0, "web beside grip"),
    (92.0, "grip root"),
)


def section_moment(mesh, x):
    """Integrate area, first moment and Izz over nested Y/Z boundary loops."""
    segments = trimesh.intersections.mesh_plane(
        mesh, plane_origin=[x, 0, 0], plane_normal=[1, 0, 0]
    )
    if not len(segments):
        raise ValueError(f"No section at X={x:g}")
    # Join shared tessellation endpoints; 1e-7 mm is below STL float precision.
    lines = [LineString(np.round(line[:, 1:3], 7)) for line in segments]
    loops = [Polygon(poly.exterior) for poly in polygonize(unary_union(lines))]
    total = np.zeros(3)
    for index, poly in enumerate(loops):
        point = poly.representative_point()
        depth = sum(
            other.contains(point) and other.area > poly.area
            for j, other in enumerate(loops) if j != index
        )
        boundary = np.asarray(poly.exterior.coords)
        y, z = boundary[:-1].T
        yn, zn = boundary[1:].T
        cross = y * zn - yn * z
        area = cross.sum() / 2
        first = ((y + yn) * cross).sum() / 6
        second = ((y * y + y * yn + yn * yn) * cross).sum() / 12
        # Polygon orientation is independent of whether a nested loop is a void.
        total += np.sign(area) * (-1 if depth % 2 else 1) * np.array(
            [area, first, second]
        )
    area, first, second = total
    if area <= 0:
        raise ValueError(f"Invalid closed section at X={x:g}: area={area}")
    return {
        "area_mm2": float(area),
        "centroid_y_mm": float(first / area),
        "Izz_mm4": float(second - first * first / area),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", default=BASELINE)
    parser.add_argument("--current", type=Path, default=ROOT / PART)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    baseline = subprocess.check_output(
        ["git", "rev-parse", args.baseline], cwd=ROOT, text=True
    ).strip()
    before = subprocess.check_output(["git", "show", f"{baseline}:{PART}"], cwd=ROOT)
    current = args.current.read_bytes()
    meshes = {
        "before_spring_move": trimesh.load(io.BytesIO(before), file_type="stl"),
        "current": trimesh.load(io.BytesIO(current), file_type="stl"),
    }
    rows = []
    for x, label in SECTIONS:
        values = {name: section_moment(mesh, x) for name, mesh in meshes.items()}
        rows.append({
            "x_mm": x, "section": label, **values,
            "Izz_ratio": values["current"]["Izz_mm4"] / values["before_spring_move"]["Izz_mm4"],
        })
    result = {
        "baseline_commit": baseline,
        "current_path": str(args.current.resolve()),
        "before_spring_move_mesh_sha256": hashlib.sha256(before).hexdigest(),
        "current_mesh_sha256": hashlib.sha256(current).hexdigest(),
        "method": "Native printed STL sections normal to X; centroidal Izz at equal modulus. Does not model whole-carrier compliance, joint slip, anisotropy or infill.",
        "sections": rows,
    }
    content = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(content)
    else:
        print(content, end="")


if __name__ == "__main__":
    main()
