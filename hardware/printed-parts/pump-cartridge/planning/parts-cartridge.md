# Pump Cartridge -- Parts Specification

Five printed PETG parts forming the removable pump cartridge module. The cartridge holds two Kamoer KPHM400 peristaltic pumps, makes 4 fluid connections (John Guest PP0408W fittings) and 4 electrical contacts at the rear face, and locks via a flip-down lever whose cam lobes drive a release plate for collet disengagement.

All dimensions in millimeters. All positions reference the part's own coordinate frame unless explicitly stated otherwise. The spatial resolution document is the authoritative source for every interface position used here.

---

## Mechanism Narrative

### What the user sees and touches

When the cartridge is docked, the user sees a rectangular face at the bottom-front of the enclosure. From outside in: the dock face frame (part of the enclosure), a 1 mm uniform reveal gap, the front bezel (cartridge identity surface), and centered within it the lever paddle. The lever paddle sits 0.5 mm recessed behind the bezel's cutout rebate (0.5 mm step-in around the cutout perimeter, X = 10 to 130, Z = 18 to 58 in bezel frame), creating a shadow line rather than a flush butt joint. When locked, the paddle face is flush with the bezel minus that 0.5 mm recess. The lever paddle is the only interactive element.

The user's hand contacts the lever paddle (120 mm wide, 40 mm tall, 4 mm thick at the pivot end). The grip edge at the bottom of the paddle (lever frame Z = -20, corresponding to tray Z = 18 when locked) has a 3 mm fillet radius for a comfortable finger hook. During insertion/removal, the user also contacts the tray side walls, which are smooth with no exposed fasteners or sharp edges. The rail ribs (on the outer faces of the tray walls) are captured inside the dock's C-channel grooves and never touched.

### What moves

**During lever operation (lock/unlock):**
1. **Lever** -- rotates 90 degrees about the pivot axis (tray Y = 9.0, Z = 58.0, parallel to X axis). The pivot stubs (6.0 mm diameter) rotate in bearing holes (6.1 mm diameter, 0.1 mm diametral clearance) in the tray side walls.
2. **Two push/pull rods** -- translate 3.0 mm along the tray Y axis. Each rod runs in a channel molded into a tray side wall interior face, from the cam contact zone (Y ~ 6 to 9) to the rear wall (Y = 121). The rods pass through 5.0 mm x 5.0 mm transfer slots in the rear wall.
3. **Release plate** -- translates 3.0 mm along the tray Y axis (in the -Y direction, toward the fittings, when unlocking). The plate rides on two guide posts (4.0 mm diameter) via edge slots (4.3 mm wide, 0.3 mm clearance).

**Stationary during operation:**
- Cartridge tray (structural backbone)
- Cartridge lid (pump retention)
- Front bezel (cosmetic frame)
- John Guest fittings (press-fit in rear wall bores)
- Pumps (bolted to tray floor)

**During cartridge insertion/removal:**
- The entire cartridge assembly translates along the tray Y axis (= dock insertion axis) on C-channel rails.

### What converts the motion

The lever's rotation is converted to linear plate travel by a cam-and-rod linkage:

1. **Cam lobes** (two eccentric discs, one on each end of the lever, 8.0 mm radius, 3.0 mm eccentric offset from pivot axis, 4.0 mm thick) convert lever rotation into Y-axis displacement at the rod contact point.
2. **Push/pull rods** (rigid rods, one per side, running along tray interior walls at X = 7.0 and X = 133.0, Z = 58.0) transmit the 3.0 mm Y-axis displacement from the cam contact zone near the front to the release plate transfer tabs beyond the rear wall.
3. **Release plate transfer tabs** receive the rod force and translate the plate along its guide posts.

When the lever rotates from locked to unlocked, the cam eccentricity shifts from the -Z direction (downward) to the -Y direction (toward user). This pulls the rod front ends 3.0 mm in the -Y direction. The rod rear ends also shift 3.0 mm in -Y, pulling the release plate 3.0 mm in the -Y direction (toward the fittings). The plate's stepped bores then engage and compress all 4 collets simultaneously.

### What constrains each moving part

**Lever:** Constrained to pure rotation about the X-parallel pivot axis by the two pivot stub / bearing hole interfaces (left bearing at tray X = 2.5, right at X = 137.5, both at Y = 9.0, Z = 58.0). Axial translation along X is prevented by the lever body contacting the tray inner side walls. The lever is captive once the lid is installed (lid covers the top of the pivot area).

**Push/pull rods:** Constrained to Y-axis translation by channels in the tray side wall interior faces. Each channel is a U-groove running from Y ~ 6 to Y = 112.5 (rear wall inner face) at the rod's X and Z position. The channel prevents X and Z motion. The rods pass through the 5.0 mm x 5.0 mm transfer slots in the rear wall to reach the plate.

**Release plate:** Constrained to Y-axis translation by two guide posts (left at tray X = 8.0, right at X = 132.0, both at Z = 34.8). Edge slots in the plate (4.3 mm wide for 4.0 mm posts, 0.3 mm clearance) prevent X and Z motion while allowing free Y travel. The plate is captive between the tray rear wall outboard face (Y = 121.0) and the guide post tips (tray Y = 143.0).

