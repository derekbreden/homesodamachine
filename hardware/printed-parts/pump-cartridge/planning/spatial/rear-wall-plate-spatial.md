# Rear Wall Plate -- Spatial Resolution

## 1. System-Level Placement

```
Part:        Rear Wall Plate (pump cartridge rear closure + JG fitting mount)
Parent:      Shell bottom rear pocket (and shell top matching pocket above seam)
Position:    Rear face of cartridge, Y = 0..15 in shell-bottom frame
Orientation: Axis-aligned with shell bottom (no rotation)
             Plate face normal is parallel to Y axis (depth axis)
```

The rear wall plate sits flat in the rectangular rear pocket of the shell bottom (and shell top above the seam). The plate's dock-facing face is coplanar with the shell rear exterior face at Y = 0. No angular transformation relative to the shell or enclosure.

---

## 2. Reference Frame

```
Part:   Rear Wall Plate
Origin: Lower-left corner of the DOCK-FACING face
        (the face that faces rearward / outward when installed,
         coplanar with shell rear face at Y = 0 in shell frame)

X:      Width (left to right), 0..147.8 mm
Z:      Height (bottom to top), 0..69.8 mm
Y:      Thickness (toward cartridge interior), 0..14.8 mm

Print orientation: Flat on build plate (dock-facing face DOWN on bed, Z = 0 on build plate)
                   JG pocket bores are vertical (along print Z)
                   Dock-facing surface gets smooth bed finish (pogo pad face)
Installed orientation: Rotated 90 degrees from print — plate stands vertical in the shell pocket
```

### 2.1 Frame relationship to shell-bottom frame

```
Transform: pure translation, no rotation

X_shell = X_plate + 13.1
Z_shell = Z_plate + 4.1
Y_shell = Y_plate + 0.1

Inverse:
X_plate = X_shell - 13.1
Z_plate = Z_shell - 4.1
Y_plate = Y_shell - 0.1
```

The 13.1 mm X offset accounts for the left lip (1 mm) plus 0.1 mm clearance inside the 148 mm pocket opening (pocket X = 13..161 in shell frame). The 4.1 mm Z offset accounts for the bottom lip (1 mm) plus 0.1 mm clearance inside the pocket opening (pocket Z = 4..74 spanning both shell halves). The 0.1 mm Y offset provides clearance from the rear exterior face.

---

## 3. Plate Outer Dimensions

All coordinates in rear-wall-plate frame unless stated otherwise.

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Width (X) | 147.8 mm | Shell pocket opening 148 mm minus 0.1 mm clearance per side |
| Height (Z) | 69.8 mm | Shell pocket opening 70 mm (Z = 4..74 in cartridge frame) minus 0.1 mm clearance per side |
| Thickness (Y) | 14.8 mm | Shell pocket depth 15 mm minus 0.1 mm clearance per side |

### 3.1 Width derivation

Shell pocket opening: X_shell = 13..161 (148 mm). Source: shell-bottom-spatial.md, Section 12.1.

Plate width: 148 - 2 x 0.1 = 147.8 mm. Clearance per side: 0.1 mm (snug fit per requirements.md for captured parts).

### 3.2 Height derivation

The plate spans both shell halves. Shell bottom pocket: Z_shell = 4..38 (34 mm). Shell top pocket: Z_shell = 39..74 (35 mm, with 1 mm lip at top). Total pocket opening: Z_shell = 4..74 = 70 mm.

Plate height: 70 - 2 x 0.1 = 69.8 mm.

Note: the shell seam at Z_shell = 39 crosses the plate at Z_plate = 39 - 4.1 = 34.9 mm. The plate is a single piece bridging both shell halves. During assembly, it is placed into the shell bottom pocket (standing 34.8 mm proud above the shell bottom rim) before the shell top is closed.

### 3.3 Thickness derivation

Shell pocket depth: Y_shell = 0..15 (15 mm). Source: shell-bottom-spatial.md, Section 12.1.

