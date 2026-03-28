# Pump Cartridge — Spatial Resolution

This document resolves every spatial relationship in the pump cartridge mechanism into concrete coordinates in each part's own reference frame. Every number is in a named frame. No downstream derivation is required.

---

## 1. System-Level Placement

```
Mechanism: Pump Cartridge Assembly (cartridge + dock)
Parent: Enclosure interior (220mm W x 300mm D x 400mm H)
Position: bottom-front of enclosure, centered on width
  Dock cradle centerline at enclosure X = 110mm
  Dock cradle bottom at enclosure Z = 0mm (enclosure floor)
  Dock cradle front face at enclosure Y = 0mm (enclosure front panel)
Orientation: level (no rotation), cartridge insertion axis = enclosure Y axis (front to back)
```

The cartridge slides in along the enclosure Y axis. When fully docked, the cartridge front face is flush with the enclosure front panel.

---

## 2. Part Reference Frames

All dimensions in millimeters.

### 2.1 Cartridge Tray

```
Origin: outer lower-left corner of the FRONT face (user-facing)
X: width, left to right, 0..140
Y: depth, front face toward rear wall, 0..121
Z: height, bottom to top, 0..70
Print orientation: rear wall (Y=121) down on build plate; front opening (Y=0) faces up
Installed: X = enclosure width axis, Y = insertion axis (toward dock rear wall), Z = vertical
```

Y=0 is the cartridge front face (user side). Y=121 is the rear wall outboard face (dock side). The rear wall extends from Y=112.5 (inner face) to Y=121 (outboard face), giving 8.5mm wall thickness.

### 2.2 Cartridge Lid

```
Origin: lower-left-front corner
X: 0..140 (matches tray width)
Y: 0..121 (matches tray depth)
Z: 0..4 (thickness)
Print orientation: outer surface (Z=4) down on build plate
Installed: sits atop tray, lid Z=0 at tray Z=70
```

### 2.3 Lever

```
Origin: center of left pivot stub end face
X: left pivot to right pivot, 0..130 (spans tray interior between side walls)
Y: pivot axis reference, paddle extends in -Y direction (toward user)
Z: perpendicular to pivot axis in the plane of rotation
Print orientation: paddle face down on build plate
Installed: pivot axis parallel to tray X axis
```

The lever's local Y and Z rotate with the lever. At the locked position, lever-local -Y aligns with tray -Y (toward user) and lever-local +Z aligns with tray -Z (downward). At the unlocked position (90 degrees rotated), lever-local -Y aligns with tray +Z (upward).

### 2.4 Release Plate

```
Origin: lower-left corner of the collet-contact face (+Y face in tray frame)
X: 0..120 (plate width)
Z: 0..50 (plate height)
Y: 0..3 (plate thickness; Y=0 is collet-contact face, Y=3 is rear face)
Print orientation: flat, XZ plane on build plate
Installed: collet-contact face faces in -Y direction (toward dock / away from user)
  Sits outboard of tray rear wall, between rear wall outboard face and dock tube stubs
```

Note on installed orientation: despite "collet-contact face" being at plate Y=0, in the tray frame this face points in the +Y direction (toward the wall/user). The plate pushes collets inward by moving in the +Y direction in tray frame. See Section 3.4 for the full mapping.

### 2.5 Front Bezel

```
Origin: lower-left corner of outer (user-facing) surface
X: 0..140 (matches tray width)
Y: 0..5 (depth into tray)
Z: 0..70 (matches tray height)
Print orientation: outer face (Y=0) down on build plate
Installed: press-fits onto tray front opening, bezel Y=0 at tray Y=0
```

### 2.6 Dock Cradle

```
Origin: lower-left corner of the front opening (user-facing side, floor level)
X: 0..160 (wider than cartridge for rail walls and clearance)
Y: 0..130 (depth; front opening toward rear wall)
Z: 0..80 (taller than cartridge for rail structure)
Print orientation: rear wall (Y=130) down on build plate
Installed: front opening at enclosure front panel, Y increases toward enclosure rear
```

### 2.7 Dock Floor Plate

```
Origin: lower-left-front corner
X: 0..150
Y: 0..120
Z: 0..3 (thickness)
Print orientation: flat on build plate
Installed: snaps into ledge at dock cradle inner floor level (cradle Z=5)
```

### 2.8 Dock Face Frame

```
Origin: lower-left corner of outer (user-facing) surface
X: 0..170
Y: 0..5 (depth)
Z: 0..90
Print orientation: outer face down on build plate
Installed: outer face flush with enclosure front panel
```

---

## 3. Derived Geometry

### 3.1 Pump Placement in Tray Frame

Two Kamoer KPHM400 pumps sit side by side, pump heads facing front (toward Y=0), motors facing rear (toward Y=121).

**Key pump dimensions (caliper-verified):**
- Pump head: 62.6mm square cross-section, 48mm deep
- Mounting bracket: 68.6mm wide, at junction between head and motor
- Motor body: ~35mm diameter, ~63mm long (end cap to bracket)
- Motor nub: 5mm protrusion from motor end cap
- Total length (with nub): 116.5mm
- Total length (without nub): 111.4mm
- Mounting hole spacing: 49.45mm center-to-center (on bracket ears)
- Mounting hole diameter: 3.13mm (M3 clearance)

**Pump center X positions in tray frame:**

```
Tray inner width: X = 5.0 to X = 135.0 (5mm side walls)
Available interior: 130.0mm
Two pump heads at 62.6mm: 125.2mm total
Center gap: 4.8mm

Pump 1 (left) X_center:  36.5mm  (spans X = 5.2 to X = 67.8)
Pump 2 (right) X_center: 103.5mm (spans X = 72.2 to X = 134.8)
Center-to-center (X): 67.0mm
```

**Pump Z position in tray frame:**

```
Tray floor: Z = 0 (outer), Z = 3.0 (inner, 3mm floor thickness)
Pump head bottom face: Z = 3.5 (0.5mm clearance above inner floor)
Pump head top face: Z = 3.5 + 62.6 = 66.1
Pump Z_center: 34.8
Tray inner ceiling (lid bottom): Z = 70.0 (3.9mm clearance above pump top)
```

**Pump Y positions in tray frame (all features along depth axis):**

