# freedom-03: six taut lines (measured first, driven later)

Scene: `scenes/freedom-03-cable-platform`. Origin: swarm original (from the freedom framing). Depth: developed (five break-and-repair entries). Numbers from `calc/22-cable-layout.cjs`, `calc/23-cable-platform.cjs`, and the scene's model; **illustrative** unless tagged.

## Picture it

The printed shell has six small lugs. From each, a thin line runs up and outward to an overhead frame and ends on a drum. Nothing clamps the gun; the lines only pull, and the gun's own weight keeps them taut. In the first version the drums are encoders, someone moves the gun by hand and a screen says where the dot is. In the second the drums are winches and software chooses six lengths.

## The proposal

A **tension-only platform**: six lines from lugs on the shell to a frame above. Its properties follow from three facts of a taut line: it is stiff along its length (EA/L), it is soft across, and it cannot push. Six well-spread taut lines are stiff in all six directions at once, provided none goes slack. The stiffness is *geometry*: it comes from the lines being long and pulled, not from any part being massive.

Two stages, one hardware set:

- **Sense** (software moves and observes; the hand positions): the drums are draw-wire encoders (a spool, a return spring, an encoder). Six lengths give the gun's pose by forward kinematics. Something else supports the gun (the ring-and-bungee suspension or a balancer); the encoders' own retract springs even carry most of the weight.
- **Drive** (software moves): the drums are winches. Software turns a commanded pose into six lengths by inverse kinematics, optionally removing the predicted elastic stretch, and the platform follows. A camera closes the loop on the dot.

## What carries the loads, what establishes position, what is free or restrained

- **Weight**: the lines, in tension, by geometry; the frame carries the lines.
- **Position of the dot**: six line lengths from the frame. The frame is the reference.
- **Restrained**: all six degrees of freedom, softly (line stretch) and unilaterally (a line can only pull).
- **Free**: nothing, as long as every line is taut; the moment one slackens, one direction of one motion is free.
- **Driven**: six winches (drive mode); none (sense mode).
- **Umbilical**: pulls on the shell and, in sense mode, competes with the retract springs; it is what closes or opens the force loop.

## What software could command, observe, and what stays manual

- **Command** (drive): six lengths; optionally stretch compensation.
- **Observe**: six lengths (encoder resolution 0.005 to 0.05 mm is easy with a magnetic encoder on a small spool), six tensions (winch motor current, or an inline load cell), the dot by camera. In sense mode the pose comes from the encoders alone. The scene computes the dot's uncertainty from the length resolution through the actual layout: 0.05 mm resolution gives about 0.09 / 0.06 / 0.07 mm (radial / tangent / vertical, one sigma of a quantisation step) at a pose 4 / −3 / 2 mm from the reference.
- **Manual or unresolved**: fitting the lugs and lines; routing the umbilical clear of the lines; in sense mode the hand and the second support.

## What was tried to break it

**Entry 1. Four lines are not enough.**
- Conflict: two lines at the nozzle and two at the tail leave the shell under-constrained: every line taut, and the shell hangs 62 mm and about 66° from the commanded pose, wherever gravity and the umbilical settle it (`calc/23-cable-platform.cjs`).
- Assumption: taut lines mean a held pose. Taut lines mean equilibrium of the forces, not a unique pose.
- Change: six well-placed lines (the layout was found by a random search that requires every line positive under gravity and 2 N to 4 N of umbilical pull, with clearance from the gun body: `calc/22-cable-layout.cjs`).
- Leaves uncertain: whether six lines fit around the tube and the operator.

**Entry 2. Slack is the failure.**
- Conflict: with the found layout the lines carry 1.8 to 4.3 N each at the reference; a 6 N umbilical pull along the cable exit takes one line to zero and the dot moves 23 mm. Tension-only means the workspace is bounded by slack, not by reach.
- Assumption: gravity keeps everything taut.
- Change: pre-tension with a spring or a seventh line from below; choose the layout for wrench margin, not only for the reference pose; route the cable so its pull is down or back (not up and out).
- Leaves uncertain: the real umbilical pull (unknown) and direction.

