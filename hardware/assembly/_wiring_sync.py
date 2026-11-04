"""Doc-sync driver for hardware/assembly/wiring.md.

Run: tools/cad-venv/bin/python hardware/assembly/_wiring_sync.py"""
import sys
from pathlib import Path
_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next((p for p in _here.parents if p.name == 'hardware')) / 'scripts'))
sys.path.insert(0, str(next((p for p in _here.parents if (p / 'tools' / 'docgen').is_dir())) / 'tools'))
sys.path.insert(0, str(_here.parents[0] / 'wiring'))
from _ac_wiring_schedule_sync import awg_mains as _sched_awg_mains, awg_ac_branch as _sched_awg_ac_branch, awg_compressor_lead as _sched_awg_compressor_lead, awg_sig as _sched_awg_sig, awg_lv as _sched_awg_lv, line_voltage_v as _sched_line_voltage_v, v_rail_dc as _sched_v_rail_dc, v_rail_logic as _sched_v_rail_logic, v_rail_io as _sched_v_rail_io, ds18b20_pullup_kohm as _sched_ds18b20_pullup_kohm, len_short_mm as _sched_len_short_mm, len_short_2_mm as _sched_len_short_2_mm, len_mid_mm as _sched_len_mid_mm, len_earth_carbonator_mm as _sched_len_earth_carbonator_mm, len_compressor_mm as _sched_len_compressor_mm, len_opening_join_mm as _sched_len_opening_join_mm, len_fan_mm as _sched_len_fan_mm, len_vk_mm as _sched_len_vk_mm, len_front_face_mm as _sched_len_front_face_mm, len_onewire_mm as _sched_len_onewire_mm, len_reeds_a_mm as _sched_len_reeds_a_mm, len_umbilical_m as _sched_len_umbilical_m, jst_pitch_mm as _sched_jst_pitch_mm

_assembly_doc_root = next(p for p in Path(__file__).resolve().parents if (p / "hardware/scripts").is_dir())
sys.path.insert(0, str(_assembly_doc_root / "hardware/assembly"))
from _rust_docs import evaluate as _evaluate, update as _update


def _inputs():
    return {
        '_sched_awg_mains': _sched_awg_mains,
        '_sched_awg_ac_branch': _sched_awg_ac_branch,
        '_sched_awg_sig': _sched_awg_sig,
        '_sched_awg_lv': _sched_awg_lv,
        '_sched_line_voltage_v': _sched_line_voltage_v,
        '_sched_v_rail_dc': _sched_v_rail_dc,
        '_sched_v_rail_logic': _sched_v_rail_logic,
        '_sched_v_rail_io': _sched_v_rail_io,
        '_sched_len_compressor_mm': _sched_len_compressor_mm,
        '_sched_len_opening_join_mm': _sched_len_opening_join_mm,
        '_sched_len_short_mm': _sched_len_short_mm,
        '_sched_len_mid_mm': _sched_len_mid_mm,
        '_sched_len_short_2_mm': _sched_len_short_2_mm,
        '_sched_len_earth_carbonator_mm': _sched_len_earth_carbonator_mm,
        '_sched_len_onewire_mm': _sched_len_onewire_mm,
        '_sched_len_reeds_a_mm': _sched_len_reeds_a_mm,
        '_sched_len_umbilical_m': _sched_len_umbilical_m,
        '_sched_len_front_face_mm': _sched_len_front_face_mm,
        '_sched_len_fan_mm': _sched_len_fan_mm,
        '_sched_len_vk_mm': _sched_len_vk_mm,
        '_sched_jst_pitch_mm': _sched_jst_pitch_mm,
        '_sched_ds18b20_pullup_kohm': _sched_ds18b20_pullup_kohm,
        '_sched_awg_compressor_lead': _sched_awg_compressor_lead,
    }


globals().update(_evaluate('wiring', _inputs())["exports"])


def main():
    _update('wiring', _inputs())


if __name__ == "__main__":
    main()