| Feature | Y position | Notes |
|---------|-----------|-------|
| Pump head front face | 0.6 | 0.6mm behind tray front opening (Y=0) |
| Pump head rear face / bracket plane | 48.6 | 0.6 + 48.0 |
| Motor adapter plate | 48.6 to 52.6 | ~4mm thick |
| Motor body start | 52.6 | |
| Motor end cap | 111.0 | 0.6 + 111.4 - 1.0 (rounded) |
| Motor nub tip | 116.0 | 111.0 + 5.0 |
| Rear wall inner face | 112.5 | 1.5mm clearance from motor end cap |
| Rear wall outboard face | 121.0 | 112.5 + 8.5 |

Motor nub pocket in rear wall: centered on each pump's X_center, 8mm diameter, extending from Y = 112.5 to Y = 117.5 (5mm deep into the 8.5mm wall).

### 3.2 Pump Mounting Holes in Tray Frame

The bracket has 2 mounting holes per pump, spaced 49.45mm center-to-center along the X axis, centered on each pump. Both holes are at the bracket Z height (pump Z_center = 34.8) and at the bracket Y plane (Y = 48.6).

| Hole ID | X | Y | Z | Frame |
|---------|-----|------|------|-------|
| P1-L (pump 1, left) | 11.8 | 48.6 | 34.8 | Tray |
| P1-R (pump 1, right) | 61.2 | 48.6 | 34.8 | Tray |
| P2-L (pump 2, left) | 78.8 | 48.6 | 34.8 | Tray |
| P2-R (pump 2, right) | 128.2 | 48.6 | 34.8 | Tray |

Derivation:
- P1-L X: 36.5 - 24.725 = 11.8
- P1-R X: 36.5 + 24.725 = 61.2
- P2-L X: 103.5 - 24.725 = 78.8
- P2-R X: 103.5 + 24.725 = 128.2

All holes: diameter 3.13mm (M3 clearance). Heat-set insert boss: 7.0mm OD, 5.0mm depth in +Z direction (into tray floor boss, building upward from floor).

### 3.3 John Guest Fitting Positions in Tray Rear Wall

Each pump has two tube connections (inlet and outlet). The Kamoer pump has two barbed connectors on its front face, offset roughly +/-15mm from the pump center in Z. The fittings in the rear wall are arranged in a 2x2 rectangular pattern centered on the two pump X positions. The fitting Z positions are spaced 30mm apart (matching approximate pump barb spacing) and centered on pump Z_center.

**Fitting center positions (bore centerline) in tray frame, at rear wall outboard face Y = 121.0:**

| Fitting | X | Y | Z | Tray frame | Connects to |
|---------|-----|-------|------|------------|-------------|
| F1 | 36.5 | 121.0 | 49.8 | Tray | Pump 1 outlet (upper barb) |
| F2 | 36.5 | 121.0 | 19.8 | Tray | Pump 1 inlet (lower barb) |
| F3 | 103.5 | 121.0 | 49.8 | Tray | Pump 2 outlet (upper barb) |
| F4 | 103.5 | 121.0 | 19.8 | Tray | Pump 2 inlet (lower barb) |

**Fitting pattern dimensions:**
- X span: 67.0mm (between F1/F2 and F3/F4)
- Z span: 30.0mm (between upper and lower fittings)
- Pattern center: (70.0, 121.0, 34.8) in tray frame
- Pattern diagonal: 73.4mm (for angular tolerance analysis; half-diagonal = 36.7mm)

**Fitting axial profile in tray frame (Y axis):**

The fitting's center body (9.31mm OD, 12.16mm long) passes through the 8.5mm rear wall bore (9.5mm diameter bore). The outboard body end shoulder seats against the wall's outboard face.

| Zone | Y_start | Y_end | OD | Notes |
|------|---------|-------|-----|-------|
| Outboard collet (extended) | 122.4 | 121.0 | 9.57 | Collet protrudes 1.4mm from body end face |
| Outboard body end | 121.0 | 133.1 | 15.10 | 12.08mm long, protrudes outboard (+Y) |
| Shoulder (outboard) | 121.0 | 121.0 | 15.10 to 9.31 | Seats against wall outboard face |
| Center body (in bore) | 121.0 | 112.5 | 9.31 | In 9.5mm bore through 8.5mm wall |
| Center body (inboard protrusion) | 112.5 | 108.8 | 9.31 | Protrudes 3.7mm past wall inner face |
| Shoulder (inboard) | 108.8 | 108.8 | 9.31 to 15.10 | |
| Inboard body end | 108.8 | 96.7 | 15.10 | 12.08mm, protrudes into cartridge interior |
| Inboard collet (extended) | 96.7 | 95.3 | 9.57 | Protrudes 1.4mm, faces cartridge interior |

Note: Y values increase toward the rear/dock. Outboard body end protrudes beyond the tray rear face. The outboard collet is where dock tube stubs enter. The inboard collet is where internal silicone tubing connects from pump barbs.

**Entry funnel geometry around each fitting bore (outboard face, Y > 121.0):**

```
Funnel mouth diameter: 12.0mm (at Y = 129.0, which is 8mm outboard from wall face)
Funnel exit diameter: 9.5mm (at Y = 121.0, matches bore)
Taper half-angle: 9 degrees
Funnel depth: 8.0mm
```

The funnel is printed into the rear wall exterior. The fitting's outboard body end (15.10mm OD) protrudes through and past the funnel.

### 3.4 Release Plate Position and Geometry

The release plate sits on the outboard side of the tray rear wall, between the outboard body ends of the four fittings and the dock's tube stubs (when docked). The plate slides along the Y axis on two guide posts.

**Plate position in tray frame:**

The plate's collet-contact face is the face closest to the fittings' outboard body ends (+Y side of the plate in installed orientation).

```
Plate at rest position (lever locked):
  Collet-contact face: Y = 134.5  (1.4mm outboard of fitting body end faces at Y=133.1)
  Rear face: Y = 137.5  (3mm plate thickness)
  The plate does NOT contact the collets at rest — 1.4mm gap.

Plate at actuated position (lever unlocked, plate shifted 3.0mm toward fittings):
  Collet-contact face: Y = 131.5  (shifted 3.0mm in -Y direction toward fittings)
  Rear face: Y = 134.5

Collet engagement:
  Outboard collet extended face at Y = 133.1 + 1.4 = 134.5 (same as plate rest position)
  After 3mm plate shift, plate face at Y = 131.5
  Collet is pushed from Y = 134.5 to Y = 134.5 - 1.3 = 133.2 (compressed)
  Plate face reaches Y = 131.5 while collet stops at Y = 133.2
  Net collet compression: 1.3mm (full release travel achieved)
```

