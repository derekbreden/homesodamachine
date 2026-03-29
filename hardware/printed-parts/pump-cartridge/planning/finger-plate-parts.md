# Finger Plate -- Parts Specification

The finger plate is the user-facing squeeze surface on the front face of the pump cartridge. The user's fingers curl around and pull this surface toward the palm surface during cartridge removal. It is the only moving part visible to the user. Printed in PETG, flat on the build plate with the front (user-facing) face down. The plate translates 2-4 mm in the -Y direction (rearward, into the cartridge) when the user squeezes, pulling the release plate via two rigid linkage arms. Two downward tabs extend from the visible plate body into the bottom shell interior to connect with the linkage arm front-end pins at mid-height.

---

## Coordinate System

Origin: front-left-bottom corner of the visible plate body.

- **X axis**: width (left to right), 0 at left face of visible body, positive rightward. Visible body extent: 0 to 120.0 mm. Downward tabs extend to X = -3.5 (left tab left face) and X = 123.5 (right tab right face).
- **Y axis**: depth (front face to rear face), 0 at front face (user-facing surface), positive rearward. Visible body extent: 0 to 4.0 mm. Tabs extend to Y = 5.0.
- **Z axis**: height (bottom to top of visible body), 0 at bottom face (parting line level), positive upward. Visible body extent: 0 to 24.5 mm. Tabs extend to Z = -8.25.

Front face at Y = 0 (user-facing, build-plate face). Rear face at Y = 4.0 (faces cartridge interior). Left edge at X = 0. Right edge at X = 120.0. Bottom of visible body at Z = 0. Top at Z = 24.5.

**Relation to bottom shell frame (at rest, no rotation):**
- shell_X = plate_X + 6.0
- shell_Y = plate_Y + 3.3
- shell_Z = plate_Z + 33.5

During operation at travel distance T (0 to 4.0 mm, practical limit 3.0 mm): shell_Y = plate_Y + 3.3 - T.

---

## Mechanism Narrative

### What the user sees and touches

The front face of the pump cartridge has two flat zones separated by a 3.0 mm recess. The upper zone is the palm surface -- a fixed, continuous PETG surface that is part of the top shell front wall. The lower zone is the finger plate -- a separate PETG plate recessed 3.0 mm behind the palm surface, spanning most of the cartridge width (120.0 mm wide, 24.5 mm tall visible portion).

A 0.5 mm gap surrounds the finger plate on three sides (left, right, and top) where it sits within the rectangular slot in the top shell front wall (121.0 mm wide x 25.0 mm tall slot). This gap communicates that the finger plate moves. The bottom of the slot is open at the shell parting line; the finger plate extends downward past this point, but the 0.3 mm parting-line step between the top and bottom shell hides the transition.

The finger plate's front face carries the same crosshatch grip texture as the palm surface: 0.2 mm deep grooves, 0.4 mm wide, at 1.0 mm pitch in a perpendicular crosshatch pattern. The front face is the build-plate face when printed -- the smoothest possible FDM surface with texture embossed through slicer settings or a textured build plate. Matte black PETG, matching the rest of the cartridge.

### What moves

**Finger plate (this part): translates.** The plate translates 0 to 4.0 mm in the -Y direction (rearward, into the cartridge) during the squeeze action. Practical limit is 3.0 mm, set by the release plate's maximum stroke. At rest, the front face is at Y = 3.3 in the bottom shell frame (3.0 mm behind the top shell front exterior at Y = 0.3). At practical full travel (3.0 mm), the front face is at Y = 0.3 in the bottom shell frame.

**Stationary parts the finger plate interacts with:**
- Top shell front wall (the finger plate slot). The slot side walls and upper edge constrain the plate laterally (X) and vertically (Z) during sliding. The slot walls do not move.
- Bottom shell interior (front zone). The downward tabs descend through the bottom shell interior with clearance to the side walls.

