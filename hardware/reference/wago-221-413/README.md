# WAGO 221-413 — reference solid

The AC distribution block on the [AC hub](/hardware/printed-parts/electronics/ac-hub/):
three **3-conductor COMPACT lever-nut** splicing connectors (`hardware/ledger/bom.md`
§11), one each for H / N / G. Rated 32 A, 450 V; accepts 24–12 AWG.

`wago-221-413.step` is a generated stand-in. Body geometry is from the official
WAGO 221-413 datasheet; the connector has **no mounting holes** (it is a free
splice), so the AC hub retains each one in a **printed press-fit pocket**.

## Geometry

| | mm |
|---|---|
| Body envelope (W × D × H) | **18.8 × 18.6 × 8.4** |
| Mass | ~2.5 g |
| Wires | enter the −Y face; 3 levers on the +Z face |
| Lever-open clearance | **~15.25 mm** (measured, levers fully up) — a pocket must clear this if the levers are worked in place |

In the file's frame: X = width / lever-hinge axis (18.8), Y = depth / wire-entry
axis (18.6), Z up; origin at the footprint center, Z = 0 the seating plane. The
datasheet figures are slightly generous vs. calipered (H ≈ 8.25 measured) — treat
the body envelope as loose by ~0.15 mm. Regenerate with
`tools/cad-venv/bin/python wago_221_413.py`.
