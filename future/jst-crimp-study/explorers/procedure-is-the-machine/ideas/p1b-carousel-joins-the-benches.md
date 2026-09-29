# p1b Carousel joins the benches

Sketch: [`../sketches/p1b-carousel.svg`](../sketches/p1b-carousel.svg) (schematic
plan view). Numbers: the first calcs in [`../calc/`](../calc/) by name.

**A branch of [p1](p1-cassette-and-benches.md).** The person stops carrying
cassettes. p1's benches become stations bolted around a turntable, unchanged, and
the turntable carries a unit's cassettes past them. A web splitter joins station
A, so the person also stops peeling. This is where p1's build order ends if every
step pays off.

## Picture it: a unit in one loading

**Loading (person).**
- The person cuts the unit's 14 ribbons square to length, as in p1.
- Each end is laid flat in its cassette **without peeling**: the clamp takes the
  webbed ribbon and the tips stick out ~40 mm.
- J4 and J7 are the exception: their crossing conductor is peeled free by hand and
  laid over its neighbours into its key through the loft before the station splits
  the rest.
- The person drops the ten cassettes into the carousel's nests, tails in their trays
  toward the centre, loads an XHP housing into each cassette's front nest, and
  walks away.

**The turntable.**
- A 300 mm lazy-susan bearing [Prime: 12 in lazy susan bearing, $22.99] carries a
  printed ring of 12 nests.
- A GT2 belt round the rim and a NEMA 17 turn it 30° per index, about 31:1 at the
  rim [calc transfer_capture §1].
- A spring ball plunger [Prime: uxcell M8 ball plungers, $7.79] drops into a notch
  at each index, so the carousel delivers each nest within ±0.1–0.3 mm, or
  ±0.5–1 mm with play in the belt.
- That is all it has to do. At each station, dowels or three balls rise through the
  nest and lift the cassette 1–2 mm off the ring onto the station's own reference,
  which captures ±1.5–3 mm [calc transfer_capture §1]. The carousel's error never
  reaches the work.

