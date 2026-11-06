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
_compiled = _RustModule('_facts')

class _BB:
    __slots__ = ('xmin', 'ymin', 'zmin', 'xmax', 'ymax', 'zmax')
    def __init__(*args, **kwargs):
        return _compiled.call('_BB.__init__', *args, **kwargs)
    def add(*args, **kwargs):
        return _compiled.call('_BB.add', *args, **kwargs)
    @property
    def xlen(*args, **kwargs):
        return _compiled.call('_BB.xlen', *args, **kwargs)
    @property
    def ylen(*args, **kwargs):
        return _compiled.call('_BB.ylen', *args, **kwargs)
    @property
    def zlen(*args, **kwargs):
        return _compiled.call('_BB.zlen', *args, **kwargs)
    def __repr__(*args, **kwargs):
        return _compiled.call('_BB.__repr__', *args, **kwargs)

class _Frame:
    __slots__ = ('ports',)
    def __init__(*args, **kwargs):
        return _compiled.call('_Frame.__init__', *args, **kwargs)

class _Row(dict):
    def __getattr__(*args, **kwargs):
        return _compiled.call('_Row.__getattr__', *args, **kwargs)

class Facts:
    def __init__(*args, **kwargs):
        return _compiled.call('Facts.__init__', *args, **kwargs)
    @property
    def box(*args, **kwargs):
        return _compiled.call('Facts.box', *args, **kwargs)
    @property
    def pack(*args, **kwargs):
        return _compiled.call('Facts.pack', *args, **kwargs)
    @property
    def card_ports(*args, **kwargs):
        return _compiled.call('Facts.card_ports', *args, **kwargs)
    @property
    def constants(*args, **kwargs):
        return _compiled.call('Facts.constants', *args, **kwargs)
    @property
    def bodies(*args, **kwargs):
        return _compiled.call('Facts.bodies', *args, **kwargs)
    def bb(*args, **kwargs):
        return _compiled.call('Facts.bb', *args, **kwargs)
    def group(*args, **kwargs):
        return _compiled.call('Facts.group', *args, **kwargs)
    @property
    def runs(*args, **kwargs):
        return _compiled.call('Facts.runs', *args, **kwargs)

def _request(*args, **kwargs):
    return _compiled.call('_request', *args, **kwargs)

def _read_graph(*args, **kwargs):
    return _compiled.call('_read_graph', *args, **kwargs)

def _source_names(*args, **kwargs):
    return _compiled.call('_source_names', *args, **kwargs)

def sources(*args, **kwargs):
    return _compiled.call('sources', *args, **kwargs)

def write(*args, **kwargs):
    return _compiled.call('write', *args, **kwargs)

def read(*args, **kwargs):
    return _compiled.call('read', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['_request', '_read_graph', '_source_names', 'sources', 'write', 'read'])
_rust_exports = frozenset(['json', 'sys', 'Path', '_HERE', '_HW', '_ROOT', '_p', 'ARTIFACT', 'GRAPH', '_request', '_read_graph', '_source_names', 'sources', 'CARD_PORT_BODIES', '_BOX_FACT_ORDER', 'write', '_BB', '_Frame', '_Row', 'Facts', 'read'])
sys.modules[__name__].__class__ = _RustSurface