Wait — I had the directions confused above. Let me redo this clearly.

In tray frame, +Y points from front face toward rear wall toward dock. The outboard direction is +Y.

The outboard body end of each fitting protrudes from Y = 121.0 to Y = 133.1 (12.08mm outboard of wall face). The outboard collet (extended) protrudes an additional 1.4mm to Y = 134.5.

The release plate sits outboard of the body ends. Its collet-contact face (the face pointing in the -Y direction, toward the fittings) is:

```
At rest (locked): collet-contact face at Y = 136.0 (2.9mm gap to collet face at Y=134.5,
                                                     this includes the gap and body-end clearance)
At actuated (unlocked): plate shifts -Y by 3.0mm, contact face at Y = 133.0

The plate engages and pushes each collet inward (-Y direction):
  Collet face starts at Y = 134.5 (extended)
  Plate contact begins when plate face reaches Y = 134.5 (after 1.5mm of travel)
  Remaining 1.5mm of plate travel pushes collet to Y = 134.5 - 1.5 = 133.0
  Collet compression: 1.5mm (more than the 1.3mm needed for full release)
```

**Revised release plate positions in tray frame:**

```
Plate at rest (locked):
  -Y face (collet-contact face): Y = 136.0
  +Y face (dock-facing / rear face): Y = 139.0  (3mm thickness)

Plate at full actuation (unlocked):
  -Y face: Y = 133.0  (shifted 3.0mm in -Y)
  +Y face: Y = 136.0

Plate travel: 3.0mm in -Y direction (toward fittings/wall)
```

**Fitting bore centers in release plate frame:**

Plate is 120mm wide (X), 50mm tall (Z). In tray frame the plate is centered on the fitting pattern:
- Plate left edge at tray X = (140 - 120) / 2 = 10.0
- Plate bottom edge at tray Z = 34.8 - 25.0 = 9.8

Transform from tray to plate: plate_X = tray_X - 10.0, plate_Z = tray_Z - 9.8

| Fitting | Tray (X, Z) | Plate (X, Z) |
|---------|-------------|--------------|
| F1 | (36.5, 49.8) | (26.5, 40.0) |
| F2 | (36.5, 19.8) | (26.5, 10.0) |
| F3 | (103.5, 49.8) | (93.5, 40.0) |
| F4 | (103.5, 19.8) | (93.5, 10.0) |

**Stepped bore profile at each fitting center in release plate frame (Y=0 is collet-contact face, Y increases toward dock):**

| Zone | Diameter | Y_start | Y_end | Purpose |
|------|----------|---------|-------|---------|
| Tube clearance | 6.5 | 0.0 | 0.5 | Clears 6.35mm tube; annular face 6.5-9.57mm contacts collet |
| Collet hugger | 9.8 | 0.5 | 2.0 | Surrounds 9.57mm collet OD for lateral constraint |
| Body end relief | 15.5 | 2.0 | 3.0 | Clears 15.10mm body end OD |

### 3.5 Guide Posts for Release Plate

Two guide posts protrude from the tray rear wall outboard face (Y = 121.0), extending in the +Y direction. The release plate's edge slots ride on these posts.

**Guide post positions in tray frame:**

| Post | X | Y_base | Y_tip | Z | Diameter |
|------|-----|--------|-------|-----|----------|
| Left | 8.0 | 121.0 | 143.0 | 34.8 | 4.0 |
| Right | 132.0 | 121.0 | 143.0 | 34.8 | 4.0 |

Posts are 22mm long, extending outboard past the plate's maximum +Y extent (139.0 at rest) with 4mm margin.

**Guide slot positions in release plate frame:**

The guide posts pass through slots at the plate edges. Slot is open on the plate edge (allowing the plate to be dropped onto the posts from the side).

| Slot | Plate X_center | Plate Z_center | Slot width | Slot height |
|------|---------------|----------------|------------|-------------|
| Left | -2.0 (open at left edge) | 25.0 | 4.3 (0.3mm clearance) | 4.3 |
| Right | 122.0 (open at right edge) | 25.0 | 4.3 | 4.3 |

### 3.6 Lever Pivot Axis

The lever pivot runs parallel to the tray X axis, through the tray side walls near the front of the tray. The pivot is positioned so the paddle covers the lower portion of the front face when locked.

**Pivot axis position in tray frame:**

```
Y = 9.0   (9mm from front face, inside the tray near the front)
Z = 58.0  (near the top of the tray, leaving 40mm of paddle below and 12mm above)
X: left bearing hole at X = 3.0 (in left wall), right bearing hole at X = 137.0 (in right wall)
Span between bearings: 130mm (tray inner width = 135 - 5 = 130)
```

**Bearing hole positions in tray frame:**

| Bearing | X_center | Y_center | Z_center | Hole diameter | Depth (into wall) |
|---------|----------|----------|----------|---------------|-------------------|
| Left | 2.5 | 9.0 | 58.0 | 6.1 | 5.0 (from X=5 inward to X=0) |
| Right | 137.5 | 9.0 | 58.0 | 6.1 | 5.0 (from X=135 inward to X=140) |

Lever pivot stub diameter: 6.0mm (0.1mm diametral clearance in 6.1mm holes).

### 3.7 Cam Lobe Geometry

Each cam lobe is an eccentric disc integral to the lever at the pivot stub ends, positioned inside the tray side walls.

**Cam lobe positions in lever frame:**

```
Left cam lobe:
  Center of eccentric disc: X = 2.0, Y = 0.0, Z = 3.0  (3mm offset from pivot in Z)
  Disc radius: 8.0mm
  Disc thickness: 4.0mm (X = 0.0 to X = 4.0)

Right cam lobe:
  Center of eccentric disc: X = 128.0, Y = 0.0, Z = 3.0
  Disc radius: 8.0mm
  Disc thickness: 4.0mm (X = 126.0 to X = 130.0)
```

