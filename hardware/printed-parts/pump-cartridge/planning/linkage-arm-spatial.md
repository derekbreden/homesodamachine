# Linkage Arms (Left and Right) -- Spatial Resolution

All coordinates are in the **linkage arm local frame** unless explicitly stated otherwise. The left arm is the reference geometry; the right arm is its mirror. Every dimension is a concrete number. No downstream trigonometry or coordinate transforms are required.

---

## 1. System-Level Placement

```
Part: Linkage arm (left, reference; right is mirror)
Parent: Pump cartridge (bottom shell)
Position: mid-height outer corridor of the left pump bay, running the
          full depth of the cartridge interior from the front zone to the
          rear zone. The arm sits on the groove band thickening top surface
          at shell Z = 17.25, inside a guide channel bounded by the side
          wall and an inner rib.
Orientation: no rotation -- arm X/Y/Z axes align with bottom shell
             width/depth/height axes.
Motion: translates +Y (toward rear wall) by up to 3.0mm during
        squeeze action, then returns via spring force transmitted
        through the release plate.
```

This section is context only. All geometry below is resolved in the arm's own local frame.

---

## 2. Part Reference Frame

```
Part: Linkage arm (left)
  Origin: front-left-bottom corner of the bar body
  X: width (left to right), 0..6.0mm
  Y: length (front to back), 0..154.4mm
  Z: thickness (bottom to top), 0..3.0mm
  Print orientation: flat on build plate, 6mm face (XY plane) down.
    Layers stack through the 3mm thickness (Z direction).
  Installed orientation: identical to part frame (no rotation),
    translated to mid-height outer corridor of left pump bay.
```

Conventions:
- Arm front face at Y = 0, arm rear face at Y = 154.4.
- Arm left face at X = 0, arm right face at X = 6.0.
- Arm bottom face at Z = 0, arm top face at Z = 3.0.
- Front pin extends upward from the top face (+Z) near the front end.
- Rear pin extends rearward from the rear face (+Y) at the rear end.

---

## 3. Derived Geometry

### 3a. Bar Body Envelope

| Parameter | Value |
|-----------|-------|
| Width (X) | 6.0mm |
| Length (Y) | 154.4mm |
| Thickness (Z) | 3.0mm |
| X range (arm local) | 0 to 6.0 |
| Y range (arm local) | 0 to 154.4 |
| Z range (arm local) | 0 to 3.0 |

**Length derivation:** The arm body spans from just behind the front wall interior to the release plate's front face at rest. The front pin center Y is at arm local Y = 3.0 (see Section 3b), allowing 3.0mm of arm material in front of the pin. The rear face must align with the release plate socket opening at shell Y = 157.2. In arm local: 157.2 - 2.8 = 154.4. Total arm body length: 154.4mm.

**Width derivation:** The concept specifies 6mm width. The arm runs in a 7.0mm-wide guide channel (bottom shell left channel X = 2.0 to 9.0), providing 0.5mm clearance per side.

**Thickness derivation:** The concept specifies 3mm thickness. The arm sits on the groove band thickening top surface (shell Z = 17.25) and rises to shell Z = 20.25, flush with the channel top and inner rib top.

**Channel fit verification:**

| Dimension | Arm | Channel | Clearance per side |
|-----------|-----|---------|-------------------|
| Width (X) | 6.0mm | 7.0mm | 0.5mm |
| Height (Z) | 3.0mm | 3.0mm (shell Z = 17.25 to Z = 20.25) | 0mm (constrained from above by rib top / channel top) |

The arm slides freely fore-and-aft (Y) within the channel with 0.5mm lateral clearance. Vertical constraint is provided by the groove band thickening surface below and the channel top (rib top at Z = 20.25) above.

---

### 3b. Front Pin (Z-Axis, Vertical)

The front pin is a 3.0mm-diameter cylinder extending upward from the arm body's top face. It press-fits into the finger plate's left tab socket.

