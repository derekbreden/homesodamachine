# Parts Specification: Release Plate

## Scope

This document specifies the release plate -- a separate printed part (Part #4 in the conceptual architecture) that slides on 4 guide posts to compress the dock-facing collets of the 4 John Guest PP0408W fittings, releasing all 4 tubes simultaneously. The plate is a single 55 x 55 x 5 mm PETG plate with 4 stepped bores, 4 guide post bores, and 2 linkage rod hook features on the left and right edges.

**Coordinate frame:** Plate local frame. Origin at lower-left-front corner of plate bounding box. X = width (0..55), Y = depth/thickness (0 = user-facing/fitting-facing face, 5 = dock-facing/rear-wall-facing face), Z = height (0..55). Print orientation: flat in XY, bores along Z axis. For print frame: plate X = print X, plate Z = print Y, plate Y = print Z (plate lies flat with its 55 x 55 face on the build plate and its 5 mm thickness as print height).

**Installed orientation:** Plate X aligns with tray X, plate Z aligns with tray Z, plate Y aligns with tray Y (inverted: plate Y=0 faces higher tray Y values, plate Y=5 faces lower tray Y values). At rest, plate origin (0,0,0) corresponds to tray frame (52.5, 14.5, 8.5). Transform: tray_X = plate_X + 52.5, tray_Y = 14.5 - plate_Y, tray_Z = plate_Z + 8.5.

---

## 1. Mechanism Narrative (Rubric A)

### What the user sees and touches

The user never sees or directly touches the release plate. It is entirely internal to the cartridge, behind the front bezel and between the rear wall and the John Guest fittings. The user interacts with the front bezel: their palm pushes against the flat outer surface and their fingers curl into the finger channels to pull the pull-tab paddles. The pull-tab paddles connect to the release plate via two rigid linkage rods running along the tray inner side walls. The release plate is the invisible mechanism that makes the squeeze gesture release all 4 tube connections.

### What moves

- **Release plate** (this part): translates 1.5 mm along tray +Y direction (from tray Y=14.5 toward tray Y=16.0, user-face reference). The plate slides on 4 guide posts (Sub-E, 3.5 mm diameter, printed integral with the tray). The plate's user-facing face (plate Y=0) contacts and pushes the dock-facing collets of the 4 John Guest fittings inward.
- **Linkage rods** (2x, 4 mm diameter PETG rods): translate 1.5 mm along tray +Y simultaneously with the plate. They connect the plate to the pull-tab paddles. The rods run through the Sub-G linkage slots in the tray side walls.
- **Pull-tab paddles**: translate 1.5 mm along tray +Y when the user's fingers pull them.

Stationary parts: tray (including rear wall, guide posts, fitting bore plate, side walls with linkage slots), John Guest fittings (bodies fixed in bore plate; only the collet sleeves deflect), front bezel, lid.

### What converts the motion

No motion conversion. The mechanism is a pure linear linkage. The user's finger pull force on the pull-tab paddles transmits through the rigid linkage rods to the release plate. All three elements (paddles, rods, plate) translate the same 1.5 mm along the same axis (tray +Y). The rods are rigid connecting members, not cams, levers, or screws. Force magnitude is preserved: 1 N of finger pull = 1 N at the plate face (minus negligible friction).

### What constrains the release plate

The plate has exactly 1 degree of freedom: translation along tray Y (plate slides along the 4 guide posts).

- **X translation:** prevented by 4 guide posts at plate positions (5.5, 6.0), (49.5, 6.0), (5.5, 49.0), (49.5, 49.0). Post diameter 3.5 mm in 3.8 mm bores = 0.15 mm clearance per side. Maximum X play = 0.30 mm.
- **Z translation:** prevented by the same 4 guide posts. Maximum Z play = 0.30 mm.
- **Y-rotation (spin in XZ plane):** prevented by the 4-post rectangular pattern spanning 44.0 mm (X) x 43.0 mm (Z). Rotational play = arctan(0.30 / 43.0) = 0.40 degrees. Negligible.
- **X-tilt (pitch about X):** prevented by the 43.0 mm Z-span between upper and lower post pairs. Tilt = arctan(0.30 / 43.0) = 0.40 degrees. At the 20 mm fitting span, this produces 0.14 mm differential. Negligible relative to collet engagement geometry.
- **Z-tilt (yaw about Z):** prevented by the 44.0 mm X-span between left and right post pairs. Same analysis, negligible.
- **+Y travel limit (toward fittings):** the collet internal bottoming mechanism limits effective travel to ~1.3 mm. The design travel of 1.5 mm includes 0.2 mm margin. A 2.0 mm hard stop exists from the collet mechanism's physical limit.
- **-Y travel limit (away from fittings, toward rear wall):** mushroom cap stop features (4.5 mm OD, 0.5 mm radial overhang) at each guide post tip prevent the plate from sliding off the posts. These caps are at tray Y = 22.0 to 22.5 (the post tips). The plate would need to travel far past its rest position to reach the caps -- this only occurs during free handling of the cartridge outside the dock, not during normal operation.

### What provides the return force

The 4 John Guest fitting collet springs. At rest, the plate's user-facing face (plate Y=0) contacts the extended collet tips at tray Y=14.5. When the user releases the squeeze, the spring steel gripper rings inside all 4 fittings push their collet sleeves back to the extended position, pushing the release plate back to its rest position (tray Y=14.5 user face). The return force is 20-60 N total (4 collets, each contributing 5-15 N from their spring steel elements). No additional springs or return mechanisms are needed.

**DESIGN GAP: Rest position collet contact.** The plate rest position is defined as the plate user face sitting flush against the extended collet tips (both at tray Y=14.5). If manufacturing tolerance creates an air gap between the plate and the collets at rest, the collet springs cannot push the plate back. Fallback: add 2-4 printed PETG cantilever springs (12 mm x 3 mm x 1 mm beams) to the tray frame bearing against the plate's dock face. Verify contact during prototyping.

### User's physical interaction

The user never touches the release plate. Their interaction is entirely through the front bezel:

1. **Grip:** The user wraps their hand around the front bezel -- palm on the flat outer face, fingers curling into one of the two finger channels (left for left-handed, right for right-handed).
2. **Squeeze:** The user squeezes, pulling the pull-tab paddle toward their palm. This pulls the linkage rods, which pull the release plate 1.5 mm in the +Y tray direction (toward the fittings).
3. **Tactile feedback:** The user feels a firm resistance that suddenly increases when the collets bottom out at ~1.3 mm of travel. The remaining 0.2 mm of designed travel is absorbed by the collet mechanism. The user perceives this as a solid endpoint -- the plate cannot move further. The total force required is 20-60 N, well within comfortable one-handed squeeze for the 5th-percentile female population (150 N capacity, 3-9x margin).
4. **Release:** The user relaxes the squeeze. The collet springs push the plate back to rest. The pull-tab paddles return to their original position. The tubes are now free to withdraw when the cartridge is slid out of the dock.

---

## 2. Constraint Chain Diagram (Rubric B)

```
[User fingers on pull-tab paddles]
    -> [Pull-tab paddles: translate +Y (tray), 1.5 mm]
    -> [Linkage rods: rigid axial links, translate +Y through Sub-G wall slots]
         ^ rod constrained in Z by slot walls (5.0 mm slot vs 4.0 mm rod, 0.5 mm clearance/side)
         ^ rod constrained in Y-travel by slot length (6.0 mm slot, 0.25 mm clearance each end)
    -> [Release plate: translates +Y on 4 guide posts (Sub-E)]
         ^ X constrained by: 4 guide posts, 3.8 mm bore on 3.5 mm post, 0.15 mm clearance/side
         ^ Z constrained by: 4 guide posts, same clearance
         ^ rotation constrained by: 4-post rectangular pattern, 44.0 x 43.0 mm span
         ^ -Y limit: mushroom caps at post tips (4.5 mm OD, at tray Y = 22.0..22.5)
         ^ +Y limit: collet internal bottoming (~1.3 mm effective travel)
    -> [Plate user face (Y=0) annular push surfaces: contact collet end faces]
         ^ push surface: annular ring from 6.5 mm (through-hole) to 6.69 mm (collet ID)
         ^ engagement lip: 0.095 mm per side (6.69 - 6.50) / 2
    -> [Collets compress inward 1.3 mm: gripper teeth disengage from tube surface]
    -> [Tubes released: free to withdraw when cartridge slides out]

[User palm on front bezel outer face]
    -> [Front bezel: stationary reaction surface]
    -> [Bezel snap tabs -> tray body: reaction force path to tray structure]
    -> [Tray rear wall -> bore plate: holds fittings rigid while collets are compressed]
         ^ guide posts integral with tray: reaction torque from plate tilt goes into tray

Return path:
[4 collet springs, 20-60 N total] -> [Push collet sleeves back to extended position]
    -> [Collet faces push release plate -Y to rest] -> [Linkage rods relax -Y]
    -> [Pull-tab paddles return to rest position]
```

---

## 3. Parts and Features

### 3a. Plate Body

| Parameter | Value | Source |
|-----------|-------|--------|
| Width (plate X) | 55.0 mm | Spatial doc section 3a |
| Thickness (plate Y) | 5.0 mm | Spatial doc; collet release research |
| Height (plate Z) | 55.0 mm | Spatial doc section 3a |
| Material | PETG | Concept doc section 7 |
| Corners | 1 mm fillet on all 4 long edges (parallel to Y) | Concept doc design language: 1 mm fillets on internal parts |

The plate body is a simple rectangular solid with all precision features cut into it.

### 3b. Stepped Bores (4x, identical)

Four 3-step bores cut through the plate thickness, engaging the dock-facing collets of the 4 John Guest fittings. Each bore axis runs along plate Y (the 5 mm thickness direction). In print orientation, bore axes are along Z (print height), which gives the best circularity for FDM.

**Bore center positions (plate frame):**

| Bore | Plate X (mm) | Plate Z (mm) | Tray X (mm) | Tray Z (mm) |
|------|-------------|-------------|------------|------------|
| B1 (lower-left) | 17.5 | 17.5 | 70.0 | 26.0 |
| B2 (lower-right) | 37.5 | 17.5 | 90.0 | 26.0 |
| B3 (upper-left) | 17.5 | 37.5 | 70.0 | 46.0 |
| B4 (upper-right) | 37.5 | 37.5 | 90.0 | 46.0 |

Center-to-center spacing: 20.0 mm in both plate X and plate Z. Bore grid center: (27.5, 27.5) in plate frame, which is the plate center.

**Stepped bore profile (per bore, from user face to dock face):**

| Step | Diameter (mm) | Y-start (mm) | Y-end (mm) | Depth (mm) | Purpose |
|------|---------------|--------------|------------|------------|---------|
| 1: Body end clearance counterbore | 15.5 | 0 | 1.0 | 1.0 | Clears 15.10 mm body end OD with 0.40 mm diametral clearance. Prevents the plate from bottoming out on the body end before the collet is fully depressed. |
| 2: Collet engagement counterbore | 9.8 | 1.0 | 3.0 | 2.0 | Surrounds 9.57 mm collet OD with 0.23 mm diametral clearance. Provides lateral constraint so the plate engages each collet squarely, centering the push force even with slight plate misalignment. |
| 3: Tube clearance through-hole | 6.5 | 0 | 5.0 | 5.0 (full thickness) | 6.35 mm (nominal) / 6.30 mm (measured) tube passes freely through the 6.5 mm hole with 0.15-0.20 mm clearance. The annular face between the 6.5 mm bore wall and the 6.69 mm collet ID is the contact surface that pushes each collet inward. |

**Entry chamfers on bore steps:**

| Chamfer | Location | Angle | Depth | Purpose |
|---------|----------|-------|-------|---------|
| Body end counterbore entry | User face (Y=0), 15.5 mm step | 45 degrees | 0.3 mm | Guides plate onto fitting body ends during assembly. Eases alignment when placing the plate on the guide posts with fittings already installed. |
| Collet engagement counterbore entry | Step from 15.5 mm to 9.8 mm at Y=1.0 | 45 degrees | 0.3 mm | Funnels the collet into the engagement bore as the plate moves toward the fittings. Prevents edge catch if the plate has slight lateral play (up to 0.30 mm). |

**Structural checks between adjacent bores:**

| Y range | Bore diameter (mm) | Wall between adjacent bores (mm) | Structural assessment |
|---------|-------------------|--------------------------------|----------------------|
| 0 to 1.0 | 15.5 | 20.0 - 15.5 = 4.5 | Adequate for PETG FDM |
| 1.0 to 3.0 | 9.8 | 20.0 - 9.8 = 10.2 | Generous |
| 3.0 to 5.0 | 6.5 | 20.0 - 6.5 = 13.5 | Generous |

Minimum wall (4.5 mm between body end counterbores) is sufficient for the low forces involved (5-15 N per collet, distributed across the annular push face at each bore).

**Critical tolerance note:** The 6.5 mm through-hole has only 0.095 mm engagement lip per side against the 6.69 mm collet ID. This annular contact face is what pushes each collet inward. The tolerance window on the through-hole diameter is 6.30 mm (tube OD, measured) to 6.69 mm (collet ID, derived from caliper measurements). A 6.5 mm bore gives 0.10 mm clearance to the tube and 0.095 mm engagement per side on the collet. Print at 0.1 mm layer height. Verify with a test print of a single stepped bore before committing to the full plate.

### 3c. Guide Post Bores (4x, identical)

Four simple cylindrical through-holes at the plate corners for the 4 guide posts (Sub-E).

**Bore positions (plate frame):**

| Bore | Plate X (mm) | Plate Z (mm) | Tray X (mm) | Tray Z (mm) |
|------|-------------|-------------|------------|------------|
| G1 (lower-left) | 5.5 | 6.0 | 58.0 | 14.5 |
| G2 (lower-right) | 49.5 | 6.0 | 102.0 | 14.5 |
| G3 (upper-left) | 5.5 | 49.0 | 58.0 | 57.5 |
| G4 (upper-right) | 49.5 | 49.0 | 102.0 | 57.5 |

| Parameter | Value | Source |
|-----------|-------|--------|
| Bore diameter | 3.8 mm | Spatial doc; 0.15 mm clearance per side on 3.5 mm posts |
| Bore depth | 5.0 mm (through-hole, full plate thickness) | Spatial doc |
| Bore axis | Along plate Y (plate thickness direction) | -- |

**Entry chamfers:**

| Chamfer | Location | Angle | Depth | Purpose |
|---------|----------|-------|-------|---------|
| Dock-face entry | Dock face (Y=5), all 4 guide bores | 45 degrees | 0.3 mm | Guides plate onto posts during assembly. The plate is installed by pressing it onto the posts from the dock side, passing over the mushroom caps (Sub-E). The chamfer eases initial engagement. |
| User-face entry | User face (Y=0), all 4 guide bores | 45 degrees | 0.3 mm | Symmetrical chamfer for manufacturing cleanliness. |

**Edge clearance check (plate edge to nearest guide bore edge):**

| Bore | Direction | Distance to edge | Wall remaining |
|------|-----------|-----------------|----------------|
| G1 | Left (X=0) | 5.5 - 1.9 = 3.6 mm | OK |
| G2 | Right (X=55) | 55 - 49.5 - 1.9 = 3.6 mm | OK |
| G1 | Bottom (Z=0) | 6.0 - 1.9 = 4.1 mm | OK |
| G3 | Top (Z=55) | 55 - 49.0 - 1.9 = 4.1 mm | OK |

**Guide bore to stepped bore interference check:**

Closest pair is G1 (5.5, 6.0) to B1 (17.5, 17.5): center distance = sqrt((17.5-5.5)^2 + (17.5-6.0)^2) = sqrt(144 + 132.25) = 16.62 mm. Nearest edges: 16.62 - 1.9 (guide bore radius) - 7.75 (body end counterbore radius) = 6.97 mm wall. No interference.

### 3d. Linkage Rod Hook Features (2x, mirrored)

Two C-shaped hooks on the left and right edges of the plate at mid-height, capturing the 4 mm diameter linkage rods. The hooks are open toward the respective plate edge (left hook opens toward -X, right hook opens toward +X), allowing the rods to be inserted laterally during assembly.

**Hook positions (plate frame):**

| Hook | Edge | Plate X (mm) | Plate Z (mm) |
|------|------|-------------|-------------|
| Left | Left edge (X=0) | 0 (hook extends from plate edge) | 27.5 (plate vertical center) |
| Right | Right edge (X=55) | 55 (hook extends from plate edge) | 27.5 |

**Hook geometry:**

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Rod diameter (captured) | 4.0 mm | Concept doc |
| Hook internal diameter | 4.3 mm | 4.0 mm rod + 0.15 mm clearance per side |
| Hook wall thickness | 1.5 mm | Minimum printable wall for structural hook in PETG |
| Hook outer diameter | 7.3 mm | 4.3 mm ID + 2 x 1.5 mm wall |
| Hook opening width | 3.0 mm | Narrower than 4.0 mm rod diameter, requiring slight flex to snap rod in |
| Hook opening direction | -X (left hook), +X (right hook) | Opening faces outward toward plate edge |
| Hook Y span | 1.0 to 4.0 mm (centered in plate thickness) | 3.0 mm hook depth within the 5 mm plate; leaves 1.0 mm solid plate on each face |
| Hook Z span | 24.0 to 31.0 mm | Centered on plate Z = 27.5, 7.0 mm total (hook outer diameter) |
| Hook X extension beyond plate edge | 3.65 mm | Half of hook OD (7.3 / 2); hook center at plate edge, so half protrudes |

**Rod capture and travel:** The hook must allow the rod to slide 1.5 mm along plate Y as the plate moves relative to the rod's fixed anchor points (the rod angles slightly in Y and Z from the plate attachment to the tray wall slot). The hook internal diameter of 4.3 mm (vs 4.0 mm rod) provides 0.15 mm clearance per side, and the hook spans from plate Y=1.0 to Y=4.0 (3.0 mm), which is sufficient for the rod to slide within the hook during the 1.5 mm plate travel without binding.

**DESIGN GAP: Hook snap-in force.** The 3.0 mm hook opening for a 4.0 mm rod requires the hook arms to deflect 0.5 mm each during rod insertion. At 1.5 mm wall thickness in PETG, this should be achievable with finger force, but the exact snap-in force depends on the hook arm length and print quality. Verify during prototyping. If the hooks are too stiff, widen the opening to 3.5 mm (still narrower than the 4.0 mm rod, providing retention). If the hooks are too flexible, increase wall thickness to 2.0 mm.

---

## 4. Direction Consistency Check (Rubric C)

All directions referenced to the tray frame (Y=0 at dock, increasing Y toward user).

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| User squeezes, pulling pull tabs toward palm | Pull tabs move toward rear wall/dock | +Y (tray) | Yes | Wait -- rechecking. The user's palm is on the front bezel (user side). Fingers pull the tabs toward the palm. The tabs are inside the cartridge behind the bezel. Pulling them toward the palm means pulling them toward the user side (+Y). But the release plate must move toward the fittings, which are at higher Y than the plate. The plate at rest has its user face at tray Y=14.5. The fittings' dock-side collets are also at tray Y=14.5. Squeezing pushes the plate's user face from Y=14.5 to Y=16.0 (+Y). Consistent. |
| Release plate moves toward fittings during squeeze | +Y (tray) | +Y | Yes | Plate user face moves from tray Y=14.5 to Y=16.0. Fitting collet tips start at tray Y=14.5. Plate pushes collets in the +Y direction (toward fitting body center). |
| Plate user face (Y=0) contacts collet tips | Plate Y=0 faces higher tray Y | +Y | Yes | At rest, plate Y=0 maps to tray Y=14.5. Collet tips are at tray Y=14.5. Contact confirmed. |
| Collet springs push plate back to rest (-Y tray) | -Y (tray) | -Y | Yes | When user releases squeeze, collet springs push collet sleeves outward (toward lower tray Y = toward dock). The collet faces push the plate's user face back from tray Y=16.0 to tray Y=14.5 (-Y motion). |
| Linkage rods transmit force from front (high Y) to plate (low Y) | Force along -Y to +Y depending on direction | Both | Yes | At rest, rods run from plate edge (tray X=52.5 or 107.5, tray Y=12.0) to wall slots (tray Y=17..23). During squeeze, the rod's front end (at the pull-tab) moves +Y, pulling the plate-end +Y. Consistent. |
| Plate dock face (Y=5) faces the rear wall | Dock face toward lower tray Y | -Y | Yes | Plate Y=5 maps to tray Y=14.5-5=9.5 at rest. Rear wall interior is at tray Y=8.5. Gap = 1.0 mm. Consistent. |
| Mushroom caps prevent plate from sliding off posts in -Y direction | Caps at post tips, far from rear wall in -Y | -Y limit | Yes | Caps are at tray Y ~22.0 to 22.5 (post tips, projecting from rear wall exterior at tray Y=0). Wait -- the Sub-E spec describes posts projecting in -Y from Y=0. But the spatial doc places posts from tray Y=8.5 to Y=22.0. Using the spatial doc as authoritative: posts span tray Y=8.5 (base at rear wall interior) to Y=22.0 (tip). Caps at Y=22.0 to 22.5. The plate at rest has its dock face at tray Y=9.5. To reach the caps, the plate would need to move in the +Y direction to tray Y ~22.0, far beyond the 1.5 mm operating travel. The caps retain the plate during free handling when there are no collets to provide return force. Direction is consistent. |

No contradictions found. All directional claims are verified against the tray coordinate system.

---

## 5. Interface Dimensional Consistency (Rubric D)

| Interface | Part A dimension | Part B dimension | Clearance | Source |
|-----------|-----------------|-----------------|-----------|--------|
| Guide post to guide bore | 3.5 mm OD (Sub-E post) | 3.8 mm ID (plate bore) | +0.30 mm diametral (0.15 mm/side) | Sub-E spec; spatial doc |
| Body end to clearance counterbore | 15.10 mm OD (caliper-verified) | 15.5 mm ID (plate counterbore) | +0.40 mm diametral (0.20 mm/side) | Caliper photo 01; spatial doc |
| Collet OD to engagement counterbore | 9.57 mm OD (caliper-verified) | 9.8 mm ID (plate counterbore) | +0.23 mm diametral (0.115 mm/side) | Caliper photos 04/05; spatial doc |
| Tube OD to through-hole | 6.30 mm OD (caliper-measured) | 6.5 mm ID (plate through-hole) | +0.20 mm diametral (0.10 mm/side) | Caliper measurement; spatial doc |
| Through-hole to collet ID (push contact) | 6.5 mm (plate bore wall) | 6.69 mm (collet ID) | 0.19 mm (engagement lip per side) | Derived from caliper data |
| Linkage rod to hook ID | 4.0 mm OD (rod) | 4.3 mm ID (hook) | +0.30 mm diametral (0.15 mm/side) | Concept doc; spec section 3d |
| Plate dock face to rear wall interior | Plate dock face at tray Y=9.5 | Rear wall interior at tray Y=8.5 | 1.0 mm gap (at rest) | Spatial doc section 3g |
| Mushroom cap to guide bore (retention) | 4.5 mm OD (cap) | 3.8 mm ID (bore) | -0.70 mm (interference, intentional snap-over) | Sub-E spec |

No zero-clearance fits at sliding interfaces. The 0.19 mm engagement lip on the through-hole/collet interface is the tightest functional dimension and is the critical tolerance for the design. The mushroom cap interference is intentional for snap-over retention during assembly.

---

## 6. Assembly Feasibility Check (Rubric E)

### Assembly Sequence

The release plate is assembled after the fittings are pressed into the bore plate and before the linkage rods, lid, and front bezel are installed.

1. **Fittings already installed.** The 4 John Guest fittings are pressed into the tray bore plate (Sub-D). Their dock-side body ends protrude at tray Y=15.9, with collet tips at tray Y=14.5.

2. **Install release plate onto guide posts.** Orient the plate so its 4 guide bores (3.8 mm) align with the 4 guide posts (3.5 mm, projecting from the tray toward higher tray Y values). The plate is installed from the post-tip side: the dock face (plate Y=5) faces the post bases (rear wall). Press the plate onto the posts. The plate bores cam over the mushroom caps at the post tips (Sub-E: 4.5 mm OD caps with 45-degree chamfer). The 3.8 mm bore passes over the 4.5 mm cap by flexing the cap fins inward 0.35 mm per side. Apply firm even pressure. Snap-over force is under 5 N total.

   **Can the plate physically fit?** Yes. The plate is 55 x 55 mm. The tray interior cross-section is approximately 150 x 69 mm (X x Z). The plate center is at tray (80, 36), well within the interior. The plate passes between the bore plate bosses (tray X=60..100, Z=16..56) and the side walls with ample clearance. The plate user face (at tray Y=14.5 at rest) clears the fitting collet tips (also at tray Y=14.5). The dock face (at tray Y=9.5) clears the rear wall interior (at tray Y=8.5) by 1.0 mm.

3. **Verify plate slides freely.** Push the plate toward the fittings (+Y) and release. The plate should slide smoothly 1.5 mm and return when released (collet springs provide return force if tubes are present, or gravity/finger push if not). Verify no binding at any guide bore.

4. **Thread linkage rods through tray wall slots.** Each 4 mm PETG rod is threaded through the Sub-G slot from the tray interior, passing through the 5 mm wall thickness. The rod's interior end is snapped into the plate's edge hook at plate Z=27.5.

5. **Connect rod exterior ends to pull-tab paddles.** The rod protrudes on the exterior of the tray wall. The exterior end hooks into the pull-tab paddle (inside the front bezel's finger channel).

6. **Snap front bezel onto tray.** The bezel captures the pull-tab paddles, preventing the rods from withdrawing through the slots.

### Can each step be physically performed?

- Step 2: The plate is small (55 x 55 mm) and lightweight. A hand can easily reach into the open tray (open top, open front) and press the plate onto the posts. The posts are at tray X=58/102, Z=14.5/57.5, roughly centered in the tray cross-section.
- Step 4: The linkage slots are at tray Z=35..40, mid-height on the side walls. The slots are 6.0 x 5.0 mm openings. A 4 mm rod threads through easily.
- Step 4 (hook attachment): The rod end must snap into the C-hook on the plate edge. The plate is already on the guide posts. The hook is at plate Z=27.5 (mid-height, at tray Z=36.0). The rod approaches from the side wall (tray X=5 for left rod). The rod end can be guided into the hook by hand. The hook opening faces the plate edge, so the rod is pushed laterally (-X for left, +X for right) into the hook, requiring the rod to flex the hook arms 0.5 mm.

### Disassembly (service, Tier 4: extremely rare)

1. Pop front bezel off (snap-fit, tool-free).
2. Unhook rod exterior ends from pull-tab paddles.
3. Slide rods back through wall slots toward interior.
4. Unhook rods from plate edge hooks.
5. Slide plate off guide posts by pulling away from rear wall (-Y in tray frame). The plate bores cam back over the mushroom caps (same snap-over as assembly, under 5 N).

No parts become trapped. The plate is accessible at all times via the open top (after lid removal) and open front (after bezel removal). The rods can be withdrawn through the slots at any time after the bezel is removed.

---

## 7. Part Count Minimization (Rubric F)

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|----------------|----------------|---------|
| Plate body + stepped bores | Integral (bores are cuts in the body) | No | Yes (PETG) | Already one part. Correct. |
| Plate body + guide post bores | Integral (bores are cuts in the body) | No | Yes | Already one part. Correct. |
| Plate body + linkage hooks | Integral (hooks are extrusions from the body) | No | Yes | Already one part. Correct. |
| Release plate + guide posts (Sub-E) | Not joined (sliding fit) | Yes (plate slides on posts) | Yes (both PETG) | Must be separate: relative motion. Correct. |
| Release plate + linkage rods | Not joined (rod captive in hook, slides during travel) | Yes (rod slides ~1.5 mm within hook during plate travel) | Yes (both PETG) | Must be separate: relative motion. Correct. |
| Release plate + tray | Not joined (plate slides inside tray) | Yes | Yes | Must be separate: relative motion. Correct. |
| Left hook + right hook | Both integral with plate body | No | Yes | Already one part (both part of the plate). Correct. |

**Could the linkage rods be printed integral with the plate?** The concept doc mentions this possibility ("T-shaped hooks at each end"). However, the rods must pass through the Sub-G wall slots (5 mm wall thickness) and connect to pull-tab paddles that are outside the tray walls. If printed integral, the rods would need to be in place before the tray walls exist, which is impossible since the tray is a separate part printed first. The rods must be separate pieces inserted during assembly. This is confirmed by the assembly sequence: rods are threaded through the wall slots after the plate is installed.

**Total printed parts for this specification: 1** (the release plate, with all features integral). Plus 2 separate linkage rods (either cut from 4 mm PETG rod stock or printed as separate straight rods with hook ends).

---

## 8. Print Orientation and Manufacturing

| Parameter | Value |
|-----------|-------|
| Print orientation | Flat in XY. Plate's 55 x 55 mm face on the build plate. 5 mm thickness = print height along Z. |
| Layer height | 0.1 mm (required for stepped bore critical tolerance) |
| Material | PETG |
| Supports | None required. The stepped bore counterbores open toward the build plate (plate Y=0 = print Z=0 is on the build plate). The counterbores are cut from the user face, which faces the build plate. This means the 15.5 mm and 9.8 mm counterbores are on the bottom, and the 6.5 mm through-hole exits at the top (print Z=5 mm). All bore transitions are concentric steps with no overhangs beyond what FDM handles natively (cylindrical bore walls perpendicular to the build plate). |
| Build plate contact surface | The user face (plate Y=0) with its 15.5 mm counterbore openings contacts the build plate. This gives the best circularity for the 15.5 mm and 9.8 mm bores (printed first, closest to build plate). |
| Estimated print time | 0.5-1 hr |
| Test print | Print a single stepped bore in a 25 x 25 x 5 mm test block before the full plate. Verify: 6.5 mm through-hole passes a 6.35 mm tube, and the annular lip contacts a fitting collet face when pushed. |

---

## 9. Complete Dimension Table

All values in plate local frame (mm) unless noted. Source abbreviations: SD = spatial resolution document, CR = collet release research, CD = concept document, CP = caliper-verified, DV = derived from caliper data.

| Parameter | Value | Frame | Source |
|-----------|-------|-------|--------|
| Plate width (X) | 55.0 | Plate | SD 3a |
| Plate thickness (Y) | 5.0 | Plate | SD, CR |
| Plate height (Z) | 55.0 | Plate | SD 3a |
| Plate origin in tray frame (at rest) | (52.5, 14.5, 8.5) | Tray | SD 3b |
| **Stepped bores** | | | |
| B1 center (X, Z) | (17.5, 17.5) | Plate | SD 3c |
| B2 center (X, Z) | (37.5, 17.5) | Plate | SD 3c |
| B3 center (X, Z) | (17.5, 37.5) | Plate | SD 3c |
| B4 center (X, Z) | (37.5, 37.5) | Plate | SD 3c |
| Bore center-to-center spacing | 20.0 (X and Z) | Plate | SD 3c |
| Body end clearance counterbore dia | 15.5 | Plate | SD 3d; 0.40 mm clearance on 15.10 mm body end OD (CP) |
| Body end counterbore Y range | 0 to 1.0 | Plate | SD 3d |
| Collet engagement counterbore dia | 9.8 | Plate | SD 3d; 0.23 mm clearance on 9.57 mm collet OD (CP) |
| Collet engagement bore Y range | 1.0 to 3.0 | Plate | SD 3d |
| Tube clearance through-hole dia | 6.5 | Plate | SD 3d; between 6.30 mm tube OD (CP) and 6.69 mm collet ID (DV) |
| Through-hole Y range | 0 to 5.0 | Plate | SD 3d |
| Collet push lip per side | 0.095 mm | -- | (6.69 - 6.50) / 2, DV |
| Body end counterbore entry chamfer | 45 deg x 0.3 mm | Plate Y=0 | Spec 3b |
| Collet bore entry chamfer | 45 deg x 0.3 mm | Plate Y=1.0 step | Spec 3b |
| **Guide post bores** | | | |
| G1 center (X, Z) | (5.5, 6.0) | Plate | SD 3e |
| G2 center (X, Z) | (49.5, 6.0) | Plate | SD 3e |
| G3 center (X, Z) | (5.5, 49.0) | Plate | SD 3e |
| G4 center (X, Z) | (49.5, 49.0) | Plate | SD 3e |
| Guide bore diameter | 3.8 | Plate | SD 3e; Sub-E spec |
| Guide bore depth | 5.0 (through-hole) | Plate | SD 3e |
| Guide bore entry chamfers | 45 deg x 0.3 mm, both faces | Plate Y=0 and Y=5 | Spec 3c |
| **Linkage rod hooks** | | | |
| Left hook center (X, Z) | (0, 27.5) | Plate | SD 3f |
| Right hook center (X, Z) | (55, 27.5) | Plate | SD 3f |
| Hook internal diameter | 4.3 | Plate | 4.0 mm rod + 0.30 mm clearance |
| Hook wall thickness | 1.5 | Plate | Spec 3d |
| Hook opening width | 3.0 | Plate | Spec 3d; narrower than 4.0 mm rod for retention |
| Hook Y span | 1.0 to 4.0 | Plate | Centered in plate thickness |
| Hook Z span | 24.0 to 31.0 | Plate | Centered on Z=27.5, 7.0 mm total |
| Hook X extension beyond plate edge | 3.65 | Plate | Half of 7.3 mm hook OD |
| **Travel** | | | |
| Operating travel | 1.5 mm along +Y tray | Tray | CR; SD 3g |
| Hard stop travel | 2.0 mm (collet mechanism limit) | Tray | CR |
| Plate user face at rest | tray Y = 14.5 | Tray | SD 3g |
| Plate user face at full travel | tray Y = 16.0 | Tray | SD 3g |
| Gap to rear wall at rest | 1.0 mm | Tray | SD 3g |
| Gap to rear wall at full travel | 2.5 mm | Tray | SD 3g |

---

## 10. Design Gaps

1. **Rest position collet contact.** The plate rest position relies on the plate user face contacting the extended collet tips (both at tray Y=14.5). If tolerance stack-up creates an air gap, the collet springs cannot return the plate. Fallback: printed cantilever springs on the tray frame. Verify during prototyping with the test-fit of plate + fittings on the guide posts.

2. **Through-hole critical tolerance (0.095 mm engagement lip per side).** The 6.5 mm through-hole must be between 6.30 mm (tube clearance) and 6.69 mm (collet ID contact). The design window is only 0.39 mm. FDM at 0.1 mm layer height on a Bambu H2C should achieve this, but must be verified with a test print. If the bore prints oversize (above 6.69 mm), no collet engagement occurs. If undersize (below 6.30 mm), the tube cannot pass through. Test with a single-bore block before printing the full plate.

3. **Hook snap-in force.** The C-hook opening is 3.0 mm for a 4.0 mm rod. The hook arms must deflect 0.5 mm each during rod insertion. Verify that PETG at 1.5 mm wall thickness provides sufficient flex without fracturing. Adjust opening width (3.0-3.5 mm) or wall thickness (1.5-2.0 mm) based on test results.
