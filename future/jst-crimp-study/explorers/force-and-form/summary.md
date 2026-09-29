# force-and-form

*A crimp is a small, slow sheet-metal forming operation.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [f1 — The hand tool is the press: the SN-2549 closed by a slow actuator, with a swinging keyed flap](ideas/f1-motorised-ratchet-crimper.md)

A second SN-2549 lies flat in a printed cradle and a linear actuator with a load cell squeezes its handles; the tool's own toggle and ratchet form the crimp. A swinging keyed flap takes a contact outside the jaws (stick magazine, strip shear or a tacked contact) and lifts it into the nest from below, and the jaws close to just short of the first ratchet tooth, so the barrels are located but not pinched. The camera measures the hanging tip's bare length, the X/Z carriage lowers the conductor to the depth that puts the insulation edge mid-window, the actuator completes the stroke, and after the crimp a 0.3 mm neck blade on the box's rear face reacts a 20 N pull.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die · usable without a motor.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Loading the magazine or strip (or tacked ends), clamping a pre-split, pre-stripped ribbon end, insertion and test. The neighbours leave with one uniform set at the fork line (26-46 deg). About 67 calls per unit with hand-dropped contacts, 14-15 with strip or magazine.
- **Major unresolved problems:**
  - SN-2549 handle force and travel (sizes the actuator)
  - Whether the SN-2549's XH nest meets JST crimp height on this ribbon
  - Where its fixed insulation step lands in this silicone's window
  - Whether the nest locates the barrels at the position short of the first tooth
  - Transition t >= 0.50-0.70 mm for the neck blade
  - The fork's unavoidable 26-46 deg set on every neighbour
  - Whether the force curve through a ratchet is clean enough to flag faults

### [f1b — Branch of f1: JST WC-110 in the same cradle, its locator and profile taken apart](ideas/f1b-wc110-in-the-cradle.md)

f1's cradle, actuator, load cell, camera and carriage around JST's WC-110. JST's steel flap locator places the contact (fed clicked-out by magazine or strip shear), the actuator holds it lightly, and the carriage lowers the conductor to the tool's insulation stop blade, accepted only as a force rise inside a +/-0.3 mm window around the depth the camera's bare-length measurement predicts. What the $536 buys beyond f1 is JST's die profile and insulation step; the $0.90 JST reference lead, copper-corrected at each crimp's own width, judges the SN-2549 against it first.

- contacts: either loose or strip · steel: JST or Engineer hand tool · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** f1.
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** As f1: contact supply, ribbon loading, insertion and test.
- **Major unresolved problems:**
  - Side-entry orientation relative to a machine-held wire; the tool may need to stand on edge
  - Handle force unpublished
  - Ratchet release on an aborted stroke
  - JST's fixed insulation step is calibrated on UL1007 PVC wire and may sit low in the silicone window
  - Ten times the SN-2549 route's cost for a profile the reference crimp can judge first
  - No Prime listing

### [f2 — Build the press, buy the applicator: a slow crank press around an OTP side-feed mini-applicator](ideas/f2-crank-press-for-an-applicator.md)

A bought OTP side-feed XH mini-applicator ($150-250) feeds, locates, crimps both barrels and cuts the tab; it sits in a built steel C-frame whose crankshaft runs in its own pillow blocks and turns at ~2 rpm through a NEMA 23 and a 30:1 self-locking worm (<3.3 N m; 1 deg at bottom dead centre is 3-4 um), or by a handwheel on the worm. A ribbon carriage's fork presents each pre-stripped conductor into the pre-fed contact; the grounded applicator lets the far end name the conductor before each stroke. The conductor dial is set at the applicator's own crimp width from a copper-corrected JST reference crimp, and the insulation wedge into this wire's window.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die · usable without a motor.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Splitting, stripping and loading the ribbon into the carriage; a strip reel every thousand-odd crimps; insertion and test (unless f2c).
- **Major unresolved problems:**
  - Which XH contact the OTP applicator is tooled for; its fixed profile and width on 22 AWG silicone
  - Frame metalwork: ram-to-shank coupling, shut-height lock at 135.78 mm
  - Wire-hold spring behaviour on silicone
  - Where the IH wedge must sit in this wire's window
  - Neighbour folds at the clamp face if the ribbon is split into planes
  - No Prime listing for the applicator

### [f2b — Branch of f2: the applicator in a bought arbor press with a hard stop](ideas/f2b-arbor-press-with-a-hard-stop.md)

The same applicator and carriage in a bought arbor press; a steel stop collar on the rack meets the press body at the applicator's shut height, and the applicator's dials set crimp height. Derek's hand, a current-limited actuator on the handle, or a worm on the pinion drives it, and surplus force goes into the stop. Only the 3 t presses open far enough (VEVOR AP-3 and PR-3, 310 mm, Prime-confirmed); the 1 t presses (139.7 and 150 mm) are too short for an applicator.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** f2.
- **Automates:** supply contacts, place contact on conductor, crimp.
- **What the person still does:** As f2; in the hand-lever form also pulling the lever.
- **Major unresolved problems:**
  - Setting the stop collar to about +/-0.01 mm
  - Pinion radius, ram play and gib wear of the 3 t presses (thin listings)
  - A drive that can crush the stop unless current- or spring-limited
  - Everything f2 leaves open about the applicator

