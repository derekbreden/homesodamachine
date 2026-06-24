"""Controller tray — the logic / I2C group of the Zone-B electronics shelf.

Carries the ESP32 (on its DIN-rail breakout), both MCP23017 I2C GPIO expanders,
the DS3231 RTC, and the TTL-to-RS485 transceiver. Same idioms as the power tray:
boards pack flush, a single convex-outline floor, no walls, heat-set bosses sized
per board (M2 for the MCP23017, DS3231, and RS485; the RS485 takes 4 corner
bosses). Built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine.

Layout: ESP32 breakout at the left; the two MCP23017s stacked just to its right;
the DS3231 + RS485 in the next column. Local frame: X right, Y deep, Z up; origin
at the floor's bottom-left corner.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
for _r in ("esp32-din-breakout", "mcp23017", "ds3231-rtc", "rs485-transceiver"):
    sys.path.insert(0, str(_hw / "reference" / _r))
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step
import module_tray as mt
from module_tray import Mount
import esp32_din_breakout as esp32
import mcp23017 as mcp
import ds3231_rtc as ds3231
import rs485_transceiver as rs485

m = mt.margin

# ESP32 breakout lower-left; small boards flush to its right.
_esp_c = (m + esp32.length / 2.0, m + esp32.width / 2.0)
_esp_r = m + esp32.length
_mcp_cx = _esp_r + mcp.length / 2.0
_mcp_r = _esp_r + mcp.length
_ds_cx = _mcp_r + ds3231.length / 2.0
_rs_cx = _mcp_r + rs485.length / 2.0

MOUNTS = [
    Mount(esp32, _esp_c, 0.0),
    Mount(mcp, (_mcp_cx, m + mcp.width / 2.0), 0.0),
    Mount(mcp, (_mcp_cx, m + mcp.width + mcp.width / 2.0), 0.0),
    Mount(ds3231, (_ds_cx, m + ds3231.width / 2.0), 0.0),
    Mount(rs485, (_rs_cx, m + ds3231.width + rs485.width / 2.0), 0.0),
]


def build_controller_tray():
    return mt.build_module_tray(MOUNTS)


def main():
    export_step(build_controller_tray(), str(_here.parent / "controller-tray.step"))
    print("-> controller-tray.step")


if __name__ == "__main__":
    main()
