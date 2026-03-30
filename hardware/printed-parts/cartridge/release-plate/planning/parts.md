# Release Plate — Parts Specification

**Pipeline step:** 4b — Parts Specification
**Input documents:** spatial-resolution.md, synthesis.md, concept.md, decomposition.md, john-guest-union/geometry-description.md, requirements.md, vision.md

---

## 1. Part Summary

| Field | Value |
|---|---|
| Part name | Release plate |
| Part type | Single printed PETG part |
| Function | Sliding actuator that simultaneously depresses the rear-facing collets of four PP0408W quick-connect fittings, releasing the cartridge from the enclosure dock tube stubs |
| Material | PETG |
| Envelope (W × H × D) | 137.2 mm × 68.6 mm × 95.0 mm (plate 137.2×68.6×5; struts extend 90 mm from front face) |
| Print orientation | Front face DOWN on build plate (XZ plane on build plate). Guide pins and struts extend upward (+Y print direction). All stepped bore features open downward toward build plate. |
| Piece count | 1 |
| Fasteners | None |
| Sub-assemblies | None |

**Coordinate system (part local frame):**

| Axis | Direction | Range |
|---|---|---|
| X | Width, left to right | 0 → 137.2 mm |
| Y | Depth, front (user-facing) to rear (fitting-facing) | 0 → 5.0 mm |
| Z | Height, bottom to top | 0 → 68.6 mm |

Origin: bottom-left-front corner of the plate (the corner at X=0, Y=0, Z=0).
Y=0 = front face (pull surface, faces user, sits on build plate in print orientation).
Y=5 = rear face (bore-entry face, faces the PP0408W fittings in assembled cartridge).

---

## What Changed from v2

**v2** placed the 4 bores in a 2×2 grid (two columns at X=9.0 and X=71.0, two rows at Z=47.5 and Z=17.5) on an 80×65mm plate.

**v3** moves all 4 bores into a single horizontal row (1×4) at Z=34.3mm, with centers at X=43.1, 60.1, 77.1, 94.1mm, matching the coupler tray v3 layout exactly. The plate footprint is updated to 137.2×68.6mm to match the coupler tray footprint. The 4 struts are repositioned to the four corners of the plate, clear of all bore outer circles. The 2 guide pins are repositioned diagonally to match the new plate geometry.

---

## 2. Mechanism Narrative (Rubric A)

### What the user sees and touches

The release plate is invisible during normal use. It lives entirely inside a rectangular pocket on the front face of the cartridge body — a clean, flat-bottomed recess that runs across most of the cartridge front face width. From the user's perspective, the cartridge front face shows one designed inset zone. The surrounding rim of the cartridge front face is the palm surface. The floor of the inset is the plate's front face — the pull surface. Both are flat. The inset is 10 mm deep (plate front face is 10 mm behind the cartridge body front face). The gap between the plate perimeter and the pocket walls is 0.6–1.0 mm uniform, with sharp edges on both sides. This gap is barely visible from straight-on and recedes into shadow from the normal viewing angle. Nothing about the exterior communicates that the floor of the inset is a separate moving part.

### What moves

**Moving:** The release plate — a single flat PETG part — translates 0–3.0 mm in the −Y direction (toward the user) during actuation. It is the only moving part.

**Stationary:** The cartridge body (including the rear wall holding the four PP0408W fittings, the guide pin bores, and the spring pockets). The four PP0408W fittings are pressed into the cartridge body rear wall and do not move.

### What converts the motion

There is no mechanical advantage conversion. The user's finger pull force is transmitted directly through the plate body to the collet contact faces. The plate is a rigid translation link — it converts finger pull force into collet depression force 1:1 with no amplification, reduction, or direction change.

Force path: user finger pads contact the plate front face (Y=0) → force transmits through the 5.0 mm plate body in tension along Y → annular lip faces at the Zone 2→Zone 3 step transition (Y=1.6 mm) contact the PP0408W collet annular end faces → collets translate inward (in the +Y direction relative to the cartridge, away from the user) → collet spring compression → collet gripper teeth release the dock tube stubs.

