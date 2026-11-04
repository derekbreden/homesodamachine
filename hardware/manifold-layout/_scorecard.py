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
_compiled = _RustModule('_scorecard')

class _DeferredModule:
    def __init__(*args, **kwargs):
        return _compiled.call('_DeferredModule.__init__', *args, **kwargs)
    def __getattr__(*args, **kwargs):
        return _compiled.call('_DeferredModule.__getattr__', *args, **kwargs)

class _PlacedShapes(Mapping):
    def __init__(*args, **kwargs):
        return _compiled.call('_PlacedShapes.__init__', *args, **kwargs)
    def __iter__(*args, **kwargs):
        return _compiled.call('_PlacedShapes.__iter__', *args, **kwargs)
    def __len__(*args, **kwargs):
        return _compiled.call('_PlacedShapes.__len__', *args, **kwargs)
    def __contains__(*args, **kwargs):
        return _compiled.call('_PlacedShapes.__contains__', *args, **kwargs)
    def __getitem__(*args, **kwargs):
        return _compiled.call('_PlacedShapes.__getitem__', *args, **kwargs)

@dataclass
class Connection:
    id: str
    kind: str
    frm: str
    to: str
    made: str = 'not drawn'
    blocked: str = ''
    note: str = ''
    @property
    def routed(*args, **kwargs):
        return _compiled.call('Connection.routed', *args, **kwargs)

@dataclass
class Scorecard:
    checks: list
    bends: list
    conns: list
    sizes: list
    @property
    def gates_pass(*args, **kwargs):
        return _compiled.call('Scorecard.gates_pass', *args, **kwargs)

def pack_bodies(*args, **kwargs):
    return _compiled.call('pack_bodies', *args, **kwargs)

def _placed_sources(*args, **kwargs):
    return _compiled.call('_placed_sources', *args, **kwargs)

def _split_placed(*args, **kwargs):
    return _compiled.call('_split_placed', *args, **kwargs)

def _population_names(*args, **kwargs):
    return _compiled.call('_population_names', *args, **kwargs)

def rides_hold(*args, **kwargs):
    return _compiled.call('rides_hold', *args, **kwargs)

def _selected_mounts(*args, **kwargs):
    return _compiled.call('_selected_mounts', *args, **kwargs)

def derived_mounts(*args, **kwargs):
    return _compiled.call('derived_mounts', *args, **kwargs)

def mounts(*args, **kwargs):
    return _compiled.call('mounts', *args, **kwargs)

def fastened_by(*args, **kwargs):
    return _compiled.call('fastened_by', *args, **kwargs)

def tees_land_held(*args, **kwargs):
    return _compiled.call('tees_land_held', *args, **kwargs)

def never_holds(*args, **kwargs):
    return _compiled.call('never_holds', *args, **kwargs)

def made_of(*args, **kwargs):
    return _compiled.call('made_of', *args, **kwargs)

def load_connections(*args, **kwargs):
    return _compiled.call('load_connections', *args, **kwargs)

def need_of(*args, **kwargs):
    return _compiled.call('need_of', *args, **kwargs)

def need_clause(*args, **kwargs):
    return _compiled.call('need_clause', *args, **kwargs)

def bend_radii(*args, **kwargs):
    return _compiled.call('bend_radii', *args, **kwargs)

def _bounds(*args, **kwargs):
    return _compiled.call('_bounds', *args, **kwargs)

def pump_cap_contact(*args, **kwargs):
    return _compiled.call('pump_cap_contact', *args, **kwargs)

def _drain_seal_region(*args, **kwargs):
    return _compiled.call('_drain_seal_region', *args, **kwargs)

def drain_seal_contact(*args, **kwargs):
    return _compiled.call('drain_seal_contact', *args, **kwargs)

def _reducer_stem_region(*args, **kwargs):
    return _compiled.call('_reducer_stem_region', *args, **kwargs)

def reducer_port_contact(*args, **kwargs):
    return _compiled.call('reducer_port_contact', *args, **kwargs)

def elbow_stem_contact(*args, **kwargs):
    return _compiled.call('elbow_stem_contact', *args, **kwargs)

def _selected_mate_regions(*args, **kwargs):
    return _compiled.call('_selected_mate_regions', *args, **kwargs)

def selected_mate_contacts(*args, **kwargs):
    return _compiled.call('selected_mate_contacts', *args, **kwargs)

def fine_world(*args, **kwargs):
    return _compiled.call('fine_world', *args, **kwargs)

