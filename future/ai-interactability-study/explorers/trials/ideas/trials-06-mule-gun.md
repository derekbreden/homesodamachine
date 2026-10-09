# trials-06-mule-gun: a stand-in for the gun that can run all night

Scene: `scenes/trials-06-mule-gun/index.html` (developed). Sourcing: laser module and IMU in `sourcing/trials.md`.

## Picture it

A printed dummy sits in the scanned shell where the X1 Pro would: same outside, ballast to the real weight, a small red laser module at the real dot position, an IMU, a switch in the nozzle tip, a dummy umbilical. It can be switched on and off by software, run for hours with no laser and no gas and no wire, crash into the rim, and blink its dot so a camera can find it against the glare. When the AI has learned what it can, the real gun comes out for confirming runs.

## The proposal

Scanning a gun and printing a shell that fits it are established **[Derek]**. Print a body for the same shell. Fill it with: ballast (amber blocks) to the real mass and balance; a 650 nm module at the real dot position (from a board pivot trial, trials-05); an IMU on the housing; a switch in the nozzle tip (a contact probe the real copper nozzle is not used as); a vibration motor to mimic the head (the real head has one **[manual p.20]**); a solenoid to mimic the trigger; a dummy umbilical and conduit. Three branches in the scene: the real gun in the plain shell; **the real gun in an instrumented shell** (IMU and a camera on the shell, nothing inside the gun); and the mule.

What the mule gives that the real gun does not: unattended runs, crash tolerance, a switchable dot, an IMU and a contact probe without touching the real hardware. What it does not have: the real weight distribution (until matched), the real umbilical drag, the real dot's size and its relation to the melt. So it develops and rehearses; the real gun confirms.

## What carries the loads, what establishes position, what stays free

The shell carries the mule (ballast makes it the real weight); whatever carries the gun attaches to the shell's lugs. Position is established by the shell's scanned outline and the module placed at the dot. Free: nothing of its own except the optional vibration and trigger mimics.

## What software could command, observe, and what stays manual

- Command: dot on/off/blink; vibration; trigger solenoid.
- Observe: **IMU pitch and roll from gravity** (pitch = barrel angle from vertical, roll = turn about the barrel); nozzle tip contact; dot position by cameras; weight on the dock scale.
- **The IMU cannot see the turn about the vertical axis.** The scene shows it: changing the vertical-axis dial leaves pitch and roll unchanged (44.6° and −60.7° at the opening pose, before and after a 55° yaw change). That turn is the tangent alignment the wire approach needs. A magnetometer gives yaw in principle, but the gun has a motor and a steel bench is near; the judge cameras see the wire's approach instead.
- Manual: scanning, printing, matching mass and balance, placing the module.

## Tried to break it

1. **The mule's dot is not the real dot.** The real gun's red light has its own adjustment **[manual p.25, 39]**. Repair: place the module from a board pivot trial and re-check when the real gun is re-aligned. Leaves: dot size, brightness and the relation to the melt are a real-gun question.
2. **The umbilical drag is not the real drag.** The fibre is 5 m, has a 240 to 350 mm minimum bend radius and must not be twisted **[manual p.20]**; a dummy cable will not have its stiffness. Repair: measure the real pull per pose with the dock weigh-in (trials-02) and shape the dummy to match. Leaves: real stiffness **[unknown]**.
3. **Mass and balance are unknown.** Gun mass and centre of gravity **[unknown]**. Repair: weigh it and hang it from two points. Leaves: nothing until someone does.
4. **Class of the module.** A 5 mW module is class 3R, brighter than the real 0.3 mW dot **[manual p.12]**. Repair: a dimmer module or a resistor. Leaves: the eye-safety of an unattended red laser near a real one is Derek's call.
5. **Unattended near a real laser.** Leaves: interlocks and guarding; out of scope for the study.

## Branches and combinations

- Branch inside the scene: the instrumented shell on the real gun (no mule).
- Combines with `trials-02` (dock weigh-in gives the umbilical pull), `trials-05` (dot position), `trials-03` (a blinkable dot allows frame subtraction), `trials-07` (an unattended cell wants the mule).
- Transferable: IMU sees two of the three rotations; switchable dot for lock-in detection; instrumented shell.

- **Wave 2, a mule whose dot moves:** `trials-18-steerable-mule` puts a steerable pointer (borrowed's `borrowed-10-gun-free-dot`) or a nose mirror in the mule's nose, so the AI can put the dot at labelled offsets from the seam with nothing else moving; its third steering type is the gun's own swing offset (`borrowed-06`). Turns the mule from a stand-in into an instrument for calibrating the judge.
- **Wave 2, borrowed from `datum-04-corner-follower`:** the nozzle-tip switch could be a small ball feeler in the corner instead: a continuous reading of the corner's r and z at a lead ahead of the dot, and the tacks show as bumps. On the mule it gives an independent touch truth on the *real* 316L tube in dry runs, which the notch tube gives only on a modified one. Datum-04's wire-corridor numbers (a 6 mm lead has 0.08 mm to spare at a 30 degree wire) decide where the ball can be.
- **Wave 3, from datum's exchange (wave 2, section 4: "the mule could carry a wire stub with its own contact sense"):** answered and kept as an option, not drawn. A 0.76 mm wire stub with its own contact sense in the mule's shell lets the dot-to-wire vector (`datum-20-dot-and-wire`) be found first on a stand-in that can run all night; the vector is re-measured at every start because each weld ends with the wire cut or retracted [repo], and one millimetre of stick-out is about 0.6 mm of tip height. What decides it: whether the feeder can be driven by software at all (**[unknown]**) and the mule's nose room (the same scan question as `trials-18`). With the steerable pointer of `trials-18` in the same nose, the dot sweeps the corner and the stub touches it in one run.
- **Wave 2:** a power dip with the real gun on a gimbal kinks the fibre (borrowed-02 scene, motor power off: 73 mm bend radius against 240 mm); the mule has no fibre to kink, which is one more reason the first hundred unattended hours belong to the mule.

## Unresolved, and questions for Derek

- Q: What does the X1 Pro weigh, and where is its centre of gravity?
- Q: Are you comfortable with an unattended low-power red laser stand-in running near the bench?
- Whether the laser box accepts a command to blink its own red dot (RS232 protocol not in the manual pages) **[unknown]**.

## Assumptions

Gun proxy and shell are the kit's **[illustrative]**; envelope 253 x 143 x 34 mm **[manual p.17]**; internal parts are symbols, not from a scan; IMU readouts are exact from the drawn pose, with no noise or drift.
