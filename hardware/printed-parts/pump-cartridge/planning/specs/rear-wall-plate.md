# Rear Wall Plate -- Parts Specification

The rear closure of the pump cartridge. A rectangular plate (147.8 mm wide x 14.8 mm thick x 69.8 mm tall) that snaps into the shell bottom rear pocket and bridges both shell halves. It hosts four John Guest PP0408W union fittings in stepped press-fit bores, two guide pin bosses for the release plate, four pogo contact pad recesses on the dock-facing face, and two U-notches at the bottom edge for link rod pass-through.

Material: PETG (matte black). Single printed piece, no fasteners, no inserts (JG fittings, guide pins, springs, and copper pads are installed into the printed body during assembly).

---

## Coordinate System

Origin: lower-left corner of the dock-facing face (the face that faces rearward/outward when installed, coplanar with the shell rear face).

- **X axis**: width (left to right), 0..147.8 mm.
- **Y axis**: thickness (toward cartridge interior), 0..14.8 mm.
- **Z axis**: height (bottom to top), 0..69.8 mm.

Print orientation: dock-facing face down on build plate (Y = 0 surface on bed). JG pocket bores are vertical (along print Z axis). Installed orientation: plate stands vertical in the shell rear pocket (rotated 90 degrees from print orientation).

**Frame relationship to shell-bottom frame:**

```
X_shell = X_plate + 13.1
Z_shell = Z_plate + 4.1
Y_shell = Y_plate + 0.1

Inverse:
X_plate = X_shell - 13.1
Z_plate = Z_shell - 4.1
Y_plate = Y_shell - 0.1
```

---

## Mechanism Narrative

### What the user sees and touches

The rear wall plate is never visible to the user during normal operation. When the cartridge is in the dock, the dock-facing face (Y = 0) is pressed against the dock rear wall. When the cartridge is removed from the dock, the rear face shows four circular openings (the JG fitting collet bores, 6.69 mm ID) arranged in a 2x2 grid, and four small copper dots (the pogo contact pads, 4 mm diameter) in a horizontal row below the fittings. The user does not interact with any of these features directly. The entire rear face communicates nothing to the user -- it is hidden infrastructure.

### What moves

**Stationary parts:**
- The plate body itself (rigid, captured in the shell pocket)
- The four JG fittings (press-fit into the plate, cannot translate)
- The two guide pin bosses (integral to the plate)
- The two steel dowel pins (press-fit into the guide pin bores)

**Moving parts hosted by this plate:**
- The release plate slides on the two guide pins along the Y axis. The pins are press-fit into the rear wall plate (stationary) and the release plate slides over them (moving). The rear wall plate is the fixed anchor for this sliding interface.
- The two link rods pass freely through the U-notches at the plate bottom edge. The rods translate in Y during the squeeze gesture. The notches provide clearance only -- they do not guide the rods (the shell bottom bushings do that).

### What converts the motion

The rear wall plate does not convert motion. It is a structural anchor point. The guide pins press-fit into the plate provide the linear rails on which the release plate translates. The compression springs seated on the guide pin boss faces provide the return force that pushes the release plate away from the fittings.

### What constrains each moving part

**Release plate (slides on guide pins):**
- X and Z translation: prevented by the two guide pins (3 mm diameter steel dowels press-fit into 3.1 mm bores at X = 25.0, Z = 34.9 and X = 122.8, Z = 34.9). The 97.8 mm horizontal spacing between pins prevents Z-axis rotation (racking). The release plate has 3.2 mm clearance holes that slide over the pins with 0.2 mm diametral clearance.
- Y-axis rotation (tilting about X): prevented by the two guide pins acting as a pair. The wide spacing (97.8 mm) and the pin length (extending 10 mm from the boss face plus 3 mm boss protrusion = 13 mm total engagement length) resist tilting moments.
- Y-axis forward limit (rest position): set by the compression springs (3 mm ID, 8 mm free length) seated on the guide pin boss faces (6 mm OD annular seat at Y = 17.8). The springs push the release plate away from the fittings. The forward limit is approximately 3 mm in front of the JG body-end faces, determined by the spring free length minus the guide pin engagement geometry.
- Y-axis rearward limit (full stroke): the release plate contacts the JG fitting body-end faces after approximately 3 mm of travel. The collets compress 1.3 mm within that stroke. The plate cannot travel further because the fitting body-ends are rigid (seated against the plate bore shoulders).

