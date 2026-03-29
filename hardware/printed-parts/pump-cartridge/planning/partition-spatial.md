# Mounting Partition -- Spatial Resolution

All coordinates are in the **partition local frame** unless explicitly stated otherwise. Every dimension is a concrete number. No downstream trigonometry or coordinate transforms are required.

---

## 1. System-Level Placement

```
Mechanism: Pump cartridge
Part: Mounting partition
Parent: Bottom shell + top shell interior
Position: vertical plate in the XZ plane of the cartridge, at the junction
          between the pump head zone and the motor zone.
          In the bottom shell frame: Y = 72.3 to Y = 77.7 (center Y = 75.0).
          Spans full interior width (X = 0 to X = 132 including tab engagement
          in side wall slots).
          Spans full interior height (Z = 2.0 in bottom shell to Z = 65.0 in
          full cartridge frame, i.e., 63 mm tall).
Orientation: no rotation relative to the cartridge frame -- partition X aligns
             with cartridge X, partition Z aligns with cartridge Z.
```

This section is context only. All geometry below is resolved in the partition's own local frame.

---

## 2. Part Reference Frame

```
Part: Mounting partition
  Origin: bottom-left corner of the plate as printed flat on the build plate
  X: width (left to right when viewed from the front of the cartridge), 0..132.0 mm
  Y: thickness (plate through-thickness), 0..5.0 mm
  Z: height (bottom to top), 0..63.0 mm
  Print orientation: flat on build plate, lying on the XZ face (large face down)
  Installed orientation: X maps to cartridge X, Y maps to cartridge Y
    (centered at cartridge Y = 75.0), Z maps to cartridge Z (partition Z = 0
    corresponds to cartridge interior floor at Z = 2.0)
```

Conventions:
- Partition X = 0 corresponds to the left exterior face of the cartridge (bottom shell X = 0). The left tab occupies X = 0 to X = 2.0. The main plate body spans X = 2.0 to X = 130.0 (128 mm). The right tab occupies X = 130.0 to X = 132.0.
- Partition Y = 0 is the forward face of the plate (facing the pump heads). Partition Y = 5.0 is the rearward face (facing the motors).
- Partition Z = 0 is the bottom edge (corresponding to bottom shell floor interior at Z = 2.0). Partition Z = 63.0 is the top edge (corresponding to top shell ceiling interior at Z = 65.0 in full cartridge frame).

---

## 3. Derived Geometry

### 3a. Plate Body Envelope

| Parameter | Value |
|-----------|-------|
| Total width (X) | 132.0 mm (including tabs engaging side wall slots) |
| Main body width (X) | 128.0 mm (X = 2.0 to X = 130.0, spanning cartridge interior) |
| Thickness (Y) | 5.0 mm |
| Height (Z) | 63.0 mm (from floor interior to ceiling interior) |
| Material | PETG |

### 3b. Side Wall Tab Geometry

The partition's left and right edges sit in vertical slots in the side walls. The tabs are the portions of the plate that extend into these slots.

**Left tab:**

| Parameter | Value |
|-----------|-------|
| X range | X = 0 to X = 2.0 |
| Y range | Y = 0 to Y = 5.0 (full thickness) |
| Z range | Z = 0 to Z = 63.0 (full height) |
| Tab depth (X, into wall) | 2.0 mm |
| Mating feature | Bottom shell left wall slot: shell X = 0..2.0, shell Y = 72.3..77.7, shell Z = 2.0..33.5; top shell has matching slot for Z = 33.5..65.0 |

**Right tab:**

| Parameter | Value |
|-----------|-------|
| X range | X = 130.0 to X = 132.0 |
| Y range | Y = 0 to Y = 5.0 (full thickness) |
| Z range | Z = 0 to Z = 63.0 (full height) |
| Tab depth (X, into wall) | 2.0 mm |
| Mating feature | Bottom shell right wall slot: shell X = 130.0..132.0, shell Y = 72.3..77.7, shell Z = 2.0..33.5; top shell has matching slot for Z = 33.5..65.0 |