### What provides the return force

**Lever detent:** Two V-notches in the front bezel inner face (bezel X = 70, Y = 5, Z = 18 for locked; Z = 58 for unlocked) receive a printed cantilever spring tab on the lever's paddle edge. Notch geometry: 2.0 mm wide, 0.5 mm deep, 45-degree walls. The cantilever tab is 12 mm long, 2 mm wide, 1.5 mm thick PETG -- well within elastic deflection limits for 0.5 mm detent depth. This produces the audible/tactile click at both positions.

**Release plate return:** When the lever moves from unlocked to locked, the cam pulls the rods in the +Y direction (toward rear), which pulls the plate in the +Y direction (away from fittings) via the rod-to-tab connection. The plate does not rely on springs or gravity -- it is positively driven in both directions by the cam linkage.

### What is the user's physical interaction

**To dock the cartridge:**
1. User grips the cartridge by the lever paddle (natural handle). Cartridge weighs ~400-500 g.
2. User aligns cartridge with the dock opening. The dock face frame has 5 mm deep entry chamfers at 30 degrees on all four inner edges, providing a 2.9 mm capture radius per side.
3. User slides the cartridge in on the C-channel rails. The tray's rectangular rail ribs (2.0 mm protrusion, 20 mm tall, full depth) engage the dock's C-channel grooves (2.6 mm wide for 2.0 mm rib, 0.3 mm clearance per side) within the first 10 mm of travel.
4. At ~105 mm insertion, the two registration bosses on the dock rear wall (25 mm long, 10 mm base diameter, 7 mm tip diameter) enter the tapered sockets in the tray rear wall (socket A at tray X = 21.5, Z = 9.8; socket B at X = 118.5, Z = 59.8; both 15 mm deep, 10.3 mm mouth, 7.3 mm base). Bosses protrude 5 mm farther than tube stubs, so they engage and align the cartridge before any tube contacts a fitting.
5. At ~110 mm insertion, the 4 chamfered tube stubs (6.35 mm OD, 1.5 mm x 45-degree chamfer, effective tip ~3.35 mm) enter the entry funnels around each fitting bore (12.0 mm mouth at 8 mm depth, 9.5 mm exit, 9-degree half-angle taper). Tactile resistance increases as tubes push past collets and O-rings.
6. At full insertion (~121 mm), the cartridge front face is flush with the dock opening.
7. User flips the lever down 90 degrees. The cam lobes pull the cartridge body 3 mm rearward, fully seating tube stubs in fittings and pressing electrical contacts together. Detent clicks at the locked position (bezel V-notch at Z = 18).

**To remove the cartridge:**
1. User hooks a finger under the lever grip edge (3 mm fillet at tray Z = 18) and rotates the lever 90 degrees upward. The cam shifts the push/pull rods 3 mm in -Y, pulling the release plate 3 mm toward the fittings. The plate's stepped bores compress all 4 collets 1.5 mm inward (exceeding the 1.3 mm needed for full release). Detent clicks at the unlocked position (bezel V-notch at Z = 58).
2. User pulls the cartridge straight out by the lever (which now serves as a handle). The released fittings slide cleanly off the tube stubs. Rails guide the cartridge out smoothly.

---

## Part 1: Cartridge Tray

### Coordinate System

```
Origin: outer lower-left corner of the FRONT face (user-facing)
X: width, left to right, 0..140
Y: depth, front face toward rear wall, 0..121
Z: height, bottom to top, 0..70
Print orientation: rear wall (Y=121) down on build plate; front opening (Y=0) faces up
```

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width) | 140.0 mm (144.0 mm including rail ribs) |
| Y extent (depth) | 121.0 mm |
| Z extent (height) | 70.0 mm |
| Wall thickness (sides) | 5.0 mm |
| Wall thickness (rear) | 8.5 mm (Y = 112.5 to Y = 121.0) |
| Floor thickness | 3.0 mm |
| Material | PETG |
| Print orientation | Rear wall down (Y = 121 on build plate) |
| Supports needed | No |

### Tray Floor

Flat plate at Z = 0.0 (outer) to Z = 3.0 (inner surface). The floor spans the full tray interior from X = 5.0 to X = 135.0 and Y = 0.0 to Y = 112.5.

### Side Walls

Two vertical walls, each 5.0 mm thick, running the full depth and height:
- Left wall: X = 0.0 to X = 5.0, Y = 0.0 to Y = 112.5, Z = 0.0 to Z = 70.0
- Right wall: X = 135.0 to X = 140.0, Y = 0.0 to Y = 112.5, Z = 0.0 to Z = 70.0

The front face (Y = 0) is open (no wall). The front bezel press-fits into this opening.

### Rear Wall

Integral to the tray. A solid wall spanning the full width and height:
- Y extent: 112.5 (inner face) to 121.0 (outboard face), 8.5 mm thick
- X extent: 0.0 to 140.0
- Z extent: 0.0 to 70.0

The rear wall contains all rear-face interfaces: fitting bores, guide post bosses, registration boss sockets, electrical contact pad pockets, push rod transfer slots, and motor nub pockets.

