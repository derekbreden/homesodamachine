# p3 Terminate at the spool, cut last

Sketch: [`../sketches/p3-spool-cut-last.svg`](../sketches/p3-spool-cut-last.svg)
(schematic side view). Order diagram:
[`../sketches/orders-of-work.svg`](../sketches/orders-of-work.svg). Numbers: the first
calcs in [`../calc/`](../calc/) by name, [`../calc/wave2.out.txt`](../calc/wave2.out.txt)
and [`../calc/wave3.out.txt`](../calc/wave3.out.txt) (cited as [calc wave2 §n]
and [calc wave3 §n]).

**The order change:** today's procedure cuts first and terminates second [repo
cable-assemblies.md]. Here the XH end is made on the free end of the ribbon
**while it is still on the spool**. The loom is fed out to length and cut free
only after the end has passed every check. Five things follow:
1. **The spool is the carrier.** The ribbon is never loose until it is finished.
2. **A redo costs spool, never a loom.** No loom carries a length reserve.
3. **The rest of the spool is a test lead.** With the spool's inner end wired to
   a slip ring, every conductor of the new end is tested for opens, shorts and
   identity before the cut.
4. **The cut that frees one loom squares the next end.**
5. **The machine runs one ribbon type for hours**, across several units.

ribbon-as-pallet [a4](../../ribbon-as-pallet/ideas/a4-spool-as-magazine.md) and
change-the-question [c5](../../change-the-question/ideas/c5-ends-as-stock.md)
reached the same order independently. [p6](p6-spool-end-bench-that-grows.md) is
the path to it from today's bench, done by hand at a clamp with no motor and
motors joining one step at a time; [p3b](p3b-ribbon-ams-whole-unit.md) mounts
every spool at once; [p6b](p6b-reel-end-docks-on-a-strip.md) docks the reel's end
onto a contact strip.

## Picture it: the 4P spool, making J11 and then J1's 4P half

**Setup (person, once per spool).**
- The 4P spool (15.24 m [repo]) goes on an axle behind the machine. Its **inner
  end** has been stripped and put in a spare XH housing that plugs into a socket
  on the axle, wired through a 6-circuit slip ring [Prime: 12.5 mm capsule slip
  ring, 6 × 2 A, $9.99; or Adafruit 736, $14.95, in stock (source:
  adafruit.com/product/736)] to the tester.
- If the BNTECHGO spool's inner end cannot be reached, the person rewinds the
  spool once onto a printed reel with an 80 mm hub radius through a roller
  straightener, bringing the inner end out through the hub (~5 minutes with the
  HOTO screwdriver or the drill press [estimate]; p6).
- The free end runs between two belts of a **belt feed** (what ribbon machines use
  against slip [prior-art §1]), past an **encoder wheel**, into a flat **work
  clamp** on a short X slide.
- The person loads a tube of XHP-4 housings and picks the run: "4P, five units".
  The machine's list is J3, J5, J9, J11, J13, J1-4P and J4-4P, five times over,
  each with its loom length.

**Per end, e.g. J11 (4P into XHP-4, ~600 mm leg).**
1. The feed pushes the end forward until the tip breaks a light beam at the clamp
   face [Prime: IR break-beam pair, 3 mm, $9.99], and the clamp closes.
2. **Trim** at the clamp face with the guillotine; on every end after the first,
   the previous cut did it.
3. **Strip and split.** [p7](p7-strip-before-split.md)'s whole-end stroke while
   the web holds the pitch, then a zip or razor comb from the slug's gap; or split
   ~30 mm first with three razors in the web valleys pressed onto a grooved anvil
   [prior-art §1] and strip each conductor in its lifted pose. A fan comb steers
   the conductors to 2.5 mm.
4. **Place and crimp**, per conductor, at a lift-once station at the clamp (this
   view's C1 combination with hand-tool-as-press
   [a3](../../hand-tool-as-press/ideas/a3-tool-travels-to-ribbon.md)'s module). The
   clamp's X slide brings *k* to the station line; a lift finger raises it; the
   station stands in either of two forms, both crimping upright:
   - **the SN module on its side** ([p1c](p1c-lift-once-tip-down-module.md)):
     lift 8.7–14.7 mm, a 30–35 mm split and a squaring push after each crimp;
     contacts picked from a post revolver loaded in loom order;
   - **the fin from below** ([p1d](p1d-lift-once-fin-from-below.md)): lift
     3.5 mm, a 20–25 mm split; contacts slid onto each conductor from a two-tier
     post bar; made steel.

   The slip ring is the far-end electrode **during** the crimp: at the end of the
   wing curl the head's steel touches strands through the contact, and exactly one
   conductor reads closed through the spool. That checks identity before any
   copper is formed, and confirms J2's and J7's trimmed conductors absent. The
   whole spool anchors the copper, so the 20 N proof pull through the box tests
   the crimp alone.
5. **Look**: a camera frame of the crimp, and the head's force curve.
6. **Insert.** An XHP-4 drops from the tube into a nest in front of the squared,
   upright row and slides back onto all four contacts (gang). The nest pulls back
   5–10 N to check seating.
7. **Test through the spool.** P75 pogo pins [Prime: MEETOOT P75-E2, $6.49] touch
   each contact through the housing's mating face; the tester drives each
   conductor in turn from the inner end: each pin ~0.1–0.9 Ω depending on how much
   spool is left, every other pin open. Opens, adjacent shorts and swapped
   conductors show; a crimp's own milliohms against ~0.9 Ω of spool do not [calc
   spool_test §1].
