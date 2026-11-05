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
_compiled = _RustModule('_machine_checks')

def _path(*args, **kwargs):
    return _compiled.call('_path', *args, **kwargs)

def _sha(*args, **kwargs):
    return _compiled.call('_sha', *args, **kwargs)

def _binding(*args, **kwargs):
    return _compiled.call('_binding', *args, **kwargs)

def _plain(*args, **kwargs):
    return _compiled.call('_plain', *args, **kwargs)

def _construction_metadata(*args, **kwargs):
    return _compiled.call('_construction_metadata', *args, **kwargs)

def read(*args, **kwargs):
    return _compiled.call('read', *args, **kwargs)

def check(*args, **kwargs):
    return _compiled.call('check', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['_path', '_sha', '_binding', '_plain', '_construction_metadata', 'read', 'check'])
_rust_exports = frozenset(['annotations', 'ast', 'redirect_stdout', 'hashlib', 'importlib', 'io', 'json', 'Path', 'sys', 'ROOT', '_path', '_sha', '_binding', '_plain', '_source_statements', '_construction_metadata', 'read', 'check'])
sys.modules[__name__].__class__ = _RustSurface
