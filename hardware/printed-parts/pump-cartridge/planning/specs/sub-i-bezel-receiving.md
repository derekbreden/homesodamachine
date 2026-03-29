# Sub-I: Front Bezel Receiving Features -- Parts Specification

Cuts applied to the tray box shell (Sub-A) at the Y = 155 front face. These features receive the front bezel via a step-lap rabbet (shadow-line seam) and six snap tab pockets (detent recesses). Sub-I adds no material -- every feature is a rectangular pocket or rabbet cut from existing Sub-A geometry.

---

## Coordinate System

Same as the tray (Sub-A):

- **Origin**: rear-left-bottom corner (dock side)
- **X axis**: width, 0..160 mm (left to right when facing the front)
- **Y axis**: depth, 0..155 mm (0 = rear/dock, 155 = front/user)
- **Z axis**: height, 0..72 mm (0 = floor bottom, 72 = top of side walls)
- **Print orientation**: open top facing up, XY plane on build plate
- **Installed orientation**: identical (identity transform)

All Sub-I features lie at or near the Y = 155 face.

---

## Mechanism Narrative

### What the user sees and touches

The user never interacts with Sub-I features directly. These are internal receiving geometry hidden inside the tray-to-bezel joint. The user sees only the front bezel's outer face (the palm rest surface). The shadow-line seam -- a 1.5 mm step where the bezel overlaps the tray -- is visible as a thin dark line running around the front perimeter of the cartridge. This seam is the only external evidence of Sub-I.

### What moves

**During bezel installation:** The front bezel translates in the -Y direction (pushed onto the tray from the front, toward the dock). The bezel's six cantilevered snap tabs deflect inward as they pass the tray's front edges, then spring outward into the six Sub-I pockets. The tray is stationary throughout.

**During operation:** Nothing moves. The bezel is retained by the six snap tab engagements and the step-lap rabbet prevents lateral shifting.

### What converts the motion

The user's push force (-Y) is converted to snap tab deflection by the ramp geometry on the bezel's tab barbs (the ramp is on the bezel, not on the tray). As each tab barb slides past the tray's front edge, the angled leading face of the barb wedges the tab inward. Once the barb clears the edge and reaches the pocket, the tab's cantilever spring force pushes it outward into the pocket recess. The pocket's rear wall (the face at Y = 152) captures the barb and prevents the bezel from pulling back in the +Y direction.

The step-lap rabbet converts the same -Y push into precise lateral registration: the bezel's inner perimeter contacts the rabbet ledge surfaces (X = 1.5, X = 158.5, and Z = 1.5 planes), preventing movement in X and Z.

### What constrains each part

**Tray (stationary):** Constrained by the dock rails during use, or by the user's other hand during assembly.

**Bezel (after installation):**
- **-Y (toward dock):** Six snap tab barbs bear against the rear walls of the six pockets at Y = 152.
- **+Y (away from dock):** The barb's lock face catches the pocket opening edge at Y = 155 (the front face of the tray wall/floor). The barb cannot back out because the lock face is perpendicular to Y.
- **X (lateral):** The bezel's inner left face seats against the left wall rabbet ledge at X = 1.5. The bezel's inner right face seats against the right wall rabbet ledge at X = 158.5. The 157 mm span between these two ledges matches the bezel's inner width (157 mm nominal, with 0.2 mm clearance per side built into the bezel, not the tray).
- **Z (vertical):** The bezel's inner bottom face seats against the floor rabbet ledge at Z = 1.5. The bezel's top edge butts against the lid's front edge at Z = 72. The pocket at T1 provides additional +Z retention at the top.

### What provides the return force

There is no return force. The bezel is intended to stay installed. Removal requires the user to depress all six snap tabs simultaneously (practically: flex the bezel sides inward slightly while pulling +Y). The cantilever spring force of the bezel tabs holds them in the pockets during normal use.

### What is the user's physical interaction

1. The user holds the tray with one hand (or the tray is seated in the dock).
2. The user aligns the bezel to the tray's front face, inner perimeter facing the tray. The rabbet ledges self-center the bezel laterally and vertically.
3. The user pushes the bezel firmly in the -Y direction. Six clicks are felt in rapid succession (or near-simultaneously) as each snap tab barb clears the tray edge and springs into its pocket. The 1.5 mm barb engagement depth produces a definitive tactile pop at each pocket.
4. The user confirms engagement by attempting to pull the bezel in the +Y direction. It should not move. The step-lap overlap and six detent captures hold the bezel rigid.

