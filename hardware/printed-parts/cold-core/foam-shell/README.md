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
  two per cold core. Cap on top with a single ⌀[6.5 mm](TUBE_HOLE_D) bulkhead
  pass-through; bottom is a wet-slope floor with a printed boss for the
  internal SS float rod. Body envelope: **[140 mm](RESERVOIR_W) wide (along Y)
  × [48 mm](RESERVOIR_D) deep (along X, radially outward) × [199.4 mm](RESERVOIR_H)
  tall**, sized to hold ≥ 1 L usable per reservoir. Reservoir geometry
  and internal features live at [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/).
- **Evaporator coil** — 1/4" OD × 0.187" ID × 0.031" wall ACR copper,
  hand-wound helically around the vessel exterior, bonded with 3M 425
  aluminum foil tape. ~6.35 mm radial occupancy plus tolerance — budgeted
  at [7 mm](COIL_GAP). The coil is embedded in the inner slice of the
  cylinder's foam blanket; pour foam fills the helical gaps between wraps
  and out to the reservoir wall.
- **Tank-port fittings** — 1/4" NPT 90° elbows on every port, turning the
  line laterally. ~[30 mm](ELBOW_ENV) vertical envelope per elbow above
  and below the tank. An additional **John Guest PP0308E 1/4" PTC 90° elbow**
  stands in the [18](CO2_NOTCH_W) mm-wide CO2 inlet notch at x = 0, cut inward
  from the +Y face at y = [+78.5](CO2_DOORWAY_Y), where the CO2 line entering
  from above through the foam-cap stack transitions 90° into a horizontal run
  that connects to the vessel-port TAISHER elbow via a PP010822E 1/4" PTC ×
  1/4" NPT M adapter. That elbow is made up on the vessel at the bench and
  descends through the notch as the vessel seats, so the notch is open to the
  ring's top plateau — nothing arches over it.

## Shells

The geometry is built up from open-topped sub-shells that union into
one foam-shell solid. **All structural walls and floors use [2 mm](FSHELL_WALL_T)
thickness.**

### reservoir_pocket_walls

Two reservoir pockets, one on each ±X side of the cold-core, mirrored
across the YZ plane. Each pocket is a four-walled enclosure (open at
+Z; the outer_shell's floor closes the bottom; the shell's open +Z
top receives the foam pour):

- **Far ±X wall** — outboard face at x = ±[131.5 mm](POCKET_X_OUTER), cavity face at
  x = ±[129.5 mm](POCKET_X_INNER).
- **+Y wall** — outboard face at y = +[72.5 mm](POCKET_Y_OUTER), cavity face at y = +[70.5 mm](POCKET_Y_INNER).
- **−Y wall** — outboard face at y = −[72.5 mm](POCKET_Y_OUTER), cavity face at y = −[70.5 mm](POCKET_Y_INNER).
  The ±Y half-width is the reservoir's own standalone flavor-charge
  dimension (the window that holds 2 × SodaStream 0.44 L bottles); it
  is not derived from the centerward-arc radius, so growing the
  cylinder's foam blanket slides the pocket outward without resizing
  or splaying the reservoir.
- **Centerward wall** — the only curved wall. Its cavity-side face
  rides on a cylinder of radius **[80.5 mm](POCKET_ARC_R)** (centered on the
  cold-core Z axis); its tank-side face is concentric one wall-thickness
  inboard. That tank-side face is the reservoir's tank-facing wall, and
  because it is a concentric arc the span from the cylinder OD
  (R = [63.5 mm](TANK_R)) out to it is a uniform 15 mm of foam around the
  wrapped arc — the cylinder's designed foam blanket, with the 1/4" ACR
  copper coil ([7 mm](COIL_GAP) radial) embedded in its inner slice and
  pour foam filling everywhere the copper isn't.

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
R < [78.5 mm](POCKET_ARC_INNER_R). During operation, that interior region
holds the tank + copper coil, and the foam pour fills the full 15 mm
blanket from the cylinder OD out to the wall's tank-side face —
around and between the embedded helical wraps.

