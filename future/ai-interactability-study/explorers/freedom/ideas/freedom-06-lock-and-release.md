# freedom-06: lock and release (an articulated arm whose constraints change by state)

Scene: `scenes/freedom-06-lock-and-release`. Origin: swarm original (from the freedom framing). Depth: rough (a 2D chain with illustrative friction; three entries). Numbers from the scene's model.

## Picture it

A photographer's "magic arm", or a machinist's flex indicator holder: a chain of ball joints ending in the gun's shell, with one central lock. Unlocked, every joint is loose and a hand (or a small stage) can place the gun anywhere the chain reaches. Locked, every joint is clamped. The gun has two lives: floppy while it is being placed, rigid-ish while it welds.

## The proposal

Assign the arm's freedom **by state** rather than by joint: all free, or all held. A lock actuator (a solenoid or air cylinder pulling a cable through the chain, as in the arms on the market) is the only software-commanded part; the placing is by hand, or by a vernier stage at the tip; the pose is read by small magnetic encoders at the joints. The point is the sequencing: release, place, lock, weld, release, swap.

## What carries the loads, what establishes position, what is free or restrained

- **Weight**: each joint's clamp friction carries the torque of everything beyond it. The base joint carries the most when the chain reaches out sideways: the gun's weight times its horizontal reach.
- **Position**: nothing in this arrangement establishes it; the joints hold whatever pose the hand left. Encoders report the shape; a camera reports the dot.
- **Free** (released): all joints. **Held** (locked): all joints, up to their capacity and with a little give.
- **Driven**: by hand or vernier; the lock by an actuator.

## What software could command, observe, and what stays manual

- **Command**: lock/release; an optional vernier at the tip.
- **Observe**: joint angles (a magnetic encoder is a few dollars, [sourcing](../../../sourcing/freedom.md)); the dot by camera; a nearest-to-slip estimate from the joint torques (no torque sensor is proposed).
- **Manual or unresolved**: placing the gun while released; choosing mount and link lengths.

## What was tried to break it

**Entry 1. A locked friction chain is not a locator.**
- Conflict: with illustrative clamps (0.3 × 20 mm ball × 1000 N = 6 N·m per joint) and pre-sliding stiffness 20 N·m/rad, a locked three-joint chain gives 7 to 11 mm per newton at the tip.
- Assumption: locked means rigid.
- Change: keep the vernier and the camera; the lock holds weight (as in freedom-02, entry 5).
- Leaves uncertain: real photo-arm clamp torque and stiffness. The arm on the SmallRig listing does not state a payload rating (unchecked, [sourcing](../../../sourcing/freedom.md)).

**Entry 2. The base joint slips first.**
- Conflict: for the default shape the base joint carries about 5 N·m against 6 N·m available; lengthen the reach or lower the clamp force and it slips, and the chain sags until it finds a shape it can hold.
- Assumption: every joint has the same job.
- Change: fold the chain compactly, shorten the first link, or clamp the base harder than the tip.

**Entry 3. Hang it from above.**
- Conflict/opportunity: mounted overhead and straight down, the load acts along the links and the joint torques fall to the cable pull's share (all four bars almost empty); the tip still gives sideways (25 mm/N in the scene: pre-sliding lets it swing like a pendulum).
- Assumption: an arm reaches out from the side.
- Change: overhead mount. The cost: the chain hangs above the tube, in the umbilical's way.

**Entry 4. Releasing under load.**
- Conflict: at the moment of release the gun's weight is uncarried; a hand, a balancer, or the vernier must already hold it.
- Change: a gas spring or balancer carries the weight through the release (freedom-02).
- Leaves uncertain: whether the lock and release can be timed so the gun does not drop or jump.

**Entry 5 (wave 3, from borrowed's exchange, "smaller remarks"). A chain is the wrong shape for a load that is almost all vertical. Decision: revised (scene text) and the branch noted.**
- Conflict: at the scene's defaults the locked three-joint chain gives 176 mm at the tip under the gun's own weight (7.1 mm/N horizontally, 11.1 vertically; 20 N·m/rad of pre-sliding per joint). Reproduced in the scene: 176.5 mm.
- Assumption: every joint carries a share of the load and every joint needs a lock.
- Change: a monitor arm is a SCARA: its two swivels carry no gravity torque, and the one joint that does is the shoulder. The lock belongs on the one axis where the load acts, and a locking gas spring (Bansbach B-locking, 28 inch, 135 N, "rigidly lock in both directions", $71.57; chair gas lifts $22.99, 2.2K ratings: the same idea in the billions, borrowed's listings) holds any height rigidly under load and releases by a pin. It is freedom-06's lock on that one axis, freedom-10's retract (unlock and the spring's excess force lifts) and freedom-02's balance in one part. The overhead mount of entry 3 is the same idea by geometry.
- Leaves uncertain: the lock's stiffness and its release force (borrowed's listings do not state them).

## Branches and combinations

- With freedom-02: a brake at each joint of the balanced arm is this idea.
- With freedom-05: the vernier for the per-tube offset.
- With freedom-04: the overhead mount puts gravity along the links; the free tangent is a pendulum swing.

## Unresolved problems, and questions that need Derek's observation

- Clamp a photo arm at the working reach with a 1.2 to 1.5 kg dummy load: does it hold? How much does the tip move under a 2 N cable tug?
- Is there a joint design (ball-and-socket versus hinge) whose pre-sliding stiffness is high enough that locking gives millimetre-level hold?

## Assumptions

- Three joints, four links of 130 mm, 60 g each; payload 1.2 kg (gun mass **[unknown]**); μ 0.3, ball radius 20 mm, clamp force 1000 N; pre-sliding stiffness 20 N·m/rad; released friction 5% of locked: **illustrative**.
- The chain is planar and static; out-of-plane behaviour is not modelled.

## Sourcing pointers

`sourcing/freedom.md`: SmallRig 9.8 in magic arm ($19.99, 2,975 ratings, "3K+ bought"; payload unchecked); AS5600 encoders; small stepper and linear rail for the vernier.

## Scene

`freedom-06-lock-and-release` (rough).