---

## Constraint Chain Diagram

```
[User hand: pushes bezel -Y] -> [Bezel: translates -Y] -> [Tab barb ramps: wedge tabs inward]
                                                            -> [Tabs spring outward into 6 pockets]
                                                                ^ captured by: pocket rear wall at Y=152

[Bezel lateral position] -> [Rabbet ledge X=1.5 (left)] + [Rabbet ledge X=158.5 (right)]
                             ^ constrains -X               ^ constrains +X

[Bezel vertical position] -> [Rabbet ledge Z=1.5 (floor)] + [Lid front edge at Z=72 (top)]
                              ^ constrains -Z                ^ constrains +Z

[Bezel axial position]    -> [Tab barbs in pockets: prevent +Y pull-out]
                           -> [Rabbet ledge depth: seats bezel at Y=153.5..155]
```

Every arrow is labeled. Every constraint names a geometric feature.

---

## Features

### Feature 1: Step-Lap Rabbet

A 1.5 mm deep x 1.5 mm wide step cut around the exterior perimeter of the Y = 155 face. This rabbet creates the ledge surfaces where the bezel's inner face seats, producing the shadow-line seam.

The rabbet runs along three segments (no top segment -- the tray is open-top):

#### Left Wall Rabbet

| Parameter | Value |
|-----------|-------|
| Cut volume (tray frame) | X = 0..1.5, Y = 153.5..155, Z = 0..72 |
| Depth into wall (X) | 1.5 mm (removes outer 1.5 mm of the 5 mm left wall) |
| Extent in Y | 1.5 mm (from Y = 153.5 to Y = 155) |
| Extent in Z | 72 mm (full wall height, Z = 0 to Z = 72) |
| Remaining wall thickness at front edge | 3.5 mm (5.0 - 1.5) |
| Resulting ledge surface | X = 1.5 plane, spanning Y = 153.5..155, Z = 0..72 |

#### Right Wall Rabbet

| Parameter | Value |
|-----------|-------|
| Cut volume (tray frame) | X = 158.5..160, Y = 153.5..155, Z = 0..72 |
| Depth into wall (X) | 1.5 mm (removes outer 1.5 mm of the 5 mm right wall) |
| Extent in Y | 1.5 mm (from Y = 153.5 to Y = 155) |
| Extent in Z | 72 mm (full wall height, Z = 0 to Z = 72) |
| Remaining wall thickness at front edge | 3.5 mm (5.0 - 1.5) |
| Resulting ledge surface | X = 158.5 plane, spanning Y = 153.5..155, Z = 0..72 |

#### Floor Rabbet

| Parameter | Value |
|-----------|-------|
| Cut volume (tray frame) | X = 0..160, Y = 153.5..155, Z = 0..1.5 |
| Depth into floor (Z) | 1.5 mm (removes bottom 1.5 mm of the 3 mm floor) |
| Extent in Y | 1.5 mm (from Y = 153.5 to Y = 155) |
| Extent in X | 160 mm (full tray width, including through the wall corners) |
| Remaining floor thickness at front edge | 1.5 mm (3.0 - 1.5) |
| Resulting ledge surface | Z = 1.5 plane, spanning X = 0..160, Y = 153.5..155 |

#### Corner Treatment

Where the left/right wall rabbets meet the floor rabbet (at the two bottom-front corners of the tray), the cut volumes intersect naturally, producing inside corners. These inside corners receive a 1 mm fillet for printability and stress relief. The fillets run along the Y axis (1.5 mm long, from Y = 153.5 to Y = 155) at coordinates:

- Left bottom corner: intersection of X = 1.5 plane and Z = 1.5 plane
- Right bottom corner: intersection of X = 158.5 plane and Z = 1.5 plane

Fillet radius: 1.0 mm. This matches the internal corner fillet convention from the concept document (Section 5).

---

### Feature 2: Snap Tab Pockets

Six rectangular pocket cuts in the tray's front edges that receive the bezel's cantilevered snap tabs. All six pockets share identical cross-sectional dimensions; only their positions and orientations differ.

#### Common Pocket Dimensions

