# Front-top and tee-carrier print readiness

**The production enclosure is not released for printing.** The known tee collar interference
and Kamoer contact defects are corrected in the source. The selected G Ganen water pump
is being scanned for its reference, mounts and tube routes. The combined enclosure rebuild,
carrier retention and the physical checks below remain open.

H2C's `enclosure-front-top-petgf-z018-h2c.gcode.3mf` is cancelled. Its valve-tray region was
2 mm above the corrected assembly. The last running reading was 51/813 layers; cancellation
and zero heater targets are recorded in [print-jobs.json](enclosure/print-jobs.json).
Removal of that object from H2C is not yet confirmed.

## Scans and fitted parts

| Part | Current evidence and model | Remaining physical work |
|---|---|---|
| Beduan solenoid | Measured reference: 24.4 × 24.85 mm post pitch, Ø6.9 posts, 5.2 mm bearing height, 59.5 mm port span and 57.3 mm overall height. Sockets, valve trays and cold-core cradles consume these dimensions. | Fit actual posts in a production-profile socket coupon and check the other valves. No new full scan is indicated. |
| DIGITEN flow meter | Measured offset body and mounting collars; placement, anchors, ties and adjacent tubing follow that envelope. | Confirm the molded flow arrow and actual installed direction. No new full scan is indicated. |
| John Guest PP0208E tee | Registered fixed surfaces support the conservative Ø16.5 collar and Ø14 root envelopes. The generated reference, carrier, journals, manifold and water split consume those dimensions and the measured 42.5 mm extended run. | Resolve absolute extended branch reach, the fixed/moving nose boundary and the release rim. Those axial features remain explicitly provisional. |
| Kamoer pump | Two complementary native scans are complete. The short terminal pieces are Derek's inserted ¼-inch LLDPE stubs in silicone, excluded from rigid registration and integral pump dimensions. Cap pressing rails, floor relief and outlet stations are corrected. | Fit both actual pumps in the corrected cartridge/cap, then test four-tube insertion, capture, release and primed pumping. No third scan is needed for these contact corrections. |
| G Ganen water pump | Derek selected the received G Ganen sample on September 20. No caliper dimensions were recorded. First native scan: 1,033 frames, high accuracy, 0.10 mm fusion; complementary view and dimensional analysis are pending. | Update the pump reference, mounts and affected tube routes from the scan, then check installation and operation. Existing SeaFlo assembly checks do not qualify this pump. |
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
The production reference preserves Derek's **42.5 mm extended / 39.2 mm pressed run span,
1.65 mm sleeve stroke, 0.5 mm nose gap and 10 mm insertion depth from the pressed sleeve**.
The branch reach, body-to-nose boundary and release rim are named provisional parameters;
the registration of fixed surfaces does not settle those axial stations.

Deck separation is 60.95 mm. The carrier retains its full 2.5 mm station backing and clears
the aft valves' complete mounting-post entry by 0.25 mm. All four pump-tube axes align with
the carried tees. The [local native integration audit](tee-readiness/tee-integration.json)
passes 107 checks, including all carrier states, native tee envelopes and valve insertion.
Those checks are distinct from the full enclosure build.

Kamoer's corrected cap has two exposed 3 × 32 mm pressing rails per pump, landing nominally
8 mm above the fitted skirt seats with 0.25 mm screw adjustment. The continuous floor relief
is 2.6 mm. At the archived contact fixture it retains 4.015 mm floor stock and gives the
minimum observed front rim 0.340 mm air. The fitted skirt lands and locating profiles remain
the seating reference. The molded outlet station and 0.251 mm seating drop propagate through
the pump placement and all four tube paths. The [contact audit](../../reference/kamoer-kphm400/contact-check.json)
checks native cap clearance, bearing faces, screw adjustment and the flat insertion corridor.

## Carrier rigidity and assembly

The carrier has a 6 mm web, broad inner shelf and spring reaction in each grip. The current
[section and bending audit](tee-carrier/readiness-audit.json) compares its actual mesh with
the print preceding spring relocation. Local Izz ratios are 156.29 at the inner tee, 5.21 at
the outer tee and 0.887 at the grip root. A load-weighted beam comparison gives body bending
gains of 35.82 for equal grips and 1.379 for spring return, assuming equal modulus and
excluding the center joint, torsion and shear. These are bounded model comparisons, not
measured assembly stiffness.

The relocated spring loads require 23.795 N·mm of center-joint bending and 25.035 N·mm of
roll restraint per 1 N total spring force. Service-slot lands and rim-to-roof/fore-guide
contacts provide positive restraint in the source, with 0.50 mm nominal vertical clearance.
The fresh native wall, complete joint and physical full-width mechanism still need checking.

The [joint coupon physical report](tee-carrier/joint-coupon/physical-fit.json) establishes:

- Both interlocking halves assemble with a small amount of force and a tight friction fit.
- Derek observes **no rocking or play**.
- The separate keeper inserts, but its tiny catch supplies essentially no observed spring
  tension. The catch is not accepted as a meaningful positive lock.

