# Tube insertion base — Mark1

One PET-GF base A for the [tube insertion fixture](../../README.md) occupies
the first of its three plates. The [reviewed native archive](../../ready/tube-insertion-rigid-base-h2c.gcode.3mf)
uses the shared [petgf.3mf](../../../../petgf.3mf) baseline, six walls,
100% zigzag infill, a 0.20 mm first layer and 0.24 mm normal layers.
The full-bead envelope has at least 26.02 mm bed-edge clearance; no supports
are generated on this plate.

Mark1 uses Derek's loaded PET-GF in its left 0.4 mm hotend, left external
spool 254 reported as black PET-CF, and Textured PEI. Its normal user trim
is +0.18 mm; the native G-code resets the trim and emits `G29.1 Z0.16`
after textured-plate compensation.

Task/job **1331280889** is accepted, first observed at **9:09:03 pm CDT on
October 11, 2026**, following one Send. Bambu Connect shows the exact base
archive and homing; telemetry reports RUNNING, 0/225 layers and no fault.
Timelapse and bed leveling are On; flow and nozzle-offset calibration are Auto.
The native estimate is **11 h 55 min / 829.2 g**, plus additional startup
calibration and any pauses.

The [preflight](preflight.json), [launch receipt](launch.json) and
[post-send readings](after-send.json) bind the original archive and G-code
hashes, printer state, mapping and shared-circuit spacing. Printer 2 retains
the launch receipt for normal job management. The other two tool plates
have no submission in this record.

Physical adhesion, fit, grip performance and printed strength remain unassessed.
