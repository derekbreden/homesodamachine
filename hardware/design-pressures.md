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
own front opening. Pulling the cartridge carries four tied tees to a fixed release face; insertion
holds the carrier at squeeze with two recessed service tabs, bottoms four tubes, then releases the
tabs so two springs settle the joints at connected. `enclosure-front-top` stays on. Every other
physical fault is answered by shipping a replacement; units are sold over the
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
  first, and a body whose butts run on two axes being last in. The flavour manifold has three
  interior butt joints; the four carrier-tee-to-fore-valve links are exposed bowed flex stubs,
  not butts ([`manifold-layout/`](/hardware/manifold-layout/README.md)).
- **A moving quick-connect needs compliant tube at every moving end and a positive carrier for
  its fitting.** Y-C, Y-D, Y-F and Y-G are journalled in X and Z, tied twice each to one
  Y-guided carrier, and move together. Four bowed stubs flex between those tees and fixed fore
  valves; the tee-side ends of four spine hairpins move with them. Neither a tube nor a fixed
  wall journal substitutes for the carrier.
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
- **How far a tube runs into a collet, and how far its sleeve presses, is measured for the
  tee.** The PP0208E's own figures are in
  [`reference/tee-connector/`](/hardware/reference/tee-connector/README.md): a 1/4" tube meets
  resistance at 7 mm, is held from 8.5 mm and bottoms at 10 mm, all from the sleeve's face with
  the sleeve pressed home, and one sleeve presses 1.65 mm. Those measurements set four carrier
  states from the squeeze datum: release −3.15 mm, where the fixed face has spent the connection
  gap and sleeve stroke; squeeze 0, finger-held while all four tubes bottom at 10 mm; connected
  +1.5 mm, floating under the two aft-pushing springs with 8.5 mm of grip; and park +3 mm, the
  final aft stop at first resistance and beyond connection reach. Only release and park are
  fixed stops.
- **Exposed path length is not stock cut length.** Each of the four bowed flex stubs presents a
  12 mm developed path across a 10 mm sleeve-face chord at squeeze. Its blank also includes the
  insertion at both fittings, and the valve-side depth has not been measured. The tee–valve bow
  trial therefore owns the blank before production; no cut instruction may call that blank
  12 mm.
- **The front-top assembly order follows the moving mechanism.** Install the aft valves; place
  both springs and lower the empty carrier into its open-top guides, then install the two rigid
  service-tab arms and their top-drop tab locks; insert the four tees individually through
  their fixed journals; tie each tee twice; install the fore valves and four bench-fitted bowed
  stubs; then, after the chassis closes, squeeze both tabs, bottom all four cartridge tubes and
  release to connected. A free-standing subassembly remains a convenience of the bench, not a
  reason to reverse those joint motions.
- **Catalog arithmetic and collision-free CAD do not qualify the mechanism.** Before the
  production instruction closes, the complete four-tee assembly is force-measured and cycled
  through all four states with its springs, eight ties, rigid tab arms and keys, bowed stubs and
  four moving hairpin ends. The gate is equal tab motion, positive empty return to park, no
  racking, rubbing, coil bind, buckling or spring escape, repeatable four-tube release and
  reconnection, and no leak or tube damage after cycling.
- **Clearance around a fitting is not a placement criterion.** Room for a hand, a spanner or a
  collet release ranks below volume. Where a run needs room, it needs it to be *routed*, not to
  be reached.
- **A tolerance that is hard to hit is not a reason to move a body.** It is a reason to fixture
  it.
