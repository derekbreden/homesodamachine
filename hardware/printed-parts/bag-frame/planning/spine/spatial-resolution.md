# Spine — Spatial Resolution

**Date:** 2026-03-29
**Inputs:** concept.md, decomposition.md, synthesis.md, requirements.md, vision.md,
           cradle-platform/parts.md §Feature 6, cradle-platform/spatial-resolution.md §5
**Next step:** parts.md — feature geometry definitions using this document as the sole dimensional source

---

## Preamble: Coordinate Transform from Cradle Frame to Spine Frame

The cradle snap tabs are defined in the cradle's local frame (Z = bag axis, running 287mm from cap end to fold end). The spine's local frame has Z = enclosure vertical axis. The two frames share the X axis (enclosure width). The cradle's Z axis is tilted 35° from horizontal, so a distance d along the cradle's Z axis projects to:

- Enclosure vertical (spine Z): d × sin(35°) = d × 0.5736
- Enclosure horizontal depth (spine Y): d × cos(35°) = d × 0.8192

All tab slot positions on the spine's rear face are derived from this transform applied to the tab Z-center positions in the cradle frame (Z = 97, 145, 192, 240mm) plus the installed height of each cradle's cap end in the enclosure.

---

## 1. Part Reference Frame Definition

### Print Orientation

The spine is printed front-face-down. The front face (the face bearing transverse ribs and fold-end slots) is flat on the build plate. In the print, this face is at Z=0 (the build plate surface), and the spine body builds upward from it. In the installed orientation, the spine is inserted vertically into the enclosure with the front face toward the enclosure front wall — the same face that was on the build plate during printing. The print Z axis (upward from build plate) corresponds to the installed Z axis (vertical in enclosure). No rotation is required between print frame and installed frame.

### Rib Orientation Clarification

The transverse ribs protrude from the front face. In the print frame, the front face is at Z=0 (build plate). The ribs protrude in the −Z direction (downward, toward the build plate). In the print, the rib tips are the first features to contact the build plate; the rib bodies build upward, then the spine body builds above them. In the installed orientation, the front face is toward the enclosure front wall and the ribs protrude outward (toward the user-facing front direction). The ribs are not structural — they are a visual/design language element on the face visible between the two bag positions.

### Axis Definitions

| Axis | Direction | Physical meaning in installed orientation |
|------|-----------|------------------------------------------|
| X    | Width      | Left to right across enclosure interior; X=0 is left end of spine, X=220mm is right end |
| Y    | Depth      | Front face at Y=0 (build plate face during print); rear face at Y=35mm (spine depth). Positive Y = toward enclosure back wall |
| Z    | Height     | Bottom of spine at Z=0 (build plate surface during print); top of spine at Z=240mm. Positive Z = upward in enclosure |

### Origin

The origin is the corner where the front face (Y=0), left end face (X=0), and bottom face (Z=0) meet. This is the lower-left corner of the front face as seen from the front.

### Part Envelope

| Axis | Minimum | Maximum | Span |
|------|---------|---------|------|
| X    | 0mm     | 220mm   | 220mm |
| Y    | −1.5mm (rib tips protruding from front face) | 35mm (rear face) | 36.5mm |
| Z    | −1.5mm (rib tips protruding below Z=0 front face) | 240mm (top face) | 241.5mm |

Note: Y=−1.5mm and Z=−1.5mm are the rib tip positions. In the print frame, these correspond to the rib tips that print first on the build plate. The main body envelope is X: 0–220mm, Y: 0–35mm, Z: 0–240mm.

---

## 2. Body Dimensions

### Width (X)

**Exact: 220mm.** The spine spans the full enclosure interior width. The enclosure interior is 220mm wide. The spine ends (at X=0 and X=220mm) are the surfaces from which the snap posts protrude.

### Depth (Y)

**Exact: 35mm** (Y=0 front face to Y=35mm rear face).

Derivation of minimum required depth:

| Constraint | Depth consumed | From face |
|------------|----------------|-----------|
| Fold-end slots (front face) | 10mm | Front face (Y=0 inward to Y=10mm) |
| Rear-face tab slots | 15mm | Rear face (Y=35mm inward to Y=20mm) |
| Minimum wall between slot zones | 2mm | Y=10mm to Y=20mm (10mm gap > 2mm minimum) |
| **Minimum total** | **27mm** | — |

