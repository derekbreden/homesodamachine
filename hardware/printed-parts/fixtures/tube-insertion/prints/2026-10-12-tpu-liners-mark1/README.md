# Tube insertion TPU grip liners — Mark1

Task **1333827786** has a failed physical result: Derek reports that one liner
fell over. The [failure record](failure.json) binds that observation to this
archive; Mark1 reports FAILED with no current error or HMS. The
[compact 0.00 mm trim retry](../2026-10-12-tpu-liners-close-z000-mark1/README.md)
contains the replacement print.

The final [tube insertion tool](../../README.md) plate contains two identical
preformed TPU 85A liners F. Their tube axes are vertical, with each 8 × 20 mm
end on the bed and the constant half-round gripping channel carried through
28 mm of height. The [native project](2026-10-12-tube-insertion-liners-tpu85a-right06-z018-mark1.3mf)
and [reviewed G-code archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-tpu-liners-mark1/2026-10-12-tube-insertion-liners-tpu85a-right06-z018-mark1.gcode.3mf)
are prepared for Mark1's right fixed 0.6 mm hotend and black TPU 85A on
external spool 255.

The reviewed solid TPU recipe uses 225 °C nozzle, 35 °C Textured PEI,
2.2 mm³/s maximum flow, two Arachne walls, 100% zigzag infill, three top/bottom
layers, a 0.30 mm first layer and 0.18 mm normal layers. Supports are disabled
and automatic brim remains enabled. The native slice generates no supports
and retains at least 128.39 mm of full-bead bed-edge clearance.

Mark1's normal user trim is +0.18 mm. The native startup resets trim and
emits `G29.1 Z0.16` on Textured PEI. The process compatibility identity
matches the printer's 0.6 mm trim preset. The [preparation record](2026-10-12-tube-insertion-liners-tpu85a-right06-z018-mark1.print.json)
and [native review](2026-10-12-tube-insertion-liners-tpu85a-right06-z018-mark1.readiness.json)
bind the source mesh, settings and source project. All 34,580 commands
from the first deposited layer through print end match the reviewed liner
slice, including the first and second layers. Native preparation can be
reproduced with [prepare_mark1.py](prepare_mark1.py) and an empty named
scratch directory; it does not submit a print.

Task/job **1333827786** is accepted, first observed at **4:30:07 pm CDT on
October 12, 2026**, following one Send. Bambu Connect shows the exact archive,
the selected right hotend and homing; telemetry reports RUNNING, 0/155 layers
and no fault. Timelapse and leveling are On; flow and nozzle-offset
calibration are Auto. The native estimate is **1 h 06 min / 8.8 g**, plus
additional startup calibration and any pauses.

The [preflight](preflight.json), [launch receipt](launch.json) and
[post-send readings](after-send.json) bind source and submitted G-code hashes,
printer mapping, options and shared-circuit spacing. Printer 2 retains the
launch time for job management. This is plate three of three. Both PET-GF
plates have telemetry completion records. Liner cleanup, fit, grip performance
and printed strength remain unassessed.
