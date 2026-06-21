# TTL-to-RS485 transceiver — reference solid

The ALMOCN auto-direction RS485 module on the controller tray
(`hardware/ledger/bom.md`: **B09998FY4X**) — base side of the SIG-7 link to the
front 4.3″ config display (the 4.3B has onboard RS485).

**Estimated stand-in — verify by caliper.** Tiny breakout with **no mounting
holes** — modelled with `holes = []`, so the tray gives it no bosses; it rides on
adhesive / tucks against a neighbour.

| | mm |
|---|---|
| Footprint | **40 × 18** (est.) |
| Height | ~11 |

Frame: X = length, Y = width, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the seating plane. Regenerate with
`tools/cad-venv/bin/python rs485_transceiver.py`.
