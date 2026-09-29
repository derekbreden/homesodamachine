# a1b Hand shuttle: the same pallet, moved by hand between seated stations

## Picture it

A branch of [a1](a1-pallet-tour.md). The XY stage goes away. The person moves
the pallet from station to station and works a lever at each. Each station has
its own seat, which gives the position the stage gave in a1. The crimp stroke
is a hand lever too. Sketch: a1's
[`../sketches/a1-pallet-tour.svg`](../sketches/a1-pallet-tour.svg) shows the
same pallet and stations.

**The bench.** A baseplate carries the stations in a row: zip
([a7](a7-zip-station.md), its hand comb on a rail), fan press, flush cut,
strip ([a8](a8-rolling-ring-scorer.md), its knob-and-lever block), crimp, and
insert ([a6](a6-housing-as-last-comb.md), its hand jig).

**Seats.** Every station has a **kinematic seat** for the pallet:
- three 6 mm chrome steel balls under the pallet;
- at each station, three seats, each a pair of the same balls pressed into a
  printed block, or two short lengths of case-hardened rod laid side by side;
- a disc magnet under each seat pulls the pallet home.

This is a Maxwell coupling: three balls in three radial grooves, six contact
points, exact constraint ([source](https://en.wikipedia.org/wiki/Kinematic_coupling)).
With hardened steel on hardened steel and magnet preload, the pallet should
return to within about 0.01–0.02 mm [estimate], through a printed body. The
seat parts must be hardened: at 10–40 N of magnet pull the contacts see
1,050–2,070 MPa, which dents the Prime row's precision-ground 304 stainless
dowels and stays elastic on 52100 balls or case-hardened rod [calc F §1].

**Moving the pallet.** The person lifts it off one seat and sets it on the
next, and it clicks home. Motions that follow a path run on rails with stops:
the zip slides forward into the tine comb to a stop at the split length; the
strip pull-off slides back against a stop after the blades close.

**The crimp station.** An X rail with ball detents at 5.0 mm crimp pitch and a
Y slide with a hard stop.
1. The person clicks the pallet to conductor k and pushes it forward to the
   stop. A fixed cam at the stop presses that conductor's tongue down and lays
   it into the waiting contact (a1's tongue).
2. The person pulls the press lever through one stroke and **stops just after
   the crimpers clear the contact**, before the feed finger moves.
3. They draw the pallet back to the Y stop, then finish the lever's return, and
   the feed brings the next contact. A hand lever pauses by itself, which
   removes the pre-feed collision with no electronics.
4. They click to the next detent. The tongue has sprung up and lifted the
   crimped conductor.

**The press.** A hand press that strokes an applicator to its shut height:
- the VEVOR 12-ton press's own jack, with a printed adapter on its ram and a
  hard-stop collar landing on the applicator frame (borrowed-machines'
  zero-build test of [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)),
  already on the bench;
- a TE 91085-2-class manual arbor frame [prior-art §4];
- or the $79.98 KAMsnaps DK93 snap press as a guided lever frame for harvested
  applicator blades (borrowed-machines' notebook; its force is unpublished).

**What locates what, and the reference for fixed.** "Fixed" is each station's
seat; at the crimp station, the anvil, to which the seat, rail and detents are
referenced. The pallet does the remembering: every position the hand would
otherwise find is a seat, a stop or a detent. Laterally and axially as a1.

**What drives the crimp and carries its force.** The person's lever, through
the press, to the applicator: ram → crimpers → contact → anvil → frame. The
person's hand holds only the pallet against a stop.

**How it knows.** The person looks: a loupe, or the ELP camera on a stand fixed
to the crimp station, frames every crimp at the same place. A hand stroke gives
under one HX711 sample in the last 0.2 mm [calc X §10], so there is no force
curve. The proof pull at insertion ([a6](a6-housing-as-last-comb.md)) and a
continuity check by hand follow.

**What the person does.** Everything the stage did: carrying, sliding and
indexing, every press stroke and the pause in it, and watching every crimp. Plus
a1's loading, housing supply and far ends.

## Steps it covers and what it hands back

- **Machine (by fixture):** contact supply from the reel through the
  applicator's feed; placement of each contact on its conductor, by the tongue
  cam when the person pushes to the stop; every position by seat, stop or
  detent.
- **Person:** cut, load, every motion between stations, every lever and
  stroke, the pause, the look, insertion by hand jig, the far end.
- **Person's time.** About 65 attended minutes a unit on procedure-is-the-machine's
  task library, against ~46 for today's hand procedure [P3 §7, estimate]. The
  cost sits in per-end preparation at the seats (cut, load, zip, fan, flush
  cut, strip, seat, lift). What a1b buys is not minutes: contacts that arrive
  by themselves, dies at a dialled height, and positions that come from steel
  stops.

## The SN-2549 variant, and why it needs the conductors folded away

A version whose crimp station is the bench's iCrimp SN-2549 clamped in a stand
meets a geometric conflict [calc X §6, borrowed-machines]:
- a ratchet tool's die axis is normal to its jaw plane; with contacts along Y
  and the crimp in Z, the jaw lies along X, the row direction, toward its pivot;
- at 5 mm pitch every neighbour within the jaw's 20–40 mm span [estimate] is
  under or over a jaw;
- at the captive click the conductor must go in along its own axis, and
  neighbours held at h meet the jaw's front face.

So the SN-2549 version works only with the neighbours folded out of the plane.
That combines a1b's seats and detents with borrowed-machines'
[b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md)
fold-back cassette (every conductor but the active one folded back 180° over
the pallet) and [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md)'s
SN-2549 in a frame, with a strip feeder, a box gripper and a blade stop. The
person folds one conductor forward, slides the pallet to its stop and taps a
pedal. The contact is never touched by hand. What stays uncertain is the
SN-2549's crimp on this ribbon and the person's time per crimp (~10–15 s
[estimate, borrowed-machines]).

A different way to put the SN-2549 to work with no fold-back is
[a10b](a10b-tacked-row-into-the-hand-tool.md): every contact is docked and
tacked on its conductor first, and the tool only closes.

## Why keep this branch

- **Cost of trying.** The pallet, one fan block with tongues, the seats and the
  hand zip and strip blocks can be printed and tried before anything is
  motorised. With the applicator on the VEVOR jack, only the applicator is
  bought.
- **Derek's priority step.** The contact arrives by itself from the strip, the
  lay-in comes from pushing the pallet to a stop, and the crimp from one lever
  stroke.

## Major unresolved problems

- **Everything a1 carries:** the applicator's upstream envelope under the
  neighbours at h, and the 30–47 mm split the tongue costs.
- **A person-dependent pause.** Whether a person reliably stops the lever
  between crimp and feed. A detent or a light on the lever's path could mark it.
- **Whether seats beat rails.** One long rail carrying the pallet past all
  stations, with a detent at each, keeps one reference throughout; six seats let
  the stations sit anywhere.
- **Attended time above today's** (above).
- **The applicator is a long-lead item** with no Prime listing.

## Related ideas

- Parent: [a1](a1-pallet-tour.md). Sibling: [a1c](a1c-crimp-upstream-first-park-after.md).
- No-motor relatives in this directory: [a2d](a2d-by-hand.md),
  [a10b](a10b-tacked-row-into-the-hand-tool.md).
- Other explorers: borrowed-machines
  [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md),
  [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md),
  [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md).

## What rests on assumptions

- Kinematic seat repeatability through a printed body [estimate].
- That the VEVOR jack with a hard-stop collar, or a hand lever frame, reaches
  the applicator's shut height repeatably [assumption; borrowed-machines'
  ground].
- Person-time figures [estimate, one task library].

## Labels

As [a1](a1-pallet-tour.md#labels); [calc F §n] is
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt).
