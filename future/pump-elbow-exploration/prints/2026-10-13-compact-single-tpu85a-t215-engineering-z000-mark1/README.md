# Single TPU 85A elbow — 215°C normal layers

**Prepared offline; not submitted.** One compact elbow on Mark1's right fixed
0.6 mm nozzle, TPU 85A, glued Engineering Plate and zero user Z trim. Native
estimate: **67 minutes / 4.30 g**.

The target is an intact underside and rim without upward curl, ragged loops
or nozzle pickup. The [10 mm/s physical record](../2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json)
contains the user's reassessment and six rim close-ups. A dependable quality
improvement from the speed change is unestablished. The user declines the
13 mm/s midpoint.

This candidate tests **215°C normal layers**, retaining the **225°C first
layer** and **10 mm/s outer wall**. The [native readback](native-readback.json)
confirms that normal-layer nozzle temperature and the recipe label are the
only differences from the identified 10 mm/s archive. The native mesh and
pose match; 100% part/auxiliary fan commands, 35°C bed, 0.20 mm first / 0.12 mm
normal layers, 0.62 mm line widths and `G29.1 Z0` are retained.
The [emitted-command review](emitted-commands.json) records the temperature
transition and actual outer-wall speed in the curl-onset region.

The hypothesis is that reducing nozzle temperature helps the fresh edge hold
its shape. Excess heat is not established as the cause. Simplify3D identifies
insufficient solidification as a cause of later-layer curl and suggests a
5–10°C reduction when cooling is already in use. Bambu publishes a
200–250°C nozzle range for TPU 85A. This candidate uses a 10°C normal-layer
reduction from the manufacturer's selected H2C profile. Extrusion continuity
and layer bonding still require observation; edge appearance supplies no
sealing or pressure result.
[Curling guidance](https://www.simplify3d.com/resources/print-quality-troubleshooting/curling-or-rough-corners/),
[temperature adjustment](https://www.simplify3d.com/resources/print-quality-troubleshooting/overheating/),
[Bambu TPU 85A settings](https://us.store.bambulab.com/products/tpu-85a-tpu-90a/).

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-outer10-t215-engineering-right06-z000-mark1.3mf)
- [Native archive](2026-10-13-compact-single-elbow-tpu85a-outer10-t215-engineering-right06-z000-mark1.gcode.3mf)
- [Manual preparation script](prepare_mark1.py)

The script prepares a slice offline. It does not connect to a printer or submit
a job. Fit, clamping, sealing, retained grip and lifetime remain unqualified.
