"""Wiring-procedure constants — source-of-truth for the per-run electrical
values in `wiring.md`.

No generator script (the procedure is prose, not geometry); this module exists
solely as the dimension source against which `wiring.md`'s [value](NAME)
markers substitute. Most of the values here are *imports* from the AC wiring
schedule's own sync driver (`../wiring/_ac_wiring_schedule_sync.py`) — the
schedule owns the source-of-truth gauges, voltages, and per-run lengths; the
procedure restates a handful for narrative flow and stays in lockstep by
importing the same constants.

The remaining values are procedure-only (cabinet-side slack, Keszoox pigtail
length, the compressor-shroud cable-OD references, the chassis-ground stud
hole, the compressor class) — those import from the compressor-shroud's
dimension source upstream.

A few procedure-only narrative numbers (the donor compressor winding
resistance range ~10–30 Ω, the 50 cm Keszoox pigtail length, the 200 mm
cabinet-side slack) have no upstream source and are defined locally below.

Run as a script to substitute the markdown:

    tools/cad-venv/bin/python _wiring_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md

# Import from the AC schedule's sync driver — the schedule is the source of
# truth for every per-run gauge, voltage, and length the procedure references.
sys.path.insert(
    0,
    str(_here.parents[0] / "wiring"),
)
from _ac_wiring_schedule_sync import (  # noqa: E402
    awg_mains as _sched_awg_mains,
    awg_ac_branch as _sched_awg_ac_branch,
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

# Import shroud-side values (cable OD, bushing range, ground-stud hole,
# compressor class) so the prose stays tied to the shroud's dimension source.
sys.path.insert(
    0,
    str(_here.parents[0] / "cut-parts" / "compressor-shroud"),
)
from _compressor_shroud_dimensions import (  # noqa: E402
    ac_cable_awg as _shroud_ac_cable_awg,
    bushing_cable_od_low_mm as _shroud_bushing_low_mm,
    bushing_cable_od_high_mm as _shroud_bushing_high_mm,
    chassis_ground_hole_mm as _shroud_gnd_hole_mm,
    compressor_class_w as _shroud_compressor_class_w,
)


# ─── Procedure-only constants (no upstream source) ──────────────────────
# Values that belong to the *procedure* — they're how-to-build numbers, not
# part-spec or schedule numbers. Defined locally because there's no upstream
# script that owns them.

cabinet_slack_mm = 200       # umbilical-end ground-bond slack at the cabinet
                             # side ("plus 200 mm of cabinet-side slack")

keszoox_pigtail_len_cm = 50  # Keszoox B0F8HMQRRN pre-crimped pigtail
                             # length, from BOM §11 inter-module connectors

# Donor-compressor nameplate winding-resistance reference range for the
# dielectric / continuity check. Generic ~10–30 Ω band for a 100 W-class
# hermetic; the actual donor measures within that band per
# ../harvested/ice-maker/ "Powering and control".
winding_r_low_ohm = 10
winding_r_high_ohm = 30


def main():
    variables = {
        # Wire gauges (imported from the AC schedule's source-of-truth driver).
        "AWG_AC_MAIN": f"{_sched_awg_mains:g} AWG",
        "AWG_AC_BRANCH": f"{_sched_awg_ac_branch:g} AWG",
        "AWG_DC_BRANCH": f"{_sched_awg_sig:g} AWG",
        "AWG_SIGNAL": f"{_sched_awg_lv:g} AWG",
        "AWG_TRIPLE": (
            f"{_sched_awg_mains:g}/{_sched_awg_ac_branch:g}/"
            f"{_sched_awg_sig:g} AWG"
        ),
        # Voltages (imported).
        "AC_LINE_V": f"{_sched_line_voltage_v:g} VAC",
        "DC_BUS_V": f"{_sched_v_rail_dc:g} V",
        "LOGIC_V": f"{_sched_v_rail_logic:g} V",
        "MCU_V": f"{_sched_v_rail_io:g} V",
        # Schedule-restated run lengths.
        "SHROUD_LEAD_LEN": f"~{_sched_len_compressor_mm:g} mm",
        "SHROUD_FAN_OUT": f"~{_sched_len_short_mm:g} mm",
        "AC1_LEN": f"~{_sched_len_short_mm:g} mm",
        "AC2_LEN": f"~{_sched_len_short_2_mm:g} mm",
        "LV_SHORT_LEN": f"~{_sched_len_mid_mm:g} mm",
        "SIG_COLD_CORE_LEN": f"~{_sched_len_cold_core_mm:g} mm",
        "SIG_UMBILICAL_LEN": f"~{_sched_len_umbilical_m:g} m",
        "SIG_DISPLAY_LEN": f"~{_sched_len_umbilical_m:g} m",
        "DC9_LEN": f"~{_sched_len_compressor_mm:g} mm",
        # Connector pitch (imported).
        "JST_PITCH": f"{_sched_jst_pitch_mm:g} mm",
        # Electrical-component values.
        "PULLUP_R": f"{_sched_ds18b20_pullup_kohm:g} kΩ",
        # Procedure-only (local).
        "CABINET_SLACK": f"{cabinet_slack_mm:g} mm",
        "KESZOOX_LEN": f"{keszoox_pigtail_len_cm:g} cm",
        "WINDING_R_LOW": f"{winding_r_low_ohm:g}",
        "WINDING_R_HIGH": f"{winding_r_high_ohm:g} Ω",
        # Shroud-side imports (live-tied to upstream).
        "SHROUD_SJOOW_AWG": f"{_shroud_ac_cable_awg:g} AWG",
        "BUSHING_LOW": f"{_shroud_bushing_low_mm:g}",
        "BUSHING_HIGH": f"{_shroud_bushing_high_mm:g} mm",
        "GND_STUD_HOLE": f"{_shroud_gnd_hole_mm:g} mm",
        "COMP_CLASS_W": f"{_shroud_compressor_class_w:g} W-class",
    }

    substitute_md(
        _here / "wiring.md",
        variables=variables,
        expected_counts={
            "AWG_AC_MAIN": 5,
            "AWG_AC_BRANCH": 3,
            "AWG_DC_BRANCH": 3,
            "AWG_SIGNAL": 3,
            "AWG_TRIPLE": 2,
            "AC_LINE_V": 4,
            "DC_BUS_V": 18,
            "LOGIC_V": 6,
            "MCU_V": 6,
            "JST_PITCH": 2,
            "SHROUD_LEAD_LEN": 1,
            "SHROUD_FAN_OUT": 1,
            "AC1_LEN": 1,
            "AC2_LEN": 1,
            "LV_SHORT_LEN": 1,
            "SIG_COLD_CORE_LEN": 2,
            "SIG_UMBILICAL_LEN": 1,
            "SIG_DISPLAY_LEN": 1,
            "DC9_LEN": 1,
            "CABINET_SLACK": 1,
            "KESZOOX_LEN": 1,
            "PULLUP_R": 1,
            "WINDING_R_LOW": 1,
            "WINDING_R_HIGH": 1,
            "SHROUD_SJOOW_AWG": 4,
            "BUSHING_LOW": 1,
            "BUSHING_HIGH": 1,
            "GND_STUD_HOLE": 1,
            "COMP_CLASS_W": 1,
        },
    )
    print("-> wiring.md")


if __name__ == "__main__":
    main()
