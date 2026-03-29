# Floor Plate -- Spatial Resolution

## 1. System-Level Placement

```
Mechanism: Floor Plate (removable bottom panel)
Parent: Tray (Sub-A box shell), attached to underside of tray floor
Position: centered under the pump mounting zone, fastened to tray floor exterior (Z = 0 plane)
Orientation: level, aligned with tray frame (no rotation)
```

The floor plate is a flat rectangular panel that sits flush against the underside of the tray floor, covering a rectangular cutout in the pump zone. It is secured by 2x M3 screws threading into heat-set inserts in tray floor ribs that border the cutout. The plate provides an optional access path for installing pumps from below.

---

## 2. Part Reference Frame

```
Part: Floor Plate
  Origin: rear-left corner of the plate, top face
  X: width, 0..148 mm (left to right, parallel to tray X axis)
  Y: depth, 0..58 mm (rear to front, parallel to tray Y axis)
  Z: thickness, 0..-4 mm (0 at top face, -4 at bottom face; Z is negative downward from the top bearing surface)
  Print orientation: flat, top face (bearing surface) up, XY plane on build plate
  Installed orientation: top face contacts tray floor rib undersides at tray Z = 0
```

Note: The floor plate's local Z = 0 (top face) sits at tray Z = 0 (floor exterior). The plate extends downward from there. When installed, the plate's local +X aligns with tray +X, local +Y aligns with tray +Y.

---

## 3. Derived Geometry

### 3a. Pump Zone Footprint (Driving the Cutout Size)

The floor plate must provide access for installing both pump heads from below. The relevant pump geometry (all coordinates in tray frame):

| Parameter | Value (tray frame) | Source |
|-----------|-------------------|--------|
| Pump 1 head X range | 11.90 to 74.50 | Sub-C spatial: centerline 43.20, head width 62.6 |
| Pump 2 head X range | 85.50 to 148.10 | Sub-C spatial: centerline 116.80, head width 62.6 |
| Combined head X range | 11.90 to 148.10 (136.20 mm) | Both pumps |
| Pump head Y range | 35.00 to 83.00 (48.00 mm) | Sub-C spatial: tube face Y=35 to bracket plane Y=83 |
| Pump head cross-section | 62.6 x 62.6 mm square | Kamoer KPHM400 |

To pass a pump head through the floor opening, the cutout must be at least 62.6 mm in both X and Y. To accommodate both pumps side by side, the cutout must span the combined head X range (136.2 mm) plus clearance.

### 3b. Tray Floor Cutout (Feature on the Tray, Not on the Floor Plate)

The tray floor currently has no cutout or floor plate mounting provisions. This section defines the cutout geometry that the tray must incorporate if the floor plate option is used.

**Cutout rectangle (tray frame):**

| Parameter | Value (tray frame) | Derivation |
|-----------|-------------------|------------|
| X start | 10.00 mm | Pump 1 head left edge (11.90) minus 2 mm clearance, rounded down |
| X end | 150.00 mm | Pump 2 head right edge (148.10) plus 2 mm clearance, rounded up |
| Y start | 33.00 mm | Pump tube face (Y=35) minus 2 mm clearance |
| Y end | 85.00 mm | Bracket plane (Y=83) plus 2 mm clearance |
| X width | 140.00 mm | 150.00 - 10.00 |
| Y depth | 52.00 mm | 85.00 - 33.00 |

The cutout removes the full 3 mm floor thickness (tray Z = 0 to Z = 3) within the rectangle X = 10..150, Y = 33..85.

**Cutout clearance to tray walls:**
- Left wall interior (X = 5): cutout starts at X = 10, leaving a 5 mm floor rib
- Right wall interior (X = 155): cutout ends at X = 150, leaving a 5 mm floor rib
- Rear wall interior (Y = 8.5): cutout starts at Y = 33, leaving a 24.5 mm floor span
- Front edge (Y = 155): cutout ends at Y = 85, leaving a 70 mm floor span

All four floor ribs bordering the cutout are at least 5 mm wide -- adequate for structural integrity and for hosting heat-set inserts on the side ribs.

### 3c. Floor Plate Dimensions (Part-Local Frame)

