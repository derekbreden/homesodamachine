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
_compiled = _RustModule('above_core_wiring')

def placements(*args, **kwargs):
    return _compiled.call('placements', *args, **kwargs)

def frame(*args, **kwargs):
    return _compiled.call('frame', *args, **kwargs)

def owner(*args, **kwargs):
    return _compiled.call('owner', *args, **kwargs)

def carry(*args, **kwargs):
    return _compiled.call('carry', *args, **kwargs)

def components(*args, **kwargs):
    return _compiled.call('components', *args, **kwargs)

def _box(*args, **kwargs):
    return _compiled.call('_box', *args, **kwargs)

def _well(*args, **kwargs):
    return _compiled.call('_well', *args, **kwargs)

def _union(*args, **kwargs):
    return _compiled.call('_union', *args, **kwargs)

def _features(*args, **kwargs):
    return _compiled.call('_features', *args, **kwargs)

def cap_features(*args, **kwargs):
    return _compiled.call('cap_features', *args, **kwargs)

def shell_features(*args, **kwargs):
    return _compiled.call('shell_features', *args, **kwargs)

def driver_columns(*args, **kwargs):
    return _compiled.call('driver_columns', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['placements', 'frame', 'owner', 'carry', 'components', '_box', '_well', '_union', '_features', 'cap_features', 'shell_features', 'driver_columns'])
_rust_exports = frozenset(['cache', 'Path', 'sys', 'cq', 'HERE', 'HW', 'layout', 'import_step', 'C_AC_HUB', 'REFERENCES', 'SIZES', 'IDENTITY', 'PORTS_WEST', 'PORTS_FORE', 'UPRIGHT_PORTS_FORE', 'WALL_BACK_FORE', 'WALL_BACK_AFT', 'EAST_FLANK', 'WALL', 'FIT', 'placements', 'frame', 'owner', 'carry', 'components', '_box', '_well', '_union', '_features', 'cap_features', 'shell_features', 'driver_columns'])
sys.modules[__name__].__class__ = _RustSurface
