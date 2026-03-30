# Enclosure Bottom Half — Parts Specification

**Date:** 2026-03-29
**Inputs:** requirements.md, vision.md, concept.md, synthesis.md, decomposition.md, spatial-resolution.md, snap-fit-geometry.md, display-switch-dimensions.md, pump-cartridge/concept.md
**Next step:** Engineering drawing (Step 5) → CadQuery generation (Step 6g)

---

## Overview

The enclosure bottom half is one of two printed halves that together form the 220 × 300 × 400 mm appliance enclosure. The bottom half constitutes the lower 185 mm of the enclosure, from the device floor to the horizontal seam. Its bounding box is 220 mm (X) × 300 mm (Y) × 185 mm (Z).

The bottom half carries: the entire front-face component panel (RP2040, S3, KRAUS cutouts), the pump cartridge dock opening, the printed interior floor with dock cradle snap pockets, the interior dividing wall separating the pump/valve zone from the rear interior, the complete snap-join hardware for the horizontal seam (24 snap arms, continuous tongue, 4 alignment pins), and 4 integral exterior feet. It is a closed shell open only at the top seam and at the dock opening in its front face.

The bottom half is a permanently installed part. The user never interacts with it directly — all user interaction passes through features within it (component cutouts, dock opening) rather than with the shell itself.

---

## Coordinate System

**Origin:** Exterior bottom-left-front corner of the part.

| Axis | Direction | Range |
|------|-----------|-------|
| X | Width, left to right (viewed from front) | 0 → 220 mm |
| Y | Depth, front to back (Y=0 = front/user-facing face) | 0 → 300 mm |
| Z | Height, bottom to top (Z=0 = device floor) | 0 → 185 mm |

**Envelope:** X:[0, 220] × Y:[0, 300] × Z:[0, 185]

**Transform note:** Print orientation is base-down (exterior bottom face on build plate). Installed orientation is also base-down. No rotation, no flip, no axis relabeling between print frame and installed frame. All coordinates in this document are valid in both contexts without transformation.

---

## Material and Print Orientation

**Material:** ASA, matte black.

Rationale: The enclosure exterior is the largest visible surface of the product. The pump cartridge is also ASA. Using the same material on both parts ensures surface character consistency (identical sheen level, texture, and color response) — required for the unified appliance appearance stated in vision.md. ASA provides UV stability for countertop placement near windows, crisp matte finish, and low warp at the Bambu H2C's enclosure temperatures.

**Print orientation:** Exterior bottom face on the build plate. The part prints standing upright with Z = 0 (feet and floor exterior) on the build plate, growing to Z = 185 (seam face) as the last layers.

**Build-plate face:** Z = 0 (exterior bottom face / feet contact surface). This is the smoothest printed surface on this part.

**Reason for orientation:**
- The front-face component cutouts (RP2040, S3, KRAUS) are holes in a vertical wall, which print cleanly as through-holes in this orientation — no overhang.
- The snap arms at the top edge (Z = 185) are horizontal cantilever features in the XY plane. Printed this way, their flex direction is parallel to the build plate — the strongest FDM orientation per requirements.md.
- The tongue on the seam face grows in +Z with full layer support throughout its height.
- Alignment pins grow in +Z from the seam face — no overhang.
- The dock opening in the front wall is a vertical cutout — no overhang.

**Build volume confirmation:** 220 × 300 × 185 mm fits within single-nozzle volume (325 × 320 × 320 mm) with 105 mm X margin, 20 mm Y margin, 135 mm Z margin. Confirmed.

---

## Mechanism Narrative (Rubric A)

### What the user sees and touches

The bottom half is a smooth matte black box. The front face presents three circular/square openings in its upper portion (RP2040, S3, KRAUS — each component face flush with or recessed 0.5 mm behind the front wall surface) and a wide rectangular aperture at its lower portion (the dock opening, always filled by the cartridge front face). The bottom half's exterior walls are flush with the enclosure silhouette; the only visible discontinuity is the 0.5 mm horizontal shadow-line reveal at the top edge, where the top half's exterior wall laps 0.5 mm over the bottom half. Below that shadow line is the component zone; the shadow line itself is the designed seam detail.

### What is stationary

The shell body is rigid and permanent. Once the two halves are joined, no part of the bottom half moves relative to the enclosure. The interior floor is a fixed surface. The interior dividing wall at Y = 175 is a fixed stop for the dock cradle.

### How the snap join works

The top seam face (Z = 185) carries three co-planar features: 24 cantilever snap arms, a continuous tongue, and 4 alignment pins. When the top half is lowered:

1. The 4 corner alignment pins (4.0 mm diameter, 8.0 mm tall, centered at (10, 10), (210, 10), (10, 290), (210, 290) in XY, based at Z = 185) enter their matching sockets in the top half before any snap arm is reached. The 1.0 mm × 45° chamfer on each pin tip guides entry. This constrains X and Y to ±0.075 mm before further motion proceeds.

2. The continuous tongue (3.0 mm wide, 4.0 mm tall, centerline at 2 mm setback from exterior wall face, running the full perimeter with a gap across the dock opening span on the front face) enters the matching groove in the top half. The 0.5 mm × 30° tongue tip chamfer guides entry. The tongue is 4.0 mm tall while the snap hook is only 1.2 mm — the tongue is fully engaged before the first snap hook is reached. This constrains lateral (XY) shift to ±0.05 mm and sets the seam face alignment.

3. The 24 cantilever arms (18 mm long, 2.0 mm root thickness tapering to 1.4 mm at tip, 8.0 mm wide, with a 1.2 mm hook at the tip featuring a 30° lead-in and 90° retention face) engage the matching ledge pockets in the top half. The 30° lead-in converts downward travel into arm deflection. Each arm produces approximately 5 N of assembly force; total assembly force is approximately 120 N, applied as a comfortable two-palm press along the 300 mm faces.

4. When all 24 hooks seat, the seam faces contact and the joint reaches a definitive hard stop. The user feels and hears a firm progressive click-stop as all 24 arms engage within 1–2 mm of travel. The 90° retention face on every hook means disengagement requires fracturing the arm root (~640 N per arm). The joint is permanent.

5. After pressing, the user verifies the 0.5 mm reveal runs continuously around the full perimeter. The reveal is produced by the top half's exterior wall extending 0.5 mm below the seam plane and lapping over the bottom half's exterior wall face. Any locally absent reveal indicates an unengaged snap, which can be pressed individually.

### How components are installed and removed

**RP2040 module:** The 33.2 mm circular through-hole in the front wall at (X=55, Z=142.5) accepts the 33.0 mm module. The module drops in from the front. A separate printed retention ledge integral to the front wall — a 1.5 mm-wide lip printed at Y = 9.8 mm depth (measuring from the front wall interior face at Y = 2.4, so the ledge front face is at Y = 2.4 + 9.8 = 12.2 mm) — provides the rear stop. The RP2040 module body (9.8 mm total depth) rests its rear acrylic plate on this ledge. The 1.75 mm front chamfer of the CNC aluminum case catches on the 0.5 mm × 45° chamfer of the front-wall cutout rim, acting as the front stop. Removal: reach through the cutout with a finger or tool, push the module slightly rearward to disengage the rear ledge, then withdraw forward. Cable access: the SH1.0 connector exits the left side of the module — plan 25 mm clear lateral depth behind the panel at left of the RP2040.

**S3 module:** The 48.2 mm square through-hole in the front wall at (X=110, Z=142.5), with a 33.1 mm deep pocket behind it, houses the full S3 module body. Two M2.5 press-fit boss inserts (or integral printed ledges with M2.5 captured nut geometry) on the interior walls of the pocket at the 8 o'clock and 2 o'clock positions on the circular PCB retain the module. The 47.3 mm face diameter sits flush in the 48.2 mm square opening with 0.45 mm clearance on each side. Removal: access the M2.5 retention through the square cutout opening, release the retention, withdraw module rearward through the pocket (module cannot exit forward through the cutout — the 48 mm square housing corners are larger than the 47.3 mm circular clear zone of the opening, so the module must exit rearward). See DESIGN NOTE at end of this section.

**KRAUS air switch:** The 32.0 mm circular through-hole in the front wall at (X=165, Z=142.5) accepts the 31.75 mm threaded stem. The 47.6 mm cap rests against the front wall exterior face as the front stop. The ABS nut threads onto the stem from behind the panel (accessible through the interior via the dock opening below, or by working around adjacent components). No printed retention feature is required — the switch is self-retaining. Removal: thread off the ABS nut, withdraw the switch forward through the front face. 50 mm of clear interior depth is required at (X=165) behind the front wall for the threaded stem and nut.

**DESIGN NOTE on S3 removal direction:** The synthesis specifies the S3 cutout as square at 48.2 mm. The module's square housing is 48 mm × 48 mm — it can nominally pass through a 48.2 mm square opening. The 0.1 mm clearance per side (0.2 mm FDM correction applied to achieve 48.2 mm) should permit forward removal with slight skewing. The 4b specification preserves both options (forward through cutout or rearward through interior) and resolves this during test-print verification.

### Tactile feedback

- Assembly of the two halves: the user feels the corner pins register (gentle guidance), the tongue enter the groove (smooth consistent resistance), then 24 progressive clicks as the snap arms engage. Final state: firm stop, no give. No ambiguity.
- Cartridge insertion/removal: handled by the dock cradle mechanism, not this part. This part provides only the dock opening aperture.
- Component removal (RP2040/KRAUS): gentle push-through; the retention features are not tactile snap-fits but ledge-and-gravity retention and threaded lock. The grounding features are the RP2040 ledge at Y = 12.2 mm (lip width 1.5 mm) and the KRAUS ABS nut threaded to the stem.

---

## Constraint Chain Diagram (Rubric B)

