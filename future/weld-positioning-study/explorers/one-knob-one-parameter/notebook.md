# Notebook: one knob, one parameter

The station is an apparatus for controlled experiments. Every weld-relevant
quantity should be something you can set, read, lock, record and return to
on its own, so that "change one thing" physically changes one thing.

## Files

- `ideas/isocentric-couch-and-gantry.md` — main arrangement, developed furthest.
- `ideas/c-arm-on-the-gun.md` — the literal version: the scene's three dials as three nested physical axes on the gun side; the work only translates.
- `ideas/recipe-cartridges.md` — gun angles frozen in printed pose blocks on kinematic seats; the dot place stays as knobs.
- `ideas/flexure-trim-head.md` — (wave 4) printed flexure fine stages (across-the-corner, work-angle remote-centre pivot at the dot, standoff) on a coarse seated carrier; primary host who-moves-what's tilt cradle (T-b1).
- `ideas/knob-wired-suspension.md` — (wave 3) Derek's suspension as a one-wire-per-angle machine: three wires meet at the dot; each angle wire lies in the plane of the other two axes.
- Wave 4/5 calcs and sketches: `flexures.py`, `tilt_exchange_calcs.py`, `sketch_flexure.py`, `sketch_cartridge.py`; `sketches/flexure-trim-head.svg`, `sketches/recipe-cartridge-pose.svg`.
- Wave 2/3 calcs: `exchange_calcs.py`, `diagonal_wires.py` (+ `.out.txt`, `_layout.json`), `diagonal_wires_checks.py`; sketches `a1g-isocentric-rider.svg`, `c-g2-vertical-angle.svg`, `knob-wired-suspension.svg`.
- `sketches/` — `chain-principle.svg`, `isocentric-side.svg`, `isocentric-plan.svg`, `c-arm-side.svg`, `recipe-cartridge.svg`. The first four side/plan views are drawn from the scene's pose math (`sketch_isocentric.py`, `sketch_carm.py`).
- `geometry.py` — port of `pose.js`: proxy positions, envelopes, collision gaps, and the table of weld angles against knobs.
- `stiffness.py` — how much arm sag reaches the dot as the hole angle changes.

## Principles that came out of wave 1

1. **Isocentre.** Every rotation axis passes through one fixed point, and the
   beam is calibrated through it. Angle knobs then cannot move the dot. That
   is what makes a knob a single parameter, and it needs no care from the
   operator.
2. **Translations nearer ground than rotations.** A translation between a
   rotation and the gun (for example, an XY trim on the shell) knocks the beam
   off the rotation centre. Every later angle change then moves the dot by
   about d·θ: a 0.5 mm trim and 10° give 0.09 mm. Translations must carry the
   rotations. On the gun side that means carrying everything, so they belong
   on the work side, where they carry only the rotator.
3. **Gravity decides which side a knob lives on.** A rotation about the vertical
   and all translations leave the puddle's relation to gravity alone, so they
   can move the work (the "couch"). Tilting rotations must move the gun: tilting
   the tube instead would change a second thing, the direction of gravity at
   the puddle.
4. **Three kinds of adjustment, kept physically different.**
   - *Knobs* are parameters: graduated, approached from one side, locked,
     recorded.
   - *Calibration screws* make the axes meet the dot. They are set during a QA
     run, then painted over.
   - *Motions to a stop* get something out of the way (standoff retract, drawer,
     wire-guide flip, camera flip) and return to a stop the knob set.
5. **The knob is the actuator; the measurement at the dot is the parameter.**
   A camera on the rotator's stationary base looks across the bore at the
   corner, so it reads the dot's place in the joint's own coordinates. Tube-to-tube
   variation (bore, recess, seating, runout) makes micrometer numbers
   non-transferable; camera offsets transfer.
6. **During a weld the gun is static and the work turns.** The gun side
   carries static loads, except the wire's push into the puddle, the wobble
   motor's vibration, and heat. So precision is static stability for ~50 s plus
   repeatability of setting. A red-dot dry run reproduces the weld's load state
   almost exactly, which makes dry-run measurements meaningful.
7. **Keep gravity loads one-signed** so worm and screw backlash is always taken
   up the same way.
   - Hole table, Z, standoff: one sign throughout.
   - Roll: one sign above ~10°; near 0 it flips and needs a preload spring.
