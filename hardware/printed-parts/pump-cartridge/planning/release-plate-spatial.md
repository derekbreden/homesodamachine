# Release Plate — Spatial Resolution

All coordinates are in the **release plate local frame** unless explicitly stated otherwise. Every dimension is a concrete number. No downstream trigonometry or coordinate transforms are required.

---

## 1. System-Level Placement

```
Part: Release plate
Parent: Pump cartridge (bottom shell)
Position: rear zone of cartridge, between motor end caps and JG fitting
          body ends. Sits approximately Y = 157..162 in the bottom shell
          frame at rest.
Orientation: no rotation — plate X/Y/Z axes align with bottom shell
             width/depth/height axes.
Motion: translates +Y (toward rear wall) by up to 3.0mm during release
        action. Returns to rest via compression springs.
```

This section is context only. All geometry below is resolved in the release plate's own local frame.

---

## 2. Part Reference Frame

```
Part: Release plate
  Origin: front-left-bottom corner of the main plate body
  X: width (left to right), 0..83.4mm (main body)
  Y: depth (front face to rear face), 0..5.0mm
  Z: height (bottom to top), 0..34.2mm (main body)
  Print orientation: flat on build plate, rear face (Y = 5.0) down on
    build plate. Stepped bores are vertical holes (Z-axis circles).
  Installed orientation: identical to part frame (no rotation),
    translated to rear zone of bottom shell.
```

Conventions:
- Front face at Y = 0 (faces toward cartridge front, away from fittings).
- Rear face at Y = 5.0 (faces toward rear wall and JG fittings).
- Left edge at X = 0, right edge at X = 83.4 (main body only).
- Bottom edge at Z = 0, top edge at Z = 34.2 (main body only).
- Lateral tabs extend beyond the main body in X for the linkage arm pin sockets.

---

## 3. Derived Geometry

### 3a. Plate Body Envelope

**Main body:**

| Parameter | Value |
|-----------|-------|
| Width (X) | 83.4mm (X = 0 to 83.4) |
| Depth/thickness (Y) | 5.0mm (Y = 0 to 5.0) |
| Height (Z) | 34.2mm (Z = 0 to 34.2) |

**Width derivation:** The plate spans all 4 JG bore centers (plate local X = 9.2 to 74.2) plus the 15.4mm body end cradle bore radius (7.7mm) plus 1.5mm wall material on each side. Left edge: 9.2 - 7.7 - 1.5 = 0.0. Right edge: 74.2 + 7.7 + 1.5 = 83.4.

**Height derivation:** The plate spans all 4 JG bore centers (plate local Z = 8.55 to 25.65) plus cradle bore radius (7.7mm) plus wall material. Bottom: 8.55 - 7.7 - 0.85 = 0.0. Top: 25.65 + 7.7 + 0.85 = 34.2. The 0.85mm wall at top and bottom is above the 0.8mm minimum wall thickness for non-structural edges.

**Wall between bores:**

| Gap | Value | Notes |
|-----|-------|-------|
| Between lower and upper cradle bores (Z direction) | 1.70mm | Z gap: (25.65 - 7.7) - (8.55 + 7.7) = 17.95 - 16.25 = 1.70mm. Adequate for non-structural web. |
| Between left and right cradle bores (X direction) | 47.30mm | X gap: (74.2 - 7.7) - (9.2 + 7.7) = 66.5 - 16.9 = 49.6mm. Ample material. |

**Depth derivation:** 5.0mm accommodates the three-step bore profile (see Section 3b) and provides adequate stiffness across the 83.4mm span. The plate is loaded axially (in Y) by the collet contact force.

**Clearances in the bottom shell:**

| Interface | Release plate (local) | Bottom shell (shell frame) | Clearance |
|-----------|----------------------|---------------------------|-----------|
| Left side wall interior (non-groove band) | X = 0 | X = 24.3 | 22.3mm to wall at X = 2.0 |
| Right side wall interior (non-groove band) | X = 83.4 | X = 107.7 | 22.3mm to wall at X = 130.0 |
| Floor interior | Z = 0 | Z = 1.0 | ~1.0mm above floor (plate rides on collets, not floor) |
| Bottom shell open top edge | Z = 34.2 | Z = 35.2 | Protrudes 1.7mm above shell edge at Z = 33.5; captured by top shell |