**Other moving parts connected to the finger plate:**
- Two linkage arms (rigid PETG bars), connected to the finger plate tabs via pin-and-socket press-fit joints (3.0 mm pins from the arms pressing into 3.1 mm sockets in the tabs). The arms transmit the finger plate's -Y motion to the release plate's +Y motion (the arms translate in -Y at the front end and +Y at the rear end -- they are rigid bars, so both ends move the same direction and distance; the release plate's frame defines its motion as +Y toward the rear wall, which is the same absolute direction as the finger plate's -Y motion).

### What converts the motion

No conversion. The finger plate is the input end of a 1:1 rigid linkage. The user pulls the finger plate rearward (-Y); the two linkage arms transmit this translation directly to the release plate as a +Y translation (same absolute direction, same magnitude). No amplification, no rotation, no cam or lever.

### What constrains the finger plate

**Lateral constraint (X):** The top shell finger plate slot side walls (121.0 mm wide slot, 120.0 mm wide plate, 0.5 mm clearance per side). The slot side walls are rigid 5.2 mm wide PETG columns flanking the slot. Slot left edge at assembly X = 5.5; slot right edge at X = 126.5. Plate left edge at X = 6.0; plate right edge at X = 126.0. The 0.5 mm clearance allows free sliding without visible daylight (per design patterns research: seam gaps under 0.3 mm for finished appearance, but this is a functional sliding gap at 0.5 mm, which reads as intentional because the slot geometry communicates "this part moves").

**Vertical constraint (+Z):** The slot upper edge (assembly Z = 58.5) prevents the plate from shifting upward. The plate top edge is at assembly Z = 58.0, with 0.5 mm clearance.

**Vertical constraint (-Z):** The plate extends below the parting line. At the parting line (assembly Z = 33.5), the top and bottom shell walls together constrain the plate from shifting downward beyond the clearance gaps. The downward tabs are constrained by the bottom shell side walls (0.5 mm clearance per side in X).

**Axial constraint (+Y, rest position):** The return springs (on the release plate, transmitted through the linkage arms) push the finger plate in the +Y direction (toward the user). The finger plate's rest position is set by the equilibrium between the spring return force and the physical interference between the linkage arm pins and their sockets. At rest, the front face sits at 3.0 mm behind the palm surface plane. There is no mechanical stop at the rest position -- the springs continuously bias the plate forward.

**Axial constraint (-Y, squeeze limit):** The release plate's collet mechanical stops and compression springs limit the total travel. The release plate travels 3.0 mm maximum. The finger plate, connected 1:1 through the linkage arms, also stops at 3.0 mm of practical travel. The cartridge geometry permits up to 4.0 mm of physical clearance in -Y, but the mechanism stops at 3.0 mm.

### What provides the return force

Two compression springs captured between the release plate rear face and the bottom shell rear wall. The spring force is transmitted through the rigid linkage: release plate -> linkage arm rear pins -> linkage arm bodies -> linkage arm front pins -> finger plate tab sockets. The finger plate itself has no springs. Return force at rest: ~8.4 N total. Return force at full travel: ~14.4 N total.

### What is the user's physical interaction

The user wraps one hand around the cartridge front face. The palm rests on the palm surface (top shell front wall exterior). The fingers curl underneath and rest on the finger plate front face. The user squeezes by pulling the finger plate toward the palm. The squeeze motion is along the Y axis (front-to-back of the cartridge).

The user feels:
1. **Light initial resistance** (~8.4 N from spring preload) over the first ~1.0 mm of travel (the take-up gap before the release plate contacts the collets).
2. **Rising resistance** as the release plate engages and depresses all four collets (40-60 N combined over the next ~1.3 mm of travel).
3. **Sharp force drop** as the collet grab ring teeth clear the tube surfaces. This is the tactile "click" that confirms release.
4. **Firm stop** at the end of travel (mechanism limit at ~3.0 mm).

The grip texture on the front face (crosshatch, 0.2 mm deep, 1.0 mm pitch) prevents the fingers from slipping under the 40-60 N load. The 120 mm width distributes finger pressure across 3-4 fingers. The 24.5 mm visible height provides adequate contact area for comfortable finger purchase.