Using 35mm provides 10mm gap between the deepest front slot and the shallowest rear slot (Y=10 front slot → Y=20 rear slot = 10mm of solid material). 35mm satisfies all constraints with margin and matches the concept/decomposition working value.

**Non-intersection verification:** Front fold-end slots extend from Y=0 to Y=10mm. Rear tab slots extend from Y=35mm to Y=20mm. The two zones do not overlap. ✓

### Height (Z)

**Exact: 240mm** (Z=0 bottom face to Z=240mm top face).

The height is set by the upper fold-end slot: the upper fold-end slot top edge is at Z=239.6mm (see §3 below). The spine must enclose this feature with at least 0.4mm of solid material above the slot top. Setting Z=240mm provides exactly this margin.

**Derivation chain** (see §3 and §4 for full derivation):
- Upper cradle fold end projects to spine Z=229.6mm
- Upper fold-end slot runs Z=219.6 to Z=239.6mm
- Spine top = Z=239.6 + 0.4mm wall = 240mm ✓

The snap tab zone (highest tab at Z=202.7mm) is entirely within the 240mm height. ✓

---

## 3. Front Face Features

### 3.1 Transverse Ribs

**Quantity:** 22 ribs.

**Rib profile (in spine local frame):**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Rib tip Z | −1.5mm (protrudes below front face) | Spine Z |
| Rib base Z | 0mm (flush with front face surface) | Spine Z |
| Rib protrusion height | 1.5mm (in −Z direction from front face) | Spine Z |
| Rib width in Y | 0.8mm (centered at Y=0, spanning Y=−0.4 to Y=0.4mm) | Spine Y |
| Rib length in X | 220mm (full spine width, interrupted by fold-end slots) | Spine X |

Note on Y direction: Y=0 is the front face. Ribs protrude toward negative Y (forward, outward). In print frame the ribs are at Z<0 (they build first on the plate); in installed frame they protrude toward the enclosure front wall.

**Rib X positions (center of each rib body):**

Ribs are equally spaced at 10mm intervals. The first rib center is at X=5mm; the last is at X=215mm. Formula: rib center X = 5 + 10n for n = 0, 1, 2, ... 21.

| n | X center (mm) | n | X center (mm) |
|---|--------------|---|--------------|
| 0 | 5            | 11 | 115          |
| 1 | 15           | 12 | 125          |
| 2 | 25           | 13 | 135          |
| 3 | 35           | 14 | 145          |
| 4 | 45           | 15 | 155          |
| 5 | 55           | 16 | 165          |
| 6 | 65           | 17 | 175          |
| 7 | 75           | 18 | 185          |
| 8 | 85           | 19 | 195          |
| 9 | 95           | 20 | 205          |
| 10| 105          | 21 | 215          |

**Rib Z positions:** Ribs run the full height of the front face (Z=0 to Z=240mm), interrupted where fold-end slots are cut. Ribs do not run continuously — they are broken wherever a fold-end slot occupies the front face. See fold-end slot interaction below.

**Fold-end slot interaction:** Fold-end slots take priority over ribs. The two slots occupy the front face at the Z ranges defined in §3.2. Within each slot's Z range, ribs are absent (the slot removes the front face surface in that zone). The 20 rib positions at X=15 through X=205 (n=1 through n=20) fall within the slot X range of X=12.5 to X=207.5mm and are interrupted at the slot Z ranges. The two end ribs at X=5mm (n=0) and X=215mm (n=21) are entirely outside both fold-end slots in X and run the full Z=0 to Z=240mm without interruption.

**Interrupted rib summary:**

| Rib X centers (mm) | Status |
|--------------------|--------|
| 5, 215 | Continuous — full Z extent (Z=0 to Z=240mm). Outside fold-end slot X range. |
| 15, 25, 35, 45, 55, 65, 75, 85, 95, 105, 115, 125, 135, 145, 155, 165, 175, 185, 195, 205 | Interrupted at lower and upper fold-end slot Z ranges. Three continuous segments per rib: Z=0 to Z=159.6mm, Z=179.6mm to Z=219.6mm, and Z=239.6mm to Z=240mm. |

