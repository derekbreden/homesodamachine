# Mounting Partition -- Parts Specification

The mounting partition is a vertical PETG plate that spans the full interior width and height of the pump cartridge at the junction between the pump head zone and the motor zone. It holds both Kamoer KPHM400 peristaltic pumps via M3 rubber vibration isolation mounts. Two motor bores allow the motor bodies to pass through. The partition drops into vertical slots in the bottom shell side walls and is captured when the top shell closes.

**Cross-references:**
- Conceptual architecture: `concept.md` (Section 8: mounting partition integration)
- Spatial resolution: `partition-spatial.md`
- Decomposition: `partition-decomposition.md` (pass-through, no decomposition)
- Pump geometry: `../../off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`
- Bottom shell spatial: `bottom-shell-spatial.md` (slot positions, pump axis positions)
- Bottom shell parts: `bottom-shell-parts.md` (slot dimensions, linkage channel positions)
- Synthesis: `synthesis.md`
- FDM constraints: `../../../requirements.md` (Section 6)
- Vision: `../../../vision.md`

---

## Coordinate System

Origin: bottom-left corner of the plate as it sits on the build plate (printed flat on the XZ face).

- **X axis**: width (left to right when viewed from the front of the cartridge), 0 at left exterior edge, positive rightward. Total extent: 132.0 mm (including side wall engagement tabs).
- **Y axis**: thickness (through-thickness of the plate), 0 at forward face (pump head side), positive rearward (motor side). Total extent: 5.0 mm.
- **Z axis**: height (bottom to top), 0 at bottom edge of main plate body, positive upward. Total extent: 63.0 mm for main body. Registration tabs extend to Z = -2.0 (bottom) and Z = 65.0 (top).

Forward face (pump head side) at Y = 0. Rearward face (motor side) at Y = 5.0. Left edge at X = 0. Right edge at X = 132.0. Bottom edge at Z = 0. Top edge at Z = 63.0.

---

## Mechanism Narrative (Rubric A)

### What the user sees and touches

The user never sees or touches the mounting partition. It is entirely internal to the cartridge, hidden when the top shell closes over the bottom shell. No exterior surface of the cartridge reveals the partition's presence. When the cartridge is assembled, the partition is invisible -- consistent with the vision that every visible feature has an obvious user-facing purpose and the cartridge reads as a sealed black box.

During developer service (top shell removed), the developer sees the partition as a vertical plate dividing the pump head bays (forward) from the motor bays (rearward). Two circular motor bores are visible with motor bodies passing through them. Eight M3 fastener points are visible around the bores (four per pump). Two rectangular notches at the bottom corners allow the linkage arms to pass through.

### What moves

**Nothing on the partition moves during normal operation.** The partition is a stationary structural member. It is rigidly captured between the bottom shell floor/wall slots and the top shell ceiling/wall slots. The pumps are mounted to it via vibration isolation mounts, which absorb motor vibration through rubber compression rather than through relative rigid-body motion.

The linkage arms pass through the bottom-corner notches but do not contact the partition. The arms slide 2-4 mm fore-aft within their floor guide channels; the notches provide passive clearance only.

### What converts the motion

The partition does not convert motion. It is a rigid structural plate. Its function is:

1. **Pump mounting surface:** The rearward face (Y = 5.0) receives the M3 vibration isolation mount studs that hold both pumps. The 48 mm square mounting hole pattern on each side aligns with the pump bracket mounting holes.

2. **Motor clearance:** Two 36.4 mm diameter bores (as-drawn; expected to print at approximately 36.2 mm) allow the motor bodies (~35 mm diameter) to pass through the plate from the pump head side to the motor side.

3. **Load transfer:** Pump weight (200-300 g per pump) transfers through the isolation mounts into the partition, through the partition's side wall tabs into the bottom shell side walls, and through the floor registration tabs into the bottom shell floor.

### What constrains the partition

