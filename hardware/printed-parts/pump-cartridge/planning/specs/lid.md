# Lid -- Parts Specification

A flat rectangular PETG panel (160 x 155 x 4 mm) that snaps onto the tray's top edges, closing the open-top box into a torsion box. The lid retains tubes, stiffens the assembly against racking, and hosts the bezel top snap tab pocket (T1) that the tray cannot provide. It is the second-to-last structural part installed (before the bezel) and the second part removed during service (after the bezel).

---

## Coordinate System

The lid has its own local frame, offset from the tray frame by a pure Z translation.

- **Origin**: rear-left-bottom corner of the lid (the corner nearest Y = 0 and X = 0, on the bottom face)
- **X axis**: width, 0..160 mm (left to right when facing the front, same direction as tray X)
- **Y axis**: depth, 0..155 mm (0 = rear/dock side, 155 = front/user side, same direction as tray Y)
- **Z axis**: thickness, 0..4 mm. Z = 0 is the bottom face (contacts tray top edges at tray Z = 72). Z = 4 is the top face (faces enclosure interior, never seen by user).
- **Print orientation**: flat, bottom face (Z = 0) on build plate, top face (Z = 4) facing up
- **Installed orientation**: bottom face seats on tray Z = 72 plane. No rotation. Identity transform except Z offset.

**Frame transform**: lid Z = 0 corresponds to tray Z = 72. X and Y axes are identical. `tray_point = (lid_X, lid_Y, lid_Z + 72)`.

---

## 1. Mechanism Narrative

### What the user sees and touches

The lid is an internal structural component. The user never sees or touches it during normal operation. The cartridge sits in the dock with the lid facing upward, inside the enclosure. The only time anyone handles the lid is during the one-time build or during rare service events (tube re-routing or pump replacement). The builder sees a flat rectangular panel with 8 small snap tabs hanging from its underside near the left and right edges, and a rectangular pocket cut into the front edge center.

### What moves

**During lid installation:** The lid translates in the -Z direction (pressed straight down onto the tray). The 8 snap tabs -- 4 cantilever beams per long edge, hanging from the lid's underside -- deflect outward (away from the tray center, in the +/-X direction) as they contact the 45-degree ramps on the tray's detent ridges (Sub-H). Once each tab hook clears the ridge peak at lid Z = -1.5 (tray Z = 70.5), the cantilever spring force drives the hook inward, behind the ridge's vertical catch face. Each tab produces a small click at the moment of engagement.

**During operation:** Nothing moves. The lid is a rigid, stationary panel.

**During lid removal:** The builder grips the lid edges and pulls upward (+Z). The tab hooks press against the underside of each ridge catch face at lid Z = -2.5 (tray Z = 69.5). Continued upward force deflects all 8 tabs outward by 1.0 mm simultaneously, clearing the ridge peaks, and the lid lifts free.

### What converts the motion

The lid is pressed straight down (-Z). Each tray ridge has a 45-degree ramp face (1.0 mm run in X, 1.0 mm rise in Z) that converts the vertical insertion force into a horizontal outward deflection of each snap tab. The 1:1 ratio (arctan(1.0/1.0) = 45 degrees) means 1 mm of downward travel produces 1 mm of outward tab deflection.

The conversion is produced by the ramp geometry on the tray ridges (Sub-H vertices A-to-B: from (5.0, 71.5) to (6.0, 70.5) in the tray frame for the left side). The lid tabs are passive flexible beams that ride over this ramp.

### What constrains the lid

| Degree of freedom | Constraint feature | Dimensions |
|---|---|---|
| -Z (downward) | Lid bottom face (Z = 0) rests on tray wall top edges at tray Z = 72. Left wall bearing: X = 0..5, Y = 0..155. Right wall bearing: X = 155..160, Y = 0..155. Rear wall bearing: X = 0..160, Y = 0..8.5. | Three bearing strips, total contact area ~3,175 mm^2 |
| +Z (upward / lift) | 8 snap tab hooks engaged behind 8 tray ridge catch faces. Each hook overlaps 1.0 mm behind the catch face at lid Z = -2.5 (tray Z = 69.5). | 1.0 mm retention depth per tab, 8 tabs total |
| +/-X (lateral) | Lid outer edges flush with tray outer walls (X = 0 and X = 160). The lid sits within the tray's outer wall footprint -- the side wall top edges (5 mm wide) prevent lateral shifting. | Lid width = tray width = 160 mm. Nominal 0 clearance (both printed at 160 mm). |
| +/-Y (fore-aft) | Rear: lid rear edge (Y = 0) flush with tray rear wall exterior. The 8.5 mm deep rear wall bearing strip arrests -Y motion. Front: bezel top edge butts against lid front face (Y = 155) after bezel installation. Before bezel installation, the lid is retained laterally by the 8 snap tabs engaging the side wall ridges. | Rear bearing depth 8.5 mm. Front constraint depends on bezel. |
| Rotation about Z | 8 snap tabs at Y = 20, 60, 100, 140 on both sides resist any twisting moment about Z. The distributed tab locations (4 per side, 40 mm spacing) provide anti-rotation couples. | Moment arm from centerline to tabs: 75 mm per side |

