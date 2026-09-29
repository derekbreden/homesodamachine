# machine-that-sees-and-learns

*The first stage of a cell is one software can move and observe.*

This page indexes every arrangement this explorer holds, with the explorer's own one-paragraph picture of each. The idea files carry the development. Paths are relative to this directory.

## Arrangements

### [v1 — The watched nest: a fixed press photographed at every step, fed by a stage that steers by the picture](ideas/v1-watched-nest.md)

A small press with a narrow punch (under 7.45 mm wide for ~5.9 mm above its crimping edge) holds one XH contact barrels-up in a blackened nest. The ribbon end sits flush-cut in an under-width channel and a fan block of hinged keys, every waiting conductor held 5 mm up; a hover picture predicts across and reads each conductor's own torn insulation edge along the wire, a plunger lowers key k so only that conductor drops into the U, and a gate (outline on black, silhouette under the lifted neighbours, the bundle's displaced shadow under 60-75 deg LEDs, far-end continuity) precedes an MCU-owned crawl stroke to a geometric bottom with a steel ceiling in series. The crimp is then set on a blade in a silhouette window, its height roll-corrected by the box's own silhouette, and proof-pulled on the carrier tab or a lance-notched plate in the neck.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Combines:** [ribbon-as-pallet/a1](../ribbon-as-pallet/summary.md), [ribbon-as-pallet/a5](../ribbon-as-pallet/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cutting, splitting and stripping unless v6 does them; loading fan blocks; contact supply by hand unless strip or v4/v4b; insertion; answering parked conductors in v7's queue.
- **Major unresolved problems:**
  - Room for 60-75 deg LEDs between a raised punch and the lifted neighbours, and whether a tin floor gives a findable shadow edge
  - The neck gap, which decides the loose-contact proof plate
  - Key design: TPU lip grip, 0.3-0.4 mm printed walls at 2.5 mm hinge pitch, and a 5-12 deg kink the key root leaves 20-30 mm behind every contact
  - Whether a given host's punch meets the 7.45 mm requirement
  - Silhouette against micrometer crimp height; box-to-box height spread in a lot
  - Whether a crimped contact sticks in the punch
  - On an applicator four of its asks do not carry (anvil load cell, nest by supply form, lifted neighbours over the pressure plate, side window), so it becomes v9 there

### [v1b — Branch of v1: a cheap printer's three axes become the stage](ideas/v1b-printer-as-stage.md)

An Ender 3 V3 SE ($186-219 on Prime) with its hot end removed gives the pallet across, along-the-wire and height, steered by the picture rather than its step count. Four arrangements by what the crimp host weighs: A, a light press or tack station rides the bed; B, the Ender lies on its back in front of a bench-fixed press so its Z lead screws run along the wire and hold the 20 N proof pull (0.02-0.09 N.m at the motor); C, b1's two MGN12 rails in front of the press; D, borrowed-machines' b3 self-contained crimp head on the carriage with v1's fan block and keys on the bed. The fan block seats on steel balls in hardened dowel pairs with a magnet, and the loom's tail coils in a cup with its cut face in a pogo block.

- contacts: either loose or strip · steel: any of several · meeting: a general-purpose arm or gantry hand.
- **Branch of** v1.
- **Combines:** [borrowed-machines/b3](../borrowed-machines/summary.md), [borrowed-machines/b1](../borrowed-machines/summary.md).
- **Automates:** place contact on conductor.
- **What the person still does:** Everything v1 hands back; the stage decides nothing.
- **Major unresolved problems:**
  - Which arrangement suits the chosen host
  - Stock firmware as a plain G-code stage, upright or on its back
  - Ender frame stiffness lying on its back
  - Pogo cable run and a tail cup that holds a 600 mm coil
  - D: the head's throat reaching past a 5P fan, punch under 7.45 mm at the neighbours' height

### [v2 — An arm taught by Derek's hands carries the work between stations; docks and cameras do the precision](ideas/v2-arm-taught-by-hand.md)

An SO-101 follower arm with its leader arm carries rigid pallets between fixed stations, each with a >=5 mm funnel and a steel-ball-on-dowel-pin seat pulled home by a magnet; the station's own small stage and camera do the last tenths of a millimetre. Derek teaches each subtask ~50 times with the leader arm, LeRobot trains ACT policies on the Mac, and failed deliveries become DAgger corrections. Tip wander is ~1.2 mm RSS approached one way and ~6 mm when approaches vary, so the arm never does an XH-precise act; its jobs are carrying, flipping, racking and perhaps peeling a web against the clamp face.

