# Face-up display-cover fit trial

The bezel and both horizontal wings share a flat back, so the cover prints face
up with no supports. The matching receiver holds the display plane at the
enclosure's 30° print angle and uses the shared PET-GF tree supports.

| Feature | Trial dimension |
|---|---:|
| Bezel thickness | 3.84 mm |
| Optical opening at the glass | 107.5 × 71 mm |
| Wing thickness | 1.44 mm |
| Wing projection × span, each side | 3.60 × 70 mm |
| Clearance above each wing | 1.20 mm |
| Receiver lip thickness | 1.20 mm |
| Minimum capture at full sideways float | 3.00 mm |
| Wing-tip clearance | 0.60 mm |
| Wing-end clearance | 0.30 mm, plus 0.75 mm at the print-down end |

The visible face is flush with this receiver. Its glass seat is 5.84 mm below
the face: a 3.84 mm cover, 1 mm TPU gasket and 1 mm glass stack. The display sits
1.84 mm deeper than in the accepted vertical-leaf interface. This trial requires
its matching receiver; integration into front-top includes a complete display
module and rear-housing clearance check.

Insertion flexes the middle of the bezel outward while both wings enter their
pockets. The relaxed wings retain the frame beneath the lips. The exact seated
CAD is clear at the center and both extremes of sideways float. An ideal
circular-bend envelope also clears the receiver through 101 sampled positions.
These checks do not qualify insertion force, fatigue or three-dimensional
corner motion. Flatness, complete capture and shake retention require this
physical pair. The accepted +0.75 mm vertical-leaf cover remains the physical
reference in [`../physical-acceptance.json`](../physical-acceptance.json).

The H2C plate contains one cover and one receiver. It uses the established
+0.18 mm trim, black PET-GF on the left 0.4 mm nozzle, a 0.20 mm first layer,
normal speeds, wall order and 15% overlap. The cover has a 0.28 mm second layer
to put its wings exactly on the 1.44 mm plane, then 0.24 mm layers. The receiver
uses 0.24 mm layers throughout above its first layer. Its shared support
clearances are 0.40 mm XY, 0.45 mm top Z and 0.30 mm bottom Z. Remove its trees
through the open fixture before installing glass or cover.

The native estimate for the pair is **3 h 10 min**, using **80.68 g** at the
saved profile density. The receiver's support removal remains a physical test.
The cover has zero emitted support paths.

Generate with `face_up_trial.py`, publish with `tools/publish_now.py`, then lint
the generated STLs. `prepare_print.py` creates an immutable native H2C slice;
`verify_print.py` checks its source hashes, layer planes, wing paths, profile
and support connectivity. `verify_insertion.py` records the entry envelope.