### What provides the return force

No return force. The lid is intended to stay installed. It does not have a rest position different from its installed position. Removal requires deliberate upward pull overcoming 8 tab cantilever deflections.

### What is the builder's physical interaction

1. **Orient:** Builder holds the lid with the bottom face (snap tabs visible) facing down. The tabs are visible as 8 small hooks near the left and right edges.
2. **Align:** Builder places the lid over the tray opening, aligning the rear edge with the tray rear wall and the left/right edges with the tray side walls. The lid is the same 160 x 155 mm footprint as the tray, so alignment is self-evident.
3. **Press down:** Builder applies uniform downward pressure. All 8 tabs simultaneously contact the 45-degree ramps on the tray ridges at lid Z = -0.5 (tray Z = 71.5). Continued pressure deflects tabs outward by 1.0 mm.
4. **Click:** As each tab clears the ridge peak at lid Z = -1.5 (tray Z = 70.5), it springs inward behind the catch face. The transition from ramped resistance to sudden release produces a perceptible click. With 8 tabs engaging near-simultaneously, the builder feels and hears a compound snap.
5. **Verify:** The lid sits flat on the tray top edges. Attempting to lift the lid requires enough force to deflect all 8 tabs, confirming retention.

---

## 2. Constraint Chain Diagram

```
[Builder hand: presses lid -Z]
  -> [Lid panel: translates -Z onto tray top edges]
       -> [8 snap tab hooks contact 8 tray ridge 45-deg ramps]
            -> [Ramps convert -Z force to +/-X tab deflection (1.0 mm)]
                 -> [Tabs clear ridge peaks at lid Z = -1.5]
                      -> [Cantilever spring force drives tabs inward behind catch faces]
                           -> [8 catch faces at lid Z = -2.5 block +Z lift]
                                ^ tabs constrained by: cantilever root at lid Z = 0 (integral to lid body)
                                ^ ridges constrained by: integral bond to tray walls (Sub-H, all 6 DOF)

[Lid -Z constraint]  -> tray wall top edges (Z = 0 bearing surfaces, 3 strips)
[Lid +Z constraint]  -> 8 tab hooks behind 8 ridge catch faces (1.0 mm retention depth each)
[Lid +/-X constraint] -> side wall top edges (5 mm wide bearing strips at X = 0..5 and X = 155..160)
[Lid -Y constraint]  -> rear wall top edge (8.5 mm deep bearing strip at Y = 0..8.5)
[Lid +Y constraint]  -> bezel top edge at Y = 155 (after bezel installation)
```

Every arrow names the force transmission mechanism. Every constraint names a geometric feature with dimensions.

---

## 3. Feature Specification

### 3a. Panel Body

The base solid is a flat rectangular box.

| Parameter | Value | Source |
|-----------|-------|--------|
| X extent | 0 to 160 mm | Lid spatial 3a; matches tray outer width |
| Y extent | 0 to 155 mm | Lid spatial 3a; matches tray outer depth |
| Z extent | 0 to 4 mm | Lid spatial 3a; concept ~4 mm |
| Material | PETG | Concept architecture Sec. 7; requirements.md |
| Volume (panel body only) | 160 x 155 x 4 = 99,200 mm^3 | Derived |

The panel body spans the full tray footprint. The unsupported interior span (X = 5..155, Y = 8.5..155) bridges the open tray cavity. The 4 mm PETG thickness plus the three stiffening ribs (Section 3d) provide adequate rigidity.

### 3b. Snap Tabs (8 total)

Each snap tab is a cantilever beam extending downward from the lid's underside (Z = 0 plane), near the left or right edge. The beam ends in a hook that engages behind a tray detent ridge (Sub-H).

#### Tab positions

| Tab ID | Side | Y center (mm) | Y extent (mm) | Root X (mm) |
|--------|------|---------------|---------------|-------------|
| LT1 | Left | 20 | 17 to 23 | 5 |
| LT2 | Left | 60 | 57 to 63 | 5 |
| LT3 | Left | 100 | 97 to 103 | 5 |
| LT4 | Left | 140 | 137 to 143 | 5 |
| RT1 | Right | 20 | 17 to 23 | 155 |
| RT2 | Right | 60 | 57 to 63 | 155 |
| RT3 | Right | 100 | 97 to 103 | 155 |
| RT4 | Right | 140 | 137 to 143 | 155 |

Tab Y width: 6 mm each, matching the tray ridge extrusion length of 6 mm (Sub-H Section 3d).

