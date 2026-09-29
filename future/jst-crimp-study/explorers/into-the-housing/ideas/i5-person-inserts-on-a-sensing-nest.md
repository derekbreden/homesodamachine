# i5 — The person starts each contact; a lever nest seats it, checks the cavity and tests the latch (with a proof-pull fork and crimp-height pocket: K4)

- **Sketch:** [`../sketches/i5-sensing-nest.svg`](../sketches/i5-sensing-nest.svg) (schematic);
  [`../sketches/latch-signature.svg`](../sketches/latch-signature.svg) for the trace it looks for.
- **Numbers:** [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt)
  [calc geometry §n], [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w3 X].
- **What it combines:**
  - K4, with force-and-form's proof-pull fork and 0.001 mm crimp-height pocket;
  - C3, with hand-tool-as-press [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md)'s
    far-end terminal block.
- **Related:** [i2d](i2d-locator-the-lance-never-touches.md) upstream (the stub
  on the SN-2549); change-the-question [c6b](../../change-the-question/ideas/c6b-by-hand-this-week.md)
  (its insertion step is this nest).

The bench station has three parts:
- the sensing nest;
- force-and-form's **proof-pull fork** and **crimp-height pocket** beside it;
- i2d's stub on the SN-2549 upstream.

Together they are a first bench that places, crimps, proves, measures and
inserts, with Derek's hands doing the aiming. None of it needs a motor.

## Picture it

**On the bench.**
- **The nest.** A small printed base holds a PCB carrying the five XH headers
  the appliance's board uses, side by side: B4B, B5B, B6B, B7B and B9B-XH-A.
  - Every post is wired to an ESP32 input with a pull-up.
  - The whole PCB sits on a 5 kg bar load cell, so any push or tug on a housing
    is weighed.
- **The lever carriage.** Behind the headers, a carriage runs on a short X rail
  with detents at 2.5 mm, moved by hand or by a small stepper.
  - It carries a slotted pusher blade of stacked stencil foil.
  - The lever drives the blade +Y through a spring, so it can never push harder
    than the spring's trip force. A switch opens at ~20 N.
- **The far end.** The loom's far end sits in a push-in terminal block, each
  conductor a separate line driven by the ESP32.
- **Beside the nest, two checks for the crimp** (K4):
  - a **proof-pull fork**: a steel fork on a second load cell. The person drops
    a crimped contact's barrels into it, box forward, and pulls the wire until
    the ESP32 beeps at ~20 N, half of JST's 39.2 N;
  - a **crimp-height pocket**: a point-and-blade anvil under a 0.001 mm
    indicator on a lever, read by the same ESP32 [force-and-form metrology §1].
- **A small screen** shows the loom being built (J1…J13), the pin map, and which
  cavity is next. An LED on the carriage lights over it.

**One contact.**
1. The person crimps it on the SN-2549, with i2d's stub as the locator (or as
   today).
2. **Prove and measure.** The person drops the crimp into the fork and pulls to
   the beep, then sets it in the pocket and lowers the indicator. The ESP32 logs
   both against the loom and pin.
   - This happens before insertion, because a ~20 N proof load would pull a
     latched contact out of its cavity. force-and-form's force ladder: 5 N
     latch test < 14.7 N retention (analog) < 19.6 N proof < 39.2 N pull-out.
3. The person plugs the housing onto its header. The four-sided shroud lets it
   go on only one way, so Circuit 1 is right by construction [mfr S12].
4. The person starts the box into the lit cavity by hand, ~2 mm, lance down.
   This is the only aiming, the part hands do well.
5. **Seat.** The person pulls the lever.
   - The blade drops behind the insulation barrel, straddling the wire, and
     pushes. It follows up to ~2 mm into the cavity, since a seated rear lies
     0–1.8 mm inside the rear face [calc w3 H].
   - A magnetic angle sensor on the pivot gives the blade's position, and the
     load cell logs force against it.
   - When the box slides onto post n, the post sees the conductor the ESP32 is
     driving: it knows **which conductor reached which cavity**, and at what
     blade position.
   - The push ends at the spring's trip.
