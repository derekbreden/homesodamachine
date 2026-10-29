# TPU O-ring — Mark1 task 1336815709

Mark1 accepted one sealing thimble at 3:49 pm CDT on October 13. A fresh
startup reading reports RUNNING, layer 0 of 87, with no printer error or HMS
fault. Printed fit and sealing results are pending.

The editable project retains the mesh and cap-down orientation from
[`tpu-o-ring-85A-6mm.3mf`](../../tpu-o-ring-85A-6mm.3mf), the project identified
in the [successful May 30 tube-plus-sleeve seating record](../../print-log.md).
Nominal dimensions remain 10.44 mm outside diameter, 9.2 mm sleeve bore,
6.5 mm cap hole, 2.1 mm cap, 0.62 mm sleeve wall, and 15.6 mm overall height.
No geometry regeneration or dimensional adjustment is included.

The saved process uses black TPU 85A, a 0.30 mm first layer, 0.18 mm subsequent
layers, Classic with one wall, 0.62 mm line width, no supports, 225 °C nozzle,
35 °C textured PEI bed, and 2.2 mm³/s maximum volumetric flow. Filament is
mapped to Mark1's right fixed 0.6 mm nozzle and external spool 255, whose
reported type and colour match TPU / 161616. Mark1's standard +0.18 mm user
trim emits `G29.1 Z0.16` after the reset to zero.

The centered complete bead footprint has at least 147.09 mm of usable-bed
edge clearance. The native estimate is 10 minutes 59.9 seconds and 0.399 g
using the saved density. The slicer reports no warning. Timelapse and bed
leveling are On; flow dynamic and nozzle offset calibration are Auto.
Mark2 task 1335906696 was accepted more than five hours before this start.

- [Editable project](2026-10-13-tpu-o-ring-85a-right06-z018-mark1.3mf)
- [Exact launched native slice](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/tpu-o-ring/prints/2026-10-13-tpu85a-right06-mark1/2026-10-13-tpu-o-ring-85a-right06-z018-mark1.gcode.3mf)
- [Source mesh hashes and settings changes](2026-10-13-tpu-o-ring-85a-right06-z018-mark1.print.json)
- [Native checksums, bead envelope and estimate](2026-10-13-tpu-o-ring-85a-right06-z018-mark1.readiness.json)
- [Launch receipt and shared-circuit spacing](launch.json)
- [Preflight observation](preflight.json)
- [Fresh startup observation](startup.json)
- [Manual preparation script](prepare_mark1.py)

The first acceptance receipt includes the preceding job's layer counter
(155); the fresh startup observation records this new job at layer 0 of 87.
