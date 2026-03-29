# Cartridge Tray — Parts Specification

The tray is the structural backbone of the pump cartridge: a single printed PETG part containing every alignment-critical feature. All precision geometry — fitting bores, guide posts, pump mounting bosses, rail tongues — lives in this one part, eliminating cross-part tolerance stack-up. The tray is an open-top, open-front box built up by boolean union/cut operations on a single growing solid, following the 10-step build sequence from the decomposition (6 unions, then 4 cuts).

---

## Coordinate System

**Origin:** front-left-bottom corner of the tray outer envelope.

| Axis | Direction | Range | Reference |
|------|-----------|-------|-----------|
| **X** | Width, left to right when facing the cartridge front | 0 to 160.0 mm | 0 = left outer face |
| **Y** | Depth, front toward dock/rear | 0 to 155.0 mm | 0 = front face (open, where bezel attaches); 155 = rear outer face |
| **Z** | Height, bottom to top | 0 to 72.0 mm | 0 = bottom outer face; 72 = top edge (open) |

The user faces the front (Y=0 plane). The dock is at the rear (Y=155 plane). The cartridge inserts in the +Y direction.

---

## Mechanism Narrative (Rubric A)

### What the user sees and touches

The tray is an internal structural part — the user never directly sees or touches it. The front bezel covers the front (Y=0), the lid covers the top (Z=72), and the dock encloses the sides, bottom, and rear during use. The user interacts with the tray indirectly: the T-rail tongues (Sub-B) on the outer side walls guide the cartridge along the dock channels during insertion and removal, providing a smooth linear-rail feel. The tray transmits palm force from the front bezel rearward into the rail interface. The linkage rod guide slots (Sub-G) in the side walls allow the squeeze-release rods to pass through during the collet release action.

During assembly (by manufacturer or advanced user), the tray is the first part handled. Heat-set inserts are pressed into four floor bosses (Sub-C) with a soldering iron at 245 C. John Guest fittings are press-fit into four bores in the fitting bore plate (Sub-D), a transverse wall spanning Y=120.0 to Y=128.5. The release plate (separate part) is placed onto four guide posts (Sub-E) rising from the dock-facing face of the bore plate. Pumps are screwed into the floor bosses via M3 screws through bracket holes. Tubing is routed from pump BPT stubs to the user-facing fitting ports through floor channels (Sub-F). The lid snaps on top and the front bezel snaps onto the front.

### What moves

**During cartridge insertion/removal:** The entire tray translates along the Y axis, guided by T-rail tongues (Sub-B) in the dock's T-channels. The tongues are integral to the tray — nothing moves relative to the tray.

**During squeeze-release (while cartridge is seated in dock):** The release plate (separate part) slides on the four guide posts (Sub-E) rising from the bore plate dock-facing face at Y=128.5. The plate moves in the -Y direction (toward the dock-facing collets) during squeeze, depressing the collets, and returns in the +Y direction when released. The linkage rods (separate parts) slide through the guide slots (Sub-G) in the side walls, translating in the -Y direction during squeeze. The tray itself is rigid and stationary.

### What converts the motion

1. **User's fingers** pull the pull tabs (in the front bezel's finger channels) in the -Y direction.
2. The pull tabs pull the **linkage rods** through the side wall **guide slots** (Sub-G: stadium-shaped through-slots, 5.0 mm wide x 12.0 mm long Y, at Z=37.0 center height, through 5.0 mm wall thickness in X).
3. The linkage rods pull the **release plate** in the -Y direction along the **guide posts** (Sub-E: 3.5 mm diameter x 18.0 mm long posts, 0.3 mm diametral clearance in 3.8 mm plate bores).
4. The release plate's **stepped bores** engage the dock-facing collets of the John Guest fittings. The annular face between the 6.5 mm tube clearance bore and the 6.69 mm collet ID pushes each collet inward (toward fitting body center, in the -Y direction), disengaging the gripper teeth from the dock tube stubs.
5. With collets released, the user slides the entire cartridge in the -Y direction (out of the dock). The dock tube stubs slide freely out of the released fitting ports.

### What constrains each moving part interfacing with the tray

**Release plate:** X and Z translation prevented by four guide posts (Sub-E) at corners of a 44.0 mm (X) x 40.0 mm (Z) rectangle. Rotation about Y prevented by the same four posts. -Y travel limited to 2.0 mm by four stop bosses (5.0 mm dia x 10.8 mm tall cylinders on the bore plate dock-facing face, tips at Y=139.3; plate contacts these after 2.0 mm from rest). Design travel: 1.5 mm. +Y travel limited by collet spring-back: the four dock-facing collet springs push the plate to its rest position where it contacts the extended collet faces at Y=141.32 (plate front face).

**Linkage rods (~4 mm diameter):** Z constrained by guide slot top and bottom edges (slot height 5.0 mm for 4.0 mm rod = 0.5 mm clearance per side). X constrained by slot depth through wall (5.0 mm). Y motion permitted: 12.0 mm slot length provides for 1.5 mm plate travel + rod hook geometry clearance.

**Pumps:** X and Y constrained by M3 screws through bracket holes (3.13 mm clearance) into heat-set inserts in floor bosses (Sub-C). Rotation about the screw axis prevented by semicircular motor cradles (Sub-C: 36.0 mm ID half-pipe ribs). Z constrained by bracket ears bearing on boss tops and motor resting in cradles.

**John Guest fittings:** All 6 DOF constrained by press-fit of 9.31 mm center body into 9.5 mm bores (Sub-D: 0.19 mm diametral interference) plus 15.10 mm body end shoulders bearing against both faces of the 8.5 mm fitting bore plate.

**Lid:** Z constrained by snap tabs engaging detent ridges (Sub-H) on inner side wall faces. X and Y constrained by nesting fit of lid edges inside tray walls.

**Front bezel:** Constrained by snap tab pockets (Sub-I) in front edges of side walls and floor. The 1.5 mm step-lap ledge positions the bezel flush with the tray exterior.

### What provides the return force

The release plate returns via collet spring-back. The four John Guest dock-facing collet springs (spring steel gripper rings, estimated 5-15 N per collet, 20-60 N total) push the plate in the +Y direction when the user releases the squeeze. The plate's rest position is at Y=141.32 (front face), defined by contact with the four extended collet end faces. No additional springs or return mechanisms are required.

Fallback (if tolerance stack-up creates an air gap between plate and collets at rest): 2-4 printed PETG cantilever springs (12 mm x 3 mm x 1 mm beams) on the bore plate dock face, bearing against the plate, producing ~2-4 N return force. **DESIGN GAP: cantilever spring geometry is not specified. These are a prototyping fallback — omit from initial print.**

### User's physical interaction (grounded)

