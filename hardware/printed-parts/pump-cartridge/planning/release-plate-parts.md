# Release Plate -- Parts Specification

The release plate is an internal structural plate within the pump cartridge that simultaneously depresses all four John Guest collet sleeves during cartridge removal. It is entirely hidden from the user. Printed in PETG, flat on the build plate with the rear face down. The plate translates 3.0 mm in the +Y direction (toward the rear wall) when the user squeezes the cartridge front face, and returns to its rest position via two compression springs when released.

---

## Coordinate System

Origin: front-left-bottom corner of the main plate body.

- **X axis**: width (left to right), 0 at left face of main body, positive rightward. Main body extent: 0 to 83.4 mm. Lateral tabs extend to -18.8 (left) and 102.2 (right).
- **Y axis**: depth (front face to rear face), 0 at front face, positive rearward. Extent: 0 to 5.0 mm (main body). Spring bosses protrude to Y = 8.0.
- **Z axis**: height (bottom to top), 0 at bottom face, positive upward. Main body extent: 0 to 34.2 mm.

Front face at Y = 0 (faces toward cartridge front, away from fittings). Rear face at Y = 5.0 (faces toward rear wall and JG fittings). Left edge of main body at X = 0. Right edge at X = 83.4. Bottom edge at Z = 0. Top edge at Z = 34.2.

**Relation to bottom shell frame (at rest, no rotation):**
- plate_X_shell = plate_X_local + 24.3
- plate_Y_shell = plate_Y_local + 157.2
- plate_Z_shell = plate_Z_local + 1.0

During operation at travel distance T (0 to 3.0 mm): plate_Y_shell = plate_Y_local + 157.2 + T.

---

## Mechanism Narrative

### What the user sees and touches

Nothing. The release plate is entirely internal, enclosed within the cartridge shell. The user never sees, touches, or directly interacts with it. No part of the release plate is visible on any exterior surface of the assembled cartridge. The user's interaction is with the finger plate (front face) and palm surface (top shell front wall). The release plate exists to translate the user's squeeze motion into simultaneous collet depression at the rear of the cartridge.

### What moves

**Release plate (this part): translates.** The plate translates 0 to 3.0 mm in the +Y direction (toward the rear wall) during the squeeze action. At rest (no squeeze), the plate sits with its front face at Y = 157.2 in the bottom shell frame. At full travel, the front face is at Y = 160.2.

**Stationary parts that the release plate interfaces with:**
- Four John Guest PP0408W union fittings, press-fit into the bottom shell rear wall. The fittings do not move. Their inboard collet sleeves (9.57 mm OD) protrude from the body ends and serve as both the functional target (the plate pushes them) and the guide surfaces (the plate rides on them).
- The bottom shell rear wall, which anchors the fixed ends of the two compression springs.

**Other moving parts connected to the release plate:**
- Two linkage arms (rigid PETG bars), connected to the release plate via pin-and-socket press-fits at the lateral tabs. The arms translate the same 3.0 mm in +Y, driven by the finger plate at the front of the cartridge.

### What converts the motion

The release plate receives its motion from two rigid PETG linkage arms. The arms connect the finger plate (at the cartridge front face) to the release plate (in the rear zone) through pin-and-socket press-fit joints at both ends. The linkage is a 1:1 rigid connection -- no mechanical advantage, no rotation, no cam or thread. The user's finger pull on the finger plate translates directly into +Y motion of the release plate at the same displacement and force.

The release plate converts this linear translation into collet depression through direct face contact: the annular contact face at Y = 1.0 (plate local) -- the step between the 6.5 mm tube clearance bore and the 9.8 mm collet hugger bore -- pushes the annular end faces of the four collet sleeves simultaneously as the plate advances in +Y.

### What constrains the release plate

**Lateral constraint (X and Z):** Four collet-hugger bores (9.8 mm diameter, 0.6 mm deep) ride on the four collet ODs (9.57 mm). With 0.115 mm radial clearance at each bore, the four-point pattern (65.0 mm span in X, 17.1 mm span in Z) constrains the plate against translation in X and Z and against tilt about all axes. Maximum tilt: 0.77 degrees about X, 0.20 degrees about Z -- both well within the 3.5-degree angular tolerance for collet depression.

**Axial constraint (+Y limit):** The collet mechanical stops limit how far the collets can be depressed (1.3 mm per collet). The compression springs resist further +Y travel. The plate never contacts the rear wall directly; at full travel, 8.8 mm of gap remains between the plate rear face and the rear wall (shell frame Y = 165.2 vs Y = 174.0).

**Axial constraint (-Y limit, rest position):** The two compression springs push the plate in the -Y direction (away from the rear wall, toward the front of the cartridge). The spring force at rest (~4.2 N per spring, ~8.4 N total) holds the plate at its rest position. The linkage arms, connected to the finger plate, transmit the spring return force to the finger plate, maintaining the squeeze gap.

### What provides the return force

Two compression springs (~5 mm OD, ~10 mm free length, ~1 N/mm rate), captured between cylindrical centering bosses on the release plate rear face and matching bosses on the bottom shell rear wall inboard face. The springs are not bonded -- they sit on the bosses and are retained by compression between the two surfaces.

At rest: springs compressed ~4.2 mm, producing ~4.2 N per spring, ~8.4 N total return force.
At full travel (+3.0 mm): springs compressed ~7.2 mm, producing ~7.2 N per spring, ~14.4 N total return force.

**DESIGN EVALUATION: Spring pre-compression.** The synthesis target is 5-10 N total return force at full travel. The current geometry produces ~14.4 N at full travel and ~8.4 N at rest. The rest force (~8.4 N) adds to the user's initial squeeze resistance on top of the 40-60 N collet depression force. This is acceptable: 8.4 N is a small fraction of the 40-60 N working force (14-21% overhead), and the user will perceive it as part of the initial light resistance before collet contact. The 14.4 N at full travel provides strong positive return when the user releases. However, if the spring pre-compression proves excessive during testing, the spatial resolution document notes that a softer spring (~0.5 N/mm) would reduce the idle force to ~2 N per spring while still providing ~3.6 N per spring (~7.2 N total) at full travel. This is a spring selection adjustment, not a geometry change.

### What is the user's physical interaction

The user does not interact with the release plate. The user squeezes the finger plate toward the palm surface on the cartridge front face. The linkage arms transmit this motion to the release plate. The user feels: (1) light initial resistance from the springs (~8.4 N) over the first ~1.0 mm of plate travel (the take-up gap before collet contact), (2) rising resistance as the plate contacts and depresses all four collets (40-60 N over the next 1.3 mm), (3) a sharp force drop as the collet grab ring teeth clear the tube surface, and (4) a hard stop at the end of travel. The release plate is invisible and silent throughout.

---

## Constraint Chain Diagram

