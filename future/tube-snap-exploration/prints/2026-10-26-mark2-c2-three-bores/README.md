# C2 tube-snap bore comparison — Mark2

One **60 × 16 × 3 mm** floor carries C2 and two smaller bores. The raised labels
read **6.55 / 6.45 / 6.35** from left to right. All three retain **2.40 mm wings**,
**125.421° circular wrap per wing**, rounded noses, filled roots and 8 mm span.
The floor prints flat with mouths upward. Tube axes run along Y so a long tube
can test any one clip without encountering its neighbours.

The left 6.55 mm clip matches C2's native geometry exactly. The smaller bores use
the organizer's established **0.10 mm diameter** tuning step. The [geometry report](../../c2-bore-geometry.json)
binds every native bore section and the control comparison. The [physical feedback](../2026-10-26-mark2-retention-matrix/physical-result.json)
records Derek's C2 preference and request for this comparison.

This standalone job is **prepared, not submitted**. The
[combined plate](../../../snap-fit-tests/2026-10-26-mark2-combined/README.md)
uses the same part with two 9 mm-wall cable coupons and its experimental cooling
recipe. The standalone native estimate is **14 min 12 s** and **3.98 g** using
the saved profile density.

- [Editable project](2026-10-26-tube-snap-c2-three-bores-mark2-cf1d0d5d/2026-10-26-tube-snap-c2-three-bores-mark2-cf1d0d5d.3mf)
- [Native print archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/tube-snap-exploration/prints/2026-10-26-mark2-c2-three-bores/2026-10-26-tube-snap-c2-three-bores-mark2-cf1d0d5d/2026-10-26-tube-snap-c2-three-bores-mark2-cf1d0d5d.gcode.3mf)
- [Native preview](2026-10-26-tube-snap-c2-three-bores-mark2-cf1d0d5d/plate_1.png)
- [Offline preparation and native review](offline-review.json)
- [Individual wing and layer-contact reading](path-review.json)
- [Manual preparer](prepare.py) and [local declaration](job.json)

Mark2 uses its left hardened 0.4 mm Standard-flow hotend and black PET-GF external
spool 254, reported as PET-CF. The saved process retains a 0.20 mm first layer,
0.24 mm normal layers, two walls, 15% gyroid infill and Tree(auto)/Default.
Its +0.04 mm requested user trim emits `G29.1 Z0.02` after reset on Textured PEI.
The native archive has **no support or brim**, with **132.485 mm** minimum
full-bead bed margin.

All six upper wings have connected bead footprints touching the previous layer.
Minimum sampled wing-section coverage is **99.50%**. Every sampled upper-wing
road and second-layer road has previous-layer bead contact. These path readings
do not predict physical grip, adhesion or layer strength.
