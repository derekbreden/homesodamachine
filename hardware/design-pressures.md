# Design pressures

What the appliance is optimised for, and what it is not. Placement decisions answer to this
document; [`future.md`](/hardware/future.md) describes the subsystems it applies to.

## Optimised

**Volume, and the machine in the space the customer has for it.** The enclosure goes under a
counter. Every millimetre of envelope is a millimetre of someone's kitchen.

**Assemblability** — that a build order exists. Special tools are available, the bench is the
factory, and tight tolerances are wanted. What a joint needs is access at the moment it is
made, once.

**The operation inside design constraints**, which is where the machine spends its life.

## Not optimised

**Field service.** There is none. Units are sold over the internet to customers in other
states; a physical fault is answered by shipping a replacement, and the returned unit comes
back to the factory. Diagnosis of a returned unit is a teardown with factory tools — cutting
included — not a repair.

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
- **How much axial travel a collet needs is not in this tree.** The models carry collet faces
  and `BUTT = 0`; the insertion depth of the 1/4" quick-connects, and whether over-inserting a
  stub buys slack to close a joint between two fixed bodies, are unmeasured. Any claim that a
  particular arrangement cannot be assembled answers to that number first.
- **Assembly order runs opposite to group size** where a group is built as a unit. A
  free-standing sub-assembly is a convenience of the bench, not a requirement the joints
  impose.
- **Clearance around a fitting is not a placement criterion.** Room for a hand, a spanner or a
  collet release ranks below volume. Where a run needs room, it needs it to be *routed*, not to
  be reached.
- **A tolerance that is hard to hit is not a reason to move a body.** It is a reason to fixture
  it.