**Link rods (pass through U-notches):**
- The U-notches (3.4 mm wide, open at bottom edge, semicircular top at Z = 3.4) provide clearance only. The rods are guided by the shell bottom bushings (3.2 mm bore, three per rod). The notch width (3.4 mm) is wider than the bushing bores (3.2 mm) to avoid binding from slight angular misalignment between the bushing centerline (Z_shell = 5) and the notch centerline.

### What provides the return force

Two compression springs (3 mm ID, 8 mm free length), one on each guide pin. Each spring sits on the annular face of the guide pin boss (6 mm OD, 3.1 mm bore = 1.45 mm radial seat width). The spring pushes the release plate forward (toward -Y, away from the fittings) to its rest position. When the user squeezes the inset panel, the link rods push the release plate rearward (+Y) against the springs.

### What is the user's physical interaction

The user never touches or directly interacts with the rear wall plate. During factory assembly:

1. Press four JG PP0408W fittings into the four stepped bores. Each fitting center body (9.31 mm OD) presses into the 9.5 mm bore with 0.19 mm interference. The body-end shoulders (15.10 mm OD) seat against the 15.5 mm shoulder clearance zones on each face. Tactile feedback: firm press-fit resistance, then a definitive stop as both shoulders contact the plate faces simultaneously. Each fitting requires moderate thumb pressure (~20-40 N) applied axially.
2. Press two 3 mm x 40 mm steel dowel pins into the guide pin bores (3.1 mm bore, 10 mm deep blind holes entering from the interior face at Y = 14.8). Each pin seats with light press-fit resistance. The pin protrudes 30 mm from the interior face (10 mm in-bore + 3 mm boss - 0 mm = 33 mm total beyond the boss face... correction: the pin is 40 mm long, 10 mm is embedded in the bore, leaving 30 mm protruding from the interior face of the plate. Of that, 3 mm passes through the boss, leaving 27 mm exposed beyond the boss face). Actually: bore depth is 10 mm from interior face inward (Y = 4.8..14.8). The pin enters from the interior face. 10 mm of pin is inside the bore. The boss protrudes 3 mm beyond the interior face (Y = 14.8..17.8). So 10 mm of pin is in the plate, 3 mm of pin is inside the boss bore, and 27 mm of pin protrudes beyond the boss face. The spring and release plate slide onto this 27 mm exposed length.
3. Slide one compression spring onto each guide pin (spring sits on boss face).
4. Slide the release plate onto both guide pins simultaneously (release plate clearance holes at matching X, Z positions).
5. Thread the two link rods through the release plate attachment points and through the plate U-notches.
6. The rear wall plate subassembly (plate + fittings + pins + springs + release plate + link rods) is then placed into the shell bottom rear pocket until the four corner snap tabs click.

---

## Constraint Chain

```
[Shell bottom rear pocket] -> [Rear wall plate: stationary]
   ^ constrained by: 1 mm lips on all 4 edges + 4 corner snap tabs (1 mm engagement, 45-deg chamfer)
   ^ rearward retention by: snap tabs resist tube insertion forces
   |
   |--> 4x JG fitting press-fit bores (stepped through-bores)
   |      ^ constrained by: 9.5 mm bore grips 9.31 mm center body (0.19 mm interference)
   |      ^ axially located by: 15.5 mm shoulder clearance zones bear on 15.10 mm body-end shoulders
   |      -> provides: 4 fluid connection ports (dock-side collet bores accept tube stubs)
   |      -> provides: 4 collet faces for release plate to push
   |
   |--> 2x guide pin bores with bosses
   |      ^ constrained by: integral to plate body (blind bores + protruding bosses)
   |      -> anchors: 3 mm steel dowel pins (press-fit in 3.1 mm bore, 10 mm engagement)
   |      -> seats: compression springs (3 mm ID, on 6 mm OD boss face)
   |      -> guides: release plate (slides on pins, 0.2 mm diametral clearance)
   |
   |--> 2x link rod U-notches
   |      ^ constrained by: integral to plate bottom edge
   |      -> clears: 3 mm steel link rods (3.4 mm wide notch, no guiding function)
   |
   |--> 4x pogo contact pad recesses
          ^ constrained by: shallow pockets on dock-facing face (Y = 0)
          -> provides: flat copper contact surfaces for dock pogo pins
```

