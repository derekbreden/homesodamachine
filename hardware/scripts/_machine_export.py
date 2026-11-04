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
_compiled = _RustModule('_machine_export')

def _run(*args, **kwargs):
    return _compiled.call('_run', *args, **kwargs)

def export(*args, **kwargs):
    return _compiled.call('export', *args, **kwargs)

def scene(*args, **kwargs):
    return _compiled.call('scene', *args, **kwargs)

def graft(*args, **kwargs):
    return _compiled.call('graft', *args, **kwargs)

def views(*args, **kwargs):
    return _compiled.call('views', *args, **kwargs)

def append_wiring(*args, **kwargs):
    return _compiled.call('append_wiring', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['_run', 'export', 'scene', 'graft', 'views', 'append_wiring'])
_rust_exports = frozenset(['annotations', 'Path', '_run', 'export', 'scene', 'graft', 'views', 'append_wiring'])
sys.modules[__name__].__class__ = _RustSurface