| Parameter | Value |
|-----------|-------|
| Width (along the host edge, parallel to pocket opening) | 5.0 mm |
| Depth into tray body (in Y, away from Y = 155 face) | 3.0 mm (from Y = 152 to Y = 155) |
| Height (perpendicular to host wall/floor face, into wall) | 1.5 mm |
| Pocket opening face | Flush with the interior surface of the host wall/floor |

The 3.0 mm Y extent means each pocket extends 1.5 mm behind the rabbet step (the rabbet occupies Y = 153.5..155; the pocket extends to Y = 152). This is intentional: the bezel tab barb must reach past the rabbet ledge to latch behind it. The barb engages the rear wall of the pocket at Y = 152, providing 1.5 mm of engagement depth behind the rabbet step.

#### Pocket L1 (Left Wall, Lower)

| Parameter | Value |
|-----------|-------|
| Host surface | Interior face of left wall (X = 5 plane) |
| Center position (tray frame) | (4.25, 153.5, 22.0) |
| Cut volume | X = 3.5..5.0, Y = 152..155, Z = 19.5..24.5 |
| Cut depth into wall (X) | 1.5 mm (from X = 5.0 inward to X = 3.5) |
| Remaining wall thickness at pocket | 3.5 mm (5.0 - 1.5) |
| Tab approach | Bezel tab on left inner face deflects +X during insertion, springs -X into pocket |

#### Pocket L2 (Left Wall, Upper)

| Parameter | Value |
|-----------|-------|
| Host surface | Interior face of left wall (X = 5 plane) |
| Center position (tray frame) | (4.25, 153.5, 50.0) |
| Cut volume | X = 3.5..5.0, Y = 152..155, Z = 47.5..52.5 |
| Cut depth into wall (X) | 1.5 mm (from X = 5.0 inward to X = 3.5) |
| Remaining wall thickness at pocket | 3.5 mm (5.0 - 1.5) |
| Tab approach | Bezel tab on left inner face deflects +X during insertion, springs -X into pocket |

#### Pocket R1 (Right Wall, Lower)

| Parameter | Value |
|-----------|-------|
| Host surface | Interior face of right wall (X = 155 plane) |
| Center position (tray frame) | (155.75, 153.5, 22.0) |
| Cut volume | X = 155.0..156.5, Y = 152..155, Z = 19.5..24.5 |
| Cut depth into wall (X) | 1.5 mm (from X = 155.0 outward to X = 156.5) |
| Remaining wall thickness at pocket | 3.5 mm (5.0 - 1.5) |
| Tab approach | Bezel tab on right inner face deflects -X during insertion, springs +X into pocket |

#### Pocket R2 (Right Wall, Upper)

| Parameter | Value |
|-----------|-------|
| Host surface | Interior face of right wall (X = 155 plane) |
| Center position (tray frame) | (155.75, 153.5, 50.0) |
| Cut volume | X = 155.0..156.5, Y = 152..155, Z = 47.5..52.5 |
| Cut depth into wall (X) | 1.5 mm (from X = 155.0 outward to X = 156.5) |
| Remaining wall thickness at pocket | 3.5 mm (5.0 - 1.5) |
| Tab approach | Bezel tab on right inner face deflects -X during insertion, springs +X into pocket |

#### Pocket F1 (Floor, Center)

| Parameter | Value |
|-----------|-------|
| Host surface | Top face of floor (Z = 3 plane) |
| Center position (tray frame) | (80.0, 153.5, 2.25) |
| Cut volume | X = 77.5..82.5, Y = 152..155, Z = 1.5..3.0 |
| Cut depth into floor (Z) | 1.5 mm (from Z = 3.0 downward to Z = 1.5) |
| Remaining floor thickness at pocket | 1.5 mm (3.0 - 1.5) |
| Tab approach | Bezel tab on bottom edge deflects +Z during insertion, springs -Z into pocket |

Note: F1's pocket floor is at Z = 1.5, which coincides with the floor rabbet ledge surface. The pocket is carved out of the rabbet step itself -- the rabbet removes material from Z = 0..1.5, and the pocket removes material from Z = 1.5..3.0. These are complementary, non-overlapping cuts.

#### Pocket T1 (Top Edge, Center)

