# F. Teach by hand, record, replay — the hand finds, the record keeps, a mechanism repeats

Sketch: `../sketches/w4-teach-record-replay.svg` (flow, plus a plan to scale at the
true opening pose showing camera and tag placement). Numbers: `../calc/w4_calcs.py`
§2.

## Picture it

Derek holds the gun on the weightless carrier of idea E (or the film-grip arm):
the gun hangs from a bail at its centre of mass, carry pins out. He puts the red
dot on the corner by eye while the pedal turns the table, as he would to weld.

- **Pose.** A small AprilTag plate and an IMU on the shell are watched by a pose
  camera high on the −X/+Y side, against tags on the subplate and dock post. The
  rim has already been set to its flag, so the station frame is the joint frame.
- **Dot.** The joint camera on the free +Y side sees the dot against the corner.
- **Timing.** The rotator's console logs table degrees and pedal. A switch on the
  trigger presser logs trigger on and off.
- **The record.** A file (mean pose, spread, timing, settings, dot image) plus a
  recipe block printed from the taught angles.
- **Replay (R1).** Set the dock's two dials from the file, fit the block, carry the
  gun into the dock with carry pins in, and compare the live dot to the recorded
  image.
- **Other replays.** R2 guides a hand with live error bars instead. R3 puts the
  dock's axes on motors.
- **What carries, what locates.** The carrier carries while teaching. The cameras
  and IMU measure and hold nothing. The dock locates on replay.

## Major unresolved problems

1. **The pose-to-dial model.** It needs the scanned gun and a measured
   dot-to-shell relation. Until then R1 replays by iteration against the recorded
   dot image.
2. **Whether tags survive real weld light.** Dry laps are safe.
3. **How steady a guided hand is (R2).** The first teaching sessions measure it.

## The idea, through the session view

Derek's hand is good at one phase and poor at three:

- **Good at finding a pose.** With the red dot as feedback, and his eye on the
  corner and puddle, he already welds this joint.
- **Poor at holding it** for a 48 s lap, **repeating it** tomorrow, and **handing
  it** to someone else.

Machines are the opposite. So split the session: the hand finds the pose, a record
captures it, a mechanism reproduces it, and a second person follows the record.

