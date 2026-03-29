# Spatial Resolution: Sub-B T-Rail Tongues

## 1. System-Level Placement

```
Mechanism: T-Rail Tongues (2x, left and right side walls)
Parent: Tray (Sub-A box shell)
Position: Outer faces of left and right side walls, running full depth
Orientation: Constant cross-section extruded along Y (insertion axis)
Purpose: Guide cartridge insertion/removal in dock C-channels; asymmetric Z placement prevents upside-down insertion
```

The tray sits in the lower-front zone of the 220 x 300 x 400 mm enclosure. The dock provides mating C-channel grooves on its left and right inner walls. The cartridge slides along Y (depth axis), with Y=0 at the dock (rear) and Y=155 at the user (front).

---

## 2. Reference Frame

```
Part: Tray (the parent solid that Sub-B attaches to)
  Origin: rear-left-bottom corner of the tray outer envelope
  X: width, 0 (left wall outer face) .. 160 (right wall outer face)
  Y: depth, 0 (dock-facing rear face) .. 155 (user-facing front edge)
  Z: height, 0 (bottom of floor) .. 72 (top of side walls)
  Print orientation: open top facing up, XY plane on build plate
```

All coordinates below are in this tray frame.

---

## 3. Derived Geometry

### 3.1 T-Profile Cross-Section Definition

The T-tongue is the male feature on the tray; the dock C-channel is the female groove. The T-profile cross-section is defined in the XZ plane (constant along Y).

**Tongue dimensions (tray side):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Cap width (Z extent) | 6.0 mm | The wider flange at the outer tip |
| Stem height (Z extent) | 3.0 mm | The narrow neck connecting cap to wall |
| Total protrusion from wall face (X) | 4.0 mm | How far the tongue sticks out |
| Cap thickness (X extent) | 2.0 mm | Thickness of the cap flanges in the protrusion direction |
| Stem depth (X extent) | 2.0 mm | Distance from wall face to where cap flanges begin (4.0 - 2.0) |
| Cap flange overhang per side (Z) | 1.5 mm | (6.0 - 3.0) / 2 |

**Mating dock C-channel dimensions (dock side, for reference):**

| Parameter | Value | Notes |
|-----------|-------|-------|
| Slot opening (Z) | 3.6 mm | Stem height 3.0 + 2 x 0.3 clearance |
| Channel cavity width (Z) | 6.6 mm | Cap width 6.0 + 2 x 0.3 clearance |
| Channel depth (X) | 4.3 mm | Protrusion 4.0 + 0.3 clearance at tip |
| Slot depth behind opening (X) | 2.3 mm | Stem depth 2.0 + 0.3 clearance |

Clearance is 0.3 mm per side throughout, consistent with standard FDM tolerance for sliding fits in PETG.

### 3.2 Left Rail Cross-Section (XZ profile at any Y slice)

The left rail protrudes in the **-X direction** from the left wall outer face (X = 0).

```
Left rail cross-section (looking from Y=155 toward Y=0, i.e., from user toward dock):

Z (mm)
 ^
 |
57.0  ─────────────────  cap top edge
      |               |
      |     CAP       |  cap: 6.0 mm tall (Z), 2.0 mm deep (X)
      |               |
55.5  ─────┐   ┌──────  cap-to-stem shoulder (1.5 mm flange)
            |   |
            |   |        stem: 3.0 mm tall (Z), 2.0 mm deep (X)
            |   |
52.5  ─────┘   └──────  stem-to-cap shoulder (1.5 mm flange)
      |               |
      |     CAP       |
      |               |
51.0  ─────────────────  cap bottom edge
      |               |
      X=-4    X=-2    X=0 (wall face)

         -X ──────────> toward wall
```

**Left rail coordinate table (XZ, tray frame):**

| Point | X (mm) | Z (mm) | Description |
|-------|--------|--------|-------------|
| A | 0.0 | 52.5 | Stem root, bottom |
| B | -2.0 | 52.5 | Stem tip / cap inner face, bottom |
| C | -2.0 | 51.0 | Cap outer corner, bottom |
| D | -4.0 | 51.0 | Cap tip, bottom |
| E | -4.0 | 57.0 | Cap tip, top |
| F | -2.0 | 57.0 | Cap outer corner, top |
| G | -2.0 | 55.5 | Stem tip / cap inner face, top |
| H | 0.0 | 55.5 | Stem root, top |

**Left rail center Z:** 54.0 mm (midpoint of cap: (51.0 + 57.0) / 2)
**Left rail stem center Z:** 54.0 mm (midpoint of stem: (52.5 + 55.5) / 2)