The four walls of each pocket are traced as a single connected
outer-perimeter polyline (with the matching cavity-perimeter polyline
cut out of it), so the four walls union into one solid by
construction. The +X pocket is traced explicitly; the −X pocket is
its mirror across YZ. Total assembly height = [213.4 mm](OUTER_H).

### tank_support_ring

Annular ring sitting inside the lower portion of the assembly,
holding the tank up by its outer rim. The ring's outer face sits on
the tank+coil envelope (R = 70.5, the tank OD plus the coil radial
clearance) — inboard of the pocket's centerward wall, which has moved
outward with the foam blanket. Its inner face sits [9 mm](SUPPORT_RING_W)
inboard. The top face is a flat annular plateau where the tank's outer
rim rests, [30 mm](SUPPORT_RING_H) tall above the floor.

Inboard of the ring's inner face (R < [61.5 mm](SUPPORT_RING_INNER_R))
is open volume — so the tank's bottom-plate fittings have unobstructed
downward space, and pour foam fills around them.

Four 30°-wide angular slots are cut through the ring at azimuths
45°/135°/225°/315°, leaving four 60° support segments aligned with
the cardinal axes. The slots let pour foam reach the under-tank
floor regardless of which cavity it enters from.

The +Y segment carries the **CO2 inlet notch** — [18](CO2_NOTCH_W) mm wide
at x = 0, cut through the ring's full radial width and its full height, so
it opens through the top plateau at z = [32](CO2_NOTCH_Z_TOP). The PP0308E
elbow rides down it with the vessel. The notch splits that segment into two
~22° bearing arcs; the other three segments are untouched.

### outer_shell

Outer rectangular cup framing the whole foam-shell: floor + four
perimeter walls + six ⌀[8 mm](BOSS_D) cylindrical bosses. Total height
matches the foam-shell outer height of [213.4 mm](OUTER_H).
Outer footprint [283 mm](OUTER_X) × [181](FSHELL_OUTER_Y). The outboard
foam-pour gap is split by direction: the ±Y (front/back) faces leave
[16 mm](OUTER_GAP) of foam-pour zone between the outer_shell's inner
face and the pocket's ±Y walls, while on the ±X (reservoir) side there
is no outboard foam — the reservoir's reed channel butts the outer
shell wall. The 283 mm outer width is held that way: the reservoir,
shifted outward by the cylinder's foam blanket, lands with its reed
channel against the shell wall, and the foam that would otherwise sit
outboard of the reed has moved to the cylinder side.

The four vertical corners are rounded — the exterior wall is a true
[12 mm](CORNER_ROUND_R)-radius quarter-arc on the outer face, the inner
face concentric one wall-thickness inboard — so the warp-prone sharp
corner is gone and the corner boss is wrapped by a curved wall.

The six bosses are positioned at the four corners + two mid-long-side
positions (offset in X by ±[15 mm](MID_BOSS_OFFSET) with opposite signs
at +Y vs −Y, to preserve 180° rotational symmetry around the Z axis).
Every boss sits tangent to the EXTERIOR wall and is tied into it with the
cylinder + corner-fill teardrop idiom of the reservoir pocket-corner
supports, so the boss fuses into the outer skin (one wall-thickness of PETG
over the insert) instead of meeting the wall on a knife-edge seam. A corner
boss sits against two walls (a far ±X wall and an end ±Y wall), so it gets
two webs — one toward each — with the diagonal-inboard quadrant left open
for foam. A mid-side boss sits against one wall, so it gets a single web
toward it (a D: flat to the wall, round toward the foam). Each boss carries
a heat-set insert pocket at each end (drilled in from each face) — twelve
inserts total, six per face, for fastening the foam-cap stacks.

