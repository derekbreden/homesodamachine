# Lever — Parts Specification

**Pipeline step:** 4b — Parts Specification
**Input documents:** spatial-resolution.md, synthesis.md, concept.md, decomposition.md, requirements.md, vision.md
**Output:** This document — primary input to the CadQuery generation agent (Step 6g)

---

## 1. Part Summary

| Field | Value |
|---|---|
| Part name | Lever |
| Part type | Single printed PETG part |
| Function | Pull surface for the squeeze mechanism. The user's fingers contact the lever plate front face; struts transmit the pull force rearward through the interior plates to the release plate (via Phase 2 joint). In Phase 1 the strut ends are free — no joint geometry exists. |
| Material | PETG |
| Envelope (W × H × D) | 80.0 mm × 65.0 mm × 94.0 mm (plate 80×65×4, struts extend 90 mm rearward) |
| Print orientation | Front face DOWN on build plate (XZ plane on build plate). Struts extend upward (+Y print direction). |
| Piece count | 1 |
| Fasteners | None |
| Sub-assemblies | None |

**Coordinate system (part local frame):**

| Axis | Direction | Range |
|---|---|---|
| X | Width, left to right as seen by user | 0 → 80.0 mm |
| Y | Depth, front (user-facing) to rear (strut-tip end) | 0 → 94.0 mm |
| Z | Height, bottom to top | 0 → 65.0 mm |

Origin: bottom-left corner of the lever plate front face (the corner at X=0, Y=0, Z=0) as seen from the front face.
Y=0 = lever plate front face (pull surface — user finger contact; sits on build plate in print orientation).
Y=4 = lever plate rear face (struts begin here).
Y=94 = strut tips (plain square ends; Phase 2 joint zone).

---

## 2. Mechanism Narrative (Rubric A)

### What the user sees and touches

The lever plate front face is the deepest surface the user touches during the squeeze. The user inserts their fingers through the rectangular hole in the front panel — the hole is positioned so that, from the outside, it reads as a designed grip recess in a clean flat surface. The lever plate face is set back from the front panel exterior face by a depth determined in Season 2. The user cannot see the lever as a separate part; they see a grip pocket and a flat pull surface at the bottom of it. The four struts extending from the lever rear face are invisible to the user at all times.

### What moves

**Moving:** The lever — a single flat PETG part — translates rearward (in the +Y direction, into the cartridge) during squeeze. Translation distance: 3.0 mm (matching the release plate stroke; the struts are a rigid link between the two plates).

**Stationary:** Everything else during the squeeze: the front panel, the pump tray, the coupler tray, the cartridge walls. The pump tray and coupler tray constrain the struts laterally (in Phase 4 when the strut bores are added) but do not move with the lever.

### What converts the motion

There is no mechanical advantage conversion. The user's pull force on the lever plate front face (Y=0) transmits directly through the 4.0 mm plate body and the four 6.0×6.0 mm struts to the Phase 2 joint, and from there to the release plate. The lever is a rigid translation link — force is transmitted 1:1 with no amplification or direction change.

Force path: user finger pads contact lever front face (Y=0) → tension transmits through the 4.0 mm plate body → compressive load distributes across the four 6.0×6.0 mm struts → struts carry load in compression along their length (Y axis) → Phase 2 joint connects lever strut tips (Y=94) to release plate struts → release plate translates rearward → release plate annular lips contact PP0408W collet faces → collets release.

Note on direction: the user pulls the lever toward them (+Y in lever frame = rearward into cartridge). The plate pulls away from the user in part-frame Y, so the struts are in compression (the lever is being driven rearward toward the rear wall, not pulled away from it). The collets are depressed by rearward plate motion. The force on the struts during squeeze is compressive along the strut length axis — the mechanically strong FDM orientation.

**DESIGN GAP — lever pull travel stop:** There is no geometric feature in Phase 1 that limits the lever's rearward travel to 3.0 mm. The collet mechanism in the release plate (Zone 1 bore floor contacting the fitting body shoulder) provides the de facto stop, but the lever itself has no stop feature. This is a Phase 1 design gap; a travel limit is a Season 2 or Phase 2 item. The lever plate will physically bottom out only when the release plate hard-stops against the fitting bodies. No Phase 1 action required.

### What constrains the lever