**Cam lobe positions in tray frame (locked position):**

When locked, the lever is in its "down" position with the paddle hanging below the pivot. In this position, lever-local Z = 3mm maps to tray -Z (the cam eccentricity points downward).

```
Left cam lobe center in tray frame (locked):
  X = 7.0  (5.0 wall + 2.0 offset)
  Y = 9.0  (same as pivot)
  Z = 55.0  (58.0 - 3.0 eccentricity pointing down)
  Disc radius: 8.0
  Lowermost contact point: Z = 55.0 - 8.0 = 47.0

Right cam lobe center in tray frame (locked):
  X = 133.0
  Y = 9.0
  Z = 55.0
  Disc radius: 8.0
  Lowermost contact point: Z = 47.0
```

When unlocked (lever rotated 90 degrees, paddle up), the 3mm eccentricity shifts from -Z to +Y:

```
Left cam lobe center in tray frame (unlocked):
  X = 7.0
  Y = 9.0 + 3.0 = 12.0  (eccentricity now points in +Y direction)
  Z = 58.0  (returns to pivot Z)
  Rearmost contact point: Y = 12.0 + 8.0 = 20.0

Right cam lobe center in tray frame (unlocked):
  X = 133.0
  Y = 12.0
  Z = 58.0
  Rearmost contact point: Y = 20.0
```

**Cam-to-plate force transmission:**

The cam lobes are near the front of the tray (Y = 9.0). The release plate is at the rear (Y = 133 to 139). The 3mm cam eccentric displacement must be transmitted ~125mm from cam to plate.

This requires two push rods (one per side) running along the tray side walls from the cam lobe contact zone to the release plate transfer tabs:

```
Push rod path in tray frame:
  Left rod: X = 7.0, Z = 58.0, from Y = 20.0 (cam contact) to Y = 121.0 (rear wall)
  Right rod: X = 133.0, Z = 58.0, from Y = 20.0 to Y = 121.0
  Rod passes through slots in the rear wall to contact release plate transfer tabs
```

The push rods slide in channels molded into the tray side wall interior faces. When the lever unlocks, the cam eccentricity shifts 3mm in the +Y direction, pushing the rods +Y by 3mm, which pushes the release plate transfer tabs +Y by 3mm. Since the release plate needs to move in the -Y direction (toward fittings), the rod acts THROUGH the rear wall and pushes on the -Y face of the plate transfer tabs from the +Y side...

Actually, the rod pushes the plate in the +Y direction from the inboard side. Wait, the plate is on the outboard side of the wall (Y > 121). The rod would need to pass through the wall. If the rod pushes in +Y and the plate is at Y=136 (outboard), the rod pushes the plate further outboard (+Y), which is AWAY from the fittings. That's the wrong direction.

The plate needs to move in the -Y direction (toward the fittings). For that, the mechanism must PULL the plate in -Y.

**Alternative mechanism: the cam pulls the plate via the push rods.** When locked, the cam eccentricity points down (-Z) and the push rods are at rest (no Y displacement). When unlocked, the cam rotates 90 degrees and the eccentricity shifts to -Y (toward front), pulling the rods -Y by 3mm, which pulls the plate -Y by 3mm (toward the fittings).

Let me re-examine the cam rotation direction. The lever paddle is below the pivot when locked. When the user flips the lever up, the paddle swings from below (locked) to above (unlocked), rotating in the direction where the bottom moves toward +Y (paddle swings up and over). This means the cam eccentricity, which was at -Z (downward) in locked position, rotates to +Y (rearward) when unlocked.

So: locked = cam eccentricity at -Z, unlocked = cam eccentricity at +Y. The push rods are pushed REARWARD (+Y) by 3mm when unlocking. This pushes the plate +Y (further away from fittings), which is wrong.

If instead the push rods are behind the cam (rod runs from cam to rear in -Y direction, not +Y), then the cam eccentricity shifting to +Y would push the rod contact point +Y, which means the rod tip at the rear also moves +Y. Still wrong direction.

The geometry needs the cam rotation to produce -Y motion at the plate. This happens if the lever rotation direction is the opposite: when unlocking, the paddle swings so the cam eccentricity shifts to -Y. Then the push rods move -Y, pulling the plate -Y (toward fittings).

For this, when unlocking (flipping up), the bottom of the paddle must move in the -Y direction (toward front/user). This means the paddle rotates backward (top goes toward +Y, bottom goes toward -Y). The cam eccentricity, starting at -Z (down), rotates to -Y (toward front). The push rods are then pushed -Y by 3mm, and they pull the release plate -Y by 3mm via connections through the rear wall.

But physically, flipping the lever "up" from a locked-down position: if the pivot is near the top of the front face (Z=58) and the paddle hangs down to Z=18 when locked, flipping up would swing the bottom of the paddle forward (toward -Y) and then up. This is consistent with the cam eccentricity moving from -Z toward -Y.

Let me re-derive with the corrected rotation:

```
Locked position: cam eccentricity points -Z (downward)
  Left cam disc center in tray frame: (7.0, 9.0, 55.0)

Unlocked position (90 degrees, paddle bottom swings toward user then up):
  Cam eccentricity rotates from -Z toward -Y
  Left cam disc center in tray frame: (7.0, 6.0, 58.0)  [9.0 - 3.0 = 6.0]

Push rods:
  Locked: rod rests with no -Y displacement
  Unlocked: cam contact shifts to Y = 6.0, pushing rod tip 3mm in -Y direction
  But rod contact is at Y ≈ 6.0 (near front)... and the rod needs to transmit this to Y = 121+ (rear wall)
```

This is getting complicated. The push rod doesn't change the direction — a 3mm shift at one end of a rigid rod produces a 3mm shift at the other end in the same direction. So if the cam shifts the rod -Y by 3mm at the front, the rod tip at the rear also shifts -Y by 3mm. This pulls the release plate -Y by 3mm.

But wait: the release plate is outboard of the rear wall (Y > 121). If the rod connects through the rear wall to the plate, and the rod shifts -Y by 3mm, the rod pulls the plate -Y (toward fittings). This IS the correct direction.

**Resolved cam-to-plate linkage:**

