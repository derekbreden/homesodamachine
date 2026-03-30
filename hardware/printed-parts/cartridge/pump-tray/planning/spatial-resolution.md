# Pump Tray — Spatial Resolution

**Season 1, Phase 1, Item 2**
**Pipeline step:** 4s

---

## 1. System-Level Placement

**Mechanism:** Pump Tray
**Parent:** Cartridge interior
**Approximate position:** Bottom region of the cartridge interior, near the front. The pump bodies face forward — tube connectors protrude toward the cartridge front face, motor bodies protrude toward the cartridge back.

**The cartridge interior does not exist in Phase 1.** The side walls, rails, and enclosure bay are Season 2 work. This section is approximate context only, derived from vision.md:

- The pump cartridge sits at the front and bottom of the enclosure.
- The pump tray is one of two interior plates (the other being the coupler tray). In the assembled cartridge, the pump tray and coupler tray slide into protruding rails on the left and right side walls.
- The pumps mount to the front face of the tray; their motor bodies extend behind the tray toward the cartridge back.
- Exact position within the cartridge interior (distance from bottom, distance from front wall, rail slot height) is not resolvable until Season 2 wall geometry exists.

**This placement context is for orientation only. No downstream agent should derive a dimension from it.**

---

## 2. Part Reference Frame

The pump tray is modeled and printed in its own local frame, flat on the build plate.

```
Part: Pump Tray
  Origin: bottom-left corner of the front face
  X: width axis — runs left to right across both pump positions, 0..137.2mm
  Y: thickness axis — runs front to back through the plate, 0..3.0mm
      Y=0: front face (pump bracket face — the side the pump mounts to)
      Y=3.0: back face (the side the motor bodies protrude from)
  Z: height axis — runs bottom to top, 0..68.6mm
  Print orientation: front face (XZ plane, Y=0) down on the build plate
                     Z is up during printing
```

**Installed orientation vs. print orientation:** The part is printed flat with the front face down. When installed in the cartridge, the part is oriented so the front face faces forward (toward the cartridge front panel) and the Z axis runs vertically. The local frame is defined identically in both orientations — the part does not need to be reoriented in the local frame to describe the installed position.

No rotation transform is required. The part mounts flat: its XZ plane is parallel to the cartridge's front-to-back cross-section plane. The only transform from part frame to cartridge frame is a translation, addressed in Section 4.

---

## 3. Derived Geometry

### 3.1 Plate Envelope

All values in pump tray local frame.

| Dimension | Axis | Value | Description |
|-----------|------|-------|-------------|
| Width | X | 137.2mm | 0..137.2mm |
| Height | Z | 68.6mm | 0..68.6mm |
| Thickness | Y | 3.0mm | 0..3.0mm |

**Front face:** Y=0, spanning X=0..137.2mm, Z=0..68.6mm.
**Back face:** Y=3.0mm, spanning X=0..137.2mm, Z=0..68.6mm.

### 3.2 Hole Positions — Local Frame

Origin: bottom-left corner of front face (X=0, Y=0, Z=0).

All holes are through-holes: they enter at Y=0 (front face) and exit at Y=3.0mm (back face). Hole diameter: 3.3mm. Hole axis is parallel to the Y axis.

**Pump 1 center axis (in plate XZ plane): X=34.3mm, Z=34.3mm**

| Hole | X (mm) | Z (mm) | Y entry | Y exit | Diameter |
|------|--------|--------|---------|--------|----------|
| 1-A (top-left)     |  9.3 | 59.3 | Y=0 | Y=3.0mm | 3.3mm |
| 1-B (top-right)    | 59.3 | 59.3 | Y=0 | Y=3.0mm | 3.3mm |
| 1-C (bottom-right) | 59.3 |  9.3 | Y=0 | Y=3.0mm | 3.3mm |
| 1-D (bottom-left)  |  9.3 |  9.3 | Y=0 | Y=3.0mm | 3.3mm |

**Pump 2 center axis (in plate XZ plane): X=102.9mm, Z=34.3mm**

| Hole | X (mm) | Z (mm) | Y entry | Y exit | Diameter |
|------|--------|--------|---------|--------|----------|
| 2-A (top-left)     |  77.9 | 59.3 | Y=0 | Y=3.0mm | 3.3mm |
| 2-B (top-right)    | 127.9 | 59.3 | Y=0 | Y=3.0mm | 3.3mm |
| 2-C (bottom-right) | 127.9 |  9.3 | Y=0 | Y=3.0mm | 3.3mm |
| 2-D (bottom-left)  |  77.9 |  9.3 | Y=0 | Y=3.0mm | 3.3mm |

