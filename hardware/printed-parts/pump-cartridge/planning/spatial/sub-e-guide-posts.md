# Spatial Resolution: Sub-E Guide Post Array

## 1. System-Level Placement

```
Mechanism: Guide Post Array (Sub-E)
Parent: Tray rear wall, dock-facing exterior surface
Position: 4 posts projecting from the rear wall exterior face (Y = 0 plane)
          in the -Y direction (toward the dock), surrounding the 2x2 fitting grid
Orientation: posts are cylindrical extrusions along -Y axis (no rotation)
```

The guide posts project outward from the dock-facing surface of the rear wall. The release plate rides on these posts in the space between the rear wall and the dock. This places the release plate on the dock side of the fittings, where it can engage the dock-facing collets to disconnect the cartridge from the dock tube stubs.

---

## 2. Part Reference Frame

```
Part: Guide Post Array (Sub-E)
  Frame: Tray reference frame (same as Sub-A)
  Origin: rear-left-bottom corner of tray
  X: width, 0..160 mm (left to right when facing the front)
  Y: depth, 0..155 mm (0 at rear/dock wall exterior, 155 at front/user side)
  Z: height, 0..72 mm (0 at floor bottom, 72 at top of side walls)
  Print orientation: posts print as part of tray, open top up, XY on build plate
  Installed orientation: identical to print orientation (no rotation)
```

Posts project in the -Y direction from Y = 0 (dock-facing exterior face of the rear wall). All coordinates below are in the tray frame.

---

## 3. Derived Geometry

### 3a. Fitting Grid Positions (reference from Sub-D)

The fitting grid is a 2x2 array at 20 mm center-to-center spacing, centered on the rear wall interior area.

Rear wall interior span: X = 5..155 mm (150 mm), Z = 3..72 mm (69 mm).
Grid center: X = 80 mm, Z = 37.5 mm.

Fitting bore centers (tray frame):

| Fitting | X (mm) | Z (mm) |
|---------|--------|--------|
| F1 (lower-left) | 70 | 27.5 |
| F2 (lower-right) | 90 | 27.5 |
| F3 (upper-left) | 70 | 47.5 |
| F4 (upper-right) | 90 | 47.5 |

Each fitting has a body end OD of 15.10 mm (radius 7.55 mm) protruding from the dock face. The fitting envelope on the dock side is:
- X: 62.45 to 97.55 mm
- Z: 19.95 to 55.05 mm

### 3b. Fitting Axial Position Along Y

The fitting is inserted from the dock side until its interior-side shoulder bears against the rear wall interior face (Y = 8.5 mm). The center body is 12.16 mm long, so it spans:

- Interior shoulder: Y = 8.5 mm (bears against rear wall interior face)
- Center body: Y = 8.5 to Y = -3.66 mm
- Dock-side shoulder: Y = -3.66 mm
- Dock-side body end (12.08 mm long): Y = -3.66 to Y = -15.74 mm
- Dock-side collet, extended (protrudes ~1.4 mm): tip at Y = -17.14 mm
- Dock-side collet, compressed (pushed ~1.3 mm inward): tip at Y = -15.84 mm

### 3c. Guide Post Positions (X, Z)

The 4 posts are placed at the corners of a 40 x 40 mm rectangle centered on the fitting grid center (80, 37.5). This places them outside the fitting body end envelopes with adequate clearance.

Guide post centers (tray frame):

| Post | X (mm) | Z (mm) | Nearest fitting center | Distance to nearest fitting (mm) | Clearance from fitting body end edge (mm) |
|------|--------|--------|----------------------|--------------------------------|------------------------------------------|
| P1 (lower-left) | 60 | 17.5 | F1 (70, 27.5) | 14.14 | 14.14 - 7.55 - 1.75 = 4.84 |
| P2 (lower-right) | 100 | 17.5 | F2 (90, 27.5) | 14.14 | 4.84 |
| P3 (upper-left) | 60 | 57.5 | F3 (70, 47.5) | 14.14 | 4.84 |
| P4 (upper-right) | 100 | 57.5 | F4 (90, 47.5) | 14.14 | 4.84 |

