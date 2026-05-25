"""AC wiring schedule — source-of-truth constants for the appliance's
mains + 12 V + low-voltage wiring spec.

No CAD geometry here; this module exists as the dimension source that
the schedule's [value](NAME) markers substitute against, so the prose
numbers (voltages, breaker/GFCI ratings, AWG choices, conductor
counts, expected run lengths) stay in lockstep with a single named
constant. The schedule lives at the appliance level (every run
references it) rather than at any single part, so its sync script
lives alongside it under `hardware/wiring/` rather than next to a
part.

Run as a script to substitute the schedule:

    tools/cad-venv/bin/python _ac_wiring_schedule_sync.py
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
# US household single-phase line voltage. The whole appliance is built
# around 120 VAC nominal; the GFCI, the PSU's universal-input window,
# and the breaker assumption all key off this number.
line_voltage_v = 120

# Legrand Radiant 1597BKCCD12 GFCI trip threshold. UL 943 Class A
# (the consumer-grade class that protects against personnel shock)
# specifies a 4–6 mA nominal trip current; the Legrand is the upper
# end of that window. The "UL 943" and "Class A" strings are external
# standards left raw; only the trip current is a parameterized number.
gfci_trip_ma = 6

# AC primary fuse rating considered in "What's not yet decided". Sized
# below the 15 A branch breaker so the fuse trips first on appliance
# fault — protects the appliance even if the building breaker is
# laggy or oversized.
ac_primary_fuse_a = 5

# ─── Conductor gauges ─────────────────────────────────────────────────
# Four AWG classes used across the schedule:
#   - mains-side (AC-1a/b and AC-6 ground bond, also the 12 V trunk
#     out of the PSU)
#   - AC branch (downstream of the AC distribution block — PSU primary,
#     compressor leads, relay legs)
#   - signal (DS18B20 bus, peristaltic-pump rail, solenoid fan-out)
#   - low-voltage logic (ESP32 GPIO, I2C, reed switches, UART trunk)
awg_mains = 16          # AC-1a/b, AC-6, DC-1/DC-2/DC-3, ground bus
awg_ac_branch = 18      # AC-2/AC-3/AC-4/AC-5, DC-6
awg_sig = 22            # DS18B20 + peristaltic + solenoid + fan
awg_lv = 24             # ESP32 GPIO, I2C, reeds, UART

# ─── PSU (Mean Well IRM-90-12ST) ──────────────────────────────────────
# Primary-side current at full load and the rated output current.
# These set the AC-2 and DC-1 gauge choices and the 5 A primary-fuse
# discussion. 80 W full-load is the PSU's nominal output;
# 0.67 A primary is 80 W ÷ 120 V (full-load worst case) with PSU
# efficiency rolled into the datasheet number.
psu_primary_a = 0.67
psu_full_load_w = 80
psu_max_dc_a = 6.7

# ─── Major 12 V loads ─────────────────────────────────────────────────
# SeaFlo diaphragm pump peak current (refill pump for the carbonator
# reservoir). Sets DC-3 gauge.
diaphragm_peak_a = 5

# Kamoer peristaltic pump current range per pump (two pumps on the
# L298N motor driver). 300–500 mA depending on dispense duty.
peri_pump_ma_low = 300
peri_pump_ma_high = 500

# Condenser fan motor (harvested from donor ice maker — 12 V DC
# brushless axial). Low-side switched through ULN2803A #2 ch5 per
# DC-9; the 0.35 A figure is from the donor PCB's regulated supply
# rating.
fan_current_a = 0.35

# ─── Logic rails ──────────────────────────────────────────────────────
# Two regulated logic-level supplies downstream of the 12 V trunk:
# 5 V for MCUs / module VCC / opto coils, 3.3 V for ESP32 GPIO and
# I2C-side signals. The 3.3 V regulator chains from the 5 V rail per
# `power.mmd`; only 5 V draws directly from the 12 V trunk (run DC-8).
v_rail_dc = 12
v_rail_logic = 5
v_rail_io = 3.3

# DS18B20 1-wire bus pull-up between data and 3.3 V (SIG-1). Standard
# Maxim recommended value; sits at the ESP32 end of the bus.
ds18b20_pullup_kohm = 4.7

# ─── Conductor counts through the shroud / cabinet trunks ────────────
# Three wires (switched H + N + chassis G) cross the compressor shroud
# wall in the SJOOW bundle, vs the five (add the relay's #1 logic
# leg + opto return) that would cross if Teyleten relay #1 lived
# inside the shroud. The 3-vs-5 contrast is the rationale for keeping
# the relay outside the protected refrigerant compartment.
shroud_wires_outside = 3
shroud_wires_inside = 5

# Beduan solenoid coils on the manifold (one per flavor × bus position
# in the current valve plan). Sets the DC-7 conductor count.
solenoid_count = 12

# Conductors in the bundle from the electronics shelf to the manifold
# — 12 solenoid coils × 2 conductors per valve (the COM/GND share at
# the ULN2803A side reduces it from a strict 24, but the conservative
# loom is sized for 24). Matches the "What's not yet decided" loom
# question.
loom_conductors = 24

# ─── Run-length design targets ────────────────────────────────────────
# Approximate cable lengths assumed by the schedule. The enclosure
# layout in ../future.md sets the cabinet dimensions these key off of;
# revise once the prototype is mocked up and lengths are measured.
# All values mm except where noted.
len_short_mm = 50       # AC-3 (shelf hop), DC-8 (12 V → 5 V regulator)
len_short_2_mm = 100    # AC-2 (distribution → PSU), DC-1, DC-2, LV-3
len_mid_mm = 150        # AC-1a/AC-1b (C14 → GFCI → block), LV-1, LV-2, DC-4, DC-6, DC-7 fan-out, SIG-8
len_pump_mm = 250       # DC-3 (diaphragm pump), DC-5 to manifold
len_manifold_mm = 300   # DC-7 (shelf → manifold)
len_compressor_mm = 400 # AC-4, AC-5, AC-6 (shelf → compressor through grommet), DC-9 (shelf → side-wall fan)
len_cold_core_mm = 600  # SIG-1/SIG-2/SIG-3 (shelf → back of cold core), SIG-9 (shelf → drip pan)
len_umbilical_m = 1.0   # SIG-4 (umbilical-side flow meter), SIG-7 (front-face S3 extended)

# ─── Inter-module connector pitch ────────────────────────────────────
# JST XH 2.54 mm — the standard 0.1" pitch connector family for every
# module-to-module hop on the electronics shelf. 4-pin / 6-pin / 9-pin
# variants per the inter-module connector table; only the pitch is
# parameterized.
jst_pitch_mm = 2.54


def main():
    variables = {
        # Mains-side voltage / fault protection.
        "V_LINE": f"{line_voltage_v:g} V",
        "GFCI_TRIP": f"{gfci_trip_ma:g} mA",
        "PRIMARY_FUSE_A": f"{ac_primary_fuse_a:g} A",
        # Conductor gauges.
        "AWG_MAINS": f"{awg_mains:g}",
        "AWG_AC_BRANCH": f"{awg_ac_branch:g}",
        "AWG_SIG": f"{awg_sig:g}",
        "AWG_LV": f"{awg_lv:g}",
        # "16 AWG" / "18 AWG" with units, used in prose.
        "AWG_MAINS_U": f"{awg_mains:g} AWG",
        "AWG_AC_BRANCH_U": f"{awg_ac_branch:g} AWG",
        "AWG_SIG_U": f"{awg_sig:g} AWG",
        # PSU.
        "PSU_PRI_A": f"{psu_primary_a:g} A",
        "PSU_W": f"{psu_full_load_w:g} W",
        "PSU_MAX_A": f"{psu_max_dc_a:g} A",
        # Major 12 V loads.
        "DIAPHRAGM_A": f"{diaphragm_peak_a:g} A",
        "PERI_MA_LOW": f"{peri_pump_ma_low:g}",
        "PERI_MA_HIGH": f"{peri_pump_ma_high:g} mA",
        "FAN_A": f"{fan_current_a:g} A",
        # Logic rails.
        "V_DC": f"{v_rail_dc:g} V",
        "V_LOGIC": f"{v_rail_logic:g} V",
        "V_IO": f"{v_rail_io:g} V",
        "DS18B20_PULLUP": f"{ds18b20_pullup_kohm:g} kΩ",
        # Conductor counts.
        "SHROUD_WIRES": f"{shroud_wires_outside:g}",
        "SHROUD_WIRES_ALT": f"{shroud_wires_inside:g}",
        "SOLENOID_COUNT": f"{solenoid_count:g}",
        "LOOM_CONDUCTORS": f"{loom_conductors:g}",
        # Run-length design targets.
        "LEN_SHORT": f"~{len_short_mm:g} mm",
        "LEN_SHORT_2": f"~{len_short_2_mm:g} mm",
        "LEN_MID": f"~{len_mid_mm:g} mm",
        "LEN_PUMP": f"~{len_pump_mm:g} mm",
        "LEN_MANIFOLD": f"~{len_manifold_mm:g} mm",
        "LEN_COMPRESSOR": f"~{len_compressor_mm:g} mm",
        "LEN_COLD_CORE": f"~{len_cold_core_mm:g} mm",
        "LEN_UMBILICAL": f"~{len_umbilical_m:g} m",
        # Connector pitch.
        "JST_PITCH": f"{jst_pitch_mm:g} mm",
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
            "AWG_LV": 9,           # LV-1/2/3, SIG-2/3/4/7/8/9
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
            "V_DC": 15,
            "V_LOGIC": 7,
            "V_IO": 7,
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
            "LEN_UMBILICAL": 2,
            # Connector pitch.
            "JST_PITCH": 1,
        },
    )
    print("-> ac-wiring-schedule.md")


if __name__ == "__main__":
    main()
