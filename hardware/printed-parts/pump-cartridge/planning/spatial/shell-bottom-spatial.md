# Shell Bottom -- Spatial Resolution

## 1. System-Level Placement

```
Part:        Shell Bottom (pump cartridge primary structure)
Parent:      Enclosure interior, front-bottom zone (dock bay)
Position:    Bottom of cartridge dock, front of enclosure
Orientation: Axis-aligned with enclosure (no rotation)
             Cartridge slides along Y axis (rear-to-front)
```

The shell bottom sits flat in the dock bay with no angular transformation relative to the enclosure. The cartridge's depth axis (Y) aligns with the enclosure's depth axis. No trigonometry or coordinate transforms are needed between the shell bottom's modeling frame and its installed orientation.

---

## 2. Reference Frame

```
Part:   Shell Bottom
Origin: Lower-left-rear corner of the EXTERIOR bounding box
X:      Width (left to right),  0..174 mm
Y:      Depth (rear to front),  0..200 mm
Z:      Height (bottom to top), 0..39 mm

Print orientation: Open side up (interior facing up, Z=0 on build plate)
Installed orientation: Same as print (no rotation required)
```

The full assembled cartridge is 174 mm wide x 200 mm deep x 78 mm tall. The shell bottom is the lower 39 mm (Z = 0..39). The shell top (separate part) covers Z = 39..78. The horizontal seam between the two halves is at Z = 39 mm.

---

## 3. Outer Envelope

All coordinates in shell-bottom frame.

| Dimension | Range | Value | Derivation |
|-----------|-------|-------|------------|
| Width (X) | 0..174 mm | 174 mm | See width derivation below |
| Depth (Y) | 0..200 mm | 200 mm | See depth derivation below |
| Height (Z) | 0..39 mm | 39 mm | Half of 78 mm total cartridge height |

### 3.1 Width derivation

Source dimensions (caliper-verified):
- Pump head width: 62.6 mm
- Pump bracket width: 68.6 mm (bracket extends 3 mm beyond pump head per side)
- Center gap between pump heads: 15 mm (concept architecture)

Interior clearance requirement: pump bracket edges must have at least 2 mm clearance to the interior wall faces (vibration isolation with rubber grommet mounts).

| Component | X range (mm) | Width (mm) |
|-----------|-------------|------------|
| Left wall + T-rail zone | 0..12 | 12 |
| Left bracket clearance | 12..14 | 2 |
| Pump 1 bracket | 14.0..82.6 | 68.6 |
| Inter-bracket gap | 82.6..91.4 | 8.8 |
| Pump 2 bracket | 91.4..160.0 | 68.6 |
| Right bracket clearance | 160..162 | 2 |
| Right wall + T-rail zone | 162..174 | 12 |

Check: 12 + 2 + 68.6 + 8.8 + 68.6 + 2 + 12 = 174.0 mm.

Note: the inter-bracket gap (8.8 mm) corresponds to a 15 mm gap between pump head edges. The pump heads (62.6 mm) are narrower than the brackets (68.6 mm) by 3 mm per side. Gap between pump heads = 8.8 + 2 x 3.0 = 14.8 mm, effectively 15 mm.

### 3.2 Depth derivation

| Zone | Y range (mm) | Length (mm) | Contents |
|------|-------------|-------------|----------|
| Rear pocket | 0..15 | 15 | Receives rear wall plate (separate piece) |
| Motor nub clearance | 15..17 | 2 | Air gap to motor shaft nub tips |
| Motor bodies | 17..85 | 68 | DC motor cylinders extending rearward from mounting plate |
| Mounting plate | 85 (plane) | -- | Vertical mounting plate sits at Y = 85; bracket faces on front side |
| Pump heads | 85..133 | 48 | Pump head housings extending forward from mounting plate |
| Tube routing | 133..185 | 52 | BPT tube stubs (40 mm) + U-bend (25 mm radius) + barb reducers |
| Front wall | 185..200 | 15 | Structural wall + lower portion of inset panel recess |

Motor zone depth derivation from caliper-verified pump geometry:
- Total pump length (front face to motor nub tip): 116.48 mm
- Pump head depth (front face to bracket face): 48 mm
- Motor zone behind bracket (bracket to nub tip): 116.48 - 48 = 68.48 mm, rounded to 68 mm
- Motor nub protrusion beyond end cap: 5.05 mm (caliper-verified)

### 3.3 Height derivation

Full cartridge height (78 mm) breakdown from exterior bottom (Z = 0):

| Zone | Z range (mm) | Thickness (mm) | Contents |
|------|-------------|----------------|----------|
| Bottom wall | 0..3 | 3 | Solid floor (build plate surface) |
| Link rod channel zone | 3..7 | 4 | U-channels for 3 mm steel link rods |
| Sub-pump clearance | 7..9 | 2 | Air gap below pump heads |
| Pump heads (lower) | 9..39 | 30 | Lower portion of 62.6 mm pump head cross-section |
| **Seam (Z = 39)** | -- | -- | **Shell bottom / shell top split line** |
| Pump heads (upper) | 39..71.6 | 32.6 | Upper portion of pump head cross-section |
| Super-pump clearance | 71.6..73.6 | 2 | Air gap above pump heads |
| Top wall | 73.6..78 | 4.4 | Shell top wall (slightly thicker for snap-fit ledge) |

