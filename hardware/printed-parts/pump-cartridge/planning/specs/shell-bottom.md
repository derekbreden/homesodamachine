# Shell Bottom -- Parts Specification

The primary structural piece of the pump cartridge. An open-top box (174 mm wide x 200 mm deep x 39 mm tall) that contains: the bottom wall, lower side walls with integral T-rail profiles, two link rod channels with six guide bushings, the lower portion of the front wall and inset panel recess, a rear pocket for the rear wall plate, four mounting plate locating slots, twelve snap-fit hooks along the top rim, and a continuous step joint lip for mating with the shell top.

Material: PETG (matte black). Single printed piece, no fasteners, no inserts.

---

## Coordinate System

Origin: lower-left-rear corner of the exterior bounding box.

- **X axis**: width (left to right), 0..174 mm.
- **Y axis**: depth (rear to front), 0..200 mm.
- **Z axis**: height (bottom to top), 0..39 mm.

Print orientation: open side up (Z = 0 on build plate, interior facing up). Installed orientation is identical -- no rotation required.

---

## Mechanism Narrative

### What the user sees and touches

The shell bottom is the lower half of the cartridge enclosure. When the cartridge is assembled, the user sees the bottom wall (flat, featureless) and the lower halves of the front face, side faces, and rear face. When the cartridge is in the dock, only the lower portion of the front face is visible. The user's palm rests on the front face during the squeeze gesture, with the lower portion of the front face contributing to the palm bearing surface.

The bottom face is not visible when the cartridge is in the dock. The side faces show T-rail grooves -- subtle 6 mm deep x 8 mm tall geometric accents running front-to-back. The front face is flat with the lower 15 mm of the inset release panel recess visible (the recess spans the shell seam).

### What moves

**Nothing in the shell bottom moves.** The shell bottom is entirely static. It serves as the rigid structural chassis for all moving parts (link rods, release plate, inset panel) which are separate pieces that slide within features molded into the shell bottom.

Stationary parts contained/supported by the shell bottom:
- Bottom wall (floor)
- Side walls with T-rail profiles
- Front wall with lower recess pocket
- Rear pocket structure (receives rear wall plate)
- Link rod channel walls and guide bushings
- Mounting plate locating slots
- Snap-fit hooks and step joint lip

### What converts the motion

Not applicable -- the shell bottom has no moving parts. It provides the guide surfaces (bushings, channels, recess walls) that constrain the motion of other parts.

### What constrains each moving part (that the shell bottom guides)

**Link rods (3 mm steel):** Each rod slides through three guide bushings (3.2 mm bore ID, 6 mm boss OD, 8 mm boss length) at Y = 18, Y = 85, and Y = 188. The 0.2 mm diametral clearance (3.2 mm bore minus 3.0 mm rod) permits axial sliding while preventing lateral wobble. The U-channel walls (6 mm outer width, 4 mm inner opening, running Z = 3..7) prevent the rods from dropping out of the bushing plane.

**Inset release panel:** The lower portion of the recess (X = 42..132, Y = 195..200, Z = 24..39) constrains the panel's lower edge in X and Z. The recess side walls (0.2 mm clearance per side) and floor (recess bottom at Z = 24) prevent the panel from tilting or shifting laterally. The panel translates only in Y (rearward, toward -Y) by up to 3 mm.

**Mounting plate:** Four locating slots (3 mm deep into each side wall, 5 mm wide in Y, 5 mm tall in Z) at Y = 82.5..87.5 receive the plate's tabs. The snug fit (0.1 mm clearance per side) prevents the plate from shifting in Y or Z. The plate is captured in X when the shell top closes, sandwiching the plate tabs between the bottom and top shell slots.

**Rear wall plate:** A rectangular pocket (Y = 0..15, X = 13..161, Z = 4..38) with 1 mm lips on all four edges holds the plate. Four corner snap tabs (4 mm wide, 1 mm protrusion, 45-degree chamfer) retain the plate against rearward forces during tube insertion.

### What provides the return force

Not applicable -- the shell bottom is static and has no rest-position mechanism. Return forces for the link rods and release plate are provided by the compression springs on the guide pins in the rear wall plate (separate part).

### What is the user's physical interaction

The user does not interact with the shell bottom directly during cartridge operation. During factory assembly, the user handles the shell bottom as the primary assembly chassis:

1. Place shell bottom on work surface (open side up, bottom wall flat on table).
2. Drop rear wall plate into rear pocket (Y = 0..15) until four corner snaps click. The 45-degree chamfer on each snap tab guides the plate past the 1 mm lip. Tactile feedback: four small clicks at corners (X = 16, Z = 7) and (X = 158, Z = 7) and (X = 16, Z = 35) and (X = 158, Z = 35).
3. Thread link rods through guide bushings and connect to release plate and inset panel (subassembly).
4. Slide inset panel into front recess (panel enters from above since shell is open-top).
5. Place vertical mounting plate into locating slots (tabs register into the 3 mm deep x 5 mm wide x 5 mm tall slots at Y = 82.5..87.5).
6. Install pumps onto mounting plate (from the front/pump head side).
7. Route tubing from pump barbs rearward to JG fittings in rear wall plate.
8. Route motor wiring along bottom of cartridge to pogo pads on rear wall plate.
9. Close shell top onto shell bottom. Press down until 12 snap-fit hooks engage (4 per long side, 2 per short side). The 45-degree lead-in chamfers on the hooks guide the shell top past the 0.5 mm retention shoulders. Tactile feedback: 12 clicks.

