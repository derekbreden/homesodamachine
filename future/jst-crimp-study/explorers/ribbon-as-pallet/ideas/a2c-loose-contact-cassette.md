# a2c Loose-contact cassette: kit contacts in keyed printed nests

## Picture it

A branch of [a2](a2-two-pallets-meet.md). A printed **nest bar** with one shaped
pocket per contact replaces the carrier strip. Loose contacts go into it: the
CQRobot kit terminals on hand [repo bom.md §11], BXH-001T-P0.6 ($0.0444 at 50,
Digi-Key [xh-facts §6]), or contacts cut off a strip one at a time. Everything
after loading is a2's: dock the ribbon pallet, check, crimp, pull. It is the
route in this directory for the contacts actually on the bench. Sketch:
[`../sketches/a2c-loose-contact-cassette.svg`](../sketches/a2c-loose-contact-cassette.svg)
(schematic).

**The nest bar.** A printed bar with N pockets at a free crimp pitch, 4–5 mm.
Each pocket is the contact's shape seen from above:
- a box pocket about 2.0 × 2.45 mm, deep enough that the box's floor sits on the
  pocket floor;
- a relief on **one side only** for the retention lance, which stands 0.6–0.9
  mm proud of the box's floor side [xh-facts §1], so a contact upside down or
  reversed does not drop in, and the right one sits flat instead of propped on
  its lance;
- a shallow cradle under the barrels, open at the front so a head's lower die
  can reach under them, or itself a steel anvil insert if the crimp is made in
  the bar;
- a **rear shoulder** behind the box that the box's rear face bears on, the
  pull-test reaction (20 N on ~1.5 mm² of PET-CF is ~13 MPa [estimate]).

**Loading the nests.**
- **By hand,** tweezers, about 5 s a contact [estimate]. This is the step
  Derek wants rid of.
- **By stapler stick:** loose contacts stacked nose to tail in a printed stick,
  pushed by a spring, the front one picked or sheared off. Loading the stick in
  orientation stays the person's job.
- **By shaking:** tilt the bar ~15° under a small heap of contacts and vibrate
  it with a coin motor (20 for $12.99 [Prime]). Contacts that meet a pocket
  box-first and the right way up drop in; the rest slide off into a cup
  [assumption: general practice, source not gathered]. machine-that-sees-and-learns'
  [v4b](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md) pocket
  plate, filled by tapping and checked by camera, is the same idea developed.
- **From strip at a free pitch:** borrowed-machines'
  [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md) feeder,
  shear and box gripper aimed at the pockets. Orientation comes from the strip.
- **Then the camera** looks down the bar: every pocket must show a contact
  with its barrels' U open upward.

**Docking and after.** The ribbon pallet, prepared as in a2 but fanned only to
the bar's pitch, docks on three hardened seats. Every conductor goes into every
contact; a finger comb presses them in if the open wings are narrower than the
jacket [calc F §4]. Continuity is read conductor to the bar's grounded
contacts only if each pocket has a spring contact to ground (loose contacts are
not common as a carrier is): a phosphor-bronze leaf under each box, wired
together.

**What locates what, and the reference for fixed.** "Fixed" is the nest bar,
located on the same plate as the ribbon pallet's seats. Each contact sits in its
pocket to ±0.1 mm plus pocket clearance [estimate, H2C]; the conductors to
±0.1 mm by the fan block; axially, the pocket's rear shoulder and the ribbon
pallet's strip line.

**What drives the crimp and carries its force.** Whatever crimps: a2's head
bringing its own anvil, a steel anvil insert under each pocket and a press, the
lift-to-punch of the 3.4 mm variant below, or the SN-2549 by hand after a tack
(below). A printed cradle cannot be an anvil: it would see 400–900 MPa
[xh-facts §4].

**How it knows.** The camera frame of the loaded bar; continuity to each
pocket's ground leaf after docking; the crimp's own checks.

**What the person does.** Loads the bar (or supervises the shaker, or keeps the
strip feeder threaded), plus a2's loading and far ends.

## Steps it covers and what it hands back

- **Machine or fixture:** contact orientation (the keyed pocket), placement by
  docking; with the shaker or b2's feeder, contact supply; the crimp as a2.
