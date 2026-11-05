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
_compiled = _RustModule('manifold_layout')

class Extents(NamedTuple):
    xmin: float
    ymin: float
    zmin: float
    xmax: float
    ymax: float
    zmax: float
    @property
    def xlen(*args, **kwargs):
        return _compiled.call('Extents.xlen', *args, **kwargs)
    @property
    def ylen(*args, **kwargs):
        return _compiled.call('Extents.ylen', *args, **kwargs)
    @property
    def zlen(*args, **kwargs):
        return _compiled.call('Extents.zlen', *args, **kwargs)
    @property
    def escape(*args, **kwargs):
        return _compiled.call('Extents.escape', *args, **kwargs)
    def __str__(*args, **kwargs):
        return _compiled.call('Extents.__str__', *args, **kwargs)

class Clash(NamedTuple):
    a: str
    b: str
    volume: float
    where: Extents

def valve_dirs(*args, **kwargs):
    return _compiled.call('valve_dirs', *args, **kwargs)

def tee_dirs(*args, **kwargs):
    return _compiled.call('tee_dirs', *args, **kwargs)

def barb_station(*args, **kwargs):
    return _compiled.call('barb_station', *args, **kwargs)

def body_name(*args, **kwargs):
    return _compiled.call('body_name', *args, **kwargs)

def _half(*args, **kwargs):
    return _compiled.call('_half', *args, **kwargs)

def lay_out(*args, **kwargs):
    return _compiled.call('lay_out', *args, **kwargs)

def fold_pt(*args, **kwargs):
    return _compiled.call('fold_pt', *args, **kwargs)

def fold_dir(*args, **kwargs):
    return _compiled.call('fold_dir', *args, **kwargs)

def two_arc_floor(*args, **kwargs):
    return _compiled.call('two_arc_floor', *args, **kwargs)

def sbend_solve(*args, **kwargs):
    return _compiled.call('sbend_solve', *args, **kwargs)

def source_offset(*args, **kwargs):
    return _compiled.call('source_offset', *args, **kwargs)

def step_cross(*args, **kwargs):
    return _compiled.call('step_cross', *args, **kwargs)

def hairpin_back(*args, **kwargs):
    return _compiled.call('hairpin_back', *args, **kwargs)

def source_valve_shift(*args, **kwargs):
    return _compiled.call('source_valve_shift', *args, **kwargs)

def source_cross(*args, **kwargs):
    return _compiled.call('source_cross', *args, **kwargs)

def source_step(*args, **kwargs):
    return _compiled.call('source_step', *args, **kwargs)

def bend_pt(*args, **kwargs):
    return _compiled.call('bend_pt', *args, **kwargs)

def bend_dir(*args, **kwargs):
    return _compiled.call('bend_dir', *args, **kwargs)

def hairpin_flat(*args, **kwargs):
    return _compiled.call('hairpin_flat', *args, **kwargs)

def hairpins_drawn(*args, **kwargs):
    return _compiled.call('hairpins_drawn', *args, **kwargs)

def sbend_flat(*args, **kwargs):
    return _compiled.call('sbend_flat', *args, **kwargs)

def fore_deck_aft_shift(*args, **kwargs):
    return _compiled.call('fore_deck_aft_shift', *args, **kwargs)

def fixed_aft_shift(*args, **kwargs):
    return _compiled.call('fixed_aft_shift', *args, **kwargs)

def enclosure_point(*args, **kwargs):
    return _compiled.call('enclosure_point', *args, **kwargs)

def authoring_point(*args, **kwargs):
    return _compiled.call('authoring_point', *args, **kwargs)

def enclosure_axis(*args, **kwargs):
    return _compiled.call('enclosure_axis', *args, **kwargs)

def authoring_axis(*args, **kwargs):
    return _compiled.call('authoring_axis', *args, **kwargs)

def pump_wall_fore_y(*args, **kwargs):
    return _compiled.call('pump_wall_fore_y', *args, **kwargs)

def pump_plumbing(*args, **kwargs):
    return _compiled.call('pump_plumbing', *args, **kwargs)

def _tee_ports(*args, **kwargs):
    return _compiled.call('_tee_ports', *args, **kwargs)

def fixed_tee_centers(*args, **kwargs):
    return _compiled.call('fixed_tee_centers', *args, **kwargs)

def _posed(*args, **kwargs):
    return _compiled.call('_posed', *args, **kwargs)

def port(*args, **kwargs):
    return _compiled.call('port', *args, **kwargs)

def port_axis(*args, **kwargs):
    return _compiled.call('port_axis', *args, **kwargs)

