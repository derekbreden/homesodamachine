# WAGO 221-413 — reference solid

Every distribution splice in the machine: **five 3-conductor COMPACT lever-nut**
connectors (`hardware/ledger/bom.md` §11) — H / N / G for the AC mains and + / GND
for the 12 V rails. Rated 32 A, 450 V; accepts 24–12 AWG.

`wago-221-413.step` is a generated stand-in. Body geometry is from the official
WAGO 221-413 datasheet; the connector has **no mounting holes** (it is a free
splice), so the enclosure's +X wall stands each one on its butt end in a **printed
press-fit well** grown into its own inner face (`enclosure._east_wells`), ports
facing the room. There is no carrier part.

## Geometry

| | mm |
|---|---|
| Body envelope (W × D × H) | **18.8 × 18.6 × 8.4** |
| Mass | ~2.5 g |
| Wires | enter the +Y face; 3 levers on the +Z face above it |
| Lever-open clearance | **~15.25 mm** off the seating plane (measured, levers fully up) — a retainer must clear this if the levers are worked in place |

In the file's frame: X = width / lever-hinge axis (18.8), Y = depth / wire-entry
axis (18.6), Z up; origin at the footprint center, Z = 0 the seating plane. The
datasheet figures are slightly generous vs. calipered (H ≈ 8.25 measured) — treat
the body envelope as loose by ~0.15 mm. Regenerate with
`tools/cad-venv/bin/python wago_221_413.py`.
