# procedure-is-the-machine

*The sequence and the division of labor are the design.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [p1 — Cassette and benches (bench B in three forms: B-drop here, B-lift p1c, B-fin p1d)](ideas/p1-cassette-and-benches.md)

A printed cassette holds one housing's worth of ribbon end: the person clamps it (a hard stop sets a 15-30 % jacket squeeze), fans the conductors into keys where key k = cavity k, makes J4/J7 crossings in a raised loft, blanks J2's key 3, and puts the raw far end in a pogo block on the cassette. Single-purpose benches take the cassette onto their own dowels: bench A trims along the cassette's own slot and strips; bench B in its B-drop form presses the waiting conductors ~7 mm down, a V-fork rises under k, a lay-in finger sets k into a cut-free contact waiting on a stepped fin (1.45 mm under the conductor barrel, 1.8-1.9 under the insulation barrel), and a ram through a stiff spring drives the punch to stop blocks in a short steel loop. Identity is read through the fin at lay-in; a hook pulls 20 N through the box with the punch up; bench C gang-inserts and tests pin to pin through the far-end block.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die · usable without a motor.
- **Combines:** [ribbon-as-pallet/a6](../ribbon-as-pallet/summary.md), [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [hand-tool-as-press/a2](../hand-tool-as-press/summary.md), [force-and-form/f7](../force-and-form/summary.md).
- **Automates:** cut, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting, peeling, laying conductors into cassettes (and making J4/J7 crossings in the loft), loading cut-free contacts (stubs, blade-held loose contacts, or posts), carrying cassettes between benches, labelling. Build stages run from the cassette alone with the SN-2549 by hand, to a squeezer module, to bench B, then A, then C.
- **Major unresolved problems:**
  - B-drop's stepped fin (9-10 mm tall, 1.45/1.88 mm) made and hardened without cracking, and a cut-free contact supply that reaches it without crossing the dropped row
  - The presser leaves 1.3-4.5 mm of set in every waiting conductor at 20 mm free, so B-drop wants a 25-30 mm split and capture from below
  - B-drop axial chain ±0.23-0.33 mm RSS against a ±0.3 mm window, mostly unmeasured strip-length scatter
  - V-jaw-and-pull stripping of silicone at bench A is untested
  - Gang insertion needs every front on one line ±0.3 mm
  - Web peel stays a person step (repo Open item 5)

### [p1b — Carousel joins the benches](ideas/p1b-carousel-joins-the-benches.md)

p1's benches are bolted unchanged around a 300 mm lazy-susan ring of 12 cassette nests, turned by a rim belt with a ball-plunger detent; each station lifts the cassette 1-2 mm onto its own pins, so the ring's ±0.5-1 mm never reaches the work. Station A flush-cuts, strips the webbed end with p7's razors and pads, splits from the slug's gap with a razor comb in the valleys, and fans into the comb; bench B is any of its three forms (B-fin, B-lift, B-drop); then a camera, gang insertion with a force-before-distance check, and a pin-to-pin test and label. The person loads a unit's ten cassettes unpeeled and returns to unload and label; a failed cassette rides round for a redo lap.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Branch of** p1.
- **Automates:** cut, split, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting ribbons and laying them in, peeling and laying J4/J7's crossing conductors by hand, loading housings and the posts, unloading, labelling, redo laps (sliding the ribbon out 6 mm). About 19 attended minutes a unit [estimate].
- **Major unresolved problems:**
  - Machine web splitting on this silicone (web neck thickness unmeasured)
  - J4/J7 crossings still need hands, or a changed ribbon assignment
  - Five stations' worth of motors and wiring for 53 crimps a unit
  - A cassette-ID misread runs the wrong program (the test header is the backstop)

### [p1c — Lift once under a hand-tool module: the SN-2549 lies on its side](ideas/p1c-lift-once-tip-down-module.md)

At bench B a finger lifts key k alone by h = a + 2.7 mm (a = the anvil jaw half's depth below the nest, 6-12 mm assumed, so 8.7-14.7 mm); the neighbours stay in the row. A dedicated SN-2549 lies on its side (jaws closing vertically, normal to the row, anvil half underneath, so every crimp is upright; hung tip-down closing along the row it would roll every crimp 90°), its pusher bolted to its own handle so the force closes inside a ~0.8 kg module. A short X shuttle on a Y carriage brings a grounded trim blade (which squares k and reads identity through the far-end pogo block), a strip head, and the module, which has picked a contact from a post revolver closing only to wing touch (short of the first ratchet tooth, so the insulation bore stays open) with a blade in the neck; the camera reads the bare length, Y slides the contact onto k to that depth, the pusher pauses at the end of the curl for a second identity read, then completes the crimp. A 20 N pull through the box, then k is laid back and squared into the row.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: die head brought to a still conductor.
- **Branch of** p1.
- **Combines:** [hand-tool-as-press/a3](../hand-tool-as-press/summary.md), [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [terminal-supply/a4](../terminal-supply/summary.md), [terminal-supply/x1](../terminal-supply/summary.md).
- **Automates:** cut, strip, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cutting, peeling and loading the cassette (crossings in the loft), loading the post revolver in key order, bench C gang insertion or hand insertion, labelling.
- **Major unresolved problems:**
  - a, the anvil jaw half's depth over the ~20 mm of jaw crossing the row, sets the lift; 8.7-14.7 mm leaves 0-8.2 mm of rise at 30 mm free, so a 30-35 mm split and a squaring push after every crimp
  - Whether copper that yielded twice stays within ~0.5 mm of the row after squaring
  - Camera depth needs the contact's neck ≥0.70-0.90 mm so tips stay off the blade; otherwise touch-off depth (±0.22 mm RSS)
  - Crimp height and insulation step are the SN-2549's own, fixed
  - The proof pull's reaction through the cassette clamp needs a 15-30 % jacket squeeze

### [p1d — Lift once, crimp upright: a fin rises from below into a steel C](ideas/p1d-lift-once-fin-from-below.md)

The cassette (or a reel clamp) indexes key k to a fixed station; a narrow finger lifts k alone 3.5 mm while a tip comb 5-7 mm behind the tips holds the neighbours. A grounded blade trims k (identity through the far end), the backlit camera reads its bare length, and a two-tier post bar (odd keys, then even keys 8 mm forward, loaded in key order with kit contacts or strip stubs) slides the fully open contact onto k to that depth. A stepped fin (1.45 mm under the conductor barrel, 1.88 under the insulation barrel, ground stock on edge or laminated 1095 shim) rises ~4.8 mm through k's own empty slot with 0.56-1.42 mm of clearance to the neighbours, a gate wedge slides under its foot, and a knee in a fist-sized steel C (spine ~25-30 mm ahead of the tips) drives a narrow stepped crimper to the knee's straight position, pausing at the end of the curl so the C reads identity through the contact. A re-touch reads crimp height on a 0.001 mm indicator, a hook pulls 20 N through the box, and k is laid back upright with 0-0.05 mm of set at 25 mm free.

- contacts: either loose or strip · steel: made dies (EDM, machined, laser-cut) · meeting: conductor brought to a fixed die.
- **Branch of** p1c.
- **Combines:** [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f4](../force-and-form/summary.md), [force-and-form/f7](../force-and-form/summary.md), [force-and-form/f8](../force-and-form/summary.md), [terminal-supply/a4](../terminal-supply/summary.md).
- **Automates:** cut, strip, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cutting and peeling (or p7's lever strip first), laying the cassette with crossings in the loft, loading the post bar in key order, docking cassettes or a magazine of ten, insertion at bench C or by hand, labelling. About 40-44 attended minutes a unit on the library that gives ~46 by hand; the machine calls once a unit.
- **Major unresolved problems:**
  - The steel: crimper profile (EDM to a traced drawing, or a knife set of unknown profile and price) and fin temper
  - The contact's neck n: the fin must carry the conductor barrel's front and stop behind the lance (n ≥ 0.34-0.74 mm; clone drawings allow 0.30-2.28)
  - Tip wander against 0.56-1.42 mm of fin clearance; the tip comb is unbuilt
  - The insulation crimp on silicone at a fixed crimper step (branch p1d-f6 separates it)
  - The proof-pull reaction through the cassette clamp (disappears at a reel)
  - Wear of the gate, fin slide and knee pins over ~3,200 cycles

### [p2 — Still ribbon, tools come to it (crimp head in three forms: C, T, F)](ideas/p2-still-ribbon-tool-turret.md)

The ribbon end is clamped once on a y carriage, far end in a pogo block, and never re-gripped; a drum turret on an x slide brings trim, splitter, strip jaws, a crimp head, a camera and an insertion gripper along the wire axis. Per conductor, straight through: the selector lifts k once and every tool acts on it in that pose. The crimp head is C (a strip-fed C-frame whose lead-in halves part so the crimp can leave), T (an SN-2549 on its side, lift 8.7-14.7 mm) or F (p1d's steel C whose lower arm slides under the cantilevered tips, lift 3.5 mm), each upright and closing its own force; a bow-and-push gripper inserts each contact into its cavity, so J4/J7 crossings and J2's skip are made by program.

- contacts: either loose or strip · steel: any of several · meeting: die head brought to a still conductor.
- **Combines:** [hand-tool-as-press/a3](../hand-tool-as-press/summary.md), [force-and-form/f4](../force-and-form/summary.md), [ribbon-as-pallet/a6](../ribbon-as-pallet/summary.md).
- **Automates:** cut, split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting to length, laying each housing's ribbon(s) into the clamp with a housing in the nest (ten calls a unit), unloading, labelling.
- **Major unresolved problems:**
  - Six or more motions around one point, and their clearances
  - Head C's exit and depth, head T's lift (a, 30-35 mm split), head F's made steel
  - Bow-and-push insertion on soft silicone is not demonstrated anywhere found
  - Per-housing loading; a magazine of clamps turns it into p1
  - Stripping and splitting as elsewhere

### [p3 — Terminate at the spool, cut last](ideas/p3-terminate-at-the-spool-cut-last.md)

The XH end is made on the free end of the ribbon while it is still on the spool, whose inner end is wired through a slip ring so the rest of the spool is a test lead. A belt feed pushes the end to a beam at a work clamp on an X slide; it is trimmed by the guillotine at the clamp face, stripped whole (p7) and split, and each conductor is crimped upright at a lift-once station (the SN on its side, p1c, or the fin from below, p1d), with the slip ring reading identity at the end of every wing curl and the whole spool anchoring the proof pull. Single-ribbon ends are gang-inserted from a housing tube and tested pin to pin through the spool; then a belt carriage clips the ribbon behind the housing and pulls the loom length out along a rail, and the guillotine cut frees it and squares the next end.

- contacts: either loose or strip · steel: any of several · meeting: die head brought to a still conductor.
- **Combines:** [hand-tool-as-press/a3](../hand-tool-as-press/summary.md).
- **Automates:** cut, split, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Spool changes (about three per five units), housing tubes, loading posts, clipping half-housed ends into the partner nest, J4/J7 insertion at a jig, labelling, every far end after the cut. About 16 attended minutes a unit; the 4P run makes five units of 4P ends in ~5-6 h alone.
- **Major unresolved problems:**
  - Whether the BNTECHGO spool's inner end is reachable, or each spool needs a rewind
  - Spool curl off a small hub (a 40 mm free end rises 3-15 mm off a 25 mm hub radius)
  - Machine web splitting on silicone
  - The puller's clip on silicone at a few newtons
  - Half-housed ends travelling in a bin
  - The lift-once station's own open problems (a and a 30-35 mm split, or made steel)

### [p3b — Ribbon AMS: the whole unit from five spools](ideas/p3b-ribbon-ams-whole-unit.md)

Five spools (5P, 4P-L, 3P-a on a left lane; 4P-R, 3P-b on a right lane), each with its own belt feed, merge AMS-style so a pair's two ribbons meet edge to edge at a wide work clamp, each on its own slip ring. Each ribbon is stripped on its own, both are split and crimped at p3's lift-once station with identity through both spools, gang-housed, tested through both spools, pulled out together by the puller and cut together, so pairs are equal length by construction. The machine works through the loom list and houses 8 of 10 housings; J4 and J7 leave in parking combs for the person.

- contacts: either loose or strip · steel: any of several · meeting: die head brought to a still conductor.
- **Branch of** p3.
- **Automates:** cut, split, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Loading five spools and five housing tubes, loading posts, inserting J4's and J7's 14 contacts by hand, labelling, far ends. About 14 attended minutes a unit.
- **Major unresolved problems:**
  - Merging and retracting floppy flat silicone ribbon is untested
  - Machine size: five spools and two lanes for 53 crimps a unit
  - Per-loom fan combs need an indexing holder
  - The lift finger at the seam between two ribbons
  - Everything unresolved in p3

### [p4 — The person presents, the machine takes](ideas/p4-person-presents-machine-takes.md)

A shoebox station with a funnel: the person pokes one square-cut conductor in until its tip meets a hard stop and breaks a beam, and a soft clamp (its stop sets a 30 % jacket squeeze) takes it. V-jaws strip 2.4 mm while the clamp pulls back; then either a strip-fed shuttle presents a pre-fed contact whose carrier is the lead-in's floor (the crimp leaves upward after the tab shears), or an SN-2549 lying so its jaws close normal to the ribbon's plane holds a cut-free contact at wing touch with a blade in its neck. The clamp feeds forward to a hard stop corrected by the camera's bare-length reading, the crimp is made, and a 15-20 N pull goes through the box with the dies open; lights show the next conductor and its cavity, and the person inserts contact k-1 while the machine works on k.

- contacts: either loose or strip · steel: any of several · meeting: the person presents, the machine takes.
- **Combines:** [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [terminal-supply/x1](../terminal-supply/summary.md).
- **Automates:** strip, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cutting square, peeling, presenting every conductor, inserting every contact, labelling. With one head the person is present ~54 min a unit at a 40 s cycle, so it saves no minutes; p4b is where they fall.
- **Major unresolved problems:**
  - Clamp-and-pull stripping may stretch silicone and walk the strip line
  - Strands splaying on the barrel's rear edge during axial entry
  - One head saves minutes only if its cycle beats the ~31 s of a hand strip-crimp-insert

### [p4b — Two heads, one person: the person's pace sets the rhythm](ideas/p4b-two-heads-one-person.md)

Two mirror-image heads flank a sensing insertion nest on one plate. Each head is a funnel ending at a grounded steel tip stop (which reads the conductor's identity through the far end before anything is cut), a soft clamp, strip jaws, and an SN-2549 on its side in a cradle with a pusher and load cell, fed loose kit contacts by a revolver and closing only to wing touch; the camera sets depth. Odd conductors go to A, even to B; the person presents k+1 to one head while the other crimps, then lifts out the finished crimp and seats it with a lever on i5's header nest, whose post names the cavity. With a 20-35 s head cycle the person's present-and-insert pace sets the rhythm.

- contacts: loose kit contacts · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes.
- **Branch of** p4.
- **Combines:** [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [hand-tool-as-press/a2b](../hand-tool-as-press/summary.md), [borrowed-machines/b2b](../borrowed-machines/summary.md), [into-the-housing/i5](../into-the-housing/summary.md).
- **Automates:** strip, place contact on conductor, crimp, verify crimp, verify insertion and pin order.
- **What the person still does:** Cut and peel, present each conductor, insert each contact with the lever, fill the revolvers, label. Attended ~28-39 min a unit against ~46 by hand.
- **Major unresolved problems:**
  - Whether a 20-35 s head cycle including strip and contact drop is reachable (at 45 s the person waits 6-12 s per conductor)
  - Clamp-and-pull stripping of silicone, twice
  - Kit contacts dropping through a revolver, twice
  - The contact's neck for a blade the tips must not reach with camera depth (0.70-0.90 mm)
  - Bench width within one person's reach

### [p5 — Camshaft: one revolution per conductor (B-drop tooling, stops and a soft loop)](ideas/p5-camshaft-one-revolution-per-conductor.md)

One gearmotor or planetary stepper turns one shaft once per conductor, ~40 s: printed face cams drive the presser, a V-fork rising from below, strip jaws and pull, the lay-in finger, a revolver pawl that sets the next cut-free contact on a stepped fin, and a hook for a pull through the box. A steel eccentric drives the punch onto the fin until stop blocks in a short steel loop meet; the outer frame is allowed to be springy (5-10 kN/mm), so the margin that guarantees reaching the stops costs only 1.05-1.4x the crimp and a doubled contact is capped at 3.9-5.4 kN, with no preloaded stack. The cassette rides a rail whose printed rack is the escapement, with skip and end bumps as the program.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Combines:** [hand-tool-as-press/a4](../hand-tool-as-press/summary.md), [hand-tool-as-press/a2b](../hand-tool-as-press/summary.md).
- **Automates:** strip, supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** As p1 at stage 3: cut, peel, load and trim cassettes, load the revolver with cut-free contacts, insert (or bench C), label.
- **Major unresolved problems:**
  - The die profile (punch and stepped fin): where the steel comes from
  - The fin and a cut-free contact supply (as p1 B-drop)
  - Set in waiting conductors from the presser; a 25-30 mm split
  - The strip-pull cam must allow for silicone's stretch
  - Accumulated printed-rack error over nine teeth against the fork's capture

### [p5b — The camshaft squeezes an SN-2549 lying on its side](ideas/p5b-camshaft-squeezes-the-hand-tool.md)

One self-locking 12 V worm gearmotor with an AS5600 turns one shaft per conductor, 40-60 s: an index cam advances the cassette's rack, a lift cam raises k by a + 2.7 mm, a post wheel presents the next contact at nest height, and a Y cam shuttles an SN-2549 lying on its side (jaws closing normal to the row, crimps upright) between the post and k. The squeeze lobe dwells just short of wing touch while the contact is picked and slid onto k, pauses at the end of the curl for an identity read, then pushes the handle through a 275 N spring link to complete the ratchet; a pawl switch must see release at 250-255° or the shaft stops by angle before the Y and lift cams act. A 20 N spring pull through the box, then cams lower k and square the crimp; skip and end bumps and an empty post carry J2's empty cavity.

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: die head brought to a still conductor.
- **Branch of** p5.
- **Combines:** [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [terminal-supply/x1](../terminal-supply/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cut, peel, load cassettes (crossings in the loft), trim and strip (bench A or p7), load the post wheel in key order, insert (bench C), label.
- **Major unresolved problems:**
  - The SN-2549's a, handle travel and wing-touch position are unmeasured; a sets a 30-35 mm split
  - Lever and follower geometry for a tool lying on its side, handles across the row
  - The fixed-depth axial chain (±0.21 mm RSS) cannot take a camera correction
  - Retiming means reprinting cams
  - Post-wheel pick repeatability and kit-contact grip on a post
  - Fixed crimp height and insulation step of the SN on silicone

### [p5c — The camshaft turns a knee: one motor, one turn per conductor, crimp height from geometry](ideas/p5c-camshaft-turns-a-knee.md)

p5's one-shaft timing diagram drives p1d's station: cams index the cassette's rack, lift k 3.5 mm, slide the open contact onto k from a two-tier post bar, raise the fin through k's slot and slide the gate wedge in, and a knee lobe carries the knee joint through straight onto a stop, so the printed lobe's error never reaches crimp height (0.2 mm off straight is 1-3 µm). The shaft stops by angle at the end of the curl while the steel C reads identity, re-touches for height on an indicator, pulls 20 N through the box, and squares k back into the row. A 12 V self-locking worm gearmotor through a ~5:1 belt drives it; the knee needs 0.25-1.9 N·m peak plus 0.1-0.3 for friction, and the printed frame carries only the knee's 60-160 N input.

- contacts: either loose or strip · steel: made dies (EDM, machined, laser-cut) · meeting: conductor brought to a fixed die.
- **Branch of** p5.
- **Combines:** [force-and-form/f3](../force-and-form/summary.md), [force-and-form/f7](../force-and-form/summary.md), [force-and-form/f8](../force-and-form/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cut; strip the webbed end with p7's lever; peel; load the cassette (crossings in the loft); load the post bar in key order; insert (or bench C); label. About 40-44 attended minutes a unit; 35-53 minutes of shaft time.
- **Major unresolved problems:**
  - Everything p1d leaves open: the steel, the contact's neck, tip wander against 0.56-1.42 mm of fin clearance, the insulation crimp at a fixed step, gate and fin-slide wear
  - Fixed depth ±0.21 mm plus 0.05-0.16 mm of fan recession unless the Y cam gives way to a stepper (p5c-Y)
  - Retiming means reprinting cams
  - The proof-pull reaction through the cassette clamp

### [p6 — The spool-end bench that grows (stage 0 with no motor; stage 1 in two forms)](ideas/p6-spool-end-bench-that-grows.md)

Stage 0 has no motor: three reels behind the bench (rewound once, if needed, onto printed 80 mm-hub-radius reels through a roller straightener, the inner end crimped into an XH socket in the hub), a channel clamp at the bench edge whose face guides the flush cutters, a test board of real XH headers, and a length rail with pegs. The person makes the XH end by hand on the reel's free end, plugs the housing onto the test board and a flying lead into the hub socket for pin order, opens and shorts before the loom exists, draws the ribbon by a grip behind the housing to its peg, and cuts at the clamp face, which squares the next end. Motors then join the same clamp in the order Derek wants: stage 1 is a powered crimp, either an SN-2549 on its side (lift 8.7-14.7 mm) or p1d's fin station (lift 3.5 mm), with identity through the hub at every crimp and the whole reel anchoring the pull, and stages 0-1 double as the rig to qualify steel sources and the insulation window against a JST reference lead; then steppers on the same screws with posts, strip in the pose (or p7), a puller, guillotine and gang insertion, and finally a split station.

- contacts: either loose or strip · steel: any of several · meeting: die head brought to a still conductor · usable without a motor.
- **Combines:** [hand-tool-as-press/a3](../hand-tool-as-press/summary.md), [hand-tool-as-press/a6](../hand-tool-as-press/summary.md), [terminal-supply/x1](../terminal-supply/summary.md), [into-the-housing/i5](../into-the-housing/summary.md), [change-the-question/c5](../change-the-question/summary.md), [ribbon-as-pallet/a7](../ribbon-as-pallet/summary.md), [force-and-form/f6](../force-and-form/summary.md), [force-and-form/f7](../force-and-form/summary.md).
- **Automates:** cut, split, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Stage 0: everything by hand at the clamp plus a rewind once per spool (~51 attended min/unit vs ~46 today). Stage 1: split, strip, index and lift, place contacts, knob to the light, pedal, insert (~61). Stage 2: split, strip, load posts, insert (~40). Stage 3: split, posts, insert (~33). Stage 4: split, posts, pairs at the partner nest, J4/J7 (~24). Stage 5: posts, housing tubes, reels, pairs, J4/J7, labels (~15).
- **Major unresolved problems:**
  - Whether the spool's inner end is reachable, and what the rewind costs
  - Stage 1's form: 1-SN depends on a and asks for a 30-35 mm split and squaring; 1-fin depends on made steel
  - Pairs travel half-housed; the partner nest and J4/J7 need the person at every stage
  - Bench space: a ~650 mm rail along the bench front, three reels behind
  - Stages 0 and 1 cost minutes (they buy recovery, testing, a record and measurements)
  - Whether a roller straightener takes curl out of silicone ribbon without marking or twisting it

### [p6b — The reel end docks on a strip: every contact placed at once, a bought applicator crimps](ideas/p6b-reel-end-docks-on-a-strip.md)

At p6's reel clamp the flush-cut webbed end is fed to a grounded tip stop (touch-off through the hub socket), stripped whole by p7's razors with toothed pads, zipped apart from the slug's gaps (a7), and fanned to 7.1 mm strip pitch by an equal-path fan whose inner grooves carry humps so every tip recedes the same amount. The clamp and fan block drop onto three balls over a strip segment on a fixed track, so every conductor settles into every open contact at once, and the hub socket reads each conductor to the grounded carrier before any force. The docked row indexes through a bought OTP applicator with its feed removed, driven by a 3-4 mm eccentric on a small planetary stepper with a pilot in the carrier slot; then a 20 N pull through each box, a shear comb, gang insertion onto a real wafer, a pin-to-pin test through the reel, and the puller draws the loom off before the cut.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: pallets dock (all contacts placed at once).
- **Branch of** p6.
- **Combines:** [ribbon-as-pallet/a2e](../ribbon-as-pallet/summary.md), [ribbon-as-pallet/a7](../ribbon-as-pallet/summary.md), [ribbon-as-pallet/a6](../ribbon-as-pallet/summary.md), [force-and-form/f2c](../force-and-form/summary.md), [borrowed-machines/b1b](../borrowed-machines/summary.md).
- **Automates:** cut, split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** The rewind once per spool; mounting reels and the contact reel; the housing magazine; four pair events a unit at the partner nest including 5 crossing contacts for J4/J7 by hand; labels; every far end. About 12 attended minutes a unit; a 4P reel run ~3.5 h alone. Branch p6b-fed (force-and-form f2c at the reel) presents one conductor at a time with depth corrected from p7's frame.
- **Major unresolved problems:**
  - p7's flank tear and slug push
  - Closing the equal-path fan block over tine-fanned conductors without a conductor riding up; the humps leave vertical set
  - Parted length 22-33 mm at 7.1 mm pitch (Derek's split-length question)
  - The OTP applicator: its tooling, which parts unbolt, the pilot pocket, shut height; no Prime listing
  - Docking capture depends on whether the clone drawings' barrel widths are inside or outside dimensions (0.14-0.54 mm half-gap)
  - A redo costs the whole parted end, ~35 mm of reel
  - J4 and J7 crossings stay with the person

### [p7 — Strip before split: one stroke takes the whole end's slug while the web still holds the pitch](ideas/p7-strip-before-split.md)

At a channel clamp the webbed ribbon end is flush-cut at the clamp face. Two single-edge razor blades close from above and below across the whole width 2.4 mm from the cut, slicing 2-4 mm along their edges as they close, and stop on steel stops at strand radius + 0.2-0.3 mm from the conductors' centre plane; toothed pads bite the slug's top and bottom, and the carriage (which carries the floor ahead of the strip line, a split floor) slides 3-4 mm forward and pushes the whole slug (every jacket plus the webs, ~20-75 N for 3P-5P) off the strands. One backlit camera frame measures every bare length and brush on one line, and the split then starts from the open gap the slug left. A lever version with shim stops is a hand tool for stage 0.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [ribbon-as-pallet/a7](../ribbon-as-pallet/summary.md).
- **Automates:** cut, strip.
- **What the person still does:** With the station: the split itself (until a split station exists), then crimping and insertion elsewhere. As a hand lever: the squeeze and the push.
- **Major unresolved problems:**
  - How silicone tears across flanks and web from two straight scores, and at what pull; the hand trial wants running with and without pads
  - Pads must grip the jacket harder than it grips the strands (smooth pads 32-132 N a side on a 5P, toothed 6-25 N)
  - Strand splay at bare tips through splitting and fanning (splitter nose ≤0.9 mm between bundles)
  - The strand bundle's offset in its jacket sets the minimum ligament; one cross-section photo measures it
  - The web's neck thickness in the valley; the split floor's joint marking the ribbon

## Combinations with other explorers

- p1d = p1c's lift-once order × force-and-form's steel C with a knee (f3, f4), fin anvil from ground stock (f7), narrow stepped crimper and lance relief (f8), with terminal-supply a4's post-held contacts on a two-tier post bar (force-and-form's FP1 pairing, developed here)
- p5c = p5's one-shaft timing × p1d's station, the knee lobe carrying the joint through straight (force-and-form's FP2 pairing, from its f3)
- p6b = p6's reel and cut-last order × p7's whole-end strip × ribbon-as-pallet a2e (docking onto a strip through a feedless applicator), a7 (zip stopped at the clamp face), a6 (closing block, real-wafer nest) and an equal-path fan; its branch p6b-fed is force-and-form f2c's applicator station at the reel (force-and-form's FP3)
- p1c = p1 cassette × hand-tool-as-press a3 (SN-2549 module closing its own force loop, lying on its side or over an on-edge fixture so crimps are upright) + a1 (neck blade) + terminal-supply a4/x1 (post-held contacts)
- p4b = p4 division of labor × hand-tool-as-press a1 squeezer + a2b revolver, taking borrowed-machines b2b's station as one head and into-the-housing i5's sensing header between two heads
- p5b = p5 camshaft × hand-tool-as-press a1 squeezer, with terminal-supply x1's post pick made Z-free by a post wheel on the station line; hand-tool-as-press a1b (pawl out) as its branch
- p3 station (C1) = p3 spool, cut last × hand-tool-as-press a3 travelling module, or × p1d's fixed fin station; the slip ring is the far-end electrode during every crimp
- p6 stages 0-1 × force-and-form f6 (insulation-window sweep) and f7 (four steel sources): the reel clamp as a qualification rig, every sample tested through the hub and cheap to discard (force-and-form's FP5)
- p7 × force-and-form f5b/f9 gangs: one stroke puts every insulation edge of a row on one line; half-row spreading then moves outer edges back 0.02-0.51 mm by row length (force-and-form's FP4)
- p6 stage 0 × hand-tool-as-press a6 / borrowed-machines b2b / terminal-supply x1: hand stations work unchanged at the reel clamp, the hub socket replacing their per-loom far-end fixture
- p6 test board = into-the-housing i5 / change-the-question real-wafer test, read through the reel
- p1 / p1c / p1d / p2 × ribbon-as-pallet a6 far-end pogo block riding on the cassette or clamp carriage: identity at every crimp, pin-to-pin header test
- p6 stage 4 puller × ribbon-as-pallet a3's fold round a bar: a 3 N clip becomes a 14-69 N grip on silicone
- p6 stage 4+ × change-the-question c5: the same bench makes stock ends of standard length if bins of ends suit Derek better

## Transferable mechanisms

- Lift once, and do everything to conductor k in that pose (trim, strip, measure, place, crimp, pull), then square it back: the waiting conductors keep no set, and k's own set never enters its own crimp
- The closing direction of any crimp head is the contact's floor normal: a head working a flat row must close normal to the row, and only the part under the conductor (a fin anvil) needs to pass through the row plane, so the lift is set by die geometry (3.5 mm with a fin, a + 2.7 mm with a hand tool)
- A fin anvil rising from below through the lifted conductor's own empty slot, stepped 1.45 / 1.88 mm, with a tip comb ≥ ~4.7 mm behind the tips holding the neighbours beside it
- Place the contact on the conductor first (from a post, barrels fully open), then close the tool once around both; a hand tool stopped at wing touch, short of its first ratchet tooth, keeps the insulation bore open if it must hold the contact first
- Take identity where copper is touched anyway (a grounded trim blade, the tool at the end of the wing curl, a grounded tip stop at presentation, the anvil at lay-in), never from a stop that fights a camera-set depth
- With stop blocks, a soft outer loop is the design: the margin to reach the stops costs k x m, a 5-10 kN/mm loop pays 1.05-1.4x the crimp and caps a doubled contact at 3.9-5.4 kN; the load cell goes under the whole lower die, outside the stop loop, or foil gauges go on steel
- A knee or crank driven through its geometric bottom makes crimp height a property of link length (x²/L); cams and printed parts only have to carry the joint past it
- Every clamp that reacts a proof pull has a hard stop setting a 15-30 % jacket squeeze over 5-20 mm, or the copper is anchored by the whole reel
- Push a silicone slug through pads that bite, not through a cut face, and slice the blades along their edges as they close
- Straight razor blades on steel stops across a webbed ribbon: a whole-end strip whose depth is mechanical and which ignores conductor pitch error; the slug's gap starts the split
- An equal-path fan (humps on the inner grooves) keeps a straight strip line straight after fanning, so every conductor can dock at once
- The reel's inner end in a hub socket as a test lead: plugged only while the reel stands still it never twists; one connection serves 5-11 units of looms and replaces every per-loom far-end fixture
- Terminate first, cut last: the cut that frees one loom squares the next end, and a redo costs reel, never a loom
- Pull the loom off by the ribbon behind the housing along a rail; the housing is never the handle
- Rewind once onto an 80 mm hub radius through a roller straightener: no new set, curl removed, inner end brought out
- The reel clamp as a qualification rig for steel and settings: every sample tested, pulled against the whole reel, and cheap to discard
- Two slow, cheap heads alternating make the person's own present-and-insert pace the rhythm
- A camshaft whose timing diagram is the procedure; the carrier's printed rack as escapement and program, with skip and end bumps; stop the shaft by angle for checks
- A ratcheting hand tool driven by a machine needs a release check before anything moves the conductor it may still be clamping
- The cassette as the only reference benches share; key k = cavity k; crossings made in a loft at loading; printed blanks for empty cavities
- Stages that carry the interface the next motor takes over: knob-turned lead screws become stepper screws, a peg becomes a puller

## Key findings

- [calc wave3 §1] Lift for an upright crimp from a flat 2.5 mm row: a fin from below needs 3.5 mm and leaves 0-0.77 mm of rise at 20 mm free and 0-0.05 mm at 25 mm; an SN-2549 closing normal to the row needs a + 2.7 = 8.7-14.7 mm and leaves 0-8.2 mm at 30 mm free and 0-5.7 mm at 35 mm, so every SN-based lift-once station wants a 30-35 mm split and a squaring push per crimp. Hung tip-down closing along the row, the SN rolls every crimp 90° (hand-tool-as-press a3; into-the-housing), which is why every SN head in this view now lies on its side
- [calc wave3 §2] Fin clearance to neighbours at 2.5 mm pitch: 0.92 mm (1.45 mm conductor step vs an uncrimped jacket), 0.71 mm (1.88 mm insulation step), 1.02 and 0.56 mm against crimped neighbours; fin travel ~4.8 mm from rest; the tip comb must stand ≥ ~4.7 mm behind the tip line or its pins (0.93 mm half-gap) collide with the fin's insulation step (0.94 mm half-width). Laminated 1095 shim gives 1.448 and 1.880 mm; a 1.45 mm free-standing B-drop fin 9-10 mm tall buckles at 5.1-6.3 kN
- [calc wave3 §3] A knee's bottom is geometry: 0.2 mm short of straight is 1.3-2.7 µm on 15-30 mm links; what moves height is loop stretch, ±1.5-6 µm at 100-200 kN/mm
- [calc wave3 §4] Stops under an eccentric: frame load at bottom = F + k m; a 40 kN/mm loop pays 1.3-2.6x the crimp for a 0.02-0.10 mm margin and puts 14.4 kN into a doubled contact, a 5-10 kN/mm loop 1.05-1.4x and 3.9-5.4 kN. A 500 kg button cell inside the stop loop adds ±3-12 µm of height scatter
- [calc wave3 §5] Pads that push a slug also press the jacket onto the strands: net drive 2N(μ_pad − μ_js). For a 5P at 3-15 N tear per conductor, smooth TPU needs 32-132 N a side, grippy TPU 11-44 N, toothed pads 6-25 N [assumed μ]
- [calc wave3 §6] p1d: 55-76 s a key, J1 8-11 min, a unit 49-67 min of machine time; person 40-44 min a unit against ~46 by hand on the same library. The crimp is automated but cutting, peeling, laying in and inserting remain most of the person's time. p5c: 35-53 min of shaft time a unit
- [calc wave3 §7] p5b's squeeze lobe does 1.8-2.2 J at the handle against 0.13-0.48 J of crimp work, so its 2.1-3.2 N·m motor sizing is conservative; p5c's knee lobe needs 0.25-1.9 N·m plus 0.1-0.3 (force-and-form calc), inside a Prime 3.9 N·m self-locking gearmotor ($26.99)
- [calc wave2 §3] Axial chain at a lift-once station: ±0.21 mm RSS with strip in pose and a neck blade, ±0.07-0.09 mm with a camera bare-length correction, ±0.22 mm for touch-off on strand tips (the wrong end). With camera depth the neck blade must be clear of the tips, which needs a 0.70-0.90 mm neck (force-and-form)
- [calc wave2 §2] Spool curl: off a 25 mm hub radius a 40 mm free end rises 3.3-14.6 mm; a rewind reel with an 80 mm hub radius adds no set
- [calc wave2 §4, §6] Two alternating heads make the person's present-and-insert pace the rhythm (28-39 attended min a unit vs ~46); p6's stages cost 51/61 min at stages 0-1 and fall to 40/33/24/15 from stage 2 (wave2.out.txt re-run so the stored table matches)
- [calc P3 §1, §11, §12] An equal-path fan needs a 5.1 mm hump over 21.4 mm for a 5P's centre at 7.1 mm pitch; docking with grips in the carrier's end slots uses ~55 contacts a unit; a redo at the reel with docking costs the whole parted end, ~37 mm of reel a unit at a 2 % crimp failure rate
- [calc recovery_length] Cut-first orders with a 12 mm reserve scrap ~35 looms over the program at a 10 % bad-crimp rate; terminating on the reel scraps none
- [Prime, observed 2026-09-28] Parts confirmed for these ideas include: iCrimp SN-2549 $22.29; NEMA 17 with integrated Tr8×2 $27.99; MGN9 $16.12 and MGN12 $20.49 rails; Greartisan 12 V self-locking worm gearmotor 3.9 N·m $26.99; StepperOnline NEMA 17 26.85:1 planetary $41.91; 0.001 mm indicator $52.99; 1095 blue-tempered shim assortment $53.39; pin gauges to 1.448 mm $45.58; BF350 gauges $6.99; 6-circuit slip ring $9.99; P75 pogo pins $6.49; single-edge razors $12.90/100. No Prime listing for a NEMA 17 worm-gear stepper, an OTP XH applicator or knife set, XH contacts on strip, or hardened h6 dowels

## Where this view still had trouble

- A hand tool that stays cheap and on-hand yet crimps upright from a flat row with a small lift: every SN-based variant found either rolls the crimp (tip-down along the row) or needs 8.7-14.7 mm of lift and a 30-35 mm split; only made steel (a fin from below) or docking into an applicator gets the lift down
- J4 and J7 crossings between two ribbons made by a machine in a gang-insertion order: only p2's per-conductor bow-and-push reaches them, and it is undemonstrated on silicone; every other arrangement hands 5-14 crossing contacts a unit back to the person
- Machine splitting of the silicone web without a person peeling: every automated split (razor comb in the valleys, zip from p7's slug gap) rests on the untested tear and the unmeasured web neck
- Taking the person's minutes below ~40 a unit for cut looms: with the crimp automated, cutting, peeling, laying into cassettes and inserting still dominate; only the reel-based orders (p3, p3b, p6 stage 4+, p6b) get to 12-24 minutes, and they bring batching and half-housed pairs
- Feeding loose kit contacts automatically in the right orientation: every arrangement here loads posts or revolvers by hand in key order; a bowl or scoop singulator was named but not developed
- Setting the insulation crimp on soft silicone at a fixed crimper step: no variant of this view makes insulation height an independent setting except by borrowing force-and-form f6's separate blade
- Recovering one bad crimp at a cut loom without cutting back the whole end: no single-conductor re-crimp was found, so recovery is always ~6 mm of loom (or reel)
- Making both ribbons of a pair together on the reel without a person at the partner nest: only p3b's two merging lanes do it, and merging floppy flat ribbon is the least certain mechanism in this view

## Questions for Derek

- How deep is the SN-2549's anvil jaw half below its XH nest floor, over ~20 mm of jaw on the pivot side (a)? It sets the lift (a + 2.7 mm) for every station that uses the tool lying on its side
- Would you crimp one contact with the SN-2549 held tip-down over a flat row of conductors, jaws closing along the row, and photograph it end-on? It shows the 90° roll by looking
- Would you photograph one kit contact side-on and end-on under the ELP camera? Side-on gives the neck between box and conductor barrel (a fin needs 0.34-0.74 mm, a neck blade clear of the tips 0.70-0.90 mm); end-on gives the insulation barrel floor's inner width (whether the first ratchet tooth pinches the bore)
- Would you pull one crimped conductor held in a TPU clamp at 20 N through the box with a luggage scale? Does the copper creep back inside the jacket?
- Would you try two single-edge razors squeezed across a fresh 5P end with shims as stops, 2.4 mm from the cut, then pushed, once with and once without toothed pads on the slug? Does the slug come off whole, or do the cut caps roll over the edges?
- What does the SN-2549's handle need at the moment its ratchet releases, on a bathroom scale (against p5b's 275 N link)?
- How long may the split behind the housing be: 20, 25, 30 or 35 mm? A fin from below wants 20-25 mm; an SN lying on its side wants 30-35 mm
- Would made dies (a ground-stock or laminated-shim fin, an EDM or knife-set crimper) be welcome for p1d/p5c, or should every crimp head stay a bought hand tool?
- What is the BNTECHGO spool's hub diameter, can its inner end be reached, and is ribbon from near the hub visibly curled?
- Would making each XH end on the reel, tested pin to pin through the reel before it is cut, suit how the bench is used (a rewind once per spool, ~5 more attended minutes a unit, a bad crimp costing 6 mm of reel)?
- Would J7's GND riding the 3P with CLO/CHI, and the 5P's fifth conductor being the trimmed one, be acceptable? It makes J7 straight
- Would you hold finished looms ahead of units (one reel's life of one ribbon type), or should the machine work one unit at a time?
- How much shorter than its cut length may a loom end up, and which end of a loom do you make first today?
- Would you switch the machines to SXH-001T-P0.6 on cut strip, keeping kit contacts for hand repair? Every lift-once station takes either on posts; only p6b needs strip
- Would a second (and third) dedicated SN-2549 be welcome for a squeezer module or two alternating heads (p4b)?