| Parameter | Value (arm local) | Value (bottom shell frame) |
|-----------|-------------------|---------------------------|
| Pin center X | 3.0 | 5.5 |
| Pin center Y | 3.0 | 5.8 |
| Pin base Z (on arm top face) | 3.0 | 20.25 |
| Pin tip Z | 8.0 | 25.25 |
| Pin diameter | 3.0mm | |
| Pin height | 5.0mm | |
| Pin axis | +Z (upward) | |

**Position derivation:**

- X: Pin centered in arm width: 6.0 / 2 = 3.0 arm local. In shell: 2.5 + 3.0 = 5.5. This matches the finger plate left socket center X in shell frame (5.5).
- Y: The finger plate left socket center Y in shell frame is 5.8. In arm local: 5.8 - 2.8 = 3.0. The pin is 3.0mm from the arm front face, leaving 3.0mm of arm material in front of the pin (arm front face to pin leading edge: 3.0 - 1.5 = 1.5mm; adequate).
- Z: Pin base at arm top face Z = 3.0. Pin extends 5mm upward to Z = 8.0. In shell frame: 17.25 + 8.0 = 25.25, matching the finger plate socket opening at shell Z = 25.25.

**Mating interface:**

| Parameter | Arm (pin) | Finger plate (socket) |
|-----------|-----------|----------------------|
| Diameter | 3.0mm (+ 0.1mm oversize in X for FDM oval compensation) | 3.1mm |
| Engagement | 5.0mm pin into 5.0mm deep socket | |
| Press-fit clearance | 0.1mm diametral (nominal) | |
| Axis | Z | Z |

---

### 3c. Rear Pin (Y-Axis, Rearward)

The rear pin is a 3.0mm-diameter cylinder extending rearward from the arm body's rear face. It press-fits into the release plate's left tab socket.

| Parameter | Value (arm local) | Value (bottom shell frame) |
|-----------|-------------------|---------------------------|
| Pin center X | 3.0 | 5.5 |
| Pin center Z | 1.5 | 18.75 |
| Pin base Y (on arm rear face) | 154.4 | 157.2 |
| Pin tip Y | 158.4 | 161.2 |
| Pin diameter | 3.0mm | |
| Pin length | 4.0mm | |
| Pin axis | +Y (rearward) | |

**Position derivation:**

- X: Pin centered in arm width: 3.0 arm local = shell 5.5. The release plate socket center X in shell frame is 14.9 per the release plate spatial document. **DESIGN GAP: X mismatch.** The arm is constrained to the guide channel centered at shell X = 5.5. The release plate socket is centered in the tab at shell X = 14.9. These are 9.4mm apart. The arm pin at X = 5.5 cannot reach a socket at X = 14.9. The release plate tab extends to shell X = 5.5 at its tip (plate local X = -18.8). The socket should be near the tab tip, not the tab center. The socket center X must be at shell X = 5.5 (with adequate wall material on both sides of the bore: tab extends from 5.5 to 24.3 shell, so 18.8mm of material behind the socket). This requires updating the release plate spatial document to move the socket center X from plate local -9.4 to approximately plate local -17.25 (shell X = 7.05) or ideally at the point that aligns with the arm. Given the 3.1mm socket diameter (1.55mm radius) and a minimum 1.2mm structural wall, the socket center must be at least 2.75mm from the tab tip: -18.8 + 2.75 = -16.05 plate local = 8.25 shell. The arm pin at 5.5 does not align with this minimum-wall position (8.25). The tab must be extended by 2.75mm (to plate local X = -21.55, shell X = 2.75) to place the socket at shell X = 5.5 with 2.75mm wall material from the tip. **For the purposes of this document, the rear pin X = 5.5 shell is used, assuming the release plate tab and socket will be corrected to align.**
- Z: Pin at arm center height: 3.0 / 2 = 1.5 arm local. In shell: 17.25 + 1.5 = 18.75. The release plate socket center Z in shell frame is 18.75 (tab center, matching channel center Z). Confirmed alignment.
- Y: Pin base at arm rear face Y = 154.4. In shell: 2.8 + 154.4 = 157.2. This matches the release plate socket opening Y at rest (release plate front face at shell Y = 157.2). Pin extends 4.0mm rearward to arm local Y = 158.4 (shell Y = 161.2), entering the 4.0mm deep socket in the release plate tab.

