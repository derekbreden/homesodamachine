# Nameplate with flat side wings

The nameplate has a flat 3.36 mm face, with no raised perimeter. Its back and both
wings print directly on the bed, face up, without supports. Each wing projects
2.40 mm sideways, is 1.68 mm thick, and spans 30 mm of the plate height. Rounded
wing ends stop short of the show corners. The receiver's rear diamond opening
provides access to bend the plate outward for removal.

All 29 white artwork solids, including the logo, drop, lettering and QR, rise
0.48 mm above the face and embed 0.72 mm into it. The Mark2 correction is white
X −0.50 mm, Y +0.70 mm, implemented by the slicer's native extruder offset.
The [appearance reference](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-flat-wings-mark2-v3/physical-result.json)
records the accepted artwork finish. Its QR scan and residual alignment error
are unmeasured.

## Static fit

The locating gaps use `../../../cadlib/fits.py`. Each nonlocating wing tip has
0.25 mm of X clearance as a narrow-slot fit trial. This plate is inserted by
hand and has no sliding-fit or low-force additions.

| Surface | Nominal clearance |
|---|---:|
| Body left and right | 0.15 mm each; 0.30 mm total X travel |
| Body ordinary Z end | 0.15 mm |
| Body print-down Z end | 0.15 + 0.25 mm for the rough receiver face |
| Total Z travel | 0.55 mm |
| Wing tip to slot end in X | 0.25 mm each at center; 0.10 mm minimum at full body X float |
| Wing ordinary Z end | 0.15 mm |
| Wing print-down Z end | 0.15 + 0.25 mm for the rough receiver face |
| Wing top to flat retaining bearing | 0.15 mm; 1.83 mm slot for a 1.68 mm wing |
| Plate back and wing undersides at the seating datum | 0 mm |

The body and wing limits constrain the same motion; their gaps do not add to
each other. The dimensions above are pure-axis limits. Rounded corners constrain
combined translations. The receiver prints with assembled −Z as build-up, so its
negative-Z pocket ends receive the directional rough-face allowance. Y slot walls
print vertically and receive the ordinary static gap.

The body establishes X location. Its wing tips have another 0.10 mm of relief
beyond the 0.15 mm static gap to avoid redundant location in narrow slots. The
slot's thickness gap and Z ends retain their standard allowances. The
[physical observation](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-flat-standard-mark2-v5/physical-result.json)
records bowing with apparent body clearance; interference from printed corner
rounding remains a hypothesis for this receiver test.

The entry bevel is 1.10 mm wide and 0.40 mm deep at each slot mouth. It clears the
wing's rotation during hand-bent insertion. The outer flat bearing keeps the
0.15 mm seated gap. At full lateral float, each wing retains at least 2.10 mm of
geometric overlap and 1.00 mm of flat bearing width. The retaining lip is 1.53 mm
thick over the flat bearing and 1.13 mm at the bevel entrance.

`wing_interface.py` supplies the reusable wall cutter. The full enclosure awaits
the corrected coupon's physical fit result. Use the matching receiver for this
trial; its mouth and slots establish the locating clearances.

## Verification and printing

`horizontal_wing_trial.py` generates the STEP/STL/viewer triplets and
`geometry-check.json`. `verify_insertion.py` checks 101 positions of an ideal
circular bend in the central cross-section. `verify_pair.py` checks exported
solids at all six pure-axis travel limits and just beyond each, then verifies
the emitted artwork, wing layers, supports and native coordinate correction.
The bend model does not establish insertion force, fatigue or corner motion.

`prepare_pair.py` slices the complete pair for Mark2. The nameplate has no supports
or brim. The receiver uses the shared `petgf.3mf` tree supports and its enclosure
orientation: 0.40 mm support XY, 0.45 mm upper Z and 0.30 mm lower Z gaps. Support
and interface material are explicitly black. Every emitted support bead is checked
against the wing slots and their entry bevels; support removal remains a bench test.

Both objects use a 0.20 mm first layer, a 0.28 mm second layer, then 0.24 mm layers.
Their shared schedule permits the prime tower and preserves complete raised-artwork
layers at 3.60 and 3.84 mm. Saved speeds, wall order and 15% infill overlap apply.
`prepare_receiver.py` and `verify_receiver.py` create and check the receiver-only
comparison on Mark2. It uses 0.20 mm followed by 0.24 mm layers, shared tree
supports and the existing flat nameplate. Its
[slice review](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-nameplate-tip025-receiver-mark2-v6/README.md)
records a 42 min 37 sec estimate and a geometric comparison proving that only
the two slot-tip strips changed. Physical bow, insertion and retention remain
to be evaluated with this receiver.