| Degree of freedom | Constraint | Feature | Dimensions |
|-------------------|-----------|---------|------------|
| Translation X | Side wall slots (left and right) | Left tab (X = 0..2.0) in left slot; right tab (X = 130.0..132.0) in right slot | Slot depth 2.0 mm per side; 0.2 mm clearance in Y |
| Translation Y | Side wall slots | Slot width 5.4 mm constrains 5.0 mm thick partition to 0.2 mm play per side | |
| Translation Z (-Z, downward) | Floor registration tabs | Bottom-left tab at (X = 9..11, Z = -2..0); bottom-right tab at (X = 121..123, Z = -2..0) engage floor slots | Tab 2.0 mm deep into 2.0 mm floor |
| Translation Z (+Z, upward) | Top shell ceiling registration tabs | Top-left tab at (X = 9..11, Z = 63..65); top-right tab at (X = 121..123, Z = 63..65) captured by ceiling slots | Captured when top shell closes |
| Rotation about X | Side wall slots at full height | 63 mm tall engagement along both side walls prevents tilt about X |
| Rotation about Z | Side wall slots at full depth | 2.0 mm tab depth on each side prevents rotation about Z |
| Rotation about Y | Floor + ceiling tabs at two X positions | Two tabs at X = 10 and X = 122 (112 mm apart) prevent rotation about Y |

### What provides the return force

Not applicable. The partition does not move during operation. No return force is needed.

### What is the user's physical interaction

None. The partition is fully internal. The user interacts with the cartridge through the palm surface, finger plate, rail grooves, and tube connections. The partition is never seen, touched, or accessed by the user.

---

## Constraint Chain Diagram (Rubric B)

```
[Pump (x2): 200-300g static weight + motor vibration]
    |
    | (M3 vibration isolation mounts, 4 per pump, rubber decoupling)
    v
[Mounting partition: stationary rigid plate]
    ^ constrained in X by: side wall slot tabs (left X = 0..2, right X = 130..132)
    ^ constrained in Y by: side wall slot width (5.4mm slot, 5.0mm partition, 0.2mm/side)
    ^ constrained in -Z by: floor registration tabs (X = 9..11, X = 121..123, Z = -2..0)
    ^ constrained in +Z by: ceiling registration tabs (X = 9..11, X = 121..123, Z = 63..65)
    |
    | (tab-in-slot engagement, bottom and top)
    v
[Bottom shell floor + side walls: stationary structure]
    |
    | (shell sits on dock rails)
    v
[Dock: stationary in enclosure]
```

Every arrow is labeled. Every constraint is dimensioned. The partition has no unlabeled connections and no unconstrained degrees of freedom.

---

## Features

### 1. Plate Body

| Parameter | Value |
|-----------|-------|
| Shape | Rectangular box |
| X range | 0 to 132.0 mm |
| Y range | 0 to 5.0 mm |
| Z range | 0 to 63.0 mm |
| Material | PETG |
| Wall thickness | 5.0 mm (the plate itself is a solid slab) |
| Function | Structural plate body. Carries pump weight and motor vibration loads. Provides flat mounting surface for vibration isolation mounts on the Y = 5.0 face. |

### 2. Left Motor Bore

| Parameter | Value |
|-----------|-------|
| Shape | Cylindrical through-hole |
| Center (X, Z) | (33.5, 31.3) |
| Axis | Y (through full plate thickness, Y = 0 to Y = 5.0) |
| As-drawn diameter | 36.4 mm |
| Expected as-printed diameter | ~36.2 mm (FDM hole shrinkage: -0.2 mm) |
| Clearance over motor body | 0.5 mm radial on ~35.2 mm worst-case motor body |
| Function | Allows left pump motor body to pass through partition. No contact with motor; clearance only. |
| Source | Motor diameter: caliper photos 15/16 (low confidence, ~34.54-35.13 mm). As-drawn diameter includes +0.2 mm FDM hole compensation per requirements.md. |

### 3. Right Motor Bore

| Parameter | Value |
|-----------|-------|
| Shape | Cylindrical through-hole |
| Center (X, Z) | (98.5, 31.3) |
| Axis | Y |
| As-drawn diameter | 36.4 mm |
| All other parameters | Identical to left motor bore |

### 4. M3 Through-Holes (x8)

