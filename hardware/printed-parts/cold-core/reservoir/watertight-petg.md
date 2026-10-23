# Printing the reservoir in PETG

[reservoir.3mf](reservoir.3mf) uses the **five-wall May Water adaptation**
through Mark1's right 0.8 mm Standard nozzle: **flow 1.05, 30% Infill/Wall overlap,
265/270 °C, no brim, zero added user Z trim and ironing Off**. Arachne uses its
10° default transition threshold. Mark1 task **1365626370** has a **reported
one-hour water hold** on its intentionally partially printed left body,
reported October 23, 2026. [Physical result](prints/2026-10-22-mark1-flow105-overlap30-right08-z000/physical-result/physical-result.json) ·
[Launch and startup](prints/2026-10-22-mark1-flow105-overlap30-right08-z000/README.md).
[Adaptation, wall-count comparison and installed preset facts](recipe-reviews/2026-10-22-flow105-overlap30/README.md).

The project's two plates contain
the current left and right body/cap pairs. [print-settings.json](print-settings.json) holds every saved machine,
filament and process setting; [reservoir.print.json](reservoir.print.json)
identifies the current geometry and project. The baseline water-hold acceptance source is
`may-30-clear-06` in [water-hold-acceptance.json](water-hold-acceptance.json).
Its water hold belongs to the historical May article. The most recent 59° article [still leaks at the bottom and has a new vertical-edge defect](prints/2026-10-22-mark1-walls-t59-right08-z000/physical-result/physical-result.json). The preceding walls-only article has [reported seam leakage](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json); corner-flatness and adhesion are not separately reported for that article.

## Current recipe

| Parameter | Value |
| --- | --- |
| Active nozzle | Mark1 right 0.8 mm, Standard flow |
| Filament | Bambu PETG Translucent Clear, GFG01 |
| Layer height, first / subsequent | 0.30 / 0.24 mm |
| Nozzle temperature, first / subsequent | 265 / 270 °C |
| Textured PEI bed, first / subsequent | 70 / 70 °C |
| Flow ratio / maximum volumetric speed | 1.05 / 21 mm³/s |
| Requested outer / inner wall speeds | 200 / 300 mm/s |
| Requested solid fill / sparse fill / top speeds | 250 / 350 / 200 mm/s |
| Requested wall width / wall loops | 0.80 mm / 5, Arachne; ordinary walls and curved corners entirely wall paths |
| Arachne wall transition angle | 10°, the Arachne default |
| Fill / top / first-layer width | 0.80 mm |
| Model fill | 100% zig-zag; top 3 layers with 0.8 mm minimum thickness; bottom 3 layers |
| Infill / Wall overlap | 30% |
| Floor construction | Modeled 3 mm floor, perimeter loops and solid fill |
| Top / bottom pattern | Zig-zag |
| Ironing, model and supports | Off |
| Wall order | Inner then outer |
| Seam | Random, scarf on all walls; inner walls included; conditional; gap 15% |
| Ordinary cooling | Part fan 10–20%; first three layers off; auxiliary off |
| Overhang cooling | 90% override |
| Supports | Tree auto, bed only, 30° threshold |
| Support top / bottom gap | 0.18 / 0.18 mm |
| Support interface top / bottom layers | Two / two |
| Saved printer trim | Mark1 clear PETG: zero added user trim |
| Brim | None; no native brim paths |

The start block clears user trim and emits **`G29.1 Z-0.02`**, the stock
Textured PEI compensation for this 0.8 mm nozzle. This clear PETG recipe has no
added Z lift. Its [first-layer failure record](prints/2026-10-20-mark1-right08/physical-result/physical-result.json)
and [retry](prints/2026-10-21-mark1-right08-z000/README.md) bind the correction to
this material and article. PET-GF profiles retain their own trim settings.