---

## Constraint Chain

```
[Static structure]

Shell bottom (rigid box)
  |
  |--> T-rail profiles (left & right side walls)
  |      ^ constrained by: integral to side walls (no relative motion)
  |      -> engages: dock bay channels (0.2 mm sliding clearance per side)
  |
  |--> Link rod channels + bushings (bottom interior)
  |      ^ constrained by: integral to bottom wall (no relative motion)
  |      -> guides: 3 mm steel link rods (0.2 mm diametral clearance in 3.2 mm bores)
  |
  |--> Rear pocket (Y = 0..15)
  |      ^ constrained by: integral to shell walls
  |      -> captures: rear wall plate (1 mm lip + 4x corner snap tabs)
  |
  |--> Mounting plate locating slots (Y = 82.5..87.5)
  |      ^ constrained by: integral to side walls
  |      -> positions: vertical mounting plate (0.1 mm snug fit per side)
  |
  |--> Front recess (Y = 195..200, lower portion)
  |      ^ constrained by: integral to front wall
  |      -> guides: inset release panel (0.2 mm clearance per side, Y translation only)
  |
  |--> Snap-fit hooks (Z = 39..42, 12 total)
  |      ^ constrained by: integral to top rim
  |      -> retains: shell top (0.5 mm retention shoulder)
  |
  |--> Step joint lip (Z = 39..39.5, outer perimeter)
         ^ constrained by: integral to outer wall top edge
         -> aligns: shell top (0.1 mm gap target)
```

No arrows are unlabeled. No force transmission occurs through the shell bottom -- it is passive structure. All forces are reacted through rigid geometry.

---

## Part Geometry

### Overall Envelope

| Parameter | Value |
|-----------|-------|
| Outer X extent | 174 mm |
| Outer Y extent | 200 mm |
| Outer Z extent | 39 mm |
| Bottom wall thickness | 3 mm (Z = 0..3) |
| Side wall zone thickness (including T-rail) | 12 mm per side |
| Structural wall thickness (X) | 6 mm per side |
| Front wall thickness (Y) | 15 mm (Y = 185..200) |
| Interior clear width (X) | 150 mm (X = 12..162) |
| Interior clear depth (Y) | 170 mm (Y = 15..185) |

### Side Walls and T-Rail Profiles

Each side wall is a 12 mm thick zone running the full depth (Y = 0..200) and full height (Z = 0..39). The T-rail is integral to the outer face.

**Left side wall cross-section (constant along Y except at lead-in taper):**

| Feature | X range (mm) | Z range (mm) | Size |
|---------|-------------|-------------|------|
| Crossbar | 0..2 | 16..24 | 2 mm thick (X) x 8 mm tall (Z) |
| Stem | 2..6 | 18..22 | 4 mm deep (X) x 4 mm wide (Z) |
| Upper groove | 0..6 | 24..39 | Open channel above crossbar |
| Lower groove | 0..6 | 0..16 | Open channel below crossbar |
| Structural wall | 6..12 | 0..39 | 6 mm thick solid wall |

T-rail center: Z = 20 mm.

**Crossbar underside chamfers:** 45-degree x 2 mm chamfers on both inner faces of the crossbar where it overhangs the stem (at crossbar-to-stem transitions). These chamfers eliminate the overhang that would otherwise be unprintable. The chamfer runs the full Y length of the rail. The chamfered faces are non-functional (the dock channel engages the crossbar top surface, bottom surface, and outer face -- not the inner chamfered faces).

**Right side wall:** Mirror of left about X = 87.

| Feature | X range (mm) | Z range (mm) |
|---------|-------------|-------------|
| Structural wall | 162..168 | 0..39 |
| Stem | 168..172 | 18..22 |
| Crossbar | 172..174 | 16..24 |
| Upper groove | 168..174 | 24..39 |
| Lower groove | 168..174 | 0..16 |

**T-rail lead-in taper (front 15 mm):**

The crossbar tapers from 6 mm to 8 mm width over Y = 185..200, providing a centering funnel for dock insertion.

| Y position (mm) | Crossbar Z range | Crossbar width (Z) |
|-----------------|-----------------|---------------------|
| 200 (front tip) | 17..23 | 6 mm |
| 192 | 16.5..23.5 | 7 mm |
| 185 | 16..24 | 8 mm (full profile) |
| 185..0 | 16..24 | 8 mm (constant) |

The stem width remains 4 mm throughout the taper. Only the crossbar narrows toward the front.

### Link Rod Channels and Guide Bushings

Two U-shaped channels on the interior floor, running rear to front.

| Parameter | Rod 1 (left) | Rod 2 (right) |
|-----------|-------------|---------------|
| Center X | 57 mm | 117 mm |
| Spacing | 60 mm (symmetric about X = 87) |
| Y range | 15..185 mm |
| Z range | 3..7 mm (4 mm tall) |

**Channel cross-section:**

| Feature | Dimension |
|---------|-----------|
| Outer width (X) | 6 mm |
| Inner opening (X) | 4 mm |
| Wall thickness | 1 mm per side |
| Depth (Z) | 4 mm (Z = 3..7) |

**Guide bushings (6 total, 3 per rod):**