8. **A mechanism natively decouples one parameterization.** Derek's grip axis
   keeps the cable exit still, but in weld terms each of his knobs moves three
   angles. At the opening pose, a pure +1° of work angle is roll −1.12°,
   hole +0.26°, vertical +0.56°. The isocentre makes such combinations safe,
   because the dot does not move, but not single.
   - The alternative is a "collimator ring" around the barrel: roll about the
     beam itself. It decouples wobble orientation from beam direction, but the
     cable exit swings on a ~118 mm radius.
   - The choice between the two is Derek's.
9. **Coupling is measured, not assumed.** The radiotherapy "isocentre walk"
   test transfers directly:
   - Set up a printed corner phantom in the nest, with the red dot on and the
     camera watching.
   - Sweep each rotary knob through its range. The trace is that knob's
     coupling in mm.
   - It becomes the station's QA number for the session.
10. **Where the wire guide is mounted decides which relations a knob holds
    constant** (table in the isocentric idea). The standoff slide must not
    carry the wire, or focus changes move the wire tip.
11. **Standoff and nozzle extension are two parameters.** The standoff slide
    moves the whole gun along the beam, which moves focus relative to the joint.
    The graduated tube moves the nozzle relative to the optics, which changes
    clearance at fixed focus. They need separate knobs, and the shell must grip
    a barrel section that the graduated tube does not move.
12. **Nothing the operator does may push the gun.** The trigger is pressed by a
    lever on the shell, pulled by a Bowden cable whose housing also stops on
    the shell, so the force reacts inside the shell.
13. **Kinematic interfaces wherever things come apart:** the shell to the station,
    the camera, cartridges. The gun can go to hand work and come back to the same
    pose.

## Wave 1 log

- Read shared-context, working-method, `weld-position.md`, `pose.js`,
  `main.js` (proxy geometry, dial offset 35°, slider ranges),
  `weld-rotation-rig.md`, the rotator README and `weld_rotator.py` constants.
  Also read the manual pages: drawing, specs, interlock 3.6.2, wire pullback and
  ramp settings, red-light alignment, cable rules.
- Ported `pose.js` to Python. Confirmed that the hole dial equals the grip
  axis's elevation (35.0° at zero rotation). At the opening pose the nozzle tip
  is ~5 mm above the rim and ~7 mm inboard of the bore, and the grip base is
  279 mm out at 30° elevation, ~140 mm above the rim, outside the tube in plan.
  At hole 20° the proxy barrel comes within ~5 mm of the bore wall.
- Found the isocentric framing. Then worked out:
  - why translations must sit nearer ground than rotations;
  - which knobs can go under the work (vertical rotation and translations are
    gravity-neutral);
  - which side the dot sits on in the rotator frame: its free +Y side, so the
    motor stays clear of the gantry;
  - how far the couch can turn before the tube reaches the hole table: ±50°;
  - where the Z column must stand: outside a ~260 mm sweep.
- Arm sag estimate: the gun folds back along the spoke, so the nozzle sits
  near the spoke root. Arm sag then contributes ≤ 0.005 mm of walk for 4040
  or a printed 60 × 60 box. The unknowns are in the joints: table tilt,
  bearings, the shell-to-gun contact.
- Broke the roll bearing on the captive umbilical. A closed ring cannot be
  threaded over it. Repairs: a bore large enough for the gun to pass nose-first
  (6816, 80 mm; needs the scan), or an open roll track, or cartridges (no ring
  at all).
- Found the interlock issue. Moving the wire guide off the gun's bracket
  and holding the gun in plastic may break whatever contact path the laser
  senses (manual 3.6.2).
- Sourcing: 4-inch rotary tables are Prime, $99–$160, with 2–3 day delivery
  and many sellers. They are the key "buy the precision" part: worm, dial,
  lock and a stiff bearing for the price of a few printed-part filament
  spools. Also observed on Prime: micrometer heads $16, MGN12 $18, 6816 $15,
  32011 $17, AS5600 3-pack $8, Klein angle gauge (5K+/month), G25 balls, dowel
  pins, a module-1 worm, an LD40 XYZ stage, and spring balancers. SendCutSend
  claims delivery in days for 6061 up to 0.75 in. No part needs a quote.

## Open questions

- Locked tilt stiffness and lock-induced shift of a 4-inch rotary table under
  an eccentric couch load or a 300 mm spoke. Walk test on a bought table.
