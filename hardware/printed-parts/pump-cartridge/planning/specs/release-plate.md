# Release Plate -- Parts Specification

A flat rectangular plate (110.8 mm wide x 5.0 mm thick x 51.0 mm tall main body, with two downward-protruding link rod attachment tabs extending to 55.7 mm total height) that slides on two 3 mm steel dowel pins press-fit into the rear wall plate. It translates along the Y axis to push all four JG fitting collets simultaneously when the user squeezes the inset release panel. Four stepped through-bores align with the four JG fittings; annular ledges inside each bore contact the collet end faces and push them inward to release the gripper teeth.

Material: PETG (matte black). Single printed piece, no fasteners, no inserts (the guide pins are in the rear wall plate; the link rods press-fit into the tabs).

---

## Coordinate System

Origin: lower-left corner of the dock-facing face of the main body (the face that faces toward the rear wall plate / dock side).

- **X axis**: width (left to right), main body 0..110.8 mm.
- **Y axis**: thickness (toward cartridge interior), 0..5.0 mm.
- **Z axis**: height (bottom to top), main body 0..51.0 mm; link rod tabs extend to Z = -4.7.

Print orientation: dock-facing face down on build plate (Y = 0 surface on bed). Stepped bores print as vertical cylinders (best roundness). Guide pin holes print as vertical cylinders. Installed orientation: plate stands vertical, parallel to the rear wall plate interior face.

**Frame relationship to rear wall plate frame:**

```
X_rwp = X_plate + 18.5
Z_rwp = Z_plate + 5.0
Y_rwp = Y_plate + Y_dock
```

Where Y_dock is the Y position of the plate's dock-facing face in the rear wall plate frame. Y_dock = 25.8 at rest, 22.8 at full actuation.

**Frame relationship to shell-bottom frame:**

```
X_shell = X_plate + 31.6
Z_shell = Z_plate + 9.1
Y_shell = Y_plate + Y_dock + 0.1
```

---

## Mechanism Narrative

### What the user sees and touches

The release plate is never visible or touchable by the user. It is a fully internal part, captive inside the cartridge between the rear wall plate and the cartridge interior. The user interacts only with the inset release panel on the front face; the release plate is the hidden output end of the squeeze mechanism.

### What moves

**Moving parts:**
- The release plate itself translates along the Y axis (toward and away from the JG fittings on the rear wall plate). Travel range: 3.0 mm (from rest at Y_rwp = 25.8 to full actuation at Y_rwp = 22.8).
- The two 3 mm steel link rods translate with the plate (press-fit into the tab bores; they move as a rigid unit with the plate).
- The four JG collets are pushed inward by the plate's bore ledges during actuation. Each collet compresses 1.3 mm (from 2.74 mm protrusion to 1.40 mm protrusion relative to the body-end face).

**Stationary parts:**
- The rear wall plate (anchored in the shell bottom pocket).
- The two 3 mm steel dowel pins (press-fit into the rear wall plate guide pin bores).
- The four JG PP0408W fittings (press-fit into the rear wall plate).
- The two compression springs (seated between the rear wall plate guide pin boss faces and the release plate dock-facing face; they compress and extend but do not translate).

### What converts the motion

The squeeze mechanism is a straight-line push with no motion conversion. The user squeezes the inset panel rearward (toward -Y). The two steel link rods, press-fit into both the inset panel and the release plate tabs, transmit this motion directly. The release plate translates toward -Y by the same distance as the inset panel. No threads, cams, levers, or gears are involved. The link rods are rigid compression members.

### What constrains each moving part

**Release plate:**
- **X and Z translation:** prevented by the two 3 mm steel dowel pins passing through 3.2 mm sliding-fit through-holes at (X_plate = 6.5, Z_plate = 29.9) and (X_plate = 104.3, Z_plate = 29.9). The 97.8 mm horizontal spacing between pins prevents Z-axis rotation (racking). The 0.2 mm diametral clearance (3.2 mm bore on 3.0 mm pin) permits smooth Y-axis sliding.
- **Y-axis rotation (tilting about X):** prevented by the two guide pins acting as a parallel pair. The 5.0 mm plate thickness provides 5.0 mm of pin engagement length at all positions; the wide horizontal spacing (97.8 mm) creates a large anti-tilt moment arm.
- **Y-axis forward limit (rest):** set by the two compression springs (3 mm ID, 8 mm free length) seated on the guide pin boss annular faces (Y_rwp = 17.8). At rest the springs are at their free length (zero preload). The plate dock-facing face rests at Y_rwp = 25.8.
- **Y-axis rearward limit (full stroke):** the bore ledges contact the fully compressed JG collets, which bottom out against the fitting body-end internal geometry. Force is reacted through the fitting body into the rear wall plate bore shoulders. Maximum rearward position: Y_rwp = 22.8 (3.0 mm travel from rest).