def _fine_read(*args, **kwargs):
    return _compiled.call('_fine_read', *args, **kwargs)

def _fine_masked(*args, **kwargs):
    return _compiled.call('_fine_masked', *args, **kwargs)

def _fine_pack_clashes(*args, **kwargs):
    return _compiled.call('_fine_pack_clashes', *args, **kwargs)

def _fine_pack_readings(*args, **kwargs):
    return _compiled.call('_fine_pack_readings', *args, **kwargs)

def _fine_contact(*args, **kwargs):
    return _compiled.call('_fine_contact', *args, **kwargs)

def pack_clashes(*args, **kwargs):
    return _compiled.call('pack_clashes', *args, **kwargs)

def _pack_closes(*args, **kwargs):
    return _compiled.call('_pack_closes', *args, **kwargs)

def _bed_fit(*args, **kwargs):
    return _compiled.call('_bed_fit', *args, **kwargs)

def run_world(*args, **kwargs):
    return _compiled.call('run_world', *args, **kwargs)

def selected_clearance_joints(*args, **kwargs):
    return _compiled.call('selected_clearance_joints', *args, **kwargs)

def _clearance_box(*args, **kwargs):
    return _compiled.call('_clearance_box', *args, **kwargs)

def _clearance_rows(*args, **kwargs):
    return _compiled.call('_clearance_rows', *args, **kwargs)

def _fine_run_clearance_pairs(*args, **kwargs):
    return _compiled.call('_fine_run_clearance_pairs', *args, **kwargs)

def _fine_clearance_rows(*args, **kwargs):
    return _compiled.call('_fine_clearance_rows', *args, **kwargs)

def _fine_clearance_pairs(*args, **kwargs):
    return _compiled.call('_fine_clearance_pairs', *args, **kwargs)

def _fine_part_clearances(*args, **kwargs):
    return _compiled.call('_fine_part_clearances', *args, **kwargs)

def part_clearances(*args, **kwargs):
    return _compiled.call('part_clearances', *args, **kwargs)

def run_clearances(*args, **kwargs):
    return _compiled.call('run_clearances', *args, **kwargs)

def _run_clearance_pairs(*args, **kwargs):
    return _compiled.call('_run_clearance_pairs', *args, **kwargs)

def anchored_pairs(*args, **kwargs):
    return _compiled.call('anchored_pairs', *args, **kwargs)

def lane_notes(*args, **kwargs):
    return _compiled.call('lane_notes', *args, **kwargs)

def _clearance_floor(*args, **kwargs):
    return _compiled.call('_clearance_floor', *args, **kwargs)

def _runs_drawn(*args, **kwargs):
    return _compiled.call('_runs_drawn', *args, **kwargs)

def _bend_radius(*args, **kwargs):
    return _compiled.call('_bend_radius', *args, **kwargs)

def _routed(*args, **kwargs):
    return _compiled.call('_routed', *args, **kwargs)

def _located(*args, **kwargs):
    return _compiled.call('_located', *args, **kwargs)

def _coverage(*args, **kwargs):
    return _compiled.call('_coverage', *args, **kwargs)

def _mounted(*args, **kwargs):
    return _compiled.call('_mounted', *args, **kwargs)

def seat_misses(*args, **kwargs):
    return _compiled.call('seat_misses', *args, **kwargs)

def seat_tol(*args, **kwargs):
    return _compiled.call('seat_tol', *args, **kwargs)

def _placed(*args, **kwargs):
    return _compiled.call('_placed', *args, **kwargs)

def _room_holds(*args, **kwargs):
    return _compiled.call('_room_holds', *args, **kwargs)

def loose_holds(*args, **kwargs):
    return _compiled.call('loose_holds', *args, **kwargs)

def _tube_anchored(*args, **kwargs):
    return _compiled.call('_tube_anchored', *args, **kwargs)

def _extent(*args, **kwargs):
    return _compiled.call('_extent', *args, **kwargs)

def size_rows(*args, **kwargs):
    return _compiled.call('size_rows', *args, **kwargs)

def _size_line(*args, **kwargs):
    return _compiled.call('_size_line', *args, **kwargs)

def build(*args, **kwargs):
    return _compiled.call('build', *args, **kwargs)

def _build(*args, **kwargs):
    return _compiled.call('_build', *args, **kwargs)

def to_dict(*args, **kwargs):
    return _compiled.call('to_dict', *args, **kwargs)

def write(*args, **kwargs):
    return _compiled.call('write', *args, **kwargs)

