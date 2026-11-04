"""Typed compatibility surface for the machine's compiled Rust recipes."""
from __future__ import annotations
from pathlib import Path
import sys
_source = Path(__file__).resolve()
_hardware = next(parent for parent in _source.parents if parent.name == "hardware")
sys.path.insert(0, str(_hardware / "scripts"))
import dataclasses
from dataclasses import dataclass
from collections.abc import Mapping
from typing import NamedTuple
from _machine_data import Module as _RustModule, Surface as _RustSurface
_compiled = _RustModule('_stated_bounds')

class StatedBound:
    def __init__(*args, **kwargs):
        return _compiled.call('StatedBound.__init__', *args, **kwargs)
    def __call__(*args, **kwargs):
        return _compiled.call('StatedBound.__call__', *args, **kwargs)
    @property
    def ok(*args, **kwargs):
        return _compiled.call('StatedBound.ok', *args, **kwargs)
    @property
    def value(*args, **kwargs):
        return _compiled.call('StatedBound.value', *args, **kwargs)
    def record(*args, **kwargs):
        return _compiled.call('StatedBound.record', *args, **kwargs)

def bound(*args, **kwargs):
    return _compiled.call('bound', *args, **kwargs)

def state(*args, **kwargs):
    return _compiled.call('state', *args, **kwargs)

def records(*args, **kwargs):
    return _compiled.call('records', *args, **kwargs)

def report(*args, **kwargs):
    return _compiled.call('report', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['bound', 'state', 'records', 'report'])
_rust_exports = frozenset(['namedtuple', 'Bound', 'BOUNDS', 'StatedBound', 'bound', 'state', 'records', 'report'])
sys.modules[__name__].__class__ = _RustSurface
