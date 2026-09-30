# Face-up display-cover fit trial

The bezel and both horizontal wings share a flat back, so the cover prints face
up with no supports. The matching receiver holds the display plane at the
enclosure's 30° print angle and uses the shared PET-GF tree supports. Each wing
pocket opens through the frame along print-down. The retaining lip remains;
there is no pocket floor beneath it to trap a short support strip.

## Geometry and clearances

X runs across the screen, Y up the screen and Z outward from its visible face.
These are the cover's local axes, before the receiver's print rotation.

| Feature | Trial dimension |
|---|---:|
| Bezel thickness | 3.84 mm |
| Optical opening at the glass | 107.5 × 71 mm |
| Wing thickness | 1.44 mm |
| Wing projection × span, each side | 3.60 × 70 mm |
| Body perimeter clearance | 0.15 mm each side; 0.30 mm total X or Y travel |
| Wing tip to slot end in X | 0.25 mm centered; 0.10 mm minimum at full body X float |
| Wing end clearance in Y at the retaining roof | 0.15 mm each |
| Wing top to retaining roof | 0.40 mm: 0.15 static + 0.25 for one supported roof |
| Cover back to seating datum | 0 mm |
| Receiver lip thickness | 2.00 mm |
| Capture beneath lip, centered | 3.45 mm per wing |
| Minimum capture at full sideways float | 3.30 mm |
| Glass perimeter clearance | 0.15 mm each side |

The body locates X. The extra wing-tip relief is a local narrow-slot trial, not
a sliding or low-force allowance. The hand-bent horizontal wings have no
spring-driven hook engagement. Their bedded faces receive no rough-surface
allowance. The retaining roof is supported; its one 0.25 mm allowance is applied
to the same normal gap as the ordinary 0.15 mm static clearance. The open slot
ends below that roof follow the print-down exit and do not establish another
body locating gap.

The visible face is flush with this receiver. Its glass seat is 5.84 mm below
the face: a 3.84 mm cover, 1 mm TPU gasket and 1 mm glass stack. The display sits
1.84 mm deeper than in the accepted vertical-leaf interface. Integration into
front-top requires a complete display-module and rear-housing clearance check.

## Verification and printing

The receiver accepts the existing face-up cover from the H2C v1 pair. That cover
STL is unchanged (SHA-256
`bd0545aa076fed3d7adc895df205b098f11a08b6fc37c883893115aec83dd5f2`).

Insertion flexes the middle of the bezel outward while both wings enter their
pockets. The open underside lets their tips dip during entry; the seating land
locates the relaxed cover. The seated CAD clears at all six pure-axis travel
limits and interferes just beyond them. An ideal circular-bend envelope clears
101 sampled positions in the central section. These checks do not qualify
insertion force, fatigue or three-dimensional corner motion. The vertical-leaf
cover's physical acceptance does not qualify this mechanism.

`face_up_trial.py` generates the geometry and checks a continuous print-down
exit beneath each wing pocket through the complete fixture, including its
standing cheeks. Publish with `tools/publish_now.py`, then lint the receiver.
`verify_insertion.py` records the entry envelope. `prepare_receiver.py` creates
the immutable H2C receiver-only slice; `verify_receiver.py` checks source hashes,
layer planes, profile settings and support connectivity, including unlabeled
support bodies. The native slice has one bed-rooted support body and no
model-rooted bodies. Straight exit access is geometrically clear; actual tree
breakup and removal remain a physical check.

The receiver uses the established H2C +0.18 mm trim, black PET-GF on the left
0.4 mm nozzle, a 0.20 mm first layer and 0.24 mm above it, normal speeds, wall
order and 15% overlap. Shared tree-support gaps are 0.40 mm XY, 0.45 mm upper Z
and 0.30 mm lower Z. Remove trees through the open underside before installing
glass or cover. The native estimate is **2 h 53 min 20 sec**, **69.97 g** at the
saved profile density. The
[slice review](../../tee-readiness/full-enclosure-print/native-slice-reviews/2026-09-29-display-open-wing-receiver-h2c-v2/README.md)
records the exact archive and launch. Support removal, relaxed flatness, complete
capture and shake retention need this physical receiver.
