# Enclosure

What the pieces have actually been printed in, and at what settings:
[print-log.md](print-log.md).

A PETG box, 3 mm walls, **split into four printable pieces** — front/back ×
bottom/top, every piece inside the H2C bed — that telescope and screw together.
It measures [215 × 462 × 358 mm](BOX_SIZE), and **width, height and the back wall
are all stated bounds**. `_dims` measures the pack against each one and enters the
reading in `BOUNDS`; the box comes back at its stated size regardless, so a pack
that overruns one gets a wall drawn through it, a red row naming by how much, and a
clash in `pack-closes` at the body that overran.

- **Width** is `appliance_width`, struck symmetric about x = 0. What the pack owes
  it is clearance: a body on the floor slab spans the interior wall to wall, so a
  floor body stands one `side_band_inset` in from the wall **where it meets one of the
  seam's bosses in depth and in height**, leaving each mouth, plug and collar its full
  section. A boss is a pipe as tall as it is wide, so over and under one, as much as
  between two, the band is the wall's own air. The cold
  core is the widest of the floor bodies, yawed a quarter turn
  (`enclosure_assembly.FOAM_YAW`) so what crosses the machine is its 181 mm short face
  instead of its 283 mm long one. The yaw is the thin machine.
- **Height** is a stated [358 mm](APPLIANCE_HEIGHT), floor slab's underside to the
  top wall's outer face. The contents do not lift it; they have to fit under it.

