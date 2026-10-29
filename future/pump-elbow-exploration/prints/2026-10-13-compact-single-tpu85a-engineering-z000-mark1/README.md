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

The [physical record](physical-result.json) binds the reported left-lip curl,
subsequent nozzle pickup and worsening on both lips after the user's runtime
part-fan reduction from 100% to 50%. The [photo](curl-left-edge.jpg) shows the
raised left lip. The [bounded toolpath review](curl-toolpath-review.json)
covers layers 26–33; geometric bead overlap does not establish resistance to curl.
The [side comparison](underside-side-comparison.json) finds 45° underside on
printer-left and about 66° on printer-right at layer 28, with approximately
82% versus 92% nominal local bead overlap. The right neck steepens as its
radius decreases; equal leg-axis angles do not give equal underside slopes.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-engineering-right06-z000-mark1.3mf)
- [Native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-engineering-z000-mark1/2026-10-13-compact-single-elbow-tpu85a-engineering-right06-z000-mark1.gcode.3mf)
- [Native readback](2026-10-13-compact-single-elbow-tpu85a-engineering-right06-z000-mark1.readiness.json)
- [Print mesh](compact-single-elbow-print.stl)
- [Preparation reading](preparation-printer-status.json)
- [Stock start template snapshot](stock-machine-start-template.json) and [elbow source](elbow-source.txt)

`prepare_mark1.py --colour 161616` prepares these files offline. It does not
send a printer job or change a global printer preset.
