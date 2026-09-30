# Nameplate receiver with 0.15 mm body X and 0.45 mm wing Y clearance

Mark2 accepted task **1297285813** at 2026-09-30T20:56:43.564281+00:00.
The native estimate is **43 min 4 sec**, **20.06 g** at the saved profile density.
Use the existing flat nameplate from task 1294806669.

| Interface | Nominal dimension |
|---|---:|
| Body X clearance, each side | 0.15 mm |
| Gap above the seated wing | 0.45 mm |
| Wing-tip X gap, centered / full body float | 0.25 / 0.10 mm |
| Minimum wing capture at full X float | 2.10 mm |

[Exact solid comparison](geometry-delta.json) confines the change to 47.3676 mm³
of added material in the body-X opening and wing-slot X ends.
The last 0.20 mm-per-side body-X increment is undone. The matching 0.20 mm wing-tip increment is also undone.
Wing-thickness clearance, seating datums and the existing mating part are held.
Pure-axis seated travel and the ideal 101-position insertion envelope pass.
These checks do not establish printed force or retention.

[Native verification](verification.json) measures 468 sections across both flat
bearings: a 2.13 mm slot and 1.23 mm retaining stock are present in the emitted
bead envelopes. No support bead enters either slot or entry bevel. One shared
PET-GF tree rises from the bed to its labelled interface after 41.28 mm.

The receiver uses its enclosure orientation, a 0.20 mm first layer, 0.24 mm above,
saved speeds and wall order, and shared 0.40 XY / 0.45 top Z / 0.30 bottom Z
tree-support gaps. Support and interface are black; physical removal remains a
bench check. [Published artifacts](published-artifacts.json) match the live STEP
and viewer payload. [Geometry lint](geometry-lint.log) has no unanswered findings.

The [launch receipt](launch.json) binds the reviewed archive, left black PET-GF,
ordinary startup options including Auto nozzle offset, and the user's clear-bed
report. Startup was 22755.1 seconds after the other printer's
preceding accepted start, exceeding the 180-second minimum.
[Postlaunch](postlaunch.json) confirms the matching task RUNNING without errors.

Physical result: Fit accepted by Derek with the existing nameplate. See the
[physical result](physical-result.json) for the exact accepted pair and scope.
