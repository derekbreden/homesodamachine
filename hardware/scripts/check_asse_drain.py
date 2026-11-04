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
_compiled = _RustModule('check_asse_drain')

def sha(*args, **kwargs):
    return _compiled.call('sha', *args, **kwargs)

def centerline_radii(*args, **kwargs):
    return _compiled.call('centerline_radii', *args, **kwargs)

def _path(*args, **kwargs):
    return _compiled.call('_path', *args, **kwargs)

def _binding(*args, **kwargs):
    return _compiled.call('_binding', *args, **kwargs)

def _names(*args, **kwargs):
    return _compiled.call('_names', *args, **kwargs)

def _base(*args, **kwargs):
    return _compiled.call('_base', *args, **kwargs)

def _overlap(*args, **kwargs):
    return _compiled.call('_overlap', *args, **kwargs)

def _rows(*args, **kwargs):
    return _compiled.call('_rows', *args, **kwargs)

def _torus_records(*args, **kwargs):
    return _compiled.call('_torus_records', *args, **kwargs)

def write(*args, **kwargs):
    return _compiled.call('write', *args, **kwargs)

def main(*args, **kwargs):
    return _compiled.call('main', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['sha', 'centerline_radii', '_path', '_binding', '_names', '_base', '_overlap', '_rows', '_torus_records', 'write', 'main'])
_rust_exports = frozenset(['Path', 'hashlib', 'json', 'sys', 'ROOT', 'OUTPUT', 'NAMES', 'CONNECTED', 'sha', 'centerline_radii', '_path', '_binding', '_names', '_base', '_overlap', '_rows', '_torus_records', 'write', 'main', 'pair'])
sys.modules[__name__].__class__ = _RustSurface

if __name__ == '__main__':
    _compiled.main()