Plate thickness: 15 - 2 x 0.1 = 14.8 mm.

---

## 4. JG Fitting Pocket Positions (2 x 2 Grid)

### 4.1 Grid layout

The four John Guest PP0408W union fittings are arranged in a 2 x 2 grid centered on the plate. The grid is positioned in the gap between the two motor cylinders (which protrude rearward from the mounting plate and terminate near the plate interior face).

| Fitting | Column | Row | X_plate (mm) | Z_plate (mm) | Pump assignment |
|---------|--------|-----|-------------|-------------|-----------------|
| JG1 | Left | Upper | 61.4 | 47.4 | Pump 1 inlet |
| JG2 | Right | Upper | 86.4 | 47.4 | Pump 2 inlet |
| JG3 | Left | Lower | 61.4 | 22.4 | Pump 1 outlet |
| JG4 | Right | Lower | 86.4 | 22.4 | Pump 2 outlet |

Grid center: X_plate = 73.9, Z_plate = 34.9 (plate centroid).

| Grid parameter | Value | Derivation |
|----------------|-------|------------|
| Horizontal spacing (X) | 25.0 mm center-to-center | Concept architecture: ~25 mm |
| Vertical spacing (Z) | 25.0 mm center-to-center | Symmetric square grid |
| Left column X_plate | 73.9 - 12.5 = 61.4 mm | Center minus half spacing |
| Right column X_plate | 73.9 + 12.5 = 86.4 mm | Center plus half spacing |
| Upper row Z_plate | 34.9 + 12.5 = 47.4 mm | Center plus half spacing |
| Lower row Z_plate | 34.9 - 12.5 = 22.4 mm | Center minus half spacing |

### 4.2 Motor clearance verification

The JG fitting body-ends (15.10 mm OD) protrude from the plate interior face into the cartridge interior where the motor cylinders are located. The motors are ~35 mm diameter, centered on the pump axes.

Motor positions in plate frame:
- Pump 1 motor center: X_plate = 35.2, Z_plate = 36.2
- Pump 2 motor center: X_plate = 112.6, Z_plate = 36.2

(Derived: motor center X_shell = 48.3 -> X_plate = 48.3 - 13.1 = 35.2. Motor center Z_cartridge = 40.3 -> Z_plate = 40.3 - 4.1 = 36.2.)

Clearance check (2D distance in XZ plane between fitting center and nearest motor center, minus fitting body-end radius 7.55 mm minus motor radius 17.5 mm):

| Fitting | Nearest motor | 2D distance (mm) | Net clearance (mm) |
|---------|--------------|-------------------|---------------------|
| JG1 (61.4, 47.4) | Pump 1 (35.2, 36.2) | 28.5 | 3.5 |
| JG2 (86.4, 47.4) | Pump 2 (112.6, 36.2) | 28.5 | 3.5 |
| JG3 (61.4, 22.4) | Pump 1 (35.2, 36.2) | 29.6 | 4.6 |
| JG4 (86.4, 22.4) | Pump 2 (112.6, 36.2) | 29.6 | 4.6 |

All fittings clear the motor cylinders with at least 3.5 mm radial clearance in the XZ plane. The fitting body-ends protrude ~10.8 mm into the motor zone along Y (see Section 4.3), overlapping with the motor body in Y but not in XZ.

### 4.3 JG fitting axial position within plate

The JG PP0408W fitting has a barbell profile (caliper-verified geometry-description.md):
- Center body: 9.31 mm OD, 12.16 mm long
- Body-end sections: 15.10 mm OD, 12.08 mm long each
- Shoulders: flat annular faces at the transition between zones

The stepped bore captures the center body and provides clearance for the body-end shoulders.

| Bore zone | Y_plate range (mm) | Bore diameter (mm) | Length (mm) | Purpose |
|-----------|-------------------|-------------------|-------------|---------|
| Dock-side shoulder clearance | 0..1.32 | 15.5 | 1.32 | Clears 15.10 mm body-end OD (0.4 mm diametral clearance) |
| Press-fit zone | 1.32..13.48 | 9.5 | 12.16 | Grips 9.31 mm center body OD (0.19 mm interference fit) |
| Interior-side shoulder clearance | 13.48..14.8 | 15.5 | 1.32 | Clears 15.10 mm body-end OD |

