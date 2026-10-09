# borrowed-07-tonearm: the tube's own rim sets the height

Origin: swarm (phonograph tonearm, counterbalanced follower). Maturity: rough. Scene: `scenes/borrowed-07-tonearm/index.html`.

## Picture it

A long arm with a counterweight on a post beside the rotator. Its front end carries the gun and, under it, a small ball that rests on the top edge of the tube. When the turning tube wobbles, the ball rides up and down and the whole arm nods with it, and the dot stays the same distance below the rim without any sensor or motor. A magnetic encoder on the pivot happens to read the wobble.

## The proposal

Let the workpiece hold the gun's height: a follower on the rim, as a stylus rides a groove. The counterweight makes the gun weigh a couple of newtons at the foot instead of its full weight. The foot rides the rim, not the plate, so nothing touches the weld path. The arm's pitch angle is a free face-runout signal.

## What carries the loads, establishes position, is free, restrained, driven

- Load path: gun, bracket, arm, pivot post, bench; the counterweight balances the arm.
- Position: height from the rim under the foot (contact). Free: arm pitch. Restrained: everything else (radial, tangent, orientation) is not addressed and needs another mechanism. Driven: nothing.

## Software: command, observe, manual

- Could command: nothing. Could observe: the arm angle (rim height at the station).
- Manual: balancing the counterweight for the gun; placing the pivot post so the foot is on the rim and the dot on the seam; radial position.

## What was tried to break it

1. **What the foot follows.** Rim height only. The scene at the opening pose with the rig-doc face runout exaggerated 20 times: the dot's vertical error is 1.43 mm with the arm locked and -0.005 mm with the follower; the radial error (-2.5 / -2.2 mm in exaggerated units) is untouched. Assumption: the rim is a good reference for the seam. It is not, if the plate's depth below the rim varies from tube to tube [unknown]: a 1 mm recess error is a 1 mm dot error the follower cannot see. Change: a per-tube height trim on the foot stalk. Left standing: one axis of three.
2. **Force.** With the defaults the foot force is about 2 N [derived from illustrative masses]; 100 g of gun mass error is 0.98 N and 50 g of counterweight at 150 mm is 0.31 N. Too much and the foot scuffs the rim; none and the gun rises to its stop (the scene lifts it 13 mm at a 2.5 kg counterweight). Uncertain: the gun's mass; the umbilical's pull.
3. **Friction drag.** The turning rim pushes the foot with about mu times the foot force (0.3 illustrative: 0.6 N at 2 N). A tonearm calls this skating. Not drawn.
4. **Foot on 316L.** Wear, marking and static: unresolved; a ceramic or PTFE foot is a guess.

## Branches and combinations

- Combines with borrowed-05-guide-star or borrowed-06-swing-offset for the axes the follower does not cover; with borrowed-03 (the same encoder-at-a-pivot idea).
- Contrast with the nose-seat and rim-crown ideas of other explorers (not read in this wave), which also use the rim as the reference.

## Unresolved problems and questions that need Derek

- The plate's depth below the rim across his tubes (a caliper or depth gauge reading on several tubes: does it vary by tenths or by millimetres?).
- The gun's mass; whether the umbilical pulls noticeably.

## Assumptions

- Arm length 237 mm to the foot, pivot height, ball radius 3 mm, arm mass 0.15 kg, friction 0.3: illustrative. Rim height = joint height plus 6.35 mm plus the recess slider [repo dims]. Face runout limits 0.25 / 0.30 mm TIR [repo], exaggerated for display. The arm follows exactly while loaded.

## Sourcing pointers

None needed yet (an encoder module is in sourcing/borrowed.md; a ball-transfer unit or ceramic ball was not looked up).

## Scene

`borrowed-07-tonearm`
