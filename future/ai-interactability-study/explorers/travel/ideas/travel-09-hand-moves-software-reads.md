# travel-09-hand-moves-software-reads: the person is the actuator

**Picture it.** The stack of travel-01, or a hand-set gun holder, cranked by hand with handwheels, but every axis carries a digital scale whose count goes to the computer. The AI cannot move anything. It reads every stage position and the dot from a camera and says: "X wheel plus 0.35 mm, approach from the low side." A person turns the wheel; the scale confirms.

Scene: it is the `hand wheels + scales` branch of `scenes/travel-01-tube-travels` (Who turns the screws). Idea only otherwise.

## The proposal

Software observes and moves nothing, on purpose. Instrumenting a manual stage gives the AI the one channel it lacks with hand-set stages, the *position of each stage*, so it can learn how stage positions map to the dot, log every setup for repeatability, and give exact instructions. It needs no motors, controllers or drivers, and a mill-style cross table is an ordinary object (`sourcing/travel.md` 1, 2). It is also the cheapest first step toward the motorised version: the scales stay when motors are added.

## What carries the loads, what establishes position, what is free or restrained

As travel-01: holder post carries the gun; the stack carries the rotator. Position is set by the wheels and read by the scales; each axis is locked (gib screws) once set. Free: nothing; restrained: gibs; driven: by a hand.

## What software could command, observe, what stays manual

- **Commands:** none. It *instructs*: which axis, how far, from which side.
- **Observes:** scale counts per axis; the dot from a camera; the rotator (existing console).
- **Manual:** every motion.

## What was tried to break it

**1. Handwheel resolution.** *Conflict:* the dovetail table in `sourcing/travel.md` 1 lists a handwheel ring of 1.5 mm; a person can set a dial to perhaps a fiftieth of a ring (0.03 mm) but not hit 0.005 mm. *Assumption:* the target is a few hundredths. *Change:* the scale, not the dial, is the reference; the software instructs a move and the person stops when the scale reads the target. *Leaves:* backlash: approach from one side.

**2. A scale is not the dot.** *Conflict:* stage position is not seam position: tilt (232 mm Abbe height), holder creep and runout do not show on the scales. *Change:* the camera closes the loop as in travel-01. *Leaves:* the same blind spots.

**3. Whether the scales can be read.** *Conflict:* the DRO console on Prime has 6 reviews and its data output is unverified (`sourcing/travel.md` 11). *Change:* scales with a documented quadrature or serial output; or read the display with the camera. *Leaves:* unresolved.

## Branches and combinations

- **With travel-10:** the mirror image: software moves, a person is the eye.
- **With travel-01:** motors replace hands; scales stay to confirm the motion.
- **With travel-02:** the ladder works with hand stages, only slower.

## Unresolved problems and questions for Derek

- Does he own a mill or a bench table with scales he could borrow for a dry run?
- Would he accept "turn X by 0.35" instructions during dry runs, and how long could he keep it up?

## Assumptions

- Handwheel ring 1.5 mm/turn: listing text (Amazon, MYSWEETY, 2026-09-28). Person's dial resolution: illustrative.

## Sourcing pointers

`sourcing/travel.md`: dovetail XY tables (1, 2), digital scales (11), digital indicator (12).

## Scene id

Branch inside `travel-01-tube-travels`.
