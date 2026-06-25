"""Doc-sync driver for hardware/assembly/firmware-and-commissioning.md.

Run: tools/cad-venv/bin/python hardware/assembly/_firmware_and_commissioning_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── ESP32 pin assignments ────────────────────────────────────────────
# Source: hardware/wiring/esp32-pinout.mmd.

gpio_relay1 = 17            # Teyleten relay #1 (compressor AC)
gpio_onewire = 14           # DS18B20 1-wire bus (tank-wall + suction-line)
gpio_flow = 23              # DIGITEN flow meter pulse input
gpio_relay2 = 16            # Teyleten relay #2 (diaphragm pump 12 V refill)

# ─── I²C device addresses ─────────────────────────────────────────────
# 7-bit addresses on the shared SDA/SCL bus (GPIO 21/22).

mcp_valves_addr = 0x20      # MCP23017: 8 valves on PA[0:7] -> ULN U4, Rsvr A reeds on PB[0:3]
mcp_reservoirs_addr = 0x21  # MCP23017: 4 valves PA[0:3] + cond-fan PA4 -> ULN U5; Rsvr B reeds PB[0:3], carbonator reeds PB[4:5]
rtc_addr = 0x68             # DS3231 RTC

# Carbonator reeds ride the 0x21 MCP23017 on its internal pull-ups (no externals).
reed_low_loc = "0x21 PB4"   # Carbonator reed low (refill threshold)
reed_high_loc = "0x21 PB5"  # Carbonator reed high (full threshold)

# ─── Sensor inventory ─────────────────────────────────────────────────

valve_count = 12            # Beduan solenoids: 8 on 0x20 + 4 on 0x21 → ULN2803A U4/U5
reservoir_count = 2         # Flavor reservoirs (A + B)
reeds_per_reservoir = 4     # Float-rod reeds per reservoir
reeds_carbonator = 2        # Carbonator low + high reeds
reeds_total = (
    reservoir_count * reeds_per_reservoir + reeds_carbonator
)                           # = 10

# ─── Voltage-rail commissioning thresholds (bench multimeter check) ──

rail_12v_nominal = 12.0     # V — Mean Well IRM-90-12ST output
rail_12v_tol = 0.2          # V — ±, no-load expected window
rail_5v_nominal = 5.0       # V — 5 V LDO/buck feeds MCUs + relay-module VCC
rail_5v_tol = 0.1           # V — ±, bench-acceptance window
rail_33v_nominal = 3.3      # V — 3.3 V LDO feeds I²C pull-ups + MCP logic
rail_33v_tol = 0.05         # V — ±, bench-acceptance window

# ─── DS18B20 + onewire ────────────────────────────────────────────────
onewire_pullup_kohm = 4.7   # 1-wire data-line pull-up
ds18b20_count = 2           # Tank-wall + suction-line probes on the bus
ambient_tol_c = 2           # ±, room-ambient sensor-health check

# ─── Firmware factory-default setpoints (refrigeration control) ───────

tank_target_c = 2           # Tank-wall DS18B20 target
hysteresis_c = 2            # ±, around the tank target
comp_on_temp_c = tank_target_c + hysteresis_c   # = 4 — compressor turns on
comp_off_temp_c = tank_target_c                  # = 2 — compressor turns off
freeze_cutoff_c = -8        # Suction-line freeze-protect cutoff
min_off_time_min = 3        # Compressor start-capacitor minimum off-time


def main():
    variables = {
        # Pin assignments (decimal GPIO numbers in the doc's prose).
        "GPIO_RELAY1": f"GPIO {gpio_relay1:d}",
        "GPIO_ONEWIRE": f"GPIO {gpio_onewire:d}",
        "REED_LOW": reed_low_loc,
        "REED_HIGH": reed_high_loc,
        "GPIO_FLOW": f"GPIO {gpio_flow:d}",
        # I²C addresses — formatted as 7-bit hex (0xNN).
        "MCP_VALVES": f"0x{mcp_valves_addr:02x}",
        "MCP_RESERVOIRS": f"0x{mcp_reservoirs_addr:02x}",
        "RTC_ADDR": f"0x{rtc_addr:02x}",
        # Sensor counts.
        "VALVE_COUNT": f"{valve_count:d}",
        "RSVR_COUNT": f"{reservoir_count:d}",
        "REEDS_PER_RSVR": f"{reeds_per_reservoir:d}",
        "REEDS_CARB": f"{reeds_carbonator:d}",
        "REEDS_TOTAL": f"{reeds_total:d}",
        # Voltage-rail tolerances (nominal V written without trailing .0).
        "RAIL_12V": f"{rail_12v_nominal:.4g} V",
        "RAIL_12V_TOL": f"± {rail_12v_tol:.4g} V",
        "RAIL_5V": f"{rail_5v_nominal:.4g} V",
        "RAIL_5V_TOL": f"± {rail_5v_tol:.4g} V",
        "RAIL_33V": f"{rail_33v_nominal:.4g} V",
        "RAIL_33V_TOL": f"± {rail_33v_tol:.4g} V",
        # DS18B20 / onewire.
        "ONEWIRE_PULLUP": f"{onewire_pullup_kohm:.4g} kΩ",
        "AMBIENT_TOL": f"±{ambient_tol_c:.4g} °C",
        # Setpoints (factory defaults on `main`).
        "TANK_TARGET": f"{tank_target_c:.4g} °C",
        "HYSTERESIS": f"±{hysteresis_c:.4g} °C",
        "COMP_ON_TEMP": f"{comp_on_temp_c:.4g} °C",
        "COMP_OFF_TEMP": f"{comp_off_temp_c:.4g} °C",
        "FREEZE_CUTOFF": f"−{abs(freeze_cutoff_c):.4g} °C",
        # Three surface forms: "3-minute", "3-min", "3 min".
        "MIN_OFF_TIME": f"{min_off_time_min:.4g}-minute",
        "MIN_OFF_TIME_HYPHEN": f"{min_off_time_min:.4g}-min",
        "MIN_OFF_TIME_BARE": f"{min_off_time_min:.4g} min",
    }

    substitute_md(
        _here / "firmware-and-commissioning.md",
        variables=variables,
        expected_counts={
            # Pin assignments.
            "GPIO_RELAY1": 1,
            "GPIO_ONEWIRE": 1,
            "REED_LOW": 2,
            "REED_HIGH": 1,
            "GPIO_FLOW": 1,
            # I²C addresses.
            "MCP_VALVES": 5,
            "MCP_RESERVOIRS": 5,
            "RTC_ADDR": 3,
            # Sensor counts.
            "VALVE_COUNT": 4,
            "RSVR_COUNT": 1,
            "REEDS_PER_RSVR": 1,
            "REEDS_CARB": 1,
            "REEDS_TOTAL": 3,
            # Voltage-rail tolerances.
            "RAIL_12V": 5,
            "RAIL_12V_TOL": 1,
            "RAIL_5V": 4,
            "RAIL_5V_TOL": 1,
            "RAIL_33V": 4,
            "RAIL_33V_TOL": 1,
            # DS18B20 / onewire.
            "ONEWIRE_PULLUP": 2,
            "AMBIENT_TOL": 2,
            # Setpoints.
            "TANK_TARGET": 3,
            "HYSTERESIS": 3,
            "COMP_ON_TEMP": 2,
            "COMP_OFF_TEMP": 2,
            "FREEZE_CUTOFF": 3,
            "MIN_OFF_TIME": 4,
            "MIN_OFF_TIME_HYPHEN": 1,
            "MIN_OFF_TIME_BARE": 1,
        },
    )
    print("-> firmware-and-commissioning.md")


if __name__ == "__main__":
    main()
