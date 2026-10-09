# travel - Split the travel (notebook)

Framing: the relative pose between gun, tube and room can be produced by moving the gun, the tube, a support or a setup adjustment; by motor, hand, spring or gravity; at setup or during the weld. A small angle at the grip is a long travel at the dot. Questions: which body moves and which stays, what range and resolution each stage needs, which stage's error shows up as which error at the dot.

Source tags used below: **[Derek] [repo] [manual] [derived] [unknown]** as in `context/shared-context.md`. Numbers marked *illustrative* are mine, chosen to make a picture, not measured. No budget applies anywhere in this notebook.

---

## Wave 1, step 1 - what the geometry says before any arrangement (calc in `calc/`)

Facts I keep coming back to. Each is derived from numbers in `shared-context.md`; the scripts are in `calc/`.

1. **The seam is a circle, so one of the three translations is free.** The rotator turns the seam through the station; moving the gun (or the tube) along the tangent by s does not leave the seam to first order (radial error = s^2/2r, 0.008 mm at 1 mm). **[derived]** `calc/02`. The horizontal plane therefore holds only two real position requirements (radial error, and plan angle), not three.
2. **A tangent shift of the work is a plan-angle rotation with a built-in 1/r reduction.** Shifting the tube along the tangent by 1 mm turns the seam normal by 0.93 deg relative to the gun; about 1.08 mm of tangent travel per degree of plan angle, 1 micron = 0.0009 deg. So the "vertical-axis" rotation of the orientation scene can be produced by a plain linear stage under the rotator, with the dot staying on the seam if the radial axis moves too (dx = r(1 - cos psi), dy = r sin psi). **[derived]** `calc/02`.
3. **Lever arms decide where an angle becomes a distance.** In the kit's illustrative proxy at the reference opening pose the dot is 93 mm from the barrel middle, 190 mm from the grip top, 279 mm from the grip base: 1 deg = 1.6 / 3.3 / 4.9 mm at the dot. A pivot at the dot gives 0. **[derived from illustrative geometry]** `calc/01`.
4. **Moving the work does not remove the Abbe problem; it moves it.** The seam stands 232 mm above the rotator's feet **[derived from repo numbers]**, so a 0.05 deg tilt error of a stage under the rotator is 0.20 mm at the dot, comparable to a gun-side joint with 200-280 mm lever. Only the change in tilt across the range actually used matters, so short-travel stages suffer far less than long-travel ones. `calc/03`.
5. **Runout is slow.** 0.25 mm radial TIR **[repo]** is a 0.125 mm sinusoid; at 15 mm/s the fastest it changes is 30 microns per second. A follow stage needs range about 0.3-0.5 mm, resolution a few microns, and almost no bandwidth (about 6 steps/s of 5 micron). `calc/04`.
6. **The reference pose leaves 5 mm between nozzle tip and the rim plane, inside the bore.** With the kit's illustrative 16 mm nozzle clearance and 44.6 deg beam, the tip is 5.0 mm above the rim and 55 mm from the axis. So (a) with the gun seated the tube can be lifted only about 55 mm before its rim meets the barrel, so it cannot be lifted out (a straight lift-out needs the gun raised about 144 mm); lifting 12 mm and sliding it out sideways needs the gun raised about 13 mm (`calc/07`); (b) a purely horizontal shuttle of the whole rotator with no lift under a fixed gun is collision-free only while 16 cos(beta) > 6.35 mm, i.e. beta < 66.6 deg from vertical, and only with the wire retracted (`calc/05`). **[derived from illustrative geometry]** (An earlier version of this line said the tube cannot be lifted at all; `calc/07` showed that was wrong.)
7. **The existing tube nest is already a fine stage nobody counts.** Three M3 radial adjusters bear on the tube OD inside 0.20 mm (ID pilot) / 0.40 mm (outer guide) nominal radial clearance **[repo]** `hardware/printed-parts/fixtures/weld-rotator/README.md`. It is a manual radial stage of a few tenths of a millimetre, on the rotating side.
8. **The head has a built-in one-axis fine stage.** The X1 Pro sweeps the beam (wobble, 2 mm at 80 Hz recorded) and the settings screen has a left/right "red light alignment" adjustment **[manual]** pp. 25, 39. Whether either can offset the process beam and how far, and whether the RS232 "PC-based supervisory software" port exposes it, is **[unknown]**. Later: a third-party explainer for handheld guns says the red-light offset moves only the red pilot, not the weld beam (unchecked for the X1 Pro), so this may be a calibration setting, not a stage: see `ideas/travel-12-heads-own-stage.md`.

