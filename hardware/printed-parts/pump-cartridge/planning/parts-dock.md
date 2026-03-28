# Pump Cartridge Dock -- Parts Specification

Three printed PETG parts forming the permanent dock assembly inside the enclosure. The dock receives the removable pump cartridge on C-channel rails, presents 4 tube stubs and 2 registration bosses for blind fluid connection, and houses 4 spring-loaded blade contacts for electrical connection. The dock is assembled once during initial build and never removed by the user.

All dimensions in millimeters. All positions reference the part's own coordinate frame unless explicitly stated otherwise. The spatial resolution document is the authoritative source for every interface position used here.

---

## Mechanism Narrative

### What the user sees and touches

When the cartridge is removed, the user sees the dock opening at the bottom-front of the enclosure. The dock face frame (Part 3) is the only user-visible dock component -- a rectangular bezel flush with the enclosure front panel, framing the opening with a 5 mm deep entry chamfer on all four inner edges (30-degree taper, providing 2.9 mm of capture radius per side at the outer face). The face frame's outer surface is smooth matte black PETG printed against the build plate.

Looking through the opening, the user sees the dock cradle interior: a U-shaped channel with smooth side walls, the floor plate providing a flat sliding surface, and at the far end the rear wall with 4 tube stubs and 2 registration bosses protruding toward the user. The tube stubs are 1/4" OD polyethylene tubes with chamfered tips. The registration bosses are tapered PETG cylinders (10 mm base narrowing to 7 mm tip over 25 mm). The 4 blade contacts are recessed 2 mm behind the rear wall face and are not visible or touchable during normal cartridge handling.

During cartridge insertion, the user's hands contact only the cartridge (lever paddle and tray side walls). The dock interior is not touched -- the rails guide the cartridge without hand contact inside the dock.

### What moves

**Nothing in the dock moves during operation.** All three dock parts are permanently fixed:
- Dock cradle: mounted to enclosure interior walls via 4 snap-fit lugs (2 per side wall)
- Dock floor plate: snapped into cradle floor ledge
- Dock face frame: press-fit into enclosure front panel cutout

The only moving elements are the cartridge assembly (slides in/out on rails) and the spring-loaded blade contacts (compress 2 mm when the cartridge seats). The blade contacts are off-the-shelf phosphor bronze springs, not printed parts -- they deflect within their printed pockets.

### What converts the motion

No motion conversion occurs in the dock. The dock is a passive receiver. The cartridge's lever-cam mechanism handles all active functions (seating, release plate actuation, collet disengagement). The dock provides:
- **Guidance:** C-channel rail grooves constrain the cartridge to Y-axis travel (left groove at dock X = 7.7 to 10.3, right groove at X = 149.7 to 152.3, both Z = 32.7 to 53.3, full Y depth)
- **Alignment:** Registration bosses (25 mm long, engaging 5 mm before tubes reach fittings) center the cartridge within 0.2 mm before fluid connections are attempted
- **Connection:** Tube stubs (20 mm protrusion, 1.5 mm x 45-degree chamfer tips) enter the cartridge's John Guest fittings passively as the cartridge slides in
- **Electrical contact:** Spring-loaded blade contacts (3 mm spring travel) press against the cartridge's copper pads when the lever cam seats the cartridge the final 3 mm

### What constrains each moving part

**Blade contacts:** Each contact sits in a printed pocket in the dock cradle rear wall. The pocket constrains X and Z motion (pocket walls). The contact translates only in Y (spring compression direction). The pocket depth (5 mm) captures the contact body. The spring behind each contact provides the return force (pushes contact toward the cartridge when unloaded).

**Cartridge (as guest in the dock):** The C-channel grooves constrain the cartridge in X (lateral), Z (vertical), roll, and yaw. Only Y-axis translation (insertion axis) and small pitch adjustment remain free. The registration bosses eliminate pitch at the point of fluid connection.

### What provides the return force

The blade contacts' phosphor bronze springs provide the return force that keeps contacts protruding 1 mm past the rear wall face when the cartridge is absent. No other dock component has a return force requirement -- the dock is entirely passive and rigid.

### What is the user's physical interaction

The user never directly interacts with the dock parts during normal operation. The interaction sequence from the dock's perspective:

**Cartridge insertion (dock receives):**
1. User presents cartridge at the dock opening. The face frame's entry chamfers (5 mm deep, 30-degree taper) funnel the cartridge toward the rail grooves, providing 2.9 mm lateral capture range and 2.9 mm vertical capture range at the opening.
2. Cartridge rail ribs (2.0 mm protrusion, 20 mm tall) engage the C-channel grooves (2.6 mm wide, 20.6 mm tall, 0.3 mm clearance per side) within the first 10 mm of insertion.
3. At ~105 mm insertion depth, the registration bosses engage the cartridge's tapered sockets. Boss tips (7.0 mm diameter) enter socket mouths (10.3 mm diameter with matching taper to 7.3 mm base). This centers the cartridge to within 0.15-0.3 mm.
4. At ~110 mm insertion, the 4 chamfered tube stubs (effective tip diameter 3.35 mm) enter the cartridge's entry funnels (12.0 mm mouth at 8 mm depth). Stubs are guided into the 6.69 mm collet bores.
5. At full insertion (~121 mm in tray depth = dock Y travel from 130 to 9), the cartridge front face is flush with the face frame inner edge. The user flips the lever, and the cam pulls the cartridge 3 mm rearward, fully seating tube stubs, compressing blade contacts, and engaging electrical connections.

