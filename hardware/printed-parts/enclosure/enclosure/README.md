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
and the pump heads run down through it on their way out, so the
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
so the square registration faces and full insertion travel remain while neither half leaves a
support contact in the pin slot. Its square pass envelope stays whole under one flat roof
at the envelope's own ceiling, leaving the socket collar's complete structural stock above it.
On back-top, which prints ceiling-down, the upper pin's top face is a supported flat the
pin's own width, reached from the slab.
Both ends are fenced — nearer its wall, the lower collar's
carve leaves a corner of the front lip in the back half's register; further from it, the upper
collar's 45° underside comes down the −X wall into `fluid-1`'s lane.

Each cross-pin is sized to its job. Reading an M3×10 screw outboard→inboard from
the ±X exterior: a Ø6.15 mm head counterbore, then [5 mm](SEAM_PIN_SHANK) of pin body
ending exactly on the [9 mm](BACK_SEAM_FLANK_T) back flank's physical interior face, then a
[5 mm](SEAM_HEATSET_DEPTH) heat-set pilot, then a one-wall cap. The pilot holds the complete
4 mm insert and [1 mm](SEAM_HEATSET_RELIEF) of screw-tip relief, so the blind end and cap stay
on the M3×10 stack's datum while the plug and its corbel meet the wall flush. The counterbore
retains that complete circular pass and bearing envelope, while its unsupported crown continues
on two tangent [36°](TEARDROP_ROOF) roof planes. The four head pockets therefore close without
isolated support towers.

- **Receiving piece = pin** (the back pieces): a [9.9 mm](PLUG_DIA) SQUARE prism (the shank
  + one wall each side, *not* the head — the head sits in the wall counterbore) from the
  exterior to the common full-thickness flank face, seating in the socket's slot and carrying
  aft into that flank.
- **Lip piece = socket** (the front pieces): a collar slotted
  [10.2 mm](SOCKET_BORE) square to take that pin as a slide fit, with the ruthex M3
  heat-set (Ø4.0 × 4.0 body in its [5 mm](SEAM_HEATSET_DEPTH) pilot) capped at its deep
  inboard end.

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
along both whole runs** — [100 mm](RAIL_RUN_FRONT) per flank on the front column,
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

**Every face of the joint prints at its own piece's rule, and the two columns' catches
differ.** On the front column the catch faces are square: the head's underside is the joint's
one down-looking flat, an abrupt ledge at the top of a piece that prints floor-down, and the
arm's base falls back to the lip's underwall on a 45° under-flare; front-top's foot presents a
flat caught face that looks print-up on its mouth-down print. On the back column the catch is a
**ridge in a groove** (`hook_apex_flat`): back-top prints on its ceiling, so its caught face
looks print-down, and instead of a flat cantilevered the head's width over the notch the foot
carries a 45° groove down the run with a [1 mm](HOOK_APEX_FLAT) land at its apex, and
back-bottom's head a matching ridge at least one `slide_slip` inside it on every face. The catch's
flanks are slopes each print lays on the layer below it; its two lands are the flats that remain —
the groove's, a 1.2 mm bridge between its flanks on back-top, and the ridge's, a 1 mm
supported face on floor-down back-bottom where the head's whole 5 mm underside was one before.
A lift lands the ridge in the groove on both flanks at once with the two flanks' side loads
cancelling, and `z-slide-back-catch` reads the engagement. On either column the notch is an open rebate in the wall's own inboard face —
no cavity closes over the bed — and where the channel's lane does cut interior bulk, a
**gabled roof** of two 45° faces closes it. Every sliding face is vertical, horizontal or that
45°, and the top's outer skin keeps its full `wall` of flute backing down to the mouth.

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
board, two relays and ground stack: 17 in all. back-top beds on its ceiling's outer face, so its
print-up is machine −Z (`enclosure.print_up`) and on this piece print-down is machine-up: a face
that looks up in the machine is the face the slicer has to carry, and every boss is carried from
above. Each stem is a D in its mounting plane — the round crown keeps the M3 insert annulus
compact, and its 7 mm flat chord, on the machine-top side of the hole, gives a full-width 45°
corbel one continuous print-down plane to carry. The corbel stands on that chord and climbs to
the wall at 45°, so every layer of it lies on the one before. The D section runs all the way to
the body's own mounting face, so no round pipe is left bridging between a generic support block
and the part.

`enclosure_assembly.wall_mounts` offers that corbel, struck for back-top's print-up, all the way
to every mounting face and intersects the offered material with the installed pack. Where a body
crosses the offered wedge, the wedge is held back to one millimetre past that body's exact
envelope; where the body crosses it to within that clearance of the wall, no wedge stands over
the blocker itself, and what is clear beside it is a wing only where `enclosure.east_boss_wings`
lets one stand — a wing at each end of the span roots a bridge between them, and a stub carrying
the minority of the span stands down so the chord is offered whole. The two relays' holes come
in pairs 13 mm apart at either end of each board, and each pair stands in one flat-topped bar
with two bores, carried on its upper hole's corbel where the pair stands one over the other and
on one wedge across the bar's span where it stands side by side; the other nine stems stay
D-shaped and whole across their holes. `east-boss-corbels` reads all 17 stations back against
the installed bodies and records the full-width, split and held-back populations.

The five Wago wells on the same wall are carried the same way (`enclosure._side_wells`). The
row's tower stands its 45° wedge on its machine-top face, climbing to the wall and cut off flat
at the ceiling slab's interior face (`enclosure.back_top_ceiling_face`), which is the piece's
own stock. Each pocket keeps its two `wago_roof_tab` tabs on its floor, with the 45° ramp folded
on the wall between them, and the complete `wago_well_wall` section on its roof; the lug rests
on the two tabs and the wall's press fit locates it.

## Condenser cradle

The condenser's four sheet flanges are the block's whole purchase. Its two fore flanges slide
into rails on the front wall; its two aft holes screw into fingers on a standing fin at the +X
wall. The base rail and lower finger run to the floor slab. The crown rail and upper finger do
not: each carries its entire down-facing plane on a 45° corbel rooted on the wall or fin it grows
from (`_cond_cradle_corbel`, `_cond_mount_corbel`).

