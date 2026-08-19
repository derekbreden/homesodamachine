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

Both columns take their bottom↔top seam on **one stated plane**, `enclosure.z_seam`,
inside the band both of a column's pieces print in (`_bed_band`): the piece under the
seam runs the floor slab to the lip rim, the piece over it the seam to the top wall,
and all four stand on the bed. The seam line runs level round the box, and the four
pieces meet at a four-way corner on each side wall.

Neither column leaves the plane an **open band** — a range with `z_joint_clear` of air
on either side of it, read off the pack, where no body straddles the seam and neither
does whatever holds one. The refrigeration stratum and the flavour deck run the front
column solid; the cold core stands from the floor slab and the whole service bay
stands on its lid in the back. So the seam runs **through** both columns, on the lane
each lip needs — the cavity's own one-`wall` skin (`_lip_band`, the same shape `_z_lip`
fuses onto a piece), held open at every height by the standoffs the pack is packed to,
one wall off the front and back walls and one boss chain off the sides. Being the skin
and not a box, it **wraps every column standing in a vertical**, and that wrap stands a
whole `column_round` inboard of any wall segment — so a body clear of all four walls
can still be in the lip's way there, as the PSU's aft corner is at the X+/Y+ column.
`_lip_denied` measures that lane per column, each seam answering for its own half of
the box (`z-seam-front-lane`, `z-seam-back-lane`). The four station collars ride with
that ring, in the ±X boss-chain bands its own side segments run down, so the seam
height carries the lip and the collars together. The cold core spans the seam in both
columns.

