# Top Shell -- Spatial Resolution

This document resolves every multi-frame spatial relationship for the top shell into concrete coordinates in the top shell's own reference frame. All numbers are final -- no downstream derivation required.

---

## 1. System-Level Placement

The pump cartridge sits at the front-bottom of the enclosure (220 mm wide x 300 mm deep x 400 mm tall per vision.md). The cartridge slides in along the depth axis on T-slot rails, with its front face flush with the enclosure dock opening.

```
Mechanism: Pump Cartridge
Parent: Enclosure interior
Position: centered on enclosure width, at the bottom of the enclosure, front face flush with enclosure front wall
Orientation: no rotation -- cartridge axes align with enclosure axes
  Enclosure X (width) = Cartridge X (width)
  Enclosure Y (depth, front-to-rear) = Cartridge Y (depth, front-to-rear)
  Enclosure Z (height) = Cartridge Z (height)
```

The cartridge occupies approximately the center 155 mm of the 220 mm enclosure width, with ~32.5 mm clearance per side. It extends ~170 mm rearward from the front face. The bottom of the cartridge sits on or near the enclosure floor.

---

## 2. Part Reference Frame

The top shell is modeled in its **print orientation** -- inverted, with the palm-contact surface (the external "top" face when installed) facing down on the build plate.

```
Part: Top Shell
  Origin: lower-left-front corner of the bounding box as printed
  X: width axis, left-to-right, 0..155 mm
  Y: depth axis, front-to-rear (user side to dock side), 0..170 mm
  Z: height axis, upward from build plate, 0..50 mm

  Print orientation: inverted (palm surface is at Z=0, the build plate face)
  Installed orientation: flipped 180 degrees about the X axis, then placed
    at the front-bottom of the enclosure. The palm surface (Z=0 as printed)
    becomes the top face when installed.
```

**Envelope:** 155 mm (X) x 170 mm (Y) x 50 mm (Z)

**Coordinate conventions in this document:**
- All coordinates are in the **top shell print frame** (origin at lower-left-front corner, Z=0 on build plate = palm surface).
- X increases left-to-right.
- Y increases front-to-rear (from the user-facing front wall toward the dock-facing rear wall).
- Z increases upward from the build plate (into the shell interior).

When the shell is installed (flipped), Z=0 is the top of the cartridge and Z=50 is the interior. The X and Y axes remain unchanged.

---

## 3. Derived Geometry

### 3.1 Outer Walls

The top shell is a rectangular box with open bottom (the bottom is closed by the bottom shell). In the print frame, the open face is at the top (high Z), and the solid palm surface is at Z=0.

| Wall | Position in print frame | Thickness | Notes |
|------|------------------------|-----------|-------|
| Palm surface (external top face) | Z = 0 to Z = 1.5 mm | 1.5 mm | Cosmetic, build-plate face. Smooth finish. |
| Front wall | Y = 0 to Y = 3.0 mm, full X, Z = 0 to 50 mm | 3.0 mm | Structural: carries lever reaction forces and palm surface inset |
| Rear wall (external) | Y = 168 to Y = 170 mm, full X, Z = 0 to 50 mm | 2.0 mm | External closure; tube entry holes pass through this |
| Left side wall | X = 0 to X = 3.0 mm, full Y, Z = 0 to 50 mm | 3.0 mm | Structural: carries rail groove, lever pivot boss, snap-fit ledge |
| Right side wall | X = 152 to X = 155 mm, full Y, Z = 0 to 50 mm | 3.0 mm | Mirror of left side wall |

### 3.2 Pump Mounting Shelf

The pump mounting shelf is a horizontal plate spanning between the two side walls and tied into the rear bulkhead. It is integral with the top shell.

| Parameter | Value in print frame |
|-----------|---------------------|
| Shelf Z position (top face) | Z = 34.0 mm |
| Shelf Z position (bottom face) | Z = 31.0 mm |
| Shelf thickness | 3.0 mm (4 perimeters = 1.6 mm structural minimum; 3 mm for rigidity under pump weight) |
| Shelf X extent | X = 3.0 mm to X = 152.0 mm (side wall to side wall) |
| Shelf Y extent | Y = 80.0 mm to Y = 155.0 mm (forward edge to rear bulkhead) |

The shelf is reinforced with two vertical ribs (1.2 mm thick, Z = 31.0 down to Z = 1.5 mm) running front-to-rear underneath each pump position, connecting the shelf to the palm surface for stiffness.

### 3.3 Rear Bulkhead

The rear bulkhead is a vertical wall inside the shell, carrying the four quick connect bulkhead fittings.

| Parameter | Value in print frame |
|-----------|---------------------|
| Bulkhead Y position (front face) | Y = 155.0 mm |
| Bulkhead Y position (rear face) | Y = 158.0 mm |
| Bulkhead thickness | 3.0 mm (required for PP1208W clamping shoulder) |
| Bulkhead X extent | X = 3.0 mm to X = 152.0 mm |
| Bulkhead Z extent | Z = 1.5 mm to Z = 50.0 mm |