### What constrains the plate

**Rotational constraint:** Two integral guide pins (Pin 1 at X=5.0, Z=63.6; Pin 2 at X=132.2, Z=5.0) extend 30.0 mm from the plate rear face (Y=5.0 to Y=35.0 in part frame) and slide in matched cylindrical bores in the cartridge body. The diagonal placement of the two pins prevents any rotation of the plate about the Y axis (or any other axis) during translation. The 0.5 mm designed diametric clearance between pin OD (5.0 mm) and bore ID (5.5 mm) limits maximum tilt.

**Translational constraint (over-travel):** The Zone 1 outer bore floor acts as a hard stop. When the plate has traveled 1.33 mm toward the user, the Zone 1 bore floor (at Y=3.6 mm from front face = Y=1.4 mm depth from rear face) contacts the PP0408W body-end shoulder (15.10 mm OD annular face). The fitting body becomes the over-travel stop.

**Rearward limit:** At rest, the plate is held at its resting position by the return springs. The annular lip face at Y=1.6 mm rests against the collet end faces (which are spring-loaded outward). The plate cannot travel rearward (+Y) beyond its rest position because the collets prevent it.

### Return force

Two compression springs, one per guide pin, provide the return force. Each spring sits in an 8 mm diameter × 10 mm deep pocket in the cartridge body rear wall, concentric with the corresponding guide pin bore. The spring bears against the flat plate rear face (Y=5.0 mm, no feature on the plate required).

### The user's physical interaction

The user approaches the installed cartridge with one hand, palm up. The palm presses against the cartridge body front face rim. The fingers curl into the 10 mm deep pocket and contact the plate front face. The user squeezes: fingers pull, palm pushes. Resistance builds as the four collet springs compress. At approximately 1.33 mm of plate travel, all four collets simultaneously clear their internal stops — the gripping teeth release the dock tube stubs — and the user feels and hears four simultaneous clicks. The resistance drops sharply. The user's hand continues pulling the cartridge forward out of the bay on its protruding tracks.

---

## 3. Feature List

Every feature is described with: name, operation type (Add = material added to blank, Remove = material removed), exact dimensions, position in part local frame, and justification.

### Feature 1 — Plate Body

| Field | Value |
|---|---|
| Operation | Add (base body) |
| Shape | Rectangular prism |
| Width (X) | 137.2 mm |
| Height (Z) | 68.6 mm |
| Depth (Y) | 5.0 mm |
| Position | Fills entire part envelope: X: 0→137.2, Y: 0→5.0, Z: 0→68.6 |
| Justification | Width 137.2 mm and height 68.6 mm match the coupler tray v3 footprint so both parts align on the same cartridge axis. Depth 5.0 mm accommodates Zone 1 (1.4 mm) + Zone 2 (2.0 mm) + Zone 3 (1.6 mm) exactly. |

### Feature 2 — Perimeter Corner Radii

| Field | Value |
|---|---|
| Operation | Remove (blend, CadQuery fillet) |
| Shape | Convex cylindrical fillet, R = 2.0 mm |
| Affected edges | The four vertical edges of the plate parallel to Y, at the four XZ corners: (X=0, Z=0), (X=137.2, Z=0), (X=0, Z=68.6), (X=137.2, Z=68.6). Each edge runs from Y=0 to Y=5.0. |
| Radius | 2.0 mm |
| Justification | Vision §3 design language: rounded corners read as a designed part. Also manufacturing: the 2.0 mm corner radius must match the cartridge body pocket interior corner radius to maintain the designed uniform 0.6–1.0 mm parting line gap at corners. |

### Feature 3 — Pull Edge Radius (Perimeter Front Face Edge)

| Field | Value |
|---|---|
| Operation | Remove (blend, CadQuery fillet) |
| Shape | Convex quarter-circle fillet, R = 3.0 mm |
| Affected edges | All four perimeter edges at the front face plane (Y=0): left edge (X=0, Y=0, Z: 0→68.6); right edge (X=137.2, Y=0, Z: 0→68.6); bottom edge (Z=0, Y=0, X: 0→137.2); top edge (Z=68.6, Y=0, X: 0→137.2). |
| Radius | 3.0 mm |
| Justification | Tactile comfort: the radius is on the rearward-facing edge the finger pads bear against during the pull stroke. This surface must not feel sharp. requirements.md §6 dimensional accuracy elephant's foot requirement is fully satisfied by this 3.0 mm radius. |

