# Top Shell -- Parts Specification

The top shell is the upper half of the pump cartridge enclosure. It contains the ceiling, upper side walls, the front wall (with the palm surface and finger plate slot), the rear wall (with JG body end clearance relief), snap-fit cantilever hooks on three sides, and mounting partition capture slots. Printed in PETG, open-face-up (ceiling on build plate).

---

## Coordinate System

Origin: front-left-bottom exterior corner (as printed).

- **X axis**: width (left to right), 0 at left exterior face, positive rightward. Total extent: 131.4 mm.
- **Y axis**: depth (front to back), 0 at front exterior face, positive rearward. Total extent: 176.4 mm.
- **Z axis**: height (bottom to top), 0 at ceiling exterior face (build plate), positive upward. Total extent: 33.5 mm.

Front face at Y = 0. Rear face at Y = 176.4. Left exterior at X = 0. Right exterior at X = 131.4. Ceiling exterior at Z = 0 (build plate face). Open edge (parting line) at Z = 33.5.

All wall thicknesses measured inward from exterior faces.

**Assembly relationship:** The top shell prints upside down relative to its installed orientation. The ceiling (Z = 0 in print frame) is the assembly top face at assembly Z = 67.0. The open face (Z = 33.5 in print frame) is the parting line at assembly Z = 33.5. Transform: X_assembly = X_print + 0.3, Y_assembly = Y_print + 0.3, Z_assembly = 67.0 - Z_print.

---

## Mechanism Narrative

### What the user sees and touches on the top shell

The top shell is the upper half of a smooth, matte black PETG box. When the cartridge is assembled and docked, the top shell forms the entire visible top face (the ceiling) and the upper portion of all four vertical faces. The user-visible surfaces of the top shell are:

- **Top face (ceiling):** A flat, featureless surface. This is the build-plate face during printing -- the smoothest surface on the part. It spans 131.4 mm x 176.4 mm. A 0.3 mm x 45-degree elephant's foot chamfer runs around the perimeter edge (Z = 0 plane) to prevent first-layer flare from creating a visible lip. When the cartridge is docked, this face is typically not visible (facing the dock ceiling), but when the cartridge is on a counter or being handled, this face is visible and must be clean.

- **Front face -- palm surface:** The solid portion of the front wall exterior above the finger plate slot. This is the most important user-contact surface on the entire cartridge. The user's palm presses here during the squeeze-to-release action. It consists of a continuous horizontal strip spanning the full 131.4 mm width from Z = 0 to Z = 8.5 in print frame (assembly Z = 58.5 to 67.0, the upper 8.5 mm of the front face), plus two vertical columns flanking the finger plate slot, each 5.2 mm wide, from Z = 8.5 to Z = 33.5 in print frame (assembly Z = 33.5 to 58.5). Together, these form an inverted-U shape framing the slot opening. The palm surface carries a crosshatch texture (0.2 mm deep, 1 mm pitch) that provides grip without looking industrial. The palm surface is a single, unbroken printed surface with no seams or fasteners. The crosshatch texture is produced by the slicer's infill pattern on the vertical front wall -- the layer lines create a natural horizontal texture, and the crosshatch is applied via a post-process texture or embossed directly in the model as a grid of 0.2 mm deep, 0.4 mm wide channels at 1 mm spacing.

- **Front face -- finger plate slot:** A rectangular opening through the front wall, 121.0 mm wide x 25.0 mm tall, centered horizontally. The finger plate protrudes through this opening, recessed 3.0 mm behind the palm surface plane. A 0.5 mm gap surrounds the finger plate on all four exposed edges within the slot, communicating that the finger plate moves. The slot edges have 0.5 mm chamfers on the exterior face for a finished appearance.

- **Side faces (left and right):** Flat vertical walls, each 2.0 mm thick, uniform over the full height. No rail grooves -- the grooves are entirely within the bottom shell. The horizontal parting line at the open edge (Z = 33.5 in print frame, assembly Z = 33.5) runs the full depth. The top shell side walls are inset 0.3 mm from the bottom shell side walls, creating a deliberate step at the parting line that reads as a design accent.

- **Rear face:** A flat wall, 2.0 mm thick, thinner than the bottom shell rear wall (3.0 mm). No press-fit bores, no blade terminal slots -- those are entirely in the bottom shell. The rear face is featureless except for the horizontal parting line. On the interior at the open face, a continuous clearance relief (Section 3g) accommodates the upper JG body ends that protrude 0.7 mm above the parting line, but this is invisible from the exterior.

All exterior edges carry 1.0 mm radius fillets, matching the bottom shell, giving the part a finished, handle-able quality.

### What moves

**Nothing on the top shell moves during operation.** The top shell is entirely stationary. It is a cosmetic and structural enclosure.

The top shell constrains the following moving and stationary parts:

- **Finger plate (1):** A separate PETG plate that translates 2-4 mm in the -Y direction (rearward) within the finger plate slot. The slot edges (5.2 mm wide columns on each side, plus the solid strip at the bottom of the slot in assembly) constrain the finger plate laterally (X) and vertically (Z) while permitting the -Y squeeze travel. The 0.5 mm clearance per side between the finger plate edges and slot edges allows free sliding motion. The finger plate does not directly contact the top shell except at the slot edges.

- **Mounting partition (1):** A stationary vertical plate captured in the side wall slots (Y = 72.0 to 77.4). The partition's top registration tabs engage these slots when the top shell closes, capturing the partition between the top and bottom shell. The partition does not move during operation.

### What constrains internal parts

The top shell provides:

1. **Enclosure and ceiling over both pump bays.** The ceiling interior face (Z = 2.0) sits approximately 0.4 mm above the top of the pump heads (pump head top at approximately Z = 2.4 in print frame). This gap prevents contact while ensuring the pump heads cannot shift vertically.