---

## Constraint Chain Diagram

```
[User fingers: pull finger plate -Y, 40-60N working + ~8.4N spring preload]
    |
    | (finger force on front face, -Y direction)
    v
[FINGER PLATE: translates -Y, 3.0mm practical max] <-- THIS PART
    ^ constrained in X by: top shell slot side walls (0.5mm clearance per side)
    ^ constrained in +Z by: top shell slot upper edge (0.5mm clearance)
    ^ constrained in -Z by: parting line geometry (shell walls)
    ^ returned in +Y by: springs (via linkage arms from release plate)
    |
    | (3.0mm arm pin in 3.1mm tab socket, press-fit, Z-axis, left and right)
    v
[Linkage arms (x2): translate -Y, 3.0mm, rigid 1:1 connection]
    ^ constrained laterally (X) by: bottom shell mid-height guide rib channels
    ^ constrained vertically (-Z) by: groove band thickening top surface (Z = 17.25)
    |
    | (3.0mm arm pin in 3.1mm socket, press-fit, X-axis, left and right)
    v
[Release plate: translates +Y (same absolute direction), 3.0mm]
    |
    v
[JG collet sleeves (x4): pushed, releasing tubes]
```

---

## Direction Consistency Check

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| User pulls finger plate rearward | Rearward = toward rear of cartridge = into cartridge | -Y | Yes | Consistent with squeeze action description |
| Finger plate slides in slot | Rearward | -Y | Yes | Slot permits Y-axis travel only |
| Linkage arms transmit motion to release plate | Same absolute direction (rearward) | -Y at finger plate end, +Y in release plate frame | Yes | Both refer to the same physical direction (toward rear wall). Release plate frame defines +Y as toward rear. |
| Springs return finger plate forward | Forward = toward user | +Y | Yes | Springs push release plate in -Y (away from rear wall), transmitted through arms to finger plate as +Y |
| Finger plate front face recessed behind palm surface | Rearward from palm plane | +Y offset from palm exterior | Yes | Palm at assembly Y = 0.3, finger plate at Y = 3.3, difference = 3.0mm in +Y |
| Tabs extend downward from visible plate body | Downward | -Z | Yes | Tabs span plate local Z = -8.25 to 0, assembly Z = 25.25 to 33.5 |
| Arm pins point upward into tab sockets | Upward | +Z | Yes | Arm body top at Z = 20.25, pin rises to Z = 25.25, socket at tab bottom face Z = 25.25 |

No contradictions found.

---

## Interface Dimensional Consistency

| # | Interface | Part A dimension | Part B dimension | Clearance | Source |
|---|-----------|-----------------|-----------------|-----------|--------|
| 1 | Finger plate width / slot width | Plate: 120.0 mm | Slot: 121.0 mm | 0.5 mm per side (1.0 mm total) | Spatial doc; top shell parts |
| 2 | Finger plate height / slot height | Plate visible: 24.5 mm | Slot: 25.0 mm | 0.5 mm at top only (bottom open) | Spatial doc; top shell parts |
| 3 | Left tab socket / left arm pin | Socket: 3.1 mm dia | Pin: 3.0 mm dia | 0.1 mm diametral (press-fit) | Concept; spatial doc |
| 4 | Right tab socket / right arm pin | Socket: 3.1 mm dia | Pin: 3.0 mm dia | 0.1 mm diametral (press-fit) | Concept; spatial doc |
| 5 | Left tab / left side wall | Tab left face: shell X = 2.5 | Wall interior: shell X = 2.0 | 0.5 mm | Spatial doc |
| 6 | Right tab / right side wall | Tab right face: shell X = 129.5 | Wall interior: shell X = 130.0 | 0.5 mm | Spatial doc |
| 7 | Pin socket depth / arm pin height | Socket: 5.0 mm deep | Pin: 5.0 mm tall (Z = 20.25 to 25.25) | Flush engagement (full pin insertion) | Spatial doc |
| 8 | Tab bottom face / arm pin top | Tab bottom: shell Z = 25.25 | Pin top: shell Z = 25.25 | 0 mm (flush contact when pin fully inserted) | Spatial doc |