### Feature 4 — Stepped Bore A (H1)

| Field | Value |
|---|---|
| Operation | Remove (three-diameter concentric bore from rear face through front face) |
| Center position (X, Z) | X = 43.1 mm, Z = 34.3 mm |
| Bore axis | Parallel to Y axis |
| Zone 1 — Outer bore | Ø 15.60 mm; depth from rear face (Y=5.0): 1.4 mm; Y range: 5.0 → 3.6 mm |
| Zone 2 — Inner lip bore | Ø 10.07 mm; depth: 2.0 mm beyond Zone 1; Y range: 3.6 → 1.6 mm |
| Zone 3 — Tube through-hole | Ø 6.50 mm; depth: 1.6 mm through remaining plate; Y range: 1.6 → 0.0 mm (exits front face) |
| Annular lip face | Flat annular face at Y=1.6 mm; inner radius 3.25 mm (Zone 3); outer radius 5.035 mm (Zone 2). This is the collet contact face. |
| Hard stop face | Flat annular face at Y=3.6 mm (Zone 1 floor); inner radius 5.035 mm (Zone 2); outer radius 7.8 mm (Zone 1); contacts PP0408W body-end shoulder at full plate travel. |
| Wall to left plate edge | 43.1 − 7.8 = 35.3 mm — well exceeds 1.2 mm structural minimum |
| Justification | Same bore geometry as v2. Position X=43.1, Z=34.3 matches coupler tray v3 hole H1 exactly. The release plate must align with the coupler tray so the collet interfaces register correctly. |

### Feature 5 — Stepped Bore B (H2)

Identical geometry to Feature 4.

| Center position (X, Z) | X = 60.1 mm, Z = 34.3 mm |
| All bore zone dimensions | Same as Feature 4 (Zones 1, 2, 3 — all diameters and depths identical) |
| Inter-bore clearance to A | 60.1 − 43.1 = 17.0 mm c-c; edge-to-edge = 17.0 − 15.60 = 1.4 mm — no interference |
| Justification | Same as Feature 4. Position matches coupler tray v3 hole H2. |

### Feature 6 — Stepped Bore C (H3)

Identical geometry to Feature 4.

| Center position (X, Z) | X = 77.1 mm, Z = 34.3 mm |
| All bore zone dimensions | Same as Feature 4 |
| Inter-bore clearance to B | 77.1 − 60.1 = 17.0 mm c-c; edge-to-edge = 17.0 − 15.60 = 1.4 mm — no interference |
| Justification | Same as Feature 4. Position matches coupler tray v3 hole H3. |

### Feature 7 — Stepped Bore D (H4)

Identical geometry to Feature 4.

| Center position (X, Z) | X = 94.1 mm, Z = 34.3 mm |
| All bore zone dimensions | Same as Feature 4 |
| Inter-bore clearance to C | 94.1 − 77.1 = 17.0 mm c-c; edge-to-edge = 17.0 − 15.60 = 1.4 mm — no interference |
| Wall to right plate edge | 137.2 − 94.1 − 7.8 = 35.3 mm — well exceeds 1.2 mm structural minimum |
| Justification | Same as Feature 4. Position matches coupler tray v3 hole H4. |

**Bore pattern summary (1×4 row):**

| Bore | Center X | Center Z | Coupler Tray Hole |
|---|---|---|---|
| A | 43.1 mm | 34.3 mm | H1 |
| B | 60.1 mm | 34.3 mm | H2 |
| C | 77.1 mm | 34.3 mm | H3 |
| D | 94.1 mm | 34.3 mm | H4 |

All four bores at Z=34.3mm (plate vertical midpoint at Z=34.3mm). 17.0 mm center-to-center spacing along X. Row centered at X=68.6mm (plate horizontal midpoint).