### 3.2 Fold-End Slots

Two slots, one per bag cradle position (lower and upper), on the front face (Y=0 face, cut inward to Y=10mm).

**Slot profile:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| Slot width in X | 195mm (X=12.5 to X=207.5mm) | Spine X |
| Slot depth in Y | 10mm (Y=0 front face to Y=10mm into body) | Spine Y |
| Slot height in Z | 20mm per slot | Spine Z |
| Slot wall thickness on each X side | 12.5mm (from spine end face X=0 or X=220mm to slot edge) | Spine X |

**Derivation of slot Z positions:**

The fold-end slot is at the height corresponding to where the bag's fold end (Z=287mm in cradle frame) projects in the enclosure vertical axis.

Lower cradle cap end height in spine frame: H_lower = 5mm (design choice — 5mm clearance from spine base).
Upper cradle cap end height in spine frame: H_upper = H_lower + 60mm = 65mm (60mm vertical pitch between bags per synthesis.md §6).

Fold end height = cap end height + 287 × sin(35°) = cap end height + 287 × 0.5736 = cap end height + 164.6mm.

| Slot | Cap end height (mm) | Fold end height in spine frame (mm) | Slot center Z (mm) | Slot Z range |
|------|--------------------|------------------------------------|-------------------|--------------|
| Lower | H_lower = 5.0 | 5.0 + 164.6 = 169.6 | 169.6 | Z=159.6 to Z=179.6mm |
| Upper | H_upper = 65.0 | 65.0 + 164.6 = 229.6 | 229.6 | Z=219.6 to Z=239.6mm |

**Lower fold-end slot — complete specification:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| X range | X=12.5mm to X=207.5mm | Spine X |
| Y range | Y=0 (front face) to Y=10mm (into body) | Spine Y |
| Z range | Z=159.6mm to Z=179.6mm | Spine Z |
| Center Z | Z=169.6mm | Spine Z |

**Upper fold-end slot — complete specification:**

| Parameter | Value | Frame |
|-----------|-------|-------|
| X range | X=12.5mm to X=207.5mm | Spine X |
| Y range | Y=0 (front face) to Y=10mm (into body) | Spine Y |
| Z range | Z=219.6mm to Z=239.6mm | Spine Z |
| Center Z | Z=229.6mm | Spine Z |

**Slot clearance check:** Upper slot top is at Z=239.6mm. Spine top face is at Z=240mm. Remaining wall thickness above upper slot: 0.4mm. This is thin. **Flag for review:** if modeling or printing tolerance requires more wall above the upper slot, the spine height should increase to 245mm, which provides 5.4mm above the upper slot. Use 245mm if structural margin is required; 240mm if part count and fit are the priority. This document uses 240mm as the resolved dimension with this flag noted.

**Mating part:** The fold end of the Platypus bag (a 190mm-wide, 15–20mm-tall flat heat-sealed strip, 3–8mm thick when folded) slips into the slot from above during assembly. The slot is 5mm wider than the bag fold end (195 − 190 = 5mm total clearance, ~2.5mm per side). The slot depth of 10mm captures the fold end (5mm required per synthesis.md; 10mm provides positive capture).

---

## 4. Rear Face Features — Cradle Tab Slots

### Assembly Geometry Overview

The cradle platform's four snap tabs (at its inboard long edge) engage slots cut into the spine rear face (Y=35mm). During assembly, the cradle is offered from above and pressed down (in the −Z direction in spine frame). The slots are open at their top (Z = slot center + 4.1mm) so the tabs enter from the top as the cradle descends. The cradle's inboard edge is the left lip outer face of the cradle, which is assigned as the inboard face in cradle-platform/spatial-resolution.md §5.

### Slot Geometry

Each slot is a rectangular blind pocket cut into the rear face.

| Parameter | Value | Frame |
|-----------|-------|-------|
| Slot width in Z | 8.2mm (accommodates 8mm tab with 0.2mm sliding clearance per requirements.md) | Spine Z |
| Slot depth in Y | 15mm (from rear face inward: Y=35mm to Y=20mm) | Spine Y |
| Slot open direction | Open at top (Z = slot top edge is open to spine top face) | Spine Z |
| Slot width in X | 2.2mm (accommodates 2mm tab thickness with 0.2mm clearance per requirements.md) | Spine X |
| Slot X position | X=8mm (cradle inboard edge position; see below) | Spine X |