def branch_port(*args, **kwargs):
    return _compiled.call('branch_port', *args, **kwargs)

def _cross(*args, **kwargs):
    return _compiled.call('_cross', *args, **kwargs)

def elbow_pose(*args, **kwargs):
    return _compiled.call('elbow_pose', *args, **kwargs)

def _authored(*args, **kwargs):
    return _compiled.call('_authored', *args, **kwargs)

def lower_links(*args, **kwargs):
    return _compiled.call('lower_links', *args, **kwargs)

def lower_link_length(*args, **kwargs):
    return _compiled.call('lower_link_length', *args, **kwargs)

def _junction_at_author_x(*args, **kwargs):
    return _compiled.call('_junction_at_author_x', *args, **kwargs)

def return_exposed(*args, **kwargs):
    return _compiled.call('return_exposed', *args, **kwargs)

def return_cut(*args, **kwargs):
    return _compiled.call('return_cut', *args, **kwargs)

def _fore_segments(*args, **kwargs):
    return _compiled.call('_fore_segments', *args, **kwargs)

def fore_stub_length(*args, **kwargs):
    return _compiled.call('fore_stub_length', *args, **kwargs)

def stub_tip(*args, **kwargs):
    return _compiled.call('stub_tip', *args, **kwargs)

def factory_tail_runs(*args, **kwargs):
    return _compiled.call('factory_tail_runs', *args, **kwargs)

def factory_tail_length(*args, **kwargs):
    return _compiled.call('factory_tail_length', *args, **kwargs)

def runs(*args, **kwargs):
    return _compiled.call('runs', *args, **kwargs)

def fore_stubs(*args, **kwargs):
    return _compiled.call('fore_stubs', *args, **kwargs)

def turns_meet(*args, **kwargs):
    return _compiled.call('turns_meet', *args, **kwargs)

def _sum(*args, **kwargs):
    return _compiled.call('_sum', *args, **kwargs)

def _matrix(*args, **kwargs):
    return _compiled.call('_matrix', *args, **kwargs)

def _source_segments(*args, **kwargs):
    return _compiled.call('_source_segments', *args, **kwargs)

def numbers(*args, **kwargs):
    return _compiled.call('numbers', *args, **kwargs)

def _segment_numbers(*args, **kwargs):
    return _compiled.call('_segment_numbers', *args, **kwargs)

def mirror_off(*args, **kwargs):
    return _compiled.call('mirror_off', *args, **kwargs)

def dist(*args, **kwargs):
    return _compiled.call('dist', *args, **kwargs)

def skew_deg(*args, **kwargs):
    return _compiled.call('skew_deg', *args, **kwargs)

def main(*args, **kwargs):
    return _compiled.call('main', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['valve_dirs', 'tee_dirs', 'barb_station', 'body_name', '_half', 'lay_out', 'fold_pt', 'fold_dir', 'two_arc_floor', 'sbend_solve', 'source_offset', 'step_cross', 'hairpin_back', 'source_valve_shift', 'source_cross', 'source_step', 'bend_pt', 'bend_dir', 'hairpin_flat', 'hairpins_drawn', 'sbend_flat', 'fore_deck_aft_shift', 'fixed_aft_shift', 'enclosure_point', 'authoring_point', 'enclosure_axis', 'authoring_axis', 'pump_wall_fore_y', 'pump_plumbing', '_tee_ports', 'fixed_tee_centers', '_posed', 'port', 'port_axis', 'branch_port', '_cross', 'elbow_pose', '_authored', 'lower_links', 'lower_link_length', '_junction_at_author_x', 'return_exposed', 'return_cut', '_fore_segments', 'fore_stub_length', 'stub_tip', 'factory_tail_runs', 'factory_tail_length', 'runs', 'fore_stubs', 'turns_meet', '_sum', '_matrix', '_source_segments', 'numbers', '_segment_numbers', 'mirror_off', 'dist', 'skew_deg', 'main'])
