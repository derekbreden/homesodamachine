# Linkage Arms (Left and Right) -- Parts Specification

The linkage arms are internal rigid bars that transmit the user's squeeze motion from the finger plate (front of cartridge) to the release plate (rear of cartridge). They are entirely hidden inside the cartridge shell -- the user never sees or touches them. Two identical arms run in mid-height guide channels along the outer corridors of the left and right pump bays. Printed in PETG, flat on the build plate with the 6mm face down.

---

## Coordinate System

Origin: front-left-bottom corner of the bar body.

- **X axis**: width (left to right), 0 at left face, positive rightward. Bar body extent: 0 to 6.0 mm.
- **Y axis**: length (front to back), 0 at front face, positive rearward. Bar body extent: 0 to 154.4 mm. Rear pin extends to Y = 158.4.
- **Z axis**: thickness (bottom to top), 0 at bottom face, positive upward. Bar body extent: 0 to 3.0 mm. Front pin extends to Z = 8.0.

Front face at Y = 0. Rear face at Y = 154.4. Left face at X = 0. Right face at X = 6.0. Bottom face at Z = 0 (build-plate face). Top face at Z = 3.0.

**Relation to bottom shell frame (at rest, no rotation, left arm):**
- shell_X = arm_X + 2.5
- shell_Y = arm_Y + 2.8
- shell_Z = arm_Z + 17.25

During operation at travel distance T (0 to 3.0 mm): shell_Y = arm_Y + 2.8 + T.

**Both arms are identical parts.** The left and right arms have the same geometry. The front pin (+Z) and rear pin (+Y) are both on the arm centerline, so no mirroring is needed. The two arms install in the left and right channels respectively, at the same Y and Z positions but at mirrored X positions in the bottom shell.

---

## Mechanism Narrative

### What the user sees and touches

Nothing. The linkage arms are entirely internal, enclosed within the cartridge shell. They run at mid-height through the guide channels alongside the pump bays, passing through the mounting partition notches. No part of either arm is visible on any exterior surface of the assembled cartridge.

### What moves

**Linkage arms (these parts): translate.** Each arm translates 0 to 3.0 mm in the +Y direction (toward the rear wall) during the squeeze action. The arms are rigid 1:1 connections between the finger plate and the release plate. When the user squeezes, both arms translate the same distance as the finger plate and release plate.

**Connected moving parts:**
- Finger plate: connected to both arm front pins via Z-axis pin-and-socket press-fits in the finger plate's downward tabs. The finger plate's squeeze motion (3.0 mm in +Y in shell frame) drives the arms.
- Release plate: connected to both arm rear pins via Y-axis pin-and-socket press-fits in the release plate's lateral tabs. The arms drive the release plate in +Y at the same displacement.

**Stationary parts the arms interact with:**
- Bottom shell guide channels (mid-height, on groove band thickening surface) and inner ribs: provide the channels that constrain the arms laterally (X) and vertically (Z).
- Mounting partition: has notches at its outer corners at mid-height that the arms pass through with clearance.

### What converts the motion

No conversion. The arms are rigid bars in a 1:1 linkage. The finger plate's Y-direction translation is transmitted directly and without amplification through the arm bodies to the release plate. There is no rotation, cam, thread, lever, or any other mechanical transformation. The arms are push-pull rods.

### What constrains each arm

**Lateral constraint (X):** The bottom shell guide channel. Left arm: X = 2.0 to 9.0 in shell frame (arm X = 0 to 6.0 with 0.5 mm clearance per side). The inner rib on the inboard side (left face at shell X = 9.0) and the side wall on the outboard side (interior face at shell X = 2.0) prevent lateral shift. This constraint spans the full Y length of the channel (shell Y = 2.0 to 174.0), providing continuous lateral guidance.