**Slot X position derivation:**

The cradle is 204mm wide in X (left lip outer face to right lip outer face). The enclosure/spine interior is 220mm wide in X. With 8mm margin on each side: cradle X range in spine frame = X=8mm (left lip outer face) to X=212mm (right lip outer face). The inboard edge (left lip outer face per cradle-platform/spatial-resolution.md) is at X=8mm. The tab extends 15mm from this face into the spine in the −Y direction (into the spine body from the rear face). The slot is therefore centered at X=8mm and is 2.2mm wide in X (X=6.9mm to X=9.1mm). The slot depth is in the −Y direction (from Y=35 to Y=20mm).

Note: The two cradles (lower and upper) are both oriented identically with the left lip as inboard; all 8 slots share the same X position (X=8mm). The two sets of 4 slots are distinguished only by their Z positions.

### Coordinate Transform: Cradle Tab Positions → Spine Z Frame

The cradle snap tab Z-center positions in the cradle frame are Z = 97, 145, 192, 240mm (from cradle-platform/spatial-resolution.md §5). These are positions along the bag axis (cradle Z axis), measured from the cap end (cradle Z=0). To find the corresponding spine Z positions, apply:

**spine_Z = cradle_cap_end_height + cradle_Z × sin(35°)**

where cradle_cap_end_height is H_lower or H_upper (the height of the cradle cap end in the spine frame).

**Lower cradle** (H_lower = 5mm):

| Cradle tab | Cradle Z center (mm) | Cradle Z × sin35° (mm) | Spine Z center (mm) | Spine Z range (±4.1mm) |
|------------|---------------------|------------------------|--------------------|-----------------------|
| Tab 1      | 97                  | 55.6                   | **60.6**           | Z=56.5 to Z=64.7mm   |
| Tab 2      | 145                 | 83.2                   | **88.2**           | Z=84.1 to Z=92.3mm   |
| Tab 3      | 192                 | 110.1                  | **115.1**          | Z=111.0 to Z=119.2mm |
| Tab 4      | 240                 | 137.7                  | **142.7**          | Z=138.6 to Z=146.8mm |

**Upper cradle** (H_upper = 65mm):

| Cradle tab | Cradle Z center (mm) | Cradle Z × sin35° (mm) | Spine Z center (mm) | Spine Z range (±4.1mm) |
|------------|---------------------|------------------------|--------------------|-----------------------|
| Tab 1      | 97                  | 55.6                   | **120.6**          | Z=116.5 to Z=124.7mm |
| Tab 2      | 145                 | 83.2                   | **148.2**          | Z=144.1 to Z=152.3mm |
| Tab 3      | 192                 | 110.1                  | **175.1**          | Z=171.0 to Z=179.2mm |
| Tab 4      | 240                 | 137.7                  | **202.7**          | Z=198.6 to Z=206.8mm |

**Note on slot Z range:** The tab body is 8mm wide in the cradle Z direction. Projected to spine Z: 8 × sin(35°) = 4.6mm. However, the concept spec treats the slot width as 8.2mm in the spine Z direction (matching the "8mm wide" tab spec directly). This is the conservative interpretation — the slot is slightly wider in spine Z than the projected tab, ensuring entry without interference. Use 8.2mm in spine Z as specified; each slot center ± 4.1mm gives the Z range.

**Slot overlap check:** Verify no two slots overlap in Z:

Lower Tab 4 top: Z=146.8mm. Upper Tab 1 bottom: Z=116.5mm. Upper Tab 1 is ABOVE Lower Tab 4 → no overlap from Lower Tab 4 to Upper Tab 1.
Lower Tab 3 top: Z=119.2mm. Upper Tab 1 bottom: Z=116.5mm. These are 2.7mm apart. **Flag:** Lower Tab 3 (Z=111.0–119.2mm) and Upper Tab 1 (Z=116.5–124.7mm) overlap by 2.7mm in Z.