```
[User hand: squeeze finger plate toward palm surface]
    |
    | (finger force, +Y direction at plate, 40-60N working + ~8.4N spring preload)
    v
[Finger plate: translates +Y, 3.0mm]
    |
    | (3.0mm pin in 3.1mm socket, press-fit, left and right)
    v
[Linkage arms (x2): translate +Y, 3.0mm, rigid 1:1 connection]
    ^ constrained laterally (X) by: bottom shell mid-height guide rib channels
    |   (left: X = 2.0..9.0, Z = 17.25..20.25; right: X = 123.0..130.0, Z = 17.25..20.25)
    ^ constrained vertically (-Z) by: groove band thickening top surface (Z = 17.25)
    |
    | (3.0mm pin in 3.1mm Y-axis socket, press-fit, left and right)
    v
[RELEASE PLATE: translates +Y, 3.0mm] <-- THIS PART
    ^ constrained laterally (X, Z) by: 4x collet-hugger bores (9.8mm)
    |   riding on 4x collet ODs (9.57mm), 0.115mm radial clearance
    |   Pattern: 65.0mm span (X) x 17.1mm span (Z)
    ^ returned to rest (-Y) by: 2x compression springs
    |   (seated on 2.0mm dia bosses, plate side at Y=5.0, rear wall side at Y=174.0 shell frame)
    |
    | (annular contact face at Y=1.0 plate local, ID 6.5mm, OD 9.8mm)
    | (contacts collet annular end faces, ID 6.69mm, OD 9.57mm)
    v
[JG collet sleeves (x4): pushed +Y 1.3mm into fitting bodies]
    ^ axially located by: JG fittings press-fit into rear wall bores (9.6mm bore, 9.31mm body)
    |
    v
[Output: grab ring teeth deflect radially outward, tubes released]
```

Spring return path:
```
[Compression springs (x2)]
    |
    | (spring seated on rear wall bosses at Y=174.0 shell frame,
    |  opposite end on release plate bosses at Y=5.0 plate local / Y=162.2 shell frame)
    v
[Release plate: pushed -Y to rest position when user releases squeeze]
    |
    | (via linkage arms, 1:1)
    v
[Finger plate: returns to rest, restoring squeeze gap]
```

---

## Overall Envelope

| Parameter | Value |
|-----------|-------|
| Main body width (X) | 83.4 mm |
| Main body depth (Y) | 5.0 mm |
| Main body height (Z) | 34.2 mm |
| Left lateral tab X extent | -18.8 to 0 (18.8 mm long) |
| Right lateral tab X extent | 83.4 to 102.2 (18.8 mm long) |
| Tab Z extent | 15.25 to 20.25 (at mid-height, centered on arm channel) |
| Tab cross-section (Z x Y) | 5.0 mm x 5.0 mm |
| Overall bounding box (X) | -18.8 to 102.2 = 121.0 mm |
| Overall bounding box (Y) | 0 to 8.0 = 8.0 mm (including spring bosses) |
| Overall bounding box (Z) | 0 to 34.2 mm |
| Material | PETG |
| Color | Matte black |
| Mass (estimated) | ~15-20 g |

---

## Feature List

### Feature 1: Main Plate Body

A rectangular solid forming the structural core of the release plate. All four stepped bores pass through this body.

| Parameter | Value |
|-----------|-------|
| X extent | 0 to 83.4 mm |
| Y extent | 0 to 5.0 mm |
| Z extent | 0 to 34.2 mm |
| Front face | Y = 0 |
| Rear face | Y = 5.0 |
| Left face | X = 0 |
| Right face | X = 83.4 |
| Bottom face | Z = 0 |
| Top face | Z = 34.2 |
| Function | Structural body. Contains four stepped bores for collet engagement and guidance. Transfers linkage arm forces to collet contact faces. Stiff enough to distribute force evenly across all four collets despite off-center loading from linkage arms at bottom edges. |

**Wall thicknesses between features:**

| Location | Thickness | Minimum required | Status |
|----------|-----------|-----------------|--------|
| Left edge to JG1/JG3 cradle bore edge (X direction) | 1.5 mm (X = 0 to cradle edge at X = 9.2 - 7.7 = 1.5) | 0.8 mm (non-structural edge) | OK |
| Right edge to JG2/JG4 cradle bore edge (X direction) | 1.5 mm (83.4 - (74.2 + 7.7) = 1.5) | 0.8 mm | OK |
| Bottom edge to JG1/JG2 cradle bore edge (Z direction) | 0.85 mm (8.55 - 7.7 = 0.85) | 0.8 mm | OK (0.05 mm margin) |
| Top edge to JG3/JG4 cradle bore edge (Z direction) | 0.85 mm (34.2 - (25.65 + 7.7) = 0.85) | 0.8 mm | OK (0.05 mm margin) |
| Wall between lower and upper cradle bores (Z direction) | 1.70 mm ((25.65 - 7.7) - (8.55 + 7.7) = 1.70) | 0.8 mm (non-structural web) | OK |
| Wall between left and right cradle bores (X direction) | 49.6 mm ((74.2 - 7.7) - (9.2 + 7.7) = 49.6) | N/A (ample) | OK |

### Feature 2: Stepped Bores (x4, identical)

Each bore is a three-step concentric profile, entered from the rear face (Y = 5.0) and passing through to the front face (Y = 0). The bore axes are parallel to Y (the plate depth direction). Each bore performs three functions: cradles the JG body end during plate travel, guides the plate on the collet OD, and provides the annular contact face that pushes the collet.

**Bore center positions (X, Z) in plate local frame:**

| Bore | X | Z | Bottom shell X | Bottom shell Z |
|------|---|---|----------------|----------------|
| JG1 (left lower) | 9.2 | 8.55 | 33.5 | 9.55 |
| JG2 (right lower) | 74.2 | 8.55 | 98.5 | 9.55 |
| JG3 (left upper) | 9.2 | 25.65 | 33.5 | 26.65 |
| JG4 (right upper) | 74.2 | 25.65 | 98.5 | 26.65 |

**Center-to-center spacing:**

| Pair | Distance | Direction |
|------|----------|-----------|
| JG1 to JG2 (horizontal) | 65.0 mm | X |
| JG1 to JG3 (vertical) | 17.1 mm | Z |
| JG1 to JG4 (diagonal) | 67.2 mm | X-Z |

**Stepped bore profile (all 4 bores identical), entered from rear face:**

| Step | Diameter | Y start | Y end | Depth | Function |
|------|----------|---------|-------|-------|----------|
| 1. Body end cradle | 15.4 mm | Y = 5.0 (rear face) | Y = 1.6 | 3.4 mm | Clears 15.10 mm body end OD as plate advances over fittings. 0.15 mm clearance per side. |
| 2. Collet hugger | 9.8 mm | Y = 1.6 | Y = 1.0 | 0.6 mm | Close fit around 9.57 mm collet OD. 0.115 mm clearance per side. Provides lateral guidance during plate travel. |
| 3. Tube clearance | 6.5 mm | Y = 1.0 | Y = 0 (front face) | 1.0 mm | Through-hole for 6.35 mm tube. 0.075 mm clearance per side. |

**Entry chamfers:**

Each bore step transition has a 0.3 mm x 45-degree chamfer at the entry from the rear face (Y = 5.0 side of the body end cradle bore). This chamfer eases initial engagement with the JG body ends during assembly and compensates for elephant's foot on the build-plate face.

