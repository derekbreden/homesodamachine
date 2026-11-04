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
_compiled = _RustModule('_tube_export')

def unit(*args, **kwargs):
    return _compiled.call('unit', *args, **kwargs)

def _resolve_end(*args, **kwargs):
    return _compiled.call('_resolve_end', *args, **kwargs)

def route_metadata(*args, **kwargs):
    return _compiled.call('route_metadata', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['unit', '_resolve_end', 'route_metadata'])
_rust_exports = frozenset(['math', 'sys', 'Path', 'ROOT', 'HW', '_p', 'unit', '_resolve_end', 'route_metadata'])
sys.modules[__name__].__class__ = _RustSurface