**Overlap resolution:** This overlap arises because the two cradles' tab sets interleave in Z rather than separate cleanly. The lower cradle's highest tab (Tab 3 at Z=115.1mm, not Tab 4 at Z=142.7mm) and the upper cradle's lowest tab (Tab 1 at Z=120.6mm) are closest. They are 5.5mm apart center-to-center, with their Z ranges overlapping 2.7mm.

Two options to resolve:
1. Separate the tab slots in X — lower cradle tabs at X=8mm (left inboard), upper cradle tabs at X=212mm (right inboard, using right lip as inboard for upper cradle). This requires the two cradles to be oriented as mirrors of each other (one with left-inboard, one with right-inboard). The slot sets are then on opposite sides of the spine rear face and do not conflict.
2. Accept the overlap and offset the two slot sets in X (slot center at X=8mm for lower cradle, slot center at X=14mm for upper cradle — 6mm X offset, which places the slots adjacent but non-overlapping in X at the cost of more material removal).

**Resolved choice: Option 1 (mirrored cradle orientations).** The lower cradle uses the left lip as inboard (slots at X=8mm), the upper cradle uses the right lip as inboard (slots at X=212mm). The cradle design is symmetric and can be installed either way. The lower slot set and upper slot set are on opposite sides of the spine rear face — no Z overlap conflicts. This is the cleaner solution and eliminates the overlap.

**Revised slot X positions:**
- Lower cradle tab slots: X=8mm (X=6.9 to X=9.1mm, 2.2mm wide in X)
- Upper cradle tab slots: X=212mm (X=210.9 to X=213.1mm, 2.2mm wide in X)

### Complete Slot Table (All 8 Slots on Rear Face)

All slots are on the rear face (Y=35mm surface), cut −Y inward to Y=20mm. All slots are open at their top Z edge (Z = slot_center + 4.1mm, where the spine body allows).

| Slot | Cradle | Spine Z center (mm) | Spine Z range (mm) | X position (mm) | Depth (Y=35 to Y=20mm) |
|------|--------|--------------------|--------------------|----------------|------------------------|
| L1 | Lower | 60.6 | 56.5 – 64.7 | X=8.0 | 15mm (Y=35 to Y=20) |
| L2 | Lower | 88.2 | 84.1 – 92.3 | X=8.0 | 15mm |
| L3 | Lower | 115.1 | 111.0 – 119.2 | X=8.0 | 15mm |
| L4 | Lower | 142.7 | 138.6 – 146.8 | X=8.0 | 15mm |
| U1 | Upper | 120.6 | 116.5 – 124.7 | X=212.0 | 15mm |
| U2 | Upper | 148.2 | 144.1 – 152.3 | X=212.0 | 15mm |
| U3 | Upper | 175.1 | 171.0 – 179.2 | X=212.0 | 15mm |
| U4 | Upper | 202.7 | 198.6 – 206.8 | X=212.0 | 15mm |

### Slot Geometry (Profile at Each Slot)

| Parameter | Value | Frame |
|-----------|-------|-------|
| Open face | Y=35mm (rear face surface) | Spine Y |
| Slot depth | 15mm (to Y=20mm) | Spine Y |
| Slot width in Z | 8.2mm | Spine Z |
| Slot width in X | 2.2mm (centered on X=8.0mm or X=212.0mm) | Spine X |
| Slot top opening (assembly entry) | Open — slot top edge coincides with spine top face or is open to it | Spine Z |
| Slot bottom wall | Solid — slot terminates at its Z bottom edge | Spine Z |
| 1mm chamfer on top entry edge | Per concept.md: 1mm chamfer on entry edges of all snap features to guide alignment | — |

**Mating part interface:** The cradle's snap tab enters the slot from above as the cradle descends in −Z. Tab body: 8mm × 2mm cross-section. Hook at tip: 1.2mm height, 30° lead-in, 90° retention face. The retention face is at Y = 35mm − 2mm (the hook underside, 2mm from the rear face, facing outward toward −Y) that prevents the cradle from pulling away from the spine in +Y. The 30° lead-in on the hook cams the tab in −Y during entry. Once the hook clears the slot bottom edge, it springs back and the 90° face is captured.

---

## 5. End Face Features — Snap Posts

### Post Overview

4 posts total: 2 on the left end face (X=0 face, protruding in −X direction), 2 on the right end face (X=220mm face, protruding in +X direction). Each post has an oval (stadium) cross-section and engages a matching slot in the enclosure half's inner wall.