**Depth** is stated at the back — `rear_plane_y` — and follows the pack at the
front, where the wall stands one `front_seam_clear` ahead of the frontmost body
placed by
[`../../../manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py).
The refrigeration stratum stands on the floor at the front and the cold core sits
behind it, front face mated flush against the stratum's aft plane.

Each column takes its bottom↔top seam at its own height, inside the band both its
pieces print in (`_bed_band`): the piece under a seam runs the floor slab to the lip
rim, the piece over it the seam to the top wall, and both stand on the bed.

The FRONT column's seam is a **stated** plane, `enclosure.front_z_seam` — which
pieces the box comes apart into is a decision about the pieces, and this one stands
over the refrigeration stratum's crown, so the compressor and the condenser
beside it are one piece's whole cargo and the front-top piece carries nothing on the
floor.

The BACK column's is **searched** instead. A searched seam wants the box's own
half-height — the split that leaves both pieces their best chance on the bed — and
takes the nearest height in an **open band** of its column: a range with
`z_joint_clear` of air on either side of it, read off the pack (`_z_joints`). There no
body straddles the seam and neither does whatever holds it, and a body standing clear
above one is a body the seam passes under. This column has no such band inside the
bed's: the cold core stands from the floor slab and the whole service bay stands on
its lid, so the column runs solid to the bay's crown and what it leaves open is above
all of it. So that seam runs **through** its column, on the lane its lip needs — a
one-`wall` ring inset from the cavity, held open at every height by the standoffs the
pack is packed to, one wall off the front and back walls and one boss chain off the
sides, which `_lip_denied` measures. The four station collars ride with that ring, in
the ±X boss-chain bands its own side segments run down, so a seam height carries the
lip and the collars together. The cold core spans that
seam, as it spans the front column's on the other side of the Y joint.

The two stand `z_joint_pitch` apart — closer and the Y seam quietly comes out with
fewer cross-pins than it has levels for — so the back column's search runs around the
front's stated plane, and the `z-seam-pitch` gate reds when every height it has is
inside that pitch. The pitch is what gives way there and the band is not: the seam
still lands, in its own open band. They land
far apart, which is why they stagger like a brick bond. `main()` prints each seam, how
it landed, and the band the bed allowed it.

`enclosure.py` exports the four printable pieces (`enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`) plus
`enclosure.step` — the four as separate solids in assembled position, seams
intact (mirrors `faucet/touch-flo-shell`).

## Seams + bosses

Three seams, one joint idiom. Front↔back: the front pieces' rear lip telescopes
into the back pieces, cross-pinned with M3 screws driven from the ±X exterior.
That **proud** lip is **3-sided** — both side walls and the ceiling. A proud
tongue is the wall continued one `wall` *into* the cavity, and on those faces the
cavity is free; the floor's is not — the cold core rides on it — so a proud floor
tongue would drive straight into the core. The floor laps anyway, but as a
**shiplap within the slab** (`_floor_lap`): the front floor's cavity-side half
runs one overlap aft, the back keeps its bed-side half and yields its cavity-side
half to receive it, so the slab reads unbroken across the seam with no
straight-through line and the core still seats on a flush floor. **Every seam
laps, none butts** — the form suited to the face.

The core spans this seam. It is one body running the box's whole depth, so it goes
in before the two halves close around it — which the standoffs are what make
possible: the lip's side segments pass in the ±X chain bands, its ceiling segment
under the top wall, and the floor's shiplap inside the slab, so none of the three
meets the core at all.

That seam runs the box's whole height, so it is pinned at **six levels** per side
wall, not once near the top — a wall above the floor, one under each Z seam, one
over each of their lip rims, and one under the ceiling, so every piece crossing
it is pinned at both ends of its own span. Because the Z seams stagger, a level
pairs whichever front and back piece meet at that height — the brick bond. That
ladder is also what sets the two Z seams' **offset**: `_bosses` drops a level
landing within two socket collars of one already placed, so seams too close
together silently cost the Y seam a fastener. The front seam's over-rim level and
the back seam's under-seam level are the pair that meet, and the offset holds them
a collar pitch apart.

Bottom↔top, per column: the same joint rotated 90°, at `z_joint_front` and
`z_joint_back` — the bottom pieces carry a 3-sided lip + socket collars, the top
pieces carry the pins, more X-axis screws crossing
each seam. The front pair joins, the back pair joins, then the front assembly
telescopes into the back as one.

A Z seam is pinned at **both ends of its column**, not just one, or the far end
hinges open. The front column takes the front-wall corner and the aft end of its
own lip; the back column takes one just behind the Y-seam mouth and one in the
rear-wall corner. Every station stands in the ±X band the walls' standoff opens
off the cold core, which runs clear the full depth, so none has to dodge the
pack.
Each cross-pin mates the walls of its overlap (the
pin's mouth-side face on the receiving mouth, the socket collar's rim-side face
on the lip rim) and the two are coaxial by construction, so the **overlap
depth is derived from those matings**, not chosen — it works out to
(plug + bore)/2 + one wall.

Each cross-pin is sized to its job. Reading an M3×10 screw outboard→inboard from
the ±X exterior: a Ø6.15 mm head counterbore, then the pin body (the screw spans
the head seat to the heat-set, so the body is screw length − heat-set long), then
the heat-set, then a one-wall cap.

- **Receiving piece = pin** (the back pieces on the Y seam, the top pieces on
  the Z seam): a Ø[9.9 mm](PLUG_DIA) cylinder (the shank + one wall each side, *not*
  the head — the head sits in the wall counterbore) from the exterior to the
  heat-set, registering in the socket bore.
- **Lip piece = socket** (the front pieces / the bottom pieces): a collar bored
  Ø[10.3 mm](SOCKET_BORE) to take the round pin as a slide fit, with the ruthex M3
  heat-set (Ø4.0 × 5.25) capped at its deep inboard end.

**Each boss stands on the joint it pins.** A plug is the wall it drives through and
the reach it needs past it: the first `wall` of its length *is* that wall's own
material and the rest a stub off it, its mouth-side face on the receiving mouth. A
socket is a **pipe round that plug** — Ø[16.3 mm](SOCKET_OD) outside,
Ø[10.3 mm](SOCKET_BORE) bored, one `wall` of material the whole way, a `socket_cap`
over the insert's blind end — its rim-side face on the lip rim and its far face a
hair inside the lip's own fusion shoulder, so it stands on the lip band down its
whole length. That band is one `wall` deep and runs the piece's full height, the way
a telescoping lip does. Those two matings are the pair the overlap depth is struck
from. Between two levels the corner is the wall's own air.

**What makes all of that fit is the band the walls keep.** A body standing on the
floor slab spans the interior wall to wall, so a body laid on a wall's face would
leave the seam machinery nowhere to stand. A **floor body is held one
`side_band_inset` in from the ±X walls where it meets one of the seam's bosses** — the
boss chain's own reach — and the **back wall keeps one `rear_seam_clear`**, the rear
Z-seam lip's own thickness. That is a requirement on the body where it meets one, not
a rule about the wall: each boss is a pipe at its own station and its own height, and
beside one — over or under one — the band is nothing but the wall's own air. Of the
three bodies on the slab only the cold core meets the chain; the compressor stands
under the front column's collars. Everything on the slab sits flat on it:
the print-corner relief runs on the standing verticals and the Y-seam's floor lap
stays inside the slab, so the seat is square and there is nothing standing there to
clear.

So the pack seats flush against the **seams**, not against the walls, and both
walls carry all six levels at full section.

The Y seam is a stated plane, `enclosure.y_seam`, checked against those bands
rather than derived from them: which pieces the box comes apart into is a decision
about the pieces — what each has to carry, and what a hand reaches when the front
assembly is off.

`rear_seam_clear` is the single source for the back wall: `enclosure_assembly` seats the
rear-wall bodies against it and `enclosure.py` builds the box to it, so the wall
the bulkheads mount through and the wall the box is built to cannot drift apart.

The crowding mechanism stays in place even though nothing is crowded now: each level
is offered only where the socket's whole body — bore, heat-set and cap, one collar
radius either side of the axis — stands clear of what `_measure_wall_block` found in
that corner, measured against the contents themselves rather than their bounding
boxes. It reads zero on both walls today, and the build prints each wall's levels so
a wall that ever loses one is visible rather than silent.

Each printed piece fits the H2C left-nozzle build envelope (325 × 320 × 320 mm)
even though the whole enclosure does not — that is the point of the split.

## Cold-core grips

The core is the heaviest body in the machine and the one with no hole in it — a foamed cup
under a screwed cap, plain skin the whole way round. What fastens it is the seams: **every
quadrant is screwed to the two beside it**, so a feature printed on one piece stands over a
body sitting in another, and the front-bottom, the back-bottom and the back-top close on the
core together.

Four features, two mirror pairs, and nothing on either that is not a face of the core:

- **Front corner blocks** (`_core_stops`, on `enclosure-front-bottom`). A block in each front
  corner of the slab, [38 mm](CORE_STOP_WIDE) across — the ±X wall inboard to one corner round
  past the tangent — and [40 mm](CORE_STOP_RISE) off the slab. **The pocket in it is the core's
  own plan outline offset one `split_slip`, not a shape of its own**: a Ø[24.4 mm](CORE_STOP_BORE)
  bore on the round's own axis outboard of the tangent, and the core's own flat front face
  inboard of it. So the block bears flat where the core is flat and round where it is round —
  the flat takes it forward, the round takes it across and in yaw, and the pair leaves it no
  lateral travel. The web ahead of that outline is [6 mm](CORE_STOP_WEB) at every point of it,
  including the tangent, where a bore alone leaves it thinnest. Underside on the slab, outboard
  face on the wall: a corner bracket in one piece with both faces it stands on, the card slot's
  own form.
- **Aft brackets** (`_core_holds`, on `enclosure-back-top`). A right trapezoid in section,
  [9 mm](CORE_HOLD_WIDE) wide: the bearing face along the cap from [12 mm](CORE_HOLD_REACH)
  forward of the core's aft face back to the wall, a leg [40 mm](CORE_HOLD_RISE) up that wall in
  the `rear_seam_clear` band, and one straight from the head of the leg down to the foot's tip,
  [8 mm](CORE_HOLD_LAND) over the crown. The foot lands on the cap — 0 by intent, the way every
  other seat in this box lands on the face it takes — and that straight is what makes the foot a
  flange on a web instead of a cantilever. The lane is the one strip of the aft crown clear of
  the water pump inboard, the power column outboard and the rear wall's two flavour unions in the
  band, taken on both flanks so the pair is a mirror.

The slab takes the weight and the back wall takes the aft, so the four between them close every
direction the core could go. `enclosure_assembly.check_core_held` reads each inside its own
window off the built pieces (`core-held`).

**The core enters the pocket from ahead or from above.** The pocket is that outline carried
straight down, so it stands clear of the core at every stand-off and closes on it at the slip:
the front assembly slides aft onto a core already down, or the core comes straight down into a
box already telescoped.

**Neither feature needs support.** The front blocks print floor-down with no overhang in them at
all. An aft bracket's leg stands up off the bed and its foot's bearing face is uppermost, and the
straight between them descends toward the tip at 25° off vertical, so every layer of the foot is
laid on the one above it.

## Print orientation + corner relief

Every piece prints on a **Z face** — the bottom pieces floor-down, the top
pieces ceiling-down, each lying on its closed face with its seam mouth up. The
build axis is therefore Z, and the anti-warp relief goes on the arrises that run
along it: the box's four **standing verticals**, rounded to match the foam
shell's 12 mm outer radius — concentric inner one wall in, so the wall is
preserved.

A quadrant owns only **two** of those four. Its other two "corners" are the
Y-seam — a telescoping mating face, with no exterior arris there to relieve
(the side walls run straight through the seam). So the front pieces round the
front-left and front-right verticals, the back pieces the back-left and
back-right, and **every seam edge stays 90°**. Assembled, all four verticals
read as relieved, each sourced from a different quadrant. The horizontal
front-to-back arrises — side-wall↔floor and side-wall↔ceiling — are square.

The display facet raises no fifth standing vertical: running wall to wall, it ends
on the ±X exterior walls and runs out into their own rounds.

The seam furniture follows the same rule: the Z-seam lip is a *horizontal* band
that telescopes straight through those verticals, so its corners are relieved on
Z concentric with the cavity it enters, and a socket collar standing in one of them
is held inside that same cavity; the Y-seam lip sits mid-wall where there is no
vertical arris, so it stays square.

The Y-seam lip is the one joint the orientation costs something. Its ceiling
tongue juts one overlap past the body into the space the back piece's ceiling
occupies — a cantilever that cannot be buttressed without colliding with the back
piece, and so wants print support. The floor **shiplap** costs the same, on the
half that reaches: the front floor's cavity-side tongue runs one overlap aft over
open air (the back's bed-side half fills under it only once assembled), so it
prints on a thin support strip at the seam, the ceiling tongue's twin one slab
down. The side-wall segments, vertical to the bed, are free.

The **drip tray's sleeve** in the back-top piece costs the same, and it is the
first of three features in the box that do. The sleeve is a solid block off the −X wall
running east on the withdrawal axis, and the rim rebate cut through it leaves a flat
ceiling down either flank — the lid the tray's flange runs under, held at one height
for the block's whole length, so it cannot be reached at 45° from the wall it grows out
of. Its floor is the same case one storey down, and wider: a slab the tray's whole
footprint, hanging off that wall. Ceiling-down neither turns into a face that can be
laid on air, and what stands over the lid is the vent gap (`drip_pan.VENT_GAP`), which
is air by construction. So the sleeve prints on support, one block 53 mm deep by the
tray's rim plus a wall either way, in the band above the tray's slot.

The **tap-water cradle** one storey above it costs the same. Its two 60° flanks
stand 30° off vertical and are free; its **top face is flat**, a soffit off the wall
over the lane, and that face hangs. The strap's cavity behind the trough is one
opening the trough's whole length, and the support in it draws out end to end.

The **pump trays** off the front wall are the third. A tray's plate goes down on the
bed first and its socket's octagon walls grow off the underside, so the socket itself
has no overhang in it; the plate is a soffit over the lane its pump hangs in, anchored
along its whole width where it meets the wall and bridging out from there.

## Tap-water cradle

A stepped trough on the −X wall that the ASSE 1022 chain lies in
(`_asse_cradle`). The chain is five fittings made up by hand on one axis, so
neither the run's length nor the clock any one fitting lands at is a number this
wall can know — but the **section** each one presents about that axis is the
fitting's own. The trough is cut to each in turn, and the steps between sections
fall out as faces square to the axis.

| section | across | seated on |
|---|---|---|
| PI4512F6S swivel nut | 22.0 | its circumscribed circle — the nut spins on the body |
| Multiplex hex barrel | 33.0 | its own two flats |
| GAGIRA coupling | 25.67 | its circumscribed circle — its clock is wherever the thread stopped |

The two end sections are there to make the barrel's steps and for nothing else, so
each runs the **shorter of the two fittings' lengths** rather than its own: the
coupling is more than twice the nut, and trough past a section already seated is PETG
paid for in the deck's own headroom. The flanks reach under the axis exactly as far as
the chain's own lowest arris — the barrel's apothem, `asse_reach_down` — and no
further, for the same reason.

Every section is the **same 120° V** and only its apex moves. A V of that angle is
the two flanks of a hex read off its corner, and it is equally the tangent seat of
any circle — so the section that sits deepest in the wall is the section that is
widest, and the barrel steps down out of both its neighbours rather than out of a
number chosen here.

**Only the barrel's V is read off flats, and only the barrel's may.** The other two
spin: a V cut to their flats would demand an angle the assembly does not control and
bind on the build that landed 30° off. The Multiplex's hex does not spin — its
atmospheric vent is machined into it — so keying that one section is what holds the
drip over the tray, and it is the whole reason this is a trough and not a strap.

`asse_seat_slip` is the fit across the V and `ASSE_STEP_SLIP` the play along it, the
deeper section taking the latter past both its ends so the barrel drops in and the
steps stop it travelling rather than hold it still. Aft it needs neither: the chain's
inlet collet butts the tap-water union's, and that joint takes the length up.

Two **zip ties** shut the trough's mouth, one in each band the vent leaves clear on
the barrel — the brass, which is the only section a tie may close on.

Both run in **one cavity through the trough's back** (`asse_tie_*`), closed on every
side but its two mouths and spanning the trough's whole length. It is **straight on
the west and the trough's own V on the east**, so it is narrowest at the axis and
flares to both mouths: each mouth opens `asse_tie_back / sin 60°` off its lip's own
arris, on the block's face where a hand reaches it, and at the axis the flare leaves
a strap pushed through the room to turn the vertex by cutting its corner. It stands
one `wall` west of the apex at every station, struck on the deepest section's apex so
the web is no thinner than that anywhere, and one `wall` off the side wall behind it —
so its width is a remainder between the two rather than a number.

A tie is a closed loop, so its strap also has to cross the chain's top flat — and
**the top wall is never cut for it.** The storey the chain lies on is struck to leave
that channel instead (`enclosure_assembly.DECK_CEILING_CLEAR`, the strap's own section
plus its clearance), so `wall` stays whole across the whole ceiling and the deck pays
the millimetre out of its own headroom. That leg is **laid, not pulled**: this piece
prints ceiling-down and is populated the same way up, so the strap lies on the
ceiling's inner face and the chain comes down onto it.

Nothing about the chain's weight is theirs: cut both and it still lies where it lies. `enclosure_assembly.check_asse_seated` is the row that reads the trough
closed on the barrel, measured off the two placed solids, because every other
reading on the card is satisfied by a chain floating in air.

## Flow-meter saddles

Two saddles off the **top wall**, one over each of the DIGITEN meter's collet
barrels, and nothing over the round body between them (`_digiten_saddles`).

The meter is a ⌀26 body with a ⌀12 barrel out of each rim. The body reaches to
within a hair of the top wall's inner face; the barrels leave the best part of a
centimetre under it. So the arms are what a printed feature reaches here, and each
takes a **bore concentric with its barrel** — half a cylinder at `seat_r`, opening
down, so the seat and the barrel share a surface all the way round instead of
touching on the two lines a V gives. The barrel comes straight up into it.

**The arc stops on the barrel's own axis plane, and the rib carries one
`digiten_saddle_wall` past that.** The axis plane is where the arc is widest, so
each lip comes out a **flat 3.000 mm strip**. Carried any further round, the arc
runs out to nothing against the flank and leaves a feather.

Each saddle runs the middle of its barrel: one `DIGITEN_BODY_CLEAR` off the body's
rim, and clear of the outer `DIGITEN_COLLET_FREE`, which is the push-fit ring the
tube comes back out of. The rib's length is its cavity's — `tie_cav_w` of strap and
buffer with `tie_cav_wall` of itself at each end, centred in the band the barrel
allows.

**The straps are the load path here.** A seat that opens downward carries nothing, so
unlike the trough's two ties these hold the meter up — a purchased part of a few tens
of grams on two nylon straps. `enclosure_assembly.check_digiten_seated` reads the
seats closed on the barrels at the slip itself, there being no angle in a bore to
divide by; travel off the placed pack is 0.231 up into them, 0.400 either way across,
and free downward.

Each saddle's strap runs a cavity over its bore, and **nothing is cut for it.** The
rib is one box its whole length up to one `wall` over the bore's crown, its two ends
carried on up to the top wall, and one bore through all of it — so the channel is the
length the ends do not span. It has no floor of its own to draw and no cut to make it.
On the built piece: seat R 6.2 crowning at 342.411, channel floor flat at 345.411,
and 6.589 mm of it under the wall.

**The rib is unified before it joins the wall.** A fuse imprints the seam of every
solid that went into it, so a rib fused straight on carries its lip in as many pieces
as it was laid down in. Cleaned first, the built piece reads one cylindrical seat face
9.50 long, one channel floor of 64.40 mm², and each lip **one 9.500 edge**.

Printed ceiling-down there is **no overhang in this feature at all** — the rib stands
up off the bed, its flanks are vertical, and the bore's crown is the deepest thing in
it, facing up the whole way round. Nothing in it needs support and nothing has to be
picked out of it.

## Tube anchors

One pattern wherever a wall comes near enough to reach something round
(`_tube_anchors`): a **bore concentric with the body**, half a cylinder at
`seat_r`, and the strap's channel behind it. Three of these hold a length of tube
(`enclosure_assembly.TUBE_ANCHOR_SITES`) and one holds a fitting
(`enclosure_assembly.BODY_ANCHOR_SITES`) — the same rib either way, since what the
builder is handed is an axis, a direction along it and a radius.

**The arc stops on the body's own axis plane and the rib carries one `wall` past
it**, so each lip is a flat strip rather than a feather — the saddles' bargain,
on the one body this machine has twenty of. The rib's length is its cavity's:
`tie_cav_w` of strap and buffer with `tie_cav_wall` of itself at each end. It states
no height of its own — it is handed the body, and the wall it stands on is where it
stops.

**The strap's channel is what is never fused.** The rib is one box its whole length
up to one `wall` over the bore's crown, its two ends carried on up to the face it
roots on, and one bore through all of it — so the channel has no floor to draw and no
cut to make it, and the face the rib roots on is its roof. A strap therefore goes in
**before** the body does.

**The regulator's rib** is the one bored for a fitting. The WR1110 lies fore and aft
on the panel deck one column east of the carb union, and the section under the rib is
the **⌀19 barrel between its two wrench hexes** — the two hexes stand on made-up NPT
threads, so where their flats come to rest is wherever the thread stopped, while the
barrel is the same circle whatever the makeup did. The rib is 9.500 long inside a
27 mm barrel, so it reaches neither hex.

On the built piece: one cylindrical seat face at R 9.700 crowning at 345.911, both
end walls filled 100% from the channel's floor at 348.911 to the top wall's inner
face, the channel between them a true void 3.089 deep, the web under the bore filled
100%, and each lip **one 9.500 edge** on a flat 3.000 strip of 28.5 mm². Travel off
the placed pack is 0.199 either way across, 0.197 up into the seat, and free
downward — the mouth the strap shuts.

**The strap is the load path here**, the same bargain the meter's saddles make: a
seat that opens downward carries nothing. Barrel and rib make an [84.1 mm](LOOP_WR1110)
loop, past what a 4" tie closes, so this one takes the 6".
`enclosure_assembly.check_body_seated` reads the seat closed on the barrel at the slip
itself, and `check_tube_seated` reads the three run anchors the same way.

## Pump trays

The front wall carries one per Kamoer (`_pump_trays`, off
`enclosure_assembly.pump_tray_stations`), and it is **the two-piece pump case with its
cylinder cut off**. `printed-parts/flavor/pump-case/` draws that case; its base is a
plate on the head's crown, a 45° ramp off the plate, an octagon bore wall standing in
the ramp, and a cylindrical tower over the bore. Cut the tower off above the bore and
cut down to one shoulder over it, and the four surfaces that were fitted on the part
are the four that hold it. `printed-parts/enclosure/pump-tray/` owns what the cut adds.

**It wraps two storeys of the pump, and that is why it is a case and not a plate.** The
base plate lands on the head's own crown and wraps its top edge; the bore wall takes
the boss on each of its eight faces and both its ledges, over the boss's whole depth;
and the shoulder the cut tower leaves lands on the boss's crown and wraps that edge
too. No plate reaches both — they stand a bore's depth apart. The can rises out of the
tower's own bore and the tray never touches it.

**The bore is the whole of the location.** A pump is held in X, in Y and in yaw by the
octagon alone; nothing about where one sits is a number this wall chose. Plate on the
head's crown, shoulder on the boss's, bore on the boss's flanks — each a plane or a
shared wall, so a tray and the pump it takes share no volume.

**The straps are the load path**, the meter's bargain again and on the heaviest body
either wall carries: a pump hangs UNDER its tray, so the tray on its own holds nothing.
**Two** close round the plate and the pump's own stamped mounting bracket — the steel
plate at the head-to-motor junction, which stands proud of the head all the way round
in the very plane the tray's plate lands on. `kamoer_kphm400` states that bracket and
draws none of it; a strap here reaches under its lip rather than round the head, so the
loop is a bracket wide and the 8" tie the tap-water trough takes closes it.

**The four channels stand in two bands, one either side of the can.** They sit outside
the head, so each run crosses the shoulder's own face: inboard of the can's radius a
run lies against the can, and outboard of the bracket's half-width its legs come down
off the lip they reach under. Unlike every other cavity on this box the channels are
**cut**, because there is no pair of end walls in a plate for a channel to be the gap
between.

**A tray is a cantilever off the front wall and nothing else, so `_tray_webs` closes
what it leaves.** One web to each side wall, one between the two trays, and one aft
onto the valve panel standing behind them — each the trays' own plate thick and in that
plate's own band, so the storey comes out **one plate wall to wall** rather than two
tongues in air. None of the four is a typed span: the three across are the remainder
between the interior faces and the flanks the trays already have, and the aft one reads
the panel's own near face, taking the nearest panel plate that crosses this band and
leaving the aft deck's to its own storey.

Printed ceiling-down the plate goes on the bed first and everything over it — ramp,
bore wall, shoulder — grows off its underside, so the only face that hangs is the
plate's own. It is a soffit over the lane its pump hangs in and takes print support,
the way the tap-water trough's block does.
`enclosure_assembly.check_trays_hold` reads each pump against the tray on it.

## Display housing

A flat 45° facet chamfers the **whole top-front arris**, wall to wall, and carries
the [Waveshare ESP32-S3-Touch-LCD-4.3B config display](/hardware/reference/waveshare-43b-display/)
facing up-and-forward (−Y front / +Z up) toward the standing user. The display is
**centred** on it: the box is 223 mm wide and the glass 113.5, so what is left is
roughly 55 mm of flat 45° face either side of the window.

Spending the whole width on it costs nothing — the chamfer is inside the box's own
silhouette, so that corner is unpackable at any width — and the geometry gets
simpler for it. There is no end wall closing a recess, no shoulder where a window
stops, and no bed relief on the arris a shoulder would raise. The window's lateral
size is the box's; `display_facet_x` is what the *glass plus its buffer* needs —
[157.3 mm](DISPLAY_FACET_X) × [86.8 mm](DISPLAY_FACET_SLOPE) up the slope — which is
what `main()` prints beside the measured face.

The facet is thickened into a 19 mm housing (the display's overall depth) with
the display let in. The glass is the datum: a shallow 2 mm bezel counterbore,
centred on the box (corners rounded 2.5 mm to match the glass), recesses the
glass with the 3 mm buffer uniform all around. The glass overhangs the body
unevenly (further up-and-left), so the 106 × 69 mm PCB through-hole sits offset
the opposite way; where a socket collar sits behind the facet, the hole takes it
clean through.

The whole housing is cut into the box itself, flush with the front wall: the
facet chamfers the top-front corner away and the back plane stands one housing
depth behind it. Both are the housing's own 45° planes — the facet above, the back
plane as its soffit — so the frame holds one constant thickness through the
corner. The display reference is seated in the housing by
[`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py), on the same
`display_centre_x` the counterbore reads, so the housing and the part in it cannot
land on two different centres.

