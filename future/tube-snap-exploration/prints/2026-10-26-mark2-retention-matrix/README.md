# Tube-snap retention matrix — Mark2

Nine constant-**R3.275 mm / Ø6.55 mm** clips print on **three separate strips**,
so a long tube can be tested after moving the strips apart. Each strip has
a 60 × 16 × 3 mm floor and three clips side by side across X. The tube axes
run along Y. Raised A1–C3 labels preserve identity off the bed.

| Row / strip | Wing thickness | 1 — left | 2 — centre | 3 — right |
| --- | ---: | --- | --- | --- |
| A — front | 1.44 mm | Reference wrap | +5° per wing | +10° per wing |
| B — middle | 1.92 mm | Reference wrap | +5° per wing | +10° per wing |
| C — rear | 2.40 mm | Reference wrap | +5° per wing | +10° per wing |

A1 is the control: the prior smallest-bore clip geometry. The
[geometry report](../../retention-matrix-geometry.json) measures all nine
native bore sections at the same radius and verifies A1 against the
[first trial](../2026-10-26-mark2-organizer-fit/physical-result.json).
The [study description](../../README.md) gives circular coverage and mouth
widths, including the way nose thickness affects the mouth.

The native estimate is **29 min 43 s**. The job uses Mark2's left hardened
0.4 mm Standard-flow hotend and black PET-GF external spool 254, reported
as PET-CF. The saved PET-GF recipe retains 0.20 mm first / 0.24 mm normal
layers, Tree(auto)/Default, two walls and 15% gyroid infill. The native slice
emits **no support bodies**, with **132.485 mm** minimum full-bead bed margin.
The normal +0.04 mm requested trim emits +0.02 mm on Textured PEI after reset.

Mark2 accepted task **1379148667** at **22:28 CDT on October 26**. The
[launch receipt](launch.json) identifies the exact reviewed three-object
archive as RUNNING with print error 0 and no HMS entries. The
[launch context](launch-context.json) records the user instructions,
[fresh two-printer preflight](preflight.json) and shared-circuit startup spacing.

- [Native print archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/tube-snap-exploration/prints/2026-10-26-mark2-retention-matrix/2026-10-26-tube-snap-retention-matrix-mark2-4f9f9960/2026-10-26-tube-snap-retention-matrix-mark2-4f9f9960.gcode.3mf)
- [Editable project](2026-10-26-tube-snap-retention-matrix-mark2-4f9f9960/2026-10-26-tube-snap-retention-matrix-mark2-4f9f9960.3mf)
- [Native preview](2026-10-26-tube-snap-retention-matrix-mark2-4f9f9960/plate_1.png)
- [Offline source and native review](offline-review.json)
- [Individual wing and layer-contact reading](path-review.json)
- [Manual preparer](prepare.py)

Separate the three pieces before feeding a long tube into any clip. Compare
insertion, pull-out resistance, seated grip and layer/root survival by
printed sample label. A native slice does not establish those physical results.