The floor plate must overlap the cutout edges to bear against the tray floor ribs. A 4 mm overlap per edge provides adequate bearing surface for the M3 screw clamping force.

**Plate envelope (part-local frame):**

| Parameter | Value (part frame) | Derivation |
|-----------|-------------------|------------|
| X extent | 0 to 148.00 mm | Cutout width (140) + 2 x 4 mm overlap |
| Y extent | 0 to 60.00 mm | Cutout depth (52) + 2 x 4 mm overlap |
| Z extent | 0 to -4.00 mm | 4 mm thick plate (extending downward from top face) |

**Plate-to-tray position mapping:**

| Plate corner | Part-local (X, Y, Z) | Tray frame (X, Y, Z) |
|--------------|----------------------|----------------------|
| Rear-left, top face | (0, 0, 0) | (6.00, 29.00, 0) |
| Front-right, top face | (148, 60, 0) | (154.00, 89.00, 0) |
| Rear-left, bottom face | (0, 0, -4) | (6.00, 29.00, -4.00) |
| Front-right, bottom face | (148, 60, -4) | (154.00, 89.00, -4.00) |

The plate origin in tray frame is at (6.00, 29.00, 0). The plate is centered on the cutout with 4 mm overlap on each edge:
- Plate left edge: tray X = 10 - 4 = 6.00
- Plate right edge: tray X = 150 + 4 = 154.00
- Plate rear edge: tray Y = 33 - 4 = 29.00
- Plate front edge: tray Y = 85 + 4 = 89.00

### 3d. Screw Hole Positions

Two M3 counterbore through-holes, placed along the X centerline of the plate, spaced near each end for balanced clamping. The screws must land on the tray floor ribs (outside the cutout).

**Screw placement strategy:** The screws are on the left and right ribs (the 5 mm wide floor strips between the cutout edge and the wall interior). Each screw is centered on its rib in X and centered on the plate in Y.

**Screw hole positions (part-local frame):**

| Hole | Part X (mm) | Part Y (mm) | Tray X (mm) | Tray Y (mm) | Rib location |
|------|-------------|-------------|-------------|-------------|-------------|
| Hole 1 (left) | 6.50 | 30.00 | 12.50 | 59.00 | Left floor rib, X = 5..10 in tray, centered at X = 7.5; offset to 12.5 for insert clearance |
| Hole 2 (right) | 141.50 | 30.00 | 147.50 | 59.00 | Right floor rib, X = 150..155 in tray, centered at X = 152.5; offset to 147.5 for insert clearance |

**Derivation of screw X positions:**

The left floor rib spans tray X = 5..10 (between the wall interior and cutout edge). The rib is 5 mm wide. An M3 heat-set insert (4.0 mm pilot hole OD, ~5.4 mm knurled OD) needs at least 5 mm of surrounding material. The 5 mm rib width is tight for a centered insert -- the insert knurl (5.4 mm) would leave only ~0.3 mm of material on each side of a 5 mm wide rib.

**Revised strategy:** Place the heat-set inserts in thickened boss pads on the tray floor, just outside the cutout, rather than in the narrow ribs. Each boss pad is a local thickening (8 mm diameter circular pad, 3 mm tall, on the Z = 3 interior floor surface) that provides adequate material around the insert. The insert is bored from the Z = 0 exterior face up into the boss pad.

**Revised screw positions (centered on boss pads):**

| Hole | Part X (mm) | Part Y (mm) | Tray X (mm) | Tray Y (mm) | Notes |
|------|-------------|-------------|-------------|-------------|-------|
| Hole 1 (left) | 21.50 | 30.00 | 27.50 | 59.00 | On floor, Y centered on cutout, X = 27.5 (17.5 mm inboard from left cutout edge) |
| Hole 2 (right) | 126.50 | 30.00 | 132.50 | 59.00 | On floor, Y centered on cutout, X = 132.5 (17.5 mm inboard from right cutout edge) |

