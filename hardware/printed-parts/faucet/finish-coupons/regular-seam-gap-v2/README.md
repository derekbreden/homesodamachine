# Ordinary seam gap — larger range, Mark2

Nine identical, full-scale 18.2 mm sections of the faucet neck compare only ordinary **Seam gap**, with scarf disabled. All specimens use the saved `petgf.3mf` temperature, cooling, flow, retraction, speed, support and wall settings: 0.20 mm first bed layer, 0.24 mm subsequent layers, two walls and 15% grid infill. Mark2 uses its normal +0.04 mm requested/+0.02 mm emitted trim, left external PET-GF and a fixed hardened standard-flow 0.4 mm nozzle on Textured PEI.

Facing the printer, the front of the plate is nearest you:

| Row | Left | Center | Right |
| --- | --- | --- | --- |
| Back | H — 90% | G — 30% reference | I — 100% |
| Middle | D — 70% | E — 15% control | F — 80% |
| Front | A — 40% | B — 50% | C — 60% |

[Plate map](plate-layout.png). The 15% control and 30% reference retain their positions from the first plate. The complete comparison stays on Mark2 to hold printer, nozzle and trim constant. The seven new settings range from 40% to 100% in ten percentage-point increments. Larger percentages stop the perimeter sooner; the native gap witnesses are 0.16–0.40 mm for those seven settings.

The [manual native review](native-check.json) verifies every source mesh and object override, absence of scarf ramps or clump-probing calls, first/second-layer bead contact, 76 ordinary layers, and actual exterior endpoint gaps at three heights. There are no emitted supports and no G-code editing. The complete bead footprint has **104.4 mm edge clearance**.

Native estimate: **1 h 12 min 9 s**, **38.44 g**, plus startup and any pauses. The [launch receipt](launch.json) supplies the submission and acceptance state; [preparation](preparation.json) is a captured preparation-only record. Timelapse and bed leveling are On; flow dynamic and nozzle-offset calibration are Auto. No automatic resume or scheduled monitor is requested.

Record ridge, groove, flatness, exposed gap and adjacent damage per letter in [results](results.json), comparing with E and the previous plate. Short sections and nine simultaneous objects differ from a complete curved faucet's thermal cycle. Physical flatness, a winning setting and complete-faucet transfer remain unassessed.

Mark2 accepted task/job **1331147501** at **7:59:33 pm CDT on October 11** after one foreground Send. The native forecast from observed acceptance is **9:11:43 pm CDT**, plus any additional startup/calibration or pauses. A RUNNING state at layer zero does not establish model-layer progress.