---

## Wave 1, step 2 - twelve arrangements, one line each

Written before developing any. Silly ones stay. "Moves" = which body moves; "by" = motor / hand / spring / gravity.

| # | Arrangement (working name) | One line |
|---|---|---|
| T1 | **The tube travels** | Gun stays put in a hand-set, locked holder; a small XYZ stack under the rotator (motor) moves the work; tangent shift doubles as plan angle at 1/r; umbilical and wire never move. |
| T2 | **Cascade** | Hand puts the gun in the neighbourhood, a motor stage trims the per-tube offset, a tiny follow stage replays the revolution's runout: each stage sized by what the one above leaves; software closes the loop only if it can see the dot. |
| T3 | **Dot-centred orientation** | The gun (or the work) turns on arcs whose centre is the dot, so orientation moves cannot displace the dot and position stages never inherit lever errors; software sees two decoupled interfaces. |
| T4 | **Return seat** | The gun swings or slides away for tube swap (and end-of-weld lift-off, if the sequence has one: unconfirmed) and returns to a magnetic kinematic seat; adjust once per lot, return every time; the hard stop, not the motor, is the position. |
| T5 | **Nest driver** | The rotator turns its own three nest screws around to a stationary powered driver; software indicates the tube (probe or camera), nulls eccentricity before the weld: work-side fine stage from parts that already exist. |
| T6 | **Hand moves, software reads** | Hand-cranked cross-slide (or lockable gun holder) with digital scales; software reads every stage position plus the dot and tells the person which wheel to turn how much: software observes and moves nothing. |
| T7 | **Software moves, a person is the eye** | Steppers with home switches and stored per-lot offsets, no measurement: Derek looks at the dot and says "0.2 in"; the AI moves the axis: software moves and observes nothing. |
| T8 | **The cable gets its own travel** | Umbilical and wire conduit ride a constant-force balancer / gallows that carries their weight and swings with the gun, so the fine stage sees only the gun and a residual of grams. |
| T9 | **Ratio devices** | Put the reduction where the motion is made: reducing lever with a flexure pivot, micrometer head or differential screw on a stepper, a soft link (series spring) between anchor and gun; travel and resolution traded on purpose. |
| T10 | **Rides the tube** | A non-rotating bearing collar (or rim skid) on the tube carries the gun and cable support, so gun-to-work position is set by the work; the room only stops the collar turning. |
| T11 | **The head's own fine stage** | Use the head's galvo axis (wobble width, red-light alignment) as a zero-mass +-1 mm radial trim if the laser software can offset it; nothing else moves. |
| T12 | **Print to adjust** | The AI computes a shim, spacer or wedge from the observed error and a printer or a shim peel makes the adjustment: a stage whose actuator is a printer (minutes) plus a hand. |

Also noted, not numbered:

- **Orbit instead of spin (silly).** The gun circles a still tube, like an orbital weld head. The fibre may not twist **[manual]** p. 20, which is why the work turns. Useful form: because the along-seam position is free (insight 1), the station azimuth can be chosen to suit cables, cameras and clearance; nothing about the seam depends on it.
- **Derek's examples read as allocations** (matrix below and in `travel-07-allocation-matrix`): monitor arm = gun carried and coarsely placed by hand/spring, joints locked in the weld; hole in the table = work Z by shelf, gun XY by gantry, table as height datum; suspension = Z by wire, one axis by bungees, shell rings choose where the constraints act.

### Derek's examples as allocations (what supplies which relative motion)