Eight clearance holes for M3 vibration isolation mount studs. Two groups of four, one group per pump, each in a 48 mm x 48 mm square pattern centered on the corresponding motor bore.

| Parameter | Value |
|-----------|-------|
| Shape | Cylindrical through-hole |
| Axis | Y (through full plate thickness) |
| As-drawn diameter | 3.6 mm |
| Expected as-printed diameter | ~3.4 mm (M3 clearance) |
| FDM compensation | +0.2 mm per requirements.md |
| Source | 48 mm c-c square pattern: caliper-verified (pump geometry photo 05, 47.88 mm edge-to-edge + 3.13 mm hole diameter = 51.01 mm, yielding 48.0 mm c-c). Hole diameter: M3 clearance standard. |

**Hole positions (partition local frame):**

| Hole | X | Z | Pump | Corner |
|------|---|---|------|--------|
| L1 | 9.5 | 7.3 | Left | Bottom-left |
| L2 | 57.5 | 7.3 | Left | Bottom-right |
| L3 | 9.5 | 55.3 | Left | Top-left |
| L4 | 57.5 | 55.3 | Left | Top-right |
| R1 | 74.5 | 7.3 | Right | Bottom-left |
| R2 | 122.5 | 7.3 | Right | Bottom-right |
| R3 | 74.5 | 55.3 | Right | Top-left |
| R4 | 122.5 | 55.3 | Right | Top-right |

### 5. Left Linkage Arm Notch

| Parameter | Value |
|-----------|-------|
| Shape | Rectangular cut from bottom-left corner of plate body |
| X range | X = 2.0 to X = 10.0 (8.0 mm wide) |
| Z range | Z = 0 to Z = 5.0 (5.0 mm tall from bottom edge) |
| Y range | Full thickness (Y = 0 to Y = 5.0, through-cut) |
| Clearance over arm | 1.0 mm per side in X on 6.0 mm wide arm; 2.0 mm above 3.0 mm tall arm in Z |
| Function | Allows left linkage arm (6 mm W x 3 mm H) to pass through the partition plane without contact. Passive clearance only. |
| Source | Arm dimensions: concept.md. Notch size: concept.md (8 mm x 5 mm). Channel positions: bottom-shell-spatial.md Section 3d. |

### 6. Right Linkage Arm Notch

| Parameter | Value |
|-----------|-------|
| Shape | Rectangular cut from bottom-right corner of plate body |
| X range | X = 122.0 to X = 130.0 (8.0 mm wide) |
| Z range | Z = 0 to Z = 5.0 |
| Y range | Full thickness |
| All other parameters | Mirror of left notch |

### 7. Bottom-Left Registration Tab

| Parameter | Value |
|-----------|-------|
| Shape | Rectangular protrusion from bottom edge |
| X range | X = 9.0 to X = 11.0 (2.0 mm wide) |
| Z range | Z = -2.0 to Z = 0 (2.0 mm tall, extending below plate body) |
| Y range | Y = 0 to Y = 5.0 (full plate thickness) |
| Function | Positive Y-axis and X-axis location at floor level. Tab engages a 2.4 mm wide slot through the bottom shell floor, preventing the partition from sliding fore-aft beyond the side wall slot clearance. |
| Mating feature | Floor slot in bottom shell: shell X = 8.8..11.2, Y = 72.3..77.7, Z = 0..2.0. Slot is 2.4 mm wide in X (tab 2.0 mm + 0.2 mm clearance per side). |

### 8. Bottom-Right Registration Tab

| Parameter | Value |
|-----------|-------|
| Shape | Rectangular protrusion from bottom edge |
| X range | X = 121.0 to X = 123.0 |
| Z range | Z = -2.0 to Z = 0 |
| Y range | Y = 0 to Y = 5.0 |
| Function | Mirror of bottom-left tab |
| Mating feature | Floor slot: shell X = 120.8..123.2, Y = 72.3..77.7, Z = 0..2.0 |

### 9. Top-Left Registration Tab