| Parameter | Value |
|-----------|-------|
| Host surface | Top face of side wall at front edge (Z = 72 plane) |
| Center position (tray frame) | (80.0, 153.5, 71.25) |
| Cut volume | X = 77.5..82.5, Y = 152..155, Z = 70.5..72.0 |
| Cut depth from top surface (Z) | 1.5 mm (from Z = 72.0 downward to Z = 70.5) |
| Notes | Cut into the top edge at the X midline. This is not inside a wall -- it is an open recess on the top edge of the tray between the side walls. The bezel's top tab wraps over this edge and latches downward. When the lid is installed, the lid's front edge sits adjacent, adding retention. |
| Tab approach | Bezel tab on top edge deflects -Z during insertion, springs +Z into pocket |

**DESIGN GAP: T1 sits between the side walls at X = 77.5..82.5 on the top edge. At this X position there is no wall -- the tray is open-top with walls only at X = 0..5 (left) and X = 155..160 (right). The floor spans X = 5..155 at Z = 0..3 only. There is no solid material at X = 77.5..82.5, Y = 152..155, Z = 70.5..72 to cut the pocket into. T1 requires either: (a) a cross-beam or bridge at the top of the tray front edge spanning the open gap, which Sub-A does not currently provide, or (b) relocating T1 onto the top of the left or right side wall where solid material exists (e.g., X = 0..5 or X = 155..160 at Z = 70.5..72). This must be resolved before T1 can be manufactured.**

---

## Finger Channel Clearance

The bezel has finger channels (vertical slots, approximately 25 mm deep x 15 mm wide) centered vertically on its left and right edges, spanning approximately Z = 22..47. Pockets L1/L2 and R1/R2 are positioned at Z = 19.5..24.5 and Z = 47.5..52.5 respectively -- bracketing the finger channel zone from below and above. This avoids interference: no pocket overlaps the Z = 24.5..47.5 channel opening zone.

---

## Material and Print Notes

- **Material:** PETG (per concept document Section 5/7)
- **Print orientation:** Tray prints open-top-up. All Sub-I cuts are in the XZ plane at the Y = 155 end, perpendicular to the build plate. The rabbet and pockets are simple rectangular voids -- no supports needed for any Sub-I feature. The rabbet is a step on the outer face; the pockets are shallow internal recesses.
- **Minimum wall remaining:** 1.5 mm (floor at F1 pocket and at floor rabbet). This is 7.5 layers at 0.2 mm layer height -- adequate for PETG structural integrity, especially since the bezel reinforces this zone once installed.
- **Tolerances:** All pocket dimensions are nominal (as specified). The bezel's snap tabs are the compliant members -- tab thickness and barb geometry on the bezel side are designed to provide the necessary deflection and retention force. The tray pockets are rigid receivers and require no compliance.

---

## Assembly Sequence (Sub-I context only)

Sub-I features are cuts in the tray -- they exist as manufactured geometry, not assembled parts. The relevant assembly is the bezel-to-tray installation:

1. **Tray is complete** (all Sub-A through Sub-H features applied, Sub-I cuts made).
2. **Lid is installed** on the tray (Sub-H snap tabs engaged). The lid must be installed before the bezel so the bezel's top edge can bridge the tray-to-lid seam.
3. **Bezel is aligned** to the tray front face. The rabbet ledges guide lateral and vertical registration.
4. **Bezel is pushed in -Y direction.** The six snap tabs deflect and latch into the six pockets. All six engage in a single push.
5. **Bezel is fully seated** when its inner perimeter is flush against the rabbet ledges and all six tabs have clicked into pockets.

**Disassembly:** Flex the bezel's side walls inward slightly (compressing left and right tabs out of L1/L2 and R1/R2 pockets) while pulling +Y. The floor tab (F1) and top tab (T1) release as the bezel lifts away. No tools required, but deliberate force is needed -- accidental release during normal handling does not occur because all six tabs must be simultaneously disengaged.

---

## Design Gaps

1. **T1 pocket location has no solid material.** The tray is open-top between the side walls. At X = 77.5..82.5, Z = 70.5..72, there is no wall or beam to cut T1 into. Resolution options: (a) add a cross-beam to Sub-A at the front top edge, (b) relocate T1 to the top of a side wall (X = 0..5 or X = 155..160), or (c) eliminate T1 and rely on five pockets (four side + one floor) plus the lid's front edge for top retention. This gap must be resolved before the tray can be manufactured.
