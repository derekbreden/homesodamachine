# trials-18-steerable-mule: a dot with known offsets

Scene: `scenes/trials-18-steerable-mule/index.html` (developed). Origin: combination of `trials-06-mule-gun`, `trials-03-dot-touch-probe` and `borrowed-06-swing-offset`, from borrowed's sketch `borrowed-10-gun-free-dot` (exchange: `exchange/trials--on--borrowed-w2.md`, section 3). Sourcing: `sourcing/trials.md`, wave 2 additions.

## Picture it

The mule stands in the printed shell where the gun would be. Inside its nose sits a tiny steerable pointer: a hobby pan/tilt with a red diode behind the dot, or a small mirror at the nose, or (on the real gun) the head's own swing offset. The AI commands one number and the red dot slides across the recessed corner: on the plate, then across the seam and up the wall. Nothing else in the station moves. Overhead, camera A watches the plate part of the dot vanish at the seam, and from that the software knows which command puts the dot's centre exactly on the corner. Every later command is a labelled offset: 1.0 mm short, 0.5 mm short, on the corner.

## The proposal

Take the sketch `borrowed-10` (a pan/tilt pointer standing in for the gun so the vision chain can run dry) and put the pointer in the mule. Its value then is not only that it runs all night with no gun; it is the only thing in the station that puts a dot at a chosen place on the corner with no arrangement moving and no mass. Three ways to steer, all drawn in the section-plane scene:

- **Pan/tilt 100 mm behind the dot** (borrowed-10 as drawn): 2.07 mm of dot per degree, 0.21 mm per 0.1 degree step, reach minus 16 to plus 4 mm (about 8 degrees each way), and only 0.6 per cent scale change for 0.5 mm of shell height.
- **Mirror at the nose, 16 mm from the dot**: the beam turns twice the mirror, 0.68 mm per degree of mirror tilt, 0.068 mm per 0.1 degree step, reach minus 5.6 to plus 5.9 mm, 3.7 per cent scale change for 0.5 mm of shell height.
- **The gun's own swing offset** (`borrowed-06`): a parallel shift of the beam; slope 1.83 mm per mm and range unknown (sliders). The mule rehearses the interface before Derek learns whether the head accepts a commanded shift.

The routine: a coarse sweep of the whole reach (41 samples), then a fine sweep through the transition (31 samples), a line through the points where the visible fraction is between 6 and 94 per cent, and the knee where it crosses 50 per cent. That is the seam in the pointer's own units. Labels are then written from the step the software commanded, not from where the servo landed.

