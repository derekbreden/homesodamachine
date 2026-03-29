# Spatial Resolution: Lid

## 1. System-Level Placement

```
Mechanism: Lid (flat panel closing the tray top)
Parent: Tray assembly (sits on top edges of left wall, right wall, and rear wall)
Position: Lid bottom face rests on the Z = 72 plane of the tray
Orientation: level (no rotation). Lid X and Y axes align with tray X and Y axes.
```

The lid is a flat rectangular panel that closes the open top of the tray. It sits directly on the top edges of the three closed tray walls (left, right, rear). The lid is the last structural part installed before the bezel. It stiffens the tray into a torsion box and retains tubes.

---

## 2. Part Reference Frame

```
Part: Lid
  Origin: rear-left-bottom corner (looking from above, the corner nearest Y=0 and X=0)
  X: width, 0..160 mm (left to right when facing the front, same direction as tray X)
  Y: depth, 0..155 mm (0 = rear/dock side, 155 = front/user side, same direction as tray Y)
  Z: thickness, 0 = bottom face (contacts tray top edges), positive upward
  Print orientation: flat, bottom face (Z=0) on build plate, top face (Z=max) facing up
  Installed orientation: bottom face seats on tray Z=72 plane. No rotation.
```

The lid frame is offset from the tray frame by a pure Z translation: lid Z=0 corresponds to tray Z=72. The X and Y axes are identical in both frames.

---

## 3. Derived Geometry

### 3a. Lid Outer Envelope

The lid must span the full tray opening. The tray outer envelope is 160 mm (X) x 155 mm (Y). The lid sits on top of the side wall and rear wall top edges, covering the full tray footprint.

| Parameter | Value (lid frame) | Source |
|-----------|-------------------|--------|
| X extent | 0 to 160 mm | Matches tray outer width (Sub-A: X = 0..160) |
| Y extent | 0 to 155 mm | Matches tray outer depth (Sub-A: Y = 0..155) |
| Z extent (thickness) | 0 to 4 mm | Concept: ~4 mm flat panel |
| Bottom face | Z = 0 plane | Seats on tray top edges at tray Z = 72 |
| Top face | Z = 4 plane | Exposed surface (faces enclosure interior, never seen by user) |

### 3b. Tray Top Edge Bearing Surfaces (where the lid rests)

The lid's bottom face (Z = 0 in lid frame) rests on the top edges of the tray walls. These are the solid material strips at tray Z = 72:

| Bearing surface | Lid frame position | X range | Y range | Width (narrow dim) |
|-----------------|-------------------|---------|---------|-------------------|
| Left wall top edge | Z = 0 | 0 to 5 | 0 to 155 | 5 mm (X) |
| Right wall top edge | Z = 0 | 155 to 160 | 0 to 155 | 5 mm (X) |
| Rear wall top edge | Z = 0 | 0 to 160 | 0 to 8.5 | 8.5 mm (Y) |

The tray has no front wall -- the front is open at Y = 155. The lid's front edge (Y = 155) is unsupported by the tray until the bezel is installed. The bezel's top edge butts against or slightly overlaps the lid's front edge, providing the fourth-side constraint.

There is no top edge bearing strip along the floor (the floor is at tray Z = 3, far below the lid). The interior span of the lid (X = 5..155, Y = 8.5..155) is unsupported from below -- it bridges the open tray cavity. The 4 mm PETG panel thickness plus optional underside stiffening ribs provide adequate rigidity.

### 3c. Snap Tab Positions

The lid has 8 snap tabs (4 per long edge) that engage the tray's detent ridges (Sub-H). Each tab is a flexible cantilever extending downward from the lid's underside, near the left or right edge. The tabs hang below the lid's bottom face (into negative Z in lid frame).

The tray ridges are at Y = 20, 60, 100, 140 (center positions, tray frame = lid frame in Y). The lid tabs must align with these positions.

#### Tab Y positions (lid frame, same as tray frame)

| Tab ID | Side | Y center (mm) | Y extent (mm) |
|--------|------|---------------|---------------|
| LT1 | Left | 20 | 17 to 23 |
| LT2 | Left | 60 | 57 to 63 |
| LT3 | Left | 100 | 97 to 103 |
| LT4 | Left | 140 | 137 to 143 |
| RT1 | Right | 20 | 17 to 23 |
| RT2 | Right | 60 | 57 to 63 |
| RT3 | Right | 100 | 97 to 103 |
| RT4 | Right | 140 | 137 to 143 |

