# Foam-bag shell (plan A — round vertical vessel)

The foam-bag shell is the printed PETG enclosure that wraps the carbonator
pressure vessel, holds the two flavor bladders in dry pockets against the
vessel's sides, accommodates the copper evaporator coil and its bonding gap,
and contains two pour-in-place polyurethane foam regions that thermally
insulate everything. It is the "cold core" of the appliance — the back-of-
enclosure subsystem that everything else connects to.

This folder is for plan A: 5" OD round vertical pressure vessel, four ports
(two top plate, two bottom plate), bags arranged on opposite Y faces of the
vessel. The plan-B racetrack version, retained as fallback, lives in
[`../plan-b/foam-bag-shell-racetrack/`](../plan-b/foam-bag-shell-racetrack/).

## Inputs from other subsystems

- **Pressure vessel** — 5.000" OD × 0.065" wall × 6.000" cut length 316 SS
  welded tube (OnlineMetals #12498). Two 1/4"-thick 316 SS endcap plates
  laser-welded internally, recessed flush with the tube ends (plate OD = tube
  ID). Hand-tapped 1/4" NPT, four ports total — two on the top plate (water
  inlet, PRV), two on the bottom plate (CO2 inlet, water outlet). Vessel
  assembled outer height = tube length = **152.4 mm**.
- **Bag** — Platypus-style soft-walled bladder, 1 L max capacity but used at
  ≤ 750 mL, single port at the cap end with a 90° tube turn. Total envelope
  when filled and posed cap-down (cap and 90° turn included): **125 mm wide
  × 35 mm thick × 225 mm tall**. Two bags per cold core.
- **Evaporator coil** — 1/4" OD × 0.187" ID × 0.031" wall ACR copper, hand-
  wound helically around the vessel exterior, bonded with 3M 425 aluminum
  foil tape. ~6.35 mm radial occupancy.
- **Tank-port fittings** — 1/4" NPT 90° elbows on every port turn the line
  laterally, exiting the cold core through the **X-face** outer shell.
  Specific fittings TBD; budget ~25–30 mm vertical envelope per elbow body.
- **PRV** — Control Devices SV-100 (B0D361X97X). Body sits horizontally in
  the top foam band. Vents to atmosphere through a dedicated printed PETG
  conduit through the outer shell. Path must be unobstructed.
- **Level sensors** — 2 × Gebildet reed switches (B0CW9418F6) bonded to the
  outside of the vessel tube wall (austenitic 316 = non-magnetic). Low- and
  high-threshold positions. Signal wires routed out through the outer shell.
- **Temperature sensors** — 2 × DS18B20 waterproof probes on a shared 1-wire
  bus. One clamped to the vessel wall, one bonded to the evaporator suction
  line. Signal wires routed similarly.

## Cold-core envelope (locked)

Outer dimensions of the printed cold core, treated as a brick:

| Axis | Dimension | Driver |
|---|---|---|
| X (perpendicular to bag axis) | **166.2 mm** | Tank ⌀127 + 2 × (7 + 5 + 0.8 + 6 + 0.8) |
| Y (bag axis) | **237.8 mm** | Same + 2 × 35 mm bag |
| Z (vertical) | **~226 mm** | Bag height 225 + skin clearances |

