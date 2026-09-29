# a1c Crimp from the upstream end, fold each finished conductor back: the fan lies flat in the anvil plane

## Picture it

A combination of ribbon-as-pallet [a1](a1-pallet-tour.md) (one pallet clamped
once, the flush cut as the axial reference, a fan block at crimp pitch, a
reel-fed side-feed applicator on a slow press) and borrowed-machines'
[b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md) (a
fork fixed on the applicator's axis that folds a conductor 180° back over the
cassette, and a presser foot that seats it). borrowed-machines named it C2.
Sketch: [`../sketches/a1c-upstream-first-park-after.svg`](../sketches/a1c-upstream-first-park-after.svg)
(schematic).

Against a1, the neighbours are never held up at a height h. Every uncrimped
conductor lies flat in the anvil plane on the downstream side of the anvil,
where no waiting contact and no feed hardware is. There is no drop, finger,
tongue, S-bend or ramp. Against b1, conductors are not parked before crimping:
each is folded only after its crimp and comes back only for insertion.

**Where things start.**
- A reel of SXH contacts threads a side-feed applicator with its feed intact.
  The next contact waits open on the anvil (pre-feed). The applicator stands in
  a slow crank press (borrowed-machines'
  [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md)).
- The pallet holds a ribbon end, parted to the split root at the clamp face
  ([a7](a7-zip-station.md)), fanned to the crimp pitch p_c in a fan block whose
  grooves lie in the anvil plane, and flush-cut and ring-stripped at the fan
  block's face ([a8](a8-rolling-ring-scorer.md); order A of
  [a5](a5-part-fan-strip-in-the-pallet.md)).

**Which way is which.** The strip comes in from upstream (+X); the anvil is at
X = 0. The pallet sits on the wire-entry side (−Y) on a two-axis stage.
Conductor 1 is the one furthest toward +X; every other conductor lies at X < 0,
downstream.

**One conductor.**
1. The stage puts conductor k on the applicator's axis and slides the pallet in
   +Y. The tip enters the waiting contact's open barrels along their axis at
   barrel height; the insulation barrel's U is its funnel. It stops when the
   insulation edge sits in the gap between the barrels.
2. The applicator's wire hold spring, or b1's presser foot, seats the conductor
   with a flat sole at least 3 mm long, so it lies level rather than diving at
   the tip.
3. The far-end port reads conductor k continuous to the grounded applicator,
   and the camera looks. The crank turns: crimp, tab shear, and a pause where
   the crimpers have cleared the contact and the feed has not yet moved.
4. The stage backs out 10 mm in −Y, drawing the crimped contact off the anvil.
   The crank completes its turn and the feed brings the next contact.
5. **Fold.** A fork fixed on the applicator's axis swings the crimped conductor
   180° up and back over the pallet's top plate, into a numbered pocket that
   takes the contact's box. The fold is in free conductor just ahead of the
   clamp face.
6. **Index.** The stage moves one crimp pitch in +X; conductor k+1 comes onto
   the axis.

**After the last conductor.** Every conductor lies folded back over the pallet
with its contact in its pocket, in pin order. At
[a6](a6-housing-as-last-comb.md) a comb lifts each out of its pocket and folds
it forward into the 2.5 mm insertion clamp: the second and last reversal at the
root.

**What locates what, and the reference for fixed.**
- **"Fixed" is the anvil**; the stage frame and the applicator base are one
  plate, and the fork is fixed to the applicator base, so it shares the
  contact's reference.
- The applicator locates the contact.
- The fan block locates the conductor laterally to ±0.1 mm; the open insulation
  barrel's capture on an axial entry is between ~0 and ±0.5 mm, depending on the
  open-wing reading ([P3 §2]; [a2](a2-two-pallets-meet.md)).
- Axially, the flush cut at the fan block face and the stage's Y. The camera
  trims Y from the session's first crimp.

