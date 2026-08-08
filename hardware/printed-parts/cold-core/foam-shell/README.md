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
  bottom plate (CO2 inlet, water outlet). Both plates are clocked so the
  port pairs stand on the shell's **±Y** axis
  (`_cold_core_interface.vessel_port_offset`); the float rod's register, at
  right angles to each plate's own pair, is what holds the two together. Vessel assembled height = tube
  length = **[152.4 mm](TANK_H)**. Outer radius = **[63.5 mm](TANK_R)**.
- **Reservoir** — printed rigid PETG flavor reservoir, one per flavor,
  two per cold core. **Two mouths, and they never share one.** The FILL is a
  ⌀[6.5 mm](TUBE_HOLE_D) bore in the cap, opening into the headspace above the
  liquid; the DRAW is a PureSec bulkhead clamped through the floor's central
  trough, at the bottom of the wet V and the lowest drainable point in the
  cavity. Everything that enters has to cross the cavity to leave. The floor is
  a wet slope to that trough and carries a printed boss for the internal SS float
  rod. Body envelope: **[140 mm](RESERVOIR_W) wide (along Y)
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
  and below the tank. Each is clocked to the line it feeds, which is what lets
  a run leave straight. The bottom-plate CO2 port's elbow carries a
  **PP010822E 1/4" PTC × 1/4" NPT M adapter** on its outlet; that pair is made
  up on the vessel at the bench and hangs inboard of the support ring's bore,
  so it descends in open space as the vessel seats. Its collet faces the CO2
  bore at y = [-19.05](CO2_BORE_Y), and the 1/4" OD line arrives on that axis
  from the port lane — laid down the lane from the top cap before the cap goes
  on, not pushed in from outside.

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

**Both bottom-plate lines cross the ring at the 225° slot, and the ring is bored
nowhere.** The **CO2 inlet** takes a ⌀[6.5 mm](TUBE_HOLE_D) reach in from the
bottom plate's lane-side port at y = [-19.05](CO2_BORE_Y), z = [17](CO2_BORE_Z),
**leaning** across the shell's floor to land on the port lane under the top cap's
`co2-in` conduit. The line falls the shell's whole height down that lane, and an
axis struck on the shell's centreline would end 7 mm from the ring's own face —
less than the corner takes, so the tube would have to finish bending inside the
reach. Struck on the conduit's column instead, the fall lands on the axis itself:
one corner out in the open, then straight in. The **carbonated-water outlet**
crosses the same slot on the column its own cap conduit stands over, one storey
above the CO2, leaning up as it goes.

Neither notches a bearing segment and all four stay whole.
`_port_cuts.ring_crossing_azimuths` measures the water outlet's crossing against
`ring_slot_spans` every build, so moving either the column or the ring fails
rather than drifts.

### outer_shell

Outer rectangular cup framing the whole foam-shell: floor + four
perimeter walls + six ⌀[8 mm](BOSS_D) cylindrical bosses. Total height
matches the foam-shell outer height of [213.4 mm](OUTER_H).
Outer footprint [283 mm](OUTER_X) × [181](FSHELL_OUTER_Y). The **short** axis is
the one that matters to the appliance: the foam assembly is yawed a quarter turn
in the enclosure, so 181 is what sets the machine's width and the ±X faces are
its front and back. The outboard foam-pour gap is split by direction: the ±Y
faces leave [16 mm](OUTER_GAP) of foam-pour zone between the outer_shell's inner
face and the pocket's ±Y walls, while on the ±X side there is no outboard foam —
the reservoir's reed channel butts the outer shell wall. The 283 mm is held that
way: the reservoir, shifted outward by the cylinder's foam blanket, lands with
its reed channel against the shell wall, and the foam that would otherwise sit
outboard of the reed has moved to the cylinder side. Those two ±Y bands are what
every penetration travels along — see §Port lane.

The four vertical corners are rounded — the exterior wall is a true
[12 mm](CORNER_ROUND_R)-radius quarter-arc on the outer face, the inner
face concentric one wall-thickness inboard — so the warp-prone sharp
corner is gone and the corner boss is wrapped by a curved wall.

