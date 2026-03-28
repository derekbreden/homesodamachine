# Enclosure Tub (Structural Monocoque)

The tub is the structural core of the entire product. It is a five-sided open-top box (floor + left wall + right wall + back wall + partial front wall Z=0-130) that carries every internal load and defines every internal geometry. All sub-assemblies mount to the tub: valve rack to the floor, bag cradle brackets to the side walls and back wall, electronics shelf to the upper back wall, dock back wall to the interior, and the front panel and top panel attach to the tub's upper rim. The tub is permanent -- once assembled, it is never disassembled.

The tub prints as two halves split horizontally at Z=200, permanently joined with alignment pins + tongue-and-groove + CA glue. The two halves together form a single structural piece.

See `enclosure-concept.md` for the settled concept architecture. See `../../../planning/spatial-layout.md` for the master coordinate table. See `../../../planning/cartridge-architecture.md` for the cartridge dock interface.

**Coordinate system:** Origin at exterior front-bottom-left corner of the enclosure. X = width (0-220mm, positive rightward). Y = depth (0-300mm, positive toward rear). Z = height (0-400mm, positive upward).

---

## Mechanism Narrative

### Q0: What does the user see and touch?

The tub is mostly invisible. Its exterior surfaces are dark matte PETG with 6mm-radius vertical edges and 4mm-radius horizontal edges. The user sees four exterior faces: left, right, back, and the lower front (Z=0-130). The upper front (Z=130-400) is covered by the removable front panel. The top (Z=396-400) is covered by the removable top panel.

