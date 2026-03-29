# Spatial Resolution: Sub-D Fitting Bore Array

## Critical Correction: Rear Wall vs. Bore Plate

The tray decomposition document states that the fitting bores are in the "rear wall" (Y=0 to Y=8.5) and that the bore depth of 12.16mm "fits within" the 8.5mm wall. **This is physically impossible.** The John Guest PP0408W center body is 12.16mm long; an 8.5mm wall cannot contain it.

The decision document's spatial ordering (dock to user) clarifies the actual layout:

1. Dock wall (enclosure)
2. Cartridge rear wall (Y=0 to Y=8.5) -- tubes pass through clearance holes
3. Release plate -- slides on guide posts between rear wall and fittings
4. John Guest fittings -- mounted in a bore plate further inside the cartridge

The fittings are NOT in the 8.5mm rear wall. They are in an internal **bore plate** -- a structural feature integral to the tray, extending inward from the rear wall as cylindrical bosses or a reinforced buttress. The bore plate captures the center body in a press-fit bore, with body-end shoulders bearing against both faces.

This document resolves the exact positions of the bore plate, all 4 fittings, and the release plate in the tray reference frame.

---

## 1. System-Level Placement

```
Mechanism: Fitting Bore Array (Sub-D)
Parent: Tray (Sub-A box shell)
Position: centered on the rear wall, extending inward as bosses from the rear wall interior face
Orientation: bore axes parallel to Y (depth axis), fitting long axes along Y
```

The bore array sits in the rear zone of the cartridge interior, behind the release plate, with fittings oriented along the Y axis (dock-to-user). The bore plate is not a free-standing wall -- it is the rear wall thickened locally at the 4 bore positions via cylindrical bosses extending into the cartridge interior.

---

## 2. Part Reference Frame

```
Part: Fitting Bore Array (Sub-D)
  Frame: Tray frame (same as Sub-A)
  Origin: rear-left-bottom corner of tray
  X: width, 0..160 mm (left to right when facing front)
  Y: depth, 0..155 mm (0 = dock face, 155 = user side)
  Z: height, 0..72 mm (0 = floor bottom, 72 = top of walls)
  Print orientation: open top facing up, XY plane on build plate
  Installed orientation: identical to print orientation
```

All coordinates below are in this tray frame. No rotation or translation is needed -- Sub-D cuts and bosses are applied directly to the Sub-A solid.

---

## 3. Derived Geometry

### 3a. Y-Axis Stack-Up (Dock to User)

The Y positions are derived from the fitting's caliper-verified barbell profile (from `geometry-description.md`) and the requirement that the release plate sits between the rear wall interior and the fitting dock-side collets, in contact with the extended collets at rest.

**Fitting dimensions (caliper-verified):**
- Body end section length: 12.08 mm (each end, 15.10 mm OD)
- Center body length: 12.16 mm (9.31 mm OD)
- Collet protrusion (extended): ~1.4 mm beyond body end face
- Collet protrusion (compressed): ~0.1 mm beyond body end face (1.3 mm travel)
- Total body length: 36.32 mm
- Total length with collets extended: 41.80 mm

**Release plate dimensions (from collet release research):**
- Plate thickness: 5 mm
- Travel: 1.5 mm toward user (higher Y)
- Hard stop: 2.0 mm

**Constraint chain (working backward from release plate contact):**

The release plate dock-facing face must clear the rear wall interior (Y = 8.5) with a small working gap. Setting a 1.0 mm gap:

| Element | Y-start | Y-end | Derivation |
|---------|---------|-------|------------|
| Rear wall | 0 | 8.5 | Sub-A: 8.5 mm rear wall |
| Gap (rear wall to plate) | 8.5 | 9.5 | 1.0 mm clearance for plate travel range |
| Release plate (at rest) | 9.5 | 14.5 | 5.0 mm plate thickness |
| Collet (extended) | 14.5 | 15.9 | 1.4 mm protrusion; plate face contacts collet face at rest |
| Dock-side body end face | 15.9 | 15.9 | End face of the 15.10 mm OD body end section |
| Dock-side body end section | 15.9 | 28.0 | 12.08 mm length (15.9 + 12.08 = 27.98, rounded to 28.0) |
| Dock-side shoulder | 28.0 | 28.0 | Transition from 15.10 mm to 9.31 mm; bears against bore plate dock face |
| Center body (in bore) | 28.0 | 40.2 | 12.16 mm length (28.0 + 12.16 = 40.16, rounded to 40.2) |
| User-side shoulder | 40.2 | 40.2 | Transition from 9.31 mm to 15.10 mm; bears against bore plate user face |
| User-side body end section | 40.2 | 52.3 | 12.08 mm length (40.2 + 12.08 = 52.28, rounded to 52.3) |
| User-side body end face | 52.3 | 52.3 | Tube entry face |
| User-side collet (extended) | 52.3 | 53.7 | 1.4 mm protrusion |

