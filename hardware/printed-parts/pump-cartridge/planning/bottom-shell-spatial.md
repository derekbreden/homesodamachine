# Bottom Shell — Spatial Resolution

All coordinates are in the **bottom shell local frame** unless explicitly stated otherwise. Every dimension is a concrete number. No downstream trigonometry or coordinate transforms are required.

---

## 1. System-Level Placement

```
Mechanism: Pump cartridge
Parent: Enclosure interior (220mm W x 300mm D x 400mm H)
Position: front and bottom of the enclosure, cartridge front face flush
          with the dock opening, centered on enclosure width
Orientation: no rotation — cartridge X/Y/Z axes align with enclosure
             width/depth/height axes
```

This section is context only. All geometry below is resolved in the bottom shell's own local frame.

---

## 2. Part Reference Frame

```
Part: Bottom shell
  Origin: front-left-bottom exterior corner
  X: width (left to right), 0..132mm
  Y: depth (front to back), 0..177mm
  Z: height (bottom to top), 0..33.5mm
  Print orientation: open face up, floor on build plate
  Installed orientation: identical to part frame (no rotation),
    translated to enclosure dock position
```

Conventions:
- Front face at Y = 0, rear face at Y = 177.
- Left exterior at X = 0, right exterior at X = 132.
- Floor exterior at Z = 0, open top edge at Z = 33.5.
- All wall thicknesses measured inward from exterior faces.

---

## 3. Derived Geometry

### 3a. Shell Envelope and Wall Thicknesses

**Exterior dimensions:**

| Face | Position | Extent |
|------|----------|--------|
| Left | X = 0 | Full Y, full Z |
| Right | X = 132.0 | Full Y, full Z |
| Front | Y = 0 | Full X, full Z |
| Rear | Y = 177.0 | Full X, full Z |
| Floor | Z = 0 | Full X, full Y |
| Top edge (open) | Z = 33.5 | -- |

**Wall thicknesses:**

| Wall | Outer face | Inner face | Thickness | Notes |
|------|-----------|------------|-----------|-------|
| Left side | X = 0 | X = 2.0 | 2.0mm | Nominal thickness. Thickens at groove band; see below. |
| Right side | X = 132.0 | X = 130.0 | 2.0mm | Nominal thickness. Thickens at groove band; see below. |
| Front | Y = 0 | Y = 2.0 | 2.0mm | |
| Rear | Y = 174.0 | Y = 177.0 | 3.0mm | Thicker wall to support JG press-fit bores |
| Floor | Z = 0 | Z = 2.0 | 2.0mm | |

**Side wall profile at groove band (Z = 12.75 to Z = 17.25):**

The rail grooves are 4.5mm deep, cut into the outer face of each side wall. The wall must be at least 4.5mm (groove depth) + 1.2mm (structural minimum behind groove) = 5.7mm thick at the groove height band.

| Z range | Left wall inner face | Right wall inner face | Wall thickness |
|---------|---------------------|----------------------|----------------|
| 0 to 12.75 | X = 2.0 | X = 130.0 | 2.0mm |
| 12.75 to 17.25 | X = 5.7 | X = 126.3 | 5.7mm |
| 17.25 to 33.5 | X = 2.0 | X = 130.0 | 2.0mm |

**Interior cavity dimensions:**

| Z range | X range | Width | Y range | Depth |
|---------|---------|-------|---------|-------|
| 2.0 to 12.75 | 2.0 to 130.0 | 128.0mm | 2.0 to 174.0 | 172.0mm |
| 12.75 to 17.25 | 5.7 to 126.3 | 120.6mm | 2.0 to 174.0 | 172.0mm |
| 17.25 to 33.5 | 2.0 to 130.0 | 128.0mm | 2.0 to 174.0 | 172.0mm |

**Center divider wall** (separates left and right pump bays):

| Parameter | Value |
|-----------|-------|
| Center X | 66.0 |
| Left face | X = 65.0 |
| Right face | X = 67.0 |
| Thickness | 2.0mm |
| Y extent | Y = 2.0 to Y = 150.0 |
| Z extent | Z = 2.0 to Z = 33.5 |

