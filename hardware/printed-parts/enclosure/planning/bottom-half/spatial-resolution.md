# Enclosure Bottom Half — Spatial Resolution

**Date:** 2026-03-29
**Role:** Pre-compute all geometry for the bottom half so the 4b specification agent can write every dimension without performing coordinate math.
**Inputs:** requirements.md, vision.md, concept.md, synthesis.md, decomposition.md, snap-fit-geometry.md, display-switch-dimensions.md, back-panel-ports.md, pump-cartridge/concept.md

---

## Reference Frame

**Part:** Enclosure bottom half
**Print orientation:** Exterior bottom face on build plate (base-down). This is also the installed orientation — no rotation needed between print and installation.

| Axis | Direction | Range |
|------|-----------|-------|
| X | Width, left to right (viewed from front) | 0 → 220 mm |
| Y | Depth, front to back (front = user-facing face, rear = back of enclosure) | 0 → 300 mm |
| Z | Height, bottom to top | 0 → 185 mm |

**Origin:** Exterior bottom-left-front corner of the part.

**Envelope:** 220 × 300 × 185 mm → X:[0, 220] Y:[0, 300] Z:[0, 185]

**Transform summary:** The part prints base-down and installs base-down. The reference frame origin is at the same corner in both the print and installed orientations. No rotation, no flip, no axis relabeling. Print frame = installed frame. Confirmed self-consistent.

---

## 1. Box Shell Geometry

All values in bottom half part frame.

### Wall thickness

| Wall | Nominal thickness | Derived from |
|------|-------------------|--------------|
| All exterior walls | 2.4 mm | concept.md Section 5 — 6 perimeters at 0.4 mm nozzle |
| Interior floor | 2.4 mm | concept.md Section 5 |
| Interior dividing wall (pump/valve zone) | 2.0 mm | concept.md Section 5 |

### Exterior face positions (each face's exterior surface)

| Face | Exterior surface position | Part frame |
|------|--------------------------|------------|
| Bottom (floor exterior) | Z = 0 | Bottom half part frame |
| Front | Y = 0 | Bottom half part frame |
| Rear | Y = 300 | Bottom half part frame |
| Left | X = 0 | Bottom half part frame |
| Right | X = 220 | Bottom half part frame |
| Top seam face | Z = 185 | Bottom half part frame |

### Interior face positions (each wall's interior surface)

| Wall | Interior face position | Derived from |
|------|------------------------|--------------|
| Front wall interior | Y = 2.4 | Y=0 exterior + 2.4 mm wall |
| Rear wall interior | Y = 297.6 | Y=300 exterior − 2.4 mm wall |
| Left wall interior | X = 2.4 | X=0 exterior + 2.4 mm wall |
| Right wall interior | X = 217.6 | X=220 exterior − 2.4 mm wall |
| Interior floor top surface | Z = 2.4 | Z=0 exterior bottom + 2.4 mm floor thickness |
| Top seam interior face | Z = 185 | Top edge of walls — no thickness added here; seam face is the wall top |

### Interior cavity bounds

| Axis | Range | Derived from |
|------|-------|--------------|
| X | [2.4, 217.6] | Left interior at 2.4, right interior at 217.6 |
| Y | [2.4, 297.6] | Front interior at 2.4, rear interior at 297.6 |
| Z | [2.4, 185] | Floor top at 2.4, top seam face at 185 |

**Interior cavity dimensions:** 215.2 mm wide × 295.2 mm deep × 182.6 mm tall

### Interior dividing wall (pump/valve zone separator)

Positioned at approximately 175 mm from the front face exterior (Y = 0), per concept.md. This wall runs left-to-right and serves as the rear stop for the dock cradle.

| Feature | Position | Derived from |
|---------|----------|--------------|
| Dividing wall front face | Y = 175 | concept.md: ~175 mm from front face |
| Dividing wall rear face | Y = 177 | 175 mm + 2.0 mm wall thickness |
| Dividing wall X extent | X: [2.4, 217.6] | Runs between left and right interior walls |
| Dividing wall Z extent | Z: [2.4, 185] | Floor to top seam face |

---

## 2. Front-Face Component Cutout Positions

All values in bottom half part frame. The front wall exterior is at Y = 0; interior face at Y = 2.4.

### Z-center resolution

**Component panel zone:** Z = 100 mm to Z = 185 mm (above dock opening, below seam).
Zone height = 85 mm. Zone center = (100 + 185) / 2 = **142.5 mm**.

**Prompt directive:** Place all three components at the same Z-center height (horizontal row).

