# k6 — Combination: force-and-form's head crimps each still conductor while a carrier holds it, then the carrier sorts the row into housing order and the housing is pushed on

- **Sources.**
  - force-and-form [f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md).
    A fist-sized steel C with a knee and a NEMA 17 inside rides a light gantry.
    It picks a contact off a strip at a dispenser that shears its tab, carries
    it captured, threads it onto a still conductor, crimps, and leaves toward
    the box. The force stays in the C.
  - into-the-housing [i6](i6-sort-then-push.md). Crimped contacts wait in ribbon
    order in a staging plane. A carrier lowers each into its housing slot, lower
    layer first, centre outward. A backing blade squares the row, and the
    housing is pushed onto it.
  - It is force-and-form's "one gantry, two tools" (their reading of
    [i4](i4-gantry-hand-with-eyes.md) with f4), with i6 in place of i4's direct
    insertion.
- **Numbers:**
  - [`../calc/wave2.out.txt`](../calc/wave2.out.txt) [calc w2 X] and
    [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w3 X];
  - force-and-form's [`drives`](../../force-and-form/calc/drives.out.txt),
    [`force_loop`](../../force-and-form/calc/force_loop.out.txt) and
    [`placement_budget`](../../force-and-form/calc/placement_budget.out.txt);
  - change-the-question's [`on_into_the_housing_w3.out.txt`](../../change-the-question/calc/on_into_the_housing_w3.out.txt) [ctq w3 §n].
- **Sketch:** i6's [`../sketches/i6-sort-then-push.svg`](../sketches/i6-sort-then-push.svg)
  shows phases 2 and 3; force-and-form's f4 sketches show the head.
- **Related:** [i2](i2-crimp-in-the-cavity.md)'s narrow dies (the 2.5 mm
  variant); change-the-question [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md)'s
  closed ring (a variant below).

## Picture it

**On the bench.**
- A base with the web clamp at the back and a **root comb** in front of it.
  - The person lays a split, stripped ribbon end into it (or a pair edge to
    edge).
  - The root comb fans the conductors from 1.7 to 5 mm pitch in ribbon order;
    laying them in is the splay, as in f4.
  - The conductors stick out forward, straight, in the staging plane, their
    stripped tips in a line ~20 mm ahead of the root comb.
- Beside the base is f4's **strip dispenser**: a printed track with a contact
  strip and a servo drop-shear.
- Over everything, a **gantry** (a 3018-class CNC frame or a printer-class
  Cartesian) carries f4's **crimp head**.
- Under the staging plane, a separate small X–Z stage with a short Y carries the
  **carrier**: two fingers that close above and below a conductor, stiff in Y,
  and switchable to loose in X and Z (a flexure with a solenoid lock).
- 8–10 mm below the staging plane, in front, is i6's target row: a target comb
  at 2.5 mm pitch, a backing blade, a guide comb, a finishing tine, and the
  housing nest on its Y slide with a load cell.

**Phase 1: crimp every conductor where it lies** (Derek's priority step).
1. The carrier closes on conductor k, 3.5–5 mm behind the stripped edge, fingers
   locked. The conductor now has a short, still free end.
2. The head picks the lead contact at the dispenser: anvil up, crimper closed to
   capture height, tab sheared by the dispenser's drop-shear. The head carries a
   captured, square contact.
3. The head camera finds conductor k's tip.
   - The gantry aligns the captured barrel's flared rear on the tip to ±0.05 mm
     and moves along the conductor's axis, so the contact slides onto the still
     conductor like a sleeve.
   - Depth is gantry travel referenced to the carrier's fingers.
   - The ELP camera checks the insulation edge in the window.
4. The carrier's fingers switch to loose in X and Z, still stiff in Y.
   - The knee straightens, and the crimp is logged as force against true die
     gap.
   - The knee re-touches for crimp height.
5. **Proof pull.** The carrier locks and pulls −Y ~20 N against the head's
   closed crimper (the head's fork or neck blade, f3's practice).
6. The head opens, drops its anvil, and leaves toward the box, then up. The
   carrier lets go. Conductor k stays in the staging plane with its crimped
   contact.
7. Next conductor. Neighbours are 5 mm apart, room for f4's nose under ~6 mm
   wide.

**Phase 2: sort** (i6).
- The carrier takes each crimped contact by its barrels, lower layer first and
  centre outward.
- It lowers each 8–10 mm into its target slot, sets its rear on the line and
  presses the wire in.
- J4's 3V3 and GND and J7's GND go last, riding over the rest to the housing's
  end.

**Phase 3: push and check** (i6).
- Backing blade down; the housing nest advances −Y to the first wall; the
  finishing tine brings each contact to its own wall [calc w3 E].
- A per-wire 5 N pull-back.

## At a glance

| | |
|---|---|
| **What locates the contact** | The strip's pilot pin and pawl at the dispenser, then the head's captured dies. At the sort: the carrier's pads. At the push: slot, blade, cavity |
| **What locates the conductor** | The root comb (X, in ribbon order); the carrier's locked fingers during threading (Y and Z); loose in X and Z during the stroke |
| **Reference for "fixed"** | The gantry frame, which carries the dispenser, root comb and target row. During each crimp the carrier's fingers are the conductor's reference and the head's dies the contact's |
| **What drives the crimp** | A NEMA 17 inside the head, through a knee: 0.8–2.6 kN at the dies [digest] |
| **What carries the crimp force** | The head's own steel C. The gantry only positions it |
| **How it knows** | Camera before the crimp (tip in the funnel, insulation edge in the window); force against die gap; re-touch crimp height; proof pull; camera on the slot; push trace and finishing traces; pull-back |
| **Steps it covers** | Contact supply (strip), place the contact on the conductor (the head threads a captured contact onto a still conductor), hold both, crimp, crimp height, proof pull, tab cut, pin order and crossings, insert, latch check |
| **What it hands back** | Laying each split, stripped, lightly twisted ribbon end into the root comb; loading strip into the dispenser (a 100-piece strip covers ~2 units, a reel ~150 [digest]); dropping a housing in; lifting the finished end out; labelling |

## What each side brings

- **force-and-form** brings the crimp:
  - a strip locator (pilot pin and pawl at the dispenser);
  - capture before threading;
  - a geometric bottom in a short steel loop;
  - per-crimp height and pull.

  The conductor never moves for the crimp.
- **into-the-housing** brings:
  - the carrier as the conductor's holder during the crimp (f4's comb held the
    insulation; here a finger does, and then goes on to be the sorter);
  - insertion with no stored feed;
  - the pin map as software: crossings, pairs and J2's gap.

