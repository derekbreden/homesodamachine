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

## Tube grips and air paths

The 4 mm lid plate carries matched 45° countersinks for flush TPU spools:
two 1/4-inch tube grips and one 4 mm air-tube grip per reservoir. Each air
tube passes through its own integral foam-cap passage and opens 6 mm above
the insulation. [Air tubes and splash baffles](vent.md) ·
[Tube insertion and grip](floor-and-dip-tube.md).

Print four [liquid-tube grips](reservoir-tube-grip.step) and two
[air-tube grips](reservoir-air-grip.step) in TPU 90A per machine. The
[approved review](tube-vent-proposal/README.md) defines their geometry;
printed grip and splash performance remain unqualified. Frozen print archives
retain the geometry of their tested articles. A fresh lid slice is required
for these countersunk ports.

The [native integration check](tube-grip-integration.json) records the flush
seats, open air paths, casing clearance and unchanged body geometry.

## Two-hour leakage and next overlap candidate

Derek reports that the most recent reservoir leaks a small amount after
**two hours**, at the line between wall and infill. The
[physical record and photographs](water-hold-evidence/2026-10-26-two-hour-leak/physical-result.json)
retain that result without assigning an unconfirmed task ID. The visible wet
marks establish leakage beside the base; the internal path is unconfirmed.

The [next candidate](recipe-reviews/2026-10-26-overlap50/README.md) uses **50%
Infill/Wall overlap**, with the latest **255/260 °C Engineering Plate / left
0.8 mm** recipe otherwise retained. The candidate settings and unchanged
body geometry are verified; its frozen lid predates the flush grips. Native slicing and a physical water-hold result are
pending. No new job is submitted. Earlier task-specific observations retain
their recorded scope.

## Recorded Engineering Plate left reservoir and lid

The [left body and matching lid](prints/2026-10-25-mark1-left-engineering-flow105-overlap30-temp260-left08-z000/README.md)
have recorded launch **Mark1 task 1375878568**, accepted **22:03:53 CDT October 25 /
03:03:53 UTC October 26**, through the fixed **left 0.8 mm Standard** nozzle.
The glued **Engineering Plate** recipe retains flow 1.05, five Arachne walls,
30% overlap, 255/260 °C nozzle, 70 °C bed and **0.00 mm Z compensation**.
**A2** is the recorded starting spool with automatic refill; A1 is recorded empty.
The retained startup observation is RUNNING, layer 0/833, print error 0 and no HMS.
The October 26 leak report identifies the most recent reservoir without an
explicit task ID.

The preceding [right reservoir, task 1374963298](prints/2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-left08-z000/physical-result/physical-result.json)
completed 833/833 layers and **turned out well and is holding water**, as
reported by Derek. Duration and water head are unspecified. Its body and float-guide datums
match current CAD. The recorded plate includes its matching left lid; current
lids carry the flush tube grips described above.

The preceding Engineering Plate **task 1374272357** has [reported right-hotend
polymer buildup and a motion-step-loss warning](prints/2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-right08-z000/physical-result/physical-result.json).
It is FAILED with no current error/HMS. Four photographs do not establish a
fault-onset layer or a general right-hotend defect. The left-hotend retry is
selected by Derek.

The preceding **task 1372664582** has [reported persistent lifting](prints/2026-10-25-mark1-right-flow105-overlap30-temp260-right08-z000/physical-result/physical-result.json)
on Textured PEI, documented in two photographs. It reports FAILED with no
print error/HMS. Its submitted G-code has zero added user trim and the stock
**−0.02 mm Textured PEI compensation**. The Engineering Plate trial emits zero.

The completed [left article, task 1371867808](prints/2026-10-24-mark1-flow105-overlap30-temp260-right08-z000/physical-result/physical-result.json)
is **holding water**, as reported by Derek on October 25. He reports it turned
out well so far and requests the other side with the same settings. The older
265/270 °C article is also still holding water. Total hold durations and water
heads are unspecified. [Acceptance records](water-hold-acceptance.json).

The recorded 30% repeat recipe uses **1.05 flow, five requested Arachne wall loops,
30% Infill/Wall overlap and 255/260 °C** first/subsequent nozzle temperatures.
The [Engineering Plate repeat settings](prints/2026-10-25-mark1-left-engineering-flow105-overlap30-temp260-left08-z000/settings.json)
and [native source](prints/2026-10-25-mark1-left-engineering-flow105-overlap30-temp260-left08-z000/packaging.json)
identify this 30% print through Mark1's left **0.8 mm Standard** nozzle. The completed
left water-hold article used Textured PEI.

[reservoir.3mf](reservoir.3mf) and [print-settings.json](print-settings.json)
retain the **265/270 °C reference recipe** on the current left/right body/cap
geometry. Its intentionally shortened task **1365626370** has a reported
one-hour hold on October 23 and remains holding water on October 25.
[Physical result](prints/2026-10-22-mark1-flow105-overlap30-right08-z000/physical-result/physical-result.json) ·
[Wall-count comparison and installed presets](recipe-reviews/2026-10-22-flow105-overlap30/README.md).
The [255/260 °C comparison](prints/2026-10-24-mark1-flow105-overlap30-temp260-right08-z000/native-review.json)
changes only temperature-related executable commands from that reference.

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
The Engineering Plate trial emits **`G29.1 Z0`**; the Textured PEI reference
emits stock **`G29.1 Z-0.02`** compensation.
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

Reservoir leak results belong to the articles and process tested. Reported October
water holds include the completed 255/260 °C left article on Textured PEI,
the completed 255/260 °C right article on glued Engineering Plate and the
shortened 265/270 °C article. Total ongoing durations and water heads are unspecified.
CAD clearance does not establish a print's sealing or finished float sliding.