Derivation of Y positions:
- Press-fit zone length = center body length = 12.16 mm
- Remaining plate thickness: 14.8 - 12.16 = 2.64 mm
- Split equally: 2.64 / 2 = 1.32 mm per side
- Fitting is centered in plate thickness

Body-end protrusion from plate faces:
- Each body-end is 12.08 mm long; only 1.32 mm sits in the shoulder clearance bore
- Protrusion = 12.08 - 1.32 = **10.76 mm** per side
- Dock-side protrusion: 10.76 mm beyond Y_plate = 0 (into dock space)
- Interior-side protrusion: 10.76 mm beyond Y_plate = 14.8 (into cartridge interior, reaching Y_shell = 15 + 10.76 = 25.76)

Collet positions (collets protrude from body-end faces):
- Dock-side collet tip (extended): 10.76 + 2.74 = 13.5 mm beyond dock face
- Dock-side collet tip (compressed): 10.76 + 1.4 = 12.16 mm beyond dock face
- Interior-side collet tip (extended): same protrusions from interior face

### 4.4 Dock-side chamfer for tube entry

Each JG fitting port on the dock-facing side needs a 1 mm x 45-degree chamfer at the bore entry (Y_plate = 0 face) to guide the dock tube stubs into the collet bore. The chamfer is on the 15.5 mm shoulder clearance bore, transitioning from the plate face to the bore wall.

---

## 5. Guide Pin Bore Positions

Two 3 mm steel dowel pins are press-fit into the rear wall plate. The release plate slides on these pins. Compression springs on the pins return the release plate to its rest (forward) position.

### 5.1 Pin positions

| Pin | X_plate (mm) | Z_plate (mm) | Derivation |
|-----|-------------|-------------|------------|
| Left | 25.0 | 34.9 | Symmetric about plate center X, at plate center Z |
| Right | 122.8 | 34.9 | Symmetric about plate center X, at plate center Z |

Horizontal spacing: 122.8 - 25.0 = 97.8 mm (wide spacing for release plate stability).

Pin Z_plate = 34.9 = plate center height. This maximizes the lever arm against release plate tilting in both Z directions.

Symmetry check: plate center X = 73.9. Left offset = 73.9 - 25.0 = 48.9. Right offset = 122.8 - 73.9 = 48.9. Symmetric.

### 5.2 Pin bore dimensions

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.1 mm (3 mm pin + 0.1 mm press-fit per requirements.md) |
| Bore depth | 10 mm (from interior face, Y_plate = 4.8..14.8) |
| Bore type | Blind hole from interior face (does not penetrate dock face) |

The bore enters from the interior face (Y_plate = 14.8) and extends 10 mm into the plate. The pin is pressed in from the interior side. The remaining 4.8 mm of plate thickness (Y_plate = 0..4.8) is solid behind the pin bore, providing structural backing.

### 5.3 Clearance to JG fittings

| Pin | Nearest JG fitting | 2D distance (mm) | Pin radius (mm) | Fitting bore radius (mm) | Net clearance (mm) |
|-----|-------------------|-------------------|-----------------|--------------------------|---------------------|
| Left (25.0, 34.9) | JG3 (61.4, 22.4) | 38.5 | 1.55 | 7.75 | 29.2 |
| Right (122.8, 34.9) | JG4 (86.4, 22.4) | 38.0 | 1.55 | 7.75 | 28.7 |

No interference. Generous clearance between guide pins and JG fitting bores.

---

## 6. Link Rod Pass-Through Positions

Two 3 mm steel link rods pass through the rear wall plate, connecting the release plate (rear) to the inset release panel (front). The rods slide freely through clearance holes in the plate.

### 6.1 Pass-through positions