The outer −Y wall carries the shared copper/water-inlet slot, the
two ⌀[6.5 mm](TUBE_HOLE_D) reservoir-line holes, the two reed-cable holes,
and the water-outlet hole. See Penetrations. (The CO2 inlet bore is
internal to the assembly — it cuts down through the support ring at
+Y (the rear), not through any outer wall.)

### foam_cap and foam_cap_lid

The `foam_cap` is a [16 mm](CAP_H)-tall cup matching the outer
shell's footprint, printed twice. The top cap opens +Z (mouth up);
the bottom cap is the same cup built mouth-down so its open ceiling
faces −Z. Each seats with its floor against the shell's end face and
its open mouth + lid pointing outward — the lid is the outermost
(extreme-Z) layer at that end, most +Z on top and most −Z on the
bottom. Both share the one screw pattern (below), so the mouth-down
bottom cap lands its screws on the shell's existing bottom-face
inserts with no rotation. The cap interior receives the foam pour
through the pour and vent holes in the lid.

The `foam_cap_lid` is a flat [2 mm](FSHELL_WALL_T) plate matching the same
outer footprint, covering a cap's open mouth during its foam pour. It
has the pour hole (Ø [20 mm](POUR_D)) and two vent holes
(Ø [6 mm](LID_VENT_D)).

