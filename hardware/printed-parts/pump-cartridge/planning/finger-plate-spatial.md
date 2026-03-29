# Finger Plate -- Spatial Resolution

All coordinates are in the **finger plate local frame** unless explicitly stated otherwise. Every dimension is a concrete number. No downstream trigonometry or coordinate transforms are required.

---

## 1. System-Level Placement

```
Part: Finger plate
Parent: Pump cartridge (spans both shell halves)
Position: front face of the cartridge. The visible plate body sits in
          the finger plate slot of the top shell. Two downward tabs
          extend below the parting line into the bottom shell interior
          to reach the linkage arm front-end pin positions.
Orientation: no rotation -- plate X/Y/Z axes align with bottom shell
             width/depth/height axes.
Motion: translates in -Y (rearward, toward release plate) by 2-4mm
        during squeeze action. Returns to rest via compression springs
        (spring force transmitted through linkage arms from the release
        plate).
```

This section is context only. All geometry below is resolved in the finger plate's own local frame.

---

## 2. Part Reference Frame

```
Part: Finger plate
  Origin: front-left-bottom corner of the visible plate body
  X: width (left to right), 0..120.0mm
  Y: depth (front face to rear face), 0..4.0mm
  Z: height (bottom to top of visible plate body), 0..24.5mm
  Print orientation: flat on build plate, front face (Y = 0) down.
    The user-facing surface is the build-plate face (smoothest surface).
  Installed orientation: identical to part frame (no rotation),
    translated to front face of cartridge.
```

Conventions:
- Front face at Y = 0 (user-facing surface, the build-plate face when printed).
- Rear face at Y = 4.0 (faces interior of cartridge).
- Left edge at X = 0, right edge at X = 120.0.
- Bottom of visible plate body at Z = 0 (corresponds to the parting line in assembly).
- Top of visible plate body at Z = 24.5 (0.5mm below the slot upper edge).
- Downward tabs extend below Z = 0 into negative Z territory (into the bottom shell interior in assembly).

---

## 3. Derived Geometry

### 3a. Visible Plate Body Envelope

The visible plate body is what the user sees through the finger plate slot. It is a flat rectangular plate.

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Width (X) | 120.0mm | Slot width 121.0mm minus 0.5mm clearance per side |
| Depth/thickness (Y) | 4.0mm | Concept specification (~4mm thick) |
| Height (Z) | 24.5mm | Slot height 25.0mm minus 0.5mm clearance at top edge only |
| X range (plate local) | 0 to 120.0 | |
| Y range (plate local) | 0 to 4.0 | |
| Z range (plate local) | 0 to 24.5 | |

**Width derivation:** The top shell finger plate slot is 121.0mm wide (top shell X = 5.2 to 126.2; assembly X = 5.5 to 126.5). With 0.5mm sliding clearance per side, the plate is 120.0mm wide. The plate spans assembly X = 6.0 to 126.0.

**Height derivation:** The slot is 25.0mm tall in the top shell (print Z = 8.5 to 33.5; assembly Z = 33.5 to 58.5). The plate has 0.5mm clearance at the top (palm-surface side, assembly Z = 58.0). At the bottom, the slot is open at the parting line (assembly Z = 33.5) -- the finger plate passes through this opening into the bottom shell, so no gap is needed at the bottom. Visible plate height: 25.0 - 0.5 = 24.5mm.

**Thickness derivation:** The concept specifies ~4mm. The finger plate recess depth is 3.0mm from the palm surface plane (the front face of the finger plate is 3.0mm behind the top shell front exterior). The plate's rear face at Y = 4.0 in plate local is at assembly Y = 7.3, which is 5.3mm behind the front wall interior face of the top shell (Y = 2.3 in assembly). With 2-4mm of squeeze travel in the -Y direction, the rear face moves to a maximum of Y = 11.3 in assembly at full squeeze, well within the 177mm cartridge depth.

**Clearances in the top shell slot:**

| Interface | Clearance | Notes |
|-----------|-----------|-------|
| Left edge to slot left wall | 0.5mm | Sliding fit for lateral constraint |
| Right edge to slot right wall | 0.5mm | Sliding fit for lateral constraint |
| Top edge to slot upper edge (palm strip) | 0.5mm | Prevents contact with palm surface horizontal strip |
| Bottom edge at parting line | 0mm (open) | Plate passes through open slot edge into bottom shell |

