# Coupler Tray Split — Parts Specification

**Season 1, Phase 5 — Split coupler tray into two halves**

---

## Overview

The coupler tray is split into two halves — a **base half** (flat front side) and a **boss half**
(back side, contains the bosses). Both halves stack face-to-face along the Y axis (the coupler
axis). Every coupler passes through both halves. Each half has a 9.5mm through-bore; together
the two halves provide 12.08mm of total bore depth that captures the narrow center section
(9.31mm OD, 12.16mm long) of each John Guest union coupler. The wider body-end shoulders
(15.10mm OD) bear against the flat outer faces of each half, providing axial retention.

This is NOT a left/right split along the tray length. It is a front/back split perpendicular to
Y (the coupler axis).

The two STEP files are:
- `coupler-tray-top-cadquery.step`   — boss half (contains bosses, coupler Y+ side)
- `coupler-tray-bottom-cadquery.step` — base half (flat, coupler Y− side)

The old single-piece `coupler-tray-cadquery.step` is superseded and deleted.

---

## John Guest Union Coupler Geometry (relevant dimensions)

Source: `hardware/off-the-shelf-parts/john-guest-union/extracted-results/geometry-description.md`

| Zone | OD | Length |
|------|----|--------|
| Body-end section (×2, each end) | 15.10mm | 12.08mm |
| Center body (narrow waist) | 9.31mm | 12.16mm |
| Total body length | — | 36.32mm |

The center body (9.31mm OD) is what the tray bore grips. Bore at 9.5mm = light press-fit on
9.31mm center body. The body-end shoulders (15.10mm OD) are wider than the bore and provide
axial retention by bearing against the outer faces of the assembled tray.

---

## Assembly Logic

When the two halves are pressed together face-to-face:

1. Base half contributes 6.04mm of bore depth (through the full base half Y thickness).
2. Boss half contributes 6.04mm of bore depth (through the boss half base plate).
   The boss protrusion (9.08mm beyond the base plate) provides additional bore depth through
   the boss inner bore — together with the base plate this gives the boss half a total bore
   depth of 12.08mm — but only the 6.04mm at the mating face contributes to capturing
   the center body alongside the base half.
3. Total bore depth at center body = 6.04 + 6.04 = 12.08mm ≈ center body length (12.16mm). ✓
4. Coupler body-end shoulder (15.10mm OD) bears on base half outer face (flat, Y=0). ✓
5. Coupler body-end shoulder (15.10mm OD) bears on boss half boss-tip face (Y=12.08mm from
   boss half mating face). ✓

To install: separate the halves, lay coupler center body into boss half bore (or base half bore),
press other half onto it. The halves capture the center body. In Season 3, dovetail and snap
features will be added to lock the halves permanently.

---

## Coordinate System — SHARED (both halves use the same origin)

Both halves are designed in the same coordinate system so they can be overlaid to verify
the mating interface.

```
Origin: bottom-left-front corner of the assembled tray (= bottom-left corner of base half
        outer face = bottom-left corner of base half at Y=0)

X:  width axis — left to right, 0..137.2mm
Y:  thickness axis — from base half outer face (Y=0) through base half mating face (Y=6.04mm)
    through boss half mating face (Y=6.04mm) to boss half boss-tip face (Y=18.12mm)
    Base half spans:  Y=0   to Y=6.04mm
    Boss half spans:  Y=6.04mm to Y=18.12mm
    (Each part's own local Y=0 is at the bottom of its own Y range, i.e. the base half origin
    is at absolute Y=0, the boss half origin is at absolute Y=6.04mm — but both scripts place
    their own origin at local Y=0 for simplicity.)
Z:  height axis — bottom to top, 0..68.6mm
```

The mating face for both halves is a flat YZ plane at their respective local Y = 6.04mm
(base half) and local Y = 0.0mm (boss half). Flat with no features.

---

## Part 1 — Base Half

### Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray — Base Half |
| STEP file | `coupler-tray-bottom-cadquery.step` |
| Piece count | 1 (of the matched pair) |
| Outer dimensions | 137.2mm (X) × 6.04mm (Y) × 68.6mm (Z) |
| Features | Base plate + 4x coupler through-bores + 4x strut bores |
| Print orientation | Outer front face (XZ plane, local Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

### Coordinate System (local — base half)

```
Origin: bottom-left corner of outer front face.
X: width axis — left to right, 0..137.2mm
Y: thickness axis — outer face (Y=0) to mating face (Y=6.04mm)
Z: height axis — bottom to top, 0..68.6mm
Bounding envelope: 137.2 × 6.04 × 68.6 mm
```

Print orientation: outer face (XZ plane, local Y=0) down on build plate. Z is up during
printing. Bores print as vertical cylinders — no overhangs.

### Feature 1 — Base Plate Body

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 137.2mm |
| Thickness (Y) | 6.04mm |
| Height (Z) | 68.6mm |
| All corners | Square (no chamfer, no fillet) |

**Justification:** Width 137.2mm and height 68.6mm match the pump tray and original coupler
tray footprint (both slide into same side-wall rails). Thickness 6.04mm = half of total
12.08mm bore depth.

### Feature 2 — Coupler Through-Bores (4×, base half)

Through-holes from outer face (Y=0) to mating face (Y=6.04mm). Bore axis parallel to Y.
Bore diameter 9.5mm = light press-fit on 9.31mm coupler center body.

Layout: 1×4 row along X, identical to original coupler tray.

| Bore ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| BH1 | 43.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.04mm) |
| BH2 | 60.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.04mm) |
| BH3 | 77.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.04mm) |
| BH4 | 94.1 | 34.3 | 9.5mm | Through (Y=0 to Y=6.04mm) |

