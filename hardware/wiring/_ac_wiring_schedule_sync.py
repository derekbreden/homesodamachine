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

# AC primary fuse rating.
ac_primary_fuse_a = 5

# ─── Conductor gauges ─────────────────────────────────────────────────
# Two loose-wire AWG classes: power (16) — AC mains feed + branches +
# ground bond, 12 V trunk + branches; signal (22) — board-driven DC
# actuators + every sensor / reed / display / logic run. The AC-branch
# and LV runs share the power and signal gauge respectively but keep
# their own markers. The compressor lead (AC-4/5/6) is its own gauge:
# it is a purchased jacketed cord, not wire cut off a spool, so its
# three conductors come at whatever gauge the cord is bought at.
awg_mains = 16          # AC-1, DC-1/DC-2/DC-3/DC-4, ground bus
awg_ac_branch = 16      # AC-2/AC-3 (power gauge)
awg_compressor_lead = 18  # AC-4/AC-5/AC-6 — the SJOOW cord's three conductors
awg_sig = 22            # DC-5/DC-6/DC-7/DC-8, SIG-1
awg_lv = 22             # LV-1/2/3, SIG-2/3/4/7/9/10/11/12 (signal gauge)

# ─── PSU (Mean Well IRM-90-12ST) ──────────────────────────────────────
psu_primary_a = 0.67    # primary-side current at full load (80 W ÷ 120 V)
psu_full_load_w = 80    # nominal output
psu_max_dc_a = 6.7      # rated output current

# ─── Major 12 V loads ─────────────────────────────────────────────────
# SeaFlo diaphragm pump peak current (refill pump for the carbonator
# reservoir). Sets DC-3 gauge.
diaphragm_peak_a = 5

# Kamoer KPHM400-SW peristaltic pump peak current per pump (two pumps
# on the board's DRV8870 H-bridges, PUMPS J13 / run DC-5). Matches the
# board's ampacity declaration (`/hardware/pcb/pcba/pcba.tsx`).
pump_peak_a = 0.8

# Condenser fan motor (harvested from donor ice maker — 12 V DC
# brushless axial). Low-side switched through the MANIFOLD B J2 `FAN`
# conductor per DC-8.
fan_current_a = 0.35

# ─── Logic rails ──────────────────────────────────────────────────────
# Both logic rails are made on the PCBA off its J10 12 V inlet: 5 V from
# the K7805 buck (U10), 3.3 V from the AMS1117 LDO (U9, off the 5 V
# rail) per `power.mmd`. Off-board loads draw them through the loom
# connectors (V5 / 3V3 pins).
v_rail_dc = 12
v_rail_logic = 5
v_rail_io = 3.3

# DS18B20 1-wire bus pull-up between data and 3.3 V — on-board (R9),
# cited in SIG-1.
ds18b20_pullup_kohm = 4.7

# ─── Conductor counts down the cabinet trunks ────────────────────────
# Three wires (switched H + N + chassis G) reach the compressor in the
# SJOOW bundle. Five would reach it if Teyleten relay #1 stood beside it
# rather than on the shelf (add the relay's #1 logic leg + opto return).
compressor_wires_shelf_relay = 3
compressor_wires_local_relay = 5

# Beduan solenoid coils across both manifolds. Cited in DC-4's board
# load list. The board carries 12 channels (J1 ×8, J2 ×4); the manifold
# uses 10 — J2.OUT3/OUT4 are spare capacity, not a load.
solenoid_count = 10

# ─── Run-length design targets ────────────────────────────────────────
# All values mm except where noted.
len_short_mm = 50       # AC-3 (shelf hop)
len_short_2_mm = 100    # AC-2 (distribution → PSU), DC-1, DC-2, DC-5 pigtail
len_mid_mm = 150        # AC-1 (C14 → distribution block, over the foam-cap top), LV-1/2/3, DC-4, DC-6/DC-7 valve fan-outs, SIG-4
len_pump_mm = 250       # DC-3 (diaphragm pump), DC-5 to the peristaltic pumps
len_manifold_mm = 300   # DC-6/DC-7 (shelf → manifold trunks)
len_compressor_mm = 400 # AC-4, AC-5, AC-6 (shelf → compressor on the unbroken SJOOW jacket), DC-8 (shelf → side-wall fan)
len_cold_core_mm = 600  # SIG-1/2/3/10/11 (shelf → cold core), SIG-9 (drip pan), SIG-12 (rear cabinet floor)
len_umbilical_m = 1.0   # SIG-6 (faucet display up the umbilical), SIG-7 (front-face 4.3B config display, internal)