The plane stands where the seam's own machinery fits the pack: the seam ring's foot
over the condenser's fin crown, and the rim under the forward valve panel's
wall-to-wall span (`z-seam-under-deck` — a plate roots on a wall only above the rim;
its foot runs below, inset on the lip's own face). The ring's front segment across
the flat span is the bay's (`_front_flat_lip_drop`): the bay floor stands in that band
and the pump heads run down through it on their way out (`heads-sweep-out`), so the
flat front carries no lip there at any height.
`main()` prints each seam, how it landed, and the band the bed allowed it.

`enclosure.py` exports the four printable pieces (`enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`), the
`enclosure-pump-cartridge` that slides out of the front pair, and
`enclosure.step` — all of them as separate solids in assembled position, seams
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

That seam runs the box's whole height, so it is pinned at **[2](Y_LEVELS) levels** per
side wall — a wall above the floor and one under the ceiling — and at the
**four-corner screw** between them, so every piece crossing it is pinned at both ends
of its own span: the floor level pins the two bottom pieces, the ceiling level the two
tops, and the corner screw all four at once. `_bosses` drops a level landing within
two socket collars of one already placed, so the ladder carries one level per height
it is owed.

**The four-corner screw is the Y-boss idiom with the seam plane through it.** One M3×12
per side wall at the Y-boss station on `z_seam`, where all four pieces meet: the back
pair carries the plug as two half-cylinders — each piece its own half, the flat on the
plane, the bottom's at its rim and the top's flat-face-down on its own mouth — the
front lip's two halves carry the slide channel, and `enclosure-front-bottom` alone
carries the socket: a pedestal off its own lip face, proud through the plane the way
the lip itself is, so the bore and the heat-set live in one piece's solid. The
pedestal is a D below its axis, and a 45° web carries it to the lip face — collar,
fill and web meet on flats, and the piece prints floor-down with nothing hanging.
The Y seam's own collars keep the same shape: a D squared onto the slab at the floor
level, a D on its web with its crown squared into the ceiling at the top one
(`_front_socket`).
The head sits in the standard counterbore astride the visible seam line, and the screw
clamps back wall and front lip against the pedestal's shoulder — all four pieces in
one sandwich, the shank shear-locking them in Y and Z at the point. Its cap stands
`corner_core_reach` past the boss chain, in a slot the cold core's flanks carry for it
(`_cold_core_interface.corner_boss_slots`, read live by `corner-slot-lands`).

Bottom↔top, per column: the same joint rotated 90°, at `enclosure.z_seam` — the
bottom pieces carry the lip + socket collars, the top pieces carry the pins,
more X-axis screws crossing each seam. Front-bottom's lip runs its side walls
whole and gives its front-flat span to the bay (`_front_flat_lip_drop`): the front
Z-joint there is the corner columns' pillar telescopes and a butt at the seam. Where
the side lip runs on, front-top's **bay floor** channels for it and stands on the seam
mouth beside it (`bay-floor-bedded`). The front pair joins, the back pair joins, then
the front assembly telescopes into the back as one.

**A wall that lip stands on is `2 * wall` thick, floor slab to lip rim.** The lip is
the cavity's own one-`wall` skin standing proud of the interior face, and a skin that
began at the seam would land its underside in air: a one-`wall` soffit round three
sides of a piece that prints floor-down, with nothing under it to print on.
`_lip_underwall` carries that same skin from the shoulder down to the slab, so the
two fuse into one wall with no step in it and the bottom pieces come off the bed with
no bridge in them. What it spends is the cavity, one `wall` off three sides of each
bottom piece — which is what the pack already stands off them (`front_seam_clear`,
`rear_seam_clear`, `side_band_inset`), measured rather than assumed by
`wall-under-lip`. `lip_face_x` is the flank a body down there meets: the MQ-6's card
bottoms on it, the condenser's aft fin roots on it, and the compressor's suction lane
is struck from it.

A Z seam is pinned at **both ends of its column**, not just one, or the far end
hinges open. The front column takes the front-wall corner and the four-corner
screw; the back column takes the four-corner screw and the rear-wall corner.
Every station stands in the ±X band the walls' standoff opens off the cold
core, so none has to dodge the pack.
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
hair under the seam mouth, so it stands on that band down its
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
walls carry all [2](Y_LEVELS) levels at full section.

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

**The core enters the pocket from ahead.** The pocket is that outline carried straight
down, so it stands clear of the core at every stand-off and closes on it at the slip:
the core goes down into the open back tub, and the front assembly slides aft onto it —
the four-corner bosses riding the flank slots the core carries for them
(`corner-slot-lands`).

**The front blocks need no support**: they print floor-down with no overhang in them at all. **An
aft bracket's bearing face does.** The straight from the head of the leg out to the foot's tip
descends at 25° off vertical and is the bracket's upper face, laid on the section beneath it the
whole way out — but the bearing face under it is flat and is the lowest thing on the bracket, so
it is a soffit off the back wall and takes support, the way the tap-water trough on that same
wall does.

## Print orientation + corner relief

Every piece prints on its **Z− face** — the bottom pieces floor-down on the
floor slab, the top pieces mouth-down on the seam rim. One bed plane for all
four, read in the box's own frame: the build axis is **+Z** everywhere, so the
face that hangs is always the one looking **down**, and that is the side every
45° relief on this box is struck on. The anti-warp relief goes on the arrises
that run along the build axis: the box's four **standing verticals**, rounded to match the foam
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

Inside those verticals stand the **columns**, and each one is that relief
**mirrored** — congruent, which is what fixes it. The relief outside is a **quarter turn**
of [12 mm](COLUMN_ARC); a mirror is congruent or it is not a mirror, so the column's face is
a quarter turn of the same radius — the **same arc and the same length**. The only place such
a turn fits inside the cavity with its ends on the two inner faces is swung from the corner
they meet at, and that is the whole construction: one radius, one centre.

It lands on each face at 90°, so a standing vertical presents **two sharp corners** opposite
each other, [12 mm](COLUMN_ALONG) along each inner face, with the arc between them. The
section stands [8.27 mm](COLUMN_DEPTH) out of the cove at the corner's diagonal.

**The corner behind it is solid.** The face is the column's only free surface — a second arc
back there would leave a through slot the column's whole height — so the column is everything
within the radius and the wall keeps the rest. The cove the wall had turned stops being a
surface at all: what the room meets at a standing vertical is **one arc, congruent with the
one it meets outside**. All four verticals carry one (`enclosure.column_corners`), so each
quadrant prints the two its own two exterior arrises stand behind.

A wall's inner face is **flat only past that landing**, so anything BEARING on it answers to
`enclosure.wall_flat_from_corner` rather than to the relief's own tangent — the C14 inlet's
flange is the one that does.

A column is the cavity's own shape (`enclosure._cavity`), not a feature bolted into
it, so everything held inside the cavity meets one the way it meets a wall: the
Z-seam lip wraps its face and telescopes on it, a socket collar is clipped by it, and
anything standing inside its footprint is **absorbed** — the boss becomes the column's
own material and keeps only its bore.

Where what stands there is a **body** rather than a boss, the column is the one that gives:
`_dims` measures every placed body against every column and hands `build_piece` a pocket per
lump one actually reaches into (`Box.column_reliefs`), cut last of all and clipped to the
pillar so it can never take the wall behind it or the boss beside it. A column is a
print-corner feature — what it buys is a fat vertical on the bed, and it buys that over the
height it does have; a body hung on a wall has already answered to the boss that holds it and
to whatever the pack packed it against. Two corners are relieved today, and `main()` prints
every one so a hollowed column is never silent:

- **X+/Y-** — the condenser's two sheet flanges, at z 8.0–10.4 and 144.6–147.0. The pocket
  is nearly a no-op: those flanges already slide into a groove the cradle rail cuts through
  the same material, and the rail's east end and the lens print as one body.
- **X+/Y+** — the PSU's aft-east corner, over z 252.4–306.4, about a millimetre deep at its
  widest. The brick cannot give ground instead: its rear mount hole is on the aftmost boss
  station, the relay and the controller board are packed one `WIRED_CLEAR` at a time ahead of
  it, and the front of that stack stands ~1.3 mm off `carb-1`. What a column cannot absorb is a seam station:
the lens runs along the wall to its cusp and would be a leaf-shaped hole through a socket
collar's root, so a station landing there stands one collar radius clear of that cusp
instead and the collar comes out whole — the front column's front-wall station
(`enclosure._z_front_station_y`) and the back column's rear-wall one
(`enclosure._z_back_station_y`), which are the two seam ends that sit in a standing corner.

The rest of the seam furniture follows the orientation rule: the Z-seam lip is a
*horizontal* band that telescopes straight through those verticals, so it is struck as
the cavity's own one-wall skin — corners relieved on Z, columns wrapped — and a socket
collar standing in one of them is held inside that same cavity; the Y-seam lip sits
mid-wall where there is no vertical arris, so it stays square.

The Y-seam lip is the one joint the orientation costs something. Its ceiling
tongue juts one overlap past the body into the space the back piece's ceiling
occupies — a cantilever that cannot be buttressed without colliding with the back
piece, and so wants print support. The floor **shiplap** costs the same, on the
half that reaches: the front floor's cavity-side tongue runs one overlap aft over
open air (the back's bed-side half fills under it only once assembled), so it
prints on a thin support strip at the seam, the ceiling tongue's twin one slab
down. The side-wall segments, vertical to the bed, are free.

The **drip tray's sleeve** in the back-top piece costs the same, and it is the
first of two features in the box that do. The sleeve is a solid block off the −X wall
running east on the withdrawal axis, and the rim rebate cut through it leaves a flat
ceiling down either flank — the lid the tray's flange runs under, held at one height
for the block's whole length, so it cannot be reached at 45° from the wall it grows out
of. Its floor is the same case one storey down, and wider: a slab the tray's whole
footprint, hanging off that wall. Both look down, so neither turns into a face that can
be laid on air, and what stands over the lid is the vent gap (`drip_pan.VENT_GAP`), which
is air by construction. So the sleeve prints on support, one block 53 mm deep by the
tray's rim plus a wall either way, in the band above the tray's slot.

The **tap-water cradle** one storey above it costs the same. Its two 60° flanks
stand 30° off vertical and are free; its **underside is flat**, a soffit off the wall
under the lane, and that face hangs. The strap's cavity behind the trough is one
opening the trough's whole length, and the support in it draws out end to end.

The **bay floor** is the one feature that costs nothing and pays: it IS front-top's
first layers. Its underside is the seam mouth, the plane the piece beds on, so there is
no face under it to hang and no support in it to pick out. It is a solid slab across the
whole front storey: the cartridge slides across it, and the collet plate's foot sits in a
blind seat sunk in its top.

The **tee wall** behind that plate costs nothing standing up, and its four bores are the
only thing in it that could have hung. The piece beds on the seam plane, so a bore on Y
lies horizontal and its crown is the only face in the wall that could be laid on air.
Each is **teardropped** (`_tee_bore`): the roof is two 45° planes standing on the bore's
own tangent points, 45° being the steepest the arc itself reaches before it turns over,
so the hole is taken over from exactly where it stops being printable and nothing above
it is laid on air. The three lower quarters the collar bears on are untouched, and the
wall needs no support.

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
is populated inverted on the bench — ceiling down — so the strap lies on the
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

Printed Z−-down the rib **hangs off the top wall** and starts on its two lips — one
`digiten_saddle_wall` strip either side of the bore, the saddle's whole 9.50 length, with
nothing under them. Everything over those lips is the arc closing inward on itself, so
the hood carries its own crown, its flanks are vertical, and the lips are the only thing
in the feature support has to reach.

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

## The pump cartridge and its bay

**The pumps slide out of the front of the box.** The front wall's flat span — corner
column to corner column, sill to lintel — a **return** down each flank, and the storey
both pumps stand in come out of front-top as the **pump cartridge**
(`build_cartridge`): the face, the two returns, the block behind them, both trays and
both pumps, riding the bay's own floor.

**It is a block, and it parts on the pump's own bracket plane.** What the bay leaves
between the face and the collet plate is filled — sparse infill under a printed skin —
and the two Kamoers are voids in that fill. The split is `cap_split_z`, the head-to-boss
junction the tray's plate already lands on: over it the block is the cartridge and each
pump stands in the tray that bores its boss; under it the block is
**`enclosure-pump-cap`** (`build_pump_cap`), one piece closing on both heads. What
carries a pump is the stamped bracket it holds in that plane — `bracket_w` across
against a head of `head_w` — lapping the cap's top face all round the head's opening,
with two M3 on the lane between the pumps drawing the cap up onto the block
(`_cap_screws`). The motor cans open through the block's ceiling and each head's front
face through the cap's underside: the bay top stands `bay_crown_air` over the crowns and
the sill one millimetre under the faces, so what the block covers is what there is room
to cover. Nothing latches the cartridge. The four barb tubes
gripped in the anchor tees' branch collets are the retention, and the **collet plate**
is the release: a waterjet flat of 1/8" 304
(`enclosure_assembly.build_collet_plate`, `collet-plate.dxf`) standing one rest gap
fore of the four collets in the bay floor's own seat, four holes passing the tubes and
nothing wider. Pull the cartridge and the gripped tubes drag the tees forward, each tee
running in its own bore in the wall behind the steel and held across its collar while
free along its axis, until each collet's nose lands on the steel — the body keeps
coming, the nose is held, the grip opens, and the tubes draw out through the holes they
entered by. Push it home and the tubes thread back into the same collets, the cap's own
aft face landing on the plate's own fore face, the tees square in those same bores and
braced by the valves their runs butt into, each of those in a panel seat. One hand
pulls, the other braces the box; the box carries the brace to the steel through the
floor.

**THE STROKE IS READ, NOT ASSUMED.** `release-travel` offers every body the release moves
the whole stroke and reports what it hits — a motion, where every other bound on that card
reads where a body stands — and all eight clear it. A butted neighbour travels with the
body it butts, so the four valves butted to the anchor tees make the same stroke the
tees do: they all stand on one deck, and `_valve_panels` sets that plate's face a whole
stroke further fore and sinks its four sockets by the same figure, so a post keeps its grip
over the travel. The other deck's setback is zero and nothing about it moves. Its sibling
`check_insertion_backing` reads the other direction, where a tube pushed into a branch
collet drives its tee aft and the step in the wall's bore is what stops it.

**What lands on the steel is the cap's own aft face.** The cap's whole storey stands
under the plate's top, so the face it presents to the steel is the piece's own — nothing
hangs off anything to reach it — and `cap_kiss` is the air left at that face when the
cartridge is home. `pump-cap-stops-on-plate` reads the area standing against the plate's band
and that the kiss itself is air.

## The flank openings

**Both flanks open across the cartridge's own storey** (`_flank_opening`), and the corner
posts are the only thing left standing in them. A column here is the whole of the box's
corner — the side wall's own section, the front wall's, and the quarter-round between
them, one post. So the opening does not begin at the exterior: it begins where that post's
arc lands on the side wall's inner face, [12 mm](COLUMN_ALONG) aft of `front_plane_y`, and
runs from there to the collet plate.

**Its floor is the Z-seam rim.** Front-top's side wall under that plane is the outer
register front-bottom's lip telescopes into, so the opening begins where the lip ends and
the Z seam keeps its whole lip. The flat span's sill runs one `lip_len` lower because the
pump heads leave under it, and the two meet in a step at the post.

**The cartridge stays between the jambs.** It is the flat span and what stands behind it,
out to `bay_x_span` and no further at any height. The posts stand in this piece's own
withdrawal path, so nothing of it reaches their x, and the front of the box outboard of
the bay is theirs.

## The bay floor

**Front-top carries a floor across the bay** (`_bay_floor`), from the front wall's
interior face aft past the collet plate, and everything in this storey stands on it.
**It is this piece's first layers.** Front-top beds on the seam plane, so a floor
struck there lies on the bed with nothing under it to hang, and what sets its section
is the only thing over it: the cartridge reaches down to the plane its own pump
reliefs floor on, one millimetre under the heads, and the floor's top is that plane
(`bay_floor_z`). Sill, face reveal and head clearance are then one figure, not three.
`bay-floor-bedded` reads the floor's whole plan solid on the bed.

**One pocket per collar passes the Z seam** (`_z_seam_berth`), and nothing else does.
Front-bottom's side lip is given up over this whole run (`_flank_lip_drop`) — round both
front corners and back down each flank as far as the tee wall's aft face — so the floor
crosses it wall to wall instead of surrendering one `wall` at each flank. What still
stands over the mouth here is the front column's socket boss on its own plinth, and the
floor opens for that alone. Aft of that run the lip is carried whole and the telescope
is untouched.

The **collet plate's foot is sunk in a seat** cut one `wall` down the floor's top, so
the steel is located fore, aft and across by printed material and carried on the
seat's own bottom, and nothing over it is closed — with the cartridge out, the plate
lifts straight up through the bay. Its Z band follows from that: the bottom is the
seat, and the top is whatever puts the four collet holes **centred** in the band
(`plate-holes-centred`). Its two bottom corners are notched one `wall` in from each
end, from the foot up to the rim, for the side lip standing proud there — the outline
is a waterjet cut and `build_collet_plate` writes the notches into `collet-plate.dxf`
with the holes.

The **wall behind the steel is struck on the same four collets** (`_tee_wall`).
Front-top stands a section of its own material aft of the plate, wall to wall and the
whole height of the bay, with one bore per anchor tee. A bore closes on the round collar
that tee's branch arm carries — `TEE_WALL_BORE_SLIP` on the radius, a running fit and
not a grip — so a tee is located in X and Z by printed material and free in Y, which is
the one direction the release moves it. The wall's fore face IS the steel's aft face,
one figure with the plate (`enclosure_assembly.collet_plate_spec`), so every bore is
stopped at its fore mouth by steel and the nose that lands there lands on steel; the
plate bears back on the wall across its whole face. Its aft face stands one whole stroke
plus `TEE_WALL_BODY_AIR` fore of the tee's own body, so at full release there is still
air behind the tee — depth past that plane is the tee's and not the wall's to take. What
the wall holds is the collar, across the bore; what stops the tee is the steel.

**That wall is also the bay's back.** Over the plate's own band the steel closes the
bay; above and below it this wall does, so what stands behind the berth the cartridge
leaves is a wall rather than the cavity. The Z seam passes it the way it passes the
floor, on `_z_seam_berth`'s own channels.

The **bay** is the opening all that leaves through (`_bay_cut`): jamb to jamb between
the corner columns' cusps, from the floor's own top up past the motor cans' crowns
(`pump_bay`, struck off the placed cans), and both flanks over the rim. The flat span's
sill runs wall to wall, washed fore
so what runs down the face drains out (`_sill_wash`); the lintel over the opening
carries the facet and the display on a stated ligament (`bay-under-display`).
`heads-sweep-out` reads each head's path to the front against the piece it passes
through. Front-bottom's front lip drops across the whole flat span
(`_front_flat_lip_drop`) — the floor stands in that band and the heads run down through
it — and the front wall below keeps its single `front_wall` section from slab to seam.
The face rides its opening on stated air, `bay_face_slip` at the jambs and
`face_reveal` at the sill and lintel.

**The front wall is `front_wall` thick — a face a user hauls on — and grows inward,**
the exterior and the facet standing where the appliance's stated depth put them. What
noses into the section gets a 45°-chamfered relief (`_front_relief_cuts`): one stated
pocket across the compressor, floored on its own kiss, and one pocket per pump in the
cartridge's face, floored where the tray's own wrap rule puts its root
(`pump_relief_floor`). The compressor is the only body in the refrigeration stratum
standing fore of the wall's interior plane — the condenser bears on that plane through
its rails and the fuse clamp stands clear behind it — so the wall keeps its full section
across the rest of the front. `box-front` reads every placed body against the relieved
surface, region by region.

## Pump trays

The cartridge's deck carries one per Kamoer (rooted on the pump reliefs' floor, off
`enclosure_assembly.pump_tray_stations`), and it is **the two-piece pump case with its
cylinder cut off**. `pump-tray/pump_case.py` draws that case; its base is a
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

**A tray is a cantilever off the cartridge's face, and `_tray_webs`' own boxes close
the deck.** One web between the two trays and the across-runs to the deck's edges —
each the trays' own plate thick and in that plate's own band, cropped to the jambs'
sweep air, so the deck comes out **one plate** whose edge strips ride the bay's
rails. The webs to the side walls and the aft web onto a panel are not drawn here:
the rails standing on the floor carry the deck instead, and its aft edge stops two
millimetres short of the collet plate, and the cap's aft face one storey down is what lands on the steel.

Printed face-down the outer skin goes on the bed first, the deck and both flank
returns stand as walls off it, and every pocket rises as a plateau's absence. The one
hole in the piece is a flank grip, and its aft end is gabled at `relief_chamfer` so the
return's section is laid over it — nothing on the cartridge hangs.
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

Printed Z−-down the housing's two planes are the facet, facing up, and its back
plane as the soffit, facing down — both at 45° to the bed, which is the angle
everything else on this box is relieved to, so the soffit lays on itself and
neither takes support.

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
nothing beside it to leave room for. The frame's two side strips on the front top are
corbelled (`_ceiling_corbels`): a 45° underside off each ±X wall to nothing at the
opening's edge, and over the seam's ceiling tongue off the top collar's own chain
face, so the piece printing on its mouth lays every ceiling layer on the one below
it. THE HOPPER IS WHERE THE USER POURS, so that
plane stands as far forward as the wall lets it — which is the display housing's own
back cut — and what fences THAT is the brim rather than the throat: the flange
overhangs the collar and has to land on top wall, and the top wall begins at the
facet's own arris. `funnel-brim-lands` is the reading, and the ledge the facet
leaves the throat is read back as a bound on the frame above. The basin reaches aft for the plan area its
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