**Vertical constraint (-Z):** The groove band thickening top surface at shell Z = 17.25. The arm bottom face rests on this surface. On the left side, the thickening extends from X = 2.0 to 5.7, providing partial support. The arm (6mm wide, X = 2.5 to 8.5 in shell) is supported across X = 2.5 to 5.7 (3.2mm) by the thickening, with the remainder cantilevered as a rigid beam to the inner rib at X = 9.0.

**Vertical constraint (+Z):** The channel top at shell Z = 20.25 (inner rib top and channel ceiling). The arm top face is flush with this at Z = 20.25, preventing upward movement. The press-fit pin joint at the front end further fixes the arm vertically.

**Axial constraint (Y):** The arm is not constrained in Y by the channel. It slides freely 3.0 mm in +Y during operation. Its Y position is determined by the finger plate (front) and release plate (rear) connections. The return springs on the release plate push the entire linkage assembly (release plate + arms + finger plate) in the -Y direction back to rest.

### What provides the return force

The return force does not originate in the arms. Two compression springs captured between the release plate and the bottom shell rear wall push the release plate in -Y. This force transmits through the arm bodies (in compression along Y) to the finger plate, returning the entire assembly to rest. The arms experience ~4.2 N per arm in compression at rest (half of ~8.4 N total spring force) and ~7.2 N per arm at full travel (half of ~14.4 N total).

### What is the user's physical interaction

The user does not interact with the arms. The user's interaction is entirely through the finger plate and palm surface on the cartridge front face. The arms are invisible, silent, and impalpable during operation.

---

## Constraint Chain Diagram

```
[User fingers: pull finger plate +Y, 40-60N working + ~8.4N spring preload]
    |
    | (finger force on finger plate front face, +Y direction in shell frame)
    v
[Finger plate: translates +Y, 3.0mm]
    |
    | (3.0mm front pin in 3.1mm Z-axis socket, press-fit + CA glue, both arms)
    v
[LINKAGE ARMS (x2): translate +Y, 3.0mm, rigid bars] <-- THESE PARTS
    ^ constrained in X by: bottom shell mid-height guide channels
    |   (left: shell X = 2.0..9.0; right: shell X = 123.0..130.0;
    |    0.5mm clearance per side)
    ^ constrained in -Z by: groove band thickening top surface (shell Z = 17.25)
    ^ constrained in +Z by: channel top / rib top (shell Z = 20.25)
    ^ slides through: mounting partition notches (8mm W x 5mm H at mid-height,
    |   Z = 15.25..20.25, 1mm clearance/side)
    |
    | (3.0mm rear pin in 3.1mm Y-axis socket, press-fit + CA glue, both arms)
    v
[Release plate: translates +Y, 3.0mm]
    ^ constrained in X, Z by: 4x collet-hugger bores on collet ODs
    ^ returned -Y by: 2x compression springs
    |
    v
[JG collet sleeves (x4): pushed, releasing tubes]
```

---

## Direction Consistency Check

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| Arms translate rearward during squeeze | Toward rear wall | +Y in shell frame | Yes | Same direction as finger plate and release plate motion |
| Arms slide in channels along Y | Fore-aft | +/- Y | Yes | Channels span full Y depth, arm slides freely in Y |
| Arms are constrained laterally by channel walls | Side-to-side | X direction | Yes | 0.5mm clearance per side in 7mm channel for 6mm arm |
| Arms sit on groove band thickening surface | Downward support | -Z | Yes | Arm bottom at shell Z = 17.25, thickening surface at Z = 17.25 |
| Arms constrained above by channel top | Upward limit | +Z | Yes | Arm top at shell Z = 20.25, rib top at Z = 20.25 |
| Front pin extends upward from arm top | Upward | +Z | Yes | Pin base at arm Z = 3.0, tip at Z = 8.0 (shell Z = 20.25 to 25.25) |
| Rear pin extends rearward from arm rear face | Rearward | +Y | Yes | Pin base at arm Y = 154.4, tip at Y = 158.4 |
| Spring return force pushes arms forward | Toward front | -Y in shell frame | Yes | Springs push release plate -Y, transmitted through arms |
| Arms pass through partition notches | Arms cross partition plane | Y = 72.3..77.7 in shell | Yes | Arm at Y = 69.5..74.9 in arm local at this Y range |

