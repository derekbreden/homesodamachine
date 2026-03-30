# Release Plate — Spatial Resolution

**Step:** 4s — Spatial Resolution
**Input:** synthesis.md, concept.md, decomposition.md, guide-geometry.md, collet-release-force.md, john-guest-union geometry-description.md
**Output:** Every spatial relationship resolved to concrete coordinates in the part's local reference frame. No downstream math required.

---

## 1. System-Level Placement

The release plate is a captive sliding part inside the cartridge body. It lives in the pocket formed by the cartridge body front wall. Its position in the cartridge assembly changes during actuation: at rest, the plate user-facing face sits 10 mm behind the cartridge body front face plane; when fully actuated, the plate has translated 3 mm toward the user (user-facing face is 7 mm behind the cartridge front face plane).

```
Mechanism:  Release plate (cartridge sub-component)
Parent:     Cartridge body pocket
Orientation: No rotation. Plate X-axis = cartridge width axis.
             Plate Y-axis = cartridge front-to-back depth axis (positive = rearward).
             Plate Z-axis = cartridge height axis.
At rest:    Plate user-facing face (Y=5 in part frame) is 10 mm behind cartridge body front face.
Actuated:   Plate translates 0→3 mm toward user (+Y direction in part frame).
```

This section is for context only. All downstream dimensions are in the part's local frame below.

---

## 2. Part Reference Frame

```
Part:       Release plate (single printed PETG part)
Origin:     Plate bottom-left corner at fitting-facing face
X:          Plate width, left to right, 0 → 80.0 mm
Y:          Plate depth (through thickness), fitting-facing to user-facing, 0 → 5.0 mm
            Y=0 = fitting-facing face (tube exit side, on build plate in print orientation)
            Y=5 = user-facing face (stepped bore entry, pull surface)
Z:          Plate height, bottom to top, 0 → 65.0 mm

Print orientation: Fitting-facing face DOWN on build plate (XZ plane on build plate).
                   Guide pins extend upward in +Y (toward top of printed part).
                   Stepped bore counterbores open upward away from build plate.
```

---

## 3. Derived Geometry

### 3.1 Plate Envelope

All coordinates are in the plate local frame defined in Section 2.

| Dimension | Value | Source and Derivation |
|---|---|---|
| Width (X) | 80.0 mm | concept.md §7 dimensional correction: 75mm nominal is insufficient — outer bore edge at extreme horizontal position lands at 38.8mm from center vs. 37.5mm half-width at 75mm; 80mm provides 1.20mm wall (exactly 3 perimeters). |
| Depth / Thickness (Y) | 5.0 mm | synthesis.md §4: provides all three zone depths plus a through-plate clearance section. |
| Height (Z) | 65.0 mm | synthesis.md §4 working value. Wall check below confirms ≥1.2mm on all sides. |

**Envelope corner coordinates (plate local frame):**

| Corner | X | Y | Z |
|---|---|---|---|
| Bottom-left-fitting | 0 | 0 | 0 |
| Bottom-right-fitting | 80.0 | 0 | 0 |
| Top-left-fitting | 0 | 0 | 65.0 |
| Top-right-fitting | 80.0 | 0 | 65.0 |
| Bottom-left-user | 0 | 5.0 | 0 |
| Bottom-right-user | 80.0 | 5.0 | 0 |
| Top-left-user | 0 | 5.0 | 65.0 |
| Top-right-user | 80.0 | 5.0 | 65.0 |

---

### 3.2 Stepped Bore Positions — Center Coordinates

Four stepped bores, identically configured, arranged in a 62 mm horizontal × 30 mm vertical center-to-center rectangle centered on the plate.

**Bore pattern center:** X = 40.0 mm, Z = 32.5 mm (= plate center)

**Bore center coordinates (X, Z) in plate local frame:**

| Bore | Pump | Role | X (mm) | Z (mm) |
|---|---|---|---|---|
| A | Pump 1 (left) | Inlet | 9.0 | 47.5 |
| B | Pump 1 (left) | Outlet | 9.0 | 17.5 |
| C | Pump 2 (right) | Inlet | 71.0 | 47.5 |
| D | Pump 2 (right) | Outlet | 71.0 | 17.5 |