| Bushing | Center X (mm) | Center Y (mm) | Center Z (mm) | Context |
|---------|--------------|---------------|---------------|---------|
| Front-L | 57 | 188 | 5 | In front wall structure |
| Mid-L | 57 | 85 | 5 | At mounting plate Y |
| Rear-L | 57 | 18 | 5 | Just inside rear pocket |
| Front-R | 117 | 188 | 5 | In front wall structure |
| Mid-R | 117 | 85 | 5 | At mounting plate Y |
| Rear-R | 117 | 18 | 5 | Just inside rear pocket |

| Bushing parameter | Value |
|-------------------|-------|
| Bore ID | 3.2 mm |
| Boss OD | 6 mm |
| Boss length (Y) | 8 mm |
| Bore center Z | 5 mm |

The boss OD (6 mm) matches the channel outer width, so the bosses are flush with the channel walls. Between bushing locations, the channels are open-top U-grooves. At bushing locations, the channel closes over to form the cylindrical bore.

### Front Wall

The front wall spans X = 12..162 at Y = 185..200 (15 mm thick).

| Zone | X range (mm) | Y range (mm) | Z range (mm) | Description |
|------|-------------|-------------|-------------|-------------|
| Solid wall (below recess) | 12..162 | 185..200 | 0..24 | Full-thickness structural wall |
| Recess pocket (lower portion) | 42..132 | 195..200 | 24..39 | 5 mm deep pocket from exterior face |
| Solid wall (beside recess, left) | 12..42 | 185..200 | 24..39 | Full-thickness flanking wall |
| Solid wall (beside recess, right) | 132..162 | 185..200 | 24..39 | Full-thickness flanking wall |

**Inset panel recess (shell bottom portion):**

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Recess X range | 42..132 mm | 90 mm wide, centered at X = 87 |
| Recess Z range | 24..39 mm | Lower 15 mm of 30 mm full recess (full recess: Z = 24..54) |
| Recess Y range | 195..200 mm | 5 mm deep from outer face |
| Wall behind recess | 10 mm (Y = 185..195) | Structural wall behind pocket |
| Bottom edge radius | 2 mm | Finger comfort at Z = 24 |
| Side edge radius | 0.5 mm | Crisp visual boundary |

**Link rod pass-throughs in front wall:** Two clearance holes at (X = 57, Z = 5) and (X = 117, Z = 5), bore ID = 3.2 mm, passing through the 10 mm structural wall (Y = 185..195). These connect the guide bushings (at Y = 188) to the recess zone (Y = 195..200) where the inset panel attaches to the rods.

### Rear Pocket

A rectangular pocket at the rear face (Y = 0) receives the rear wall plate.

| Parameter | Value |
|-----------|-------|
| Pocket opening X range | 13..161 mm (148 mm wide) |
| Pocket opening Z range | 4..38 mm (34 mm tall) |
| Pocket depth (Y) | 15 mm (Y = 0..15) |
| Lip width (all edges) | 1 mm |
| Left lip X | 12..13 |
| Right lip X | 161..162 |
| Bottom lip Z | 3..4 |
| Top lip Z | 38..39 |

**Corner snap tabs (4 total):**

| Corner | Center X (mm) | Center Z (mm) | Tab width | Tab protrusion (Y) | Chamfer |
|--------|--------------|---------------|-----------|---------------------|---------|
| Bottom-left | 16 | 7 | 4 mm | 1 mm | 45-degree on leading face |
| Bottom-right | 158 | 7 | 4 mm | 1 mm | 45-degree |
| Top-left | 16 | 35 | 4 mm | 1 mm | 45-degree |
| Top-right | 158 | 35 | 4 mm | 1 mm | 45-degree |

The snap tabs protrude inward from the lip face (in +Y direction) to engage matching chamfered edges on the rear wall plate.

### Mounting Plate Locating Slots

Four rectangular slots in the inner faces of the side walls, positioned at Y = 82.5..87.5 (centered on mounting plate plane at Y = 85).

| Slot | Wall | X range (mm) | Y range (mm) | Z range (mm) |
|------|------|-------------|-------------|-------------|
| Left-lower | Left inner face (X = 12) | 9..12 | 82.5..87.5 | 12..17 |
| Left-upper | Left inner face (X = 12) | 9..12 | 82.5..87.5 | 33..38 |
| Right-lower | Right inner face (X = 162) | 162..165 | 82.5..87.5 | 12..17 |
| Right-upper | Right inner face (X = 162) | 162..165 | 82.5..87.5 | 33..38 |

| Slot parameter | Value |
|----------------|-------|
| Depth into wall (X) | 3 mm |
| Width (Y) | 5 mm |
| Height (Z) | 5 mm |
| Fit clearance | 0.1 mm per side (tab: 2.8 x 4.8 x 4.8 mm) |

### Snap-Fit Hooks

Twelve hooks along the top rim at Z = 39 mm, protruding upward (into the shell top zone).

**Hook layout:**

| Wall | Hook count | Positions (mm) |
|------|-----------|----------------|
| Left side (inner face X = 12) | 4 | Y = 40, 80, 120, 160 |
| Right side (inner face X = 162) | 4 | Y = 40, 80, 120, 160 |
| Front wall (inner face Y = 185) | 2 | X = 62, 112 |
| Rear pocket edge (Y = 15) | 2 | X = 62, 112 |