### Post Cross-Section Profile

| Parameter | Value | Frame |
|-----------|-------|-------|
| Cross-section shape | Stadium (oval) — two semicircles connected by straight sides | YZ plane |
| Post height in Z | 10mm | Spine Z |
| Post thickness in Y | 6mm | Spine Y |
| Post protrusion in X | 8mm (from end face outward) | Spine X |
| Post entry chamfer | 1.0mm × 45° on all post perimeter edges at the entry end (at X=−8mm for left, X=228mm for right) | Per requirements.md and concept.md |

The stadium cross-section: two semicircles of radius 3mm at top and bottom (in Z), connected by a 4mm straight section (6mm total height in Z, 6mm total width in Y). Center of cross-section: at the Z and Y centerline of the post.

### Post Z Positions

Two posts per end face, 40mm apart in Z. Positioned in the lower portion of the spine to provide:
- Stable 2-point contact per side (resisting rotation about any axis)
- Clearance from fold-end slots and tab slot zones in the mid-to-upper spine Z range

| Post | End face | Center Z | Center Y | X position (root face / tip) |
|------|----------|----------|----------|------------------------------|
| Left lower | X=0 face | Z=30mm | Y=17.5mm (spine Y midpoint) | Root: X=0 / Tip: X=−8mm |
| Left upper | X=0 face | Z=70mm | Y=17.5mm | Root: X=0 / Tip: X=−8mm |
| Right lower | X=220mm face | Z=30mm | Y=17.5mm | Root: X=220mm / Tip: X=228mm |
| Right upper | X=220mm face | Z=70mm | Y=17.5mm | Root: X=220mm / Tip: X=228mm |

Post pair separation: 40mm (Z=70 − Z=30 = 40mm). ✓

**Post Y center:** Y=17.5mm (midpoint of 35mm depth). This centers the post on the spine thickness for symmetric load transfer.

### Post Flange (Retention Hook)

Each post carries one circumferential retention flange (a 1.5mm-tall ridge encircling the post oval perimeter).

| Parameter | Value | Frame | Notes |
|-----------|-------|-------|-------|
| Flange position along protrusion | 6mm from root face (2mm from post tip) | Spine X (along protrusion axis) | Post tip is 8mm from root; flange at 6mm leaves 2mm entry stub beyond flange |
| Flange height (circumferential ridge height) | 1.5mm | Radial direction from post surface | Adds 1.5mm to each cross-sectional dimension at the flange location |
| Lead-in angle | 30° taper on the entry side (tip side) of the flange | — | Allows the flange to cam into the enclosure slot as the enclosure halves close |
| Retention face | 90° perpendicular face on the root side of the flange | — | Prevents post from backing out of slot after assembly |
| Flange X range | X=6.0mm to X=7.5mm from root face (1.5mm wide in X along protrusion) | Spine X (local to post) | For left post: X=−6.0mm to X=−7.5mm in spine frame |

**Assembly direction:** The enclosure halves close in the X direction (toward X=110mm, the spine center). As each half closes, the spine posts enter the enclosure wall slots. The 30° lead-in cams the flange over the slot rim. At full closure, the 90° retention face is captured behind the slot rim. This is permanent — the spine cannot be removed without destroying the enclosure, consistent with the vision's permanent-assembly architecture.

**Mating feature in enclosure:** Each enclosure half has two oval slots (matching the 10mm×6mm post cross-section with 0.2mm clearance per requirements.md → designed slot = 10.2mm×6.2mm stadium) in the inner wall. The slot rim is 1.5mm thick to engage the post retention flange.

---

## 6. Transform Summary: Print Frame → Installed Frame

The spine is installed vertically in the enclosure with the same orientation it was printed. No rotation is required.

| Axis | Print frame | Installed frame |
|------|-------------|-----------------|
| X | Width of part on build plate (220mm) | Enclosure width (left=X=0, right=X=220mm) |
| Y | Depth from front face (build plate face = Y=0) | Depth from front face (toward enclosure back wall = +Y) |
| Z | Height from build plate (first layer = Z=0) | Enclosure vertical (up = +Z) |

**Three verification points:**