Tab Y extent: 6 mm each, matching the tray ridge extrusion length of 6 mm (Sub-H spatial 3f).

#### Tab X positions (lid frame)

The tabs hang from the lid's underside near the left and right edges. The tray interior wall faces are at X = 5 (left) and X = 155 (right) in the tray frame, which is the same in the lid frame. The tabs must reach inward from the lid edge to engage the ridges.

**Left-side tabs:**

| Parameter | Value (lid frame) |
|-----------|-------------------|
| Tab root (where tab joins lid body) | X = 5, Z = 0 (underside of lid, directly above left wall interior face) |
| Tab hangs downward | From Z = 0 into negative Z (below the lid) |
| Tab tip (hook face) X position when engaged | X = 5 to 7 mm (extends 2 mm inward from left wall interior face) |
| Tab tip (hook face) Z position when engaged | Z = -2.5 to -4.5 mm (tray frame: Z = 67.5 to 69.5) |

**Right-side tabs:**

| Parameter | Value (lid frame) |
|-----------|-------------------|
| Tab root (where tab joins lid body) | X = 155, Z = 0 (underside of lid, directly above right wall interior face) |
| Tab hangs downward | From Z = 0 into negative Z (below the lid) |
| Tab tip (hook face) X position when engaged | X = 153 to 155 mm (extends 2 mm inward from right wall interior face) |
| Tab tip (hook face) Z position when engaged | Z = -2.5 to -4.5 mm (tray frame: Z = 67.5 to 69.5) |

#### Tab engagement geometry -- interface with tray ridges

The tab hook engages behind the tray ridge's vertical catch face. All dimensions resolved in both frames:

| Parameter | Lid frame | Tray frame | Source |
|-----------|-----------|------------|--------|
| Ridge peak Z | Z = -1.5 | Z = 70.5 | Sub-H spatial 3e |
| Ridge catch face bottom Z | Z = -2.5 | Z = 69.5 | Sub-H spatial 3e |
| Ridge top (ramp start) Z | Z = -0.5 | Z = 71.5 | Sub-H spatial 3e |
| Ridge protrusion from left wall (peak X) | X = 6 | X = 6 | Sub-H spatial 3e |
| Ridge protrusion from right wall (peak X) | X = 154 | X = 154 | Sub-H spatial 3e |
| Tab hook Z range (engaged) | Z = -2.5 to -4.5 | Z = 67.5 to 69.5 | Sub-H spatial 3g |
| Tab deflection to clear ridge | 1.0 mm outward (away from tray center) | same | Sub-H spatial 3g |
| Retention depth (overlap behind catch face) | 1.0 mm | same | Sub-H spatial 3g |

The tab must be a cantilever beam of sufficient length to deflect 1.0 mm outward without yielding. The cantilever length (from root at Z = 0 to hook at approximately Z = -2.5) is at least 2.5 mm. The hook itself occupies Z = -2.5 to -4.5 (2.0 mm tall hook face). Total tab extent below the lid bottom face: 4.5 mm.

#### Tab cross-section profile (left-side tab, looking in +Y direction, lid frame)

```
  X (lid frame)
  ^
  |
7 -|    *---------*  hook tip, inward face
  |    |         |
  |    |  hook   |  (2 mm tall, from Z = -4.5 to -2.5)
  |    |         |
  |    *---------*  hook top (Z = -2.5, X = 5..7)
  |              |
  |    cantilever|  (2.5 mm tall, from Z = -2.5 to Z = 0)
  |    beam      |
5 -|              *  root (Z = 0, X = 5)
  |
  +--|----|----|----> Z (lid frame, negative = downward)
    -4.5 -2.5  0
```

The hook protrudes inward (toward X = 80, tray center) from the cantilever beam. The cantilever beam hangs from the lid underside at X = 5 (left wall interior face position).

For right-side tabs, mirror about X = 80: the cantilever root is at X = 155, and the hook extends from X = 155 to X = 153.

### 3d. Front Edge -- Bezel Interface

The lid's front edge is at Y = 155 (lid frame). This edge interfaces with the front bezel. The bezel is installed after the lid and its top edge meets the lid's front edge.