Cross-section is a **flatted stadium** — round on X faces (tight to the
tank), flat on Y faces (tangent to the bag's flat backs).

## Radial budget

From the tank centerline outward, on the **Y axis** (through bag centerline):

| Layer | Thickness | Material | Notes |
|---|---|---|---|
| Tank wall (radius) | 0–63.5 mm | 316 SS | 5" OD vessel |
| Coil zone | 7 mm | Cu coil + foil tape + foam | Helix + tolerance |
| Inner foam | 5 mm | Pour PU | Bag-freeze prevention; thermal break |
| Inner shell wall | 0.8 mm | PETG | Flat at y = ±76.3 over the bag width |
| Bag | 35 mm | bag + air | Dry cavity, never foam-contacted |
| Pocket outboard wall | 0.8 mm | PETG | Encloses bag from outer foam |
| Outer foam | 6 mm | Pour PU | Bag temp control + outer-shell condensation |
| Outer shell wall | 0.8 mm | PETG | Sealed perimeter |

On the **X axis** (perpendicular to bag axis, no bag in this radial line):

| Layer | Thickness | Material | Notes |
|---|---|---|---|
| Tank wall (radius) | 0–63.5 mm | 316 SS | |
| Coil zone | 7 mm | Cu coil + tape + foam | |
| Inner foam | 5 mm | Pour PU | |
| Inner shell wall | 0.8 mm | PETG | Round arc, radius 76.3 mm from tank centerline |
| Outer foam | 6 mm | Pour PU | |
| Outer shell wall | 0.8 mm | PETG | |

## Inner shell cross-section (flatted stadium)

The inner shell is a closed PETG cylinder with a flatted-stadium cross-section:

- **Round arcs** of radius 76.3 mm centered at the tank centerline, covering
  the X faces (`|x| > 62.5 mm`).
- **Flat sides** at y = ±76.3 mm, covering the bag-tangent region
  (`-62.5 ≤ x ≤ +62.5`), each flat 125 mm long matching the bag width.
- **Vertical jump segments** at x = ±62.5 mm connecting the flats (at
  y = ±76.3) to the round arcs (at y = ±43.8, where the radius-76.3 circle
  reaches the bag-corner x). These are short straight lateral walls
  (~32.5 mm in y), inside the inner shell, that close off the wedge corners
  of the bag-pocket region.

The 8 join points where flat meets vertical-jump and where vertical-jump
meets arc should be **filleted slightly** for printability and stress relief
— suggest 1–2 mm radius, CAD code's call.

The inner shell is **sealed at top and bottom** with PETG discs (part of
Floor 2's print) so the inner-cavity foam pour stays separated from the
outer-cavity foam pour. Both discs have small holes where the printed PETG
fitting shafts pass through.

## Bag pocket (dry cavity)

Each bag sits in a 5-walled PETG pocket against one of the inner-shell flat
sides. The pocket has six bounding faces:

| Face | Wall | Notes |
|---|---|---|
| Inboard (toward tank) | Inner-shell flat at y = ±76.3 | Shared with inner shell — bag's inner face rests directly against this PETG. No separate inboard pocket wall. |
| Outboard | Pocket outboard wall | 0.8 mm PETG, parallel to inner shell flat |
| +X end | Pocket end wall | 0.8 mm PETG, vertical |
| -X end | Pocket end wall | 0.8 mm PETG, vertical |
| Top (+Z) | Floor 3's top skin | Caps the pocket at z ≈ 225 mm |
| Bottom (-Z) | Floor 1's bottom skin | Bag cap end rests on this |

The pocket interior is **dry** — pour foam never enters. The bag must be
free to expand during fill and contract during empty. Wall clearance to the
bag at full 750 mL is approximately zero (bag form-fits the pocket); pocket
ID = bag OD = 125 × 35 mm.

The bag flavor tube exits through a **printed PETG conduit** in the pocket
outboard wall near the bag-cap elevation (z ≈ 0), running horizontally
through the outer foam region to the outer shell on the Y face. The bag tube
is press-fit through the outer-shell-side end of the conduit (grommet or
press-fit seal) before the outer-cavity foam pour. The conduit becomes the
permanent seal between the dry bag pocket and the foam-filled outer region.

## Floor breakdown

The cold core is printed as **three pieces, stacking vertically**. Each
piece is a single integral print — multiple "rooms" within a piece, but no
horizontal sub-division. Floors join at horizontal mating planes.

### Floor mating

**Pure butt joints + 4 locating pins per seam. No lap, tongue-and-groove,
or swept mating geometry on any wall.**

- The mating plane is horizontal (z = constant) at z ≈ 37 mm (Floor 1 / 2)
  and z ≈ 189 mm (Floor 2 / 3).
- Every wall that crosses the mating plane (outer shell perimeter, bag-
  pocket outboard wall, bag-pocket end walls, printed PETG fitting shafts)
  butts cleanly against its counterpart in the adjacent piece. No mating
  geometry on any wall — both ends are flat at the mating plane.
- **4 locating pins** on the outer shell perimeter (suggest near the four
  corners of the bounding rectangle) — ~3 mm diameter × 4 mm tall on the
  *lower* piece, matching holes on the *upper* piece. Pins print cleanly
  with their long axis along Z (no overhangs). These do all the alignment.
- Pour foam seals the seams. The Floor 1/2 and Floor 2/3 seams sit inside
  the outer-cavity foam region (Pour 2), so liquid foam expands across
  these seams during pour and bonds the pieces permanently after cure.
- **Bag-pocket wall mating edges should be coated with a thin bead of
  silicone or pour-foam paste at assembly time, before stacking.** This is
  the only seam where liquid foam ingress would damage the assembly (foam
  bonding to the bag), and an assembly-time sealant is sufficient. Not a
  CAD geometry concern.

This avoids the racetrack's pain points (45° swept grooves with T-
junctions where divider walls crossed the perimeter sweep). Each crossing
wall is independent. T-junctions between walls have no special mating
geometry to navigate.

Print orientation: each piece prints with one of its faces (the bottom
skin for Floor 1; the top skin for Floor 3, upside-down; either mating
face for Floor 2) on the build plate. The locating pins protrude from the
upper face during print, so they print as vertical extrusions (no
overhangs). All wall edges at mating planes are simple flat tops/bottoms.

### Floor 1 — bottom skin + bottom foam band

- z-range: **0 to ~37 mm**
- Outer-shell perimeter walls (full cold-core cross-section)
- **Bottom skin** at z = 0–0.8 mm (PETG slab, sealed, no cutouts)
- Bag-pocket lower walls — 5 sides except top, capping the bag-cap end of
  each bag
- Printed PETG **vertical shafts** for tank-bottom-plate fittings to thread
  through
- Printed PETG **conduits** (or simple cutouts) for tank-line lateral exits
  on the X face
- Printed PETG **conduits** for bag flavor tubes on the Y face
- Top of Floor 1 is open to receive Floor 2 (mating plane at z ≈ 37 mm)
- During the **outer-cavity foam pour**, foam fills this band, encasing the
  90° elbows + lateral tubing + the 6.35 mm thermal break under the tank's
  bottom plate

### Floor 2 — tank zone

- z-range: **~37 to ~189 mm** (matches tank assembled height of 152.4 mm)
- Outer-shell perimeter walls (continuing from Floor 1)
- **Inner shell** (flatted-stadium cross-section), sealed top and bottom
  with PETG discs. Bottom disc at z ≈ 30 mm includes shaft holes for the
  bottom-plate fittings; top disc at z ≈ 196 mm includes shaft holes for
  the top-plate fittings
- **4 small printed standoffs** (~5 × 5 × 0.8 mm) on the inner-shell
  interior wall at z = 37 mm, supporting the tank's bottom-plate perimeter
  during assembly. Standoffs are permanent — foam-encased after pour, but
  they pre-position the tank without requiring an external fixture
- Bag-pocket walls (continuing the open shaft from Floor 1, no horizontal
  partition where the bag passes)
- During the **inner-cavity foam pour**, foam fills inside the inner shell
  around the tank — wedge corners on Y face, 5 mm + coil zone everywhere
  else, 6.35 mm foam-floor below the tank's bottom plate, 6.35 mm foam-
  ceiling above the tank's top plate
- During the **outer-cavity foam pour**, foam fills outside the inner shell
  on X face and around the bag pockets, between the inner shell and outer
  shell

### Floor 3 — top foam band + top skin

- z-range: **~189 to ~226 mm**
- Outer-shell perimeter walls (continuing from Floor 2)
- **Top skin** at z = ~225–226 mm (PETG slab, sealed; caps bag pockets and
  the outer-foam region)
- Mirror of Floor 1's printed shafts: vertical PETG shafts for top-plate
  fittings, lateral conduits for X-face exits
- **Printed PETG conduit** for the PRV vent path to atmosphere
- Bottom of Floor 3 is open to mate with Floor 2 at z ≈ 189 mm
- During the **outer-cavity foam pour**, foam fills this band, encasing the
  top elbows + lateral tubing + PRV body + thermal break above the tank's
  top plate

## Foam pours

Two separate pours, in the order below.

### Pour 1 — inner cavity

- **Volume:** inside the inner shell only (Floor 2's inner cavity)
- **Encases:** the tank on all sides, including the 6.35 mm foam-floor
  below the tank's bottom plate and the 6.35 mm foam-ceiling above the
  tank's top plate, plus the wedge corners on Y face (12–32 mm of foam
  inside the inner shell where the flat is offset from the tank surface)
- **Tank position:** held by the 4 printed standoffs; no external fixture
  needed
- **Fill port:** small hole through the inner shell's top PETG disc (in
  Floor 2). Foam expands from this point through the cavity.