Ceiling-down the housing lies flat, and every one of its faces — the facet and
its back plane as the soffit — is 45° or vertical to the bed, so none of them is
an overhang.

## Hopper opening

One rectangular opening spans the top wall **directly behind the display
housing**, where the removable silicone funnel
([`../../zone-c/hopper-funnel/`](/hardware/printed-parts/zone-c/hopper-funnel/))
drops in — its straight chute press-fitting the opening, its whole floor one
ramp falling to the centred spout, its flat brim resting on the wall frame left
around the cut.

The funnel is a static placed part: the opening is cut at its collar
(`_hopper_hole` reads the funnel's own dims at `enclosure_assembly.funnel_centre()`), so
funnel and hole cannot drift apart. The frame that cut leaves is bounded by the
facet's own back plane ahead (the collar's front edge stands on it), the ±X
boss chains either side, and the back wall behind — and the collar is measured
one `brim_margin` inside it on all four sides at once, so a placement that crowds an
edge is a red row naming the edge and the margin it is short. That margin
is the brim's landing: it is wider than the flange's overhang, so a full
overhang's width of wall remains outboard of the brim edge the whole way around.

The basin stands on the box's own stated **`funnel_front_y`** and takes the top
wall's full width, because the facet in front of it spans the machine and there is
nothing beside it to leave room for. What fences that plane is under the drain
rather than over the brim: the union on the spout stands in the window between
`_lines.CROSS_Y`'s crossing and the cold core's front face, and neither wall of
that window rides the display. The ledge the facet leaves the throat is read back
as a bound on the frame above. The basin reaches aft for the plan area its
capacity needs — which puts it **across the Y seam**. Both halves take their share
of the cut and the collar bridges it; what the seam gives up there is its top-wall
lip over the hole's span, which the mouth shelf's own relief already accounts for.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ the four `enclosure-*.step` pieces + `enclosure.step`. Wall, seam, boss, and
facet constants are at the top of `enclosure.py`. Prints the facet size, the
cross-pin levels each side wall ended up with, each piece's envelope vs. the H2C
bed, every piece-pair's slip fit, and the cold-core clearance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
