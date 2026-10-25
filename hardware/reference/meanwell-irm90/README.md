# Mean Well IRM-90-12ST — reference solid

The appliance's 12 V supply (`hardware/ledger/bom.md` §1): an encapsulated
**12 V / 6.7 A, ~80 W** AC-DC power module, screw-terminal ("ST") variant. It is
mounted on the [dry west wall of back-top](/hardware/assembly/electronics-bay.md),
with AC mains in at its aft end and the 12 V bus out at its fore end. Its potted
base and four-hole mounting plane face the enclosure's −X wall. Four integral
wall hosts carry the module independently of the cold-core lid.

`meanwell-irm90.step` is a generated stand-in for layout, not the real potted
module. Geometry is from the official Mean Well IRM-90-SPEC mechanical drawing
(screw-terminal style), cross-checked against distributor drawings.

The production baseline retains this supply and its existing mounting geometry.
The [conditional electrical Plan B](/future/carbonation-plan-b.md) depends on
measured current and voltage under the intended load schedule.

## Geometry

| | mm |
|---|---|
| Envelope (W × L × H) | **52 × 109 × 33.5** |
| Mass | ~219 g |
| Mounting | 4× ⌀3.5 (M3) on a **33 × 98 mm** rectangle — centers at (±16.5, ±49) from the footprint center |
| Terminal ledges | both short ends step down to **6.7 mm**; AC 2-pole block (7.5 mm pitch) at +Y, DC 4-pole block (5 mm pitch) at −Y |

In the file's frame: X = width (52), Y = length (109), Z up from the base; origin
at the footprint center, Z = 0 the mounting plane.

The drawing dimensions the terminal-end ledges, which carry the four mounting
holes, at 6.7 mm (±1 mm general tolerance), so each mounting screw crosses 6.7 mm
of moulded ear ([`bom.md`](/hardware/ledger/bom.md) §13 sizes it). The ledge
outline and terminal blocks here are representative; the **envelope, ledge
height and hole pattern are the drawing's**. Regenerate with
`tools/cad-venv/bin/python meanwell_irm90.py`.

## Terminal access

AC wire entry faces +Y and DC entry −Y along the 109 mm axis. Screw heads
face +Z in this reference; in the appliance their access axes point +X.
`wire_entry()` separates the representative side-entry mouths from the
`ac_in()` / `dc_out()` screw-head planes. Block dimensions are representative.
The [assembly-fit review](../../printed-parts/enclosure/enclosure/assembly-fit-review/README.md)
records the module placement and installed-wire fit scope.
