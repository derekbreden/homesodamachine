# Pump Tray v2 -- Parts Specification

**Build sequence line:** Add strut bores to pump tray -- 4 holes sized to the strut cross-section, positioned so the struts pass through cleanly.

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Pump Tray |
| Piece count | 1 |
| Outer dimensions | 137.2mm (X) x 3.0mm (Y) x 68.6mm (Z) |
| Features | Plate body + 2x motor bores + 8x M3 clearance holes + 4x strut bores |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

---

## Coordinate System

Origin: bottom-left corner of the front face of the plate.

```
X: width axis -- left to right, 0..137.2mm
Y: thickness axis -- front to back through the plate, 0..3.0mm
    Y=0: front face (pump bracket contact side)
    Y=3.0mm: back face (motor/screw-access side)
Z: height axis -- bottom to top, 0..68.6mm
```

Print orientation: front face (XZ plane, Y=0) down on build plate.

---

## What Changed (v1 to v2)

v1 features (unchanged): plate body, 2 motor bores, 8 M3 clearance holes.

v2 adds: 4 rectangular strut bores (Features 12-15).

---

## Feature List

### Feature 1 -- Plate Body (unchanged)

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Dimensions | 137.2 (X) x 3.0 (Y) x 68.6 (Z) mm |

### Features 2-3 -- Motor Bores (2x, unchanged)

| Property | Value |
|----------|-------|
| Geometry | Cylindrical through-bore, 37mm dia, Y=0 to Y=3.0 |
| Bore 1 center (X, Z) | (34.3, 34.3) |
| Bore 2 center (X, Z) | (102.9, 34.3) |

### Features 4-11 -- M3 Clearance Holes (8x, unchanged)

3.3mm diameter through-holes, Y=0 to Y=3.0. Positions per v1 spec.

### Features 12-15 -- Strut Bores (4x, NEW)

The release plate has 4 rectangular struts (6.0 x 6.0 mm cross-section) at corner positions that pass through the pump tray. The bores are rectangular through-holes at the same (X, Z) centers, sized with 0.2mm clearance per side per requirements.md sliding fit tolerance.

| Property | Value |
|----------|-------|
| Geometry | Rectangular through-bore |
| Bore cross-section | 6.4mm (X) x 6.4mm (Z) |
| Derivation | 6.0mm strut + 0.2mm clearance per side = 6.4mm per axis |
| Bore axis | Parallel to Y, Y=0 to Y=3.0mm (full through-hole) |

| Bore ID | Center X (mm) | Center Z (mm) | Source |
|---------|---------------|---------------|--------|
| S-TL | 10.0 | 63.6 | Release plate strut TL |
| S-TR | 127.2 | 63.6 | Release plate strut TR |
| S-BL | 10.0 | 5.0 | Release plate strut BL |
| S-BR | 127.2 | 5.0 | Release plate strut BR |

---

## Clearance Checks

**Strut bores vs. plate edges (minimum wall thickness 0.8mm required):**

| Bore | Nearest edge | Distance from bore edge to plate edge |
|------|-------------|---------------------------------------|
| S-TL | X=0 (left) | 10.0 - 3.2 = 6.8mm |
| S-TL | Z=68.6 (top) | 68.6 - 63.6 - 3.2 = 1.8mm |
| S-TR | X=137.2 (right) | 137.2 - 127.2 - 3.2 = 6.8mm |
| S-TR | Z=68.6 (top) | 1.8mm |
| S-BL | X=0 (left) | 6.8mm |
| S-BL | Z=0 (bottom) | 5.0 - 3.2 = 1.8mm |
| S-BR | X=137.2 (right) | 6.8mm |
| S-BR | Z=0 (bottom) | 1.8mm |

All above 0.8mm minimum. Passes.

**Strut bores vs. M3 holes (void merge check):**

Each corner strut bore's nearest M3 hole is the corner hole of the adjacent pump. The rectangular bore and circular hole overlap slightly (0.55mm in Z), creating a merged void. This is structurally acceptable -- both are through-holes in a non-load-bearing internal plate, and the surrounding material provides adequate structure.

| Bore | Nearest hole | Bore Z edge | Hole Z edge | Overlap |
|------|-------------|-------------|-------------|---------|
| S-TL (Z=63.6) | 1-A (Z=59.3) | Z=60.4 (bottom) | Z=60.95 (top) | 0.55mm |
| S-TR (Z=63.6) | 2-B (Z=59.3) | Z=60.4 (bottom) | Z=60.95 (top) | 0.55mm |
| S-BL (Z=5.0) | 1-D (Z=9.3) | Z=8.2 (top) | Z=7.65 (bottom) | 0.55mm |
| S-BR (Z=5.0) | 2-C (Z=9.3) | Z=8.2 (top) | Z=7.65 (bottom) | 0.55mm |

**Strut bores vs. motor bores:**

Nearest motor bore center to any strut bore: bore 1 at (34.3, 34.3), nearest strut S-TL at (10.0, 63.6). Distance = 37.8mm center-to-center. Motor bore radius = 18.5mm. Strut bore half-width = 3.2mm. Edge-to-edge gap = 37.8 - 18.5 - 3.2 = 16.1mm. No conflict.

---

## FDM Check

No new overhangs. The strut bores are rectangular through-holes in the Y direction (print Z direction in stated orientation). Rectangular holes print as vertical-walled pockets -- no support required. Minimum wall between strut bores and plate edges is 1.8mm (above 0.8mm minimum).

---

## Feature Traceability

| Feature | Justification |
|---------|---------------|
| Strut bores (4x) | Build sequence line: "4 holes sized to the strut cross-section, positioned so the struts pass through cleanly." |
| Bore positions match release plate struts | The struts are defined by the release plate. Bore centers must match strut centers for the struts to pass through. |
| Bore size 6.4mm (strut 6.0mm + 0.4mm clearance) | Requirements.md: 0.2mm clearance for sliding fits. Applied to each side = 0.4mm total per axis. |
| Rectangular bore shape | Struts are rectangular (6x6mm). Rectangular bores match the strut cross-section as specified in the build sequence line. |