No mismatched dimensions. All clearances are reasonable and specified. Interface #3 and #4 (0.1 mm press-fit clearance) matches the concept specification and the release plate's identical pin-and-socket joints.

Note: Interfaces 5-6 previously also checked tab-to-rib clearance. The tabs (shell Z = 25.25 to 33.5) are now entirely above the inner rib tops (Z = 20.25), so there is no X-direction overlap between the tabs and the guide ribs. The only lateral clearance concern is the side walls.

---

## Feature List

### Feature 1: Visible Plate Body

| Parameter | Value |
|-----------|-------|
| X range (plate local) | 0 to 120.0 |
| Y range (plate local) | 0 to 4.0 |
| Z range (plate local) | 0 to 24.5 |
| Width | 120.0 mm |
| Thickness | 4.0 mm |
| Height | 24.5 mm |
| Material | PETG |
| Function | Primary user-contact surface (finger side of squeeze). Provides rigid surface for distributing finger force across 120 mm width. Transmits 40-60 N squeeze force through the downward tabs to the linkage arm pins. The 4.0 mm thickness provides bending stiffness across the 120 mm span: for a simply supported beam (supported at the two tab positions, span = 120 mm, width = 24.5 mm, thickness = 4.0 mm) under 60 N center load, maximum deflection = (60 x 120^3) / (48 x 2100 x 24.5 x 4.0^3 / 12) = ~0.6 mm. This deflection is barely perceptible to the user and does not affect mechanism function. |

### Feature 2: Left Downward Tab

| Parameter | Value |
|-----------|-------|
| X range (plate local) | -3.5 to 2.5 |
| Y range (plate local) | 0 to 5.0 |
| Z range (plate local) | -8.25 to 0 |
| Width (X) | 6.0 mm |
| Thickness (Y) | 5.0 mm |
| Length (Z) | 8.25 mm |
| Function | Structural bridge connecting visible plate body to left linkage arm front-end pin. Transmits squeeze force in tension (pulling arm rearward) and return spring force in compression (pushing plate forward). Cross-section: 6.0 x 5.0 = 30.0 mm^2. At 60 N tensile load: 2.0 MPa, well below PETG tensile strength (~50 MPa). |
| Wall around socket | X: 1.45 mm per side (above 1.2 mm structural min). Y: 0.95 mm per side (above 0.8 mm non-structural min, adequate for cyclic load path along Z axis). |

### Feature 3: Right Downward Tab

Mirror of Feature 2.

| Parameter | Value |
|-----------|-------|
| X range (plate local) | 117.5 to 123.5 |
| Y range (plate local) | 0 to 5.0 |
| Z range (plate local) | -8.25 to 0 |
| Width (X) | 6.0 mm |
| Thickness (Y) | 5.0 mm |
| Length (Z) | 8.25 mm |
| Function | Same as left tab. Mirror geometry. |

### Feature 4: Left Pin Socket

| Parameter | Value |
|-----------|-------|
| Center (plate local) | (-0.5, 2.5, -8.25) -- at socket opening |
| Socket opening face | Z = -8.25 (bottom face of left tab) |
| Socket blind end | Z = -3.25 |
| Diameter | 3.1 mm (3.0 mm arm pin + 0.1 mm FDM press-fit clearance) |
| Depth | 5.0 mm (upward into tab, from Z = -8.25 to -3.25) |
| Axis | Z (vertical, pin enters from below) |
| Function | Accepts the 3.0 mm diameter cylindrical pin at the front end of the left linkage arm. Press-fit joint with CA glue for permanent retention. The 0.1 mm diametral clearance provides a snug press-fit accounting for FDM dimensional variation. The 5.0 mm depth provides 5.0 mm of shear engagement along the pin surface, adequate for the cyclic 30 N per arm tensile load. |

### Feature 5: Right Pin Socket

