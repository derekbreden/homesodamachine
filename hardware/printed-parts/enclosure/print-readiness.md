# Front-top and tee-carrier print readiness

**The complete enclosure test print is being prepared.** Measured tee geometry, the
simpler two-piece carrier, G Ganen mounts and tube routes need one coherent regenerated
assembly and current slices. The assembled print supplies the spring-retention, tension,
rigidity and feel results.

The regenerated Box and complete front-top pass their current carrier checks. The
[fresh native report](tee-readiness/full-enclosure-print/current-front-top-check.json)
records 152 readings and 36 continuous sweeps using both canonical halves and the reusable
2 mm pusher. Complete assembly closure and current slices have their separate checks.

H2C's earlier front-top and the cap-rail cartridge jobs are cancelled. The latest cap-rail
job was paused at layer 1; cancellation and zero heater targets are recorded in
[print-jobs.json](enclosure/print-jobs.json). Derek has cleared both beds. H2C is available
for the corrected enclosure work; Mark2 is allocated to the other agent's fake-countertop job.

## Scans and fitted parts

| Part | Current evidence and model | Remaining physical work |
|---|---|---|
| Beduan solenoid | Measured reference: 24.4 × 24.85 mm post pitch, Ø6.9 posts, 5.2 mm bearing height, 59.5 mm port span and 57.3 mm overall height. Derek physically accepts the [production-profile socket coupon](../fixtures/valve-socket-fit/README.md): easy insertion and some inverted retention during loose shaking. Preserve the socket fit and use zip ties for positive retention. | Verify that the ties can be threaded and tightened in the complete carrier without disturbing valve seating. No new full scan is indicated. |
| DIGITEN flow meter | Measured offset body and mounting collars; placement, anchors, ties and adjacent tubing follow that envelope. | Confirm the molded flow arrow and actual installed direction. No new full scan is indicated. |
| John Guest PP0208E tee | Registered fixed surfaces support the conservative Ø16.5 collar and Ø14 root envelopes. Derek measures branch width at 30.5 mm extended and 29.0 mm pressed. Only the small outermost ring moves. Measured travel and face stations are integrated. The observed terminal face supports the Ø8.5 release aperture in all 36 sampled angular sectors. | Test simultaneous contact, release and relocking of all four actual rings in the complete enclosure. No additional full scan is indicated before the trial. |
| Kamoer pump | Two complementary native scans are complete. The short terminal pieces are Derek's inserted ¼-inch LLDPE stubs in silicone, excluded from rigid registration and integral pump dimensions. Derek confirms the existing cartridge/cap holds both pumps firmly with no vertical play. The cap retains a broad underside and fitted Ø37 motor bores; its raised crown has open Ø45 terminal wells. The fitted lower-well comparison matches the retained printed input within 0.004 mm. Floor relief leaves the well and cap surfaces unchanged. | Verify the raised crown with actual connectors and cycle four-tube insertion, capture, release and primed pumping in the complete enclosure. Use the matching new cartridge on the relieved floor. |
| G Ganen water pump | Three native views containing 1,033, 1,146 and 1,114 frames are fused at 0.10 mm and archived with hashes. The detailed reference, conservative mounting envelope, four sliding-foot mounts and affected hose routes are integrated; 58 native installation checks pass. Its flexible rubber feet slide fore/aft on channels and are removable. Derek identifies discharge as enclosure −X, mapping to local +Y at the intended +90° mounting yaw. | Complete the combined assembly check, then verify the actual mounting screws, washers, loaded rubber feet and operation. Captured foot positions are individual poses, not a fixed bolt pattern. |
| Faucet lever | The accepted flat-sided model with the 9 mm cylinder channel is primary. The printed mesh is byte-identical to the successful Mark2 artifact, with Derek's fit/function confirmation on record. | The complete faucet assembly needs a measured installed pose for its lever representation; that is separate from enclosure readiness. |
| Faucet display cover | **Physically accepted in PET-GF.** Derek confirms that its broad, long, thin walls provide successful give and spring. The current STL matches the successful complete-cover trial. | Use its broad-wall geometry as a proven example for new retention features; each new geometry still needs its own fit test. |

