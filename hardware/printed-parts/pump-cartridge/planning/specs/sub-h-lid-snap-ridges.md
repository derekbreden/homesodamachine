# Parts Specification: Sub-H Lid Snap Detent Ridges

## Coordinate System

Same as tray (Sub-A):
- Origin: rear-left-bottom corner of tray
- X: width, 0..160 mm (left to right when facing front)
- Y: depth, 0..155 mm (0 = dock/rear, 155 = user/front)
- Z: height, 0..72 mm (0 = floor bottom, 72 = top of side walls)

---

## 1. Mechanism Narrative

### What the user sees and touches

The lid snap detent ridges are interior features that the user never sees or touches during normal operation. They are small triangular bumps on the inside faces of both long side walls, near the top edge. The user interacts with them indirectly: when pressing the lid down onto the tray, the lid's flexible snap tabs deflect outward to clear these ridges and then spring back behind them, producing a click. When prying the lid off for service, the user pulls upward on the lid, forcing the tabs to deflect outward again to clear the ridges.

### What moves

**Stationary:** All 8 ridges. They are printed integral with the tray side walls and do not move.

**Moving:** The lid's snap tabs (not part of Sub-H, but the mating feature). Each tab is a flexible cantilever hanging from the lid perimeter. During lid installation, the tab tip deflects outward (away from tray center) by 1.0 mm to pass over the ridge peak, then springs inward behind the ridge's vertical catch face.

### What converts the motion

No motion conversion. The lid is pressed straight down (in -Z). The 45-degree ramp on the top face of each ridge converts the vertical lid force into a horizontal outward deflection of each snap tab. The ramp geometry (45-degree angle over 1.0 mm of vertical rise from the peak at Z = 70.5 to the top of the ridge at Z = 71.5) produces a 1:1 ratio of vertical travel to horizontal tab deflection.

### What constrains each moving part

The ridges themselves are constrained by being integral to the tray wall (they are solid PETG bonded to the wall face, not separate parts). The lid tabs are constrained by the lid geometry (specified elsewhere). From the tray's perspective, the ridges provide a single constraint: they prevent the lid from lifting in the +Z direction once the tabs are engaged behind the catch faces.

### What provides the return force

Not applicable to the ridges themselves (they are rigid, stationary features). The lid tabs return to their undeflected position via their own cantilever stiffness (specified in the lid parts.md, not here).

### What is the user's physical interaction

**Lid installation:** The user aligns the lid over the tray and presses downward. The lid tabs contact the 45-degree ramps at Z = 71.5 on each ridge. Continued downward pressure slides each tab along the ramp, deflecting it outward by 1.0 mm (the ridge protrusion distance). When the tab tip passes the peak at Z = 70.5, the tab springs inward behind the vertical catch face. The tab hook now rests below Z = 69.5, behind the 1.0 mm vertical catch face. The transition from ramped resistance to sudden release produces a perceptible click at each ridge location.

**Lid removal:** The user grips the lid edges and pulls upward (+Z). The tab hooks press against the underside of the vertical catch face at Z = 69.5. Continued upward force deflects the tabs outward by 1.0 mm to clear the ridge tips, and the lid lifts free. The removal force is the sum of all 8 tab cantilever deflection forces -- this is specified by the lid, not by the ridges. The ridges contribute only the geometry that the tabs must deflect past.

---

## 2. Constraint Chain Diagram

```
[User hand] -> [Lid: translates -Z] -> [Lid snap tab contacts ridge ramp]
                                         -> [45-deg ramp converts -Z force to +/-X tab deflection]
                                         -> [Tab clears ridge peak (1.0 mm protrusion)]
                                         -> [Tab springs behind catch face]
                                         -> [Catch face at Z=69.5 prevents +Z lid motion]
                                              ^ ridge constrained by: integral bond to tray wall (all 6 DOF)
                                              ^ lid constrained by: 8 ridge catch faces (-Z only, +Z blocked)
```

**For removal:**
```
[User hand] -> [Lid: pulled +Z] -> [Tab hook presses on catch face underside at Z=69.5]
                                    -> [Tab deflects outward by 1.0 mm to clear ridge tip]
                                    -> [Tab clears peak, lid lifts free]
                                         ^ deflection force set by lid tab geometry (not Sub-H)
                                         ^ ridge geometry sets the 1.0 mm deflection requirement
```

---

## 3. Feature Specification

### 3a. Ridge Quantity and Distribution

8 ridges total: 4 on the left wall interior face, 4 on the right wall interior face. Positions are symmetric about the tray X centerline (X = 80 mm).

### 3b. Ridge Positions (tray frame)