**Entry 3. Stretch is a pose error, and it can be predicted.**
- Conflict: a thin braid (EA about 3 kN, illustrative) sags 0.73 mm under the reference load and is about 8 times softer at the dot (0.55 / 0.24 / 0.36 mm/N) than a 1 mm synthetic line (EA about 25 kN: 0.067 / 0.029 / 0.043 mm/N; a 1 mm steel rope at 40 kN: 0.042 / 0.018 / 0.027).
- Assumption: a commanded length is a delivered length.
- Change: command the length that removes the predicted stretch (the scene's stretch-compensation toggle takes the static error to zero); use a stiffer line.
- Leaves uncertain: creep and hysteresis of synthetic lines (not modelled; creep is the classic problem of UHMWPE lines under sustained load), knots, spool winding.

**Entry 4. Frame spread is a design parameter.**
- Change of the anchor spread by 0.5×, 0.75×, 1.25× moves the dot's compliance from 0.13 / 0.05 / 0.03 to 0.062 / 0.031 / 0.056 mm/N and the line tensions from 1.4 to 3.8 N to 2.2 to 4.9 N. Wider is better conditioned and worse for clutter over the tube.

**Entry 5. Measuring loads the thing measured.**
- Conflict: six draw-wire encoders each carry a retract spring; at an assumed 2 N each they pull with a net 8.9 N (0.4 / 2.4 / 8.5 N x / y / z), about 72% of the gun's weight, and a net torque.
- Assumption: sensing is free.
- Change: use it: the encoders' own springs are most of the weight support in sense mode; the remainder is a light bungee or balancer. Or use magnetic encoders with a weaker return.
- Leaves uncertain: the real retract force of the encoders ([unknown]; the CALT listings do not state it).

**Entry 6 (wave 3, from borrowed's exchange, section 2). Taut is not held: the lines are taut inside a cone of pulls. Decision: revised (scene readouts) and the branch adopted (`borrowed-16-taut-cone` stays as their scene); the question answered with a run.**
- Conflict: entry 2 says "gravity keeps them taut" and the scene's panel reads "all taut" with the umbilical at 0 N, where two of the six lines carry 0.3 and 0.4 N (3.6 / 3.8 / 2.8 / 0.3 / 0.4 / 4.8 N; the scene rounds to 0.1 and 0.2 at its exact pose). The layout is taut because the fibre pulls, along a direction it was searched for (three particular pulls). Six lines for six freedoms fix the tensions uniquely, so the layout is taut only for loads inside a cone. Re-run (borrowed's `w2-taut-set.cjs` and my own `calc/32-cone-narrow.cjs`, 6000 directions): the worst direction slackens a line at 0.13 N; 58 % of directions below 1 N, 82 % below 4 N, 96 % below 8.7 N.
- Assumption: gravity is the preload and the fibre pulls along its exit. The fibre's direction is a routing choice nobody has made.
- Change: the scene now reads the margin along the pull you set (6.4 N at 2 N of pull and droop 0.5), the worst direction anywhere, the slack pull within ±10 degrees of the current direction (4.7 N) and warns when the smallest tension is under 0.5 N. The mistake in the scene (a readout that said "all taut" for a layout one grain from slack) is fixed. What the cone means for a known direction: about the exit axis the layout holds to 5.5 N; a pull known to within ±8 degrees holds it to 5.3 N; ±10 degrees 3.2 N; ±15 degrees 1.0 N.
- Answer to borrowed's question ("the layout for the route, or the route for the layout?"): the route first. The manual's bend limit, the exit direction and the clip leave the route little freedom; the layout is a cheap search (16 million random tries in borrowed's script). A route that fixes the fibre's direction, such as freedom-16's boot and rail, turns the shipped layout from a fragile one into a good one, and a layout can then be searched for that route's cone, as borrowed-16 does for a 10 N preload. A preload only helps a layout made for it: 10 N down at the grip base takes the shipped layout to two slack lines.
- Leaves uncertain: rigid lines at the reference pose only (stretch, creep and frame spread still apply); the balancer's line has to reach the grip base past the tube and the bench; the real fibre direction.

## Branches and combinations

- Sense-only stage: the cheapest software-observes-and-moves-nothing version (see freedom-09).
- With freedom-01b: the tail bridle is two of these lines.
- With freedom-05: a vernier can ride any of the six lengths as a table.
- With freedom-01: the ring-and-bungee suspension carries the weight while the lines measure.

## Unresolved problems, and questions that need Derek's observation

- Line routing that clears the tube, the gun body and the umbilical.
- The lugs and a shell that does not flex under 4 N line loads.
- Winch resolution and backlash on a small spool; creep of the line.
- Measure the umbilical pull at the exit at the working pose (as freedom-01).
- How does the fibre behave when the gun rolls? (Twist, manual p. 20.)

## Assumptions

- Gun and shell 1.2 kg; COM at (0, −18, 178) local: **illustrative** (gun mass **[unknown]**).
- Layout: random search result, lug positions and line directions **illustrative**; frame 600 mm above the bench-zero.
- Line EA 3 / 25 / 40 kN: order-of-magnitude, **illustrative**; not from any listing.
- Encoder retract 2 N, resolution 0.05 mm: **illustrative**.

## Sourcing pointers

`sourcing/freedom.md`: UHMWPE braided cord; INJORA servo winch ($22.98, 300 ratings); AS5600 magnetic encoder 3-pack ($7.99, 70 ratings); CALT draw-wire encoder ($118, 6 ratings: thin evidence and pricey against a home-made one); load cell with HX711.

## Scene

`freedom-03-cable-platform`.
