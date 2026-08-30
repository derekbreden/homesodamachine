# Enclosure

What the pieces have actually been printed in, and at what settings:
[print-log.md](print-log.md).

A PET-GF15 box. [3 mm](WALL_T) is the section a piece starts from and every exterior
wall carries at least [6 mm](LIP_UNDERWALL), each taken INWARD so the silhouette
and `interior_x` both stand still: a bottom piece's three lipped sides get
[6 mm](LIP_UNDERWALL) as the lip's own skin carried to the slab, front-top's ±X
flanks are [9 mm](FRONT_TOP_FLANK), back-top's are [9 mm](BACK_TOP_FLANK) and its
+Y wall [6 mm](BACK_TOP_WALL). The floor is the one section taken OUTWARD:
[6 mm](FLOOR_T) of slab under both bottom pieces, with the stated height struck to
its underside, so it stands in the silhouette and the cavity's floor plane — the
one the pack sets its bodies on — does not move. **Split into four printable pieces** — front/back × bottom/top, every piece inside the H2C bed. Each
column's top SLIDES onto its bottom on hooked rails; the two halves telescope and four screws
close the whole box.
It measures [215 × 462 × 361 mm](BOX_SIZE), and **width, height and the +Y wall
are all stated bounds**. `_dims` measures the pack against each one and enters the
reading in `BOUNDS`; the box comes back at its stated size regardless, so a pack
that overruns one gets a wall drawn through it, a red row naming by how much, and a
clash in `pack-closes` at the body that overran.

- **Width** is `appliance_width`, struck symmetric about x = 0. What the pack owes
  it is clearance: a body on the floor slab spans the interior wall to wall, so a
  floor body stands one `side_band_inset` in from the wall **where it meets one of the
  seam's bosses in depth and in height**, leaving each mouth, plug and collar its full
  section. A boss is a block as tall as it is wide, so over and under one, as much as
  between two, the band is the wall's own air. The cold
  core is the widest of the floor bodies, yawed a quarter turn
  (`enclosure_assembly.FOAM_YAW`) so what crosses the machine is its 181 mm short face
  instead of its 283 mm long one. The yaw is the thin machine.
- **Height** is a stated [361 mm](APPLIANCE_HEIGHT), floor slab's underside to the
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
one wall off the front and +Y walls and one boss chain off the sides. Being the skin
and not a box, it **wraps every column standing in a vertical**, and that wrap stands a
whole `column_round` inboard of any wall segment — so a body clear of all four walls
can still be in the lip's way there, as the PSU's aft corner is at the X+/Y+ column.
`_lip_denied` measures that lane per column, each seam answering for its own half of
the box (`z-seam-front-lane`, `z-seam-back-lane`) — the ring read one rail deeper down
the straight runs, where the groove, arm and head ride. The cold core spans the
seam in both columns.

The plane stands where the seam's own machinery fits the pack: the seam ring's foot
over the condenser's fin crown, and the rim under the forward valve tray's
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
intact (mirrors `faucet/faucet-shell`).

## Seams + bosses

Three seams. Front↔back: the front pieces' rear lip telescopes
into the back pieces, cross-pinned with M3 screws driven from the ±X exterior — the box's
only four screws. That **proud** lip is **3-sided** — both side walls and the ceiling. A proud
tongue is the wall continued one `wall` *into* the cavity, and on those faces the
cavity is free; the floor's is not — the cold core rides on it — so a proud floor
tongue would drive straight into the core. The floor laps anyway, but as a
**full-thickness tongue with a 45° scarf nose inside the slab** (`_floor_scarf`):
the front floor runs one overlap aft on the print bed and tapers through the slab
at its nose; the back keeps the matching bed-side wedge. The assembled top stays
flat under the core, while both printed bearing faces remain support-free.
**Every seam laps, none butts** — the form suited to the face.

That seam is pinned at **[2](Y_LEVELS) levels** per side wall — a wall above the floor
and one under the ceiling — so every piece crossing it is pinned at its own end: the floor
level pins the two bottom pieces, the ceiling level the two tops. `_bosses` drops a level
landing within two socket collars of one already placed, so the ladder carries one level per
height it is owed.

Each level stands the pin's own face **[13 mm](BOSS_END_CLEAR)** off the end wall it pins
under. The back plug's full-width underside runs to its inboard tip on a 45° wall-rooted
corbel. The front lip's slide channel gives up the matching profile one `fits.slip` lower,
so the square registration faces and full insertion travel remain while neither half leaves
a support contact in the pin slot. Its square pass envelope stays whole and its roof then
rises 45° in X to the inboard tip, adding clearance rather than taking any from the plug.
Both ends are fenced — nearer its wall, the lower collar's
carve leaves a corner of the front lip in the back half's register; further from it, the upper
collar's 45° underside comes down the −X wall into `fluid-1`'s lane.

Each cross-pin is sized to its job. Reading an M3×10 screw outboard→inboard from
the ±X exterior: a Ø6.15 mm head counterbore, then the pin body (the screw spans
the head seat to the heat-set, so the body is screw length − heat-set long), then
the heat-set, then a one-wall cap. The counterbore retains that complete circular pass and
bearing envelope, while its unsupported crown continues on two tangent
[36°](TEARDROP_ROOF) roof planes. The four head pockets therefore close without isolated
support towers.

- **Receiving piece = pin** (the back pieces): a [9.9 mm](PLUG_DIA) SQUARE prism (the shank
  + one wall each side, *not* the head — the head sits in the wall counterbore) from the
  exterior to the heat-set, seating in the socket's slot.
- **Lip piece = socket** (the front pieces): a collar slotted
  [10.2 mm](SOCKET_BORE) square to take that pin as a slide fit, with the ruthex M3
  heat-set (Ø4.0 × 5.25) capped at its deep inboard end.

**Each boss stands on the joint it pins.** A plug is the wall it drives through and
the reach it needs past it: the first `wall` of its length *is* that wall's own
material and the rest a stub off it, its mouth-side face on the receiving mouth. A
socket is a **block round that plug** — [16.2 mm](SOCKET_OD) square outside,
[10.2 mm](SOCKET_BORE) square slotted, one `wall` of material the whole way, a
`socket_cap` over the insert's blind end — its rim-side face on the lip rim and its far face a
hair under the seam mouth, so it stands on that band down its
whole length. That band is one `wall` deep and runs the piece's full height, the way
a telescoping lip does. Those two matings are the pair the overlap depth is struck
from — it works out to (plug + bore)/2 + one wall. Between the two levels the corner
is the wall's own air.

## The Z seams slide home

Bottom↔top, per column, at `enclosure.z_seam`: **a full-travel slide on hooked rails, and
no screw anywhere on it.** Down each flank's **straight run** the bottom piece raises an
**arm** on its mouth, standing one [0.15 mm](SLIDE_SLIP) inboard of the top's own wall,
and the arm's **head** steps back out over the **groove** between them: a
[5 mm](FRONT_HOOK_LAP) overlap on the front column and [5 mm](BACK_HOOK_LAP) on the back.
The top piece's wall runs to the mouth at full section — the **foot**, its caught face
[8.7 mm](HOOK_FOOT) over the mouth — with a **notch** in its inboard face that swallows
the head, closing back to the full wall on a 45° roof. The storey is [14.8 mm](Z_RISE)
mouth to rim, and **the flavour deck is its ceiling** — the rim stands under the lowest
valve plate (`z-seam-under-deck`), which is the whole height the box has to spend here.
It buys the groove first: [8.85 mm](HOOK_NECK) of it, the top piece's own sliding tongue,
with 5.9 mm of head over the catch. That height is the Z seam's own — `lip_len` is the Y
seam's overlap, struck off its boss, and the two are independent figures. The two columns
enter from opposite ends: **front-top enters fore of home and slides AFT**, over the front
wall's own plane in open air ahead of the box; **back-top enters aft of home and slides FORE**,
over the open Y-seam mouth before the halves telescope. Each mouth rides its shoulder the
whole way until the foot's end face lands on the **stop block** closing that rail. That
contact is the column's Y datum; the end walls and corner turns close head-on one
`slide_slip` behind it — the same telescoping mate, arrived at along Y instead of dropped in.

On both columns, the foot carries the flank's full 6 mm inward section from `interior_x` to
the nominal 9 mm face on both sides: [6 mm](FRONT_RAIL_FOOT) in front and
[6 mm](BACK_RAIL_FOOT) in back. Each bottom hook carries a 5 mm bearing overlap at that
face's inboard edge. Their arms reach [10.15 mm](FRONT_RAIL_INBOARD) in front and
[10.15 mm](BACK_RAIL_INBOARD) in back from `interior_x`, inside the 14 mm body-free seam
band. Each catch lies wholly over its six-millimetre foot and keeps a complete exterior wall
outside its channel.

**Lifting a seated top lands each foot's flat top face on its head's flat underside,
along both whole runs** — [102 mm](RAIL_RUN_FRONT) per flank on the front column,
[233 mm](RAIL_RUN_BACK) and [221 mm](RAIL_RUN_BACK_W) on the back — horizontal printed
face on horizontal printed face, square faces bearing full from the first micron. The two
back flanks differ by the PRV passage: it crosses the −X run and takes
[12 mm](VENT_CHANNEL_W) of it, which is the figure that flank is already short by.
**The two columns end their runs on different things.** Aft of the front run the top
piece carries nothing but its own seam band and the Y-seam tongue, and both are inboard
surfaces the channel may cut — so that lane runs clear off the piece's aft end, nothing is
left to sweep around, and the run reaches its own structural limit: `wall + z_lip_y_margin`
short of the joint, where the Y telescope's overlap begins and the Z lip must stop. **The
back column is that mirrored**: back-top enters AFT of home and slides FORE, so what sweeps
its run is what it carries fore of it — its own Y-seam band, inboard surface the same
channel may cut. That run needs no horizon either and reaches the rear wall's own corner
round. Neither flank stops short for the PRV chase either, because the chase's two halves
are held to different rules (`_vent_chase`): the RIB keeps out of the band the joint reaches,
since it is solid and would sweep the rail, and it parts on the seam's rim so each piece
stands its own height of it and neither crosses into the other's travel; the PASSAGE is the
hole through that rib, sweeps nothing, and goes straight across — the rail gives up
[12 mm](VENT_CHANNEL_W) where the one opening that has to cross it does, and the duct keeps
its whole section. Both pieces cut that passage, so the groove's discharge leaves through
the flank on either side of the seam rather than half of it standing in the other's wall.
**Each top escapes toward the end of the box it stands at** — front-top fore into the room,
back-top aft toward the wall — so neither has to be lifted over the other. Front-top's
escape is open air, and what holds it there is the Y
seam's **upper pair of screws** — so two screws out and front-top draws straight off the
front of the box, the back column and whatever the box is built under never touched.
Four M3×10 close the box; the same four open it.