2. **Lateral constraint for the finger plate** via the slot side columns (X = 0 to 5.2 and X = 126.2 to 131.4), with 0.5 mm clearance per side on the 120 mm wide finger plate.

3. **Top capture for the mounting partition** via side wall slots (Section 3e). The partition is captured top and bottom when the shell is closed, preventing any tilt or shift.

4. **Snap-fit clamping of the bottom shell** via 14 cantilever hooks on three sides (Section 3c). The hooks engage 0.3 mm catch ledges on the bottom shell, pulling the two halves together and holding them closed.

### What provides the return force

Not applicable. The top shell has no springs or return mechanisms. It is a stationary enclosure. The return springs for the release plate mechanism are in the bottom shell.

### What is the user's physical interaction with the top shell

The user's palm contacts the palm surface (front wall exterior, the inverted-U zone around the finger plate slot) during the squeeze-to-release action. The palm pushes in the +Y direction (toward the rear). This force is reacted by the JG fitting retention in the rear wall -- the palm surface is rigidly connected through the top shell walls and the bottom shell structure to the rear wall where the fittings hold the cartridge to the dock tube stubs. The top shell does not deflect under palm load; the 2.0 mm PETG walls are stiff enough that 40-60 N of palm force produces negligible deflection over the 176.4 mm depth.

During cartridge handling (insertion and removal from the dock), the user grips the cartridge with their hand wrapping around the front. The palm rests on the top shell's palm surface; the fingers curl underneath to the finger plate. The top face and rear face are secondary contact surfaces during handling.

---

## Constraint Chain Diagram

```
[User palm: pushes +Y against palm surface (front wall exterior)]
    |
    | (palm force reacted by shell rigidity)
    v
[Top shell: stationary enclosure, rigidly connected to bottom shell]
    ^ connected to bottom shell by: 14 snap-fit hooks (3 sides)
    |
    | (rigid shell transfers force to bottom shell structure)
    v
[Bottom shell rear wall -> JG fittings -> dock tube stubs]
    = cartridge held in dock
```

Partition capture:
```
[Mounting partition top tabs]
    |
    | (tabs insert into side wall slots, Y = 72.0..77.4)
    v
[Top shell side wall slots: left X = 0..2.0, right X = 129.4..131.4]
    ^ constrained in X by: slot depth (2.0 mm into wall)
    ^ constrained in Y by: slot width (5.4 mm)
    ^ constrained in Z by: ceiling interior face (Z = 2.0) above, bottom shell floor below
```

Finger plate constraint:
```
[Finger plate: translates -Y, 2-4 mm]
    ^ constrained in X by: slot side columns (X = 5.2 and X = 126.2), 0.5 mm clearance per side
    ^ constrained in +Z by: slot lower edge (print Z = 8.5, assembly Z = 58.5)
    ^ constrained in -Z by: bottom shell front wall and open slot at parting line
    ^ unconstrained in -Y: finger plate slides rearward (the intended squeeze travel)
    ^ returned in +Y by: compression springs via linkage arms (spring force path through bottom shell)
```

---

## Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width) | 131.4 mm |
| Y extent (depth) | 176.4 mm |
| Z extent (height) | 33.5 mm |
| Material | PETG |
| Color | Matte black |
| Mass (estimated) | ~55-70 g (PETG, walls + ceiling, no infill in thin walls) |

---

## Feature List

### Region 1: Ceiling

#### 1.1 Ceiling Plate

| Parameter | Value |
|-----------|-------|
| Exterior face | Z = 0 (build plate face) |
| Interior face | Z = 2.0 |
| Thickness | 2.0 mm |
| X extent | X = 0 to X = 131.4 (full width) |
| Y extent | Y = 0 to Y = 176.4 (full depth) |
| Function | Structural top wall and cosmetic surface. Provides enclosure above both pump bays. The ceiling interior face (Z = 2.0) sits approximately 0.4 mm above the pump head tops, preventing vertical shift. Load path: palm force through front wall into ceiling, through side walls into bottom shell. |

### Region 2: Side Walls (Left and Right)

#### 2.1 Left Side Wall

| Parameter | Value |
|-----------|-------|
| Outer face | X = 0 |
| Inner face | X = 2.0 |
| Thickness | 2.0 mm (uniform over full height -- no groove band thickening) |
| Y extent | Y = 0 to Y = 176.4 |
| Z extent | Z = 0 to Z = 33.5 |
| Function | Structural side wall. Contains snap-fit hooks on inner face, mounting partition slot, and provides lateral enclosure. |

#### 2.2 Right Side Wall (mirror of left)

| Parameter | Value |
|-----------|-------|
| Outer face | X = 131.4 |
| Inner face | X = 129.4 |
| Thickness | 2.0 mm |
| Y extent | Y = 0 to Y = 176.4 |
| Z extent | Z = 0 to Z = 33.5 |

#### 2.3 Mounting Partition Capture Slots (x2)

Two vertical slots in the side walls capture the top edges of the mounting partition when the shell closes. These match the bottom shell's partition slot Y positions (offset by -0.3 mm for the inset).

**Left wall slot:**

| Parameter | Value |
|-----------|-------|
| Slot X range | X = 0 to X = 2.0 (2.0 mm deep, through full wall thickness from interior face) |
| Slot Y range | Y = 72.0 to Y = 77.4 |
| Slot width (Y) | 5.4 mm (5.0 mm partition + 0.2 mm clearance per side) |
| Slot Z range | Z = 2.0 to Z = 33.5 (from ceiling interior to open face) |
| Function | Captures top-left edge of mounting partition. The partition's top registration tab (2.0 mm x 2.0 mm) engages this slot when the top shell closes onto the bottom shell. |

**Right wall slot:**

| Parameter | Value |
|-----------|-------|
| Slot X range | X = 129.4 to X = 131.4 |
| Slot Y range | Y = 72.0 to Y = 77.4 |
| Slot width (Y) | 5.4 mm |
| Slot Z range | Z = 2.0 to Z = 33.5 |
| Function | Captures top-right edge of mounting partition. Mirror of left slot. |