### Feature 3 — Strut Bores (4×, base half)

Rectangular through-holes in the base half for the release plate struts to pass through.
Bore axis parallel to Y. Same positions as original coupler tray strut bores.

| Bore ID | X (mm) | Z (mm) | Size (X × Z) | Depth |
|---------|--------|--------|---------------|-------|
| S-TL | 10.0 | 63.6 | 6.4 × 6.4mm | Through (Y=0 to Y=6.04mm) |
| S-TR | 127.2 | 63.6 | 6.4 × 6.4mm | Through (Y=0 to Y=6.04mm) |
| S-BL | 10.0 | 5.0 | 6.4 × 6.4mm | Through (Y=0 to Y=6.04mm) |
| S-BR | 127.2 | 5.0 | 6.4 × 6.4mm | Through (Y=0 to Y=6.04mm) |

### FDM Check — Base Half

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Base plate walls | Overhang | All faces vertical or on build plate | ≤45° | Yes |
| Base plate thickness | Wall thickness | 6.04mm | 1.2mm structural min | Yes |
| Coupler bore span | Bridge | 9.5mm | 15mm max | Yes |
| Strut bore span | Bridge | 6.4mm | 15mm max | Yes |
| Wall between adjacent coupler bores | Gap | 1mm (17mm c-c, 9.5mm dia → 7.5mm gap) | ≥0mm | Yes |
| Strut bore min wall to plate edge | Wall | 6.8mm (X), 1.8mm (Z) | 1.2mm min | Yes |

No overhangs. No supports required.

---

## Part 2 — Boss Half

### Summary

| Property | Value |
|----------|-------|
| Part name | Coupler Tray — Boss Half |
| STEP file | `coupler-tray-top-cadquery.step` |
| Piece count | 1 (of the matched pair) |
| Outer dimensions | 137.2mm (X) × 12.08mm (Y, bounding box incl. bosses) × 68.6mm (Z) |
| Base plate thickness | 3.0mm |
| Boss protrusion | 9.08mm (from back face of base plate) |
| Features | Base plate + 4× bosses (outer/back face) + 4× coupler through-bores + 4× strut bores |
| Print orientation | Mating face (XZ plane, local Y=0) down on build plate |
| Material | PLA or PETG |
| Supports required | None |
| User-facing | No |

### Coordinate System (local — boss half)

The boss half's local Y=0 is at its mating face (which faces the base half). The bosses
protrude in the +Y direction from the back of the base plate. This keeps the mating face flat
on the build plate for printing.

```
Origin: bottom-left corner of mating face (the flat face that presses against base half).
X: width axis — left to right, 0..137.2mm
Y: thickness axis — mating face (Y=0) to back of base plate (Y=3.0mm);
   bosses protrude from Y=3.0mm to Y=12.08mm
Z: height axis — bottom to top, 0..68.6mm
Bounding envelope: 137.2 × 12.08 × 68.6 mm
```

Print orientation: mating face (XZ plane, Y=0) down on build plate. Z is up during printing.
Bosses and bores print as vertical cylinders — no overhangs.

### Justification for retaining boss geometry

The boss half retains the original boss geometry from the pre-split coupler tray (v4). The
bosses provide:
1. An outer cylindrical bearing ring (OD 16mm) for the coupler body-end shoulder (15.10mm OD)
   to bear against at the boss-tip face.
2. Continuous bore depth: the boss half's bore runs from mating face (Y=0) through the base
   plate and through the full boss length to the boss-tip face (Y=12.08mm). This 12.08mm bore
   depth in the boss half exceeds the boss half's contribution to center-body capture (6.04mm
   needed, 12.08mm available), but does not cause interference — the coupler body-end (15.10mm)
   cannot enter the 9.5mm bore and bears on the boss-tip flat annular face at Y=12.08mm. ✓

### Feature 1 — Base Plate Body (boss half)

| Property | Value |
|----------|-------|
| Geometry | Rectangular solid |
| Width (X) | 137.2mm |
| Thickness (Y) | 3.0mm (Y=0 to Y=3.0mm) |
| Height (Z) | 68.6mm |
| All corners | Square |

Matches original coupler tray base plate thickness (3mm) and footprint (137.2 × 68.6mm).

### Feature 2 — Bosses (4×, boss half outer face)

Hollow cylindrical protrusions from the base plate back face (Y=3.0mm) in the +Y direction.
Boss OD = 16mm, boss inner bore = 9.5mm (continuous with base plate bore).

