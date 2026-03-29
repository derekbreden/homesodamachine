# Floor Plate -- Parts Specification

A flat rectangular PETG panel (148 x 60 x 4 mm) that attaches to the underside of the tray floor with two M3 screws. It closes a rectangular cutout in the pump zone, providing an optional access path for installing or replacing pumps from below. This is the simplest part in the cartridge: a flat box with two counterbore through-holes and perimeter chamfers.

---

## Reference Frame

All coordinates are in the floor plate's local frame unless labeled "(tray frame)."

- Origin: rear-left corner of the plate, top face
- X: width, 0..148 mm (left to right, parallel to tray X axis)
- Y: depth, 0..60 mm (rear to front, parallel to tray Y axis)
- Z: thickness, 0 at top face, -4 at bottom face (negative downward)
- Print orientation: flat, bottom face (Z = -4) on build plate, top face (Z = 0) facing up
- Installed orientation: top face contacts tray floor rib undersides at tray Z = 0

**Plate-to-tray transform:** Part-local (px, py, pz) maps to tray frame (px + 6.00, py + 29.00, pz). No rotation.

Material: PETG (per conceptual architecture).

---

## 1. Mechanism Narrative

### What the user sees and touches

Nothing. The floor plate is on the underside of the cartridge, hidden inside the dock. The cartridge rides on T-rails with the floor plate facing downward into the dock cavity. The user never sees or touches this part during normal operation.

During pump replacement (Tier 3 service, once per 1-2 years), the builder removes the cartridge from the dock, flips it over, and accesses the floor plate from below. The two M3 screw heads (5.50 mm diameter, recessed 3.20 mm into counterbores) are the only visible features on the bottom face. The rest of the surface is a plain flat rectangle.

### What moves

**Nothing moves during normal operation.** The floor plate is a static panel clamped to the tray floor.

During service, the floor plate is removed by unscrewing two M3 SHCS from the bottom face, then lifting the plate away from the tray. This exposes the rectangular cutout (140 x 52 mm) in the tray floor, through which pump heads can be passed.

### What converts the motion

Not applicable. No mechanism. Two M3 screws provide the only retention.

### What constrains the floor plate

- **X and Y position:** The plate is 4 mm wider and 4 mm deeper than the cutout on each edge. When pressed against the tray floor from below, the plate's perimeter overlap lips (4.00 mm wide strips on all four edges) bear against the underside of the tray floor ribs bordering the cutout. The cutout edges provide coarse lateral centering. The two M3 screws passing through the plate into heat-set inserts in the tray floor provide precise alignment via the 3.40 mm clearance holes engaging the insert bores.
- **Z position:** The M3 screw clamping force pulls the plate's top face flush against the tray floor rib undersides at tray Z = 0. The counterbore depth (3.20 mm) recesses the screw heads below the plate's bottom face, so the plate sits flat on any surface during service.
- **Rotation about Z:** The two screws at X = 21.50 and X = 126.50 (105.00 mm apart) prevent rotation. The clearance holes (3.40 mm) on 3.00 mm screws allow only 0.20 mm of lateral play per hole, which over the 105.00 mm span limits angular rotation to arctan(0.40 / 105.00) = 0.22 degrees.

### What provides the return force

Not applicable. No rest position, no spring, no detent. The plate is either fastened (in use) or removed (during service).

### What is the builder's physical interaction

**Installation:** The builder holds the floor plate against the underside of the tray, aligning the two counterbore holes with the heat-set insert bores in the tray floor. Two M3 x 8 mm SHCS are inserted from below, passing through the counterbore and clearance hole in the plate and threading into the M3 x 5.7 mm brass heat-set inserts in the tray's boss pads. Tightened with a 2.5 mm hex key.

**Removal:** The builder unscrews the two M3 SHCS with a 2.5 mm hex key and lifts the plate away. The screws remain captured in the counterbores (head diameter 5.50 mm in 5.70 mm counterbore) unless deliberately removed.