**The stations, clockwise from the person.**
1. **Load and unload** (the person's place).
2. **A: strip, split, trim.**
   - **Strip, webbed.** [p7](p7-strip-before-split.md)'s two razors across the whole
     webbed end, pads on the slug, 2.4 mm from a flush cut along the cassette's own
     blade slot.
   - **Split.** A printed holder carries N−1 single-edge razor blades at 1.7 mm
     pitch [Prime: single-edge razor blades, $12.90 per 100], each seated in the
     valley between two round conductors, entering from the slug's gap and pressed
     down through the web over ~30 mm onto a grooved anvil [prior-art §1,
     "punching"], slowly, by a lead screw.
   - **Fan.** A fan comb closes over the split conductors and steers them to 2.5 mm
     into the cassette's comb, by their insulation.
3. **B: place and crimp.** p1's bench B in one of its three forms, each with its
   own slide:
   - **B-fin** ([p1d](p1d-lift-once-fin-from-below.md)): a lift finger, a two-tier
     post bar on the nest, and a small steel C whose fin rises through the lifted
     conductor's empty slot; what reaches in toward the ring is the finger, the
     post bar's Y slide and the C's throat;
   - **B-lift** ([p1c](p1c-lift-once-tip-down-module.md)): a lift finger, a Y
     carriage with an X shuttle bringing trim, strip and an SN-2549 module lying on
     its side, and a post revolver;
   - **B-drop**: the presser, the V-fork, the stepped fin and a ram, sitting outside
     the ring and reaching in with its slide.
4. **Look.** The ELP camera under a ring light takes every contact in the row in
   one or two frames, a second opinion on the frames bench B took of each crimp.
5. **C: insert.** The cassette's housing nest pushes the housing back onto all the
   upright contacts at once (gang), then a push-then-pull check: the housing seats
   before a set force, and a 5–10 N back-pull does not move it (Boeing's "force
   before distance" [prior-art §5]).
6. **Test header and label.** The housing mates onto a header wired to a tester and,
   through the cassette's far-end pogo block, is tested pin to pin: opens, shorts,
   J2's cavity 3 open. A label printer, or a printed tag the person adds, names the
   loom from the cassette ID.

**Knowing it worked.** Every station reads the cassette ID and logs its result. A
failed cassette is not unloaded mid-ring; it rides round to the person's station
flagged "redo". On the redo lap the person slides the ribbon out ~6 mm, and the
cassette goes round again: station A strips and splits the extra length and trims
the old contacts off [calc recovery_length §1].

**What the person does.** Cut the ribbons and lay them in; make J4's and J7's
crossings; load housings; unload and label; handle any redo lap. About 19 attended
minutes a unit, the carousel running ~2.2 h alone [calc person_timeline;
estimates].

## Why a ring

- **One place for the person.** Cassettes come back to where they left.
- **Stations stay p1's benches**, each with its own slide and pins, so a station
  can be lifted off the ring and used alone for testing, or while another is
  rebuilt.
- **Tails** coiled flat in trays pointing to the centre ride round without swinging;
  at one index every few minutes nothing swings anyway.
- **A linear conveyor is the same idea opened out**, taking more length and
  returning cassettes to the far end unless it loops.

## What locates what

The same as p1: every station lifts the cassette onto its own pins, and "fixed" is
each station's frame. The ring only brings a cassette within the capture of those
pins.

## What drives the crimp and carries its force

Bench B's own drive, closed inside its steel C, SN module or ram frame (p1d, p1c,
p1). The ring and the lift pins carry positioning loads only.

## Steps it covers, and what it hands back

- **Automated:** strip, split, trim, place the contact on the conductor, crimp,
  look, insert, pin-to-pin test.
- **Handed back:** cutting ribbons and laying them in, J4/J7 crossings, loading
  housings and the posts, unloading, labelling, redo laps.

## Printed and bought

- **Printed:** the ring in keyed segments screwed to the bearing's top plate; nests
  with pockets for the stations' lift pins; the splitter blade holder and grooved
  anvil; the fan comb; station bases.
- **Bought** (Prime rows observed 2026-09-28): the lazy-susan bearing ($22.99); GT2
  pulleys [Prime: $5.99] and belt; ball plungers ($7.79); NEMA 17s for the ring and
  each station's lift; razor blades ($12.90). p1's benches and controller are
  reused; five stations need two SKR Pico boards [Prime: $35.99 each] or one larger
  board.

## Problems, and what answers each

1. **A turntable cannot index to 0.05 mm.** It does not need to: stations lift the
   cassette onto their own pins [calc transfer_capture §1].
2. **Stations fight for room around a ring.** Twelve nests at ~R 185 mm give
   ~95 mm of arc each. Bench B is the bulky one: in B-fin and B-lift it is a small
   module on rails whose force closes inside itself; in B-drop it is a ram and a
   fin outside the ring. Two nests can stay empty as buffers either side of it.
3. **The redo lap re-bends conductors that already carry set.** In B-drop the
   conductors pressed on the first lap arrive low again. In B-fin and B-lift the
   waiting conductors were never pressed, and each crimped one was squared.
4. **Splitting the web by machine may nick insulation.** Unknown: the web's
   thickness and notch depth are unstated [xh-facts §7, Unresolved 6]. The blades
   sit in the valleys, which steer them, and enter from the slug's gap; a blade
   off-centre by more than the valley's width cuts into insulation. Interlaced
   toothed jaws (US 4,179,964) and scalloped cutters (US 4,046,045) are the prior
   art's alternatives [prior-art §1]. If splitting fails, station A becomes "person
   peels", ~9 more minutes a unit [estimate, 14 ends × 40 s].
5. **Crossings (J4, J7)** cannot be made by a straight splitter-and-fan: the person
   peels the crossing conductor by hand at loading, and the station splits only the
   rest. Whether a splitter works round a conductor already peeled is open.

## Contribution

The carousel adds no crimp mechanism of its own. It shows that the joined-up
machine is p1's benches plus a delivery device of modest accuracy, so nothing
already built is thrown away, and it shows where the person's remaining minutes go
once the benches exist: loading, crossings, labels.

## Major unresolved problems

- **Machine web splitting on silicone** (problem 4).
- **J4 and J7** keep a hand step, or need a changed ribbon assignment (Questions for
  Derek, in the notebook).
- **Five stations' worth of motors and wiring** for 53 crimps a unit; each station
  is simple, the total is not. [p5](p5-camshaft-one-revolution-per-conductor.md)'s
  camshaft collapses stations A and B into one motor.
- **Cassette ID at every station**: a misread runs the wrong program; the test
  header is the backstop.

## What rests on assumptions

- Carousel accuracy, lead-in capture and the station layout [estimate].
- The splitter's behaviour on this web.
- The ~2.2 h unattended run assumes ~115 s per conductor for strip, crimp and insert
  combined [estimate].
