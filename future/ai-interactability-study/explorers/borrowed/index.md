# Summary: borrowed (Borrowed from elsewhere)

Framing: mass-produced products sold for other purposes already do parts of this job; for each piece, which product, what is taken, what changes, how fast it is in hand. Nothing here is ranked or scored. Maturity says how far I took an idea, not how good it is. Wave 1 observed 2026-09-28/29; wave 2 (the exchange with freedom, Derek's examples, the thin region of bought positioners) 2026-09-29. Numbers are illustrative unless the idea file tags a source; the gun's mass and centre of mass and the umbilical's pull are still **[unknown]**.

| id | arrangement | how motion is assigned | maturity | scene | idea file |
|---|---|---|---|---|---|
| borrowed-01-ring-pivots | Telescope-style bearing rings around empty axes through the dot (yaw ring above the rim, trunnion ring outside the wall, roll ring at the grip base), frame on a bench post, trim stage under the frame | three ring drives (belt, friction, worm) plus two trim axes; software commands angles | deep | `scenes/borrowed-01-ring-pivots` | `ideas/borrowed-01-ring-pivots.md` |
| borrowed-02-gimbal-on-gantry | Stabiliser gimbal balanced on the gun (orientation) hung from a printer-style gantry that cancels the dot's swing (position); dot = C - t g | gimbal motors for angles, gantry motors for XYZ, software composes with one formula | deep | `scenes/borrowed-02-gimbal-on-gantry` | `ideas/borrowed-02-gimbal-on-gantry.md` |
| borrowed-03-encoded-arm | Spring-balanced monitor/lamp arm with a magnetic encoder per joint: a hand-guided measuring arm; software observes and coaches | the operator moves; nothing driven | deep | `scenes/borrowed-03-encoded-arm` | `ideas/borrowed-03-encoded-arm.md` |
| borrowed-04-axis-map | Analysis: which axis directions through the dot can hold a shaft, a two-sided shaft or a ring bearing | none (analysis) | developed | `scenes/borrowed-04-axis-map` | `ideas/borrowed-04-axis-map.md` |
| borrowed-05-guide-star | Astrophotography autoguiding as bring-up: nudge each trim axis, watch the dot, solve the matrix and backlash, then guide | two trim axes of any arrangement; simulation | developed | `scenes/borrowed-05-guide-star` | `ideas/borrowed-05-guide-star.md` |
| borrowed-06-swing-offset | The gun's own swing motor and red-light shift as a fine axis across the seam (if software can set it) | the head's internal swing centre; nothing else moves | developed | `scenes/borrowed-06-swing-offset` | `ideas/borrowed-06-swing-offset.md` |
| borrowed-07-tonearm | Counterbalanced arm with a ball foot on the rim: the tube's rim sets the dot's height with no sensor | passive; the rotating tube moves the arm | rough | `scenes/borrowed-07-tonearm` | `ideas/borrowed-07-tonearm.md` |
| borrowed-08-manual-stack-spotter | Cross-slide, jack and geared head with digital scales; software computes coupled knob readings and reads a camera; a person turns knobs | a person; software observes and instructs | rough | `scenes/borrowed-08-manual-stack-spotter` | `ideas/borrowed-08-manual-stack-spotter.md` |
| borrowed-09-hand-controller | Small leader arm (SO-101 pattern) or 6-DoF puck as the hand controller for a larger follower; demonstrations recorded | a person moves the leader; the follower is another idea | sketch | none | `ideas/borrowed-09-hand-controller.md` |
| borrowed-10-gun-free-dot | Pan/tilt laser pointer stands in for the dot so the camera and calibration chain can run dry | two hobby servos | sketch | none | `ideas/borrowed-10-gun-free-dot.md` |
| borrowed-11-balancer-festoon | Spring tool balancer carries weight from above; umbilical on a festoon track or in a cable chain | none; carrying and cable | sketch | none | `ideas/borrowed-11-balancer-festoon.md` |
| borrowed-12-other-trades | Axes from other trades: stage-light yoke, window regulator, wiper motor, desk column, welding positioner, roller rotary; wave 2 adds the locking gas spring and the chair gas lift | per donor | sketch | none | `ideas/borrowed-12-other-trades.md` |
| **borrowed-13-hexapod-pivot** | (wave 2, thin region: bought positioners; combination: drawn on freedom-02's arm as its carrier) A hexapod with a ring platform just above the rim, clamped on the shell near the nozzle, the centre of rotation a software number set on the dot; the gun's body leaves through a gap between leg pairs; variable-length struts or fixed rods on vertical rails (delta-printer parts) | six leg lengths from one 6-D pose about a chosen pivot; software commands all six | developed | `scenes/borrowed-13-hexapod-pivot` | `ideas/borrowed-13-hexapod-pivot.md` |
| **borrowed-14-arm-mass-window** | (wave 2, branch of freedom-02; Derek's monitor-arm example) The balanced arm with the payload counted from parts, the spring drawn as a gas spring or an Anglepoise spring-and-parallelogram (plain or zero-length), the mismatch friction forgives in grams (+-0.09 kg at 0.4 N.m and 0.45 m) and a strip of bought arms' rated windows | by hand inside the friction window; passive | developed | `scenes/borrowed-14-arm-mass-window` | `ideas/borrowed-14-arm-mass-window.md` |
| **borrowed-15-sled-keel** | (wave 2, combination: branch of freedom-08 with 02 and 14) A stabiliser sled for freedom-08's plumb bob: a keel sets the gravity spring, a fluid-head damper turns ringing into settling, and the cable anchored on the pivot removes the force's lever; the couple is what is left | no tilt actuator; an optional trim mass on a screw | developed | `scenes/borrowed-15-sled-keel` | `ideas/borrowed-15-sled-keel.md` |
| **borrowed-16-taut-cone** | (wave 2, branch of freedom-03) The taut set of six lines from above as a map over the direction of the fibre's pull, for the shipped layout, a robustness-searched layout and a layout searched for a 10 N downward preload from a spring balancer | not moving: line lengths from the frame | developed | `scenes/borrowed-16-taut-cone` | `ideas/borrowed-16-taut-cone.md` |
| **borrowed-17-positioner-shelf** | (wave 2, lens; thin region and Derek's PTZ and robot-arm requests) What ordinary arms, telescope mounts, PTZ cameras, printer and CNC gantries, rails, sit-stand frames, drawer slides and a laser-alignment hexapod state, how each is spoken to, and what a Prime listing costs and when it arrives | per product | developed | `scenes/borrowed-17-positioner-shelf` | `ideas/borrowed-17-positioner-shelf.md` |
| **borrowed-19-haptic-jog** | (wave 2, thin region: the hand supplies motion, software supplies resistance; combination of freedom-14 and borrowed-09) A knob on a brushless gimbal motor with a magnetic encoder whose feel is a program: detents, a wall past the eye's seam, a capped pull toward the seam, a damper; it jogs a fine axis and the gun is never touched | the hand turns the knob; software renders torque and moves the stage | developed | `scenes/borrowed-19-haptic-jog` | `ideas/borrowed-19-haptic-jog.md` |
| **borrowed-18-examples-in-hardware** | (wave 2, Derek's examples) What bought hardware would realise suspension, the monitor arm, the table opening and the automated-setup vision, with the number that matters and what each product changes | per example | sketch | drawn in borrowed-14 to 17 | `ideas/borrowed-18-examples-in-hardware.md` |

Not developed on purpose: a used industrial six-axis arm (the obvious first one; the reference the others are measured against). Wave 2 puts one collaborative arm on the shelf (Fairino FR3: 3 kg, +-0.02 mm, a maker product) as that reference in `borrowed-17`.

## Combinations (wave 2)

- `borrowed-19-haptic-jog` (freedom-14 + borrowed-09; drawn): the same three helps (wall, centring, damper) on a handle instead of the gun.
- `borrowed-15-sled-keel` (freedom-08 + freedom-02 + freedom-14; drawn): the keel fills a monitor arm's payload floor and sets the spring, the fluid head is the damper.
- `borrowed-16-taut-cone` (freedom-03 + a spring balancer; drawn): a preload only helps a layout made for it.
- The cable anchored on the pivot (freedom-15 + freedom-08; drawn as a preset of the sled scene).
- A hexapod as freedom-02's location path (named; its mass fills the arm's payload floor); the hexapod ring and freedom-01b's seat (the same pivot-near-the-dot logic); a locking gas spring for freedom-06 and freedom-10 (named).

## Questions that need Derek's observation, by idea

- **borrowed-14, 15, 16 and 03, 02:** weigh the gun in its shell, the vernier stage with its motors, the camera (kitchen scale to 25 g); gun centre of mass (thread at two points).
- **borrowed-15:** drop time of the gun hung from a thread through each candidate pivot (stopwatch; the period gives K/I); the tilt from plumb with the fibre attached and laid as it will lie (the cable's torque, force and couple together); a fluid head's drag by the Newton meter on the handle, smallest and largest step.
- **borrowed-14:** push the tip of a monitor arm or mic boom with the Newton meter at 0.5, 1 and 2 N: give and hold.
- **borrowed-16:** the fibre's direction as well as its size at the working pose (Newton meter along and across the exit, a photo of the route).
- **borrowed-13:** play and lost motion of a printed hexapod prototype; whether a ring of 50 mm radius fits beside the wire guide and the beam (a printed sectioned shell).
- **borrowed-19:** does a hand on a knob with feel beat the hand on the gun or a plain handwheel? (an afternoon and a $35 kit); the torque and cogging of a bought gimbal motor.
- **borrowed-17, 18:** which of these does Derek already have (a printer, a monitor arm, a mic boom, a telescope mount, a PTZ camera)?
- **From wave 1, still open:** red-light alignment (borrowed-06); plate depth across tubes and rim-versus-plate parallelism (borrowed-07); useful travel of a skilled hand (borrowed-03); fibre twist tolerance (borrowed-01, 02); can any camera see the dot in the corner (borrowed-05).

## Supporting material

- Notebook (wide list, development log, wave 2, open threads): `notebook.md`. Scripts behind numbers: `calc/` (wave 1: `free_directions.py`, `gimbal_geometry.py`, `encoder_error.py`, `guide_star_sim.py`, `spotter_rounds.py`, harnesses `probe.mjs`, `scene_grid.mjs`, `ring_grid.mjs`; wave 2: `arm.js`, `sled.js` (models shared with the scenes), `w2-arm.cjs`, `w2-sled.cjs`, `w2-taut-set.cjs`, `w2-robust-layout.cjs` and its `.json`, `w2-verify-layouts.cjs`, `w2-cone-check.cjs`, `w2-slack-sweep.mjs`, `w2-hex-sweep.mjs`, `elshot.mjs`).
- Exchange: `../../exchange/borrowed--on--freedom-w2.md` (from me to freedom); `../../exchange/trials--on--borrowed-w2.md` (from trials to me; answered in wave 3).
- Sourcing: `../../sourcing/borrowed.md` (wave 1: 13 entries observed 2026-09-28; wave 2: about two dozen observed 2026-09-29, Prime only, plus maker and reseller sources marked as such).

## Transferable pieces (for the exchange)

- Ring bearing around an empty axis, and a free-direction map (04, 01); a hexapod's software pivot as the same thing without a bearing (13).
- dot = C - t g: orientation from a balanced gimbal, position from any XYZ (02, 08).
- Joint-error to dot-error propagation and touch-off zeroing (03); recording the poses a skilled hand uses (03).
- Nudge-and-watch calibration, backlash from a reversal, wall thickness as the scale bar (05).
- Use the head's own scanner as the fine axis (06).
- Counterweight sets a follower's force; arm angle as a free runout readout (07).
- Mismatch tolerance in grams = friction / (g L cos); zero-length spring balances at every angle; count the location path's mass as payload (14).
- A keel is a chosen gravity spring and a gear on the trim; anchor the cable on the pivot; drop time measures the spring (15).
- The taut set as a map over pull directions; a preload only helps a layout made for it (16).
- Angular step times lever is millimetres at the dot; a rating is a window on mass, not moment (17).
