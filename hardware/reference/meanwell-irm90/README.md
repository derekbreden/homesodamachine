# Mean Well IRM-90-12ST — reference solid

The appliance's 12 V supply (`hardware/ledger/bom.md` §1): an encapsulated
**12 V / 6.7 A, ~80 W** AC-DC power module, screw-terminal ("ST") variant. It is
the heaviest item on the [electronics shelf](/hardware/assembly/electronics-shelf.md)
and its AC→DC anchor — AC mains in on one end, the 12 V bus out the other. Its
potted base lies flat on the top foam cap's lid, on four of the cap's own
deck-mount columns.

`meanwell-irm90.step` is a generated stand-in for layout, not the real potted
module. Geometry is from the official Mean Well IRM-90-SPEC mechanical drawing
(screw-terminal style), cross-checked against distributor drawings.

## Geometry

| | mm |
|---|---|
| Envelope (W × L × H) | **52 × 109 × 33.5** |
| Mass | ~219 g |
| Mounting | 4× ⌀3.5 (M3) on a **33 × 98 mm** rectangle — centers at (±16.5, ±49) from the footprint center |
| Terminal ledges | both short ends step down to **6.7 mm**; AC 2-pole block (7.5 mm pitch) at +Y, DC 4-pole block (5 mm pitch) at −Y |

In the file's frame: X = width (52), Y = length (109), Z up from the base; origin
at the footprint center, Z = 0 the mounting plane.

The mounting-tab outline/thickness isn't dimensioned by the datasheet, so the
ledge + terminal-block shapes here are representative; the **envelope and the
hole pattern are exact**. Regenerate with
`tools/cad-venv/bin/python meanwell_irm90.py`.
