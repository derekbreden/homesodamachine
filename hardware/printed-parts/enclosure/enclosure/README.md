# Enclosure

A PETG box, 3 mm walls, sized live to the bounding box of the contents placed
by [`../enclosure-assembly/_contents.py`](/hardware/printed-parts/enclosure/enclosure-assembly/_contents.py),
**split into four printable pieces** — front/back × bottom/top, every piece
inside the H2C bed — that telescope and screw together. The Y seam sits as
close to the box's midpoint as the cold core allows, and each column takes its
bottom↔top seam at its own height (the seams stagger like a brick bond): the
back-bottom piece houses the cold core, the back-top covers the band above it
— the electronics shelf on the foam-cap top and every panel port (the whole
external-connection inventory penetrates its rear wall, above the cold core);
the front column splits at its waist over the condenser — refrigeration below,
the valve tray + funnel + display above.

`enclosure.py` exports the four printable pieces (`enclosure-front-bottom`,
`enclosure-front-top`, `enclosure-back-bottom`, `enclosure-back-top`) plus
`enclosure.step` — the four as separate solids in assembled position, seams
intact (mirrors `faucet/touch-flo-shell`). It also exports two test-print
coupons over the shared Y-seam mating geometry: `enclosure-front-coupon.step`,
a reduced-size front (~156 × 101 × 116 mm) carrying every feature at full size
(the display housing, the telescoping lip, the corner bosses, the ribs), and
`enclosure-back-coupon.step`, the matching back (~156 × 40 × 116 mm) — its
mouth, plugs, and screw bores aligned to the front coupon's lip and sockets.

## Seams + bosses

Three seams, one joint idiom. Front↔back: the front pieces' full-wall rear lip
telescopes into the back pieces, cross-pinned with M3 screws driven from the ±X
exterior. That seam runs the box's whole height, so it is pinned at **four
levels** per side wall, not once near the top — a wall above the floor and just
under the front Z seam (those two pin the bottom pieces at both ends of their
span), just over that seam's lip rim and under the ceiling (those two pin the
top pieces). Because the Z seams stagger, a level pairs whichever front and back
piece meet at that height — the brick bond. A seam pinned at one end of a piece
and nothing else hinges at the other; front-bottom carried both its stations in
the top 20 mm of a 188 mm piece before this. Bottom↔top, per column: the same joint rotated
90°, at `z_joint_front` (the front stack's waist, above the condenser) and
`z_joint_back` (the one back-wall band left open between the cold core's
foam-cap top and the rear bulkhead field) — the bottom pieces carry a 3-sided
lip + socket pods, the top pieces carry the D-pins and the braces that back
them, more X-axis screws crossing each seam. The front pair joins, the
back pair joins, then the front assembly telescopes into the back as one.

A Z seam is pinned at **both ends of its column**, not just one, or the far end
hinges open. The back column runs from the Y seam clear to the rear wall, so it
takes a station just behind the Y-seam mouth *and* one in the rear-wall corner.
The front column keeps a single front-wall station: the source-select assembly
fills the depth its seam crosses, leaving no rear station to be had there
without moving that assembly.
Each cross-pin mates the walls of its overlap (the
pin's mouth-side face on the receiving mouth, the socket pod's rim-side face
on the lip rim) and the two are coaxial by construction, so the **overlap
depth is derived from those matings**, not chosen — it works out to
(plug + bore)/2 + one wall.

Each cross-pin is sized to its job. Reading an M3×10 screw outboard→inboard from
the ±X exterior: a Ø6.15 mm head counterbore, then the pin body (the screw spans
the head seat to the heat-set, so the body is screw length − heat-set long), then
the heat-set, then a one-wall cap.

- **Receiving piece = D-pin** (the back pieces on the Y seam, the top pieces on
  the Z seam): a Ø9.9 mm cylinder (the shank + one wall each side, *not* the
  head — the head sits in the wall counterbore) from the exterior to the
  heat-set, registering in the socket bore, fused to a flat tab that runs to
  the lip rim, where the corner post behind it backs the pin in Y.
- **Lip piece = socket** (the front pieces / the bottom pieces): a pod bored
  Ø10.3 mm to take the round pin as a slide fit, with the ruthex M3 heat-set
  (Ø4.0 × 5.25) capped at its deep inboard end and a channel the pin's tab
  slides through as the lip telescopes home.

The top pieces carry braces above their Z-seam pins, running from the lip rim to
the ceiling they print against.

**Every boss stands on a post of its own section, run to the bed face.** Not a
collar on a spine — the whole socket footprint, carried the full height of its
piece: floor to the seam below, seam to the ceiling above. Printed Z-down that is
the face the piece lies on, so there is material under every part of the boss the
whole way down and the piece simply stacks; a narrower stalk would leave the
socket cantilevered over open air on the layer it starts, which is the overhang
that needs print support. The two pieces' posts meet at the seam, so assembled
the corner reads one column floor to ceiling — which is also the corner stiffener
a printed shell this size wants. The back pieces get the same post behind the lip
rim at the pin's own depth; before, their pins and braces hung off the wall with
nothing beneath them.

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
runs on the standing verticals, so the floor is square and there is nothing down
there to clear.

So the core seats flush against the **seams**, not against the walls. Every post
has its full section, both walls carry all six levels, and the rear station's
post runs its own corner the whole way to the floor.

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

The Y-seam lip is the one joint the orientation costs something. It is the
telescoping tongue, so its floor and ceiling segments jut one overlap past the
body into the space the mating piece's own floor and ceiling occupy — a
cantilever that cannot be buttressed without colliding with the back piece, and
so wants print support. The side-wall segments, vertical to the bed, are free.

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
funnel and hole cannot drift apart, and the cut asserts the top-wall frame
accommodates the placement — the display end-wall gusset left, the top-right
corner pod's inboard end, the Y-seam lip band behind (the hole lives whole in
the front-top piece), and the kept front ledge.

## Regenerate

`tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure/enclosure.py`
→ the four `enclosure-*.step` pieces + `enclosure.step`. Wall, seam, boss, and
facet constants are at the top of `enclosure.py`. Prints the facet size, each
piece's envelope vs. the H2C bed, every piece-pair's slip fit, and the
cold-core clearance.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/enclosure/enclosure.py`
