# k8 — Combination: half-rows crimped where they lie in pallets, sorted into one row, housing pushed on

- **Sources.**
  - change-the-question [c1c](../../change-the-question/ideas/c1c-crimp-in-the-row.md).
    Interlaced jaws split the ribbon end into two planes. A presser comb snaps
    (pre-formed contacts, [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md))
    or tack-lays a whole half-row into carriers at 3.4 mm. A fixed steel C
    crimps each contact where it lies with an ordinary single-nest punch, and
    the carrier holds box, roll and lance groove through the crimp.
  - into-the-housing [i6](i6-sort-then-push.md): a carrier sorts crimped
    contacts into a 2.5 mm target comb in housing order; a backing blade squares
    the row; the housing is pushed onto it.
  - change-the-question proposed the pairing (its S2) in
    [`../../../exchange/change-the-question--on--into-the-housing-w3.md`](../../../exchange/change-the-question--on--into-the-housing-w3.md).
- **Sketch:** [`../sketches/k8-pallets-then-sort.svg`](../sketches/k8-pallets-then-sort.svg) (schematic).
- **Numbers:** [`../calc/wave3.out.txt`](../calc/wave3.out.txt) sections E and I
  [calc w3 X]; change-the-question's [`on_into_the_housing_w3.out.txt`](../../change-the-question/calc/on_into_the_housing_w3.out.txt)
  §7 and §9 [ctq w3 §n].
- **Coordinates** as in [`../handover.md`](../handover.md).

## Why it exists

- **c1c ends in two row pushes with the web clamp and housing still.** By the
  feed-length rule ([`../handover.md`](../handover.md)), every conductor of a
  pushed row must then carry the ~7 mm push as extra length: a bow of 4–9 mm
  over the split [ctq w3 §7]. That is the zone where c1c's presser comb,
  pallets and row B's carriers work.
- **i6 pushes the housing onto one merged row and stores nothing.**
- **In the other direction, i6's open problems ease.**
  - i6 needs "a staging plane from the crimp step upstream". Here the pallets
    are that plane.
  - i6 has to grip a 0.043 g contact without roll. Here every crimped contact
    waits in a keyed pocket, at known roll, open from above and from below
    through the anvil window.
- **J4 and J7 need no special split.** c1c routes J4's two off-parity
  conductors between planes at the split jaws. Here the split goes by web
  position only, and the sort maps every conductor to its pin.

## Picture it

**The machine.** c1c's baseplate:
- a fixed small steel C-frame at the back, holding a guided ram, one punch, an
  anvil blade and a hard stop;
- one X slide in front carrying the web clamp, **pallet A** and **pallet B**
  (carriers at 3.4 mm on swing arms) and, in front, i6's target row: a target
  comb at 2.5 mm that can drop away, the housing nest on a Y slide with a bar
  load cell, a slotted backing blade, and a finishing tine;
- i6's carrier on a small X–Y–Z stage, with the camera above.

**One ribbon end.**
1. **Crimp both rows** (c1c steps 1–4).
   - Clamp and split: odd conductors to plane A, even to plane B.
   - Lay and snap row A into pallet A. The camera looks at every U.
   - Crimp row A in the row, one carrier at a time under the fixed press.
   - Proof-pull each at ~20 N with the box held by its pocket's rear shoulder.
     The lance groove runs out the front, so the lance carries none of it.
   - **Park pallet A up and back**, over the root.
   - Plane B swings up. Lay, snap, crimp and proof-pull row B.
2. **Pick.** The carrier's upper pad closes on a crimp's two lobes. Its lower pad
   comes up through the carrier's **anvil window**, the path the anvil blade
   used. The pad pair lifts the contact out of its open-topped pocket with its
   roll unchanged.
3. **Place row B first.** Pallet B sits in the working plane. Its contacts go
   down into their target slots, lower layer first and centre outward (i6's
   rule).
4. **Then row A.** Pallet A swings down from above into the working plane. It
   sweeps only the space above the working plane, and the sorted row-B
   conductors lie below it [calc w3 I]. Its contacts are placed the same way,
   upper layer last.
   - With J4 laid V5, IO25, 3V3, IO26 | GND, IO27, IO23 and J7 laid RB1–RB4,
     GND | X, CLO, CHI (X is the trimmed conductor), every upper-layer conductor
     sits at an odd ribbon position, so in pallet A: J4's 3V3 and GND, and J7's
     GND [ctq w3 §9].
   - So "B first, then A, upper layer last" satisfies i6's rule.
   - Straight looms (T4, J1, J2) have no crossing when placed centre outward
     [calc w2 C]. Their drop need only clear the comb's tines, ~2–4 mm
     [estimate], not 8–10 mm.