- contacts: not applicable · steel: not applicable · meeting: a general-purpose arm or gantry hand.
- **Combines:** [ribbon-as-pallet/a3](../ribbon-as-pallet/summary.md), [borrowed-machines/b5](../borrowed-machines/summary.md).
- **Automates:** split.
- **What the person still does:** Every precise act (to the stations); loading pallets, or snapping backshells in the a3 branch; 4-6 h of teaching plus retraining; ~6 asks a unit at 90 % per transfer.
- **Major unresolved problems:**
  - Teaching cost and policy durability over 60 units
  - Success rate per transfer
  - Servo overload protection under sustained load in a flip
  - A plain rail or v1b's stage carries a straight line more cheaply
  - Whether the web peels at all

### [v3 — The press that runs its own experiments: it finds the crimp height nobody published, then polices it](ideas/v3-press-that-runs-experiments.md)

A crimp host with a 0.001 mm indicator across the dies, a load cell in the force path, v1's cameras and a pull axis crimps production-made 5P coupon ends at a sweep of heights and pulls each to failure on a soldered lug or a bare-copper wrap, never a capstan on the jacket. Height is set by a stepper stop, stop blocks on shims, hit-and-re-touch, or a crank stopped short of bottom whose 14-bit shaft encoder reads a 10 N re-touch at 0.2-0.5 um per count; hosts run from b1b's hand-pumped jack test and $22-39 hand tools with a pusher to the crank. Arms sweep conductor height, insulation height, the tack (0.2-0.5 mm above the final insulation height, 0-0.2 mm wider), strip length per contact and the insulation edge, under a Claude session in v7's campaign mode.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die · usable without a motor.
- **Combines:** [ribbon-as-pallet/a2b](../ribbon-as-pallet/summary.md), [force-and-form/f3](../force-and-form/summary.md), [borrowed-machines/b1b](../borrowed-machines/summary.md), [hand-tool-as-press/a1b](../hand-tool-as-press/summary.md), [hand-tool-as-press/a5](../hand-tool-as-press/summary.md).
- **Automates:** crimp, verify crimp.
- **What the person still does:** Making ~30 coupon ends and their far-end grips (1-4 h); deciding whether to adopt the windows; any sectioning.
- **Major unresolved problems:**
  - Contact-side reaction for loose contacts depends on the neck gap
  - Tab yield caps strip pulls at 72-96 N; an applicator shears the tab in the stroke, so pulls use a neck fork
  - Far-end grip failure modes above ~80 N
  - Pull-force scatter unknown
  - With both crimpers on one ram a re-touch reads whichever barrel springs back higher
  - Cross-sections are manual

### [v4 — Tap, look, pick: loose contacts on a lit tray, singulated by software, placed in the nest](ideas/v4-tap-look-pick.md)

About twenty loose kit contacts on a frosted tray over an A5 light pad are tapped by a 10 mm solenoid, photographed backlit and top-lit, and sorted by pose. A barrels-up contact rests tilted 11-17 deg on its lance, and a lance of 7-52 N/mm cannot be levelled by a light nozzle, so the pick head seals on the tilted top with a 2-3 mm bellows cup or a face cut at the tilt, confirms the pick by vacuum pressure, and drops the contact into an open nest. This is OpenPnP HeapFeeder logic at bench scale; for genuine strip, shearing the tab over the nest is the other singulator.

- contacts: loose kit contacts · steel: not applicable · meeting: not applicable (supporting station or module).
- **Automates:** supply contacts.
- **What the person still does:** Pouring ~60 contacts a unit; clearing hooked pairs; everything after the nest.
- **Major unresolved problems:**
  - Pose odds and tangling rate
  - Whether a bellows cup or tilt-cut face holds a tilted 0.043 g contact and releases it square
  - Whether nest chamfers seat a dropped contact every time
  - Vacuum and rotation on a stage that also carries a pallet
  - The lance's real stiffness

### [v4b — Branch of v4: a pocket plate that tapping fills, and a camera that checks every pocket](ideas/v4b-pocket-plate.md)

A printed plate with 20-30 channels at least 2.05 mm wide at the floor, flaring above, with a lance relief at one end, admits only the barrels-up pose, in which the contact sinks and lies flat; reversed ones tilt on their lance, barrels-down and side-lying ones rest on top. Tapping or a hand brush fills it, the camera checks every pocket, and a plain rigid nozzle picks from known coordinates because the box top is level. Branches: a hanging plate of stepped through-slots with a post rising from below; the plate as a 4-5 mm crimp cassette a ribbon pallet docks onto; and the plate as a supply of kit contacts for borrowed-machines' b3 head.