- **Vents:** small holes near the top of the inner-shell PETG disc for
  excess

### Pour 2 — outer cavity

- **Volume:** everywhere outside the inner shell but inside the outer shell
  — Floor 1's bottom foam band, Floor 3's top foam band, and the outer-foam
  region in Floor 2 around the bag pockets and outside the inner shell on
  X face. One continuous volume because Floors 1, 2, 3 stack with the outer
  region open between them.
- **Encases:** the 90° elbows + lateral tubing on both top and bottom plates,
  the PRV body (sitting horizontally in the top foam band), the refrigerant
  stubs from the evaporator coil, and all sensor wires
- **Pre-pour requirements:**
  - Bags must be installed in their pockets
  - Bag flavor tubes must be threaded through the printed PETG conduits and
    seated with grommets at the Y-face outer-shell exits
  - All external tubing (refrigerant stubs, sensor wires, fitting tube
    exits, PRV vent) must be in final routed position
- **Fill port:** small hole through Floor 3's top skin
- **Vents:** small holes near the top of the outer-shell perimeter

After both pours cure, trim flush at fill ports and vents.

## Assembly sequence

1. Print Floor 1, Floor 2, Floor 3.
2. Pre-assemble the tank: vessel + bonded coil + reed switches + DS18B20
   probes + 1/4" NPT fittings on all four ports + 90° elbows + lateral
   tubing routed to where the X-face exits will be + refrigerant stubs +
   sensor wire pre-routes.
