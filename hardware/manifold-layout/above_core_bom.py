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
_compiled = _RustModule('above_core_bom')

def reservoir_gate_elbow_hosts(*args, **kwargs):
    return _compiled.call('reservoir_gate_elbow_hosts', *args, **kwargs)

def stem_elbow_names(*args, **kwargs):
    return _compiled.call('stem_elbow_names', *args, **kwargs)

def core_stem_elbow_names(*args, **kwargs):
    return _compiled.call('core_stem_elbow_names', *args, **kwargs)

def union_elbow_names(*args, **kwargs):
    return _compiled.call('union_elbow_names', *args, **kwargs)

def core_union_elbow_names(*args, **kwargs):
    return _compiled.call('core_union_elbow_names', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['reservoir_gate_elbow_hosts', 'stem_elbow_names', 'core_stem_elbow_names', 'union_elbow_names', 'core_union_elbow_names'])
_rust_exports = frozenset(['layout', '_data', 'reservoir_gate_elbow_hosts', 'stem_elbow_names', 'core_stem_elbow_names', 'union_elbow_names', 'core_union_elbow_names'])
sys.modules[__name__].__class__ = _RustSurface
