# Matching funnel mold core — October 7, 2026

Mark1 accepted task **1317250748** at **09:30:52 CDT** through one foreground
Bambu Connect Send. [Launch receipt](launch.json) · [Fresh preflight](preflight.json).

The core is plate 2 of the frozen [October 6 matching cavity/core project](../2026-10-06-mark1-retry-z004-v2/funnel-mold-mark1-retry-z004.3mf).
Its submitted G-code is byte-identical to that plate's reviewed native slice.
[Packaging and hashes](packaging.json) · [Authorized launch plan](launch-plan.json) ·
[Native two-plate review](../2026-10-06-mark1-retry-z004-v2/readiness-review.json).
The current generator was not used. Derek identifies the completed cavity as
the mate for this core; a finished pair's physical fit and casting behavior are unassessed.

The inverted core uses PETG Translucent Clear from **AMS HT-A**, the **right
0.4 mm Standard nozzle**, Textured PEI and **+0.04 mm requested trim**
(emitted G29.1 Z0.02). It has six walls, 15% gyroid, six top/bottom layers,
0.20/0.24 mm layers, 0.88 flow and 5.61702 mm³/s maximum volumetric speed.
First-layer walls/infill run at 20/30 mm/s with an 8 mm outer brim. There are
no model supports. The complete bead envelope clears the right-nozzle usable
bed boundary by at least 39.565 mm.

The native estimate is **11 h 35 min, 233.23 g and 176 layers**.
Timelapse, bed leveling, flow dynamic calibration and nozzle offset calibration
are On in the Send dialog. Probing clump checks remain Off and camera AI
preferences are retained. Startup telemetry supplies no visual adhesion or
finished-part result. Existing scheduled chat monitors remain paused.

Both printers reached layer 1 without print errors or HMS alerts. The
[timelapse inspection](timelapse-review.json) records **runtime timelapse
disabled** despite Send On, with 97 clips per card. Recording is not verified
enabled for these jobs.
