# eyes-14 The wall as a window (branch of room-03)

Scene: `scenes/eyes-14-wall-as-window/`. Origin: exchange with room (wave 2). Maturity: developed. Numbers: `calc/wall-window.mjs` (the scene's beam model).

**Picture it.** room-03's cabinet has the gun inside and a long tail outside. Draw the rod along its own axis, the room on the left, the cabinet on the right, the sideways direction stretched forty times. The rod is not straight: it sags on both sides of the ball. Step counts believe it is straight. Two small scales on the clean side of the lid read where it really is, and a load cell at the tail reads the one number that says how much it bends.

## The proposal

Two observations about room-03 that its note does not make.

1. **The wall is a window as well as a fulcrum.** The outside end of the rod is in room air, with no spatter, fume or plume: scales, a load cell or an inclinometer can live there. Two scales on the lid frame read the rod's sideways position at two stations and see the ball's play, which step counts cannot.
2. **The rod bends, and that, not the ball's play, is the large term for a thin rod.** One bending moment F d passes through the ball (1.5 kg at 400 mm, 45 degrees, plus a 2 N cable tug: about 5 N m) and bends the inside segment and the tail. The counterweight balances the actuators, not the rod.

## What carries loads, what establishes position, what is free or restrained

As in room-03: ball and lid carry the gun through the rod; the counterweight balances gravity about the ball; the actuators hold the tail point at its commanded place. New here: scales on the lid frame (locate the rod's sideways position), a load cell at the tail actuators (reads the moment), and the rod treated as a beam.

## What software could command, observe, and what stays manual

- **Command:** unchanged (plate slide, insertion, tail pitch and yaw).
- **Observe:** rod position at two stations outside (scales); tail force (load cell or motor current); dot against the seam (camera inside, blind when the plume is on).
- **Manual:** fitting the scales to the lid frame; measuring the rod's stiffness once with a direct look at two tilts; the ball's clearance.

## What was tried to break it

1. **Assumed (room-03 note 4):** with the counterweight the actuators carry nothing and the rod is a stiff line. **Found (aluminium tube, wall 2 mm, illustrative loads):** Ø12: dot 14 mm off the commanded line; Ø16: 5.2; Ø20: 2.4 (tail droop 3.3 mm, inside flex 0.83 mm); Ø25: 1.1; Ø30: 0.59; Ø40: 0.19; Ø50: 0.06. Bending stiffness goes as the fourth power of the diameter. The ball's play is 0.05 mm at the ball and 0.075 at the dot.
2. **Straight-line extrapolation of two scales.** For a thin rod it is no better than step counts (2.44 against 2.41 mm at Ø20; 0.26 against 0.19 at Ø40) because the tail droops one way and the inside another amount.
3. **Repair: read the moment.** The tail force gives F d; a beam model with that load subtracts the bend at both stations and at the dot. At Ø20, 0.13 mm (0.05 noise); at Ø40, 0.04. A 20 % error in EI gives 0.41 mm at Ø20, so EI wants one direct look at two tilts.
4. **A mitigating view.** The thin-rod error is large but nearly constant with pose: gravity across the rod changes 5 % over ±3 degrees of trim (about 0.10 mm at Ø20), and a ±1 N change of cable pull moves it about ±0.19 mm. A one-time direct look absorbs the constant part (this is room-06's calibration idea applied to room-03). What stays is the cable's tug.
5. **Only the camera knows the seam.** The scales say where the gun is in the cabinet, not where the tube is.

## Branches and combinations

- room-03 + eyes-11: an inclinometer or IMU at the tail gives the tilt at a dollar-class price (already in sourcing).
- room-03 + room-06's self-calibration: fit the constant part of the flex and the ball's centre together from looks at many poses.
- The idea that the outside of a wall is the place for the exposed part of a sensor transfers to room-05's cabinet and to any enclosure.

## Unresolved problems, questions for Derek

- What does the tail actuator hold: the tail *point* at Lt, or the rod's tangent at the ball (a rigid tail)? The model assumes the point.
- The real gun is a rigid body 270 mm long on the rod end; the cable pulls at the grip; the rod ends are clamps. The scene treats the load as at the dot end.
- Whether the plume blinds the inside camera during the bead, and whether the red dot stays on while emitting: **[unknown]**.
- Scale output: the cheap LCD scales found have no data port listed (`sourcing/eyes.md`).

## Assumptions

Rod: aluminium tube, wall 2 mm, E 69 GPa, Ø as a slider **[illustrative]**. Mass 1.5 kg, pull 2 N, angle 45 degrees, play 0.05 mm, d 400 mm, Lt 800 mm: room-03's numbers **[illustrative, room]**. Scale noise 0.01 mm, load-cell noise 0.1 N, EI error 5 %, camera noise 0.08 mm **[illustrative]**.

## Sourcing pointers

`sourcing/eyes.md` wave 2: digital LCD linear scale 150 mm (0.01 mm resolution, plus or minus 0.06 mm accuracy, no data output listed); load cell + HX711; 1-1/2 in aluminium tube.

## Scene

`eyes-14-wall-as-window`. Scene edits: rod diameter, geometry, loads, play, station positions, noise. State: the plume switch. View: sideways exaggeration.
