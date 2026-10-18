"""Mesh reading for print preparation: numpy and shapely, no CAD kernel.

Every geometry-dependent value of a trial preparation is read here from the STL
it is pointed at. The STL is cut from the piece's STEP; face extents read here
match the STEP faces to within the export tolerance.
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

import numpy as np

CHAMFER_NZ = -1.0 / math.sqrt(5.0)   # cadlib/overhang_round.py: 0.5 outward per mm of rise


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def read_stl(path: Path) -> np.ndarray:
    """Triangles (N, 3, 3) in millimetres, float32, from a binary or ASCII STL."""
    data = Path(path).read_bytes()
    if len(data) >= 84:
        count = int(np.frombuffer(data[80:84], "<u4")[0])
        if 84 + 50 * count == len(data):
            record = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
            return np.ascontiguousarray(np.frombuffer(data, record, count, 84)["v"])
    # ASCII: each "vertex" keyword is followed by its three coordinates.
    words = data.decode("ascii", "replace").split()
    values = [float(v) for i, w in enumerate(words) if w == "vertex" for v in words[i + 1:i + 4]]
    return np.array(values, dtype=np.float32).reshape(-1, 3, 3)


def merge(triangles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Shared vertices (float64) and face indices: STL corners that are the same float32 point."""
    flat = np.ascontiguousarray(triangles.reshape(-1, 3), dtype=np.float32) + np.float32(0.0)  # -0.0 is 0.0
    keys = flat.view(np.dtype((np.void, 12))).ravel()
    _, first, inverse = np.unique(keys, return_index=True, return_inverse=True)
    return flat[first].astype(np.float64), inverse.reshape(-1, 3).astype(np.int64)


def closed_check(faces: np.ndarray) -> dict:
    """Edge-manifold, consistently oriented and single-bodied, read from the faces alone."""
    start = np.concatenate([faces[:, 0], faces[:, 1], faces[:, 2]])
    end = np.concatenate([faces[:, 1], faces[:, 2], faces[:, 0]])
    span = int(faces.max()) + 1
    key = np.minimum(start, end) * span + np.maximum(start, end)
    _, edge_index, counts = np.unique(key, return_inverse=True, return_counts=True)
    del key
    balance = np.bincount(edge_index, weights=np.where(start < end, 1, -1), minlength=len(counts))
    bodies = len(set(component_labels(faces).tolist()))
    return {"edges": int(len(counts)), "boundary_edges": int(np.sum(counts == 1)),
            "nonmanifold_edges": int(np.sum(counts > 2)),
            "inconsistent_edges": int(np.sum((counts == 2) & (balance != 0))),
            "bodies": bodies,
            "closed_oriented_single_body": bool(np.all(counts == 2) and np.all(balance == 0)
                                                and bodies == 1)}


