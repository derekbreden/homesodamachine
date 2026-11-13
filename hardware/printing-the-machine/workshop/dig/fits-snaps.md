A. STORY
Fits were found by printing labelled ladders in the production pose and letting Derek choose by hand; almost nothing was measured. On the PET-CF faucet (May-June) zero-clearance slip joints jammed, 0.5-1.0 mm was far too loose, 0.05-0.10 mm radial held, and printed dowels sheared off and were replaced by screws in heat-set inserts. Flat-wing snaps for the nameplate and display cover took up to ten versions to stop bowing, then became four screws because their pockets trapped supports. Rear equipment caps went from "basically 0 hold" to approved in a week. The 2026-11-12 Wago session replayed it all in four hours: roofs printed in air, a cracked pocket, a cancelled fine-layer plate, then a coupon Derek called "awesome".

B. LESSONS
1. Z dimensions move only in whole layers: read the sliced opening; never change layer height to chase a fit. Why: a 0.05 mm CAD difference either vanishes or flips a 0.24 mm layer. Evidence: eb3ec0fcf:hardware/print-tests/front-top-wago-fit/2026-11-12-mark1-dots-3-4-standard-layers/print-job.json (CAD 29.9 and 30.0 both sliced 30.0; 30.1 and 30.2 sliced 30.0 and 30.24); b57b985c6:hardware/printed-parts/fixtures/faucet-cover-retention/README.md (3.00 and 3.10 mm tabs "finish on the same printed layer"). Derek (ae3a1e7b7): "Do not use finer layers anywhere - that is not an option - that is a completely different variable". Scope: any FDM. Stated: /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/AGENTS.md.

2. For a bought hard part held by friction, draw the PET-GF pocket at catalog size between vertical walls and about 0.1 mm per side along the build axis; for one clamped under a cap, follow its real profile at 0.15 radial, 0.25 axial. Why: PET-GF will not stretch. Evidence, Wago 221 per side against catalog: Y +0.15 "a bit loose", 0.00 accepted, -0.35 or tighter spread the wall 0.7 mm and cracked it; Z as sliced +0.10 accepted (eb3ec0fcf and cbd8efc66, physical-result.json). Magnet and valve posts chosen at nominal: /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/enclosure/magnet-retention/fit-coupons/physical-fit-selection.json. PISCO regulator in bounding cylinders had "no useful retention": /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/rear-snap-retention/v5/pisco-fit-review/README.md. Derek: "My guesses on adjustments were way off... you can see it snapped the edge of the receiver." Scope: PET-GF15, 0.4 nozzle. Numbers stated; rule inferred.

3. Printed-to-printed clearance is surface, not air: 0.15 static, 0.25 sliding, +0.25 per supported face, +0.10 at a cavity floor, +0.50 where only a spring moves the part. Evidence: /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/clearance-audit.md; port chips 0.15 "a bit tight", 0.30 "a bit loose", 0.20 chosen (/Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/rear-identification/prints/2026-11-09-co2-width-mark1/physical-result.json). Derek (f87d2686b): "if you put a 1mm object next to a 1mm object pressed with several lbs of fource you still don't get a 2 mm object, you get a 2.15 mm one." Scope: PET-GF pairs. Stated.

4. Give a snap its own leaves bending within the layer plane (2.0 mm thick, about 22 mm free, R1.5 root, flat 2.6 mm catch), a long solid pointed lead-in (rise 1, 3, finally 6 mm) and exposed leaves to spread for release. Why: a thin arch cap held nothing; 1.3 mm leaves printed across layers fractured; 2.6 mm bent only at the root; a cradle wing cut from 11.24 to 9.24 mm snapped; a screwdriver tunnel bent the wing only locally. Evidence: /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/pump-mount-fit/physical-result.json; /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/rear-snap-retention/physical-result/physical-result.json, then v2/, v4/; /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/receiver-tool-access/physical-result/physical-result.json; /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/rear-equipment-caps/prints/2026-11-07-ceiling-down-mark2/physical-result.json; b57b985c6:hardware/printed-parts/zone-c/funnel/cradle-trial/physical-acceptance.json. Derek (9a96de823, 015b351fc): "Can they all be designed to be printed on their end like the pump cap?"; "The longer pointed tips on the snaps there worked beautifully." Scope: PET-GF, hand feel only; long tip tried on one cap. Stated.

