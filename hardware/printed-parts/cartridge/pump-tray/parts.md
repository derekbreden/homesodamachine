# Pump Tray v3 -- Parts Specification

**Build sequence line:** Widen pump tray -- make the pump tray wider so that the strut bores can be moved outward and no longer overlap the pump mounting holes.

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Pump Tray |
| Piece count | 1 |
| Outer dimensions | 140.0mm (X) x 3.0mm (Y) x 68.6mm (Z) |
| Features | Plate body + 2x motor bores + 8x M3 clearance holes + 4x strut bores |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

---

## Coordinate System

Origin: bottom-left corner of the front face of the plate.

```
X: width axis -- left to right, 0..140.0mm
Y: thickness axis -- front to back through the plate, 0..3.0mm
    Y=0: front face (pump bracket contact side)
    Y=3.0mm: back face (motor/screw-access side)
Z: height axis -- bottom to top, 0..68.6mm
```

Print orientation: front face (XZ plane, Y=0) down on build plate.

---

## What Changed (v2 to v3)

**Problem in v2:** The strut bores overlapped with the M3 pump mounting holes. Each corner strut bore merged with its nearest M3 hole by 0.55mm in Z, and the features also overlapped in X (strut bore X range [6.8, 13.2] vs. M3 hole X range [7.65, 10.95] for the left side). This created merged voids where two functionally separate holes combined.

**Fix:** Widen the plate from 137.2mm to 140.0mm (+2.8mm, +1.4mm per side). The pump mounting pattern stays centered. The strut bores move outward to X=4.0 and X=136.0 (from 10.0 and 127.2), placing them fully outside the M3 hole pattern with 1.85mm clearance edge-to-edge.

**v2 dimensions (unchanged):** plate thickness 3.0mm, plate height 68.6mm, 2 motor bores 37mm dia, 8 M3 clearance holes 3.3mm dia in 50mm square patterns, 4 strut bores 6.4x6.4mm.

**v3 changes:**
- Plate width: 137.2mm -> 140.0mm
- Pump 1 motor bore center X: 34.3 -> 35.7 (+1.4mm, stays centered)
- Pump 2 motor bore center X: 102.9 -> 104.3 (+1.4mm, stays centered)
- All M3 hole X positions shift +1.4mm (stay centered relative to motor bores)
- Strut bore X positions: 10.0 -> 4.0 (left), 127.2 -> 136.0 (right)
- Strut bore Z positions unchanged: 63.6 (top), 5.0 (bottom)

---

## Feature List

### Feature 1 -- Plate Body

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Dimensions | 140.0 (X) x 3.0 (Y) x 68.6 (Z) mm |

### Features 2-3 -- Motor Bores (2x)

| Property | Value |
|----------|-------|
| Geometry | Cylindrical through-bore, 37mm dia, Y=0 to Y=3.0 |
| Bore 1 center (X, Z) | (35.7, 34.3) |
| Bore 2 center (X, Z) | (104.3, 34.3) |
| Derivation | Pump center-to-center 68.6mm, symmetric about plate center X=70.0. Pump 1: 70.0 - 34.3 = 35.7. Pump 2: 70.0 + 34.3 = 104.3. |

### Features 4-11 -- M3 Clearance Holes (8x)

3.3mm diameter through-holes, Y=0 to Y=3.0. 50mm square pattern around each motor bore center.

| Hole | Center X (mm) | Center Z (mm) | Derivation |
|------|---------------|---------------|------------|
| 1-A | 10.7 | 59.3 | Pump 1: 35.7 - 25 = 10.7, 34.3 + 25 = 59.3 |
| 1-B | 60.7 | 59.3 | Pump 1: 35.7 + 25 = 60.7, 34.3 + 25 = 59.3 |
| 1-C | 60.7 | 9.3 | Pump 1: 35.7 + 25 = 60.7, 34.3 - 25 = 9.3 |
| 1-D | 10.7 | 9.3 | Pump 1: 35.7 - 25 = 10.7, 34.3 - 25 = 9.3 |
| 2-A | 79.3 | 59.3 | Pump 2: 104.3 - 25 = 79.3, 34.3 + 25 = 59.3 |
| 2-B | 129.3 | 59.3 | Pump 2: 104.3 + 25 = 129.3, 34.3 + 25 = 59.3 |
| 2-C | 129.3 | 9.3 | Pump 2: 104.3 + 25 = 129.3, 34.3 - 25 = 9.3 |
| 2-D | 79.3 | 9.3 | Pump 2: 104.3 - 25 = 79.3, 34.3 - 25 = 9.3 |

