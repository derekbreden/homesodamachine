Paths: R=/Users/derekbredensteiner/Developer/homesodamachine; ENC=R/hardware/printed-parts/enclosure; E=ENC/enclosure; NSR=ENC/tee-readiness/full-enclosure-print/native-slice-reviews; CH=R/changes; GA=R/hardware/fdm-print-guide/art. "@sha" = archived (git show). Dates are 2026. No repo file was touched.

A. STORY
The box began as two halves printed on a Y face. The four-piece split (07-21, 7b127a240) laid each piece on a closed Z face, with every relief drawn for its piece's build direction. Early September a support-count audit turned the rear rail's flat catch into a cam ridge; 09-06 restored it, "accepting support under it" (4d5e1d300), and the audit stopped ranking designs. Late September a print-bottom R6 in 0.08 mm layers curled, then with the fan off: "Exploded basically."; geometry fixed it. October's full prints failed on removal: front-top v17 (fused normal and tree masses, spaghetti over supported fine layers), a back-top full of normal supports, then spindly bed-rooted trees stuck in its walls. November deleted overhangs (corbels, teardrops, bridges, solid fill) and supported the remaining flat faces from the part's own nearby floor.

B. FRONT-BOTTOM (HSM-0078, 221 x 216 x 181 mm; E/prints/2026-11-11-front-bottom-D-mark2)
Pose: floor-down, unrotated; 0.20 mm first layer, 0.24 after (754 layers); 52 mm bed margin; no fine bands, six-wall bands, fins or bed-rooted trees.
Supported faces: two, the east and west rail-head catches, flat at Z169.2, about 4.5 x 158 mm each (support-contact-review.json). They are the Z seam's whole bearing against lift: "Sloping introduces a camming bearing" (lint answer). Each tree roots on the piece's own seam mouth 7.9 mm below, in a groove open to the outside along its run; supports are 14 minutes of a 22.7 h native slice. Derek, 11-08: "the tree supports in those rail cavities *are* easy to remove, as long as they are actually in that cavity"; 11-10 rail coupon: "It came off as a single piece".
Feature -> lesson -> where learned:
- Handhold roof is a 45° corbel from the inner wall (Z21.5) up to the mouth (Z34, hsm section) -> slope a roof's hidden side; the change deleted a six-wall band, a ceiling inset and edge fins from the recipe -> 3dc5416a8, 11-09: "simply add a corbel to avoid the ugly overhang here. We don't need any fine layers."
- Tree branch angle 20°, roots allowed on the model -> trees start in their cavity -> back-top 10-11: "spindly tiny incredibly long fragile supports reaching from the plate".
- 45° under-flare beneath each rail arm, 45° Y-seam knuckle faces, 45° corbels under condenser rail, finger and plate feet -> hidden down-faces rise at one angle -> E/README.md "Print orientation + corner relief".
- M5 passage becomes a slot where it crosses a 45° knuckle face -> a vertical bore through a slope leaves a 0.3 mm skin -> CH/2026-10-20-2154-hinge-bore-slots.
- Wall under the seam lip is two walls thick to the slab -> "the bottom pieces come off the bed with no bridge in them" -> 7cecc5ab1.
- Floor tongue at full slab thickness on the bed, square ends, one floor plane -> "What I mind is introducing steps and edges" -> CH/2026-10-22-0248-one-floor-plane.
- R12 standing corners, solid columns behind, square seam edges -> anti-warp relief on arrises parallel to the build axis -> 1ecae31e6, 7b127a240 (no warp failure recorded).
- Flutes run up the build axis and fade over 5 mm from bed, seam and openings; four perimeter loops remain under each groove -> plain first-layer outline, no infill read-through -> @c14bb2fff ENC/texture-coupons/README.md; 0f076a3e0.
- Vents: slots down groove floors, 45° hips, three unpierced transoms -> nothing bridges -> E/README.md "The condenser's vents".
- Seam band: circular swell, steepest 41° from vertical (measured; purpose inferred).
- Bores all on the build axis, round; bosses stand on the slab (ea9093830); ten 100 % infill-only modifiers at knuckle, rail and post roots.
Other quadrants:
- Back-bottom: same pose; rear catch counts two supported faces; forced trees under the handhold arch and seam lip after a coupon sagged; warning letters with 45° undersides, level tops (CH/2026-10-20-2346-disposal-letter-tops).
- Front-top: mouth-down on its seam rim; rail channels gabled at 45°, unsupported; pump mount carried up as solid stock; Tree Slim; the only 0.08 mm bands (R6 roof edges, R18 roll).
- Back-top: ceiling-down, roof as first layer, ceiling panel gone (366d54ba0); R6 roof edges as chamfers with six walls; teardrop bores; 42 mm catch bridges between full shoulders; 28 support-free and 23 forced regions (E/enclosure-back-top.print-features.json).