---

## 2. Constraint Chain Diagram

```
[Tray floor ribs, Z=0 underside] -> [Floor plate top face, Z=0: direct bearing] -> [Plate body]
  ^ resists: +Z (plate cannot push upward through the tray floor)

[M3 SHCS x 2] -> [Heat-set inserts in tray boss pads] -> [Tray floor structure]
  ^ clamp force pulls plate against tray ribs
  ^ resists: -Z (plate cannot fall away from tray)
  ^ resists: +X/-X, +Y/-Y (lateral restraint via screw shaft in clearance hole + friction under clamp)

[Cutout edges (tray floor)] -> [Plate overlap lips, 4 mm perimeter strips] -> [Coarse X/Y centering]
  ^ backup lateral restraint if screws are loose
```

Every arrow names a force path. Every part lists its constraints. No unlabeled arrows.

---

## 3. Feature Specifications

### 3a. Plate Body

A solid rectangular box.

| Parameter | Value | Source |
|-----------|-------|--------|
| X extent | 0 to 148.00 mm | Spatial: cutout width 140 + 2 x 4 mm overlap |
| Y extent | 0 to 60.00 mm | Spatial: cutout depth 52 + 2 x 4 mm overlap |
| Z extent | 0 to -4.00 mm | Concept architecture: 4 mm thickness |
| Volume | 148.00 x 60.00 x 4.00 = 35,520 mm^3 (~35.5 cm^3) | Derived |
| Estimated mass | ~45 g | PETG at 1.27 g/cm^3, solid (no infill pattern -- 4 mm thick plate is fully solid at typical slicer settings) |

### 3b. Bearing Surfaces (Top Face Perimeter Strips)

The floor plate's top face (Z = 0) contacts the tray floor rib undersides only along the 4 mm perimeter overlap strips that extend beyond the cutout edges. The central area of the top face spans the cutout void and does not contact the tray.

| Strip | Part X range | Part Y range | Width | Tray location |
|-------|-------------|-------------|-------|---------------|
| Left | 0..4 | 0..60 | 4.0 mm | Tray X = 6..10, against left floor rib |
| Right | 144..148 | 0..60 | 4.0 mm | Tray X = 150..154, against right floor rib |
| Rear | 4..144 | 0..4 | 4.0 mm | Tray Y = 29..33, against rear floor rib |
| Front | 4..144 | 56..60 | 4.0 mm | Tray Y = 85..89, against front floor rib |

Total bearing contact perimeter: 2 x (148 + 60) = 416 mm of 4 mm wide strips, minus 4 corner overlaps (4 x 4 x 4 = 64 mm^2). Net bearing area approximately 1,600 mm^2.

These strips are not raised features -- they are simply the portions of the flat top face that happen to contact the tray ribs. The top face is one continuous flat plane.

### 3c. M3 Counterbore Through-Holes (2x)

Two identical holes for M3 SHCS fasteners, counterbored from the bottom face.

**Hole positions (part-local frame):**

| Hole | Part X (mm) | Part Y (mm) | Tray X (mm) | Tray Y (mm) |
|------|-------------|-------------|-------------|-------------|
| Hole 1 (left) | 21.50 | 30.00 | 27.50 | 59.00 |
| Hole 2 (right) | 126.50 | 30.00 | 132.50 | 59.00 |

Hole-to-hole spacing: 105.00 mm (X direction). Both holes are on the Y centerline of the plate (Y = 30.00 = 60.00 / 2).

**Hole geometry:**

