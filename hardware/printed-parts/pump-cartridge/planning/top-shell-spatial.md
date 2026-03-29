# Top Shell -- Spatial Resolution

All coordinates are in the **top shell local frame** unless explicitly stated otherwise. Every dimension is a concrete number. No downstream trigonometry or coordinate transforms are required.

---

## 1. System-Level Placement

```
Mechanism: Pump cartridge
Parent: Enclosure interior (220mm W x 300mm D x 400mm H)
Position: front and bottom of the enclosure, cartridge front face flush
          with the dock opening, centered on enclosure width
Orientation: no rotation -- cartridge X/Y/Z axes align with enclosure
             width/depth/height axes
```

The top shell is the upper half of the pump cartridge. In assembly, it sits on top of the bottom shell at the horizontal parting line (assembly Z = 33.5). This section is context only. All geometry below is resolved in the top shell's own local frame.

---

## 2. Part Reference Frame

```
Part: Top shell
  Origin: front-left-bottom exterior corner (as printed)
  X: width (left to right), 0..131.4mm
  Y: depth (front to back), 0..176.4mm
  Z: height (bottom to top), 0..33.5mm
  Print orientation: open face up, ceiling on build plate
  Installed orientation: flipped 180 degrees about the X axis (or Y axis),
    then translated to sit on top of the bottom shell
```

Conventions:

- **The top shell prints upside down** relative to its assembled orientation. The ceiling (assembly top) is on the build plate (Z = 0 in print frame). The open face (assembly parting line) is at Z = 33.5 in print frame.
- Front face at Y = 0, rear face at Y = 176.4.
- Left exterior at X = 0, right exterior at X = 131.4.
- Ceiling exterior at Z = 0, open edge (parting line face) at Z = 33.5.
- All wall thicknesses measured inward from exterior faces.

**Exterior dimensions (0.3mm inset from bottom shell):**

The top shell outer dimensions are 131.4mm x 176.4mm x 33.5mm. This is 0.3mm smaller per side than the bottom shell (132.0mm x 177.0mm) in both X and Y. In assembly, the top shell's outer faces sit 0.3mm inward from the bottom shell's outer faces on all four vertical sides, creating a deliberate step at the parting line. The ceiling (top face in assembly, Z = 0 in print frame) is also 131.4mm x 176.4mm -- the inset is uniform over the full height.

**Assembly-to-print correspondence:**

| Assembly feature | Assembly Z | Print frame Z |
|-----------------|-----------|---------------|
| Ceiling (top face) | 67.0 | 0 (build plate) |
| Parting line (open face) | 33.5 | 33.5 |

| Assembly feature | Assembly X | Print frame X |
|-----------------|-----------|---------------|
| Left exterior | 0.3 | 0 |
| Right exterior | 131.7 | 131.4 |

| Assembly feature | Assembly Y | Print frame Y |
|-----------------|-----------|---------------|
| Front exterior | 0.3 | 0 |
| Rear exterior | 176.7 | 176.4 |

---

## 3. Derived Geometry

### 3a. Shell Envelope and Wall Thicknesses

**Exterior dimensions:**

| Face | Position (print frame) | Extent |
|------|----------------------|--------|
| Left | X = 0 | Full Y, full Z |
| Right | X = 131.4 | Full Y, full Z |
| Front | Y = 0 | Full X, full Z |
| Rear | Y = 176.4 | Full X, full Z |
| Ceiling (build plate) | Z = 0 | Full X, full Y |
| Open edge (parting line) | Z = 33.5 | -- |

**Wall thicknesses:**

| Wall | Outer face | Inner face | Thickness | Notes |
|------|-----------|------------|-----------|-------|
| Left side | X = 0 | X = 2.0 | 2.0mm | |
| Right side | X = 131.4 | X = 129.4 | 2.0mm | |
| Front | Y = 0 | Y = 2.0 | 2.0mm | Contains palm surface and finger plate slot |
| Rear | Y = 174.4 | Y = 176.4 | 2.0mm | Thinner than bottom shell rear wall (3.0mm); no press-fit bores, only enclosure function |
| Ceiling | Z = 0 | Z = 2.0 | 2.0mm | |