**Derivation:**
- Horizontal offset: ±62.0/2 = ±31.0 mm from plate center X (40.0). Left column: 40.0 − 31.0 = 9.0 mm. Right column: 40.0 + 31.0 = 71.0 mm.
- Vertical offset: ±30.0/2 = ±15.0 mm from plate center Z (32.5). Top row: 32.5 + 15.0 = 47.5 mm. Bottom row: 32.5 − 15.0 = 17.5 mm.
- Source: synthesis.md §5 fitting layout.

**Wall checks — outer bore (Ø15.60 mm, radius 7.8 mm) to plate edges:**

| Bore | Left wall | Right wall | Bottom wall | Top wall | Min required |
|---|---|---|---|---|---|
| A (9.0, 47.5) | 9.0 − 7.8 = **1.20 mm** | 80.0 − 9.0 − 7.8 = 63.2 mm | 47.5 − 7.8 = 39.7 mm | 65.0 − 47.5 − 7.8 = 9.7 mm | 1.2 mm |
| B (9.0, 17.5) | 9.0 − 7.8 = **1.20 mm** | 80.0 − 9.0 − 7.8 = 63.2 mm | 17.5 − 7.8 = 9.7 mm | 65.0 − 17.5 − 7.8 = 39.7 mm | 1.2 mm |
| C (71.0, 47.5) | 71.0 − 7.8 = 63.2 mm | 80.0 − 71.0 − 7.8 = **1.20 mm** | 47.5 − 7.8 = 39.7 mm | 65.0 − 47.5 − 7.8 = 9.7 mm | 1.2 mm |
| D (71.0, 17.5) | 71.0 − 7.8 = 63.2 mm | 80.0 − 71.0 − 7.8 = **1.20 mm** | 17.5 − 7.8 = 9.7 mm | 65.0 − 17.5 − 7.8 = 39.7 mm | 1.2 mm |

All walls meet the 1.2 mm structural minimum. The left wall of bores A and B, and the right wall of bores C and D, are exactly 1.20 mm — which is the minimum acceptable (= 3 perimeters at 0.4 mm nozzle). This confirms 80.0 mm is the correct minimum width; any narrower would violate the structural wall requirement.

**Inter-bore edge-to-edge clearances:**

| Direction | Pair | Center-to-center | Edge-to-edge | Min required |
|---|---|---|---|---|
| Horizontal | A→C or B→D | 62.0 mm | 62.0 − 15.60 = 46.4 mm | 1.2 mm |
| Vertical | A→B or C→D | 30.0 mm | 30.0 − 15.60 = 14.4 mm | 1.2 mm |

No inter-bore interference.

---

### 3.3 Stepped Bore Geometry — Depth Zones

All four bores are identical. The bores open from the **user-facing face** (Y = 5.0 mm) and break through the **fitting-facing face** (Y = 0 mm). Zone boundaries are given as Y-coordinates.

**Zone boundary table (same for all 4 bores):**

| Zone | Diameter | Y-start (user-facing end) | Y-end (fitting-facing end) | Axial depth of zone | Depth from user-facing face |
|---|---|---|---|---|---|
| Zone 1 — outer bore (body-end cradle) | Ø 15.60 mm | Y = 5.0 mm | Y = 3.6 mm | 1.4 mm | 0 → 1.4 mm |
| Zone 2 — inner lip (collet hugger) | Ø 10.07 mm | Y = 3.6 mm | Y = 1.6 mm | 2.0 mm | 1.4 → 3.4 mm |
| Zone 3 — tube clearance through-hole | Ø 6.50 mm | Y = 1.6 mm | Y = 0 mm | 1.6 mm | 3.4 → 5.0 mm (through-plate) |

**Zone depth derivation:**
- Zone 1 depth (1.4 mm): nominal midpoint of the 1.3–1.5 mm range from synthesis.md §3 and guide-geometry.md §6. Sets the over-travel stop: at full collet depression (1.33 mm travel), the outer bore floor contacts the PP0408W body-end shoulder (Ø 15.10 mm). The fitting becomes the hard stop.
- Zone 2 depth (2.0 mm): minimum from collet-release-force.md §4 to prevent collet canting during the full 1.33 mm depression stroke.
- Zone 3 depth (1.6 mm): remaining plate thickness after Zones 1+2 (5.0 − 1.4 − 2.0 = 1.6 mm). Through-hole exits fitting-facing face. This zone must be ≥0 mm (i.e., Zone 1 + Zone 2 < plate thickness); 3.4 mm < 5.0 mm, confirmed.