No arrows are unlabeled. Force transmission through the plate is: tube insertion forces pass from the JG fitting shoulders through the plate body to the shell pocket lips and snap tabs. Release plate spring forces pass from the springs through the boss faces into the plate body.

---

## Part Geometry

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| Width (X) | 147.8 mm |
| Thickness (Y) | 14.8 mm |
| Height (Z) | 69.8 mm |
| Plate centroid X | 73.9 mm |
| Plate centroid Z | 34.9 mm |

### JG Fitting Stepped Through-Bores (4x)

Each bore is a coaxial stepped through-hole penetrating the full plate thickness (Y = 0..14.8). The bore profile captures the JG PP0408W center body in a press-fit and provides clearance for the body-end shoulders on both faces.

**Bore positions (center coordinates in plate frame):**

| Fitting | X (mm) | Z (mm) | Assignment |
|---------|--------|--------|------------|
| JG1 | 61.4 | 47.4 | Pump 1 inlet |
| JG2 | 86.4 | 47.4 | Pump 2 inlet |
| JG3 | 61.4 | 22.4 | Pump 1 outlet |
| JG4 | 86.4 | 22.4 | Pump 2 outlet |

Grid spacing: 25.0 mm horizontal (X), 25.0 mm vertical (Z). Grid centered on plate centroid (73.9, 34.9).

**Stepped bore profile (each bore identical, from Y = 0 to Y = 14.8):**

| Zone | Y range (mm) | Diameter (mm) | Length (mm) | Purpose |
|------|-------------|---------------|-------------|---------|
| Dock-side shoulder clearance | 0..1.32 | 15.5 | 1.32 | Clears 15.10 mm body-end OD with 0.40 mm diametral clearance |
| Press-fit zone | 1.32..13.48 | 9.5 | 12.16 | Grips 9.31 mm center body OD with 0.19 mm interference |
| Interior-side shoulder clearance | 13.48..14.8 | 15.5 | 1.32 | Clears 15.10 mm body-end OD |

Derivation: press-fit zone length = center body length (12.16 mm, caliper-verified). Remaining plate thickness: 14.8 - 12.16 = 2.64 mm, split equally (1.32 mm per side). The fitting is centered in the plate thickness.

**Dock-side entry chamfer:** 1 mm x 45-degree chamfer at each bore entry on the dock-facing face (Y = 0), on the 15.5 mm shoulder clearance bore. This guides dock tube stubs into the collet bore during cartridge insertion.

**JG fitting protrusion from plate faces:** Each body-end is 12.08 mm long; 1.32 mm sits inside the shoulder clearance zone. Protrusion per side = 12.08 - 1.32 = 10.76 mm. Dock-side: 10.76 mm beyond Y = 0. Interior-side: 10.76 mm beyond Y = 14.8 (reaching Y = 25.56 in plate frame).

**Minimum wall between adjacent bores:** The closest bore edges are between JG1 and JG2 (or JG3 and JG4): center spacing 25.0 mm, each bore 15.5 mm diameter at shoulder clearance zones. Edge-to-edge: 25.0 - 15.5 = 9.5 mm. At the press-fit zone (9.5 mm diameter): 25.0 - 9.5 = 15.5 mm. Well above the 1.2 mm structural wall minimum.

### Guide Pin Bores and Bosses (2x)

Two blind bores from the interior face, each with a cylindrical boss protruding from the interior face.

**Positions (center coordinates in plate frame):**

| Pin | X (mm) | Z (mm) |
|-----|--------|--------|
| Left | 25.0 | 34.9 |
| Right | 122.8 | 34.9 |

Horizontal spacing: 97.8 mm (symmetric about plate center X = 73.9). Pin Z = 34.9 = plate center height.

**Bore dimensions:**

| Parameter | Value |
|-----------|-------|
| Bore diameter | 3.1 mm (3 mm pin + 0.1 mm for FDM press-fit per requirements.md) |
| Bore depth from interior face | 10 mm (Y = 4.8..14.8) |
| Bore type | Blind hole from interior face (solid plate from Y = 0..4.8 behind bore) |