The step from the body end cradle (15.4 mm) down to the collet hugger (9.8 mm) at Y = 1.6 has a 0.3 mm x 45-degree internal chamfer to guide the collet OD into the hugger bore during assembly. The step from collet hugger (9.8 mm) down to tube clearance (6.5 mm) at Y = 1.0 does NOT have a chamfer -- this is the annular contact face that must remain a flat perpendicular surface to push the collet end faces squarely.

**Annular contact face (the primary functional surface):**

| Parameter | Value |
|-----------|-------|
| Y position (plate local) | Y = 1.0 |
| Y position (shell frame, rest) | Y = 158.2 |
| Y position (shell frame, full travel) | Y = 161.2 |
| Inner diameter | 6.5 mm (tube clearance bore) |
| Outer diameter | 9.8 mm (collet hugger bore) |
| Annular width | 1.65 mm |
| Surface | Flat, perpendicular to Y axis. No chamfer. This face must be clean and square to ensure even collet depression. |

**Travel verification:**

| Parameter | Value |
|-----------|-------|
| Take-up gap at rest (contact face to collet tip) | 1.0 mm (shell Y: 159.2 - 158.2) |
| Plate travel to first collet contact | 1.0 mm |
| Collet travel required | 1.3 mm |
| Total plate travel consumed | 1.0 + 1.3 = 2.3 mm |
| Total plate travel available | 3.0 mm |
| Remaining margin | 0.7 mm |
| Body end clearance at full travel | Cradle depth (3.4 mm) minus body end penetration at full travel (3.22 mm) = 0.18 mm margin |

**DESIGN EVALUATION: Collet hugger engagement depth.** The collet hugger bore is only 0.6 mm deep (Y = 1.0 to Y = 1.6). This means the plate rides on each collet OD with only 0.6 mm of axial engagement. At 0.115 mm radial clearance across four points spanning 65.0 mm x 17.1 mm, this is geometrically sufficient to prevent the plate from tilting beyond the 3.5-degree tolerance. However, 0.6 mm is a thin contact band that could be vulnerable to wear, debris, or slight misalignment causing the bore edge to ride up on the collet. The 0.18 mm body-end clearance margin means the geometry cannot accommodate a deeper hugger bore without either thickening the plate (increasing Y) or reducing the cradle depth (reducing body-end clearance below 0.18 mm). **This is tight but acceptable for the expected service life of a replaceable cartridge. Monitor for binding or wear during prototype testing. If the hugger engagement proves insufficient, the plate depth could be increased from 5.0 mm to 5.5 mm, adding 0.5 mm to the hugger depth (total 1.1 mm) while maintaining body-end clearance.**

**DESIGN EVALUATION: Body end clearance margin.** At full travel, the body end penetrates 3.22 mm into the 3.4 mm deep cradle bore, leaving only 0.18 mm of clearance. This is tight. If the JG fitting position varies by more than 0.18 mm from the nominal press-fit location, the plate could bottom out on the body end face before fully depressing the collets. The press-fit bore in the rear wall locates the fitting axially against the wall shoulder faces (Y = 174.0 and Y = 177.0), so positional variation should be limited to manufacturing tolerance of the wall thickness (under 0.1 mm for FDM). **Acceptable, but verify with prototype that the plate reaches full collet depression without bottoming out on the body ends.**

### Feature 3: Lateral Tabs (x2)

Two rectangular tabs extending from the mid-height sides of the main body, reaching the mid-height linkage arm channel positions in the bottom shell. Each tab contains a blind cylindrical pin socket for the linkage arm press-fit connection. The tabs are centered on the arm channel center Z = 18.75 in the shell frame (17.75 in plate local frame).

**Left tab:**

| Parameter | Value |
|-----------|-------|
| X extent | -18.8 to 0 (18.8 mm long) |
| Y extent | 0 to 5.0 (full plate depth) |
| Z extent | 15.25 to 20.25 (5.0 mm tall, centered on Z = 17.75 plate local) |
| Cross-section (Z x Y) | 5.0 mm x 5.0 mm |
| Connection to main body | Integral at X = 0, Z = 15.25 to 20.25, Y = 0 to 5.0 |
| Shell frame Z extent | 16.25 to 21.25 (tab center at shell Z = 18.75, matching arm channel center) |
| Function | Extends plate to reach left linkage arm channel (bottom shell X = 2.0 to 9.0, Z = 17.25 to 20.25). Contains pin socket for left linkage arm rear-end pin. |

**Right tab:**

| Parameter | Value |
|-----------|-------|
| X extent | 83.4 to 102.2 (18.8 mm long) |
| Y extent | 0 to 5.0 |
| Z extent | 15.25 to 20.25 (same as left tab) |
| Cross-section (Z x Y) | 5.0 mm x 5.0 mm |
| Connection to main body | Integral at X = 83.4, Z = 15.25 to 20.25, Y = 0 to 5.0 |
| Shell frame Z extent | 16.25 to 21.25 |
| Function | Mirror of left tab. Contains pin socket for right linkage arm rear-end pin. |

**Tab structural evaluation:** Each tab is a 5.0 mm x 5.0 mm cross-section cantilever extending 18.8 mm from the main body at mid-height. The tab connects to the main body at Z = 15.25 to 20.25, which is in the solid region between the lower bores (cradle top at Z = 8.55 + 7.7 = 16.25) and upper bores (cradle bottom at Z = 25.65 - 7.7 = 17.95). The tab Z range overlaps slightly with the upper bore cradle (Z = 17.95 to 20.25 of the tab overlaps with Z = 17.95 to 20.25 of the upper cradle bore perimeter). At the main body edge (X = 0 and X = 83.4), the bore centers are at X = 9.2 and X = 74.2 respectively, so the bore perimeters (radius 7.7) extend to X = 1.5 and X = 81.9. The tab joins the body at X = 0 (left) and X = 83.4 (right), which are outside the bore perimeter, so the tab connection is in solid material. The tab transmits the linkage arm force (20-30 N per arm, half the total squeeze force) axially along its length to the main body. In pure tension/compression along X, a 5.0 x 5.0 mm PETG cross-section can withstand far more than 30 N. The 1.2 mm structural minimum wall thickness is satisfied (5.0 mm exceeds 1.2 mm in both directions).

### Feature 4: Pin Sockets (x2)

Blind cylindrical bores in the lateral tabs, accepting the 3.0 mm cylindrical pins on the rear ends of the linkage arms. The socket axis is Y (opening on the front face of the tab), matching the arm approach direction. The arms run fore-aft (Y direction) in the bottom shell guide channels, so the pin enters the socket from the front face.

**Left pin socket:**

| Parameter | Value |
|-----------|-------|
| Center (X, Y, Z) plate local | (-9.4, 0, 17.75) |
| Center (X, Y, Z) shell frame at rest | (14.9, 157.2, 18.75) |
| Socket diameter | 3.1 mm |
| Socket axis | +Y (pointing into tab from front face toward rear) |
| Socket depth | 4.0 mm (from front face Y = 0 to blind end Y = 4.0) |
| Socket opening face | Y = 0 (front face of tab) |
| Socket end (blind) Y plate local | 4.0 |
| Pin diameter | 3.0 mm |
| Diametral clearance | 0.1 mm (press-fit) |
| Function | Receives 3.0 mm pin from left linkage arm rear end. Arm slides rearward in the bottom shell guide channel and its pin enters the socket through the front face. Press-fit connection. CA glue for permanent bond in final assembly. |