**Clearance check:** The side wall slots are 5.4 mm wide in the Y direction (shell Y = 72.3 to 77.7). The partition is 5.0 mm thick (Y = 0 to 5.0). Clearance per side: (5.4 - 5.0) / 2 = 0.2 mm. This is the specified sliding fit for easy insertion.

### 3c. Motor Bore Positions

Each motor bore allows the motor body (~35 mm diameter) to pass through the partition. The bore centers align with the pump center axes.

**Pump center axes in bottom shell frame:** Left pump at (X = 33.5, Z = 33.3), Right pump at (X = 98.5, Z = 33.3).

**Converting to partition frame:** Partition X = bottom shell X (no offset). Partition Z = bottom shell Z - 2.0 (partition Z = 0 corresponds to bottom shell Z = 2.0).

| Bore | Partition X center | Partition Z center | Derivation |
|------|-------------------|-------------------|------------|
| Left motor bore | 33.5 | 31.3 | shell X = 33.5; shell Z = 33.3, partition Z = 33.3 - 2.0 = 31.3 |
| Right motor bore | 98.5 | 31.3 | shell X = 98.5; shell Z = 33.3, partition Z = 33.3 - 2.0 = 31.3 |

**Bore diameter derivation:** Motor body diameter is approximately 35 mm (low confidence, caliper photos 15/16 show 34.54-35.13 mm). The motor also has a flat on one side (standard anti-rotation feature). To clear the motor body including the flat and any manufacturing variation:

| Parameter | Value |
|-----------|-------|
| Motor body diameter (worst case) | 35.2 mm |
| Diametral clearance | 1.0 mm (0.5 mm per side) |
| Motor bore diameter (as-designed) | 36.2 mm |
| FDM hole compensation | +0.2 mm (holes print smaller) |
| Motor bore diameter (as-drawn) | 36.4 mm |

The 36.4 mm as-drawn bore provides approximately 36.2 mm as-printed, giving 0.5 mm radial clearance on the 35.2 mm worst-case motor body. This clearance accommodates the motor flat and minor alignment variation.

**Y position:** Each bore runs through the full plate thickness (Y = 0 to Y = 5.0). The bore axis is at the X, Z center position specified above.

### 3d. M3 Through-Hole Positions

Eight M3 through-holes in two 48 mm square patterns, one pattern per pump. Each pattern is centered on its respective pump center axis.

**Mounting hole pattern:** 48 mm center-to-center square. Four holes per pump at the corners of a 48 mm x 48 mm square centered on the motor bore center.

**Offset from bore center to each hole:** +/-24 mm in X and +/-24 mm in Z.

**Left pump M3 holes (centered on X = 33.5, Z = 31.3):**

| Hole | Partition X | Partition Z | Derivation |
|------|------------|------------|------------|
| L1 (bottom-left) | 9.5 | 7.3 | 33.5 - 24.0, 31.3 - 24.0 |
| L2 (bottom-right) | 57.5 | 7.3 | 33.5 + 24.0, 31.3 - 24.0 |
| L3 (top-left) | 9.5 | 55.3 | 33.5 - 24.0, 31.3 + 24.0 |
| L4 (top-right) | 57.5 | 55.3 | 33.5 + 24.0, 31.3 + 24.0 |

**Right pump M3 holes (centered on X = 98.5, Z = 31.3):**

| Hole | Partition X | Partition Z | Derivation |
|------|------------|------------|------------|
| R1 (bottom-left) | 74.5 | 7.3 | 98.5 - 24.0, 31.3 - 24.0 |
| R2 (bottom-right) | 122.5 | 7.3 | 98.5 + 24.0, 31.3 - 24.0 |
| R3 (top-left) | 74.5 | 55.3 | 98.5 - 24.0, 31.3 + 24.0 |
| R4 (top-right) | 122.5 | 55.3 | 98.5 + 24.0, 31.3 + 24.0 |

**Clearance check -- holes within plate body:**