The seam at Z = 39 passes through the pump head zone, 30 mm above the pump bottom edge and 32.6 mm below the pump top edge. The shell bottom contains the link rod channels, the sub-pump clearance, and the lower 30 mm of the pump heads.

---

## 4. Pump Center Positions

All coordinates in shell-bottom frame. The pump centerlines are above the shell bottom seam (Z = 40.3 mm > 39 mm), so they are technically in the shell top domain. However, the shell bottom must accommodate the lower halves of the pump heads and the mounting plate screw patterns that are below the centerline.

| Parameter | Pump 1 | Pump 2 | Derivation |
|-----------|--------|--------|------------|
| Center X | 48.3 mm | 125.7 mm | 12 (wall) + 2 (clearance) + 34.3 (half bracket) = 48.3 |
| Center Z (full cartridge) | 40.3 mm | 40.3 mm | 3 (floor) + 4 (rod channel) + 2 (clearance) + 31.3 (half pump head) |
| Mounting plate Y | 85 mm | 85 mm | Bracket face against mounting plate |
| Pump head front face Y | 133 mm | 133 mm | 85 + 48 = 133 |
| Motor nub rear Y | 17 mm | 17 mm | 85 - 68 = 17 |

Symmetry check: cartridge center X = 174 / 2 = 87.0 mm. Pump 1 offset = 87.0 - 48.3 = 38.7 mm. Pump 2 offset = 125.7 - 87.0 = 38.7 mm. Symmetric.

### 4.1 Mounting screw hole positions

Each pump has 4x M3 holes in a 48 mm x 48 mm square pattern (caliper-verified, user-confirmed) centered on the pump axis. The holes are on the mounting plate at Y = 85 mm.

**Pump 1 screw holes (in shell-bottom frame):**

| Hole | X (mm) | Z (full cartridge, mm) | Z (shell-bottom, mm) | In shell bottom? |
|------|--------|----------------------|----------------------|------------------|
| Lower-left | 48.3 - 24 = 24.3 | 40.3 - 24 = 16.3 | 16.3 | Yes |
| Lower-right | 48.3 + 24 = 72.3 | 16.3 | 16.3 | Yes |
| Upper-left | 24.3 | 40.3 + 24 = 64.3 | n/a | No (above seam) |
| Upper-right | 72.3 | 64.3 | n/a | No (above seam) |

**Pump 2 screw holes (in shell-bottom frame):**

| Hole | X (mm) | Z (full cartridge, mm) | Z (shell-bottom, mm) | In shell bottom? |
|------|--------|----------------------|----------------------|------------------|
| Lower-left | 125.7 - 24 = 101.7 | 16.3 | 16.3 | Yes |
| Lower-right | 125.7 + 24 = 149.7 | 16.3 | 16.3 | Yes |
| Upper-left | 101.7 | 64.3 | n/a | No (above seam) |
| Upper-right | 149.7 | 64.3 | n/a | No (above seam) |

The shell bottom sees the lower two screw holes of each pump through the mounting plate locating slots. The mounting plate is a separate piece -- the shell bottom provides the locating slots that position it, not the screw holes themselves.

### 4.2 Motor bore positions

Each pump motor passes through the mounting plate at Y = 85 mm. Motor diameter: ~35 mm (caliper-verified, low confidence). Bore diameter in mounting plate: 37 mm (35 + 1 mm clearance per side).

| Motor bore | Center X (mm) | Center Z (full cartridge, mm) |
|------------|--------------|-------------------------------|
| Pump 1 | 48.3 | 40.3 |
| Pump 2 | 125.7 | 40.3 |

The lower edge of each motor bore: 40.3 - 18.5 = 21.8 mm (well within shell bottom at Z = 21.8). The shell bottom must provide clearance in the motor zone (Y = 17..85) for the motor cylinders, which occupy a circular cross-section of ~37 mm diameter centered at (X, Z) = (48.3, 40.3) and (125.7, 40.3).

---

## 5. Side Wall and T-Rail Profiles

### 5.1 Side wall structure

Each side wall is a 12 mm thick zone (X direction) running the full depth (Y = 0..200) and full shell-bottom height (Z = 0..39). The T-rail is integral to the wall.

**Left side wall cross-section (looking from the front, constant along Y except at lead-in taper):**

```
     X=0   X=2     X=6         X=12
      |     |       |            |
Z=39  |=====|=======|============|  top rim
      |     |       |            |
      | cb  | groove|   wall     |
Z=24  | 8mm |  4mm  |   body    |  <- crossbar top
      | wide| deep  |   6mm     |
      |     |       |  thick    |
      |-----|       |            |
      |     |-------|            |
Z=22  |     | stem  |            |  <- stem top
      |     | 4mm   |            |
Z=18  |     | wide  |            |  <- stem bottom
      |     |-------|            |
      |-----|       |            |
Z=16  |     |       |            |  <- crossbar bottom
      |     |       |            |
      | cb  | groove|   wall     |
      |     |       |   body    |
Z=0   |=====|=======|============|  bottom edge
```

