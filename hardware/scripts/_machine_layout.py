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
_compiled = _RustModule('_machine_layout')

def _source(*args, **kwargs):
    return _compiled.call('_source', *args, **kwargs)

def _linear(*args, **kwargs):
    return _compiled.call('_linear', *args, **kwargs)

def _point(*args, **kwargs):
    return _compiled.call('_point', *args, **kwargs)

def _axis(*args, **kwargs):
    return _compiled.call('_axis', *args, **kwargs)

def _installed(*args, **kwargs):
    return _compiled.call('_installed', *args, **kwargs)

def _manifold_datums(*args, **kwargs):
    return _compiled.call('_manifold_datums', *args, **kwargs)

def numbers(*args, **kwargs):
    return _compiled.call('numbers', *args, **kwargs)

def _box_tuple(*args, **kwargs):
    return _compiled.call('_box_tuple', *args, **kwargs)

def installed_numbers(*args, **kwargs):
    return _compiled.call('installed_numbers', *args, **kwargs)

def _run_records(*args, **kwargs):
    return _compiled.call('_run_records', *args, **kwargs)

def _result_plan(*args, **kwargs):
    return _compiled.call('_result_plan', *args, **kwargs)

def _route_records(*args, **kwargs):
    return _compiled.call('_route_records', *args, **kwargs)

def _placement_metadata(*args, **kwargs):
    return _compiled.call('_placement_metadata', *args, **kwargs)

def _equipment(*args, **kwargs):
    return _compiled.call('_equipment', *args, **kwargs)

def _normal_metadata(*args, **kwargs):
    return _compiled.call('_normal_metadata', *args, **kwargs)

def _bind_presentations(*args, **kwargs):
    return _compiled.call('_bind_presentations', *args, **kwargs)

def _work_directory(*args, **kwargs):
    return _compiled.call('_work_directory', *args, **kwargs)

def _run(*args, **kwargs):
    return _compiled.call('_run', *args, **kwargs)

def plan(*args, **kwargs):
    return _compiled.call('plan', *args, **kwargs)

def dock_instances(*args, **kwargs):
    return _compiled.call('dock_instances', *args, **kwargs)

def main(*args, **kwargs):
    return _compiled.call('main', *args, **kwargs)

def _view_metadata(*args, **kwargs):
    return _compiled.call('_view_metadata', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['_source', '_linear', '_point', '_axis', '_installed', '_manifold_datums', 'numbers', '_box_tuple', 'installed_numbers', '_run_records', '_result_plan', '_route_records', '_placement_metadata', '_equipment', '_normal_metadata', '_bind_presentations', '_work_directory', '_run', 'plan', 'dock_instances', 'main', '_view_metadata'])
_rust_exports = frozenset(['annotations', 'json', 'math', 'Path', 'sys', 'ROOT', 'HW', 'LAYOUT', 'ENCLOSURE', '_path', '_source', '_linear', '_point', '_axis', '_installed', '_manifold_datums', 'numbers', '_box_tuple', 'installed_numbers', '_run_records', '_result_plan', '_route_records', '_placement_metadata', '_equipment', '_normal_metadata', '_bind_presentations', '_work_directory', '_run', 'plan', 'dock_instances', 'main', '_view_metadata'])
sys.modules[__name__].__class__ = _RustSurface
