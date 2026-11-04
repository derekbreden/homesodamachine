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
_compiled = _RustModule('_machine_equipment')

def _request(*args, **kwargs):
    return _compiled.call('_request', *args, **kwargs)

def _read(*args, **kwargs):
    return _compiled.call('_read', *args, **kwargs)

def frame(*args, **kwargs):
    return _compiled.call('frame', *args, **kwargs)

def compose(*args, **kwargs):
    return _compiled.call('compose', *args, **kwargs)

def transform(*args, **kwargs):
    return _compiled.call('transform', *args, **kwargs)

def _along_y(*args, **kwargs):
    return _compiled.call('_along_y', *args, **kwargs)

def plan(*args, **kwargs):
    return _compiled.call('plan', *args, **kwargs)

def _source(*args, **kwargs):
    return _compiled.call('_source', *args, **kwargs)

def _stem(*args, **kwargs):
    return _compiled.call('_stem', *args, **kwargs)

def _reducer(*args, **kwargs):
    return _compiled.call('_reducer', *args, **kwargs)

def _check(*args, **kwargs):
    return _compiled.call('_check', *args, **kwargs)

def _bfp_port(*args, **kwargs):
    return _compiled.call('_bfp_port', *args, **kwargs)

def _chain_parts(*args, **kwargs):
    return _compiled.call('_chain_parts', *args, **kwargs)

def _inputs(*args, **kwargs):
    return _compiled.call('_inputs', *args, **kwargs)

def _context(*args, **kwargs):
    return _compiled.call('_context', *args, **kwargs)

def _chain_inlet(*args, **kwargs):
    return _compiled.call('_chain_inlet', *args, **kwargs)

def local_ports(*args, **kwargs):
    return _compiled.call('local_ports', *args, **kwargs)

def _grid(*args, **kwargs):
    return _compiled.call('_grid', *args, **kwargs)

def _joint_numbers(*args, **kwargs):
    return _compiled.call('_joint_numbers', *args, **kwargs)

def _palette(*args, **kwargs):
    return _compiled.call('_palette', *args, **kwargs)

def numbers(*args, **kwargs):
    return _compiled.call('numbers', *args, **kwargs)

def build(*args, **kwargs):
    return _compiled.call('build', *args, **kwargs)

def _reducer_insertion(*args, **kwargs):
    return _compiled.call('_reducer_insertion', *args, **kwargs)

def route_port_frame(*args, **kwargs):
    return _compiled.call('route_port_frame', *args, **kwargs)

def _offset(*args, **kwargs):
    return _compiled.call('_offset', *args, **kwargs)

def _link(*args, **kwargs):
    return _compiled.call('_link', *args, **kwargs)

def _line(*args, **kwargs):
    return _compiled.call('_line', *args, **kwargs)

def _bezier(*args, **kwargs):
    return _compiled.call('_bezier', *args, **kwargs)

def _crowned_beziers(*args, **kwargs):
    return _compiled.call('_crowned_beziers', *args, **kwargs)

def _sample_bezier(*args, **kwargs):
    return _compiled.call('_sample_bezier', *args, **kwargs)

def local_routes(*args, **kwargs):
    return _compiled.call('local_routes', *args, **kwargs)

def _arc_three(*args, **kwargs):
    return _compiled.call('_arc_three', *args, **kwargs)

def _rear_routes(*args, **kwargs):
    return _compiled.call('_rear_routes', *args, **kwargs)

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

_rust_functions = frozenset(['_request', '_read', 'frame', 'compose', 'transform', '_along_y', 'plan', '_source', '_stem', '_reducer', '_check', '_bfp_port', '_chain_parts', '_inputs', '_context', '_chain_inlet', 'local_ports', '_grid', '_joint_numbers', '_palette', 'numbers', 'build', '_reducer_insertion', 'route_port_frame', '_offset', '_link', '_line', '_bezier', '_crowned_beziers', '_sample_bezier', 'local_routes', '_arc_three', '_rear_routes', 'continuations', '_flavor_s_bend', '_flavor_rear', 'flavor_routes'])
_rust_exports = frozenset(['annotations', 'cache', 'json', 'Path', 'sys', 'ROOT', 'HW', 'LAYOUT', 'layout', 'stem_elbow_names', 'union_elbow_names', 'reservoir_gate_elbow_hosts', 'IDENTITY', '_request', '_read', 'frame', 'compose', 'transform', '_along_y', 'plan', '_source', '_stem', '_reducer', '_check', '_bfp_port', '_chain_parts', '_inputs', '_context', '_chain_inlet', 'local_ports', '_grid', '_joint_numbers', '_palette', 'numbers', 'build', '_reducer_insertion', 'route_port_frame', '_offset', '_link', '_line', '_bezier', '_crowned_beziers', '_sample_bezier', 'local_routes', '_arc_three', '_rear_routes', 'continuations', '_flavor_s_bend', '_flavor_rear', 'flavor_routes'])
sys.modules[__name__].__class__ = _RustSurface
