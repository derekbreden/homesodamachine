# a4c — Every cavity's post at once: bare contacts crimped on a post bed through the housing, one push

Branch of [`a4b-through-cavity-post.md`](a4b-through-cavity-post.md), and a
combination. **What it changes:** a4b puts one post through one cavity, crimps
on its tip and pushes that contact home before the next, so each conductor must
carry ~14 mm of extra length at its crimp. a4c stands a post through **every**
cavity at once, puts a bare contact on each post tip, crimps them all where they
stand, and seats every contact with one move of the housing. Nothing is stored in
any conductor.

**Sources.**
- this explorer's [a4b](a4b-through-cavity-post.md): a post through the cavity,
  a bare contact mated on its tip, the crimp 9 mm clear of the rear face;
- into-the-housing's [i6b](../../into-the-housing/ideas/i6b-post-bed-through-the-housing.md):
  a bed of posts at 2.50 mm through the housing, each post wired as an
  electrode, a backing blade behind the barrels and one housing move that seats
  every contact (i6b threads crimped contacts onto the posts; a4c crimps bare
  ones on them);
- into-the-housing's [i2b](../../into-the-housing/ideas/i2b-preload-the-whole-housing.md)
  and [i6](../../into-the-housing/ideas/i6-sort-then-push.md): odd cavities, then
  even, because clone wings collide at 2.5 mm pitch; lower layer first for J4
  and J7.

Sketch: [`../sketches/a4c-post-bed-one-push.svg`](../sketches/a4c-post-bed-one-push.svg) (schematic).
Numbers: [`../calc/w3.py`](../calc/w3.py) §1–3, §7, §8 [w3 §n]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
calc [ith-w3 X].

**Related.** [x3](x3-stage-crimp-one-push.md) is the same order with the
contacts staged 1.5 mm inside the housing's mouth instead of 9 mm out on posts.
How far out the contacts stand is a dial between the two (below).

## Picture it

- **The bed.** A small PCB drilled at 2.50 mm pitch (not 2.54: across nine
  positions that would be 0.32 mm, ±0.16 mm at the ends [w3 §8]) carries square
  0.64 mm steel pins pressed in, one per cavity of the loom's housing, ~25 mm
  long. J2's post 3 is left out. Each post is wired to an ESP32 input, and the
  loom's far end sits in a terminal block, so every conductor is its own circuit.
