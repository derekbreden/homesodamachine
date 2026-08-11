"""Doc-sync driver for hardware/assembly/wiring.md.

Run: tools/cad-venv/bin/python hardware/assembly/_wiring_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md

import importlib.util  # noqa: E402


def _load_module(name: str, path: Path):
    """Load a module from an explicit file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The under-counter plate's own disc, off the script that cuts it: the diameter falls
# out of the two pockets' extremes plus one reach margin, so a pocket that moves
# resizes the disc. `_faucet_and_umbilical_sync` states the same figure off the same
# module — one plate under one diameter, and the two procedures cannot disagree.
_plate = _load_module(
    "_under_counter_plate_gen",
    next(p for p in _here.parents if p.name == "hardware")
    / "cut-parts" / "faucet" / "touch-flo-under-counter-plate"
    / "touch_flo_under_counter_plate.py",
)

# Import from the AC schedule's sync driver — the schedule is the source
# for every per-run gauge, voltage, and length the procedure references.
sys.path.insert(
    0,
    str(_here.parents[0] / "wiring"),
)
from _ac_wiring_schedule_sync import (  # noqa: E402
    awg_mains as _sched_awg_mains,
    awg_ac_branch as _sched_awg_ac_branch,
    awg_compressor_lead as _sched_awg_compressor_lead,
    awg_sig as _sched_awg_sig,
    awg_lv as _sched_awg_lv,
    line_voltage_v as _sched_line_voltage_v,
    v_rail_dc as _sched_v_rail_dc,
    v_rail_logic as _sched_v_rail_logic,
    v_rail_io as _sched_v_rail_io,
    ds18b20_pullup_kohm as _sched_ds18b20_pullup_kohm,
    len_short_mm as _sched_len_short_mm,
    len_short_2_mm as _sched_len_short_2_mm,
    len_mid_mm as _sched_len_mid_mm,
    len_compressor_mm as _sched_len_compressor_mm,
    len_cold_core_mm as _sched_len_cold_core_mm,
    len_umbilical_m as _sched_len_umbilical_m,
    jst_pitch_mm as _sched_jst_pitch_mm,
)


# ─── Procedure-only constants ───────────────────────────────────────────

cabinet_slack_mm = 200       # umbilical-end ground-bond slack at cabinet side
vk_run_len_mm = 500          # DC-9, J2 trunk to V-K on the aft strip (schedule literal)

# Donor-compressor nameplate readings: the winding-resistance reference range
# for the dielectric / continuity check, and the power class the AC side is
# sized against.
winding_r_low_ohm = 10
winding_r_high_ohm = 30
compressor_class_w = 100


def main():
    variables = {
        # Wire gauges.
        "AWG_AC_MAIN": f"{_sched_awg_mains:.4g} AWG",
        "AWG_AC_BRANCH_U": f"{_sched_awg_ac_branch:.4g} AWG",
        "AWG_DC_BRANCH": f"{_sched_awg_sig:.4g} AWG",
        "AWG_SIGNAL": f"{_sched_awg_lv:.4g} AWG",
        "AWG_TRIPLE": f"{_sched_awg_mains:.4g}/{_sched_awg_sig:.4g} AWG",
        # Voltages.
        "AC_LINE_V": f"{_sched_line_voltage_v:.4g} VAC",
        "DC_BUS_V": f"{_sched_v_rail_dc:.4g} V",
        "LOGIC_V": f"{_sched_v_rail_logic:.4g} V",
        "MCU_V": f"{_sched_v_rail_io:.4g} V",
        # Run lengths.
        "COMP_LEAD_LEN": f"~{_sched_len_compressor_mm:.4g} mm",
        "COMP_FAN_OUT": f"~{_sched_len_short_mm:.4g} mm",
        "AC1_LEN": f"~{_sched_len_mid_mm:.4g} mm",
        "AC2_LEN": f"~{_sched_len_short_2_mm:.4g} mm",
        "SIG_COLD_CORE_LEN": f"~{_sched_len_cold_core_mm:.4g} mm",
        "SIG_UMBILICAL_LEN": f"~{_sched_len_umbilical_m:.4g} m",
        "SIG_DISPLAY_LEN": f"~{_sched_len_umbilical_m:.4g} m",
        "FAN_RUN_LEN": f"~{_sched_len_compressor_mm:.4g} mm",
        # Connector pitch.
        "JST_PITCH": f"{_sched_jst_pitch_mm:.4g} mm",
        # Electrical-component values.
        "PULLUP_R": f"{_sched_ds18b20_pullup_kohm:.4g} kΩ",
        # Procedure-only (local).
        "CABINET_SLACK": f"{cabinet_slack_mm:.4g} mm",
        "VK_RUN_LEN": f"~{vk_run_len_mm:.4g} mm",
        "WINDING_R_LOW": f"{winding_r_low_ohm:.4g}",
        "WINDING_R_HIGH": f"{winding_r_high_ohm:.4g} Ω",
        "COMP_CLASS_W": f"{compressor_class_w:.4g} W",
        # The compressor lead's own gauge — a purchased cord, so the schedule
        # carries it beside the loose-wire classes rather than as one of them.
        "COMP_LEAD_AWG": f"{_sched_awg_compressor_lead:.4g} AWG",
        # The faucet plate WR-06 stages but does not land.
        "PLATE_D": f"{_plate.disc_diameter:.4g} mm",
    }

    substitute_md(
        _here / "wiring.md",
        variables=variables,
        expected_counts={
            "PLATE_D": 1,
            "AWG_AC_MAIN": 4,
            "AWG_AC_BRANCH_U": 1,
            "AWG_DC_BRANCH": 2,
            "AWG_SIGNAL": 2,
            "AWG_TRIPLE": 2,
            "AC_LINE_V": 2,
            "DC_BUS_V": 9,
            "LOGIC_V": 2,
            "MCU_V": 1,
            "JST_PITCH": 2,
            "COMP_LEAD_LEN": 1,
            "COMP_FAN_OUT": 1,
            "AC1_LEN": 1,
            "AC2_LEN": 1,
            "SIG_COLD_CORE_LEN": 2,
            "SIG_UMBILICAL_LEN": 1,
            "SIG_DISPLAY_LEN": 1,
            "FAN_RUN_LEN": 1,
            "CABINET_SLACK": 1,
            "VK_RUN_LEN": 1,
            "PULLUP_R": 1,
            "WINDING_R_LOW": 1,
            "WINDING_R_HIGH": 1,
            "COMP_LEAD_AWG": 4,
            "COMP_CLASS_W": 1,
        },
    )
    print("-> wiring.md")


if __name__ == "__main__":
    main()
