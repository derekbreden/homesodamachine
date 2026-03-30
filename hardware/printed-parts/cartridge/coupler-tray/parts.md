# Coupler Tray — Parts Specification

**Season 1, Phase 4 — Add strut bores to coupler tray**

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray (with strut bores) |
| Piece count | 1 |
| Outer dimensions | 137.2mm (X) x 12.08mm (Y, bounding box incl. bosses) x 68.6mm (Z) |
| Base plate thickness | 3mm |
| Features | Base plate + 4x coupler capture holes + 4x bosses (back face) + 4x strut bores |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

---

## Coordinate System

Origin: bottom-left corner of the front face of the plate.

```
X: width axis — left to right, 0..137.2mm
Y: thickness axis — front to back through the plate, 0..3mm (base) + bosses extend to 12.08mm
    Y=0:     front face (on build plate)
    Y=3mm:   back face of base plate / base of bosses
    Y=12.08mm: tip face of bosses (shoulder-bearing surface)
Z: height axis — bottom to top, 0..68.6mm
Bounding envelope: 137.2 x 12.08 x 68.6 mm -> X:[0,137.2] Y:[0,12.08] Z:[0,68.6]
```

Print orientation: front face (XZ plane, Y=0) down on the build plate. Z is up during printing.
Hole axes and boss axes are parallel to Y, which becomes print Z — holes and bosses print as
vertical cylinders. Bosses protrude upward from the back of the base plate and print without
overhangs. Strut bores are rectangular through-holes through the 3mm base plate, parallel to Y.

---

## What Changed from v3

**v3** had the base plate, 4 coupler capture holes in a 1x4 row, and 4 bosses. No strut bores.

**This version** adds 4 rectangular strut bores at the plate corners, matching the release plate
strut positions and the pump tray strut bore positions. Strut cross-section is 6.0 x 6.0 mm;
bores are 6.4 x 6.4 mm (0.2mm clearance per side, per requirements.md sliding fit tolerance).

All other geometry is unchanged from v3.

---

## Feature 1 — Base Plate Body

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 137.2mm |
| Thickness (Y) | 3mm |
| Height (Z) | 68.6mm |
| All corners | Square (no chamfer, no fillet) |

**Justification:** Width 137.2mm and height 68.6mm match the pump tray footprint so both parts
slide into the same side-wall rails. Thickness 3mm matches the pump tray thickness.

---

## Feature 2 — Coupler Capture Holes (4x)

All holes are through-holes through the base plate. Hole axis is parallel to Y.
Entry at Y=0, exit at Y=3mm. The hole continues as the inner bore of the boss (Y=3 to Y=12.08).

**Layout: 1x4 row along X, centered in the plate.**

- All 4 holes at Z = 34.3mm (plate vertical midpoint)
- 17mm center-to-center spacing along X
- Row centered at X = 68.6mm (plate horizontal midpoint)

| Hole ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| H1 | 43.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm, continuous with boss bore) |
| H2 | 60.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm, continuous with boss bore) |
| H3 | 77.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm, continuous with boss bore) |
| H4 | 94.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm, continuous with boss bore) |

---

## Feature 3 — Bosses (4x, back face)

Bosses are hollow cylindrical protrusions on the back face (Y=3mm), protruding in the +Y
direction. The front face remains flat (no bosses), keeping it flat on the build plate.

| Boss ID | X (mm) | Z (mm) | Inner Dia | Outer Dia | Height (Y) | Y range |
|---------|--------|--------|-----------|-----------|------------|---------|
| B1 | 43.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B2 | 60.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B3 | 77.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B4 | 94.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |

---

## Feature 4 — Strut Bores (4x, through base plate)

Rectangular through-holes in the base plate for the release plate struts to pass through.
Bore axis is parallel to Y. Bores run from Y=0 to Y=3mm (full base plate thickness).

Strut cross-section (release plate): 6.0 x 6.0 mm.
Bore size: 6.4 x 6.4 mm (0.2mm clearance per side per requirements.md sliding fit).
Bore positions match release plate strut centers and pump tray strut bore centers.