6. **Tug.** The blade backs off 1 mm, and the person tugs the wire lightly (the
   load cell reads up to ~5 N). The blade comes forward until it touches the
   barrel. Touching within ~0.1 mm of before means the contact did not move:
   latched.
7. The screen marks the cavity green and moves the LED. For J2 it skips cavity 3,
   and at the end confirms post 3 never saw a contact.

**When the housing is full.** There is a per-cavity record: crimp proof load,
crimp height, conductor and cavity, seating trace, tug. The person pulls the
housing off, holding the housing, within 15° of straight, as JST asks [mfr S5].

## At a glance

| | |
|---|---|
| **What locates the contact** | The person's hand to the cavity mouth; then the cavity walls and, for the last millimetres, the header post |
| **Reference for "fixed"** | The header's posts and shroud, soldered to the PCB and fixed to the base; the carriage detents registered to the posts |
| **Crimp force** | Upstream, by hand on the SN-2549. The nest's own force is the spring-limited seat, ≤ ~20 N |
| **How it knows** | The fork's proof load and the pocket's crimp height per crimp; the conductor-to-post circuit; the seating trace (fold, snap, wall); the tug and re-touch; J2's post 3 never closing |
| **Steps it covers** | Verify the crimp (proof pull and crimp height), insert (the seat), cavity identification and pin order, latch check, order guidance |
| **What it hands back** | Crimping (by hand, with i2d's stub); dropping each crimp in the fork and pocket; starting every contact ~2 mm into its lit cavity; J4's and J7's crossings by hand |

## Why this arrangement exists

- Insertion is the dexterous step. The cheapest machine that takes over its
  judgement, not its dexterity, leaves the aiming to the person and makes the
  rest certain:
  - force, by a spring;
  - cavity, by the real mating post;
  - latch, by a tug on the load cell;
  - order, by screen and LED, as in Yazaki's light-guided insertion [context
    prior-art §5].
- It pairs with any crimp machine from any explorer, and works on day one with
  hand crimps.
- With the fork and pocket, **every hand crimp's height and proof load are logged
  in normal production**. That is also the SN-2549 measurement the whole study
  is waiting on.
- **The real header is the nest.** JST's handling precautions say continuity and
  miswiring checks must use "the applicable mating (shrouded header and header,
  etc.)" [mfr S5]. B4B-XH-A: Newark 171,802 in stock at $0.07–0.28. B9B-XH-A:
  Digi-Key 44,226 at $0.17–0.34 (findchips, 2026-09-28) [source].

## Mechanism, references and tolerances

**Inserting into a mated housing.**
- The contact is pushed onto a post already in its cavity: the same relative
  motion as mating a loaded housing onto a header [assumption: harmless].
- The insertion force rises by one contact's share of mating force, unknown for
  XH [mfr S16].
- The post also centres the box for the last few millimetres.

**What continuity proves.** The box touching post n proves the cavity and a depth
at least to the post tip, not the latch; the tug does that.

**Driving from the far end** (C3).
- The ESP32 drives conductor k and every header post listens.
- When k's box arrives on post n, the record pairs **conductor with cavity**
  directly, not only "something reached cavity n". J4's and J7's crossings, and
  a J4/J7 swap, are caught at the moment they are made.
- The blade then needs no electrical path through the tin: it is a plain
  spring-limited pusher.
- The same block serves hand-tool-as-press a1's touch-off at the crimp, so each
  conductor has one record from its crimp curve to its seating trace.

**Post grip against the tug.** A box's spring on a 0.64 mm post probably
withdraws at ~0.5–2 N [estimate, force-and-form], under the 5 N tug. So an
unlatched contact still slides under the tug. Measure both with one contact:
unlatched on the post (lance held down with a pin through the window), and
latched.

