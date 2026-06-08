"""Doc-sync driver for hardware/assembly/electronics-shelf.md.

Run: tools/cad-venv/bin/python hardware/assembly/_electronics_shelf_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── ESP32 GPIO pin assignments ────────────────────────────────────────
# Source: ../wiring/esp32-pinout.mmd.
relay_compressor_gpio = 14              # ESP32 GPIO -> Teyleten relay #1 (compressor AC)
relay_diaphragm_gpio = 4                # ESP32 GPIO -> Teyleten relay #2 (diaphragm pump 12 V)

# ─── PSU spec (Mean Well IRM-90-12ST) ──────────────────────────────────
psu_power_w = 80                        # rated output
psu_voltage_v = 12                      # regulated rail
psu_current_a = 6.7                     # max
psu_mass_g = 200

# ─── GFCI spec (Legrand 1597BKCCD12) ───────────────────────────────────
gfci_trip_threshold_ma = 6              # UL 943 Class A trip
gfci_self_test_interval_s = 3           # self-test cycle

# ─── AC pigtail lengths ────────────────────────────────────────────────
# Source: ../wiring/ac-wiring-schedule.md "AC mains" table.
pigtail_short_mm = 50                   # AC-3 load-side
pigtail_medium_mm = 100                 # AC-2, DC-1
pigtail_gfci_mm = 150                   # AC-1a (C14 → GFCI LINE), AC-1b (GFCI LOAD → Wago)
pigtail_slack_mm = 150                  # AC-1a inlet-side slack
pigtail_compressor_mm = 400             # AC-4/5/6 compressor-side runs

# ─── Wire-stock format (Keszoox pigtail length) ────────────────────────
# Source: Keszoox B0F8HMQRRN packaging spec (50 cm × 22 AWG × 20 wires).
keszoox_length_cm = 50

# ─── Wago 221-413 lever-block count ────────────────────────────────────
# Source: ../bom.md §11 (one per AC conductor — H, N, G).
wago_count = 3

# ─── JST inter-module harness counts ───────────────────────────────────
# Source: ../wiring/ac-wiring-schedule.md "Inter-module connectors" table.
jst_4pin_count = 3                      # 4-pin (I²C + UART hops)
jst_6pin_count = 1                      # 6-pin (L298N control row)
jst_9pin_count = 4                      # 9-pin (ULN2803A sides only)
jst_10pin_count = 4                     # 10-pin (MCP23017 GPIO rows)

# ─── DS18B20 1-wire bus pull-up ────────────────────────────────────────
# Source: DS18B20 datasheet (Maxim/ADI).
ds18b20_pullup_kohm = 4.7


def main():
    variables = {
        # ESP32 GPIO pins.
        "RELAY_COMPRESSOR_GPIO": f"GPIO {relay_compressor_gpio:.4g}",
        "RELAY_DIAPHRAGM_GPIO": f"GPIO {relay_diaphragm_gpio:.4g}",
        # PSU specs.
        "PSU_POWER": f"{psu_power_w:.4g} W",
        "PSU_VOLTAGE": f"{psu_voltage_v:.4g} V",
        "PSU_CURRENT": f"{psu_current_a:.4g} A",
        "PSU_MASS": f"~{psu_mass_g:.4g} g",
        # GFCI specs.
        "GFCI_TRIP": f"{gfci_trip_threshold_ma:.4g} mA",
        "GFCI_SELF_TEST": f"{gfci_self_test_interval_s:.4g} seconds",
        # AC pigtail lengths.
        "PIGTAIL_SHORT": f"~{pigtail_short_mm:.4g} mm",
        "PIGTAIL_MEDIUM": f"~{pigtail_medium_mm:.4g} mm",
        "PIGTAIL_GFCI": f"~{pigtail_gfci_mm:.4g} mm",
        "PIGTAIL_SLACK": f"~{pigtail_slack_mm:.4g} mm",
        "PIGTAIL_COMPRESSOR": f"~{pigtail_compressor_mm:.4g} mm",
        # Wire-stock pigtail.
        "KESZOOX_LENGTH": f"{keszoox_length_cm:.4g} cm",
        # Wago count.
        "WAGO_COUNT": f"{wago_count:.4g}",
        # JST harness counts.
        "JST_4PIN_COUNT": f"~{jst_4pin_count:.4g}",
        "JST_6PIN_COUNT": f"~{jst_6pin_count:.4g}",
        "JST_9PIN_COUNT": f"~{jst_9pin_count:.4g}",
        "JST_10PIN_COUNT": f"~{jst_10pin_count:.4g}",
        # DS18B20 pull-up.
        "DS18B20_PULLUP": f"{ds18b20_pullup_kohm:.4g} kΩ",
    }

    substitute_md(
        _here / "electronics-shelf.md",
        variables=variables,
        expected_counts={
            "RELAY_COMPRESSOR_GPIO": 2,
            "RELAY_DIAPHRAGM_GPIO": 2,
            "PSU_POWER": 1,
            "PSU_VOLTAGE": 1,
            "PSU_CURRENT": 1,
            "PSU_MASS": 1,
            "GFCI_TRIP": 1,
            "GFCI_SELF_TEST": 1,
            "PIGTAIL_SHORT": 1,
            "PIGTAIL_MEDIUM": 2,
            "PIGTAIL_GFCI": 2,
            "PIGTAIL_SLACK": 1,
            "PIGTAIL_COMPRESSOR": 3,
            "KESZOOX_LENGTH": 2,
            "WAGO_COUNT": 1,
            "JST_4PIN_COUNT": 1,
            "JST_6PIN_COUNT": 1,
            "JST_9PIN_COUNT": 1,
            "JST_10PIN_COUNT": 1,
            "DS18B20_PULLUP": 1,
        },
    )
    print("-> electronics-shelf.md")


if __name__ == "__main__":
    main()