| Relative motion at the dot | Monitor arm | Hole in the table + gantry | Suspension (rings, wire, two bungees) | T1 tube travels |
|---|---|---|---|---|
| radial (into the wall) | arm joints (hand, locked) | gantry axis (motor) | bungee anchor (hand/motor); stiffness sets the error | work X stage (motor) |
| along the tangent | arm | gantry axis | other bungee; free to first order | work Y stage, doubles as plan angle |
| vertical | arm, gas spring | shelf (hand or motor) | wire length | work Z stage |
| plan angle | arm wrist | not named | ring positions | work Y (1/r reduction) |
| pitch (hole axis) | arm wrist | not named | ring positions | gun holder, hand, locked |
| beam roll (grip axis) | arm wrist | not named | ring positions | gun holder, hand, locked |
| what carries the gun | gas-spring arm | gantry + table | wire and bungees | holder post |
| what carries the cable | arm/gun | gantry | rings | nothing moves |

The second and third columns leave rows blank because Derek did not name them. They are exactly the rows this framing asks about.

---

## Wave 1, step 3 - what I chose to develop, and why

- **Deep (several rounds): T1 tube travels** and **T2 cascade** (they meet: the stack of T1 is the medium stage of T2), with **T4 return seat** carried far enough to answer T1's biggest break (swap and retract clearance).
- **Developed: T3 dot-centred orientation** (two forms, gun-side arcs and work-side cradle), **T5 nest driver**.
- **Sketch: T6, T7, T10, T11, T12** (and T8 cable travel, later given a rough scene) - held in the table below and in short idea files.

Rounds for each are in the idea files under `ideas/`. The record of what broke is kept there next to the original.

---

## Wave 1, step 4 - rounds on the developed ideas

Scenes came first where the shape was definite (travel-01, 02, 03, 04 in that order), and drawing corrected the thinking three times: (a) the outside camera reported "blocked by the tube" for a dot that was actually inside the wall, because a camera sees where the red beam *lands*, not the focal point (scene 1 now tests the surface hit); (b) the first cascade plot put three stages on one axis and hid what each stage leaves (now one row per stage with its own scale); (c) my own claim that the tube "cannot be lifted off the nest with the gun in place" was wrong once `calc/07` computed it (lift works to about 55 mm; it is the lift-and-slide and the lift-out that fail).

### T1 tube travels (`ideas/travel-01-tube-travels.md`, scene 01)

- **Round 1.** Gun fixed and locked; XYZ under the rotator; tangent shift as plan angle at 1/r. Numbers: `calc/02`.
- **Round 2 (break).** Swap: horizontal shuttle works only while 16 cos(beta) > 6.35 mm (`calc/05`); lift and slide needs the gun raised about 13 mm, lift-out about 144 mm (`calc/07`).
- **Round 3 (break).** Abbe: 232 mm from feet to seam; 0.05 degree of layer tilt = 0.20 mm at the dot (`calc/03`); repair by short fine travel and hard-stopped long axes at the bottom.
- **Round 4 (break).** Holder stiffness per newton: 44 microns for a 12 mm steel rod 300 mm long, 6 for a 20 mm rod; a friction joint creeping 0.02 degree at 250 mm is 0.09 mm (`calc/06`). Force unknown.
- **Round 5 (branch).** Monitor arm carries, stack locates (travel-01b); table plate (travel-01d); hand-crank branch built into the scene.
- **What stays standing:** hard stop repeatability, cables on a shuttling rotator, gun mass and cable pull unknown.

### T2 cascade (`ideas/travel-02-cascade.md`, scene 02)

- **Round 1.** Hand -> motor -> follow, peak error at the dot 1.86 -> 0.14 -> 0.04 mm radial (illustrative, `calc/04`).
- **Round 2 (break).** Latency 2 s leaves a quarter of the runout; repair by a table indexed by angle.
- **Round 3 (break).** Step 0.02 mm leaves 0.10 mm p-p; follow range 0.10 mm clips 0.25 mm TIR.
- **Round 4 (break, the allocation itself).** A printed flexure on the gun side moves 0.26-2 mm per newton of cable pull; spring-steel leaves 3-27 microns per newton (`calc/06`); the same flexure under the work sees no cable force and mass does not matter at 30 microns per second. So: fine stages under the work, nothing soft on the gun side.
- **Round 5 (combination).** T2 + T5 nest screws for the static radial part; face runout still needs a vertical follow.
- **What stays standing:** what sensor sees the dot at micron scale (nothing on Prime); whether the dry-run runout repeats in the weld.

### T4 return seat (`ideas/travel-04-return-seat.md`, scene 04)