**Lateral tabs (linkage arm pin connections):**

Two rectangular tabs extend from the main body's sides at mid-height to reach the linkage arm channel positions. The tabs are centered on the arm channel center Z = 18.75 in the bottom shell frame, which is Z = 17.75 in the plate local frame (18.75 - 1.0 = 17.75). Each tab is 5.0mm tall, spanning Z = 15.25 to 20.25 in the plate local frame.

| Parameter | Left tab | Right tab |
|-----------|----------|-----------|
| X extent (plate local) | -18.8 to 0 | 83.4 to 102.2 |
| Y extent (plate local) | 0 to 5.0 | 0 to 5.0 |
| Z extent (plate local) | 15.25 to 20.25 | 15.25 to 20.25 |
| Tab length (X) | 18.8mm | 18.8mm |
| Tab height (Z) | 5.0mm | 5.0mm |
| Tab depth (Y) | 5.0mm | 5.0mm |
| Cross-section (Z x Y) | 5.0mm x 5.0mm | 5.0mm x 5.0mm |

The tabs extend from the mid-height of the main body's left and right edges to the pin socket positions in the mid-height linkage arm channels (bottom shell Z = 17.25 to 20.25). The tab Z range in the shell frame is 15.25 + 1.0 = 16.25 to 20.25 + 1.0 = 21.25. The arm channel spans Z = 17.25 to 20.25 in the shell frame. The tab center Z in the shell frame is 18.75, matching the channel center Z = 18.75. The tab extends 1.0mm below the channel (shell Z = 16.25 to 17.25) and 1.0mm above (shell Z = 20.25 to 21.25); the below portion overlaps with the groove band thickening zone and the above portion is in the open bay area -- both are clear of obstructions.

**Overall bounding box (including tabs):**

| Parameter | Value |
|-----------|-------|
| X extent | -18.8 to 102.2 (121.0mm total) |
| Y extent | 0 to 5.0 (5.0mm) |
| Z extent | 0 to 34.2 (34.2mm) |

Note: The tabs (Z = 15.25 to 20.25) are within the main body height (Z = 0 to 34.2), so they do not extend the bounding box in Z.

---

### 3b. JG Collet Stepped Bore Positions (4 bores)

Each bore is a three-step concentric profile, entered from the rear face (Y = 5.0) and passing through to the front face (Y = 0). The bore axes are parallel to Y.

**Bore center positions (X, Z) in the plate local frame:**

| Bore | Plate local X | Plate local Z | Bottom shell X | Bottom shell Z |
|------|---------------|---------------|----------------|----------------|
| JG1 (left lower) | 9.2 | 8.55 | 33.5 | 9.55 |
| JG2 (right lower) | 74.2 | 8.55 | 98.5 | 9.55 |
| JG3 (left upper) | 9.2 | 25.65 | 33.5 | 26.65 |
| JG4 (right upper) | 74.2 | 25.65 | 98.5 | 26.65 |

**Center-to-center spacing:**

| Pair | Distance | Direction |
|------|----------|-----------|
| JG1 to JG2 (horizontal) | 65.0mm | X |
| JG1 to JG3 (vertical) | 17.1mm | Z |
| JG1 to JG4 (diagonal) | 67.2mm | X-Z |

**Stepped bore profile (all 4 bores identical):**

Each bore is entered from the rear face (Y = 5.0). The three steps are:

| Step | Diameter | Y start (from rear face) | Y end | Depth | Function |
|------|----------|--------------------------|-------|-------|----------|
| Body end cradle | 15.4mm | Y = 5.0 (rear face) | Y = 1.6 | 3.4mm | Clears 15.10mm body end OD as plate advances over fittings. 0.15mm clearance per side. |
| Collet hugger | 9.8mm | Y = 1.6 | Y = 1.0 | 0.6mm | Close fit around 9.57mm collet OD. 0.115mm clearance per side. Provides lateral guidance. |
| Tube clearance | 6.5mm | Y = 1.0 | Y = 0 (front face) | 1.0mm | Through-hole for 6.35mm tube. 0.075mm clearance per side. |

**Collet contact annular face:**

The step between the tube clearance bore (6.5mm) and the collet hugger bore (9.8mm) at Y = 1.0 forms the annular face that pushes the collet end faces during release. This face is perpendicular to Y and is the primary functional surface of the release plate.