The [tee registration](../../reference/jg-pp0208e-tee/scan-registration.json) uses scale 1.0
and six fixed exterior patches; held-out p95 residuals are 0.061–0.107 mm. The corresponding
Beduan and DIGITEN comparisons reproduce 0.113 and 0.155 mm p95 respectively. These describe
agreement with the scans, not manufacturing tolerances.

The [Kamoer review](../../reference/kamoer-kphm400/scan-review.md) records the raw clouds,
rigid alignment, independent contact selections, frozen baseline CAD and reproducible checks.
Both native projects and their raw fused clouds are archived in
`~/Documents/3D Scans/2026-09-20-kamoer-pump/`.

## Tee and pump corrections

The tee journal is **Ø17.0 mm**, giving 0.25 mm nominal radial running air around the
conservative Ø16.5 collar envelope. Carrier troughs are R8.75; upper backing is 5.504 mm.
The measured run span is **42.5 mm extended / 39.2 mm pressed**, giving 1.65 mm per run end.
The [branch measurements](../../reference/jg-pp0208e-tee/branch-operating-measurements.json)
are **30.5 mm extended / 29.0 mm pressed**, giving **1.5 mm branch travel**. The branch
face stations are nominally 22.35 and 20.85 mm from the run axis when derived with the
nominal Ø16.3 back collar. The conservative Ø16.5 envelope is not that caliper datum.
The small outermost terminal ring moves. Its exact outer diameter and rear seam remain
unmeasured; the [terminal-face review](../../reference/jg-pp0208e-tee/terminal-bearing-review.json)
observes 99.73% coverage of the R4.25–4.75 mm bearing band around the Ø8.5 aperture,
with stock in all 36 angular sectors. Those unmeasured dimensions do not block the trial.
The measured branch datums are in the production source. The submitted cap-rail slice is
cancelled and its exact source closure is retained. Current Box and enclosure exports are
identified in the [geometry receipt](tee-readiness/full-enclosure-print/current-geometry.json). The frozen
measured-tee front-top fixture passes 38 interface checks, 26 stock checks and 12 positive contact probes.
The integrated simpler carrier passes complete rigid insertion and spring-loading
paths against the fresh canonical front-top, including the actual integral fixed cups.
That reading uses the regenerated Box with its paired 0.050 mm fore pump-station adjustment;
complete appliance closure remains separate. The [propagation record](tee-readiness/branch-propagation/README.md) names the
changed placements and the scope of each native check.

Deck separation is 60.95 mm. The carrier retains its full 2.5 mm station backing and clears
the aft valves' complete mounting-post entry by 0.25 mm. All four pump-tube axes align with
the carried tees. The [local native integration audit](tee-readiness/tee-integration.json)
passes 958 checks, including all carrier states, native tee envelopes, valve insertion and
declared tie-slot and tie-head clearances. It reads the regenerated 0.90 mm-backing carrier
halves and the paired pump stations at Y45.859 mm.
Those checks are distinct from the full enclosure build.

Kamoer's [physical-fit record](../../reference/kamoer-kphm400/physical-fit.json) confirms
firm retention in the existing assembled cap. The current cap's fitted boss/can band differs
from the retained printed mesh by at most 0.012 mm, within mesh approximation. Its surrounding
crown is level with the cartridge top, with open terminal wells and unchanged screw seats.
The [bounded native check](../../reference/kamoer-kphm400/contact-check.json) also verifies
its clear lift path and the conditional scan-to-floor clearance. Whole-enclosure generation
and the assembled physical trial remain separate.

## Carrier rigidity and assembly

