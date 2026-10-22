# Walls-only reservoir print on Mark1

Mark1 accepted task **1362982574** at **23:25:22 CDT on October 21, 2026**
(**04:25:22 UTC October 22**). The printer acknowledged `project_file` SUCCESS
and entered PREPARE with no print error or HMS alert.
[Launch](launch.json) · [Preflight](preflight.json) · [Native review](native-review.json).

The plate contains the full-height **left reservoir and matching cap**, using
clear PETG through the **right 0.8 mm Standard nozzle**. The foreground Send dialog
visibly selected **A4 PETG R** and the right **0.8 Standard** hotend. Timelapse and
bed leveling were On; flow dynamic and nozzle offset calibration were Auto.

The [recipe adaptation](adaptation.json) continues model perimeters inward with
**999 requested walls**, **0% sparse infill** and **zero top/bottom shell fill**.
The native model features on both plates are only Inner wall, Outer wall and
Overhang wall. Supports retain their own Support/Support interface paths.
There are no model raster-fill, gap-fill, brim or ironing feature paths.

Other physical controls retain the [May Water baseline](baseline-settings.json):
**flow 1.02**, **255/260 °C**, **21 mm³/s**, **70 °C** bed, **0.30/0.24 mm** layers,
nominal **0.8 mm** lines, Arachne, inner then outer walls, random conditional scarf
with 15% seam gap, ordinary **10–20%** cooling with the first three layers off,
**90%** local overhang override and auxiliary off. Added user Z trim is **zero**;
`G29.1 Z-0.02` retains stock Textured PEI compensation. **No brim or ironing**.
Geometry, placement and Tree(auto)/Default supports are retained.

The native left plate estimates **5 h 46 min, 430.66 g and 833 layers** with no
plate warning. Full beads stay at least **70.5 mm** inside the usable bed edge.
All seven support bodies start at the bed; six have no explicit interface label.
[Packaging](packaging.json) preserves every submitted G-code byte.

The [floor paths](floor-wall-paths.png) show perimeters continuing across the
floor. The manual [XY footprint reading](floor-wall-coverage.json) inspects all
twelve full-floor layers. Its rounded bead model retains about **10 mm²** of
small pockets at medial junctions in an approximately **8,348 mm²** section.
It is a nominal XY reading, not measured deposited material or proof of a
through-floor leak. Scarf Z/flow ramps and molten spreading are outside its scope.
The printed article supplies the sealing result.

Use the **most depleted matching spool first**, then work toward fuller spools.
A4 is selected first per Derek. A1 reports **57%**, A3 **100%**, A4 **unknown** and
A2 is empty; the preferred order is **A4 → A1 → A3**. Automatic refill is retained.
The Send dialog selects the starting spool and provides no verified backup-priority
editor. Automatic selection of A1 before A3 is unverified.

The preceding May-adapted article has a [reported leak at the floor-fill/perimeter
boundary](../2026-10-21-mark1-may-water-right08-z000/physical-result/physical-result.json).
Its [geometry comparison](../2026-10-21-mark1-may-water-right08-z000/physical-result/floor-layout-comparison.json)
confirms a sloped historical May floor with sampled 3 mm material thickness.
Historical water holds remain scoped to their tested articles. This walls-only article has reported seam leakage; corner contact and adhesion were not separately reported.

At **23:29:25 CDT**, runtime current/target tray **3 (A4)** and right-extruder
`snow=3` confirm A4 loaded to the mounted right **0.8 mm** nozzle. The task was
RUNNING at **0/833**, with no print error/HMS. Two changing live camera frames
showed the empty plate during startup; first-layer contact and runtime timelapse
activation at deposition remain unassessed. [Startup observation](startup.json).

## Physical result

Derek reports: **“Leaks along the seam”**. The off-plate photograph shows multiple
droplets along a branching junction across the concentric floor paths and at
lower corners. The article fails its reported water hold. Fill height, hold
duration and the complete internal water route are unreported. The retained
job reports FINISH at 833/833, with no print error/HMS.

The photographed line qualitatively resembles the perimeter-convergence regions
in the native floor reading. This is not a calibrated point registration or
proof that a layer-change/scarf seam is the exit mechanism. The native comparison
examines closing those junctions while retaining walls-only construction.
[Photograph and result](physical-result/physical-result.json) ·
[Native seam/junction comparison](physical-result/seam-comparison.json).
