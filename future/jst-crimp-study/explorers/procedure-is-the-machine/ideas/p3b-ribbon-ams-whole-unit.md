# p3b Ribbon AMS: the whole unit from five spools

Sketch: [`../sketches/p3b-ribbon-ams.svg`](../sketches/p3b-ribbon-ams.svg)
(schematic plan view).

**A branch of [p3](p3-terminate-at-the-spool-cut-last.md).** p3 runs one spool at
a time and leaves the pairs to a partner nest and the person. p3b mounts every
spool at once, the way a Bambu AMS holds four filaments with one feed each. It
feeds two ribbons side by side into **two lanes**, so a pair's ribbons are made,
housed, tested and cut together as if they were one wide ribbon. The machine then
makes a whole unit in loom order, including eight of the ten housings.

## Picture it: J1, then J2, then J4

**The spools and lanes.**
- Five spools, each with its own belt feed that can advance and retract: **left
  lane** 5P, 4P-L, 3P-a; **right lane** 4P-R, 3P-b.
- Each lane has a merge funnel. As in an AMS, only one ribbon occupies a lane's
  shared path at a time; the others retract behind the merge, their tips parked at
  a light beam.
- The two lanes deliver side by side into the work clamp, edge to edge; the clamp
  is wide enough for 5P + 4P (15.3 mm [repo]).
- Why two lanes and five spools: every pair has a "cavity-1 ribbon" (left) and a
  second ribbon (right); the 4P appears on the left for J4 and on the right for
  J1; J2 needs two 3Ps at once. So a second 4P and a second 3P spool are bought;
  BNTECHGO spools are the same stock [repo bom.md §11].
- Each spool's inner end is on its own slip ring [Prime: 12.5 mm capsule slip
  ring, 6 × 2 A, $9.99 each], so both ribbons of a pair are tested through their
  spools.

**J1 (5P left + 4P right into an XHP-9).**
- Both lanes advance to the clamp-face beam; the clamp closes on both; the
  guillotine squares both.
- Each ribbon is stripped on its own with [p7](p7-strip-before-split.md)'s stroke
  (a pair stripped together moves J1's outer fronts 0.35–0.41 mm), then split;
  the fan comb takes nine conductors to 2.5 mm. The seam between the two ribbons
  is already a split.
- Place and crimp run nine times at p3's lift-once station, in either form: the
  SN module on its side ([p1c](p1c-lift-once-tip-down-module.md), lift
  8.7–14.7 mm) or the fin from below ([p1d](p1d-lift-once-fin-from-below.md), lift
  3.5 mm). Both spools' slip rings read identity across all nine conductors at
  every crimp.
- The XHP-9 comes from a tube and slides on (gang). Both spools test all nine
  pins.
- **Both feeds give the loom length together, and the puller draws it out**,
  clipping both ribbons behind the housing. The pair is equal length by
  construction, which is what the repo asks for: "cut to the same length, laid
  edge to edge" [repo cable-assemblies.md].
- The guillotine cuts both, and J1 drops.

**J2.** 3P-a (left) and 3P-b (right) come in. The program cuts 3P-a's third
conductor back at the split; J2's fan comb has position 3 empty. Five crimps, one
XHP-6, cavity 3 open, and the test checks it is open.

**J4 (4P-L left + 3P-b right).** The ends are made and tested but cannot be
gang-inserted: the 3P's GND must reach cavity 2 [into-the-housing]. The machine
leaves both ends in a parking comb, fed out and cut together, for the person. J7
is the same.

**The person's run.** Load five spools (their changes are staggered; the 4P-L
empties first, about every 5 units [calc unit_inventory]); load housing tubes for
XHP-4, -5, -6, -7 and -9; press go for a unit; later take ten looms from the bin,
insert J4's and J7's 14 contacts by hand, label. About 14 attended minutes; the
machine runs ~2.3 h a unit alone [calc person_timeline; estimates].

## Where it differs in kind from p3

- **The pair becomes a wide ribbon**: no partner nest, no half-housed end in a
  bin, length equality from the shared feed-out.
- **The machine's order is the loom list**, not the spool's life: units are made
  one at a time, with no finished looms held ahead.
- **Five feeds and two merges** are the price: two lanes of AMS-style plumbing for
  flat ribbon.

## What locates what

As p3: the ribbon is registered once per end at its own tip (the clamp-face beam),
"fixed" is the machine frame, and the crimp's references are the lift-once
station's own. The seam between the two ribbons is located by the clamp's width
and the fan comb.

## What drives the crimp and carries its force

The lift-once station's own drive, closed inside the SN module or the steel C, as
in p3.

## How it knows it worked

As p3, through both slip rings: identity at every crimp across both ribbons, the
force curve, the camera, the proof pull, and the pin-to-pin test through both
spools before the cut.

## Steps it covers, and what it hands back

- **Automated:** trim, split, strip, place the contact on the conductor, crimp,
  look, insert (8 of 10 housings), test through the spools, feed out pairs
  together, cut to length.
- **Handed back:** loading five spools and five housing tubes, loading the posts,
  inserting J4's and J7's 14 contacts by hand, labelling, every far end.

## Printed and bought

- **Printed:** five feed units of one design; two merge funnels shaped for flat
  ribbon; the wide clamp; five housing tubes and a housing selector (a slide that
  brings the right tube over the nest); per-loom fan combs on an indexing holder;
  p3's station parts.
- **Bought:** five small steppers for the feeds plus p3's set; five slip rings; two
  extra spools; ~10 axes of drivers, three SKR Pico class boards [Prime: BTT SKR
  Pico, $35.99] or one larger board.

## Problems, and what answers each

1. **Flat ribbon does not merge like filament.** Filament is round and stiff;
   ribbon is flat, floppy and pushes poorly. The merges are short, every ribbon
   stays under belt drive until 20 mm from the clamp, the funnels are shallow Y's
   in the ribbon's own plane so it bends only about its thin axis, and a retracted
   ribbon parks at a beam. This stays the least certain mechanism here.
2. **The J4/J7 crossings still need a person.** Alternatives: p2's bow-and-push
   gripper as a station; J7's ribbon assignment changed so only J4 needs a hand;
   or 14 hand insertions a unit.
3. **A pair made together shares its failures.** A bad crimp on either ribbon
   redoes both ends, 6 mm from each spool, so the pair stays equal [calc
   recovery_length §4].

## Contribution

p3b carries the spool order to "a unit per press of a button" without giving up
recovery at the spool or testing through the spool. It makes the pair-length
requirement a property of the machine, and shows what remains for a person under
this view: two crossings, housings in tubes, spools, labels.

## Major unresolved problems

- **Ribbon merging and retracting**, untested for silicone flat ribbon.
- **Machine size**: five spools, two lanes and the p3 machine is a large bench
  appliance for 53 crimps a unit.
- **Per-loom fan combs**: J1, J2 and J4 each fan differently, so the combs sit on
  an indexing holder, another axis.
- **The lift finger at the seam** must raise a conductor next to the other
  ribbon's free edge without disturbing it; the edge conductors are freer there
  [assumption].
- Everything unresolved in p3.

## What rests on assumptions

- Five spools and the lane assignments from [repo pcba.tsx] pin orders and
  cable-assemblies.md ribbon pairs; J1's 5 | 4 split is straight.
- Attended minutes and run length [estimate].
