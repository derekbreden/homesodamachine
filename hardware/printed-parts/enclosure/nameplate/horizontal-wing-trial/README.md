# Nameplate with flat side wings

The plate prints face up with its back and both wings on the bed. Each wing
projects 3 mm sideways, is 1.2 mm thick (half the plate thickness), and spans
32 mm of the plate height. Rounded wing ends stop short of the show corners.
Insertion flexes the plate to enter the matching receiver slots.

All 29 white artwork solids—including the logo, drop, lettering and QR—rise
0.48 mm above the black face, with 0.72 mm embedded in it. The nameplate has
**no supports**. Its 0.20 mm first and 0.28 mm second layers establish the
following 0.24 mm planes: wing top 1.20, inlay bottom 1.68, face 2.40, white top
2.88 mm. Saved speeds, wall order and infill overlap apply.

The receiver has 1.50 mm slots for the 1.20 mm wings: 0.30 mm total thickness
air, 0.30 mm tip air, and 2.70 mm minimum lateral engagement at full sideways
float. Its 0.90 mm front ledges capture the wings. `wing_interface.py` provides
the shared cutter; the full enclosure awaits this coupon's physical fit result.
This clearance applies to these supported surfaces and low insertion force;
it is not a universal fit allowance.

`geometry-check.json` verifies valid solids, zero seated clash, and capture in
the outward direction. Physical insertion strain, relaxed flatness, retention
under shaking, support removal and QR scanning still require inspection.

`prepare_print.py` and `verify_print.py` prepare and inspect the Mark2 plate.
The native slice contains the wings from the first layer, no support roads, and
white paths for every artwork region on both raised layers. Its estimate is
30 minutes 8 seconds. **The nameplate is held for Mark2's alignment result.**

`prepare_receiver.py` and `verify_receiver.py` prepare the H2C coupon in the
enclosure wall orientation. It uses normal snug black supports with 0.80 mm XY
and 0.45 mm upper/lower Z clearance. Every support bead has been checked against
both wing slots: neither slot contains support. The central support exits
through the open front before assembly; the two small bed-rooted bodies are
exposed at the bottom corners. Physical removability is still part of the trial.

The receiver's native review and launch receipt are retained in
[`2026-09-29-nameplate-flat-wing-receiver-h2c-v1`](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-flat-wing-receiver-h2c-v1/README.md).