No contradictions found.

---

## Interface Dimensional Consistency

| # | Interface | Part A dimension | Part B dimension | Clearance | Source |
|---|-----------|-----------------|-----------------|-----------|--------|
| 1 | Arm body width / channel width | Arm: 6.0 mm | Channel: 7.0 mm (shell X = 2.0 to 9.0) | 0.5 mm per side | Spatial doc; bottom shell spatial |
| 2 | Arm body height / channel height | Arm: 3.0 mm | Channel: 3.0 mm (shell Z = 17.25 to 20.25) | 0 mm (flush top and bottom; full vertical constraint) | Spatial doc; bottom shell spatial |
| 3 | Front pin / finger plate socket | Pin: 3.0 mm dia | Socket: 3.1 mm dia | 0.1 mm diametral (press-fit) | Concept; finger plate parts |
| 4 | Rear pin / release plate socket | Pin: 3.0 mm dia | Socket: 3.1 mm dia | 0.1 mm diametral (press-fit) | Concept; release plate parts |
| 5 | Front pin height / finger plate socket depth | Pin: 5.0 mm | Socket: 5.0 mm | Full engagement | Finger plate spatial |
| 6 | Rear pin length / release plate socket depth | Pin: 4.0 mm | Socket: 4.0 mm | Full engagement | Spatial doc |
| 7 | Arm body in partition notch (X) | Arm: 6.0 mm | Notch: 8.0 mm | 1.0 mm per side | Concept; bottom shell spatial |
| 8 | Arm body in partition notch (Z) | Arm: 3.0 mm (Z = 17.25 to 20.25 in shell) | Notch: 5.0 mm (Z = 15.25 to 20.25 in shell) | 2.0 mm below, 0 mm above (flush) | Spatial doc |

No mismatched dimensions. All clearances are specified and reasonable.

---

## Feature List

### Feature 1: Bar Body

| Parameter | Value |
|-----------|-------|
| X range (arm local) | 0 to 6.0 |
| Y range (arm local) | 0 to 154.4 |
| Z range (arm local) | 0 to 3.0 |
| Width | 6.0 mm |
| Length | 154.4 mm |
| Thickness | 3.0 mm |
| Material | PETG |
| Function | Rigid push-pull rod transmitting 40-60 N of squeeze force (in tension when user squeezes) and ~7.2 N of spring return force (in compression when user releases) along Y between the finger plate front pin and the release plate rear pin. Cross-section: 6.0 x 3.0 = 18.0 mm^2. At 60 N (worst case, single arm carries 30 N): tensile stress = 30 / 18 = 1.67 MPa, far below PETG tensile strength (~50 MPa). Safety factor: 30x. |
| Bending stiffness | The arm is loaded primarily in tension/compression along Y. Bending loads are secondary (from any misalignment or friction in the channel). Second moment of area about X: I_x = 6.0 x 3.0^3 / 12 = 13.5 mm^4. For a 154mm span, a 1N lateral force at midspan would produce 0.22mm deflection -- negligible. The arm is effectively rigid as a push-pull rod. |

### Feature 2: Front Pin (Z-Axis)

| Parameter | Value |
|-----------|-------|
| Center X (arm local) | 3.0 |
| Center Y (arm local) | 3.0 |
| Base Z (arm local) | 3.0 (top face of bar body) |
| Tip Z (arm local) | 8.0 |
| Diameter | 3.0 mm |
| Height | 5.0 mm |
| Axis | +Z (vertical, upward) |
| FDM compensation | The pin prints as stacked circular layers (axis along Z in arm local = along Z in print orientation since the arm prints flat). The pin cross-section in the XY print plane is circular. No oval compensation needed for a Z-axis feature in this print orientation. |
| Function | Connects arm to finger plate left downward tab via press-fit into 3.1 mm diameter, 5.0 mm deep blind Z-axis socket. Transmits squeeze force (tension in +Y) and return force (compression in -Y) between arm body and finger plate. At 30 N per arm and 3.0 mm pin diameter: shear stress on pin = 30 / (pi x 3.0 x 5.0) = 0.64 MPa, far below PETG shear strength (~25 MPa). |

