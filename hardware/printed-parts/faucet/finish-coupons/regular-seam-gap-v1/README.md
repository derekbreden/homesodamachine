# Ordinary seam-gap comparison — PET-GF defaults, Mark2

Seven identical, unscaled 18.2 mm faucet-neck sections test **ordinary Seam gap
only**, with one **E / 15% control**. Scarf is disabled by the inherited
`petgf.3mf` process and filament settings. There are no scarf overrides or
fine-layer bands. The control has no object process overrides; each other
specimen overrides only `seam_gap`.

| Row, facing the printer | Left | Center | Right |
| --- | --- | --- | --- |
| Back | Empty | G 30% | Empty |
| Middle | D 25% | **E 15% control** | F 5% |
| Front | A 0% | B 20% | C 10% |

The [native bead map](plate-layout.png) identifies positions. Keep the letters
with the specimens during removal; the geometry has no added label features.
The gap is a percentage of the 0.4 mm nozzle diameter: 0/5/10/15/20/25/30%
correspond to nominal closure interruptions of 0/0.02/0.04/0.06/0.08/0.10/0.12 mm.

All use the actual saved [PET-GF defaults](../../../petgf.3mf): aligned seams,
0.20 mm first bed layer, 0.24 mm model layers, Classic walls, two wall loops,
15% grid, saved temperatures, cooling, flow, retraction and automatic
Tree(auto)/Default support decisions. Native slicing generated no support
paths for these sections. Probing clump detection is disabled. The only global
configuration changes identify Mark2's normal +0.04 mm requested/+0.02 mm
emitted trim and its loaded black `#161616` external PET-GF spool colour.
The left fixed hardened standard-flow 0.4 mm uses external slot 254,
PET-CF/GFT01, on Textured PEI. Timelapse and bed leveling are On; flow dynamic
and nozzle-offset calibration are Auto.

The [manual native check](native-check.json) verifies the exact source geometry,
one-factor settings, normal layers, zero scarf ramps, first/second-layer bead
contact and actual closure-gap witnesses at three heights. Complete deposited
model/brim paths have **104.4 mm minimum edge clearance**. The plate stays
compact and centered. The seven specimens share one machine and thermal cycle
so printer/nozzle/trim differences do not enter the comparison. Mark2 had the
longer known idle period while loaded with suitable PET-GF.

Native estimate: **57 min 28 s**, **29.95 g** at the saved profile density,
plus startup and any pauses. [Plan](launch-plan.json), [preflight](preflight.json)
and [launch receipt](launch.json) record the exact attempt and acceptance.
Preparation and native review are snapshots; the launch receipt supplies the
current submission state. No automatic resume or scheduled monitor is requested.
Mark2 accepted exact task/job **1330991481** at **6:42:18 pm CDT on October 11**.
The native forecast from observed acceptance is **7:39:46 pm CDT**, plus any
additional calibration or pauses. The initial retained layer counter in PREPARE
is not evidence of model progress.

Use raking light and a fingernail to compare ridge, groove, an exposed gap and
damage beside the seam. Record each observation in [results](results.json).
Short sections and seven simultaneous objects change thermal/return-time
conditions from a complete faucet. There is no physical winner yet and no
change to the complete-faucet recipe from this comparison.
