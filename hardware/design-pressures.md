# Design pressures

What the appliance is optimised for, and what it is not. Placement decisions answer to this
document; [`hardware/README.md`](/hardware/README.md) describes the subsystems it applies to.

## Optimised

**Volume, and the machine in the space the customer has for it.** The enclosure goes under a
counter. Every millimetre of envelope is a millimetre of someone's kitchen.

**Assemblability** — that a build order exists. Special tools are available, the bench is the
factory, and tight tolerances are wanted. What a joint needs is access at the moment it is
made, once.

**The operation inside design constraints**, which is where the machine spends its life.

## Not optimised

**Field service.** One operation: the pump swap in
[`service/pump-replacement.md`](/hardware/service/pump-replacement.md), which runs on the bench's
own access — the pump cartridge withdraws through front-top's bay and its integral collet plate
releases four tubes. Every other physical fault is answered by shipping a replacement; units are sold over the
internet to customers in other states, and the returned unit comes back to the factory. Diagnosis
of a returned unit is a teardown with factory tools — cutting included — not a repair.

**Disassembly.** Not a goal and not a tiebreaker. A part that can only come out by being
destroyed is a part that comes out by being destroyed.

**Access for hands or tools after assembly.** A fitting buried behind three bodies is buried.

## What follows for placement

- **A butt joint needs one of its two bodies free along the port axis when it is made.** The
  stub lies entirely inside the two collets, so it is pushed home into one and the second body
  comes onto it. This constrains the ORDER, not the grouping: a chain of butts installs in
  chain order, each body free as its own joint closes. What it forbids is fixing both ends
  first, and a body whose butts run on two axes being last in. The flavour manifold is 19 such
  joints ([`manifold-layout/`](/hardware/manifold-layout/README.md)).
- **A catch in PET-GF goes home on a SECOND MOTION, never by deflecting.** Short glass buys
  stiffness with elongation, and a wall that carries a lip is `2 * wall` thick — a snap asking
  either of those to flex cracks rather than clicks. So a `barbed lip` is set down clear of its
  roof by the motion that closes its own seam and driven under it by the motion that closes the
  next, and the fastener is what stops it travelling back out. The exemplar is the faucet display
  cover ([`printed-parts/faucet/faucet-display-cover/`](/hardware/printed-parts/faucet/faucet-display-cover/)):
  set down `display_cover_hook_travel` up-gooseneck of home, pushed to the spout until the riser
  stops on the roof's face, then the screw. Its bearing face is FLAT, because a ramp there would
  let the hook cam out under the screw's own clearance. This constrains the ORDER: **a seam is
  locked by the motion that closes the seam after it, so the seam closing LAST has no motion
  behind it and takes a screw.**
- **What strain PET-GF15 has before it breaks is not in this tree.** The rule above is the
  material's direction, not a number: no elongation, modulus or stress figure for Fiberon PET-GF15
  is recorded anywhere here. Any claim that a particular catch *could* be sprung answers to that
  number first.
- **The anchor tees' axial release travel needs a physical check.** The release design uses
  the 1.335 mm sleeve travel measured on the John Guest union. The tees' own travel and the
  compliance of their `BUTT = 0` valve joints remain unmeasured.
- **Assembly order runs opposite to group size** where a group is built as a unit. A
  free-standing sub-assembly is a convenience of the bench, not a requirement the joints
  impose.
- **Clearance around a fitting is not a placement criterion.** Room for a hand, a spanner or a
  collet release ranks below volume. Where a run needs room, it needs it to be *routed*, not to
  be reached.
- **A tolerance that is hard to hit is not a reason to move a body.** It is a reason to fixture
  it.