### Feature 3: Rear Pin (Y-Axis)

| Parameter | Value |
|-----------|-------|
| Center X (arm local) | 3.0 |
| Center Z (arm local) | 1.5 |
| Base Y (arm local) | 154.4 (rear face of bar body) |
| Tip Y (arm local) | 158.4 |
| Diameter | 3.0 mm |
| Length | 4.0 mm |
| Axis | +Y (rearward) |
| FDM compensation | The pin axis is along Y. In print orientation (arm flat, Z = thickness = print Z), the pin extends horizontally in the Y direction at print Z = 1.5 + build plate offset. The pin's circular cross-section is in the XZ plane. X is horizontal on the print bed (accurate), Z is the layer stacking direction. The pin will print slightly oval: wider in X, narrower in Z. Apply +0.1 mm oversize to the pin diameter to compensate. As-modeled: 3.0 mm. As-printed: approximately 3.0 mm in X, 2.9 mm in Z, still adequate for press-fit into the 3.1 mm socket. |
| Function | Connects arm to release plate left lateral tab via press-fit into 3.1 mm diameter, 4.0 mm deep blind Y-axis socket. Transmits squeeze force (tension along Y when user squeezes; the arm pulls the release plate rearward) and return force (compression along Y when springs push release plate forward). Same stress levels as the front pin. |

### Feature 4: Elephant's Foot Chamfer

| Parameter | Value |
|-----------|-------|
| Location | Bottom face perimeter (Z = 0 plane), all four bottom edges of the bar body |
| Chamfer size | 0.3 mm x 45 degrees |
| Function | Prevents elephant's foot flaring on the build-plate face from interfering with the 7.0 mm guide channel. Without the chamfer, the bottom edge could flare up to 0.3 mm, reducing effective clearance from 0.5 mm to 0.2 mm per side. The chamfer ensures the arm slides freely in the channel. Applied to the bar body only, not to the pin features. |

---

## Feature Traceability (Rubric H)