- contacts: loose kit contacts · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Branch of** v4.
- **Combines:** [ribbon-as-pallet/a2c](../ribbon-as-pallet/summary.md), [terminal-supply/a3](../terminal-supply/summary.md), [borrowed-machines/b3](../borrowed-machines/summary.md).
- **Automates:** supply contacts.
- **What the person still does:** Pouring or hand-filling; everything after the pick. Hand fill with a tweezer pick beside today's SN-2549 is usable with no motor.
- **Major unresolved problems:**
  - Pocket geometry that admits only barrels-up across clone variation
  - Fill rate by tapping; pop-out of seated contacts
  - Cassette branch: steel anvils through a printed plate, and the pull reaction against the lance
  - Head-supply branch: a loose contact on a head built for strip

### [v5 — The inspection booth: look at and pull every crimp, whoever made it](ideas/v5-inspection-booth.md)

A shoebox booth: a hardened blade under the conductor barrel, a ground roll flat on which a spring presses the box, a lance-notched steel stop in the neck bearing on the box's side walls, a backlight and camera across at crimp height, a 45 deg mirror for the top view, a gauge pin in frame, and a servo clamp and lead-screw axis for a ~20 N proof pull. The box's front 1 mm grows 32-34 um per degree of roll in the same silhouette, so the crimp height is roll-corrected and crimps rolled over 2 deg are re-seated. Modes: after Derek's hand crimps today; in line with any machine, including an applicator's dwell position >=7 mm out; the finished housing on a board-wafer tester; a whole docked pallet; and with hand-tool-as-press's a6 foot bench, whose pull plate is the same part.

- contacts: either loose or strip · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Combines:** [ribbon-as-pallet/a1b](../ribbon-as-pallet/summary.md), [ribbon-as-pallet/a2d](../ribbon-as-pallet/summary.md), [hand-tool-as-press/a6](../hand-tool-as-press/summary.md), [into-the-housing/i5](../into-the-housing/summary.md).
- **Automates:** verify crimp, verify insertion and pin order.
- **What the person still does:** All making; dropping each hand crimp in (~20 s), or docking pallets.
- **Major unresolved problems:**
  - Silhouette against point-micrometer offset (a point-and-blade crimp micrometer is not on Prime)
  - Neck gap for the notched stop on kit contacts
  - Hand-drop consistency
  - Box-to-box height spread within a lot

### [v6 — The patient cell: the whole procedure on one stage, every act bracketed by a look, every doubt sent to a queue](ideas/v6-patient-cell.md)

One stage carries a channel pallet (guillotine flush cut, keys, tail in a cup with a pogo block) past stations. Split: the under-width channel registers each valley over a steel rib, a sensed blade plunges at the root and the pallet is drawn so the blade runs out to the tip, keeping the free length in tension. Strip: die-hole blades close at the contact's own strip length and the slug is pulled with a twist that shears the remaining ring. Then place and crimp (v1, v8 or v9), inspect (v5), insert along the wire axis with the latch seen through the mating-face window, crossing conductors inserted last or by hand, and a wafer-board test; every station is look, act, look, decide, with back-out as a guillotine stroke 6-10 mm further in.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die.
- **Combines:** [ribbon-as-pallet/a1](../ribbon-as-pallet/summary.md), [ribbon-as-pallet/a5](../ribbon-as-pallet/summary.md), [ribbon-as-pallet/a6](../ribbon-as-pallet/summary.md), [borrowed-machines/b6](../borrowed-machines/summary.md), [borrowed-machines/b7](../borrowed-machines/summary.md), [ribbon-as-pallet/a4](../ribbon-as-pallet/summary.md), [procedure-is-the-machine/p3](../procedure-is-the-machine/summary.md), [change-the-question/c5](../change-the-question/summary.md).
- **Automates:** split, strip, place contact on conductor, crimp, verify crimp, insert, verify insertion and pin order.
- **What the person still does:** Cutting and palleting 14 ribbon ends (~15-30 min) unless the spool branch; stocking contacts and housings; J4/J7 crossings unless the tweezer route is built; the queue; labels; far-end terminations.
- **Major unresolved problems:**
  - Stripping silicone cleanly (measured and retried, not solved)
  - Splitting the web: whether a blade plunged onto a rib pierces it cleanly; peel and laser untested
  - Whether the lance shows through the mating-face window
  - XH insertion and retention forces are not public; seat depth of the contact's rear
  - Crossing looms need slack and 0.8 mm of jaw room, or hands
  - Crowding on one head

