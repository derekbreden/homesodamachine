# Machine display retention trial

One complete cover and a matching receiver surround. The cover is symmetric across
both screen axes. Its two [1.3 mm](WALL) leaves each run [75 mm](SPAN), centered along
the screen, with [3.6 mm](LIP) square hooks. Each root has at least
[0.5 mm](ROOT_EDGE_STOCK) of bezel outside it at the rounded corners and an inward
[0.8 mm](ROOT_FILLET) fillet. The span is the largest half-millimetre increment within
that root-stock envelope.

The leaves sit [0.9 mm](INSET) inward per side. Each hook overlaps its catch by
[3.1 mm](OVERLAP) when centered and at least [2.8 mm](MIN_OVERLAP) at full lateral float.
Its bearing face stands [0.98 mm](BEARING_CLEARANCE) below the catch. The insertion nose
runs [3.2 mm](NOSE_DEPTH) down from its square land, and the leaf reaches
[15.4 mm](TIP_DEPTH) below the visible face. The receiver slots have
[0.5 mm](END_SLIP) clearance at each end and open inward flex lanes.

Print the cover visible face down on Mark2 and the receiver with its display plane at
[30°](ANGLE) on H2C. Both use black PET-GF, the left 0.4 mm nozzle, 0.24 mm layers with
a 0.20 mm first layer, two walls, and the saved speeds and wall order. Supports carry
the flat hook bearings and receiver seats. The cover's support lanes are exposed beside
the leaves; the receiver opens underneath and at the back for support removal.

The [geometry reading](geometry-check.json) measures both axes of cover symmetry,
root stock, the unchanged bezel, seated clearance and engagement. Physical insertion
force, shake retention and printed contact finish are unmeasured for this pair.

`retention_trial.py` writes both STEP/STL/viewer triplets. `prepare_print.py` prepares
one part per printer. The printer starts use the shared-circuit three-minute minimum.

Print records: [cover on Mark2](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-28-display-cover-retention-mark2-v12/README.md), [receiver on H2C](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-28-display-receiver-retention-h2c-v2/README.md).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/display-cover/retention-trial/retention_trial.py`