The space between the rear bulkhead (Y = 158.0 mm) and the outer rear wall (Y = 168.0 mm) is 10.0 mm. This zone contains the PP1208W fitting bodies protruding rearward through the bulkhead, and the tube entry holes in the outer rear wall.

### 3.4 Pump Positions

Two Kamoer KPHM400 pumps sit side-by-side on the mounting shelf. Each pump's motor cylinder passes through a bore in the shelf, with the pump head forward of the shelf and the motor body behind.

**Pump center-to-center spacing:** 74.0 mm (68.6 mm bracket width + 5.4 mm gap between brackets for wiring clearance).

**Pump 1 (left) center axis:** X = 40.5 mm, Z = 34.0 mm (shelf top face)
**Pump 2 (right) center axis:** X = 114.5 mm, Z = 34.0 mm (shelf top face)

Verification: Pump 1 bracket extends from X = 40.5 - 34.3 = 6.2 mm to X = 40.5 + 34.3 = 74.8 mm. Pump 2 bracket extends from X = 114.5 - 34.3 = 80.2 mm to X = 114.5 + 34.3 = 148.8 mm. Gap between brackets: 80.2 - 74.8 = 5.4 mm. Left bracket clears left wall (6.2 > 3.0 mm). Right bracket clears right wall (148.8 < 152.0 mm). All clear.

#### Motor Bore Holes (2x)

| Bore | Center X | Center Y | Bore diameter | Through-shelf |
|------|----------|----------|---------------|---------------|
| Pump 1 motor bore | 40.5 mm | centered on shelf, see below | 36.4 mm | Yes, Z = 31.0 to Z = 34.0 mm |
| Pump 2 motor bore | 114.5 mm | centered on shelf, see below | 36.4 mm | Yes, Z = 31.0 to Z = 34.0 mm |

The pump mounting bracket sits on the shelf top face (Z = 34.0 mm). The bracket is at the junction between pump head and motor. Per the concept internal layout, the mounting plate is at Y = 80.0 to 83.0 mm. The bore centers are at the center of the shelf Y-extent at the bracket position:

**Motor bore center Y position:** Y = 81.5 mm (midpoint of 80.0-83.0 mm shelf-to-bracket zone, which is where the bracket face sits on the shelf surface).

| Bore | Center (X, Y, Z) in print frame |
|------|----------------------------------|
| Pump 1 motor bore | (40.5, 81.5, 34.0) -- 36.4 mm diameter, through shelf |
| Pump 2 motor bore | (114.5, 81.5, 34.0) -- 36.4 mm diameter, through shelf |

#### Mounting Screw Holes (8x)

Each pump has a 48 mm x 48 mm square M3 mounting pattern centered on the motor bore. Holes are 3.4 mm diameter (M3 + 0.2 mm FDM compensation). Screws pass through the shelf from the motor side (high Z to low Z in print frame, since the shelf is inverted when installed).

**Pump 1 screw holes (centered on X=40.5, Y=81.5):**

| Hole ID | X | Y | Z (top of shelf) | Diameter |
|---------|---|---|-------------------|----------|
| P1-H1 (front-left) | 16.5 | 57.5 | 34.0 | 3.4 mm |
| P1-H2 (front-right) | 64.5 | 57.5 | 34.0 | 3.4 mm |
| P1-H3 (rear-left) | 16.5 | 105.5 | 34.0 | 3.4 mm |
| P1-H4 (rear-right) | 64.5 | 105.5 | 34.0 | 3.4 mm |

**Pump 2 screw holes (centered on X=114.5, Y=81.5):**

| Hole ID | X | Y | Z (top of shelf) | Diameter |
|---------|---|---|-------------------|----------|
| P2-H1 (front-left) | 90.5 | 57.5 | 34.0 | 3.4 mm |
| P2-H2 (front-right) | 138.5 | 57.5 | 34.0 | 3.4 mm |
| P2-H3 (rear-left) | 90.5 | 105.5 | 34.0 | 3.4 mm |
| P2-H4 (rear-right) | 138.5 | 105.5 | 34.0 | 3.4 mm |

All 8 holes are through-holes in the 3.0 mm thick shelf (Z = 31.0 to 34.0 mm).

### 3.5 Quick Connect Fitting Positions

Four PP1208W bulkhead fittings mount through the rear bulkhead. Each requires a 17.0 mm hole (per JG spec; concept says 17.2 mm with FDM compensation -- use 17.2 mm as the design diameter).

The fittings are in a 2x2 pattern. Each pump has one inlet and one outlet. The tube connectors exit the pump head's front face (forward of the mounting plate), and silicone tubing routes rearward from the pump connectors to the fittings in the bulkhead. The fitting pattern must allow clean tube routing without kinking.

