# Digest after wave 1

Eight explorers, 109 recorded ideas, 67 scenes. Each idea below carries the explorer's own one-line account and a five-part reading of the arrangement: how motion is assigned, what carries the gun and umbilical, what establishes the dot position, how the result is observed, and how the equipment is used. Statements are agent findings from wave 1; sources and numbers are in each idea file (`explorers/<code>/ideas/<id>.md`).

## The arrangements by how they hold and move the gun

1. **The hand keeps the gun; software watches or coaches.** room-08 · use-06 · use-08 · use-09 · borrowed-03 · borrowed-08 · borrowed-09 · travel-09 · trials-10 · trials-12 · freedom-09
2. **Weight carried from above, position set elsewhere.** freedom-02 · room-02 · borrowed-11 · travel-08 · freedom-08 · borrowed-07
3. **Hung on lines.** freedom-01 · freedom-01b · freedom-01c · freedom-03 · room-06 · room-11
4. **Stages, gantries and enclosures around the work.** room-01 · room-01b · room-03 · room-04 · room-05 · borrowed-02 · freedom-10 · borrowed-10
5. **Rotations that pass through the dot.** borrowed-01 · travel-03 · travel-05 · travel-05b · borrowed-04 · freedom-06
6. **The work moves; the gun stays.** travel-01 · trials-04b · trials-16 · room-09 · room-10 · datum-12 · travel-06
7. **The gun rides on, or is seated by, the work.** datum-03 · datum-03b · datum-08 · datum-04 · travel-11 · freedom-07 · borrowed-07
8. **Docks, kinematic seats, swaps and return.** trials-01 · trials-01b · trials-02 · trials-07 · trials-08 · travel-04 · use-02 · use-03 · use-07
9. **Ways of seeing.** eyes-01 to eyes-12 · datum-05 · datum-06 · datum-10 · borrowed-05 · borrowed-10 · trials-05 · trials-06 · trials-13
10. **Touch and probe.** trials-03 · trials-14 · eyes-05 · eyes-06 · eyes-06b · eyes-12 · datum-04 · datum-07 · use-10
11. **A map learned in a dry turn and replayed by rotator angle.** freedom-05 · trials-04 · eyes-09 · datum-02 · travel-02 · use-04
12. **Lenses: views of a question rather than an arrangement.** freedom-04 · travel-07 · datum-01 · use-01 · use-05 · eyes-11 · room-07 · trials-11 · trials-17 · borrowed-04

Derek's examples appear as freedom-01 (suspension, with 01b, 01c and room-11), freedom-02 (the balanced arm), and room-01 with room-01b (the table opening). Two explorers who began without the examples arrived at neighbours of them independently: borrowed-03 (an encoded balanced arm) and borrowed-11 (balancer plus festoon).

## Findings several explorers reached independently

These are agent findings. Their numbers are illustrative unless the idea file tags a source.

- The corner moves under a stationary gun each revolution (runout and plate seat). Six explorers reached a map of that motion learned in one dry turn and replayed by rotator angle, each with a different sensor and stage: freedom-05, trials-04, eyes-09, datum-02, travel-02, use-04.
- The dot lies against the wall, 6.35 mm below the rim. Every camera stands on the bore side or looks down through the open top; the wall hides the dot from outside. eyes-02, trials-03, room-01, room-05.
- The tangent direction is forgiving and the radial and vertical directions are not: a slide along the tangent costs s²/2r. freedom-04, travel-03, eyes-09.
- A soft support can carry weight without locating; on each axis the stiffest element is the one that locates. freedom-01, freedom-01c, travel-05b.
- Gas-spring monitor arms of the ordinary kind are rated from about 2 kg upward; the gun's mass is unknown and may sit below that range. Spring balancers rated 0.5 to 1.5 kg are sold. freedom-02, borrowed-11, travel-01.
- Three balls in three grooves is the common way to re-create a pose after a swap or a swing-away. trials-02, travel-04, use-02, use-03, room-05.
- The dot and the wire tip can both act as probes: the dot sweeps across the corner and the image breaks at the wall; the wire tip closes a circuit on contact. eyes-06, trials-03, use-10, trials-14.
- Roll about the grip axis is roll about the cable's exit axis; the manual forbids twisting the fibre. freedom-01, room-04, datum-03b.