| Rod | X_plate (mm) | Z_plate (mm) | Derivation |
|-----|-------------|-------------|------------|
| Left | 43.9 | 0.9 | X_shell = 57 -> 57 - 13.1 = 43.9; Z_shell = 5 -> 5 - 4.1 = 0.9 |
| Right | 103.9 | 0.9 | X_shell = 117 -> 117 - 13.1 = 103.9; Z_shell = 5 -> 5 - 4.1 = 0.9 |

Source: shell-bottom-spatial.md, Section 6.1 — link rod centers at X_shell = 57 and X_shell = 117, Z_shell = 5.

### 6.2 Pass-through bore dimensions

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.4 mm (3 mm rod + 0.2 mm clearance per side for sliding fit) |
| Bore type | Through-hole (full plate thickness, Y_plate = 0..14.8) |

The 0.2 mm per side clearance exceeds the 0.1 mm per side used in the guide bushings (which need tighter tolerance for guidance). These pass-throughs only need to allow the rod to pass freely without binding.

### 6.3 Position verification

The pass-through Z_plate = 0.9 is very close to the plate bottom edge (Z_plate = 0). The bore edge at Z_plate = 0.9 - 1.7 = -0.8 would extend below the plate. This is a problem.

**Correction:** The bore center must be at least 1.7 mm (bore radius) + 0.8 mm (minimum wall) = 2.5 mm from the plate bottom edge.

Revised positions:

| Rod | X_plate (mm) | Z_plate (mm) | Derivation |
|-----|-------------|-------------|------------|
| Left | 43.9 | 2.5 | Minimum distance from bottom edge for 3.4 mm bore with 0.8 mm wall |
| Right | 103.9 | 2.5 | Same |

In shell-bottom frame: Z_shell = 2.5 + 4.1 = 6.6.

**Interface note:** The shell bottom has link rod channels at Z_shell = 3..7 with rod center at Z_shell = 5. The plate pass-throughs at Z_shell = 6.6 are 1.6 mm above the channel rod center. The link rods will angle slightly upward as they pass through the plate — the 3.4 mm bore diameter accommodates this angular offset (1.6 mm offset over 14.8 mm plate thickness = 6.2 degrees, resulting in <0.3 mm lateral displacement at the bore entry, within the 0.4 mm diametral clearance).

Actually, this angular misalignment is undesirable. Let me reconsider.

**Alternative approach:** Use an oval/slotted pass-through instead of a round bore. The slot is elongated in Z to accommodate the rod center at Z_shell = 5 (where the bushings are) while maintaining minimum wall thickness.

**Revised pass-through geometry:**

| Parameter | Value |
|-----------|-------|
| Slot width (X) | 3.4 mm (same as bore diameter) |
| Slot height (Z) | 4.6 mm (Z_plate = 0.1..4.7, centered on the rod line at Z_plate = 0.9) |
| Slot type | Through-slot, full plate thickness |
| Minimum wall to bottom edge | 0.1 mm (Z_plate = 0..0.1 is solid) |

This is too thin. The bottom edge of the plate would have only 0.1 mm of material below the slot.

**Better solution:** Extend the slot to the plate bottom edge — make it an open-bottom notch rather than a closed bore. The rod passes through a U-shaped notch at the bottom edge of the plate.

**Final pass-through geometry:**

| Parameter | Value |
|-----------|-------|
| Notch center X_plate | 43.9 (left), 103.9 (right) |
| Notch width (X) | 3.4 mm |
| Notch height (Z) | From Z_plate = 0 (bottom edge) to Z_plate = 3.4 mm (semicircular top) |
| Notch center Z_plate | 0 (open at bottom edge, semicircular closure at top) |

The rod (at Z_shell = 5 = Z_plate = 0.9) passes through the notch with clearance above and open below. The notch top (Z_plate = 3.4) is above the rod top edge (Z_plate = 0.9 + 1.5 = 2.4), providing 1.0 mm of wall above the rod.

This eliminates the thin-wall problem. The plate simply has two U-notches at its bottom edge through which the link rods pass.

