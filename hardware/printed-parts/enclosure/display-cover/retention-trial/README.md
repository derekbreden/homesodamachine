# Machine display retention trial

This receiver is paired with the selected [0.75 mm extra-arm-reach cover](../retention-reach-trial/README.md),
which snaps cleanly, has no noticeable bow and passes shaking. The dimensions below
describe this folder's 0.50 mm cover and the fixed receiver. The [production cover](../README.md)
uses the accepted horizontal wings. This retained trial also supplies helpers to the
[face-up trial](../face-up-trial/face_up_trial.py).

One complete cover and a matching receiver surround. The cover is symmetric across
both screen axes. Its two leaves each run, centered along
the screen, with square hooks. Each root has at least
 of bezel outside it at the rounded corners and an inward
 fillet. The span is the largest half-millimetre increment within
that root-stock envelope.

The leaves sit inward per side. Each hook overlaps its catch by
 when centered and at least at full lateral float.
Its bearing face stands below the catch. The insertion nose
runs down from its square land, and the leaf reaches
 below the visible face. The receiver slots have
 clearance at each end and open inward flex lanes.

Print the cover visible face down on Mark2 and the receiver with its display plane at
 on H2C. Both use black PET-GF, the left 0.4 mm nozzle, 0.24 mm layers with
a 0.20 mm first layer, two walls, and the saved speeds and wall order. Supports carry
the flat hook bearings and receiver seats. The cover's support lanes are exposed beside
the leaves; the receiver opens underneath and at the back for support removal.

The [geometry reading](geometry-check.json) measures both axes of cover symmetry,
root stock, the unchanged bezel, seated clearance and engagement. The [physical fit report](physical-acceptance.json) passes shaking and records a very small
bow with the snaps fully engaged. Insertion force and repeated-use performance are
unmeasured. The [arm-reach trials](../retention-reach-trial/README.md) use this same receiver.

`retention_trial.py` writes both STEP/STL/viewer triplets. `prepare_print.py` prepares
one part per printer. The printer starts use the shared-circuit three-minute minimum.

Print records: [cover on Mark2](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-28-display-cover-retention-mark2-v12/README.md), [receiver on H2C](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-28-display-receiver-retention-h2c-v2/README.md).
