# a6 The housing is the last comb: insertion, pairs, and the far-end test port (module)

## Picture it

In this view the fan blocks are combs at one pitch or another, and the XHP
housing is the last comb, at 2.5 mm. This module covers how a pallet delivers
crimped contacts into it, how two ribbons share it, and the far end's gift to
the machine: a wire to every conductor for the whole process. Sketch:
[`../sketches/a6-housing-as-last-comb.svg`](../sketches/a6-housing-as-last-comb.svg)
(schematic).

**Where things start.**
- The pallet holds the ribbon, clamped since the beginning. Its crimped contacts
  sit at the crimp pitch, all with the same roll, because the ribbon never
  turned over. In [a1c](a1c-crimp-upstream-first-park-after.md) they lie folded
  back over the pallet in numbered pockets.
- A kit XHP-n housing sits in a nest on a load cell (HX711), cavities facing the
  contacts, window face on the lance side [assumption: which face that is; one
  kit housing settles it]. The nest is a **real XH wafer on a small test board**,
  which is what JST's handling precautions ask continuity and miswiring checks
  to be made against [into-the-housing key findings].

**What moves.**
1. **Close the pitch.** The fan block is swapped for a 2.5 mm **closing block**
   with plain grooves, or the pitch changer ([a5](a5-part-fan-strip-in-the-pallet.md)
   F2) closes. Crimped insulation barrels 1.8–2.05 mm wide leave 0.45–0.7 mm
   between neighbours at 2.5 mm (KONNRA's 2.05 mm max; force-and-form's
   [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md) window 1.8–1.9 mm)
   [w3 C5].
2. **Let the fronts step.** Closing a fan changes the conductors' path lengths.
   Left free, the fronts form a **V staircase**, outer contacts ahead: a 4P
   closed from 7.1 mm has its outer pair 1.85 mm ahead of its inner pair; a 5P
   has its outer pair 2.47 mm and its next pair 1.22 mm ahead of the centre; from
   5 mm, 1.00 mm (4P) and 1.34/0.65 mm (5P) [P3 §10]. The **insertion clamp**
   closes on every conductor 1–2 mm behind its insulation barrel at its own
   front, so its jaw face is stepped to match the V for that ribbon type. The
   clamp's jaws are half-round grooves at 2.5 mm, lined with TPU or finely
   ridged, with small pockets at the front shaped to the crimped insulation
   barrel (~2.1 × 1.9 mm) that square each contact's roll.
   - Forcing the fronts onto one line instead bows the outer conductors
     2.2–4.5 mm over 5–20 mm of free span, where only 0.8 mm separates jackets
     [P3 §10].
   - The clamp must be this close: a free conductor is a column that buckles at
     ~6 N at 5 mm and ~40 N at 2 mm, and the strands yield sooner [calc §4],
     against up to 9.8 N of insertion per contact (KONNRA PS-KR2501-01 §6.2).
     Grip needed: 10–20 N normal per conductor at μ 0.5–1 [calc §4].