**Mating interface:**

| Parameter | Arm (pin) | Release plate (socket) |
|-----------|-----------|----------------------------------|
| Diameter | 3.0mm (+ 0.1mm oversize in Y for FDM oval compensation) | 3.1mm |
| Engagement | 4.0mm pin into 4.0mm deep socket | |
| Press-fit clearance | 0.1mm diametral (nominal) | |
| Axis | Y | Y |

**Socket wall adequacy (assuming corrected release plate tab):**

| Direction | Socket dia | Tab dimension | Wall per side |
|-----------|------------|---------------|---------------|
| X (inboard of socket) | 3.1mm | Tab extends 18.8mm inboard from tip to body | >15mm |
| Z | 3.1mm | 5.0mm tab height | (5.0 - 3.1) / 2 = 0.95mm |
| Y (behind socket) | -- | 5.0mm tab depth - 4.0mm socket = 1.0mm | 1.0mm |

All walls above 0.8mm minimum. The 0.95mm cross-section walls are above the structural minimum for the primarily axial (Y) load path through the pin.

---

### 3d. Partition Notch Clearance

The arm passes through the mounting partition at Y = 72.3 to 77.7 in the bottom shell frame (arm local Y = 69.5 to 74.9). The partition has an 8mm wide x 5mm tall notch at each outer corner at mid-height (shell Z = 15.25 to 20.25, updated from floor level).

| Parameter | Value (arm local) | Value (bottom shell frame) |
|-----------|-------------------|---------------------------|
| Arm at partition Y range | Y = 69.5 to 74.9 | Y = 72.3 to 77.7 |
| Arm cross-section at this Y | 6.0mm W x 3.0mm H | |
| Notch width (X direction) | 8.0mm | |
| Notch height (Z direction) | 5.0mm (shell Z = 15.25 to Z = 20.25) | |
| Arm in notch (X) | 6.0mm in 8.0mm notch | 1.0mm clearance per side |
| Arm in notch (Z) | 3.0mm (shell Z = 17.25 to 20.25) in 5.0mm notch (Z = 15.25 to 20.25) | 2.0mm below arm, 0mm above (arm top flush with notch top) |

The arm passes through the partition notch with 1.0mm lateral clearance per side and 2.0mm vertical clearance below. The arm top face is flush with the notch top edge (both at shell Z = 20.25). The arm slides freely through the notch during the 3.0mm fore-aft travel.

---

### 3e. Arm Path Straightness Verification

The front pin center and rear pin center must be at the same X and Z positions for the arm to be a straight bar (no bends).

| Pin | Shell X | Shell Z |
|-----|---------|---------|
| Front pin center | 5.5 | 20.25 (pin base, on arm top face) |
| Rear pin center | 5.5 | 18.75 (arm center height) |

**X alignment:** Both pins at shell X = 5.5. The arm runs straight in X with no lateral offset. Confirmed: straight bar, no X-direction bend needed.

**Z positions:** The front pin BASE is at Z = 20.25 (arm top face); the pin center at this base is at Z = 20.25. The rear pin CENTER is at Z = 18.75 (arm center). These Z positions differ, but neither requires the arm body itself to bend:
- The arm body sits flat at Z = 17.25 to 20.25 throughout its full length.
- The front pin rises vertically from the top face at Z = 20.25.
- The rear pin extends rearward from the rear face at the body center Z = 18.75.

The arm body is a perfectly straight bar. The pins are perpendicular appendages at each end. No bends, offsets, or tapers in the bar body.

---

## 4. Interface Summary

### 4.1. Finger Plate Left Tab Socket (front end)