### [v7 — The run: what drives the motors and cameras, where each loop closes, how a Claude session supervises, and the first day](ideas/v7-the-run.md)

A station ESP32 runs every press stroke whole (approach to a taught position, a 0.05-0.1 mm/s crawl or, on a crank, a speed profile indexed to angle, a force envelope checked every sample), drives the servos, lights and far-end inputs, and every hosted press carries a steel force ceiling whose switch cuts the drivers' enable line with the e-stop and lid. On the Mac a capture app keeps each ELP stream open all run with a sync LED marking the lighting state, a runner owns the recipe, per-conductor state, write-ahead journal and log, and a judge takes numbers only from OpenCV with pass, borderline and hard-fail bands; borderlines go to claude -p with a JSON schema, asks go to Derek's phone by ntfy, and a resumed supervisor session drafts asks, watches trends and writes the unit report but can never move a motor, resume, change a threshold or pass a hard fail. Klipper's API server streams load_cell/dump_force and angle/dump_angle, and the ladder runs from the booth with no motor to the heavy crimp under one runner.

- contacts: not applicable · steel: not applicable · meeting: not applicable (supporting station or module) · usable without a motor.
- **Automates:** verify crimp.
- **What the person still does:** Choosing the stack; commissioning with Claude at the bench; answering asks (5-11 a unit on day 1, 1-2 later, estimated); approving threshold changes; keeping the Mac awake or giving the cell its own computer.
- **Major unresolved problems:**
  - Which stack suits Derek (own PlatformIO firmware, FluidNC or Klipper)
  - Which angle sensors Klipper's [angle] reads
  - The ELP board's MJPG rate and buffer depth
  - The finish-the-stroke-on-silence policy is a choice
  - Real ask rates
  - Stock Ender firmware as a plain stage
  - ntfy privacy
  - Heavy disc springs for the ceilings are not on Prime

### [v8 — Tack, look, then crimp: a light watched station pins the contact to the conductor, and the heavy crimp comes after](ideas/v8-tack-look-crimp.md)

At station T a printed nest holds a contact on a steel insert with a 20 kg load cell under it; v1's key lowers one conductor, and a 1.2-1.5 mm steel former cut 0.1-0.2 mm wider than C's insulation crimper, driven by a 35 kg.cm servo on a 1:1 lever to a screw stop at C's final insulation height plus 0.2-0.5 mm, closes the insulation wings loosely over the jacket. A camera then looks straight down into the still-open conductor barrel with nothing above it, under LEDs at 60-75 deg that show the hovering bundle's displaced shadow (a strand on the floor has none); a fail slides the loose tack off the tip and costs a contact, not a ribbon end. The tacked contact rides on its conductor to station C: a narrow-punch host fed from the pallet (hand-tool-as-press a4c, force-and-form f3), the SN-2549 as sold with the ribbon off the pallet (a6c, foot or hand), or, on strip, an applicator, which becomes v9; a toggle-clamp version with no motor measures the tack on today's bench.

- contacts: either loose or strip · steel: any of several · meeting: conductor brought to a fixed die · usable without a motor.
- **Combines:** [change-the-question/c1b](../change-the-question/summary.md), [force-and-form/f9](../force-and-form/summary.md), [hand-tool-as-press/a4c](../hand-tool-as-press/summary.md), [hand-tool-as-press/a6c](../hand-tool-as-press/summary.md).
- **Automates:** place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cutting and palleting; splitting and stripping unless v6; contact supply if the plate is hand-filled; insertion; with a6c at C, the foot crimp (9-15 min a unit).
- **Major unresolved problems:**
  - The tack's grip window on this silicone (0.2-1.5 N wanted; the width and height offsets that give it are unknown within a factor-of-eight grip model)
  - Whether C's insulation crimper takes a tacked barrel 0.1-0.2 mm wider than itself
  - Tacked then re-formed against one pass (sections)
  - A rear shoulder for the back-out needs an unmeasured neck gap
  - The shadow test on tin
  - The T-to-C carry rides on a 0.2-1.5 N tack
  - Narrow-punch C hosts are built things; the SN-2549 as sold takes the ribbon off the pallet