### Pump Pockets

Two open-top rectangular pockets in the tray floor, sized to accept the Kamoer KPHM400 pump heads (62.6 mm square cross-section, 48 mm deep from front face to mounting bracket).

| Parameter | Pump 1 (left) | Pump 2 (right) |
|-----------|--------------|----------------|
| Pocket X range | 5.2 to 67.8 | 72.2 to 134.8 |
| Pocket Y range | 0.6 to 48.6 | 0.6 to 48.6 |
| Pocket Z range | 3.5 to 66.1 (inner) | 3.5 to 66.1 (inner) |
| Pump X center | 36.5 | 103.5 |
| Pump Z center | 34.8 | 34.8 |
| Clearance above inner floor | 0.5 mm | 0.5 mm |
| Clearance below lid | 3.9 mm | 3.9 mm |
| Center gap between pumps | 4.4 mm (67.8 to 72.2) | -- |

The pump head front face sits 0.6 mm behind the tray front opening (Y = 0). The motor bodies extend rearward from the pump bracket plane (Y = 48.6) through the tray interior toward the rear wall. Motor end caps reach Y = 111.0 with 1.5 mm clearance to the rear wall inner face (Y = 112.5).

### Motor Nub Pockets

Two circular pockets in the rear wall inner face, centered on each pump X center, to clear the 5 mm motor shaft nub:

| Pocket | X center | Y range | Z center | Diameter |
|--------|----------|---------|----------|----------|
| Left | 36.5 | 112.5 to 117.5 | 34.8 | 8.0 |
| Right | 103.5 | 112.5 to 117.5 | 34.8 | 8.0 |

Pockets are 5.0 mm deep into the 8.5 mm wall, leaving 3.5 mm of wall material behind each pocket.

### Pump Mounting Holes (Heat-Set Insert Bosses)

Four mounting holes total (two per pump), positioned at the bracket plane (Y = 48.6) at pump Z center (Z = 34.8). Each boss is a cylindrical protrusion rising from the tray inner floor.

| Hole ID | X | Y | Z | Boss OD | Boss height (Z) | Insert hole diameter |
|---------|------|------|------|---------|-----------------|---------------------|
| P1-L | 11.8 | 48.6 | 34.8 | 7.0 | 5.0 | 4.0 (M3 heat-set) |
| P1-R | 61.2 | 48.6 | 34.8 | 7.0 | 5.0 | 4.0 |
| P2-L | 78.8 | 48.6 | 34.8 | 7.0 | 5.0 | 4.0 |
| P2-R | 128.2 | 48.6 | 34.8 | 7.0 | 5.0 | 4.0 |

Heat-set insert: M3, installed from the +Z direction with a soldering iron at 230 C. Boss grows upward from the inner floor surface (Z = 3.0 to Z = 8.0). The mounting bracket sits at Z = 34.8 (pump center height); the screws pass through the bracket holes (3.13 mm diameter) and thread into the heat-set inserts in the bosses. The bosses are located on the tray floor at each mounting hole X position, with a vertical support rib connecting the boss top to the bracket Z height. Screws: M3 x 8 mm SHCS.

**DESIGN GAP:** The mounting bosses are at floor level (Z = 3.0 to 8.0) but the bracket mounting holes are at Z = 34.8. A vertical standoff or rib structure is needed to bridge this 26.8 mm gap. The spatial resolution document specifies hole positions but does not detail the standoff geometry. The standoff should be a 7.0 mm wide rib running from the floor boss to the bracket plane, integral to the tray floor/wall structure.

### John Guest Fitting Bores

Four through-bores in the rear wall, sized for press-fit of the JG PP0408W center body (9.31 mm OD):

| Fitting | X | Z | Bore diameter | Bore Y range |
|---------|------|------|---------------|-------------|
| F1 (Pump 1 outlet) | 36.5 | 49.8 | 9.5 | 112.5 to 121.0 |
| F2 (Pump 1 inlet) | 36.5 | 19.8 | 9.5 | 112.5 to 121.0 |
| F3 (Pump 2 outlet) | 103.5 | 49.8 | 9.5 | 112.5 to 121.0 |
| F4 (Pump 2 inlet) | 103.5 | 19.8 | 9.5 | 112.5 to 121.0 |

Bore diameter is 9.5 mm for the 9.31 mm center body, giving 0.1 mm radial clearance (light press-fit, allows self-centering on tube stubs). The 15.10 mm body end shoulders seat against the wall faces on both sides, providing axial retention without adhesive.

### Entry Funnels (Rear Wall Outboard Face)

Conical funnels printed into the rear wall outboard face around each fitting bore, guiding dock tube stubs into the collet bores:

| Parameter | Value |
|-----------|-------|
| Funnel mouth diameter | 12.0 mm |
| Funnel exit diameter | 9.5 mm (matches bore) |
| Funnel depth | 8.0 mm (from Y = 121.0 to Y = 129.0) |
| Taper half-angle | 9 degrees |
| Number of funnels | 4 (one per fitting) |

### Registration Boss Sockets