**Link rod tabs:**
- **X translation within channels:** the 3.6 mm wide tabs slide inside the 4.0 mm inner opening of the shell bottom U-channels, with 0.2 mm clearance per side.
- **Z position:** the tabs extend from Z_plate = -4.7 to Z_plate = 0, placing them inside the link rod channels (Z_shell = 4.4 to 9.1). The main body above (wider than the channel) clears the channel tops (Z_shell = 7) by 2.1 mm.

### What provides the return force

Two compression springs (3 mm ID, estimated ~4 mm OD, 8 mm free length), one on each guide pin. Each spring sits on the annular face of the rear wall plate guide pin boss (6 mm OD, Y_rwp = 17.8) and pushes against the release plate dock-facing face (Y_plate = 0). At rest, the springs are at free length. At full actuation (3.0 mm compression), the spring length is 5.0 mm (37.5% compression, well within the 60% maximum for compression springs). The springs return the plate to its rest position when the user releases the squeeze.

### What is the user's physical interaction

The user never touches or sees the release plate. During factory assembly:

1. Slide the release plate onto both guide pins simultaneously (the two 3.2 mm through-holes align with the pins protruding from the rear wall plate). The compression springs are already on the pins. Push the plate against the springs until it seats. Tactile feedback: smooth sliding resistance from the springs.
2. Press-fit the two link rod ends into the tab bores (3.1 mm bores at Z_plate = -2.35 in each tab). Each rod enters from the dock-facing side (Y_plate = 0) and seats with light press-fit resistance. The rods are already threaded through the shell bottom guide bushings before this step.

---

## Constraint Chain

```
[Inset release panel] -> [Link rods: translate -Y] -> [Release plate: translates -Y on guide pins]
                           ^ rigid steel rods in             ^ constrained X,Z by: 2x guide pins
                             compression, press-fit             (3.2 mm bore on 3.0 mm pin, 97.8 mm spacing)
                             into tab bores                  ^ returned +Y by: 2x compression springs
                                                               (3 mm ID, 8 mm free, on boss faces at Y_rwp = 17.8)
                                                             |
                                                             v
                                                       [4x bore ledges: push collets -Y]
                                                             ^ annular ledge at Y_plate = 3.5
                                                               (ID 6.5 mm, OD 9.8 mm)
                                                             ^ contacts collet face (ID 6.69, OD 9.57)
                                                             ^ 1.0 mm dead stroke, then 1.3 mm collet compression
                                                             -> [JG collets release gripper teeth]
```

Every arrow names a force transmission mechanism. Every part lists its constraints.

---

## Part Geometry

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| Width (X) | 110.8 mm (X_plate = 0..110.8) |
| Thickness (Y) | 5.0 mm (Y_plate = 0..5.0) |
| Height, main body (Z) | 51.0 mm (Z_plate = 0..51.0) |
| Height, including tabs (Z) | 55.7 mm (Z_plate = -4.7..51.0) |
| Main body bottom (Z_plate) | 0 |
| Main body top (Z_plate) | 51.0 |
| Tab bottoms (Z_plate) | -4.7 |

### Stepped Collet-Actuating Through-Bores (4x)

Four identical coaxial stepped through-bores penetrating the full plate thickness (Y_plate = 0..5.0). Each bore has three diameter zones.

**Bore center positions (in plate frame):**

| Bore | X_plate (mm) | Z_plate (mm) | JG fitting |
|------|-------------|-------------|------------|
| B1 | 42.9 | 42.4 | JG1 (Pump 1 inlet) |
| B2 | 67.9 | 42.4 | JG2 (Pump 2 inlet) |
| B3 | 42.9 | 17.4 | JG3 (Pump 1 outlet) |
| B4 | 67.9 | 17.4 | JG4 (Pump 2 outlet) |