_rust_exports = frozenset(['annotations', 'math', 'os', 'sys', 'Path', 'NamedTuple', '_here', '_hw', '_repo', '_tools', '_p', '_rust_part', 'vlv', 'kp', 'tee', 'ydiv', '_routing', '_bounds', '_enc_if', '_returns', 'ELBOW_STEP', 'TEE_STEP', 'KAMOER_STEP', 'PUMP_TURNS', 'VALVE_LEN', 'VALVE_PITCH', 'VALVE_PORT_Z', 'VALVE_TOP_Z', 'TEE_RUN', 'TEE_BRANCH', 'TUBE_D', 'STOCK', 'MIN_BEND', 'FLAVOR_SKEW', 'LINE_HUG', 'HEAD_W', 'MOTOR_D', 'BARB_PITCH', 'BARB_INSET', 'BUTT', 'CARRIER_DROP', 'INNER_LIMB_DROP', 'FORE_VALVE_RISE', 'FORE_STUB_GAP', 'FORE_VALVES', 'OUTER_AFT_X', 'CARRIER_DATUM_SHIFT', 'FIXED_TEE_AFT_SHIFT', 'AFT_DECK_AFT_SHIFT', 'AFT_PACK_RISE', 'OUTER_AFT_DROP', 'WORLD_LIFT', 'PACK_ORIGIN_Y', 'BARB_TO_PLATE', 'PUMP_STUB_PROJECTION', 'PUMP_TUBE_HELD', 'PUMP_TUBE_CUT', 'PUMP_BARBS_TO_BORE_FACE', 'BARB_PLATE_BERTH', 'PUMP_BARB_Z', 'PUMP_Y', 'BARB_STANDOFF', 'CROSSBAR', 'LIMB_PITCH', 'INNER_X', 'PUMP_DX', 'OUTER_X', 'OUTER_AFT_INSET', 'LIMB_STEP', 'BARB_LEAD_FLOOR', 'BARB_LEAD', 'DECK_Z', 'STUB', 'HINGE_Y', 'FOLD_CLEAR', 'ELBOW_LEG', 'C_COIL', 'C_PUMP_BOSS', 'C_PUMP_HEAD', 'C_PUMP_MOTOR', 'C_VALVE', 'M_JG_BLACK_PP', 'C_TEE', 'C_HEAD', 'C_BOSS', 'C_MOTOR', 'valve_dirs', 'tee_dirs', 'LIMBS', 'PUMPS', 'BARB_OF', 'PUMP_JUNCTIONS', 'FIXED_TEES', 'PUMP_VALVES', 'PUMP_PART_SUFFIX', 'CARRIER_TEES', 'CARRIER_RELEASE', 'CARRIER_SQUEEZE', 'CARRIER_CONNECTED', 'CARRIER_PARK', 'CARRIER_STATES', 'barb_station', 'body_name', '_half', 'lay_out', 'FLAT', 'P', 'PURCHASED_TEES', 'DECK_SEP', 'FOLD_BINDS', 'HINGE_Z', 'UPPER_Z', 'FOLD_AXIS', 'fold_pt', 'fold_dir', 'BEND_R', 'BEND_Y', 'BENT', 'SOURCE_TRAVEL', 'SOURCE_JOG', 'SOURCE_SPREAD', 'SOURCE_SLACK', 'HAIRPIN_OUT', 'HAIRPIN_TILT', 'two_arc_floor', 'sbend_solve', 'source_offset', 'step_cross', 'hairpin_back', 'source_valve_shift', 'source_cross', 'source_step', 'SHIFT', '_name', '_dx', '_dy', '_dz', 'bend_pt', 'bend_dir', 'hairpin_flat', 'hairpins_drawn', 'sbend_flat', 'fore_deck_aft_shift', 'fixed_aft_shift', 'enclosure_point', 'authoring_point', 'enclosure_axis', 'authoring_axis', 'pump_wall_fore_y', '_plumbing_cache', 'pump_plumbing', '_tee_ports', 'fixed_tee_centers', '_posed', 'port', 'port_axis', 'branch_port', 'JOINS', '_cross', 'elbow_pose', '_authored', 'lower_links', 'lower_link_length', '_junction_at_author_x', 'return_exposed', 'return_cut', '_fore_segments', 'fore_stub_length', 'stub_tip', 'factory_tail_runs', 'factory_tail_length', 'runs', 'RUNS', 'BARB_TUBE_LEN', 'PUMP_TUBE_PROJECTION', 'fore_stubs', 'FORE_STUBS', 'FORE_STUB_EXPOSED', 'turns_meet', 'SEGMENTS', 'QUARTERS', 'QUARTER_LEN', 'SBENDS', 'LOWER_CONNECTIONS', 'SPINE', 'MOUTHS', '_sum', '_matrix', '_source_segments', 'numbers', '_segment_numbers', 'Extents', 'Clash', 'TWINS', 'mirror_off', 'dist', 'skew_deg', 'main', 'name', 'offset', '_depth', 'n', 'cid', 'frm', '_to', 'how', 'p', 'what', 'body', 'end'])
sys.modules[__name__].__class__ = _RustSurface

if __name__ == '__main__':
    _compiled.main()