```
Mechanism: Two push/pull rods running along tray side wall interiors
  Left rod: X = 7.0, Z = 58.0, from Y = 6.0 (cam contact, unlocked) to Y = 136.0 (plate tab)
  Right rod: X = 133.0, Z = 58.0, same Y range

When lever goes from locked to unlocked:
  Cam eccentricity shifts from (0, 0, -3) to (0, -3, 0) relative to pivot
  Rod front end shifts 3mm in -Y direction
  Rod rear end shifts 3mm in -Y direction
  Release plate shifts 3mm in -Y direction (toward fittings)
  Plate collet-contact face moves from Y = 136.0 to Y = 133.0
  Collets are compressed 1.5mm, achieving full release
```

**Transfer slot positions in tray rear wall (for rods to pass through to plate):**

| Slot | X_center | Z_center | Width | Height | Y range | Frame |
|------|----------|----------|-------|--------|---------|-------|
| Left | 7.0 | 58.0 | 5.0 | 5.0 | 112.5 to 121.0 (through wall) | Tray |
| Right | 133.0 | 58.0 | 5.0 | 5.0 | 112.5 to 121.0 (through wall) | Tray |

### 3.8 Lever Paddle and Detent

**Paddle geometry in lever frame:**

```
Paddle face (-Y face, user-facing when locked):
  X: 5.0 to 125.0 (120mm wide, narrower than full lever span to clear walls)
  Z: -20.0 to +20.0 (40mm tall, centered on pivot axis)
  Y: -4.0 to 0.0 (4mm thick at the pivot end)

Grip edge (bottom when locked):
  Z = -20.0, 3mm fillet radius on bottom edge for finger hook
```

**Paddle position in tray frame (locked, paddle hanging down):**

```
Paddle top edge: Y = 9.0, Z = 58.0 (at pivot)
Paddle bottom edge: Y = 9.0, Z = 18.0 (58.0 - 40.0)
Paddle outer face: Y = 5.0 (9.0 - 4.0 thickness, facing toward user)
Paddle inner face: Y = 9.0 (at pivot Y)
```

The paddle bottom (Z=18) is above the tray floor (Z=0), and the front bezel covers the area from Z=0 to Z=18 below the paddle and from Z=58 to Z=70 above it.

**Detent notch positions in front bezel frame:**

The bezel has two V-notches on the inner face (Y=5 plane) that receive a spring tab on the lever:

| Notch | Bezel X | Bezel Y | Bezel Z | Position |
|-------|---------|---------|---------|----------|
| Locked | 70.0 | 5.0 | 18.0 | At paddle bottom edge when locked |
| Unlocked | 70.0 | 5.0 | 58.0 | At paddle bottom edge when unlocked (rotated 90 deg) |

Notch geometry: V-shape, 2mm wide, 0.5mm deep, 45-degree walls.

**Lever paddle cutout in front bezel frame:**

```
Cutout: X = 10.0 to 130.0, Z = 18.0 to 58.0
Rebate: 0.5mm step-in around cutout perimeter (paddle sits 0.5mm recessed)
```

### 3.9 Rail Rib Geometry (Tray and Dock Cradle)

The cartridge tray has male T-profile rail ribs on both side walls. The dock cradle has matching female C-channel grooves.

**Rail rib positions on tray (tray frame):**

```
Left rail rib:
  X: 0.0 to -1.5 (protrudes 1.5mm beyond tray outer wall, which is at X=0)
  ... actually, the rib is on the outer face of the tray side wall.

Let me re-define: the tray outer walls are at X=0 and X=140. The rail ribs protrude outward.

Left rib:
  X_outer_face: -1.5 (protrudes 1.5mm left of tray wall at X=0)
  X_inner_face: 0.0 (flush with tray wall)
  Z_bottom: 20.0
  Z_top: 50.0 (30mm tall rib, centered on tray mid-height)
  Y: full depth, 0.0 to 121.0
  T-profile head: 3.0mm wide (X = -1.5 to -4.5), 2.0mm tall (centered on rib Z range)
  T-profile neck: 1.5mm wide (X = 0.0 to -1.5)

Right rib (mirror):
  X_inner_face: 140.0
  X_outer_face: 141.5
  T-profile head: X = 141.5 to 144.5
  Same Z and Y range
```

This makes the tray outer envelope 140mm + 2 x 4.5mm = 149mm including ribs. That seems wide. Let me reconsider: the ribs should be simpler.

**Revised rail rib (simple rectangular rib, not T-profile):**

```
Left rib on tray:
  Protrudes from left wall outer face (X=0) by 2.0mm in -X direction
  Rib: X = -2.0 to 0.0, Z = 25.0 to 45.0 (20mm tall), Y = 0.0 to 121.0 (full depth)

Right rib on tray:
  Protrudes from right wall outer face (X=140) by 2.0mm in +X direction
  Rib: X = 140.0 to 142.0, Z = 25.0 to 45.0, Y = 0.0 to 121.0
```

**Matching rail grooves on dock cradle (dock cradle frame):**

The dock cradle is wider than the tray. The cartridge tray (140mm wide + 2mm ribs each side = 144mm total) slides into the dock cradle's interior. The dock cradle interior width must accommodate 144mm + 0.3mm clearance per side = 144.6mm.

Dock cradle side walls: 7.7mm thick each side. Outer width = 144.6 + 2 x 7.7 = 160.0mm (matches the 160mm envelope).

The C-channel groove is cut into the dock cradle's inner side wall to accept the tray's rib.

```
Cartridge tray center is at dock cradle X = 80.0 (dock cradle is 160mm wide, centered)

Tray left wall (X=0 in tray frame) sits at dock cradle X = 80.0 - 70.0 = 10.0
Tray right wall (X=140 in tray frame) sits at dock cradle X = 80.0 + 70.0 = 150.0

Left rib (X=-2 to 0 in tray frame) sits at dock cradle X = 8.0 to 10.0
Right rib (X=140 to 142 in tray frame) sits at dock cradle X = 150.0 to 152.0

Left C-channel groove in dock cradle (cradle frame):
  Groove: X = 7.7 to 10.3, Z = 24.7 to 45.3, Y = full depth
  (2.6mm wide groove for 2.0mm rib, 0.3mm clearance per side)
  (20.6mm tall groove for 20.0mm rib, 0.3mm clearance top/bottom)

Right C-channel groove (mirror):
  Groove: X = 149.7 to 152.3, Z = 24.7 to 45.3, Y = full depth
```