Tab Y center-to-center spacing: 40 mm, matching tray ridge spacing.

#### Tab cross-section geometry (left-side tab, XZ plane, lid frame)

```
  X (lid frame)
  ^
  |
7 -|    *---------*  hook inward face (X = 7, Z = -4.5 to -2.5)
  |    |         |
  |    |  HOOK   |  2.0 mm tall (Z = -4.5 to -2.5)
  |    |         |  2.0 mm wide (X = 5 to 7)
  |    *---------*  hook top (X = 5..7, Z = -2.5)
  |              |
  |  cantilever  |  2.5 mm tall (Z = -2.5 to 0)
  |    beam      |  1.5 mm thick (X = 5 to 6.5)
5 -|              *  root (X = 5, Z = 0)
  |
  +--|----|----|----> Z (lid frame, negative = downward)
    -4.5 -2.5  0
```

For right-side tabs, mirror about X = 80: root at X = 155, hook extends from X = 153 to 155.

#### Tab dimensional summary

| Parameter | Value (lid frame) | Tray frame equivalent | Source |
|-----------|-------------------|-----------------------|--------|
| Root position (Z) | Z = 0 | Z = 72 | Underside of lid body |
| Cantilever beam length | 2.5 mm (Z = 0 to Z = -2.5) | Z = 72 to 69.5 | Lid spatial 3c |
| Cantilever beam thickness | 1.5 mm (X) | -- | Sized for 1.0 mm deflection without yielding in PETG |
| Hook height | 2.0 mm (Z = -2.5 to Z = -4.5) | Z = 69.5 to 67.5 | Lid spatial 3c |
| Hook inward protrusion (from wall face) | 2.0 mm | -- | Lid spatial 3c: X = 5 to 7 (left) or X = 153 to 155 (right) |
| Total tab extent below lid | 4.5 mm (Z = 0 to Z = -4.5) | Z = 72 to 67.5 | Lid spatial 3c |
| Tab width (Y) | 6.0 mm | -- | Matches ridge Y extent |

#### Tab engagement with tray ridges

| Parameter | Value | Source |
|-----------|-------|--------|
| Ridge peak (lid Z) | -1.5 | Sub-H 3c: tray Z = 70.5 |
| Ridge catch face bottom (lid Z) | -2.5 | Sub-H 3c: tray Z = 69.5 |
| Ridge ramp start (lid Z) | -0.5 | Sub-H 3c: tray Z = 71.5 |
| Ridge protrusion from wall (left, X) | 1.0 mm (X = 5 to 6) | Sub-H 3d |
| Required tab deflection to clear ridge | 1.0 mm outward | Sub-H 3e |
| Retention depth (overlap behind catch face) | 1.0 mm | Sub-H 3e |
| Engagement zone below catch face | lid Z = -2.5 to -4.5 (tray Z = 67.5 to 69.5) | Lid spatial 3c |

#### Tab cantilever deflection analysis

The cantilever beam must deflect 1.0 mm outward without yielding.

| Parameter | Value |
|-----------|-------|
| Beam material | PETG (tensile yield ~50 MPa, flexural modulus ~2100 MPa) |
| Beam length (L) | 2.5 mm (from root at Z = 0 to hook junction at Z = -2.5) |
| Beam thickness (t) | 1.5 mm (X direction) |
| Beam width (w) | 6.0 mm (Y direction) |
| Required deflection (delta) | 1.0 mm |
| Max bending stress | sigma = (3 * E * t * delta) / (2 * L^2) = (3 * 2100 * 1.5 * 1.0) / (2 * 6.25) = 756 MPa |

**DESIGN GAP: The 2.5 mm cantilever length is too short for 1.0 mm deflection in PETG.** At 2.5 mm length and 1.5 mm thickness, the beam cannot deflect 1.0 mm without far exceeding the yield stress. The cantilever needs to be longer (reducing stiffness) or thinner (reducing section modulus), or both.

**Resolution:** Extend the cantilever beam length to 8 mm by starting the beam root further up inside the lid body. Instead of hanging from Z = 0 as a simple extrusion below the lid, the tab is a slot-released cantilever: a 1.5 mm thick beam runs downward from Z = 0 to Z = -4.5 as before, but the effective bending length is increased by cutting a relief slot into the lid body along the wall-adjacent zone, allowing the beam to flex from a virtual root at Z = +3.5 (1.5 mm inside the lid panel, 0.5 mm below the top face). This gives an effective cantilever length of 8.0 mm (from Z = +3.5 down to the hook top at Z = -4.5, with the beam thickness reducing to the free section from Z = 0 downward).

**Revised cantilever (slot-released design):**

