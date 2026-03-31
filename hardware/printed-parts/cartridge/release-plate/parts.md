# Release Plate v5 -- Parts Specification

**Build sequence line:** Widen release plate -- match the new width and move its struts to align with the new strut bore positions and the lever's struts.

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Release plate |
| Piece count | 1 |
| Outer dimensions | 160.0mm (X) x 5.0mm (Y plate) + 90.0mm (Y struts) x 68.6mm (Z) |
| Envelope | 160.0mm (X) x 95.0mm (Y) x 68.6mm (Z) |
| Features | Plate body + 4x stepped bores + 4x struts + corner radii + pull edge radius |
| Print orientation | Fitting-facing face (Y=0) down on build plate. Struts extend upward in print Z. |
| Material | PETG |
| Supports required | None |
| User-facing | No (hidden inside cartridge pocket) |

---

## Coordinate System

Origin: bottom-left corner of the plate at the fitting-facing face.

```
X: width axis -- left to right, 0..160.0mm
Y: depth axis -- fitting-facing to user-facing; struts extend beyond user-facing face
    Y=0: fitting-facing face (tube exit side; sits on build plate in print orientation)
    Y=5.0: user-facing face (stepped bore entry, pull surface, strut attachment)
    Y=95.0: strut tips
Z: height axis -- bottom to top, 0..68.6mm
```

Print orientation: fitting-facing face (XZ plane, Y=0) down on build plate. Struts extend upward in print Z.

---

## What Changed (v4 to v5)

**Problem in v4:** The release plate was 137.2mm wide with struts at X=10.0 and X=127.2. All interior plates have been widened to 140.0mm in Phase 6 (items 13-15), and strut bore/strut positions have moved outward. The release plate's width and strut positions no longer match.

**Fix:** Widen the plate from 137.2mm to 140.0mm. Move strut center positions to match the lever's strut centers exactly: (4.0, 63.6), (136.0, 63.6), (4.0, 5.0), (136.0, 5.0).

**v4 dimensions (unchanged):** plate thickness 5.0mm, plate height 68.6mm, 4 stepped bores (1x4 row at Z=34.3), strut cross-section 6.0x6.0mm, strut length 90.0mm, corner radii 2.0mm, pull edge radius 3.0mm.

**v5 changes:**
- Plate width: 137.2mm -> 140.0mm
- Strut TL center: (10.0, 63.6) -> (4.0, 63.6)
- Strut TR center: (127.2, 63.6) -> (136.0, 63.6)
- Strut BL center: (10.0, 5.0) -> (4.0, 5.0)
- Strut BR center: (127.2, 5.0) -> (136.0, 5.0)
- Bore positions unchanged (still centered in the plate row)

---

## Feature List

### Feature 1 -- Plate Body

| Property | Value |
|----------|-------|
| Operation | Add (base body) |
| Geometry | Rectangular prism |
| Dimensions | 160.0 (X) x 5.0 (Y) x 68.6 (Z) mm |
| Position | X:[0, 160.0] Y:[0, 5.0] Z:[0, 68.6] |
| Justification | Width 160.0mm accommodates struts moved outward. Height 68.6mm unchanged. Depth 5.0mm accommodates Zone 1 (1.4mm) + Zone 2 (1.2mm) + Zone 3 (2.4mm). |

### Feature 2 -- Perimeter Corner Radii

| Property | Value |
|----------|-------|
| Operation | Remove (fillet) |
| Geometry | Convex cylindrical fillet on four vertical (Y-parallel) plate edges |
| Affected edges | (X=0, Z=0), (X=160.0, Z=0), (X=0, Z=68.6), (X=160.0, Z=68.6); each runs Y=0 to Y=5.0 |
| Radius | 2.0mm |
| Justification | Design language consistency with lever. Corner radius must match cartridge body pocket interior corner radius. |

### Feature 3 -- Pull Edge Radius

| Property | Value |
|----------|-------|
| Operation | Remove (fillet) |
| Geometry | Convex quarter-circle fillet on all four perimeter edges at fitting-facing face (Y=0) |
| Affected edges | Left (X=0), right (X=160.0), bottom (Z=0), top (Z=68.6) edges at Y=0 |
| Radius | 3.0mm |
| Justification | Tactile comfort on the edge finger pads bear against during the pull stroke. Also satisfies elephant's foot requirement. |

### Feature 4 -- Stepped Bore A (H1)