- Does an upside-down rotary table tolerate hanging loads (C-arm)?
- Collision envelope at the extremes of roll and hole, and nozzle against wire
  guide. Needs the scan.
- The process window. It decides whether residual couplings of a few
  hundredths of a millimetre matter at all.
- Whether cartridges' print error and creep are small enough to count as
  frozen.

## Questions that need Derek's observation

1. Gun mass and balance point, with the shell.
2. Which contact the conductance interlock senses: nozzle, wire, or body.
3. Trigger force and travel. What the process switch does.
4. Which barrel sections stay fixed when the graduated tube is turned.
5. Does the red dot sweep when wobble is on in red-light mode? If yes, the
   camera reads the wall/cap split directly. If not, a burn card fixes the
   wobble direction once.
6. Umbilical diameter and stiffness near the grip. Is the QBH ever unplugged at
   the gun?
7. Would you give up the free workpiece view (couch rotates the rotator) or the
   free head space (C-arm hangs overhead)? This is the main difference between
   the two knob stations.

## Wave 2 (exchange with borrowed-ecosystems)

Wrote `../../exchange/one-knob-one-parameter--on--borrowed-ecosystems.md`
(calcs `exchange_calcs.py`; sketches `a1g-isocentric-rider.svg`,
`c-g2-vertical-angle.svg`).

- **Dial convention.** Five explorers' geometry passes the hole value 30
  straight in as the rotation. That is scene dial 65: gun near upright, grip
  base 253 mm above the dot, umbilical apex ~680 mm. The scene's pose (Derek's
  defaults, commit `eda643038`) is dial 30 = rotation −5°: barrel 45°, grip base
  140 mm up and 234 mm back, apex ~416 mm. Hole-axis gravity torque is ~3.7×
  larger at the real pose. My `geometry.py` uses the dial correctly.
- **Correction to my own couch.** The tangent (Y) drawer is not a "don't care"
  axis. A tangent offset is the vertical angle, 0.93° per mm, so the drawer now
  returns to a kinematic stop (updated in the idea file). Same fix for anyone's
  Y: curved slides concentric with the tube, or G2 arcs, make Y an exact
  vertical-angle knob.
- **Revision of my wave-1 framing of Derek's axes.** They mix weld angles, but
  his grip roll moves a gun-mounted wire guide only 1.8 mm per 5°. A rotation
  about the tangent, hole or vertical axis through the dot moves it 6.5–8.7 mm.
  His roll is the wall/cap knob that leaves the wire nearly alone.
- **New principle: carry and locate separately.** From A1/A2: if weight is
  carried by a hook at the CG, the locating chain carries newtons, and
  printed arcs and optics stages become adequate knobs. A dot-near arc
  (R 70) turns joint compliance into a quarter of the dot motion of a 300 mm
  arc. This should come back into my isocentric station: hang the gun's
  weight from a balancer at its CG so the hole table and roll bearing only
  locate.
- **The wire belongs on the translation carriage.** Then translations move beam
  and wire together, while rotations move the gun only.

### Derek's examples, through this view (to develop at least one in wave 3)

- **Monitor arm.** A carrier with no knobs: zero rate, every joint free, and
  no joint at the dot. It is useful here as the weight path and the park
  motion for a knob chain that locates: an arm + CG hook + isocentric seat.
  Locking its joints does not give one-parameter changes. Their pivots are
  elsewhere.
- **Table opening, rotator beneath.** It fits the chain rule unusually well.
  - The shelf on four rods is a work-side Z translation, sitting nearer ground
    than everything on the gun.
  - The table top is a natural common "fixed" for both the shelf and the gantry.
  - His gantry's Y is the tangent, so it is the vertical angle: a curved rail
    or G2 would make it exact. That also answers his own "the gun is not
    tangent as it needs to be". A Y position *is* a non-tangent approach.
  - Rotations on the gantry carriage must pivot on the dot, or be cassettes.
- **Suspension.** Carry-and-locate's six-wire layout is an isocentre made of
  tension: three wire lines meeting at the dot form a virtual ball joint there.
  The wave-3 question for my view: can the remaining three wires (or
  bungees) be arranged so that each one's length is *one* of the angles? That
  needs a diagonal Jacobian at the dot, with each wire's moment axis on one
  rotation axis and the others insensitive to it. Then the suspension is a
  one-knob machine whose knobs are turnbuckles. This is the leading candidate
  for serious development.