**Zone step cross-section profile at bore center (all 4 bores, viewed in the XY plane):**

```
Y = 5.0  ─────────────────────────────────────────────────────
          │         Zone 1: Ø 15.60 mm (radius 7.80 mm)         │
Y = 3.6  ─────────────────────────────────────────────────────
              │  Zone 2: Ø 10.07 mm (radius 5.035 mm)   │
Y = 1.6  ─────────────────────────────────────────────────────
                    │  Zone 3: Ø 6.50 mm (r 3.25)  │
Y = 0.0  ─────────────────────────────────────────────────────
          (fitting-facing face — Zone 3 through-hole exits here)
```

**Annular lip (collet contact face):** The step transition between Zone 2 and Zone 3 at Y = 1.6 mm is a flat annular face. Its inner radius = 3.25 mm (Zone 3 radius), outer radius = 5.035 mm (Zone 2 radius), annular width = 1.785 mm per side. This face contacts the PP0408W collet's annular end face (collet ID 6.69 mm, collet OD 9.57 mm) during actuation.

**Contact geometry with PP0408W collet (from geometry-description.md):**

| PP0408W feature | Dimension | Plate bore zone | Plate dimension | Clearance |
|---|---|---|---|---|
| Body-end OD (hard stop ring) | 15.10 mm | Zone 1 bore | Ø 15.60 mm | 0.50 mm diametric |
| Collet OD (sleeve to hug) | 9.57 mm | Zone 2 bore | Ø 10.07 mm | 0.50 mm diametric |
| Collet ID (tube passes through) | 6.69 mm | Zone 3 bore | Ø 6.50 mm | Plate contacts annular face (6.50 < 6.69 ✓) |
| Tube OD | 6.30 mm | Zone 3 bore | Ø 6.50 mm | 0.20 mm diametric |

---

### 3.4 Guide Pin Positions

Two guide pins, integral to the plate, extend from the user-facing face (positive Y direction in print orientation = upward from build plate). Placed at diagonally opposite corners — top-left and bottom-right.

**Pin center coordinates (X, Z) in plate local frame:**

| Pin | Position | X (mm) | Z (mm) |
|---|---|---|---|
| Pin 1 | Top-left | 5.0 | 60.0 |
| Pin 2 | Bottom-right | 75.0 | 5.0 |

**Derivation:** The pin centers are placed diagonally symmetric about the plate center (40.0, 32.5). Pin 1 offset from center: (−35.0, +27.5). Pin 2 offset: (+35.0, −27.5). Each pin is positioned to maximize clearance from the nearest outer bore while respecting plate edge minimums.

**Pin clearance verification:**

| Measurement | Pin 1 | Pin 2 | Minimum |
|---|---|---|---|
| Distance to nearest bore center (A for Pin 1, D for Pin 2) | 13.12 mm | 13.12 mm | 11.5 mm (bore_r + pin_r + wall = 7.8+2.5+1.2) |
| Surface gap (bore outer edge to pin outer edge) | 2.82 mm | 2.82 mm | 1.2 mm |
| Distance to left plate edge | 5.0 mm | 75.0 mm | 3.7 mm (pin_r + wall = 2.5+1.2) |
| Distance to right plate edge | 75.0 mm | 5.0 mm | 3.7 mm |
| Distance to bottom plate edge | 60.0 mm | 5.0 mm | 3.7 mm |
| Distance to top plate edge | 5.0 mm | 60.0 mm | 3.7 mm |

All clearances confirmed. The 1.0 mm extra margin beyond the 3.7 mm minimum on the tight edges (top for Pin 1, bottom for Pin 2) is sufficient.

**Pin center-to-center diagonal:** sqrt((75.0−5.0)² + (5.0−60.0)²) = sqrt(4900 + 3025) = **89.0 mm**

This is the anti-rotation moment arm for the guide system. It exceeds the ~74 mm value cited in guide-geometry.md §3 (which was based on a smaller plate assumption); 89 mm provides greater anti-rotation stiffness.

---

### 3.5 Guide Pin Geometry

