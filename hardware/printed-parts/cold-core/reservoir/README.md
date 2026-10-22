# Flavor reservoirs

Current bodies and matching caps carry the ASA Aero float guide at
**(x = ±106.25, y = +32.5) mm** in the assembled cold-core frame,
**20 mm inward from the wet far wall**. Use a 36 × 28 mm ASA Aero float with
a midplane RC62 on the 3.175 mm rod.

Each body stands on its pocket's floor with one flat 3 mm floor, full height, and its cap
carries both mouths: the fill, and the dip tube the draw line becomes.

[Float installation and reed calibration](../magnetic-float/all-aero/installation.md) ·
[Level sensing](level-sensing.md) · [Floor and dip tube](floor-and-dip-tube.md) ·
[Vent](vent.md)

## Current print

Mark1 task **1362982574** completed the current left reservoir and matching cap with the
**walls-only May Water recipe through the right 0.8 mm Standard nozzle**. It was accepted
at **23:25:22 CDT on October 21, 2026**, starting on **A4** with automatic refill.
[Launch, adaptation and native review](prints/2026-10-21-mark1-walls-only-right08-z000-a4/README.md).

Use **[reservoir.3mf](reservoir.3mf)** for the current pairs: plate 1 is left,
plate 2 is right. Bodies print mouth up; caps print exterior face down.
Bambu PETG Translucent Clear uses **255/260 °C** first/subsequent nozzle,
**70 °C** bed, **1.02 flow**, **21 mm³/s** ceiling, **0.30/0.24 mm** layers and
**0.80 mm** lines. May's requested wall speeds are **200/300 mm/s** outer/inner,
with **250/200 mm/s** solid/top speeds; actual motion is flow/acceleration limited.
Ordinary cooling is **10–20%**, first three layers off, with 90% local overhang
cooling and auxiliary off. Random conditional scarf seams retain the May 15% gap.

**No brim, zero added user Z trim and ironing Off** are explicit selections.
Stock Textured PEI compensation emits **`G29.1 Z-0.02`**. The
[flat-square finish result](ironing-study/prints/2026-10-06-mark2-squares-v1/physical-result.json)
supplies the ironing-Off preference; it supplies no water-hold result.
**999 requested walls** continue inward across each section; sparse, top and bottom fill are disabled. Current automatic Tree/Default supports serve the flat-floor geometry.

[Complete settings](print-settings.json) · [Printing guide](watertight-petg.md) ·
[Project verification](reservoir.print.json) · [Native slice review](slice-review.json).
The left body/cap plate estimates **5 h 46 min and 431 g**, with a **70.5 mm**
minimum full-bead bed-edge inset. Its [reported seam leakage](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json) is a failed water hold. The pictured floor junction is being compared with the native perimeter-convergence paths.

The preceding May-adapted article has [reported leakage between floor infill and walls](prints/2026-10-21-mark1-may-water-right08-z000/physical-result/physical-result.json). The earlier zero-trim article has
[reported corner curl and leaks at many places](prints/2026-10-21-mark1-right08-z000/physical-result/physical-result.json).
The [historical review](corner-lifting/historical-recipe-review.json) identifies
the successful May source and exact limits of the recovered sphere record.
Historical May and September water holds remain scoped to their tested articles
in [water-hold-acceptance.json](water-hold-acceptance.json).

## Current print geometry

| Pair | Body | Cap |
| --- | --- | --- |
| Left | [STEP](reservoir-left.step) | [STEP](reservoir-cap-left.step) |
| Right | [STEP](reservoir-right.step) | [STEP](reservoir-cap-right.step) |

[`reservoir.py`](reservoir.py) generates these body/cap pairs together from
the shared [float interface](../_float_interface.py).
[prepare_print.py](prepare_print.py) builds the one current project from these
STEP files and the complete frozen recipe. Run it with `tools/cad-venv/bin/python`;
it checks source hashes against the
[integration record](../magnetic-float/all-aero/integration-check.json), closed
meshes, centered bed placement and preservation of the frozen native base
with the declared May adaptation, ironing and assignment settings.
[review_slice.py](review_slice.py) checks the native recipe, absence of ironing,
right-nozzle assignment, Mark1 Z trim, full bead inset and bed-rooted supports.

Past settings, reported outcomes and source commits are in the
[print log](print-log.md) and [September inspection record](history/seal-trial.md).
Historical 3MFs are retained in Git.

Reservoir leak results belong to the articles and process tested. The current
walls-only article has reported seam leakage; the matching right body is unassessed.
CAD clearance does not establish a print's sealing or finished float sliding.
