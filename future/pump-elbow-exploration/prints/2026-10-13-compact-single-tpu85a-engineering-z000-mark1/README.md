# Single TPU 85A elbow — Engineering Plate, zero Z trim

Mark1 accepted task **1337517926** on **2026-10-13 at 21:09:41 CDT**.
The [launch receipt](launch.json) binds the submitted archive and G-code.

One compact rounded-heel V elbow, using Mark1's right fixed 0.6 mm nozzle and
the user-reported TPU 85A load. The user reports a glued Engineering Plate.
The exact mesh matches the compact TPU for AMS specimen; the plate contains
one body, one normal volume, one object and one build instance.

This job uses Bambu's unmodified H2C machine-start template. On Engineering
Plate with the 0.6 mm nozzle, the native G-code emits only **`G29.1 Z0`**.
The user Z trim is **0.00 mm**, local to this job. The selected plate is
**Engineering Plate**, with the manufacturer's 35°C initial/normal bed
temperature and TPU 85A's 225°C nozzle temperature.

The recipe requests six walls, 100% infill, 0.20 mm first / 0.12 mm normal
layers, 0.62 mm beads, 25 mm/s walls and a 5 mm outer brim. The manufacturer's
TPU 85A H2C profile uses 2.2 mm³/s maximum flow and 1 mm retraction.
Spiral mode and supports are off. The native estimate is **62 minutes / 4.30 g**.
Printed adhesion, socket fit, clamping and sealing remain unqualified.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-engineering-right06-z000-mark1.3mf)
- [Native archive](2026-10-13-compact-single-elbow-tpu85a-engineering-right06-z000-mark1.gcode.3mf)
- [Native readback](2026-10-13-compact-single-elbow-tpu85a-engineering-right06-z000-mark1.readiness.json)
- [Print mesh](compact-single-elbow-print.stl)
- [Preparation reading](preparation-printer-status.json)
- [Stock start template snapshot](stock-machine-start-template.json) and [elbow source](elbow-source.txt)

`prepare_mark1.py --colour 161616` prepares these files offline. It does not
send a printer job or change a global printer preset.