| Bore ID | X (mm) | Z (mm) | Size (X x Z) | Depth |
|---------|--------|--------|---------------|-------|
| S-TL | 10.0 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |
| S-TR | 127.2 | 63.6 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |
| S-BL | 10.0 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |
| S-BR | 127.2 | 5.0 | 6.4 x 6.4 mm | Through (Y=0 to Y=3mm) |

### Interference Check — Strut Bores vs. Coupler Pockets/Bosses

Nearest strut bore to nearest coupler pocket/boss:
- S-BL (10.0, 5.0) to H1/B1 (43.1, 34.3): center-to-center = sqrt(33.1^2 + 29.3^2) = 44.2mm
  Strut bore half-extent = 3.2mm, boss radius = 8.0mm. Edge-to-edge gap = 44.2 - 3.2 - 8.0 = 33.0mm.
- S-TL (10.0, 63.6) to H1/B1 (43.1, 34.3): center-to-center = sqrt(33.1^2 + 29.3^2) = 44.2mm. Same gap.
- S-BR (127.2, 5.0) to H4/B4 (94.1, 34.3): center-to-center = sqrt(33.1^2 + 29.3^2) = 44.2mm. Same gap.
- S-TR (127.2, 63.6) to H4/B4 (94.1, 34.3): center-to-center = sqrt(33.1^2 + 29.3^2) = 44.2mm. Same gap.

All strut bores are over 33mm edge-to-edge from the nearest coupler pocket/boss. No interference.

### Edge Clearance — Strut Bores vs. Plate Boundary

| Bore | X range | Z range | Min X edge | Min Z edge |
|------|---------|---------|------------|------------|
| S-TL | [6.8, 13.2] | [60.4, 66.8] | 6.8mm from left | 1.8mm from top |
| S-TR | [124.0, 130.4] | [60.4, 66.8] | 6.8mm from right | 1.8mm from top |
| S-BL | [6.8, 13.2] | [1.8, 8.2] | 6.8mm from left | 1.8mm from bottom |
| S-BR | [124.0, 130.4] | [1.8, 8.2] | 6.8mm from right | 1.8mm from bottom |

All bores are well within the plate boundary. Minimum remaining wall = 1.8mm (Z direction),
above the 1.2mm structural minimum from requirements.md.

---

## Path Continuity

Each coupler capture bore is a straight through-path from Y=0 to Y=12.08mm:
- Base plate hole: Y=0 to Y=3mm, 9.5mm dia
- Boss inner bore: Y=3 to Y=12.08mm, 9.5mm dia
- Both segments share the same XZ center and diameter — continuous bore, no transition step.

Strut bores are independent through-holes (Y=0 to Y=3mm). No path continuity required with
coupler bores — the struts are a separate structural system.

---

## FDM Check

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Base plate — all walls | Overhang | All faces vertical or on build plate | <=45 deg | Yes |
| Base plate thickness | Wall thickness | 3mm | 1.2mm structural min | Yes |
| Boss wall thickness | Thickness | 3.25mm | 1.2mm structural min | Yes |
| Boss height | Bridge/overhang | Vertical cylinder, no overhang | <=45 deg | Yes |
| Wall between adjacent holes/bosses | Gap | 1mm gap between boss ODs | >=0mm | Yes |
| Hole top span (bridge) in base | Bridge span | 9.5mm | 15mm max | Yes |
| Strut bore span (bridge) in base | Bridge span | 6.4mm | 15mm max | Yes |
| Strut bore min wall to plate edge | Wall thickness | 1.8mm (Z direction) | 1.2mm min | Yes |
| Strut bore min wall to coupler pocket | Gap | 33.0mm edge-to-edge | >=0mm | Yes |
| Holes — orientation | Print as vertical features | Axis parallel to print Z | — | Yes |

No overhangs. No supports required.

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| Base plate 137.2 x 3 x 68.6mm | Width/height: pump tray footprint match. Thickness 3mm: build sequence. |
| 4x through-holes, 9.5mm dia | Unchanged from v3. Coupler capture. |
| 1x4 row layout, 17mm c-c along X | Unchanged from v3. |
| 4x bosses, back face | Unchanged from v3. Coupler body-end capture at full 12.08mm depth. |
| 4x strut bores, 6.4 x 6.4 mm | Build sequence: "Add strut bores to coupler tray — same as pump tray." Positions match release plate strut centers. Clearance per requirements.md sliding fit (0.2mm/side). |
