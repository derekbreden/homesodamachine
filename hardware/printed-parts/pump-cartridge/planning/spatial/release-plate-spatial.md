# Spatial Resolution: Release Plate

## Discrepancy Notice

The Sub-D spatial document and the Sub-E spatial document disagree on the fitting grid center Z position and guide post XZ positions. Sub-D places the fitting grid center at (80, 36) with bores at Z = 26 and Z = 46. Sub-E places the grid center at (80, 37.5) with fittings at Z = 27.5 and Z = 47.5. Correspondingly, guide post positions differ: Sub-D has posts at (58, 14.5), (102, 14.5), (58, 57.5), (102, 57.5); Sub-E has posts at (60, 17.5), (100, 17.5), (60, 57.5), (100, 57.5).

Sub-D also places the release plate on the interior side of the rear wall (Y = 9.5 to 14.5, between the rear wall interior face at Y = 8.5 and the dock-side body ends of the fittings). Sub-E places the release plate on the exterior/dock side of the rear wall (negative Y values). Sub-G's spatial document is consistent with Sub-D's framing (plate at Y = 8.5 to 13.5 at rest, slots at Y = 17..23).

**This document follows the Sub-D spatial document as authoritative.** Sub-D contains the complete Y-axis stack-up derivation from caliper-verified fitting dimensions. The Sub-E document's positions should be updated to match Sub-D. Where Sub-D and Sub-E agree (post diameter 3.5 mm, bore diameter 3.8 mm, 4-post diagonal layout), those values are used directly.

For the release plate's local reference frame, I adopt the Sub-D fitting grid and guide post positions. The specific values used are:

- Fitting bore centers (tray frame): (70, 26), (90, 26), (70, 46), (90, 46)
- Guide post centers (tray frame): (58, 14.5), (102, 14.5), (58, 57.5), (102, 57.5)
- Release plate Y range at rest (tray frame): 9.5 to 14.5

---

## 1. System-Level Placement

```
Mechanism: Release Plate
Parent: Tray (Sub-A box shell), riding on guide posts (Sub-E)
Position: between the rear wall interior face (tray Y = 8.5) and the
          dock-side body ends of the 4 John Guest fittings (tray Y = 15.9)
Orientation: plate XZ plane parallel to tray XZ plane; plate slides along tray Y axis
```

The release plate is a small flat plate that slides along the Y axis on 4 guide posts. It sits inside the cartridge, just forward of the rear wall interior face, engaging the dock-facing collets of the 4 John Guest fittings. When the user squeezes, the plate moves in the +Y direction (toward the fittings), pushing the collets inward and releasing all 4 tubes simultaneously.

---

## 2. Part Reference Frame

```
Part: Release Plate
  Origin: lower-left-front corner of plate bounding box
  X: width, 0..55 mm (left to right, mirroring tray width direction)
  Y: depth (thickness), 0..5 mm (0 = front/user-facing face, 5 = rear/dock-facing face)
  Z: height, 0..55 mm (bottom to top, mirroring tray height direction)
  Print orientation: flat, XY plane on build plate (bore axes along Z for best circularity)
  Installed orientation: plate XZ is parallel to tray XZ;
    plate X aligns with tray X, plate Z aligns with tray Z,
    plate Y aligns with tray Y (plate Y=0 faces the user/fittings, plate Y=5 faces the dock/rear wall)
```

**Note on plate Y direction:** The plate is 5 mm thick. Plate Y = 0 is the user-facing face (faces the fittings). Plate Y = 5 is the dock-facing face (faces the rear wall). When the user squeezes, the plate moves in the +Y tray direction. The plate's user-facing face (plate Y = 0) contacts the collets and pushes them inward (+Y in tray frame).

---

## 3. Derived Geometry

### 3a. Plate Envelope in Tray Frame

The release plate must span all 4 fitting bores and all 4 guide posts. The bounding rectangle in the tray XZ plane is determined by the outermost features:

- Outermost guide post centers: X = 58 and X = 102, Z = 14.5 and Z = 57.5
- Guide post bore radius on plate: 3.8 / 2 = 1.9 mm
- Minimum plate edge beyond outermost guide bore edge: 2.0 mm structural wall