Mirror of Feature 4.

| Parameter | Value |
|-----------|-------|
| Center (plate local) | (120.5, 2.5, -8.25) -- at socket opening |
| Socket opening face | Z = -8.25 (bottom face of right tab) |
| Socket blind end | Z = -3.25 |
| Diameter | 3.1 mm |
| Depth | 5.0 mm |
| Axis | Z (vertical) |
| Function | Same as left socket. Mirror geometry. |

### Feature 6: Crosshatch Grip Texture

| Parameter | Value |
|-----------|-------|
| Location | Front face (Y = 0) of visible plate body |
| X range | 0 to 120.0 |
| Z range | 0 to 24.5 |
| Pattern | Two sets of parallel grooves at 90 degrees (crosshatch) |
| Groove depth | 0.2 mm into front face surface |
| Groove width | 0.4 mm |
| Groove pitch | 1.0 mm center-to-center |
| Function | Prevents finger slip under 40-60 N squeeze load. Matches the palm surface texture on the top shell for visual consistency. Applied via slicer bottom-layer pattern settings (the front face is the build-plate face) or a textured build plate. |

**Note on texture implementation:** The crosshatch texture is specified as a surface treatment, not a geometric feature in the STEP model. It is applied during slicing via the slicer's bottom pattern settings (e.g., grid pattern with 1.0 mm spacing) or by printing on a textured build plate. The STEP model represents the front face as a smooth plane at Y = 0. The 0.2 mm texture depth is negligible for dimensional purposes and does not affect any interface clearance.

### Feature 7: Elephant's Foot Chamfer

| Parameter | Value |
|-----------|-------|
| Location | All perimeter edges of the front face (Y = 0) on the visible plate body only |
| Chamfer size | 0.3 mm x 45 degrees |
| Function | Prevents elephant's foot flaring on the build-plate face from affecting the sliding fit in the top shell slot. The chamfer is on the visible plate body perimeter only -- not on the tab faces, which are at the top of the print and not subject to elephant's foot. |
| Edges chamfered | Top edge (Z = 24.5, Y = 0), bottom edge (Z = 0, Y = 0), left edge (X = 0, Y = 0), right edge (X = 120.0, Y = 0) |

---

## Assembly Feasibility Check

**Assembly sequence (finger plate into the cartridge, per concept step 8):**

1. The bottom shell is assembled with JG fittings, springs, release plate, linkage arms in mid-height channels, pump-partition assembly, and tube routing (concept steps 1-7).
2. The linkage arm front-end pins are pointing upward (+Z) from the arm bodies at approximately shell Z = 20.25 to 25.25, near the front of the cartridge (shell Y ~ 2.0..7.0).
3. The finger plate is lowered from above, with the downward tabs descending into the bottom shell front zone. The tabs align with the arm pins: left tab at shell X = 2.5..8.5, right tab at shell X = 123.5..129.5. The pins at shell X = 5.5 (left) and 126.5 (right) center within the tabs.
4. The finger plate is pushed down until the tab bottom faces contact the arm pin tops (shell Z = 25.25). The 3.0 mm pins press into the 3.1 mm sockets. A small dab of CA glue on each pin before insertion creates a permanent bond.
5. The visible plate body now sits at the parting line level (shell Z = 33.5 at the bottom of the visible body), extending upward to shell Z = 58.0.
6. The top shell is then closed (concept step 10). The finger plate's visible body protrudes through the top shell's finger plate slot. The slot side walls (5.2 mm columns) constrain the plate laterally.

**Physical feasibility:**
- Step 3: The tabs must clear the bottom shell side walls (0.5 mm clearance). The tabs at shell Z = 25.25..33.5 are above the inner rib tops (Z = 20.25) so the ribs do not interfere. The tabs are 6.0 mm wide; the space between the side wall interior (X = 2.0) and the center divider is much wider than needed. Adequate for a straight vertical drop.
- Step 4: The press-fit requires pushing the finger plate down with moderate force (~5-10 N, typical for a 3.0/3.1 mm FDM press-fit). The user can push on the top of the visible plate body. Access is open from above (top shell not yet installed).
- Step 6: The visible plate body must enter the top shell slot from below as the top shell is closed. The slot is 121 mm wide; the plate is 120 mm. The 0.5 mm per side clearance allows the plate to enter the slot during shell closure without interference.

