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
_compiled = _RustModule('enclosure_assembly')

def wago_step(*args, **kwargs):
    return _compiled.call('wago_step', *args, **kwargs)

def box(*args, **kwargs):
    return _compiled.call('box', *args, **kwargs)

def _shift(*args, **kwargs):
    return _compiled.call('_shift', *args, **kwargs)

def _turned(*args, **kwargs):
    return _compiled.call('_turned', *args, **kwargs)

def record_seat(*args, **kwargs):
    return _compiled.call('record_seat', *args, **kwargs)

def record_pump_dock_seats(*args, **kwargs):
    return _compiled.call('record_pump_dock_seats', *args, **kwargs)

def note_room(*args, **kwargs):
    return _compiled.call('note_room', *args, **kwargs)

def east_lane_free(*args, **kwargs):
    return _compiled.call('east_lane_free', *args, **kwargs)

def power_face_station(*args, **kwargs):
    return _compiled.call('power_face_station', *args, **kwargs)

def cap_face(*args, **kwargs):
    return _compiled.call('cap_face', *args, **kwargs)

def mq6_cradle(*args, **kwargs):
    return _compiled.call('mq6_cradle', *args, **kwargs)

def record_bound(*args, **kwargs):
    return _compiled.call('record_bound', *args, **kwargs)

def carry_enclosure_bounds(*args, **kwargs):
    return _compiled.call('carry_enclosure_bounds', *args, **kwargs)

def carry_stated_bounds(*args, **kwargs):
    return _compiled.call('carry_stated_bounds', *args, **kwargs)

def _core_frame(*args, **kwargs):
    return _compiled.call('_core_frame', *args, **kwargs)

def cap_xy(*args, **kwargs):
    return _compiled.call('cap_xy', *args, **kwargs)

def cradle_rows(*args, **kwargs):
    return _compiled.call('cradle_rows', *args, **kwargs)

def cradles_land(*args, **kwargs):
    return _compiled.call('cradles_land', *args, **kwargs)

def _valve_up(*args, **kwargs):
    return _compiled.call('_valve_up', *args, **kwargs)

def _bodies(*args, **kwargs):
    return _compiled.call('_bodies', *args, **kwargs)

def _tray_valve(*args, **kwargs):
    return _compiled.call('_tray_valve', *args, **kwargs)

def valve_tray_decks_from_bounds(*args, **kwargs):
    return _compiled.call('valve_tray_decks_from_bounds', *args, **kwargs)

def valve_tray_decks(*args, **kwargs):
    return _compiled.call('valve_tray_decks', *args, **kwargs)

def tray_name(*args, **kwargs):
    return _compiled.call('tray_name', *args, **kwargs)

def valve_tray_stations(*args, **kwargs):
    return _compiled.call('valve_tray_stations', *args, **kwargs)

def valve_tray_stations_from_bounds(*args, **kwargs):
    return _compiled.call('valve_tray_stations_from_bounds', *args, **kwargs)

def _valve_tray_stations(*args, **kwargs):
    return _compiled.call('_valve_tray_stations', *args, **kwargs)

def _pump_up(*args, **kwargs):
    return _compiled.call('_pump_up', *args, **kwargs)

def pump_tray_seats(*args, **kwargs):
    return _compiled.call('pump_tray_seats', *args, **kwargs)

def pump_tray_seats_from_bounds(*args, **kwargs):
    return _compiled.call('pump_tray_seats_from_bounds', *args, **kwargs)

def pump_tray_stations(*args, **kwargs):
    return _compiled.call('pump_tray_stations', *args, **kwargs)

def collet_plate_spec(*args, **kwargs):
    return _compiled.call('collet_plate_spec', *args, **kwargs)

def vent_chase(*args, **kwargs):
    return _compiled.call('vent_chase', *args, **kwargs)

def core_holds(*args, **kwargs):
    return _compiled.call('core_holds', *args, **kwargs)

def refrigerant_mates(*args, **kwargs):
    return _compiled.call('refrigerant_mates', *args, **kwargs)

def pump_mount_rows(*args, **kwargs):
    return _compiled.call('pump_mount_rows', *args, **kwargs)