| Ridge ID | Wall | Wall face X (mm) | Y center (mm) | Y start (mm) | Y end (mm) | Z peak (mm) |
|----------|------|-------------------|----------------|---------------|-------------|--------------|
| L1 | Left | 5.0 | 20.0 | 17.0 | 23.0 | 70.5 |
| L2 | Left | 5.0 | 60.0 | 57.0 | 63.0 | 70.5 |
| L3 | Left | 5.0 | 100.0 | 97.0 | 103.0 | 70.5 |
| L4 | Left | 5.0 | 140.0 | 137.0 | 143.0 | 70.5 |
| R1 | Right | 155.0 | 20.0 | 17.0 | 23.0 | 70.5 |
| R2 | Right | 155.0 | 60.0 | 57.0 | 63.0 | 70.5 |
| R3 | Right | 155.0 | 100.0 | 97.0 | 103.0 | 70.5 |
| R4 | Right | 155.0 | 140.0 | 137.0 | 143.0 | 70.5 |

Center-to-center spacing along Y: 40.0 mm.

### 3c. Ridge Cross-Section Profile

Each ridge has a quadrilateral cross-section (viewed in the XZ plane, looking in the +Y direction). The profile is identical for all 8 ridges, mirrored about X = 80 for the right wall.

**Left wall ridge profile (vertices in tray frame, at any Y slice within the ridge extent):**

| Vertex | X (mm) | Z (mm) | Description |
|--------|--------|--------|-------------|
| A | 5.0 | 71.5 | Wall face, top of ridge (flush with ramp start) |
| B | 6.0 | 70.5 | Peak / tip (maximum protrusion from wall) |
| D | 6.0 | 69.5 | Base of vertical catch face |
| C | 5.0 | 69.5 | Wall face, bottom of ridge |

Profile edges:
- A to B: 45-degree ramp (entry/installation face). Run = 1.0 mm (+X), rise = 1.0 mm (-Z). The lid tab slides down this ramp during installation, being deflected outward.
- B to D: vertical catch face, 1.0 mm tall. This face prevents the lid from lifting once the tab is engaged behind it.
- D to C: base edge, 1.0 mm long, flush against wall face (this edge lies on the wall interior surface).
- C to A: wall-face edge, 2.0 mm tall (the ridge height measured along Z on the wall face).

**Right wall ridge profile (mirrored, vertices in tray frame):**

| Vertex | X (mm) | Z (mm) | Description |
|--------|--------|--------|-------------|
| A | 155.0 | 71.5 | Wall face, top of ridge |
| B | 154.0 | 70.5 | Peak / tip (protrudes in -X, toward tray center) |
| D | 154.0 | 69.5 | Base of vertical catch face |
| C | 155.0 | 69.5 | Wall face, bottom of ridge |

### 3d. Ridge Dimensions Summary

| Parameter | Value | Source |
|-----------|-------|--------|
| Protrusion from wall face | 1.0 mm | Spatial resolution (3e) |
| Total height (Z extent) | 2.0 mm (Z = 69.5 to 71.5) | Spatial resolution (3b) |
| Ramp height (A to B, vertical component) | 1.0 mm | Spatial resolution (3e) |
| Catch face height (B to D) | 1.0 mm | Spatial resolution (3e): Z_peak(70.5) - Z_base(69.5) |
| Ramp angle | 45 degrees | Derived: arctan(1.0 / 1.0) |
| Extrusion length (Y extent per ridge) | 6.0 mm | Spatial resolution (3f) |
| Distance from side wall top edge to ridge top (A vertex) | 0.5 mm | 72.0 - 71.5 = 0.5 mm |

### 3e. Retention Geometry

| Parameter | Value | Source |
|-----------|-------|--------|
| Retention depth (horizontal overlap behind catch face) | 1.0 mm | Spatial resolution (3g) |
| Tab deflection required to clear ridge peak | 1.0 mm | Equals protrusion distance |
| Engagement zone below catch face (Z range for tab hook) | Z = 67.5 to 69.5 mm | Spatial resolution (3g) |
| Tab-to-wall overlap when engaged (X range) | 2.0 mm from wall face | Spatial resolution (3g) |

### 3f. Material and Print Considerations

| Parameter | Value | Source |
|-----------|-------|--------|
| Material | PETG | requirements.md, concept architecture Sec. 7 |
| Print orientation | Ridges print integral with tray, open-top-up | Spatial resolution (Sec. 2) |
| Layer direction relative to ridge | Layers stack in Z; the 45-degree ramp face and vertical catch face are both printed at angles relative to layer lines | Derived from print orientation |
| Minimum feature size (protrusion) | 1.0 mm | Above H2C minimum; 2+ perimeters at 0.4 mm nozzle |
| Supports needed | None | Ridges protrude from vertical wall faces; no unsupported overhangs. The 45-degree ramp is at exactly 45 degrees from horizontal, which is the typical no-support threshold for FDM. |

---

## 4. Interface Specifications

### 4a. Ridge-to-Tray-Wall Bond (Sub-H to Sub-A)

The ridges are integral geometry -- they are boolean-unioned to the tray side wall interior faces. There is no separate part or joint. The bond is the full rectangular footprint of each ridge on the wall face.