| Parameter | Value |
|-----------|-------|
| Mating part | Finger plate, left downward tab |
| Interface type | Pin-and-socket press-fit (arm pin into finger plate socket) |
| Pin center (arm local) | (3.0, 3.0, 3.0) at pin base; extends to Z = 8.0 |
| Pin center (shell frame) | (5.5, 5.8, 20.25) base to (5.5, 5.8, 25.25) tip |
| Socket center (shell frame) | (5.5, 5.8, 25.25) opening, Z-axis, 5.0mm deep upward |
| Pin diameter / socket diameter | 3.0mm / 3.1mm |
| Engagement depth | 5.0mm |
| Assembly direction | Pin inserts upward (+Z) into socket |

### 4.2. Release Plate Left Tab Socket (rear end)

| Parameter | Value |
|-----------|-------|
| Mating part | Release plate, left lateral tab |
| Interface type | Pin-and-socket press-fit (arm pin into release plate socket) |
| Pin center (arm local) | (3.0, 154.4, 1.5) at pin base; extends to Y = 158.4 |
| Pin center (shell frame) | (5.5, 157.2, 18.75) base to (5.5, 161.2, 18.75) tip |
| Socket center (shell frame) | (5.5, 157.2, 18.75) opening, Y-axis, 4.0mm deep rearward |
| Pin diameter / socket diameter | 3.0mm / 3.1mm |
| Engagement depth | 4.0mm |
| Assembly direction | Pin inserts rearward (+Y) into socket |
| **DESIGN GAP** | Release plate socket center X is currently at shell X = 14.9 (centered in tab). Must be corrected to shell X = 5.5 (at tab tip) to align with arm channel. Release plate tab must be extended ~2.75mm to provide structural wall around socket at this position. See Section 3c for details. |

### 4.3. Bottom Shell Guide Channel

| Parameter | Value |
|-----------|-------|
| Mating part | Bottom shell, left arm channel (mid-height) |
| Interface type | Sliding guide (lateral and vertical constraint, axial freedom) |
| Channel X range (shell frame) | X = 2.0 to 9.0 |
| Channel Z range (shell frame) | Z = 17.25 to 20.25 |
| Channel Y range (shell frame) | Y = 2.0 to 174.0 |
| Arm cross-section | 6.0mm W x 3.0mm H |
| Lateral clearance | 0.5mm per side |
| Vertical constraint (-Z) | Groove band thickening top surface at shell Z = 17.25 (X = 2.0 to 5.7 on left side) |
| Vertical constraint (+Z) | Channel top / rib top at shell Z = 20.25 |
| Arm travel in channel | 3.0mm in +Y direction |

### 4.4. Mounting Partition Notch

| Parameter | Value |
|-----------|-------|
| Mating part | Mounting partition, left outer-corner notch (mid-height) |
| Interface type | Pass-through clearance |
| Notch position (shell frame) | Y = 72.3 to 77.7, X = 2.0 to 10.0, Z = 15.25 to 20.25 |
| Arm at notch | 6.0mm W x 3.0mm H |
| X clearance | 1.0mm per side |
| Z clearance | 2.0mm below arm, 0mm above (flush) |

---

## 5. Right Arm (Mirror)

The right arm is the left arm mirrored about the cartridge centerline (shell X = 66.0).

| Feature | Left arm (shell frame) | Right arm (shell frame) |
|---------|----------------------|------------------------|
| Arm body X range | 2.5 to 8.5 | 123.5 to 129.5 |
| Arm body center X | 5.5 | 126.5 |
| Channel X range | 2.0 to 9.0 | 123.0 to 130.0 |
| Front pin center X | 5.5 | 126.5 |
| Rear pin center X | 5.5 | 126.5 |
| Finger plate socket X | 5.5 | 126.5 |
| Release plate socket X | 5.5 | 126.5 |

All Y and Z positions are identical. The right arm's rear pin extends in +Y (same direction as left arm), entering the release plate's right tab socket. Both arms are geometrically identical -- no mirror-specific features. Both the front pin (+Z axis) and rear pin (+Y axis) are symmetric about the arm's own centerline, so left and right arms are the SAME part, not mirror images.