**Boss dimensions:**

| Parameter | Value |
|-----------|-------|
| Boss OD | 6 mm |
| Boss height (protrusion from interior face) | 3 mm (Y = 14.8..17.8) |
| Boss bore | 3.1 mm, continuous with guide pin bore |
| Boss annular face | Flat ring at Y = 17.8, OD = 6 mm, ID = 3.1 mm -- serves as compression spring seat |

**Pin engagement:** The 3 mm x 40 mm steel dowel pin is pressed in from the interior face. 10 mm of pin length sits in the bore; the remaining 30 mm protrudes from the interior face (3 mm through the boss bore + 27 mm beyond the boss face). The compression spring (3 mm ID, 8 mm free length) slides onto the exposed pin and rests on the boss annular face. The release plate then slides onto both pins.

### Link Rod U-Notches (2x)

Two U-shaped notches at the plate bottom edge, open downward, allowing the 3 mm steel link rods to pass through the plate without constraining them (the shell bottom bushings provide rod guidance).

**Positions (notch center X in plate frame):**

| Notch | Center X (mm) |
|-------|---------------|
| Left | 43.9 |
| Right | 103.9 |

**Notch geometry:**

| Parameter | Value |
|-----------|-------|
| Notch width (X) | 3.4 mm |
| Notch height (Z) | 3.4 mm from bottom edge (Z = 0..3.4) |
| Notch depth (Y) | Full plate thickness (Y = 0..14.8), through-slot |
| Notch profile | Rectangular with semicircular top (radius 1.7 mm centered at Z = 1.7) opening to bottom edge |
| Minimum wall to nearest feature | Left notch to plate left edge: 43.9 - 1.7 = 42.2 mm (ample). Right notch to plate right edge: 147.8 - 103.9 - 1.7 = 42.2 mm (ample). |

The notch is open at the bottom edge (Z = 0), meaning the plate simply has a slot cut upward from the bottom. The semicircular top at Z = 3.4 ensures the rod (3 mm diameter at Z_shell = 5 = Z_plate = 0.9) has clearance above (rod top edge at Z_plate = 0.9 + 1.5 = 2.4; notch top at Z_plate = 3.4; clearance = 1.0 mm).

### Pogo Contact Pad Recesses (4x)

Four shallow circular recesses on the dock-facing face (Y = 0) that accept copper pad inserts (small PCB fragments or copper tape).

**Positions (center coordinates in plate frame):**

| Pad | X (mm) | Z (mm) | Assignment |
|-----|--------|--------|------------|
| 1 | 66.3 | 8.0 | Pump 1 motor + |
| 2 | 71.4 | 8.0 | Pump 1 motor - |
| 3 | 76.4 | 8.0 | Pump 2 motor + |
| 4 | 81.5 | 8.0 | Pump 2 motor - |

Pad pitch: 5.08 mm. Cluster centered at X = 73.9 (plate center X), Z = 8.0.

**Recess geometry:**

| Parameter | Value |
|-----------|-------|
| Recess diameter | 4.5 mm |
| Recess depth | 0.5 mm (from Y = 0 face inward) |
| Pad insert diameter | 4 mm copper |
| Pad surface | Flush with or 0.1 mm proud of dock-facing face |

**Wire routing grooves (2x):** On the interior face (Y = 14.8), two grooves (1.5 mm wide x 1.0 mm deep) route motor wires from the cartridge interior to the pad positions. Wires are soldered to the copper pads from the interior side through small through-holes (1 mm diameter) at each pad position, connecting the interior wire routing to the dock-facing pad surface.

### Snap Tab Chamfers (8x)

The rear wall plate engages 8 snap tabs total: 4 on the shell bottom and 4 on the shell top. At each engagement position, the plate edge has a 45-degree x 1 mm chamfer along a 6 mm length centered on the tab position, oriented along the X direction (on the left and right edges of the plate).

**Chamfer positions:**

