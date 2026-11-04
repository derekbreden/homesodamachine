"""Enclosure fit/readings on fine model references, without Python CAD objects.

The enclosure's scalar station functions supply numeric tool recipes. Rust owns
their geometry and all model, volume, face and connected-component readings. The
existing report functions consume those readings, keeping their labels, units,
limits and document variables in one place with the mechanical dimensions.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = '_rust_enclosure_checks'

from _enclosure_panel import _Shape, _Graph

class _Vector:
    def __init__(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Vector.__init__',), args=(self, *args), kwargs=kwargs)
    def __iter__(self, *args, **kwargs):
        return iter(_compiled('_rust_enclosure_checks', path=('_Vector.__iter__',), args=(self, *args), kwargs=kwargs))
    def __getitem__(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Vector.__getitem__',), args=(self, *args), kwargs=kwargs)
    def __add__(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Vector.__add__',), args=(self, *args), kwargs=kwargs)
    def __sub__(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Vector.__sub__',), args=(self, *args), kwargs=kwargs)
    def dot(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Vector.dot',), args=(self, *args), kwargs=kwargs)
    @property
    def Length(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Vector.Length',), args=(self, *args), kwargs=kwargs)

class _ScalarFace:
    def __init__(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarFace.__init__',), args=(self, *args), kwargs=kwargs)
    def Area(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarFace.Area',), args=(self, *args), kwargs=kwargs)
    def Center(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarFace.Center',), args=(self, *args), kwargs=kwargs)
    def normalAt(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarFace.normalAt',), args=(self, *args), kwargs=kwargs)
    def BoundingBox(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarFace.BoundingBox',), args=(self, *args), kwargs=kwargs)
    def geomType(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarFace.geomType',), args=(self, *args), kwargs=kwargs)

class _ScalarComponent:
    def __init__(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarComponent.__init__',), args=(self, *args), kwargs=kwargs)
    def BoundingBox(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarComponent.BoundingBox',), args=(self, *args), kwargs=kwargs)
    def Volume(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ScalarComponent.Volume',), args=(self, *args), kwargs=kwargs)

class _ReadingShape(_Shape):
    def translate(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ReadingShape.translate',), args=(self, *args), kwargs=kwargs)
    def Volume(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ReadingShape.Volume',), args=(self, *args), kwargs=kwargs)
    def BoundingBox(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ReadingShape.BoundingBox',), args=(self, *args), kwargs=kwargs)
    def Solids(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ReadingShape.Solids',), args=(self, *args), kwargs=kwargs)
    def isValid(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ReadingShape.isValid',), args=(self, *args), kwargs=kwargs)
    def Faces(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_ReadingShape.Faces',), args=(self, *args), kwargs=kwargs)

class _Questions(_Graph):
    def __init__(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Questions.__init__',), args=(self, *args), kwargs=kwargs)
    def add(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Questions.add',), args=(self, *args), kwargs=kwargs)
    def model(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Questions.model',), args=(self, *args), kwargs=kwargs)
    def identity(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Questions.identity',), args=(self, *args), kwargs=kwargs)
    def reading(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Questions.reading',), args=(self, *args), kwargs=kwargs)
    def document(self, *args, **kwargs):
        return _compiled('_rust_enclosure_checks', path=('_Questions.document',), args=(self, *args), kwargs=kwargs)

def __getattr__(name):
    if name == "__all__":
        return _compiled('_rust_enclosure_checks', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('_rust_enclosure_checks', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('_rust_enclosure_checks', action="main")