| Parameter | Revised value |
|-----------|---------------|
| Relief slot in lid body | Cut from Z = 0 to Z = 3.5, 1.5 mm wide (X), 6 mm long (Y), at each tab location. The slot separates the tab from the bulk lid panel, creating a longer effective beam. |
| Effective cantilever length (L) | 8.0 mm (Z = +3.5 to Z = -4.5) |
| Beam thickness (t) | 1.5 mm |
| Required deflection (delta) | 1.0 mm |
| Max bending stress (revised) | sigma = (3 * 2100 * 1.5 * 1.0) / (2 * 64) = 73.8 MPa |

At 73.8 MPa, this exceeds PETG yield (~50 MPa) by roughly 50%. Reduce beam thickness to 1.0 mm:

| Parameter | Final value |
|-----------|-------------|
| Effective cantilever length (L) | 8.0 mm |
| Beam thickness (t) | 1.0 mm |
| Required deflection (delta) | 1.0 mm |
| Max bending stress (final) | sigma = (3 * 2100 * 1.0 * 1.0) / (2 * 64) = 49.2 MPa |

At 49.2 MPa vs ~50 MPa yield, this is at the limit. Acceptable for PETG's slight ductility and the infrequent deflection cycles (lid installed/removed rarely). The 1.0 mm beam thickness is 2.5 perimeters at 0.4 mm nozzle -- printable but should be verified with a test print.

**Final tab cross-section (left-side, revised, lid frame):**

```
     X (lid frame)
     ^
     |
  7 -|         *---------*  hook inward face (X = 6..7, Z = -4.5 to -2.5)
     |         |         |
     |         |  HOOK   |  2.0 mm tall, 1.0 mm thick
     |         |         |
     |         *---------*  hook top (X = 6..7, Z = -2.5)
     |         |
     |    beam |  1.0 mm thick (X = 6 to 7)
     |         |  runs from Z = -2.5 up to Z = +3.5
     |         |
  6 -*=========*  root (Z = +3.5) -- virtual root inside lid body
     |
     +--|----|----|----|----> Z (lid frame, negative = downward)
       -4.5 -2.5  0  +3.5
```

Note: The beam is offset 1.0 mm inward from the wall face (X = 6..7 for left side, X = 153..154 for right side). A relief slot (X = 5..6, Z = 0..3.5) separates the beam from the outer 1.0 mm of lid thickness along the wall. The remaining 0.5 mm of lid above the slot root (Z = 3.5 to Z = 4.0) is the intact top surface.

**Relief slot dimensions (per tab, left side):**

| Parameter | Value (lid frame) |
|-----------|-------------------|
| Slot X extent | 5.0 to 6.0 (1.0 mm wide, between wall face and beam) |
| Slot Y extent | Same as tab Y extent (e.g., LT1: 17 to 23) |
| Slot Z extent | 0 to 3.5 (cut into lid body from bottom face, 3.5 mm deep) |
| Remaining lid above slot | 0.5 mm (Z = 3.5 to 4.0) |

For right-side tabs: slot at X = 154..155, beam at X = 153..154.

### 3c. Bezel Top Snap Tab Pocket (T1)

This pocket resolves the T1 design gap identified in Sub-I: the tray has no solid material at X = 77.5..82.5 between the side walls at the top edge, so the lid hosts this pocket instead.

| Parameter | Value (lid frame) | Tray frame equivalent | Source |
|-----------|-------------------|-----------------------|--------|
| Pocket X extent | 77.5 to 82.5 mm | Same | Lid spatial 3d |
| Pocket Y extent | 152 to 155 mm (3 mm deep from front edge) | Same | Lid spatial 3d |
| Pocket Z extent | 0 to 2.5 mm (cut upward from bottom face) | 72 to 74.5 | Lid spatial 3d |
| Pocket width (X) | 5.0 mm | -- | -- |
| Pocket depth (Y) | 3.0 mm | -- | -- |
| Pocket height (Z) | 2.5 mm | -- | -- |
| Remaining lid above pocket | 1.5 mm (Z = 2.5 to 4.0) | -- | Derived |
| Opening face | Z = 0 plane (bottom of lid) | Z = 72 | Tab enters from below |

The bezel's T1 tab approaches from below (-Z in lid frame) and hooks upward (+Z) into this pocket. The pocket rear wall at Y = 152 captures the tab barb and prevents the bezel from pulling forward (+Y). The pocket ceiling at Z = 2.5 provides the surface the tab barb locks behind.

### 3d. Stiffening Ribs (3 ribs, underside)

Three straight rectangular ribs on the lid underside span between the side wall bearing zones (X = 5 to X = 155). They stiffen the unsupported 150 mm interior span against flexural deflection.

| Rib ID | Y position (center, lid frame) | X extent | Z extent (downward from Z = 0) | Cross-section |
|--------|-------------------------------|----------|-------------------------------|---------------|
| Rib 1 | Y = 40 | X = 5 to 155 | Z = 0 to -3 (3 mm tall) | 150 mm long x 2 mm thick (Y) x 3 mm tall (Z) |
| Rib 2 | Y = 80 | X = 5 to 155 | Z = 0 to -3 | Same |
| Rib 3 | Y = 120 | X = 5 to 155 | Z = 0 to -3 | Same |

