# Ø7.75 mm TPU grip liners — Mark1

This plate contains two identical TPU 85A liners for the original PET-GF
T-handle jaws. Each liner has a Ø7.75 mm half-round channel, 4.125 mm minimum
backing, and an 8 × 20 × 28 mm manufacturing envelope. The [geometry record](geometry.json)
confirms 0.75 mm of radial material inside the channel with the original
outside envelope preserved.

The [editable project](2026-10-12-tube-insertion-liners-d775-tpu85a-right06-z000-mark1.3mf)
and [native slice](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-liners-d775-mark1/2026-10-12-tube-insertion-liners-d775-tpu85a-right06-z000-mark1.gcode.3mf)
use Mark1's right fixed 0.6 mm hotend, black TPU 85A on external spool 255,
textured PEI, 0.00 mm user Z trim, and a 2 mm model gap. Stock plate
compensation remains enabled. The [slice record](2026-10-12-tube-insertion-liners-d775-tpu85a-right06-z000-mark1.readiness.json)
records unchanged process settings, no supports, 155 layers, a 1 h 09 min
estimate and 9.4 g of filament.

Open the [plain G-code](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/fixtures/tube-insertion/prints/2026-10-12-liners-d775-mark1/2026-10-12-tube-insertion-liners-d775-tpu85a-right06-z000-mark1.gcode)
in Bambu Studio to inspect the exact launched toolpaths. Its bytes are
extracted from `Metadata/plate_1.gcode` in the native archive and match the
SHA-256 in the slice and launch records. Opening the editable project loads
geometry and presets; a subsequent slice is a separate toolpath.

The [launch receipt](launch.json) records task 1334257829 accepted on
2026-10-12 at 7:45:25 pm CDT, with Timelapse and Bed Leveling On and both
calibration options Auto. The [physical grip record](grip-failure.json) reports closure to the rigid stop
without grip and uneven axial compression. CAD confirms an 8.5 mm offset
between the liner centre and closure-screw line.

The [wall-start observation](wall-start-observation.json) records an
intermittent strand forming as the nozzle arrives from the other object
and starts a wall. Its [preview screenshot](wall-start-preview.png) shows
layer 108 of the launched slice; that layer is not identified as affected.
The pictured restart restores the preceding 1.00 mm retraction before an
inner wall, with no extra restart amount. The physical cause remains open.
