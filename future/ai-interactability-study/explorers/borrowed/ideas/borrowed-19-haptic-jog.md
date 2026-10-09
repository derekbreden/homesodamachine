# borrowed-19-haptic-jog: the hand supplies the motion, software supplies the feel

Origin: combination (wave 2; my own idea in the thin region "the hand supplying motion while software supplies resistance or guidance (a virtual wall, a brake, a detent)", combining freedom-14 and borrowed-09; the exchange section 5 leads to it). Maturity: developed (a scene with a torque model; nothing measured). Scene: `scenes/borrowed-19-haptic-jog/index.html`.

## Picture it

A knob the size of a coffee-jar lid on a small brushless motor, wired to a laptop. Turn it and a fine axis moves a millimetre per turn. Every hundredth of a millimetre, or every twentieth, it clicks, and the clicks are a program: you can count them blind. Turn it toward the tube wall and, a third of a millimetre past where the camera says the seam is, it pushes back, gently at first, then hard, and you can still turn it through if you mean to. Let go and it leans, very slightly, toward the seam. The gun never moved by itself and nothing pushed on it.

## The proposal

freedom-14 puts a soft force on the gun (a bungee moved by a motor) so that a hand is helped; every other arrangement gives software a position. A third way leaves the gun and the hand alone and changes what the *handle* feels like. A brushless gimbal motor with a magnetic encoder, run with field-oriented control, is a knob whose torque is a function of angle and speed: detents at any spacing, walls (software end stops), a spring, a damper. The open-source SmartKnob (software-defined endstops and virtual detents, a BLDC gimbal motor with a hollow shaft and a magnetic encoder) and the haptic examples of SimpleFOC do this [search: the projects' pages, unchecked]. The parts are the ones found in wave 1 for borrowed-01: a 2804 hollow-shaft gimbal motor kit with an AS5600 encoder and a SimpleFOC driver, $34.88 on Prime (16 ratings, "50+ bought"; a $24.99 and a $39.89 alternative on the same search). The knob jogs the fine axis (the radial trim of the dot): stage position = knob angle x ratio, or, in the leader-follower reading of borrowed-09, the knob follows the stage when software moves it and the hand feels the correction.

## What carries the loads, establishes position, is free, restrained or driven

- Carried: the knob carries only the hand's torque; a stage carries the gun (freedom-05's vernier, freedom-01b's nose stage, a hexapod leg).
- Position: knob angle x ratio; the seam is the eye's estimate, with its bias.
- Free: the hand.
- Restrained: by the detent, wall and guide torques, clipped at the motor's limit.
- Driven: the stage by the hand through software; the knob by its own motor.

## Software: command, observe, manual

- Command: motor torque at kilohertz from the encoder angle and speed: detent + wall + guide + damper + cogging compensation; the stage position.
- Observe: knob angle and speed (12-bit encoder, 0.088 deg, 0.24 micrometre of stage per count at 1 mm/turn). The dot is the eye's job.
- Manual: turning the knob; deciding what the wall and the guide are for.

## What was tried to break it

1. **The wall is advice, not a stop.** Clipped at the motor's limit (60 mN.m, illustrative) a wall can be pushed through by a hand, which is the property freedom-14 wanted. It also protects nothing: the stage's own end stops and software limits do.
2. **The pull toward the seam carries the eye's bias.** Set the eye 0.2 mm off and the soft spring leans the hand toward the wrong place (freedom-14 entry 3). Difference: on the knob it is felt, can be turned off, and the gun never moved by itself.
3. **Detents must beat cogging.** Hobby gimbal motors cog moderately to severely (the SmartKnob project says nearly every tested off-the-shelf motor does), a periodic torque that a smooth-rotation mode cannot hide and that the detents must exceed. The scene's cogging slider (84 cycles per turn for a 12N14P motor) makes the point; software can measure and cancel it in a calibration turn.
4. **Resolution is not the limit; the ratio is the gear between a shaky hand and the dot.** 0.24 micrometre per count at 1 mm/turn; a hand's control of about a degree is 2.8 micrometres; a 10 degree tremor is 28 micrometres at 1 mm/turn and 6 at 0.2 mm/turn.
5. **The loop through the hand is still there.** A hand on a knob watches the dot on a screen with the delay of the eye (freedom-14 entry 2). Feel can help the hand count and stop; it cannot supply what the eye does not see.

## Branches and combinations

- With freedom-14: the same three helps (wall, centring, damper) on the handle instead of the gun.
- With borrowed-09: the hand controller gains a rendered feel; a SpaceMouse puck ($171, 1,044 ratings) is the other 6-DoF controller.
- With trials-10 (human-labelled jog): the clicks are a countable, repeatable increment for Derek's "a bit more" taps.
- With borrowed-13: one knob per axis of a hexapod is six haptic knobs; more likely one knob with a mode switch.

## Unresolved problems and questions that need Derek

- The torque a bought gimbal motor can render and its cogging: not on any listing read [unknown]. A printed knob on a $35 kit answers it.
- Whether a hand jogging with feel beats the hand on the gun (freedom-14) or a plain handwheel with a digital scale (borrowed-08): nobody has tried. An afternoon.
- Does Derek prefer a knob to a puck to a joystick, for the fine axis?

## Assumptions

- Illustrative: 12-bit encoder, ratio 1 mm/turn, detents 0.05 mm at 12 mN.m, wall 0.30 mm past the eye's seam and a retract wall at -4 mm, guide 6 mN.m/mm capped at 10 mN.m, damping 2 mN.m.s/rad, cogging 4 mN.m at 84 cycles per turn, torque limit 60 mN.m. The torque model is detent = A sin(2 pi x/d), springs for wall and guide, c omega, cogging, all clipped; no motor dynamics, no hand.
- Hardware facts: the 2804 hollow-shaft kit is a Prime listing observed 2026-09-28 (sourcing/borrowed.md wave 1); the SmartKnob and SimpleFOC facts are from search summaries: unchecked.

## Sourcing pointers

sourcing/borrowed.md: 2804 hollow-shaft gimbal motor kit with AS5600 and SimpleFOC driver (Prime, $34.88, wave 1); SpaceMouse Compact (Prime, $171, wave 1). Wave 2 records the SmartKnob and SimpleFOC references as search results.

## Scene

`borrowed-19-haptic-jog`