- **Automated vision.** Five motors: XY, Z, two rolls, plus PTZ cameras. They
  map onto X radial, Y tangent (= vertical angle), Z, and two rolls about the
  dot. If each motor is one parameter (rolls isocentric, Y curved or G2), the
  AI's dry-run search is separable and needs no inverse kinematics. The walk
  test is its first experiment; the dot camera is its PTZ camera.

## Wave 3

### Objections worked (borrowed-ecosystems on my ideas)

- **Y drawer = unseen yaw.** Agreed. It now has a kinematic return, and a new
  branch B-Y makes Y the yaw knob (±3° to 0.085 mm; larger angles by a printed X
  cam or a 61.85 mm parallelogram couch), so the couch rotary table becomes
  optional. I now prefer B-Y as the default.
- **Roll bearing cannot pass the gun.** Agreed and checked: the proxy reaches
  130 mm from the grip axis. Adopted their hinged clamshell rings on a printed
  sleeve, with a gravity-loaded micrometer lever as the roll knob (R-C). The new
  unknown is the sleeve's creep under ring pressure.
- **Sine arm on gauge blocks** for the hole angle, added as R3: a knob plus its
  reference standard. The stack is the record and the return to baseline; a
  sweeping actuator does the exploring.
- **C-arm yaw joint redundant.** Agreed, branch C-0. The C-arm and the couch
  station have converged. The remaining fork is arc versus table on the hole
  axis: the arc supports the gun close in.
- **Cartridges: steel sets the angle.** Branch S. Its hinge must pivot on the
  dot, which is the same isocentre condition.
- **Their §5 rider-as-X-stop.** Added as R4, with a caveat: the wheel reads the
  OD, so wall-thickness variation enters.
- **Balancer vs one-signed gravity.** Their objection holds, so my wave-2
  "float the gun at its CG" is revised to "relieve down to a few N, or hang the
  umbilical only".

### Derek's suspension, developed: `ideas/knob-wired-suspension.md`

- **The rule.** With three wires through the dot held fixed, a rotation wire
  changes only its own rotation iff it lies in the plane of the other two
  rotation axes. That maps onto his example:
  - base loop on a vertical wire = hole knob;
  - the base loop's pull along the hole-axis direction = vertical knob;
  - third ring in the radial vertical plane through the dot = roll knob;
  - the tip's lines aimed at the dot = the pivot.
  - His "complete, openable loop" around a round collar is what makes the base
    loop pass force through the grip axis while the gun rolls inside it.
- **A fully diagonal six-wire layout is impossible here.** The pure
  vertical-angle wire would have to run through the tube wall. So the dot's
  place moves at the work (couch X/Z), and the dot wires stay as calibration.
- **Numbers** (proxy, 1.5 kg assumed):
  - The angle knobs are exactly single to first order.
  - In 2° steps the dot drifts < 0.08 mm and the other angles move ≤ 0.04°; at
    5°, ≤ 0.5 mm and ≤ 0.26°.
  - Stiffness: 21–34 µm per 5 N.
  - Modes at 31/50/116/191/213/252 Hz. At 80 Hz wobble, ~4 µm per N; a
    wobble-frequency sweep through ~116 Hz meets a mode, so the wobble-frequency
    setting can couple into dot vibration.
  - Tension margin is thin: 5.9 N, with 4 of 40,000 layouts feasible.
  - Planes need only mm care (2 mm out of plane → ≤ 2.7% leak).
- **Biggest open problem:** thin tension margins that depend on the real gun
  mass, CG and cable pull, and first-order-only exactness. It needs a measured
  gun and one prototype with the walk test.

### Convergence noted

- **Isocentres.** Couch station, C-arm, borrowed-ecosystems' B and the wire
  suspension are one kinematic idea in four materials: tables, arcs, panorama
  parts, wires.
- **Translations at the work.** Six explorers now put translations at the
  work.
- **The walk test** is the shared QA for all of them.

## Wave 4

### Exchange with who-moves-what on the tilt cradle + escape rail

Wrote `../../exchange/one-knob-one-parameter--on--who-moves-what-w4.md`
(calcs `tilt_exchange_calcs.py`).

