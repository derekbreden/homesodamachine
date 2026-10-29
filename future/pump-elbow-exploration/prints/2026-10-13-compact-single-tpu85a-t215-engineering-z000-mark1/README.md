# Single TPU 85A elbow — 215°C normal layers

Mark1 accepted task **1337710290** on **2026-10-13 at 23:05:30 CDT**.
The [launch receipt](launch.json) binds the submitted archive and G-code.

The [in-progress physical record](physical-result.json) reports faint curl
by **layer 21 (Z2.60 mm)** and about the same defect as two prints earlier
by **layer 27 (Z3.32 mm)**. The user clarifies that layer 28 was when curl
was noticed, not an established sudden onset. The read-only layer-29 snapshot
shows 215°C actual and target temperature, with no printer errors. No early
visual improvement is reported; completed-part results remain pending.

One compact elbow on Mark1's right fixed
0.6 mm nozzle, TPU 85A, glued Engineering Plate and zero user Z trim. Native
estimate: **67 minutes / 4.30 g**.

The target is an intact underside and rim without upward curl, ragged loops
or nozzle pickup. The [10 mm/s physical record](../2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json)
contains the user's reassessment and six rim close-ups. A dependable quality
improvement from the speed change is unestablished. The user declines the
13 mm/s midpoint.

The identified rough-edged 225°C article has
[reported firm, stretchy friction fit](../2026-10-13-compact-single-tpu85a-outer10-engineering-z000-mark1/physical-result.json)
with manageable manual insertion and no jig. This trial retains its geometry,
including the cuff bores, insertion depths, walls and entries. Fit of the
215°C article and fit after surface correction remain unassessed.

This candidate tests **215°C normal layers**, retaining the **225°C first
layer** and **10 mm/s ordinary outer-wall setting**. The [native readback](native-readback.json)
confirms that normal-layer nozzle temperature and the recipe label are the
only differences from the identified 10 mm/s archive. The native mesh and
pose match; 100% part/auxiliary fan commands, 35°C bed, 0.20 mm first / 0.12 mm
normal layers, 0.62 mm line widths and `G29.1 Z0` are retained.
The [emitted-command review](emitted-commands.json) records the temperature
transition and actual left-lip commands. The [complete-perimeter review](curl-toolpath-review.json)
shows **14.37 mm/s at layer 21, 16.40 mm/s at layer 27 and up to 21.80 mm/s
by layer 32**. Separate process overhang settings replace the ordinary
outer-wall value. This trial does not establish a test of a 10 mm/s lip.
The commanded temperature and fans are steady across layers 17–28, and the
lip is away from the seam. The interior opening adds paths at layer 29,
after reported curl is already visible.

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

The [offline overhang-speed candidate](../2026-10-13-compact-single-tpu85a-overhang10-engineering-z000-mark1/README.md)
retains the accepted-fit article's 225°C recipe and geometry, with the two
higher overhang entries capped at 10 mm/s. Its actual lip commands are
verified; it is not submitted.

- [Editable project](2026-10-13-compact-single-elbow-tpu85a-outer10-t215-engineering-right06-z000-mark1.3mf)
- [Native archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/pump-elbow-exploration/prints/2026-10-13-compact-single-tpu85a-t215-engineering-z000-mark1/2026-10-13-compact-single-elbow-tpu85a-outer10-t215-engineering-right06-z000-mark1.gcode.3mf)
- [Manual preparation script](prepare_mark1.py)

The script prepares a slice offline. It does not connect to a printer or submit
a job. Fit of this recipe, clamping, sealing, retained grip and lifetime remain
unqualified.
