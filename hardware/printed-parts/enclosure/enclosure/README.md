# Enclosure

A PETG box, 3 mm walls, **split into four printable pieces** — front/back ×
bottom/top, every piece inside the H2C bed — that telescope and screw together.
It measures [223 × 481 × 358 mm](BOX_SIZE), and **width, height and the back wall
are all stated bounds**. `_dims` measures the pack against each one and enters the
reading in `BOUNDS`; the box comes back at its stated size regardless, so a pack
that overruns one gets a wall drawn through it, a red row naming by how much, and a
clash in `pack-closes` at the body that overran.

- **Width** is `appliance_width`, struck symmetric about x = 0. What the pack owes
  it is clearance: a body on the floor slab spans the interior wall to wall, so a
  floor body stands one `side_rib_inset` in from the wall **at the depths the seam's
  columns stand there**, leaving each post, chain and pod its full section. The cold
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
sides, which `_lip_denied` measures. The four station pods and the posts over them
stand in the ±X boss-chain bands over their piece's whole height, so a seam height
moves only the lip. The cold core spans that
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

## Test-print coupon

It exports those same five files a second time as `enclosure-coupon-*.step` —
the whole four-piece assembly shrunk to a [158 × 140 × 136 mm](COUPON_SIZE)
box, printable in an evening, to prove the fit before the real one is
committed. It is the same geometry from the same code: only the numbers
describing the box differ, so a coupon that assembles is evidence about the
appliance and not about a second model of it.

Everything the assembly is judged on is on it at **full size** — the display
housing, and all three seams with their full six-level ladder of cross-pins. Its
facet runs the coupon's own full width, the way the appliance's runs the
appliance's; the coupon is just narrower, being only as wide as the display window
plus a corner chain either side. The extra flat 45° face the appliance spends its
width on proves nothing about the housing and would only make the coupon wider.

No dimension of it is chosen. Each is the minimum its own feature allows — the
depth is the display housing plus the back column's two Z-seam stations, the
width is the display window with a corner chain either side, the height is the
cross-pin ladder raised to clear the facet — so the coupon shrinks and grows with
the features rather than drifting from them.

Three things are left off, being the ones a reduced box cannot host honestly:
the contents (there is nothing packed inside it, so the walls' relief and the
seam's stand-off have nothing to dodge), the panel through-holes (there are none
yet), and the hopper throat (the placed funnel's collar does not fit the shrunken
top-wall frame).

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
`z_joint_back` — the bottom pieces carry a 3-sided lip + socket pods, the top
pieces carry the D-pins and the posts that carry them, more X-axis screws crossing
each seam. The front pair joins, the back pair joins, then the front assembly
telescopes into the back as one.

A Z seam is pinned at **both ends of its column**, not just one, or the far end
hinges open. The front column takes the front-wall corner and the aft end of its
own lip; the back column takes one just behind the Y-seam mouth and one in the
rear-wall corner. Every station stands in the ±X band the walls' standoff opens
off the cold core, which runs clear the full depth, so none has to dodge the
pack.
Each cross-pin mates the walls of its overlap (the
pin's mouth-side face on the receiving mouth, the socket pod's rim-side face
on the lip rim) and the two are coaxial by construction, so the **overlap
depth is derived from those matings**, not chosen — it works out to
(plug + bore)/2 + one wall.

Each cross-pin is sized to its job. Reading an M3×10 screw outboard→inboard from
the ±X exterior: a Ø6.15 mm head counterbore, then the pin body (the screw spans
the head seat to the heat-set, so the body is screw length − heat-set long), then
the heat-set, then a one-wall cap.

- **Receiving piece = pin** (the back pieces on the Y seam, the top pieces on
  the Z seam): a Ø9.9 mm cylinder (the shank + one wall each side, *not* the
  head — the head sits in the wall counterbore) from the exterior to the
  heat-set, registering in the socket bore. On the Z seam a flat tab carries it
  up to the lip rim, where the post above takes over.
- **Lip piece = socket** (the front pieces / the bottom pieces): a pod bored
  Ø10.3 mm to take the round pin as a slide fit, with the ruthex M3 heat-set
  (Ø4.0 × 5.25) capped at its deep inboard end.

**Every boss stands on a post of its own section, run to the bed face at constant
section.** Not a collar on a spine — the whole socket footprint, carried the full
height of its piece: bed face to the seam. Printed Z-down that face is what the
piece lies on, so there is material under every part of the boss the whole way
down and the piece simply stacks. A narrower stalk leaves the socket cantilevered
over open air on the layer it starts; so does a post that reaches the wall on one
piece and stops short of it on the other, or two posts on one wall standing a
sliver apart. **A station's pod and the post over it take the same section, and a
post runs to whatever its neighbour reaches** — the corner is one column or it is
an overhang. The two pieces' posts meet at the seam, so assembled the corner
reads one column floor to ceiling, which is also the corner stiffener a printed
shell this size wants.

**Where a corner is the other piece's, the two interlock.** The Y-seam overlap
belongs to the front half — its lip and pod fill that corner floor to ceiling —
so the back half's pins stood in it with nothing beneath them and its own post
could only begin behind the lip rim. The slide path the pin's tab needed is run
the pod's **full height** instead, and the back half fills it with a web of the
same section: each piece then prints with a continuous column under every boss on
it, and assembled the slot and the web make the corner solid. The floor and
ceiling strata over the overlap interlock the same way — the front post's foot
and head come through a relief in the back half's floor and ceiling, so the post
reaches its bed face instead of starting an overlap's length out over air.