**Interface alignment with bottom shell:** Bottom shell partition slots are at Y = 72.3 to Y = 77.7 in bottom shell frame. Top shell slots at Y = 72.0 to Y = 77.4 in print frame. In assembly: top shell Y = 72.0 + 0.3 = 72.3 to 77.7, matching the bottom shell slots exactly.

#### 2.4 Snap-Fit Cantilever Hooks -- Side Walls (5 per side, 10 total)

Cantilever hooks on the inner edges of both side walls, extending from the wall interior face toward the open face (Z = 33.5). Each hook is a cantilever beam that flexes inward (toward the shell interior) during assembly, snapping over the bottom shell's catch ledges.

**Hook geometry (all hooks identical):**

| Parameter | Value |
|-----------|-------|
| Cantilever length (Z direction) | 10.0 mm |
| Beam thickness (perpendicular to wall, toward interior) | 2.0 mm |
| Beam width (along wall, Y direction) | 8.0 mm |
| Hook tip catch depth | 0.3 mm (engages 0.3 mm catch ledge on bottom shell) |
| Hook entry ramp angle | 30 degrees from beam axis |
| Root fillet radius | 1.0 mm (at cantilever base where beam meets wall, 0.5x beam thickness) |
| Hook base Z (print frame) | 23.5 (10.0 mm from open face) |
| Hook tip Z (print frame) | 33.5 (flush with open face) |
| Beam attachment | Root at wall interior face, beam extends into interior cavity |
| Hook tip catch orientation | Curls outward (toward wall exterior) at Z = 33.5 |

**Hook flex direction:** Hooks flex inward (toward shell interior) in the XY plane during assembly. In print orientation, the flex is perpendicular to Z (parallel to build plate). This is the correct orientation per FDM manufacturing constraints: flex direction parallel to the build plate maximizes fatigue life because layer lines run along the beam length.

**Left wall hooks (5 hooks, beams protrude +X from inner face at X = 2.0):**

Beams span X = 2.0 to X = 4.0.

| # | Y center | Y extent | Matching bottom shell ledge |
|---|----------|----------|-----------------------------|
| L1 | 18.7 | 14.7 to 22.7 | Left wall L1 (Y = 15.0..23.0 in bottom shell frame) |
| L2 | 53.7 | 49.7 to 57.7 | Left wall L2 (Y = 50.0..58.0) |
| L3 | 88.7 | 84.7 to 92.7 | Left wall L3 (Y = 85.0..93.0) |
| L4 | 123.7 | 119.7 to 127.7 | Left wall L4 (Y = 120.0..128.0) |
| L5 | 158.7 | 154.7 to 162.7 | Left wall L5 (Y = 155.0..163.0) |

Y positions offset -0.3 mm from bottom shell Y values due to top shell 0.3 mm inset at the front face.

**Right wall hooks (5 hooks, beams protrude -X from inner face at X = 129.4):**

Beams span X = 127.4 to X = 129.4. Same Y positions as left wall hooks.

| # | Y center | Y extent | Matching bottom shell ledge |
|---|----------|----------|-----------------------------|
| R1 | 18.7 | 14.7 to 22.7 | Right wall R1 |
| R2 | 53.7 | 49.7 to 57.7 | Right wall R2 |
| R3 | 88.7 | 84.7 to 92.7 | Right wall R3 |
| R4 | 123.7 | 119.7 to 127.7 | Right wall R4 |
| R5 | 158.7 | 154.7 to 162.7 | Right wall R5 |

### Region 3: Rear Wall

#### 3.1 Rear Wall Plate

| Parameter | Value |
|-----------|-------|
| Outer face | Y = 176.4 |
| Inner face | Y = 174.4 |
| Thickness | 2.0 mm |
| X extent | X = 0 to X = 131.4 (full width) |
| Z extent | Z = 0 to Z = 33.5 (full height) |
| Function | Enclosure wall. Thinner than bottom shell rear wall (3.0 mm) because it carries no press-fit bores or tube retention load. Provides only enclosure and cosmetic exterior surface. |

#### 3.2 JG Fitting Body End Clearance Relief

The upper JG fitting body ends (JG3 and JG4) protrude 0.7 mm above the parting line (assembly Z = 33.5 to 34.2). These body ends intrude into the top shell interior at the open face. A continuous relief in the top shell interior accommodates them.

| Parameter | Value (print frame) |
|-----------|---------------------|
| Relief X range | X = 17.0 to X = 115.0 |
| Relief Z range | Z = 32.8 to Z = 33.5 (0.7 mm deep from open face) |
| Relief Y range | Y = 174.4 to Y = 176.4 (full rear wall interior thickness) |
| Relief depth from open face | 0.7 mm |
| Function | Provides clearance for the upper JG body end cylinders (15.10 mm OD at bottom shell X = 33.5 and X = 98.5, which map to top shell X = 33.2 and X = 98.2). The continuous relief is simpler than individual circular notches and avoids misalignment risk. |

**Body end positions within relief zone:**

| Body end | X center (print frame) | X extent (15.10 mm OD) | Within relief? |
|----------|----------------------|----------------------|----------------|
| JG3 upper | 33.2 | 25.65 to 40.75 | YES (17.0 to 115.0 covers both) |
| JG4 upper | 98.2 | 90.65 to 105.75 | YES |

#### 3.3 Snap-Fit Cantilever Hooks -- Rear Wall (4 hooks)

Hooks on the inner face of the rear wall, flexing in -Y (toward interior). Beams span Y = 172.4 to Y = 174.4.

