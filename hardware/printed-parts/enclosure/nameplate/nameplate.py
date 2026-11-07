"""The nameplate's recipe as its print preparation, the trial preparers and the old enclosure
pipeline's rear tiles import it. The plate itself is cut by `nameplate.rs`.

The origin is the back of the rigid plate; +Y points out of the enclosure, +Z up,
and text reads along -X from outside.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'nameplate'

from fontTools.pens.basePen import BasePen

class _OutlinePen(BasePen):
    def __init__(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen.__init__',), args=(self, *args), kwargs=kwargs)
    def point(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen.point',), args=(self, *args), kwargs=kwargs)
    def _moveTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen._moveTo',), args=(self, *args), kwargs=kwargs)
    def _lineTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen._lineTo',), args=(self, *args), kwargs=kwargs)
    def _curveToOne(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen._curveToOne',), args=(self, *args), kwargs=kwargs)
    def _qCurveToOne(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen._qCurveToOne',), args=(self, *args), kwargs=kwargs)
    def _closePath(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen._closePath',), args=(self, *args), kwargs=kwargs)
    def _endPath(self, *args, **kwargs):
        return _compiled('nameplate', path=('_OutlinePen._endPath',), args=(self, *args), kwargs=kwargs)

class _FaucetPen:
    def moveTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_FaucetPen.moveTo',), args=(self, *args), kwargs=kwargs)
    def lineTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_FaucetPen.lineTo',), args=(self, *args), kwargs=kwargs)
    def arcTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_FaucetPen.arcTo',), args=(self, *args), kwargs=kwargs)
    def closePath(self, *args, **kwargs):
        return _compiled('nameplate', path=('_FaucetPen.closePath',), args=(self, *args), kwargs=kwargs)
    def endPath(self, *args, **kwargs):
        return _compiled('nameplate', path=('_FaucetPen.endPath',), args=(self, *args), kwargs=kwargs)

class _NumbersPen(BasePen):
    def __init__(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen.__init__',), args=(self, *args), kwargs=kwargs)
    def _moveTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen._moveTo',), args=(self, *args), kwargs=kwargs)
    def _lineTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen._lineTo',), args=(self, *args), kwargs=kwargs)
    def _curveToOne(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen._curveToOne',), args=(self, *args), kwargs=kwargs)
    def _qCurveToOne(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen._qCurveToOne',), args=(self, *args), kwargs=kwargs)
    def arcTo(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen.arcTo',), args=(self, *args), kwargs=kwargs)
    def _closePath(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen._closePath',), args=(self, *args), kwargs=kwargs)
    def _endPath(self, *args, **kwargs):
        return _compiled('nameplate', path=('_NumbersPen._endPath',), args=(self, *args), kwargs=kwargs)

def __getattr__(name):
    if name == "__all__":
        return _compiled('nameplate', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('nameplate', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])
