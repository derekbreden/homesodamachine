# a2d By hand: dock the pallets, then slide the cassette under a guided hand press

## Picture it

A branch of [a2](a2-two-pallets-meet.md) with no motors. The person docks the
ribbon pallet onto the strip pallet by hand. The docked cassette slides on
detents at strip pitch under one pair of applicator dies in a guided hand frame,
and the person strokes once per contact. It is the cheapest experiment that
tests a2's core: whether every contact can be placed on its conductor by one
docking motion. Sketch: a2's
[`../sketches/a2-two-pallets-meet.svg`](../sketches/a2-two-pallets-meet.svg)
shows the docked cassette.

1. **Load the strip.** Snip N + 2 contacts off the strip, lay them on the slot
   pins, flip the clamp bar down and the support comb up. The comb and the rail
   carry a groove along X under the lance line, so no contact sits propped on
   its lance [w3 §5].
2. **Dock.** Set the ribbon pallet, hand-zipped, fanned, flush-cut and stripped
   on the bench blocks of [a7](a7-zip-station.md) and
   [a8](a8-rolling-ring-scorer.md), onto its three hardened seats. The magnets
   click it home and every conductor goes into its contact; a finger comb on the
   pallet presses them in if the open wings are narrower than the jacket
   [calc F §4].
3. **Look and test.** Photograph the docked row, and touch a meter from each
   conductor's far end to the carrier. This step needs no crimp tool and
   answers most of a2 by itself.
4. **Crimp each contact.** The cassette rides a printed rail with ball detents
   at strip pitch under a **guided hand frame** holding one crimper-and-anvil
   pair: a harvested OTP applicator set, or an OTP knife set bought alone
   (terminal-supply; no Prime listing). The frame is the VEVOR 12-ton press's
   own jack with a printed adapter and a hard-stop collar (borrowed-machines'
   zero-build test), or the $79.98 KAMsnaps DK93 snap press (force
   unpublished). At each detent the anvil sits under one contact's barrels and
   the crimper above; the person strokes once to the stop, lifts, and slides on.
5. **Pull.** The shear comb's pad comes down on the crimped barrels, and a
   luggage scale on a hook pulls each conductor at the fan block's face to
   ~20 N. Without the pad the tab pitches at 2.5–4.6 N [w3 §4].
6. **Shear.** The shear comb of [a2](a2-two-pallets-meet.md), on a lever.
7. **Insert** with a printed insertion jig ([a6](a6-housing-as-last-comb.md)).

**What locates what, and the reference for fixed.** "Fixed" is the strip
pallet's slot pins until the crimp; at each stroke, the frame's anvil, to which
the rail's detents are referenced. Placement as a2.

**What drives the crimp and carries its force.** The person's pump or lever,
through the frame, vertically through a narrow die pair: frame → crimper →
contact → anvil → frame. The carriage and pallets carry none of it. The force
comes through a die pair, not a jaw lying along the row.

**How it knows.** The person looks, through a loupe or the camera on a stand,
and pulls every crimp at step 5. Continuity is checked before the crimp and
after insertion.

**What the person does.** Every motion and every stroke, but no finding: the
strip pallet has the contacts where they belong, the ribbon pallet has the
conductors where they belong, the seats bring them together, and the detents
bring the dies to each one.

## Steps it covers and what it hands back

- **Fixture:** placement of every contact on its conductor by one docking;
  every position by pins, seats and detents.
- **Person:** preparation at the bench blocks, strip segments, docking, every
  stroke, pull, shear, insertion, far ends. Roughly 2–3 minutes of hand work
  per 5P at the crimp alone [estimate].

## Why not a ratchet hand crimper on the rail

A ratchet crimper's die axis is normal to its jaw plane, so with contacts along
Y and the crimp in Z the jaw lies along X, the row, toward its pivot. At 7.1 mm
pitch 1–4 neighbours lie within its 10–30 mm nest-to-pivot extent [calc X §6].
Cutting the jaw down removes the far side, never the pivot side. Using every
other contact (14.2 mm) leaves 0–2 neighbours in the way, wastes half the strip
and doubles the fan. JST's YRS-110, made "to crimp the applicable contact in
strip form" ($1,565.93 [xh-facts §2]), is the bought route; whether its body
clears the next contact is not stated [assumption].

The SN-2549 on the bench does enter the picture once every contact has left
the carrier on its own conductor: [a10b](a10b-tacked-row-into-the-hand-tool.md)
tacks the docked row and crimps each contact in the hand tool.

## What this tests cheaply

- **Placement by docking:** do the conductors go into the open barrels, strands
  inside the conductor wings and jacket inside the insulation wings? Steps 1–3
  decide most of a2 with no crimp at all.
- **Fan block fit** at the measured strip pitch.
- **Cantilevered contacts:** do they stay put when the support comb swings away?
- **The crimp on this ribbon** from real applicator dies, stroked slowly.

## Major unresolved problems

- **A harvested die pair in a hand frame:** punch-to-anvil alignment without the
  applicator's side block; the snap press's ram play is unknown.
- **The frame's hard stop:** a pumped jack cannot stop precisely by itself, so
  the collar sets bottom [estimate].
- **The dies are a long-lead purchase** (eBay, AliExpress), so the crimp half of
  a2d waits on them; steps 1–3 do not.

## Related ideas

- Parent: [a2](a2-two-pallets-meet.md). Motor versions: [a2e](a2e-docked-strip-through-a-feedless-applicator.md),
  [a2b](a2b-gang-press-stop-die.md). The hand-tool route after a tack:
  [a10b](a10b-tacked-row-into-the-hand-tool.md).
- No-motor relative with an applicator: [a1b](a1b-hand-shuttle.md).
- Other explorers: borrowed-machines
  [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)
  (the jack test).

## What rests on assumptions

- Strip pitch ~7.1 mm [Würth analog].
- YRS-110 body clearance [assumption]; hand-frame alignment [assumption].

## Labels

As [a1](a1-pallet-tour.md#labels) and [a2](a2-two-pallets-meet.md#labels).