## Conflicts found by combining, and their repairs

1. **The carrier's grip against the anvil's position.**
   - A rigid grip 3.5–5 mm behind the barrels, with the anvil setting the
     barrel floor, kinks the conductor if the two disagree by 0.05–0.4 mm
     [force-and-form §4].
   - The silicone jacket takes 13–52 % of a mismatch over 2–3 mm of free length
     at Shore 50–70A [calc w3 G]: some, not all.
   - Repair: the fingers go loose in X and Z for the forming stroke.
2. **The head working over placed conductors.** If phases 1 and 2 were
   interleaved, the head's lower jaw, several millimetres below the conductor it
   crimps, would reach down toward conductors already lowered 8–10 mm. Repair:
   crimp everything first, then sort.
3. **The carrier holding while the head threads.** Two positioners are needed:
   the head moves along the conductor while the carrier holds still. The
   carrier's stage is small (X over the fan's width, Z 10 mm, Y a few mm).
4. **Splay to 5 mm.** J1's outermost conductor moves 13.2 mm, which needs
   23–36 mm of split [calc geometry §7]. The 4P family needs 9–14 mm. The finished
   split is long on J1.

## Variants

**At 2.5 mm, with K1's narrow dies.**
- f4's head carries i2's stepped narrow dies: a 3.1 mm conductor step and a
  2.5–2.7 mm insulation step, walls bottoming on anvil shoulders. The C's arms
  are above and below the plane, and only the dies pass it. That keeps the split
  near the finished fan, at the cost of custom dies.
- Crimping in web order, the neighbour on one side is crimped: its barrels are
  1.5 and 1.9–2.0 mm wide.
  - The conductor step clears the crimped conductor barrel by 0.15–0.25 mm a
    side.
  - The insulation step's mouth has a half-width of only 1.50 mm on that side
    [calc w3 A]. Open clone wings above ~2.5 mm (tight margins) or ~2.2 mm
    (generous) do not fit, and a bronze barrel cannot be pushed aside.
  - Pre-formed contacts (keyhole 1.96–2.14 mm) fit with +0.08 to +0.37 mm. So
    this variant runs on strip through an in-line pre-former, as in
    [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md)'s strip branch.
- On the other side the neighbour is a waiting conductor cantilevered from the
  root comb, which gives way easily.

**Threading through a closed ring** (change-the-question's c6 sub-variant).
- The insulation barrel is pre-formed to a closed ring just over the jacket.
- As the head slides the captured contact along the still conductor, the
  strands lead through the ring and into the open conductor U, and the ring
  centres the jacket.
- It trades the snap for a guide. The ribbon's jacket is 1.7 ±0.1 mm [source
  S29], so the ring wants ~1.85–1.9 mm with a flared rear edge rather than
  c6's 1.75–1.8 mm, and the final insulation crimp then closes further than
  from an open barrel.

## Major unresolved problems

- **Everything f4 leaves open:** a nose under ~6 mm, gantry repeatability, die
  supply, threading 60 fine strands without fold-back.
- **Everything i6 leaves open:** gripping a crimped contact by its barrels, the
  gang push, ribbon identity.
- **Two positioners and one person-loaded root comb.** The person's time is
  loading, ~1–2 min per ribbon end [estimate, as in b1 and f4].
- **The 2.5 mm variant** depends on custom dies and pre-formed contacts.

## Contribution

A cell in which the conductor never moves while its contact is placed and
crimped, and every crossing and pair is made without hands. The person loads
ribbon ends, strip and housings.

## What rests on assumptions

- f4's head geometry and repeatability [force-and-form estimates].
- Silicone at Shore 50–70A for the jacket's share [estimate].
- Clone contact dimensions [source S19–S22].