---

## 7. Pogo Contact Pad Positions

Four flat copper contact pads on the dock-facing face (Y_plate = 0) for blind-mate electrical connection with the dock pogo pin header.

### 7.1 Pad layout

| Pad | X_plate (mm) | Z_plate (mm) | Assignment |
|-----|-------------|-------------|------------|
| 1 | 66.3 | 8.0 | Pump 1 motor + |
| 2 | 71.4 | 8.0 | Pump 1 motor - |
| 3 | 76.4 | 8.0 | Pump 2 motor + |
| 4 | 81.5 | 8.0 | Pump 2 motor - |

Pad pitch: 5.08 mm (2 x 2.54 mm standard pitch).

| Parameter | Value |
|-----------|-------|
| Pad diameter | 4 mm |
| Pad surface | Y_plate = 0 (dock-facing face, smooth bed-printed surface) |
| Pad cluster center X_plate | 73.9 (plate center) |
| Pad cluster center Z_plate | 8.0 |
| Total cluster width | 4 pads x 5.08 mm pitch = 15.24 mm (from pad 1 center to pad 4 center) |
| Implementation | Small PCB fragment or copper tape squares epoxied into a shallow (0.5 mm) recess |

### 7.2 Clearance to JG fittings

Nearest JG fitting body-end protrusion on dock face: JG3 or JG4 at Z_plate = 22.4, body-end extends down to Z_plate = 22.4 - 7.55 = 14.85.

Pogo pad top edge: Z_plate = 8.0 + 2.0 = 10.0.

Clearance: 14.85 - 10.0 = **4.85 mm**. Sufficient — no interference between pogo pads and JG fitting body-ends.

### 7.3 Clearance to link rod notches

Link rod notches at X_plate = 43.9 and 103.9, Z_plate = 0..3.4.

Nearest pogo pad (pad 1) at X_plate = 66.3: distance to left notch center = 66.3 - 43.9 = 22.4 mm. No interference.

### 7.4 Wiring routing

Motor wires (22 AWG, ~150 mm) route from the pump motors along the bottom of the cartridge interior to the pogo pads on the rear wall plate. The wires enter the plate zone at the interior face (Y_plate = 14.8) and connect to the pads via through-plate channels or surface routing. Two small wire routing grooves (1.5 mm wide x 1.0 mm deep) on the interior face connect the wire entry points to the pad positions. The wires are soldered to the pads from the interior side.

---

## 8. Corner Snap Tab Engagement Positions

The shell bottom has 4 corner snap tabs that engage chamfered edges on the rear wall plate. The shell top has a matching set for the upper portion.

### 8.1 Snap tab engagement positions (shell bottom)

| Corner | X_plate (mm) | Z_plate (mm) | Shell-bottom X,Z | Tab width | Engagement |
|--------|-------------|-------------|-------------------|-----------|------------|
| Bottom-left | 2.9 | 2.9 | (16, 7) | 4 mm | Chamfered plate edge engages 1 mm tab |
| Bottom-right | 144.9 | 2.9 | (158, 7) | 4 mm | Same |
| Mid-left | 2.9 | 30.9 | (16, 35) | 4 mm | Same |
| Mid-right | 144.9 | 30.9 | (158, 35) | 4 mm | Same |

### 8.2 Snap tab engagement positions (shell top, projected)

The shell top will have matching snap tabs for the upper portion of the plate. By mirror symmetry about the seam (Z_plate = 34.9):

| Corner | X_plate (mm) | Z_plate (mm) | Projected shell-top X,Z | Tab width |
|--------|-------------|-------------|--------------------------|-----------|
| Mid-upper-left | 2.9 | 38.9 | (16, 43) | 4 mm |
| Mid-upper-right | 144.9 | 38.9 | (158, 43) | 4 mm |
| Top-left | 2.9 | 66.9 | (16, 71) | 4 mm |
| Top-right | 144.9 | 66.9 | (158, 71) | 4 mm |

