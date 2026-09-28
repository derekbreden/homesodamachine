# Printing the reservoir watertight in PETG

The starting point is the **physically successful Bambu PETG Basic recipe**.
[Print attempt 3](print-log.md) records hours of water retention with the
gaskets installed. Its archived project and extracted active-nozzle settings
are identified in [petg-water-recipe.json](../magnetic-float/petg-water-recipe.json).
This result establishes water holding at reservoir head; it supplies no measured
pressure rating. Later PETG Translucent projects have a different material and
recipe and no success result recorded in that log.

## Proven printing basis

| Parameter | Successful PETG Basic reservoir |
| --- | --- |
| Printer / active nozzle | H2C / left 0.6 mm standard flow |
| Nozzle temperature, first / subsequent | 255 / 260 °C |
| Flow ratio / maximum volumetric speed | 1.02 / 21 mm³/s |
| Textured bed | 70 °C |
| Layer height, first / subsequent | 0.30 / 0.18 mm |
| Requested line width / wall loops | 0.60 mm / six, Arachne |
| Wall / floor material depth | 3 mm |
| Fill / wall overlap | 100% zig-zag / 15% |
| Top / bottom pattern | Zig-zag |
| Top ironing | 10% flow, 0.15 mm spacing, 30 mm/s |
| Wall order | Inner then outer |
| Seam | Random; conditional scarf on all walls, 10% start height; 15% seam gap |
| Ordinary cooling | Part fan 10–20%, first three layers off; auxiliary off |

The source recipe also permits 90% overhang cooling for the supported reservoir
floor. These are observed settings, not a universal PETG preset. The
[magnetic float](../magnetic-float/petg-shell.md) specifies its own slower paths,
zero seam gap, unconditional scarf and lower overhang cooling for a roof backed
by an insert. Its adaptations are separate from the physical reservoir result.

## The part and its seal

The reservoir is a vented, non-pressurized cup with 3 mm walls/floor and 6 mm
internal corner fillets. A separately printed cap clamps a TPU gasket through
six M3 fasteners. The PTFE vent equalizes headspace pressure. A 210 mm water
column produces about 0.3 psi at the floor; syrup head scales with its density.

The V-trough floor has a bulkhead penetration. A purchased silicone flat washer
in its wet-side counterbore is the primary seal, with a printed TPU washer on
the dry side and a locknut below. Use the sealing faces and controlled washer
compression; printed threads/barrel contact do not establish a liquid seal.

Cold service is 8–15 °C. Bare-print food-contact and taint acceptance is addressed
by [wetted-surface-test.md](wetted-surface-test.md), separately from leakage.

## What controls leakage

### Deposited paths and extrusion amount

Inspect the wall, corners, seam closures, floor/wall junction and bulkhead seat.
Arachne changes widths to fit the actual geometry; requested wall count is a
limit. Wall thickness need not be a whole multiple of requested line width.
The [0.8 mm seal trial](seal-trial.md), for example, has four nominally
overlapping paths across a straight 3 mm wall. That path description is not
a physical seal result.

**Flow is a principal sealing variable.** The successful 1.02 ratio is 5.15%
above its 0.97 stock baseline. Published experiments show large leakage changes
with extrusion amount; multiplier values do not transfer directly between
printers/materials. Use the successful local value for this PETG Basic recipe.
There is no evidence-based universal limit of a 2% adjustment.

Line width, infill overlap and flow are distinct. The slicer generally changes
path spacing with line width; widening the requested line is not equivalent
to adding material into an unchanged volume. Infill overlap acts at the
infill/perimeter junction. Excess flow can close pores but also change
dimensions, surface finish and assembly fit. Nominal 100% fill can retain voids.

### Layer height, temperature, speed and cooling

The successful 0.18 mm layer is 30% of the 0.6 mm nozzle diameter. Both Prusa's
water-holding work and independent leakage experiments support low layers.
Preserve solid floor thickness when changing layer height; a fixed layer count
does not preserve the amount of sealing material.

For **Bambu PETG Basic here, use 255/260 °C**. No retrieved evidence establishes
a universal PETG adhesion peak at 245–250 °C or a universal decline above
260 °C. Welding depends on material, actual melt temperature, extrusion rate,
cooling and the temperature of the receiving layer. Gloss is a surface
observation, not proof that the wall is fused or sealed.

Preserve the low ordinary cooling in the proven recipe and distinguish supported
overhang requirements from sealing-wall requirements. A nominal maximum speed
does not establish the speed actually reached: volumetric limits and layer-time
slowdowns also matter. The small float uses explicitly slower wall speeds.

### Seams, floor and moisture

Loop starts/stops and floor-to-wall junctions deserve particular inspection.
Random seam placement distributes starts between layers; it does not establish
that all adjacent loops have staggered starts. Scarf and seam-gap settings
change deposition at the closure. Inspect the emitted paths before treating
either setting as an airtightness guarantee.

Preserve the solid zig-zag floor and top ironing in the proven recipe. In a
new geometry, inspect both the perimeter/fill junction and the region above
supports. Neither an all-perimeter wall nor a particular fill pattern is
universally leak-proof; successful published prints use several arrangements.

Dry PETG Basic using the [shop drying table](/hardware/ledger/tools.md) and keep
it dry during printing. A dry-box humidity reading measures its air rather
than residual moisture inside the filament. Popping, bubbles or rough extrusion
merit investigation; visual quality alone cannot qualify a seal.

## Water-holding acceptance

Assemble the intended washers/gaskets and fill to the maximum service level.
Use a dry exterior and an absorbent witness beneath the seams and bulkhead to
localize any seepage. Record water level, temperature, duration and leak
location. A full, cold 24-hour hold is a useful acceptance observation; the
existing success record states **hours**, not a documented 24-hour hold.

The reservoir is vented and has no assigned pneumatic proof pressure. Pressure
vessel results belong to the [separate float pressure investigation](../magnetic-float/pressure-printing-research.md).
The reservoir's gasket/body water-holding result does not qualify a float
under external pressure.

## Coatings

The demonstrated reservoir recipe uses bare PETG. Published coated-print results
establish the performance of a particular coating/process/specimen. They do not
establish food-contact suitability of an arbitrary epoxy or a universal cure
schedule. Any proposed wetted coating needs a named product, manufacturer
instructions and acceptance against the intended concentrate and cold service.

## Research basis

- [Prusa: open water-holding models](https://blog.prusa3d.com/watertight-3d-printing-pt1-vases-cups-and-other-open-models_48949/).
- [Prusa: closed models under external pressure](https://blog.prusa3d.com/watertight-3d-printing-part-2_53638/).
- [Gordeev et al.: extrusion amount, wall structure and connected pores](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198370).
- [Pressure-printing research and source-file audit](../magnetic-float/pressure-printing-research.md): positive and negative pressure results, test durations, post-processing and limits on transferring published recipes.