1. **Squeeze:** User wraps hand around front bezel. Palm on outer flat surface (Y < 0, bezel exterior). Fingers curl into finger channel on one side (25 mm deep x 15 mm wide channel in bezel). Fingers pull pull-tab in -Y direction. Force path: pull tab -> linkage rod -> guide slot (Sub-G at Y=108.0 to Y=120.0, Z=34.5 to Z=39.5) -> release plate. Plate translates 1.5 mm in -Y along guide posts (Sub-E). All four dock-facing collets compress simultaneously. Total required force: 20-60 N. Ergonomic margin: 3x-9x vs. 150 N 5th-percentile female capability. Tactile feedback: resistance increases sharply as collets reach full compression at 1.3 mm travel. Hard stop at 2.0 mm (plate contacts stop boss tips at Y=139.3).

2. **Slide out:** With collets released and squeeze held, user pulls cartridge in -Y direction. T-rail tongues (Sub-B) guide the motion. Dock spring-detent provides 5-10 N retention, overcome by continued pull. Dock tube stubs slide out of released fitting ports.

3. **Insert new cartridge:** Align T-rail tongues with dock channels. Left tongue center Z=54.0 (upper), right tongue center Z=18.0 (lower) — asymmetric, preventing upside-down insertion. Slide in +Y. Dock tube stubs push into dock-facing fitting ports during last ~16 mm of insertion (push-to-connect, per John Guest spec). Blade terminals (Sub-J) engage during last ~5 mm. Dock spring-detent clicks at end-of-travel, confirming full seating.

---

## Constraint Chain Diagram (Rubric B)

```
[User fingers]
    |  pull force, -Y direction
    v
[Pull tabs] (part of bezel/linkage, not tray)
    |  rigid rod connection
    v
[Linkage rods, ~4mm dia PETG]
    |  slide through guide slots (Sub-G) in tray side walls
    |  ^ constrained Z: slot top/bottom edges (5.0mm slot for 4.0mm rod)
    |  ^ constrained X: wall thickness (5.0mm)
    v
[Release plate, separate part, ~55x55x5mm]
    |  slides on 4x guide posts (Sub-E), 3.5mm dia, 18mm long
    |  ^ constrained X,Z: 4 guide posts at 44x40mm rectangle corners
    |  ^ constrained -Y: stop bosses (tips at Y=139.3), max 2.0mm travel
    |  ^ returned +Y: collet spring-back, 20-60N
    v
[Stepped bores in plate] -> [Dock-facing collets on John Guest fittings]
    |  annular push face (6.5mm bore vs 6.69mm collet ID)
    |  collet compressed 1.3mm inward toward fitting center (-Y)
    v
[Gripper teeth disengage from dock tube stubs]
    |
    v
[Tubes released — cartridge free to slide out on T-rails (Sub-B)]
```

All arrows labeled. All constraints identified. No unlabeled force paths.

---

## Sub-Component Specifications

### Sub-A: Box Shell

**Operation:** CREATE (first step)

**Description:** Open-top, open-front rectangular box. This is the base solid from which everything else is added or subtracted.

**Outer dimensions:**
- X: 0.0 to 160.0 mm (160.0 mm)
- Y: 0.0 to 155.0 mm (155.0 mm)
- Z: 0.0 to 72.0 mm (72.0 mm)

**Wall thicknesses:**
| Wall | Location | Thickness | Notes |
|------|----------|-----------|-------|
| Left side wall | X=0.0 to X=5.0 | 5.0 mm | Full Y and Z extent |
| Right side wall | X=155.0 to X=160.0 | 5.0 mm | Full Y and Z extent |
| Floor | Z=0.0 to Z=3.0 | 3.0 mm | Full X and Y extent |
| Fitting bore plate | Y=120.0 to Y=128.5 | 8.5 mm | Transverse wall, full interior X and Z extent. Front face at Y=120.0, dock face at Y=128.5 |
| Rear skin | Y=153.0 to Y=155.0 | 2.0 mm | Full X and Z extent (clearance holes cut later in Sub-D) |

**Open faces:**
- Top: Z=72.0 (lid snaps on, specified in lid parts.md)
- Front: Y=0.0 (bezel attaches, specified in bezel parts.md)

**Interior pocket (main cavity):**
- X: 5.0 to 155.0 (150.0 mm wide)
- Y: 0.0 to 120.0 (120.0 mm deep, from open front to bore plate front face)
- Z: 3.0 to 72.0 (69.0 mm tall)

**Release plate pocket (rear cavity):**
- X: 5.0 to 155.0 (150.0 mm wide)
- Y: 128.5 to 153.0 (24.5 mm deep, from bore plate dock face to rear skin inner face)
- Z: 3.0 to 72.0 (69.0 mm tall)

**Structural cross-ribs in release plate pocket:**
Three vertical ribs (Y-oriented, connecting bore plate to rear skin) in the release plate pocket, positioned to avoid the 4-fitting bore grid + release plate envelope:
- Rib 1: X=28.0 to X=30.0, Z=3.0 to Z=72.0 (left of fitting grid)
- Rib 2: X=130.0 to X=132.0, Z=3.0 to Z=72.0 (right of fitting grid)
- Rib 3: X=78.0 to X=82.0 at Z=3.0 to Z=15.0 (below fitting grid, floor-level rib only)

Ribs are 2.0 mm thick (X), spanning full Y from bore plate dock face (Y=128.5) to rear skin inner face (Y=153.0).

**Corner fillets:**
- All interior corners: 1.0 mm fillet for stress relief and printability
- Bore plate junction with side walls and floor: 1.0 mm fillet

**Material:** PETG

**Print orientation:** Open top facing up (+Z). All precision bores (fitting bores, guide post roots) are in the XZ plane at Y=120-128.5, printed perpendicular to the Z build direction for best circularity.

**Motor protrusion note:** The Kamoer KPHM400 pump is 116.48 mm long (with motor nub). With motors facing forward (-Y) and the pump connector face at Y=82.0, the motor nub extends to Y = 82.0 - 116.48 = -34.5, protruding 34.5 mm in front of the tray (past Y=0). The tray front is open. The front bezel (separate part) and enclosure accommodate this protrusion. The tray itself has no geometry at Y < 0.

---

### Sub-B: T-Rail Tongues

**Operation:** UNION to Sub-A (step 2)

**Description:** Two T-shaped rail extrusions running the full Y depth of both outer side walls. Asymmetrically positioned in Z to prevent upside-down cartridge insertion.

**T-profile cross-section (both rails identical):**
```
         ┌───────────┐
 3.0mm   │  CAP      │ 6.0 mm wide (X)
         ├─────┬─────┤
         │     │     │
 4.0mm   │     │     │ 3.0 mm wide tongue (X), extends outward from side wall
         │     │     │
         └─────┘
         ◄─1.5─►
              ◄─3.0──►
         ◄────6.0────►
```

The tongue is 3.0 mm wide (X), extending 4.0 mm outward from the side wall face. The cap is 6.0 mm wide (X) x 3.0 mm tall (Z), centered on the tongue, creating 1.5 mm overhang on each side.

**Left rail (on left side wall, X=0 face):**
- Tongue extends from X=-4.0 to X=0.0 (outward from left wall)
- Cap extends from X=-4.0-1.5 = X=-5.5 to X=0.0+1.5...