def cap_anchor(*args, **kwargs):
    return _compiled.call('cap_anchor', *args, **kwargs)

def cap_side_anchor(*args, **kwargs):
    return _compiled.call('cap_side_anchor', *args, **kwargs)

def cap_conduit(*args, **kwargs):
    return _compiled.call('cap_conduit', *args, **kwargs)

def water_pump_west_limit(*args, **kwargs):
    return _compiled.call('water_pump_west_limit', *args, **kwargs)

def water_pump_port_lane_limit(*args, **kwargs):
    return _compiled.call('water_pump_port_lane_limit', *args, **kwargs)

def bulkhead_seat_y(*args, **kwargs):
    return _compiled.call('bulkhead_seat_y', *args, **kwargs)

def bulkhead_mouth_y(*args, **kwargs):
    return _compiled.call('bulkhead_mouth_y', *args, **kwargs)

def y_wall_ports(*args, **kwargs):
    return _compiled.call('y_wall_ports', *args, **kwargs)

def ring_name(*args, **kwargs):
    return _compiled.call('ring_name', *args, **kwargs)

def word_name(*args, **kwargs):
    return _compiled.call('word_name', *args, **kwargs)

def port_clamp_stack(*args, **kwargs):
    return _compiled.call('port_clamp_stack', *args, **kwargs)

def port_pocket_d(*args, **kwargs):
    return _compiled.call('port_pocket_d', *args, **kwargs)

def port_pocket_rise(*args, **kwargs):
    return _compiled.call('port_pocket_rise', *args, **kwargs)

def wall_stations(*args, **kwargs):
    return _compiled.call('wall_stations', *args, **kwargs)

def y_wall_field(*args, **kwargs):
    return _compiled.call('y_wall_field', *args, **kwargs)

def customer_tube_name(*args, **kwargs):
    return _compiled.call('customer_tube_name', *args, **kwargs)

def collar_name(*args, **kwargs):
    return _compiled.call('collar_name', *args, **kwargs)

def collar_word_name(*args, **kwargs):
    return _compiled.call('collar_word_name', *args, **kwargs)

def nameplate_cut(*args, **kwargs):
    return _compiled.call('nameplate_cut', *args, **kwargs)

def west_interior_face(*args, **kwargs):
    return _compiled.call('west_interior_face', *args, **kwargs)

def west_exterior_face(*args, **kwargs):
    return _compiled.call('west_exterior_face', *args, **kwargs)

def west_seam_crown(*args, **kwargs):
    return _compiled.call('west_seam_crown', *args, **kwargs)

def flavor_storey(*args, **kwargs):
    return _compiled.call('flavor_storey', *args, **kwargs)

def panel_z(*args, **kwargs):
    return _compiled.call('panel_z', *args, **kwargs)

def digiten_anchors(*args, **kwargs):
    return _compiled.call('digiten_anchors', *args, **kwargs)

def tube_anchor_midpoint(*args, **kwargs):
    return _compiled.call('tube_anchor_midpoint', *args, **kwargs)

def tube_anchor_sites(*args, **kwargs):
    return _compiled.call('tube_anchor_sites', *args, **kwargs)

def body_anchors(*args, **kwargs):
    return _compiled.call('body_anchors', *args, **kwargs)

def cap_tube_anchors(*args, **kwargs):
    return _compiled.call('cap_tube_anchors', *args, **kwargs)

def lid_cap_stations(*args, **kwargs):
    return _compiled.call('lid_cap_stations', *args, **kwargs)

def reservoir_a_anchor_sites(*args, **kwargs):
    return _compiled.call('reservoir_a_anchor_sites', *args, **kwargs)

def reservoir_a_developed_stations(*args, **kwargs):
    return _compiled.call('reservoir_a_developed_stations', *args, **kwargs)

def unsupported_spans(*args, **kwargs):
    return _compiled.call('unsupported_spans', *args, **kwargs)

def _on_leg(*args, **kwargs):
    return _compiled.call('_on_leg', *args, **kwargs)