| Position | X_plate (mm) | Z_plate (mm) | Shell half |
|----------|-------------|-------------|------------|
| Bottom-left | 2.9 | 2.9 | Bottom |
| Bottom-right | 144.9 | 2.9 | Bottom |
| Mid-left | 2.9 | 30.9 | Bottom |
| Mid-right | 144.9 | 30.9 | Bottom |
| Mid-upper-left | 2.9 | 38.9 | Top |
| Mid-upper-right | 144.9 | 38.9 | Top |
| Top-left | 2.9 | 66.9 | Top |
| Top-right | 144.9 | 66.9 | Top |

The chamfers are on the plate's left (X = 0) and right (X = 147.8) edges, running 6 mm along the X direction. The 45-degree angle faces the insertion direction (the plate inserts from above, +Z in shell frame, so the chamfer leading edges face downward in the installed orientation).

### Exterior Edge Chamfers

| Feature | Dimension |
|---------|-----------|
| Elephant's foot chamfer | 0.3 mm x 45-degree on all edges at the build-plate face (dock-facing face, Y = 0 in plate frame = print bed surface) |
| General exterior edge chamfer | 1 mm on all non-bottom exterior edges |

The elephant's foot chamfer prevents the first-layer flare from interfering with the shell pocket fit. The 1 mm general chamfer softens all edges for handling and matches the cartridge design language.

---

## Interface Dimensional Consistency

### Interface Table

| Interface | Part A (rear wall plate) | Part B (mating part) | Clearance / Fit | Source |
|-----------|------------------------|---------------------|-----------------|--------|
| Plate width in shell pocket | 147.8 mm | 148 mm pocket opening (shell bottom) | 0.1 mm per side (snug) | Shell-bottom spec Section 12.1 / spatial Section 3.1 |
| Plate height in shell pocket | 69.8 mm | 70 mm pocket opening (shell bottom + top) | 0.1 mm per side (snug) | Shell-bottom spec / spatial Section 3.2 |
| Plate thickness in shell pocket | 14.8 mm | 15 mm pocket depth (shell bottom) | 0.1 mm per side (snug) | Shell-bottom spec / spatial Section 3.3 |
| JG press-fit bore to center body | 9.5 mm bore | 9.31 mm OD center body | 0.19 mm interference (press-fit) | Caliper-verified JG geometry |
| JG shoulder clearance bore to body-end | 15.5 mm bore | 15.10 mm OD body-end | 0.40 mm diametral clearance | Caliper-verified JG geometry |
| Guide pin bore to dowel pin | 3.1 mm bore | 3.0 mm pin OD | 0.1 mm (press-fit per requirements.md) | Requirements.md press-fit guideline |
| Guide pin boss OD to release plate clearance | 6.0 mm boss OD | 6.4 mm clearance hole (release plate) | 0.4 mm diametral clearance | Concept architecture |
| Link rod notch width to rod | 3.4 mm notch | 3.0 mm rod OD | 0.4 mm diametral clearance | Spatial Section 6.2 |
| Pogo pad recess to pad insert | 4.5 mm recess dia | 4.0 mm copper pad dia | 0.5 mm diametral clearance | Spatial Section 10.2 |
| Pogo pad pitch to dock header pitch | 5.08 mm | 5.08 mm | Matched | Spatial Section 7.1 |
| Snap tab engagement to plate chamfer | 1 mm tab protrusion | 1 mm x 45-degree chamfer | Matched engagement | Shell-bottom spec / spatial Section 8.3 |

No zero-clearance or negative-clearance interfaces except the intentional JG press-fit (0.19 mm interference) and guide pin press-fit (0.1 mm press-fit per FDM guidelines).

---

## Assembly Feasibility

### Assembly Sequence (factory)

1. **Press 4 JG fittings into plate bores.** Each fitting is oriented with the barbell profile aligned to the stepped bore. The center body aligns with the 9.5 mm press-fit zone. Apply axial force (~20-40 N) until both body-end shoulders seat against the plate faces. Access: the fitting is pushed through the bore from either face; the bore is a through-hole with no blind end to trap air. The 1 mm x 45-degree entry chamfer on the dock-facing side guides initial alignment.

2. **Press 2 guide pins into bores.** Each 3 mm x 40 mm steel dowel pin enters the 3.1 mm bore from the interior face (Y = 14.8). Push until seated (10 mm deep). Access: the interior face is fully open at this stage.

3. **Slide springs onto guide pins.** One compression spring (3 mm ID, 8 mm free length) per pin, resting on the 6 mm boss annular face. Access: open interior face.