**Hook cross-section (all hooks identical):**

| Feature | Dimension |
|---------|-----------|
| Hook base width (along wall) | 4 mm |
| Hook protrusion from wall face | 3 mm (inward) |
| Hook height above rim | 3 mm (Z = 39..42) |
| Hook lip undercut depth | 1 mm |
| Hook lip width (narrowest) | 1.2 mm |
| Lead-in chamfer (outer face) | 45-degree x 1 mm |
| Retention shoulder | 0.5 mm step on inner face |

**Sacrificial support nubs:** Each hook lip has a 0.2 mm interface-gap support nub below the 1 mm undercut. The nub sits at Z = 39 (the rim surface) and supports the hook lip overhang. It breaks away cleanly after printing, leaving the undercut face intact.

### Step Joint Lip

A continuous 0.5 mm tall x 1.5 mm wide lip on the outer perimeter of the top rim.

| Parameter | Value |
|-----------|-------|
| Lip height (Z) | 0.5 mm (Z = 39..39.5) |
| Lip width (X or Y) | 1.5 mm (outermost edge of wall top surface) |
| Extent | Full perimeter: left wall, front wall, right wall, rear wall top edges |
| Mating feature | Shell top has a matching 0.5 mm recess on its lower outer rim |
| Gap target | 0.1 mm |

The step joint is outboard of the snap-fit hooks. It provides visual seam concealment and self-alignment during assembly.

### Bottom Wall and Exterior Treatment

**Interior floor:** Flat at Z = 3 mm. Link rod channels sit on this surface (Z = 3..7).

**Elephant's foot chamfer:** 0.3 mm x 45-degree chamfer on all four bottom exterior edges (Z = 0 perimeter). This is the build-plate contact face.

**Exterior edge chamfers:** 1 mm chamfer on all non-bottom exterior edges:
- Four vertical corners of the box
- Top rim exterior edges at Z = 39 (except where step joint lip protrudes)

**T-rail groove edges:** Not chamfered -- these are functional mating surfaces.

---

## Interior Clearances

### Pump head zone (Y = 85..133)

Each pump head is ~62.6 mm x 62.6 mm, centered at (X, Z_cartridge) = (48.3, 40.3) and (125.7, 40.3).

| Direction | Pump 1 edge | Nearest feature | Clearance |
|-----------|-------------|-----------------|-----------|
| Left (-X) | X = 17.0 | Interior wall X = 12 | 5.0 mm |
| Right (+X) | X = 79.6 | Pump 2 left edge X = 94.4 | 14.8 mm |
| Down (-Z) | Z = 9.0 | Rod channel top Z = 7 | 2.0 mm |

Pump 2 clearances mirror pump 1 about X = 87.

### Motor zone (Y = 17..85)

Motors are ~35 mm diameter, centered on pump axes.

| Motor | Center X | Bottom edge Z | Clearance to rod channel (Z = 7) |
|-------|----------|--------------|----------------------------------|
| 1 | 48.3 | 22.8 | 15.8 mm |
| 2 | 125.7 | 22.8 | 15.8 mm |

Motor edge-to-wall clearance: 18.8 mm per side (generous space for wiring and tube routing).

### Tube routing zone (Y = 133..185)

Fully open. Clear cross-section: 150 mm wide x 36 mm tall (X = 12..162, Z = 3..39). The 25 mm minimum bend radius for BPT tubing is easily accommodated.

---

## Direction Consistency Check

| # | Claim | Direction | Axis | Verified? | Notes |
|---|-------|-----------|------|-----------|-------|
| 1 | Rear pocket receives rear wall plate at rear face | Rear face at Y = 0 | Y = 0 | Yes | Pocket opens at Y = 0, plate inserts from above (+Z), seats to Y = 0..15 |
| 2 | Front wall at front of cartridge | Front face at Y = 200 | Y = 200 | Yes | Front wall Y = 185..200, exterior face at Y = 200 |
| 3 | Link rods run rear to front | Along Y axis | Y = 15..185 | Yes | Channels span rear pocket to front wall |
| 4 | T-rails run front to back on side walls | Along Y axis | Y = 0..200 | Yes | Full depth, outer side faces |
| 5 | T-rail taper narrows toward front | Crossbar narrows at Y = 185..200 | +Y direction | Yes | 8 mm at Y = 185, 6 mm at Y = 200 |
| 6 | Snap-fit hooks protrude upward from rim | +Z direction | Z = 39..42 | Yes | Above seam line |
| 7 | Step joint lip protrudes upward | +Z direction | Z = 39..39.5 | Yes | 0.5 mm above rim |
| 8 | Mounting plate slots are cut into inner side wall faces | Into wall, -X on left, +X on right | X = 9..12 (left), 162..165 (right) | Yes | 3 mm into 6 mm structural wall |
| 9 | Rear pocket snap tabs protrude inward into pocket | +Y direction (from lip face) | +Y | Yes | Tabs at Y = 0 face protrude toward Y = 15 interior |
| 10 | Inset panel recess is 5 mm deep from outer face | Into wall, -Y direction | Y = 195..200 (pocket), Y = 200 outer | Yes | Panel sits 5 mm back from exterior |
| 11 | Crossbar chamfers on underside inner faces | Angled faces at stem-to-crossbar transition | 45-deg in XZ plane | Yes | Removes overhang at crossbar overhang |

No contradictions found.