5. Where a snap pocket needs supports no tool can reach, use screws in heat-set inserts: maker's pilot (Ruthex 4.0 for M3, 6.4 for M5), 1 mm blind relief, local 100% infill, no supports in pilots. Evidence: commits fc74d2e40, 01119b116; /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/enclosure/heat-set-review/README.md. Derek: "So I'd like four screws for this display cover instead of these impossible-to-remove supports." Scope: enclosed PET-GF receivers. Stated.

6. Cut coupons from the production STL with the parent wall, both bridge landings and every stop, in production pose, unscaled. Evidence: a relieved coupon lost its roofs (a8f24b2b5:hardware/print-tests/front-top-wago-fit/2026-11-12-mark2/physical-result/); /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/rear-snap-retention/v4/README.md; layer-grid placement in /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/enclosure/contact-pair-coupon/README.md. Derek: "The only reason a bridge works is because it *is* a bridge that actually has a column supporting both ends." Stated.

7. A good coupon still misses tool access, assembled stack-up and layer time. Evidence: the full back-top's walls blocked the screwdriver that cleared the coupons (/Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/enclosure/enclosure/prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json); ASSE body and adapter each seated alone but together lifted the cap; a lone coupon with 1-3 s layers deformed (2f2d9c94a:future/snap-fit-tests/2026-10-26-mark2-combined/README.md). Derek: "I can't reach in that far to remove those tiny little supports." Stated.

8. Size passages by ladder at two lengths; drag grows with engaged length. Evidence: M5 thread 5.2 (b57b985c6:hardware/print-tests/m5-seam-bearing/physical-result.json); quarter-inch tube 6.65 in a 10 mm organizer, 7.05 through the long curved PET-CF faucet. Derek: "On the 12 mm sample it pushed through fine, on the 40 mm sample I got some resistance". Scope: PET-GF vertical bores. Stated; tube comparison inferred.

9. Never load a printed peg or plate across its layers. Evidence: /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/faucet/faucet-shell/print-log.md (attempt 16: 4 mm bosses snapped twice); pump base split before the snaps released. Derek: "they snap so easy because of the orientation of the layer lines. This is just not workable." Scope: PET-CF, PET-GF. Stated.

10. First-layer Z trim belongs to one printer, plate, material and nozzle; homing touches the texture peaks, and plates differ. Evidence: /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/z-trim.md; /Users/derekbredensteiner/Developer/homesodamachine/tools/bambu-printers.md (Mark2 +0.04, Mark1 +0.18); PET-GF trim on a glued Engineering plate "lifted right off." Derek: "one of the confounding variables is which textured PEI plate is used." Stated.

C. BAKED-IN BASICS
- Fit prints keep production pose, layer schedule, nozzle and per-printer trim, centred on the plate; hole and contour compensation stay zero, so fits are tuned in CAD.
- Ladders step 0.05-0.10 mm; every specimen is labelled in the plastic, with a control and independent axes.
- Empty cap first, then real hardware; verdicts are Derek's own words, scoped: force and fatigue not established.
- 3 mm walls and backing; solid local infill at snap, insert and knuckle hosts; one body, fewest edges.
- Thin flat features are whole layers (1.44, 1.68, 3.36, 3.84 mm) [inferred].