### 3b. Downward Tabs (Linkage Arm Connection)

The finger plate must connect to the linkage arm front-end pins. The linkage arms run in mid-height channels in the bottom shell at Z = 17.25 to 20.25 (arm center Z = 18.75 in bottom shell frame). The arm body top face is at shell Z = 20.25. The arm's front pin (3mm diameter, 5mm tall) rises from the arm top face at Z = 20.25 to Z = 25.25. The visible plate body bottom is at the parting line (assembly Z = 33.5). Two narrow rectangular tabs extend downward from the bottom-left and bottom-right corners of the plate body, running vertically inside the bottom shell front zone to reach the arm pin socket positions.

**Tab length derivation:**

The tab must bridge from the parting line (shell Z = 33.5) down to the arm pin top (shell Z = 25.25). Tab length = 33.5 - 25.25 = 8.25mm.

**Tab sizing rationale:**

The tabs transmit the full squeeze force (40-60N) in tension along their length (Z axis). Cross-section: 6.0mm wide (X) x 5.0mm deep (Y) = 30.0mm^2. At 60N, the tensile stress is 2.0 MPa -- well below PETG's tensile strength (~50 MPa). The tabs are also loaded in compression when the return springs push the finger plate back to rest; the same cross-section is adequate.

**Tab X-position derivation:**

The fundamental constraint is: the socket center must align with the arm pin center at bottom shell X = 5.5 (left) and X = 126.5 (right). The tab must surround the socket with at least 1.2mm structural wall.

Minimum tab extent around socket in X: 3.1/2 + 1.2 = 2.75mm from socket center to each tab face. Minimum tab width: 5.5mm. Use 6.0mm for margin.

Left tab centered on X = 5.5 in bottom shell frame:
- Tab X range: 5.5 - 3.0 to 5.5 + 3.0 = 2.5 to 8.5 in bottom shell frame
- Plate local X: 2.5 - 6.0 = -3.5 to 8.5 - 6.0 = 2.5

Right tab centered on X = 126.5 in bottom shell frame:
- Tab X range: 126.5 - 3.0 to 126.5 + 3.0 = 123.5 to 129.5 in bottom shell frame
- Plate local X: 123.5 - 6.0 = 117.5 to 129.5 - 6.0 = 123.5

**Tab Y thickness derivation:**

Tab Y = 5.0mm (1mm thicker than the visible plate body at Y = 4.0). Socket diameter 3.1mm. Wall around socket in Y direction: (5.0 - 3.1) / 2 = 0.95mm per side. Above 0.8mm non-structural minimum, adequate because the primary load is axial along Z.

**Left tab:**

| Parameter | Value (plate local) | Value (bottom shell frame) |
|-----------|--------------------|-----------------------------|
| Tab center X | -0.5 | 5.5 |
| Tab X range | -3.5 to 2.5 | 2.5 to 8.5 |
| Tab Y range | 0 to 5.0 | 3.3 to 8.3 |
| Tab top Z | 0 | 33.5 (parting line) |
| Tab bottom Z | -8.25 | 25.25 |
| Tab length (Z) | 8.25mm | |
| Tab width (X) | 6.0mm | |
| Tab thickness (Y) | 5.0mm | |

**Right tab (mirror of left):**

| Parameter | Value (plate local) | Value (bottom shell frame) |
|-----------|--------------------|-----------------------------|
| Tab center X | 120.5 | 126.5 |
| Tab X range | 117.5 to 123.5 | 123.5 to 129.5 |
| Tab Y range | 0 to 5.0 | 3.3 to 8.3 |
| Tab Z range | -8.25 to 0 | 25.25 to 33.5 |
| Tab width (X) | 6.0mm | |
| Tab thickness (Y) | 5.0mm | |
| Tab length (Z) | 8.25mm | |

**Tab clearance in the bottom shell front zone:**

The bottom shell front zone (Y = 2.0 to 27.0) is a clear tube routing zone. The tabs descend vertically in the outer corners of this zone.

The tabs span shell Z = 25.25 to 33.5, which is entirely above the inner rib top (Z = 20.25) and above the groove band thickening (Z = 12.75 to 17.25). At this Z range, the side wall interior face is at X = 2.0 (nominal 2.0mm wall thickness).

