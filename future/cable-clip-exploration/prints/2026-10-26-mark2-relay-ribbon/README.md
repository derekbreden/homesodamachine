# Bare J5 relay-ribbon coupon — Mark2

The **10 min 1 s** upright job is prepared for Mark2’s left hardened 0.4 mm
Standard-flow nozzle in black Polymaker Fiberon PET-GF15. The editable project
and sliced archive identify **task 1379210744**, running on Mark2. Its single
Send was accepted **October 26 at 11:11 p.m. CDT**, with print error 0 and no
HMS in the launch receipt.

The [study](../../README.md) describes the bare 22 AWG 4P J5 ribbon and its
proposed west-wall location. This coupon is not a production enclosure feature.
The clip prints **entry-up in its installed orientation**. The 3 mm host wall
is 24 mm wide and extends 6 mm below the hook, giving one **72 mm²** native
bed footprint. The hook grows from the wall on a 45° corbel starting at print
Z6 mm. Overall print height is 25.70 mm. The 0.75 mm retaining lip keeps its
flat underside.

- [Editable project](2026-10-26-relay-ribbon-4p-upright-mark2-78832950/2026-10-26-relay-ribbon-4p-upright-mark2-78832950.3mf)
- [Native print archive](2026-10-26-relay-ribbon-4p-upright-mark2-78832950/2026-10-26-relay-ribbon-4p-upright-mark2-78832950.gcode.3mf)
- [Native preview](2026-10-26-relay-ribbon-4p-upright-mark2-78832950/plate_1.png)
- [Accepted launch receipt](launch.json), [launch context](launch-context.json) and [preflight](preflight.json)
- [Offline preparation and native review](offline-review.json)
- [Pocket, entry, wall footprint and corbel path reading](path-review.json)
- [Manual preparer](prepare.py), [path reader](path_review.py) and [local declaration](job.json)

The shared PET-GF profile retains **Tree(auto)/Default supports**. This coupon
requests **no brim** and uses its larger wall footprint for bed attachment.
It uses a 0.20 mm first layer, 0.24 mm normal layers, two wall loops
and 15% gyroid infill. Mark2’s +0.04 mm user trim emits `G29.1 Z0.02` after
the reset on Textured PEI. The native review passes with a **147.916 mm**
minimum full-bead bed margin and a **2.16 g** profile-based material estimate.

The path reading finds **no support or brim anywhere in the job**. The first
and second model layers each have one connected footprint. Every second-layer
road has some first-layer bead contact; combined overlap is **87.7%**. Each
connected section containing the hook contacts the previous model layer,
including its first corbel layer. These are commanded paths, not physical
adhesion or surface-finish acceptance.

Actual bare-ribbon entry, grip, axial slide, release and layer/root survival
remain untested. This preparation does not integrate a production enclosure feature.