### 3.3 Right Rail Cross-Section (XZ profile at any Y slice)

The right rail protrudes in the **+X direction** from the right wall outer face (X = 160).

```
Right rail cross-section (looking from Y=155 toward Y=0):

Z (mm)
 ^
 |
21.0  ─────────────────  cap top edge
      |               |
      |     CAP       |
      |               |
19.5  ─────┐   ┌──────  cap-to-stem shoulder
            |   |
            |   |        stem
            |   |
16.5  ─────┘   └──────  stem-to-cap shoulder
      |               |
      |     CAP       |
      |               |
15.0  ─────────────────  cap bottom edge
      |               |
    X=160   X=162   X=164 (wall face at 160, tip at 164)

         wall ──────────> +X toward tip
```

**Right rail coordinate table (XZ, tray frame):**

| Point | X (mm) | Z (mm) | Description |
|-------|--------|--------|-------------|
| A | 160.0 | 16.5 | Stem root, bottom |
| B | 162.0 | 16.5 | Stem tip / cap inner face, bottom |
| C | 162.0 | 15.0 | Cap outer corner, bottom |
| D | 164.0 | 15.0 | Cap tip, bottom |
| E | 164.0 | 21.0 | Cap tip, top |
| F | 162.0 | 21.0 | Cap outer corner, top |
| G | 162.0 | 19.5 | Stem tip / cap inner face, top |
| H | 160.0 | 19.5 | Stem root, top |

**Right rail center Z:** 18.0 mm (midpoint of cap: (15.0 + 21.0) / 2)
**Right rail stem center Z:** 18.0 mm (midpoint of stem: (16.5 + 19.5) / 2)

### 3.4 Rail Y Extent (Extrusion Length)

Both rails are extruded along Y from the rear face to the front edge of the tray:

| Parameter | Value | Frame |
|-----------|-------|-------|
| Y start | 0.0 mm | Tray frame (flush with rear wall outer face) |
| Y end | 155.0 mm | Tray frame (flush with front edge) |
| Extrusion length | 155.0 mm | Along Y axis |

The rails run the full tray depth. The front is open (no front wall on the tray; the bezel attaches separately), so the rail extrusion simply terminates at the tray's Y extent.

### 3.5 Keying Verification

The asymmetric vertical placement prevents upside-down insertion:

| Configuration | Left rail center Z | Right rail center Z | Status |
|---------------|-------------------|--------------------|----|
| Correct orientation | 54.0 | 18.0 | Matches dock channels |
| Upside-down (Z flipped: Z' = 72 - Z) | 18.0 | 54.0 | Left at 18, right at 54 -- reversed, does NOT match dock |
| Left-right swapped (X flipped) | Right channel at 54, left at 18 | Also reversed, does NOT match | Blocked by asymmetry |

The 36.0 mm vertical offset between rails (54.0 - 18.0) provides unambiguous keying. The cartridge physically cannot enter the dock in any orientation other than the correct one.

### 3.6 Wall Contact Surfaces

Each tongue bonds flush to the flat outer face of its side wall. The contact (bonding) surface is a rectangular strip:

**Left rail contact surface:**
- Plane: X = 0 (left wall outer face)
- Z extent: 52.5 .. 55.5 mm (stem height, 3.0 mm)
- Y extent: 0 .. 155 mm (full depth)
- Area: 3.0 x 155.0 = 465 mm^2

**Right rail contact surface:**
- Plane: X = 160 (right wall outer face)
- Z extent: 16.5 .. 19.5 mm (stem height, 3.0 mm)
- Y extent: 0 .. 155 mm (full depth)
- Area: 3.0 x 155.0 = 465 mm^2

### 3.7 Printability Note

The T-profile cap flanges create overhangs when printed with open-top-up orientation (the tray's intended print orientation). Each flange is a 1.5 mm horizontal overhang in the Z build direction. At 1.5 mm, this is within the self-bridging capability of PETG on the Bambu H2C (overhangs under 2 mm typically print without support). A 45-degree chamfer on the underside of each flange can be added as a printability aid if needed -- this is a feature-level detail for the parts specification step.

### 3.8 Interface: Tray T-Tongue to Dock C-Channel (Both Sides)

**From the tray tongue side (this sub-component):**

| Interface | Tray feature | Position in tray frame | Mating dock feature |
|-----------|-------------|----------------------|-------------------|
| Left rail into dock left C-channel | T-tongue protruding at X < 0 | Cap: X = -4.0 .. -2.0, Z = 51.0 .. 57.0, full Y | C-channel groove in dock left wall, opening faces +X |
| Right rail into dock right C-channel | T-tongue protruding at X > 160 | Cap: X = 162.0 .. 164.0, Z = 15.0 .. 21.0, full Y | C-channel groove in dock right wall, opening faces -X |

**From the dock C-channel side:**

The dock C-channel is a captured slot. Its cross-section (in the dock's XZ plane, which aligns with the tray frame during insertion):

| Dock channel parameter | Left channel | Right channel |
|----------------------|-------------|--------------|
| Slot opening Z range | 52.2 .. 55.8 mm | 16.2 .. 19.8 mm |
| Slot opening width (Z) | 3.6 mm | 3.6 mm |
| Cavity Z range | 50.7 .. 57.3 mm | 14.7 .. 21.3 mm |
| Cavity width (Z) | 6.6 mm | 6.6 mm |
| Channel depth (X, into dock wall) | 4.3 mm | 4.3 mm |
| Channel Y extent | Full dock depth (matches tray Y range) | Same |

The dock channel Z positions are derived from the tray tongue Z positions plus 0.3 mm clearance on each side.

---

## 4. Transform Summary

The tray frame is the reference frame for this sub-component. The tongues are modeled directly in the tray frame -- no rotation or transform is needed because the tongues are integral to the tray.

```
Sub-B frame = Tray frame (identity transform)
  No rotation, no translation.
  The T-tongue profiles are defined as XZ cross-sections extruded along Y.
```

**Tray frame to enclosure (system) frame:**

The tray occupies the lower-front zone of the enclosure. The exact enclosure-to-tray transform depends on enclosure internal layout (not yet resolved), but for reference:

```
Tray frame -> Enclosure frame:
  Translation only (no rotation -- tray sits level in the enclosure)
  Tray origin (rear-left-bottom) maps to enclosure interior position TBD
  Tray X aligns with enclosure X (width)
  Tray Y aligns with enclosure Y (depth, 0=back, positive=front)
  Tray Z aligns with enclosure Z (height, 0=bottom, positive=up)
```

**Verification points (all in tray frame, identity transform):**

| Test point | Tray frame | Description | Check |
|------------|-----------|-------------|-------|
| Left rail cap tip, bottom-rear | (-4.0, 0.0, 51.0) | Outermost point of left rail at rear | Cap protrudes 4 mm left of wall at Z=51 |
| Right rail cap tip, top-front | (164.0, 155.0, 21.0) | Outermost point of right rail at front | Cap protrudes 4 mm right of wall at Z=21 |
| Left rail stem root center | (0.0, 77.5, 54.0) | Mid-depth of left wall, stem center | Stem center at Z=54, on wall face |

All three points are trivially consistent because the sub-component frame is the tray frame (identity transform). The tongue geometry is defined directly in the frame where it will be built.

---

## 5. Dimension Summary Table

All values in tray frame. This table collects every number a downstream CadQuery agent needs.

| Dimension | Value | Axis | Notes |
|-----------|-------|------|-------|
| Left wall outer face | X = 0.0 mm | X | Stem root plane |
| Right wall outer face | X = 160.0 mm | X | Stem root plane |
| Left tongue protrusion | 4.0 mm in -X | X | Wall face to cap tip |
| Right tongue protrusion | 4.0 mm in +X | X | Wall face to cap tip |
| Left tongue cap Z range | 51.0 .. 57.0 mm | Z | 6.0 mm cap width |
| Left tongue stem Z range | 52.5 .. 55.5 mm | Z | 3.0 mm stem height |
| Right tongue cap Z range | 15.0 .. 21.0 mm | Z | 6.0 mm cap width |
| Right tongue stem Z range | 16.5 .. 19.5 mm | Z | 3.0 mm stem height |
| Rail Y start | 0.0 mm | Y | Rear face |
| Rail Y end | 155.0 mm | Y | Front edge |
| Stem depth (X) | 2.0 mm | X | From wall face to cap inner face |
| Cap thickness (X) | 2.0 mm | X | Cap flange radial thickness |
| Cap flange overhang (Z) | 1.5 mm | Z | Per side beyond stem |
| Keying offset | 36.0 mm | Z | Between left rail center (54) and right rail center (18) |
| Clearance per side vs dock | 0.3 mm | all | Standard FDM sliding fit |
| Total tray envelope with tongues (X) | -4.0 .. 164.0 mm | X | 168 mm total width including tongues |
