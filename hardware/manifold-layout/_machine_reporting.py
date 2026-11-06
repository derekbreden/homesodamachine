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
_compiled = _RustModule('_machine_reporting')

def _paths(*args, **kwargs):
    return _compiled.call('_paths', *args, **kwargs)

def plain(*args, **kwargs):
    return _compiled.call('plain', *args, **kwargs)

def scalar_namespace(*args, **kwargs):
    return _compiled.call('scalar_namespace', *args, **kwargs)

def _request(*args, **kwargs):
    return _compiled.call('_request', *args, **kwargs)

def _bounds(*args, **kwargs):
    return _compiled.call('_bounds', *args, **kwargs)

def _ports(*args, **kwargs):
    return _compiled.call('_ports', *args, **kwargs)

def _route_rows(*args, **kwargs):
    return _compiled.call('_route_rows', *args, **kwargs)

def _run_length(*args, **kwargs):
    return _compiled.call('_run_length', *args, **kwargs)

def scene_document(*args, **kwargs):
    return _compiled.call('scene_document', *args, **kwargs)

def gather(*args, **kwargs):
    return _compiled.call('gather', *args, **kwargs)

def write(*args, **kwargs):
    return _compiled.call('write', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['_paths', 'plain', 'scalar_namespace', '_request', '_bounds', '_ports', '_route_rows', '_run_length', 'scene_document', 'gather', 'write'])
_rust_exports = frozenset(['annotations', 'hashlib', 'importlib', 'json', 'Path', 'sys', 'time', 'SimpleNamespace', 'ROOT', 'HW', 'LAYOUT', '_paths', 'plain', 'scalar_namespace', '_request', '_bounds', '_ports', '_route_rows', '_run_length', 'scene_document', 'gather', 'write'])
sys.modules[__name__].__class__ = _RustSurface
