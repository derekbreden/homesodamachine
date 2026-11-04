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
_compiled = _RustModule('rear_snaps')

def surface_points(*args, **kwargs):
    return _compiled.call('surface_points', *args, **kwargs)

def envelope(*args, **kwargs):
    return _compiled.call('envelope', *args, **kwargs)

def swept(*args, **kwargs):
    return _compiled.call('swept', *args, **kwargs)

def steps(*args, **kwargs):
    return _compiled.call('steps', *args, **kwargs)

def turned(*args, **kwargs):
    return _compiled.call('turned', *args, **kwargs)

def hex_prism(*args, **kwargs):
    return _compiled.call('hex_prism', *args, **kwargs)

def asse_cap_profile(*args, **kwargs):
    return _compiled.call('asse_cap_profile', *args, **kwargs)

def asse_cap_room(*args, **kwargs):
    return _compiled.call('asse_cap_room', *args, **kwargs)

def meter_cap_corner_room(*args, **kwargs):
    return _compiled.call('meter_cap_corner_room', *args, **kwargs)

def box(*args, **kwargs):
    return _compiled.call('box', *args, **kwargs)

def stadium_x(*args, **kwargs):
    return _compiled.call('stadium_x', *args, **kwargs)

def half_width(*args, **kwargs):
    return _compiled.call('half_width', *args, **kwargs)

def station(*args, **kwargs):
    return _compiled.call('station', *args, **kwargs)

def receiver_tool_ports(*args, **kwargs):
    return _compiled.call('receiver_tool_ports', *args, **kwargs)

def prism_x(*args, **kwargs):
    return _compiled.call('prism_x', *args, **kwargs)

def clearance_profile(*args, **kwargs):
    return _compiled.call('clearance_profile', *args, **kwargs)

def radial_profile(*args, **kwargs):
    return _compiled.call('radial_profile', *args, **kwargs)

def asse_adapter_capture(*args, **kwargs):
    return _compiled.call('asse_adapter_capture', *args, **kwargs)

def stadium_profile_x(*args, **kwargs):
    return _compiled.call('stadium_profile_x', *args, **kwargs)

def radial_room(*args, **kwargs):
    return _compiled.call('radial_room', *args, **kwargs)

def pisco_grip_stock(*args, **kwargs):
    return _compiled.call('pisco_grip_stock', *args, **kwargs)

def pisco_cap_fit(*args, **kwargs):
    return _compiled.call('pisco_cap_fit', *args, **kwargs)

def pisco_bearing_profile(*args, **kwargs):
    return _compiled.call('pisco_bearing_profile', *args, **kwargs)

def pockets(*args, **kwargs):
    return _compiled.call('pockets', *args, **kwargs)

def pisco_cap_service_cuts(*args, **kwargs):
    return _compiled.call('pisco_cap_service_cuts', *args, **kwargs)

def asse_service_corner(*args, **kwargs):
    return _compiled.call('asse_service_corner', *args, **kwargs)

def pisco_station(*args, **kwargs):
    return _compiled.call('pisco_station', *args, **kwargs)

def pisco_cap_span(*args, **kwargs):
    return _compiled.call('pisco_cap_span', *args, **kwargs)

def cap_section(*args, **kwargs):
    return _compiled.call('cap_section', *args, **kwargs)

def section_solid(*args, **kwargs):
    return _compiled.call('section_solid', *args, **kwargs)

def cap(*args, **kwargs):
    return _compiled.call('cap', *args, **kwargs)

def at_world(*args, **kwargs):
    return _compiled.call('at_world', *args, **kwargs)

def build(*args, **kwargs):
    return _compiled.call('build', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['surface_points', 'envelope', 'swept', 'steps', 'turned', 'hex_prism', 'asse_cap_profile', 'asse_cap_room', 'meter_cap_corner_room', 'box', 'stadium_x', 'half_width', 'station', 'receiver_tool_ports', 'prism_x', 'clearance_profile', 'radial_profile', 'asse_adapter_capture', 'stadium_profile_x', 'radial_room', 'pisco_grip_stock', 'pisco_cap_fit', 'pisco_bearing_profile', 'pockets', 'pisco_cap_service_cuts', 'asse_service_corner', 'pisco_station', 'pisco_cap_span', 'cap_section', 'section_solid', 'cap', 'at_world', 'build'])
_rust_exports = frozenset(['json', 'math', 'Path', 'np', 'cq', 'fits', 'SLIDE', 'THREAD', 'WALL', 'SPLIT', 'INTO', 'WING', 'REACH', 'SIDE', 'FREE_LENGTH', 'ROOT_RADIUS', 'REAR_ROOT_DROP', 'ASSE_HEX_SEATING_DEPTH', 'ASSE_BODY_SEATING_DEPTH', 'PISCO_RADIAL_RELIEF', 'PISCO_CAP_AIR', 'PISCO_CAP_FIT', 'PISCO_BEARING_LENGTH', 'METER_AIR', 'METER_BACK', 'METER_CAP_AIR', 'METER_HOUSING_FIT', 'METER_BEARING_DEPTH', 'LEDGE', 'NOSE_LAND', 'TIP_RISE', 'TOOL_SLOT_WIDTH', 'TOOL_SLOT_HEIGHT', 'TOOL_APPROACH_DEGREES', 'HOOK', 'CATCH', 'VAR', 'METER_COLLAR_AXIAL_AIR', 'CHAIN', 'SOLIDS', 'SEATS', 'CAPS', 'ON', 'surface_points', 'envelope', 'swept', 'steps', 'turned', 'hex_prism', 'asse_cap_profile', 'asse_cap_room', 'meter_cap_corner_room', 'box', 'stadium_x', 'half_width', 'station', 'receiver_tool_ports', 'prism_x', 'clearance_profile', 'radial_profile', 'asse_adapter_capture', 'stadium_profile_x', 'radial_room', 'pisco_grip_stock', 'pisco_cap_fit', 'pisco_bearing_profile', 'pockets', 'pisco_cap_service_cuts', 'asse_service_corner', 'pisco_station', 'pisco_cap_span', 'cap_section', 'section_solid', 'cap', 'at_world', 'build'])
sys.modules[__name__].__class__ = _RustSurface
