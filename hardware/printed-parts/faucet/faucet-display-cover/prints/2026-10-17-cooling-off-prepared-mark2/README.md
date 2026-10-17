# Sculpted display cover — part-cooling trial, prepared only

One complete current cover is ready for Mark2's right hardened 0.4 mm hotend
and white PET-GF, external spool 255. **Not submitted.** Derek will give the
instruction to start. The native estimate is **24 min 42 s, 6.64 g**, 77 layers.

The single experimental change is part cooling: minimum, maximum and overhang
fan speeds are all zero. The current cover geometry, −50° pose, 0.20/0.24 mm
layers, 265/280°C nozzle, 80°C bed, speed settings, bridge flow, automatic
Tree/Default supports and Aligned/15%/scarf-off seam remain as in the October 16
single-cover project. The production recipe is unchanged.

The [native review](native-review.json) verifies zero commanded part-fan PWM
through all 64,630 identified model extrusion moves, the right nozzle mapping,
Mark2's +0.04 mm requested/+0.02 mm emitted trim, and 131.63 mm of complete
bead clearance to the usable bed boundary. Startup nozzle cooling and other
machine fans retain their normal commands. The preview shows the complete
cover and its unchanged pose. [Packaging](packaging.json) binds the identical
G-code in the full native and ready print-only archives.

## Evidence and hypothesis

The [failure report](reported-failure.json) identifies both recent covers and
records breakage even during display loading. The September 18 white Sculpted
set is identified as `sculpted-white-z018-mark2.gcode.3mf` in the
[faucet print log](../../../faucet-shell/print-log.md#white-sculpted-faucet--2026-09-18-mark2).
The [historical acceptance](../../physical-acceptance.json) preserves its
successful cover geometry.

The [comparison](comparison.json) finds adaptive 0–70% saved cooling in the
September project and continuous 70% after three layers in both recent
archives. Nozzle temperatures and nominal layer height match. Polymaker's
[PET-GF guidance](https://wiki.polymaker.com/polymaker-products/polymaker-filaments/fiberon-tm/fiberon-tm-pet-gf15)
specifies fan off and suggests slower printing for layer-adhesion trouble.
Reduced bonding from continuous cooling is the leading hypothesis; these
breaks do not establish their fracture plane or cause.

The [September](september-geometry.json) and [current](current-geometry.json)
CAD readings retain 1.3 mm nominal walls, 3 mm lips and the same designed
preload. The neck diameter grows from 26.025 to 27 mm and the rear skirt has
an extended closure. Sampled lower wing sections differ by at most 0.014 mm;
upper sampled sections are slightly thicker. This is a local section reading,
not a stress analysis or proof that the geometry has no effect. The broader
neck and closure can affect flexing. Thickening the spring walls would also
increase stiffness, so the cooling comparison precedes a thickness change.

## Physical reading after authorization

Let the print cool, remove its supports, load the display and seat the complete
cover on the matching current Sculpted tip using the documented assembly
sequence. The normal assembly motion must produce no crack and leave the
display and cover retained. Record underside finish too: removing cooling
can affect the overhangs. This trial assesses normal assembly; it establishes
no cycle-life value. If it still fractures, identify the broken section and
layer direction before selecting a local geometry change.