The production target is **two halves that lock during their normal mating movement**.
There should be no separate keeper or extra fastening step. Simpler assembly is a required
benefit of the snap fit. The successful key and lap fit should be preserved while an integral
broad compliant wall and retaining lip provide capture. The
[accepted faucet cover](../faucet/faucet-display-cover/physical-acceptance.json) is the physical
PET-GF precedent. Production integration must also verify full-half entry, valve clearance,
release access and full-width stiffness. The production carrier currently retains its
screw-clamped lap. The [integral latch study](tee-carrier/joint-coupon/integral-latch-study/README.md)
checks the two-piece alternative against the current tee and valve positions. Its existing
left bench coupon is reusable; the revised right half supplies the broad spring wall. The
right-only Mark2 trial is prepared at 21 min 46 sec and 7.54 g. Production integration also
requires a 1.392 mm trim of the plain lap tip while preserving the accepted keys. Automatic
engagement, retention force and practical release await the physical trial.

## Measured springs and capture

[Derek's measured pair](tee-carrier/spring-measurements.json) is **27 mm free, approximately
7 mm compressed (possibly slightly less), and Ø6 mm**. Wire diameter, inside diameter and
spring rate are not measured.

| State | Bearing separation | Compression from 27 mm | Margin above approximately 7 mm compressed |
|---|---:|---:|---:|
| Release / squeeze | 19.50 mm | 7.50 mm | 12.50 mm |
| Connected | 21.65 mm | 5.35 mm | 14.65 mm |
| Aft limit | 24.15 mm | 2.85 mm | 17.15 mm |

The Ø6.57 spring channel has 0.285 mm nominal radial air. The 9.61 mm loading space is
2.61 mm above the measured compressed estimate. The measured-spring consumer uses these
actual dimensions and records force as unknown.

**Both-end positive capture is still required.** The current moving channel's first 10 mm
is open inboard; only 1.1 mm remains closed at its blind end. The free gap between fixed and
moving mouths ranges from 6.40 to 11.05 mm. Straight-envelope clearance and preload do not
prove that a sideways-deflected spring remains aligned.

The [capture study](tee-carrier/spring-capture-study/README.md) checks an enclosed moving bore and axial loading from the empty pump
bay, with one recessed guide/seat plug per spring. Rigid retaining surfaces carry spring
reaction; any compliant latch retains the plug's assembled position. The guide diameter must
follow the actual spring ID. The study is not integrated or released for printing. It must
preserve the reaction-floor stations and cartridge path while keeping assembly simple.

## Nameplate print

Mark2 has accepted the black-and-white unit-0001 nameplate and its matching receiver coupon.
The [native job record](nameplate/mark2-print-readiness.json) records black PET-GF on the left,
white PET-GF on the right, both carrying the printer's PET-CF label. This is the right
hotend's first use with white PET-GF. The commanded first-layer paths decode to
`HTTPS://HOSM.US/0001`; physical QR readability, support removal and snap retention remain
to be checked after printing. The estimate is 1 h 23 min and 35.12 g using the saved profile
density.

## Other readiness evidence

| Scope | Needed evidence |
|---|---|
| PP0208E operating nose | Caliper the extended branch width shown in the [measurement diagram](../../reference/jg-pp0208e-tee/branch-measurement.svg), and identify the fixed/moving boundary. A targeted end view is useful only if that seam cannot be resolved directly. |
| Kamoer physical contact and tubes | Both skirt seats loaded; rims clear floor; cap removes play before hard stops. Cycle all four marked insertion depths, tug/capture, carrier release and primed pumping. |
| Complete tee carrier | Both springs captured at every stop, including unequal grip motion and sideways deflection; compare full-width stiffness under the same loads and constraints. |
| Machine display cover | Test its actual printed snap and housing section. The faucet cover's success is a precedent, not acceptance of this different part. |
| Before wider enclosure release | Complete the G Ganen scan-derived reference and propagate its actual feet, head, switch and port geometry through mounting, storey and tube-route consumers. |
| Before back-top/gas-chain release | Caliper made-up adapter/coupling/check-valve lengths, seat diameters and thread engagement; scan external forms only where needed. |

Already fitted rectangular and cylindrical parts do not require scans merely because a
scanner is available. Printed friction, spring capture and tube reconnection require the
physical mechanism.

## Production release

1. Settle the remaining tee operating datums and integrate simple, positive joint and spring
   retention; preserve established pump seating faces and successful joint fit.
2. Complete affected part generation and the combined native assembly checks. Verify the
   actual final STEP/STL/payload digests, motion, neighbors and lower-shell interfaces.
3. Print the small mating parts and corrected cartridge as they become ready. Establish
   the physical fit and mechanism readings above before the large enclosure print.
4. Slice the final enclosure with the current PET-GF profile and H2C +0.18 mm requested
   trim; confirm the emitted +0.16 mm Textured PEI compensation. Inspect actual support
   contacts and straight extraction lanes. Retained old support audits do not qualify a
   changed STL or profile.
5. Confirm H2C's plate is clear, send a uniquely named replacement and verify that exact
   job on the printer.

The prior assembly's 107 passing checks, 398 carrier motion/envelope readings and source
hashes are retained as baseline evidence. A fresh combined build is required for the current
tee and pump corrections. The machine-readable [readiness record](print-readiness.json)
tracks current artifacts separately from that baseline. Repository-wide checks are not all
passing and must not be presented as an all-green project.
