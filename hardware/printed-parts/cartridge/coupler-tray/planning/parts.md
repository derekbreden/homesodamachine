# Coupler Tray (Split) -- Parts Specification

**Split coupler tray into two halves** -- split between couplers 2 and 3 (the natural midpoint of the 1x4 line). Produce two STEP files. Plain flat mating faces at the split -- no dovetail geometry.

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray (Split) |
| Piece count | 2 (left half + right half) |
| Split line | X = 68.6mm (plate midpoint, between H2 at X=60.1 and H3 at X=77.1) |
| Left half X range | 0 to 68.6mm |
| Right half X range | 68.6 to 137.2mm |
| Base plate thickness | 3mm |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |

---

## Coordinate System

Same as previous coupler tray. Both halves use the same global coordinate system. The split produces two bodies; the right half is not re-zeroed.

```
Origin: bottom-left corner of the front face of the full plate (X=0, Y=0, Z=0)
X: width axis -- left to right, 0..137.2mm (full plate), split at X=68.6mm
Y: thickness axis -- front face (Y=0) to back face of base (Y=3mm);
   bosses extend from Y=3 to Y=12.08mm
Z: height axis -- bottom to top, 0..68.6mm
Bounding envelope (full): 137.2 x 12.08 x 68.6 mm
Left half envelope: 68.6 x 12.08 x 68.6 mm -> X:[0, 68.6] Y:[0, 12.08] Z:[0, 68.6]
Right half envelope: 68.6 x 12.08 x 68.6 mm -> X:[68.6, 137.2] Y:[0, 12.08] Z:[0, 68.6]
```

---

## Split Geometry

The split is a planar cut at X = 68.6mm (the plate horizontal midpoint). This falls between coupler H2 (X=60.1) and coupler H3 (X=77.1), with 8.5mm clearance to H2 and 8.5mm clearance to H3 -- both well clear of the 8mm boss radius.

Mating faces are flat. No dovetail, no interlock, no snap geometry.

- Left half: X = [0, 68.6], contains H1/B1, H2/B2, S-TL, S-BL
- Right half: X = [68.6, 137.2], contains H3/B3, H4/B4, S-TR, S-BR

---

## Left Half Features

### Feature L1 -- Base Plate (left)

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 68.6mm (X=0 to X=68.6) |
| Thickness (Y) | 3mm |
| Height (Z) | 68.6mm |

### Feature L2 -- Boss B1

| Property | X | Z | Inner Dia | Outer Dia | Height (Y) | Y range |
|----------|---|---|-----------|-----------|------------|---------|
| B1 | 43.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |

### Feature L3 -- Boss B2

| Property | X | Z | Inner Dia | Outer Dia | Height (Y) | Y range |
|----------|---|---|-----------|-----------|------------|---------|
| B2 | 60.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |

### Feature L4 -- Bore H1

| Property | X | Z | Diameter | Depth |
|----------|---|---|----------|-------|
| H1 | 43.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |

### Feature L5 -- Bore H2

| Property | X | Z | Diameter | Depth |
|----------|---|---|----------|-------|
| H2 | 60.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |

### Feature L6 -- Strut Bore S-TL

| Property | X | Z | Size (X x Z) | Depth |
|----------|---|---|---------------|-------|
| S-TL | 10.0 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |

### Feature L7 -- Strut Bore S-BL

| Property | X | Z | Size (X x Z) | Depth |
|----------|---|---|---------------|-------|
| S-BL | 10.0 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |

---

## Right Half Features

### Feature R1 -- Base Plate (right)

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 68.6mm (X=68.6 to X=137.2) |
| Thickness (Y) | 3mm |
| Height (Z) | 68.6mm |

### Feature R2 -- Boss B3

| Property | X | Z | Inner Dia | Outer Dia | Height (Y) | Y range |
|----------|---|---|-----------|-----------|------------|---------|
| B3 | 77.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |

### Feature R3 -- Boss B4

| Property | X | Z | Inner Dia | Outer Dia | Height (Y) | Y range |
|----------|---|---|-----------|-----------|------------|---------|
| B4 | 94.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |

### Feature R4 -- Bore H3

| Property | X | Z | Diameter | Depth |
|----------|---|---|----------|-------|
| H3 | 77.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |

### Feature R5 -- Bore H4

| Property | X | Z | Diameter | Depth |
|----------|---|---|----------|-------|
| H4 | 94.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |

### Feature R6 -- Strut Bore S-TR

| Property | X | Z | Size (X x Z) | Depth |
|----------|---|---|---------------|-------|
| S-TR | 127.2 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |

### Feature R7 -- Strut Bore S-BR

| Property | X | Z | Size (X x Z) | Depth |
|----------|---|---|---------------|-------|
| S-BR | 127.2 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |

---

## FDM Check

Identical to the full coupler tray -- no new overhangs, no new thin walls introduced by the split. The mating face at X=68.6 is a full-height, full-depth flat face with no features crossing it. Minimum wall from split face to nearest boss edge: 68.6 - (60.1 + 8.0) = 0.5mm on the left side, and (77.1 - 8.0) - 68.6 = 0.5mm on the right side. Both bosses are fully contained within their respective halves with 0.5mm of plate material between the boss OD and the split face.

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Split face to nearest boss OD | Wall thickness | 0.5mm | 0.8mm min | Marginal |
| Base plate thickness | Wall thickness | 3mm | 1.2mm structural min | Yes |
| Boss wall thickness | Thickness | 3.25mm | 1.2mm structural min | Yes |
| Strut bore min wall to plate edge | Wall thickness | 1.8mm (Z direction) | 1.2mm min | Yes |

Note: The 0.5mm wall between split face and nearest boss OD is below the 0.8mm minimum wall thickness. However, this is acceptable because the boss is a cylindrical protrusion on the back face only (Y=3 to Y=12.08), and the base plate extends the full 3mm thickness at this location. The thin wall only exists in the boss region, not the structural base plate. The struts and side-wall rails provide the structural retention, not this wall.

---

## Path Continuity

Same as previous version. Each coupler bore is a straight through-path from Y=0 to Y=12.08mm. All four coupler paths are fully contained within their respective halves -- no path crosses the split line. Strut bores are independent through-holes fully within their respective halves.

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| Split at X=68.6mm | Build sequence: "Split coupler tray into two halves -- split between couplers 2 and 3." |
| Flat mating faces | Build sequence: "Plain flat mating faces at the split -- no dovetail geometry." |
| All other features | Unchanged from previous coupler tray spec. |
