# freedom — notebook (Freedom and force)

Framing: an arrangement is a set of motions that are free, restrained, driven or locked, and the forces that push along each. Precision belongs to whichever motions are constrained at the moment it matters. For every arrangement: which motion is free, which force displaces it, what happens at each contact, when the constraints change, who supplies precision at each moment.

Tags: **[Derek] [repo] [manual] [derived] [unknown]** as in `context/shared-context.md`. **illustrative** = a number I chose to make a scene or script run; it is not a measurement and not a requirement.

## Wave 1 — the wide look (one line each; silly ones kept)

The twelve lines, with the ids of the idea files (`ideas/`) and scenes they became:

1. **Ring-and-bungee, as Derek wrote it.** Two openable loops (nozzle end, cable pair at the grip base), each hung by a wire in Z and pulled sideways by a bungee pair in X or Y; a printed shell gripped by an arm somewhere along its length. The loops carry weight and cable pull; the arm locates. → `freedom-01-ring-bungee` (deep; scene `freedom-01-ring-bungee`).
2. **Seat, not loop.** The nose contact is a spherical collar on the shell resting in a cone ring near the nozzle: three translations fixed by gravity and preload, all rotations free; the tail is the lever. Pivot sits tens of mm from the dot instead of 279 mm. → `freedom-01b-nose-seat` (developed; scene `freedom-01b-nose-seat`).
3. **Who is the master of each axis?** Bungee as *preload* with a hard stop as the locator; bungee in series with a motor (series-elastic: force from stretch); bungee alone (compliance). Same rubber, three jobs. → `freedom-01c-master-per-axis` (developed; scene `freedom-01c-master-per-axis`, also visible in scene 01's supports).
4. **Monitor arm as the weight path only.** A gas-spring arm is a neutral-equilibrium support held by friction; it carries gun and umbilical. A small XYZ vernier between arm tip and shell is the location path. Arm friction and creep are the disturbance. → `freedom-02-balanced-arm` (deep; scene `freedom-02-balanced-arm`).
5. **Six taut lines.** Gun shell hung from six cables; lengths *measured* (draw-wire encoders on a hand-positioned or bungee-floated gun; software moves nothing) or *driven* (winches). Gravity and umbilical pull close the force loop; the map of where every line stays taut is the design. → `freedom-03-cable-platform` (developed; scene `freedom-03-cable-platform`).
6. **The tangent is free.** The seam is a circle under a rotator, so only radial and vertical dot position (plus orientation through the lever) must be held; the tangent slide costs s²/2r. → `freedom-04-free-tangent` (developed; scene `freedom-04-free-tangent`).
7. **Runout is a known periodic force, not a stiffness problem.** Runout at the weld circle repeats once per revolution; a dry-run fits amplitude, phase and a per-tube offset; a ±0.5 mm vernier follows the rotator angle. → `freedom-05-runout-table` (developed; scene `freedom-05-runout-table`).
8. **Lock-and-release arm.** One-knob-lock articulated arm free while a hand or vernier positions the gun, all locked to weld. → `freedom-06-lock-and-release` (rough; scene `freedom-06-lock-and-release`).
9. **Floating gun leaned on the work.** Gun nearly weightless; a two-roller shoe kisses wall and rim under a preload software sets; contact restrains the critical axes while engaged; retract is the tube swap. → `freedom-07-floating-on-work` (rough; scene `freedom-07-floating-on-work`).
10. **Gravity as the tilt actuator.** Gun on a low-friction pivot above its COM, orientation trimmed by shifting a mass; gravity is the (weak) restoring force. → `freedom-08-gravity-tilt` (rough; scene `freedom-08-gravity-tilt`).
11. **Observe only: pose logger on a hand-positioned floating gun.** Six draw-wire encoders and a camera; software moves nothing. → `freedom-09-pose-logger` (sketch; the *sense* mode of scene 03).
12. **Move only, blind: nudge box.** Open-loop stepper vernier, known increments, mechanical home stop; a person watches the dot. Coda: spring-driven retract with a latch. → `freedom-10-nudge-box` (sketch; the retract coda has scene `freedom-10-spring-retract`, the nudge box none).

## Wave 1 — log

### Tools and reference

- Read the context files, the kit README, the two reference scenes' source, and ran `check-scene.mjs 00-reference-orientation --shot` (renders, 39% content). Kit `cornerInset` needs only an object with `dotOffset()` and `beamDir()`, so my 3D scenes pass a small proxy that carries the *true* (un-exaggerated) offset while the drawn pose is exaggerated.
- Wrote `calc/statics.js`: one rigid body plus massless ring nodes on springs, wires that only pull, ring pins, seats, a friction-limited slide, a sphere-in-cone seat, point pins, rotational stiffness. Newton with damping and a numeric Hessian; returns the equilibrium pose and the Hessian, from which come the dot's compliance (mm/N) and the soft motions. `calc/ringmodel.js` builds the ring-and-bungee and the nose-seat/bridle arrangements on it. 10 to 40 ms per solve. Everything numeric fed to it is **illustrative** (1.2 kg, COM offset, bungee k, arm k, umbilical 2 N); gun mass and COM are **[unknown]**.
- Checks (`calc/02-sanity.cjs`): an arm alone carries exactly the weight (11.77 N) and sags W/k_arm. Two kinks in the energy (taut/slack switching and the cone apex line) made Newton stall; the unilateral terms are smoothed (0.02 mm) and the cone apex regularised (0.05 mm). Noted on the scenes as modelling notes, not findings.
- `calc/20-balanced-arm.js` is the model behind scene 02 (a single balanced boom with friction, pre-sliding and a payload-rating window). `calc/22-cable-layout.cjs` is a random search for a six-line layout with all lines taut across a small range of umbilical pull; `calc/23-cable-platform.cjs` uses it; scene 03 uses the same layout. `calc/25`, `26`, `27` are small numbers for ideas 10, 3, 12.
- Sourcing: `sourcing/freedom.md` (Prime-only on Amazon, each product page checked for the buy-box Prime badge, 2026-09-28).

### What the model said before anything was drawn (`calc/06-tables.cjs`, `08-hinge-torque.cjs`, `09-slide.cjs`)

- **A vertical wire through a loop cannot carry the weight of an inclined barrel** (round 1 of freedom-01). Smooth loop: the barrel slides until the wire slacks; the arm carries 12.0 N of 11.8 N. A collar seat (wire 7.7 N, arm 4.7 N) or a rubber loop (friction limit 4 N: arm 6.7 N) repairs it.
- **A stiff wire is a position, not a force.** With a 200 N/mm wire on Z the arm's Z command moves the dot −0.04 mm per mm; with a bungee or balancer 0.93 to 0.99. One master per axis. Asked to null the arm force, a stiff wire needs 204 N.
- **Grip changes everything**, as Derek said: rigid grip gain 0.93 to 0.99 and 0.3 to 0.9 mm/N wherever it grips; ball-ended grip gain 0.4 to 3.4 with cross-coupling and 1 to 120 mm/N.
- **The two loops define a hinge** close to the reference scene's grip axis. With the illustrative COM 35 to 61 mm off the line, gravity puts about 0.5 N·m on it at the working roll and wants ~131° more roll; a counterweight to remove that is 0.73 kg at 90 mm.
- **Twist.** The grip-axis roll is a rotation about the cable's own exit axis; the manual forbids twisting the fibre (p. 20). Flagged in every scene that rolls the gun.

### What drawing exposed

- Drawing scene 01 made the *cable* a design object: a loop on the bare cable 120 mm out drags a 149 mm bend radius, against 240 mm stored / 350 mm emitting [manual p. 20]; even the plain route from the exit to the floor sits near 315 mm.
- Scene 01b's first version put the collar 16 mm behind the nozzle. Drawing the cup put its apex 4 mm above the plate and inside the bore: it cannot be built there; from about 60 mm it clears.
- Scene 03's first four-line version looked taut and fine; only the readout (62 mm, 66° off) exposed that taut is not held.
- Scene 07's first section drew the rim at the wrong height; fixing it made the two-roller shoe's clearance beside the beam visible as a real problem.

### Rounds (break, repair, branch) — details are in each idea file

- freedom-01: eight rounds (smooth loop slides; stiff wire vs arm; rings alone don't locate; hinge and gravity; base loop as a cable problem; bungee stiffer than the arm; how the arm grips; Derek's third ring: arm load 5.0 → 3.0 N with a rigid grip, 7.3 → 4.0 N with a ball end, and its bungee axis shapes the range). Branches: 01b, 01c; siblings 02, 03, 06.
- freedom-01b: four (two ball joints leave a hinge; the seat is unilateral and the cable pulls it out; where the cup can physically be; numerical note).
- freedom-02: six (monitor arm too flexible; payload floor 2 kg; friction window; cable on arm; brake vs stiffness; motor sizing).
- freedom-03: five (four lines under-constrain; slack; stretch; frame spread; measuring loads the thing measured).
- freedom-04, 05, 06, 07: three or four each; 08, 09, 10, 01c: entries in the files.

### Combinations I see

- 01b (seat at the nose) + 05 (runout table) + 03 (bridle as two of the six lines): position by the seat, orientation by lines, per-tube offset by a table.
- 02 (balanced arm carries) + 07 (roller shoe locates while engaged) + 05: the cheapest version I can imagine that works on bought parts: a balancer or monitor arm, a shoe, a vernier fed by a dry-run.
- 03's sense mode as the observer for any of the others.

## Arrangements held (running summary, current after wave 1)

The running summary lives in `index.md` (current, with the wave 2 additions) and in the structured return; this table is the wave 1 state. Nothing is ranked. Origin: derek-example, branch, swarm.

| id | arrangement | origin | depth | scene | assigned to / carried by / position by |
|---|---|---|---|---|---|
| freedom-01-ring-bungee | two openable loops (tip, cable pair), wires in Z, bungees in X or Y, arm grips the shell; every contact and grip solved | derek-example | deep | freedom-01-ring-bungee | arm XYZ / wires + bungees, arm carries the rest / the arm |
| freedom-01b-nose-seat | ball collar in a cone seat at the nose, tail on a two-wire bridle and yaw bungee | branch | developed | freedom-01b-nose-seat | nose stage XYZ + tail winches / the seat + tail wires / the seat |
| freedom-01c-master-per-axis | bungee as compliance, preload against a stop, or in series with a motor | branch | developed | freedom-01c-master-per-axis | stop, arm, motor anchor / springs by stiffness / the stiffest element |
| freedom-02-balanced-arm | gas-spring arm carries; XZ vernier and camera locate | derek-example | deep | freedom-02-balanced-arm | vernier (+ optional shoulder motor) / spring and arm / vernier and camera |
| freedom-03-cable-platform | shell on six taut lines, encoders (observe) or winches (drive) | swarm | developed | freedom-03-cable-platform | six lengths or none / lines in tension / the frame |
| freedom-04-free-tangent | which motions must be held: tangent second order, tilt = pivot lever | swarm | developed | freedom-04-free-tangent | none / not modelled / seam geometry |
| freedom-05-runout-table | runout as a fitted table, vernier follows the rotator angle | swarm | developed | freedom-05-runout-table | vernier over angle / the support (mean only) / model + angle index |
| freedom-06-lock-and-release | friction articulated arm, free while placing, locked to weld | swarm | rough | freedom-06-lock-and-release | lock actuator, hand or vernier / joint clamps / nothing in the arm |
| freedom-07-floating-on-work | floating gun with a two-roller shoe on wall and rim, preload set by software | swarm | rough | freedom-07-floating-on-work | preload actuator / balancer / wall and rim while engaged |
| freedom-08-gravity-tilt | gun hung above its COM, gravity sets tilt, trim mass adjusts | swarm | rough | freedom-08-gravity-tilt | trim mass / the pivot / gravity + trim |
| freedom-09-pose-logger | observe only: six draw-wire encoders and a camera on a hand-positioned gun | swarm | sketch | sense mode of freedom-03 | nothing / a passive support / the hand |
| freedom-10-nudge-box | move only, blind: stepper vernier with a home stop; coda: spring retract with a latch | swarm | sketch | freedom-10-spring-retract (coda) | steps, latch / the stage, spring energy / the stop and screw |

Connecting ideas to hand a partner: one master per axis (01c, 01 rounds 2 and 6); pivot near the dot with the actuator far (01b, 04); the tangent is free (04); carry with one thing and locate with another (02, 07, 05); a contact carries precision only while it exists (07, 01b); tension-only supports are bounded by slack (03); measuring loads the thing measured (03, 09); forces tell you about an arrangement even when position is known coarsely (01, 01b, 01c, 03).

Tools partners can use: `calc/statics.js` (one rigid body on springs, Newton solver, Hessian, dot compliance; page or node), `calc/ringmodel.js`, `calc/20-balanced-arm.js`, `calc/22-cable-layout.cjs`/`.json`.

## Wave 2 (exchange with eyes; borrowed works on my ideas and answers in wave 3)

### What I did

- Ran `check-scene --shot --exercise` on all eight of eyes's scenes (the shared machine was loaded, load average 50 to 70; the stock 20 s navigation timeout failed every run, so I used a copy of the checker with longer timeouts kept in my scratchpad; it changes nothing else). All eight pass. Looked at every thumbnail and the per-control shots for eyes-01, and drove eyes-01's camera sweep against the revised kit (pose A, clock 0: clear from 30 to 130 mm, as eyes-01 says).
- Read all of eyes's ideas, their notebook, and the digest. Chose five ideas: eyes-01 (deep, stressed), eyes-05 (sketch, developed with a scene), eyes-09, eyes-11b (sketch), eyes-04. Wrote `exchange/freedom--on--eyes-w2.md` (five sections, three named combinations, four smaller remarks on eyes-06, 07, 12).
- Three scenes from the exchange: `freedom-11-eye-on-the-seat` (combination of eyes-01 and my 01b), `freedom-12-touch-trigger` (branch of eyes-05, combines my 07 and datum-07), `freedom-13-map-and-step` (branch of eyes-09, combines my 05). Their idea files are `freedom-11`, `12`, `13` in `ideas/`.
- Two new ideas in thin regions of the digest: `freedom-14-hand-plus-guidance` (hand supplies motion, software supplies a bounded force; scene, rough) and `freedom-15-pull-ledger` (the umbilical, wire conduit and gas hose as the design driver; sketch with numbers, no scene).
- Calculations: `calc/eye-support.js` (a support model with a trim loop, reused by the scene), `calc/29`, `30` (mm per newton by support), `31` (the fibre as a spring and force gauge).
- Sourcing (Prime only, own tab, closed): 3 mm chrome steel balls, the EISCO Newton force meter (`sourcing/freedom.md`, wave 2 section).
- Appended short "Wave 2" notes to my own idea files 01b, 01c, 05, 07, 09, 10.

### What broke, what I learned (rounds, details in the idea files)

1. **eyes-01's loose support holds no rotation.** Drawing the support's rotation (the scene's drift slider is a translation) took the gun 29° from the hand-set pose and moved the dot 1.4 / 4.2 mm per newton; one newton was 1.0 to 1.8 N of trim range. A rigid base gives 0.45 / 1.0 mm per newton (5.8 N fills the trim), the nose seat 0.10 / 0.01. The elastic in the drawing carries the weight only at about 53 N of tension.
2. **The cup and the camera want the same barrel.** With the collar at 70 mm the camera map (11 clock angles × 6 stations, drawn line of sight, cup and stage as occluders) has 34 of 66 stations clear against 47 of 66 with a rigid lug. The default camera (85 mm, clock 0) reports blocked by cone seat. Found by the scene's own badge, not predicted.
3. **A bug of mine, kept as a note:** the first version of the loop nulled the *world x* of the dot, not the radial offset from the seam circle; with a 10 mm tangent slide the residual read 0.78 mm (s²/2r). The eye sees the seam-relative radial; fixed in `eye-support.js` (`rad`). And freedom-14's first sign of the guide force was wrong (it pushed the gun away from the seam and made every help worse); a wrong sign gives a plausible-looking bad result, so I checked the algebra against the trace.
4. **Silent string-replace failures.** Several of my scripted text edits did not apply because the file held real characters where my pattern had escapes; I found them by grepping the result. Worth checking any scripted edit by reading it back.
5. **The touch measures the support.** Trigger force over path stiffness: 1.3 mm short on a 0.15 N/mm bungee axis for 0.2 N; 3 µm on the seat's nose stage. The plate touch takes 1.5 N against 0.18 N for the wall.
6. **The pull is mostly the fibre's own recoil**, EI/R² ∝ 1/R²: 0.4 to 4 N at 350 mm and 0.9 to 8.7 N at 240 mm for EI 0.05 to 0.5 N·m². A step of pull at bead start is force × compliance, and the map cannot contain it.

### Borrowed (from the digest; what I use, and where)

- **datum-07 (touch-off):** the fast-then-slow double touch, the latency arithmetic (speed × latency) and the CR Touch as a ready-made single-axis probe; in `freedom-12-touch-trigger`.
- **trials-02 (dock, three load cells) and travel-08 (load cell in the cable balancer's line):** a load cell in the support as the input of a force term; in `freedom-13-map-and-step`. travel-08 also states the cable's lateral-stiffness placeholder that I replaced with 3EI/l³.
- **borrowed-05 (guide star):** nudge-and-watch to learn a compliance table and the backlash from a reversal; the span calibration of eyes-04's pads (exchange section 5).
- **use-04 (the lap):** the 49 s clock and the "change since the dry lap" slider; freedom-13 puts a number on that change.
- **eyes-11 (IMU, gravity sees pitch and roll):** the observer for the tail loop of 01b (named in scene 11's I/O panel).
- **eyes-02 (dome):** the camera map of scene 11 is the dome with the support's own parts as occluders.
- **datum-04 (corner follower):** the ball feeler is the leaning contact of `freedom-12`.
- **borrowed-01 and borrowed-02 (rotations through the dot):** the kit's cable exit axis passes through the dot, so an axial pull is torque-free about any pivot on that line (freedom-15).
- **borrowed-11 and travel-08 (festoon, balancer, gallows):** the way to make the pull small and constant: route the fibre at the largest radius and carry its weight elsewhere.

### The arrangements I now hold

See `index.md`: the twelve wave 1 ideas plus 01c, and `freedom-11`, `12`, `13`, `14`, `15`.

## Wave 3 (revise, and the new direction)

### What I did

- Read borrowed's critique (five sections, six combinations, a page of smaller remarks), the digest, my own notes and the kit 1.1.0; opened borrowed's five scenes that name one of mine (`borrowed-13`, `-14`, `-15`, `-16`, `-19`) in a headless browser and drove their controls; re-ran their numbers (all reproduce). Wrote `exchange/freedom--reply-to-borrowed-w3.md` (one section per critiqued idea, each decision named: revised, branched, answered and kept, adopted, left standing) and put every point into the idea file's "What was tried to break it" in the same form as before, marked as coming from borrowed's exchange.
- Scenes revised in place (refinements, not material changes): `freedom-02` (mismatch in grams, payload from parts, the vernier's torque share), `freedom-03` (taut margin, worst direction and ±10° cone, a warning for a layout taut by a hair), `freedom-08` (period, damping ratio, a 1 N step, the cable's lever and couple as sliders, a rotary damper), `freedom-14` (the damper as a rotary part with a lever), `freedom-10` (a soft-close damper), `freedom-06` (text), and two mistakes fixed while opening scenes as a stranger: `freedom-01b` (a NaN readout, an ellipsoid too small to see) and `freedom-01c` (raw decimals in labels).
- New direction, the umbilical and the wire conduit as the design driver: three ideas. `freedom-16-fibre-line` (deep; 3D, four routes, a planar elastica solver written for it), `freedom-17-hung-on-the-line` (a combination of freedom-08 and borrowed-15: the sled pivot on the roll axis in the kit's geometry), `freedom-18-roll-into-twist` (a lens on the roll, twist and swing).
- Sourcing (Prime only, own tab, closed): a cable pulling grip, a ball-bearing swivel, a ball-bearing pulley, a 600 mm MGN12 rail, constant force springs, lead shot (`sourcing/freedom.md`, wave 3). A second and third tool search was needed to load the batch and script tools for the browser.
- Ran `check-scene --shot --exercise` on all my scenes; opened each as a stranger in a headless browser (screenshots, control kinds, text with NaN or long decimals).

### What broke, what I learned

1. **The cable is a wrench.** A force, a couple and a lever, and the wrench on the gun is the wrench where the last rigid part of the shell lets go of the cable. A boot printed onto the shell takes the bend inside; what is left is a straight span. That changes the ledger more than any support idea did.
2. **A clamp at each end is a trap.** A clamped fibre with any slack is post-buckled at about 4π²EI/L²; a clip 10 mm or 5° off puts 2.4 to 2.8 N on the gun and breaks the bend limit. My earlier estimate of the pull, EI/R², is the floor for an exact route. A collar that slides on a rail has no such trap.
3. **A straight taut tether was my first idea and it is wrong.** I drew a constant force along the roll axis through the dot to make the pull torque-free. With EI 0.1 the span sags 2.4 mm with no tension; tension only adds a constant force and a static torque; and a taut span's sag tilts the pull's line 100 mm off the dot unless the rail is aimed to compensate. The line through the dot matters for the axial forces (feed push, friction), not for the lateral ones, and it makes the roll pure twist. Default rail force: zero.
4. **The kit's exit tangent is not on the roll axis.** The stub leaves along the grip's rake, 30 degrees off. My own earlier notes said "the roll is a rotation about the cable's own exit axis": not in the kit. A roll is part twist, part swing, and only a boot that lands the fibre on the axis makes it pure twist. That is what freedom-18 is about.
5. **Twist is moved, not removed.** A swivel or a ring frees the fibre at that point and the rotation is still held at the laser unit's connector: twist rate = roll / distance to the first hold.
6. **Stiff-rotation supports make the route a second-order concern; soft ones make it the first.** Every step (5 mm anchor, 0.5 N feed push, 10 degrees of roll) is a fraction of a millimetre through the arm and the seat and millimetres through one elastic with gravity only. The route matters most where the support is softest in rotation.
7. **The plumb-bob is a trim, not a locator, for every route that lets go far from the pivot.** In the kit's geometry the roll axis is far from the centre of mass, the keel does two jobs, and a 0.03 N change at 440 mm of lever needs 26 N·m/rad to hold 0.1 mm against 0.45 from gravity.
8. **borrowed's arithmetic reproduces.** Every number I re-ran (0.091 kg, 88 g, 0.118 N·m, 0.13 N, 5.5 N, 0.99 s, 2.0 N·m·s/rad, 176 mm) matched to the digit. Where their critique hit a scene of mine it hit a real mistake: a readout that said "all taut", a scene with no time, a payload that left out the stage.
9. **Silent edit failures again.** The Write tool turns `\u00b0`-style escapes in a file into real characters, so several of my scripted replacements did not apply until I grepped for the result. Read back every scripted edit.
10. **A model I could not close.** A seat with its ball moved onto the roll axis did not converge in the statics (the tail wires and the cone apex have to be solved together for a ball 44 mm below the barrel). I did not claim it; `calc/35-seat-on-line.cjs` is the record, and the estimate (36 N·mm per newton at the barrel seat against zero) is stated as an estimate.

### The arrangements I now hold

See `index.md`: the wave 1 and 2 ideas plus `freedom-16`, `freedom-17`, `freedom-18`; borrowed's `-13`, `-14`, `-15`, `-16` and `-19` are listed as related arrangements of theirs that answer mine.

## Open threads

1. **Numbers only Derek can supply** (each with the idea it belongs to in `index.md`): where the fibre leaves the grip base and in which direction; the fibre's weight and stiffness (overhang test); the maker's limit on twist and tension; the gun's mass and balance point; the drop time at a candidate pivot; the wire-feed push (dial gauge, laser off); the umbilical's pull along and across the exit; how far his relaxed hand yields per newton; the vernier's and camera's weights; a fluid head's drag; a P-clamp's friction; runout and plate seat depth of a few tubes; whether the red dot sits on the melt.
2. **The rod model is planar and frictionless.** Contact with the bench, friction on a hook, out-of-plane gravity, hysteresis and creep of the sheath are not modelled; the twist and swing under roll for route A use small-angle beam formulas, not the solver. A 3D rod (with twist) would replace them.
3. **Statics of a seat with its ball on the roll axis** did not converge; a solve that finds the tail wires' lengths, the cone apex and the yaw anchor together would settle whether the pivot on the line buys anything for a stiff seat.
4. **Untouched from wave 1 and 2:** freedom-09's own scene; the nudge box of freedom-10; eyes-03 tags in place of the pose logger's encoders; the vertical axis and tilts of freedom-14; lift-away and wire break-off as a design driver; the work in another orientation (tube axis horizontal or inverted); the station around the arrangement (lighting, fume, the camera's own mounting).
5. **Answers I am waiting for:** from borrowed, whether they read the route-first answer on the six lines as settling the layout question; from eyes, the state the dry turn is taken in (still open from wave 2).
6. **Things I would attack in my own work:** (a) freedom-16's support presets are round numbers, not statics; the ordering of supports is robust, the millimetres are not; (b) the rail's stiffness and alignment at 0.75 m are assumed, not designed; (c) freedom-17's centre of mass is illustrative and moves every number; (d) the boot is a tube on a picture: its clearance to the hand grip and the wire guide is a fit test; (e) freedom-18's GJ = 0.8 EI.
7. **Thin regions I did not reach:** the gas hose beside the fibre (not drawn, never in a ledger row with numbers); the umbilical for an orbiting crown (datum-03b: 380 degrees of orbit); a fibre lying on the bench (rotational hold by friction along its length).