**Governing constraint check (using the largest cutout — S3 at 48.2 mm square, half-height = 24.1 mm):**

| Constraint | Check |
|------------|-------|
| Bottom edge of S3 cutout must be above Z = 100 | 142.5 − 24.1 = 118.4 mm > 100 ✓ |
| Top edge of S3 cutout must be below Z = 180 | 142.5 + 24.1 = 166.6 mm < 180 ✓ |
| Bottom edge must be above Z = 50 | 118.4 mm > 50 ✓ |

**Resolved Z-center for all three components: Z = 142.5 mm**

This places the component band from Z = 118.4 mm (bottom of S3) to Z = 166.6 mm (top of S3), with 18.4 mm of clear surface above the dock opening and 18.4 mm of clear surface below the seam breathing zone.

### Lateral separation check (minimum 5 mm material between cutout edges)

| Adjacent pair | X separation (center-to-center) | Left radius | Right radius | Gap between edges |
|---------------|----------------------------------|-------------|--------------|-------------------|
| RP2040 ↔ S3 | 110 − 55 = 55 mm | 16.6 mm (RP2040 radius) | 24.1 mm (S3 half-width) | 55 − 16.6 − 24.1 = **14.3 mm** ✓ |
| S3 ↔ KRAUS | 165 − 110 = 55 mm | 24.1 mm (S3 half-width) | 16.0 mm (KRAUS radius) | 55 − 24.1 − 16.0 = **14.9 mm** ✓ |

Both gaps exceed the 5 mm minimum. No overlap. The 14+ mm gaps also provide adequate visual breathing room between components.

### Resolved cutout center positions

All three components share Z-center = 142.5 mm. The front face pocket depth extends into the interior from the front wall interior face at Y = 2.4.

| Component | X_center | Y (front wall interior face) | Z_center | Derived from |
|-----------|----------|------------------------------|----------|--------------|
| RP2040 | 55.0 mm | 2.4 mm | 142.5 mm | synthesis.md X=55; Z resolved above |
| S3 CrowPanel | 110.0 mm | 2.4 mm | 142.5 mm | synthesis.md X=110 (centered on 220 mm face); Z resolved above |
| KRAUS air switch | 165.0 mm | 2.4 mm | 142.5 mm | synthesis.md X=165; Z resolved above |

### Individual cutout geometry

#### RP2040 (Waveshare 0.99" round LCD)

| Dimension | Value | Derived from |
|-----------|-------|--------------|
| Cutout shape | Circle | display-switch-dimensions.md |
| Cutout diameter | 33.2 mm | 33.0 mm nominal + 0.2 mm FDM loose-fit correction (requirements.md) |
| Cutout center X | 55.0 mm | synthesis.md |
| Cutout center Z | 142.5 mm | resolved above |
| Through-hole Y range | Y: [0, 2.4] | Full front wall thickness — through-hole, no pocket needed for module body (9.8 mm depth handled by interior space) |
| Front edge chamfer | 0.5 mm × 45° on outer rim | concept.md / synthesis.md |
| Cutout edge at leftmost | X = 55.0 − 16.6 = 38.4 mm | |
| Cutout edge at rightmost | X = 55.0 + 16.6 = 71.6 mm | |
| Cutout edge at bottom | Z = 142.5 − 16.6 = 125.9 mm | |
| Cutout edge at top | Z = 142.5 + 16.6 = 159.1 mm | |
| Retention pocket depth | Retention ring is a separate part — bottom half provides through-hole only. Gap 3 from concept.md applies: bayonet vs. separate part unresolved; the bottom half's contribution is the 33.2 mm through-hole. | |

#### S3 CrowPanel 1.28" Rotary Display

The S3 has a 33.1 mm module depth. The front wall is only 2.4 mm thick. A through-pocket (the full module depth) must be cut from Y = 2.4 into the interior.

| Dimension | Value | Derived from |
|-----------|-------|--------------|
| Cutout shape | Square | synthesis.md: 48.2 mm square (48 mm housing + 0.2 mm FDM clearance) |
| Cutout width (X) | 48.2 mm | 48 mm nominal + 0.2 mm FDM correction |
| Cutout height (Z) | 48.2 mm | same |
| Cutout center X | 110.0 mm | synthesis.md |
| Cutout center Z | 142.5 mm | resolved above |
| Cutout X range | X: [110.0 − 24.1, 110.0 + 24.1] = **[85.9, 134.1]** | |
| Cutout Z range | Z: [142.5 − 24.1, 142.5 + 24.1] = **[118.4, 166.6]** | |
| Through-hole Y range | Y: [0, 2.4] | Full front wall thickness — visible opening |
| Module pocket Y range | Y: [2.4, 35.5] | Y=2.4 (front wall interior face) + 33.1 mm module depth = 35.5 mm. Pocket extends 33.1 mm into the interior. |
| Pocket width (X) | 48.2 mm | same as through-hole |
| Pocket height (Z) | 48.2 mm | same as through-hole |
| Front edge chamfer | 0.5 mm × 45° on outer rim | synthesis.md |
| Knob rotation clearance | Cutout diameter 48.2 mm accommodates the 47.3 mm knob ring with 0.45 mm clearance per side — within the 0.5 mm minimum per synthesis.md (acceptable; verify with test print) | |