**Inter-bore clearances (edge-to-edge, outer bore Ø15.60 mm):**
- All adjacent pairs: 17.0 − 15.60 = 1.4 mm — no interference
- Non-adjacent pairs (34mm spacing): 34.0 − 15.60 = 18.4 mm — no interference

### Feature 8 — Guide Pin 1 (Top-Left)

| Field | Value |
|---|---|
| Operation | Add (integral cylindrical boss protruding from rear face) |
| Shape | Right circular cylinder |
| Diameter | 5.0 mm (OD) |
| Center position (X, Z) | X = 5.0 mm, Z = 63.6 mm |
| Base Y | Y = 5.0 mm (at plate rear face) |
| Tip Y | Y = 35.0 mm |
| Length from rear face | 30.0 mm |
| Tip geometry | Flat circular end face, Ø 5.0 mm, at Y = 35.0 mm |
| Nearest bore (A) surface gap | Distance (5.0, 63.6) to (43.1, 34.3): sqrt(38.1²+29.3²) = sqrt(1452+858) = 48.1 mm center-to-center; minus pin radius 2.5 mm and bore outer radius 7.8 mm = 37.8 mm gap — well exceeds 1.2 mm structural minimum |
| Distance to left plate edge | 5.0 − 2.5 = 2.5 mm — exceeds 1.2 mm structural minimum |
| Distance to top plate edge | 68.6 − 63.6 − 2.5 = 2.5 mm — exceeds 1.2 mm structural minimum |
| Justification | Guides plate translation in −Y; prevents rotation. Diagonal placement with Pin 2 provides anti-rotation moment arm. 30.0 mm length provides adequate bore engagement at all travel positions. |

### Feature 9 — Guide Pin 2 (Bottom-Right)

| Field | Value |
|---|---|
| Operation | Add (integral cylindrical boss protruding from rear face) |
| Diameter | 5.0 mm (OD) |
| Center position (X, Z) | X = 132.2 mm, Z = 5.0 mm |
| Base Y | Y = 5.0 mm |
| Tip Y | Y = 35.0 mm |
| Length from rear face | 30.0 mm |
| Tip geometry | Flat circular end face, Ø 5.0 mm, at Y = 35.0 mm |
| Nearest bore (D) surface gap | Distance (132.2, 5.0) to (94.1, 34.3): sqrt(38.1²+29.3²) = 48.1 mm center-to-center; minus 2.5+7.8 = 37.8 mm gap — well exceeds 1.2 mm structural minimum |
| Distance to right plate edge | 137.2 − 132.2 − 2.5 = 2.5 mm — exceeds 1.2 mm structural minimum |
| Distance to bottom plate edge | 5.0 − 2.5 = 2.5 mm — exceeds 1.2 mm structural minimum |
| Justification | Same as Feature 8. Diagonal pair (Pin 1 top-left, Pin 2 bottom-right) provides the anti-rotation moment arm. |

**Pin geometry summary:**

| Pin | Center (X, Z) | OD | Base Y | Tip Y | Length |
|---|---|---|---|---|---|
| Pin 1 | (5.0, 63.6) | 5.0 mm | 5.0 mm | 35.0 mm | 30.0 mm |
| Pin 2 | (132.2, 5.0) | 5.0 mm | 5.0 mm | 35.0 mm | 30.0 mm |

Pin center diagonal: sqrt((132.2−5.0)² + (5.0−63.6)²) = sqrt(127.2²+58.6²) = sqrt(16180+3434) = sqrt(19614) = 140.1 mm.

### Feature 10 — Strut TL (Top-Left)

