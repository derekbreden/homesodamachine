# L298N dual H-bridge module — reference solid

The peristaltic-pump driver on the driver tray (`hardware/ledger/bom.md`:
**B0C5JCF5RS**) — drives both Kamoer pumps; its onboard 78M05 also makes the 5 V
logic rail.

The classic red L298N module: footprint and hole pattern are well established;
the heatsink height is approximate.

| | mm |
|---|---|
| Footprint | **43.5 × 43.5** |
| Mounting holes | 4× ⌀3.2 on a **37.5 × 37.5** square |
| Height | ~27 (finned heatsink) |

Frame: X = length, Y = width, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the standoff plane. Regenerate with
`tools/cad-venv/bin/python l298n.py`.