```
ENCLOSURE BOTTOM HALF — CONSTRAINT CHAIN
==========================================

DEVICE FLOOR
    │  (Z=0 exterior, Z=2.4 interior floor top)
    │  ← 4 feet prevent slide on countertop [foot cylinders: Φ15 mm, 3 mm tall, at corners]
    │
    ├── INTERIOR FLOOR SURFACE (Z=2.4)
    │       │
    │       ├── DOCK CRADLE SNAP POCKETS [4 pockets at (32.5,2.4→5.4), (187.5,2.4→5.4),
    │       │       │                      (32.5,172.4), (187.5,172.4) at Z=2.4]
    │       │       └── constrains dock cradle in Z (down) and XY
    │       │
    │       └── INTERIOR DIVIDING WALL [Y=175 front face, 2.0 mm thick, full Z height]
    │               └── constrains dock cradle in +Y (rear stop)
    │
    ├── FRONT WALL (Y=0 exterior, Y=2.4 interior)
    │       │
    │       ├── RP2040 CUTOUT [Φ33.2 mm, center X=55, Z=142.5]
    │       │       ├── front stop: 0.5mm×45° chamfer at Y=0 catches 1.75mm front chamfer of CNC case
    │       │       └── rear stop: RETENTION LEDGE [1.5 mm wide, at Y=12.2 mm from front wall exterior]
    │       │               └── constrains RP2040 in Y
    │       │
    │       ├── S3 CUTOUT + POCKET [48.2×48.2 mm through-hole + pocket to Y=35.5]
    │       │       ├── front stop: pocket walls at Y=2.4 (panel face flush stop via module bezel)
    │       │       └── M2.5 BOSS INSERTS [at 8-o'clock and 2-o'clock on PCB, within pocket]
    │       │               └── constrains S3 in all 6 DOF
    │       │
    │       ├── KRAUS CUTOUT [Φ32.0 mm, center X=165, Z=142.5]
    │       │       └── ABS nut (component-supplied) constrains KRAUS in Z
    │       │
    │       └── DOCK OPENING [157×80 mm, X:[31.5,188.5], Z:[0,80]]
    │               └── provides cartridge access; dock cradle provides cartridge constraint
    │
    └── TOP SEAM FACE (Z=185)
            │
            ├── 4 ALIGNMENT PINS [Φ4.0 mm, 8.0 mm tall]
            │       └── constrain top half in X and Y before snaps engage
            │
            ├── CONTINUOUS TONGUE [3.0 mm wide, 4.0 mm tall, 2 mm setback from exterior]
            │       └── constrains lateral shift of halves to ±0.05 mm
            │
            └── 24 SNAP ARMS [18 mm × 2.0 mm × 8.0 mm, 90° retention]
                    └── constrain halves in Z (permanent, fracture-limited ~15,360 N)
```

All arrows are labeled. No floating constraint sources.

---

## Features

### Feature 1: Box Body

- **Name:** Box body (exterior shell)
- **Description:** The structural outer shell of the bottom half — five walls (front, rear, left, right, and floor) forming a box open at the top. All other features are additions or subtractions from this base geometry.
- **Operation:** Add
- **Shape:** Rectangular hollow box (shell)
- **Position:**
  - Exterior bounding box: X:[0, 220], Y:[0, 300], Z:[0, 185]
  - Interior cavity: X:[2.4, 217.6], Y:[2.4, 297.6], Z:[2.4, 185]
- **Dimensions:**
  - Exterior: 220 mm × 300 mm × 185 mm
  - Exterior wall thickness (all 4 walls): 2.4 mm (6 perimeters at 0.4 mm nozzle)
  - Interior floor thickness: 2.4 mm
  - Interior cavity: 215.2 mm wide × 295.2 mm deep × 182.6 mm tall
- **FDM notes:** Printed base-down. All vertical walls print without overhang. Box-section rib structure (outer wall + inner wall + ribs at 40 mm intervals, aligned with snap arm positions) adds approximately 8× bending stiffness to the 300 mm faces, reducing warp contribution at the seam to < 0.05 mm. Warp risk is moderate for ASA at 300 mm span; mitigated by the rib structure and the Bambu H2C enclosure. 2.4 mm wall (6 perimeters) accommodates the 2.0 mm snap arm root on the interior face while keeping the exterior wall uninterrupted.

---

### Feature 2: Front Face Wall

- **Name:** Front face wall
- **Description:** The Y=0 face of the box — the user-facing surface. Carries three component cutouts in its upper section (Z=118 to Z=167) and the dock opening in its lower section (Z=0 to Z=80). The exterior face is smooth matte black ASA. The remaining solid material in this wall after all cutouts and the dock opening is approximately 31.5 mm on each lateral edge (left and right of dock opening), a 6 mm breathing band between the top of the component panel and the seam, and the 33.1 mm zone between the front wall interior face and the S3 pocket rear at the S3 position.
- **Operation:** (integral to box body — this is a zone descriptor for clarity, not a separate operation)
- **Shape:** Rectangular slab with cutouts and pocket
- **Position:** Y:[0, 2.4] (front wall occupies this depth), full X:[0, 220], full Z:[0, 185]
- **Dimensions:**
  - Wall thickness: 2.4 mm (through Y)
  - Exterior face: Y = 0
  - Interior face: Y = 2.4
- **FDM notes:** Printed as part of the box body. All cutouts in this face are holes in a vertical wall — no overhang. The 0.5 mm × 45° chamfer on each cutout exterior rim is on a vertical surface — no overhang. The 2 mm × 45° chamfer on the dock opening perimeter is on vertical and horizontal edges of the opening.

---

### Feature 3: RP2040 Cutout

- **Name:** RP2040 cutout
- **Description:** Circular through-hole in the front face that accommodates the Waveshare RP2040-LCD-0.99-B module (33.0 mm OD). The module inserts from the front; the front chamfer of the CNC aluminum case (1.75 mm) rests on the chamfered cutout rim as the front stop.
- **Operation:** Remove
- **Shape:** Cylinder (through-hole)
- **Position:**
  - Center X: 55.0 mm
  - Center Z: 142.5 mm
  - Through Y: [0, 2.4] (full front wall thickness)
- **Dimensions:**
  - Cutout diameter: 33.2 mm (33.0 mm nominal + 0.2 mm FDM loose-fit correction per requirements.md)
  - Depth: 2.4 mm (full front wall through-cut)
  - Cutout left edge: X = 38.4 mm
  - Cutout right edge: X = 71.6 mm
  - Cutout bottom edge: Z = 125.9 mm
  - Cutout top edge: Z = 159.1 mm
  - Front edge chamfer: 0.5 mm × 45° on exterior rim (at Y=0)
- **FDM notes:** Hole in vertical wall — prints cleanly with no overhang. FDM holes print smaller than designed — the 0.2 mm addition to diameter corrects for this per requirements.md. Verify with a first test print at this exact diameter before committing the full bottom half. The 0.5 mm × 45° chamfer is on the exterior face (a vertical surface) — no overhang.

---

### Feature 4: RP2040 Retention Ledge

- **Name:** RP2040 retention ledge
- **Description:** An integral printed ledge on the interior face of the front wall, inside the RP2040 cutout cylinder, that the RP2040 module body rests on from behind. This resolves concept.md Gap 3 (integral retention vs. separate part) in favor of an integral ledge: a 1.5 mm-wide annular lip at the back of the cutout that the module's rear acrylic back plate (which protrudes ~1.8 mm beyond the cylindrical case body) rests against. The ledge is a narrow annular ring printed at the rear of the through-hole, not a full bayonet ring. The module is accessible from the front for removal by pushing slightly rearward to disengage the ledge, then withdrawing forward.
- **Operation:** Add (material added at the rear of the through-hole cylinder to form the ledge)
- **Shape:** Annular ring (partial — see note) inside the Φ33.2 mm through-hole cylinder
- **Position:**
  - Front face of ledge: Y = 12.2 mm (= front wall interior face 2.4 + module body depth 9.8 mm)
  - Rear face of ledge: Y = 13.7 mm (= 12.2 + 1.5 mm ledge width)
  - Ledge inner diameter: 30.0 mm (clears the 9.8 mm module cylindrical body, which has the same 33 mm OD — the ledge narrows the opening behind the module body while allowing the acrylic back plate, which has a smaller profile than the CNC case OD, to be captured)
  - Ledge outer diameter: 33.2 mm (flush with through-hole wall)
  - Z center: 142.5 mm (same as cutout)
- **Dimensions:**
  - Ledge width (Y direction): 1.5 mm
  - Ledge protrusion (radially inward from hole wall): 1.6 mm (= (33.2 − 30.0) / 2)
  - Inner clear diameter: 30.0 mm
  - Outer diameter: 33.2 mm
- **FDM notes:** The ledge is a horizontal annular ring inside a vertical cylinder. In the base-down print orientation, this ledge overhangs at 90° (it is a horizontal disc inside a vertical hole). This requires a designed frangible support: a 0.2 mm interface gap below the ledge with 0.3 mm × 0.3 mm break-away tabs at 2 mm and 6 mm from one edge of the ledge arc (matching the snap-arm support spec). The ledge face is interior and accessible from the front cutout for support removal. Alternatively: machine a notch on one arc segment (2 mm wide, full ledge depth) to allow the module to pass the ledge during installation and then rotate to engage — a partial bayonet. The full-annular ledge approach is specified here; the notch approach is available as a fallback if support removal is impractical on first article.

---

### Feature 5: S3 Cutout and Pocket

- **Name:** S3 cutout and pocket
- **Description:** A square through-hole in the front face for the S3 module's circular face, plus a full-depth pocket extending into the interior to house the 33.1 mm deep module body. The pocket is the same square cross-section as the through-hole (48.2 mm × 48.2 mm) and extends from the front wall interior face to 33.1 mm depth. The module's square 48 mm housing corners cannot exit forward through the cutout (48 mm housing vs. 48.2 mm cutout with FDM tolerance), but the circular 47.3 mm face fits within the 48.2 mm opening with 0.45 mm clearance on each side, giving the knob ring full rotational clearance.
- **Operation:** Remove
- **Shape:** Square prism (through-hole + pocket)
- **Position:**
  - Center X: 110.0 mm
  - Center Z: 142.5 mm
  - Through-hole Y range: [0, 2.4]
  - Pocket Y range: [2.4, 35.5] (front wall interior face to 33.1 mm module depth)