1. **Spine origin** (X=0, Y=0, Z=0 in print frame):
   - In installed frame: lower-left corner of front face of spine, at the spine's lowest point on its front face
   - In enclosure frame: this corner is at the left interior wall, at the height where the spine base rests, at the front face of the spine

2. **Left lower snap post tip** (X=−8mm, Y=17.5mm, Z=30mm in spine frame, after the post protrudes 8mm beyond the left end face):
   - Print frame: the post extends 8mm beyond the X=0 face of the part in the −X direction
   - Installed frame: this post tip is the point that contacts the enclosure left half slot, 8mm inside the enclosure left wall, at height Z=30mm (30mm above spine base), at depth Y=17.5mm (midpoint of spine)

3. **Upper fold-end slot far corner** (X=207.5mm, Y=10mm, Z=239.6mm in spine frame):
   - Print frame: this is the deepest back-right corner of the upper fold-end slot, near the spine top
   - Installed frame: this point is 207.5mm from the left wall, 10mm behind the front face of the spine, and 239.6mm above the spine base — near the top of the spine at the bag fold-end capture region

**Transform is a translation only** (from spine local origin to enclosure mounting position). The enclosure mounting height of the spine base (spine Z=0 in enclosure coordinates) is determined by the enclosure design. The spine's own local frame is self-consistent and does not depend on this absolute height.

---

## 7. Feature Interaction Summary

### Front Face Interactions

| Feature A | Feature B | Interaction | Resolution |
|-----------|-----------|-------------|------------|
| Transverse ribs (X = 15–205mm, all Z) | Fold-end slots (Z=159.6–179.6mm and Z=219.6–239.6mm) | Ribs would pass through slot zones | Ribs are absent within slot Z ranges. Three rib segments per affected rib: Z=0–159.6mm, Z=179.6–219.6mm, Z=239.6–240mm. Ribs at X=5mm and X=215mm are unaffected (outside slot X range). |
| Fold-end slots (Y=0 to Y=10mm) | Rear face tab slots (Y=35mm to Y=20mm) | Could intersect if body is too shallow | No intersection. Front slots end at Y=10mm; rear slots start at Y=20mm. 10mm gap of solid material. ✓ |

### Rear Face Interactions

| Feature A | Feature B | Interaction | Resolution |
|-----------|-----------|-------------|------------|
| Lower cradle slots (X=8mm) | Upper cradle slots (X=212mm) | Could overlap in Z | Resolved by mirrored cradle orientation: lower cradle inboard = left (X=8mm), upper cradle inboard = right (X=212mm). Slots are on opposite X sides of the rear face. No Z overlap conflict remains. |
| L3 slot (Z=111.0–119.2mm, X=8mm) | U1 slot (Z=116.5–124.7mm, X=212mm) | Would overlap in Z if both at X=8mm | Resolved by X separation above. L3 at X=8mm, U1 at X=212mm — no interference. ✓ |

### Body Depth Interactions

| Feature | From face | Depth |
|---------|-----------|-------|
| Fold-end slots | Front face (Y=0) | 10mm (to Y=10mm) |
| Tab slots | Rear face (Y=35mm) | 15mm (to Y=20mm) |
| Gap between zones | — | Y=10mm to Y=20mm = 10mm solid material |

---

## 8. Complete Dimension Table