**Lateral (XZ plane) constraint:** In Phase 4, four square bores (6.2×6.2 mm each) cut through the pump tray and coupler tray will constrain the struts laterally, preventing rotation of the lever about the Y axis and preventing XZ translation. In Phase 1, no lateral constraint exists — the lever is a free-standing part.

**Rearward (+Y) translation limit:** None in Phase 1 (see design gap above).

**Forward (−Y) translation limit (rest position):** None in Phase 1. In the assembled cartridge the return springs bear against the release plate rear face and push the entire lever-strut-release plate assembly toward the user. The forward rest position is where the release plate front face contacts the fitting collet faces. The lever plate front face position at rest is set by the strut length and the release plate rest position — not by any feature on the lever itself.

### Return force

None in Phase 1. Return springs are a Phase 12 (Season 4) item. The spring pockets are in the cartridge body rear wall (established in the release plate specification) and bear against the release plate rear face — no feature on the lever plate is needed for spring return.

### The user's physical interaction

The user's hand is palm-up. The palm presses forward against the front panel exterior face (the stationary surface). The fingers curl upward through the rectangular front panel hole and contact the lever plate front face (Y=0 in lever local frame). The 80.0 mm × 65.0 mm contact area provides a two-to-three finger contact zone (grip width 80 mm; grip height 55 mm usable — the bottom 5 mm and top 5 mm zones are immediately adjacent to the strut attachment zones on the rear face but present a flat front face surface to the fingers). The user squeezes: fingers pull rearward, palm pushes forward. The lever translates 3.0 mm rearward until the release plate hard-stops. The user feels and hears the four collets release and withdraws the cartridge.

**Grounding note:** The 80.0 mm plate width, 50.0 mm plate height, and 4.0 mm plate thickness are the geometric features that produce the grip feel. The 3.0 mm travel comes from the release plate specification (collet release at 1.33 mm, hard stop at plate body shoulder). No additional feature on the lever plate produces tactile feedback during Phase 1.

---

## 3. Rubric B — Constraint Chain Diagram

```
[User fingers, palm-up, curled upward]
        |
        | Pull force (rearward, +Y direction)
        v
[Lever plate front face — Y=0, 80mm×50mm flat PETG surface]
        |
        | Tension through 4.0mm plate body
        v
[Lever plate rear face — Y=4mm; struts originate here]
        |
        | Compression along strut length (Y axis), 4× 6mm×6mm×90mm struts
        | Constrained laterally by: pump tray strut bores (Phase 4) + coupler tray strut bores (Phase 4)
        v
[Strut tips — Y=94mm; Phase 2 joint zone]
        |
        | Force transfer via Phase 2 tapered dovetail + snap detent joint (NOT IN PHASE 1)
        v
[Release plate — translates 3.0mm rearward]
        |
        | Constrained rotationally by: guide pins (Pin1 X=5, Z=60; Pin2 X=75, Z=5 in release plate frame)
        | Returned by: compression springs in cartridge body rear wall (Phase 12)
        v
[Zone 2→3 annular lip faces contact PP0408W collet end faces]
        |
        | Collet translation (inward, +Y relative to cartridge rear wall)
        v
[Output: collet gripper teeth release dock tube stubs]

HARD STOP: Zone 1 bore floor contacts PP0408W body shoulder at 1.33mm travel → limits over-travel.
           Feature: Zone 1 bore floor at Y=3.6mm from release plate front face (Y=1.4mm from rear face).

TRAVEL LIMIT (LEVER): DESIGN GAP — no feature on the lever limits its rearward travel.
                      Stop is de facto via release plate fitting body hard stop.
```

---

## 4. Rubric C — Direction Consistency Check

Coordinate system: lever local frame (Y = rearward into cartridge; X = rightward as seen by user; Z = upward).