**Fitting pattern derivation:**
- Horizontal (X) spacing: match the pump center-to-center of 74.0 mm. Each pump's inlet and outlet are roughly symmetric about the pump's X center. Place each pump's two fittings at the pump's X center +/- 14.0 mm (28.0 mm apart per pump pair). This gives adequate clearance between adjacent fittings (17.2 mm holes at 28 mm c-c leaves 10.8 mm between hole edges -- sufficient).
- Vertical (Z) spacing: place the fittings centered on the bulkhead height. With bulkhead from Z=1.5 to Z=50.0, the midpoint is Z=25.75. Space the two rows 28.0 mm apart (Z = 11.75 and Z = 39.75). This leaves clearance: top fitting edge at 39.75 + 8.6 = 48.35, clears 50.0. Bottom fitting edge at 11.75 - 8.6 = 3.15, clears 1.5.

**Fitting positions in print frame:**

| Fitting ID | Center X | Center Y (bulkhead front face) | Center Z | Hole diameter | Purpose |
|------------|----------|-------------------------------|----------|---------------|---------|
| QC1 (Pump 1, inlet) | 26.5 | 155.0 | 11.75 | 17.2 mm | Left pump inlet |
| QC2 (Pump 1, outlet) | 54.5 | 155.0 | 39.75 | 17.2 mm | Left pump outlet |
| QC3 (Pump 2, inlet) | 100.5 | 155.0 | 11.75 | 17.2 mm | Right pump inlet |
| QC4 (Pump 2, outlet) | 128.5 | 155.0 | 39.75 | 17.2 mm | Right pump outlet |

**Pattern summary:** Two columns at X = 26.5/54.5 (left pump) and X = 100.5/128.5 (right pump). Two rows at Z = 11.75 (inlets, lower in print frame) and Z = 39.75 (outlets, upper in print frame). Horizontal spacing within each pump pair: 28.0 mm. Vertical spacing between rows: 28.0 mm. Column-to-column spacing between pumps: 74.0 mm (matching pump c-c).

The holes are through-holes in the 3.0 mm bulkhead (Y = 155.0 to 158.0 mm).

**Corresponding rear wall tube entry holes:** Four 7.5 mm diameter holes in the outer rear wall (Y = 168.0 to 170.0 mm) at the same X, Z coordinates as the bulkhead fitting holes. These are the holes visible from outside.

| Hole ID | Center X | Center Y | Center Z | Diameter |
|---------|----------|----------|----------|----------|
| TE1 | 26.5 | 169.0 | 11.75 | 7.5 mm |
| TE2 | 54.5 | 169.0 | 39.75 | 7.5 mm |
| TE3 | 100.5 | 169.0 | 11.75 | 7.5 mm |
| TE4 | 128.5 | 169.0 | 39.75 | 7.5 mm |

### 3.6 Lever Pivot Positions

Two lever pivot bosses, one on each side wall interior. The pivot pins are 3.0 mm steel dowels press-fit into the bosses. The lever arms rotate on these pins.

**Pivot position derivation:**
- Y position: The concept places lever pivots in the Y = 15-25 mm zone. The pivot must be positioned so the short arm (4-5 mm) reaches the release plate front face (~Y = 25-35 mm zone) and the long arm (20-25 mm) reaches forward to the finger bar zone (~Y = 0-15 mm). A pivot at Y = 20.0 mm places the short arm tip at ~Y = 24-25 mm (reaching the release plate) and the long arm tip at ~Y = 0-5 mm (reaching the finger bar connection zone through the bottom shell). This satisfies the 4:1 to 6.25:1 MA requirement (20 mm long arm / 4 mm short arm = 5:1).
- Z position: The lever must sit in the interior cavity. The lever is 4 mm thick and 8 mm wide. The pivot should be at a Z that allows the lever to swing between the palm surface (Z = 1.5 mm) and the mounting shelf (Z = 31.0 mm). Place the pivot at Z = 15.0 mm (roughly mid-cavity, leaving clearance above and below for lever arm travel).
- X position: Bosses protrude from the inner faces of the side walls.

**Pivot boss geometry:** Each boss is a cylindrical protrusion, 8.0 mm outer diameter, 8.0 mm tall (protruding inward from the side wall), with a 3.0 mm bore (press-fit for pin, no FDM compensation -- 3.0 mm pin in 3.0 mm hole per concept).

| Pivot | Center X | Center Y | Center Z | Boss OD | Bore ID | Protrusion direction |
|-------|----------|----------|----------|---------|---------|---------------------|
| Left pivot | 7.0 mm (3.0 wall + 4.0 boss radius) | 20.0 | 15.0 | 8.0 mm | 3.0 mm | +X (inward from left wall) |
| Right pivot | 148.0 mm (155.0 - 3.0 wall - 4.0 boss radius) | 20.0 | 15.0 | 8.0 mm | 3.0 mm | -X (inward from right wall) |

The boss extends from the wall inner face (X = 3.0 for left, X = 152.0 for right) inward by 8.0 mm (to X = 11.0 for left, X = 144.0 for right).

**Alternate pivot holes:** Per concept, 2-3 alternate pivot holes spaced 3 mm apart in Y for tuning lever ratio. Primary hole at Y = 20.0, alternates at Y = 17.0 and Y = 23.0. Same X, Z for each.

### 3.7 Spring Pocket Positions

Two compression spring pockets **behind the release plate**. The springs bias the release plate away from the collets (toward the front / toward the user, -Y direction).