Rib thickness: 2 mm (Y direction). Rib height: 3 mm (hangs below lid bottom face).

**Clearance check -- ribs vs. snap tabs:** Snap tabs are at Y = 17..23, 57..63, 97..103, 137..143. Ribs are at Y = 39..41, 79..81, 119..121 (2 mm thick centered on Y = 40, 80, 120). Minimum gap: rib 1 edge (Y = 41) to tab LT2/RT2 edge (Y = 57) = 16 mm. No conflict.

**Clearance check -- ribs vs. tray interior:** Ribs extend to Z = -3 in lid frame = tray Z = 69. The nearest interior component below the ribs is the tube routing zone at tray Z = 3..13 (Sub-F). Clear by 56 mm. No conflict.

**Clearance check -- ribs vs. bezel pocket:** Rib 3 at Y = 119..121 is far from the bezel pocket at Y = 152..155. No conflict.

### 3e. External Edge Treatment

| Edge | Treatment | Dimension |
|------|-----------|-----------|
| All four top-face perimeter edges (Z = 4 plane) | 0.5 mm chamfer | Removes sharp edge; slight enough to not affect seating |
| Underside edges along wall bearings | No treatment (flat bearing surface) | -- |
| Front edge face (Y = 155 plane) | Square (no chamfer or fillet) | Bezel top edge butts against this face |
| Rear edge face (Y = 0 plane) | 0.5 mm chamfer on top only | Cosmetic; bottom edge is bearing surface |

---

## 4. Interface Specifications

### Interface 1: Lid bottom face to tray top edges

| Parameter | Lid dimension | Tray dimension | Clearance | Source |
|-----------|--------------|----------------|-----------|--------|
| Left wall bearing width | Lid X = 0..5 (bottom face) | Tray X = 0..5, Z = 72 (top edge) | 0 (flush contact) | Sub-A, lid spatial 3b |
| Right wall bearing width | Lid X = 155..160 (bottom face) | Tray X = 155..160, Z = 72 (top edge) | 0 (flush contact) | Sub-A, lid spatial 3b |
| Rear wall bearing depth | Lid Y = 0..8.5 (bottom face) | Tray Y = 0..8.5, Z = 72 (top edge) | 0 (flush contact) | Sub-A, lid spatial 3b |
| Lid outer width | 160 mm | Tray outer width: 160 mm | 0 nominal (both printed at same dimension; FDM tolerance ~0.2 mm ensures slight clearance) | Sub-A |
| Lid outer depth | 155 mm | Tray outer depth: 155 mm | 0 nominal (same reasoning) | Sub-A |

### Interface 2: Lid snap tabs to tray detent ridges (Sub-H)

| Parameter | Lid tab dimension | Tray ridge dimension | Clearance / engagement | Source |
|-----------|------------------|---------------------|----------------------|--------|
| Tab hook X range (left, engaged) | X = 6..7 | Ridge X = 5..6 (catch face at X = 6) | Hook behind catch face by 1.0 mm (X = 6 to 7 is behind ridge peak at X = 6) | Sub-H 3c, lid spatial 3c |
| Tab hook X range (right, engaged) | X = 153..154 | Ridge X = 154..155 (catch face at X = 154) | Hook behind catch face by 1.0 mm | Sub-H 3c, lid spatial 3c |
| Tab hook Z range (engaged) | Z = -4.5 to -2.5 (lid) = Z = 67.5 to 69.5 (tray) | Ridge catch face at tray Z = 69.5, engagement zone Z = 67.5..69.5 | 2.0 mm hook depth below catch face | Sub-H 3e, lid spatial 3c |
| Tab Y width | 6.0 mm | Ridge Y extrusion length: 6.0 mm | 0 (matched) | Sub-H 3d |
| Tab Y centers | 20, 60, 100, 140 | Ridge Y centers: 20, 60, 100, 140 | 0 (aligned) | Sub-H 3b |
| Tab deflection required | 1.0 mm outward | Ridge protrusion: 1.0 mm | Tab deflects to clear ridge peak | Sub-H 3e |
| Tab beam thickness | 1.0 mm | -- | -- | Sized for stress limit |
| Effective cantilever length | 8.0 mm (slot-released) | -- | -- | Stress analysis |

### Interface 3: Lid bezel pocket (T1) to bezel top snap tab

