"""Doc-sync driver for hardware/assembly/faucet-and-umbilical.md.

Run: tools/cad-venv/bin/python hardware/assembly/_faucet_and_umbilical_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'scripts'))
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
from docgen import load_module

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import update as _update


def _inputs():
    hardware_root = next((p for p in _here.parents if p.name == 'hardware'))
    sys.path.insert(0, str(hardware_root / 'printed-parts' / 'enclosure' / 'enclosure'))
    from _enclosure_datums import install
    install()
    tpu = load_module('_tpu_oring_gen', hardware_root / 'printed-parts' / 'faucet' / 'tpu-o-ring' / 'tpu_o_ring.py')
    plate = load_module('_under_counter_plate_gen', hardware_root / 'cut-parts' / 'faucet' / 'under-counter-plate' / 'under_counter_plate.py')
    faucet = load_module('_faucet_assembly_gen', hardware_root / 'faucet-layout' / 'faucet_assembly.py')
    envelope = load_module('_install_envelope_sync', hardware_root.parent / 'marketing' / '_install_envelope_sync.py')
    collet, _chip, _recess = envelope.behind_the_rear_face()
    return {
        'faucet.above_counter_plate.plate_thickness': faucet.above_counter_plate.plate_thickness,
        'faucet.above_counter_gasket.gasket_thickness': faucet.above_counter_gasket.gasket_thickness,
        'tpu.cap_hole_diameter': tpu.cap_hole_diameter,
        'tpu.westbrass_port_diameter': tpu.westbrass_port_diameter,
        'tpu.outer_diameter': tpu.outer_diameter,
        'tpu.westbrass_squeeze': tpu.westbrass_squeeze,
        'tpu.inner_diameter': tpu.inner_diameter,
        'tpu.lldpe_interference': tpu.lldpe_interference,
        'tpu.total_height': tpu.total_height,
        'tpu.cap_thickness': tpu.cap_thickness,
        'tpu.cylinder_length': tpu.cylinder_length,
        'tpu.lldpe_id': tpu.lldpe_id,
        'tpu.lldpe_od': tpu.lldpe_od,
        'plate.disc_diameter': plate.disc_diameter,
        'plate.shank_diameter': plate.shank_diameter,
        'plate.pill_long_y': plate.pill_long_y,
        'plate.pill_short_x': plate.pill_short_x,
        'plate.fillet_radius': plate.fillet_radius,
        'faucet.countertop_hole_diameter': faucet.countertop_hole_diameter,
        'faucet.gasket_hole_cover()': faucet.gasket_hole_cover(),
        'faucet.tube_collar.LENGTH': faucet.tube_collar.LENGTH,
        'faucet.tube_collar.bore_printed()': faucet.tube_collar.bore_printed(),
        'faucet.tube_collar.TUBE_OD': faucet.tube_collar.TUBE_OD,
        'faucet.foam_bare_at_wall': faucet.foam_bare_at_wall,
        'faucet.under_counter_plate_bottom_z': faucet.under_counter_plate_bottom_z,
        'faucet.organizer_top_z': faucet.organizer_top_z,
        'faucet.umbilical_organizer.LENGTH': faucet.umbilical_organizer.LENGTH,
        'faucet.umbilical_organizer.TUBE_BORE': faucet.umbilical_organizer.TUBE_BORE,
        'faucet.umbilical_organizer.FLAVOR_BORE': faucet.umbilical_organizer.FLAVOR_BORE,
        'faucet.umbilical_organizer.DRAIN_BORE': faucet.umbilical_organizer.DRAIN_BORE,
        'faucet.umbilical_organizer.CABLE_SLOT_LENGTH': faucet.umbilical_organizer.CABLE_SLOT_LENGTH,
        'faucet.umbilical_organizer.CABLE_SLOT_DEPTH': faucet.umbilical_organizer.CABLE_SLOT_DEPTH,
        'faucet.umbilical_organizer.MIN_MATERIAL': faucet.umbilical_organizer.MIN_MATERIAL,
        'faucet.umbilical_organizer.FLAVOR_SPREAD': faucet.umbilical_organizer.FLAVOR_SPREAD,
        'faucet.umbilical_organizer.FLAVOR_FORWARD': faucet.umbilical_organizer.FLAVOR_FORWARD,
        'faucet.umbilical_organizer.DRAIN_FORWARD': faucet.umbilical_organizer.DRAIN_FORWARD,
        'faucet.cable_lane': faucet.cable_lane,
        'faucet.cable_width': faucet.cable_width,
        'faucet.bundle_girth()': faucet.bundle_girth(),
        'faucet.bundle_bore()': faucet.bundle_bore(),
        'envelope.TURN_IN_LEAD_BEND': envelope.TURN_IN_LEAD_BEND,
        'collet': collet,
        'faucet.flavor_cut_length': faucet.flavor_cut_length,
        'faucet.blue_cut_length': faucet.blue_cut_length,
        'faucet.drain_factory_cut_length()': faucet.drain_factory_cut_length(),
        'faucet.flavor_path_above_foot()': faucet.flavor_path_above_foot(),
        'faucet.tails_apart': faucet.tails_apart,
        'faucet.countertop_thickness': faucet.countertop_thickness,
        'faucet.soda_umbilical_tube_z_top': faucet.soda_umbilical_tube_z_top,
        'faucet.countertop_bottom_z': faucet.countertop_bottom_z,
        'faucet.soda_faucet_cut_length': faucet.soda_faucet_cut_length,
        'faucet.countertop_max_thickness': faucet.countertop_max_thickness,
        'faucet.foam_length': faucet.foam_length,
        'faucet.foam_bare_at_westbrass': faucet.foam_bare_at_westbrass,
        'faucet.sleeve_z_top': faucet.sleeve_z_top,
        'faucet.umbilical_z_bottom': faucet.umbilical_z_bottom,
        'faucet.bare_bundle_girth()': faucet.bare_bundle_girth(),
    }


def main():
    _update('faucet-and-umbilical', _inputs())


if __name__ == "__main__":
    main()
