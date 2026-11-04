"""Enclosure-private numeric construction for the structural back-bottom panel.

The native seam helpers keep ownership of their stations. This module records their
simple solid operations; Rust builds the solids and releases each intermediate after
its last use. Native builders and their cached geometry remain available to callers.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = '_enclosure_panel'

class _Shape:
    def __init__(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.__init__',), args=(self, *args), kwargs=kwargs)
    def _boolean(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape._boolean',), args=(self, *args), kwargs=kwargs)
    def fuse(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.fuse',), args=(self, *args), kwargs=kwargs)
    def cut(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.cut',), args=(self, *args), kwargs=kwargs)
    def intersect(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.intersect',), args=(self, *args), kwargs=kwargs)
    def translate(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.translate',), args=(self, *args), kwargs=kwargs)
    def rotate(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.rotate',), args=(self, *args), kwargs=kwargs)
    def mirror(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.mirror',), args=(self, *args), kwargs=kwargs)
    def clean(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.clean',), args=(self, *args), kwargs=kwargs)
    def val(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.val',), args=(self, *args), kwargs=kwargs)
    def BoundingBox(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.BoundingBox',), args=(self, *args), kwargs=kwargs)
    def Solids(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Shape.Solids',), args=(self, *args), kwargs=kwargs)

class _Graph:
    def __init__(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Graph.__init__',), args=(self, *args), kwargs=kwargs)
    def add(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Graph.add',), args=(self, *args), kwargs=kwargs)
    def box(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Graph.box',), args=(self, *args), kwargs=kwargs)
    def cylinder(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Graph.cylinder',), args=(self, *args), kwargs=kwargs)
    def prism(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Graph.prism',), args=(self, *args), kwargs=kwargs)
    def rounded(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Graph.rounded',), args=(self, *args), kwargs=kwargs)
    def document(self, *args, **kwargs):
        return _compiled('_enclosure_panel', path=('_Graph.document',), args=(self, *args), kwargs=kwargs)

def __getattr__(name):
    if name == "__all__":
        return _compiled('_enclosure_panel', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('_enclosure_panel', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])

if __name__ == "__main__":
    _compiled('_enclosure_panel', action="main")
