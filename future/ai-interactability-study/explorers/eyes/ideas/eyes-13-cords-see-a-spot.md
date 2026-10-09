# eyes-13 Cords see a spot (branch of room-06, combined with room-05's camera pair)

Scene: `scenes/eyes-13-cords-see-a-spot/`. Origin: exchange with room (wave 2). Maturity: developed. Numbers: `calc/cords-spot-cov.mjs`, `calc/cords-spot-grid.mjs` (the table in the scene), `calc/cords-spot-observer.mjs` (a nonlinear cross-check).

**Picture it.** The gun hangs on eight cords and software drives it to forty poses while a camera watches where the red dot lands. But the dot is not a bead floating in air. It is a small bright patch on the plate or the wall, the place a straight beam ends. Slide the whole gun six millimetres along its beam and the patch does not move at all, while the nozzle moves six millimetres. The scene shows that, and what it costs the calibration.

## The proposal

room-06's self-calibration fits 32 numbers (24 anchor offsets, 8 cord zeros) from where the dot lands and reaches 0.05 to 0.25 mm in simulation. Its observation is a 3-D dot position with 0.10 mm noise per axis. A camera cannot deliver that. It delivers where a beam meets a known surface, two numbers per pose, and the surface has to be somewhere known. This idea keeps room-06 whole and changes only the observation:

- **One board at plate height.** Two numbers per pose. The gun's position *along its beam* is invisible whatever the camera; sliding the gun along the beam leaves the observation unchanged.
- **A stepped board, or the tube's own corner (plate and wall).** Still the same: every surface cuts the beam somewhere, none says where the gun sits on it.
- **The spot plus one number that does depend on the position along the beam.** The nozzle tip's height over the rim, from a low side camera at 0.2 mm, or the nozzle tip in 3-D. That is the pair room-05 already draws (camera A on the dot, camera B on the nozzle).

## What carries loads, what establishes position, what is free or restrained

Not the subject: room-06's cords carry the shell, the winches set the pose. What establishes position *for the calibration* is the surface the spot lands on (its place in the cage frame is assumed known: a board on the rotator would give it, the tube's seat depth would not) and the nozzle-height camera on the table or a post.

## What software could command, observe, and what stays manual

- **Command:** room-06's eight winch lengths to a list of calibration poses.
- **Observe:** the spot on the surface (camera A), the nozzle tip's height over the rim (camera B). Not observed by A alone: where the gun is on its beam.
- **Manual:** placing and calibrating both cameras to the cage or the tube; registering the board or tube to the cage frame.

## What was tried to break it

1. **Assumed:** the observer reports where the dot is (room-06). **Found:** a spot is a line's end. Expected 1-sigma error of the dot after calibration (N = 40, 0.1 mm, linearised, mean of 4 draws): 3-D dot 0.043 / 0.036 / 0.036 mm (radial, tangent, vertical); one board 0.19 / 0.23 / 0.31; stepped board 0.18 / 0.23 / 0.29; tube corner 0.19 / 0.24 / 0.30. At 0.3 mm noise the board is 0.38 / 0.46 / 0.59.
2. **Checked against the actual nonlinear fit** (25 seeds, 40 poses): 0.10 mm rms for a 3-D dot, about 0.5 mm for one board (three of twenty runs did not converge). Same order as the linearised numbers (0.07 and 0.43 in 3-D once lug errors are added).
3. **Repair:** add camera B. Spot + nozzle height (0.2 mm): 0.057 / 0.051 / 0.054. Spot + nozzle in 3-D: 0.046 / 0.039 / 0.043. Back to room-06's number, with a spot instead of a point.
4. **A narrow stereo pair on a dot in air** (depth noise five times worse): radial 0.145. But a dot in air is not visible: it needs a surface, which is where this started.
5. **Poses that put the dot behind the wall.** In room-06's scene, 15 of 120 random poses in the ±25 × ±25 × ±15 mm range hide the dot from the cage-top camera behind the tube wall (the dot is inside the metal). The *spot* is still visible on the wall's face: a further reason to observe the spot, not the dot.
6. **The nozzle enters the plate.** A pose that lowers the dot 14 mm puts the nozzle in the plate (11 mm clearance at the opening pose, room-01 finding 6). The calc keeps only poses whose beam lands in front of the nozzle.

## Branches and combinations

Combines room-06 and room-05 (the A/B camera pair). Compare trials-03: the spot's size gives standoff, which is another along-the-beam observation, weaker than a nozzle-height camera. datum-11's witness pass on a scrap coupon could register the board. The 3-D observation in room-06's other transfer (room-03's ball) is the same problem: observe the spot, not the dot.

## Unresolved problems, questions for Derek

- Which surface does the calibration beam land on: the tube's own corner, a board on the rotator, a plane on the shelf?
- Where does the spot's centroid sit on stainless, and is it small enough to centre to 0.1 mm? (photograph the dot on the plate from 30 cm).
- The aim (beam direction) error is 0.10 to 0.15 degrees in every row: no observation type here improves it.
- room-07's roll-up row "Software-calibrated (room-06, room-03)" carries a calibration residual of 0.15 mm (illustrative); with a spot observer alone it is about 0.4 to 0.5 (nonlinear) or 0.2 to 0.3 (linearised per axis), with the nozzle-height camera about 0.06 to 0.1.

## Assumptions

room-06's: anchors 2 mm, cord zeros 1 mm, lugs 0.2 mm (1 sigma), pairing 6 0 1 4 5 7 2 3, poses ±25 × ±25 × ±15 mm and ±4 degrees **[illustrative, room]**. Spot noise 0.05 to 0.30 mm per in-surface axis; nozzle aux 0.2 mm **[illustrative]**. Linearised at the true parameters.

## Sourcing pointers

`sourcing/eyes.md`: the same cameras as wave 1 (Arducam OV9281, Logitech C920).

## Scene

`eyes-13-cords-see-a-spot`. Scene edits: gun slid along its beam, observation type, N, spot noise. Nothing is an actuator.