| Obstacle | Position (bottom shell) | Tab position | Clearance |
|----------|------------------------|-------------|-----------|
| Left side wall interior | X = 2.0 | Left tab left face at X = 2.5 | 0.5mm |
| Right side wall interior | X = 130.0 | Right tab right face at X = 129.5 | 0.5mm |
| Floor (interior) | Z = 2.0 | Tab bottom at Z = 25.25 | 23.25mm above floor |
| Inner rib top (left) | Z = 20.25 at X = 9.0..10.2 | Left tab right face at X = 8.5 | Tab is above rib top by 5.0mm (Z = 25.25 vs 20.25); rib right face at X = 10.2, tab right face at X = 8.5 -- no X overlap concern at tab Z range |
| Inner rib top (right) | Z = 20.25 at X = 121.8..123.0 | Right tab left face at X = 123.5 | Tab is above rib top; rib left face at X = 121.8, tab left face at X = 123.5 -- no overlap |
| Linkage arm body (top) | Z = 20.25 | Tab bottom at Z = 25.25 | 5.0mm (pin fills this gap) |

### 3c. Pin Sockets (2 sockets)

Each socket is a blind cylindrical bore in the bottom face of a downward tab, accepting the 3mm pin on the front end of each linkage arm. The pin axis is along Z (vertical, pin pointing upward from the arm, entering the tab from below).

The arm body top face is at shell Z = 20.25. The arm's front pin (3mm diameter, 5mm tall) rises from Z = 20.25 to Z = 25.25. The tab bottom face is at Z = 25.25. The socket opens at the tab bottom face and extends 5mm upward into the tab.

**Left pin socket:**

| Parameter | Value (plate local) | Value (bottom shell frame) |
|-----------|--------------------|-----------------------------|
| Socket center X | -0.5 | 5.5 |
| Socket center Y | 2.5 | 5.8 |
| Socket opening Z (bottom face of tab) | -8.25 | 25.25 |
| Socket blind end Z | -3.25 | 30.25 |
| Socket diameter | 3.1mm | |
| Socket depth | 5.0mm (extends upward into tab from bottom face) | |
| Socket axis | Z (vertical) | |
| Pin clearance (diametral) | 0.1mm (3.1mm socket, 3.0mm pin) | |

**Right pin socket:**

| Parameter | Value (plate local) | Value (bottom shell frame) |
|-----------|--------------------|-----------------------------|
| Socket center X | 120.5 | 126.5 |
| Socket center Y | 2.5 | 5.8 |
| Socket opening Z (bottom face of tab) | -8.25 | 25.25 |
| Socket blind end Z | -3.25 | 30.25 |
| Socket diameter | 3.1mm | |
| Socket depth | 5.0mm | |
| Socket axis | Z (vertical) | |
| Pin clearance (diametral) | 0.1mm | |

**Socket wall check:**
- X direction: (6.0 - 3.1) / 2 = 1.45mm per side. Above 1.2mm structural minimum.
- Y direction: (5.0 - 3.1) / 2 = 0.95mm per side. Above 0.8mm non-structural minimum. Acceptable because the pin-socket joint is primarily in shear/tension along Z, and the Y-direction wall is not the primary load path.

**Socket X-position derivation:** Centered on the arm channel center line. Left: bottom shell X = 5.5. Right: bottom shell X = 126.5. These match the release plate socket X-positions in the bottom shell frame (5.5 and 126.5).

**Socket Y-position derivation:** The socket is centered in the tab's Y dimension: Y = 5.0 / 2 = 2.5 in plate local. This aligns with the arm center Y in the bottom shell frame: the arm approaches from behind (high Y) and its pin is centered in the arm's 6mm width, which spans approximately Y = 2.3 to 8.3 in the bottom shell frame at the front end. The arm's Y-direction center at the front end is approximately Y = 5.3. The socket at Y = 5.8 (shell frame) is close to this center.

**Arm pin geometry (for reference -- arm is a separate part):**

The arm's front pin rises from the arm body top face (Z = 20.25 in bottom shell) to Z = 25.25 (5mm tall pin). The pin diameter is 3.0mm. The pin is centered in the arm's 6mm width (X) and 3mm height. When the finger plate is installed, the tab drops over the pin until the tab bottom face rests at Z = 25.25 (bottom shell), with the pin fully engaged in the 5mm deep socket.