**Note:** The pocket at Y:[2.4, 35.5] for the S3 module must not conflict with any interior feature in that volume at X:[85.9, 134.1], Z:[118.4, 166.6]. This zone is clear of dock cradle geometry (dock is forward of Y=175 dividing wall, so Y < 175; pocket extends only to Y=35.5 — fully in the front wall zone, clear of dock cradle).

#### KRAUS KWDA-100MB Air Switch

| Dimension | Value | Derived from |
|-----------|-------|--------------|
| Cutout shape | Circle | display-switch-dimensions.md |
| Cutout diameter | 32.0 mm | 31.75 mm nominal (standard 1-1/4" faucet hole) + 0.2 mm FDM loose-fit correction |
| Cutout center X | 165.0 mm | synthesis.md |
| Cutout center Z | 142.5 mm | resolved above |
| Through-hole Y range | Y: [0, 2.4] | Full front wall thickness — the ABS nut retains from behind |
| Interior clearance depth | ≥ 50 mm behind panel face (38.1 mm stem + nut + tube fitting). Clear to Y = 52.4 (2.4 + 50). This zone is open interior space at X=165, well clear of the dock cradle. | |
| Front edge chamfer | 0.5 mm × 45° on outer rim | synthesis.md |
| Cutout edge at leftmost | X = 165.0 − 16.0 = 149.0 mm | |
| Cutout edge at rightmost | X = 165.0 + 16.0 = 181.0 mm | |
| Cutout edge at bottom | Z = 142.5 − 16.0 = 126.5 mm | |
| Cutout edge at top | Z = 142.5 + 16.0 = 158.5 mm | |

---

## 3. Dock Opening — Front Face

All values in bottom half part frame.

### Derivation

The pump cartridge is 155 mm wide × 75 mm tall × ~170 mm deep (pump-cartridge/concept.md Section 5, design language: "approximately 155 mm wide × 170 mm deep × 75 mm tall").

**Opening width resolution:**

| Step | Calculation | Result |
|------|-------------|--------|
| Cartridge width | — | 155.0 mm |
| FDM clearance (0.2 mm per side) | 155 + 2 × 0.2 | 155.4 mm |
| Reveal frame step (1 mm per side) | 155.4 + 2 × 1.0 | 157.4 mm |
| Adopted opening width | Round to nearest 0.5 mm | **157.0 mm** |

The 1 mm reveal frame step on each side means the wall has a 1 mm wide × 2 mm × 45° chamfer border framing the opening — the cartridge front face is visually framed, not flush to raw cutout edges. This matches the "aperture, not a hole" intent from concept.md.

**Opening height resolution:**

The dock opening extends from the bottom of the front wall (Z = 0) upward. The cartridge sits on the interior floor at Z = 2.4. The cartridge is 75 mm tall, so its top is at Z = 2.4 + 75 = 77.4 mm. Adding clearance for user hand access (palm-up grasp):

| Step | Calculation | Result |
|------|-------------|--------|
| Cartridge top | 2.4 + 75 | 77.4 mm |
| Clearance for hand (top of opening above cartridge top) | 77.4 + 2.6 mm margin | 80.0 mm |
| Adopted opening top | — | **Z = 80 mm** |
| Opening Z range | Z: [0, 80] | 80 mm tall opening |

The opening begins at Z = 0 (the very bottom of the front wall exterior face) — no sill at the bottom. The dock cradle floor inside aligns with the interior floor at Z = 2.4, so the cartridge slides in at Z = 2.4 level. The 2.4 mm below the cartridge floor is the wall floor thickness visible as a thin ledge on each side of the opening.

**Opening Y extent:** The dock opening is a through-hole in the front wall: Y: [0, 2.4] (full front wall thickness).

**Opening X range (centered at X = 110):**

| Calculation | Result |
|-------------|--------|
| Half-width: 157 / 2 | 78.5 mm |
| X_min: 110 − 78.5 | **X = 31.5 mm** |
| X_max: 110 + 78.5 | **X = 188.5 mm** |

**Confirmed X ranges:** Wall material to the left of opening: X:[0, 31.5] = 31.5 mm. Wall material to the right: X:[188.5, 220] = 31.5 mm. Both sides are symmetric, providing 31.5 mm of solid wall on each side of the dock opening.

### Dock opening resolved dimensions

| Dimension | Value | Derived from |
|-----------|-------|--------------|
| Opening width | 157.0 mm | 155 mm cartridge + 0.2 mm clearance per side + 1 mm reveal frame per side |
| Opening height | 80.0 mm | Cartridge height 75 mm + 2.4 mm floor + clearance, opening from Z=0 |
| Opening X range | X: [31.5, 188.5] | Centered at X=110, ±78.5 mm |
| Opening Y range | Y: [0, 2.4] | Full front wall through-cut |
| Opening Z range | Z: [0, 80] | Bottom of front wall to Z=80 mm |
| Opening X center | X = 110.0 mm | Centered on 220 mm face |
| Perimeter chamfer | 2 mm × 45° on all four edges of the dock opening | concept.md |
| Material left of opening | 31.5 mm | X: [0, 31.5] |
| Material right of opening | 31.5 mm | X: [188.5, 220] |

---

## 4. Snap Arms on Top Edge (Z = 185 mm)

All values in bottom half part frame. Snap arms protrude horizontally inward from the interior face of the top seam-edge wall. All arm positions are given as the arm centerline position in the face-parallel direction.

### Arm geometry (from snap-fit-geometry.md and synthesis.md)

| Parameter | Value |
|-----------|-------|
| Arm length | 18.0 mm (extends inward from wall interior face) |
| Arm thickness at root | 2.0 mm |
| Arm thickness at tip | 1.4 mm (tapered) |
| Arm width | 8.0 mm |
| Hook height | 1.2 mm |
| Lead-in angle | 30° |
| Retention face angle | 90° (permanent) |
| Root fillet | 0.3 mm radius |
| Hook undercut support interface gap | 0.2 mm |
| Break-away tabs | 0.3 mm wide × 0.3 mm tall, 2 per hook at 2 mm and 6 mm from one edge |

### Front face snap arms (Y = 0 exterior, Y = 2.4 interior face)

5 arms on the 220 mm front face. Centered on 220 mm span at 40 mm pitch.
Span covered by 5 arms: 4 × 40 = 160 mm. Start position from left: (220 − 160) / 2 = 30 mm.

| Arm | X_center | Y (arm axis, inward from front wall interior face) | Z (arm base) |
|-----|----------|---------------------------------------------------|--------------|
| F1 | **30.0 mm** | 2.4 mm | 185 mm |
| F2 | **70.0 mm** | 2.4 mm | 185 mm |
| F3 | **110.0 mm** | 2.4 mm | 185 mm |
| F4 | **150.0 mm** | 2.4 mm | 185 mm |
| F5 | **190.0 mm** | 2.4 mm | 185 mm |

Corner clearance: F1 at X=30 mm from left corner (X=0) — **30 mm clearance** ✓ (≥ 15 mm required).
F5 at X=190 from left corner, 220−190 = **30 mm clearance** from right corner ✓.

Arm protrudes inward: from Y=2.4 to Y=2.4+18=20.4 mm (arm tip at Y=20.4 mm).

### Rear face snap arms (Y = 300 exterior, Y = 297.6 interior face)

5 arms on the 220 mm rear face. Same X positions as front face arms (symmetric).

| Arm | X_center | Y (arm axis, inward from rear wall interior face) | Z (arm base) |
|-----|----------|--------------------------------------------------|--------------|
| R1 | **30.0 mm** | 297.6 mm | 185 mm |
| R2 | **70.0 mm** | 297.6 mm | 185 mm |
| R3 | **110.0 mm** | 297.6 mm | 185 mm |
| R4 | **150.0 mm** | 297.6 mm | 185 mm |
| R5 | **190.0 mm** | 297.6 mm | 185 mm |

Arm protrudes inward: from Y=297.6 to Y=297.6−18=279.6 mm (arm tip at Y=279.6 mm).

### Left face snap arms (X = 0 exterior, X = 2.4 interior face)

7 arms on the 300 mm left face. Centered on 300 mm span at 40 mm pitch.
Span covered by 7 arms: 6 × 40 = 240 mm. Start position from front: (300 − 240) / 2 = 30 mm.

| Arm | Y_center | X (arm axis, inward from left wall interior face) | Z (arm base) |
|-----|----------|--------------------------------------------------|--------------|
| L1 | **30.0 mm** | 2.4 mm | 185 mm |
| L2 | **70.0 mm** | 2.4 mm | 185 mm |
| L3 | **110.0 mm** | 2.4 mm | 185 mm |
| L4 | **150.0 mm** | 2.4 mm | 185 mm |
| L5 | **190.0 mm** | 2.4 mm | 185 mm |
| L6 | **230.0 mm** | 2.4 mm | 185 mm |
| L7 | **270.0 mm** | 2.4 mm | 185 mm |

Corner clearance: L1 at Y=30 mm from front corner (Y=0) — **30 mm clearance** ✓.
L7 at Y=270 from front, 300−270 = **30 mm clearance** from rear corner ✓.

Arm protrudes inward: from X=2.4 to X=2.4+18=20.4 mm (arm tip at X=20.4 mm).

### Right face snap arms (X = 220 exterior, X = 217.6 interior face)

7 arms on the 300 mm right face. Same Y positions as left face arms (symmetric).

| Arm | Y_center | X (arm axis, inward from right wall interior face) | Z (arm base) |
|-----|----------|---------------------------------------------------|--------------|
| RL1 | **30.0 mm** | 217.6 mm | 185 mm |
| RL2 | **70.0 mm** | 217.6 mm | 185 mm |
| RL3 | **110.0 mm** | 217.6 mm | 185 mm |
| RL4 | **150.0 mm** | 217.6 mm | 185 mm |
| RL5 | **190.0 mm** | 217.6 mm | 185 mm |
| RL6 | **230.0 mm** | 217.6 mm | 185 mm |
| RL7 | **270.0 mm** | 217.6 mm | 185 mm |

Arm protrudes inward: from X=217.6 to X=217.6−18=199.6 mm (arm tip at X=199.6 mm).

### Corner alignment pins (on top seam face, Z = 185)

Pins are 4.0 mm diameter, 8.0 mm tall, centered in the wall cross-section at each corner. Wall thickness = 2.4 mm, so wall centerline is at 1.2 mm from each exterior face. Pin centers are placed 10 mm from each corner edge (to pin centerline), per synthesis.md.

| Pin | X_center | Y_center | Z_base | Z_tip | Derived from |
|-----|----------|----------|--------|-------|--------------|
| Front-left | **10.0 mm** | **10.0 mm** | 185 mm | 193 mm | synthesis.md: 10 mm from each corner edge; corner at X=0, Y=0 |
| Front-right | **210.0 mm** | **10.0 mm** | 185 mm | 193 mm | 220 − 10 = 210 |
| Rear-left | **10.0 mm** | **290.0 mm** | 185 mm | 193 mm | 300 − 10 = 290 |
| Rear-right | **210.0 mm** | **290.0 mm** | 185 mm | 193 mm | |

**Wall centering check:** Pin center at X=10 is within the left wall (X:[0, 2.4]) — no, X=10 is 10 mm from the corner edge, inside the enclosure proper. Per synthesis.md the spec is "10 mm from each corner edge to pin centerline." The pins don't need to be centered in the wall cross-section; they are positioned 10 mm from the corner edge along each wall face direction. This places them in the corner region of the seam face where they are surrounded by wall material on two sides. Confirmed: pins at (10, 10), (210, 10), (10, 290), (210, 290) each have ≥ 7.6 mm of surrounding material (10 mm from edge, minus 4 mm diameter / 2 = 2 mm radius → 8 mm to nearest exterior edge, well above minimum).

Pin tip chamfer: 1.0 mm × 45°, per synthesis.md.

---

## 5. Tongue Position (Top Mating Face)

All values in bottom half part frame. The tongue protrudes upward from Z = 185 (the seam face), growing in the +Z direction from Z = 185 to Z = 189 (4 mm tongue height).

### Tongue cross-section (from snap-fit-geometry.md and synthesis.md)

| Parameter | Value |
|-----------|-------|
| Tongue width | 3.0 mm |
| Tongue height (protrudes above Z = 185) | 4.0 mm |
| Tongue tip Z | 185 + 4.0 = **189.0 mm** |
| Tongue base chamfer | 0.3 mm × 45° |
| Tongue tip chamfer | 0.5 mm × 30° |

### Tongue path derivation

The tongue is set 2 mm inward from the exterior wall surface (synthesis.md Section 2; concept.md Section 2). Wall thickness = 2.4 mm, so the interior face of the wall is at 2.4 mm from the exterior face.

"2 mm setback from exterior wall" means the tongue's **exterior-facing side** (the side nearest the exterior wall) is at 2 mm from the exterior surface.

| Wall | Tongue near face | Tongue far face | Tongue centerline |
|------|-----------------|-----------------|-------------------|
| Left (exterior at X=0) | X = 2.0 mm | X = 5.0 mm | X = 3.5 mm |
| Right (exterior at X=220) | X = 218.0 mm | X = 215.0 mm | X = 216.5 mm |
| Front (exterior at Y=0) | Y = 2.0 mm | Y = 5.0 mm | Y = 3.5 mm |
| Rear (exterior at Y=300) | Y = 298.0 mm | Y = 295.0 mm | Y = 296.5 mm |

The tongue runs as a continuous rectangular frame. The corners are mitered at 45° where the tongue turns from one face to the next.

### Tongue frame bounds (the rectangular path the tongue traces, expressed as outer bounds)

| Dimension | Value | Derived from |
|-----------|-------|--------------|
| X range of tongue path (left and right arms) | Left: X center = 3.5 mm; Right: X center = 216.5 mm | 2 mm setback from X=0 and X=220 |
| Y range of tongue path (front and rear arms) | Front: Y center = 3.5 mm; Rear: Y center = 296.5 mm | 2 mm setback from Y=0 and Y=300 |
| Tongue body occupies (X, left arm): | X: [2.0, 5.0] | exterior face of tongue to interior face |
| Tongue body occupies (X, right arm): | X: [215.0, 218.0] | |
| Tongue body occupies (Y, front arm): | Y: [2.0, 5.0] | |
| Tongue body occupies (Y, rear arm): | Y: [295.0, 298.0] | |

**Compact statement for the specification agent:** The tongue traces a rectangular frame on the seam face (Z = 185). The tongue centerline path is:
- Left arm: X = 3.5, running Y: [3.5, 296.5]
- Right arm: X = 216.5, running Y: [3.5, 296.5]
- Front arm: Y = 3.5, running X: [3.5, 216.5]
- Rear arm: Y = 296.5, running X: [3.5, 216.5]

The tongue body (3 mm wide) spans ±1.5 mm from centerline on each arm. The tongue protrudes from Z = 185 to Z = 189.

**Note on dock opening interruption:** The tongue on the front face arm runs at Y = 3.5, X: [3.5, 216.5]. The dock opening occupies X: [31.5, 188.5] through the full front wall. The tongue at Y = 3.5 on the front face crosses the dock opening zone. The tongue must be interrupted (or stepped around) at the dock opening. Recommended: the front-face tongue arm terminates at X = 31.5 and resumes at X = 188.5, leaving a 157 mm gap corresponding to the dock opening width. The tongue continues uninterrupted on the other three faces. This is consistent with concept.md intent (dock opening is a full aperture, no material at Y = 0 across the opening span at Z = 0–80).

**Tongue interruption at dock opening:**
- Front face tongue left segment: X: [3.5, 31.5], Y = 3.5, Z: [185, 189]
- Front face tongue right segment: X: [188.5, 216.5], Y = 3.5, Z: [185, 189]
- Left face tongue: X = 3.5, Y: [3.5, 296.5], Z: [185, 189] — uninterrupted
- Right face tongue: X = 216.5, Y: [3.5, 296.5], Z: [185, 189] — uninterrupted
- Rear face tongue: Y = 296.5, X: [3.5, 216.5], Z: [185, 189] — uninterrupted

---

## 6. Feet on Bottom Exterior

All values in bottom half part frame. Feet are integral printed pads on the exterior bottom face (Z = 0), extending downward from Z = 0.

Since the part's Z origin is at the exterior bottom face, feet protrude in the −Z direction from the print reference frame. In the installed orientation, feet protrude downward from the device base.

### Foot geometry (from concept.md)

| Parameter | Value | Derived from |
|-----------|-------|--------------|
| Foot shape | Circular cylinder | concept.md |
| Foot diameter | 15 mm | concept.md |
| Foot height | 3 mm | concept.md: "approximately 3–5 mm"; minimum for stable base and build-plate adhesion zone clearance; 3 mm chosen as minimum sufficient |
| Foot top surface Z | 0 mm (flush with exterior bottom face) | Feet are integral protrusions below Z=0 |
| Foot bottom surface Z | −3 mm | Z = 0 − 3 mm |
| Inset from corner edges | 15 mm from each adjacent edge to foot center | concept.md: "inset 15 mm from each corner edge" |

### Foot center positions

| Foot | X_center | Y_center | Z_top | Z_bottom | Derived from |
|------|----------|----------|-------|----------|--------------|
| Front-left | **15.0 mm** | **15.0 mm** | 0 mm | −3 mm | 15 mm from X=0 edge, 15 mm from Y=0 edge |
| Front-right | **205.0 mm** | **15.0 mm** | 0 mm | −3 mm | 220 − 15 = 205 mm |
| Rear-left | **15.0 mm** | **285.0 mm** | 0 mm | −3 mm | 300 − 15 = 285 mm |
| Rear-right | **205.0 mm** | **285.0 mm** | 0 mm | −3 mm | |

**Stability check:** Foot pattern spans 190 mm × 270 mm. The enclosure footprint is 220 × 300 mm. Foot centers are 15 mm from edges, providing stable 4-point support. Tipping angle: arctan(190/2 / 300) ≈ arctan(0.317) ≈ 17.6° in the X direction; arctan(270/2 / 220) ≈ arctan(0.614) ≈ 31.5° in the Y direction. Adequate stability in both directions.

**Elephant's foot note:** A 0.3 mm × 45° chamfer is applied to the bottom perimeter edge of the bottom half (the outermost edges at Z = 0), per requirements.md and concept.md. This prevents first-layer flare from creating visible irregularity at the base.

---

## 7. Interior Snap Pockets for Dock Cradle

All values in bottom half part frame. Pockets are cut into the interior floor surface (at Z = 2.4, facing upward in +Z).

### Dock cradle footprint derivation

From pump-cartridge/concept.md (dock cradle section and internal layout table):
- Cartridge dimensions: **155 mm wide × ~170 mm deep × 75 mm tall**
- Dock cradle provides rails, rear wall, and retention features for the cartridge
- The dock cradle footprint matches the cartridge plan dimensions: 155 mm wide × 170 mm deep

The dock cradle is centered on the front face (X center = 110 mm) and begins at the interior face of the front wall (Y = 2.4).

| Dock cradle dimension | Value | Derived from |
|-----------------------|-------|--------------|
| Width | 155 mm | Cartridge width — pump-cartridge/concept.md |
| Depth | 170 mm | Cartridge depth — pump-cartridge/concept.md |
| X center | 110.0 mm | Centered on 220 mm face = 220/2 |
| X_min of cradle footprint | 110.0 − 77.5 = **32.5 mm** | |
| X_max of cradle footprint | 110.0 + 77.5 = **187.5 mm** | |
| Y_min of cradle footprint | **2.4 mm** | Abutting interior face of front wall |
| Y_max of cradle footprint | 2.4 + 170 = **172.4 mm** | Front wall interior face + cradle depth |

The rear face of the dock cradle (Y = 172.4 mm) falls within the interior of the bottom half and contacts the interior dividing wall (which is at Y = 175 mm front face). This provides the rear stop for the cradle, with 2.6 mm of clearance between cradle rear and dividing wall face (sufficient for assembly tolerance).

### Snap pocket positions

Pockets are at the four corners of the dock cradle footprint. These are cut into the floor at Z = 2.4 (floor top surface).

| Pocket | X_center | Y_center | Z (floor surface) | Derived from |
|--------|----------|----------|-------------------|--------------|
| Front-left | **32.5 mm** | **2.4 mm** | 2.4 mm | X_min of cradle, Y_min of cradle |
| Front-right | **187.5 mm** | **2.4 mm** | 2.4 mm | X_max of cradle, Y_min of cradle |
| Rear-left | **32.5 mm** | **172.4 mm** | 2.4 mm | X_min of cradle, Y_max of cradle |
| Rear-right | **187.5 mm** | **172.4 mm** | 2.4 mm | X_max of cradle, Y_max of cradle |

**Pocket geometry (from pump-cartridge/concept.md dock cradle section):** The specific pocket dimensions (width, depth, overhang geometry for the snap feature) depend on the dock cradle's snap post geometry, which is defined in the dock cradle specification. The bottom half's floor carries blind pockets that accept the cradle's snap posts from above. Pocket geometry to be finalized in the dock cradle specification. The positions above are the pocket centerpoints.

**Floor clearance check:** Snap pockets at front corners (Y = 2.4) are directly adjacent to the front wall interior face. These pockets must not break through the front wall. Wall interior face is at Y = 2.4; pockets centered at Y = 2.4 with any reasonable pocket depth (e.g., 5 mm) in the Y direction would extend from Y = 2.4 ± 2.5 mm — the pocket would extend behind the wall (toward Y = 0) which violates the wall. Resolution: the front-edge pockets should be positioned at Y = 2.4 + (pocket_half_depth). If pocket depth in Y is 6 mm, front-pocket center Y = 2.4 + 3.0 = 5.4 mm. This is a refinement the 4b specification agent should apply once the dock cradle snap post depth is known. The X and Y coordinates above represent the geometric corner of the cradle footprint, not necessarily the pocket body center — the pocket body centers will be offset slightly inward from the footprint corners.

---

## 8. Summary Reference Table

All coordinates in bottom half part frame (origin: exterior bottom-left-front corner).

| Feature | Key position(s) |
|---------|----------------|
| Interior cavity | X:[2.4, 217.6] Y:[2.4, 297.6] Z:[2.4, 185] |
| Interior dividing wall (front face) | Y = 175.0 mm |
| RP2040 cutout center | X=55.0, Y=2.4, Z=142.5 (Φ33.2 mm, through Y:[0,2.4]) |
| S3 cutout center | X=110.0, Y=2.4, Z=142.5 (48.2×48.2 mm, through Y:[0,2.4], pocket to Y=35.5) |
| KRAUS cutout center | X=165.0, Y=2.4, Z=142.5 (Φ32.0 mm, through Y:[0,2.4]) |
| Dock opening | X:[31.5, 188.5] Y:[0, 2.4] Z:[0, 80] |
| Snap arms — front | X: 30, 70, 110, 150, 190 mm; at Y=2.4, Z=185 |
| Snap arms — rear | X: 30, 70, 110, 150, 190 mm; at Y=297.6, Z=185 |
| Snap arms — left | Y: 30, 70, 110, 150, 190, 230, 270 mm; at X=2.4, Z=185 |
| Snap arms — right | Y: 30, 70, 110, 150, 190, 230, 270 mm; at X=217.6, Z=185 |
| Alignment pins | (10,10), (210,10), (10,290), (210,290) at Z:185→193 |
| Tongue centerline | Left X=3.5; Right X=216.5; Front Y=3.5; Rear Y=296.5; Z:185→189 |
| Tongue front interruption | Gap at X:[31.5, 188.5] (dock opening span) |
| Feet centers | (15,15), (205,15), (15,285), (205,285) at Z:0→-3 |
| Dock cradle footprint | X:[32.5, 187.5] Y:[2.4, 172.4] |
| Dock cradle snap pockets | (32.5, 2.4), (187.5, 2.4), (32.5, 172.4), (187.5, 172.4) at Z=2.4 |

---

## 9. Transform Summary

| Check | Result |
|-------|--------|
| Print orientation | Base-down (exterior bottom face on build plate, Z axis growing upward from build plate) |
| Installed orientation | Base-down (device sits on its feet, Z axis growing upward) |
| Any rotation between print and installed? | None |
| Any axis relabeling between print and installed? | None |
| Origin in print frame | Exterior bottom-left-front corner |
| Origin in installed frame | Exterior bottom-left-front corner |
| Frame consistency | Print frame = installed frame. All coordinates in this document are valid in both contexts without any transformation. |

The part prints in its installed orientation. No rotation, flip, or axis transformation is needed. The 4b specification agent may use every coordinate in this document directly.

---

## 10. Open Items for Downstream Agents

These items were flagged in prior pipeline stages and remain unresolved. The 4b specification agent must resolve them before the CadQuery generation agent begins.

| Item | Source | Impact on this document |
|------|--------|------------------------|
| Gap 3 (concept.md): RP2040 retention ring — integral bayonet geometry vs. separate part | concept.md, decomposition.md | If integral: the RP2040 cutout geometry becomes a through-hole + bayonet slot pattern behind Y=2.4. If separate: the bottom half cutout is only the Φ33.2 mm through-hole as stated here. The position (X=55, Z=142.5) is unaffected. |
| Dock cradle snap post geometry | pump-cartridge spec (not yet written) | Snap pocket dimensions (body size, depth) at the 4 corners above. Pocket center offsets from footprint corners depend on post size. |
| Front face tongue interruption at dock opening | Resolved here | The tongue terminates at X=31.5 and resumes at X=188.5 on the front arm. This must be explicit in the 4b specification. |
| S3 pocket depth | display-switch-dimensions.md, confirmed here | Pocket extends to Y=35.5 (33.1 mm behind front wall interior face). The 4b agent must verify no interior feature occupies X:[85.9,134.1] Y:[2.4,35.5] Z:[118.4,166.6]. This is confirmed clear in this document (no dock cradle geometry extends past Y=2.4 at that Z height; dock cradle is in the lower Z region). |