4. **Slide release plate onto guide pins.** The release plate's two 3.2 mm clearance holes align with the two pins. The plate slides over both pins simultaneously. The springs compress slightly to the plate's rest position. Access: both pins are accessible from the interior.

5. **Thread link rods through release plate and through U-notches.** The link rods (3 mm x long) pass through the release plate's attachment points and then through the U-notches in the rear wall plate. The rods extend forward through the cartridge interior toward the inset panel.

6. **Place subassembly (plate + fittings + pins + springs + release plate + rods) into shell bottom rear pocket.** The plate inserts from above (the shell bottom is open-top during assembly). The plate drops into the pocket (Y = 0..15 in shell frame) and the corner snap tabs click over the chamfered plate edges. Access: the pocket is fully open from above.

**Can each step be performed?** Yes. All components insert from the interior face or from above (open shell). No component blocks access to a subsequent installation point.

**Is the order correct?** Yes. The JG fittings must be installed before the release plate (the release plate must clear the fitting body-ends). The guide pins must be installed before the springs and release plate. The link rods thread through the release plate before the subassembly is placed in the shell.

**Are any parts trapped or inaccessible?** The guide pins are press-fit into blind bores -- once installed, they cannot be removed without destructive force. This is intentional: the pins are permanent. The JG fittings are press-fit and similarly permanent. The release plate can be removed by sliding it off the guide pins (compress springs, slide plate forward off pins). The compression springs are captive between the boss face and release plate but can be removed when the release plate is off.

**Disassembly for service:** Not a design goal (the cartridge is replaced as a unit). If needed: pry shell top off, slide release plate off guide pins, remove springs, pull link rods out through U-notches. The JG fittings and guide pins are permanent -- they cannot be non-destructively removed from the plate.

---

## Part Count Minimization

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|----------------|----------------|---------|
| Plate body + guide pin bosses | Yes (integral) | No | Same (PETG) | Correct: one piece |
| Plate body + JG fittings | Press-fit (permanent) | No | Different (PETG vs acetal) | Cannot combine: different materials, off-the-shelf part |
| Plate body + guide pins | Press-fit (permanent) | No | Different (PETG vs steel) | Cannot combine: different materials |
| Plate body + copper pads | Epoxied (permanent) | No | Different (PETG vs copper/FR4) | Cannot combine: different materials, electrical function |
| Plate body + release plate | No | Yes (release plate slides on pins) | Same (PETG) | Must be separate: relative motion |
| Plate body + link rods | No | Yes (rods slide through notches) | Different (PETG vs steel) | Must be separate: relative motion + different materials |

No parts can be combined. The rear wall plate is already at minimum part count for its function.

---

## FDM Printability

### Step 1 -- Print Orientation

**Orientation:** Dock-facing face (Y = 0) down on the build plate. The plate prints as a flat slab with the JG pocket bores oriented vertically (along the print Z axis).

**Rationale:**
- JG fitting bores require the best roundness accuracy for press-fit. Vertical cylinders in FDM have the best roundness.
- Guide pin bores (blind holes from interior face) print as vertical blind holes from the top -- good accuracy.
- The dock-facing face (which receives the pogo pads) gets the smooth bed surface finish -- ideal for flat electrical contact.
- The plate is only 69.8 mm tall in the print Z direction, well within the 320 mm build height.

### Step 2 -- Overhang Audit