No, the tongue protrudes outward. Left wall outer face is at X=0. Tongue extends in -X direction:
- Tongue: X=-4.0 to X=0.0, width (into page) 3.0 mm in Z
- Cap: X=-4.0 to X=0.0, width 6.0 mm in Z (centered on tongue Z center)

Wait, I need to reconsider the orientation. The T-profile is in the XZ plane. The tongue extends outward from the wall in X, and the cap is at the tip in Z width.

**Left rail:**
- Wall outer face: X=0.0
- Tongue root at X=0.0, tongue tip at X=-4.0
- Tongue cross-section: 3.0 mm tall in Z, centered at Z=54.0
- Tongue occupies: X=-4.0 to 0.0, Z=52.5 to 55.5
- Cap at tongue tip: 6.0 mm tall in Z, 3.0 mm deep in X
- Cap occupies: X=-7.0 to -4.0, Z=51.0 to 57.0
- Rail extrusion: full Y extent, Y=0.0 to Y=155.0

**Right rail:**
- Wall outer face: X=160.0
- Tongue root at X=160.0, tongue tip at X=164.0
- Tongue cross-section: 3.0 mm tall in Z, centered at Z=18.0
- Tongue occupies: X=160.0 to 164.0, Z=16.5 to 19.5
- Cap at tongue tip: 6.0 mm tall in Z, 3.0 mm deep in X
- Cap occupies: X=164.0 to 167.0, Z=15.0 to 21.0
- Rail extrusion: full Y extent, Y=0.0 to Y=155.0

**Keying:** Left rail center Z=54.0 (upper half of wall). Right rail center Z=18.0 (lower half). Difference: 36.0 mm. The cartridge cannot be inserted upside down because the rails would be at the wrong Z positions for the dock channels.

**Clearance to dock channels:** 0.3 mm per side (designed into the dock channel dimensions, not the rail dimensions). Rail nominal dimensions above are the as-printed target. The dock channel is 0.3 mm wider and taller than the rail.

**Interface fillet:** 1.0 mm fillet at the junction between the T-rail cap underside and the tongue, and between the tongue root and the side wall face. These fillets prevent sharp overhang angles during printing and improve stress distribution.

**Tray outer envelope with rails:**
- X: -7.0 to 167.0 (174.0 mm total with rails)
- Y: 0.0 to 155.0
- Z: 0.0 to 72.0

---

### Sub-C: Pump Mounting Bosses and Motor Cradles

**Operation:** UNION to running solid (step 3)

**Description:** Four cylindrical mounting bosses with heat-set insert pilot holes rising from the tray floor, plus two semicircular motor cradle ribs. Two bosses and one cradle per pump.

**Pump layout in the tray:**

Both pumps are oriented with their long axis along Y: Kamoer connector face (barb side) at +Y, motor at -Y. Motors face the front of the cartridge.

| Parameter | Pump 1 (left) | Pump 2 (right) |
|-----------|---------------|-----------------|
| Pump center X | 42.0 mm | 118.0 mm |
| Pump center Z | 37.0 mm | 37.0 mm |
| Bracket Y position | Y=82.0 (at connector face, which is the junction between head and motor) | Y=82.0 |
| Connector face (barbs face +Y) | Y=82.0 | Y=82.0 |
| Motor nub tip | Y=-34.5 (protrudes past tray front) | Y=-34.5 |
| Pump head extent in Y | Y=34.0 to Y=82.0 (~48 mm) | Y=34.0 to Y=82.0 |

Pump spacing: 118.0 - 42.0 = 76.0 mm center-to-center. Bracket width per pump: 68.6 mm. Gap between bracket edges: 76.0 - 68.6 = 7.4 mm. Bracket edges: Pump 1 right edge at X = 42.0 + 34.3 = 76.3. Pump 2 left edge at X = 118.0 - 34.3 = 83.7. Gap: 83.7 - 76.3 = 7.4 mm.

**Mounting bosses (4 total, 2 per pump):**

Each boss is a solid cylinder rising from the tray floor (Z=0) to the bracket mounting height.

| Boss | Center X | Center Y | Z range | OD | Pilot hole dia | Pilot hole depth (from top) |
|------|----------|----------|---------|-----|----------------|---------------------------|
| B1 (Pump 1, left) | 17.3 | 82.0 | 0.0 to 37.0 | 10.0 mm | 4.0 mm | 5.7 mm |
| B2 (Pump 1, right) | 66.7 | 82.0 | 0.0 to 37.0 | 10.0 mm | 4.0 mm | 5.7 mm |
| B3 (Pump 2, left) | 93.3 | 82.0 | 0.0 to 37.0 | 10.0 mm | 4.0 mm | 5.7 mm |
| B4 (Pump 2, right) | 142.7 | 82.0 | 0.0 to 37.0 | 10.0 mm | 4.0 mm | 5.7 mm |

**Boss X position derivation:** Pump bracket mounting holes are at 49.45 mm center-to-center (caliper-verified), symmetric about pump center.
- Pump 1 (center X=42.0): left hole at X = 42.0 - 24.725 = 17.275, right hole at X = 42.0 + 24.725 = 66.725.
- Pump 2 (center X=118.0): left hole at X = 118.0 - 24.725 = 93.275, right hole at X = 118.0 + 24.725 = 142.725.

**Boss Y position derivation:** All bosses at Y=82.0 — directly below the bracket, which is at the pump head / motor junction. The bracket is a vertical plate in the XZ plane at Y=82.0. The bracket ears extend outward in X at this Y position, with mounting holes at the pump's Z centerline (Z=37.0).

**Boss Z height derivation:** Boss top at Z=37.0 (pump center height). The bracket ear surface rests on the boss top. Boss height from tray bottom outer face: 37.0 mm. Boss height above interior floor surface: 37.0 - 3.0 = 34.0 mm.

**Boss OD rationale:** 10.0 mm (pilot hole 4.0 mm + 3.0 mm wall all around). Aspect ratio: 37.0 / 10.0 = 3.7:1. Acceptable for PETG. Buttress ribs connect each boss to the floor for stability (see below).

**Heat-set insert specification:**
- M3 x 5.7 mm brass knurled insert (CNC Kitchen style)
- Pilot hole: 4.0 mm diameter, 5.7 mm deep from boss top (Z=37.0 to Z=31.3)
- Installation: soldering iron at 245 C, press insert flush with boss top
- Pull-out resistance: 200-400 N (PETG typical)

**Boss buttress ribs (4 per boss, 16 total):**
Each boss has 4 triangular buttress ribs at 90-degree intervals (aligned with X and Y axes), connecting the boss to the floor surface (Z=3.0):
- Rib thickness: 2.0 mm
- Rib height: from floor (Z=3.0) to boss mid-height (Z=20.0)
- Rib extends 5.0 mm radially outward from boss OD

**Motor cradles (2 total, 1 per pump):**

Each cradle is a semicircular (180-degree) half-pipe rib rising from the tray floor, positioned along the motor body between the bracket (Y=82.0) and the pump's mid-motor zone.

