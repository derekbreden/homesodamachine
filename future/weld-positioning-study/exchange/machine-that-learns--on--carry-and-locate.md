# machine-that-learns on carry-and-locate

Wave 2, 2026-09-28. I read carry-and-locate's four ideas, notebook and calcs
as they stood at 05:28, after they applied the scene's 35° hole-dial offset.
Their pose module now agrees with my port to 0.1 mm at the opening pose, so I
used their module directly for the calculations below. Calcs and the sketch
are in `explorers/machine-that-learns/calc/exchange/` and
`explorers/machine-that-learns/sketches/exchange-follower-section.svg`.

My view: the station as something software moves and observes. Their view:
carrying and locating are different jobs. The main thing I add to their view is
that **locating itself splits into sensing and acting.** The sensor can be a
camera, a stylus or a wire length. The actuator can sit anywhere in the loop,
as long as the sensor closes the loop around the thing that matters.

I worked on three of their ideas: the suspension original (developed
furthest), the wire-located suspension, and the rim carriage (left roughest).
There is one line on float-and-dock at the end.

---

## 1. Suspension, original — can a camera and a small correction make softness hold a dot?

**Variant.** Derek's two loops, as they developed it. The bungees hold X
(radial), the pendulum is left free on Y, and the stiffness at the tip node is
~0.1 N/mm. Branch A-r1 (float + arm) leaves the arm unspecified.

**The difficulty.** The float returns to its equilibrium, not to where it was
put. Their load table has a 2 N wire push, a 3–8 N trigger and slow cable
creep. Through 0.1 N/mm those become millimetres to centimetres.

**The assumption I tested.** Every usable form of the suspension needs a stiff
locator during the weld. The alternative the coordinator asked about is a
camera watching the dot while something small moves the float's anchors to
hold it (sensing plus acting instead of stiffness).

**Model** (`servoed_float.py`). One degree of freedom along X:
m ẍ + c ẋ + k(x − u) = F(t), with m = 1.5 kg on the tip node and
k = 0.1 N/mm. The camera samples x at 30 fps with 60 ms latency. A stepper
slide moves the bungee anchor u at up to 50 mm/s under PID. The gains were
searched over a grid, and only sets that settle were accepted.

| Disturbance (their load table) | Anchor fixed | Camera loop, float as built (ζ ≈ 0.03) | Camera loop + damper (ζ = 0.5) |
|---|---|---|---|
| Wire push, 2 N ramped over 0.3 s | 34 mm peak, 24 mm held | no stable gain in the grid | 17 mm peak, back within 0.06 mm |
| Trigger, 5 N step (hand on the gun) | 96 mm peak | — | 50 mm peak, back within 0.11 mm |
| Cable creep, 0.5 N over 60 s | 0.5 mm | — | within 0.08 mm |

What this says:

- **Undamped, the loop cannot be closed at all.** A ~1.3 Hz, lightly damped
  float plus ~77 ms of camera delay leaves no phase margin once the loop
  crosses the resonance. A soft suspension needs real damping before any
  servoing: a dashpot, or an eddy-current vane on the node. Cranes have the
  same anti-sway problem.
- **With damping, the camera makes the float an excellent placer and drift
  canceller.** Slow drift is nulled to below 0.1 mm, and steady forces are
  trimmed out within a second.
- **It is not a holder.** The wire push starts with the bead, and anything
  acting faster than a 30 fps loop can respond through a 0.1 N/mm spring
  becomes a 10–50 mm transient. Holding 2 N to 0.05 mm needs ~40 N/mm at the
  dot, and that has to be mechanical.
- **During the weld the red dot cannot be seen** (process glare). A weld-time
  loop would have to track fiducials on the shell, lit by a narrowband LED and
  filtered. That is feasible, but the table shows it would not help against
  the onset forces.

So the assumption survives, with a sharper boundary. Softness plus a camera is
the right tool for **setup, dry runs and drift**. A mechanical hold is needed
**only during the weld**.