**Interior cavity dimensions:**

| Parameter | Value |
|-----------|-------|
| X range | X = 2.0 to X = 129.4 |
| Width | 127.4mm |
| Y range | Y = 2.0 to Y = 174.4 |
| Depth | 172.4mm |
| Z range | Z = 2.0 to Z = 33.5 |
| Height | 31.5mm |

**No center divider wall.** The top shell does not have an internal center divider. The bottom shell's center divider (at assembly X = 65.0 to 67.0) rises to the parting line (assembly Z = 33.5). The pump heads extend above the parting line into the top shell cavity and are free to occupy the full interior width minus the side walls. The ceiling provides enclosure, not bay separation.

**No groove band thickening.** The rail grooves are entirely in the bottom shell (centered at assembly Z = 15.0, well below the parting line at Z = 33.5). The top shell side walls are a uniform 2.0mm thick over their full height.

---

### 3b. Parting Line Interface

The open face of the top shell (Z = 33.5 in print frame) mates with the open face of the bottom shell (Z = 33.5 in bottom shell frame).

**Mating face perimeter:**

| Parameter | Top shell (print frame) | Bottom shell frame | Step |
|-----------|------------------------|--------------------|------|
| Left face | X = 0 | X = 0 | Top shell inset 0.3mm (top shell outer at assembly X = 0.3, bottom shell at assembly X = 0) |
| Right face | X = 131.4 | X = 132.0 | Same 0.3mm step |
| Front face | Y = 0 | Y = 0 | Top shell inset 0.3mm (top shell outer at assembly Y = 0.3, bottom shell at assembly Y = 0) |
| Rear face | Y = 176.4 | Y = 177.0 | Same 0.3mm step |

**Mating face contact:** The top shell's open edge perimeter (Z = 33.5 plane) rests on the bottom shell's open edge perimeter (Z = 33.5 plane). The contact occurs at the wall-thickness ring:

| Wall | Top shell contact zone | Bottom shell contact zone |
|------|----------------------|--------------------------|
| Left | X = 0 to 2.0, full Y | X = 0.3 to 2.0, full Y (overlap width: 1.7mm) |
| Right | X = 129.4 to 131.4, full Y | X = 130.0 to 131.7, full Y (overlap width: 1.4mm) |
| Front | Full X, Y = 0 to 2.0 | Full X, Y = 0.3 to 2.0 (overlap depth: 1.7mm) |
| Rear | Full X, Y = 174.4 to 176.4 | Full X, Y = 174.0 to 176.7 (overlap depth: 2.4mm) |

Note: The overlap widths differ because the top shell walls (2.0mm) are inset 0.3mm from the bottom shell walls. The bottom shell's left wall inner face is at X = 2.0; the top shell's left wall spans X = 0 to 2.0 in print frame, which maps to assembly X = 0.3 to 2.3. The wall-on-wall contact is from assembly X = 0.3 to X = 2.0 (1.7mm wide). The inner 0.3mm of the top shell wall (assembly X = 2.0 to 2.3) overhangs the bottom shell interior. This is where the snap-fit hooks are located.

---

### 3c. Snap-Fit Hook Positions

Cantilever hooks on the inner edges of the side and rear walls, matching catch ledges on the bottom shell. Each hook is a cantilever beam attached to the wall interior face, extending toward the open face (Z = 33.5 in print frame). The hook tip has a catch feature that engages the bottom shell's catch ledge.

**Hook geometry (all hooks identical):**

| Parameter | Value |
|-----------|-------|
| Cantilever length (Z direction) | 10.0mm |
| Beam thickness (perpendicular to wall) | 2.0mm |
| Beam width (along wall) | 8.0mm |
| Hook tip catch depth | 0.3mm (engages 0.3mm catch ledge on bottom shell) |
| Hook entry ramp angle | 30 degrees (from beam axis) |
| Root fillet radius | 1.0mm (at cantilever base, 0.5x beam thickness) |
| Hook base Z (print frame) | 23.5 (10mm from open face at Z = 33.5) |
| Hook tip Z (print frame) | 33.5 (flush with open face) |