Clearance check: 4.84 mm between post outer surface and fitting body end outer surface. This is sufficient -- no interference with fitting installation or release plate stepped bores.

Wall clearance check:
- P1 and P3 at X = 60: distance to left wall interior (X = 5) = 55 mm. OK.
- P2 and P4 at X = 100: distance to right wall interior (X = 155) = 55 mm. OK.
- P1 and P2 at Z = 17.5: distance to floor interior (Z = 3) = 14.5 mm. OK.
- P3 and P4 at Z = 57.5: distance to top edge (Z = 72) = 14.5 mm. OK.

### 3d. Guide Post Projection Along Y

Posts project from the dock-facing exterior surface of the rear wall (Y = 0 plane) in the -Y direction (into the dock space).

The posts must be long enough to:
1. Support the release plate through its full travel range
2. Provide adequate bearing length to prevent plate tilt
3. Reach past the release plate's rest position

Release plate rest position: the plate sits against the collet faces at their extended position. The collet tips are at Y = -17.14 mm. The release plate is approximately 5 mm thick (per concept doc: "~55 x 55 x 5 mm"). Its dock-facing surface is at approximately Y = -17.14 - 5 = -22.14 mm. Its wall-facing surface contacts the collet tips at Y = -17.14 mm.

Post length must reach at least to Y = -22.14 mm from Y = 0, so minimum post length = 22.14 mm. Adding margin for a stop shoulder and to keep the plate captive:

```
Post base:  Y = 0 mm (flush with rear wall exterior face)
Post tip:   Y = -25 mm (25 mm projection into dock space)
Post length: 25 mm
Post diameter: 3.5 mm
```

### 3e. Release Plate Travel Range

The release plate slides along the Y axis on the 4 guide posts.

| Position | Y of plate wall-facing surface (mm) | Description |
|----------|-------------------------------------|-------------|
| Rest (collets extended) | -17.14 | Plate rests against extended collet faces |
| Pressed (collets compressed) | -15.84 | Plate has pushed collets inward 1.3 mm |

- Travel direction: +Y (toward the rear wall)
- Travel distance: 1.3 mm (matches collet travel per side)
- Design travel allowance: 1.5 mm (per concept doc, provides 0.2 mm margin)

The plate is pushed toward the wall (+Y direction) by the linkage mechanism when the user squeezes. At rest, springs in the collets push the plate back to Y = -17.14.

### 3f. Stop Mechanism

The posts themselves provide the stop. The release plate cannot travel past Y = 0 (rear wall face) because the wall blocks it. However, the actual stop is the collet mechanism itself -- the collet compresses only ~1.3 mm before bottoming out internally.

An explicit stop feature is not needed on the posts because:
1. The collet internal bottoming limits inward travel
2. The post tips (Y = -25 mm) and optional retaining features (snap ring or printed cap) prevent the plate from sliding off in the -Y direction during cartridge removal

Post tip stop detail:
```
Post tip position: Y = -25 mm
Stop feature: small printed mushroom cap (0.5 mm radial overhang) at Y = -25 mm
Purpose: prevents release plate from sliding off posts when cartridge is out of dock
```

### 3g. Release Plate Bore Positions on Posts

The release plate has 4 clearance bores matching the 4 post positions. The bore pattern on the plate mirrors the post pattern:

| Plate bore | X (mm) | Z (mm) | Bore diameter (mm) | Post diameter (mm) | Clearance per side (mm) |
|------------|--------|--------|--------------------|--------------------|------------------------|
| B1 | 60 | 17.5 | 3.8 | 3.5 | 0.15 |
| B2 | 100 | 17.5 | 3.8 | 3.5 | 0.15 |
| B3 | 60 | 57.5 | 3.8 | 3.5 | 0.15 |
| B4 | 100 | 57.5 | 3.8 | 3.5 | 0.15 |

