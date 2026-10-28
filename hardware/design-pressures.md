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

**Simplicity of the whole assembly.** Choose clean routes, broad printable shapes, simple
supports and straightforward assembly steps. A tube can move to another wall, the floor or
the ceiling when that produces a simpler arrangement. Judge a change by the crowding,
special reliefs and rework it creates elsewhere. Distance moved and the number of edited
items do not measure its disruption.

## Not optimised

**Field service.** None. Every physical fault, the pumps' included, is answered by shipping a
replacement unit; units are sold over the internet to customers in other states, and the
returned unit comes back to Derek. Diagnosis of a returned unit is a teardown with factory
tools — cutting included — not a repair.

**Disassembly.** Not a goal and not a tiebreaker. A part that can only come out by being
destroyed is a part that comes out by being destroyed.

**Access for hands or tools after assembly.** A fitting buried behind three bodies is buried.

## What follows for placement

- **Design a tube's complete path and its supports together.** Intermediate waypoints are
  design variables. Choose them where simple integral supports have room, considering the
  surrounding tubes, wiring and hardware as one layout. Reconsider the whole route when a
  local attachment becomes awkward; coordinated changes to neighboring routes or bodies
  can be part of the simpler solution.
- **A butt joint needs one of its two bodies free along the port axis when it is made.** The
  stub lies entirely inside the two collets, so it is pushed home into one and the second body
  comes onto it. This constrains the ORDER, not the grouping: a chain of butts installs in
  chain order, each body free as its own joint closes. What it forbids is fixing both ends
  first, and a body whose butts run on two axes being last in. The flavour manifold has three
  interior butt joints: Y-A to V-C, Y-B to V-D and the crossbar between Y-A and Y-B. Each
  pump tee reaches its fore valve on a short straight tube, not a butt
  ([`manifold-layout/`](/hardware/manifold-layout/README.md)).
- **The pump mount and dock close at the factory.** Both prepared pumps rise motor-first
  from underneath loose front-top on the broad lower retainer. Its two integral snap wings
  secure the molded-skirt capture against the fitted upper pockets. Each prepared
  tee/upper-tube/fore-valve group then approaches individually from aft, its extended branch
  collet gripping and sealing a fixed pump tube. Each tee's branch stands in a bore through
  the tee wall, which holds it in X and Z; its fixed branch barrel lands on the bore face if
  the tee is pushed fore, and its lower return stops it aft. Each upper tube stands straight
  under its fore valve, and each lower return is two stem elbows and a straight tube
  ([pump dock](/hardware/printed-parts/enclosure/pump-dock/README.md)). Complete the pump
  fastening, plumbing and accessible wiring before joining the front column. A pump that
  fails means a factory teardown.
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
  1.50 mm. A pump tube bottoms 11.50 mm beyond its tee's extended branch face, and a tube
  in a run collet 11.65 mm beyond the extended run face. Every collet stands extended and grips
  its tube.
- **Exposed path length is not stock cut length.** The four upper tubes are reported
  between their fitting mouths. Each blank also includes the actual insertion at both
  fittings; the valve-side insertion is established while preparing the blank. The four
  lower return tubes are reported as cut stock: the straight between their elbows and each
  elbow's socket depth. [`manifold-layout/`](/hardware/manifold-layout/README.md) and the
  assembly procedure supply the current paths and cut instructions.
- **The commercial collet action has its own physical evidence.** The
  [`tee-connector observations`](/hardware/reference/tee-connector/README.md#observed-push-connect-action)
  establish insertion against spring-level collet tension and relocking after a small
  separating tug on the identified fittings. They carry no instrumented force and provide no
  seal or endurance acceptance for the assembled dock. Each prepared tee group approaches
  its secured tube individually; its actual seating force and the return's aft-stop capacity
  remain unmeasured.
- **Clearance around a fitting is not a placement criterion.** Room for a hand, a spanner or a
  collet release ranks below volume. Where a run needs room, it needs it to be *routed*, not to
  be reached.
- **A tolerance that is hard to hit is not a reason to move a body.** It is a reason to fixture
  it.
