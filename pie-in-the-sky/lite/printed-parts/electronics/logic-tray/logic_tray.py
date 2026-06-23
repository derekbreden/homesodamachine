"""Lite logic tray — the controller + driver block of the Lite electronics shelf.

One tray carries the whole low-voltage logic set: the ESP32 (on its DIN-rail
breakout), the MCP23017 I2C GPIO expander, both ULN2803A solenoid drivers, the
L298N pump driver, and the TTL-to-RS485 transceiver. The Lite folds the Kitchen
edition's two trays (controller + driver) into one — it has a single MCP23017
and no DS3231, so the combined set fits one compact frame.

Same idioms as the rest of the shelf: boards pack flush, a single
convex-outline floor, no walls, heat-set standoff bosses (M3 per board, M2 for
the MCP23017's 2 mm holes). Built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine.

Layout: ESP32 breakout at the lower-left; the L298N flush to its right; the two
ULN2803As stacked in the next column; the MCP23017 + RS485 stacked in the last
column. Local frame: X right, Y deep, Z up; origin at the floor's bottom-left
corner.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
_hw = _repo / "hardware"
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
for _r in ("esp32-din-breakout", "mcp23017", "uln2803a", "l298n", "rs485-transceiver"):
    sys.path.insert(0, str(_hw / "reference" / _r))
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step
import module_tray as mt
from module_tray import Mount
import esp32_din_breakout as esp32
import mcp23017 as mcp
import uln2803a as uln
import l298n
import rs485_transceiver as rs485

m = mt.margin

# ESP32 breakout lower-left; L298N flush to its right; the two ULN2803As stacked
# in the next column; the MCP23017 + RS485 stacked in the last column.
_esp_c = (m + esp32.length / 2.0, m + esp32.width / 2.0)
_esp_r = m + esp32.length
_l_cx = _esp_r + l298n.length / 2.0
_l_r = _esp_r + l298n.length
_uln_cx = _l_r + uln.length / 2.0
_uln_r = _l_r + uln.length
_last_cx = _uln_r + max(mcp.length, rs485.length) / 2.0

MOUNTS = [
    Mount(esp32, _esp_c, 0.0),
    Mount(l298n, (_l_cx, m + l298n.width / 2.0), 0.0),
    Mount(uln, (_uln_cx, m + uln.width / 2.0), 0.0),
    Mount(uln, (_uln_cx, m + uln.width + uln.width / 2.0), 0.0),
    Mount(rs485, (_last_cx, m + rs485.width / 2.0), 0.0),
    Mount(mcp, (_last_cx, m + rs485.width + mcp.width / 2.0), 0.0),
]


def build_logic_tray():
    return mt.build_module_tray(MOUNTS)


def main():
    export_step(build_logic_tray(), str(_here.parent / "logic-tray.step"))
    print("-> logic-tray.step")


if __name__ == "__main__":
    main()
