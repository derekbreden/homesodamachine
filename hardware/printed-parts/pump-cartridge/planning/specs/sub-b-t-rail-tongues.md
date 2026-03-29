# Parts Specification: Sub-B T-Rail Tongues

## 1. Overview

Sub-B consists of two T-profile rail tongues integrated into the outer side walls of the tray. They guide cartridge insertion and removal in the dock's mating C-channels and provide orientation keying through asymmetric vertical placement.

**Parent part:** Tray (Sub-A box shell)
**Operation:** Boolean UNION onto left and right outer side wall faces
**Material:** PETG (same as all tray geometry)
**Print orientation:** Open-top-up (XY plane on build plate, Z is build direction)

---

## 2. Mechanism Narrative

### What the user sees and touches

During insertion and removal, the user holds the front bezel. The T-rail tongues are visible as two narrow ribs running the full depth of the cartridge on its left and right sides. They are not a primary touch surface -- the user's palm contacts the front bezel, not the rails. However, the rails are the first features to engage the dock and the last to disengage, so the user feels their effect as the smooth, guided, single-axis sliding motion of the cartridge.

### What moves

The entire cartridge (tray + all attached sub-components) translates along the Y axis (depth axis) during insertion and removal. The dock is stationary. The T-rail tongues ride inside the dock's C-channel grooves.

### What converts the motion

There is no motion conversion. The user pushes the cartridge along Y; the tongues slide along Y inside the C-channels. The force path is direct: user hand -> front bezel -> tray body -> T-rail tongues -> C-channel groove walls (reaction forces in X and Z).

### What constrains each moving part

The T-rail tongues constrain the cartridge in X and Z while permitting translation in Y:

- **X constraint (lateral):** The tongue cap (6.0 mm Z extent, 2.0 mm X thickness) is captured behind the C-channel slot opening (3.6 mm Z opening). The cap cannot pass through the slot opening because the cap is 6.0 mm tall and the slot is only 3.6 mm tall. This prevents the cartridge from moving in X (left-right) once engaged.
- **Z constraint (vertical):** The cap flanges (1.5 mm overhang per side beyond the 3.0 mm stem) bear against the upper and lower cavity walls of the C-channel. The cavity width is 6.6 mm (cap 6.0 mm + 0.3 mm clearance per side), so the cartridge can shift at most 0.3 mm vertically before a flange contacts a cavity wall. This prevents the cartridge from moving in Z (up-down).
- **Y freedom (insertion axis):** The tongue cross-section is constant along Y, and the C-channel is a straight slot along Y. Nothing prevents Y translation -- this is the intended degree of freedom.

### What provides the return force

There is no return force mechanism in the rail system. The cartridge stays where the user places it along Y. End-of-travel positioning is provided by other features (the fitting press-fits and the dock end wall, not by Sub-B).

### What is the user's physical interaction

1. **Insertion:** The user aligns the cartridge with the dock opening. The asymmetric rail placement (left rail center at Z=54.0, right rail center at Z=18.0) means only the correct orientation allows the tongues to enter the C-channels. The user pushes the cartridge along Y (away from themselves) with their palm on the front bezel. The tongues slide into the C-channels with 0.3 mm clearance per side, providing a smooth, guided motion. There is no tactile click from the rails themselves -- the rails provide only the guided sliding feel.
2. **Removal:** The user squeezes the release mechanism (Sub-B is not involved in this), then pulls the cartridge toward themselves along Y. The tongues slide out of the C-channels. The cartridge exits the dock.

### Keying behavior

The left rail is centered at Z=54.0 mm and the right rail at Z=18.0 mm -- a 36.0 mm vertical offset. If the user attempts to insert the cartridge upside-down (Z flipped), the left tongue would be at Z=18.0 and the right at Z=54.0, which are the reversed positions. These do not align with the dock C-channels (left channel at Z=54.0, right channel at Z=18.0), so the tongues physically cannot enter the grooves. The cartridge is blocked at the dock entrance. The keying feature is the 36.0 mm asymmetric offset between the two rail center heights.

---

## 3. Constraint Chain

```
[User hand] -> [Front bezel: stationary relative to tray] -> [Tray body: translates along Y]
    -> [T-rail tongues: translate along Y inside C-channels] -> [Dock C-channels: stationary]
         ^ X constrained by: cap captured behind slot opening (cap 6.0 mm > slot 3.6 mm)
         ^ Z constrained by: cap flanges vs cavity walls (0.3 mm clearance per side)
         ^ Y: free (constant cross-section along Y, straight channel along Y)
         ^ Keying: left rail Z=54.0, right rail Z=18.0 (36.0 mm asymmetric offset)
```

---

## 4. Coordinate System

All coordinates are in the tray frame:

```
Origin: rear-left-bottom corner of the tray outer envelope
X: width, 0 (left wall outer face) .. 160 (right wall outer face)
Y: depth, 0 (dock-facing rear face) .. 155 (user-facing front edge)
Z: height, 0 (bottom of floor) .. 72 (top of side walls)
Print orientation: open top facing up, XY plane on build plate
```

---

## 5. Part Geometry

Sub-B consists of exactly two solid features (left tongue and right tongue), each defined as a constant T-profile cross-section extruded along Y. Both tongues are boolean-unioned to the tray body. They are NOT separate printed parts -- they are integral features of the single tray print.

### 5.1 T-Profile Cross-Section (both tongues share this profile)

| Parameter | Value | Notes |
|-----------|-------|-------|
| Cap width (Z extent) | 6.0 mm | The wider flange at the outer tip |
| Stem height (Z extent) | 3.0 mm | The narrow neck connecting cap to wall |
| Total protrusion from wall face (X) | 4.0 mm | How far the tongue sticks out from the side wall |
| Cap thickness (X extent) | 2.0 mm | Thickness of the cap portion in the protrusion direction |
| Stem depth (X extent) | 2.0 mm | Distance from wall face to where cap flanges begin |
| Cap flange overhang per side (Z) | 1.5 mm | (6.0 - 3.0) / 2; each flange extends 1.5 mm beyond the stem |

### 5.2 Left Tongue

The left tongue protrudes in the **-X direction** from the left wall outer face (X=0).

**XZ cross-section coordinate table (tray frame, constant along Y):**

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

**Profile path:** A -> B -> C -> D -> E -> F -> G -> H -> (closed by wall face at X=0)

**Key positions:**
- Cap center Z: 54.0 mm
- Stem center Z: 54.0 mm
- Cap Z range: 51.0 .. 57.0 mm
- Stem Z range: 52.5 .. 55.5 mm

**Wall contact surface (bonding strip):**
- Plane: X = 0.0 (left wall outer face)
- Z extent: 52.5 .. 55.5 mm (3.0 mm, matches stem height)
- Y extent: 0.0 .. 155.0 mm (full tray depth)
- Area: 3.0 x 155.0 = 465.0 mm^2

### 5.3 Right Tongue

The right tongue protrudes in the **+X direction** from the right wall outer face (X=160).

**XZ cross-section coordinate table (tray frame, constant along Y):**

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

**Profile path:** A -> B -> C -> D -> E -> F -> G -> H -> (closed by wall face at X=160)

**Key positions:**
- Cap center Z: 18.0 mm
- Stem center Z: 18.0 mm
- Cap Z range: 15.0 .. 21.0 mm
- Stem Z range: 16.5 .. 19.5 mm

**Wall contact surface (bonding strip):**
- Plane: X = 160.0 (right wall outer face)
- Z extent: 16.5 .. 19.5 mm (3.0 mm, matches stem height)
- Y extent: 0.0 .. 155.0 mm (full tray depth)
- Area: 3.0 x 155.0 = 465.0 mm^2

### 5.4 Extrusion (Y Extent)

Both tongues are extruded along Y:

| Parameter | Value |
|-----------|-------|
| Y start | 0.0 mm (flush with rear wall outer face) |
| Y end | 155.0 mm (flush with front edge of tray) |
| Extrusion length | 155.0 mm |

The front of the tray is open (no front wall), so the tongue extrusion terminates cleanly at Y=155. The rear face of each tongue is flush with the tray rear wall outer face at Y=0.

### 5.5 Printability: Cap Flange Overhangs

Each cap flange creates a horizontal overhang in the Z build direction. The overhang length is 1.5 mm (one flange overhang per side). At 1.5 mm, this is within the self-bridging capability of PETG on the Bambu H2C -- overhangs under 2 mm print without support on this printer/material combination per `hardware/requirements.md` (Bambu H2C specs: 0.1 mm minimum layer height, PETG supported material).

No 45-degree chamfer is added to the flange undersides. The 1.5 mm overhang is small enough that the printed edge will sag negligibly. If prototype prints show unacceptable sag, a 45-degree chamfer (0.5 mm x 0.5 mm triangle removed from each flange underside inner corner) can be added as a revision -- but this would reduce the effective flange overhang from 1.5 mm to 1.0 mm and correspondingly reduce the Z capture margin in the dock C-channel. This is a test-print decision, not a first-iteration change.

### 5.6 Junction Fillet

Per the tray decomposition document, a 1.0 mm fillet is applied at the junction between each T-rail cap and the side wall outer face. Specifically:

