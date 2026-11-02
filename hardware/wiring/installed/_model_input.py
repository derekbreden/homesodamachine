"""Installed-body measurements read from the enclosure's explicit fine model."""
from __future__ import annotations

from dataclasses import dataclass
import itertools
import json
import math
from pathlib import Path
import re

_SOLID_INDEX = re.compile(r"/\d+$")
QUERY_SOURCES: set[Path] = set()


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
        name: (Body(tuple(Solid(bound(s["min"]), bound(s["max"]), s["volume"])
                          for r in found for s in r.get('components',[r]))),
               next((r["color"] for r in found if r["color"] is not None), None))
        for name, found in grouped.items()
    }


def measurements(path, *, component_names=()):
    """Raw Rust fine summaries, shared by numeric consumers of one physical export."""
    import _assembly_model
    import hashlib

    # Separate spades and the compressor power cover remain meaningful even when
    # one logical archive entry holds their disconnected shells.
    hosts = ('compressor','valve-v-a','valve-v-b','vk-solenoid',
             *(f'coil-v-{letter}' for letter in 'cdefghij'))
    result = _assembly_model.measure([_assembly_model.instance(path)], (),
        component_names=sorted(set(component_names)|
            {name for host in hosts for name in (host,'cold-core/'+host)}))
    path=Path(path).resolve()
    with path.open('rb')as stream:digest=hashlib.file_digest(stream,'sha256').hexdigest()
    return {'path':str(path),'sha256':digest,'bodies':result['bodies']}


def read(path, *, reading=None):
    """Component bounds and volumes, measured by Rust on their fine f64 arrays."""
    from meshcad.rule import GRID

    if reading is None:reading=measurements(path)
    if Path(reading['path']).resolve()!=Path(path).resolve():
        raise ValueError('Physical measurements belong to another model')
    import hashlib
    with Path(path).open('rb')as stream:
        digest=hashlib.file_digest(stream,'sha256').hexdigest()
    if digest!=reading['sha256']:
        raise ValueError('Physical model changed after its measurements')
    # Attachments use the model reader's coordinate grid. Snapping the extrema
    # gives the bounds of those snapped vertices without rebuilding the mesh.
    return bodies(reading['bodies'], grid=GRID)


def reference_bounds(path, rotation):
    """Bounds of a source reference in the requested orientation, without shapes.

    Frozen references carry source-bound scalar queries beside their assets. The
    display's YZ support points preserve its bounds at any source X tilt. Authored
    references are measured from their current fine producer output.
    """
    path = Path(path)
    queries = path.with_name('native-queries.json')
    if queries.is_file():
        row = json.loads(queries.read_text())['references'][path.name]
        manifest = path.with_name('frozen-asset.json')
        identity = json.loads(manifest.read_text())
        QUERY_SOURCES.update((queries.resolve(),manifest.resolve()))
        if identity['members'][path.name] != row['step_sha256']:
            raise ValueError(f'{path}: reference bounds name a different frozen asset')
        lo,hi = row['bounds_mm']
        if 'yz_support_mm' in row:
            if any(abs(rotation[i][j]-(1. if i==j==0 else 0.)) > 1e-12
                   for i,j in ((0,0),(0,1),(0,2),(1,0),(2,0))):
                raise ValueError(f'{path}: reference supports X-axis turns')
            points = ((x,y,z) for x in (lo[0],hi[0]) for y,z in row['yz_support_mm'])
        else:
            if (any(abs(sum(abs(v) for v in axis)-1.) > 1e-12 for axis in rotation)
                    or any(min(abs(v),abs(abs(v)-1.)) > 1e-12
                           for axis in rotation for v in axis)):
                raise ValueError(f'{path}: reference supports axis-aligned turns')
            points = itertools.product(*zip(lo,hi))
        carried = [tuple(sum(axis[j]*point[j] for j in range(3)) for axis in rotation)
                   for point in points]
        return (tuple(min(p[i] for p in carried) for i in range(3)),
                tuple(max(p[i] for p in carried) for i in range(3)))
    import _assembly_model
    result = _assembly_model.measure([
        _assembly_model.instance(Path(str(path)+'.npz'),
            transform=[[*axis,0.] for axis in rotation])], ())
    return (tuple(min(row['min'][i] for row in result['bodies']) for i in range(3)),
            tuple(max(row['max'][i] for row in result['bodies']) for i in range(3)))