- Round 1 seat; break: seat amplification (50 micron on a 30 mm circle is 0.24 mm at the dot); break: pin hinge overconstrains the seat -> forked slot; break: a 12 degree swing lifts the nozzle about 45 mm, enough for lift-and-slide, not lift-out; break: cables ride the swing (open).

### T3 dot-centred (`ideas/travel-03-dot-centred.md`, scene 03)

- Round 1: the lever table (`calc/01`). Break: no hinge can sit at the dot -> arcs. Break: beam roll about the dot-to-grip line is free for the dot but may twist the umbilical if it leaves along that line (**manual**: twisting forbidden); work-side branch leaves the cable alone but tilts the ball race. Repair of "arcs must be centred exactly": have the AI watch the dot walk and feed the residual forward.

### T5 nest driver (`ideas/travel-06-nest-driver.md`, scene 06)

- Scene loop: TIR 0.360 -> 0.111 -> 0.024 mm in two passes at slip 0.7 (illustrative). Breaks: over-determination (zero net advance), slip, clearance clip at 0.20 mm, cannot reach bearing or face runout.

### Cable travel and the sketches (`ideas/travel-08..13`)

- T8 cable travel (`travel-08-cable-travel`, scene `travel-08-force-path`): the cable eats k_ext/(k_stage + k_ext) of every gun-side move; torsion of the fibre found here.
- T6 hand moves, software reads (`travel-09`); T7 software moves, a person is the eye (`travel-10`); T10 rides the tube (`travel-11`); T11 the head's own stage (`travel-12`; a third-party explainer says red-light offset moves only the pilot: the idea is held with that against it); T12 print to adjust (`travel-13`).

## Insights that came out of the work (candidates for other explorers)

1. **The along-seam translation is redundant; XY of the work is exactly (radial, plan angle).** Any explorer's XY stage design over-asks if it has three independent horizontal freedoms at the dot.
2. **Beam roll is the one free rotation for the dot**, but it is a twist for the fibre if the cable leaves along the roll axis. **[unknown]** exit direction.
3. **Where a soft element lives matters more than its mass:** the cable pulls on the gun side, not on the work side.
4. **The nest screws are an existing fine stage**; the rotator can index them.
5. **A camera sees where the beam lands, not the focus**: a dot buried in the wall looks like a dot high on the wall; radial and vertical errors are entangled in what a camera sees. (For `eyes`.)
6. **Seat and shuttle give repeatable returns; motors give trims**: the two kinds of motion want different devices.

## Kit issues hit (also in the return)

- `WK.seamOffset` / `gun.dotOffset` assume the seam at its nominal place; scenes that move the work must compute the offset in the tube frame (`inverse(ws.tubeGroup.matrixWorld)`), and pass a custom object to `app.cornerInset`. A helper would help.
- `app.inset.markVisibility` tests a point; the visible dot is the beam's first hit on the work. A `gun.beamSurfacePoint()` would avoid false "blocked by the tube" when the dot is buried in the wall.
- `app.legend` on a custom stage sits over the lower left of the content; scenes must leave a blank strip.
- The checker once timed out with `__sceneReady` never true on a page that loads fine when opened alone (transient; reran clean).
- A file-write hook rewrites `\uXXXX` escapes into characters in the files I wrote; not a kit problem but string replaces in later edits must use the character.

## Every arrangement held (wave 1)

`summary.md` could not be written: the file tool refused a report-style file with that name ("subagents should return findings as text"). This section is its content, so the notebook stays the one continuity file. Nothing is ranked; maturity is depth of work only.