Pins are integral to the user-facing face of the plate — they are cylindrical bosses rising from the user-facing face in the +Y (print-upward) direction.

| Parameter | Value | Source |
|---|---|---|
| Pin OD (designed) | 5.0 mm | guide-geometry.md §2 |
| Pin base center Y | 5.0 mm (at user-facing face) | User-facing face definition |
| Pin tip Y | 35.0 mm (= 5.0 + 30.0) | guide-geometry.md §1: 28 mm min engagement + 2 mm travel clearance = 30 mm |
| Pin length from user-facing face | 30.0 mm | guide-geometry.md §1 |

**Pin Y extent (plate local frame):**

```
Y = 5.0 mm  ── Pin base (at user-facing face, integral junction with plate body)
             │
             │  30.0 mm cylindrical pin, Ø 5.0 mm
             │
Y = 35.0 mm ── Pin tip (flat circular end face, Ø 5.0 mm)
```

**Pin cross-section at any Y between 5.0 and 35.0:**
Circular, centered at (X_pin, Z_pin), radius 2.5 mm.

Pin 1: circle center (5.0, 60.0) in XZ plane, radius 2.5 mm.
Pin 2: circle center (75.0, 5.0) in XZ plane, radius 2.5 mm.

**Mating bore in cartridge body (interface — specified from plate side):**

| Feature | Plate side (provides) | Cartridge body (must provide) |
|---|---|---|
| Pin OD | 5.0 mm | Bore ID = 5.5 mm (0.5 mm over pin for FDM sliding clearance) |
| Pin length | 30.0 mm | Bore depth ≥ 30.0 mm |
| Pin center XZ | Pin 1: (5.0, 60.0); Pin 2: (75.0, 5.0) | Bore centers at matching XZ in cartridge |
| Pin base Y | Y = 5.0 (user-facing face) | Bore entry at cartridge interior face |
| Pin tip Y | Y = 35.0 | Bore must extend ≥ 30 mm from entry |

---

### 3.6 Spring Pocket Context

**There are no spring pockets on the release plate.**

The two return springs (one per guide pin) sit in pockets in the **cartridge body** rear-wall structure. Each pocket is 8 mm diameter, 10 mm deep, positioned concentric with the corresponding guide pin bore in the cartridge body. The spring bears against the plate user-facing face (Y = 5.0 mm) at the pin boss base circle; the plate user-facing face is the only spring-contact surface on the plate.

**Plate user-facing face Y-coordinate:** Y = 5.0 mm (constant, flat face, no pockets or bosses in the spring contact zone).

The spring contact annulus for each pin is approximately centered at the pin center (X_pin, Z_pin), with inner radius ≈ 2.5 mm (pin OD/2) and outer radius ≈ 4.0 mm (half the 8 mm spring/pocket diameter). The plate user-facing face is flat throughout this zone — no feature on the plate needed for spring guidance.

---

### 3.7 Perimeter Edge Radius — Pull Edge (3 mm)

The 3 mm radius runs around the entire plate perimeter at the fitting-facing face (Y = 0) edge. This is the edge formed by the intersection of the fitting-facing face plane (Y = 0) and each perimeter wall.

**In print orientation** (fitting-facing face down), this edge is the very first printed perimeter — it lies at Z = 0 on the build plate. The radius is a convex curvature on the perimeter that faces into the cartridge body pocket when assembled.

**Affected edges (by perimeter wall, in plate local frame):**

| Edge | Fixed coordinates | Varying coordinate |
|---|---|---|
| Left perimeter edge at fitting-facing face | X = 0, Y = 0 | Z: 0 → 65.0 mm |
| Right perimeter edge at fitting-facing face | X = 80.0, Y = 0 | Z: 0 → 65.0 mm |
| Bottom perimeter edge at fitting-facing face | Z = 0, Y = 0 | X: 0 → 80.0 mm |
| Top perimeter edge at fitting-facing face | Z = 65.0, Y = 0 | X: 0 → 80.0 mm |

**Radius cross-section (at any point along the above edges):**

The radius is a convex quarter-circle of R = 3.0 mm. It transitions from the fitting-facing face plane (Y = 0, flat) to the perimeter wall plane (X = 0 or X = 80 or Z = 0 or Z = 65). The radius center is inset 3.0 mm from both the fitting-facing face (Y = 3.0) and the perimeter wall plane.

