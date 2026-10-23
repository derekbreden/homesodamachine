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

## Current print recipe

[reservoir.3mf](reservoir.3mf) contains the current left and right
body/cap pairs through **Mark1's right 0.8 mm Standard nozzle**. The recipe uses
**1.05 flow, five requested Arachne wall loops, 30% Infill/Wall overlap and
265/270 °C** first/subsequent nozzle temperatures. The partially printed left
article, Mark1 task **1365626370**, has a **reported one-hour water hold** on
October 23, 2026. Derek intentionally stopped the print early.
[Physical result](prints/2026-10-22-mark1-flow105-overlap30-right08-z000/physical-result/physical-result.json) ·
[Launch and startup](prints/2026-10-22-mark1-flow105-overlap30-right08-z000/README.md).
[Settings, wall-count comparison and installed presets](recipe-reviews/2026-10-22-flow105-overlap30/README.md).

Derek reports aesthetic concerns with this article. His [next intended
trial](corner-lifting/next-trial-options.json) retains all of its settings except
nozzle temperatures: **255 °C first layer / 260 °C subsequent layers**. This is
an intention recorded for later; the printer is occupied and filament is not
loaded, as reported October 23. The current project retains the tested
265/270 °C recipe.

The ordinary body walls and their thick curved corners contain only native
wall paths. Five is the lowest tested requested count that achieves this on
both bodies; counts two through four retain fill in the corner sections.
Broad floor and cap faces use **100% solid zig-zag fill**, with May's three
bottom and three top layers (0.8 mm minimum top thickness). Arachne uses its
**10° default transition threshold**. The installed Bambu H2C 0.8 presets
select **Classic**; Arachne is a recovered May recipe selection.

Retain **0.30/0.24 mm** first/subsequent layers, **0.80 mm** nominal lines,
**70 °C** bed and a **21 mm³/s** ceiling. May's requested wall speeds are
**200/300 mm/s** outer/inner, with **250/200 mm/s** solid/top speeds; actual
motion is flow/acceleration limited. Ordinary cooling is **10–20%**, first
three layers off, with 90% local overhang cooling and auxiliary off. Random
conditional scarf seams retain the May 15% gap. Automatic Tree/Default supports
serve the current geometry.

**No brim, zero added user Z trim and ironing Off** are explicit selections.
Stock Textured PEI compensation emits **`G29.1 Z-0.02`**.
[Complete settings](print-settings.json) · [Printing guide](watertight-petg.md) ·
[Project verification](reservoir.print.json) · [Native slice review](slice-review.json).
The left body/cap plate estimates **5 h 42 min and 444 g**, with a **70.5 mm**
minimum full-bead bed-edge inset. These are native estimates and path checks,
not physical sealing results.

The 59° walls-only article, task **1364550539**, has [reported bottom leakage
and a vertical-edge strand defect](prints/2026-10-22-mark1-walls-t59-right08-z000/physical-result/physical-result.json).
Its exact 59° walls-only settings and launch belong to that print record.
The preceding walls-only article has [reported seam leakage](prints/2026-10-21-mark1-walls-only-right08-z000-a4/physical-result/physical-result.json).
The preceding May-adapted article has [reported leakage between floor fill and walls](prints/2026-10-21-mark1-may-water-right08-z000/physical-result/physical-result.json).
The earlier zero-trim article has [reported corner curl and leaks at many places](prints/2026-10-21-mark1-right08-z000/physical-result/physical-result.json).
The [historical review](corner-lifting/historical-recipe-review.json) identifies
the successful May source and limits of the recovered sphere record.
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
five-wall recipe has a reported one-hour water hold on the printed portion;
the exact print height and water head are unspecified.
CAD clearance does not establish a print's sealing or finished float sliding.
