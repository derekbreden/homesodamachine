# DS3231 RTC — reference solid

The I²C real-time clock on the controller tray (`hardware/ledger/bom.md`:
**B09LLMYBM1**), I²C address 0x68.

**Estimated stand-in — verify by caliper.** Common ZS-042 form factor.

| | mm |
|---|---|
| Footprint | **38 × 22** (est.) |
| Mounting holes | 4× ⌀3.0 on a **32 × 16** rectangle (est.) |
| Height | ~14 (coin-cell holder on top) |

Frame: X = length, Y = width, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the standoff plane. Regenerate with
`tools/cad-venv/bin/python ds3231_rtc.py`.
