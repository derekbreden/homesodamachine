"""Doc-sync driver for hardware/assembly/cold-core.md.

Run: tools/cad-venv/bin/python hardware/assembly/_cold_core_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'scripts'))
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
_hw = next((p for p in _here.parents if p.name == 'hardware'))
sys.path.insert(0, str(_hw / 'printed-parts' / 'cadlib'))
sys.path.insert(0, str(_hw / 'printed-parts' / 'cold-core'))
sys.path.insert(0, str(_hw / 'printed-parts' / 'enclosure' / 'enclosure'))
from _enclosure_datums import install as _scalar_datums
_scalar_datums()
from _cold_core_interface import attachment_xy_positions, deck_mounts, deck_mount_xy, co2_inlet_y, foam_cap_lid_vent_radius, foam_shell_outer_height, foam_cap_lid_height, foam_shell_rim_z, bottom_cap_height, bottom_pour_radius, forward_band_width, insert_length, insert_pocket_depth, insert_pocket_radius, lldpe_bend_radius, lldpe_tube_od, cap_conduit_shell_xy, outer_shell_x_length, outer_shell_y_length, port_hole_radius, reservoir_clearance, top_band_to_cap, wall_and_floor_thickness
sys.path.insert(0, str(_hw / 'printed-parts' / 'cold-core' / 'reservoir'))
from reservoir import insert_positions_for_side_plus_1
from _foam_cap import cap_face_z, stack_floor_z
from docgen import load_module
_coil_mandrel_gen = load_module('cold_core_coil_mandrel_gen', _hw / 'printed-parts' / 'cold-core' / 'coil-mandrel' / 'coil_mandrel.py')
_coil_gen = load_module('cold_core_coil_gen', _hw / 'cold-core-layout' / '_coil.py')
_reed_bridge_gen = load_module('cold_core_reed_bridge_gen', _hw / 'printed-parts' / 'cold-core' / 'reed-bridge' / 'reed_bridge.py')
import _port_cuts

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        'attachment_xy_positions': attachment_xy_positions,
        'insert_positions_for_side_plus_1': insert_positions_for_side_plus_1,
        'deck_mount_positions': [deck_mount_xy(n) for n in deck_mounts],
        '_coil_mandrel_gen.groove_depth': _coil_mandrel_gen.groove_depth,
        '_coil_mandrel_gen.mandrel_od': _coil_mandrel_gen.mandrel_od,
        '_coil_mandrel_gen.carbonator_od': _coil_mandrel_gen.carbonator_od,
        '_coil_mandrel_gen.net_undersize': _coil_mandrel_gen.net_undersize,
        '_coil_mandrel_gen.wind_length': _coil_mandrel_gen.wind_length,
        '_coil_gen.TOTAL_WRAPS': _coil_gen.TOTAL_WRAPS,
        '_coil_gen.PITCH': _coil_gen.PITCH,
        '_coil_mandrel_gen.fitted_wrap_length': _coil_mandrel_gen.fitted_wrap_length,
        '_coil_gen.wrap_length()': _coil_gen.wrap_length(),
        "_coil_mandrel_gen.stub_allowance['inlet']": _coil_mandrel_gen.stub_allowance['inlet'],
        "_coil_mandrel_gen.stub_allowance['outlet']": _coil_mandrel_gen.stub_allowance['outlet'],
        "_coil_mandrel_gen.stub_protrusion['inlet']": _coil_mandrel_gen.stub_protrusion['inlet'],
        "_coil_mandrel_gen.stub_protrusion['outlet']": _coil_mandrel_gen.stub_protrusion['outlet'],
        '_coil_mandrel_gen.carbonators_per_roll': _coil_mandrel_gen.carbonators_per_roll,
        '_coil_gen.cut_length()': _coil_gen.cut_length(),
        '_coil_mandrel_gen.tail_inlet_y': _coil_mandrel_gen.tail_inlet_y,
        '_coil_mandrel_gen.tail_outlet_y': _coil_mandrel_gen.tail_outlet_y,
        'bottom_cap_height': bottom_cap_height,
        'wall_and_floor_thickness': wall_and_floor_thickness,
        'foam_shell_rim_z': foam_shell_rim_z,
        'foam_shell_outer_height': foam_shell_outer_height,
        'foam_cap_lid_height': foam_cap_lid_height,
        'bottom_pour_radius': bottom_pour_radius,
        'foam_cap_lid_vent_radius': foam_cap_lid_vent_radius,
        'insert_pocket_radius': insert_pocket_radius,
        'insert_length': insert_length,
        'insert_pocket_depth': insert_pocket_depth,
        'port_hole_radius': port_hole_radius,
        'co2_inlet_y': co2_inlet_y,
        'top_band_to_cap': top_band_to_cap,
        'lldpe_bend_radius': lldpe_bend_radius,
        'forward_band_width': forward_band_width,
        'cap_conduit_shell_xy("reed-cable-a")[0]': cap_conduit_shell_xy("reed-cable-a")[0],
        'cap_conduit_shell_xy("reed-cable-a")[1]': cap_conduit_shell_xy("reed-cable-a")[1],
        'reservoir_clearance': reservoir_clearance,
        'outer_shell_x_length': outer_shell_x_length,
        'outer_shell_y_length': outer_shell_y_length,
        'cap_face_z': cap_face_z,
        'stack_floor_z': stack_floor_z,
        '_reed_bridge_gen.low_level_z': _reed_bridge_gen.low_level_z,
        '_reed_bridge_gen.high_level_z': _reed_bridge_gen.high_level_z,
        '_reed_bridge_gen.reed_low_z': _reed_bridge_gen.reed_low_z,
        '_reed_bridge_gen.reed_high_z': _reed_bridge_gen.reed_high_z,
        '_reed_bridge_gen.inter_wrap_clear': _reed_bridge_gen.inter_wrap_clear,
        '_reed_bridge_gen.bridge_z_bottom': _reed_bridge_gen.bridge_z_bottom,
        '_reed_bridge_gen.pocket_depth': _reed_bridge_gen.pocket_depth,
        '_port_cuts.co2_inlet_y': _port_cuts.co2_inlet_y,
        '_port_cuts.front_face_port_z': _port_cuts.front_face_port_z,
        'lldpe_tube_od': lldpe_tube_od,
    }


globals().update(_evaluate('cold-core', _inputs())["exports"])


def main():
    _update('cold-core', _inputs())


if __name__ == "__main__":
    main()