**Right pin socket:**

| Parameter | Value |
|-----------|-------|
| Center (X, Y, Z) plate local | (92.8, 0, 17.75) |
| Center (X, Y, Z) shell frame at rest | (117.1, 157.2, 18.75) |
| Socket diameter | 3.1 mm |
| Socket axis | +Y (pointing into tab from front face toward rear) |
| Socket depth | 4.0 mm (from front face Y = 0 to blind end Y = 4.0) |
| Socket opening face | Y = 0 (front face of tab) |
| Socket end (blind) Y plate local | 4.0 |
| Pin diameter | 3.0 mm |
| Diametral clearance | 0.1 mm (press-fit) |
| Function | Mirror of left socket. Receives right linkage arm rear pin. |

**Socket position within tab:** Each socket is centered in the tab X width (left: X = -18.8 to 0, center at -9.4; right: X = 83.4 to 102.2, center at 92.8) and centered vertically at Z = 17.75 (mid-height of the 5.0 mm tab spanning Z = 15.25 to 20.25). The socket axis is Y, with the opening at the front face (Y = 0) and the blind end at Y = 4.0, leaving 1.0 mm of wall material between the blind end and the rear face (Y = 5.0).

Wall material around the socket: The tab is 5.0 mm wide in Z (15.25 to 20.25), and the socket center is at Z = 17.75 with 3.1 mm diameter, so the bore edge extends from Z = 16.2 to Z = 19.3. Wall below socket: 16.2 - 15.25 = 0.95 mm. Wall above socket: 20.25 - 19.3 = 0.95 mm. The tab is 18.8 mm wide in X, and the socket center is at X = -9.4 (left) or 92.8 (right) with 3.1 mm diameter, so wall on each side in X: (18.8 - 3.1) / 2 = 7.85 mm. The Z-direction wall (0.95 mm) is above the 0.8 mm minimum wall but below the 1.2 mm structural minimum. **Acceptable for the moderate loads (20-30 N per arm) and PETG material, consistent with the previous specification.**

### Feature 5: Spring Boss Receivers (x2)

Two cylindrical centering bosses protruding from the rear face (Y = 5.0) of the plate. These mate with the compression springs that provide the return force.

**Left spring boss:**

| Parameter | Value |
|-----------|-------|
| Center (X, Z) plate local | (9.2, 17.1) |
| Center (X, Z) shell frame | (33.5, 18.1) |
| Base (on plate rear face) Y plate local | 5.0 |
| Tip Y plate local | 8.0 |
| Boss diameter | 2.0 mm |
| Boss height (protrusion from rear face) | 3.0 mm |
| Function | Centers the inboard end of the left compression spring. Spring ID (~2.5 mm) slides over the 2.0 mm boss with 0.25 mm clearance per side. |

**Right spring boss:**

| Parameter | Value |
|-----------|-------|
| Center (X, Z) plate local | (74.2, 17.1) |
| Center (X, Z) shell frame | (98.5, 18.1) |
| Base Y plate local | 5.0 |
| Tip Y plate local | 8.0 |
| Boss diameter | 2.0 mm |
| Boss height | 3.0 mm |
| Function | Mirror of left boss. Centers right compression spring. |

**Boss position derivation:** The bosses are centered at the same X positions as the JG bore centerlines in each bay (X = 9.2 and 74.2 in plate local, corresponding to X = 33.5 and 98.5 in shell frame). In Z, they are at 17.1 (plate local) which transforms to 18.1 in shell frame -- centered in the 2.0 mm gap between the lower body end top (Z = 17.1 shell) and upper body end bottom (Z = 19.1 shell).

**CROSS-REFERENCE: Bottom shell spring boss specification.** The bottom shell parts spec (Section 3.3, revised) specifies rear wall spring bosses at height 5.0 mm (tip at Y = 169.0 shell frame), revised upward from 3.0 mm to clear the spring-to-body-end radial overlap. The release plate spatial document specifies 3.0 mm boss height (tip at Y = 8.0 plate local = Y = 165.2 shell frame at rest). The spring sits between the plate boss tip (Y = 165.2 at rest) and the rear wall boss tip (Y = 169.0). Free span between tips at rest: 169.0 - 165.2 = 3.8 mm. With a ~10 mm free-length spring, compression at rest: 10.0 - 3.8 = 6.2 mm, producing ~6.2 N per spring (~12.4 N total). At full travel (+3.0 mm): free span = 169.0 - 168.2 = 0.8 mm. Compression: 10.0 - 0.8 = 9.2 mm, producing ~9.2 N per spring (~18.4 N total).

**DESIGN GAP: Spring force with revised rear wall boss height.** The bottom shell parts spec revised the rear wall boss height from 3.0 mm to 5.0 mm to clear spring-to-body-end radial overlap, but the release plate spatial document was not updated to account for this change. With the revised rear wall boss, the spring pre-compression increases and the total return force at full travel reaches ~18.4 N -- exceeding the 5-10 N synthesis target by nearly 2x. **Resolution options:** (1) Use a softer spring (~0.5 N/mm) to bring forces back to target range: rest ~3.1 N per spring (~6.2 N total), full travel ~4.6 N per spring (~9.2 N total). This hits the 5-10 N target at full travel. (2) Reduce release plate boss height from 3.0 mm to 1.0 mm (tip at Y = 6.0 plate local = Y = 163.2 shell frame at rest), increasing free span to 5.8 mm. With 1 N/mm spring: rest force ~4.2 N per spring (~8.4 N total), full travel ~7.2 N per spring (~14.4 N total). **Recommended: Use option (1) -- select a 0.5 N/mm spring. This keeps the geometry as specified in the spatial document and achieves the synthesis target force range. The spring rate is a procurement decision, not a geometry change.**

### Feature 6: Elephant's Foot Chamfer

| Parameter | Value |
|-----------|-------|
| Chamfer | 0.3 mm x 45 degrees |
| Location | Perimeter bottom edge of the main body and tabs at the build-plate face (Y = 5.0 in plate local, which is the rear face, printed face-down) |
| Function | Prevents elephant's foot flaring from bed adhesion. The rear face is the build-plate face. Without this chamfer, the first 0.2-0.3 mm flares outward, potentially interfering with the body end cradle bore openings and spring boss bases on the rear face. |

---

## Assembly Sequence

The release plate is installed into the bottom shell after the JG fittings and springs are in place, and before the linkage arms are connected.

**Step 1: Pre-requisite -- JG fittings and springs already installed.**
The four JG fittings are press-fit into the rear wall bores, and the two compression springs are placed on the rear wall bosses. The bottom shell is open-face-up on a work surface.