8. **Feed out and cut.** The clamp opens. A small carriage on a GT2 belt along a
   rail at the bench front clips the ribbon just behind the housing and **pulls**
   the loom length out, read by the encoder wheel (±3–6 mm on 600 mm at 0.5–1 %
   slip [calc spool_test §4]). The housing is never the handle, so the spool's
   drag never passes through a crimp. The guillotine cuts: ~250 N straight across
   four conductors, or 40–65 N per conductor with an angled blade [calc spool_test
   §3]. J11 drops into a bin; the new end is square.
   - **The drop-tube form**, the housing leading the loom down a tube by gravity
     from a bench edge, is the alternative where bench front is short; pushing
     floppy ribbon into the tube is its weak point.

**J1's 4P half** (straight into cavities 6–9 of an XHP-9 [repo pcba.tsx: OUT3,
OUT2, OUT1, COM]) is made the same way into an XHP-9 from a second tube, with only
cavities 6–9 filled, and leaves **half-housed**. When the 5P spool's run makes
J1's 5P half, the person clips the half-housed 4P end into a **partner nest**
beside the work clamp, the 5P's five contacts go into cavities 1–5, and the test
through the 5P spool checks cavities 1–5 and their isolation from 6–9.
- **J2** is made from one 3P spool, one ribbon after the other: 3P-b into
  cavities 4–6, then 3P-a's first two into cavities 1–2 of the same housing via
  the partner nest, its third conductor cut back at the split by the program.
- **J4 and J7** need their crossings [into-the-housing]. The machine makes and
  tests both ribbon ends and leaves them unhoused, contacts held in order in a
  printed **parking comb**. The person inserts both into the real XHP-7 at an
  insertion jig.

**What the person does.** Changes spools (about three per ~5 units once runs are
batched by spool); loads the post revolvers or post bars in loom order (~4 s a
contact [estimate]); loads housing tubes; clips half-housed ends into the partner
nest; inserts J4's and J7's ends at a jig; labels; makes every far end after the
cut, as today. That is ~16 attended minutes a unit for the XH work, and the
longest unattended stretch is the 4P run: five units' worth, 35 ends and 140
crimps in ~5–6 h [calc person_timeline; estimates].

## Batching this order makes natural

| Spool | Ends per unit | Units per spool | One run makes |
|---|---:|---:|---|
| 4P | 7 (J1, J3, J4, J5, J9, J11, J13) | ~5.4 | 35 ends, 140 crimps |
| 5P | 3 (J1, J6, J7) | ~11 | 33 ends, 165 crimps |
| 3P | 4 (J2 ×2, J4, J7) | ~8 | 32 ends, 80 crimps |