| Feature | X range | Z range | Size |
|---------|---------|---------|------|
| Crossbar | 0..2 | 16..24 | 2 mm thick (X) x 8 mm tall (Z) |
| Stem | 2..6 | 18..22 | 4 mm deep (X) x 4 mm wide (Z) |
| Upper groove | 0..6 | 24..39 | 6 mm deep (X) x 15 mm tall (Z) |
| Lower groove | 0..6 | 0..16 | 6 mm deep (X) x 16 mm tall (Z) |
| Structural wall | 6..12 | 0..39 | 6 mm thick (X) x 39 mm tall (Z) |

T-rail center Z = 20 mm. This places the rail in the lower half of the shell bottom, leaving the upper rim (Z = 24..39) free for snap-fit hooks and seam features.

The crossbar has a 45-degree chamfer on its underside edges (per FDM constraint -- eliminates overhang at the crossbar-to-stem transition). The chamfer runs the full Y length. Chamfer extent: 2 mm x 2 mm at 45 degrees on each of the two overhanging faces (crossbar bottom inner edge and crossbar top inner edge).

### 5.2 Right side wall cross-section (mirror of left)

| Feature | X range | Z range |
|---------|---------|---------|
| Structural wall | 162..168 | 0..39 |
| Stem | 168..172 | 18..22 |
| Crossbar | 172..174 | 16..24 |
| Upper groove | 168..174 | 24..39 |
| Lower groove | 168..174 | 0..16 |

### 5.3 T-rail lead-in taper

At the front end of the cartridge (insertion leading edge), the T-rail crossbar tapers from 6 mm wide to 8 mm wide over the front 15 mm of depth.

| Y position | Crossbar Z range | Crossbar width (Z) |
|------------|-----------------|---------------------|
| Y = 200 (front tip) | 17..23 | 6 mm |
| Y = 192 | 16.5..23.5 | 7 mm |
| Y = 185 | 16..24 | 8 mm (full profile) |
| Y = 185..0 | 16..24 | 8 mm (constant) |

The stem width remains 4 mm throughout. The taper is only on the crossbar, providing a centering funnel for dock insertion.

### 5.4 T-rail interface with dock channel

| Parameter | Cartridge rail (shell bottom) | Dock channel (mating) |
|-----------|-------------------------------|----------------------|
| Crossbar width (Z) | 8 mm | 8.4 mm (0.2 mm clearance per side) |
| Crossbar thickness (X) | 2 mm | 2.4 mm slot depth |
| Stem width (Z) | 4 mm | 4.4 mm |
| Stem depth (X) | 4 mm | 4 mm slot |
| Sliding clearance | -- | 0.2 mm per side in all directions |

---

## 6. Link Rod Channels and Guide Bushings

### 6.1 Channel layout

Two U-shaped channels run along the bottom interior surface (on top of the 3 mm bottom wall), spanning from the rear pocket to the front wall.

| Parameter | Rod 1 (left) | Rod 2 (right) |
|-----------|-------------|---------------|
| Center X | 57 mm | 117 mm |
| Spacing | 60 mm apart, symmetric about X = 87 mm centerline |
| Y range | 15..185 mm (rear wall plate interior face to front wall interior face) |
| Z range | 3..7 mm (4 mm tall channel sitting on bottom wall) |

### 6.2 Channel cross-section (XZ plane)

Each channel is a U-groove with a cylindrical bore at bushing locations.

```
     ← 6mm →
  Z=7 |--    --|
      |  ----  |   <- 4mm wide opening
      | (    ) |   <- 3.2mm bore at bushing locations
  Z=3 |========|   <- bottom wall top surface
```

| Feature | Dimension |
|---------|-----------|
| Channel outer width (X) | 6 mm (centered on rod center X) |
| Channel inner width (X) | 4 mm opening |
| Channel wall thickness | 1 mm per side |
| Channel depth (Z) | 4 mm (Z = 3..7) |
| Rod diameter | 3 mm (steel) |

### 6.3 Guide bushing locations and dimensions

Six bushings total (3 per rod). Each bushing is a cylindrical bore through a boss integrated into the channel.

| Bushing | Rod | Center X (mm) | Center Y (mm) | Center Z (mm) | Location context |
|---------|-----|--------------|---------------|---------------|------------------|
| Front-L | 1 | 57 | 188 | 5 | In front wall structure |
| Mid-L | 1 | 57 | 85 | 5 | At mounting plate Y position |
| Rear-L | 1 | 57 | 18 | 5 | Just inside rear pocket |
| Front-R | 2 | 117 | 188 | 5 | In front wall structure |
| Mid-R | 2 | 117 | 85 | 5 | At mounting plate Y position |
| Rear-R | 2 | 117 | 18 | 5 | Just inside rear pocket |

