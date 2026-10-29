# Deposited-path Siraya elbow trial — Mark2

**Status: finished; no strings reported and seal seems as good as before.**
Mark2 accepted task **1365546966** on **2026-10-22 at 18:01 CDT**.
The [launch receipt](launch.json) identifies
`2026-10-22-elbows-siraya-links-mark2-z000.gcode.3mf`.
Allow approximately **2 hours / 8.55 g**; startup telemetry estimates 128 minutes.

This is the [reviewed deposited-path pair](../2026-10-16-deposited-links-siraya85a-mark1/README.md),
with two identical elbows, their cutaway fins and the vertical joining sheet.
The nozzle prints the native wall and fin paths through turns, with contained
straight free transfers between deposited paths. The existing
[emitted-command review](../2026-10-16-deposited-links-siraya85a-mark1/emitted-command-review.json)
covers all 184 layer tours and 6,118 free attachment chords. The
[physical result](physical-result.json) records Derek's acceptance:

> That worked very well. I see no strings, and seal seems as good as before.

Completion telemetry reports **FINISH, 184/184, 100%**, with no print error or HMS.
This result accepts visible stringing quality and records a qualitative seal
comparison for the identified recipe.

The [submission record](submission.json) binds a byte-identical copy of the
[processed archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-16-deposited-links-siraya85a-mark1/2026-10-16-elbows-deposited-links-siraya85a-right06-z000-mark1.gcode.3mf)
to the submitted filename. Its G-code SHA-256 is
`2e2052b96de0fc177a27430732a133e15cfe40eddcf4799ec901eaa64a6fcbe0`.
The embedded checksum matches. Use this processed archive directly; reslicing
the editable project omits the deposited-path processing.

## Material and launch

Derek identifies **Siraya clear TPU 85A** on Mark2's **right 0.6 mm nozzle**
and confirms the **glued Engineering Plate** is ready. The
[prelaunch record](prelaunch.json) preserves that authorization and verifies
the mounted right nozzle and right external TPU spool. Mark1 retains its
finished reservoir task, whose recorded start precedes this launch by more
than the required 180 seconds.

The retained recipe uses **225°C first layer, 215°C normal layers, 35°C bed**,
0.20 / 0.12 mm layers, six walls, 100% infill and an attached 5 mm outer brim.
The only emitted Z-trim command is **`G29.1 Z0`**, clearing the trim to zero.
No added first-layer Z offset is applied.

The [send dialog](launch-dialog.json) verifies **Ext TPU R**, **Timelapse Off**,
**Bed Leveling On**, **Flow Calibration Auto** and **Nozzle Offset Calibration
Auto**. [Printer events](launch-events.json) record `project_file` SUCCESS.
The source G-code contains no camera-trip commands.

At **18:01:54 CDT**, [startup telemetry](startup.json) reports RUNNING at
**0/184**, right external TPU at the mounted **0.6 mm** nozzle, timelapse disabled,
and no print error or HMS. Model first-layer contact is unassessed at this stage.

Fin-removal effort and fitting force are unmeasured. The seal comparison supplies
no pressure, hold duration, fixture or identified comparison article; quantified
pressure holding, retention and lifetime remain unmeasured.