- **The housing.** The person slides the housing onto the posts, mating face
  first, down to a stop near the bed, so the posts stand ~9 mm out of its rear
  face. The housing rests in a nest on a Y slide driven by a NEMA 17 on a T8
  screw through a 20 kg load cell (into-the-housing i3's push drive).
- **One pallet.** The bed, the housing nest and the web clamp with its root comb
  are one pallet on an X stage, so the ribbon never moves relative to the housing
  while contacts are being crimped. The dies, the camera, the contact shuttle and
  the picker finger are the fixed station.
- **The ribbon end.** Split and stripped, its conductors fanned to 2.5 mm at a
  root comb in pin-map order. A loft at the root holds the even conductors (and
  J4's and J7's upper-layer conductors) ~4 mm up; the odd conductors lie in the
  post plane.
- **Odd pass.** For each odd cavity:
  1. A shuttle nest with a lance groove along its floor and low side walls
     (≤ 4.06 mm wide, clearing the bare even posts at 2.18 mm from the axis
     [w3 §8]) slides a bare contact along the post's axis until the tip enters
     the box, and its rear wall pushes the box on, 1.5–1.8 mm.
  2. The finger presses odd conductor k into the open barrels. Continuity from
     the loom's far end to post k now reads closed: this conductor is in this
     contact, before anything is crimped.
  3. The anvil rises under the barrels 1.0–4.5 mm beyond the post tips; every
     post ends before the barrels, so the dies never meet the bare neighbour
     posts, and with the even conductors lifted, ordinary knife-set dies fit
     [w3 §8].
  4. The punch crimps onto its hard stop. A fork in the neck, bearing on the
     box's rear shoulder, takes a ~20 N proof pull on the wire while the camera
     watches the insulation edge.
- **Even pass.** For each even cavity, between crimped neighbours whose boxes
  stand 1.525 mm from the station axis:
  1. A tongue nest (≤ 2.75 mm wide, lance groove, no side walls above the floor)
     slides the bare contact onto post k. The open wings clear the crimped
     neighbours' insulation barrels by +0.03 (3.0 mm wings) to +0.30 mm (2.46 mm)
     [w3 §7].
  2. The finger lowers even conductor k from the loft into the barrels;
     continuity to post k closes.
  3. Narrow stepped dies crimp it: a 3.1 mm conductor step with 0.8 mm walls
     (+0.20 mm to the crimped neighbours' conductor barrels) and a 2.5–2.7 mm
     insulation step (+0.17–0.28 mm), the walls landing on the anvil's shoulders
     (into-the-housing i2, force-and-form f8) [w3 §7].
  4. Proof pull as in the odd pass.
- **Upper layer last.** J4's 3V3 and GND and J7's GND come down from the loft
  last, crossing over the placed conductors at the root, into cavities at an end
  of the housing [into-the-housing i6].
- **One push.** A slotted backing blade drops behind every insulation barrel,
  straddling the wires. The nest drives the housing along the posts, away from
  the bed, 13.95–14.45 mm, onto every contact at once [w3 §3; ith-w3 A]. The posts
  guide each box into its cavity; the blade holds each contact still on its post
  while the lance folds and snaps; the load cell logs the lance events. Nothing
  was stored in any conductor, so nothing bows.
- **Test and release.** The housing is now mated on the posts as it will be on
  the board's header. Continuity per post, adjacent shorts, J2's missing post 3
  and the J4/J7 identity are read here; JST asks for continuity checks against
  the applicable header [mfr S5]. The blade lifts; a 5 N pull-back per wire
  confirms each latch (above the 0.2–2 N post grip, below the 14.7–19.6 N
  retention [w3 §9]). The housing is pulled straight off the posts, within 15°
  [mfr S5].
- **What the person does.** Slides a housing onto the bed; lays the split,
  stripped ribbon end in the root comb and loft; keeps the contact supply
  filled; lifts the finished end off and labels it (J4 and J7 share a housing).

## What locates what

| Moment | Reference | Located part |
|---|---|---|
| Housing on the bed | the posts through its front openings; the nest stop | cavities |
| Bare contact on its post | the post (in plane); the nest's floor and lance groove (height at loading) | contact |
| Conductor in the barrels | the root comb and the finger; the insulation edge as seen | conductor |
| Crimp | anvil and punch lead-in; the post is soft and only carries | barrels |
| Push | posts (the box's line into its cavity), backing blade (each contact's rear) | every contact |
| Seat | the housing's own shoulders | every contact |

**The reference for "fixed" during crimping is the station's anvil block**, with
the pallet (bed, nest, web clamp) stepped past it and parked by a detent.
**During the push it is the bed and the backing blade,** against which the
housing moves.

## What drives and carries the crimp force

The crimp (0.8–2.6 kN) closes punch → barrels → anvil → station block, onto the
hard stop; the posts carry none of it. Posts cantilevered 17–19 mm are soft,
1.2–1.7 N/mm, so the die centres the barrels for 0.2–0.3 N of post bending
[w3 §8]. The push-on at loading (0.2–2 N) is far below the posts' buckling load
(19–24 N) [w3 §8]. The gang push (39–88 N at the KONNRA clone's 9.8 N per
contact, up to 225 N with margin on J1 [w3 §7]) goes from the nest through the
housing into the contacts and the backing blade, and into the bed.

## How it knows it worked

- The contact on its post, seen before the conductor arrives.
- Continuity from the far end to post k when the conductor lies in the barrels:
  the right conductor in the right contact, before the crimp.
- Stop and force trace for each crimp; the proof-pull trace.
- The push trace (one lance event per contact in the sum).
- Continuity per post and adjacent shorts after the push, on the posts that are
  now a header; the 5 N pull-back per wire.

## Where the contacts stand: a dial between a4c and x3

How far out of the rear face the contacts are crimped is a free choice:

| Box front at the crimp | Push | Dies | Contacts held by |
|---|---|---|---|
| 1.5 mm inside the mouth ([x3](x3-stage-crimp-one-push.md)) | 5.25–5.45 mm | within ~1 mm of the housing face; flat anvil window ~0.06 mm or a lance slot | the mouth's friction and the conductor |
| ~7.5 mm outside, on posts (a4c) | 13.95–14.45 mm | clear of the housing | the posts, every one wired |

Both crimp every contact of a housing at one Y and seat them with one move, so
neither stores length. Any stagger in Y between neighbours at the crimp would be
stored in the finished loom by that one push [w3 §3].

## Problems and repairs

1. **Clone wings collide at 2.5 mm pitch** (−0.50 to +0.04 mm), so not every
   post can carry an open contact at once. Repair: odd, then even. Genuine
   contacts inside JST's 1.95 mm envelope would let every post be loaded at once,
   but the 3.1 mm conductor step then clears an open neighbour's conductor barrel
   by only 0.00–0.11 mm [ith-w3 J].
2. **The even pass has no room for ordinary dies.** Repair: narrow stepped dies
   bottoming on anvil shoulders. They are made, not bought (into-the-housing's
   own open problem).
3. **The waiting conductors lie beside the dies.** Fanned flat at 2.5 mm they meet
   a 3.5 mm punch by 0.10 mm [w3 §7]. Repair: the loft keeps them ~4 mm up.
4. **A walled nest cannot reach between crimped neighbours.** Repair: the tongue
   nest for the even pass, which relies on the lance in its groove for lateral
   position (±0.1–0.25 mm, inside the pin's capture with a near-pointed tip
   [w3 §1, §2]).
5. **The posts must be at 2.50 mm, not 2.54.** Repair: a drilled PCB bed, as
   i6b. A 2.54 mm long-pin header strip is off by ±0.06 mm on a 4-way and
   ±0.16 mm on a 9-way [w3 §8].
6. **Does laid-in stranded copper close continuity to an open barrel?** The
   finger presses the strands onto the barrel floor, tin on tin, at a light load.
   Plausible, unmeasured; if not, the check moves to just after the crimp.

## Steps covered, and what it hands back

- **Covers:** placing each contact (bare, onto its post, in its own cavity's
  line); placing each conductor in its contact in pin-map order, crossings
  included; an identity check before each crimp; crimping; a proof pull before
  insertion; insertion by one move; continuity, shorts and latch checks on a
  mated header.
- **Hands back:** splay and strip; loading the housing onto the bed and the
  ribbon into the root comb; keeping the contact supply filled; labelling.

## Printed and bought

| Part | Printed / bought |
|---|---|
| Post bed | a small PCB drilled at 2.50 mm with 0.64 mm square steel pins pressed in (hardened square pins in [`../sourcing-requests.md`](../sourcing-requests.md) #16; the uxcell 25 mm-pin headers, Prime, $15.49, are 2.54 mm pitch and suit only 4- and 5-way beds) |
| Nest on a Y slide, root comb, loft, finger, shuttle and tongue nests with lance grooves | printed (0.2 mm nozzle for the combs [repo tools.md]) |
| Backing blade | laminated stencil-steel foil, slotted at 2.5 mm (JLCPCB stencil, from $3 [source, via into-the-housing]) |
| Nest drive | Iverntech NEMA 17 with Tr8×2 screw (Prime, $27.99); 20 kg bar cell ([`../sourcing-requests.md`](../sourcing-requests.md) #29) |
| Station dies | a knife set for the odd pass; narrow stepped crimper and shouldered anvil for the even pass (EDM or ground; force-and-form f7 sets out die sources) |
| Controller inputs | an ESP32, one input per post |

## Contribution

The post as holder, guide and electrode for every contact of a housing at once.
Bare, rigid contacts go onto the posts, so threading is easy; every conductor is
identified in its contact before its crimp; every crimp is made at its final
position relative to the web; and one move seats the whole housing on what is,
at that moment, its own header.

## Major unresolved problems

- **The narrow stepped dies** for the even pass.
- **The post's path through each cavity** past the housing's inner features (one
  flashlight photograph).
- **Soft posts at 17–19 mm free,** and whether the box stays square on a post tip
  as the wings first curl.
- **The front-wall thickness,** which sets the push (assumed 0.8–1.0 mm).
- **Laid-in continuity** before the crimp.
- **Machine time,** ~2–2.5 h per unit by the same step count as x3 [w3 §7,
  estimate].

## What each conclusion rests on

- **Facts [mfr, source]:** 2.50 mm pitch and housing height [xh-facts §3]; JST's
  handling precautions on mating tests and straight withdrawal [mfr S5]; clone
  wing widths [xh-facts §1]; Prime listings.
- **Calculations [calc]:** push length [w3 §3; ith-w3 A]; post stiffness and
  buckling, die region beyond the tips, nest widths, 2.54 mm error [w3 §8];
  even-pass clearances [w3 §7; ith-w3 C, J]; capture and lance groove [w3 §1,
  §2]; force ladder [w3 §9].
- **Estimates:** gang push force per contact; machine time.
- **Assumptions:** the cavity is clear on its axis; the front wall is 0.8–1.0 mm;
  laid-in strands close a circuit to the barrel; post grip 0.2–2 N (secondhand
  Molex analog).
