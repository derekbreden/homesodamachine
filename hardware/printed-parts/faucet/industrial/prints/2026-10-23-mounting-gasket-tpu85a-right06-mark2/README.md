# Industrial above-counter mounting gasket — Mark2 task 1368637649

**Status: printing beyond plate detection; physical result pending.** Mark2 accepted one black Bambu
TPU 85A gasket on **2026-10-23 at 17:07 CDT**. The [launch receipt](launch.json)
binds task **1368637649** to the reviewed processed archive. The native estimate
is **43 minutes / 5.88 g**, with ten layers. Processed part motion is nominally
36.5 minutes, excluding startup, shutdown and acceleration effects.

Use the [processed print archive](2026-10-23-industrial-mounting-gasket-tpu85a-right06-z000-mark2-continuous-layers.gcode.3mf)
directly. Reslicing the [editable project](2026-10-23-industrial-mounting-gasket-tpu85a-right06-z000-mark2.3mf)
produces the separate [native source slice](2026-10-23-industrial-mounting-gasket-tpu85a-right06-z000-mark2.gcode.3mf).

## Part and recipe

The unchanged current [Industrial gasket STL](../../industrial-above-counter-gasket.stl)
supplies the 59 mm diameter, 2 mm CAD thickness and two mounting passages.
Its SHA-256 is `306ad5f786ecfeccb85c3b9c3a883fcb2646c883619d6738814042ac51e33edc`.
One gasket is flat and centered at **X177.5, Y160 mm**, with at least
**122.89 mm** full-bead bed-edge clearance. The [native preview](native-preview.png)
shows the circular Industrial footprint and its two openings.

The [solid-gasket project](../../../../gaskets.3mf) supplies the Bambu TPU
85A material and dense process: **225°C nozzle, 35°C Engineering Plate,
1.0 flow ratio, 2.2 mm³/s flow cap, 0.30 mm first / 0.18 mm normal layers,
two Arachne walls, 100% zigzag infill and three top/bottom shells**. No supports
or brim are needed. The native slice commands ten layers through Z1.92 mm.

Derek identifies **black Bambu TPU 85A** on Mark2's **right fixed 0.6 mm nozzle**
and the cleared, glued **Engineering Plate**. This job uses **zero added user
Z trim**; the only emitted trim is **`G29.1 Z0`**. The [preparation record](2026-10-23-industrial-mounting-gasket-tpu85a-right06-z000-mark2.print.json)
and [native readback](2026-10-23-industrial-mounting-gasket-tpu85a-right06-z000-mark2.readiness.json)
bind the source mesh, settings, footprint, trim and warning-free native slice.

## Deposited turns and open passages

The [accepted elbow trial](/future/pump-elbow-exploration/prints/2026-10-22-deposited-links-siraya85a-mark2/README.md)
prints through turns so a loose strand cannot straighten across an opening.
The [Touch-Flo sleeve](../../../tpu-o-ring/prints/2026-10-23-black-tpu85a-right06-mark2/README.md)
applies the same approach to its cap and has a qualitative general print-quality
report. This gasket applies deposited tours to every layer.

[`continuous_layers.py`](continuous_layers.py) reorders or reverses the native
beads. Visible straight links connect deposited paths; a minimum-distance
perfect pairing joins their odd endpoints without duplicating deposition.
The nozzle follows existing deposition through turns, and free transfers are
collapsed to straight chords wholly contained in gasket material. Both holes
remain present in every native section. **No plastic is added.**

The independent [emitted-path review](emitted-path-review.json) accounts for all
**3,955** native deposition commands and their extrusion, feature, width,
layer and geometry. The native slice has **21** potential free attachment chords
across an opening. The processed file has **138 checked free chords**, all inside
the gasket sections. All **134 chords** also pass when printed runs shorter
than **1 mm** are ignored as attachments. In-part retractions, Z hops and camera
commands are absent. Timelapse is Off.

Native startup and shutdown bytes are retained, with the native entry and final
positions preserved. Feed and acceleration are restored before the native final
wipe. The [processing record](layer-processing.json) binds each layer tour and
the immutable source and output hashes. This review describes commanded paths;
physical strand capture, flatness, counter fit and spill sealing remain unreported.

## Launch evidence

The [prelaunch record](prelaunch.json) verifies the mounted right 0.6 mm nozzle,
black external TPU and shared-circuit spacing. The [send-dialog reading](launch-dialog.json)
shows **Mark2 / Engineering / Ext TPU R**, **Timelapse Off**, **Bed Leveling On**,
**Flow Calibration Auto** and **Nozzle Offset Calibration Auto**. The
[submission readback](submission.json) confirms that the imported G-code still
matches the reviewed file after sending. [Startup telemetry](startup.json)
and the [physical result](physical-result.json) belong to this exact task.

At **17:15:51 CDT**, task-bound telemetry confirms **RUNNING at 1/10**, with
the right nozzle at **225°C**, bed at **35°C**, timelapse disabled and no
print error or HMS. Bambu Connect also displays **Printing, 1/10**, with
**37 minutes remaining**. Finished stringing, flatness, fit and spill sealing
remain unreported.

## Reproduce offline

These manual commands do not send a print or run on commits/builds:

```sh
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prints/2026-10-23-mounting-gasket-tpu85a-right06-mark2/prepare_mark2.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prints/2026-10-23-mounting-gasket-tpu85a-right06-mark2/continuous_layers.py
tools/cad-venv/bin/python hardware/printed-parts/faucet/industrial/prints/2026-10-23-mounting-gasket-tpu85a-right06-mark2/review_paths.py
```