**What makes all of that fit is the band the walls keep.** A body standing on the
floor slab spans the interior wall to wall, so a body laid on a wall's face would
leave the seam machinery nowhere to stand. Every **floor body is held one
`side_rib_inset` in from the ±X walls where the seam's columns stand** — the boss
chain's own reach — and the **back wall keeps one `rear_seam_clear`**, the rear
Z-seam lip's own thickness. That is a requirement on the body at those depths, not
a rule about the wall: the columns stand at their own Y stations, and between them
the band is nothing but the wall's own air. Everything on the slab sits flat on it:
the print-corner relief runs on the standing verticals and the Y-seam's floor lap
stays inside the slab, so the seat is square and there is nothing standing there to
clear.

So the pack seats flush against the **seams**, not against the walls. Every post
has its full section, both walls carry all six levels, and the rear station's
post runs its own corner the whole way to the floor.

The Y seam is a stated plane, `enclosure.y_seam`, checked against those bands
rather than derived from them: which pieces the box comes apart into is a decision
about the pieces — what each has to carry, and what a hand reaches when the front
assembly is off.

`rear_seam_clear` is the single source for the back wall: `enclosure_assembly` seats the
rear-wall bodies against it and `enclosure.py` builds the box to it, so the wall
the bulkheads mount through and the wall the box is built to cannot drift apart.

The crowding mechanism stays in place even though nothing is crowded now: a post
necks to whatever is measured clear at its wall with 45° run-outs, and no level
is offered where the necking would leave a socket with no body to bore. It reads
zero on both walls today, and the build prints each wall's levels so a wall that
ever loses one is visible rather than silent.

Each printed piece fits the H2C left-nozzle build envelope (325 × 320 × 320 mm)
even though the whole enclosure does not — that is the point of the split.

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
Z concentric with the cavity it enters, as are the front Z-seam socket pods that
sit in them; the Y-seam lip sits mid-wall where there is no vertical arris, so it
stays square.

The Y-seam lip is the one joint the orientation costs something. Its ceiling
tongue juts one overlap past the body into the space the back piece's ceiling
occupies — a cantilever that cannot be buttressed without colliding with the back
piece, and so wants print support. The floor **shiplap** costs the same, on the
half that reaches: the front floor's cavity-side tongue runs one overlap aft over
open air (the back's bed-side half fills under it only once assembled), so it
prints on a thin support strip at the seam, the ceiling tongue's twin one slab
down. The side-wall segments, vertical to the bed, are free.

The **drip tray's rail pair** in the back-top piece costs the same, and it is the
one feature in the box that does. Each rail is a ledge off the −X wall running
east on the withdrawal axis, and its bearing face is the tray's seat — a flat
plane, held at one height for the rail's whole length, so it cannot be reached at
45° from the wall it grows out of. Ceiling-down it is that face and not the
underside that hangs, and what stands over it is the vent gap (`drip_pan.VENT_GAP`),
which is air by construction. So the pair prints on support, two strips 73 mm long
by the bearing width, in the band above the tray's slot — as does the stop bar
that closes their east ends, whose own top face is flat at the rim's height.

The **tap-water cradle** one storey above it costs the same. Its two 60° flanks
stand 30° off vertical and are free; its **top face is flat**, a soffit off the wall
over the lane, and that face hangs. The strap's cavity behind the trough is one
opening the trough's whole length, and the support in it draws out end to end.

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
[119.5 mm](DISPLAY_FACET_X) × [83 mm](DISPLAY_FACET_SLOPE) up the slope — which is
what the coupon is sized to carry and what `main()` prints beside the measured
face.

The facet is thickened into a 19 mm housing (the display's overall depth) with
the display let in. The glass is the datum: a shallow 2 mm bezel counterbore,
centred on the box (corners rounded 2.5 mm to match the glass), recesses the
glass with the 3 mm buffer uniform all around. The glass overhangs the body
unevenly (further up-and-left), so the 106 × 69 mm PCB through-hole sits offset
the opposite way; where a corner pod sits behind the facet, the hole takes it
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
facet's own back plane ahead (with a ledge of top wall between the two), the ±X
top corner pods either side, and the back wall behind — and the collar is measured
one `brim_margin` inside it on all four sides at once, so a placement that crowds an
edge is a red row naming the edge and the margin it is short. That margin
is the brim's landing: it is wider than the flange's overhang, so a full
overhang's width of wall remains outboard of the brim edge the whole way around.

The basin is pushed as far **forward** as that frame allows and takes the top
wall's full width, because the facet in front of it spans the machine and there is
nothing beside it to leave room for. It then reaches aft for the plan area its
capacity needs — which puts it **across the Y seam**. Both halves take their share
of the cut and the collar bridges it; what the seam gives up there is its top-wall
lip over the hole's span, which the mouth shelf's own relief already accounts for.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ the four `enclosure-*.step` pieces + `enclosure.step`, and the coupon's
`enclosure-coupon-*.step` + `enclosure-coupon.step`. Wall, seam, boss, and
facet constants are at the top of `enclosure.py`. Prints, for each box, the
facet size, the cross-pin levels each side wall ended up with, each piece's
envelope vs. the H2C bed, and every piece-pair's slip fit — plus the cold-core
clearance for the appliance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