These positions place the screws on the solid floor area within the cutout zone but outside the pump head footprints:
- Hole 1 at tray (27.50, 59.00): between Pump 1 head left edge (X = 11.90) and Pump 1 boss P1-L (X = 18.48). This is within the Pump 1 head footprint (X = 11.90..74.50) -- the screw sits directly under the pump head where it will be hidden and the boss pad won't interfere with the flat pump head bottom.
- Hole 2 at tray (132.50, 59.00): symmetric position under Pump 2 head.

**Alternative: screws outside the cutout entirely.** The simplest approach places the M3 inserts in the solid floor ribs beyond the cutout edges but requires the plate overlap to extend far enough. With the ribs at 5 mm wide, there is not enough material for reliable inserts.

**Final screw position decision:** Place the insert boss pads on the tray interior floor (Z = 3 surface) at the Y centerline of the cutout, at X positions that avoid interference with pump bosses and cradles. The inserts are bored through the 3 mm floor thickness plus into the boss pad. The floor plate counterbore holes align from below.

**Final screw hole positions (part-local frame):**

| Hole | Part X (mm) | Part Y (mm) | Tray X (mm) | Tray Y (mm) |
|------|-------------|-------------|-------------|-------------|
| Hole 1 | 21.50 | 30.00 | 27.50 | 59.00 |
| Hole 2 | 126.50 | 30.00 | 132.50 | 59.00 |

**Hole geometry (part-local frame):**

| Feature | Dimension |
|---------|-----------|
| Through-hole diameter | 3.40 mm (M3 clearance, +0.2 mm per requirements.md) |
| Counterbore diameter | 5.70 mm (M3 SHCS head 5.5 mm + 0.2 mm clearance) |
| Counterbore depth | 3.20 mm (M3 SHCS head height 3.0 mm + 0.2 mm clearance, from bottom face) |
| Remaining plate thickness above counterbore | 4.00 - 3.20 = 0.80 mm (thin bearing ring around through-hole) |

The counterbore is on the bottom face (plate Z = -4 side, the face visible from below). The screw enters from below, passes through the counterbore and clearance hole, and threads into the heat-set insert in the tray floor.

### 3e. Bearing Surface Contact

The floor plate's top face (part Z = 0) contacts the underside of the tray floor ribs at tray Z = 0. The bearing contact occurs only on the 4 mm overlap strips around the cutout perimeter:

**Bearing strips (part-local frame):**

| Strip | Part X range | Part Y range | Width (mm) | Tray location |
|-------|-------------|-------------|------------|---------------|
| Left | 0..4 | 0..60 | 4.0 | Tray X = 6..10, against left floor rib |
| Right | 144..148 | 0..60 | 4.0 | Tray X = 150..154, against right floor rib |
| Rear | 4..144 | 0..4 | 4.0 | Tray Y = 29..33, against rear floor rib |
| Front | 4..144 | 56..60 | 4.0 | Tray Y = 85..89, against front floor rib |

Total bearing perimeter: ~400 mm of 4 mm wide strips. Adequate for distributing the clamping load from 2x M3 screws.

### 3f. Boss Pad Interference Check

The screw boss pads on the tray interior floor must not interfere with pump bosses (Sub-C) or motor cradles.

| Feature | Tray position | Distance to Hole 1 (27.50, 59.00) | Distance to Hole 2 (132.50, 59.00) |
|---------|-------------|-----------------------------------|-------------------------------------|
| Boss P1-L | (18.48, 83.00) | 25.7 mm | -- |
| Boss P1-R | (67.93, 83.00) | -- | -- |
| Boss P2-L | (92.08, 83.00) | -- | -- |
| Boss P2-R | (141.53, 83.00) | -- | 25.3 mm |
| Cradle 1 footprint | X: 22.45..63.95, Y: 109..124 | >50 mm | -- |
| Cradle 2 footprint | X: 96.05..137.55, Y: 109..124 | -- | >50 mm |

Closest approach is Boss P1-L at 25.7 mm from Hole 1 and Boss P2-R at 25.3 mm from Hole 2. An 8 mm diameter boss pad has a 4 mm radius -- ample clearance. No interference.

### 3g. Size Revision Note

The conceptual architecture estimated the floor plate at ~80 x 60 x 4 mm. The spatial resolution yields 148 x 60 x 4 mm. The X dimension is significantly larger because both pump heads together span 136.2 mm across the tray width, and the plate must span the full cutout (140 mm) plus overlap (8 mm). The 60 mm Y dimension matches the concept estimate. The 4 mm thickness matches the concept.

