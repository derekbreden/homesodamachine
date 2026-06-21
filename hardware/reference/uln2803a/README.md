# ULN2803A Darlington driver module — reference solid

Used 2× on the driver tray (`hardware/ledger/bom.md`: **B0F872W528**, 2-pc) — sink
the 12 solenoid coils + the condenser fan to GND; COM tied to 12 V for flyback.

**Estimated stand-in — verify by caliper.** Generic reseller module with
input/output screw terminals, no controlled drawing.

| | mm |
|---|---|
| Footprint | **65 × 33** (est.) |
| Mounting holes | 4× ⌀3.0 on a **58 × 26** rectangle (est.) |
| Height | ~12 (terminal strips both long edges) |

Frame: X = length, Y = width, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the standoff plane. Regenerate with
`tools/cad-venv/bin/python uln2803a.py`.