---

## Interface Dimensional Consistency

| # | Interface | Part A dimension | Part B dimension | Clearance | Source |
|---|-----------|-----------------|-----------------|-----------|--------|
| 1 | Link rod bushing bore to steel rod | 3.2 mm bore ID | 3.0 mm rod OD | 0.2 mm diametral (0.1 mm per side) | requirements.md: 0.2 mm for sliding fits |
| 2 | T-rail crossbar to dock channel (Z) | 8 mm crossbar | 8.4 mm channel | 0.4 mm (0.2 mm per side) | requirements.md: 0.2 mm per side sliding fit |
| 3 | T-rail crossbar to dock channel (X) | 2 mm crossbar thickness | 2.4 mm slot depth | 0.4 mm (0.2 mm per side) | requirements.md |
| 4 | T-rail stem to dock channel (Z) | 4 mm stem | 4.4 mm channel | 0.4 mm (0.2 mm per side) | requirements.md |
| 5 | Mounting plate slot to tab (Y) | 5 mm slot | 4.8 mm tab | 0.2 mm (0.1 mm per side) | requirements.md: 0.1 mm snug fit |
| 6 | Mounting plate slot to tab (Z) | 5 mm slot | 4.8 mm tab | 0.2 mm (0.1 mm per side) | requirements.md |
| 7 | Mounting plate slot to tab (X) | 3 mm depth | 2.8 mm tab | 0.2 mm (0.1 mm per side) | requirements.md |
| 8 | Rear pocket to rear wall plate (X) | 148 mm opening | ~147.8 mm plate | 0.2 mm (0.1 mm per side) | requirements.md |
| 9 | Rear pocket to rear wall plate (Y) | 15 mm depth | ~14.8 mm plate | 0.2 mm (0.1 mm per side) | requirements.md |
| 10 | Snap-fit hook retention to shell top ledge | 0.5 mm shoulder | 0.5 mm ledge | 0.1 mm gap target | requirements.md |
| 11 | Step joint lip to shell top recess | 0.5 mm lip height, 1.5 mm width | 0.5 mm recess | 0.1 mm gap target | requirements.md |
| 12 | Inset panel recess to panel (X) | 90 mm recess | 89.6 mm panel | 0.4 mm (0.2 mm per side) | requirements.md: 0.2 mm sliding fit |
| 13 | Inset panel recess to panel (Y) | 5 mm recess depth | ~4.6 mm panel | 0.4 mm front + rear clearance | Concept architecture |
| 14 | Pump head bottom to rod channel top | Z = 9.0 (pump bottom) | Z = 7 (channel top) | 2.0 mm air gap | Spatial resolution: vibration isolation |
| 15 | Front wall rod pass-through to rod | 3.2 mm bore | 3.0 mm rod | 0.2 mm diametral | Same as bushing bore |

No zero-clearance or mismatched interfaces. All clearances are sourced from requirements.md FDM tolerance guidelines.

---

## Assembly Feasibility

### Assembly sequence (factory, one-time)

1. **Shell bottom on work surface** (open side up). All subsequent steps access the interior from above.
2. **Drop rear wall plate into rear pocket.** The plate (147.8 mm wide x ~70 mm tall full height, but only 34 mm exposed in shell bottom) enters from above (+Z). The 1 mm lip on all edges guides it. The four corner snap tabs click past the plate edges. The plate can be installed because the pocket opening (148 mm x 34 mm) is accessible from above, and the plate's chamfered corners clear the snap tabs. **Check:** The plate's full height (~70 mm) extends above the shell bottom seam (Z = 39), but since the shell top is not yet installed, the plate stands proud of the shell bottom by ~36 mm. This is correct -- the shell top will capture the upper portion.
3. **Thread link rods through bushings.** The rods (3 mm x ~170 mm long) feed from the front (Y = 185) rearward through the three bushing bores to Y = 18. The rod path is a straight line at Z = 5. Since the shell is open-top, any binding can be addressed by slight vertical lift. **Check:** The bushing bores (3.2 mm) are accessible from above because the channel is open-top between bushing locations.
4. **Attach release plate to rod rear ends.** The release plate slides onto the guide pins (already installed in the rear wall plate from step 2) and the link rod rear ends press-fit into the release plate. The release plate is accessible since the shell is open from above. **Check:** The release plate operates in the rear pocket zone (Y = 0..15). With the rear wall plate at Y = 0..15 and the release plate floating forward of it, there is room to work.
5. **Attach inset panel to rod front ends.** The inset panel's blind holes receive the rod front tips (press-fit). The panel sits in the recess zone (Y = 195..200). **Check:** Accessible from above.
6. **Install vertical mounting plate.** The plate drops into the four locating slots (2 per side wall). The tabs register into the 3 mm deep x 5 mm wide x 5 mm tall slots. **Check:** The plate drops from above; slots are open at the top (Z = 39 is the rim).
7. **Bolt pumps onto mounting plate.** Each pump is inserted from the front (pump head first, motor trailing). The pump bracket face presses against the mounting plate at Y = 85. Four M3 screws (with rubber grommets) secure each pump through the bracket into the mounting plate. **Check:** Screws are accessible from the front side of the mounting plate (Y > 85), and the shell is open from above for wrench access.
8. **Route tubing.** BPT tubes from pump barbs curve in the tube routing zone (Y = 133..185) and run rearward alongside the pump heads and motors to reach the JG fittings in the rear wall plate. **Check:** Generous clearance in tube routing zone.
9. **Route motor wiring** along the bottom interior to the rear wall plate pogo pads. **Check:** Wire routing space alongside link rod channels.
10. **Close shell top.** Press shell top down in -Z. Twelve snap-fit hooks engage the shell top ledges. The step joint lip self-aligns the halves. **Check:** All internal components are below Z = 39 or extend above it with accommodation from the shell top geometry.

