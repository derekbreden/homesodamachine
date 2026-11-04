"""Typed fine-model measurements read and grouped in Rust."""
from dataclasses import dataclass
from pathlib import Path
from ._wiring_data import read as _read

QUERY_SOURCES = set()


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
        return tuple(_read("terminal_bounds", {"body": self})[0])

    @property
    def upper(self):
        return tuple(_read("terminal_bounds", {"body": self})[1])


def _solid(row):
    return Solid(tuple(row["lower"]), tuple(row["upper"]), row["volume_mm3"])


def _bodies(rows):
    return {name: (Body(tuple(_solid(solid) for solid in body["solids"])), color)
            for name, (body, color) in rows.items()}


def components(vertices, triangles):
    return tuple(_solid(row) for row in _read("model_components", {"vertices": vertices, "triangles": triangles}))


def bodies(rows, *, grid=None):
    return _bodies(_read("model_bodies", {"rows": rows, "grid": grid}))


def measurements(path, *, component_names=()):
    return _read("model_measurements", {"path": str(Path(path).resolve()), "component_names": component_names})


def read(path, *, reading=None):
    return _bodies(_read("model_read", {"path": str(Path(path).resolve()), "reading": reading}))


def reference_bounds(path, rotation):
    result = _read("model_reference_bounds", {"path": str(Path(path).resolve()), "rotation": rotation})
    QUERY_SOURCES.update(Path(path) for path in result["query_sources"])
    return tuple(tuple(row) for row in result["bounds"])
