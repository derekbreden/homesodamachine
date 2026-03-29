# Spine — Parts Specification

**Version:** 1.0
**Date:** 2026-03-29
**Dimensional source:** spatial-resolution.md (sole authoritative source for all coordinates and dimensions)
**FDM constraint source:** hardware/requirements.md
**Assembly authority:** concept.md

---

## 1. Part Identification

| Field | Value |
|-------|-------|
| Part name | Spine |
| Version | 1.0 |
| Material | PETG |
| Instances | 1 |
| Print orientation | Front face down — the front face (Y=0, bearing ribs and fold-end slots) is flat on the build plate |
| Print envelope (X × Y × Z) | 220mm × 35mm × 245mm |
| Build plate footprint | 220mm (X) × 35mm (Y) |
| Print height | 245mm |
| Fits single-nozzle volume | Yes — 220mm ≤ 325mm (X); 35mm ≤ 320mm (Y); 245mm ≤ 320mm (Z) |

**Height resolved to 245mm:** spatial-resolution.md §9 Open Flag 1 recommends 245mm for structural margin. The upper fold-end slot top edge is at Z=239.6mm. At Z=240mm only 0.4mm of material remains above the slot — below the minimum structural wall. At Z=245mm, 5.4mm of material is above the slot top. This document uses **245mm** as the spine height. All feature Z positions are unchanged; the additional 5mm is dead material above Z=240mm.

**Print orientation rationale:** Front face down gives the highest surface quality on the spine's visually dominant face (the rib face, visible between the two bag positions during assembly). In this orientation: ribs are the first printed features (rib tips contact the build plate at Z=−1.5mm in spine frame, equivalent to Z=0 in print frame). Fold-end slots open upward during printing — no overhang or bridging. Snap posts on the end faces protrude in ±X, printing as walls in the XY plane — no overhang. Tab slots on the rear face are open at the top of the print — no overhang.

---

## 2. Coordinate System

**Origin:** Corner where the front face (Y=0), left end face (X=0), and bottom face (Z=0) meet. This is the lower-left corner of the front face as viewed from the front of the spine (looking in the +Y direction).

| Axis | Zero point | Positive direction | Physical meaning |
|------|------------|-------------------|-----------------|
| X | Left end face | Right — toward right end face | Enclosure width; X=0 = left interior wall, X=220mm = right interior wall |
| Y | Front face | Rearward — toward rear face | Depth from front face toward enclosure back wall; Y=35mm = rear face |
| Z | Bottom face | Upward — toward top face | Enclosure vertical; Z=0 = spine base, Z=245mm = spine top |

**Part envelope:**

| Axis | Minimum | Maximum | Span |
|------|---------|---------|------|
| X | 0mm (left end face) | 220mm (right end face) | 220mm |
| Y | −1.5mm (rib tips protrude outward from front face) | 35mm (rear face) | 36.5mm |
| Z | −1.5mm (rib tips protrude below bottom front face edge) | 245mm (top face) | 246.5mm |

Note: The Y=−1.5mm and Z=−1.5mm extents are rib tips. The main body envelope is X: 0–220mm, Y: 0–35mm, Z: 0–245mm. Rib protrusion in −Y is outward from the front face toward the enclosure front wall. Rib protrusion in −Z is below the bottom edge of the front face — in print frame these are the first layers on the build plate, and in installed frame they are at the bottom of the spine below the lowest front face edge.

**Transform: print frame → installed frame.** The spine is installed with the same orientation it was printed. No rotation required. Print Z (upward from build plate) = installed Z (enclosure vertical, upward). Print Y=0 (build plate face) = installed Y=0 (front face, toward enclosure front wall). Print X = installed X (enclosure width).

---

## 3. Mechanism Narrative (Rubric A)

The spine is a rigid structural bracket. It does not move. It has no moving parts. It is assembled once into the enclosure and is never accessed again.

**What the spine is:** The spine is the structural and visual backbone of the bag frame zone. It is a single continuous part spanning the full 220mm interior width of the enclosure. From the front, it reads as the unifying element between the two bag positions — the thing that makes the bag zone read as one organized mechanism rather than two independent cradles.

**What holds the spine:** Four snap posts, two per end face, engage matching oval slots in the enclosure half inner walls. The posts engage as the enclosure halves close from left and right in the X direction. The 30° lead-in flange on each post cams into the enclosure slot; the 90° retention face locks the post permanently after closure. The spine cannot be removed without destroying the enclosure. It is captive.

**What the spine holds:** Two cradle platforms (one per bag position), snapped into the rear face via four tab slots each. The lower cradle's tabs engage slots L1–L4 at X=8mm. The upper cradle's tabs engage slots U1–U4 at X=212mm. The two cradles are installed from above; the slots are open at the top of the spine so tabs enter as the cradle descends, then click into retention at each slot's closed bottom wall. The spine also holds the fold ends of both Platypus bags in two front-face pockets (one per bag), each capturing the bag's flat heat-sealed strip against the enclosure front wall.