D. PICTURES
1. cbd8efc66:hardware/print-tests/front-top-wago-fit/2026-11-12-mark1/physical-result/IMG_8623.jpeg: cracked pocket corner beside the orange Wago (L2).
2. Same folder, IMG_8624.jpeg and IMG_8625.jpeg: caliper at 21.83 and 22.53 (L2).
3. a8f24b2b5:hardware/print-tests/front-top-wago-fit/2026-11-12-mark2/physical-result/IMG_8621.jpeg: coupon roofs printed into air (L6).
4. /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/rear-snap-retention/physical-result/meter-fracture.jpg: first cap, wing torn, layers across the arch (L4, failure).
5. /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/rear-snap-retention/v2/physical-result/pump-fit.jpg: box cap seated on the pump (L4, success).
6. /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/rear-snap-retention/v4/physical-result/10-all-five.jpg: five cropped coupons holding real hardware (L6).
7. /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/rear-snap-retention/v2/physical-result/pump-base-fracture.jpg: base split along a layer (L9).
8. /Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/faucet/faucet-display-cover/prints/2026-10-17-cooling-off-prepared-mark2/fracture-photo.jpg: white PET-GF cover peeled along layers (E).
9. b57b985c6:hardware/print-tests/m5-seam-bearing/plate-map.png: drawn ladder map, not a photo (L8).

E. SURPRISES
- Catalog size is the easy-but-held fit for hard bought parts; 0.15 mm per side felt loose.
- Two same-model printers need trims 0.14 mm apart; one machine's two nozzles sat 0.50 and 0.70 mm apart in XY under Auto calibration (/Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/calibration/dual-nozzle-registration/README.md).
- Part-fan cooling made PET-GF covers break during assembly; the fan-off cover outlasted "the other parts of the faucet".
- Tube collars are held by the tube's coil-set bend, not the bore (/Users/derekbredensteiner/Developer/homesodamachine/hardware/printed-parts/faucet/tube-collar/README.md).

F. GAPS
- Wago: five-dot result pending; production still 0.15 (/Users/derekbredensteiner/Developer/homesodamachine/hardware/manifold-layout/junctions.json). Records do not say which pocket Derek tried; dots 3 to 4 changed Y and Z together. By my arithmetic the coupon base (Z224.85 over a Z160.25 bed) is a third of a layer off the production grid, so the layer the four-dot 415 pocket lost would survive in the real front-top [inferred].
- heat-set-review/README.md says clearance holes print at 5.6; source and trial say 5.2. The ladder stopped at 40 mm; the joint is 100 mm.
- /Users/derekbredensteiner/Developer/homesodamachine/hardware/ledger/fitted.json rows HSM-0449 and HSM-0450 cite the v4 result, which records play; the approving quote is in /Users/derekbredensteiner/Developer/homesodamachine/hardware/print-tests/pointed-snaps/physical-result/physical-result.json. Rows HSM-0069 and HSM-0076 attest snap versions since replaced by screws.
- A September display-cover trial realised a sub-layer change with a fine "precision band"; the November rule forbids it.
- No snap has force, cycle or vibration data.
- z-trim.md quotes Derek near +0.01 to +0.02; production runs +0.04 and +0.18, unexplained.
- Several results cite photos kept outside the repo.

Note: sha:path entries are archived (`git show`). The 2026-11-12 guide (/Users/derekbredensteiner/Developer/homesodamachine/hardware/fdm-print-guide/README.md) already carries lessons 1 and 6 and pictures 1 and 8. Extracted copies of the archived pictures:
/private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-fits/wago-mark1-IMG_8623.jpeg
/private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-fits/wago-mark1-IMG_8624.jpeg
/private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-fits/wago-mark1-IMG_8625.jpeg
/private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-fits/wago-mark2-IMG_8621.jpeg
/private/tmp/claude-501/-Users-derekbredensteiner--claude-spares-spare-R8DUrN/f08a8255-97ac-445e-9478-10dd59e4e1e7/scratchpad/agent-fits/m5-plate-map.png