| Claim | Direction | Axis | Verified? | Notes |
|---|---|---|---|---|
| User pulls lever rearward | Into cartridge | +Y (lever local) | Yes | User is in front; pulling toward themselves moves lever away from them and into the cartridge = +Y in lever frame |
| Struts extend rearward from plate rear face | Into cartridge | +Y (lever local) | Yes | Struts start at Y=4mm (plate rear face) and end at Y=94mm |
| Struts carry load in compression along length | Along strut axis | +Y axis | Yes | Lever is pushed rearward relative to the resistance; struts are compressed not tensioned |
| Release plate moves rearward during squeeze | Into cartridge | +Y (lever local) = +Y (cartridge) | Yes | Release plate moves away from user toward rear wall |
| Return springs push lever/release plate toward user | Toward user | −Y (lever local) | Yes | Springs in rear wall push release plate toward user; lever follows via struts |
| Collets are depressed rearward | Into cartridge | +Y (cartridge) | Yes | PP0408W collets are on the rear face of the release plate; depression is in the +Y cartridge direction, consistent with release plate synthesis |
| Strut tips are at Y=94mm | Rearward from plate | +Y direction from plate | Yes | Y=94mm = 4mm plate + 90mm strut, rearward of front face |
| Lever plate spans Z=0 to Z=65mm | Bottom to top | +Z | Yes | Origin at bottom-left; Z increases upward |
| Struts positioned at Z=5mm and Z=60mm | Within plate height | Z in [0, 65] | Yes | 5mm from bottom edge, 5mm from top edge |

No directional contradictions found.

---

## 5. Feature List

Every feature is described with: name, operation type (Add = material added to blank, Remove = material removed), exact dimensions, position in part local frame, and justification.

### Feature 1 — Plate Body

| Field | Value |
|---|---|
| Operation | Add (base body) |
| Shape | Rectangular prism |
| Width (X) | 80.0 mm |
| Height (Z) | 65.0 mm |
| Depth (Y) | 4.0 mm |
| Position | X: 0→80.0, Y: 0→4.0, Z: 0→65.0 |
| Justification | Physical necessity (structural): provides the rigid load-transfer body between the user's finger contact surface (Y=0) and the strut attachment zone (Y=4). Width 80.0 mm matches the release plate width so lever strut positions align with release plate strut positions (vision §3: "lever connects to release plate struts"). Height 65.0 mm matches the release plate height so the strut Z positions (Z=5.0 and Z=60.0) align with the release plate strut Z positions in the assembly. Depth 4.0 mm provides rigid plate with center deflection <0.1 mm under 30 N (synthesis §3 calculation: δ ≈ 0.063 mm at 4.0 mm thickness). |

### Feature 2 — Plate Perimeter Corner Radii

| Field | Value |
|---|---|
| Operation | Remove (blend, CadQuery fillet) |
| Shape | Convex cylindrical fillet |
| Affected edges | The four vertical edges of the plate parallel to Y, at the four XZ corners: (X=0, Z=0), (X=80.0, Z=0), (X=0, Z=65.0), (X=80.0, Z=65.0). Each edge runs from Y=0 to Y=4.0. |
| Radius | 2.0 mm |
| Justification | Vision §3: consistent design language with the release plate (concept.md §5: "corner treatment: 2–3mm radii, consistent with the release plate's corner language"). A 2.0 mm radius prevents sharp rectangle corners from reading as raw rectangular stock. Also physical necessity (assembly): the corner radius reduces the risk of the plate perimeter snagging against the front panel hole edges during lever travel. |

### Feature 3 — Plate Bottom Chamfer (Elephant's Foot Prevention)

| Field | Value |
|---|---|
| Operation | Remove (chamfer) |
| Shape | 45° chamfer |
| Dimension | 0.3 mm × 45° on the bottom perimeter edge of the plate (the edge at Z=0, running the full perimeter at Y=0 to Y=4.0). Applied only to the Z=0 face edge, not the Y=0 face edge (those receive corner radii per Feature 2). |
| Position | Z=0 plane, full X perimeter of the plate front face |
| Justification | Physical necessity (manufacturing): requirements.md §6 states "the first 0.2–0.3mm of the part flares outward from bed adhesion." The plate is printed face-down; Z=0 is the build plate contact face in print orientation. The bottom edge of the plate in print orientation = Z=0 in part frame = the build plate edge. A 0.3mm×45° chamfer prevents elephant's foot from causing dimensional inaccuracy at the pull surface perimeter edge. |

### Feature 4 — Strut TL (Top-Left)