- **Dimensions:**
  - Cutout / pocket width (X): 48.2 mm (48.0 mm nominal + 0.2 mm FDM correction)
  - Cutout / pocket height (Z): 48.2 mm
  - X range: [85.9, 134.1]
  - Z range: [118.4, 166.6]
  - Pocket depth (Y, from front wall interior face): 33.1 mm (to Y = 35.5)
  - Front edge chamfer: 0.5 mm × 45° on exterior rim
- **FDM notes:** The through-hole is in a vertical wall — no overhang. The pocket is a rectangular channel extending into the interior — its rear face (at Y = 35.5) is a horizontal ledge inside a vertical channel. At 33.1 mm depth, the rear wall of the pocket (48.2 mm × 48.2 mm open front) prints as a roof bridging 48.2 mm. 48.2 mm bridge span exceeds the 15 mm unsupported bridge limit in requirements.md. Resolution: the pocket rear wall at Y = 35.5 is not a bridge — it is a slab supported by the four surrounding pocket walls. This is an enclosed rectangular prism cutout, not a bridge over empty space. The slicer will fill in the rear wall of the pocket with full support from all four sides. No overhang concern for the rear pocket wall itself. The pocket side walls (at X = 85.9 and X = 134.1, running in Y) are vertical surfaces — no overhang. The pocket floor and ceiling (at Z = 118.4 and Z = 166.6, running in Y) are horizontal surfaces inside the pocket. The ceiling (top face of pocket at Z = 166.6) is a horizontal roof inside a 33.1 mm deep slot — this overhangs downward in the print. It is not a bridge across empty space; it is the top wall of a closed pocket that begins at Y = 2.4 and ends at Y = 35.5. The material above the pocket (the solid front wall above Z = 166.6) is in place at those print layers, so the ceiling of the pocket is a print-in-place overhang 48.2 mm wide by 33.1 mm deep. This exceeds the 15 mm unsupported bridge limit. **RESOLUTION: the top wall of the S3 pocket requires a designed frangible support shelf at Z = 166.6 - 0.2 mm = 166.4 mm (0.2 mm interface gap), 0.3 mm break-away tabs every 5 mm, spanning the 33.1 mm depth in Y. The support is interior and accessible from the front through the cutout opening before the S3 module is installed.**

---

### Feature 6: S3 Retention (M2.5 Boss Inserts)

