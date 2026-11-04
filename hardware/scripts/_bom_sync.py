"""Doc-sync driver for hardware/ledger/bom.md.

Run: tools/cad-venv/bin/python hardware/scripts/_bom_sync.py
Use --only-bom to update the BOM without rewriting the labor ledger.
"""

import argparse
import json
import sys
from decimal import Decimal
from pathlib import Path

_here = Path(__file__).resolve().parent  # = hardware/scripts/
sys.path.insert(0, str(_here.parent / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core" / "reservoir"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet" / "faucet-shell"))
sys.path.insert(0, str(_here.parent / "reference" / "beduan-solenoid"))
sys.path.insert(0, str(_here.parent / "manifold-layout"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "enclosure" / "enclosure"))
sys.path.insert(0, str(_here.parent / "reference" / "compressor"))
for _scalar_path in ('reference/teyleten-relay', 'reference/meanwell-irm90',
                     'reference/iec-c14-inlet', 'reference/digiten-flow-sensor',
                     'printed-parts/electronics/pcba-tray'):
    sys.path.insert(0, str(_here.parent / _scalar_path))
sys.path.insert(0, str(_here.parent / "printed-parts" / "enclosure" / "pump-dock"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _enclosure_datums import load as _enclosure_numbers
_enc = _enclosure_numbers()

from _cold_core_interface import (attachment_xy_positions, cap_anchors,
                                  cap_cradles, deck_mounts,
                                  deck_mount_xy, deck_mount_reach, deck_mount_bore_depth)
from _reed_channels import reeds_per_reservoir
from docgen import load_module

from reservoir import insert_positions_for_side_plus_1
from faucet_shell import base_pod_centers

import manifold_layout as ml
import _facts
import compressor as _compressor
from _cadq_export import note_read
note_read(_here.parent / 'manifold-layout/enclosure_assembly.py')
for _source in _facts.sources():
    if Path(_source).suffix in ('.py', '.rs', '.json', '.toml', '.lock', '.yaml', '.yml'):
        note_read(_here.parents[1] / _source)
import _box_spec
import _fixed_pump_mount
from materialize_pump_cartridge import _declared_box
import digiten_flow_sensor as _digiten  # likewise — the arm the meter's anchors bore for
import iec_c14_inlet as _c14  # likewise — the inlet whose flange the +Y wall's tunnel bores for
import meanwell_irm90 as _psu  # the west-wall supply and its mounting ears
import teyleten_relay as _relay  # likewise
import pcba_tray as _pcba  # likewise
import _above_core_shell as _selected_shell
import _above_core_mounts as _selected_cap
import _reservoir_a_anchors
import above_core as _above_core
import above_core_bom as _above_core_bom

from _ledger_rust import call, main as _main

_wire_schedule = load_module('bom_wire_schedule', _here.parent / 'wiring/_ac_wiring_schedule_sync.py')
_coil_mandrel_gen = load_module('bom_coil_mandrel_gen', _here.parent / 'printed-parts/cold-core/coil-mandrel/coil_mandrel.py')
_coil_gen = load_module('bom_coil_gen', _here.parent / 'cold-core-layout/_coil.py')
_routes_gen = load_module('bom_internal_routes_gen', _here.parent / 'printed-parts/cold-core/_internal_routes.py')
_faucet_gen = load_module('bom_faucet_assembly_gen', _here.parent / 'faucet-layout/faucet_assembly.py')

def _inputs():
    facts = _facts.read()
    pump_box, _bounds, _path = _declared_box(_box_spec, _enc)
    return {
        'placed': list(facts.pack['placed']),
        'floor_bosses': facts.box['floor_bosses'],
        'cond_mount': facts.box['cond_mount'],
        'bodies': list(facts.bodies),
        'collet_holes': facts.box['collet_plate']['holes'],
        'wire': {name:getattr(_wire_schedule,name) for name in (
            'len_mid_mm','len_short_2_mm','len_short_mm','len_dc1_mm',
            'len_dc2_mm','len_opening_join_mm')},
        'coil': {'pitch':_coil_gen.PITCH,'wrap':_coil_gen.wrap_length(),
                 'cut':_coil_gen.cut_length(),'spare_ft':_coil_gen.roll_spare_ft()},
        'mandrel': {name:getattr(_coil_mandrel_gen,name) for name in (
            'net_undersize','mandrel_wrap_length','stub_allowance','carbonators_per_roll')},
        'prv_segments':_routes_gen.route_segments(_routes_gen.routes['prv-vent'],_routes_gen.route_bend_radius),
        'faucet': {'flavor_cut':_faucet_gen.flavor_cut_length,'soda_cut':_faucet_gen.soda_faucet_cut_length},
        'fluid_runs':[dict(id=r.id,length=r.length) for r in facts.runs],
        'manifold': {'positions':list(ml.P),'purchased_tees':list(ml.PURCHASED_TEES),
                     'lower_connections':ml.LOWER_CONNECTIONS,'pump_junctions':ml.PUMP_JUNCTIONS,
                     'pump_tube_cut':ml.PUMP_TUBE_CUT},
        'reservoir_a_anchors':_reservoir_a_anchors.datums(),
        'meter_tie_routes':_selected_cap.meter_tie_routes(),
        'union_tie_routes':_selected_cap.union_tie_routes(),
        'union_support_datums':_selected_cap.union_support_datums(),
        'attachments':attachment_xy_positions,
        'reservoir_positions':insert_positions_for_side_plus_1,
        'deck_mount_xy':{name:deck_mount_xy(name) for name in deck_mounts},
        'pcba_screw_len':deck_mounts['pcba'].screw,
        'pcba_bore':deck_mount_bore_depth,
        'pcba_screw_reach':deck_mount_reach('pcba'),
        'reeds_per_reservoir':reeds_per_reservoir,
        'base_pod_centers':base_pod_centers,
        'union_elbows':_above_core_bom.union_elbow_names(),
        'core_union_elbows':_above_core_bom.core_union_elbow_names(),
        'stem_elbows':_above_core_bom.stem_elbow_names(),
        'core_stem_elbows':_above_core_bom.core_stem_elbow_names(),
        'above_core_parts':list(_above_core.specification()['parts']),
        'psu_fasteners':_selected_shell.psu_fastener_plan(),
        'relay_fasteners':_selected_shell.relay_fastener_plan(),
        'c14_fasteners':_selected_shell.c14_fastener_plan(),
        'c14_panel_screws':_c14.panel_screws(),
        'pump_fasteners':_fixed_pump_mount.fasteners(_enc,pump_box),
        'seam_rods':_enc.y_stack_rods(facts.box['inner']),
        'funnel_fasteners':_enc._funnel_frame_part.fastener_datums(),
        'cap_cradles':cap_cradles,
        'heatset_len':_enc.heatset_len,
        'psu_ledge_h':_psu.ledge_h,
        'pcba_thickness':_pcba._thickness,
        'relay_pcb_t':_relay.pcb_t,
        'c14_flange_t':_c14.FLANGE_T,
        'c14_rim_proud':_c14.RIM_PROUD,
        'display_angle':_enc._display_wings.ANGLE,
        'compressor_mount_ligament':_compressor.MOUNT_LIGAMENT,
        'compressor_mount_d':_compressor.MOUNT_D,
        'floor_grommet_squeeze':facts.constants.FLOOR_GROMMET_SQUEEZE,
    }

_INPUTS = _inputs()
_COUNTS = call('bom_sync.counts', inputs=_INPUTS)
for _name, _value in _COUNTS.items():
    globals()[_name] = Decimal(_value) if isinstance(_value, str) else _value


def pack_line_cost(quantity, pack_price, pack_quantity):
    return call('bom_sync.pack_cost', quantity=quantity, price=pack_price, count=pack_quantity)


def main(*, only_bom=False):
    _main('bom_sync.main', inputs=_INPUTS, only_bom=only_bom)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--only-bom', action='store_true', help='update only bom.md and its figure bindings')
    main(only_bom=parser.parse_args().only_bom)