**Spring pocket derivation:**
- The release plate at rest sits at Y=35 (front face) to Y=38 (rear face). When depressed, the plate moves to Y=38 (front) to Y=42 (rear).
- Compression springs must be **behind** the plate (higher Y) to push it forward (-Y). The springs sit between the plate rear face and a fixed pocket floor at higher Y.
- Y position: Pocket floor at Y=57.0, pocket open end at Y=45.0, facing the release plate. Springs compress between the plate rear face (Y=38 at rest, Y=42 depressed) and pocket floor (Y=57.0). Free span at rest: 57-38=19mm. Compressed span at full travel: 57-42=15mm. Compression: 4mm.
- X positions: Near the side walls at X=10.0 and X=145.0. These are offset from the pump centers (X=40.5 and X=114.5) to avoid interference with pump head bodies that start at Y=50 and extend to the mounting shelf. The side-wall positions also keep the spring force symmetric about the plate centerline.
- Z position: Mid-cavity at Z=25.0, same as the release plate center height. This avoids torque on the plate from off-center spring force.

**Spring pocket geometry:** Cylindrical pockets, 7.0 mm ID (to accept ~5 mm OD springs with clearance), 12.0 mm deep (Y-direction from Y=45 to Y=57), open toward the front (-Y, toward the release plate).

| Pocket | Center X | Y range (pocket walls) | Center Z | ID | Depth (Y) |
|--------|----------|----------------------|----------|----|-----------|
| Left spring pocket | 10.0 | Y = 45.0 to Y = 57.0 | 25.0 | 7.0 mm | 12.0 mm |
| Right spring pocket | 145.0 | Y = 45.0 to Y = 57.0 | 25.0 | 7.0 mm | 12.0 mm |

The pocket walls are 1.2 mm thick (structural minimum), making the OD 9.4 mm. The pockets are formed as cylindrical bosses on the interior side walls, between the side wall and the pump head zone. The pocket floor (Y=57.0) provides the reaction surface for the compressed springs.

### 3.8 Over-Center Detent Position

A cantilever arm printed integral with an internal wall. The arm has a 1.5 mm bump that engages a groove on the release plate edge as the plate travels past.

**Detent position derivation:**
- The detent engages the release plate during its 3-4 mm travel (Y = ~32 to ~36 mm at the engagement point, which is 60-80% of the full plate travel).
- The cantilever arm is attached to the top shell's left side wall interior (or a central rib). Place it on the left interior wall for accessibility.
- The arm extends inward (in X) from the left side wall, with the bump facing the release plate's left edge.

| Parameter | Value in print frame |
|-----------|---------------------|
| Arm attachment wall | Left side wall interior, X = 3.0 mm |
| Arm base Y | Y = 28.0 mm |
| Arm tip Y | Y = 33.0 mm (arm length ~5 mm in Y-direction) |
| Arm Z (center) | Z = 25.0 mm |
| Arm cross-section | 2.0 mm wide (X) x 1.5 mm thick (Z) |
| Bump position | At arm tip, Y = 33.0 mm, protruding 1.5 mm in +X from the arm face |
| Bump peak X | X = 6.5 mm (3.0 wall + 2.0 arm width + 1.5 bump) |
| Bump engages plate edge at | Y = 33.0 mm, X = 6.5 mm, Z = 25.0 mm |

The bump engages a matching groove on the release plate's left edge. The plate edge passes by the bump during travel, deflecting the cantilever ~0.8 mm and then snapping past for the click.

### 3.9 T-Slot Rail Groove Geometry

The top shell carries the upper half of the T-profile groove on each side wall. The groove runs the full depth of the cartridge (Y = 0 to Y = 170 mm) on the exterior faces of both side walls.

**T-slot profile cross-section (viewed from front, looking in +Y direction):**

The T-slot groove is cut into the exterior of each side wall. The profile consists of a narrow neck opening at the outer surface and a wider undercut behind it.

```
Cross-section of left wall T-slot (upper half), looking in +Y:

  Exterior surface (X = 0)
        |
        |  ←2.0mm→  Neck opening
        |___________
        |           |
        |  ←5.0mm→  | ←1.5mm undercut depth (Z)
        |___________|
        |
  Wall interior (X = 3.0)

  Z increases upward (away from build plate in print frame)
```

| Parameter | Value |
|-----------|-------|
| Neck width (X direction, measured from exterior surface inward) | 2.0 mm |
| Neck height (Z extent) | 3.0 mm |
| T-bar slot width (wider portion behind neck) | 5.0 mm |
| T-bar slot depth (Z direction, behind neck) | 1.5 mm above and 1.5 mm below the neck |
| Total groove depth from exterior surface | 5.0 mm |
| Groove Y extent | Y = 0 to Y = 170 mm (full depth) |

**Left wall upper T-groove (upper half of the T-profile, straddling seam at Z=50):**

The T-groove is split at the seam (Z=50). The top shell carries the upper half: the upper portion of the neck and the upper T-bar undercut.