| # | X center | X extent | Matching bottom shell ledge |
|---|----------|----------|-----------------------------|
| R1 | 17.7 | 13.7 to 21.7 | Rear wall R1 (X = 14.0..22.0 in bottom shell frame) |
| R2 | 49.7 | 45.7 to 53.7 | Rear wall R2 (X = 46.0..54.0) |
| R3 | 81.7 | 77.7 to 85.7 | Rear wall R3 (X = 78.0..86.0) |
| R4 | 113.7 | 109.7 to 117.7 | Rear wall R4 (X = 110.0..118.0) |

X positions offset -0.3 mm from bottom shell X values due to the 0.3 mm inset. Hook geometry identical to side wall hooks (10.0 mm cantilever, 2.0 mm thick, 8.0 mm wide, 0.3 mm catch depth, 30-degree entry ramp, 1.0 mm root fillet).

### Region 4: Front Wall

#### 4.1 Front Wall Plate

| Parameter | Value |
|-----------|-------|
| Outer face | Y = 0 |
| Inner face | Y = 2.0 |
| Thickness | 2.0 mm |
| X extent | X = 0 to X = 131.4 (full width) |
| Z extent | Z = 0 to Z = 33.5 (full height) |
| Function | Contains the palm surface (the primary user-contact surface) and the finger plate slot. The front wall is the most important exterior surface on the cartridge. |

#### 4.2 Finger Plate Slot

A rectangular through-opening in the front wall, through which the finger plate protrudes.

| Parameter | Value |
|-----------|-------|
| Slot width (X direction) | 121.0 mm |
| Slot height (Z direction, print frame) | 25.0 mm |
| Slot left edge X | 5.2 |
| Slot right edge X | 126.2 |
| Slot lower edge Z (print frame) | 8.5 |
| Slot upper edge Z (print frame) | 33.5 (flush with open face / parting line) |
| Slot depth (Y direction) | 2.0 mm (full wall thickness, through-opening) |
| Exterior edge chamfer | 0.5 mm x 45 degrees on all four exterior slot edges (at Y = 0 face) |
| Function | Allows finger plate to protrude through front wall. The finger plate surface sits 3.0 mm behind the palm surface plane (Y = 3.0 from front exterior). |

**Assembly correspondence:** In assembly, the slot lower edge (print Z = 8.5) maps to assembly Z = 58.5. The slot upper edge (print Z = 33.5) maps to assembly Z = 33.5 (the parting line). So in assembly, the slot spans from Z = 33.5 (bottom of the top shell at the parting line) to Z = 58.5, a 25.0 mm opening in the lower portion of the top shell's front face.

#### 4.3 Palm Surface Zone

The solid portions of the front wall that the user's palm contacts.

**Geometry:** An inverted-U shape around the finger plate slot:

| Zone | X range | Z range (print frame) | Assembly Z range | Function |
|------|---------|----------------------|-----------------|----------|
| Horizontal strip | 0 to 131.4 (full width) | 0 to 8.5 | 58.5 to 67.0 | Continuous strip above slot, full width |
| Left column | 0 to 5.2 | 8.5 to 33.5 | 33.5 to 58.5 | Left side of slot |
| Right column | 126.2 to 131.4 | 8.5 to 33.5 | 33.5 to 58.5 | Right side of slot |

| Parameter | Value |
|-----------|-------|
| Surface plane | Y = 0 (front wall exterior) |
| Surface texture | Crosshatch grip: 0.2 mm deep channels, 0.4 mm wide, 1.0 mm pitch, perpendicular to each other, embossed into front wall exterior |
| Texture extent | Full palm surface zone (horizontal strip + both columns) |
| Wall thickness behind palm surface | 2.0 mm (Y = 0 to Y = 2.0) |
| Function | Primary user-contact surface. User's palm pushes here (+Y) during squeeze-to-release. The rigid 2.0 mm PETG wall transmits force to the shell structure without deflection. |

#### 4.4 Front Wall -- No Snap-Fit Hooks

**The front wall has no snap-fit hooks.** The finger plate slot (X = 5.2 to 126.2, Z = 8.5 to 33.5 in print frame) removes the material where hooks would attach. The remaining solid front wall zones (the horizontal strip at Z = 0 to 8.5 and the two 5.2 mm wide columns) are either in the wrong Z range for hooks (hooks must reach the open face at Z = 33.5) or too narrow to host an 8.0 mm wide hook beam.

The 4 front wall catch ledges (F1-F4) on the bottom shell at X centers 18.0, 50.0, 82.0, 114.0 in bottom shell frame are unengaged. These ledges are non-functional but structurally harmless -- they are 0.3 mm protrusions on the bottom shell front wall interior, adding negligible material. They can remain in the bottom shell for now and be removed in a future revision to simplify that part.

**Front edge retention strategy:** The front edge of the top-shell-to-bottom-shell joint is held by:

1. Side wall hooks L1 and R1 (Y_center = 18.7, approximately 19 mm from front face), providing clamping near the front corners.
2. The finger plate slot creates a mechanical interlock: the finger plate protrudes through the slot, and the slot edges constrain the top shell laterally at the front face. The finger plate prevents the top shell front edge from lifting away from the bottom shell.

### Region 5: Internal Features

#### 5.1 Center Divider Clearance

The bottom shell's center divider wall (bottom shell X = 65.0 to 67.0, top shell X = 64.7 to 66.7) extends to the parting line at Z = 33.5. The divider top edge seats against the top shell's open face (Z = 33.5 in print frame). No matching feature is needed in the top shell -- the interior cavity at this X range is flat and unobstructed. The divider does not extend into the top shell interior or touch the ceiling. No feature required.

### Region 6: Exterior Edge Treatment

#### 6.1 Exterior Fillets

| Parameter | Value |
|-----------|-------|
| Radius | 1.0 mm |
| Applied to | All exterior edges of the top shell |
| Function | Eliminates sharp FDM edges. Gives finished, handle-able quality. Matches bottom shell treatment. Reduces stress concentrations at shell parting line. |