5. **Push.**
   - The backing blade drops, its tines following into the cavity mouths.
   - The housing nest drives onto the row to the first wall.
   - The finishing tine then brings each contact to its own wall
     ([i6](i6-sort-then-push.md); calc w3 E).
6. **Check.** A per-wire 5 N pull-back. Or the target is
   [i6b](i6b-post-bed-through-the-housing.md)'s post bed, which names each
   conductor before the latch.

## At a glance

| | |
|---|---|
| **What locates the contact** | At the crimp: its carrier's box slot, the anvil blade (plane) and a hardened front stop on the die block (c1c). At the sort: the carrier's pads. At the push: the target slot, the backing blade, then the cavity |
| **What locates the conductor** | c1c's web clamp, side fence and tip stop; the presser comb at the snap |
| **Reference for "fixed"** | The fixed press's die block for the crimp; the X slide carrying clamp and pallets together, so stepping never changes contact-to-conductor; the base for the target row |
| **What drives and carries the crimp** | The fixed press (f3's knee, hand-tool-as-press a4's die set on an eccentric, or an OTP knife set in an arbor press). Only its C carries the force; slide, pallets and printed carriers carry none, because the anvil blade rises through each carrier's window |
| **How it knows** | c1c's camera before force, force against ram position, proof pull in the pocket; i6's camera at the slot; the push trace and finishing traces; pull-back or post continuity |
| **Steps it covers** | Split, contact supply (sticks or strip into pockets), place the contact on the conductor (snap), crimp, proof pull, pin order including crossings (sort), insert, latch check |
| **What it hands back** | Keeping the pre-formed sticks (or strip) and housings stocked; laying each ribbon end in the clamp; lifting finished ends out. No crossing is made by hand |

## Conflicts found by combining, and their repairs

1. **Pallet A's path.**
   - Parked down and back (c1c as drawn), pallet A's arc into the working plane
     sweeps the space in front of and below the root. That is where the sorted
     row-B conductors lie, and they travel up to 6.7 mm sideways [calc w2 B].
   - **Repair: park A up and back**, over the root. Its arc then stays above the
     working plane.
   - Once there, its carriers reach 1–2 mm below the plane. They clear the
     sorted conductors under them when the target drop is ≥ ~6 mm and the pallet
     sits beyond 0.36–0.53 of the span from the root [calc w3 I].
   - Whether the fixed press's C and the presser comb leave room above the root
     is unmeasured.
   - If they do not, sort row A first while pallet B is parked. That only works
     for ribbon orders whose upper-layer conductors all lie in row B. For J4 and
     J7 as laid above they lie in row A, so it needs different orders, and the
     parked B pallet's swing then meets the same problem mirrored.
2. **Length spread in the push.** The rigid backing blade meets the contacts'
   length spread. Answered by pushing to the first wall and then finishing each
   contact with one tine (or by constant-force tines, as in i3b).
3. **Split length.**
   - c1c's split jaws need 12–20 mm, and i6's sort ~25–30 mm on J4 and J7.
   - Straight looms need only the tine-clearing drop.
   - c1c's spread to 5.0 mm (its step 5) and its S-bend budget disappear,
     because the sort replaces the spread and both row pushes.

## Printed and bought parts

- As c1c: an MGN12 rail with MGN12H carriage ($20.49, Prime-confirmed
  [sourcing/amazon-prime.md]) under the X slide, a NEMA 17 lead screw, printed
  or stencil-steel carriers with ~0.5 mm walls, and the press of choice.
- As i6: the carrier stage (Iverntech Tr8×2 NEMA 17s and MGN9 rails,
  Prime-confirmed), the stencil-steel blade and tine, a bar load cell, and the
  ELP camera.
- Pre-formed sticks from c6's pre-former, or strip.

## Contribution

- Derek's priority step whole, from c1c: a half-row of contacts placed on their
  conductors in one motion, held in pockets that stay put through the crimp,
  crimped where they lie.
- Insertion from i6, with no stored feed and every crossing, pair and gap made
  by the sort.
- Every crimped contact is proof-pulled and handled only by its pocket and the
  carrier's pads, never by a floppy wire.

## Major unresolved problems

- **The lower pad through the anvil window.** The window is sized for an anvil
  blade (~1.2–1.5 mm wide under the conductor barrel [estimate]), so the pad
  bears only there.
- **Room above the root** for pallet A to park up and back beside the fixed
  press.
- **Two pallets, swing arms and a sort stage** on one slide.
- **Everything c1c leaves:** the final crimp over the pre-form or tack, and
  carrier walls of ~0.5 mm.
- **Everything i6 leaves:** gang-push risks and ribbon identity.

## What rests on assumptions

- Carrier depth below the working plane of 1–2 mm [estimate].
- A sort drop of 2–4 mm suffices on straight looms [estimate].
- c1c's and c6's estimates for the snap and the crimp in the row [ctq w2].