C. LESSONS
1. Keep the working face; take a support that leaves cleanly; never score by support count. "A count of support bodies falls when the supported thing is deleted" (35a260e36, agent-written). E/README.md "Support-removal strategy". No Derek quote; trailers begin in October. All parts. Stated.
2. No rectangular supports in cavities; Tree(auto) by default. R/hardware/printed-parts/drain-readiness/prints/2026-10-08-current-back-top-mark1/physical-result.json. "I've yet to see bambu's auto put a normal support in an impossible to remove place". Stated.
3. Where no tool reaches, print support-free: teardrops, bridges with two full landings. E/prints/2026-11-05-back-top-smooth-corners-mark2/physical-result.json. "The bulkhead holes on the back, why aren't those teardrop shaped?" Stated.
4. A round expanding off the bed becomes a chamfer tangent to it: 0.5 mm out per mm up, normal layers, six local walls. NSR/2026-09-24-tee-carrier-plate-mark2-v12; NSR/2026-09-29-tee-chamfer-h2c-v6; @d8d50f9a5 ENC/tee-carrier/physical-acceptance.json. "That turned out worse. Exploded basically." Show rounds. Stated.
5. Fine layers only on inward/top show rounds, through the whole curve, never over support. E/print-log.md (09-21 to 09-24); NSR/2026-10-03-enclosure-front-top-current-h2c-v17/physical-result.json. "thin layers create a visible artifact that should only be used when absolutely necessary". Stated.
6. Remove the overhang before tuning its support. Same v17 record: "all of these problems go away if we simply don't have an overhang here". Stated.
7. Fill unreachable voids solid; saving material is not a goal. 98f4736f2: "Why stop printing the slab? Why not carry it forever up?" R/hardware/printed-parts/AGENTS.md. Stated.
8. Orientation is a datum. Back-top was tilted 11-06 (b222fcc32), then: "Restore our correct print orientation and fix the support problems the right way" (c91ec3569). Stated.
9. Reinforcement modifiers change infill only; wall overrides printed tracks on both faces of a show wall. R/hardware/printed-parts/drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/physical-result.json. Stated.
10. With manual supports every underside is yours. E/prints/2026-11-10-back-top-D-mark1/physical-observation/physical-observation.json: "loops are falling down". Stated.
11. A coupon's easy cleanup does not transfer to a walled part: "I can't reach in that far" (11-05 record). Stated.
12. Beads, brim and trees included, stay 20 mm inside an unseasoned plate's edge. c6c6a0c59: "that plate is not well seasoned there yet". Stated.

D. BASICS
3 mm minimum section; 9 mm flanks and front wall. 45° for every relief. Vertical bores round; horizontal bores teardrops pointing up the build. Clearance 0.15 static, 0.25 sliding, +0.25 per supported face, +0.10 at a cavity floor: "An allowance is surface, not air" (ENC/clearance-audit.md); "SEATING FACES ARE NOT EXEMPT FROM THE RULES!" Two walls, 15 % gyroid, 100 % zig-zag in insert hosts and seam roots. Heat-set pilots to the Ruthex table. One watertight body per piece, inside 325 x 320. Flutes exist only in the STL.

E. PICTURES
1. GA/rail-release.jpg (original R/hardware/print-tests/petgf-dense-roofs/rail-fit-30/photos/01-whole-support-release.jpg): rail tree and roof out as one piece.
2. GA/front-rail-section.png, GA/front-bottom-section.png, GA/front-bottom.png: catch and floor; corbel; whole piece.
3. CH/2026-11-09-0213-grip-corbels/handhold-before.webp, handhold-after.webp.
4. @aab7f24fec ENC/tee-carrier/physical-observations/2026-09-24-v12/IMG_7847.jpeg: spaghetti on a print-bottom round; 2026-09-24-v11/IMG_7842.jpeg; lesson 4.
5. NSR/2026-09-29-tee-chamfer-h2c-v6/bottom-profile.png: chamfer diagram.
6. E/prints/2026-11-10-back-top-D-mark1/physical-observation/photo-1.jpg: loops under an unsupported ledge; lesson 10.
7. CH/2026-11-06-1259-rear-support-access/covered-bores-before.webp, covered-bores-after.webp: round to teardrop.
8. R/hardware/printed-parts/drain-readiness/prints/2026-10-10-current-back-top-bridge50-mark1/physical-xplus-reinforcement-tracks.jpg; lesson 9.
9. R/web/public/update-images/2026-09-25-front-top.png: the only committed photo of a printed quadrant I found.

F. SURPRISES
- The cleanest piece keeps two supports, model-rooted with the shortest build-up, which the September audit scored as defects.
- Finer layers and less fan both made the bottom round worse.
- The reeded skin is a printing decision: vertical grooves cost nothing, put the Y seam in a groove's shadow and are the vent grille.
- Clearance follows print orientation: the same rail joint is 0.50 mm in front, 0.75 mm behind.

G. GAPS
- No physical result is recorded for the 11-11 front-bottom or the corbelled grips. "Precisely one pair of supported faces" is not in the repo verbatim.
- R/hardware/printed-parts/lint-answers/enclosure/enclosure/enclosure-front-bottom.lint-answers still defends flat grip ceilings; E/README.md's support table describes October STLs (four bodies).
- Back-bottom forces support under the handhold arch that front-bottom's mirrored arch prints bare.
- E/heat-set-review/README.md says Ø5.6 M5 holes; the catalog and the 10-26 selection say 5.2.
- The seam band's root is steeper than the 0.5:1 chamfer rule and has no print result.
- Photos for the 11-05 back-top and front-top feedback are cited at /tmp paths that no longer exist.
- R/calibration/Principle.md, which a repo hook pointed me to when I drafted this, says "any rule is better encoded as an example"; a rules-first guide sits in tension with it.
