# Left Wall — Parts Specification

Build sequence: Season 2, Phase 7, Item 17
Part: Left wall panel with interior rails for all 6 enclosure panels and 2 interior plates.

---

## Spatial Layout Reasoning

### Coordinate Conventions for the Cartridge

The left wall lives in the YZ plane. Its thickness runs in X.

- X: wall thickness axis. X=0 = exterior face (left side, facing away from interior). X=WALL_T = interior face (facing +X, toward the inside of the cartridge).
- Y: front-to-back axis. Y=0 = cartridge front (where user interface is). Y increases toward the back.
- Z: height axis. Z=0 = cartridge bottom. Z increases upward.

All interior plates (pump tray, coupler tray) are 140.0mm wide (X span between inner faces of left and right walls), 68.6mm tall (Z), and 3.0mm thick (Y). They slide into rails on left and right walls, moving in the Y direction (front to back).

---

### Interior Width (X between inner faces of left and right walls)

Set by the plate width: **140.0mm**. Both plates are exactly 140.0mm wide.

---

### Interior Height (Z between inner faces of bottom and top panels)

The interior plates are 68.6mm tall. The rails for the interior plates run in Y (front-to-back), and the plates fill the full Z interior span. Interior height = **68.6mm**.

All wall panels (front, back, bottom, top) are also sized to fit this Z interior dimension where relevant.

---

### Interior Depth (Y between inner faces of front and back panels)

The Y depth is set by the components that must coexist in this space.

**Front zone (in front of pump tray, toward cartridge front):**

The pump bracket face is the pump tray front face (Y=0 of the pump tray). The pump head extends 48.88mm forward of the bracket face (caliper-verified: geometry-description.md, photo 14). This 48.88mm of pump head depth must fit between the pump tray front face and the inner face of the front panel.

The lever (4mm thick), release plate (5mm thick), and coupler tray (12.08mm deep with bosses) also live in this front zone. Combined mechanical stack depth = 4 + 5 + 12.08 = 21.08mm, which is less than the 48.88mm pump head constraint. The pump head is the binding constraint.

Front zone minimum = 48.88mm pump head + clearance. Using 50.0mm (1.12mm clearance for tolerance and front panel inner face offset).

Pump tray placement: pump tray front face at Y = FRONT_ZONE = 50.0mm from inner face of front panel, i.e., pump tray occupies Y_interior = 50.0 to 53.0mm (3mm thick plate).

**Rear zone (behind pump tray, toward cartridge back):**

The motor body extends behind the pump tray bracket face. Motor body length (bracket face to nub end): ~67.6mm (derived from: total length with nub 116.48mm minus pump head depth 48.88mm = 67.6mm). Motor diameter: 35.73mm.

Rear zone minimum = 67.6mm motor + clearance. Using 70.0mm (2.4mm for motor nub tolerance and back panel clearance).

**Total interior depth = front zone + pump tray + rear zone:**
= 50.0 + 3.0 + 70.0 = **123.0mm**

Interior Y runs from inner face of front panel (Y_int = 0) to inner face of back panel (Y_int = 123.0mm).

---

### Panel Thickness and Wall Outer Dimensions

All panels (front, back, bottom, top, left, right) use 3.0mm thickness.

Wall Y extent (front to back, outer):
- Front panel outer face at Y=0 (flush with cartridge front).
- Front panel is 3.0mm thick: inner face at Y=3.0mm.
- Interior depth: 123.0mm → back panel inner face at Y = 3.0 + 123.0 = 126.0mm.
- Back panel outer face at Y = 126.0 + 3.0 = 129.0mm.
- **Wall Y (WALL_Y) = 129.0mm**

Wall Z extent (bottom to top, outer):
- Bottom panel outer face at Z=0 (cartridge bottom).
- Bottom panel is 3.0mm thick: inner face at Z=3.0mm.
- Interior height: 68.6mm → top panel inner face at Z = 3.0 + 68.6 = 71.6mm.
- Top panel outer face at Z = 71.6 + 3.0 = 74.6mm.
- **Wall Z (WALL_Z) = 74.6mm**

Wall X (thickness): **WALL_T = 3.0mm**

**Left wall outer envelope: 3.0mm (X) × 129.0mm (Y) × 74.6mm (Z)**

Print bed check: 129.0mm × 74.6mm — well within 320mm × 320mm build area.

---

## Rail Geometry

A rail is two parallel lips protruding from the interior face (at X=WALL_T=3.0mm), forming a channel that a panel or plate slides into.

**Rail parameters (from brief):**
- Channel width = panel/plate thickness + 0.4mm (0.2mm clearance per side): 3mm panels → 3.4mm channels
- Rail lip height: 3.0mm (protrusion inward from interior face, in -X direction, i.e., from X=3.0 toward X=6.0 for the left wall)
- Rail lip width: 2.0mm (in the direction perpendicular to slide travel, along the channel edge)
- No detent geometry (Phase 7 scope)

The rail itself as built: two rectangular bars attached to the interior face, separated by the channel width, running in the slide direction.