| Boss ID | X (mm) | Z (mm) | Inner Dia | Outer Dia | Height (Y) | Y range |
|---------|--------|--------|-----------|-----------|------------|---------|
| TB1 | 43.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3.0 to Y=12.08 |
| TB2 | 60.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3.0 to Y=12.08 |
| TB3 | 77.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3.0 to Y=12.08 |
| TB4 | 94.1 | 34.3 | 9.5mm | 16mm | 9.08mm | Y=3.0 to Y=12.08 |

### Feature 3 — Coupler Through-Bores (4×, boss half)

Through-holes from mating face (Y=0) to boss-tip face (Y=12.08mm). Bore axis parallel to Y.
Diameter 9.5mm throughout (continuous from base plate bore through boss inner bore).

| Bore ID | X (mm) | Z (mm) | Diameter | Depth |
|---------|--------|--------|----------|-------|
| TH1 | 43.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |
| TH2 | 60.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |
| TH3 | 77.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |
| TH4 | 94.1 | 34.3 | 9.5mm | Through (Y=0 to Y=12.08mm) |

### Feature 4 — Strut Bores (4×, boss half)

Rectangular through-holes in the boss half base plate for the release plate struts to pass
through. Bore axis parallel to Y. Same XZ positions as original coupler tray strut bores.
Struts pass through the full boss half (Y=0 to Y=12.08mm) in the region where only the
3mm base plate exists (strut bores are at corners, far from boss positions — no boss material
in the strut bore region, so bores run through Y=0 to Y=3mm only, with open air beyond).

| Bore ID | X (mm) | Z (mm) | Size (X × Z) | Depth |
|---------|--------|--------|---------------|-------|
| TS-TL | 10.0 | 63.6 | 6.4 × 6.4mm | Through (Y=0 to Y=3.0mm, base plate only) |
| TS-TR | 127.2 | 63.6 | 6.4 × 6.4mm | Through (Y=0 to Y=3.0mm, base plate only) |
| TS-BL | 10.0 | 5.0 | 6.4 × 6.4mm | Through (Y=0 to Y=3.0mm, base plate only) |
| TS-BR | 127.2 | 5.0 | 6.4 × 6.4mm | Through (Y=0 to Y=3.0mm, base plate only) |

Note: in the boss half, the strut bores only go through the 3mm base plate (Y=0 to Y=3.0mm).
The region beyond the base plate (Y=3.0mm onward) is open at strut bore positions — the
bosses are only at coupler positions (XZ center 43.1–94.1mm, Z=34.3mm), far from the
strut bore positions at the plate corners.

### FDM Check — Boss Half

| Feature | Check | Value | Limit | Pass? |
|---------|-------|-------|-------|-------|
| Base plate walls | Overhang | All faces vertical or on build plate | ≤45° | Yes |
| Base plate thickness | Wall thickness | 3.0mm | 1.2mm structural min | Yes |
| Boss wall thickness | Thickness | (16−9.5)/2 = 3.25mm | 1.2mm structural min | Yes |
| Boss height | Overhang | Vertical cylinder, no overhang | ≤45° | Yes |
| Coupler bore span | Bridge | 9.5mm | 15mm max | Yes |
| Strut bore span | Bridge | 6.4mm | 15mm max | Yes |
| Wall between adjacent coupler bores/bosses | Gap | 1mm (boss OD 16mm, 17mm c-c → 1mm gap) | ≥0mm | Yes |
| Strut bore min wall to plate edge | Wall | 6.8mm (X), 1.8mm (Z) | 1.2mm min | Yes |

No overhangs. No supports required.

---

## Matched Pair Interface

When assembled face-to-face:

| Interface | Value |
|-----------|-------|
| Mating face flatness | Both faces flat, no dovetail or feature geometry (Season 3 addition) |
| Coupler bore alignment | Both halves share identical XZ bore centers — bores align to form continuous 9.5mm bore |
| Strut bore alignment | Both halves share identical XZ strut bore centers — rectangular bores align |
| Total bore depth at coupler positions | 6.04mm (base half) + 12.08mm (boss half) = 18.12mm total bore available; center body (12.16mm) captured across mating plane ≈6.08mm per half |
| Total tray assembled Y | 6.04mm (base half) + 12.08mm (boss half from mating face to boss tip) = 18.12mm |

---

## Feature Traceability

| Feature | Traces to |
|---------|-----------|
| XZ footprint 137.2 × 68.6mm | Both halves inherit original coupler tray footprint (pump tray match for rail sliding) |
| 9.5mm coupler bores — 1×4 row, 17mm c-c | Unchanged from original coupler tray v3/v4 |
| Boss geometry (boss half) | Unchanged from original coupler tray v4 |
| Strut bore positions TL/TR/BL/BR | Unchanged from original coupler tray v4 |
| Base half thickness 6.04mm | 12.08mm total bore depth ÷ 2 halves |
| Boss half retains 3mm plate + 9.08mm boss | Preserves original boss geometry on boss side |
| Plain flat mating faces, no dovetail | Build sequence Phase 5 scope; Season 3 adds dovetail |