**Every one of the six bosses stands hard against a ±Y wall** — none in a
corner, and none on a ±X wall. Four sit over the reservoir pockets' own far
walls, near the ±X ends; two are mid-long-side, offset in X by
±[15 mm](MID_BOSS_OFFSET). Opposite signs at +Y vs −Y preserve 180°
rotational symmetry around the Z axis, which is what leaves the top cap free
to install either way round.

That is a placement rule the PORT LANE sets, not a preference. A boss seated
diagonally IN a corner — its cylinder tangent to the exterior arc, which is the
deepest seat available — reaches diagonally into the ±Y pour band, and closed the
one corner every front penetration has to travel through. Held against the wall
instead, all six reach exactly [8 mm](BOSS_D) in from its outer face and leave
the same clear lane. See §Port lane.

Each boss is tied into the wall with the cylinder + corner-fill teardrop idiom of
the reservoir pocket-corner supports, so it fuses into the outer skin (one
wall-thickness of PETG over the insert) instead of meeting the wall on a
knife-edge seam. The four end bosses also get a web toward the ±X wall they stand
near, which stiffens that corner; every boss gets one toward its own ±Y wall.
Each carries a heat-set insert pocket at each end (drilled in from each face) —
twelve inserts total, six per face, for fastening the foam-cap stacks.

The outer **−X** wall carries every penetration that crosses a wall at all: a
Z-elongated slot on each of its two lanes and the two ⌀[6.5 mm](TUBE_HOLE_D) round bores of the
front port field, which are the reed cables'. **No fluid line crosses it** — this
face is mated flat against the refrigeration base, so a bore struck here opens
into that base rather than into the machine, and all seven leave by the top cap's
conduits instead. See Penetrations.

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

The `foam_cap_lid` is a [2 mm](FSHELL_WALL_T) plate matching the same outer
footprint, closing a cap's open mouth. It has the pour hole (Ø [20 mm](POUR_D))
and two vent holes (Ø [6 mm](LID_VENT_D)), and it carries a pad at each of the
six screw stations on its mouth-facing side — "The head sits in the lid" below.
It is the clamp for the pour and it stays: the lid ships bolted to its cap, and
its outer face is the plane the core stands on at the bottom and the water deck
and the electronics stand on at the top.

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

### The head sits in the lid

At each station the cap's boss column stops [3.2 mm](HEAD_PAD_H) short of the
cup's mouth, and the lid carries a pad of that same boss cross-section into the
relief — both trimmed to the one footprint, the relief a slip larger. The pad is
counterbored Ø[6.15 mm](HEAD_CBORE_D) from the lid's outer face and the
[3 mm](SCREW_HEAD_H) head drops into it, leaving one wall of PETG between the
head and the boss section it bears on. The outer face is a plane: the bottom
cap's is what the whole core stands on.

From under the head an M3 × [25](SCREW_LEN) crosses the land, the continuous
pad-and-column section, and the gasket, reaching [6.2 mm](SCREW_REACH) past the
shell's face — the whole [4 mm](INSERT_LEN) of the insert, with
[1.8 mm](TIP_CLEAR) of pocket under the tip. `_cold_core_interface.py` asserts
both ends of that.

## Penetrations

Twelve pass-throughs total — ten tube lines and two reed cables. Every tube is **1/4" OD
(6.35 mm)**, and where one crosses printed material the hole is ⌀[6.5 mm](TUBE_HOLE_D) for
a tight fit.

**THE CORE IS REACHED THROUGH ITS LID.** All seven fluid lines leave by the TOP, each up a
conduit through the foam cap and its lid (`_cold_core_interface.cap_conduits`), and the
service bay stands on the face they open on. What is left on the −X face — the one the
enclosure's quarter turn puts at the front of the machine, mated flat against the
refrigeration base — is the two reed cables on the front port field and the three
refrigeration-side lines in the two lane slots above it.

