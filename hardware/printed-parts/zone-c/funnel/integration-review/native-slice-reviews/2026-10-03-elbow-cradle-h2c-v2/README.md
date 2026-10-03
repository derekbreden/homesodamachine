# Current elbow cradle native H2C slice

This offline native slice binds the exact current STEP and STL below. It uses the
shared PET-GF recipe, left 0.4 mm nozzle and external black PET-GF (profile label
PET-CF). The first layer is 0.20 mm; normal layers are 0.24 mm. Saved speeds,
wall order and 15% infill/wall overlap are retained. Elephant-foot compensation
is zero and there is no brim. Requested H2C Z trim +0.18 mm emits G29.1 Z0.16
for the textured plate. **No print has been submitted from this receipt.**

| Artifact | SHA-256 |
| --- | --- |
| STEP | `02127f475220ce77f32d955cb795fc941f43c36346ee4fdfaf5210b2eb07047d` |
| STL | `651e537dfff26b46a18509768de188e617c63c3e75fb2d8e9622ddcff7171f03` |
| Native input project | `63408110336a60e23ffa66f112849a08e990470ef9ac70684d3bb59b48915c9e` |
| Native archive | `80beec7102cb67f18497179e0934156f6f45cfdf4305d1a93ff35c4da6c8fcd7` |
| Emitted G-code | `3e3374fb6e51107d4a019990894da64c47491f4f4e915f02f6a5efab971cf17b` |

The [preparation](preparation.json) and [verification](verification.json) retain
the exact native files, settings, production pose, embedded-mesh equality,
ZIP integrity and G-code MD5 checks. Native estimate: **29 min 59 s**.

The [emitted-path review](emitted-path-review.json) covers all
**154 model layers**, including every native stock
component and outer/hole perimeter. No native component lacks model wall paths.
Every second-layer bead overlaps the first layer by at least
75.7% of its area;
the outer-wall minimum is 99.9%.
All model and support beads retain at least
135.647 mm to the reachable bed edge.

The [support audit](support-audit.json) retains **2 support bodies**,
0 without explicit interface labels.
The [complete removal sweep](support-removal-review.json) checks all emitted
support beads against native stock using their actual widths and slab heights.
The cradle prints bottom-down with its pocket opening upward. Its two supports reach the square external hook undersides. Every complete support bead, including any path without an interface label, has a clear outward sweep into open space. Detach the hook contacts, then remove the sections outward; the pocket stays free of support paths. The current production and trial cradle STL bytes are identical.

The [native mouth check](native-mouth-correction-check.json) retains the elbow seat, 0.65 mm catch gap and 3.15 mm hook tops. The aft collet clearance opens straight through the mouth; its floor retains 5.103 mm and its side walls retain 8.840 mm.

The [post-live geometry lint](geometry-lint.json) follows hash verification of the
production cradle on the site. Both its STL and the byte-identical trial STL
report zero unanswered findings; their two square retention ceilings retain
the recorded accessible supports.

The [accepted v4 record](../../../cradle-trial/physical-acceptance.json) remains
limited to its frozen printed pair. Current 3.15 mm hooks, corresponding slots
and flat silicone bearing require separate physical acceptance. Native slicing
does not establish insertion force, retention, operating life, support-removal
effort or contact finish.

![Native preview](preview.png)
