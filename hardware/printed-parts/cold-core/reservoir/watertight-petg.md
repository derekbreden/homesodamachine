# Printing the reservoir in PETG

Use [reservoir.3mf](reservoir.3mf) for the next print. Its two plates contain
the current left and right body/cap pairs and the September 0.24 mm
baseline **with ironing off**. [print-settings.json](print-settings.json) holds every saved machine,
filament and process setting; [reservoir.print.json](reservoir.print.json)
identifies the current geometry and project. The baseline water-hold acceptance source is
`september-08-024` in [water-hold-acceptance.json](water-hold-acceptance.json).

## Current recipe

| Parameter | Value |
| --- | --- |
| Active nozzle | Left 0.8 mm, Standard flow |
| Filament | Bambu PETG Translucent Clear, GFG01 |
| Layer height, first / subsequent | 0.30 / 0.24 mm |
| Nozzle temperature, first / subsequent | 255 / 255 °C |
| Textured PEI bed, first / subsequent | 70 / 70 °C |
| Flow ratio / maximum volumetric speed | 0.97 / 6 mm³/s |
| Requested wall / fill / top speeds | 30 mm/s |
| Requested wall width / wall loops | 0.80 mm / six, Arachne |
| Fill / top / first-layer width | 0.90 mm |
| Fill / wall overlap | 100% zig-zag / 15% |
| Top / bottom shells | 12 layers and 2 mm minimum thickness |
| Top / bottom pattern | Zig-zag |
| Ironing, model and supports | Off |
| Wall order | Inner then outer |
| Seam | Aligned scarf on all walls; inner walls included; unconditional; gap 0% |
| Ordinary cooling | Part fan 20%; first three layers off; auxiliary off |
| Overhang cooling | 90% override |
| Supports | Tree auto, bed only, 30° threshold |
| Support top / bottom gap | 0.18 / 0.18 mm |
| Support interface top / bottom layers | Two / two |
| Saved printer trim | +0.04 mm over stock plate compensation, from the accepted Mark2 job |

The textured-plate compensation emits `G29.1 Z0.02` for this saved trim after
the initial zero reset. A job on another printer must retain that printer's
own calibrated trim; see [printer profiles](../../../../tools/bambu-printers.md).

The project uses the September baseline, with ironing disabled according to the
[flat-square finish selection](ironing-study/prints/2026-10-06-mark2-squares-v1/physical-result.json).
Its process and filament display names identify the current reservoir recipe.
Both plates explicitly assign the left nozzle in Manual mode. Mark2 starts on
A4, with **A4 → A3 → A1** preferred as each spool runs out;
[printer guidance](../../../../tools/bambu-printers.md#mark2-clear-petg-spool-order)
records the loaded material and refill scope. Bodies print mouth up
with the floor underside on the bed; caps print exterior face down with their
gasket rims up. The matching cap belongs with its named left or right body.

## The part and its seal

The reservoir is a vented cup with 3 mm walls/floor and 6 mm internal corner
fillets. Six M3 fasteners clamp a separate cap through a TPU gasket. The PTFE
vent equalizes headspace pressure. Cold service is 8–15 °C.

A purchased silicone flat washer in the wet-side bulkhead counterbore is the
primary floor seal; the dry side carries a printed TPU washer and locknut.
Sealing faces and controlled washer compression establish that joint.
[Floor and bulkhead](floor-and-bulkhead.md) describes the hardware.

Arachne fits widths to the geometry. Six requested walls are a limit, rather
than six tracks everywhere in a 3 mm wall. Check the emitted wall, corner,
seam, floor/wall and bulkhead-seat paths when refreshing geometry. Nominal
100% fill and a closed mesh do not establish that the deposited part holds
water. Ironing is disabled on every model and support surface.

Dry the actual stock using the [shop drying table](../../../ledger/tools.md)
and keep it dry during printing. A dry-box humidity reading describes the
surrounding air rather than residual moisture in the filament.

## Evidence and print records

The September 0.24 mm article held water, as reported by Derek. Its recovered
Mark2 slice estimated 20 h 7 min and 414.76 g; those estimates belong to that
historical geometry. The [current native slice review](slice-review.json)
estimates **19 h 23 min and 419 g** per body/cap plate, with **zero ironing**,
740 layers and an empty plate-warning field. The model/support/brim full bead
envelope stays at least **80.5 mm from the nearest usable bed edge**, including
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