| Bushing parameter | Value |
|-------------------|-------|
| Bore ID | 3.2 mm (3 mm rod + 0.2 mm sliding clearance) |
| Boss OD | 6 mm |
| Boss length (Y) | 8 mm |
| Bore center Z | 5 mm (centered in 4 mm channel: Z = 3 + 2 = 5) |

### 6.4 Link rod interface specification

| Parameter | Shell bottom (channel + bushing) | Mating part |
|-----------|----------------------------------|-------------|
| Rod 1 path | X=57, Z=5, Y=15..185 | Inset release panel (front, Y~192) and release plate (rear, Y~12) |
| Rod 2 path | X=117, Z=5, Y=15..185 | Same |
| Bore ID | 3.2 mm | Rod OD = 3.0 mm |
| Fit type | Sliding (0.2 mm diametral clearance) | -- |
| Boss OD | 6 mm | Channel walls provide structural backing |

---

## 7. Front Wall Geometry

### 7.1 Front wall structure

The front wall spans X = 12..162 (interior width) at Y = 185..200 mm (15 mm deep).

| Zone | X range | Y range | Z range | Description |
|------|---------|---------|---------|-------------|
| Solid wall (below recess) | 12..162 | 185..200 | 0..24 | Full-thickness structural wall |
| Recess zone (lower portion) | 42..132 | 195..200 | 24..39 | 5 mm deep pocket from outer face |
| Solid wall (beside recess, left) | 12..42 | 185..200 | 24..39 | Full-thickness wall flanking recess |
| Solid wall (beside recess, right) | 132..162 | 185..200 | 24..39 | Full-thickness wall flanking recess |

### 7.2 Inset panel recess (lower portion)

The full inset panel recess is 90 mm wide x 30 mm tall x 5 mm deep, centered on the front face. The recess center is at Z = 39 mm (the seam line), so the shell bottom contains the lower 15 mm of the recess.

| Parameter | Value | Derivation |
|-----------|-------|------------|
| Recess X range | 42..132 mm | 90 mm wide, centered at X = 87 |
| Recess Z range (shell bottom portion) | 24..39 mm | Lower 15 mm of 30 mm recess; full recess spans Z = 24..54 in cartridge frame |
| Recess Y range | 195..200 mm | 5 mm deep from outer face at Y = 200 |
| Wall thickness behind recess | 10 mm | Y = 185..195 (structural wall behind recess pocket) |
| Bottom edge radius | 2 mm | Finger comfort radius on the recess bottom edge at Z = 24 |
| Side edge radius | 0.5 mm | Crisp visual boundary |

### 7.3 Front wall interface with inset release panel

The inset panel is a separate moving piece that sits in the recess and translates rearward (negative Y) by up to 3 mm when squeezed.

| Parameter | Shell bottom (recess) | Inset panel (mating) |
|-----------|----------------------|----------------------|
| Recess width (X) | 90 mm (X = 42..132) | Panel width: 89.6 mm (0.2 mm clearance per side) |
| Recess depth (Y) | 5 mm (Y = 195..200) | Panel thickness: ~4.6 mm (0.2 mm clearance front + 0.2 mm behind) |
| Panel travel | 3 mm rearward (Y = 195 to 192) | Guided by recess side walls |
| Link rod attachment | Rods at X=57, X=117, Z=5 | Panel has blind holes on rear face at matching X positions |

### 7.4 Front wall interface with link rod channels

The front guide bushings (at Y = 188) are embedded in the front wall structure. The link rods pass through these bushings, through the 10 mm structural wall behind the recess (Y = 185..195), and connect to the inset panel in the recess zone (Y = 195..200). The rods must pass through the wall, so the wall has clearance holes at (X=57, Z=5) and (X=117, Z=5), 3.2 mm diameter.

---

## 8. Snap-Fit Hooks Along Top Rim

Hooks are on the top rim (Z = 39 mm) of the shell bottom. They protrude upward and engage matching ledges on the shell top's inner rim.

### 8.1 Hook layout

| Wall | Number of hooks | Hook Y or X positions (mm) |
|------|----------------|---------------------------|
| Left side (X = 12, inner face) | 4 | Y = 40, 80, 120, 160 |
| Right side (X = 162, inner face) | 4 | Y = 40, 80, 120, 160 |
| Front wall (Y = 185, inner face) | 2 | X = 62, 112 |
| Rear wall (Y = 15, inner face) | 2 | X = 62, 112 |

Total: 12 hooks.

### 8.2 Hook cross-section profile

All hooks have the same profile. Dimensions below are for a left-wall hook (protruding inward in +X direction and upward in +Z direction). Mirror for right wall. Rotate 90 degrees for front/rear wall hooks.

| Feature | Dimension |
|---------|-----------|
| Hook base width (along wall, Y) | 4 mm |
| Hook protrusion from wall (X) | 3 mm |
| Hook height above rim (Z) | 3 mm (Z = 39..42) |
| Hook lip undercut (Z) | 1 mm |
| Hook lip width (X) | 1.2 mm |
| Lead-in chamfer (outer face) | 45 degrees x 1 mm |
| Retention shoulder | 0.5 mm step on inner face |