Minimum plate extent:
- X_min = 58 - 1.9 - 2.0 = 54.1 mm (tray frame)
- X_max = 102 + 1.9 + 2.0 = 105.9 mm (tray frame)
- Z_min = 14.5 - 1.9 - 2.0 = 10.6 mm (tray frame)
- Z_max = 57.5 + 1.9 + 2.0 = 61.4 mm (tray frame)

Required plate dimensions: 51.8 mm wide (X) x 50.8 mm tall (Z). Rounding up to 55 x 55 mm (matching concept document) with the plate centered on the fitting grid center in X and vertically balanced between the guide posts.

**Plate placement in tray frame (at rest position):**

| Parameter | Value (tray frame, mm) | Derivation |
|-----------|----------------------|------------|
| X range | 52.5 to 107.5 | Centered on fitting grid center X = 80; 80 - 27.5 = 52.5, 80 + 27.5 = 107.5 |
| Z range | 8.5 to 63.5 | Centered on fitting grid center Z = 36; 36 - 27.5 = 8.5, 36 + 27.5 = 63.5 |
| Y range (at rest) | 9.5 to 14.5 | Per Sub-D: 1.0 mm gap from rear wall interior (Y = 8.5), 5 mm thickness |

**Clearance to tray interior walls:**
- Left edge (tray X = 52.5) to left interior wall (tray X = 5): 47.5 mm. OK.
- Right edge (tray X = 107.5) to right interior wall (tray X = 155): 47.5 mm. OK.
- Bottom edge (tray Z = 8.5) to floor interior (tray Z = 3): 5.5 mm. OK.
- Top edge (tray Z = 63.5) to top of wall (tray Z = 72): 8.5 mm. OK.

### 3b. Tray-to-Plate Coordinate Transform

The plate's local origin (0, 0, 0) corresponds to tray frame (52.5, 14.5, 8.5) when the plate is at the rest position.

```
Plate frame -> Tray frame (at rest):
  tray_X = plate_X + 52.5
  tray_Y = (5 - plate_Y) + 9.5  =  14.5 - plate_Y
  tray_Z = plate_Z + 8.5

Explanation of Y inversion:
  plate Y = 0 is the user-facing face, which is at tray Y = 14.5 (at rest)
  plate Y = 5 is the dock-facing face, which is at tray Y = 9.5 (at rest)
  So: tray_Y = 14.5 - plate_Y
```

When the plate travels 1.5 mm toward the fittings (+Y tray direction), the transform becomes:

```
Plate frame -> Tray frame (at 1.5 mm travel):
  tray_X = plate_X + 52.5
  tray_Y = 16.0 - plate_Y
  tray_Z = plate_Z + 8.5
```

### 3c. Stepped Bore Positions (Plate Frame)

The 4 stepped bores must be coaxial with the 4 fitting bore centers. The fitting bore centers in the tray frame are at (70, 26), (90, 26), (70, 46), (90, 46). Converting to plate frame using the transform from 3b:

| Bore | Tray X | Tray Z | Plate X (= tray_X - 52.5) | Plate Z (= tray_Z - 8.5) |
|------|--------|--------|---------------------------|--------------------------|
| B1 (lower-left) | 70.0 | 26.0 | 17.5 | 17.5 |
| B2 (lower-right) | 90.0 | 26.0 | 37.5 | 17.5 |
| B3 (upper-left) | 70.0 | 46.0 | 17.5 | 37.5 |
| B4 (upper-right) | 90.0 | 46.0 | 37.5 | 37.5 |

Center-to-center spacing: 20.0 mm in both plate X and plate Z.

Bore grid center in plate frame: (27.5, 27.5) -- centered in the 55 x 55 mm plate.

### 3d. Stepped Bore Profile (Along Plate Y Axis)

Each stepped bore is identical. The bore axis runs along plate Y (through the 5 mm plate thickness). Plate Y = 0 is the user-facing/fitting-facing side.

The bore has three concentric diameters, cut from two directions:

| Feature | Diameter (mm) | Y-start (plate) | Y-end (plate) | Depth (mm) | Cut from | Purpose |
|---------|---------------|------------------|----------------|------------|----------|---------|
| Body end clearance counterbore | 15.5 | 0 | 1.0 | 1.0 | User face (Y=0) | Clears 15.10 mm body end OD of fitting dock-side section |
| Collet engagement counterbore | 9.8 | 1.0 | 3.0 | 2.0 | User face (Y=0) | Lateral constraint on 9.57 mm collet OD |
| Tube clearance through-hole | 6.5 | 0 | 5.0 | 5.0 (full thickness) | Through | 6.35 mm tube passes freely; annular face between 6.5 mm hole and 6.69 mm collet ID pushes collet inward |