| Feature | X range | Z range | Y range |
|---------|---------|---------|---------|
| Neck opening (upper half) | X = 0 to X = 2.0 | Z = 48.5 to Z = 50.0 | Y = 0 to 170 |
| T-bar undercut (upper lobe) | X = 0 to X = 5.0 | Z = 47.0 to Z = 48.5 | Y = 0 to 170 |

The lower half of the T-profile is on the bottom shell. The seam between shells runs at the midpoint of the T-neck: Z = 39.5 mm in print frame (this is the horizontal split line).

**Right wall upper T-groove:** Mirror of left wall about X = 77.5 mm centerline.

| Feature | X range | Z range | Y range |
|---------|---------|---------|---------|
| Neck opening (upper half) | X = 153.0 to X = 155.0 | Z = 48.5 to Z = 50.0 | Y = 0 to 170 |
| T-bar undercut (upper lobe) | X = 150.0 to X = 155.0 | Z = 47.0 to Z = 48.5 | Y = 0 to 170 |

**45-degree chamfer on T-bar undercut ceiling:** The horizontal ceiling of the T-bar undercut (at Z = 47.0) has a 1.0 mm x 45-degree chamfer on its inward-facing leading edge to eliminate the need for print supports, per concept Section 7.

### 3.10 Snap-Fit Ledge Positions

Four ledges on the top shell interior walls for the bottom shell's snap-fit hooks. Two on the left wall, two on the right wall.

The snap-fit hooks on the bottom shell engage these ledges from below (in the print frame, from above when installed). Each ledge is a horizontal step protruding from the interior wall face.

| Ledge ID | Wall | Center X | Center Y | Ledge Z (top face) | Width (Y) | Depth (X protrusion) | Engagement depth (Z) |
|----------|------|----------|----------|--------------------|-----------|--------------------|---------------------|
| SL1 | Left interior | 3.0 (protrudes to 5.0) | 30.0 | 44.0 | 10.0 mm | 2.0 mm | 2.0 mm |
| SL2 | Left interior | 3.0 (protrudes to 5.0) | 140.0 | 44.0 | 10.0 mm | 2.0 mm | 2.0 mm |
| SL3 | Right interior | 152.0 (protrudes to 150.0) | 30.0 | 44.0 | 10.0 mm | 2.0 mm | 2.0 mm |
| SL4 | Right interior | 152.0 (protrudes to 150.0) | 140.0 | 44.0 | 10.0 mm | 2.0 mm | 2.0 mm |

Ledge details:
- Each ledge is a rectangular shelf, 10.0 mm long (Y), 2.0 mm deep (X, inward from wall), with a 2.0 mm tall (Z) hook engagement surface underneath.
- The ledge underside (Z = 42.0 to Z = 44.0) is the engagement surface the bottom shell hook catches on.
- Designed supports with 0.3 mm break-away tabs are required for the 2.0 mm undercut (per concept Section 7).

### 3.11 Alignment Pin Hole Positions

Two holes in the top shell that receive the bottom shell's 4.0 mm alignment pins. The holes are 4.2 mm diameter (0.1 mm clearance per side for snug press fit per concept).

| Hole ID | Center X | Center Y | Z range (hole depth) | Diameter |
|---------|----------|----------|---------------------|----------|
| AH1 | 20.0 | 85.0 | Z = 44.0 to Z = 50.0 (6.0 mm deep, blind hole from top) | 4.2 mm |
| AH2 | 135.0 | 85.0 | Z = 44.0 to Z = 50.0 (6.0 mm deep, blind hole from top) | 4.2 mm |

The holes open at the seam face (Z = 50.0 mm in print frame, which is the open edge where the bottom shell mates). The pins enter from the bottom shell side.

### 3.12 Release Plate Guide Ribs

Two guide ribs molded into the top shell side walls. The release plate's edge channels ride on these ribs, constraining the plate to pure axial (Y-direction) translation.

| Rib | Wall | X position | Y extent | Z extent | Cross-section |
|-----|------|-----------|----------|----------|---------------|
| Left guide rib | Left interior | X = 3.0 to X = 5.0 (2.0 mm protrusion) | Y = 18.0 to Y = 50.0 | Z = 20.0 to Z = 30.0 (10.0 mm tall) | Rectangular, 2.0 mm wide (X) x 10.0 mm tall (Z) |
| Right guide rib | Right interior | X = 152.0 to X = 150.0 (2.0 mm protrusion) | Y = 18.0 to Y = 50.0 | Z = 20.0 to Z = 30.0 | Mirror of left |

The release plate has matching 2.4 mm wide channels (0.2 mm clearance per side for sliding fit) cut into its left and right edges.

### 3.13 Palm Surface Inset

The palm-contact area on the front face is inset 1.5 mm from the surrounding shell surface, per concept Section 4.