**How loads travel:** The Platypus bags (filled: ~20N each) bear on the cradle platforms. Cradle weight transfers through the snap tabs into the spine rear face slot walls. The spine body carries the combined ~40N load from both cradles as a distributed compressive and shear load across its 220mm width. The snap posts transfer this load laterally into the enclosure wall slots, which are structural features of the enclosure halves. Load exits the spine body at both ends simultaneously.

**Structural role of features:** The 35mm depth (Y) of the spine body provides the material thickness required for both the 10mm fold-end pocket (front face) and the 15mm tab slot (rear face) without breakthrough. The ribs on the front face are not structural (loads do not pass through them) — they are a design-language element. The snap posts are the only load-path exits from the spine to the enclosure.

**User interaction:** None in normal use. The user never sees or touches the spine. It is assembled once (either by the user or at the factory) and enclosed permanently. The only assembly event is the enclosure closure step (spine posts engage) and the cradle drop-in step (tabs click into slots).

---

## 4. Constraint Chain Diagram (Rubric B)

```
Bag contents × 2 (each ~20N at 35° from horizontal)
                    |
                    | Load transferred through bag film into cradle bowl surface
                    ↓
         Cradle platform floor (R=341mm arc, 2.0mm wall, 3 longitudinal ribs)
                    |
                    | Load transferred through 4 snap tabs per cradle
                    ↓
         Spine rear face tab slots (8.2mm × 2.2mm × 15mm deep, closed bottom)
                    |
                    | Load carried through spine body as distributed internal stress
                    ↓
         Spine body (220mm × 35mm × 245mm PETG block, features subtracted)
                    |
                    | Load exits laterally at both end faces through 4 snap posts
                    ↓
         Snap posts ×4 (10mm × 6mm stadium, 8mm protrusion, 1.5mm retention flange)
                    |
                    | Posts locked into enclosure half inner wall oval slots
                    ↓
         Enclosure walls (left half and right half, each carrying 2 post loads)
```

---

## 5. Feature List

### 5.1 Core Body

| Parameter | Value | Frame |
|-----------|-------|-------|
| Shape | Rectangular box | — |
| Width | 220mm | X=0 to X=220mm |
| Depth | 35mm | Y=0 to Y=35mm |
| Height | 245mm | Z=0 to Z=245mm |
| Material | PETG | — |
| Wall minimum (structural) | 1.2mm (3 perimeters at 0.4mm nozzle) — met everywhere: thinnest zone is rib width 0.8mm (visual ribs, non-structural, 2-perimeter minimum acceptable) | — |

**Body non-intersection verification (from spatial-resolution.md §7):**
- Front fold-end slots end at Y=10mm. Rear tab slots start at Y=20mm. Gap: 10mm of solid material. ✓
- Lower tab slots (L1–L4) at X=8mm and upper tab slots (U1–U4) at X=212mm — fully separated in X. ✓
- Highest tab slot top edge: U4 at Z=206.8mm. Upper fold slot bottom at Z=219.6mm. Gap: 12.8mm. ✓

---

### 5.2 Front Face — Transverse Ribs

**Location:** Y=0 face (front face). Ribs protrude outward in the −Y direction (toward enclosure front wall in installed orientation; toward the build plate in print frame).

**Profile:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Protrusion direction | −Y (outward from front face) | Spine Y |
| Protrusion height | 1.5mm | Y=0 to Y=−1.5mm |
| Rib width | 0.8mm (centered on Y=0, spanning Y=−0.4mm to Y=+0.4mm — wait: the rib protrudes outward from the front face, so the rib body is Y=−1.5mm to Y=0; it is centered at Y=−0.75mm. Width of 0.8mm means the rib body is from Y=−0.4mm to Y=+0.4mm relative to the front face surface. The rib sits flush with and protrudes from Y=0.) | Spine Y |
| Rib length | 220mm (full spine width; interrupted by fold-end slots — see below) | Spine X |
| Rib profile shape | Rectangular cross-section: 0.8mm (Y) × 1.5mm (Z protrusion in print frame) | YZ section |

**Rib spacing:** 22 ribs at 10mm pitch in X. First rib center at X=5mm, last at X=215mm.

**Complete rib X center table:**

| n | X center (mm) | n | X center (mm) |
|---|--------------|---|--------------|
| 0 | 5 | 11 | 115 |
| 1 | 15 | 12 | 125 |
| 2 | 25 | 13 | 135 |
| 3 | 35 | 14 | 145 |
| 4 | 45 | 15 | 155 |
| 5 | 55 | 16 | 165 |
| 6 | 65 | 17 | 175 |
| 7 | 75 | 18 | 185 |
| 8 | 85 | 19 | 195 |
| 9 | 95 | 20 | 205 |
| 10 | 105 | 21 | 215 |

