# hand-tool-as-press

*The crimp tool is already the machine.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [a1 — The squeezer: the bench's SN-2549 in a printed cradle, closed by a slow actuator](ideas/a1-squeezer-cradle.md)

The SN-2549 lies on its side in a printed cradle, lower handle strapped down, and a NEMA 17 Tr8x2 pusher (or a worm winch on a cord) closes the upper handle through a load cell while the station ESP32 runs each squeeze whole and logs force against travel. A printed locator plate on the lower jaw's M4 screw carries a front stop and a 0.10 mm steel blade, insulated on its front face, that drops into the contact's neck; with the ribbon's far end in a push-in block, strands on the contact read amber and strands at the blade read green. The person places the contact and feeds the conductor against these stops; a printed ramp lifts the crimp off the anvil before it is drawn back.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes · usable without a motor.
- **Combines:** [terminal-supply/a2c](../terminal-supply/summary.md).
- **Automates:** crimp, verify crimp.
- **What the person still does:** Cut, split and strip (strip length set from one measured contact of the lot); placing the contact and feeding the conductor; lifting and drawing the crimp out; proof pull and fit check at a6's jigs; housing insertion; label.
- **Major unresolved problems:**
  - Neck length on a kit contact is unmeasured (0.2-0.5 mm is a reading, not a measurement); a blade plus brush needs >= ~0.3 mm, otherwise a pilot pin (strip) or a camera line
  - Where the first ratchet tooth falls relative to 'contact held, wire still enters'
  - Which SN nest crimps this 22 AWG silicone well, its crimp height, and whether its insulation crimp fits the cavity
  - Whether the SN-2549's dies bottom face to face

### [a1b — Pawl out: the tool as a plain linkage, closure owned by the station MCU](ideas/a1b-pawl-out.md)

a1's cradle with the SN-2549's ratchet pawl removed, or held off by a servo on the release lug. The pusher holds wherever the controller says, backs out if continuity never comes, and crimps to a force wall enforced sample by sample on the ESP32, or stops at a taught grip position short of die contact. A write-ahead journal names any squeeze cut off by a power loss; the crimp leaves through a6's keyhole gauge, and the proof pull is taken at a backed plate, never in the tool. The same settable stop makes it a crimp-height sweep press, the motorised pre-former for a6b, and change-the-question c3's fold station.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes.
- **Branch of** a1.
- **Combines:** [machine-that-sees-and-learns/v3](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v7](../machine-that-sees-and-learns/summary.md), [change-the-question/c3](../change-the-question/summary.md), [change-the-question/c2](../change-the-question/summary.md).
- **Automates:** crimp, verify crimp.
- **What the person still does:** As a1, including the proof pull, which is taken at a6's pull jig or a2's pull slot.
- **Major unresolved problems:**
  - Inside the tool the software is the whole guarantee; an under-compacted crimp that still fits is caught only by the force curve
  - Removing the pawl from a riveted tool is an unknown teardown; the release-lug servo is the alternative if the lug holds the pawl off
  - Stopping short of die contact makes crimp height depend on handle stiffness and wear over ~3,200 crimps
  - Handle stiffness is unmeasured; it sets the overshoot past the wall between samples

### [a2 — The ribbon comes to a fixed tool: a carriage loads contact and conductor into a1's squeezer](ideas/a2-ribbon-to-fixed-tool.md)

a1's squeezer is bolted to a baseplate beside a magazine of genuine SXH carrier stubs. A three-axis head (short rails, or a bed-slinger printer) clamps a ribbon end, fetches a stub by a pin in its pilot hole, carries the contact in 1 mm above the anvil and sets it down; the tool closes to hold and a servo blade shears the tab down the die's rear face before any wire arrives. The fork stands conductor k out of the row by the jaw-half depth plus 2.7 mm, a backlit picture of its tip corrects its axis, and Y feeds it until green or a set distance from a grounded tip plate. The tool crimps; the crimp is lifted, drawn out and proof-pulled at a backed slot, ~90-100 s a crimp.

- contacts: carrier strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die.
- **Combines:** [machine-that-sees-and-learns/v1](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v1b](../machine-that-sees-and-learns/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cut to length; split 25-35 mm; strip (unless a2c); load stubs; clamp ribbon ends and pick the loom; answer parked conductors; housing insertion (unless a2d); label.
- **Major unresolved problems:**
  - The side-entry jaw law: stand-out a + 2.7 mm = 8.7-14.7 mm sets the strands (root radius 9-47 mm); the jaw-half depth a is unmeasured
  - Carrier stub geometry (pitch, pilot hole, tab) until a strip is measured
  - An open jaw gap of ~4.5-5 mm is needed to carry the contact in clear of the anvil
  - Tab stub length left by the rear-face shear
  - The pull slot needs a 0.35-0.5 mm neck for a flat plate, or a stepped plate

### [a2b — Gravity: the tool lies flat, loose contacts drop into the nest, the ribbon hangs into them](ideas/a2b-gravity-tool-flat.md)

The SN-2549 lies flat on a stand with its nest axis vertical, with a1's pusher and insulated blade. A hand-filled revolver disc, or a loom-order stick of pre-formed contacts, drops one loose kit contact per crimp down a chute whose tongue carries the lance clear between the open jaws onto a stop pocket; a camera measures each contact before loading so the chute fits the lot. The ribbon hangs from an X-Z carriage; a fork and a close U-guide set conductor k's line, and Z lowers it to amber, then green, before the crimp, which moves sideways off the anvil before rising out.

- contacts: loose kit contacts · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die.
- **Branch of** a2.
- **Combines:** [machine-that-sees-and-learns/v4](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v4b](../machine-that-sees-and-learns/summary.md), [into-the-housing/i3](../into-the-housing/summary.md), [change-the-question/c6](../change-the-question/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Filling the revolver or sticks away from any wire; cut, split, strip (stop set from a measured kit contact); clamping ribbon ends and unloading; insertion, or the vertical gang push.
- **Major unresolved problems:**
  - Kit contacts' shape and uniformity; a mixed bag jams (per-contact measurement is the repair)
  - A 6 mm, 0.043 g contact tumbling in the chute
  - Whether the open SN jaw has room for the chute tongue plus a 3.35-4.10 mm passage
  - The jaw law turned vertical: 8.7-14.7 mm of stand-out and the copper set it leaves
  - Per-crimp pulls on loose contacts need the neck or a stepped plate

### [a2c — One baseplate, three stations: a stripper in a squeezer, a1's crimper, a housing nest](ideas/a2c-one-baseplate-strip-crimp-insert.md)

a2's carriage visits three stations in batches. Every conductor goes into the Klein 11063W in a second squeezer, cut end on a grounded length stop; then every conductor goes through a2's crimp cycle; then the contacts are inserted one at a time at a housing nest. For each insertion the fork forms a 7.5-10 mm hump in conductor k to store its seating travel while the head stays still, and a slotted stencil-steel blade no wider than 1.95 mm pushes the contact home by the rear of its insulation crimp, followed by a 3-8 N pull-back. The head routes any conductor to any cavity, so the machine makes J4's and J7's crossings.

- contacts: carrier strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die.
- **Branch of** a2.
- **Automates:** strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cut to length and split the ends; load stubs; drop housings in and swap ribbon ends for pairs; label.
- **Major unresolved problems:**
  - Whether the Klein 11063W strips this silicone cleanly, without nicks, at 2.4 mm
  - The Klein moves the wire during its pull; the axial position is re-found at the crimp station
  - The hump in set copper, and the blade pusher between seated neighbours
  - Insertion force is not public; the insulation crimp's rear edge is the push face and is weak above ~15 N

### [a2d — Strip all, crimp all, lay the row into a squaring comb, push the housing onto it](ideas/a2d-batch-then-gang-push.md)

a2c's strip and crimp stations run in batch; the head then lays each crimped conductor into its pocket of a 2.5 mm steel-faced squaring comb in pin-map order, laying J4's and J7's crossing conductors last, over the top. A front plate pushes every nose back to one line and a rear clamp closes 1-2 mm behind the insulation crimps. A fixed housing slide (NEMA 17 on a Tr8x2 screw through a load cell, ~280 N) drives the XHP onto the whole row past a sprung guide comb, so no conductor needs stored feed.

- contacts: carrier strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die.
- **Branch of** a2c.
- **Combines:** [into-the-housing/i3](../into-the-housing/summary.md), [change-the-question/c5](../change-the-question/summary.md).
- **Automates:** strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting and splitting the ends; loading stubs; clamping ends and dropping housings; unloading and labelling; the latch check unless a camera, wired-header or staggered-row route is built.
- **Major unresolved problems:**
  - The latch check: a summed force hides one unlatched contact
  - Slack stored behind the housing by squaring; whether it looks acceptable
  - Laying a crossing over the top without dislodging contacts already in their pockets
  - Jam recovery in a nine-contact push; a wide clamp and two loom tails for pairs

### [a3 — The tool travels: a self-closing crimper on a light gantry, over a ribbon clamped on edge](ideas/a3-tool-travels-to-ribbon.md)

The ribbon end is clamped once in a printed fixture standing on edge, its conductors stacked vertically at 2.5 mm in a comb. A laser-engraver-class gantry carries the SN-2549 hung tip-down with its own pusher and load cell, so the force loop closes inside the module; it picks a contact off a wired post column, a side-puller draws conductor k out by the jaw-half depth plus 2.7 mm, a backlit picture of the tip corrects the module's axis, and the tool slides the contact on until green, crimps, steps sideways and rises out. After the last conductor a front plate and a late rear clamp square the fronts, and the fixture's own housing slide pushes the XHP onto the whole row.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: die head brought to a still conductor.
- **Combines:** [into-the-housing/i3](../into-the-housing/summary.md), [machine-that-sees-and-learns/v1](../machine-that-sees-and-learns/summary.md), [change-the-question/c5](../change-the-question/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cut and split; strip unless a strip module is added; load the post column; clamp the end and lay J4's and J7's crossings; drop the housing; unload and label.
- **Major unresolved problems:**
  - The jaw-half depth a sets the pull (a + 2.7 = 8.7-14.7 mm) and how much copper sets
  - Slide-on capture of +/-0.24-0.59 mm against a tip that may sit 0.28-0.69 mm off; how often tips splay
  - Contact pull-off from a 0.64 mm post (0.2-1.6 N estimated)
  - The latch check in a gang push is a sum
  - A ~0.8 kg module on a light belt gantry whose payload is not stated

### [a4 — The dies leave the tool: SN jaws in a guided die set, driven by a slow eccentric](ideas/a4-dies-in-a-die-set.md)

A spare SN-2549 jaw set is screwed into laminated laser-cut steel holders on a two-rod guided ram, turned by a 2-2.5 mm eccentric: first by a 150-200 mm hand lever, later by a NEMA 23 through a 10:1 planetary or a self-locking worm. A disc-spring stack preloaded to ~3.5 kN under the lower die, with die contact set 0.17-0.28 mm above BDC, lets the dies bottom on every stroke with the peak capped near 3.6 kN; a button cell reads die force directly and a 0.001 mm indicator read at a 10 N re-touch gives crimp height on every crimp. The open die set shows the neck and lance; a1's locator or a2's carriage loads it.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes · usable without a motor.
- **Combines:** [force-and-form/f3](../force-and-form/summary.md).
- **Automates:** crimp, verify crimp.
- **What the person still does:** Whatever a1 or a2 hands back, depending on what loads it; the one-time metalwork of two holders and two side plates.
- **Major unresolved problems:**
  - The SN jaw's seat geometry has to be copied from a tool; the only Prime 2549 die comes inside the IWS-0723K kit
  - Whether SN dies bottom face to face (if not, a stop block between the holders sets height)
  - Four custom steel parts, none printable
  - Heavy-series disc springs are not on Prime
  - Frame-loop stiffness and stack rate are estimates; one empty stroke with the cell settles both

### [a4b — One SN nest on a C-frame arm that reaches over the row](ideas/a4b-c-frame-one-nest-head.md)

a4's eccentric, disc-spring cartridge and a one-nest SN die pair go into a fist-sized steel C-frame whose lower arm, 6-8 mm wide and 3-5.5 mm thick, reaches back over a flat row from in front of the tips and carries a flush anvil insert. a3's gantry carries the head; a lifter raises conductor k 6.3-9.2 mm, a tip picture corrects its axis, and the head slides the contact on until green, crimps with the dies bottoming on the stack, drops 1.5 mm and withdraws. The crimp comes out upright whatever shape the SN jaw has, the neighbours pass under the arm, and a3's squaring and housing slide finish the end.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: die head brought to a still conductor.
- **Branch of** a4.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** As a3, plus the metalwork: C-frame plates, one-nest cuts in a jaw set, laminated holders.
- **Major unresolved problems:**
  - Cutting hardened SN pieces to one nest and a flush anvil insert without cracking
  - Aligning a ram-guided punch to an anvil on a cantilevered arm that deflects 30-150 um and tilts 0.4-1 degree
  - The 6.3-9.2 mm lift still sets copper (root radius 22-63 mm)
  - Slide-on capture against tip offset, as in a3
  - A 1-1.5 kg head on a light gantry

### [a4c — One SN nest as the heavy station behind a tack station: the machine places and pins, the die set crimps](ideas/a4c-one-nest-behind-a-tack-station.md)

A bed-slinger printer stage carries a ribbon end fanned to 5 mm in machine-that-sees-and-learns' keyed pallet. At station T a servo former cut from a spare SN jaw's insulation section tacks each contact onto its conductor, and a camera looks straight down into the open conductor barrel before anything irreversible; a failed look costs a contact, not a ribbon end. The stage carries the tacked contact 1.0-1.7 mm high into station C, a one-nest SN die set whose T-section punch holder stays narrow enough to pass between the lifted neighbours, sets it on a ledge, and the eccentric crimps against a preloaded disc stack; a re-touch indicator and a silhouette give two independent crimp heights.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die.
- **Branch of** a4.
- **Combines:** [machine-that-sees-and-learns/v8](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v1](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v1b](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v4b](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v7](../machine-that-sees-and-learns/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cut, split and strip; loading pallets and the pocket plate; answering 1-2 asks a unit; housing insertion; label; the one-time steelwork (die set, one-nest cuts, T's former).
- **Major unresolved problems:**
  - Cutting hardened SN pieces to one nest without cracking, twice (C's die pair and T's former)
  - The tack's grip window on silicone (0.2-1.5 N wanted, 0.4-9 N estimated); a snag on the T-to-C carry is resisted only by the tack
  - Tacked then re-formed against one pass for the insulation crimp (narrowed to re-registration if T's former is the SN's own section)
  - The per-crimp pull on loose contacts needs the neck or a stepped plate
  - Whether SN die faces meet, and the jaw seat to copy
  - The keys' root kink (5-12 degrees) in every conductor

### [a4d — One SN nest cut to a tongue, crimping in the row under change-the-question's windowed pallet](ideas/a4d-tongue-under-a-windowed-pallet.md)

change-the-question's c1c layout: one X slide carries the web clamp, two pallets of printed carriers at 3.4 mm and the housing nest under a fixed steel C whose spine stands in front of the housing. Contacts arrive pre-formed (a6b's click or c6's keyhole) in loom-order sticks, a presser comb snaps a whole half-row onto its conductors, and the slide steps each carrier over a 1.9 mm HSS anvil blade under a one-nest SN punch cut to a tongue no wider than 4.45 mm, with height from a stop and force capped by a disc stack. No conductor is stood out or kinked; the rows are spread, pushed into the housing and tested on a wafer.

- contacts: pre-formed contacts · steel: SN-2549 or similar hand-tool dies · meeting: pallets dock (all contacts placed at once).
- **Branch of** a4.
- **Combines:** [change-the-question/c1c](../change-the-question/summary.md), [change-the-question/c6](../change-the-question/summary.md).
- **Automates:** split, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Stripping (another station); pre-forming (by hand at a6b's click, or a1b); feeding sticks and housings; laying each ribbon end; J4's crossings; label.
- **Major unresolved problems:**
  - Cutting a hardened jaw to a 4.45 mm tongue without cracking
  - The flat HSS anvil replaces the SN's lower cradle: the crimp's underside differs and the stop alone sets height
  - c1c's cam plate and the anvil want the same place under the carrier
  - Carriers sprung against a fixed stop meet it sideways when stepping, and 40-100 N of rearward proof pull has no restraint
  - The pre-form's own window and grip
  - Everything c1c leaves: split length behind the housing, row B's push between row A's wires, J4

### [a5 — A precision plier with no ratchet (Engineer PA-09), squeezed twice by a machine that knows when to stop](ideas/a5-two-squeeze-plier.md)

An Engineer PA-09 ($38.99 on Prime) lies in an a1-style cradle and is squeezed twice by the pusher: once in its 1.6 mm die on the conductor barrel, then, moved by its wire, in the 1.9 mm die on the insulation barrel. The station MCU stops each squeeze on a force or position taught from crimps that measured well, so crimp height becomes a setting and each barrel has its own force curve; the insulation squeeze stops between a floor (fits the cavity) and a ceiling (cuts the silicone). The first build is the plier in the hand with two printed stops on its jaw.

- contacts: either loose or strip · steel: JST or Engineer hand tool · meeting: the person presents, the machine takes · usable without a motor.
- **Combines:** [machine-that-sees-and-learns/v3](../machine-that-sees-and-learns/summary.md).
- **Automates:** crimp, verify crimp.
- **What the person still does:** Whatever a1, a2 or a3 hands back; the second placement in the person-fed version; teach-in by sectioning or micrometering sample crimps.
- **Major unresolved problems:**
  - The 1.8 mm-thick die over a clone-length conductor barrel reaches the box by up to 0.55 mm: a genuine-contact arrangement unless the kit barrel measures ~1.8 mm
  - No mechanical stop: every crimp rests on the machine's stop decision
  - Scissor action closes the dies on an arc
  - Two placements per crimp
  - The insulation squeeze's floor and ceiling are ~0.1-0.3 mm apart on this wire

### [a6 — The foot-closed jig bench: today's hand procedure, a stop for every placement, no motor](ideas/a6-foot-closed-jig-bench.md)

Five jigs on a baseplate: an end jig (under-width channel, cut slot, split line, Klein stop set from a measured contact); the SN-2549 in a cradle with a1's insulated-blade locator, closed through a Dyneema cord by a two-stage foot treadle (half-press is the first tooth, full press the crimp); a pull-and-look jig (a backed plate on the box, a blade and roll flat under the crimp, an ELP silhouette, a capstan lever to a 20 N leaf switch); a stencil-steel keyhole gauge; and into-the-housing's i5 wired header nest. The far end sits in a push-in block on an ESP32 from start to finish, giving amber and green lamps, a buzzer for the wrong conductor, a conductor-to-cavity record and, optionally, a force log of every foot-closed crimp. Every jig carries the interface a motor takes later.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes · usable without a motor.
- **Combines:** [into-the-housing/i5](../into-the-housing/summary.md), [machine-that-sees-and-learns/v5](../machine-that-sees-and-learns/summary.md), [ribbon-as-pallet/a1](../ribbon-as-pallet/summary.md).
- **Automates:** verify crimp, verify insertion and pin order.
- **What the person still does:** Every motion: cutting, splitting, stripping, placing each contact, steering each conductor, both presses, the pull and the gauge, starting each contact into its cavity, labelling. About 31 min a unit with pull and keyhole against ~22 min today; it buys repeatability and checks, not minutes.
- **Major unresolved problems:**
  - The neck on a kit contact decides blade or camera line, and flat or stepped pull plate
  - Where the first ratchet tooth falls, which the treadle's step is set to
  - The Klein on this silicone: the jig makes the length repeatable, not the cut clean
  - The far end must be stripped and in the block before the XH end is crimped
  - Per-crimp pulls on loose contacts depend on the neck or an untested stepped plate

### [a6b — Flags by hand: the SN-2549 pre-forms its own contacts, a snap block puts each on its wire, the foot crimps](ideas/a6b-flags-by-hand-foot-crimp.md)

A second SN-2549 closed to one chosen click on an empty kit contact narrows its insulation barrel to the die's own width, because the insulation wings meet a single-stroke die before the conductor wings; the contacts go nose to tail into loom-order sticks while a print runs. At a snap block with a wired tip plate and a backlit window, a thumb tool presses each stripped conductor's jacket into the narrowed U and its strands into the open conductor barrel, making a flag. At a6's crimp jig a sprung seat carries the flag 1.1-1.7 mm above the anvil so its lance never drags; the person slides it until a wired front-stop leaf lights green, stops pushing, and crimps with a single-stage treadle.

- contacts: pre-formed contacts · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes · usable without a motor.
- **Branch of** a6.
- **Combines:** [change-the-question/c6](../change-the-question/summary.md), [change-the-question/c6b](../change-the-question/summary.md).
- **Automates:** verify crimp, verify insertion and pin order.
- **What the person still does:** Every motion: the click pre-form, the snap, sliding each flag to green, the treadle, drawing out, pull and gauge, insertion, labelling. About 19-30 min a unit, 7-11 of them pre-forming while a print runs.
- **Major unresolved problems:**
  - Whether the insulation-first window exists on this SN-2549 (0.65-1.7 mm of die stroke on the edge model; can vanish on the apex model)
  - What throat the chosen click leaves, and the snap's grip in a U (0.08-3.8 N by change-the-question's model)
  - Whether the SN-2549 opens 3.6-4.9 mm at the nest for a flag carried at h
  - The SN insulation profile (B or not) and its closed height
  - Whether the release lever frees the pawl at any mid-cycle click
  - The jacket's real OD, which sets the grip

### [a6c — Flags by machine: a tack station places and pins every contact, the foot crimps each flag in the SN-2549](ideas/a6c-flags-by-machine-foot-crimp.md)

machine-that-sees-and-learns' station T on a printer stage runs a whole ribbon end unattended: it lays each conductor from a keyed 5 mm pallet into a contact, closes the insulation wings loosely with a servo former, looks straight down at every strand, and backs out on a failed look at the cost of a contact. The person then takes the pallet to a6's crimp jig, bends each flag out of the row, slides it along a6b's sprung seat to a wired front stop set per contact lot, and presses a single-stage treadle. The machine does the step Derek most wants automated; the person does the squeeze.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die.
- **Branch of** a6.
- **Combines:** [machine-that-sees-and-learns/v8](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v1](../machine-that-sees-and-learns/summary.md), [machine-that-sees-and-learns/v1b](../machine-that-sees-and-learns/summary.md).
- **Automates:** supply contacts, place contact on conductor, verify crimp, verify insertion and pin order.
- **What the person still does:** Loading pallets and contacts; carrying the pallet to the crimp jig; bending each conductor out; every squeeze by foot; pull and gauge; insertion; cut, split, strip; label. About 20-33 min a unit at the crimp jig plus pallet loading.
- **Major unresolved problems:**
  - The tack's grip window on silicone
  - Roll in handling past the tack's ~0.34 N.mm resistance
  - Tacked then re-formed against one pass
  - The jaw opening at the nest for a tacked flag at h (3.6-4.4 mm) is unmeasured
  - Set copper from the keys' roots and the hand's bend
  - T's former and lever must stay <= ~7.3 mm wide between tacked neighbours when a whole end is tacked first

## Combinations with other explorers

- a4c: a4's one-nest SN die set as station C behind machine-that-sees-and-learns v8's tack station T, on v1's keyed pallet and v1b's printer stage, run by v7 (their W1); this view adds T's former cut from the SN's own insulation section, so the tack is the SN stroke paused
- a6c: machine-that-sees-and-learns v8's tack station making flags for a6's foot-closed SN-2549 with a6b's sprung seat and wired stop (their W2)
- a6b: change-the-question c6/c6b's flag, snap block and loom-order sticks with the SN-2549 itself as the pre-former (a click inside the insulation-first window), a6's treadle and electrode stops (K1)
- a4d: a4's one-nest die cut to a <= 4.45 mm tongue with a <= 1.90 mm HSS anvil blade under change-the-question c1c's windowed pallet at 3.4 mm, neighbours pre-formed by c6 or a6b (K2)
- a6's pull-and-look jig: the backed pull plate plus machine-that-sees-and-learns v5's blade, roll flat and silhouette (W3); a6's cord cell and pulley AS5600 as v7's rung 0.5, labelled data before any motor (W4)
- a3 with machine-that-sees-and-learns v1's backlit tip picture before every slide-on (W5); a2's grounded tip plate checked against v1's hover picture (W9)
- a2b with machine-that-sees-and-learns v4/v4b per-contact measurement before loading (W7), and with change-the-question c6's loom-order sticks as its chute (K3)
- a1b with machine-that-sees-and-learns v7's MCU-owned force wall and write-ahead journal (W8); a1b and a5 as v3's sweep presses with change-the-question c2's JST lead as the target (W6, K6); a1b as change-the-question c3's fold station (K5)
- a2d and a3 with change-the-question c5's T4 scope and the unspooled remainder on a slip ring as the far-end electrode array (K4)
- a6 with into-the-housing i5: one far-end block records conductor-in-cavity, catching J2's post 3 and J4/J7 swaps (their C3)
- a2d = a2c + into-the-housing i3's housing press and sprung guide comb (their C2); a3 on edge + i3's gang push on the fixture
- a1 and a6 with terminal-supply a2c's pilot-pin clip for strip stubs when the neck is too short for a blade

## Transferable mechanisms

- The hand as existence proof for force: any two-handle tool Derek closes by hand needs at most ~90-220 N at the grip, whatever its internal gain
- Squeezer cradle: a printed saddle plus one pusher, winch or cord turns any bench hand tool (crimper, stripper, cutters, ferrule crimper) into a station
- A foot closes the hand tool through a cord on a 2:1 heel-hinged treadle (<= ~120 N at the toe over ~60 mm); a sprung two-stage step makes 'hold' a half-press at the first ratchet tooth
- Opening limiter: a printed block so the tool opens only as wide as loading and the lift-before-draw need
- Load cell in the cord and an AS5600 on its pulley: a force-against-travel curve for a foot-closed crimp, kept when a motor replaces the foot
- The station MCU owns every squeeze of a hand tool (force wall, ratchet-release detection, heartbeat); the handle's rising gain gives a free crawl at the die (0.05-0.13 mm/s at 2 mm/s grip) but not a free stop
- Insulated strand-stop blade: polyimide on the front face, bare rear face as electrode, so 'strands entered' (amber) and 'strands at depth' (green) are separate events
- Electrode stops through the ribbon's far end: tip plate, box stop and die jaws each wired as a separate lamp; the far end also names the conductor and pairs it with a header post
- The side-entry jaw law: a hand tool making upright crimps lies along the row, so the working conductor stands out a + 2.7 mm once neighbours carry crimps; closing across the row rolls every crimp 90 degrees
- Lift before drawing back (a ramp on the locator), and carry-clear-then-set-down, so a crimp's lance never meets the anvil face
- Proof pull on a backed plate bearing on the box's rear walls, lance relieved, never in the tool; a stepped plate bears outside the crimped barrel's width and above its height, so only a non-bearing tongue must fit the neck
- Keyhole fit gauge: a stencil-steel cavity section with a lance notch and a side slot narrower than the wire; the crimp passes nose first once
- Rear-face drop-shear of a carrier tab while the jaws hold, before any wire arrives
- Lay-down into a squaring comb in pin-map order with crossing conductors laid last over the top, then front plate, late rear clamp and a fixed housing press
- Die set with preloaded disc springs as the ratchet; die contact set at preload / frame stiffness + 0.05 mm above BDC, found by stepping down on empty strokes until the button cell shows the stack's knee
- Re-touch at ~10 N with a 0.001 mm indicator across the holders; with a silhouette it gives two independent crimp heights that check each other
- A hand lever on an eccentric shaft: a motorless press whose bottom is geometry, later motor-driven on the same shaft
- The crimp tool as its own pre-former or tack: a single-stroke die shapes the insulation barrel before the conductor barrel, so a click or a set grip position, or a former cut from the same die's insulation section, narrows the barrel in the profile that will finish the crimp
- Flag seat: a sprung two-level entry (rear U guide on the jacket, keyed ledge under the box, both at h on 1-3 N springs) with a wired front-stop leaf; green means stop pushing
- T-section punch holder: narrow where lifted neighbours are, wide above them
- Tongue punch <= 4.45 mm with a narrow HSS anvil blade rising through a carrier window, height from a stop beside the anvil
- Per-lot calibration: strip stop, box-front stop and chute section set from five contacts of the lot measured under the camera, not from drawing tolerances
- Force loop closed inside the tool or head, so any light positioner (printer frame, laser-engraver gantry) carries it

## Key findings

- a4's rigid-frame overtravel does not hold [calc w3 §1, agreeing with machine-that-sees-and-learns' w3 §6]: with a 15-30 kN/mm loop, 0.15 mm past die contact leaves the stack idle or the dies apart; die contact set 0.17-0.28 mm above BDC engages the stack at every stiffness, ~3.6 kN at BDC, 1.6-2.0 N.m before friction and 2.0-3.0 N.m with it; a NEMA 23 through the Prime 10:1 planetary or a 150-200 mm hand lever at 15-20 N carries it
- A proof pull cannot be taken honestly in a hand tool: a grip-side few newtons is 30-200 N at the dies and adds 4-100 N of grip; held open, the lance meets the anvil face before the box shoulder. Pulls go to a backed plate on the box's rear walls
- The pull plate: a flat plate needs the same 0.35-0.5 mm neck as the blade; a stepped plate bearing outside the crimped barrel's width (0.12-0.28 mm a side) and above its height needs only a clean step at the box's rear; a backer to 1 mm above the floor lets a 0.15 mm plate fit a 0.2 mm transition at 100-630 MPa [calc w3 §3, estimate]
- Side-entry stand-out with crimped neighbours is a + 2.7 mm = 8.7-14.7 mm, root radius 9-47 mm on a 20-35 mm free length, tip pull-back 1.3-6.5 mm [calc w3 §2]
- Strip length belongs to the contact: JST's own rule on clone-drawing barrels gives 1.60-2.10 mm (the KONNRA clone spec); 2.4 mm implies a genuine barrel of 1.8-2.05 mm; each is wrong on the other by up to ~0.5 mm toward a named defect, so the stop is set from a measured contact of the lot
- The PA-09's 1.8 mm-thick conductor die over a clone-length barrel reaches the box by up to 0.55 mm; a5 is a genuine-contact arrangement unless the kit barrel measures ~1.8 mm
- The insulation crimp's room under the 2.4 mm envelope on 1.7 mm silicone is ~0.1-0.3 mm; the ellipse is the tallest section
- A single-stroke SN die touches the insulation wings 0.65-1.7 mm of stroke before the conductor wings (edge model, can vanish on the apex model), so the tool can pre-form or tack its own contacts; change-the-question c6's round keyhole is a shape a B die neither makes nor re-forms (tips 0.14-0.52 mm below the closed height)
- A flag's grip on its wire (0.08-3.8 N pre-formed, 0.2-1.5 N tacked) is below the 1-5 N that folds a lance dragged over the jaw's edge, so a flag must be carried at h = 1.1-1.7 mm, needing 3.6-4.9 mm of jaw opening [calc w3 §5]
- The W1 pairing's geometry holds: 7.45 mm free between crimped neighbours' boxes at 5 mm pitch; a T-section punch narrow to ~5.9 mm above the crimping edge; e = 2.0-2.5 mm passes a tacked contact carried level with 0.5-1.7 mm to spare; laying in under the punch instead needs e = 3.0-3.5 mm and loses the straight-down look [calc w3 §4]
- At 3.4 mm with pre-formed neighbours a one-nest SN tongue <= 4.45 mm crimps upright with no stand-out; the anvil becomes a <= 1.90 mm HSS blade and crimp height comes from a stop [calc w3 §6]
- The handle gives a free crawl but not a free stop: a 0.5 s Mac stall is 108-857 N extra at the dies, so the force wall lives on the station MCU
- Person time: jig bench ~31 min a unit with pull and keyhole; hand-made flags 19-30 min (7-11 of them pre-forming while printing); machine-made flags 20-33 min at the crimp jig plus pallet loading; today ~22 min. The motorless benches buy checks and one-stop acts, not minutes
- Prime pass: SN-2549 $22.29, PA-09 $38.99, DITR-0105 0.001 mm indicator $52.99, 500 kg button cell $74.99, NEMA 23 10:1 planetary $48, Greartisan 40 kg.cm self-locking worm $26.99; no SN jaw set alone and no heavy disc springs on Prime

## Where this view still had trouble

- Crimping in the row at 2.5 mm: no SN-derived punch fits beside open neighbours (walls need 0.47-1.12 mm each, a 2.8-4.1 mm punch against 3.3 mm free); every variant here lifts, stands out, spreads to 3.4-5 mm, or narrows the neighbours first
- An unmodified side-entry hand tool at 2.5 mm pitch always stands the working conductor out 8.7-14.7 mm and sets the copper; only cutting the jaw (a4b, a4c, a4d) or putting the contact on the wire first (a6b, a6c) escapes it
- Stripping soft silicone: this view hands it to the Klein 11063W in a squeezer or behind a jig stop and has no developed answer for a clean, nick-free cut on this jacket
- Loose kit contacts in a fully automated path without a camera: a2b's chute and a3's post column rest on uniform contacts; a mixed bag needs machine-that-sees-and-learns' per-contact measurement
- A per-crimp proof pull on loose kit contacts depends on the unmeasured neck; the stepped plate is untested
- Automated insertion with crossings and pairs from a hand-tool station: a2c and a2d make crossings only at the cost of a humped feed or a gang push whose latch check is a sum
- How long a cradled SN-2549 holds its crimp over ~3,200 crimps: this view cannot say where hand-tool compliance and wear should hand over to a die set

## Questions for Derek

- Photograph one kit contact from the side under the ELP beside a steel rule: how long are the conductor barrel, the window and the neck, and is the box's rear edge a clean step? (strip length, blade, pull plate, a5's fit)
- Close the SN-2549 one click at a time on an empty kit contact, releasing after each, and look end-on: at which click are the insulation wings inside the die width, and at which does the conductor barrel first show a mark? (a6b, a4c's former, a1b's pre-form)
- How wide does the SN-2549 open at the XH nest, jaw to jaw, handles fully open? A flag carried clear of the anvil needs 3.6-4.9 mm
- Is the SN-2549's XH insulation section a B (two arches and a cusp), and how tall is it closed? An ELP image of the die, or one crimp on a bare jacket cut through
- Clamp the closed SN-2549 by one handle and hang a known weight from the other grip: how far does the grip move?
- Held closed against a light, do the SN-2549's jaws meet face to face?
- With a luggage scale on the grip, what force does one XH crimp take, and what is the grip span open, closed, and at the least opening that still passes a contact?
- How deep is the SN-2549's jaw half behind the XH nest in the closing direction? It sets the stand-out (a + 2.7 mm) in a2, a2b and a3
- Caliper the OD of five split conductors, not the ribbon pitch: it sets a flag's grip on its wire
- Would a foot treadle under the bench suit how you sit or stand there?
- Is each loom's far end free and stripped while its board end is crimped, so it can sit in the far-end block from start to finish?
- Would the machine get its own SN-2549 ($22.29 on Prime), leaving the bench one for hand use? A second one is also a6b's click pre-former
- Is genuine SXH-001T-P0.6 on strip acceptable in place of the kit's loose contacts? A 100-piece Digi-Key strip ($4.71) gives pitch, pilot hole, tab and the genuine barrel length
- Is ~2 mm of slack stored behind the housing (from squaring the fronts before a gang push) acceptable on a finished loom?
- Would you slice one kit housing to measure its rear-entry section for the keyhole gauge?
- If a die set is built, one empty stroke with the button cell gives the frame's stiffness and the stack's knee