### [f2c — Branch of f2: the applicator station makes whole T4 ends from the spool, one pallet at housing pitch, one push](ideas/f2c-applicator-station-makes-t4-ends.md)

A 4P spool on a slip ring feeds its leading end to a web clamp on f2's carriage; two straight blades strip the whole webbed end in one stroke (procedure-is-the-machine p7) and the web is parted to the clamp face. The applicator crimps one conductor per crank turn at its measured depth, and the carriage sets each crimped contact into one hinged pallet at 2.5 mm riding on the carriage, in cavity order. One push inserts all four with the web following (every contact latches at the same distance from the web, so no conductor needs stored feed), a real XH wafer tests the end, and a puller draws 400/700 mm into a guillotine whose cut frees the end into a bin and squares the next.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Branch of** f2.
- **Combines:** [change-the-question/c1](../change-the-question/summary.md), [change-the-question/c5](../change-the-question/summary.md), [procedure-is-the-machine/p7](../procedure-is-the-machine/summary.md), [procedure-is-the-machine/p6](../procedure-is-the-machine/summary.md).
- **Automates:** strip, split, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Threading a spool, supplying housings and a contact reel, emptying the bin; at unit build, cutting stock ends to loom length and making the far end.
- **Major unresolved problems:**
  - A hinged pallet on the carriage that swings clear of the applicator at every crimp and takes a crimped contact carried on 12-20 mm of split conductor
  - Unattended stripping and splitting on silicone (p7's slug caps crushing, the tear path)
  - The pusher tongue beside the insulation crimp inside the cavity
  - Everything f2 leaves open about the OTP applicator

### [f3 — Knee micro-press: the die is the locator, the gauge is the micrometer](ideas/f3-knee-micropress.md)

A palm-sized steel die set on two ground pins, closed by a knee (0.2 mm short of straight is ~1 um) that a NEMA 17, a servo or a hand lever pushes at 60-160 N; a wedge under the anvil is the crimp-height dial, and a load cell under the anvil with a 0.001 mm indicator across the dies logs force against true die gap. Tapered pins in the neighbours' holes and a flush pilot pin from below locate the lead contact on its strip; the press captures at a height chosen from the contact's floor width, the camera checks the barrel and measures the tip's bare length, and the carriage threads over the carrier (tab in tension) to the camera-set depth while the far end names the conductor. After the crimp it re-touches at 10 N for height, drop-shears the tab, and a neck blade on the box's rear face reacts a 20 N pull against the web clamp.

- contacts: carrier strip · steel: any of several · meeting: conductor brought to a fixed die · usable without a motor.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Pre-split, pre-stripped ribbon loaded into the carriage by its web clamp; strip loading; insertion.
- **Major unresolved problems:**
  - Die supply: SN jaw seat, quick-turn EDM roof form, shop skill for a crimper, knife-set profile provenance
  - Transition t >= 0.50-0.70 mm for the neck blade
  - Capture height that holds the barrels without closing the insulation bore (floor width)
  - Hold-down keeping a 0.2 mm carrier on a flush pin
  - Carrier pitch, pilot hole and tab length unmeasured
  - Threading 60 fine strands without fold-back
  - Reading the 0.001 mm indicator (its DTCR-01 cable is not on Prime)
  - The target crimp height itself (licence-gated)

### [f3b — Branch of f3: curl at a light station, finish anywhere (coin, hand crimp or solder)](ideas/f3b-two-station-forming.md)

Station A, a light frame around steel dies, does f3's feed, pilot, capture and thread, crimps the insulation barrel fully, and curls the conductor wings only until their tips land on the strands (end of the curl plateau, ~150-450 N), stopping on the force curve's shape. Its product, a contact on its wire with the wings curled but not coined, takes any of three finishes: coining at a tiny stiff press with a ~0.3 mm stroke, a hand crimp in today's SN-2549, or solder. A single station A is harmless in a printed frame; a gang station A (0.4-2.9 kN) needs a steel local stop, and as a gang curl tack on the strip it is one branch of f9b.

- contacts: carrier strip · steel: any of several · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** f3.
- **Combines:** [change-the-question/c3](../change-the-question/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp.
- **What the person still does:** As f3, plus carrying parts from A to their finish unless the uncut strip carries them.
- **Major unresolved problems:**
  - Whether curl-then-coin equals a one-stroke B-crimp (the four-arm sectioning experiment)
  - Re-registration of a curled, sprung-back crimp in a second die
  - Transfer on an uncut strip with conductors trailing
  - Two die sets

### [f4 — The head goes to the wire: a closed steel C on a gantry picks, threads and crimps while the ribbon stays still](ideas/f4-crimp-head-goes-to-the-wire.md)

The person lays a split ribbon end once into a printed comb board (plane A at ~5 mm, stripped after the spread or captured by a grooved fan block from the root; plane B folded back at the split root). A fist-sized steel C with a knee and a dropping anvil wedge rides a printer-class or 3018 gantry, so the gantry never feels the crimp; it picks a contact box-first at a strip dispenser whose drop-shear cuts the tab outside its mouth, probes the tip with the captured barrel's rim (the far end reads the touch, giving position and identity), slides the contact onto the still conductor to a camera-set depth, crimps, and leaves toward the box with the anvil dropped 1.5 mm to clear the lance. Both planes are crimped before any insertion, then merged into a 2.5 mm comb and a housing is moved onto the whole row.

- contacts: carrier strip · steel: any of several · meeting: die head brought to a still conductor.
- **Combines:** [change-the-question/c1](../change-the-question/summary.md), [ribbon-as-pallet/a6](../ribbon-as-pallet/summary.md), [into-the-housing/i3](../into-the-housing/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Splitting, laying the comb board (J4/J7 crossings on raised routes), strip loading, stripping unless a strip head is added, parking and unparking the planes, the housing move or insertion.
- **Major unresolved problems:**
  - A nose under ~6 mm wide carrying a knee-driven crimper and a wedge-dropped anvil
  - Anvil wedge returning to ~0.01 mm after each drop, or re-touch every crimp
  - Aiming a 1.4-1.9 mm barrel mouth at a tip 4-5 mm out of a comb
  - Gantry repeatability and Z travel unmeasured
  - Parking and unparking the crimped planes; J4/J7 need a sort
  - The bore at capture (floor width)
  - Far-end port wiring on every ribbon end for the tip probe

### [f5 — Die cassette: load and look at leisure, then one push per ribbon end in any press](ideas/f5-die-cassette-and-the-shop-press.md)

A steel two-post cassette holds N anvil and crimper stations at the strip's pitch, with stop blocks that set crimp height; a strip segment on pilot pins locates N contacts at once. At a loading station the ribbon is fanned into a comb, flush-cut and stripped at the comb face so every insulation edge is on one line, laid into the barrels by a presser, and checked by the camera and by insulated anvils that let the far end name each station's conductor before any force. The idle 12-ton shop press, a 1 t arbor press or a ball-screw pusher closes the cassette to its stops (5-12 kN), a floating shear under the carrier cuts every tab, and each conductor is proof-pulled at the comb face.

- contacts: carrier strip · steel: made dies (EDM, machined, laser-cut) · meeting: the person presents, the machine takes · usable without a motor.
- **Combines:** [ribbon-as-pallet/a8](../ribbon-as-pallet/summary.md).
- **Automates:** crimp, verify crimp.
- **What the person still does:** Loading strip and ribbon into the cassette, pumping the press (or starting a screw), insertion (the row keeps its fan's copper set), a sample crimp-height check.
- **Major unresolved problems:**
  - Strip pitch unmeasured (7-9.5 mm means a 25-40 mm fan)
  - Split length the looms can carry
  - N matched die pairs
  - A per-conductor proof-pull gripper
  - Insulating N anvils for identity
  - Whether loading is quicker than hand crimping
  - Overpumping the shop press

### [f5b — Half-row cassette: crimp every other cavity at 5.0 mm, merge both half-rows at 2.5 mm, insert once](ideas/f5b-half-row-cassette.md)

f5's two-post cassette with five stations at 5.0 mm: one EDM crimper plate with five B profiles (3.0-3.5 mm webs), a ground anvil block, and five open-topped keyed steel pockets for loose kit contacts, the ribbon pallet riding on balls on the lower shoe with its clamp face at the split root. Plane A is captured by a grooved fan block from the root, stripped after the spread, checked by camera and per-station identity, and closed to the stops in a 1 t arbor press or the shop press; it lifts out and parks folded back while plane B is crimped in the reloaded pockets. Both crimped half-rows then unfold into a 2.5 mm comb, where they interleave exactly, and a housing is moved onto the whole row in one push with no stored feed, then tested on a real wafer.

- contacts: loose kit contacts · steel: made dies (EDM, machined, laser-cut) · meeting: the person presents, the machine takes · usable without a motor.
- **Branch of** f5.
- **Combines:** [change-the-question/c1](../change-the-question/summary.md), [into-the-housing/i3](../into-the-housing/summary.md), [ribbon-as-pallet/a8](../ribbon-as-pallet/summary.md).
- **Automates:** crimp, insert, verify insertion and pin order.
- **What the person still does:** Loading loose contacts into pockets (or pushing them off a post bar), splitting into planes, operating the press, parking and unparking the planes, making the housing move: about 30 calls per unit.
- **Major unresolved problems:**
  - Split length 12-20 mm behind the housing, Derek's call
  - A five-profile EDM plate with matched heights, and its price
  - One fixed insulation step for all stations
  - Unparking into the 2.5 mm comb without a pick; J4/J7 need a sort
  - Lifting crimped contacts out of close-fitting pockets
  - The one-shoe branch fails with 2.7-3.0 mm open clone wings unless plane B is tacked first
  - Rows of four and five need more than 1 t at the high estimate

### [f6 — Two blades, two drives: the copper to its geometric stop, the silicone jacket to its own height](ideas/f6-two-blades-two-drives.md)

f3's knee press with its upper tooling split: the conductor crimper on the knee to a geometric bottom, and beside it in the same slot a separate insulation crimper on its own small NEMA 17 lever drive (<=150 N), its own load cell and a motor-set wedge. The conductor is crimped first; then the insulation blade descends alone to the height a one-time 35-crimp sweep found between cutting the jacket and overfilling the cavity (roughly 2.0-2.2 mm tall at 1.8-1.9 mm wide), and its load cell sees the 20-500x steeper slope if the tips reach copper. The camera reads the insulation crimp in silhouette, and after the tab cut a track section drops ~3 mm so a 2 mm pin can bend the wire's tail down 60-90 deg, putting the wing tips on the outside where a cut gapes 0.23-0.56 mm.

- contacts: carrier strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Branch of** f3.
- **Combines:** [ribbon-as-pallet/a3](../ribbon-as-pallet/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** As f3 (split, strip, ribbon loading, insertion), plus the per-lot window sweep and Derek's call on bend-testing every crimp or a sample.
- **Major unresolved problems:**
  - The window is modelled, not measured
  - Where today's SN-2549 insulation crimp lands, and whether today's looms already have cut jackets
  - A thin insulation blade sliding square along a conductor blade that has taken 2.4 kN
  - Squeezed-out silicone collars at the housing's rear entry
  - Room below the barrel at f3's press (a dropping track section, unbuilt)
  - Whether tip cuts show only at the top
  - The cost of three bends per production crimp

### [f7 — Where the steel comes from: die cartridges from four sources, closed by any press](ideas/f7-where-the-steel-comes-from.md)

One small press (f3's knee or a 1 t arbor press) with a pocket and a pusher, and interchangeable palm-sized die cartridges that share one outer shape: two ground pins, a return spring, their own stop block, a button. Their dies come from harvested SN-2549 jaws, an OTP XH knife set, wire-EDM plates to a traced drawing, or ground flat stock (or laminated hardened shim) stood on edge for anvils. The same ribbon is crimped by each on one afternoon and compared by height, section and pull, each die's channel width measured with pin gauges and its height set for that width, and the steel Derek settles on moves unchanged into f3, f4, f5, f8, f9b or f10.

- contacts: either loose or strip · steel: any of several · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [machine-that-sees-and-learns/v3](../machine-that-sees-and-learns/summary.md), [procedure-is-the-machine/p6](../procedure-is-the-machine/summary.md).
- **Automates:** crimp.
- **What the person still does:** Laying contact and conductor into an open cartridge; making or buying cartridge parts; the comparison measurements.
- **Major unresolved problems:**
  - Knife-set price, dimensions and profile unobserved; no Prime listing
  - EDM price and the roof form, which no quoted tolerance covers
  - SN jaw seat geometry; jaws alone not on Prime
  - Line-boring cartridge pins to +/-0.01-0.02 mm, or a bought die set (none on Prime)
  - Whether spring-temper shim survives as an anvil
  - A heavy-series disc-spring stack (only light stainless on Prime)

### [f8 — A narrow press at the housing's mouth: crimp with the box already in its cavity](ideas/f8-narrow-press-at-the-housing-mouth.md)

A fixed steel C with a knee drives an EDM-cut stepped crimper, 2.9 mm wide at the conductor step (1.5 mm channel, 0.7 mm walls) and 2.5-2.7 mm at the insulation step, whose walls land on anvil-block shoulders below the floor; the housing nest is fixed in Y and floats in X and Z so the steel die is master, and a comb behind the rear face centres the seated neighbours. A strip over a crowned block presents the lead contact, pushed box-first 1.4-2.4 mm into its own cavity; a presser lays the conductor from its feed-storing saddle, the knee crimps 0.2-0.3 mm from the PA6 face, the tab is drop-sheared, the anvil drops 1.5 mm to clear the lance, and a blade pushes the contact home with a force trace and 5 N pull-back before the carriage steps 2.5 mm.

- contacts: carrier strip · steel: made dies (EDM, machined, laser-cut) · meeting: the housing locates the contact.
- **Combines:** [into-the-housing/i2](../into-the-housing/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splitting and stripping; laying conductors over saddles in cavity order including J4/J7 crossings; threading the strip; loading and unloading housings; wafer test.
- **Major unresolved problems:**
  - The transition t decides it: an anvil can stop behind the lance only if t >= 0.34-0.74 mm
  - EDM of the 2.9 mm stepped crimper and shoulder-bottoming anvil; surplus force capped near 1 kN
  - X registration through the floating nest (0.00 to +0.08 mm net beside a seated wire)
  - The cavity's real rear opening
  - Pushing a contact box-first while its carrier is attached; feeding on an arc
  - No proof pull before insertion (latch holds 14.7-19.6 N)
  - Two-ribbon housings (J1, J4, J7)

### [f9 — A light station tacks a half-row of loose contacts on; a heavy station crimps them one by one in a keyed nest](ideas/f9-tack-station-feeds-crimp-station.md)

At an attended station T, a ribbon pallet whose clamp face is the split root holds a half-row split at 3.4 mm; loose kit contacts in a pallet receive the conductors from a presser comb, and a sheet-steel comb closes every insulation barrel loosely in one light stroke (66-660 N), pinning each contact at its axial position and roll; the other plane follows. The same pallet goes to an unattended station C, f3's knee press with a keyed steel nest (box slot, lance relief, front stop), where a stage lowers one tacked contact vertically into the nest while a fork holds the rigid in-plane neighbours up and the other plane is parked folded back at the root. The knee crimps the conductor barrel and re-forms the insulation barrel, re-touches for height, the far end names the conductor, and a neck blade reacts a 20 N pull.

- contacts: loose kit contacts · steel: any of several · meeting: conductor brought to a fixed die · usable without a motor.
- **Combines:** [change-the-question/c1b](../change-the-question/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Splitting, stripping, loading loose contacts into the tack pallet, tacking (attended), J4/J7 crossings at the lay, seating the pallet at station C, insertion. About 34 calls per unit if the pallet carries each end from T to C.
- **Major unresolved problems:**
  - Tack grip on silicone, measured
  - Tack-first crimp quality (sectioning)
  - Folding and swapping the parked plane at station C without a person
  - The fork's 3-4 mm lift at 3.4 mm pitch
  - Transition t for the nest's anvil and the neck blade

### [f9b — Tack on the strip: dock a ribbon end onto a strip, tack every contact, cut the tabs, then crimp one at a time in a keyed nest](ideas/f9b-tack-on-the-strip.md)

A ribbon pallet, its end fanned to strip pitch and stripped after the fan, docks on three balls onto a strip segment lying on slot pins, with a hardened rail under the insulation barrels only, so every conductor drops into every open contact and the far end reads each conductor to the grounded carrier. A toggle lever drives a laser-cut tack comb to its stop, closing every insulation barrel loosely, and a second lever shears every tab against the rail's edge while the comb holds the contacts (they see at most the tab's 3.6-6 N mm plastic moment). The pallet then goes to a fixed steel C whose narrow post carries a keyed nest; a stage lowers each tacked contact straight down into the nest (loading the tack across the jacket), the knee crimps the conductor barrel, f6's second blade sets the insulation barrel, re-touch reads height, a neck blade reacts a 20 N pull against the web clamp, and the stage bends the wire down over the anvil's rear edge for a look.

- contacts: carrier strip · steel: any of several · meeting: pallets dock (all contacts placed at once) · usable without a motor.
- **Branch of** f9.
- **Combines:** [ribbon-as-pallet/a2](../ribbon-as-pallet/summary.md), [change-the-question/c1b](../change-the-question/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Parting, fanning and stripping the ribbon end at pallet stations (or by hand), snipping and laying a strip segment, docking, pulling two levers, moving the pallet to the heavy station (about 55 s per ribbon end, 14 calls per unit), and insertion after converging the row from ~7 mm to 2.5 mm.
- **Major unresolved problems:**
  - Tack grip on silicone and the tack-first crimp
  - Transition t: anvil behind the lance (t >= 0.34-0.74) and neck blade (t >= 0.50-0.70)
  - Ejecting a box from a slot 0.05 mm longer than itself
  - Strip pitch unmeasured; a 21-30 mm split behind the housing is Derek's call
  - Converging the crimped row to 2.5 mm and the copper set the fan leaves
  - A loose tack re-formed cleanly by the insulation blade
  - Room for the downward bend beside the C's lower arm (~0.5 mm estimated)

### [f10 — Lift once, crimp upright: a fixed steel C over a flat row, its anvil a fin rising from below](ideas/f10-lift-once-fin-from-below.md)

The ribbon stays flat at 2.5 mm in procedure-is-the-machine's cassette (keys = cavities, crossings in the loft, far end in a pogo block) or at a reel clamp; a finger lifts only conductor k by 3.5 mm, a grounded trim blade squares it and names it through the far end, and a side silhouette measures its bare length. A post bar holding contacts in key order on 0.64 mm posts slides contact k onto the stripped end through fully open barrels to the camera-set depth, a stepped fin of ground stock (1.45 mm under the conductor barrel, 1.88 mm under the insulation barrel) rises through k's empty slot between the unlifted neighbours, and a fixed steel C's knee crimps from above to its geometric bottom with a re-touch height. The fin drops, a hook in the neck pulls 20 N, and k is laid back and squared, the crimp upright with its lance down.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die · usable without a motor.
- **Combines:** [procedure-is-the-machine/p1c](../procedure-is-the-machine/summary.md), [procedure-is-the-machine/p1](../procedure-is-the-machine/summary.md), [procedure-is-the-machine/p6](../procedure-is-the-machine/summary.md), [terminal-supply/a4](../terminal-supply/summary.md).
- **Automates:** strip, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cutting, peeling or splitting, laying the cassette with J4/J7 crossings, filling the post bar in key order, docking cassettes, insertion (rows arrive upright in cavity order), labelling.
- **Major unresolved problems:**
  - The crimper's steel profile (knife set or EDM)
  - Transition t for the fin's lance relief (0.34-0.74 mm) and the hook (0.50-0.70 mm)
  - Tip wander against 0.55-0.92 mm of fin clearance; the tip comb is unbuilt
  - Set below 20 mm of free length needs a squaring pass
  - Gate block and fin repeatability over ~3,200 cycles
  - The post bar's lateral compliance against its positioning
  - Proof-pull reaction at a cut loom needs a clamp squeezing the jacket 15-30 % over 5-20 mm

## Combinations with other explorers

- f9b = ribbon-as-pallet a2 (a ribbon fanned to strip pitch docks onto a strip segment, every contact placed in one motion, continuity to the carrier before force) x change-the-question c1b (a light gang tack of the insulation barrels) x force-and-form f3/f6/f9 (a knee press with a keyed nest and a second insulation blade). The carrier's job ends at the tack, so the heavy station needs no feeder, pilot pin, threading, planes or fork; the tab shear under the comb puts at most the tab's plastic moment into each contact, and the vertical entry loads the tack across the jacket
- f10 = procedure-is-the-machine p1c/p1/p6 (lift one conductor once, cassette with keys = cavities, far-end identity, reel clamp) x terminal-supply a4 (contacts on 0.64 mm posts) x force-and-form f4/f3/f7/f8 (a fixed steel C with a knee, ground-stock fin anvil, lance relief). Works the flat row at 2.5 mm with a 3.5 mm lift and keeps the crimp upright; FP2 (p5's camshaft turning the knee through straight) is its branch
- f5b = force-and-form f5 (self-stopping cassette, any press) x change-the-question c1 (planes, half-rows at 5.0 mm) x ribbon-as-pallet K4/a8/a7 (merge at 2.5 mm, strip after the spread, clamp face at the split root) x into-the-housing i3 (the housing moved onto the whole row). The two half-rows interleave exactly at 2.5 mm, so one housing move inserts both with zero stored feed
- f2c = force-and-form f2 (applicator in a slow crank press) x change-the-question c1 and c5 (pallet, push, wafer test; ends as stock, cut last) x procedure-is-the-machine p7 and p6 (whole-end strip at the clamp; slip ring and puller). One pallet at housing pitch filled in cavity order replaces two half-row pallets
- f8 = into-the-housing i2 (the product cavity locates the contact) x force-and-form f4/f3 (a fixed steel C with a knee, shoulders below the floor, re-touch height), with 0.7 mm walls and a floating nest
- f9 = change-the-question c1b (gang tack) x force-and-form f3-t (knee press with a keyed nest), with f3b's station A as the firmer tack and f9b as the no-planes branch
- f4 x ribbon-as-pallet a6 (far-end port): the captured contact on grounded steel is a touch probe that locates the tip to ~0.01-0.05 mm and names the conductor before threading (ribbon-as-pallet K7)
- f6 x ribbon-as-pallet a3 (K5): on silicone the insulation crimp cannot carry the loom's pull, so a backshell fold carrying 14-69 N without loading any crimp is the strain relief; and f6 x ribbon-as-pallet K6: a whole crimped row bent down at once over a steel edge by swinging the ribbon pallet
- f7 x procedure-is-the-machine p6 (FP5): the four steel sources and f6's insulation sweep qualified at the reel clamp, each sample with identity, open/short, a whole-reel pull reaction and 6 mm of reel as its cost; and f7 x machine-that-sees-and-learns v3 (the settable-stop press that sweeps crimp height)
- f5, f5b and f9 x procedure-is-the-machine p7 (FP4): one whole-end strip stroke puts every insulation edge on one line, with the fan's pull-back (~0.6 d^2/L) as the stated cost for rows of 4-5

## Transferable mechanisms

- Geometric bottom: a crank at bottom dead centre (1 deg = 3-4 um) or a knee at straight (0.2 mm short = ~1 um) makes crimp height nearly independent of the motor
- Hard stop in a short steel local loop, and with stops a compliant outer loop is the design: the surplus past the stop is loop stiffness times margin, and a spring caps a doubled contact
- Separate precision from power: dies, stop and gauge carry precision; any slow push supplies force
- Re-touch crimp height: after the stroke, close again at ~10 N and read an indicator across the dies
- Chase a measured height in two or three hits, approaching from above, the knee's straight position as the over-travel guard
- Target crimp height follows channel width (compaction is W x H, 1.20-1.32 mm^2 here): measure the channel with pin gauges and set the height for it; a +/-0.05 mm channel is then usable for a single die
- Place the contact on the conductor first and close the die on both, or hold short of pinching: capture at the first tooth closes the insulation bore on floors of 1.6-1.7 mm
- Camera bare length as the axial reference: it splits the strip's +/-0.2 mm scatter into +/-0.1 on the brush and +/-0.1 on the window; a blade used as a depth stop leaves the whole error on the window and can fold strands
- Neck blade dropped only after the crimp, bearing on the box's upper rear face for the proof pull (needs t >= 0.50-0.70 mm; 24-48 MPa at 20-39 N)
- React a proof pull at a long clamp or a whole reel, not a short jaw on silicone: strands slip inside a squeezed jacket at 0.5-6.3 N per mm of grip
- Identity through the far end: a grounded die, nest, trim blade or applicator plus a far-end port names the conductor before the stroke; insulated anvils give a gang per-station identity
- The jaw's closing direction is the contact's floor normal: a head working a flat row must close normal to it, and only a fin anvil needs to pass through the row plane
- Fin or anvil from ground flat stock stood on edge, or laminated hardened shim: its width is its thickness
- Lance relief at every anvil and nest; a head leaving along the wire leaves toward the box and drops its anvil
- Two blades, two drives: the insulation crimp on silicone is set by position, not force, and its own load cell sees tips reaching copper
- Bend-and-look with the wire's tail bent away from the wing tips (down for a B/F insulation crimp): over a 2 mm pin a cut gapes 0.23-0.56 mm; bending the other way closes it
- Tab shear under a tack comb held at its stop: the contact sees only the tab's plastic moment (3.6-6 N mm), so a tack survives the shear
- Vertical entry into a keyed slot cut ~0.05 mm over the box loads a tack across the jacket, never along it
- Length from the web is a design quantity: groups inserted in turn need stored feed equal to the insertion stroke (6-9 mm); crimp everything, merge at housing pitch, insert once
- Strip after the fan or spread, at the fan block's face; a grooved fan block pressed from the root captures rows of any length
- Die cartridges with their own stop and a spring in the pusher let any press close any die source
- A gang crimper cut as one plate at 5.0 mm has 3.0-3.5 mm webs; narrow in-row dies hold with 0.7 mm walls landing on shoulders below the floor
- Floating drop-shear under the carrier cuts tabs from below, away from the wire
- Printed parts guide, never set, and never carry the crimp

## Key findings

- Bend-and-look by pin diameter: a 2 mm pin gives the jacket 0.46 outer strain and a cut gapes 0.23-0.56 mm (0.18-0.77 mm over 1-3 mm pins); wave2.py's '1/2/3 mm pins' were radii. The tail must bend away from the wing tips (down), needing ~3 mm of room below the barrel [calc: explorers/force-and-form/calc/final_w3.out.txt §1]
- Tab shear under a tack comb at its stop: 53-104 N per tab; the contact sees at most the tab's plastic moment, 3.6-6 N mm, reacted by the comb with 2-8 N; the tack carries none of the shear [calc: final_w3 §2]
- A neck blade dropped after the crimp needs transition t >= 0.50-0.70 mm (0.70-0.90 mm if it stands in place during threading); it bears 24-48 MPa on the box's upper rear face at 20-39 N [calc: final_w3 §3]
- A 20 N pull through a jaw on the jacket needs 3.2-14 mm of grip at 30 % squeeze and 9.5-40 mm at 10 %: a 3-5 mm throat jaw is marginal, so the reaction belongs at a web clamp or reel [calc: final_w3 §3, exchange_procedure_w3 §4]
- In f1 the neighbours must stand 4-6 mm higher than the working tip, which bends them 37-46 deg at a 20 mm split and 26-32 deg at 40 mm; an elastic arc above copper's 67 mm set radius shortens a 30 mm conductor only 0.25 mm, so the set is unavoidable and only its direction can be chosen [calc: final_w3 §4]
- f8 with 0.7 mm walls (2.9 mm crimper) leaves 0.00 to +0.08 mm net beside a seated neighbour's wire; 0.8 mm walls rub (-0.10 to -0.02); 0.7 mm walls run 720-1,740 MPa unbraced at k 0.3-0.5 [calc: final_w3 §5]
- Both half-rows in one 2.5 mm shoe: the crimper plate keeps 0.90 mm conductor walls and 0.57 mm insulation walls over grooves for the crimped plane, but the insulation flare's edge falls to 0.22/0.10/-0.05 mm at 2.46/2.7/3.0 mm open wings [calc: final_w3 §6]
- Target crimp height by channel width: 1.20-1.32 mm^2 / W, i.e. 0.80-0.88 mm at 1.50 mm, 0.74-0.81 at 1.63, 0.69-0.75 at 1.75; a +/-0.05 mm channel is +/-3.3 % compaction and is restored by -/+0.027 mm of height [calc: final_w3 §7; ribbon-as-pallet w3 §7]
- Crimped contacts fit side by side at 2.5 mm (0.45-0.70 mm between insulation crimps; box pockets leave 0.40-0.45 mm ribs), so a single-conductor station can fill one pallet at housing pitch in cavity order [calc: final_w3 §8]
- A latched contact holds 14.7 N (Molex analog) to at least 19.6 N (KONNRA XH clone spec), so the ~20 N proof pull comes before insertion [calc: final_w3 §9]
- Camera bare length splits the strip's +/-0.2 mm scatter into +/-0.1 mm on each of brush and window; touch-off on a blade leaves +/-0.2 on the window [calc: final_w3 §10]
- Two half-rows from one web cannot be pushed into a housing in turn: the 6-9 mm insertion stroke against at most ~0.4 mm of lay slack; merged at 2.5 mm they interleave exactly and one housing move inserts both [calc: ribbon-as-pallet exchange_on_force_and_form_w3 §1]
- FP1/f10: a 3.5 mm lift clears every neighbour case for a crimper of any width; a stepped fin (1.45/1.88 mm) keeps 0.55-1.42 mm to the neighbours and 27 kN of Euler load against 3 kN [calc: exchange_procedure_w3 §1-2]
- On this silicone the insulation crimp is not a pull-out grip (strands slip in the jacket at 0.4-9 N) and is invisible in the stroke's force; its window is roughly 2.0-2.2 mm tall at 1.8-1.9 mm wide, above the clone spec's PVC-class 1.80 [calc: wave2 §5]
- Only the 3 t arbor presses (VEVOR AP-3 $255.90, PR-3 $262.14, 310 mm opening) open far enough for a mini-applicator; the 1 t presses open 139.7-150 mm [Prime table]
- Force and drives: peak 0.75-2.43 kN in the modelled family (xh-facts 0.8-2.6 kN in all); crank <3.3 N m, knee 60-160 N, hand tool 40-250 N at the grip [calc: stroke_model, drives]

## Where this view still had trouble

- Stripping and splitting 22 AWG silicone reliably without a person: every idea here borrows a stripper (p7, a8, a7) whose tear behaviour this view cannot judge on paper
- A contact whose transition t turns out shorter than ~0.34 mm: then f8, f9b's nest, f10's fin and the neck blade all need a lance-folding entry or a different reaction face, and no variant was worked out
- A proof pull for f8's crimp-in-the-cavity before insertion: the box's rear face sits at the housing's rear face and nothing reaches it
- Two-ribbon housings (J1, J4, J7) at the housing's mouth (f8) and J4/J7 crossings in any gang without a person or a sort
- Seeing a lost or cut strand inside a closed crimp: force monitoring cannot, and only the pre-crimp silhouette and sections see it
- Loading loose kit contacts into pockets or magazines in orientation without a person: relied on other explorers' post bars and pocket plates
- A cheap, JST-correct crimper profile without the licence-gated drawing: the roof form is untoleranced by every source here
- Motorless versions of f4, f6 and f8: each depends on coordinated motion
- Ejecting a crimped box from a close-fitting keyed slot reliably, thousands of times
- Measuring the insulation crimp's real window, and tip cuts that open at the sides rather than the top, without a sweep on the real wire

## Questions for Derek

- One kit contact, three photographs under the ELP camera: side-on (the transition t from box to conductor barrel, the lance root and tip), end-on (the insulation barrel floor's inner width), and top-down (the transition strap's width against the box floor). They decide f8, f9b's nest and neck blade, f10's fin, f1's hold and f3's capture height
- The tack by hand: lay three contacts of a strip segment under three split, stripped conductors, close each insulation barrel loosely with smooth pliers, cut the tabs, then pull and twist each contact on its conductor with the bench scale
- Five of today's SN-2549 crimps on the ribbon: caliper conductor crimp height and width and insulation height and width, then bend each 90 deg over a 2 mm pin with the tail going away from the wing tips, three times, and look at the top of the insulation crimp. Is any jacket cut?
- Squeeze the SN-2549 through one XH crimp with a scale at the handle ends: handle force at the moment the ratchet releases, handle travel, and whether the jaws meet face to face
- How long a split behind each housing can the looms carry: none (f10), 12-20 mm (f5b, f4, f9), or 21-30 mm (f9b)?
- A crimped conductor clamped in a TPU clamp and pulled at 20 N through the box with a luggage scale: does the copper creep back inside the jacket?
- Would you buy one 100-piece SXH-001T-P0.6 strip ($4.71) to measure carrier pitch, pilot hole and tab length, and five JST ASXHSXH22K305 leads (~$4.50) as reference crimps?
- Should a machine reproduce today's SN-2549 crimp, or aim at JST's profile as judged by the reference lead at the machine's own crimp width?
- Would you buy an OTP XH knife set or send a traced crimper profile out for wire EDM, and would you order laser-cut plate for cartridges and presses?
- Should every production crimp get a proof pull and a bend-and-look, or a sample per ribbon end?
- Does the VEVOR 12-ton shop press have a pressure gauge, and are its bed plates flat enough to seat a small cassette?