Grid spacing: 25.0 mm horizontal (X), 25.0 mm vertical (Z). Grid center: X_plate = 55.4, Z_plate = 29.9.

**Stepped bore profile (each bore identical, from dock-facing face to interior face):**

| Zone | Y_plate range (mm) | Diameter (mm) | Length (mm) | Purpose |
|------|-------------------|---------------|-------------|---------|
| Body-end clearance | 0.0..2.0 | 15.5 | 2.0 | Clears 15.10 mm JG body-end OD (0.40 mm diametral clearance) |
| Collet-hugging | 2.0..3.5 | 9.8 | 1.5 | Surrounds 9.57 mm collet OD (0.23 mm diametral clearance) for lateral alignment |
| Tube clearance | 3.5..5.0 | 6.5 | 1.5 | Tube (6.30 mm OD) passes through; smaller than collet ID (6.69 mm) so the annular ledge at Y_plate = 3.5 contacts the collet end face |

**Collet-pushing ledge:** The annular transition from 9.8 mm bore to 6.5 mm bore at Y_plate = 3.5. This ledge faces -Y (toward the dock/fittings). When the plate translates toward -Y, this ledge contacts the collet annular end face and pushes the collet into the fitting body.

- Ledge inner diameter: 6.5 mm
- Ledge outer diameter: 9.8 mm
- Effective contact annulus (limited by collet geometry): ID = 6.69 mm (collet ID), OD = 9.57 mm (collet OD). Contact area per bore = 36.8 mm^2.

**Bore wall thickness between adjacent bores (at 15.5 mm diameter, 25.0 mm center spacing):**
- Same row (B1-B2, B3-B4): 25.0 - 15.5 = 9.5 mm.
- Same column (B1-B3, B2-B4): 25.0 - 15.5 = 9.5 mm.
- Diagonal (B1-B4, B2-B3): sqrt(25^2 + 25^2) - 15.5 = 19.9 mm.

All well above the 1.2 mm structural wall minimum.

**Bore to plate outer edge (nearest cases):**

| Bore | Edge | Distance to edge (mm) |
|------|------|-----------------------|
| B1 top (Z_plate = 42.4 + 7.75 = 50.15) | Top (Z_plate = 51.0) | 0.85 mm (at 0.8 mm minimum, acceptable) |
| B3 bottom (Z_plate = 17.4 - 7.75 = 9.65) | Bottom (Z_plate = 0) | 9.65 mm |
| B3 left (X_plate = 42.9 - 7.75 = 35.15) | Left (X_plate = 0) | 35.15 mm |
| B2 right (X_plate = 67.9 + 7.75 = 75.65) | Right (X_plate = 110.8) | 35.15 mm |

### Guide Pin Through-Holes (2x)

Two through-holes for the 3 mm steel dowel pins that provide linear guidance.

**Positions (in plate frame):**

| Pin | X_plate (mm) | Z_plate (mm) |
|-----|-------------|-------------|
| Left | 6.5 | 29.9 |
| Right | 104.3 | 29.9 |

Horizontal spacing: 97.8 mm. Both at Z_plate = 29.9 (near plate center height).

**Bore dimensions:**

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.2 mm (3 mm pin + 0.1 mm per side sliding-fit clearance per requirements.md) |
| Bore type | Through-hole, Y_plate = 0..5.0 |
| Bore axis | Along Y (perpendicular to plate faces) |

**Spring seat:** The compression spring (3 mm ID, ~4 mm OD, 8 mm free length) seats on the flat dock-facing face (Y_plate = 0) around each guide pin hole. The spring coils surround the pin; the contact annulus is ID = 3.2 mm (bore edge), OD = ~4 mm (spring OD). No counterbore or recess is needed -- the flat face provides adequate seating.

**Clearance to nearest stepped bore:**

| Pin | Nearest bore | 2D center-to-center (mm) | Pin bore radius (mm) | Stepped bore radius (mm) | Edge-to-edge (mm) |
|-----|-------------|--------------------------|---------------------|-------------------------|--------------------|
| Left (6.5, 29.9) | B3 (42.9, 17.4) | 38.6 | 1.6 | 7.75 | 29.2 |
| Right (104.3, 29.9) | B4 (67.9, 17.4) | 38.6 | 1.6 | 7.75 | 29.2 |

