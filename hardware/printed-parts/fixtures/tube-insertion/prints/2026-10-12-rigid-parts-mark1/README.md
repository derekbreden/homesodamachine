# Tube insertion rigid parts — Mark1

The second [tube insertion tool](../../README.md) plate contains one guided
carrier B, lower jaw D, upper jaw E and cap-support puck G. It uses the
[reviewed native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/ready/tube-insertion-rigid-parts-h2c.gcode.3mf),
with the shared [PET-GF baseline](../../../../petgf.3mf), six walls, 100%
zigzag infill, a 0.20 mm first layer and 0.24 mm ordinary layers. The full
model/support bead footprint retains at least 46.21 mm bed-edge clearance.

Mark1 uses loaded black PET-GF through left external spool 254, reported
as PET-CF, its left 0.4 mm hotend, and Textured PEI. The normal requested
user trim is +0.18 mm; the native G-code resets trim and emits `G29.1 Z0.16`.
Automatic Tree/default supports remain enabled. Four previously reviewed
bed-rooted support bodies occupy the lower jaw's two underside locator-key
pockets and two side-entry carrier nut pockets.

Task/job **1332859109** is accepted, first observed at **10:50:40 am CDT on
October 12, 2026**, after one Send. Bambu Connect shows the exact archive
and homing; telemetry reports RUNNING, 0/63 layers and no fault. Timelapse
and leveling are On; flow and nozzle-offset calibration are Auto. The
native estimate is **4 h 19 min / 241.6 g**, plus startup calibration and
any pauses.

The [preflight](preflight.json), [launch receipt](launch.json) and
[post-send readings](after-send.json) bind the reviewed source and G-code
hashes, options, printer mapping and startup spacing. Printer 2 retains the
launch time for job coordination. Physical print quality, support removal,
fit and strength remain unassessed.

The [base completion reading](../2026-10-11-base-mark1/completion.json) reports
FINISH at 225/225 layers for job 1331280889 without a machine fault. The
remaining tool plate contains the two TPU 85A grip liners.