### Features 12-15 -- Strut Bores (4x)

Rectangular through-holes for the 6.0 x 6.0 mm struts. Bore size 6.4 x 6.4 mm (6.0mm strut + 0.2mm clearance per side). Moved outward in X so they no longer overlap the M3 holes.

| Property | Value |
|----------|-------|
| Geometry | Rectangular through-bore |
| Bore cross-section | 6.4mm (X) x 6.4mm (Z) |
| Derivation | 6.0mm strut + 0.2mm clearance per side = 6.4mm per axis |
| Bore axis | Parallel to Y, Y=0 to Y=3.0mm (full through-hole) |

| Bore ID | Center X (mm) | Center Z (mm) |
|---------|---------------|---------------|
| S-TL | 4.0 | 63.6 |
| S-TR | 136.0 | 63.6 |
| S-BL | 4.0 | 5.0 |
| S-BR | 136.0 | 5.0 |

---

## Clearance Checks

**Strut bores vs. plate edges (minimum wall thickness 0.8mm required):**

| Bore | Nearest edge | Distance from bore edge to plate edge |
|------|-------------|---------------------------------------|
| S-TL | X=0 (left) | 4.0 - 3.2 = 0.8mm |
| S-TL | Z=68.6 (top) | 68.6 - 63.6 - 3.2 = 1.8mm |
| S-TR | X=140.0 (right) | 140.0 - 136.0 - 3.2 = 0.8mm |
| S-TR | Z=68.6 (top) | 1.8mm |
| S-BL | X=0 (left) | 0.8mm |
| S-BL | Z=0 (bottom) | 5.0 - 3.2 = 1.8mm |
| S-BR | X=140.0 (right) | 0.8mm |
| S-BR | Z=0 (bottom) | 1.8mm |

All at or above 0.8mm minimum. Passes.

**Strut bores vs. M3 holes (the overlap this version fixes):**

| Bore | Nearest M3 hole | Bore X range | Hole X range | X gap (mm) |
|------|----------------|--------------|--------------|------------|
| S-TL | 1-A (10.7, 59.3) | [0.8, 7.2] | [9.05, 12.35] | 9.05 - 7.2 = 1.85 |
| S-TR | 2-B (129.3, 59.3) | [132.8, 139.2] | [127.65, 130.95] | 132.8 - 130.95 = 1.85 |
| S-BL | 1-D (10.7, 9.3) | [0.8, 7.2] | [9.05, 12.35] | 9.05 - 7.2 = 1.85 |
| S-BR | 2-C (129.3, 9.3) | [132.8, 139.2] | [127.65, 130.95] | 132.8 - 130.95 = 1.85 |

All strut bores fully separated from M3 holes by 1.85mm in X. No overlap in any axis. Passes.

**Strut bores vs. motor bores:**

Nearest motor bore to any strut bore: bore 1 at (35.7, 34.3), nearest strut S-TL at (4.0, 63.6). Distance = sqrt((35.7-4.0)^2 + (34.3-63.6)^2) = sqrt(1004.9 + 858.5) = 43.2mm. Motor bore radius = 18.5mm. Strut bore half-width = 3.2mm. Edge-to-edge gap = 43.2 - 18.5 - 3.2 = 21.5mm. No conflict.

---

## FDM Check

No overhangs. The strut bores are rectangular through-holes in the Y direction (print Z direction in stated orientation). Rectangular holes print as vertical-walled pockets -- no support required. Minimum wall between strut bores and plate edges is 0.8mm (meets 0.8mm minimum for non-structural walls).

---

## Feature Traceability

| Feature | Justification |
|---------|---------------|
| Plate width increase (137.2 -> 140.0mm) | Build sequence line: "make the pump tray wider so that the strut bores can be moved outward and no longer overlap the pump mounting holes." |
| Pump pattern re-centered (+1.4mm X shift) | Pump pattern stays centered in the widened plate. |
| Strut bore X positions moved outward (10.0 -> 4.0, 127.2 -> 136.0) | Build sequence line: "strut bores can be moved outward and no longer overlap the pump mounting holes." Moving outward in X fully separates them from the M3 holes. |
| Strut bore Z positions unchanged (63.6, 5.0) | No Z change needed -- the X separation alone resolves the overlap. |
| All other features unchanged | Only the width and strut positions changed per scope. |
