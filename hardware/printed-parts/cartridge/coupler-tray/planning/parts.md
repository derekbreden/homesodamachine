# Coupler Tray — Parts Specification

**Season 1, Phase 1, Item 3**

---

## Part Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray |
| Piece count | 1 |
| Outer dimensions | 137.2mm (X) × 12.08mm (Y) × 68.6mm (Z) |
| Features | Plate body + 4× coupler capture holes |
| Print orientation | Front face (XZ plane, Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

---

## Coordinate System

Origin: bottom-left corner of the front face of the plate.

```
X: width axis — left to right, 0..137.2mm
Y: thickness axis — front to back through the plate, 0..12.08mm
    Y=0: front face
    Y=12.08mm: back face
Z: height axis — bottom to top, 0..68.6mm
Envelope: 137.2 × 12.08 × 68.6 mm → X:[0,137.2] Y:[0,12.08] Z:[0,68.6]
```

Print orientation: front face (XZ plane, Y=0) down on the build plate. Z is up during printing. The 4 hole axes are parallel to Y, which becomes the print Z direction — holes print as vertical cylinders for maximum roundness and positional accuracy.

---

## Feature 1 — Plate Body

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 137.2mm |
| Thickness (Y) | 12.08mm |
| Height (Z) | 68.6mm |
| All corners | Square (no chamfer, no fillet in Phase 1) |

**Justification:** Width 137.2mm and height 68.6mm match the pump tray footprint so both parts slide into the same side-wall rails (vision.md Section 3). Thickness 12.08mm matches the John Guest union body-end length (geometry-description.md Zone 1), so the body-end shoulders (15.10mm OD, wider than the 9.5mm holes) bear against both plate faces and provide axial retention of the captured coupler.

---

## Feature 2 — Coupler Capture Holes (4×)

All holes are through-holes. Hole axis is parallel to Y. Entry at Y=0, exit at Y=12.08mm.

| Hole ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| H1 | 60.1 | 25.8 | 9.5mm | Through (Y=0 to Y=12.08mm) |
| H2 | 77.1 | 25.8 | 9.5mm | Through (Y=0 to Y=12.08mm) |
| H3 | 60.1 | 42.8 | 9.5mm | Through (Y=0 to Y=12.08mm) |
| H4 | 77.1 | 42.8 | 9.5mm | Through (Y=0 to Y=12.08mm) |

**Layout:** 2×2 grid, centered in the plate footprint at (X=68.6, Z=34.3). Center-to-center spacing: 17mm in both X and Z.

**Justification:**
- 9.5mm diameter: build sequence line specifies "four 9.5mm holes." Per geometry-description.md Zone 3, a 9.5mm bore gives a light press-fit on the 9.31mm central body OD.
- Plate thickness 12.08mm captures the central body (12.16mm long), with body-end shoulders (15.10mm OD) bearing against both plate faces for axial retention.
- 17mm center-to-center: provides 7.5mm wall between hole walls within the plate (well above the 0.8mm structural minimum), and 1.9mm clearance between adjacent body-end OD faces outside the plate.
- 2×2 arrangement: natural first version; Phase 3 will redesign to 1×4 for the split (vision.md Phase 3, item 7).

**Derivation check:**
- Grid center: (137.2/2, 68.6/2) = (68.6, 34.3)
- X centers: 68.6 ± 8.5 → {60.1, 77.1}
- Z centers: 34.3 ± 8.5 → {25.8, 42.8}
- Edge clearance (hole center to plate edge): X: min(60.1, 137.2−77.1) = 60.1mm; Z: min(25.8, 68.6−42.8) = 25.8mm. Both far above minimum.

---

## Path Continuity

Each hole is a straight through-bore, Y=0 to Y=12.08mm, with no other features intersecting it. No multi-segment path exists; no continuity check required.

---

## FDM Check

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Plate body — all walls | Overhang | All faces vertical or on build plate | ≤45° | Yes |
| Plate thickness | Wall thickness | 12.08mm | 1.2mm structural min | Yes |
| Wall between adjacent holes | Thickness | 17 − 9.5 = 7.5mm | 0.8mm min | Yes |
| Hole top span (bridge) | Bridge span | 9.5mm | 15mm max | Yes |
| Holes — orientation | Print as vertical cylinders | Axis parallel to print Z | — | Yes |

No overhangs. No supports required.

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| Plate body (137.2 × 12.08 × 68.6mm) | Width and height: pump tray footprint match for same side-wall rails (vision.md Section 3). Thickness: Zone 1 body-end length 12.08mm (geometry-description.md). |
| Plate thickness = 12.08mm | Physical necessity — Zone 1 body-end length is 12.08mm; plate must be this thick for body-end shoulders to bear against both faces. |
| Plate width = 137.2mm | Physical necessity — must match pump tray width for same side-wall rails (vision.md Section 3, "slide into protruding tracks on the cartridge walls"). |
| Plate height = 68.6mm | Physical necessity — must match pump tray height for same side-wall rails. |
| 4× through-holes, 9.5mm dia | Build sequence line: "four 9.5mm holes." Physical necessity — captures 9.31mm central body of John Guest union (geometry-description.md Zone 3). |

---

## Excluded Features (Phase 1)

| Feature | Excluded because |
|---------|-----------------|
| Strut bores | Build sequence line explicitly: "No strut bores — those come in Phase 4." |
| Split geometry (dovetail, snap detent) | Phase 5 work (vision.md items 13–14, Phase 9–10). |
| Rail tabs or slots on plate edges | Season 2 work (vision.md Phase 6). |
| Retention detents | Season 3 work (vision.md Phase 15–16). |
| Stepped/counterbored holes | Not in build sequence line. Simple 9.5mm through-holes are the deliverable. |
| Chamfers, fillets, surface texture | No mating surfaces, no cosmetic requirements in Phase 1. |