**Hook orientation in print frame:** The cantilever beams extend from Z = 23.5 to Z = 33.5 along the wall inner face, rising toward the open top of the print. The hook catch feature at Z = 33.5 curls outward (toward the wall exterior). In assembly (flipped), the beams hang downward from assembly Z = 43.5 to Z = 33.5, and the catch curls outward to engage the bottom shell's catch ledges.

**Hook flex direction:** The hooks flex inward (toward the shell interior) during assembly. In print orientation, the flex direction is in the XY plane (perpendicular to Z / build direction). This is the correct orientation per manufacturing constraints: flex direction parallel to the build plate.

**Left wall hooks (5 hooks, flex in +X from wall inner face at X = 2.0):**

Hook beams protrude 2.0mm in the +X direction from the wall inner face at X = 2.0, spanning X = 2.0 to X = 4.0.

| # | Y center | Y extent | Matching bottom shell ledge |
|---|----------|----------|-----------------------------|
| L1 | 18.7 | 14.7 to 22.7 | Left wall L1 (Y = 15.0..23.0 in bottom shell frame) |
| L2 | 53.7 | 49.7 to 57.7 | Left wall L2 (Y = 50.0..58.0) |
| L3 | 88.7 | 84.7 to 92.7 | Left wall L3 (Y = 85.0..93.0) |
| L4 | 123.7 | 119.7 to 127.7 | Left wall L4 (Y = 120.0..128.0) |
| L5 | 158.7 | 154.7 to 162.7 | Left wall L5 (Y = 155.0..163.0) |

Y positions are offset -0.3mm from the bottom shell Y values due to the 0.3mm inset at the front face (bottom shell Y = 0 maps to top shell Y = -0.3, so bottom shell Y_feature - 0.3 = top shell Y_feature).

**Right wall hooks (5 hooks, flex in -X from wall inner face at X = 129.4):**

Hook beams protrude 2.0mm in the -X direction from the wall inner face at X = 129.4, spanning X = 127.4 to X = 129.4.

Same Y positions as left wall hooks.

**Front wall hooks -- DESIGN CONFLICT:**

The bottom shell has 4 catch ledges on the front wall (F1-F4) at X centers 18.0, 50.0, 82.0, 114.0 in bottom shell frame. All four positions fall within the finger plate slot X range (X = 5.2 to 126.2 in top shell frame; see Section 3d). The front wall material at these X positions has been removed by the slot opening (which extends from Z = 8.5 to Z = 33.5 in print frame). There is no solid front wall material at these locations to anchor cantilever hooks.

**Solid front wall zones available for hooks:**

| Zone | X range (top shell frame) | Width | Can host 8mm hook? |
|------|--------------------------|-------|---------------------|
| Left column | X = 0 to 5.2 | 5.2mm (minus 2.0mm wall = 3.2mm interior) | NO (too narrow for 8mm beam) |
| Right column | X = 126.2 to 131.4 | 5.2mm | NO |
| Lower strip (print frame Z = 0 to 8.5) | Full width, but below the hook Z range (Z = 23.5..33.5) | N/A | NO (wrong Z zone -- hooks need to reach the open face at Z = 33.5) |

**Resolution: The 4 front wall catch ledges on the bottom shell (F1-F4) cannot be engaged by hooks on the top shell.** The remaining 14 hooks (5 left + 5 right + 4 rear) provide clamping around 3 sides of the perimeter. The front edge is held by:

1. The two closest side wall hooks (L1 and R1 at Y_center = 18.7, approximately 19mm from the front face) provide clamping near the front corners.
2. The finger plate slot creates a mechanical interlock: the finger plate protrudes through the slot, and the slot edges constrain the top shell laterally at the front face.