**Cross-section profile (reading from user face Y=0 to dock face Y=5):**

| Plate Y (mm) | Bore diameter (mm) | Wall to next bore (mm) |
|--------------|-------------------|----------------------|
| 0.0 to 1.0 | 15.5 | 20.0 - 15.5 = 4.5 |
| 1.0 to 3.0 | 9.8 | 20.0 - 9.8 = 10.2 |
| 3.0 to 5.0 | 6.5 | 20.0 - 6.5 = 13.5 |

**Collet engagement geometry:** At rest (tray Y = 14.5 for plate user face), the extended collet tip is at tray Y = 14.5 (collet tip touches plate user face). The collet protrudes ~1.4 mm from the body end face. The body end face is at tray Y = 15.9. So at rest, the collet occupies the space from tray Y = 14.5 to 15.9. In plate coordinates, this maps to plate Y = 0 (collet tip) extending into the plate to plate Y = 0 (it is flush with the face). The collet engagement counterbore (plate Y = 1.0 to 3.0, 9.8 mm dia) surrounds the collet as it is pushed inward during squeeze. The body end clearance counterbore (plate Y = 0 to 1.0, 15.5 mm) provides room for the body end section that follows the collet.

**Critical tolerance:** The 6.5 mm through-hole has only 0.19 mm engagement lip per side against the 6.69 mm collet ID. This annular face (from 6.5 mm bore edge to 6.69 mm collet ID) is the contact surface that pushes the collet inward. Print at 0.1 mm layer height; verify with test print.

### 3e. Guide Post Bore Positions (Plate Frame)

The 4 guide post centers in the tray frame are at (58, 14.5), (102, 14.5), (58, 57.5), (102, 57.5). Converting to plate frame:

| Post bore | Tray X | Tray Z | Plate X (= tray_X - 52.5) | Plate Z (= tray_Z - 8.5) |
|-----------|--------|--------|---------------------------|--------------------------|
| G1 (lower-left) | 58.0 | 14.5 | 5.5 | 6.0 |
| G2 (lower-right) | 102.0 | 14.5 | 49.5 | 6.0 |
| G3 (upper-left) | 58.0 | 57.5 | 5.5 | 49.0 |
| G4 (upper-right) | 102.0 | 57.5 | 49.5 | 49.0 |

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.8 mm |
| Post diameter (mating) | 3.5 mm |
| Clearance per side | 0.15 mm |
| Bore depth | 5.0 mm (full plate thickness, through-hole) |
| Post bore rectangle span (plate frame) | X: 5.5 to 49.5 (44.0 mm), Z: 6.0 to 49.0 (43.0 mm) |

**Edge clearance check:**
- G1 to plate left edge (plate X = 0): 5.5 - 1.9 = 3.6 mm wall. OK.
- G2 to plate right edge (plate X = 55): 55 - 49.5 - 1.9 = 3.6 mm wall. OK.
- G1 to plate bottom edge (plate Z = 0): 6.0 - 1.9 = 4.1 mm wall. OK.
- G3 to plate top edge (plate Z = 55): 55 - 49.0 - 1.9 = 4.1 mm wall. OK.

**Bore-to-bore interference check:**
- G1 to B1: distance = sqrt((17.5 - 5.5)^2 + (17.5 - 6.0)^2) = sqrt(144 + 132.25) = sqrt(276.25) = 16.62 mm. Nearest bore edges: 16.62 - 1.9 (guide bore radius) - 7.75 (15.5 mm counterbore radius) = 6.97 mm. OK.
- G1 to B3: distance = sqrt((17.5 - 5.5)^2 + (37.5 - 6.0)^2) = sqrt(144 + 992.25) = sqrt(1136.25) = 33.71 mm. OK.

### 3f. Linkage Rod Attachment Positions (Plate Frame)

The linkage rods attach to the left and right edges of the plate. From the Sub-G spatial document, the rods are 4 mm diameter PETG rods running parallel to the tray Y axis. The rod centers pass through the tray side wall slots at tray Z = 37.5 (slot Z center) and tray Y = 20.0 (slot Y center).