**Disassembly:** To remove the finger plate (for development or repair), the top shell is removed first (reverse of step 10). The finger plate can then be pulled upward out of the tab sockets. If CA glue was used, moderate prying force is needed. The tabs may be damaged during removal of a glued joint -- this is acceptable because the finger plate is a replaceable part and the joint is intended to be permanent in production.

---

## Part Count Minimization

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|---------------|----------------|---------|
| Finger plate + left linkage arm | No (press-fit + CA glue, but designed as separate parts) | Yes (arm slides in channel while plate slides in slot; the pin joint is permanent but the arm and plate have different constraint paths) | Yes (PETG) | Keep separate: different constraint paths (arm constrained by mid-height channels, plate constrained by top shell slot). Different print orientations (plate prints face-down, arm prints flat on 6mm face). Combining would create a U-shaped part that cannot be printed without support or compromised orientation. |
| Finger plate + right linkage arm | Same as above | Same | Same | Keep separate (same reasoning) |
| Visible plate body + left tab + right tab | These are one part | N/A -- monolithic | Yes | Already one part. The tabs are integral with the plate body. No split needed. |

The finger plate is correctly one printed part (body + two tabs). It cannot be further combined with any other part without compromising print orientation or assembly.

---

## FDM Printability

### Print Orientation

The finger plate prints flat on the build plate with the front face (Y = 0) down.

**Why this orientation:**
1. The user-facing front surface is the build-plate face -- smoothest possible FDM surface. This is the primary UX requirement: the surface the user's fingers touch must be the highest quality surface the printer can produce.
2. The pin sockets (Z-axis blind bores) are vertical holes in this orientation -- optimal circularity and diameter accuracy for the 3.1 mm press-fit bores.
3. The visible plate body is the first 4 mm of the print, giving it the best dimensional accuracy (closest to the build plate). The tabs extend upward for another 8.25 mm.
4. No overhangs, no supports needed (see audit below).

**Build plate footprint:** 127.0 mm (X, from tab X = -3.5 to 123.5) x 32.75 mm (in the print Y direction, from tab Z = -8.25 to visible body Z = 24.5 in plate local). Print height: 5.0 mm (maximum Y extent at tabs). Well within the 325 x 320 mm build plate.

### Overhang Audit

In print orientation (front face Y = 0 on build plate, print Z = Y in plate local):

| Surface / Feature | Angle from horizontal | Printable? | Resolution |
|-------------------|----------------------|------------|------------|
| Front face (Y = 0, build plate face) | 0 degrees (horizontal, on bed) | OK | Build plate contact |
| Rear face of visible body (Y = 4.0) | 0 degrees (horizontal, top face of thin section) | OK | Flat top of 4mm extrusion |
| Rear face of tabs (Y = 5.0) | 0 degrees (horizontal, top face of tab section) | OK | Flat top of 5mm extrusion |
| Left face of visible body (X = 0) | 90 degrees (vertical) | OK | |
| Right face of visible body (X = 120.0) | 90 degrees (vertical) | OK | |
| Top face (Z = 24.5) | 90 degrees (vertical in print) | OK | Vertical wall in print orientation |
| Bottom face of visible body (Z = 0) | 90 degrees (vertical in print) | OK | Vertical wall in print orientation |
| Left tab left face (X = -3.5) | 90 degrees (vertical) | OK | |
| Left tab right face (X = 2.5) | 90 degrees (vertical) | OK | |
| Right tab left face (X = 117.5) | 90 degrees (vertical) | OK | |
| Right tab right face (X = 123.5) | 90 degrees (vertical) | OK | |
| Tab bottom faces (Z = -8.25) | 90 degrees (vertical in print) | OK | Vertical wall edge in print |
| Tab-to-body junction (Z = 0, transition from body Y=4 to tab Y=5) | Step at Z = 0: 1mm step in Y, tab extends 1mm rearward from body rear face | See below | |
| Pin socket bores (3.1mm dia, Z-axis) | Vertical holes (along print Z through tab) | OK | Printed as vertical bores, excellent circularity |