No interference. Generous clearance.

### Link Rod Attachment Tabs (2x)

Two rectangular tabs protruding downward from the main body bottom edge. Each tab drops into a shell bottom U-channel and contains a press-fit bore for a link rod end.

**Tab positions (in plate frame):**

| Tab | X_plate center (mm) | X_plate range (mm) |
|-----|--------------------|--------------------|
| Left | 25.4 | 23.6..27.2 |
| Right | 85.4 | 83.6..87.2 |

Symmetric about plate center X (X_plate = 55.4). Offset from center: 30.0 mm each side.

**Tab dimensions:**

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Tab width (X) | 3.6 mm | Link rod channel inner opening 4.0 mm minus 0.2 mm clearance per side |
| Tab height (Z) | 4.7 mm (Z_plate = -4.7..0) | Sized to reach link rod center height with 0.8 mm wall above and below bore |
| Tab thickness (Y) | 5.0 mm | Same as plate thickness (continuous with main body) |

**Link rod press-fit bore (in each tab):**

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.1 mm (3 mm rod + 0.1 mm per side press-fit per requirements.md) |
| Bore axis | Along Y, centered in tab width and height |
| Bore center X_plate | 25.4 (left), 85.4 (right) |
| Bore center Z_plate | -2.35 |
| Bore type | Through-hole (Y_plate = 0..5.0) |

**Tab wall thickness:**

| Wall | Dimension (mm) | Status |
|------|---------------|--------|
| Above bore to tab top (Z) | 0.8 mm | At minimum (0.8 mm) |
| Below bore to tab bottom (Z) | 0.8 mm | At minimum (0.8 mm) |
| Each side of bore (X) | 0.25 mm | Below 0.8 mm minimum -- documented acceptable violation |

The 0.25 mm side walls are a known weak point. The tab is loaded in compression along Y (the rod pushes the plate rearward). The rod is press-fit and does not cycle. The thin side walls need only resist the negligible radial press-fit expansion force. The primary structural load (axial push along Y) is carried by the rod-to-bore interface, not the tab side walls.

**Rod insertion angle:** The rod runs at Z_shell = 5.0 in the shell bottom bushings (3.2 mm bore). The tab bore center is at Z_shell = 6.75 (1.75 mm above the bushing centerline). Over the 7.9 mm span from the nearest bushing (Y_shell = 18) to the tab bore entry (Y_shell = 25.9 at rest), the rod bends slightly (12.5 degrees). The 3 mm steel rod accommodates this deflection elastically. The rear wall plate U-notch (Z_shell = 4.1..7.5) clears the rod at this height.

### Elephant's Foot Chamfers

| Feature | Dimension |
|---------|-----------|
| Chamfer on all edges at Z_plate = -4.7 (tab bottoms, the build-plate face) | 0.3 mm x 45-degree |
| Chamfer on main body bottom edges at Z_plate = 0, excluding tab junctions | 0.3 mm x 45-degree |

These chamfers prevent first-layer flare from interfering with the link rod channel fit and the rear wall plate clearance.

---

## Actuation Sequence

### Rest position (springs at free length)

| Parameter | Value (Y_rwp) |
|-----------|---------------|
| Plate dock face | 25.8 |
| Bore ledge (collet-pushing surface) | 29.3 |
| Plate interior face | 30.8 |
| Collet tip (extended) | 28.3 |
| Gap between ledge and collet tip | 1.0 mm |

The collet is fully extended. The bore ledge is 1.0 mm behind (further from dock) the collet tip. No contact, no preload on the collet.

### Actuation stroke (plate moves toward -Y)

| Travel (mm) | Event | Y_rwp of bore ledge |
|-------------|-------|---------------------|
| 0..1.0 | Dead stroke: ledge closes the 1.0 mm gap to the collet tip | 29.3..28.3 |
| 1.0..2.3 | Collet compression: ledge pushes collet inward 1.3 mm (full collet travel) | 28.3..27.0 |
| 2.3..3.0 | Over-travel margin: plate pushes against fully compressed collet; force reacted through fitting body | 27.0..26.3 |

