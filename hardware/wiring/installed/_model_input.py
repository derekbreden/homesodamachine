"""Installed-body measurements read from the enclosure's explicit fine model."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re

_SOLID_INDEX = re.compile(r"/\d+$")


@dataclass(frozen=True)
class Solid:
    lower: tuple[float, float, float]
    upper: tuple[float, float, float]
    volume_mm3: float


@dataclass(frozen=True)
class Body:
    solids: tuple[Solid, ...]

    @property
    def lower(self):
        return tuple(min(s.lower[i] for s in self.solids) for i in range(3))

    @property
    def upper(self):
        return tuple(max(s.upper[i] for s in self.solids) for i in range(3))


def components(vertices, triangles):
    """Solid measurements from immutable fine triangles, independent of display pairing.

    One logical model entry can contain several disconnected solids. Keep each
    positive shell and the voids it contains, as the native solid reader does.
    The arrays retain their coordinates, indices and records unchanged.
    """
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    v = np.asarray(vertices, dtype=np.float64)
    t = np.asarray(triangles, dtype=np.int64).reshape(-1, 3)
    if not len(t):
        return ()
    edges = np.concatenate((t[:, :2], t[:, 1:]))
    count, labels = connected_components(coo_matrix(
        (np.ones(len(edges), dtype=np.uint8), (edges[:, 0], edges[:, 1])),
        shape=(len(v), len(v))), directed=False)
    a, b, c = (v[t[:, k]] - v[0] for k in range(3))
    volumes = np.bincount(labels[t[:, 0]],
                          np.einsum('ij,ij->i', a, np.cross(b, c)) / 6., count)
    lower = np.full((count, 3), np.inf)
    upper = np.full((count, 3), -np.inf)
    np.minimum.at(lower, labels, v)
    np.maximum.at(upper, labels, v)
    positive = np.flatnonzero(volumes > 0.)
    sizes = np.prod(upper[positive] - lower[positive], axis=1)
    for void in np.flatnonzero(volumes < 0.):
        around = np.flatnonzero(np.all(lower[positive] <= lower[void], axis=1)
                                & np.all(upper[positive] >= upper[void], axis=1))
        if len(around):
            volumes[positive[around[np.argmin(sizes[around])]]] += volumes[void]
    return tuple(Solid(tuple(lower[i]), tuple(upper[i]), float(volumes[i]))
                 for i in positive)


def bodies(rows, *, grid=None):
    """Group the writer's per-solid suffixes under the installed component names."""
    def bound(values):
        if grid is None:
            return tuple(values)
        return tuple(math.copysign(round(abs(v) / grid) * grid, v) for v in values)

    grouped = {}
    for row in rows:
        name = _SOLID_INDEX.sub("", row["name"])
        grouped.setdefault(name, []).append(row)
    return {
        name: (Body(tuple(Solid(bound(r["min"]), bound(r["max"]), r["volume"])
                          for r in found)),
               next((r["color"] for r in found if r["color"] is not None), None))
        for name, found in grouped.items()
    }


def read(path):
    """Component bounds and volumes, measured by Rust on their fine f64 arrays."""
    import _assembly_model
    from meshcad.rule import GRID

    result = _assembly_model.measure([_assembly_model.instance(path)], ())
    # Attachments use the model reader's coordinate grid. Snapping the extrema
    # gives the bounds of those snapped vertices without rebuilding the mesh.
    return bodies(result["bodies"], grid=GRID)