Two tapered sockets in the rear wall outboard face, receiving the dock's alignment bosses:

| Socket | X | Z | Y range (mouth to base) | Mouth diameter | Base diameter | Depth |
|--------|------|------|------------------------|----------------|---------------|-------|
| A | 21.5 | 9.8 | 121.0 to 106.0 | 10.3 | 7.3 | 15.0 |
| B | 118.5 | 59.8 | 121.0 to 106.0 | 10.3 | 7.3 | 15.0 |

Sockets are 0.3 mm oversize relative to bosses (10.3 mm for 10.0 mm boss base), with matching taper.

### Electrical Contact Pad Pockets

Four shallow rectangular pockets on the rear wall outboard face for adhesive copper foil tape pads:

| Pad | X center | Z center | Width (X) | Height (Z) | Pocket depth | Y position |
|-----|----------|----------|-----------|------------|-------------|-----------|
| E1 (Motor A+) | 58.0 | 34.8 | 10.0 | 5.0 | 0.1 | 121.0 (outboard face) |
| E2 (Motor A-) | 70.0 | 34.8 | 10.0 | 5.0 | 0.1 | 121.0 |
| E3 (Motor B+) | 82.0 | 34.8 | 10.0 | 5.0 | 0.1 | 121.0 |
| E4 (Motor B-) | 94.0 | 34.8 | 10.0 | 5.0 | 0.1 | 121.0 |

Pads are centered at fitting pattern center height (Z = 34.8), in a row between the two pump fitting columns (X = 53 to X = 99). Copper tape sits flush with the wall surface when installed in the 0.1 mm recessed pocket.

### Guide Posts for Release Plate

Two cylindrical posts protruding from the rear wall outboard face in the +Y direction:

| Post | X | Z | Y base | Y tip | Diameter | Length |
|------|-----|------|--------|-------|----------|--------|
| Left | 8.0 | 34.8 | 121.0 | 143.0 | 4.0 | 22.0 |
| Right | 132.0 | 34.8 | 121.0 | 143.0 | 4.0 | 22.0 |

Posts extend 22 mm outboard, past the release plate's maximum extent (Y = 139.0 at rest) with 4 mm margin. Posts are integral to the rear wall.

### Push Rod Transfer Slots

Two rectangular through-slots in the rear wall, allowing the push/pull rods to pass from tray interior to release plate:

| Slot | X center | Z center | Width (X) | Height (Z) | Y range |
|------|----------|----------|-----------|------------|---------|
| Left | 7.0 | 58.0 | 5.0 | 5.0 | 112.5 to 121.0 |
| Right | 133.0 | 58.0 | 5.0 | 5.0 | 112.5 to 121.0 |

### Push Rod Channels

Two U-groove channels molded into the tray side wall interior faces, guiding the push/pull rods:

| Channel | X range | Z range | Y range | Rod clearance |
|---------|---------|---------|---------|---------------|
| Left | 5.0 to 9.0 (4.0 wide) | 56.0 to 60.0 (4.0 tall) | 0.0 to 112.5 | Rod: 3.5 mm dia in 4.0 mm channel |
| Right | 131.0 to 135.0 | 56.0 to 60.0 | 0.0 to 112.5 | Same |

Channels are open on the interior face of the wall and closed on three remaining sides. Rod diameter is 3.5 mm in a 4.0 mm channel (0.25 mm clearance per side).

### Lever Bearing Holes

Two cylindrical blind holes in the tray side walls, receiving the lever's pivot stubs:

| Bearing | X center | Y center | Z center | Hole diameter | Depth (into wall from inner face) |
|---------|----------|----------|----------|---------------|---------------------------------|
| Left | 2.5 | 9.0 | 58.0 | 6.1 | 5.0 (from X = 5.0 inward to X = 0.0) |
| Right | 137.5 | 9.0 | 58.0 | 6.1 | 5.0 (from X = 135.0 inward to X = 140.0) |

Hole diameter: 6.1 mm for 6.0 mm pivot stubs (0.1 mm diametral clearance for smooth rotation).

### Rail Ribs

Two rectangular ribs on the tray outer side walls, engaging the dock's C-channel grooves:

| Rib | X range | Z range | Y range | Protrusion |
|-----|---------|---------|---------|-----------|
| Left | -2.0 to 0.0 | 25.0 to 45.0 | 0.0 to 121.0 | 2.0 mm outward from left wall |
| Right | 140.0 to 142.0 | 25.0 to 45.0 | 0.0 to 121.0 | 2.0 mm outward from right wall |

Rib height: 20 mm (Z = 25 to 45). Rib runs the full tray depth. Total tray envelope including ribs: 144 mm wide.

### Lid-to-Tray Detent Ridges

Four small ridges on the tray outer side walls for snap-fit engagement with the lid's cantilever hooks:

| Ridge | X face | Y center | Z range | Protrusion (X) | Length (Y) |
|-------|--------|----------|---------|----------------|-----------|
| CL1 | 0.0 (left) | 30.0 | 67.0 to 69.0 | 0.8 mm in -X | 8.0 |
| CL2 | 0.0 (left) | 91.0 | 67.0 to 69.0 | 0.8 mm in -X | 8.0 |
| CL3 | 140.0 (right) | 30.0 | 67.0 to 69.0 | 0.8 mm in +X | 8.0 |
| CL4 | 140.0 (right) | 91.0 | 67.0 to 69.0 | 0.8 mm in +X | 8.0 |