Uses (all laser-off, unattended): thousands of labelled frames to train and score the judge (about 1200 an hour at 3 s a label); the camera-to-gun-frame transform, because the pointer's axes are in the shell's frame (borrowed-05's nudge-and-watch gives the 2x2 without moving the arrangement); a golden dot for camera drift (the same command repeated every ten minutes) and, stepped or blinked, latency; and a bench for any fine-axis loop (`borrowed-05`, `borrowed-06`, `trials-20`).

## What carries the loads, what establishes position, what stays free

- The shell carries the mule; whatever holds the shell is the arrangement under test, or nothing (the shell can stand on the rotator). The pointer is fixed in the shell; only its beam moves.
- Position: the corner. The seam is found by the knee of the visible fraction, in pointer units; the mm scale comes from the pivot geometry (height above the plate), or from the wall thickness in the image.
- Free: the tangent direction (the out-of-plane axis is not drawn). Restrained: nothing.

## What software could command, observe, and what stays manual

- Command: the pointer angle (or mirror tilt, or swing offset); the dot on, off or blinked (mule only; whether the gun's own dot can be blinked is unknown); start a sweep; steer to a labelled offset.
- Observe: the visible fraction and centroid of the plate part of the dot in camera A; the knee. Blind: the wall spot (edge-on to A; camera B sees it), the melt position.
- Manual: standing the shell so the seam is inside the reach, mounting the pointer or mirror, deciding whether an unattended red laser is acceptable.

## Tried to break it

1. **Resolution against reach.** Conflict: borrowed-10 states the resolution at 100 mm (0.1 degree is 0.17 mm); in the mule's geometry (beam 32 degrees to the plate, dot 16 mm ahead) the pan/tilt gives 0.21 mm per 0.1 degree and a 0.05 mm label needs 0.025 degrees. Assumption: the pivot sits where the pointer sits. Change: a nose mirror moves the pivot to 16 mm (0.068 mm per step) at the cost of reach (plus or minus 5.7 mm against minus 16 to plus 4). Leaves: whether a mirror fits in the nose, which tapers to 2.2 mm radius at the tip **[illustrative kit proxy]**.
2. **The sweep is coarser than the knee.** Conflict found in the scene: a 61-point sweep over plus or minus 8 degrees has 0.27 degree (0.55 mm) between points, about the width of the dot's footprint (0.59 mm), so the first version's knee was 0.3 mm off. Change: coarse then fine. Leaves: the sweep time (about 70 samples).
3. **Servo lash.** Conflict: the knee is found upward; the achieved angle lags the command by half the lash (0.1 degree = 0.21 mm at the far pivot). Assumption: the servo lands where told. Change: label from the commanded step, approach labels from the sweep's side, and the lag cancels (labels within 0.02 to 0.03 mm); from the other side it does not (the scene's radio). This is the unidirectional final approach of `trials-02`. Leaves: real hobby servo lash and drift are not measured.
4. **Sensitivity to how the shell stands.** Conflict: the mm scale needs the pivot's height above the plate; an unknown 0.5 mm of shell height changes the scale 0.6 per cent (far pivot) or 3.7 per cent (near mirror), so a 1.5 mm label is off 0.01 or 0.055 mm. Change: none needed for the far pivot; for the mirror, measure the scale once from the fraction curve's own width (the dot's footprint, if known) or from the wall thickness in the image. Leaves: neither is drawn.
5. **It is not the gun's dot.** Conflict: 5 mW modules are 17 times brighter than 0.3 mW **[manual p.12]**, size and finish response differ. Change: a class 2, under 1 mW module (Prime, $15.99, 79 ratings) or a filter; the test is of the camera chain, not the gun. Leaves: eye safety of an unattended pointer, Derek's call.
6. **Where the melt is.** Nothing in a dry run relates any red dot to where an infrared beam melts; the dot finds the seam. Leaves: `datum-11` (a witness pass on a scrap coupon).

## Branches and combinations

- Combines `trials-06-mule-gun` (the shell and the dummy), `trials-03-dot-touch-probe` (the knee), `borrowed-06-swing-offset` (the third type), `borrowed-05-guide-star` (nudge and watch; `trials-20` fixes its target).
- Feeds `trials-17-trial-card` (a golden dot per session), `trials-05` (the corner coupon and the notch tube check the knee), `eyes-12-dot-lattice` (a lattice of offsets at zero mass: the pointer *is* the positioner).
- Borrowed for this idea: `eyes-06b-corner-mirror`'s merge of two spots is a second null criterion for the knee (dot and its plate reflection meet when the dot is on the corner); `datum-04-corner-follower`'s ball is an independent touch truth on the real tube.

## Unresolved, and questions for Derek

- Q (nozzle scan): how thin can the printed nose be at the tip? Whether a mirror of a few millimetres fits decides between the two servo types.
- Q: can the gun's red light alone be lit and blinked (RS232 or the DB25 port, or a panel setting)? If yes the gun's own dot can be used for fixed-dot work; a moving dot still needs the swing offset (borrowed-06).
- Q: are you comfortable with an unattended class 2 red pointer running near the bench?
- Servo lash and drift over hours; stepper versus hobby servo.

## Assumptions

Recess 6.35 mm and wall 1.65 mm **[repo]**; beam 32 degrees from vertical in the section plane, 16 mm nozzle-to-dot, 0.5 mm spot, camera fraction noise 0.02, servo step 0.1 degrees, lash 0.2 degrees, swing-offset slope and range **[illustrative]**; the out-of-plane axis is not drawn; camera A sees only the plate part of the dot.

## Sourcing pointers

`sourcing/trials.md`, wave 2: pan/tilt kits and MG90S/SG90 servos (Prime, high volume), 28BYJ-48 steppers (831 ratings, 400+ a month), a class 2 red module ($15.99), a galvo set (thin).

## Scene

`trials-18-steerable-mule`
