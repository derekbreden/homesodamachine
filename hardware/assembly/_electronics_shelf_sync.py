"""Electronics-shelf assembly source-of-truth constants.

The `electronics-shelf.md` assembly procedure has no CadQuery generator
of its own (the shelf STL itself is still TBD — see the README's "Open
items" §1). This module is the dimension / spec source that the README's
[value](NAME) markers substitute against, keeping prose-side numbers
in sync with named constants the same way every part-level
_dimensions.py / _sync.py does.

Coverage is **selective**: only multi-cite, drift-risk numbers are
managed here. Single-cite electrical specs (e.g. 80 W, 6.7 A, 6 mA,
~200 g) get NAMEs anyway because they trace back to off-the-shelf
datasheets and any future double-citing should not silently drift.

Most numbers in this file's prose are still raw — Amazon SKU
identifiers ("B0CNRST18V"), I²C address bytes ("0x20"), wire AWG values
("16 AWG"), and Mermaid-diagram-rooted GPIO assignments. Those are
either part-spec / part-procurement strings (BOM source-of-truth, not
adjustable here), JST kit pin counts, or values that have their
canonical source in `../wiring/esp32-pinout.mmd` (a Mermaid diagram —
not Python-importable). Sweep agents that revisit this file should
treat raw numbers as intentional unless they re-cite within the file
in a way that introduces new drift risk.

Run as a script to substitute the README:

    tools/cad-venv/bin/python _electronics_shelf_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── ESP32 GPIO pin assignments (relays — cited multiple times) ───────
# Canonical source: ../wiring/esp32-pinout.mmd. Mirrored here because
# the .mmd is a Mermaid diagram, not a Python module that can be
# imported. Only the two relay-drive GPIOs are mirrored — they're the
# pins this assembly procedure actually wires through. Pump-bridge and
# I²C pins are cited inside Dupont-build sentences with one occurrence
# each and stay raw.
relay_compressor_gpio = 14              # ESP32 GPIO -> Teyleten relay #1 (compressor AC)
relay_diaphragm_gpio = 4                # ESP32 GPIO -> Teyleten relay #2 (diaphragm pump 12 V)

# ─── PSU spec (Mean Well IRM-90-12ST) ──────────────────────────────────
# Source: Mean Well IRM-90-12ST datasheet. Cited in the inputs-table
# row, in the Open-items §4 frame-thickness discussion, and (PSU mass)
# implicitly drives the frame-thickness rationale.
psu_power_w = 80                        # 80 W rated output
psu_voltage_v = 12                      # 12 V regulated rail
psu_current_a = 6.7                     # 6.7 A max
psu_mass_g = 200                        # ~200 g (heaviest module on the shelf)

# ─── GFCI spec (Legrand 1597BKCCD12) ───────────────────────────────────
# Source: Legrand datasheet + UL 943. Cited in the GFCI inputs-table
# row.
gfci_trip_threshold_ma = 6              # UL 943 Class A 6 mA trip
gfci_self_test_interval_s = 3           # 3-second self-test cycle

# ─── AC pigtail lengths (procedure estimates) ──────────────────────────
# Source-of-truth: ../wiring/ac-wiring-schedule.md "AC mains" table.
# Mirrored here because the wiring schedule is a markdown table, not a
# Python module. These lengths are "estimates based on the future.md
# layout; revise once the prototype enclosure is mocked up and lengths
# are measured" (wiring-schedule prose). Multi-cite within this file:
# AC-1 inlet stub (~50 mm load-side + ~150 mm inlet-side slack),
# AC-2 (~100 mm), AC-3 (~50 mm), AC-4/5/6 (~400 mm each), DC-1 (~100 mm).
pigtail_short_mm = 50                   # AC-1, AC-3 load-side
pigtail_medium_mm = 100                 # AC-2, DC-1
pigtail_slack_mm = 150                  # AC-1 inlet-side slack
pigtail_compressor_mm = 400             # AC-4/5/6 compressor-side runs

# ─── Wire-stock format (Keszoox pigtail length) ────────────────────────
# Source: Keszoox B0F8HMQRRN packaging spec (50 cm × 22 AWG × 20 wires).
# Cited in the inputs-table row and in step 7's ULN-fan-out callout.
keszoox_length_cm = 50                  # 50 cm pre-crimped silicone pigtail

# ─── Wago 221-413 lever-block count ────────────────────────────────────
# Source: ../bom.md §11 (one per AC conductor — H, N, G). Cited in the
# scope summary, inputs-table row, step-3 procedure, and step-5 procedure.
wago_count = 3                          # 3 lever-nut connectors (H + N + G)

# ─── JST inter-module harness counts (per-unit estimates) ──────────────
# Source-of-truth: ../wiring/ac-wiring-schedule.md "Inter-module
# connectors" table. Mirrored here because that schedule is markdown.
# Cited in the inputs-table row and procedurally in step 2.
jst_4pin_count = 3                      # ~3× 4-pin (I²C + UART hops)
jst_6pin_count = 1                      # ~1× 6-pin (DS3231 bus)
jst_9pin_count = 6                      # ~6× 9-pin (ULN sides + MCP ports)

# ─── DS18B20 1-wire bus pull-up ────────────────────────────────────────
# Source: DS18B20 datasheet (Maxim/ADI) — 4.7 kΩ recommended pull-up
# between data and 3.3 V. Cited in step 8's SIG-1 callout.
ds18b20_pullup_kohm = 4.7               # 4.7 kΩ pull-up


def main():
    variables = {
        # ESP32 GPIO pins.
        "RELAY_COMPRESSOR_GPIO": f"GPIO {relay_compressor_gpio:g}",
        "RELAY_DIAPHRAGM_GPIO": f"GPIO {relay_diaphragm_gpio:g}",
        # PSU specs.
        "PSU_POWER": f"{psu_power_w:g} W",
        "PSU_VOLTAGE": f"{psu_voltage_v:g} V",
        "PSU_CURRENT": f"{psu_current_a:g} A",
        "PSU_MASS": f"~{psu_mass_g:g} g",
        # GFCI specs.
        "GFCI_TRIP": f"{gfci_trip_threshold_ma:g} mA",
        "GFCI_SELF_TEST": f"{gfci_self_test_interval_s:g} seconds",
        # AC pigtail lengths.
        "PIGTAIL_SHORT": f"~{pigtail_short_mm:g} mm",
        "PIGTAIL_MEDIUM": f"~{pigtail_medium_mm:g} mm",
        "PIGTAIL_SLACK": f"~{pigtail_slack_mm:g} mm",
        "PIGTAIL_COMPRESSOR": f"~{pigtail_compressor_mm:g} mm",
        # Wire-stock pigtail.
        "KESZOOX_LENGTH": f"{keszoox_length_cm:g} cm",
        # Wago count.
        "WAGO_COUNT": f"{wago_count:g}",
        # JST harness counts.
        "JST_4PIN_COUNT": f"~{jst_4pin_count:g}",
        "JST_6PIN_COUNT": f"~{jst_6pin_count:g}",
        "JST_9PIN_COUNT": f"~{jst_9pin_count:g}",
        # DS18B20 pull-up.
        "DS18B20_PULLUP": f"{ds18b20_pullup_kohm:g} kΩ",
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
            "PIGTAIL_SHORT": 2,
            "PIGTAIL_MEDIUM": 2,
            "PIGTAIL_SLACK": 1,
            "PIGTAIL_COMPRESSOR": 3,
            "KESZOOX_LENGTH": 2,
            "WAGO_COUNT": 1,
            "JST_4PIN_COUNT": 1,
            "JST_6PIN_COUNT": 1,
            "JST_9PIN_COUNT": 1,
            "DS18B20_PULLUP": 1,
        },
    )
    print("-> electronics-shelf.md")


if __name__ == "__main__":
    main()
