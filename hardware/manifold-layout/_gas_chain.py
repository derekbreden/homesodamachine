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
_compiled = _RustModule('_gas_chain')

def advance(*args, **kwargs):
    return _compiled.call('advance', *args, **kwargs)

def regulator_inlet(*args, **kwargs):
    return _compiled.call('regulator_inlet', *args, **kwargs)

def regulator_outlet(*args, **kwargs):
    return _compiled.call('regulator_outlet', *args, **kwargs)

def check_inlet(*args, **kwargs):
    return _compiled.call('check_inlet', *args, **kwargs)

def check_outlet(*args, **kwargs):
    return _compiled.call('check_outlet', *args, **kwargs)

def check_socket(*args, **kwargs):
    return _compiled.call('check_socket', *args, **kwargs)

def male_connector(*args, **kwargs):
    return _compiled.call('male_connector', *args, **kwargs)

def female_adapter(*args, **kwargs):
    return _compiled.call('female_adapter', *args, **kwargs)

def bodies(*args, **kwargs):
    return _compiled.call('bodies', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['advance', 'regulator_inlet', 'regulator_outlet', 'check_inlet', 'check_outlet', 'check_socket', 'male_connector', 'female_adapter', 'bodies'])
_rust_exports = frozenset(['sys', 'Path', 'cq', '_hw', '_folder', '_ptc', '_check', '_reg', '_female', 'MALE_REACH', 'FEMALE_REACH', 'REGULATOR_ENGAGEMENT', 'REGULATOR_FEMALE_REACH', 'REG_IN_ADAPTER', 'REG_OUT_ADAPTER', 'CHECK_IN_ADAPTER', 'CHECK_OUT_ADAPTER', 'ADAPTER_NAMES', 'PORT_ADAPTERS', 'advance', 'regulator_inlet', 'regulator_outlet', 'check_inlet', 'check_outlet', 'check_socket', 'male_connector', 'female_adapter', 'bodies'])
sys.modules[__name__].__class__ = _RustSurface
