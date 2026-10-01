# Display receiver with 0.30 mm body X and 0.60 mm wing-thickness clearance

H2C accepted task **1297296218** at 2026-09-30T21:01:31.807503+00:00.
The native estimate is **2 h 49 min 41 sec**, **68.86 g** at the saved profile density.
Use the existing face-up display cover from the H2C v1 pair.

| Interface | Nominal dimension |
|---|---:|
| Body X clearance, each side | 0.30 mm |
| Gap above the seated wing | 0.60 mm |
| Wing-tip X gap, centered / full body float | 0.55 / 0.25 mm |
| Minimum wing capture at full X float | 3.00 mm |

[Exact solid comparison](geometry-delta.json) confines the change to 70.1035 mm³
of added material in the full-depth body-X opening.
The last 0.20 mm-per-side body-X increment is undone. Wing pockets retain their dimensions.
Wing-thickness clearance, seating datums and the existing mating part are held.
Pure-axis seated travel and the ideal 101-position insertion envelope pass.
These checks do not establish printed force or retention.

[Native verification](verification.json) confirms one bed-rooted tree body and
no model-rooted bodies. The wing pockets have clear print-down exits through
the fixture. The 1.80 mm retaining lip and 0.60 mm wing-thickness gap are held.
That thickness direction is local Z on this display, corresponding to nameplate Y.

The receiver uses its enclosure orientation, a 0.20 mm first layer, 0.24 mm above,
saved speeds and wall order, and shared 0.40 XY / 0.45 top Z / 0.30 bottom Z
tree-support gaps. Support and interface are black; physical removal remains a
bench check. [Published artifacts](published-artifacts.json) match the live STEP
and viewer payload. [Geometry lint](geometry-lint.log) has no unanswered findings.

The [launch receipt](launch.json) binds the reviewed archive, left black PET-GF,
ordinary startup options including Auto nozzle offset, and the user's clear-bed
report. Startup was 288.2 seconds after the other printer's
preceding accepted start, exceeding the 180-second minimum.
[Postlaunch](postlaunch.json) confirms the matching task RUNNING without errors.

The [physical result](physical-result.json) accepts the existing face-up cover in
this receiver. The shake test passes and the appearance is acceptable with a small
residual bow. Derek suspects insertion bending leaves some set; that cause is
unverified. Further bow tuning is not requested.
