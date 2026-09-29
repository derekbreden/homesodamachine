# Nameplate with flat side wings

The plate prints face up with its back and both wings on the bed. Each wing
projects 2.40 mm sideways, is 1.68 mm thick, and spans 30 mm of the plate height.
Rounded wing ends stop short of the show corners. The 3 mm wide perimeter is
3.36 mm thick; the recessed artwork field is 2.40 mm thick so insertion can flex
the middle. The receiver's rear diamond opening gives access to push the centre
outward for removal. This is a fit trial, including the required bending force.

All 29 white artwork solids—including the logo, drop, lettering and QR—rise
0.48 mm above the black face, with 0.72 mm embedded in it. The nameplate has
**no supports**. Its 0.20 mm first and 0.28 mm second layers establish the
following 0.24 mm planes: wing top and inlay bottom 1.68, field face 2.40,
white top 2.88, and frame top 3.36 mm. Saved speeds, wall order and infill overlap apply.

The receiver has 2.16 mm slots for the 1.68 mm wings: 0.48 mm total thickness
air, 0.50 mm tip air, and 2.00 mm minimum lateral engagement at full sideways
float. Its 1.20 mm front ledges capture the wings. The thickness gap lies between
vertical printed faces. Slot ends have 0.30 mm air plus an additional 0.75 mm at
the print-down end for rough overhang surfaces. The pocket mouth likewise has
0.20 mm perimeter air plus 0.75 mm at its print-down edge. `wing_interface.py` provides
the shared cutter; the full enclosure awaits this coupon's physical fit result.
This clearance applies to these supported surfaces and low insertion force;
it is not a universal fit allowance.

`geometry-check.json` verifies valid solids, zero seated clash, and capture in
the outward direction. [`insertion-envelope.json`](insertion-envelope.json)
checks 101 positions of an ideal circular bend in the central cross-section;
the body and wing envelopes clear the receiver throughout that path. It does
not establish insertion force, corner motion or fatigue. Physical insertion,
relaxed flatness, retention under shaking, receiver support removal and QR
scanning still require inspection.

`prepare_print.py` and `verify_print.py` prepare and inspect the Mark2 plate.
The native slice contains the wings from the first layer, no support roads, and
white paths for every artwork region on both raised layers. Its estimate is
32 minutes 50 seconds. **The nameplate is held for Mark2's alignment result.**

`prepare_receiver.py` and `verify_receiver.py` prepare the H2C coupon with CAD
−Z as build-up, matching the back-top enclosure's roof-down orientation. Its
tree support shape, speed, interface and clearance settings come directly from
`../../../petgf.3mf`: 0.40 mm XY, 0.45 mm upper Z, and 0.30 mm lower Z gaps.
Support and interface material are explicitly black. Normal Snug is excluded.
Check every emitted support bead against both wing slots and inspect the branches
through the open front before assembly. Physical removability remains a bench test.

The receiver's native review and launch receipt are retained in
[`2026-09-29-nameplate-flat-wing-receiver-h2c-v3`](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-flat-wing-receiver-h2c-v3/README.md).