### Can each step physically be performed?

Yes. Every step accesses the interior from above while the shell bottom is open-side-up. No step requires reaching through a narrow opening or working blind. The widest internal component (mounting plate, ~150 mm wide) clears the interior opening (150 mm clear width at X = 12..162).

### Order dependencies satisfied?

Yes. The rear wall plate (step 2) must be installed before the release plate (step 4) because the guide pins are in the rear wall plate. The mounting plate (step 6) must be installed before the pumps (step 7). Tubing (step 8) and wiring (step 9) must happen before shell closure (step 10). The sequence respects all dependencies.

### Trapped/inaccessible parts?

After step 10 (shell closed), all internal components are inaccessible without prying the shell open. This is intentional -- the cartridge is a disposable replacement unit. No component needs servicing after assembly.

### Disassembly (factory rework only)

Pry shell top off with a spudger (snap-fits tolerate ~5 cycles). Reverse the assembly sequence. The rear wall plate snap tabs can be released by pressing inward on the tab faces with a small tool through the open top.

---

## Part Count Minimization

| Part pair | Permanently joined? | Move relative? | Same material? | Could combine? | Decision |
|-----------|-------------------|----------------|----------------|----------------|----------|
| Shell bottom + T-rails | Yes (integral) | No | Yes (PETG) | Already combined | Correct |
| Shell bottom + link rod channels | Yes (integral) | No | Yes | Already combined | Correct |
| Shell bottom + guide bushings | Yes (integral) | No | Yes | Already combined | Correct |
| Shell bottom + snap-fit hooks | Yes (integral) | No | Yes | Already combined | Correct |
| Shell bottom + step joint lip | Yes (integral) | No | Yes | Already combined | Correct |
| Shell bottom + front wall | Yes (integral) | No | Yes | Already combined | Correct |
| Shell bottom + rear pocket | Yes (integral) | No | Yes | Already combined | Correct |
| Shell bottom + mounting plate locating slots | Yes (integral) | No | Yes | Already combined | Correct |
| Shell bottom + shell top | No (snap-fit) | No (static after assembly) | Yes | Could combine, but: (a) internal components require top-down assembly access, (b) single piece would need support structures in the interior, (c) the concept architecture mandates top/bottom split for assembly | Correct to keep separate |
| Shell bottom + mounting plate | No (captured) | No | Yes | Could combine, but: (a) the mounting plate is vertical and spans the full cartridge height (both shell halves), (b) making it integral would prevent top-down assembly, (c) M3 screw holes and motor bores print with best accuracy when the plate is flat on the build plate | Correct to keep separate |

No unnecessary part boundaries exist. The shell bottom integrates every feature that is static, same-material, and does not require separate print orientation for accuracy.

---

## FDM Printability

### Step 1 -- Print orientation

**Orientation: Open side up (Z = 0 on build plate, interior facing up).**

Rationale:
- The bottom wall (Z = 0) is a flat surface ideal for the build plate -- produces the best flatness for a surface that may rest on the dock floor.
- T-rail features print as vertical extrusions along the side walls. Layer lines stack along the Z axis, and the rail shear loads during cartridge sliding are along the Y axis (parallel to layers). This is the strongest orientation for rail loads.
- Interior features (channels, bushings, pockets, slots) are all accessible from above for support removal if needed.
- The snap-fit hooks print upward from the rim, placing layer lines perpendicular to the hook flex direction (X or Y). This is NOT the ideal orientation for hook flex strength, but the hooks only need to survive ~5 assembly cycles and do not flex during cartridge operation. The retention is provided by the 0.5 mm shoulder geometry, not by sustained flex. This tradeoff favors overall part quality (flat bottom, accurate rails) over hook flex strength.

### Step 2 -- Overhang audit

