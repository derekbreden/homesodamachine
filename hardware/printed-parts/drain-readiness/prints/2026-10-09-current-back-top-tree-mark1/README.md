# Automatic-support back top on Mark1

This replacement prints the reviewed three-row rear wall with Tree (auto),
Default style. Bambu retains automatic support placement and normal sections it
chooses. The branch angle is 45° and trunk-diameter growth is
0.5°; the part is shifted 5 mm toward printer X−. These
plate settings keep the complete model/support/brim footprint inside the
required 20 mm bed inset. The [native review](native-review.json) reads a
21.40 mm minimum margin.

The source mesh and all 23 solid-host reinforcement modifiers match the
[reviewed compatible back top](../2026-10-08-current-back-top-mark1/README.md).
All 50 [mating and hardware checks](compatibility-check.json) apply to that
identical geometry. The layer schedule, reinforcement, support gaps and core
process remain intact. The [support-interface comparison](support-interface-comparison.json)
records changed automatic contact areas after compensating for placement.
The [exact-STL region-presence reading](support-interface-region-presence.json)
finds interface-envelope overlap at all 101 relevant connected overhang-region
slabs. This establishes presence, not complete coverage or physical stiffness. The
[support-clearance reading](support-clearance.json) checks every emitted support
road against nine exact protected exterior faces; the functional rear-port
field has a separate retained contact reading.

Mark1 uses physical PET-GF through its fixed left hardened 0.4 mm nozzle and
external slot 254, on Textured PEI. Its standard requested +0.18 mm trim emits
`G29.1 Z0.16`. Probing clump detection is off. Timelapse and bed leveling are
on at Send. The native estimate is 27.55 hours and
844.4 g at the saved density. The
[launch receipt](launch.json) records submission and exact printer acceptance.

The [rejected article](../2026-10-08-current-back-top-mark1/physical-result.json)
has impracticable normal-support removal throughout. This replacement still
needs physical cleanup, finish and installed-fit assessment.

Mark1 accepted task `1324612230` at 5:46 PM CDT on 2026-10-09.
The native-duration forecast is about 9:19 PM CDT on 2026-10-10;
startup, pauses and actual speed can change that forecast.
