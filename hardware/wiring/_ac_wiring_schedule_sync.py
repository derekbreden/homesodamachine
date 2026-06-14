"""Doc-sync driver for hardware/wiring/ac-wiring-schedule.md.

Run: tools/cad-venv/bin/python hardware/wiring/_ac_wiring_schedule_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── Mains-side voltage / fault-protection design ────────────────────
# US household single-phase line voltage.
line_voltage_v = 120

# Legrand Radiant 1597BKCCD12 GFCI trip threshold. UL 943 Class A.
gfci_trip_ma = 6

# AC primary fuse rating.
ac_primary_fuse_a = 5

# ─── Conductor gauges ─────────────────────────────────────────────────
# Four AWG classes used across the schedule:
#   - mains-side (AC-1a/b and AC-6 ground bond, 12 V trunk out of PSU)
#   - AC branch (PSU primary, compressor leads, relay legs)
#   - signal (DS18B20 bus, peristaltic-pump rail, solenoid fan-out)
#   - low-voltage logic (ESP32 GPIO, I2C, reed switches, UART trunk)
awg_mains = 16          # AC-1a/b, AC-6, DC-1/DC-2/DC-3, ground bus
awg_ac_branch = 18      # AC-2/AC-3/AC-4/AC-5, DC-6
awg_sig = 22            # DS18B20 + peristaltic + solenoid + fan
awg_lv = 24             # ESP32 GPIO, I2C, reeds, UART

# ─── PSU (Mean Well IRM-90-12ST) ──────────────────────────────────────
psu_primary_a = 0.67    # primary-side current at full load (80 W ÷ 120 V)
psu_full_load_w = 80    # nominal output
psu_max_dc_a = 6.7      # rated output current

# ─── Major 12 V loads ─────────────────────────────────────────────────
# SeaFlo diaphragm pump peak current (refill pump for the carbonator
# reservoir). Sets DC-3 gauge.
diaphragm_peak_a = 5

# Kamoer peristaltic pump current range per pump (two pumps on the
# L298N motor driver).
peri_pump_ma_low = 300
peri_pump_ma_high = 500

# Condenser fan motor (harvested from donor ice maker — 12 V DC
# brushless axial). Low-side switched through ULN2803A #2 ch5 per DC-9.
fan_current_a = 0.35

# ─── Logic rails ──────────────────────────────────────────────────────
# 5 V for MCUs / module VCC / opto coils, 3.3 V for ESP32 GPIO and
# I2C-side signals. The 3.3 V regulator chains from the 5 V rail per
# `power.mmd`; only 5 V draws directly from the 12 V trunk (run DC-8).
v_rail_dc = 12
v_rail_logic = 5
v_rail_io = 3.3

# DS18B20 1-wire bus pull-up between data and 3.3 V (SIG-1).
ds18b20_pullup_kohm = 4.7

# ─── Conductor counts through the shroud / cabinet trunks ────────────
# Three wires (switched H + N + chassis G) cross the compressor shroud
# wall in the SJOOW bundle. Five would cross if Teyleten relay #1 lived
# inside the shroud (add the relay's #1 logic leg + opto return).
shroud_wires_outside = 3
shroud_wires_inside = 5

# Beduan solenoid coils on the manifold. Sets the DC-7 conductor count.
solenoid_count = 12

# Conductors in the bundle from the electronics shelf to the manifold.
loom_conductors = 24

# ─── Run-length design targets ────────────────────────────────────────
# All values mm except where noted.
len_short_mm = 50       # AC-3 (shelf hop), DC-8 (L298N onboard 5 V reg → MCU)
len_short_2_mm = 100    # AC-2 (distribution → PSU), DC-1, DC-2, LV-3
len_mid_mm = 150        # AC-1a/AC-1b (C14 → GFCI → block), LV-1, LV-2, DC-4, DC-6, DC-7 fan-out, SIG-8
len_pump_mm = 250       # DC-3 (diaphragm pump), DC-5 to manifold
len_manifold_mm = 300   # DC-7 (shelf → manifold)
len_compressor_mm = 400 # AC-4, AC-5, AC-6 (shelf → compressor through grommet), DC-9 (shelf → side-wall fan)
len_cold_core_mm = 600  # SIG-1/SIG-2/SIG-3 (shelf → back of cold core), SIG-9 (shelf → drip pan)
len_umbilical_m = 1.0   # SIG-4 (umbilical-side flow meter), SIG-7 (front-face 4.3B config display, internal)

# ─── Inter-module connector pitch ────────────────────────────────────
# JST XH 2.54 mm. 4-pin / 6-pin / 9-pin variants per the inter-module
# connector table.
jst_pitch_mm = 2.54


def main():
    variables = {
        # Mains-side voltage / fault protection.
        "V_LINE": f"{line_voltage_v:.4g} V",
        "GFCI_TRIP": f"{gfci_trip_ma:.4g} mA",
        "PRIMARY_FUSE_A": f"{ac_primary_fuse_a:.4g} A",
        # Conductor gauges.
        "AWG_MAINS": f"{awg_mains:.4g}",
        "AWG_AC_BRANCH": f"{awg_ac_branch:.4g}",
        "AWG_SIG": f"{awg_sig:.4g}",
        "AWG_LV": f"{awg_lv:.4g}",
        # "16 AWG" / "18 AWG" with units, used in prose.
        "AWG_MAINS_U": f"{awg_mains:.4g} AWG",
        "AWG_AC_BRANCH_U": f"{awg_ac_branch:.4g} AWG",
        "AWG_SIG_U": f"{awg_sig:.4g} AWG",
        # PSU.
        "PSU_PRI_A": f"{psu_primary_a:.4g} A",
        "PSU_W": f"{psu_full_load_w:.4g} W",
        "PSU_MAX_A": f"{psu_max_dc_a:.4g} A",
        # Major 12 V loads.
        "DIAPHRAGM_A": f"{diaphragm_peak_a:.4g} A",
        "PERI_MA_LOW": f"{peri_pump_ma_low:.4g}",
        "PERI_MA_HIGH": f"{peri_pump_ma_high:.4g} mA",
        "FAN_A": f"{fan_current_a:.4g} A",
        # Logic rails.
        "V_DC": f"{v_rail_dc:.4g} V",
        "V_LOGIC": f"{v_rail_logic:.4g} V",
        "V_IO": f"{v_rail_io:.4g} V",
        "DS18B20_PULLUP": f"{ds18b20_pullup_kohm:.4g} kΩ",
        # Conductor counts.
        "SHROUD_WIRES": f"{shroud_wires_outside:.4g}",
        "SHROUD_WIRES_ALT": f"{shroud_wires_inside:.4g}",
        "SOLENOID_COUNT": f"{solenoid_count:.4g}",
        "LOOM_CONDUCTORS": f"{loom_conductors:.4g}",
        # Run-length design targets.
        "LEN_SHORT": f"~{len_short_mm:.4g} mm",
        "LEN_SHORT_2": f"~{len_short_2_mm:.4g} mm",
        "LEN_MID": f"~{len_mid_mm:.4g} mm",
        "LEN_PUMP": f"~{len_pump_mm:.4g} mm",
        "LEN_MANIFOLD": f"~{len_manifold_mm:.4g} mm",
        "LEN_COMPRESSOR": f"~{len_compressor_mm:.4g} mm",
        "LEN_COLD_CORE": f"~{len_cold_core_mm:.4g} mm",
        "LEN_UMBILICAL": f"~{len_umbilical_m:.4g} m",
        # Connector pitch.
        "JST_PITCH": f"{jst_pitch_mm:.4g} mm",
    }

    substitute_md(
        _here / "ac-wiring-schedule.md",
        variables=variables,
        expected_counts={
            # Mains-side voltage / fault protection.
            "V_LINE": 1,
            "GFCI_TRIP": 1,
            "PRIMARY_FUSE_A": 1,
            # Conductor gauges (raw, in the per-row "AWG" column).
            "AWG_MAINS": 6,        # AC-1a, AC-1b, AC-6, DC-1, DC-2, DC-3
            "AWG_AC_BRANCH": 5,    # AC-2/3/4/5, DC-6
            "AWG_SIG": 6,          # DC-4/5/7/8/9, SIG-1
            "AWG_LV": 10,          # LV-1/2/3, SIG-2/3/4/6/7/8/9
            # Conductor gauges with " AWG" suffix in prose.
            "AWG_MAINS_U": 3,
            "AWG_AC_BRANCH_U": 1,
            "AWG_SIG_U": 1,
            # PSU.
            "PSU_PRI_A": 1,
            "PSU_W": 1,
            "PSU_MAX_A": 1,
            # Major 12 V loads.
            "DIAPHRAGM_A": 1,
            "PERI_MA_LOW": 1,
            "PERI_MA_HIGH": 1,
            "FAN_A": 1,
            # Logic rails.
            "V_DC": 16,
            "V_LOGIC": 7,
            "V_IO": 8,
            "DS18B20_PULLUP": 1,
            # Conductor counts.
            "SHROUD_WIRES": 1,
            "SHROUD_WIRES_ALT": 1,
            "SOLENOID_COUNT": 2,
            "LOOM_CONDUCTORS": 2,
            # Run-length design targets.
            "LEN_SHORT": 2,
            "LEN_SHORT_2": 5,
            "LEN_MID": 8,
            "LEN_PUMP": 2,
            "LEN_MANIFOLD": 1,
            "LEN_COMPRESSOR": 4,
            "LEN_COLD_CORE": 4,
            "LEN_UMBILICAL": 3,
            # Connector pitch.
            "JST_PITCH": 1,
        },
    )
    print("-> ac-wiring-schedule.md")


if __name__ == "__main__":
    main()