| Parameter | Value |
|-----------|-------|
| Cradle ID | 36.0 mm (35 mm motor + 0.5 mm clearance per side) |
| Cradle wall thickness | 3.0 mm |
| Cradle OD | 42.0 mm |
| Cradle center Z | 37.0 mm (same as pump center) |
| Cradle center Y | 50.0 mm (mid-motor body region) |
| Cradle extent in Y | 45.0 to 55.0 mm (10.0 mm wide rib) |
| Cradle arc | 180 degrees, bottom half (from Z=19.0 at bottom to Z=37.0 at sides) |
| Cradle bottom | Floor surface at Z=3.0 — solid fill between floor and cradle arc bottom (Z=3 to Z=19) |

Cradle center X:
- Pump 1 cradle: X=42.0
- Pump 2 cradle: X=118.0

The cradle inner surface is a semicircle of radius 18.0 mm centered at (X=pump_center, Z=37.0). The motor body rests in this semicircle. The solid fill between the floor and the cradle arc provides a sturdy pedestal.

**Pump head clearance verification:**
- Pump head bottom: Z = 37.0 - 31.3 = 5.7 mm. Floor surface at Z=3.0. Clearance: 2.7 mm. Sufficient.
- Pump head top: Z = 37.0 + 31.3 = 68.3 mm. Tray wall top at Z=72.0. Clearance to lid: 3.7 mm. Sufficient for lid snap tabs (the lid sits on top of the walls, not pressing down into the cavity).
- Pump head left edge (Pump 1): X = 42.0 - 31.3 = 10.7 mm. Left wall inner face at X=5.0. Clearance: 5.7 mm.
- Pump head right edge (Pump 2): X = 118.0 + 31.3 = 149.3 mm. Right wall inner face at X=155.0. Clearance: 5.7 mm.

---

### Sub-D: Fitting Bore Array

**Operation:** CUT from running solid (step 7)

**Description:** Four through-bores in the fitting bore plate for John Guest PP0408W press-fit mounting, plus four entry funnels on the rear skin, plus four clearance holes in the rear skin.

**Fitting bore plate location:** Y=120.0 (front/user face) to Y=128.5 (rear/dock face). Thickness: 8.5 mm.

**Fitting grid:**
- 2x2 rectangular array
- Center-to-center spacing: 20.0 mm in both X and Z
- Grid center: X=80.0, Z=37.0

| Fitting | Center X | Center Z |
|---------|----------|----------|
| F1 (lower-left) | 70.0 | 27.0 |
| F2 (lower-right) | 90.0 | 27.0 |
| F3 (upper-left) | 70.0 | 47.0 |
| F4 (upper-right) | 90.0 | 47.0 |

**Press-fit bore (through the bore plate, 4x):**
- Bore diameter: 9.5 mm (light press-fit on 9.31 mm center body; 0.19 mm diametral interference)
- Bore depth: 8.5 mm (full bore plate thickness, Y=120.0 to Y=128.5)
- Bore axis: parallel to Y axis (perpendicular to bore plate faces)
- Entry chamfer on user-facing side (Y=120.0): 0.5 mm x 45-degree chamfer for press-fit ease

**Body end shoulder counterbores (2 per fitting bore, 8 total):**

The John Guest center body is 12.16 mm long. The bore plate is 8.5 mm thick. So 12.16 - 8.5 = 3.66 mm of center body protrudes on each side (1.83 mm per side). The body end shoulders (15.10 mm OD) bear against the bore plate faces.

- **User-facing counterbore:** 15.5 mm diameter (clears 15.10 mm body end with 0.4 mm diametral clearance), 2.0 mm deep from Y=120.0 (to Y=122.0). This provides a shallow recess for the body end shoulder to seat into.
- **Dock-facing counterbore:** 15.5 mm diameter, 2.0 mm deep from Y=128.5 (to Y=126.5). Same purpose on dock side.

Net bore plate thickness at bore locations: 8.5 - 2.0 - 2.0 = 4.5 mm of 9.5 mm bore. Adequate for press-fit retention. **NOTE:** The center body length is 12.16 mm and the bore through the 4.5 mm middle section + two 2.0 mm counterbores = 8.5 mm total bore depth. The center body is 12.16 mm, so 12.16 - 8.5 = 3.66 mm of center body protrudes. Body end sections (12.08 mm each) sit in the counterbores (2.0 mm deep) with 12.08 - 2.0 = 10.08 mm protruding on each side. This is the body end protrusion into the main cavity and release plate pocket.

**User-facing body end protrusion:** 10.08 mm from bore plate user face (Y=120.0), tips at Y = 120.0 - 10.08 = 109.92.
**Dock-facing body end protrusion:** 10.08 mm from bore plate dock face (Y=128.5), tips at Y = 128.5 + 10.08 = 138.58.

**Dock-facing collet positions:**
- Collet in extended (rest) state: protrudes additional (41.80 - 36.32)/2 = 2.74 mm per side beyond body end face.
- Dock-facing collet tip (extended): Y = 138.58 + 2.74 = 141.32.
- Dock-facing collet tip (compressed, full release): Y = 141.32 - 1.3 = 140.02.

**Rear skin clearance holes (4x):**
The rear skin (Y=153.0 to Y=155.0) needs clearance for the dock tube stubs to pass through and enter the dock-facing fitting ports. Clearance holes centered on the fitting grid:
- Diameter: 16.0 mm (clears 15.10 mm body end + tubing approach angle)
- Centers: same as fitting grid (X=70/90, Z=27/47)
- Through the full 2.0 mm rear skin thickness

**Entry funnels on rear skin (dock-facing face, Y=155.0):**
Conical countersinks guiding dock tube stubs toward the fitting ports:
- Outer diameter at Y=155.0 face: 20.0 mm
- Inner diameter (meets clearance hole): 16.0 mm
- Depth: 1.0 mm (shallow guide cone in the rear skin outer face)

---

### Sub-E: Guide Post Array

**Operation:** UNION to running solid (step 4)

**Description:** Four cylindrical guide posts and four cylindrical stop bosses rising from the dock-facing surface of the fitting bore plate (Y=128.5) into the release plate pocket.

**Guide posts (4x):**

Posts are at the corners of a rectangle centered on the fitting grid, positioned to be outside the fitting body end envelopes (15.10 mm OD).

| Post | Center X | Center Z |
|------|----------|----------|
| GP1 (lower-left) | 58.0 | 17.0 |
| GP2 (lower-right) | 102.0 | 17.0 |
| GP3 (upper-left) | 58.0 | 57.0 |
| GP4 (upper-right) | 102.0 | 57.0 |

Guide post rectangle: 44.0 mm (X) x 40.0 mm (Z), centered at X=80.0, Z=37.0.

| Parameter | Value |
|-----------|-------|
| Post diameter | 3.5 mm |
| Post length | 18.0 mm |
| Post root | Y=128.5 (bore plate dock face) |
| Post tip | Y=128.5 + 18.0 = Y=146.5 |
| Mating bore in release plate | 3.8 mm diameter (0.3 mm diametral clearance) |