**FLAGGED ISSUE for parts specification:** The bottom shell's 4 front wall catch ledges (F1-F4) should either be (a) removed from the bottom shell spec since they serve no function, or (b) the front wall geometry should be redesigned to provide hook anchor points (e.g., by adding internal hook bridges across the slot opening). This is a design decision for the parts specification step, not a spatial resolution issue. The spatial resolution documents the conflict and its cause.

**Rear wall hooks (4 hooks, flex in -Y from wall inner face at Y = 174.4):**

Hook beams protrude 2.0mm in the -Y direction from the wall inner face at Y = 174.4, spanning Y = 172.4 to Y = 174.4.

| # | X center | X extent | Matching bottom shell ledge |
|---|----------|----------|-----------------------------|
| R1 | 17.7 | 13.7 to 21.7 | Rear wall R1 (X = 14.0..22.0 in bottom shell frame) |
| R2 | 49.7 | 45.7 to 53.7 | Rear wall R2 (X = 46.0..54.0) |
| R3 | 81.7 | 77.7 to 85.7 | Rear wall R3 (X = 78.0..86.0) |
| R4 | 113.7 | 109.7 to 117.7 | Rear wall R4 (X = 110.0..118.0) |

X positions are offset -0.3mm from the bottom shell X values due to the 0.3mm inset at the left face.

**Total: 14 hooks** (5 left + 5 right + 4 rear), engaging 14 of the 18 catch ledges on the bottom shell. The 4 front wall catch ledges are unengaged (see flagged issue above).

---

### 3d. Front Wall -- Palm Surface and Finger Plate Slot

The front wall (Y = 0 to Y = 2.0 in print frame) contains two functional zones:

1. **Palm surface:** The solid portion of the front wall exterior. The user's palm rests here during the squeeze action.
2. **Finger plate slot:** A rectangular opening through the front wall, through which the finger plate protrudes.

**Front wall layout in print frame:**

In print frame, Z = 0 is the ceiling (assembly top) and Z = 33.5 is the open face (assembly parting line). The finger plate slot is at the TOP of the print (near Z = 33.5) because it is at the BOTTOM of the assembly (near the parting line at assembly Z = 33.5).

The palm surface is the lower portion of the front wall in print frame (corresponding to the upper portion in assembly -- the zone closer to the ceiling).

**Finger plate slot dimensions:**

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Slot width (X direction) | 121.0mm | 120mm finger plate + 0.5mm clearance per side |
| Slot height (Z direction in print frame) | 25.0mm | ~30mm finger plate minus the portion that sits behind the bottom shell front wall |
| Slot left edge X | 5.2 | (131.4 - 121.0) / 2 = 5.2 (centered on front wall) |
| Slot right edge X | 126.2 | 5.2 + 121.0 |
| Slot lower edge Z (print frame) | 8.5 | Palm surface zone below the slot in print frame |
| Slot upper edge Z (print frame) | 33.5 | Flush with open face / parting line |
| Slot depth (Y direction) | 2.0mm (full wall thickness, through-opening) | |

**Palm surface zone (solid front wall):**

| Parameter | Value |
|-----------|-------|
| Z range (print frame) | Z = 0 to Z = 8.5 |
| Corresponds to assembly | Z = 58.5 to Z = 67.0 (the uppermost 8.5mm of the top shell front face) |
| Width | Full 131.4mm |
| Plus side columns flanking the slot | X = 0..5.2 and X = 126.2..131.4, Z = 8.5..33.5 |

The palm surface consists of the continuous lower strip (print frame Z = 0 to 8.5) spanning the full width, plus the two vertical columns on each side of the slot extending from Z = 8.5 to Z = 33.5. This forms an inverted-U shape around the slot opening.

**Finger plate recess depth:**

| Parameter | Value |
|-----------|-------|
| Palm surface plane | Y = 0 (front wall exterior) |
| Finger plate surface plane | Y = 3.0 (3mm recessed from palm surface) |
| Recess is formed by | The 2mm front wall thickness + 1mm of the interior cavity behind the wall |