## Where coverage is thin

- Bought multi-axis positioners that already have a software interface: desktop and collaborative robot arms, delta, SCARA and hexapod platforms, camera motion-control rigs, telescope mounts, microscope and lab stands. Wave 1 reached gimbals, gantries and a hobby CNC.
- The work in another orientation: tube axis horizontal, tilted, or inverted; the gun in another relation to gravity.
- The umbilical and the wire conduit as the design driver: where they leave the gun, how they route, what they weigh and pull, how the wire meets the dot on the arriving side.
- Lift-away and wire break-off at the end of the bead as the design driver.
- The hand supplying motion while software supplies resistance or guidance (a virtual wall, a brake, a detent).
- Shells and seats formed by the work: a gun shell that mates the bore, rim, ports or plate, beyond the rim crown.
- The station around the arrangement: enclosure, lighting, glare on stainless, fume, cameras' own mounting.
- Calibrating the observation itself: hand-eye calibration, camera drift, time synchronisation.

## Questions that need Derek's observation

Collected from the returns; each idea file lists the ones it depends on. Gun mass and centre of mass; umbilical pull and its direction at the exit; whether the red dot coincides with the melt position at working standoff (and how the "red light alignment" setting moves it); tube length and plate seat depth spread; radial and face runout of a few tubes before and after indicating; loop friction on a printed shell; how much of the corner the dot shows on a sawn half-tube; whether the laser's ready lamp responds to nozzle contact.

## Kit 1.1.0 after wave 1

`kit/README.md` lists the additions: `beamSurfacePoint`, `ws.setWorkPose`, `app.ui.panel`, `app.stageOverlay`, `cornerInset.addMarker`, `gun.setLaser(on,{sweepMm,offsetMm})`, `noVisual` controls, a persistent custom legend, and custom-stage `minWidth`. Visibility tests now default to `eps` 0.8 mm, so a dot on the 1.65 mm wall reads as hidden from outside the tube. Scenes whose readings changed: room-01 and room-05 (side camera looking at the nozzle tip reads blocked by the gun), room-04 (the room camera sees the dot for 42 % of the orbit), use-06 (the dot reads blocked by the endcap), datum-05 (a scene-added camera no longer occludes itself: 2 usable tags), freedom-01, freedom-01b and freedom-03 (bend-radius badge now about 380 mm instead of 314 mm after a fix to array input in `curveMinRadius`).

## Every idea, by explorer

One line each. Scenes are `scenes/<id>/index.html`; the full account is `explorers/<code>/ideas/<id>.md`.


### freedom — Freedom and force