Specific fillet locations:
- All 12 edges of the rectangular box exterior (4 ceiling-to-wall edges, 4 wall-to-wall vertical corners, 4 open-face-to-wall edges)
- Finger plate slot exterior edges (0.5 mm chamfer specified separately in Section 4.2; the 1.0 mm fillet applies to the shell exterior corners, the 0.5 mm chamfer applies to the slot opening edges)

#### 6.2 Elephant's Foot Chamfer

| Parameter | Value |
|-----------|-------|
| Chamfer | 0.3 mm x 45 degrees |
| Location | Ceiling perimeter edge (Z = 0 plane, all four sides of the top face) |
| Function | Prevents elephant's foot flaring from bed adhesion on the first printed layer. The ceiling face (Z = 0) is the build-plate face. Without this chamfer, the first 0.2-0.3 mm flares outward, creating a visible lip on what should be a smooth top surface. In assembly, this chamfer is on the cartridge's top face -- not visible when docked but visible when handling the cartridge. |

---

## Assembly Sequence

The top shell has no internal sub-assembly. It is a single printed part. Its integration into the cartridge assembly is described here.

**Prerequisites:** All internal components are already loaded into the bottom shell per the bottom shell assembly sequence (Steps 1-9 in bottom-shell-parts.md).

**Step 1: Orient and align the top shell.**
Flip the top shell from its print orientation (open face up) to its assembly orientation (open face down, ceiling up). Align over the bottom shell, matching the 0.3 mm inset on all four sides.

**Step 2: Close the top shell onto the bottom shell.**
Press down. The 14 snap-fit cantilever hooks (5 left, 5 right, 4 rear) flex inward as the 30-degree entry ramps ride over the bottom shell's catch ledges. At full closure, the hooks snap past the ledges and the 0.3 mm catch depth locks the shells together. An audible click confirms engagement. The mounting partition top tabs engage the top shell's side wall slots. The finger plate protrudes through the finger plate slot.

**Disassembly:**
1. Insert a spudger or flat screwdriver at the rear face parting line (the rear face has no functional features that would be damaged by prying). Lever the top shell upward to disengage the rear wall hooks first, then work along the sides.
2. Lift the top shell off. All internal components remain in the bottom shell.

The snap-fit hooks can withstand at least 20-30 assembly/disassembly cycles before significant wear (PETG fatigue resistance with 0.3 mm deflection on a 10 mm cantilever at 5% max strain).

---

## Rubric Results

### Rubric A -- Mechanism Narrative

**Status: COMPLETE.** The mechanism narrative starts from the user-visible exterior (ceiling, palm surface, finger plate slot, side faces, rear face), describes what moves (nothing -- the top shell is stationary), what it constrains (finger plate laterally and vertically via slot edges, partition via side wall slots, pump heads vertically via ceiling clearance, bottom shell via snap-fit hooks), and the user's physical interaction (palm pushes +Y against the palm surface during squeeze). Every behavioral claim is grounded to a named feature with dimensions:

- "Palm pushes +Y" -- palm surface at Y = 0, 2.0 mm thick front wall
- "Finger plate constrained laterally" -- slot columns at X = 5.2 and X = 126.2, 0.5 mm clearance per side
- "Partition captured" -- side wall slots Y = 72.0 to 77.4, 5.4 mm wide, 2.0 mm deep
- "Pump heads cannot shift vertically" -- ceiling interior at Z = 2.0, pump head top at approximately Z = 2.4, 0.4 mm clearance
- "Snap-fit hooks hold shells together" -- 14 hooks, 0.3 mm catch depth, 10.0 mm cantilever, 30-degree entry ramp

### Rubric B -- Constraint Chain Diagram

**Status: COMPLETE.** See Constraint Chain Diagram section above. Three chains shown: (1) palm force through shell to dock, (2) partition capture, (3) finger plate constraint. All arrows labeled with force transmission mechanism. All parts list their constraints. No unlabeled arrows or unconstrained parts.

### Rubric C -- Direction Consistency Check

| # | Claim | Direction | Axis | Verified? | Notes |
|---|-------|-----------|------|-----------|-------|
| 1 | User's palm pushes toward rear wall | Toward rear | +Y | YES | Palm surface at Y = 0, force pushes +Y through shell to rear wall |
| 2 | Snap-fit hooks flex inward during assembly | Toward shell interior | Left: +X, Right: -X, Rear: -Y | YES | Left hooks at X = 2.0 flex +X; right at X = 129.4 flex -X; rear at Y = 174.4 flex -Y |
| 3 | Hook catch curls outward at tip | Toward wall exterior | Left: -X, Right: +X, Rear: +Y | YES | Catch at Z = 33.5 curls toward exterior to engage ledges on bottom shell |
| 4 | Finger plate translates rearward | Toward rear | -Y | YES | Finger plate slides from Y = 3.0 rearward during squeeze, slot permits -Y motion |
| 5 | Partition tabs insert into side wall slots | Into wall | Left: -X, Right: +X | YES | Left tab into slot at X = 0..2.0; right tab into slot at X = 129.4..131.4 |
| 6 | Top shell is inset 0.3 mm from bottom shell | Inward on all four vertical faces | +X on left, -X on right, +Y on front, -Y on rear | YES | Top shell 131.4 vs bottom 132.0 (0.3 mm per side in X); 176.4 vs 177.0 (0.3 mm per side in Y) |
| 7 | JG clearance relief accommodates body ends protruding above parting line | Body ends protrude upward from bottom shell | +Z in assembly = -Z in print frame | YES | Body ends at assembly Z = 34.2, relief at print Z = 32.8..33.5 (assembly Z = 33.5..34.2) |

No contradictions found. All directional claims are consistent with the coordinate system.

### Rubric D -- Interface Dimensional Consistency