**Cartridge removal (dock releases):**
1. User flips the lever up (cam releases collets via the cartridge's internal release plate mechanism).
2. User pulls cartridge straight out. Tube stubs withdraw from fittings. Blade contacts spring back to protruding position.

---

## Part 1: Dock Cradle

### Coordinate System

```
Origin: lower-left corner of the front opening (user-facing side, floor level)
X: 0..160 (width, left to right)
Y: 0..130 (depth, front opening toward rear wall)
Z: 0..80 (height, bottom to top)
Print orientation: rear wall (Y=0) down on build plate; front opening (Y=130) faces up
Installed: front opening at enclosure front panel, Y increases toward enclosure rear
```

Note on Y convention: dock cradle Y = 0 is the rear wall (build-plate side, enclosure interior side). Y = 130 is the front opening (user side). The cartridge enters from Y = 130 and travels toward Y = 0. This is the opposite direction from the tray frame (where Y = 0 is the cartridge front). The transform is: dock_Y = 130.0 - tray_Y.

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent (width) | 160.0 mm |
| Y extent (depth) | 130.0 mm |
| Z extent (height) | 80.0 mm |
| Side wall thickness | 7.7 mm |
| Rear wall thickness | 7.0 mm (Y = 0.0 to Y = 7.0) |
| Floor ledge height | 5.0 mm |
| Material | PETG |
| Print orientation | Rear wall down (Y = 0 on build plate) |
| Supports needed | No |

### Outer Walls

**Side walls:**
- Left wall: X = 0.0 to X = 7.7, Y = 0.0 to Y = 130.0, Z = 0.0 to Z = 80.0
- Right wall: X = 152.3 to X = 160.0, Y = 0.0 to Y = 130.0, Z = 0.0 to Z = 80.0

Interior clear width between side wall inner faces: 152.3 - 7.7 = 144.6 mm. This accommodates the cartridge tray (140.0 mm body + 2.0 mm rail rib each side = 144.0 mm) with 0.3 mm clearance per side.

**Rear wall:**
- Y = 0.0 (outboard/enclosure-interior face) to Y = 7.0 (inboard face, facing the dock interior)
- X = 0.0 to X = 160.0
- Z = 0.0 to Z = 80.0

The rear wall thickness is 7.0 mm, sufficient to house the tube stub through-holes, registration boss bases, and blade contact pockets. The tube stubs pass through the wall as press-fit or bonded assemblies. The bosses are integral printed features protruding from the inboard face.

**Floor ledge:**
- Z = 0.0 to Z = 5.0 (bottom 5 mm of the cradle forms a ledge)
- The ledge inner face runs along both side walls and the rear wall, creating a perimeter shelf
- Ledge inner width: X = 5.0 to X = 155.0 (2.7 mm step-in from each side wall inner face for floor plate retention)
- Ledge top surface at Z = 5.0 receives the dock floor plate (3 mm thick, Z = 5.0 to 8.0)

The front opening (Y = 130) is fully open -- no front wall. The face frame mounts to the enclosure front panel around this opening.

### C-Channel Rail Grooves

Two grooves cut into the side wall inner faces, running the full depth from Y = 0 (rear wall inboard face, adjusted: groove starts at Y = 7.0 where the rear wall inboard face is) to Y = 130 (front opening). Each groove is a rectangular channel that captures the cartridge tray's rail rib.

| Groove | X range | Z range | Y range | Notes |
|--------|---------|---------|---------|-------|
| Left | 7.7 to 10.3 | 32.7 to 53.3 | 7.0 to 130.0 | 2.6 mm wide, 20.6 mm tall |
| Right | 149.7 to 152.3 | 32.7 to 53.3 | 7.0 to 130.0 | Mirror of left |

Groove dimensions:
- Width (X): 2.6 mm (for 2.0 mm rail rib, 0.3 mm clearance per side)
- Height (Z): 20.6 mm (for 20.0 mm rail rib, 0.3 mm clearance top and bottom)
- Depth into wall: the groove is cut 2.6 mm into the side wall inner face. Left groove starts at left wall inner face (X = 7.7) and extends 2.6 mm inward. Right groove starts at right wall inner face (X = 152.3) and extends 2.6 mm inward.

The grooves are open at the front (Y = 130) for cartridge entry. The groove is closed at the rear wall inboard face (Y = 7.0), providing a positive depth stop when the cartridge is fully inserted.

**Entry chamfer on grooves (at front opening, Y = 125 to Y = 130):**
- Groove width expands from 2.6 mm at Y = 125 to 5.6 mm at Y = 130 (1.5 mm chamfer per side)
- Groove height expands from 20.6 mm at Y = 125 to 26.6 mm at Y = 130 (3.0 mm chamfer top and bottom)
- Chamfer angle: 30 degrees on all four inner edges of each groove

**Print orientation note:** The cradle prints with Y = 0 (rear wall) on the build plate. The grooves run along the Z direction on the side walls, which builds as vertical channels parallel to the build direction. Layer lines run parallel to the insertion axis (Y), so sliding friction acts along layer boundaries -- favorable for smooth rail action.

### Tube Stub Through-Holes

Four through-holes in the rear wall for 1/4" OD (6.35 mm) polyethylene tube stubs:

| Hole | Dock X | Dock Z | Hole diameter | Y range |
|------|--------|--------|---------------|---------|
| H1 (mates F1) | 46.5 | 57.8 | 6.6 | 0.0 to 7.0 (through wall) |
| H2 (mates F2) | 46.5 | 27.8 | 6.6 | 0.0 to 7.0 |
| H3 (mates F3) | 113.5 | 57.8 | 6.6 | 0.0 to 7.0 |
| H4 (mates F4) | 113.5 | 27.8 | 6.6 | 0.0 to 7.0 |

Hole diameter: 6.6 mm for 6.35 mm tube (0.125 mm clearance per side; tubes are bonded or press-fit with adhesive on the enclosure side). The tube stubs protrude 20 mm from the inboard face of the rear wall into the dock interior (Y = 7.0 to Y = 27.0 in dock frame). On the outboard face (Y = 0), the tubes continue to the enclosure plumbing via John Guest fittings mounted permanently on the enclosure side.

**Tube stub details:**
- Material: 1/4" OD polyethylene hard tubing (6.35 mm OD)
- Protrusion into dock interior: 20.0 mm from rear wall inboard face (Y = 7.0 to Y = 27.0)
- Tip chamfer: 1.5 mm at 45 degrees (effective tip diameter ~3.35 mm)
- The chamfered tips increase the effective entry target from 6.69 mm (collet bore) to approximately 3.35 mm tip entering a 12 mm funnel mouth, providing substantial misalignment tolerance

### Registration Bosses

Two tapered cylindrical bosses protruding from the rear wall inboard face, for cartridge alignment:

| Boss | Dock X | Dock Z | Y base | Y tip | Base diameter | Tip diameter | Length |
|------|--------|--------|--------|-------|---------------|-------------|--------|
| A (lower-left) | 31.5 | 17.8 | 7.0 | 32.0 | 10.0 | 7.0 | 25.0 |
| B (upper-right) | 128.5 | 67.8 | 7.0 | 32.0 | 10.0 | 7.0 | 25.0 |

Boss taper: linear from 10.0 mm diameter at base (Y = 7.0) to 7.0 mm diameter at tip (Y = 32.0), over 25 mm length. Taper half-angle: arctan((10.0 - 7.0) / (2 x 25)) = 3.4 degrees.

Bosses are integral printed features of the dock cradle rear wall. They are positioned at diagonally opposite corners of the fitting pattern -- Boss A near fitting F2 (lower-left), Boss B near fitting F3 (upper-right).

**Engagement sequence:** Bosses protrude to Y = 32.0 in dock frame; tube stubs protrude to Y = 27.0. Bosses extend 5 mm farther than tube stubs. This means the boss tips engage the cartridge's tapered sockets 5 mm before any tube stub contacts a fitting collet, providing progressive alignment: bosses center the cartridge to within 0.15-0.3 mm before tubes attempt the 6.69 mm collet entry.

**Matching cartridge sockets:** Boss A mates with tray socket A at tray (X = 21.5, Z = 9.8), which maps to dock (31.5, 9.0, 17.8). Boss B mates with tray socket B at tray (X = 118.5, Z = 59.8), which maps to dock (128.5, 9.0, 67.8). Socket mouths are 10.3 mm diameter (0.3 mm oversize for 10.0 mm boss base), with matching taper to 7.3 mm at 15 mm depth.

### Blade Contact Pockets

Four rectangular pockets in the rear wall inboard face, each housing a spring-loaded phosphor bronze blade contact:

| Pocket | Dock X center | Dock Z center | Width (X) | Height (Z) | Depth (Y) | Y range |
|--------|--------------|---------------|-----------|------------|-----------|---------|
| P1 (C1) | 68.0 | 42.8 | 12.0 | 6.0 | 5.0 | 2.0 to 7.0 |
| P2 (C2) | 80.0 | 42.8 | 12.0 | 6.0 | 5.0 | 2.0 to 7.0 |
| P3 (C3) | 92.0 | 42.8 | 12.0 | 6.0 | 5.0 | 2.0 to 7.0 |
| P4 (C4) | 104.0 | 42.8 | 12.0 | 6.0 | 5.0 | 2.0 to 7.0 |

Pocket width (12.0 mm) and height (6.0 mm) are each 2 mm larger than the blade contact (10.0 mm x 4.0 mm) to allow pocket wall clearance for the contact body and spring. Pocket depth (5.0 mm) extends from Y = 2.0 (2 mm behind the rear wall inboard face at Y = 7.0, into the wall) to the rear wall inboard face. The pocket opens at the inboard face (Y = 7.0) so the blade tip protrudes into the dock interior.

**Blade contact geometry (off-the-shelf part):**
- Blade face: 10.0 mm wide (X) x 4.0 mm tall (Z)
- Blade body + spring: ~15 mm long (Y)
- At rest (no cartridge): blade tip protrudes 1.0 mm past the rear wall inboard face (tip at Y = 8.0)
- Spring travel: 3.0 mm (blade can be pushed back to 2 mm behind the inboard face)
- When cartridge is locked: blade is compressed ~2 mm, achieving solid contact pressure against the copper pad

**Wire routing:** Each blade contact has a solder tab or wire crimp extending from its rear end. The wire exits the pocket through the rear wall outboard face (Y = 0) via a 3.0 mm diameter routing hole at the same X and Z as the pocket center. Wires route from the dock rear wall outboard face to the L298N motor driver mounted elsewhere in the enclosure.

| Wire hole | Dock X | Dock Z | Diameter | Y range |
|-----------|--------|--------|----------|---------|
| W1 | 68.0 | 42.8 | 3.0 | 0.0 to 2.0 |
| W2 | 80.0 | 42.8 | 3.0 | 0.0 to 2.0 |
| W3 | 92.0 | 42.8 | 3.0 | 0.0 to 2.0 |
| W4 | 104.0 | 42.8 | 3.0 | 0.0 to 2.0 |

### Enclosure Mounting Lugs

Four snap-fit lugs on the cradle outer side walls for permanent attachment to the enclosure half-shell interior:

| Lug | X face | Y center | Z center | Protrusion | Lug dimensions |
|-----|--------|----------|----------|-----------|----------------|
| L1 | 0.0 (left) | 40.0 | 40.0 | 3.0 mm in -X | 10 x 10 x 3 mm (Y x Z x X) |
| L2 | 0.0 (left) | 100.0 | 40.0 | 3.0 mm in -X | 10 x 10 x 3 mm |
| L3 | 160.0 (right) | 40.0 | 40.0 | 3.0 mm in +X | 10 x 10 x 3 mm |
| L4 | 160.0 (right) | 100.0 | 40.0 | 3.0 mm in +X | 10 x 10 x 3 mm |

Each lug is a rectangular tab with a 45-degree lead-in ramp and a 1.0 mm hook depth. The lugs engage rectangular pockets molded into the enclosure inner walls. The hook face is vertical (perpendicular to X) for positive retention. Lugs are at Z = 40 (dock mid-height) and spaced at Y = 40 and Y = 100 for stable two-point mounting on each side.

**DESIGN GAP:** The enclosure half-shell is not yet designed. The lug positions (X, Y, Z) and pocket dimensions are preliminary estimates. These must be reconciled with the enclosure interior wall geometry when the enclosure parts spec is written.

### Print Orientation Notes

The cradle prints with the rear wall (Y = 0) on the build plate:
- Side walls build vertically in Z and extend in Y from the build plate. Layer lines are parallel to the XZ plane.
- C-channel grooves are cut into the side wall inner faces, running along Y. Since the grooves run perpendicular to the layer lines, they are vertical channels during printing -- no overhang, no supports needed.
- Registration bosses build vertically from the rear wall (build plate surface), tapering from 10 mm to 7 mm. The taper is shallow (3.4-degree half-angle) and builds cleanly layer by layer.
- Tube stub holes are vertical through-holes in the rear wall (which is flat on the build plate). These print as simple circular holes in the first few layers.
- Blade contact pockets are rectangular cavities in the rear wall. They open toward the dock interior (+Y direction, which is upward during printing). The pocket ceilings (at Y = 7.0) are flat faces built on top of the pocket void. At 12 mm x 6 mm cross-section, bridging is feasible without supports.

---

## Part 2: Dock Floor Plate

### Coordinate System

```
Origin: lower-left-front corner
X: 0..150
Y: 0..120
Z: 0..3 (thickness)
Print orientation: flat on build plate (Z = 0 down)
Installed: snaps into cradle floor ledge at dock cradle Z = 5.0
```

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent | 150.0 mm |
| Y extent | 120.0 mm |
| Z extent (thickness) | 3.0 mm |
| Material | PETG |
| Print orientation | Flat (Z = 0 on build plate) |
| Supports needed | No |

### Flat Plate

The floor plate is a simple flat rectangular plate, 150 mm x 120 mm x 3 mm. The top surface (Z = 3.0) is the sliding surface the cartridge tray rides on. This surface should be smooth -- printed flat on the build plate ensures the bottom face (Z = 0) is smooth; the top face (Z = 3.0) is the last printed layer and can be ironed for a smooth finish.

### Position in Dock Cradle

The floor plate sits on the cradle floor ledge:
- Plate Z = 0 rests on the cradle ledge top surface at dock cradle Z = 5.0
- Plate Z = 3 (top surface, sliding surface) is at dock cradle Z = 8.0
- The cartridge tray bottom (tray Z = 0) sits on this surface at dock cradle Z = 8.0

**X positioning:** The plate is centered in the cradle interior. Cradle interior width between ledge step-ins: X = 5.0 to X = 155.0 (150 mm). Plate X = 0 maps to cradle X = 5.0. Plate X = 150 maps to cradle X = 155.0. The plate fits snugly between the ledge step-ins.

**Y positioning:** The plate extends from the rear wall inboard face to 10 mm short of the front opening. Cradle rear wall inboard face at dock Y = 7.0. Plate Y = 0 maps to cradle Y = 7.0. Plate Y = 120 maps to cradle Y = 127.0. The 3 mm gap to the front opening (dock Y = 127 to 130) allows the face frame inner lip to overlap without interference.

### Snap-Fit Retention

The floor plate is retained in the cradle by the ledge geometry. The plate drops in from above (before the cartridge is installed) and is captured by:
- **Lateral (X):** The cradle ledge step-ins (2.7 mm per side) create a channel. The plate fits within 0.15 mm clearance per side (plate width 150.0 mm in 150.3 mm channel = 0.15 mm per side).
- **Vertical (Z):** The plate rests on the ledge by gravity. The cartridge tray sits on top of the plate, preventing upward displacement during use.
- **Depth (Y):** The plate is constrained between the rear wall inboard face (Y = 7.0) and friction with the cartridge tray.

Two snap tabs on the plate underside (Z = 0 face) engage small pockets in the cradle ledge to prevent the plate from shifting during cartridge insertion/removal:

| Tab | Plate X | Plate Y | Tab protrusion (-Z) | Tab dimensions |
|-----|---------|---------|---------------------|---------------|
| S1 | 75.0 | 30.0 | 1.0 mm | 5 x 5 x 1 mm (X x Y x Z) |
| S2 | 75.0 | 90.0 | 1.0 mm | 5 x 5 x 1 mm |

Tabs are centered on the plate width (X = 75) and spaced along Y. Each tab is a small rectangular bump that snaps into a matching 5.2 x 5.2 x 1.2 mm pocket in the cradle ledge surface at the corresponding position (cradle X = 80.0, cradle Y = 37.0 and 97.0, cradle Z = 5.0 face).

### Corner Treatment

All edges have 0.5 mm chamfers. The plate is not a user-visible or user-touched part; cosmetic treatment is minimal.

---

## Part 3: Dock Face Frame

### Coordinate System

```
Origin: lower-left corner of outer (user-facing) surface
X: 0..170
Y: 0..5 (depth)
Z: 0..90
Print orientation: outer face (Y = 0) down on build plate
Installed: outer face flush with enclosure front panel
```

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| X extent | 170.0 mm |
| Y extent (depth) | 5.0 mm |
| Z extent | 90.0 mm |
| Material | PETG |
| Print orientation | Face down (Y = 0 on build plate) |
| Supports needed | No |

### Frame Structure

The face frame is a rectangular bezel -- a flat frame with a central opening. The frame width (material around the opening) varies:
- Left and right: (170 - 142) / 2 = 14.0 mm per side
- Top and bottom: (90 - 72) / 2 = 9.0 mm per side

### Inner Opening

The opening receives the cartridge front bezel (140 mm wide x 70 mm tall) with a 1 mm reveal gap on all sides:

| Parameter | Value (face frame frame) |
|-----------|------------------------|
| Opening X range | 14.0 to 156.0 (142 mm wide) |
| Opening Z range | 9.0 to 81.0 (72 mm tall) |
| Reveal gap to cartridge bezel | 1.0 mm per side (uniform) |

### Entry Chamfers

All four inner edges of the opening have entry chamfers that funnel the cartridge into the dock:

| Parameter | Value |
|-----------|-------|
| Chamfer depth | 5.0 mm (full frame Y depth, from Y = 0 to Y = 5) |
| Chamfer angle | 30 degrees from the insertion axis |
| Outer face opening (Y = 0) | X = 8.2 to 161.8 (153.6 mm wide), Z = 6.1 to 83.9 (77.8 mm tall) |
| Inner face opening (Y = 5) | X = 14.0 to 156.0 (142 mm wide), Z = 9.0 to 81.0 (72 mm tall) |
| Capture expansion per side | 5 x tan(30) = 2.9 mm |

Derivation: at the outer face (Y = 0), the chamfer widens the opening by 2.9 mm per side relative to the inner face (Y = 5). So: outer left edge = 14.0 - 2.9 = 11.1 mm...

Let me restate using the spatial resolution document directly: At Y = 0 (outer face), the opening is approximately 152 mm x 82 mm (5 mm x tan(30) = 2.9 mm expansion per side from the 142 x 72 inner opening). At Y = 5 (inner face, where the cartridge bezel sits flush), the opening is 142 mm x 72 mm.

The chamfers smoothly guide the cartridge bezel (140 x 70 mm) into the 142 x 72 mm opening. With the outer face opening at approximately 148 x 78 mm (142 + 2 x 2.9 = 147.8 wide, 72 + 2 x 2.9 = 77.8 tall), the user has approximately 4 mm of lateral and vertical tolerance when initially presenting the cartridge.

### Enclosure Panel Mounting

The face frame press-fits into a matching rectangular cutout in the enclosure front panel. The frame's outer perimeter (170 x 90 mm) is the retention surface. A 0.5 mm interference fit on the perimeter provides retention. Adhesive backup can be applied if press-fit alone is insufficient.

**DESIGN GAP:** The enclosure front panel cutout dimensions and retention feature geometry are not yet specified. The face frame perimeter dimensions (170 x 90 mm) and the press-fit interface need to be coordinated with the enclosure parts spec when it is written.

### Corner Treatment

All user-facing edges (outer perimeter and chamfer surfaces) have 3 mm fillets for a smooth appliance feel. The chamfer surfaces themselves are smooth, printed against the build plate (face-down orientation). Internal edges at the inner opening (where the chamfer meets the straight inner wall) have 1.5 mm fillets.

### Visual Design

The face frame is matte black PETG, matching the project's dark design language. The outer surface (Y = 0) is the cosmetically finished face, printed against the build plate for maximum smoothness. This surface is visually part of the enclosure front panel -- it should blend seamlessly. The 1 mm reveal gap between the face frame inner edge and the cartridge bezel is the primary visual signal that the cartridge is removable.

---

## Off-The-Shelf Hardware (Dock Assembly)

| Part | Qty | Interface |
|------|-----|-----------|
| 1/4" OD polyethylene tube (stubs) | 4 x 20 mm | Press-fit/bonded in dock cradle rear wall 6.6 mm holes |
| Phosphor bronze blade contact (spring-loaded) | 4 | Press-fit in dock cradle rear wall pockets |
| Silicone-insulated wire (to motor driver) | 4 lengths | Soldered to blade contact tails, routed through rear wall wire holes |

---

## Assembly Sequence (Dock, One-Time Build)

1. **Insert tube stubs** into the dock cradle rear wall through-holes from the inboard face (Y = 7.0 side). Push each 1/4" OD polyethylene tube through the 6.6 mm hole until 20 mm protrudes on the inboard side. Bond with adhesive on the outboard face (Y = 0) if needed. Chamfer the inboard tips: 1.5 mm at 45 degrees.
2. **Install blade contacts** into the 4 pockets in the rear wall inboard face. Press each spring-loaded phosphor bronze blade into its 12 x 6 x 5 mm pocket (P1-P4). The contact body sits in the pocket with the blade tip protruding 1 mm past the inboard face. Spring behind the contact body provides restoring force.
3. **Route wires** from each blade contact tail through the 3.0 mm wire routing holes to the outboard face. Solder or crimp wires. Route to the L298N motor driver.
4. **Drop in the floor plate.** Lower the floor plate into the cradle from above, aligning it on the floor ledge (Z = 5.0). Press down until the 2 snap tabs click into the ledge pockets.
5. **Mount the cradle in the enclosure.** Press the cradle into the enclosure interior until the 4 mounting lugs snap into the enclosure wall pockets. Front opening aligns with the enclosure front panel cutout.
6. **Press-fit the face frame** into the enclosure front panel cutout from the exterior. Push until the frame is flush with the panel surface.
7. **Connect dock tube stubs** to the enclosure plumbing on the outboard side (Y = 0) using John Guest fittings or direct tubing connections.

### Service Disassembly

The dock is a permanent assembly. If service is needed:
1. Separate the enclosure half-shells (requires removing enclosure snap-fits -- a Tier 3 builder operation).
2. The cradle, floor plate, and face frame are then individually accessible.
3. Blade contacts can be pulled from their pockets and replaced.
4. Tube stubs can be cut and re-bonded if damaged.

---

## Critical Tolerances

| Feature | Nominal | Tolerance | Notes |
|---------|---------|-----------|-------|
| C-channel groove width | 2.6 mm | +0.2 / -0.0 | Oversize preferred; binding worse than wobble |
| C-channel groove height | 20.6 mm | +0.2 / -0.0 | Same rationale |
| Tube stub hole diameter | 6.6 mm | +0.1 / -0.0 | Slight oversize for bonded assembly |
| Registration boss base diameter | 10.0 mm | +0.0 / -0.2 | Undersize preferred for clearance in 10.3 mm socket |
| Registration boss tip diameter | 7.0 mm | +0.0 / -0.2 | Undersize preferred for clearance in 7.3 mm socket base |
| Blade contact pocket width | 12.0 mm | +0.2 / -0.0 | Contact must slide in freely |
| Blade contact pocket height | 6.0 mm | +0.2 / -0.0 | Same rationale |
| Floor plate X fit | 150.0 mm in 150.3 mm channel | 0.15 mm per side | Snug but not binding |
| Face frame inner opening width | 142.0 mm | +0.5 / -0.0 | Must clear 140 mm cartridge + 1 mm gap per side |
| Face frame inner opening height | 72.0 mm | +0.5 / -0.0 | Must clear 70 mm cartridge + 1 mm gap per side |