**Dock cradle Z positioning:** The tray floor sits on the dock floor plate. Dock cradle inner floor at Z = 5.0 (5mm wall below floor plate). Dock floor plate at Z = 5.0 to Z = 8.0 (3mm thick). Tray bottom (Z=0 in tray frame) sits on floor plate at dock cradle Z = 8.0.

So tray Z = 0 maps to dock cradle Z = 8.0.

```
Left groove in dock cradle frame:
  Z_bottom: 24.7 + 8.0 = 32.7
  Z_top: 45.3 + 8.0 = 53.3
  X: 7.7 to 10.3

Right groove in dock cradle frame:
  Z: same as left
  X: 149.7 to 152.3
```

**Entry chamfer on dock grooves (front opening):**

```
Chamfer at Y = 130 (dock front face) extending 5mm inward to Y = 125:
  Groove width expands from 2.6mm at Y=125 to 5.6mm at Y=130 (1.5mm chamfer per side)
  Groove height expands from 20.6mm at Y=125 to 26.6mm at Y=130 (3mm chamfer top/bottom)
  30-degree entry taper on all four inner edges
```

### 3.10 Registration Boss Positions

Two tapered registration bosses on the dock cradle rear wall engage tapered sockets in the tray rear wall. Bosses are at diagonally opposite corners of the fitting pattern.

**Boss positions in dock cradle frame:**

The dock cradle rear wall is at Y = 0. Bosses protrude from the wall in the +Y direction (toward the cartridge during insertion).

| Boss | Dock X | Dock Y_base | Dock Y_tip | Dock Z |
|------|--------|-------------|------------|--------|
| Lower-left | 21.5 | 0.0 | 25.0 | 22.8 |
| Upper-right | 138.5 | 0.0 | 25.0 | 57.8 |

Derivation: the bosses are positioned at diagonally opposite corners of the fitting pattern. The fitting pattern center maps to dock cradle (80.0, -, 42.8). Boss offset from pattern center: ~25mm diagonally. Lower-left boss at fitting F2's position minus 5mm in X and Z; upper-right at F3's position plus 5mm in X and Z.

Actually, let me compute from the tray-to-dock transform first (Section 4), then map fitting positions to dock frame.

The transform from tray frame to dock cradle frame (see Section 4):
- dock_X = tray_X + 10.0
- dock_Y = 130.0 - tray_Y  (tray Y=0/front at dock Y=130, tray Y=121/rear at dock Y=9)
- dock_Z = tray_Z + 8.0

Fitting pattern center in tray frame: (70.0, 121.0, 34.8)
In dock frame: (80.0, 9.0, 42.8)

Individual fitting positions in dock frame:

| Fitting | Dock X | Dock Z |
|---------|--------|--------|
| F1 | 46.5 | 57.8 |
| F2 | 46.5 | 27.8 |
| F3 | 113.5 | 57.8 |
| F4 | 113.5 | 27.8 |

Registration bosses at diagonal corners, offset 15mm from fitting pattern corners:

| Boss | Dock X | Dock Y_base | Dock Y_tip | Dock Z | Diameter (base) | Diameter (tip) | Length |
|------|--------|-------------|------------|--------|-----------------|----------------|--------|
| Boss A (near F2) | 31.5 | 0.0 | 25.0 | 17.8 | 10.0 | 7.0 | 25.0 |
| Boss B (near F3) | 128.5 | 0.0 | 25.0 | 67.8 | 10.0 | 7.0 | 25.0 |

Boss taper: 10mm base diameter at Y=0, narrowing to 7mm at Y=25 (3mm lead-in taper over 25mm length).

**Matching sockets in tray rear wall (tray frame):**

| Socket | Tray X | Tray Y_start | Tray Y_end | Tray Z | Diameter (mouth) | Diameter (base) | Depth |
|--------|--------|-------------|------------|--------|------------------|-----------------|-------|
| Socket A | 21.5 | 121.0 | 106.0 | 9.8 | 10.3 | 7.3 | 15.0 |
| Socket B | 118.5 | 121.0 | 106.0 | 59.8 | 10.3 | 7.3 | 15.0 |

Sockets are 0.3mm oversize (10.3mm for 10mm boss) with matching taper. Socket depth is 15mm (boss enters 15mm into the socket; boss tip at Y=25 in dock frame corresponds to boss entering cartridge to Y = 121 - 25 + engagement = ~106 in tray frame).

**Registration boss engagement sequence:**

Bosses protrude 25mm from dock rear wall. Tube stubs protrude 20mm. Bosses engage the tray sockets 5mm before tubes reach fitting bores, confirming alignment before fluid connection attempt.

### 3.11 Tube Stub Positions on Dock Cradle

Four 1/4" OD (6.35mm) polyethylene tube stubs protrude from the dock cradle rear wall, aligned with the fitting positions.

**Tube stub positions in dock cradle frame:**

| Stub | Dock X | Dock Y_base | Dock Y_tip | Dock Z | Stub OD |
|------|--------|-------------|------------|--------|---------|
| S1 (mates F1) | 46.5 | 0.0 | 20.0 | 57.8 | 6.35 |
| S2 (mates F2) | 46.5 | 0.0 | 20.0 | 27.8 | 6.35 |
| S3 (mates F3) | 113.5 | 0.0 | 20.0 | 57.8 | 6.35 |
| S4 (mates F4) | 113.5 | 0.0 | 20.0 | 27.8 | 6.35 |

Stubs protrude 20mm from rear wall (Y = 0 to Y = 20). Chamfered tips: 1.5mm at 45 degrees (effective tip diameter ~3.35mm).

### 3.12 Electrical Contact Positions

Four blade contacts on the dock rear wall, four copper pads on the tray rear wall. Contacts are arranged in a horizontal row between the fittings, centered vertically on the fitting pattern.

**Contact pad positions on tray rear wall outboard face (tray frame):**

