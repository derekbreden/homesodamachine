# Current back top on Mark1

This plate prints the current redesigned three-row rear wall. The
[compatibility check](compatibility-check.json) reads the recorded front top,
front/back bottoms and funnel frame, together with installed prototype hardware.
All 50 checks pass, including shell intersections, joint slide and capture,
roof/frame clearance and installed component clearance.

The DIGITEN meter retains its existing body and moves 2.9 mm toward X− to seat
in this back top. Its checked minimum native clearance is 0.154 mm. The other
fixed prototype component fixtures retain their recorded positions.

Mark1 uses physical PET-GF through its fixed left hardened 0.4 mm nozzle and
external slot 254. The standard requested +0.18 mm trim emits `G29.1 Z0.16`
on Textured PEI. A different Mark1 trim requires authorization for that specific
print. The editable project preserves the reviewed model, 23 solid-host modifiers,
layer schedule and process settings. Probing clump detection is off. Timelapse
and bed leveling are on at Send.

The [native review](native-trim-review.json) binds the actual corrected archive
and its emitted paths. The estimate is about 27 hours 1 minute and 892.4 g at
the saved filament density. The [launch receipt](launch.json) records its one
foreground Send and observed printer acceptance.

This archive uses Normal (auto) supports with the default style across the rear
wall. Its preparation selected normal columns for the 20 mm bed margin; the
native removal routes establish access and do not qualify cleanup effort.
The [physical result](physical-result.json) rejects this article for impracticable
removal of every normal support. The operator intends to discard it. Installed
fit and finished surface qualification remain unassessed. The standing preparation preference is
[tree supports with specific exceptions](../../../enclosure/enclosure/README.md#support-removal-strategy).

Recheck current geometry against the prototype fixtures with:

```sh
tools/cad-venv/bin/python hardware/printed-parts/drain-readiness/check_prototype_back_top.py
```

Physical adhesion, support cleanup, finish and installed fit remain separate
from these geometric and native slice checks.
