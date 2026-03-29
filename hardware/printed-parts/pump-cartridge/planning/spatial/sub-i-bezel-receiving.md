# Spatial Resolution: Sub-I Front Bezel Receiving Features

## 1. System-Level Placement

```
Mechanism: Front Bezel Receiving Features (Sub-I)
Parent: Tray box shell (Sub-A), front open edge
Position: Y = 155 face (the open front end of the tray, facing the user)
Orientation: features face the user along the +Y axis
```

The front bezel attaches at Y = 155, the open end of the tray opposite the rear/dock wall (Y = 0). The bezel overlaps the tray's front edge perimeter by 1.5 mm, creating a shadow-line seam. Sub-I consists of (a) a step-lap ledge rabbet around the perimeter of the Y = 155 face, and (b) snap tab pockets recessed into the tray's front edges where the bezel's snap tabs engage.

---

## 2. Part Reference Frame

```
Part: Tray (Sub-I features applied to the Sub-A box shell)
  Origin: rear-left-bottom corner (dock side)
  X: width, 0..160 mm (left to right when facing the front)
  Y: depth, 0..155 mm (0 = rear/dock, 155 = front/user)
  Z: height, 0..72 mm (0 = floor bottom, 72 = top of side walls)
  Print orientation: open top facing up, XY plane on build plate
  Installed orientation: identical (identity transform)
```

Sub-I features are cuts applied to the existing box shell (Sub-A). All coordinates are in the tray frame defined by Sub-A.

---

## 3. Derived Geometry

No cross-frame transforms are required. The tray is level (identity transform to system frame), and all bezel-receiving features lie at the Y = 155 face. The geometry below is resolved entirely in the tray's own coordinate frame.

### 3a. Front Edge Perimeter — Wall Cross-Sections at Y = 155

Before any Sub-I cuts, the tray's open front face at Y = 155 exposes the following solid cross-sections (from Sub-A):

| Segment | X range | Z range | Notes |
|---------|---------|---------|-------|
| Left wall | 0..5 | 0..72 | 5 mm wide, full height |
| Right wall | 155..160 | 0..72 | 5 mm wide, full height |
| Floor | 5..155 | 0..3 | 150 mm wide, 3 mm tall |
| Top edge | (none — open top) | — | No ceiling; lid attaches separately |

The bezel must engage all three solid segments (left wall, right wall, floor) plus interface with the lid at the top edge. Sub-I provides receiving features on the tray side only.

### 3b. Step-Lap Ledge (Rabbet)

The step-lap creates a 1.5 mm deep rabbet on the exterior faces of the tray at the front edge. The bezel's inner face seats against this ledge, overlapping the tray by 1.5 mm in the Y direction. The rabbet produces the shadow-line seam described in the concept document.

**Rabbet geometry:** A 1.5 mm deep (in Y) x 1.5 mm wide (into the wall/floor thickness) step cut around the exterior perimeter of the Y = 155 face.

The rabbet runs along three segments:

| Rabbet segment | Location (tray frame) | Cut volume |
|----------------|----------------------|------------|
| Left wall rabbet | X = 0..1.5, Y = 153.5..155, Z = 0..72 | Removes 1.5 mm from exterior face of left wall at front end |
| Right wall rabbet | X = 158.5..160, Y = 153.5..155, Z = 0..72 | Removes 1.5 mm from exterior face of right wall at front end |
| Floor rabbet | X = 0..160, Y = 153.5..155, Z = 0..1.5 | Removes 1.5 mm from bottom face of floor at front end |

**Resulting ledge surfaces (where bezel inner face seats):**

| Ledge surface | Plane | Extent |
|---------------|-------|--------|
| Left wall ledge | X = 1.5 plane | Y = 153.5..155, Z = 0..72 |
| Right wall ledge | X = 158.5 plane | Y = 153.5..155, Z = 0..72 |
| Floor ledge | Z = 1.5 plane | X = 0..160, Y = 153.5..155 |

The bezel's inner perimeter sits on these ledge surfaces. The bezel extends from Y = 153.5 to Y = 155 + (bezel depth beyond tray face). The 1.5 mm overlap zone (Y = 153.5..155) is the shadow-line seam region.

