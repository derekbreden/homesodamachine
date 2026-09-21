# Full enclosure print readiness

The requested trial uses **all four fresh shell quadrants, the complete carrier pair,
one reusable spring-loading pusher, and both matching G Ganen cold-core mounting parts**.
H2C is printing the complete Kamoer cartridge and raised open cap. Mark2 is printing the
countertop under the **Tube miter box** task. No additional coupons or scans are required
before this full assembly trial.

**The complete current assembly passes all active native gates.** Its scorecard has
105 checks: 104 pass and one inactive physical gas-fit goal remains a warning. There are
zero clashes or unanswered overlaps, 67/67 clear port leads, and no pair below the required
clearance. The carrier passes 638 native solid/sweep checks. The actual canonical 2 mm
pusher separately passes 38 checks and 19 continuous sweeps against matching current inputs.

The verified assembly STEP SHA-256 is
`0bf745015625bde33b3672941b49fe7acb1cbbfcdbc652e2b2dc55959f883a67`.
The [readiness record](print-readiness.json) binds the scorecard, Box, sources and focused
pusher evidence. The seven fresh workflows still need the exact print receipt, staging,
native slicing and support reviews; none is submitted. The
[queue](tee-readiness/full-enclosure-print/queue.json) tracks those stages separately.

## Complete parts and printer plan

| Plate | Assigned printer | Print orientation | Current state |
| --- | --- | --- | --- |
| Front-top and one 2 mm spring pusher | H2C | Shell +Z up, Z90; pusher flat | Awaiting final receipt and fresh slice review |
| Front-bottom | Mark2 | +Z up | Awaiting final receipt and fresh slice review |
| Back-bottom | Mark2 | +Z up | Awaiting final receipt and fresh slice review |
| Back-top | H2C | X180, ceiling down | Awaiting final receipt and fresh slice review |
| Complete left and right carrier halves | Mark2 | +Z up, Z90 | Awaiting final receipt and fresh slice review |
| G Ganen foam-cap-top | H2C | +Z up, flat underside on bed | Awaiting final receipt and fresh slice review |
| Matching foam-cap-lid-top | H2C | +Z up, flat underside on bed | Awaiting final receipt and fresh slice review |

The exact running H2C job is `pump-cartridge-cap-black-z018-h2c-v1.gcode.3mf`, archive
SHA-256 `8dc3f3dcb4e55020b5e8235a03ac9cbb3eec256484ef2fdd8b6cafad4fe3c562`.
Its [launch record](tee-readiness/full-enclosure-print/h2c-pump-cartridge-cap-launch.json)
records the selected printer, material mapping, archive and observed start.
The latest recorded observations are:

| Printer | Observed at (UTC) | Progress | Reported layer | Estimated minutes left | Errors |
| --- | --- | ---: | ---: | ---: | --- |
| H2C | 2026-09-21T13:43:23.192158+00:00 | 58% | 203/496 | 255 | None |
| Mark2 | 2026-09-21T13:43:24.036245+00:00 | 37% | 46/917 | 611 | None |

These are timestamped printer readings, not live remaining-time promises. Both jobs
were running; Mark2 remains owned by Tube miter box.
The running cartridge has 260 exterior divisions; the new shell uses 262, a pitch
difference of 0.006324 mm per groove. A small exterior groove-phase difference is possible.
Native fitted cartridge/cap geometry is unchanged and the cap is unfluted; this cosmetic
note does not require stopping or reprinting the running job.