| # | Interface | Part A (top shell) | Part B | Clearance | Source |
|---|-----------|-------------------|--------|-----------|--------|
| 1 | Parting line perimeter (top shell outer to bottom shell outer) | 131.4 x 176.4 mm | 132.0 x 177.0 mm | 0.3 mm per side (deliberate inset) | Spatial doc |
| 2 | Snap-fit hook catch / bottom shell ledge | Hook catch depth: 0.3 mm | Ledge protrusion: 0.3 mm, ledge height: 0.3 mm | 0 mm (designed interference for snap engagement) | Both spatial docs |
| 3 | Partition slot (top shell) / partition top tab | Slot width: 5.4 mm (Y) | Partition thickness: 5.0 mm | 0.2 mm per side (sliding fit) | Spatial doc; concept doc |
| 4 | Partition slot Y position / bottom shell slot Y position | Top shell: Y = 72.0..77.4 (assembly Y = 72.3..77.7) | Bottom shell: Y = 72.3..77.7 | 0 mm (aligned in assembly frame) | Both spatial docs |
| 5 | Finger plate slot width / finger plate width | Slot: 121.0 mm | Finger plate: ~120.0 mm | 0.5 mm per side | Spatial doc; concept doc |
| 6 | Finger plate slot height / finger plate height | Slot: 25.0 mm (Z = 8.5 to 33.5) | Finger plate visible height: ~25.0 mm | 0.5 mm clearance at top (palm strip side) | Spatial doc |
| 7 | JG clearance relief / upper body end protrusion | Relief: 0.7 mm deep (Z = 32.8..33.5), X = 17.0..115.0 | Body end: 15.10 mm OD, protrudes 0.7 mm above parting line | 0 mm at Z extent (relief exactly matches protrusion); lateral clearance: relief 98 mm wide, body ends each 15.1 mm OD at X = 33.2 and 98.2 | Spatial doc; bottom shell parts |
| 8 | Top shell wall overlap on bottom shell wall at parting line | Left wall: X = 0..2.0 (assembly X = 0.3..2.3) | Bottom shell left inner face: X = 2.0 | Overlap contact: assembly X = 0.3 to 2.0 (1.7 mm); inner 0.3 mm overhangs interior | Spatial doc |

No zero-clearance sliding interfaces. No mismatched dimensions. The snap-fit hook-to-ledge interface is designed zero-clearance (snap interference), which is intentional.

### Rubric E -- Assembly Feasibility Check

| Step | Physically feasible? | Notes |
|------|---------------------|-------|
| 1. Orient and align top shell | YES | The top shell is a rigid box. The 0.3 mm inset provides a natural alignment register -- the top shell nests inside the bottom shell perimeter. |
| 2. Close top shell | YES | 14 hooks around 3 sides engage simultaneously. The 30-degree entry ramps allow progressive engagement -- hooks do not require simultaneous snap. User presses down with both hands; hooks engage sequentially from the point of pressure outward. The partition slots receive the partition tabs passively as the shell closes. |

**Order dependencies:**
- Step 1 before Step 2 (must orient before closing).
- All bottom shell internal loading (Steps 1-9 in bottom shell spec) before Step 1 here.

**Trapped parts check:** After Step 2, the following are captured inside the closed shell: mounting partition (captured in slots), release plate (on JG collets), linkage arms (in floor channels, under pump heads), springs (between rear wall and release plate), pumps (on partition), BPT tubes (routed), blade terminal wiring. The finger plate protrudes through the slot and is accessible. All captured parts are intentionally inaccessible -- the cartridge is a sealed module.

**Disassembly:** Pry top shell at rear face (Step 2 reverse). Hooks flex inward to release. 20-30 cycle life on PETG hooks at 0.3 mm deflection. Developer can use a spudger at the rear face parting line where no functional features are at risk.

### Rubric F -- Part Count Minimization

| Part pair | Permanently joined? | Relative motion? | Same material? | Verdict |
|-----------|--------------------|--------------------|----------------|---------|
| Top shell + snap-fit hooks | YES (integral) | Hooks flex during assembly but do not translate | YES | Correct: one piece. Hooks are cantilever beams printed integrally with side/rear walls. |
| Top shell + bottom shell | NO (snap-fit, separable) | NO (stationary relative to each other in use) | YES | Must be separate for assembly access. Correct. |
| Top shell + finger plate | NO (finger plate passes through slot) | YES (finger plate translates 2-4 mm in -Y) | YES | Must be separate (relative motion). Correct. |
| Top shell + mounting partition | NO (partition captured in slots) | NO | YES | Could theoretically combine, but partition must be installed into bottom shell before top shell closes. Combining would prevent assembly. Correct as separate. |

No parts can be combined. No parts are unnecessarily separate. Part count for the top shell alone: 1 printed part (all features integral).

### Rubric G -- FDM Printability

**Step 1 -- Print orientation.**

| Parameter | Value |
|-----------|-------|
| Print orientation | Open face up (ceiling on build plate, walls and hooks rise upward) |
| Build plate face | Z = 0 (ceiling exterior) |
| Rationale | Ceiling gets the smoothest surface (build-plate face) -- this is the cartridge's top face in assembly. Front wall (palm surface) prints as a vertical wall with natural layer-line finish. Snap-fit hooks are cantilever beams protruding from wall interior faces, rising upward with flex in XY plane (parallel to build plate) -- correct for maximum fatigue life per manufacturing constraints. Finger plate slot is a rectangular cutout in a vertical wall -- no overhang. |
| Build plate footprint | 131.4 mm x 176.4 mm (well within 325 x 320 mm bed) |

**Step 2 -- Overhang audit.**