**Every face of the joint prints at the box's own rule, and the catch faces are square.**
The head's underside — the catch — is the joint's one down-looking flat, an abrupt
ledge at the top of a piece that prints floor-down; the arm's base falls back to the lip's
underwall on a 45° under-flare. On the piece that prints mouth-down, the notch is an
open rebate in the wall's own inboard face — no cavity closes over the bed — and where
the channel's lane does cut interior bulk, a **gabled roof** of two 45° faces closes it.
Every sliding face is vertical or horizontal, and the top's outer skin keeps its full
`wall` of flute backing down to the mouth.

**The corners give the slide its lane.** Over the seam band each bottom piece carries its
two pillars **solid to the rim**, flats one `slide_slip` off the walls the top's faces
sweep along; the top piece stands off that whole band and its pillar regrows above on the
45° pair every ceiling over a void here closes at. **The channel is the run's own span
and the sweep aft of it**: what a station of the sliding piece has to clear is the head,
so behind the stop block the lane is carried at **full section right off the front piece's
aft end**, through the Y-seam tongue's own flank segment and past its tip. The flank's
mouth band comes out as one unbroken rebate with no blunt face standing in it. At the
front column's Y/Z crossing, the channel opens all the way through the tongue's slipped
outer face below its roof: the outboard half-gable rises aft at 45° from the full wall on
the Y-joint plane, carrying its own support path with it. There is no 0.7 mm strip standing
from the bed between the two clearances. The tongue returns at full section **above that
ramp** — which is the height the Y telescope bears on.

**And the slide is proved, not asserted.** `_report_slide` sweeps each built top from full
entry to home against its built bottom — a ladder of stations, dense where the joint
closes — and lifts it a millimetre off its catch: `z-slide-front-clear`,
`z-slide-back-clear`, and the two `-catch` rows carry the readings on the scorecard.
`z-slide-front-lanes` runs the front sweep again loaded — the piece with the flavour pack
aboard, against the seated refrigeration stratum — and `core-rides-in` sweeps the cold
core's own entry (below).

**What makes all of that fit is the band the walls keep.** A body standing on the
floor slab spans the interior wall to wall, so a body laid on a wall's face would
leave the seam machinery nowhere to stand. A **floor body is held one
`side_band_inset` in from the ±X walls where it meets the seam's furniture** — the
Y-seam collars, or the rail band over the seam's own storey. Each column's full-section foot,
groove, arm and head reach [10.2 mm](RAIL_REACH) inward from `interior_x`, inside that same
band.
The **+Y wall keeps one `rear_seam_clear`**, the rear Z-seam lip's own thickness. That is a requirement
on the body where it meets one, not a rule about the wall: beside one — over or under
one — the band is the wall's own air. Of the three bodies on the slab only the cold
core meets the band at the seam's storey; the compressor and condenser stand wholly
under the mouth. Everything on the slab sits flat on it: the print-corner relief runs
on the standing verticals and the Y-seam's floor joint stays inside the slab, so the
seat is square and there is nothing standing there to clear.

So the pack seats flush against the **seams**, not against the walls, and both
walls carry all [2](Y_LEVELS) levels at full section.

**A wall that lip stands on is `2 * wall` thick, floor slab to lip rim.** The lip is
the cavity's own one-`wall` skin standing proud of the interior face, and a skin that
began at the seam would land its underside in air: a one-`wall` soffit round three
sides of a piece that prints floor-down, with nothing under it to print on.
`_lip_underwall` carries that same skin from the shoulder down to the slab, so the
two fuse into one wall with no step in it and the bottom pieces come off the bed with
no bridge in them. What it spends is the cavity, one `wall` off three sides of each
bottom piece — which is what the pack already stands off them (`front_seam_clear`,
`rear_seam_clear`, `side_band_inset`), measured rather than assumed by
`wall-under-lip`. `lip_face_x` is the flank a body down there meets: the MQ-6's can
bottoms on it through the well cut back to it, the condenser's aft fin roots on it, and
the compressor's suction lane is struck from it.

The Y seam is a stated plane, `enclosure.y_seam`, checked against those bands
rather than derived from them: which pieces the box comes apart into is a decision
about the pieces — what each has to carry, and what a hand reaches when the front
assembly is off.

`rear_seam_clear` is the single source for the +Y wall: `enclosure_assembly` seats the
rear-wall bodies against it and `enclosure.py` builds the box to it, so the wall
the bulkheads mount through and the wall the box is built to cannot drift apart.

The crowding mechanism stays in place even though nothing is crowded now: each Y-seam level
is offered only where the socket's whole body — slot, heat-set and cap, one collar
radius either side of the axis — stands clear of what `_measure_wall_block` found in
that corner, measured against the contents themselves rather than their bounding
boxes. It reads zero on both walls today, and the build prints each wall's levels so
a wall that ever loses one is visible rather than silent.

Each printed piece fits the H2C left-nozzle build envelope (325 × 320 × 320 mm)
even though the whole enclosure does not — that is the point of the split.

## Power-column boss corbels

The +X wall of back-top carries one horizontal boss for every mounting hole in the PSU, main
board, two relays and ground stack: 17 in all. Each stem is a D in its mounting plane — the
round crown keeps the M3 insert annulus compact and its 7 mm flat floor gives a full-width 45°
corbel one continuous down-facing plane to carry. The D section runs all the way to the body's
own mounting face, so no round pipe is left bridging between a generic support block and the
part.

`enclosure_assembly.wall_mounts` offers that corbel all the way to every mounting face and
intersects the offered material with the installed pack. Fifteen fit across their complete
width. At the two upper holes of relay #2, the module's conservative underside pin envelope
crosses only the inboard side of the offered wedge. Those two corbels begin 1 mm past the exact
blocker only across its Y projection; each clear outer side still carries a wall-rooted 45° wing
all the way to the mounting face. Their D stems remain whole across the holes. `east-boss-corbels`
reads all 17 additions back against the installed bodies and records both the full-width and
blocker-profiled populations; `east-bosses-print` reads the built back-top and rejects a missing
wedge or any complete Ø7 free edge.

## Condenser cradle

The condenser's four sheet flanges are the block's whole purchase. Its two fore flanges slide
into rails on the front wall; its two aft holes screw into fingers on a standing fin at the +X
wall. The base rail and lower finger run to the floor slab. The crown rail and upper finger do
not: each carries its entire down-facing plane on a 45° corbel rooted on the wall or fin it grows
from (`_cond_cradle_corbel`, `_cond_mount_corbel`).

The crown wedge is only the rail's [3 mm](COND_SLOT_GRIP) reach. The aft wedge is longer, but it
lies wholly in the donor block's open end recess and stops on the fin's west face. Both are read
against the installed solids by `cond-corbels-clear`; the condenser stays fixed and the closer
one keeps `cond_mount_clear` of assembly air.

Each fore-flange groove keeps its exact [1 mm](COND_SLOT_OPEN) opening at the seated wall stop,
then its roof rises toward the bay at 45° and runs through the rail crown at the insertion mouth.
The sheet datum and grip are unchanged, while no flat one-millimetre roof is printed over the
rail below it.

## The box closes in four motions

The slides fix the order, and the order is the service story backwards. **Front column**,
on the bench: the refrigeration stratum seats in front-bottom, and front-top — carrying the
flavour pack made up into its trays and tee wall — slides AFT onto it, in from the front. **Back column**,
on the bench, empty: back-top — carrying the chain, the meter, the ceiling panel and the
wall electronics — slides FORE onto a bare back-bottom, over nothing. **The core rides in
through the mouth**: the closed back column stands upright and the cold core enters over
the open Y-seam mouth and slides aft to its seat on the rear lip, under the hold-down
feet (each fore arris eased 45° for exactly this), past the chain and the bulkhead unions,
into the pockets their stems land in; the lid's tenants — the water pump and the rest —
go on through the same mouth after it. **Then the halves telescope**: the front assembly
slides aft into the back, its corner blocks closing on the core's front face, and the four
Y-seam screws drive from the ±X exteriors. Service is the same door swinging the other
way, and the first of it needs no bench: **the upper two screws alone free front-top**,
which draws fore off its rails into open air with the box still standing where it is —
the flavour pack, the trays and the tee wall coming with it. All four screws out takes
the front assembly fore and off, opens the bay through the mouth, brings the core out
fore, and back-top slides fore off its rails if the tub itself is the work.

## Cold-core grips

The core is the heaviest body in the machine and the one with no hole in it — a foamed cup
under a screwed cap, plain skin the whole way round. What fastens it is the closed box: **the
seams stand every piece against its neighbours**, so a feature printed on one piece stands
over a body sitting in another, and the front-bottom, the back-bottom and the back-top close
on the core together.

Four features, two mirror pairs, and nothing on either that is not a face of the core:

- **Front corner blocks** (`_core_stops`, on `enclosure-front-bottom`). A block in each front
  corner of the slab, [38 mm](CORE_STOP_WIDE) across — the ±X wall inboard to one corner round
  past the tangent — and [40 mm](CORE_STOP_RISE) off the slab. **The pocket in it is the core's
  own plan outline offset one `split_slip`, not a shape of its own**: a Ø[24.3 mm](CORE_STOP_BORE)
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
  [8 mm](CORE_HOLD_LAND) over the crown. The foot lands on the cap — 0 by intent, the way a seat
  in this box lands on the face it takes unless something else locates it — and that straight is
  what makes the foot a flange on a web instead of a cantilever. The lane is the one strip of the aft crown clear of
  the water pump inboard, the power column outboard and the +Y wall's two flavour unions in the
  band, taken on both flanks so the pair is a mirror.

The slab takes the weight and the +Y wall takes the aft, so the four between them close every
direction the core could go. `enclosure_assembly.check_core_held` reads each inside its own
window off the built pieces (`core-held`).

**The core enters from ahead, and only from ahead.** The back column closes empty — its
+Y wall cannot pass over a seated core — so the core rides in through the open Y-seam
mouth, aft over the slab to its seat, the crown sliding under the brackets' eased feet
(`core-rides-in` sweeps the whole lane). The front assembly then slides aft onto it and
the corner blocks' pockets — the core's own plan outline offset one `split_slip` — close
on the front face at the slip.

**The front blocks need no support**: they print floor-down with no overhang in them at all. **An
aft bracket's bearing face does.** The straight from the head of the leg out to the foot's tip
descends at 25° off vertical and is the bracket's upper face, laid on the section beneath it the
whole way out — but the bearing face under it is flat and is the lowest thing on the bracket, so
it is a soffit off the +Y wall and takes removable support in its open lane.

## The reeded skin

