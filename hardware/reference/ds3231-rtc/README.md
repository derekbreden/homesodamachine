# DS3231 RTC module — reference solid

The I²C real-time clock on the controller tray (`hardware/ledger/bom.md`:
**B09LLMYBM1** = the DORHEA DS3231 + AT24C32 board), RTC at **0x68**; the onboard
AT24C32 EEPROM sits at **0x57** on the same bus.

Geometry **calipered from the physical board**. Frame matches the `module_tray`
convention: **X = length = the 38.5 mm long axis, Y = width = the 21.3 mm short
axis**, origin at the footprint centre.

| Feature | Measurement |
|---|---|
| Footprint | **38.5 (X, length) × 21.3 (Y, width)** mm |
| Mounting holes | **3 × ⌀2.4 (M2)** at (−10.75, ±8.65) and (15.05, 8.65); the 4th corner is left open for the coin-cell holder |
| 6-pin header | **2.54 mm**, along Y at the −X short end (X = −17.25), span 12.7 |
| 4-pin header | **2.54 mm**, along Y at the +X short end (X = +17.25), span 7.62 |

**Pinouts.** The 6-pin header (one short end), top→bottom along +Y→−Y:
**32K · SQW · SCL · SDA · VCC · GND**. The 4-pin header (other short end),
+Y→−Y: **SCL · SDA · VCC · GND**.

The two headers are the **same I²C bus** — the 4-pin is just the VCC/GND/SDA/SCL
subset, a clean tap point; the carrier wires one of them. **SQW** (programmable
square-wave) and **32K** (32.768 kHz) outputs are unused. VCC runs at 3.3 V to
keep the bus at one logic level. The module carries its own I²C pull-ups, the
TCXO, and the coin-cell backup, so the carrier adds none.

Regenerate the solid with `tools/cad-venv/bin/python ds3231_rtc.py`.