Clearance of 0.15 mm per side (0.3 mm total diametral) provides smooth sliding with minimal tilt. This matches the concept doc specification of "3.7-3.8 mm bores" on 3.5 mm posts.

### 3h. Interface Positions

**Interface: Posts to rear wall exterior face**

Each post base bonds flush to the rear wall exterior face at Y = 0.
- Bond surface: circle, 3.5 mm diameter, at the (X, Z) positions listed in 3c
- Bond plane: Y = 0 (dock-facing exterior surface of rear wall)
- Mating feature: rear wall exterior face (Sub-A, Y = 0 plane)
- Post material is continuous with the rear wall (printed as one piece)

**Interface: Posts to release plate**

Each post passes through a sliding bore in the release plate.
- Post positions: (X, Z) per table 3c
- Plate bore positions: (X, Z) per table 3g, matching post positions
- Sliding fit: 3.5 mm post in 3.8 mm bore, 0.15 mm clearance per side
- Mating feature: release plate guide bores (separate printed part)
- Plate slides along Y from -17.14 to -15.64 mm (1.5 mm design travel)

**Interface: Posts to dock (clearance)**

When the cartridge is seated in the dock, the posts and release plate occupy space inside the dock cavity. The dock must provide a recess or cavity of at least:
- X: 55 to 105 mm (post span + margin)
- Z: 12.5 to 62.5 mm (post span + margin)
- Y depth from dock mating face: at least 25 mm (post length) + 5 mm (plate thickness) = 30 mm

---

## 4. Transform Summary

```
Sub-E frame = Tray frame = Sub-A frame (identity transform)

No rotation, no translation. Posts are defined directly in the tray coordinate system.
```

### Verification

| Test point | Tray frame (X, Y, Z) | Description |
|------------|----------------------|-------------|
| Post P1 base center | (60, 0, 17.5) | Lower-left post, bonded to rear wall exterior |
| Post P1 tip center | (60, -25, 17.5) | Lower-left post tip, projecting into dock space |
| Post P4 base center | (100, 0, 57.5) | Upper-right post, bonded to rear wall exterior |
| Release plate center at rest | (80, -17.14, 37.5) | Plate center, resting against extended collets |
| Release plate center when pressed | (80, -15.64, 37.5) | Plate center, collets compressed 1.5 mm |

All points are in the tray frame. The Y-negative values indicate projection into the dock space (behind the rear wall exterior face). This is geometrically consistent: the rear wall exterior is at Y = 0, and the dock is in the -Y direction.

---

## Dimensional Summary Table

| Parameter | Value | Frame |
|-----------|-------|-------|
| Number of posts | 4 | -- |
| Post diameter | 3.5 mm | -- |
| Post length | 25 mm | -- |
| Post projection direction | -Y (from Y=0 toward dock) | Tray |
| Post base plane | Y = 0 mm | Tray |
| Post tip plane | Y = -25 mm | Tray |
| Post P1 center (X, Z) | (60, 17.5) | Tray |
| Post P2 center (X, Z) | (100, 17.5) | Tray |
| Post P3 center (X, Z) | (60, 57.5) | Tray |
| Post P4 center (X, Z) | (100, 57.5) | Tray |
| Post rectangle span | 40 x 40 mm (X: 60..100, Z: 17.5..57.5) | Tray |
| Post rectangle center | (80, 37.5) = fitting grid center | Tray |
| Release plate bore diameter | 3.8 mm | -- |
| Sliding clearance per side | 0.15 mm | -- |
| Release plate rest position (wall-facing face) | Y = -17.14 mm | Tray |
| Release plate pressed position (wall-facing face) | Y = -15.64 mm | Tray |
| Release plate travel | 1.5 mm along +Y | Tray |
| Fitting grid center | X = 80, Z = 37.5 | Tray |
| Fitting spacing | 20 mm c-c in X and Z | -- |
| Min clearance: post to fitting body end | 4.84 mm (surface to surface) | -- |
| Stop feature | Mushroom cap at post tip (Y = -25) | Tray |
| Dock cavity depth required | >= 30 mm from mating face | -- |