---

## 4. Interface Specifications

### 4a. Floor Plate Top Face to Tray Floor Ribs

| Parameter | Floor Plate (this part) | Tray (Sub-A) |
|-----------|------------------------|--------------|
| Contact surface | Part Z = 0 (top face), 4 mm perimeter strips | Tray Z = 0 (floor exterior), rib undersides bordering the cutout |
| Contact area | ~400 mm perimeter x 4 mm width = ~1,600 mm^2 | Same area on tray side |
| Alignment | Plate drops into position from below; cutout edges center it in X and Y | Cutout rectangle acts as a loose location feature (plate is 8 mm wider and 8 mm deeper than cutout) |

### 4b. M3 Screw Holes to Tray Floor Heat-Set Inserts

| Parameter | Floor Plate (this part) | Tray (Sub-A, with boss pads) |
|-----------|------------------------|------------------------------|
| Hole 1 center | Part (21.50, 30.00) = Tray (27.50, 59.00, 0) | Insert at tray (27.50, 59.00), bored from Z = 0 upward through 3 mm floor into boss pad |
| Hole 2 center | Part (126.50, 30.00) = Tray (132.50, 59.00, 0) | Insert at tray (132.50, 59.00), bored from Z = 0 upward through 3 mm floor into boss pad |
| Hole-to-hole spacing | 105.00 mm (X direction) | Must match: 105.00 mm |
| Through-hole dia | 3.40 mm | Pilot hole dia: 4.00 mm (for M3 x 5.7 mm heat-set insert) |
| Fastener | M3 x 8 mm SHCS from below | M3 x 5.7 mm brass heat-set insert in boss pad |

### 4c. Floor Plate Edges to Cutout Edges (Centering)

The cutout edges provide coarse alignment. The plate is 4 mm wider than the cutout on each side. When the plate is pressed against the tray floor from below, the 4 mm overlap lips sit against the rib undersides. The screws provide the actual retention; the overlap provides bearing area.

---

## 5. Design Gaps

### 5a. Tray Floor Has No Cutout or Floor Plate Mounting Points

**Status: The tray (Sub-A) spec and all downstream sub-component specs (B through J) were designed without floor plate provisions.** The Sub-A box shell spec describes a solid, continuous floor from X = 0..160, Y = 0..155. No cutout, no boss pads, and no heat-set insert pockets for floor plate mounting exist in the current tray design.

**Required tray modifications if the floor plate option is used:**
1. Rectangular cutout in the tray floor: X = 10..150, Y = 33..85, full 3 mm depth (Z = 0 to Z = 3)
2. Two circular boss pads on the tray interior floor (Z = 3 surface) at (27.50, 59.00) and (132.50, 59.00), 8.0 mm diameter, 4.0 mm tall (Z = 3 to Z = 7), with 4.0 mm pilot holes bored from Z = 0 through the floor and into the boss pad (total bore depth: 3 + 4 = 7 mm, accommodating the 5.7 mm insert with 1.3 mm clearance below)
3. Floor ribs must remain at least 4 mm wide around the cutout perimeter (currently 5 mm on left/right sides, 24.5 mm on rear, 70 mm on front -- all adequate)