| Parameter | Value |
|-----------|-------|
| Bond surface per ridge | 6.0 mm (Y) x 2.0 mm (Z) = 12.0 mm^2 |
| Bond plane (left wall) | X = 5.0 mm |
| Bond plane (right wall) | X = 155.0 mm |
| Fillet at junction | None. The ridge IS the snap feature; filleting the base would reduce the catch face effectiveness. |

### 4b. Ridge-to-Lid-Tab Interface (Sub-H to Lid)

This defines what the tray ridge expects from the lid's snap tab. The lid specification must satisfy these interface requirements.

| Parameter | Tray-side value | What the lid tab must provide |
|-----------|----------------|-------------------------------|
| Catch face location | Z = 69.5 mm, extending 1.0 mm from wall face | Tab hook must reach below Z = 69.5 and extend at least 1.0 mm from wall face when engaged |
| Tab engagement zone (X, left wall) | X = 5.0 to 7.0 mm | Tab occupies this zone when locked |
| Tab engagement zone (X, right wall) | X = 153.0 to 155.0 mm | Tab occupies this zone when locked |
| Tab engagement zone (Z) | Z = 67.5 to 69.5 mm | 2.0 mm hook depth below catch face |
| Required tab deflection | 1.0 mm outward (away from tray center) | Tab must be flexible enough to deflect 1.0 mm without yielding |
| Ridge Y extent | 6.0 mm per ridge | Tab width must be <= 6.0 mm to engage a single ridge, or wider if spanning multiple ridges (not recommended) |
| Number of engagement points per side | 4 | Lid must have 4 tabs per long edge at Y = 20, 60, 100, 140 mm |

---

## 5. Clearance Analysis

### 5a. Ridge Tips vs. Interior Pocket

| Check | Value | Status |
|-------|-------|--------|
| Left ridge tips at X | 6.0 mm | 1.0 mm into 150 mm interior pocket |
| Right ridge tips at X | 154.0 mm | 1.0 mm into 150 mm interior pocket |
| Clear span between opposing tips | 148.0 mm | No interference with interior components |
| Ridge Z range | 69.5 to 71.5 mm | Top 2.5 mm of 69 mm interior cavity -- above pump zone, tube routing zone, release plate, and all other interior features |

### 5b. Ridge vs. Other Sub-Components

| Potential conflict | Check | Result |
|-------------------|-------|--------|
| Sub-G linkage rod slots (through side walls) | Slots are at mid-wall Z, aligned with release plate edge height (~30-40 mm Z). Ridges are at Z = 69.5-71.5. | No conflict. Vertically separated by > 25 mm. |
| Sub-I bezel receiving features (front edge, Y > 145 mm) | Ridge L4/R4 at Y = 137-143 mm. Bezel features at Y > 145 mm. | No conflict. 2 mm gap between ridge end and bezel zone start. |
| Sub-B T-rail tongues (outer side walls) | T-rails are on exterior wall faces. Ridges are on interior wall faces. | No conflict. On opposite sides of 5 mm wall. |
| Sub-F tube routing channels (floor level) | Channels are at floor level (Z = 3-13 mm). Ridges at Z = 69.5-71.5. | No conflict. Vertically separated by > 56 mm. |

---

## 6. Assembly Sequence (Sub-H specific)

Sub-H has no assembly sequence because the ridges are printed integral with the tray. They exist as features of the tray solid from the moment the tray is printed.

**Lid installation sequence (the only assembly event involving Sub-H):**

1. Orient lid over tray with snap tabs facing downward and inward.
2. Align lid tabs with ridge Y positions (4 tabs per long edge at Y = 20, 60, 100, 140 mm).
3. Press lid downward. Tabs contact 45-degree ramps at Z = 71.5 and deflect outward by 1.0 mm.
4. Continue pressing until tabs clear peaks at Z = 70.5 and spring inward behind catch faces.
5. Lid is retained: catch faces at Z = 69.5 prevent the lid from lifting.

**Lid removal (service):**

1. Grip lid edges and pull upward (+Z).
2. Tab hooks press against catch face undersides at Z = 69.5, deflecting tabs outward by 1.0 mm.
3. Tabs clear ridge peaks, lid lifts free.

**Disassembly for ridge service:** Not applicable. The ridges are integral to the tray. If a ridge breaks, the tray must be reprinted. Given that each ridge is 1.0 mm PETG bonded to a 5 mm wall over a 12 mm^2 footprint, breakage under normal lid snap forces is unlikely.

---

## 7. Design Gaps

None identified. All behavioral claims in this specification resolve to named geometric features with explicit dimensions. The ridges are geometrically simple (prismatic extrusions of a 4-vertex polygon) with no moving parts, no return forces, and no tolerance-critical fits on the tray side.

The only tolerance-sensitive aspect of the snap-fit system is the lid tab's cantilever stiffness and deflection limit -- but that is specified by the lid, not by Sub-H. From the tray's perspective, the ridges are passive geometry with fully defined dimensions.