Ridges are at Z = 67 to 69 (2 mm tall), near the top of the tray wall (Z = 70). The lid hooks engage from above when the lid is pressed down.

### Bezel Snap Tab Receiving Pockets

Two small rectangular pockets on the tray inner surfaces at the front opening, receiving the bezel's snap tabs:

| Pocket | X center | Y center | Z face | Pocket dimensions |
|--------|----------|----------|--------|------------------|
| T1 | 70.0 | 2.5 | 0.0 (bottom inner) | 5 x 3 x 0.8 mm (X x Y x Z) |
| T2 | 70.0 | 2.5 | 70.0 (top inner) | 5 x 3 x 0.8 mm |

---

## Part 2: Cartridge Lid

### Coordinate System

```
Origin: lower-left-front corner
X: 0..140 (matches tray width)
Y: 0..121 (matches tray depth)
Z: 0..4 (thickness)
Print orientation: outer surface (Z=4) down on build plate
Installed: sits atop tray, lid Z=0 at tray Z=70
```

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent | 140.0 mm |
| Y extent | 121.0 mm |
| Z extent | 4.0 mm |
| Material | PETG |
| Print orientation | Outer surface (Z = 4) down on build plate |
| Supports needed | No |

### Flat Plate

The lid is a flat plate 4.0 mm thick spanning the full tray top area. The underside (Z = 0, which contacts the tray top edges at tray Z = 70) is flat. The outer surface (Z = 4) is the cosmetically finished face, printed against the build plate for smooth finish.

### Snap-Fit Hooks

Four cantilever hooks extending downward from the lid perimeter, engaging the tray detent ridges:

| Hook | Lid X | Lid Y | Hook extends in | Cantilever length | Width | Thickness | Hook depth | Deflection |
|------|-------|-------|-----------------|-------------------|-------|-----------|-----------|-----------|
| H1 | 0.0 | 30.0 | -X (wraps left wall) | 12.0 | 2.0 | 1.5 | 0.8 | 2.0 |
| H2 | 0.0 | 91.0 | -X | 12.0 | 2.0 | 1.5 | 0.8 | 2.0 |
| H3 | 140.0 | 30.0 | +X (wraps right wall) | 12.0 | 2.0 | 1.5 | 0.8 | 2.0 |
| H4 | 140.0 | 91.0 | +X | 12.0 | 2.0 | 1.5 | 0.8 | 2.0 |

Each hook is a cantilever arm extending from the lid edge, wrapping around the tray side wall, with a 45-degree lead-in ramp at the tip and a vertical lock face at the hook engagement point. PETG's 5-7% elongation at break provides adequate flex for the 0.8 mm hook depth with 2.0 mm cantilever deflection.

---

## Part 3: Lever

### Coordinate System

```
Origin: center of left pivot stub end face
X: left pivot to right pivot, 0..130 (spans tray interior between side walls)
Y: pivot axis reference, paddle extends in -Y direction (toward user)
Z: perpendicular to pivot axis in the plane of rotation
Print orientation: paddle face down on build plate
```

The lever's local Y and Z rotate with the lever. At the locked position, lever-local -Y aligns with the tray front face direction, and lever-local +Z aligns with tray -Z (downward). At the unlocked position (90 degrees rotated), lever-local -Y aligns with tray +Z (upward).

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent | 130.0 mm (pivot to pivot) |
| Paddle width | 120.0 mm (X = 5.0 to 125.0) |
| Paddle height | 40.0 mm (Z = -20.0 to +20.0) |
| Paddle thickness | 4.0 mm (Y = -4.0 to 0.0) |
| Material | PETG |
| Print orientation | Paddle face down |
| Supports needed | No |

### Pivot Stubs

Two cylindrical stubs at each end of the lever body:

| Stub | X range | Diameter | Length |
|------|---------|----------|--------|
| Left | X = 0.0 to X = -5.0 | 6.0 | 5.0 |
| Right | X = 130.0 to X = 135.0 | 6.0 | 5.0 |

Stubs press into the tray bearing holes (6.1 mm diameter, 0.1 mm diametral clearance). The stubs print as short vertical cylinders when the paddle face is down -- no supports needed, bridge spans under 6 mm.

### Cam Lobes

Two eccentric discs, one at each end of the lever, positioned inside the tray side walls:

| Lobe | X range (lever frame) | Disc center (Y, Z) | Disc radius | Eccentricity from pivot |
|------|----------------------|---------------------|-------------|------------------------|
| Left | 0.0 to 4.0 | (0.0, 3.0) | 8.0 | 3.0 mm in +Z |
| Right | 126.0 to 130.0 | (0.0, 3.0) | 8.0 | 3.0 mm in +Z |

