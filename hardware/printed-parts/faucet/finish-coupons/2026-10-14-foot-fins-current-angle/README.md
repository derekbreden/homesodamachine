# Stock fin walls at the production faucet angle

This actual-part comparison tests the complete plate-mating rim, defect 3 in
the [confirmed faucet defect visualization](../../industrial/defects/2026-10-14.html).
The customer outcome is a clean, intact rim after support removal, with the
accepted upper finish recipe retained.

The [Full-mode comparison](full-annulus/README.md) applies the bridge
recipe to both support conditions and adds annulus-specific contact placement.
Its [layout and measured front strand](support-layout-review.png) retain the
accepted angle. [Mark1 accepted job 1340913124](full-annulus/mark1/README.md)
at 23:53:32 CDT on 2026-10-14 with its own +0.18 mm trim.

Both sections preserve the production **−15° X rotation**, original underside
and original bed contact. They end at original print Z16.76, below the first
0.12 mm fine band. No production angle, model, project or shared profile is changed.

| Facing Mark2 | Condition |
| --- | --- |
| A, left | Eight stock fin walls under the bottom annulus; automatic supports elsewhere |
| B, right | Production Tree(auto), Default, including its automatic normal sections |

Mark2 accepted **job 1340828943 at 22:55:45 CDT on 2026-10-14** and reported
RUNNING without errors. The [launch receipt](stock-vs-tree/mark2/launch.json)
identifies the stock-fin comparison. The native estimate is
**1 h 49 min 16 s**, **45.95 g**, **70 layers**.
The [editable project and native slice](stock-vs-tree/mark2/) retain the exact
inputs. Physical results remain pending.

## Supports and evidence

The unmodified [Support Fins engine](https://github.com/gittrahan/support-fins/tree/511d81fc9124075cef142bfb2766bd5e8bfa777d)
generates eight underlying walls at −15°. The
[engine record](stock-engine.json) preserves their geometry and options.
These are fin walls without horizontal gripping teeth. The source tool's
roughly 20° shallow-face cutoff naturally omits those teeth on this 15° face.
No cutoff override is used in this print.

A uses 1.0 mm walls, 0.6 mm contact tips, a 0.24 mm requested vertical gap,
12 mm maximum requested span and 0.6 mm free-edge inset. Bed pad and sway
braces are off. The [PET-GF v8 G1 result](../../../../print-tests/petgf-fins/under-roof-walls-v8/README.md)
selects that gap as a candidate for an underlying 1 mm wall: it supported well
and bent off easily on its coupon. The sloped faucet face and native production
cooling differ; faucet finish and removal remain physical questions.

The explicit local support choice serves A's **bottom annulus only**, addressing
the observed circumferential scalloping and lifted strands. Support-block paint
covers that 1,641.24 mm² plane and the added support surfaces to avoid duplicate
or recursive slicer supports. Tree(auto)/Default remains enabled elsewhere.
B has no support-block paint or designed-in supports, retaining the production
automatic decisions and requested 0.45 mm top gap. A's 0.24 mm gap does not
select a replacement gap for automatic tree supports.

The [native bead review](stock-vs-tree/mark2/review.json) confirms support
deposition in both conditions, the intended model-face paint scope and at least
**89.94 mm** bed-edge clearance for all emitted model, support and brim beads,
including arc paths. A nominal gap does not ensure a uniform empty deposited
course or establish physical release. The [print-only packaging record](stock-vs-tree/mark2/packaging.json)
binds the native G-code to the submitted archive without G-code edits.

The [three selected-path review](stock-vs-tree/mark2/rim-path-review.json) and
[whole-annulus review](stock-vs-tree/mark2/annulus-review.json) measure deposited
bearings and chronological neighbouring beads. At the lever-facing midpoint,
the 7.867 mm strand has no lower bearing in its preceding three courses. The
saved engine span target alone does not establish support for the native paths.

## Preserved print recipe

Both sections retain production Arachne walls, solid foot modifier, rear seam,
scarf settings, bridge flow 1.0, native model cooling and native feeds. The first
bed layer is 0.20 mm and subsequent courses are 0.24 mm. The cut is below the
original fine bands. This coupon does not requalify the complete upper finish.

Mark2 uses black PET-GF on external spool 254, the fixed left hardened
standard-flow 0.4 mm nozzle, Textured PEI and its +0.04 mm requested trim
(`G29.1 Z0.02`). Temperatures are 265°C first layer, 280°C normal and 80°C bed.
Timelapse and bed leveling are On; Flow Dynamics and Nozzle Offset Calibration
are Auto. Mark1's independent [tip material comparison](../2026-10-14-bridge-transfer/README.md)
started more than three minutes before this Mark2 submission.

## Physical assessment

Keep A and B identified before support removal. After cooling, use fingers
first and the existing cleanup tools if needed. Inspect the whole rim,
including the photographed worst area, without sanding it first.

Compare removal effort, retained model skin, contact marks, loose strands and
rim scalloping. Check the edge against the existing mounting plate. A useful
candidate improves edge shape, has no loose or catching strands, and removes
without tearing the rim or impairing mating fit. If B does not reproduce the
defect, a clean A does not establish a cure. Physical observations are pending.

This crop isolates defect 3. The localized shoulder buildup at defect 1 and
the tip lip at defect 2 remain separate observations. The
[optional gripping-tooth source experiment](grip-option.md) records a local
cutoff override and its native limitations; it has no accepted printer job and
is not the stock fin-wall comparison.

## Manual reproduction

From the repository root, run this directory's `prepare.py stock` using
`tools/cad-venv/bin/python`, then `review.py stock` with the same runtime.
Preparation expects the recorded upstream pin at `.cache/support-fins-faucet`.
The scripts preserve the native slice, package a print-only copy, and refuse
to overwrite a launched plate. They are manual experiment tools, with no build
or commit checks. The separate `grip` mode prepares the optional tooth comparison.
