# Organizer-fit tube snaps — Mark2

One comparison floor carries **Ø6.55 / Ø6.65 / Ø6.75 mm** snaps, left to right
when facing the printer. The common floor is **54 × 14 × 3 mm**, flat on the
bed, with the tube axes horizontal and the mouths upward. The middle bore is
the accepted organizer dimension; the neighbours use its last **0.10 mm
diameter** tuning increment. The [trial description](../../README.md)
records the dimensions, identity and physical-fit questions.

The native estimate is **12 min 8 s**. The job is prepared for **Mark2's left
hardened 0.4 mm Standard-flow hotend**, with black PET-GF on external spool
254, reported by the printer as PET-CF. The job has not been submitted.

- [Ready native print archive](2026-10-26-tube-snap-three-bores-mark2-f10f7183/2026-10-26-tube-snap-three-bores-mark2-f10f7183.gcode.3mf)
- [Editable project](2026-10-26-tube-snap-three-bores-mark2-f10f7183/2026-10-26-tube-snap-three-bores-mark2-f10f7183.3mf)
- [Native preview](2026-10-26-tube-snap-three-bores-mark2-f10f7183/plate_1.png)
- [Offline preparation and native review](offline-review.json)
- [Layer-contact and leaf-path readings](path-review.json)
- [Preparation-time printer observation](printer-observation.json)
- [Manual preparer](prepare.py) and [local job declaration](job.json)

The [shared PET-GF profile](../../../../hardware/printed-parts/petgf.3mf)
supplies the process: 0.20 mm first layer, 0.24 mm normal layers, two wall
loops and 15% gyroid infill. Tree(auto)/Default supports and automatic brim
remain enabled in the profile; the native slice generates **no supports or
brim**. The normal Mark2 +0.04 mm user Z trim emits `G29.1 Z0.02` after the
reset on Textured PEI. The archive uses only the left nozzle.

The native review binds the source STL, source STEP and editable project to
the sliced geometry and confirms **135.485 mm** minimum full-bead clearance
to the usable bed edge. The six upper leaves each retain a connected emitted
bead footprint through their layers. These are commanded-path readings;
adhesion, wing survival and actual tube grip are the purpose of the test.

Keep the left-to-right identity when removing the floor. Use the actual
quarter-inch tube to compare insertion, seated grip, axial movement and
release, and report the A/B/C position of any failure.
