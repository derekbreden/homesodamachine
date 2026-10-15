# Faucet bridge and cooling transfer

These matched actual-part sections test whether the PET-GF bridge and ramp
findings improve the [three confirmed faucet finish defects](../../industrial/defects/2026-10-14.html).
The customer outcome is an intact, clean mating edge and lower rim, with the
accepted upper surface finish retained. The production geometry, projects and
shared material profile are inputs to this experiment.

| Printer | Actual part section | A, left when facing the printer | B, right |
| --- | --- | --- | --- |
| Mark1 | Full-circumference tip joint, through original print Z40 mm | Production reference | Bridge/cooling treatment |
| Mark2 | Complete foot and first shoulder, through original print Z33.8 mm | Production reference | Bridge/cooling treatment |

Mark1 accepted the tip pair as **job 1340794235 at 22:32:42 CDT on
2026-10-14** and reported RUNNING without errors. Its native estimate is
1 h 03 min 07 s, 21.19 g; the local bridge slowdown adds time beyond it.
The [launch receipt](mark1/launch.json) identifies the submitted archive.

The [foot material pair](mark2/README.md) is prepared but **not selected for
submission**. The active Mark2 fin iteration is the
[single tip candidate](../2026-10-15-tip-fins/README.md), with no repeat control.
The foot pair's native estimate is 3 h 54 min 14 s, 95.84 g, before the
local Bridge slowdown. It holds Tree(auto) constant while comparing the material
recipe and retains the first shoulder for a separate defect 1 assessment.
Mark1's [Full-annulus comparison](../2026-10-14-foot-fins-current-angle/full-annulus/README.md)
compares support placement with the bridge recipe on both specimens. Mark2's
completed [stock fin walls comparison](../2026-10-14-foot-fins-current-angle/README.md)
records easy fin removal, generally uniform underside texture with sag and a
worse front edge than trees at the missing contact.

## Basis and treatment

The [v5 comparison](../../../../print-tests/petgf-fins/normal-flow-cooling-v5/mark1/physical-result.json)
prefers 125% bridge extrusion at 70% fan for closing first-layer gaps. The
[v7 completed roofs](../../../../print-tests/petgf-fins/flow-bracket-v7/mark1/physical-result.json)
also prefer 125%; increasing beyond it has no established advantage. The
[v6 matrix](../../../../print-tests/petgf-fins/finish-matrix-v6/mark2/physical-result.json)
accepts the tested 35–42.5° ramps, and its F07/F08 comparison favors 15 over
25 mm/s within that particular fin geometry. These results select a transfer
candidate; they do not establish the faucet's physical result.

A retains the production object's bridge flow and the native fan/feed commands.
B uses the native per-object `bridge_flow=1.25`, including the slicer's treatment
of overhang-wall extrusion. After the first three bed layers, B's named wall,
bridge, infill, surface and gap-infill features receive 70% part fan, and Bridge
moves are capped at 15 mm/s. The **Mark2 foot** treatment also includes Floating
vertical shell, covering every model feature in its slice. The submitted **Mark1
tip** retains native cooling and feed on Floating vertical shell and therefore
does not test an all-model fixed-fan recipe. Other model feeds, supports and brim
retain their native values.
The local treatment preserves every native XYZ, arc and E word. The editable
project contains the flow treatment; `finish.py` applies the local fan/feed
treatment to its native slice and refreshes the checksum.

The actual references receive 0–62% model fan on the foot and 22–64% on the tip
after the first three layers. Bridge feed is 25 mm/s. The
[Mark1](mark1/review.json) and [Mark2](mark2/review.json) reviews retain the
observed ranges and treatment checks. Native 125% bridge flow's perimeter
treatment is part of this physical transfer question, as identified in the
[profile review](../../../../print-tests/petgf-fins/profile-transfer-review.json).

The [wall-under-roof result](../../../../print-tests/petgf-fins/under-roof-walls-v8/README.md)
selects a 0.24 mm gap for its narrow wall. It does not establish a replacement
for the faucet's automatic tree-support gap. These material comparisons retain
Tree(auto), Default style and the saved 0.45 mm requested top gap.

## Geometry and print conditions

The source meshes match the [identified production print](../../industrial/prints/2026-10-13-complete-rear-seam-base-tip-mark2/physical-result.json).
The base remains at −15° and the tip at −105°. The cropped sections preserve
the full circumference of the affected regions, original underside and bed
contact. The source STEP supplies the cuts, tessellated at 0.012 mm; each
preparation records the input STEP/STL hashes, pose and crop.

The base retains the current Arachne wall generator, solid foot region, eight
coarse lip layers and 0.12 mm band at print Z17–29. Its second fine band lies
above the cropped section. The tip retains its ordinary 0.24 mm layers.
Both retain the selected A2/Back/150% scarf settings, wipe-off filament
treatment and rear seam enforcement. The first bed layer is 0.20 mm.

Both printers use their fixed left hardened standard-flow 0.4 mm nozzle,
PET-GF on external spool 254 and Textured PEI. Mark1 requests +0.18 mm trim
and emits `G29.1 Z0.16`; Mark2 requests +0.04 and emits `G29.1 Z0.02`.
Temperatures remain 265°C first layer, 280°C normal and 80°C bed. Timelapse
and bed leveling are On; Flow Dynamics and Nozzle Offset Calibration are Auto.
The recorded full-bead envelopes have at least 102.29 mm edge clearance for
the tip pair and 90.04 mm for the foot pair.

Cropping and two simultaneous specimens change layer return time and support
topology. A cropped foot test cannot establish the complete upper faucet's
appearance at another angle. The accepted full-faucet finish remains the
reference for any production decision.

## Physical assessment

Keep each cooled A/B pair identified before removing supports. Use fingers
first and the existing cleanup tools as needed, keeping the supports with
their specimen until the edge is inspected.

- At defect 1, compare the localized raised bead at the rear midpoint of the
  CAD Z14 shoulder. Extra extrusion could enlarge this buildup; score it
  separately from the rim finish.
- At defect 2, inspect the entire tip-side joint lip, especially the previously
  photographed worst area, for curled or bunched strands and loss of model skin.
- At defect 3, inspect the complete lower foot edge after cleanup. Check for
  scalloping, lifted strands and a variable gap against the existing mounting
  plate, without sanding the test edge first.

A useful candidate retains its model layers through cleanup, has no loose or
catching edge strands, and improves the identified defects without damaging
the adjacent finish or mating fit. If A does not reproduce the relevant
defect, a clean B does not establish a cure. Numerical gap size, load capacity
and lifetime are unmeasured. Physical observations remain pending.

## Manual reproduction

From the repository root, use `tools/cad-venv/bin/python` to run this directory's
`prepare.py Mark1` or `prepare.py Mark2`, then its `finish.py` for that printer.
Preparation refuses to overwrite a
launched experiment. The saved slice command calls the installed Bambu Studio
with arrange/orient disabled. `finish.py` packages a print-only copy with the
reviewed G-code unchanged by packaging. Open that copy without reslicing.
These tools are manual experiment tools; they add no build or commit checks.