**Derivation check:** Each 4-hole set forms a 50mm × 50mm square (c-c). From pump center to nearest hole: 25mm in X, 25mm in Z.
- Pump 1 holes: X = 34.3 ± 25mm → {9.3, 59.3}. Z = 34.3 ± 25mm → {9.3, 59.3}. ✓
- Pump 2 holes: X = 102.9 ± 25mm → {77.9, 127.9}. Z = 34.3 ± 25mm → {9.3, 59.3}. ✓

**Edge clearance check (in local frame):**
- Outermost holes from plate edges: X=9.3mm from left edge; X=127.9mm → 137.2-127.9=9.3mm from right edge. Z=9.3mm from bottom edge; Z=59.3mm → 68.6-59.3=9.3mm from top edge.
- 9.3mm edge-to-center clearance on all four sides. Minimum required for M3: ~4mm. ✓

### 3.3 Motor Bore Positions — Local Frame

2 motor bores, one per pump. Each bore is a through-hole parallel to the Y axis: enters at Y=0 (front face), exits at Y=3.0mm (back face). Bore diameter: 37mm (motor cylinder is 35.73mm per caliper photo 16; bore per vision.md Section 4 Season 1 Phase 1 Item 2).

| Bore | Center X (mm) | Center Z (mm) | Diameter | Y entry | Y exit |
|------|--------------|--------------|----------|---------|--------|
| Bore 1 (Pump 1 motor axis) | 34.3 | 34.3 | 37mm | Y=0 | Y=3.0mm |
| Bore 2 (Pump 2 motor axis) | 102.9 | 34.3 | 37mm | Y=0 | Y=3.0mm |

**Bore radius:** 18.5mm.

**Clearance verification — bore edge to screw hole centers:**

Distance formula: sqrt((bore_X - hole_X)² + (bore_Z - hole_Z)²). Clearance = distance − 18.5mm.

Bore 1 center (34.3, 34.3) to Pump 1 screw holes:

| Hole | Hole (X, Z) | Distance | Clearance |
|------|------------|----------|-----------|
| 1-A | (9.3, 59.3) | sqrt(25² + 25²) = sqrt(1250) = 35.36mm | 35.36 − 18.5 = 16.86mm ✓ |
| 1-B | (59.3, 59.3) | sqrt(25² + 25²) = 35.36mm | 16.86mm ✓ |
| 1-C | (59.3, 9.3) | sqrt(25² + 25²) = 35.36mm | 16.86mm ✓ |
| 1-D | (9.3, 9.3) | sqrt(25² + 25²) = 35.36mm | 16.86mm ✓ |

Bore 2 center (102.9, 34.3) to Pump 2 screw holes:

| Hole | Hole (X, Z) | Distance | Clearance |
|------|------------|----------|-----------|
| 2-A | (77.9, 59.3) | sqrt(25² + 25²) = 35.36mm | 16.86mm ✓ |
| 2-B | (127.9, 59.3) | sqrt(25² + 25²) = 35.36mm | 16.86mm ✓ |
| 2-C | (127.9, 9.3) | sqrt(25² + 25²) = 35.36mm | 16.86mm ✓ |
| 2-D | (77.9, 9.3) | sqrt(25² + 25²) = 35.36mm | 16.86mm ✓ |

All bore-to-hole clearances are 16.86mm. The bore edge does not reach any screw hole.

**Plate edge clearance verification:**

- Bore 1 extends X = 34.3 ± 18.5mm → X=15.8..52.8mm. Plate spans X=0..137.2mm. Bore stays within plate. ✓
- Bore 1 extends Z = 34.3 ± 18.5mm → Z=15.8..52.8mm. Plate spans Z=0..68.6mm. Bore stays within plate. ✓
- Bore 2 extends X = 102.9 ± 18.5mm → X=84.4..121.4mm. Plate spans X=0..137.2mm. Bore stays within plate. ✓
- Bore 2 extends Z = 34.3 ± 18.5mm → Z=15.8..52.8mm. Same as Bore 1 in Z. ✓

### 3.4 Interface: Pump Bracket Mates to Plate Front Face

**From the plate side (local frame):**

Each pump mounts via its metal mounting bracket. The bracket bears flat against the front face of the plate (Y=0). The bracket face is centered on the pump center axis.

| Property | Pump 1 | Pump 2 |
|----------|--------|--------|
| Bracket center (X, Z) | X=34.3mm, Z=34.3mm | X=102.9mm, Z=34.3mm |
| Bracket footprint (X extent) | X=0..68.6mm | X=68.6..137.2mm |
| Bracket footprint (Z extent) | Z=0..68.6mm | Z=0..68.6mm |
| Contact face | Y=0 | Y=0 |
| Bracket width | 68.6mm in X | 68.6mm in X |
| Bracket height | 68.6mm in Z | 68.6mm in Z |
| Bracket thickness | ~1.5mm (in Y, behind Y=0) | ~1.5mm (in Y, behind Y=0) |