**The simpler two-piece carrier is integrated in production source.** Its two moving
halves use a full-height fore lap, one captured rail and an overlapping upper shelf;
an integral broad rear wall retains the seated joint. The fixed spring cups belong to
the enclosure. No joint screws, heat-set inserts, separate keeper or spring-ID guide
are retained. The [integration record](tee-carrier/simple-carrier-study/README.md) and
[digest manifest](tee-carrier/simple-carrier-study/artifact-manifest.json) identify the
frozen native baseline. The [production backing check](tee-carrier/entry-backing-check.json)
identifies the current source and exact bounded difference.

The main web is 6 mm thick. Broad inner backing adds 0.90 mm above the lower valve coils'
insertion path. The shelf overlaps 31.85 mm across X and 18 mm in Y, with 6.625 mm plies
and 0.10 mm nominal face air. The 26.35 mm-wide fore lap, captured rail and upper cheek
provide broad bearing regions. The 51.75 × 9 × 3 mm rear wall retains the seated position;
its geometric clearance witness uses 2.3 mm free-tip displacement. Force, strain and
endurance are unmeasured.

The current production manifold derives the same carrier spec as the printed source,
including 0.25 mm valve-entry air. Its selftest and 34 backing integration checks pass.
The canonical carrier STEP, STL and viewer payloads are regenerated from that source;
their verified digests are in the [readiness record](print-readiness.json). The
[fresh wall report](tee-readiness/full-enclosure-print/current-front-top-check.json)
proves their native equality, actual Box agreement and complete placement/working paths
through the canonical front-top. The actual slice and support-removal lanes are separate.
Each source-built half is an exact subset of the frozen study: only the declared
0.05 mm backing strip is absent, with no change to cups, joint, guides or bearing faces.
Those bounds carry the baseline collision-free paths to the current halves. Checks pass for five
continuous inter-half sweeps, nine deflection witnesses, ten full-half wall sweeps, ten
held-spring/pusher sweeps, four pusher-removal sweeps, six working wall states and twelve
opposed guide-contact probes. Another 102 native neighbor readings, forty tee-entry sweeps,
sixteen lower-valve/body and coil insertion sweeps, thirty-two tie lanes and thirty fixed-cup
neighbor checks pass. These use the exact frozen measured-tee wall named in the manifest;
they remain distinct from the fresh complete-wall report and combined assembly.

Install the left half and then the right through the loose front-top with the bare tees
at release and valves absent. Each spring is held axially in its closed moving cup.
Each half has five placement segments: rear entry, lowering, outward staging, fore slide
and outward seating. The temporary pusher then withdraws inboard and lifts through the
outer tee well. One 2 mm-thick reusable pusher serves both sides in sequence; its
[19 native route checks](../fixtures/carrier-spring-pusher/native-sequence-check.json)
include right-half entry with the left spring already released into its cups.
The shelf requires no separate lift or twist; the right half's final
outward seat retains the joint. The [assembly view](tee-carrier/simple-carrier-study/assembly-sequence.png)
shows these motions. Actual hand effort is a full-enclosure trial result.

The [current section readings](tee-carrier/entry-backing-check.json)
give sampled minimum Iy of 78,368.9 mm⁴ versus 76,204.1 mm⁴, and Iz of 12,249.1 mm⁴ versus
994.5 mm⁴, for the frozen measured-tee screwed CAD reference. The reference is not the bowed
physical coupon or the carrier preceding spring relocation. The beam spans X: transverse
Y loading bends about Z and uses Iz; transverse Z loading bends about Y and uses Iy.
Observed bowing along X does not identify the force direction. Improved sampled minima
do not imply uniform local improvement or measured assembled stiffness; joint slip,
print anisotropy and guide compliance remain physical properties of the complete trial.

The [archived body audit](tee-carrier/readiness-audit.json) retains its separate comparison
to the print preceding spring relocation: local Izz ratios 156.29 at the inner tee, 5.21
at the outer tee and 0.887 at the grip root, with equal-modulus body bending gains of
35.82 for equal grips and 1.379 for spring return. It excludes the center joint, torsion
and shear and does not qualify this complete carrier. Its spring-load fixture requires
23.795 N·mm of center-joint bending and 25.035 N·mm of roll restraint per 1 N total spring
force. Those values remain archived model evidence.

