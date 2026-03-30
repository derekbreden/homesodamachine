# Coupler Tray — Parts Specification

**Season 1, Phase 3, Item 9 (v3)**

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray v3 |
| Piece count | 1 |
| Outer dimensions | 137.2mm (X) × 12.08mm (Y, bounding box incl. bosses) × 68.6mm (Z) |
| Base plate thickness | 3mm |
| Features | Base plate + 4× coupler capture holes + 4× bosses (back face) |
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
Bounding envelope: 137.2 × 12.08 × 68.6 mm → X:[0,137.2] Y:[0,12.08] Z:[0,68.6]
```

Print orientation: front face (XZ plane, Y=0) down on the build plate. Z is up during printing.
Hole axes and boss axes are parallel to Y, which becomes print Z — holes and bosses print as
vertical cylinders for maximum roundness and positional accuracy. Bosses protrude upward from
the back of the base plate and print without overhangs.

---

## What Changed from v2

**v2** placed the 4 couplers in a 2×2 grid (2 columns × 2 rows) centered in the plate.

**v3** moves all 4 couplers into a single horizontal row (1×4) along the X axis, centered
vertically at Z = 34.3mm (plate midpoint). Spacing between adjacent coupler centers remains
17mm c-c (unchanged). The plate footprint (137.2 × 68.6mm), base plate thickness (3mm), boss
geometry, and bore dimensions are all unchanged from v2.

This layout enables a clean split between couplers 2 and 3 (Phase 5). The split line falls at
X = 68.6mm — the exact plate midpoint — dividing the tray symmetrically into two halves of
identical width.

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
slide into the same side-wall rails (vision.md Section 3). Thickness 3mm matches the pump tray
thickness (build sequence line: "same thickness as the pump tray, so both slide into the same
side-wall rails"). The v1 plate was 12.08mm thick; the axial retention function is now provided
by bosses instead.

---

## Feature 2 — Coupler Capture Holes (4×)

All holes are through-holes through the base plate. Hole axis is parallel to Y.
Entry at Y=0, exit at Y=3mm. The hole continues as the inner bore of the boss (Y=3 to Y=12.08).

**Layout: 1×4 row along X, centered in the plate.**

- All 4 holes at Z = 34.3mm (plate vertical midpoint)
- 17mm center-to-center spacing along X
- Row centered at X = 68.6mm (plate horizontal midpoint)
- First hole at X = 68.6 − 1.5 × 17 = 43.1mm; subsequent holes at +17mm increments

| Hole ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| H1 | 43.1 | 34.3 | 9.5mm | Through base plate (Y=0 to Y=3mm) |
| H2 | 60.1 | 34.3 | 9.5mm | Through base plate (Y=0 to Y=3mm) |
| H3 | 77.1 | 34.3 | 9.5mm | Through base plate (Y=0 to Y=3mm) |
| H4 | 94.1 | 34.3 | 9.5mm | Through base plate (Y=0 to Y=3mm) |

**Layout:** 1×4 row, centered at (X=68.6, Z=34.3), 17mm c-c along X only.

**Justification:** 9.5mm diameter unchanged from v2. The 1×4 layout is required by build
sequence Phase 3 (vision.md item 9) and enables the Phase 5 split. The holes continue through
the boss inner bore for the full 12.08mm coupler capture depth.

**Phase 5 split note (no geometry added here):** The split between couplers 2 and 3 falls at
X = 68.6mm, exactly the plate midpoint. Half 1 contains H1 (X=43.1) and H2 (X=60.1); Half 2
contains H3 (X=77.1) and H4 (X=94.1). Each half is 68.6mm wide — symmetric. No split geometry
is added in this version.

---

## Feature 3 — Bosses (4×, back face)

Bosses are hollow cylindrical protrusions on the back face (Y=3mm), protruding in the +Y
direction. The front face remains flat (no bosses), keeping it flat on the build plate.

| Boss ID | X (mm) | Z (mm) | Inner Dia | Outer Dia | Height (Y) | Y range |
|---------|--------|--------|-----------|-----------|------------|---------|
| B1 | 43.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B2 | 60.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B3 | 77.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B4 | 94.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |

**Boss inner diameter = 9.5mm:** Continuous with the through-hole in the base plate. The central
body of the JG union (9.31mm OD) press-fits through the full 12.08mm bore (Y=0 to Y=12.08).

**Boss outer diameter = 16mm:** The body-end shoulder (JG union zone 2) is an annular face from
9.31mm OD to 15.10mm OD. The boss face annulus (from 9.5mm inner to 16mm outer = 3.25mm wide
per side) exceeds the shoulder annulus (2.895mm wide), providing full bearing contact. OD 16mm
chosen over larger values because adjacent bosses are 17mm c-c: 16mm OD leaves a 1mm gap between
adjacent boss walls (17mm - 16mm = 1mm), avoiding boss-to-boss intersection. Wall thickness
= (16 - 9.5) / 2 = 3.25mm, well above the 1.2mm structural minimum.

**Boss height = 9.08mm:** Base plate is 3mm thick; bosses extend the capture depth to 12.08mm
total. 12.08mm = JG union Zone 1 body-end length (geometry-description.md Zone 1). With the
full 12.08mm bore, the body-end shoulders on both sides bear against surfaces: front shoulder
bears against the front face of the base plate (Y=0), back shoulder bears against the boss
tip face (Y=12.08mm), providing axial retention of the captured coupler.

**Adjacency check (1×4 row, all at same Z):**
- Adjacent bosses (17mm X spacing): Boss radius = 8mm. Edge-to-edge = 17 - 16 = 1mm. No intersection.
- Non-adjacent bosses (34mm X spacing): Edge-to-edge = 34 - 16 = 18mm. No intersection.
- No Z-direction adjacency (all bosses at same Z).

**Edge clearance (boss OD to plate edge):**
- H1 (X=43.1): boss edge in -X = 43.1 - 8 = 35.1mm from left edge. Fine.
- H4 (X=94.1): boss edge in +X = 94.1 + 8 = 102.1mm from left (137.2 - 102.1 = 35.1mm to right). Fine.
- All holes (Z=34.3): boss edge in -Z = 34.3 - 8 = 26.3mm from bottom. Fine.
- All holes (Z=34.3): boss edge in +Z = 34.3 + 8 = 42.3mm from top (68.6 - 42.3 = 26.3mm to top). Fine.

---

## Path Continuity

Each coupler capture bore is a straight through-path from Y=0 to Y=12.08mm:
- Base plate hole: Y=0 to Y=3mm, 9.5mm dia
- Boss inner bore: Y=3 to Y=12.08mm, 9.5mm dia
- Both segments share the same XZ center and diameter — continuous bore, no transition step.

---

## FDM Check

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Base plate — all walls | Overhang | All faces vertical or on build plate | ≤45° | Yes |
| Base plate thickness | Wall thickness | 3mm | 1.2mm structural min | Yes |
| Boss wall thickness | Thickness | 3.25mm | 1.2mm structural min | Yes |
| Boss height | Bridge/overhang | Vertical cylinder, no overhang | ≤45° | Yes |
| Wall between adjacent holes/bosses | Gap | 1mm gap between boss ODs | ≥0mm (no intersection) | Yes |
| Hole top span (bridge) in base | Bridge span | 9.5mm | 15mm max | Yes |
| Holes — orientation | Print as vertical cylinders | Axis parallel to print Z | — | Yes |

No overhangs. No supports required.

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| Base plate 137.2 × 3 × 68.6mm | Width/height: pump tray footprint match (vision.md Section 3). Thickness 3mm: build sequence line "thin the plate to 3mm (same thickness as the pump tray)". |
| 4× through-holes, 9.5mm dia | Unchanged from v2. Build sequence line: same holes. |
| 1×4 row layout, 17mm c-c along X | Build sequence Phase 3, item 9: "Redesign coupler tray layout to 1×4 — all four couplers in a single row." (vision.md) |
| 4× bosses, back face | Build sequence line: "Add bosses on one face only (protruding from the back face, keeping the front face flat on the build plate) to capture the coupler body-ends at the full 12.08mm depth." |
| Boss height 9.08mm | Physical necessity — 3mm base + 9.08mm boss = 12.08mm total = Zone 1 body-end length (geometry-description.md). |
| Boss inner dia 9.5mm | Physical necessity — continuous with through-hole; central body press-fit requires 9.5mm bore. |
| Boss outer dia 16mm | Physical necessity — must exceed body-end OD (15.10mm) for shoulder bearing; must not intersect adjacent bosses (17mm c-c → max 17mm OD). 16mm chosen. |

---

## Excluded Features (Phase 3 / v3 scope)

| Feature | Excluded because |
|---------|-----------------|
| Strut bores | Build sequence line explicitly: "No strut bores — those come in Phase 4." |
| Split geometry | Phase 5 (vision.md items 15–16). |
| Rail tabs/slots | Season 2 (vision.md Phase 6). |
| Chamfers, fillets | No cosmetic requirements in Phase 3. |
| Boss chamfers/fillets | Not in build sequence line. |
