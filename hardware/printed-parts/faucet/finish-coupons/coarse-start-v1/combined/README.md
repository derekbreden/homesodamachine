# Combined faucet lift and seam-gap comparison — Mark2

This nineteen-object plate is authorized by Derek's bed-clear request to run
all five lift variations and at least five seam variations together. The
[placement map](plate-layout.png) identifies every specimen, facing the printer
with the front at the bottom. Letters identify positions; keep them with the
specimens during removal. Geometry has no added labels.

**A–E** are the [five coarse-start cases](../README.md). The left column from
front to back is **B (1), A (control), C (2)**; the next column is **D (4), E (8)**.
The numbers count 0.24 mm layers at the last-starting part of the retained lip
before switching to 0.12 mm. Read the linked counting rule and native rounded
support-gap limitation when scoring the remaining underside.

**SA–SN** are the [fourteen seam-gap swatches](../../seam-gap-swatches-v1/README.md).
They test regular gaps 0/5/10/15% and scarf slope gaps 0/2.5/5/10/15/20/25/30%,
with duplicate regular-15% and scarf-zero controls. Scarf length stays 10 mm.

| Seam row | Left | Middle-left | Middle-right | Right |
| --- | --- | --- | --- | --- |
| Front | SA regular 15% | SB scarf 10% | SC regular 5% | SD scarf 25% |
| 2 | SE scarf 0% | SF regular 0% | SG scarf 5% | SH scarf 20% |
| 3 | SI scarf 30% | SJ scarf 2.5% | SK regular 10% | SL scarf 15% |
| Back | SM regular 15% | Empty | Empty | SN scarf 0% |

The native estimate is **6 h 48 min 9 s**, versus **3 h 10 min 18 s** for the
separate lift plate and **3 h 42 min 57 s** for the separate seam plate.
The complete model/support/brim deposition envelope has **51.2 mm minimum
edge clearance**, above Derek's 40 mm inset. All use the same frozen shipping
global settings, and this combined slice has no warnings. Nineteen simultaneous
objects alter thermal exposure and layer return time; these are comparative
screens and do not establish a full-faucet result.

[Native review](native-check.json) verifies geometry, coarse counts, fine bands,
first/second-bed-layer bead overlap, the lip support witnesses, actual seam
material commands, and Mark2 +0.04 mm requested / +0.02 mm emitted trim.
PET-GF uses external left slot 254 and fixed left hardened standard-flow 0.4 mm
on Textured PEI. Timelapse and leveling are on; nozzle clump probing is off.

[Launch plan](launch-plan.json), [preflight](preflight.json) and [receipt](launch.json)
record the accepted start. An interrupted pre-import navigation issued no Send;
Derek authorized a retry, which issued the one successful Send. Neither separate plate is authorized to
start. There is no scheduled monitor or automatic resume.

Mark2 accepted task **1328441515** at **1:41:41 AM CDT, October 11**.
The native forecast is **8:29 AM CDT, October 11**.

Derek selected **SB (scarf slope gap 10%)** and **E (eight coarse lip layers)**
for the next complete faucet. The [physical result](physical-result.json) records
recovery in the latter four layers of E and difficulty distinguishing the seam
swatches. The attached crops identify the choices; they do not show full surfaces.
The [complete-faucet trial](../../../industrial/prints/2026-10-11-scarf10-lift8-mark1/README.md)
retains these provisional choices for confirmation on the actual curved parts.