**Pump bay dimensions:**

| Bay | X range (nominal) | Width | Pump head clearance per side |
|-----|-------------------|-------|------------------------------|
| Left | 2.0 to 65.0 | 63.0mm | 0.2mm (on 62.6mm pump head) |
| Right | 67.0 to 130.0 | 63.0mm | 0.2mm |

**Groove band interference note:** At the groove Z-band (Z = 12.75 to 17.25), each bay narrows to 59.3mm (left: X = 5.7 to 65.0; right: X = 67.0 to 126.3). The pump head is 62.6mm wide. The pump head has rounded corners; if the corner radius exceeds 4mm, the pump head clears the thickened wall at this height band (10.75 to 15.25mm above the floor interior is within the corner transition zone). The Kamoer geometry does not provide a caliper-verified corner radius. This clearance must be verified with the physical pump before the parts specification is finalized. If insufficient, the options are: increase cartridge width to ~139mm at the groove band, reduce groove depth, or add a local relief pocket at each pump bay corner in the groove band.

---

### 3b. Rail Groove Positions

**Groove cross-section (both grooves identical):**

| Parameter | Value |
|-----------|-------|
| Width (Z direction) | 4.5mm |
| Depth (X direction, into wall from outside) | 4.5mm |
| Center Z | 15.0 |
| Top edge Z | 17.25 |
| Bottom edge Z | 12.75 |

**Left groove:**

| Parameter | Value |
|-----------|-------|
| Groove mouth (outer face) | X = 0 |
| Groove floor (innermost surface) | X = 4.5 |
| Remaining wall behind groove | 1.2mm (X = 4.5 to X = 5.7) |
| Y start (chamfer begins) | Y = 0 |
| Y start (full-depth groove begins) | Y = 5.0 |
| Y end | Y = 177.0 |

**Right groove (mirror of left):**

| Parameter | Value |
|-----------|-------|
| Groove mouth (outer face) | X = 132.0 |
| Groove floor (innermost surface) | X = 127.5 |
| Remaining wall behind groove | 1.2mm (X = 126.3 to X = 127.5) |
| Y start (chamfer begins) | Y = 0 |
| Y start (full-depth groove begins) | Y = 5.0 |
| Y end | Y = 177.0 |

**Entry chamfer (both grooves):**

| Parameter | Value |
|-----------|-------|
| Y range | Y = 0 to Y = 5.0 |
| Angle | 30 degrees from groove face |
| Effect on width | Tapers from ~10.3mm at Y = 0 to 4.5mm at Y = 5.0 |
| Effect on depth | Tapers from 0mm at Y = 0 to 4.5mm at Y = 5.0 |

**Detent relief (one per groove, at full-insertion position):**

| Parameter | Value |
|-----------|-------|
| Y center | Y = 174.5 |
| Y extent | Y = 173.5 to Y = 175.5 (2.0mm long) |
| Additional depth beyond groove floor | 0.3mm |

---

### 3c. John Guest Fitting Pocket Positions

The rear wall contains 4 JG union press-fit bores in a 2x2 pattern. Each bore axis runs along Y, through the 3.0mm rear wall (Y = 174.0 to Y = 177.0). Two bores per pump bay, stacked vertically.

**Rear wall:**

| Parameter | Value |
|-----------|-------|
| Outer face | Y = 177.0 |
| Inner face | Y = 174.0 |
| Thickness | 3.0mm |

**Bore center positions:**

The JG body end OD is 15.10mm (radius 7.55mm). Two vertically stacked bores per bay require at least 15.10 + 2.0 (minimum wall between bores) + 15.10 = 32.2mm of vertical space. The bottom shell interior height is 31.5mm (Z = 2.0 to Z = 33.5). The pattern fits by allowing the lower bores to sit with their body ends flush against the floor interior and the upper bores to have their body ends protrude 0.7mm above the bottom shell open edge (captured by the top shell).