---

## 6. Transform Summary

```
Left arm local frame -> Bottom shell frame:
  Rotation: identity (none)
  Translation: (+2.5, +2.8, +17.25)

  shell_X = arm_X + 2.5
  shell_Y = arm_Y + 2.8
  shell_Z = arm_Z + 17.25

Bottom shell frame -> Left arm local frame:
  Translation: (-2.5, -2.8, -17.25)

  arm_X = shell_X - 2.5
  arm_Y = shell_Y - 2.8
  arm_Z = shell_Z - 17.25
```

During operation at travel distance T (0 to 3.0mm):
```
shell_Y = arm_Y + 2.8 + T
```
X and Z transforms unchanged during operation.

**Verification (3 test points at rest, T = 0):**

| Test point | Arm local (X, Y, Z) | Bottom shell (X, Y, Z) | Round-trip | Match? |
|------------|---------------------|------------------------|------------|--------|
| Origin | (0, 0, 0) | (2.5, 2.8, 17.25) | (0, 0, 0) | Yes |
| Front pin base | (3.0, 3.0, 3.0) | (5.5, 5.8, 20.25) | (3.0, 3.0, 3.0) | Yes |
| Rear pin base | (3.0, 154.4, 1.5) | (5.5, 157.2, 18.75) | (3.0, 154.4, 1.5) | Yes |

**Verification at full travel (T = 3.0mm):**

| Test point | Arm local (X, Y, Z) | Bottom shell (X, Y, Z) | Notes |
|------------|---------------------|------------------------|-------|
| Front pin base | (3.0, 3.0, 3.0) | (5.5, 8.8, 20.25) | Pin moved 3mm rearward from rest |
| Rear pin tip | (3.0, 158.4, 1.5) | (5.5, 164.2, 18.75) | Pin tip at shell Y = 164.2 |

All test points self-consistent.

---

## 7. Dimension Summary Table

| Dimension | Value | Frame | Source |
|-----------|-------|-------|--------|
| Bar body width | 6.0mm | Arm X | Concept spec |
| Bar body length | 154.4mm | Arm Y | Derived from pin center-to-center + front material |
| Bar body thickness | 3.0mm | Arm Z | Concept spec |
| Front pin diameter | 3.0mm | -- | Concept spec |
| Front pin height | 5.0mm | Arm Z | Finger plate socket depth |
| Front pin center (arm local) | (3.0, 3.0, 3.0) base | -- | Derived from channel center and socket positions |
| Rear pin diameter | 3.0mm | -- | Concept spec |
| Rear pin length | 4.0mm | Arm Y | Release plate tab depth minus 1mm wall |
| Rear pin center (arm local) | (3.0, 154.4, 1.5) base | -- | Derived from socket position |
| Pin center-to-center (Y) | 151.4mm | Arm Y | 154.4 - 3.0 = 151.4 |
| Channel clearance (X) | 0.5mm per side | Shell X | 7.0mm channel, 6.0mm arm |
| Partition notch clearance (X) | 1.0mm per side | Shell X | 8.0mm notch, 6.0mm arm |
| Overall bounding box | 6.0 x 158.4 x 8.0 mm | Arm local | Body + front pin extends to Z = 8.0, rear pin to Y = 158.4 |

---

## 8. Design Gaps

### 8.1. Release plate socket X-position mismatch

The release plate spatial document places the left pin socket center at shell X = 14.9 (centered in the 18.8mm-long lateral tab). The arm is constrained to the guide channel centered at shell X = 5.5. The arm pin at X = 5.5 cannot reach a socket at X = 14.9.

**Required correction:** The release plate socket must be repositioned to the tab tip, at or near shell X = 5.5, to align with the arm channel. The tab must be extended approximately 2.75mm (from plate local X = -18.8 to approximately -21.55) to provide the minimum 1.2mm structural wall around the 3.1mm socket bore at the new position. The socket center Z (shell 18.75) and Y (shell 157.2 at rest) are correct and do not need updating.