The crown wedge is only the rail's [3 mm](COND_SLOT_GRIP) reach. The aft wedge is longer, but it
lies wholly in the donor block's open end recess and stops on the fin's west face. The condenser stays fixed and the closer
one keeps `cond_mount_clear` of assembly air.

Each fore-flange groove keeps its exact [1 mm](COND_SLOT_OPEN) opening at the seated wall stop,
then its roof rises toward the bay at 45° and runs through the rail crown at the insertion mouth.
The sheet datum and grip are unchanged, while no flat one-millimetre roof is printed over the
rail below it.

## The box closes in four motions

The slides fix the order, and the order is the service story backwards. **Front column**,
on the bench: the refrigeration stratum seats in front-bottom, and front-top — carrying the
flavour pack made up into its trays and tee wall — slides AFT onto it, in from the front. **Back column**,
on the bench, empty: back-top — carrying the chain, the meter, the ceiling's anchors and the
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
direction the core could go.

**The core enters from ahead, and only from ahead.** The back column closes empty — its
+Y wall cannot pass over a seated core — so the core rides in through the open Y-seam
mouth, aft over the slab to its seat, the crown sliding under the brackets' eased feet. The front assembly then slides aft onto it and
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
[355.58 mm](STOREY_RUN) over the storey at z [177.8..283.5 mm](STOREY_BAND). The two open flanks
and the lower tee face advance the phase but carry no cutter: the former are air, the latter is
berthed or hidden, and the upper closure face stands on another Y plane. The datum remains
**x = 0** and the pitch remains [5.1285 mm](FLUTE_PITCH), so both ledges retain the machine's
inside phase. Each real surface is open; its two ends are edges like any other and the field
ramps to zero on them, as it does at both Z ends of the band, which keeps cutter caps off every
mouth and window arris.

**And a body berthed in the room is an edge too.** Inside a storey the piece has material at
the rail in places the pump cartridge stands in front of, and a face another body beds
against is not one anybody finishes. `flute_skin._shadow_mask` asks, at every station, whether
a berthed body stands between that face and the storey's mouth — the same question the show
mask asks, asked of the other bodies — so the tee wall carries flutes only where the pump cartridge
leaves it visible, and the plate's own bearing band is left plain. Nothing is listed: the
lower cradle and top clamp are what the assembly stands there; the collet plate is part of front-top.

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
less than one 3 mm wall to that chute stay solid through the courses the chute reaches, and vent
like any other above it, there being no chute up there to leave a strip against; the chute is not
widened into a vent, and no 1.261 or 1.981 mm strip survives between the two openings. All
[85](VENT_RUNS_IN) realized intake openings are the full [24.5 mm](VENT_SHORTEST) segment;
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
| −X intake | [22](VENT_SLOTS_IN) | [85](VENT_RUNS_IN) | [2.0285 mm](VENT_MEAS_MULLION) | [24.5 mm](VENT_TOWER_IN) | [60.5 cm²](VENT_OPEN_IN) |
| +X exhaust | [22](VENT_SLOTS_OUT) | [88](VENT_RUNS_OUT) | [2.0285 mm](VENT_MEAS_MULLION) | [24.5 mm](VENT_TOWER_OUT) | [62.6 cm²](VENT_OPEN_OUT) |

Both read off the built piece at the flank's mid-section, over the fan's own band. A pierced field
is [60.4 %](VENT_OPEN_PCT) open where every slot runs; the readings above are what the band came
out at with the transoms, the hips and the intake's rail in it. The tallest opening on either flank is [24.5 mm](VENT_TOWER) on a
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
- A support's root is read against the face the piece prints on. On a piece whose cavity opens
  toward the bed — the bottoms on their floors, front-top on its mouth — a support rooted on
  the print bed is preferred irrespective of its length and a root on model material is a
  defect of its own, so a short bed-rooted support and a long material-rooted support are
  reported as two different compromises rather than traded against one another invisibly.
  On back-top the cavity opens away from the bed: the ceiling slab's interior face is the
  root every interior support has, a hidden flat the piece lays down in its first layers, and
  a root there is that piece's own bed. Supports that start on material are expected on it,
  and the ledger names each retained body by the flat it carries and why that flat is flat.

A candidate which removes a whole separate support that was both short and rooted on model
material wins on every count at once, and is the strongest fix the audit can name.

Down-facing geometry is changed before support is accepted. A corbel, chamfer or tangent
teardrop follows the exact feature it carries and reaches its whole supported face; it is not a
generic triangle merely placed nearby. A corbel that reaches only part of its face is read by
what it leaves: the remainder is a supported face still, and the corbel's end is one more
printed wall that support has to come away from. A partial corbel therefore stands where it
leaves less than it carries, or where a second wing at the span's other end roots a bridge
between the two; a stub carrying the minority stands down, and the face is offered whole with
nothing beside whatever carries it. Relay #2's upper bar keeps a 2.5 mm wing at each end and
bridges the 15 mm between them; the main board's boss at y 241 offered 1.53 mm of wing on a
7 mm floor and keeps none (`enclosure.east_boss_wings`). A feature on a wall preferentially
ramps along that wall's normal — an X ramp from an X wall and a Y ramp from a Y wall — because the wall is the
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
git show 366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf \
  > /tmp/enclosure-back-top-petgf.3mf
python3 hardware/scripts/enclosure_support_audit.py \
  --piece enclosure-back-top --slice-current \
  --model hardware/printed-parts/enclosure/enclosure/enclosure-back-top.stl \
  --profile /tmp/enclosure-back-top-petgf.3mf \
  --profile-label git:366d54ba040ecc7f1465c200e63e52410ffc0d4c:hardware/printed-parts/enclosure/enclosure/enclosure-back-top-petgf.3mf \
  --json-out hardware/printed-parts/enclosure/enclosure/enclosure-back-top.support-audit.json