| # | Pass-through | Opening | Carries |
|---|---|---|---|
| 1 | Reed cable (+X) | own ⌀[6.5 mm](TUBE_HOLE_D) field bore | the reservoir-A level reeds' cable |
| 2 | Reed cable (−X) | own ⌀[6.5 mm](TUBE_HOLE_D) field bore | the reservoir-B level reeds' cable |
| 3 | Copper evaporator inlet | port-lane slot | 1/4" OD ACR copper, made up on the condenser's own outlet pick across the plane the two bodies share |
| 4 | Copper evaporator outlet | west-lane slot | 1/4" OD ACR copper, made up on the compressor shroud's own suction pick across that same plane |
| 5 | PRV vent | port-lane slot | 1/4" OD LLDPE from the prv-shroud cap into the appliance interior (unpressurized; carries relief-event discharge only — see [`/hardware/printed-parts/cold-core/prv-shroud/`](/hardware/printed-parts/cold-core/prv-shroud/)) |
| 6 | Water inlet | **top-cap conduit** `water-in` | from the diaphragm pump — down the forward strip, along the +Y band under the cap floor, into the top-plate Port 2 elbow **above the water line**, where it falls into the headspace against the CO2 back-pressure |
| 7 | Carbonated-water outlet | **top-cap conduit** `carb-water-out` | to the dispense faucet — off the bottom-plate Port 3 elbow **under the liquid**, across under the tank, out through the ring's 225° slot and up beside the coil |
| 8 | CO2 inlet | **top-cap conduit** `co2-in` | from the WR1110 regulator — the one line running DOWN: the port lane the shell's whole height, one corner, then the leaning bore through the ring onto Port 1, which feeds the **sparge stone below the liquid** |
| 9 | Reservoir A draw | **top-cap conduit** `reservoir-a` | off A's floor bulkhead at the **bottom of its wet V**, out the pocket's −Y wall, forward along the port lane's own floor, up the forward strip |
| 10 | Reservoir B draw | **top-cap conduit** `reservoir-b` | the same off B's floor bulkhead, out the pocket's +Y wall and forward along the west lane |
| 11 | Reservoir A fill | **top-cap conduit** `reservoir-a-fill` | straight down onto the fill bore in reservoir A's own cap, **above its liquid** |
| 12 | Reservoir B fill | **top-cap conduit** `reservoir-b-fill` | the same onto reservoir B's cap |

**Every vessel is filled high and drawn low** — the carbonator at its two plates, each
reservoir at its cap and its trough. Nothing that enters can leave without crossing the
vessel, which is what the air-purge and clean-flush service modes run on.

For the water inlet and CO2 inlet, the supply-side tubing reduces to
1/4" OD before reaching the shell — transition fittings (3/8"
barb-to-NPT adapter, 5/16" push-to-connect, 1/4" NPT check valves, etc.)
live on the warm side. Inside, every line is 1/4" OD.

### The runs themselves

[`_internal_routes.py`](/hardware/printed-parts/cold-core/_internal_routes.py) draws all
seven as swept solids on the tube's own centreline, and `foam_assembly.py` measures each
against the shell, the tank with its wrapped coil, and both reservoirs with their caps —
then lands them as `foam-assembly/internal-routes.step`. A line in here is a void's
occupant: it appears in no bounding box and collides with nothing, so drawing it is the
only way to know it fits.

Each run also reports the **arc it turns at**, found by drawing it at the stock's own bend
floor — `_routing.STOCKS`, the same bench-tested figure every run outside the core is
graded against — and stepping down until it stops meeting anything. That reading is the
corridor's answer, not a choice, and the last line of the report is the pack's short list.

Six of the seven turn at the stock arc, and two things buy that. Where a line crosses a
wall, **the wall gives way**: the opening is the line's own corridor rather than a circle
(`_port_cuts.cut_line_corridors`), so a draw comes about the moment it is through instead
of holding a bore's length of straight first. Where a line has to reach and rise at once
it **leans** — one diagonal in place of two square corners on a step's own width — which
is what the carbonated water does under the tank to cross the CO2, and again at the top to
put itself on its conduit's column.