The cam disc center is offset 3.0 mm from the pivot axis in the lever-local +Z direction. When locked (paddle down), this eccentricity points in tray -Z (downward). When unlocked (paddle up, 90-degree rotation), the eccentricity shifts to tray -Y (toward front/user), pulling the push rods 3.0 mm in the -Y direction.

**Cam positions in tray frame (locked):**
- Left: disc center at tray (7.0, 9.0, 55.0), lowermost contact at Z = 47.0
- Right: disc center at tray (133.0, 9.0, 55.0), lowermost contact at Z = 47.0

**Cam positions in tray frame (unlocked):**
- Left: disc center at tray (7.0, 6.0, 58.0), rearmost contact at Y = 6.0 - 8.0 = N/A (the cam pushes the rod at the frontmost point Y = 6.0 + 8.0 = 14.0, but the contact interface is on the -Y face of the cam at Y = 6.0 - 8.0 = -2.0)

**DESIGN GAP:** The cam-to-rod contact interface geometry is not fully resolved in the spatial resolution document. The cam disc (8.0 mm radius) centered at tray Y = 6.0 (unlocked) would have its rearmost face at Y = 6.0 + 8.0 = 14.0 and its frontmost face at Y = 6.0 - 8.0 = -2.0. The rod channel starts at Y = 0.0. The cam must contact the rod's front end. In locked position the cam disc center is at Y = 9.0 and the rod front end sits against the cam's rearward face. When unlocking, the cam center shifts 3 mm in -Y (from 9.0 to 6.0), and the rod front end must follow. The rod-to-cam contact point and engagement geometry need detailed specification. For now, the rod front end is positioned at the cam disc's rearward tangent point.

### Paddle Face

The paddle is the flat user-facing surface:

| Parameter | Value (lever frame) |
|-----------|-------------------|
| Width | X = 5.0 to 125.0 (120 mm) |
| Height | Z = -20.0 to +20.0 (40 mm) |
| Thickness | Y = -4.0 to 0.0 (4 mm) |
| Grip edge fillet | 3 mm radius at Z = -20.0 bottom edge |
| User-facing surface | Y = -4.0 plane |

When locked, paddle bottom (lever Z = -20) is at tray Z = 18.0 and paddle top (lever Z = +20) is at tray Z = 58.0.

### Detent Spring Tab

A printed cantilever tab on the paddle edge for engaging the front bezel's V-notches:

| Parameter | Value (lever frame) |
|-----------|-------------------|
| Tab position | X = 60.0 to 62.0 (centered at X = 65.0, near paddle midpoint) |
| Tab extends from | Paddle edge at Z = -20.0 |
| Tab length | 12.0 mm in -Z direction |
| Tab width | 2.0 mm (X) |
| Tab thickness | 1.5 mm (Y) |
| Tip radius | 0.5 mm (matches V-notch depth) |

The tab sweeps across the bezel inner face as the lever rotates, clicking into V-notches at the locked (Z = -20 maps to tray Z = 18) and unlocked (Z = -20 maps to tray Z = 58) positions.

### Push/Pull Rods

Two rigid rods, one per side, integral to the lever assembly or as separate captive parts:

| Parameter | Value |
|-----------|-------|
| Rod diameter | 3.5 mm |
| Rod length | ~130 mm (from cam contact at Y ~ 9 to plate tab beyond Y = 121) |
| Rod X positions | 7.0 (left), 133.0 (right) |
| Rod Z position | 58.0 (pivot height) |
| Material | PETG or steel rod |

**DESIGN GAP:** The push/pull rods are described in the spatial resolution document as running from cam contact to plate transfer tabs, but whether they are printed PETG rods, steel rods, or integral extensions of the lever is not specified. Printed PETG rods 130 mm long at 3.5 mm diameter may flex under the 20-32 N collet force. Steel rods (3 mm music wire) would be stiffer and more reliable. The rod attachment to both the cam and the plate transfer tabs also needs detailed specification (pin joint, slot, captured end).

---

## Part 4: Release Plate

### Coordinate System

```
Origin: lower-left corner of the collet-contact face
X: 0..120 (plate width)
Z: 0..50 (plate height)
Y: 0..3 (plate thickness; Y=0 is collet-contact face, Y=3 is rear/dock-facing face)
Print orientation: flat, XZ plane on build plate
```

Installed orientation: collet-contact face (plate Y = 0) faces in the -Y direction in tray frame (toward fittings/wall when the plate shifts -Y during actuation). The plate sits outboard of the tray rear wall.

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width) | 120.0 mm |
| Z extent (height) | 50.0 mm |
| Y extent (thickness) | 3.0 mm |
| Material | PETG |
| Print orientation | Flat (XZ plane on build plate) |
| Supports needed | No |

### Position in Tray Frame

| Position | Collet-contact face (-Y face) | Rear face (+Y face) |
|----------|-------------------------------|---------------------|
| At rest (locked) | Y = 136.0 | Y = 139.0 |
| Actuated (unlocked) | Y = 133.0 | Y = 136.0 |
| Travel | 3.0 mm in -Y direction |

Plate left edge at tray X = 10.0. Plate bottom edge at tray Z = 9.8.