**Rib Z extent:** Ribs run the full height of the front face from Z=0 to Z=245mm, interrupted where fold-end slots remove the front face. The two fold-end slots occupy X=12.5mm to X=207.5mm in X. Ribs at X=5mm (n=0) and X=215mm (n=21) are outside this X range and are continuous (Z=0 to Z=245mm, uninterrupted). All other ribs (n=1 through n=20, X=15mm to X=205mm) fall within the slot X range and are interrupted at both fold-end slot Z ranges.

**Rib Z segments for interrupted ribs (n=1 through n=20):**

| Segment | Z range | Length | Notes |
|---------|---------|--------|-------|
| Segment 1 | Z=0 to Z=159.6mm | 159.6mm | Below lower fold-end slot |
| Segment 2 | Z=179.6mm to Z=219.6mm | 40.0mm | Between lower and upper fold-end slots |
| Segment 3 | Z=239.6mm to Z=245mm | 5.4mm | Above upper fold-end slot |

**Micro-segment rule (from spatial-resolution.md §9 Open Flag 4):** Omit any rib segment shorter than 5mm. Segment 3 for interrupted ribs (Z=239.6 to Z=245mm) is 5.4mm — this is at the boundary. Because 5.4mm ≥ 5mm, it is retained. No segments are omitted under the 5mm rule when using the 245mm spine height. (At 240mm height the segment would be 0.4mm and would be omitted. The choice of 245mm preserves this segment.)

**Uninterrupted ribs (n=0 at X=5mm and n=21 at X=215mm):**
- Single segment: Z=0 to Z=245mm (full spine height).

---

### 5.3 Front Face — Fold-End Slots

Two horizontal pockets cut into the front face (Y=0), one per bag position. The slots capture the folded top end of each Platypus bag (a 190mm-wide flat heat-sealed strip) against the enclosure front wall.

**Slot profile (both slots identical in X and Y):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Width in X | 195mm | X=12.5mm to X=207.5mm |
| Depth in Y | 10mm (cut inward from front face) | Y=0 to Y=10mm |
| Height in Z | 20mm per slot | See table below |
| Side wall thickness | 12.5mm each side (X=0 to X=12.5mm and X=207.5mm to X=220mm) | Spine X |
| Chamfer on slot entry edges | 1mm × 45° on the four Z-facing edges at Y=0 (top and bottom edges of the slot opening on the front face) | — |

**Slot Z positions:**

| Slot | Z range | Center Z | Mating feature |
|------|---------|----------|----------------|
| Lower | Z=159.6mm to Z=179.6mm | Z=169.6mm | Lower bag fold end |
| Upper | Z=219.6mm to Z=239.6mm | Z=229.6mm | Upper bag fold end |

**Lower fold-end slot — complete specification:**

| Parameter | Value |
|-----------|-------|
| X range | X=12.5mm to X=207.5mm |
| Y range | Y=0mm to Y=10mm (pocket into body) |
| Z range | Z=159.6mm to Z=179.6mm |
| Entry chamfer | 1mm × 45° on top Z-edge (Z=179.6mm face at Y=0) and bottom Z-edge (Z=159.6mm face at Y=0) |

**Upper fold-end slot — complete specification:**

| Parameter | Value |
|-----------|-------|
| X range | X=12.5mm to X=207.5mm |
| Y range | Y=0mm to Y=10mm (pocket into body) |
| Z range | Z=219.6mm to Z=239.6mm |
| Entry chamfer | 1mm × 45° on top Z-edge (Z=239.6mm face at Y=0) and bottom Z-edge (Z=219.6mm face at Y=0) |

**Mating part:** Platypus 2L bag fold end — 190mm wide, 15–20mm tall seal band, 3–8mm thick when folded. Slot is 5mm wider than bag (195 − 190 = 5mm total, ~2.5mm per side). Slot depth 10mm provides positive capture (5mm required per synthesis.md; 10mm specified for retention margin).

---

### 5.4 Rear Face — Cradle Tab Slots

Eight slots cut into the rear face (Y=35mm surface), cut −Y inward to Y=20mm. Four slots per cradle, two cradles. Each slot receives one snap tab from a cradle platform during top-down assembly.

**All slots share this profile:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Open face | Y=35mm (rear face surface) | Spine Y |
| Depth | 15mm (from Y=35mm to Y=20mm) | Spine Y |
| Width in Z | 8.2mm (tab body 8mm + 0.2mm sliding clearance per requirements.md) | Spine Z |
| Width in X | 2.2mm (tab thickness 2mm + 0.2mm sliding clearance) | Spine X |
| Top opening | Open — slot has no ceiling. The slot top edge coincides with or is open to the spine top face (Z=245mm). The slot runs from its closed bottom edge upward continuously to Z=245mm. | Spine Z |
| Bottom wall | Closed — slot terminates at Z = slot_center − 4.1mm. This is the retention ledge against which the snap tab hook locks. | Spine Z |
| Chamfer on top entry | 1mm × 45° on all four edges at the slot top opening (the rim where the tab enters from above) | — |