| Surface / Feature | Angle from horizontal | Printable? | Resolution |
|---|---|---|---|
| Dock-facing face (Y = 0) | 0 degrees (flat on bed) | OK -- build plate surface | N/A |
| Interior face (Y = 14.8) | 0 degrees (top face) | OK -- horizontal top surface, fully supported | N/A |
| Left face (X = 0) | 90 degrees (vertical) | OK | N/A |
| Right face (X = 147.8) | 90 degrees (vertical) | OK | N/A |
| Bottom face (Z = 0 in plate frame = vertical in print) | 90 degrees (vertical) | OK | N/A |
| Top face (Z = 69.8 in plate frame = vertical in print) | 90 degrees (vertical) | OK | N/A |
| JG bore walls (cylindrical, vertical) | 90 degrees | OK -- vertical cylinders | N/A |
| JG bore shoulder transitions (15.5 mm to 9.5 mm step) | Horizontal ledge (0 degrees) inside bore | Requires resolution | The shoulder is a 3.0 mm radial step (from 9.5 to 15.5 mm diameter) at Y = 1.32 and Y = 13.48. In print orientation, these are horizontal ledges inside a vertical bore. The dock-side shoulder (Y = 1.32, near the bed) is supported by the bed/earlier layers. The interior-side shoulder (Y = 13.48, near the top) is an unsupported horizontal ledge. **Resolution:** The radial overhang per side is (15.5 - 9.5) / 2 = 3.0 mm. This is a bridge across a 3.0 mm annular gap. Per requirements.md, bridges under 15 mm are acceptable. A 3.0 mm bridge will print cleanly with minor sag. |
| Guide pin boss (6 mm OD cylinder, 3 mm tall, protruding from interior face) | Vertical cylinder on top face | OK -- printed as vertical cylinders on the top layer | N/A |
| Guide pin bore (3.1 mm blind hole, 10 mm deep from interior face) | Vertical hole from top | OK -- vertical bore, blind end is a small 3.1 mm bridge at the bore bottom (Y = 4.8) which prints fine | N/A |
| Link rod U-notches (open at bottom edge) | Semicircular top (radius 1.7 mm) | OK -- the notch top is a small 3.4 mm bridge at Z = 3.4. In print orientation this is a vertical feature (the notch runs along the Y axis in plate frame = horizontal in print). The semicircular top is a 3.4 mm wide bridge in the horizontal plane. Under 15 mm, printable. | N/A |
| Pogo pad recesses (0.5 mm deep, on bed face) | On build plate | OK -- recesses on the bed face print as raised features on the bed surface | N/A |
| Snap tab chamfers (45-degree x 1 mm on edges) | 45 degrees | OK -- at the printability limit, acceptable | N/A |
| Elephant's foot chamfer (0.3 mm x 45-degree) | 45 degrees | OK | N/A |
| General edge chamfers (1 mm) | 45 degrees | OK | N/A |

**Summary:** The only overhang concern is the interior-side shoulder transition in the JG bores (3.0 mm annular bridge). This is well under the 15 mm bridge limit and will print with acceptable quality. No supports needed anywhere.

### Step 3 -- Wall Thickness Check

| Feature | Thickness | Minimum required | Pass? |
|---------|-----------|-----------------|-------|
| Plate body (solid zones between features) | 14.8 mm | 1.2 mm (structural) | Yes |
| Wall between adjacent JG bores at shoulder clearance (15.5 mm dia) | 9.5 mm edge-to-edge | 1.2 mm | Yes |
| Wall between adjacent JG bores at press-fit (9.5 mm dia) | 15.5 mm edge-to-edge | 1.2 mm | Yes |
| Wall between JG bore and plate edge (minimum) | JG1 at X = 61.4, bore edge at 61.4 - 7.75 = 53.65 mm from plate left edge at X = 0. | 1.2 mm | Yes (53.65 mm) |
| Solid backing behind guide pin bore (Y = 0..4.8) | 4.8 mm | 1.2 mm | Yes |
| Guide pin boss wall thickness | (6.0 - 3.1) / 2 = 1.45 mm | 0.8 mm (standard) | Yes |
| Wall above link rod notch (nearest feature) | Z = 3.4 to nearest JG bore edge at Z = 22.4 - 7.75 = 14.65. Distance: 14.65 - 3.4 = 11.25 mm | 1.2 mm | Yes |
| Wall between pogo pad recess and plate bottom edge | Z = 8.0 - 2.25 = 5.75 mm to bottom edge | 0.8 mm | Yes |
| Wall between pogo pad recess and link rod notch | Pogo pad 1 at X = 66.3 vs notch at X = 43.9. Distance: 66.3 - 43.9 - 2.25 - 1.7 = 18.45 mm | 0.8 mm | Yes |

All wall thicknesses exceed minimums.

### Step 4 -- Bridge Span Check

| Bridge | Span | Maximum | Pass? |
|--------|------|---------|-------|
| JG bore interior-side shoulder (annular) | 3.0 mm radial | 15 mm | Yes |
| Guide pin bore blind end | 3.1 mm diameter | 15 mm | Yes |
| U-notch semicircular top | 3.4 mm | 15 mm | Yes |