Every standing wall is **fluted** — half-round grooves [4 mm](FLUTE_WIDTH) across and
[1.2 mm](FLUTE_DEPTH) deep, the profile `cadlib/reeding.py` carries and
the corner coupon at `c14bb2fff` was printed on. That coupon is this box's own corner
at this box's own `wall` and `corner_round`, so what printed there is what prints here, and
neither can drift from the other while they read one function.

**It is in the MESH and not in the solid**, and that is a decision rather than a shortcut. The
fade is what makes the texture look made rather than applied, and the fade is a FIELD OVER THE
SURFACE — how far a station stands from the nearest place the show face ends. A boundary
representation can carry a fade that runs level, because a level fade is a loft; it cannot carry
one that follows an opening's rim, a pocket's edge and the display facet's diagonal arris all at
once. So the STEP is a plain box and [flute_skin.py](/hardware/printed-parts/cadlib/flute_skin.py) cuts the flutes into the
mesh on the way to the bed. Everywhere else on the machine the STEP is the whole of the part;
here it is not, and the `.stl` beside it is.

**Nothing tells it where an edge is.** At every station it asks the piece whether it has
material AT the nominal plan — by level cut, not by naming features — and takes a distance
transform of the answer. A flank opening, a port chip's seat, the nameplate's pocket, the bay's
own mouth, the seam a piece simply ends on, the bed, the top arris and the facet's 45° arris are
one fact to it, and every one of them gets the same ramp over [5 mm](FLUTE_RISE), on the same
smoothstep the coupon fades on. There is no list of edges anywhere, because there is nothing to
list.

A rim that runs WITH the flutes is not one of them: a groove ending along its own length has
nothing to stop. The Y seam is one, and so is every jamb.

**The field closes on itself.** [260](FLUTE_COUNT) grooves go round [1333.4 mm](FLUTE_PERIM) of
plan, struck by ARC LENGTH from a datum on the front wall's centreline — which is what carries a
flute across a [12 mm](COLUMN_ARC) corner turn at exactly the spacing it keeps on the flat. No
station restarts the array and no two arrays meet anywhere. The pitch is what that count lands
on, [5.1285 mm](FLUTE_PITCH) against the coupon's [5 mm](COUPON_PITCH), and three bounds spend
the choice:

- **`flute-closes`** holds the pitch to the coupon's.
- **`flute-hides-seam`** puts the **Y seam inside a groove** — the one straight line running the
  full height of both side walls, landing [0.1 mm](FLUTE_SEAM_MISS) off a groove's centre, in
  the shadow that is already there rather than on a land.
- **`flute-clears-jamb`** is the opposite ask and the right one for the bay: each mouth arris
  and the pump cartridge edge inside it fall on a LAND. A rim landing in a groove is an arris tapering to
  nothing on the groove's floor, and a wedge that fine at a 0.42 mm bead prints ragged — on the
  one line the user looks straight at.

The datum is a groove centre on **x = 0**, the plane the whole machine is struck about, so the
field is symmetric in x whatever its pitch.

**The box has a second field indoors.** What the field is struck along is a RAIL, and the outer
plan is one of them. With the pump cartridge in, the bay storey shows the two narrow mouth
returns outboard of the cavity planes; those two actual surfaces are two open rails.
`_bay_storey_segments` carries their one global arc coordinate from one mouth edge to the other:
[350.62 mm](STOREY_RUN) over the storey at z [177.8..281 mm](STOREY_BAND). The two open flanks
and the lower tee face advance the phase but carry no cutter: the former are air, the latter is
berthed or hidden, and the upper closure face stands on another Y plane. The datum remains
**x = 0** and the pitch remains [5.1285 mm](FLUTE_PITCH), so both ledges retain the machine's
inside phase. Each real surface is open; its two ends are edges like any other and the field
ramps to zero on them, as it does at both Z ends of the band, which keeps cutter caps off every
mouth and window arris.

**And a body berthed in the room is an edge too.** Inside a storey the piece has material at
the rail in places the drawer and its steel stand in front of, and a face another body beds
against is not one anybody finishes. `flute_skin._shadow_mask` asks, at every station, whether
a berthed body stands between that face and the storey's mouth — the same question the show
mask asks, asked of the other bodies — so the tee wall carries flutes only where the pump cartridge
leaves it visible, and the plate's own bearing band is left plain. Nothing is listed: the
lower cradle, top clamp and collet plate are simply what the assembly stands there.

**Nothing may relieve into the outermost [3 mm](FLUTE_BACKING) of a fluted face.** The exterior
profile ([print-log.md](print-log.md)) lays two wall loops a side at 0.42 and 0.45, so one
`wall` is 1.74 mm of solid perimeter and a groove floor still has all four of them, with 0.06 mm
to spare. Take more out of the far side and the two pairs of loops meet: the slicer stops laying
four walls, and the change in what it lays under the groove reads THROUGH to the show face as a
mark you can find with a fingertip. What a groove leaves is [1.8 mm](FLUTE_LEFT), and
**`flute-backed`** reads every stated section on a fluted face against the rule — with two of
them computed rather than typed, because the survey that measured this found them and the file
had not stated them: `facet-arris-backed` for the ligament under the display facet's arris, and
`east_boss_bore_end` for an insert bore behind a corner round, where the turn carries the
surface inboard of the plane the bore was struck on.

**It is free to print.** Every groove runs down the build axis, so its own side surfaces are
drawn by the nozzle in XY, carry no layer quantisation at all, and hang over nothing. The ramps
are `flute_depth` of relief over `flute_rise` of height — [19.8°](FLUTE_RAMP) off the wall at the
smoothstep's steepest, against the 45° every relief on this box is struck at.

## The condenser's vents

**The vent is the flutes, pierced.** The condenser's fan draws through one flank of the block
and blows out the other, and both flanks of the box already carry the reeded field — so a slot
[3.1 mm](VENT_SLOT) across is struck down the FLOOR of every groove standing over the finstack,
on the field's own centres, clean through the [6 mm](VENT_FLANK_T) a bottom piece's lipped flank
carries. Both jambs run WITH the flute and the groove carries on past both ends of the slot at
full depth, so nothing crosses a flute anywhere here and no edge it makes is one the skin stops
on. Off-normal the wall reads as unbroken reeding; head-on it is a grille.

**The mullion is the governing number, not the section behind the groove.** A slot takes its
width out of the pitch, and what is left between two of them is [2.0285 mm](VENT_MULLION) at
[5.1285 mm](FLUTE_PITCH) centres — against the [1.74 mm](VENT_SHELL) of loops the exterior
profile lays (2 × 0.42 outer + 2 × 0.45 inner, [print-log.md](print-log.md)), which leaves
[0.2885 mm](VENT_SPARE) and ceilings a slot down every groove at [3.3885 mm](VENT_CEILING). The
two figures move OPPOSITE ways: the jamb stands half a slot off the groove's centre, out on the
half-ellipse where the groove is shallower, so the flank behind a jamb is
[5.2416 mm](VENT_JAMB) rather than the 4.8 under the groove's own floor — a wider slot never
thins the wall and only ever thins the mullion.
The coupon at `c14bb2fff` printed this scheme beside the ceiling slot and a full-groove-width slot
down alternate grooves, on a section of this same flank at this same pitch.
**`flank-vent-mullions`** reads every mullion off the built piece.

**Every groove, and the stations are the field's own.** `vent_grooves` walks `flute_centres` and
asks `plan_at` where each one landed, so a slot is struck at a groove centre by construction and
the vent follows the field if `flute_count` is ever retuned — there is no Y station typed
anywhere in the feature. A groove is in when its whole slot lies inside the block's AIRWAY: the
[34..148 mm](VENT_WINDOW) between the block's two recesses, which is finstack. The 20 mm at
either end is the sheet the box holds the block by, and the fan draws through neither.
[22](VENT_GROOVES) grooves stand in that window on each flank.

**In height the band is the FAN, not the airway.** What moves air through this wall is the axial
fan bolted to the block's own flank; the finstack either side of it is served by whatever that fan
pushes, and wall opened opposite it is opening on metal. So the band is the placed block brought
in [22 mm](VENT_FAN_RISE) at its base and [5 mm](VENT_FAN_DROP) at its crown —
[31..141 mm](VENT_BAND), a [110 mm](VENT_BAND_H) band, the fan's own footprint and nothing wider.
Both insets are read against the block where it stands, so raising the block raises the vent.

**Less whatever the flank carries behind that particular groove.** Nothing is listed: the piece
is asked, groove by groove, what stands ROOTED on its inner face, probing one
[3 mm](VENT_CLEAR) wall inward and keeping that same margin past both jambs and both ends. The
transoms are the opening vocabulary: if a root's margin enters one course, that whole segment
stays solid and fluted rather than becoming a one-off short slit. A single opening marooned past
such a land stays wall too. The MQ-6's two posts stop below the vent band, but its can chute is
cut through the added inner flank skin beside it. The two intake grooves whose jambs would leave
less than one 3 mm wall to that chute remain completely solid in every course; the chute is not
widened into a vent, and no 1.261 or 1.981 mm strip survives between the two openings. All
[80](VENT_RUNS_IN) realized intake openings are the full [24.5 mm](VENT_SHORTEST) segment;
[0](VENT_SHORT) have a different height.

**[3](VENT_TRANSOMS) transom bands cross that vent, and they are why it prints.** A mullion is
[2.0285 mm](VENT_MULLION) across. Pierced clean over the whole band it would stand
[54.2:1](VENT_ASPECT_BARE) — a picket that tall with nothing tying its top to anything. The brace
is **not** a bar between two mullions, and nothing stands at 45° across a groove: at
[3](VENT_TRANSOMS) heights — [57.5, 86, 114.5 mm](VENT_TRANSOM_Z) — the wall is simply **not
pierced**, so every mullion and both jambs run into one plate of full section
[4 mm](VENT_TRANSOM_H) tall. Nothing bridges and nothing grows out of a tower. What is left is
[4](VENT_SEGMENTS) slot segments of [24.5 mm](VENT_SEGMENT) apiece, and the four of them plus the
three transoms close exactly on the band — `vent_transoms` divides the band rather than listing
stations, and asserts that closure, so the layout stays symmetric about its own mid-height
whichever of the three figures moves.

**The groove runs through a transom unbroken.** Only the piercing stops. The field is struck on
the flank's whole plan, so a transom is invisible off-normal and the reeding reads continuous down
the wall — head-on it is a grille in four courses. Both ends of every one of those
[4](VENT_SEGMENTS) segments are closed by a 45° hip, the angle every relief on this box rises at:
each hip sits down inside the groove's own shadow, the sill only takes material away as the print
climbs, and the ceiling closes at exactly the angle the box supports nothing steeper than.

