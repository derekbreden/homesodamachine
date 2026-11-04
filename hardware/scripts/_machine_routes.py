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
_compiled = _RustModule('_machine_routes')

def numbers(*args, **kwargs):
    return _compiled.call('numbers', *args, **kwargs)

def equipment_inputs(*args, **kwargs):
    return _compiled.call('equipment_inputs', *args, **kwargs)

def build(*args, **kwargs):
    return _compiled.call('build', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['numbers', 'equipment_inputs', 'build'])
_rust_exports = frozenset(['annotations', 'deepcopy', 'json', 'Path', 'numbers', 'equipment_inputs', 'build'])
sys.modules[__name__].__class__ = _RustSurface