| Parameter | Value in print frame |
|-----------|---------------------|
| Inset region X extent | X = 45.0 to X = 110.0 (65.0 mm wide, centered) |
| Inset region Z extent | Z = 0 to Z = 0 (this is the palm face -- the inset is on the front wall's outer surface) |
| Inset depth | 1.5 mm (into the front wall in the -Y direction, creating a shallow recess) |
| Inset Y position on front wall exterior | The front wall exterior face is at Y = 0. The inset recess floor is at Y = 1.5 mm. |
| Inset height (Z on front wall) | From Z = 3.0 mm to Z = 48.0 mm (45.0 mm tall) |
| Corner radii | 1.0 mm fillet at all inset-to-surface transitions |

---

## 4. Interface Positions

### 4.1 Top Shell to Bottom Shell

**Seam line:** The shell split runs at Z = 50.0 mm in the print frame (the open top edge of the top shell as printed). This corresponds to the installed mid-height of the cartridge.

| Interface feature | Top shell side | Bottom shell side |
|------------------|---------------|-------------------|
| Seam plane | Z = 50.0 mm, full XY perimeter | Z = 0 on bottom shell (its build-plate face), full XY perimeter |
| Seam gap target | 0.3 mm maximum | Set by alignment pin registration |
| Seam chamfer | 0.15 mm x 45 deg on external edge at Z = 50.0 | 0.15 mm x 45 deg on external edge at Z = 0 |
| Snap-fit ledges (x4) | Ledges at SL1-SL4 (see Section 3.10) | Hooks on bottom shell engage from below (installed: from above in print frame) |
| Alignment pin holes (x2) | 4.2 mm holes at AH1, AH2 (see Section 3.11) | 4.0 mm pins at matching positions, 5.0 mm tall |

**Elephant's foot chamfer:** 0.3 mm x 45 deg chamfer on the top shell at Z = 0 (build-plate face, external perimeter edge). This prevents interference at the seam from first-layer flare.

### 4.2 Top Shell to Release Plate

| Interface feature | Top shell side | Release plate side |
|------------------|---------------|-------------------|
| Guide ribs | Two ribs: 2.0 mm wide x 10.0 mm tall, protruding from side walls (see Section 3.12) | 2.4 mm wide channels in plate left/right edges, 10.0 mm tall, 0.2 mm clearance/side |
| Release plate travel zone | Y = 32.0 to Y = 50.0 (plate slides 3-4 mm in this range; at rest ~Y=35-38, depressed ~Y=38-42) | Plate thickness 3.0 mm, translates in +Y direction |
| Over-center detent | Cantilever arm at Y=33.0, bump at X=6.5, Z=25.0 (see Section 3.8) | Matching groove on plate left edge, 1.5 mm wide x 0.8 mm deep |
| Spring contact | Spring pockets at Y=6-18 (springs push plate rearward) | Plate front face contacts spring ends |
| Through-holes in plate | (Not a top shell feature -- plate has 4x 7.2 mm holes aligned with QC fitting pattern) | Aligned with QC1-QC4 X, Z positions |

### 4.3 Top Shell to Lever Arms

| Interface feature | Top shell side | Lever arm side |
|------------------|---------------|----------------|
| Pivot bosses | Two bosses: 8.0 mm OD, 3.0 mm bore (press-fit for pin), at left (7.0, 20.0, 15.0) and right (148.0, 20.0, 15.0) | 3.2 mm bore in lever (0.1 mm clearance/side, rotates freely on 3.0 mm pin) |
| Pin capture | Pin extends from boss bore through lever to blind pocket on opposite side of boss. Bottom shell closing captures pin axially. | Lever arm ~8 mm wide x 4 mm thick, centered on pin |
| Lever short arm tip | (Space at Y=24-25 for short arm to contact release plate) | Short arm 4-5 mm from pivot toward release plate |
| Lever long arm tip | (Space at Y=0-5 for long arm to reach finger bar connection zone) | Long arm 20-25 mm from pivot toward front |

### 4.4 Top Shell to Finger Bar

The finger bar does not directly interface with the top shell. It connects to the lever arm tips and protrudes through a slot in the bottom shell. The top shell provides clearance:

| Interface feature | Top shell side | Finger bar side |
|------------------|---------------|-----------------|
| No direct contact | Front wall interior provides clearance at Y = 0-6 mm, Z = 38-50 mm for finger bar travel zone | Finger bar ~65 mm wide x 13 mm deep x 4 mm thick, located in bottom shell slot |

### 4.5 Top Shell to Quick Connect Fittings

| Interface feature | Top shell side | Fitting side |
|------------------|---------------|-------------|
| Bulkhead mounting holes (x4) | 17.2 mm holes at QC1-QC4 in rear bulkhead (Y=155-158, see Section 3.5) | PP1208W body passes through; internal nut clamps both sides of 3.0 mm thick bulkhead |
| Fitting body clearance zone | Y = 158.0 to Y = 168.0 (10.0 mm between bulkhead and outer rear wall) | Fitting body extends ~15 mm rearward from bulkhead front face; clamped within the 10 mm zone |
| Rear wall tube entry holes (x4) | 7.5 mm holes at TE1-TE4 in outer rear wall (Y=168-170, see Section 3.5) | Tube stubs from dock enter through these holes to reach fitting collets |

### 4.6 Top Shell to Pumps

| Interface feature | Top shell side | Pump side |
|------------------|---------------|-----------|
| Mounting shelf face | Flat surface at Z = 34.0, X = 3-152, Y = 80-155 | Pump bracket face (flat, ~68.6 mm wide) sits on shelf |
| Motor bores (x2) | 36.4 mm diameter holes at (40.5, 81.5) and (114.5, 81.5) | 35.0 mm motor cylinder passes through with ~0.7 mm clearance/side |
| Screw holes (x8) | 3.4 mm through-holes at P1-H1 through P2-H4 (see Section 3.4) | M3 screws pass through bracket holes (3.13 mm), through shelf, secured with lock nuts on motor side (below shelf in print frame) |
| Motor clearance zone | Z = 1.5 to Z = 31.0 (below shelf in print frame = behind shelf when installed), Y = 83 to 155 | Motor bodies 35 mm dia x 63 mm long + 5 mm nub, extending rearward from bracket |
| Pump head clearance zone | Z = 34.0 to Z = 50.0 (above shelf in print frame = forward of shelf when installed), Y = 50 to 80 | Pump heads 62.6 x 62.6 mm cross-section, ~48 mm deep, plus tube connector stubs |

### 4.7 Top Shell to Dock Cradle

| Interface feature | Top shell side | Dock cradle side |
|------------------|---------------|-----------------|
| T-slot rail grooves (x2) | Upper T-groove halves on left and right walls (see Section 3.9) | T-profile rails on dock, running front-to-rear. Rails engage the full T-slot (upper half from top shell + lower half from bottom shell). |
| Rail engagement direction | Groove runs Y = 0 to 170. Cartridge slides in +Y to seat. | Rails run front-to-rear matching groove length. Chamfered entries (2 mm x 30 deg) on dock rail fronts. |
| Asymmetric keying | Left groove center Z = 39.5 mm from palm surface. Right groove center Z = 39.5 mm from palm surface. Asymmetry is achieved by making the left dock rail 2 mm higher than the right (per concept). The groove geometry on the top shell is symmetric; the keying is a dock-side feature. | Left rail positioned 2 mm higher than right rail |

### 4.8 Top Shell to Springs

| Interface feature | Top shell side | Spring side |
|------------------|---------------|-------------|
| Spring pockets (x2) | Cylindrical pockets: 7.0 mm ID, 12 mm deep, at positions in Section 3.7 | ~5 mm OD x 10-15 mm free length compression springs seat into pockets; spring rear end sits against pocket floor (Y = 6.0), spring front end contacts release plate front face |
| Spring retention | Pocket walls constrain radial movement. Pocket floor prevents rearward escape. | Spring is not fastened; captured between pocket floor and release plate |

---

## 5. Transform Summary

### Part Frame to System Frame

The top shell prints inverted. To install:

```
Step 1: Rotate 180 degrees about the X axis (flip upside-down)
  Print frame Z-up becomes installed Z-down
  Print frame Y remains unchanged (front-to-rear)
  Print frame X remains unchanged (left-to-right)

Step 2: Translate to installed position in the enclosure
  The cartridge center X aligns with enclosure center X: offset = (220 - 155) / 2 = 32.5 mm
  The cartridge front face aligns with enclosure front: Y_offset = 0
  The cartridge bottom rests on enclosure floor: Z_offset = cartridge height = 75 mm (when both shells are combined)
```

**Full transform:**

```
System (X_s, Y_s, Z_s) = (X_p + 32.5, Y_p, -Z_p + 75.0)

Where:
  X_p, Y_p, Z_p = coordinates in top shell print frame
  X_s, Y_s, Z_s = coordinates in enclosure system frame
  System origin = front-left-bottom corner of enclosure interior
```

Note: The 75.0 mm in the Z transform is the full cartridge height (top shell 50 mm + bottom shell ~25 mm seam-to-bottom). When only considering the top shell: Z_s = -Z_p + 75.0 maps print-frame Z=0 (palm surface) to system Z=75.0 (top of cartridge), and print-frame Z=50 (seam) to system Z=25.0 (cartridge mid-height).

### Verification Points

**Point 1: Origin**
- Print frame: (0, 0, 0) -- lower-left-front corner, palm surface
- System frame: (0 + 32.5, 0, -0 + 75.0) = (32.5, 0, 75.0)
- Check: Front-left corner of cartridge top face, at the front of the enclosure, 75 mm above floor. Correct -- the cartridge is 155 mm wide starting at X_s=32.5, and its top (palm) surface is at Z_s=75.0.

**Point 2: Pump 1 motor bore center**
- Print frame: (40.5, 81.5, 34.0)
- System frame: (40.5 + 32.5, 81.5, -34.0 + 75.0) = (73.0, 81.5, 41.0)
- Check: Left pump center at 73 mm from left enclosure wall (roughly centered left-of-center in 220 mm enclosure), 81.5 mm from front, 41 mm above floor. The pump mounting shelf is at mid-height of the cartridge interior. Correct.

**Point 3: Rear bulkhead fitting QC4**
- Print frame: (128.5, 155.0, 39.75)
- System frame: (128.5 + 32.5, 155.0, -39.75 + 75.0) = (161.0, 155.0, 35.25)
- Check: Right pump outlet fitting, at 161 mm from left wall (right side of cartridge in the 220 mm enclosure), 155 mm from front, 35.25 mm above floor. This is in the rear portion of the cartridge, at a height between the floor and mid-height. Correct.

**Inverse verification (System to Print):**
```
X_p = X_s - 32.5
Y_p = Y_s
Z_p = -(Z_s - 75.0) = 75.0 - Z_s
```

Point 3 inverse: X_p = 161.0 - 32.5 = 128.5, Y_p = 155.0, Z_p = 75.0 - 35.25 = 39.75. Matches original. Round-trip verified.

---

## Appendix: Coordinate Summary Table

All positions in the top shell print frame for quick reference.

| Feature | X (mm) | Y (mm) | Z (mm) | Size / Notes |
|---------|--------|--------|--------|-------------|
| **Outer envelope** | 0-155 | 0-170 | 0-50 | Bounding box |
| **Palm surface** | 0-155 | 0-170 | 0-1.5 | Build-plate face, smooth |
| **Front wall** | 0-155 | 0-3.0 | 0-50 | 3.0 mm thick |
| **Rear wall** | 0-155 | 168-170 | 0-50 | 2.0 mm thick |
| **Left wall** | 0-3.0 | 0-170 | 0-50 | 3.0 mm thick |
| **Right wall** | 152-155 | 0-170 | 0-50 | 3.0 mm thick |
| **Rear bulkhead** | 3-152 | 155-158 | 1.5-50 | 3.0 mm thick |
| **Pump shelf** | 3-152 | 80-155 | 31-34 | 3.0 mm thick |
| **Pump 1 bore** | ctr 40.5 | ctr 81.5 | at Z=34 | 36.4 mm dia |
| **Pump 2 bore** | ctr 114.5 | ctr 81.5 | at Z=34 | 36.4 mm dia |
| **P1-H1** | 16.5 | 57.5 | 34 | 3.4 mm dia |
| **P1-H2** | 64.5 | 57.5 | 34 | 3.4 mm dia |
| **P1-H3** | 16.5 | 105.5 | 34 | 3.4 mm dia |
| **P1-H4** | 64.5 | 105.5 | 34 | 3.4 mm dia |
| **P2-H1** | 90.5 | 57.5 | 34 | 3.4 mm dia |
| **P2-H2** | 138.5 | 57.5 | 34 | 3.4 mm dia |
| **P2-H3** | 90.5 | 105.5 | 34 | 3.4 mm dia |
| **P2-H4** | 138.5 | 105.5 | 34 | 3.4 mm dia |
| **QC1** | 26.5 | 155 | 11.75 | 17.2 mm dia |
| **QC2** | 54.5 | 155 | 39.75 | 17.2 mm dia |
| **QC3** | 100.5 | 155 | 11.75 | 17.2 mm dia |
| **QC4** | 128.5 | 155 | 39.75 | 17.2 mm dia |
| **TE1-TE4** | same X,Z as QC | 169 | same Z | 7.5 mm dia |
| **Left pivot boss** | ctr 7.0 | 20.0 | 15.0 | 8 mm OD, 3.0 mm bore |
| **Right pivot boss** | ctr 148.0 | 20.0 | 15.0 | 8 mm OD, 3.0 mm bore |
| **Left spring pocket** | ctr 40.0 | 6-18 | 25.0 | 7.0 mm ID, 12 mm deep |
| **Right spring pocket** | ctr 115.0 | 6-18 | 25.0 | 7.0 mm ID, 12 mm deep |
| **Detent arm tip** | 6.5 | 33.0 | 25.0 | 1.5 mm bump |
| **SL1** | 3-5 | 30.0 | 44.0 | 10x2x2 mm ledge |
| **SL2** | 3-5 | 140.0 | 44.0 | 10x2x2 mm ledge |
| **SL3** | 150-152 | 30.0 | 44.0 | 10x2x2 mm ledge |
| **SL4** | 150-152 | 140.0 | 44.0 | 10x2x2 mm ledge |
| **AH1** | 20.0 | 85.0 | 44-50 | 4.2 mm dia, 6 mm deep |
| **AH2** | 135.0 | 85.0 | 44-50 | 4.2 mm dia, 6 mm deep |
| **Left guide rib** | 3-5 | 18-50 | 20-30 | 2.0 mm wide x 10 mm tall |
| **Right guide rib** | 150-152 | 18-50 | 20-30 | 2.0 mm wide x 10 mm tall |
| **Left T-groove neck** | 0-2.0 | 0-170 | 38-41 | 2.0 mm wide x 3.0 mm tall |
| **Left T-groove undercut** | 0-5.0 | 0-170 | 41-42.5 | 5.0 mm wide x 1.5 mm tall |
| **Right T-groove neck** | 153-155 | 0-170 | 38-41 | 2.0 mm wide x 3.0 mm tall |
| **Right T-groove undercut** | 150-155 | 0-170 | 41-42.5 | 5.0 mm wide x 1.5 mm tall |
| **Palm inset** | 45-110 | at Y=0 face | 3-48 | 1.5 mm deep recess, 65x45 mm |