| Pad | Tray X | Tray Y | Tray Z | Width (X) | Height (Z) | Function |
|-----|--------|--------|--------|-----------|------------|----------|
| E1 | 58.0 | 121.0 | 39.8 | 10.0 | 5.0 | Motor A (+) |
| E2 | 70.0 | 121.0 | 39.8 | 10.0 | 5.0 | Motor A (-) |
| E3 | 82.0 | 121.0 | 39.8 | 10.0 | 5.0 | Motor B (+) |
| E4 | 94.0 | 121.0 | 39.8 | 10.0 | 5.0 | Motor B (-) |

Pads are centered at Z = 34.8 (fitting pattern center Z), in a row spanning X = 53 to X = 99 (between pump 1 and pump 2 fitting columns). Pads are recessed 0.1mm below the wall surface (flush with copper tape thickness).

**Matching blade contact positions on dock cradle rear wall (dock frame):**

| Contact | Dock X | Dock Y_base | Dock Y_tip | Dock Z | Width (X) | Height (Z) |
|---------|--------|-------------|------------|--------|-----------|------------|
| C1 | 68.0 | 0.0 | 1.0 | 42.8 | 10.0 | 4.0 |
| C2 | 80.0 | 0.0 | 1.0 | 42.8 | 10.0 | 4.0 |
| C3 | 92.0 | 0.0 | 1.0 | 42.8 | 10.0 | 4.0 |
| C4 | 104.0 | 0.0 | 1.0 | 42.8 | 10.0 | 4.0 |

Blade contacts protrude 1mm from dock wall face (spring travel: 3mm; contact compresses to 2mm behind wall face when cartridge is fully seated). Contacts are recessed 2mm behind the wall face at rest, protruding 1mm. When cartridge seats and presses against them, they compress to 1mm behind wall face.

### 3.13 Lid-to-Tray Interface

The lid snaps onto the tray top edges with 4 cantilever clips (2 per side).

**Clip positions in tray frame (detent ridges on tray outer side walls):**

| Clip | Tray X | Tray Y | Tray Z | Side |
|------|--------|--------|--------|------|
| CL1 | 0.0 | 30.0 | 68.0 | Left wall, outer face |
| CL2 | 0.0 | 91.0 | 68.0 | Left wall, outer face |
| CL3 | 140.0 | 30.0 | 68.0 | Right wall, outer face |
| CL4 | 140.0 | 91.0 | 68.0 | Right wall, outer face |

Detent ridge: 0.8mm protrusion in X, 2mm tall (Z = 67 to 69), 8mm long (Y +/-4mm from position).

**Matching snap hooks on lid (lid frame):**

| Hook | Lid X | Lid Y | Lid Z | Deflection direction |
|------|-------|-------|-------|---------------------|
| H1 | 0.0 | 30.0 | 0.0 | -X (hooks inward around tray left wall) |
| H2 | 0.0 | 91.0 | 0.0 | -X |
| H3 | 140.0 | 30.0 | 0.0 | +X (hooks inward around tray right wall) |
| H4 | 140.0 | 91.0 | 0.0 | +X |

Hook geometry: 0.8mm hook depth, 2mm deflection cantilever, 45-degree lead-in ramp, 12mm cantilever length, 2mm wide, 1.5mm thick.

### 3.14 Bezel-to-Tray Interface

The front bezel press-fits onto the tray front opening with 2 snap tabs.

**Bezel installation in tray frame:**

```
Bezel outer face at tray Y = 0.0 (flush with tray front; note tray front is open)
Bezel extends inward to tray Y = 5.0 (5mm depth)
Bezel covers the full front face: X = 0 to 140, Z = 0 to 70
Lever paddle cutout in bezel: X = 10 to 130, Z = 18 to 58
```

**Snap tab positions (tray frame):**

| Tab | X | Y | Z | Side |
|-----|---|---|---|------|
| T1 | 70.0 | 2.5 | 0.0 | Bottom edge |
| T2 | 70.0 | 2.5 | 70.0 | Top edge |

### 3.15 Dock Face Frame Inner Opening

The dock face frame surrounds the cartridge front bezel when docked, creating a 1mm reveal gap.

**Face frame inner opening (face frame frame):**

```
Inner opening: X = 14.0 to 156.0, Z = 9.0 to 81.0
  Width: 142mm (tray front = 140mm + 1mm gap each side)
  Height: 72mm (tray front = 70mm + 1mm gap each side)
Entry chamfer: 5mm deep at 30 degrees on all four inner edges
  At Y=0 (outer face): opening is 152mm x 82mm (5mm x tan30 = 2.9mm expansion per side)
  At Y=5 (inner face): opening is 142mm x 72mm
```

---

## 4. Transform Summary

### 4.1 Tray Frame to Dock Cradle Frame

When the cartridge is fully docked (lever locked):

```
dock_X = tray_X + 10.0
dock_Y = 130.0 - tray_Y
dock_Z = tray_Z + 8.0
```

Explanation:
- X: tray is centered in dock. Tray X=0 (left wall) maps to dock X=10 (inside dock left wall).
- Y: tray and dock Y axes point in opposite directions. Tray Y=0 (front face) maps to dock Y=130 (dock front opening). Tray Y=121 (rear wall outboard face) maps to dock Y=130-121=9.0.
- Z: tray sits on the dock floor plate. Tray Z=0 (bottom) at dock Z=8 (floor plate top surface at dock Z=5+3=8).

### 4.2 Dock Cradle Frame to Tray Frame (Inverse)

```
tray_X = dock_X - 10.0
tray_Y = 130.0 - dock_Y
tray_Z = dock_Z - 8.0
```

### 4.3 Verification: Test Points

**Test point 1: Tray origin**

```
Tray (0, 0, 0) → Dock (10.0, 130.0, 8.0)
Dock (10.0, 130.0, 8.0) → Tray (0, 0, 0)  ✓ round-trip
```

Meaning: tray front-left-bottom corner is at dock X=10 (just inside dock left wall), dock Y=130 (at dock front opening), dock Z=8 (on floor plate).

**Test point 2: Tray rear wall outboard face center**

```
Tray (70.0, 121.0, 35.0) → Dock (80.0, 9.0, 43.0)
Dock (80.0, 9.0, 43.0) → Tray (70.0, 121.0, 35.0)  ✓ round-trip
```

Meaning: center of tray rear wall maps to dock X=80 (dock center), dock Y=9 (9mm from dock rear wall), dock Z=43.

**Test point 3: Fitting F1 center**

