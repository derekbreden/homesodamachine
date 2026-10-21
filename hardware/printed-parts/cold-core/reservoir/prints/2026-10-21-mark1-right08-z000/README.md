# Reservoir clear PETG retry on Mark1

Mark1 accepted task **1359909015** at **00:40:29 CDT on
October 21, 2026**, through one Bambu Connect Send. The printer acknowledged
`project_file` SUCCESS and entered PREPARE without errors or HMS alerts.
[Launch receipt](launch.json) · [Fresh preflight](preflight.json).

The left reservoir and matching cap use the **right 0.8 mm Standard-flow
hotend**, Bambu PETG Translucent Clear from **A2**, and automatic refill.
Textured PEI uses **zero added user Z trim**: `G29.1 Z0` clears the trim and
**`G29.1 Z-0.02`** applies Bambu's stock textured-plate compensation.
This setting belongs to the clear PETG reservoir recipe; PET-GF profiles retain
their settings. Derek reports the failed material removed and Mark1 clear for
this retry.

The [failed A4 print and photographs](../2026-10-20-mark1-right08/physical-result/physical-result.json)
document a lifted first-layer cap strand. This retry retains **255 °C** nozzle,
**70 °C** bed, **0.30 / 0.24 mm** first / normal layers, **0.97** flow,
**6 mm³/s** ceiling, ironing Off and the other physical settings. Normal part
cooling is off for three layers, then 20%, with 90% local overhang cooling and
auxiliary cooling off. No brim is emitted by the saved auto-brim setting.

[Executable comparison](command-diff.json) checks all 1,362,949 plate-1 commands
and all 1,348,749 plate-2 commands against the failed job. The single changed
command on each plate is **`G29.1 Z0.16` → `G29.1 Z-0.02`**. Deposition,
geometry, supports, temperature and fan commands are identical. Bed-rooted
support findings are reused on that explicit basis. The
[frozen native review](native-review.json) verifies the right-nozzle assignment,
zero user trim, 833 layers, no ironing and no plate warnings. Native estimate:
**19 h 21 min, 410.28 g**; full-bead edge inset **70.519 mm**, body/cap gap
**10.042 mm**.

[Preparation](preparation.json) binds the current project and native G-code.
[prepare_launch.py](prepare_launch.py) selects plate 1 and makes the print-only
archive without changing its native G-code; [packaging](packaging.json) binds
its hashes. Launch file:
`.cache/reservoir-mark1-right08-z000/slice/2026-10-21-reservoir-left-cap-clear-right08-z000-mark1.gcode.3mf`.
The separate imported copy's embedded G-code was verified before Send.

Timelapse and bed leveling are On; flow dynamic and nozzle offset calibration
use Auto. Mark2's enclosure comparison was already running. The launch was
**478.44 seconds** after its recorded start,
exceeding the shared-circuit 180-second interval.

The [adhesion investigation](../../corner-lifting/README.md) separates first-layer
non-adherence from the reported later corner lifting. This task's first-layer
attachment, later corner contact, finished-part fit and water hold await
physical observation. Startup acceptance establishes none of those results.

At **00:42:20 CDT**, the [startup observation](startup.json) reports this exact
task RUNNING at layer 0/833 without errors or HMS alerts. Two updating Bambu
Studio camera frames confirm live access during startup, before model
deposition. A2 is verified in the Send dialog; startup telemetry still reports
the previously loaded A4 before material preparation. Runtime timelapse is
disabled during this startup phase; verify activation at deposition.

The thread's adhesion monitor checks every five minutes through layer 3,
every ten minutes through layer 120, then every thirty minutes if stable.
It observes this exact task and stops when the task ends or changes.

At **00:52:14 CDT**, the [deposition-start observation](deposition-start.json)
confirms layer **1/833**, **A2** current and target, the mounted right **0.8 mm**
nozzle, and runtime timelapse **enabled**. Nozzle/bed/chamber read
**255/70/35 °C**, ordinary and auxiliary part cooling read zero, and no
print error or HMS alert is reported. Two live camera frames identify no
confirmed lift or strike; the toolhead, clear PETG and reflected illumination
prevent a complete body/cap corner-contact assessment. An attached-corner
baseline is not established by this observation.

At **00:57:17 CDT**, Mark1 reports a
[dirty nozzle-camera-lens warning](nozzle-camera-warning.json), HMS attr
201326848 / code 131095. Bambu Studio says this may affect AI monitoring.
The task remains RUNNING at layer 1/833, with `print_error` zero and
255/70 °C nozzle/bed targets. A2 and runtime timelapse remain selected.
The chamber video continues updating. Studio's separate telemetry panel
displays a connection failure from 00:57:55 CDT, while fresh LAN MQTT
at 00:58:16 still identifies this exact RUNNING task. The exposed camera-right
body-floor edge appears flat; cap contact and occluded edges remain unassessed.
No confirmed lifting or nozzle strike is established by these observations.

The [early-layer checkpoint](early-layers.json) records **layer 4/833** at
**01:27:50 CDT**, with the first three layers complete. Sampled live frames
through 01:28:36 show the exposed camera-right body-floor edge/corner and
near cap perimeter/corners visibly flat, without a confirmed raised strand,
underside gap, curl or strike. Occluded and reflective contact remains
unassessed. A2 and timelapse remain active; nozzle/bed read 255/70 °C.
Part-cooling telemetry becomes nonzero at layer 4. No onset bracket or
water-hold result is established. Checks continue every ten minutes.

The [layer-120 checkpoint](through-layer-120.json) records this exact task at
**06:40:08 CDT / 11:40:08 UTC**, MQTT layer **125/833**, followed by two live
views at layer **126** through **06:41:17 CDT / 11:41:17 UTC**. The exposed
camera-right body bottom edge/corner and near cap perimeter/corners show no
discernible underside gap or upward curl. No plate flex, nozzle strike or
displaced material is confirmed. Occluded and reflective contact remains
unassessed; no complete attached baseline or lift-onset bracket is established.
Selected earlier samples at layers 53, 98 and 116 preserve the same visibility
limits. A2, the right 0.8 mm nozzle and timelapse remain active, with 255/70 °C
nozzle/bed targets and no current print error or HMS alert. This same monitor
checks every thirty minutes through the remainder of this task.
