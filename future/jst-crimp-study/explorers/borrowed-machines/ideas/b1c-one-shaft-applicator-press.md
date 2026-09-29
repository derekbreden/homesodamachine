# b1c — One shaft: the applicator crank also turns the cams that lay in, withdraw and pull

**A combination:** [b1b](b1b-applicator-in-slow-crank-press.md) (the OTP
applicator in a slow crank press, this explorer) × **p5**, the camshaft that
turns once per conductor, from
[procedure-is-the-machine](../../procedure-is-the-machine/ideas/p5-camshaft-one-revolution-per-conductor.md).
Its gate and reject turn take terminal-supply's
[a1](../../terminal-supply/ideas/a1-applicator-slow-ram.md) supply-side gate.

**What each side brings.**
- **b1b:** the bought applicator does "place the contact, hold, crimp, cut the
  tab"; a 15 mm crank at bottom dead centre is the crimp; the strain-gauged rod
  with its disc-spring stack; the dwell after bottom dead centre.
- **p5:** the timing diagram is the machine. Printed face cams on the same shaft
  do the light motions, and a mechanical proof pull and switch cams do the
  checks.
- **What borrowing adds:** the sewing machine's and the applicator's own
  principle, one shaft timing everything, applied to the whole cycle rather
  than to the feed alone.

Sketch: [`../sketches/w2-b1c-timing.svg`](../sketches/w2-b1c-timing.svg)
(schematic timing diagram, drawn from the crank formula below).