| Hole | X | Z | Distance to nearest plate edge | OK? |
|------|---|---|-------------------------------|-----|
| L1 | 9.5 | 7.3 | X: 9.5 - 2.0 = 7.5 mm from left body edge; Z: 7.3 mm from bottom | Yes |
| L2 | 57.5 | 7.3 | X: 65.0 - 57.5 = 7.5 mm from center divider plane; Z: 7.3 mm | Yes |
| L3 | 9.5 | 55.3 | X: 7.5 mm; Z: 63.0 - 55.3 = 7.7 mm from top | Yes |
| L4 | 57.5 | 55.3 | X: 7.5 mm from center; Z: 7.7 mm from top | Yes |
| R1 | 74.5 | 7.3 | X: 74.5 - 67.0 = 7.5 mm from center divider plane; Z: 7.3 mm | Yes |
| R2 | 122.5 | 7.3 | X: 130.0 - 122.5 = 7.5 mm from right body edge; Z: 7.3 mm | Yes |
| R3 | 74.5 | 55.3 | X: 7.5 mm; Z: 7.7 mm | Yes |
| R4 | 122.5 | 55.3 | X: 7.5 mm; Z: 7.7 mm | Yes |

All holes have at least 7.3 mm from the nearest edge. With a 3.4 mm hole diameter (see below), the minimum wall from hole edge to plate edge is 7.3 - 1.7 = 5.6 mm. Adequate.

**M3 hole diameter:** The pump bracket holes are 3.13 mm diameter. The vibration isolation mounts have M3 male studs on both ends. One stud threads into the pump bracket; the other passes through the partition. The partition holes should be M3 clearance holes.

| Parameter | Value |
|-----------|-------|
| M3 nominal diameter | 3.0 mm |
| Clearance hole diameter (as-designed) | 3.4 mm |
| FDM compensation | +0.2 mm |
| As-drawn diameter | 3.6 mm |
| As-printed expected | ~3.4 mm |

**Y position:** Each hole runs through the full plate thickness (Y = 0 to Y = 5.0).

### 3e. Linkage Arm Pass-Through Notch Positions

Two rectangular notches at the bottom corners of the partition allow the linkage arms to pass through.

**Linkage arm channel positions in bottom shell frame:**
- Left channel interior: X = 2.0 to 9.0, Z = 2.0 to 5.0
- Right channel interior: X = 123.0 to 130.0, Z = 2.0 to 5.0

The partition sits at the boundary between the pump head zone and the motor zone. The linkage arms run through this boundary within their guide channels. The notches must clear the arm cross-section (6 mm wide x 3 mm tall) plus clearance.

**Converting to partition frame:**

| Notch | Partition X range | Partition Z range | Derivation |
|-------|------------------|------------------|------------|
| Left notch | X = 2.0 to X = 10.0 (8 mm wide) | Z = 0 to Z = 4.0 (4 mm tall from bottom edge) | Shell X = 2.0..10.0 (channel 2.0..9.0 + 1mm margin); shell Z = 2.0..6.0, partition Z = 0..4.0 |
| Right notch | X = 122.0 to X = 130.0 (8 mm wide) | Z = 0 to Z = 4.0 | Shell X = 122.0..130.0 (channel 123.0..130.0 + 1mm margin left); shell Z = 2.0..6.0, partition Z = 0..4.0 |

**Clearance check:** The arm is 6 mm wide x 3 mm tall. The notch is 8 mm wide x 4 mm tall. Clearance: 1 mm per side in X (8 - 6 = 2, split), 1 mm above the arm in Z (4 - 3 = 1). This matches the concept specification of "8mm x 5mm notches" in the concept document. Adjusting to match concept:

**Revised per concept (8 mm wide x 5 mm tall):**

| Notch | Partition X range | Partition Z range | Width | Height |
|-------|------------------|------------------|-------|--------|
| Left notch | X = 2.0 to X = 10.0 | Z = 0 to Z = 5.0 | 8.0 mm | 5.0 mm |
| Right notch | X = 122.0 to X = 130.0 | Z = 0 to Z = 5.0 | 8.0 mm | 5.0 mm |