```
Cross-section at left perimeter edge (X=0):
  At X=0, Y=0:  Fitting-facing face corner (radius start on fitting-facing face)
  Radius arc:   Quarter circle from (X=0, Y=0) to (X=−3, Y=3)
                → resolved to plate exterior: arc center at (X=−3, Y=3)...

  More precisely: the 3mm fillet rounds the edge between the fitting-facing face (Y=0 plane)
  and the left perimeter wall (X=0 plane). The center of the circular arc is at
  (X=0+3, Y=0+3) = (3.0, 3.0) in the local XY cross-section.
  The arc spans from (0, 3.0) on the perimeter wall to (3.0, 0) on the fitting-facing face.
```

**Note on elephant's foot interaction:** This 3 mm radius on the front face perimeter edges satisfies the elephant's foot mitigation requirement from requirements.md (0.3 mm × 45° chamfer on bottom edge). A 3 mm radius is a far more generous treatment than the minimum 0.3 mm chamfer. No additional chamfer is needed at any point where the 3 mm radius is applied. The 3 mm radius applies to all four perimeter edges at Y = 0, which is the complete set of build-plate-contact edges, so the elephant's foot requirement is fully satisfied by this feature alone.

---

### 3.8 Perimeter Corner Radii (2 mm)

The four vertical edges (parallel to Y, running through the plate thickness) at the XZ-plane corners of the plate receive a 2 mm radius.

**Affected edges:**

| Corner | Edge path (plate local frame) |
|---|---|
| Bottom-left | From (0, 0, 0) to (0, 5.0, 0) — edge parallel to Y at X=0, Z=0 |
| Bottom-right | From (80.0, 0, 0) to (80.0, 5.0, 0) — edge at X=80, Z=0 |
| Top-left | From (0, 0, 65.0) to (0, 5.0, 65.0) — edge at X=0, Z=65 |
| Top-right | From (80.0, 0, 65.0) to (80.0, 5.0, 65.0) — edge at X=80, Z=65 |

**Radius:** 2.0 mm. The 2 mm corner radius must match the corresponding pocket corner radius in the cartridge body pocket interior to maintain the designed 0.6–1.0 mm uniform parting line gap at corners.

**Note on interaction with pull edge radius:** The 3 mm pull edge radius (§3.7) and the 2 mm corner radius (§3.8) meet at each of the four front-face-perimeter-corner points: (0, 0, 0), (80, 0, 0), (0, 0, 65), (80, 0, 65). The CadQuery agent should apply the corner radii first (on the vertical edges) then the pull edge radius (on the front face perimeter edges); the order produces a smoothly blended corner. Alternatively, the two radii may be applied simultaneously and the kernel will resolve the blend. The front face perimeter edges at the corners are shorter than the full edge lengths due to the 2 mm corner radius removing material at the ends — the effective length of each pull-radius edge is reduced by 2 mm at each end.

---

### 3.9 Elephant's Foot Chamfer

Resolved in §3.7. The 3 mm pull edge radius applied to all four perimeter edges at Y = 0 fully satisfies the elephant's foot requirement. No additional 0.3 mm × 45° chamfer is required.

For completeness, the requirement from requirements.md (§6, Dimensional Accuracy) states: "If the bottom face is a mating surface, add a 0.3 mm × 45° chamfer to the bottom edge." The fitting-facing face (Y = 0) is a mating surface (it mates with the cartridge body pocket floor). The 3 mm radius on the fitting-facing face perimeter edges provides a far larger relief than the minimum 0.3 mm chamfer and fully addresses the elephant's foot concern.

---

## 4. Interface Specifications (From Both Sides)

### Interface 1: Stepped Bore ↔ PP0408W Collet

| Parameter | Plate side | PP0408W side | Clearance |
|---|---|---|---|
| Outer bore diameter | 15.60 mm | Body-end OD 15.10 mm | 0.50 mm diametric (0.25 mm radial) |
| Inner lip bore diameter | 10.07 mm | Collet OD 9.57 mm | 0.50 mm diametric (0.25 mm radial) |
| Tube through-hole diameter | 6.50 mm | Tube OD 6.30 mm | 0.20 mm diametric; collet ID 6.69 mm (plate contacts annular face ✓) |
| Zone 1 axial depth | 1.4 mm (from user-facing face) | Collet travel 1.33 mm per side | 0.07 mm over-travel margin before hard stop |
| Zone 2 axial depth | 2.0 mm | Collet OD engagement needed ≥ 2.0 mm | Exactly met |
| Contact face (annular step Z2→Z3) | Y = 1.6 mm in plate frame | Collet annular end face | Contacts at full depression |