The 3mm recess accommodates the finger plate (4mm thick) with its front face at Y = 3.0 from the top shell exterior, and its back face at Y = 7.0. The finger plate's 2-4mm squeeze travel occurs in the -Y direction (the finger plate and linkage arms pull rearward).

**Slot wall treatment:**

The slot edges have 0.5mm chamfers on the exterior face (Y = 0 side) to give a finished appearance. The slot side walls (the 5.2mm wide columns on each side) are structural -- they carry no squeeze load but maintain the visual frame of the palm surface around the finger plate recess.

**Surface texture:**

| Zone | Texture |
|------|---------|
| Palm surface (Z = 0 to 8.5, full width; plus flanking columns) | Crosshatch, 0.2mm deep, 1mm pitch |
| Slot interior walls | Smooth (no texture in the sliding clearance zone) |

---

### 3e. Mounting Partition Capture Slots

Two slots in the ceiling and/or side walls capture the top edges of the mounting partition when the shell is closed. These must match the bottom shell's partition slot Y positions.

**Slot Y position derivation:**

Bottom shell partition slots are at Y = 72.3 to Y = 77.7 in bottom shell frame. The partition sits at a fixed assembly Y position. The bottom shell frame and assembly frame share the same Y origin. The top shell frame Y origin is offset +0.3mm from the assembly Y origin (top shell print Y = 0 corresponds to assembly Y = 0.3). Therefore: top shell Y = assembly Y - 0.3 = bottom shell Y - 0.3.

| Parameter | Value (top shell print frame) |
|-----------|-------------------------------|
| Slot center Y | 74.7 |
| Slot front edge Y | 72.0 |
| Slot rear edge Y | 77.4 |
| Slot width (Y) | 5.4mm (matching bottom shell: 5.0mm partition + 0.2mm clearance per side) |

**Left wall slot:**

| Parameter | Value |
|-----------|-------|
| Slot X range | X = 0 to X = 2.0 (2.0mm deep, through full wall thickness from interior face) |
| Slot Y range | Y = 72.0 to Y = 77.4 |
| Slot Z range | Z = 2.0 to Z = 33.5 (from ceiling interior to open face) |
| Function | Captures top-left edge of mounting partition. Partition's top registration tab engages this slot when the top shell closes. |

**Right wall slot:**

| Parameter | Value |
|-----------|-------|
| Slot X range | X = 129.4 to X = 131.4 |
| Slot Y range | Y = 72.0 to Y = 77.4 |
| Slot Z range | Z = 2.0 to Z = 33.5 |
| Function | Captures top-right edge of mounting partition. Mirror of left slot. |

**Ceiling slots (alternative implementation):**

If the partition's top registration tabs are horizontal (protruding in +/-X into the side walls), the side wall slots above are correct. If the tabs protrude upward (+Z in assembly), the ceiling needs matching slots:

| Parameter | Value |
|-----------|-------|
| Slot X range (left) | X = 2.0 to X = 4.0 (2mm deep into ceiling from interior face) |
| Slot X range (right) | X = 127.4 to X = 129.4 |
| Slot Y range | Y = 72.0 to Y = 77.4 |
| Slot Z range | Z = 0 to Z = 2.0 (in ceiling plate) |

The side wall slot implementation is preferred (matching the bottom shell design). The partition drops into the bottom shell slots from above, and the top shell side wall slots capture the partition top edge when the shell closes.

---

### 3f. Rear Wall Upper Portion and JG Fitting Clearance

The top shell's rear wall (Y = 174.4 to Y = 176.4, 2.0mm thick) sits above the bottom shell's rear wall (Y = 174.0 to Y = 177.0, 3.0mm thick) in assembly. The top shell rear wall is thinner and inset.

**JG fitting body end clearance:**