| Bore | Bay | X | Z | Body end bottom Z | Body end top Z |
|------|-----|---|---|-------------------|----------------|
| JG1 (left lower) | Left | 33.5 | 9.55 | 2.0 | 17.1 |
| JG2 (right lower) | Right | 98.5 | 9.55 | 2.0 | 17.1 |
| JG3 (left upper) | Left | 33.5 | 26.65 | 19.1 | 34.2 |
| JG4 (right upper) | Right | 98.5 | 26.65 | 19.1 | 34.2 |

| Derived parameter | Value |
|-------------------|-------|
| Vertical center-to-center | 17.1mm |
| Wall between upper and lower body ends | 19.1 - 17.1 = 2.0mm |
| Lower body end to floor interior | 2.0 - 2.0 = 0mm (flush) |
| Upper body end above bottom shell open edge | 34.2 - 33.5 = 0.7mm (captured by top shell) |
| Horizontal center-to-center (across bays) | 98.5 - 33.5 = 65.0mm |

**X positions:** Each bore is centered in its pump bay. Left bay center: (2.0 + 65.0) / 2 = 33.5. Right bay center: (67.0 + 130.0) / 2 = 98.5.

**Bore profile (each bore identical):**

The fitting's center body (9.31mm OD, 12.16mm long) press-fits into the bore. The body-end shoulders (step from 9.31mm to 15.10mm OD) seat against the wall faces, providing positive axial location. Body ends protrude from both wall faces.

| Feature | Diameter | Y extent | Notes |
|---------|----------|----------|-------|
| Press-fit bore | 9.6mm (as-designed; prints to ~9.5mm with +0.1mm compensation) | Y = 174.0 to Y = 177.0 (3.0mm, full wall) | Grips 9.31mm center body |

No counterbore is needed. The body-end shoulders (15.10mm) seat against the flat wall faces. Body ends protrude freely on both sides:
- **Inboard protrusion** (into cartridge interior): 12.08mm body end + ~1.4mm collet = ~13.5mm from Y = 174.0, reaching to approximately Y = 160.5.
- **Outboard protrusion** (toward dock): 12.08mm body end + ~1.4mm collet from Y = 177.0.

The rear wall face must be flat and perpendicular to Y at each bore location to provide a clean shoulder seat surface. The 15.10mm body end OD requires 15.10mm of clearance around each bore on the wall face (no adjacent features encroaching within this diameter).

---

### 3d. Linkage Arm Channel Positions

Two channels guide the linkage arms along the outer edges of the pump bays at mid-height. Each channel is positioned at the vertical center of the JG bore pattern (shell Z = 18.1) so that the linkage arms apply force through the center of the collet pattern on the release plate, preventing tilt during operation.

**Channel construction:**

The channel sits just above the groove band (Z = 12.75..17.25). The groove band thickening creates a horizontal top surface at Z = 17.25 (X = 2.0 to 5.7 on the left side, X = 126.3 to 130.0 on the right) that serves as a natural shelf for the arm. No separate bridge shelf is required. The inner rib (vertical wall rising from the floor to the channel top) provides the lateral constraint on the channel's inboard side. The side wall interior face provides the outboard lateral constraint.

The inner rib extends from the floor (Z = 2.0) to the channel top (Z = 20.25) for structural support and FDM printability. Both the rib and the side wall are vertical features -- no overhangs. The arm rests on the groove band thickening top surface at Z = 17.25 (partially supported from X = 2.0 to 5.7 by the thickening, with the remainder of the arm span cantilevered as a rigid beam to X = 9.0).

| Parameter | Value |
|-----------|-------|
| Channel width (between side wall and rib inner faces) | 7.0mm |
| Channel height (arm slot) | 3.0mm (Z = 17.25 to Z = 20.25) |
| Channel center Z | 18.75 |
| JG bore pattern center Z | 18.1 (offset: 0.65mm -- within acceptable range to prevent plate tilt) |
| Inner rib thickness | 1.2mm |
| Inner rib Z extent | Z = 2.0 to Z = 20.25 (floor to channel top) |
| Arm sits at | Z = 17.25 (groove band thickening top surface) |
| Arm top | Z = 20.25 (flush with channel top / rib top) |