| # | Surface / Feature | Angle from horizontal | Printable? | Resolution |
|---|-------------------|----------------------|------------|------------|
| 1 | Bottom wall (Z = 0) | 0 deg (horizontal, ON build plate) | OK | Build plate surface |
| 2 | Side walls (XZ planes) | 90 deg (vertical) | OK | No overhang |
| 3 | Front wall (XZ plane) | 90 deg (vertical) | OK | No overhang |
| 4 | T-rail stem (vertical extrusion) | 90 deg | OK | No overhang |
| 5 | T-rail crossbar overhanging stem | ~0 deg (horizontal overhang, 2 mm each side) | No -- requires resolution | **Resolved:** 45-degree x 2 mm chamfers on underside of crossbar at stem-to-crossbar transitions. Chamfers bring angle to exactly 45 deg from horizontal. Printable without support. |
| 6 | Link rod channel walls | 90 deg (vertical, 4 mm tall) | OK | No overhang |
| 7 | Guide bushing bore ceilings | ~0 deg (top of 3.2 mm bore in 6 mm boss) | Marginal -- 3.2 mm span | OK. Bridge span is only 3.2 mm, well under 15 mm limit. Will sag slightly but bore can be cleaned with a 3 mm drill bit. |
| 8 | Rear pocket ceiling (Z = 38..39) | 0 deg (horizontal, 148 mm span) | No -- too wide for bridging | **Resolved:** The pocket is open at the top (the pocket ceiling is the seam plane at Z = 39, which is the top rim of the shell bottom -- it is not a closed ceiling). The rear wall plate sits in an open-top channel. No overhang exists. |
| 9 | Snap-fit hook undercuts | ~0 deg (1 mm undercut below hook lip) | No -- requires resolution | **Resolved:** 0.2 mm interface-gap sacrificial support nub below each hook lip. The nub prints as a thin connection to the rim surface at Z = 39, bridging to the underside of the hook lip at Z = 41. Breaks away cleanly. Access for removal: from above (interior) and from the side (hook faces inward). |
| 10 | Mounting plate locating slots | 90 deg cuts into wall | OK | Rectangular cutouts in vertical walls, no overhang |
| 11 | Rear pocket snap tab chamfers | 45 deg | OK | Exactly at the FDM printability limit |
| 12 | Inset recess ceiling at Z = 39 | This is the top rim -- open | OK | No ceiling; recess opens at the seam plane |
| 13 | Inset recess bottom (Z = 24) | Horizontal surface, but it is the TOP of the solid wall below the recess | OK | This is upward-facing; the solid wall below simply stops at Z = 24. No overhang. |
| 14 | Step joint lip (0.5 mm tall at Z = 39..39.5) | Vertical (0.5 mm step on outer perimeter) | OK | Tiny feature, no overhang |
| 15 | Elephant's foot chamfer (Z = 0) | 45 deg | OK | On build plate edge |

### Step 3 -- Wall thickness check

| Feature | Thickness | Minimum required | Status |
|---------|-----------|-----------------|--------|
| Bottom wall | 3 mm | 1.2 mm (structural) | OK (2.5x minimum) |
| Structural side wall | 6 mm | 1.2 mm (structural) | OK (5x minimum) |
| T-rail crossbar | 2 mm (X) | 0.8 mm (standard) | OK |
| T-rail stem | 4 mm (X) | 0.8 mm | OK |
| Link rod channel wall | 1 mm | 0.8 mm (standard) | OK (above minimum, non-structural) |
| Guide bushing wall | 1.4 mm (boss wall = (6 - 3.2) / 2) | 0.8 mm | OK |
| Snap-fit hook lip | 1.2 mm | 1.2 mm (structural, bears snap load) | OK (at minimum) |
| Front wall thickness | 15 mm | 1.2 mm | OK |
| Rear pocket lip | 1 mm | 0.8 mm | OK |
| Rear pocket snap tab | 4 mm wide x 1 mm protrusion | 0.8 mm | OK |
| Step joint lip | 1.5 mm wide x 0.5 mm tall | 0.4 mm minimum feature | OK |

No violations.

### Step 4 -- Bridge span check

| Feature | Span | Maximum allowed | Status |
|---------|------|----------------|--------|
| Guide bushing bore ceiling | 3.2 mm | 15 mm | OK |
| Link rod channel (open-top U, no bridging) | N/A | 15 mm | OK (no bridge) |
| Hook lip sacrificial support | ~1.2 mm span | 15 mm | OK |
| Rear pocket (open-top, no ceiling bridge) | N/A | 15 mm | OK |

No bridge spans exceed 15 mm.

### Step 5 -- Layer strength check

| Feature | Load direction | Layer line direction | Status |
|---------|---------------|---------------------|--------|
| T-rails | Shear along Y (slide direction) | Layers stack in Z, parallel to XY plane. Shear along Y is in-plane. | OK -- strongest direction |
| T-rail crossbar | Separation in X (rail pulled from dock channel) | Layers in XY plane. X-direction pull is in-plane. | OK |
| Snap-fit hooks | Flex in X (or Y for front/rear hooks) during assembly | Layers in XY plane. Flex is in-plane for side hooks (X direction), but hooks print vertically -- layers are perpendicular to the Z-direction hook stem. The hook flexes by bending in X, and layers stack in Z. This means the flex load is perpendicular to layer boundaries. | **Tradeoff noted.** Hook flex strength is reduced by this orientation. However: (a) hooks flex only during assembly (~5 cycles), (b) deflection is small (1 mm over 3 mm arm length), (c) PETG has good interlayer adhesion, (d) the 1.2 mm lip width provides adequate cross-section. The alternative (printing on a side) would compromise bottom wall flatness and rail accuracy. Rail accuracy takes priority over hook flex strength because rail function is continuous (every insertion/removal) while hook flex is one-time (assembly). |
| Link rod channel walls | Vertical load from rod weight | Layers in XY plane, walls are vertical. Load is perpendicular to layers. | OK -- load is negligible (rod weight ~10 g per rod) |
| Step joint lip | Shear from shell top alignment | Layers in XY plane. Shear in X/Y is in-plane. | OK |
| Rear pocket snap tabs | Shear in Y from plate insertion | Layers in XY plane. Y-shear is in-plane. | OK |

---

## Design Gaps

No design gaps were identified. Every behavioral claim in this document resolves to a named geometric feature with dimensions. All clearances are sourced from requirements.md. All features are printable as designed.

---