**Corner treatment:** Where the left/right wall rabbets meet the floor rabbet (at the two bottom corners), the rabbet volumes intersect naturally, producing clean inside corners. A 1 mm fillet at these inside corners is recommended for printability and stress relief.

### 3c. Snap Tab Pockets

The bezel's snap tabs are small cantilevered hooks that deflect inward during assembly, then spring outward into pockets (detent recesses) cut into the tray's front edges. Each pocket is a rectangular recess that captures the bezel tab's barb.

**Pocket count and placement (from concept):**
- 2 per side wall = 4 on side walls
- 1 on floor front edge
- 1 on top edge (for lid-bezel interface — the tray provides the pocket, the lid provides the mating ridge, or vice versa; this pocket is on the tray's top edge to receive the bezel tab that also bridges to the lid)
- **Total: 6 pockets on the tray**

**Pocket dimensions (each pocket is identical):**
- Width (along the wall face, parallel to the pocket's host edge): 5 mm
- Height (perpendicular to the wall face, into the pocket depth): 1.5 mm
- Depth into the tray (in Y, away from the Y=155 face): 3 mm

**Individual pocket positions (tray frame coordinates):**

#### Left wall pockets (2 pockets)
Cut into the interior face of the left wall at the front edge. The pockets are recesses in the X = 5 plane, extending from X = 3.5 to X = 5 (1.5 mm deep into wall), spanning 3 mm in Y from Y = 152 to Y = 155.

| Pocket | Center (X, Y, Z) | Cut volume (tray frame) |
|--------|-------------------|------------------------|
| L1 (lower) | (4.25, 153.5, 22) | X = 3.5..5, Y = 152..155, Z = 19.5..24.5 |
| L2 (upper) | (4.25, 153.5, 50) | X = 3.5..5, Y = 152..155, Z = 47.5..52.5 |

#### Right wall pockets (2 pockets)
Cut into the interior face of the right wall. The pockets are recesses in the X = 155 plane, extending from X = 155 to X = 156.5 (1.5 mm deep into wall), spanning 3 mm in Y.

| Pocket | Center (X, Y, Z) | Cut volume (tray frame) |
|--------|-------------------|------------------------|
| R1 (lower) | (155.75, 153.5, 22) | X = 155..156.5, Y = 152..155, Z = 19.5..24.5 |
| R2 (upper) | (155.75, 153.5, 50) | X = 155..156.5, Y = 152..155, Z = 47.5..52.5 |

#### Floor pocket (1 pocket)
Cut into the top face of the floor at the front edge. The pocket is a recess in the Z = 3 plane, extending from Z = 1.5 to Z = 3 (1.5 mm deep into floor), spanning 3 mm in Y.

| Pocket | Center (X, Y, Z) | Cut volume (tray frame) |
|--------|-------------------|------------------------|
| F1 (center) | (80, 153.5, 2.25) | X = 77.5..82.5, Y = 152..155, Z = 1.5..3 |

#### Top edge pocket (1 pocket)
Cut into the top surface of a side wall at the front edge. This pocket engages the bezel's top tab. Located on the top edge of the left wall (the right wall could also work — left is chosen arbitrarily; symmetry means either works).

| Pocket | Center (X, Y, Z) | Cut volume (tray frame) |
|--------|-------------------|------------------------|
| T1 (top-center) | (80, 153.5, 71.25) | X = 77.5..82.5, Y = 152..155, Z = 70.5..72 |

Note: T1 is positioned at the center of the top edge span, cut downward into the wall top face by 1.5 mm. This engages a bezel tab that wraps over the top front edge of the tray. When the lid is installed, the lid's front edge sits adjacent and adds retention, but the pocket itself is in the tray.

### 3d. Interface Positions

#### Interface: Bezel snap tabs to tray pockets

Each tray pocket receives one bezel snap tab. The bezel tab is a cantilevered hook on the bezel's inner face that flexes during insertion (bezel pushed onto tray from the +Y direction, toward -Y) and latches into the pocket.

| Tray pocket | Pocket opening face | Bezel tab approach direction | Mating feature on bezel |
|-------------|--------------------|-----------------------------|------------------------|
| L1 | X = 5 plane (interior left wall) | Tab deflects in +X, springs back to -X into pocket | Left inner face tab, lower |
| L2 | X = 5 plane (interior left wall) | Tab deflects in +X, springs back to -X into pocket | Left inner face tab, upper |
| R1 | X = 155 plane (interior right wall) | Tab deflects in -X, springs back to +X into pocket | Right inner face tab, lower |
| R2 | X = 155 plane (interior right wall) | Tab deflects in -X, springs back to +X into pocket | Right inner face tab, upper |
| F1 | Z = 3 plane (interior floor top) | Tab deflects in +Z, springs back to -Z into pocket | Bottom edge tab, center |
| T1 | Z = 72 plane (top edge) | Tab deflects in -Z, springs back to +Z into pocket | Top edge tab, center |

#### Interface: Bezel step-lap overlap to tray rabbet

The bezel's inner perimeter seats against the rabbet ledge surfaces (Section 3b). The bezel's inner face contacts:

| Bezel inner face | Mates with tray ledge surface | Contact plane |
|-----------------|------------------------------|---------------|
| Left inner face | X = 1.5 plane | Y = 153.5..155, Z = 0..72 |
| Right inner face | X = 158.5 plane | Y = 153.5..155, Z = 0..72 |
| Bottom inner face | Z = 1.5 plane | X = 0..160, Y = 153.5..155 |

The bezel's outer face is flush with (or marginally proud of) the tray's outer surfaces:
- Left: bezel outer face at X = 0 (flush with tray left wall exterior)
- Right: bezel outer face at X = 160 (flush with tray right wall exterior)
- Bottom: bezel outer face at Z = 0 (flush with tray floor bottom)

#### Interface: Bezel to lid at top edge

The bezel's top edge meets the lid's front edge at Y = 155, Z = 72. The lid (Sub-H provides its snap ridges on the side walls) sits on the tray's top edges. The bezel's top edge butts against or slightly overlaps the lid's front edge. This interface is defined by the lid and bezel specifications — the tray's contribution is the T1 pocket and the rabbet, which stop at Z = 72.

#### Interface: Bezel finger channels and linkage pull tabs

The bezel has finger channels (vertical slots, ~25 mm deep x 15 mm wide) on its left and right edges. These channels expose the pull-tab paddles connected to the linkage rods (Sub-G). The tray's Sub-I features do not directly interact with the finger channels — the channels are entirely within the bezel's geometry. However, the snap tab pockets L1/L2 and R1/R2 must not intrude into the finger channel zone. The finger channels are centered vertically on the bezel (~Z = 22..47 approximate). The pocket positions (L1 at Z = 19.5..24.5 and L2 at Z = 47.5..52.5) are placed at the edges of the finger channel zone, outside the channel opening, to avoid interference.

---

## 4. Transform Summary

```
Part frame = Tray frame (identity transform)

Sub-I features are cuts applied to the Sub-A box shell at the Y = 155 end.
No rotation. No translation offset.

Part-local (0, 0, 0) = tray origin (rear-left-bottom) = dock-side corner
Part-local Y = 155 = front/user side (open end, where bezel attaches)
```

### Verification

- Part-local (0, 155, 0) = front-left-bottom corner of tray = left end of floor rabbet start
- Part-local (160, 155, 72) = front-right-top corner of tray = right end of top edge
- Part-local (80, 153.5, 36) = center of front face, 1.5 mm behind the Y = 155 edge = center of rabbet ledge zone

All correct by identity transform.

### Dimensional cross-checks

- Rabbet depth (1.5 mm in Y) + remaining wall at front = 1.5 mm rabbet leaves 3.5 mm of side wall thickness at the front edge (from the original 5 mm wall). Adequate structural integrity.
- Floor rabbet (1.5 mm in Z) leaves 1.5 mm of floor thickness at the front edge (from the original 3 mm floor). Thin but acceptable — the bezel provides structural reinforcement once installed.
- Snap tab pocket depth into wall (1.5 mm in X or Z) leaves 3.5 mm remaining wall (side walls) or 1.5 mm remaining floor. Pockets do not penetrate through any wall.
- Pocket Y extent (Y = 152..155, 3 mm) is within the rabbet zone (Y = 153.5..155) and extends 1.5 mm further into the tray body. This is correct — the tab barb catches behind the rabbet step.
