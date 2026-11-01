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