The [joint coupon physical report](tee-carrier/joint-coupon/physical-fit.json) establishes:

- Both interlocking halves assemble with a small amount of force and a tight friction fit.
- Derek observes **no rocking or play**.
- The assembled coupon is secure but **bows along X more easily than acceptable for the
  carrier's function**. Derek identifies short X engagement as a possible contributor;
  force and bending mode are unmeasured.
- The separate keeper inserts, but its tiny catch supplies essentially no observed spring
  tension. The catch is not accepted as a meaningful positive lock.

Neither coupon half is selected for reuse in the integrated carrier. The tight fit and
absence of play are observations; Derek does not accept the coupon's design or complexity.
The right-only integral latch trial is withdrawn from the print queue. The
[faucet display cover](../faucet/faucet-display-cover/physical-acceptance.json)
is Derek's preferred example for the snap-fit approach: simple, broad, substantial
walls provide the give and spring. Its success does not qualify a differently proportioned
part. The nameplate is physically successful, including its snaps, but is not accepted
as an example of the desired simplicity.

The complete enclosure assembly-test print supplies the actual rigidity, joint retention,
spring behavior and assembly-effort readings. These are test outcomes, not requirements for
another coupon before that print. The [integral latch study](tee-carrier/joint-coupon/integral-latch-study/README.md)
retains its distinct geometric and toolpath evidence without a print release.

## Measured springs and capture