def interior_ceiling(*args, **kwargs):
    return _compiled.call('interior_ceiling', *args, **kwargs)

def c14_mount_half(*args, **kwargs):
    return _compiled.call('c14_mount_half', *args, **kwargs)

def c14_seat_y(*args, **kwargs):
    return _compiled.call('c14_seat_y', *args, **kwargs)

def c14_stations(*args, **kwargs):
    return _compiled.call('c14_stations', *args, **kwargs)

def c14_cutout(*args, **kwargs):
    return _compiled.call('c14_cutout', *args, **kwargs)

def keystone_cutout(*args, **kwargs):
    return _compiled.call('keystone_cutout', *args, **kwargs)

def co2_inlet_mouth_y(*args, **kwargs):
    return _compiled.call('co2_inlet_mouth_y', *args, **kwargs)

def co2_wall_port(*args, **kwargs):
    return _compiled.call('co2_wall_port', *args, **kwargs)

def _manifold(*args, **kwargs):
    return _compiled.call('_manifold', *args, **kwargs)

def east_wall_seat(*args, **kwargs):
    return _compiled.call('east_wall_seat', *args, **kwargs)

def floor_mounts(*args, **kwargs):
    return _compiled.call('floor_mounts', *args, **kwargs)

def _wago_skirt(*args, **kwargs):
    return _compiled.call('_wago_skirt', *args, **kwargs)

def wago_row_reach(*args, **kwargs):
    return _compiled.call('wago_row_reach', *args, **kwargs)

def wago_wells(*args, **kwargs):
    return _compiled.call('wago_wells', *args, **kwargs)

def asse_sections(*args, **kwargs):
    return _compiled.call('asse_sections', *args, **kwargs)

def asse_ties(*args, **kwargs):
    return _compiled.call('asse_ties', *args, **kwargs)

def asse_reach_down(*args, **kwargs):
    return _compiled.call('asse_reach_down', *args, **kwargs)

def _asse_section_drops(*args, **kwargs):
    return _compiled.call('_asse_section_drops', *args, **kwargs)

def asse_cradle(*args, **kwargs):
    return _compiled.call('asse_cradle', *args, **kwargs)

def anchor_rows(*args, **kwargs):
    return _compiled.call('anchor_rows', *args, **kwargs)

def _whole(*args, **kwargs):
    return _compiled.call('_whole', *args, **kwargs)

def manifold_carry(*args, **kwargs):
    return _compiled.call('manifold_carry', *args, **kwargs)

def manifold_pump_trays(*args, **kwargs):
    return _compiled.call('manifold_pump_trays', *args, **kwargs)

def manifold_references(*args, **kwargs):
    return _compiled.call('manifold_references', *args, **kwargs)

def _with_manifold_rows(*args, **kwargs):
    return _compiled.call('_with_manifold_rows', *args, **kwargs)

def _contained_reliefs(*args, **kwargs):
    return _compiled.call('_contained_reliefs', *args, **kwargs)

def _enveloped_reliefs(*args, **kwargs):
    return _compiled.call('_enveloped_reliefs', *args, **kwargs)

def _level_reliefs(*args, **kwargs):
    return _compiled.call('_level_reliefs', *args, **kwargs)

def _full_depth_reliefs(*args, **kwargs):
    return _compiled.call('_full_depth_reliefs', *args, **kwargs)

def _minimum_depth_reliefs(*args, **kwargs):
    return _compiled.call('_minimum_depth_reliefs', *args, **kwargs)

def _asse_end_reliefs(*args, **kwargs):
    return _compiled.call('_asse_end_reliefs', *args, **kwargs)

def _connected_reliefs(*args, **kwargs):
    return _compiled.call('_connected_reliefs', *args, **kwargs)

def stand_anchors(*args, **kwargs):
    return _compiled.call('stand_anchors', *args, **kwargs)

def stand_wells(*args, **kwargs):
    return _compiled.call('stand_wells', *args, **kwargs)

def authored_anchor_corbels(*args, **kwargs):
    return _compiled.call('authored_anchor_corbels', *args, **kwargs)

