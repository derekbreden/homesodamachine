# Bag Cradle

See `bag-cradle-concept.md` for conceptual architecture and design rationale.
See `research/decision.md` for design decision and alternatives considered.
See `research/platypus-2l-geometry.md` for bag dimensions.

**Coordinate system:** Origin at exterior front-left-bottom corner of the tray (when tray is lying flat, not tilted). X = width (positive right, 0 to 206 mm). Y = length (positive toward back/cap end, 0 to 370 mm). Z = height (positive up, 0 to 30 mm).

---

## Mechanism Narrative

The bag cradle is a passive, single-piece tray. Nothing moves during normal operation. The user interacts with it during two operations: installing a bag and removing a bag. Both are described below.

**What the user sees and touches:**

The cradle is a shallow rectangular PETG tray, roughly the size and shape of a small baking sheet. It lives inside the enclosure, mounted on angled rails so the cap end (back, +Y) sits lower than the sealed end (front, -Y). The user sees the tray interior: a smooth, gently concave floor with low sidewalls on three sides. The fourth side (cap end, +Y) is open, with a semicircular notch where the bag's spout exits. The exterior underside has lateral mounting tabs along the long edges and a tube routing clip near the cap end.

**What moves:**

During bag installation and removal, the tray slides along the enclosure's rail channels in the Y direction (front-to-back). The tray translates; the enclosure is stationary. During normal operation (bag installed, dispensing), nothing moves. The bag rests in the tray under gravity. The tray is held stationary by the rail detent barbs.

**What constrains the tray:**

The tray is constrained in all six degrees of freedom by the enclosure rail channels:
- Y translation: limited by the barb detents on each mounting tab clicking past corresponding detent ledges in the enclosure rail channels. The barbs engage at full insertion, preventing the tray from sliding out under the bag's weight. The barb face angle (45-degree lead-in, 90-degree retention face) means passive loads along Y cannot disengage the tray.
- X translation: the tab inserts 5.0 mm into the 5.0 mm deep channel; the remaining 1.0 mm of tab width stays outside the channel as a lateral stop. The channel end wall prevents further inward motion. The sidewall exterior prevents outward motion.
- Z translation: the tab body (2.8 mm thick) fits within the channel slot opening (3.2 mm tall), leaving 0.2 mm clearance per side. The lower channel surface supports the tab; the upper channel surface prevents uplift.
- Rotation about all axes: two rails, one on each side, 206 mm apart (the tray exterior width), prevent any rocking or twisting.

**What provides the return force:**