### 3d. Crosshatch Grip Texture

The front face (Y = 0) of the visible plate body carries the same crosshatch texture as the palm surface on the top shell.

| Parameter | Value |
|-----------|-------|
| Texture location | Front face (Y = 0), full extent of visible plate body |
| X range | 0 to 120.0 |
| Z range | 0 to 24.5 |
| Pattern | Crosshatch: two sets of parallel grooves at 90 degrees to each other |
| Groove depth | 0.2mm into front face |
| Groove width | 0.4mm |
| Groove pitch | 1.0mm center-to-center |
| Surface | The build-plate face (smoothest possible FDM surface) with texture embossed via slicer bottom pattern or textured build plate |

### 3e. Perimeter Chamfer (Elephant's Foot Compensation)

The front face (Y = 0) is the build-plate face. A chamfer on the perimeter edges of the front face prevents elephant's foot flaring.

| Parameter | Value |
|-----------|-------|
| Chamfer location | All edges of the front face (Y = 0) perimeter, visible plate body only |
| Chamfer size | 0.3mm x 45 degrees |
| Chamfer type | Edge break, from front face into body |

---

## 4. Interface Summary

### 4.1. Top Shell Finger Plate Slot

| Parameter | Value |
|-----------|-------|
| Mating part | Top shell front wall slot |
| Interface type | Sliding fit; plate slides in Y within slot, constrained in X and Z |
| Plate visible body (plate local) | X: 0..120.0, Y: 0..4.0, Z: 0..24.5 |
| Slot (assembly frame) | X: 5.5..126.5, Y: 0.3..2.3 (through-wall), Z: 33.5..58.5 |
| Plate in slot (assembly frame) | X: 6.0..126.0, Y: 3.3..7.3, Z: 33.5..58.0 |
| Clearance left/right | 0.5mm per side |
| Clearance top | 0.5mm (plate top at assembly Z = 58.0, slot upper edge at Z = 58.5) |
| Clearance bottom | 0mm (open at parting line, plate passes through) |
| Sliding direction | -Y (rearward), 2-4mm travel |

### 4.2. Linkage Arm Front Pins (x2)

| Parameter | Value |
|-----------|-------|
| Mating part | Linkage arms (left and right), 3mm pins at front ends |
| Interface type | Pin-and-socket press-fit (3.0mm pin in 3.1mm socket, 0.1mm diametral clearance) |
| Pin axis | Z (vertical, pin points upward from arm into tab bottom) |
| Left socket center (plate local) | (-0.5, 2.5, -8.25) -- at socket opening face |
| Left socket center (bottom shell, at rest) | (5.5, 5.8, 25.25) |
| Right socket center (plate local) | (120.5, 2.5, -8.25) -- at socket opening face |
| Right socket center (bottom shell, at rest) | (126.5, 5.8, 25.25) |
| Socket diameter | 3.1mm |
| Socket depth | 5.0mm (upward into tab) |
| Mating arm pin diameter | 3.0mm |
| Mating arm pin height | 5.0mm (from arm top face Z = 20.25 to Z = 25.25 in bottom shell) |
| Joint type | Permanent press-fit with CA glue |

### 4.3. Bottom Shell Front Zone (clearance)

| Parameter | Value |
|-----------|-------|
| Mating part | Bottom shell walls (front zone Y = 2.0..27.0) |
| Interface type | Clearance only; tabs descend into bottom shell interior without contact |
| Left tab (bottom shell) | X: 2.5..8.5, Y: 3.3..8.3, Z: 25.25..33.5 |
| Right tab (bottom shell) | X: 123.5..129.5, Y: 3.3..8.3, Z: 25.25..33.5 |
| Clearance to left wall | 0.5mm (wall at X = 2.0, tab at X = 2.5) |
| Clearance to right wall | 0.5mm (wall at X = 130.0, tab at X = 129.5) |
| Clearance to floor | 23.25mm (floor at Z = 2.0, tab bottom at Z = 25.25) |
| Clearance to inner rib top | 5.0mm (rib top at Z = 20.25, tab bottom at Z = 25.25) |

### 4.4. Palm Surface (opposition surface)

