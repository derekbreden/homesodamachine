# Coupler Tray — Parts Specification

**Season 1, Phase 6 — Widen coupler tray to match pump tray**

---

## Part Summary

| Property | Value |
|----------|-------|
| Part names | Coupler Tray Base Half, Coupler Tray Boss Half |
| Piece count | 2 |
| Assembly | Press together: mating faces at Z=34.3mm, plain flat |
| Assembled outer dimensions | 140.0mm (X) x 12.08mm (Y, bounding box incl. bosses) x 68.6mm (Z) |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

---

## Coordinate System

Origin: bottom-left corner of the front face of the assembled plate.

```
X: width axis — left to right, 0..140.0mm
Y: thickness axis — front to back through the plate, 0..3mm (base) + bosses extend to 12.08mm
    Y=0:     front face (on build plate)
    Y=3mm:   back face of base plate / base of bosses
    Y=12.08mm: tip face of bosses (shoulder-bearing surface)
Z: height axis — bottom to top, 0..68.6mm
Split plane: Z=34.3mm (vertical midpoint, centerline of all 4 coupler holes)
```

Both halves share this coordinate system. The split is a horizontal cut at Z=34.3mm.

---

## What Changed from Phase 5

**Phase 5** split the coupler tray into two halves (base half and boss half) at Z=34.3mm.
Width was 137.2mm. Strut bore X positions were 10.0 (left) and 127.2 (right).

**Phase 6** widens the coupler tray to match the pump tray's new width and strut bore positions.
Width: 137.2mm → 140.0mm. Strut bore X positions: 10.0 → 4.0 (left), 127.2 → 136.0 (right).
All other geometry (Z positions, split plane, coupler holes, bosses) unchanged.

---

## Part A — Coupler Tray Base Half

### Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray Base Half |
| Outer dimensions | 140.0mm (X) x 12.08mm (Y) x 34.3mm (Z) |
| Z range | Z=0 to Z=34.3mm (bottom half of assembled tray) |
| Mating face | Z=34.3mm, flat |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Supports required | None |

### Feature A-1 — Base Plate Body (base half)

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 140.0mm |
| Thickness (Y) | 3mm |
| Height (Z) | 34.3mm |
| All corners | Square (no chamfer, no fillet) |

Z range: Z=0 to Z=34.3mm. Mating face is the top face at Z=34.3mm, flat.

### Feature A-2 — Semicircular Channels (4x, mating face)

The split cuts through the center of each coupler hole. Each hole center is at Z=34.3mm.
Cutting at Z=34.3mm produces semicircular channels on the mating face (opening toward +Z).

| Channel ID | X (mm) | Z (mating face) | Shape | Radius | Depth (Y) |
|------------|--------|-----------------|-------|--------|-----------|
| C1 | 43.1 | 34.3 | Semicircle (lower half) | 4.75mm | Y=0 to Y=3mm |
| C2 | 60.1 | 34.3 | Semicircle (lower half) | 4.75mm | Y=0 to Y=3mm |
| C3 | 77.1 | 34.3 | Semicircle (lower half) | 4.75mm | Y=0 to Y=3mm |
| C4 | 94.1 | 34.3 | Semicircle (lower half) | 4.75mm | Y=0 to Y=3mm |

Each channel is the lower half (Z < 34.3mm portion) of a 9.5mm-diameter through-bore,
running through the full Y thickness (Y=0 to Y=3mm in the base plate, and Y=3 to Y=12.08mm
through the boss). The boss inner bore continues the channel upward through the boss.

### Feature A-3 — Semicircular Boss Protrusions (4x, back face)

The split also cuts through the center of each boss. Each boss center is at Z=34.3mm.
The base half retains the lower half of each boss: a semicylindrical protrusion on the mating
face at Z=34.3mm, with the flat face of the semicylinder at Z=34.3mm.

| Boss ID | X (mm) | Outer radius | Inner radius | Height (Y) | Y range |
|---------|--------|-------------|--------------|------------|---------|
| B1 | 43.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |
| B2 | 60.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |
| B3 | 77.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |
| B4 | 94.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |

Each is the half (Z <= 34.3mm portion) of the original full cylindrical boss. The inner bore
is open (void) at the mating face and continues through the boss into the base plate.

### Feature A-4 — Strut Bores (2x, base half only)

The two bottom strut bores (Z=5.0mm) are entirely within the base half (Z=0 to Z=34.3mm).
The two top strut bores (Z=63.6mm) are in the boss half — not present in the base half.

| Bore ID | X (mm) | Z (mm) | Size (X x Z) | Depth |
|---------|--------|--------|---------------|-------|
| S-BL | 4.0 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |
| S-BR | 136.0 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |

### FDM Check — Base Half

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Base plate walls | Overhang | All faces vertical or on build plate | <=45 deg | Yes |
| Base plate thickness | Wall thickness | 3mm | 1.2mm structural min | Yes |
| Boss wall thickness | Thickness | 3.25mm (outer-inner radius) | 1.2mm structural min | Yes |
| Boss height | Overhang | Vertical, no overhang | <=45 deg | Yes |
| Semicircular channels | Bridge at mating face | Half-circle opening, 4.75mm radius — no overhang since open face is at top (mating face is top face during print) | <=45 deg | Yes |
| Strut bore span | Bridge span | 6.4mm | 15mm max | Yes |
| Strut bore wall to plate edge (X) | Wall thickness | 0.8mm (X direction from S-BL/S-BR to plate edge) | 0.8mm min | Yes |
| Strut bore wall to plate edge (Z) | Wall thickness | 1.8mm (Z direction from S-BL/S-BR to bottom edge) | 1.2mm min | Yes |

