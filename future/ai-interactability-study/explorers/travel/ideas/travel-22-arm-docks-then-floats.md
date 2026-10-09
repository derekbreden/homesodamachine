# travel-22-arm-docks-then-floats: an arm docks the gun, floats it, reads the joints, re-teaches, holds

Origin: combination of `travel-14b-crown-cartridge` (an idea with no scene; the scene's meta names its neighbour `travel-04-return-seat`) with `use-14-handover-shift`, answering use's question "who docks the gun, a hand or a machine?". Depth: developed. Scene: `scenes/travel-22-arm-docks-then-floats`. Calculations: `calc/17-float-release.mjs`.

**Picture it.** A six-axis arm carries the gun in its printed shell to a yoke with three balls and sets it down within capture (a few millimetres). Magnets pull the plate onto the balls. The arm then goes limp in the way its own hand-guide mode does: it carries the weight and nothing else. The AI reads the six joint angles, which now say where the seat holds the gun, and teaches that as the dock pose. Only then does the arm hold, or its brakes take, and the weld begins.

## The proposal

use-14 found that an arm may let go of a soft support only at zero arm force, and that a handover shifts the gun after the last look. A dock is a handover to a seat, and a cobot has the feature the rule asks for: **float** (gravity compensation with the declared payload). The proposal is a sequence, **dock, float, read, re-teach, hold**, and the reason for each step comes from a number:

- **Hold fights the seat.** An arm holding a taught pose 0.5 mm off the seat, at 5 N/mm, still pushes about 1 N into it after the seat has given; the dot ends 352 micrometres off.
- **Float leaves residuals.** Joint friction (1.5 N at the flange, unmeasured), the umbilical's change (1 N) and a payload declaration error (0.1 kg is 1 N) are forces the arm cannot null: 444 micrometres.
- **Read and re-teach.** In float the encoders are a coordinate measuring arm: they read the seat's pose. Re-taught, the mismatch falls to the encoder's 0.03 mm plus 0.05 mm of drift and the dot to 131 micrometres; stiffnesses then add in parallel.
- **The seat's rocking compliance is the term that matters.** A sideways force at the flange, 120 mm above the balls, tips the plate about the far balls, and the dot sits 200 mm from that axis: 0.16 mm per newton against 0.017 mm per newton of translation at 40 N/mm per ball and a 50 mm ring. A seat at the nozzle end (lever 20 mm, ring 80 mm, flange 60 mm up) leaves 3 micrometres per newton: 25 micrometres after a re-teach.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** between docks, the arm; once docked, the seat carries the gun and, in float, the arm carries the weight; in hold the arm and the seat share the sideways load by stiffness.
- **Establishes position:** three balls in three grooves; after a float, the arm's joint angles are that position, read exactly.
- **Free / restrained / driven:** the gun is free above the seat, restrained by six contacts and a preload once docked; the arm's mode is the commanded state (hold, brake, float).

## What software could command, observe, what stays manual

- **Commands:** move to the taught pose and descend to capture; float; re-teach; hold or brake.
- **Observes:** the six encoder angles (exact), the flange force on arms that have a sensor (UR3e: +-2 N precision, too coarse for a 1 N change), contact continuity if the seat has switches. **Blind:** the dot, the declared-mass error, the umbilical's pull.
- **Manual:** declaring payload and centre of gravity; placing the dock and its magnets; the fibre routing.

## What was tried to break it

1. **Own break: a printed groove is not 40 N/mm.** *Conflict:* every seat number scales with the contact stiffness; at 400 N/mm a re-taught hold leaves 23 micrometres, at 40 N/mm 131. *Assumption:* 40 N/mm per ball. *Change:* the slider; the nose seat and a wider ring reduce the dependence more than a stiffer contact does. *Leaves:* the real stiffness of a steel ball in a printed groove.
2. **Own break: the release shift.** *Conflict:* letting go from a re-taught hold into float moves the dot 304 micrometres at these numbers, because float brings its own residual force. *Assumption:* float is neutral. *Change:* do not release into float for the weld; hold or brake after the re-teach; use float only for the read. *Leaves:* the brake's engage shift (0.03 mm is a placeholder).
3. **Own break: the declared mass is a force.** A heavier declaration than the truth lifts the gun by the difference times g. *Change:* weigh the gun; the AI can estimate the error by floating and reading the force the seat carries. *Leaves:* the gun's mass is unknown; the umbilical's pull is not in the payload and changes with the pose.
4. **Which arm.** No Prime-listed arm carries a gun of 1 kg (desk arms are 0.25 to 0.5 kg); the 3 kg class (UR3e, Fairino FR3) is sold by the makers. A desk arm carries a camera or a stylus and reads joint angles.

## Branches and combinations

- With `use-16-yoke-escape` (theirs): the same pivot as the dock's pitch axis; the arm does the escape by moving along the beam instead.
- With `travel-04`: the seat with contact switches; with `freedom-01b-nose-seat`: the seat at the nozzle end.

## Unresolved problems and questions for Derek

- Would you let a machine put the gun on a dock? What does the gun weigh with the shell on? Could a printed seat sit at the nozzle end rather than the housing?
- Every stiffness, force, height and lever is illustrative.

## Assumptions

- Ball circle 50 mm, flange 120 mm up, dot 200 mm from the rocking axis, 40 N/mm per ball, friction 0.2, preload 15 N, arm 5 N/mm in hold, 0.1 N/mm in float, float residual 1.5 N, 0.1 kg declaration error, 1 N umbilical change, 0.03 mm encoder re-teach error, 0.05 mm drift: **illustrative**.

## Sourcing pointers

`sourcing/travel.md` entries 24 to 34: desk arms on Prime (24 to 29), the Fairino FR3 and UR3e (31, 32), other makers (33).

## Scene id

`travel-22-arm-docks-then-floats`