Note: the shell top snap tab positions are projections from shell bottom symmetry. The shell top specification must confirm these positions.

### 8.3 Chamfer geometry on plate edges

Each snap tab engagement point on the plate has a 45-degree x 1 mm chamfer on the leading edge (the edge that faces the tab during insertion). The plate inserts from above (+Z in shell frame) during assembly, so the leading edges are the bottom edges in the Z direction.

| Feature | Dimension |
|---------|-----------|
| Chamfer angle | 45 degrees |
| Chamfer size | 1 mm |
| Chamfer location | Both Z-direction edges at each tab position (bottom edge for insertion, top edge for shell-top tabs) |
| Chamfer runs along | X direction (along the plate left/right edges), 6 mm length centered on each tab position |

---

## 9. Interior-Side Features

### 9.1 Guide pin boss protrusions

Each guide pin bore has a cylindrical boss protruding from the interior face to provide additional pin engagement length and clearance for the compression spring.

| Parameter | Value |
|-----------|-------|
| Boss OD | 6 mm |
| Boss protrusion from interior face | 3 mm (Y_plate = 14.8..17.8, protruding into cartridge interior) |
| Boss bore diameter | 3.1 mm (same as pin bore, continuous) |
| Spring seat | Flat annular face of boss end (6 mm OD, 3.1 mm ID) |

The compression spring (3 mm ID, 8 mm free length) sits on the boss face. The release plate's guide pin clearance holes slide over the bosses.

### 9.2 Collet access clearance

The interior-side body-ends of the JG fittings protrude 10.76 mm from the plate interior face. The release plate must translate along Y (toward the fittings) to push the collets. The release plate's starting position is determined by the guide pin springs (which push the plate away from the fittings).

Release plate rest position: approximately 3 mm forward of the fitting body-end faces (this is the spring-determined gap — the plate must travel 3 mm to contact and depress the collets).

---

## 10. Dock-Side Features

### 10.1 Tube stub entry clearance