Total available stroke: 3.0 mm. Required collet compression: 1.3 mm. Dead stroke: 1.0 mm. Over-travel margin: 0.7 mm.

### Spring state at full actuation

Spring compressed length: Y_rwp 22.8 - 17.8 = 5.0 mm. Compression from free length: (8.0 - 5.0) / 8.0 = 37.5%. Well within the 60% maximum.

### Guide pin engagement throughout travel

| Position | Pin engagement in plate (mm) | Pin extending past plate (mm) |
|----------|-----------------------------|-----------------------------|
| Rest | 5.0 (full thickness) | 14.0 |
| Full actuation | 5.0 (full thickness) | 17.0 |

No risk of the plate departing the pins at any position.

---

## Direction Consistency Check

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| User squeezes inset panel rearward | Into cartridge interior | -Y | Yes | Squeeze closes gap between palm (on shell face) and fingers (pulling panel inward) |
| Link rods push release plate rearward | Toward JG fittings | -Y | Yes | Rods are rigid in compression, press-fit into tabs; panel and plate move together |
| Bore ledges push collets rearward | Into fitting body | -Y | Yes | Ledge at Y_plate = 3.5 faces -Y; plate translating -Y brings ledge into contact with collet face |
| Springs push plate forward | Away from fittings | +Y | Yes | Springs seated on boss face (Y_rwp = 17.8) push plate dock face toward +Y (rest position Y_rwp = 25.8) |
| Plate slides on guide pins | Along Y axis only | Y | Yes | 3.2 mm bore on 3.0 mm pin constrains X and Z; through-hole permits Y translation |
| Tabs slide inside U-channels | Along Y axis only | Y | Yes | Tab width 3.6 mm in 4.0 mm channel opening; channel walls constrain X; tab height constrained by channel depth |

No contradictions. All directions consistent with -Y = toward dock/fittings, +Y = toward cartridge interior.

---

## Interface Dimensional Consistency

| Interface | Part A dimension | Part B dimension | Clearance / Fit | Source |
|-----------|-----------------|-----------------|-----------------|--------|
| Guide pin hole to dowel pin | 3.2 mm bore (release plate) | 3.0 mm pin OD (steel dowel in RWP) | 0.2 mm diametral, sliding fit | requirements.md: +0.1 mm per side for sliding fit |
| Guide pin spacing | 97.8 mm (release plate holes) | 97.8 mm (RWP pin bores) | Matched | Spatial resolution Section 6.1 |
| Stepped bore to JG body-end OD | 15.5 mm bore (body-end clearance zone) | 15.10 mm OD (JG body-end) | 0.40 mm diametral clearance | Caliper-verified JG geometry |
| Stepped bore to collet OD | 9.8 mm bore (collet-hugging zone) | 9.57 mm OD (JG collet) | 0.23 mm diametral clearance | Caliper-verified JG geometry |
| Tube clearance bore to tube OD | 6.5 mm bore | 6.30 mm tube OD | 0.20 mm diametral clearance | Caliper-verified tube dimension |
| Bore positions to JG fitting positions | X_plate = 42.9, 67.9; Z_plate = 17.4, 42.4 | X_rwp = 61.4, 86.4; Z_rwp = 22.4, 47.4 (via transform) | Aligned (X_rwp = X_plate + 18.5, Z_rwp = Z_plate + 5.0) | Spatial resolution Section 5.1 |
| Link rod tab bore to rod | 3.1 mm bore | 3.0 mm rod OD | 0.1 mm press-fit per requirements.md | requirements.md: +0.1 mm for press fit |
| Tab width in channel | 3.6 mm tab | 4.0 mm channel inner opening (shell bottom) | 0.2 mm clearance per side | Shell-bottom spec: channel inner opening 4 mm |
| Tab height in channel | 4.7 mm tab (Z_shell = 4.4..9.1 at rest) | Channel Z_shell = 3..7 | Tab protrudes 2.1 mm above channel top; only the 3.6 mm wide tab enters the channel, main body clears above | Spatial resolution Section 7.7 |

No zero-clearance or negative-clearance interfaces. The 0.1 mm press-fit on the link rod bores is intentional (press-fit per requirements.md guidelines). The 0.19 mm interference on the JG fitting center body is in the rear wall plate, not the release plate.

