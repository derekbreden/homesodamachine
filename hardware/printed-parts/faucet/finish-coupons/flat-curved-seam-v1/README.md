# Flat and curved seam diagnostic — Mark2

Four unsupported, full-scale **7.16 mm** faucet-neck sections compare a flat
inspection face with the original curved face. The curved reference retains the
faucet neck's 27 mm outer diameter, 15-degree axis and interior passages. The flat
variant trims only the outer cap to make a **12 mm wide face**; the bores remain
unchanged, with at least **3 mm of uninterrupted backing** behind that face.

All four use the saved `petgf.3mf` process: regular aligned seam, **15% seam gap,
scarf off**, 0.20 mm first layer and 29 subsequent 0.24 mm layers, two walls and
15% grid infill. Temperature, cooling, flow, wall order, speed, retraction, wipe,
arc fitting and motion settings are shared. Central seam paint locates the join
on the inspection face without changing those process settings. There are no
reinforcement modifiers, support overrides or fine-layer bands.

Facing the printer, the front of the plate is nearest you:

| Row | Left | Right |
| --- | --- | --- |
| Back | C — curved | D — flat |
| Front | A — flat | B — curved |

[Plate map](plate-layout.png). Each seam is on the **Y+ face**, farther from you
while the specimen is on the bed. The map's arrows identify it. Keep the letter
with each specimen during removal; letters are not embossed on the pieces.
The two copies of each shape occupy swapped positions in a compact 2 × 2 layout.

Native estimate: **20 min 51 s**, **7.96 g** at the saved profile density.
Mark2's target is external PET-GF in the left hardened standard-flow **0.4 mm**
nozzle on **Textured PEI**, with its ordinary +0.04 mm requested/+0.02 mm emitted
Z trim. Startup and calibration can change actual elapsed time.

The [native review](native-check.json) verifies all four meshes and settings,
30 layers per piece, no supports or scarf ramps, first/second-layer wall contact,
the 0.06 mm commanded seam gap, and **127.39 mm** of complete-bead edge clearance.
Across every layer, the flat seams stay within **0.08 mm** of face center and the
curved seams within **0.14 mm**; both flat seams have over 5.9 mm of corner
clearance. The [editable project](2026-10-12-flat-curved-seams-petgf-left04-z004-mark2.3mf)
and [native slice](https://github.com/derekbreden/homesodamachine/blob/33d50d2ecd2a0fb6b518483a44c8031e3a0c1617/hardware/printed-parts/faucet/finish-coupons/flat-curved-seam-v1/2026-10-12-flat-curved-seams-petgf-left04-z004-mark2.gcode.3mf)
are prepared locally. No import or Send has occurred.

Inspect the arrowed face under several lighting directions and across its
surface. Compare a lateral step, raised/recessed material and a texture-only line,
then check whether the second copy repeats the observation. A difference confined
to the curved specimens would implicate curvature in the visible effect; it
would not by itself identify a firmware or extrusion mechanism. The changed
contour slightly changes per-object extrusion duration, and these short sections
do not reproduce the complete faucet's thermal history. Physical seam shape is
unassessed.