Each JG fitting dock-side port protrudes 10.76 mm from the dock face plus collet protrusion (2.74 mm extended). The dock tube stubs (20 mm long, 1/4" OD) must align with and enter these ports during cartridge insertion.

The collet bore ID is 6.69 mm; the tube OD is 6.30 mm. The 0.39 mm clearance, combined with the rail alignment tolerance of 0.4 mm lateral, provides sufficient acceptance.

### 10.2 Pogo pad recesses

Four shallow recesses (4.5 mm diameter, 0.5 mm deep) at the pogo pad positions accept the copper pad inserts (PCB fragments or copper tape). The recess ensures the pad surface is flush with or 0.1 mm proud of the plate face, providing consistent contact with the pogo pins.

---

## 11. Interface Summary (Both Sides)

### 11.1 Shell bottom pocket interface

| Parameter | Shell bottom (pocket) | Rear wall plate | Clearance |
|-----------|----------------------|-----------------|-----------|
| Width (X) | 148 mm opening | 147.8 mm | 0.1 mm per side |
| Height (Z, shell bottom portion) | 34 mm (Z=4..38) | 69.8 mm full (34.8 mm in bottom half) | 0.1 mm per side |
| Thickness (Y) | 15 mm depth | 14.8 mm | 0.1 mm per side |
| Bottom lip | Z_shell = 3..4, 1 mm | Plate bottom at Z_shell = 4.1 | Retained by lip |
| Left lip | X_shell = 12..13, 1 mm | Plate left at X_shell = 13.1 | Retained by lip |
| Right lip | X_shell = 161..162, 1 mm | Plate right at X_shell = 160.9 | Retained by lip |
| Snap tabs (4x) | At (16,7), (158,7), (16,35), (158,35) in shell frame | Chamfered edges at (2.9,2.9), (144.9,2.9), (2.9,30.9), (144.9,30.9) in plate frame | 1 mm engagement |

### 11.2 Link rod interface

| Parameter | Shell bottom (bushings) | Rear wall plate (notches) |
|-----------|------------------------|--------------------------|
| Rod 1 X position | X_shell = 57 | X_plate = 43.9 (X_shell = 57.0) |
| Rod 2 X position | X_shell = 117 | X_plate = 103.9 (X_shell = 117.0) |
| Rod Z position | Z_shell = 5 | Notch bottom at Z_plate = 0 (Z_shell = 4.1), top at Z_plate = 3.4 (Z_shell = 7.5) |
| Feature type | 3.2 mm cylindrical bore | 3.4 mm wide U-notch, open at bottom edge |

### 11.3 Release plate interface

| Parameter | Rear wall plate | Release plate (mating) |
|-----------|----------------|----------------------|
| Guide pin 1 position | X_plate = 25.0, Z_plate = 34.9 | Clearance hole at matching position |
| Guide pin 2 position | X_plate = 122.8, Z_plate = 34.9 | Clearance hole at matching position |
| Pin diameter | 3 mm dowel, press-fit in 3.1 mm bore | 3.2 mm clearance hole (sliding fit) |
| Pin boss OD | 6 mm, protrudes 3 mm from interior face | Release plate hole clears 6 mm boss |
| Spring on each pin | 3 mm ID, 8 mm free length, seated on boss face | Spring pushes plate away from fittings |
| JG fitting body-ends | Protrude 10.76 mm from interior face at 4 locations | Release plate has 4 stepped bores aligned with fittings |

### 11.4 Dock pogo pin interface

| Parameter | Rear wall plate (pads) | Dock (pogo pins) |
|-----------|----------------------|------------------|
| Contact positions | X_plate = 66.3, 71.4, 76.4, 81.5 at Z_plate = 8.0 | Pogo pin header at matching positions |
| Pad diameter | 4 mm | Pogo pin tip ~1.5 mm |
| Pad surface | Y_plate = 0 (dock-facing face) | Pins protrude toward cartridge |
| Pad pitch | 5.08 mm | Header pitch: 5.08 mm |

---

## 12. Transform Summary

### 12.1 Rear wall plate frame to shell-bottom frame

```
Transform: pure translation (no rotation)

X_shell = X_plate + 13.1
Z_shell = Z_plate + 4.1
Y_shell = Y_plate + 0.1
```

### 12.2 Rear wall plate frame to full cartridge frame

```
Same as shell-bottom frame (the shell-bottom frame IS the cartridge frame for Z = 0..39,
and extends identically above the seam).

X_cartridge = X_plate + 13.1
Z_cartridge = Z_plate + 4.1
Y_cartridge = Y_plate + 0.1
```

### 12.3 Verification points

| Test point (plate frame) | Transformed (shell frame) | Expected | Pass? |
|--------------------------|--------------------------|----------|-------|
| Origin (0, 0, 0) | (13.1, 0.1, 4.1) | Inside pocket, near bottom-left-rear corner | Yes |
| Top-right-interior (147.8, 14.8, 69.8) | (160.9, 14.9, 73.9) | Near top-right of pocket, at pocket depth | Yes |
| JG1 center (61.4, 7.4, 47.4) | (74.5, 7.5, 51.5) | Between motors, upper half of cartridge | Yes |
| Guide pin left (25.0, 14.8, 34.9) | (38.1, 14.9, 39.0) | Interior face, near seam height, left of fittings | Yes |
| Rod 1 notch (43.9, 0, 0) | (57.0, 0.1, 4.1) | Bottom edge of plate at rod 1 X, near rear face | Yes |
| Pogo pad 1 (66.3, 0, 8.0) | (79.4, 0.1, 12.1) | Dock face, below fittings, near center | Yes |

### 12.4 Round-trip verification

Forward then inverse for JG1: (61.4, 7.4, 47.4) -> (74.5, 7.5, 51.5) -> (74.5-13.1, 7.5-0.1, 51.5-4.1) = (61.4, 7.4, 47.4). Correct.

Forward then inverse for guide pin right: (122.8, 14.8, 34.9) -> (135.9, 14.9, 39.0) -> (135.9-13.1, 14.9-0.1, 39.0-4.1) = (122.8, 14.8, 34.9). Correct.

Forward then inverse for origin: (0, 0, 0) -> (13.1, 0.1, 4.1) -> (0, 0, 0). Correct.

---

## 13. Complete Feature Position Table

All positions in rear-wall-plate frame. This table provides every coordinate a CadQuery agent needs.

| Feature | X_plate (mm) | Y_plate (mm) | Z_plate (mm) | Type | Size |
|---------|-------------|-------------|-------------|------|------|
| Plate body | 0..147.8 | 0..14.8 | 0..69.8 | Rectangular solid | 147.8 x 14.8 x 69.8 |
| JG1 pocket bore | 61.4 | 0..14.8 | 47.4 | Stepped through-bore | See Section 4.3 |
| JG2 pocket bore | 86.4 | 0..14.8 | 47.4 | Stepped through-bore | See Section 4.3 |
| JG3 pocket bore | 61.4 | 0..14.8 | 22.4 | Stepped through-bore | See Section 4.3 |
| JG4 pocket bore | 86.4 | 0..14.8 | 22.4 | Stepped through-bore | See Section 4.3 |
| Guide pin bore (left) | 25.0 | 4.8..14.8 | 34.9 | Blind bore from interior | 3.1 mm dia, 10 mm deep |
| Guide pin bore (right) | 122.8 | 4.8..14.8 | 34.9 | Blind bore from interior | 3.1 mm dia, 10 mm deep |
| Guide pin boss (left) | 25.0 | 14.8..17.8 | 34.9 | Cylindrical protrusion | 6 mm OD, 3 mm tall |
| Guide pin boss (right) | 122.8 | 14.8..17.8 | 34.9 | Cylindrical protrusion | 6 mm OD, 3 mm tall |
| Rod notch (left) | 43.9 | 0..14.8 | 0..3.4 | U-notch, open at bottom | 3.4 mm wide |
| Rod notch (right) | 103.9 | 0..14.8 | 0..3.4 | U-notch, open at bottom | 3.4 mm wide |
| Pogo pad 1 recess | 66.3 | 0 (surface) | 8.0 | Shallow recess | 4.5 mm dia, 0.5 mm deep |
| Pogo pad 2 recess | 71.4 | 0 (surface) | 8.0 | Shallow recess | 4.5 mm dia, 0.5 mm deep |
| Pogo pad 3 recess | 76.4 | 0 (surface) | 8.0 | Shallow recess | 4.5 mm dia, 0.5 mm deep |
| Pogo pad 4 recess | 81.5 | 0 (surface) | 8.0 | Shallow recess | 4.5 mm dia, 0.5 mm deep |
| Snap chamfer (BL) | 2.9 | -- | 2.9 | Edge chamfer | 45 deg x 1 mm |
| Snap chamfer (BR) | 144.9 | -- | 2.9 | Edge chamfer | 45 deg x 1 mm |
| Snap chamfer (ML) | 2.9 | -- | 30.9 | Edge chamfer | 45 deg x 1 mm |
| Snap chamfer (MR) | 144.9 | -- | 30.9 | Edge chamfer | 45 deg x 1 mm |
| Snap chamfer (MUL) | 2.9 | -- | 38.9 | Edge chamfer | 45 deg x 1 mm |
| Snap chamfer (MUR) | 144.9 | -- | 38.9 | Edge chamfer | 45 deg x 1 mm |
| Snap chamfer (TL) | 2.9 | -- | 66.9 | Edge chamfer | 45 deg x 1 mm |
| Snap chamfer (TR) | 144.9 | -- | 66.9 | Edge chamfer | 45 deg x 1 mm |
| Elephant's foot chamfer | All edges at Z_plate = 0 | -- | 0 | Edge chamfer | 0.3 mm x 45 deg |
| Exterior edge chamfer | All non-bottom exterior edges | -- | -- | Edge chamfer | 1 mm |