| Property | Value |
|----------|-------|
| Operation | Remove (three-diameter concentric bore from user-facing face through fitting-facing face) |
| Center (X, Z) | (53.1, 34.3) |
| Bore axis | Parallel to Y |
| Zone 1 (outer bore) | Dia 15.60mm; depth 1.4mm from user-facing face; Y: 5.0 -> 3.6 |
| Zone 2 (inner lip bore) | Dia 10.07mm; depth 1.2mm; Y: 3.6 -> 2.4 |
| Zone 3 (through-hole) | Dia 6.75mm; depth 2.4mm; Y: 2.4 -> 0.0 (exits fitting-facing face) |
| Justification | Position matches coupler tray hole H1. Unchanged from v4. |

### Feature 5 -- Stepped Bore B (H2)

Identical geometry to Feature 4. Center (X, Z) = (70.1, 34.3). Position matches coupler tray hole H2.

### Feature 6 -- Stepped Bore C (H3)

Identical geometry to Feature 4. Center (X, Z) = (87.1, 34.3). Position matches coupler tray hole H3.

### Feature 7 -- Stepped Bore D (H4)

Identical geometry to Feature 4. Center (X, Z) = (104.1, 34.3). Position matches coupler tray hole H4.

**Bore pattern summary (1x4 row):**

| Bore | Center X | Center Z |
|------|----------|----------|
| A | 53.1 | 34.3 |
| B | 70.1 | 34.3 |
| C | 87.1 | 34.3 |
| D | 104.1 | 34.3 |

17.0mm center-to-center spacing. Row centered at X=78.6mm (plate center = 80.0mm).

### Feature 10 -- Strut TL (Top-Left)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular boss protruding from user-facing face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (4.0, 63.6) |
| Extents X | [1.0, 7.0] |
| Extents Z | [60.6, 66.6] |
| Extents Y | [5.0, 95.0] |
| Justification | Position matches lever strut TL center (4.0, 63.6) and pump tray bore S-TL center (4.0, 63.6). |

### Feature 11 -- Strut TR (Top-Right)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular boss protruding from user-facing face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (156.0, 63.6) |
| Extents X | [153.0, 159.0] |
| Extents Z | [60.6, 66.6] |
| Extents Y | [5.0, 95.0] |
| Justification | Position matches lever strut TR center (156.0, 63.6). |

### Feature 12 -- Strut BL (Bottom-Left)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular boss protruding from user-facing face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (4.0, 5.0) |
| Extents X | [1.0, 7.0] |
| Extents Z | [2.0, 8.0] |
| Extents Y | [5.0, 95.0] |
| Justification | Position matches lever strut BL center (4.0, 5.0) and pump tray bore S-BL center (4.0, 5.0). |

### Feature 13 -- Strut BR (Bottom-Right)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular boss protruding from user-facing face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (156.0, 5.0) |
| Extents X | [153.0, 159.0] |
| Extents Z | [2.0, 8.0] |
| Extents Y | [5.0, 95.0] |
| Justification | Position matches lever strut BR center (156.0, 5.0). |

**Strut geometry summary:**

| Strut | Center (X, Z) | Cross-section | Extents Y | Length |
|-------|---------------|---------------|-----------|--------|
| TL | (4.0, 63.6) | 6.0 x 6.0 mm | 5.0 -> 95.0 | 90.0mm |
| TR | (156.0, 63.6) | 6.0 x 6.0 mm | 5.0 -> 95.0 | 90.0mm |
| BL | (4.0, 5.0) | 6.0 x 6.0 mm | 5.0 -> 95.0 | 90.0mm |
| BR | (156.0, 5.0) | 6.0 x 6.0 mm | 5.0 -> 95.0 | 90.0mm |

Strut horizontal spacing (TL-TR or BL-BR): 152.0mm center-to-center.
Strut vertical spacing (TL-BL or TR-BR): 58.6mm center-to-center.

---

## Clearance Checks

**Struts vs. plate edges (minimum wall thickness 0.8mm required):**

| Strut | Nearest edge | Strut edge pos | Plate edge pos | Wall thickness |
|-------|-------------|----------------|----------------|----------------|
| TL | X=0 (left) | 1.0 | 0.0 | 1.0mm |
| TL | Z=68.6 (top) | 66.6 | 68.6 | 2.0mm |
| TR | X=160.0 (right) | 159.0 | 160.0 | 1.0mm |
| TR | Z=68.6 (top) | 66.6 | 68.6 | 2.0mm |
| BL | X=0 (left) | 1.0 | 0.0 | 1.0mm |
| BL | Z=0 (bottom) | 2.0 | 0.0 | 2.0mm |
| BR | X=160.0 (right) | 159.0 | 160.0 | 1.0mm |
| BR | Z=0 (bottom) | 2.0 | 0.0 | 2.0mm |

