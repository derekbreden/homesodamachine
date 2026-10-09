# borrowed-10-gun-free-dot: a $15 laser pointer on a pan/tilt stands in for the gun

Origin: swarm (a silly one, taken to its useful form). Maturity: sketch (no scene, nothing sourced).

## Picture it

A hobby pan/tilt bracket with two small servos and a red laser-diode pointer, of the kind sold as a cat toy, mounted where the gun's nozzle would be. Software points it at the corner by commanding two angles, and a camera looks at the red spot. No gun, no interlock, no laser emission, no argon, no runout unless the rotator is turned on. The whole seeing-and-calibrating chain can run all night.

## The proposal

Separate the vision and calibration work from the weld hardware. A pointer at a known position and angles can put a known red spot at a chosen place on the seam: for training and testing a centroid finder, for calibrating the camera's pixels to millimetres (with the wall thickness as a scale bar), for rehearsing borrowed-05's nudge-and-watch loop with real optics and real fume-free lighting, and for a dry-run AI experiment. Its own accuracy does not have to be high; it only has to be repeatable and known, and its angle resolution at 100 mm sets the smallest spot move (a 0.1 degree servo step is 0.17 mm at 100 mm [derived]).

## What carries loads, establishes position, is free, restrained, driven

- A printed shell mounts the pointer at the gun's nozzle position; the pan/tilt is driven by two hobby servos (or a stepper pair); position is by the servos' angles and the geometry, not measured. Nothing carries a gun.

## Software: command, observe, manual

- Could command: pan and tilt angles, rotator speed. Could observe: the camera image. Manual: mounting the pointer at the reference position; aiming it at the seam once.

## What was tried to break it

1. **It is not the gun's dot.** The gun's red dot has its own optics and brightness (0.3 mW, 630 to 670 nm [manual p. 12]), and its relation to the melt position at working standoff is unknown [manual pp. 25, 39]. A diode pointer of a few mW is brighter and a different spot size. Assumption: the vision algorithm generalises. Change: pick a pointer near 0.3 mW output or attenuate it; compare against the gun's own pilot when available. Left standing.
2. **Servo accuracy.** Hobby servos have deadband and wander; the pointer's true angle is not what is commanded. Not measured: the point is that the camera, not the servo, is the truth.
3. **Safety.** A red pointer above 5 mW is a laser product with its own rules; nothing here says which one to buy. Not sourced on purpose.

## Branches and combinations

- Feeds borrowed-05-guide-star (a real-optics test bed for calibration); pairs with any camera idea from the eyes explorer.

## Unresolved problems and questions that need Derek

- Whether the gun's red light can be lit alone without laser emission (the manual's home page mentions a light-gate and a "light" switch [manual pp. 17, 22]; not verified). If so, the gun itself is the pointer for camera work and this idea reduces to a stand.

## Assumptions

- Nothing here is sourced or measured; the servo resolution figure is arithmetic on an assumed 0.1 degree step.

## Sourcing pointers

None (deliberately: laser pointer choice depends on the answer above).

## Scene

None (sketch).