**Tab-to-body junction detail:** At Z = 0 (the bottom of the visible plate body), the body rear face is at Y = 4.0. Below Z = 0, the tabs are 5.0 mm thick (Y = 0 to 5.0). This creates a 1.0 mm step at Z = 0 where the tab rear face is 1.0 mm behind the body rear face. In print orientation, this step is a vertical wall feature (Z maps to a horizontal print axis). The step is on the interior (rear) side at the junction. This is a simple vertical wall transition -- no overhang. The slicer handles this as a perimeter width change at one layer height. No support needed.

**No overhangs requiring support.** All surfaces are either on the build plate, vertical, or horizontal (flat top faces at known Y heights). The part is purely prismatic when viewed from the print direction.

### Wall Thickness Check

| Wall / Feature | Thickness | Minimum | Status |
|----------------|-----------|---------|--------|
| Visible plate body (full extent) | 4.0 mm (Y direction) | 1.2 mm structural | OK (3.3x minimum) |
| Tab Y thickness | 5.0 mm | 1.2 mm structural | OK |
| Tab X width | 6.0 mm | 1.2 mm structural | OK |
| Wall around pin socket (X direction) | 1.45 mm per side | 1.2 mm structural | OK |
| Wall around pin socket (Y direction) | 0.95 mm per side | 0.8 mm non-structural | OK (marginal but adequate; primary load is axial along Z, not radial through Y walls) |

### Bridge Span Check

| Feature | Span | Maximum | Status |
|---------|------|---------|--------|
| Pin socket ceiling (blind end of 3.1mm bore) | 3.1 mm | 15 mm | OK |

No horizontal unsupported spans exceed 15 mm. The part is mostly solid with only the two small pin socket bores as internal voids.

### Layer Strength Check

In the print orientation (front face down, print Z = plate Y):

| Feature | Load direction | Layer orientation | Status |
|---------|---------------|------------------|--------|
| Visible plate body (bending under squeeze) | Bending about X axis; tension on front face, compression on rear face | Layers stack along Y (print Z). Bending tension/compression is in the XZ plane, which is the layer plane. Layers carry the bending load in-plane. | OK -- optimal |
| Downward tabs (tension/compression along Z) | Axial load along plate Z (vertical) | Plate Z maps to print X/Y (horizontal). The tab's length (plate Z) is perpendicular to the layer stacking direction (plate Y = print Z). Axial loads along the tab length are carried by layer-to-layer adhesion. | OK -- tabs are only 8.25mm long; cross-section of 30mm^2 at 2.0 MPa stress is far below interlayer strength (~25 MPa) |

**Tab layer strength assessment:** The tabs are 8.25 mm long in plate Z, and the primary load (squeeze tension, ~30 N per tab) acts along plate Z. In print orientation, plate Z maps to a horizontal axis (print X or Y depending on rotation). The layers stack along print Z (= plate Y). The tensile load on the tabs acts perpendicular to the layer lines.

PETG interlayer adhesion tensile strength is approximately 25-35 MPa (roughly 50-70% of in-plane tensile strength of ~50 MPa). At 30 N load on a 6.0 x 5.0 = 30.0 mm^2 cross-section, the tensile stress is 1.0 MPa -- far below even the interlayer strength. The safety margin is 25x or more. The tab geometry is adequate despite the unfavorable layer orientation. The shorter tabs (8.25mm vs the previous 23.5mm) are even less likely to fail because the shorter cantilever reduces any bending moment contribution.

---

## Feature Traceability