[calc unit_inventory §4; J3's leg assumed 300 mm]. A spool's life is a natural
batch, which asks whether Derek will hold finished looms ahead of units (5–11
units' worth of each type). Batching per unit instead means three spool changes a
unit, ~9 minutes [estimate].

## Recovery, in numbers

- A bad end is cut ~6 mm back and remade (4.5–6.7 mm [calc recovery_length §1]).
- At a 2 % bad-crimp rate that uses ~7 mm of spool a unit; at 10 %, ~43 mm, 0.7 %
  of the ribbon [calc recovery_length §4].
- No loom is ever short or scrapped for its XH end, and a pair's two ribbons stay
  equal, because each is cut to length only after it has passed. In cut-first
  orders the same 10 % rate with a 12 mm allowance scraps ~35 looms over the
  program [calc recovery_length §3].
- The far end is made after the cut, so the automated risk comes before any hand
  work.

## What locates what

| Moment | Located | Against |
|---|---|---|
| Start of an end | tip | light beam at the clamp face, then the clamp |
| Trim | tips | guillotine at the clamp face (frame) |
| Crimp | conductor, contact, crimp height | the lift-once station's own references (p1c or p1d) |
| Insert | housing | nest on the frame |
| Length | loom | encoder wheel from the clamp face |

"Fixed" is the machine frame throughout. The ribbon is registered once per end,
at its own tip, and never moves until feed-out.

## What drives the crimp and carries its force

The lift-once station's own drive: a NEMA 17 Tr8×2 on the SN's handle (p1c) or on
a knee inside a steel C (p1d). The force closes inside the module or the C; the
clamp, the X slide and the frame carry positioning loads only.

## How it knows it worked

Crimp force and position, identity through the spool at each crimp, a camera
frame, the proof pull through the box, the seating pull, and opens, shorts and pin
identity through the spool after insertion, all before the loom exists as a
separate thing. A loom that reaches the bin has passed everything the machine can
check.

## Steps it covers, and what it hands back

- **Automated:** trim, split, strip, place the contact on the conductor, crimp,
  look, identity at each crimp, insert (single-ribbon ends and the first ribbon of
  straight pairs), test through the spool, measure length, cut.
- **Handed back:** spool changes, housing tubes, loading posts, clipping
  half-housed ends into the partner nest, J4/J7 insertion at a jig, labelling,
  every far end.

## Printed and bought

- **Printed:** the reel (if needed), axle socket, roller straightener, belt-feed
  frame, clamp, splitter holder, fan comb, housing tube and nest, partner nest,
  parking combs, puller carriage (or drop-tube guide), the station's lift finger,
  carriages and posts.
- **Bought** (Prime rows observed 2026-09-28): slip ring ($9.99); P75 pogo pins
  ($6.49); GT2 pulleys ($5.99) and belt; an encoder [Prime, search result only:
  bare 600 P/R encoder, $18.99] with a printed wheel (the Prime wheel-and-bracket
  kit gives only 20 counts per 10 mm [Prime: CALT GHW38, $81.00]); IR break-beam
  ($9.99); single-edge blades ($12.90/100); NEMA 17 T8×2 screws ($27.99) for the
  guillotine and slides; the station's parts (p1c or p1d).

## Problems, and what answers each

1. **Pairs need two spools at the work point at once.** Not if the pair's housing
   waits on the first ribbon: half-housed ends and the partner nest. p3b mounts
   all spools instead.
2. **The loom has to be fed out through the tools.** The housing leads forward
   out through the clamp face, which opens wide, and the tools are above and
   beside it; only the guillotine is in line, and it retracts below.
3. **A test lead to a turning spool's inner end winds up**, 30–80 turns over a
   spool's life [calc spool_test §2], so a slip ring is needed. Its contact
   resistance adds to ~0.1–0.9 Ω of spool and does not matter for open/short
   detection.
4. **Batching across units means inventory.** The alternative is three spool
   changes a unit, which suits an attended session.
5. **J4 and J7 need a crossing** and go to the person. A changed ribbon
   assignment would make J7 straight (GND on the 3P, the 5P's fifth conductor
   trimmed), Derek's call. No assignment makes J4 straight without splitting one
   of its pairs [inference from repo pcba.tsx J4 order 3V3, GND, V5, IO25, IO26,
   IO27, IO23].
6. **Spool curl.** Off a 25 mm hub radius a 40 mm free end rises 3–15 mm [calc
   wave2 §2]. The clamp flattens it up to its face; a straightener before the
   clamp, or the 80 mm reel, removes it.

## Contribution

The order change with the largest consequences found in this view. Terminating
first makes recovery free, makes testing possible before the loom exists, gives
the slip ring an identity check before every crimp, and gives the unattended run
its length. It keeps every crimp mechanism of the lift-once stations, so the crimp
work is shared.

## Major unresolved problems

- **The spool's inner end**: reachable, or a rewind per spool.
- **Machine web splitting** on this silicone (as p1b), or p7's slug gap as the
  split's start.
- **The puller's clip on silicone** at a few newtons, untested; a fold round a bar
  in the clip multiplies its grip (ribbon-as-pallet a3's fold).
- **Half-housed ends travelling in a bin**, exposed to snagging; the partner-nest
  step needs the person to find the right half-end.
- **The lift-once station's own open problems** (p1c: *a* and a 30–35 mm split;
  p1d: the steel).
- **Silicone stripping**, as everywhere.

## What rests on assumptions

- Service loop 50 mm, J3 300 mm, the spool hub size, ~6 mm redo cut-back.
- Belt-feed slip on silicone of 0.5–1 %.
- The redo cost assumes every bad crimp is caught before feed-out; a fault found
  at the unit's final test is a cut-first repair.
