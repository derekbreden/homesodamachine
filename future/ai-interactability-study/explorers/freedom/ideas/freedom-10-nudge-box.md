# freedom-10: move only, blind (a nudge box), and a spring-driven retract

Scene: `scenes/freedom-10-spring-retract` for the retract coda (rough); the nudge box itself has no scene (the vernier of `freedom-02-balanced-arm` and `freedom-05-runout-table` is the same actuator with a camera added). Origin: swarm original (from the freedom framing). Depth: sketch (`calc/27-nudge-retract.cjs`); parameters **illustrative**.

## Picture it

A small box on the bench with two knobs' worth of stepper motor and a little XZ stage, connected to a laptop. Software can nudge the gun by 0.1 mm at a time and remembers the count. It cannot see anything. A person watches the red dot and says "a bit more". It is a tool with a memory, not a machine that knows.

## The proposal

The smallest *software moves and observes nothing but its own step counts* arrangement. An XZ vernier (stepper, T6×1 lead screw: 1 mm per turn, 5 µm per full step, 0.31 µm per microstep [derived]), a hard **home stop** on each axis, and software that stores a position as "steps from home". A person positions coarse and fine; software makes the fine part **repeatable**: the same numbers reproduce the same relative moves, and a stored setup for one tube can be recalled for the next. Repeatability comes from the stop and from the screw, not from any sensor.

Coda (assigning motion to a spring): the end-of-bead retract is a motion the current sequence does by hand: "the trigger stays held while the operator lifts the head straight away, and the gun's retract cycle breaks the wire in air" [repo]. A spring or bungee that lifts the head 20 mm in 0.2 s needs a net 1.2 N above what carries the weight (mean acceleration 1 m/s²: 24 mJ of energy); a latch (a servo hook or solenoid) holds the preload, software releases the latch when the bead has passed its stop, a slow motor re-arms. The retract speed the wire break needs is **[unknown]**.

## What carries the loads, what establishes position, what is free or restrained

- The nudge box carries nothing beyond the stage's payload (the gun's shell if it sits on the stage): position comes from the home stop and the screw.
- Retract: the spring's stored energy; the latch holds it; a hard stop ends the travel (repeatable to the stop's play).

## What software could command, observe, and what stays manual

- **Command**: steps on each axis; the latch.
- **Observe**: step count; limit-switch state at home; nothing about the weld.
- **Manual**: everything a person sees: the dot, the seam, the weld. The person is the sensor.

## What was tried to break it

**Entry 1. Step counts drift from truth.**
- Conflict: a stepper can lose steps (skipped under load, missed on a jam) and a lead screw has backlash; the count then no longer matches the position.
- Assumption: counts are a position.
- Change: re-home against the stop at every setup; a preload spring on the screw removes backlash; use light loads.
- Leaves uncertain: the real stage's stiffness under the gun's weight.

**Entry 2. A hand cannot judge 0.1 mm.**
- Conflict: a person watching the red dot at the seam cannot see 0.1 mm without magnification; nudges of 0.2 mm need a loupe or a camera.
- Assumption: a human is a good instrument.
- Change: a magnified view (a cheap camera and a screen) turns the person into a better sensor; freedom-05 replaces the person by a fit.

**Entry 3. The retract's speed is unknown.**
- Conflict: the current practice is a hand lift with the trigger held; how fast the wire breaks cleanly in air is not recorded.
- Change: measure with the current hand lift (a phone video of the head).
- Leaves uncertain: whether a spring lift is repeatable enough (spring rate, friction of the guide).

## Branches and combinations

- Same actuator as the vernier of freedom-02, 05.
- With freedom-06: the lock plus the nudge box is the minimal locked-arm system.
- The retract latch pairs with any of the arrangements (the head lifts along its own approach).

## Unresolved problems, and questions that need Derek's observation

- How fast does the head leave at the end of a bead today? How far? (Video.)
- Is a person plus a loupe good enough to teach what tolerance the weld needs?

## Assumptions

- T6×1 screw and 200-step motor at 1/16 microstepping: common stock values, **illustrative**. Gun 1.2 kg (**[unknown]**). Retract 20 mm in 0.2 s: **illustrative**.

## Sourcing pointers

`sourcing/freedom.md`: mini linear rail with a T6×1 screw and NEMA 11 ($54.80, 34 ratings), XYZ manual stage ($125, 14 ratings), NEMA 17 geared motor.

## Scene

`freedom-10-spring-retract` (the retract coda only).

## Wave 2 (after the exchange with eyes)

- **The lattice of eyes-12 needs a repeatable approach.** A raster that reverses each row folds the screw's backlash into the labels; approach every point from one side (roughly twice the time, under six minutes for 9 × 5) or preload the axis against its stop (freedom-01c). The nudge box is the positioner eyes-12 lacks.

**Wave 3 note (from borrowed's exchange). Decision: revised (the retract scene gained a soft-close damper).** The retract reaches its stop at 166 mm/s and puts 16.4 mJ of its 24 mJ into it as an impact on a 1.2 kg gun; a hydraulic soft-close damper or a gas spring with end-of-stroke damping is the mass-produced way to spend the last few millimetres. In `freedom-10-spring-retract`, 40 N·s/m over the last 6 mm brings the impact to 0.5 mJ and the speed at the stop to 27 mm/s. The AZ-GTi note is in freedom-09.
