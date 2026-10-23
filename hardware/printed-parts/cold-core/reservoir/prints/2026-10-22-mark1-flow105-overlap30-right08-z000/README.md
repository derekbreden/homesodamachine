# Mark1 left reservoir and cap: flow 1.05, overlap 30%

Mark1 task **1365626370** identifies the left reservoir article, intentionally
stopped before completion. Derek reports a **one-hour water hold** on the printed
portion on **October 23, 2026**. [Physical result](physical-result/physical-result.json).
The submitted plate includes the matching cap and uses the **right 0.8 mm Standard**
nozzle. Launch acceptance was freshly verified
at **18:39:14 CDT / 23:39:14 UTC, October 22, 2026**, after one Bambu Studio Send
click and a `project_file` SUCCESS acknowledgment. That timestamp is the
verification time, not the exact command-acceptance instant.
[Launch receipt](launch.json) · [Preflight and visible Send options](preflight.json).

The recipe uses **five wall loops, 100% solid zig-zag floor fill, 30% Infill/Wall
overlap, 1.05 flow and 265/270 °C** first/subsequent nozzle temperatures. It
retains **0.30/0.24 mm** first/subsequent layers, nominal 0.8 mm lines, Arachne
at **10°**, May motion/cooling, 21 mm³/s and 70 °C bed. **No brim, zero added user
Z trim and ironing Off**; stock Textured PEI `G29.1 Z-0.02`.
[Complete settings](settings.json) · [Adaptation](adaptation.json) ·
[Wall-count review](../../recipe-reviews/2026-10-22-flow105-overlap30/wall-count-review.json).

**A3** is selected in the foreground Send dialog and is the only loaded matching
clear-PETG spool. Preflight reports 39%; A1, A2 and A4 are empty. Use A3 fully.
AMS filament backup is visibly **On** in Mark1's AMS Settings. No other matching
refill spool is loaded at preflight. Timelapse and bed leveling are **On**;
flow dynamics and nozzle offset calibration are **Auto**. Mark2 retains task
1365546966, observed in PREPARE at 23:01:33 UTC; the final pre-send spacing is
at least **2,142 seconds**, exceeding the required 180 seconds.

The print-only archive preserves the reviewed native G-code and settings.
[Packaging and hashes](packaging.json) · [Native review](native-review.json) ·
[Geometry](geometry-review.json) · [Plate 1 supports](plate-1-supports.json) ·
[Plate 2 supports](plate-2-supports.json). Plate 1 estimates **5 h 42 min,
444.28 g and 833 layers**, with no plate warning and a 70.5 mm minimum full-bead
bed-edge inset. Studio opened the staged copy without reslicing. The printer
reports **`Flavor_reservoirs_-_PETG_0.24_mm`**, the normalized native project
Title, rather than the archive filename. The new task, acknowledgment and
matching native estimate bind that name to this submission.

[Startup observations](startup.json) distinguish selected material/options
from runtime state. The live camera shows the empty plate during layer-0
preparation. First-layer contact and corner attachment are unassessed. The
[reported one-hour water hold](physical-result/physical-result.json) applies to
the printed portion. [Current status limit](terminal-observation.json) records
that the printer no longer retains this task; exact stop layer and height are
unspecified. No scheduled monitor was created or reactivated.

Derek authorized:

> Okay, good enough, start that print


## Water-hold report

Derek reported on October 23:

> We've been holding water for an hour now (though you may see I did stop the print a bit early, there is plenty there to test with)

This is a successful reported one-hour hold for the printed article. Retain
flow 1.05, five walls, 30% overlap and 265/270 °C as the current recipe. The
combined settings have supporting physical evidence; this result does not
isolate which setting supplied the improvement. Fill height, exact printed
height and cap/gasket assembly sealing are unspecified.

Derek also reports aesthetic concerns with this print. His [next intended
trial](../../corner-lifting/next-trial-options.json) retains every setting here
except nozzle temperatures, using **255 °C first layer / 260 °C subsequent
layers**. The temperature pair is recorded in the recipe adaptation as the
values before the 10 °C increase. This is a planning note: Derek reports the
printer is busy with other work and filament is not loaded. The submitted
recipe and its one-hour water-hold result remain unchanged.
