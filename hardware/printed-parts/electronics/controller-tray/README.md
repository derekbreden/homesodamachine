# Controller tray (logic / I²C group)

The logic block of the Zone-B electronics shelf — the MCU and its I²C bus. Built
by the shared [`module_tray`](/hardware/printed-parts/electronics/module_tray.py)
engine, same idioms as the [power tray](/hardware/printed-parts/electronics/power-tray/):
boards pack **flush**, a **single convex-outline floor**, **no walls**, **heat-set
M3 bosses**.

## What mounts here

- **[ESP32-DevKitC-32E on its DIN-rail breakout](/hardware/reference/esp32-din-breakout/)** — the MCU
- **2× [MCP23017](/hardware/reference/mcp23017/)** — I²C GPIO expanders (0x20, 0x21)
- **[DS3231 RTC](/hardware/reference/ds3231-rtc/)** — I²C clock
- **[TTL→RS485 transceiver](/hardware/reference/rs485-transceiver/)** — base side of the SIG-7 link to the front 4.3″ display

Off this tray: the 12 V switching lives on the [driver tray](/hardware/printed-parts/electronics/driver-tray/);
the MCP→ULN control ribbons cross between the two.

## Layout & retention

ESP32 breakout at the lower-left; the two MCP23017s stacked just to its right;
the DS3231 + RS485 in the next column. Each board screws onto heat-set standoff
bosses sized per its holes — **M2** for the MCP23017 (⌀2), the DS3231 (⌀2.4), and
the RS485 (⌀2, 4 holes in the corners). Two caveats from the research: the
**MCP23017 mounts cantilevered** (both holes on one end), and the **ESP32 breakout
is natively a 35 mm DIN-rail board** — on this tray it sits on placeholder bosses,
but it may instead want a printed DIN-rail segment.

> The **MCP23017, DS3231, and RS485 are now calipered** from the physical boards —
> MCP23017 38.5 × 23.3, ⌀2 M2 holes 18.8 apart at one end; DS3231 38.5 × 21.3,
> 3× ⌀2.4 M2 holes (one corner left open for the coin cell); RS485 51.85 × 22.75,
> 4× ⌀2 M2 holes in the corners. See their references
> ([MCP23017](/hardware/reference/mcp23017/), [DS3231](/hardware/reference/ds3231-rtc/),
> [RS485](/hardware/reference/rs485-transceiver/)). The **ESP32 DIN-breakout
> footprint stays estimated** (the listing publishes pitches, not overall size) —
> verify by caliper.

`controller_tray.py` → `controller-tray.step`; `controller_assembly.py` →
`controller-assembly.step`. Regenerate with `tools/cad-venv/bin/python <script>`.