**Left channel:**

| Parameter | Value |
|-----------|-------|
| Channel center X | 5.5 |
| Inner rib (right side): left face | X = 9.0 |
| Inner rib (right side): right face | X = 10.2 |
| Inner rib Z extent | Z = 2.0 to Z = 20.25 |
| Outer wall (left side) acts as left guide | X = 2.0 (interior face of left side wall) |
| Channel interior X range | X = 2.0 to X = 9.0 |
| Channel interior Z range | Z = 17.25 to Z = 20.25 |
| Arm rests on | Groove band thickening top surface at Z = 17.25 (X = 2.0 to 5.7) |
| Y extent | Y = 2.0 to Y = 174.0 |

**Right channel (mirror of left):**

| Parameter | Value |
|-----------|-------|
| Channel center X | 126.5 |
| Inner rib (left side): right face | X = 123.0 |
| Inner rib (left side): left face | X = 121.8 |
| Inner rib Z extent | Z = 2.0 to Z = 20.25 |
| Outer wall (right side) acts as right guide | X = 130.0 (interior face of right side wall) |
| Channel interior X range | X = 123.0 to X = 130.0 |
| Channel interior Z range | Z = 17.25 to Z = 20.25 |
| Arm rests on | Groove band thickening top surface at Z = 17.25 (X = 126.3 to 130.0) |
| Y extent | Y = 2.0 to Y = 174.0 |

---

### 3e. Mounting Partition Slot Positions

Two vertical slots in the side walls receive the mounting partition at the pump head / motor junction plane.

**Slot Y position derivation:** Front wall interior at Y = 2.0. Front tube routing zone is 25mm deep (Y = 2.0 to Y = 27.0). Pump head is ~48mm deep (Y = 27.0 to Y = 75.0). Partition sits at the rear face of the pump heads.

| Parameter | Value |
|-----------|-------|
| Slot center Y | 75.0 |
| Partition thickness (assumed) | 5.0mm |
| Slot width (Y) | 5.4mm (5.0 + 0.2mm clearance per side) |
| Slot front edge Y | 72.3 |
| Slot rear edge Y | 77.7 |

**Left wall slot:**

| Parameter | Value |
|-----------|-------|
| Slot X range | X = 0 to X = 2.0 (2.0mm deep into wall, from interior face) |
| Slot Y range | Y = 72.3 to Y = 77.7 |
| Slot Z range | Z = 2.0 to Z = 33.5 (full interior height) |

**Right wall slot:**

| Parameter | Value |
|-----------|-------|
| Slot X range | X = 130.0 to X = 132.0 (2.0mm deep into wall, from interior face) |
| Slot Y range | Y = 72.3 to Y = 77.7 |
| Slot Z range | Z = 2.0 to Z = 33.5 |

The partition drops into these slots from above and is captured when the top shell closes (matching slots in the top shell ceiling).

---

### 3f. Snap-Fit Catch Ledge Positions

Catch ledges on the upper inner edges of all 4 walls. The top shell's cantilever hooks engage these ledges.

**Ledge geometry (all ledges identical):**

| Parameter | Value |
|-----------|-------|
| Z extent | Z = 33.2 to Z = 33.5 (0.3mm tall) |
| Protrusion depth (from wall inner face toward interior) | 0.3mm |
| Underside chamfer | 45 degrees, 0.3mm (eliminates overhang) |
| Ledge width along wall | 8.0mm each |

**Left wall (5 ledges, protrude in +X from X = 2.0):**

| # | Y center | Y extent |
|---|----------|----------|
| L1 | 19.0 | 15.0 to 23.0 |
| L2 | 54.0 | 50.0 to 58.0 |
| L3 | 89.0 | 85.0 to 93.0 |
| L4 | 124.0 | 120.0 to 128.0 |
| L5 | 159.0 | 155.0 to 163.0 |

**Right wall (5 ledges, protrude in -X from X = 130.0):**

Same Y positions as left wall.

**Front wall (4 ledges, protrude in +Y from Y = 2.0):**