Clearance: 1 mm per side in X on the 6 mm arm; 2 mm above the 3 mm arm in Z. The extra Z clearance allows the arm to ride slightly above the floor if needed and accommodates the guide rib tops (Z = 5.0 in bottom shell = partition Z = 3.0) -- the notch extends to partition Z = 5.0, fully clearing the rib height.

### 3f. Registration Tab Positions (Y-Direction Protrusions)

**Note: Revised during parts specification (Rubric G printability review).** The original concept described Z-direction tabs (projecting downward from the bottom edge and upward from the top edge). These are not printable in the flat orientation -- the bottom tabs would project below the build plate. The tabs are instead Y-direction protrusions (projecting rearward from the motor-side face at the bottom and top zones of the plate). This maintains the registration function while being fully printable with no supports.

The tabs provide positive Y-axis location (preventing fore-aft sliding within the 0.2 mm clearance of the side wall slots) and additional constraint against rotation about the Y axis.

**Bottom registration tabs (project in +Y from the rearward face, at the bottom zone):**

| Tab | X extent | Y extent | Z extent | Mating feature |
|-----|----------|----------|----------|----------------|
| Bottom-left | X = 9.0 to X = 11.0 (2 mm wide) | Y = 5.0 to Y = 7.0 (2 mm protrusion past rearward face) | Z = 0 to Z = 2.0 (bottom 2 mm of plate) | Notch in bottom shell cavity wall behind partition slot: shell X = 8.8..11.2, Y = 77.7..79.7, Z = 2.0..4.0 |
| Bottom-right | X = 121.0 to X = 123.0 | Y = 5.0 to Y = 7.0 | Z = 0 to Z = 2.0 | Notch: shell X = 120.8..123.2, Y = 77.7..79.7, Z = 2.0..4.0 |

**Top registration tabs (project in +Y from the rearward face, at the top zone):**

| Tab | X extent | Y extent | Z extent | Mating feature |
|-----|----------|----------|----------|----------------|
| Top-left | X = 9.0 to X = 11.0 | Y = 5.0 to Y = 7.0 | Z = 61.0 to Z = 63.0 (top 2 mm of plate) | Notch in top shell cavity wall behind partition slot |
| Top-right | X = 121.0 to X = 123.0 | Y = 5.0 to Y = 7.0 | Z = 61.0 to Z = 63.0 | Notch in top shell cavity wall |

Tab positions are placed inboard of the linkage arm notches to avoid interfering with the notch geometry.

**Note:** The bottom shell parts spec must be updated to add notches at the positions listed above. The top shell spec (when created) must include matching notches.

---

## 4. Interface Summary

### 4.1. Bottom shell side wall slots (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Bottom shell (left and right side walls) |
| Interface type | Partition left/right edge tabs sitting in vertical wall slots |
| Partition feature | Left edge: X = 0..2.0, full Y, full Z. Right edge: X = 130.0..132.0, full Y, full Z. |
| Bottom shell feature | Left slot: shell X = 0..2.0, Y = 72.3..77.7, Z = 2.0..33.5. Right slot: shell X = 130.0..132.0, Y = 72.3..77.7, Z = 2.0..33.5. |
| Clearance | 0.2 mm per side in Y (slot width 5.4 mm, partition thickness 5.0 mm) |

### 4.2. Top shell side wall slots (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Top shell (left and right side walls) |
| Interface type | Continuation of side wall slot engagement above parting line |
| Partition feature | Same left/right edges, Z = 31.5..63.0 (partition Z corresponding to above bottom shell parting line) |
| Top shell feature | Matching slots in top shell side walls at same Y position |