### Interface 2: Guide Pin ↔ Cartridge Body Bore

| Parameter | Plate side (pin) | Cartridge body side (bore) | Clearance |
|---|---|---|---|
| Pin OD | 5.0 mm designed | 5.5 mm designed bore ID | 0.5 mm diametric designed; ~0.3 mm as-printed |
| Pin length | 30.0 mm from user-facing face | Bore depth ≥ 30.0 mm | Travel clearance: 30 mm engagement at rest, 28 mm at full stroke |
| Pin center — Pin 1 | (X=5.0, Z=60.0) in plate frame | Bore center at matching position in cartridge | Positional accuracy: printer XY ±0.2 mm |
| Pin center — Pin 2 | (X=75.0, Z=5.0) in plate frame | Bore center at matching position in cartridge | Positional accuracy: printer XY ±0.2 mm |
| Pin base Y | Y = 5.0 (at user-facing face) | Bore entry face (at corresponding cartridge interior wall) | Flush — no step |
| Bore entry chamfer | Not on plate | 0.5 mm × 45° on cartridge bore entry | For pin insertion guidance |

### Interface 3: Plate Rear Face ↔ Return Springs

| Parameter | Plate side | Cartridge body side | Notes |
|---|---|---|---|
| Spring contact surface | Flat user-facing face at Y = 5.0 mm | Spring end coil bears here | No feature on plate |
| Spring contact zone (Pin 1 spring) | Rear face area centered at (X=5.0, Z=60.0), annulus r_in=2.5mm r_out=4.0mm | 8 mm dia pocket concentric with pin bore | Spring wraps pin |
| Spring contact zone (Pin 2 spring) | Rear face area centered at (X=75.0, Z=5.0), annulus r_in=2.5mm r_out=4.0mm | 8 mm dia pocket concentric with pin bore | Spring wraps pin |

### Interface 4: Plate Front Face ↔ Cartridge Body Pocket Floor (at rest)

| Parameter | Plate side | Cartridge body side | Notes |
|---|---|---|---|
| User-facing face Y position (at rest) | Y = 5 mm | 10 mm behind cartridge body front face | 10 mm inset gives grip ergonomics |
| User-facing face Y position (actuated) | Y = 5 mm (face is fixed to plate) | Gap decreases to 7 mm as plate travels toward user | Plate moves, pocket floor is fixed |
| Plate perimeter at Y = 0 | X: 0 → 80.0 mm, Z: 0 → 65.0 mm (nominal before corner radii) | Pocket inner dimensions = plate + 0.6–1.0 mm on each side | Designed parting line gap |

---

## 5. Transform Summary

### Part Frame → Cartridge Assembly Frame

The release plate has no angular mounting. The transform is a pure translation — no rotation, no scaling.

```
Part frame axes → Cartridge assembly axes:
  Part X (width, 0→80)  →  Cartridge width axis (same direction)
  Part Y (depth, 0→5)   →  Cartridge front-to-back depth axis (same direction, +Y = rearward)
  Part Z (height, 0→65) →  Cartridge height axis (same direction)
  Rotation: none (identity rotation matrix)

Translation (at rest position):
  Cart_X = T_x + Part_X   (T_x = X offset of plate left edge in cartridge frame)
  Cart_Y = T_y + Part_Y   (T_y positions plate user-facing face 10 mm behind cartridge front face)
  Cart_Z = T_z + Part_Z   (T_z = Z offset of plate bottom edge in cartridge frame)

  T_x, T_z: resolved by the cartridge body specification (they set the pocket position)
  T_y: such that at rest, plate user-facing face (Part_Y=5) is 10 mm behind cartridge front face

Actuation offset:
  At rest:     Cart_Y = T_y + Part_Y  (no actuation offset)
  Actuated δ:  Cart_Y = (T_y − δ) + Part_Y, where δ ∈ [0, 3.0 mm]
  (plate moves toward user = decreasing Cart_Y, i.e., plate translates −Y_cartridge)
```