| # | X center | X extent |
|---|----------|----------|
| F1 | 18.0 | 14.0 to 22.0 |
| F2 | 50.0 | 46.0 to 54.0 |
| F3 | 82.0 | 78.0 to 86.0 |
| F4 | 114.0 | 110.0 to 118.0 |

**Rear wall (4 ledges, protrude in -Y from Y = 174.0):**

Same X positions as front wall.

**Total: 18 ledges** (5 + 5 + 4 + 4).

---

### 3g. Return Spring Boss Positions

Two cylindrical bosses on the inboard face of the rear wall, centered between the upper and lower JG bores in each bay.

| Parameter | Left boss | Right boss |
|-----------|-----------|------------|
| X | 33.5 | 98.5 |
| Z | 18.25 | 18.25 |
| Base (on wall face) Y | 174.0 | 174.0 |
| Tip Y | 171.0 | 171.0 |
| Diameter | 3.0mm | 3.0mm |
| Height (protrusion from wall) | 3.0mm | 3.0mm |

The bosses sit in the 2.0mm wall gap between the upper and lower JG body ends (body end tops of lower bores at Z = 17.1, body end bottoms of upper bores at Z = 20.25; boss center at Z = 18.25 with 3.0mm diameter fits within this 2.0mm gap -- the boss is 1.5mm radius, which extends from Z = 16.75 to Z = 19.75, overlapping the body end edges by 0.35mm on each side). If this overlap is unacceptable, the bosses can be shifted to X positions offset from the bore centerlines (e.g., X = 25.0 and X = 90.0, in the clear space between the body end perimeter and the bay wall). The spring OD (~5mm) must clear the body ends regardless.

**Revised boss positions (offset to avoid body end overlap):**

| Parameter | Left boss | Right boss |
|-----------|-----------|------------|
| X | 25.0 | 90.0 |
| Z | 18.25 | 18.25 |
| Base Y | 174.0 | 174.0 |
| Tip Y | 171.0 | 171.0 |
| Diameter | 3.0mm | 3.0mm |

At X = 25.0, distance from left lower bore center (X = 33.5): 8.5mm. Body end radius: 7.55mm. Clearance: 8.5 - 7.55 = 0.95mm. Spring OD 5.0mm (radius 2.5mm): boss center to bore center = 8.5mm, spring edge to body end edge = 8.5 - 2.5 - 7.55 = -1.55mm. The spring overlaps the body end.

This means the bosses must be at the bore centerline X (X = 33.5 and 98.5) where the Z gap between body ends provides the only available space. The 2.0mm Z gap between body ends is tight for a 3.0mm diameter boss. The boss must be reduced to 2.0mm diameter or positioned at Z = 18.1 (midpoint between Z = 17.1 and Z = 20.25) with the boss just fitting in the gap.

**Final boss specification:**

| Parameter | Left boss | Right boss |
|-----------|-----------|------------|
| X | 33.5 | 98.5 |
| Z | 18.1 | 18.1 |
| Base Y | 174.0 | 174.0 |
| Tip Y | 171.0 | 171.0 |
| Diameter | 2.0mm | 2.0mm |
| Height | 3.0mm | 3.0mm |

A 2.0mm diameter boss fits within the 2.0mm gap between body ends (Z = 17.1 to Z = 20.25). The spring (5.0mm OD, 2.5mm ID approximately) centers on this boss.

---

### 3h. Pump Bay Layout

Pumps are oriented with heads facing front (Y = 0 direction) and motors facing rear (Y = 177 direction).

**Pump center axis positions (X, Z):**

| Pump | Center X | Center Z | Notes |
|------|----------|----------|-------|
| Left | 33.5 | 33.3 | (2.0 + 65.0)/2 = 33.5; 2.0 + 62.6/2 = 33.3 |
| Right | 98.5 | 33.3 | (67.0 + 130.0)/2 = 98.5 |

Center Z = 33.3 means the pump center is just below the bottom shell top edge (Z = 33.5). The pump head spans Z = 2.0 to Z = 64.6, crossing the shell parting line into the top shell.