Transform: plate_X = tray_X - 10.0, plate_Z = tray_Z - 9.8.

### Stepped Bores

Four stepped through-bores, one per fitting, for collet engagement:

| Fitting | Plate X | Plate Z | Tray X | Tray Z |
|---------|---------|---------|--------|--------|
| F1 | 26.5 | 40.0 | 36.5 | 49.8 |
| F2 | 26.5 | 10.0 | 36.5 | 19.8 |
| F3 | 93.5 | 40.0 | 103.5 | 49.8 |
| F4 | 93.5 | 10.0 | 103.5 | 19.8 |

**Stepped bore profile (Y = 0 is collet-contact face, Y increases toward dock):**

| Zone | Diameter | Y start | Y end | Purpose |
|------|----------|---------|-------|---------|
| Tube clearance | 6.5 | 0.0 | 0.5 | Clears 6.35 mm tube; annular face 6.5 to 9.57 mm contacts collet |
| Collet hugger | 9.8 | 0.5 | 2.0 | Surrounds 9.57 mm collet OD for lateral constraint |
| Body end relief | 15.5 | 2.0 | 3.0 | Clears 15.10 mm body end OD |

### Guide Slots

Two edge slots for riding on the tray's guide posts:

| Slot | Plate X center | Plate Z center | Slot width | Slot height | Open edge |
|------|---------------|----------------|------------|-------------|-----------|
| Left | -2.0 | 25.0 | 4.3 | 4.3 | Left edge (X = 0) |
| Right | 122.0 | 25.0 | 4.3 | 4.3 | Right edge (X = 120) |

Slots are open on the plate edge, allowing the plate to be dropped onto the guide posts from the side during assembly. Slot width 4.3 mm for 4.0 mm guide posts (0.3 mm clearance).

### Transfer Tabs

Two tabs on the rear face (+Y face) of the plate for connection to the push/pull rods:

| Tab | Plate X | Plate Z | Tab dimensions |
|-----|---------|---------|---------------|
| Left | 0.0 (left edge) | 48.2 (maps to tray Z = 58.0) | 5 x 5 x 3 mm (X x Z x Y protrusion) |
| Right | 120.0 (right edge) | 48.2 | 5 x 5 x 3 mm |

The tabs protrude in the +Y direction (toward dock) from the plate rear face. The push rod tips engage these tabs. Tab tray-frame positions: left at X = 7.0 (approximate, considering plate offset and rod X = 7.0 needing to reach beyond the wall).

**DESIGN GAP:** The transfer tab X positions in plate frame should align with the rod X positions in tray frame. Rod left is at tray X = 7.0, which maps to plate X = 7.0 - 10.0 = -3.0. This is outside the plate boundary (plate X = 0 to 120). The tab must extend beyond the plate left edge by 3 mm, or the rod must shift inward. The same applies to the right rod at tray X = 133.0, mapping to plate X = 123.0 (outside plate width of 120). The rods and tabs need positional reconciliation.

---

## Part 5: Front Bezel

### Coordinate System

```
Origin: lower-left corner of outer (user-facing) surface
X: 0..140 (matches tray width)
Y: 0..5 (depth into tray)
Z: 0..70 (matches tray height)
Print orientation: outer face (Y=0) down on build plate
```

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent | 140.0 mm |
| Y extent | 5.0 mm |
| Z extent | 70.0 mm |
| Material | PETG |
| Print orientation | Face down (Y = 0 on build plate) |
| Supports needed | No |

### Frame Structure

The bezel is a rectangular frame covering the tray front opening. It is solid PETG except for the lever paddle cutout.

Installation: press-fits onto the tray front opening. Bezel Y = 0 aligns with tray Y = 0 (front face). Bezel extends 5 mm into the tray interior (to Y = 5 in bezel frame = Y = 5 in tray frame, since origins coincide at the front face).

### Lever Paddle Cutout

A rectangular opening for the lever paddle to swing through:

| Parameter | Value (bezel frame) |
|-----------|-------------------|
| X range | 10.0 to 130.0 (120 mm wide) |
| Z range | 18.0 to 58.0 (40 mm tall) |
| Rebate depth | 0.5 mm step-in around cutout perimeter |
| Rebate width | 1.0 mm perimeter |

The rebate (0.5 mm step-in) means the cutout inner face is 0.5 mm recessed from the bezel outer face (Y = 0). The lever paddle face sits in this rebate, creating a shadow line. The paddle face is at Y = 5.0 (tray frame, paddle outer face) which is 0.5 mm behind the bezel outer face at Y = 0 in bezel frame.

**DESIGN GAP:** The paddle outer face is at tray Y = 5.0 (9.0 - 4.0 thickness) and the bezel outer face is at tray Y = 0.0. This gives a 5.0 mm recess, not 0.5 mm. For the paddle to sit only 0.5 mm behind the bezel, either the paddle needs to be thicker (extending to Y = -0.5 in tray frame) or the bezel rebate needs to account for the 5 mm depth. The concept document states "paddle sits 0.5 mm recessed" but the spatial resolution places the paddle face at Y = 5.0, 5 mm behind the bezel face. This is a dimensional conflict that must be resolved. The lever paddle Y extent or the pivot Y position likely needs adjustment.

