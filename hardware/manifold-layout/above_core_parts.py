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
_compiled = _RustModule('above_core_parts')

def _module(*args, **kwargs):
    return _compiled.call('_module', *args, **kwargs)

def check_reference(*args, **kwargs):
    return _compiled.call('check_reference', *args, **kwargs)

def tee_reference(*args, **kwargs):
    return _compiled.call('tee_reference', *args, **kwargs)

def stem_elbow_reference(*args, **kwargs):
    return _compiled.call('stem_elbow_reference', *args, **kwargs)

def _frame(*args, **kwargs):
    return _compiled.call('_frame', *args, **kwargs)

def _compose(*args, **kwargs):
    return _compiled.call('_compose', *args, **kwargs)

def _snapshot(*args, **kwargs):
    return _compiled.call('_snapshot', *args, **kwargs)

def route_port_frame(*args, **kwargs):
    return _compiled.call('route_port_frame', *args, **kwargs)

def _grid(*args, **kwargs):
    return _compiled.call('_grid', *args, **kwargs)

def _grid_module(*args, **kwargs):
    return _compiled.call('_grid_module', *args, **kwargs)

def core_components(*args, **kwargs):
    return _compiled.call('core_components', *args, **kwargs)

def _offset(*args, **kwargs):
    return _compiled.call('_offset', *args, **kwargs)

def _link(*args, **kwargs):
    return _compiled.call('_link', *args, **kwargs)

def port_stations(*args, **kwargs):
    return _compiled.call('port_stations', *args, **kwargs)

def _line(*args, **kwargs):
    return _compiled.call('_line', *args, **kwargs)

def _bezier(*args, **kwargs):
    return _compiled.call('_bezier', *args, **kwargs)

def _crowned_beziers(*args, **kwargs):
    return _compiled.call('_crowned_beziers', *args, **kwargs)

def _sample_bezier(*args, **kwargs):
    return _compiled.call('_sample_bezier', *args, **kwargs)

def route_specs(*args, **kwargs):
    return _compiled.call('route_specs', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['_module', 'check_reference', 'tee_reference', 'stem_elbow_reference', '_frame', '_compose', '_snapshot', 'route_port_frame', '_grid', '_grid_module', 'core_components', '_offset', '_link', 'port_stations', '_line', '_bezier', '_crowned_beziers', '_sample_bezier', 'route_specs'])
_rust_exports = frozenset(['cache', 'importlib', 'Path', 'sys', 'HERE', 'HW', 'ROOT', 'layout', '_data', 'stem_elbow_names', 'core_stem_elbow_names', 'reservoir_gate_elbow_hosts', 'union_elbow_names', 'core_union_elbow_names', 'IDENTITY', 'ORIGIN', 'REFERENCES', '_module', 'check_reference', 'tee_reference', 'stem_elbow_reference', '_frame', '_compose', '_snapshot', 'route_port_frame', '_grid', '_grid_module', 'core_components', '_offset', '_link', 'port_stations', '_line', '_bezier', '_crowned_beziers', '_sample_bezier', 'route_specs'])
sys.modules[__name__].__class__ = _RustSurface