| Field | Value |
|---|---|
| Operation | Add (rectangular boss protruding from front face) |
| Shape | Rectangular prism |
| Cross-section (X × Z) | 6.0 mm × 6.0 mm |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 10.0 mm, Z = 63.6 mm |
| Box extents | X: 7.0→13.0, Y: −90.0→0.0, Z: 60.6→66.6 |
| Base Y | Y = 0.0 mm (front face of plate) |
| Tip Y | Y = −90.0 mm (plain square end, no joinery) |
| Nearest bore (A) clearance | Bore A center (43.1, 34.3); strut nearest corner at (13.0, 60.6); distance = sqrt((43.1−13.0)²+(60.6−34.3)²) = sqrt(906+691) = sqrt(1597) = 40.0 mm; minus bore outer radius 7.8 mm = 32.2 mm gap — no interference |
| Nearest pin (Pin 1) | Pin 1 at (5.0, 63.6); strut center at (10.0, 63.6) — different X, no Y overlap (pin extends in +Y, strut extends in −Y from plate) — no interference |
| Distance to top plate edge | 68.6 − 66.6 = 2.0 mm to top edge — strut does not exceed plate |
| Justification | Corner strut position is well clear of all 4 bores. Struts connect to lever (Season 3); corner placement maximizes moment arm for anti-rotation during actuation. |

### Feature 11 — Strut TR (Top-Right)

| Field | Value |
|---|---|
| Operation | Add (rectangular boss protruding from front face) |
| Shape | Rectangular prism |
| Cross-section (X × Z) | 6.0 mm × 6.0 mm |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 127.2 mm, Z = 63.6 mm |
| Box extents | X: 124.2→130.2, Y: −90.0→0.0, Z: 60.6→66.6 |
| Base Y | Y = 0.0 mm |
| Tip Y | Y = −90.0 mm (plain square end) |
| Nearest bore (D) clearance | Bore D center (94.1, 34.3); strut nearest corner at (124.2, 60.6); distance = sqrt((124.2−94.1)²+(60.6−34.3)²) = sqrt(906+691) = 40.0 mm; minus 7.8 mm = 32.2 mm gap — no interference |
| Nearest pin (Pin 2) | Pin 2 at (132.2, 5.0); strut at Z=63.6 — different Z, no overlap |
| Justification | Mirror of Strut TL about X=68.6. |

### Feature 12 — Strut BL (Bottom-Left)

| Field | Value |
|---|---|
| Operation | Add (rectangular boss protruding from front face) |
| Shape | Rectangular prism |
| Cross-section (X × Z) | 6.0 mm × 6.0 mm |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 10.0 mm, Z = 5.0 mm |
| Box extents | X: 7.0→13.0, Y: −90.0→0.0, Z: 2.0→8.0 |
| Base Y | Y = 0.0 mm |
| Tip Y | Y = −90.0 mm (plain square end) |
| Nearest bore (A) clearance | Bore A center (43.1, 34.3); strut nearest corner at (13.0, 8.0); distance = sqrt((43.1−13.0)²+(34.3−8.0)²) = sqrt(906+692) = sqrt(1598) = 40.0 mm; minus bore outer radius 7.8 mm = 32.2 mm gap — no interference |
| Nearest pin (Pin 1) | Pin 1 at (5.0, 63.6); strut at Z=5.0 — different Z; no overlap |
| Justification | Mirror of Strut TL about Z=34.3. Together with TL, the left strut pair spans 58.6 mm vertically for anti-rotation stability. |

### Feature 13 — Strut BR (Bottom-Right)

| Field | Value |
|---|---|
| Operation | Add (rectangular boss protruding from front face) |
| Shape | Rectangular prism |
| Cross-section (X × Z) | 6.0 mm × 6.0 mm |
| Length (Y) | 90.0 mm |
| Center position (X, Z) | X = 127.2 mm, Z = 5.0 mm |
| Box extents | X: 124.2→130.2, Y: −90.0→0.0, Z: 2.0→8.0 |
| Base Y | Y = 0.0 mm |
| Tip Y | Y = −90.0 mm (plain square end) |
| Nearest bore (D) clearance | Bore D center (94.1, 34.3); strut nearest corner at (124.2, 8.0); distance = sqrt((124.2−94.1)²+(34.3−8.0)²) = sqrt(906+692) = 40.0 mm; minus 7.8 mm = 32.2 mm gap — no interference |
| Justification | Mirror of Strut BL about X=68.6. Completes the 4-strut corner pattern. |

**Strut geometry summary:**