The hooks are designed to snap over a matching 0.5 mm ledge on the shell top inner rim. The 45-degree lead-in allows the shell top to press down over the hooks during assembly. The 0.5 mm retention shoulder resists separation.

### 8.3 Hook print support

Each hook lip has a 0.2 mm interface-gap sacrificial support nub below the 1 mm undercut (per FDM manufacturing constraints). The nub breaks away after printing. Located at Z = 39 mm (the rim surface), supporting the hook lip overhang at Z = 41..42 mm.

### 8.4 Snap-fit interface with shell top

| Parameter | Shell bottom (hooks) | Shell top (ledges) |
|-----------|---------------------|-------------------|
| Hook protrusion | 3 mm inward from wall | Matching 3 mm wide channel in shell top rim |
| Retention | 0.5 mm shoulder | 0.5 mm ledge |
| Engagement force direction | Z (press top onto bottom) | -- |
| Clearance | 0.1 mm gap target (tight fit) | -- |

---

## 9. Step Joint Along Top Rim

The shell top/bottom seam at Z = 39 mm has a step joint (overlap lip) for alignment and visual seam quality.

| Parameter | Value |
|-----------|-------|
| Lip owner | Shell bottom has a 0.5 mm upward-protruding lip on the OUTER perimeter |
| Lip height (Z) | 0.5 mm (Z = 39..39.5 on outer edge) |
| Lip width (X or Y) | 1.5 mm (runs along outer edge of wall top surface) |
| Shell top | Has a matching 0.5 mm recess (step-down) on its outer edge lower rim |
| Gap target | 0.1 mm |

The step joint runs continuously around the full perimeter (left wall, front wall, right wall, rear wall top edges). The snap-fit hooks are inboard of the step joint.

---

## 10. Mounting Plate Locating Slots

The vertical mounting plate (separate piece) registers into rectangular slots cut into the inner faces of the side walls. The slots constrain the plate in X (lateral), Y (depth), and Z (vertical) when the shell halves are closed.

### 10.1 Slot positions

Two slots per side wall, four total. All at Y = 82.5..87.5 mm (centered on mounting plate position Y = 85).

| Slot | Wall | X range (mm) | Y range (mm) | Z range (mm) |
|------|------|-------------|-------------|-------------|
| Left-lower | Left (X=12) | 9..12 (3 mm into wall) | 82.5..87.5 | 12..17 |
| Left-upper | Left (X=12) | 9..12 | 82.5..87.5 | 33..38 |
| Right-lower | Right (X=162) | 162..165 (3 mm into wall) | 82.5..87.5 | 12..17 |
| Right-upper | Right (X=162) | 162..165 | 82.5..87.5 | 33..38 |

### 10.2 Slot dimensions

| Parameter | Value |
|-----------|-------|
| Slot depth into wall (X) | 3 mm |
| Slot width (Y) | 5 mm (matches mounting plate thickness) |
| Slot height (Z) | 5 mm |
| Clearance | 0.1 mm per side (snug fit for plate tabs) |

### 10.3 Slot interface with mounting plate

| Parameter | Shell bottom (slots) | Mounting plate (tabs) |
|-----------|---------------------|----------------------|
| Tab count | 4 slots receive 4 tabs | 2 tabs per side, 4 total |
| Tab dimensions | -- | 2.8 mm deep (X) x 4.8 mm wide (Y) x 4.8 mm tall (Z) |
| Fit type | Snug (0.1 mm clearance per side) | Plate captured when shell halves close |
| Lower tab Z | 12..17 (slot), 12.1..16.9 (tab) | Holds plate against downward loads |
| Upper tab Z | 33..38 (slot), 33.1..37.9 (tab) | Holds plate against upward loads |

Note: the upper slots (Z = 33..38) are close to the seam (Z = 39). The shell top will have matching upper slots to capture the plate tabs that extend above the seam. The plate spans the full cartridge height.

---

## 11. Interior Clearances Around Pump Zone

### 11.1 Pump head zone (Y = 85..133)

The pump heads are the largest cross-section features in the cartridge interior. Each pump head is ~62.6 mm x 62.6 mm (nearly square), centered on its pump axis.

**Pump 1 interior clearances (shell-bottom frame):**

| Direction | Pump edge | Wall/feature | Clearance |
|-----------|-----------|-------------|-----------|
| Left (-X) | X = 48.3 - 31.3 = 17.0 | Interior wall X = 12 | 5.0 mm |
| Right (+X) | X = 48.3 + 31.3 = 79.6 | Pump 2 left edge X = 94.4 | 14.8 mm (center gap) |
| Down (-Z) | Z = 9.0 (cartridge frame) | Rod channel top Z = 7 | 2.0 mm |
| Up (+Z) | Z = 71.6 (cartridge frame) | Interior ceiling (shell top) | 2.0 mm |

**Pump 2 interior clearances** mirror pump 1 about centerline X = 87.

### 11.2 Motor zone (Y = 17..85)

