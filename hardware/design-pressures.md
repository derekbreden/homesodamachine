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

**Rigidity and a substantial feel.** Available internal volume around supported hardware
belongs to the structure.

## Not optimised

**Field service.** One operation: the pump swap in
[`service/pump-replacement.md`](/hardware/service/pump-replacement.md), which runs on the bench's
own front opening. Pulling the cartridge withdraws four prepared flanged stems from
stationary TPU receivers. The rigid wall and locked flat keepers carry receiver reaction
into the enclosure, while the stem flanges bear in the removable cradle. The enclosure
can be braced by a hand, foot, cupboard edge or its own weight. The fixed commercial
tees and rear plumbing stay put, and `enclosure-front-top` stays on. Every other
physical fault is answered by shipping a replacement; units are sold over the
internet to customers in other states, and the returned unit comes back to Derek. Diagnosis
of a returned unit is a teardown with factory tools — cutting included — not a repair.

**Disassembly.** Not a goal and not a tiebreaker. A part that can only come out by being
destroyed is a part that comes out by being destroyed.

**Access for hands or tools after assembly.** A fitting buried behind three bodies is buried.

## What follows for placement

- **A butt joint needs one of its two bodies free along the port axis when it is made.** The
  stub lies entirely inside the two collets, so it is pushed home into one and the second body
  comes onto it. This constrains the ORDER, not the grouping: a chain of butts installs in
  chain order, each body free as its own joint closes. What it forbids is fixing both ends
  first, and a body whose butts run on two axes being last in. The flavour manifold has three
  interior butt joints; the four pump-side-tee-to-fore-valve links are stationary curved paths,
  not butts ([`manifold-layout/`](/hardware/manifold-layout/README.md)).
- **The pump dock separates at its permanent TPU receivers.** The wall contains each receiver
  in X/Z and a flat interior keeper captures Y. Y-C, Y-D, Y-F and Y-G, their fore links and
  their hairpins are fixed. Complete replacement pumps carry factory-fitted machined
  flanged stems; the customer replaces no receiver or other dock component.
- **The enclosure's rigid barbed lips close on sequential motions.** The first motion
  places each lip clear of its roof; the next slides it under the roof. Flat bearing faces
  retain the seam, and the Y seam's vertical screws prevent the reverse motion.
- **The faucet display cover flexes around the rigid cylindrical neck.** Its side walls
  are printed inward, spread during seating, and remain spread when the broad lips
  contact the groove roots below rigid retaining shoulders. The groove floors stop
  the cover before its bezel reaches the glass. Factory assembly places the display
  inside the cover, slides the pair along the tip with clearance above the neck,
  then lowers it onto the supports. The
  [complete tip and display covers](printed-parts/faucet/faucet-display-petgf.md)
  carry the actual enclosure, device supports, tubes and ribbon route. The print record
  identifies their geometry and settings. The preloaded geometry needs its own fit and
  retention reading. The linked PET-GF15 data are annealed specimen results, not an
  allowable strain for the saved print profile.
- **How far a tube runs into a collet, and how far its sleeve presses, is measured for the
  tee.** The PP0208E's own figures are in
  [`reference/tee-connector/`](/hardware/reference/tee-connector/README.md): a 1/4" tube meets
  resistance at 7 mm, is held from 8.5 mm and bottoms at 10 mm, all from the sleeve's face with
  the sleeve pressed home. Each run sleeve travels 1.65 mm; the branch sleeve travels
  1.50 mm. The permanent rear tails seat 11.50 mm beyond the extended branch faces;
  the commercial collets operate only during factory assembly.
- **Exposed path length is not stock cut length.** The four stationary fore links are
  reported between their fitting mouths. Each blank also includes the actual insertion
  at both fittings; the valve-side insertion is established while preparing the blank.
  [`manifold-layout/`](/hardware/manifold-layout/README.md) and the assembly procedure
  supply the current paths and cut instructions.
- **The commercial collet action has its own physical evidence.** The
  [`tee-connector observations`](/hardware/reference/tee-connector/README.md#observed-push-connect-action)
  establish extraction while depressed, relocking after a small separating tug and
  insertion against spring-level collet tension on the identified fittings. They provide
  no seal or endurance acceptance for the TPU dock. During its assembled dry cycle,
  record simultaneous stem insertion and withdrawal, rigid seating and fixed-plumbing behavior.
- **Clearance around a fitting is not a placement criterion.** Room for a hand, a spanner or a
  collet release ranks below volume. Where a run needs room, it needs it to be *routed*, not to
  be reached.
- **A tolerance that is hard to hit is not a reason to move a body.** It is a reason to fixture
  it.
