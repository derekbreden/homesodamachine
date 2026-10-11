# Faucet seam-gap swatches

Fourteen identical full-scale neck sections screen local seam closure and
scarf overlap, targeting a flat exterior. Derek reports a groove on the earlier
regular-seam D and visually identical ridges on 10 mm scarf E and 20 mm scarf F,
at both 0.08 and 0.24 mm. Those [physical results](../2026-10-10/physical-result/physical-result.json)
are qualitative; no ridge or groove dimension is recorded.

Regular seam gap is tested at 0, 5, 10 and 15%. Scarf slope gap is tested at
0, 2.5, 5, 10, 15, 20, 25 and 30%, with length fixed at 10 mm and start height
10% of the layer. These gaps are percentages of the **0.4 mm nozzle diameter**,
not flow percentages: 15% is 0.06 mm, 30% is 0.12 mm.
[Bambu's definitions](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/PrintConfig.cpp#L4591)
and [path generation](https://github.com/bambulab/BambuStudio/blob/v02.08.02.61/src/libslic3r/GCode.cpp#L6211)
identify regular end clipping and scarf overlap clipping. All scarf specimens
retain a fixed regular seam gap of 15%. The native moving outer-wall E totals
confirm more closure with smaller regular gaps and less deposition with larger
scarf gaps; this does not predict physical seam height.

| Row, facing printer | Left | Middle-left | Middle-right | Right |
| --- | --- | --- | --- | --- |
| 1, front | A regular 15% | B scarf 10% | C regular 5% | D scarf 25% |
| 2 | E scarf 0% | F regular 0% | G scarf 5% | H scarf 20% |
| 3 | I scarf 30% | J scarf 2.5% | K regular 10% | L scarf 15% |
| 4, back | M regular 15% | Empty | Empty | N scarf 0% |

A/M repeat the regular control; E/N repeat the zero-gap scarf control. They
supply a position check. Geometry carries no embossed labels: preserve location
letters during removal. The combined plate prefixes these IDs with **S**.

Frozen accepted neck geometry is cut at parent print Z82.00–100.20 mm in the
original −15° pose. The horizontal cut seats each 18.2 mm specimen on the bed.
The fine band is 0.08 mm at local Z4.04–16.04; coarse bands are 0.24 mm above a
0.20 mm first bed layer. Native automatic supports are unnecessary for these
necks, with Tree(auto)/Default retained and no blockers. Short sections and
plate companions change return time and heat exposure relative to the faucet.

Globals retain the shipping PET-GF/left-0.4/Textured-PEI Mark2 recipe, +0.04 mm
requested trim (+0.02 emitted), temperatures, cooling, flow, retraction and
pressure advance. Classic walls and a back-positioned seam are scoped to the
neck comparison, matching the prior D/E/F comparison. Smart scarf at 155°,
10 steps, inner-wall scarf and partial-loop mode are fixed. Clump probing is off.

Judge coarse and fine seam bands separately under raking light and by touch.
Prefer a flat seam with no open gap or adjacent wall damage, then confirm the
candidate on a complete faucet. A coupon result does not change the shipping
recipe. [Results](results.json) record the provisional scarf-10% choice; differences
between scarf swatches were difficult to distinguish, and no measured winner is established.

This separate plate is prepared only: **3 h 42 min 57 s**, **85.7 mm** minimum
full-bead edge clearance. The [combined plate](../coarse-start-v1/combined/README.md)
is the only plate authorized to start. [Native review](native-check.json) and
[study plan](study-plan.json) preserve hashes, local settings and emitted ramps.
Generate with `tools/cad-venv/bin/python prepare.py`; manually inspect the slice
with `tools/cad-venv/bin/python ../coarse-start-v1/review.py --seam-only`.