**Bore plate position:**
- Dock face: Y = 28.0
- User face: Y = 40.2
- Thickness: 12.2 mm (matches center body length; center body fills bore completely)

**Fitting centerline along Y:** center of center body at Y = 34.1

### 3b. Release Plate Travel Envelope

| State | Plate dock face | Plate user face | Collet tip position |
|-------|-----------------|-----------------|---------------------|
| At rest | Y = 9.5 | Y = 14.5 | Y = 14.5 (plate touching collet) |
| Full release (1.5 mm travel) | Y = 11.0 | Y = 16.0 | Y = 16.0 (collet compressed 1.3 mm + 0.2 mm margin) |
| Hard stop (2.0 mm travel) | Y = 11.5 | Y = 16.5 | Y = 16.5 (over-travel limit) |

Gap between rear wall interior (Y = 8.5) and plate dock face ranges from 1.0 mm (at rest) to 3.0 mm (at hard stop). Guide posts must span this full range.

### 3c. Guide Post Envelope

Guide posts rise from the rear wall interior face (Y = 8.5) toward the user. They must extend through the release plate and beyond the plate's full-travel position to maintain bearing engagement.

- Post base: Y = 8.5 (bonded to rear wall interior)
- Post tip: Y = 22.0 (13.5 mm long; extends 5.5 mm beyond plate user face at hard stop)
- Post diameter: 3.5 mm
- Plate bore diameter: 3.7-3.8 mm (0.2-0.3 mm clearance)

Posts at diagonal corners of the fitting grid (see section 3e for X, Z positions).

### 3d. Bore Center Positions (X, Z)

The 2x2 fitting grid is centered on the rear wall. Wall center: X = 80.0, Z = 36.0.

Center-to-center spacing: 20.0 mm in both X and Z.

| Bore | X (mm) | Z (mm) | Label |
|------|--------|--------|-------|
| 1 (lower-left) | 70.0 | 26.0 | Pump 1 inlet |
| 2 (lower-right) | 90.0 | 26.0 | Pump 1 outlet |
| 3 (upper-left) | 70.0 | 46.0 | Pump 2 inlet |
| 4 (upper-right) | 90.0 | 46.0 | Pump 2 outlet |

**Clearance check (body end OD = 15.10 mm, radius = 7.55 mm):**
- Bore 1 to left interior wall (X = 5): 70.0 - 7.55 = 62.45 mm clearance. OK.
- Bore 1 to floor interior (Z = 3): 26.0 - 7.55 = 18.45 mm clearance. OK.
- Bore 4 to right interior wall (X = 155): 155 - 90.0 - 7.55 = 57.45 mm clearance. OK.
- Bore 4 to top edge (Z = 72): 72 - 46.0 - 7.55 = 18.45 mm clearance. OK.
- Adjacent bores (20 mm c-c, 15.5 mm counterbore): 20.0 - 15.5 = 4.5 mm wall between counterbores. OK for FDM.

### 3e. Guide Post Positions (X, Z)

Posts at diagonal corners of the fitting grid, offset outward from the bore envelope to avoid interference with the 15.5 mm counterbores.

Minimum offset from bore center to post center: 15.5/2 + 3.5/2 + 2.0 (wall) = 7.75 + 1.75 + 2.0 = 11.5 mm.

Posts placed at diagonal corners of a rectangle surrounding the bore grid:

| Post | X (mm) | Z (mm) | Derivation |
|------|--------|--------|------------|
| P1 (lower-left) | 58.0 | 14.5 | Bore 1 center (70, 26) minus (12, 11.5) |
| P2 (upper-right) | 102.0 | 57.5 | Bore 4 center (90, 46) plus (12, 11.5) |
| P3 (upper-left) | 58.0 | 57.5 | Diagonal pair with P2 |
| P4 (lower-right) | 102.0 | 14.5 | Diagonal pair with P1 |

