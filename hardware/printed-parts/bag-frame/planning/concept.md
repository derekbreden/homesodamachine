# Bag Frame — Conceptual Architecture

**Date:** 2026-03-29
**Inputs:** requirements.md, vision.md, synthesis.md, design-patterns.md, platypus-bag-geometry.md, structural-analysis.md
**Next step:** specification (per-part geometry definitions, dimensioned drawings)

---

## Resolved Geometry: Rear-Wall Clearance

The synthesis flagged a potential conflict: at 35°, the 350 mm bag flat length projects to 287 mm front-to-back. The cap pocket adds ~50 mm along the bag axis. The conflict assumed the cap pocket added 50 mm of horizontal depth on top of the 287 mm projection. This is incorrect.

The 50 mm cap pocket is measured along the bag axis — it is already part of the bag's total flat length of 350 mm. The 287 mm horizontal projection is calculated from the full 350 mm length: 350 × cos(35°) = 287 mm. The cap pocket is not additive. It is the lower portion of that 287 mm span.

**Resolved geometry:**

| Dimension | Value |
|---|---|
| Bag total flat length | 350 mm |
| Horizontal projection at 35° | 350 × cos(35°) = **287 mm** |
| Vertical projection per bag | 350 × sin(35°) = **201 mm** |
| Enclosure depth | 300 mm |
| Rear clearance (projection to back wall) | 300 − 287 = **13 mm** |

The 13 mm rear clearance accommodates: 2 mm cradle rear wall + tube exit routing. The tube from the Platypus cap is 1/4" OD hard tubing + John Guest fitting (body OD ~12 mm). The tube cannot exit straight backward from the cap into 13 mm of clearance — the fitting alone is 12 mm. The tube must make a 90° bend within the cap pocket and exit laterally or downward before reaching the rear wall. This is achievable: the cap pocket rear face gets a 10–12 mm clearance hole sized for the fitting body, and the tube is routed at a right angle immediately after the fitting before running along the enclosure floor toward the rear outlets. The 13 mm clearance to the enclosure rear wall accommodates the cradle rear wall (2 mm) plus the tube pressed against the back of the pocket without the fitting protruding beyond it.

The cap pocket is not a separate volume overhanging the back wall. It is the deepest region of the cradle, occupying the lower-rear portion of the same 287 mm projected span. No geometry change is required.

**This conflict is closed.** The 35° angle stands. The enclosure depth accommodates the full bag projection. Tube routing requires a 90° bend at the cap end — this is standard for John Guest fittings and requires no special geometry beyond the pocket clearance hole.

---

## 1. Piece Count and Split Strategy

**Five printed part types, all unique designs, producing five printed instances:**

| Part | Unique designs | Printed instances | Rationale |
|---|---|---|---|
| Spine | 1 | 1 | Primary structural element; spans full enclosure width |
| Cradle platform | 1 | 2 | Both bags are identical orientation; same file, print twice |
| Upper cap | 1 | 2 | Identical to each other; same file, print twice |

This is the synthesis's proposed 3-design / 5-instance structure. Confirmed. No modifications.

**Why these splits and not others:**

The spine must be a single part. It is the unifying visual element — the thing that makes two bag positions read as one mechanism. Splitting it (e.g., two half-spines) would break the visual continuity that the design-patterns research identifies as essential. It also serves as the primary enclosure interface: the spine snaps to both enclosure halves, making it the structural backbone of the entire upper zone.

The cradle platforms are separate from the spine because: (1) a cradle integrated into the spine would make the spine enormous and unprintable as one part; (2) separate identical cradles allow the spine to be designed for its structural role while the cradle is optimized for its contact role; (3) if constrained midsection thickness requires a design revision after empirical measurement, only the cradle design changes, not the spine.

The upper caps are separate from the cradles because caps must be assembled after the bag is placed. There is no other way to load the bag from above.

**Print bed fit verification (single nozzle: 325 mm × 320 mm × 320 mm):**