- **Person:** loading or supervising the bar, the ribbon pallet, far ends.

| | a2 (carrier strip) | a2c (nest bar) |
|---|---|---|
| Contact location | carrier slots, stamping tolerance | printed pocket, ±0.1 mm plus clearance |
| Pitch | fixed by the strip (~7.1 mm) | free: 4–5 mm, so a shorter fan (a 5P splits 23 mm at 5 mm [calc §2]) |
| Pull reaction | carrier, with a pad on the barrels | pocket shoulder on the box's rear face |
| Cut-off | shear comb | none: loose parts have no tab |
| Stock | reel or cut strip, bought | kits on hand, BXH bags, or strip cut one at a time |

## Variants kept beside it

### Pockets set back by the fan's recession, for a strip made before the split

With loose contacts the pocket's Y is free, so each pocket can be set back by
its conductor's fan recession. For a 5P at 5 mm that is 0, 0.77 and 1.65 mm
from the centre out [P3 §1; calc W2 §3]. A ribbon end stripped webbed, before
the split (procedure-is-the-machine's
[p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md)), then docks
with every insulation edge in its window, with no equal-path fan. The recession
depends on the groove's exact shape, so the pockets are printed from the same
geometry as the fan block [P3 C1]. The finished loom then has every conductor
one length from the root, as in [a9](a9-reel-end-docks.md).

### The tack, then the hand tool (with a10b)

After docking, a notched steel comb closes every insulation barrel loosely in
one stroke, as [a10](a10-dock-tack-then-nest.md) does on the strip. The ribbon
pallet lifts off with every kit contact hanging from its own conductor at its
docked depth and roll, and each is crimped in the SN-2549 by hand
([a10b](a10b-tacked-row-into-the-hand-tool.md)). The pocket's rear shoulder
reacts the tack. This uses only contacts and tools on the bench, plus printed
parts, a comb and a lever.

### At 3.4 mm: half-rows, no fan (with change-the-question c1)

The pitch can be **3.4 mm, twice the ribbon's own**. change-the-question's
[c1](../../change-the-question/ideas/c1-half-rows.md) found that the odd
conductors already lie 3.4 mm apart, over the pockets, so they dock with **no
fan**; the even conductors are sorted into a second plane by interlaced toothed
jaws (US 4,179,964) and parked; the split is only what the park fold needs,
12–20 mm. Open neighbours' wings leave 0.15–1.45 mm between them, so no head
fits; each pocket becomes a steel anvil slide that lifts 3–4 mm out of the row
into a fixed punch. From this view the contribution is the keyed pocket and the
pull shoulder; the rest is c1's, developed there.

## Major unresolved problems

- **Kit contacts are unknowns:** JST or clone, and how they fit a pocket
  [xh-facts §6]. Caliper five before designing the pocket; the CQRobot listing
  does not claim JST parts [Prime: CQRobot kit row].
- **Loose contacts tangle:** open barrels hook into one another, so a shaken
  heap may pass as clumps. Strip feeding avoids it.
- **Orientation from the lance alone:** the relief must reject a reversed
  contact reliably, and a shaken contact might wedge rather than drop.
- **Continuity through loose contacts** needs a ground leaf per pocket.
- **Crimping in the bar** needs steel under each contact, or the contact leaves
  the bar on its conductor (the tack).

## Related ideas

- Parent: [a2](a2-two-pallets-meet.md). With the tack:
  [a10](a10-dock-tack-then-nest.md), [a10b](a10b-tacked-row-into-the-hand-tool.md).
- Other explorers: change-the-question
  [c1](../../change-the-question/ideas/c1-half-rows.md),
  [c1b](../../change-the-question/ideas/c1b-tack-first.md);
  procedure-is-the-machine [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md);
  borrowed-machines [b2](../../borrowed-machines/ideas/b2-hand-crimper-in-a-frame.md);
  machine-that-sees-and-learns [v4b](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md).

## What rests on assumptions

- That vibratory loading of this shape works [assumption].
- H2C pocket accuracy ~0.1 mm [estimate].
- Lance position and size [xh-facts §1, clone drawings].

## Labels

As [a1](a1-pallet-tour.md#labels).