The rods attach at the plate's left and right edges at the plate's vertical center.

**Left rod attachment:**

| Parameter | Plate frame value | Tray frame value | Derivation |
|-----------|-------------------|------------------|------------|
| X position | 0 (left edge of plate) | 52.5 | Plate left edge |
| Z position | 27.5 (plate vertical center) | 36.0 | Plate center aligns with fitting grid center Z |
| Y position | 2.5 (plate mid-thickness) | 12.0 (at rest) | Center of 5 mm plate |

**Right rod attachment:**

| Parameter | Plate frame value | Tray frame value | Derivation |
|-----------|-------------------|------------------|------------|
| X position | 55.0 (right edge of plate) | 107.5 | Plate right edge |
| Z position | 27.5 | 36.0 | Same as left |
| Y position | 2.5 | 12.0 (at rest) | Same as left |

**Rod-to-slot alignment check:** The rods run from the plate edge at tray Z = 36.0 to the slots at tray Z = 37.5. This is a 1.5 mm Z offset. The rods are not perfectly horizontal -- they angle slightly upward (+Z) as they travel from the plate toward the slots. Over the distance from the plate edge to the slot (tray X = 52.5 to tray X = 5 for the left rod, approximately 47.5 mm), the rod rises 1.5 mm. This is an angle of arctan(1.5 / 47.5) = 1.8 degrees. The slot has 0.5 mm clearance per side in Z (5 mm slot for 4 mm rod), which accommodates the 1.5 mm offset at the slot location.

However, the rod attachment on the plate at plate Z = 27.5 corresponds to tray Z = 36.0, while the slot center is at tray Z = 37.5. The rod must run at a slight angle. The 5 mm Z slot opening (tray Z = 35..40) accommodates the rod (4 mm) at tray Z = 37.5 center with 0.5 mm clearance each side. The rod entering the slot at approximately tray Z = 36.5 to 37.5 (accounting for the angle) is within the slot opening. This works.

**Attachment feature geometry:** The concept document specifies printed hooks or slots on the plate edges. The specific hook/slot design is a parts specification concern (Step 4b), but the spatial position of the attachment center is:

| Attachment | Plate X (mm) | Plate Z (mm) | Feature type |
|------------|-------------|-------------|--------------|
| Left rod | 0 (left edge) | 27.5 | Hook or slot, opening facing -X |
| Right rod | 55 (right edge) | 27.5 | Hook or slot, opening facing +X |