| Feature | Dimension | Notes |
|---------|-----------|-------|
| Through-hole diameter | 3.40 mm | M3 nominal (3.00 mm) + 0.2 mm per side clearance per requirements.md hole compensation. +0.2 mm total to the diameter. |
| Counterbore diameter | 5.70 mm | M3 SHCS head (5.50 mm) + 0.20 mm clearance |
| Counterbore depth | 3.20 mm | M3 SHCS head height (3.00 mm) + 0.20 mm clearance. Measured from bottom face (Z = -4.00) upward to Z = -0.80 |
| Remaining plate thickness above counterbore | 0.80 mm | 4.00 - 3.20 = 0.80 mm. This is a thin bearing ring (annulus: 3.40 mm ID, 5.70 mm OD) around the through-hole at Z = -0.80 to Z = 0. It bears the screw head clamping force against the tray rib. |

The counterbore is on the bottom face (Z = -4.00 side, the face visible from below when the cartridge is flipped). The screw enters from below, passes through the counterbore, through the clearance hole, and threads into the heat-set insert in the tray floor boss pad.

**Screw head recess check:** The counterbore depth (3.20 mm) exceeds the SHCS head height (3.00 mm) by 0.20 mm. The screw head sits 0.20 mm below the bottom face of the plate when fully tightened. The plate bottom face remains flat for resting on surfaces during service.

### 3d. Bottom-Edge Chamfers

0.30 mm x 45-degree chamfers on all four bottom edges of the plate (at the Z = -4.00 face perimeter). These mitigate elephant's foot from bed adhesion on the mating surface, per requirements.md Section 6 (Dimensional accuracy). The top face (Z = 0, the bearing surface) does not receive chamfers -- it must remain flat for flush contact with the tray floor ribs.

**Chamfer edges:**

| Edge | Start corner | End corner | Length |
|------|-------------|-----------|--------|
| Bottom-left | (0, 0, -4) | (0, 60, -4) | 60 mm |
| Bottom-right | (148, 0, -4) | (148, 60, -4) | 60 mm |
| Bottom-rear | (0, 0, -4) | (148, 0, -4) | 148 mm |
| Bottom-front | (0, 60, -4) | (148, 60, -4) | 148 mm |

Note: chamfers also ring the counterbore pocket perimeters is not necessary -- the counterbore pockets are cut features, not build-plate contact surfaces.

---

## 4. Interface Specifications

### 4a. Floor Plate Top Face to Tray Floor Ribs

| Parameter | Floor Plate (this part) | Tray (Sub-A + modifications) |
|-----------|------------------------|------------------------------|
| Contact surface | Part Z = 0 (top face), 4 mm perimeter strips | Tray Z = 0 (floor exterior), rib undersides bordering the cutout |
| Contact area | ~1,600 mm^2 (perimeter strips) | Same area on tray side |
| Alignment | Plate drops into position from below; cutout edges center it in X and Y with ~0 mm nominal gap (plate overlap extends 4 mm beyond cutout on each side) | Cutout rectangle acts as a loose location feature |

### 4b. M3 Screw Holes to Tray Floor Heat-Set Inserts

| Parameter | Floor Plate (this part) | Tray (Sub-A, with boss pads) |
|-----------|------------------------|------------------------------|
| Hole 1 center | Part (21.50, 30.00) = Tray (27.50, 59.00, 0) | Insert at tray (27.50, 59.00), bored from Z = 0 upward through 3 mm floor into boss pad |
| Hole 2 center | Part (126.50, 30.00) = Tray (132.50, 59.00, 0) | Insert at tray (132.50, 59.00), bored from Z = 0 upward through 3 mm floor into boss pad |
| Hole-to-hole spacing | 105.00 mm (X direction) | Must match: 105.00 mm |
| Through-hole dia | 3.40 mm | Pilot hole dia: 4.00 mm (for M3 x 5.7 mm heat-set insert) |
| Counterbore dia | 5.70 mm | N/A (insert side has no counterbore) |
| Fastener | M3 x 8 mm SHCS from below | M3 x 5.7 mm brass heat-set insert in boss pad |
| Thread engagement | 8.00 mm screw - 4.00 mm plate thickness = 4.00 mm into insert. Insert depth is 5.70 mm. Engagement: 4.00 mm (70% of insert depth). Adequate. | Insert seated in boss pad, pilot hole depth 7.00 mm from tray Z = 0 exterior |

