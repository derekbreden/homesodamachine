"""Orthographic visible outlines from a fine closed triangle model.

Silhouette and sharp edges retain their mesh positions. Projected front triangles
clip the hidden intervals of each edge analytically; no image raster or nearest
surface search supplies a drawing line.
"""

import numpy as np
from rtree import index
from shapely.geometry import LineString


def _cross(a, b):
    return a[..., 0] * b[..., 1] - a[..., 1] * b[..., 0]


def visible_edges(vertices, triangles, normal, right, *, sharp_degrees=30.0, join_planes=()):
    """Visible 2D edge fragments, in model units; ``normal`` points to the viewer."""
    normal = np.asarray(normal, dtype=float)
    normal = normal / np.linalg.norm(normal)
    right = np.asarray(right, dtype=float)
    right = right - normal * np.dot(normal, right)
    right = right / np.linalg.norm(right)
    up = np.cross(normal, right)
    projected = np.asarray(vertices, dtype=float) @ np.array([right, up, normal]).T
    triangles = np.asarray(triangles, dtype=np.int64)
    corners = projected[triangles]
    face_normals = np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0])
    front = face_normals[:, 2] > 1e-12

    # A fine kernel model shares vertices at face boundaries. Every closed edge
    # has two incident triangles, even where their face records differ.
    edges = np.sort(np.concatenate([triangles[:, [0, 1]], triangles[:, [1, 2]],
                                    triangles[:, [2, 0]]]), axis=1)
    owners = np.tile(np.arange(len(triangles)), 3)
    order = np.lexsort((edges[:, 1], edges[:, 0]))
    edges, owners = edges[order], owners[order]
    starts = np.flatnonzero(np.r_[True, np.any(edges[1:] != edges[:-1], axis=1)])
    counts = np.diff(np.r_[starts, len(edges)])
    paired = starts[counts == 2]
    adjacent = np.column_stack([owners[paired], owners[paired + 1]])
    unit = face_normals / np.maximum(np.linalg.norm(face_normals, axis=1)[:, None], 1e-30)
    sharp = np.einsum('ij,ij->i', unit[adjacent[:, 0]], unit[adjacent[:, 1]]) < np.cos(np.radians(sharp_degrees))
    silhouette = front[adjacent[:, 0]] != front[adjacent[:, 1]]
    candidates = edges[paired[sharp | silhouette]]
    candidates = np.concatenate([candidates, edges[starts[counts == 1]]])
    # Separate closed solids can be tangent pieces of one continuous article.
    # An authored joining plane suppresses only their internal cap rims.
    world_edges = np.asarray(vertices)[candidates]
    keep = np.ones(len(candidates), dtype=bool)
    for origin, axis in join_planes:
        axis = np.asarray(axis, dtype=float)
        axis = axis / np.linalg.norm(axis)
        distances = np.einsum('ijk,k->ij', world_edges - origin, axis)
        keep &= ~np.all(np.abs(distances) < 1e-6, axis=1)
    candidates = candidates[keep]

    facing = corners[front]
    area = face_normals[front, 2]
    if not len(facing):
        return []
    bounds = np.column_stack([facing[:, :, :2].min(axis=1), facing[:, :, :2].max(axis=1)])
    tree = index.Index((i, box, None) for i, box in enumerate(bounds))
    coefficients = face_normals[front] / area[:, None]
    plane = np.einsum('ij,ij->i', coefficients, facing[:, 0])
    output = []
    for a, b in projected[candidates]:
        delta = b - a
        if np.linalg.norm(delta[:2]) < 1e-10:
            continue
        box = tuple(np.r_[np.minimum(a[:2], b[:2]), np.maximum(a[:2], b[:2])])
        nearby = np.fromiter(tree.intersection(box), dtype=np.int64)
        if not len(nearby):
            output.append([a[:2].tolist(), b[:2].tolist()])
            continue
        triangle = facing[nearby, :, :2]
        vectors = np.roll(triangle, -1, axis=1) - triangle
        alpha = _cross(vectors, a[:2] - triangle)
        beta = _cross(vectors, delta[:2])
        # A front triangle hides the part lying inside its three half-planes
        # and strictly behind its own interpolated surface depth.
        alpha = np.column_stack([alpha, plane[nearby] - coefficients[nearby, :2] @ a[:2] - a[2] - 1e-7])
        beta = np.column_stack([beta, -coefficients[nearby, :2] @ delta[:2] - delta[2]])
        parallel = np.abs(beta) < 1e-15
        valid = ~np.any(parallel & (alpha < -1e-12), axis=1)
        crossing = np.divide(-alpha, beta, out=np.zeros_like(alpha), where=~parallel)
        lo = np.maximum(0.0, np.max(np.where(beta > 1e-15, crossing, -np.inf), axis=1))
        hi = np.minimum(1.0, np.min(np.where(beta < -1e-15, crossing, np.inf), axis=1))
        intervals = sorted(zip(lo[valid & (hi > lo)], hi[valid & (hi > lo)]))
        begin = 0.0
        for low, high in intervals:
            if low > begin + 1e-10:
                output.append([(a[:2] + delta[:2] * begin).tolist(),
                               (a[:2] + delta[:2] * low).tolist()])
            begin = max(begin, high)
        if begin < 1.0 - 1e-10:
            output.append([(a[:2] + delta[:2] * begin).tolist(), b[:2].tolist()])
    tree.close()
    return output


def _paths(edges, simplify):
    """Join only shared endpoints; retain branches as separate drawing paths."""
    ends = {}
    for i, edge in enumerate(edges):
        for point in edge:
            ends.setdefault(tuple(round(x, 9) for x in point), []).append(i)
    used, paths = set(), []
    for first in range(len(edges)):
        if first in used:
            continue
        used.add(first)
        points = list(edges[first])
        for _ in range(2):
            while True:
                at = tuple(round(x, 9) for x in points[-1])
                incident = ends[at]
                if len(incident) != 2:
                    break
                next_edge = next((i for i in incident if i not in used), None)
                if next_edge is None:
                    break
                used.add(next_edge)
                edge = edges[next_edge]
                points.append(edge[1] if tuple(round(x, 9) for x in edge[0]) == at else edge[0])
            points.reverse()
        if simplify and len(points) > 2:
            points = list(LineString(points).simplify(simplify, preserve_topology=False).coords)
        paths.append(points)
    return paths


def model_outlines(path, normal, right, *, simplify=0.0025, join_planes=()):
    """Project every fine solid in a kernel model, retaining its f64 coordinates."""
    vertices, triangles = [], []
    offset = 0
    with np.load(path, allow_pickle=False) as model:
        for key in (key for key in model.files if key.startswith('V') and key[1:].isdigit()):
            v = model[key]
            t = model['T' + key[1:]].astype(np.int64)
            vertices.append(v)
            triangles.append(t + offset)
            offset += len(v)
    return _paths(visible_edges(np.concatenate(vertices), np.concatenate(triangles), normal, right,
                               join_planes=join_planes), simplify)