| # | Surface / Feature | Angle from horizontal | Printable? | Resolution |
|---|-------------------|----------------------|------------|------------|
| 1 | Ceiling plate (Z = 0) | 0 deg (horizontal, on build plate) | OK | Build plate face |
| 2 | Left side wall (vertical, X = 0 plane) | 90 deg | OK | Vertical wall |
| 3 | Right side wall (vertical, X = 131.4 plane) | 90 deg | OK | Vertical wall |
| 4 | Front wall (vertical, Y = 0 plane) | 90 deg | OK | Vertical wall |
| 5 | Rear wall (vertical, Y = 176.4 plane) | 90 deg | OK | Vertical wall |
| 6 | Finger plate slot edges (vertical cutout in vertical wall) | 90 deg | OK | Slot is a rectangular opening -- just an absence of wall material |
| 7 | Snap-fit hook cantilever beams (protrude from wall inner face, extend in +Z) | 90 deg (vertical beams on vertical walls) | OK | Beams rise vertically from wall face. The root fillet (1.0 mm) transitions smoothly from wall to beam. |
| 8 | Hook entry ramp (30 deg from beam axis) | 60 deg from horizontal | OK | Above 45 deg threshold |
| 9 | Hook catch undercut (horizontal ledge curling outward at beam tip) | 0 deg (horizontal overhang) | RESOLVED | The catch is a 0.3 mm horizontal protrusion at the tip of the beam (Z = 33.5). At this location (the top of the print, the open face), the catch protrudes outward into open air -- there is nothing above it to overhang from. The catch is at the very top of the print, so it is the last layer printed on the beam. No overhang support needed. The catch is formed by widening the last 0.3 mm of beam perimeter outward. |
| 10 | Root fillet at hook base (1.0 mm radius) | Curved, minimum ~45 deg | OK | 1.0 mm radius fillet at the junction of beam and wall. The fillet is concave (transitioning from vertical wall to vertical beam) -- no overhang. |
| 11 | JG clearance relief (Z = 32.8 to 33.5 at rear wall interior) | Horizontal ceiling at Z = 32.8 over a 0.7 mm deep recess | OK | The relief is a 0.7 mm step-down at the very top of the print (open face). It is a horizontal ledge at Z = 32.8 spanning from Y = 174.4 to Y = 176.4 (2.0 mm span in Y) over the X range 17.0 to 115.0. The overhang is only 2.0 mm deep (the rear wall thickness) -- well under bridge limits. In practice, this is the last 3-4 layers being slightly inset at the rear wall, forming a shallow shelf. |
| 12 | Exterior fillets (1.0 mm radius on all edges) | Varies, minimum 45 deg on concave fillets | OK | Convex fillets on exterior edges create slight overhangs at the transition, but 1.0 mm radius fillets at 45 deg minimum are within FDM capability. The slicer resolves these as gradual perimeter offsets. |
| 13 | Partition capture slots (vertical slots through side walls) | 90 deg (vertical cuts in vertical walls) | OK | Simple rectangular channels through the wall, no overhang |
| 14 | Elephant's foot chamfer on ceiling perimeter | 45 deg | OK | Chamfer angle is exactly 45 deg from horizontal |

No unresolved overhangs. No supports required.

**Step 3 -- Wall thickness check.**

| Feature | Thickness | Minimum required | Status |
|---------|-----------|-----------------|--------|
| Left/right side walls | 2.0 mm | 1.2 mm (structural) | OK |
| Front wall | 2.0 mm | 0.8 mm (standard; structural where it bears palm load) | OK |
| Rear wall | 2.0 mm | 0.8 mm (standard; no structural load) | OK |
| Ceiling plate | 2.0 mm | 1.2 mm (structural) | OK |
| Slot side columns (flanking finger plate slot) | 5.2 mm (X extent, minus 2.0 mm wall = 3.2 mm interior face to slot edge) | 0.8 mm (standard) | OK |
| Snap-fit hook beam thickness | 2.0 mm | 1.2 mm (structural -- flexing feature) | OK |
| Snap-fit hook beam width | 8.0 mm | 0.8 mm (standard) | OK |
| Hook catch protrusion | 0.3 mm | 0.4 mm (minimum printable feature) | **BORDERLINE** -- Same as bottom shell catch ledge issue. The 0.3 mm catch protrusion at the hook tip is a step on an existing beam face, not a freestanding feature. The slicer will widen the last layer's perimeter by 0.3 mm. Acceptable in practice. Verify with test print. If unreliable, increase to 0.4 mm and update bottom shell catch ledge to 0.4 mm to match. |
| Root fillet radius | 1.0 mm | N/A (fillet, not a wall) | OK |

**Step 4 -- Bridge span check.**

| Feature | Span | Limit (15 mm) | Status |
|---------|------|---------------|--------|
| JG clearance relief ceiling (Y span at Z = 32.8) | 2.0 mm (rear wall thickness) | 15 mm | OK |

No bridge spans exceed 15 mm.

**Step 5 -- Layer strength check.**

| Feature | Load direction | Layer orientation | Status |
|---------|---------------|-------------------|--------|
| Snap-fit hooks (flex inward during assembly) | Flex in XY plane (perpendicular to beam, toward interior) | Layers stack in Z; flex is in XY (parallel to layers) | OK -- correct orientation for maximum fatigue life. Layers run along beam length. |
| Front wall (palm surface, bears +Y palm load) | +Y (into wall face) | Layers stack in Z; force is in Y (parallel to layers) | OK -- load in layer plane |
| Side walls (bear snap-fit hook reaction forces) | Hook reaction in X (perpendicular to wall) | Layers stack in Z; reaction in X (across layers) | OK -- compression loads across layers are well-handled |
| Ceiling (bears hook clamping load) | Z (compression from snap-fit hook engagement) | Layers stack in Z | OK -- compression loads across layers are well-handled by PETG |

No critical layer strength conflicts.

---

## Design Gaps Summary

1. **DESIGN GAP (MINOR): Hook catch and bottom shell ledge protrusion (0.3 mm) are below the minimum printable feature size (0.4 mm).** Both the hook catch on the top shell and the matching ledge on the bottom shell are 0.3 mm protrusions. These are steps on existing surfaces, not freestanding features, so they print as perimeter width changes rather than independent features. Expected to work in practice. **Action: Verify with a test print of a snap-fit sample (shell joint section with one hook and one ledge). If the 0.3 mm features do not engage reliably, increase both to 0.4 mm. This change must be coordinated between the top shell hook geometry and the bottom shell catch ledge geometry.**