3. Stack Floor 1.
4. Stack Floor 2 onto Floor 1.
5. Drop the pre-assembled tank down through the inner shell's open top in
   Floor 2. The tank's bottom-plate perimeter lands on the 4 printed
   standoffs at z = 37 mm. Bottom-plate fittings extend down through Floor
   2's bottom-disc shaft holes and continue into Floor 1's bottom foam band
   region, with lateral tubing routed to Floor 1's X-face exits.
6. **Pour 1** (inner-cavity foam) through the inner-shell top disc fill
   port. Cure.
7. Install bags into the dry pockets. Route bag flavor tubes through the
   printed PETG conduits. Seat grommets at the Y-face outer-shell exits.
8. Stack Floor 3 onto Floor 2. The tank's top-plate fittings (already
   installed in step 2) extend up through Floor 3's top-disc shaft holes.
   The PRV body sits horizontally in the top foam band; its outlet
   connects to Floor 3's PRV vent conduit.
9. **Pour 2** (outer-cavity foam) through the Floor 3 top-skin fill port.
   Cure.
10. Trim flush at fill ports and vents.

## Deferred to the CAD agent

Detail decisions the CAD code should make without further requirements:

- Exact angular positions of the 4 tank-supporting standoffs (suggest
  evenly spaced around the tank-plate footprint — e.g., at the inner shell's
  ±X axis and ±Y axis intersections with the tank plate).
- Fillet radii at the inner shell's 8 cross-section join points (suggest
  1–2 mm).
- Exact positions and dimensions of the bottom-plate and top-plate fitting
  shafts. These depend on the tank-plate port layout, which is specified in
  the cut-parts plate file (`endcap-circular-2hole.dxf` currently has 2
  holes — confirm whether ports are labeled such that the foam-bag-shell
  knows which port is CO2 vs water, etc.).
- Exact PETG conduit dimensions and routing for the bag flavor tubes and
  PRV vent (depends on the specific tubing OD; budget ~8 mm ID conduit for
  1/4" tubing).
- Foam-pour fill-port and vent-hole positions and dimensions.
- Stacking retention during foam cure (zip-tie holes, screw bosses, or
  external clamp — TBD).

## Reference scripts

For CadQuery code structure and conventions, see:

- [`../plan-b/foam-bag-shell-racetrack/generate_step_cadquery.py`](../plan-b/foam-bag-shell-racetrack/generate_step_cadquery.py)
  — the racetrack-stadium predecessor; shares the geometry-by-band approach
  but is specific to plan B.
- [`../pump-case/generate_step_cadquery.py`](../pump-case/generate_step_cadquery.py)
  — **gold standard** for PETG enclosure design pattern in this repo.
  Follow its structure: constants grouped by concern, geometry helpers,
  feature functions, top-level assembly as a bill of operations.

The cadquery venv lives at `tools/cad-venv/bin/python` (per
[`hardware/CLAUDE.md`](../../CLAUDE.md) — cadquery is not on system Python).