| Parameter | Value |
|-----------|-------|
| Contact face Y position (plate local) | Y = 1.0 |
| Contact face inner diameter | 6.5mm |
| Contact face outer diameter | 9.8mm |
| Contact annular width | 1.65mm |
| Contact face position from front face | 1.0mm |
| Contact face position from rear face | 4.0mm |

**Bore depth verification against travel:**

At rest, the contact face is 1.0mm from the collet tips (take-up gap). At full travel (+3.0mm in +Y), the plate advances 3.0mm. The contact face first contacts the collet tips after 1.0mm of travel, then pushes the collets inward 1.3mm (their full travel). Total plate travel consumed: 1.0 + 1.3 = 2.3mm. Remaining margin: 3.0 - 2.3 = 0.7mm.

Body end clearance at full travel: the body end face (at Y = 161.92 in shell frame) penetrates 3.22mm from the plate's rear face. The cradle bore depth is 3.4mm. Clearance margin: 0.18mm.

---

### 3c. Linkage Arm Pin Sockets (2 sockets)

Each socket is a blind cylindrical bore in the lateral tabs, accepting the 3mm pin on the rear end of each linkage arm. The pin axis is along Y (opening on the front face of the tab), matching the linkage arm approach direction. The arms run fore-aft (Y direction) in the bottom shell guide channels, so the pin enters the socket from the front face of the tab.

**Left pin socket:**

| Parameter | Value |
|-----------|-------|
| Center (X, Y, Z) plate local | (-9.4, 0, 17.75) |
| Center (X, Y, Z) bottom shell, at rest | (14.9, 157.2, 18.75) |
| Socket diameter | 3.1mm |
| Socket axis | +Y (pointing into tab from front face, toward rear) |
| Socket depth | 4.0mm |
| Socket opening face | Y = 0 (front face of tab) |
| Socket blind end Y plate local | 4.0 |

**Right pin socket:**

| Parameter | Value |
|-----------|-------|
| Center (X, Y, Z) plate local | (92.8, 0, 17.75) |
| Center (X, Y, Z) bottom shell, at rest | (117.1, 157.2, 18.75) |
| Socket diameter | 3.1mm |
| Socket axis | +Y (pointing into tab from front face, toward rear) |
| Socket depth | 4.0mm |
| Socket opening face | Y = 0 (front face of tab) |
| Socket blind end Y plate local | 4.0 |

**Socket position derivation:**

The sockets are centered vertically within the lateral tabs at Z = 17.75 (tab spans Z = 15.25 to 20.25, center at 17.75), and centered in the X width of each tab (left tab X = -18.8 to 0, center at -9.4; right tab X = 83.4 to 102.2, center at 92.8). The socket axis is Y, opening on the front face (Y = 0) of the tab. The socket depth is 4.0mm (from Y = 0 to Y = 4.0), leaving 1.0mm of wall material between the blind end and the rear face (Y = 5.0). The socket center Z = 17.75 in plate local corresponds to shell Z = 18.75, which matches the arm channel center Z = 18.75 in the bottom shell frame (midpoint of channel Z = 17.25 to 20.25).

---

### 3d. Spring Boss Receivers (2 receivers)

The release plate has two cylindrical centering bosses on its rear face that mate with the compression springs. The springs sit between these bosses and the matching bosses on the rear wall of the bottom shell.

**Left spring boss:**

| Parameter | Value |
|-----------|-------|
| Center (X, Z) plate local | (9.2, 17.1) |
| Center (X, Z) bottom shell | (33.5, 18.1) |
| Base (on plate rear face) Y plate local | 5.0 |
| Tip Y plate local | 8.0 |
| Boss diameter | 2.0mm |
| Boss height (protrusion from rear face) | 3.0mm |

**Right spring boss:**

| Parameter | Value |
|-----------|-------|
| Center (X, Z) plate local | (74.2, 17.1) |
| Center (X, Z) bottom shell | (98.5, 18.1) |
| Base Y plate local | 5.0 |
| Tip Y plate local | 8.0 |
| Boss diameter | 2.0mm |
| Boss height (protrusion from rear face) | 3.0mm |