New jobs inherit the saved [PET-GF profile](../petgf.3mf): black PET-GF on the fixed left
0.4 mm nozzle, whole-layer printing and `auto_brim`. H2C uses +0.18 mm requested trim
(+0.16 mm emitted for Textured PEI); Mark2 uses +0.04 mm (+0.02 mm emitted).
Both configured printable areas are 325 × 320 mm, with at least 15 mm model border.
Each actual slice reports its emitted brim and support paths. Every support contact needs
an accessible removal lane before hardware installation, following the
[support-removal strategy](enclosure/README.md#support-removal-strategy).

Derek's operating rule is to keep productive jobs running while checks proceed, or cancel
a concretely defective job and switch to useful work. Do not pause a print for design
analysis or hold an idle machine merely for an agent review. Printer handoff uses the exact
reviewed archive after the assigned machine is available and its plate is cleared.

## Accepted physical evidence

| Part or interface | Established result and current use |
| --- | --- |
| Kamoer cartridge and cap | Derek confirms both pumps are firmly held with screws tightened and no vertical play. The current cap keeps the broad fitted contact geometry; its surrounding crown reaches the cartridge top while motor ends and spade-terminal wells remain open. The raised crown and four-tube operation are checked in the full trial. [Physical record](../../reference/kamoer-kphm400/physical-fit.json). |
| Beduan sockets | The production-profile socket fit is easy and accepted, with some retention during loose inverted shaking. Preserve the Ø7.2 sockets and use zip ties for positive retention. Installed tie access remains a full-assembly observation. [Physical record](../fixtures/valve-socket-fit/physical-acceptance.json). |
| Faucet lever | The flat-sided lever with the 9 mm cylinder channel has accepted fit and function. Reuse it. [Physical record](../faucet/lever-replica/physical-acceptance.json). |
| Faucet display cover | Its broad, substantial flexing walls and retaining lips work in PET-GF. This is Derek's accepted simple snap-fit example; the new carrier still needs its own physical evaluation. [Physical record](../faucet/faucet-display-cover/physical-acceptance.json). |
| Machine display cover | Derek confirms the existing cover was already test fit. Reuse that cover; its shell interface belongs in the final generated assembly checks. |
| Nameplate | Appearance, QR readability and snap fit are accepted. Reuse the print. Its complexity is not the preferred design example. [Physical record](nameplate/physical-acceptance.json). |
| C14 inlet and cord | Derek accepts the printed inlet/C13-cord station. Its fitted pocket and screw stations are preserved; the reference uses the measured flange outline and R6 corners. [Native interface evidence](tee-readiness/full-enclosure-print/hard-contact-review/README.md). |
| G Ganen feet and flow | Derek identifies flexible rubber feet that slide fore/aft independently and can be removed. Captured scan positions are not a fixed bolt pattern. Discharge is enclosure −X, corresponding to reference +Y at +90° yaw. Actual screw passage, washer seating and loaded rubber behavior remain assembly observations. [Sample authority](../../reference/g-ganen-pump/scan-evidence.json). |

## Tee, carrier and springs

The registered tee envelope uses a conservative Ø16.5 fixed collar and Ø17.0 journal,
leaving 0.25 mm radial running air. Derek's run span is 42.5 mm extended / 39.2 mm pressed,
with 1.65 mm travel per run end. The branch measures **30.5 mm extended / 29.0 mm pressed**,
with **1.5 mm travel**; only the small outermost ring moves. The branch face stations
22.35 / 20.85 mm use the nominal Ø16.3 back-collar datum. The conservative clearance
envelope is a separate dimension. [Measurements](../../reference/jg-pp0208e-tee/branch-operating-measurements.json).

The Ø8.5 circular release aperture retains annular bearing against the observed terminal
face. The [terminal-bearing review](../../reference/jg-pp0208e-tee/terminal-bearing-review.json)
supports the full trial without another ring scan or caliper reading. Simultaneous contact,
release and relocking of all four actual rings remain physical checks.

The carrier has **two moving halves with an integral broad retaining wall**, a fore lap,
a captured rail and an overlapping shelf. It uses no joint screws, heat-set inserts or
separate keeper. The fixed spring cups belong to front-top; the moving cups have closed
sides. One flat 2 mm pusher loads the two springs in turn and is removed before operation.

Derek measures the stiffer springs at **27 mm free length, about 7 mm compressed length
(possibly slightly less), and Ø6 mm**. The present bearing separations are:

| State | Carrier offset | Spring length | Compression from 27 mm |
| --- | ---: | ---: | ---: |
| Release | 0 mm | 19.35 mm | 7.65 mm |
| Connected | 2 mm | 21.35 mm | 5.65 mm |
| Aft stop | 4.5 mm | 23.85 mm | 3.15 mm |

The 6.57 mm cup bores provide nominal 0.285 mm radial air. Fixed cups are 8 mm deep with
2 mm radial walls; moving cups are 11.1 mm deep. The design does not need a spring-ID
measurement or an added guide pin. Geometric capture and retained stock do not establish
helical-spring escape resistance, operating force or printed stiffness. **Improved physical
rigidity over the carrier before the springs moved has not yet been demonstrated.**

## What remains before and during the trial

Bind the verified source, native solids, meshes, profile and current carrier/pusher
proofs in the fresh print receipt. For each plate, review its actual native slice, emitted
working features and every support-contact removal lane before printer handoff. Earlier
receipts and support approvals do not qualify new geometry or archives.

The complete printed assembly establishes spring retention at both ends through every
stop and unequal-hand motion; tension, feel, sideways deflection and full-span rigidity;
valve tie installation; four-tube insertion, capture, release and relocking; pump mounting,
connectors and primed operation; and shell closure. G Ganen screw/washer seating and rubber
compression, DIGITEN arrow orientation, and actual made-up gas-fitting fit are direct
assembly observations. They do not require another scan or a separate coupon before the
requested trial. Production LLDPE routes retain nominal ¼-inch and ⅜-inch outside diameters.

Physical spring behavior and complete enclosure fit are **outcomes of this trial**, not
prerequisites to printing it. No whole-carrier functional rigidity, retention force or
cycle-life result is claimed.

The immutable [front-top cancellation](tee-readiness/full-enclosure-print/h2c-front-top-cancellation.json),
[launch](tee-readiness/full-enclosure-print/h2c-front-top-launch.json) and
[print-job records](enclosure/print-jobs.json) remain available for the affected archived
jobs. Their geometry and slice approvals are not active entries in the current queue.