**Clearance check (post OD = 3.5 mm, radius = 1.75 mm):**
- P1 to floor interior (Z = 3): 14.5 - 1.75 = 12.75 mm. OK.
- P3 to top edge (Z = 72): 72 - 57.5 - 1.75 = 12.75 mm. OK.
- P1 to left wall interior (X = 5): 58.0 - 1.75 = 56.25 mm. OK.
- P4 to right wall interior (X = 155): 155 - 102.0 - 1.75 = 51.25 mm. OK.
- P1 to nearest bore center (bore 1 at 70, 26): sqrt(12^2 + 11.5^2) = 16.6 mm. Post edge at 16.6 - 1.75 = 14.85 mm from bore center. Counterbore radius = 7.75 mm. Clearance = 14.85 - 7.75 = 7.1 mm. OK.

### 3f. Bore Profile (Cross-Section Along Y)

Each bore is a stepped profile cut through the bore plate bosses, with an entry funnel on the dock face of the rear wall (Y = 0). All 4 bores are identical.

**Rear wall pass-through (Y = 0 to Y = 8.5):**

These are NOT the fitting press-fit bores. They are clearance holes for tubes from the dock that pass through the rear wall, through the release plate, and into the fitting dock-side ports. The tubes are 6.35 mm OD (nominal).

| Feature | Diameter (mm) | Y-start | Y-end | Purpose |
|---------|---------------|---------|-------|---------|
| Entry funnel (dock face) | 12.0 at Y=0, tapering to 8.0 at Y=2.0 | 0 | 2.0 | Guides dock tube stubs into clearance hole |
| Tube clearance bore | 8.0 | 2.0 | 8.5 | 6.35 mm tube with 0.825 mm radial clearance |

**Bore plate fitting bores (Y = 28.0 to Y = 40.2):**

The bore plate is formed by cylindrical bosses extending from the rear wall interior face (Y = 8.5) to Y = 40.2. Each boss is a solid cylinder from Y = 8.5 to Y = 28.0 (19.5 mm structural support), with the bore cut only through the bore plate region (Y = 28.0 to Y = 40.2).

| Feature | Diameter (mm) | Y-start | Y-end | Depth (mm) | Purpose |
|---------|---------------|---------|-------|------------|---------|
| Dock-side counterbore | 15.5 | 26.0 | 28.0 | 2.0 | Recess for dock-side body end shoulder; seats the 15.10 mm to 9.31 mm transition |
| Press-fit bore | 9.5 | 28.0 | 40.2 | 12.2 | Captures 9.31 mm center body in press-fit |
| User-side counterbore | 15.5 | 40.2 | 42.2 | 2.0 | Recess for user-side body end shoulder |

**Boss outer diameter:** 20.0 mm (provides 2.25 mm wall thickness around 15.5 mm counterbore). Alternatively, a single rectangular reinforcement plate spanning all 4 bores: approximately X = 58 to X = 102, Z = 14 to Z = 58, Y = 8.5 to Y = 42.2. Design choice -- deferred to parts specification.

### 3g. Fitting Barbell Profile Mapped into Tray Frame

For each fitting (bore centers at X, Z from section 3d), the complete fitting profile along Y:

| Zone | Y-start | Y-end | OD (mm) | Description |
|------|---------|-------|---------|-------------|
| Dock collet (extended) | 14.5 | 15.9 | 9.57 | Moving release sleeve, dock side |
| Dock body end | 15.9 | 28.0 | 15.10 | Fixed housing, dock side |
| Center body | 28.0 | 40.2 | 9.31 | Press-fit zone (in 9.5 mm bore) |
| User body end | 40.2 | 52.3 | 15.10 | Fixed housing, user side |
| User collet (extended) | 52.3 | 53.7 | 9.57 | Moving release sleeve, user side |

Tube insertion on user side: tube enters at Y = 52.3, inserts ~16 mm to Y = 36.3 (inside the fitting body, past the center).

### 3h. Release Plate Interface Positions

The release plate (detailed in its own spatial document) interfaces with Sub-D at these positions in the tray frame:

| Feature | X (mm) | Y (mm) | Z (mm) | Diameter (mm) |
|---------|--------|--------|--------|---------------|
| Stepped bore 1 center | 70.0 | 9.5 to 14.5 | 26.0 | 6.5 / 9.8 / 15.5 (through / collet / clearance) |
| Stepped bore 2 center | 90.0 | 9.5 to 14.5 | 26.0 | 6.5 / 9.8 / 15.5 |
| Stepped bore 3 center | 70.0 | 9.5 to 14.5 | 46.0 | 6.5 / 9.8 / 15.5 |
| Stepped bore 4 center | 90.0 | 9.5 to 14.5 | 46.0 | 6.5 / 9.8 / 15.5 |
| Guide bore P1 | 58.0 | 9.5 to 14.5 | 14.5 | 3.7-3.8 |
| Guide bore P2 | 102.0 | 9.5 to 14.5 | 57.5 | 3.7-3.8 |
| Guide bore P3 | 58.0 | 9.5 to 14.5 | 57.5 | 3.7-3.8 |
| Guide bore P4 | 102.0 | 9.5 to 14.5 | 14.5 | 3.7-3.8 |

The release plate bore centers are coaxial with the fitting bore centers and the guide post centers.

### 3i. Rear Wall Tube Pass-Through Positions

4 clearance holes in the rear wall (Y = 0 to Y = 8.5), coaxial with the fitting bores:

| Hole | X (mm) | Z (mm) | Bore diameter (mm) | Funnel OD at Y=0 (mm) |
|------|--------|--------|--------------------|-----------------------|
| 1 | 70.0 | 26.0 | 8.0 | 12.0 |
| 2 | 90.0 | 26.0 | 8.0 | 12.0 |
| 3 | 70.0 | 46.0 | 8.0 | 12.0 |
| 4 | 90.0 | 46.0 | 8.0 | 12.0 |

These are simple clearance holes for tube passage. The entry funnels on the dock face (Y = 0) are conical countersinks tapering from 12.0 mm to 8.0 mm over 2.0 mm depth.

---

## 4. Transform Summary

```
Sub-D frame = Tray frame = Sub-A frame (identity transform)

No rotation. No translation.
All coordinates in this document are directly in the tray frame.
```

### Verification

- Bore 1 center at tray (70.0, 34.1, 26.0) -- center of center body, lower-left bore. Within interior pocket (X: 5-155, Y: 8.5-155, Z: 3-72). Correct.
- Bore plate dock face at tray Y = 28.0 -- inside cartridge interior (Y > 8.5). Correct.
- Release plate dock face at rest at tray Y = 9.5 -- just inside rear wall interior (Y > 8.5). Correct.
- Entry funnel at tray (70.0, 0, 26.0) -- on dock face of rear wall (Y = 0). Correct.
- Guide post P1 base at tray (58.0, 8.5, 14.5) -- on rear wall interior face (Y = 8.5), within interior bounds. Correct.

---

## 5. Key Dimensions Summary Table

All values in tray frame (mm).

| Parameter | Value | Source |
|-----------|-------|--------|
| Bore grid center (X, Z) | (80.0, 36.0) | Centered on rear wall |
| Bore center-to-center spacing | 20.0 x 20.0 | Decision doc + clearance analysis |
| Bore plate Y range | 28.0 to 40.2 | Derived from Y stack-up |
| Bore plate thickness | 12.2 | Matches center body length (12.16 caliper-verified) |
| Press-fit bore diameter | 9.5 | 0.19 mm interference on 9.31 mm center body |
| Counterbore diameter (both faces) | 15.5 | Clears 15.10 mm body end OD |
| Counterbore depth (both faces) | 2.0 | Recesses shoulder transition |
| Boss support length (rear wall to bore plate) | 19.5 | Y = 8.5 to Y = 28.0 |
| Boss outer diameter | 20.0 | 2.25 mm wall around 15.5 mm counterbore |
| Rear wall tube clearance bore | 8.0 | 0.825 mm radial clearance on 6.35 mm tube |
| Entry funnel (dock face) | 12.0 to 8.0 taper, 2.0 deep | Guides dock tube stubs |
| Release plate Y range (at rest) | 9.5 to 14.5 | 1.0 mm gap from rear wall interior |
| Fitting dock-side collet tip (extended) | Y = 14.5 | Contacts release plate user face at rest |
| Fitting user-side port face | Y = 52.3 | Tube connection point |
| Guide post Y range | 8.5 to 22.0 | 13.5 mm long, base on rear wall interior |