Labels: [calc wave3 §n], [calc presses §n] are this explorer's
[`wave3.out.txt`](../calc/wave3.out.txt) and [`presses.out.txt`](../calc/presses.out.txt);
[TS §n] is terminal-supply's
[`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28).

## Picture it

**The machine.** b1b's crank unit under the shop press's top beam, with its
crankshaft extended outboard of one pillow block. On the extension sit printed
face cams (PET-CF) with roller followers on printed levers, and three switch
cams. A NEMA 23 turns the shaft through a 30:1 self-locking worm, one turn per
conductor in 30–40 s. An AS5600 magnetic encoder ($7.99 for three [Prime]) on
the shaft end reads angle.

**Where things start.** The applicator is in pre-feed: a contact waits open on
the anvil. b1's cassette sits on a small **X sub-slide** on top of the Y
shuttle, spring-returned forward and pulled back only by a cam lever. The
ribbon end is split, stripped and folded back as one flat band.

**One turn** (0° is top dead centre; the ram reaches bottom at 180°; a 30 mm
stroke on a 15 mm crank and 100 mm rod):

| Shaft angle | Ram above bottom | What happens | Driven by |
|---|---|---|---|
| 0° | 30 mm | **gate 0:** switch cam stops the shaft; the camera checks the waiting contact alone | switch cam, controller |
| 0–10° | 30 mm | fork tines descend into the valleys either side of conductor *i* | cam 1 |
| 10–50° | 29.8 → 25.3 mm | fork swings 180° and lays conductor *i* into the waiting contact | cam 2, lever, 4:1 sector onto the fork pinion |
| 50–58° | 25.3 → 23.8 mm | foot presses the conductor into both barrels | cam 3 |
| 60° | 23.3 mm | **gate 1:** switch cam stops the shaft; picture and far-end continuity; forward, or back to 0° | switch cam, controller |
| 140–185° | wings curl, then compaction | the crimp; HX711 force against encoder angle, ~78 samples through the last 0.2 mm at a 40 s turn [calc wave3 §3] | crank |
| 220° | 4 mm | crimpers clear the box; foot lifts | cam 3 |
| 222–248° | 4 → 11 mm | sub-slide drawn back 10 mm: the crimped contact slides out along its axis until its box roof meets a fixed catch | cam 4 |
| 248–262° | | **proof pull:** cam 4 goes 2 mm further through a ~10 N/mm pull spring, ~20 N on the box; a slipping crimp lets the sub-slide over-travel onto a switch | cam 4, spring, switch |
| ~266–285° | 15 → 20 mm | pre-feed finger moves; the anvil is already empty | applicator's own cam |
| 280–340° | | fork swings back and parks the crimped conductor in its place in the band; tines lift | cams 2 and 1 |
| 300–340° | | sub-slide returns forward on its spring | cam 4 |
| 340–360° | | switch cam tells the Y stepper to move one band position | switch cam, stepper |

Angles come from the crank formula for a crank above the ram [calc wave3 §0–2].
The feed's band is an assumption until the jack test measures it.

**Why the feed can never arrive on a crimped contact.** The cam that withdraws
the crimped contact is on the same shaft as the crank that drives the feed. No
controller decision can reorder them.

**Why the gate sits at 60°.** A cam-driven feed lever follows ram height
[assumption, WERI-pattern]. So on the way *down* the feed finger retracts to the
next pilot hole between ~75° and ~94° (ram 20 → 15 mm up) [calc wave3 §2].
Reversing the shaft back through that band would drive the finger forward
again and push a fresh contact under a laid-in, footed conductor. With lay-in
and seating finished by 58° and the gate at 60°, backing the shaft out to 0°
crosses nothing irreversible: the fork's cam carries the conductor back to the
band, and the foot lifts, because both are on the shaft.

**What the gate's answers do.**
- **Pass:** the shaft runs on through the crimp.
- **The conductor is off** (edge outside the window, a stray strand): back to 0°,
  the shuttle corrects X or Y, and the turn repeats.
- **The contact is bad** (gate 0, or gate 1 blaming the contact): back to 0° if
  needed, then a **reject turn**. The Y shuttle moves the band aside so the
  tines descend on nothing, and the shaft turns once. The fork swings empty, the
  crank crimps the bad contact empty and shears its tab, and between 225° and
  260° a cam switch opens a 24 V 5/2 valve (TAILONZ, $16.99 [Prime]) for a puff
  through a 1 mm nozzle that clears the crushed contact into a reject cup
  [calc wave3 §5]. The feed then brings the next contact, and gate 0 looks at it.

**What locates what; the reference for "fixed."**
- The applicator locates the contact.
- The fork's tines and the foot locate the conductor in the barrels; both pivot
  on brackets bolted to the applicator base.
- Every motion's timing is referenced to the crankshaft, and the force curve is
  plotted against the crankshaft's angle.
- The Y position is the shuttle's stepper, which only has to land inside the
  tines' valley capture.
- The fixed catch for the proof pull sits ~2.0 mm above the anvil's floor
  line, so the crimped barrels pass under it and the box roof, 0.4–0.6 mm
  higher, meets it; it stays above the floor and clear of the lance [TS §11].

**What drives the crimp and carries its force.**
- The crimp: the crank and the shop-press frame, as in b1b, through the
  disc-spring stack.
- The cams carry only light loads: fork, foot, sub-slide and a 20 N pull, each
  under ~50 N at the follower [estimate]. At a 30–60 mm cam radius that adds
  under ~1.5–3 N·m to the 3.8–5.4 N·m of crimp and applicator springs [calc
  presses §1].
- The worm self-locks, so the shaft holds any angle unpowered, including both
  gates.

**How it knows it worked.** The contact alone at gate 0; contact, conductor and
continuity at gate 1; force against shaft angle through the crimp; the
proof-pull switch; the stack's force switch; the camera in the dwell. A failure
before 60° backs out with nothing done; a failure after it stops the shaft
before 266°, with the crimped contact already out of the feed's way.

**What the person does.** As b1b: loads and folds cassettes, inserts, changes
reels, measures crimp height by sample, empties the reject cup. A redo is a
whole-end cut-back.

## Steps it covers and what it hands back

- **Covers:** supply contacts (reel), place the contact on the conductor,
  crimp, verify the crimp (two gates, force curve, spring-and-switch proof pull,
  stack switch, dwell picture), and the order of fork, foot, withdraw, pull and
  park, by mechanism.
- **Hands back:** as b1b.

## The fork's swing in 40° of shaft

Squeezing the fork's 180° swing into 10–50° steepens its cam. With a follower
arm of 15 mm, a lever throw of 45° through a **4:1 sector** onto the fork pinion,
and a cam track of ~**60 mm radius**, the peak pressure angle is ~26° under a
modified-sine law; a 30 mm track with a 3:1 sector would be ~53°, too steep
[calc wave3 §2]. So the fork cam is the machine's largest part.

**Branch inside b1c: a servo fork, permitted by the shaft.** The fork is light,
and only the ram and the feed must be tied to the shaft. The fork can be a servo
(as in b1b) that swings only while a shaft switch says 0–55°, and the shaft may
pass 58° only while a fork sensor says "laid in". Backing out is then a
controller act for the fork and a mechanical one for the foot.

## What stays from b1b and p5, and what does not

- **No skip mechanism.** p5's skip bump lifts the punch link for a blank
  cavity. In b1's band the unused conductors (J2's and J7's) have been trimmed
  at the root before folding, so there is no conductor at that place; the Y
  stepper does not stop there. J2's empty cavity 3 is an insertion matter.
- **Y stays a stepper.** p5's printed rack at the key pitch would be a 1.7 mm
  rack here, at the band's pitch, near the limit of a printed tooth.
- **Pre-feed stays.** The conductor is laid into a contact already in the die,
  which is what a hand-fed bench press does, and it gives both gates.

## Drives that fit a one-shaft machine

- **NEMA 23 + 30:1 self-locking worm** (StepperOnline NMRVS30, C$76.69, 20 N·m,
  ships in 24 h [force-and-form, source]; or the Heechoo 30:1 worm-gear NEMA 23,
  $120, output torque not stated [Prime]): stops anywhere; both gates are
  pauses.
- **A plain 12 V worm gearmotor at 1.5–2 rpm** with a cam stop switch (the wiper
  park principle, slowed down) and the AS5600 for the force curve. It needs
  ~6.5–7 N·m with margin. The self-locking 12 V worm motor on Prime (Greartisan,
  10 rpm, 40 kg·cm ≈ 3.9 N·m, $26.99 [Prime]) is too weak and too fast; a
  1.5–2 rpm, ≥7 N·m unit is a sourcing request. It cannot back out unless it is
  reversible, which the 60° gate needs.

## Contribution

- It turns b1b's software-timed dwell into a mechanical order: laying in,
  seating, crimping, withdrawing, pulling and parking happen in shaft angle, and
  the feed comes last because it is on the same shaft.
- A gate placed before the first irreversible angle, so "no" is a clean reverse.
- A proof pull made of a spring, a cam and a switch.
- A bad contact leaves by an empty turn and a timed puff of air.

## Major unresolved problems

- **The fork cam.** A ~60 mm track radius and a 4:1 printed sector: backlash of
  a few tenths of a degree at the fork, a few hundredths of a millimetre at the
  tines [estimate]; stiffness under the tines' drag unmeasured. The servo-fork
  branch avoids it.
- **Cam phasing** depends on the feed finger's real band, measured in b1b's jack
  test, and on the applicator's stroke (30 or 40 mm; on a 40 mm stroke the same
  heights fall at different angles [calc wave3 §1]).
- **Whether the feed lever really follows ram height.** If it is driven some
  other way, the retract band moves and so must the gate.
- **The fixed catch.** A 0.4–0.6 mm height band between the crimped insulation
  barrel and the box roof, on silicone whose insulation crimp height is
  unmeasured.
- **Clearance under the descending ram** for the fork swing, the stripper plate
  and the wire hold spring slot.
- **Cam wear** on PET-CF over ~3,200 turns under ~50 N: probably fine, untested.
- **Guarding** a shaft that moves the ram, a fork and a slide together.
- Everything open in b1 (tines in the band, applicator geometry, contact match)
  and b1b (crank disc, shop-press bed, blow-off).

## Disagreement on angles, with the physics

terminal-supply's calculation puts the crimpers clearing at 226° and the feed
at 274–293° [TS §6]. Those figures come from the slider-crank formula with the
rod's obliquity term subtracted, which is the geometry of a crank *below* a ram
it pulls down. b1b's crank is *above* the ram, so the ram's lowest point is the
rod's straight-in-line position and the term adds: a vector check puts the ram
4.0 mm above bottom at 40° from bottom dead centre (220° from top), not 46°
[calc wave3 §0]. Their point holds either way: a back-out from a late gate
re-crosses the feed finger's retract band on the downstroke. That band is
~75–94° here, and the 60° gate is placed from it.

## What rests on what

- **Derek:** the bench's NEMA 23 and DM542T, and the idle shop press [repo].
- **Facts:** applicator strokes and cams [facts §2]; contact heights [facts §1].
- **Calculations:** crank angles, the gate margin, cam pressure angles, samples,
  the reject window [calc wave3 §0–5]; crank torque [calc presses §1]; the catch
  heights [TS §11].
- **Estimates:** cam follower loads under ~50 N; sector backlash.
- **Assumptions:** the OTP feed finger moves at 15–20 mm of ram height, both ways;
  a pull spring and switch repeat a 20 N pull within ~±2 N.