There is no return force. The tray is either fully inserted (locked by barb detents) or fully removed (in the user's hands). There is no spring, detent valley, or mechanism pushing the tray to a rest position. The user pushes it in until it clicks; the user deflects the tabs inward and pulls it out.

**What is the user's physical interaction:**

*Installation:*
1. User holds the tray by the sidewalls at the front (sealed) end.
2. User aligns the left and right mounting tabs with the enclosure rail channel openings at the enclosure front.
3. User slides the tray rearward (+Y direction) along the rail channels. The 45-degree lead-in chamfer on each barb rides up the channel wall as the tray moves inward. The tab deflects inward (toward tray center, -X on left, +X on right) by approximately 1.0 mm as the barb passes the channel detent ledge.
4. At full insertion, each barb snaps past the detent ledge. The tab springs back outward (+X on left, -X on right) and the 90-degree retention face of the barb seats behind the detent ledge. The user hears and feels a click (the snap of the 2.8 mm PETG tab returning to its undeflected state after 1.0 mm of elastic deflection).
5. The tray is now locked. The bag can be laid in from above (if clearance exists) or the bag can be pre-loaded before sliding the tray in.

*Removal:*
1. User pinches both sidewalls inward (squeezing toward tray center) to deflect the mounting tabs inward by ~1.0 mm, clearing the barbs from behind the detent ledges.
2. User slides the tray forward (-Y direction) and out of the enclosure.

---

## 3D Printed Part: Bag Cradle Tray

- **Type:** 3D printed
- **Material:** PETG
- **Quantity:** 2 (identical parts, one per flavor bag)
- **Print orientation:** open-side-up (tray sitting normally on bed, +Z up)
- **Supports:** none required
- **Bed placement:** diagonal (~40 degrees on the 325 x 320 mm bed; tray diagonal ~425 mm fits within bed diagonal ~456 mm)

### Overall Envelope

- **Exterior envelope:** 206.0W (X) x 370.0L (Y) x 30.0H (Z) mm (excludes mounting tabs)
- **Envelope with tabs:** 218.0W (X) x 370.0L (Y) x 30.0H (Z) mm (tabs add 6.0 mm per side)
- **Interior tray volume:** ~200.0W x 367.0L x 23.0-27.0H mm (usable bag space; L measured from front wall interior face at Y=3 to cap end at Y=370; H varies from 23 mm at sidewall edges to 27 mm at floor center due to concavity)

### Walls and Floor

- **Floor thickness:** varies from 3.0 mm at center to 7.0 mm at sidewall edges (exterior underside is flat at Z = 0; interior surface is concave, see below)
- **Floor profile (cross-section in X-Z plane):** gently concave arc across the 200.0 mm interior width. The concavity is a circular arc segment with a sagitta (center depth) of 4.0 mm. The floor interior surface at the sidewall bases (X = 3.0 and X = 203.0) is at Z = 7.0 mm. The floor interior surface at center (X = 103.0) is at Z = 3.0 mm. The floor exterior (underside) is flat at Z = 0. This means the floor is 7.0 mm thick at the edges (where it meets the sidewalls) and 3.0 mm thick at the center. This produces a shallow dish that centers the bag laterally.
- **Floor profile (along Y):** flat (no curvature along the length). The concave cross-section is constant from Y = 3.0 mm (interior face of front wall) to Y = 355.0 mm (the start of the spout notch zone).
- **Left sidewall:** exterior face at X = 0, interior face at X = 3.0 mm. Thickness: 3.0 mm. Height: from Z = 0 to Z = 30.0 mm.
- **Right sidewall:** interior face at X = 203.0, exterior face at X = 206.0 mm. Thickness: 3.0 mm. Height: from Z = 0 to Z = 30.0 mm.
- **Sidewall visible height above floor:** the floor meets the sidewall at Z = 7.0 mm (top of the fillet zone). The sidewall top is at Z = 30.0 mm. So the sidewall rises 23.0 mm above the interior floor surface at the edges.
- **Sidewall draft angle:** 3 degrees outward (top of sidewall is 1.4 mm wider than base on each side, easing bag placement). At Z = 30.0 mm, the interior width opens from 200.0 mm to approximately 202.8 mm.
- **Front end wall (Y = 0):** 3.0 mm thick, full height (Z = 0 to Z = 30.0 mm), spans full width (X = 0 to X = 206.0 mm). Interior face at Y = 3.0 mm. The sealed end of the bag rests against or near this wall.
- **Cap end (Y = 370.0):** NO end wall. The tray is open at this end. The floor extends to Y = 370.0 mm and terminates. See spout notch below.
- **Interior fillet radius:** 3.0 mm at all interior floor-to-wall junctions and floor-to-front-wall junction (reduces stress concentration, eases cleaning, smooth transition from concave floor to vertical walls)

### Spout Notch

The cap end of the tray floor has a semicircular notch centered on the tray width. This notch accommodates the Platypus 28 mm threaded spout collar, allowing the spout and tubing to exit the tray downward when the tray is tilted.

- **Notch shape:** semicircle, open toward +Y (the cap end)
- **Notch diameter:** 34.0 mm (provides 3.0 mm clearance around the ~28 mm spout collar)
- **Notch center:** X = 103.0 mm (tray centerline), Y = 355.0 mm
- **Notch depth through floor:** full floor thickness (the notch is a through-cut in the floor, Z = 0 to Z = 3.0 at the floor baseline, following the concave profile)
- **Notch edge treatment:** 1.0 mm chamfer on the top edge of the notch (prevents sharp edges from contacting the bag film or spout)

The floor between Y = 355.0 and Y = 370.0 exists only as two flanking sections on either side of the notch (each ~83.0 mm wide), providing structural continuity for the sidewalls and mounting tabs in this zone.

### Mounting Tabs (Snap-Fit Rail Interface)

Two identical mounting tabs, one on each long side (left and right), run nearly the full length of the tray. These tabs slide into horizontal rail channels on the enclosure interior walls.

- **Tab location (left):** extends from the left sidewall exterior face (X = 0) outward to X = -6.0 mm. Runs from Y = 10.0 to Y = 360.0 mm (350.0 mm long, inset 10.0 mm from each end to clear the front wall corner and the cap end termination).
- **Tab location (right):** mirror of left tab, extends from the right sidewall exterior face (X = 206.0) outward to X = 212.0 mm.
- **Tab cross-section (X-Z plane):**
  - Body: 6.0 mm wide (X direction) x 2.8 mm thick (Z direction). The tab extends horizontally outward from the sidewall with its bottom surface at Z = 0 (flush with the tray floor underside) and top surface at Z = 2.8 mm.
  - Barb: on the underside of the tab body, near the outer edge. The barb is a triangular ridge:
    - Barb height: 0.8 mm (extends downward from tab underside, from Z = 0 to Z = -0.8 mm)
    - Barb position: outer 2.0 mm of the tab width (the outermost 2.0 mm of the 6.0 mm tab)
    - Barb lead-in face: 45-degree chamfer (the face that contacts the rail channel wall during insertion, ramping the tab inward)
    - Barb retention face: 90 degrees (vertical face, perpendicular to the Y axis, preventing the tab from sliding back out under passive load)
  - Tab top surface: flat at Z = 2.8 mm
  - Tab bottom surface: flat at Z = 0, except where the barb protrudes down to Z = -0.8 mm

- **Barb detent positions:** each tab has two barb detent bumps (not a continuous ridge) to reduce insertion force while maintaining retention:
  - Front detent: centered at Y = 100.0 mm, 20.0 mm long (Y = 90.0 to Y = 110.0)
  - Rear detent: centered at Y = 280.0 mm, 20.0 mm long (Y = 270.0 to Y = 290.0)
  - Between and beyond the detents, the barb ridge is absent (tab underside is flat at Z = 3.0 mm)

- **Tab flexibility:** the 6.0 mm wide, 2.8 mm thick PETG tab can deflect inward ~1.0 mm elastically when the user squeezes the sidewalls. This deflection clears the 0.8 mm barb past the enclosure detent ledge. The tab acts as a cantilever beam anchored at the sidewall.

### Enclosure Rail Channel Interface (Mating Geometry)

The enclosure must provide matching rail channels. These dimensions define the interface contract:

- **Channel slot height (Z opening):** 3.2 mm (accommodates 2.8 mm tab thickness with 0.2 mm clearance per side)
- **Channel slot depth (X, into wall):** 5.0 mm (accommodates the 6.0 mm tab width minus the 1.0 mm that remains outside as a lateral stop)
- **Channel slot length:** 360.0 mm minimum (from enclosure front opening to rear wall, must accept the 350.0 mm tab)
- **Detent ledge:** a 0.8 mm step on the lower channel wall at the fully-inserted position, matching each barb detent. The barb retention face (90 degrees) seats behind this ledge.
- **Channel angle:** the channels are molded into the enclosure walls at the 15-20 degree mounting angle. The tray inserts horizontally from the front of the enclosure; the channel geometry determines the tray's installed tilt angle.
- **Channel vertical position:** determined by enclosure design (two sets of channels, vertically staggered for upper and lower cradles)

### Tube Routing Clip

A printed clip on the tray underside near the cap end routes the silicone tubing from the bag spout along the tray structure, preventing unsupported spans that could snag or kink during bag installation.

- **Clip location:** centered on the tray underside at X = 103.0 mm (centerline), Y = 350.0 mm (just forward of the spout notch center)
- **Clip type:** open C-clip (a printed arc that the tube snaps into from below)
- **Clip inner diameter:** 7.0 mm (accommodates 6.35 mm OD silicone tubing with ~0.3 mm clearance per side)
- **Clip wall thickness:** 1.5 mm
- **Clip outer diameter:** 10.0 mm
- **Clip opening width:** 4.5 mm (less than the 6.35 mm tube OD, so the tube must be pressed past the clip arms to snap in; the PETG arms flex ~1.0 mm each to admit the tube)
- **Clip height (Z direction, below tray floor):** 10.0 mm (extends from Z = 0 downward to Z = -10.0 mm)
- **Clip arc extent:** 270 degrees (open 90-degree gap facing downward, -Z direction)
- **Attachment:** integral with the tray floor (printed as part of the tray in the same operation; the clip prints as a short vertical column with an arc — no supports needed since the opening faces down and the arc overhangs are within 45 degrees)

### Print Specifications

- **Layer height:** 0.2 mm
- **Infill:** 15-20% (gyroid or grid)
- **Walls:** 3 perimeters
- **Floor/ceiling:** 3 layers top, 3 layers bottom (0.6 mm solid skin)
- **Material:** PETG (bed 70-80C, nozzle 230-250C per H2C standard profile)
- **Estimated print time:** 3-4 hours per tray
- **Estimated mass:** ~120-150 g per tray

---

## Purchased Parts

None. The bag cradle is a single printed part with no purchased components. The Platypus 2L bag and silicone tubing are separate system components, not mounted to the cradle.

---

## Dimensional Summary Table

| Parameter | Value | Source |
|-----------|-------|--------|
| Tray exterior width (X) | 206.0 mm | Bag width 190 mm + 10 mm interior clearance + 2x 3.0 mm walls |
| Tray exterior length (Y) | 370.0 mm | Bag length 350 mm + 10 mm clearance + 10 mm spout extension |
| Tray exterior height (Z) | 30.0 mm | Concept: sidewalls 25-30 mm |
| Floor thickness (center) | 3.0 mm | Concept: 2.5-3 mm |
| Floor thickness (edges) | 7.0 mm | 3.0 mm base + 4.0 mm sagitta |
| Sidewall thickness | 3.0 mm | Concept: 2.5-3 mm |
| Floor concavity sagitta | 4.0 mm | Concept: 3-5 mm dish |
| Interior width | 200.0 mm | 190 mm bag + 10 mm clearance |
| Interior length | 367.0 mm | Y=3 (front wall interior) to Y=370 (cap end) |
| Spout notch diameter | 34.0 mm | 28 mm spout + 6 mm clearance |
| Mounting tab width | 6.0 mm | Derived from rail channel depth |
| Mounting tab thickness | 2.8 mm | Concept: 2.8 mm |
| Barb height | 0.8 mm | Concept: small barb |
| Tube clip inner diameter | 7.0 mm | 6.35 mm tube OD + 0.65 mm clearance |
| Bag weight (filled) | ~2,037 g | Platypus geometry doc |
| Bag width | 190 mm | Manufacturer spec |
| Bag length | 350 mm | Manufacturer spec |
| Bag filled thickness | 40-50 mm | Calculated estimate (MEDIUM confidence) |
| Spout collar OD | ~28 mm | Industry standard |
| Silicone tubing OD | 6.35 mm (1/4") | Requirements (1/4" tubing system) |

---

## Assembly Sequence

### Cradle into Enclosure

1. Orient the tray with the open cap end (+Y) pointing away from you.
2. Align the left and right mounting tabs with the rail channel openings on the enclosure interior walls.
3. Slide the tray rearward (+Y) into the channels. The 45-degree barb lead-in chamfers ride along the channel walls.
4. Continue sliding until both barb detents click past the enclosure detent ledges. The tray is now locked.

### Bag into Cradle (tray installed in enclosure)

1. Hold the bag by the sealed end (the end without the spout).
2. Lower the spout end into the tray, guiding the spout through the semicircular notch at Y = 355.
3. Lay the bag body down into the concave tray floor.
4. Route the silicone tubing from the spout downward, snapping it into the tube routing clip on the tray underside.
5. Connect the tubing to the downstream quick-connect fitting.

### Bag Removal

1. Disconnect tubing from the downstream quick-connect.
2. Unsnap tubing from the tube routing clip.
3. Lift the bag by the sealed end. The spout slides out of the open notch.

### Cradle Removal from Enclosure

1. Squeeze both sidewalls inward to deflect the mounting tabs ~1.0 mm inward, clearing the barbs from behind the detent ledges.
2. Slide the tray forward (-Y) and out of the enclosure.

---

## Design Gaps

1. **DESIGN GAP: Bag filled thickness is a calculated estimate (40-50 mm), not a physical measurement.** The sidewall height of 27.0 mm above floor center is less than the bag's filled thickness. This is intentional (the concept states sidewalls contain the bag laterally but the bag bulges above the sidewalls), but the exact clearance above the sidewall top when installed should be verified with a physical bag. If the bag is thicker than 50 mm, the upper cradle may need more vertical clearance.

2. **DESIGN GAP: Enclosure rail channel angle (15-20 degree range) is not yet pinned to a single value.** The cradle geometry is independent of tilt angle (the tray is flat; the tilt comes entirely from the enclosure rail angle), but the enclosure parts.md must specify the exact angle. This specification assumes 15-20 degrees per the concept.

3. **DESIGN GAP: Tube routing from the clip to the pump/valve manifold is unspecified.** The clip captures the tube at the tray underside, but the path from the clip to the enclosure wall and then down to the manifold depends on the enclosure interior layout, which is not yet designed.

4. **DESIGN GAP: Upper vs. lower cradle vertical stagger distance is unspecified.** Both cradles are identical parts, but the enclosure must provide two sets of rail channels at different heights. The vertical offset between them depends on bag filled thickness (~50 mm) plus clearance, plus the funnel above, plus the pump below. This is an enclosure design constraint, not a cradle design constraint.

5. **DESIGN GAP: Enclosure interior width accommodation.** The tray body is 206 mm wide. With 220 mm enclosure exterior and ~3 mm enclosure walls, interior is ~214 mm. The tray fits (4 mm clearance per side), and the 6 mm mounting tabs enter the 5 mm deep rail channels cut into the enclosure walls. This geometry works but constrains the enclosure wall thickness to at least 5 mm where the rail channels are located (the channel is 5 mm deep into a wall that may be only 3 mm from the exterior). The enclosure wall in the rail zone must be thickened locally to at least 8 mm (5 mm channel + 3 mm remaining wall) or the channel must be recessed differently. This is an enclosure design constraint.

6. **DESIGN GAP: Diagonal print fit margin is tight.** The tray diagonal with tabs is approximately sqrt(218^2 + 370^2) = 430 mm. The bed diagonal is ~456 mm. This leaves ~26 mm total margin for brim/skirt. A test print of the bounding rectangle should confirm clearance before committing to single-piece printing.

---

## Related Documents

- **Conceptual architecture:** `bag-cradle-concept.md`
- **Design decision:** `research/decision.md`
- **Platypus bag geometry:** `research/platypus-2l-geometry.md`
- **Requirements:** `../../../requirements.md`
- **Vision:** `../../../vision.md`
