# Provisional faucet scarf swatches — Mark2

This length/start-height plate is held unprinted. The active comparison is the
[seam-gap screen](../seam-gap-swatches-v1/README.md), using Derek's D/E/F groove
and ridge observations. No Send or automatic follow-up is authorized for this archive.

This is a prepared follow-up to the [current cooling and seam plate](../2026-10-10/README.md),
task **1327799013**. Its [physical results](../2026-10-10/physical-result/physical-result.json)
report a regular-seam groove and visually indistinguishable scarf ridges.
The [study plan](study-plan.json) authorizes preparation only. A separate start
instruction is required; there is no automatic next print.

Fourteen short swatches screen **scarf length** and **start height** while keeping
the remaining process settings fixed. Twelve combinations cover lengths of
5, 10, 20 and 30 mm at 5%, 10% and 25% start height. Two identical ordinary-seam
controls sit at opposite corners of the occupied footprint. Treatments are mixed
across positions so one setting is not concentrated at one plate edge.

Each swatch is an unscaled section of the [accepted Industrial faucet](../../industrial/physical-acceptance.json),
cut at parent print Z82.00–100.20 mm in its original −15° pose. It retains the real
curved exterior and shared internal passage. Print-horizontal cuts provide a
stable seated bottom and an 18.20 mm height. These specimens require no supports
in the native slice. Tree(auto)/Default is retained, with no support blockers.

The first bed layer is 0.20 mm. Normal layers are 0.24 mm; the comparison band
is **0.08 mm at local Z4.04–16.04 mm**, totaling 150 fine layers per swatch.
This supplies a coarse base, a visible fine-layer seam and a coarse finish band.
The common fine height can be reconsidered after D/E/F are inspected.

Black Polymaker PET-GF uses Mark2's fixed left hardened standard-flow 0.4 mm
nozzle, external left slot 254, Textured PEI and +0.04 mm requested trim
(+0.02 mm emitted). Nozzle temperatures are 265/280°C; the bed is 80°C.
Global temperatures, flow, speeds, cooling, two walls and 15% grid infill are
inherited unchanged from the accepted faucet project. Cooling is calculated by
Bambu for this plate; there is no fan-command postprocessing.

All specimens place the seam on the back curved wall. Scarf specimens override
the filament's ordinary seam with Bambu Contour scarf. The other saved defaults
are smart application at 155°, 10 steps, inner-wall scarf enabled, zero slope
gap and entire-loop scarf disabled. Ordinary controls explicitly disable scarf.
[Bambu's versioned setting definitions](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp)
define start height relative to the current layer height. In the 0.08 mm band,
the tested starts are 0.004, 0.008 and 0.020 mm above the previous layer.

Facing the printer, read each row left to right, with row 1 nearest you.
Keep the letters with the articles before removing them. The letters below
identify plate locations; specimen geometry is identical and has no added labels.

| Row | Left | Middle-left | Middle-right | Right |
| --- | --- | --- | --- | --- |
| 1 — front | A — regular | B — 5 mm / 10% | C — 20 mm / 25% | D — 10 mm / 5% |
| 2 | E — 30 mm / 10% | F — 5 mm / 25% | G — 20 mm / 5% | H — 10 mm / 10% |
| 3 | I — 30 mm / 25% | J — 5 mm / 5% | K — 20 mm / 10% | L — 10 mm / 25% |
| 4 — back | M — 30 mm / 5% | Empty | Empty | N — regular |

The [placement map](plate-layout.png) shows native first-layer beads. Centers are
34 mm apart across and 38.5 mm between rows. The full native deposition footprint
has **85.7 mm minimum bed-edge clearance**, exceeding the requested 40 mm inset.
The provisional native estimate is **3 h 48 min 50 s**, about **63 g** at the saved
filament density. Neither an import nor a Send has been attempted.

Longer scarves might distribute the seam discontinuity across a less visible
region, or widen a depression. A lower start height gives a stronger initial
taper but deposits a thinner first segment; a higher start retains more material
there but could leave a more noticeable start. The matrix distinguishes those
responses rather than assuming a longer or lower scarf is better.

Compare the middle of the fine band under the same diffuse light, then raking
light. Judge seam visibility, any broad trough, rough surrounding wall, exposed
gap and loose strands. Compare both ordinary controls before ranking scarf
variants; a substantial difference between A and N limits treatment conclusions.
A useful candidate has a less visible seam without a broader trough, exposed gap
or damaged neighboring wall. Similar-looking candidates favor settings closest
to Bambu's 10 mm / 10% defaults. [Results](results.json) remain unrecorded.

If current E/F improve on D, this wider matrix brackets that improvement. If they
produce broad depressions, prioritize the shorter lengths and higher starts. If
the current fine band itself lifts or splits, revise the common band before
using these swatches to choose a scarf. The present draft records no winner.

Short sections and fourteen simultaneous objects change layer return time and
heat exposure relative to the complete faucet. Curved neck screening also does
not qualify supported shoulders, sharp corners or every surface. A promising
setting needs a complete-faucet confirmation before replacing the shipping recipe.
Appearance screening establishes no bond strength, load capacity or lifetime.

The editable project, local native archive, [native inspection](native-check.json)
and source hashes are saved beside this file. Native inspection confirms all
fourteen fine bands, the requested scarf start heights and lengths in emitted
paths, identical source triangles, zero support deposition and first/second-layer
wall overlap. Probing clump detection is disabled. Timelapse and bed leveling
remain intended launch options; they have not been sent to a printer for this study.

`prepare.py` generates the geometry and project and saves a local slicing command
under `.cache/printer-control/faucet-scarf-swatches-v1/`. `review.py` inspects its
native output manually. Neither script launches a print, and neither is added
to a recurring check or build gate.