# ─── Loom connector pitch ─────────────────────────────────────────────
# JST XH 2.54 mm — every board loom connector (J1–J9, J11, J13); J10 is
# the 5.0 mm screw block.
jst_pitch_mm = 2.54


def main():
    variables = {
        # Mains-side voltage / fault protection.
        "V_LINE": f"{line_voltage_v:.4g} V",
        "PRIMARY_FUSE_A": f"{ac_primary_fuse_a:.4g} A",
        # Conductor gauges.
        "AWG_MAINS": f"{awg_mains:.4g}",
        "AWG_AC_BRANCH": f"{awg_ac_branch:.4g}",
        "AWG_COMP_LEAD": f"{awg_compressor_lead:.4g}",
        "AWG_SIG": f"{awg_sig:.4g}",
        "AWG_LV": f"{awg_lv:.4g}",
        # Gauge with the " AWG" unit, used in prose.
        "AWG_MAINS_U": f"{awg_mains:.4g} AWG",
        "AWG_AC_BRANCH_U": f"{awg_ac_branch:.4g} AWG",
        "AWG_COMP_LEAD_U": f"{awg_compressor_lead:.4g} AWG",
        # PSU.
        "PSU_PRI_A": f"{psu_primary_a:.4g} A",
        "PSU_W": f"{psu_full_load_w:.4g} W",
        "PSU_MAX_A": f"{psu_max_dc_a:.4g} A",
        # Major 12 V loads.
        "DIAPHRAGM_A": f"{diaphragm_peak_a:.4g} A",
        "PUMP_PEAK_A": f"{pump_peak_a:.4g} A",
        "FAN_A": f"{fan_current_a:.4g} A",
        # Logic rails.
        "V_DC": f"{v_rail_dc:.4g} V",
        "V_LOGIC": f"{v_rail_logic:.4g} V",
        "V_IO": f"{v_rail_io:.4g} V",
        "DS18B20_PULLUP": f"{ds18b20_pullup_kohm:.4g} kΩ",
        # Conductor counts.
        "COMP_WIRES": f"{compressor_wires_shelf_relay:.4g}",
        "COMP_WIRES_ALT": f"{compressor_wires_local_relay:.4g}",
        "SOLENOID_COUNT": f"{solenoid_count:.4g}",
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
            "PRIMARY_FUSE_A": 1,
            # Conductor gauges (raw, in the per-row "AWG" column).
            "AWG_MAINS": 5,        # AC-1, DC-1/2/3/4
            "AWG_AC_BRANCH": 2,    # AC-2/3
            "AWG_COMP_LEAD": 3,       # AC-4/5/6
            "AWG_SIG": 5,          # DC-5/6/7/8, SIG-1
            "AWG_LV": 11,          # LV-1/2/3, SIG-2/3/4/7/9/10/11/12
            # Conductor gauges with " AWG" suffix in prose.
            "AWG_MAINS_U": 3,
            "AWG_AC_BRANCH_U": 1,
            "AWG_COMP_LEAD_U": 1,
            # PSU.
            "PSU_PRI_A": 1,
            "PSU_W": 1,
            "PSU_MAX_A": 1,
            # Major 12 V loads.
            "DIAPHRAGM_A": 1,
            "PUMP_PEAK_A": 1,
            "FAN_A": 2,            # DC-8, COM budget paragraph
            # Logic rails.
            "V_DC": 18,
            "V_LOGIC": 5,
            "V_IO": 4,
            "DS18B20_PULLUP": 1,
            # Conductor counts.
            "COMP_WIRES": 1,
            "COMP_WIRES_ALT": 1,
            "SOLENOID_COUNT": 1,
            # Run-length design targets.
            "LEN_SHORT": 1,
            "LEN_SHORT_2": 4,
            "LEN_MID": 8,
            "LEN_PUMP": 2,
            "LEN_MANIFOLD": 2,
            "LEN_COMPRESSOR": 4,
            "LEN_COLD_CORE": 7,
            "LEN_UMBILICAL": 2,
            # Connector pitch.
            "JST_PITCH": 1,
        },
    )
    print("-> ac-wiring-schedule.md")


if __name__ == "__main__":
    main()