def report(*args, **kwargs):
    return _compiled.call('report', *args, **kwargs)

def selftest(*args, **kwargs):
    return _compiled.call('selftest', *args, **kwargs)

def main(*args, **kwargs):
    return _compiled.call('main', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['pack_bodies', '_placed_sources', '_split_placed', '_population_names', 'rides_hold', '_selected_mounts', 'derived_mounts', 'mounts', 'fastened_by', 'tees_land_held', 'never_holds', 'made_of', 'load_connections', 'need_of', 'need_clause', 'bend_radii', '_bounds', 'pump_cap_contact', '_drain_seal_region', 'drain_seal_contact', '_reducer_stem_region', 'reducer_port_contact', 'elbow_stem_contact', '_selected_mate_regions', 'selected_mate_contacts', 'fine_world', '_fine_read', '_fine_masked', '_fine_pack_clashes', '_fine_pack_readings', '_fine_contact', 'pack_clashes', '_pack_closes', '_bed_fit', 'run_world', 'selected_clearance_joints', '_clearance_box', '_clearance_rows', '_fine_run_clearance_pairs', '_fine_clearance_rows', '_fine_clearance_pairs', '_fine_part_clearances', 'part_clearances', 'run_clearances', '_run_clearance_pairs', 'anchored_pairs', 'lane_notes', '_clearance_floor', '_runs_drawn', '_bend_radius', '_routed', '_located', '_coverage', '_mounted', 'seat_misses', 'seat_tol', '_placed', '_room_holds', 'loose_holds', '_tube_anchored', '_extent', 'size_rows', '_size_line', 'build', '_build', 'to_dict', 'write', 'report', 'selftest', 'main'])
_rust_exports = frozenset(['annotations', 'json', 'math', 're', 'sys', 'ChainMap', 'Mapping', 'dataclass', 'field', 'cache', 'Path', '_here', '_hw', '_repo', '_p', 'Check', 'GRADE_BANDS', 'grade_of', 'verdict', '_DeferredModule', '_boxes', '_clearing', '_overlap', 'R', '_ports', '_gas_chain', '_TOPOLOGY', 'BEND_GRADE_PASS', 'DETAIL_MAX', 'CLEARANCE_FLOOR', 'REPORT_NEAR', 'ROOM_TOL', 'TUBE_PREFIXES', 'PUMP_ELBOW_BODIES', 'pack_bodies', '_placed_cache', '_placed_sources', '_PlacedShapes', '_split_placed', '_population_names', 'REFRIGERANT_SEGMENTS', 'WATER_SEGMENTS', 'CO2_SEGMENTS', 'CARB_SEGMENTS', 'PUMP_DOCK_PORTS', 'MOUNTS', 'RIDES', 'rides_hold', '_selected_mounts', 'derived_mounts', 'mounts', 'fastened_by', 'NEVER', 'TEE_LANDS', 'tees_land_held', 'never_holds', 'MADE_UP', 'TOUCHING_OK', 'MADE_AS', 'UNMADE', 'made_of', 'Connection', 'load_connections', 'need_of', 'need_clause', 'bend_radii', '_bounds', '_clash_cache', 'pump_cap_contact', '_drain_seal_region', 'drain_seal_contact', '_reducer_stem_region', 'reducer_port_contact', 'elbow_stem_contact', '_selected_mate_regions', 'selected_mate_contacts', 'fine_world', '_fine_read', '_fine_masked', '_fine_pack_clashes', '_fine_pack_readings', '_fine_contact', 'pack_clashes', '_pack_closes', '_bed_fit', 'run_world', 'selected_clearance_joints', '_clearance_box', '_clearance_rows', '_fine_run_clearance_pairs', '_fine_clearance_rows', '_fine_clearance_pairs', '_fine_part_clearances', 'part_clearances', 'run_clearances', '_run_clearance_pairs', 'anchored_pairs', 'lane_notes', '_clearance_floor', '_runs_drawn', '_bend_radius', '_routed', '_located', '_coverage', '_mounted', 'seat_misses', 'seat_tol', '_placed', '_room_holds', 'LOOSE', 'loose_holds', '_tube_anchored', 'MM_PER_INCH', '_extent', 'size_rows', '_size_line', 'Scorecard', '_card_cache', 'build', '_build', 'to_dict', 'write', 'report', 'selftest', 'main', 'v', 'p', 'part', 'w', 'name', 'tee', 'valve', 'x', 'y'])
sys.modules[__name__].__class__ = _RustSurface

if __name__ == '__main__':
    _compiled.main()