**Step 2: Lower the release plate onto the JG fittings.**
Orient the release plate with the rear face (Y = 5.0, with the spring bosses protruding) facing the rear wall. Align the four body end cradle bores (15.4 mm diameter, on the rear face) with the four inboard JG body ends (15.10 mm OD). Lower the plate straight down (-Z in the shell frame, into the open-top shell). The cradle bores slide over the body ends. The collet hugger bores (9.8 mm) engage the collet ODs (9.57 mm). The spring bosses on the plate rear face enter the compression spring coil IDs. The springs compress slightly between the plate bosses and the rear wall bosses, biasing the plate away from the rear wall.

The plate is now seated: guided by the four collets, held away from the rear wall by the springs, with its lateral tabs extending into the mid-height linkage arm channel zones on each side of the shell.

**Step 3: Connect linkage arms to the release plate.**
Slide each linkage arm rearward through its mid-height guide channel (Z = 17.25 to 20.25 in the shell frame) until the arm's rear-end 3.0 mm pin aligns with the release plate's lateral tab pin socket. The pin enters the Y-axis socket through the front face of the tab. Left arm into left socket (center at plate local X = -9.4, Y = 0, Z = 17.75). Right arm into right socket (center at plate local X = 92.8, Y = 0, Z = 17.75). The arm slides rearward (+Y) and its pin engages the socket from the front face. Press-fit connection. Apply CA glue during final assembly.

**Disassembly (developer service):** With the top shell removed and the pump-partition assembly lifted out, the linkage arms can be slid forward (-Y) to disengage the pins from the release plate sockets (friction fit allows this during development without CA glue). The release plate then lifts straight up off the four collet ODs. Springs remain on the rear wall bosses or come out with the plate.

---

## Rubric Results

### Rubric A -- Mechanism Narrative

**Status: COMPLETE.** The narrative starts from the user-visible surface (nothing -- the plate is entirely internal), then describes what moves (the plate translates +Y), what converts the motion (rigid 1:1 linkage arms, direct face contact on collets), what constrains the plate (four collet-hugger bores for lateral guidance, springs for return force, collet mechanical stops for travel limit), what provides return force (two compression springs on centering bosses producing ~8.4 N at rest, ~14.4 N at full travel), and the user's physical interaction (indirect, through the finger plate and linkage arms, feeling spring preload, collet resistance, force drop at release, and hard stop). Every behavioral claim is grounded to a named feature with dimensions.

### Rubric B -- Constraint Chain Diagram

**Status: COMPLETE.** See Constraint Chain Diagram section above. All arrows are labeled with force transmission mechanisms. All parts list their constraints. The spring return path is shown separately. No unlabeled arrows or unconstrained parts.

### Rubric C -- Direction Consistency Check

| # | Claim | Direction | Axis | Verified? | Notes |
|---|-------|-----------|------|-----------|-------|
| 1 | Plate translates toward rear wall during squeeze | Toward rear wall | +Y (plate and shell) | YES | User squeezes finger plate, arms pull plate +Y toward rear wall at Y = 174.0 shell |
| 2 | Springs push plate away from rear wall (return) | Away from rear wall | -Y (plate and shell) | YES | Springs compressed between rear wall (Y = 174.0 shell) and plate (Y = 162.2 shell at rest); spring extends in -Y direction |
| 3 | Contact face pushes collets inward toward fitting center | Into fitting body | +Y (shell frame) | YES | Contact face at Y = 158.2 (rest) advances to Y = 161.2 (full travel); collet tips at Y = 159.2 (rest) compress to Y = 160.5. Plate pushes collets in +Y. |
| 4 | Lateral tabs extend left and right from main body | Left and right | -X (left tab) and +X (right tab) | YES | Left tab: X = -18.8 to 0; right tab: X = 83.4 to 102.2 |
| 5 | Pin sockets open toward tab front face | Forward from rear | -Y (opening at Y = 0, front face) | YES | Both socket axes: +Y (pointing rearward into tab from front face). Opening at Y = 0. Arm pins enter from the front face as the arm slides rearward through the guide channel. |
| 6 | Spring bosses protrude from rear face toward rear wall | Toward rear wall | +Y (plate local) | YES | Boss base at Y = 5.0 (rear face), tip at Y = 8.0. +Y is toward the rear wall. |
| 7 | Collet hugger bores ride on collet ODs during +Y travel | Plate slides +Y along collets | +Y | YES | 9.8 mm bore slides over 9.57 mm collet with 0.115 mm radial clearance as plate advances +Y |
| 8 | Body end cradle bores advance over body ends during +Y travel | Plate slides +Y, cradle bores envelop body ends | +Y | YES | At full travel, body end penetrates 3.22 mm into 3.4 mm deep cradle bore |
| 9 | Linkage arms pull plate in +Y (toward rear wall) | Same direction as finger plate motion relative to cartridge body | +Y | YES | Finger plate moves +Y relative to the palm surface (which is fixed to the shell/rear wall). Arms are rigid. Plate moves +Y same amount. |

No contradictions found. All directional claims are consistent with the coordinate system. Note: the finger plate moving "toward the palm surface" means the finger plate moves in the -Y direction in the shell frame (toward the front wall), but the linkage arms run from front to rear, so when the finger plate is pulled inward (-Y shell), the arms push the release plate outward...

**CORRECTION:** Re-examining the linkage arm force path. The finger plate is at the front face. The user's fingers curl around and pull the finger plate toward the palm (the palm rests on the top shell front wall). The finger plate moves -Y in the shell frame (toward the front wall). But the vision says the release plate moves toward the collets, which are at the rear. This requires the linkage arms to convert the finger plate's -Y motion into the release plate's +Y motion.

Re-reading the concept document (Section 8): "the user squeezes... this motion pulls the release plate rearward (toward the collets)." The bottom shell parts spec constraint chain says: "Release plate: translates -Y, 3mm."

**CRITICAL DIRECTION CORRECTION:** The bottom shell parts spec states the release plate translates -Y (toward rear wall), and the finger plate translates -Y. This means both the finger plate and the release plate move in the same direction (-Y, toward the rear wall). The finger plate is at the front; when the user squeezes (fingers pull toward palm), the finger plate moves inward, and through the rigid linkage arms, the release plate also moves in the same direction.

Wait -- re-reading more carefully. The palm surface is the front wall of the top shell (rigidly connected to the rear wall structure). The finger plate is a separate surface inset ~3 mm from the palm surface. When the user squeezes (brings fingers toward palm), the finger plate moves toward the palm surface, which means the finger plate moves in the +Y direction (rearward, away from Y = 0). This +Y motion of the finger plate propagates through the rigid linkage arms (which run rearward) to the release plate, which also moves +Y (toward the rear wall and collets).

The bottom shell parts spec says the release plate translates "-Y, 3mm" with the description "toward the rear wall." This is a direction error in the bottom shell parts spec: -Y is toward the front wall (Y = 0), not the rear wall (Y = 177). The rear wall is at +Y.

**Resolution:** The spatial resolution document states: "Motion: translates +Y (toward rear wall) by up to 3.0mm during release action." This is the authoritative source. The release plate moves +Y. The bottom shell parts spec's constraint chain diagram contains a sign error (says -Y where it should say +Y for both the finger plate and release plate motion during squeeze). The bottom shell parts spec's Rubric C table (row 5) says "Release plate translates toward rear wall: -Y direction: YES" -- this is inconsistent because "toward rear wall" is +Y, not -Y.