| Idea id | Arrangement | Depth | Scene | What moves, by what | Biggest thing standing |
|---|---|---|---|---|---|
| `travel-01-tube-travels` | Gun fixed and locked; XYZ + long shuttle under the rotator move the work; tangent shift = plan angle at 1/r | deep (5 rounds) | `travel-01-tube-travels` | work, motor (or hand wheels + scales) | hard-stop repeatability; gun mass and cable pull unknown |
| `travel-02-cascade` | Hand -> motor trim -> follow stage (runout replay) | deep (5 rounds) | `travel-02-cascade` | three stages by what the one above leaves | no micron-class sensor found; does dry-run runout repeat in the weld |
| `travel-03-dot-centred` | Orientation about the dot (arcs on gun or under work); beam roll free on the dot-grip line | developed | `travel-03-dot-centred` | gun or tube on arcs, motor | arcs need room; roll may twist the fibre |
| `travel-04-return-seat` | Swing-away carrier returning to a 3-ball magnetic seat | developed | `travel-04-return-seat` | gun on a hinge, small motor or hand | seat amplifies specks; cables ride the swing |
| `travel-05-lever-map` | Ratio devices: pivot, attachment, reducing lever, micrometer, gearbox, soft link | developed (calculator) | `travel-05-lever-map` | any angle stage | backlash of cheap reductions unmeasured |
| `travel-05b-soft-drive-hard-lock` | Branch of the lever map: a soft spring as a reduction gear, a clamp as the precision (Derek's bungees read as a gear) | rough | `travel-05b-soft-drive-hard-lock` | gun via a soft spring, motor anchor | friction dead band; gun position unobserved |
| `travel-06-nest-driver` | Rotator indexes its 3 nest screws to a powered driver; probe nulls eccentricity | developed | `travel-06-nest-driver` | tube in the nest, driver + rotator | probe sensor unresolved; bearing and face runout out of reach |
| `travel-07-allocation-matrix` | Lens: who supplies each relative motion, Derek's three examples plus these | rough | `travel-07-allocation-matrix` | none | cell wording is mine |
| `travel-08-cable-travel` | Umbilical and conduit on a balancer and gallows; force-path split | rough | `travel-08-force-path` | cable, spring | bundle weight and stiffness unknown; fibre torsion |
| `travel-09-hand-moves-software-reads` | Hand-cranked stages with scales; software reads and instructs | sketch | branch of travel-01 | hand | scale data output unverified |
| `travel-10-software-moves-person-sees` | Steppers with stored offsets; a person is the eye | sketch | branch of travel-02 | motor | size of tube-to-tube variation |
| `travel-11-rides-the-tube` | Non-rotating collar on the tube carries the gun | sketch | none | nothing under software | rim is not the seam |
| `travel-12-heads-own-stage` | Head's galvo sweep centre as a radial trim | sketch (held with a question) | none | mirror in the head | red light offset probably moves only the pilot |
| `travel-13-print-to-adjust` | Computed shim or spacer, made by printer and hand | sketch | none | printer + hand | printed thickness and creep |

Named branches and combinations not yet built as separate scenes: `travel-01b` (monitor arm carries, stack locates), `travel-01d` (table plate locates the gun, stack moves the work), `travel-03b` (work-side cradle: built in as a branch), T1 + T2 + T5 as one ladder, soft drive with a hard lock (now built: `travel-05b-soft-drive-hard-lock`).

Sourcing: `sourcing/travel.md` (18 Amazon Prime entries with Prime confirmation noted, 3 non-Amazon notes, 3 gaps).

## Wave 2 - exchange with datum (the seam is the datum)

Partner: **datum**. Exchange file: `exchange/travel--on--datum-w2.md`. `use` works on my ideas this wave and leaves a file for wave 3. All eight of datum's scenes were run through the checker with `--shot --exercise` (all OK; datum-04..07 needed a second, sequential run because the machine was loaded), their per-control shots read, and datum-01 (ring on the outside) and datum-03 (drag and tether at their limits) opened at states the shots do not show.

### What datum's set looks like through the framing

datum-03 is `travel-11` (rides the tube) with a design behind it; datum-02 is `travel-02` (cascade) with the stage in the gun's shell, where I found it should not be; datum-07 is a probe on the wrong side of the move. So the exchange asks of each: which element locates on each axis, what carries, what is free, where does the compliance sit.

### Chosen and why (five)

1. **datum-03 crown (deep, stressed):** the seat. Its scene puts the ring exactly on the outside, datum-01 charges a 0.20 mm clearance as +-0.10, neither is a seat. `calc/08`: k equal pads pass out-of-round harmonics k-1 and k+1 at gain 1; a pad soft enough to seat is as stiff as the ring; a tab tether turns a torque into a 3.07x force on the seat. Drawn: `travel-14-exact-crown`; sketch `travel-14b-crown-cartridge`.
2. **datum-02 signature (deep, stressed):** the hold between the dry turn and the weld turn; change of force times compliance (44 micron/N for a 12 mm steel rod) is twice the fit residual; a second dry turn in the weld state measures it; the constants are two thirds of the rms (`calc/10`). Drawn: `travel-18-signature-parity`.
3. **datum-07 touch-off (rough):** answer the "what carries and moves the tip" question with the tube-travels stack (the work comes to the stylus; a null measurement), and turn the largest term (tip-to-dot) into a calibration against the dot with the stack as the yardstick. Drawn: `travel-15-touch-stack`.
4. **datum-09 preplaced ring (sketch):** yaw does not become free; a family of attitudes does (gun over the bore, COM 118 -> 50 mm, no ring gap, a yoke). **I got the cable wrong first**: my quarter-turn route did not end tangent to a concentric track and made the radial-plane exit look 1.5 m shorter than it is; the scene (which reproduces datum-03b's own 5.6 m for pose A) showed A and B the same, and the G1 route in `calc/09` says the exit direction is not the fix, a weld that can go either way round is (190 degrees, 3.4 m). Drawn: `travel-16-radial-plane`, with a branch of my own (the wire guide carried by the ring, gun free).
5. **datum-12 wedge (sketch):** the wedge pivots at the bench, 232 mm below the dot; the station azimuth chooses which rotation the tilt supplies; two rings make a Risley pair. `calc/11`, idea `travel-17-risley-wedges` (no scene).

### Log of what changed my mind

- **The tether is a force.** A tab tether reacts the drag torque as a net force 233/76 = 3.07 times the drag; I had thought soft versus stiff was the only question. A wire pair wrapped on the ring is a couple. (Also: the stiffest element may go on the free axis at no cost, which inverts the intuition that the free axis should be the softest.)
- **Three-point centring is a filter with gain 1.** k equal pads pass k-1 and k+1; three pads pass ovality. That turned "the crown removes the runout" into "the crown swaps the rotator's runout for the tube's own out-of-round, and only vertical is a clear win".
- **A first calculation of mine was wrong and the scene caught it.** The orbit-cable claim above. Lesson recorded: a claim from a hand-built construction gets checked against a route the kit or another explorer's number reproduces.
- **What the hold does is small and specific.** `calc/10`: 0.006 to 0.128 mm per newton of change; nothing else in datum-02 is as easy to test (a second dry turn).
- **The hole-axis / grip-axis dials are not the beam.** Free rotations for the beam are tangent translation (already) and spin about the beam axis, which is a 0.91-for-1 twist of the fibre in the proxy, so freedoms count differently for the beam than for the dials.

### Borrowed (cross-pollination from the digest)

- **trials-02 (dock) and use-03 (preset cartridge)** -> `travel-14b-crown-cartridge`: the tube and its crown are a cartridge; the gun docks; presetting moves the depth measurement to a gauge on a plinth.
- **use-10 (wire first)** -> the parity dry turn (feeder jogging, gas on, laser off) in `travel-18-signature-parity`.
- **eyes-06 (the dot as the probe)** -> the yardstick that calibrates the stylus against the dot in `travel-15-touch-stack`; **trials-14 (contact sense)** -> the source of the one-bit contact; **trials-13 (pivot calibration)** -> the alternative route to the stylus-to-dot vector.
- **freedom-01b (nose seat)** -> the sphere-in-cone as another exact way to hold the radial-plane attitude; the free rotation about the beam axis is the roll it leaves free.
- **freedom-04 (free tangent) and borrowed-04 (axis map)** -> the free-axis lens: a free motion is where a stiff constraint costs nothing (the wire pair).
- **borrowed-05 (guide star)** -> how to find the stack's backlash without a gauge: nudge and watch.
- **room-04 / datum-03b (orbit the gun)** -> the orbit mode of `travel-16-radial-plane`, and the cable route.
- **datum-01 (datum chain)** -> its per-link spreads are the vocabulary of `travel-14` (ring clearance) and of the window in `travel-18`.

### Kit issues hit in wave 2

- `DIM.gunHeight` is 143 and `DIM.gunWidth` 34 in the kit: the gun is 34 mm wide, so my first trunnion pins at +-71.5 mm (I had read 143 as the width) floated 54 mm off the housing; fixed to +-21 mm. A yoke on a 34 mm housing has a short trunnion span.
- `WK.curveMinRadius` on a Bezier joined to a Catmull-Rom arc gave lower radii than the construction implies (a kink at the join); I compute the radius analytically for a G1 route and label it a construction.
- `ws.setWorkPose` and `ws.offsetOf` worked for the touch scene without any reparenting (unlike wave 1); ovality and seat depth have to be added by the scene.
- A bulk `str.replace('', ...)` after a failed slice corrupted a scene file to 13.9 MB; rewriting from the source in the conversation fixed it. Edits to scene files use exact strings or a rewrite.

### Sourcing in wave 2

`sourcing/travel.md` entries 19 to 23 (detent plungers, 1/16 in wire rope with crimps, HX711 amplifier, ER316L .035 in wire, a 12 in lazy Susan bearing). Prime confirmed on the product page for the ER316L wire; the others are Prime-badged search cards.

## Every arrangement held (through wave 2)

Wave 1's fourteen are listed in `index.md`; the new ones are `travel-14-exact-crown`, `travel-14b-crown-cartridge`, `travel-15-touch-stack`, `travel-16-radial-plane`, `travel-17-risley-wedges`, `travel-18-signature-parity`. `index.md` is the current list.

## Wave 3 - reply to use, and a new direction (bought arms and positioners)

Reply: `exchange/travel--reply-to-use-w3.md` (one section per critiqued idea, then the smaller notes). New direction: `ideas/travel-20-arm-joints-at-the-dot.md` (deep), `travel-21-arm-parks-rotator-turns.md`, `travel-22-arm-docks-then-floats.md`; sourcing entries 24 to 34.

### What use's exchange changed

- **A source I had wrong.** I quoted the head's lift-away at the end of a bead as [repo] in `travel-04`; it is the shared context's sentence and guide 46 says only "release the trigger, then the pedal". Corrected in the notebook, `travel-04`, `travel-01`, `travel-14b`, `travel-16` and `travel-07`'s scene. Every escape slider starts at 0.
- **Two scene mistakes fixed in place.** The clamp of `travel-05b` and the lock of `travel-14` added stiffness and no closing shift; `travel-04`'s 12 degree swing lifts the nozzle 54.5 mm, not about 45.
- **Re-run, not just accepted.** use's 81 % / 95 % (no look after the clamp / one relock loop) and the 49 / 82 / 81 bias case reproduce; friction costs rounds (median 3 at 0.15 N); a wedge with a learned mean beats a pinch of the same size (91 % / 97 % against 81 % / 95 %).
- **A correction I made to use.** The shoe's push is a force fixed in the room under a turning tube: its static part is trimmed away and only a part that turns with the table (unequal contacts, slack) reaches the centring. The ordering rule (shoe on before the last pass) is adopted anyway.
- **Something I had not seen.** A three-ball seat's sideways stiffness is not what sets the dot's shift; the rocking term (a force at the flange times its height times the dot's lever over 1.5 contact stiffnesses times the ball circle squared) is ten times larger at the proxy numbers, and a seat at the nozzle end makes it fifty times smaller. That came from asking who docks the gun.

### The new direction, in the framing's terms

Bought arms and multi-axis positioners as an allocation of motion. The tube's rotation makes the whole seam path, so an arm's job is one pose held; that turns the datasheet upside down (repeatability is the closure's figure, stiffness and drift are the weld's and are on no datasheet read). The gun needs four degrees of freedom at the dot (radial, vertical, plan angle, beam tilt), a free roll and a free tangent; a six-axis arm has two to spare, a SCARA or gantry none and no tilt. The per-joint map is a Jacobian, so an AI can compute where each joint's error lands and choose the base position and the grip at commissioning; it decides less than expected (61 to 100 micrometres for 0.01 degree at every joint, base azimuth and grip varied), because the wrist has the gun's length as its lever. A SCARA on the radial line has two joints whose error costs nothing; joint resolution is a floor; a coarse arm with a fine stack under the work splits the two jobs. Ideas: `travel-20` (deep), `travel-21` (lens: the closure as a table), `travel-22` (dock, float, read, re-teach, hold).

### Log of what changed my mind

- **The base on the radial line is not a rule.** I expected a clean win from putting the base joint's error on the free tangent; the sweep shows 0 of 68 for that joint and a total that is not the smallest, because the wrist and elbow solution costs more than the base saves.
- **Float is not neutral.** Letting go from a re-taught hold into float moves the dot 304 micrometres at the proxy numbers, because float brings its own residual force (joint friction, declaration error, umbilical). Float once to read the joints, then hold.
- **A first version of the arm scene put arrows the same colour as the shell and hid them.** Arrows now draw on top in their own colours.
- **A check I ran on my own claim.** "Park up 250, out 150" was not reachable by this arm and base (the continuation solve failed); the scene ships with up 200, out 200 and a badge.

### Kit issues hit in wave 3

- A file-write hook rewrites `\uXXXX` escapes into characters in files written by the Write tool; in JS strings a double backslash (`\\u00b5`) then shows literally. Scenes written with the Write tool must use the characters, or single-backslash escapes only in JS (not in HTML text set through `innerHTML`).
- `app.ui.panel` cards are appended after the controls card, not inside it: a budget table wanted at the top of the controls has to be a stage overlay (both are used in `travel-20`).
- `app.stageOverlay` and the custom stage's legend both sit over content; I keep overlays narrow.
- Puppeteer screenshots of custom-stage scenes are the viewport only: tall tables are cut off in a thumbnail but scroll in a page.

### Sourcing in wave 3

`sourcing/travel.md` entries 24 to 34 (Prime: the Dobot Magician family, Mirobot, SO-ARM101, reBot B601-DM, an XYZ manual stage; ordinary retail: Fairino FR3 at fairino.us, the UR3e datasheet and RTDE page, other makers by search). Prime searches for SCARA, delta and hexapod returned only educational arm kits. My Chrome tab was closed when done.

## Open threads

- **For `use` (their exchange file on my ideas, answered in wave 3):** `exchange/travel--reply-to-use-w3.md`. Their next questions would be about `travel-19` (the seat's preload against the tier's weight shift) and `travel-21` (the states with an arm).
- **Scenes to revise after other explorers answer:** `travel-14-exact-crown` and `travel-16-radial-plane` (datum's answers on clearance and the cable exit); `travel-15-touch-stack` (the nozzle thread and the stylus slide); `travel-20` (a real arm's flange stiffness once anyone measures a support's newtons per millimetre with a spring scale and the indicator).
- **Ideas to develop further:** the ring-carried wire guide; the wire-pair tether; a stylus slide beside the nozzle; the arm as a follow stage (stick-slip at 16 micrometres a second is the open question); `travel-19`'s seat under a real rotator and tube (the weight, the preload); the arm's fibre routing and a J6 limit rule.
- **Still to make:** `travel-01b` (monitor arm carries, stack locates) and `travel-01d` (table plate + stack) are now partly covered by `travel-20` (a SCARA is a monitor arm with motors) and `travel-19`; a scene for `travel-17` (two wedge rings) if it survives.
- **Held with a question:** `travel-12-heads-own-stage` (Derek's two-minute touch-screen test).
- **Questions that need Derek's observation (all repeated with their idea):** how he ends a bead and whether the head lifts at all; the indicator on the tube with the shoe engaged and disengaged; an indicator on the shell while a clamp closes (a push to one side or a pinch); whether the dial can stand opposite the gun; the gun's mass and balance point with the shell; the umbilical's pull before and after the wire feed and gas start; newtons per millimetre of whatever holds the gun (a spring scale and the indicator); the rotator, its base and a tube weighed together; five tubes measured for OD out-of-round, wall thickness, rim flatness, plate seat depth and tube length; whether the touch screen or RS232 can offset the swing centre; whether the nozzle comes off and its thread; how the laser's work circuit closes; the rotator's fastest safe jog.
- **Sourcing gaps:** a Prime listing of an arm that carries a gun (none; the two 3 kg arms found are sold by their makers, no lead time observed); any stated stiffness, lost motion or drift for any arm; a micron-class software-readable probe on Prime; a spring pad of 40 to 50 N/mm; any stated torsion or stretch stiffness for pre-tensioned wire rope; a lift speed or holding force for a linear stage that could be the drop tier.
