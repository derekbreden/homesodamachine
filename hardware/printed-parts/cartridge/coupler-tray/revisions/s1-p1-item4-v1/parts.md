# Coupler Tray — Parts Specification

**Season 1, Phase 1, Item 4 (v2)**

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray v2 |
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

| Hole ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| H1 | 60.1 | 25.8 | 9.5mm | Through base plate (Y=0 to Y=3mm) |
| H2 | 77.1 | 25.8 | 9.5mm | Through base plate (Y=0 to Y=3mm) |
| H3 | 60.1 | 42.8 | 9.5mm | Through base plate (Y=0 to Y=3mm) |
| H4 | 77.1 | 42.8 | 9.5mm | Through base plate (Y=0 to Y=3mm) |

**Layout:** 2×2 grid, centered in the plate footprint at (X=68.6, Z=34.3), 17mm c-c spacing.
(Unchanged from v1 — Phase 3 will redesign to 1×4.)

**Justification:** 9.5mm diameter, 2×2 grid, and all XZ positions unchanged from v1.
The holes continue through the boss inner bore for the full 12.08mm coupler capture depth.

---

## Feature 3 — Bosses (4×, back face)

Bosses are hollow cylindrical protrusions on the back face (Y=3mm), protruding in the +Y
direction. The front face remains flat (no bosses), keeping it flat on the build plate.

| Boss ID | X (mm) | Z (mm) | Inner Dia | Outer Dia | Height (Y) | Y range |
|---------|--------|--------|-----------|-----------|------------|---------|
| B1 | 60.1 | 25.8 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B2 | 77.1 | 25.8 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B3 | 60.1 | 42.8 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |
| B4 | 77.1 | 42.8 | 9.5mm | 16mm | 9.08mm | Y=3 to Y=12.08 |

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
tip face (Y=12.08mm), providing axial retention of the captured coupler — same mechanical
function as the v1 plate but with a thinner base plus bosses.

**Adjacency check:**
- H1↔H2 and H3↔H4: 17mm X spacing. Boss radius = 8mm. Edge-to-edge = 17 - 16 = 1mm. No intersection.
- H1↔H3 and H2↔H4: 17mm Z spacing. Same check. 1mm gap. No intersection.
- H1↔H4 (diagonal): sqrt(17²+17²) = 24.04mm c-c. Edge-to-edge = 24.04 - 16 = 8.04mm. No intersection.

**Edge clearance (boss OD to plate edge):**
- H1 (X=60.1): boss edge in -X = 60.1 - 8 = 52.1mm from left edge. Fine.
- H4 (X=77.1): boss edge in +X = 77.1 + 8 = 85.1mm from left (137.2 - 85.1 = 52.1mm to right). Fine.
- H1/H2 (Z=25.8): boss edge in -Z = 25.8 - 8 = 17.8mm from bottom. Fine.
- H3/H4 (Z=42.8): boss edge in +Z = 42.8 + 8 = 50.8mm from bottom (68.6 - 50.8 = 17.8mm to top). Fine.

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
| 4× through-holes, 9.5mm dia | Unchanged from v1. Build sequence line: same holes. |
| 4× bosses, back face | Build sequence line: "Add bosses on one face only (protruding from the back face, keeping the front face flat on the build plate) to capture the coupler body-ends at the full 12.08mm depth." |
| Boss height 9.08mm | Physical necessity — 3mm base + 9.08mm boss = 12.08mm total = Zone 1 body-end length (geometry-description.md). |
| Boss inner dia 9.5mm | Physical necessity — continuous with through-hole; central body press-fit requires 9.5mm bore. |
| Boss outer dia 16mm | Physical necessity — must exceed body-end OD (15.10mm) for shoulder bearing; must not intersect adjacent bosses (17mm c-c → max 17mm OD). 16mm chosen. |

---

## Excluded Features (Phase 1 / v2 scope)

| Feature | Excluded because |
|---------|-----------------|
| Strut bores | Build sequence line explicitly: "No strut bores — those come in Phase 4." |
| Split geometry | Phase 5 (vision.md items 13–14). |
| Rail tabs/slots | Season 2 (vision.md Phase 6). |
| Chamfers, fillets | No cosmetic requirements in Phase 1. |
| Boss chamfers/fillets | Not in build sequence line. |