**Assembly direction:** Cradle offered from above (−Z direction). Tab enters slot from the top opening. Tab body 8mm × 2mm slides down through the open-top slot. Hook (1.2mm height, 30° lead-in, 90° retention face) cams over the slot bottom wall as the tab descends, then springs inward. 90° retention face locks against bottom wall — permanent.

**Slot open-top modeling note:** Model each slot as a rectangular pocket from Z=slot_center−4.1mm (closed bottom) to Z=245mm (spine top). The slot is a through-cut in Z from Z=245mm down to the closed bottom, not a blind pocket.

**Lower cradle slots (L1–L4) — X=8.0mm, X range X=6.9mm to X=9.1mm:**

| Slot | Z center (mm) | Z range (mm) | Closed bottom Z (mm) | Top opens to |
|------|--------------|--------------|----------------------|--------------|
| L1 | 60.6 | 56.5 – 64.7 | 56.5 | Z=245mm (spine top) |
| L2 | 88.2 | 84.1 – 92.3 | 84.1 | Z=245mm |
| L3 | 115.1 | 111.0 – 119.2 | 111.0 | Z=245mm |
| L4 | 142.7 | 138.6 – 146.8 | 138.6 | Z=245mm |

**Upper cradle slots (U1–U4) — X=212.0mm, X range X=210.9mm to X=213.1mm:**

| Slot | Z center (mm) | Z range (mm) | Closed bottom Z (mm) | Top opens to |
|------|--------------|--------------|----------------------|--------------|
| U1 | 120.6 | 116.5 – 124.7 | 116.5 | Z=245mm |
| U2 | 148.2 | 144.1 – 152.3 | 144.1 | Z=245mm |
| U3 | 175.1 | 171.0 – 179.2 | 171.0 | Z=245mm |
| U4 | 202.7 | 198.6 – 206.8 | 198.6 | Z=245mm |

**Assembly orientation note (from spatial-resolution.md §9 Open Flag 2):** The overlap of lower cradle tab Z ranges with upper cradle tab Z ranges is resolved by placing lower cradle slots at X=8mm (left side of rear face) and upper cradle slots at X=212mm (right side of rear face). This requires the two cradle instances to be installed as mirrors: the lower cradle installs with its left lip as inboard (tabs at X=8mm); the upper cradle installs with its right lip as inboard (tabs at X=212mm). The cradle part is symmetric and supports both orientations. Assembly instructions must specify: lower cradle — left lip inboard; upper cradle — right lip inboard.

**Material check at slot X positions (from spatial-resolution.md §9 Open Flag 3):**
- L1–L4 slots at X=8mm (X=6.9 to X=9.1mm): material from spine left end face (X=0) to slot edge (X=6.9mm) = 6.9mm. Exceeds 1.2mm structural minimum. ✓
- U1–U4 slots at X=212mm (X=210.9 to X=213.1mm): material from slot edge (X=213.1mm) to spine right end face (X=220mm) = 6.9mm. Exceeds 1.2mm structural minimum. ✓

**Mating part interface:** Cradle platform snap tab: body 8mm wide (Z on cradle) × 2mm thick (X on spine), 15mm cantilever. Hook: 1.2mm height, 30° lead-in, 90° retention face. Slot clearance: 8.2mm in Z (0.2mm over tab), 2.2mm in X (0.2mm over tab). Clearances per requirements.md sliding fit standard.

---

### 5.5 End Faces — Snap Posts

Four posts total. Two on the left end face (X=0, protrude in −X direction). Two on the right end face (X=220mm, protrude in +X direction). Posts engage matching oval slots in the enclosure half inner walls when the enclosure halves close.

**Post cross-section (stadium / oval profile):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Shape | Stadium — two semicircles of radius 3mm at Z-top and Z-bottom, connected by 4mm straight sides | YZ plane |
| Height in Z | 10mm (3mm radius + 4mm straight + 3mm radius) | Spine Z |
| Width in Y | 6mm (diameter of each semicircle end) | Spine Y |
| Protrusion length | 8mm | ±X from end face |

**Post positions:**

| Post | End face | Root center — X | Root center — Y | Root center — Z | Tip X |
|------|----------|-----------------|-----------------|-----------------|-------|
| Left lower | X=0 | X=0 | Y=17.5mm | Z=30mm | X=−8mm |
| Left upper | X=0 | X=0 | Y=17.5mm | Z=70mm | X=−8mm |
| Right lower | X=220mm | X=220mm | Y=17.5mm | Z=30mm | X=228mm |
| Right upper | X=220mm | X=220mm | Y=17.5mm | Z=70mm | X=228mm |

Post pair vertical separation: 40mm (Z=70 − Z=30). Y=17.5mm centers posts on the 35mm spine depth.

**Retention flange (circumferential ridge on each post):**

| Parameter | Value | Frame / Notes |
|-----------|-------|---------------|
| Position along protrusion | 6mm from root face (2mm from post tip) | Along ±X protrusion axis |
| Ridge height | 1.5mm (circumferential, radially outward from post surface all around perimeter) | Radial |
| Lead-in angle | 30° taper on the entry (tip) side of the flange | Cams flange over enclosure slot rim as halves close |
| Retention face | 90° perpendicular on the root side of the flange | Locks post; prevents spine from pulling out of enclosure |
| Flange axial width | 1.5mm in ±X | Flange body from 6.0mm to 7.5mm from root face |