### 4c. Floor Plate Edges to Tray Cutout Edges (Centering)

The plate is 148 mm wide, the cutout is 140 mm wide. The plate overhangs the cutout by 4 mm on each side in X. Similarly, the plate is 60 mm deep, the cutout is 52 mm deep, overhanging by 4 mm on each side in Y. The overlap lips bear against the tray floor rib undersides. No snap features, no tongue-and-groove -- purely a flat-on-flat bearing joint held by the two screws.

---

## 5. Assembly Sequence

1. **Install heat-set inserts in tray (prerequisite, not floor plate scope):** Two M3 x 5.7 mm brass heat-set inserts are pressed into the boss pads on the tray interior floor at positions (27.50, 59.00) and (132.50, 59.00) in tray frame. Done once during cartridge build, before pumps are installed.

2. **Install pumps from above (standard path):** Pumps are lowered into the tray from above, through the open top, and fastened to the pump bosses (Sub-C). This is the expected primary assembly path. If this path works, the floor plate cutout is left closed and the floor plate is never removed.

3. **Alternative: install pumps from below.** If pumps cannot be installed from above (interference with tube routing, boss access, etc.), the floor plate is removed by unscrewing the two M3 SHCS from the bottom face. Pump heads are then passed upward through the 140 x 52 mm cutout. After pump installation, the floor plate is re-attached.

4. **Attach floor plate:** Hold the plate against the tray underside with the overlap lips registering against the floor ribs. Insert two M3 x 8 mm SHCS into the counterbore holes from below. Thread into the heat-set inserts. Tighten with a 2.5 mm hex key. Screw heads recess 0.20 mm below the plate bottom face.

**Can each step physically be performed?**
- Step 4: Yes. The plate is accessed from below. The two screw holes are 105 mm apart with clear access from below. A 2.5 mm hex key reaches the screw heads through the 5.70 mm counterbore without obstruction.
- The plate (148 x 60 mm) is smaller than the tray footprint (160 x 155 mm) and does not interfere with any features outside the cutout zone.

**Disassembly:**
1. Remove cartridge from dock.
2. Flip cartridge (floor plate facing up).
3. Unscrew two M3 SHCS from the bottom face with 2.5 mm hex key.
4. Lift floor plate away.
5. Access pump heads through the 140 x 52 mm cutout.

No parts become trapped. No order dependencies beyond "remove screws before lifting plate." The floor plate is the outermost part on the bottom face and is always accessible.

---

## 6. Print Orientation and Manufacturing Notes

### Print Orientation

**Orientation: bottom face (Z = -4) on build plate, top face (Z = 0) facing up.**

Rationale: The top face (Z = 0) is the bearing surface that contacts the tray floor ribs. Printing with this face up means it is the last layer printed, giving a smooth, dimensionally accurate surface. The bottom face (on the build plate) gets the best flatness from PEI sheet contact, but it is the non-mating cosmetic surface (only screw heads are visible there). The counterbore pockets are on the bottom face (build plate side), which means they are cut into the first few layers -- this is ideal because the counterbore is simply an absence of material at the bottom of the print, not an overhang.

**Wait -- correction.** The counterbore is on the bottom face. If the bottom face is on the build plate, the counterbore pockets are on the build plate side. This means the printer must print the 0.80 mm thin ring above the counterbore as a bridge spanning the 5.70 mm counterbore diameter. A 5.70 mm bridge is well under the 15 mm maximum from requirements.md.

**Alternative orientation: top face (Z = 0) on build plate.** This would put the bearing surface directly on the PEI sheet (best flatness) and the counterbores would be cut from the top (open to air, no bridging). However, the elephant's foot would affect the bearing surface, requiring chamfers on the mating face edges, which is undesirable for a flush-bearing joint.