`water-in` is the one left short. It comes off the top plate's elbow, has to travel
outboard of both pockets (each one is full of reservoir to within a pour clearance of the
cap's floor), and has to arrive back on its conduit's own station — and the whole of that
step is taken inside the band between the top plate and the cap. The step is wider than
the band is tall, so the two corners either end of it share a leg neither can have.

### Port lane

**Nothing reaches the −X face head-on.** The reservoir pockets fill both ±X ends
of the shell, so a line from the tank or from either pocket gets there along the
−Y pour band — the [16 mm](OUTER_GAP) strip that runs the shell's whole length
outboard of both pockets.

What a line may use of that band is the **lane**: the strip inboard of every
attachment boss, y [-82.5 to -72.5](LANE_Y) — [10 mm](LANE_W) wide, on
y = [-77.5](LANE_MID_Y). All six bosses stand hard against a ±Y wall and reach
[8 mm](BOSS_D) in from its outer face, so the lane is exactly what they leave, and
it runs clear from one corner round to the other at every height above the floor
slab. `foam_shell.py` measures both claims at every build and fails on either: the
lane holding material, or a station's bore not going through.

Approaching a ±X wall the corner rounds' inner arcs — concentric one wall inboard
of the exterior ones — bulge into the lane's outboard edge and pinch it to about a
bore's width at the very corner. That is not an obstruction: it is the material
each station's bore is cut through.

The lane is **one bore wide**, which is what makes the front port field a column
rather than a grid.

### Front port field

Two round bores, one per reed cable, stacked up the lane on one Y at a pitch of one
bore plus one wall:

[reed-cable-a 6.75, reed-cable-b 14.75](FIELD_Z)

A station's Z is **not** the height of the fitting it serves. A cable leaves its
pocket, turns onto the lane and climbs it, so the field is ordered by what leaves
together — and both cables leave the pockets' bulkhead band together. Above the field
this lane's slot takes the rest of the column, and `copper_plugs.evap_cross_z` is
derived from where the field ends — so adding a station pushes the slot up rather
than colliding with it, and dropping one brings the slot down.

**Three fluid lines use this lane and none of them crosses this wall:** reservoir A's
draw runs forward along the lane's own floor at the bulkhead band, under everything;
the CO2 falls the lane's whole height and turns in at the plate band above it; the
carbonated water joins only once the tank's top plate is under it. The lane is one bore
wide, so what keeps those three apart is the storey each takes, and
`_internal_routes.report_routes` is what proves it. Above the shell,
`cap_conduit_pair_neck` holds the two columns in this lane apart.

### Two-bore front pass-throughs

Each reed cable crosses its bag-pocket wall and then the −X wall, and the two bores
share neither an axis nor a height. The pocket-wall bore sits outboard of the bulkhead
axis at x = ±[109 mm](CABLE_POCKET_X); reservoir A's draw comes about on the station
inboard of it at x = ±[97 mm](FLAVOR_POCKET_X), and that step is what the cable costs.
Both cross at the elbow's own exit Z. The cable's front bore is its station on the field,
and between the two the run turns onto the lane and climbs to it — the lane is what lets
them sit at different X *and* different Z.

The cable's crossing is a round bore because a cable is limp. A DRAW's is not: it is that
line's own corridor through the wall, which is a longer opening in x and the same tight
fit round the tube (`_port_cuts.cut_line_corridors`). Only two bodies in the shell give
way to a line that way — a bag pocket's ±Y wall and the pocket corner posts — and every
other thing a line meets stops it.

A shaped hole has no diameter to check, so the LAND between it and its neighbour in the
same wall is measured instead: `foam_shell.py` reads both openings out of the walls
themselves at every build and fails under one wall thickness. A route that moves changes
the hole's shape, and this is what keeps it from walking into the cable's.

Both cables run through the open pocket space under the reservoir's raised floor, are
threaded after the pour has cured, and are potted nowhere.
`cut_pour_band_pass_through` in `_cold_core_interface.py` cuts each pair.

### The two lane slots and their copper plug stacks

The −X outer_shell wall carries a **Z-elongated slot** on each of its two lanes, and
between them they take three pass-throughs above the front port field: the two copper
evaporator lines and the PRV vent. Each slot is
⌀[6.5 mm](TUBE_HOLE_D) wide (rounded ends along Z) and both are cut by
`cut_lane_slots` in `_port_cuts.py`. A slot's
top extends past the wall top so no sliver of wall material remains
above it — the plugs slide down into the slot from
above during assembly. With the centerward wall extending only to
y = ±[72.5 mm](POCKET_Y_OUTER) (where it meets the ±Y walls via the
transition arcs), each slot pierces only this one outer wall.

**There are two because the refrigeration base is two bodies.** This wall is mated face
to face with that base: the condenser stands against the port lane's face and the
compressor's shroud against the west lane's. So the evaporator's two coppers leave by
opposite lanes, each on the pick the body behind it already carries, and neither joint is
a length of tube. A slot rather than a bore is the coil's doing either way — a tail formed
off a coil that is lowered into the cavity travels *down* the wall to its station rather
than being threaded through it.

Both the slots and the plug stacks that fill them are authored in the **port frame** —
the frame where the wall a port crosses is a −Y wall and the slot runs lateral in
x — and `_cold_core_interface.port_to_shell` is the one transform that carries that
frame onto a lane. A pose turned by hand alongside a slot cut by hand is two
implementations of one transform; this way the plug and the hole it plugs cannot
land in two places. One frame serves both lanes, so a plug drawn there fits either.

Pass-through Z heights (centers, absolute in the model — the floor occupies
z = 0 to z = [2 mm](FSHELL_WALL_T), so subtract that for a height above the
cavity floor):

[port-lane evap-inlet 27.75, prv-vent 35.75; west-lane evap-outlet 27.75](SLOT_Z)

The three continue the front port field at its own pitch rather than each crossing
where its own fitting sits: each line leaves its fitting, turns onto its lane and climbs
or drops it. The two coppers cross at one height because the lanes are one strip mirrored
and one coil's two tails reach either the same way. So the whole
of the shell's front face — field and slots together — is one band in the bottom
[35.75 mm](COLUMN_TOP) of a wall [213.4 mm](OUTER_H) tall, which is what lets a machine
packed against this face reach every port in one reach. `copper_plugs.py` derives
them.

Three printed PETG **copper plugs**, one per span, slide down into their own lane's slot
from above:

| Plug | Lane | Z span (mm) | Z end arches |
|---|---|---|---|
| `copper-plug-lower` | port | [27.75 → 35.75](PLUG_SPAN_LOWER) | both ends |
| `copper-plug-middle` | port | [35.75 → 213.4](PLUG_SPAN_MIDDLE) | bottom end only (top flat) |
| `copper-plug-top` | west | [27.75 → 213.4](PLUG_SPAN_TOP) | bottom end only (top flat) |

The spans meet end-to-end **at the pass-through centers**: each plug
runs from one tube's center to the next, and the arch cutout at each
end holds exactly half of that tube. A stack tiles its own slot from that lane's
lowest line to the wall top with no linear gaps — the tube is the gap.

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
without crushing it. A plug arches at the bottom Z end always, over the line its own
station carries, and at the top only where another station stands above it in the same
column — so `lower` arches at both ends and `middle` and `top`, each the last plug of its
column, arch at the bottom only and stay flat on top.

A column's last plug reaches the wall top with that flat face, so nothing is left
open above either stack. Once the three plugs are installed, what is left unfilled
in either slot along Z — the strip below that lane's lowest line, plus the narrow
clearance band around each tube — gets filled by the body foam pour.

## Assembly and foam pour

Production-procedure framing at [`/hardware/assembly/cold-core.md`](/hardware/assembly/cold-core.md). The geometry detail below is the source-of-truth for the shells and the pour paths; the assembly doc is the production-cadence wrapper that places this pour in the appliance build sequence.

The cold core is foam-filled in **three pour operations** — one per cap
(each a self-contained cup + lid pour, done in parallel on the bench) and
the body pour into the shell's open +Z top.

### Body pour (after all body-side assembly)

Every internal component is installed first:

- Pressure vessel lowered into the centerward arc envelope, seated
  on the `tank_support_ring`. Its four port elbows are already made up and clocked
  to the lines they feed — the bottom-plate CO2 elbow onto the leaning bore, the
  bottom-plate outlet elbow toward −X, the top-plate inlet elbow toward +Y — with
  the PP010822E collets on them hanging inboard of the ring, and the sparge stone
  and its silicone stub already inside.
- Copper evaporator coil hand-wound around the vessel exterior and
  bonded with 3M 425 aluminum foil tape.
- Reservoirs installed into the two reservoir pockets.
- Copper evaporator inlet and PRV vent LLDPE (from the prv-shroud cap) routed along the
  port lane and out through its slot; copper evaporator outlet routed along the WEST
  lane and out through that lane's own slot. Each leaves its fitting and turns onto its
  lane, and each of the two coppers lands on the pick of the body standing against its
  own lane's face — the condenser's outlet east, the compressor shroud's suction west.
- Water inlet: a 1/4" PTC × 1/4" NPT M adapter (JG PP010822E) made up on the
  lateral FNPT of the vessel's top-plate Port 2 elbow, collet turned into the
  +Y band, and a length of 1/4" OD LLDPE from that collet along the band between
  the top plate and the cap floor, forward, then into the forward strip and up
  the top cap's `water-in` conduit. Every corner on it is potted where it turns, and
  the two either end of the step into the strip are the pack's only ones under the
  stock arc — that band is 14 mm and the step across it is wider.
- Three copper plugs slid down into their own lane's slot from above (through
  the 10 mm open extension past the wall top) to seal between the
  pass-throughs — `lower` and `middle` on the port lane, `top` on the west.