**Post tip chamfer:**
- 1mm × 45° chamfer on all post perimeter edges at the entry end (left posts: at X=−8mm; right posts: at X=228mm). This guides alignment as the enclosure halves approach. Per concept.md §5 design language.

**Mating feature (enclosure design input):** Each enclosure half requires two oval slots in its inner wall — one per spine post. Designed slot dimensions: 10.2mm (Z) × 6.2mm (Y) stadium (post 10mm × 6mm + 0.2mm clearance per requirements.md). Slot rim thickness: 1.5mm (to engage the 1.5mm retention flange).

---

### 5.6 Edge Treatments (Design Language)

| Feature | Treatment | Location |
|---------|-----------|----------|
| Spine face-to-face transitions | 2mm fillet radius | All edges where front/rear/end faces meet the top face (Z=245mm) and where end faces meet front and rear faces. Per concept.md §5: "Spine face corners: 2mm fillet radius on all corners where the spine face transitions to spine side walls." |
| Fold-end slot entry edges | 1mm × 45° chamfer | Top and bottom Z-edges of both fold-end slots at Y=0 (the opening face). Guides bag fold end insertion from above. |
| Tab slot top entry edges | 1mm × 45° chamfer | All four edges at the top opening of each tab slot on the rear face. Guides cradle tab insertion from above. |
| Snap post entry edges | 1mm × 45° chamfer | All perimeter edges at the post tip (entry end). Per concept.md §5 and requirements.md. |

---

## 6. Rubric A: Mechanism Narrative

See Section 3 above. The spine is stationary. It is assembled once. It is the structural backbone of the bag zone — the single element to which both cradle platforms attach and from which all bag loads are transferred to the enclosure. It is also the visual backbone — the front face rib language and the slot reveals between parts are all organized by the spine as the dominant interior surface.

---

## 7. Rubric B: Constraint Chain

See Section 4 above.

---

## 8. Rubric C: Direction Consistency Check

**Bag load direction:** In the installed frame, the bags are at 35° from horizontal. The distributed load on the cradle floor is perpendicular to the bag face — at 35° from vertical (55° from horizontal). This load is transmitted through the cradle snap tabs into the spine rear face slot walls. The slot walls are YZ-plane surfaces (X-normal faces bounding the 2.2mm X-width slot). These faces resist the Y-component of the load (perpendicular to the bag face, which in spine frame has a significant Y component — the bags are toward the front of the enclosure and pull the cradle toward the front face). The Z-component (bag weight pulling downward) bears against the slot bottom wall.

**Spine to enclosure load direction:** The spine transmits load to the enclosure in ±X (through the snap posts on the end faces). The posts resist the resultant load from both bags at a Z=30mm and Z=70mm height — the posts are in the lower spine. The bag loads arrive in Y and Z at the spine body; the posts redirect the resultant to ±X. This redirection is through the spine body as internal stress (bending and shear) — standard bracket behavior.

**No directional contradictions found:**
- Bag load: acts in the bag-axis-normal direction (compound Y and Z in spine frame). ✓
- Tab slot retention: slot bottom wall (Z-normal) resists Z-component; slot side walls (X-normal) resist X-component; slot depth walls (Y-normal) resist Y-component. All three components resisted by geometry. ✓
- Snap post retention: 90° retention face (X-normal) resists X-component of post pullout (the direction in which the enclosure would need to open to release the post). ✓
- Assembly direction for cradles: −Z (downward into slots). Slots open at top (+Z). Consistent. ✓
- Assembly direction for enclosure halves: ±X (closing from left and right). Posts protrude in ±X. Consistent. ✓

---

## 9. Rubric D: Interface Table

| Interface | Spine feature | Mating part feature | Spine dim | Mating dim | Clearance | Status |
|-----------|--------------|---------------------|-----------|------------|-----------|--------|
| Tab slots ↔ cradle snap tabs (Z width) | Slots 8.2mm wide in Z | Tabs 8mm wide in Z (cradle frame) | 8.2mm | 8.0mm | 0.2mm | ✓ Within requirements.md 0.2mm sliding fit |
| Tab slots ↔ cradle snap tabs (X width) | Slots 2.2mm wide in X | Tabs 2.0mm thick | 2.2mm | 2.0mm | 0.2mm | ✓ |
| Tab slots ↔ cradle snap tabs (depth) | Slots 15mm deep (Y=35 to Y=20) | Tabs 15mm cantilever | 15mm | 15mm | 0mm (tab fills full depth to allow hook to reach bottom wall) | ✓ |
| Snap posts ↔ enclosure wall oval slots | Posts 10mm(Z) × 6mm(Y) stadium | Enclosure slots to be designed | 10mm × 6mm | 10.2mm × 6.2mm (enclosure design input) | 0.2mm | Input to enclosure design — not yet designed |
| Fold-end slots ↔ bag fold end (X width) | Slots 195mm wide in X | Bag fold end 190mm wide | 195mm | 190mm | 5mm total (2.5mm/side) | ✓ |
| Fold-end slots ↔ bag fold end (Z height) | Slots 20mm tall in Z | Bag seal band 15–20mm | 20mm | 20mm max | 0mm min (snug at max) | ✓ Slot height matches max bag fold end height |
| Fold-end slots ↔ bag fold end (Y depth) | Slots 10mm deep in Y | Bag fold end 3–8mm thick | 10mm | 8mm max | 2mm min | ✓ |

