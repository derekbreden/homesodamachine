# Mark1 right reservoir and cap: repeat 255/260 °C recipe

Mark1 task **1372664582** has **reported persistent lifting** on the right
reservoir and matching cap. Derek says it seemed worse and supplied two
photographs. Fresh retained status reports **FAILED**, print error 0 and no
HMS; the layer field has reset to 0 and cannot establish a stop or lift-onset
layer. There is no water-hold result for this right article.
[Physical report and photographs](physical-result/physical-result.json) ·
[Terminal observation](terminal-observation.json).

The print used the **right 0.8 mm Standard** hotend. One Studio Send was
acknowledged **SUCCESS** at **00:34:07 CDT / 05:34:07 UTC, October 25, 2026**.
[Launch](launch.json) · [Startup](startup.json).
Derek requests the [same right pair on glued Engineering Plate](../2026-10-25-mark1-right-engineering-flow105-overlap30-temp260-right08-z000/README.md).

The completed [left reservoir, task 1371867808](../2026-10-24-mark1-flow105-overlap30-temp260-right08-z000/README.md),
reports **FINISH 833/833** and Derek reports it is **holding water** alongside
the older 265/270 °C article, which is still holding water. Neither ongoing
hold has a newly specified total duration. The left result is the recipe basis
for this right pair. [Left physical result](../2026-10-24-mark1-flow105-overlap30-temp260-right08-z000/physical-result/physical-result.json) ·
[Acceptance records](../../water-hold-acceptance.json).

## Identical recipe

**255/260 °C first/subsequent nozzle**, **flow 1.05**, **five Arachne wall loops**
at the retained **10°** threshold, **30% Infill/Wall overlap**, 100% solid zig-zag
floor fill, three bottom/three top shells with 0.8 mm minimum top thickness,
**0.30/0.24 mm** first/subsequent layers, nominal **0.8 mm** lines, **70 °C** bed,
**21 mm³/s** ceiling and May motion/cooling. Automatic Tree/Default bed-only
supports are retained. **No brim, zero added user Z trim and ironing Off**;
stock Textured PEI compensation is **`G29.1 Z-0.02`**.
[Complete frozen settings](settings.json) · [Selection and provenance](adaptation.json).

The complete settings file is byte-identical to the left article's. Native
**plate 2**, `reservoir-right` and `reservoir-cap-right`, comes from the same
completed two-plate native slice as that left print. Its source G-code and
project settings are preserved byte for byte. Packaging selects that plate,
renumbers its container to plate 1 and omits editable geometry. No geometry
change, toolpath edit or reslice is involved.
[Native review](native-review.json) · [Print-only packaging](packaging.json).

The native estimate is **5 h 42 min 27 s, 444.21 g and 833 layers**, with no
plate warning and **70.519 mm** minimum full-bead bed-edge inset. The printer
reports the native title **`Flavor_reservoirs_-_PETG_0.24_mm`**; the visible
right-pair archive, hashes and new task receipt identify this submission.

## Material and Send

**A1 PETG R** is selected. Fresh preflight reports A1 **65%** and A2–A4 **100%**,
all matching Bambu PETG Translucent Clear (`GFG01`, transparent `00000000`).
A1 follows Derek's most-depleted-first preference. **AMS filament backup On**
was freshly verified, with A1–A4 in the right-side Auto Refill group. A specific
backup priority sequence is unverified. Startup status reports **unit 0 tray 0
(A1)** with the mounted right 0.8 mm nozzle during loading.
[Preflight and Send options](preflight.json).

**Timelapse On, Auto Bed Leveling On, Flow Dynamics Calibration Auto and Nozzle
Offset Calibration Auto** were visibly verified before the single Send.
Runtime timelapse is disabled during layer-0 material preparation; model-deposition
activation is unobserved. The same running Mark2 task was freshly re-read at
final preflight, establishing at least **270 seconds** of startup spacing,
above the required 180 seconds. No scheduled monitor was created or reactivated.

Derek authorized:

> That turned out well so far. It is holding water along with its older sibling that is still holding water. Please print me the other side (left or right) from what you just printed, same settings, mark1 bed is clear.