**Pump Y zones within cartridge:**

| Zone | Y start | Y end | Contents |
|------|---------|-------|----------|
| Front tube routing | 2.0 | 27.0 | BPT tube bends from pump face to routing channels |
| Pump head | 27.0 | 75.0 | 48mm pump head body |
| Mounting partition | 72.3 | 77.7 | Partition slot (overlaps with pump head rear / motor front) |
| Motor + adapter | 75.0 | 143.0 | ~4mm adapter + ~63mm motor body |
| Motor nub | 143.0 | 148.0 | 5mm shaft nub |
| Air gap | 148.0 | 153.0 | 5mm thermal clearance |
| Release/electrical zone | 153.0 | 174.0 | Release plate, springs, wiring |

**Clearances:**

| Interface | Value |
|-----------|-------|
| Pump head to left/right side wall (non-groove band) | 0.2mm per side |
| Pump head to center divider | 0.2mm per side |
| Pump head to floor | 0mm (rests on floor interior at Z = 2.0) |
| Motor body (~35mm dia) to bay walls | ~14mm per side |
| Between pumps (across center divider) | 2.0mm divider + 0.2mm clearance each side = 2.4mm |

---

### 3i. Blade Terminal Slot Positions

Four recessed slots in the exterior rear face (Y = 177.0) for 6.3mm male blade terminals. Positioned in the corners of the rear face, outside the JG fitting bore pattern.

| Terminal | X center | Z center |
|----------|----------|----------|
| BT1 (left lower) | 12.0 | 5.5 |
| BT2 (left upper) | 12.0 | 28.0 |
| BT3 (right lower) | 120.0 | 5.5 |
| BT4 (right upper) | 120.0 | 28.0 |

**Each slot:**

| Parameter | Value |
|-----------|-------|
| Width (X) | 8.0mm |
| Height (Z) | 4.0mm |
| Recess depth into rear face (Y) | 1.0mm |
| Surrounding lip | 0.5mm |

The blade terminal body sits in the recessed slot. The 6.3mm blade protrudes outward past Y = 177.0.

---

### 3j. Exterior Edge Treatment

| Feature | Specification |
|---------|---------------|
| Exterior fillets | 1.0mm radius on all exterior edges |
| Elephant's foot chamfer | 0.3mm x 45 degrees on bottom perimeter edge (Z = 0 plane) |

---

## 4. Interface Summary

### 4.1. Top shell

| Parameter | Value |
|-----------|-------|
| Mating part | Top shell |
| Interface type | Perimeter snap-fit catch ledges + flat mating face at Z = 33.5 |
| Position | Z = 33.5, full perimeter |
| Geometry | 18 catch ledges (Section 3f). Top shell is inset 0.3mm per side (131.4mm x 176.4mm outer). |

### 4.2. Mounting partition

| Parameter | Value |
|-----------|-------|
| Mating part | Mounting partition |
| Interface type | Vertical slots in side walls |
| Left slot | X = 0..2.0, Y = 72.3..77.7, Z = 2.0..33.5 |
| Right slot | X = 130.0..132.0, Y = 72.3..77.7, Z = 2.0..33.5 |
| Slot width (Y) | 5.4mm |
| Slot depth (X) | 2.0mm |
| Mating feature on partition | Registration tabs on bottom corners |

### 4.3. John Guest fittings (x4)

| Parameter | Value |
|-----------|-------|
| Mating part | John Guest PP0408W union |
| Interface type | Press-fit bore in rear wall |
| Bore centers (X, Z) | JG1: (33.5, 9.55), JG2: (98.5, 9.55), JG3: (33.5, 26.65), JG4: (98.5, 26.65) |
| Bore axis | Y, through wall Y = 174.0 to Y = 177.0 |
| Bore diameter | 9.6mm (as-designed; prints to ~9.5mm for press-fit on 9.31mm center body) |
| Shoulder seat | Body end shoulders (15.10mm OD) seat against wall faces at Y = 174.0 and Y = 177.0 |
| Inboard protrusion | ~13.5mm from Y = 174.0 (body end + collet) |