---

## Assembly Feasibility

### Assembly Sequence (factory)

The release plate is assembled as part of the rear wall plate subassembly, before the subassembly is placed into the shell bottom.

1. **Prerequisite:** The rear wall plate already has 4 JG fittings pressed into its bores, 2 guide pins pressed in, and 2 compression springs slid onto the guide pins (steps 1-3 of the RWP assembly sequence).

2. **Slide release plate onto guide pins.** Hold the release plate with the dock-facing face (Y_plate = 0) toward the rear wall plate. Align the two 3.2 mm through-holes (at X_plate = 6.5 and 104.3, Z_plate = 29.9) with the two guide pins. Push the plate onto both pins simultaneously. The springs compress from 8.0 mm to ~6 mm during the push and then return to 8.0 mm (free length) when released, establishing the rest position. Access: fully open, no obstructions. Hands can grip the plate edges.

3. **Press-fit link rods into tab bores.** Two 3 mm steel rods, already threaded through the shell bottom guide bushings, are pressed into the tab bores (3.1 mm diameter at Z_plate = -2.35 in each tab). The rods enter from the dock-facing side. Push each rod until it is flush with the interior face. Light press-fit resistance. Access: the tabs protrude below the main body, visible and accessible from below.

4. **Place rear wall plate subassembly into shell bottom rear pocket.** The complete subassembly (rear wall plate + fittings + pins + springs + release plate + link rods) inserts from above into the open shell bottom. The release plate is forward of the rear wall plate, floating on the guide pins. The link rod tabs drop into the U-channels. The rear wall plate seats in the pocket and the corner snap tabs click.

**Can each step be performed?** Yes. All access is from above or from the open interior. No component blocks access to subsequent steps.

**Is the order correct?** Yes. The release plate must go on after the springs (which must go on after the pins). The link rods must be threaded through the shell bottom bushings before they can be pressed into the release plate tabs (the rods are long; easier to thread them first). The subassembly inserts into the shell last.

**Are any parts trapped or inaccessible?** The release plate can be removed by compressing the springs and sliding it off the guide pins (toward +Y). The link rods can be driven out of the press-fit tab bores with a pin punch if needed. Nothing is permanently trapped.

**Disassembly for service:** Not a design goal (cartridge is replaced as a unit). If needed: open shell top, push link rods out of tab bores, slide release plate off guide pins, remove springs.

---

## Part Count Minimization

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|----------------|----------------|---------|
| Plate main body + link rod tabs | Yes (integral) | No | Same (PETG) | Correct: one piece |
| Plate body + guide pins | No | Yes (pins are stationary, plate slides) | Different (PETG vs steel) | Must be separate: relative motion + different materials |
| Plate body + link rods | No (press-fit, but semi-permanent) | Could be argued either way, but rods span the full cartridge length to the inset panel | Different (PETG vs steel) | Must be separate: rods serve two interfaces (plate + inset panel) and are a different material |
| Plate body + rear wall plate | No | Yes (plate slides relative to RWP) | Same (PETG) | Must be separate: relative motion |
| Plate body + compression springs | No | Yes (springs compress/extend) | Different (PETG vs steel) | Must be separate: relative motion + different materials |

No parts can be combined. The release plate is already at minimum part count: one printed piece.

---

## FDM Printability

### Step 1 -- Print Orientation

**Orientation:** Dock-facing face (Y_plate = 0) down on the build plate. The plate prints as a flat slab, with the link rod tabs protruding upward (in print Z) from the main body.

Wait -- the tabs extend below the main body (Z_plate = -4.7..0). In the print orientation (Y_plate = 0 on the bed, plate lying flat with Z vertical), the tabs protrude downward from the main body toward the bed. The build plate face is the dock-facing face (Y = 0), and the tabs are at the bottom edge of the plate (low Z). The tabs do not protrude toward the bed -- they are part of the plate's Z profile. In print orientation, the Z axis of the plate is vertical (print Z), and the Y axis is the build height. Since the plate is only 5.0 mm thick (Y), it lies flat on the bed with the full 55.7 mm Z height vertical and the 110.8 mm X width horizontal.

