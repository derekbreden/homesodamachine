# ESP32-DevKitC-32E on DIN-rail breakout — reference solid

The controller-tray MCU (`hardware/ledger/bom.md`: ESP32 **B09MQJWQN2** on DIN-rail
breakout **B0BW4SJ5X2**). The carrier is what bolts to the tray (the DevKitC
plugs into it), so the footprint and mounting holes are the carrier's.

**Estimated stand-in — verify by caliper.** No controlled drawing for the
breakout; the carrier size and hole pattern are typical-module guesses.

| | mm |
|---|---|
| Carrier footprint | **100 × 66** (est.) |
| Mounting holes | 4× ⌀3.2 on an **88 × 56** rectangle (est.) |
| Height | ~15 (ESP32 module + sockets); screw-terminal strips down both edges |

Frame: X = length, Y = width, Z up from the carrier underside; origin at the
footprint centre, Z = 0 the standoff plane. Regenerate with
`tools/cad-venv/bin/python esp32_din_breakout.py`.