### [v9 — Tack at the anvil: the watched tack made inside a stopped crank applicator, on a contact still on its carrier](ideas/v9-tack-at-the-anvil.md)

An OTP side-feed XH applicator in pre-feed sits in the idle 12-ton press, driven by b1b's 15 mm crank with a 4 kN disc stack in the rod; at top dead centre a contact waits on the anvil, still on its carrier. b1's fork lays conductor i from a folded-back band into it and a foot seats the jacket; a T-arm doweled to the applicator base swings in and a servo drives a former (the scanned insulation-crimper profile plus 0.1-0.2 mm) to a stop at the applicator's own final insulation height plus 0.2-0.5 mm, then an M-arm swings a 10 mm mirror in so a camera looks straight down into the open conductor barrel with the shadow test. A pass is crimped by a crawl profiled to crank angle and the tab sheared at bottom; a fail draws the conductor straight back while the carrier holds the box (0.4-1.5 N release against a tab that bends at 4-12 N), the empty contact is crimped empty and blown off in the dwell, and the dwell carries a neck-fork 20 N pull and a roll-corrected silhouette; 72-142 s a conductor, and on b1c's one shaft the same stop sits at 0-40 deg.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die.
- **Combines:** [borrowed-machines/b1b](../borrowed-machines/summary.md), [borrowed-machines/b1](../borrowed-machines/summary.md), [borrowed-machines/b1c](../borrowed-machines/summary.md).
- **Automates:** supply contacts, place contact on conductor, crimp, verify crimp.
- **What the person still does:** Cutting and cassette loading; splitting and stripping unless a prep station is built; insertion; reels and the reject cup; sample crimp heights (~27 attended min a unit with hand insertion).
- **Major unresolved problems:**
  - Room under the raised OTP crimpers at top dead centre for a ~17 mm former guide and ~11 mm mirror
  - Modifying a bought applicator: doweling the former guide to its base; the former's scanned profile
  - The tack's grip and the width/height that give 0.2-1.5 N
  - Whether the insulation crimper's mouth takes a tacked barrel 0.1-0.2 mm wider than itself
  - Tacked then re-formed against one pass
  - Shadow test on tin; blow-off of a crushed empty contact
  - Pre-feed and strip only; applicator and reel are not on Prime, so lead time is the vendor's
  - b1b's applicator interface (shut height, stroke, spring loads, feed timing)

### [v9b — The tack by hand on the jack-test applicator: lay in, throw a toggle, look, pump](ideas/v9b-tack-by-hand-on-the-jack-test.md)

The OTP applicator in pre-feed sits on the VEVOR 12-ton press bed with the press's own bottle jack stroking it through a T-slot adapter to a stop collar (b1b stage 0). Derek lays a stripped conductor into the waiting contact by hand, throws a POWERTEC push-pull toggle that drives the scanned-profile former to its tack stop, swings a mirror in and checks the open barrel from straight above on the Mac with the ELP and two ~65 deg LEDs, then pumps the jack to the collar; release lets the applicator return and pre-feed the next contact. At 31-93 s a crimp it is slower than today by hand, but it removes the contact juggling in the first week and is the bench that measures the tack's grip, height and width, the stroke order by section, the room under the crimpers, the mouth and the shadow test before anything is motorised.

- contacts: carrier strip · steel: bought mini-applicator or knife set · meeting: conductor brought to a fixed die · usable without a motor.
- **Branch of** v9.
- **Combines:** [borrowed-machines/b1b](../borrowed-machines/summary.md).
- **Automates:** supply contacts, verify crimp.
- **What the person still does:** All motion (lay-in, toggle, mirror, pumping), judging the picture, splitting and stripping, insertion; 27-82 attended min a unit.
- **Major unresolved problems:**
  - The applicator is not on Prime (lead time, die cut for which contact, interface)
  - The toggle's stroke is not stated
  - Holding a split conductor in the U by hand while throwing the toggle
  - A guard over the crimper faces
  - Whether an air-over-hydraulic jack (BIG RED, $136.04 Prime) fits the press

## Combinations with other explorers

