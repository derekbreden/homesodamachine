# borrowed-machines

*Somebody already mass-produces most of this, for another purpose.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [b1 — The bought press and applicator, operated by a printer-axis ribbon shuttle](ideas/b1-press-and-applicator-with-shuttle.md)

A Chinese 1.5-2 t mute terminal press with an OTP side-feed XH applicator set to post-feed (the WERI manual's 'automatic' default), so the anvil is empty at rest. The ribbon end sits in a printed cassette, split and stripped, with every conductor but one folded back as a flat band; a valley-tine fork lays the target conductor over the anvil ~4.6 mm up, and one relay-fired stroke slides the contact in, a spring V-finger on the ram seats the conductor, and the crimpers form both barrels and cut the tab. The camera first looks at the contact waiting one pitch upstream; after the stroke the shuttle withdraws, a neck fork takes a 20 N proof pull, and far-end continuity names the conductor.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert.
- **What the person still does:** Cutting and loading cassettes, the fold lid, splitting and stripping unless a prep station is built, insertion unless the extension is built, reel changes and crimp height by sample; ~27 attended min/unit with hand insertion, 22 with the extension, against 46 today.
- **Major unresolved problems:**
  - Applicator geometry (tooling half-width, tip-to-face depth, room for the ram finger) sets the 8-15 mm split
  - Whether the OTP unit has both feed-cam positions and where post-feed finishes
  - Whether a ram finger seats a raised conductor cleanly in a ~0.5 s stroke; nothing is seen between lay-in and crimp
  - Genuine SXH wings leave +/-0.08-0.18 mm of lateral capture, so the V's setting is the whole margin
  - No Prime route for press, applicator or reel; 50 kg freight; guarding a relay-fired press

### [b1b — The OTP applicator in a slow crank press built into the idle 12-ton shop press](ideas/b1b-applicator-in-slow-crank-press.md)

The same applicator, in pre-feed, on the bed of the VEVOR 12-ton shop press, driven by a crank (throw = half the applicator's 30 or 40 mm stroke) from Derek's NEMA 23 through a Prime 10:1 planetary held to its 10 N*m rating, with a two-disc DIN 2093 A35.5 stack in the rod as the force cap and switch. The camera looks at the contact alone on the anvil, the fork lays the conductor in, a gate checks picture and far-end continuity, the crank crimps (19-39 HX711 samples through compaction), and in the dwell after bottom dead centre the crimp is withdrawn and pulled against a neck fork before the feed moves. A bad contact gets a reject turn: an empty crimp and a timed air puff into a reject cup.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** b1.
- **Combines:** [terminal-supply/a1](../terminal-supply/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** As b1 (cassette loading, fold lid, prep, insertion, reels, sample crimp height), plus setting shut height once and emptying the reject cup. Stage 0, the jack test, is a hand-pumped crimper and measuring bench in the first week.
- **Major unresolved problems:**
  - OTP shut height, stroke, ram head, spring loads and feed timing unpublished (the jack test measures them)
  - Laser-cut crank disc and keyway on a 20 mm shaft without a lathe
  - Shop-press bed flatness and applicator clamping
  - Whether a crushed empty contact leaves the anvil on a puff
  - Heavy disc springs not on Prime; crimpers at ~5 kN on a doubled contact; guarding

### [b1c — One shaft: the applicator crank also turns the cams that lay in, withdraw and pull](ideas/b1c-one-shaft-applicator-press.md)

b1b's crankshaft, turned once per conductor in 30-40 s by a NEMA 23 on a self-locking worm, carries printed face cams: tines down 0-10 deg, fork lays in 10-50 deg, foot seats 50-58 deg, and a switch-cam gate at 60 deg, before the feed finger's downstroke retract band (75-94 deg), so a failed gate simply reverses the shaft to 0 with nothing done. The crimp runs 140-185 deg, a cam draws the crimp back to a fixed catch on the box roof and a spring gives a 20 N proof pull with an over-travel switch, and only then (~266 deg) does the applicator feed. A bad contact gets a reject turn with the band moved aside and a cam-timed puff.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Branch of** b1b.
- **Combines:** [procedure-is-the-machine/p5](../procedure-is-the-machine/summary.md), [terminal-supply/a1](../terminal-supply/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** As b1b: cassette loading and folding, insertion, reels, sample crimp height, the reject cup.
- **Major unresolved problems:**
  - Squeezing the 180 deg fork swing into 40 deg of shaft needs a ~60 mm cam track with a 4:1 sector, or a servo fork permitted by a shaft switch
  - Cam phasing depends on the measured feed band and the applicator's stroke
  - Whether the feed lever really follows ram height
  - The fixed catch's 0.4-0.6 mm height band on silicone
  - Clearance under the ram, cam wear, guarding a shaft that moves ram, fork and slide

### [b2 — The ratchet hand crimper in a frame, closed by an actuator, fed from the strip](ideas/b2-hand-crimper-in-a-frame.md)

A dedicated $22 SN-2549 stands on edge in a saddle, closed by a 12 V actuator (Justech 1,500 N with an AS5600 on the pivot, or a PA-01-POT) through a spring link that caps die force near 3.2 kN and signals 'closed by force'. In front, a pawl on a flat run feeds an SXH strip and a tapered pin fixes it; a 0.64 mm post enters the lead contact's box, the tab shears on a steel land at its root, the post's silhouette is measured, and the post carries the contact barrels first into the open jaws to a jaw-face fiducial. The actuator closes to the captive click, a feeler-leaf flap drops into the neck, the conductor comes in through a funnel to the blade, and the tool crimps.

- contacts: carrier strip · steel: SN-2549 or similar hand-tool dies · meeting: conductor brought to a fixed die.
- **Combines:** [terminal-supply/a6](../terminal-supply/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Presenting each conductor (by hand as in b2b, or by b1's shuttle and band), splitting and stripping unless b6/b7 are added, loading strips, sample crimp height, insertion.
- **Major unresolved problems:**
  - SN-2549 crimp quality on 1.7 mm silicone over 60 x 0.08 strands untested
  - Whether the jaws bottom face to face; if not, crimp height follows force
  - Carrier geometry (tab, pitch, pilot position) unmeasured
  - Whether the neck takes a 0.3-0.4 mm blade, and whether the nest's front face stops the box
  - Whether track, drop section, post head and flap fit in front of the jaw face

### [b2b — The pedal-less hand station: the person pokes, the machine holds the contact, keeps the order and crimps](ideas/b2b-pedal-less-hand-station.md)

A bench plate with a die-hole strip nozzle (b7), b2's crimp station with a TPU soft clamp behind its funnel, and a sensing XH-header nest with lit cavities (i5); the loom's raw far end sits in a pogo block so every conductor is a wire to the ESP32, and an LED strip lights conductor k. Derek pokes conductor k into the nozzle (the tip stop names it), then into the crimp funnel until the strands touch the flap blade; the soft clamp takes it, the tool crimps through the spring link, pulls 20 N and checks continuity, and he lifts the crimp out and inserts it at the lit cavity while the machine places contact k+1. One contact type is held from the first week (kit maker's reel, loose throughout with the post head, genuine BXH then SXH, or b8b's thinning cup).

- contacts: either loose or strip · steel: SN-2549 or similar hand-tool dies · meeting: the person presents, the machine takes.
- **Branch of** b2.
- **Combines:** [procedure-is-the-machine/p4](../procedure-is-the-machine/summary.md), [hand-tool-as-press/a1](../hand-tool-as-press/summary.md), [ribbon-as-pallet/a6](../ribbon-as-pallet/summary.md), [into-the-housing/i5](../into-the-housing/summary.md), [terminal-supply/x1](../terminal-supply/summary.md), [terminal-supply/a6](../terminal-supply/summary.md).
- **Automates:** strip, supply contacts, place contact on conductor, crimp, verify crimp, verify insertion and pin order.
- **What the person still does:** Splitting (by hand or b6's rip board), clipping the far end, poking each conductor twice, lifting out and inserting, loading contacts and housings, labels; ~37 attended min/unit (33 with a rip board) against 46.
- **Major unresolved problems:**
  - SN-2549 crimp quality, jaw bottoming and neck on this ribbon
  - Lifting a crimp out of the open mouth with the tool on edge
  - Pogo pins on a raw cut face over many clip-ins; a skewed cut shorting two pins
  - Everything open in b7's die-hole nozzle
  - Which contact route applies (do kit contacts carry tab stubs?); a person-paced station keeps Derek at the bench

### [b3 — A cheap printer gantry carries a narrow crimp head to a fanned ribbon](ideas/b3-gantry-carries-the-crimp-head.md)

An Ender 3 V3 SE without its hot end holds a ribbon end, split and stripped while it was still flat, in a printed fan fixture at ~4-5 mm pitch, so every tip is the same along-conductor distance from the root. A ~1 kg head on the carriage (a second OTP applicator's punches and anvil in a laser-cut C-frame, closed by a NEMA 17 planetary and a 3 mm crank) picks a contact from a pawl-fed strip, closes to captive and cuts the tab on the anvil's rear edge, drops a neck blade in, and a V-fork on its rear face guides each conductor as the bed slides it into the barrels; then it crimps. A converging comb closes the row to 2.5 mm and the housing is pushed onto all contacts at once, the outermost front landing short only by the housing fan (J1 0.25 mm at 20 mm).

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: die head brought to a still conductor.
- **Combines:** [into-the-housing/i3](../into-the-housing/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Laying each end into the fan fixture (60-90 s), splitting and stripping flat unless b6/b4/p7 feed it, housings, strip, unloading.
- **Major unresolved problems:**
  - Harvesting and aligning applicator punches to ~0.02 mm in a 1 kg head
  - Whether the converging comb closes crimped contacts from 4.35 to 2.5 mm without snagging
  - Fixture loading time
  - Captive position as wing height varies by reel; head stiffness at low mass
  - Insertion force unmeasured

### [b4 — A laser engraver slits the webs and scores the strip line in the cassette](ideas/b4-laser-slits-and-scores.md)

The cassette docks on two pins on the H2C's 455 nm laser module (kit $698/$1,348, not on Prime) or a CO2 engraver ($759.90 Prime). One job scores the crowns top at the reel's strip length Ls to ~60-70 % of the wall, slits each web from the clamp edge only to the score line and to about mid-plane, flips on the pins and repeats underneath, so every precise line is cut while the ribbon is one piece. Off the laser, TPU pads pinch the still-webbed tip and the cassette backs off 3 mm: the whole tip leaves as one comb-shaped slug (~24-65 N for a 5P), then brush and air.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module).
- **Automates:** split, strip.
- **What the person still does:** Cutting, flush-cutting and clamping the end; docking and one flip; pinch, pull and brush (~60-80 s/end, about a hand strip); everything from the contact onward goes to the crimper that receives the cassette.
- **Major unresolved problems:**
  - Silicone under 455 nm: char, residue, depth control on a round surface, untested
  - Neck geometry (repo Open item 5) and whether slits leave both jackets intact
  - Whether each flank tears cleanly from top and bottom scores in a whole-tip pull
  - Ash among 60 strands
  - Person time near a hand strip

### [b4b — Two small diode heads at the station: score and slit in the pose the crimp uses](ideas/b4b-diode-heads-at-the-station.md)

Two fixed-focus 450 nm modules (LASER TREE 10 W optical, $137.17 Prime), one above and one below a slotted steel bed at a station on b1's shuttle rail or at b8/b8b's work clamp, inside a light-tight interlocked box. The shuttle's own X and Y sweep the ribbon under them: crown scores top and bottom in one sweep, then each web slit from both sides from the clamp edge to the score line; TPU pads pinch the webbed tip and the shuttle backs off 3 mm. No dock, no flip, no H2C module swap, and a redo is re-scored in the crimp's own coordinates.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module).
- **Branch of** b4.
- **Automates:** split, strip.
- **What the person still does:** Nothing new at the station beyond the crimper's own cassette loading.
- **Major unresolved problems:**
  - 455 nm on this silicone, untested
  - The lower head's window fouling with falling ash
  - Class 4 enclosure and interlock around a moving shuttle; fume path
  - Whether 5-10 W optical modules score 0.3-0.35 mm of silicone in a few passes

### [b5 — A desktop arm as the operator of the other stations](ideas/b5-desktop-arm-as-operator.md)

A ring of kinematically docked one-step stations (cassette rack, rip board or laser, pinch pull, crimp cell, insertion jig, tester) around a desktop arm. At the cheap tier an SO-101 ($184.99-459.99 on Prime) carries cassettes dock to dock, approaching every dock from above the same way so taught waypoints absorb its backlash (~1.2 mm RSS inside 5 mm lead-ins). At the precise tier a Dobot MG400 (+/-0.05 mm, ~$2,900-3,500) carries terminal-supply's post head: it picks a loose contact, measures it on the post, sets it in an open die, then presents each conductor, Kurabo's pattern with one custom end effector.

- contacts: either loose or strip · steel: any of several · meeting: a general-purpose arm or gantry hand.
- **Combines:** [machine-that-sees-and-learns/v2](../machine-that-sees-and-learns/summary.md), [terminal-supply/a6](../terminal-supply/summary.md).
- **Automates:** supply contacts, place contact on conductor.
- **What the person still does:** Loading ribbon ends into cassettes unless the arm learns it by imitation, taking finished looms off, teaching and correcting the arm.
- **Major unresolved problems:**
  - Managing the 100-600 mm loom tail through docks
  - Whether a learned policy lays silicone ribbon into a channel reliably
  - A ~$200-460 docking arm versus a ~$3k placing arm
  - Whether the MG400, a floating post and a silhouette correction reach ~+/-0.1 mm axial placement
  - Every cheap-tier carrying reason has a cheaper route

### [b6 — Pierce at the root, pull toward the tip: splitting borrowed from zip cord and the sewing machine](ideas/b6-pierce-at-the-root-pull-to-the-tip.md)

A station on the shuttle rail with a stencil-steel needle plate under the ribbon and a guide strip above; a 0.6 mm hardened needle (cut-down sewing needle or 0.025 in music wire) on a servo Z slide that floats +/-0.4 mm in Y drops into the top valley at the split root, slides into the neck and pierces it. The shuttle then draws the cassette back so the needle travels toward the tip, tearing (3-15 N) or, with a scalpel point, cutting (0.2-3 N) the neck, and stops at the strip line, leaving the tip webbed; the ribbon is in tension, the root is where the needle went in, the needle is an electrode, and the rip force is logged. Crown scores to 50-60 % and a pinch then take the whole webbed tip off as one slug; a no-motor hand rip board (~25 s/end) is useful the week it is printed.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Automates:** split, strip.
- **What the person still does:** Loading the cassette (or laying the ribbon and pulling the carriage on the hand board); everything from placing the contact onward.
- **Major unresolved problems:**
  - The neck (repo Open item 5): its height and whether a tear follows it; round needle or edge
  - How far off the valley the floating cone can land and still reach the neck (+/-0.5 mm estimated)
  - Needle-plate slot tight in X and long in Y with the float
  - Fixed-pitch pins on the hand board near a 5P's outer strands
  - Whole-tip flank tear after the split

### [b7 — A bought bench stripper fed one conductor at a time, and the blade geometry it has to have](ideas/b7-borrowed-strip-head-one-conductor.md)

A sensor-triggered bench stripper (used Schleuniger RotaryStrip 2400 class, or a Chinese touch-sensor stripper) beside the crimper: the fork and shuttle push each split conductor's tip into the nozzle, the machine clamps, cuts, pulls and twists, and a backlit frame checks the stub. On this wire two V-blades cut to 0.02 mm of the strands at four points while leaving 0.35 mm at four others, die-hole blades leave an even 0.04-0.19 mm ring, and one orbiting blade needs +/-0.05 mm centring; so the build route is a static die-hole head (0.90-0.94 mm hole, closed to stops, optional twist, an isolated tip stop at the reel's strip length Ls). The same blades in a hand lever with a wired tip-stop sleeve are a motorless version.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Automates:** strip.
- **What the person still does:** Splitting; presenting each conductor at b2b; everything from the contact onward.
- **Major unresolved problems:**
  - Bought strippers on silicone untested; RotaryStrip's rated list omits silicone; used price unknown; no Prime route
  - How deep inside the nozzle a bought machine grips (may push the split to ~12-15 mm)
  - Whether die-hole blades near 0.94 mm are sold
  - Strip length per reel (2.4 mm JST vs 1.6-2.1 mm clone spec)
  - Isolating a bought machine's blades for touch detection

### [b8 — The spool-fed borrowed line: the feed rips the webs, the applicator crimps, the cut frees the loom](ideas/b8-spool-fed-borrowed-line.md)

A 4P spool with its inner end on a 6-circuit slip ring feeds a belt feed, encoder, guillotine and work clamp on an X/Y stage in front of b1b's applicator in the shop press. The belts push the square end 12 mm + Ls past a needle bar, the needles pierce every web, the belts retract 12 mm so the needles rip to the strip line and the root lands on the clamp face; crown blades to 50-60 % and pads strip the still-webbed tip as one slug, a lid folds the four conductors back as a band, and each is crimped through b1b's gates with identity checked through the rest of the spool. A comb runs root to tip twice to take out the fold's set and converges the row to 2.5 mm, an XHP-4 from a tube is pushed on, the end is tested through the spool, and the loom is fed out and cut, squaring the next end.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Combines:** [procedure-is-the-machine/p3](../procedure-is-the-machine/summary.md), [ribbon-as-pallet/a4](../ribbon-as-pallet/summary.md), [change-the-question/c5](../change-the-question/summary.md), [into-the-housing/i3](../into-the-housing/summary.md), [ribbon-as-pallet/a6](../ribbon-as-pallet/summary.md).
- **Automates:** cut, split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Loading and threading a spool (~5 min per 5-7 units of T4), housing tube, bins, reject cup, labels, every far end, and all non-T4 looms (J6 is the next spool type); ~33 attended min/unit with the rest by hand, against 46.
- **Major unresolved problems:**
  - Whether the BNTECHGO spool's inner end is reachable, or each spool needs a rewind
  - Feeding floppy silicone ribbon out and back with belts, slip seen only on the encoder
  - The neck (repo Open item 5); whole-tip flank tear at 50-60 % scores
  - Whether two comb passes straighten the fold's set inside the gang window
  - Loom tail down a ~0.7 m drop tube; moving a feed head under a crank press; pairs and J4/J7 crossings not covered

### [b8b — The flat spool line over a crown: nothing folds, the fresh contacts fall out of the ribbon's plane](ideas/b8b-flat-spool-line-over-a-crown.md)

b8's spool, belt feed, needle rip (here 16 mm) and whole-tip strip feed terminal-supply a2d's station: a strip with every other contact punched out wraps over a steel crown (R 25-30 mm) whose crest land is a knife-set anvil under a hand-sized VEVOR AP-1 arbor press pulled by a stepper to a hard stop, so the next kept contact lies 14.2 mm away and below the plane. After the strip, a comb brought in from the tip side threads the stripped bundles and spreads the conductors from 1.7 mm to the crimp pitch p (2.35-2.80 mm), behind the 5.3-9.2 mm carrier zone; the flat end then slides conductor k over the carrier into the waiting contact, a level gate picture and continuity through the spool to the crown block pass, the stroke crimps and the drop plate shears the tab, and a neck fork takes a 20 N pull. At p = 2.5 mm the crimped row is already at housing pitch; an XHP-4 is pushed on, the end is tested through the spool, and the cut frees the loom, with the thinning cup's loose contacts feeding a hand station.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** b8.
- **Combines:** [terminal-supply/a2d](../terminal-supply/summary.md), [terminal-supply/a2](../terminal-supply/summary.md).
- **Automates:** cut, split, strip, supply contacts, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order, cut to length.
- **What the person still does:** Spool and reel loading, housing tube, three cups and the loom bin, labels, far ends, all non-T4 looms; pairs and J4/J7 crossings not made.
- **Major unresolved problems:**
  - The knife set outside its applicator needs a guided holder (a2's open problem); knife set not on Prime
  - p depends on the punch's width and holder protrusion; if the holder does not clear, p is 4-6 mm
  - Whether the tip-entered comb wedges between split jackets without scuffing; the real carrier width
  - Split length: 16 mm here, ~20 mm for J1's fronts; Derek's call
  - Neck, flank tear, spool inner end, belt feed; carrier pitch and temper; tab stub from a one-sided drop

## Combinations with other explorers

- b8b = b8 (spool as carrier, feed-driven needle rip, whole-tip strip, gang push, cut last) x terminal-supply a2d (skip-pitch strip over a crowned knife-set anvil, pins in removed contacts' holes, level gate view, one-sided drop shear): the ribbon lies flat through the whole cycle; the spreading comb enters from the tip side after the strip; at p = 2.5 mm the crimped row is already at housing pitch; terminal-supply's one-shaft contact side (their K6) and the applicator body as a guided die holder are variants inside it.
- b1c = b1b (applicator in a slow crank, disc stack, dwell) x procedure-is-the-machine p5 (camshaft, one turn per conductor) x terminal-supply a1 (look at the contact alone, reject turn): the gate sits at 60 deg, before the feed finger's downstroke retract band, so a failed gate is a clean reverse.
- b1b takes terminal-supply's supply-side gate (contact seen alone, reject turn with a puff), its stepper wedge for crimp-height sweeps, and its two-supplies jack test (vendor reel and one genuine Digi-Key strip through the same die).
- b2 x terminal-supply a6 / x1: a 0.64 mm post in the contact's box places it in the SN-2549 along its axis from the front, the tab shears on a steel land at its root, and a pawl on a flat run with a tapered pin replaces a wrapped sprocket.
- b2b = b2 x procedure p4 x hand-tool-as-press a1 x ribbon-as-pallet a6 x into-the-housing i5 x b7 x terminal-supply x1/a6: pedal-less station holding one contact type from the first week.
- b8 = procedure p3 / ribbon-as-pallet a4 x change-the-question c5 x b1b x b6 x b1 x into-the-housing i3 / ribbon-as-pallet a6: the spool line with the applicator, now with a contact-alone gate and a straightening pass before the gang push.
- b5 x terminal-supply a6: the MG400 carrying the post head is the precise tier, Kurabo's pattern with one custom end effector.
- b3 x procedure-is-the-machine p7 / b6 / b4: the strip line cut while the ribbon is flat before the fan, so fronts at the housing are independent of fan pitch and the stepped trim disappears.

## Transferable mechanisms

- Put a machine's gate before its first irreversible shaft angle, so 'no' is a clean reverse: on a cam-fed applicator the feed finger's downstroke retract band (~75-94 deg on a 15 mm crank) sets the latest safe gate (b1c).
- Reject turn: a bad contact is crimped empty and blown off the anvil by a timed puff in the dwell between 'crimpers clear' and 'feed moves' (1.3 s at a 10 s turn, or stopped), so no conductor ever meets it (b1b, b1c, from terminal-supply a1).
- Look at the waiting contact alone before any conductor moves (b1 one pitch upstream, b1b/b1c on the anvil, b8b on the crown).
- Post-feed ('automatic') applicator configuration with the conductor held above and the holding part riding the ram (b1).
- No sprung holder can both locate a stranded 22 AWG conductor and yield before it sets (24-85 mN at 6-15 mm): holders come off by timing, not compliance (b1).
- Disc-spring stack in the connecting rod, preloaded above the crimp peak (two DIN 2093 A35.5 in series), as over-travel cap and 'stopped at force' switch (b1b).
- Spring link between an oversized actuator and a hand tool's handle: caps die force and gives a closed-by-force switch; a no-feedback actuator gets an AS5600 on the handle pivot for the captive click (b2).
- A post in the contact's box as the placing tool, the holder face as the box-front datum, the silhouette on the post as the per-contact axial correction (b2, b5; from terminal-supply a6).
- Cut the tab against a steel land at its root before any wire exists; a gripper on the box cannot react the shear moment (b2, b3).
- Feed carrier strip with a pawl on a flat run plus a tapered pin in a neighbouring hole; a wrapped sprocket must be >= ~25 mm radius to stay elastic (b2, b3).
- Cut the strip line while the ribbon is flat and one piece, so every contact sits the same along-conductor distance from the root and the crimp pitch drops out of the fronts at the housing (b3, b8b).
- A spreading comb for split conductors enters from the tip side after the strip, threading the ~1.0 mm gaps between stripped bundles; it cannot start at the clamp face (b8b).
- Strip length is a per-reel recipe value (2.4 mm genuine JST, 1.85-2.1 mm clone), set in every stripper stop, score line and feed offset (b1, b4, b6, b7, b8, b8b, b2b).
- Flat scoring blades closed to a fixed stop hold 50-60 % of the wall; deeper needs a shoe riding the jacket top (b6, b8, b8b); a laser score's depth does not depend on where the clamp holds the conductor centre (b4).
- Pierce each web at the root and draw the ribbon so the needle travels to the tip: tension, a placed root, a webbed tip for a one-piece slug; a spool feed's retraction can be the draw (b6, b8, b8b).
- Die-hole or centred rotary blades, not V-blades, on soft insulation over fine strands; a twist during the pull tears the ring (b7).
- The shop press's jack as a zero-build applicator bench, and two supplies through one die in the same session (b1b).
- Identity through the far end at every act: stripper stop, blade, crimp, cavity (b2b, b1, b6, b8, b8b).
- Same-direction docking for backlash-heavy cheap arms (b5).

## Key findings

- [calc wave3 s0] For a crank above the ram (b1b's crank unit under the shop press's top beam) the slider-crank obliquity term adds: the ram is 4.0 mm above bottom at 40 deg from bottom dead centre (220 deg from top), 15-20 mm up at 266-285 deg. terminal-supply's 226 and 274-293 deg use the crank-below-a-pulled-ram sign; their conclusion (a late gate's back-out re-crosses the feed band) holds either way.
- [calc wave3 s2] A cam-driven feed finger that follows ram height retracts on the downstroke at ~75-94 deg; b1c's gate at 60 deg leaves ~15 deg of margin, but squeezing the 180 deg fork swing into 10-50 deg needs a ~60 mm cam track with a 4:1 sector (peak pressure angle ~26 deg) or a servo fork permitted by a shaft switch.
- [calc wave3 s3] HX711 at 80 Hz through the last 0.2 mm: 19 / 39 / 78 samples at 10 / 20 / 40 s per turn on a 15 mm crank (not ~190, which was p5's eccentric).
- [calc wave3 s4] The Prime 10:1 NEMA 23 planetary held to its 10 N*m permissible rating still gives ~4.6 kN at 0.1 mm above bottom (3.3 kN at 0.2 mm), covering the 3.8 N*m crimp and 5.4 N*m spring need; a 4 kN obstruction met below ~0.13 mm is pushed through, so the rod stack needs ~0.13-0.15 mm of travel past preload.
- [calc wave3 s5] The reject-turn puff window is 1.3 s at a 10 s turn (220-266 deg); a 1 mm jet at 1-3 bar gives ~40-120 mN against a 0.42 mN contact, so what can stop it is a contact wedged in the nest, not the jet's force.
- [calc wave3 s6] The Prime Justech actuator (1,500 N, 7 mm/s, no feedback) closes or opens the SN-2549 in ~5.7 s, a b2b machine cycle of ~22-26 s against Derek's ~17 s; a NEMA 17 on Tr8x2 (~330 N) carries the spring link only if the tool's handle ratio is >= ~10.
- [calc wave3 s7] On a crown station the rest of the window, insulation barrel, tab, carrier and crown clearance occupy ~5.3-9.2 mm behind the strip line, so a spreading comb behind them makes the split >= 9.3-15.2 mm; with every contact the same along-conductor distance from the root, the outermost front lands short by 4P 0.05, 5P 0.09, J4 0.19, J1 0.34 mm at 15 mm free length and J1 0.25 mm at 20 mm.
- [calc wave3 s7] A parting pair (two blades pushing each side out by p - 1.7) needs only 50-85 mN per conductor but leaves crimped boxes (1.85-1.95 mm wide) crowded at 1.7-2.0 mm pitch; a tip-entered comb leaves the row at p, and at p = 2.5 mm already at housing pitch.
- [calc wave3 s8] Whole-tip strip at 60 % crown scores: 4.7-13 N per conductor with silicone at 4-11 MPa, 9.4-13 N at the digest's 8-11 MPa; 19-52 N for a 4P, 24-65 N for a 5P, carried by the clamp against an 85-100 N conductor break.
- [TS s1] A gripper on the box cannot react the tab drop-shear: 48-158 N at 4.8-5.7 mm is 230-905 N*mm, 3-200x the neck's plastic moment; a steel land at the tab root reacts it with no lever.
- [TS s2] Trimming a stepped edge after stripping moves the insulation edge forward by the trim (5P 1.06 mm, J4 2.27 mm at 4.35 mm fan pitch), putting insulation under the conductor barrel; stripping flat before fanning removes the step geometry entirely.
- [TS s4] Lateral capture of the insulation in the open wings per side: clone +/-0.21-0.83 mm, Wurth analog +/-0.25-0.35 mm, JST's 1.95 mm envelope (if it is the open width) +/-0.08-0.18 mm; b1's +/-0.4 mm holds for clone wings only, and with genuine contacts the ram finger V's setting is the whole margin.
- [TS s11] A proof-pull catch slot 'narrower than the box, wider than the crimped barrels' has no width window (margin -0.15 to +0.15 mm); a neck fork above the floor or a plate edge ~2.0 mm up on the box roof bears on the box and clears the lance.
- [Prime] No Prime listing for the 1.5-2 t press, the OTP applicator, the OTP knife set, XH reels, the sensor-triggered stripper, the Bambu laser module or heavy disc springs; every applicator and knife-set route is eBay or Made-in-China. The VEVOR AP-3 (310 mm opening, $255.90) is the Prime frame that fits an applicator; the AP-1 ($61.90) fits a knife-set block.
- [Prime] Genuine Engineer PA-09 is on Prime at $38.99 next day; the SN-2549 at $22.29; an iCrimp IWS-0723K set with a second 2549 die at $46.59.
- [facts s2] JST's CDS SXH001-06/CMKS-L applicator has a 40 mm stroke and post- or pre-feed cams, so a crank's throw must match the applicator that arrives (15 mm for 30 mm, 20 mm for 40 mm), and every b1c angle moves with it.

## Where this view still had trouble

- Insertion of crossed conductors (J4's and J7's GND) by a borrowed machine: no mass-produced machine inserts a crossing; my arrangements only carry an 'insert the crossing conductor last' order rule or hand it back.
- Two ribbons into one housing (J1, J2, J4, J7) on the spool lines: two spools edge to edge is named but not pictured; nothing borrowed handles a half-housed pair.
- Loose kit contacts in an unattended borrowed machine: bowl feeders and screw feeders do not orient an XH contact; my view relies on strip, or on terminal-supply's post head.
- A bought stripper known to work on 22 AWG silicone: every mass-produced stripper found is either V-blade (predicted to fail) or untested on silicone; the die-hole head has to be made or improvised from a 20 AWG hole.
- In-line crimp height: no cheap borrowed gauge measures it on the machine; every arrangement samples by micrometer or sweeps with a wedge.
- A Prime (days, not freight) route to hardened XH crimp tooling other than the hand tools: no press, applicator or knife set is on Prime, so every die-set arrangement waits on eBay or Made-in-China.
- Guarding a relay-fired 2 t press cheaply without modifying its own finger guard.
- The far ends (Fastons, ferrules, IDC, screw terminals): the same borrowed-applicator logic could apply but was not developed.

## Questions for Derek

- If an OTP applicator is ordered: is its stroke 30 or 40 mm, does its feed cam have both post-feed ('automatic') and pre-feed positions, and is there a wire-hold-spring slot? Stroking it slowly in the shop press's jack and noting where the feed finger moves (up and down) sets b1, b1b, b1c and b8's timing.
- Would you run the jack test with two supplies through one die: the vendor's reel, then one Digi-Key 100-piece genuine SXH strip ($4.71)? It shows which contact the die is cut for, whether genuine carrier pitch fits the feed, and whether genuine wings clear a ram-finger V.
- Do the CQRobot kit contacts carry a tab stub at their rear? If so they were cut from a reel, and a clone reel from the same maker may be the kit contact on strip.
- One SXH strip under the caliper: carrier width, pitch and tab length. The carrier width sets b8b's split and b2's steel land.
- How long a split behind the housing is acceptable on a finished loom: 8-15 mm folded (b1, b8), ~16 mm for a flat crown line (b8b), ~20 mm if J1's fronts must land inside +/-0.3 mm?
- On the SN-2549: held closed to a light, do the jaws bottom face to face; and does the XH nest's front face stop a contact's box or let it through?
- Peel a metre of 3P and 5P and section one ribbon under the ELP camera: does the tear stay in the neck, and how tall is the neck? It decides round needle or cutting edge in b6, b8 and b8b.
- Would a hand rip board (~25 s an end) be welcome in place of peeling, this week?
- Is a spool-fed line that makes only 4P-into-XHP-4 ends (5 of 10 housings) a useful first machine, and is the BNTECHGO spool's inner end reachable?
- For b2b: is poking each conductor twice and inserting at a lit cavity, with the contact never in your fingers, an end state you would use, or is unattended (b1c, b8, b8b) the goal?
- Would you run a Class 4 diode laser station on the bench (b4b), or keep lasers inside the H2C enclosure?
- Genuine JST SXH reel or the vendor's clone reel when an applicator or knife set is ordered? The strip length and every stop follow the choice.