```
Tray (36.5, 121.0, 49.8) → Dock (46.5, 9.0, 57.8)
Dock (46.5, 9.0, 57.8) → Tray (36.5, 121.0, 49.8)  ✓ round-trip
```

This confirms tube stub S1 at dock (46.5, 20.0, 57.8) is 11mm in front of fitting F1 at dock (46.5, 9.0, 57.8). In dock frame, the stub extends from Y=0 to Y=20, and the fitting outboard body end is at Y=9. The stub enters the fitting at Y=9 during insertion.

**Test point 4: Electrical contact E1 center**

```
Tray (58.0, 121.0, 39.8) → Dock (68.0, 9.0, 47.8)
Dock contact C1 at (68.0, 0-1.0, 42.8)
```

The dock Z value (47.8 for the pad vs 42.8 for the contact) shows a 5mm mismatch. This indicates the pad Z and contact Z must be reconciled. Correcting: tray pad E1 Z should be 34.8 (at fitting pattern center), which maps to dock Z = 34.8 + 8.0 = 42.8. This matches dock contact C1 Z = 42.8. ✓

Corrected tray pad positions (Z = 34.8 for all, at fitting pattern center height):

| Pad | Tray X | Tray Z | → Dock X | → Dock Z |
|-----|--------|--------|----------|----------|
| E1 | 58.0 | 34.8 | 68.0 | 42.8 ✓ |
| E2 | 70.0 | 34.8 | 80.0 | 42.8 ✓ |
| E3 | 82.0 | 34.8 | 92.0 | 42.8 ✓ |
| E4 | 94.0 | 34.8 | 104.0 | 42.8 ✓ |

**Test point 5: Registration boss A**

```
Dock boss A base at (31.5, 0.0, 17.8)
Boss tip at (31.5, 25.0, 17.8)
Boss tip in tray frame: (21.5, 105.0, 9.8)

Tray socket A mouth at (21.5, 121.0, 9.8)
In dock frame: (31.5, 9.0, 17.8) — this is at the rear wall face

When cartridge slides in, boss tip (dock Y=25) meets socket mouth (dock Y=9 when cartridge is fully seated).
During insertion, the boss enters the socket when the cartridge rear wall is at dock Y=25.
Socket depth in tray = 15mm, so socket extends from tray Y=121 to Y=106, or dock Y=9 to Y=24.
Boss length = 25mm (dock Y=0 to Y=25).
Boss engages socket at dock Y=24 (first contact), fully seats at dock Y=9 (cartridge fully docked).
```

### 4.4 Release Plate Frame to Tray Frame

```
tray_X = plate_X + 10.0
tray_Z = plate_Z + 9.8
tray_Y = depends on plate travel position:
  At rest: tray_Y = 136.0 + plate_Y  (plate Y=0 face at tray Y=136.0)
  At actuation: tray_Y = 133.0 + plate_Y
```

### 4.5 Lever Frame to Tray Frame (Locked Position)

```
tray_X = lever_X + 5.0
tray_Y = 9.0 - lever_Y   (lever -Y = toward user = tray -Y = toward front)
tray_Z = 58.0 - lever_Z   (lever -Z = tray +Z would be upward, but locked means paddle hangs down, so lever +Z = tray -Z)
```

Actually, at locked position the lever has rotated such that the paddle hangs below the pivot:

```
Locked position (paddle down):
  tray_X = lever_X + 5.0
  tray_Y = 9.0 + lever_Z  (lever Z-down maps to tray Y-forward, toward user...

This rotation mapping is complex. For clarity:

At locked position, the lever's paddle extends downward from the pivot:
  Lever point (X, Y=-40, Z=0) → paddle tip, in tray frame at (X+5, 9.0, 18.0)
  Lever point (X, Y=0, Z=0) → pivot center, in tray frame at (X+5, 9.0, 58.0)
  Lever point (X, Y=0, Z=3) → cam eccentricity, in tray frame at (X+5, 9.0, 55.0)
```

---

## Summary of Critical Interface Positions

All positions in tray frame unless noted.

### Fitting Centers (XZ positions at Y=121, rear wall outboard face)

| ID | X | Z |
|----|-----|------|
| F1 | 36.5 | 49.8 |
| F2 | 36.5 | 19.8 |
| F3 | 103.5 | 49.8 |
| F4 | 103.5 | 19.8 |

### Pump Mounting Holes (at Y=48.6, bracket plane)

| ID | X | Z |
|----|------|------|
| P1-L | 11.8 | 34.8 |
| P1-R | 61.2 | 34.8 |
| P2-L | 78.8 | 34.8 |
| P2-R | 128.2 | 34.8 |

### Registration Boss Socket Mouths (at Y=121, rear wall outboard face)

| ID | X | Z |
|----|------|------|
| A | 21.5 | 9.8 |
| B | 118.5 | 59.8 |

### Electrical Contact Pad Centers (at Y=121, rear wall outboard face)

| ID | X | Z | Function |
|----|------|------|----------|
| E1 | 58.0 | 34.8 | Motor A (+) |
| E2 | 70.0 | 34.8 | Motor A (-) |
| E3 | 82.0 | 34.8 | Motor B (+) |
| E4 | 94.0 | 34.8 | Motor B (-) |

### Pivot Axis

```
Y = 9.0, Z = 58.0, parallel to X axis, X = 5.0 to 135.0
```

### Tube Stub Positions (dock cradle frame)

| ID | Dock X | Dock Z | Stub length |
|----|--------|--------|-------------|
| S1 | 46.5 | 57.8 | 20.0 |
| S2 | 46.5 | 27.8 | 20.0 |
| S3 | 113.5 | 57.8 | 20.0 |
| S4 | 113.5 | 27.8 | 20.0 |

### Registration Boss Positions (dock cradle frame)

| ID | Dock X | Dock Z | Boss length |
|----|--------|--------|-------------|
| A | 31.5 | 17.8 | 25.0 |
| B | 128.5 | 67.8 | 25.0 |

### Dock Electrical Contact Positions (dock cradle frame)

| ID | Dock X | Dock Z |
|----|--------|--------|
| C1 | 68.0 | 42.8 |
| C2 | 80.0 | 42.8 |
| C3 | 92.0 | 42.8 |
| C4 | 104.0 | 42.8 |