**What drives the crimp and carries its force.** The applicator in the crank
press: ram → crimpers → contact → anvil → frame, 0.8–2.6 kN [xh-facts §4]. The
pallet carries only positioning. The feed stays, so the crank keeps the
applicator's full stroke (15 mm throw, 2.2–6 N·m [P3 §5]): a NEMA 23 with 10:1
(the bench's own is installed in the cap-weld tube rotator [shared-context]),
or a NEMA 17 with 26.85:1 (3 N·m permissible [Prime]) if the ram's return spring
is light.

**How it knows.** Continuity conductor-to-applicator before the stroke; the
crank's force curve and ΔF/k height; a camera frame before and after; a proof
pull by the stage against a catch plate at step 4 (b1's).

**What the person does.** Loads the pallet, keeps the reel threaded, empties
the scrap chute, carries the pallet to insertion, makes the far end.

## Steps it covers and what it hands back

- **Machine:** contact supply (the applicator's feed), placement by axial
  slide-in and sole, crimp and tab cut, verification, parking of crimped
  conductors; with [a7](a7-zip-station.md), [a8](a8-rolling-ring-scorer.md) and
  [a6](a6-housing-as-last-comb.md) also split, strip and insert.
- **Person:** cut to length and load, reel threading, scrap, carrying the
  pallet, far ends.

## What it removes from a1, and what it costs

| a1's problem | In a1c |
|---|---|
| a 5–6 mm drop adds 10–15 mm of split [calc W2 §7] | no drop: the conductor enters along its own axis at barrel height |
| a point finger leaves the tip diving | a flat sole, or the applicator's own wire hold spring, seats a conductor that is already level |
| neighbours at h over the upstream feed plates | nothing uncrimped is ever upstream; crimped ones are folded back over the pallet |
| a ramp where the shear and scrap chute are | no ramp: the fork lifts and parks |
| pre-feed pushes the next contact into the crimped one | the crank pauses between crimp and feed while the stage backs out |

What it costs:
- **Downstream tooling must clear flat neighbours at p_c.** At p_c = 5 mm the
  applicator's lowest ~3 mm must be no wider than ±3.95 mm beside a bare
  conductor [calc X §4]. Nothing guarantees it. Wider tooling pushes p_c toward
  strip pitch: a 5P's split is 23 mm at 5 mm and 30 mm at 7.1 mm [calc §2].
- **A fold at the root after every crimp.** The web root sees peel when one
  conductor folds and its neighbour stays flat, so the split root has to sit
  exactly at the clamp face, which [a7](a7-zip-station.md)'s tear stop gives.
  Every root takes two reversals, at about 2 % strand strain each at a 2 mm fold
  radius [calc X §3]. Fatigue is not the concern at that count [estimate]; the
  set left in the root is, and a6's clamp straightens it.
- **The fork's reach.** It swings a conductor carrying a 2 × 2.4 mm box 180°
  over the pallet without touching the flat neighbour 5 mm away.
- **Stripping one at a time here needs care.** [a8b](a8b-spindle-with-touch-off.md)'s
  15 mm head butts the flat neighbours at 5 mm pitch unless it has a snout no
  wider than 7.8 mm reaching 6 mm ahead of its bearings [P3 §8]. The rolling
  scorer [a8](a8-rolling-ring-scorer.md) strips the whole flat row at the fan
  face at any pitch, so a1c uses a8.
- **The finished loom's length difference** (order A): a 5P fanned to 5 mm
  leaves its outer conductors 1.34 mm long once closed, a 3–4 mm arc in the
  split [calc F §5].

## Parts

As [a1](a1-pallet-tour.md), minus the tongues, finger and ramp; plus b1's fork
on a servo (MG996R or DS3218 [Prime]), a presser foot if the applicator has no
wire hold spring, and a pocket row on the pallet's top plate. The fan block's
grooves lie flat.

## What it contributes

- The reel-fed applicator, with its feed and shear intact, crimps a fanned
  ribbon with no conductor ever lifted, dropped or held over the feed side.
- **The order of crimping is the clearance scheme:** upstream end first, the
  finished ones folded away behind the strip line.

## Major unresolved problems

- **The applicator's downstream tooling width**, which sets p_c and the split.
  Scan it with the Revopoint.
- **Root peel at the fold**, and the set it leaves for insertion.
- **The crank's pause window** on the OTP cam (hand-cycle and watch the feed
  finger; borrowed-machines' b1c timing model suggests ~220° to ~266°
  [assumption for the OTP unit]).
- **Axial entry of 60 untwisted strands** into the conductor barrel. a8's roll,
  or a8b's quarter turn with a snout, may be what keeps them together.
- **A second motor** for the crank, or sharing the weld station's.

## Related ideas

- Parent: [a1](a1-pallet-tour.md). Sibling: [a1b](a1b-hand-shuttle.md).
- The same clearance problem solved by docking instead:
  [a2e](a2e-docked-strip-through-a-feedless-applicator.md).
- [a4](a4-spool-as-magazine.md) uses a1c's order at the spool clamp.
- Other explorers: borrowed-machines
  [b1](../../borrowed-machines/ideas/b1-press-and-applicator-with-shuttle.md),
  [b1b](../../borrowed-machines/ideas/b1b-applicator-in-slow-crank-press.md).

## What rests on assumptions

- Strip pitch ~7.1 mm [Würth analog]; 6.8–9.5 mm from clone drawings
  [calc §2; xh-facts §1].
- That the OTP applicator's wire hold spring, if present, seats a 1.7 mm
  silicone conductor [assumption].

## Labels

As [a1](a1-pallet-tour.md#labels).
