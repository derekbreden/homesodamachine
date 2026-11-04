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
_compiled = _RustModule('_machine')

@dataclasses.dataclass
class Machine:
    bodies: dict
    colors: dict
    solids: tuple
    core: tuple
    runs: dict
    frames: dict
    box: object
    anchors: dict
    sources: dict
    taken: float
    path: Path = None
    card: dict = None
    drain: dict = None
    @property
    def moved(*args, **kwargs):
        return _compiled.call('Machine.moved', *args, **kwargs)
    def measured(*args, **kwargs):
        return _compiled.call('Machine.measured', *args, **kwargs)

def sources(*args, **kwargs):
    return _compiled.call('sources', *args, **kwargs)

def stamps(*args, **kwargs):
    return _compiled.call('stamps', *args, **kwargs)

def document(*args, **kwargs):
    return _compiled.call('document', *args, **kwargs)

def write_from_fine(*args, **kwargs):
    return _compiled.call('write_from_fine', *args, **kwargs)

def _tupled(*args, **kwargs):
    return _compiled.call('_tupled', *args, **kwargs)

def _run(*args, **kwargs):
    return _compiled.call('_run', *args, **kwargs)

def _box(*args, **kwargs):
    return _compiled.call('_box', *args, **kwargs)

def load(*args, **kwargs):
    return _compiled.call('load', *args, **kwargs)

def current(*args, **kwargs):
    return _compiled.call('current', *args, **kwargs)

def machine(*args, **kwargs):
    return _compiled.call('machine', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['sources', 'stamps', 'document', 'write_from_fine', '_tupled', '_run', '_box', 'load', 'current', 'machine'])
_rust_exports = frozenset(['dataclasses', 'json', 'sys', 'time', 'types', 'Path', '_HERE', '_ROOT', '_ML', 'PATH', 'SCHEMA', '_GRAPH', '_WORLD', '_FALLBACK_SOURCES', 'sources', 'stamps', 'Machine', 'document', 'write_from_fine', '_tupled', '_run', '_box', 'load', 'current', 'machine'])
sys.modules[__name__].__class__ = _RustSurface
