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

- **A joint with no slack is made before installation.** Two collets butted face to face
  cannot be brought together along their own axis once both bodies are trapped, so the group
  that contains such a joint is built free-standing and installed as one rigid body. The
  flavour manifold is 19 such joints ([`manifold-layout/`](/hardware/manifold-layout/README.md)).
- **Assembly order runs opposite to group size.** The most internally constrained group is
  built first and goes in as a unit; freer bodies go in later and individually, in place.
- **Clearance around a fitting is not a placement criterion.** Room for a hand, a spanner or a
  collet release ranks below volume. Where a run needs room, it needs it to be *routed*, not to
  be reached.
- **A tolerance that is hard to hit is not a reason to move a body.** It is a reason to fixture
  it.