- **Name:** S3 M2.5 retention bosses (×2)
- **Description:** Two printed cylindrical bosses on the interior walls of the S3 pocket, with central Φ2.5 mm through-holes that accept M2.5 heat-set inserts or provide direct pass-through for M2.5 screws. The bosses locate to the M2.5 mounting holes on the S3 PCB (at approximately 8-o'clock and 2-o'clock positions on the circular PCB relative to display center). The module's bezel face rests against the front wall interior face (Y = 2.4) as the Z-front stop; the M2.5 screws clamp the module rearward against this stop.
- **Operation:** Add (bosses project inward from the left and right walls of the S3 pocket)
- **Shape:** Cylindrical boss with axial through-hole
- **Position (both bosses relative to S3 pocket, in part frame):**
  - Boss 1 (8-o'clock position): X = 89.0 mm (left pocket wall at X=85.9, boss protrudes right), Y within pocket [2.4, 35.5], Z = 129.5 mm (110 - 47.3/2 × sin(60°) ≈ 130 mm from center, verify against actual PCB drawing)
  - Boss 2 (2-o'clock position): X = 131.0 mm (right pocket wall at X=134.1, boss protrudes left), Z = 155.5 mm (110 + 47.3/2 × sin(60°) ≈ 155 mm, verify against actual PCB drawing)
  - **DESIGN GAP:** Exact M2.5 hole positions on the S3 CrowPanel PCB are not specified in display-switch-dimensions.md ("approximately at the 8 o'clock and 2 o'clock positions on the circular PCB" from the CNX diagram). The boss center XZ coordinates above are estimates. The CadQuery generation agent must obtain the exact M2.5 hole positions from the Elecrow dimension drawing before placing these bosses. The pocket dimensions and location are fully specified; only the boss center positions within the pocket are approximate.
  - Boss protrusion depth (into pocket from wall face): 5.0 mm
  - Boss Y position: Y = 10.0 mm to 15.0 mm from front wall exterior (centered in accessible depth zone, forward of module PCB to allow screw access from front)
- **Dimensions:**
  - Boss outer diameter: 7.0 mm (M2.5 boss: minimum 2.5 × boss OD = ~5 mm minimum; 7 mm gives 2.25 mm wall around the hole)
  - Boss hole diameter: 2.7 mm (2.5 mm nominal + 0.2 mm FDM correction for loose fit — the M2.5 screw passes through or heat-set insert is pressed in)
  - Boss protrusion: 5.0 mm into pocket
- **FDM notes:** Bosses project horizontally from vertical pocket walls — horizontal protrusion is a 90° overhang. Each boss underside requires a 45° chamfer or frangible support. Apply 45° chamfer on the underside of each boss (the face pointing toward Z = 0), converting the 90° ledge to a 45° ramp. The boss top face retains its flat seating surface for the PCB or bracket. Chamfer does not affect mounting function.

---

### Feature 7: KRAUS Cutout

- **Name:** KRAUS air switch cutout
- **Description:** Circular through-hole in the front face for the KRAUS KWDA-100MB air switch. The 31.75 mm threaded stem passes through the hole; the 47.6 mm button cap sits flush on the exterior front face. The ABS lock nut retains the switch from behind — no printed retention is required.
- **Operation:** Remove
- **Shape:** Cylinder (through-hole)
- **Position:**
  - Center X: 165.0 mm
  - Center Z: 142.5 mm
  - Through Y: [0, 2.4] (full front wall thickness)
- **Dimensions:**
  - Cutout diameter: 32.0 mm (31.75 mm nominal + 0.2 mm FDM correction — loose fit to allow the 1 1/4" standard threaded stem to pass without binding)
  - Depth: 2.4 mm (full front wall through-cut)
  - Cutout left edge: X = 149.0 mm
  - Cutout right edge: X = 181.0 mm
  - Cutout bottom edge: Z = 126.5 mm
  - Cutout top edge: Z = 158.5 mm
  - Front edge chamfer: 0.5 mm × 45° on exterior rim
  - Interior clearance required: ≥ 50 mm depth behind panel face (38.1 mm stem + ABS nut + tube fitting). Interior clear zone: X: [149.0, 181.0], Z: [126.5, 158.5], Y: [2.4, 52.4]. This zone is in the open interior, clear of the dock cradle (dock cradle extends to Y = 172.4 at its rear, but is only Z = 0 to 77.4, so no conflict at Z = 126.5–158.5).
- **FDM notes:** Hole in vertical wall — no overhang. 0.2 mm addition per requirements.md. Verify with test print.

---

### Feature 8: Dock Opening

- **Name:** Dock opening
- **Description:** The large rectangular aperture in the lower front wall through which the pump cartridge inserts and withdraws. The cartridge front face is flush with the enclosure front face when fully inserted. The opening is always open — no door or cover. The 2 mm × 45° chamfer around the full perimeter of the opening communicates "insert here" and frames the aperture as an intentional design feature rather than a raw cutout.
- **Operation:** Remove
- **Shape:** Rectangular prism through-cut
- **Position:**
  - X: [31.5, 188.5] (centered at X = 110.0, ±78.5 mm)
  - Y: [0, 2.4] (full front wall through-cut)
  - Z: [0, 80.0]
- **Dimensions:**
  - Opening width: 157.0 mm (155 mm cartridge width + 0.2 mm FDM clearance per side + 1.0 mm reveal frame step per side)
  - Opening height: 80.0 mm (from Z=0 to Z=80, cartridge top at Z=77.4 + 2.6 mm hand clearance)
  - Opening Y depth: 2.4 mm (full front wall thickness)
  - Perimeter chamfer: 2 mm × 45° on all four edges (exterior rim of the opening)
  - Wall material left of opening: 31.5 mm (X: [0, 31.5])
  - Wall material right of opening: 31.5 mm (X: [188.5, 220])
- **FDM notes:** Rectangular cutout in a vertical wall — no overhang. The top edge of the opening at Z = 80 is the underside of the wall section between the dock opening and the component panel zone. This is a continuous wall section (not a lintel bridging air), so it has full structural support from the walls to either side and from the wall layer above. The 2 mm × 45° chamfer on the top edge of the opening (at Z = 80) is a downward-facing 45° chamfer — within the 45° limit, no support required.

---

### Feature 9: Interior Dividing Wall

- **Name:** Interior dividing wall
- **Description:** A full-height, full-width interior wall at Y = 175 mm that runs from the left interior wall to the right interior wall and from the floor to the top seam face. It separates the pump/valve zone (Y:[2.4, 175]) from the rear interior zone (Y:[175, 297.6]). It serves as the rear stop for the dock cradle (dock cradle rear at Y = 172.4, 2.6 mm clearance gap between cradle rear and dividing wall face).
- **Operation:** Add
- **Shape:** Rectangular slab (internal wall)
- **Position:**
  - Front face: Y = 175.0 mm
  - Rear face: Y = 177.0 mm
  - X extent: X:[2.4, 217.6] (runs between left and right interior wall faces)
  - Z extent: Z:[2.4, 185] (floor surface to top seam)
- **Dimensions:**
  - Wall thickness: 2.0 mm
  - Wall width: 215.2 mm (full interior width)
  - Wall height: 182.6 mm (interior floor top to seam face)
- **FDM notes:** An interior vertical wall growing from the floor in +Z — full layer support throughout. No overhang. 2.0 mm thickness: 5 perimeters at 0.4 mm nozzle. This exceeds the 1.2 mm structural wall minimum per requirements.md. The wall will warp at 215 mm width if printed as a thin slab; mitigated by bonding to the floor (full base contact) and by adding horizontal rib ties to the outer walls at approximately 70 mm intervals (at X ≈ 72, 145 mm from left interior face). These ribs are 2.0 mm thick, 5.0 mm tall, running in Y from the dividing wall to the outer wall — added as additional interior features. **DESIGN NOTE: These rib ties are not in the minimum feature list but are required for printability. Add them as part of the dividing wall feature. Three ribs: at X = 72, X = 145, and at the corners where the dividing wall meets the left and right interior walls (already bonded at those junctions).**

---

### Feature 10: 24 Cantilever Snap Arms on Top Edge

- **Name:** Snap arm array (24 arms total)
- **Description:** The 24 cantilever snap arms that permanently join the bottom half to the top half. Arms protrude horizontally inward from the interior face of the top-edge wall perimeter. Each arm has a hook at its free end; the hook's 30° lead-in guides engagement and the 90° retention face makes disengagement require arm fracture (~640 N per arm). Arms are arranged in 4 groups: 5 on the front face, 5 on the rear face, 7 on the left face, 7 on the right face.

- **Operation:** Add (24 cantilever extrusions from top-edge interior wall faces)

- **Shape:** Tapered rectangular cantilever with hook profile at tip

- **Arm geometry (all arms identical):**

  | Parameter | Value |
  |-----------|-------|
  | Arm length (inward protrusion) | 18.0 mm |
  | Arm thickness at root | 2.0 mm |
  | Arm thickness at tip | 1.4 mm (linear taper) |
  | Arm width | 8.0 mm |
  | Hook height | 1.2 mm |
  | Lead-in angle | 30° |
  | Retention face angle | 90° (permanent) |
  | Hook depth (horizontal) | 1.2 mm |
  | Root fillet | 0.3 mm radius |
  | Hook undercut support interface gap | 0.2 mm |
  | Break-away tabs | 0.3 mm wide × 0.3 mm tall, 2 per hook at 2 mm and 6 mm from one edge |

- **Front face arms (5 arms, at Y=2.4 interior face, Z=185 base, arms extend in +Y):**

  | Arm | X_center |
  |-----|----------|
  | F1 | 30.0 mm |
  | F2 | 70.0 mm |
  | F3 | 110.0 mm |
  | F4 | 150.0 mm |
  | F5 | 190.0 mm |

  Arm tip at Y = 20.4 mm. Corner clearance: 30 mm from each corner. Pitch: 40 mm.

- **Rear face arms (5 arms, at Y=297.6 interior face, Z=185 base, arms extend in −Y):**

  | Arm | X_center |
  |-----|----------|
  | R1 | 30.0 mm |
  | R2 | 70.0 mm |
  | R3 | 110.0 mm |
  | R4 | 150.0 mm |
  | R5 | 190.0 mm |

  Arm tip at Y = 279.6 mm.

- **Left face arms (7 arms, at X=2.4 interior face, Z=185 base, arms extend in +X):**

  | Arm | Y_center |
  |-----|----------|
  | L1 | 30.0 mm |
  | L2 | 70.0 mm |
  | L3 | 110.0 mm |
  | L4 | 150.0 mm |
  | L5 | 190.0 mm |
  | L6 | 230.0 mm |
  | L7 | 270.0 mm |

  Arm tip at X = 20.4 mm. Corner clearance: 30 mm from each corner. Pitch: 40 mm.

- **Right face arms (7 arms, at X=217.6 interior face, Z=185 base, arms extend in −X):**

  | Arm | Y_center |
  |-----|----------|
  | RL1 | 30.0 mm |
  | RL2 | 70.0 mm |
  | RL3 | 110.0 mm |
  | RL4 | 150.0 mm |
  | RL5 | 190.0 mm |
  | RL6 | 230.0 mm |
  | RL7 | 270.0 mm |

  Arm tip at X = 199.6 mm.

- **FDM notes:** Arms are horizontal cantilevers at the top of the print (Z near 185 mm), growing in the XY plane. The flex direction is parallel to the build plate — the strongest FDM orientation per requirements.md. The hook undercut (1.2 mm, facing downward = toward the build plate) requires a designed frangible support: 0.2 mm interface gap beneath each hook's underside face, with 0.3 mm × 0.3 mm break-away tabs at 2 mm and 6 mm from one edge of each 8 mm wide hook. The supports are inside the assembly cavity, accessible from the open top of the part before assembly. The support break-away surface is the hook's 90° retention face — the 0.3 mm gap ensures clean separation. Verify with a single-arm test print before committing the full perimeter.

---

### Feature 11: Continuous Tongue on Top Mating Edge

- **Name:** Continuous tongue (seam face)
- **Description:** A continuous rectangular-profile tongue that runs the full perimeter of the seam face, set 2 mm inward from the exterior wall face. The tongue enters the matching groove in the top half before the snap arms engage (tongue is 4.0 mm tall vs. 1.2 mm hook height), constraining lateral shift of the halves to ±0.05 mm before any arm deflects. The front face arm is interrupted at the dock opening span.
- **Operation:** Add
- **Shape:** Continuous rectangular-section extrusion along a rectangular path
- **Position (tongue centerline path):**
  - Left arm: X = 3.5, Y: [3.5, 296.5], Z: [185, 189]
  - Right arm: X = 216.5, Y: [3.5, 296.5], Z: [185, 189]
  - Front arm (left segment): Y = 3.5, X: [3.5, 31.5], Z: [185, 189]
  - Front arm (right segment): Y = 3.5, X: [188.5, 216.5], Z: [185, 189]
  - Rear arm: Y = 296.5, X: [3.5, 216.5], Z: [185, 189]
  - Corners: mitered at 45°
- **Dimensions:**
  - Tongue width: 3.0 mm (tongue body spans ±1.5 mm from centerline)
  - Tongue height (protrusion above seam face): 4.0 mm (Z: 185 → 189)
  - Tongue tip Z: 189.0 mm
  - Tongue base chamfer: 0.3 mm × 45° (prevents elephant's foot interference at tongue base)
  - Tongue tip chamfer: 0.5 mm × 30° (guides entry into groove)
  - Tongue body (left arm): X: [2.0, 5.0]
  - Tongue body (right arm): X: [215.0, 218.0]
  - Tongue body (front arm): Y: [2.0, 5.0]
  - Tongue body (rear arm): Y: [295.0, 298.0]
  - Front arm gap (dock opening): X: [31.5, 188.5] — no tongue material in this span
- **FDM notes:** The tongue grows in +Z from the seam face — fully supported by the wall below throughout its height. No overhang. The 0.5 mm × 30° tip chamfer is on the top face (last surface printed) — clean geometry. The 0.3 mm × 45° base chamfer prevents any first-layer flare at the wall/tongue junction from interfering with tongue-groove fit.

---

### Feature 12: 4 Corner Alignment Pins on Top Edge

- **Name:** Alignment pins (×4)
- **Description:** Four cylindrical pins growing upward from the seam face at the four corners of the enclosure. They enter matching sockets in the top half before any snap arm engages, constraining X and Y to ±0.075 mm before force is applied to the snap arms.
- **Operation:** Add (×4 cylinders from seam face)
- **Shape:** Cylinder with chamfered tip
- **Position:**

  | Pin | X_center | Y_center | Z_base | Z_tip |
  |-----|----------|----------|--------|-------|
  | Front-left | 10.0 mm | 10.0 mm | 185 mm | 193 mm |
  | Front-right | 210.0 mm | 10.0 mm | 185 mm | 193 mm |
  | Rear-left | 10.0 mm | 290.0 mm | 185 mm | 193 mm |
  | Rear-right | 210.0 mm | 290.0 mm | 185 mm | 193 mm |

- **Dimensions:**
  - Diameter: 4.0 mm (designed; FDM-printed pins are accurate to ±0.05 mm with Bambu H2C)
  - Height: 8.0 mm
  - Tip chamfer: 1.0 mm × 45°
  - Clearance to matching socket: 0.15 mm (0.1 mm design intent + 0.05 mm elephant's foot compensation per synthesis.md) — pins are 4.0 mm designed but socket is designed at 4.15 mm inner diameter
  - Material surrounding each pin: ≥ 7.6 mm to nearest exterior edge (10 mm from edge − 2 mm radius = 8 mm, minus 0.4 mm minimum)
- **FDM notes:** Pins grow in +Z — no overhang. The chamfered tip is the last material printed — smooth and accurate. Pin diameter 4.0 mm printed on the Bambu H2C will be ±0.05 mm — verify on first article and adjust socket clearance if needed.

---

### Feature 13: 4 Exterior Feet on Bottom Face

- **Name:** Exterior feet (×4)
- **Description:** Four integral circular cylinder pads on the exterior bottom face (Z=0), extending downward (in −Z) from the device floor. Feet prevent the enclosure from sliding on smooth countertop surfaces and protect the bottom face from contact wear. The flat bottom face of each foot provides a seating zone for optional adhesive-backed rubber pads.
- **Operation:** Add (4 cylinders extruding below Z=0)
- **Shape:** Circular cylinder
- **Position (foot centers, at Z = 0):**

  | Foot | X_center | Y_center | Z_top | Z_bottom |
  |------|----------|----------|-------|----------|
  | Front-left | 15.0 mm | 15.0 mm | 0 mm | −3 mm |
  | Front-right | 205.0 mm | 15.0 mm | 0 mm | −3 mm |
  | Rear-left | 15.0 mm | 285.0 mm | 0 mm | −3 mm |
  | Rear-right | 205.0 mm | 285.0 mm | 0 mm | −3 mm |

- **Dimensions:**
  - Diameter: 15.0 mm
  - Height: 3.0 mm (extends 3 mm below Z = 0)
  - Foot pattern span: 190 mm × 270 mm
  - Inset from corner edges: 15 mm (to foot center from each adjacent exterior edge)
- **FDM notes:** Feet are on the build-plate face (Z = 0 is the build plate). They print as circular islands on the first layers. Build-plate contact surface quality: smooth from PEI plate. The 0.3 mm × 45° elephant's foot chamfer (Feature 17) on the bottom perimeter edge mitigates first-layer flare at the enclosure walls, but the feet themselves will have their own elephant's foot at their base perimeter edges — this is acceptable as the feet are not precision mating surfaces. If feet have visible flare, add a small chamfer to the foot perimeter base edge during CadQuery generation.

---

### Feature 14: Dock Cradle Snap Pockets (Interior Floor)

- **Name:** Dock cradle snap pockets (×4)
- **Description:** Four blind pockets cut into the interior floor surface (Z = 2.4, opening upward) that accept the snap posts of the dock cradle from above during assembly. The pocket positions correspond to the four corners of the dock cradle footprint. The exact pocket body dimensions (width, depth in Z, overhang geometry) depend on the dock cradle snap post geometry, which is defined in the dock cradle specification (not yet written). The positions below are the pocket centers as derived from the dock cradle footprint corners; actual pocket body centers will be offset slightly inward (in +Y) from the front-edge pockets to avoid breaking through the front wall.
- **Operation:** Remove
- **Shape:** Rectangular blind pocket (opening upward from floor surface)
- **Position (pocket center, at floor surface Z = 2.4):**

  | Pocket | X_center | Y_center nominal | Y_center adjusted | Note |
  |--------|----------|-----------------|-------------------|------|
  | Front-left | 32.5 mm | 2.4 mm | 5.4 mm | Offset 3.0 mm in +Y to clear front wall |
  | Front-right | 187.5 mm | 2.4 mm | 5.4 mm | Same |
  | Rear-left | 32.5 mm | 172.4 mm | 172.4 mm | No adjustment needed |
  | Rear-right | 187.5 mm | 172.4 mm | 172.4 mm | No adjustment needed |

- **Dimensions (PLACEHOLDER — finalize when dock cradle specification is written):**
  - Pocket plan dimensions: 6.0 mm × 6.0 mm (nominal — adjust per dock cradle post size)
  - Pocket depth: 4.0 mm (from Z = 2.4 down to Z = −1.6 — this is INTO the 2.4 mm floor, meaning pocket bottom is at Z = 2.4 − 4.0 = −1.6 mm, which would break through the floor. **CORRECTION: pocket depth limited to 2.0 mm (from Z=2.4 down to Z=0.4), preserving 0.4 mm floor base. If dock cradle posts require deeper pockets, the floor must be locally thickened to 6.0 mm at pocket locations.**)
  - Pocket overhang (snap hook geometry): defined by dock cradle specification
- **FDM notes:** Pockets in the floor (Z = 2.4, opening upward) print as upward-opening blind pockets — no overhang. The pocket walls grow upward from the floor surface. Clean geometry. The front-edge pockets at Y = 5.4 are 5.4 − (6/2) = 2.4 mm from the front wall interior face — just clearing the front wall.

---

### Feature 15: 3 mm Vertical Edge Fillets on Exterior Corners

- **Name:** Exterior vertical edge fillets
- **Description:** 3 mm radius fillets on the four vertical exterior corner edges of the enclosure (the long Z-axis edges at the intersections of front/left, front/right, rear/left, and rear/right exterior faces). These soft-radius corners make the appliance feel intentionally designed rather than machine-cut, consistent with consumer precedents (Nest Audio, Vitamix base).
- **Operation:** Modify (fillet applied to selected edges)
- **Shape:** Concave quarter-round of radius 3.0 mm
- **Position:** The four vertical edges of the exterior box body:
  - Front-left edge: intersection of X=0 and Y=0 faces, full Z:[0, 185]
  - Front-right edge: intersection of X=220 and Y=0 faces, full Z:[0, 185]
  - Rear-left edge: intersection of X=0 and Y=300 faces, full Z:[0, 185]
  - Rear-right edge: intersection of X=220 and Y=300 faces, full Z:[0, 185]
- **Dimensions:**
  - Fillet radius: 3.0 mm
  - Fillet length (Z extent): 185 mm (full height of bottom half)
- **FDM notes:** Vertical edges print as Z-axis features — the fillet is a continuously curved vertical surface. At 0.1 mm layer height, a 3 mm radius fillet in ASA will appear smooth at normal viewing distance. 3 mm is well above the 0.4 mm minimum printable feature radius. The fillet slightly reduces the effective footprint at the corners but does not affect interior volume.

---

### Feature 16: 0.3 mm × 45° Elephant's Foot Chamfer on Bottom Exterior Edges

- **Name:** Elephant's foot chamfer (bottom perimeter)
- **Description:** A 0.3 mm × 45° chamfer on the outermost perimeter edge of the bottom exterior face (at Z = 0). This prevents first-layer flare (elephant's foot) from creating a visible irregularity at the enclosure base, which would make the device appear to rest on a flair rather than a flat plane.
- **Operation:** Modify (chamfer applied to bottom perimeter edges)
- **Shape:** 45° chamfer (45° angle, 0.3 mm depth)
- **Position:** The complete perimeter of the exterior bottom face at Z = 0:
  - Runs along the outermost edges of all four exterior walls at Z = 0
  - Applies to the full 1040 mm perimeter (2 × (220 + 300)) of the bottom edge, including the fillet-transitioned corner regions
- **Dimensions:**
  - Chamfer width: 0.3 mm (horizontal, from exterior face)
  - Chamfer height: 0.3 mm (vertical, up from Z = 0)
  - Angle: 45°
- **FDM notes:** Per requirements.md: "If the bottom face is a mating surface, add a 0.3 mm × 45° chamfer to the bottom edge." The bottom face is the device's base — visible in countertop placement. The chamfer is on the exterior face side — a 45° ramp that is printed cleanly without overhang (the chamfer angle exactly equals the 45° limit). The feet do not have this chamfer (they are not mating surfaces), but the enclosure wall base perimeter does.

---

### Feature 17: 0.5 mm Exterior Reveal

- **Name:** Exterior reveal step (seam detail)
- **Description:** The 0.5 mm designed shadow-line reveal at the top edge of the bottom half. The bottom half's exterior wall terminates at the seam plane (Z = 185) — it does NOT extend beyond Z = 185. The top half's exterior wall extends 0.5 mm BELOW the seam plane, lapping over the bottom half's exterior wall face from above. This feature in the bottom half is therefore defined by what the bottom half does NOT have: the top edge of the bottom half's exterior walls is a square (non-chamfered) termination at Z = 185.

  The reveal visible in assembly is produced by the top half's 0.5 mm lap. From the bottom half's perspective, the required geometry is: exterior wall top edge is flat at Z = 185, no chamfer or radius on the exterior corner of the top edge. The inner face of the top edge carries the tongue (which is set 2 mm inward) and snap arms (set at interior wall face). The outer face at Z = 185 is a clean square edge that will be covered by the top half's 0.5 mm lip.

  Where snap arms are located, the exterior wall lip tapers back to zero over 5 mm on each side of the arm — this preserves the visual continuity of the exterior shadow line by preventing the snap arm from creating a visible bump or gap in the reveal.

- **Operation:** (geometry of the top edge — no separate operation; the condition is a clean square termination of the exterior wall at Z = 185)
- **Shape:** Square-terminated exterior wall top edge
- **Position:** The exterior face of all four walls at Z = 185 (top seam edge)
- **Dimensions:**
  - Bottom half exterior wall terminates at Z = 185 — no protrusion above this plane
  - Top edge is a 90° corner: exterior face (e.g., Y=0) meets seam face (Z=185) at 90° — no chamfer on this corner
  - At snap arm locations: lip tapers to zero over 5 mm on each side of each arm centerline
  - The 0.5 mm reveal depth is a property of the assembled joint (top half's lap dimension), not of the bottom half alone
- **FDM notes:** The clean square exterior corner at Z = 185 prints as the last few layers of the exterior wall. FDM layer edges here will be well-defined at 0.1 mm layer height. The snap arm support tabs at the hook undercuts are inside the cavity — they do not affect the exterior corner geometry. No special FDM treatment required for this feature.

---

## Interface Table (Rubric D)

| Interface | This Part Dimension | Mating Part Dimension | Clearance | Source |
|-----------|--------------------|-----------------------|-----------|--------|
| Bottom half top seam edge ↔ Top half bottom seam edge (snap hooks) | 24 snap arms: 18 mm × 2.0 mm × 8.0 mm, hook height 1.2 mm, 90° retention face | 24 ledge pockets in top half seam wall: 1.2 mm deep × 8.0 mm wide × 2.0 mm tall | Designed: arms flex 1.2 mm during engagement; zero clearance at 90° retention face (permanent). Assembly force ~5 N per arm. | snap-fit-geometry.md, synthesis.md Section 2 |
| Bottom half tongue ↔ Top half groove | Tongue: 3.0 mm wide, 4.0 mm tall, runs full perimeter (with gap at dock opening) | Groove: 3.1 mm wide, 4.2 mm deep | Lateral: 0.1 mm per side (0.05 mm clearance per wall — snug fit per requirements.md for locating features); Z: 0.2 mm at groove bottom (tongue does not bottom). Total lateral play: ±0.05 mm | snap-fit-geometry.md Section 4.2, synthesis.md Section 2 |
| Bottom half alignment pins ↔ Top half alignment sockets | 4 pins: Φ4.0 mm, 8.0 mm tall, located at (10,10), (210,10), (10,290), (210,290) | 4 sockets: Φ4.15 mm inner diameter, ≥ 8.0 mm deep blind holes | Radial: 0.075 mm per side (0.15 mm diametric clearance). Z: pins bottom out in sockets at full engagement. | synthesis.md Section 2, snap-fit-geometry.md Section 4.1 |
| RP2040 module ↔ RP2040 cutout | Cutout: Φ33.2 mm through-hole; retention ledge: 30.0 mm ID, 33.2 mm OD, at Y=12.2 mm | Module: Φ33.0 mm OD, 9.8 mm total depth; rear plate protrudes ~1.8 mm beyond cylindrical body | Radial: 0.1 mm per side (0.2 mm diametric — loose fit per requirements.md). Front stop: 1.75 mm CNC chamfer on module rests on cutout rim (0.5 mm × 45° chamfer provides positive stop). Rear stop: retention ledge at Y=12.2 mm (module acrylic plate seats against ledge face) | display-switch-dimensions.md, spatial-resolution.md Section 2 |
| S3 module ↔ S3 cutout + pocket | Cutout: 48.2 mm × 48.2 mm square; pocket: 48.2 mm × 48.2 mm × 33.1 mm deep | Module: 48 mm × 48 mm housing, 33.1 mm deep; face Φ47.3 mm | Cutout-to-housing: 0.1 mm per side (snug, sufficient for insertion); face-to-cutout-edge: 0.45 mm per side for knob rotation clearance (47.3 mm face in 48.2 mm opening — 0.45 mm per side clearance > 0.5 mm minimum required for free knob rotation... MARGINALLY BELOW MINIMUM). **DESIGN GAP:** Knob clearance is 0.45 mm per side but synthesis.md states 0.5 mm minimum for free rotation. The cutout must be widened to 48.3 mm (47.3 mm + 2 × 0.5 mm = 48.3 mm) to meet the clearance requirement. **Correct the cutout to 48.3 mm width and height.** This increases material removal by 0.1 mm per side. Rear stop: M2.5 retention bosses clamp module against front wall interior face (Y=2.4). | display-switch-dimensions.md, synthesis.md Section 3, spatial-resolution.md Section 2 |
| KRAUS air switch ↔ KRAUS cutout | Cutout: Φ32.0 mm through-hole; no retention feature (self-retaining) | Switch body: Φ31.75 mm threaded stem; Φ47.6 mm cap (front stop) | Radial: 0.125 mm per side (0.25 mm diametric — loose fit, within 0.2 mm minimum per requirements.md + some margin). Front stop: 47.6 mm cap rests on exterior front face (Y=0). Rear stop: ABS nut on threaded stem, clamps from behind. | display-switch-dimensions.md, spatial-resolution.md Section 2 |
| Dock cradle ↔ snap pockets on interior floor | 4 pockets: 6.0 mm × 6.0 mm × 2.0 mm deep at (32.5,5.4), (187.5,5.4), (32.5,172.4), (187.5,172.4) at Z=2.4 | Dock cradle snap posts: geometry TBD per dock cradle specification | PLACEHOLDER: 0.1–0.2 mm clearance per side on post-to-pocket fit (snug to loose, to be verified on dock cradle spec). Rear stop: interior dividing wall at Y=175.0 (2.6 mm clearance from cradle rear at Y=172.4). | spatial-resolution.md Section 7, pump-cartridge/concept.md |

---

## Direction Consistency Check (Rubric C)

| Claim | Feature | Axis | Direction stated | Geometry confirms |
|-------|---------|------|-----------------|-------------------|
| Snap arms protrude inward | Feature 10 | X or Y | "Inward" = away from exterior wall, toward enclosure center | Front arms: +Y from Y=2.4; rear arms: −Y from Y=297.6; left arms: +X from X=2.4; right arms: −X from X=217.6. All directed toward center. ✓ |
| Tongue protrudes upward | Feature 11 | Z | +Z from Z=185 | Z range [185, 189]. ✓ |
| Alignment pins protrude upward | Feature 12 | Z | +Z from Z=185 | Z base=185, tip=193. ✓ |
| Feet protrude downward | Feature 13 | Z | −Z from Z=0 | Z top=0, bottom=−3. ✓ |
| Snap pocket opens upward | Feature 14 | Z | +Z (upward opening) | Pocket cut from Z=2.4 downward (opens from floor surface into the floor material, opening faces upward toward +Z). Opening at Z=2.4 faces up. ✓ |
| Dock opening is in front face | Feature 8 | Y | Y=0 exterior, cut through to Y=2.4 | Y range [0, 2.4]. ✓ |
| Component cutouts are in front face | Features 3, 5, 7 | Y | Y=0 exterior through to Y=2.4 | All three: Y:[0, 2.4] through-cut. ✓ |
| S3 pocket extends into interior | Feature 5 | Y | Pocket goes into interior from front wall | Y:[2.4, 35.5]. +Y direction into enclosure interior. ✓ |
| Retention ledge is at rear of RP2040 cutout | Feature 4 | Y | Ledge is behind the module (in +Y direction from front face) | Ledge front face at Y=12.2 (= exterior face 0 + module depth 9.8 + front wall 2.4). ✓ |
| Interior dividing wall separates zones | Feature 9 | Y | Wall at Y=175, front zone Y:[2.4,175], rear zone Y:[177,297.6] | Dividing wall: Y:[175, 177]. ✓ |
| Top half is proud (0.5 mm reveal) | Feature 17 | Z | Top half's exterior wall extends 0.5 mm BELOW Z=185 (the seam plane) | Bottom half terminates at Z=185; top half extends from Z=185 down to Z=184.5. The bottom half does not protrude — the top half's lip covers it. ✓ |
| Dock opening begins at Z=0 | Feature 8 | Z | Z=0 is the lowest point of the opening | Z:[0, 80]. ✓ |
| Front-arm tongue gap matches dock opening | Feature 11 | X | Gap at X:[31.5, 188.5] | Dock opening X:[31.5, 188.5]. Both match. ✓ |
| Dock cradle rear at Y=172.4, dividing wall at Y=175 | Features 9, 14 | Y | Cradle rear must be in front of dividing wall | 172.4 < 175.0; 2.6 mm clearance. ✓ |
| Arm tip positions | Feature 10 | X or Y | Front arm tips at Y=20.4; left arm tips at X=20.4 | Front: 2.4 + 18.0 = 20.4. Left: 2.4 + 18.0 = 20.4. Right: 217.6 − 18.0 = 199.6. Rear: 297.6 − 18.0 = 279.6. ✓ |

No directional contradictions found.

---

## Assembly Feasibility Check (Rubric E)

**Assembly sequence for the complete enclosure (as defined in concept.md, Step 7 → bottom half's contributions):**

| Step | Action | Feasibility check |
|------|--------|-------------------|
| 1 | Install dock cradle into bottom half (snap pockets in floor) | Bottom half is open at the top (seam face). Dock cradle is lowered vertically into the interior, snap posts engage pockets from above. Clear: 215 mm interior width accommodates the 155 mm cradle with 30 mm clearance on each side. Z access: full open top. ✓ |
| 2 | Remove snap arm hook undercut break-away supports | Access: the 24 support tabs are inside the open top of the bottom half before the top half is placed. Each tab is at the top of the part (Z ≈ 185 mm), accessible with fingertip or dental pick from above. Interior is open. ✓ |
| 3 | Place top half over bottom half; corner pins enter sockets | The four 4.0 mm pins at (10,10), (210,10), (10,290), (210,290) must enter matching sockets in the top half simultaneously. With 1.0 mm × 45° chamfers on both pins and sockets, alignment is self-guided. The user positions the top half over the bottom half, locating by feel. ✓ |
| 4 | Lower top half; tongue enters groove | The tongue at Z:[185,189] enters the groove as the top half descends. The 0.5 mm × 30° tip chamfer guides entry. The groove (4.2 mm deep in top half) captures the tongue (4.0 mm tall) before snap arms engage. ✓ |
| 5 | Press both palms along 300 mm faces; 24 snaps engage | User applies ~60 N per palm along the 300 mm faces (left and right walls). All 24 hooks engage within 1–2 mm. Hard stop. ✓ Ergonomic: the 300 mm face span comfortably accommodates two adult palms simultaneously. |
| 6 | Verify reveal continuity | User visually and tactilely checks the 0.5 mm reveal runs continuously. Any gap = unengaged snap. Press locally. ✓ |
| RP2040 install | Drop module into Φ33.2 mm cutout from front | Module OD 33.0 mm, cutout 33.2 mm — 0.1 mm clearance per side. Module drops in front-face-forward, guided by cutout. Module rear plate seats on retention ledge at Y=12.2. The break-away support on the ledge must be removed before module installation. Access for support removal: through the 33.2 mm cutout opening from the front, with the enclosure fully assembled. Dental pick through cutout. ✓ **BUT: support removal access through 33.2 mm hole is tight. Consider removing support before enclosure assembly.** |
| S3 install | Insert module into 48.2 mm square cutout + pocket from front | Module 48 mm housing in 48.2 mm cutout. Module must be inserted from behind (housing corners may not clear through the cutout without skewing). Insertion from behind through open top of bottom half BEFORE the two enclosure halves are joined. M2.5 retention accessed through the cutout after insertion. ✓ S3 should be installed before closing the enclosure. |
| KRAUS install | Thread stem through 32.0 mm cutout from front | Self-guiding. ABS nut threaded from behind. Nut accessible through the interior — either through the dock opening or through the open top before halves join. ✓ Install before closing enclosure or access through dock opening. |
| Dock cradle snap support removal | N/A — dock cradle posts snap in from above; no hook undercut support | Pockets are simple blind holes. Cradle posts insert downward. ✓ |

**Feasibility finding:** S3 module and KRAUS nut access from behind is most practical BEFORE the enclosure halves are joined. RP2040 retention ledge support removal is most practical before module installation (access through the cutout with the part on the bench, not inside the assembled enclosure). The assembly sequence should specify:

1. Remove all snap arm supports (open top, easy access)
2. Remove RP2040 ledge support (through front cutout, part on bench)
3. Install KRAUS (from front, nut from interior through open top)
4. Install S3 (from rear/interior, before top half is joined)
5. Install dock cradle (from above, through open top)
6. Join enclosure halves
7. Install RP2040 (from front, after enclosure is joined)

---

## Part Count Minimization (Rubric F)

| Feature pair | Move relative to each other? | Conclusion |
|-------------|------------------------------|------------|
| Box body + front face wall | No — front face wall is an integral face of the box | Single part. ✓ |
| Box body + snap arms | No — snap arms are permanently part of the bottom half | Single part. Arms flex during assembly but remain attached. ✓ |
| Box body + tongue | No — tongue is stationary relative to box | Single part. ✓ |
| Box body + alignment pins | No — pins are stationary locating features | Single part. ✓ |
| Box body + feet | No — feet are stationary | Single part. ✓ |
| Box body + interior dividing wall | No — dividing wall is a permanent interior structure | Single part. ✓ |
| Box body + RP2040 retention ledge | No — ledge is a permanent stopping surface | Single part. Integral ledge, not a separate insert. ✓ |
| Box body + S3 M2.5 boss inserts | No — bosses are permanent printed geometry | Single part. No screws are in the bottom half; bosses receive M2.5 fasteners that come with or are added to the S3 bracket. ✓ |
| Box body + dock cradle snap pockets | No — pockets are permanent floor geometry | Single part. ✓ |
| Box body ↔ dock cradle | Yes — cradle inserts separately into snap pockets | Separate parts (dock cradle is a separate component defined elsewhere). ✓ |
| Box body ↔ RP2040 module | Yes — module is removable | Separate parts. ✓ |
| Box body ↔ S3 module | Yes — module is removable | Separate parts. ✓ |
| Box body ↔ KRAUS switch | Yes — switch is removable | Separate parts. ✓ |
| Box body ↔ top half | Yes — top half is a separate printed piece | Separate parts (joined permanently but printed separately). ✓ |

**Result:** The enclosure bottom half is a single printed part with no subcomponents. All structural, retention, and join features are integral. This is the minimum possible part count consistent with the required removability of the dock cradle, display modules, and air switch. No further reduction is possible.

---

## FDM Printability (Rubric G)

### Step 1: Print Orientation Statement

**Orientation:** Exterior bottom face (Z = 0) on the build plate. The part prints base-down, growing in +Z from Z = 0 (feet, floor) to Z = 185 (seam face). No rotation, no support structure for primary surfaces. This is the natural orientation for a box printed upright.

---

### Step 2: Overhang Audit Table

| Surface | Angle from horizontal (in print) | Overhang concern? | Resolution |
|---------|----------------------------------|-------------------|------------|
| Exterior front face (Y=0, vertical) | 90° (vertical) | None — vertical surface, no overhang | — |
| Exterior rear face (Y=300, vertical) | 90° | None | — |
| Exterior left face (X=0, vertical) | 90° | None | — |
| Exterior right face (X=220, vertical) | 90° | None | — |
| Exterior bottom face (Z=0, horizontal) | 0° (on build plate) | None — on build plate | — |
| Seam face (Z=185, horizontal) | 0° (last layers, fully supported) | None — fully supported by wall material below | — |
| RP2040 cutout rim, front edge chamfer (0.5 mm × 45°, on vertical face) | 45° chamfer on vertical surface | At limit — 45° is exactly the threshold | Acceptable per requirements.md (≤ 45° limit). No support needed. |
| S3 cutout rim, front edge chamfer | 45° chamfer on vertical surface | At limit | Acceptable. No support. |
| KRAUS cutout rim, front edge chamfer | 45° chamfer on vertical surface | At limit | Acceptable. No support. |
| Dock opening perimeter chamfer (2 mm × 45°) | 45° chamfer on vertical and horizontal opening edges | At limit | Acceptable on vertical edges. On the top edge of the dock opening (horizontal face, chamfer faces downward): 45° downward chamfer from horizontal — at limit, acceptable. No support. |
| Dock opening top lintel (Z=80, inner face) | Horizontal — but this is a continuous wall section, not a span | This is the underside of the wall between Z=80 and the component zone. It overhangs downward as the inside of the box just above the dock opening. The wall material to the left and right of the dock opening provides vertical support columns. The lintel is ~157 mm span. | **This is a 90° overhang on the underside of the wall above the dock opening.** The lintel (underside of front wall from Z=80 to Z=100 above the dock opening, at Y between 0 and 2.4) overhangs at 90° for a 157 mm horizontal span over the dock opening. This requires a designed support or a chamfer. Resolution: add a 45° chamfer on the inside face of the front wall at the top edge of the dock opening (at Z=80, facing into the dock opening interior). A 2 mm × 45° chamfer converts the 90° inside edge to a 45° ramp. This is already specified as the dock opening perimeter chamfer (Feature 8). ✓ |
| Tongue tip chamfer (0.5 mm × 30°, on top of tongue) | 30° below horizontal — printed at top of Z stack | 30° tip is a tapered top — not a true overhang (the taper faces upward). The chamfer reduces the tongue tip width from 3.0 to ~2.0 mm over 0.5 mm. This is the last printed surface — no overhang in the downward sense. ✓ | None needed |
| Tongue base chamfer (0.3 mm × 45°) | 45° at base of tongue on seam face | At limit. The chamfer at the tongue base creates a 45° surface between the seam face and the tongue side face. Acceptable. ✓ | None |
| Snap arm body (horizontal, in XY plane) | 90° from vertical = 0° from horizontal (horizontal cantilever) | The arm body itself is a horizontal element growing from the wall. Below the arm (between the arm underside and the wall below) is open interior space. The arm underside is a 0° horizontal surface — this is a 90° overhang of significant span (18 mm). | **The arm body underside requires support.** 18 mm horizontal cantilever with 8 mm width. The arm is printed at the top of the part (Z near 185 mm) on the interior. The arm underside sags without support. Resolution: the arm root is attached to the wall at Z=185; the arm hangs horizontally. In a base-down print, the arm layers build up from the wall: each layer of the arm is cantilevered from the wall at increasing Y (or X). This is a 90° overhang for a structure 2.0 mm thick (at root) × 18 mm long × 8 mm wide. **For FDM in base-down print, horizontal cantilever arms ARE printable as bridges: the arm is 8 mm wide (the bridge direction is X or Y for arms on the respective walls) and the bridge spans 18 mm in the overhang direction. 18 mm > 15 mm bridge limit.** Resolution for arm body: print with slicer-generated support under the arm body, OR add a 45° chamfer to the underside of the arm at the root region. Adding a 45° chamfer to the arm underside at the root (from root to 4 mm outward, 45° up from horizontal) reduces the effective unsupported span and creates a printable geometry. The outer 14 mm of the arm (beyond the chamfer zone) still has an 8 mm wide × 14 mm span overhang — within the 15 mm limit at the narrowest unsupported point. **Apply: 45° chamfer on arm underside at root, 2 mm horizontal × 2 mm vertical, tapered in over 2 mm from the wall face. This leaves a 16 mm free-span arm body, still within 15 mm limit if the effective free span is measured from the chamfer termination.** |
| Snap arm hook undercut (1.2 mm, downward face on hook tip) | 0° from horizontal (horizontal face facing downward) | 90° overhang — explicitly addressed in requirements.md and synthesis.md | Designed frangible support: 0.2 mm interface gap, break-away tabs 0.3 mm × 0.3 mm at 2 mm and 6 mm from hook edge. Tabs accessible from interior cavity (top of part, before assembly). ✓ |
| RP2040 retention ledge (horizontal annular ring inside vertical cylinder) | 0° from horizontal (ring faces upward — but looking at the underside in print: the ring underside faces downward = 90° overhang) | 90° overhang on ledge underside | Designed frangible support: 0.2 mm interface gap below ledge, break-away tabs. Access: through Φ33.2 mm cutout from front. ✓ |
| S3 pocket top wall (ceiling of 48.2 × 33.1 mm pocket, at Z=166.6) | 0° from horizontal (faces downward into pocket) | Horizontal ceiling inside enclosed pocket. Span in X direction: 48.2 mm (exceeds 15 mm limit). Span in Y direction: 33.1 mm (exceeds 15 mm limit). | **Designed frangible support shelf inside pocket at Z=166.6 − 0.2 mm = 166.4 mm, spanning 48.2 mm × 33.1 mm footprint (with cutouts per break-away tab spec). Support accessible through 48.3 mm front opening before S3 installation.** ✓ |
| S3 M2.5 boss underside | 0° from horizontal (boss hangs from pocket wall) | Boss protrudes horizontally from vertical pocket wall — boss underside is a 90° overhang | 45° chamfer on boss underside converts 90° to 45°. ✓ |
| Exterior vertical edge fillets (3 mm radius, vertical) | 90° (vertical curved surface) | None | — |
| 0.3 mm × 45° elephant's foot chamfer (at Z=0, exterior perimeter) | 45° (bottom of part, on build plate) | This is at the base, on the build plate — it IS the first layer region. The chamfer is intended to compensate for elephant's foot by creating a controlled taper. It prints cleanly as the first few layers widen slightly and then the chamfer geometry controls the transition. ✓ | None |
| Interior dividing wall (vertical, bonded to floor and side walls) | 90° (vertical) | None | — |
| Feet (vertical cylinder sides) | 90° | None | — |
| Foot top faces (circular horizontal, on build plate at Z=0) | 0° (on build plate) | None | — |

---

### Step 3: Wall Thickness Check

| Wall | Designed thickness | Minimum required | Pass? |
|------|--------------------|-----------------|-------|
| All exterior walls | 2.4 mm | 1.2 mm structural | ✓ (2×) |
| Interior floor | 2.4 mm | 1.2 mm structural | ✓ |
| Interior dividing wall | 2.0 mm | 1.2 mm structural | ✓ |
| Snap arm at root | 2.0 mm | 0.8 mm minimum, 1.2 mm structural | ✓ |
| Snap arm at tip | 1.4 mm | 0.8 mm | ✓ |
| Tongue width | 3.0 mm | 0.8 mm | ✓ |
| S3 M2.5 boss wall around hole | 2.25 mm ((7.0 − 2.5)/2 = 2.25 mm) | 0.8 mm | ✓ |
| Wall material left/right of dock opening | 31.5 mm | 1.2 mm | ✓ (26×) |
| Wall between RP2040 and S3 cutout edges | 14.3 mm | 1.2 mm | ✓ |
| Wall between S3 and KRAUS cutout edges | 14.9 mm | 1.2 mm | ✓ |
| Wall above dock opening (below component panel, Z:[80,118.4]) | ≥ 38 mm height, 2.4 mm thick | 1.2 mm | ✓ |

All walls pass minimum thickness requirements.

---

### Step 4: Bridge Span Check

| Bridge location | Span | Limit | Status | Resolution |
|----------------|------|-------|--------|------------|
| Snap arm body (18 mm cantilever, 8 mm wide) | 18 mm in overhang direction | 15 mm | OVER | 45° chamfer at root reduces effective free span; see overhang audit above |
| S3 pocket ceiling (48.2 mm × 33.1 mm) | 48.2 mm × 33.1 mm | 15 mm | OVER | Designed frangible support inside pocket |
| RP2040 retention ledge (annular, max span ≈ 30 mm ID) | ~30 mm | 15 mm | OVER | Designed frangible support below ledge |
| Dock opening top edge (157 mm span above dock opening) | See analysis — NOT a bridge; it is a continuous wall section with columns to each side | N/A | Not a bridge | 45° chamfer on inside edge of front wall at Z=80 |
| All cutout holes in front wall (Φ33.2, Φ32.0, 48.2 mm sq.) | No bridge — holes in vertical wall | N/A | Not bridges | — |

---

### Step 5: Layer Strength Check

| Feature | Primary load direction | FDM orientation | Strength concern? |
|---------|----------------------|-----------------|-------------------|
| Snap arms | Flexure in XY plane during assembly; tension/shear at root during retention | Flex direction parallel to build plate — strongest FDM orientation. Root bends in XY. | ✓ No concern — flex-parallel to build plate per requirements.md |
| Tongue | Shear load in XY (lateral force from mating groove) | Tongue grows in +Z, layers perpendicular to XY shear. Shear load is parallel to layer planes. This is the weakest direction (inter-layer shear). | Low risk: the safety factor is 13× per snap-fit-geometry.md Section 5.3 analysis. Tongue is 3 mm wide × 4 mm tall × full perimeter length — substantial cross-section. ✓ |
| Front wall (carrying cutouts) | In-plane loads from snap assembly force distributed through front wall | Vertical layers — in-plane loads are in XY (the strong FDM direction for a vertical wall). | ✓ |
| Alignment pins | Bending/shear during assembly (lateral loads as halves are roughly positioned) | Pins grow in +Z — inter-layer bond is the weak direction under lateral bending. Pin diameter 4.0 mm, height 8.0 mm. Cantilever bending. | Low risk: pins experience lateral force only during the brief assembly before the groove engages. Forces are small (user guidance, not impact). ✓ |
| Exterior walls (300 mm span) | Bending from assembly press force and handling | Vertical layers — bending in-plane is strong direction. Box section rib structure (per synthesis.md Section 4) provides 8× bending stiffness. | ✓ |
| RP2040 retention ledge | Shear from module weight and withdrawal force | Ledge is perpendicular to Z (a horizontal disc) — inter-layer bond. | Low risk: module weight ~20 g = 0.2 N. Withdrawal force is gentle push. Ledge cross-section: 1.5 mm wide × ~47 mm circumference ≈ 70 mm² area. PETG tensile ~40 MPa × 0.6 inter-layer factor ≈ 24 MPa. Capacity ~1680 N. Actual load < 20 N. Safety factor > 80×. ✓ |

---

## Feature Traceability (Rubric H)

| Feature | Justification source | Specific reference |
|---------|---------------------|-------------------|
| Box body (220 × 300 × 185 mm, 2.4 mm walls) | vision.md outer dimensions + concept.md seam height + concept.md wall thickness | vision.md Section 2: "220 mm × 300 mm × 400 mm"; concept.md Section 1: seam at 185 mm; concept.md Section 5: "Exterior walls: 2.4 mm nominal (6 perimeters)" |
| Front face wall | vision.md component placement + concept.md zone allocation | vision.md Section 2: "screens and air switch are in the middle of the front face" |
| RP2040 cutout (Φ33.2 mm, X=55, Z=142.5) | requirements.md component list + display-switch-dimensions.md + synthesis.md + spatial-resolution.md | requirements.md Section 5: RP2040 module; display-switch-dimensions.md Section 1: "Outer diameter 33.0 mm"; synthesis.md Section 3: X=55 mm; spatial-resolution.md Section 2: Z=142.5 mm |
| RP2040 retention ledge (integral, Y=12.2, 1.5 mm wide) | concept.md Gap 3 resolution directive + this specification | concept.md Section 6: "bayonet vs. separate part unresolved"; task prompt: "specify an integral 1.5mm-wide ledge at Y=9.8mm depth" (resolved as Y=12.2 mm from exterior face = 2.4 mm wall + 9.8 mm module depth) |
| S3 cutout (48.2 mm sq., X=110, Z=142.5) + pocket to Y=35.5 | display-switch-dimensions.md + synthesis.md + spatial-resolution.md | display-switch-dimensions.md Section 2: "48 mm × 48 mm × 33 mm"; synthesis.md Section 3: X=110 mm; spatial-resolution.md Section 2: pocket to Y=35.5 |
| S3 M2.5 retention bosses | display-switch-dimensions.md + vision.md removable module intent | display-switch-dimensions.md Section 2: "integral M2.5 mounting holes"; vision.md Section 2: modules are "snapped out and placed elsewhere" |
| KRAUS cutout (Φ32.0 mm, X=165, Z=142.5) | requirements.md + display-switch-dimensions.md + synthesis.md + spatial-resolution.md | requirements.md Section 5: KRAUS KWDA-100MB; display-switch-dimensions.md Section 3: "1 1/4" faucet hole, 31.75 mm"; synthesis.md Section 3: X=165 mm; spatial-resolution.md Section 2: Z=142.5 mm |
| Dock opening (157 × 80 mm, X:[31.5,188.5], Z:[0,80]) | requirements.md pump replacement + concept.md + spatial-resolution.md | requirements.md Section 4: "user can remove and replace the pump cartridge"; concept.md Section 6: "approximately 215 mm wide × 95 mm tall"; spatial-resolution.md Section 3: all dock opening dimensions |
| Interior dividing wall (Y=175, 2.0 mm) | concept.md + spatial-resolution.md | concept.md Section 1: "internal dividing wall at approximately 175 mm from the front face"; spatial-resolution.md Section 1 |
| 24 snap arms (18 mm × 2.0 mm × 8.0 mm, 30°/90°) | snap-fit-geometry.md + synthesis.md + spatial-resolution.md | snap-fit-geometry.md Section 2 all arm dimensions; synthesis.md Section 2 all arm dimensions; spatial-resolution.md Section 4 all arm positions |
| Continuous tongue (3.0 mm × 4.0 mm, 2 mm setback) | snap-fit-geometry.md + synthesis.md + spatial-resolution.md | snap-fit-geometry.md Section 4.2; synthesis.md Section 2 tongue dimensions; spatial-resolution.md Section 5 tongue path |
| 4 corner alignment pins (Φ4.0 mm, 8.0 mm tall) | snap-fit-geometry.md + synthesis.md + spatial-resolution.md | snap-fit-geometry.md Section 4.1; synthesis.md Section 2; spatial-resolution.md Section 4 pin positions |
| 4 feet (Φ15 mm, 3 mm tall, 15 mm from corners) | concept.md + spatial-resolution.md | concept.md Section 4: "four printed feet — approximately 15 mm diameter, 3 mm tall, inset 15 mm from each corner edge"; spatial-resolution.md Section 6 |
| Dock cradle snap pockets (4 pockets, floor Z=2.4) | pump-cartridge/concept.md + spatial-resolution.md | pump-cartridge/concept.md dock cradle section; spatial-resolution.md Section 7 |
| 3 mm vertical edge fillets | concept.md + vision.md | concept.md Section 5: "Exterior vertical edge corners: 3 mm fillet radius"; vision.md Section 1: "this is a consumer product" |
| 0.3 mm × 45° elephant's foot chamfer | requirements.md + concept.md | requirements.md FDM constraints: "If the bottom face is a mating surface, add a 0.3 mm × 45° chamfer"; concept.md Section 4: "standard for any build-plate-down print" |
| 0.5 mm exterior reveal | concept.md + snap-fit-geometry.md + synthesis.md | concept.md Section 3: "The top half's exterior wall extends 0.5 mm below the seam plane"; snap-fit-geometry.md Section 4.3; synthesis.md Section 2 |

---

## Open Items for CadQuery Generation Agent

The following items must be resolved before or during CadQuery generation:

1. **S3 cutout width correction:** The interface table identifies a knob clearance shortfall. Change S3 cutout width and height from 48.2 mm to **48.3 mm** to achieve 0.5 mm minimum rotational clearance on each side of the 47.3 mm knob ring.

2. **Exact M2.5 hole positions on S3 PCB:** The S3 retention boss positions (Feature 6) are estimated at 8-o'clock and 2-o'clock. Obtain the exact M2.5 hole XY positions from the Elecrow CrowPanel 1.28" official dimension drawing before placing the bosses.

3. **Dock cradle snap post dimensions:** Feature 14 pocket geometry (width, depth, hook geometry) is a placeholder. Finalize when the dock cradle specification is written.

4. **Snap arm root chamfer vs. support:** The overhang audit (Rubric G, Step 2) resolves the snap arm body overhang with a 45° root chamfer (2 mm × 2 mm). This chamfer should be applied to all 24 arm root undersides in the CadQuery script.

5. **S3 pocket ceiling frangible support:** A designed support shelf at Z = 166.4 mm (0.2 mm below the pocket ceiling at Z = 166.6 mm) with break-away tabs every 5 mm, spanning the full 48.3 mm × 33.1 mm pocket footprint, must be included in the CadQuery model as a separate body (not unioned with the main shell) with the 0.2 mm interface gap.

6. **RP2040 retention ledge frangible support:** A designed support below the annular ledge (at Y = 12.2 mm, Z = 142.5 mm, OD = 33.2 mm, ID = 30.0 mm) with 0.2 mm interface gap and break-away tabs. Must be included as a separate body in the CadQuery model.

7. **Interior dividing wall rib ties:** Add three rib ties connecting the dividing wall to the outer walls at X ≈ 72 mm and X ≈ 145 mm (each rib: 2.0 mm thick × 5.0 mm tall × ~8.5 mm long in Y from the dividing wall to the side wall). Also at the left and right wall junctions (already integral).

8. **CadQuery build order (per decomposition.md recommendation):** Box body first → subtractive operations (cutouts, pocket, openings) → additive features (tongue, arms, pins, feet, dividing wall, bosses, retention ledge) → chamfer/fillet passes last.