- **Left tongue:** 1.0 mm fillet at the edges where the cap meets the wall face at X=0, running along the full Y extent. Applied at points (0, Y, 51.0) to (0, Y, 52.5) bottom and (0, Y, 55.5) to (0, Y, 57.0) top -- i.e., at the two re-entrant corners where the cap flanges meet the wall plane.
- **Right tongue:** 1.0 mm fillet at the equivalent edges at X=160.

These fillets improve printability (reducing the sharp overhang angle at the wall-to-cap junction) and add stress relief at the highest-load point (the root where the tongue meets the wall).

---

## 6. Interface Specifications

### 6.1 Tongue-to-Wall Bond (Sub-B to Sub-A)

This is not a mechanical interface -- it is a boolean union. The tongue geometry is fused to the tray body as a single continuous solid during the CadQuery build sequence.

**Bond geometry:**
- Left: rectangular strip at X=0, Z=52.5..55.5, Y=0..155 (465 mm^2)
- Right: rectangular strip at X=160, Z=16.5..19.5, Y=0..155 (465 mm^2)

### 6.2 Tongue-to-Dock C-Channel (Sub-B to Dock)

This is the functional sliding interface. The tray tongue slides inside the dock C-channel during cartridge insertion/removal.

**Left rail interface:**

| Tray tongue feature | Tongue dimension | Dock channel dimension | Clearance per side | Source |
|---------------------|-----------------|----------------------|-------------------|--------|
| Cap width (Z) | 6.0 mm | Cavity width: 6.6 mm | 0.3 mm | Spatial doc Section 3.1 |
| Stem height (Z) | 3.0 mm | Slot opening: 3.6 mm | 0.3 mm | Spatial doc Section 3.1 |
| Total protrusion (X) | 4.0 mm | Channel depth: 4.3 mm | 0.3 mm (at tip) | Spatial doc Section 3.1 |
| Stem depth (X) | 2.0 mm | Slot depth behind opening: 2.3 mm | 0.3 mm | Spatial doc Section 3.1 |

**Right rail interface:** Identical dimensions, mirrored about the tray centerline (X=80).

**Dock channel Z positions (derived from tongue positions + 0.3 mm clearance):**

| Dock feature | Left channel | Right channel |
|-------------|-------------|--------------|
| Slot opening Z range | 52.2 .. 55.8 mm | 16.2 .. 19.8 mm |
| Cavity Z range | 50.7 .. 57.3 mm | 14.7 .. 21.3 mm |
| Channel depth (X) | 4.3 mm | 4.3 mm |

### 6.3 Total Tray Envelope With Tongues

The tongues extend the tray's X envelope:

| Parameter | Value |
|-----------|-------|
| Tray body X range | 0.0 .. 160.0 mm |
| Left tongue extends to | X = -4.0 mm |
| Right tongue extends to | X = 164.0 mm |
| Total X envelope | -4.0 .. 164.0 mm = 168.0 mm |

---

## 7. Keying Verification

| Insertion attempt | Left rail center Z | Right rail center Z | Dock left channel Z | Dock right channel Z | Result |
|---|---|---|---|---|---|
| Correct orientation | 54.0 | 18.0 | 54.0 | 18.0 | Matches. Cartridge enters. |
| Upside-down (Z' = 72 - Z) | 18.0 | 54.0 | 54.0 | 18.0 | Left tongue at 18 vs channel at 54: blocked. |
| Left-right swapped (X mirrored) | Right at 54 on left side, left at 18 on right side | -- | 54.0 | 18.0 | Would require 180-degree Y rotation, which also swaps front/rear: blocked by rail Y engagement direction. |

The 36.0 mm vertical offset between rail centers is the keying dimension. This offset is large relative to the cap width (6.0 mm) -- a misaligned tongue would need to be 36 mm away from its channel, making accidental insertion in the wrong orientation impossible.

---

## 8. Assembly Notes

The T-rail tongues are integral to the tray. There is no assembly step for Sub-B -- the tongues are printed as part of the tray in a single print operation.

**Build sequence position:** Step 2 (immediately after Sub-A box shell creation). The two T-profile solids are boolean-unioned to the left and right outer side wall faces.

**CadQuery construction approach:**
1. Define the T-profile as a closed wire in the XZ plane (8 points per tongue, as listed in Sections 5.2 and 5.3).
2. Extrude each wire 155.0 mm along Y.
3. Union each extruded solid to the tray body.
4. Apply 1.0 mm fillets at the cap-to-wall junction edges.

---

## 9. Design Gaps

None identified. Every behavioral claim in this document resolves to a named geometric feature with dimensions. The mechanism is a simple constant-cross-section extrusion with no moving parts within Sub-B itself (the motion is the entire cartridge translating in Y). The keying is verified by arithmetic. The clearances are specified per side from the spatial resolution document.
