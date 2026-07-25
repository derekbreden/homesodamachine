# Enclosure

A PETG box, 3 mm walls, sized live to the bounding box of the contents placed
by [`../enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py),
**split into four printable pieces** — front/back × bottom/top, every piece
inside the H2C bed — that telescope and screw together. **Both seams stand
clear of the front pack**, so a valve tray in either front quadrant may run the
box's full width and depth without being notched around seam furniture: the Y
seam sits one stance behind the cold core's front face (behind the box midpoint,
not at it), and the front column's bottom↔top seam sits *beneath* the manifold
stack rather than inside it, so each tray lands wholly in the front-top piece.
Each column takes its bottom↔top seam at its own height (the seams stagger like
a brick bond): the back-bottom piece houses the cold core, the back-top covers
the band above it — the electronics shelf on the foam-cap top and every panel
port (the whole external-connection inventory penetrates its rear wall, above
the cold core); the front column splits at the top of the refrigeration
stratum — compressor and condenser below, the valve trays + funnel + display
above.

`enclosure.py` exports the four printable pieces (`enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`) plus
`enclosure.step` — the four as separate solids in assembled position, seams
intact (mirrors `faucet/touch-flo-shell`).

## Test-print coupon

It exports those same five files a second time as `enclosure-coupon-*.step` —
the whole four-piece assembly shrunk to a [159 × 140 × 154 mm](COUPON_SIZE)
box, printable in an evening, to prove the fit before the real one is
committed. It is the same geometry from the same code: only the numbers
describing the box differ, so a coupon that assembles is evidence about the
appliance and not about a second model of it.

Everything the assembly is judged on is on it at **full size** — the display
housing, all three seams with their full six-level ladder of cross-pins, and
the rear port cluster. That cluster drops as one rigid body (down by the back
seam's own drop, so it keeps its exact stance on that lip band), but in X it is
**packed to what it occupies** — every real spacing kept, the appliance's wide
dead wall between distant ports closed — then centred. So it still keeps every
spacing that matters: nut to nut, nut to lip band, flange to corner chain; only
the empty wall between independent ports is dropped, and the coupon is that much
narrower for it (the box's width in X, not the appliance's core-driven span).

No dimension of it is chosen. Each is the minimum its own feature allows — the
depth is the display housing plus the back column's two Z-seam stations, the
width is the packed port cluster with a corner chain either side, the height is the
cross-pin ladder raised to clear the ports — so the coupon shrinks and grows
with the features rather than drifting from them.

Three things are left off, being the ones a reduced box cannot host honestly:
the contents (there is nothing packed inside it, so the walls' relief and the
seam's stand-off have nothing to dodge), the hopper throat (the placed funnel's
collar does not fit the shrunken top-wall frame), and the front panel's single
CO2 bore (its one real relationship — its height over the front seam — lands
behind the display facet in a box this short).

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
laps, none butts** — the form suited to the face. Because that shiplap lives
inside the slab rather than standing proud, it does not push the seam ahead of the
core: the seam still sits behind the core's front face, near the box's middle, and
the four pieces come out near quarters.

That seam runs the box's whole height, so it is pinned at **six levels** per side
wall, not once near the top — a wall above the floor, one under each Z seam, one
over each of their lip rims, and one under the ceiling, so every piece crossing
it is pinned at both ends of its own span. Because the Z seams stagger, a level
pairs whichever front and back piece meet at that height — the brick bond.
Bottom↔top, per column: the same joint rotated 90°, at `z_joint_front` (the front
stack's waist, above the condenser) and `z_joint_back` (the back-wall band
between the cold core's foam-cap top and the rear bulkhead field) — the bottom
pieces carry a 3-sided
lip + socket pods, the top pieces carry the D-pins and the posts that carry
them, more X-axis screws crossing each seam. The front pair joins, the
back pair joins, then the front assembly telescopes into the back as one.

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

**The Y seam is pinned at a level for each end of each piece that crosses it**,
and both Z seams count, so six levels rather than one pair near the top: a wall
above the floor, one under each Z seam, one over each of their lip rims, and one
under the ceiling.

**What makes all of that fit is where the walls stand.** The cold core spans the
interior wall to wall and floor to its cap, and it is what sets the box width, so
a wall laid on its face would leave the seam machinery nowhere to stand. The **±X
walls stand one `_contents.SIDE_RIB_INSET` off the core** — the boss chain's own
reach — and the **back wall one `_contents.REAR_STANDOFF`**, the rear Z-seam
lip's own thickness. The core sits flat on the floor: the print-corner relief
runs on the standing verticals and the Y-seam's floor lap stays inside the slab,
so the seat is square and there is nothing standing there for the core to clear.

So the core seats flush against the **seams**, not against the walls. Every post
has its full section, both walls carry all six levels, and the rear station's
post runs its own corner the whole way to the floor.

Those bands also set where the Y seam falls. Its full-width furniture clears the
core two ways: the lip's ceiling segment stops ahead of it, so the **lip rim
lands on the core's front face**, and the floor's shiplap passes beneath it in the
slab. The mouth, plugs, pods and posts reach further aft than that but live only
in the bands, so they pass alongside the core rather than stopping at it. What caps them is measured from whatever stands in the
bands, not tabulated. The seam therefore sits close to the box's middle, and the
four pieces come out near quarters.

`_contents.REAR_STANDOFF` is the single source for the back wall: `_port_frame()`
seats the rear panel bodies against it and `enclosure.py` builds the box to it,
so the wall the bulkheads mount through and the wall the box is built to cannot
drift apart.

The crowding mechanism stays in place even though nothing is crowded now: a post
necks to whatever is measured clear at its wall with 45° run-outs, and no level
is offered where the necking would leave a socket with no body to bore. It reads
zero on both walls today, and the build prints each wall's levels so a wall that
ever loses one is visible rather than silent.

The cold core rides in the back-bottom piece, verified clear of every boss at
build time. Each printed piece fits the H2C left-nozzle build envelope
(325 × 320 × 320 mm) even though the whole enclosure does not — that is the
point of the split.

## Refrigeration mounts

The compressor, its sheet-metal shroud and the condenser/fan are the only
contents the box holds by its own printed features rather than by a tray, so
their mounts are the box's. All of them stand below the front Z seam and land
whole in the **front-bottom** piece — the floor under the shroud and the
condenser, and the +X wall the condenser's fan shroud screws to.

One fastener vocabulary throughout, the seams' own: an **M3 SHCS into a ruthex
M3 heat-set** (Ø4.0 × 5.25), the insert bored from the face the screw arrives
at with a 3 mm blind relief past it, so no stock screw length can jack on the
bottom of its pocket. `boss_reach` is that whole chain and is how deep every
one of these bosses stands behind the face it presents.

The floor stratum stands one `_contents.SEAM_CLEAR_LIFT` off the floor slab.
That stance is a **seat**: a band under the shroud's rim, two rails under the
condenser's footprint, and the compressor's pads rising from it. A band and
rails, not slabs — a slab under a whole footprint is the same landing and
several times the plastic.

- **Compressor** — four pads on the floor under the donor's feet, each with a
  heat-set on a vertical axis (a hole up the build axis, no arc to droop). The
  factory rubber grommet stays in each foot and **is** the isolation element:
  the pad is what its lower flange lands on, and the screw runs through a
  spacer sleeve inside the grommet, so the clamp closes sleeve-to-pad and the
  rubber is left free to work. The foot pattern is
  [100 × 65 mm](COMP_FOOT_PITCH) — an **estimate**; the donor's is not
  recorded, and measuring it moves the pads by changing one pair of numbers.
- **Shroud** — the two Ø4.5 mm holes already in its side walls, read off the
  placed part rather than re-derived from the shroud's frame and `_contents`'
  turn of it. Their axes run along Y, so each boss stands **inside** the
  shroud against the wall it backs and the screw arrives from outside: the
  front one through the front wall, its head counterbored in the exterior face
  (the seam idiom), the rear one from the machine corridor. Inside is where the
  depth is — outside, the front wall stands 3 mm ahead of the shroud's front
  face and the corridor's floor gas sensor 1 mm behind its rear one. A
  **register** rising inside the shroud's own walls locates it in plan, so the
  two screws are left holding it down and not aligning it.
- **Condenser/fan** — the donor fan shroud's ears, in the block's +X (exhaust)
  face, taken by pads on two webs bridging the channel to the +X wall. The
  block's weight rides the floor rails, not the webs; the webs stop it moving.
  Each pad runs out at 45° above and below to the web's thickness, because a
  pad standing straight on a narrower web starts its first layer out over open
  air on both sides. The ear pattern is [82.5 × 82.5 mm](COND_EAR_PITCH) — an
  **estimate** (a 92 mm axial fan's, square about the fan axis, which is the
  block face's own centre); the donor shroud is not yet separated. A pattern
  taller than the stratum raises rather than silently colliding with the front
  Z seam's lip band.

`main()` prints every station it placed, so a measured compressor and a
separated fan shroud have a list to be checked against.

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

## Display housing

A flat 45° facet on the top-front-left carries the
[Waveshare ESP32-S3-Touch-LCD-4.3B config display](/hardware/reference/waveshare-43b-display/),
facing up-and-forward (−Y front / +Z up) toward the standing user, flush to the
−X (left) edge. The facet surface is sized to the bezel + a 3 mm buffer all
around — [119.5 mm](DISPLAY_FACET_X) (X, lateral) × [83 mm](DISPLAY_FACET_SLOPE)
(along the 45° slope).

The facet is thickened into a 19 mm housing (the display's overall depth) with
the display let in. The glass is the datum: a shallow 2 mm bezel counterbore,
centered on the facet (corners rounded 2.5 mm to match the glass), recesses the
glass with the 3 mm buffer uniform all around. The glass overhangs the body
unevenly (further up-and-left), so the 106 × 69 mm PCB through-hole sits offset
the opposite way; where the corner pod sits behind the facet, the hole takes it
clean through.

The whole housing is cut into the box itself, flush with the front wall: the
facet chamfers the top-front-left corner away and the back plane stands one
housing depth behind it. Both are the housing's own 45° planes — the facet above,
the back plane as its soffit — so the frame holds one constant thickness through
the corner. The cut spans the facet window from the −X edge; east of the window
the top-front corner runs on unbroken.

The recessed panel is sealed from the cavity at both lateral edges: the −X edge
by the left exterior wall, the +X edge by a one-wall gusset spanning the full
housing depth (inner front wall, inner top wall, housing back plane), continuous
with the slab. The display reference is seated in the housing in
`../enclosure-assembly/`.

Ceiling-down the housing lies flat, and every one of its faces — the facet and
its back plane as the soffit — is 45° or vertical to the bed, so none of them is
an overhang.

One localised cost follows from the Z-face orientation, shared with the other
pieces: the panel bores that were vertical when the build axis was Y are
horizontal now, so their top arcs would droop without a teardrop (not applied).
That covers the front CO2 inlet here and the four Ø18 bulkhead ports plus the
C14 cutout in the back-top piece's rear wall.

## Hopper opening

One rectangular opening spans the top wall right of the display housing, where
the removable silicone funnel
([`../../zone-c/hopper-funnel/`](/hardware/printed-parts/zone-c/hopper-funnel/))
drops in — its straight chute press-fitting the opening, its whole floor one
ramp falling to the spout descending toward V-B on the source-select assembly,
its flat brim resting on the wall frame left around the cut.
The funnel is a static placed part: the opening is cut at its collar
(`_hopper_hole` reads the funnel's own dims at `_contents.FUNNEL_CX/CY`), so
funnel and hole cannot drift apart. The frame that cut leaves is bounded by the
display end-wall gusset left, the top-right corner pod's inboard end, the
Y-seam lip band behind (the hole lives whole in the front-top piece), and the
kept front ledge — and the collar is asserted to sit one `brim_margin` inside
it on all four sides at once, so the opening is centred in what the top wall
has to give rather than crowding one edge. That margin is the brim's landing:
it is wider than the flange's overhang, so a full overhang's width of wall
remains outboard of the brim edge the whole way around.

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