## Dimensional Summary Table

All dimensions in shell-bottom frame. This is the complete set of numbers a downstream CadQuery agent needs.

| ID | Dimension | Value (mm) | Source |
|----|-----------|-----------|--------|
| E1 | Outer width (X) | 174 | Spatial: 2x62.6 pump + 15 gap + 2x2 clearance + 2x12 wall |
| E2 | Outer depth (Y) | 200 | Spatial: 15 rear + 2 gap + 68 motor + 48 head + 52 tube + 15 front |
| E3 | Outer height (Z) | 39 | Half of 78 total cartridge height |
| W1 | Side wall total thickness | 12 | Structural wall (6) + stem (4) + crossbar (2) |
| W2 | Structural wall thickness | 6 | X = 6..12 left, X = 162..168 right |
| W3 | Bottom wall thickness | 3 | Z = 0..3 |
| W4 | Front wall thickness | 15 | Y = 185..200 |
| W5 | Interior clear width | 150 | X = 12..162 |
| W6 | Interior clear depth | 170 | Y = 15..185 |
| T1 | T-rail crossbar width (Z) | 8 | Crossbar Z = 16..24 |
| T2 | T-rail crossbar thickness (X) | 2 | Crossbar X = 0..2 (left) |
| T3 | T-rail stem depth (X) | 4 | Stem X = 2..6 (left) |
| T4 | T-rail stem width (Z) | 4 | Stem Z = 18..22 |
| T5 | T-rail center Z | 20 | Centered in lower half |
| T6 | T-rail taper start Y | 185 | 15 mm from front face |
| T7 | T-rail taper end Y | 200 | Front face |
| T8 | Crossbar underside chamfer | 2 x 45-deg | Both inner faces of crossbar |
| R1 | Link rod center X (left) | 57 | 87 - 30 |
| R2 | Link rod center X (right) | 117 | 87 + 30 |
| R3 | Link rod center Z | 5 | Centered in Z = 3..7 channel |
| R4 | Link rod channel outer width | 6 | Centered on rod X |
| R5 | Link rod channel inner width | 4 | Opening for rod |
| R6 | Link rod channel depth (Z) | 4 | Z = 3..7 |
| R7 | Bushing bore ID | 3.2 | 3 mm rod + 0.2 mm clearance |
| R8 | Bushing boss OD | 6 | Matches channel outer width |
| R9 | Bushing boss length (Y) | 8 | Per spatial resolution |
| R10 | Bushing Y positions | 18, 85, 188 | Rear, middle, front |
| P1 | Pump 1 center X | 48.3 | 12 + 2 + 34.3 |
| P2 | Pump 2 center X | 125.7 | 174 - 48.3 |
| P3 | Pump center Z (cartridge frame) | 40.3 | 3 + 4 + 2 + 31.3 |
| P4 | Pump head bottom Z (cartridge frame) | 9 | 3 + 4 + 2 |
| P5 | Mounting plate Y | 85 | Depth layout |
| P6 | Pump head front face Y | 133 | 85 + 48 |
| P7 | Motor nub rear Y | 17 | 85 - 68 |
| S1 | Mounting plate slot depth (X) | 3 | Into wall from interior face |
| S2 | Mounting plate slot width (Y) | 5 | Plate thickness |
| S3 | Mounting plate slot height (Z) | 5 | Tab height |
| S4 | Lower slot Z range | 12..17 | Caliper-verified pump screw pattern |
| S5 | Upper slot Z range | 33..38 | Near seam |
| F1 | Inset recess X range | 42..132 | 90 mm wide centered at 87 |
| F2 | Inset recess Z range (shell bottom) | 24..39 | Lower 15 mm of 30 mm recess |
| F3 | Inset recess Y range | 195..200 | 5 mm deep from outer face |
| F4 | Recess bottom edge radius | 2 | Finger comfort |
| F5 | Recess side edge radius | 0.5 | Crisp visual boundary |
| K1 | Rear pocket X range | 13..161 | 1 mm lip from interior walls |
| K2 | Rear pocket Z range | 4..38 | 1 mm lip from floor and seam |
| K3 | Rear pocket depth (Y) | 15 | Y = 0..15 |
| K4 | Rear pocket lip width | 1 | All edges |
| K5 | Snap tab positions (X, Z) | (16,7), (158,7), (16,35), (158,35) | Four corners |
| K6 | Snap tab width | 4 | Along lip edge |
| K7 | Snap tab protrusion (Y) | 1 | Into pocket |
| H1 | Hook height above rim (Z) | 3 | Z = 39..42 |
| H2 | Hook protrusion from wall | 3 | Inward |
| H3 | Hook base width | 4 | Along wall |
| H4 | Hook lip undercut | 1 | Retention depth |
| H5 | Hook lip width (narrowest) | 1.2 | Structural minimum |
| H6 | Hook lead-in chamfer | 1 x 45-deg | Outer face |
| H7 | Hook retention shoulder | 0.5 | Inner face step |
| H8 | Hook support nub gap | 0.2 | Interface gap |
| J1 | Step joint lip height | 0.5 | Z = 39..39.5 |
| J2 | Step joint lip width | 1.5 | Outer perimeter |
| C1 | Elephant's foot chamfer | 0.3 x 45-deg | Bottom exterior edges |
| C2 | Exterior edge chamfer | 1 | All non-bottom, non-groove edges |