Each rail lip is a box:
- Width along slide axis: full span of channel travel (the length the panel traverses)
- Width perpendicular to slide: 2.0mm (lip width)
- Height (protrusion from interior face): 3.0mm

The channel floor is the interior face of the wall. Channel width = 3.4mm (between inner faces of the two lips, i.e., the gap through which the panel slides).

A rail for a panel that spans full Y and slides in Z: the two lips run in Y (full Y extent of the channel), separated by 3.4mm in Z.

A rail for a panel or plate that spans full Z (or partial Z) and slides in Y: the two lips run in Z, separated by 3.4mm in Y.

---

## Rail Positions on the Left Wall Interior Face

Coordinate system for rail positions: using wall-local coordinates.
- Wall interior face is at X=WALL_T=3.0mm.
- Y runs 0 to 129.0mm (front to back).
- Z runs 0 to 74.6mm (bottom to top).
- Rail lips protrude from X=3.0mm inward (+X direction), reaching X=6.0mm at tips.

### 1. Front Panel Rail

Front panel: 3.0mm thick in Y, slides in from above (-Z direction, entering Z=WALL_Z and moving to its final Z position). Sits at Y=0..3.0mm (front panel outer face flush with wall front edge at Y=0, inner face at Y=3.0mm).

Rail channel runs in Z (panel slides in Z direction). Two lips parallel to Z, separated by 3.4mm in Y, centered on panel Y position.

- Panel Y center = 1.5mm
- Lip 1 (front lip): Y = 1.5 - 3.4/2 = 1.5 - 1.7 = -0.2mm → clamp to Y=0.0mm (lip at Y=0 front edge — the wall body front face acts as one rail face; use a single lip at Y=3.4mm instead, letting the wall front edge serve as the other)

Actually, cleaner: the two lips straddle the panel. Panel center at Y=1.5mm. Lip 1 at Y_inner edge = 0.0mm (wall front edge), Lip 2 at Y_inner edge = 3.4mm. But Y=0 is the wall front face — no room for a lip there. Better to place the channel so the panel front face is flush with the wall front face (Y=0). Then:

- Lip 1: inner edge at Y=0, outer edge at Y=2.0mm (lip width = 2mm in Y, lip runs from Y=0 to Y=2.0mm)
- Panel sits against lip 1: panel front face at Y=2.0mm... but we want front face at Y=0.

Alternative: let the wall front face (Y=0) be one edge of the channel (no lip needed there — wall body is the stop), and put only one lip at Y=3.4mm (inner edge). This is a one-sided rail; the wall face serves as the other side. This works for the front and back panels.

Simpler approach used by the brief: just two lips. For front panel, place:
- Channel center at Y = 1.5mm (panel center)
- Lip A: from Y=0.0 to Y=(-0.2)... impossible. Let the wall extend slightly in front.

Revised approach: Accept that the front panel sits recessed 2.0mm from the wall front face (the lip takes up 2mm). So:

Front panel rail: Panel sits at Y = 2.0 to 5.0mm (front lip takes Y=0..2mm, panel occupies Y=2.0..5.0mm, rear lip takes Y=5.0..7.0mm). Interior Y then starts at Y=5.0mm (inner face of front panel). This shifts interior Y start.

Let me redo Y layout using realistic rail positions:

**Revised Y layout with rail space:**

- Front panel rail front lip: Y=0..2mm (outer lip)
- Front panel: Y=2..5mm (3mm panel, outer face at Y=2, inner face at Y=5)
- Front panel rail rear lip: Y=5..7mm (inner lip)
- Interior depth: Y=7mm to Y=7+123=130mm (but 123mm is measured from inner face of front panel to inner face of back panel, so inner face of front panel = Y=5mm, inner face of back panel = Y=5+123=128mm)
- Back panel rail front lip: Y=128..130mm (inner lip of back panel rail)
- Back panel: Y=130..133mm
- Back panel rail rear lip: Y=133..135mm (outer lip)
- Wall rear face: Y=135mm

Hmm this is getting complicated. Let me step back and use a cleaner model.

**Clean approach:** Define the wall Y extent directly, then place the rail lips as features added to the interior face.

The rail lips are features ON the interior face — they protrude inward (in +X for the left wall). They do NOT extend in Y outside the wall body. The wall body runs Y=0..WALL_Y.

For the front panel: it slides into the left wall (and right wall) in the -Z direction (enters from the top). The panel is 3mm thick in Y. Its position in Y is set by the rail channel. The channel's Y center position is where I want the front panel to sit.

I want the front panel outer face (the exterior face of the cartridge front) at Y=0. So:
- Front panel: Y=0..3.0mm (outer face at Y=0, inner face at Y=3.0mm)
- Rail channel Y span: 0..3.4mm (panel occupies 3mm + 0.2mm clearance each side → channel from Y=-0.2 to Y=3.2... so centered at Y=1.5mm with half-width 1.7mm)

The rail lips for the front panel:
- Lip A: centered at Y = -0.2mm (outside the wall) — this doesn't work, the wall starts at Y=0

