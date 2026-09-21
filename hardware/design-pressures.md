# Design pressures

What the appliance is optimised for, and what it is not. Placement decisions answer to this
document; [`hardware/README.md`](/hardware/README.md) describes the subsystems it applies to.

## Optimised

**Volume, and the machine in the space the customer has for it.** The enclosure goes under a
counter. Every millimetre of envelope is a millimetre of someone's kitchen.

**Assemblability** — that a build order exists. Special tools are available, the bench is the
factory, and tight tolerances are wanted. What a joint needs is access at the moment it is
made, once.

For the tee carrier, prefer tying the tees to the carrier on the bench before enclosure
insertion. Fitting the ties in place is an acceptable tradeoff when it permits simpler or
thicker geometry.

**The operation inside design constraints**, which is where the machine spends its life.

**Rigidity and a substantial feel.** Available internal volume around supported hardware
belongs to the structure. The tee carrier's fixed body fills the space south (Y−) of its
backing, connecting the tee journals, spring pockets and broad plate guides into both enclosure
flanks. Hardware, travel, tubing and assembly motions define the cavities; the remaining stock
forms continuous sections with clean flat working faces. Minimizing material is not an objective
for this body.

## Not optimised

**Field service.** One operation: the pump swap in
[`service/pump-replacement.md`](/hardware/service/pump-replacement.md), which runs on the bench's
own front opening. Pulling the cartridge carries four tied tees to a fixed release face; insertion
uses each hand to squeeze between a cartridge pocket and its carrier tab: cartridge aft,
carrier fore, until four tubes bottom. Relaxing the grasp lets two springs settle the joints at
connected. The fixed plate carries removal reaction into the whole enclosure, which can be
braced by a hand, foot, cupboard edge or its own weight. `enclosure-front-top` stays on. Every other
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
- **The enclosure's rigid barbed lips close on sequential motions.** The first motion
  places each lip clear of its roof; the next slides it under the roof. Flat bearing faces
  retain the seam, and the final seam screws prevent the reverse motion.
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
  1.50 mm. The fixed plate acts on the four branch sleeves and holds them fully depressed
  at the fore stop. Nominal connected travel is 2.00 mm: 1.50 mm of sleeve travel and
  0.50 mm of nose air. Release and squeeze share the fore stop. The mechanical aft limit
  is 4.50 mm from release, 2.50 mm beyond nominal connected; an empty spring-driven
  carrier returns to that limit. Tube projection bottoms at nominal connected with the
  cartridge fully seated, 11.50 mm beyond each extended branch face. At squeeze it
  bottoms 10.00 mm beyond each pressed face with the cartridge 2.00 mm shy of seating.
  Relax the grips and push through that final seating stroke.
- **Exposed path length is not stock cut length.** Each of the four bowed flex stubs presents a
  17.251 mm developed path between sleeve faces separated by 15.251 mm in height and 1.75 mm fore/aft
  at squeeze. Its blank also includes the
  insertion at both fittings, and the valve-side depth has not been measured. The tee–valve bow
  trial therefore owns the blank before production; no cut instruction may call that blank
  17.251 mm.
- **The front-top assembly order follows the moving mechanism.** Both carrier bodies must
  enter the actual shell, engage their guides and retain each other without colliding with
  the tees or valve hardware. Spring loading needs an accessible controlled path into both
  retained ends. Prefer two substantial, self-latching bodies whose normal seating motion
  closes the joint; separate keepers or screws add assembly work. The current candidate's
  native assembly checks and support-removal review precede a complete enclosure test print.
  That assembled print establishes spring capture, return tension, joint retention and feel;
  those physical readings are acceptance results, not prerequisites for printing the test.
- **The collet action is physically established.** Derek's checks with a tube-tight collar
  show easy extraction while the collet is continuously held, relocking after a small
  separating tug, and insertion against spring-level collet tension. The fixed plate carries
  the removal reaction and the springs provide the short return movement. The observations
  are recorded in [`tee-connector/`](/hardware/reference/tee-connector/README.md#observed-push-connect-action).
  The assembled unit's dry cycle checks its guide, joint, return and flexible links.
- **Clearance around a fitting is not a placement criterion.** Room for a hand, a spanner or a
  collet release ranks below volume. Where a run needs room, it needs it to be *routed*, not to
  be reached.
- **A tolerance that is hard to hit is not a reason to move a body.** It is a reason to fixture
  it.