| Feature | Justification source | Specific reference |
|---------|---------------------|--------------------|
| Visible plate body | Vision | "both surfaces can be perfectly flat and that will still provide the satisfying user experience we seek" -- vision Section 3. The finger plate is the surface the user's fingers pull. Its 120mm width and 24.5mm height provide finger purchase across 3-4 fingers. |
| Left downward tab | Physical necessity: Structural | The visible plate body must transmit force to the linkage arm. The tab is the only structural path from the plate body (at the parting line, Z = 33.5) to the arm pin (at Z = 25.25). Without it, the finger plate would be disconnected from the mechanism. |
| Right downward tab | Physical necessity: Structural | Mirror of left tab. Same justification. |
| Left pin socket | Physical necessity: Assembly | The socket accepts the linkage arm's front pin, forming the permanent joint between the finger plate and the arm. Without the socket, the parts cannot be joined. |
| Right pin socket | Physical necessity: Assembly | Mirror of left socket. Same justification. |
| Crosshatch grip texture | Vision | "both surfaces can be perfectly flat and that will still provide the satisfying user experience we seek" -- vision Section 3. The texture prevents finger slip under 40-60N squeeze load, directly supporting the one-handed squeeze UX. Matches the palm surface texture for visual consistency. |
| Elephant's foot chamfer | Physical necessity: Manufacturing | FDM first-layer flare (elephant's foot) would increase the visible plate body perimeter dimensions, reducing clearance in the top shell slot and potentially binding the sliding fit. The chamfer compensates per requirements.md Section 6. |

No unjustified features.

---

## Design Gaps

1. **DESIGN GAP (MINOR): Crosshatch texture implementation.** The crosshatch texture (0.2 mm deep, 0.4 mm wide grooves, 1.0 mm pitch) is specified as a slicer/build-plate treatment, not as geometry in the STEP model. The exact texture depth and pattern depend on slicer settings and build plate surface. This should be verified empirically with a test print. If the slicer bottom pattern does not produce adequate grip texture, the grooves could be modeled as 0.2 mm deep cuts in the STEP file, but this adds significant geometric complexity for a cosmetic feature.

2. **DESIGN GAP (MINOR): Tab-to-body junction reinforcement.** The junction where the tabs meet the visible plate body (at Z = 0) is a stress concentration point under cyclic squeeze loading. The current design has a right-angle junction. A 1.0 mm fillet at this junction (on the rear face, inside the cartridge where it is not visible) would reduce the stress concentration. This fillet does not affect any interface clearance (the rear face is inside the cartridge with ample clearance). **Resolution: Add a 1.0 mm fillet at the tab-to-body junction on the rear face (Y = 4.0..5.0 transition at Z = 0), both left and right tabs.**

---

## Dimension Summary

| Dimension | Value | Notes |
|-----------|-------|-------|
| Visible body: 120.0 x 4.0 x 24.5 mm (X x Y x Z) | | Main user-facing plate |
| Left tab: 6.0 x 5.0 x 8.25 mm (X x Y x Z) | X: -3.5 to 2.5, Z: -8.25 to 0 | Structural bridge to left arm |
| Right tab: 6.0 x 5.0 x 8.25 mm (X x Y x Z) | X: 117.5 to 123.5, Z: -8.25 to 0 | Structural bridge to right arm |
| Left pin socket: 3.1 mm dia x 5.0 mm deep at (-0.5, 2.5, -8.25) | Z-axis, blind, opens on tab bottom | |
| Right pin socket: 3.1 mm dia x 5.0 mm deep at (120.5, 2.5, -8.25) | Z-axis, blind, opens on tab bottom | |
| Elephant's foot chamfer: 0.3 mm x 45 deg | Visible body front face perimeter | |
| Tab-to-body fillet: 1.0 mm radius | Rear face junction at Z = 0 | Stress relief |
| Material: PETG | Matte black | |
| Overall bounding box: 127.0 x 5.0 x 32.75 mm | X: -3.5..123.5, Y: 0..5.0, Z: -8.25..24.5 | |
| Mass (estimated): ~15-18 g | PETG density 1.27 g/cm^3 | |
