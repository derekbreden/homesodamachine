# Mark1 left reservoir and cap: flow 1.05, overlap 30%

Mark1 task **1365626370** is printing the full-height left reservoir and matching
cap through the **right 0.8 mm Standard** nozzle. Acceptance was freshly verified
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
preparation. Body/cap first-layer contact, corner attachment and sealing are
unassessed. No scheduled monitor was created or reactivated.

Derek authorized:

> Okay, good enough, start that print