The upper JG fitting body ends (JG3 at X = 33.5, Z = 26.65 and JG4 at X = 98.5, Z = 26.65 in bottom shell frame) protrude 0.7mm above the bottom shell open edge (body end top Z = 34.2 in bottom shell frame, shell edge at Z = 33.5). In the top shell's assembled position, these body ends intrude into the top shell's interior cavity.

In top shell print frame, these protrusions appear near Z = 33.5 (the open face). The body ends are cylindrical with 15.10mm OD, protruding 0.7mm past the parting line into the top shell's interior.

**Clearance notches in the top shell interior (at the rear wall):**

The top shell rear wall interior face is at Y = 174.4 in print frame (assembly Y = 174.7). The bottom shell rear wall inner face is at Y = 174.0 in bottom shell frame (assembly Y = 174.0). The JG body ends protrude inboard from assembly Y = 174.0 to approximately Y = 161.9 (12.08mm body end). These body ends are entirely within the bottom shell's deeper rear zone (the top shell's rear wall is thinner and further forward in assembly). No conflict with the top shell rear wall.

The 0.7mm protrusion above the parting line IS a concern at the open face of the top shell. The body ends at the open face (Z = 33.5 in print frame, Z = 33.5 in assembly) protrude 0.7mm into the top shell interior.

**Required clearance features:**

Two semicircular clearance notches on the interior face of the top shell, at the rear wall / open face junction, to accommodate the upper JG body end protrusions.

| Parameter | Value (top shell print frame) |
|-----------|-------------------------------|
| Notch 1 center X | 33.2 (bottom shell X = 33.5 - 0.3) |
| Notch 2 center X | 98.2 (bottom shell X = 98.5 - 0.3) |
| Notch center Z | 33.5 (at the open face) |
| Notch diameter | 16.0mm (15.10mm body end OD + 0.9mm clearance) |
| Notch depth into ceiling | 0.7mm (from Z = 33.5 inward toward Z = 32.8) |
| Notch Y range | Y = 174.4 to Y = 176.4 (within rear wall thickness) |

These notches are semicircular reliefs in the top shell's interior at the rear wall zone, allowing the upper body end cylinders to fit without interference. The notches are only 0.7mm deep and do not penetrate the ceiling or exterior surfaces.

**Alternative: Full-width rear wall relief.** Instead of individual notches, the top shell rear wall could have a continuous 0.7mm step-down along its interior at the open face, running from X = 17 to X = 115 (covering both JG body end positions with margin). This is simpler to model and avoids the possibility of misaligned circular reliefs.

| Parameter | Value |
|-----------|-------|
| Relief X range | X = 17.0 to X = 115.0 |
| Relief Z range | Z = 32.8 to Z = 33.5 (0.7mm deep from open face) |
| Relief Y range | Y = 174.4 to Y = 176.4 (full rear wall interior) |

---

### 3g. Center Divider Clearance

The bottom shell has a center divider wall from X = 65.0 to X = 67.0 (bottom shell frame), which extends to Z = 33.5 (the parting line). In the top shell frame, this divider's position maps to X = 64.7 to X = 66.7. The top shell does not continue this divider. The pump heads extend above the parting line and the ceiling provides the enclosure. No matching feature is needed in the top shell at this location. However, the divider's top edge (Z = 33.5 in bottom shell) contacts the top shell's open face. The top shell's interior at Z = 33.5 must be flat and unobstructed at this X range to allow the divider to seat against it.

**Verification:** The top shell interior cavity extends from X = 2.0 to X = 129.4. The divider at X = 64.7 to 66.7 is well within this range. No conflict. The divider's top edge is at Z = 33.5 in bottom shell frame, which corresponds to the parting line (assembly Z = 33.5). In the top shell, this is the open face at Z = 33.5. The divider does NOT extend into the top shell interior or touch the ceiling. The top shell provides enclosure above the divider's top edge, but no structural contact with it. No feature is required in the top shell at this location.

---

## 4. Interface Summary

### 4.1. Bottom Shell (mating partner)