| Strut | Center (X, Z) | Cross-section | Base Y | Tip Y | Length |
|---|---|---|---|---|---|
| TL (Top-Left) | (10.0, 63.6) | 6.0 × 6.0 mm | 0.0 mm | −90.0 mm | 90.0 mm |
| TR (Top-Right) | (127.2, 63.6) | 6.0 × 6.0 mm | 0.0 mm | −90.0 mm | 90.0 mm |
| BL (Bottom-Left) | (10.0, 5.0) | 6.0 × 6.0 mm | 0.0 mm | −90.0 mm | 90.0 mm |
| BR (Bottom-Right) | (127.2, 5.0) | 6.0 × 6.0 mm | 0.0 mm | −90.0 mm | 90.0 mm |

Strut horizontal spacing (TL↔TR or BL↔BR): 117.2 mm center-to-center.
Strut vertical spacing (TL↔BL or TR↔BR): 58.6 mm center-to-center.
All four struts clear all bore outer circles by ≥32.2 mm minimum. No interference.

### Features NOT Present (by explicit design decision)

| Absent feature | Reason |
|---|---|
| Elephant's foot chamfer (0.3 mm × 45°) | The 3.0 mm pull edge radius (Feature 3) applied to all four front-face perimeter edges fully satisfies requirements.md §6 elephant's foot requirement. No separate chamfer needed. |
| Spring pockets | Springs sit in pockets in the cartridge body rear wall, not in the plate. Plate rear face (Y=5.0 mm) is the spring contact surface — flat, no feature required. |
| Embossed texture on pull surface | The front face is smooth (satin PETG as-printed). |
| Labels, text, graphics | vision.md §3: the mechanism is hidden. No user-facing information on the plate. |
| Retention tabs or service features | vision.md §3: the cartridge is a black box. The plate is not user-serviceable. |
| Strut bores in interior plates | Phase 4 (vision.md build sequence item 12–13). Not in this version. |
| Split geometry | Not in scope for this part. |
| Rail tabs/slots | Season 2 (vision.md Phase 6). |

---

## 4. Interface Table (Rubric D)

### Interface 1: Plate Zone 2 bore (inner lip) ↔ PP0408W collet OD

| Dimension | Plate side | PP0408W side | Clearance | Source |
|---|---|---|---|---|
| Inner lip bore Ø | 10.07 mm | Collet OD 9.57 mm | 0.50 mm diametric (0.25 mm radial) | Plate: spatial-resolution.md §3.3; Fitting: geometry-description.md caliper-verified |
| Zone 2 axial depth | 2.0 mm | Collet engagement needed ≥ 2.0 mm | Exactly met | synthesis.md §3 |

### Interface 2: Plate Zone 1 bore (outer) ↔ PP0408W body-end OD (hard stop)

| Dimension | Plate side | PP0408W side | Clearance | Source |
|---|---|---|---|---|
| Outer bore Ø | 15.60 mm | Body-end OD 15.10 mm | 0.50 mm diametric (0.25 mm radial) | Plate: spatial-resolution.md §3.3; Fitting: geometry-description.md caliper-verified |
| Zone 1 depth from rear face | 1.4 mm | Collet travel to release ~1.33 mm | 0.07 mm over-travel margin before hard stop | geometry-description.md; synthesis.md §3 |

### Interface 3: Plate Zone 3 through-hole ↔ 1/4" tube OD + collet annular face

| Dimension | Plate side | Tube / fitting side | Clearance / contact | Source |
|---|---|---|---|---|
| Through-hole Ø | 6.50 mm | Tube OD 6.30 mm | 0.20 mm diametric tube clearance | Plate: spatial-resolution.md; Tube: geometry-description.md |
| Through-hole Ø vs collet ID | 6.50 mm bore | Collet ID 6.69 mm | 6.50 < 6.69 → plate annular lip contacts collet face ✓ | geometry-description.md |

### Interface 4: Plate guide pin OD ↔ Cartridge body guide bore ID

