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
_compiled = _RustModule('_lines')

def _ea_cap(*args, **kwargs):
    return _compiled.call('_ea_cap', *args, **kwargs)

def valve_ends(*args, **kwargs):
    return _compiled.call('valve_ends', *args, **kwargs)

def flavor_outlet(*args, **kwargs):
    return _compiled.call('flavor_outlet', *args, **kwargs)

def frames(*args, **kwargs):
    return _compiled.call('frames', *args, **kwargs)

def _frame(*args, **kwargs):
    return _compiled.call('_frame', *args, **kwargs)

def build_runs(*args, **kwargs):
    return _compiled.call('build_runs', *args, **kwargs)

def build_seated_runs(*args, **kwargs):
    return _compiled.call('build_seated_runs', *args, **kwargs)

def _co2_0(*args, **kwargs):
    return _compiled.call('_co2_0', *args, **kwargs)

def _co2_1(*args, **kwargs):
    return _compiled.call('_co2_1', *args, **kwargs)

def _water_3(*args, **kwargs):
    return _compiled.call('_water_3', *args, **kwargs)

def _fluid_1(*args, **kwargs):
    return _compiled.call('_fluid_1', *args, **kwargs)

def _water_2(*args, **kwargs):
    return _compiled.call('_water_2', *args, **kwargs)

def _water_7(*args, **kwargs):
    return _compiled.call('_water_7', *args, **kwargs)

def _water_6(*args, **kwargs):
    return _compiled.call('_water_6', *args, **kwargs)

def _water_5(*args, **kwargs):
    return _compiled.call('_water_5', *args, **kwargs)

def _co2_2(*args, **kwargs):
    return _compiled.call('_co2_2', *args, **kwargs)

def _fluid_2(*args, **kwargs):
    return _compiled.call('_fluid_2', *args, **kwargs)

def _fluid_4(*args, **kwargs):
    return _compiled.call('_fluid_4', *args, **kwargs)

def _carb_1(*args, **kwargs):
    return _compiled.call('_carb_1', *args, **kwargs)

def _carb_2(*args, **kwargs):
    return _compiled.call('_carb_2', *args, **kwargs)

def _gate_a_anchor(*args, **kwargs):
    return _compiled.call('_gate_a_anchor', *args, **kwargs)

def gate_cruise(*args, **kwargs):
    return _compiled.call('gate_cruise', *args, **kwargs)

def station(*args, **kwargs):
    return _compiled.call('station', *args, **kwargs)

def _gate_climb_under_cruise(*args, **kwargs):
    return _compiled.call('_gate_climb_under_cruise', *args, **kwargs)

def _fluid_28(*args, **kwargs):
    return _compiled.call('_fluid_28', *args, **kwargs)

def _fluid_18(*args, **kwargs):
    return _compiled.call('_fluid_18', *args, **kwargs)

def _fill_a_lane_y(*args, **kwargs):
    return _compiled.call('_fill_a_lane_y', *args, **kwargs)

def _fill_a_cap_z(*args, **kwargs):
    return _compiled.call('_fill_a_cap_z', *args, **kwargs)

def _fill_a_turn_y(*args, **kwargs):
    return _compiled.call('_fill_a_turn_y', *args, **kwargs)

def _fluid_14(*args, **kwargs):
    return _compiled.call('_fluid_14', *args, **kwargs)

def _on_cap(*args, **kwargs):
    return _compiled.call('_on_cap', *args, **kwargs)

def _gate_lead(*args, **kwargs):
    return _compiled.call('_gate_lead', *args, **kwargs)

def _fluid_16(*args, **kwargs):
    return _compiled.call('_fluid_16', *args, **kwargs)

def _fluid_24(*args, **kwargs):
    return _compiled.call('_fluid_24', *args, **kwargs)

def _fluid_26(*args, **kwargs):
    return _compiled.call('_fluid_26', *args, **kwargs)

def _refrig_3(*args, **kwargs):
    return _compiled.call('_refrig_3', *args, **kwargs)

def _refrig_1(*args, **kwargs):
    return _compiled.call('_refrig_1', *args, **kwargs)

def _refrig_2(*args, **kwargs):
    return _compiled.call('_refrig_2', *args, **kwargs)

def authored(*args, **kwargs):
    return _compiled.call('authored', *args, **kwargs)

def tubes(*args, **kwargs):
    return _compiled.call('tubes', *args, **kwargs)

def report(*args, **kwargs):
    return _compiled.call('report', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['_ea_cap', 'valve_ends', 'flavor_outlet', 'frames', '_frame', 'build_runs', 'build_seated_runs', '_co2_0', '_co2_1', '_water_3', '_fluid_1', '_water_2', '_water_7', '_water_6', '_water_5', '_co2_2', '_fluid_2', '_fluid_4', '_carb_1', '_carb_2', '_gate_a_anchor', 'gate_cruise', 'station', '_gate_climb_under_cruise', '_fluid_28', '_fluid_18', '_fill_a_lane_y', '_fill_a_cap_z', '_fill_a_turn_y', '_fluid_14', '_on_cap', '_gate_lead', '_fluid_16', '_fluid_24', '_fluid_26', '_refrig_3', '_refrig_1', '_refrig_2', 'authored', 'tubes', 'report'])
