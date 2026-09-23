# Full enclosure print readiness

The requested trial uses **all four fresh shell quadrants and both matching G Ganen
cold-core mounting parts**. The Kamoer cartridge and raised open cap, front-top and
front-bottom are finished and removed. H2C is printing back-top. Mark2 has finished
the **34 mm-skirt display cover that matches the printed front-top**; its removal
is unconfirmed. **Front-top v8 is held at Derek's direction.** The next Mark2 job
choice is pending in “Scan results 2”; no next job is selected in the handoff.

**G Ganen feet and mounts are corrected.** Four copies of the shared 7 mm foot sit at the fully engaged rail ends, 58 mm apart. Matching cap and lid archives are freshly reviewed. The pump is 1 mm forward to clear the rear fitting.

**The frozen production qualification binds the geometry recorded below.** Its assembly
scorecard has 105 checks: 104 pass and one inactive physical gas-fit goal warning. There
are zero clashes or unanswered overlaps, 67/67 clear port leads, and no pair below its
required clearance.

The qualified assembly STEP SHA-256 is
`c86f83b78edabb1726847b9dcf3cc179514335109bbc56f4f46c54e1d00ef28a`.
The [geometry receipt](tee-readiness/full-enclosure-print/qualified-production/g-ganen-feet-v1/current-geometry.json) binds those production inputs and corrected mounts. Back-top has zero native added/removed volume; its mesh differs only by at most 0.000016 mm. The two mounting archives use their [mount input receipt](tee-readiness/full-enclosure-print/qualified-production/g-ganen-mount-inputs-v1/current-geometry.json). Archive and support-review provenance remains intact. These results qualify the recorded inputs, not every revision of the working assembly. The [queue](tee-readiness/full-enclosure-print/queue.json) records current eligibility and the front-top v8 hold.

**The six original production plates have completed native/support review.**
Back-bottom and the two G Ganen mounts remain unsubmitted. The two display-cover
plates are finished; v4 matches the printed front-top, and v3 belongs to the held
replacement front-top. Full-enclosure printing is already authorized; an offline-ready job
awaits machine availability, removal of
that machine’s latest print, the correct material mapping and the normal verified
handoff. `print_released=false` and `submitted=false`
record execution, not a request for another approval.

## Complete parts and printer queue

| Plate | Printer | Native time estimate | PET-GF at 1.43 g/cm³ (g) | Current state |
| --- | --- | ---: | ---: | --- |
| Front-top | H2C | 24 h 18 min | 903.02 | Finished and removed; replacement v8 held |
| Front-bottom | Mark2 | 17 h 27 min | 621.26 | Finished and removed |
| Back-bottom | Mark2 | 17 h 59 min | 709.45 | Offline ready; not submitted |
| Back-top | H2C | 27 h 51 min | 962.13 | Running; 813 layers |
| G Ganen foam-cap-top | Mark2 | 5 h 09 min | 182.63 | Offline ready; not submitted |
| Matching foam-cap-lid-top | Mark2 | 4 h 28 min | 202.92 | Offline ready; not submitted |

H2C has **back-top running** and no further assigned plate. Mark2's **display-cover
v4 is finished at 142/142 layers**, with no reported error; fresh removal confirmation
has been requested. The remaining reviewed Mark2 plates are back-bottom, foam-cap-top
and foam-cap-lid-top. “Scan results 2” has asked Derek which should follow the cover.
Front-top v8 remains held and must not be substituted as the next job.

Both G Ganen mounting plates are assigned to **Mark2**, after the bottoms.
The reviewed Mark2 v2 mounting archives use +0.04 mm requested trim and belong to the
reviewed production set. Earlier H2C variants have superseded mounting geometry and
are ineligible for submission.

| Original six-plate lane | Slicer time | PET-GF estimate |
| --- | ---: | ---: |
| H2C | 52 h 09 min | 1865.15 g |
| Mark2 | 45 h 03 min | 1716.27 g |