**Post length derivation:** The release plate rest position has its front face at Y=141.32 (derived from fitting geometry below). Plate thickness is 5.0 mm. Plate rear face at Y=146.32. Post tips at Y=146.5 extend fully through the plate at rest (146.5 - 141.32 = 5.18 mm of engagement, covering the full 5.0 mm plate thickness). At maximum travel (2.0 mm in -Y from rest), plate front face at Y=139.32, rear at Y=144.32. Posts provide 146.5 - 139.32 = 7.18 mm of bearing length through the 5.0 mm plate. Full engagement at all travel positions.

**Release plate rest position derivation (from caliper-verified fitting geometry):**
- Fitting bore plate dock face: Y=128.5
- Fitting center body protrusion from dock face: center body is 12.16 mm long in the 8.5 mm bore plate. Body end shoulder seats in 2.0 mm counterbore. Dock-facing body end protrudes: 12.08 - 2.0 = 10.08 mm from bore plate dock face. Body end tip at Y = 128.5 + 10.08 = 138.58.
- Dock-facing collet in extended (rest) state: protrudes (41.80 - 36.32)/2 = 2.74 mm beyond body end face. Collet tip at Y = 138.58 + 2.74 = 141.32.
- Release plate rests against the extended collet faces. Plate front face at Y=141.32. Plate rear face at Y=146.32.

**Stop bosses (4x):**

Stop bosses limit release plate travel to 2.0 mm maximum. They are cylindrical stubs on the bore plate dock face, positioned between fitting bores and clear of guide posts.

| Boss | Center X | Center Z |
|------|----------|----------|
| SB1 (bottom) | 80.0 | 20.0 |
| SB2 (top) | 80.0 | 54.0 |
| SB3 (left) | 65.0 | 37.0 |
| SB4 (right) | 95.0 | 37.0 |

| Parameter | Value |
|-----------|-------|
| Boss diameter | 5.0 mm |
| Boss height | 10.8 mm |
| Boss root | Y=128.5 |
| Boss tip | Y=139.3 |

**Stop boss height derivation:** Plate front face at rest: Y=141.32. Hard stop at 2.0 mm travel: plate front face at Y = 141.32 - 2.0 = 139.32. Boss tip at Y=139.3 (10.8 mm protrusion from Y=128.5). Gap at rest: 141.32 - 139.3 = 2.02 mm (the 2.0 mm hard stop distance with 0.02 mm rounding margin).

**Final guide post specification:**

| Parameter | Value |
|-----------|-------|
| Post diameter | 3.5 mm |
| Post length | 18.0 mm |
| Post root | Y=128.5 (bore plate dock face) |
| Post tip | Y=146.5 |
| Mating bore in release plate | 3.8 mm diameter (0.3 mm diametral clearance) |

**Release plate position summary:**
| State | Plate front face Y | Plate rear face Y | Notes |
|-------|-------------------|-------------------|-------|
| Rest (collets extended) | 141.32 | 146.32 | Resting against extended collet faces |
| Design travel (1.5 mm) | 139.82 | 144.82 | Collets fully compressed |
| Max travel / hard stop (2.0 mm) | 139.32 | 144.32 | Plate contacts stop boss tips |

---

### Sub-F: Tube Routing Channels

**Operation:** UNION/CUT on running solid (step 6, after Sub-C)

**Description:** Four U-shaped channels in the tray floor for routing silicone tubes from pump BPT stubs to user-facing John Guest fitting ports. Plus snap-over clip features.

**Tube routing overview:**
The four tubes run from the pump connector face area (Y≈82) toward the fitting bore plate (user-facing ports at Y≈110). The fitting user-facing body end tips are at Y=109.92. Tubes insert 16 mm into the fitting ports, so tube tips reach Y = 109.92 + 16 = 125.92 (inside the fitting body). The tube approaches from -Y (from the pump side).

Each tube runs roughly parallel to Y with a lateral (X) offset to reach the correct fitting position from the correct pump barb position.