| | slots | openings | thinnest mullion | tallest opening | free area |
|---|---|---|---|---|---|
| −X intake | [20](VENT_SLOTS_IN) | [80](VENT_RUNS_IN) | [2.0285 mm](VENT_MEAS_MULLION) | [24.5 mm](VENT_TOWER_IN) | [56.9 cm²](VENT_OPEN_IN) |
| +X exhaust | [22](VENT_SLOTS_OUT) | [88](VENT_RUNS_OUT) | [2.0285 mm](VENT_MEAS_MULLION) | [24.5 mm](VENT_TOWER_OUT) | [62.6 cm²](VENT_OPEN_OUT) |

Both read off the built piece at the flank's mid-section, over the fan's own band. A pierced field
is [60.4 %](VENT_OPEN_PCT) open where every slot runs; the readings above are what the band came
out at with the transoms, the hips and the intake's rail in it. **`flank-vent-towers`** is the
reading the bed cares about: the tallest opening on either flank is [24.5 mm](VENT_TOWER) on a
[2.0285 mm](VENT_MEAS_MULLION) mullion, which is [12.1:1](VENT_ASPECT).

**Two things this does not answer.** There is **no thermal spec anywhere in this repo** — no CFM,
no free-area requirement, no ΔT budget — and the fan is documented only as a 12 V brushless axial
drawing ~0.35 A, so the areas above are what the flanks give and not what anything has asked for.
And **the intake path is obstructed**: the compressor stands 110 mm wide across the west half of
the same bay, x −76.1 to 33.9 and up to z 135, and the condenser's intake face is at x 44.5 — so
air drawn through the −X flank reaches the finstack through a 10.6 mm slot between the two
bodies. Neither is a question the vent geometry settles.

## Support-removal strategy

The enclosure is optimized for **how its supports come out**, not for the smallest total
overhang area. A production-profile slice reports both the connected support bodies which reach
the model and their separate interface islands: the former is the number of things a hand has to
remove, while the latter keeps a branching tree from hiding several distinct contact regions.
Fewer connected supports comes first. Supported area and support volume are only tie-breakers
after that topology.

The two other costs remain **independent readings**, not terms collapsed into a score:

- A support's useful build-up is the vertical distance from its own base to its first model
  interface. Under **5 mm** is a defect, **5–10 mm** is marginal, and **10 mm or more** is a decent
  length for the support to establish itself. Improvement is capped at **15 mm**: more length is
  harmless, but earns no further preference.
- A support rooted on model material is a defect of its own. A support rooted on the print bed is
  preferred irrespective of its length. A short bed-rooted support and a long material-rooted
  support are therefore reported as two different compromises rather than traded against one
  another invisibly.

A candidate which removes a whole separate support that was both short and rooted on model
material wins on every count at once, and is the strongest fix the audit can name.

Down-facing geometry is changed before support is accepted. A corbel, chamfer or tangent
teardrop follows the exact feature it carries and reaches its whole supported face; it is not a
generic triangle merely placed nearby. A feature on a wall preferentially ramps along that
wall's normal — an X ramp from an X wall and a Y ramp from a Y wall — because the wall is the
root that already prints. The corresponding exact solid, passage, clearance and motion gates
remain hard constraints.

