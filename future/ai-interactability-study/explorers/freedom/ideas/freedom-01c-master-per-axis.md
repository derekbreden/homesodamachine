# freedom-01c: one master per axis (bungee as preload, as a series spring, or as the whole support)

Scene: `scenes/freedom-01c-master-per-axis` (a one-axis spring bank: bungee, preload bungee, stop, arm, motor bungee, stiff wire). The same effects in the full statics are in `scenes/freedom-01-ring-bungee` (vertical support: stiff wire / long bungee / balancer; bungee stiffness; arm authority); numbers in `calc/06-tables.cjs`, `calc/26-masters.cjs`. Origin: branch of freedom-01. Depth: developed (one scene, four entries).

## Picture it

Take one horizontal axis of the ring-and-bungee support: a ring, a bungee on each side. Now give the same piece of rubber three different jobs. In one it is the only thing on that axis and the ring wanders. In another a screw pushes the ring against the bungee's pull, and the ring sits exactly where the screw puts it. In the third a motor moves the bungee's far end, and the ring floats where the forces balance. Same rubber, three different answers to "who is the master of this axis".

## The proposal

Derek's bungee "holding one axis steadyish" is one of three roles, and the roles have very different consequences for software:

1. **Bungee alone: compliance.** The ring is where forces balance. 1 N of disturbance moves it 6.7 mm at 0.15 N/mm; 0.1 N moves it 0.67 mm. The axis is a soft spring: it isolates and it wanders.
2. **Bungee for preload, hard stop as the locator: position by contact.** A screw or an actuator-driven stop on one side, the bungee on the other with a few newtons of preload. Position is set by the stop (0.02 mm per newton of stiffness with a 50 N/mm contact) until a push larger than the preload unloads it; no backlash while the preload holds. The rubber carries force, the stop carries position.
3. **Series-elastic: force by stretch.** A motor moves the bungee's anchor; the force on the ring is the spring constant times the stretch, so a 0.01 mm anchor step changes the force by 1.5 mN. The ring's position is not commanded but follows; a camera or an encoder closes the loop. Safe (it gives way), gentle on a thin tube, and slow.

The general statement: **a stiff element is a position source, a soft element is a force source; put exactly one stiff thing on each axis and make every other thing on that axis soft or slack.** Two stiff things on the same axis let their mismatch decide the force.

## What carries the loads, what establishes position, what is free or restrained

- Role 1: loads by the bungee; position by nothing; the ring is free within the bungee's range.
- Role 2: loads by the bungee preload; position by the stop; the axis is locked until the push exceeds the preload.
- Role 3: loads by the stretch; position by whatever else is stiff on the axis (the arm) or by the camera loop.

## What software could command, observe, and what stays manual

- Role 2: command the stop's position (a lead screw at 0.01 mm per step or finer); observe with a load cell whether the stop is loaded (contact detected) and with the motor's step count.
- Role 3: command the anchor; observe the force by the stretch (a length encoder on the anchor) and the load cell; the force resolution is set by the anchor resolution times the spring constant.
- Manual: choosing which axes get which role; adjusting preloads.

## What was tried to break it

**Entry 1. Two stiff things on one axis (freedom-01, round 2).**
- Conflict: with the wire at 200 N/mm and the arm at 5 N/mm on Z, the dot moved −0.04 mm for a 1 mm arm command (the wire mastered Z); with a bungee vertical support the same command gave 0.93 mm.
- Assumption: that adding a support only adds capacity. It also adds a competing master.
- Change: make the vertical support soft (role 1 or 3) or give Z to the wires (role 2).

**Entry 2. A bungee stiffer than the arm takes over its axis (freedom-01, round 6).**
- Conflict: bungee 3 N/mm against a 5 N/mm arm: tangent gain 0.24.
- Change: keep the rubber an order below the arm, or make it the master on purpose.

**Entry 3. The stop unloads.**
- Conflict: in role 2 a push larger than the preload lifts the stop off, and the axis drops from 0.02 mm/N to 6.7 mm/N. The cable's pull and the trigger are the pushes that matter.
- Assumption: the disturbance stays below the preload.
- Change: preload above the largest expected push; a second stop on the other side turns it into a clamp (then two stiff things again: manage the mismatch).
- Leaves uncertain: the real disturbance (umbilical pull unknown).

**Entry 4. Friction and creep of real bungees.**
- Not modelled anywhere. A real cord has hysteresis and creeps under sustained load, so a preload drifts over an hour; a metal spring does not. That is a reason to prefer a metal spring where the preload matters, and it is a measurement, not a calculation.

## Branches and combinations

- Feeds freedom-01 (vertical support choice) and freedom-01b (the tail bungee pair is role 3 for yaw).
- The transferable rule (one master per axis, put a stop where the precision is) applies to freedom-02, 03, 07.

## Unresolved problems, and questions that need Derek's observation

- Which axes of the real arrangement should be masters? Nobody has decided.
- Is a bought spring (metal) preferable to a bungee for the preloads (see sourcing: bungee cord roll, spring balancers)?

## Assumptions

- Bungee 0.15 N/mm, preload 5 N, stop 50 N/mm, step 0.01 mm: **illustrative**. Pendulum stiffness = load / wire length [derived], 12 N and 350 mm.

## Sourcing pointers

`sourcing/freedom.md`: bungee cord roll, spring balancers, mini linear rail with lead screw (the stop-and-screw axis), load cell.

## Scene

`freedom-01c-master-per-axis`; see also `freedom-01-ring-bungee`.

## Wave 2 (after the exchange with eyes)

- **The same rule at the moment of contact.** A touch on a soft axis reports the support: a 0.2 N stylus trigger reads 1.3 mm short on a 0.15 N/mm bungee axis and 3 µm on the seat's nose stage (`freedom-12-touch-trigger`). And the rule read the other way gives `freedom-14-hand-plus-guidance`: a soft element in parallel with the hand is a force source the hand can always overrule, and 0.2 N moves a relaxed hand about 0.3 mm.

**Wave 3 note (from borrowed's exchange, "smaller remarks" on freedom-01).** Two spring balancers opposing in X and Y are a zero-stiffness horizontal support where friction is the only stiffness: the "soft element as a force source" of this file with nothing to set its rest position but the friction, which is the master-per-axis rule read at its limit. A bungee's stiffness is EA/L, so its length is the stiffness knob. The scene's stiffness labels were printing raw decimals (0.1517050367459337 N/mm); they now read to two figures. Decision: answered, no change of the idea.
