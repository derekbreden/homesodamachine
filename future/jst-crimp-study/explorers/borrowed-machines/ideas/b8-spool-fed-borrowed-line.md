# b8 — The spool-fed borrowed line: the feed rips the webs, the applicator crimps, the cut frees the loom

**A combination**, named by its sources:
- **p3** "terminate at the spool, cut last" (from
  [procedure-is-the-machine](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md)),
  reached independently as **a4** "spool as magazine" (from
  [ribbon-as-pallet](../../ribbon-as-pallet/ideas/a4-spool-as-magazine.md)): the
  spool is the carrier; a belt feed and encoder; the work clamp; test through the
  rest of the spool on a slip ring; feed out down a drop tube; the cut that frees
  one loom squares the next end; a redo costs spool, not a loom.
- **c5** "ends as stock" (from
  [change-the-question](../../change-the-question/ideas/c5-ends-as-stock.md)):
  start with T4 (4P into XHP-4: J3, J5, J9, J11, J13), half of every unit's
  housings and 38 % of its crimps, with no pair, skip or crossing.
- [b1b](b1b-applicator-in-slow-crank-press.md) (this explorer): the bought OTP
  applicator in a slow crank on the idle shop press, pre-feed, the look at the
  contact alone, the gate before the crimp, the dwell after it, the reject turn.
- [b6](b6-pierce-at-the-root-pull-to-the-tip.md) (this explorer): needles pierce
  each web at the root and the ribbon is drawn so they travel to the strip line.
  **Here the belt feed's own retraction is the draw.**
- [b1](b1-press-and-applicator-with-shuttle.md) (this explorer): the split
  conductors folded back as one band over the clamp face, and the valley-tine
  fork.
- **i3** / **a6** (into-the-housing, ribbon-as-pallet): a converging comb to
  2.5 mm and the housing pushed onto the whole row.

**Branch:** [b8b](b8b-flat-spool-line-over-a-crown.md) replaces the applicator
with terminal-supply's skip-pitch crown station, so nothing folds.
**Neighbours:** force-and-form's
[f2c](../../force-and-form/ideas/f2c-applicator-station-makes-t4-ends.md) makes
whole T4 ends from the spool at an applicator station;
procedure-is-the-machine's [p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md)
starts the same spool-end idea with no motor.

Sketch: [`../sketches/w2-b8-spool-line.svg`](../sketches/w2-b8-spool-line.svg).