2. **DESIGN GAP (MINOR): Bottom shell front wall catch ledges (F1-F4) are non-functional.** The top shell cannot engage them because the finger plate slot removes the front wall material at those positions. The ledges are structurally harmless 0.3 mm protrusions on the bottom shell. **Action: Accept as non-functional for now. Remove from bottom shell in a future revision to simplify the part. The 14 active hooks on 3 sides provide sufficient clamping.**

3. **DESIGN GAP (MINOR): Pump head to ceiling clearance is approximately 0.4 mm.** The ceiling interior face is at Z = 2.0 in print frame. The pump head top is at approximately Z = 2.4 (pump center at assembly Z = 33.3 = print Z = 33.7, head is 62.6 mm square, top at assembly Z = 64.6 = print Z = 2.4). The 0.4 mm clearance is tight but intentional -- it prevents vertical shift without contacting the pump. **Action: Verify with physical pump measurement. If the pump head extends higher than expected, the ceiling thickness could be reduced locally (from 2.0 mm to 1.5 mm in the pump head zone) or the cartridge height increased. This is a cross-part dimension that depends on caliper verification of the Kamoer pump head height.**

---

## Grounding Rule Verification

Every behavioral claim in this document has been traced to a named geometric feature with dimensions:

| Claim | Grounding feature | Dimensions |
|-------|-------------------|------------|
| "Palm surface is a single, unbroken surface" | Front wall exterior, inverted-U zone around slot | Full width strip Z = 0..8.5 plus columns X = 0..5.2 and X = 126.2..131.4 from Z = 8.5..33.5 |
| "Crosshatch texture provides grip" | Embossed grid on palm surface | 0.2 mm deep, 0.4 mm wide channels, 1.0 mm pitch |
| "Finger plate constrained laterally by slot edges" | Slot side columns | X = 5.2 and X = 126.2, slot 121.0 mm wide, plate ~120.0 mm wide, 0.5 mm clearance per side |
| "0.5 mm gap communicates that finger plate moves" | Slot-to-plate clearance | 0.5 mm on all four exposed edges |
| "Snap-fit hooks produce audible click" | 14 cantilever hooks, 0.3 mm catch depth | 10.0 mm beam, 2.0 mm thick, 30-degree entry ramp, engages 0.3 mm ledge on bottom shell |
| "Top shell inset 0.3 mm reads as design accent" | Outer perimeter difference | 131.4 vs 132.0 mm (X), 176.4 vs 177.0 mm (Y), 0.3 mm per side |
| "Partition captured top and bottom" | Side wall slots | Left: X = 0..2.0, Y = 72.0..77.4; Right: X = 129.4..131.4, Y = 72.0..77.4; 5.4 mm wide, 2.0 mm deep |
| "JG body ends accommodated without interference" | Continuous clearance relief | X = 17.0..115.0, Z = 32.8..33.5, Y = 174.4..176.4; 0.7 mm deep |
| "Elephant's foot chamfer prevents first-layer flare" | Perimeter chamfer on ceiling face | 0.3 mm x 45 degrees at Z = 0 plane |
| "1.0 mm fillets eliminate sharp edges" | Exterior edge fillets | 1.0 mm radius on all exterior edges |
| "20-30 cycle snap-fit life" | PETG hooks, 0.3 mm deflection, 10 mm cantilever, 2 mm thickness | At 5% max strain, PETG fatigue life exceeds 20 cycles for 0.3 mm deflection. Grounding: Y = 0.67 * (0.05 * 10^2) / 2.0 = 1.675 mm max deflection >> 0.3 mm actual. Actual strain ~0.9%, well within fatigue limit. |
| "Palm does not deflect under 40-60 N load" | Front wall 2.0 mm PETG, 131.4 mm wide, 8.5 mm tall solid strip plus columns | PETG modulus ~2100 MPa. 2.0 mm wall over 131.4 mm width, loaded at 60 N in +Y: deflection negligible (<<0.1 mm). The force distributes across the full palm area. |

No ungrounded behavioral claims remain. All design gaps are explicitly flagged above.

---

## Vision Compliance Check

Checked against `hardware/vision.md` values:

| Vision value | Top shell compliance | Status |
|-------------|---------------------|--------|
| Consumer appliance, not a collection of components | Single matte black PETG piece. No visible fasteners on exterior. 1.0 mm fillets on all exterior edges. Parting line reads as design accent (0.3 mm step). | PASS |
| User experience paramount | Palm surface is a single, seamless contact surface with crosshatch grip texture. Finger plate slot with 0.5 mm gap communicates movability. Snap-fit click at closure. No sharp edges. | PASS |
| Cartridge is a "black box" to the user | All mechanism is interior. User sees palm surface, finger plate slot, smooth side walls, and featureless rear wall. No hooks, screws, or internal features visible on any exterior surface. | PASS |
| Release plate hidden inside | Release plate is entirely within the bottom shell. Top shell provides only enclosure above it. Nothing on the top shell exterior hints at the release mechanism. | PASS |
| Squeeze mechanism surfaces inset on front | Palm surface (top shell front wall) and finger plate (separate part through slot) form the two squeeze surfaces. The finger plate is recessed 3.0 mm behind the palm surface. The 0.5 mm gap between plate and slot edges communicates the squeeze zone. | PASS |
| Ease of 3D printing and assembly second consideration after UX | Open-face-up print with no supports. Single-piece print (all features integral). Assembly is one step: press top shell onto bottom shell. Snap-fits alone hold the shell closed. | PASS |
| Every visible feature has obvious purpose | Palm surface: grip zone. Finger plate slot: squeeze zone. Side walls: enclosure. Fillets: finished feel. Parting line: design accent. No decorative elements, no mysterious features. | PASS |