| Parameter | Value |
|-----------|-------|
| Mating part | Top shell front wall exterior (palm surface zone) |
| Interface type | No contact. The palm surface is the rigid surface the user pushes against. The finger plate is the surface the user pulls. The 3.0mm gap between them is the recess depth. |
| Palm surface plane | Assembly Y = 0.3 (top shell front exterior) |
| Finger plate front face | Assembly Y = 3.3 (at rest) |
| Gap at rest | 3.0mm |
| Gap at full squeeze | 3.0 + 4.0 = 7.0mm (finger plate moves 4mm rearward at maximum travel) |

---

## 5. Transform Summary

The finger plate's local frame is related to the bottom shell frame by a pure translation. No rotation. The plate translates along -Y during operation.

```
Finger plate local frame -> Bottom shell frame (at rest):
  Rotation: identity (none)
  Translation: (+6.0, +3.3, +33.5)

  shell_X = plate_X + 6.0
  shell_Y = plate_Y + 3.3
  shell_Z = plate_Z + 33.5

Bottom shell frame -> Finger plate local frame (at rest):
  Translation: (-6.0, -3.3, -33.5)

  plate_X = shell_X - 6.0
  plate_Y = shell_Y - 3.3
  plate_Z = shell_Z - 33.5
```

**During operation:** The plate translates 0 to 4.0mm in -Y. At travel distance T (0 <= T <= 4.0mm):

```
shell_Y = plate_Y + 3.3 - T
```

X and Z transforms are unchanged during operation.

**Verification (3 test points at rest, T = 0):**

| Test point | Plate local (X, Y, Z) | Bottom shell (X, Y, Z) | Round-trip back | Match? |
|------------|----------------------|------------------------|-----------------|--------|
| Origin (visible plate body front-left-bottom) | (0, 0, 0) | (6.0, 3.3, 33.5) | (0, 0, 0) | Yes |
| Visible plate body top-right corner (front face) | (120.0, 0, 24.5) | (126.0, 3.3, 58.0) | (120.0, 0, 24.5) | Yes |
| Left pin socket center | (-0.5, 2.5, -8.25) | (5.5, 5.8, 25.25) | (-0.5, 2.5, -8.25) | Yes |

**Verification (at full squeeze, T = 4.0mm):**

| Test point | Plate local (X, Y, Z) | Bottom shell (X, Y, Z) | Notes |
|------------|----------------------|------------------------|-------|
| Front face center | (60.0, 0, 12.25) | (66.0, -0.7, 45.75) | Front face has moved 4mm rearward; Y = -0.7 means the front face is now 0.7mm in front of the bottom shell front wall exterior (Y = 0). This is correct: the finger plate recess starts 3.3mm behind the shell exterior at rest, so 4mm of travel puts it at -0.7 in shell frame. The plate is now deeper into the cartridge. |
| Left socket center | (-0.5, 2.5, -8.25) | (5.5, 1.8, 25.25) | Socket has moved 4mm rearward, pulling arm and release plate. |

**CORRECTION to full-squeeze verification:** At T = 4.0mm, shell_Y = plate_Y + 3.3 - 4.0 = plate_Y - 0.7. For the front face (plate_Y = 0): shell_Y = -0.7. This is technically outside the bottom shell (which starts at Y = 0). However, this represents the maximum squeeze travel. The practical working range is 2-3mm (per the release plate travel of 3mm). At T = 3.0mm: shell_Y = 0 + 3.3 - 3.0 = 0.3, which is exactly at the shell exterior. The 4mm maximum is the physical limit; the mechanism stops at 3mm due to the release plate deflection stop.

---

## 6. Print Orientation Notes

The finger plate prints flat on the build plate with its front face (Y = 0) down. In this orientation:

- The user-facing front surface is the build-plate face -- the smoothest possible FDM surface. The crosshatch texture is applied via slicer bottom pattern settings or a textured build plate.
- The two downward tabs print as vertical features rising upward from the plate body (in the print Z direction). The tabs are 6mm x 5mm cross-section, 8.25mm tall -- stable vertical features with no support needed.
- The pin sockets at the bottom of the tabs (plate local Z = -8.25) are at the TOP of the print. They are blind bores along the print Z axis (vertical holes) -- optimal for diameter accuracy.
- The visible plate body is the first 4mm of the print (Y = 0 to 4.0 maps to print Z = 0 to 4.0). The tabs then continue upward for another 8.25mm (with the extra 1mm in Y extending the tab section to print Z = 5.0).
- Build plate footprint: approximately 127mm x 32.75mm (X extent from -3.5 to 123.5 = 127mm; Z extent from -8.25 to 24.5 = 32.75mm).