- v9 = v8 (tack, straight-down look, then crimp) x borrowed-machines b1b (OTP applicator in pre-feed on a slow crank in the 12-ton frame) x b1 (cassette with folded band, valley-tine fork, foot, far-end pogo block): T and C are one anvil, the carrier is the back-out fixture, the tack is the holder so the fork and foot leave before the crank turns; branch A1 puts it on b1c's one shaft with the stop at 0-40 deg.
- v9b = v9 x b1b stage 0 (the jack test): the tack by a toggle clamp, the look by the ELP through a hand-swung mirror, the crimp by pumping the press's own bottle jack; motorless, first week.
- v8 x hand-tool-as-press a4c (one-nest SN die set on the same stage) and a6c (tacked by machine, crimped by foot): the C hosts that fit a pallet holding neighbours 5 mm up at 5 mm pitch; hand-tool-as-press holds them as its own idea files.
- v8 x change-the-question c1b x force-and-form f9: a single watched tack whose straight-down look precedes the conductor crimp; force-and-form f9b tacks a whole docked strip segment instead.
- v8 C host x borrowed-machines b2 on edge: the tacked contact enters the open SN jaws from the wire side, box first, lance trailing; saves no jaw opening.
- v1b arrangement D = v1 x borrowed-machines b3: b3's self-contained crimp head on the printer carriage, v1's fan block and keys on the bed, cameras on the head's frame.
- v1b arrangement B/C = v1 x a bench-fixed press: the Ender on its back (Z lead screws along the wire) or b1's two MGN12 rails give the pallet its along-wire axis.
- v3 x borrowed-machines b1b (jack test, then crank): a zero-build campaign press on the production reel, then the crank as its own height knob and gauge (10 N re-touch on a 14-bit shaft encoder).
- v3 x hand-tool-as-press a1b and a5: $22-39 campaign hosts whose grip position v5's silhouette maps to a height.
- v7 stack C x Klipper API server hosting b1b, b1c, b8 and v9: force against crank angle as one stream (load_cell/dump_force, angle/dump_angle), switch cams as runner gates, disc-stack ceiling in the enable line.
- v4b x borrowed-machines b3: the pocket plate as a strip-fed head's supply of loose kit contacts.
- v5 x hand-tool-as-press a6: a6's backed pull plate is v5's lance-notched stop; adding blade, roll flat and camera gives every foot-closed crimp a roll-corrected height. v5 at b1/b1b/v9's dwell withdraw position gives applicator machines an in-line crimp height.
- v6 x borrowed-machines b6 (plunge at the root, draw to the tip) and b7 (die-hole blades, twist-on-pull).
- v1 x ribbon-as-pallet a1/a5/a6: under-width channel, flush-cut tip line, fan block with keys and neighbours lifted, far-end pogo port, tab-reacted proof pull.
- v5 mode 4 x ribbon-as-pallet a1b/a2d: hand crimps on a docked strip segment come to the booth still on the carrier.
- v4b cassette x ribbon-as-pallet a2c; v4b hanging plate x terminal-supply a3/a4.
- v6 spool branch x ribbon-as-pallet a4 x procedure-is-the-machine p3 x change-the-question c5; v6 insertion x ribbon-as-pallet a6.
- v2 backshell branch x ribbon-as-pallet a3.

## Transferable mechanisms

- Tack at the applicator's own anvil: the contact never leaves its datum between tack, look, crimp and tab shear, and the carrier is the back-out fixture (a 0.4-1.5 N tack release against a tab that bends only at 4-12 N along the wire; draw flat, since it yields at 0.5-1.7 N sideways).
- Define a tack relative to the final crimp on the same contact and wire (height H_f + 0.2-0.5 mm, former 0.1-0.2 mm wider than the final crimper), never as an absolute height.
- The shadow test: a bundle held by its jacket hovers 0.3-0.5 mm off the barrel floor, and an LED at 60-75 deg throws its shadow 0.08-0.30 mm aside; a strand lying on the floor casts none. It works where focus (0.55-1.5 mm depth of field) cannot.
- A steel force ceiling in series with every drive (disc stack preloaded above the crimp peak, or a spring link for a hand tool), its switch in the drivers' enable line, so the limit does not live only in firmware.
- On a crank, profile the stepper so the ram crawls at 0.05-0.1 mm/s from a taught angle with the envelope indexed to angle; a doubled contact is then stopped at ~200 N rather than pushed through.
- A crank stopped short of bottom is its own crimp-height knob and gauge: sub-micron ram travel per microstep and 0.2-0.5 um of height per 14-bit encoder count at a 10 N re-touch.
- Swing-in arms doweled to the reference (former, mirror) for a tool that only has room at top dead centre.
- An Ender on its back gives a bench-fixed press the along-wire axis on lead screws that hold a proof pull unpowered.
- The MCU owns every stroke; the Mac commands whole strokes and reads traces.
- Three bands per measurement (pass, borderline for Claude, hard fail only for Derek), every Claude verdict scored later against the measurement.
- Write-ahead journal: intent before each act, result after; a restart re-looks and never repeats an act.
- One long-lived capture app per run (the ELP re-parks focus on stream start), cameras matched by name, a sync LED in frame to reject stale frames.
- Asks as push notifications with a photo and three buttons, answered on a second topic the runner listens to.
- A supervisor Claude session limited by its tool list: may pause, cannot resume, move motors, change thresholds or pass a hard fail.
- The contact's box is its own roll gauge in the crimp's silhouette (32-34 um per degree).
- Neighbours out of plane plus a key per conductor; the pallet makes the nominal, the picture finds the exceptions.
- Anything that reacts on the box does it in the neck: box and crimped insulation barrel cannot be told apart by width or height across lots.
- Crimp height by hit-and-re-touch needs no settable stop.
- Pull coupons to failure on copper (soldered lug or bare-copper wrap), not on the jacket.
- A build ladder where every rung is useful the week it is made and reuses the same log and labels: booth, foot bench or hand tack, tack station, heavy crimp, then split, strip and insert.

