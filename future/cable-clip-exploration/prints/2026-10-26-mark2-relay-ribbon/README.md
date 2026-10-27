# Bare J5 relay-ribbon coupon — Mark2

The **8 min 36 s** job is prepared for Mark2’s left hardened 0.4 mm
Standard-flow nozzle in black Polymaker Fiberon PET-GF15. The editable project
and sliced archive are ready; **no printer job has been submitted**.

The [study](../../README.md) describes the bare 22 AWG 4P J5 ribbon and its
proposed west-wall location. This coupon is not a production enclosure feature.
The 3 mm host and clip print entry-down, matching an installed-up mouth on
ceiling-down back-top. The host ends at the exact 19.70 mm clip height, giving
both the wall and outer arm a bed face. Native contact areas are 42 and
24 mm², respectively. The pocket closes across a 2.20 mm span at print Z11.50 mm.

- [Editable project](2026-10-26-relay-ribbon-4p-print-mark2-b4879c6b/2026-10-26-relay-ribbon-4p-print-mark2-b4879c6b.3mf)
- [Native print archive](2026-10-26-relay-ribbon-4p-print-mark2-b4879c6b/2026-10-26-relay-ribbon-4p-print-mark2-b4879c6b.gcode.3mf)
- [Native preview](2026-10-26-relay-ribbon-4p-print-mark2-b4879c6b/plate_1.png)
- [Offline preparation and native review](offline-review.json)
- [Pocket, entry and bridge path reading](path-review.json)
- [Manual preparer](prepare.py), [path reader](path_review.py) and [local declaration](job.json)

The shared PET-GF profile retains **Tree(auto)/Default supports and automatic
brim**. It uses a 0.20 mm first layer, 0.24 mm normal layers, two wall loops
and 15% gyroid infill. Mark2’s +0.04 mm user trim emits `G29.1 Z0.02` after
the reset on Textured PEI. The native review passes with a **152.934 mm**
minimum full-bead bed margin and a **1.29 g** profile-based material estimate.

The path reading finds **no support or brim in the cable seat or entry
corridor**. The outer arm remains one connected bead section below the bridge,
and every sampled layer above the first contacts the previous model layer.
The second-layer roads all have some first-layer bead contact; their combined
coverage over the first-layer footprint is 84.0%. These are commanded paths,
not physical adhesion or bridge-finish acceptance.

Actual bare-ribbon entry, grip, axial slide, release and layer/root survival
remain untested. No launch or production integration is included in this preparation.