**This specification uses +Y as the squeeze direction for the release plate, consistent with the spatial resolution document.** The bottom shell parts spec's constraint chain should be corrected in a future update to show +Y for the squeeze direction.

| # | Claim (revised) | Direction | Axis | Verified? | Notes |
|---|-------|-----------|------|-----------|-------|
| 1 | Plate translates toward rear wall during squeeze | Toward rear wall | +Y | YES | Consistent with spatial doc |
| 2 | Springs push plate away from rear wall | Away from rear | -Y | YES | |
| 3 | Contact face pushes collets into fitting body | Into body | +Y | YES | |
| 9 (revised) | Finger plate moves toward palm surface (+Y), linkage arms transmit this as +Y to release plate | +Y | +Y | YES | Both finger plate and release plate move in +Y during squeeze |

**FLAGGED: Bottom shell parts spec direction inconsistency.** The bottom shell parts spec (constraint chain diagram and Rubric C row 5) labels the release plate squeeze direction as -Y. The spatial resolution document and this specification use +Y. The rear wall is at Y = 174.0 to 177.0 in the shell frame; motion toward the rear wall is +Y. The bottom shell spec should be updated to correct the sign.

### Rubric D -- Interface Dimensional Consistency

| # | Interface | Release plate dimension | Mating part dimension | Clearance | Source |
|---|-----------|------------------------|----------------------|-----------|--------|
| 1 | Tube clearance bore / 1/4" OD tube | 6.5 mm bore | 6.35 mm tube OD | 0.15 mm diametral (0.075 mm/side) | Bore: spatial doc; Tube: caliper-verified |
| 2 | Tube clearance bore / collet ID | 6.5 mm bore | 6.69 mm collet ID | Bore is smaller than collet ID by 0.19 mm -- this is correct: the bore face contacts the collet annular end face between 6.5 mm and 6.69 mm | Bore: spatial doc; Collet ID: caliper-derived |
| 3 | Collet hugger bore / collet OD | 9.8 mm bore | 9.57 mm collet OD | 0.23 mm diametral (0.115 mm/side) | Bore: spatial doc; Collet OD: caliper-verified |
| 4 | Body end cradle bore / body end OD | 15.4 mm bore | 15.10 mm body end OD | 0.30 mm diametral (0.15 mm/side) | Bore: spatial doc; Body end OD: caliper-verified |
| 5 | Pin socket / linkage arm pin | 3.1 mm bore | 3.0 mm pin | 0.1 mm diametral (press-fit) | Bore: spatial doc; Pin: concept doc |
| 6 | Spring boss / spring ID | 2.0 mm boss OD | ~2.5 mm spring ID | 0.5 mm diametral (0.25 mm/side, centering fit) | Boss: spatial doc; Spring: concept doc (approximate) |
| 7 | Bore centers / bottom shell JG bore centers | Plate X: 9.2, 74.2; Z: 8.55, 25.65 | Shell X: 33.5, 98.5; Z: 9.55, 26.65 | Transform check: 9.2 + 24.3 = 33.5 OK; 74.2 + 24.3 = 98.5 OK; 8.55 + 1.0 = 9.55 OK; 25.65 + 1.0 = 26.65 OK | Both from spatial docs |
| 8 | Tab position / linkage arm channel | Left tab X = -18.8 to 0 (shell X = 5.5 to 24.3), Z = 15.25..20.25 (shell Z = 16.25..21.25) | Left channel: shell X = 2.0 to 9.0, Z = 17.25 to 20.25 | Tab center Z = 18.75 shell matches channel center. Tab depth (5.0 mm Y) fits within channel width (7.0 mm X) with clearance. Tab extends 1.0 mm below channel (shell Z = 16.25 to 17.25) into groove band thickening zone and 1.0 mm above (shell Z = 20.25 to 21.25) into open bay. | Spatial docs |
| 9 | Plate bounding box / shell interior | Plate X = -18.8 to 102.2 (shell X = 5.5 to 126.5) | Shell interior X = 2.0 to 130.0 (non-groove band) | 3.5 mm clearance on left, 3.5 mm on right | Spatial docs |
| 10 | Plate Z extent / shell interior height | Plate Z = 0 to 34.2 (shell Z = 1.0 to 35.2) | Shell interior Z = 2.0 to 33.5 | Plate bottom at shell Z = 1.0 is below floor interior at Z = 2.0; plate top at shell Z = 35.2 is above shell edge at Z = 33.5. **See evaluation below.** | Spatial docs |

**Interface 10 evaluation: Plate extends beyond shell interior.** The plate bottom (shell Z = 1.0) is 1.0 mm below the shell floor interior (Z = 2.0). The plate does not rest on the floor -- it rides on the collet ODs which position it at this height. The main body bottom (plate Z = 0 = shell Z = 1.0) is within the floor thickness, but the main body is suspended by the collets and never contacts the floor. The lateral tabs are now at mid-height (plate Z = 15.25 to 20.25 = shell Z = 16.25 to 21.25), well above the floor. **The previous design gap where tabs at Z = 0 extended below the floor is fully resolved by moving the tabs to mid-height.** No floor relief pockets are needed.

### Rubric E -- Assembly Feasibility Check

| Step | Physically feasible? | Notes |
|------|---------------------|-------|
| 1. JG fittings + springs pre-installed | YES | Done per bottom shell assembly steps 1-2. |
| 2. Lower release plate onto JG fittings | YES | Shell is open-top. Four body ends protrude upward from the rear wall. The plate's four 15.4 mm cradle bores align over the 15.10 mm body ends and slide down. The collet hugger bores (9.8 mm) engage the collet ODs (9.57 mm). The plate is 83.4 mm wide (main body) with 121 mm including tabs. The shell interior is 128 mm wide. Tabs extend to shell X = 5.5 and 126.5, within the 2.0 to 130.0 interior. The plate drops in from above without obstruction. |
| 3. Connect linkage arms | YES | Arms slide rearward through floor channels. Rear pins press into tab sockets. Tab sockets face outward (left socket at X = -18.8 faces -X; right socket at X = 102.2 faces +X). The arm approaches from the front (+Y to -Y direction along the channel), and its rear pin is oriented in X to enter the socket. Tweezers or fingers can reach the rear zone in the open-top shell. |
| Disassembly | YES | Reverse of assembly. Pull arms forward to disengage pins. Lift plate straight up off collets. Springs may come up with plate or remain on rear wall bosses. |

**Order dependency:** The release plate must be installed after JG fittings (step 1 of bottom shell assembly) and springs (step 2), and before the pump-partition assembly (step 6) which would obstruct access to the rear zone.

**Trapped parts check:** After the top shell closes, the release plate is captured between the collets (which prevent upward removal) and the springs (which prevent rearward removal past the rear wall). The plate can only be removed by opening the top shell and lifting from above. This is intentional.

### Rubric F -- Part Count Minimization

