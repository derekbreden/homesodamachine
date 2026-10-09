# borrowed-13-hexapod-pivot: six legs, a ring near the dot, the centre of rotation set in software

Origin: combination (wave 2; my own bought-positioner idea, drawn on freedom-02's arm as its carrier; from the thin region "multi-axis positioners with a software interface", reached through what laser and optics alignment already uses). Maturity: developed. Scene: `scenes/borrowed-13-hexapod-pivot/index.html`.

## Picture it

A ring, about the size of a saucer, hovers a hair above the tube's rim and clamps the printed shell near the nozzle. Six struts run up from the ring to a bigger ring held by an arm, three pairs, like the legs of a Stewart platform seen from below. The gun's body leaves the cage through the gap between two pairs, up and out over the bench. On the screen a small window says "pivot: the dot". Tilt the gun ten degrees about any axis and the dot does not move: the struts change by five millimetres each, and the corner stays under the red spot. Change the pivot to "platform centre" and the dot swings by four millimetres.

## The proposal

A hexapod moves a platform in six degrees with six struts whose lengths are set by software. The precision ones sold for optics, fibre and laser alignment let the user define the **centre of rotation as a coordinate**: tilt about a point in space with no shaft, ring or bearing there. That is the problem borrowed-01 and borrowed-04 spent their effort on (an axis through the dot cannot hold hardware because the dot is in a metal corner, and a bearing ring's axes have to meet at a point) and in a hexapod it is an inverse-kinematics parameter. The maker of the miniature hexapod H-811 quotes +-17 mm and +-21 degrees with the position and alignment of the reference frame and the centre of rotation definable in software [search: manufacturer pages]; LinuxCNC ships generic hexapod kinematics (genhexkins) [search: repository]. A small one built from six mini linear rails with motors (5 micrometres per full step on a T6x1 screw [derived], $54.80 each on Prime, two-day) and rod ends (M5, $9.99 for four) is a printing and assembly job of a week.

The arrangement drawn: the platform is a ring **about 18 mm above the dot** (12 mm above the 6.35 mm rim), so the pivot is near the platform and the legs need little stroke; a base ring 170 mm above the dot is held by a carrier (freedom-02's arm, a balancer, a gantry: the coarse position is someone else's job). Two leg types: variable-length struts (a Stewart platform), or fixed-length rods on six vertical rails, the way a delta 3D printer's arms hang from carriages (a hexaglide), so the six axes are six ordinary linear axes and the rods are the carbon rods with magnetic ball joints from a delta printer.

## What carries the loads, establishes position, is free, restrained or driven

- **Carries:** the six legs carry the gun through a clamp around the barrel and the fibre's pull; each leg is axial. The scene solves the six leg forces for the gun's weight and the pull: about 23 N at the largest, at the default, illustrative.
- **Establishes position:** the base ring and the leg lengths; the pivot point is a coordinate defined at the dot. The dot itself is unobserved by the legs.
- **Free:** nothing while the legs hold; the gun's other end is held by the same rigid body.
- **Driven:** all six degrees. One 6-D pose about a chosen pivot becomes six lengths.

## Software: command, observe, manual

- **Command:** a 6-D pose and a pivot; six leg lengths or carriage positions from closed-form inverse kinematics (the distance between the joint on the base and on the platform; for fixed rods the vertical position that keeps the rod's length). LinuxCNC's genhexkins does the general case; a Python script can stream six axes of G-code to any six-axis controller.
- **Observe:** leg step counts or encoders; nothing here sees the dot, so the pivot has to be calibrated to it (trials-13 pivot calibration with the dot on a board, guide-star calibration of borrowed-05 for the trims).
- **Manual:** placing the base ring near the corner, clamping the shell in the ring, routing the fibre and the wire out of the gap.

## What was tried to break it

1. **Does a software pivot avoid the axis problem?** Yes in the geometry: tilt 10 degrees about any axis about the dot and the exact dot offset stays 0.00 / 0.00 / 0.00 mm (corner inset) with the legs changing by up to 5.5 mm. Assumption: the pivot equals the true dot. It equals it to whatever the calibration gives; a 0.5 mm error in the pivot is a 0.5 mm x sin(angle) swing at every tilt, so the calibration is the whole accuracy of the idea. Left standing: how the pivot is calibrated and how it drifts.
2. **The stroke is the lever.** Rotating 10 degrees about the dot needs leg changes of about 5.5 mm with the ring 18 mm above the dot, 10 mm at 60 mm and 19 mm at 140 mm (the base ring kept 152 mm above the platform). About the platform's centre the legs move the same and the dot swings 3.7 mm (18 mm ring), 12 mm (60 mm) and 29 mm (140 mm). Change: put the platform plane near the dot. Left standing: the ring can be no lower than the rim plus the shell's own clearance.
3. **The gun's body has to leave the cage.** The housing rises at 45 degrees through the leg cage. With a gap between two leg pairs facing the tail the closest leg is 34 mm from the drawn housing axis; at 10 degrees of clock it is 29 mm, at 20 degrees 22 mm, at 40 degrees 2 mm (a leg pair beside the housing). Against an illustrative housing radius of 30 mm the gap has to face the tail within about 8 degrees. It worsens with the ring higher: at 80 mm the closest leg is 11 mm. Left standing: whether the printed shell, the fibre, the wire conduit and the gas hose all fit in one gap.
4. **Stiffness sits at the dot.** A 1 N push at the dot moves it 0.115 mm with the ring 6 mm above the dot, 0.097 mm at 18 mm, 0.09 mm at 30 to 45 mm, 0.11 at 60, 0.16 at 80, 0.23 at 100 and 0.45 at 140 mm, for six axial springs of 20 N/mm (`calc/w2-hex-sweep.mjs`). At 50 N/mm the push is 0.039 mm/N; at 10 N/mm 0.19. The fibre's pull along the exit axis gives 0.06 / 0.24 / 0.07 mm/N (radial / tangent / vertical) at 18 mm. For comparison freedom-01b's nose seat and bridle is 0.10 / 0.01 mm/N (radial / vertical) and a rigid-based stage 0.45 / 1.0 [freedom-11]. Assumption: the legs are ideal axial springs and the clamp and shell are rigid. The real leg stiffness (screw, coupling, joints) and the play of twelve ball joints (tens of micrometres each for cheap rod ends) are unmeasured and decide it.
5. **Fixed rods on rails.** Effective leg stiffness is the rail's divided by the square of the rod's vertical component, so at the same 20 N/mm the push at the dot is 0.072 mm/N against 0.097. The carriages are six ordinary linear axes; the rods and their magnetic ball joints are delta-printer stock. Left standing: magnetic joints are preloaded and can carry a limited pull.
6. **Resolution.** The largest dot displacement per millimetre of one leg is 0.94 mm at the default; at 0.31 micrometre per microstep (T6x1 screw at 1/16) that is 0.29 micrometre at the dot before backlash. Backlash and joint play are the limit, not the step.

## Branches and combinations

- **With freedom-02 (drawn: the scene's balanced-arm carrier and its payload row):** the arm carries the base ring; six rails and motors weigh about 1.8 kg (0.3 kg each, illustrative; the listing states no weight), so gun, legs and rings come to 3.2 kg, inside the rated range of the 2 to 7 kg and 2 to 9 kg monitor arms and above the 3 kg of the Elgato gas-spring mic arm. That is what a monitor arm's 2 kg floor wants. The arm supplies coarse position and orientation by friction; the hexapod trims all six freedoms about the dot. In freedom-02 the vernier is two axes.
- **With freedom-01b:** the nose seat and this ring are the same "pivot near the dot" logic. The seat is unilateral (the fibre pulls it out at 6.7 N) and cheap; the ring is bilateral and costs a cage.
- **With trials-13 (pivot calibration) and trials-19:** the pivot and the leg offsets are calibratable from a dot on a board.
- **With borrowed-05 (guide star):** the six legs' nudge-and-watch calibration is a 6-column version of the 2 x 2 matrix.
- **With freedom-04:** the tangent slide with a yaw at no radial cost is one commanded pose.
- **Versus borrowed-01 (ring pivots):** three bearing rings whose axes must meet within a fraction of a millimetre are replaced by a coordinate.

## Unresolved problems and questions that need Derek

- Play in the ball joints and the backlash of the legs (measure a printed prototype with the dial indicator: push the platform with the Newton meter and read the give and any lost motion).
- Whether a ring of 50 mm radius fits around the shell near the nozzle beside the wire guide, the beam and the tube rim. A sectioned printed shell (Derek prints and scans shells) settles it in an afternoon.
- How the pivot is found on the real gun: does the dot coincide with the modelled point (Derek's question: does the red dot sit on the melt at working standoff)?
- Which range is needed: the hole, roll and yaw ranges a skilled hand uses are not recorded anywhere in the study.

## Assumptions

- Illustrative geometry: base ring radius 130 mm at 170 mm above the dot, platform ring radius 50 mm at 18 mm above the dot, joint pairs 30 degrees apart, stroke +-40 mm, leg stiffness 20 N/mm, housing radius 30 mm, gun 1.2 kg with the kit's proxy COM. The kit gun is not measured. Legs have ball joints at both ends with no play and no friction.
- Product facts: PI H-811 (+-17 mm, +-21 degrees, software pivot) from manufacturer pages via search; LinuxCNC genhexkins from its repository, via search; both unchecked against the pages. Prices from Prime listings observed 2026-09-29 (sourcing/borrowed.md).

## Sourcing pointers

sourcing/borrowed.md wave 2: 100 mm mini linear rail with T6x1 screw and NEMA 11 ($54.80, Prime, two-day, 34 ratings), M5 rod ends ($9.99 for four, search card), linear actuators (search card), delta-printer parts and printers (Ender-3 V3 SE, $219, 2,153 ratings). No Prime hexapod was found.

## Scene

`borrowed-13-hexapod-pivot`