## Key findings

- [calc: w3_final s1] At the final crimper's own width a closed insulation barrel squeezes the 1.7 +/-0.1 mm jacket sideways by 3-22 %, which force-and-form's grip model puts at up to ~7 N, beyond the ~1.5 N a tack must release at; a former 0.1-0.2 mm wider brings it to 0-17 % or 0-11 %. This view disagrees with cutting the former to the final crimper's width, on that physics.
- [calc: w3_final s1] After a tack at H_f + 0.2-0.5 mm the conductor wings are met first (0.62-0.87 mm left) and curl 0.12-0.67 mm before the insulation crimper retouches the tacked barrel; untacked, on this silicone's 2.0-2.46 mm final heights, the insulation wings are met at 0.29-1.40 mm, before or after the conductor wings. The jacket is held before compaction either way.
- [calc: w3_final s5] Using the applicator's own ram as the tacker (stop 0.2-0.5 mm above bottom) leaves the conductor barrel's top opening only 0-71 % open, which is why the tack needs a separate former.
- [calc: w3_final s2] A DS3235 35 kg.cm servo on a 1:1 lever gives 137-172 N at the former; the 20 kg bar cell belongs under the nest insert on a bench T (forming force only) and in the link on an applicator, where the trace up to the stop's knee is the forming curve.
- [calc: w3_final s3, s4] Machine time per unit: v8 1.0-2.4 h, a4c 1.0-2.1 h, v9 1.1-2.1 h; v9b by hand 31-93 s a crimp, 27-82 min a unit, slower than today's ~22 min.
- [bm W s2] The tacked bundle hovers 0.30-0.52 mm above the barrel floor; depth of field is 0.55-0.76 mm at 122 px/mm; LEDs at 60-75 deg displace its shadow 0.08-0.30 mm (10-36 px at 122 px/mm); lowest elevations reaching the floor are 53-66 deg.
- [bm W s3, s14] A 30-40 mm applicator stroke leaves ~23-42 mm under raised crimpers (estimate); a former needs ~17 mm and a mirror ~11 mm; on b1c's shaft that room exists only at 0-40 deg.
- [bm W s5] A crank turned at constant speed passes 0.3 mm above bottom at 0.67 mm/s (30 s turn); a profiled crawl stops a doubled contact at ~200-212 N against 242-367 N at constant turning.
- [bm W s13] The lance is 7-52 N/mm as a cantilever, so a nozzle on a few tenths of a newton cannot level a barrels-up contact; the pick seals on the tilted top or picks from lance-relieved pockets.
- [bm W s9] A split drawn with the blade running toward the clamp puts 25-35 mm of 5P in compression, buckling at 1.1-2.2 N against 0.8-12 N of drag; plunging at the root and drawing to the tip keeps it in tension.
- [source: klipper3d.org/API_Server.html, fetched 2026-09-28] Klipper's API server offers load_cell/dump_force and angle/dump_angle subscriptions over a Unix-domain socket with JSON messages; [load_cell] sensor types are CS1237, HX711, HX717, ADS1220, ADS131M0x (Config_Reference, fetched 2026-09-28).
- [Prime] The IMX298 M12 module lists MJPEG 4656 x 3496 at 10 fps (8 lighting states in 2.6-4.2 s); the Ender 3 V3 SE is $219 (2,112 ratings, 500+ a month) or $186.14; no OTP applicator, XH reel, SN jaw set alone, crimp micrometer or heavy disc spring is on Prime.
- [calc: cycle_and_cost s1, s2] With the crawl rule the watched nest is 69-177 s a crimp, 1.1-2.9 h a unit; the patient cell 2.8-6.6 h a unit.
- [claude-api skill table, cached 2026-09-25] Cache reads are $0.20/MTok on both Opus 5.5 and Sonnet 5.5; this view's wave2 calc had used 0.1x input ($0.40 for Opus) and is corrected, giving $0.2-2.8 a unit of supervision.
- [bm cycle_and_arm s2] SO-101 tip wander is ~1.2 mm RSS (2.2 worst) when docks are approached the same way and ~6 mm RSS when approaches vary.
- [calc: w3htp s7, s4] A punch fed from v1's pallet must stay under 7.45 mm wide for ~5.9 mm above its crimping edge; strip length belongs to the contact (1.6-2.1 mm on the clone barrel, 2.4 mm implies a genuine barrel of ~1.8-2.05 mm).

