# Touch-Flo sealing sleeve — Mark2 task 1368570348

**Status: printing beyond plate detection; printed stringing, fit and sealing pending.**
Mark2 accepted one black Bambu TPU 85A sleeve on **2026-10-23 at 16:38 CDT**.
The [launch receipt](launch.json) binds the submitted processed archive to task
**1368570348**. The source estimate is **11 minutes / 0.40 g**, with 87 layers.

Use the [processed print archive](2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2-continuous-cap.gcode.3mf)
directly. It includes the cap routing; reslicing the
[editable project](2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.3mf)
produces the [native source slice](2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.gcode.3mf).

## Recipe and fit basis

The [accepted May Touch-Flo / LLDPE fit project](../../tpu-o-ring-85A-6mm.3mf)
supplies the unchanged mesh, cap-down pose, Bambu TPU 85A material profile,
0.30 mm first / 0.18 mm subsequent layers, one Classic wall, spiral mode,
225°C nozzle, 1.0 flow ratio and 2.2 mm³/s flow cap. One sleeve is centered at
**X177.5, Y160 mm**, with at least **147.09 mm** full-bead bed-edge clearance.

Derek identifies **black Bambu TPU 85A** on Mark2's **right 0.6 mm nozzle**
and a **glued Engineering Plate**. This job selects **Engineering Plate at
35°C**, with **zero added user Z trim**. The only emitted trim command is
**`G29.1 Z0`**. The [preparation record](2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.print.json)
binds the unchanged mesh and local settings; the
[native readback](2026-10-23-touch-flo-sleeve-tpu85a-right06-z000-mark2.readiness.json)
records the trim, footprint and no slicer warning.

The saved spiral recipe commands **three solid cap layers totaling 0.66 mm**,
followed by the spiral wall. The model's cap region is **2.1 mm**; that CAD
dimension is not the solid cap thickness commanded by this recipe. The
accepted fit project supplies this same three-layer cap recipe.

## Applying the stringing result

The [accepted elbow trial](/future/pump-elbow-exploration/prints/2026-10-22-deposited-links-siraya85a-mark2/README.md)
prints through turns so that free strands cannot straighten across an opening.
The sleeve's native wall already rises as one uninterrupted spiral. Its native
cap has five potential free attachment chords across its hole, even with
wall-crossing avoidance enabled.

[`continuous_cap.py`](continuous_cap.py) splices only the three planar cap layers
into deposited tours using the elbow's graph helpers. The nozzle prints through
the turns and takes straight contained transfers between deposited paths.
The native spiral and shutdown bytes are retained verbatim, starting from the
same position, feed and acceleration. Cap deposition is reordered or reversed,
with **no added cap plastic**. Startup remains native.

The independent [emitted-path review](emitted-path-review.json) accounts for all
**629** native cap deposition commands. All **60 free attachment chords**,
including layer transfers, stay inside native material sections retaining the
hole. The same check passes for **33 chords** when deposition runs shorter than
**1 mm** are ignored as possible attachments. There are **no in-part retractions,
Z hops or camera commands**. [Cap processing](cap-processing.json) records each
tour. Physical strand capture, fit and sealing remain unassessed for this print.

## Launch

The [prelaunch record](prelaunch.json) verifies the mounted nozzle, black right
external TPU spool and shared-circuit spacing. The
[send dialog](launch-dialog.json) verifies **Mark2 / Ext TPU R / Engineering**,
**Timelapse Off**, **Bed Leveling On**, **Flow Calibration Auto** and **Nozzle
Offset Calibration Auto**. [Submission readback](submission.json) binds the
imported G-code to the reviewed file. [Startup telemetry](startup.json) and
the pending [physical result](physical-result.json) belong to this task.

At **16:46:36 CDT**, task-bound telemetry confirms **RUNNING at 1/87**,
**225°C** at the right 0.6 mm nozzle, **35°C** at the bed, timelapse disabled
and no print error or HMS. Model printing has begun beyond plate detection.
Bambu Connect also displays **Printing, 2/87**. Visual adhesion and finished
stringing, fit and sealing remain unassessed.

The separate [cancelled plate-mismatch attempt](cancelled-plate-mismatch/README.md)
has no printed article or physical acceptance.

## Reproduce

These manual steps do not send a print or run on commits/builds:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/prepare_mark2.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/continuous_cap.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/review_paths.py
```