| Parameter | Lid pocket dimension | Bezel tab dimension (expected) | Clearance | Source |
|-----------|---------------------|-------------------------------|-----------|--------|
| Pocket X extent | 77.5 to 82.5 (5 mm wide) | Tab width: ~4.5 mm (0.25 mm clearance per side) | 0.25 mm per side | Lid spatial 3d; Sub-I T1 gap note |
| Pocket Y extent | 152 to 155 (3 mm deep) | Tab barb depth: ~1.5 mm (1.5 mm clearance behind barb to pocket rear wall) | 1.5 mm behind barb | Lid spatial 3d |
| Pocket Z extent | 0 to 2.5 (2.5 mm tall from bottom face) | Tab barb height: ~1.5 mm (1.0 mm clearance above barb to pocket ceiling) | 1.0 mm above barb | Lid spatial 3d |

### Interface 4: Lid front face to bezel top edge

| Parameter | Lid dimension | Bezel dimension | Clearance | Source |
|-----------|--------------|----------------|-----------|--------|
| Lid front face plane | Y = 155 | Bezel top edge abuts from +Y direction | Butt joint (cosmetic, not structural) | Lid spatial 3d |
| Contact zone | X = 0..160, Z = 0..4 | Bezel top edge: full width, height up to Z = 4 (lid top face) | 0 nominal | Lid spatial 3d |

---

## 5. Direction Consistency Check