| Feature | Parameter | Value | Spine frame |
|---------|-----------|-------|-------------|
| Body | Width | 220mm | X=0 to X=220mm |
| Body | Depth | 35mm | Y=0 to Y=35mm |
| Body | Height | 240mm | Z=0 to Z=240mm |
| Ribs (×22) | Protrusion | 1.5mm | Z=−1.5mm to Z=0 (below front face) |
| Ribs (×22) | Width in Y | 0.8mm | At Y=0 |
| Ribs (×22) | Spacing | 10mm pitch | X=5, 15, 25 ... 215mm |
| Fold slot (lower) | X range | X=12.5 to X=207.5mm | — |
| Fold slot (lower) | Z range | Z=159.6 to Z=179.6mm | Center Z=169.6mm |
| Fold slot (lower) | Depth | 10mm | Y=0 to Y=10mm |
| Fold slot (upper) | X range | X=12.5 to X=207.5mm | — |
| Fold slot (upper) | Z range | Z=219.6 to Z=239.6mm | Center Z=229.6mm |
| Fold slot (upper) | Depth | 10mm | Y=0 to Y=10mm |
| Tab slot L1 (lower cradle) | Z center | 60.6mm | Z=56.5 to Z=64.7mm |
| Tab slot L2 (lower cradle) | Z center | 88.2mm | Z=84.1 to Z=92.3mm |
| Tab slot L3 (lower cradle) | Z center | 115.1mm | Z=111.0 to Z=119.2mm |
| Tab slot L4 (lower cradle) | Z center | 142.7mm | Z=138.6 to Z=146.8mm |
| Tab slots L1–L4 | X position | X=8.0mm | X=6.9 to X=9.1mm (2.2mm wide) |
| Tab slot U1 (upper cradle) | Z center | 120.6mm | Z=116.5 to Z=124.7mm |
| Tab slot U2 (upper cradle) | Z center | 148.2mm | Z=144.1 to Z=152.3mm |
| Tab slot U3 (upper cradle) | Z center | 175.1mm | Z=171.0 to Z=179.2mm |
| Tab slot U4 (upper cradle) | Z center | 202.7mm | Z=198.6 to Z=206.8mm |
| Tab slots U1–U4 | X position | X=212.0mm | X=210.9 to X=213.1mm (2.2mm wide) |
| All tab slots | Depth | 15mm | Y=35mm to Y=20mm |
| All tab slots | Z width | 8.2mm | ±4.1mm from Z center |
| Snap post (left lower) | Root center | (X=0, Y=17.5, Z=30mm) | Protrudes to X=−8mm |
| Snap post (left upper) | Root center | (X=0, Y=17.5, Z=70mm) | Protrudes to X=−8mm |
| Snap post (right lower) | Root center | (X=220, Y=17.5, Z=30mm) | Protrudes to X=228mm |
| Snap post (right upper) | Root center | (X=220, Y=17.5, Z=70mm) | Protrudes to X=228mm |
| Snap posts | Cross-section | 10mm (Z) × 6mm (Y) stadium | YZ plane |
| Snap posts | Protrusion length | 8mm | In ±X direction |
| Snap post flange | Position from root | 6mm (2mm from tip) | Along protrusion axis |
| Snap post flange | Ridge height | 1.5mm circumferential | Radially outward |
| Snap post flange | Lead-in | 30° taper on entry side | — |
| Snap post flange | Retention face | 90° perpendicular on root side | — |

---

## 9. Open Flags for Parts Specification

1. **Spine height margin above upper fold-end slot (Z=240mm vs Z=245mm):** The upper fold-end slot top edge is at Z=239.6mm. The resolved spine height of 240mm leaves only 0.4mm of material above the slot. Parts specification should evaluate whether this is structurally adequate or whether 245mm is required. The additional 5mm does not affect print bed fit (still well within 325mm × 320mm × 320mm envelope). Recommend **245mm** for production and note it as the conservative value; 240mm is the minimum.

2. **Cradle orientation convention (lower = left inboard, upper = right inboard):** The resolution of the tab slot overlap required designating the lower cradle as left-inboard and the upper cradle as right-inboard. This means the two cradle instances are installed as mirrors of each other. The cradle part is symmetric and supports both orientations — but the assembly instruction must specify this clearly. Parts.md for the spine must note this assembly requirement on the slot table.

3. **Tab slot X width (2.2mm in X):** The tab body is 2mm thick in Y (cradle frame) / X (spine frame). The 0.2mm clearance is per requirements.md. The slot at X=8mm extends from X=6.9 to X=9.1mm. Verify the spine has adequate material outside the slot (X=0 to X=6.9mm = 6.9mm of material from the spine end face). This is above the 1.2mm structural wall minimum. ✓

4. **Rib continuity at fold-end slot zones:** The rib segments above the upper fold-end slot are very short: Z=239.6mm to Z=240mm = 0.4mm. These micro-segments should be omitted in modeling; they provide no structural or visual value and would be a print artifact. Rule: omit rib segments shorter than 5mm. For affected ribs at X=15–205mm, the third segment (Z=239.6 to Z=240mm) is omitted. Parts specification should apply this rule.
