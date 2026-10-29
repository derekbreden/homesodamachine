# Bare J5 relay-ribbon coupon — Mark2

**Derek stopped task 1379210744 before completion.** He describes the partial
coupon as “pretty melty” and requests more part-fan cooling and time between
layers, a 9 mm host wall, a longer cable cavity and variants on a combined
tube/cable test plate. The [physical result](physical-result.json) preserves his
exact report with [photo 1](physical-photo-1.jpg) and [photo 2](physical-photo-2.jpg).

The upright job’s native estimate is **10 min 1 s**, on Mark2’s left hardened
0.4 mm Standard-flow nozzle in black Polymaker Fiberon PET-GF15. The editable
project and sliced archive bind the identified task. Its launch receipt records
the accepted start **October 26 at 11:11 p.m. CDT**, with print error 0 and no
HMS at that startup observation.

The [study](../../README.md) describes the bare 22 AWG 4P J5 ribbon and its
proposed west-wall location. This coupon is not a production enclosure feature.
The clip prints **entry-up in its installed orientation**. The 3 mm host wall
is 24 mm wide and extends 6 mm below the hook, giving one **72 mm²** native
bed footprint. The hook grows from the wall on a 45° corbel starting at print
Z6 mm. Overall print height is 25.70 mm. The 0.75 mm retaining lip keeps its
flat underside.

- [Editable project](2026-10-26-relay-ribbon-4p-upright-mark2-78832950/2026-10-26-relay-ribbon-4p-upright-mark2-78832950.3mf)
- [Native print archive](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/future/cable-clip-exploration/prints/2026-10-26-mark2-relay-ribbon/2026-10-26-relay-ribbon-4p-upright-mark2-78832950/2026-10-26-relay-ribbon-4p-upright-mark2-78832950.gcode.3mf)
- [Native preview](2026-10-26-relay-ribbon-4p-upright-mark2-78832950/plate_1.png)
- [Physical result](physical-result.json), [photo 1](physical-photo-1.jpg) and [photo 2](physical-photo-2.jpg)
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

The photos show uneven layer bands and localized material buildup on the partial
hook. Actual part temperature, fan performance and defect-layer duration were not
measured; the heat/short-layer interpretation remains Derek’s reported explanation.
The cancelled article has no accepted cable fit or retention result. This coupon
does not integrate a production enclosure feature.
