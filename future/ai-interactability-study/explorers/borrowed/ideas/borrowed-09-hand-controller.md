# borrowed-09-hand-controller: a small leader arm, or a 6-DoF puck, as the way a person and an AI meet the machine

Origin: swarm. Maturity: sketch (no scene). Related scene for the same pattern: borrowed-03-encoded-arm (encoders on a hand-guided arm).

## Picture it

A small printed arm with servo encoders on the bench, the leader. A person moves its tip and a larger motorised arm or gantry (the follower) carrying the gun mirrors it at scale. The moves are recorded as episodes: pose against time, alongside the camera. Later an AI replays them, adjusts them, or learns from them. For plain setup jogging, a 6-DoF puck (the kind CAD people push and tilt) or a machinist's handwheel does the same job with fewer parts.

## The proposal

Hobby robotics has a full pipeline for recording hand demonstrations and replaying them (LeRobot with the SO-101 arm: six Feetech STS3215 servos, printed frame, Python API). The follower there is far too small for a gun; the leader is the useful part: it is a $100 to $200 hand controller with absolute encoders, and every hand-taught pose becomes data. On Prime: an SO-101 follower electronics kit ($184.99, 1 rating, 1 in stock; the listing is thin), a 3Dconnexion SpaceMouse Compact ($171, 1,044 ratings, 200+ bought). Neither was tried; the SO-101 numbers come from the listing and search summaries (unchecked).

## What carries loads, establishes position, is free, restrained, driven

- The leader carries nothing but itself. Position is mapped, not measured: leader pose to follower pose through a calibration. The follower is another idea's mechanism (a gantry, rings, the gimbal).

## Software: command, observe, manual

- Could command: the follower, from the leader. Could observe: leader joints; the follower's own state; a camera. Manual: the human's hand.

## What was tried to break it

1. **Accuracy.** A hand controller is not a measuring instrument: 12-bit servo encoders (0.088 degrees) on a 300 mm arm are about 0.5 mm per joint before backlash, the same scale of problem as borrowed-03. Change: use it for gross moves and demonstrations, and let a camera loop (borrowed-05) do the last millimetre. Left standing.
2. **Scale.** Mapping a 300 mm leader to a much smaller weld neighbourhood makes jog gain a parameter. Not explored.
3. **Silly version.** The kit's follower carrying the gun: the servos are rated 30 kg-cm each (search summary, unchecked), against a gun and umbilical of unknown mass at a 250 mm lever. Not credible; kept only as the reason the leader is the useful half.

## Branches and combinations

- With borrowed-02 or borrowed-01 as the follower; with borrowed-03 (encoders as the demonstration recorder).

## Unresolved problems and questions that need Derek

- Whether an AI trained on demonstrations of this weld is wanted at all, or whether a scripted loop is enough.

## Assumptions

- STS3215 encoder resolution and torque figures: from search summaries, unchecked. Prices observed 2026-09-28 (sourcing/borrowed.md).

## Sourcing pointers

sourcing/borrowed.md: SO-101 follower electronics kit; SpaceMouse Compact; CNX Software article.

## Scene

None (sketch).

## Wave 2

- **A hand controller with a rendered feel:** `borrowed-19-haptic-jog` (combination with freedom-14) is a knob on a brushless gimbal motor and a magnetic encoder (a $35 kit on Prime): detents, a wall, a capped pull toward the seam and a damper are a program, the hand supplies the motion, and the gun is never touched. In the leader-follower reading, the knob follows the stage when software moves it and the hand feels the correction.