- PRV shroud subassembly (`../prv-shroud/`) — already built and
  cured ahead of time, threaded into Port 4 at vessel install — is
  here as part of the vessel by the time the body pour happens.
  Press-fit a length of 1/4" OD LLDPE into the shroud's cap hole and
  route it along the port lane and out through its slot to the appliance interior.
- Reservoir A's draw off its floor bulkhead, out through the pocket's −Y wall
  inboard of the bulkhead axis — the opening there is the line's own corridor, so
  the tube turns as it crosses rather than after it — onto the port lane at the
  bulkhead band, then forward along the lane's own floor, under everything else
  standing in it, and up the forward strip to its conduit. Reservoir B's leaves by
  its pocket's +Y wall onto the west lane and comes forward to the same strip.
- Carbonated-water outlet off the bottom-plate Port 3 elbow, out to its own column
  on the +Y side of the plate's axis, then **leaning** −Y and up together out
  through the ring's 225° slot — over the CO2's run, which sweeps the same quadrant
  at the plate band, one tube and one hug clear where the two cross. From there it
  climbs beside the coil clear of the lane, and leans again at the top to put itself
  on its conduit's own column for the last stock arc.
- CO2 inlet on the plate's lane-side port at y = [-19.05](CO2_BORE_Y),
  z = [17](CO2_BORE_Z) — its leaning reach crosses the ring's 225° slot on that line
  and opens on the lane under the top cap's `co2-in` conduit. The line comes DOWN the
  lane from that conduit, turns once in the open and runs straight in onto the collet
  already made up under the plate.