The lower front face (Z=0-130) presents the cartridge slot opening -- a 148mm x 84mm rectangular aperture centered in the 220mm width, with a 5mm x 45-degree chamfer on all four edges that reads as a deliberate frame. The 60mm knurled disc knob (part of the cartridge, not the tub) sits centered in this opening. Around the slot, the front wall is flat, uninterrupted dark matte PETG: 36mm on each side of the slot, 46mm above the slot to the Z=130 seam line. The 2mm reveal line at Z=130 (where the front panel meets the tub's partial front wall) is the only visible seam on the front face below the top panel.

The left, right, and back faces show a single hairline seam at Z=200 -- the permanent tub-half joint, sanded flush after CA glue. This seam is at bag-slab height and reads as a faint horizontal line on otherwise featureless dark matte surfaces.

The tub's upper rim (Z=396) is hidden beneath the top panel (1.5mm reveal line around three sides). Four snap-fit receptacle slots (two per side wall, at Z=200 and Z=340) are recessed into the interior face of the side walls -- invisible from outside.

The user touches the tub only indirectly: when sliding a cartridge along the dock floor rails, when pressing the front panel snap hooks to release them (pressing against the tub's interior wall flanges), or when lifting the top panel off the tub rim (the magnets pull against steel discs embedded in the tub's rim). In normal use (dispensing, hopper refill), the user never contacts the tub.

### Q1: What moves?

Nothing in the tub moves. The tub is entirely static structure. All moving elements belong to other parts: the cartridge slides along the dock rails (dock-back-wall part), the front panel snaps engage/disengage the tub's receptacle slots, and the top panel lifts off the tub rim.

### Q2: What converts motion?

Not applicable -- the tub has no mechanism. It receives forces from other mechanisms:
- Cartridge insertion/removal: rail friction along dock floor rails (integral to lower tub half floor).
- Front panel snap engagement: cantilever hooks deflect into receptacle slots in tub side walls.
- Top panel retention: magnetic attraction between neodymium discs in the top panel and steel discs in the tub rim.
- Static loads: bag weight (up to 4.5 kg when full) transferred through cradle brackets to side walls. Valve rack weight (~1.2 kg) transferred through M3 screw bosses to floor. Electronics shelf weight (~0.5 kg) transferred through brackets to back wall.

### Q3: What constrains each interface?

**Front panel to tub:**
- Four cantilever snap receptacle slots (two per side wall) constrain the front panel in Y (depth) and Z (height). Each slot is a 12mm-wide x 3mm-deep x 8mm-tall rectangular pocket cut into the interior face of the side wall, with a 1mm-deep chamfered entry ramp at the top to guide the hook tip during installation.
- The front panel's bottom tongue (3mm tall x 2mm deep, running full 220mm width) seats in a groove in the top face of the tub's partial front wall at Z=130, constraining X (lateral) and Y (depth) at the bottom edge.

**Top panel to tub:**
- A 3mm-wide x 2mm-tall tongue on the tub's upper rim perimeter (three sides: left, right, back) engages a matching groove in the top panel underside, constraining X and Y.
- Two 6x3mm neodymium disc magnets (one in each side wall rim, at Y=150) attract to steel discs embedded in the top panel, providing Z retention (vertical hold). Pull-off force: ~3N per magnet, 6N total -- enough to stay closed during normal use, easy to overcome with a firm upward pull.
- The front edge of the top panel butts against the top edge of the front panel at Z=396-400, constrained by the tongue-and-groove on the other three sides.

**Valve rack to tub floor:**
- Four M3 screw bosses (8mm OD, 4.2mm pilot hole for heat-set M3 inserts, 12mm tall) protrude from the tub floor at the valve rack mounting positions.

**Bag cradle to tub walls:**
- Three pairs of bracket slots (one pair at each end plus one at midpoint) cut into the interior faces of left and right side walls, accepting the cradle's mounting tabs.

**Electronics shelf to tub back wall:**
- Two L-shaped bracket ledges (10mm wide x 4mm thick, protruding 10mm from interior back wall face) at Z=340, spanning Y=220 to Y=290, provide shelf support.

**Dock back wall to tub interior:**
- The dock back wall (separate part, 148W x 10D x 84H mm) sits against the tub's interior at Y=130-140, secured by two M3 screw bosses on the tub floor and two M3 screw bosses on the tub side walls (within the cartridge slot zone).

### Q4: What provides return force?

Not applicable -- the tub is static. Return forces for interfacing parts:
- Front panel snaps: the cantilever hooks on the front panel are spring-loaded by their own material elasticity. The tub's receptacle slots are passive pockets.
- Top panel magnets: gravity provides the return force (lid sits on rim). Magnets provide retention against accidental displacement.

### Q5: User's physical interaction

The user does not interact with the tub directly. The tub is infrastructure -- the user interacts with the cartridge (twist knob, slide in/out), the front panel (press to release snaps), the top panel (lift off), and the hopper (pour). All of these interactions are mediated by other parts that interface with the tub's passive receptacles, rails, bosses, and rim features.

---

## Constraint Chain

```
[Bag weight: 4.5 kg max, distributed along diagonal cradle]
    | cradle mounting tabs into bracket slots in side walls
    v
[Tub side walls: 4mm PETG, static]
    | continuous wall to floor
    v
[Tub floor: 4mm PETG, static]
    | rubber feet on cabinet floor
    v
[Cabinet floor: reaction force]

[Valve rack: ~1.2 kg, static]
    | 4x M3 screws into heat-set inserts in floor bosses
    v
[Tub floor bosses: 8mm OD, 12mm tall, integral to floor]
    | continuous to floor
    v
[Tub floor → cabinet floor]

[Electronics shelf: ~0.5 kg, static]
    | rests on 2x L-bracket ledges
    v
[Tub back wall: 4mm PETG, static]
    | continuous to floor
    v
[Tub floor → cabinet floor]

[Front panel: ~0.15 kg, retained by 4 snaps + bottom tongue]
    | snap hooks engage receptacle slots in side walls
    | bottom tongue in groove at Z=130
    v
[Tub side walls + partial front wall: passive receptacles]

[Top panel: ~0.1 kg, retained by tongue-and-groove + 2 magnets]
    | tongue on tub rim engages groove in top panel
    | magnets in rim attract steel discs in panel
    v
[Tub upper rim: perimeter ledge with tongue + magnet pockets]

[Cartridge: ~0.82 kg, slides on floor rails]
    | floor rails guide in Y, side guides constrain in X
    v
[Tub floor rails + side guides: integral to lower tub half]
```

---

## Part Specification: Enclosure Tub

**Type:** 3D printed, two pieces permanently joined
**Material:** PETG, dark matte finish
**Quantity:** 1 (printed as 2 halves, glued into one piece)

### Exterior Dimensions

| Parameter | Value |
|-----------|-------|
| Exterior width (X) | 220mm |
| Exterior depth (Y) | 300mm |
| Exterior height (Z) | 400mm (full enclosure), but tub's own wall height: left/right/back walls run 0-396mm; front wall runs 0-130mm only |
| Wall thickness | 4mm solid, all walls, no ribs |
| Floor thickness | 4mm solid |
| Interior cavity | X: 4-216 (212mm), Y: 4-296 (292mm), Z: 4-396 (392mm) |
| Corner radii, vertical edges | 6mm exterior radius on all four vertical corners |
| Corner radii, horizontal edges | 4mm exterior radius at floor perimeter and at Z=396 rim perimeter |
| Mass (estimated) | ~1.8 kg total (both halves, PETG at 1.27 g/cm3) |

### Z=200 Horizontal Split

The tub prints as two halves divided at Z=200. This height was chosen because: (a) each half is under 200mm tall, fitting the 256mm print bed when printed on its back (largest flat face on bed), (b) the seam falls at bag-slab height, hidden by the cradle and bags on all viewing angles, and (c) it sits behind the front panel (which covers Z=130-400 on the front face).

#### Tongue-and-Groove Joint

The split perimeter runs along all four walls at Z=200. The joint uses a lap joint with tongue-and-groove:

| Parameter | Value |
|-----------|-------|
| Tongue (on upper half, Z=200 bottom edge) | 3mm wide (wall-thickness direction, centered in 4mm wall), 4mm tall (extending downward from Z=200 to Z=196), runs full perimeter of all four walls |
| Groove (in lower half, Z=200 top edge) | 3.2mm wide (0.1mm clearance per side for CA glue), 4.5mm deep (0.5mm deeper than tongue for glue reservoir at bottom), runs full perimeter |
| Overlap direction | Upper half tongue inserts downward into lower half groove. The outer wall face of the upper half overlaps the outer wall face of the lower half by 0mm -- faces are flush. The inner wall face of the upper half overlaps the inner wall face of the lower half by 0mm -- faces are flush. The tongue is centered in the wall thickness, creating a labyrinth path that prevents light leakage. |
| Interference fit | 0.1mm per side (tongue 3.0mm in 3.2mm groove) -- slight resistance during assembly, filled with CA glue |
| Glue reservoir | 0.5mm gap at groove bottom allows excess CA glue to pool without squeezing out at the exterior seam |

#### Alignment Pins

Four alignment pin pairs position the halves during glue-up:

| Pin pair | X | Y | Pin diameter | Hole diameter | Pin height | Location |
|----------|---|---|-------------|---------------|------------|----------|
| 1 | 30 | 150 | 4.0mm | 4.3mm (0.15mm radial clearance) | 8mm (4mm protrudes from each half) | Left wall, mid-depth |
| 2 | 190 | 150 | 4.0mm | 4.3mm | 8mm | Right wall, mid-depth |
| 3 | 110 | 290 | 4.0mm | 4.3mm | 8mm | Back wall, centered in X |
| 4 | 110 | 10 | 4.0mm | 4.3mm | 8mm | Front wall stub (Z=130 front wall), centered in X |

Pin design: Each pin is a 4.0mm-diameter cylindrical boss printed integral to the lower half, protruding 4mm above Z=200. Each hole is a 4.3mm-diameter x 4.5mm-deep blind hole in the upper half bottom face, positioned to mate with the corresponding pin. The 0.15mm radial clearance allows easy hand assembly while constraining lateral alignment to within 0.3mm. Pins are printed solid PETG, not metal dowels -- adequate for alignment during CA glue cure (no structural load after glue sets).

**DESIGN GAP DG-1:** Pin pair 4 is on the front wall stub at Y=10, which only exists up to Z=130. The upper half has no front wall above Z=130 (that area is covered by the removable front panel). The pin pair 4 hole must be in a short internal boss protruding from the upper half's interior at the corresponding position, bridging across the open front. Alternatively, pin pair 4 could be relocated to an interior feature (e.g., a floor-mounted internal rib at the cartridge-slot back wall zone). This needs resolution before CAD.

#### Glue Strategy

1. Dry-fit upper half onto lower half using alignment pins. Verify flush exterior walls.
2. Separate halves. Apply medium-viscosity CA glue to the groove floor and inner faces (not the exterior-facing groove walls, to prevent squeeze-out).
3. Press upper half onto lower half, pins into holes. Tongue seats into groove.
4. Clamp or weight for 60 seconds (CA cure time).
5. Sand exterior seam flush with 220-grit, then 400-grit. The seam becomes a hairline on dark matte PETG.

#### Post-Join Seam Appearance

| Face | Seam visibility |
|------|----------------|
| Front | Hidden behind front panel (panel covers Z=130-400) |
| Left | Hairline at Z=200, full depth Y=0-300 |
| Right | Hairline at Z=200, full depth Y=0-300 |
| Back | Hairline at Z=200, full width X=0-220 |

---

### Front Wall (Partial, Z=0 to Z=130)

The tub's front wall extends only from Z=0 to Z=130. Above Z=130, the front face is the removable front panel (separate part).

| Parameter | Value |
|-----------|-------|
| Extent | X: 0-220, Y: 0-4 (4mm thick), Z: 0-130 |
| Cartridge slot opening | 148mm wide x 84mm tall, centered in X (X=36 to X=184), Z=0 to Z=84 |
| Remaining wall around slot | 36mm on each side (X=0-36 and X=184-220), 46mm above slot (Z=84-130) |
| Material above slot | Solid 4mm PETG wall from Z=84 to Z=130, full 220mm width |

#### Chamfered Slot Entrance

The cartridge slot opening has a 5mm x 45-degree chamfer on all four interior edges, creating a funnel that narrows from 158mm x 94mm (exterior face) to 148mm x 84mm (interior face) over the 4mm wall thickness + 16mm additional depth:

| Parameter | Value |
|-----------|-------|
| Chamfer angle | 45 degrees |
| Chamfer depth | 5mm per edge (on interior face, angled inward) |
| Exterior opening (after chamfer) | 158W x 94H mm (5mm larger on each edge) |
| Interior opening (true slot) | 148W x 84H mm |
| Funnel depth | 20mm from exterior face (4mm wall + 16mm interior taper) |
| Acceptance misalignment | 10-15mm in any direction (user can be off-center and the funnel captures) |

The chamfer is on the interior face of the front wall, not the exterior. The exterior face of the front wall is flat around the slot at 148mm x 84mm. The chamfer creates a recessed funnel visible only when looking into the slot.

**DESIGN GAP DG-2:** The concept doc states a 5mm chamfer with a 20mm deep funnel. But the front wall is only 4mm thick. A 20mm funnel requires additional internal guide structure (chamfered guide blocks) extending 16mm behind the front wall. These guide blocks must be integral to the tub's lower half interior at X=31-36 and X=184-189 (sides) and Z=84-94 (top), protruding inward from the front wall. The floor chamfer is the tub floor itself (Z=0-4, chamfer from Z=0 at exterior to Z=4 at interior, then continuing as the ramp on the floor surface). This internal guide structure needs full specification.

#### Front Wall Top Edge (Z=130) -- Front Panel Interface

The top edge of the partial front wall at Z=130 carries a groove for the front panel's bottom tongue:

| Parameter | Value |
|-----------|-------|
| Groove width | 2.2mm (accepts 2mm front panel tongue, 0.1mm clearance per side) |
| Groove depth | 3mm (into the top face of the front wall) |
| Groove length | Full 220mm width |
| Groove position | Centered in the 4mm wall thickness (1mm wall material on each side of groove) |

**DESIGN GAP DG-3:** A 2.2mm groove centered in a 4mm wall leaves only 0.9mm of wall material on each side. This is fragile for PETG. Options: (a) thicken the front wall to 6mm at Z=120-130 to provide 1.9mm on each side, (b) offset the groove toward the interior face, leaving 1.5mm exterior / 0.3mm interior, (c) use a rabbet joint instead of a groove (tongue rests on a step rather than inserting into a slot). The rabbet approach would provide a 2mm step on the interior face at Z=128-130, with the front panel resting on the step and held in place by the snaps. This eliminates the thin-wall concern entirely but provides less lateral constraint at the bottom edge.

---

### Side Walls (Left and Right)

| Parameter | Value |
|-----------|-------|
| Left wall | X: 0-4, Y: 0-300, Z: 0-396 |
| Right wall | X: 216-220, Y: 0-300, Z: 0-396 |
| Thickness | 4mm solid |
| Vertical edge radii | 6mm exterior radius on all four vertical corners (front-left, front-right, back-left, back-right) |
| Height | Full 396mm (interior top = Z=396, exterior top = Z=400 with top panel) |

#### Snap-Fit Receptacle Slots (4 total, 2 per side wall)

The front panel attaches to the tub via four cantilever snap hooks (on the front panel) engaging four receptacle slots (in the tub side walls). Two receptacles per side wall:

| Receptacle | Wall | X position | Y position | Z position |
|------------|------|-----------|-----------|-----------|
| 1 (left lower) | Left (X=4 interior face) | 0-4 (in wall) | 10-22mm from front face (Y=10-22) | Z=200 (centered) |
| 2 (left upper) | Left (X=4 interior face) | 0-4 (in wall) | 10-22mm from front face (Y=10-22) | Z=340 (centered) |
| 3 (right lower) | Right (X=216 interior face) | 216-220 (in wall) | 10-22mm from front face (Y=10-22) | Z=200 (centered) |
| 4 (right upper) | Right (X=216 interior face) | 216-220 (in wall) | 10-22mm from front face (Y=10-22) | Z=340 (centered) |

Each receptacle slot geometry:

| Parameter | Value |
|-----------|-------|
| Slot width (along Y) | 12mm |
| Slot depth (into wall, along X) | 3mm (from interior wall face into wall body) |
| Slot height (along Z) | 8mm |
| Entry chamfer | 1mm x 45-degree chamfer on the upper edge of the slot opening, to guide the front panel hook tip during top-down installation |
| Wall remaining behind slot | 1mm (4mm wall - 3mm slot depth) |

**DESIGN GAP DG-4:** A 3mm-deep slot in a 4mm wall leaves only 1mm of exterior wall. This is structurally marginal for a snap receptacle that must resist ~5N of pull-out force per hook. Options: (a) locally thicken the side wall to 6mm at the receptacle zones (adding a 2mm interior boss around each slot), (b) reduce slot depth to 2mm and redesign the front panel hooks for shallower engagement, (c) add a reinforcing rib behind each receptacle on the interior face. Option (a) is preferred -- a local 12mm x 10mm x 2mm boss on the interior wall face around each receptacle provides 3mm of material behind the 3mm slot.

#### Bag Cradle Bracket Slots (6 total, 3 per side wall)

The bag cradle mounts to the tub via tabs that insert into slots in the side walls:

| Slot pair | Z position | Y position | Slot width (Y) | Slot height (Z) | Slot depth (X, into wall) |
|-----------|-----------|-----------|----------------|-----------------|---------------------------|
| Lower (cap end) | Z=130 | Y=29 | 20mm | 4mm | 3mm |
| Middle | Z=260 | Y=160 | 20mm | 4mm | 3mm |
| Upper (sealed end) | Z=385 | Y=285 | 20mm | 4mm | 3mm |

Slots are cut into the interior face of each side wall. The cradle tabs (20mm x 4mm x 5mm, with 3mm insertion depth and 2mm lip) slide into these slots from the interior during manufacturing assembly. Once the bags are installed and the front panel attached, the cradle tabs cannot slide out.

#### Magnet Pockets (2 total, 1 per side wall, in upper rim)

For top panel magnetic retention:

| Pocket | Wall | Position | Magnet size | Pocket dimensions |
|--------|------|----------|-------------|-------------------|
| Left | Left wall rim (X=4 interior) | Y=150, Z=393-396 | 6mm dia x 3mm tall disc | 6.2mm dia x 3.2mm deep blind hole in rim top face (0.1mm clearance, press-fit with CA glue) |
| Right | Right wall rim (X=216 interior) | Y=150, Z=393-396 | 6mm dia x 3mm tall disc | 6.2mm dia x 3.2mm deep blind hole in rim top face |

**Note:** These are steel discs, not magnets. The neodymium magnets are in the top panel. Steel discs in the tub rim are cheaper, cannot demagnetize, and have no polarity concern during assembly. Material: mild steel, 6mm dia x 3mm.

#### Display Reel Pockets (2 total, in side walls)

The two retractable cat6 reels mount inside the tub, behind the front panel zone. Each reel is ~55mm diameter x ~22mm deep. They require cylindrical pockets in the interior:

| Pocket | Position (center) | Dimensions | Notes |
|--------|-------------------|-----------|-------|
| Left reel (RP2040 display) | X=4, Y=15, Z=275 | 57mm dia x 24mm deep pocket in left wall interior face | 1mm clearance around 55mm reel, 2mm clearance behind 22mm depth |
| Right reel (S3 display) | X=216, Y=15, Z=275 | 57mm dia x 24mm deep pocket in right wall interior face | Symmetric with left |

**DESIGN GAP DG-5:** A 24mm-deep pocket in a 4mm-thick wall is impossible without thickening. The reels must be mounted differently. Options: (a) the reels mount to the back face of the front panel (the front panel is a separate part, and the reels are associated with its display dock recesses -- this is the most logical approach since the cable exits through the front panel), (b) the reels mount on brackets that screw to the tub side walls or to the tub interior. Given that the front panel carries the display dock recesses and cable exit holes, option (a) is correct -- the reel pockets belong to the front panel, not the tub. The tub needs only a clear volume behind the front panel at these positions (which already exists -- interior cavity from Y=4 to Y=26 at Z=248-303 is open). Removing reel pockets from the tub spec.

---

### Back Wall

| Parameter | Value |
|-----------|-------|
| Extent | X: 0-220, Y: 296-300 (4mm thick), Z: 0-396 |
| Thickness | 4mm solid |
| Corner radii | 6mm exterior radius at back-left and back-right vertical edges |

#### Bulkhead Fitting Holes (3 total)

Three 1/4" John Guest bulkhead fittings pass through the back wall for water lines:

| Fitting | Function | Center X | Center Z | Hole diameter | Notes |
|---------|----------|----------|----------|---------------|-------|
| 1 | Tap water inlet | 170 | 40 | 15.9mm (JG PP1208W bulkhead spec) | Lower-right zone (from rear) |
| 2 | Soda water in | 110 | 40 | 15.9mm | Lower-center |
| 3 | Soda water out | 70 | 40 | 15.9mm | Lower-center-left |

Each hole is at Y=296-300 (through the back wall). The JG bulkhead fitting has a 15.10mm OD body that passes through a 15.9mm hole (0.4mm radial clearance). A bulkhead nut on the interior face clamps the fitting to the wall. The 4mm wall thickness is adequate for bulkhead clamping (JG bulkhead spec allows 1-10mm panel thickness).

#### Cable Gland Holes (2 total)

Two PG7 cable glands for flavor line silicone tube pass-throughs:

| Gland | Function | Center X | Center Z | Hole diameter | Notes |
|-------|----------|----------|----------|---------------|-------|
| 1 | Flavor line 1 exit | 180 | 160 | 12.5mm (PG7 mounting hole spec) | Mid-height, right from rear |
| 2 | Flavor line 2 exit | 40 | 160 | 12.5mm | Mid-height, left from rear |

#### IEC C14 Power Inlet Cutout

| Parameter | Value |
|-----------|-------|
| Center X | 55 |
| Center Z | 360 |
| Cutout dimensions | 27.5mm wide x 20mm tall (standard IEC C14 panel-mount with fuse drawer) |
| Cutout type | Rectangular through-hole with 1mm corner radius |
| Mounting holes | 2x M3 clearance holes (3.2mm dia), 40mm center-to-center horizontally, centered on the cutout |

#### Electronics Shelf Bracket Ledges (2 total)

Two L-shaped ledges protruding from the interior face of the back wall:

| Parameter | Value |
|-----------|-------|
| Ledge width (along X) | 70mm each (left ledge: X=4-74, right ledge: X=146-216) |
| Ledge depth (protrusion from wall, along -Y) | 10mm (from Y=292 interior face to Y=282) |
| Ledge thickness (Z) | 4mm |
| Ledge Z position | Z=336-340 (top face at Z=340) |
| Load capacity | Each ledge supports ~0.25 kg (half the electronics shelf weight) |

The electronics shelf (separate part, ~190W x 92D x 4H mm) rests on these two ledges with its rear edge against the back wall interior face. The shelf spans the 142mm gap between the two ledges. Two M3 screw bosses on the ledge top faces (one per ledge, at the midpoint of each ledge) accept screws through the shelf to prevent sliding.

| Screw boss | X | Y | Z | Dimensions |
|-----------|---|---|---|------------|
| Left shelf boss | 40 | 286 | 340 | 8mm OD, 4.2mm pilot hole (heat-set M3), 8mm tall (Z=340-348) |
| Right shelf boss | 180 | 286 | 340 | 8mm OD, 4.2mm pilot hole (heat-set M3), 8mm tall (Z=340-348) |

#### Back-Wall Bag Pin Mount (1 total)

A mounting boss for the bag pin/clamp that holds the sealed ends of both bags against the back wall:

| Parameter | Value |
|-----------|-------|
| Position | X=110 (centered), Y=292 (interior face), Z=388 |
| Boss dimensions | 20mm wide (X) x 8mm protrusion (Y) x 10mm tall (Z=383-393) |
| Screw holes | 2x M3 clearance (3.2mm dia), 10mm apart horizontally, for mounting the bag pin/clamp assembly |

---

### Floor

| Parameter | Value |
|-----------|-------|
| Extent | X: 0-220, Y: 0-300, Z: 0-4 (4mm thick) |
| Interior surface | Z=4 |
| Exterior surface | Z=0 |

#### Cartridge Dock Floor Rails (2 total)

Two parallel raised rails on the interior floor surface guide the cartridge during insertion:

| Rail | X position (inner edge) | X position (outer edge) | Y extent | Height above floor | Width |
|------|------------------------|------------------------|----------|-------------------|-------|
| Left | X=39 | X=42 | Y=4 to Y=134 (130mm, full dock depth) | 2mm (Z=4 to Z=6) | 3mm |
| Right | X=178 | X=181 | Y=4 to Y=134 | 2mm (Z=4 to Z=6) | 3mm |

Rail inner-edge spacing: 178 - 42 = 136mm (cartridge base width ~140mm with grooves at the rail positions). The cartridge base grooves (3mm wide x 2.5mm deep) ride on these rails with 0.3-0.5mm clearance per side.

Each rail has a 2mm x 30-degree entry ramp at the front end (Y=4-6) to ease cartridge loading.

#### Cartridge Dock Side Guides (2 total)

Two raised rails on the interior side walls within the dock zone:

| Guide | X position | Y extent | Z extent | Width | Clearance to cartridge |
|-------|-----------|----------|----------|-------|----------------------|
| Left | X=4 to X=5.5 (1.5mm protrusion from left wall interior face) | Y=4 to Y=134 | Z=4 to Z=84 | 1.5mm | 0.3-0.5mm to cartridge side |
| Right | X=214.5 to X=216 (1.5mm protrusion from right wall interior face) | Y=4 to Y=134 | Z=4 to Z=84 | 1.5mm | 0.3-0.5mm to cartridge side |

Side guide inner face spacing: 214.5 - 5.5 = 209mm. Cartridge width: 148mm. Side guide to cartridge clearance: (209 - 148) / 2 = 30.5mm per side. This is not a tight guide -- the side guides only prevent gross lateral misalignment. Fine lateral alignment is provided by the dock back wall's tapered alignment pins at the mating face.

**DESIGN GAP DG-6:** The side guides are 30.5mm from the cartridge sides -- too far for effective lateral guidance. The dock-back-wall parts.md specifies side guides at X=36 and X=184 (matching the cartridge slot edges), which would be 1.5mm protrusions from dedicated guide walls, not from the enclosure side walls. The tub should provide either: (a) dedicated guide walls integral to the floor/lower-half at X=36 and X=184 running Y=4-134 at Z=4-84, or (b) the dock-back-wall part should include integral side guides. The spatial layout shows "Dock side guides (2x)" at X=36/183.5 to X=37.5/184.5, which confirms option (a). The tub's lower half needs two interior guide walls:

| Guide wall | X extent | Y extent | Z extent | Thickness |
|-----------|----------|----------|----------|-----------|
| Left dock guide | X=36 to X=37.5 | Y=4 to Y=134 | Z=4 to Z=84 | 1.5mm |
| Right dock guide | X=183 to X=184.5 | Y=4 to Y=134 | Z=4 to Z=84 | 1.5mm |

These are thin walls integral to the tub's lower half, running the full dock depth and height.

#### Valve Rack Floor Bosses (4 total)

| Boss | X | Y | Z extent | Diameter | Pilot hole |
|------|---|---|----------|----------|-----------|
| 1 | 30 | 179 | Z=4 to Z=16 (12mm tall) | 8mm OD | 4.2mm (heat-set M3 insert) |
| 2 | 30 | 214 | Z=4 to Z=16 | 8mm OD | 4.2mm |
| 3 | 190 | 179 | Z=4 to Z=16 | 8mm OD | 4.2mm |
| 4 | 190 | 214 | Z=4 to Z=16 | 8mm OD | 4.2mm |

These bosses accept M3 x 8mm screws through the valve rack frame's mounting flanges.

#### Dock Back Wall Floor Bosses (2 total)

| Boss | X | Y | Z extent | Diameter | Pilot hole |
|------|---|---|----------|----------|-----------|
| 1 | 60 | 137 | Z=4 to Z=12 (8mm tall) | 8mm OD | 4.2mm (heat-set M3 insert) |
| 2 | 160 | 137 | Z=4 to Z=12 | 8mm OD | 4.2mm |

#### Rubber Foot Pockets (4 total)

| Pocket | X | Y | Diameter | Depth (into floor exterior face) | Notes |
|--------|---|---|----------|----------------------------------|-------|
| 1 | 20 | 20 | 12mm | 2mm | Front-left, accepts 12mm adhesive rubber bumper |
| 2 | 200 | 20 | 12mm | 2mm | Front-right |
| 3 | 20 | 280 | 12mm | 2mm | Back-left |
| 4 | 200 | 280 | 12mm | 2mm | Back-right |

Each pocket is a 12mm-diameter x 2mm-deep circular recess in the exterior floor face (Z=0 surface). Standard 12mm adhesive-backed rubber bumper feet sit in these pockets, with the adhesive backed against the pocket floor and the rubber dome protruding ~3mm below the exterior surface. The pocket prevents the feet from sliding on the cabinet shelf.

#### Dock Back Wall Side Bosses (2 total)

The dock back wall also screws to the tub side walls within the dock zone:

| Boss | Wall | X | Y | Z | Dimensions |
|------|------|---|---|---|------------|
| 1 | Left wall interior | 4 | 137 | 42 | 8mm OD, 4.2mm pilot hole, 8mm protrusion from wall face |
| 2 | Right wall interior | 216 | 137 | 42 | 8mm OD, 4.2mm pilot hole, 8mm protrusion from wall face |

---

### Upper Rim (Z=393-396)

The top 3mm of the side walls and back wall form the seating surface for the top panel:

| Parameter | Value |
|-----------|-------|
| Rim height | 3mm (Z=393-396, the last 3mm of the 4mm wall at Z=392-396) |
| Rim width | 4mm (full wall thickness) |
| Tongue on rim | 3mm wide x 2mm tall, centered on the interior edge of the rim top face, running along left wall (X=4), back wall (Y=296), and right wall (X=216). NOT on the front edge (where the front panel meets the top panel). |
| Tongue dimensions | 3.0mm wide (along the wall-to-interior direction), 2.0mm tall (above Z=394 to Z=396), centered 0.5mm from interior wall face |
| Magnet pocket positions | See Side Walls section -- steel disc pockets at Y=150 in each side wall rim |
| Front edge treatment | No tongue on front rim. The top panel's front edge butts against the top edge of the front panel. The front panel's top edge is the reference surface. |

---

### Print Orientation and FDM Considerations

#### Lower Half (Z=0 to Z=200)

| Parameter | Value |
|-----------|-------|
| Print orientation | On its back -- exterior back wall face (Y=300 surface) on the build plate |
| Build plate footprint | 220mm (X) x 200mm (Z, now the print height becomes the depth on the bed) -- fits 256mm bed |
| Print height (off bed) | 300mm (Y dimension) -- this is the depth of the tub. **Exceeds 256mm bed height.** |

**DESIGN GAP DG-7:** The lower half printed on its back has a 300mm print height (the Y/depth dimension), which exceeds the 256mm build volume. The concept doc states each half prints "on their backs (largest flat face down)" and "220mm width fits within 256mm." But the depth (300mm) exceeds the bed in the vertical direction. Options: (a) print on the side wall instead (left or right wall on bed) -- footprint would be 300mm (Y) x 200mm (Z) = 300mm exceeds bed, (b) print upright with the floor on the bed -- footprint 220 x 300mm, both exceed 256mm, (c) print at an angle, (d) use a larger-format printer (e.g., Bambu X1E at 256x256x256 won't work either; Creality K1 Max at 300x300x300 would work). This is a fundamental constraint that needs resolution. A 300x300x300mm build volume printer would allow back-on-bed orientation. Alternatively, the tub could be split into more than 2 pieces.

#### Upper Half (Z=200 to Z=396)

| Parameter | Value |
|-----------|-------|
| Height range | Z=200 to Z=396 (196mm tall) |
| Note | Same print orientation challenges as lower half -- 300mm depth exceeds 256mm bed |

**Assuming a 300x300x300mm build volume printer (e.g., Creality K1 Max):**

| Half | Orientation | Footprint on bed | Print height |
|------|------------|-----------------|-------------|
| Lower (Z=0-200) | Back wall on bed (Y=300 face down) | 220 x 200mm | 300mm (tight fit on 300mm bed) |
| Upper (Z=200-396) | Back wall on bed | 220 x 196mm | 300mm |

Both halves have the exterior back wall as the smooth build-plate surface. The exterior side walls print vertically (good surface quality from FDM layer lines parallel to the surface). The interior features (bosses, rails, guide walls) print as they protrude from the walls -- supported by the wall surfaces.

**Layer orientation for the Z=200 split joint:** When printed on the back, the Z=200 split face becomes the "top" of the print (furthest from the bed). The tongue-and-groove features at this edge print last, with good dimensional accuracy. The alignment pin bosses (on the lower half) print as vertical cylinders extending from the top face -- clean geometry for FDM.

---

## Direction Consistency Check

| Claim | Direction | Axis | Verified? | Notes |
|-------|-----------|------|-----------|-------|
| Upper half tongue inserts downward into lower half groove | -Z during assembly | Z | Yes | Upper half placed on top of lower half, tongue enters groove vertically |
| Front panel tongue seats in groove at Z=130 top face | -Z during panel installation | Z | Yes | Front panel slides down, tongue enters groove from above |
| Top panel tongue engages rim tongue from above | -Z during lid placement | Z | Yes | Top panel drops onto rim, groove captures tongue |
| Cartridge slides in along floor rails toward rear | +Y direction | Y | Yes | User pushes cartridge from front to back |
| Snap hooks engage receptacle slots by pressing inward | Hooks press in +X (left wall) or -X (right wall) | X | Yes | Hooks on front panel edges deflect inward toward tub interior during installation, then spring outward into slots |
| Electronics shelf rests on bracket ledges | -Z (gravity) | Z | Yes | Shelf sits on horizontal ledge faces |
| Bag weight transfers through cradle to side walls | -Z (gravity) through angled cradle to X-direction reaction at side walls | Z and X | Yes | Diagonal load resolved into vertical (floor) and lateral (side wall) components |
| CA glue applied to groove, upper half pressed down | -Z during assembly | Z | Yes | |

---

## Interface Dimensional Consistency

| Interface | Part A dimension | Part B dimension | Clearance | Source |
|-----------|-----------------|-----------------|-----------|--------|
| Tongue-and-groove (Z=200 split) | Tongue: 3.0mm wide x 4.0mm tall | Groove: 3.2mm wide x 4.5mm deep | 0.1mm/side (width), 0.5mm (depth, glue reservoir) | Derived from FDM tolerance (0.1-0.2mm) |
| Alignment pins to holes | Pin: 4.0mm dia x 4mm protrusion | Hole: 4.3mm dia x 4.5mm deep | 0.15mm radial, 0.5mm depth | Derived from FDM tolerance |
| Front panel tongue in groove (Z=130) | Tongue: 2.0mm wide (front panel) | Groove: 2.2mm wide x 3.0mm deep (tub) | 0.1mm/side | Derived from FDM tolerance |
| Snap hook in receptacle slot | Hook: 10mm wide x 2.5mm deep (front panel) | Slot: 12mm wide x 3mm deep x 8mm tall (tub) | 1mm/side width, 0.5mm depth | Derived; generous for FDM |
| Magnet/steel disc in rim pocket | Steel disc: 6.0mm dia x 3.0mm tall | Pocket: 6.2mm dia x 3.2mm deep | 0.1mm radial, 0.2mm depth (for CA glue) | Assumed disc dimensions |
| Dock floor rail to cartridge groove | Rail: 3mm wide x 2mm tall | Groove: 3mm wide x 2.5mm deep (cartridge) | 0-0.5mm width (press/slide fit), 0.5mm depth | From dock-back-wall parts.md |
| JG bulkhead hole in back wall | Fitting body: 15.10mm OD | Hole: 15.9mm dia | 0.4mm radial | JG PP1208W spec |
| PG7 cable gland in back wall | Gland thread: 12.0mm OD | Hole: 12.5mm dia | 0.25mm radial | PG7 spec |
| M3 heat-set insert in boss | Insert: 4.0mm OD (knurl) | Pilot hole: 4.2mm dia | 0.1mm radial (insert expands on heating) | Standard M3 heat-set practice |
| IEC C14 inlet in back wall | Inlet body: 27.0mm x 19.5mm | Cutout: 27.5mm x 20mm | 0.25mm/side | Standard IEC C14 panel mount |
| Upper rim tongue to top panel groove | Tongue: 3.0mm wide x 2.0mm tall | Groove: 3.2mm wide x 2.2mm deep (top panel) | 0.1mm/side width, 0.2mm depth | Derived from FDM tolerance |
| Dock guide walls to cartridge | Guide inner face spacing: 148mm (184.5 - 36 = 148.5mm, minus 0.5mm) | Cartridge width: 148mm | 0.25mm per side | From spatial layout |

**DESIGN GAP DG-8:** The dock guide wall spacing (X=36 to X=184.5, inner faces at X=37.5 and X=183, gap = 145.5mm) does not match the cartridge width (148mm). The cartridge is wider than the guide gap. The guide walls should be at X=34.5 and X=185.5 (inner faces) to provide 148mm + 1mm clearance = 149mm gap, or the cartridge width needs verification. Using the spatial layout values: slot opening is X=36-184 (148mm), dock side guides inner edges at X=37.5 and X=183. Inner gap = 183 - 37.5 = 145.5mm, which is 2.5mm narrower than the 148mm cartridge. This is a dimensional conflict. Resolution: the guides should have inner faces at X=37 and X=183, but the cartridge fits in the 148mm slot opening, not between the 1.5mm-thick guides. The guides protrude into the slot zone. The cartridge must have matching grooves or the guide positions must be outside the cartridge envelope. Per the spatial layout, guides are at X=36/183 to X=37.5/184.5 -- the inner edges at 37.5 and 183 define a 145.5mm channel. The cartridge outer width must be less than 145.5mm at the guide contact faces, with the 148mm dimension being the overall width including features that clear above or below the guides. This needs resolution against the cartridge shell parts.md.

---

## Assembly Feasibility Check

### Tub Half Joining (one-time, permanent)

1. **Print lower half and upper half separately.** Each half is a five-sided partial box (open on one side at the Z=200 split plane and open on top/bottom respectively).
2. **Install heat-set M3 inserts** into all floor bosses and wall bosses while each half is accessible as a separate piece. This is easier before joining.
3. **Press steel discs** into rim magnet pockets on the upper half with CA glue.
4. **Dry-fit** upper half onto lower half. Four alignment pins guide the halves together. Verify exterior wall faces are flush. Verify tongue seats into groove with slight resistance.
5. **Separate.** Apply medium-viscosity CA glue to groove inner faces and floor. Avoid exterior-facing surfaces.
6. **Join permanently.** Press upper half onto lower half. Clamp or weight for 60 seconds.
7. **Sand exterior seam** at Z=200 with 220-grit then 400-grit until hairline.

**Feasibility:** All steps are straightforward. The halves are large but manageable (each ~0.9 kg). The alignment pins ensure repeatable positioning. CA glue sets in 60 seconds. Sanding a horizontal seam on flat walls is simple.

### Component Installation Into Joined Tub

After tub halves are joined, components install in this order:

1. **Dock floor rails and side guide walls** -- integral to the tub (printed as part of the lower half). No installation needed.
2. **Dock back wall** -- separate part, screws into floor bosses (2x M3) and side wall bosses (2x M3). Access: from above (open top) or from front (open front above Z=130). Four M3 screws, all accessible with a standard driver.
3. **Pogo pin mount** -- attaches to dock back wall ceiling face. Access: from front through cartridge slot opening.
4. **Valve rack** -- slides in from above (open top) or from front. Screws into 4x floor bosses. Access: from above.
5. **All internal tubing** -- routed through open top and open front.
6. **Bag cradle** -- tabs slide into side wall bracket slots. Access: from front (open front above Z=130) and from above.
7. **Bags** -- placed into cradle, sealed ends pinned to back wall. Access: from above and front.
8. **Electronics shelf** -- rests on bracket ledges at Z=340, screws into 2x ledge bosses. Access: from above.
9. **All electronics wiring** -- routed from shelf to valve rack, pogo pins, back wall. Access: from above and front.
10. **Back wall fittings and cable glands** -- installed from the exterior rear. Thread through holes, tighten nuts from interior (access from above).
11. **Top panel** -- placed on rim. Tongue-and-groove + magnets. Access: from above.
12. **Front panel** -- installed last. Bottom tongue into groove at Z=130, then press snap hooks into receptacle slots. Access: from front.

**Feasibility:** All components can be installed through the open top (after step 11) or open front (before step 12). No component becomes trapped or inaccessible. The installation order is sequenced so that each component is accessible when it needs to be installed. Disassembly reverses the order: front panel off (release snaps), top panel off (lift), then all components accessible from above and front.

---

## Part Count Minimization

| Part pair | Permanently joined? | Move relative? | Same material? | Verdict |
|-----------|-------------------|----------------|----------------|---------|
| Lower tub half + Upper tub half | Yes (CA glue) | No | Yes (PETG) | Correct to combine as one part (printed as 2 pieces due to bed size, permanently joined) |
| Tub + Dock floor rails | N/A (integral) | No | Yes | Already integral -- correct |
| Tub + Dock side guide walls | N/A (integral) | No | Yes | Already integral -- correct |
| Tub + Floor bosses | N/A (integral) | No | Yes | Already integral -- correct |
| Tub + Wall bosses | N/A (integral) | No | Yes | Already integral -- correct |
| Tub + Bracket ledges | N/A (integral) | No | Yes | Already integral -- correct |
| Tub + Rim tongue | N/A (integral) | No | Yes | Already integral -- correct |
| Tub + Dock back wall | No (screwed) | No | Yes | Could combine, but the dock back wall carries JG tube stubs and pogo pin mount -- it has complex features on both faces that require independent print orientation. Separate part justified. |
| Tub + Bag cradle | No (tabbed into slots) | No after installation | Yes | Could combine, but cradle is 350mm along the diagonal (~420mm diag length), which exceeds any print bed. Must be separate. Justified. |
| Tub + Electronics shelf | No (screwed onto ledges) | No | Yes | Could combine, but shelf needs to be installed after internal wiring is routed. Separate for assembly sequence. Justified. |
| Tub + Front panel | No (snap-fit, removable) | Yes (removable for service) | Yes | Must be separate -- removable by design. Correct. |
| Tub + Top panel | No (magnetic, removable) | Yes (removable for hopper access) | Yes | Must be separate -- removable by design. Correct. |

All part separations are justified. No unnecessary part splits.

---

## Design Gap Summary

| ID | Description | Severity | Suggested resolution |
|----|-------------|----------|---------------------|
| DG-1 | Alignment pin pair 4 at Y=10 has no upper-half wall above Z=130 to receive a hole. Need internal boss or relocated pin. | Medium | Relocate pin 4 to an internal feature, e.g., a boss on the interior of the upper half at X=110, Y=10 projecting downward from an internal bridge. Or relocate to X=110, Y=100 (still within the front wall zone but deeper, where the upper half has interior wall returns). |
| DG-2 | 20mm chamfer funnel exceeds 4mm front wall thickness. Internal guide blocks needed. | Medium | Add chamfered guide blocks integral to lower tub half at the slot perimeter, extending 16mm rearward from the front wall interior face. 5mm-wide blocks on all four sides of the 148x84mm slot opening. |
| DG-3 | 2.2mm groove in 4mm wall at Z=130 leaves 0.9mm on each side -- too fragile. | High | Switch to rabbet joint: 2mm step on interior face at Z=128-130, front panel rests on step. Eliminates thin-wall concern. Or thicken front wall to 6mm at Z=120-130. |
| DG-4 | 3mm-deep snap receptacle slot in 4mm wall leaves 1mm exterior material. | High | Add 2mm-deep local boss (12mm W x 10mm H) on interior wall face around each receptacle, providing 3mm behind the slot. |
| DG-5 | Display reel pockets were incorrectly assigned to tub walls. | Low | Resolved: reels mount to front panel back face, not tub walls. Tub needs only clear interior volume at those positions (already exists). |
| DG-6 | Side guides at enclosure wall (30.5mm from cartridge) are too far for guidance. Dedicated guide walls needed at X=36/184. | Medium | Resolved in spec: added dedicated dock guide walls integral to lower tub half at X=36-37.5 and X=183-184.5. |
| DG-7 | Both tub halves exceed 256mm build volume in one dimension (300mm depth) when printed on their backs. | Critical | Requires 300x300x300mm printer (Creality K1 Max, Bambu A1, etc.), or re-split the tub into more pieces (e.g., 4 quadrants), or redesign the enclosure depth. |
| DG-8 | Dock guide wall inner spacing (145.5mm) is narrower than cartridge width (148mm). Dimensional conflict. | High | Guide positions need verification against cartridge shell. Either guides must be repositioned outside cartridge envelope, or cartridge has relieved edges at guide heights. Requires cross-part coordination. |

---

## Related Documents

- **Enclosure concept:** `enclosure-concept.md`
- **Spatial layout:** `../../../planning/spatial-layout.md`
- **System architecture:** `../../../planning/architecture.md`
- **Cartridge architecture:** `../../../planning/cartridge-architecture.md`
- **Dock back wall:** `../../dock-back-wall/planning/parts.md`
- **Valve rack:** `../../valve-rack/planning/parts.md`
- **Electronics shelf:** `../../electronics-shelf/planning/parts.md`
- **Bag cradle:** `../../bag-cradle/planning/parts.md`
- **Front panel:** `../../front-panel/planning/parts.md`
- **Back panel:** `../../back-panel/planning/parts.md`
- **Cartridge shell:** `../../cartridge-shell/planning/parts.md`
- **Cartridge twist-release:** `../../cartridge-twist-release/planning/parts.md`