Let the channel be from Y=0 to Y=3.4mm. Panel slides into Y=0.2..3.2mm (0.2mm clearance each side). The "outer" face of the front panel at Y=0.2mm is nearly flush with wall front face.

For this Phase 7 part (no retention features), the rail just needs to guide the panel. The wall front face (Y=0) naturally acts as a stop for the outer face. I'll model:

- Front panel rail: lip at Y=3.4mm (one lip only on the inner side; the wall front face Y=0 serves as the outer guide face implicitly via the wall body). But the brief says "two parallel lips." So I must add two lips.

For the front panel, place both lips inward from the wall front face:
- Lip A (outer): Y=0 to Y=2.0mm (sits at front of wall)
- Channel: Y=2.0 to Y=5.4mm (3.4mm channel width)
- Lip B (inner): Y=5.4 to Y=7.4mm

Front panel outer face at Y=2.0mm (recessed 2mm from cartridge exterior). Accept this.
Front panel inner face at Y=5.0mm (= 2.0 + 3.0mm panel thickness, with channel Y=2.0..5.4, panel sits at Y=2.2..5.2 with clearance... actually panel inner face = Y=2.0 + 3.0 = 5.0mm).

Interior Y starts at Y=5.0mm (inner face of front panel at Y=5.0).

Applying same logic to back panel (rear lip of back panel at wall rear edge):
- Back panel inner face at Y = 5.0 + 123.0 = 128.0mm
- Lip B (inner): Y=128.0 to Y=130.0mm
- Channel: Y=128.0..131.4mm (or: channel starts at Y=127.8, panel inner face at Y=128.0)
- Lip A (outer): at Y=131.4..133.4mm

Back panel inner face at Y=128.0mm, outer face at Y=131.0mm.

Wall rear face at Y ≥ 133.4mm. Use WALL_Y = 134.0mm (rounds up cleanly).

Similarly for Z (bottom/top panels):

Bottom panel (slides in from front, Y direction):
- Lip A: Z=0..2.0mm (at bottom of wall)
- Channel: Z=2.0..5.4mm
- Lip B: Z=5.4..7.4mm
- Bottom panel outer face at Z=2.0mm, inner face at Z=5.0mm.

Top panel (slides in from top, -Z direction):
- Interior Z starts at Z=5.0mm (inner face of bottom panel)
- Interior height = 68.6mm → interior Z ends at Z=5.0+68.6=73.6mm (inner face of top panel)
- Top panel outer face at Z=73.6+3.0=76.6mm
- Lip B (inner): Z=73.6..75.6mm
- Channel: Z=73.6..77.0mm
- Lip A (outer): Z=77.0..79.0mm
- Wall top face: Z ≥ 79.0mm. Use WALL_Z = 80.0mm.

**Revised final wall outer envelope: 3.0mm (X) × 134.0mm (Y) × 80.0mm (Z)**

---

**Pause and simplify:** The above reasoning tracks 0.2mm clearances inside the channel, but for the rail positions what matters is the **lip positions** (as modeled geometry). The panels and plates themselves have separate scripts. For the left wall script, I model the wall body plus the rail lips. The channel is the gap between the lips.

Let me define everything in terms of lip positions and derive the wall dimensions from those.

**Panel thickness (all panels): PANEL_T = 3.0mm**
**Clearance per side: 0.2mm → channel width = 3.4mm**
**Lip height (protrusion from interior face): LIP_H = 3.0mm**
**Lip width (along the edge): LIP_W = 2.0mm**

**Rail channel = 3.4mm wide gap between inner faces of two lips.**

---

### Summary: Rail Positions (Wall-Local Coordinates)

All rail lips are rectangular bars attached to the interior face (X=WALL_T, protruding in +X to X=WALL_T+LIP_H).

**Interior face is at X=WALL_T=3.0mm. Lips run from X=3.0mm to X=6.0mm.**

---

**Front Panel Rail** — panel slides in -Z direction (entering from top of wall, moves downward to seat)

Slide axis: Z. Lip bars run along Z (parallel to Z axis). Two lips at fixed Y positions, separated by 3.4mm channel in Y.

Desired front panel position: outer face at Y=0 (flush with wall front edge). Panel occupies Y=0..3.0mm. Channel: Y=-0.2 to Y=3.2mm, centered at Y=1.5mm.

Since Y=-0.2 is outside wall body, let the lip A run from Y=0 (wall front edge):
- Lip A: Y_start=0.0mm, Y_width=2.0mm → lip outer face at Y=0, inner face at Y=2.0mm. Channel outer edge at Y=2.0mm.
- Channel: Y=2.0 to Y=5.4mm (width 3.4mm)
- Lip B: Y_start=5.4mm, Y_width=2.0mm → inner face at Y=5.4, outer face at Y=7.4mm.
- Panel occupies Y=2.2 to Y=5.2mm (3mm panel with 0.2mm clearance each side within 3.4mm channel).
- Panel inner face at Y=5.2mm. Use Y=5.0mm as nominal (clearance is in the channel width, not a hard position offset). Let's say front panel inner face = Y=5.0mm.