### Branch A-r4c — place soft, lock stiff, let the camera learn the lock

This is their A-r4 (soft for setup, locked for the weld), made automatic and
precise. The original A-r4 stays as they wrote it.

- **Carry.** Derek's loops and saddle, unchanged: the tip loop carries 56–68 %
  and the base loop the rest plus cable (their corrected shares).
- **Place.** The Z wires run to small winches and the X bungee anchors sit on
  printer-class slides. Add a damper at the tip node (ζ ≈ 0.5). The camera then
  drives the float to the target in dry-run mode. This is Derek's
  automated-setup vision in suspension form: the motors move the float's
  equilibrium, not the gun directly.
- **Lock.** The locking has to be done by a shell feature at the node, not by
  the loop. A round loop on a round barrel still lets the barrel slide and
  roll. The tip node carries a ball or short trunnion on the shell, and a split
  clamp closes it against a vertical 16 mm steel rod standing on the rotator
  base, outside the tube. As a cantilever at 200 mm that rod is ~240 N/mm
  (3EI/L³; a 10 mm rod would be only ~37 N/mm). The base node gets a second
  rod clamp, and roll gets a brake on their A-r2 trunnion.
- **Learn.** Every lock is measured: dot before, dot after. The clamp's shift
  has a bias and a scatter. After some tens of locks the bias is known, and the
  float is placed at the target minus the bias ("lock where it will land"). If
  the scatter is too large, the machine unlocks, trims and relocks until it is
  inside tolerance — the station has hours to do this.
- **Weld.** Locked. The 2 N wire push onset against ≥150 N/mm at the node
  moves the dot about 0.01–0.02 mm (rod and clamp only; the node and shell are
  not counted). The trigger is pressed inside the shell (their presser or my
  Bowden lever).
- **Stuck wire.** The clamp holds to its friction limit (tens of N). The wire's
  stick-out yields at 3–5 N first, so the gun stays put for the snip, as the
  procedure asks.
- **Tube change.** Unlock and lift: the float carries everything. Change the
  tube, lower, and the winches and slides still hold the placement. Relock, and
  the camera confirms.

**Still open:** the node design around the real shell; the lock's shift
scatter (only measurement will tell); whether the rods can stand on the
rotator base without meeting the table-indexing path of plate hangers during
tacking; the damper hardware.

---

## 2. Wire-located suspension, driven as a cable robot

Their idea is six taut wires. Three of them have lines meeting at the dot, so
they act as a virtual ball joint; bungees only keep the wires taut. They
suggest six motorised anchor slides. I evaluated their current all-taut layout
as a cable robot: anchors fixed, wire lengths driven, statics re-solved at each
pose with gravity, both preloads, ±5 N pushes at the dot and a 5 N trigger push
(`wire_robot_workspace.py`, using their module and layout).

| Move from the design pose | Wire length changes (W1…W6), mm | Worst-case min tension | Dot deflection under 5 N |
|---|---|---|---|
| grip-axis roll ±10° | W1–W3 ≤ 1.2; **W6 alone** +15.5 / −12.7 | 3.3–6.4 N | 32 µm |
| hole axis −10° / +5° | W4, W5 +38 / −18; W6 −4 / +5 | 1.7 / 3.6 N | 31–32 µm |
| hole axis +10° | W4, W5 −35 | **−0.7 N (slack)** | — |
| vertical axis −10° (rotation) | W4 +21, W5 −9, W6 −8 | **−3.9 N (slack)** | — |
| vertical axis ±10° **as a tangent translation** (±10.7 mm) | W1 ∓6, others ≤ 5 | 3.2 / 4.3 N | — |
| vertical axis ±15° as a translation (±16 mm) | ≤ 9.4 | 1.3 / 2.8 N | — |
| dot ±5 mm in x, y, z | ≤ 4.8 | 5.1–7.1 N | 31 µm |