**Position derivation:** The spring bosses are at the same (X, Z) as the JG bore centerlines in each bay, matching the rear wall spring bosses on the bottom shell (bottom shell X = 33.5, Z = 18.1 and X = 98.5, Z = 18.1). In the plate local frame: X = bore center X = 9.2 and 74.2; Z = 18.1 - 1.0 = 17.1.

**Spring geometry at rest:**

| Parameter | Value |
|-----------|-------|
| Plate boss tip Y (shell frame, rest) | 162.2 + 3.0 = 165.2 |
| Rear wall boss tip Y (shell frame) | 171.0 |
| Free span between boss tips | 171.0 - 165.2 = 5.8mm |
| Spring free length (nominal) | ~10mm |
| Spring compression at rest | ~4.2mm |
| Spring force at rest (~1 N/mm) | ~4.2N per spring |

**Spring geometry at full travel (+3mm):**

| Parameter | Value |
|-----------|-------|
| Plate boss tip Y (shell frame) | 165.2 + 3.0 = 168.2 |
| Free span between boss tips | 171.0 - 168.2 = 2.8mm |
| Spring compression at full travel | ~7.2mm |
| Spring force at full travel (~1 N/mm) | ~7.2N per spring |
| Total return force at full travel (2 springs) | ~14.4N |

Note for downstream parts specification: the spring pre-compression at rest (4.2mm) adds to the user's initial squeeze resistance. A softer spring (~0.5 N/mm) or shorter bosses (reducing pre-compression) would reduce the idle spring force to ~2N per spring while still providing adequate return force (~3.6N per spring, ~7.2N total at full travel). The parts specification agent should optimize the spring rate and boss height to achieve 5-10N total return force at full travel per the synthesis target.

---

### 3e. Guide Features

The release plate is guided laterally (X and Z) by the four collet-hugger bores (9.8mm diameter, 0.6mm deep) riding on the four collet ODs (9.57mm). This four-point guidance prevents tilt during the release stroke.

**Guide bore engagement:**

| Parameter | Value |
|-----------|-------|
| Bore diameter | 9.8mm |
| Collet OD | 9.57mm |
| Diametral clearance | 0.23mm |
| Radial clearance | 0.115mm |
| Engagement depth along Y | 0.6mm |
| Number of guide points | 4 |
| Guide pattern span (X) | 65.0mm |
| Guide pattern span (Z) | 17.1mm |

The four bores constrain the plate in X and Z while permitting Y translation. With 0.115mm radial clearance at each bore, the maximum tilt the plate can develop is:

- Tilt about X axis: arctan(2 x 0.115 / 17.1) = 0.77 degrees
- Tilt about Z axis: arctan(2 x 0.115 / 65.0) = 0.20 degrees

Both are well within the 3.5-degree angular tolerance calculated in the collet release force research.

No additional guide features are required. The collet-hugger bores serve as the sole guide surfaces.

---

## 4. Interface Summary

### 4.1. JG Fitting Collets (x4)

| Parameter | Value |
|-----------|-------|
| Mating part | JG PP0408W collet sleeves (inboard side) |
| Interface type | Stepped bore riding on collet OD; contact face pushes collet annular end face |
| Plate local bore centers (X, Z) | JG1: (9.2, 8.55), JG2: (74.2, 8.55), JG3: (9.2, 25.65), JG4: (74.2, 25.65) |
| Bottom shell bore centers (X, Z) | JG1: (33.5, 9.55), JG2: (98.5, 9.55), JG3: (33.5, 26.65), JG4: (98.5, 26.65) |
| Contact face Y (plate local) | Y = 1.0 |
| Contact face Y (shell frame, rest) | Y = 158.2 |
| Contact face Y (shell frame, full travel) | Y = 161.2 |
| Collet tip Y (shell frame, extended) | Y = 159.2 |
| Collet tip Y (shell frame, compressed) | Y = 160.5 |
| Take-up gap at rest | 1.0mm (159.2 - 158.2) |
| Bore diameters | 6.5mm / 9.8mm / 15.4mm (tube clearance / collet hugger / body end cradle) |
| Mating feature on bottom shell | JG fittings press-fit into rear wall bores at Y = 174.0..177.0 |