**This is an expected gap.** The concept architecture identifies the floor plate as optional (Part #5, "decide during prototyping"). The tray was intentionally designed without floor plate features so they can be added as a tray variant if prototyping reveals they are needed.

### 5b. Boss Pad Height vs Pump Head Clearance

The boss pads protrude 4 mm above the tray interior floor (Z = 3 to Z = 7). The pump head bottoms rest on the floor at Z = 3. If a boss pad is directly under a pump head, the pump head will rest on the boss pad instead of the floor, raising it 4 mm and reducing top clearance from 6.4 mm to 2.4 mm. This is acceptable but tight.

At tray positions (27.50, 59.00) and (132.50, 59.00), the boss pads are within the pump head footprints (Pump 1: X = 11.90..74.50, Pump 2: X = 85.50..148.10; both at Y = 35..83). **The pump head bottom is flat and contacts the floor across its full area. The 8 mm boss pads will create two small raised points under each pump head.**

**Mitigation options (for the spec agent to resolve):**
- Move boss pads to Y < 35 (behind the pump head, in the tube routing zone) -- this keeps them off the pump bearing surface but places them in the rear floor rib
- Accept the boss pads under the pump heads -- the pump head is rigid stamped metal and will bridge across two 8 mm pads without issue, but the pump will sit 4 mm higher (top clearance reduced to 2.4 mm, still positive)
- Recess the boss pads flush with the floor exterior (bore the insert from Z = 0 into the 3 mm floor only, no boss pad) -- but the 3 mm floor is too thin for a 5.7 mm deep insert

---

## 6. Transform Summary

```
Floor plate frame -> Tray frame:
  Translation: (+6.00, +29.00, 0)
  Rotation: none (identity)

  Part-local (px, py, pz) -> Tray (px + 6.00, py + 29.00, pz)
  Tray (tx, ty, tz) -> Part-local (tx - 6.00, ty - 29.00, tz)
```

### Verification Points

| Description | Part-local (X, Y, Z) | Tray frame (X, Y, Z) | Check |
|-------------|----------------------|----------------------|-------|
| Origin (rear-left, top face) | (0, 0, 0) | (6.00, 29.00, 0) | Plate left edge at tray X=6, plate rear edge at tray Y=29 |
| Far corner (front-right, top face) | (148.00, 60.00, 0) | (154.00, 89.00, 0) | Plate right edge at tray X=154, plate front edge at tray Y=89 |
| Screw hole 1 | (21.50, 30.00, 0) | (27.50, 59.00, 0) | On solid floor at tray Y=59, tray X=27.5 -- within Pump 1 zone, clear of bosses |
| Bottom face center | (74.00, 30.00, -4.00) | (80.00, 59.00, -4.00) | Plate center at tray centerline X=80, below floor by 4 mm |

**Round-trip verification:**
- Part (21.50, 30.00, 0) -> Tray (27.50, 59.00, 0) -> Part (27.50 - 6.00, 59.00 - 29.00, 0) = (21.50, 30.00, 0) -- correct
- Part (0, 0, 0) -> Tray (6.00, 29.00, 0) -> Part (0, 0, 0) -- correct
- Part (148, 60, -4) -> Tray (154, 89, -4) -> Part (148, 60, -4) -- correct

---

## 7. Dimensional Summary Table

All values in the stated reference frame (mm).

| Parameter | Value | Frame | Source |
|-----------|-------|-------|--------|
| Plate X extent | 148.00 | Part | Cutout 140 + 2 x 4 overlap |
| Plate Y extent | 60.00 | Part | Cutout 52 + 2 x 4 overlap |
| Plate Z thickness | 4.00 | Part | Concept architecture |
| Cutout X range | 10.00 to 150.00 | Tray | Pump head span + 2 mm clearance per side |
| Cutout Y range | 33.00 to 85.00 | Tray | Pump head Y span + 2 mm clearance per side |
| Cutout X width | 140.00 | Tray | Derived |
| Cutout Y depth | 52.00 | Tray | Derived |
| Screw hole 1 (X, Y) | (21.50, 30.00) | Part | Tray (27.50, 59.00) |
| Screw hole 2 (X, Y) | (126.50, 30.00) | Part | Tray (132.50, 59.00) |
| Screw hole spacing | 105.00 (X) | Part | 126.50 - 21.50 |
| Through-hole diameter | 3.40 | Part | M3 + 0.2 mm clearance |
| Counterbore diameter | 5.70 | Part | M3 SHCS head + 0.2 mm |
| Counterbore depth | 3.20 | Part | M3 SHCS head height + 0.2 mm |
| Overlap width (all edges) | 4.00 | Part | Design choice for bearing area |
| Plate origin in tray frame | (6.00, 29.00, 0) | Tray | Plate left edge = cutout X_start - overlap |
| Plate top face Z | 0 | Tray | Flush with tray floor exterior |
| Plate bottom face Z | -4.00 | Tray | Below tray floor by plate thickness |