**Design gap flagged:** Enclosure wall slot dimensions are not yet specified. The spine posts define the required slot: 10.2mm × 6.2mm stadium OD (with 0.2mm clearance over post 10mm × 6mm), rim thickness 1.5mm, slot depth ≥ 8mm (to allow full post protrusion engagement). This is a design input to the enclosure, not a problem with the spine. The spine interface is fully defined.

---

## 10. Rubric E: Assembly Feasibility

**Assembly sequence (from concept.md §Summary):**

1. Spine snap posts engage enclosure left half when the left half is offered to the spine. Left lower post (Z=30mm, X=0) and left upper post (Z=70mm, X=0) enter the two oval slots in the left half inner wall. 30° lead-in flanges cam the posts into their slots. Engagement force: 2 posts × low cam force.

2. Enclosure right half closes over the spine's right side. Right lower post (Z=30mm, X=220mm) and right upper post (Z=70mm, X=220mm) enter the right half's two oval slots. Enclosure is now closed. Spine is permanently captured by 4 posts. Bag zone is accessible from the top (before funnel sub-assembly mounts).

3. Lower cradle (left lip inboard) is lowered from above into spine tab slots L1–L4 at X=8mm. All four tabs click simultaneously as the cradle reaches its installed depth. Tactile and audible confirmation per concept.md snap UX guidance.

4. Upper cradle (right lip inboard) is lowered from above into spine tab slots U1–U4 at X=212mm. Same engagement sequence.

5. Bags are placed into cradles; fold ends slip into front-face slots from above.

6. Upper caps are pressed down onto cradles; caps snap closed.

7. Tube connections made; funnel sub-assembly mounts.

**Feasibility assessment:**
- Steps 1–2 are feasible: posts protrude in ±X (enclosure close direction), 30° lead-in provides alignment tolerance.
- Steps 3–4 are feasible: slots are open at top (Z=245mm). Cradle tabs enter from above. No blind insertion. No interference between slot sets (L-series at X=8mm, U-series at X=212mm).
- The two cradle insertion events are independent (different X positions, different Z ranges) and can occur in either order.
- Fold-end insertion (step 5) is feasible after cradles are in place: the bag is lowered at an angle with cap end first into cap pocket, fold end guided into front-face slot from above.
- No feature placement creates a physical block to any assembly step. ✓

---

## 11. Rubric F: Part Count

The spine is one part. No features of the spine are split off to the cradle or cap:
- Fold-end slots are integrated into the spine front face (not the enclosure front wall) — confirmed by concept.md §2 "Front-face slot integrated into the spine."
- Snap posts are integrated into the spine end faces.
- Tab slots are integrated into the spine rear face.
- All edge treatments are on the spine.

Nothing here should be merged with the cradle, cap, or enclosure. Confirmed. ✓

---

## 12. Rubric G: FDM Printability — Full Overhang Audit

**Print orientation:** Front face down (Y=0 face on build plate). Ribs are printed first (they protrude below the front face — rib tips touch the build plate). Spine body builds upward (+Z print direction) from Z=0 to Z=245mm.

**Overhang definition used:** A surface is overhanging if it is more than 45° from vertical — equivalently, if it faces more than 45° below horizontal. Surfaces facing downward (−Z in print frame) with no support below them are the concern.