| # | Claim | Direction | Axis | Verified? | Notes |
|---|-------|-----------|------|-----------|-------|
| 1 | "Lid pressed straight down onto tray" | Down | -Z in lid frame, -Z in tray frame | Yes | Lid Z = 0 seats on tray Z = 72 |
| 2 | "Tabs deflect outward away from tray center" | Left tabs deflect -X, right tabs deflect +X | +/-X | Yes | Ridge peak at X = 6 (left) pushes tab tip in -X; ridge peak at X = 154 (right) pushes tab tip in +X |
| 3 | "Tabs spring inward behind catch face" | Left tabs return +X, right tabs return -X | +/-X (opposite of #2) | Yes | Cantilever spring restores tab to undeflected position, engaging behind ridge |
| 4 | "Lid removal by pulling upward" | Up | +Z | Yes | Opposite of installation direction |
| 5 | "Bezel T1 tab enters from below and hooks upward" | Tab enters -Z into pocket, hooks +Z | -Z then +Z | Yes | Pocket open at Z = 0 (lid bottom); tab barb catches pocket ceiling at Z = 2.5 |
| 6 | "Stiffening ribs hang below lid" | Down | -Z (lid frame) | Yes | Ribs extend from Z = 0 to Z = -3 |
| 7 | "Rear edge flush with tray rear exterior" | -- | Y = 0 alignment | Yes | Both lid and tray have rear face at Y = 0 |
| 8 | "Front edge at Y = 155" | -- | Y = 155 alignment | Yes | Both lid and tray have front face at Y = 155 |

No contradictions found.

---

## 6. Assembly Sequence

### Lid installation (in context of full cartridge build)

The lid is installed at Step 9 in the cartridge assembly sequence (concept Section 12), after all internal components (pumps, tubes, fittings, release plate, linkage rods) are in place.

1. **Verify tray is fully loaded:** Pumps bolted, tubes routed and clipped, fittings pressed in, release plate on guide posts, linkage rods threaded through slots.
2. **Orient lid:** Hold with bottom face (tabs, ribs, and bezel pocket visible) facing down.
3. **Align rear edge:** Place the lid's rear edge (Y = 0) against the tray's rear wall top edge. The 8.5 mm deep rear wall bearing surface provides a registration reference.
4. **Lower front edge:** Hinge the lid down until the front edge (Y = 155) is level with the tray side wall tops. All 8 tabs now hover above the tray interior, just outside the ridge positions.
5. **Press down:** Apply uniform downward pressure across the lid surface. Tabs deflect outward by 1.0 mm over the ridge ramps and snap behind the catch faces. A compound click confirms engagement.
6. **Verify:** Lid sits flat. Attempt to lift -- lid resists. Ready for bezel installation.

### Lid removal (service)

1. **Remove bezel first** (bezel is the outermost part; its removal exposes the lid front edge).
2. **Grip lid edges** at the left and right sides (or front and rear edges).
3. **Pull upward (+Z)** firmly and evenly. All 8 tabs deflect outward by 1.0 mm, clearing the ridges.
4. **Lift lid free.** Set aside. All internal components are now accessible from above.

### Assembly feasibility check

| Step | Check | Result |
|------|-------|--------|
| Orient lid | Can the builder distinguish top from bottom? | Yes. Snap tabs, ribs, and bezel pocket are all on the bottom face (visible when flipped). The top face is smooth and featureless. |
| Align rear edge | Can the lid be placed in only one orientation? | Mostly. The lid is nearly symmetric in X, but the bezel pocket at X = 77.5..82.5 is centered, so 180-degree rotation about Z would swap front/rear but the tabs would still align with ridges. **DESIGN GAP: The lid is symmetric about the X centerline. A 180-degree rotation about X = 80 swaps front and rear, placing the bezel pocket at the wrong end (Y = 0..3 instead of Y = 152..155). The tabs would still snap into ridges, producing a false-positive click. Keying feature needed.** See Section 8. |
| Press down | Can a hand reach the full surface? | Yes. The 160 x 155 mm lid is small enough to press with one palm. |
| After installation, are any components trapped? | The lid traps tube runs (by design -- retention). All internal components were installed before the lid and remain accessible by removing the lid. | No trapped components. |
| Disassembly access | Can the lid be removed without removing internal components first? | Yes. The lid lifts straight off. No internal part blocks lid removal. |

---

## 7. Part Count Analysis

The lid is a single printed part. There are no sub-assemblies, fasteners, or separate components.

| Check | Part A | Part B | Permanently joined? | Move relative? | Same material? | Action |
|-------|--------|--------|--------------------|--------------:|----------------|--------|
| Panel body + snap tabs | Panel | 8 tabs | Yes (integral) | No | Yes (PETG) | Correct: one printed part |
| Panel body + ribs | Panel | 3 ribs | Yes (integral) | No | Yes (PETG) | Correct: one printed part |
| Panel body + bezel pocket | Panel | Pocket | N/A (pocket is a cut) | No | N/A | Correct: feature of one part |
| Lid + tray | Lid | Tray | No (snap-fit, removable) | Yes (lid translates Z during install/removal) | Yes (PETG) | Correct: must be separate (lid must be removable for service) |

Part count: **1 printed part.** No fasteners. No hardware. Minimized.

---

## 8. Design Gaps

### Gap 1: Lid orientation keying (anti-reversal)

**Claim:** "The builder aligns the lid over the tray and presses down."

**Problem:** The lid is symmetric about its X centerline (X = 80). A 180-degree rotation about this axis swaps Y = 0 with Y = 155, placing the bezel pocket at the rear (Y = 0..3) instead of the front (Y = 152..155). The snap tabs would still engage the tray ridges because the tab Y positions (20, 60, 100, 140) are symmetric about Y = 77.5, and the ridge Y positions are the same. The builder would get a satisfying click with the lid installed backwards. The only symptoms would be: (a) the bezel T1 tab has no pocket to engage, and (b) a pocket exists at the rear edge that serves no purpose.

**Resolution needed:** An asymmetric keying feature that prevents 180-degree Y reversal. Options:
- (a) Make one stiffening rib asymmetric in Y (e.g., move Rib 1 from Y = 40 to Y = 35) so it interferes with a ridge or tray feature when reversed.
- (b) Add a small nub on the lid underside near the front edge (Y > 145) that seats into a matching recess on the tray rear wall top edge. When reversed, the nub hits the flat rear wall top with no recess, preventing the lid from seating flush.
- (c) Rely on the builder noticing the bezel pocket orientation. This violates the product value of error-proof assembly.

**Recommended resolution:** Option (b). Add a 3 mm diameter x 1 mm tall alignment nub on the lid underside at (X = 80, Y = 150, Z = 0), protruding downward to Z = -1. Add a matching 3.2 mm diameter x 1 mm deep recess on the tray rear wall top edge at the equivalent tray position (X = 80, Y = 150, tray Z = 72). Wait -- Y = 150 is not on the rear wall (the rear wall top edge is Y = 0..8.5). The nub must be at the rear of the lid to mate with the rear wall.

**Corrected resolution:** Add alignment nub on lid underside at (X = 80, Y = 4.25, Z = 0), protruding to Z = -1. This sits over the center of the rear wall top edge (tray Y = 0..8.5, centered at Y = 4.25). Add a 3.2 mm diameter x 1 mm deep recess in the tray rear wall top edge at (X = 80, Y = 4.25, Z = 72). When the lid is reversed, the nub (now at the front, Y = 150.75) hangs over the open tray interior, clears into the cavity (Z = -1 = tray Z = 71, well above interior components), but the lid does NOT seat flat because the rear edge no longer has the nub engaging the recess -- actually, the lid would still seat flat because the nub just hangs in the void.

**Revised approach:** Make the nub a protruding pin (2 mm diameter x 2 mm tall) on the lid underside at (X = 130, Y = 4.25, Z = 0 to -2), with a matching 2.2 mm diameter x 2.0 mm deep hole in the tray rear wall top edge at (X = 130, Y = 4.25, Z = 72 to 70). The X = 130 position is intentionally off-center. When the lid is reversed 180 degrees about Y = 77.5, the pin moves to (X = 130, Y = 150.75) -- hanging over the open tray interior with no matching hole, which is fine. But the real keying comes from the X position: when reversed, X = 130 maps to X = 30 (mirrored about X = 80), but we aren't flipping about X. A Y-reversal keeps X the same. So the pin at X = 130, Y = 4.25 maps to X = 130, Y = 150.75 when reversed -- no tray hole at that position, pin hangs in void, lid seats flat anyway because the pin is below the bottom face and the void is open.

**The pin must physically prevent seating.** Make it longer: 3 mm diameter x 4 mm tall pin at (X = 130, Y = 4.25, Z = 0 to -4). Matching hole: 3.2 mm diameter x 4 mm deep at (X = 130, Y = 4.25, tray Z = 68..72). When correct, the pin drops into the hole and the lid seats flat. When reversed (Y flipped), the pin at Y = 150.75 hits nothing -- but also doesn't prevent seating because it hangs into the open tray cavity.

**Final resolution:** The simplest approach is to make the lid non-symmetric by offsetting the bezel pocket plus adding a rear-edge asymmetric alignment tab. Add a rectangular tab (5 mm X x 3 mm Y x 2 mm Z) protruding downward from the lid underside at X = 130, Y = 1..4 (over the rear wall top edge). Matching slot: 5.2 mm x 3.2 mm x 2 mm in the tray rear wall top at the same position. When reversed, the tab at Y = 151..154 extends below the lid over the open tray interior and does NOT prevent seating. This means geometric keying alone cannot prevent Y-reversal if the only interference target is the rear wall and the front is open.

**Conclusion: Geometric keying against Y-reversal is difficult because the tray front is open.** The most practical resolution is to add a visible directional indicator: a molded arrow or "FRONT" text on the lid top face near Y = 155. This violates the "languageless" product value for user-facing surfaces, but the lid top face is never seen by the user (it faces upward inside the enclosure). A molded arrow at 0.3 mm depth is sufficient for the one-time builder assembly. Combined with the asymmetric bezel pocket location (only at the front edge), a reasonably attentive builder will orient the lid correctly.

**Status:** Accepted risk. Add a 0.3 mm deep molded arrow on the lid top face at (X = 75..85, Y = 145..150, Z = 4) pointing toward Y = 155 (front). This is a cosmetic emboss on a non-user-facing surface and is adequate for the one-time build step.

### Gap 2: Cantilever stress margin

**Claim:** "Tabs deflect 1.0 mm without yielding."

**Status:** Marginal. The final beam geometry (1.0 mm thick x 8.0 mm effective length) produces ~49 MPa peak stress vs. ~50 MPa PETG yield. This is within the material's capability given PETG's ductility and the low cycle count (lid removed/installed fewer than 20 times in the product lifetime), but there is effectively zero safety margin. A test print of the tab geometry should be performed before committing to the full lid. If the tab cracks or takes a permanent set after 5 install/remove cycles, increase the effective cantilever length to 10 mm (deepen the relief slot to Z = +5.5, leaving 0 mm below the top face -- not viable) or reduce the required deflection by reducing the tray ridge protrusion from 1.0 mm to 0.7 mm (requires updating Sub-H).

**Recommendation:** Prototype the tab geometry. If stress is a problem, the first lever is reducing ridge protrusion to 0.75 mm (update Sub-H) which reduces required deflection to 0.75 mm and drops peak stress to ~37 MPa (comfortable margin). This requires coordinated changes to Sub-H dimensions.

---

## 9. Print Specification

| Parameter | Value |
|-----------|-------|
| Material | PETG |
| Print orientation | Flat, bottom face (Z = 0) on build plate, top face (Z = 4) up |
| Layer height | 0.2 mm (standard). The 1.0 mm snap tab beams are the tightest feature; 0.2 mm layers give 5 layers through the beam thickness, adequate for flexibility. |
| Supports | None. The snap tabs print hanging downward from the lid body -- they are vertical walls and do not require support. The relief slots are rectangular pockets with flat ceilings at Z = 3.5 (0.5 mm from top face), which is a short bridge. The 6 mm bridge span (Y direction) is within PETG bridge capability. Stiffening ribs print as downward extrusions from the panel (vertical walls, no support needed). |
| Infill | Not applicable (the panel is only 4 mm thick -- at 4 perimeter walls x 0.4 mm = 1.6 mm per side, the panel is essentially solid through its full thickness with no room for infill). |
| Perimeters | 4 minimum |
| Estimated print time | 1-2 hours |
| Build plate fit | 160 x 155 mm footprint, well within 325 x 320 mm build volume |

---

## 10. Summary

The lid is a single PETG printed part: a 160 x 155 x 4 mm flat panel with 8 slot-released snap tabs (4 per long edge), 3 underside stiffening ribs, one bezel tab pocket (T1) on the front edge, and a molded directional arrow on the top face. It snaps onto the tray top edges with no fasteners, closing the torsion box. Total features: 8 tabs + 8 relief slots + 3 ribs + 1 pocket + 1 arrow emboss = 21 machining operations on the base panel solid. All geometry is prismatic (extrudes and cuts). No supports required for printing. Two design gaps identified: (1) orientation keying resolved with a molded arrow; (2) cantilever stress margin is tight and requires prototype verification.
