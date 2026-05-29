# Foam shell

3D-printed PETG enclosure for the soda machine's "cold core" — the
back-of-enclosure subsystem that holds the carbonator pressure vessel, the
copper evaporator coil wrapped around it, and two flavor reservoirs in
pockets on opposite sides. Pour-in-place polyurethane foam fills the
cavities around the wetted/cold parts for thermal insulation.

## Coordinate convention

The CadQuery script uses an explicit XY plane with +Z normal
(`xy_plane_z_up`), so geometry grows upward in +Z.

- **Z** is vertical. The floor sits at z=0; everything stacks upward from
  there.
- **X** is the reservoir axis. Two reservoir pockets sit on opposite sides along X.
- **Y** is perpendicular to the reservoir axis.

## Physical inputs

- **Pressure vessel** — 5.000" OD × 0.065" wall × 6.000" cut length 316 SS
  welded tube (OnlineMetals #12498). Two 1/4"-thick 316 SS endcap plates
  laser-welded internally, recessed flush with the tube ends. Hand-tapped
  1/4" NPT, four ports total — two top plate (water inlet, PRV), two
  bottom plate (CO2 inlet, water outlet). Vessel assembled height = tube
  length = **[152.4 mm](TANK_H)**. Outer radius = **[63.5 mm](TANK_R)**.
- **Reservoir** — printed rigid PETG flavor reservoir, one per flavor,
  two per cold core. Cap on top with a single ⌀[6.5 mm](PORT_D) bulkhead
  pass-through; bottom is a wet-slope floor with a printed boss for the
  internal SS float rod. Body envelope: **[140 mm](RESERVOIR_W) wide (along Y)
  × [48 mm](RESERVOIR_D) deep (along X, radially outward) × [199.4 mm](RESERVOIR_H)
  tall**, sized to hold ≥ 1 L usable per reservoir. Reservoir geometry
  and internal features live at [`../reservoir/`](../reservoir/).
- **Evaporator coil** — 1/4" OD × 0.187" ID × 0.031" wall ACR copper,
  hand-wound helically around the vessel exterior, bonded with 3M 425
  aluminum foil tape. ~6.35 mm radial occupancy plus tolerance — budgeted
  at [7 mm](COIL_GAP).
- **Tank-port fittings** — 1/4" NPT 90° elbows on every port, turning the
  line laterally. ~[30 mm](ELBOW_ENV) vertical envelope per elbow above
  and below the tank. An additional **John Guest PP0308E 1/4" PTC 90° elbow**
  seats in the Ø16 CO2 inlet bore at x = 0, y = −70.5, where the cap-top
  CO2 line transitions 90° into a horizontal run that connects to the
  vessel-port TAISHER elbow via a PP010822E 1/4" PTC × 1/4" NPT M adapter.

## Shells

The geometry is built up from open-topped sub-shells that union into
one foam-shell solid. **All structural walls and floors use [2 mm](WALL_T)
thickness.**

### reservoir_pocket_walls

Two reservoir pockets, one on each ±X side of the cold-core, mirrored
across the YZ plane. Each pocket is a four-walled enclosure (open at
+Z; the outer_shell's floor closes the bottom; the foam_cap closes
the top during foam pour):

- **Far ±X wall** — outboard face at x = ±[123.5 mm](POCKET_X_OUTER), cavity face at
  x = ±[121.5 mm](POCKET_X_INNER).
- **+Y wall** — outboard face at y = +[72.5 mm](POCKET_ARC_R), cavity face at y = +[70.5 mm](POCKET_ARC_INNER_R).
- **−Y wall** — outboard face at y = −[72.5 mm](POCKET_ARC_R), cavity face at y = −[70.5 mm](POCKET_ARC_INNER_R).
- **Centerward wall** — the only curved wall. Its cavity-side face
  rides on a cylinder of radius **[72.5 mm](POCKET_ARC_R)** (centered on the
  cold-core Z axis); its tank-side face is concentric one wall-thickness
  inboard. The [7 mm](COIL_GAP) of radial clearance between the
  tank's outer face (R = [63.5 mm](TANK_R)) and the wall's tank-side
  face fits the 1/4" ACR copper coil + thermal tape + slack.

The centerward wall is one continuous curved wall built from three
arc segments along its length:

1. A **middle segment** — the cylindrical arc that wraps the tank+coil
   envelope, running from y = −[60 mm](POCKET_ARC_TRANSITION_Y) to y = +[60 mm](POCKET_ARC_TRANSITION_Y).
2. Two **transition segments**, one at each ±Y end — short
   [8 mm](TRANSITION_ARC_R)-radius arcs that swing the wall out from
   the middle arc to the pocket's ±Y wall. Each transition arc is
   tangent to the middle arc and to the ±Y outboard face; its
   tank-side face has radius [8 mm](TRANSITION_ARC_R) and its
   cavity-side face is concentric with the same center but a slightly
   smaller radius derived from geometry.

The two **far-side corners** (where the far +X wall meets the ±Y
walls) are filleted: **[6.5 mm](POCKET_CORNER_R) inner radius**,
outer radius one wall-thickness larger (so the wall thickness stays
uniform through the bend). The inner radius matches the rigid PETG
reservoir's outer fillet plus the [0.5 mm](RESERVOIR_GAP) clearance, so
the reservoir slides into a snugly-mated pocket with uniform clearance
around the corner.

The pocket is **open along its centerward face into the foam zone
inside the centerward arc envelope** — there's no wall at radius
R < [70.5 mm](POCKET_ARC_INNER_R). During operation, that interior region
holds the tank + copper coil, and the foam pour fills the gap
between the coil and the wall's tank-side face.

The four walls of each pocket are traced as a single connected
outer-perimeter polyline (with the matching cavity-perimeter polyline
cut out of it), so the four walls union into one solid by
construction. The +X pocket is traced explicitly; the −X pocket is
its mirror across YZ. Total assembly height = [213.4 mm](OUTER_H).

### tank_support_ring

Annular ring sitting inside the lower portion of the assembly,
holding the tank up by its outer rim. The ring's outer face is
coincident with the centerward wall's tank-side face; its inner
face sits [9 mm](SUPPORT_RING_W) inboard. The top face is a flat
annular plateau where the tank's outer rim rests, [30 mm](SUPPORT_RING_H)
tall above the floor.

Inboard of the ring's inner face (R < [61.5 mm](SUPPORT_RING_INNER_R))
is open volume — so the tank's bottom-plate fittings have unobstructed
downward space, and pour foam fills around them.

Four 30°-wide angular slots are cut through the ring at azimuths
45°/135°/225°/315°, leaving four 60° support segments aligned with
the cardinal axes. The slots let pour foam reach the under-tank
floor regardless of which cavity it enters from.

### outer_shell

Outer rectangular cup framing the whole foam-shell: floor + four
perimeter walls + six [8 × 8 mm](BOSS) bosses. Total height matches
the foam-shell outer height of [213.4 mm](OUTER_H).
Outer footprint [283 mm](OUTER_X) × [181](OUTER_Y),
sized to leave [16 mm](OUTER_GAP) of foam-pour zone
between the outer_shell's inner face and the outermost reservoir-
pocket walls on each side.

The six bosses are positioned at the four corners + two mid-long-side
positions (offset in X by ±[15 mm](MID_BOSS_OFFSET) with opposite signs
at +Y vs −Y, to preserve 180° rotational symmetry around the Z axis).
Each boss carries a heat-set insert pocket at the top (drilled down
from the top face) and at the bottom (drilled up from the bottom face) —
twelve inserts total, six per face, for fastening the foam_cap above
and below.

The outer +Y wall carries the shared copper/water-inlet slot, the
two ⌀[6.5 mm](PORT_D) reservoir-line holes, the two reed-cable holes,
and the water-outlet hole. See Penetrations. (The CO2 inlet bore is
internal to the assembly — it cuts down through the support ring at
−Y, not through any outer wall.)

### foam_cap and foam_cap_lid

The `foam_cap` is a [16 mm](CAP_H)-tall cup matching the outer
shell's footprint, printed twice — one sits on top of the assembly
(flipped, open side mating with the outer shell's top edge) and one
on the bottom (in normal orientation, open side mating with the
outer shell's bottom edge). The cap interior receives the foam pour
through pour and vent holes in the lid above.

The `foam_cap_lid` is a flat [2 mm](WALL_T) plate matching the same
outer footprint, sitting on top of a cap during its foam pour. It
has the pour hole (Ø [10 mm](POUR_D)) and two vent holes
(Ø [6 mm](VENT_D)).

Both the cap and the lid have **six [8 × 8 mm](BOSS) boss / clearance-hole
positions** — four at the corners and two at the mid-points of the long
edges (one near the +Y wall and one near the −Y wall, offset in X by
±[15 mm](MID_BOSS_OFFSET) with opposite signs at +Y vs −Y for 180°
rotational symmetry). Each position passes a clearance hole for an M3
cap screw all the way through the part. See "Cap-to-outer-shell
joinery" below.

### foam_cap_gasket

A TPU 90A gasket, printed twice — one between each cap and its
mating face on the outer_shell. Outer envelope matches the cap's
footprint; [2 mm](GASKET_T) thick (flat 2D shape throughout — no 3D
features). The shape is a **[5 mm](GASKET_W)-wide perimeter ring +
an [8 × 8 mm](BOSS) pad at each of the six screw positions**,
matching the boss footprints on the cap and shell above and below.
The pads carry the screw clamp force across the full boss footprint;
the perimeter ring seals along the wall sections away from the bosses.

## Cap-to-outer-shell joinery

Each cap (top and bottom) is fastened to the outer_shell with **six
M3 × 25 mm DIN 912 socket head cap screws, 12.9 alloy steel, black
oxide finish** ([BNUOK B0DJQGF665](https://www.amazon.com/dp/B0DJQGF665),
60-pc bag $8.57 delivered = $0.14/screw, head Ø 5.5 × 3.0 mm tall,
2.5 mm hex) threading into **six ruthex M3 short heat-set inserts**
([B09ZHSGHXD](https://www.amazon.com/dp/B09ZHSGHXD) — same insert
spec as in `touch-flo-shell`; the 100-pc bag already on order for
that part covers ~7 builds at the combined 14-inserts-per-unit
total) pressed into the corresponding face of the outer_shell.
**Twelve inserts and twelve screws total per outer_shell:** six on
the top face accepting the top-cap screws threading down from above,
six on the bottom face accepting the bottom-cap screws threading up
from below.

Each cap-to-shell joint compresses a stack of lid + cap floor + cap
boss / interior void + cap mating edge + [2 mm](GASKET_T) gasket
above the outer_shell mating face. The screw engages a heat-set
insert in the outer_shell with a small relief below the insert for
tip clearance. See `_foam_cap.py` and `_cold_core_interface.py` for
the values that set the screw length.

Insert pocket: Ø 4.0 mm × [8 mm](INSERT_DEPTH) deep (insert
engagement + tip-relief). Pockets are drilled inward from each face —
top face pockets go down, bottom face pockets go up.

## Penetrations

Eight pass-throughs total, all carrying **1/4" OD tubing (6.35 mm)** through
holes sized at ⌀[6.5 mm](PORT_D) for a tight tube fit. Four pass-throughs
each get their own dedicated round hole; the remaining four share a single
Z-elongated slot at the +Y outer wall.

| # | Pass-through | Opening | Carries |
|---|---|---|---|
| 1 | Reservoir line (+X) | own ⌀[6.5 mm](PORT_D) hole | 1/4" OD soft tubing — reservoir to peristaltic pump |
| 2 | Reservoir line (−X) | own ⌀[6.5 mm](PORT_D) hole | 1/4" OD soft tubing — reservoir to peristaltic pump |
| 3 | CO2 inlet | own ⌀16 doorway | 1/4" OD line from the regulator (90° push-to-connect elbow seats in the doorway) |
| 4 | Water outlet | own ⌀[6.5 mm](PORT_D) hole | 1/4" OD line to the dispense faucet |
| 5 | Copper evaporator inlet (low) | shared +Y slot | 1/4" OD ACR copper to compressor |
| 6 | Copper evaporator outlet (high) | shared +Y slot | 1/4" OD ACR copper to compressor |
| 7 | Water inlet | shared +Y slot | 1/4" OD line from the diaphragm pump |
| 8 | PRV vent | shared +Y slot | 1/4" OD LLDPE from the prv-shroud cap into the appliance interior (unpressurized; carries relief-event discharge only — see [`../prv-shroud/`](../prv-shroud/)) |

For the water inlet and CO2 inlet, the supply-side tubing reduces to
1/4" OD before reaching the shell wall — transition fittings (3/8"
barb-to-NPT adapter, 5/16" push-to-connect, 1/4" NPT check valves, etc.)
live on the warm side of the shell. Inside the shell, every penetration
is 1/4" OD.

### Shared +Y slot and copper plug stack

The +Y outer_shell wall carries four pass-throughs along a single
**Z-elongated slot** at x = 0: the two copper evaporator lines (low
and high), the water inlet, and the PRV vent. The slot is
⌀[6.5 mm](PORT_D) wide in X (rounded ends along Z) and is cut by
`cut_slot_for_copper_and_water_inlet` in `_port_cuts.py`. The slot's
top extends past the wall top so no sliver of wall material remains
above the slot — the four plugs can slide down into the slot from
above during assembly. With the centerward wall extending only to
y = ±[72.5 mm](POCKET_ARC_R) (where it meets the ±Y walls via the
transition arcs), the slot pierces only this one outer +Y wall.

Pass-through Z heights (centers, measured from the **top of the
floor** — i.e. from the interior cavity's lower bound, not from z = 0):

| Pass-through | Z center above floor (mm) |
|---|---|
| Lowest copper (evaporator inlet) | 45.0 |
| Highest copper (evaporator outlet) | 164.4 |
| Water inlet | 196.4 |
| PRV vent | 204.4 |

(Absolute Z in the CadQuery model is +`wall_and_floor_thickness`
above these — i.e. 47.0 / 166.4 / 198.4 / 206.4 at the current
2 mm wall — since the floor occupies z = 0 to
z = `wall_and_floor_thickness`.)

Four printed PETG **copper plugs** slide down into the slot from
above to seal the gaps between (and above) the four pass-throughs:

| Plug | Z span (mm) | Z end arches |
|---|---|---|
| `copper-plug-lower` | 50.75 → 162.65 | both ends |
| `copper-plug-middle` | 170.15 → 194.65 | both ends |
| `copper-plug-upper` | 202.15 → 202.65 | both ends |
| `copper-plug-top` | 210.15 → 211.40 | bottom end only (top flat) |

Each plug has a **binder-clip cross-section** that grips the wall
edge instead of floating loosely in the slot. Viewed end-on, it's an
I-beam: a 6.5 mm × 2 mm plate-body web fits the slot's wall Y range
exactly, 4 mm-tall "wings" at the outer X edges of the slot span the
full plug Y envelope, and 1 mm × 1 mm rail prongs branch out past
the wings at +Y (above the wall outer face) and −Y (below the wall
inner face). The 2 mm air gap between the top and bottom prongs at
the rail edges is where the wall material slides in — that's how
the plug grips the wall like a binder clip. The wings act as the
I-beam flange linking web to prongs along a continuous 2D face. See
the docstring at the top of `copper-plugs/copper_plugs.py` for the
full cross-section diagram.

Each plug end that abuts a tube has a **⌀[6.5 mm](PORT_D) half-circle
arch cutout** centered at x = 0, so the plug seats around the tube
without crushing it. `lower`, `middle`, and `upper` all arch at both
Z ends; `top` arches at the bottom Z end only (its top is flush with
the wall top and stays flat).

After the four plugs are installed, the slot's remaining unfilled
length within the wall along Z (a strip at the bottom of the slot,
a strip at the top, and narrow clearance bands above and below each
of the four tubes) gets filled by the body foam pour.

## Assembly and foam pour

Production-procedure framing at [`../../../assembly/cold-core.md`](../../../assembly/cold-core.md). The geometry detail below is the source-of-truth for the shells and the pour paths; the assembly doc is the production-cadence wrapper that places this pour in the appliance build sequence.

The cold core is foam-filled in **three independent pour operations**:
the top cap, the bottom cap, and the body. Each is a self-contained
pour; nothing chains across the three.

### Top cap and bottom cap (independent, before final assembly)

Each cap is a [16 mm](CAP_H)-tall foam-filled cup. Liquid pour-in-place
foam goes in through the `foam_cap_lid`'s Ø[10 mm](POUR_D) pour hole,
air escapes through the lid's two Ø[6 mm](VENT_D) vents, foam expands
to fill the cap's interior, cures to a self-contained foam puck.
Done before the cap is mated to the body.

### Body pour (after all body-side assembly)

Every internal component is installed first:

- Pressure vessel lowered into the centerward arc envelope, seated
  on the `tank_support_ring`.
- Copper evaporator coil hand-wound around the vessel exterior and
  bonded with 3M 425 aluminum foil tape.
- Reservoirs installed into the two reservoir pockets.
- Copper evaporator inlet (low), copper evaporator outlet (high),
  water inlet, and PRV vent LLDPE (from the prv-shroud cap) routed
  through the shared +Y slot at their four Z heights. The water
  inlet and PRV vent both come from above the tank and take slight
  bends in their LLDPE runs to land in vertical alignment in the
  slot.
- Four copper plugs slid down into the slot from above (through
  the 10 mm open extension past the wall top) to seal between the
  pass-throughs.
- PRV shroud subassembly (`../prv-shroud/`) — already built and
  cured ahead of time, threaded into Port 4 at vessel install — is
  here as part of the vessel by the time the body pour happens.
  Press-fit a length of 1/4" OD LLDPE into the shroud's cap hole and
  route it through the +Y slot to the appliance interior.
- Reservoir LLDPE lines routed through holes #1 and #2 in the
  reservoir-pocket far ±X walls.
- Water outlet through hole #4 in the outer_shell +Y wall.
- CO2 inlet enters from above through the foam-cap-top boss +
  foam-cap-lid-top hole at (x=0, y=−68.75); the line drops to
  z=17 inside the cavity and bends 90° at a PP0308E push-to-connect
  elbow seated in the Ø16 CO2 inlet bore at x = 0, y = −70.5.

With everything in place, liquid foam is poured **directly into the
body's open +Z top** all at once — no cap on, no down-channels.
Foam falls into the body and reaches the two air volumes in
parallel:

- the **two reservoir-pocket cavities** (each open at +Z, fully
  enclosed below and on its four sides);
- the **surrounding foam zone** — a single connected volume wrapping
  around the pockets between the outer_shell and the pockets'
  outboard walls. This zone reaches the centerward space around the
  tank+coil through the gap at x ∈ [−39.7, +39.7] where the pockets'
  ±Y walls end (y = ±72.5) and the centerward walls' transition arcs
  swing in to join them.

The longest required slot traverse for the foam is the ~0.5 mm
radial gap between the coil and the centerward wall's tank-side
face at the ±X azimuths — ~110 mm of arc to reach around the back
of the coil from the ±Y entry.

Foam expansion may push a small amount of material out through the
clearance bands around tubes in the +Y slot and through the tight-fit
tube exits at the other penetrations. Trim flush after cure.

### Final assembly (after all three foam pours have cured)

TPU gasket onto the body's top edge, top cap screwed down with six
M3 × 25 SHCS. Bottom cap screwed onto the body's underside (no
gasket — the body floor handles the air seal). See the screw /
insert spec under "Cap-to-outer-shell joinery" above.

## Coincident-wall principle

Wherever two structural surfaces touch in the assembly, their walls
**overlap exactly in 3D space** — same outer face, same inner face.
After union, that boundary is one wall's worth of material (2 mm).

This drives several dimension choices:

- Each **reservoir pocket's ±Y outboard face** sits at
  y = ±`pocket_centerward_arc_outer_radius` (= ±72.5), tangent to the
  cylinder the centerward arc rides on. The ±Y walls meet the
  centerward wall's transition arcs along that tangent.
- The **tank_support_ring**'s outer face sits at
  `pocket_centerward_arc_outer_radius − wall_and_floor_thickness`
  (= 70.5), coincident with each pocket's centerward wall on its
  tank-side face.
- Each **reservoir pocket's four walls** are traced as a single
  connected outer-perimeter polyline (with one cavity-perimeter
  polyline cut from it), so the four walls union into one solid by
  construction.
- The **outer_shell**'s inner face sits [16 mm](OUTER_GAP)
  outboard of the outermost reservoir-pocket walls — the outer
  foam-pour zone.

## Print settings

**Print with stock Bambu Studio defaults.**

Plate contents (when slicing): `foam-shell` + `copper-plug-lower` +
`copper-plug-middle` + `copper-plug-upper` together; `foam-cap` and
`foam-cap-lid` on a separate plate.

### Printer / profile

- **Printer:** Bambu Lab H2C, **0.8 mm nozzle**
- **Print profile:** `0.40mm Standard @BBL H2C 0.8 nozzle`
- **Layer height:** 0.4 mm (initial layer 0.4 mm)
- **Line width:** 0.82 mm (inner / outer / top all 0.82)
- **Wall loops:** 2
- **Top / bottom shells:** 4 / 3
- **Sparse infill:** 15 % grid
- **Speeds (mm/s):** outer 200, inner 300, infill 350, top 200,
  travel 1000, initial layer 50
- **Supports:** off (threshold 30°)
- **Brim:** auto, 5 mm width, 0.1 mm object gap, 0.15 mm elephant-foot
  compensation
- **Wrapping detection:** off

### Filament

- **Material:** Bambu PETG Basic @BBL H2C
- **Nozzle temp:** 250 °C (initial layer 245 °C)
- **Bed:** Textured PEI Plate at 70 °C
- **Chamber:** passive (`chamber_temperatures: 0`)
- **Flow ratio:** 0.97
- **Max volumetric speed:** 21 mm³/s (28 on the second nozzle slot)
- **Part-cooling fan:** max 40 %, min 20 %, overhang 90 % at ≥ 10 %
  overhang, closed first 3 layers
- **Auxiliary fan (P1):** on

## Regression baseline

Source-level refactors of `_foam_shell.build_full_shell()` should
preserve the geometry of `foam-shell.step` exactly. These scalars
are the canonical regression sieve — any change to them (beyond
OCCT numerical noise at the ~1e-6 mm³ level) is a geometry shift
that needs a deliberate explanation:

| metric | value |
|---|---|
| volume | [1049790.912 mm³](VOLUME) |
| bbox x | [-141.500 to 141.500 mm](BBOX_X) |
| bbox z | [0.000 to 213.400 mm](BBOX_Z) |
| bbox y | [-90.500 to 90.500 mm](BBOX_Y) |
| centroid | [(0.000005, -0.619692, 88.802543) mm](CENTROID) |

Quick reproduction:

```python
import cadquery as cq
s = cq.importers.importStep("foam-shell.step").val()
bb = s.BoundingBox()
com = s.Center()
print(s.Volume(), (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax), (com.x, com.z, com.y))
```

## Reference

- [`../../flavor/pump-case/pump_case.py`](../../flavor/pump-case/pump_case.py)
  — gold standard for the PETG-enclosure pattern in this repo.

The cadquery venv lives at `tools/cad-venv/bin/python` (cadquery is not
on system Python).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/foam-shell/foam_shell.py`
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