| Dimension | Plate side (pin) | Cartridge body side (bore) | Clearance | Source |
|---|---|---|---|---|
| Pin OD | 5.0 mm designed | 5.5 mm designed bore ID | 0.5 mm diametric designed | spatial-resolution.md §3.5; synthesis.md §3 |
| Pin length | 30.0 mm from rear face | Bore depth ≥ 30.0 mm | 27 mm retained at full stroke | spatial-resolution.md §3.5 |
| Pin 1 center | (X=5.0, Z=63.6) | Bore center at matching position | ±0.2 mm positional (printer XY accuracy) | spatial-resolution.md §3.5 |
| Pin 2 center | (X=132.2, Z=5.0) | Bore center at matching position | ±0.2 mm positional | spatial-resolution.md §3.5 |

### Interface 5: Plate bore pattern ↔ Coupler tray v3 coupler positions

| Bore | Release plate center (X, Z) | Coupler tray v3 hole (X, Z) | Match |
|---|---|---|---|
| A (H1) | (43.1, 34.3) | (43.1, 34.3) | Exact |
| B (H2) | (60.1, 34.3) | (60.1, 34.3) | Exact |
| C (H3) | (77.1, 34.3) | (77.1, 34.3) | Exact |
| D (H4) | (94.1, 34.3) | (94.1, 34.3) | Exact |

The release plate bore centers align exactly with the coupler tray v3 coupler hole centers so the plate presses the collets that sit in the coupler tray's couplers.

### Interface 6: Plate rear face (Y=5.0) ↔ Return springs

| Dimension | Plate side | Cartridge body side | Notes |
|---|---|---|---|
| Spring contact surface | Flat rear face, Y=5.0 mm, no feature | Spring end coil; spring OD 7–8 mm, coil wraps guide pin | No plate feature needed |

### Interface 7: Plate front face (Y=0) ↔ Cartridge body pocket floor (at rest)

| Dimension | Plate side | Cartridge body side | Notes |
|---|---|---|---|
| Plate dimensions | 137.2 mm × 68.6 mm nominal (before corner radii) | Pocket inner = plate + 0.6–1.0 mm on each side | Designed parting line gap |
| Plate corner radius | 2.0 mm | Pocket corner radius = 2.0 mm | Must match to maintain uniform gap at corners |

---

## 5. FDM Check

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Base plate — all walls | Overhang | All faces vertical or on build plate | ≤45° | Yes |
| Base plate thickness | Wall thickness | 5mm | 1.2mm structural min | Yes |
| Bore wall to left/right edge | Thickness | 35.3mm | 1.2mm structural min | Yes |
| Adjacent bore wall | Gap | 1.4mm edge-to-edge (outer bore) | ≥0mm no intersection | Yes |
| Guide pin wall thickness | (5mm OD pin from rear face) | Solid cylinder on flat face | — | Yes |
| Strut cross-section | Wall thickness | 6mm × 6mm | 1.2mm structural min | Yes |
| Strut clearance to bores | Gap | 32.2mm minimum | ≥0mm no intersection | Yes |
| Holes — orientation | Print as vertical cylinders | Axis parallel to print Z (Y axis) | — | Yes |

No overhangs. No supports required.

---

## 6. Assembly Sequence

1. **Before cartridge assembly:** The release plate is a complete printed part. No sub-assembly.

2. **Insert guide pins into cartridge body bores:** Align the two guide pins with the two 5.5 mm bores in the cartridge body rear-wall structure. Lower the plate until the pins are fully seated.

3. **Seat return springs (cartridge body operation — for context):** Place one compression spring in each spring pocket concentric with each guide pin bore before inserting the plate.

4. **Insert plate over springs:** Lower the plate into the cartridge body pocket with the guide pins aligned to the bores.

5. **Capture by cartridge body front wall:** The cartridge body front wall is assembled last, capturing the plate inside the pocket.

6. **Verification:** With the cartridge assembled, the plate should translate smoothly 0–3 mm in the −Y direction when pressed, and return to the rest position when released.

---

## 7. Rubric Results

### Rubric A — Mechanism Narrative

**Result: PASS**

All five rubric requirements satisfied: user sees/touches described; what moves named; force conversion named; constraints named and dimensioned; return force described; user interaction described with tactile endpoint.