### 4.2. Spring Bosses (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Compression springs (captured between plate bosses and rear wall bosses) |
| Interface type | Cylindrical centering boss on plate rear face, spring compressed between plate and rear wall |
| Plate local boss centers (X, Z) | Left: (9.2, 17.1), Right: (74.2, 17.1) |
| Bottom shell boss centers (X, Z) | Left: (33.5, 18.1), Right: (98.5, 18.1) |
| Plate boss base Y (plate local) | 5.0 |
| Plate boss base Y (shell frame, rest) | 162.2 |
| Rear wall boss base Y (shell frame) | 174.0 |
| Rear wall boss tip Y (shell frame) | 171.0 |
| Boss diameter (both plate and wall) | 2.0mm |
| Boss height (both plate and wall) | 3.0mm |

### 4.3. Linkage Arm Pins (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Linkage arms (left and right), 3mm pins at rear ends |
| Interface type | Pin-and-socket press-fit (3mm pin in 3.1mm socket) |
| Left socket center (plate local) | (-9.4, 0, 17.75) |
| Left socket center (shell frame, rest) | (14.9, 157.2, 18.75) |
| Right socket center (plate local) | (92.8, 0, 17.75) |
| Right socket center (shell frame, rest) | (117.1, 157.2, 18.75) |
| Socket diameter | 3.1mm |
| Socket depth | 4.0mm |
| Pin axis | Y (arm approaches from front, pin enters socket from front face Y = 0) |
| Mating arm channel (bottom shell) | Left: X = 2.0..9.0, Right: X = 123.0..130.0, Z = 17.25..20.25 |

### 4.4. Rear Wall Face (travel limit)

| Parameter | Value |
|-----------|-------|
| Mating part | Bottom shell rear wall inboard face |
| Interface type | Proximity limit (no contact at full travel, springs prevent hard stop) |
| Rear wall Y (shell frame) | 174.0 |
| Plate rear face Y (shell frame, rest) | 162.2 |
| Plate rear face Y (shell frame, full travel) | 165.2 |
| Gap at rest | 11.8mm |
| Gap at full travel | 8.8mm |
| Spring boss tip-to-tip gap at full travel | 2.8mm |

The plate never contacts the rear wall directly. The compression springs and the collet mechanical stops limit the plate's forward travel. The springs compress to ~7.2mm at full travel, well short of their solid length (~5mm for a 10mm free-length spring).

---

## 5. Transform Summary

The release plate's local frame is related to the bottom shell frame by a pure translation. No rotation. The plate translates along Y during operation.

```
Release plate local frame -> Bottom shell frame (at rest):
  Rotation: identity (none)
  Translation: (+24.3, +157.2, +1.0)

  plate_X_shell = plate_X_local + 24.3
  plate_Y_shell = plate_Y_local + 157.2
  plate_Z_shell = plate_Z_local + 1.0

Bottom shell frame -> Release plate local frame (at rest):
  Translation: (-24.3, -157.2, -1.0)

  plate_X_local = plate_X_shell - 24.3
  plate_Y_local = plate_Y_shell - 157.2
  plate_Z_local = plate_Z_shell - 1.0
```

**During operation:** The plate translates 0 to 3.0mm in +Y. At travel distance T (0 <= T <= 3.0mm):

```
plate_Y_shell = plate_Y_local + 157.2 + T
```

X and Z transforms are unchanged during operation.

**Verification (3 test points at rest, T = 0):**

| Test point | Plate local (X, Y, Z) | Bottom shell (X, Y, Z) | Round-trip back | Match? |
|------------|----------------------|------------------------|-----------------|--------|
| Origin | (0, 0, 0) | (24.3, 157.2, 1.0) | (0, 0, 0) | Yes |
| JG1 bore center (at contact face) | (9.2, 1.0, 8.55) | (33.5, 158.2, 9.55) | (9.2, 1.0, 8.55) | Yes |
| Left pin socket center | (-9.4, 0, 17.75) | (14.9, 157.2, 18.75) | (-9.4, 0, 17.75) | Yes |

**Verification (at full travel, T = 3.0mm):**

| Test point | Plate local (X, Y, Z) | Bottom shell (X, Y, Z) | Notes |
|------------|----------------------|------------------------|-------|
| JG1 contact face | (9.2, 1.0, 8.55) | (33.5, 161.2, 9.55) | Contact face has passed collet tip (Y = 159.2) and compressed collet to Y = 160.5 |
| Plate rear face center | (41.7, 5.0, 17.1) | (66.0, 165.2, 18.1) | 8.8mm gap to rear wall at Y = 174.0 |
| Left pin socket | (-9.4, 0, 17.75) | (14.9, 160.2, 18.75) | Socket moved 3mm rearward from rest position |

