# f2c — Branch of f2: the applicator station makes whole T4 ends from the spool

Explorer: force-and-form. Parent: [`f2-crank-press-for-an-applicator.md`](f2-crank-press-for-an-applicator.md).
A combination with change-the-question's
[c1](../../change-the-question/ideas/c1-half-rows.md) (a pocketed output pallet,
a push into the housing, a real-wafer test) and
[c5](../../change-the-question/ideas/c5-ends-as-stock.md) (spool-fed stock ends,
cut last), with procedure-is-the-machine's
[p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md) (strip the
whole webbed end in one stroke at the clamp) and
[p6](../../procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md)
(the reel as the far end, a puller instead of a push).
Sketch: [`../sketches/f2c-t4-ends-from-the-spool.svg`](../sketches/f2c-t4-ends-from-the-spool.svg) (schematic).
Numbers: [`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) §8 [calc final §n];
change-the-question's [`ctq.out.txt`](../../change-the-question/calc/ctq.out.txt)
and [`on_force_and_form.out.txt`](../../change-the-question/calc/on_force_and_form.out.txt).

## Picture it

- **Feed.** A 4P spool's leading end, flush cut by the last end's guillotine,
  is held by a web clamp on f2's ribbon carriage. The spool's inner end is on a
  slip ring (p6), so every conductor is a wire to the controller.
- **Strip.** p7's two straight blades close on steel stops across the whole
  webbed end at the clamp and take the slug in one stroke (43–59 N for a 4P at
  a 0.2 mm ligament, procedure-is-the-machine's estimate). One backlit frame
  measures every insulation edge; those become per-conductor depth corrections
  at the applicator.
- **Split.** The web is parted back to the clamp face (ribbon-as-pallet a7's
  zip, or change-the-question c1's jaws). The clamp face is the split root, so
  later folds do not peel the web further.
- **Place and crimp.** f2 as it stands: the OTP applicator in the slow crank
  press leaves a contact pre-fed on its anvil; the carriage's fork presents one
  conductor at the depth its measured insulation edge asks for; one crank turn
  crimps, cuts the tab and feeds the next contact. The applicator is grounded,
  so the slip ring reads which conductor is in the contact before the stroke.
- **Deliver in cavity order, into one pallet at housing pitch.** After each
  stroke the carriage lifts the crimped contact and sets it, box first, into
  its pocket in **one** output pallet at 2.5 mm, in cavity order. Crimped
  contacts fit side by side at housing pitch (0.45–0.7 mm between insulation
  crimps 1.8–2.05 wide; box pockets 2.05–2.1 wide leave 0.4–0.45 mm steel ribs)
  [calc final §8]. A crossing is made by the order of delivery. T4 has none;
  J7's one and J4's two would be (J4's largest move is 6.3 mm sideways, 17–23°
  over a 15–20 mm split).
- **The pallet rides with the web.** It is mounted on the carriage in front of
  the web clamp, on a hinge that swings it down and back while the carriage
  presents the next conductor to the applicator, and up again to take the
  crimped contact. A pallet fixed to the bench would tether the carriage to
  every contact already placed.
- **Insert.** With all four in the pallet, one straight push drives the whole
  row into an XHP-4 held at the pallet's front edge. The web clamp slides +Y
  with the push, so no conductor needs stored feed: every contact latches at
  the same distance from the web, as it was crimped. The pusher bears on the
  top band of each box's rear face.
- **Test.** The housing goes onto a board-type male XH wafer read by a
  microcontroller, which reads each cavity against the slip ring (c1, c5).
- **Cut.** A puller draws 400 or 700 mm of ribbon through the guillotine
  (p6's puller, so the housing is never the handle), and the cut frees the
  finished T4 end into a bin and squares the next leading end (c5).
- **What locates what.** Fixed is the applicator's anvil for the crimp; the
  web clamp on the carriage is the datum for depth and for pocket delivery; the
  pallet's pockets locate the boxes for the push; the housing nest locates the
  housing.
- **The person** threads a spool, supplies housings and a contact reel, and
  empties the bin. At unit build: cuts each stock end to loom length and makes
  the far end.

## Why one pallet, not two

Every conductor of a ribbon end has the same length from the web, so every
latched contact sits at the same distance D from it. Two half-rows pushed in
turn cannot both reach D: if the web follows the first push, the second row is
carried to D with it, which is inside the housing; if it does not, the first
push drags each crimp toward the web. The insertion stroke is 6–9 mm, and a
straight lay stores at most ~0.4 mm (ribbon-as-pallet's reading of
force-and-form, B1). One row at housing pitch, pushed once with the web
following, needs no stored feed at all.

## Numbers

- **Cycle.** ~1 minute per crimp including carriage moves; a T4 end ~4–5
  minutes. A 15.2 m 4P spool makes 21 long or 38 short ends, ~1.5–3 hours:
  inside one printing day [change-the-question calc §9, estimate].
- **Scope.** T4 is 5 of every unit's 10 housings and 20 of its 53 crimps; the
  program's ~300 T4 ends are 1,200 crimps.
- **Press.** f2's numbers stand: under 3.3 N·m at the crank, a NEMA 23 through
  a 30:1 self-locking worm [calc: drives §A].

## Who contributes what

- **f2:** place, crimp and cut, from a bought applicator in a slow crank press.
- **c1:** the pocketed pallet, the push and the wafer test.
- **c5:** the spool feed, the cut-last order and the bins.
- **p7 and p6:** the whole-end strip at the clamp, the slip ring and the
  puller.

## Major unresolved problems

- **The hinged pallet on the carriage**: swinging clear of the applicator's
  tooling at every crimp and back, and whether its pockets take a crimped
  contact carried on 12–20 mm of split conductor. The conductor bends at
  1–3 mN, so the pockets' chamfers do the locating and the carriage only has
  to reach them (ribbon-as-pallet's figure).
- **Stripping and splitting on the spool unattended, on silicone**: p7's own
  open problems (the slug's caps crushing under the push, the tear path).
- **The pusher's face** and whether a 0.4–0.6 mm tongue fits beside the
  insulation crimp inside the cavity.
- **Everything f2 leaves open**: which contact the OTP applicator is tooled
  for, its wire-hold spring on silicone, and the insulation wedge setting in
  this wire's window ([`f6`](f6-two-blades-two-drives.md)).

## Which conclusions rest on assumptions

- **Cycle time** is an estimate.
- **Pocket delivery** assumes the web clamp is the datum for the crimped
  contact's position to ±0.1 mm.
- **p7's slug removal** is procedure-is-the-machine's estimate, untested.