def front_flank_reliefs_fine(*args, **kwargs):
    return _compiled.call('front_flank_reliefs_fine', *args, **kwargs)

def above_core_ceiling_reliefs(*args, **kwargs):
    return _compiled.call('above_core_ceiling_reliefs', *args, **kwargs)

def funnel_centre(*args, **kwargs):
    return _compiled.call('funnel_centre', *args, **kwargs)

def seat_off(*args, **kwargs):
    return _compiled.call('seat_off', *args, **kwargs)

def __getattr__(name):
    return _compiled.get(name)

def __dir__():
    return _compiled.names()

_rust_functions = frozenset(['wago_step', 'box', '_shift', '_turned', 'record_seat', 'record_pump_dock_seats', 'note_room', 'east_lane_free', 'power_face_station', 'cap_face', 'mq6_cradle', 'record_bound', 'carry_enclosure_bounds', 'carry_stated_bounds', '_core_frame', 'cap_xy', 'cradle_rows', 'cradles_land', '_valve_up', '_bodies', '_tray_valve', 'valve_tray_decks_from_bounds', 'valve_tray_decks', 'tray_name', 'valve_tray_stations', 'valve_tray_stations_from_bounds', '_valve_tray_stations', '_pump_up', 'pump_tray_seats', 'pump_tray_seats_from_bounds', 'pump_tray_stations', 'collet_plate_spec', 'vent_chase', 'core_holds', 'refrigerant_mates', 'pump_mount_rows', 'cap_anchor', 'cap_side_anchor', 'cap_conduit', 'water_pump_west_limit', 'water_pump_port_lane_limit', 'bulkhead_seat_y', 'bulkhead_mouth_y', 'y_wall_ports', 'ring_name', 'word_name', 'port_clamp_stack', 'port_pocket_d', 'port_pocket_rise', 'wall_stations', 'y_wall_field', 'customer_tube_name', 'collar_name', 'collar_word_name', 'nameplate_cut', 'west_interior_face', 'west_exterior_face', 'west_seam_crown', 'flavor_storey', 'panel_z', 'digiten_anchors', 'tube_anchor_midpoint', 'tube_anchor_sites', 'body_anchors', 'cap_tube_anchors', 'lid_cap_stations', 'reservoir_a_anchor_sites', 'reservoir_a_developed_stations', 'unsupported_spans', '_on_leg', 'interior_ceiling', 'c14_mount_half', 'c14_seat_y', 'c14_stations', 'c14_cutout', 'keystone_cutout', 'co2_inlet_mouth_y', 'co2_wall_port', '_manifold', 'east_wall_seat', 'floor_mounts', '_wago_skirt', 'wago_row_reach', 'wago_wells', 'asse_sections', 'asse_ties', 'asse_reach_down', '_asse_section_drops', 'asse_cradle', 'anchor_rows', '_whole', 'manifold_carry', 'manifold_pump_trays', 'manifold_references', '_with_manifold_rows', '_contained_reliefs', '_enveloped_reliefs', '_level_reliefs', '_full_depth_reliefs', '_minimum_depth_reliefs', '_asse_end_reliefs', '_connected_reliefs', 'stand_anchors', 'stand_wells', 'authored_anchor_corbels', 'front_flank_reliefs_fine', 'above_core_ceiling_reliefs', 'funnel_centre', 'seat_off'])
_rust_exports = frozenset(['annotations', 'Path', 'sys', '_here', '_hw', 'main', '_p', 'cq', 'collections', 'math', 'fits', '_boxes', '_above', '_stated', '_comp', '_enc', '_anchor_cap', '_funnel_frame', 'ml', '_asse', '_oad', '_mq6', '_foam', '_cci', '_keystone', '_jg', '_ring', '_np', '_tray', '_dock', '_split', '_drain_bulkhead', '_drain', '_neofit', '_wr1110', '_gas_chain', '_digiten', '_card', 'PSU_STEP', 'PCBA_STEP', 'RELAY_STEP', 'WAGO_STEPS', 'wago_step', 'WAGO_POLES', 'CLUSTER_WAGOS', 'FOAM_STEP', 'FUNNEL_STEP', 'FUNNEL_COVER_STEP', 'FOAM_YAW', 'COMPRESSOR_YAW', 'FUNNEL_ROT', 'box', '_shift', '_turned', 'Seat', 'SEATS', '_FACE', 'record_seat', 'record_pump_dock_seats', 'note_room', 'BASE_YAW', 'COMPRESSOR_FRONT', 'PACK_CROWN', 'east_lane_free', 'FUSE_TURN', 'FUSE_FACE_NORMAL', 'power_face_station', 'CORE', 'cap_face', 'MQ6_Y0', 'mq6_cradle', 'Bound', 'BOUNDS', 'record_bound', 'carry_enclosure_bounds', 'carry_stated_bounds', 'CRADLE_TOL', '_core_frame', 'cap_xy', 'cradle_rows', 'cradles_land', 'TRAY_SEAT_SLIP', '_valve_up', '_bodies', '_tray_valve', 'valve_tray_decks_from_bounds', 'valve_tray_decks', 'tray_name', 'valve_tray_stations', 'valve_tray_stations_from_bounds', '_valve_tray_stations', 'PUMP_TRAY_SLIP', '_pump_up', 'pump_tray_seats', 'pump_tray_seats_from_bounds', 'pump_tray_stations', 'collet_plate_spec', 'COND_PROBE_INSET', 'COND_AIR_INSET', '_COND_UNPRINTED', '_CORE_HOLD_EAST_EDGE', 'CORE_HOLD_LANES', 'vent_chase', 'core_holds', 'FRONT_RIDERS', 'CORE_RIDERS', 'CORE_RIDE_LATER', 'CORE_RIDE_RUNS', 'BEDDED_TOL', 'JOINT_STATIONS', 'REFRIGERANT_IDS', 'MADE_BY_MATE', 'MADE_BY_TUBE', 'JOINT_TOL', 'refrigerant_mates', 'MOUNT_TOL', 'pump_mount_rows', 'cap_anchor', 'cap_side_anchor', 'cap_conduit', 'water_pump_west_limit', 'water_pump_port_lane_limit', 'DISCHARGE_ELBOW_DIP', 'PUMP_ELBOWS', 'CHAIN_SEAT_SLIP', 'PORT_HOLE_SLIP', 'bulkhead_seat_y', 'bulkhead_mouth_y', 'y_wall_ports', 'Y_WALL_FITTINGS', 'ring_name', 'word_name', 'BULKHEAD_RING_SLIP', 'BULKHEAD_RING_RIM', 'PORT_BOSS_PROUD', 'port_clamp_stack', 'port_pocket_d', 'port_pocket_rise', 'wall_stations', 'y_wall_field', 'CUSTOMER_TUBE_STATIONS', 'COLLAR_OFF_COLLET', 'COLLAR_TUBE_TAIL', 'customer_tube_name', 'collar_name', 'collar_word_name', 'NAMEPLATE_MARGIN', 'NAMEPLATE', 'NAMEPLATE_INK', 'NAMEPLATE_PSU_CLEAR', 'NAMEPLATE_CAP_CLEAR', 'nameplate_cut', 'DECK_CLEAR', 'DECK_FALL_LIMIT', 'PORT_NUT_GAP', 'PORT_DECK_EXTRA', 'PORT_HARDWARE_PITCH', 'PORT_FIELD_PITCH', 'PORT_PITCH', '_port_stack', '_n', '_fit', '_r', '_w', '_f', '_bare', '_port', '_t', '_stack', 'west_interior_face', 'west_exterior_face', 'west_seam_crown', 'PORT_LANE_CLEAR', 'PORT_WEST_COLUMN', 'PANEL_X', 'PORT_FOOT_CLEAR', 'FLAVOR_STOREY_DROP', 'flavor_storey', 'PANEL_ON_GATE_LANE', 'panel_z', 'DIGITEN_STEP', 'DIGITEN_TURN', 'CARB_2', 'DIGITEN_CEILING_CLEAR', 'DIGITEN_WEST_SET', 'DIGITEN_SEAT_SLIP', 'digiten_anchors', 'TUBE_ANCHOR_SPAN', 'TUBE_ANCHOR_SLIP', 'TUBE_ANCHOR_SITES', 'TUBE_ANCHOR_END_FORMS', 'ANCHOR_END_FORMS', 'FLAVOR_B_ANCHOR_WELL_CLEAR', 'TUBE_ANCHOR_CLOSURES', 'ANCHOR_CLOSURES', 'tube_anchor_midpoint', 'tube_anchor_sites', 'BODY_ANCHOR_SLIP', 'BODY_ANCHOR_SITES', 'BODY_ANCHOR_END_FORMS', 'body_anchors', 'cap_tube_anchors', 'lid_cap_stations', 'reservoir_a_anchor_sites', 'reservoir_a_developed_stations', 'unsupported_spans', '_on_leg', 'ASSE_TIE_T', 'ASSE_TIE_CLEAR', 'interior_ceiling', 'C14_STEP', 'c14_mount_half', 'C14_STATION', 'c14_seat_y', 'c14_stations', 'c14_cutout', 'CO2_CHAIN_TURN', 'keystone_cutout', 'CO2_REGULATOR_SETBACK', 'CO2_CHECK_SIDE_OFFSET', 'CO2_CHECK_FORWARD_OFFSET', 'co2_inlet_mouth_y', 'co2_wall_port', 'STANDALONE', '_manifold', '_ROUTED', 'east_wall_seat', 'FLOOR_BOSS_SLIP', 'FLOOR_GROMMET_SQUEEZE', 'floor_mounts', 'PSU_TURN', 'PSU_AFT_WIRE_ALLOWANCE', 'PSU_RELAY_BODY_GAP', 'RELAY_BOARD_BODY_GAP', 'PCBA_TURN', 'WIRED_CLEAR', 'RELAY_TURN', 'RELAY1_CORBEL_LIFT', 'WAGO_TURN', 'WAGO_TURN_WEST', 'WAGO_CORBEL_FLOOR_CLEAR', '_wago_skirt', 'wago_row_reach', 'wago_wells', 'ASSE1022_YAW', 'ASSE_SEAT_SLIP', 'ASSE_STEP_SLIP', 'asse_sections', 'ASSE_TIE_VENT_CLEAR', 'ASSE_TIE_NECK_ALLOWANCE_D', 'asse_ties', 'asse_reach_down', '_asse_section_drops', 'asse_cradle', 'anchor_rows', 'SPLIT_TURN', 'FLAVOR_STEP', 'BOWL_CLEAR', 'WATER_2', 'SPLIT_FLANK_OFFSET', '_whole', 'PACK_Y', 'manifold_carry', 'manifold_pump_trays', 'manifold_references', '_with_manifold_rows', 'THROUGH_WALL', 'CEILING_RELIEF_PLAN_SLIP', 'CEILING_RELIEF_Z_CLEAR', 'CEILING_RELIEF_LEVEL_GROUPS', 'CEILING_RELIEF_LANE_BODIES', 'CEILING_RELIEF_MIN_DEPTH_BODIES', 'CEILING_RELIEF_CONNECTOR_PAIRS', 'CEILING_RELIEF_CONNECTOR_ENTRY', 'CEILING_RELIEF_ENVELOPE_BODIES', '_contained_reliefs', '_enveloped_reliefs', '_level_reliefs', '_full_depth_reliefs', '_minimum_depth_reliefs', '_asse_end_reliefs', '_connected_reliefs', 'WEDGE_CLEAR', 'WELL_COLUMNS', 'KEPT_WEDGES', 'stand_anchors', 'stand_wells', '_PLAN_INSET', 'authored_anchor_corbels', 'front_flank_reliefs_fine', 'above_core_ceiling_reliefs', 'funnel_centre', 'COVER_ORIGIN', 'RIDGE_REACH', 'SEAT_TOL', 'NOT_A_BODY', 'seat_off'])
sys.modules[__name__].__class__ = _RustSurface

def main():
    import _machine_layout
    return _machine_layout.main()

if __name__ == '__main__':
    main()