This is his own argument ("If I learn the skill on my own … I become the
bottleneck") turned into equipment. It also gives his learning curve a measured
starting point: today's hand practice becomes a recorded baseline, not a memory.

## The whole arrangement (F1)

**Carrier for teaching:** the weightless carrier of idea E (monitor arm and CG
bail), or borrowed-ecosystems' film-grip arm, with the carry pins OUT. The gun then
floats with no weight and no gravity torque, and the hand sets its attitude freely.
What the hand feels is the gun's inertia, the umbilical's torque about the CG
(0.1–0.6 N·m for 1–5 N at the 129 mm cable-exit lever), and nothing else. The
record is not distorted by fatigue.

**What is recorded, every frame, on one clock:**

| Quantity | How | Resolution (estimates) | Used for |
|---|---|---|---|
| Shell pose (6 DOF) in the station frame | AprilTag plate on the shell; tags on the subplate and dock post; a pose camera high on −X/+Y (a second camera improves depth) | ~0.1 mm, ~0.1–0.3° after calibration (the pixel limit is far finer: 0.064 mm/px at a 300 mm field) | the recipe's angles and position |
| Dot vs corner, standoff, wire tip | Joint camera on the free +Y side, with a red long-pass filter (machine-that-learns' observation layer) | dot centroid 10–20 µm; ~3 px per 0.1 mm of standoff | where the beam actually was |
| Tilt vs gravity at 100 Hz | IMU on the shell (BNO085 class) | ~0.2–0.5° absolute, better relative; no heading | hand tremor and drift through the lap |
| Table angle, pedal | the rotator's console (0.025° per pulse) | exact | timing against the joint |
| Trigger on / off | microswitch on the trigger presser lever | ms | timing |
| Stickout | set at the cradle gauge; seen by the joint camera | set value | recipe |

The pose is recorded relative to **station** tags, after the rim has been brought
to its flag (per-tube height, phase 2). That makes the record a pose relative to
the joint, not to wherever the carrier happened to be. Nothing is tagged on the
turning table.

**Teaching, as a session:**

1. **Setup.** Load the tube, set the rim to the flag, and fit the plate at its
   recess.
2. **Dry laps.** Hold the gun at the pose Derek would weld at, with the dot on the
   corner by eye and the pedal turning the table at weld speed, no trigger. Record
   2–5 laps.
3. **Optionally, real hand welds** (tacks, coupons), recorded the same way. In the
   weld light the pose camera loses the tags (see F2), so the IMU and the console
   carry those records.
4. **Review.** The software gives the mean pose, its spread (how steady the hand
   was), and the dot track against the corner. Derek marks the lap he trusts.

**The recipe, a file plus an object:**

- **From the mean pose, the dock's numbers:** X and Y dials, the WELD stop, and
  per-tube height stays with the flag.
- **The recipe block, printed from the taught angles** (who-moves-what's blocks,
  one-knob-one-parameter's cartridges). Teach in the afternoon, print overnight,
  dock tomorrow.
- **Validation before printing:** the taught pose must dock and must escape. The
  wire-escape sweep (`calc/lid_swing2.py`) and the dock and plate-head clearance
  checks run on it. The sweep scripts become the recipe validator; a taught pose
  that cannot escape the lip is reported, not printed.
- **Timing, settings, and the target image:** start N° after rotation, stop at 380°,
  wobble, power, wire feed, pullback, stickout and graduated-tube reading, plus the
  recorded dot image.

## What replay means physically

- **R1 — stops from the record (main).** The dock's X/Y dials are set to the
  record's numbers and the printed block goes in. The gun is carried to the dock
  (carry pins in), seated and latched; the dock's geometry reproduces the taught
  pose. The joint camera overlays the live dot on the recorded dot image, and the
  tags report the pose error.
  - *Error budget:* dial reading and block print (~0.1 mm, ~0.1°) + dock
    repeatability (tens of µm) + the pose-to-dial model.
- **R2 — a guided hand.** No dock. The gun floats on the carrier, and a small
  display (LED bars, or a phone on the post) shows the live error on each of the
  scene's axes and on the dot's position. The hand brings it to zero and holds. This
  is the digest's uncovered direction "the hand kept as the actuator, with a guide
  making it repeatable". It suits training, tacks, and an unknown process window.
  Its error is how still a weightless, guided hand stays; Derek's own recorded
  spread is the benchmark.
- **R2b — lock where the hand stops.** Holding electromagnets (uxcell 24 V 100 N,
  Prime) on each carrier joint clamp a steel disc when the bars read zero. This is
  the weakest meaning:
  - lock-shift as the magnet pulls the disc;
  - a soft chain of five or six joints;
  - the CG bail must be locked too.

  It is kept because it needs no dock.
- **R3 — motors.** The dock's X and Z (then the angles) go on steppers that drive to
  the recorded numbers and replay a per-tube runout map (who-moves-what's 3b).
  Derek's automated vision starts here: the AI starts from his demonstration
  instead of from nothing.

## Surviving a tube change and a second person

- **Tube change.** The record lives in the joint frame. Rim to the flag, then R1 or
  R2. Tube length and seating drop out; runout is either tolerated (R1) or replayed
  (R3).
- **Second person, R1.** Load the recipe, fit the printed block, set two dials,
  carry with pins in, dock, compare the live dot with the recorded image, weld.
  **R2:** follow the bars by hand; their own record is then comparable with Derek's.
- **Every dock is a calibration event.** The docked pose is known from the recipe,
  so the pose camera is re-checked each time the gun seats.

## Trying to break it

**F1 — the pose-to-dial model (biggest open problem).** Turning a recorded shell
pose into dial numbers needs the dock's kinematics and the dot's position in the
shell frame: the scanned gun plus a measured dot-to-shell relation (focus,
red-light centring). Until then, R1 replays by iteration: set from the record, dock,
compare with the recorded dot image, trim, and record the trims. The trims teach
the model.

**F2 — cameras in the weld light.** Record dry laps primarily. During real welds the
puddle and the 1080 nm reflections swamp tags. Use tag lighting (narrowband LEDs)
with the red long-pass filter, short exposures, and lean on the IMU and console for
the weld's own record. *Leaves:* whether tags survive a real bead at all.

**F3 — the hand fights the umbilical; the dock doesn't.** The taught pose includes
the hand's reaction to the cable torque. R1 reproduces the pose, not the forces, so
that doesn't matter. R2 inherits it.

**F4 — the taught pose may not be dockable.** Some taught angles fall outside the
lid or dock escape range (for example, slide-yaw beyond −25°). The validator
catches it, and the answer is a rotation-yaw block rather than a slide.

**F5 — how steady can a guided hand be (R2)?** Unknown. The first teaching sessions
measure exactly this, which is itself the most useful number for choosing between
R1 and R2.

**F6 — timing replay.** The rig's rule is that nothing takes the table away from
the operator. Replaying "stop at 380°" is therefore a cue, not a limit: a proposed
firmware beep at the recorded angle, or the overlap pointer (kit K4).

## Branches

- **F0 — record today's practice first.** No carrier: an AprilTag plate and IMU on
  a shell, one camera and the console, while Derek welds exactly as now. It is the
  cheapest measurement in the study, and it tells everyone what "good by hand"
  actually is.
- **F-d — digitizer linkage.** A separate, light, passive five-joint printed linkage
  from the station to the shell with AS5048A 14-bit encoders (Prime, "0.05°"
  claimed). It carries no weight, because the carrier does, and it measures pose
  where cameras struggle (weld light). ~0.3 mm RSS at the dot for 0.03° joints on
  250 mm links, or ~1 mm with calibrated 12-bit AS5600s. It clips on and off the
  shell.
- **F-j — encoders on the carrier's own joints** (AS5600, the idea-E branch M3).
  They give only the CG position, because the bail decouples orientation. Cheap,
  but not a pose.

## Parts (see `../../../sourcing/sequence-of-use.md`)

- BNO085 IMU breakout (Prime, $20.49, 100+/month).
- AS5048A 14-bit encoder (Prime, $14.24; few ratings) and AS5600 (recorded).
- uxcell 24 V 100 N holding electromagnet for R2b (Prime, $9.99, low stock).
- M8 pull-ring index plungers for carry pins (Prime, $8.99 per 6).
- ELP 16 MP camera (on hand; a second for the pose view).
- Printed AprilTags, tag plate, and the presser microswitch.

## What it connects

- **machine-that-learns:** the observation layer's joint camera and its teach-arm
  note.
- **who-moves-what / one-knob-one-parameter:** printed recipe blocks, now generated
  from a demonstration.
- **My ideas E and A-r, and borrowed-ecosystems' E:** the carriers and docks that
  R1 replays into.
- **who-moves-what 3b:** the runout map that R3 replays.
- **Derek's automated vision:** it starts from his demonstration.
