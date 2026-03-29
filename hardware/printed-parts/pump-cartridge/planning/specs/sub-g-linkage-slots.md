# Sub-G: Linkage Rod Guide Slots -- Parts Specification

Two identical rectangular through-slots, one in each side wall of the tray, allowing the 4 mm diameter linkage rods to pass from the interior release plate through the walls to the exterior. The rods slide fore-aft within the slots during the 1.5 mm squeeze-release travel. These are purely subtractive features (cuts) applied to the Sub-A box shell.

---

## Coordinate System

Same as the tray reference frame (Sub-A):

- **Origin**: rear-left-bottom corner of the tray.
- **X axis**: width, 0 to 160 mm (0 = left wall exterior, 160 = right wall exterior).
- **Y axis**: depth, 0 to 155 mm (0 = dock/rear, 155 = user/front).
- **Z axis**: height, 0 to 72 mm (0 = floor bottom, 72 = top edge).

Left wall spans X = 0 to 5 mm (5 mm thick). Right wall spans X = 155 to 160 mm (5 mm thick).

---

## Mechanism Narrative

### What the user sees and touches

The user never sees or touches the linkage rod guide slots. They are internal to the tray, hidden behind the front bezel and inside the dock during normal operation. During assembly (one-time, at build), the slots are visible as rectangular openings in the left and right side walls.

### What moves

**During operation (squeeze-release):**
- The linkage rods translate along Y within the slots. Each rod is a 4 mm diameter rigid PETG rod running parallel to the Y axis. When the user squeezes the front bezel (pressing the palm surface while pulling the finger tabs), the release plate moves 1.5 mm toward the user (+Y). The linkage rods, attached to the release plate at one end and to the pull-tab paddles at the other, translate +Y by the same 1.5 mm. The rods slide within the slots during this motion.

**Stationary parts:**
- The tray side walls (Sub-A box shell) are stationary. The slots are fixed openings in these walls.

### What converts the motion

No motion conversion occurs at the slots. The slots are passive guides. The rods translate linearly along Y; the slots simply permit this translation while constraining the rods in X and Z. The motion originates at the pull-tab paddles (user finger force along +Y), transmits through the rigid linkage rods, and arrives at the release plate. The slots are in the force path but do not transform direction or magnitude.

### What constrains each moving part

Each linkage rod is constrained by its slot in two axes:
- **Z constraint**: The slot width (Z dimension) is 5.0 mm, accommodating the 4 mm rod with 0.5 mm clearance per side. This prevents the rod from moving up or down.
- **X constraint**: The slot cuts through the full 5 mm wall thickness. The rod passes through this 5 mm bore along X and is constrained laterally by the slot walls on either side in Z and the slot ends in Y.
- **Y constraint (travel limits)**: The slot length (Y dimension) is 6.0 mm. With the 4 mm rod diameter inside, there is 1.0 mm of free Y travel at each end when the rod is centered, or 2.0 mm total linear travel. The release plate's actual travel is 1.5 mm, leaving 0.25 mm clearance at each end of the stroke.

The rod's remaining degrees of freedom (rotation about its own axis, and translation along X through the wall) are constrained by the rod's attachment to the release plate on the interior side and to the pull-tab paddle on the exterior side.

### What provides the return force

No return force originates at the slots. The slots are passive. Return force is provided by the John Guest fitting collet springs acting on the release plate (pushing the plate back toward the rear wall, -Y direction), which returns the rods to their rest position within the slots.

### What is the user's physical interaction

The user does not interact with the slots. During assembly, the user threads each linkage rod through the slot from the interior side of the tray, passing the rod through the 5 mm wall thickness until it protrudes on the exterior. The 5.0 mm Z opening and 6.0 mm Y opening accept the 4 mm rod with visible clearance, requiring no force and no alignment difficulty. The rod simply passes through the rectangular hole.

---

## Constraint Chain Diagram

```
[User fingers on pull tabs] -> [Pull-tab paddles: translate +Y] -> [Linkage rods: rigid, translate +Y]
       -> [Through Sub-G slots: passive guide] -> [Release plate: translates +Y, releases collets]
              ^ Z constrained by: slot walls (5.0 mm opening vs 4 mm rod, 0.5 mm clearance/side)
              ^ Y constrained by: slot length (6.0 mm opening, 1.5 mm rod travel + 0.25 mm clearance/end)
              ^ X constrained by: rod endpoints (release plate interior, pull-tab exterior)
              ^ returned by: collet springs on release plate (push -Y)
```

---

## Feature Geometry

Sub-G consists of exactly two features: a left wall slot and a right wall slot. Both are identical rectangular through-cuts, mirrored about the tray centerline at X = 80 mm.

### Left Wall Slot