### 4.4. Linkage arms (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Linkage arm (left and right) |
| Interface type | Mid-height guided channel (lateral and vertical constraint, axial sliding) |
| Left channel | X = 2.0..9.0, Z = 17.25..20.25, Y = 2.0..174.0 |
| Right channel | X = 123.0..130.0, Z = 17.25..20.25, Y = 2.0..174.0 |
| Arm cross-section | 6.0mm W x 3.0mm H |
| Arm sits at | Z = 17.25 (groove band thickening top surface) |
| Arm travel | 2-4mm in Y |
| Partition notches | Mid-height: 8mm W x 5mm H at Z = 15.25..20.25 at partition outer corners (updated from floor level) |

### 4.5. Return springs (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Compression springs |
| Interface type | Cylindrical centering boss on rear wall inboard face |
| Left boss | (X=33.5, Y=174.0 base / 171.0 tip, Z=18.1), 2.0mm dia, 3.0mm height |
| Right boss | (X=98.5, Y=174.0 base / 171.0 tip, Z=18.1), 2.0mm dia, 3.0mm height |
| Mating feature on release plate | Matching centering boss |

### 4.6. Release plate

| Parameter | Value |
|-----------|-------|
| Mating part | Release plate |
| Interface type | No direct attachment to bottom shell. Guided by JG fitting collets. |
| Position in rear zone | Approximately Y = 155..165 |
| Relationship | Springs bias plate away from rear wall bosses; JG collet bores guide plate |

### 4.7. Dock rails (external)

| Parameter | Value |
|-----------|-------|
| Mating part | Dock rails (enclosure) |
| Interface type | Rail tongue slides into groove channel |
| Left groove | X = 0..4.5, Z = 12.75..17.25, Y = 0..177 |
| Right groove | X = 127.5..132.0, Z = 12.75..17.25, Y = 0..177 |
| Rail tongue | 4.0mm W x 4.0mm H |
| Clearance | 0.25mm per side |
| Detent relief | Y = 173.5..175.5, 0.3mm extra depth |

### 4.8. Blade terminals (x4)

| Parameter | Value |
|-----------|-------|
| Mating part | 6.3mm male blade terminals |
| Interface type | Recessed slot in rear face (Y = 177.0) |
| Positions (X, Z) | BT1: (12, 5.5), BT2: (12, 28), BT3: (120, 5.5), BT4: (120, 28) |
| Slot | 8mm W x 4mm H x 1mm deep recess |
| Dock-side mate | Shrouded female blade receptacles |

### 4.9. Pumps (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Kamoer KPHM400 pumps |
| Interface type | No direct contact. Pumps mount to partition via M3 vibration isolation mounts. |
| Pump center (X, Z) | Left: (33.5, 33.3), Right: (98.5, 33.3) |
| Load path | Pump -> isolation mounts -> partition -> partition slots -> bottom shell side walls/floor |

---

## 5. Transform Summary

The bottom shell sits flat in the dock with no rotation. Part frame = installed frame + translation.

```
Part frame -> Installed frame:
  Rotation: identity (none)
  Translation: + (Tx, Ty, Tz) to dock position in enclosure coordinates

Installed frame -> Part frame:
  Translation: - (Tx, Ty, Tz)
  Rotation: identity
```

**Verification (3 test points):**

| Point | Part frame (X, Y, Z) | Installed frame | Round-trip back to part frame | Match? |
|-------|----------------------|-----------------|-------------------------------|--------|
| Origin | (0, 0, 0) | (Tx, Ty, Tz) | (0, 0, 0) | Yes |
| Rear-right-top corner | (132, 177, 33.5) | (Tx+132, Ty+177, Tz+33.5) | (132, 177, 33.5) | Yes |
| JG1 bore center | (33.5, 174.0, 9.55) | (Tx+33.5, Ty+174.0, Tz+9.55) | (33.5, 174.0, 9.55) | Yes |

No transforms are needed for downstream agents. All coordinates in this document are directly usable in CadQuery.