```

The result carries the model, profile and derived G-code hashes, the slicer's support settings,
all interface islands and both plate and CAD coordinates. The ledger supplies the human reason
for each connected body that remains.

**All six printable pieces are audited, each through a production project of its own.** The 3MF
snapshots are retained only in Git history — five at `aef8f43c0eb3eef9c6525ecaa0a1ca52c5b8c71a` and
back-top's ceiling-down project at `366d54ba040ecc7f1465c200e63e52410ffc0d4c`; they
are evidence inputs rather than current files in this directory. No piece is re-oriented to be
read: each beds on the face its own relief scheme is struck on — the Z− face on five of them,
the ceiling's show face on back-top (`enclosure.print_up`), whose project carries that half
turn in its build item. `enclosure-front-bottom-petgf.3mf` and `enclosure-back-bottom-petgf.3mf` carry the PET-GF15
exterior settings of `enclosure-front-top-petgf.3mf` around their own mesh — the same clones
`enclosure-pump-cap-petgf.3mf` and `enclosure-pump-cartridge-petgf.3mf` are.
`enclosure-back-top-petgf.3mf` is the one piece on its own 0.24 mm process, and the one whose build item carries a half turn about X. What BambuStudio
02.08.02.61 emits after substituting the current meshes into those history snapshots:

| piece | bodies | interface islands | root | shortest build-up |
|---|---|---|---|---|
| `enclosure-pump-cartridge` | 0 | 0 | — | — |
| `enclosure-pump-cap` | 2 | 2 | bed | 18.40 mm |
| `enclosure-front-top` | 3 | 4 | bed | 55.60 mm |
| `enclosure-back-bottom` | 2 | 3 | 1 bed, **1 model** | **6.00 mm** |
| `enclosure-front-bottom` | 4 | 4 | 2 bed, **2 model** | **8.00 mm** |
| `enclosure-back-top` | 11 | 28 | 6 bed, **5 model** | **1.44 mm** |

**One piece slices clean, and five bodies are the campaign's open work.**
`enclosure-pump-cartridge` emits no support at all. On the pump cap and front-top, every body
roots on the print bed and stands 18 mm or more before it
touches the model, which is past the point the build-up reading saturates at; so do front-bottom's two lower
Y-seam socket collar crowns, at 28.20 mm. The bottom-quadrant exceptions are one feature standing
on all four flanks: the **Z seam's slide-head catch**, the joint's one down-looking flat and the
whole of its bearing against lift. Back-bottom's west catch reaches the bed from outside its
flank through the 12 mm PRV passage that crosses it — the same opening that splits that catch
into two interface islands. The other three have no such lane and root on the arm's own 45°
under-flare **8.00 mm** below the catch they carry: front-bottom's pair and back-bottom's east
catch are the only material-rooted bodies outside the 15 mm band.

Back-top prints on its ceiling, so what a support reaches there is the set of faces that look print-down and cannot carry themselves: the drip pan's berth floor and its sleeve's lid, the nameplate bar's top and the pocket's lower rim, the upper Y-seam pins' tops, the C14's aperture and flange-pocket floors, the keystone pocket's floor, the tap-water ribs' tie-band flanks and the regulator rib's crown, the Z-seam grooves' lands, the ASSE anchor's two round seats and its tie channel's overrun, and the identification-chip pockets' lower arcs on the rear face. The slice reaches them with **11 bodies** over **28 islands**, 6 rooted on the plate around the bedded piece — fore of its mouth, behind its rear face, through the funnel's opening — and 5 on the slab's interior face, which is that piece's own first layers; the shortest build-up is **1.44 mm**, under the regulator rib's 3.5 mm crown band, the one tie band with no room for a gable. The reading is this project's: tree(auto) supports at a 35° threshold, 0.4 mm top and bottom Z distances, 0.6 mm from the object in XY and two interface layers, all carried in the reading's `slicer_settings`; a plate sliced with other support settings is audited again against that project. Back-bottom's two slide-head bodies carry the ridge's 1 mm land: the west run from the bed through the PRV passage and the east from the arm's under-flare **6.00 mm** below. The three slide-head bodies on the two bottoms are the places the support campaign still names.

## Print orientation + corner relief

Three pieces print on their **Z− face** — the bottom pieces floor-down on the
floor slab, front-top mouth-down on its seam rim — and back-top prints on its
**Z+ face**, its ceiling on the bed. The build axis is the box's own Z on every
piece and the sign is the piece's (`enclosure.print_up`): where it is +Z the face
that hangs is the one looking **down**, where it is −Z the one looking **up**, and
every 45° relief on this box is struck on the side that hangs for its piece — a
corbel under a floor on one piece is a corbel over a crown on the other. Faces at
45° print either way. The anti-warp relief goes on the arrises
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
that width. The cartridge has [0.5 mm](PUMP_CARTRIDGE_Z_CLEARANCE) of functional Z clearance
above the sill and 1 mm below the lintel; it has no cosmetic reveal or corresponding X/Y inset.

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

The Y-seam lip is the one joint the orientation costs something. Front-top's ceiling
tongue juts one overlap past the body into the space the back piece's ceiling
occupies — a cantilever that cannot be buttressed without colliding with the back
piece, and so wants print support. The floor does not share that cost: its tongue
runs aft at the slab's full thickness with its underside on the bed, then ends in
a one-wall-long 45° scarf nose. The back half's matching wedge also grows from the
bed, so the cold-core bearing plane carries no supported surface. The side-wall
segments, vertical to the bed, are free. On back-top the upper pin's own top face
looks print-down: a flat the pin's width, [13 mm](BOSS_END_CLEAR) under the ceiling
lane, reached from the slab.

The **ASSE drip pan's sleeve** in back-top is a plain carcase — floor, two jambs, backstop and a
square lid — rooted on the −X wall. Printed ceiling-down its floor and the rebate's roof look
print-up and carry themselves; its lid and the berth's floor look print-down over the tray's own
room, which no material may fill, and the ASSE chain stands over the lid, so both are supported
faces, reached from the slab through the open mouth. The pan lies on a flat floor.

The moisture plate's **cable clip** is immediately aft of the sleeve on the dry inner face of
the −X flank. The shared profile is [9 mm](CABLE_CLIP_DEPTH) deep; [6 mm](PAN_CLIP_EMBED) are embedded in this
[9 mm](PAN_CLIP_WALL) wall, leaving [3 mm](PAN_CLIP_PROUD) proud in the cabinet and [3 mm](CABLE_CLIP_BACKING) of
exterior backing. The profile is asymmetric in its own up, and that up follows the print's:
back-top prints ceiling-down, so the run is laid along +Y and the profile's up is the box's −Z.
Its two hooked sections grow from the wall on 45° faces toward the print's up, and the recessed
channel ramps to the wall face over [6 mm](CABLE_CLIP_RAMP) at both ends of its [18 mm](CABLE_CLIP_RUN) run. It therefore
adds no supported face to the ceiling-down back-top print. The plate's continuous lead leaves a
service loop between this fixed clip and the open pan.

The **ASSE anchor** one storey above it looks print-down on its top. Outside the zip ties'
span a 45° wedge carries that top from the V's upper arris, or the bore's crossing of it, back to
the wall and up to the lane, where it fuses into the slab and the chain's own pocket; over the
span the wedge is absent so the loop has its room, and the web between the tie cavity and the V
is chamfered at 45° down into the cavity, a slope the print lays on itself and a funnel the loop
drops through. Its two 60° seat flanks stand 30° off vertical and lay on themselves either way;
the two round seats' lower arcs look print-down inside their bores and are supported faces.
Behind the anchor, one channel spans both zip-tie bands: its fore and aft end faces remain
`tie_cav_wide_w` wide about their tie centres, the volume between them is open, and its top
mouth opens into the lane the slab leaves over the same span (`_ceiling_tie_channel_relief`).

The **bay floor** is the one feature that costs nothing and pays: it IS front-top's
first layers. Its underside is the seam mouth, the plane the piece beds on, so there is
no face under it to hang and no support in it to pick out. It is a solid slab across the
whole front storey with one slot through it: the pump cartridge slides across it, and the collet
plate comes up that slot from the bed face onto the floor's own top.

The **tee wall** behind that plate costs nothing standing up, and its four bores are the
only thing in it that could have hung. The piece beds on the seam plane, so a bore on Y
lies horizontal and its crown is the only face in the wall that could be laid on air.
Each is **teardropped** (`_tee_bore`): the roof stands on the bore's own tangent points.
Its two planes rise at [36°](TEARDROP_ROOF), one whole degree above the history-only back-top
PET-GF profile's automatic-support threshold and verified support-free with that exact profile;
tangency makes that the narrowest and shortest peak at this angle. The lower circle the collar
bears on is untouched, and the wall needs no support.

The **five round tube crossings in the +Y wall** use the same `_teardrop_y` section through
the wall's whole section at each station, struck toward back-top's print-up. This piece beds
on its ceiling's outer face (`BACK_TOP_UP`), so the crown a print cannot close is each bore's
machine-bottom, and that is the side the tangent [36°](TEARDROP_ROOF) roof stands on; their
stated Ø18/Ø17.86 figures remain the complete circular pass envelopes for the threaded barrels
everywhere else round the circle. The separately printed identification chip keeps its
circular bore, and the fitting's flange and nut clamp the chip and the remaining wall annulus
on their two faces. No face in any of the five passages lies flatter than that roof.

The **AC inlet's mount** stands off the +Y wall's inner face in back-top and costs
nothing either. It is one rectangular block from the flange pocket's mouth to the wall
(`enclosure._c14_tunnel`): its two flanks are vertical to the bed, its crown runs out into the
ceiling slab the piece prints on, and its underside looks print-up — a free flat, with the wall
and the slab carrying the block between them. What is left over air is the bore's own
print-roof, the aperture's machine-bottom face — a bridge the aperture's full width, carried
between the block's two flanks. Nothing on the piece stands outside the print silhouette: the
receptacle's two heat-sets go into the seating face at the floor of the block's flange pocket,
from inside the box, and the back of the machine is flat.

The inlet stands on one column, `enclosure.c14_station_x`: the aperture, tunnel, pocket and
both screw stations all follow that one X datum, and its Z is aligned with the other top-row
ports. Over the inlet the ceiling is the slab's own underside, which looks print-up, so nothing
between the receptacle's moulded rim and the ceiling asks for a relief band or a support
stack.

The **PRV chase's roofs lean from the −X wall too**. Where its open exterior groove
becomes the closed fall, the roof rises inward across the exact
[3 mm](VENT_GROOVE_ROOF) show-skin section at 45°. The closed passage's roof is one X plane
from its liner inside the flank through the wall and out to the cold-core lip, and the lip
keeps [3.1 mm](VENT_RIB_LAND) of solid land below the square mouth. Back-top's share of the rib
stands square on the seam rim, which looks print-up on that piece, and its crown — the one face
of it that looks print-down — is carried by a 45° wedge from the lip back over the
[8 mm](VENT_RIB_BASE) to the grown flank. The mouth's floor is a `vent_channel_w` bridge
between the passage's two jambs. The exterior groove edge, the square passage and the back
slide's opening remain on their own datums.

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

Both run through **one shared channel in the anchor's back** (`_asse_tie_cavity`), closed on
every side but its two mouths. Its fore and aft ends are `tie_cav_wide_w` bands centred on
their respective ties. The same XZ profile cuts continuously across the volume between them.
It is **straight on the west and the anchor's own V on the east**, so
it is narrowest at the axis and flares to both mouths: each mouth opens
`asse_tie_back / sin 60°` off its lip's own arris, on the block's face where a hand reaches
it, and at the axis the flare leaves a zip tie pushed through the room to turn the vertex by
cutting its corner. It stands one `wall` west of the apex at every station, struck on the
deepest section's apex so the web is no thinner than that anywhere, and one `wall` off the
side wall behind it — so its width is a remainder between the two rather than a number. The
continuous horizontal passage gives the slicer one support body with a full-width removal path.

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
the ceiling, which is the room the loop comes down; the slab is open to the lane over the
channel's whole span (`_ceiling_tie_channel_relief`).

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

Back-top prints on its ceiling, so the rib **stands up off the bed**: its two end webs rise
from the slab, the seat is an upward-opening cradle in the print, its lips look print-up, and
the channel's floor over the crown is a `tie_cav_w` bridge between the two webs. The slab
stands off the rib's room over its tie band (`_ceiling_tie_reliefs`), so the loop comes down
both flanks in the lane.

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
and both hand pulls. Its filled bearing block rides the bay floor; its exterior
face begins on that same bed plane above a 0.5 mm recess in the fixed sill and ends 1 mm below
the lintel. The bed plane is z [165.365 mm](PUMP_CARTRIDGE_BOTTOM_Z), the crown is z
[282.495 mm](PUMP_CARTRIDGE_TOP_Z), and the complete removable face is
[117.13 mm](PUMP_CARTRIDGE_RISE) high. Its outer shell
keeps the complete 215 mm enclosure width, including both rounded front corners and side skins,
and its show plane shares the fixed front face at [0 mm](PUMP_FACE_OFFSET) offset. The flavour pack stands behind that plane. The show plane stands one complete
[1.2 mm](PUMP_SHOW_GROWTH) flute depth ahead of the pump-pocket datum. Its filled body reaches both cavity
planes, and the front display-support columns have no section anywhere in this withdrawal span.

The pump stations use a [3 mm](PUMP_STATION_DROP) downward world-Z datum. The stationary
manifold, tees and tube passages stand 2 mm above the manifold's nominal datum. The pump
reference's rear boss and motor axis stands 1 mm toward Y− from its head datum, and the
clamp's fitted octagon and motor-can openings follow that rear-stack axis. The four short
barb tubes connect each pump head to its fixed tee interface.

**Each pump drops into that cradle from Z+.** Two straight wells pass the motor, boss, stamped
bracket, head and tube fittings at every insertion station. Below `cap_split_z`, the head well
closes to `cap_pump_air` around the moulded head. That leaves a continuous cradle land under
the stamped bracket on −Y and both X sides; +Y remains open for the fittings. Pump weight goes
from that bracket directly into the lower cradle and then into the bay floor.

The head's [8 mm](PUMP_SKIRT_DEPTH) skirt stands over one flat horizontal land at z
[205.594 mm](PUMP_SKIRT_SUPPORT_Z). The [0.15 mm](PUMP_SKIRT_SUPPORT_AIR) difference between
the skirt bottom and that land is Z clearance. The land keeps the skirt's existing X/Y plan;
there is no slanted substitute for it. It is continuous across the X−, Y− and X+ flanks, with
[5 mm](PUMP_SKIRT_Y_MINUS_LAND) under Y−. The
measured [54 mm](PUMP_SKIRT_BODY_Y) body has [0.15 mm](PUMP_SKIRT_XY_AIR) per-face clearance
in a [54.3 mm](PUMP_SKIRT_OPEN_Y) Y opening, from y
[17.133 mm](PUMP_SKIRT_BODY_Y_MINUS_EDGE) to y
[71.433 mm](PUMP_SKIRT_BODY_Y_PLUS_EDGE). On Y+ the same land continues only between the two
tube-casing passages. The skirt itself spans [62.5 mm](PUMP_SKIRT_Y), from y
[12.115 mm](PUMP_SKIRT_Y_MINUS_EDGE) to y [74.615 mm](PUMP_SKIRT_Y_PLUS_EDGE); its opening ends
at y [74.915 mm](PUMP_SKIRT_Y_PLUS_OPEN_EDGE), leaving
[0.3 mm](PUMP_SKIRT_Y_PLUS_AIR) around the skirt and
[3.482 mm](PUMP_SKIRT_Y_PLUS_LAND) of supporting land back to the body opening. Only
[3 mm](PUMP_SKIRT_UPPER_BAND) of upper band remains behind
that opening, ending at y [77.915 mm](PUMP_SKIRT_UPPER_BAND_AFT). That same
[77.915 mm](PUMP_CARTRIDGE_AFT_Y) plane is the complete cartridge's Y+ edge; no lower-cradle
stock continues behind it.

**The second printed piece is the top clamp.** `enclosure-pump-cap`
(`build_pump_cap`) is [169.9 mm](CLAMP_SPAN) across and [61.75 mm](CLAMP_RISE) high. Its Z− face
stands at z [215.75 mm](CLAMP_BASE_Z) on the upper face of each measured
[2 mm](CLAMP_BRACKET_T) stamped bracket. One filled field spans both pump heads from their clean
fore envelope to the aft wall and reaches one common crown at z
[277.5 mm](CLAMP_CROWN_Z), with [6 mm](CLAMP_LINTEL_AIR) of Z air below the fixed bay lintel.
Two fitted openings wrap
both bosses with the pump case's exact octagonal bore and leave one shoulder around each motor
can. Both fitted openings follow the pump reference's rear-stack axis,
[1 mm](CLAMP_PUMP_Y_SHIFT) toward Y− from the head and lower-cradle datum. A single
[33.89 mm](CLAMP_ACCESS_W) × [48 mm](CLAMP_ACCESS_RUN) top recess joins the two screw stations;
its retained floor stands at z [221.75 mm](CLAMP_ACCESS_FLOOR_Z), [6 mm](CLAMP_ACCESS_BASE)
above the broad print face. The individual counterbores continue to head seats which keep
[4 mm](CLAMP_HEAD_LAND) of printed land underneath. The two M3s run into heat-set inserts in the
cradle. The clamp carries no show face, plate stop or hand pull.

The service sequence follows those two load paths. Withdraw the assembled cartridge by its
cradle pulls before any Z service; back out the two clamp screws on the withdrawn cartridge;
lift off the clamp; then lift either complete pump straight up. Assembly is the reverse on the
bench, followed by straight Y insertion.

**Each of the four tube-casing openings is [13 mm](CAP_TUBE_OPEN) wide** around a
[12.75 mm](CAP_TUBE_PART) casing, leaving 0.125 mm per side. The two casing axes on each pump
stand [59.75 mm](CAP_TUBE_PITCH) apart. The physical pair spans
[72.5 mm](CAP_TUBE_PART_SPAN), while its holder openings span
[72.75 mm](CAP_TUBE_OPEN_SPAN). Each passage begins
[0.15 mm](CAP_TUBE_AXIAL_AIR) before the casing face along Y. Its circular lower half is
centered on the casing axis and a straight 13 mm shaft continues through the complete vertical
insertion path. The shafts, tube-side case room and upper well share the same outer X planes;
printed wall remains between and outside the passages. The full-width upper wells end together
at y [74.915 mm](PUMP_UPPER_WELL_AFT). Past that plane only the four individual shafts continue:
the closed middle span on each pump and the centre span between the pumps all carry the same
cap-following reinforcement to the cartridge's aft edge.

The four short barb runs retain [1.28 mm](PUMP_STATION_LEAD) of moving-end lead before the
plate berth. The show face shares the fixed front plane at [0 mm](PUMP_FACE_OFFSET) offset and
stands one flute depth ahead of the pump-pocket datum. The pump wells and their Y+ edge occupy
the complete flavour pack's common station.

Nothing latches the cartridge in the enclosure. The four barb tubes gripped in the anchor
tees' branch collets retain it, and the **collet plate** releases them: a 3.175 mm section
printed into front-top, standing 1.5 mm fore of the four collet noses. Pull the cradle and
the tubes draw the tees forward until their collet noses land on the printed release face;
the collets open and the tubes pass back through the four plate passages. Push it home and
the tubes enter the same collets and bottom in them. One hand pulls the cradle and the other
braces the box. The plate is joined to the tee wall behind it.

Each passage has an Ø8.5 mm circular bore and a tangent teardrop roof. It passes the
Ø6.35 mm tube between the aligned pump and tee stations while the surrounding face
catches the release nose's Ø11.43 mm rim. The four tube-centre stations are independent of
the plate's rectangular outline, its upper cap and the cartridge's pull pockets.

**The tee travels and the valve stays seated.** The modeled release travel is
[3.15 mm](PLATE_STROKE): [1.5 mm](PLATE_REST_GAP) of nose air followed by
[1.65 mm](SLEEVE_TRAVEL) of sleeve travel, the PP0208E's own stroke
([`reference/tee-connector/`](/hardware/reference/tee-connector/README.md)). The tube stub
flexes inside the two collets that hold it. Compliance is not modeled in the reference bodies.

**The cradle ends at the skirt band's aft edge**, y [77.915 mm](PUMP_CARTRIDGE_AFT_Y): a plate-retention return or side skin
cannot survive behind that plane.

**Both pulls belong to the cradle and stand on its own Y midline.** Each side pocket is
[18 mm](PULL_DEPTH) deep, [28 mm](PULL_RUN) fore/aft and [48 mm](PULL_RISE) high, centred at
y [41.46 mm](PULL_CENTER_Y). Its floor at z [176.25 mm](PULL_FLOOR_Z) leaves
[10.88 mm](PULL_FLOOR_LIGAMENT) of bed-rooted cradle below it and places the pull datum,
z [188.25 mm](PULL_CENTER_Z), 12 mm inside the mouth. At the deepest fingertip wall the
straight vertical opening is [30 mm](PULL_PLUMB) high; its roof then climbs at 45° to the open
flank and reaches z [224.25 mm](PULL_TOP_Z). A Y-normal wall closes each end of the pocket:
the fore wall at y [27.46 mm](PULL_LEDGE) is the ledge the fingers pull on, the aft wall at
y [55.46 mm](PULL_AFT_LEDGE) the one they push on, with [22.46 mm](PULL_FORE_STOCK) of cradle
fore of the pocket and [22.46 mm](PULL_AFT_STOCK) aft of it.
Pulling force enters the one load-bearing cradle; the clamp has no separate grip to split the
load or invite a second tug.

## The full-width opening

**One opening spans the entire lower-cradle storey** (`_bay_cut`), from exterior side face to
exterior side face and from the bay floor to the lintel. No fixed `enclosure-front-top` skin,
rim cap or display-support post remains in that band. Two narrow fixed plate-retention cheeks are added
back only at the aft outer edges and overlap the collet plate's tails; the cartridge carries
one local aft-corner notch round each cheek. Each cheek is a wedge in plan, standing
[3 mm](PLATE_GUIDE_WEDGE) further fore at the fixed side wall than at its inboard face:
the section carrying the plate's moment is deepest where the cheek is rooted in that wall.
The cheek stands aft of the cradle pull and the cartridge carries a local notch around it.
The rake is the cheek's whole height, so it is one prism — every face a plane, every
wall vertical and supported, nothing anywhere in it overhanging. The opening runs **past the
collet plate to the tee wall's fore face**, where it ends on printed section rather than on a
free edge.

**The lower cradle's complete exterior is one bed-rooted wall.** Its flush front, both rounded
corners and both exterior flanks begin with the filled block on one plane and continue plumb as
one uninterrupted silhouette to 1 mm below the lintel, without a bevel, ramp, starter strip or
shelf. The fixed shell perimeter is recessed 0.5 mm below that lower edge while the interior bay
floor remains at the bearing plane. Only the grip pockets and two aft plate-retention notches otherwise
depart from the outline; the top clamp sits wholly inside the wells above.

## The bay floor

**Front-top carries a floor across the bay** (`_bay_floor`), from the front wall's
interior face aft past the collet plate, and everything in this storey stands on it.
**It is this piece's first layers.** Front-top beds on the seam plane, so a floor
struck there lies on the bed with nothing under it to hang. Its flat bearing sill is z
[165.365 mm](PUMP_BAY_FLOOR_Z), [1 mm](PUMP_BAY_FLOOR_RELIEF) below the pump-neutral floor
datum (`bay_floor_z`). The fitted reference pump model's signed head-to-floor clearance is
[0.5 mm](PUMP_HEAD_FLOOR_AIR). The removable exterior face begins on the sill plane, while
the fixed shell perimeter is
recessed 0.5 mm below it for the running gap.

**One pocket per collar passes the Z seam**, and nothing else does.
Front-bottom's side lip is given up over this whole run (`_flank_lip_drop`) — round both
front corners and back down each flank as far as the tee wall's aft face — so the floor
crosses it wall to wall instead of surrendering one `wall` at each flank. What still
stands over the mouth here is the front column's socket boss on its own plinth, and the
floor opens for that alone. Aft of that run the lip is carried whole and the telescope
is untouched.

**Two feet under the collet plate belong to front-bottom's flanks.** Each foot presents a
[10 mm](PLATE_FOOT_X) X × [20 mm](PLATE_FOOT_Y) Y land on the seam plane, centred fore/aft
on the plate, and keeps [3 mm](PLATE_FOOT_T) of section at its inboard edge. Its underside
rises at [45°](PLATE_FOOT_ANGLE) from the flank. The lowest line is z
[147 mm](PLATE_FOOT_LOW_Z), [1 mm](PLATE_FOOT_COND_Z_AIR) over the condenser+fan envelope's
crown; over their common X/Y footprint the sloped face keeps
[2 mm](PLATE_FOOT_COND_AIR) of air from that complete bounding box.

**The collet plate's nominal release section is rectangular.** Its bottom reaches the seam
plane and each nominal end stands [4.5 mm](PLATE_STEP_IN) off its cavity-side wall, at
x = ±100.0. `enclosure_assembly.collet_plate_spec` supplies that outline and the four tube
stations. The printed plate joins the tee wall, floor, outer cheeks and upper cap continuously.

The perimeter joins fill the 0.2 mm construction offsets at both X ends, the fore offset at
the tail cheeks and below the floor top, and the aft floor slot with its
[1 mm](PLATE_SLOT_LEAD) lead flare. Above the nominal rectangle, the plate fills the wedge
up to the cap's raked underside. The nominal slot ends at x = ±100.2; beyond each end, a
4.3 mm printed return continues into the 3 mm outer wall. The central release section keeps
its two Y faces and the cartridge's working space.

**The upper cap joins the plate to the bay roof** (`_plate_cap`). It fills the band above
the plate to the ceiling at [283.5 mm](PLATE_CAP_TOP). Its underside has a
[1 mm](PLATE_CAP_LAND) flat land at [216.5 mm](PLATE_CAP_Z), then rakes at 45° to
`plate_guide_fore_y`. The complete front edge is z [221.865 mm](PLATE_CAP_FORE_Z),
continuously across X.

**The two outer cheeks are stationary prisms** (`_plate_fore_guides`) fore of the plate's
tails. Outside either slot end, each prism returns aft through the complete 4.3 mm band
to the cavity-side wall and joins the 3 mm outer wall. Each cheek overlaps 10 mm of the
plate's fore face, is [3 mm](PLATE_GUIDE_WEDGE) deeper at the fixed wall than at its
inboard face, and stands from the bay floor to the ceiling. Its head carries the cap's
land out to the side wall. The cartridge has a local aft-corner notch around each cheek.

**The tee wall stands behind the release face** (`_tee_wall`), wall to wall and the full
height of the bay. One bore per anchor tee clears the round collar on its branch arm by
`TEE_WALL_BORE_SLIP` on the radius. The bore locates the tee in X and Z while leaving it
free in Y. The wall's fore face meets the plate's aft face; the plate's smaller teardrop
passage leaves a release face around each tube. The wall's aft face stands one modeled
stroke plus 1.454 mm of body air (`TEE_WALL_BODY_AIR`) fore of the tee body. Its larger collar-clear bores continue
through that broad face.

**That wall is also the bay's back.** The printed plate closes its release band and the
wall fills the surrounding height. The Z seam crosses it in the rail channels' deep lane
(`_z_rail_channels`).

The **bay** is the opening all that leaves through (`_bay_cut`): exterior side face to exterior
side face, from the floor's own top at z [165.365 mm](PUMP_BAY_FLOOR_Z) to the fixed lintel at z
[283.495 mm](PUMP_BAY_LINTEL_Z), and aft to the printed collet plate. The lintel is relieved
[2.5 mm](PUMP_BAY_ROOF_RELIEF) upward from its pump-neutral roof datum and keeps
[7.2 mm](PUMP_MOTOR_LINTEL_AIR) over the installed motor crowns. The flat sill runs wall to
wall; the lintel carries the facet and the display on a stated ligament.
The removable shell follows the enclosure's rounded plan with its front plane flush at
[0 mm](PUMP_FACE_OFFSET) offset. The moving pump ends keep their
[1.28 mm](PUMP_STATION_LEAD) lead over the fixed tee deck, and the filled block behind the
face reaches both cavity planes.
Front-bottom's front lip drops across the whole flat span
(`_front_flat_lip_drop`) — the floor stands in that band and the heads run down through
it — and the front wall below keeps its single `front_wall` section from slab to seam.
The face keeps [0.5 mm](PUMP_CARTRIDGE_Z_CLEARANCE) of Z clearance over the recessed stationary
sill and 1 mm below the lintel. Its complete front, rounded corners and exterior flanks stand plumb
between those two flat gaps with no taper.

**The fixed front wall is [9 mm](FRONT_WALL) thick and grows inward.** The complete flavour
pack stands far enough aft for the removable pump face to share that plane while keeping
[5.1 mm](PUMP_FACE_SKIN) of smooth stock over each lower head relief. Over the upper insertion
wells the cut reaches forward to leave [4.2 mm](PUMP_UPPER_SMOOTH_SKIN) of smooth section; the
same uninterrupted full-depth flute field as the enclosure leaves exactly
[3 mm](PUMP_UPPER_FLUTED_SKIN) of finished printable backing, the
[3 mm](PUMP_FACE_BACKING) front-face minimum. What
noses into the section gets a 45°-chamfered relief (`_front_relief_cuts`): two stated
compressor pockets following the mounting plate's front strip and the power box, both floored
on the can's own kiss, and one pocket per pump in the
lower cradle's face, floored where the pump head and bracket insertion well puts its root
(`pump_relief_floor`). The compressor is the only body in the refrigeration stratum
standing fore of the wall's interior plane — the condenser bears on that plane through
its rails and the fuse clamp stands clear behind it — so the wall keeps its full section
across the rest of the front. `box-front` reads every placed body against the relieved
surface, region by region.

## Pump clamp field

The geometry in `printed-parts/enclosure/pump-tray/` supplies the two fitted openings in the top
clamp. The clamp is one rectangular field over both pumps, from each stamped bracket's upper
face to the common pump-carried crown. The fixed bay lintel does not locate it. The exact
pump-case octagon and motor-can bore are cut from it, leaving the case-derived locating walls,
pressing lands and can shoulders wherever a pump does not occupy the material. It is one
printed `enclosure-pump-cap`, not separate collars or fastener pieces.

**The bracket divides bearing from location.** The lower cradle bears under three sides of the
68.6 mm stamped bracket, and the clamp's complete broad base lands on its upper face. The
bracket remains wholly below the printed cap: every cap wall grows directly from one common
Z− plane, with no shallow pocket ceiling or narrow perimeter foot. Above that steel, the
case-derived octagon engages the white boss over its complete run and the shoulder surrounds
the can. Thus the cradle takes weight, the clamp prevents lift, and the octagon fixes X, Y and
yaw. With the cartridge withdrawn, the clamp's vertical path keeps
[4.305 mm](CLAMP_FRONT_SKIN) of smooth cradle skin ahead of its fore face. A
[4.81 mm](CLAMP_AFT_WALL) wall remains aft of each octagon to locate the boss
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

**The lower cradle prints on its Z− floor.** Its filled bearing block, flush front, rounded
corners and both flank skins begin together on that bed and rise plumb. The two
pull roofs climb at 45° and the pump wells remain open above. The top clamp's complete
field begins on one broad Z− bed face. Its only internal down-facing transitions are the two
functional boss-to-can shoulders, 19 mm above that face and open through the fitted bores for
support removal. Both screw heads remain accessible from the top.

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
the plane the display's body already lies against. Where the two meet is read, not chosen.

The rib's cavity-side roof is **one flat plane** from its wall-to-wall aft crown toward the
funnel opening. At the crown it spans front-top's two flank faces; toward the opening the
ceiling corbels absorb its sides. The descending funnel chute takes one body-shaped notch from
that plane with [0.15 mm](FUNNEL_COLLAR_AIR) of running air in plan. The roof remains one
connected planar face around the notch, reaches both front opening corners, and has zero volume
inside the funnel keepout.

**Running it to the flanks closes the storey, and two electrical paths cross.** The **pump jack**
owns the centreline a hand finds behind the display, directly above the valves: a RiteAV RJ11
keystone jack in a printed keystone receptacle, the same module in the same receptacle the +Y
wall of back-top holds for the umbilical ([`reference/riteav-keystone/`](/hardware/reference/riteav-keystone/)).
Its [14.9 × 16.3 mm](PUMP_JACK_APERTURE) aperture passes the 3 mm rib, which is the receptacle's
whole lip; the pocket, the two catches the jack's tang and latch snap over, and the boss that
carries them stand [6.7 mm](PUMP_JACK_BOSS_REACH) aft of the rib in the cavity, the boss's lower
wall on the plate cap's crown, which puts the aperture centre at z [296.53 mm](PUMP_JACK_Z). The
jack goes in from the cavity, tang first, swinging down onto the lower catch, and its
[30 mm](PUMP_JACK_BODY) body with the 110 punchdown block reaches aft over the valves. The fixed
J13 lead ends on that punchdown; the cartridge's cord ends in the **pump plug**, an RJ11 6P4C
modular plug whose clip faces down into the empty pump bay. After the cartridge is drawn, the
hand reaches up through that bay, presses the clip, pulls the plug straight forward until it is
clear of the plate cap, and lowers it through the bay without approaching the display body.

SIG-7 still crosses the rib, at the same height but shifted [-32 mm](DISPLAY_LOOM_X) in X. Its
four conductors remain in the 1/2" PET expandable braid, so its teardrop bore remains the opened
figure — Ø[19.05 mm](CABLE_BORE) — with solid stock between that bore and the receptacle's boss.
It locates nothing and carries nothing; the display loom is dressed after it is through.

On the same rib's cavity face, one unembedded [9 mm](CABLE_CLIP_DEPTH)-deep cable clip runs toward
+X and stops [12 mm](PUMP_JACK_CLIP_LAND) short of that edge. It guides and strain-relieves the
**fixed enclosure-side J13-to-jack lead** on its return to the main-board wall. It does not
retain the cartridge's cord. The shifted loom bore remains teardropped because the piece beds on
Z; the receptacle's aperture and pocket keep the module standard's rectangles, whose flat tops the
rib and the boss bridge.

## Funnel opening

One rectangular opening spans the top wall **directly behind the display
housing**, where the removable silicone funnel
([`../../zone-c/funnel/`](/hardware/printed-parts/zone-c/funnel/))
drops in — its straight chute running clear in the opening, its whole floor one
ramp falling to the centred spout, its flat brim resting on the wall frame left
around the cut.

The funnel is a static placed part: `_funnel_hole` reads the funnel's own collar at
`enclosure_assembly.funnel_centre()`, and `_funnel_cut_plan` adds
[0.15 mm](FUNNEL_COLLAR_AIR) on each plan face. That opening continues downward as the
funnel's filled outer chute, ramp and spout envelope, so neither printed shell nor roof stock
can occupy the silicone or liquid volume. The frame that cut leaves is bounded by the
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

back-top's ceiling is **one slab, and it is the face the piece prints on.** The exterior
top stays at z 355 and the rear storey's established pack lane at z [352](CEILING_LANE):
every body, port and anchor station under the ceiling is struck on that lane. The slab
carries [12 mm](BACK_TOP_CEILING_T) of section from the show face inward, to z
[343](BACK_TOP_CEILING_FACE), between the grown flanks and from the Y telescope's end to
the +Y wall — [9 mm](BACK_TOP_CEILING_GROWTH) more than the top wall's own `wall` — and
gives that section back over whatever stands in it. Every pocket opens from the slab's
interior face up to the lane and no further, so the top wall's own `wall` stands over each
one (`ceiling-show-cap`).

**Three kinds of pocket.** A purchased body whose placed solid enters the slab earns one
over its exact plan plus assembly slip, up to its own crown plus a clearance
(`enclosure_assembly.ceiling_reliefs`; the named population is what keeps an unrelated
encroachment visible to `pack-closes`). The flow meter's two anchors and every rib rooted on
the ceiling — the carb-1 and co2-2 ribs and the regulator's — get the room their zip tie's
loop comes down: the rib's reach plus the tie's thickness and its routing air either side,
the rib's whole length, from the axis plane to the lane (`_ceiling_tie_reliefs`); the rib is
fused back into that pocket and stands up off the bed with its seat an upward-opening cradle
in the print. And the tap-water chain's shared tie channel is open to the lane from the −X
flank to the far edge of the chain's own pocket over the span its two zip ties take
(`_ceiling_tie_channel_relief`), so each loop comes west over the chain's crown in the
`DECK_CEILING_CLEAR` lane and drops into the anchor's cavity through the mouth the flank
leaves it.

**Everything rooted on the ceiling is this piece's**: the flow meter's two anchors and the
three ribs bored for `carb-1`, `co2-2` and the WR1110's barrel, each drawn to the lane
through `piece_root_faces` and fused into its own pocket. Back-top is populated inverted
on the bench, ceiling down, and every one of those seats is a cradle a body drops into.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ the four `enclosure-*.step` pieces + `enclosure.step`. Wall, seam, boss, and
facet constants are at the top of `enclosure.py`. Prints the facet size, the
cross-pin levels each side wall ended up with, each piece's envelope vs. the H2C
bed, every piece-pair's slip fit, and the cold-core clearance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