| Field | Value |
|---|---|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Shape | Rectangular prism |
| Cross-section | 6.0 mm (X) × 6.0 mm (Z) |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 9.0 mm, Z = 60.0 mm |
| Extents in X | 6.0 mm to 12.0 mm (center ±3 mm) |
| Extents in Z | 57.0 mm to 63.0 mm (center ±3 mm) |
| Y start (plate rear face) | Y = 4.0 mm |
| Y end (strut tip) | Y = 94.0 mm |
| Justification | Physical necessity (structural): transmits pull force from lever plate to Phase 2 joint. Position matches release plate strut TL position (X=9.0, Z=60.0) so struts align when the two parts are held together. X=9.0 mm derives from release plate bore horizontal spacing. Z=60.0 mm is the release plate's TL strut Z position, adopted directly. Cross-section 6.0×6.0 mm: Euler buckling critical load ≈333 N at 90 mm length, design load 15 N per strut — 22× margin. |

### Feature 5 — Strut TR (Top-Right)

| Field | Value |
|---|---|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Shape | Rectangular prism |
| Cross-section | 6.0 mm (X) × 6.0 mm (Z) |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 71.0 mm, Z = 60.0 mm |
| Extents in X | 68.0 mm to 74.0 mm |
| Extents in Z | 57.0 mm to 63.0 mm |
| Y start | Y = 4.0 mm |
| Y end | Y = 94.0 mm |
| Justification | Physical necessity (structural): same as Feature 4. Mirror of TL about X=40.0 mm. Position matches release plate strut TR position (X=71.0, Z=60.0). Horizontal spacing from TL: 71.0 − 9.0 = 62.0 mm. |

### Feature 6 — Strut BL (Bottom-Left)

| Field | Value |
|---|---|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Shape | Rectangular prism |
| Cross-section | 6.0 mm (X) × 6.0 mm (Z) |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 9.0 mm, Z = 5.0 mm |
| Extents in X | 6.0 mm to 12.0 mm |
| Extents in Z | 2.0 mm to 8.0 mm |
| Y start | Y = 4.0 mm |
| Y end | Y = 94.0 mm |
| Justification | Physical necessity (structural): same as Feature 4. Position matches release plate strut BL position (X=9.0, Z=5.0). Vertical spacing from TL: 60.0 − 5.0 = 55.0 mm, matching release plate strut vertical spacing. |

### Feature 7 — Strut BR (Bottom-Right)

| Field | Value |
|---|---|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Shape | Rectangular prism |
| Cross-section | 6.0 mm (X) × 6.0 mm (Z) |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 71.0 mm, Z = 5.0 mm |
| Extents in X | 68.0 mm to 74.0 mm |
| Extents in Z | 2.0 mm to 8.0 mm |
| Y start | Y = 4.0 mm |
| Y end | Y = 94.0 mm |
| Justification | Physical necessity (structural): same as Feature 4. Mirror of BL about X=40.0 mm. Position matches release plate strut BR position (X=71.0, Z=5.0). Diagonal distance from TL (9.0, 60.0) to BR (71.0, 5.0): √(62²+55²) = √(3844+3025) = √6869 = 82.9 mm. This diagonal spacing provides anti-rotation stability when struts are constrained by Phase 4 bores. |

---

## 6. Dimension Summary Table

All values in lever local frame (origin: bottom-left corner of plate front face).