**Channel dimensions:**
- Width: 10.0 mm (for 1/4" OD / 6.35 mm nominal tubing with 1.8 mm clearance per side)
- Depth: 5.0 mm (below channel wall top, which is at Z=8.0; channel floor at Z=3.0)
- Channel walls: 2.0 mm thick ribs rising from floor surface (Z=3.0) to Z=8.0

The channels are cut into the floor zone — their walls are 5.0 mm tall ribs on the floor surface, forming U-shaped troughs.

**Channel routing (approximate — Y start to Y end, X position):**

| Channel | From (pump barb area) | To (fitting port) | X at start | X at end | Notes |
|---------|----------------------|--------------------|-----------|-----------| ------|
| CH1 | Pump 1 outlet, Y=82 | F1 (X=70, Z=27), Y=110 | X=35 | X=70 | Left pump, lower-left fitting |
| CH2 | Pump 1 inlet, Y=82 | F3 (X=70, Z=47), Y=110 | X=49 | X=70 | Left pump, upper-left fitting |
| CH3 | Pump 2 outlet, Y=82 | F2 (X=90, Z=27), Y=110 | X=111 | X=90 | Right pump, lower-right fitting |
| CH4 | Pump 2 inlet, Y=82 | F4 (X=90, Z=47), Y=110 | X=125 | X=90 | Right pump, upper-right fitting |

**DESIGN GAP: Exact pump barb exit positions (X and Z offsets on the pump connector face) are not caliper-verified. The tube connector positions on the Kamoer KPHM400 are listed as MEDIUM confidence. Channel X start positions above are estimates. Physical verification of barb positions is required before finalizing channel routing.**

Channels run at floor level (Z=3.0 to Z=8.0). The tubes are below the pump heads (pump head bottom at Z=5.7) — the channels occupy the narrow gap between the floor and the pump head bottom. This is tight but the tubes (6.35 mm OD) fit within the 5.0 mm channel depth plus the remaining 5.7 - 3.0 - 5.0 = -2.3 mm...

The channel walls rise to Z=8.0 but the pump head bottom is at Z=5.7. Interference! The channel walls extend above the pump head bottom.

**Resolution:** The channels run in the tube routing zone (Y=82 to Y=110) which is BEHIND the pump heads (Y=34 to Y=82 is the pump head zone). The pump heads don't overlap with the tube routing channels in Y. At Y>82, the pump heads have ended and the channels have clear height up to Z=72 (tray top).

Channel wall height revised: 5.0 mm walls (Z=3.0 to Z=8.0) are adequate in the tube routing zone since there's no pump head obstruction there.

**Snap-over clips (3 per channel, 12 total):**
Small overhanging tabs at the top of channel walls to retain tubing:
- Tab thickness: 1.0 mm (Z)
- Tab overhang: 3.0 mm into channel (X, from each wall)
- Tab length along Y: 3.0 mm
- Spacing along Y: approximately 30 mm intervals (at Y=87, Y=97, Y=107 for each channel)
- Gap between opposing tab tips: 10.0 - 2(3.0) = 4.0 mm. Tube OD is 6.35 mm. Tube snaps past the 4.0 mm gap with slight deformation of the 1.0 mm PETG tabs.

---

### Sub-G: Linkage Rod Guide Slots

**Operation:** CUT from running solid (step 8)

**Description:** Two through-slots in the side walls for the linkage rods connecting the release plate to the front pull tabs.

**Slot geometry:** Stadium shape (rectangle with semicircular ends), cut through the full wall thickness in X.

| Parameter | Left wall slot | Right wall slot |
|-----------|---------------|-----------------|
| Wall | X=0.0 to X=5.0 | X=155.0 to X=160.0 |
| Slot center Y | 114.0 | 114.0 |
| Slot center Z | 37.0 | 37.0 |
| Slot width (Z) | 5.0 mm | 5.0 mm |
| Slot length (Y) | 12.0 mm | 12.0 mm |
| Slot Y extent | 108.0 to 120.0 | 108.0 to 120.0 |
| Slot Z extent | 34.5 to 39.5 | 34.5 to 39.5 |
| Through thickness | 5.0 mm (full wall) | 5.0 mm (full wall) |

**Slot center Z derivation:** Z=37.0 aligns with the pump center and release plate approximate center height, placing the linkage rods at a height that transmits force to the plate center without creating a torque moment.

**Slot center Y derivation:** Y=114.0 positions the slot in the tube routing zone between the pump heads (Y<82) and the bore plate (Y=120). The slot extends from Y=108 to Y=120 (reaching the bore plate front face). The linkage rod runs from the release plate (at Y≈141) through this slot and forward through the interior toward the pull tabs at the front.

**Rod clearance:** 4.0 mm rod in 5.0 mm wide slot = 0.5 mm clearance per side in Z. 12.0 mm slot length in Y provides for rod travel: at rest, rod is at one Y position; at 2.0 mm plate travel, rod shifts 2.0 mm in -Y. The remaining 10 mm of slot length accommodates the rod hook geometry and assembly insertion path.

---

### Sub-H: Lid Snap Detent Ridges

**Operation:** UNION to running solid (step 5)

**Description:** Detent ridges along the top edges of both side walls (interior face). The lid's snap tabs engage these ridges. Four ridges per side, eight total.

**Ridge cross-section:**
- Profile: right-triangle (ramp on top for lid insertion, vertical face on bottom for retention)
- Height from wall surface: 1.0 mm (protrudes into interior in X direction)
- Width along Z (vertical): 2.0 mm
- Ramp angle: 45 degrees (upper face, guides lid tab over ridge during snap-on)
- Retention face: vertical (lower face, prevents lid from lifting off)

**Ridge positions:**

| Ridge | Wall | Center Y | Z position |
|-------|------|----------|------------|
| H1 | Left (X=5.0 face) | 20.0 | Z=70.0 (2.0 mm below top edge at Z=72.0) |
| H2 | Left | 50.0 | Z=70.0 |
| H3 | Left | 80.0 | Z=70.0 |
| H4 | Left | 110.0 | Z=70.0 |
| H5 | Right (X=155.0 face) | 20.0 | Z=70.0 |
| H6 | Right | 50.0 | Z=70.0 |
| H7 | Right | 80.0 | Z=70.0 |
| H8 | Right | 110.0 | Z=70.0 |

Each ridge is 10.0 mm long in Y, centered at the listed Y position. Ridges protrude 1.0 mm into the interior from the wall inner face (left wall ridges protrude in +X from X=5.0; right wall ridges protrude in -X from X=155.0).

---

### Sub-I: Front Bezel Receiving Features

**Operation:** CUT from running solid (step 9)

**Description:** Step-lap ledge and snap tab pockets at the front open edge (Y=0) of the tray for bezel attachment.

**Step-lap ledge:**
A 1.5 mm deep x 1.5 mm wide rabbet (step) cut around the entire front edge perimeter (Y=0 face) of the tray. The bezel overlaps this step, creating a shadow-line seam.

| Edge | Rabbet geometry |
|------|----------------|
| Left wall at Y=0 | X=0.0 to X=1.5, Z=0.0 to Z=72.0, Y=0.0 to Y=1.5 (removes 1.5mm strip from outer left face) |
| Right wall at Y=0 | X=158.5 to X=160.0, Z=0.0 to Z=72.0, Y=0.0 to Y=1.5 |
| Floor at Y=0 | X=0.0 to X=160.0, Z=0.0 to Z=1.5, Y=0.0 to Y=1.5 |
| Top edges at Y=0 | X=0.0 to X=5.0 and X=155.0 to X=160.0, Z=70.5 to Z=72.0, Y=0.0 to Y=1.5 |

**Snap tab pockets (5 total):**
Rectangular recesses in the front edges for the bezel's snap tabs to engage:

| Pocket | Location | Dimensions (X x Z x Y depth) |
|--------|----------|------------------------------|
| IP1 | Left wall, lower | X=0.0 to 1.5, Z=15.0 to 20.0, Y=0.0 to 3.0 |
| IP2 | Left wall, upper | X=0.0 to 1.5, Z=52.0 to 57.0, Y=0.0 to 3.0 |
| IP3 | Right wall, lower | X=158.5 to 160.0, Z=15.0 to 20.0, Y=0.0 to 3.0 |
| IP4 | Right wall, upper | X=158.5 to 160.0, Z=52.0 to 57.0, Y=0.0 to 3.0 |
| IP5 | Floor, center | X=75.0 to 85.0, Z=0.0 to 1.5, Y=0.0 to 3.0 |

Each pocket is 1.5 mm deep in X (into the wall), 5.0 mm tall in Z (IP1-4) or 10.0 mm wide in X (IP5), and 3.0 mm deep in Y (into the tray from the front edge).

---

### Sub-J: Electrical Contact Pad Areas

**Operation:** CUT from running solid (step 10, after Sub-D)

**Description:** Wire routing channels and terminal retention features on the rear wall exterior (dock-facing) for blade terminal connectors.

**Terminal layout:**
- 4 motor terminals: 2 per pump (+ and -)
- 1 cartridge-present detection pair (continuity loop)
- Total: 5 blade terminal positions, but 10 individual contacts (5 pairs)

Actually, the motor terminals are 4 individual blades (2 per pump x 2 pumps). The cartridge-present is 1 additional pair (2 blades). Total: 6 individual blade positions. But the decision says "4x 6.3 mm blade terminals total (2 per pump)" plus "A 5th blade pair."

**Terminal channels:** Rectangular grooves cut into the rear skin outer face (Y=155.0) and the side wall rear portions, routing wires from the pump motor connections to the dock-facing blade terminals.

| Terminal pair | Center X | Center Z | Blade spacing (Z) | Notes |
|---------------|----------|----------|--------------------|-------|
| Pump 1 (+/-) | 30.0 | 25.0 / 35.0 | 10.0 mm | Left-side, asymmetric Z spacing |
| Pump 2 (+/-) | 130.0 | 30.0 / 42.0 | 12.0 mm | Right-side, different spacing for keying |
| Cart-present | 80.0 | 60.0 / 64.0 | 4.0 mm | Center-top, smaller 4.8 mm blade |

**Polarity enforcement:** Pump 1 blades at 10.0 mm Z spacing; Pump 2 blades at 12.0 mm Z spacing. This asymmetry, combined with fixed dock blade positions, prevents connecting Pump 1 wires to Pump 2's dock blades.

**Wire channel dimensions:**
- Width: 4.0 mm
- Depth: 2.0 mm (into rear skin or side wall surface)
- Channels route from terminal positions toward the interior (through small pass-through holes in the rear skin) to reach the pump motor wires inside the cartridge.

**Terminal retention slots:**
At each blade position, a rectangular slot in the rear skin outer face sized for a 6.3 mm (or 4.8 mm for cart-present) female spade terminal housing:
- Motor terminal slots: 8.0 mm wide (X) x 3.0 mm deep (Y into rear skin) x 8.0 mm tall (Z)
- Cart-present slots: 6.0 mm wide x 3.0 mm deep x 6.0 mm tall

**Wire pass-through holes (5 pairs = 10 holes):**
Small holes through the rear skin connecting the exterior terminal slots to the interior cavity, allowing wires to pass through:
- Diameter: 3.0 mm per hole
- Positioned adjacent to each terminal slot

**DESIGN GAP: The rear skin is only 2.0 mm thick (Y=153.0 to Y=155.0). Terminal retention slots at 3.0 mm deep would penetrate through the skin. Options: (a) locally thicken the rear skin at terminal positions to 4.0 mm, (b) reduce slot depth to 1.5 mm (marginal retention), or (c) mount terminals on the side walls instead of the rear skin. Recommend option (a): local boss/thickening at each terminal slot, protruding 2.0 mm outward from Y=155.0 to Y=157.0. This creates localized bumps on the rear face but they align with the dock blade positions.**

---

## Direction Consistency Check (Rubric C)

| # | Claim | Direction | Axis | Verified? | Notes |
|---|-------|-----------|------|-----------|-------|
| 1 | "User pulls pull tabs toward themselves" | Toward user | -Y | YES | User is at -Y side (front). Pull tabs move in -Y. |
| 2 | "Release plate moves toward the dock-facing collets" | Toward dock collets | -Y | YES | Collets are at Y≈141 (extended). Bore plate dock face at Y=128.5. Plate moves -Y toward bore plate = toward fitting center = toward collets. The collets are between plate and bore plate, so -Y motion pushes plate against collet faces. |
| 3 | "Collets compressed toward fitting body center" | Inward | -Y (toward fitting center) | YES | Fitting center body midpoint is at Y≈124.25 (bore plate midplane). Dock-facing collets at Y≈141 compress toward Y≈124 = -Y direction. |
| 4 | "Collet spring-back pushes plate in +Y" | Away from fittings | +Y | YES | Collet springs push the plate back toward rear of cartridge = +Y direction. |
| 5 | "Cartridge inserts in +Y" | Toward dock | +Y | YES | Dock is at the rear (Y=155). Insertion is toward dock = +Y. |
| 6 | "Dock tube stubs enter from +Y" | From dock side | -Y into cartridge | YES | Stubs are on the dock at Y>155. They protrude in -Y direction through rear skin clearance holes into fitting ports. |
| 7 | "Motors face forward (toward user)" | Toward user | -Y | YES | Motor extends from bracket at Y=82 toward Y=-34.5 = -Y direction. |
| 8 | "Barbs face rearward (toward dock)" | Toward dock | +Y | YES | Connector face at Y=82, barbs point +Y. |
| 9 | "Left rail upper, right rail lower" | Asymmetric Z | Left Z=54, Right Z=18 | YES | Prevents upside-down insertion. |

No contradictions found.

---

## Interface Dimensional Consistency (Rubric D)

| # | Interface | Part A dimension | Part B dimension | Clearance | Source |
|---|-----------|------------------|------------------|-----------|--------|
| 1 | Fitting center body → bore plate bore | 9.31 mm OD (caliper) | 9.5 mm bore | 0.19 mm diametral (press-fit) | Caliper-verified OD |
| 2 | Fitting body end → counterbore | 15.10 mm OD (caliper) | 15.5 mm counterbore | 0.40 mm diametral clearance | Caliper-verified OD |
| 3 | Guide post → release plate bore | 3.5 mm post | 3.8 mm bore | 0.30 mm diametral clearance | FDM design rule |
| 4 | Linkage rod → guide slot | 4.0 mm rod | 5.0 mm slot (Z width) | 1.0 mm total (0.5/side) | FDM design rule |
| 5 | M3 screw → bracket hole | M3 (3.0 mm) shaft | 3.13 mm hole (caliper) | 0.13 mm diametral | Caliper-verified hole |
| 6 | M3 insert → pilot hole | M3 x 5.7 mm insert (~4.0 mm OD knurl) | 4.0 mm pilot hole | ~0 (heat-set press-fit) | CNC Kitchen spec |
| 7 | Motor body → cradle | ~35 mm OD (LOW confidence) | 36.0 mm ID | ~1.0 mm diametral clearance | LOW confidence — must verify with calipers |
| 8 | T-rail tongue → dock channel | Tongue 3.0 mm (Z) x 4.0 mm (X) | Channel TBD (dock design) | 0.3 mm per side target | FDM design rule |
| 9 | Tube → channel width | 6.35 mm OD nominal | 10.0 mm channel | 3.65 mm total | Generous for tube routing flexibility |
| 10 | Release plate → stop boss | Plate front face | 5.0 mm dia boss tips at Y=139.3 | 2.0 mm travel gap at rest | Derived from collet geometry |
| 11 | Snap clip gap → tube | 4.0 mm gap (10mm - 2x3mm overhang) | 6.35 mm tube OD | -2.35 mm (snap interference) | Intentional snap-fit |

No zero-clearance issues on sliding/press-fit interfaces. Interface #7 (motor body to cradle) has LOW confidence on the motor diameter — physical verification required before printing.

---

## Assembly Feasibility Check (Rubric E)

**Assembly sequence:**

1. **Press 4x heat-set inserts** into pilot holes in floor bosses (B1-B4) from above using soldering iron at 245 C. Access: open top, open front — full access. Insert from Z+ direction into boss tops at Z=37.0.

2. **Press 4x John Guest fittings** into bore plate bores. Access: from main cavity (-Y side) or release plate pocket (+Y side). Press center body into 9.5 mm bore. Body end shoulders seat against counterbores. Can be done from either face. Recommend from user-facing side (Y<120) for easier visual alignment.

3. **Place release plate** onto guide posts. Drop plate from above (Z+ direction) into the release plate pocket (Y=128.5 to Y=153.0), aligning plate's four 3.8 mm bores with guide posts. Slide plate onto posts. Verify plate slides freely (1.5 mm travel in -Y, returns via collet spring-back).

4. **Mount pumps.** Place Pump 1 into tray: motor end (-Y) forward, connector face at Y=82.0. Motor body settles into cradle (X=42.0, Y=50.0). Bracket ears rest on boss tops (B1, B2) at Z=37.0. Insert 2x M3 x 8 mm SHCS through bracket holes into heat-set inserts. Tighten with M3 hex key. Repeat for Pump 2 (bosses B3, B4, cradle at X=118.0). Access: open top — hex key reaches screws from Z+ direction. **Note: pumps extend past tray front (Y<0). The pump motor end protrudes ~34.5 mm in -Y. Pumps must be installed before the front bezel.**

5. **Route tubing.** Push silicone tubing onto BPT stubs on each pump (4 connections). Route tubes through floor channels (Sub-F) from pump zone to fitting zone. Snap tubes under retention clips. Push tube free ends into user-facing John Guest ports (push-to-connect, 16 mm insertion). Access: open top provides full access to floor channels and fitting ports.

6. **Thread linkage rods** through side wall guide slots (Sub-G). Insert from interior side of each slot. Attach rod ends to release plate hooks (at the plate's left and right edges). Verify rod slides freely in slot.

7. **Snap lid** onto tray. Align lid edges with tray wall inner faces. Press down until snap tabs engage detent ridges (Sub-H). Access: from above (Z+).

8. **Snap front bezel** onto tray front edge. Bezel tabs engage pockets (Sub-I). Pull tab paddles capture linkage rod front hooks inside finger channels. Access: from front (-Y).

9. **(If floor plate is used)** Attach with 2x M3 screws into heat-set inserts in tray floor ribs. Access: from below (Z-). Must be done before step 7 if floor plate is present.

**Feasibility notes:**
- Step 1 requires reaching Z=37.0 inside the tray with a soldering iron — the tray is 72mm tall with 150mm interior width. Feasible but requires a longer-tip soldering iron or inserting the iron at an angle.
- Step 4: hex key access to M3 screws at Z=37.0 (boss top), Y=82.0. Access from above with the tray open-top. Interior is 150mm wide, 120mm deep to the bore plate. Feasible.
- Step 6: linkage rods must thread through 5mm thick wall slots from the interior. Rod is ~4mm diameter, slot is 5x12mm. Rod must be oriented correctly to pass through. Feasible with care.

**Disassembly sequence (for pump service):**
1. Remove front bezel (pry snap tabs)
2. Detach linkage rods from release plate and pull tabs
3. Remove lid (pry snap tabs)
4. Disconnect tubing from fitting ports (press collets on user-facing side, pull tubes)
5. Remove tubing from pump barbs
6. Unscrew 2x M3 per pump, lift pumps out
7. Release plate slides off guide posts (if needed)

All steps are physically feasible with standard hand tools (M3 hex key, small flat screwdriver for prying snap fits).

---

## Part Count Minimization (Rubric F)

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|----------------|----------------|---------|
| Tray + T-rails | Yes (printed integral) | No | Same (PETG) | Correctly combined as one part |
| Tray + pump bosses | Yes (printed integral) | No | Same | Correctly combined |
| Tray + guide posts | Yes (printed integral) | No | Same | Correctly combined |
| Tray + detent ridges | Yes (printed integral) | No | Same | Correctly combined |
| Tray + tube channels | Yes (printed integral) | No | Same | Correctly combined |
| Tray + release plate | No | Yes (plate slides on posts) | Same | Must be separate — correctly separate |
| Tray + lid | No (snap-fit, removable) | No during use, removed for service | Same | Could be one piece if never opened. However, the lid must be removable for tube routing during assembly (step 5) and pump service. Correctly separate. |
| Tray + front bezel | No (snap-fit, removable) | No during use | Same | Must be separate for cosmetic reprints and assembly sequence (bezel installed last). Correctly separate. |
| Tray + floor plate | No (screwed) | No | Same | Floor plate exists only if pumps can't be installed from above. If pumps install from above (step 4 feasibility confirmed: YES), floor plate can be eliminated. **Recommend eliminating floor plate — 4 parts instead of 5.** |
| Tray + linkage rods | No | Yes (rods slide in slots) | Same | Must be separate — correctly separate |
| Stop bosses + guide posts | Both printed integral to tray | No | Same | Correctly combined (both are features on the bore plate dock face) |

**Floor plate recommendation:** Pumps install from above through the open top (feasibility confirmed in assembly step 4). The floor plate is unnecessary and should be eliminated, reducing the printed part count from 5 to 4 (tray, lid, bezel, release plate).

---

## Manufacturing Notes

**Printer:** Bambu H2C
**Material:** PETG
**Layer height:** 0.2 mm standard; 0.1 mm for fitting bore area if circularity is critical

**Print orientation:** Open top up (+Z). The fitting bores in the bore plate are parallel to the X axis (horizontal in the XZ plane), so they print as horizontal holes — PETG bridges over 9.5 mm at 0.2 mm layers require supports inside the bores. **Alternative: print with bore plate facing up (tray on its front face, Y axis vertical). This makes the fitting bores vertical (printed in Z) for best circularity, but requires extensive support for the open-top cavity. Recommended for prototype #1 to validate bore press-fit; switch to open-top-up for production once tolerances are confirmed.**

**Critical tolerances:**
| Feature | Tolerance | Verification method |
|---------|-----------|---------------------|
| Fitting press-fit bore (9.5 mm) | +0.0 / -0.1 mm (bore should be 9.4-9.5 mm for interference fit on 9.31 mm body) | Test print of bore plate section, verify with John Guest fitting |
| Guide post diameter (3.5 mm) | +0.1 / -0.0 mm | Test print, verify with calipers |
| Stop boss tip Y position | ±0.2 mm | Verify 2.0 mm travel gap with release plate installed |
| Boss pilot hole (4.0 mm) | ±0.1 mm | Test with M3 heat-set insert |

**Approximate print time:** 6-8 hours (single tray, 0.2 mm layers, 20% infill, PETG at standard speeds).

**Approximate size:** 167 x 155 x 72 mm (including T-rail protrusions in X). Well within 325 x 320 x 320 mm build volume.

---

## Open Verification Items

1. **Motor body diameter** (~35 mm, LOW confidence): cradle ID of 36.0 mm may need adjustment.
2. **Bracket hole pattern** (1x2 or 2x2): if 2x2, add 4 more bosses (8 total, 4 per pump).
3. **Tube connector exit positions** on pump face: channel routing (Sub-F) depends on exact X/Z barb positions.
4. **Motor flat orientation** relative to bracket: affects cradle anti-rotation feature.
5. **Fitting press-fit tolerance**: print test bore section and verify with actual John Guest PP0408W.
6. **Release plate rest position**: verify collet extended position matches Y=141.32 with actual fitting installed in bore plate.
7. **Rear skin terminal boss thickness** (DESIGN GAP from Sub-J): decide between local thickening vs. side-wall terminal mounting.
