# Printing the reservoir in PETG

[reservoir.3mf](reservoir.3mf) uses the **walls-only May Water recipe through Mark1's
right 0.8 mm Standard nozzle**, with **flow 1.02, no brim, zero added user Z
trim and ironing Off**. The left body/cap pair is accepted as task
**1362982574**. [Adaptation and launch](prints/2026-10-21-mark1-walls-only-right08-z000-a4/README.md).

The project's two plates contain
the current left and right body/cap pairs. [print-settings.json](print-settings.json) holds every saved machine,
filament and process setting; [reservoir.print.json](reservoir.print.json)
identifies the current geometry and project. The baseline water-hold acceptance source is
`may-30-clear-06` in [water-hold-acceptance.json](water-hold-acceptance.json).
Its water hold belongs to the historical May article. The current walls-only article has [reported seam leakage](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json); corner-flatness and adhesion are not separately reported.

## Current recipe

| Parameter | Value |
| --- | --- |
| Active nozzle | Mark1 right 0.8 mm, Standard flow |
| Filament | Bambu PETG Translucent Clear, GFG01 |
| Layer height, first / subsequent | 0.30 / 0.24 mm |
| Nozzle temperature, first / subsequent | 255 / 260 °C |
| Textured PEI bed, first / subsequent | 70 / 70 °C |
| Flow ratio / maximum volumetric speed | 1.02 / 21 mm³/s |
| Requested outer / inner wall speeds | 200 / 300 mm/s |
| Requested solid fill / sparse fill / top speeds | 250 / 350 / 200 mm/s |
| Requested wall width / wall loops | 0.80 mm / 999, Arachne; continue inward across each section |
| Fill / top / first-layer width | 0.80 mm |
| Model fill | 0% sparse; zero top/bottom shell fill; native model features are walls only |
| Saved infill / wall overlap | 15%; no model infill boundary in this slice |
| Floor construction | Modeled 3 mm floor filled with continued perimeters |
| Saved top / bottom pattern | Zig-zag; shell fill disabled |
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
Both plates explicitly assign the right nozzle in Manual mode. The Mark1
walls-only May Water article starts on **A4**, with matching-spool automatic refill;
[printer guidance](../../../../tools/bambu-printers.md#mark1-clear-petg-spool-order)
records the loaded material and refill scope. Bodies print mouth up
with the floor underside on the bed; caps print exterior face down with their
gasket rims up. The matching cap belongs with its named left or right body.

## The part and its seal

The reservoir is a vented cup with 3 mm walls/floor and 6 mm internal corner
fillets. Six M3 fasteners clamp a separate cap through a TPU gasket. The PTFE
vent equalizes headspace pressure. Cold service is 8–15 °C.

Nothing pierces the cup below its rim: both lines enter through the cap, and the
draw line goes on down to the floor as its own dip tube. The printed floor and
walls are the whole fluid barrier. [Floor and dip tube](floor-and-dip-tube.md)
describes them.

Arachne fits widths to the geometry. The 999-wall request continues inward until the cross-section is filled; actual track count follows local thickness. Check the emitted wall, corner,
seam and floor/wall paths when refreshing geometry. The wall-only feature inspection and a closed mesh do not establish that the deposited part holds water. Ironing is disabled on every model and support surface.

Dry the actual stock using the [shop drying table](../../../ledger/tools.md)
and keep it dry during printing. A dry-box humidity reading describes the
surrounding air rather than residual moisture in the filament.

## Evidence and print records

The walls-only article has reported seam leakage. Its underside photograph shows
droplets along a branching floor junction resembling the native perimeter
convergence regions. [Physical result](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json).

The preceding May-adapted left article has [reported floor-fill/perimeter leakage](prints/2026-10-21-mark1-may-water-right08-z000/physical-result/physical-result.json). The earlier zero-user-trim left article leaks at many places, as reported by
Derek. Its corner photographs show a distorted band near the floor-to-wall
transition. Neither the finished shape nor the limited live camera views
establishes an onset layer. The stopped job's
[terminal record](prints/2026-10-21-mark1-right08-z000/terminal-observation.json)
records the visibility limit and paused task-bound monitor.

The September 0.24 mm article held water, as reported by Derek. Its recovered
Mark2 slice estimated 20 h 7 min and 414.76 g; those estimates belong to that
historical geometry. The [current native slice review](slice-review.json)
estimates **5 h 46 min and 431 g** per body/cap plate, with **zero ironing**,
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