### 4.3. Bottom shell registration notches (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Bottom shell cavity wall (behind partition slot) |
| Interface type | Y-direction registration tabs engaging notches behind partition slot |
| Partition feature | Bottom-left tab: X = 9..11, Y = 5..7, Z = 0..2. Bottom-right tab: X = 121..123, Y = 5..7, Z = 0..2. |
| Bottom shell feature | Notches at shell X = 8.8..11.2, Y = 77.7..79.7, Z = 2.0..4.0 (left) and X = 120.8..123.2 (right) |
| Clearance | Tabs are 2.0 mm wide (X); notches are 2.4 mm wide (0.2 mm clearance per side) |

### 4.4. Top shell registration notches (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Top shell cavity wall (behind partition slot) |
| Interface type | Y-direction registration tabs engaging notches behind partition slot |
| Partition feature | Top-left tab: X = 9..11, Y = 5..7, Z = 61..63. Top-right tab: X = 121..123, Y = 5..7, Z = 61..63. |
| Top shell feature | Notches at matching positions in top shell |
| Clearance | Same as bottom shell notches (0.2 mm per side) |

### 4.5. Pumps via vibration isolation mounts (x2 pumps, 4 mounts each)

| Parameter | Value |
|-----------|-------|
| Mating part | Kamoer KPHM400 pumps + M3 rubber vibration isolation mounts |
| Interface type | M3 stud from isolation mount passes through partition clearance hole; nut or self-threading on the pump head side |
| Partition features | 8 M3 clearance holes (Section 3d): left pump at (9.5, 7.3), (57.5, 7.3), (9.5, 55.3), (57.5, 55.3); right pump at (74.5, 7.3), (122.5, 7.3), (74.5, 55.3), (122.5, 55.3) |
| Motor bore features | Left bore: center (33.5, 31.3), dia 36.4 mm as-drawn. Right bore: center (98.5, 31.3), dia 36.4 mm as-drawn. |
| Mounting side | Motor side of partition (Y = 5.0 face). Pump brackets sit against this face with motor bodies passing through bores. |

### 4.6. Linkage arms (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Linkage arms (left and right) |
| Interface type | Pass-through notch (no contact, clearance only) |
| Partition features | Left notch: X = 2..10, Z = 0..5. Right notch: X = 122..130, Z = 0..5. |
| Arm cross-section | 6 mm W x 3 mm H |
| Clearance | 1 mm per side in X, 2 mm above arm in Z |

---

## 5. Transform Summary

The partition is a vertical plate that installs with no rotation relative to the cartridge frame. The transform is a pure translation.

```
Partition frame -> Bottom shell frame:
  Translation: (0, +72.3, +2.0)
  Rotation: identity (none)
  Meaning: partition X = shell X, partition Y + 72.3 = shell Y, partition Z + 2.0 = shell Z

Bottom shell frame -> Partition frame:
  Translation: (0, -72.3, -2.0)
  Rotation: identity
```

**Verification (3 test points):**

| Point | Partition frame (X, Y, Z) | Bottom shell frame (X, Y, Z) | Round-trip | Match? |
|-------|--------------------------|------------------------------|------------|--------|
| Origin (bottom-left-front corner) | (0, 0, 0) | (0, 72.3, 2.0) | (0, 0, 0) | Yes |
| Left motor bore center | (33.5, 2.5, 31.3) | (33.5, 74.8, 33.3) | (33.5, 2.5, 31.3) | Yes |
| Right notch corner (bottom-right of notch) | (130.0, 0, 0) | (130.0, 72.3, 2.0) | (130.0, 0, 0) | Yes |

**Cross-check: pump axis in bottom shell frame.**
Left pump center axis: shell (33.5, -, 33.3). Via partition transform: partition (33.5, -, 33.3 - 2.0) = partition (33.5, -, 31.3). Matches Section 3c. Verified.

**Cross-check: M3 hole L1 in bottom shell frame.**
Partition (9.5, -, 7.3) -> shell (9.5, -, 7.3 + 2.0) = shell (9.5, -, 9.3). The pump mounting pattern centered at shell Z = 33.3, bottom hole at 33.3 - 24.0 = 9.3. Verified.