The project uses the May Water controls, with ironing disabled according to the
[flat-square finish selection](ironing-study/prints/2026-10-06-mark2-squares-v1/physical-result.json).
Its process and filament display names identify the current reservoir recipe.
Both plates explicitly assign the right nozzle in Manual mode. Use the matching
spool with the least filament remaining first and automatic refill to the other
matching stock; [printer guidance](../../../../tools/bambu-printers.md#mark1-clear-petg-spool-order)
records the consumption policy. Refresh actual slots before a future Send.
Bodies print mouth up with the floor underside on the bed; caps print exterior
face down with their gasket rims up. The matching cap belongs with its named
left or right body.

## Layer heights and wall generator

The recipe uses **0.24 mm** ordinary layers and a **0.30 mm** first layer.
Installed H2C 0.8 mm presets offer **0.24 mm Balanced Quality**, **0.32 mm Balanced
Quality/Strength** and **0.40 mm Standard**. Their first-layer height is 0.40 mm.
The machine profile allows custom layer heights from **0.16 to 0.56 mm**.
[Installed preset inheritance and hashes](recipe-reviews/2026-10-22-flow105-overlap30/installed-presets.json).

Those stock process presets inherit **Classic**. The recovered May project
selects **Arachne**, which varies bead widths and counts to fit the geometry.
Its **10°** wall-transition threshold is the [source-defined Arachne default](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp#L6395).

## The part and its seal

The reservoir is a vented cup with 3 mm walls/floor and 6 mm internal corner
fillets. Six M3 fasteners clamp a separate cap through a TPU gasket. The PTFE
vent equalizes headspace pressure. Cold service is 8–15 °C.

Nothing pierces the cup below its rim: both lines enter through the cap, and the
draw line goes on down to the floor as its own dip tube. The printed floor and
walls are the whole fluid barrier. [Floor and dip tube](floor-and-dip-tube.md)
describes them.

Five requested wall loops are the lowest tested count with only wall features
through both bodies' ordinary straight walls and thick curved corners. Counts
two through four retain fill there. Broad floor/cap faces and locally thicker
bosses retain solid fill. The [native comparison](recipe-reviews/2026-10-22-flow105-overlap30/wall-count-review.json)
examines the complete ordinary wall band, not just a nominal wall-width estimate.
Native coverage does not establish deposited fusion or water holding. Ironing
is disabled on every model and support surface.

Dry the actual stock using the [shop drying table](../../../ledger/tools.md)
and keep it dry during printing. A dry-box humidity reading describes the
surrounding air rather than residual moisture in the filament.

## Evidence and print records

The current five-wall / solid-floor recipe has a **reported one-hour water
hold** on the intentionally shortened task-1365626370 article. Retain its
selected settings as the current baseline. Exact printed height, water head
and cap/gasket assembly sealing are unspecified.
[Physical report](prints/2026-10-22-mark1-flow105-overlap30-right08-z000/physical-result/physical-result.json).

The preceding walls-only article has reported seam leakage. Its underside photograph shows
droplets along a branching floor junction resembling the native perimeter
convergence regions. [Physical result](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json).

The printed 59° transition trial adds center-wall paths at those junctions. The
[native comparison](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/seam-comparison.json)
shows about 72% less nominal layer-12 pocket area, with residual modeled pockets.
The printed article still leaks at the same reported location. The calculation supplies no demonstrated sealing benefit. A [wall-path reading](prints/2026-10-22-mark1-walls-t59-right08-z000/physical-result/wall-junction-review.json) identifies additional short extrusion segments near the curved-wall ends; their causal relation to the edge defect is unverified.

The preceding May-adapted left article has [reported floor-fill/perimeter leakage](prints/2026-10-21-mark1-may-water-right08-z000/physical-result/physical-result.json). The earlier zero-user-trim left article leaks at many places, as reported by
Derek. Its corner photographs show a distorted band near the floor-to-wall
transition. Neither the finished shape nor the limited live camera views
establishes an onset layer. The stopped job's
[terminal record](prints/2026-10-21-mark1-right08-z000/terminal-observation.json)
records the visibility limit and paused task-bound monitor.

The September 0.24 mm article held water, as reported by Derek. Its recovered
Mark2 slice estimated 20 h 7 min and 414.76 g; those estimates belong to that
historical geometry. The [current native slice review](slice-review.json)
estimates **5 h 42 min and 444 g** per body/cap plate, with **zero ironing**,
833 layers and an empty plate-warning field. The model/support/brim full bead
envelope stays at least **70.5 mm from the nearest right-nozzle usable bed edge**, including
arc extrema and bead width. The matching body and cap envelopes are 10.04 mm
apart.
The historical May and September results and complete source identifiers are
in the [print log](print-log.md), [September inspection](history/seal-trial.md)
and [acceptance record](water-hold-acceptance.json).

The reported water hold establishes the result for its printed article and
recipe. It supplies no measured pressure rating, specified cold hold duration
or aging result for the current geometry. Report observed seepage with its
location and hold conditions beside the part. Bare-print wetted acceptance is
addressed by [wetted-surface-test.md](wetted-surface-test.md).

## Research basis

- [Prusa: open water-holding models](https://blog.prusa3d.com/watertight-3d-printing-pt1-vases-cups-and-other-open-models_48949/).
- [Gordeev et al.: extrusion amount, wall structure and connected pores](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0198370).
- [Separate float pressure investigation](../magnetic-float/pressure-printing-research.md).