- **Difficulty 1: the rail stop is two knobs.** At τ* the beam is 32.4° off the
  vertical rail, so 1 mm on the stop is +1.18 mm of standoff and a 0.64 mm slide
  along the seam: 0.59° of yaw the camera cannot see. Nothing moves the dot
  across the corner.
  *Branch T-b1:* the stop becomes a fixed seat, and two stages on the carriage
  run along the beam (S) and horizontal-radial (A, perpendicular to beam and
  seam).
  *Branch T-g:* a work-angle pivot on the cradle's own axis. The pivot α is work
  angle at fixed gravity, the cradle τ is gravity at fixed work angle, and
  α = −τ is their T-c.
- **Difficulty 2: τ reaches the pose.** The first-closure tube (plate on top,
  CoM 108 mm) tips about its rim at τ ≈ 30.5°, before τ* and before the
  turntable lifts.
  *Repairs:* a band clamp on the OD at 70–110 mm tied to the turntable; a
  preloaded catch; a sprung carriage seat; a **tilt walk test** with two
  inclinometers, one on the shell and one on the rotator base (their
  difference is the angle change the camera can't see).
- **Difficulty 3: τ is not one gas parameter.** The Richardson number of the jet
  is ≪ 1 at the pool but 0.03–1.5 over the lip. *Repairs:* read heat tint and
  root tint; run τ × flow as a factorial; an optional nozzle skirt.

### Uncovered direction: printed flexures — `ideas/flexure-trim-head.md`

- **Gist.** Fine knobs as flexures, coarse settings from a seated block, stop or
  cradle:
  - A: across-the-corner parallelogram;
  - W: remote-centre pivot whose leaves aim at the seam tangent through the dot;
  - S: standoff parallelogram along the beam.
  Each is driven by a micrometer on a 5:1 flexure lever and preloaded by a steel
  spring. No backlash, stick-slip or lock shift.
- **Numbers** (`flexures.py`, estimates labelled):
  - Parallelograms: ±2 mm (PETG) to ±4 mm (1095 shim).
  - Remote-centre pivots: ±3–13° at D 70 with steel leaves. Drift ∝ D:
    24–42 µm at ±1° for D 70, 75–126 µm for D 150.
  - So **flexure pivots belong within ~100 mm of the dot.**
  - Gravity through printed leaves tilts 0.13–0.26 mm at 150 mm, so load paths
    get steel leaves, or weight along the leaves.
  - Micrometer-held stages relax rather than creep.
  - Thermal growth of printed loops (20–120 µm for 5–15 K) is the bigger
    thermal term. Dry run at steady state.
- **Biggest open problem:** whether ±1–3° / ±2–4 mm covers the fine-tuning the
  process needs (process window unknown). Second: thermal growth over a session.
- **Connects to:**
  - who-moves-what T-b1: supplies S and A, plus T-g's pivot;
  - A1-G: the rider's arc as a flexure;
  - the knob-wired suspension: flexure-lever anchors;
  - my gantry: fine W near the dot, not at 300 mm.

## Wave 5 (final pass)

- **who-moves-what's re-run of my wire search**
  (`../../exchange/who-moves-what--on--one-knob-one-parameter-w4.md`):
  reproduced my result, then showed my search over-constrained the sixth wire.
  - **W-R1:** any point and direction in its plane gives 12 feasible layouts and
    an 18.5 N margin, with the knobs still single. Adopted. Added what they did
    not say: the best wire crosses the open tube (snip side, camera sightline),
    and it sits in the plume. Its thermal growth of 0.03–0.09° of yaw is
    trimmable by the couch Y.
  - **W-R2:** yaw on the couch Y slide makes yaw exact at ±23°. Adopted as the
    default. Nuance: two couch moves or a cam, as in my B-Y.
  - Their negatives (sequence loads; escape-lean wires) are recorded.
  - Their `gravity-in-the-gun-plane.md` combination (one gravity-tensioned hole
    wire at τ*) is noted in my file, with my wave-4 tilt couplings attached.
- **Readability pass.** Every idea file now opens with **Picture it**, sketch
  pointers and major unresolved problems.
- **Sketches brought to the true opening pose (45/30/−15).**
  - `isocentric-*.svg`: −15° set by the Y slide; roll relabelled as the
    clamshell rings.
  - `c-arm-side.svg`: yaw table turned −15°.
  - New `recipe-cartridge-pose.svg`.
  - `flexure-trim-head.svg`: proxy gun tilted with the cradle.
- The summary goes back to the coordinator as text (the harness blocks
  summary files).