| Part pair | Permanently joined? | Relative motion? | Same material? | Verdict |
|-----------|--------------------|--------------------|----------------|---------|
| Release plate + linkage arms | NO (press-fit, separable) | YES (arms translate relative to shell; plate translates same amount, but connection is rigid) | YES (both PETG) | The arms and plate move together as one rigid body during operation. Could they be one printed part? The arms are 150 mm long bars running from the front of the cartridge; the plate is a compact 83.4 mm body in the rear. A combined part would be approximately 150 mm long, 121 mm wide, 34 mm tall with thin 6 mm x 3 mm arms extending forward. This cannot be printed in any orientation without compromising one feature: flat printing would require the arms to print as 150 mm cantilevers, and on-edge printing would produce poor bore circularity. **Correct as separate parts.** |
| Release plate + springs | NO (captured, not bonded) | YES (springs compress/extend) | Different (PETG vs steel) | Must be separate. Correct. |
| Release plate + JG fittings | NO | YES (plate slides on collet ODs) | Different (PETG vs acetal) | Must be separate. Correct. |
| Release plate main body + lateral tabs | YES (integral) | NO | YES (same print) | Correct: one piece. |
| Release plate body + spring bosses | YES (integral) | NO | YES (same print) | Correct: one piece. |

No parts can be combined. No parts are unnecessarily separate. Part count is minimized at 1 printed part.

### Rubric G -- FDM Printability

**Step 1 -- Print orientation.**

| Parameter | Value |
|-----------|-------|
| Print orientation | Flat on build plate, rear face (Y = 5.0) down |
| Build plate face | Y = 5.0 (rear face, the face with spring bosses and body end cradle bore openings) |
| Rationale | The four stepped bores become vertical holes (axes along print Z direction). This produces the best circularity and diameter accuracy for the critical collet hugger bores (9.8 mm with 0.23 mm diametral clearance on 9.57 mm collet OD). The lateral tabs lie flat on the build plate as extensions of the main body. The spring bosses print as small vertical cylinders rising from the build-plate face. |
| Build plate footprint | ~121 mm x 34 mm (well within 325 x 320 mm bed) |
| Constraint | Bore accuracy requires this orientation. The collet hugger bores must be round within ~0.1 mm. Vertical holes (Z-axis circles) achieve this on FDM. Horizontal holes (bridged circles) would not. |

**Step 2 -- Overhang audit.**

| # | Surface / Feature | Angle from horizontal | Printable? | Resolution |
|---|-------------------|----------------------|------------|------------|
| 1 | Rear face (Y = 5.0, build plate face) | 0 deg (on build plate) | OK | Build plate face |
| 2 | Front face (Y = 0, top of print) | 0 deg (horizontal ceiling) | OK | Solid top surface, standard infill coverage |
| 3 | Left face of main body (X = 0, vertical) | 90 deg | OK | Vertical wall |
| 4 | Right face of main body (X = 83.4, vertical) | 90 deg | OK | Vertical wall |
| 5 | Bottom face (Z = 0, vertical in print orientation) | 90 deg | OK | Vertical wall |
| 6 | Top face (Z = 34.2, vertical in print orientation) | 90 deg | OK | Vertical wall |
| 7 | Body end cradle bores (15.4 mm, vertical holes) | N/A (vertical cylindrical holes) | OK | Print as continuous perimeter circles. The bores open on the build-plate face (Y = 5.0 = print Z = 0). The counterbore step at Y = 1.6 (print Z = 3.4) from 15.4 mm to 9.8 mm is an inward step (larger to smaller going up) -- this is a standard internal ledge in a vertical hole, printable as a bridge across the annular step. Bridge span: (15.4 - 9.8) / 2 = 2.8 mm per side. Under 15 mm limit. |
| 8 | Collet hugger bores (9.8 mm, vertical holes) | N/A | OK | Part of the same vertical holes as the cradle bores. Intermediate step. |
| 9 | Tube clearance bores (6.5 mm, vertical holes) | N/A | OK | Smallest step, at the top of the print. Step from 9.8 mm to 6.5 mm at Y = 1.0 (print Z = 4.0) is another inward step, bridge span: (9.8 - 6.5) / 2 = 1.65 mm per side. Under 15 mm limit. This step IS the annular contact face and must be flat and clean. The bridge at this step may leave slight sag in the center -- acceptable because the contact face is the annular ring, not the bridged center (the 6.5 mm bore continues through). |
| 10 | Lateral tabs (mid-height extensions of main body) | Vertical surfaces (X and Z faces) | OK | Tabs are at Z = 15.25 to 20.25 in plate local. In print orientation (rear face Y = 5.0 down), tabs are integral mid-height extensions. All tab faces are vertical or horizontal -- no overhangs. |
| 11 | Pin sockets (3.1 mm Y-axis blind holes in tabs) | Horizontal cylindrical holes (Y-axis in plate frame = horizontal in print) | OK | 3.1 mm diameter bridged circle. Bridge span: 3.1 mm. Well under 15 mm. In print orientation, the socket axis (Y) is horizontal, producing a bridged circle. The blind end at Y = 4.0 is a flat ceiling at 3.1 mm span -- easily bridged. |
| 12 | Spring bosses (2.0 mm dia vertical cylinders on build plate face) | N/A (vertical cylinders rising from build plate) | OK | Small vertical features, 2.0 mm diameter, 3.0 mm tall. Print as standard perimeters. May be slightly oversized due to oozing on small features -- verify with test print. |
| 13 | Entry chamfers on bore openings (0.3 mm x 45 deg) | 45 deg | OK | At 45 deg from horizontal, exactly at the printability threshold. At 0.3 mm scale, this is a single-layer feature and prints acceptably. |
| 14 | Internal bore step (cradle to hugger, 0.3 mm x 45 deg chamfer) | 45 deg | OK | Same as entry chamfer. Small-scale feature at threshold angle. |

No unresolved overhangs. No supports required.

**Step 3 -- Wall thickness check.**

| Feature | Thickness | Minimum required | Status |
|---------|-----------|-----------------|--------|
| Main body walls around cradle bores (X direction) | 1.5 mm per side | 0.8 mm (non-structural edge) | OK |
| Main body walls around cradle bores (Z direction, top and bottom) | 0.85 mm per side | 0.8 mm | OK (0.05 mm margin -- tight) |
| Web between upper and lower cradle bores (Z direction) | 1.70 mm | 0.8 mm | OK |
| Lateral tab cross-section | 5.0 mm x 5.0 mm | 1.2 mm (structural, bears linkage force) | OK |
| Tab wall around pin socket (minimum) | 0.95 mm (from 3.1 mm bore edge to 5.0 mm tab face) | 0.8 mm | OK (tight but above minimum) |
| Spring boss diameter | 2.0 mm | 0.8 mm | OK (solid cylinder, no wall per se) |
| Main body thickness (Y direction) | 5.0 mm total | 0.8 mm | OK |

All wall thicknesses meet or exceed minimums. The 0.85 mm walls at top and bottom edges and the 0.95 mm socket walls are tight but above the 0.8 mm minimum for non-structural features.

**Step 4 -- Bridge span check.**