| Parameter | Value |
|-----------|-------|
| Shape | Rectangular protrusion from top edge |
| X range | X = 9.0 to X = 11.0 |
| Z range | Z = 63.0 to Z = 65.0 (2.0 mm above plate body) |
| Y range | Y = 0 to Y = 5.0 |
| Function | Captured by top shell ceiling slot when shell closes. Prevents upward displacement of partition. |
| Mating feature | Ceiling slot in top shell at matching position |

### 10. Top-Right Registration Tab

| Parameter | Value |
|-----------|-------|
| Shape | Rectangular protrusion from top edge |
| X range | X = 121.0 to X = 123.0 |
| Z range | Z = 63.0 to Z = 65.0 |
| Y range | Y = 0 to Y = 5.0 |
| Function | Mirror of top-left tab |

---

## Assembly Sequence

**Pre-assembly (done outside the cartridge):**

1. Thread 4 M3 vibration isolation mount studs into each pump bracket (8 total).
2. Pass the isolation mount studs through the partition's M3 clearance holes from the motor side (Y = 5.0 face). The pump brackets sit against the Y = 5.0 face. The motor bodies pass through the motor bores. Secure with M3 nuts or self-locking features on the pump head side (Y = 0 face).

**Installation into bottom shell:**

3. Lower the pump-partition assembly into the open-top bottom shell. The partition's bottom-left and bottom-right registration tabs (Z = -2..0) engage the floor slots. The partition's left edge (X = 0..2) and right edge (X = 130..132) drop into the side wall slots (shell Y = 72.3..77.7).
4. The pump heads settle into their respective bays. The linkage arms (already installed in the floor channels from a previous step) pass through the partition's bottom-corner notches.
5. Close the top shell. The partition's top registration tabs (Z = 63..65) are captured by the top shell ceiling slots. The partition is now fully constrained in all six degrees of freedom.

---

## Direction Consistency Check (Rubric C)

| # | Claim | Direction | Axis | Verified? | Notes |
|---|-------|-----------|------|-----------|-------|
| 1 | Partition drops into bottom shell from above | Downward | -Z (partition), -Z (shell) | YES | Side wall slots open at top (Z = 33.5 in bottom shell). Partition inserts in -Z direction. |
| 2 | Floor registration tabs engage floor slots downward | Downward | -Z | YES | Tabs at Z = -2..0 insert into floor at shell Z = 0..2.0. |
| 3 | Top shell captures top registration tabs | Top shell closes in -Z direction | -Z | YES | Top shell moves down onto bottom shell; ceiling slots capture partition top tabs. |
| 4 | Pumps mount on the motor side (Y = 5.0 face) | Rearward face | +Y face | YES | Pump brackets face the motor direction. Motor bodies pass through bores from front (Y = 0) to rear (Y = 5.0). Isolation mount studs thread from Y = 5.0 face through to Y = 0 face. |
| 5 | Linkage arms pass through bottom-corner notches | Fore-aft (Y direction) | Y | YES | Arms run along the floor in the Y direction; notches are rectangular clearance cuts open in Y. |
| 6 | Pump weight transfers through partition into floor | Gravity pulls pump mass in -Z | -Z | YES | Load path: pump -> isolation mounts -> partition -> floor registration tabs -> bottom shell floor. |

No contradictions found.

---

## Interface Dimensional Consistency (Rubric D)

