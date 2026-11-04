"""Enclosure numbers and frames for the Rust producers.

The enclosure's scalar source uses vectors, planes and placements. These are numeric
values here; every solid operation is an explicit Rust construction recipe. The normal
driver loads this namespace before the source, without loading a Python CAD kernel.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = '_enclosure_datums'

class Vector:
    def __init__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__init__',), args=(self, *args), kwargs=kwargs)
    def toTuple(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.toTuple',), args=(self, *args), kwargs=kwargs)
    def __iter__(self, *args, **kwargs):
        return iter(_compiled('_enclosure_datums', path=('Vector.__iter__',), args=(self, *args), kwargs=kwargs))
    def __getitem__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__getitem__',), args=(self, *args), kwargs=kwargs)
    def __add__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__add__',), args=(self, *args), kwargs=kwargs)
    def __sub__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__sub__',), args=(self, *args), kwargs=kwargs)
    def __mul__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__mul__',), args=(self, *args), kwargs=kwargs)
    __rmul__ = __mul__
    def __truediv__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__truediv__',), args=(self, *args), kwargs=kwargs)
    def __neg__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__neg__',), args=(self, *args), kwargs=kwargs)
    add, sub, multiply = (__add__, __sub__, __mul__)
    @property
    def Length(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.Length',), args=(self, *args), kwargs=kwargs)
    def normalized(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.normalized',), args=(self, *args), kwargs=kwargs)
    def dot(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.dot',), args=(self, *args), kwargs=kwargs)
    def cross(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.cross',), args=(self, *args), kwargs=kwargs)
    def getAngle(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.getAngle',), args=(self, *args), kwargs=kwargs)
    def __repr__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Vector.__repr__',), args=(self, *args), kwargs=kwargs)

class Plane:
    def __init__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Plane.__init__',), args=(self, *args), kwargs=kwargs)
    @classmethod
    def named(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Plane.named',), args=(self, *args), kwargs=kwargs)
    def toWorldCoords(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Plane.toWorldCoords',), args=(self, *args), kwargs=kwargs)
    def toLocalCoords(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Plane.toLocalCoords',), args=(self, *args), kwargs=kwargs)
    @property
    def location(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Plane.location',), args=(self, *args), kwargs=kwargs)

class _Matrix:
    def __init__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('_Matrix.__init__',), args=(self, *args), kwargs=kwargs)
    def Transformation(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('_Matrix.Transformation',), args=(self, *args), kwargs=kwargs)
    def Value(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('_Matrix.Value',), args=(self, *args), kwargs=kwargs)

class Location:
    def __init__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Location.__init__',), args=(self, *args), kwargs=kwargs)
    def __mul__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Location.__mul__',), args=(self, *args), kwargs=kwargs)
    @property
    def inverse(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Location.inverse',), args=(self, *args), kwargs=kwargs)

class Workplane:
    def __init__(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Workplane.__init__',), args=(self, *args), kwargs=kwargs)
    def val(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Workplane.val',), args=(self, *args), kwargs=kwargs)
    def vals(self, *args, **kwargs):
        return _compiled('_enclosure_datums', path=('Workplane.vals',), args=(self, *args), kwargs=kwargs)
    def __getattr__(self, *args, **kwargs):
        try:
            return _compiled('_enclosure_datums', path=('Workplane.__getattr__',), args=(self, *args), kwargs=kwargs)
        except ValueError as error:
            raise AttributeError(args[0]) from error

class Shape:
    pass

def __getattr__(name):
    if name == "__all__":
        return _compiled('_enclosure_datums', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('_enclosure_datums', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('_enclosure_datums', action="main")