| Parameter | Value (lid frame) | Source |
|-----------|-------------------|--------|
| Lid front edge plane | Y = 155 | Matches tray front open face |
| Lid front edge X extent | 0 to 160 | Full lid width |
| Lid front edge Z extent | 0 to 4 | Full lid thickness |
| Bezel top edge contact zone | Y = 153.5 to 155, Z = 0 to 4 | Sub-I spatial 3b: bezel overlaps 1.5 mm behind Y = 155 |

The bezel's step-lap rabbet on the tray stops at Z = 72 (tray frame) = Z = 0 (lid frame). The bezel's top edge meets the lid's front edge at or just below this plane. The lid's front edge does not have a rabbet -- the bezel butts against the lid's front face.

#### Bezel tab pocket on lid front edge

Sub-I (bezel receiving spec) identifies pocket T1 at the top-center of the tray front edge: X = 77.5..82.5, Y = 152..155, Z = 70.5..72 (tray frame). This pocket is flagged as a design gap because no solid material exists at X = 77.5..82.5 between the side walls at the tray's top edge.

With the lid installed, the lid provides solid material at this location. The lid can host a pocket or recess on its front edge to receive the bezel's top snap tab.

**Bezel tab pocket on lid front edge (lid frame):**

| Parameter | Value (lid frame) | Tray frame equivalent |
|-----------|-------------------|-----------------------|
| Pocket center | (80, 153.5, 1.25) | (80, 153.5, 73.25) |
| Pocket cut volume | X = 77.5..82.5, Y = 152..155, Z = 0..2.5 | X = 77.5..82.5, Y = 152..155, Z = 72..74.5 |
| Pocket width (X) | 5 mm | -- |
| Pocket depth into lid (Y, from front edge) | 3 mm (Y = 152 to 155) | -- |
| Pocket height (Z, from lid bottom) | 2.5 mm | -- |
| Remaining lid thickness above pocket | 1.5 mm (4 - 2.5) | -- |

Note: The pocket is cut upward from the lid's bottom face at the front edge. The bezel's top tab hooks upward (+Z in lid frame) into this pocket. The 2.5 mm pocket height (rather than the 1.5 mm used for tray pockets) accounts for the tab approaching from below.

This pocket resolves the T1 design gap identified in Sub-I: the lid, not the tray, hosts the top bezel snap tab pocket.

### 3e. Rear Edge

The lid's rear edge is at Y = 0 (lid frame). It sits on the tray rear wall top edge (tray: Y = 0..8.5, Z = 72). The rear edge is a simple bearing surface with no snap tabs or pockets.

| Parameter | Value (lid frame) |
|-----------|-------------------|
| Rear edge plane | Y = 0 |
| Bearing surface below | X = 0..160, Y = 0..8.5, Z = 0 (rear wall top, 8.5 mm deep) |

The lid's rear edge is flush with the tray's rear exterior face (Y = 0). No overhang, no recess.

### 3f. Internal Corner Fillets

All internal corners on the lid's underside edges receive 1.0 mm fillets for printability and stress relief, matching the tray convention.

| Corner | Location (lid frame) | Run |
|--------|---------------------|-----|
| No internal corners on the lid body | -- | -- |

The lid is a flat rectangular plate. It has no internal corners (no pocket walls meeting). External edge fillets (if desired) are cosmetic and specified in the parts step, not here.

### 3g. Optional Stiffening Ribs (underside)

The lid decomposition document notes optional stiffening ribs on the underside. These are straight rectangular extrusions running in the X direction (spanning the lid width between the side wall bearing surfaces). Their spatial positions depend on structural analysis, but candidate locations are:

| Rib ID | Y position (lid frame) | X extent | Z extent (downward from Z=0) |
|--------|----------------------|----------|------------------------------|
| Rib 1 | Y = 40 | 5 to 155 | 0 to -3 (3 mm tall rib hanging below lid) |
| Rib 2 | Y = 80 | 5 to 155 | 0 to -3 |
| Rib 3 | Y = 120 | 5 to 155 | 0 to -3 |

These positions divide the 155 mm depth into roughly equal spans. The ribs must not interfere with the snap tab positions (tabs at Y = 17..23, 57..63, 97..103, 137..143). The candidate rib positions (Y = 40, 80, 120) fall in the gaps between tab Y extents. Rib depth (3 mm below lid) must clear the tray interior -- the interior pocket extends from tray Z = 3 to Z = 72, so a rib at tray Z = 72 extending down to tray Z = 69 is well above any interior component.

Rib inclusion is optional and decided during the parts specification step.

---

## 4. Interface Summary (all positions in both frames)

