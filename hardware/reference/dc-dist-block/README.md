# 12 V DC distribution block — reference solid (placeholder)

The 12 V + / GND rails on the driver tray — DC-1 in from the PSU secondary,
DC-2/4/6/8/9 out to the loads.

**Placeholder.** The DC-distribution hardware is not yet chosen (Wago 221 stack
vs. screw block vs. bus bar — see `hardware/assembly/electronics-shelf.md` Open
items). This is a generic terminal-block envelope just to hold the footprint;
replace once the part is picked.

| | mm |
|---|---|
| Footprint | **50 × 26** (placeholder) |
| Mounting holes | 2× ⌀3.2 end ears at ±22 |
| Height | ~18 |

Frame: X = length, Y = width, Z up from the underside; origin at the footprint
centre, Z = 0 the standoff plane. Regenerate with
`tools/cad-venv/bin/python dc_dist_block.py`.