3. **Go in.** The nest's Y slide (or the stage) pushes the housing onto the row.
   The outer contacts meet their cavities first and latch; the clamp's grip
   slips at ~15 N on those conductors, which limits how hard the early contacts
   are pushed past their latch, while the rest travel on. The load cell sees one
   event per step of the V: for a 5P, the outer pair, the next pair, the centre
   (three events for five lances [calc F §6]). Two other ways, both slow:
   - **Lean and slide (Sogang):** the housing tilted about the row axis so each
     tip lands on the rear face and slides in as the housing rotates square.
     Parallel approach 3 of 20; lean-and-slide 18 of 20; with "weaving" and a
     guide clamp 49 of 50 ([source](https://arxiv.org/html/2608.06996)).
   - **One at a time**, neighbours held out of plane.
4. **Follow it home.** For the last millimetre the jaws open slightly and slide
   forward along the conductor to the rear of the crimped insulation barrel, and
   push on that shoulder (Molex US 4,936,011, from borrowed-machines'
   [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md)).
   The push goes into the crimped barrel, not through friction on silicone; the
   last ~1 mm is pushed through a free length that buckles only at ~150 N
   [calc §4].
5. **Pull back.** The clamp releases, the pallet draws back with a spring limited
   to ~5 N per contact, and the ELP camera looks at the housing's rear face. A
   contact that followed the pull is not latched (Boeing US 11,374,374's rule,
   "seated when the pull force reaches the test value before the gripper has
   moved the pull distance" [prior-art §5]).
6. **Test on the wafer.** The controller reads the far-end port against the
   wafer's pins: pin map, adjacent shorts, J2's cavity 3 open, the J4/J7 recipe.
   into-the-housing's [i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md)
   builds a whole station on this nest.

**What locates what, and the reference for fixed.** "Fixed" is the housing nest.
The closing block's grooves locate each conductor laterally at 2.5 mm; the clamp
pockets square each contact's roll; the stage's Y sets depth; cavity entry
chamfers take the rest [assumption: not in a public JST drawing].

**Forces.** One step of the V at a time, ~10–20 N; all straight in together, up
to 39 N for 4 contacts and 88 N for 9 [calc §8]. A NEMA 17 on a Tr8×2 screw
makes 100 N easily [estimate]. No crimp force passes through this module.

**How it knows.** Latch events on the load cell (at 0.2 mm/s an HX711 at 80 SPS
takes ~400 samples per millimetre [into-the-housing calc §6]); the pull-back and
camera per contact; continuity and pin map on the wafer.

**What the person does.** Loads a housing into the nest, or keeps a gravity
magazine of one housing type filled; removes the finished loom; for J4 and J7,
the crossing contacts (below).

## Steps it covers and what it hands back

- **Covers:** pitch close, insertion, latch verification, pin map, shorts,
  empty-cavity check, two ribbons into one housing (with the partner step below).
- **Hands back:** housing supply, and J4's and J7's crossing contacts unless the
  loft or the wiring choice is taken.

## What the finished loom carries

Every contact latches at the same depth, so every conductor needs about the same
length from the root. If the flush cut was made after a wide fan (order A of
[a5](a5-part-fan-strip-in-the-pallet.md)), the outer conductors carry their
excess into the finished loom as a 3–5 mm arc (5P from 5–7.1 mm over a 20–30 mm
split [calc F §5]). If the conductors were cut to one length at the root before
the split (order B, [a9](a9-reel-end-docks.md)), the V staircase at insertion
comes from the equal-path fan's humps instead, and the clamp's forward push pulls
them straight: the finished loom carries no excess.

## Two ribbons in one housing

Four housings take two ribbons (J1, J2, J4, J7) [repo cable-assemblies.md].
- **Processed as two, merged at insertion.** Each ribbon is parted, fanned,
  stripped and crimped alone. The two ribbon pallets bolt together at a mating
  edge through a shared dowel pair (±0.1 mm in Y), with one closing block
  spanning both. At a reel ([a9](a9-reel-end-docks.md)), the first ribbon's
  housing waits half-filled in a partner nest while the second reel's end is
  made.
- **Clamped as one.** The channel takes both edge to edge, and the recipe says
  which marked edge lies on the datum wall.

### J4 and J7: the crossing runs between the two ribbons

On the repo's pin maps, as procedure-is-the-machine reads them [calc unit_inventory §1;
the cavity numbers are its reading, assumption]:
- **J4 SENSORS (XHP-7):** the 4P goes to cavities 1, 3, 4, 5 and the 3P to 2, 6,
  7; the 3P's GND crosses into cavity 2, inside the 4P's field.
- **J7 REEDS B (XHP-7):** the 5P goes to cavities 1–4 and 7 (its GND past
  CLO/CHI) and the 3P's CLO/CHI to 5–6; one 3P conductor is trimmed.

Both crossings run from one ribbon into the other's cavities. With the pair
processed as two pallets, no groove on either pallet can make the crossing
before crimping, and a crossing contact has to pass over the other ribbon's
crimped row at 2.5 mm. What stands:
- **A gapped closing block** for the first ribbon: J4's 4P into 1 and 3–5, J7's
  5P into 1–4 and 7. The second ribbon's contacts go in by hand: J4's three and
  J7's two, five contacts a unit.
- **One pallet with a loft** for J4 (procedure-is-the-machine's
  [p1](../../procedure-is-the-machine/ideas/p1-cassette-and-benches.md)): both
  ribbons clamped as one 7-conductor end, and the person lays the GND conductor
  into a raised crossover groove at loading, where the fan is wide and the room
  generous. Cost: a ~39 mm split fanned as one at ~7 mm [calc §2], plus the
  crossover's length. Whether the crossing conductor's contact is left square
  for docking is open.
- **For J7, a wiring choice for Derek:** GND rides the 3P with CLO and CHI, and
  the 5P's fifth conductor is the trimmed one. J7 then goes in straight, 5P to
  1–4 and 3P to 5–7.
- **Trims:** J2's conductor 3 and J7's spare are cut back at the split root;
  their positions are gaps in the closing block, and the wafer test confirms
  J2's cavity 3 is empty.

## The far-end test port

- **The block.** The ribbon's far end is cut square, conductor faces at 1.7 mm
  pitch. A printed block takes it in a small clamp and presses a P75 pogo pin
  onto each cut face. The Prime row is the P75-E2 conical head, 1.3 mm cone on a
  1.02 mm tube, 100 for $6.49 [Prime: P75 pogo pins]; a crown-head P75 had no
  Prime listing. A cone should centre itself in the ~0.72 mm strand bundle
  [assumption]. hand-tool-as-press reaches the same port with a push-in terminal
  block on a stripped far end.
- **At a reel** the far end is the reel's inner end, in a hub socket or on a slip
  ring ([a4](a4-spool-as-magazine.md), [a9](a9-reel-end-docks.md)).
- **What it gives.** A wire to every conductor for the whole process: touch-off
  ([a8](a8-rolling-ring-scorer.md), [a8b](a8b-spindle-with-touch-off.md)); nick
  detection at isolated blades and tines ([a7](a7-zip-station.md), a8);
  placement before force, conductor to grounded contact or carrier
  ([a1](a1-pallet-tour.md), [a2](a2-two-pallets-meet.md),
  [a2e](a2e-docked-strip-through-a-feedless-applicator.md)); identity at a
  single-contact nest ([a10](a10-dock-tack-then-nest.md)); opens and shorts after
  insertion.
- **What it cannot do** is grade a crimp. The loom's own resistance is
  6–34 mΩ (57 mΩ/m) against a crimp's ~1–2 mΩ [calc §9].
- **Where no far end is wired,** a comb of insulated neck blades on the strip
  pallet, one in the neck between each box and conductor barrel, would confirm
  each conductor's strands at depth locally (force-and-form's
  [f3](../../force-and-form/ideas/f3-knee-micropress.md) neck blade) if the neck
  takes a 0.3 mm blade [w3 §5].
- **Harmlessness.** The pogo tips touch only the cut face, which the far-end
  termination strips or trims later.

## Contact orientation

The flat ribbon carries orientation for free: every contact is crimped
floor-down on the same anvil, and as long as the ribbon is not turned over
between crimp and insertion every lance faces the same way. The nest need only
present the housing's window face on the lance side. A conductor that has been
twisted (a8's roll, a8b's quarter turn) can roll its contact a few degrees; the
clamp's pockets take that out.

## A look at every insulation crimp at once

force-and-form's [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md)
checks an insulation crimp by bending the wire and looking for a cut at the wing
tips. The tips of a B/F insulation crimp sit on top, so the bend must be
downward to open a cut [w3 §6]. Here the crimped contacts are held by their
barrels in the clamp's front pockets, with the insulation barrels' rear line on
a steel edge, and the ribbon pallet swings down 60–90° about that edge: the fan
block face 9 mm behind it moves 7.8–9 mm down [w3 §6], and every insulation crimp
is on the outside of the bend in one camera frame. Three swings. Not developed
further.

## Major unresolved problems

- **Where the contact's rear sits when latched** (0.2–1.25 mm inside the rear
  face, into-the-housing's estimate), and whether slide-along jaws fit the rear
  opening. One contact in one kit housing, photographed from the rear, settles
  it.
- **Insertion and retention of the kit parts:** clone spec insertion ≤9.8 N,
  retention ≥19.6 N (KONNRA); JST's are licence-gated [xh-facts §3]. A 20 N pull
  after latching sits at the clone's minimum retention, so the proof pull
  belongs before insertion (at the crimp station).
- **Whether the load cell separates two lances snapping together** (the V's
  pairs).
- **Staircase overtravel** against the cavity's front wall.
- **J4 and J7:** five crossing contacts a unit by hand, unless the loft or the
  wiring choice.

## Related ideas

- Used by every arrangement in this directory.
- Other explorers: into-the-housing
  [i5](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md),
  [i3b](../../into-the-housing/ideas/i3b-staggered-row-one-push.md) (staggered
  spring seating), [i6](../../into-the-housing/ideas/i6-sort-then-push.md);
  borrowed-machines [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md)
  (slide-along jaws); procedure-is-the-machine
  [p1](../../procedure-is-the-machine/ideas/p1-cassette-and-benches.md) (the
  loft); force-and-form [f6](../../force-and-form/ideas/f6-two-blades-two-drives.md).

## What rests on assumptions

- Clone insertion and retention figures standing in for JST's.
- Chamfered cavity entries; lance snap visibility; pogo contact on fine-strand
  cut faces [assumption].

## Labels

As [a1](a1-pallet-tour.md#labels) and [a2](a2-two-pallets-meet.md#labels).