The hook/slot must accept a 4 mm diameter rod and allow the rod to translate 1.5 mm along plate Y (the rod slides within the hook as the plate moves relative to the rod's anchor points).

### 3g. Plate Travel Range (Tray Frame)

| State | Plate user face (tray Y) | Plate dock face (tray Y) | Description |
|-------|--------------------------|--------------------------|-------------|
| At rest | 14.5 | 9.5 | User face touches extended collet tips |
| Full release (1.5 mm travel) | 16.0 | 11.0 | Collets compressed; tubes released |
| Hard stop (2.0 mm travel) | 16.5 | 11.5 | Over-travel limit |

Gap between rear wall interior (tray Y = 8.5) and plate dock face:
- At rest: 9.5 - 8.5 = 1.0 mm
- At full release: 11.0 - 8.5 = 2.5 mm
- At hard stop: 11.5 - 8.5 = 3.0 mm

The hard stop is provided by the collet internal bottoming mechanism, not by a printed feature on the plate or tray. The guide posts span from tray Y = 8.5 (rear wall interior face) to tray Y = 22.0 (per Sub-D; 13.5 mm post length), passing through the plate throughout its travel range. At the rest position, the plate dock face is at tray Y = 9.5, and the post bases are at tray Y = 8.5. The posts extend through the plate and beyond (to tray Y = 22.0), maintaining full bearing engagement at all positions.

### 3h. Plate Dimensions Summary (Plate Frame)

| Dimension | Value (mm) |
|-----------|-----------|
| Width (plate X) | 55.0 |
| Thickness (plate Y) | 5.0 |
| Height (plate Z) | 55.0 |

---

## 4. Interface Positions

All interfaces specified from both the release plate side and the mating part side.

### Interface 1: Guide Post Bores to Guide Posts (Sub-E)

**Release plate side (plate frame):**

| Bore | Plate X (mm) | Plate Z (mm) | Bore diameter (mm) |
|------|-------------|-------------|-------------------|
| G1 | 5.5 | 6.0 | 3.8 |
| G2 | 49.5 | 6.0 | 3.8 |
| G3 | 5.5 | 49.0 | 3.8 |
| G4 | 49.5 | 49.0 | 3.8 |

Bore depth: 5.0 mm (through-hole, full plate thickness).
Bore axis: along plate Y.

**Mating part side (tray frame, Sub-E guide posts):**

| Post | Tray X (mm) | Tray Z (mm) | Post diameter (mm) | Post Y range (mm) |
|------|------------|------------|-------------------|--------------------|
| P1 | 58.0 | 14.5 | 3.5 | 8.5 to 22.0 |
| P2 | 102.0 | 14.5 | 3.5 | 8.5 to 22.0 |
| P3 | 58.0 | 57.5 | 3.5 | 8.5 to 22.0 |
| P4 | 102.0 | 57.5 | 3.5 | 8.5 to 22.0 |

**Fit type:** Sliding clearance, 0.15 mm per side (0.30 mm diametral).

**Coaxiality verification:**
- G1 plate (5.5, 6.0) -> tray (5.5 + 52.5, 6.0 + 8.5) = tray (58.0, 14.5). Matches P1. Correct.
- G2 plate (49.5, 6.0) -> tray (49.5 + 52.5, 6.0 + 8.5) = tray (102.0, 14.5). Matches P2. Correct.
- G3 plate (5.5, 49.0) -> tray (5.5 + 52.5, 49.0 + 8.5) = tray (58.0, 57.5). Matches P3. Correct.
- G4 plate (49.5, 49.0) -> tray (49.5 + 52.5, 49.0 + 8.5) = tray (102.0, 57.5). Matches P4. Correct.

### Interface 2: Stepped Bores to John Guest Fitting Collets (Sub-D)

**Release plate side (plate frame):**

| Bore | Plate X (mm) | Plate Z (mm) | Through-hole dia (mm) | Collet bore dia (mm) | Clearance bore dia (mm) |
|------|-------------|-------------|----------------------|---------------------|------------------------|
| B1 | 17.5 | 17.5 | 6.5 | 9.8 | 15.5 |
| B2 | 37.5 | 17.5 | 6.5 | 9.8 | 15.5 |
| B3 | 17.5 | 37.5 | 6.5 | 9.8 | 15.5 |
| B4 | 37.5 | 37.5 | 6.5 | 9.8 | 15.5 |

Bore step profile along plate Y (from user face to dock face):
- Y = 0 to 1.0: 15.5 mm dia (body end clearance)
- Y = 1.0 to 3.0: 9.8 mm dia (collet engagement)
- Y = 3.0 to 5.0: 6.5 mm dia (tube clearance, through)

**Mating part side (tray frame, fitting collets from Sub-D spatial):**

| Fitting | Tray X (mm) | Tray Z (mm) | Collet OD (mm) | Collet tip at rest (tray Y, mm) | Body end face (tray Y, mm) |
|---------|------------|------------|----------------|---------------------------------|----------------------------|
| F1 | 70.0 | 26.0 | 9.57 | 14.5 | 15.9 |
| F2 | 90.0 | 26.0 | 9.57 | 14.5 | 15.9 |
| F3 | 70.0 | 46.0 | 9.57 | 14.5 | 15.9 |
| F4 | 90.0 | 46.0 | 9.57 | 14.5 | 15.9 |

**Coaxiality verification:**
- B1 plate (17.5, 17.5) -> tray (17.5 + 52.5, 17.5 + 8.5) = tray (70.0, 26.0). Matches F1. Correct.
- B2 plate (37.5, 17.5) -> tray (37.5 + 52.5, 17.5 + 8.5) = tray (90.0, 26.0). Matches F2. Correct.
- B3 plate (17.5, 37.5) -> tray (17.5 + 52.5, 37.5 + 8.5) = tray (70.0, 46.0). Matches F3. Correct.
- B4 plate (37.5, 37.5) -> tray (37.5 + 52.5, 37.5 + 8.5) = tray (90.0, 46.0). Matches F4. Correct.

### Interface 3: Linkage Rod Attachments to Linkage Rods (passing through Sub-G slots)

**Release plate side (plate frame):**

| Attachment | Plate X (mm) | Plate Z (mm) | Rod diameter (mm) |
|------------|-------------|-------------|-------------------|
| Left | 0 (left edge) | 27.5 | 4.0 |
| Right | 55.0 (right edge) | 27.5 | 4.0 |

**Mating part side (tray frame, Sub-G linkage slots):**

| Slot | Tray X range (mm) | Tray Y range (mm) | Tray Z range (mm) |
|------|-------------------|-------------------|--------------------|
| Left wall | 0 to 5 | 17.0 to 23.0 | 35.0 to 40.0 |
| Right wall | 155 to 160 | 17.0 to 23.0 | 35.0 to 40.0 |

**Alignment check (left rod):**
- Rod exits plate at tray (52.5, 12.0, 36.0) at rest.
- Rod must reach slot at tray X = 0..5, tray Y = 17..23, tray Z = 35..40.
- The rod runs from tray X = 52.5 toward tray X = 0 (toward the left wall).
- At the slot, the rod center should be at approximately tray Y = 20.0 and tray Z = 37.5 (slot center).
- The rod attachment on the plate is at tray Y = 12.0 (at rest) and the slot Y center is at 20.0. The rod runs roughly from (52.5, 12.0, 36.0) to (2.5, 20.0, 37.5), so it angles both in Y and Z.
- The rod is a rigid straight rod, so these positions define its orientation. The rod length from plate edge to slot center is approximately sqrt(50^2 + 8^2 + 1.5^2) = sqrt(2500 + 64 + 2.25) = 50.7 mm.
- When the plate moves 1.5 mm in +Y (to tray Y = 13.5), the plate end of the rod moves to tray Y = 13.5. The rod pivots slightly at the slot, with the slot accommodating the angular change.

**Alignment check (right rod):** Symmetric. Rod exits plate at tray (107.5, 12.0, 36.0), reaches slot at tray X = 155..160, same Y and Z.

### Interface 4: Plate Dock Face to Rear Wall Interior (clearance)

**Release plate side (plate frame):** Dock face = plate Y = 5 (entire 55 x 55 mm face).

**Mating part side (tray frame):** Rear wall interior face at tray Y = 8.5.

**Clearance:** 1.0 mm at rest (tray Y = 9.5 plate dock face, tray Y = 8.5 wall face). No contact during normal operation. The gap increases to 2.5 mm at full release and 3.0 mm at hard stop.

---

## 5. Transform Summary

```
Plate frame -> Tray frame (at rest, plate user face at tray Y = 14.5):
  tray_X = plate_X + 52.5
  tray_Y = 14.5 - plate_Y
  tray_Z = plate_Z + 8.5

Plate frame -> Tray frame (at full release, 1.5 mm travel):
  tray_X = plate_X + 52.5
  tray_Y = 16.0 - plate_Y
  tray_Z = plate_Z + 8.5

General form (with travel t along +Y tray, 0 <= t <= 2.0):
  tray_X = plate_X + 52.5
  tray_Y = (14.5 + t) - plate_Y
  tray_Z = plate_Z + 8.5

Inverse (tray frame -> plate frame, at rest):
  plate_X = tray_X - 52.5
  plate_Y = 14.5 - tray_Y
  plate_Z = tray_Z - 8.5
```

### Verification (3 test points + 2 interface points)

**Test point 1: Plate origin (0, 0, 0)**
- Tray frame: (0 + 52.5, 14.5 - 0, 0 + 8.5) = (52.5, 14.5, 8.5)
- This is the lower-left-front corner of the plate, user-facing side. Tray X = 52.5 is the plate left edge, tray Y = 14.5 is the user-facing face at rest, tray Z = 8.5 is the plate bottom edge.
- Inverse: (52.5 - 52.5, 14.5 - 14.5, 8.5 - 8.5) = (0, 0, 0). Round trip correct.

**Test point 2: Plate corner (55, 5, 55)**
- Tray frame: (55 + 52.5, 14.5 - 5, 55 + 8.5) = (107.5, 9.5, 63.5)
- This is the upper-right-rear corner of the plate, dock-facing side. Tray X = 107.5 is plate right edge, tray Y = 9.5 is the dock face at rest, tray Z = 63.5 is the plate top edge.
- Inverse: (107.5 - 52.5, 14.5 - 9.5, 63.5 - 8.5) = (55, 5, 55). Round trip correct.

**Test point 3: Bore B1 center, user face (17.5, 0, 17.5)**
- Tray frame: (17.5 + 52.5, 14.5 - 0, 17.5 + 8.5) = (70.0, 14.5, 26.0)
- This should be coaxial with fitting F1 at tray (70, *, 26). X and Z match. Tray Y = 14.5 is the collet tip position. Correct.

**Interface point: Guide bore G4 center (49.5, 2.5, 49.0)**
- Tray frame: (49.5 + 52.5, 14.5 - 2.5, 49.0 + 8.5) = (102.0, 12.0, 57.5)
- Post P4 is at tray (102.0, *, 57.5). X and Z match. Tray Y = 12.0 is the mid-thickness of the plate at rest, which is within the post Y range (8.5 to 22.0). Correct.

**Interface point at full travel: Bore B1 center, user face (17.5, 0, 17.5) at t = 1.5**
- Tray frame: (70.0, 16.0, 26.0)
- The collet has been pushed from tray Y = 14.5 to 16.0, compressing it 1.5 mm. The collet travel is 1.3 mm (from extended to compressed), so at 1.5 mm plate travel the collet is at its compressed limit plus 0.2 mm margin. Consistent with the design intent.

---

## 6. Key Dimensions Summary Table

All values in the plate's local reference frame unless noted otherwise.

| Parameter | Value | Frame | Source |
|-----------|-------|-------|--------|
| Plate width (X) | 55.0 mm | Plate | Concept doc; verified fits guide posts + bores |
| Plate thickness (Y) | 5.0 mm | Plate | Collet release research |
| Plate height (Z) | 55.0 mm | Plate | Concept doc; verified fits guide posts + bores |
| Stepped bore B1 center (X, Z) | (17.5, 17.5) | Plate | Transform from tray (70, 26) |
| Stepped bore B2 center (X, Z) | (37.5, 17.5) | Plate | Transform from tray (90, 26) |
| Stepped bore B3 center (X, Z) | (17.5, 37.5) | Plate | Transform from tray (70, 46) |
| Stepped bore B4 center (X, Z) | (37.5, 37.5) | Plate | Transform from tray (90, 46) |
| Bore center-to-center spacing | 20.0 mm (X and Z) | Plate | Sub-D spatial |
| Through-hole diameter | 6.5 mm | Plate | Collet release research |
| Through-hole Y range | 0 to 5.0 (full thickness) | Plate | -- |
| Collet engagement bore diameter | 9.8 mm | Plate | Collet release research |
| Collet engagement bore Y range | 1.0 to 3.0 | Plate | Cut from user face |
| Body end clearance bore diameter | 15.5 mm | Plate | Collet release research |
| Body end clearance bore Y range | 0 to 1.0 | Plate | Cut from user face |
| Guide bore G1 center (X, Z) | (5.5, 6.0) | Plate | Transform from tray (58, 14.5) |
| Guide bore G2 center (X, Z) | (49.5, 6.0) | Plate | Transform from tray (102, 14.5) |
| Guide bore G3 center (X, Z) | (5.5, 49.0) | Plate | Transform from tray (58, 57.5) |
| Guide bore G4 center (X, Z) | (49.5, 49.0) | Plate | Transform from tray (102, 57.5) |
| Guide bore diameter | 3.8 mm | Plate | Sub-E spec; 0.15 mm clearance on 3.5 mm posts |
| Guide bore Y range | 0 to 5.0 (through-hole) | Plate | -- |
| Left linkage attachment (X, Z) | (0, 27.5) | Plate | Plate mid-height, left edge |
| Right linkage attachment (X, Z) | (55, 27.5) | Plate | Plate mid-height, right edge |
| Linkage rod diameter | 4.0 mm | -- | Concept doc |
| Plate XZ position origin in tray frame | (52.5, 8.5) | Tray | Centered on fitting grid |
| Plate Y at rest (user face) | 14.5 | Tray | Sub-D: collet tip contact |
| Plate Y at rest (dock face) | 9.5 | Tray | 14.5 - 5.0 |
| Travel distance | 1.5 mm along +Y tray | Tray | Collet release research |
| Hard stop travel | 2.0 mm along +Y tray | Tray | Over-travel protection |
| Gap to rear wall at rest | 1.0 mm | Tray | 9.5 - 8.5 |