**Final decision: bottom face on build plate.** The 5.70 mm bridge over each counterbore is trivial. The top bearing surface prints last and is dimensionally clean. Elephant's foot chamfers on the bottom edges (Section 3d) protect the non-mating bottom face only.

### Overhang Audit

| Surface / Feature | Angle from horizontal | Printable? | Resolution |
|-------------------|-----------------------|------------|------------|
| Top face (Z = 0 plane) | 0 degrees (horizontal, facing up) | OK | Top surface, no overhang |
| Bottom face (Z = -4 plane) | 0 degrees (horizontal, on build plate) | OK | Build plate contact |
| Four vertical sides | 90 degrees from horizontal | OK | Vertical walls, no overhang |
| Counterbore pocket walls (5.70 mm dia, 3.20 mm deep) | 90 degrees (vertical cylinders) | OK | Vertical pocket walls |
| Counterbore pocket ceiling (transition from counterbore to through-hole at Z = -0.80) | 0 degrees (horizontal bridge) | OK | Bridge span: 5.70 mm counterbore dia minus 3.40 mm through-hole dia = 1.15 mm annular bridge per side. Total unsupported span across the annulus is 5.70 mm. Under 15 mm limit. Acceptable. |
| Through-hole walls (3.40 mm dia) | 90 degrees (vertical cylinder) | OK | Vertical bore |
| Bottom-edge chamfers | 45 degrees | OK | At the overhang limit, printable |

No overhangs below 45 degrees. No supports needed.

### Wall Thickness Check

| Feature | Thickness | Minimum required | Status |
|---------|-----------|------------------|--------|
| Plate body (full thickness) | 4.00 mm | 0.80 mm (non-structural) | OK |
| Thin ring above counterbore | 0.80 mm radially (annulus from 3.40 to 5.70 mm dia), 0.80 mm thick in Z | 0.80 mm (non-structural, bearing load only) | At minimum. Acceptable -- the ring bears compressive load only (screw clamping). No bending or tension. |
| Plate side edges (vertical walls, 4 mm tall) | 4.00 mm (X) or 4.00 mm (Y) full plate dimensions | 0.80 mm | OK |

No violations.

### Bridge Span Check

| Bridge | Span | Maximum | Status |
|--------|------|---------|--------|
| Counterbore ceiling (annular bridge at Z = -0.80) | 5.70 mm outer dia | 15 mm | OK |

No other bridges. The plate is a solid rectangular prism with cylindrical cuts.

### Layer Strength Check

No features flex, bear tension, or act as snap-fit arms. The floor plate is a rigid panel under compression (screw clamping) and bearing (pump weight transmitted through tray floor). Layer orientation is irrelevant for this pure-compression, pure-shear part. The chosen print orientation (flat) produces layers parallel to the bearing surface, which is optimal for compressive stiffness.

---

## 7. Design Gaps

### 7a. Tray Floor Has No Cutout or Floor Plate Mounting Points

**Status: DESIGN GAP.** The tray (Sub-A box shell spec) describes a solid, continuous floor from X = 0..160, Y = 0..155, Z = 0..3. No cutout, no boss pads, and no heat-set insert pockets for floor plate mounting exist in the current tray design.

**Required tray modifications if the floor plate option is used:**

1. **Rectangular cutout in tray floor:** Remove material at X = 10..150, Y = 33..85, full 3 mm depth (Z = 0 to Z = 3).

2. **Two circular boss pads on tray interior floor** (Z = 3 surface) at tray positions (27.50, 59.00) and (132.50, 59.00):
   - Pad diameter: 8.00 mm
   - Pad height: 4.00 mm (Z = 3 to Z = 7)
   - Pilot hole: 4.00 mm diameter, bored from Z = 0 (floor exterior) upward through 3 mm floor and into boss pad (total bore depth: 7.00 mm, accommodating the 5.70 mm insert with 1.30 mm clearance below)
   - Each pad receives one M3 x 5.7 mm brass heat-set insert