**Difficulty 1 — the layout goes slack when turned about the vertical axis.**
In their layout, −10° about the vertical line through the dot slackens a wire.
**Assumption:** the positioner must physically rotate about the vertical axis.
**Repair:** it need not. The joint is a circle, so plan angle is a tangent
translation (16.1 mm for 15°). Done that way, ±15° keeps every wire taut with
1.3 N to spare, where rotating by only −10° already slackens one. Grip-axis
roll is almost a single-motor axis (W6 alone, with W1–W3 changing by at most
1.2 mm).

The cable robot's natural neighbourhood is therefore:

- dot ±5 mm;
- roll ±10° on one wire;
- hole axis −10° to +5°;
- plan angle ±15° by translation.

Beyond that, the anchors move to a new layout (a per-recipe anchor set, which
fits their "layout per neighbourhood").

**Difficulty 2 — the "collar" is three spokes, and one crosses the camera's
side.** At the corrected pose the three concurrent attachments are 19, 60 and
67 mm off the barrel axis, 57 mm above the dot. W1 (azimuth 90°, the free +Y
side) passes within 27 mm of my joint camera's line of sight. **Repair:** add
the camera's line of sight as a keep-out in their layout search (rotate the
triad), or put the camera in the triad's gap. The spokes are printed and sit
within ~60 mm of the weld, so they need a metal shield against spatter and
reflected 1080 nm light.

**Difficulty 3 — bungee preloads change as the robot moves.** At 0.1 N/mm, a
40 mm move of the grip butt shifts a preload by ~4 N against margins of
1–7 N. **Repair, either:**
- a constant-force spring balancer as each preload (they already sourced QWORK
  balancers), or
- a seventh motorised wire. With seven wires for six degrees of freedom, wire
  tension becomes a commanded quantity, and motor current or a cheap load cell
  reads it back.

**Hardware as a robot.** Six slides aligned with the wires, each with a swivel
eye on the carriage. Travel needed:
- W1–W3: ±10 mm;
- W4, W5: ±45 mm;
- W6: ±20 mm.

SFU1605 stages (the Prime commodity in my sourcing) give 1.6 µm of length per
microstep; closed-loop NEMA 17 boards give a knob-first mode.

**The camera calibrates it.** The anchor and attachment coordinates (36
numbers) are known only to millimetres. The machine calibrates them by moving
each slide and observing the dot and shell fiducials — the standard
cable-robot calibration. The virtual pivot's second-order drift (1.2 mm at
10°) then becomes a term in the model, not an error the operator has to
re-trim.

**What "fixed" is fixed to.** The anchor frame. The wires give ~160 N/mm at
the dot, so the frame needs to be several times stiffer at the anchors, or it
dominates. A push test with the camera watching measures this directly.

**Against my own hexapod (C)** this is better on the points that sank C:
- **Play:** C's 0.12 mm median dot error came from ±0.05 mm of joint and nut
  play. Wires have no joints, only elastic stretch that is linear and
  repeatable (5 N → 31 µm).
- **Heat:** the actuators sit ~400 mm from the weld.
- **Lift-off:** tension-only, so lift-off and return are free.

I would now develop the six-wire layout rather than C as the "all freedoms
actuated" option.

---

## 3. Rim carriage (left rough) → branch D-s: sense, don't carry

Sketch: `explorers/machine-that-learns/sketches/exchange-follower-section.svg`.

**Variant and difficulty.** In D as written, the carriage that follows the
tube also carries: 10–20 N of float residual, plus the ring and gun,
through rollers on a 1.65 mm lip. That lip is warm and possibly burred. The
rim is 6.35 mm from the joint, so cap tilt goes unseen. The rollers bond the
gun electrically to the work (their own interlock question). A 48° open ring
must be stiff in torsion. Ovality leaks at ±0.42e.

**Assumption:** whatever follows the tube must also hold the gun.

