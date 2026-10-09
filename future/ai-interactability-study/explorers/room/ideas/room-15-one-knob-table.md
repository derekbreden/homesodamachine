# room-15: one-knob table, the plane carries, a rail gives radial, the table turns

**Origin:** combination of `use-06-coach-loop` and `use-09-programmed-table` with `room-02`, `room-01` and `room-09` (wave 2 exchange, sections 2 and 4). **Scene:** `scenes/room-15-one-knob-table`. **Depth:** developed.

## Picture it

A table whose top is flush with the tube rim, a round hole under the tube, the rotator on a shelf below. On the table, the gun stands on three ball feet on a flat sled; the sled rides two short rails that run in the radial direction. A long screw under it ends in a knob with a digital scale beside it. The umbilical hangs from a hook overhead. Nothing holds the gun. A screen says "radial: +8 notches", the hand turns the knob, the table program goes on turning.

## The proposal

Let the room be the rest. The table plane fixes height, pitch and roll by contact; the rail fixes tangent and yaw; one screw and knob with a scale fix radial; a shelf under the rotator fixes vertical (once per tube, dropped 26 mm at the end of a bead). Because the tube turns, the seam passes under a fixed dot and the gun needs no tangent axis (a tangent slide of 1 mm costs 0.008 mm radially and turns the approach 0.93° [derived]). The rotator's controller gains programs (index to the eight tacks in the opposite-side order, one dry lap, a 380° bead) under the pedal deadman (use-09). Software reads the knob and degrees, keeps the record, and says how far to turn (use-06). The hand has one thing to steer, and, through `room-14`, one to squeeze.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** shell legs to the sled to the rail to the table. The umbilical is carried by its hook, not the gun.
- **Establishes position:** table plane (three contacts), rail, screw and scale, shelf.
- **Free:** nothing while the screw clamps the sled; the shell must be pinned or magnetised to the sled against a stuck-wire yank (a 10 N pull lifts a foot: room-02). **Driven by hand:** radial knob. **Driven by machine:** rotator, optional shelf motor.
- **Escape at the end of a bead:** the gun cannot lift along its barrel from a sled; the shelf drops the rotator 26 mm (0.43 s at 60 mm/s, illustrative).

## What software could command, observe, and what stays manual

- **Command:** rotator programs; optional shelf motor.
- **Observe:** knob scale, degrees, foot loads (three cells; the weigh-in of room-02), a camera on the dot as in room-01 (not drawn).
- **Advise:** the coach line (from the exact offset in the scene; a camera would give a noisy estimate).
- **Manual:** radial knob, pedal, trigger, loading through the hole, snipping a stuck wire.

## What was tried to break it

1. **use-06's arm is soft.** A locked friction arm is about 0.1 N/mm at the tip (freedom-06, illustrative): 1 N is 10 mm. A sled on a rail pressed by a screw is a few tens of N/mm if screw and sled behave: 1 N is 0.1 mm or less (`room-13`). *Leaves:* real stiffness, backlash of the screw against a pull of one sign.
2. **Tangent.** The rail forbids it; different coarse orientations mean different printed legs. *Leaves:* the wire approach with the rotation direction (use-10: a campaign state).
3. **Escape.** The sled cannot lift; the shelf must drop fast enough that the wire breaks in air. *Leaves:* the speed needed, and a rotator with a tube dropping under control.
4. **Stuck-wire yank.** 10 N lifts a foot at any balancer share (room-02). *Leaves:* a hold-down that adds no friction against the knob.
5. **One person, one knob, one pedal, one trigger.** The knob needs about 11°/s to follow 0.016 mm/s at 0.5 mm per turn (use-04). *Leaves:* whether a person can; a moving target on the screen keyed to degrees (use-04, datum-02) is the help.
6. **The opening.** A hole in the bench, or a rim-height platform around the rotator: the same idea without cutting. *Leaves:* Derek's bench.

## Branches and combinations

- Branch of `use-06` (the arm is replaced by the room); combines `use-09` (the program), `use-08` (the record is nearly free here), `use-04` (the angle-keyed map as the coach's target), `room-14` (the trigger path), `room-02` (stool, weigh-in, hanging umbilical), `room-09` (the shelf).
- With a motor on the screw it becomes a one-axis follower under `use-04`'s replay; with a second station it is `room-12`'s carriage.

## Unresolved problems, and questions that need Derek's observation

- Screw, sled and clamp stiffness (deflection under the gun's weight); trigger force; gun mass; umbilical pull.
- Where the operator sits; whether the bench can take an opening.
- How fast a dropped rotator can leave for the wire to break clean.

## Assumptions

- **[illustrative]** gun proxy and opening pose; mass 1.47 kg; table 30 mm, hole radius 80 mm, sled ±10 mm, screw 0.5 mm/rev, scale 0.01 mm, shelf ±12 mm; shelf speed.
- **[repo]** runout limits 0.25 / 0.30 mm TIR; rim 238.4 mm above the bench; tack pattern; pedal deadman.
- **[derived]** tangent-slide arithmetic; foot loads by statics.

## Sourcing pointers

`sourcing/room.md` entries 10 (MGN12H rail), 12 (2020 extrusion), 2 (ball transfer units); `sourcing/borrowed.md` (cross-slide, 150 mm digital scale); `sourcing/use.md` (NEMA 17 with T8 lead screw).

## Scene

`scenes/room-15-one-knob-table`