def component_labels(faces: np.ndarray) -> np.ndarray:
    """Label each face with its vertex-connected component."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    used, inverse = np.unique(faces.ravel(), return_inverse=True)
    n, m = len(faces), len(used)
    rows = np.repeat(np.arange(n), 3)
    graph = coo_matrix((np.ones(3 * n, dtype=np.int8), (rows, inverse + n)), shape=(n + m, n + m))
    _, labels = connected_components(graph, directed=False)
    return labels[:n]


def normals_areas(triangles: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    cross = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    length = np.linalg.norm(cross, axis=1)
    return cross / np.maximum(length, 1e-30)[:, None], length / 2.0


def rotation(spec) -> np.ndarray:
    """A 3x3 rotation from a declared pose: a matrix, or ordered axis turns in degrees."""
    if spec is None:
        return np.eye(3)
    if "matrix" in spec:
        matrix = np.array(spec["matrix"], dtype=float)
    else:
        matrix = np.eye(3)
        for axis, degrees in spec.get("turns", []):
            c, s = math.cos(math.radians(degrees)), math.sin(math.radians(degrees))
            turn = {"x": [[1, 0, 0], [0, c, -s], [0, s, c]],
                    "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]],
                    "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]
            matrix = np.array(turn) @ matrix
    matrix[np.abs(matrix) < 1e-12] = 0.0
    if not np.allclose(matrix @ matrix.T, np.eye(3), atol=1e-9) or np.linalg.det(matrix) < 0:
        raise ValueError(f"pose is not a proper rotation: {spec}")
    return matrix


def section_segments(triangles: np.ndarray, z: float) -> np.ndarray:
    """Segments (K, 2, 2) where the horizontal plane z cuts the surface."""
    d = triangles[:, :, 2] - z
    crossing = (d.min(axis=1) < 0) & (d.max(axis=1) > 0)
    t, dd = triangles[crossing], d[crossing]
    points = []
    for i, j in ((0, 1), (1, 2), (2, 0)):
        cut = dd[:, i] * dd[:, j] < 0
        u = np.zeros(len(t))
        u[cut] = dd[cut, i] / (dd[cut, i] - dd[cut, j])
        p = t[:, i] + (t[:, j] - t[:, i]) * u[:, None]
        points.append(np.where(cut[:, None], p, np.nan))
    stacked = np.stack(points, axis=1)[:, :, :2]
    out = []
    for row in stacked:
        good = row[~np.isnan(row[:, 0])]
        if len(good) == 2:
            out.append(good)
    return np.array(out).reshape(-1, 2, 2)


def section_polygons(triangles: np.ndarray, z: float):
    """The solid's cross-section at z as shapely geometry, holes included (even-odd)."""
    from shapely.geometry import LineString
    from shapely.ops import polygonize, unary_union
    segments = np.round(section_segments(triangles, z), 6)
    if not len(segments):
        from shapely.geometry import Polygon
        return Polygon()
    a, b = segments[:, 0], segments[:, 1]
    inside = []
    for polygon in polygonize(unary_union([LineString(s) for s in segments])):
        point = polygon.representative_point()
        crossing = (a[:, 1] > point.y) != (b[:, 1] > point.y)
        st, en = a[crossing], b[crossing]
        x = st[:, 0] + (point.y - st[:, 1]) * (en[:, 0] - st[:, 0]) / (en[:, 1] - st[:, 1])
        if np.count_nonzero(x > point.x) % 2:
            inside.append(polygon)
    return unary_union(inside)


def box_mesh(low, high) -> tuple[np.ndarray, np.ndarray]:
    """An axis-aligned box as vertices and outward-wound faces."""
    (x0, y0, z0), (x1, y1, z1) = low, high
    vertices = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                         [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], dtype=float)
    faces = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4],
                      [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    return vertices, faces


def subtract_boxes(low, high, holes) -> list[tuple[list[float], list[float]]]:
    """Axis-aligned box minus axis-aligned boxes, as disjoint boxes."""
    pieces = [(np.array(low, float), np.array(high, float))]
    for hole_low, hole_high in holes:
        hole_low, hole_high = np.array(hole_low, float), np.array(hole_high, float)
        remaining = []
        for lo, hi in pieces:
            if np.any(hole_high <= lo) or np.any(hole_low >= hi):
                remaining.append((lo, hi))
                continue
            lo, hi = lo.copy(), hi.copy()
            for axis in range(3):
                if hole_low[axis] > lo[axis]:
                    cut_hi = hi.copy(); cut_hi[axis] = hole_low[axis]
                    remaining.append((lo.copy(), cut_hi))
                    lo[axis] = hole_low[axis]
                if hole_high[axis] < hi[axis]:
                    cut_lo = lo.copy(); cut_lo[axis] = hole_high[axis]
                    remaining.append((cut_lo, hi.copy()))
                    hi[axis] = hole_high[axis]
        pieces = remaining
    return [(lo.tolist(), hi.tolist()) for lo, hi in pieces if np.all(hi - lo > 1e-6)]