The bracket is a metal plate; its rear face sits at approximately Y=-1.5mm in the local frame (it sits in front of the tray front face). The bracket itself is not a feature of the printed part — it is an off-the-shelf component. This interface describes the contact condition only.

**4 M3 screw axes per pump (from pump bracket side toward plate):**
Screws originate from behind the bracket (motor side, Y < 0), pass through the bracket, and thread into the pump head. From the plate's perspective: M3 screws pass through the plate holes (Y=0 to Y=3.0mm) and engage threads in the pump head on the far side (Y < 0). Screw axes are parallel to Y.

**From the pump bracket side:**
- Bracket presents 4× M3 clearance holes, 50mm × 50mm c-c pattern, centered on the pump motor axis.
- Pump 1 motor axis at (X=34.3mm, Z=34.3mm) in plate frame.
- Pump 2 motor axis at (X=102.9mm, Z=34.3mm) in plate frame.
- Bracket flat face contacts plate at Y=0.

### 3.5 Interface: Cartridge Interior Rails

**Not resolvable in Phase 1.**

The side wall rails that the pump tray slides into are Season 2 geometry. The rail interface positions on the pump tray (edge features or slot features on the X=0 and X=137.2mm plate edges) are not designed yet and cannot be located in the local frame at this time.

**What is known in the local frame:**
- The plate edges that will receive rail features: X=0 (left edge), X=137.2mm (right edge), spanning Z=0..68.6mm.
- No edge features exist on these surfaces in Phase 1. The edges are plain cut surfaces.

This interface will be specified in Season 2 when the side wall geometry is defined. The pump tray will be updated at that time (vision.md, Phase 9, item 29).

---

## 4. Transform Summary

The pump tray mounts flat — no rotation. The transform from part local frame to cartridge frame is a pure translation.

```
Part frame → Cartridge frame:
  Rotation: none (identity)
  Translation: (Tx, Ty, Tz) — unknown in Phase 1 (cartridge interior not designed)

  Part-local X maps to cartridge X (width, left-right)
  Part-local Y maps to cartridge Y (depth, front-back)
  Part-local Z maps to cartridge Z (height, up-down)
```

**Verification using known geometry (once cartridge position is determined):**

Let (Tx, Ty, Tz) be the cartridge-frame position of the part-local origin (bottom-left corner of front face). Then:

| Part-local point | Part-local coords | Cartridge frame |
|-----------------|-------------------|-----------------|
| Origin (bottom-left-front) | (0, 0, 0) | (Tx, Ty, Tz) |
| Top-right-front corner | (137.2, 0, 68.6) | (Tx+137.2, Ty, Tz+68.6) |
| Pump 1 center axis (front face) | (34.3, 0, 34.3) | (Tx+34.3, Ty, Tz+34.3) |

These three test points confirm the transform is a pure translation with no rotation component. When cartridge rail positions are defined in Season 2, Tx, Ty, Tz will be filled in from the wall geometry and these test points can be verified numerically.

**Confirmation that no hidden rotation exists:**
- The plate is flat. It does not mount at an angle.
- Vision.md describes the pump cartridge as sitting at the front and bottom of the device, with pumps facing forward. "Forward" in the cartridge is +Y in the local frame. This is consistent with the part axis convention.
- No transforms beyond translation are needed at any phase.

---

## 5. No Physics-Dependent Profiles

This part has no cross-sectional profiles that depend on physics (gravity, fluid, material drape). It is a rigid flat plate. No profile tables are needed.

---

## Quality Gate Verification

1. **Every number is in a named reference frame.** All coordinates above are explicitly in the pump tray local frame. The one unknown (cartridge translation offset) is named as unknown with a placeholder. ✓

2. **No downstream derivation required.** Every hole position is given as a concrete (X, Z, Y-entry, Y-exit) coordinate set. Hole diameter is stated. Plate envelope is stated. No trigonometry or frame conversion is needed to extract a dimension. ✓

3. **No cross-sectional profiles apply.** This is a flat plate. ✓

4. **Interfaces specified from both sides.**
   - Pump bracket / plate front face: described from the plate side (contact face Y=0, bracket footprint, hole positions) and from the pump bracket side (bracket presents 50mm c-c pattern, motor axis position). ✓
   - Motor bore: described from the plate side (bore diameter 37mm, center positions, Y entry/exit) and from the pump side (motor cylinder 35.73mm diameter must pass through; screws approach from motor side and require bore clearance). Clearance computed and verified. ✓
   - Cartridge rail interface: described as not resolvable in Phase 1; known edge locations stated. ✓

5. **Transform summary is self-consistent.** Three test points stated above map correctly under a pure translation. Identity rotation confirmed. ✓