Both the cap and the lid carry the **same six ⌀[8 mm](BOSS_D) bosses with
teardrop corner-fill webs** as the outer shell (built from the one shared
boss builder, so every mating part's boss cross-section is identical) —
four at the corners and two at the mid-points of the long edges (one near
the +Y wall and one near the −Y wall, offset in X by ±[15 mm](MID_BOSS_OFFSET)
with opposite signs at +Y vs −Y for 180° rotational symmetry). Each position
passes a clearance hole for an M3 cap screw all the way through the part.
See "Cap-to-outer-shell joinery" below.

### foam_cap_gasket

A TPU 90A gasket, printed twice — one between each cap and its
mating face on the outer_shell. Outer envelope matches the cap's
footprint; [2 mm](GASKET_T) thick (flat 2D shape throughout — no 3D
features). The shape is a **[5 mm](GASKET_W)-wide perimeter ring +
a boss-shaped pad at each of the six screw positions**, the pads using the
same ⌀[8 mm](BOSS_D) boss + teardrop-web shape as the cap and shell above
and below. The pads carry the screw clamp force across the full boss
footprint; the perimeter ring seals along the wall sections away from the
bosses.

## Cap-to-outer-shell joinery

Each cap (top and bottom) is fastened to the outer_shell with **six
M3 × 25 mm DIN 912 socket head cap screws, 12.9 alloy steel, black
oxide finish** ([BNUOK B0DJQGF665](https://www.amazon.com/dp/B0DJQGF665))
threading into **six ruthex M3 short heat-set inserts**
([B0D39W228K](https://www.amazon.com/dp/B0D39W228K) — same insert
spec as in `touch-flo-shell`; per-build insert counts in
[`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13) pressed into the
corresponding face of the outer_shell. **Twelve inserts and twelve screws
total per outer_shell:** six on the top face accepting the top-cap screws
threading down from above, six on the bottom face accepting the bottom-cap
screws threading up from below.

Each screw engages a heat-set insert in the outer_shell with a small relief
below the insert for tip clearance. See `_foam_cap.py` and
`_cold_core_interface.py` for the values that set the screw length.

Insert pocket: Ø 4.0 mm × [8 mm](INSERT_DEPTH) deep (insert
engagement + tip-relief), drilled in from each face.

## Penetrations

Eight pass-throughs total, all carrying **1/4" OD tubing (6.35 mm)** through
holes sized at ⌀[6.5 mm](TUBE_HOLE_D) for a tight tube fit. Four pass-throughs
each get their own dedicated round hole; the remaining four share a single
Z-elongated slot at the −Y outer wall.

| # | Pass-through | Opening | Carries |
|---|---|---|---|
| 1 | Reservoir line (+X) | own ⌀[6.5 mm](TUBE_HOLE_D) hole | 1/4" OD soft tubing — reservoir to peristaltic pump |
| 2 | Reservoir line (−X) | own ⌀[6.5 mm](TUBE_HOLE_D) hole | 1/4" OD soft tubing — reservoir to peristaltic pump |
| 3 | CO2 inlet | own [18](CO2_NOTCH_W) mm notch, +Y | 1/4" OD line from the regulator (90° push-to-connect elbow stands in the notch) |
| 4 | Water outlet | own ⌀[6.5 mm](TUBE_HOLE_D) hole | 1/4" OD line to the dispense faucet |
| 5 | Copper evaporator inlet (low) | shared −Y slot | 1/4" OD ACR copper to compressor |
| 6 | Copper evaporator outlet (high) | shared −Y slot | 1/4" OD ACR copper to compressor |
| 7 | Water inlet | shared −Y slot | 1/4" OD line from the diaphragm pump |
| 8 | PRV vent | shared −Y slot | 1/4" OD LLDPE from the prv-shroud cap into the appliance interior (unpressurized; carries relief-event discharge only — see [`/hardware/printed-parts/cold-core/prv-shroud/`](/hardware/printed-parts/cold-core/prv-shroud/)) |

For the water inlet and CO2 inlet, the supply-side tubing reduces to
1/4" OD before reaching the shell wall — transition fittings (3/8"
barb-to-NPT adapter, 5/16" push-to-connect, 1/4" NPT check valves, etc.)
live on the warm side of the shell. Inside the shell, every penetration
is 1/4" OD.

### Two-bore front pass-throughs

Each reservoir's flavor line and reed cable crosses two walls on its way
out of the −Y face — the bag-pocket wall and the outer shell — with the
[16 mm](OUTER_GAP) pour band open between them. The two bores are not
coaxial. The pocket-wall bore stays beside the bulkhead, where the elbow's
lateral port points: x = ±[97 mm](FLAVOR_POCKET_X) for the line and
±[109 mm](CABLE_POCKET_X) for the cable. The outer-shell bore sits well
inboard of that — x = ±[47 mm](FLAVOR_SHELL_X) for the line and
±[60 mm](CABLE_SHELL_X) for the cable — and each run turns and travels
along the band to reach it.

The inboard exits are what let each line leave the shell clear of the
condenser+fan block standing against the cabinet wall, and fall straight
down the core's front face instead of traversing beneath the manifold
tray stack. Both runs are potted where they cross the band, as everything
in the band is. `cut_pour_band_pass_through` in `_cold_core_interface.py`
cuts the pair.

### Shared −Y slot and copper plug stack

The −Y outer_shell wall carries four pass-throughs along a single
**Z-elongated slot** at x = 0: the two copper evaporator lines (low
and high), the water inlet, and the PRV vent. The slot is
⌀[6.5 mm](TUBE_HOLE_D) wide in X (rounded ends along Z) and is cut by
`cut_slot_for_copper_and_water_inlet` in `_port_cuts.py`. The slot's
top extends past the wall top so no sliver of wall material remains
above the slot — the four plugs can slide down into the slot from
above during assembly. With the centerward wall extending only to
y = ±[72.5 mm](POCKET_Y_OUTER) (where it meets the ±Y walls via the
transition arcs), the slot pierces only this one outer −Y wall.

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
| `copper-plug-lower` | [47 → 166.4](PLUG_SPAN_LOWER) | both ends |
| `copper-plug-middle` | [166.4 → 198.4](PLUG_SPAN_MIDDLE) | both ends |
| `copper-plug-upper` | [198.4 → 206.4](PLUG_SPAN_UPPER) | both ends |
| `copper-plug-top` | [206.4 → 213.4](PLUG_SPAN_TOP) | bottom end only (top flat) |

The spans meet end-to-end **at the pass-through centers**: each plug
runs from one tube's center to the next, and the arch cutout at each
end holds exactly half of that tube. The stack tiles the slot from the
lowest copper to the wall top with no linear gaps — the tube is the gap.

Each plug has a **binder-clip cross-section** that grips the wall
edge instead of floating loosely in the slot. Viewed end-on, it's a
true I-beam: a 6.5 mm × 2 mm web fills the slot's X range at the
wall's Y range exactly, sandwiched between two 8.5 mm × 1 mm flanges
that run the full plug width and sit immediately outboard (−Y, past
the wall outer face) and inboard (+Y, toward the cavity, past the
wall inner face) of it. The 2 mm air gap between the two flanges, in
the wall's Y range and outside the web's X range, is where the wall
material slides in — that's how the plug grips the wall like a
binder clip. See the docstring at the top of
`copper-plugs/copper_plugs.py` for the full cross-section diagram.

Each plug end that abuts a tube has a **⌀[6.5 mm](TUBE_HOLE_D) half-circle
arch cutout** centered at x = 0, so the plug seats around the tube
without crushing it. `lower`, `middle`, and `upper` all arch at both
Z ends; `top` arches at the bottom Z end only (its top is flush with
the wall top and stays flat).

The top plug's flat top face reaches the wall top, so nothing is left
open above the stack. After the four plugs are installed, the slot's
remaining unfilled length within the wall along Z — the strip below
the lowest copper, plus the narrow clearance bands around each of the
four tubes — gets filled by the body foam pour.

## Assembly and foam pour

Production-procedure framing at [`/hardware/assembly/cold-core.md`](/hardware/assembly/cold-core.md). The geometry detail below is the source-of-truth for the shells and the pour paths; the assembly doc is the production-cadence wrapper that places this pour in the appliance build sequence.

The cold core is foam-filled in **three pour operations** — one per cap
(each a self-contained cup + lid pour, done in parallel on the bench) and
the body pour into the shell's open +Z top.

### Body pour (after all body-side assembly)

Every internal component is installed first:

- Pressure vessel lowered into the centerward arc envelope, seated
  on the `tank_support_ring`, its PP0308E CO2 elbow already made up
  on the bottom-plate elbow and riding down the ring's +Y notch.
- Copper evaporator coil hand-wound around the vessel exterior and
  bonded with 3M 425 aluminum foil tape.
- Reservoirs installed into the two reservoir pockets.
- Copper evaporator inlet (low), copper evaporator outlet (high),
  water inlet, and PRV vent LLDPE (from the prv-shroud cap) routed
  through the shared −Y slot at their four Z heights. The water
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
  route it through the −Y slot to the appliance interior.
- Reservoir LLDPE lines routed through holes #1 and #2 in the
  reservoir-pocket far ±X walls.
- Water outlet through hole #4 in the outer_shell −Y wall.
- CO2 inlet enters from above through the foam-cap boss + cap-lid hole at
  (x=0, y=[+72.75](CO2_CAP_HOLE_Y)) — the top cap installs rotated 180°
  about Z, which is what brings its bore to this side. The line drops inside
  the cavity and bends 90° at the PP0308E push-to-connect elbow standing in
  the CO2 inlet notch at x = 0, cut inward from y = [+78.5](CO2_DOORWAY_Y).

With everything in place, liquid foam is poured **directly into the
body's open +Z top** all at once — no lid on, no down-channels.
Foam falls into the body and fills one connected volume: the
**surrounding foam zone** between the outer_shell and the pockets'
±Y walls (the front/back foam-pour gap; the ±X reservoir side has no
outboard foam, its reed channel butting the shell wall). This zone
reaches the centerward space around the tank+coil through the gap at
the pockets' ±Y ends (y = ±[72.5 mm](POCKET_Y_OUTER)), where the ±Y
walls stop and the centerward walls' transition arcs swing in to join
them.

The **two reservoir pockets take no foam.** Each is occupied by its
reservoir, which fills the pocket to [0.5 mm](RESERVOIR_GAP) on all
four sides and leaves the same clearance at the top under the pocket
wall top — the pour has no way in. The pocket interior stays an air
cavity, which is what lets the reed cable be threaded through it to
its −Y wall hole at final assembly, after the foam has cured
([`../reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)).
The reed channels are likewise open cavities and stay empty: their
columns drop in after cure.

The longest required traverse for the foam is around the back of the
coil at the ±X azimuths — the foam has to work through the embedded
helical wraps and fill the 15 mm blanket out to the centerward wall's
tank-side face, ~110 mm of arc to reach around from the ±Y entry.

Foam expansion may push a small amount of material out through the
clearance bands around tubes in the −Y slot and through the tight-fit
tube exits at the other penetrations. Trim flush after cure.

### Final assembly (after the body foam pour has cured)

Drop the pre-soldered reed columns into the still-open reed channels,
then seat a TPU gasket + the foam-filled top cap onto the body's top edge
with six M3 × 25 SHCS into the top-face inserts, and a second gasket + the
bottom cap (mouth-down) under the body with six more into the bottom-face
inserts. See the screw / insert spec under "Cap-to-outer-shell joinery"
above.

## Coincident-wall principle

Wherever two structural surfaces touch in the assembly, their walls
**overlap exactly in 3D space** — same outer face, same inner face.
After union, that boundary is one wall's worth of material (2 mm).

This drives several dimension choices:

- Each **reservoir pocket's ±Y outboard face** stands on the
  reservoir's own half-width (its flavor-charge dimension), not on the
  centerward-arc radius. Growing the cylinder's foam blanket slides the
  whole pocket outward without resizing or splaying the reservoir, so
  the ±Y walls keep their standalone width and meet the centerward
  wall's transition arcs there.
- The **tank_support_ring**'s outer face sits on the tank+coil envelope
  (`tank_coil_envelope_radius` = 70.5, the tank OD plus the coil radial
  clearance) — inboard of the pocket's centerward wall, which has moved
  outward with the foam blanket.
- Each **reservoir pocket's four walls** are traced as a single
  connected outer-perimeter polyline (with one cavity-perimeter
  polyline cut from it), so the four walls union into one solid by
  construction.
- The **outer_shell**'s inner face sits [16 mm](OUTER_GAP)
  outboard of the pocket's ±Y walls — the outer foam-pour zone. On the
  ±X (reservoir) side there is no outboard foam; the reservoir's reed
  channel butts the shell wall instead.

## Print settings

**Print with stock Bambu Studio defaults.**

Plate contents (when slicing): `foam-shell` + `copper-plug-lower` +
`copper-plug-middle` + `copper-plug-upper` together; the two `foam-cap`s +
their two lids on a separate plate (the TPU gaskets on their own TPU
plate).

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
| volume | [1035302.114 mm³](FSHELL_VOLUME) |
| bbox x | [-141.500 to 141.500 mm](FSHELL_BBOX_X) |
| bbox z | [0.000 to 213.400 mm](FSHELL_BBOX_Z) |
| bbox y | [-90.500 to 90.500 mm](FSHELL_BBOX_Y) |
| centroid | [(0.000006, 0.536168, 87.961389) mm](CENTROID) |

Quick reproduction:

```python
import cadquery as cq
s = cq.importers.importStep("foam-shell.step").val()
bb = s.BoundingBox()
com = s.Center()
print(s.Volume(), (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax), (com.x, com.z, com.y))
```

## Reference

- [`/hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py`](/hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py)
  — gold standard for the printed-enclosure pattern in this repo.

The cadquery venv lives at `tools/cad-venv/bin/python` (cadquery is not
on system Python).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/foam-shell/foam_shell.py`
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