| Parameter | Top shell (print frame) | Bottom shell frame | Notes |
|-----------|------------------------|--------------------|-------|
| Mating face | Z = 33.5 (open face) | Z = 33.5 (open face) | Horizontal mating plane at assembly mid-height |
| Top shell outer perimeter | 131.4mm x 176.4mm | -- | 0.3mm inset from bottom shell 132.0 x 177.0 |
| Snap-fit hooks (14 active) | Section 3c: 5 left + 5 right + 4 rear | Engage 14 of 18 catch ledges (4 front wall ledges unengaged; see Section 3c flagged issue) |
| Partition capture slots (2) | Left: X = 0..2.0, Y = 72.0..77.4; Right: X = 129.4..131.4, Y = 72.0..77.4 | Align with bottom shell slots at Y = 72.3..77.7 |
| JG body end clearance | Continuous relief at rear wall, Z = 32.8..33.5, X = 17..115 | Upper body ends protrude 0.7mm above parting line at (33.5, 26.65) and (98.5, 26.65) in bottom shell frame |

### 4.2. Mounting Partition

| Parameter | Value (top shell print frame) |
|-----------|-------------------------------|
| Interface type | Capture slots in side walls |
| Left slot | X = 0..2.0, Y = 72.0..77.4, Z = 2.0..33.5 |
| Right slot | X = 129.4..131.4, Y = 72.0..77.4, Z = 2.0..33.5 |
| Slot width (Y) | 5.4mm |
| Slot depth (X) | 2.0mm |
| Mating feature on partition | Top edge registration tabs (2.0mm x 2.0mm) |

### 4.3. Finger Plate

| Parameter | Value (top shell print frame) |
|-----------|-------------------------------|
| Interface type | Rectangular slot in front wall (Y = 0 to Y = 2.0) |
| Slot X range | X = 5.2 to X = 126.2 |
| Slot Z range (print frame) | Z = 8.5 to Z = 33.5 |
| Slot width (X) | 121.0mm |
| Slot height (Z) | 25.0mm |
| Finger plate dimensions | ~120mm W x ~25mm H (visible through slot) x 4mm thick |
| Clearance | 0.5mm per side between finger plate edges and slot edges |
| Finger plate surface plane | Y = 3.0 from top shell front exterior (3mm recess) |
| Finger plate travel | 2-4mm in -Y direction (rearward) |

### 4.4. Pumps (indirect)

| Parameter | Value |
|-----------|-------|
| Interface type | No direct contact. Pumps mount to partition; pump heads extend into top shell cavity. |
| Pump head vertical extent above parting line | Pump center Z = 33.3 (bottom shell frame), head is 62.6mm square. Top of pump head at assembly Z ≈ 64.6. In top shell print frame, the pump head extends from Z = 33.5 (open face) to approximately Z = 2.4 (near ceiling). |
| Clearance from pump head to ceiling interior (Z = 2.0) | ~0.4mm |
| Clearance from pump head to side walls | Maintained by bottom shell bay width; no additional constraint from top shell |

### 4.5. Linkage Arms (indirect)

| Parameter | Value |
|-----------|-------|
| Interface type | No direct contact. Arms guided by bottom shell floor channels. |
| Front pin exits through | The gap between the top and bottom shell front walls at the finger plate slot zone. The finger plate connects to the arm pins at approximately Z = 2.0..5.0 (bottom shell frame), which is below the top shell entirely. The linkage arm pins connect to the finger plate, which then extends upward through the top shell slot. |

### 4.6. Dock (external)

| Parameter | Value |
|-----------|-------|
| Interface type | No direct contact. The bottom shell carries the rail grooves and dock interface. The top shell only provides the upper half of the cartridge exterior visible when docked. |

---

## 5. Transform Summary

The top shell prints upside down relative to its assembled orientation. The physical assembly operation is a 180-degree rotation about the Y axis (depth axis), which flips Z and swaps left/right (X). However, because the top shell is bilaterally symmetric about its X centerline (hooks and partition slots are all symmetric), the left-right swap produces identical geometry. The transform can therefore be expressed without an X inversion:

```
Top shell print frame -> Assembly frame (bottom shell frame):
  X_assembly = X_print + 0.3
  Y_assembly = Y_print + 0.3
  Z_assembly = 67.0 - Z_print
```

**Derivation:** The top shell at print Z = 0 (ceiling) maps to assembly Z = 67.0 (top of cartridge). Print Z = 33.5 (open face) maps to assembly Z = 33.5 (parting line). The X and Y axes shift by +0.3mm (the inset offset -- top shell print frame origin is at assembly X = 0.3, Y = 0.3). The X axis does not invert because the part is bilaterally symmetric in X; the physical left-right swap during the flip produces the same geometry.

**Verification with 3 test points:**

| Test point | Print frame (X, Y, Z) | Computed assembly (X, Y, Z) | Expected | Match? |
|------------|----------------------|-----------------------------|----------|--------|
| Origin (front-left ceiling corner) | (0, 0, 0) | (0.3, 0.3, 67.0) | Top shell front-left-top corner in assembly: X = 0.3 (inset), Y = 0.3 (inset), Z = 67.0 (top) | YES |
| Open face front-left corner | (0, 0, 33.5) | (0.3, 0.3, 33.5) | Parting line front-left at X = 0.3, Y = 0.3, Z = 33.5 | YES |
| Partition slot center (left wall) | (1.0, 74.7, 17.75) | (1.3, 75.0, 49.25) | Should align with bottom shell partition slot at assembly Y = 75.0 (bottom shell Y = 75.0). Slot is at assembly X = 1.3 (within left wall). | YES |

**Inverse transform:**

```
Assembly frame -> Top shell print frame:
  X_print = X_assembly - 0.3
  Y_print = Y_assembly - 0.3
  Z_print = 67.0 - Z_assembly
```

**Round-trip verification:**

| Start (print) | -> Assembly | -> Print (round-trip) | Match? |
|---------------|------------|----------------------|--------|
| (0, 0, 0) | (0.3, 0.3, 67.0) | (0, 0, 0) | YES |
| (65.7, 88.2, 16.75) | (66.0, 88.5, 50.25) | (65.7, 88.2, 16.75) | YES |
| (131.4, 176.4, 33.5) | (131.7, 176.7, 33.5) | (131.4, 176.4, 33.5) | YES |

Transform is self-consistent.

---

## 6. Additional Notes

### Print orientation rationale

The top shell prints with the ceiling on the build plate (open face up). This provides:
- Smoothest surface on the ceiling (the build-plate face), which is the cartridge top face in assembly.
- Front wall (palm surface) is a vertical surface in print -- natural FDM layer-line finish.
- Snap-fit hooks are cantilever beams extending upward from the side walls during printing. Their flex direction (inward/outward in XY) is parallel to the build plate. This is the correct orientation per manufacturing constraints for maximum fatigue life.
- The finger plate slot is a rectangular opening in the front wall near the top of the print. This is a simple cutout in a vertical wall with no overhang issues.

### Elephant's foot chamfer

The ceiling exterior (Z = 0, the build-plate face) should have a 0.3mm x 45-degree chamfer on its perimeter edges to prevent elephant's foot flaring. This chamfer is on the assembly top face, which is not visible when the cartridge is docked.

### Exterior fillets

All exterior edges carry 1.0mm radius fillets, matching the bottom shell. The parting line edge (Z = 33.5 in print frame) has a 1.0mm fillet on the exterior. Combined with the 0.3mm step from the bottom shell, this creates a smooth transition at the parting line.

### Side wall continuity at parting line

The top shell side walls (2.0mm thick, uniform) meet the bottom shell side walls (2.0mm nominal, 5.7mm at groove band). Since the groove band is entirely within the bottom shell (Z = 12.75 to 17.25 in bottom shell frame, well below the parting line at Z = 33.5), the side walls at the parting line are both 2.0mm thick. The 0.3mm inset of the top shell creates the visible step on the side face.