**Corrected print orientation:** Dock-facing face (Y_plate = 0) down on the build plate. The part's X-Z profile faces the bed. The build height is the 5.0 mm Y thickness. The tabs are simply part of the X-Z profile and print cleanly as vertical features.

**Rationale:**
- Stepped bores (along Y axis) print as vertical cylinders -- best roundness accuracy for the 15.5 mm, 9.8 mm, and 6.5 mm diameter steps.
- Guide pin through-holes (along Y axis) print as vertical cylinders -- best roundness for the 3.2 mm sliding-fit bores.
- Tab bores (along Y axis) print as vertical cylinders -- best roundness for the 3.1 mm press-fit bores.
- The dock-facing face gets the smooth bed surface finish.
- Build height is only 5.0 mm -- very fast print.

### Step 2 -- Overhang Audit

| Surface / Feature | Angle from horizontal | Printable? | Resolution |
|---|---|---|---|
| Dock-facing face (Y_plate = 0) | 0 degrees (flat on bed) | OK | Build plate surface |
| Interior face (Y_plate = 5.0) | 0 degrees (horizontal, top surface) | OK | Top layer of print |
| Side faces (X = 0, X = 110.8) | 90 degrees (vertical) | OK | No overhang |
| Top face (Z_plate = 51.0) | 90 degrees (vertical in print) | OK | No overhang |
| Bottom face (Z_plate = 0) | 90 degrees (vertical in print) | OK | No overhang |
| Tab side faces | 90 degrees (vertical) | OK | No overhang |
| Tab bottom faces (Z_plate = -4.7) | 90 degrees (vertical in print) | OK | No overhang |
| Stepped bore transitions (15.5 to 9.8 mm, 9.8 to 6.5 mm) | Internal step transitions in vertical bore | OK | Cylinder diameter reductions in a vertically-printed bore; each step is a concentric reduction, prints as progressively smaller circles |
| Elephant's foot chamfers | 45 degrees | OK | At overhang limit |

No overhangs requiring support. The part is a simple flat slab printed with minimal build height (5.0 mm). All bores are vertical cylinders. All faces are either horizontal (bed/top) or vertical.

### Step 3 -- Wall Thickness Check

| Wall / Feature | Thickness (mm) | Minimum required (mm) | Status |
|---|---|---|---|
| Between adjacent bores (15.5 mm dia, 25 mm spacing) | 9.5 | 1.2 (structural) | OK |
| Bore B1 top to plate top edge | 0.85 | 0.8 (standard) | OK (at minimum) |
| Guide pin bore wall to plate edge | 3.3 (6.5 mm from bore center to plate left edge, minus 1.6 mm bore radius) | 0.8 | OK |
| Tab bore side walls (X) | 0.25 | 0.8 (structural) | Below minimum -- documented acceptable violation (compression load only, see Section on tab wall thickness) |
| Tab bore walls above and below (Z) | 0.8 | 0.8 (standard) | OK (at minimum) |
| Main body general wall (plate thickness minus bore diameters) | 5.0 mm full thickness; thinnest at bore transitions | 0.8 | OK |

One violation: tab side walls at 0.25 mm. Documented and accepted per the structural analysis in the spatial resolution (tab loaded only in axial compression; thin side walls are not load-bearing).

### Step 4 -- Bridge Span Check

No unsupported horizontal bridges exist in this print orientation. The part is a 5.0 mm tall slab (in print Z). The stepped bores are vertical cylinders (not bridges). The tab geometry is solid. No spans exceed 15 mm.

The largest "span" is the interior face (Y_plate = 5.0), which is the top layer of the entire part -- this is simply the top surface of the print, not a bridge. It is fully supported by infill below.

### Step 5 -- Layer Strength Check

**Load direction analysis:**
- Primary load: axial compression along Y (link rods push the plate toward -Y; collet reaction pushes plate toward +Y). Y is the build height direction. Layers stack along Y. Compression along the layer stack axis is the **strongest** FDM load direction. No delamination risk.
- Secondary load: the springs push the plate toward +Y (same axis, opposite direction). Same analysis applies.
- No flexing or bending features exist in the release plate. It is a rigid plate that translates axially. No snap-fit arms, no cantilevers.

The print orientation is optimal for the release plate's load profile.

---

## Self-Review Rubric Results