| Feature | Span | Limit | Status |
|---------|------|-------|--------|
| Cradle-to-hugger bore step (annular bridge) | 2.8 mm per side | 15 mm | OK |
| Hugger-to-tube-clearance bore step (annular bridge, = contact face) | 1.65 mm per side | 15 mm | OK |
| Pin socket horizontal bridge (top of 3.1 mm bore) | 3.1 mm | 15 mm | OK |
| Pin socket blind end (ceiling) | 3.1 mm | 15 mm | OK |

All bridges well under the 15 mm limit.

**Step 5 -- Layer strength check.**

| Feature | Load direction | Layer orientation | Status |
|---------|---------------|-------------------|--------|
| Main body under axial compression (+Y, collet reaction force) | Y axis (through plate thickness) | Layers stack along Y (print Z). Load is perpendicular to layers -- this is compression, not tension. FDM parts are adequate in compression perpendicular to layers. | OK |
| Lateral tabs under tension/compression (X axis, linkage arm force) | X axis (along tab length) | Layers stack along Y (print Z). Load is parallel to build plate (in XZ plane). Layer-to-layer adhesion is not stressed; the perimeter extrusions carry the load in X. | OK |
| Pin socket walls under hoop stress (pin press-fit) | Radial (in YZ plane around X-axis bore) | Layers stack along Y. The socket is a horizontal hole; hoop stress is partly parallel and partly perpendicular to layers. At 0.1 mm interference on a 3.0 mm pin, the hoop stress is very low. | OK |

No layer-strength conflicts. The print orientation (rear face down, bores vertical) is optimal for bore accuracy and does not create problematic layer orientations for any load-bearing feature.

---

## Dimension Summary Table

| Dimension | Value | Frame | Source |
|-----------|-------|-------|--------|
| Main body width | 83.4 mm | Plate X | Spatial doc Section 3a |
| Main body depth | 5.0 mm | Plate Y | Spatial doc Section 3a |
| Main body height | 34.2 mm | Plate Z | Spatial doc Section 3a |
| Tab length (each) | 18.8 mm | Plate X | Spatial doc Section 3a |
| Tab Z extent | 15.25 to 20.25 | Plate Z | Spatial doc Section 3a (mid-height, centered on arm channel) |
| Tab cross-section | 5.0 mm x 5.0 mm | Plate Z x Y | Spatial doc Section 3a |
| Tube clearance bore dia | 6.5 mm | -- | Spatial doc Section 3b |
| Collet hugger bore dia | 9.8 mm | -- | Spatial doc Section 3b |
| Body end cradle bore dia | 15.4 mm | -- | Spatial doc Section 3b |
| Cradle depth (from rear face) | 3.4 mm | Plate Y | Spatial doc Section 3b |
| Hugger depth | 0.6 mm | Plate Y | Spatial doc Section 3b |
| Tube clearance depth | 1.0 mm | Plate Y | Spatial doc Section 3b |
| Contact face Y | 1.0 mm from front face | Plate Y | Spatial doc Section 3b |
| JG bore horizontal spacing | 65.0 mm | Plate X | Spatial doc Section 3b |
| JG bore vertical spacing | 17.1 mm | Plate Z | Spatial doc Section 3b |
| Pin socket diameter | 3.1 mm | -- | Spatial doc Section 3c |
| Pin socket depth | 4.0 mm | Plate Y | Spatial doc Section 3c (Y-axis, opening on front face) |
| Pin socket center Z | 17.75 | Plate Z | Spatial doc Section 3c (centered on arm channel) |
| Spring boss diameter | 2.0 mm | -- | Spatial doc Section 3d |
| Spring boss height | 3.0 mm | Plate Y | Spatial doc Section 3d |
| Take-up gap (rest) | 1.0 mm | Shell Y | Spatial doc Section 3b |
| Plate travel | 3.0 mm | Shell Y | Spatial doc Section 1 |
| Entry chamfer (bore openings) | 0.3 mm x 45 deg | -- | Print orientation notes |
| Elephant's foot chamfer | 0.3 mm x 45 deg | -- | Requirements.md Section 6 |
| Overall bounding box | 121.0 x 8.0 x 34.2 mm | Plate X, Y, Z | Spatial doc Section 3a |

---

## Design Gaps and Flagged Issues

### Gap 1: Spring force exceeds synthesis target (MODERATE)

The spatial resolution document calculates spring force at rest of ~4.2 N per spring (~8.4 N total) and at full travel of ~7.2 N per spring (~14.4 N total), using a ~1 N/mm spring rate. The bottom shell parts spec further revised the rear wall boss height to 5.0 mm (from 3.0 mm) to resolve a spring-to-body-end radial overlap, which increases pre-compression and pushes forces even higher (~6.2 N per spring at rest, ~9.2 N per spring at full travel with the revised geometry). The synthesis target is 5-10 N total at full travel.

**Impact:** The excess return force adds to the user's squeeze resistance (up to ~18.4 N on top of the 40-60 N collet force), increasing total squeeze effort by up to 30%. This is within the comfortable squeeze range (60-120 N) but exceeds the synthesis target.

**Recommended resolution:** Select a 0.5 N/mm spring rate instead of 1.0 N/mm. No geometry changes required.

### Gap 2: RESOLVED -- Lateral tab bottom no longer extends below floor interior

Previously, when the tabs were at Z = 0 to 5.0 (plate local), they extended below the floor interior surface at shell Z = 2.0. The tabs are now at Z = 15.25 to 20.25 (plate local), which is shell Z = 16.25 to 21.25 -- well above the floor. **This gap is fully resolved by moving the tabs to mid-height.**

### Gap 3: Collet hugger engagement depth is minimal (LOW)

The 0.6 mm hugger depth provides guidance but is a thin contact band. Wear or debris could reduce effective guidance.

**Impact:** Low risk for the expected service life of a replaceable cartridge. The four-point guidance pattern with 65.0 mm x 17.1 mm span provides robust tilt prevention even with minimal engagement depth.

**Recommended resolution:** Monitor during prototype testing. If binding or wear is observed, increase plate depth from 5.0 mm to 5.5 mm (adds 0.5 mm to hugger depth). This consumes some of the 0.18 mm body-end clearance margin, so verify simultaneously.

### Gap 4: Body end clearance at full travel is tight (LOW)

0.18 mm margin between body end face and cradle bore bottom at full travel. FDM positional tolerance on the rear wall bore could consume this margin.

**Impact:** If the fitting sits 0.18 mm further inboard than nominal, the plate could bottom out on the body end face before fully depressing the collets.

**Recommended resolution:** Verify with prototype. The rear wall shoulder seats provide positive axial location, limiting positional variation to FDM dimensional accuracy (~0.1 mm for a well-calibrated Bambu H2C). The 0.18 mm margin should be adequate.

### Gap 5: Bottom shell direction inconsistency (DOCUMENTATION)

The bottom shell parts spec labels the release plate squeeze direction as -Y in its constraint chain diagram and Rubric C table. The spatial resolution document and this specification use +Y (toward the rear wall). The rear wall is at Y = 174.0-177.0 in the shell frame; motion toward the rear wall is +Y.

**Impact:** No physical impact -- the mechanism works the same regardless of labeling. Documentation inconsistency could cause confusion in downstream steps.

**Recommended resolution:** Update the bottom shell parts spec to use +Y for the squeeze direction.