| # | Interface | Part A dimension | Part B dimension | Clearance | Source |
|---|-----------|-----------------|-----------------|-----------|--------|
| 1 | Partition thickness / side wall slot width | 5.0 mm (Y) | 5.4 mm slot (Y) | 0.2 mm/side | Partition: concept. Slot: bottom-shell-spatial 3e. |
| 2 | Side wall tab depth / slot depth | 2.0 mm (X, each side) | 2.0 mm slot depth (X) | Flush fit (tab fills slot) | Partition-spatial 3b. Bottom-shell-spatial 3e. |
| 3 | Floor registration tab width / floor slot width | 2.0 mm (X) | 2.4 mm slot (X) | 0.2 mm/side | Partition-spatial 3f. Floor slot: new feature, specified here. |
| 4 | Floor registration tab thickness / floor slot depth | 5.0 mm (Y, full partition thickness) | 5.4 mm (Y, matching side wall slot Y extent) | 0.2 mm/side | Consistent with side wall clearance. |
| 5 | Floor registration tab height / floor thickness | 2.0 mm (Z) | 2.0 mm floor (Z) | Flush (tab fills floor thickness) | Tab Z = -2..0 = 2 mm. Floor shell Z = 0..2.0 = 2 mm. |
| 6 | Motor bore as-printed / motor body | ~36.2 mm dia | ~35.0-35.2 mm motor dia | ~0.5 mm radial | Bore: 36.4 mm as-drawn - 0.2 mm print shrink. Motor: caliper photos 15/16 (low confidence). |
| 7 | M3 hole as-printed / M3 stud | ~3.4 mm dia | 3.0 mm M3 stud | 0.2 mm radial | Standard M3 clearance fit. |
| 8 | Linkage notch width / arm width | 8.0 mm | 6.0 mm arm | 1.0 mm/side | Concept: 8 mm notch, 6 mm arm. |
| 9 | Linkage notch height / arm height | 5.0 mm | 3.0 mm arm | 2.0 mm above | Concept: 5 mm notch, 3 mm arm. |

No zero-clearance or mismatched dimensions found. Interface #6 (motor bore) has a low-confidence motor diameter -- flagged as an open question in the synthesis document. The bore is sized conservatively.

---

## Assembly Feasibility Check (Rubric E)

| Step | Physically feasible? | Notes |
|------|---------------------|-------|
| 1. Thread isolation mounts into pump brackets | YES | Standard M3 screwdriver work. Done in-hand, full access. |
| 2. Mount pumps to partition via isolation mounts | YES | Partition is free-standing. Studs pass through 3.6 mm holes from Y = 5.0 face. Full access from both sides. |
| 3. Lower pump-partition assembly into bottom shell | YES | Bottom shell is open-top. Assembly lowers vertically. Side wall slots are open at top (Z = 33.5). Floor slots are accessible from above. Pump bays are 63 mm wide for 62.6 mm pump heads. |
| 4. Verify linkage arms pass through notches | YES | Arms are already in floor channels. Notches (8 mm x 5 mm) clear the arms (6 mm x 3 mm) with 1 mm/side margin. |
| 5. Close top shell | YES | Top shell lowers onto bottom shell. Ceiling slots capture partition top tabs. Snap-fits engage. |

**Disassembly sequence:** Remove development screws (if present). Pry top shell off. Lift pump-partition assembly straight up and out of bottom shell (reversal of step 3). Remove pumps from partition by unscrewing 8 M3 isolation mount fasteners.

No parts become trapped or inaccessible. The partition is always the last internal component installed (after linkage arms, springs, and release plate) and the first removed during disassembly (after top shell removal).

---

## Part Count Minimization (Rubric F)

| Part pair | Permanently joined? | Move relative to each other? | Same material? | Could combine? | Verdict |
|-----------|--------------------|-----------------------------|----------------|----------------|---------|
| Partition + bottom shell | No (captured, removable) | No (stationary when assembled) | Yes (both PETG) | Could integrate as a vertical wall rising from the floor | **Keep separate.** Concept Section 1 rationale: a wall rising from the bottom shell with no top support would be fragile during pump installation (60+ mm tall, 5 mm thick wall is snappable during assembly). Separate partition drops in safely after pumps are pre-mounted. Also, partition spans full 63 mm height -- cannot be integral to either half-shell alone. |
| Partition + top shell | No | No | Yes | Could integrate as a wall descending from ceiling | **Keep separate.** Same rationale as above. Additionally, the partition must be installed with pumps already mounted (pre-assembly step), which is impossible if the partition is part of the top shell. |
| Registration tabs + plate body | Yes (integral) | No | Same part | Already one piece | OK |

Part count is minimized. The partition is a single part. No further consolidation is possible without compromising assembly feasibility.

---

## FDM Printability (Rubric G)

### Step 1 -- Print Orientation

**Orientation: flat on the build plate, lying on the XZ face (large face down).**

The partition's large face (132 mm x 63 mm) sits on the build plate. The part is printed as a 5 mm tall extrusion (plus registration tabs). All through-holes (motor bores, M3 holes) run vertically (Z axis in print orientation), producing perfect circles.