Placed components and printed features are design variables when those constraints still pass.
If a blocker leaves a separate short or material-rooted support, moving the smallest sensible
feature or component enough to remove that contact is part of the audit; crowded assemblies are
not shifted speculatively. The raised relay in [back-top's ceiling](#back-tops-ceiling) is this
clause worked once. Every support which remains in a production slice is named with its
piece, contact region, root kind, build-up and the geometric or functional reason it cannot be
removed. This policy applies to every printable part in the enclosure assembly, not only the
four shell quadrants.

[`support-audit.json`](support-audit.json) is the coverage and retained-support ledger. An
`audit-required` or `profile-required` piece is visible work for the support campaign, not a
publication blocker and not permission to borrow another piece's settings. The audit is a design
and quiet-time reconciliation tool; it is not part of the normal build or publish path and never
holds a coherent visual iteration for a production slice.
[`enclosure_support_audit.py`](/hardware/scripts/enclosure_support_audit.py) reads an exported
Bambu G-code directly, or refreshes only the mesh in a temporary copy of the named production
project before slicing it:

```sh
python3 hardware/scripts/enclosure_support_audit.py \
  --piece enclosure-back-top --slice-current \
  --model hardware/printed-parts/enclosure/enclosure/enclosure-back-top.stl \
  --profile hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf \
  --json-out hardware/printed-parts/enclosure/enclosure/enclosure-back-top.support-audit.json
```

The result carries the model, profile and derived G-code hashes, the slicer's support settings,
all interface islands and both plate and CAD coordinates. The ledger supplies the human reason
for each connected body that remains.

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

A wall's inner face is **flat only past that landing**, so anything ROOTED on it answers to
`enclosure.wall_flat_from_corner` rather than to the relief's own tangent — the C14 inlet's
tunnel is the one that does, and `enclosure_assembly.c14_flat_column` is the column that
leaves it whole on the flat.

**The pump-cartridge storey has no fixed front-top frame in its withdrawal span.** `_bay_cut`
removes the complete exterior front-wall band, both rounded corners and both side skins from
the bay floor through the lintel, then continues aft to the collet plate. The installed cradle
owns that same [215 mm](CRADLE_WIDE) exterior width. Its outline is vertical in Z: there is
no 45° narrowing toward the sill. Only the two hand pockets and aft guide notches interrupt
that width, and [0.5 mm](PUMP_CARTRIDGE_CLEARANCE) of reveal remains at the sill and lintel.

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
  shares material with the cradle groove. Its ceiling keeps the column's two 45° walks through
  that overlap, while the groove roof rises toward its insertion mouth; the rail's east end and
  the lens print as one body without restoring a flat roof over the pocket.
- **X+/Y+** — the PSU's aft-east corner, over z 252.4–306.4, about a millimetre deep at its
  widest. The brick cannot give ground instead: its rear mount hole is on the aftmost boss
  station, the relay and the main board are packed one `WIRED_CLEAR` at a time ahead of
  it, and the front of that stack stands ~1.3 mm off `carb-1`. What a column cannot absorb is a seam station:
the lens runs along the wall to its cusp and would be a leaf-shaped hole through a socket
collar's root, so a station landing there stands one collar radius clear of that cusp
instead and the collar comes out whole — the front column's front-wall station
(`enclosure._z_front_station_y`) and the back column's rear-wall one
(`enclosure._z_back_station_y`), which are the two seam ends that sit in a standing corner.

The rest of the seam furniture follows the orientation rule: the Z seams' rails run
the straight flanks only — a slide neither turns a corner nor stands where a corner's
own skin sweeps — and the deep channel that lets the bay floor and the posts pass the
rails is the one mark the slide leaves inside a standing corner. The Y-seam lip sits
mid-wall where there is no vertical arris, so it stays square.

The Y-seam lip is the one joint the orientation costs something. Its ceiling
tongue juts one overlap past the body into the space the back piece's ceiling
occupies — a cantilever that cannot be buttressed without colliding with the back
piece, and so wants print support. The floor does not share that cost: its tongue
runs aft at the slab's full thickness with its underside on the bed, then ends in
a one-wall-long 45° scarf nose. The back half's matching wedge also grows from the
bed, so the cold-core bearing plane carries no supported surface. The side-wall
segments, vertical to the bed, are free.

The **ASSE drip pan's sleeve** in the back-top piece has one supported surface: its floor beyond
the wall-rooted `pan_sleeve_corbel`. The tray is longer than a 45° wedge from that one wall can
carry, and nothing stands under its east half to root a second wedge. That remaining soffit is
reached from the print bed through the open enclosure rather than from material just below it.

The rim rebate's lid closes differently. Its four strips rise at 45° into the already-open tray
mouth: from the exterior skin on the west, the fore and aft jambs, and the sleeve's east backstop.
The exterior slot and seated flange gap keep their stated planes; only free clearance above the
inserted rim grows toward the mouth. The rebate therefore leaves no short, material-rooted roof.

The exception in that lid is the moisture probe's **open-top lead notch** through the
−X withdrawal wall. The leads rise in the pan's existing open mouth and turn west
through this short notch, which is centred on their installed Y station. Because the
notch opens upward it adds no bridge and traps no support; because it cuts the sleeve
rather than the pan, the pan remains watertight.

The **ASSE anchor** one storey above it carries its full underside on a 45° corbel rooted on
the −X wall and tapering to the deepest section's V foot. Its two 60° seat flanks stand 30°
off vertical and lay on themselves. Behind the anchor are the two zip ties' channels, one per
tie band and `tie_cav_wide_w` long; each channel continues through the corbel and opens at its
own end.

The **bay floor** is the one feature that costs nothing and pays: it IS front-top's
first layers. Its underside is the seam mouth, the plane the piece beds on, so there is
no face under it to hang and no support in it to pick out. It is a solid slab across the
whole front storey with one slot through it: the pump cartridge slides across it, and the collet
plate comes up that slot from the bed face onto the floor's own top.

The **tee wall** behind that plate costs nothing standing up, and its four bores are the
only thing in it that could have hung. The piece beds on the seam plane, so a bore on Y
lies horizontal and its crown is the only face in the wall that could be laid on air.
Each is **teardropped** (`_tee_bore`): the roof stands on the bore's own tangent points.
Its two planes rise at [36°](TEARDROP_ROOF), one whole degree above the committed back-top
PET-GF profile's automatic-support threshold and verified support-free with that exact profile;
tangency makes that the narrowest and shortest peak at this angle. The lower circle the collar
bears on is untouched, and the wall needs no support.

The **five round tube crossings in the +Y wall** use the same `_teardrop_y` section through
their wall and pocket bosses. Their stated Ø18/Ø17.86 figures remain the complete circular
pass envelopes for the threaded barrels; only the unsupported crown opens into the tangent
[36°](TEARDROP_ROOF) roof. The separately printed identification chip keeps its circular bore,
and the fitting's flange and nut clamp the chip and the remaining wall annulus on their two
faces. The committed back-top profile places neither support body nor support interface inside
any of the five passages.

The **AC inlet's mount** stands off the +Y wall's inner face in back-top and costs
nothing either. Its two flanks are vertical to the bed and its crown runs out into the top
wall; each soffit is cut back to the wall at 45° (`enclosure._c14_tunnel`). One sheared copy
follows the tunnel's R3 outline, leaving neither square ledges under the rounds nor air channels
between tunnel and support. A second follows the collar's exact rounded/tapered profile over the
full 10.25 mm from its open mouth to the wall, so the flange surround and its wider end ears are
carried too. What is left over air is the bore's own ceiling — a bridge the aperture's full
width, carried between the tunnel's two flanks. Nothing on the piece stands outside the print
silhouette: the receptacle's two heat-sets go into the tunnel's fore face, from inside the box,
and the back of the machine is flat.

The inlet stands on the column where its exact moulded rim clears the complete +X ceiling-strip
corbel — `c14-ceiling-corbel-clear` reads about a millimetre of air between the two — so that
wall-rooted 45° wedge continues over the inlet without a relief band or a short support stack.
The aperture, tunnel, collar and both screw stations all follow that one X datum; its Z remains
aligned with the other top-row ports.

The **PRV chase's two lowest roofs lean from the −X wall too**. Where its open exterior groove
becomes the closed fall, the roof rises inward across the exact
[3 mm](VENT_GROOVE_ROOF) show-skin section at 45°. At the Z seam the top piece's rib begins on
the rim and rises along a second 45° X plane for the full [8 mm](VENT_RIB_BASE) from the grown
flank to the cold-core lip. The lip keeps [3.1 mm](VENT_RIB_LAND) of solid land below the square
mouth. Neither level leaves a horizontal face for a short support tree, while the exterior
groove edge, the square passage and the back slide's opening remain on their own datums.

## ASSE anchor

A stepped anchor on the −X wall that the ASSE 1022 chain lies in
(`_asse_cradle`). The chain is five fittings made up by hand on one axis, so
neither the run's length nor the clock any one fitting lands at is a number this
wall can know — but the **section** each one presents about that axis is the
fitting's own. The anchor is cut to each in turn, and the steps between sections
fall out as faces square to the axis.

| section | across | seated on |
|---|---|---|
| PI4512F6S swivel nut | 22.0 | its circumscribed circle — the nut spins on the body |
| Multiplex hex barrel | 33.0 | its own two flats |
| GAGIRA coupling | 25.67 | its circumscribed circle — its clock is wherever the thread stopped |

The two end sections are there to make the barrel's steps and for nothing else, so
each runs the **shorter of the two fittings' lengths** rather than its own: the
coupling is more than twice the nut, and anchor past a section already seated is filament
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
drip over the pan, and it is the whole reason this is an anchor and not a zip tie.

`asse_seat_slip` is the fit across the V and `ASSE_STEP_SLIP` the play along it, the
deeper section taking the latter past both its ends so the barrel drops in and the
steps stop it travelling rather than hold it still. Aft it needs neither: the chain's
inlet collet butts the tap-water union's, and that joint takes the length up.

Two **zip ties** shut the anchor's mouth, one in each band the vent leaves clear on
the barrel — the brass, which is the only section a tie may close on.

Each runs in **its own channel through the anchor's back** (`asse_tie_*`), closed on
every side but its two mouths and `tie_cav_wide_w` long — centred on the tie band it
serves, so the block's back stands solid fore and aft of each and between the pair,
and the ceiling over that run keeps whatever corbel the strip has. It is **straight
on the west and the anchor's own V on the east**, so it is narrowest at the axis and
flares to both mouths: each mouth opens `asse_tie_back / sin 60°` off its lip's own
arris, on the block's face where a hand reaches it, and at the axis the flare leaves
a zip tie pushed through the room to turn the vertex by cutting its corner. It stands
one `wall` west of the apex at every station, struck on the deepest section's apex so
the web is no thinner than that anywhere, and one `wall` off the side wall behind it —
so its width is a remainder between the two rather than a number.

A tie is a closed loop, so its zip tie also has to cross the chain's top flat, come west
in that lane and drop into its channel — and **the top wall is never cut for it.** The storey the chain lies on is struck to leave
that channel instead (`enclosure_assembly.DECK_CEILING_CLEAR`, the zip tie's own section
plus its clearance), so `wall` stays whole across the whole ceiling and the deck pays
the millimetre out of its own headroom. That leg is **laid, not pulled**: this piece
is populated inverted on the bench — ceiling down — so the zip tie lies on the
ceiling's inner face and the chain comes down onto it.

Nothing about the chain's weight is theirs: cut both and it still lies where it lies. `enclosure_assembly.check_asse_seated` is the row that reads the anchor
closed on the barrel, measured off the two placed solids, because every other
reading on the card is satisfied by a chain floating in air. And `check_tie_channels`
is the row that reads the **route**: the column between each channel's top mouth and
the ceiling, which is the room the loop comes down and what a corbel on the strip's
outboard run would close over.

## Flow-meter anchors

Two anchors off the **top wall**, one over each of the DIGITEN meter's collet
barrels, and nothing over the round body between them (`_flow_meter_anchors`).

The meter is a ⌀26 body with a ⌀12 barrel out of each rim. The body reaches to
within a hair of the top wall's inner face; the barrels leave the best part of a
centimetre under it. So the arms are what a printed feature reaches here, and each
takes a **bore concentric with its barrel** — half a cylinder at `seat_r`, opening
down, so the seat and the barrel share a surface all the way round instead of
touching on the two lines a V gives. The barrel comes straight up into it.

**The arc stops on the barrel's own axis plane, and the rib carries one
`flow_meter_anchor_wall` past that.** The axis plane is where the arc is widest, so
each lip comes out a **flat 3.000 mm strip**. Carried any further round, the arc
runs out to nothing against the flank and leaves a feather.

Each anchor runs the middle of its barrel: one `DIGITEN_BODY_CLEAR` off the body's
rim, and clear of the outer `DIGITEN_COLLET_FREE`, which is the push-fit ring the
tube comes back out of. The rib's length is its cavity's — `tie_cav_w` of zip tie and
buffer with `tie_cav_wall` of itself at each end, centred in the band the barrel
allows.

**The zip ties are the load path here.** A seat that opens downward carries nothing, so
unlike the ASSE anchor's two zip ties these hold the meter up — a purchased part of a few tens
of grams on two nylon zip ties. `enclosure_assembly.check_digiten_seated` reads the
seats closed on the barrels at the slip itself, there being no angle in a bore to
divide by; travel off the placed pack is 0.231 up into them, 0.400 either way across,
and free downward.

Each anchor's zip tie runs a cavity over its bore, and **nothing is cut for it.** The
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
`flow_meter_anchor_wall` strip either side of the bore, the anchor's whole 9.50 length, with
nothing under them. Everything over those lips is the arc closing inward on itself, so
the hood carries its own crown, its flanks are vertical, and the lips are the only thing
in the feature support has to reach.

## Tube anchors

One pattern wherever a wall comes near enough to reach something round
(`_tube_anchors`): a **bore concentric with the body**, half a cylinder at
`seat_r`, and the zip tie's channel behind it. Three of these hold a length of tube
(`enclosure_assembly.TUBE_ANCHOR_SITES`) and three hold a fitting
(`enclosure_assembly.BODY_ANCHOR_SITES`) — the same rib either way, since what the
builder is handed is an axis, a direction along it and a radius.

**The arc stops on the body's own axis plane and the rib carries one `wall` past
it**, so each lip is a flat strip rather than a feather — the anchors' bargain,
on the one body this machine has twenty of. The rib's length is its cavity's:
`tie_cav_w` of zip tie and buffer with `tie_cav_wall` of itself at each end. It states
no height of its own — it is handed the body, and the wall it stands on is where it
stops.

**The zip tie's channel is what is never fused.** The rib is one box its whole length
up to one `wall` over the bore's crown, its two ends carried on up to the face it
roots on, and one bore through all of it. Where a small tube stands far enough from
its root face to put at least one routing buffer back into the load path, its central
band is solid-backed from the wall until one `wall` of useful cavity remains. Compact
fitting anchors keep their available clearance instead of acquiring a skin-thin roof.
The two side mouths stay open and no cutter grazes them. A zip tie therefore goes in
**before** the body does.

**And the face is the piece's own** (`piece_root_faces`), not the box's interior. A
station is struck in the box's frame because that is the frame the body is in; the
plane a rib STOPS on is whatever the piece carrying it presents, and on the two
pieces with a grown flank those two stand [6 mm](BACK_TOP_FLANK_GROWN) and
[6 mm](FRONT_TOP_FLANK_GROWN) apart. Measured to the wrong one, the channel is
drawn inside the wall's own stock and the rib arrives buried to its crown.

**Where the piece's face leaves no channel, the wall gives the rib its lane back.**
The box's interior is one `wall` inside the exterior, and a piece carrying stock
inboard of it carries stock the rib was drawn to use — so it gives that up over
the rib's footprint and the rib roots on the box's plane, which is
`front_top_flank_relief`'s bargain read off the station rather than stated. The
relief is **wider than the rib, and by the zip tie**: what the loop runs down is the
rib's two flanks, from the channel's floor to the body's axis plane, so it is
carried `tie_t + tie_cav_buffer` past each flank and those two lobes are
what the loop comes down. The tap-water pair's two ribs are the pair that take it —
back-top's 9 mm flank occupies the room their zip-tie cavities use, so those two generated
reliefs return only the ribs' footprints to `interior_x` while the nominal flank stays whole
around them.

**And the channel is read back** (`enclosure_assembly.check_tie_channels`,
`tie-channels` on the card). A remainder cannot fail loudly: a wall standing in
one arrives as a rib with a bore and nothing else wrong — the seat still closes on
its body at the slip, the piece is still one watertight solid, the pack still
stands clear. Nothing else on that card measures a hole. So this reading asks for
the zip tie and not the channel: `tie_t` off the bore's own crown, the
cavity's width along the body, the rib's full reach across it, struck off the
station with no root face in it, and it has to come back air.

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
downward — the mouth the zip tie shuts.

**The zip tie is the load path here**, the same bargain the flow-meter anchors make: a
seat that opens downward carries nothing. Barrel and rib make an [84.1 mm](LOOP_WR1110)
loop, past what a 4" tie closes, so this one takes the 6".
`enclosure_assembly.check_body_seated` reads the seat closed on the barrel at the slip
itself, and `check_tube_seated` reads the three run anchors the same way.

## The pump cartridge and its bay

**The pumps leave through one large lower cradle.** `enclosure-pump-cartridge`
(`build_pump_cartridge`) owns the complete removable front wall, the filled body behind it,
the plate stop and both hand pulls. Its filled bearing block rides the bay floor; its exterior
face spans between equal flat 0.5 mm reveals above the sill and below the lintel. Its outer shell
keeps the complete 215 mm enclosure width, including both rounded front corners and side skins,
and its show plane stands [7.35 mm](PUMP_PROUD) proud of the fixed front face. The pumps and
barbs remain [6.15 mm](PUMP_STATION_PROUD) proud; the show plane's additional
[1.2 mm](PUMP_SHOW_GROWTH) is one complete flute depth. Its filled body reaches both cavity
planes, and the front display-support columns have no section anywhere in this withdrawal span.

**Each pump drops into that cradle from Z+.** Two straight wells pass the motor, boss, stamped
bracket, head and tube fittings at every insertion station. Below `cap_split_z`, the head well
closes to `cap_pump_air` around the moulded head. That leaves a continuous cradle land under
the stamped bracket on −Y and both X sides; +Y remains open for the fittings. Pump weight goes
from that bracket directly into the lower cradle and then into the bay floor.

**The second printed piece is the top clamp.** `enclosure-pump-cap`
(`build_pump_cap`) is [167.1 mm](CLAMP_SPAN) across and [61.75 mm](CLAMP_RISE) high. Its Z− face
stands at z [218.75 mm](CLAMP_BASE_Z) on the upper face of each measured
[2 mm](CLAMP_BRACKET_T) stamped bracket. One filled field spans both pump heads from their clean
fore envelope to the aft wall and reaches one common crown at z
[280.5 mm](CLAMP_CROWN_Z), one running reveal below the bay lintel. Two fitted openings wrap
both bosses with the pump case's exact octagonal bore and leave one shoulder around each motor
can. A single
[31.14 mm](CLAMP_ACCESS_W) × [48 mm](CLAMP_ACCESS_RUN) top recess joins the two screw stations;
its retained floor stands at z [224.75 mm](CLAMP_ACCESS_FLOOR_Z), [6 mm](CLAMP_ACCESS_BASE)
above the broad print face. The individual counterbores continue to head seats which keep
[4 mm](CLAMP_HEAD_LAND) of printed land underneath. The two M3s run into heat-set inserts in the
cradle. The clamp carries no show face, plate stop or hand pull.

The service sequence follows those two load paths. Withdraw the assembled cartridge by its
cradle pulls before any Z service; back out the two clamp screws on the withdrawn cartridge;
lift off the clamp; then lift either complete pump straight up. Assembly is the reverse on the
bench, followed by straight Y insertion. `pumps-drop-into-cradle` samples each pump together
with the bracket and full fitting envelope, `top-clamp-drops-on` includes that otherwise-undrawn
steel bracket and the cradle but not the fixed enclosure, and `pump-clamped-in-cradle` reads
printed bearing below and above all three closed bracket sides.

**Each of the four fitting openings begins [12.55 mm](CAP_TUBE_OPEN) wide.** A fitting is
[12.25 mm](CAP_TUBE_PART), the two on each pump stand [57 mm](CAP_TUBE_PITCH) apart, and the
pair's complete outside span is [69.55 mm](CAP_TUBE_SPAN). Each passage carries
[0.15 mm](CAP_TUBE_AIR) running clearance per side. Its circular lower half is centered on the
pump-case barb axis and a shaft continues from that tangent through the complete vertical
insertion path. Each exterior shaft flares at 45° to the wider upper-well edge; each interior
shaft stays at the fitted width. Printed wall remains between and outside the passages.

The pumps and their barb planes stand [6.15 mm](PUMP_STATION_PROUD) forward. The show face
stands one flute depth farther out at [7.35 mm](PUMP_PROUD), without moving the pump wells or
their aft stop. The wells therefore leave the nominal [6 mm](PUMP_PULL_WALL) Y+ wall for the
hand pulls to load while the cartridge releases the four collets.

Nothing latches the cartridge in the enclosure. The four barb tubes gripped in the anchor
tees' branch collets retain it, and the **collet plate** releases them: a laser-cut flat of
1/8" 316 (`enclosure_assembly.build_collet_plate`, `collet-plate.dxf`) standing one rest gap
fore of the four collets in the bay floor. Pull the cradle and the tubes draw the tees forward
until their collet noses land on the steel; the cradle continues, the collets open, and the
tubes pass back through the four plate holes. Push it home and the tubes enter the same collets
while the cradle's aft face lands `cap_kiss` fore of the plate. One hand pulls the cradle and
the other braces the box; fixed wedge cheeks carry the plate's reaction into the side walls.

**THE TEE TRAVELS AND THE VALVE DOES NOT.** `release-travel` offers each anchor tee the
whole stroke and reports what it hits — a motion, where every other bound on that card
reads where a body stands — and all four clear it. The stroke is the rest gap and nothing
more: the nose presses the moment it reaches the steel, the grip opens on contact, the tee
stops there, and the tube draws out of it. What gives over that millimetre and a half is
the tube stub itself, flexing inside the two collets that hold it — the valve standing on
the far end of that stub never moves, and no valve is read here. Its sibling
`check_insertion_backing` reads the other direction, where a tube pushed into a branch
collet drives its tee aft and the step in the wall's bore is what stops it. **That the stub bends is stated and not
derived** — no body in this model has any compliance in it, so no bound reaches that premise;
`check_release_travel`'s docstring is where it is marked and why.

**The cradle's aft face is the stop.** Its body stands through the plate's complete band, and
`pump-cradle-stops-on-plate` reads both the bearing area and the `cap_kiss` air at full seat.

**Both pulls belong to the cradle and surround the tube-centre plane.** Each side pocket is
[18 mm](PULL_DEPTH) deep, [22 mm](PULL_RUN) fore/aft and [48 mm](PULL_RISE) high. Its floor at
z [176.25 mm](PULL_FLOOR_Z) leaves [9.38 mm](PULL_FLOOR_LIGAMENT) of bed-rooted cradle below
it and puts the common tube elevation, z [188.25 mm](PULL_CENTER_Z), 12 mm inside the mouth.
At the deepest fingertip wall the straight vertical opening is [30 mm](PULL_PLUMB) high; its
roof then climbs at 45° to the open flank and reaches z [224.25 mm](PULL_TOP_Z). The opening's
aft face shares the guide-notch plane at y [69.28 mm](PULL_AFT_FACE), so its whole 22 mm run
is exposed; the fore wall is the pulling ledge at y [47.28 mm](PULL_LEDGE). That leaves
[33.28 mm](PULL_TRAVEL) of cartridge withdrawal before the ledge reaches the enclosure front.
Pulling force enters the one load-bearing cradle; the clamp has no separate grip to split the
load or invite a second tug.

## The full-width opening

**One opening spans the entire lower-cradle storey** (`_bay_cut`), from exterior side face to
exterior side face and from the bay floor to the lintel. No fixed `enclosure-front-top` skin,
rim cap or display-support post remains in that band. Two narrow fixed plate guides are added
back only at the aft outer edges and overlap the collet plate's tails; the cartridge carries
one local aft-corner notch round each guide. Each guide is a wedge in plan, standing
[3 mm](PLATE_GUIDE_WEDGE) further fore at the fixed side wall than at its inboard face:
the section carrying the plate's moment is deepest where the cheek is rooted in that wall.
The guide stands aft of the cradle pull and the cartridge carries a local notch around it.
The rake is the guide's whole height, so the cheek is one prism — every face a plane, every
wall vertical and supported, nothing anywhere in it overhanging. The opening runs **past the
collet plate to the tee wall's fore face**, where it ends on printed section rather than on a
free edge.

**The lower cradle's complete exterior spans two flat reveals.** Its proud front, both rounded
corners and both exterior flanks begin 0.5 mm above the flat sill and continue plumb as one
uninterrupted silhouette to 0.5 mm below the lintel, without a bevel, ramp, starter strip or
shelf. Only the grip pockets and two aft guide notches otherwise depart from the outline; the
top clamp sits wholly inside the wells above.

## The bay floor

**Front-top carries a floor across the bay** (`_bay_floor`), from the front wall's
interior face aft past the collet plate, and everything in this storey stands on it.
**It is this piece's first layers.** Front-top beds on the seam plane, so a floor
struck there lies on the bed with nothing under it to hang, and what sets its section
is the only thing over it: the pump cartridge's filled bearing block reaches down to the plane
its own pump reliefs floor on, one millimetre under the heads, and the floor's top is that plane
(`bay_floor_z`). The top is a flat sill. The removable exterior face begins 0.5 mm above it,
while the filled block behind remains seated on it.
`bay-floor-bedded` reads the floor's whole plan solid on the bed, less the two lanes that
pass through it: the rails' own channels and the collet plate's slot.

**One pocket per collar passes the Z seam**, and nothing else does.
Front-bottom's side lip is given up over this whole run (`_flank_lip_drop`) — round both
front corners and back down each flank as far as the tee wall's aft face — so the floor
crosses it wall to wall instead of surrendering one `wall` at each flank. What still
stands over the mouth here is the front column's socket boss on its own plinth, and the
floor opens for that alone. Aft of that run the lip is carried whole and the telescope
is untouched.

The **collet plate goes in through the Z− face**, which is the seam face front-bottom mates
on and the face this piece beds on. Its slot (`_plate_slot`) passes through the floor and opens
on that plane, `plate_slot_slip` off the steel fore and aft at every height, and the mouth
flares [1 mm](PLATE_SLOT_LEAD) at 45° so the steel finds it — a lead that leans in as the print
climbs off the bed. **Across, the slot is one rectangle for its whole height**: the steel plus
0.2 mm air at each end, stopping at x = ±100.2. A 4.3 mm printed return remains between either
slot end and the cavity-side wall, followed by the enclosure's 3 mm outer wall. The floor holds
the plate fore and aft and holds it back not at all; the steel goes clean through and comes up
until its own **top edge** lands a storey higher. `bay-floor-bedded` reads the floor whole on
the bed and that land whole over the edge.

**The wall over the steel is what stops it** (`_plate_cap`). The lane above the seated top
edge is filled from that edge to the bay's ceiling at [281 mm](PLATE_CAP_TOP).
[1 mm](PLATE_CAP_LAND) of that is flat, taken off the tee wall's fore face at
[216.5 mm](PLATE_CAP_Z): the top edge comes up onto it and stops, and **that land is the
plate's Z datum** — the only stop in this joint, and the reason the outline needs no shoulder.
Fore of the land the underside **rakes at 45°** to `plate_guide_fore_y`, the same plane the two
fixed cheeks keep for their whole height, because the lane under it is air at print time and a
square ceiling `PLATE_T` wide would be a ledge hanging off the tee wall for the width of the
machine. Its complete front edge holds the nominal corbel height z
[221.865 mm](PLATE_CAP_FORE_Z), continuously across X; the forward pump station leaves the
loaded brackets 0.78 mm clear of that edge. The steel's flat stop land and both fixed cheeks
remain whole, and the pump cartridge's back lands `cap_kiss` fore of printed wall above and
steel below.

**The guides are two stationary single prisms** (`_plate_fore_guides`) standing fore of the
plate's outer tails. Immediately outside either slot end at x = ±100.2, each prism turns aft
past the steel and fills the complete 4.3 mm band to the cavity-side wall, then fuses into the
3 mm outer wall. That return stands from the bay floor through the whole storey, with no shelf
or open column above it. The tee wall is the channel's aft face and the guides its fore face,
so the steel cannot pitch forward when the four collet noses load it after the pump cartridge
has begun moving. Each cheek bears on 10 mm of the plate's Y− face, is a wedge in plan
[3 mm](PLATE_GUIDE_WEDGE) deeper at the fixed wall than at its inboard face, and **stands the
whole storey** — to the same ceiling the cap does, so it is a post between two slabs rather
than a fin off the floor, and the flank opening gets an aft jamb for its full height. Over
each tail its head carries the cap's own land out to the side wall, spanning
`PLATE_T + plate_slot_slip` between two standing walls.

**The steel is a rectangle.** The band's bottom is the **seam plane** — it fills the slot to
its mouth — and its top is whatever puts the four collet holes **centred** in the band
(`plate-holes-centred`). Each end stands [4.5 mm](PLATE_STEP_IN) off its cavity-side wall at
**every** height, putting the steel at x = ±100.0 and leaving 10 mm of each unperforated tail
on its fixed Y− cheek. **What locates the steel across is the bay floor's constant-width
slot**, one `plate_slot_slip` off each end from the mouth to the cap. The plate has four
corners and four holes; `build_collet_plate` writes that outline into `collet-plate.dxf`.

The **wall behind the steel is struck on the same four collets** (`_tee_wall`).
Front-top stands a section of its own material aft of the plate, wall to wall and the
whole height of the bay, with one bore per anchor tee. A bore closes on the round collar
that tee's branch arm carries — `TEE_WALL_BORE_SLIP` on the radius, a running fit and
not a grip — so a tee is located in X and Z by printed material and free in Y, which is
the one direction the release moves it. The wall's fore face IS the steel's aft face,
one figure with the plate (`enclosure_assembly.collet_plate_spec`), so every bore is
stopped at its fore mouth by steel and the nose that lands there lands on steel; the
plate bears back on the wall across its whole face. Its aft face stands one whole stroke
plus `TEE_WALL_BODY_AIR` fore of the tee's own body, so at the end of the stroke there is
still air behind the tee — depth past that plane is the tee's and not the wall's to take.
The collar-clear bore therefore continues through that broad face instead of leaving a
1.666 mm annular diaphragm. Two side pads per tee provide the aft insertion stop: each is
exactly 3 mm wide and 3 mm deep, rises from the front-top bed plane, and begins 0.270 mm aft
of the collar's nominal inboard plane. That setback clears the real collar/arm blend over
the complete release and leaves about 0.057 mm of insertion take-up before the collar lands.
The arm passage is recut through them with 0.050 mm radial air, leaving the purchased
collar's radial bite on two full-section printed columns. The steel stops the tee foreward
during release; these pads stop it aft while a tube is seated.

**That wall is also the bay's back.** Over the plate's own band the steel closes the
bay; above and below it this wall does, so what stands behind the berth the pump cartridge
leaves is a wall rather than the cavity. The Z seam passes it the way it passes the
floor, on the rail channels' own deep lane (`_z_rail_channels`).

The **bay** is the opening all that leaves through (`_bay_cut`): exterior side face to exterior
side face, from the floor's own top up past the motor cans' crowns (`pump_bay`, struck off the
placed cans), and aft to the steel. The flat sill runs wall to wall; the lintel over the opening
carries the facet and the display on a stated ligament (`bay-under-display`).
`heads-sweep-out` reads each head's path to the front against the piece it passes
through, and `pump-cartridge-sweep-out` reads the complete lower-cradle and top-clamp envelopes.
The removable shell follows the enclosure's rounded plan with its front plane
[7.35 mm](PUMP_PROUD) proud while the pumps remain [6.15 mm](PUMP_STATION_PROUD) proud and the
filled block behind it reaches both cavity planes.
Front-bottom's front lip drops across the whole flat span
(`_front_flat_lip_drop`) — the floor stands in that band and the heads run down through
it — and the front wall below keeps its single `front_wall` section from slab to seam.
The face keeps [0.5 mm](PUMP_CARTRIDGE_CLEARANCE) of Z clearance above the sill and below the
lintel. Its complete front, rounded corners and exterior flanks stand plumb between those two
flat gaps with no taper.

**The fixed front wall is `front_wall` thick and grows inward.** The removable pump face is the
load-bearing exception: it stands [7.35 mm](PUMP_PROUD) proud with
[5.1 mm](PUMP_FACE_SKIN) of smooth stock over each lower head relief and
[6 mm](PUMP_PULL_WALL) behind the seated pump wells. Over the upper insertion wells its smooth
section is [4.305 mm](PUMP_UPPER_SMOOTH_SKIN); the same uninterrupted full-depth flute field as
the enclosure leaves [3.105 mm](PUMP_UPPER_FLUTED_SKIN) in the finished printable mesh. What
noses into the section gets a 45°-chamfered relief (`_front_relief_cuts`): one stated
pocket across the compressor, floored on its own kiss, and one pocket per pump in the
lower cradle's face, floored where the pump head and bracket insertion well puts its root
(`pump_relief_floor`). The compressor is the only body in the refrigeration stratum
standing fore of the wall's interior plane — the condenser bears on that plane through
its rails and the fuse clamp stands clear behind it — so the wall keeps its full section
across the rest of the front. `box-front` reads every placed body against the relieved
surface, region by region.

## Pump clamp field

The geometry in `printed-parts/enclosure/pump-tray/` supplies the two fitted openings in the top
clamp. The clamp is one rectangular field over both pumps, from each stamped bracket's upper
face to the common crown below the bay lintel. The exact pump-case octagon and motor-can bore
are cut from it, leaving the case-derived locating walls, pressing lands and can shoulders
wherever a pump does not occupy the material. It is one printed `enclosure-pump-cap`, not
separate collars or fastener pieces.

**The bracket divides bearing from location.** The lower cradle bears under three sides of the
68.6 mm stamped bracket, and the clamp's complete broad base lands on its upper face. The
bracket remains wholly below the printed cap: every cap wall grows directly from one common
Z− plane, with no shallow pocket ceiling or narrow perimeter foot. Above that steel, the
case-derived octagon engages the white boss over its complete run and the shoulder surrounds
the can. Thus the cradle takes weight, the clamp prevents lift, and the octagon fixes X, Y and
yaw. With the cartridge withdrawn, the clamp's vertical path keeps
[4.305 mm](CLAMP_FRONT_SKIN) of smooth cradle skin ahead of its fore face. A
[8.68 mm](CLAMP_AFT_WALL) wall remains aft of each octagon to locate the boss
against +Y.

**Two M3 close one clamp onto one cradle.** Both screw heads are accessible from above in the
single joined centre recess. Their heat-set inserts open upward in the cradle spine. Once the
complete cartridge is withdrawn in Y, back both screws out and the entire clamp lifts in Z;
either pump then follows through the same straight well. The cradle's centre clearance spans
the clamp's complete fore/aft depth, so the filled field has one unobstructed bench-service
path. No zip tie or hidden underside fastener closes a pump.

The fitted opening's exact source dimensions and section readings are in
[`pump-tray/README.md`](/hardware/printed-parts/enclosure/pump-tray/README.md). The enclosure
uses those case profiles to shape the broad pressing base and cut the boss and can rooms from
one service clamp.

**The lower cradle prints on its Z− floor.** Its filled bearing block begins on that bed; the
proud front, rounded corners and both flank skins begin 0.5 mm above it and rise plumb. The two
pull roofs climb at 45° and the pump wells remain open above. The top clamp's complete
field begins on one broad Z− bed face. Its only internal down-facing transitions are the two
functional boss-to-can shoulders, 19 mm above that face and open through the fitted bores for
support removal. Both screw heads remain accessible from the top.

`clamp-locates-pumps` reads the octagonal collar against each drawn boss;
`cradle-pulls-on-tube-axis` reads open hand pockets and whole pulling ledges; and
`pump-cartridge-lower-cradle` verifies that both exported pieces are single solids and the
cradle carries the foremost show face.

## Display housing

A flat 45° facet chamfers the **whole top-front arris**, wall to wall, and carries
the [Waveshare ESP32-S3-Touch-LCD-4.3B enclosure display](/hardware/reference/waveshare-43b-display/)
facing up-and-forward (−Y front / +Z up) toward the standing user. The display is
**centred** on it: the box is 223 mm wide and the glass 113.5, so what is left is
roughly 55 mm of flat 45° face either side of the window.

Spending the whole width on it costs nothing — the chamfer is inside the box's own
silhouette, so that corner is unpackable at any width — and the geometry gets
simpler for it. There is no end wall closing a recess, no shoulder where a window
stops, and no bed relief on the arris a shoulder would raise. The window's lateral
size is the box's; `display_facet_x` is what the *glass plus its buffer* needs —
[158 mm](DISPLAY_FACET_X) × [87.5 mm](DISPLAY_FACET_SLOPE) up the slope — which is
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

**One line in that soffit is not a face and does not lay on itself.** The PCB
through-hole's up-slope end wall breaks out of the back plane, and the two surfaces
meeting there both point *down* — so the line is the bottom vertex of a wedge. Either
side of it is 45° and lays itself once the line exists; the line is the one bead on this
piece with nothing under it, and it runs the hole's full [106 mm](RIDGE_LEN). It stands
in the cavity behind the housing, which is closed on five sides by the time the piece
leaves the bed, so it cannot be reached with support and is built instead.

A [3 mm](RIDGE_WALL_T) rib (`_ridge_wall`) carries it — from the tee wall's crown up to
that same back plane, **wall to wall**, under the line over the whole of it. **Its fore face
is two planes the box already has and no third one**: below the jog, the bay's own back
carried straight up off the crown, so the storey over the bay reads as the same plane the
bay does; above it, the hole's own end wall carried on past the soffit, which is 45° and is
the plane the display's body already lies against — the rib presents the part the surface
its hole presents, and no new fit. Where the two meet is read, not chosen. The jog is also
what keeps the rib clear: run straight up it would stand in the funnel's throat, and slanted
straight from crown to line it would run into the display's body where that stands proud
of the soffit. `ridge-carried` reads the drop from the line to the material beneath it.

**Running it to the flanks closes the storey, and one thing crosses.** The rib lands in the
side walls rather than ending in free air over the tee wall's crown, which leaves it the only
section between the bay's storey and the cavity behind it — so the enclosure display's loom is
bored through it. SIG-7 is four 22 AWG in the 1/2" PET expandable braid, and a braid of that
kind is bought by its nominal and passes at what it *opens* to, so the bore is the opened
figure — Ø[19.05 mm](CABLE_BORE) — and a loom never has to be squeezed through one. It locates
nothing and carries nothing; the loom is dressed after it is through. The bore stands on the
box's centreline at the middle of the rib's straight run, which is where the display's back is
and where the loom leaves it, and it is teardropped for the reason every bore on Y in this
piece is: the piece beds on Z, so a hole on Y lies horizontal and its crown would otherwise be
laid across the chord under it.

## Funnel opening

One rectangular opening spans the top wall **directly behind the display
housing**, where the removable silicone funnel
([`../../zone-c/funnel/`](/hardware/printed-parts/zone-c/funnel/))
drops in — its straight chute press-fitting the opening, its whole floor one
ramp falling to the centred spout, its flat brim resting on the wall frame left
around the cut.

The funnel is a static placed part: the opening is cut at its collar
(`_funnel_hole` reads the funnel's own dims at `enclosure_assembly.funnel_centre()`), so
funnel and hole cannot drift apart. The frame that cut leaves is bounded by the
facet's own back plane ahead (the collar's front edge stands on it), the ±X
boss chains either side, and the +Y wall of back-top behind — and the collar is measured
one `brim_margin` inside it on all four sides at once, so a placement that crowds an
edge is a red row naming the edge and the margin it is short. That margin
is the brim's landing: it is wider than the flange's overhang, so a full
overhang's width of wall remains outboard of the brim edge the whole way around.

The funnel stands on the box's own stated **`funnel_front_y`** and takes the top
wall's full width, because the facet in front of it spans the machine and there is
nothing beside it to leave room for. The frame's two side strips on the front top are
corbelled (`_ceiling_corbels`): a 45° underside off each ±X wall to nothing at the
opening's edge. Over the seam's ceiling tongue a funnel-side ramp rises from the top
collar's chain face and a wall-side ramp rises from the plug tip to the socket cap, so
the complete tongue and every ceiling layer land on the one below. THE FUNNEL IS WHERE
THE USER POURS, so that
plane stands as far forward as the wall lets it — which is the display housing's own
back cut — and what fences THAT is the brim rather than the throat: the flange
overhangs the collar and has to land on top wall, and the top wall begins at the
facet's own arris. `funnel-brim-lands` is the reading, and the ledge the facet
leaves the throat is read back as a bound on the frame above. The funnel reaches aft for the plan area its
capacity needs — which puts it **across the Y seam**. Both halves take their share
of the cut and the collar bridges it; what the seam gives up there is its top-wall
lip over the hole's span, which the mouth shelf's own relief already accounts for.

## back-top's ceiling

back-top has no throat, so its ceiling would be a flat slab — the whole width of
the machine by the whole depth of the back half — laid [195 mm](PIECE_H) up over
the open service bay on a piece that prints mouth-down. It is not printed in this
piece at all. What back-top keeps is **two side strips**, [19 mm](CEILING_STRIP)
wide, and between them the [159 mm](CEILING_PANEL_W) channel the
[ceiling panel](/hardware/printed-parts/enclosure/ceiling-panel/README.md) fills
— a separate part, printed flat on the bed and **slid in** through the Y-seam
mouth before back-top meets another quadrant.

The exterior top remains z 355 and the rear storey's established pack lane
remains z 352. The fixed strips carry a [6 mm](BACK_TOP_CEILING_T) physical
section inward to z 349, while the removable panel carries an
[11 mm](CEILING_PANEL_T) structural envelope inward to z 344. Those are
piece-owned faces: no body, port, anchor or exterior plane moves to fund them.
The fixed corbel is consequently the established 45° wedge plus an exact
[3 mm](BACK_TOP_CEILING_GROWTH) parallel shell below it.

Each strip is **corbelled** the way front-top's two are either side of the throat
(`_ceiling_corbels`): a 45° underside rising off the flank face to nothing at the
panel's edge, so every ceiling layer lands on the one below it. The corbel is
therefore **deepest at the wall and thinnest at the panel's edge** — which is the
wrong way round for the rear storey, because the wall is exactly where that
storey's furniture stands.

So the strip carries **reliefs**, stated as `back_top_ceiling_reliefs` and read
back by `ceiling_corbel_at(x, y)` — the same shape `back_top_wall_reliefs` and
`back_wall_t_at` take one storey down, keyed on (x, y) rather than (x, z). A row
names the fitting, the flank, the depth band it covers, and **the run band it
gives up** — everything from `keep` out to `out`. Inboard of `keep` and outboard
of `out` the strip keeps its corbel; between them it is the top wall's own section
alone and takes print support unless that short row carries a stated two-sided Y gable.

**A relief is a band because a body is a band.** Where a fitting stands hard
against the panel's edge the two are the same thing: `out` is the strip's whole
run, and what is left is the wedge's thin end — which is exactly what a body a
millimetre under the ceiling leaves room for. Where a body stands in the **middle**
of the strip, taking everything outboard of it as well throws away the one part of
the corbel that roots on the flank and carries itself, and leaves the strip's whole
width hanging.

The rows are measured against the placed solids and not against their boxes, and
the difference is most of what they say — a strip read off boxes is a strip with no
corbel left in it. The raised relay gives up the +X strip from
[3 mm](RELAY_CEILING_KEEP) of run outward over its band, standing 2.45 mm off the crown
under it. The ground bar's shorter band gives up the X wedge around the purchased stack,
then closes again on two 45° planes from the intact wall corbel at its Y ends to a ridge over
the stack's centre. The stack stands 0.25 mm below the nominal stack floor and keeps more than
one millimetre of exact air from those planes, so there is no horizontal support roof over it.
The C14 keeps the complete established +X wedge: its shared X datum places the
moulded rim about one millimetre inboard of that corbel, while its Z remains on
the top port row. Its moulding, the relay, the ground stack, the ASSE body and
the water bulkhead reach only the new three-millimetre shell.
`ceiling_growth_reliefs` withholds that shell over each exact placed-body plan
plus 1 mm, clipped to the fixed strip, while leaving
the older wedge and its existing run-band/gable treatment intact. At the C14
this leaves exactly 1 mm of air; the relay retains 2 mm and the ground stack's
pre-existing closest feature retains its same 0.682 mm, while its printable
gable remains 1.162 mm clear.

**The tap-water chain takes four rows**, because what it occupies is four different
things. Against the full wedge, the metal inside the corbel is run 1.50…14.09 over
y 354…394 — the Multiplex barrel, its crown one `DECK_CEILING_CLEAR` under the
ceiling — and run 4.67…5.42 over y 394…424, three quarters of a millimetre of run
in a strip 19 wide. **1,275 mm³ of a 12,816 mm³ established corbel, and none of it outboard of
run 14.09.** So the outboard run goes back, and those two rows give up 0…16 and 0…7.

What still gives up the whole run is **the two tie bands**. Each zip tie is a closed
loop that comes west over the chain's top flat in the `DECK_CEILING_CLEAR` lane and
drops into the cavity through the anchor's back — and that cavity's top mouth is out
at the wall (`_asse_tie_cavity`), so a corbel standing on the outboard run would roof
the one opening the zip tie has. `_asse_cradle` reads those two rows back against the
ties it was handed, so a band that moves off its zip tie says so instead of closing
over it.

**The dado** is cut in each strip's inboard face on the section the panel states
(`ceiling_panel.dado`), and it runs from the open Y− mouth aft: the panel is slid
the length of the piece with its tongues in these two grooves. It is cut open at
both ends — a millimetre into the field at its mouth, its own depth into the back
wall at its blind end — because a groove ending exactly on either plane leaves the
strip and the thing it runs out on meeting along a line.

The current tongue is [6 mm](CEILING_TONGUE_T) square and its dado is
[6.15 mm](CEILING_DADO_DEPTH) deep. The ground-stack gable begins on the fixed
side of that deeper blind wall; allowing the old roof to extend into the moving
lane would merely let the dado cutter erase its inboard edge. Both complete
body-free rail bands are read after the cut by `ceiling-rail-capture`, including
the lower and upper ligaments and X/Z capture in the finished solids.

**The ramp is the field's, and the last `depth` is a run-out.** Beside the field the
dado's roof rises to the show face at the mouth, and both the rise and the millimetre
of overrun past it are the panel's own lane — this piece has no top wall inboard of
that plane to carry either. Aft of the field it has one: the blind end runs its own
depth into the +Y wall, where the section is continuous across the mouth plane, so
there is no free-standing lip to feather and nothing to stand a ramp under. A ramp cut
there lands its apex in the middle of the show face rather than on its edge, which is
three faces on one line and a mesh a slicer refuses; an overrun cut there opens a slot
straight through the top wall. So the last `depth` is **the groove's run-out**, and it
takes the blind end's own section carried square through — floor to roof, with the rest
of the top wall bridging the mouth plane over it.

**Two transverse keepers close the only direction the dado leaves open.** The
long grooves already carry the panel in X and Z and the +Y wall stops it at home,
so a headless M3 cross-pin stands immediately ahead of each tongue end and blocks
Y− withdrawal directly. The panel slides through first, with both stations empty;
then each M3×12 is driven OUTBOARD from the empty field into a horizontal ruthex
M3 short buried in the fixed corbel.

The insert's guide retains its established inboard face inside the deeper dado
and steps down to its Ø4 knurl bore only where the existing 45° wedge has a full
`boss_ligament` around its lower bearing land. That extra guide length clears the
small roof wedge the longer blind wall otherwise leaves over the round keeper,
without moving the keeper axis, insert or screw end. Both horizontal cuts retain
their complete nominal circles and open
above them into the same 36° tangent teardrop used by the enclosure's other X-axis
bores, so neither leaves a circular crown for support. At least three 0.24 mm PET-GF
layers remain over the insert roof. No boss, pier or pad is fused under the ceiling.
The moving panel carries no socket and no bore. One millimetre of empty bore beyond
the insert keeps the cup point off the blind PET-GF end. In service the tongue bears
on the steel pin and the pin bears in the fixed strip around its own short tunnel;
neither appliance show face is opened.
`ceiling-panel-section` reads the 11 mm envelope, complete show skin, all nine
body roofs and all three tie-approach pockets. `back-top-ceiling-growth` reads
both clean fixed shells and the three exact growth-only body yields.
`ceiling-panel-slides-in` reads the continuous field-and-rail sweep plus the six
hanging furniture solids at one-millimetre stations before the pins exist, and
`ceiling-dado-mouth-keepers` then proves both pins clear at home and catch their
own tongue over 5.60 mm in X and 2.00 mm in Z after the dado's 0.15 mm fore air
is spent, without moving their established world coordinates.

**Everything rooted on the ceiling over that field hangs off the panel**: the
flow meter's two anchors and the three ribs bored for `carb-1`,
`co2-2` and the WR1110's barrel. `ceiling_stations` is the one call that splits
them, and both parts read it, so neither can grow a rib the other grew too.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ the four `enclosure-*.step` pieces + `enclosure.step`. Wall, seam, boss, and
facet constants are at the top of `enclosure.py`. Prints the facet size, the
cross-pin levels each side wall ended up with, each piece's envelope vs. the H2C
bed, every piece-pair's slip fit, and the cold-core clearance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