The original six jobs total 97 h 11 min of printer time and 3581.42 g PET-GF.
These totals describe all six production plates, including the full original estimate
for front-top. They exclude replacement revisions, display covers, cartridge/cap, the countertop, plate changes,
support cleanup and assembly; they are not remaining-time promises.

Derek directs using every spool fully and reloading during a print as needed.
**Remaining filament quantity is not a launch condition.** The mass figures are
consumption estimates; no weighing, remaining-quantity estimate or confirmation is
required. Ready jobs use the correct black PET-GF mapping and proceed after a fresh
plate-clear confirmation. Request filament only for an actual reload.
The [filament-use policy](tee-readiness/full-enclosure-print/filament-use-policy.json)
records this standing instruction.

The completed H2C job is `pump-cartridge-cap-black-z018-h2c-v1.gcode.3mf`, archive
SHA-256 `8dc3f3dcb4e55020b5e8235a03ac9cbb3eec256484ef2fdd8b6cafad4fe3c562`.
Its [launch record](tee-readiness/full-enclosure-print/h2c-pump-cartridge-cap-launch.json)
records the selected printer, material mapping, archive and observed start. The
[completion record](tee-readiness/full-enclosure-print/h2c-pump-cartridge-cap-completion.json)
binds the same archive to the printer’s FINISH report at 496/496 layers, with no error.
The exact finish time and physical print quality are not established by this reading.

| Printer | Observed at (UTC) | Progress | Reported layer | Estimated minutes left | Errors |
| --- | --- | ---: | ---: | ---: | --- |
| H2C — back-top v2 | 2026-09-23T01:11:47.553419+00:00 | 21% | 66/813 | 1308 | None |
| Mark2 — display-cover v4 | 2026-09-23T01:11:47.350974+00:00 | 100% / FINISH | 142/142 | 0 | None |

These are timestamped readings, not live remaining-time promises. The
[front-top launch record](tee-readiness/full-enclosure-print/h2c-front-top-v4-launch.json)
binds the reviewed archive to H2C’s RUNNING report and verified send settings. The
[countertop completion and handoff](tee-readiness/full-enclosure-print/mark2-countertop-completion.json)
records the countertop’s FINISH reading and Derek’s plate-clear confirmation. The
[front-bottom completion](tee-readiness/full-enclosure-print/mark2-front-bottom-v2-completion.json)
and [front-top completion](tee-readiness/full-enclosure-print/h2c-front-top-v4-completion.json)
record their finishes and removal. The [back-top launch](tee-readiness/full-enclosure-print/h2c-back-top-v2-launch.json)
binds H2C's running archive. The [matching display-cover completion](tee-readiness/full-enclosure-print/mark2-display-cover-v4-completion.json)
records its finish without claiming removal or physical fit. The active
`finish-the-enclosure-print-queue` heartbeat checks every two hours and advances
reviewed jobs when normal physical handoff conditions are met, remaining quiet on
unchanged running states.

The completed cartridge has 260 exterior divisions; the new shell uses 262, a pitch
difference of 0.006324 mm per groove. A small exterior groove-phase difference is possible.
Native fitted cartridge/cap geometry is unchanged and the cap is unfluted; this cosmetic
note does not require reprinting the completed job.

