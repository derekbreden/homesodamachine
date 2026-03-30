# Coupler Tray — Split into Top and Bottom Plates

**Deliverable:** Split coupler tray into two halves (top plate and bottom plate) that stack face-to-face. Every coupler passes through both halves. Each half has half-depth pockets so that when the halves are pressed together, they capture the narrow center section of each coupler, and the wider shoulders on each end provide axial retention. Plain flat mating faces — no dovetail geometry. Through-holes for strut bores in both halves.

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray — Top Plate |
| Piece count | 1 |
| Outer dimensions | 137.2mm (X) x 6.08mm (Y) x 68.6mm (Z) |
| Material | PLA or PETG |

| Property | Value |
|----------|-------|
| Part name | Coupler Tray — Bottom Plate |
| Piece count | 1 |
| Outer dimensions | 137.2mm (X) x 6.08mm (Y) x 68.6mm (Z) |
| Material | PLA or PETG |

The two plates are identical in XZ footprint. Each is 6.08mm thick in Y. When stacked face-to-face, total Y = 12.16mm, matching the coupler center body length (12.16mm from John Guest geometry description).

---

## How Coupler Capture Works

The John Guest PP0408W union has a barbell profile:
- Body end (shoulder) OD: 15.10mm, length: 12.08mm each side
- Central body OD: 9.31mm, length: 12.16mm

Each plate has 9.5mm diameter through-bores at the coupler positions. The center body (9.31mm) passes through with clearance. The shoulders (15.10mm) cannot pass through the 9.5mm bore. When the two plates are pressed face-to-face, the combined bore length equals the center body length (12.16mm). Each shoulder sits against the outer face of its respective plate, preventing axial movement. The coupler is sandwiched and cannot slide in either direction.

---

## Coordinate System — Top Plate

Origin: bottom-left corner of the outer face (the face away from the mating surface).

```
X: width axis — left to right, 0..137.2mm
Y: thickness axis — outer face (Y=0) to mating face (Y=6.08mm)
Z: height axis — bottom to top, 0..68.6mm
Bounding envelope: 137.2 x 6.08 x 68.6 mm -> X:[0,137.2] Y:[0,6.08] Z:[0,68.6]
```

Print orientation: outer face (Y=0) down on build plate.

## Coordinate System — Bottom Plate

Origin: bottom-left corner of the outer face (the face away from the mating surface).

```
X: width axis — left to right, 0..137.2mm
Y: thickness axis — outer face (Y=0) to mating face (Y=6.08mm)
Z: height axis — bottom to top, 0..68.6mm
Bounding envelope: 137.2 x 6.08 x 68.6 mm -> X:[0,137.2] Y:[0,6.08] Z:[0,68.6]
```

Print orientation: outer face (Y=0) down on build plate.

---

## Features — Top Plate

### Feature T1 — Base Plate Body

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 137.2mm |
| Thickness (Y) | 6.08mm |
| Height (Z) | 68.6mm |
| All corners | Square (no chamfer, no fillet) |

### Feature T2 — Coupler Through-Bores (4x)

Through-holes for the coupler center body. Hole axis parallel to Y. Each bore runs from Y=0 (outer face) to Y=6.08mm (mating face).

| Hole ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| H1 | 43.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |
| H2 | 60.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |
| H3 | 77.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |
| H4 | 94.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |

### Feature T3 — Strut Bores (4x)

Rectangular through-holes for the release plate struts to pass through. Bore axis parallel to Y. Bores run from Y=0 to Y=6.08mm.

| Bore ID | X (mm) | Z (mm) | Size (X x Z) | Depth |
|---------|--------|--------|---------------|-------|
| S-TL | 10.0 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |
| S-TR | 127.2 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |
| S-BL | 10.0 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |
| S-BR | 127.2 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |

---

## Features — Bottom Plate

The bottom plate is geometrically identical to the top plate. Same XZ footprint, same Y thickness, same bore positions and sizes.

### Feature B1 — Base Plate Body

Identical to Feature T1.

### Feature B2 — Coupler Through-Bores (4x)

Identical to Feature T2 (same positions, diameters, through full Y thickness).

### Feature B3 — Strut Bores (4x)

Identical to Feature T3 (same positions, sizes, through full Y thickness).

---

## Assembly

The two plates are mirror images about their mating faces. The coupler is placed with its center body spanning the combined bore. The plates are pressed together face-to-face:

1. Place couplers so the center body spans across where the mating faces will meet.
2. Bring the two plates together, mating faces inward, coupler center bodies in the combined bores.
3. Each shoulder (15.10mm OD) sits against the outer face of its respective plate, retained axially.

The mating faces are plain flat surfaces — no dovetail, no detent, no interlock geometry.

---

## Interference Check — Strut Bores vs. Coupler Bores

Same as previous version. Nearest strut bore to nearest coupler bore: 44.2mm center-to-center, 33.0mm edge-to-edge. No interference.

---

## FDM Check

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Plate thickness | Wall thickness | 6.08mm | 1.2mm structural min | Yes |
| Coupler bore span | Bridge span | 9.5mm | 15mm max | Yes |
| Strut bore span | Bridge span | 6.4mm | 15mm max | Yes |
| Strut bore min wall to plate edge | Wall thickness | 1.8mm (Z direction) | 1.2mm min | Yes |
| All faces | Overhang | Vertical or on build plate | <=45 deg | Yes |

No overhangs. No supports required. Print with outer face (Y=0) down.

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| Plate footprint 137.2 x 68.6mm | Pump tray footprint match (unchanged). |
| Plate thickness 6.08mm per half | Half of coupler center body length (12.16mm / 2). Captures half the center body per plate. |
| 4x coupler through-bores, 9.5mm dia | Coupler center body clearance (9.31mm OD + clearance). Same diameter as previous versions. |
| 4x strut bores, 6.4 x 6.4 mm | Release plate strut pass-through. Same positions as previous version. |
| Plain flat mating faces | Build sequence scope: no dovetail geometry. |
