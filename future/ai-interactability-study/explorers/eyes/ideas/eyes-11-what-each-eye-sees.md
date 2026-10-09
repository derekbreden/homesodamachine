# eyes-11 What each eye sees (and: blind but listening)

Scene: `scenes/eyes-11-what-each-eye-sees/` (developed). Origin: swarm (eyes framing). Maturity: developed as bookkeeping; the IMU-and-microphone arrangement inside it is a sketch.

**Picture it.** The reference gun with its three rotation axes and three position arrows at the dot, over a table of nine sensors against six coordinates. Switch a sensor on and its cells light: filled teal where it sees a coordinate directly in its own frame against the seam, half-amber where it only infers it through a chain of calibrated transforms, thin amber where it sees it only under conditions. The arrows and axes on the gun take the colour of the best available source; red means nothing that is switched on sees it.

## The proposal

Two things in one. **(1) A bookkeeping view** of the whole problem from the observation side: the gun in the tube frame has six coordinates (radial, along-seam and vertical position of the dot; grip-axis roll, hole-axis roll, vertical-axis turn from the reference scene). Each proposed or existing sensor covers some of them, directly or by inference. Choosing a sensor set is choosing which cells are still red. **(2) An arrangement that observes and moves nothing:** an IMU on the gun and one on the rotator base (differential tilt against gravity), a contact microphone on the tube or gun, and the rotator's own step count. Software watches; a person aims. It gives two of the three rotations and the along-seam position, plus process events, and no radial or vertical position at all.

## What carries loads, what establishes position, what is free or restrained

Not addressed in the table. The blind-but-listening arrangement adds nothing that carries load: two small boards, one on the shell, one on the rotator base, and a piezo pad. Gravity establishes tilt; the rotator's counter establishes along-seam position.

## What software could command, observe, and what stays manual

- **Observe (table):** for each of six coordinates, direct / inferred / partial / nothing under the chosen set. **Command:** nothing. **Manual:** whatever the chosen set leaves red, and what it leaves amber.
- **Blind-but-listening:** observes gun tilt (differential IMU), whether the wobble motor is running (vibration spectrum on the gun IMU: the head "contains a vibration motor", **[manual]** p.20), tube noise during a bead, the rotator angle. Commands nothing.

## What was tried to break it

1. **Expected: some coordinate is unreachable by any of nine sensors.** Found: the vertical-axis turn has no direct source apart from a gun-borne camera that sees the corner over a stretch (partly) or tags (inferred through a chain). Gravity cannot see it (it is rotation about the vertical), touch does not, pads do not. Magnetometer heading near a NEMA 23 motor and a steel bench is **[unknown]** and likely poor.
2. **Along-seam position.** The least demanding: the rotator already counts degrees (14,400 pulses per turn, 0.027 mm at the bead, **[repo]**). It matters for tacks and the start, not for where the seam is: on a circle an offset s along the seam moves the joint radially by s^2/(2r) (0.008 mm at 1 mm, **[derived]** in shared context).
3. **The two tilts from gravity.** An IMU gives tilt against gravity (differential to a base IMU removes the bench's tilt) for two horizontal axes. But grip-axis roll and hole-axis roll are separable from those two numbers only if the vertical-axis turn is known, since they mix with it; the table marks them "inferred" for that reason. What this changes: pair the IMU with anything that sees the turn (a camera or tags): a complementarity: gravity sees what a top-down camera sees badly, and vice versa.
4. **"Direct" is not "accurate".** The table cannot say that a direct reading is better than an inferred one. Accuracy lives in other scenes (calc/marker-error.mjs, calc/proximity-model.mjs, calc/dot-probe.mjs).
5. **The wobble motor.** A vibration motor in the head means the accelerometer sees a steady vibration when the wobble is on; useful as an "is the head wobbling" flag, harmful to tilt accuracy unless filtered. Uncertain.
6. **Sound.** A piezo pad on the tube may hear the keyhole, spatter or a wire stub as changes in the noise; whether the laser's own fan, the stepper and the extractor drown it is unchecked. It gives events, not position.

## Branches and combinations

- `eyes-11b-umbilical-eyes`: the umbilical's state (twist, bend radius) as a seventh, orthogonal observation.
- The table is the map on which the combination candidates sit: gun-borne eye (r, z direct) + IMU (two tilts) + rotator (along seam) leaves only the vertical-axis turn partly seen; add the tags cube and it becomes inferred.
- The "blind" cells are where `eyes-05-touch-off-interlock` and `eyes-07-sectioned-tube` earn their keep (discrete registration, ground truth).
- Wave 3: the gun-borne row's turns were entered as one partial; `calc/line-laser-pose.mjs` says what they are: one fan reads two of the three combinations of the turns (about 0.15° and 0.8°, 0.3 px noise, illustrative) and one is blind, whichever fan roll; a gravity sensor (this row's IMU) or a crossed second fan closes it. Freedom named the combination of the IMU with the seat's tail loop (freedom-01b); adopted, not drawn (the IMU is a row here, the tail loop is freedom's scene). Also tagged a lens.

## Unresolved problems, questions for Derek

Cell entries are my reading of each sensor's geometry, not measurements. Several are conditional (the corner visible, the dot on stainless, the cube in view). **Question for Derek:** during a normal bead, do you feel the wobble motor through the grip? Roughly what frequency does it sound like?

## Assumptions

Coordinates and rotations follow the reference scene (weld-position.md) **[repo]**. Rotator resolution **[repo]** weld-rotation-rig.md. The vibration motor **[manual]** p.20. Each cell's status and note is an illustrative judgement (hover a cell in the scene for the reason).

## Sourcing pointers

`sourcing/eyes.md`: HiLetgo 3 pcs GY-521 MPU-6050 ($11.79, Prime, 800 reviews, "600+ bought in past month", "#1 in Acceleration Sensors" on the page); BNO085 module ($20.49, Prime, 24 reviews, "100+ bought"); piezo contact microphone pickups ($13.99, Prime search card, 959 reviews, "50+ bought").

## Scene

`eyes-11-what-each-eye-sees` (3D gun with coverage-coloured axes and arrows, plus the table). Scene edits: which sensors are on, the three rotation dials. Nothing is an actuator.
