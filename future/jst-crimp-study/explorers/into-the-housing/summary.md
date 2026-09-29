# into-the-housing

*Insertion is the dexterous step.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [i1 — Lift one conductor to a crimp head above the row, then set it into its cavity](ideas/i1-lift-to-the-head.md)

One X carriage walks the housing nest, a saddle comb (humps store feed) and the web clamp past a fixed station whose ordinary-width head sits 16-20 mm above the row: the SN-2549 in a lead-screw cradle (with i2d's stub), f3's knee press on strip, or an applicator in a crank press. A gripper on a Y-Z slide grips conductor n 2-3 mm behind the stripped edge from above and below, lifts it, and lays the tip into the captured contact with the camera's view of the insulation edge as the Y reference. The fingers go loose in X and Z for the stroke, lock for a ~20 N proof pull, re-grip on the crimped barrels, and carry the contact down into cavity n; a stencil blade finishes the last 0-1.8 mm and a 5 N pull-back tests the latch.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Combines:** [force-and-form/f1](../force-and-form/summary.md), [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f2](../force-and-form/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splitting, stripping, laying conductors over the saddles in housing order and making J4/J7 crossings by hand (unless a loft and an X axis on the gripper are added); feeding the head; loading and unloading housings.
- **Major unresolved problems:**
  - Carrying the contact to a 2.0 mm cavity (Sogang's failures were in transfer, 43/50); whether a grip 1.5-2.5 mm behind the barrels is enough
  - The head's own contact feed
  - A flexure that locks and unlocks in X and Z
  - An applicator's base may collide with a row only 16-20 mm below its anvil

### [i1b — Branch of i1: crimp in the row with narrow stepped dies, no lift](ideas/i1b-narrow-tooling-in-the-row.md)

The conductor stays in its row; a steel C beside the row holds a stepped crimper (3.1 mm conductor step, 0.8 mm walls; 2.5-2.7 mm insulation step with a chamfered neighbour-side face) coming down and an anvil lifted by a knee from below, whose shoulders catch the crimper walls so crimp height is die geometry. A contact rides up on the anvil from a lance-grooved channel plate while spreader fingers hold the neighbour wires ~0.5 mm apart, which also covers the insulation mouth's shortfall for every clone wing. After the crimp and a proof pull against a backstop on the tab stub, the anvil drops and a gripper carries the contact ~8.2 mm into its cavity.

- contacts: loose kit contacts · steel: made dies (EDM, machined, laser-cut) · meeting: die head brought to a still conductor.
- **Branch of** i1.
- **Combines:** [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f4](../force-and-form/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splitting, stripping, laying over saddles in housing order (crossings by hand), feeding contacts from below, loading and unloading housings.
- **Major unresolved problems:**
  - Custom 3.1 mm stepped dies (EDM at +/-0.05 mm is coarse for 0.8 mm walls)
  - A knee under a rising anvil carrying 1-3 kN inside a small C
  - Spreader fingers at 2.5 mm pitch that stay in through the insulation step's first touch
  - The lance condition t >= 0.34-0.74 mm

### [i2 — The housing is the locator: crimp the contact in its own cavity, then push it home (combination K1)](ideas/i2-crimp-in-the-cavity.md)

A contact slides lance-down along a lance-grooved plate box-first 1.4-2 mm into cavity n of a housing in a nest that floats in X and Z (steel is the master); an anvil rises under the barrels with its front edge behind the hanging lance and a backstop holds the tab stub. The camera-driven hump presser sets the stripped tip's Y and stays down through the stroke, the presser foot lays the conductor in, and a sprung hold-down pad in the insulation step keeps it there as a knee in a fist-sized steel C closes a stepped crimper whose walls bottom on anvil shoulders; the insulation step's chamfered outer face pushes the seated neighbour's jacket aside up to 0.33 mm if the kit's open wings are wide. The knee re-touches for crimp height, pads proof-pull ~20 N, the anvil drops 1.5 mm and a slotted stencil blade pushes the contact home while a bar cell logs fold, snap and wall, then a 5 N pull-back.

- contacts: either loose or strip · steel: made dies (EDM, machined, laser-cut) · meeting: the housing locates the contact.
- **Combines:** [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f4](../force-and-form/summary.md), [force-and-form/f8](../force-and-form/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splitting and stripping; laying conductors over saddles in housing order (J4/J7 crossings by hand, from a raised loft by a picker with X travel, or removed by a board pin-order change); loading contacts (tape of kit contacts or strip over a crowned block); loading and unloading housings.
- **Major unresolved problems:**
  - The lance condition: transition t >= 0.34-0.74 mm on the kit contact (one side photo, or a look at the SN-2549 anvil)
  - Die making: 3.1 mm stepped crimper with 0.8 mm walls bottoming on anvil shoulders
  - The insulation mouth (~2.3-2.6 mm) against open clone wings (2.46-3.25 mm): pushing the neighbour's jacket 0.33 mm aside is untested; kit wing width unmeasured
  - ~0.1 mm per side at the seated neighbour's equator for the conductor step, relying on the floating nest
  - Crimping 0.2-0.4 mm from a PA6 face; clone vs genuine transition and lance

### [i2b — Branch of i2: load every cavity first, crimp each in place, push them all home together](ideas/i2b-preload-the-whole-housing.md)

The person sets contacts ~2 mm into the odd cavities (J2's 3 stays empty), the housing goes into i2's floating nest and each is crimped with empty neighbours; then the evens are loaded and each crimped between two crimped neighbours, which the 3.1 mm conductor step clears by ~0.2 mm a side. Because nothing beside a crimped barrel can give way, pass 2 works with open kit contacts only if their wings are under ~2.2-2.5 mm (loading only up to ~2.8 mm); otherwise it runs on pre-formed contacts (k7). A laminated comb pusher drives the row to the first wall, a single finishing tine brings each contact to its own wall, and a per-cavity pull-back follows.

- contacts: loose kit contacts · steel: made dies (EDM, machined, laser-cut) · meeting: the housing locates the contact.
- **Branch of** i2.
- **Automates:** place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Pre-loading contacts into housings to the first stop in two passes; splitting, stripping, laying over saddles (crossings by hand); moving the housing out of the press between passes.
- **Major unresolved problems:**
  - Inherits i2's lance condition and die making
  - Pass-2 insulation mouth fails for most open clone wings (half-width 1.50 mm, -0.08 to -0.48 mm) with no neighbour to push aside; needs narrow kit wings or pre-formed contacts
  - Two loading passes
  - Comb pusher metalwork (0.25 mm tines reaching ~2 mm into cavities)

### [i2c — Branch of i2: a real housing cut short as a permanent crimp locator, latched by the lance](ideas/i2c-cut-down-housing-locator.md)

A sacrificial XHP cut ~3 mm from its mating face is bonded into a steel holder whose rear face is the die's front wall. A contact latches into the stub by its own lance, so the lance catch sets its axial position while the host press crimps; then a pin through the window lifts the lance (XJ-06 style) and a gripper withdraws the contact to carry it to the product housing.

- contacts: loose kit contacts · steel: any of several · meeting: the housing locates the contact.
- **Branch of** i2.
- **Automates:** crimp.
- **What the person still does:** The transfer to the product housing (another arrangement's job); ribbon presentation as in the host press.
- **Major unresolved problems:**
  - Three lance folds before the product housing, each partly plastic; retention afterwards unknown
  - The transfer back into a cavity reintroduces the dexterous step
  - Cut-plane tolerance and PA6 shoulder wear

### [i2d — Branch of i2c: a locator the lance never touches (housing stub cut short, or a steel pocket on a post), first on the SN-2549 by hand](ideas/i2d-locator-the-lance-never-touches.md)

A kit XHP-2 cut to its front wall plus 1.0-1.5 mm of cavity, with a foil shim on its floor, rides a printed parallelogram flexure (free in X and Z, stiff in roll) clipped to the SN-2549's lower jaw; in Y a 10-30 N spring holds it back on an adjusting screw 1.0-1.7 mm ahead of the anvil. Derek slides a loose kit contact forward in the XH nest until the box nose stops on the stub's front wall (the product's own +Y stop), the lance hanging free; one click captures it, he feeds the conductor and squeezes, and the carrier yields a few hundredths to the barrel's growth instead of bowing the transition. The same stub is the seat of a motorised cradle (K5), the box-keyed clip for c6b's snapped flags, and has a steel twin whose wired 0.64 mm post reads 'this conductor is in this contact' before the crimp.

- contacts: loose kit contacts · steel: SN-2549 or similar hand-tool dies · meeting: the housing locates the contact · usable without a motor.
- **Branch of** i2c.
- **Combines:** [force-and-form/f1](../force-and-form/summary.md), [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [change-the-question/c6b](../change-the-question/summary.md).
- **Automates:** crimp.
- **What the person still does:** By hand: placing each contact against the stop, feeding the conductor, squeezing. In a cradle: dropping contacts into the flap or a stick, presenting the ribbon.
- **Major unresolved problems:**
  - Stub depth: lance length and root unmeasured; found by trial with stubs at 0.2 mm steps
  - Whether the SN-2549's jaws leave room for a stub 1.0-1.7 mm ahead of the anvil, and whether its open nest passes a flag's box and lance (2.8-3.25 mm)
  - Stub floor to anvil height match before capture
  - Conductor-barrel growth (0.03-0.11 mm estimated) and whether the preloaded stop is needed
  - Nose vs box shoulder as the axial reference; post grip of kit contacts (steel twin)

### [i3 — Crimp at a wide pitch on shuttles, close them to 2.5 mm, push the housing onto the whole row](ideas/i3-converging-shuttles-gang-push.md)

Each conductor sits in a thin shuttle clamp on rods; a fan plate spreads them to 5 mm pitch and the base walks them past a fixed head (f3's knee press on strip, the SN-2549 in a cradle with i2d's stub, or an applicator). Each shuttle docks on the head's steel pin during its crimp and is proof-pulled before closing. The fan plate closes the row to 2.5 mm, a sprung guide comb squares the noses, the housing nest drives onto all contacts to the first wall through a bar cell, each remaining contact is finished alone, and per-shuttle 5 N pull-backs test the latches.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Combines:** [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f5](../force-and-form/summary.md), [hand-tool-as-press/a2](../hand-tool-as-press/summary.md), [hand-tool-as-press/a3](../hand-tool-as-press/summary.md), [hand-tool-as-press/a4](../hand-tool-as-press/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Splitting (23-36 mm on J1), stripping, laying conductors into shuttles in housing order and making the J4/J7 crossings, loading strip or contacts for the head, loading and unloading housings.
- **Major unresolved problems:**
  - Split length on J1
  - Guide-comb retreat timing
  - Jam recovery on a nine-contact push; contact length spread
  - Shuttles on rods keep their order, so crossings stay with the person (i6 or a board pin order removes them)

### [i3b — Branch of i3: stagger the row on constant-force clamps so one push seats contacts one after another, each reported](ideas/i3b-staggered-row-one-push.md)

Shuttle clamps sit 0.3-1 mm apart in Y on constant-force springs preloaded to 1.25 x the largest single insertion force (~12 N at the KONNRA clone's 9.8 N, 31 % of pull-out). As the housing advances, each contact folds, snaps and bottoms at a known housing position and rides its clamp back at constant force; the load-cell trace shows N separate steps and printed flags watched by camera confirm each. The same springs absorb contact length spread.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module).
- **Branch of** i3.
- **Combines:** [force-and-form/f5](../force-and-form/summary.md).
- **Automates:** insert, verify insertion and pin order.
- **What the person still does:** As i3.
- **Major unresolved problems:**
  - The stagger reintroduces stored feed (0.1-0.5 mm ride-back is a 0.9-2.4 mm bow)
  - Spring and flag packaging at 2.5 mm pitch (flat coils are wider than the pitch)
  - Whether single insertion is <= ~12-15 N (Derek's scale)

### [i4 — A slow gantry hand with a camera and a force wrist that operates the crimper and inserts](ideas/i4-gantry-hand-with-eyes.md)

A 3018-class gantry carries a two-finger hand with a lockable Hall-sensed wrist flexure and a small camera; a contact tray (or f3's strip), a capture-first crimp station (f3, or the SN-2549 cradle with i2d's stub), a loft holding the split conductors in ribbon order ~8-10 mm above the insertion plane, and a housing nest are bolted in reach. The station captures the contact, the hand threads conductor n axially into it, goes loose for the stroke, proof-pulls, re-grips on the barrels, photographs the contact, and inserts with lean-and-slide and a 5 N pull-back. Because waiting conductors stay in the loft above placed ones, any pin map is a list of moves.

- contacts: either loose or strip · steel: any of several · meeting: a general-purpose arm or gantry hand.
- **Combines:** [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f1](../force-and-form/summary.md), [hand-tool-as-press/a3](../hand-tool-as-press/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Filling the contact tray or loading strip, laying the ribbon into the loft in ribbon order, loading and unloading housings, clearing jams the hand reports.
- **Major unresolved problems:**
  - Grip design at 2.5 mm pitch for contact pick and wire push
  - Silicone springback after release
  - Time to make vision corrections dependable
  - A lockable wrist flexure
  - The loft still needs a hump for ~6.7 mm of the ~8 mm insertion feed

### [i5 — The person starts each contact; a lever nest seats it, checks the cavity and tests the latch (with a proof-pull fork and crimp-height pocket: K4)](ideas/i5-person-inserts-on-a-sensing-nest.md)

A PCB of real B4B-B9B XH headers on a 5 kg bar cell, each post an ESP32 input, with a spring-limited lever blade on a detented carriage and a screen showing the next cavity; beside it a steel proof-pull fork on a second cell and a crimp-height pocket under a 0.001 mm indicator log every hand crimp's proof load and height before insertion. With the loom's far end in a terminal block, the ESP32 drives conductor k and the post that sees it names the cavity, so the record pairs conductor with cavity; the lever seats the contact, and a 5 N tug with a blade re-touch proves the latch. No motor is needed.

- contacts: not applicable · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes · usable without a motor.
- **Combines:** [hand-tool-as-press/a1](../hand-tool-as-press/summary.md).
- **Automates:** verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Crimping by hand on the SN-2549 (with i2d's stub), dropping each crimp in the fork and pocket, starting every contact ~2 mm into its lit cavity, J4/J7 crossings by hand.
- **Major unresolved problems:**
  - Post grip (~0.5-2 N estimated) against the latch in the tug test
  - Added mating force when inserting onto a header; one extra mating cycle per contact
  - Whether each loom's far end is free for the terminal block while its board end is made
  - Header shroud wear over ~600 cycles

### [i6 — Sort, then push: crimped contacts wait in ribbon order, a carrier lowers each into its housing slot, the housing is pushed onto the row](ideas/i6-sort-then-push.md)

The web clamp and a root comb hold a crimped ribbon end (or a pair) with its conductors cantilevered in a staging plane in ribbon order. A carrier on a small X-Y-Z stage grips each crimped contact by its barrels and lowers it 8-10 mm into a target comb of under-width U-slots at 2.5 mm in housing order, lower layer first and from the housing centre outward, setting every rear on one line; J4's 3V3 and GND and J7's GND go last and lie over the rest to the housing's end. A stencil-steel backing blade whose tines follow into the cavity mouths drops behind all barrels, the housing is pushed onto the row to the first wall, a single finishing tine brings each contact to its own wall (lengths differ), and each wire is pulled back at 5 N.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module).
- **Automates:** insert, verify insertion and pin order.
- **What the person still does:** Bringing the crimped ribbon end into the root comb in ribbon order (or it arrives from k6, k8 or terminal-supply x2), loading a housing, lifting the finished end out, labelling J4/J7. The proof pull runs upstream at the crimp station.
- **Major unresolved problems:**
  - Gripping a 0.043 g crimped contact by its barrels and releasing without roll (terminal-supply's a6 post head is another grip)
  - Gang-push risks carried from i3 (guide-comb timing, jam recovery)
  - Needs the crimp step to leave the end in a staging plane
  - Split of ~25-30 mm during the build, a set step of 8-10 mm and bows up to ~2.9 mm on J4/J7
  - Ribbon identity: marked edge or far-end electrode block

### [i6b — Branch of i6: the target is a bed of long 0.64 mm posts standing through the housing](ideas/i6b-post-bed-through-the-housing.md)

A PCB drilled at 2.50 mm carries 0.64 mm pins through every cavity of the housing from the mating face, standing ~8.5 mm out of its rear face, each wired to an ESP32 with the loom's far end in a terminal block; a slotted stencil-steel support comb holds the posts 3 mm below their tips, since unsupported they are free ~15.6 mm and deflect 0.45-0.9 mm per N. The carrier threads each crimped contact's box 1-2 mm onto its post tip in i6's order, and continuity proves the right conductor is on the right post before anything latches. The comb withdraws, the housing slides ~13-15 mm back along the posts over every box against a backing blade to the first wall, a finishing tine seats each, and the posts read continuity and shorts.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module).
- **Branch of** i6.
- **Combines:** [terminal-supply/a4](../terminal-supply/summary.md), [terminal-supply/a4b](../terminal-supply/summary.md), [hand-tool-as-press/a1](../hand-tool-as-press/summary.md).
- **Automates:** insert, verify insertion and pin order.
- **What the person still does:** As i6: bringing the crimped end, loading a housing onto the posts, lifting the finished end off, labelling.
- **Major unresolved problems:**
  - Whether a kit cavity is clear along the post line (one header pin through one housing)
  - Threading each box onto a post tip (+/-0.2 mm capture) 53 times a unit
  - One extra partial mating cycle per contact
  - Whether the housing's post openings pass a whole XHP-9's posts drilled at +/-0.075 mm before the comb aligns them; box grip on round music wire if used

### [k6 — Combination (force-and-form f4 + i6): the travelling head crimps each still conductor while a carrier holds it, then the carrier sorts and the housing is pushed on](ideas/k6-one-gantry-crimps-in-the-fan-then-sorts.md)

The person lays a split, stripped end into a root comb that fans it to 5 mm in ribbon order, conductors cantilevered in the staging plane. For each conductor the carrier closes 3.5-5 mm behind the stripped edge, f4's fist-sized steel C on a light gantry picks a captured contact from the strip dispenser and threads it onto the still conductor by camera, the carrier goes loose in X and Z while the knee crimps and re-touches for height, then proof-pulls ~20 N against the closed head. After every conductor is crimped, the carrier sorts them into i6's target row, and the housing is pushed on to the first wall and each contact finished. Variants: K1's narrow dies at 2.5 mm (needs pre-formed contacts beside crimped neighbours) and threading through a c6 closed ring.

- contacts: carrier strip · steel: any of several · meeting: die head brought to a still conductor.
- **Combines:** [force-and-form/f4](../force-and-form/summary.md), [change-the-question/c6](../change-the-question/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Laying each split, stripped, lightly twisted ribbon end into the root comb; loading strip into the dispenser; loading and unloading housings; labelling.
- **Major unresolved problems:**
  - f4's open problems: nose under ~6 mm, gantry repeatability, die supply, threading 60 strands without fold-back
  - i6's open problems: barrel grip, gang push, ribbon identity
  - Two positioners
  - Splay to 5 mm needs 23-36 mm of split on J1; the 2.5 mm variant needs custom dies and pre-formed contacts

### [k7 — Combination (change-the-question c6 + i2/K1): pre-formed contacts, snapped onto the conductor and crimped in their own cavity](ideas/k7-pre-formed-contacts-crimped-in-the-cavity.md)

A palm-sized pre-former (servo lever or toggle clamp, its jaw a second EDM cut of the press's insulation-step profile) closes each kit contact's insulation wings around a 1.55-1.60 mm pin into a keyhole 1.96-2.14 mm wide, and pushes it into a loom-order stick. At K1's press an escapement singles the lead contact onto the channel plate and a finger slides it 1.4-2 mm into cavity n; the hump presser sets the tip's Y and stays down, and a two-tine presser foot snaps the jacket through the keyhole's throat (0.5-20 N into the anvil) and lays the strands in the open U. The knee then crimps with the conductor flare centring the contact and the insulation mouth swallowing a keyhole narrower than itself, followed by re-touch height, a 20 N proof pull, the push home and the pull-back. Branches: two passes on pre-formed contacts (i2b), strip through an in-line pre-former, and T4 spool runs with c5.

- contacts: pre-formed contacts · steel: made dies (EDM, machined, laser-cut) · meeting: the housing locates the contact.
- **Combines:** [change-the-question/c6](../change-the-question/summary.md), [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f4](../force-and-form/summary.md), [force-and-form/f8](../force-and-form/summary.md), [change-the-question/c5](../change-the-question/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Pre-forming at the lever in bulk (5-9 min a unit) or feeding a servo pre-former; dropping sticks into the feed; splitting and stripping each ribbon end and laying it over the saddles in housing order (crossings by hand or loft picker); loading and unloading housings.
- **Major unresolved problems:**
  - The insulation crimp over a pre-curl on 1.7 mm silicone (sectioning and pull tests)
  - Snap force (0.5-20 N) and bore grip (0.2-4 N) on real kit contacts
  - The press's dies: 0.8 mm walls by EDM at +/-0.05 mm
  - The transition t (lance condition); crimping 0.2-0.4 mm from PA6
  - Whether the pre-form is needed for the mouth at all (kit wings <= ~2.3 mm)

### [k8 — Combination (change-the-question c1c + i6): half-rows crimped where they lie in pallets, sorted into one row, housing pushed on](ideas/k8-half-rows-crimped-then-sorted.md)

c1c's machine splits the ribbon end into two planes, snaps pre-formed contacts onto a half-row at 3.4 mm in pallet A, crimps each under a fixed steel-C press as the X slide steps, proof-pulls it on its pocket's rear shoulder, parks pallet A up and back over the root, then does row B. i6's carrier lifts each crimped contact out of its pocket (top pad on the lobes, bottom pad through the anvil window) and places row B, then row A (which swings down from above, never through the sorted conductors), upper layer last, into a 2.5 mm target comb. The backing blade drops, the housing is pushed on to the first wall, a finishing tine seats each contact, and a pull-back or post bed checks them; no crossing is made by hand.

- contacts: pre-formed contacts · steel: any of several · meeting: conductor brought to a fixed die.
- **Combines:** [change-the-question/c1c](../change-the-question/summary.md), [change-the-question/c6](../change-the-question/summary.md).
- **Automates:** split, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Keeping pre-formed sticks (or strip) and housings stocked; laying each ribbon end in the clamp; lifting finished ends out.
- **Major unresolved problems:**
  - The lower pad through an anvil-sized window (~1.2-1.5 mm)
  - Room above the root for pallet A to park up and back beside the fixed press
  - Two pallets, swing arms and a sort stage on one slide
  - c1c's open problems: the final crimp over the pre-form or tack, ~0.5 mm carrier walls
  - i6's open problems: gang push and ribbon identity

## Combinations with other explorers

- K1 = into-the-housing i2 + force-and-form f3 (knee) and f4 (closed steel C): the cavity as locator, floating nest, stepped dies bottoming on anvil shoulders; i2's file is K1 as it stands, force-and-form's f8 develops it from their side
- K2 = i3 + force-and-form f3 + i2's crowned block: shuttles dock on a strip-fed knee press at 5 mm pitch, the unused strip dropped 3.6-4 mm by a crown (in i3's file)
- K3 = force-and-form f5 (die cassette in the 12-ton press) + i3 (fan plate, gang push) for the 4P family (in i3's file)
- K4 = i5 sensing header nest + force-and-form's proof-pull fork and 0.001 mm crimp-height pocket: a motorless bench that logs every hand crimp before insertion (in i5's file)
- K5 = i2d housing stub (preloaded in Y, floor-shimmed) + force-and-form f1 / hand-tool-as-press a1 (SN-2549 in a lead-screw cradle): the stub is the flap's seat for loose kit contacts (in i2d's file)
- k6 = force-and-form f4 (travelling steel-C head threads a captured contact onto a still conductor) + i6 (carrier sorts, gang push); variants with K1's narrow dies on pre-formed strip and with c6's closed ring (own file)
- k7 = change-the-question c6 (keyhole pre-form, snap) + i2/K1: pre-formed kit contacts from sticks, snapped and crimped in their own cavity; branches for two passes (with i2b), strip through an in-line pre-former, and T4 spool runs (with c5) (own file)
- k8 = change-the-question c1c (half-rows crimped in pallets under a fixed press) + i6 (sort into one row, housing pushed on): pallet A parked up and back, row B sorted first, upper layer last (own file)
- i6b = i6 + terminal-supply a4/a4b (post-held contacts, post through the cavity) + the wired header of C6: posts through every cavity, held by a support comb near the tips, prove pin order before the latch (own file)
- c6b flag route + i2d: the housing stub is the box-keyed clip for snapped flags on the SN-2549 (in i2d's file)
- change-the-question c2 + K1/i5: JST's ASXHSXH22K305 factory lead as the die target and reference insertion trace (in i2 and i5)
- C3 = hand-tool-as-press a1 far-end terminal block + i5 header nest: the ESP32 drives conductor k and the post names the cavity (in i5)
- C6 = wired header behind the housing during i3's gang push + far-end block: each box's arrival logged within one push (in i3; extended by i6b)
- C1/C2/C4/C5 with hand-tool-as-press (a3 travelling tool, a2 head as shuttle carrier, a4 SN jaws in a die set, a4's C-frame cutting i1's lift to 5-7 mm) (in i3 and i1)
- i1 + i6: the gripper places, holds and proof-pulls, then hands the contact to i6's target row (in i1)
- i4 + i6b: the gantry hand threads contacts onto the post bed (in i4)
- Developed by terminal-supply from this explorer's proposals: x2 (a2d crown station + i6 sort with a6's post head as carrier), x3 (a5 staging + i2b two passes + i2's dies), a4c (bare contacts crimped on i6b's post bed, one push)

## Transferable mechanisms

- A crossing is an order of placement: wait high, place low, lower layers first, centre outward; any pin map can be placed one conductor at a time without trapping
- Pin-map layering: the fewest layers is the longest run of conductors whose pins decrease in web order; one 4P order (V5, IO25, 3V3, IO26 | GND, IO27, IO23) is least-crossing for both one-plane sorts and half-row machines
- The insulation-mouth rule for any narrow crimper at 2.5 mm: outer half-width = s/2 + capture margin + wall land must fit beside the neighbour; a soft neighbour's jacket can be pushed aside by a chamfered, polished outer face (0.1-0.33 mm for 0.05-1.9 N), a crimped barrel cannot
- Pre-form the part away from the wire, and take the pre-form profile from the tool: the pre-former's jaw is a second cut of the crimper's own EDM profile, stopped at the pin
- Front stops that give way: hold the contact's nose with a 10-30 N preload against an adjusting screw so the person's push never moves it but conductor-barrel growth during coining can (6-18 MPa on PA6 instead of a bowed transition)
- A foil shim on a locator's floor leaving 0.05-0.10 mm of height clearance limits box roll to +/-1.5-3.1 deg whatever the width clearance
- Hold Y from outside the dies' footprint: a camera-set hump presser stays down through the stroke, and a sprung hold-down pad inside the insulation step takes Z once the presser foot leaves
- Push a gang to the first wall, then finish each contact alone with one slotted tine and a force ceiling, because contact lengths differ; or constant-force tines at 1.25 x single insertion
- Support comb near post tips: a slotted stencil comb 3 mm below the tips makes a post bed stiff and pin material irrelevant, then withdraws before the push
- Backing blades and finishing tines must follow up to ~2 mm into the cavity: a seated rear lies 0-1.8 mm inside the rear face
- Housing stub cut to the front wall plus 1.0-1.5 mm of cavity: a molded, cents-cheap locator (or pre-former nest) whose lance never folds
- Steel pocket with a wired 0.64 mm post: holds a contact by its own spring and, with the far end on a terminal block, reads 'this conductor is in this contact' before the crimp
- Escapement one position upstream of the working station so a nose-to-tail stick never puts the next contact inside the crimper's footprint
- Park a moving pallet on the side away from where finished work lies, so its swing never sweeps placed conductors
- Parallelogram flexure under a plastic locator so steel stays the master in X and Z; floating housing nest located only in Y
- Fingers or wrist that lock for carrying and go loose in X and Z for the forming stroke
- Force ladder ordering: proof pull ~20 N between crimp and insertion, latch tug <= 5 N after
- Web clamp as the single datum and the feed-length rule: one-at-a-time insertion stores its travel as length; a gang push stores none
- Real XH header or post bed as nest and tester, with a far-end terminal block driving each conductor so posts name the cavity
- Force-vs-travel at a crawl with a $4-10 bar cell to see lance fold, snap and wall; pull-back < 0.2 mm at 5 N as the latch test

## Key findings

- [calc: explorers/into-the-housing/calc/wave3.out.txt A] The insulation step of any crimper narrow enough to pass a neighbour at 2.5 mm has a mouth of only ~2.3-2.6 mm, while clone open wings are 2.46-3.25 mm. Beside a seated neighbour's jacket (half-width 1.65 mm) pushing the jacket 0.10-0.33 mm aside costs 0.05-1.9 N and lets every clone spread fit (untested). Beside crimped barrels (i2b pass 2, k6 at 2.5 mm; half-width 1.50 mm) nothing gives way: open clone wings are -0.08 to -0.48 mm short, pre-formed keyholes fit with +0.08 to +0.37 mm
- [calc wave3 A, i1b] i1b's spreader fingers already open ~0.5 mm between neighbour jackets, more than the widest clone wing's 0.33 mm shortfall
- [calc wave3 B] If i2's hump presser lifted before the crimp, the hump's elastic share could push the tip back with up to 0.4-5.7 N (10-20 mm hump), more than an open U holds and more than the low end of a keyhole's 0.2-4 N bore grip; it works 5-15 mm behind the dies, so it stays down through the stroke and a sprung hold-down pad takes Z
- [calc wave3 C] A rigid nose stop fights conductor-barrel growth (0.03-0.11 mm, estimated): PA6 dents, steel bows the transition. A 10-30 N preloaded stop keeps the reference exact under a 1-2 N push and gives way at 6-18 MPa on PA6, carrying at most 30 N through a transition that yields at ~90-310 N
- [calc wave3 D] Clone boxes (1.85-1.90 x 2.2-2.35) roll up to +/-6.5 deg in a 2.00-2.10 mm cavity, above the 5 deg low end of the window; a floor shim leaving 0.05-0.10 mm of height clearance limits roll to +/-1.5-3.1 deg
- [calc wave3 E] With clone lengths 5.8-6.73 mm (each +/-0.25), a rigid backing blade bottoms the longest contact first; pushing to the first wall and finishing each contact with one tine avoids both stalls and crushing; constant-force tines put 49-75 N (XHP-4) to 110-169 N (XHP-9) on the nest and store 0.1-0.5 mm ride-back as 0.9-2.4 mm bows
- [calc wave3 F] A post in i6b's bed is supported only at the front wall unless something holds it: free ~15.6 mm, 0.45 mm per N in steel and 0.9 in bronze, useless against a +/-0.2 mm capture. A support comb 3 mm below the tips gives 0.003-0.006 mm per N. 2.54 against 2.50 mm over an XHP-9 is 0.32 mm end to end (+/-0.16 centred)
- [calc wave3 G] At the Shore 50-70A silicone range (E 2.5-5.5 MPa), an under-width target slot holds 1.4-20 N and the jacket takes 33-52 % of a grip-to-anvil mismatch over 2 mm and 13-24 % over 3 mm; no conclusion changes
- [calc wave3 H] A seated contact's rear lies 0-1.8 mm inside the rear face (HDGC 5.8-0.25 to CJT 6.73+0.25 mm, front wall 0.4-0.8 mm), so pushers and backing-blade tines must follow up to ~2 mm into the cavity
- [calc wave3 I] In k8, a pallet parked up and back reaches the working plane without sweeping sorted conductors; shallow carriers clear them when the drop is >= ~6 mm and the pallet sits beyond 0.36-0.53 of the span. Parked down and back its arc crosses them
- [calc wave3 J] A pre-formed keyhole (1.96-2.14 mm) loads between crimped odds with +0.43 to +0.52 mm; open clone wings leave -0.12 to +0.27 mm. Its top stands ~2.0 mm above the floor's underside against 1.50-1.60 for the conductor wings, so the conductor flare centres the contact first. The snap lands 1.7-3.5 mm behind the anvil's front edge, never on the lance
- [calc wave2 A; change-the-question w3 §9] Every loom is one layer except J4 and J7. J4 laid V5, IO25, 3V3, IO26 | GND, IO27, IO23 is two layers for a sort and (2 off-parity, 2 crossings) for half-rows. Board orders J4 = 3V3, IO26, V5, IO25, GND, IO27, IO23 and J7 = RB1-RB4, GND, CLO, CHI make every loom straight; J7 can also be straightened by moving GND onto the 3P
- [calc wave2 G] The lance condition t >= lance tip + 0.1 - box (0.34-0.74 mm) governs every flat anvil holding the box with the lance free, including the SN-2549 today
- [calc wave2 C] Waiting conductors staged h above placed ones clear at a crossing when h >= 2.0/f; lower layer first from the housing centre outward, 8-10 mm covers every loom at either staging pitch
- [force-and-form calc section 7, accepted] Force ladder: 5 N latch test < 14.7 N retention (analog; KONNRA clone >= 19.6 N) < 19.6 N proof pull < 39.2 N JST pull-out, so the proof pull precedes insertion; in i6 it belongs at the crimp station because J4 leaves only ~7-8 mm of uncrossed wire next to the target comb
- [sourcing/amazon-prime.md] Prime-confirmed parts now cited: Iverntech Tr8x2 NEMA 17 ($27.99), MGN9 rail ($16.12), MG90S 4-pack ($13.88), ShangHJ 5 kg cells with HX711 ($9.99), Clockwise Tools DITR-0105 0.001 mm indicator with RS232 ($52.99, cable not on Prime), Hotop feeler set ($8.99), POWERTEC 305CM toggle clamps ($18.25), Accusize pin gauges to 1.52 mm, uxcell 25 mm headers (pin section unstated), K&S 0.025 in music wire, Wago 221-415; no Prime 20 kg bar cell, 3 mm ground rod or constant-force spring was found

## Where this view still had trouble

- A narrow crimper at 2.5 mm beside already-crimped neighbours using the kit's open contacts as they come: no variant found once both neighbours are bronze barrels (the mouth is 0.08-0.48 mm short and nothing can give way), short of pre-forming or genuine narrow-winged contacts
- A one-pass preload of a whole housing that is then crimped in place: the conductor step still misses by up to 0.23 mm beside an open conductor-barrel neighbour, even with pre-formed insulation barrels
- Automated split and strip ahead of the insertion arrangements: every idea here except k8 (via c1c's split jaws) still receives the ribbon end split and stripped by the person or another explorer's station
- Loading ribbon ends unattended: in every arrangement the person lays 14 ends per unit into a clamp, comb or loft; a spool-fed variant exists only for T4 runs in k7 and still lacks unattended split, strip and hump-forming
- Gripping a crimped contact by its barrels and releasing it without roll: the crimp's lobed top is unmeasured, so i6, i1, i4 and k8's grips remain drawn, not designed
- Crossings in fixed-level machines (shuttles on rods, fixed combs) without a sort stage or a board pin-order change
- Automated rework of a seated contact (extraction through the window, XJ-06 style) after a failed latch or wrong cavity was not developed
- Automating J4 and J7 crossings while keeping the finished split short (under ~10 mm): every automated crossing route here needs a 25-30 mm split during the build
- Conductor identity without a free far end or a visible marked edge
- Jam recovery in a gang push beyond stop, back off and look

## Questions for Derek

- One side photo of a kit contact under the ELP camera: lance root, lance tip, box rear, conductor-barrel front. It settles the lance condition (i2, k7, i2d), the stub depth, and nose vs box shoulder as the axial reference
- Caliper the open insulation-wing width of three kit contacts. At <= ~2.3 mm a narrow crimper swallows them as they come; wider, K1 needs the neighbour pushed aside or pre-formed contacts, and i2b and k6's 2.5 mm variant need pre-formed contacts
- The SN-2549: is its XH anvil a plain block where the lance hangs, or slotted or stepped? At one click, does the lance tip hang ahead of the anvil's front face, and by how much? Held closed against a light, are the jaw faces flush with the anvil's front edge? Fully open, is the gap at the XH nest wider than 2.8-3.25 mm?
- Growth test: five SN-2549 crimps with the box nose touching a feeler leaf held across the front of the nest and five with the nose free, photographed side-on. Does the transition bow?
- How long a split behind the housing is acceptable on a finished loom? i6, k6 and k8 want ~25-30 mm during the build on J4 and J7; 5 mm crimp pitch wants 23-36 mm on J1
- Fix J4's 4P order as V5, IO25, 3V3, IO26 | GND, IO27, IO23 in cable-assemblies.md? It is least-crossing for the sort and for half-rows alike
- J7: which 3P conductor is 'third' (beside the 5P or the far one), and does the 5P follow the reed column with GND at one edge?
- Would a board revision of J4's (and J7's) pin order, making every loom straight across, be on the table? Or the J7 rewire that moves GND onto the 3P?
- On the 0.1 g scale: the push force at the click, the tug that pulls a latched contact out, and how far inside the rear face a latched contact's rear sits
- Five kit contacts from one bag, overall length by caliper: the spread decides how much the finishing tine does
- Push a long header pin through an XHP-4 from the front post opening: does it come out the rear cleanly? (i6b)
- Caliper the closed insulation barrel of an SN-2549 crimp on the ribbon and of one JST ASXHSXH22K305 lead: width and height against 1.95 x 2.4 mm
- Is the ribbon's marked edge visible to a camera, or is each loom's far end free to sit in a terminal block while its board end is made?
- Is one extra mating cycle per contact acceptable (i5's header nest, i6b's posts)?
- Keep crimping with the SN-2549 (i1, i2d, i3, i4, i5) or make narrow stepped dies (i1b, i2, i2b, k7)?