- Spine: spans 220 mm (enclosure width) in the X direction. Along the bag axis direction, the spine's footprint depends on its depth — it carries the two cradle attachment rails plus the front-edge fold-clip features. The spine depth along the enclosure's front-to-back direction is approximately 30–40 mm (it is a bracket, not a plate). Printed with the 220 mm span along the X axis: 220 mm × ~40 mm × ~60 mm tall. Comfortably within 325 × 320 × 320 mm. The spine's 220 mm dimension leaves 105 mm margin on the 325 mm axis.

- Cradle platform: the cradle is ~287 mm long (along bag axis), ~196 mm wide (inner lip span), ~35 mm deep (floor to lip top, including rib underside). Printed face-up (convex down on bed): bed footprint is approximately 196 mm × 287 mm. This fits within 325 × 320 mm with 129 mm and 33 mm margin on each axis respectively. The 287 mm dimension is the tightest fit — it requires the cradle's long axis to run along the printer's 320 mm axis. It fits with 33 mm to spare.

- Upper cap: the cap is ~196 mm wide and ~287 mm long, ~8 mm thick (face + ribs). Printed face-down: bed footprint ~196 mm × 287 mm. Same fit as the cradle: 33 mm margin on the 320 mm axis.

All parts fit the single-nozzle build volume. No dual-nozzle mode required.

---

## 2. Join Methods

### Cradle Platforms to Spine

Each cradle platform connects to the spine at its inboard long edge (the edge that faces the center of the enclosure / the spine face).