Motor cylinders are ~35 mm diameter, centered on pump axes. The motors are much narrower than the pump heads, so clearances are generous in this zone.

| Motor | Center X | Motor edge X (left) | Motor edge X (right) | Clearance to wall |
|-------|----------|--------------------|--------------------|------------------|
| 1 | 48.3 | 30.8 | 65.8 | 18.8 mm (to X=12) |
| 2 | 125.7 | 108.2 | 143.2 | 18.8 mm (to X=162) |

Motor bottom edge Z (cartridge frame): 40.3 - 17.5 = 22.8 mm. Clearance to rod channels (Z = 7): 15.8 mm. Generous clearance below motors for tubing routing.

### 11.3 Tube routing zone (Y = 133..185)

This zone is forward of the pump heads and contains the BPT tube stubs, U-bends, barb reducers, and short PE tube segments connecting to the JG fittings (which are in the rear wall plate at Y = 0..15).

Wait -- the tubes route REARWARD from the pump face to the JG fittings at the rear. The tube routing zone described here (Y = 133..185) is where the tubes exit the pump face, extend forward, and make their U-bend to head rearward. The tubes then run alongside the pump heads and motors back toward the rear wall.

The interior space in this zone is fully open (no mounting plate, no motors). Clear cross-section: 150 mm wide (X = 12..162) x 36 mm tall (Z = 3..39, minus bottom wall). The 25 mm minimum bend radius for BPT tubing is easily accommodated.

### 11.4 Clearance summary table

| Zone | Y range | Clear X range | Clear Z range (shell bottom) | Clear area |
|------|---------|---------------|------------------------------|------------|
| Rear pocket | 0..15 | 13..161 | 4..38 | Occupied by rear wall plate |
| Motor zone | 17..85 | 12..162 | 7..39 | Two ~35mm dia. cylinders + tubes alongside |
| Pump head zone | 85..133 | 12..162 | 9..39 | Two ~62.6mm square heads + 15mm center gap |
| Tube routing | 133..185 | 12..162 | 3..39 | Fully open for tube U-bends |
| Front wall | 185..200 | -- | -- | Solid wall with recess |

---

## 12. Rear Pocket for Rear Wall Plate

### 12.1 Pocket geometry

The rear wall plate is a separate piece that snaps into a rectangular pocket at the rear face of the shell. The pocket opening is at Y = 0 (rear exterior face). A 1 mm lip on all four edges retains the plate.

| Parameter | Value |
|-----------|-------|
| Pocket opening X range | 13..161 mm (148 mm wide) |
| Pocket opening Z range | 4..38 mm (34 mm tall in shell bottom) |
| Pocket depth (Y) | 15 mm (Y = 0..15) |
| Lip width (all edges) | 1 mm |
| Lip X range | 12..13 (left), 161..162 (right) |
| Lip Z range | 3..4 (bottom), 38..39 (top, at seam) |

The pocket is bounded by:
- Left wall interior (X = 12) + 1 mm lip = X = 13
- Right wall interior (X = 162) - 1 mm lip = X = 161
- Bottom wall top (Z = 3) + 1 mm lip = Z = 4
- Shell bottom seam (Z = 39) - 1 mm lip = Z = 38

### 12.2 Pocket interface with rear wall plate

| Parameter | Shell bottom (pocket) | Rear wall plate (mating) |
|-----------|----------------------|-------------------------|
| Plate width | Pocket: 148 mm | Plate: ~147.8 mm (0.1 mm clearance per side) |
| Plate height (shell bottom portion) | Pocket: 34 mm | Full plate height: ~70 mm (spans both shell halves) |
| Plate thickness | Pocket depth: 15 mm | Plate: ~14.8 mm (0.1 mm clearance) |
| Retention | 1 mm lip with chamfered snap tabs at 4 corners | Chamfered leading edges on plate for snap-in |
| Insertion direction | From above (during assembly into shell bottom) | Plate drops into pocket before shell top closes |

### 12.3 Rear pocket corner snap detail

Four snap-fit retention points (one per corner of the pocket) hold the rear wall plate in place.

| Corner | X (mm) | Z (mm) | Snap tab protrusion |
|--------|--------|--------|---------------------|
| Bottom-left | 16 | 7 | 1 mm (in Y, protruding into pocket from lip face) |
| Bottom-right | 158 | 7 | 1 mm |
| Top-left | 16 | 35 | 1 mm |
| Top-right | 158 | 35 | 1 mm |

Each snap tab is 4 mm wide (along the lip edge), 1 mm tall (protrusion into pocket), with a 45-degree chamfer on the leading face for plate insertion.

---

## 13. Bottom Wall Features

### 13.1 Build plate face

The bottom wall exterior (Z = 0) is flat and sits on the build plate during printing. A 0.3 mm x 45-degree chamfer runs along all bottom exterior edges to mitigate elephant's foot (per FDM manufacturing constraints).