**Why this orientation:**
- Motor bores (36.4 mm diameter) print as vertical circles -- best possible circularity and dimensional accuracy. Printing the partition on-edge (63 mm tall, 5 mm wide) would make these bores horizontal bridges, destroying accuracy.
- M3 holes (3.6 mm diameter) print as vertical circles -- accurate diameter for clearance fit.
- The part is only 5 mm tall in this orientation (~25 layers at 0.2 mm), producing a very fast print with minimal Z-accumulation error.
- The build plate face is flat and smooth, suitable for the mounting surface that receives vibration isolation mounts.

### Step 2 -- Overhang Audit

In the flat print orientation, the plate thickness direction (Y in the partition frame) becomes the print Z direction.

| # | Surface / Feature | Angle from horizontal | Printable? | Resolution |
|---|-------------------|-----------------------|------------|------------|
| 1 | Plate top face (Y = 5.0) | 0 degrees (horizontal, top face) | OK | Top face of extrusion, no overhang |
| 2 | Plate bottom face (Y = 0) | 0 degrees (on build plate) | OK | Build plate face |
| 3 | All vertical side walls (X = 0, X = 132, Z = 0, Z = 63) | 90 degrees | OK | Vertical walls, no overhang |
| 4 | Motor bore interior walls | 90 degrees (vertical cylinder walls) | OK | Vertical cylinder, no bridging |
| 5 | M3 hole interior walls | 90 degrees | OK | Vertical cylinder |
| 6 | Linkage notch walls (vertical cuts at X = 2..10, Z = 0..5) | 90 degrees | OK | Rectangular pocket with vertical walls |
| 7 | Registration tab vertical faces | 90 degrees | OK | Vertical walls |
| 8 | Registration tab bottom faces (Z = -2 tabs: the underside as printed) | 0 degrees (horizontal, bridged) | NEEDS REVIEW | See below |

**Registration tab overhang resolution:** The floor registration tabs (Z = -2..0) extend below the main plate body. When printed flat, the main body sits at print Z = 0..5 mm. The bottom tabs (partition Z = -2..0) would need to be printed below the main body, which is impossible -- you cannot print below the build plate.

**Resolution:** Print the part with the bottom edge (Z = 0 of the main body) on the build plate. The floor registration tabs (Z = -2..0) project downward from Z = 0 and cannot be printed in this orientation. Similarly, the top registration tabs (Z = 63..65) project upward and CAN be printed (they add 2 mm of extrusion above the main body at specific X locations).

For the bottom tabs, two options:

**Option A (preferred): Reorient the tabs.** Instead of projecting downward from the bottom edge, make the bottom registration tabs project in the Y direction (rearward) from the bottom of the plate. This changes them from Z-direction protrusions to Y-direction protrusions. As printed flat, Y-direction protrusions become Z-direction protrusions -- perfectly printable.

**Option B: Print the partition on its bottom edge.** The 132 mm x 5 mm bottom edge sits on the build plate. The part is then 63 mm tall with 132 mm width. All registration tabs print naturally. But the motor bores become horizontal holes (requiring bridging on the top half of each 36.4 mm bore), and the part is tall and thin (63 mm tall x 5 mm thick), prone to vibration and poor surface quality.

**Decision: Option A.** The bottom and top registration tabs become Y-direction protrusions (rearward from the partition face) rather than Z-direction protrusions. This changes the tab geometry:

**Revised bottom registration tabs (Y-direction protrusion from bottom zone):**

| Tab | X range | Y range | Z range | Function |
|-----|---------|---------|---------|----------|
| Bottom-left | X = 9.0..11.0 | Y = 5.0..7.0 (protrudes 2 mm past rearward face) | Z = 0..2.0 (bottom 2 mm of plate height) | Engages a floor-level slot in the bottom shell that constrains Y translation |
| Bottom-right | X = 121.0..123.0 | Y = 5.0..7.0 | Z = 0..2.0 | Mirror |

**Revised top registration tabs (Y-direction protrusion from top zone):**