**Interface geometry:** Four snap tabs per cradle, integrated into the inboard edge of the cradle platform. The tabs engage horizontal slots in the spine face. The tabs flex in the Y/Z plane (in-plane with the cradle's layer lines when printed face-up), satisfying the requirements.md flex-direction constraint.

**Tab specification:**
- 4 tabs per cradle, spaced along the inboard edge at approximately 60 mm intervals across the supported length
- Tab body: 8 mm wide, 2 mm thick, 15 mm long (cantilever from cradle wall)
- Hook: 1.2 mm height, 30° lead-in, 90° retention face — permanent assembly
- Mating slot in spine face: 8.2 mm wide (0.2 mm sliding clearance), 15 mm deep, open at top for assembly from above
- The cradle is offered to the spine from above (along the enclosure's vertical axis) and pressed down until all four tabs click into their slots simultaneously. The tabs flex in the Y/Z plane as they cam over the slot entry; the 30° lead-in tolerates ±3 mm of lateral placement error during assembly.
- Once clicked, the 90° retention face prevents the cradle from pulling away from the spine. The cradle is captive.

The cradle's outboard long edge (toward the enclosure side wall) contacts a locating ledge on the enclosure inner wall — a 3 mm × 3 mm ridge that the cradle edge sits against, preventing lateral rotation. This is a contact locator, not a snap; the snap tabs at the inboard edge provide all retention.

### Upper Caps to Cradle

Each upper cap connects to its cradle by four horizontal snap arms: two arms on each long edge of the cap, one near each end of the cap body.

**Snap arm geometry (from structural analysis, confirmed):**
- 4 arms total per cap (2 per long edge)
- Arm length: 20 mm (from cap long edge to hook tip)
- Arm thickness: 2.0 mm (PETG; strain at 1.5 mm deflection = 1.1%, within 4% limit)
- Arm width: 6 mm
- Hook height: 1.2 mm
- Hook lead-in: 30° (cams arms outward on press-down)
- Hook retention face: 90° (perpendicular; permanent assembly)
- Root fillet: 1.0 mm

**Hook direction:** The arms extend outward from the cap's long edges in the horizontal plane (perpendicular to the bag's thickness axis). They hook over the outer face of the cradle side lip. The mating feature on the cradle is a horizontal ledge cut into the outer face of the side lip — a 1.2 mm × 1.2 mm rebate running along the lip at a height of 8 mm above the cradle floor. When the cap is pressed down onto the cradle, the arms cam outward past the lip top edge, then spring inward as the hook clears the lip and engages the rebate. The 90° retention face means the arm cannot cam back out without deliberate tool access.

**Access for disengagement:** The 90° hook face is permanent. The assembly is not intended to be opened. Per the service access strategy (Section 6 below), this is intentional.

**Engagement sequence:**
1. Cap offered from above, centered over cradle opening.
2. 30° lead-in on hooks contacts cradle lip top edge — 4 arms begin camming outward.
3. Arms reach maximum deflection (1.5 mm) as hooks cross the lip outer face.
4. Hooks clear the lip and drop into the rebate — tactile snap and drop, approximately 1.2 mm travel.
5. Cap face contacts bag, caps seats fully — firm stop.

The user experiences: approach resistance → snap drop → stop. Three events, unambiguous.

### Fold-End Restraint (Top of Bag Against Front Wall)

The folded top end of each bag — a flat 190 mm wide strip, 3–8 mm thick when folded — is captured by two features:

**Front-face slot integrated into the spine:** The spine's front face (the face that will be against or near the enclosure front wall) carries two horizontal slot features, one per bag position, at the height corresponding to each bag's fold end. Each slot is:
- 195 mm wide (190 mm bag width + 5 mm total clearance)
- 20 mm tall (accommodates the 15–20 mm seal band)
- 10 mm deep (slot depth into the spine front face; 5 mm is sufficient for retention per geometry research, 10 mm provides positive capture and prevents the fold end from drifting forward as the bag empties)

The bag fold end slips into the slot from above during assembly. Once the upper cap is clicked closed and the bag is constrained across its full length, the fold end cannot migrate out of the slot. The slot is a gravity-and-constraint retainer, not an active latch.

The enclosure front wall itself provides the vertical backing surface: the fold end is pressed flat against the front wall, and the slot captures it in the fore-aft direction. The front wall is not a structural part of the bag frame mechanism; it simply provides the vertical datum that the fold end rests against.

### Spine to Enclosure Walls

The spine snaps permanently to both enclosure halves. This is the first assembly step and is not intended to be reversible.

**Snap interface geometry:** Two snap posts per enclosure half, four posts total, integrated into the spine ends. Each post is a 10 mm × 6 mm oval cross-section feature protruding 8 mm from the spine's end face. It engages a matching oval slot in the enclosure half's inner wall. The slot has a 1.5 mm retaining rim that the post's hook flange engages.

- Post location: one post at the upper portion of the spine end, one at the lower portion, separated vertically by approximately 40 mm. This gives two-point contact per side, resisting rotation.
- The hook flange on each post is a 1.5 mm circumferential ridge with a 30° lead-in and 90° retention face.
- Assembly direction: the enclosure halves are brought together from the sides (in the X axis), pressing the spine posts into the enclosure wall slots. The snap engagement is in the X direction — this is the enclosure assembly direction, so spine engagement is simultaneous with enclosure half closure.

The spine is thus captured by four posts (two per side) and cannot be removed without destroying the enclosure — consistent with the vision's permanent-assembly enclosure architecture.

---

## 3. Seam Placement

**Spine-to-cradle seam:**

This seam runs along the inboard long edge of each cradle platform — the joint where the cradle's inboard wall meets the spine face. The seam is on the interior of the enclosure, visible only when the enclosure is open for initial assembly.

Treatment: a 1.5 mm reveal. The cradle inboard wall stops 1.5 mm short of flush with the spine face. The spine face carries a 1.5 mm step (a shallow shoulder) that the cradle wall butts against, creating a deliberate shadow line. The seam reads as "cradle seated in spine recess" rather than "two surfaces meeting." This matches the design-patterns guidance (1.5–2 mm reveal) and is consistent with the Nespresso CitiZ precedent of interior surfaces being finished as if seen.

The reveal direction: the spine face is proud by 1.5 mm relative to the cradle inboard wall. From the front, looking into the assembled mechanism, the spine face is the dominant surface and the cradle sits into it. This reinforces the visual hierarchy: spine first, cradle positions second.

**Cap-to-cradle seam:**

This seam runs along both long edges of the upper cap, where the cap's perimeter edge meets the cradle side lip top edge.

Treatment: per the synthesis and design-patterns research, the cap's perimeter edge sits 1.5–2 mm above the cradle lip top edge when locked. This is a deliberate proud step — the cap reads as a component that has engaged a housing. The step is uniform around the full cap perimeter (both long edges), making it read as intentional rather than as a tolerance accumulation artifact.

The 1.5 mm value is used (lower end of the 1.5–2 mm range) because the cap perimeter is narrow (the snap arms are at the long edges, and visual clarity is adequate at 1.5 mm).

**All seams are interior-only.** The assembled enclosure has no exterior seams from the bag frame mechanism. When the enclosure halves are joined, the only visible seams are the enclosure-half seam, which is a separate design concern.

---

## 4. User-Facing Surface Composition

The bags are loaded at initial assembly and are never accessed again in normal use. The vision explicitly states the enclosure is snap-shut permanently. Under normal use, no bag frame surface is ever seen by the user.

However, two scenarios expose bag frame surfaces:

1. **Initial owner/factory assembly.** All surfaces of the spine, cradles, and caps are visible during this step. The person assembling the machine sees all interior surfaces.

2. **Any repair or inspection.** Not a specified use case, but cannot be excluded entirely.

**Appliance quality interior standard for this mechanism:**

The bag frame interior is held to the same standard as the rest of the machine: all surfaces that could be seen have a defined surface language, no surface reads as the back side of a functional feature, and the assembly looks like it was designed intentionally from the inside out.

Specifically:
- The spine's front face (visible between the two bag positions when looking into the assembly) carries the rib language defined in Section 5.
- The cradle platform's inner bowl surface (the lens face the bag rests on) is smooth. No ribs on the bag-contact surface. Smooth bowl surfaces are the design language for contoured support surfaces — ribs on this face would print with visible layer lines in a pattern that competes with the bag film and would create stress concentrations on the bag seams.
- The cradle platform's outer/underside surface (not in contact with the bag) carries the longitudinal ribs for structural stiffening. These ribs are visible from below if looking under the mechanism. They are part of the design language — structural ribs visible on the underside of a bracket are an established appliance interior language (visible in the Nespresso CitiZ, Vitamix base, etc.).
- The upper cap's top surface (the rib side, facing away from the bag) carries the grid rib language. This face is visible when looking into the assembled mechanism from above. It reads as the stiffened back of a cover panel.
- The upper cap's bottom surface (the bag-contact face) is smooth and flat. Same reasoning as the cradle bowl surface: this face contacts the bag film and must not create stress concentrations.

"Appliance quality interior" here means: consistent surface language, no orphan surfaces, no visible layer lines on bag-contact faces (smooth face-down or face-up surface quality from print orientation), structural features that look like they belong.

---

## 5. Design Language

**Material and baseline:** PETG throughout. All surfaces at FDM minimum 0.1 mm layer height for visible faces.

**Corner treatment:**

- Interior corners (floor-to-lip on cradle inner face): **3 mm fillet radius.** This matches the midpoint of the 2–4 mm range from design-patterns guidance and is consistent with Nespresso CitiZ interior corner treatment. Below 2 mm reads as a manufacturing artifact; above 4 mm reads as soft. 3 mm is clean and intentional.
- Lip top edge (cradle outer lip, visible along the cradle perimeter): **1.5 mm fillet radius.** At the top end of the 1–1.5 mm range from design-patterns guidance. The lip top edge is a prominent visual feature — it is the perimeter of the bag containment zone. A 1.5 mm radius reads as a finished edge rather than a printed edge.
- Cap perimeter edge (outer visible edge of the upper cap): **1.5 mm chamfer.** Chamfer rather than fillet on the cap perimeter: the cap is the element the assembler presses down, and a chamfer provides a consistent visual cue to the engagement direction (the angled face catches light and reads as "press here"). The chamfer is on the outer face, not the lip-side.
- Spine face corners: **2 mm fillet radius** on all corners where the spine face transitions to spine side walls. Slightly tighter than the cradle interior corners because the spine faces are larger planar surfaces — a 3 mm fillet on a 40 mm wide face looks visually heavy.
- All external enclosure-snap post features: **1 mm chamfer on post entry edges** to guide alignment during assembly.

**Rib language:**

The design-patterns research establishes that ribs should run in one direction per surface, at consistent spacing, and that the rib language should be identical across parts — cradle underside, spine face, cap top all use the same rib height and spacing so they read as a family.

- **Spine front face:** Transverse ribs (running across the 220 mm width, perpendicular to the bag slope axis). Spacing: 10 mm. Height: 1.5 mm. Width: 0.8 mm. These are visual/stiffening ribs on a surface that will be visible between the two bag positions. Transverse orientation on the spine face creates a rhythm that is perpendicular to the bag slope direction — the eye reads the ribs as horizontal registers, reinforcing the sense of organized structure.

- **Cradle platform underside:** Three longitudinal structural ribs (running along the 287 mm bag axis). Height: 6 mm. Thickness: 1.6 mm. Spaced ~40 mm apart transversely. These are structural, not decorative — but they are a visible structural language. No additional decorative rib overlay.

- **Upper cap top face:** Grid rib pattern. Three longitudinal ribs + two transverse ribs. Height: 5 mm. Thickness: 1.2 mm. Spacing: ~40 mm longitudinal, ~55 mm transverse. The grid pattern on the cap top face is consistent with the cap being a stiffened panel — grids read as structural panels, not as decorative texture.

**Draft angles:** 1.5° draft on all vertical walls that are not functional mating surfaces. Required for print release; consistent with consumer appliance draft.

**Color:** PETG in a neutral interior color (matte black or dark gray to match the enclosure interior). No color contrast between parts — all bag frame parts are the same color, reinforcing that they are one mechanism.

---

## 6. Service Access Strategy

**Bag replacement is not a service event.**

The Platypus 2L bags are permanent fixtures, explicitly stated in requirements.md: "Nothing else is replaceable (e.g. the bags are permanent fixture the same as all other internal plumbing)." The cleaning cycle (requirements.md §3) uses the existing bag-to-pump-to-dispense pathway with tap water and air — no access to the bag or bag frame is required for cleaning.

The only assembly event for the bag frame is initial factory/owner assembly. This occurs once, during initial machine build. All snap connections (cradle to spine, cap to cradle, spine to enclosure) are designed as permanent 90° retention faces — they require tool-level force or deliberate destruction to disengage. This is not a limitation but an intentional design choice consistent with the appliance-grade assembly architecture.

The bag frame has no service access provisions. There are no access doors, no tool-release tabs, no reversible latches. The snap arms are designed for low-force assembly (13.5 N total for the upper cap — light thumb pressure) and high-force retention (90° hook: requires tool to release). Assembly is fast and certain; disassembly is not a supported operation.

**The only service event in the bag zone is pump cartridge replacement (requirements.md §4).** The pump cartridge is in the front-bottom of the enclosure, entirely separate from the bag frame mechanism. Pump cartridge service does not require opening the bag frame zone.

---

## 7. Manufacturing Constraints

### Spine

**Print orientation:** The spine spans 220 mm in the enclosure width axis (X). It is printed with this 220 mm dimension lying along the print bed's X axis. The spine's depth (front-to-back, approximately 35–40 mm) and height (spine bracket height, approximately 55–60 mm) both fit well within the build volume.

Orientation: the spine is printed with its front face down on the build plate. The front face is the visible face carrying the transverse ribs and the fold-end slots. Printing this face down gives it the best surface quality (build plate surface). The snap tabs on the cradle-mounting face are on the spine's rear face and are printed facing up as cantilever arms — no overhang violation because the snap slots open toward the top (assembly direction from above).

The enclosure snap posts protrude from the spine's two end faces. These are printed in the X/Y plane — they protrude in the X direction. With the spine lying on its front face, the posts protrude horizontally outward from the spine ends and print as walls in the X/Y plane without overhang.

The fold-end slots on the spine front face: when printed face-down, the slot interior is printed upward into the slot cavity. The slot is 10 mm deep (front-to-back, which is the Z direction when printing face-down). This creates a 10 mm tall cavity in the Z direction — no overhang, no bridge required, the slot walls simply converge toward the opening which faces upward during printing.

**Material:** PETG. No fiber reinforcement needed — the structural loads are low (11.5 N sliding, 16.5 N normal per bag, transmitted to the enclosure via four snap posts).

**Support requirements:** None required if orientation is as specified. All features either self-support or are oriented to build without overhang. The snap tab undercuts (1.2 mm hook height, 30° lead-in) are small enough that the 30° lead-in face is outside the 45° overhang limit — no support needed. The 90° retention face (hook underside) is a 0.4 mm–wide undercut at the hook tip. This can be designed with a 0.2 mm interface gap at the hook underside, creating a frangible connection to the tab body that breaks cleanly when the first assembly deflects the arm. This is the designed support geometry approach from requirements.md.

**Build volume check:** Spine footprint: 220 mm (X) × 40 mm (Y) × 60 mm (Z). Within 325 × 320 × 320 mm single-nozzle envelope. 105 mm margin on X, 280 mm margin on Y, 260 mm margin on Z.

### Cradle Platform (print 2 identical instances)

**Print orientation:** Face-up — the concave (bag-contact) surface faces upward during printing. The convex underside is on the build plate. This is required by geometry: the concave surface cannot be printed face-down without a continuous 190 mm overhang spanning the full bag width, which violates the 15 mm maximum bridge span from requirements.md.

With face-up orientation, the longitudinal ribs on the underside are printed as walls extending downward from the convex floor surface — they are on the build plate side. No: the ribs are below the floor. With face-up, the floor is the lowest printed surface (after the convex curve lifts off the bed), and the ribs are integral projections below the floor. These ribs print face-up as walls going upward. Wait — if the concave face is up and the convex underside is on the bed, then the ribs (which are on the underside) are also on the bed side. The ribs would need to be printed between the floor and the build plate, which means they hang below the floor — this is a downward projection into the build plate space, which is impossible.

**Correction:** The rib geometry requires clarification of which side is "up." The cradle is a lens-shaped bowl:
- The bag sits on the concave (inside, bowl) surface
- The ribs are on the convex (outside, bottom) surface

If printed concave-face-up: the convex bottom is on the bed, ribs point downward into the bed — ribs cannot be printed this way (they would print into the bed).

**Resolved orientation:** The cradle is printed with the convex underside up and the concave face down — BUT only if the lens shape allows this without excessive overhang. The concave face down would bridge across the full 190 mm width. This violates the 15 mm bridge limit.

**Correct resolution:** Print the cradle on its side — long axis vertical. The 287 mm length becomes the print height (Z). The cross-section (190 mm wide, 35 mm deep) lies in the X/Y plane. The lens profile builds up cross-section by cross-section. The longitudinal ribs are on the convex exterior surface, which faces outward in the X/Y plane and builds as normal vertical walls. The concave interior face also builds as normal vertical walls, with no overhang concern.

At 287 mm print height, this fits within the 320 mm Z limit of the single-nozzle printer with 33 mm margin.

With the cradle printed on its side, layer lines run perpendicular to the cradle's long axis. The bag's distributed load (pressing into the bowl surface) acts perpendicular to the cradle floor — which is now parallel to the layer planes (layers are in the X/Y plane, load is in the X/Y direction). This is actually the optimal orientation for load resistance: the normal load on the bowl surface is resisted by layers stacked parallel to that load direction, not across layer bonds.

The snap tabs on the inboard edge flex in the X/Y plane (the flex direction is along the cradle's width axis, which is in the X/Y plane when printed on-end). This satisfies the requirements.md constraint that snap-fit flex direction be parallel to the build plate.

**Support requirements:** Minimal. The side lips and snap tabs are vertical walls when printed in this orientation. The cap-end pocket is a recessed cavity in the lower end of the cradle — when printed on end with the cap end at the bottom, the pocket is a cavity that builds from its closed base upward. No overhang. The tube exit hole in the pocket rear wall is a circle printed with its axis horizontal — this creates a bridge across the hole. At 10–12 mm diameter, this is within the 15 mm bridge limit and requires no support.

**Material:** PETG.

**Build volume check:** Cradle on-end: 190 mm (X) × 35 mm (Y) × 287 mm (Z). Within 325 × 320 × 320 mm single-nozzle envelope. Print two in sequence or side by side in one print (combined footprint: 190 mm × 75 mm × 287 mm, still within envelope).

### Upper Cap (print 2 identical instances)

**Print orientation:** Face-down — the smooth bag-contact face is flat on the build plate. The rib grid is on top, printing as vertical walls and cross-walls upward from the face. This gives the best surface quality on the bag-contact face and requires no support for the rib grid.

The snap arms extend outward from both long edges of the cap in the X/Y plane. With the cap face-down, the arms are in the X/Y plane, extending horizontally. They flex in the X/Y plane — satisfying the requirements.md constraint. The hook undercut (1.2 mm at 90°) faces downward (toward the build plate). This undercut requires either a 0.2 mm interface gap to create a frangible support bridge at the hook tip, or a 45° chamfer on the undercut face. Since this is a permanent-assembly hook (90° retention), a 45° chamfer is not appropriate — it would reduce retention. The 0.2 mm interface gap approach is used: the hook tip is connected to the arm body by a 0.2 mm gap on the undercut face. The bridge prints thin and fragile; first deflection of the arm during assembly breaks it cleanly per requirements.md guidance.

**Material:** PETG.

**Support requirements:** One location requires the designed frangible bridge at each snap hook undercut (4 hooks × 1 per hook = 4 designed support features). No slicer-generated support needed.

**Build volume check:** Cap face-down: 196 mm (X) × 287 mm (Y) × 8 mm (Z). Within 325 × 320 × 320 mm. Print two in sequence or simultaneously side by side: combined footprint 196 mm × 290 mm (allowing ~3 mm gap between parts). Fits within 325 × 320 mm with 129 mm margin in X and 30 mm margin in Y.

---

## Summary

### Part List

| Part | Qty | Material | Print orientation | Approx print size |
|---|---|---|---|---|
| Spine | 1 | PETG | Front face down, 220 mm along X | 220 × 40 × 60 mm |
| Cradle platform | 2 (identical) | PETG | Long axis vertical (on-end), cap pocket at bottom | 190 × 35 × 287 mm |
| Upper cap | 2 (identical) | PETG | Bag-contact face down | 196 × 287 × 8 mm |

No hardware fasteners. Zero screws, zero bolts, zero inserts.

### Join Methods

| Interface | Method | Reversible |
|---|---|---|
| Spine to enclosure halves | 4 snap posts (2 per side), 90° retention | No |
| Cradle platform to spine | 4 snap tabs per cradle, horizontal insertion from above, 90° retention | No |
| Cradle outboard edge to enclosure side wall | Contact locating ledge on enclosure inner wall | N/A (contact only) |
| Upper cap to cradle | 4 horizontal snap arms per cap, hook over cradle lip rebate, 90° retention | No |
| Bag fold end to front-wall slot | Slip-fit into 10 mm deep slot in spine front face, retained by geometry | Assembly only |

### Assembly Sequence

1. Spine snaps into enclosure left half (2 posts engaged).
2. Enclosure right half closes around spine (2 posts engaged on right side). Enclosure is now closed and the spine is permanently captured.
3. Through the open top (before funnel is installed): two cradle platforms are pressed down into spine slots from above, one at each bag position. Four tabs per cradle click into spine face simultaneously.
4. Two filled Platypus bags are laid into their cradles from above, cap end first into the cap pocket, fold end toward the front wall slot.
5. Fold ends of both bags slip into the spine front-face slots.
6. Two upper caps are pressed down over the bags — four arms per cap cam over the cradle lip and snap into rebates. Tactile click confirms engagement.
7. Tube connections made at the cap ends (John Guest push-in fittings into the cap spout, tubes routed laterally within the pocket and along the enclosure floor to the rear outlets).
8. Funnel assembly mounts above (separate sub-assembly, not part of bag frame).

The entire bag frame step (steps 3–7) requires no tools and no fasteners. Each snap engagement produces an audible and tactile confirmation. The completed assembly is permanent and cannot be opened without destroying the enclosure.