| Edge | Start point | End point | Chamfer |
|------|------------|-----------|---------|
| Left bottom | (0, 0, 0) | (0, 200, 0) | 0.3 mm x 45 deg |
| Right bottom | (174, 0, 0) | (174, 200, 0) | 0.3 mm x 45 deg |
| Front bottom | (0, 200, 0) | (174, 200, 0) | 0.3 mm x 45 deg |
| Rear bottom | (0, 0, 0) | (174, 0, 0) | 0.3 mm x 45 deg |

### 13.2 Interior floor

The interior floor surface is at Z = 3 mm. The link rod channels sit on this surface (Z = 3..7). Between and around the channels, the floor is flat and uninterrupted.

### 13.3 Gussets under mounting plate zone

The mounting plate locating slots transfer pump loads (from the vertically-mounted pump weight and screw clamping force) into the side walls. The side wall in the Y = 80..90 zone (around the mounting plate) may be reinforced with internal gussets connecting the bottom wall to the side wall.

Gusset locations (if needed -- to be confirmed during parts specification):
- Left wall, Y = 82..88, Z = 3..12, X = 6..12: triangular gusset
- Right wall, mirror

---

## 14. Exterior Edge Treatment

All exterior edges of the shell bottom have a 1 mm chamfer or 1 mm fillet (per concept design language). The bottom edges have a 0.3 mm chamfer (elephant's foot mitigation, per Section 13.1), which is smaller. The 1 mm treatment applies to:

| Edge type | Treatment | Location |
|-----------|-----------|----------|
| Bottom exterior edges | 0.3 mm x 45 deg chamfer | Z = 0 perimeter (elephant's foot) |
| Top rim exterior edges | 1 mm chamfer | Z = 39, outer perimeter (except where step joint lip protrudes) |
| Vertical exterior corners | 1 mm chamfer | All four vertical edges of the box |
| Groove edges (T-rail) | Functional, not chamfered | Groove edges are mating surfaces |

---

## 15. Transform Summary

The shell bottom has NO rotation relative to any parent frame. The installed orientation is identical to the modeling/print orientation. The transform is a pure translation.

### 15.1 Shell bottom frame to full cartridge frame

```
Cartridge frame origin: lower-left-rear corner of full cartridge exterior
Shell bottom frame origin: same point (they share the origin)

Transform: identity (no rotation, no translation)

Shell bottom frame coordinates = cartridge frame coordinates for Z = 0..39
```

### 15.2 Shell bottom frame to enclosure frame

```
Enclosure frame: per vision.md, 220 x 300 x 400 mm outer enclosure
Cartridge dock position: front-bottom of enclosure interior

Transform: pure translation
  Enclosure X = shell_bottom X + X_offset  (centered in enclosure width)
  Enclosure Y = shell_bottom Y + Y_offset  (flush with enclosure front face)
  Enclosure Z = shell_bottom Z + Z_offset  (sitting on enclosure floor)

Offset values depend on enclosure interior dimensions (not yet resolved).
```

### 15.3 Verification points

Since the transform is identity (shell bottom to cartridge frame), all points map trivially. Three verification points:

| Point | Shell bottom frame | Cartridge frame | Check |
|-------|-------------------|-----------------|-------|
| Origin | (0, 0, 0) | (0, 0, 0) | Rear-left-bottom corner of exterior |
| Front-right-top of shell | (174, 200, 39) | (174, 200, 39) | Shell top seam at front-right |
| Pump 1 lower-left screw hole | (24.3, 85, 16.3) | (24.3, 85, 16.3) | On mounting plate plane |

All three points map correctly under the identity transform.

### 15.4 Adjacent part interface coordinates

The following interfaces are specified in the shell-bottom frame. The mating part must use the SAME coordinates since all cartridge parts share the same reference frame (origin at lower-left-rear of cartridge exterior).

| Interface | Shell bottom location | Mating part | Mating part location |
|-----------|----------------------|-------------|---------------------|
| Rear pocket | Y=0..15, X=13..161, Z=4..38 | Rear wall plate | Same coordinates (plate sits in pocket) |
| Mounting plate slots | Y=82.5..87.5, see Section 10 | Mounting plate | Same coordinates (tabs fit into slots) |
| T-rail lower | X=0..6 (left), Z=16..24, full Y | Dock bay | Dock channel coordinates derived from dock frame + cartridge position |
| Snap-fit hooks | Z=39..42, see Section 8 | Shell top | Same coordinates (hooks engage shell top inner rim) |
| Step joint lip | Z=39..39.5, outer perimeter | Shell top | Same coordinates (shell top has matching recess) |
| Front recess | Y=195..200, X=42..132, Z=24..39 | Inset release panel | Same coordinates (panel sits in recess) |
| Link rod bushings | (57,Y,5) and (117,Y,5) per Section 6 | Steel link rods | Same coordinates (rods slide through bushings) |

---

## 16. Dimensional Summary Table

All dimensions in shell-bottom frame. This table is the complete set of numbers a downstream CadQuery agent needs.

| ID | Dimension | Value (mm) | Frame | Source |
|----|-----------|-----------|-------|--------|
| E1 | Outer width (X) | 174 | Shell bottom | Derived: 2x62.6 pump + 15 gap + 2x2 clearance + 2x12 wall |
| E2 | Outer depth (Y) | 200 | Shell bottom | Derived: 15 rear + 2 gap + 68 motor + 48 head + 52 tube + 15 front |
| E3 | Outer height (Z) | 39 | Shell bottom | Half of 78 total cartridge height |
| W1 | Side wall total thickness | 12 | Shell bottom | Structural wall (6) + stem (4) + crossbar (2) |
| W2 | Structural wall thickness | 6 | Shell bottom | X=6..12 left, X=162..168 right |
| W3 | Bottom wall thickness | 3 | Shell bottom | Z=0..3 |
| W4 | Front wall thickness | 15 | Shell bottom | Y=185..200 |
| W5 | Interior clear width | 150 | Shell bottom | X=12..162 |
| W6 | Interior clear depth | 170 | Shell bottom | Y=15..185 |
| T1 | T-rail crossbar width (Z) | 8 | Shell bottom | Decision doc |
| T2 | T-rail crossbar thickness (X) | 2 | Shell bottom | Derived |
| T3 | T-rail stem depth (X) | 4 | Shell bottom | Decision doc: "stem height" |
| T4 | T-rail stem width (Z) | 4 | Shell bottom | Decision doc: "stem width" |
| T5 | T-rail center Z | 20 | Shell bottom | Centered in lower half |
| T6 | T-rail taper start Y | 185 | Shell bottom | 15 mm from front face |
| T7 | T-rail taper end Y | 200 | Shell bottom | Front face |
| R1 | Link rod center X (left) | 57 | Shell bottom | 87 - 30 |
| R2 | Link rod center X (right) | 117 | Shell bottom | 87 + 30 |
| R3 | Link rod center Z | 5 | Shell bottom | Centered in Z=3..7 channel |
| R4 | Link rod channel width | 6 | Shell bottom | Outer width of U-channel |
| R5 | Link rod channel depth (Z) | 4 | Shell bottom | Z=3..7 |
| R6 | Bushing bore ID | 3.2 | Shell bottom | 3mm rod + 0.2mm clearance |
| R7 | Bushing boss OD | 6 | Shell bottom | |
| R8 | Bushing Y positions | 18, 85, 188 | Shell bottom | Rear, middle, front |
| P1 | Pump 1 center X | 48.3 | Shell bottom | 12+2+34.3 |
| P2 | Pump 2 center X | 125.7 | Shell bottom | 174-48.3 |
| P3 | Pump center Z (cartridge frame) | 40.3 | Cartridge | 3+4+2+31.3 |
| P4 | Pump head bottom Z (cartridge frame) | 9 | Cartridge | 3+4+2 |
| P5 | Mounting plate Y | 85 | Shell bottom | Derived from depth layout |
| P6 | Pump head front face Y | 133 | Shell bottom | 85+48 |
| P7 | Motor nub rear Y | 17 | Shell bottom | 85-68 |
| S1 | Mounting plate slot depth (X) | 3 | Shell bottom | Into wall from interior face |
| S2 | Mounting plate slot width (Y) | 5 | Shell bottom | Plate thickness |
| S3 | Mounting plate slot height (Z) | 5 | Shell bottom | Tab height |
| S4 | Lower slot Z range | 12..17 | Shell bottom | |
| S5 | Upper slot Z range | 33..38 | Shell bottom | |
| F1 | Inset recess X range | 42..132 | Shell bottom | 90mm wide centered at 87 |
| F2 | Inset recess Z range (shell bottom) | 24..39 | Shell bottom | Lower 15mm of 30mm recess |
| F3 | Inset recess Y range | 195..200 | Shell bottom | 5mm deep from outer face |
| F4 | Recess bottom edge radius | 2 | Shell bottom | Finger comfort |
| F5 | Recess side edge radius | 0.5 | Shell bottom | Crisp visual boundary |
| K1 | Rear pocket X range | 13..161 | Shell bottom | 1mm lip from interior walls |
| K2 | Rear pocket Z range | 4..38 | Shell bottom | 1mm lip from floor and seam |
| K3 | Rear pocket depth (Y) | 15 | Shell bottom | Y=0..15 |
| K4 | Rear pocket lip width | 1 | Shell bottom | All edges |
| H1 | Snap-fit hook height above rim (Z) | 3 | Shell bottom | Z=39..42 |
| H2 | Snap-fit hook protrusion (X or Y) | 3 | Shell bottom | Inward from wall |
| H3 | Snap-fit hook base width | 4 | Shell bottom | Along wall direction |
| H4 | Hook lip undercut | 1 | Shell bottom | Retention depth |
| H5 | Hook lip width | 1.2 | Shell bottom | Narrowest point |
| J1 | Step joint lip height | 0.5 | Shell bottom | Z=39..39.5 |
| J2 | Step joint lip width | 1.5 | Shell bottom | Outer perimeter |
| C1 | Elephant's foot chamfer | 0.3 x 45 deg | Shell bottom | Bottom exterior edges |
| C2 | Exterior edge chamfer | 1 | Shell bottom | All non-bottom exterior edges |