### Interface 1: Lid bottom face to tray top edges

| Parameter | Lid frame | Tray frame |
|-----------|-----------|------------|
| Contact plane | Z = 0 | Z = 72 |
| Left wall bearing | X = 0..5, Y = 0..155, Z = 0 | X = 0..5, Y = 0..155, Z = 72 |
| Right wall bearing | X = 155..160, Y = 0..155, Z = 0 | X = 155..160, Y = 0..155, Z = 72 |
| Rear wall bearing | X = 0..160, Y = 0..8.5, Z = 0 | X = 0..160, Y = 0..8.5, Z = 72 |
| Mating feature on tray | Sub-A top edges (Z = 72 plane) | -- |

### Interface 2: Lid snap tabs to tray detent ridges (Sub-H)

| Parameter | Lid frame | Tray frame |
|-----------|-----------|------------|
| Left tab hook engaged X range | 5 to 7 | 5 to 7 |
| Right tab hook engaged X range | 153 to 155 | 153 to 155 |
| Tab hook engaged Z range | -4.5 to -2.5 | 67.5 to 69.5 |
| Ridge catch face Z | -2.5 | 69.5 |
| Ridge peak Z | -1.5 | 70.5 |
| Ridge ramp top Z | -0.5 | 71.5 |
| Tab Y centers | 20, 60, 100, 140 | 20, 60, 100, 140 |
| Tab Y extent each | 6 mm (centered) | 6 mm (centered) |
| Required deflection | 1.0 mm outward | 1.0 mm outward |
| Retention depth | 1.0 mm | 1.0 mm |
| Mating feature on tray | Sub-H ridges: 8 triangular bumps on side wall interiors | -- |

### Interface 3: Lid front edge to bezel (top snap tab pocket)

| Parameter | Lid frame | Tray frame |
|-----------|-----------|------------|
| Pocket cut volume | X = 77.5..82.5, Y = 152..155, Z = 0..2.5 | X = 77.5..82.5, Y = 152..155, Z = 72..74.5 |
| Pocket opening face | Z = 0 plane at X = 77.5..82.5, Y = 152..155 | Z = 72 plane |
| Bezel tab approach | Tab enters from below (from -Z) and hooks upward into pocket | Tab enters from -Z (tray frame) and hooks upward |
| Mating feature on bezel | Bezel top-edge snap tab (T1) | -- |

### Interface 4: Lid front edge face to bezel top edge

| Parameter | Lid frame | Tray frame |
|-----------|-----------|------------|
| Lid front face plane | Y = 155 | Y = 155 |
| Contact zone | X = 0..160, Z = 0..4 | X = 0..160, Z = 72..76 |
| Bezel top edge abuts | From +Y direction against lid Y = 155 face | -- |
| Mating feature on bezel | Bezel top edge (cosmetic butt joint) | -- |

---

## 5. Transform Summary

```
Lid frame → Tray frame:
  No rotation.
  Translate: (0, 0, +72) in tray frame.

  lid_point_in_tray = (lid_X, lid_Y, lid_Z + 72)

Tray frame → Lid frame:
  No rotation.
  Translate: (0, 0, -72) from tray frame.

  tray_point_in_lid = (tray_X, tray_Y, tray_Z - 72)
```

### Verification (3 test points)

**Point 1: Lid origin (rear-left-bottom corner)**
- Lid frame: (0, 0, 0)
- Tray frame: (0, 0, 0 + 72) = (0, 0, 72) -- top of left wall at rear corner. Correct.

**Point 2: Lid front-right-top corner**
- Lid frame: (160, 155, 4)
- Tray frame: (160, 155, 4 + 72) = (160, 155, 76) -- front-right corner, 4 mm above tray top edge. Correct (lid top surface protrudes 4 mm above tray Z = 72).

**Point 3: Left tab LT2 hook engagement point (mid-hook)**
- Lid frame: (6, 60, -3.5)
- Tray frame: (6, 60, -3.5 + 72) = (6, 60, 68.5) -- 1 mm inside left wall interior face, at Y = 60, Z = 68.5 (within the Sub-H engagement zone of Z = 67.5..69.5). Correct.

**Point 4: Bezel pocket center**
- Lid frame: (80, 153.5, 1.25)
- Tray frame: (80, 153.5, 73.25) -- center of the bezel top pocket, 1.25 mm above the tray top edge. Correct (pocket is carved into lid body from its bottom face).

All four points are consistent. Transform verified.
