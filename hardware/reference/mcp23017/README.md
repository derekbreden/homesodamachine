# MCP23017 I²C GPIO expander — reference solid

Used 2× on the controller tray (0x20, 0x21) as the valve / reed / fan I/O
expanders (`hardware/ledger/bom.md`: **B07P2H1NZG**).

**Estimated stand-in — verify by caliper.** Generic reseller breakout, no
controlled drawing.

| | mm |
|---|---|
| Footprint | **35 × 25** (est.) |
| Mounting holes | 4× ⌀3.0 on a **30 × 19** rectangle (est. — some variants have 2 or none) |
| Height | ~12 |

Frame: X = length, Y = width, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the standoff plane. Regenerate with
`tools/cad-venv/bin/python mcp23017.py`.
