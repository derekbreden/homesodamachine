# Lever v3 -- Parts Specification

**Build sequence line:** Widen lever -- match the new width and move its struts to align with the new strut bore positions on the pump tray.

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Lever |
| Piece count | 1 |
| Outer dimensions | 140.0mm (X) x 4.0mm (Y plate) + 90.0mm (Y struts) x 68.6mm (Z) |
| Envelope | 140.0mm (X) x 94.0mm (Y) x 68.6mm (Z) |
| Features | Plate body + 4x struts + corner radii + elephant's foot chamfer |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Material | PETG |
| Supports required | None |
| User-facing | Yes (plate front face is the pull surface) |

---

## Coordinate System

Origin: bottom-left corner of the front face of the plate.

```
X: width axis -- left to right as seen by user, 0..140.0mm
Y: depth axis -- front to back
    Y=0: front face (user contact / pull surface; sits on build plate)
    Y=4.0: plate rear face (strut attachment point)
    Y=94.0: strut tips
Z: height axis -- bottom to top, 0..68.6mm
```

Print orientation: front face (XZ plane, Y=0) down on build plate. Struts extend upward in print Z.

---

## What Changed (v2 to v3)

**Problem in v2:** The lever was 80.0mm wide with struts at X=9.0 and X=71.0, and 65.0mm tall with struts at Z=5.0 and Z=60.0. All interior plates have been widened to 140.0mm in Phase 6 (items 13-14), and strut bore positions have moved outward. The lever's width and strut positions no longer match.

**Fix:** Widen the lever plate from 80.0mm to 140.0mm and increase height from 65.0mm to 68.6mm (matching pump tray height). Move strut center positions to match the pump tray strut bore centers exactly.

**v2 dimensions (unchanged):** plate thickness 4.0mm, strut cross-section 6.0x6.0mm, strut length 90.0mm, corner radii 2.0mm, elephant's foot chamfer 0.3mm x 45 deg.

**v3 changes:**
- Plate width: 80.0mm -> 140.0mm
- Plate height: 65.0mm -> 68.6mm (matches pump tray height; contains struts at Z=63.6)
- Strut TL center: (9.0, 60.0) -> (4.0, 63.6)
- Strut TR center: (71.0, 60.0) -> (136.0, 63.6)
- Strut BL center: (9.0, 5.0) -> (4.0, 5.0)
- Strut BR center: (71.0, 5.0) -> (136.0, 5.0)

---

## Feature List

### Feature 1 -- Plate Body

| Property | Value |
|----------|-------|
| Operation | Add (base body) |
| Geometry | Rectangular solid |
| Dimensions | 140.0 (X) x 4.0 (Y) x 68.6 (Z) mm |
| Position | X:[0, 140.0] Y:[0, 4.0] Z:[0, 68.6] |
| Justification | Structural: rigid load-transfer body between user finger contact surface (Y=0) and strut attachment zone (Y=4). Width 140.0mm matches interior plate width (pump tray, coupler tray) so strut X positions align. Height 68.6mm matches pump tray height so strut Z positions align. |

### Feature 2 -- Plate Perimeter Corner Radii

| Property | Value |
|----------|-------|
| Operation | Remove (fillet) |
| Geometry | Convex cylindrical fillet on four vertical (Y-parallel) plate edges |
| Affected edges | (X=0, Z=0), (X=140.0, Z=0), (X=0, Z=68.6), (X=140.0, Z=68.6); each runs Y=0 to Y=4.0 |
| Radius | 2.0mm |
| Justification | Design language consistency with release plate. Prevents sharp corners from snagging front panel hole edges. |

### Feature 3 -- Plate Bottom Chamfer (Elephant's Foot)

| Property | Value |
|----------|-------|
| Operation | Remove (chamfer) |
| Geometry | 0.3mm x 45 deg chamfer on the bottom front edge of the plate |
| Position | Edge at Z=0, Y=0, running full X width |
| Justification | Requirements.md: elephant's foot prevention. Plate prints face-down; Z=0 in part frame maps to the build plate edge. |

### Feature 4 -- Strut TL (Top-Left)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (4.0, 63.6) |
| Extents X | [1.0, 7.0] |
| Extents Z | [60.6, 66.6] |
| Extents Y | [4.0, 94.0] |
| Justification | Structural: transmits pull force. Position matches pump tray strut bore S-TL center (4.0, 63.6). |

