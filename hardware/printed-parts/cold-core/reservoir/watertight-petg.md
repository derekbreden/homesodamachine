# Printing the reservoir watertight in PETG

The starting point is the **physically successful May 30 Bambu PETG clear recipe**.
[Print attempt 3](print-log.md) records hours of water retention with the
gaskets installed. The exact native project is
[`reservoir-water-hold-2026-05-30.3mf`](reservoir-water-hold-2026-05-30.3mf);
its extracted active-nozzle settings are in
[petg-water-recipe.json](../magnetic-float/petg-water-recipe.json).
The saved `Bambu PETG Water` preset carries PETG Basic's `GFG00` identity;
Derek confirms the actual filament was **Bambu PETG clear**. A saved preset
identity does not establish which filament was physically loaded.

Both September [0.8 mm recipes](seal-trial.md), at 0.18 and 0.24 mm layer
height, also held water, confirmed by Derek on 2026-10-05. Their recovered
Mark2 slices and the May project are identified in
[water-hold-acceptance.json](water-hold-acceptance.json).
These results establish water holding at reservoir head; they supply no measured
pressure rating. The May hold lasted several hours; the September report
specifies no duration, temperature or fill height.

## Proven printing basis

| Parameter | Successful May 30 Bambu PETG clear reservoir |
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
[separate PETG-shell bench float](../magnetic-float/petg-shell.md) specifies its own slower paths,
zero seam gap, unconditional scarf and lower overhang cooling for a roof backed
by an insert. Its adaptations are separate from the physical reservoir result.

## Accepted 0.8 mm recipes

Both September projects use PETG Translucent settings, 255 °C throughout,
flow 0.97, a 6 mm³/s volumetric limit and 30 mm/s requested wall/fill speeds.
They use six requested Arachne walls at 0.80 mm width, 100% zig-zag fill,
12-layer / 2 mm top and bottom shells, 20% normal cooling, aligned
unconditional scarf seams and zero seam gap. The first layer is 0.30 mm.
Normal layers are **0.18 or 0.24 mm**; the recovered printer slices estimate
**26 h 8 min or 20 h 7 min**, respectively. Both recipes have reported
water holds. [Complete settings and projects](seal-trial.md).

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
overlapping paths across a straight 3 mm wall. Its physical water-holding
result is recorded separately from the nominal path description.

**Flow is a principal sealing variable.** The successful 1.02 ratio is 5.15%
above its 0.97 stock baseline. Published experiments show large leakage changes
with extrusion amount; multiplier values do not transfer directly between
printers/materials. Use 1.02 when repeating the May 30 clear recipe; the
accepted September recipes use their own 0.97 flow.
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

For **the May 30 Bambu PETG clear recipe, use 255/260 °C**; both accepted
September recipes use 255/255 °C. No retrieved evidence establishes
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

Dry the actual PETG stock using the [shop drying table](/hardware/ledger/tools.md) and keep
it dry during printing. A dry-box humidity reading measures its air rather
than residual moisture inside the filament. Popping, bubbles or rough extrusion
merit investigation; visual quality alone cannot qualify a seal.

## Water-holding acceptance

Assemble the intended washers/gaskets and fill to the maximum service level.
Use a dry exterior and an absorbent witness beneath the seams and bulkhead to
localize any seepage. Record water level, temperature, duration and leak
location. A full, cold 24-hour hold is a useful acceptance observation; the
May success record states **hours**; neither September result specifies a
duration. No reported result establishes a documented cold 24-hour hold.

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