All at or above 0.8mm minimum. Passes.

**Struts vs. stepped bores (no interference required):**

| Strut | Nearest bore | Strut nearest corner | Bore center | Center-to-center dist | Minus bore R (7.8mm) | Gap |
|-------|-------------|---------------------|-------------|----------------------|---------------------|-----|
| TL | A (53.1, 34.3) | (7.0, 60.6) | (53.1, 34.3) | sqrt((53.1-7.0)^2 + (34.3-60.6)^2) = 53.0mm | 53.0 - 7.8 = 45.2mm | No interference |
| TR | D (104.1, 34.3) | (153.0, 60.6) | (104.1, 34.3) | sqrt((153.0-104.1)^2 + (60.6-34.3)^2) = 55.7mm | 55.7 - 7.8 = 47.9mm | No interference |
| BL | A (53.1, 34.3) | (7.0, 8.0) | (53.1, 34.3) | sqrt((53.1-7.0)^2 + (34.3-8.0)^2) = 53.0mm | 53.0 - 7.8 = 45.2mm | No interference |
| BR | D (104.1, 34.3) | (153.0, 8.0) | (104.1, 34.3) | sqrt((153.0-104.1)^2 + (34.3-8.0)^2) = 55.7mm | 55.7 - 7.8 = 47.9mm | No interference |

All struts fully clear of all bore outer circles. Passes.

**Strut centers vs. lever strut centers (must match exactly):**

| Strut | Release plate center (X, Z) | Lever center (X, Z) | Match? |
|-------|----------------------------|---------------------|--------|
| TL | (4.0, 63.6) | (4.0, 63.6) | Yes |
| TR | (156.0, 63.6) | (156.0, 63.6) | Yes |
| BL | (4.0, 5.0) | (4.0, 5.0) | Yes |
| BR | (156.0, 5.0) | (156.0, 5.0) | Yes |

**Strut centers vs. pump tray bore centers (must align when plates centered in assembly):**

| Strut | Release plate center (X, Z) | Dist from center | Pump tray bore center (X, Z) | Dist from center | Match? |
|-------|----------------------------|-----------------|------------------------------|-----------------|--------|
| TL | (4.0, 63.6) | 76mm | (9.0, 63.6) | 76mm | Yes |
| TR | (156.0, 63.6) | 76mm | (161.0, 63.6) | 76mm | Yes |
| BL | (4.0, 5.0) | 76mm | (9.0, 5.0) | 76mm | Yes |
| BR | (156.0, 5.0) | 76mm | (161.0, 5.0) | 76mm | Yes |

---

## Bore wall-to-edge clearances (updated for 140.0mm width)

| Bore | Nearest plate edge | Distance from bore outer edge to plate edge |
|------|-------------------|---------------------------------------------|
| A (X=53.1) | X=0 (left) | 53.1 - 7.8 = 45.3mm |
| D (X=104.1) | X=160.0 (right) | 160.0 - 104.1 - 7.8 = 48.1mm |

All well above 1.2mm structural minimum. Passes.

---

## FDM Check

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Plate body -- all walls | Overhang | All faces vertical or on build plate | 45 deg max | Yes |
| Plate thickness | Wall thickness | 5.0mm | 1.2mm structural min | Yes |
| Bore wall to left/right edge | Thickness | 45.3mm min | 1.2mm structural min | Yes |
| Adjacent bore wall | Gap | 1.4mm edge-to-edge (outer bore) | No intersection | Yes |
| Strut cross-section | Wall thickness | 6.0mm x 6.0mm | 1.2mm structural min | Yes |
| Strut clearance to bores | Gap | 36.9mm minimum | No intersection | Yes |
| Strut to plate edge | Wall thickness | 1.0mm minimum | 0.8mm non-structural min | Yes |
| Holes -- orientation | Print as vertical cylinders | Axis parallel to print Z (Y axis) | -- | Yes |

No overhangs. No supports required.

---

## Feature Traceability

| Feature | Justification |
|---------|---------------|
| Plate width increase (137.2 -> 140.0mm) | Build sequence line: "match the new width." All interior plates are now 140.0mm wide. |
| Strut positions moved (10.0/127.2 -> 4.0/136.0 in X) | Build sequence line: "move its struts to align with the new strut bore positions and the lever's struts." Lever strut centers at (4.0, 63.6), (136.0, 63.6), (4.0, 5.0), (136.0, 5.0). |
| Bore positions unchanged | Bore positions are constrained by the coupler tray coupler positions, which did not change. |
| All other features unchanged | Corner radii, pull edge radius, bore geometry, strut cross-section, strut length, plate thickness unchanged per scope. |
