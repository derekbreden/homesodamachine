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
