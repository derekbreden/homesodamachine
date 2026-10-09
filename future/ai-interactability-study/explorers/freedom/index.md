# freedom (Freedom and force): every arrangement held

Framing: an arrangement is a set of motions that are free, restrained, driven or locked, and the forces that push along each: gravity, umbilical pull, trigger, wobble, actuators, a hand. Precision belongs to whichever motions are constrained at the moment it matters, not to how stiff or heavy the parts are. Nothing here is ranked or scored. Numbers in the scenes are **illustrative** unless the idea file says otherwise; gun mass, centre of mass and the umbilical's pull are still **[unknown]**.

Idea files: `explorers/freedom/ideas/<id>.md`. Scenes: `scenes/<id>/index.html`. Calculations: `explorers/freedom/calc/`. Exchange: `exchange/freedom--on--eyes-w2.md` (wave 2, to eyes) and `exchange/freedom--reply-to-borrowed-w3.md` (wave 3, borrowed's critique answered). Parts: `sourcing/freedom.md`.

Wave 3: borrowed's critique is answered in the reply and in each idea file's "What was tried to break it" (marked as coming from that exchange). Scenes revised in place: 02, 03, 08, 14 (from the critique), 01b, 01c (mistakes found opening them), 06 and 10 (borrowed's smaller remarks). New direction, the umbilical and the wire conduit as the design driver: 16 (deep), 17 and 18.

## Arrangements and lenses

| id | one line | origin | depth | scene | who moves it / what carries it / what locates it |
|---|---|---|---|---|---|
| freedom-01-ring-bungee | two openable loops (tip, cable pair), wires in Z and bungees in X or Y, an arm grips the shell; every contact and grip solved | derek-example | deep | freedom-01-ring-bungee | arm / wires and bungees, arm carries the rest / the arm |
| freedom-01b-nose-seat | ball collar in a cone seat at the nose (pivot 60 to 110 mm from the dot), tail on a two-wire bridle and a yaw bungee | branch | developed | freedom-01b-nose-seat | nose stage and tail winches / seat and tail wires / the seat |
| freedom-01c-master-per-axis | bungee as compliance, as preload against a stop, or in series with a motor: one master per axis | branch | developed | freedom-01c-master-per-axis | stop, arm, motor anchor / springs by stiffness / the stiffest element |
| freedom-02-balanced-arm | gas-spring arm carries; an XZ vernier and a camera locate; wave 3: the mismatch the arm forgives in grams, the payload counted from parts, the vernier's torque share | derek-example | deep | freedom-02-balanced-arm | vernier (and a shoulder motor) / spring and arm / vernier and camera |
| freedom-03-cable-platform | shell on six taut lines: encoders (observe) or winches (drive); wave 3: the taut margin, the worst pull direction and the cone (borrowed-16 is the deeper scene) | swarm | developed | freedom-03-cable-platform | six lengths or none / lines in tension / the frame |
| freedom-04-free-tangent | lens: which motions must be held (tangent second order, tilt = pivot lever) | swarm | developed | freedom-04-free-tangent | none / not modelled / seam geometry |
| freedom-05-runout-table | runout as a fitted table, vernier follows the rotator angle | swarm | developed | freedom-05-runout-table | vernier over angle / the support (mean only) / model and angle index |
| freedom-06-lock-and-release | friction articulated arm, free while placing, locked to weld | swarm | rough | freedom-06-lock-and-release | lock actuator, hand or vernier / joint clamps / nothing in the arm |
| freedom-07-floating-on-work | floating gun with a two-roller shoe on wall and rim, preload set by software | swarm | rough | freedom-07-floating-on-work | preload actuator / balancer / wall and rim while engaged |
| freedom-08-gravity-tilt | gun hung above its COM: gravity sets tilt, a trim mass adjusts; wave 3: period, damping ratio and overshoot, the cable's lever and couple as sliders (freedom-17 and borrowed-15 carry the keel) | swarm | rough | freedom-08-gravity-tilt | trim mass / the pivot / gravity and trim |
| freedom-09-pose-logger | observe only: six draw-wire encoders and a camera on a hand-positioned gun | swarm | sketch | sense mode of freedom-03-cable-platform | nothing / a passive support / the hand |
| freedom-10-nudge-box | move only, blind: stepper vernier with a home stop; coda: spring retract with a latch | swarm | sketch | freedom-10-spring-retract (coda only) | steps, latch / the stage, spring energy / the stop and screw |
| **freedom-11-eye-on-the-seat** | (wave 2) the gun-borne eye's trim range spent per newton of pull for a rigid-lug elastic against the nose seat and bridle, and a camera map with the cup as an occluder | combination (eyes-01, freedom-01b) | developed | freedom-11-eye-on-the-seat | trim (nose stage) / elastic or seat and bridle / the corner in the eye's image |
| **freedom-12-touch-trigger** | (wave 2) stylus on three contacts: which one opens is the push direction; reading error is trigger force over path stiffness; the same contact can lean | branch (eyes-05), combines freedom-07, datum-07 | developed | freedom-12-touch-trigger | approach stage / three contacts under a spring / tube wall, plate, rim at trigger |
| **freedom-13-map-and-step** | (wave 2) a dry-turn map holds the periodic seam; the bead-start step (pull change × compliance) needs a force term or the eye | branch (eyes-09), combines freedom-05 | developed | freedom-13-map-and-step | trim: map + force term + eye / whatever holds the gun / map, load cell, eye |
| **freedom-14-hand-plus-guidance** | (wave 2, thin region) the hand supplies motion; software supplies a bounded force through a soft anchor, a wall or a damper; wave 3: the damper as a rotary part with a lever (borrowed-19 is the same help on a knob) | swarm | rough | freedom-14-hand-plus-guidance | the hand; anchor motor and damper add force / passive support / the eye |
| **freedom-15-pull-ledger** | (wave 2, thin region) the umbilical, wire conduit and gas hose as the design driver: sources of pull, what changes at bead start, the 1/R² of the fibre, how to measure each | swarm | sketch | none (numbers in freedom-11 and freedom-13) | none / route and balancer / measurement |
| **freedom-16-fibre-line** | (wave 3, the new direction) where the fibre lets go of the gun: four routes (a designed arc to a clip; a straight span along the grip's rake; an arc boot parallel to the roll axis; an S-boot that lands the fibre on the roll axis, the line through the dot) with the force, couple, lever, roll and steps each puts on the gun; a planar elastica solver of its own | swarm | deep | freedom-16-fibre-line | roll motor, rail aim (two small axes) / shell and boot carry the bend, a rail carries the collar / the roll axis; the dot by the eye |
| **freedom-17-hung-on-the-line** | (wave 3, adopts borrowed's sled) a sled pivot on the roll axis in the kit's geometry: the balance the keel needs, the gravity spring, and why gravity cannot hold against a cable that lets go far from the pivot | combination (freedom-08, borrowed-15) | developed | freedom-17-hung-on-the-line | trim mass / pivot, keel, a tail bridle if added / gravity and the bridle |
| **freedom-18-roll-into-twist** | (wave 3, a lens) the roll about the grip axis is part twist, part swing of the fibre's exit tangent (30 degrees off the axis in the kit); twist is spread up to the first rotational hold, a swivel only moves the hold | swarm (lens) | developed | freedom-18-roll-into-twist | roll motor / the fibre as a torsion and bending spring / the roll axis through the dot |

## Questions that need Derek's observation, by idea

- **freedom-16, 18 (new):** where does the fibre leave the grip base and in which direction (a photo along the grip and one from the side, with a ruler)? How heavy and how stiff is the fibre (weigh a metre; overhang 0.3 and 0.6 m off a table edge and measure the tip's drop)? Does the maker give any limit on twist or tension (the manual says twisting is strictly forbidden and is silent on tension: Derek's to ask)? How big is the wire-feed push (dial gauge on the shell, laser off, jog the wire)?
- **freedom-17, 08:** weigh the gun and find where it balances (a thread at two points); the drop time of the gun hung from a thread at the candidate pivot (the point on the roll axis 150 to 200 mm from the dot, measured on the shell); whether a bracket from the barrel collar can reach it without meeting the grip or the wire guide.
- **freedom-02:** weigh the vernier stage with its motors and the camera (they are payload); push the tip of a monitor arm or a mic boom with the Newton meter at 0.5, 1 and 2 N (friction and pre-sliding).
- **freedom-14:** a fluid head's drag, if you have or can borrow one: the Newton meter on the handle at walking pace, smallest and largest step.
- **freedom-01:** the friction limit of a rubber-cushioned P-clamp on a printed sleeve (pull the sleeve through it with the Newton meter).
- **freedom-01, 01b, 02, 03, 08 and every scene with a pull slider (also 11, 13, 15):** the gun's mass and where it balances (a thread at two points); the umbilical's pull at the exit at the working pose along and across (the EISCO Newton force meter, sourcing); which way the fibre leaves the grip.
- **freedom-13, 15:** with the laser disabled, does the gun's support or shell move when the wire is jogged or the gas opened (dial gauge on the shell)? Does it move when the laser starts emitting?
- **freedom-05:** radial and face runout of a few tubes on the rotator, plate seat depth spread, whether the count stays accurate over a turn.
- **freedom-07, 12:** whether a steel ball or roller at a fraction of a newton marks the 316L bore; the wall's local flexibility (2 N with an indicator outside); whether a stylus or roller fits beside the nozzle.
- **freedom-04, 05:** whether the red dot sits on the melt at working standoff; the tolerance at the dot the weld actually needs; the wire's approach tolerance.
- **freedom-06:** whether a photo-arm clamp holds 1.2 to 1.5 kg at 200 to 400 mm.
- **freedom-10:** how fast and how far the head leaves at the end of a bead (phone video).
- **freedom-14:** how far your relaxed hand yields per newton at the grip, at the working pose; the drift and tremor of the gun in your hand over a lap; whether you would accept a gun that pushes back 0.2 N if you could always push through it.
- **freedom-11:** whether a degree or two of beam turn matters to the weld.

## Related arrangements of others that answer mine (kept in their files; nothing of theirs is edited)

- `borrowed-14-arm-mass-window` (branch of freedom-02): the arm's payload counted from parts, three springs, the strip of bought arms.
- `borrowed-15-sled-keel` (branch of freedom-08, combines 02 and 14): a keel, a damper and the cable anchored on the pivot; my `freedom-17` adopts it as a combination.
- `borrowed-16-taut-cone` (branch of freedom-03): the taut set over pull directions and a bought preload; stays their scene, the route-first answer is in the reply.
- `borrowed-19-haptic-jog` (combines freedom-14): the same help on a knob; a different arrangement, answered in the reply.
- `borrowed-13-hexapod-pivot` (combines freedom-02): a software pivot, six legs; noted in freedom-01b and freedom-04.

## Calculations

`calc/statics.js` (one rigid body on springs, Newton solver, Hessian; page or node), `calc/ringmodel.js`, `calc/20-balanced-arm.js`, `calc/22-cable-layout.cjs`; wave 2: `calc/eye-support.js` (the lug-and-elastic and nose-seat supports with a trim loop, used by `freedom-11`), `calc/29-eye-support-budget.cjs`, `calc/30-eye-support.cjs` (mm per newton by support), `calc/31-cable-gauge.cjs` (the umbilical as a spring: EI/R² and 3EI/l³).