_rust_exports = frozenset(['math', 'sys', 'Path', '_here', '_hw', '_p', 'R', '_cc', '_anchor_cap', '_asse', '_funnel', '_pump', '_pump_elbow', '_dis', '_beduan', '_jg', '_drain_elbow', '_drain_bulkhead', '_flavor_reducer', '_neofit', '_flowreg', '_split', '_ml', '_comp', '_cond', '_copper', '_gasher', '_wr1110', '_gas_chain', '_digiten', '_card', 'BLOCKED', '_ea_cap', 'TUBE_BEND', 'ELBOW_CUFF_D', 'SUCTION_LEAD', 'DISCHARGE_LEAD', 'CU_OD', 'CU_BEND', 'CU_LEAD', 'CU_SUCTION_LANE', 'CAP_BORE_SKEW', 'PORT_ADAPTERS', 'STATIONS', '_b', 'VALVES', 'valve_ends', '_v', '_in', '_out', 'flavor_outlet', 'frames', '_frame', 'build_runs', 'build_seated_runs', '_co2_0', '_co2_1', '_CORE_FRONT_Y', 'CROSS_Y', 'CROSS_DODGE_Y', 'CROSS_DODGE_SPAN', 'CROSS_DODGE_RAMP', 'CROSS_DROP', 'CHANNEL_X', 'CROSS_RISE', 'CHANNEL_ENTRY_Y', 'CROSS_LIFT_X', 'CROSS_APPROACH_Y', '_water_3', 'FLUID_1_INBOARD', 'FLUID_1_APPROACH', 'FLUID_1_DIAGONAL', '_fluid_1', 'WATER_2_LEAD', 'WATER_2_RUN', '_water_2', '_water_7', '_water_6', '_water_5', '_co2_2', 'FLUID_2_LEAD', 'FLUID_2_RETURN_X', 'FLUID_2_RETURN_FORE_Y', 'FLUID_2_OVER_CAP', 'FLUID_2_DESCENT_EAST', '_fluid_2', 'FLUID_4_CROSS_Y', '_fluid_4', 'CARB_1_FORWARD_LEAN', '_carb_1', '_carb_2', 'GATE_STUB_CLEAR', 'GATE_B_JOG_LEG', 'GATE_B_DRAIN_RETURN_RISE', 'GATE_B_RETURN_WEST', 'GATE_B_RETURN_HOLD_Y', 'GATE_B_UNION_APPROACH', 'GATE_B_STEP_Y', 'GATE_B_RISE_RUN', 'GATE_A_FRONT_Y', 'GATE_A_FRONT_Z', 'GATE_A_FRONT_JOIN_X', 'GATE_A_OUTER_X', 'GATE_A_DESCENT_START_Y', 'GATE_A_BEARING_JOIN_Y', 'GATE_A_BEARING_EXIT_Y', 'GATE_A_LOW_LANE_JOIN_Y', 'GATE_A_FORE_HEIGHT', 'GATE_A_WEST_X', 'GATE_A_RETURN_START_Y', 'GATE_A_UNION_JOIN_Y', 'GATE_A_UNION_LEVEL_RUN', 'GATE_A_RISE_RUN', '_gate_a_anchor', 'gate_cruise', 'station', 'GATE_B_CLIMB', '_gate_climb_under_cruise', '_fluid_28', '_fluid_18', 'RESERVOIR_CRUISE', 'RESERVOIR_B_CRUISE', 'RESERVOIR_B_GATE_LEAN_DEG', 'FILL_B_LEAN_Y', 'FILL_B_JOIN_Y', 'LANE_CLEAR', 'FILL_A_LANE_Z', 'FILL_A_GATE_LEAD', 'FILL_A_GATE_LEAN_DEG', 'FILL_A_LANE_RUN', 'FILL_A_FALL_RUN', 'FILL_A_HOSE_DROP', 'FILL_A_HOSE_FALL_RUN', 'FILL_A_VALVE_DROP', 'FILL_A_VALVE_RETURN_RUN', 'FILL_A_BEARING_STRAIGHT', 'DRAW_A_CRUISE', 'DRAW_A_NECK_IN', 'DRAW_A_NECK_OUT', 'DRAW_A_APPROACH', 'DRAW_A_GATE_LEAD', 'DRAW_B_CRUISE', 'DRAW_B_APPROACH', 'DRAW_B_GATE_LEAD', 'DRAW_GATE_LEAN_DEG', '_fill_a_lane_y', '_fill_a_cap_z', '_fill_a_turn_y', '_fluid_14', '_on_cap', '_gate_lead', '_fluid_16', '_fluid_24', '_fluid_26', '_refrig_3', '_refrig_1', '_refrig_2', 'authored', '_AUTHORED', 'tubes', 'report'])
sys.modules[__name__].__class__ = _RustSurface
