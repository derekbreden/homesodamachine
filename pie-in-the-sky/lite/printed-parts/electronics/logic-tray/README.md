# Logic tray (controller + driver group) — Lite

The low-voltage logic block of the Lite electronics shelf — the MCU, its I²C bus,
and the 12 V drivers — on one printed frame. The Lite folds the Kitchen edition's
two trays ([controller](/hardware/printed-parts/electronics/controller-tray/) +
[driver](/hardware/printed-parts/electronics/driver-tray/)) into a single tray: it
carries one MCP23017 and no DS3231, so the whole logic set packs onto one floor.

Built by the shared [`module_tray`](/hardware/printed-parts/electronics/module_tray.py)
engine, same idioms as the [power tray](/pie-in-the-sky/lite/printed-parts/electronics/power-tray/):
boards pack **flush**, a **single convex-outline floor**, **no walls**, **heat-set
standoff bosses**.

## What mounts here

- **[ESP32-DevKitC-32E on its DIN-rail breakout](/hardware/reference/esp32-din-breakout/)** — the dispense MCU
- **[L298N](/hardware/reference/l298n/)** — dual H-bridge for the two Kamoer peristaltic pumps; also makes the 5 V logic rail
- **2× [ULN2803A](/hardware/reference/uln2803a/)** — sink the 12 manifold-solenoid coils to GND
- **[MCP23017](/hardware/reference/mcp23017/)** — I²C GPIO expander driving the 12-solenoid bank (one expander — the Lite has no reed inputs)
- **[TTL→RS485 transceiver](/hardware/reference/rs485-transceiver/)** — base side of the SIG-7 link to the front 4.3″ config display

Off this tray: the 12 V + AC switching lives on the
[power tray](/pie-in-the-sky/lite/printed-parts/electronics/power-tray/); the 12 V
feed and the ground bond cross between the two.

## Layout & retention

ESP32 breakout at the lower-left; the L298N flush to its right; the two ULN2803As
stacked in the next column; the MCP23017 + RS485 stacked in the last column.
Footprint ≈ **190 × 55 mm**. Each board screws onto heat-set standoff bosses sized
per its holes — **M3** for the ESP32, L298N, ULN2803A, and RS485; **M2** for the
MCP23017 (its holes are ⌀2). **16 heat-set bosses** total (ESP32 4 + L298N 4 +
ULN2803A 2×2 + MCP23017 2 + RS485 2).

Local frame: X right, Y deep, Z up; origin at the floor's bottom-left corner,
Z = 0 the floor underside, floor top at `floor_t`. The tray stands vertical in the
front-right of the cabinet, beside the [power tray](/pie-in-the-sky/lite/printed-parts/electronics/power-tray/);
it is placed by [`../../../enclosure-assembly/_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py).

> Two caveats carried from the board research: the **MCP23017 mounts cantilevered**
> (both holes on one short end), and the **ESP32 breakout is natively a 35 mm
> DIN-rail board** with an estimated footprint — on this tray it sits on placeholder
> bosses; verify by caliper.

The geometry engine (the floor, the bosses, the `Mount` placement) is **reused**
from the shared [`module_tray`](/hardware/printed-parts/electronics/module_tray.py);
this module only declares the Lite board set and its layout.

`logic_tray.py` → `logic-tray.step`; `logic_assembly.py` → `logic-assembly.step`
(tray + boards seated). Regenerate with `tools/cad-venv/bin/python <script>`.

## Sources

Board footprints and hole patterns are read from the reference modules — no
dimensions are invented here:

- `/hardware/reference/esp32-din-breakout/esp32_din_breakout.py`
- `/hardware/reference/l298n/l298n.py`
- `/hardware/reference/uln2803a/uln2803a.py`
- `/hardware/reference/mcp23017/mcp23017.py`
- `/hardware/reference/rs485-transceiver/rs485_transceiver.py`

The floor / boss conventions come from `/hardware/printed-parts/electronics/module_tray.py`.