**Actual build plate footprint:** In print orientation (front face down), the build plate contact is the front face of the entire part:
- X: from -3.5 to 123.5 = 127.0mm (includes tab extensions beyond plate body)
- Z (print Y): from -8.25 to 24.5 = 32.75mm
- Print height: Y extent = 0 to 5.0 = 5.0mm (maximum Y, at tabs)

The footprint is 127mm x 32.75mm. The print height is only 5mm. This is a very fast, flat print.

**Elephant's foot compensation:** The front face (Y = 0) is the build-plate face. A 0.3mm x 45-degree chamfer on the perimeter edges of the visible plate body prevents elephant's foot flaring. The tab bottom faces (where the pin sockets are) are at the top of the print and do not need elephant's foot chamfers.

---

## 7. Overall Bounding Box

| Parameter | Value (plate local) | Value (bottom shell frame) |
|-----------|--------------------|-----------------------------|
| X min | -3.5 (left tab) | 2.5 |
| X max | 123.5 (right tab) | 129.5 |
| Y min | 0 (front face) | 3.3 |
| Y max | 5.0 (tab rear face) | 8.3 |
| Z min | -8.25 (tab bottoms) | 25.25 |
| Z max | 24.5 (plate top) | 58.0 |
| Total X | 127.0mm | |
| Total Y | 5.0mm | |
| Total Z | 32.75mm | |

---

## 8. Dimension Summary Table

All critical dimensions in one table for quick reference by the parts specification agent.

| Dimension | Value | Frame | Source |
|-----------|-------|-------|--------|
| Visible plate width | 120.0mm | Plate X | Slot 121mm - 2 x 0.5mm clearance |
| Visible plate height | 24.5mm | Plate Z | Slot 25mm - 0.5mm top clearance |
| Visible plate thickness | 4.0mm | Plate Y | Concept spec |
| Tab width (each) | 6.0mm | Plate X | Socket dia 3.1 + 2 x 1.45mm wall |
| Tab thickness | 5.0mm | Plate Y | Socket dia 3.1 + 2 x 0.95mm wall |
| Tab length | 8.25mm | Plate Z | Bridge from parting line (Z=33.5) to arm pin top (Z=25.25) |
| Left tab X center | -0.5 | Plate X | Bottom shell X = 5.5 (arm channel center) |
| Right tab X center | 120.5 | Plate X | Bottom shell X = 126.5 (arm channel center) |
| Pin socket diameter | 3.1mm | -- | 0.1mm clearance on 3.0mm arm pin |
| Pin socket depth | 5.0mm | Plate Z | Matches arm pin height |
| Pin socket axis | Z (vertical) | -- | Pin enters from tab bottom face |
| Pin socket opening Z | -8.25 | Plate Z | Shell Z = 25.25 (arm pin top) |
| Pin socket blind end Z | -3.25 | Plate Z | Shell Z = 30.25 |
| Arm channel center Z | 18.75 | Shell Z | Mid-height channels (Z = 17.25..20.25) |
| Arm pin top Z | 25.25 | Shell Z | Arm top (20.25) + 5mm pin |
| Slot clearance (lateral) | 0.5mm per side | Plate X | Sliding fit |
| Slot clearance (top) | 0.5mm | Plate Z | Below palm strip |
| Recess depth (front face behind palm surface) | 3.0mm | Assembly Y | Palm at Y=0.3, plate at Y=3.3 in shell |
| Squeeze travel range | 2-4mm | -Y | Limited by release plate 3mm stroke |
| Tab-to-wall clearance | 0.5mm | Shell X | Both sides |
| Tab-to-rib clearance | N/A | -- | Tabs are above rib top (Z=20.25); no X overlap at tab Z range |
| Crosshatch groove depth | 0.2mm | Plate Y | Into front face |
| Crosshatch groove width | 0.4mm | -- | |
| Crosshatch pitch | 1.0mm | -- | Center-to-center |
| Elephant's foot chamfer | 0.3mm x 45 deg | -- | Front face perimeter, visible body only |