| Tab | X range | Y range | Z range | Function |
|-----|---------|---------|---------|----------|
| Top-left | X = 9.0..11.0 | Y = 5.0..7.0 | Z = 61.0..63.0 (top 2 mm of plate height) | Engages ceiling-level slot in top shell |
| Top-right | X = 121.0..123.0 | Y = 5.0..7.0 | Z = 61.0..63.0 | Mirror |

These Y-direction tabs are printed as 2 mm tall extrusions above the main plate body at specific X and Z locations. No overhangs. No bridging. The mating slots in the bottom shell and top shell must be correspondingly repositioned to engage these Y-direction tabs (slots cut into the rear wall surfaces at floor level and ceiling level, rather than through the floor/ceiling).

**Updated mating features in bottom shell:**

The floor-level slots become notches on the inboard face of the rear wall area at the partition Y position. Specifically: at bottom shell coordinates (X = 9.0..11.0, Y = 77.7..79.7, Z = 2.0..4.0) and (X = 121.0..123.0, Y = 77.7..79.7, Z = 2.0..4.0). These are 2 mm wide (X) x 2 mm deep (Y, behind the partition slot) x 2 mm tall (Z, just above the floor) notches in the cavity wall behind the partition slot.

**DESIGN GAP: The bottom shell parts spec must be updated to add these tab-receiving notches. The original concept's "floor slots" are replaced by Y-direction notch slots behind the partition position.**

### Step 3 -- Wall Thickness Check

| Feature | Thickness | Minimum required | OK? |
|---------|-----------|-----------------|-----|
| Plate body | 5.0 mm | 1.2 mm (structural) | YES -- well above minimum. Carries pump weight loads. |
| Wall between motor bore and M3 hole (thinnest section) | See below | 1.2 mm | See below |
| Wall between motor bore edge and plate edge | See below | 0.8 mm | See below |

**Thinnest wall check -- motor bore to M3 hole:**

Left motor bore center: (33.5, 31.3), radius 18.2 mm (as-drawn 36.4/2). Nearest M3 hole: L1 at (9.5, 7.3). Distance center-to-center: sqrt((33.5-9.5)^2 + (31.3-7.3)^2) = sqrt(576 + 576) = sqrt(1152) = 33.94 mm. Wall thickness: 33.94 - 18.2 (bore radius) - 1.8 (M3 hole radius) = 13.94 mm. Well above 1.2 mm.

**Thinnest wall check -- motor bore to nearest plate edge:**

Left bore center X = 33.5, bore radius = 18.2. Nearest body edge: X = 2.0 (left body edge). Distance from bore edge to body edge: 33.5 - 18.2 - 2.0 = 13.3 mm. Well above 1.2 mm.

Nearest Z edge: Z = 0 (bottom). Distance: 31.3 - 18.2 = 13.1 mm. Well above 1.2 mm.

**Thinnest wall between the two motor bores:**

Left bore center X = 33.5, right bore center X = 98.5. Distance: 65.0 mm. Wall between bore edges: 65.0 - 18.2 - 18.2 = 28.6 mm. Well above 1.2 mm.

All walls pass.

### Step 4 -- Bridge Span Check

When printed flat (XZ face on build plate, 5 mm tall):

| Feature | Span | Under 15 mm? | Notes |
|---------|------|--------------|-------|
| Motor bore top (if any bridging) | 0 mm | N/A | Bore is a vertical cylinder. No bridging at all -- the slicer traces circular perimeters. |
| M3 hole top | 0 mm | N/A | Same -- vertical cylinder, no bridging. |
| Registration tabs | No unsupported spans | N/A | Tabs are solid extrusions on top of the main body. |

No bridges exist in this print orientation. All through-features are vertical cylinders.

### Step 5 -- Layer Strength Check

| Feature | Load direction | Layer orientation | OK? |
|---------|---------------|-------------------|-----|
| Main plate body (pump weight in -Z) | Compression in plate plane (bending under pump cantilever loads) | Layers stack through the 5 mm thickness. Bending loads are in the XZ plane, parallel to layers. | YES -- layers carry load in their strong direction (in-plane). |
| Motor bore walls | Radial compression from isolation mount clamping | Layers are circumferential around vertical bores. | YES -- layers wrap around the bore perimeter. |
| Side wall tabs | Shear at the wall-slot interface | Layers stack through the 5 mm thickness. Shear is in the XZ plane. | YES -- in-plane shear is the strong direction for FDM. |