All bridges are well under 15 mm.

### Step 5 -- Layer Strength Check

In the print orientation (dock-face down on bed, plate laying flat), layer lines stack along the Y axis (plate thickness direction). In the installed orientation, the plate stands vertically.

**Critical load cases:**
- **Tube insertion force (axial, along Y in plate frame):** During cartridge insertion, four tube stubs push through the JG fittings. The reaction force passes through the fitting shoulders into the plate body and then into the shell pocket snap tabs. This force is along the Y axis (parallel to layer lines in print). Layers are in compression -- strong. No concern.
- **Release plate spring force (axial, along Y):** The two compression springs push the release plate away from the plate. The reaction loads the guide pin bosses in tension along Y. The boss-to-plate junction has layers stacking perpendicular to the pull direction (layers are XZ planes, pull is along Y). This is the weakest FDM orientation for tension. **Mitigation:** The boss is 6 mm OD with 1.45 mm wall thickness, and the spring force per pin is small (~2-5 N, typical for a 3 mm ID x 8 mm spring at light compression). This force is well below the inter-layer tensile strength of PETG at this cross-section (~50+ N capacity for a 6 mm OD annular ring with multiple perimeters). Acceptable.
- **Snap tab engagement forces (rearward push during tube insertion):** The snap tabs on the shell engage chamfered plate edges. The retention force is perpendicular to the layer lines at the plate edges. Again, modest forces (~15 N per tab maximum) distributed across 8 tabs. Acceptable.

No snap-fit or flex features on this part. No layer strength concerns.

---

## Direction Consistency Check

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| Release plate translates rearward (toward fittings) when user squeezes | Toward dock face | +Y in plate frame | Yes | Link rods push release plate in +Y; guide pins constrain to Y-only motion; fitting body-ends are at Y = 14.8 + 10.76 = 25.56, release plate approaches from the interior side |
| Compression springs push release plate forward (away from fittings) | Away from dock face | -Y in plate frame | Yes | Springs seated on boss faces (Y = 17.8) push against release plate in -Y direction |
| Tube stubs enter from dock side | From dock into cartridge | +Y in plate frame | Yes | Dock-side collet bores face Y = 0 (outward); tube stubs enter in +Y direction through collets |
| Plate inserts into shell pocket from above | Downward in installed orientation | -Z in shell frame | Yes | Shell bottom pocket open from Z = 38 upward; plate drops in from above before shell top closes |
| Release plate contacts collet annular faces when pushed rearward | Contact at collet face on interior-side body-ends | At Y > 14.8 in plate frame | Yes | Interior-side body-ends protrude to Y = 25.56; collet tips at Y = 25.56 + 2.74 = 28.3 (extended); release plate approaches from -Y side |
| Link rods pass through U-notches at plate bottom | Through bottom-edge notches | Along Y in plate frame | Yes | Notches are through-slots from Y = 0 to Y = 14.8 at the bottom edge (Z = 0..3.4) |

No contradictions found.

---

## Design Gaps

1. **Wire routing through-holes at pogo pads:** The specification calls for 1 mm through-holes at each pogo pad position to connect interior-side wiring to the dock-facing copper pads. The exact routing path from the interior face grooves to these through-holes is specified functionally (1.5 mm wide x 1.0 mm deep grooves on interior face) but the groove paths (start/end coordinates) are not dimensioned. The CadQuery agent should route these grooves from the plate edges (where wires enter from the cartridge interior) to the pad positions in the most direct path. This is a minor detailing gap, not a functional gap.

2. **Spring specifications are nominal.** The compression spring (3 mm ID, 8 mm free length) is specified by ID and free length but not by spring rate or solid height. The spring must fit over the 3 mm guide pin (3 mm ID is correct), seat on the 6 mm OD boss face, and provide enough force to return the release plate reliably (~2-5 N estimated) without requiring excessive squeeze force. A spring rate of ~0.5-1.0 N/mm at 3 mm compression would give 1.5-3.0 N per spring (3-6 N total). Selection of a specific spring part number is deferred to procurement. The geometric interface (3 mm ID bore, 6 mm OD boss seat, 8 mm free length fitting in the available space) is fully specified.