[Derek's measured pair](tee-carrier/spring-measurements.json) is **27 mm free, approximately
7 mm compressed (possibly slightly less), and Ø6 mm**. Wire diameter, inside diameter and
spring rate are not measured.

| State | Bearing separation | Compression from 27 mm | Margin above approximately 7 mm compressed |
|---|---:|---:|---:|
| Release / squeeze | 19.35 mm | 7.65 mm | 12.35 mm |
| Connected | 21.35 mm | 5.65 mm | 14.35 mm |
| Aft limit | 23.85 mm | 3.15 mm | 16.85 mm |

The production moving cup is a **closed Ø6.57 mm teardrop bore, 11.1 mm deep**. Its inboard
side is permanently closed. Each integral fixed cup is 8 mm deep with Ø6.57 mm ID,
Ø10.57 mm OD and 2 mm radial wall. The bore gives 0.285 mm nominal radial air to the
measured spring. Axes remain X±97.535, Z211.209 mm; spring floors are Y90.040 and
Y109.390 plus travel. Working travel is 0 / 2.00 / 4.50 mm at release / connected / aft stop.

Gaps between cup mouths are **0.25 / 2.25 / 4.75 mm** at those states. Native checks preserve
both floors, clear the spring envelope and block a rigid D6 lateral sphere witness. A real
helical coil can deform; those readings do not establish impossible real misalignment.
Both-end retention through unequal-hand movement and deliberate sideways loading is an
outcome of the full enclosure print.

The spring loads axially at **12.15 mm held length**, 5.15 mm above the approximately 7 mm
compressed estimate. The canonical [flat pusher](../fixtures/carrier-spring-pusher/README.md)
has a **Ø6.3 mm tip, 2 mm thickness and a 10 × 3 mm tongue**. One tool serves the left
spring and then the right. After each half seats, it withdraws 15.435 mm inboard and lifts
70 mm through the outer well. The fresh complete-wall check verifies installation,
one-tool reuse and removal with a conservative 0.30 mm lift-lane gap on both sides.
The fixed-cup air is 1.70 mm. The source, printable files and exact digests
are recorded in its [geometry check](../fixtures/carrier-spring-pusher/geometry-check.json).

The frozen [spring-capture checks](tee-carrier/simple-carrier-study/spring-capture-checks.json)
and [wall route](tee-carrier/simple-carrier-study/wall-checks.json) retain their thinner
0.6 mm witness; that witness is not the printable tool. The current pusher has its own
[native route record](../fixtures/carrier-spring-pusher/native-sequence-check.json).
The [fresh integrated check](tee-readiness/full-enclosure-print/current-front-top-check.json)
passes with the complete canonical front-top, both current half STEPs and the 2 mm pusher.
No spring ID measurement or retained guide plug is required. Spring force and actual
compression effort remain unknown.

The [guide-plug study](tee-carrier/spring-capture-study/README.md) and its archived 9.61 mm
loading fixture remain separate exploration records. They do not describe the integrated
closed-cup assembly or specify another required print.

## Nameplate print

Mark2 has completed the black-and-white unit-0001 nameplate and its matching receiver coupon.
The [native job record](nameplate/mark2-print-readiness.json) records black PET-GF on the left,
white PET-GF on the right, both carrying the printer's PET-CF label. This is the right
hotend's first use with white PET-GF. Derek reports clear appearance, reliable QR scanning
from 2 feet, intermittent scanning from 3 feet, and working snaps. The
[physical result and photographs](nameplate/physical-acceptance.json) identify the exact
print; its photographed QR independently decodes to `HTTPS://HOSM.US/0001`. The nameplate
remains more complex than Derek prefers for the carrier's design example.

## Other readiness evidence

| Scope | Needed evidence |
|---|---|
| PP0208E operating nose | In the complete print, confirm that all four moving rings contact, release and relock without the fixed barrel bottoming. The existing scan supports the aperture's annular contact; a contact mark or face-diameter reading is only needed if the trial exposes a problem. |
| Kamoer fit and tubes | Existing assembled cap retention is accepted. The full trial checks connectors, all four marked insertion depths, tug/capture, carrier release and primed pumping. |
| Complete tee carrier | The full enclosure trial records both-end spring retention at every stop, unequal-hand behavior, sideways deflection and whole-span bowing under the actual assembled constraints. These are physical trial outcomes. |
| Machine display cover | Derek confirms the display was already test fit with the previous design. Use that accepted fit and verify the current shell interface; no separate coupon or repeat cover print is required. |
| Before wider enclosure release | Verify the combined generated assembly and current slices containing the G Ganen reference, sliding-foot mounts and hose routes. |
| Back-top gas fittings | Seats and ceiling pockets use nominal dimensions. Confirm the made-up fitting fit in the complete enclosure; no separate coupon is required. Actual gas-fitting fit remains unverified. |

Already fitted rectangular and cylindrical parts do not require scans merely because a
scanner is available. Printed friction, spring capture and tube reconnection require the
physical mechanism.

## Complete enclosure trial

Derek requests fresh prints of all four shell quadrants and the complete pump mechanism.
No earlier shell print constrains the design or needs to be reused. The first H2C plate
contains front-top, both carrier halves and the required spring-loading tool;
the matching cartridge and raised cap are prepared for Mark2 after its countertop job. The remaining
three quadrants receive current slices for subsequent available beds. Physical testing uses
the complete enclosure; no additional test coupons are required.

1. Verify both carrier halves, the closed fixed/moving cups and the canonical 2 mm pusher
   against the regenerated front-top: complete installation/removal paths and working stops.
2. Complete affected part generation and the combined native assembly checks. Verify the
   actual final STEP/STL/payload digests, motion, neighbors and lower-shell interfaces.
3. Prepare the complete enclosure and mating parts as one assembly trial. Spring capture,
   tension, rigidity and feel are checked in that assembly after printing.
4. Slice the final enclosure with the current PET-GF profile and H2C +0.18 mm requested
   trim; confirm the emitted +0.16 mm Textured PEI compensation. Inspect actual support
   contacts and straight extraction lanes. Retained old support audits do not qualify a
   changed STL or profile.
5. Check H2C's live state against Derek's confirmed availability, send a uniquely named
   replacement and verify that exact job on the printer.

The prior assembly's 107 passing checks, 398 carrier motion/envelope readings and source
hashes are retained as baseline evidence. A fresh combined build is required for the current
tee and pump corrections. The machine-readable [readiness record](print-readiness.json)
tracks current artifacts separately from that baseline. Repository-wide checks are not all
passing and must not be presented as an all-green project.