Front panel rail lip positions (in wall Y):
- Lip A: Y=0.0..2.0mm, runs full Z extent where panel travels (Z=5.4 to Z=WALL_Z-something)
- Lip B: Y=5.4..7.4mm, same Z extent

Actually, the lip runs along the Z slide direction. The panel slides in from Z=WALL_Z (top) downward. It seats at some Z position (the bottom of its travel). For Phase 7, rails go the full available Z length. Rail Z extent: Z=0 to Z=WALL_Z (full height) — the full slide channel.

**Back Panel Rail** — panel slides in -Z direction (same as front panel)

Back panel outer face at Y=WALL_Y (flush with wall rear edge). Panel occupies Y=(WALL_Y-3.0) to Y=WALL_Y.

- Lip A (inner lip): inner face at Y=WALL_Y-3.0-0.4=-3.4+WALL_Y... Let me define from the back:
- Lip B: Y=WALL_Y-2.0..WALL_Y (outer lip, at wall rear edge)
- Channel: Y=WALL_Y-5.4 to Y=WALL_Y-2.0 (width 3.4mm)
- Lip A: Y=WALL_Y-7.4 to Y=WALL_Y-5.4

Panel occupies channel Y=(WALL_Y-5.2) to Y=(WALL_Y-2.2). Panel inner face at Y=WALL_Y-5.0 (nominal).

Back panel rail lip positions:
- Lip A: Y=(WALL_Y-7.4) to Y=(WALL_Y-5.4), runs full Z extent
- Lip B: Y=(WALL_Y-2.0) to Y=WALL_Y, runs full Z extent

**Interior Y depth** = front panel inner face to back panel inner face:
= (WALL_Y - 5.0) - 5.0 = WALL_Y - 10.0

Required interior Y = 123.0mm → WALL_Y = 133.0mm.

Use **WALL_Y = 133.0mm**.

Interior Y: Y=5.0mm to Y=128.0mm (123.0mm span).

Verify pump layout in interior Y (measured from inner face of front panel = Y=5.0 in wall coordinates):
- Front panel inner face: Y_wall=5.0mm
- Front zone (pump head + mechanism): 50.0mm
- Pump tray front face: Y_wall = 5.0 + 50.0 = 55.0mm
- Pump tray: Y_wall = 55.0 to 58.0mm (3mm thick)
- Rear zone: 70.0mm
- Rear zone end: Y_wall = 58.0 + 70.0 = 128.0mm = back panel inner face. ✓

---

**Bottom Panel Rail** — panel slides in +Y direction (entering from cartridge front, Y=0, moving toward back)

Bottom panel outer face at Z=0 (flush with wall bottom edge). Panel occupies Z=0..3.0mm.

- Lip A: Z=0..2.0mm (at wall bottom edge)
- Channel: Z=2.0..5.4mm
- Lip B: Z=5.4..7.4mm

Panel inner face at Z=5.0mm (nominal).
Bottom panel rail lips run along Y (the slide direction), full Y extent.

**Top Panel Rail** — panel slides in -Z direction (entering from above)

Top panel outer face at Z=WALL_Z. Panel occupies Z=(WALL_Z-3.0) to Z=WALL_Z.

- Lip B: Z=(WALL_Z-2.0)..WALL_Z (at wall top edge)
- Channel: Z=(WALL_Z-5.4) to Z=(WALL_Z-2.0)
- Lip A: Z=(WALL_Z-7.4) to Z=(WALL_Z-5.4)

Panel inner face at Z=WALL_Z-5.0mm (nominal).
Top panel rail lips run along Y (panel slides in Z, so... wait, top panel slides in Z direction from above).

Actually, top panel slides in -Z direction (from above). The rail lips run along Y (the full Y extent of the wall), separating in Z with a 3.4mm gap. The panel slides in and moves in the -Z direction until seated.

Top panel rail lips run along Y direction, at fixed Z positions. Full Y extent.

**Interior Z height** = top panel inner face to bottom panel inner face:
= (WALL_Z - 5.0) - 5.0 = WALL_Z - 10.0

Required interior Z = 68.6mm → WALL_Z = 78.6mm.

Use **WALL_Z = 78.6mm**.

Interior Z: Z=5.0mm to Z=73.6mm (68.6mm span). ✓

---

**Pump Tray Rail** — plate slides in +Y direction (from front, entering at Y_front)

Pump tray is 3.0mm thick in Y, 68.6mm tall in Z. The rail channel is in Y-Z plane on the interior face; the plate slides in from the front (Y direction). Rail lips run along Y (full Y travel), separated by 3.4mm in Z.

The plate must span the full interior Z = 68.6mm. The plate bottom edge is at Z=5.0mm (interior Z bottom), top edge at Z=73.6mm (interior Z top).

Rail channel Z center at Z = (5.0 + 73.6)/2 = 39.3mm. Channel spans Z=5.0mm to Z=5.0+3.4=8.4mm and Z=73.6-3.4=70.2mm to Z=73.6mm? No — the channel grips the plate at its top and bottom edges (two separate rail pairs: one at bottom of plate, one at top of plate).

One rail grips the bottom edge of the plate, another grips the top edge:

Bottom pump tray rail:
- Plate bottom edge at Z=5.0mm (inner face of bottom panel), plate bottom face at Z=5.0mm
- Channel centered at plate bottom: Z=5.0 - 0.2 to Z=5.0 + 3.2mm → channel Z=4.8 to 8.2mm, but plate sits at Z=5.0..5.0 (it's an edge, not a side).

Wait — the interior plates slide in rails that grip their top and bottom EDGES (in Z). The rail channel is horizontal (Z-direction gap) and the plate slides in through the channel opening (in the Y direction). The plate bottom edge slides along one channel groove, the plate top edge slides along another.

For pump tray bottom rail:
- Plate bottom edge at Z=5.0mm (interior Z bottom)
- The groove opens toward the interior (toward the viewer from inside). The plate edge is 3mm thick in Y. The rail channel runs in Y (plate travels in Y), 3.4mm wide in Y (for the 3mm plate thickness).
- Two lips run in Y, one at Z just below the plate bottom edge, one at Z just above it.
  - Lip below (in Z): lip top face at Z=5.0mm (touching plate bottom face), lip runs from Z=2.0mm to Z=5.0mm (3mm lip height in Z)...

I'm conflating the rail orientation. Let me be precise.

**Pump tray rail orientation:** The pump tray plate is in the YZ plane, 3mm thick in X (same as all interior plates). It slides in the Y direction. The rail grips the plate's X faces (front face at X=0, back face at X=3.0mm of plate). So the channel is in X: gap of 3.4mm in X, plate slides through in Y.

Wait, re-reading the brief: "Interior plate footprint: 140.0mm wide (X) × 68.6mm tall (Z) × 3.0mm thick (Y)." So the interior plates are 3.0mm thick in Y — they span X=0..140mm and Z=0..68.6mm when seated, and their thickness is in Y. They slide in the Y direction into the wall rails.

The rail on the left wall grips the LEFT EDGE of the plate (the plate's X=0 edge). The left wall interior face is at X=3.0mm (WALL_T=3mm). The rail lips protrude from X=3.0mm inward toward X=6.0mm. The plate's left edge is at X=0 in plate-local coordinates, which in cartridge X corresponds to... the inner face of the left wall = X=3.0mm of wall = cartridge X=3.0mm. So the left edge of each interior plate is adjacent to the left wall interior face.

The rail on the left wall (and symmetrically on the right wall) grips the top and bottom edges of the plate (in Z), NOT the left edge. The plate slides in from the front (in Y), and the rail lips above and below the plate top/bottom edges keep the plate aligned in Z as it slides.

So for the pump tray:
- Plate top edge at Z=73.6mm (interior Z top = inner face of top panel)
- Plate bottom edge at Z=5.0mm (interior Z bottom = inner face of bottom panel)
- Rail channel at plate BOTTOM EDGE: two lips (one at Z slightly below plate bottom, one slightly above), running full Y length → but this puts one lip BELOW Z=5.0mm, interfering with the bottom panel space.

Cleaner: the interior plates are contained by the bottom and top panel inner faces (they fit exactly: 68.6mm plate height into 68.6mm interior Z). The top and bottom panels themselves provide vertical constraint. The left/right wall rails only need to constrain the plate in the X direction (against the wall face). The rail channel provides X retention and Y slide guidance.

So the rail for interior plates: channel grips the plate in the Z direction (top and bottom edges) OR in the X direction. Given the plate is 3mm thick in Y and spans X=0..140mm and Z=0..68.6mm, the only face adjacent to the left wall is the plate's left face (the face at X=0 in plate coordinates, the X=3.0mm plane in wall coordinates). The wall provides a flat face for this. To keep the plate from moving in Z and X, use rails that capture the plate's front/back faces (in Y) — i.e., channel width 3.4mm in Y — and the lips run along Y (slide direction) at fixed Z positions.

That means the rail channel on the left wall:
- Is oriented with lips running in Y (slide direction of plate)
- Channel width is 3.4mm in Z (capturing the plate's top and bottom edges at Z=5.0mm and Z=73.6mm)
- Wait, "capturing the top and bottom edges" means one rail at the plate top edge and one at the plate bottom edge, each rail being a channel that runs in Y.

So for the pump tray: TWO rail channels on the left wall — one at the plate bottom edge, one at the plate top edge. Each channel grips the plate at that Z location, with lips in the Z direction (above and below the plate edge at that Z position):

Bottom-edge rail for pump tray:
- Plate bottom face at Z=5.0mm.
- Channel: plate slides in Y. Channel runs along Y. Channel gap = 3.4mm in Z (plate is 3mm thick in Y... wait, I keep confusing axes).

OK, let me be completely explicit. The pump tray plate:
- Wide axis: X (140mm)
- Tall axis: Z (68.6mm)
- Thin axis: Y (3mm)
- Slides: in Y direction (enters from Y=small, moves toward Y=large)

The rail on the LEFT WALL grips the plate's left edge (the strip of plate at X≈3mm, the left wall). The rail lips need to be on the left wall interior face (at X=3mm) protruding inward (+X direction). But the plate's left edge — this is just the leftmost 3mm-thick strip of the plate. The left wall interior face touches the plate left face (the face at X=3mm). The rail keeps the plate in X.

To retain the plate in Z while it slides in Y, the rail lips need to capture the plate's Z extent. The appropriate configuration:

- Two lip bars on the left wall interior face, running in Y (parallel to slide direction), one positioned near the plate BOTTOM edge and one near the plate TOP edge.
- Each lip has width 2.0mm in Z and height 3.0mm in X (protrusion into interior).
- The channel between lips is 3.4mm in Z, with the plate edge (3mm thick in Y, not in Z) fitting into it.

But the plate doesn't have a Z-direction "tab" — the plate spans the full Z from 5mm to 73.6mm. The rail at the bottom captures the bottom edge of the plate, at the top captures the top edge. This means two separate rails per plate:

**Pump tray bottom rail** (Z position = inner face of bottom panel = Z=5.0mm):
- Lips run in Y direction
- Lip A: Z = 5.0 - 2.0 = 3.0 to Z=5.0mm (below plate bottom edge)
- Channel: Z=5.0 to Z=8.4mm (3.4mm channel, plate bottom edge at Z=5.0..8.0mm — wait, the plate bottom edge IS at Z=5.0mm, it's a face, not a feature that fits in a channel)

I think I have been overcomplicating this. Let me reread the brief:

"A rail is two parallel lips protruding from the interior face, forming a channel. The panel or plate slides into the channel in the direction the lips are aligned."

So the PANEL slides INTO the channel. The channel is formed by two lips. The lips are parallel and the panel slides between them in the direction they run.

For the front panel (3mm thick in Y, slides in Z direction):
- The panel's Y faces are the faces that go into the channel.
- The channel is 3.4mm wide in Y (gripping the panel's front/back faces).
- Two lips run along Z (so the panel slides in Z between them).
- Lips are separated by 3.4mm in Y.
- This rail is positioned at the Y location of the front panel.

For the pump tray (3mm thick in Y, slides in Y direction):
- The plate's Z faces (top and bottom) go into channels... no, that doesn't make sense either.
- Actually: the pump tray slides into the channel in the Y direction. The channel runs in Y (lips aligned in Y). The channel grips the plate in... what direction? The channel must constrain the plate in Z.
- So: lips run in Y, channel width is 3.4mm in Z. The plate's top or bottom edge (3mm thick in Y) fits into this 3.4mm Z channel.
- This means the plate's TOP EDGE slides into a top-edge channel, and the plate's BOTTOM EDGE slides into a bottom-edge channel.
- Each edge is 3mm (in Y, the plate thickness) and the channel is 3.4mm in Z...

No — "the panel slides into the channel in the direction the lips are aligned." The lips are aligned in Y (they run in Y). The panel slides in Y. The channel constrains the panel in Z (the 3.4mm gap is in Z). The panel edge (3mm thin in Y) goes into this gap.

So the plate's 3mm Y-thickness becomes the edge that slides in. The channel is 3.4mm in Z, meaning the distance between the two lips (in Z) = 3.4mm. The plate's top edge (3mm Y thick) or bottom edge slides between these lips.

One rail at the plate bottom edge (Z=5.0mm):
- Lip A at Z = 5.0 - 1.7 = 3.3mm (bottom lip)
- Lip B at Z = 5.0 + 1.7 = 6.7mm (top lip)
- Channel between them: Z=3.3 + 2.0 (lip width) = 5.3mm...

I'll simplify: position Lip A so its top face (inner edge of channel) is at Z=Z_plate_bottom, and Lip B so its bottom face (other inner edge of channel) is at Z=Z_plate_bottom + 3.4mm.

Wait — "two parallel lips protruding from the interior face, forming a channel." The channel width is the gap BETWEEN the lips. The panel slides between the lips.

For pump tray bottom-edge rail (plate bottom edge at Z=5.0mm in interior coordinates, which is Z=5.0mm in wall coordinates):
- Lip A (lower lip): top face at Z=5.0mm - 3.4mm/2 + 3.4mm/2... Let me just use:
  - Lip A bottom face at Z = 5.0 - 3.4/2 - 2.0/2 = 5.0 - 1.7 - 1.0 = 2.3mm
  - Lip A top face at Z = 5.0 - 3.4/2 + 0 = ...

OK I will just pick concrete numbers. The plate bottom edge (Z=5.0mm interior) is gripped by a channel centered at Z=5.0mm:
- Lip A (lower): occupies Z = 5.0 - 3.4/2 - LIP_W = 5.0 - 1.7 - 2.0 = 1.3mm to Z = 5.0 - 3.4/2 = 5.0 - 1.7 = 3.3mm
- Channel gap: Z = 3.3mm to Z = 6.7mm (width = 3.4mm). Plate edge fits in here.
- Lip B (upper): Z = 6.7mm to Z = 6.7 + 2.0 = 8.7mm

But Lip A starts at Z=1.3mm and the bottom panel inner face is at Z=5.0mm. The lip at Z=1.3..3.3mm is in the bottom panel zone. This is fine — the lip goes on the left wall interior face regardless of what other panels are there (they're separate parts).

This is getting quite detailed for a parts.md. Let me define numbers concisely with a table.

---

## Definitive Dimensions

All dimensions below are in wall-local coordinates:
- Origin at wall front-bottom-exterior corner (X=0, Y=0, Z=0)
- X: exterior face (X=0) to interior face (X=WALL_T)
- Y: front (Y=0) to back (Y=WALL_Y)
- Z: bottom (Z=0) to top (Z=WALL_Z)

**Wall body:**
- WALL_T = 3.0mm (X thickness)
- WALL_Y = 133.0mm (Y depth, front to back)
- WALL_Z = 78.6mm (Z height, bottom to top)

**Interior face:** X=3.0mm

**Interior panel clearances:**
- All panels/plates: 3.0mm nominal thickness
- Channel width (rail gap): 3.4mm (0.2mm clearance per side)
- LIP_H = 3.0mm (lip protrusion from interior face, in +X)
- LIP_W = 2.0mm (lip width in direction perpendicular to slide)

**Interior coordinate frame (relative to left wall origin):**
- Interior X: X=3.0mm (interior face) to X=3.0mm (it's just a face; interior extends to right wall)
- Interior Y: Y=5.0mm (inner face of front panel) to Y=128.0mm (inner face of back panel) — 123.0mm span
- Interior Z: Z=5.0mm (inner face of bottom panel) to Z=73.6mm (inner face of top panel) — 68.6mm span

---

## Rail Feature Table

All rail lips are rectangular bars. Position given as (Y_start, Z_start) with dimensions (LIP_W × run_length × LIP_H). Lips protrude from X=WALL_T=3.0mm in +X direction to X=WALL_T+LIP_H=6.0mm.

"Run direction" = the axis the lips run along (the slide direction of the panel/plate).
"Separation axis" = the axis perpendicular to the slide direction in which the lips are separated by 3.4mm.

| # | Rail Name             | Slide Dir | Sep Axis | Lip A Position (Y,Z)       | Lip B Position (Y,Z)       | Run Length | Notes |
|---|-----------------------|-----------|----------|----------------------------|----------------------------|------------|-------|
| 1 | Front panel           | Z (down)  | Y        | Y=0.0..2.0mm               | Y=5.4..7.4mm               | Z=0..78.6  | Panel sits at Y≈2..5mm |
| 2 | Back panel            | Z (down)  | Y        | Y=125.6..127.6mm           | Y=131.0..133.0mm           | Z=0..78.6  | Panel sits at Y≈127.6..130.6mm |
| 3 | Bottom panel          | Y (back)  | Z        | Z=0.0..2.0mm               | Z=5.4..7.4mm               | Y=0..133.0 | Panel sits at Z≈2..5mm |
| 4 | Top panel             | Z (down)  | Y        | top lip region             | see below                  | Y=0..133.0 | Last assembled |
| 5 | Pump tray (bottom edge) | Y (back) | Z       | Z=1.3..3.3mm               | Z=6.7..8.7mm               | Y=0..133.0 | Plate bottom edge at Z=5.0mm interior |
| 6 | Pump tray (top edge)  | Y (back)  | Z        | Z=69.9..71.9mm             | Z=75.3..77.3mm             | Y=0..133.0 | Plate top edge at Z=73.6mm interior |
| 7 | Coupler tray (bottom) | Y (back)  | Z        | same as pump tray bottom   | same as pump tray bottom   | Y=0..133.0 | Same rail, shared with pump tray |
| 8 | Coupler tray (top)    | Y (back)  | Z        | same as pump tray top      | same as pump tray top      | Y=0..133.0 | Same rail, shared with pump tray |

**Note:** Pump tray and coupler tray both have the same plate footprint (140mm × 68.6mm × 3mm), so they share the same rail channel. One set of rails serves both plates.

**Top panel rail:** Top panel slides in from above (-Z direction). Panel outer face at Z=WALL_Z=78.6mm, inner face at Z=75.6mm. Rail:
- Lip A: Z=73.2..75.2mm (lower lip, channel bottom at Z=75.2mm)
- Channel: Z=75.2..78.6mm (3.4mm)
- Lip B: Z=78.6mm is the wall top face — Lip B is at Z=76.6..78.6mm

Panel inner face at Z=75.6mm. Wait: channel Z=75.2..78.6mm, panel 3.0mm sits at Z=75.4..78.4mm (0.2mm clearance each side). Inner face of top panel = Z=75.4mm. Interior Z = 75.4 - 5.0 = 70.4mm... too tall.

Let me re-derive WALL_Z from required interior height = 68.6mm:

Interior Z: from bottom panel inner face to top panel inner face = 68.6mm.
Bottom panel inner face at Z=5.0mm (from earlier: Lip A Z=0..2mm, channel Z=2..5.4mm, panel inner face at ~5.0mm nominal).
Top panel inner face at Z = 5.0 + 68.6 = 73.6mm.

Top panel: 3mm thick, inner face at Z=73.6mm, outer face at Z=76.6mm.
Top panel rail: channel centered at Z=75.1mm (center of 3mm panel):
- Channel: Z=73.9 to Z=77.3mm (3.4mm wide, centered on panel center 75.1mm → 75.1-1.7=73.4 to 75.1+1.7=76.8mm).

Simpler: just say Lip A inner edge at Z=73.6mm, Lip B inner edge at Z=73.6+3.4=77.0mm.
- Lip A: Z=71.6..73.6mm (top face = channel bottom = Z=73.6mm)
- Channel: Z=73.6..77.0mm (3.4mm gap)
- Lip B: Z=77.0..79.0mm (bottom face = channel top = Z=77.0mm)

WALL_Z must accommodate Lip B top at Z=79.0mm. Use **WALL_Z = 79.0mm**.

Re-check bottom panel: Lip A Z=0..2mm, Channel Z=2..5.4mm, Lip B Z=5.4..7.4mm. Bottom panel inner face = Z=5.0mm (panel at Z=2.0+0.2=2.2 to 5.2mm with clearance, nominal inner face 5.0mm). ✓

**Revised WALL_Z = 79.0mm.**

Re-check pump tray top rail with WALL_Z = 79.0mm:
Plate top edge at Z = 5.0 + 68.6 = 73.6mm (= interior Z top = top panel inner face).
Pump tray top edge rail:
- Lip A: Z=71.6..73.6mm (below plate top edge, channel bottom at Z=73.6mm)
- Channel: Z=73.6..77.0mm
- Lip B: Z=77.0..79.0mm

This is the same as the top panel rail lips (Lip A = Z=71.6..73.6mm, channel=73.6..77.0mm, Lip B=77.0..79.0mm). The pump tray top edge and the top panel SHARE the same geometric rail position. This makes sense — the top panel inner face (Z=73.6mm nominal) is also where the plate top edge seats. The top panel and the pump tray plate enter the same channel zone.

But functionally they are different: the top panel slides in Z, the pump tray slides in Y. They don't conflict because the top panel is installed AFTER the pump tray (top panel is last). The rail geometry can serve both motions at the same corner location.

---

## Final Rail Positions (Canonical)

Using these final dimensions: WALL_T=3.0mm, WALL_Y=133.0mm, WALL_Z=79.0mm.

Lips protrude from X=3.0mm to X=6.0mm (LIP_H=3.0mm in +X).
Lip width (LIP_W) = 2.0mm.

**Front panel rail** (panel slides in -Z, gripped in Y at front of wall):
- Lip A: Y=0.0..2.0mm, runs Z=0..79.0mm
- Lip B: Y=5.4..7.4mm, runs Z=0..79.0mm

**Back panel rail** (panel slides in -Z, gripped in Y at back of wall):
- Lip A: Y=125.6..127.6mm, runs Z=0..79.0mm
- Lip B: Y=131.0..133.0mm, runs Z=0..79.0mm

**Bottom panel rail** (panel slides in +Y, gripped in Z at bottom of wall):
- Lip A: Z=0.0..2.0mm, runs Y=0..133.0mm
- Lip B: Z=5.4..7.4mm, runs Y=0..133.0mm

**Top panel rail** (panel slides in -Z, gripped in Y at top of wall; ALSO serves as pump tray / coupler tray top edge rail):
- Lip A: Z=71.6..73.6mm, runs Y=0..133.0mm
- Lip B: Z=77.0..79.0mm, runs Y=0..133.0mm

**Pump tray / coupler tray bottom-edge rail** (plates slide in +Y, gripped in Z near bottom):
- Lip A: Z=1.3..3.3mm, runs Y=0..133.0mm
- Lip B: Z=6.7..8.7mm, runs Y=0..133.0mm

**Pump tray / coupler tray top-edge rail** (same as top panel rail above):
- Lip A: Z=71.6..73.6mm, runs Y=0..133.0mm
- Lip B: Z=77.0..79.0mm, runs Y=0..133.0mm

**Total distinct rail lip bars: 10** (front panel: 2, back panel: 2, bottom panel: 2, top panel / plate top rail: 2, plate bottom rail: 2).

---

## Print Orientation

Print with exterior face (X=0) down on build plate. The interior face (X=3.0mm) is up, with rail lips protruding upward (+Z on build plate = +X in wall coordinates). This puts the wall body flat on the plate with lip bars pointing up — no overhangs. Rail lips print as upright bars, no overhangs. All features are FDM-compatible in this orientation.

Wall body dimensions on build plate: 79.0mm (wall Z) × 133.0mm (wall Y). Well within build area.

---

## Interface Summary

| Interface | Mating Part | Rail Grips |
|-----------|-------------|------------|
| Front panel | Front panel (future) | Y direction at Y≈2..5mm |
| Back panel | Back panel (future) | Y direction at Y≈128..131mm |
| Bottom panel | Bottom panel (future) | Z direction at Z≈2..5mm |
| Top panel | Top panel (future) | Z direction at Z≈74..77mm |
| Pump tray | Pump tray | Z direction at bottom (Z≈5mm) and top (Z≈74mm) edges |
| Coupler tray | Coupler tray | Same rails as pump tray |