3. **Floor ribs must remain at least 4 mm wide** around the cutout perimeter. Current rib widths: left 5 mm, right 5 mm, rear 24.5 mm, front 70 mm -- all adequate.

This is an expected gap. The concept architecture identifies the floor plate as optional (Part #5, "decide during prototyping"). The tray was intentionally designed without floor plate features so they can be added as a tray variant if needed.

### 7b. Boss Pad Height vs Pump Head Clearance

The boss pads protrude 4 mm above the tray interior floor (Z = 3 to Z = 7). The pump heads rest on the floor at Z = 3.00. Both boss pads at tray (27.50, 59.00) and (132.50, 59.00) are within the pump head footprints (Pump 1: X = 11.90..74.50, Y = 35..83; Pump 2: X = 85.50..148.10, Y = 35..83).

**Impact:** Each pump head will rest on its respective boss pad instead of the floor, raising the pump 4 mm. Top clearance reduces from 6.4 mm to 2.4 mm. The pump head bottom is flat rigid stamped metal and will bridge across the 8 mm pad without distortion.

**Mitigation options (deferred to prototyping):**
- Accept the 2.4 mm top clearance (still positive, no interference)
- Move boss pads to Y < 35 in tray frame (behind pump heads, in rear floor zone) -- this avoids pump interference but places pads closer to the rear wall
- Recess pads flush with floor (but 3 mm floor is too thin for 5.7 mm insert)

### 7c. Thin Ring Above Counterbore

The 0.80 mm thick annular ring at Z = -0.80 to Z = 0 (between the counterbore ceiling and the top face) is at the minimum wall thickness per requirements.md (0.80 mm, 2 perimeters). This ring bears the full M3 screw clamping force in compression. For a purely compressive load on 2 perimeters of PETG, 0.80 mm is adequate. However, if the screw is overtightened and the ring yields, the screw head would punch through to the bearing surface. **Mitigation: do not exceed 0.5 Nm torque on the M3 screws. This is a standard hand-tight torque for M3 into heat-set inserts and presents no practical risk.**

---

## 8. Self-Review Rubric Results

### Rubric A -- Mechanism Narrative

Present and complete. The narrative describes: what the user sees (nothing during normal use; two screw heads during service), what moves (nothing during operation; plate removed during service), constraints (overlap lips + two M3 screws), return force (none -- static panel), and builder interaction (hold plate, insert screws, tighten). A reader unfamiliar with the design can understand the part from the narrative alone.

### Rubric B -- Constraint Chain Diagram

Present. Three force paths identified: bearing against tray ribs (+Z), M3 screw clamping (-Z, +/-X, +/-Y), and cutout edge centering (backup lateral). All arrows labeled with force transmission mechanism. All parts list constraints.

### Rubric C -- Direction Consistency Check

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| "Plate drops into position from below" | Plate moves upward toward tray floor | +Z in tray frame | Yes | Plate is held against tray underside; screws pull it tight in +Z |
| "Screw enters from below" | Screw driven upward into insert | +Z in tray frame | Yes | Counterbore on bottom face (Z = -4), screw threads into insert above |
| "Plate overlap lips bear against tray floor rib undersides" | Plate pushed against tray floor in +Z | +Z | Yes | Screw clamping pulls plate upward against rib undersides |
| "Screw heads recess below the plate bottom face" | Screw head below Z = -4 plane | -Z | Yes | Counterbore depth (3.20) > head height (3.00); head sits 0.20 mm below bottom face |
| "Lift floor plate away" (disassembly) | Plate moves downward away from tray | -Z | Yes | After screws removed, plate separates downward by gravity or hand |

No contradictions. All directions consistent with coordinate system.

### Rubric D -- Interface Dimensional Consistency

| Interface | Part A dimension | Part B dimension | Clearance | Source |
|-----------|-----------------|-----------------|-----------|--------|
| Through-hole to M3 screw shaft | 3.40 mm hole | 3.00 mm screw | 0.40 mm diametral (0.20 mm per side) | requirements.md: +0.2 mm to hole dia for clearance fit |
| Counterbore to M3 SHCS head | 5.70 mm pocket | 5.50 mm head | 0.20 mm diametral (0.10 mm per side) | Spatial doc |
| Counterbore depth to SHCS head height | 3.20 mm deep | 3.00 mm head | 0.20 mm recess | Spatial doc |
| Floor plate overlap to tray cutout | Plate 148 x 60 mm | Cutout 140 x 52 mm | 4.00 mm overlap per side | Spatial doc |
| Screw hole spacing (plate) to insert spacing (tray) | 105.00 mm | 105.00 mm | 0 (must match exactly) | Spatial doc |
| Plate top face Z to tray floor exterior Z | Z = 0 (plate) | Z = 0 (tray) | 0 (flush bearing contact) | Spatial doc |

No zero-clearance issues on moving/sliding interfaces. The screw-to-hole and head-to-counterbore clearances are specified and reasonable. The hole spacing is a matched dimension (both derived from the same tray boss pad positions).

### Rubric E -- Assembly Feasibility Check

1. **Can each step physically be performed?** Yes. The plate is accessed from below with no obstructions. The 2.5 mm hex key reaches the screw heads through 5.70 mm counterbores without interference. The plate (148 x 60 mm) fits against the tray underside with clearance to tray walls on all sides.
2. **Is the order correct?** Yes. Heat-set inserts (prerequisite) before plate attachment. Plate attachment is independent of pump installation order.
3. **Are there parts that become trapped?** No. The floor plate is the outermost part on the tray underside. Nothing is installed after it that would block access.
4. **Service sequence:** Remove 2 screws, lift plate. No other parts need to be removed to access the floor plate. The cartridge must be removed from the dock first (to access the underside), but no cartridge disassembly is needed.

### Rubric F -- Part Count Minimization

| Part pair | Permanently joined? | Move relative to each other? | Same material? | Combine? |
|-----------|--------------------|-----------------------------|----------------|----------|
| Floor plate + tray | No (screwed, removable) | Yes (plate is removed during service) | Yes (both PETG) | No -- they must separate for pump access. The floor plate exists specifically because it is removable. |
| Floor plate + M3 screws | No (threaded, removable) | Yes | No (PETG vs steel) | No -- different materials, different function |

Part count is at minimum: 1 printed part + 2 off-the-shelf fasteners. Cannot be reduced further.

### Rubric G -- FDM Printability

Covered in Section 6 above. Summary:
- Print orientation stated with rationale (bottom face on build plate)
- No overhangs below 45 degrees
- No supports needed
- All walls at or above 0.80 mm minimum (the thin ring at 0.80 mm is flagged in Design Gap 7c but is at-minimum, not below)
- No bridge spans over 15 mm (longest is 5.70 mm counterbore ceiling)
- No flex features -- layer strength orientation is not a concern

### Grounding Rule -- Reverse Check Against Product Values

| Product value (from vision.md) | Floor plate compliance | Status |
|-------------------------------|----------------------|--------|
| Consumer product, kitchen appliance | Floor plate is never visible to user. No cosmetic concern. | OK |
| UX paramount | No user interaction during normal use. Service interaction is two screws -- simple, obvious. | OK |
| Ease of 3D printing | Simple flat panel, no supports, prints in ~30 min. | OK |
| No exposed screws on user-facing surfaces | Screw heads are on underside, hidden inside dock. | OK |
| Languageless interaction | No labels or markings needed -- two obvious screw heads are the only features. | OK |
| Cartridge is the serviceable unit; user never opens enclosure | Floor plate is accessed by removing the cartridge. No enclosure opening required. | OK |
| Snap-fit assembly preferred | Floor plate uses screws (not snap-fit) because it is an infrequent-access service panel. Concept architecture explicitly accepts screws for this joint. | OK |