All test points are self-consistent with the transform and verify correct interface alignment.

---

## 6. Print Orientation Notes

The release plate prints flat on the build plate with its rear face (Y = 5.0) down. In this orientation:

- The four stepped bores are vertical holes (axes along the print Z direction). This produces the best circularity and diameter accuracy for the critical collet-hugger bores (9.8mm with 0.23mm diametral clearance).
- The body end cradle bores (15.4mm, 3.4mm deep) are counterbores on the build-plate face.
- The collet hugger bores (9.8mm, 0.6mm deep) are intermediate steps in the vertical holes.
- The tube clearance bores (6.5mm, 1.0mm deep) are the smallest step, at the top of the print.
- The lateral tabs are at mid-height (Z = 15.25 to 20.25 plate local) and print as integral extensions of the main body at that height. The pin sockets are Y-axis blind holes (opening on the front face) — in the print orientation (rear face down), these are horizontal blind holes that print as bridged circles (3.1mm diameter), well within the 15mm bridge span limit.
- The spring bosses (2.0mm dia, 3.0mm tall) print vertically as small cylinders rising from the build-plate face. These are the boss features on the rear face.
- Build plate footprint: approximately 121mm x 34mm (the bounding box of main body plus tabs).

**Elephant's foot compensation:** The rear face (Y = 5.0) is the build-plate face. The body end cradle bore openings and spring boss bases are on this face. A 0.3mm x 45-degree chamfer on the plate's perimeter bottom edge prevents elephant's foot from affecting the mating surfaces.

---

## 7. Dimension Summary Table

All critical dimensions in one table for quick reference by the parts specification agent.

| Dimension | Value | Frame | Source |
|-----------|-------|-------|--------|
| Main body width | 83.4mm | Plate X | Derived from JG bore span + cradle radius + wall |
| Main body depth | 5.0mm | Plate Y | Bore profile accommodation |
| Main body height | 34.2mm | Plate Z | Derived from JG bore span + cradle radius + wall |
| Tab length (each) | 18.8mm | Plate X | Distance from body edge to arm channel center |
| Tab Z extent | 15.25 to 20.25 | Plate Z | Centered on arm channel center Z = 17.75 plate local (18.75 shell) |
| Tab cross-section | 5.0mm x 5.0mm | Plate Z x Y | Matches arm channel height, full plate depth |
| Tube clearance bore dia | 6.5mm | -- | Clears 6.35mm tube, under 6.69mm collet ID |
| Collet hugger bore dia | 9.8mm | -- | 0.23mm clearance on 9.57mm collet OD |
| Body end cradle bore dia | 15.4mm | -- | 0.30mm clearance on 15.10mm body end OD |
| Cradle depth (from rear face) | 3.4mm | Plate Y | Clears body end at full travel with 0.18mm margin |
| Hugger depth | 0.6mm | Plate Y | Guide engagement length |
| Tube clearance depth (from front face) | 1.0mm | Plate Y | Through to front face |
| Contact face Y (plate local) | 1.0mm from front face | Plate Y | Step between 6.5mm and 9.8mm bores |
| JG bore center-to-center (horizontal) | 65.0mm | Plate X | Matches bottom shell JG bore spacing |
| JG bore center-to-center (vertical) | 17.1mm | Plate Z | Matches bottom shell JG bore spacing |
| Pin socket diameter | 3.1mm | -- | 0.1mm clearance on 3.0mm pin |
| Pin socket depth | 4.0mm | Plate Y | Blind bore along Y axis, opening on front face |
| Pin socket center Z | 17.75 | Plate Z | Centered on arm channel (shell Z = 18.75) |
| Spring boss diameter | 2.0mm | -- | Matches rear wall boss |
| Spring boss height | 3.0mm | Plate Y | Protrudes from rear face |
| Take-up gap (rest) | 1.0mm | Shell Y | Contact face to collet tip at rest |
| Plate travel | 3.0mm | Shell Y | +Y direction (toward rear wall) |
| Plate rest position (front face Y, shell frame) | 157.2 | Shell Y | -- |
| Plate rest position (rear face Y, shell frame) | 162.2 | Shell Y | -- |