**The trace doubles as a lance check.** A lance flattened by crimp tooling shows
as a missing fold rise and snap.

**A reference trace.** JST's own factory crimp on a 22 AWG lead
(ASXHSXH22K305, $0.90 at Digi-Key [source, via change-the-question c2]),
pushed into a kit housing on this nest, gives a genuine contact's fold, snap and
wall to compare every kit contact against.

**Spring-limited lever.** 20 N over 1.5 mm of spring travel is a ~13 N/mm spring
[calc geometry §6], printable as a PETG flexure.

## Printed and bought parts

| Part | Source |
|---|---|
| Header PCB | Five B*B-XH-A headers [source above]; board from JLCPCB [repo: `hardware/pcb/pcba/order.md`] |
| Controller | ESP32 dev board [repo: `CLAUDE.md`, shared context] |
| Load cells, ADC | ShangHJ 5 kg bar cells with HX711, $9.99 for 2, Prime-confirmed [sourcing/amazon-prime.md]; or Adafruit #4541 $3.95 and #5974 $9.95 [source] |
| Blade, fork | Stacked stencil foil ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil), from $3) [source] |
| Crimp-height indicator | Clockwise Tools DITR-0105, 0.001 mm with RS232 port, $52.99, Prime-confirmed; its DTCR-01 data cable had no Prime listing [sourcing/amazon-prime.md]. A point-and-blade anvil under it |
| Lever angle sensor | UMLIFE AS5600 boards, $7.99 for 3, Prime-confirmed (magnet inclusion not stated) [sourcing/amazon-prime.md] |
| Far-end terminal block | Wago 221-415 lever nuts, $28.00 for 25, Prime-confirmed [sourcing/amazon-prime.md] |
| Force-trip switch | HiLetgo KW12-3 micro limit switches, $5.99 for 10, Prime-confirmed [sourcing/amazon-prime.md] |
| Lever, carriage, base, detents, pocket lever | Printed PETG |
| Optional click pickup | Small enclosed piezo, Adafruit #1740 $0.95 [source] |

## Problems met, and how it answers them

1. **The person still aims every contact.** Yes, that is the point. Aiming 53
   boxes 2 mm into lit cavities is minutes of easy work [estimate: ~8 s each,
   ~7 min per unit, calc geometry §8]; the fork and pocket add ~15 s a crimp.
2. **Mated insertion wears the contacts.** One extra mating cycle each. If it
   matters, a header with shortened posts that engage only the box's first
   ~0.5 mm.
3. **Which loom is this?** J4 and J7 share the 7-way header. The screen asks, and
   the far-end circuit confirms it at the first contact.
4. **J4 and J7 cross.** The person's hands make the crossing while starting each
   contact; the screen shows which cavity, in the order the pin map gives.
5. **The far end is not free.** If a loom's far end is already terminated in
   something the block cannot take, the blade becomes the electrode instead
   (wired to ground, with a spring finger that touches the barrel), and the post
   names only the cavity.

## Contribution

- A sensing nest any machine can share: header nest, conductor-to-post
  continuity, load cell under the header, force-limited blade.
- With the fork and pocket, a bench quality station for today's hand crimps. It
  also gathers the numbers every other arrangement needs: insertion traces,
  snap, retention, post grip, crimp height, proof load.
- An incremental path: i2d's stub on the SN-2549, then this bench, then any
  machine in place of the hand crimp.

## Major unresolved problems

- **Post grip against the latch** in the tug test.
- **The added mating force.**
- **Whether each loom's far end is free and strippable** while its board end is
  made (hand-tool-as-press's question).
- **Header shroud wear** over ~600 plug-and-unplug cycles.

## What rests on assumptions

- That pushing a contact onto a post from behind is harmless.
- That the header's shroud tolerates ~600 plug-and-unplug cycles (~60 units × 10
  housings).
- Post withdrawal 0.5–2 N [estimate].
