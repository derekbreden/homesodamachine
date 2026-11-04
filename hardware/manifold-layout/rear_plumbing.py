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
_compiled = _RustModule('rear_plumbing')

def plan(*args, **kwargs):
    return _compiled.call('plan', *args, **kwargs)

def reference(*args, **kwargs):
    return _compiled.call('reference', *args, **kwargs)

def chain(*args, **kwargs):
    return _compiled.call('chain', *args, **kwargs)

def union_tee(*args, **kwargs):
    return _compiled.call('union_tee', *args, **kwargs)

def check(*args, **kwargs):
    return _compiled.call('check', *args, **kwargs)

def joint(*args, **kwargs):
    return _compiled.call('joint', *args, **kwargs)

def _arc_three(*args, **kwargs):
    return _compiled.call('_arc_three', *args, **kwargs)

def ports(*args, **kwargs):
    return _compiled.call('ports', *args, **kwargs)

def snap_datums(*args, **kwargs):
    return _compiled.call('snap_datums', *args, **kwargs)

def regulator_datums(*args, **kwargs):
    return _compiled.call('regulator_datums', *args, **kwargs)

def meter_spans(*args, **kwargs):
    return _compiled.call('meter_spans', *args, **kwargs)

def _route_stations(*args, **kwargs):
    return _compiled.call('_route_stations', *args, **kwargs)

def route_specs(*args, **kwargs):
    return _compiled.call('route_specs', *args, **kwargs)

def continuations(*args, **kwargs):
    return _compiled.call('continuations', *args, **kwargs)

def _flavor_s_bend(*args, **kwargs):
    return _compiled.call('_flavor_s_bend', *args, **kwargs)

def _flavor_rear(*args, **kwargs):
    return _compiled.call('_flavor_rear', *args, **kwargs)

def flavor_routes(*args, **kwargs):
    return _compiled.call('flavor_routes', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['plan', 'reference', 'chain', 'union_tee', 'check', 'joint', '_arc_three', 'ports', 'snap_datums', 'regulator_datums', 'meter_spans', '_route_stations', 'route_specs', 'continuations', '_flavor_s_bend', '_flavor_rear', 'flavor_routes'])
_rust_exports = frozenset(['json', 'Path', 'np', 'layout', '_data', 'plan', 'reference', 'chain', 'union_tee', 'check', 'joint', '_arc_three', 'ports', 'snap_datums', 'regulator_datums', 'meter_spans', '_route_stations', 'route_specs', 'continuations', '_flavor_s_bend', '_flavor_rear', 'flavor_routes'])
sys.modules[__name__].__class__ = _RustSurface
