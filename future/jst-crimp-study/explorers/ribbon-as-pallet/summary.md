# ribbon-as-pallet

*The ribbon is a precision part.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [a1 — Pallet tour: one clamp, one stage, a fixed strip-fed crimp station](ideas/a1-pallet-tour.md)

A printed pallet clamps a cut ribbon once, its lid face the split root, and an XY stage drives it past fixed stations: zip, a fan block at 5 mm that holds the conductors 5 mm above the anvil plane, flush cut and ring strip at the tongue lips, and a reel-fed OTP side-feed applicator in a slow crank press. At the crimp a fixed cam presses one conductor's hinged tongue down so its lip lays the conductor level into the pre-fed contact; the crank crimps, shears and pauses while the stage backs out before the feed moves, and the tongue springs back up with the crimped conductor. Continuity through the far-end port before each stroke, a strain-gauge force curve and a ΔF/k crimp height report every crimp.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Combines:** [borrowed-machines/b1b](../borrowed-machines/summary.md).
- **Automates:** split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting ribbon to length and loading the pallet, housing supply, reel threading, scrap, every far end; about 20 attended minutes a unit, called every ~11 minutes [estimate].
- **Major unresolved problems:**
  - The applicator's upstream envelope: how high the feed plates stand under the neighbours held at h
  - A 30-47 mm split with the tongue (a backshell there stands 52-69 mm above the board)
  - Whether the OTP cam has a pause window between crimpers clearing and the feed finger moving
  - Set left by the tongue's bend and lift-back, and straight insertion after it
  - The crank needs a motor the weld station is not using (the bench's NEMA 23 and DM542T are in the cap-weld tube rotator); guarding

### [a1b — Hand shuttle: the same pallet moved by hand between seated stations](ideas/a1b-hand-shuttle.md)

The a1 pallet is carried by hand between stations, each with a kinematic seat of hardened balls on ball pairs or case-hardened rod with magnet preload, and rails with stops for path motions. At the crimp station the person clicks the pallet along detents to a Y stop where a fixed cam lays that conductor's tongue into the waiting contact, strokes the applicator with a hand press (the VEVOR jack with a hard-stop collar), and pauses the lever between crimp and feed. An SN-2549 variant works only with every other conductor folded back (borrowed-machines b1 and b2).

- contacts: carrier strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Branch of** a1.
- **Combines:** [borrowed-machines/b1b](../borrowed-machines/summary.md), [borrowed-machines/b1](../borrowed-machines/summary.md), [borrowed-machines/b2](../borrowed-machines/summary.md).
- **Automates:** supply contacts, place contact on conductor.
- **What the person still does:** All motion between stations, every stroke and the pause in it, watching each crimp, preparation at the seats, insertion by hand jig, far ends; about 65 attended minutes a unit against ~46 by hand today [estimate].
- **Major unresolved problems:**
  - a1's upstream envelope and 30-47 mm split
  - Whether a person reliably pauses the lever between crimp and feed
  - Attended time above today's hand procedure
  - Whether one long detented rail beats six seats
  - The applicator is a long-lead purchase with no Prime listing

### [a1c — Crimp from the upstream end, fold each finished conductor back (a1 x borrowed-machines b1)](ideas/a1c-crimp-upstream-first-park-after.md)

The reel-fed applicator keeps its feed and shear in a slow crank, and the pallet's fan lies flat in the anvil plane entirely downstream of the anvil, so no uncrimped conductor is ever over the feed side. Each conductor slides in +Y along the open barrels' axis at barrel height and a flat sole seats it; the crank crimps and pauses while the stage backs out, then feeds. A fork on the applicator's axis folds the crimped conductor 180 degrees back over the pallet into a numbered pocket, and the pallet indexes; stripping is by a8 at the fan face.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Branch of** a1.
- **Combines:** [borrowed-machines/b1](../borrowed-machines/summary.md), [borrowed-machines/b1b](../borrowed-machines/summary.md).
- **Automates:** split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting and loading the pallet, reel threading, scrap, carrying the pallet to insertion, far ends.
- **Major unresolved problems:**
  - The applicator's downstream tooling width at 5 mm crimp pitch (lowest 3 mm within +/-3.95 mm), which sets the pitch and the 23-30 mm split
  - Root peel and set from two reversals at the fold
  - The crank's pause window on the OTP cam
  - Axial entry of 60 untwisted strands
  - A second motor for the crank

### [a2 — Two pallets meet: the carrier strip is the contact pallet](ideas/a2-two-pallets-meet.md)

A carrier segment of N+2 SXH contacts lies on a steel strip pallet on slot pins, with a groove along X under the lance line; a ribbon pallet fanned to strip pitch (~7.1 mm), flush-cut and stripped at its fan face docks on three hardened ball seats, and every conductor goes into every open contact at once (a finger comb presses them in if the wings prove narrower than the jacket). Continuity to the grounded carrier confirms placement before any force. A 1 kg steel C-frame head with harvested OTP dies rides a rail flush with the contacts' floor and crimps each from the box end; each conductor is pulled to 20 N with a pad on the crimped barrels, and a notched shear comb cuts every tab.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: pallets dock (all contacts placed at once).
- **Combines:** [borrowed-machines/b3](../borrowed-machines/summary.md).
- **Automates:** split, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting and loading the ribbon pallet, laying strip segments (~20 s), moving pallets, far ends; 81 contacts a unit.
- **Major unresolved problems:**
  - Strip pitch and whether the drawn open-wing widths are inside or outside widths (capture ~0 to +/-0.5 mm)
  - Harvested dies aligned in a 1 kg C-frame, and passing under the lance (needs neck t >= 0.34-0.74 mm)
  - Whether docked conductors stay in as the support comb swings away
  - Shear-comb tab length
  - 21-30 mm split with a 4-5 mm arc left in the outer conductors (order A)

### [a2b — Gang stroke: the docked cassette in the idle 12-ton press with a stop-block die set](ideas/a2b-gang-press-stop-die.md)

The docked cassette slides into a two-post guided die set on the VEVOR 12-ton press bed: N anvils, each with a lance relief, rise through windows and N B-profile punches hang from the upper shoe at strip pitch. The person pumps until the upper shoe bottoms on hardened stop blocks, crimping every contact of the ribbon end in one stroke to the blocks' height (4-13 kN for five against ~118 kN). A load cell under the lower shoe sees a missing conductor (12-20 %) or contact (20 %).

- contacts: carrier strip · steel: any of several · meeting: pallets dock (all contacts placed at once).
- **Branch of** a2.
- **Combines:** [borrowed-machines/b1b](../borrowed-machines/summary.md), [force-and-form/f5](../force-and-form/summary.md), [force-and-form/f7](../force-and-form/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Pumping the press (unless an air-over-hydraulic jack is fitted), moving the cassette, a2's loading and far ends.
- **Major unresolved problems:**
  - N matched punches and anvils: harvested pairs each shimmed, one wire-EDM plate pair, or two single-arch strokes
  - Target height scales with channel width (a 1.5 mm reference copied to a 1.6 mm channel over-compacts 3-10 %)
  - Punch retraction (a stripper plate)
  - Strip-pallet windows that hold the carrier flat, and a lance relief in every anvil

### [a2c — Loose-contact cassette: kit contacts in keyed printed nests](ideas/a2c-loose-contact-cassette.md)

A printed nest bar with keyed pockets (box pocket, one-sided lance relief, rear shoulder as the pull reaction, open cradle) replaces the carrier, so the CQRobot kit contacts on hand, BXH bags or strip cut one at a time dock at a free 4-5 mm pitch. Pockets are loaded by tweezers, a stapler stick, a coin-motor shaker or a strip feeder, and checked by camera. Variants: pockets set back by each conductor's fan recession so an end stripped before the split docks with no equal-path fan; a tack then the SN-2549 (a10b); change-the-question c1's 3.4 mm half-rows.

- contacts: either loose or strip · steel: any of several · meeting: pallets dock (all contacts placed at once) · usable without a motor.
- **Branch of** a2.
- **Combines:** [change-the-question/c1](../change-the-question/summary.md), [change-the-question/c1b](../change-the-question/summary.md), [procedure-is-the-machine/p7](../procedure-is-the-machine/summary.md), [borrowed-machines/b2](../borrowed-machines/summary.md), [machine-that-sees-and-learns/v4b](../machine-that-sees-and-learns/summary.md).
- **Automates:** supply contacts, place contact on conductor.
- **What the person still does:** Loading or supervising the bar, preparing and loading the ribbon pallet, far ends.
- **Major unresolved problems:**
  - Kit contact dimensions and origin (JST or clone)
  - Loose open barrels tangle when shaken
  - Lance-only relief as a reliable orientation reject
  - Continuity through loose contacts needs a ground leaf per pocket
  - Crimping in the bar needs steel under each contact

### [a2d — By hand: dock the pallets, then slide the cassette under a guided hand press](ideas/a2d-by-hand.md)

No motors: the person lays a strip segment on slot pins, docks a hand-prepared ribbon pallet on hardened seats, photographs the row and meters each conductor to the carrier, which tests docking with no crimp tool. The cassette then slides on detents at strip pitch under one harvested OTP crimper-and-anvil pair in a guided hand frame (the VEVOR jack with a hard-stop collar, or a snap press), stroked once per contact; each conductor is pulled with a luggage scale against a pad on the barrels, and a shear comb on a lever cuts the tabs.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: pallets dock (all contacts placed at once).
- **Branch of** a2.
- **Combines:** [borrowed-machines/b1b](../borrowed-machines/summary.md).
- **Automates:** place contact on conductor.
- **What the person still does:** Preparation at the bench blocks, strip segments, every stroke, pull, shear and insertion, far ends; ~2-3 minutes of hand work per 5P at the crimp.
- **Major unresolved problems:**
  - Keeping a harvested die pair aligned in a hand frame
  - A repeatable hard stop on a pumped jack
  - The dies are a long-lead purchase with no Prime listing

### [a2e — Docked strip through a feedless applicator (a2 x borrowed-machines b1b)](ideas/a2e-docked-strip-through-a-feedless-applicator.md)

An OTP side-feed XH applicator stands on the VEVOR press under a 3-4 mm eccentric (NEMA 17 + 26.85:1 planetary), with feed finger, pressure plate and shear punch removed and a pilot in the shear punch's pocket. A carriage on an MGN12 rail holds a strip segment by grips in its end slots on a shelf flush with the track and grooved under the lance line; a ribbon pallet docks so every conductor lies in every contact, continuity to the carrier is read, and the carriage moves the row through the anvil one pitch per turn while the pilot locates each contact by the carrier's own slot. Back at the load position, slot pins and a pad take a 20 N pull per conductor, then a shear comb cuts every tab.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: pallets dock (all contacts placed at once).
- **Branch of** a2.
- **Combines:** [borrowed-machines/b1b](../borrowed-machines/summary.md), [procedure-is-the-machine/p5](../procedure-is-the-machine/summary.md), [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f6](../force-and-form/summary.md), [force-and-form/f8](../force-and-form/summary.md).
- **Automates:** split, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting and loading, strip segments, docking, far ends; with hand preparation ~178 s of person time per end against ~108 s of machine, ~60 attended minutes a unit, called every ~1.8 min [estimate].
- **Major unresolved problems:**
  - Which OTP parts unbolt, whether a pilot fits the shear punch's pocket, and whether the ram has a return spring (scan it)
  - Room ~18-35 mm downstream of the anvil for the crimped row
  - The eccentric's frame stiffness and shut-height setting
  - Shear-comb tab length
  - 21-30 mm split with a 4-5 mm arc in the outer conductors
  - Genuine SXH against the applicator vendor's clone; guarding

### [a3 — The backshell that ships: the clamp is applied once and never removed](ideas/a3-backshell-that-ships.md)

A 1-2 g printed backshell per loom, with the ribbon folded 180 degrees around its bar under a snap cover (the IDC strain-relief fold), is the machine's pallet and datum, the loom's embossed label and notch-coded recipe, and its strain relief. Its front face is the split root and tear stop, and a 3 N cover resists 14-69 N of loom pull without loading a crimp, which matters because the insulation crimp on this silicone lets the strands slip at 0.4-9 N. It is also the reel puller's grip, and with fold-back parking the split falls to 8-15 mm.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [borrowed-machines/b1](../borrowed-machines/summary.md), [borrowed-machines/b4](../borrowed-machines/summary.md), [force-and-form/f6](../force-and-form/summary.md), [procedure-is-the-machine/p3](../procedure-is-the-machine/summary.md).
- **Automates:** —.
- **What the person still does:** Printing and folding a backshell onto every loom end, loading the holder, far ends.
- **Major unresolved problems:**
  - Room above the board: 30-69 mm depending on the split
  - Arms hooking ~0.8 mm XHP end flanges without reaching the wafer shroud
  - Silicone-on-PETG friction, which sets the fold's grip
  - A part on every loom is Derek's decision

### [a4 — Spool as magazine: terminate the leading end, then feed out and cut](ideas/a4-spool-as-magazine.md)

The ribbon is never cut before it is terminated: a belt feed pushes the leading end to a grounded tip stop, with touch-off read through the spool's inner end on a slip ring or hub socket, and a fixed clamp whose face is the split root holds it on a covered floor. Zip, a flat 5 mm fan, and flush cut and ring strip at the fan face come to the clamp, and the clamp rides a short X slide under a feed-intact applicator in a1c's order, each crimped conductor folded back. After insertion and a pin test through the spool, the feed pushes the loom length down a drop tube and a guillotine at the clamp face frees it and squares the next end.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Combines:** [procedure-is-the-machine/p3](../procedure-is-the-machine/summary.md), [procedure-is-the-machine/p6](../procedure-is-the-machine/summary.md), [borrowed-machines/b1](../borrowed-machines/summary.md), [borrowed-machines/b1b](../borrowed-machines/summary.md).
- **Automates:** cut, split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Threading or rewinding spools and connecting inner ends, the recipe list, housing and contact-reel supply, emptying the bin, far ends, rethreading between loom types.
- **Major unresolved problems:**
  - Machine size: a 0.6-0.7 m drop tube plus a spool rack
  - Whether the BNTECHGO spool's inner end is reachable, or a rewind is needed, and whether a straightener marks silicone
  - Threading pairs from two spools without twist
  - Housing supply for mixed loom types
  - The applicator's downstream envelope and crank pause (a1c); J4/J7 crossings

### [a5 — Part, fan and strip inside the pallet (module): three orders](ideas/a5-part-fan-strip-in-the-pallet.md)

The preparation module: a clamped end on a covered floor, parted, fanned, flush-cut and stripped in one of three orders that keep every tip and insulation edge where the crimp needs it. Order A cuts and strips at the fan block face after the fan, which leaves the outer conductors 0.65-2.46 mm long in the finished loom (a 2-5 mm arc); order B cuts at the clamp face, strips the webbed end in one stroke (procedure-is-the-machine p7), zips from the slug's gaps and fans in equal-path humped grooves, leaving every conductor one length; order C touches off and strips each conductor at its own tip. It also holds the catalogue of parting, fanning and stripping options and the isolated-blade nick detector.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [procedure-is-the-machine/p7](../procedure-is-the-machine/summary.md), [borrowed-machines/b4](../borrowed-machines/summary.md), [change-the-question/c1](../change-the-question/summary.md).
- **Automates:** split, strip.
- **What the person still does:** Nothing by itself; it is a module run by whatever carries the pallet.
- **Major unresolved problems:**
  - Neck thickness, valley depth and tear path of the web (repo Open item 5)
  - Bundle eccentricity in the jacket
  - Whether a ring score, and p7's flank tear, leave a clean edge
  - Strand behaviour on a 2.4 mm untwisted stub
  - Capture and hump set in an equal-path fan block

### [a6 — The housing is the last comb: insertion, pairs, and the far-end test port (module)](ideas/a6-housing-as-last-comb.md)

A 2.5 mm closing block and an insertion clamp grip each conductor 1-2 mm behind its barrel at its own front, letting the fronts step as the V staircase a closed fan leaves (a 5P from 7.1 mm: outer +2.47 mm, next +1.22 mm), so contacts latch in pairs from the outside in; slide-along jaws push on the crimped barrel for the last millimetre and a spring-limited pull-back with the camera checks each latch. The nest is a real XH wafer on a load cell and test board, read through the far-end pogo port (Prime P75-E2 conical pins) or the reel for pin map, shorts and J2's empty cavity. J4's and J7's crossings run between the two ribbons, so they go in by hand through a gapped closing block, or by a loft, or J7 is made straight by a wiring choice.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [into-the-housing/i5](../into-the-housing/summary.md), [into-the-housing/i3b](../into-the-housing/summary.md), [borrowed-machines/b1](../borrowed-machines/summary.md), [procedure-is-the-machine/p1](../procedure-is-the-machine/summary.md), [force-and-form/f6](../force-and-form/summary.md).
- **Automates:** insert, verify insertion and pin order.
- **What the person still does:** Housing supply, and J4's and J7's five crossing contacts a unit unless the loft or wiring choice is taken.
- **Major unresolved problems:**
  - Where the contact's rear sits when latched, and whether slide-along jaws fit the rear opening
  - Kit insertion and retention forces (clone: <=9.8 N, >=19.6 N)
  - Whether an HX711 separates two lances latching together
  - Staircase overtravel
  - J4 and J7 crossings

### [a7 — Zip station: tear each web along its own neck, stop the tear at the clamp, and let the tines hold the fan](ideas/a7-zip-station.md)

The pallet drives a clamped end into a nicker of floating razor slivers (or, for an end stripped webbed, straight into the slug's gaps) and on onto a comb of blunt laminated-stainless tines that diverge from 1.7 to 2.5 mm, each driving a tear along its own neck. The tear stops at the clamp face, which is the split root, and the tines leave the conductors fanned toward housing pitch because the copper keeps the bend. A backlit silhouette, a load plateau and isolated tines touching copper report every split.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [procedure-is-the-machine/p7](../procedure-is-the-machine/summary.md), [borrowed-machines/b4](../borrowed-machines/summary.md).
- **Automates:** split.
- **What the person still does:** Nothing on a stage or reel clamp; sliding the pallet along a rail in the hand version.
- **Major unresolved problems:**
  - Neck thickness t_n: the tear stays in the neck only while t_n is well under ~0.6 of the 0.49 mm wall
  - Whether a wedge-driven tear in this silicone runs straight at slow speed
  - Making a diverging laminated tine comb to +/-0.05 mm
  - Whether the crack creeps under a soft TPU lid

### [a7b — Plough station: floating razor blades cut along each valley](ideas/a7b-plough-station.md)

N-1 double-edge razor slivers in printed shoes, each V-nose riding its own valley on a flexure while the blade tip runs in a slot in a steel floor plate, are driven back to 1 mm short of the clamp face. Each blade finds its valley to about +/-0.07 mm independent of the ribbon's pitch stack, keeping at least 0.25 mm of flank wall; isolated blades report any touch on copper. It is for a neck too thick to zip.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Branch of** a7.
- **Automates:** split.
- **What the person still does:** Nothing on a stage; sliding the pallet in the hand version.
- **Major unresolved problems:**
  - Valley depth enough to steer a V-nose
  - Snapping and bonding 0.10 mm slivers square; sliver life
  - A per-width slotted steel floor plate
  - Web flash on each flank under the insulation wings

### [a8 — Rolling ring scorer: the row spins in place under two fixed blades, then the slugs tear off](ideas/a8-rolling-ring-scorer.md)

A fanned, flush-cut row touches off against a grounded stop bar, two fixed single-edge razors close to gauged stops for a 0.58-0.63 mm score radius, and TPU pads on two racks driven by one pinion move equal and opposite, spinning every conductor 0.6 turn in place so the blades' arcs join into a full ring. The blades stay in the score while the pallet draws back 3 mm and each slug tears off at 2.6-9.2 N; isolated blades stop the roll on a copper touch and a backlit frame inspects every stub.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Automates:** strip.
- **What the person still does:** Nothing on a stage; two levers, a knob and a pull in the bench version.
- **Major unresolved problems:**
  - Whether the tear follows the score cleanly on this silicone
  - Bundle eccentricity, which sets the score depth
  - Pads that roll without slipping or flattening the jacket
  - Strand twist kept after the turn and return
  - Slugs clinging to blades or stop bar

### [a8b — Spindle with touch-off: one conductor at a time into a small turning head with a snout](ideas/a8b-spindle-with-touch-off.md)

One conductor at a time enters a hollow printed spindle on 6700 bearings through a snout no wider than 7.8 mm; its copper face touches an isolated stop, read through the far-end port, and two razor-sliver tips on flexures close by a cone to a 0.55-0.60 mm score radius and score three turns. A half pull and a quarter to half turn twist the stub through the slug, and the stop ejects the slug. At 2.5 mm pitch the conductor is lifted ~9 mm into a full-size head instead (procedure-is-the-machine p1c).

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Branch of** a8.
- **Combines:** [procedure-is-the-machine/p1c](../procedure-is-the-machine/summary.md).
- **Automates:** strip.
- **What the person still does:** Nothing on a stage; a knob-turned head in the hand version.
- **Major unresolved problems:**
  - A closing mechanism inside a 7.8 mm snout set to +/-0.02 mm
  - The brush on a turning spindle as a clean nick signal
  - a8's tear, eccentricity and twist questions

### [a9 — The reel end docks: terminate at the reel clamp, dock onto reel strip, crimp through a feedless applicator, cut last](ideas/a9-reel-end-docks.md)

A rewound 80 mm-hub reel with a hub socket on a slip ring feeds a clamp on an X carriage whose face is the cut line; the end touches off through the hub, is stripped webbed in one stroke (p7), zipped from the slug's gaps, and fanned to 7.1 mm in an equal-path fan block whose humped inner grooves keep every tip and strip line on one line. At the dock, grips first take a reel-strip segment onto the carriage, then every conductor drops into its contact and continuity to the carrier is read; the row indexes through a feedless OTP applicator on a 3-4 mm eccentric with a pilot in the carrier slot. Back at the dock each conductor is pulled and every tab sheared, then the row is inserted into an XHP on a real wafer, tested through the hub, drawn to length by a puller gripping a fold, and cut at the clamp face, which squares the next end.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: pallets dock (all contacts placed at once) · usable without a motor.
- **Branch of** a4.
- **Combines:** [procedure-is-the-machine/p6](../procedure-is-the-machine/summary.md), [procedure-is-the-machine/p7](../procedure-is-the-machine/summary.md), [procedure-is-the-machine/p3](../procedure-is-the-machine/summary.md), [procedure-is-the-machine/p5](../procedure-is-the-machine/summary.md), [borrowed-machines/b1b](../borrowed-machines/summary.md), [borrowed-machines/b2](../borrowed-machines/summary.md).
- **Automates:** cut, split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Spools and rewinds, recipe lists, contact and housing supply, pair events and J4/J7's five crossing contacts, labels, far ends; about 12 attended minutes a unit, the machine alone ~3.5 h per 4P reel run [estimate].
- **Major unresolved problems:**
  - p7's flank tear from two straight scores, and the bulge it adds in the window
  - Starting the zip from the slug's gap needs t_n well under ~0.6 of the wall
  - Closing the equal-path fan block over tine-fanned conductors, and the set the humps leave
  - A 22-33 mm split (backshell 44-55 mm above the board)
  - The applicator scan: pilot pocket, return spring, ~32-35 mm downstream room; the eccentric's frame
  - The reel: inner-end access, straightener marks; batching per reel run; J4/J7 crossings

### [a10 — Dock, tack, cut: then each contact crimped alone in a keyed steel nest](ideas/a10-dock-tack-then-nest.md)

A fanned ribbon docks onto a strip segment on a steel pallet whose rail sits under the insulation barrels only, so every lance hangs free; one lever drives a notched steel comb that closes every insulation barrel loosely (a tack), and with the comb still down as the pad a shear drops the carrier past the rail edge and cuts every tab. Each contact now hangs from its own conductor one strip pitch from its neighbours, and at a heavy station a stage lowers one at a time into a keyed steel nest in a fist-sized C. There force-and-form's knee crimps the conductor barrel to a geometric bottom with a re-touch height, a separate blade re-forms the insulation barrel, the far-end port confirms which conductor is in the nest, and a blade on the box's rear face takes a 20 N pull.

- contacts: carrier strip · steel: made dies (EDM, machined, laser-cut) · meeting: pallets dock (all contacts placed at once).
- **Branch of** a2.
- **Combines:** [force-and-form/f9](../force-and-form/summary.md), [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f6](../force-and-form/summary.md), [force-and-form/f4](../force-and-form/summary.md), [change-the-question/c1b](../change-the-question/summary.md).
- **Automates:** split, strip, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Strip segments, docking and two levers per end (~55 s), moving pallets to the heavy station (14 calls a unit), far ends; ~13 attended minutes a unit plus loading and insertion [estimate].
- **Major unresolved problems:**
  - The tack's grip on silicone and whether a tack-first crimp is sound
  - Whether loosely closed insulation wings hold each contact on the rail edge through 50-160 N of tab shear
  - The nest's conductor anvil under the lance (neck t >= 0.34-0.74 mm, or a lance slot)
  - Ejecting a box from a slot with 0.05 mm clearance
  - Strip pitch, and a 21-30 mm split

### [a10b — The tacked row into the hand tool: dock and tack every contact with two levers, then crimp each in the SN-2549](ideas/a10b-tacked-row-into-the-hand-tool.md)

No motors: a ribbon end prepared on the bench blocks docks onto a strip segment (or kit contacts in a2c's keyed nest bar), and two toggle-clamp levers tack every insulation barrel and shear every tab, so each contact hangs from its own conductor at its docked depth and roll. The person then crimps each tacked contact in the bench's SN-2549, bending neighbours aside on 21-30 mm of free conductor, pulls each with a luggage scale and inserts with a hand jig. Nobody places a loose contact or feeds a wire into a captive one.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: pallets dock (all contacts placed at once) · usable without a motor.
- **Branch of** a10.
- **Combines:** [change-the-question/c1b](../change-the-question/summary.md), [force-and-form/f9](../force-and-form/summary.md), [hand-tool-as-press/a4c](../hand-tool-as-press/summary.md), [terminal-supply/a2c](../terminal-supply/summary.md).
- **Automates:** place contact on conductor.
- **What the person still does:** Preparation at the bench blocks, the two levers, every crimp, pull and insertion, far ends; contact-to-die position in the tool is still the person's eye or a clip-on stop.
- **Major unresolved problems:**
  - The tack's grip on silicone, and whether the SN-2549's insulation die re-forms a pre-closed barrel cleanly
  - Whether neighbours at 7.1 mm or 5 mm clear the SN-2549's jaw head
  - The SN-2549's crimp height on this ribbon (do its jaws bottom?)
  - The tack comb's notch profile

## Combinations with other explorers

- a9 (explorers/ribbon-as-pallet/ideas/a9-reel-end-docks.md) = procedure-is-the-machine p6 (80 mm-hub reel, hub socket, cut last) + p7 (strip the webbed end in one stroke) + p3 (puller, partner nest) + p5 (short eccentric) x ribbon-as-pallet a4 + a2e + a7 + a6 + an equal-path fan (a5 F5). Terminate at the reel clamp, dock onto reel strip, crimp through a feedless applicator with a pilot in the carrier slot, cut last. Developed from procedure-is-the-machine's X1 with three differences: a slip ring (the puller turns the reel about once per loom), grips before the dock, and the insertion V coming from the humps so the finished loom is equal-length.
- a10 (explorers/ribbon-as-pallet/ideas/a10-dock-tack-then-nest.md) = ribbon-as-pallet a2 (docking on strip) x force-and-form f9 (tack feeds heavy station) + f3 (knee, re-touch, neck blade) + f6 (separate insulation blade) + f4/f8 (steel C) x change-the-question c1b (the tack). The carrier's job ends at the tack; each contact is crimped alone in a keyed steel nest with ~11 mm of room.
- a10b = a10 with the bench's SN-2549 as the heavy station and toggle-clamp levers; converges with hand-tool-as-press a4c and machine-that-sees-and-learns v8; uses a2c's keyed nest bar for the kit contacts on hand.
- a2e = ribbon-as-pallet a2 x borrowed-machines b1b (applicator in a slow press) x procedure-is-the-machine p5 (3-4 mm eccentric), with force-and-form f3's re-touch, f6's insulation-height sweep and f8's crown as the downstream fallback.
- a1c = ribbon-as-pallet a1 x borrowed-machines b1: crimp from the upstream end with the fan flat downstream, fold each crimped conductor back.
- a1b SN-2549 variant = ribbon-as-pallet a1b seats x borrowed-machines b1 fold-back cassette x b2 SN-2549 in a frame with strip feeder.
- a2c x procedure-is-the-machine p7: pockets set back by each conductor's fan recession (5P at 5 mm: 0, 0.77, 1.65 mm) so an end stripped before the split docks without an equal-path fan, using loose kit contacts.
- a2c x change-the-question c1: a keyed nest bar at 3.4 mm, odd conductors dock with no fan, each pocket a steel anvil slide lifted into a punch.
- a3 x force-and-form f6: the IDC fold is the loom's strain relief because the insulation crimp on this silicone slips at 0.4-9 N; a3 x procedure-is-the-machine p3/p6: the fold is the reel puller's grip.
- a6 x procedure-is-the-machine p1: J4 clamped as one 7-conductor pallet with a raised crossover groove (loft) at a ~39 mm split; a6 x into-the-housing i5 real-wafer nest; a6 x Molex US 4,936,011 slide-along jaws (borrowed-machines b1).
- a6 x force-and-form f6: bend-and-look on a whole crimped row by swinging the ribbon pallet down 60-90 degrees about the insulation barrels' rear edge, which puts every B/F tip zone on the outside of the bend.
- a8b x procedure-is-the-machine p1c: at housing pitch the conductor is lifted ~9 mm into a full-size head, and a flat sole presses its residual rise level.
- a4 x procedure-is-the-machine p3/p6: the spool's inner end on a slip ring or in a hub socket as the far-end port; rewind onto an 80 mm hub radius to kill curl.
- a2b x borrowed-machines b1b (load sensing under the shoe) x force-and-form f7 (one-piece crimper plates with 5.1-5.6 mm webs at 7.1 mm pitch).

## Transferable mechanisms

- Three consistent preparation orders, and what each leaves in the finished loom: cut and strip after the fan (outer conductors stay long: a 5P from 7.1 mm keeps 2.46 mm, a 3-5 mm arc in the split); cut at the root and strip before the split with an equal-path fan (every conductor one length); or touch off and strip each conductor at its own tip.
- Equal-path fan grooves: a vertical hump in each inner groove makes every path as long as the outer one, so tips and strip lines made before the split stay on a line (4P at 7.1 mm: 3.3 mm over 16.7 mm).
- A fan closed to housing pitch leaves a natural V staircase of fronts; grip each conductor at its own front and let the outer contacts latch first instead of forcing one line (which bows 2.2-4.5 mm).
- Never react a proof pull on a side-feed contact's tab alone: the wire axis 0.95 mm above the tab pitches it at 2.5-4.6 N. Hold the barrels down with a pad and pin the carrier at every slot, or pull against a blade on the box's rear face.
- Put strip grips in the carrier's end slots and a pilot in the rectangular slot beside the anvil contact: the part's own feature is the reference at the moment of force, and the round hole under the jacket stays free.
- A feedless applicator needs only a 3-4 mm eccentric (clear the next open wings): 1.0-1.7 N m on a NEMA 17 planetary, twice the samples through compaction of a 15-20 mm crank.
- Any shelf, comb or rail a strip lies on needs a groove along X under the lance line, or support under the insulation barrels only; a flat face props every contact 7.6-15.9 degrees.
- Kinematic seats for pallets need hardened steel at every contact: balls on ball pairs or on cut case-hardened rod; unhardened stainless dowels dent at 1,050-1,700 MPa.
- Grip the segment to the carriage before docking, so strip and fan block share one X.
- Tack on the strip: close every insulation barrel loosely in one comb stroke while the carrier still holds the row, cut the tabs with the comb as pad, and every contact then travels on its own conductor to any crimp station, including a hand tool.
- Identity before force at a single-contact nest: through the far end, only conductor k may read continuous to the grounded nest.
- Flush-cut and strip after the fan, at the fan block's face, when the crimp needs the tips on a line in the fanned pose.
- Tangent-circle web: pitch equals OD, so tear-or-cut is one ratio, neck thickness over the 0.49 mm wall.
- The clamp as tear stop: a wedge-driven tear stops where the clamp holds the conductors, so the split root is the clamp's face.
- Tines that part and fan: a diverging blunt comb tears every web and leaves a housing-pitch fan that the copper keeps.
- Float each slitting blade on its own valley (V-nose on a flexure), independent of the ribbon's pitch stack.
- Score a ring, let the pull tear the rest: stop 0.15-0.25 mm short of the strands.
- Roll the work, not the tool: pads moving equal and opposite (one pinion between two racks) spin every conductor about its own axis under two fixed razors.
- Touch-off through the conductor itself: a copper face touching a grounded stop reads through the far end, giving each tip to ~0.01-0.05 mm.
- Twin blades closing together centre the conductor; partial pull then twist through the slug gathers the strands.
- Isolated blades and tines as nick detectors through a wire to every conductor (far-end pogo block or the reel's hub socket).
- A pallet-borne tongue per conductor, bumped by a fixed station cam, lays in and lifts back with no actuator on pallet or ram.
- The order of crimping as the clearance scheme: upstream end first, fan flat downstream, each finished conductor folded back.
- Dock, then crimp through a feedless applicator: its function guarantees room for an open contact one strip pitch upstream.
- The IDC strain-relief fold as grip and strain relief: a 180-degree wrap multiplies a 3 N clip to 14-69 N with no bite.
- The reel's inner end (hub socket or slip ring) as the far-end test port for a terminate-at-the-reel, cut-last machine.
- Check the insulation crimp for a silicone bulge in the window: a clone-spec insulation crimp squeezes this jacket to 70-80 % of its area.

## Key findings

- [calc F §5] Cutting and stripping after a wide fan leaves the outer conductors long in the finished loom: once closed to 2.5 mm and latched, a 5P fanned to 5 / 7.1 mm keeps 1.34 / 2.46 mm of excess, a 3-5 mm arc over a 20-30 mm split. Cutting at the root before the split and fanning with equal paths leaves none; its insertion V comes from the humps, which the clamp's push straightens at 0.06-0.23 N.
- [w3 §4; calc F §3; P3 §3] A proof pull against the carrier alone fails twice: the tab pitches at 2.5-4.6 N, and a 2.5-3 mm carrier held by end grips bows 0.2-2.7 mm. With a pad (3.8-6.3 N) and slot pins, the tab carries 20 N in compression (125 MPa, buckling >1.7 kN); a neck blade on the box's rear face takes it at ~25 MPa if the neck admits 0.3 mm.
- [w3 §5] The retention lance props any contact on a flat shelf 7.6-15.9 degrees about its tab (elastic limit ~2.3 degrees): a2's support comb, a2e's shelf and a2b's anvils each need a groove under the lance line.
- [P3 §2; calc F §4] Docking capture depends on an unmeasured reading of the clone drawings: +0.5 mm a side if the open widths are inside widths, ~0 at low tolerance if outside, -0.08 mm if JST's 1.95 mm envelope includes the wings, against 0.16 mm RSS placement error. Pressing conductors in takes ~0.5-2 N each.
- [calc F §1] The Prime dowel row is unhardened 304; 6 mm balls at 10-40 N of magnet preload load it to 1,050-1,700 MPa and dent it. Seats of 52100 ball pairs or cut case-hardened rod stay elastic.
- [P3 §5] A feedless applicator needs a 3-4 mm eccentric: 1.0-1.7 N m on a NEMA 17 + 26.85:1 planetary (Prime, 3 N m permissible) and ~40-47 HX711 samples through compaction, against 2.2-6 N m and 18-21 samples for a 15-20 mm crank. The bench's NEMA 23 and DM542T are installed in the cap-weld tube rotator.
- [P3 §4; calc F §7] Contacts per unit by arrangement: 111 (grips in spare contacts), 81 (N+2), 67 (end-slot grips, N+1), 55 (from the reel, N); the reel figure is ~145 units per 8,000 reel at $1.29 a unit. End-slot grips cut a 5P's downstream reach from 42.6 to ~32-35 mm.
- [P3 §1] Equal-path humps: 4P at 7.1 mm, 3.3 mm over 16.7 mm (bend R ~4.3); 5P centre 5.1 mm over 21.4 mm; 1.7-3.2 mm at 5 mm; under 1 mm at 2.5 mm. Groove shape sets the recession: a 5P at 2.5 mm recedes 0.31 mm with a compact S and 0.10-0.19 mm with a gentle one.
- [P3 §8] a8b's 15 mm head butts flat neighbours at 5 mm pitch unless it carries a snout <=7.8 mm reaching >=6 mm ahead; at 2.5 mm the snout would be <=2.8 mm, so the conductor is lifted into the head instead.
- [P3 §9] Off a 25 mm spool hub a 35 mm protrusion's tip stands 2.5-12.6 mm out of plane, enough to miss a nicker; a covered floor, a straightener, or an 80 mm-hub rewind (no new set) keeps it in plane.
- [P3 §7, estimate] In every docking arrangement the crimp is a small share of the person's time: a2e with hand preparation ~60 attended min a unit (person ~178 s per end, machine ~108 s), a1b ~65, today's hand procedure ~46, a1 ~20, a9 at the reel clamp ~12 with ~3.5 h alone per 4P run. Minutes fall only when nobody loads a pallet per end.
- [P3 §12] At a reel clamp a failed crimp costs the end's whole split (22-33 mm of reel), ~37 mm a unit at a 2 % failure rate, and never a loom.
- [w3 §3] Tacking on the strip at strip pitch takes one comb pass (3.55-3.85 mm of steel between notch mouths), gives a heavy station <=10.8-11.4 mm of jaw room, and with >=10 mm of free conductor no stage error reaches the tack (bending 1-3 mN, squaring roll 0.03-0.2 N mm, against a tack of 0.4-9 N).
- [unit_inventory via P3; a6] J4's and J7's crossings run between the two ribbons of a pair (J4: the 3P's GND into cavity 2 inside the 4P's 1, 3, 4, 5; J7: the 5P's GND to 7 past the 3P's 5-6), so two pallets bolted at insertion cannot make them: five crossing contacts a unit by hand, a loft at a ~39 mm split, or J7's wiring choice.
- [calc F §2] With a backshell at the split root, its top stands at the split + ~21.8 mm: 30-37 mm with fold-back parking, 43-52 mm at strip pitch, 44-55 mm for a9, 52-69 mm for a1's tongue.
- [calc W2 §3] Fan recession with a compact S: outer tips recede 0.11/0.20/0.31 mm (3P/4P/5P) at 2.5 mm, 0.76/1.20/1.65 at 5 mm, 1.32/2.05/2.77 at 7.1 mm.
- [calc W2 §9; w3 C5] A clone-spec 22 AWG insulation crimp (1.80 x 2.05 mm) squeezes this jacket to ~70-80 % of its area; force-and-form reaches the same figure separately. The bulge lands in the inspection window.
- [calc W2 §2, estimate] Web tear force is 1.5-17.5 N per web for a 0.15-0.7 mm neck; the tear should stay in the neck below t_n/wall ~0.6.

## Where this view still had trouble

- Crimping in the ribbon's own plane at housing pitch: this view never found a workable variant; every arrangement widens the pitch, splits planes, lifts, or folds conductors away.
- Short splits with docking: every docking arrangement needs 21-33 mm of split; the only shorter routes found (fold-back parking, every k-th conductor, c1's half-rows) give up one-motion placement or add docks.
- J4's and J7's crossings: no pallet-native way to cross a conductor from one ribbon into the other's cavities before crimping; the loft costs a ~39 mm split and hand laying.
- Loose kit contacts in a fully automatic path: beyond a shaker of uncertain reliability or a strip feeder, no way to present the contacts on hand in orientation without a person.
- Housing supply and orientation for mixed XHP types into the nest, and labelling, were not developed.
- Far ends (Faston, ferrule, IDC, screw terminal) are handed back everywhere except a second applicator at a4's guillotine, which was not developed.
- Everything in parting and stripping rests on unmeasured silicone behaviour (neck thickness, flank tear, tear following a score); if the web tears badly, only the plough and the laser remain, and both have their own unknowns.
- The equal-path fan block's capture of tine-fanned conductors, humps included, could not be judged without printing one.
- Control software, logging and supervision were described only as checks; the stack that runs them was not developed from this view.

## Questions for Derek

- Which split behind the housing is acceptable: 8-15 mm (fold-back parking), 17-23 mm (5 mm crimp pitch), 21-30 mm at strip pitch with a 3-5 mm arc left in the outer conductors (a2, a2e, a10), 22-33 mm with every conductor one length (a9), or 30-47 mm (a1's tongue)?
- Would you buy one Digi-Key SXH-001T-P0.6 100-piece strip ($4.71) and put it, with five kit contacts, under the caliper and the ELP camera? It settles carrier pitch, width and slot size, whether the open-wing widths leave any docking capture, and, photographed side-on, the neck between box and conductor barrel that decides a2's head, the pull blade and a10's nest anvil.
- Cut one ribbon with a fresh blade and photograph the face under the ELP camera: neck thickness, valley depth, and how far off-centre the strands sit.
- Three two-minute tests: a razor resting on a 1.45 mm drill blank across one conductor, rolled a turn, then pulled (a8); a 5P end squeezed between two razors on shims and pushed off, then a flat feeler driven into the gap it leaves (p7 and a7); three strip contacts closed loosely on three conductors with smooth pliers, tabs cut, pulled and twisted on the scale, then crimped in the SN-2549 and pulled again (a10b).
- What is the BNTECHGO spool's hub radius, can its inner end be reached, and would you rewind each spool once onto a printed 80 mm-hub reel with a hub socket (a4, a9)?
- If an OTP applicator arrives: would you hand-cycle it to see when the feed finger moves and whether the ram has a return spring, scan its upstream plates, downstream side and shear punch pocket with the Revopoint, and consider removing the feed finger, pressure plate and shear punch (a2e, a9)?
- For J7, would you move GND onto the 3P with CLO and CHI and trim the 5P's fifth conductor, which makes J7 straight for a machine? For J4, is inserting three crossing contacts a unit by hand acceptable?
- Five SN-2549 crimps on the ribbon: do the jaws bottom face to face, and what crimp height does a caliper read?
- Would a printed backshell with an IDC-style fold on every loom be welcome as strain relief and label, given 30-69 mm above the board depending on the split?
- Is a quarter to half turn of twist in each stripped stub acceptable (a8b)?