A rectangular through-cut removing material from X = 0 to X = 5 mm (the full 5 mm left wall thickness).

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Cut axis | X (through wall) | Wall runs in YZ plane |
| X range | 0.0 to 5.0 mm | Full left wall thickness |
| Y center | 20.0 mm | Forward of release plate front face (13.5 mm at rest), per spatial resolution |
| Z center | 37.5 mm | Release plate vertical center, per spatial resolution |
| Slot length (Y) | 6.0 mm | 4 mm rod + 1.5 mm travel + 0.5 mm clearance (0.25 mm each end) |
| Slot width (Z) | 5.0 mm | 4 mm rod + 1.0 mm clearance (0.5 mm each side) |
| Y range | 17.0 to 23.0 mm | Center 20.0 +/- 3.0 mm |
| Z range | 35.0 to 40.0 mm | Center 37.5 +/- 2.5 mm |
| Corner treatment | Sharp (no fillet) | FDM can produce sharp internal corners at this scale; rod is circular and does not contact corners |

### Right Wall Slot

Identical rectangular through-cut, mirrored to the right wall.

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Cut axis | X (through wall) | Wall runs in YZ plane |
| X range | 155.0 to 160.0 mm | Full right wall thickness |
| Y center | 20.0 mm | Mirrors left slot |
| Z center | 37.5 mm | Mirrors left slot |
| Slot length (Y) | 6.0 mm | Same as left slot |
| Slot width (Z) | 5.0 mm | Same as left slot |
| Y range | 17.0 to 23.0 mm | Mirrors left slot |
| Z range | 35.0 to 40.0 mm | Mirrors left slot |
| Corner treatment | Sharp | Same as left slot |

---

## Interface Specification

### Slot-to-Linkage-Rod Interface (both sides identical)

| Parameter | Slot (Sub-G) | Rod (part of release plate assembly) | Clearance | Source |
|-----------|-------------|--------------------------------------|-----------|--------|
| Z opening vs rod diameter | 5.0 mm | 4.0 mm | 0.5 mm per side (1.0 mm total) | Rod diameter from concept architecture; clearance from spatial resolution |
| Y opening vs rod diameter + travel | 6.0 mm | 4.0 mm dia + 1.5 mm travel = 5.5 mm swept | 0.25 mm per end (0.5 mm total) | Travel from concept (release plate 1.5 mm); clearance from spatial resolution |
| X depth (wall thickness) | 5.0 mm | Rod passes through | N/A (through-cut) | Sub-A wall thickness |

### Slot-to-Tray-Wall Interface (both sides)

The slots are subtractive features (boolean cuts) applied to the Sub-A box shell. No separate part exists. The slot boundaries are the wall material itself.

- **Left slot**: removes a 6.0 mm (Y) x 5.0 mm (Z) rectangular prism from the left wall, spanning the full wall thickness X = 0 to 5 mm, at Y = 17..23, Z = 35..40.
- **Right slot**: removes a 6.0 mm (Y) x 5.0 mm (Z) rectangular prism from the right wall, spanning X = 155 to 160 mm, at Y = 17..23, Z = 35..40.

No interface treatment (fillet, chamfer) is required. The cuts produce clean rectangular openings.

---

## Assembly Sequence

Sub-G is not a separate part. It is a pair of cuts applied to the tray during the CadQuery build sequence (Step 8 in the tray decomposition build order, after all unions are complete).

**During physical assembly of the cartridge:**

1. The tray (with slots already present from printing) is placed on the work surface.
2. The release plate is slid onto the guide posts (Sub-E) from the front.
3. Each linkage rod is threaded through its respective side wall slot from the interior, passing through the 5 mm wall thickness until it protrudes on the exterior. The rod enters the 6.0 x 5.0 mm opening easily -- no force required, no alignment jig needed.
4. The interior end of each rod hooks into the release plate's linkage attachment point.
5. The exterior end of each rod hooks into the pull-tab paddle inside the front bezel's finger channel.
6. The front bezel snaps onto the tray, capturing the pull-tab paddles and preventing the rods from withdrawing back through the slots.

**Disassembly (service):**

1. Pop the front bezel off (snap-fit, tool-free).
2. Unhook the rod exterior ends from the pull-tab paddles.
3. Slide each rod back through the slot toward the interior.
4. Unhook from the release plate.

---

## Manufacturing Notes

- **Print orientation**: The tray prints open-top-up. The slots are horizontal rectangular openings in vertical walls. They print as bridging spans across the 5.0 mm Z height of each slot. At 5.0 mm, this is well within typical FDM bridging capability (PETG bridges cleanly up to ~15 mm with proper cooling).
- **Minimum wall remaining**: The slot at Z = 35..40 mm leaves 35.0 mm of solid wall below the slot (Z = 0 to 35) and 32.0 mm above (Z = 40 to 72). No structural concern.
- **Accuracy**: The slot dimensions (6.0 x 5.0 mm) are generous relative to the 4 mm rod. FDM dimensional accuracy of +/- 0.2 mm on a 5 mm or 6 mm feature still leaves ample clearance (minimum 0.3 mm per side in Z, minimum 0.05 mm per end in Y, after worst-case shrinkage). No test print required for this feature.
- **No supports needed**: The slot is a simple rectangular through-cut. The top surface of the slot (Z = 40 mm) is a 5 mm bridge in the X direction (across the wall thickness), which prints cleanly without supports.

---

## Part Count

Sub-G adds zero parts. It is a pair of subtractive features (cuts) in the existing tray (Sub-A). The linkage rods that pass through the slots are part of the release plate assembly (Part 4 in the concept architecture), not part of Sub-G.