### Feature 5 -- Strut TR (Top-Right)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (136.0, 63.6) |
| Extents X | [133.0, 139.0] |
| Extents Z | [60.6, 66.6] |
| Extents Y | [4.0, 94.0] |
| Justification | Structural: transmits pull force. Position matches pump tray strut bore S-TR center (136.0, 63.6). |

### Feature 6 -- Strut BL (Bottom-Left)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (4.0, 5.0) |
| Extents X | [1.0, 7.0] |
| Extents Z | [2.0, 8.0] |
| Extents Y | [4.0, 94.0] |
| Justification | Structural: transmits pull force. Position matches pump tray strut bore S-BL center (4.0, 5.0). |

### Feature 7 -- Strut BR (Bottom-Right)

| Property | Value |
|----------|-------|
| Operation | Add (rectangular prism, unioned to plate rear face) |
| Cross-section | 6.0mm (X) x 6.0mm (Z) |
| Length (Y) | 90.0mm |
| Center (X, Z) | (136.0, 5.0) |
| Extents X | [133.0, 139.0] |
| Extents Z | [2.0, 8.0] |
| Extents Y | [4.0, 94.0] |
| Justification | Structural: transmits pull force. Position matches pump tray strut bore S-BR center (136.0, 5.0). |

---

## Clearance Checks

**Struts vs. plate edges (minimum wall thickness 0.8mm required):**

| Strut | Nearest edge | Strut edge pos | Plate edge pos | Wall thickness |
|-------|-------------|----------------|----------------|----------------|
| TL | X=0 (left) | 1.0 | 0.0 | 1.0mm |
| TL | Z=68.6 (top) | 66.6 | 68.6 | 2.0mm |
| TR | X=140.0 (right) | 139.0 | 140.0 | 1.0mm |
| TR | Z=68.6 (top) | 66.6 | 68.6 | 2.0mm |
| BL | X=0 (left) | 1.0 | 0.0 | 1.0mm |
| BL | Z=0 (bottom) | 2.0 | 0.0 | 2.0mm |
| BR | X=140.0 (right) | 139.0 | 140.0 | 1.0mm |
| BR | Z=0 (bottom) | 2.0 | 0.0 | 2.0mm |

All at or above 0.8mm minimum. Passes.

**Strut centers vs. pump tray bore centers (must match exactly):**

| Strut | Lever strut center (X, Z) | Pump tray bore center (X, Z) | Match? |
|-------|---------------------------|------------------------------|--------|
| TL | (4.0, 63.6) | (4.0, 63.6) | Yes |
| TR | (136.0, 63.6) | (136.0, 63.6) | Yes |
| BL | (4.0, 5.0) | (4.0, 5.0) | Yes |
| BR | (136.0, 5.0) | (136.0, 5.0) | Yes |

---

## FDM Check

No overhangs. Print orientation: front face (Y=0) down. Struts extend upward in print Z direction. All strut faces are vertical walls. Corner radii are in-plane curves parallel to print Z. Bottom chamfer at 45 deg is at the printability limit. Minimum plate material between strut attachment and plate edge is 1.0mm (exceeds 0.8mm non-structural minimum). No supports required.

---

## Feature Traceability

| Feature | Justification |
|---------|---------------|
| Plate width increase (80.0 -> 140.0mm) | Build sequence line: "match the new width." Interior plates are now 140.0mm wide. |
| Plate height increase (65.0 -> 68.6mm) | Matches pump tray height so strut Z positions (63.6, 5.0) fit within the plate. Strut at Z=63.6 extends to Z=66.6; plate must be at least 66.6mm + wall material. |
| Strut X positions moved (9.0/71.0 -> 4.0/136.0) | Build sequence line: "move its struts to align with the new strut bore positions on the pump tray." Pump tray bore centers at X=4.0 and X=136.0. |
| Strut Z positions moved (60.0/5.0 -> 63.6/5.0) | Top strut Z changed to match pump tray bore Z=63.6. Bottom strut Z unchanged at 5.0 (already matches pump tray). |
| All other features unchanged | Corner radii, chamfer, strut cross-section, strut length, plate thickness unchanged per scope. |