### Detent V-Notches

Two V-shaped notches on the bezel inner face for the lever's detent spring tab:

| Notch | X | Y (inner face) | Z | Width | Depth | Wall angle |
|-------|------|----------------|------|-------|-------|-----------|
| Locked | 70.0 | 5.0 | 18.0 | 2.0 | 0.5 | 45 degrees |
| Unlocked | 70.0 | 5.0 | 58.0 | 2.0 | 0.5 | 45 degrees |

### Snap Tabs

Two snap tabs for securing the bezel to the tray front opening:

| Tab | X | Y | Z | Tab protrusion |
|-----|------|-----|------|---------------|
| T1 (bottom) | 70.0 | 2.5 | 0.0 | 0.8 mm in -Z (engages tray pocket) |
| T2 (top) | 70.0 | 2.5 | 70.0 | 0.8 mm in +Z |

### Corner Treatment

All user-facing edges have 3 mm fillets. Internal edges (cutout perimeter, snap features) have 1.5 mm fillets minimum.

---

## Off-The-Shelf Hardware

| Part | Qty | Interface |
|------|-----|-----------|
| John Guest PP0408W 1/4" union fitting | 4 | Press-fit in 9.5 mm tray rear wall bores |
| M3 x 8 mm socket head cap screw | 8 | Through pump bracket holes into heat-set inserts |
| M3 heat-set insert | 8 | Installed in tray floor bosses |
| Copper foil tape (10 x 5 mm pads) | 4 | Adhesive in rear wall pocket recesses |
| Push/pull rod (3.5 mm diameter, ~130 mm long) | 2 | In tray side wall channels, cam-to-plate linkage |
| Silicone tubing (pump barb to JG fitting) | 4 lengths | Internal routing, ~200 mm total |

---

## Assembly Sequence

1. **Press 8 heat-set inserts** into the tray's pump mounting bosses using a soldering iron at 230 C. Insert from +Z direction into the 4.0 mm holes in the 7.0 mm OD bosses.
2. **Press 4 John Guest fittings** into the tray rear wall bores. Push the center body (9.31 mm) into the 9.5 mm bores by hand. The 15.10 mm barbell shoulders seat against both wall faces, providing axial retention.
3. **Apply copper tape pads** to the 4 electrical contact pocket recesses on the rear wall outboard face.
4. **Install the release plate** onto the guide posts. Drop the plate sideways (Z direction) so the open-edge guide slots capture the 4.0 mm posts. Slide the plate to its rest position (Y = 136.0 in tray frame).
5. **Insert push/pull rods** into the tray side wall channels. Feed each rod from the front of the tray (Y = 0) through the U-groove channel, through the rear wall transfer slot, and out to the release plate transfer tab.
6. **Set both Kamoer pumps** into the tray pockets, pump heads facing front (Y = 0), motors facing rear. Secure each pump with 4x M3 x 8 mm SHCS through the bracket mounting holes into the heat-set inserts.
7. **Route silicone tubing** from each pump barb to its corresponding JG fitting inboard port. Push tubing onto barbs and into fittings.
8. **Solder wires** from motor terminals to copper tape pads on the rear wall (or use pre-soldered leads routed along the tray floor).
9. **Press the lever pivot stubs** into the tray side wall bearing holes. Engage the cam lobes with the push/pull rod front ends.
10. **Press-fit the front bezel** onto the tray front opening. The 2 snap tabs click into the tray receiving pockets.
11. **Snap the lid** onto the tray top. Press down until all 4 snap hooks click onto the tray detent ridges.

### Service Disassembly (Pump Replacement)

1. Remove cartridge from dock (flip lever up, pull out).
2. Pry lid off (flex snap hooks with a flat tool).
3. Disconnect silicone tubing from pump barbs.
4. Unscrew 4x M3 screws per pump (8 total).
5. Lift pumps out.
6. Reverse steps 3-5 to install new pumps.
7. Snap lid back on.

---

## Critical Tolerances

| Feature | Nominal | Tolerance | Notes |
|---------|---------|-----------|-------|
| Fitting bore diameter | 9.5 mm | +0.2 / -0.0 | Slight oversize allows self-centering |
| Registration boss socket diameter (mouth) | 10.3 mm | +0.2 / -0.0 | 0.3 mm oversize for 10.0 mm boss |
| Guide post diameter | 4.0 mm | +0.0 / -0.1 | Undersize preferred |
| Guide slot width | 4.3 mm | +0.1 / -0.0 | 0.3 mm clearance for 4.0 mm post |
| Rail rib width | 2.0 mm | +0.0 / -0.3 | Undersize preferred; binding worse than wobble |
| Lever pivot stub diameter | 6.0 mm | +0.0 / -0.05 | Smooth rotation |
| Lever bearing hole diameter | 6.1 mm | +0.1 / -0.0 | 0.1 mm diametral clearance |
| Snap hook depth | 0.8 mm | +/-0.1 | Must engage detent ridge reliably |
| Detent V-notch depth | 0.5 mm | +/-0.1 | Must produce tactile click |