**Branch D-s.** Keep the following, drop the carrying:

- **Stylus.** A ceramic ball or small ceramic-bearing wheel on a stainless stem
  touches the tube's **outside diameter at the dot's own angle**, ~9 mm below
  the joint level, with 0.5–1 N of spring.
- **Scale.** The stem runs on a slide whose scale is read continuously. Options
  are an iGaging Absolute Origin caliper's beam with its SPC port ($47.77
  Prime, "900+ bought in past month"; ESP32 readers of that clock/data port
  are a known hack, not verified here), or an AS5048 on a lever.
- **Stand.** It sits on whatever carries the gun: the portal in my A, the gun
  carriage in my B, the bridge in my D.

**What that fixes.**
- **Tube and interlock:** 0.5–1 N is far below the 6–8 N radial push that
  would lift the tube in the nest, and an insulating tip makes no electrical
  path to the gun.
- **Ovality:** at the dot's angle it is measured, not leaked.
- **Rim vs joint:** the stylus reads the wall, not the rim.
- **Weld-time reference:** it works during the weld, when the camera cannot
  see the red dot. It reads runout, ovality and thermal growth of the wall
  where the bead is being laid — the gap my dry-run maps leave (my estimate is
  ~0.1 mm of radius per 100 K).

**What it leaves.**
- **Wall-thickness variation:** the stylus reads the outside, the joint is on
  the bore. The spec is ±10 % of 1.65 mm, and the variation around one tube is
  unknown. A dry-run camera map of the bore against the stylus trace
  calibrates it once per tube.
- **Seam bump:** the welded tube's outside seam passes the tip once per
  revolution; it is known and can be masked.
- **Face runout:** needs a second stylus on the rim top, or the camera's dry-run
  map.
- **Heat at the tip:** the stylus sits in hot metal during the weld, so the
  scale must be kept 60 mm or more away.
- **No passive following:** it needs an actuator (my X stage).
- **No stuck-wire fuse:** it loses D's "the don't-care rotation is the fuse".

**Use.**
- A: the X stage moves the tube to keep the stylus reading constant.
- B: the gun's X stage does the same.
- D: the reading guides the hand wheels.

Every weld leaves a stylus trace in the log. That is the dataset for learning
thermal growth against speed and power.

---

## 4. Float and dock — one line

Their open question was which stack under the seat gives Derek's rotations
about the dot without re-trimming the dot. My B's answer is:
- X, Y, Z;
- an arc about the hole axis;
- a yoke on the grip axis;
- and the vertical axis is not a joint at all (it is the Y translation).

The camera sets that stack and checks every dock. Our docks converged: their C
is my D with a balancer.

---

## What their ideas do that mine lack

- **Separate carriers.** A balancer at the centre of mass and a saddle before
  the grip take most of the gun's weight and the cable off whatever locates. My
  B carries ~3 kg through five stages in series, and my C carries it through
  the legs. Borrowing their float would cut the load on B's chain and C's legs
  by an order of magnitude and make B's stiffness problem largely go away. (For
  C, a small deliberate bias force would still be needed so the joint play
  settles on one side.)
- **Tension-only return.** Lift the gun off and set it back, and it is back.
- **A fuse.** The don't-care rotation (rim carriage), or slack wires, give way
  when a stuck wire pulls, instead of bending the wire guide or overloading a
  stage.
- **A full load inventory.** I had magnitudes for the camera, but not their
  table of every force on the gun and where each should go.

## What transfers from mine to theirs

- **Plan angle as translation.** This keeps their wires taut where the
  rotation slackened them.
- **Camera as setter and verifier.** It sets and checks every locator (stack,
  wires, ring) and learns lock and dock biases.
- **Weld-time sensing.** Fiducials on the shell, or a stylus, because the dot
  itself is blind during the weld.
- **Printer-class motorisation with a hand knob.** One mechanism for manual and
  automatic use.