- **freedom-01-ring-bungee** (deep) Ring-and-bungee suspension (Derek's original), worked through — Two openable loops (tip, cable pair) hung by wires in Z and bungees in X or Y, an arm gripping the shell; every contact type and grip solved as statics. Eight break-and-repair rounds.
- **freedom-01b-nose-seat** (developed) Seat, not loop: ball collar in a cone at the nose, tail on a bridle — Replace the tip loop with a sphere-in-cone seat 60 to 110 mm from the dot; a spreader bar with two wires and a yaw bungee sets orientation at a long lever, attenuated 3 to 14 times.
- **freedom-01c-master-per-axis** (developed) One master per axis: bungee as compliance, preload plus stop, or series-elastic — A one-axis spring bank: a stiff element is a position source, a soft one a force source; two stiff elements lock in force (200 N/mm wire vs 5 N/mm arm: 4.9 N per mm, arm gain 0.02).
- **freedom-02-balanced-arm** (deep) Monitor arm as the weight path, a vernier stage as the location path — A gas-spring arm carries gun and cable and holds by friction inside a window; an XZ vernier and a camera place the dot. Payload floor, friction window, brake, motor sizing worked.
- **freedom-03-cable-platform** (developed) Six taut lines: the gun shell hung on measured or driven cables — Shell on six lines to an overhead frame; gravity keeps them taut. Encoders only (software observes, hand positions) or winches (software drives). Slack, stretch and layout worked with numbers.
- **freedom-04-free-tangent** (developed) The tangent is free, and the pivot sets the lever — Error budget by motion for a circular seam: tangent slide costs s²/2r, a tilt costs pivot-to-dot × angle, roll about the barrel costs the dot nothing. Turns a tolerance into allowed errors.
- **freedom-05-runout-table** (developed) Runout is a known periodic disturbance: a table, not a stiffness — Fit amplitude, phase and per-tube offset from one noisy dry-run; a ±0.5 mm vernier follows the rotator angle. Needs 0.018 mm/s and 0.0023 mm/s² at 8 mm/s bead travel.
- **freedom-06-lock-and-release** (sketch) Lock and release: an articulated friction arm whose constraints change by state — Photo-style magic arm free while a hand or vernier places the gun, all joints clamped by one actuated lock to weld; joint torque against clamp capacity and hang-from-above shown.
- **freedom-07-floating-on-work** (sketch) Floating gun leaned on the work: a preloaded shoe as a temporary reference — Near-weightless gun with a two-roller shoe on bore wall and rim, preload set by software; follows runout but not plate seat depth; rolling contact keeps the tangent free.
- **freedom-08-gravity-tilt** (sketch) Gravity as the tilt actuator: plumb-bob gun with a trim mass — Hang the gun from a pivot above its COM so gravity sets pitch and roll; a trim mass adjusts by ~1° per 100 g × 7.5 mm. Gravity is weak: 2 N of cable pull leans it about 39°.
- **freedom-09-pose-logger** (sketch) Observe only: a pose logger on a hand-positioned floating gun — Six draw-wire encoders and a camera log pose and dot while a hand positions the gun on a passive support; software moves nothing. First stage of freedom-03.
- **freedom-10-nudge-box** (sketch) Move only, blind: a nudge box, and a spring-driven retract with a latch — Open-loop stepper vernier with a home stop, known increments and a person watching the dot; coda: a preloaded spring lifts the head at end of bead when a latch releases.

### room — The room is the first stage

- **room-01-table-opening** (deep) Table opening, low gantry, shelf under the hole — Rotator on a shelf under a table hole, rim flush; low gantry beside the tube reaches a fitted shell; shelf, X and Y driven, angles fixed by saddle print.
- **room-01b-edge-notch-slot** (developed) Edge, notch and slot neighbours of the opening — Table edge (cantilevered shelf, one-sided bridge), notch (seat tube at a bench, slide rotator in) and slot (carriage that drops as it moves) as neighbours of the hole.
- **room-02-ceiling-carries** (developed) Ceiling carries, table locates — Ceiling balancer and trolley carry a share of gun weight and the umbilical; the gun stands on three ball feet on the table plane; a planar drive moves it sideways.
- **room-03-wall-port** (deep) Wall port: gun on a rod through the enclosure lid — Gun on a rod through a ball in an enclosure lid: plate slide translates, insertion goes along the axis, two long-tail actuators trim tilt with reduction.
- **room-04-orbit-the-gun** (sketch) Orbit the gun around a parked tube — Tube parked; a spindle on its axis turns a boom carrying the gun 380 degrees; a steady ring on the outside diameter centres it; a boom camera keeps a constant view.
- **room-05-drawer-cell** (developed) Drawer cell: rotator comes to a fixed gun — Laser-safe cabinet: rotator rides out on drawer slides for loading and rolls into a kinematic dock under a fixed gun and cameras; a ramp lowers the tube.
- **room-06-corner-cords** (deep) Corner cords with self-calibration — Eight taut lines from cage corners to shell lugs, winches set pose; software calibrates hand-placed anchors by watching the dot, in simulation from millimetres to 0.05-0.25 mm.
- **room-07-grid-table** (sketch) Grid table and the coarse/fine budget view — Dog-hole grid top as shared datum for rotator and gun frame, plus a view of the sideways and vertical fine-stage range each coarse arrangement leaves.
- **room-08-observe-only-frame** (sketch) Observe-only frame — Fixed camera frame over the bench with fiducials on the shell: software watches dot, seam and shell pose and moves nothing while the operator welds by hand.
- **room-09-move-only-shelf** (sketch) Move-only shelf — Only the shelf under the rotator is motorised: software sets rim height from a recipe number while the operator holds the gun as today.
- **room-10-sit-stand-portal** (sketch) Sit-stand desk frame as a lift — Sit-stand desk frame used as an elevator: rotator rises from waist-height loading into a hard-stopped dock; the portal use was rejected for excess travel and leg skew.
- **room-11-pegboard-suspension** (sketch) Pegboard anchor lattice for rings and bungees — Pegboard wall as anchor lattice and ceiling as long Z for Derek's rings and bungees; numbers show 0.007 to 0.2 N/mm lateral stiffness, so it carries and sets up but cannot hold.

### travel — Split the travel

- **travel-01-tube-travels** (deep) The tube travels: gun locked, work moves — Gun stays in a hand-set locked holder; a shuttle plus Z, X, Y under the rotator moves the tube; a tangent shift is plan angle at 1/r.
- **travel-02-cascade** (deep) Cascade: hand, motor trim, follow stage — Three stages each sized by what the one above leaves; a follow stage replays one revolution's runout from a dry-run table at a few steps per second.
- **travel-03-dot-centred** (developed) Dot-centred orientation on arcs — Pitch and plan angle turn about the dot on printed arcs (gun side, or tube tilted under the rotator), so orientation never displaces the dot; beam roll is free on the dot-grip line.
- **travel-04-return-seat** (developed) Return seat: swing away, kinematic landing — Gun rides a hinged carrier that swings up for tube swap and end-of-weld lift-off and lands on a three-ball magnetic seat: adjust rarely, return every time.
- **travel-05-lever-map** (developed) Ratio devices and the lever map — Put the reduction where the motion is made: pivot lever L, actuator lever a, reducing lever, micrometer head or gearbox; a side-view calculator shows dot travel per step and per bit of slop.
- **travel-05b-soft-drive-hard-lock** (sketch) Soft drive, hard lock — Derek's bungees read as a gear: a motor anchor moves a soft spring that reduces motion to the gun; a clamp then locks it so cable pull meets a stiff mount.
- **travel-06-nest-driver** (developed) Nest driver: rotator indexes its own screws — The three M3 tube-centring screws ride the turntable, so the rotator can present each to a stationary powered driver while a probe nulls eccentricity before the weld.
- **travel-07-allocation-matrix** (sketch) Allocation matrix lens — A table of who supplies each relative motion for Derek's three examples and these arrangements, with setup and weld phases; blanks mark motions nobody named.
- **travel-08-cable-travel** (sketch) The cable gets its own travel — Umbilical and conduit ride a constant-force balancer and gallows so the gun-carrying stage sees only the gun; a soft stage belongs where no cable pulls.
- **travel-09-hand-moves-software-reads** (sketch) Hand moves, software reads — Hand-cranked stages with digital scales; software reads every stage position and the dot and tells the person which wheel to turn: software observes and moves nothing.
- **travel-10-software-moves-person-sees** (sketch) Software moves, a person is the eye — Stepper axes with stored per-lot offsets and no measurement: Derek looks at the dot and says how far off; the AI moves and logs: software moves and observes nothing.
- **travel-11-rides-the-tube** (sketch) Rides the tube — A non-rotating collar on the tube's wall and rim carries the gun, so gun-to-work position is set by the work and runout cancels by construction; the room only stops rotation.
- **travel-12-heads-own-stage** (sketch) The head's own fine stage — Use the gun's galvo sweep centre as a zero-mass radial trim if the laser software can offset it; held with a question because red-light offset may move only the pilot.
- **travel-13-print-to-adjust** (sketch) Print to adjust — The AI turns an observed error into a shim or spacer computed from the lever; a printer or brass shim stock and a hand make the adjustment.

### trials — The machine runs trials

- **trials-01-puck-swap** (deep) Puck: nest and tube swap as one lift — Nest and tube form a puck on three kinematic seats; indicating moves to a prep stand; the puck carries a seated check, rotational phase, an index magnet and a tag.
- **trials-01b-nest-as-puck** (sketch) Nest as puck (smallest version) — Keep the existing nest; replace its three M3 screws with three ball-and-dowel seats so a nest with its tube already indicated can be swapped.
- **trials-02-dock-reset** (deep) The dock: the gun's home between trials — Gun-in-shell returns to a kinematic cradle: re-anchors coordinates, clears the swap, weighs gun and umbilical on three cells, gives a one-sided final approach.
- **trials-03-dot-touch-probe** (deep) The red dot as a touch probe — Sweep one axis and watch the dot cross the seam: the plate part vanishes from above (the knee), spot size gives standoff, the plate's reflection acts as a ruler.
- **trials-04-seam-map-replay** (deep) Seam map and angle-keyed replay — Learn the seam's radial and height wobble at each rotator angle in the first turns, replay it on a small follower; only r and z matter.
- **trials-04b-follower-under-tube** (sketch) Follower under the tube — The follower is an X slide plus a small lift under the rotator; the gun hangs from a passive support and needs no actuator.
- **trials-05-artefact-ladder** (developed) The artefact ladder — Five workpieces isolate difficulties with different ground truth: calibration board, corner coupon, notch tube, printed zoo, real tube; two judge cameras; pivot trial on the board.
- **trials-06-mule-gun** (developed) The mule: instrumented stand-in for the gun — A printed dummy in the scanned shell with ballast, switchable dot, IMU, tip switch and dummy umbilical; or an instrumented shell on the real gun. IMU sees two of three rotations.
- **trials-07-toolchange-swap** (sketch) Tool-changing gantry swaps the tubes — One positioner parks the gun, picks a gripper, exchanges pucks with a rack and picks the gun up; a coupling moment check shows magnets alone cannot hold the gun.
- **trials-08-loader-tended-cell** (sketch) Loader-tended cell — Everything motorised except the tube swap; software asks the human for tube N, verifies the seat, batches its work so visits are rare.
- **trials-09-tube-zoo** (sketch) Tube zoo (printed, designed errors) — Printed tubes with plate depth, offset, ovality and tilt put in on purpose: a population with known ground truth, worse than any real tube.
- **trials-10-human-labelled-jog** (sketch) Human-labelled jog — Command only: motors jog the dot, Derek taps good or a nudge direction; the taps train a camera judge that later takes over.
- **trials-11-arrangement-yardstick** (sketch) A yardstick for any way of holding the gun — Observe only: one judge and one script score hand, monitor arm, rings or gantry; the first entry is Derek's hands, giving a measured requirement.
- **trials-12-encoded-manual-axes** (sketch) Encoded manual axes — Hand-driven stages with digital scales; software reads every knob, advises numbers, commands nothing, and learns the arrangement's Jacobian.
- **trials-13-pivot-calibration** (sketch) Pivot calibration of the dot — Tilt the gun about where the software thinks the dot is, with the dot on a board; the dot's wander gives its true offset along the beam.
- **trials-14-contact-sense** (sketch) Contact sense with the gun's circuit — The clip-and-gun circuit or the wire as a touch probe; a camera watching the laser box's ready lamp may act as a free contact sensor.
- **trials-15-one-tube-many-poses** (sketch) One tube, many poses — Swaps are the outer loop: hundreds of trials per loaded tube, blocked by tube with a golden reference; re-seat one tube ten times to measure swap noise.
- **trials-16-tube-moves-gun-hangs** (sketch) The tube moves, the gun hangs — The only actuator is a stage under the rotator; the gun hangs from a passive support and a camera closes the loop.
- **trials-17-trial-card** (sketch) The trial card: what makes trial N comparable to N+1 — A table of nuisance factors marked reset by design, recorded, randomised or uncontrolled, each linked to the idea that handles it.

### datum — The seam is the datum

- **datum-01-datum-chain** (developed) Datum chain: what each reference makes unnecessary — One elevation of the rig with the dimension chain from room to corner; choose the reference and see which links drop out and which spreads remain.
- **datum-02-seam-signature** (deep) Seam signature: learn it by turning, replay it while welding — Turn the tube once dry, log dot-versus-seam by table angle, fit a small seam model per tube, replay it into a tiny fine stage while welding.
- **datum-03-rim-crown** (deep) Rim crown: the gun rides on the tube, not on the room — A ring on the rim carries a non-rotating boom and the gun, so the gun follows this tube's wobble; counterweight, soft tether, plunger-fed height stage.
- **datum-03b-orbiting-crown** (developed) Orbiting crown: the tube holds still and the gun goes around it — Same crown with roles swapped: tube held on a plain stand, upper ring and gun driven round a ring gear; the umbilical must follow 380 degrees.
- **datum-04-corner-follower** (developed) Corner follower: feel the seam, and the tacks announce themselves — A small ball feeler rides in the corner ahead of the dot; curvature is subtracted, two leads give offset and yaw, and tacks show as bumps.
- **datum-05-fiducial-collar** (developed) Fiducial collar: the work wears its own coordinate system — Tags on a ring on the tube, camera on the gun shell: the tube's pose in the gun's frame, corner inferred; software observes and moves nothing.
- **datum-06-eddy-through-wall** (sketch) Eddy sensing through the wall: seat depth from outside — A coil sliding up the outside of the tube sees the rim step and the plate bump through the 1.65 mm wall: seat depth with no line of sight.
- **datum-07-touch-off** (sketch) Touch-off: the stylus is already at the dot — In a dry run a stylus, the wire tip or the nozzle is driven into the wall then the plate; a one-bit contact finds this tube's corner by touch.
- **datum-08-port-pin-mast** (sketch) Port-pin mast: the plate carries the gun — Two pins in the plate's ports carry a mast and hub: the datum is the plate's centre, clock and face rather than the rim.
- **datum-09-preplaced-filler-ring** (sketch) Preplaced filler ring: the corner carries its own filler — A split ring of filler wire lies in the corner: a visible self-seating line to track, and no wire-approach constraint on the gun.
- **datum-10-clear-twin** (sketch) Clear twin: a see-through corner for ground truth — A clear replica of the corner, seen by cameras outside and above, gives ground truth for the cheaper estimators before use on steel.
- **datum-11-laser-writes-datum** (sketch) Witness pass and marks the laser writes — Short low-energy pulses on a scrap L-coupon measure where the beam lands against the red dot; index ticks on the rim give an angle scale.
- **datum-12-work-side-tilt** (sketch) Work-side tilt: a wedge does one of the three rotations — Do the hole-axis rotation on the work with a fixed wedge under the rotator, so the gun needs one fewer rotation; the ridge runs from axis to station.
- **datum-13-head-swing-centre** (sketch) Head swing-centre: the laser unit's own fine axis — The head's red-light alignment, if commandable at run time, is a lateral beam-centre offset: a free fine axis across the seam with no mechanism.

### eyes — Seeing first

- **eyes-01-gun-borne-eye** (deep) Gun-borne eye — A camera and a green line laser ride on the printed shell and measure the corner against the dot in the gun's own frame; a loose support plus a small two-axis trim stage removes the leftover.
- **eyes-02-where-can-an-eye-stand** (developed) Where can an eye stand? (viewpoint dome) — A dome of camera positions around the dot is tested against wall, rim, gun and wire, coloured by blocker or by how well the view tells radial from vertical error; fixed-eye presets are dropped on it.
- **eyes-02b-sensor-crown** (sketch) Sensor crown (branch) — A ring of six fixed cameras on posts round the rim looks inward at the station; the gun passes through a gap. In the drawn geometry only three see the dot.
- **eyes-03-marker-cube** (developed) Marker cube — A cube of fiducial tags on the shell is seen by two fixed cameras; software solves gun pose in the tube frame without seeing the dot. The trade is lever arm, not line of sight.
- **eyes-04-proximity-skin** (developed) Proximity skin — Capacitive pads or eddy-current coils around the nozzle read distance to the plate and wall; four numbers solve the dot's radial and vertical offset with no light at all. Blind to the dot itself.
- **eyes-05-touch-off-interlock** (sketch) Touch-off through the interlock — A stylus or the nozzle touches the rim and plate before the bead; the laser's own work-contact circuit, or a 3 V loop, acts as the touch sensor to register the tube by contact.
- **eyes-06-dot-as-probe** (developed) The dot as the probe (sweep to find the corner) — A small axis sweeps the red dot across the seam; in the camera its path changes speed or direction at the corner, so the corner is found in actuator units without calibrating the camera.
- **eyes-06b-corner-mirror** (sketch) The corner is a mirror (branch) — The plate bounces the dot onto the wall; the two spots merge exactly when the dot is on the corner, and their separation magnifies a small radial offset (19x from a low camera).
- **eyes-07-sectioned-tube** (developed) Sectioned calibration tube — A tube and plate sawn in half through the station plane let a tangent camera see the true L-section of the corner and the dot; ground truth to calibrate and label every inferred sensor.
- **eyes-09-scan-then-weld** (developed) Scan first, weld second (seam map and look-ahead) — Because the seam moves under 0.02 mm/s, observe it in a dry turn where nothing hides it, play a slow correction during the bead, or watch it from 35 degrees upstream.
- **eyes-10-under-the-workpiece** (sketch) Under the workpiece — For the first closure only, the open tube bottom and the rotator's service bore are a window: a camera below sees light through the slip gap or the heated plate underside. The gap view fails on a number.
- **eyes-11-what-each-eye-sees** (developed) What each eye sees (and blind but listening) — Nine sensors mapped against the gun's six coordinates as direct, inferred, partial or blind; includes an IMU-and-microphone arrangement that observes tilt and process events and moves nothing.
- **eyes-11b-umbilical-eyes** (sketch) Umbilical's own eyes (branch) — A painted stripe and beads every 200 mm on the fibre umbilical, seen by a fixed camera, give twist and bend radius against the manual's 350 mm emitting and no-twist rules.
- **eyes-12-dot-lattice** (sketch) The dot lattice (software moves, video observes) — Software steps a positioner through a scripted grid of offsets over the corner while a phone records; a person or model labels frames afterwards. Or software observes and a person turns the knob.

### borrowed — Borrowed from elsewhere

- **borrowed-01-ring-pivots** (deep) Ring pivots: turn about the dot with nothing on the axis — Telescope-style bearing rings around empty axes through the dot give yaw, hole and roll while the dot stays on the seam; a bench post and trim stage carry the frame.
- **borrowed-02-gimbal-on-gantry** (deep) Gimbal on a gantry: orientation from one product, position from another — A balanced stabiliser gimbal turns the gun about a point C on the roll line; a printer-style gantry moves C so the dot stays put (dot = C - t*g).
- **borrowed-03-encoded-arm** (deep) Encoded balanced arm: the operator moves, software watches and coaches — A spring-balanced monitor or lamp arm with an encoder on each joint carries the gun; the operator moves it and software reads the pose and coaches, moving nothing.
- **borrowed-04-axis-map** (developed) Axis map: where a pivot can physically be — An analysis page: for any axis through the dot, whether a shaft, a two-sided shaft or a ring bearing fits without touching tube, plate or bench.
- **borrowed-05-guide-star** (developed) Guide star: calibrate the trim axes by nudging and watching the dot — Astrophotography autoguiding as bring-up: nudge each trim axis, watch the dot, solve the pixel-to-axis matrix and backlash, then guide; a simulation of the method.
- **borrowed-06-swing-offset** (developed) Swing offset: the gun already has a fine axis across the seam — The gun's own swing motor and red-light shift could steer the spot across the seam; the scene shows what an offset does and what a nulling loop needs; command and range are unknown.
- **borrowed-07-tonearm** (sketch) Tonearm follower: the tube's own rim sets the height — A counterbalanced arm carries the gun with a ball foot on the tube rim, so the rotating rim sets the dot's height without a sensor; radial and plate-depth errors remain.
- **borrowed-08-manual-stack-spotter** (sketch) Manual stack with a spotter: hands turn the knobs, software says which — Cross-slide, lab jack and geared head with digital scales carry the gun; software computes coupled knob readings and reads a camera; a person turns every knob.
- **borrowed-09-hand-controller** (sketch) Hand controller: small leader arm or 6-DoF puck — A small printed leader arm with servo encoders (SO-101 pattern) or a 6-DoF puck is the hand controller for a larger follower; demonstrations are recorded for an AI.
- **borrowed-10-gun-free-dot** (sketch) Gun-free dot: pan/tilt laser pointer stands in for the gun — A pan/tilt servo laser pointer stands in for the gun's dot so the camera and calibration chain can run dry, all night, with no gun, interlock or laser emission.
- **borrowed-11-balancer-festoon** (sketch) Balancer plus festoon: carry the weight from above, guide the cable — A spring tool balancer carries the gun's weight from above and the umbilical rides in a festoon track or cable chain with a guaranteed bend radius and no twist.
- **borrowed-12-other-trades** (sketch) Other trades: take the axis, not the product — A shelf of high-volume motion products from other trades: stage-light yoke, window regulator, wiper motor, desk column, welding positioner, roller rotary. Take the axis, not the product.

### use — The day of use

- **use-02-swing-head** (deep) Swing head: the arm brings, the seat locates — A swing arm and a short plunge along the barrel axis bring the gun beside a three-ball seat and seat it; software commands states, the seat sets position, a float hands over the load.
- **use-03-preset-cartridge** (deep) Preset cartridge: the tube brings its correction — Nest and tube travel as a cartridge, height-set and indicated at a presetter while the last tube is on the rotator; software advises screws and ring; the gun is never re-aimed.
- **use-06-coach-loop** (developed) Coach loop: software watches, a hand moves — Gun on a locking friction arm with a two-knob fine stage carrying digital scales; a camera reads dot versus seam and the screen tells the hand which knob and how far.
- **use-01-day-lanes** (developed) The day, lane by lane — A lens: ten states of one closure as lanes for hand doing, hand holding, eye judging or watching, software, pose owner and laser, for six arrangements, with handovers and a to-scale time bar.
- **use-04-the-lap** (developed) The lap: what changes, how fast — A lens plus lap-replay idea: dial and trace of one lap, runout slews at hundredths of a millimetre per second, four correctors, and every disturbance and corrector on one time axis.
- **use-05-gates** (sketch) Gates: what software may do alone — The closure as a state machine with owners: a hand fires the laser always, software may move, watch and veto; attended versus unattended is a three-way policy; faults are hold states.
- **use-07-two-stations** (sketch) Two stations, one head — Two rotators and one head translating on a rail; a plan view checks the fibre's bend radius with fixed, half-speed or head-riding cable hooks; a schedule shows what actually overlaps.
- **use-10-wire-first** (sketch) Wire first: the consumable as the probe — A wire-inclusive dry run: the feeder jog puts the tip on the plate with the laser off, so where the wire lands against the dot and which side of the puddle it is on become observable.
- **use-11-setup-gauge** (sketch) Setup gauge: aim at a corner you can see — A printed gauge tube with a wall window and a printed target line sits in the nest; the gun is set where the dot can be seen, then the real tube is swapped in on the same register.
- **use-08-flight-recorder** (sketch) Flight recorder: every hand-held weld is an experiment record — Weld as today, but a camera, the rotator's degrees and a trigger-time sense log each weld and join it to PT and hydro results; software observes and moves nothing.
- **use-09-programmed-table** (sketch) Programmed table: the tube follows a program, the hand holds the gun — The rotator runs index, lap and bead programs under the pedal deadman while a hand holds the gun on a rest; software moves the tube and observes only degrees.
- **use-12-golden-tube** (sketch) Golden tube: a reference tube runs the cycle every morning — A kept reference tube runs the full dry cycle first each day; its trace and readings are compared with a stored baseline so drift is seen before a real tube is committed.