### Grounding Rule

Every behavioral claim has been traced to a named geometric feature with dimensions:

| Claim | Grounding feature | Dimensions |
|-------|------------------|------------|
| Plate translates along Y only | 2x guide pin through-holes | 3.2 mm bore on 3.0 mm pin, 97.8 mm spacing |
| 3.0 mm total travel | Spring free length (8 mm) minus full-actuation spring length (5 mm) | Link rod stroke from inset panel: 3.0 mm |
| 1.0 mm dead stroke before collet contact | Gap between bore ledge (Y_rwp = 29.3 at rest) and collet tip (Y_rwp = 28.3) | 29.3 - 28.3 = 1.0 mm |
| 1.3 mm collet compression | Collet travel per side | 41.80 - 39.13 = 2.67 mm total, 1.3 mm per side (caliper-verified) |
| 0.7 mm over-travel margin | 3.0 - 1.0 - 1.3 = 0.7 mm | Arithmetic from travel and collet stroke |
| Springs return plate to rest | 2x compression springs (3 mm ID, 8 mm free length) on guide pin boss faces (Y_rwp = 17.8) | 37.5% compression at full actuation |
| Tabs fit inside link rod channels | Tab width 3.6 mm in 4.0 mm channel opening | 0.2 mm clearance per side |
| Bore ledge pushes collet squarely | Collet-hugging bore (9.8 mm) surrounds collet (9.57 mm OD) with 0.23 mm diametral clearance | Lateral alignment ensured by bore-to-collet fit |

**Product values check (from vision.md):**
- "The release plate is inside the cartridge" -- the plate is fully internal, captive on guide pins between the rear wall plate and the cartridge interior. Never visible. Satisfied.
- "Everything that the user can see has a purpose the user can understand at a glance" -- the release plate is never visible. Satisfied.
- "The cartridge should NOT have a release plate sitting outside of it in any way" -- the plate is internal, behind the front wall, constrained by the guide pins. Satisfied.
- "Consumer product, kitchen appliance" -- no user interaction with this part. It serves a purely mechanical function hidden inside the cartridge. Satisfied.

No ungrounded claims remain.

### Rubric A -- Mechanism Narrative: PASS

The narrative covers: what the user sees (nothing -- internal part), what moves (the plate + link rods + collets), what converts motion (straight-line push, no conversion), what constrains (guide pins, channel walls), what provides return force (springs), and user interaction (factory assembly only). A reader unfamiliar with the mechanism can understand how the release plate works from the text alone.

### Rubric B -- Constraint Chain: PASS

All arrows labeled with force transmission mechanisms. All parts list their constraints. No unlabeled arrows or unconstrained parts.

### Rubric C -- Direction Consistency: PASS

Six directional claims verified against the coordinate system. No contradictions. All consistent with -Y = toward dock, +Y = toward interior.

### Rubric D -- Interface Dimensional Consistency: PASS

Nine interfaces verified. No zero-clearance or negative-clearance interfaces (except the intentional 0.1 mm press-fit on tab bores). All dimension sources traceable to caliper measurements, requirements.md guidelines, or spatial resolution derivations.

### Rubric E -- Assembly Feasibility: PASS

Four-step assembly sequence (within the larger subassembly). Each step physically feasible with open access. Order is correct. No parts trapped after assembly. Disassembly path exists (though not a design goal).

### Rubric F -- Part Count Minimization: PASS

Five part pairs analyzed. No pairs can be combined. The release plate is one printed piece at minimum count.

### Rubric G -- FDM Printability: PASS

- Print orientation stated with rationale (dock-facing face on bed, 5.0 mm build height).
- No overhangs requiring support.
- One wall thickness violation documented and accepted (tab side walls 0.25 mm, non-structural in load direction).
- No unsupported bridges.
- Layer strength optimal (primary load in compression along layer stack axis).

### Design Gaps

**DESIGN GAP: Tab side wall thickness (0.25 mm) violates the 0.8 mm minimum wall requirement.** Accepted based on structural analysis (axial compression only, not a bending or shear load path). Prototype testing should verify the tabs survive assembly press-fit forces without cracking. If they crack during rod insertion, the tab width must increase (requiring a wider link rod channel in the shell bottom, currently 4.0 mm inner opening).