| Dimension | Value | Source |
|---|---|---|
| Plate width (X) | 80.0 mm | Matches release plate width for strut alignment |
| Plate height (Z) | 65.0 mm | Matches release plate height for strut Z alignment |
| Plate thickness (Y) | 4.0 mm | Spatial resolution §5 / synthesis §3 |
| Plate front face | Y = 0 | Part local frame definition |
| Plate rear face | Y = 4.0 mm | Part local frame definition |
| Strut cross-section | 6.0 mm × 6.0 mm | Spatial resolution §3b / synthesis §4 |
| Strut length | 90.0 mm (estimated) | Synthesis §6 — pending cartridge depth confirmation |
| Strut Y start | Y = 4.0 mm | Plate rear face |
| Strut Y end (tips) | Y = 94.0 mm | Y=4 + 90mm strut length |
| Strut TL center (X, Z) | (9.0, 60.0) mm | Matches release plate strut TL position |
| Strut TR center (X, Z) | (71.0, 60.0) mm | Matches release plate strut TR position |
| Strut BL center (X, Z) | (9.0, 5.0) mm | Matches release plate strut BL position |
| Strut BR center (X, Z) | (71.0, 5.0) mm | Matches release plate strut BR position |
| Horizontal strut spacing (c-c) | 62.0 mm | 71.0 − 9.0 = 62.0 mm |
| Vertical strut spacing (c-c) | 55.0 mm | 60.0 − 5.0 = 55.0 mm (matches release plate) |
| Strut center to nearest plate edge (X sides) | 9.0 mm | Min of 9.0mm (left) and 9.0mm (right) |
| Strut center to nearest plate edge (Z sides) | 5.0 mm | Min of 5.0mm (bottom) and 5.0mm (top) |
| Plate material from strut bore edge to plate perimeter (sides) | 5.9 mm | 9.0 − 3.1 (bore radius 6.2/2) |
| Plate material from strut bore edge to plate perimeter (top/bottom) | 1.9 mm | 5.0 − 3.1 — exceeds 1.2 mm structural minimum |
| Perimeter corner radii | 2.0 mm | Concept §5 |
| Bottom chamfer (elephant's foot) | 0.3 mm × 45° | Requirements.md §6 |
| Min clearance strut bore to pump hole (Phase 4 reference) | 17.0 mm edge-to-edge | Spatial resolution §3c |
| Lever pull travel (mechanism) | 3.0 mm | Release plate synthesis (collet stroke) |

---

## 7. Rubric D — Interface and Path Consistency

### Part 1 — Interface Dimensions

| Interface | Part A (Lever) dimension | Part B dimension | Clearance | Source |
|---|---|---|---|---|
| Strut cross-section → pump tray bore (Phase 4) | 6.0 × 6.0 mm square | 6.2 × 6.2 mm square bore | 0.2 mm per side | Requirements.md §6: "0.2mm clearance for sliding fits" |
| Strut cross-section → coupler tray bore (Phase 4) | 6.0 × 6.0 mm square | 6.2 × 6.2 mm square bore | 0.2 mm per side | Requirements.md §6: "0.2mm clearance for sliding fits" |
| Strut tips → Phase 2 joint (Phase 2) | 6.0 × 6.0 mm plain square end at Y=94 | TBD in Phase 2 | TBD | Joint geometry not in Phase 1 scope |
| Lever plate front face → user fingers | 80.0 × 65.0 mm flat PETG surface | N/A (skin contact) | N/A | Synthesis §3 |

No zero-clearance or mismatched interfaces exist among the Phase 1 features. The Phase 4 strut-to-bore interfaces are pre-specified with the correct 0.2 mm sliding fit clearance per requirements.md. The Phase 2 joint interface is deferred and listed as TBD.

### Part 2 — Path Continuity

The lever in Phase 1 has no fluid channels, wire routes, or fastener paths. The mechanical force path (finger contact → struts → Phase 2 joint → release plate → collets) is verified below:

| Path | Segment | Start (Y in lever local) | Stop (Y in lever local) | Cross-section | Connects to next? |
|---|---|---|---|---|---|
| Force path | User contact on plate front face | Y = 0 | Y = 0 (contact surface) | 80×50 mm area | Yes — to plate body |
| Force path | Plate body (tension) | Y = 0 | Y = 4.0 mm | 80×50 mm solid plate | Yes — to strut bases |
| Force path | Strut TL (compression) | Y = 4.0 mm | Y = 94.0 mm | 6×6 mm solid | Yes — to Phase 2 joint |
| Force path | Strut TR (compression) | Y = 4.0 mm | Y = 94.0 mm | 6×6 mm solid | Yes — to Phase 2 joint |
| Force path | Strut BL (compression) | Y = 4.0 mm | Y = 94.0 mm | 6×6 mm solid | Yes — to Phase 2 joint |
| Force path | Strut BR (compression) | Y = 4.0 mm | Y = 94.0 mm | 6×6 mm solid | Yes — to Phase 2 joint |
| Force path | Phase 2 joint → release plate | Y = 94.0 mm | TBD (Phase 2) | TBD | TBD — Phase 2 scope |

Force path is continuous from Y=0 to Y=94 within the lever. The segment from Y=94 to the release plate is Phase 2 scope. No gaps or obstructions within the Phase 1 lever.

---

## 8. Rubric E — Assembly Feasibility Check

The lever is a free-standing single part in Phase 1. There is no assembly sequence for the lever itself — it is printed, removed from the build plate, and set aside until Phase 2.

**Phase 2 assembly check (informational):** The lever strut tips will be joined to the release plate struts. The joint geometry is Phase 2 work; feasibility is assessed in the Phase 2 specification.

**Phase 4 assembly check (informational):** The struts will be inserted through square bores cut into the pump tray and coupler tray. The struts are straight 6×6 mm prisms; insertion requires sliding the lever straight along the Y axis through both bores. This is feasible provided the bores are aligned and the 0.2 mm clearance is maintained. No tools required; the hand can push the lever through the bores from the front. The bores do not yet exist in Phase 1 — they are Phase 4 work. No Phase 1 action required.

**Disassembly:** The lever is a captive interior part per vision §3. It is not user-serviceable. Disassembly (for the cartridge as a unit) requires removing the top panel and sliding the interior assembly out — a Season 2/3 concern, not Phase 1.

---

## 9. Rubric F — Part Count Minimization

| Part pair | Permanently joined? | Move relative to each other? | Same material, printable as one? | Conclusion |
|---|---|---|---|---|
| Plate body + strut TL | Yes (printed as one) | No | Yes | Combined — correct |
| Plate body + strut TR | Yes (printed as one) | No | Yes | Combined — correct |
| Plate body + strut BL | Yes (printed as one) | No | Yes | Combined — correct |
| Plate body + strut BR | Yes (printed as one) | No | Yes | Combined — correct |

The lever is a single printed part. No further combination is possible — all sub-features are integrated. Decomposition document confirmed pass-through with no split. Piece count is at the minimum: 1.

The synthesis (§9, open question 3) raised the possibility of printing the struts as separate press-fit pins into the plate if 94 mm total height causes adhesion problems. This is a conditional split that would increase piece count from 1 to 5 and add tolerance stack and pull-out risk. The 80×50 mm plate footprint provides excellent adhesion at 94 mm height; the conditional split is not triggered.

---

## 10. Rubric G — FDM Printability

### Step 1 — Print Orientation

**Lever plate front face on the build plate (Y=0 face down). Struts extend upward in the +Z print direction.**

Rationale:
- The plate front face is the user contact surface. Printing it on the build plate gives the smoothest achievable FDM surface finish (build-plate-contact layer).
- The struts extend vertically in the print direction — no overhangs on any strut face.
- Compressive load on struts during squeeze acts along the strut length, which in this orientation is the Z print axis. FDM is strongest in compression along the layer axis (layers in compression, not tension). This is the mechanically correct orientation.
- Total build height: 94 mm (4 mm plate + 90 mm struts). Well within 320 mm build height.
- Build plate footprint: 80 mm × 65 mm. Fits within 325 mm × 320 mm single-nozzle build area with 245 mm × 255 mm margin.
- No functional constraint forces a different orientation.

In print coordinate terms: plate XZ plane on build plate; struts extend in the +Z print direction. Lever part-local Y axis aligns with print Z axis.

### Step 2 — Overhang Audit

Print orientation: lever plate front face down. Struts extend upward (+Z print direction).

| Surface / Feature | Angle from horizontal (print Z up) | Printable? | Resolution |
|---|---|---|---|
| Plate front face (Y=0) | 90° from horizontal (horizontal face, on build plate) | OK — on build plate |  |
| Plate rear face (Y=4) | 90° from horizontal (horizontal face, fully supported by plate body below it) | OK — fully supported |  |
| Plate side faces (X=0, X=80) | 0° from horizontal (vertical walls, no overhang) | OK |  |
| Plate top/bottom faces (Z=0, Z=65 in part frame — sides in print orientation) | 0° from horizontal (vertical walls, no overhang) | OK |  |
| Strut side faces (4 faces per strut, parallel to print Z) | 0° from horizontal (vertical walls) | OK |  |
| Strut top faces (Y=94 in part frame — strut tips, horizontal caps) | 90° from horizontal (horizontal face, fully supported by strut below) | OK — no overhang |  |
| Strut base junction (strut meets plate rear face) | Transition from horizontal plate to vertical strut — right-angle step, no cantilever | OK — fully supported |  |
| Perimeter corner radii (2.0 mm R on XZ corners) | In-plane curve parallel to print Z axis — vertical surface, no overhang | OK |  |
| Bottom chamfer (0.3 mm × 45° on Z=0 perimeter in part frame) | 45° from horizontal exactly — at or above the 45° printability limit | OK — at limit; acceptable |  |

No overhangs below 45° from horizontal anywhere in this geometry. No supports required.

### Step 3 — Wall Thickness Check

| Feature | Actual dimension | Minimum required | Pass? |
|---|---|---|---|
| Plate thickness | 4.0 mm | 1.2 mm (structural) | Pass — 3.3× minimum |
| Strut cross-section (solid — no walls) | 6.0 × 6.0 mm solid | 1.2 mm (structural) | Pass — solid, 5× minimum dimension |
| Plate material from strut bore edge to plate perimeter (X sides) | 5.9 mm | 1.2 mm | Pass |
| Plate material from strut bore edge to plate perimeter (Z top/bottom) | 1.9 mm | 1.2 mm | Pass — 1.6× minimum |

All wall thicknesses exceed minimum requirements by substantial margin.

### Step 4 — Bridge Span Check

No horizontal unsupported spans exist anywhere in this part. The plate is a solid horizontal slab on the build plate. The struts are vertical columns with no bridging geometry. No bridge spans to audit.

### Step 5 — Layer Strength Check

| Feature | Load type | Layer line orientation (relative to load) | Adequate? |
|---|---|---|---|
| Struts during squeeze | Compression along strut long axis | Layers stack along the strut length (parallel to load) — layers in compression | Yes — strongest FDM case |
| Strut-to-plate junction | Tension/bending if lever is misaligned | Layer lines run parallel to the plate face; the junction is a right-angle step; in-plane (XY print) material is strong | Yes — XY plane is strong |
| Plate body during squeeze | Tension (fingers pulling plate away from struts) | Layers parallel to plate face — tension is in-plane (XY print direction) | Yes — in-plane tension is strong |
| Plate body bending | Bending between strut attachment points (center of plate) | Layers parallel to plate; bending stress is in-plane | Yes |

No layer orientation conflict. All critical loads are oriented favorably relative to the print direction.

---

## 11. Rubric H — Feature Traceability

| Feature | Justification source | Specific reference |
|---|---|---|
| Plate body (80×65×4 mm) | Physical necessity — structural | Load-transfer body between user contact surface (Y=0) and strut attachment zone (Y=4). Width 80 mm and height 65 mm match the release plate dimensions so lever strut positions (Z=5.0 and Z=60.0) align with release plate strut positions in the assembly. Thickness 4 mm resists plate deflection under 30 N pull force (δ=0.063 mm). |
| Plate perimeter corner radii (2.0 mm) | Vision + physical necessity | Vision §2/§3: "This is a consumer appliance. It should look and feel like one." Consistent design language with release plate (concept.md §5: "2–3mm radii, consistent with the release plate's corner language"). Physical necessity (assembly): reduces snagging risk during lever travel past front panel hole edges. |
| Plate bottom chamfer (0.3 mm × 45°) | Physical necessity — manufacturing | Requirements.md §6: "Elephant's foot: first 0.2–0.3mm flares outward from bed adhesion. If the bottom face is a mating surface, add a 0.3mm×45° chamfer." The plate is printed face-down; the bottom perimeter edge is the build plate edge. |
| Strut TL (6×6×90 mm at X=9, Z=60) | Physical necessity — structural | Four struts required to transmit 60 N pull force (15 N each) and to provide anti-rotation stability during lever translation. TL position matches release plate strut TL (X=9.0, Z=60.0). Vision §3: "The lever itself is just a flat surface, with struts extending through the two interior panels." |
| Strut TR (6×6×90 mm at X=71, Z=60) | Physical necessity — structural | Same as TL. Matches release plate strut TR (X=71.0, Z=60.0). |
| Strut BL (6×6×90 mm at X=9, Z=5) | Physical necessity — structural | Same as TL. Matches release plate strut BL (X=9.0, Z=5.0). |
| Strut BR (6×6×90 mm at X=71, Z=5) | Physical necessity — structural | Same as TL. Matches release plate strut BR (X=71.0, Z=5.0). |

All features traced. No unjustified features found.

---

## 12. Bill of Materials

| Item | Material | Qty | Notes |
|---|---|---|---|
| Printed lever | PETG | 1 | Single print. No hardware, no inserts, no post-processing in Phase 1. |

---

## 13. Open Questions / Design Gaps

### DESIGN GAP: No lever pull travel stop in Phase 1

**Claim:** Lever travel is limited to 3.0 mm.
**Grounding feature required:** A physical stop on the lever or front panel that prevents >3.0 mm rearward travel.
**Current state:** No such feature exists on the lever in Phase 1. The de facto stop is the release plate fitting body shoulder (Zone 1 bore floor contact, per release plate specification). This is an indirect stop — it lives on the release plate and fitting bodies, not the lever. In normal use this is sufficient. In Phase 1 (free-standing lever, no mechanism connected) there is no stop.
**Action required:** Season 2 or Phase 2 — add a travel stop feature to the lever, the front panel, or the cartridge wall rails. Not in scope for Phase 1.

### Open Question 1 — Strut length

The 90 mm strut length is an estimate. Confirmed pending: (a) coupler tray synthesis establishing that tray's Y position in the cartridge, and (b) cartridge body synthesis confirming total interior depth. The strut tips at Y=94 mm are free-ended in Phase 1 — excess length has no Phase 1 consequence. Strut length should be verified before Phase 2 begins.

### Open Question 2 — Lever Y-position within cartridge

The inset depth of the lever front face behind the front panel face (range 5–15 mm) is not finalized until Season 2. Phase 1 is unaffected — the lever is a free-standing part with no positional constraint in the Y axis.

### Open Question 3 — Phase 2 strut joint Z offset accommodation

The lever center is at Z=25.0 mm in pump tray coordinates; the release plate center is at Z=34.3 mm — a 9.3 mm offset. The Phase 2 joint geometry must accommodate this misalignment. The lever strut tip positions (Y=94 in lever local) will not be coaxial with the release plate strut positions in Z. This is a known Phase 2 input, not a Phase 1 conflict.

---

## 14. What Is NOT in Scope (Phase 1)

| Feature | Phase |
|---|---|
| Dovetail or joint geometry at strut tips | Phase 2 |
| Strut bores in pump tray | Phase 4 |
| Strut bores in coupler tray | Phase 4 |
| Front panel hole geometry | Season 2 |
| Lever pull travel stop | Season 2 or Phase 2 |
| Spring pockets or return spring features | Season 4, Phase 12 |
| Surface texture on lever plate front face | Season 4, Phase 11 |
| Cartridge walls or enclosure | Season 2 |

---

## 15. CadQuery Generation Notes

This part is produced by a single CadQuery script. No sub-part composition.

**Operations in order:**
1. Create plate body: `box(80.0, 4.0, 50.0)` with origin at (0, 0, 0) in part local frame.
2. Fillet four vertical XZ-corner edges (Y-axis-parallel edges at the four XZ corners): R = 2.0 mm.
3. Chamfer the bottom perimeter edge at Z=0 (build plate edge in print orientation): 0.3 mm × 45°.
4. Add Strut TL: `box(6.0, 90.0, 6.0)` positioned with center at X=9.0, Y=(4.0 + 45.0)=49.0, Z=40.0 — i.e., center of strut in Y is at Y=4+(90/2)=49, union to plate body.
5. Add Strut TR: same dimensions, center at X=71.0, Y=49.0, Z=40.0.
6. Add Strut BL: same dimensions, center at X=9.0, Y=49.0, Z=10.0.
7. Add Strut BR: same dimensions, center at X=71.0, Y=49.0, Z=10.0.

**Strut Y center for CadQuery:** Each strut starts at Y=4.0 (plate rear face) and ends at Y=94.0. The CadQuery box center in Y = 4.0 + 90.0/2 = 49.0 mm from plate origin.

**CadQuery coordinate note:** The part local frame places Y=0 at the front face (the face that sits on the build plate). In CadQuery the box origin convention should be confirmed in the generation script — the above coordinates assume the CadQuery origin matches the part local frame origin (bottom-left-front corner).

**Print orientation note for slicer:** Place the part with Y=0 face on the build plate. In the slicer this face is the bottom. Struts point upward. No brim required; no supports required.