No features bear load perpendicular to layers. The flat print orientation places all structural loads in the strong (in-plane) direction.

---

## Updated Feature List (Post-Printability Review)

The printability review changed the registration tabs from Z-direction protrusions to Y-direction protrusions. The revised feature list:

| # | Feature | Shape | Operation | X range | Y range | Z range | Key dimension |
|---|---------|-------|-----------|---------|---------|---------|--------------|
| 1 | Plate body | Box | Base body | 0..132 | 0..5 | 0..63 | 132 x 5 x 63 mm |
| 2 | Left motor bore | Cylinder | Cut | Center (33.5, 31.3) | Full Y | | Dia 36.4 mm as-drawn |
| 3 | Right motor bore | Cylinder | Cut | Center (98.5, 31.3) | Full Y | | Dia 36.4 mm as-drawn |
| 4 | M3 holes (x8) | Cylinder | Cut | See table | Full Y | See table | Dia 3.6 mm as-drawn |
| 5 | Left linkage notch | Box | Cut | 2..10 | Full Y | 0..5 | 8 x 5 x 5 mm |
| 6 | Right linkage notch | Box | Cut | 122..130 | Full Y | 0..5 | 8 x 5 x 5 mm |
| 7 | Bottom-left reg tab | Box | Add | 9..11 | 5..7 | 0..2 | 2 x 2 x 2 mm |
| 8 | Bottom-right reg tab | Box | Add | 121..123 | 5..7 | 0..2 | 2 x 2 x 2 mm |
| 9 | Top-left reg tab | Box | Add | 9..11 | 5..7 | 61..63 | 2 x 2 x 2 mm |
| 10 | Top-right reg tab | Box | Add | 121..123 | 5..7 | 61..63 | 2 x 2 x 2 mm |

---

## Print Specification

| Parameter | Value |
|-----------|-------|
| Material | PETG |
| Print orientation | Flat on build plate (XZ face down, partition Y=0 face on bed) |
| Build plate footprint | 132 mm x 63 mm |
| Print height | 7.0 mm (5.0 mm plate body + 2.0 mm registration tabs) |
| Layer height | 0.2 mm |
| Approximate layer count | 35 |
| Supports required | None |
| Elephant's foot chamfer | 0.3 mm x 45 degrees on bottom perimeter edge (Y = 0 plane, which is the build plate face). Not applied to the build-plate face of the tabs since they are on top of the part, not on the build plate. |
| Exterior fillets | Not required. The partition is fully internal and never seen by the user. Sharp edges are acceptable for an internal structural part. |

---

## Modifications Required to Other Parts

### Bottom Shell

The bottom shell parts spec (`bottom-shell-parts.md`) must be updated to add:

1. **Two Y-direction tab-receiving notches at floor level:** At bottom shell coordinates:
   - Left notch: X = 8.8..11.2, Y = 77.7..79.7, Z = 2.0..4.0
   - Right notch: X = 120.8..123.2, Y = 77.7..79.7, Z = 2.0..4.0
   - Each is 2.4 mm wide (X, tab 2.0 mm + 0.2 mm/side clearance) x 2.0 mm deep (Y, behind the partition rear face) x 2.0 mm tall (Z, above the floor interior)

### Top Shell

The top shell spec (when created) must include:

1. **Matching side wall slots** at Y = 72.3..77.7 (continuing the bottom shell slots above Z = 33.5).
2. **Two Y-direction tab-receiving notches at ceiling level** at matching positions (mirror of the floor-level notches, relative to the ceiling).

### Spatial Resolution Document

The partition spatial resolution document (`partition-spatial.md`) describes the original Z-direction tab geometry. The printability review changed these to Y-direction tabs. **The spatial resolution document should be considered superseded by this parts specification for registration tab geometry.** The revised tab geometry is defined in the "Updated Feature List" section above.