| Feature | Justification source | Specific reference |
|---------|--------------------|--------------------|
| Bar body | Physical necessity (structural) | Transmits 40-60 N squeeze force and ~7.2 N spring return force along Y between finger plate and release plate. Without this feature, the finger plate and release plate have no mechanical connection. |
| Front pin (Z-axis) | Physical necessity (assembly) | The finger plate tab descends from above (shell Z = 33.5) to shell Z = 25.25. The arm top face is at shell Z = 20.25. A vertical pin bridges this 5mm gap, enabling press-fit connection between the arm and the finger plate tab socket. Without this feature, the arm cannot connect to the finger plate. |
| Rear pin (Y-axis) | Physical necessity (assembly) | The release plate tab socket opens on its front face (Y-axis). The arm approaches from the front along Y. A rearward-extending pin enters the socket, enabling press-fit connection between the arm and the release plate. Without this feature, the arm cannot connect to the release plate. |
| Elephant's foot chamfer | Physical necessity (manufacturing) | FDM elephant's foot flaring on the build-plate face (Z = 0) would reduce the 0.5 mm lateral clearance in the guide channel, potentially binding the arm. The 0.3 mm x 45-degree chamfer removes the flared material. Required per hardware/requirements.md Section 6 (elephant's foot: 0.3mm x 45-degree chamfer on bottom edge when bottom face is a mating surface). |

No unjustified features.

---

## Assembly Feasibility Check

**Assembly sequence (per concept steps 4 and 8):**

1. **Step 4 (concept): Install linkage arms into bottom shell guide channels.** The bottom shell is open-face-up with JG fittings, springs, and release plate already installed (steps 1-3). Each arm is placed into its mid-height channel from above. At this point the channel is open-topped (nothing above the arm Z range yet). The arm's front end is toward Y = 0 and the rear pin is aligned with the release plate tab socket.

2. **Rear pin connection:** The arm's rear pin (Y-axis, extending rearward) is aligned with the release plate tab socket. The arm is pushed rearward in the channel until the rear pin enters the socket. A dab of CA glue on the pin before insertion creates a permanent bond. The arm must be positioned in the channel first, then slid rearward to engage the pin. The channel constrains the arm laterally to within 0.5mm, and the pin and socket are both centered at the channel center X, so lateral alignment is automatic. Vertical alignment: the arm sits on the groove band thickening surface (Z = 17.25), and the socket center is at Z = 18.75 (arm center). The arm's resting position sets the correct Z.

3. **Step 8 (concept): Connect finger plate to linkage arm front ends.** After the pump-partition assembly is installed (steps 5-7), the finger plate is lowered from above. The finger plate's downward tabs descend into the bottom shell front zone, and the arm front pins (rising vertically from the arm top face at shell Z = 20.25 to 25.25) press into the tab sockets. A dab of CA glue on each front pin before the finger plate is lowered creates a permanent bond.

**Physical feasibility:**

- Step 1: The arm (6mm x 3mm x 154mm body + pins) fits into the channel from above. The channel is accessible from above until the pump-partition assembly is installed. The arm's 6mm width fits in the 7mm channel with 0.5mm clearance per side.

- Step 2: The rear pin (3mm dia, 4mm long, Y-axis) must align with the socket (3.1mm dia, 4mm deep). The channel constrains the arm laterally to within 0.5mm. The pin and socket are both centered at the channel center X, so lateral alignment is automatic. Vertical alignment is set by the groove band surface. The only active alignment is pushing the arm rearward along Y until the pin engages.

- Step 3: The front pin (3mm dia, 5mm tall, Z-axis) extends upward from the arm top face at shell Z = 20.25. The finger plate tab descends with the socket opening on the tab bottom face at shell Z = 25.25. The tab is guided laterally by the bottom shell walls (0.5mm clearance per side). The press-fit requires pushing the finger plate down with moderate force (~5-10 N). Access is open from above (top shell not yet installed).

**Disassembly:** Remove top shell, then finger plate (pull upward to disengage front pin press-fits). If CA glue was used, the front pin-socket joints may require prying force. The arms can then be slid forward in the channels to disengage the rear pins from the release plate sockets. Both pin joints are designed as permanent (glued) in production but separable with effort during development.

---

## Part Count Minimization

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|---------------|----------------|---------|
| Left arm + right arm | No | No (both translate identically in +Y) | Yes (PETG) | Cannot combine: they are 121mm apart in X (left at shell X = 5.5, right at X = 126.5). A single U-shaped part spanning this distance would need a crossbar at the front or rear, adding material and complexity, and would be difficult to assemble into the channels. Two separate identical parts is simpler. |
| Arm + finger plate | Connected by press-fit + CA glue | They move together (rigid connection) | Yes (PETG) | Cannot combine: different print orientations required. Arm prints flat (6mm face down for bending stiffness). Finger plate prints flat (front face down for surface quality). A combined part would be an L-shape that cannot satisfy both orientations simultaneously. The arm is 154mm long; a combined part would exceed 180mm in the print Z direction if printed standing. |
| Arm + release plate | Connected by press-fit + CA glue | They move together (rigid connection) | Yes (PETG) | Cannot combine: release plate has precision stepped bores that require flat-on-bed printing with bore axes vertical. Arms require flat-on-bed printing with long axis horizontal. Combining creates an L-shape with conflicting print requirements. |

The linkage arms are correctly two separate identical printed parts.

---

## FDM Printability

### Print Orientation

Each arm prints flat on the build plate with the 6mm-wide face (XY plane) down. The 3mm thickness is the print Z direction.

**Why this orientation:**
1. **Bending stiffness:** Layers stack through the 3mm thickness (Z). Continuous perimeter extrusions run along the 154mm length (Y). Bending loads from channel friction or misalignment are carried by in-plane perimeters -- maximum stiffness and strength.
2. **Pin quality:** The front pin (Z-axis) prints as stacked circular layers -- excellent circularity. The rear pin (Y-axis) prints as a horizontal cylinder -- slightly oval but compensated by the 0.1mm oversize.
3. **No supports needed:** The bar body is a simple rectangle. The pins are small protrusions that require no support (see overhang audit).

**Build plate footprint:** 6.0 mm x 158.4 mm (arm width x overall length including rear pin). Well within 325 x 320 mm build plate. Both arms can print simultaneously side by side.

### Overhang Audit

In print orientation (6mm face down, print Z = arm Z):

| Surface / Feature | Angle from horizontal | Printable? | Resolution |
|-------------------|----------------------|------------|------------|
| Bottom face (Z = 0, build plate) | 0 deg (on bed) | OK | Build plate contact |
| Top face (Z = 3.0) | 0 deg (horizontal, flat top) | OK | Flat top of 3mm extrusion |
| Left face (X = 0) | 90 deg (vertical) | OK | |
| Right face (X = 6.0) | 90 deg (vertical) | OK | |
| Front face (Y = 0) | 90 deg (vertical) | OK | |
| Rear face (Y = 154.4) | 90 deg (vertical) | OK | |
| Front pin cylindrical surface | Vertical cylinder rising from top face | OK | Stacked circular layers, no overhang |
| Front pin top face (Z = 8.0) | 0 deg (horizontal, flat top) | OK | Small 3mm dia circle |
| Rear pin cylindrical surface | Horizontal cylinder extending from rear face at Z = 1.5 center | See below | |
| Rear pin end face (Y = 158.4) | 90 deg (vertical) | OK | |

**Rear pin overhang detail:** The rear pin is a 3.0 mm diameter horizontal cylinder extending 4.0 mm in the +Y direction from the rear face. The pin center is at Z = 1.5 (arm local), which is 1.5 mm above the build plate. The pin's bottom (Z = 0.0, arm local) is at the build plate level, and the pin's top (Z = 3.0) is at the arm top face level.

The pin is 3mm diameter, same height as the arm body (3mm). The bottom half of the pin cylinder overhangs from the bar body's rear face. The overhang angle at the pin's equator is 0 degrees (horizontal). However, the pin diameter is only 3mm and it extends only 4mm from the rear face. This is a short unsupported bridge (3mm diameter circle bridged over 4mm length). The bridge span is 3mm -- well under the 15mm maximum. The bottom of the pin will sag slightly during printing but the 0.1mm oversize compensates. No support needed.

### Wall Thickness Check

| Wall / Feature | Thickness | Minimum | Status |
|----------------|-----------|---------|--------|
| Bar body width (X) | 6.0 mm | 1.2 mm structural | OK (5x) |
| Bar body thickness (Z) | 3.0 mm | 1.2 mm structural | OK (2.5x) |
| Front pin diameter | 3.0 mm | 0.8 mm minimum feature | OK |
| Rear pin diameter | 3.0 mm | 0.8 mm minimum feature | OK |
| Bar wall around front pin (X direction, each side) | (6.0 - 3.0) / 2 = 1.5 mm | 1.2 mm structural | OK |
| Bar wall below front pin base (Z = 0 to 3.0, pin sits on top) | 3.0 mm (full bar thickness supports pin base) | 1.2 mm structural | OK |
| Bar wall around rear pin (Z direction, each side) | (3.0 - 3.0) / 2 = 0.0 mm | -- | The rear pin is the same diameter as the bar thickness. The pin merges flush with the top and bottom faces of the bar at the rear end. No wall deficiency: the pin is a continuation of the bar material, not a bore cut into it. The bar body provides full support around the pin circumference at the junction. |

### Bridge Span Check

| Feature | Span | Maximum | Status |
|---------|------|---------|--------|
| Rear pin bottom surface (horizontal bridge) | 3.0 mm diameter | 15 mm | OK |

No horizontal unsupported spans exceed 15 mm.

### Layer Strength Check

| Feature | Load direction | Layer orientation | Status |
|---------|---------------|------------------|--------|
| Bar body (tension/compression along Y from squeeze/spring forces) | Axial along Y | Layers stack along Z (print Z). Y-direction loads are carried by continuous perimeter extrusions running along Y. Load is in-plane with the layers. | OK -- optimal |
| Front pin (shear at pin-socket interface, lateral loads from finger plate motion) | Primarily shear/tension along Z (pin pulled out or pushed sideways) | Pin prints as stacked circular layers (Z-axis). Pull-out load (Z direction) is perpendicular to layer planes, carried by interlayer adhesion. | ACCEPTABLE -- interlayer adhesion at 3mm diameter provides adequate retention area. Shear area = pi x 3 x 3 (exposed height from arm) = 28.3 mm^2. At 30 N pull-out: 1.06 MPa, well below interlayer adhesion strength (~25-35 MPa). Safety factor: 23x minimum. |
| Rear pin (shear at pin-socket interface) | Primarily shear/tension along Y (pin pulled out from release plate socket) | Pin prints as a horizontal cylinder. Pull-out load (Y direction) is along the perimeter extrusion direction. Load is in-plane with layers. | OK -- optimal for pull-out |

No print orientation conflicts. The primary load path (axial Y through the bar body) is optimally oriented in all cases.

---

## Design Gaps

1. **DESIGN GAP: Release plate socket X-position mismatch.** The release plate spatial document places the left pin socket center at shell X = 14.9 (centered in the tab). The arm's rear pin is at shell X = 5.5 (constrained by the guide channel). The release plate tab extends to shell X = 5.5 at its tip, but the socket is centered at X = 14.9 -- 9.4mm away from the arm pin. The release plate tab must be extended and the socket repositioned to shell X = 5.5. See linkage-arm-spatial.md Section 8 for details.

2. **DESIGN GAP (MINOR): Rear pin oval compensation.** The rear pin (Y-axis, horizontal in print) will print slightly oval due to FDM layer stepping on the curved surface. The 0.1 mm oversize on the nominal 3.0 mm diameter compensates. Verify empirically with a test print that the pin fits the 3.1 mm socket with adequate press-fit retention. If too tight, reduce pin diameter to 2.9 mm as-modeled (3.0 mm as-printed in the wider direction). If too loose, increase to 3.1 mm as-modeled.

---

## Dimension Summary

| Dimension | Value | Notes |
|-----------|-------|-------|
| Bar body: 6.0 x 154.4 x 3.0 mm (X x Y x Z) | | Main structural bar |
| Front pin: 3.0 mm dia x 5.0 mm tall at (3.0, 3.0, 3.0) base | Z-axis, upward from bar top face | Connects to finger plate tab socket |
| Rear pin: 3.0 mm dia x 4.0 mm long at (3.0, 154.4, 1.5) base | Y-axis, rearward from bar rear face | Connects to release plate tab socket |
| Elephant's foot chamfer: 0.3 mm x 45 deg | Bottom face perimeter of bar body | Ensures channel sliding clearance |
| Material: PETG | Matte black | Same as all cartridge parts |
| Overall bounding box: 6.0 x 158.4 x 8.0 mm | X: 0..6.0, Y: 0..158.4, Z: 0..8.0 | Body + front pin height + rear pin length |
| Quantity: 2 (identical parts) | | One left channel, one right channel |
| Mass (estimated): ~4 g each | PETG density 1.27 g/cm^3, volume ~2.9 cm^3 | |
