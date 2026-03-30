# Coupler Tray v3 — Widened Top and Bottom Plates

**Build sequence line:** Widen coupler tray — match the pump tray's new width and strut bore positions.

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray — Top Plate |
| Piece count | 1 |
| Outer dimensions | 140.0mm (X) x 6.08mm (Y) x 68.6mm (Z) |
| Material | PLA or PETG |

| Property | Value |
|----------|-------|
| Part name | Coupler Tray — Bottom Plate |
| Piece count | 1 |
| Outer dimensions | 140.0mm (X) x 6.08mm (Y) x 68.6mm (Z) |
| Material | PLA or PETG |

The two plates are identical in XZ footprint. Each is 6.08mm thick in Y. When stacked face-to-face, total Y = 12.16mm, matching the coupler center body length (12.16mm from John Guest geometry description).

---

## What Changed (v2 to v3)

**Reason:** The pump tray was widened to 140.0mm in item 13 and its strut bores were repositioned. The coupler tray must match so that all interior plates share the same width and strut positions.

**v2 dimensions (unchanged):** plate thickness 6.08mm per half, plate height 68.6mm, 4 coupler through-bores 9.5mm dia, 4 strut bores 6.4x6.4mm.

**v3 changes:**
- Plate width: 137.2mm -> 140.0mm
- Coupler bore X positions shift +1.4mm (stay centered in widened plate): 43.1 -> 44.5, 60.1 -> 61.5, 77.1 -> 78.5, 94.1 -> 95.5
- Strut bore X positions match pump tray: 10.0 -> 4.0 (left), 127.2 -> 136.0 (right)
- Strut bore Z positions unchanged: 63.6 (top), 5.0 (bottom)

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
X: width axis — left to right, 0..140.0mm
Y: thickness axis — outer face (Y=0) to mating face (Y=6.08mm)
Z: height axis — bottom to top, 0..68.6mm
Bounding envelope: 140.0 x 6.08 x 68.6 mm -> X:[0,140.0] Y:[0,6.08] Z:[0,68.6]
```

Print orientation: outer face (Y=0) down on build plate.

## Coordinate System — Bottom Plate

Origin: bottom-left corner of the outer face (the face away from the mating surface).

```
X: width axis — left to right, 0..140.0mm
Y: thickness axis — outer face (Y=0) to mating face (Y=6.08mm)
Z: height axis — bottom to top, 0..68.6mm
Bounding envelope: 140.0 x 6.08 x 68.6 mm -> X:[0,140.0] Y:[0,6.08] Z:[0,68.6]
```

Print orientation: outer face (Y=0) down on build plate.

---

## Features — Top Plate

### Feature T1 — Base Plate Body

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 140.0mm |
| Thickness (Y) | 6.08mm |
| Height (Z) | 68.6mm |
| All corners | Square (no chamfer, no fillet) |

### Feature T2 — Coupler Through-Bores (4x)

Through-holes for the coupler center body. Hole axis parallel to Y. Each bore runs from Y=0 (outer face) to Y=6.08mm (mating face).

| Hole ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| H1 | 44.5 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |
| H2 | 61.5 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |
| H3 | 78.5 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |
| H4 | 95.5 | 34.3 | 9.5mm | Through (Y=0 to Y=6.08mm) |

Derivation: Old positions (43.1, 60.1, 77.1, 94.1) were centered in the 137.2mm plate (center X=68.6). New plate center X=70.0. Shift = +1.4mm. Coupler center-to-center spacing (17.0mm) unchanged.

### Feature T3 — Strut Bores (4x)

Rectangular through-holes for the release plate struts to pass through. Bore axis parallel to Y. Bores run from Y=0 to Y=6.08mm. Positions match pump tray v3.

| Bore ID | X (mm) | Z (mm) | Size (X x Z) | Depth |
|---------|--------|--------|---------------|-------|
| S-TL | 4.0 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |
| S-TR | 136.0 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |
| S-BL | 4.0 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |
| S-BR | 136.0 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=6.08mm) |

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

**Strut bores vs. coupler bores:**

Nearest strut bore to nearest coupler bore: S-TL (4.0, 63.6) to H1 (44.5, 34.3). Center-to-center distance = sqrt((44.5-4.0)^2 + (34.3-63.6)^2) = sqrt(1640.25 + 858.49) = 49.98mm. Strut bore half-width = 3.2mm, coupler bore radius = 4.75mm. Edge-to-edge gap = 49.98 - 3.2 - 4.75 = 42.03mm. No interference.

---

## FDM Check

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Plate thickness | Wall thickness | 6.08mm | 1.2mm structural min | Yes |
| Coupler bore span | Bridge span | 9.5mm | 15mm max | Yes |
| Strut bore span | Bridge span | 6.4mm | 15mm max | Yes |
| Strut bore min wall to plate edge | Wall thickness | 0.8mm (X direction) | 0.8mm min | Yes |
| All faces | Overhang | Vertical or on build plate | <=45 deg | Yes |

No overhangs. No supports required. Print with outer face (Y=0) down.

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| Plate width 140.0mm | Build sequence: "match the pump tray's new width." Pump tray v3 is 140.0mm wide. |
| Plate thickness 6.08mm per half | Half of coupler center body length (12.16mm / 2). Unchanged from v2. |
| Plate height 68.6mm | Unchanged from v2 — matches pump tray height. |
| 4x coupler through-bores, 9.5mm dia | Coupler center body clearance (9.31mm OD + clearance). Positions re-centered for new width. |
| 4x strut bores, 6.4 x 6.4 mm | Build sequence: "match ... strut bore positions." Positions match pump tray v3: (4.0, 63.6), (136.0, 63.6), (4.0, 5.0), (136.0, 5.0). |
| Plain flat mating faces | Scope: no dovetail geometry (deferred to Phase 9). |