| Feature | Surface analyzed | Overhang angle | Bridge span | Status | Notes |
|---------|-----------------|----------------|-------------|--------|-------|
| Transverse ribs | Rib tip face (−Z in print frame, faces build plate) | 90° from vertical = full overhang | N/A — rib tips touch build plate directly | ✓ PASS | Ribs are the first printed features. Tips contact build plate. No overhang. |
| Transverse ribs | Rib side faces (+Y and −Y faces of each rib, 0.8mm wide) | 0° from vertical (vertical walls) | N/A | ✓ PASS | Vertical walls, no overhang. |
| Front face body | Y=0 flat face | 90° from vertical = full downward face | 220mm × 245mm | ✓ PASS — on build plate | This is the build plate contact surface. No overhang. |
| Fold-end slot interior | Slot ceiling: does not exist. Slot is a pocket into Y=0 face; in print frame (+Y direction), the slot walls are vertical in Z and horizontal in X. No ceiling. | N/A | N/A | ✓ PASS | The fold-end slot is open at Y=0 (front face = build plate). In print frame, the slot opens toward the build plate and is cut −Y inward (upward in print). The slot walls are vertical (Z-parallel). The slot floor (at Y=10mm) faces downward toward build plate — but the slot opens toward the build plate at Y=0, so the slot interior builds upward without bridging. |
| Tab slots on rear face | Slot bottom wall (the closed bottom at Z=slot_center−4.1mm): this face is a −Z surface (faces downward in print frame). | 90° from vertical — downward facing | 8.2mm span in Z, 2.2mm span in X. Max bridging span = 8.2mm | ✓ PASS — within 15mm bridge limit | The slot bottom is a horizontal surface spanning 8.2mm in Z and 2.2mm in X. Max span = 8.2mm < 15mm maximum bridge span (requirements.md). No support required. |
| Tab slots on rear face | Slot side walls (X-normal faces at X=6.9mm and X=9.1mm for L-series; at X=210.9mm and X=213.1mm for U-series) | 0° from vertical | N/A | ✓ PASS | Vertical walls. |
| Tab slots on rear face | Slot top opening | Open to spine top face — no ceiling to bridge | N/A | ✓ PASS | Slot runs from closed bottom up to Z=245mm (spine top). No ceiling. |
| Tab slot entry chamfers (top rim) | 1mm × 45° chamfer at slot top rim | 45° — exactly at the limit. Self-supporting. | 1.4mm in Z at 45° | ✓ PASS | 45° chamfer self-supports per requirements.md (≥45° from horizontal is acceptable). |
| Snap posts — left/right end faces | Post protrusion in ±X (horizontal in print frame). Post side faces are Y-normal and Z-normal (vertical in print frame). | Post faces: 0° from vertical | N/A | ✓ PASS | Posts protrude horizontally (±X). Post walls are vertical in print frame. |
| Snap post flanges | Flange root-side face (90° retention face, −X-facing on left posts): faces toward enclosure center, is a vertical surface in print frame. | 0° from vertical | N/A | ✓ PASS | Vertical face. |
| Snap post flanges | Flange entry-side (30° lead-in, angled toward post tip): this is a tapered face on the post perimeter at 30° from the post axis = 60° from horizontal. | 30° from vertical = 60° from horizontal. More than 45° from horizontal. | N/A — not a bridging concern, this is a continuous face | ✓ PASS | 60° from horizontal is steeper than the 45° limit. Self-supporting. |
| Snap post tip chamfer | 1mm × 45° chamfer at post entry end | 45° — self-supporting | N/A | ✓ PASS | |
| Snap post underside (hook undercut) | The retention flange's root-side face (90°, faces −X for left posts) is vertical in print frame — no undercut issue. The flange is a circumferential ridge; its undercut (the concave groove between flange and post root) is 1.5mm deep radially and transitions with a 90° face. In print frame (posts horizontal in ±X), this groove faces −Z (downward) for the portion of the flange on the bottom of the post. | 90° from vertical — full undercut | Groove span: 1.5mm radial depth. No bridging needed. | FLAG — see note | The undercut groove on the underside of each post flange is a small downward-facing concave surface. Span is ~1.5mm (flange depth). This is below the 15mm bridge limit and is a very small feature. The slicer will bridge this 1.5mm span without issue. No designed support required. |
| Rear face (Y=35mm) | The rear face is an upward-facing surface in print frame | 90° from vertical — faces upward | N/A — it is the top surface during printing, not a bridging concern | ✓ PASS | Upward-facing surface. No overhang. |
| Top face (Z=245mm) | Upward-facing surface — printed last | N/A — top of print | N/A | ✓ PASS | |
| Fold-end slot entry chamfers | 1mm × 45° chamfer on slot Z-edges at Y=0 | 45° — self-supporting | N/A | ✓ PASS | |

**Overhang audit summary:** All features pass. The only flagged item is the snap post flange groove undercut (~1.5mm radial span downward-facing concave). This span is far below the 15mm bridge limit — no designed support required and no slicer support needed. All other surfaces are either build-plate-contact, vertical, upward-facing, 45°-chamfered (self-supporting), or bridging spans under the 15mm limit.

**No supports required. No designed support geometry required.**

---

## 13. Rubric H: Feature Traceability

Every feature on the spine is traced to a requirement from vision.md or a physical necessity.