Labels: [calc wave2 §n], [calc wave3 §n] are this explorer's
[`wave2.out.txt`](../calc/wave2.out.txt) and [`wave3.out.txt`](../calc/wave3.out.txt);
[TS §n] is terminal-supply's
[`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it: a 4P spool making T4 ends

**Setup (person, once per spool).**
- The 4P spool on an axle behind the machine, its inner end in a spare XH
  housing plugged into a socket on the axle, wired through a 6-circuit capsule
  slip ring ($9.99 [Prime]; Adafruit 736 at $14.95 is the non-Amazon route) to
  the tester. If the inner end is not reachable, the spool is rewound onto a
  printed reel first (p3).
- The free end threaded between two belts of a belt feed (GT2 pulleys, $5.99
  [Prime]), past an encoder wheel (600 P/R encoder, $18.99 [Prime]), through a
  guillotine and an open work clamp.
- A tube of XHP-4 housings, and the day's list: T4 ends, with each loom's length
  or a stock length.

**The feed head.** Belts, encoder, guillotine and work clamp ride together on a
small X/Y stage (MGN12, $20.49; NEMA 17 on Tr8×2, $27.99 [Prime]) in front of the
applicator, which stands still in the shop press. The spool feeds the head
through a slack loop. This is a4's arrangement: the ribbon goes to the fixed
applicator.

**Stations around the work clamp**, all at the clamp's face:
- a **needle bar** 12 mm ahead of the clamp face: three floating needles at
  1.7 mm pitch on a servo lever over a stencil-steel needle plate (b6);
- a pair of flat **scoring blades** and two TPU **pinch pads** at the strip line
  (or [b4b](b4b-diode-heads-at-the-station.md)'s diode heads);
- a **fold lid** hinged at the clamp face;
- the **valley-tine fork**, on the applicator's axis;
- the **applicator** in b1b's crank;
- a **converging comb** and a **housing nest** fed from the tube.

**One T4 end.**
1. **Feed out.** The clamp is open. The belts push the square end until its tip
   is 12 mm + Ls past the needle bar: 12 mm of split plus the reel's strip length
   (2.4 mm for genuine JST contacts, 1.85–2.1 mm for clone contacts [facts §1; TS
   §3]).
2. **Pierce.** The needle bar comes down; each floating needle finds its valley
   and goes through its web, 12 mm ahead of the clamp face.
3. **Rip.** The belts **retract** the ribbon 12 mm. The needles, fixed, travel
   through the ribbon from the pierce toward the tip and stop Ls from it. The pull
   is 9–45 N for a 4P's three webs; two belts on a 20–60 N nip give 32–180 N of
   traction on silicone [calc wave2 §4]. The encoder confirms the travel; a load
   cell on the needle bar records the rip.
4. **Clamp.** The needles lift. The pierce point, which is the split root, now
   sits exactly at the clamp face, because the needles were 12 mm ahead of it and
   the ribbon went back 12 mm. The clamp closes.
5. **Strip.** The scoring blades close on the crowns at the strip line to stops
   set for **50–60 % of the wall**, or ride a shoe on the jacket's top (at 70–80 %
   a stop set from the clamp reaches the strands in the worst case [TS §8]). The
   pads pinch the still-webbed tip; the head backs off 3 mm on its X stage. The
   whole tip comes off as one comb-shaped slug: 4.7–13 N a conductor, 19–52 N for
   four [calc wave3 §8]. A backlit frame checks four stubs.
6. **Fold.** The lid folds the four split conductors back over the clamp face as
   one flat band.
7. **Crimp, per conductor** (b1b):
   - the camera looks at the waiting contact alone; a bad one gets b1b's reject
     turn (an empty crimp and a puff into a reject cup);
   - the fork's tines take conductor *k* from the band and lay it into the
     contact on the anvil; a foot seats it;
   - **gate:** picture, and continuity from the spool's inner end through
     conductor *k* to the grounded applicator, which names the conductor and
     proves the strands touch the contact;
   - the crank turns through bottom dead centre, force logged;
   - **dwell:** the head's X stage withdraws the crimped contact along its axis;
     a thin fork drops into the neck behind the box and the stage pulls 20 N
     against it; picture;
   - the crank completes, the feed runs on an empty anvil, the fork parks the
     crimped conductor in the band.
8. **Straighten and insert.** The fork lays all four crimped conductors forward
   into the converging comb, which runs from root to tip twice to take out the
   fold's set, then closes them from 1.7 to 2.5 mm with their fronts in line. An
   XHP-4 drops from the tube into the nest and is pushed onto all four contacts at
   once through a load cell; each contact is pulled back ~5 N.
9. **Test through the spool** (p3): pogo pins on the housing's mating face; each
   conductor in turn from the spool's inner end; opens, adjacent shorts and swaps.
10. **Feed out and cut.** The clamp opens; the belts push out the loom's length
    (or c5's stock 400/700 mm) down a drop tube, measured by the encoder; the
    guillotine cuts. The loom drops into a bin, and the next end is already
    square.

**What locates what; the reference for "fixed."**
- **The work clamp** is the ribbon's reference from the rip onward. The split
  root is placed on its face by the needle bar's distance from it.
- **The strip line** is where the needles stopped, in the feed's own coordinates,
  which are the clamp's once it closes.
- **The contact:** the applicator, as in b1b.
- **The conductor laterally:** the fork's tines and the foot, on the applicator
  base.

**What drives the crimp and carries its force.** The crank and the shop-press
frame, through the applicator, as in b1b. The belts carry the rip, the clamp the
strip pull, and the housing nest's load cell the gang insertion.

**How it knows it worked.** Rip trace and encoder; backlit stubs; the contact
alone; the gate before each crimp with identity through the spool; the force
curve; the proof pull; the seating trace and pull-back; the through-spool test
after insertion. All logged against the unit, loom and conductor.

**What the person does.** Loads a spool and threads it (~5 min per spool, about
one per 5–7 units of T4), keeps the housing tube full, empties bins and the
reject cup, labels, and makes every loom's far end after the cut. The other looms
are made as today or by another arrangement.

## Steps it covers and what it hands back

- **Covers, for T4:** cut to length (last), split (needle rip driven by the feed),
  strip (whole-tip slug), supply contacts (reel), place the contact on the
  conductor, crimp, verify the crimp, insert (gang), verify insertion and pin
  order (the through-spool test). That is 20 of a unit's 53 crimps and 5 of its
  10 housings, and ~300 ends over the program [c5].
- **Hands back:** spools, housings, bins, labels, far ends, and every non-T4 loom.
  J6 (5P into XHP-5, also straight) is the next spool type to thread.

## The fold's set at the gang push

Each conductor's root is bent back over the clamp face at R 1.5–2.5 mm about four
times: park, lay forward, re-park, lay forward for insertion. Copper keeps a set.
With the comb holding the tips in the plane, a residual kink of 5°, 10° or 15°
becomes a bow that shortens that front by 0.05, 0.18 or 0.41 mm at 12 mm of free
length [TS §10], differently on each conductor, against a gang window of ~±0.3 mm
of which the 4P housing fan already uses 0.06 mm. So the comb runs root to tip
twice before it converges (step 8). [b8b](b8b-flat-spool-line-over-a-crown.md)
removes the fold instead.

## Time

- **Machine:** ~6–7 min per T4 end [estimate]: 2 min to feed, rip, strip and fold;
  four crimps at ~40 s; 1.5 min to straighten, insert, test, feed out and cut.
  About 35 min a unit, or a spool's worth in 3–4 h unattended.
- **Person:** ~33 attended minutes a unit, against 46 today, with everything but
  T4 still by hand [calc wave2 §5]. The minutes that remain are the other 33
  crimps.

## What the combination settles, and what it leaves

- **Settled:** no cassette to load, the largest person step in every
  cassette arrangement; no separate split and strip stations with their own
  motions (the feed does the rip, the clamp stage the strip pull); redos cost
  ~15–20 mm of spool, not a loom; every conductor is identified through the spool
  before its crimp.
- **Left:** pairs (J1, J2, J4, J7), which need two spools edge to edge (p3b) or
  half-housed ends; the J4/J7 crossings; all far ends.

## Printed and bought

- **Printed:** feed-head frame, belt carriers, clamp jaws, needle-bar carrier,
  fold lid, fork, comb, housing nest and tube, drop tube, spool axle and socket.
- **Bought:** slip ring, encoder, GT2 parts, MGN12 rails, NEMA 17 steppers, servos,
  load cells [Prime rows above]; stencil-steel needle plate (JLCPCB); music-wire
  needles [Prime]; the applicator, reel and b1b's crank parts (as b1b).
- **On hand:** the shop press, NEMA 23 and DM542T, the ELP camera [repo].

## Major unresolved problems

- **The spool's inner end**, or a rewind per spool (p3).
- **Feeding floppy ribbon both ways.** A belt feed pushing silicone ribbon out and
  pulling it back, with slip seen only by the encoder; the rip needs the
  retraction to be a pull the belts can hold.
- **The neck** (repo Open item 5), as in b6: whether the rip follows it.
- **The whole-tip strip** at the clamp: whether each flank tears cleanly from crown
  scores at 50–60 % depth.
- **The fold's set**, and whether two comb passes straighten it inside the gang
  window.
- **The loom tail:** ~0.1–0.6 m pushed down a drop tube (p3 found ~700 mm of drop
  needed).
- **Moving the feed head** in X and Y under a crank press, with the spool's slack
  loop following, and guarding the pinch points of both.
- **Machine size:** spool axle, feed head, shop press and drop tube together.
- Everything open in b1b (applicator interface, crank disc, shop-press bed) and
  b1 (tines in the band).

## What rests on what

- **Derek:** slowness and unattended running are the premise [Derek]. The
  ribbon comes on 50 ft spools [repo bom.md].
- **Facts:** contact dimensions and strip lengths [facts §1]; conductor break
  85–100 N [facts §1]; T4 counts [shared context].
- **Calculations:** rip force and belt traction [calc wave2 §2, §4]; strip pull
  [calc wave3 §8]; person minutes [calc wave2 §5]; score depth and kink [TS §8,
  §10].
- **Estimates:** belt nip 20–60 N and friction 0.8–1.5 on silicone; machine step
  times.
- **Assumptions:** rip force from tear strength 15–25 N/mm over a 0.2–0.6 mm neck;
  the BNTECHGO spool's inner end can be reached or rewound.