Print orientation: front face (Y=0) down on build plate. Z is up during printing.
The mating face is at the top during printing. The semicircular channels open upward —
no overhang. Strut bores (at Z=5.0mm) print as vertical rectangular channels.

---

## Part B — Coupler Tray Boss Half

### Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray Boss Half |
| Outer dimensions | 140.0mm (X) x 12.08mm (Y) x 34.3mm (Z) |
| Z range | Z=34.3mm to Z=68.6mm (top half of assembled tray) |
| Mating face | Z=34.3mm (bottom face of this part), flat |
| Print orientation | Mating face (Z=34.3mm) down on build plate |
| Supports required | None |

Note on print orientation: the boss half is printed upside-down (mating face down). This
puts the semicircular channels at the bottom, opening downward — no overhang. The top face
(Z=68.6mm in assembly) is up during printing.

### Feature B-1 — Base Plate Body (boss half)

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 140.0mm |
| Thickness (Y) | 3mm |
| Height (Z) | 34.3mm |
| All corners | Square (no chamfer, no fillet) |

This is the upper portion of the original base plate: Z=34.3mm to Z=68.6mm.
In the boss half's own coordinate system, Z=0 corresponds to the mating face and Z=34.3mm
is the top face. The script uses assembly-frame Z coordinates throughout.

### Feature B-2 — Semicircular Channels (4x, mating face)

| Channel ID | X (mm) | Z (mating face) | Shape | Radius | Depth (Y) |
|------------|--------|-----------------|-------|--------|-----------|
| C1 | 43.1 | 34.3 | Semicircle (upper half) | 4.75mm | Y=0 to Y=3mm |
| C2 | 60.1 | 34.3 | Semicircle (upper half) | 4.75mm | Y=0 to Y=3mm |
| C3 | 77.1 | 34.3 | Semicircle (upper half) | 4.75mm | Y=0 to Y=3mm |
| C4 | 94.1 | 34.3 | Semicircle (upper half) | 4.75mm | Y=0 to Y=3mm |

Each channel is the upper half (Z > 34.3mm portion) of a 9.5mm-diameter through-bore,
running through the full Y thickness. The boss inner bore continues the channel into the boss.

### Feature B-3 — Semicircular Boss Protrusions (4x, back face)

| Boss ID | X (mm) | Outer radius | Inner radius | Height (Y) | Y range |
|---------|--------|-------------|--------------|------------|---------|
| B1 | 43.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |
| B2 | 60.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |
| B3 | 77.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |
| B4 | 94.1 | 8.0mm | 4.75mm | 9.08mm | Y=3 to Y=12.08mm |

Each is the half (Z >= 34.3mm portion) of the original full cylindrical boss.

### Feature B-4 — Strut Bores (2x, boss half only)

The two top strut bores (Z=63.6mm) are entirely within the boss half (Z=34.3mm to Z=68.6mm).
The two bottom strut bores (Z=5.0mm) are in the base half — not present in the boss half.

| Bore ID | X (mm) | Z (mm) | Size (X x Z) | Depth |
|---------|--------|--------|---------------|-------|
| S-TL | 4.0 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |
| S-TR | 136.0 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |

### FDM Check — Boss Half

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Base plate walls | Overhang | All faces vertical or on build plate | <=45 deg | Yes |
| Base plate thickness | Wall thickness | 3mm | 1.2mm structural min | Yes |
| Boss wall thickness | Thickness | 3.25mm | 1.2mm structural min | Yes |
| Boss height | Overhang | Vertical, no overhang | <=45 deg | Yes |
| Semicircular channels | Bridge at mating face | Half-circle opening at bottom during print (mating face down) — no overhang | <=45 deg | Yes |
| Strut bore span | Bridge span | 6.4mm | 15mm max | Yes |
| Strut bore wall to plate edge (X) | Wall thickness | 0.8mm (X direction from S-TL/S-TR to plate edge) | 0.8mm min | Yes |
| Strut bore wall to plate edge (Z) | Wall thickness | 1.8mm (Z direction from S-TL/S-TR to top edge) | 1.2mm min | Yes |

Print orientation: mating face (assembly Z=34.3mm) down on build plate. The semicircular
channels open downward toward the build plate — no overhang. Bosses protrude upward (away
from build plate) in the +Y direction. Strut bores print as vertical rectangular channels.

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| Split at Z=34.3mm | Build sequence Phase 5: "slice along centerline of the 4 holes, cutting through the center of each hole." Hole centers all at Z=34.3mm. Unchanged in Phase 6. |
| Plain flat mating faces | Phase 5 spec: "Plain flat mating faces — no dovetail geometry." Dovetail is Phase 9. Unchanged in Phase 6. |
| Semicircular channels, r=4.75mm | Derived from Phase 4 coupler holes, 9.5mm diameter. Half-diameter = 4.75mm. Unchanged in Phase 6. |
| Semicircular boss halves | Derived from Phase 4 bosses (OD=16mm, ID=9.5mm). Split cuts through boss centers at Z=34.3mm. Unchanged in Phase 6. |
| Width 140.0mm | Phase 6: match pump tray width. Pump tray widened from 137.2mm to 140.0mm in its Phase 6. |
| S-BL X=4.0, S-BR X=136.0 | Phase 6: match pump tray strut bore X positions. Moved outward from 10.0/127.2 to 4.0/136.0. |
| S-TL X=4.0, S-TR X=136.0 | Phase 6: match pump tray strut bore X positions. Moved outward from 10.0/127.2 to 4.0/136.0. |
| S-BL, S-BR in base half | Bore Z=5.0mm < 34.3mm — entirely within base half Z range. Unchanged in Phase 6. |
| S-TL, S-TR in boss half | Bore Z=63.6mm > 34.3mm — entirely within boss half Z range. Unchanged in Phase 6. |