**Verification (3 test points in part local frame → cartridge frame):**

| Point | Part local (X, Y, Z) | Cartridge (X, Y, Z) | Check |
|---|---|---|---|
| Origin (fitting-left-bottom corner) | (0, 0, 0) | (T_x, T_y, T_z) | Translates correctly |
| Top-right-user corner | (80.0, 5.0, 65.0) | (T_x+80, T_y+5, T_z+65) | Pure translation, no shear |
| Bore A center at user-facing face | (9.0, 5.0, 47.5) | (T_x+9, T_y+5, T_z+47.5) | Fitting alignment in cartridge |

**Round-trip check (cartridge → part local):**
Part_X = Cart_X − T_x, Part_Y = Cart_Y − T_y, Part_Z = Cart_Z − T_z. Identity round-trip for all three test points. ✓

**Self-consistency check:**
- Part local Y=0 maps to Cart_Y = T_y (fitting-facing face) ✓
- Part local Y=5 maps to Cart_Y = T_y+5 (user-facing face, inset 10 mm from cartridge front) ✓
- Plate travel of 3 mm increases Cart_Y of all plate points by 3 mm (plate user-facing face moves to T_y+5+3) ✓
- No rotation means bore axes remain parallel to the cartridge depth axis throughout actuation ✓

---

## 6. Quality Gate Verification

| Criterion | Status | Notes |
|---|---|---|
| Every number is in a named reference frame | PASS | All coordinates explicitly labeled as plate local frame |
| No downstream derivation required | PASS | All bore centers, zone depths, pin positions are given as final numbers |
| Cross-section profiles tabulated | PASS | Bore zone table (§3.3), bore contact geometry table (§3.3), all as concrete dimensions |
| Interfaces specified from both sides | PASS | §4 covers all four interfaces with both sides |
| Transform summary is self-consistent | PASS | §5 verified with 3 test points and round-trip check |

---

## 7. Consolidated Dimension Table (for 4b Parts Specification Agent)

All values below are in the plate local frame (origin at bottom-left-front corner, X=width, Y=depth front-to-back, Z=height). The 4b agent reads these directly — no computation needed.

### Plate Envelope

| Dimension | Value |
|---|---|
| Width (X) | 80.0 mm |
| Depth / Thickness (Y) | 5.0 mm |
| Height (Z) | 65.0 mm |

### Bore Centers (all Y = 3.6–5.0 mm, user-facing face zone)

| Bore | X | Z |
|---|---|---|
| A (top-left) | 9.0 mm | 47.5 mm |
| B (bottom-left) | 9.0 mm | 17.5 mm |
| C (top-right) | 71.0 mm | 47.5 mm |
| D (bottom-right) | 71.0 mm | 17.5 mm |

### Stepped Bore Diameters

| Zone | Diameter | Y range |
|---|---|---|
| Zone 1 (outer bore) | 15.60 mm | Y 5.0 → 3.6 mm |
| Zone 2 (inner lip) | 10.07 mm | Y 3.6 → 1.6 mm |
| Zone 3 (tube through-hole) | 6.50 mm | Y 1.6 → 0.0 mm |

### Guide Pins

| Parameter | Value |
|---|---|
| Pin 1 center (X, Z) | (5.0, 60.0) mm |
| Pin 2 center (X, Z) | (75.0, 5.0) mm |
| Pin OD | 5.0 mm |
| Pin base Y | 5.0 mm (at user-facing face) |
| Pin tip Y | 35.0 mm |
| Pin length | 30.0 mm |

### Edge Features

| Feature | Value | Edge(s) |
|---|---|---|
| Pull edge radius | 3.0 mm | All 4 perimeter edges at fitting-facing face (Y = 0) |
| Corner radius | 2.0 mm | All 4 vertical edges at XZ corners (Y = 0 → 5.0) |
| Elephant's foot | Satisfied by 3 mm pull radius | No additional chamfer required |

### Spring Pockets

| Feature | Value |
|---|---|
| Spring pockets on plate | None |
| Spring contact surface | Flat user-facing face at Y = 5.0 mm |
| Spring contact locations | Centered at pin centers (5.0, 60.0) and (75.0, 5.0) |