## Where this view still had trouble

- Loose kit contacts with an applicator-grade datum: this view found no way to give a loose tacked contact the along-wire location an applicator's strip track gives, short of a printed or steel nest steered by pictures; the tack-at-the-anvil advantages belong to strip only.
- A per-crimp proof pull on loose kit contacts when the neck is short: no reaction point was found that avoids the lance, so pull strength falls back to sampling.
- Seeing a strand on the barrel floor under a raised punch (v1): whether 60-75 deg LEDs fit between the punch and lifted neighbours, and whether tin on tin gives a shadow edge at all, is unverified; the straight-down look needs the tack.
- Crossing looms (J4, J7) and two-ribbon housings (J1, J2, J4, J7) inserted by machine: only a tweezer with 0.8 mm of jaw room, or hands; this view did not develop pairs in insertion.
- Stripping silicone as a controllable process: the view measures and retries around borrowed blades but has no mechanism of its own for a clean tear.
- A precise act for the SO-101 arm: no variant was found where the arm does anything finer than carrying into a funnel.
- What happens inside the crimp (voids, strand distribution, cut strands under 1.7 % of force): cameras and force traces cannot see it, and sectioning stays manual.
- A single-actuator machine that covers split to insert: every whole-procedure variant here is several stations on a stage.

## Questions for Derek

- Would you buy an OTP side-feed XH applicator and a reel from eBay or Made-in-China (not on Prime, so weeks) to open v9, v9b and the jack test? Or stay with kit contacts, where v8 feeds hand-tool-as-press's a4c or a6c?
- The shadow photograph: a stripped conductor laid in a kit contact, jacket in the insulation barrel, from straight above with one LED at about 65 deg from each side in turn. Does the bundle's shadow show beside it? Push one strand down to the floor: does it lose its shadow?
- The tack test: close a kit contact's insulation wings lightly on the ribbon with smooth pliers and pull with a hook and the 0.1 g scale. Does it hold ~0.2 N and slide off at ~1-2 N without marking the jacket?
- The lance: one kit contact barrels-up on the 0.1 g scale with a probe on the box top. What force at 0.1, 0.3 and 0.6 mm of travel, and does the lance spring back?
- The neck: under the ELP beside a steel rule, how long are the conductor barrel, the window and the gap between box and conductor barrel, and where does the lance tip sit?
- Would a crank or eccentric press get its own NEMA 23 and DM542T, or share the weld rotator's?
- On anything built round the shop press, is an interlocked guard over the crimper faces acceptable, with the fork's parked position and the force-ceiling switch in the same enable line?
- Which control stack feels like home: your own PlatformIO firmware beside a printer as bought, FluidNC, or Klipper?
- May Claude pass a borderline crimp on its own, logged and later checked against its measurement, or only propose?
- Asks: a push to your phone with a photo and three buttons, through a Claude session you follow, or only at the bench?
- Would you request JST's XH handling manual (CHM-1-151) for the genuine crimp height?
- Does the ribbon's web zip apart cleanly by hand, or tear (repo Open item 5)?
- For production: kit contacts, genuine SXH on strip or reel, or BXH loose?
- Is a point micrometer welcome on the bench to calibrate silhouette heights?
- Is a Mac left awake for a run acceptable, or would you rather give the cell its own small computer?
- Is a $186-219 Ender 3 V3 SE acceptable as a stage, upright or on its back?
