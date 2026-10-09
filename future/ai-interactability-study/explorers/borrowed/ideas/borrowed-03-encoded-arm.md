# borrowed-03-encoded-arm: the operator moves, software watches and coaches

Origin: swarm. Maturity: worked deeply. Scene: `scenes/borrowed-03-encoded-arm/index.html`. Numbers: `calc/encoder_error.py`.

## Picture it

A spring-balanced articulated arm of the kind that holds a monitor or a lamp is clamped to the bench edge with the gun on its wrist. Every joint has a small magnetic angle sensor. The operator welds exactly as today, hand on the grip, but the arm takes the weight, and a screen or a tone tells them where the dot is and which way to move. Nothing is driven: software only reads angles, computes the gun's pose and speaks.

## The proposal

Take a mass-produced balanced arm (gas-spring monitor arms sell in the thousands per month on Prime, sourcing/borrowed.md), add an encoder per joint, and it becomes a hand-guided measuring arm, the same idea as a portable coordinate-measuring arm. The value is not that it moves the gun; it is that it gives software the gun's pose during a weld done by a skilled hand. That gives a live coach, a record of every pose a good weld used (the missing specification of the travel every other arrangement needs), and a check on how accurately any of the arrangements is placed. Motorising the joints later (brakes, small trim motors) is a ladder from the same arm.

## What carries the loads, what establishes position, what is free, restrained, driven

- Load path: gun, wrist, forearm, upper arm, shoulder post, bench clamp; a spring balances the arm.
- Position: joint angles through forward kinematics, zeroed by touching the nozzle to known datums (the welder's work-contact circuit, which the manual says the laser needs complete, is the proposed contact sensor, [manual p. 19]; never tried as a probe).
- Free: everything the hand moves. Restrained: the arm's joint limits and reach (the scene holds the last valid pose with a LIMIT badge). Driven: nothing.

## Software: command, observe, manual

- Could command: nothing. Display and logging only.
- Could observe: six joint angles; the pose and dot estimate through forward kinematics; the coach line ("move the dot 0.8 mm toward the tube axis and 1.3 mm down"); the poses over a weld.
- Stays manual: moving the gun; zeroing by touch-off; matching the spring to the gun's mass; anything the encoders cannot see (joint play, umbilical drag).

## What was tried to break it

1. **Can it know where the dot is?** Conflict: the dot is 300 to 700 mm of arm from the joints, so each joint's angle error is multiplied by 0.4 to 0.5 m for the base and shoulder joints (calc/encoder_error.py: about 0.85 mm per 0.1 degree per major joint; 2.8 mm per 0.1 degree if all errors add, 1.45 RSS). Assumption: resolution is accuracy. Change: none; the scene separates quantisation (12 bit: 0.31 mm; 8 bit: 7.5 mm), linearity error (0.2 degree: 3.1 mm) and zero offset (0.3 degree: 3.3 mm, 0.6 mm after a touch-off that removes 90 %). The AS5600 datasheet gives 12 bit and a system INL of +-1 degree maximum: at 1 degree this arm's estimate is about 15 mm off. Left standing: an $8 magnetic encoder makes a coarse pose logger, not a fine aligner, unless its per-turn error is mapped by a calibration nobody has designed.
2. **The zero.** Conflict: six unknown zero offsets after assembly, each a fraction of a degree. Change: touch-off calibration at datums (rim, rotator) and a solve for the offsets; it cannot remove linearity error. Uncertain: whether the interlock circuit works as a probe at all.
3. **Balance.** Conflict: a spring balances one mass; the top-selling gas-spring arm on Prime is rated 4.4 to 19.8 lb (2 to 9 kg), and a light gun sits below it. A different mass, or an umbilical pulling, leaves a residual force the hand feels as drift. Change: a lighter spring (lamp or balancer class) or ballast; the mass and rating sliders show the residual. Left standing: the gun's mass is unknown.
4. **A coach is not a controller.** Following the instruction leaves the estimate error, not zero (the readout says so). Left standing: whether a human can hold 0.3 mm from a display without looking away from the weld.
5. **Deflection.** Encoders read the joint, not the load path beyond it; play in a cheap arm's joints is invisible. Not modelled.

## Branches and combinations

- Ladder (not drawn): passive arm with encoders; add brakes to lock joints; add small trim motors at the wrist.
- Feeds every other arrangement: recorded poses set the hole, roll and yaw ranges for borrowed-01 and borrowed-02.
- Combines with borrowed-05-guide-star (calibrate the arm against a camera) and the datum explorer's touch-off scene (by name only; not read) for the zeroing here.

## Unresolved problems and questions that need Derek

- Whether an arm of this class carries a 1 to 2 kg gun and an umbilical without creep or play.
- Encoder choice: absolute optical or magnetic with a mapped error, wiring through joints.
- Questions for Derek: does he hold the gun freely today, or rest it on anything; what he would accept as a coach (light, tone, screen); the gun's mass.

## Assumptions

- Six-joint arm with a spherical wrist, post 260 mm, links 260 + 260 mm, wrist centre at local (0, 0, 150) of the gun proxy: illustrative. The Python twin reproduces the scene's numbers (12 bit, 0.2 degree INL: 3.07 mm; 0.3 degree offset: 3.29 mm; touch-off: 0.60 mm).
- Encoder error model: rounding, a per-turn sine, a fixed offset; not a specification of a part. Datasheet: AS5600 v1-06 (Seeed-hosted copy), 12 bit, INL +-1 degree max, RMS output noise 0.015 to 0.043 degrees.
- Gun mass, joint friction, joint play: [unknown].

## Sourcing pointers

sourcing/borrowed.md: HUANUO single monitor arm ($35.99, 16,507 ratings, 4K+ bought, rated 4.4 to 19.8 lb); AS5600 modules ($7.99 for three); the AS5600 datasheet numbers.

## Scene

`borrowed-03-encoded-arm`

## Wave 2

- **The payload of the arm is everything on the tip, and the arm forgives about 90 g** (`borrowed-14-arm-mass-window`): the mass sliders of the scene here start at 0.5 kg because the gas-spring monitor arm's floor is 2 kg; counted from parts (gun, an encoder board, a camera, the fibre's share) the total is what decides the arm class, and a mic boom (0.25 to 1.5 kg, $20 to $112, next-day) or a gas-spring mic arm to 3 kg brackets a lighter total.
- A collaborative arm's hand-guiding mode (gravity compensation, joint encoders, a force sensor) is this idea in one product; the one that states its numbers is a maker product (Fairino FR3: 3 kg, +-0.02 mm, $6,799): `borrowed-17`.