| Feature | Traced to | Source |
|---------|-----------|--------|
| Spine body 220mm width | "The outer enclosure is 220mm × 300mm × 400mm" — spine spans the full interior width | vision.md §2 |
| Spine body 35mm depth | Minimum depth to contain 10mm fold-end slots (front) + 10mm solid gap + 15mm tab slots (rear) = 35mm; derived from feature geometry | Physical necessity |
| Spine body 245mm height | Sets by upper fold-end slot position (Z=239.6mm top edge) + structural margin (5.4mm above slot); 240mm minimum per spatial-resolution.md §2, 245mm for margin per §9 Flag 1 | Physical necessity + structural margin |
| Transverse ribs (22×, front face) | "The spine face that is visible carries the same rib language as the enclosure interior panels — parallel ribs at 8–12mm spacing, 1.5mm height, running in one direction (transverse)" — ribs are the design language for all interior surfaces | vision.md §2 (consumer appliance standard) + concept.md §5 |
| Rib spacing 10mm pitch | "Spacing: 10mm. Height: 1.5mm. Width: 0.8mm." — specified in concept.md design language section | concept.md §5 |
| Rib interruption at fold-end slots | Slots remove front face material; ribs cannot exist where the face is removed | Physical necessity |
| Lower fold-end slot (Z=159.6–179.6mm) | "The spine's front face carries two horizontal slot features, one per bag position, at the height corresponding to each bag's fold end" — captures fold end against front wall | concept.md §2 + spatial-resolution.md §3.2 |
| Upper fold-end slot (Z=219.6–239.6mm) | Same as lower; upper bag's fold end height in spine frame | concept.md §2 + spatial-resolution.md §3.2 |
| Fold-end slot width 195mm | Bag fold end 190mm + 5mm total clearance (2.5mm/side) per concept.md §2 | concept.md §2 |
| Fold-end slot depth 10mm | "10mm provides positive capture" — concept.md specifies 10mm; 5mm is minimum per synthesis.md | concept.md §2 |
| Tab slots L1–L4 (lower cradle, X=8mm) | Cradle snap tab interface; concept.md §2 specifies 8.2mm wide × 15mm deep slots open at top; Z positions from 35° coordinate transform of cradle tab positions | concept.md §2 + spatial-resolution.md §4 |
| Tab slots U1–U4 (upper cradle, X=212mm) | Same as L-series; X=212mm (right side) resolves Z-overlap conflict between lower and upper cradle tab sets | spatial-resolution.md §4 overlap resolution |
| Snap posts ×4 (2 per end face, Z=30 and Z=70mm) | "Two snap points per end (four total) — making it the first permanent sub-assembly step" — vision requires snap-assembly enclosure | vision.md §2 + concept.md §2 |
| Post size 10mm × 6mm stadium, 8mm protrusion | Structural requirement: four posts carry ~40N combined bag load; concept.md §2 specifies these dimensions | concept.md §2 |
| Post retention flange 1.5mm, 30°/90° | 30° lead-in for cam-in assembly; 90° retention for permanent no-tool-access design per vision | vision.md §2 (permanent snap assembly) + concept.md §2 |
| 2mm fillet on face-to-face transitions | "Spine face corners: 2mm fillet radius" — design language for consumer appliance interior | concept.md §5 |
| 1mm chamfer on post entry edges | Per concept.md §5 and requirements.md: guide alignment during assembly | concept.md §5 + requirements.md |
| 1mm chamfer on slot entry edges | Guide bag fold-end insertion and cradle tab insertion; smooth assembly UX | concept.md §2 (UX guidance for all snap features) |
| PETG material | "PETG throughout" — all bag frame parts | concept.md §5 |
| Front-face-down print orientation | Best surface quality on the visually dominant face; ribs print without overhang; slot orientation avoids bridges | concept.md §7 (manufacturing constraints) |

---

## 14. Design Gaps and Open Flags

**Flag 1 — Enclosure slot dimensions not yet designed.** The spine snap post interface (10mm × 6mm stadium, 1.5mm retention rim, slot depth ≥ 8mm) is a design input to the enclosure. The enclosure wall slot must be specified when the enclosure is designed. This is not a gap in the spine specification but a dependency.

**Flag 2 — Cradle assembly orientation must be specified in assembly instructions.** Lower cradle: left lip inboard (tabs at X=8mm). Upper cradle: right lip inboard (tabs at X=212mm). The cradle part file is symmetric; orientation is set at assembly time. If assembly instructions are ambiguous, the cradle could be inserted in the wrong orientation. Mitigation: add a visual asymmetry to the cradle (e.g., a small embossed indicator on one lip face) or make the assembly instruction explicit. This is a cradle and assembly-instruction concern, not a spine concern — the spine slot positions are correct.

**Flag 3 — Post flange undercut (~1.5mm span).** Noted in Rubric G. Assessed as below the 15mm bridge limit. No action required. Monitor in first test print — if the 1.5mm groove underside on the post flange prints poorly, add a 45° chamfer to the undercut groove (replacing the sharp 90° internal corner on the −Z face of the groove). This would reduce retention force marginally; acceptable at this feature scale.

**Flag 4 — Rib segment above upper fold-end slot is 5.4mm (at 245mm height).** This is the minimum segment length retained under the ≥5mm rule from spatial-resolution.md §9 Flag 4. At 5.4mm, the segment provides minimal visual benefit but does not violate printability. It may read as a visual artifact. If it prints as a stub, it can be omitted (set rib Segment 3 to zero length for all interrupted ribs) without functional consequence. Decide at first test print review.

**No structural design gaps. All features are fully specified. All interfaces are dimensionally complete. No feature is orphaned.**