New jobs inherit the saved [PET-GF profile](../petgf.3mf): black PET-GF on the fixed left
0.4 mm nozzle, whole-layer printing and `auto_brim`. H2C uses +0.18 mm requested trim
(+0.16 mm emitted for Textured PEI); Mark2 uses +0.04 mm (+0.02 mm emitted).
Both configured printable areas are 325 × 320 mm, with at least 15 mm model border.
Each actual slice reports emitted brim and support paths. Every support contact needs
an accessible removal lane before hardware installation, following the
[support-removal strategy](enclosure/README.md#support-removal-strategy). Physical cleanup
effort remains unmeasured; narrow support strips may require fragmentation.

Derek's operating rule is to keep productive jobs running while checks proceed, or cancel
a concretely defective job and switch to useful work. Do not pause a print for design
analysis or hold an idle machine merely for an agent review. Printer handoff uses the exact
reviewed archive after its assigned machine is available and its latest plate is cleared.

## Accepted physical evidence

| Part or interface | Established result and current use |
| --- | --- |
| Kamoer cartridge and cap | Derek confirms both pumps are firmly held with screws tightened and no vertical play. The current cap keeps the broad fitted contact geometry; its surrounding crown reaches the cartridge top while motor ends and spade-terminal wells remain open. The raised crown and four-tube operation are checked in the full trial. [Physical record](../../reference/kamoer-kphm400/physical-fit.json). |
| Beduan sockets | The production-profile socket fit is easy and accepted, with some retention during loose inverted shaking. Preserve the Ø7.2 sockets and use zip ties for positive retention. Installed tie access remains a full-assembly observation. [Physical record](../fixtures/valve-socket-fit/physical-acceptance.json). |
| Faucet lever | The flat-sided lever with the 9 mm cylinder channel has accepted fit and function. Reuse it. [Physical record](../faucet/lever-replica/physical-acceptance.json). |
| Faucet display cover | Its broad, substantial flexing walls and retaining lips work in PET-GF. This is Derek's accepted simple snap-fit example. [Physical record](../faucet/faucet-display-cover/physical-acceptance.json). |
| Machine display cover | Display-cover v4 is the 34 mm-skirt cover matched to the printed front-top, printed face down. Its print is finished; removal and physical fit are unconfirmed. The short-skirt v3 cover belongs to the held replacement front-top. |
| Nameplate | Appearance, QR readability and snap fit are accepted. Reuse the print. Its complexity is not the preferred design example. [Physical record](nameplate/physical-acceptance.json). |
| C14 inlet and cord | Derek accepts the printed inlet/C13-cord station. Its fitted pocket and screw stations are preserved; the reference uses the measured flange outline and R6 corners. [Native interface evidence](tee-readiness/full-enclosure-print/hard-contact-review/README.md). |
| G Ganen feet and flow | Derek identifies four identical flexible rubber feet with approximately 7 mm pads; they slide fore/aft independently and can be removed. Captured scan positions are not a fixed bolt pattern. Discharge is enclosure −X, corresponding to reference +Y at +90° yaw. Actual screw passage, washer seating and loaded rubber behavior remain assembly observations. [Sample authority](../../reference/g-ganen-pump/scan-evidence.json). |

## Tee and release face

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

## What remains before and during the trial

The reviewed back-bottom and two G Ganen mounting archives remain unsubmitted.
H2C is printing back-top; Mark2 awaits removal of display-cover v4 and the next-job
choice in “Scan results 2”. Front-top v8 is held. Printing records do not release a
held replacement. The correct black PET-GF mapping and
verified exact-archive handoff remain required for each send.
Offline ready is not submitted. The H2C mount alternatives are not additional required
prints.

The complete printed assembly establishes valve tie installation; four-tube insertion,
capture, release and relocking; pump mounting,
connectors and primed operation; and shell closure. G Ganen screw/washer seating and rubber
compression, DIGITEN arrow orientation, and actual made-up gas-fitting fit are direct
assembly observations. They do not require another scan or a separate coupon before the
requested trial. Production LLDPE routes retain nominal ¼-inch and ⅜-inch outside diameters.

Complete enclosure fit is an **outcome of this trial**, not a prerequisite to printing it.

The immutable [front-top cancellation](tee-readiness/full-enclosure-print/h2c-front-top-cancellation.json),
[launch](tee-readiness/full-enclosure-print/h2c-front-top-launch.json) and
[print-job records](enclosure/print-jobs.json) remain available for the affected archived
jobs. Their geometry and slice approvals are not active entries in the current queue.