All five fluid runs are laid **before the top cap goes on**, because every one of
them leaves by the lid and every one is potted where it turns.
[`_internal_routes.py`](/hardware/printed-parts/cold-core/_internal_routes.py) is
each run's drawn shape and the arc it turns at.

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
its pocket-wall hole at final assembly, after the foam has cured
([`../reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md)).
The reed channels are likewise open cavities and stay empty: their
columns drop in after cure.

The longest required traverse for the foam is around the back of the
coil at the ±X azimuths — the foam has to work through the embedded
helical wraps and fill the 15 mm blanket out to the centerward wall's
tank-side face, ~110 mm of arc to reach around from the ±Y entry.

Foam expansion may push a small amount of material out through the
clearance bands around tubes in the slot and through the tight-fit
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
`copper-plug-middle` + `copper-plug-top` together; the two `foam-cap`s +
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
| volume | [1040065.359 mm³](FSHELL_VOLUME) |
| bbox x | [-141.500 to 141.500 mm](FSHELL_BBOX_X) |
| bbox z | [-0.000 to 213.400 mm](FSHELL_BBOX_Z) |
| bbox y | [-90.500 to 90.500 mm](FSHELL_BBOX_Y) |
| centroid | [(0.725281, 0.484131, 87.634533) mm](CENTROID) |

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
