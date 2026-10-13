# Complete Industrial faucet, A2 with Back — Mark2, 2026-10-13

The selected printing recipe uses **Back** on the base, shared tip and above-counter
mounting plate. Those three retain A2: 60 mm scarf length, 0% scarf gap and 150%
ordinary seam gap, smart application at 155°, 10% start height, ten steps, inner-wall
scarf and partial-loop mode. The cover and lever retain petgf.3mf corner settings:
**Aligned, 15% gap and scarf off**. Wipe is off.

The saved [project](../../faucet-industrial-petgf.3mf),
[selection](../../finish-selection.json) and [preparer](../../prepare_print_project.py)
carry this per-part recipe. The source geometry, placements, eight 0.24 mm lip
layers before 0.12 mm, and infill-only foot match task 1334704608.

Mark2 accepted task **1335906696** after one Send click. Timelapse and leveling are
on; flow and nozzle calibration are automatic. Left external PET-GF uses the fixed
0.4 mm hotend and Textured PEI, with Mark2's +0.04/+0.02 mm trim. The preceding
Mark1 acceptance and startup interval are in [launch.json](launch.json).

Native estimate: **6 h 5 min 55 s**, **161.06 g** at the saved density.
[Native review](native-review.json) binds effective settings, source hashes, eight
coarse layers and **45.10 mm** minimum full-bead bed clearance. The
[seam-path reading](seam-path-review.json) finds scarf ramps on the selected three
parts and none on the cover or lever. Cover starts are at 90° corners; lever starts
are at channel/ledge transitions, including one rounded transition. Physical
inspection is recorded in [physical-result.json](physical-result.json): Derek
calls this the best faucet print so far and reports everything checking out well,
apart from the base gooseneck's rear seam wobble. Tag
`faucet-industrial-approved-2026-10-13` identifies this physical reference.
The shipping reference retains its own scope.
