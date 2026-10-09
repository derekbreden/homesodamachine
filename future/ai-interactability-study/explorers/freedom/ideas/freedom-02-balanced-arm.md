# freedom-02: the monitor arm as the weight path, a vernier stage as the location path

Scene: `scenes/freedom-02-balanced-arm`. Origin: Derek's example (the monitor arm). Depth: worked deeply (six break-and-repair entries). Numbers from `calc/20-balanced-arm.js` (the scene's model) and `calc/21-arm-numbers.cjs`; parameters **illustrative** unless tagged.

## Picture it

A desk monitor arm bolted to the bench edge, gas spring in its lower link, holding the gun and its cable so that they feel weightless. Where a monitor would hang, a small XZ stage carries the printed shell. The arm does not know where the dot is and does not try to: it carries. The stage moves the gun a few millimetres, and a camera on the dot tells the stage where to go.

## The proposal

Derek [Derek]: a monitor arm is "too flexible" is a starting observation, and the question is what it carries, what it locates, where the reference is, and what else supports or drives the gun. The answer proposed here is a **division of the task by load path and location path**:

- **Weight path**: the gas-spring arm cancels the gun's weight (and, optionally, the cable's). It is a *neutral-equilibrium* support: with the spring balancing the payload in a range of poses, any pose in that range is nearly a resting pose, and joint friction alone keeps it there. It is moved by hand, or by a small motor because gravity is already cancelled.
- **Location path**: an XZ (or XYZ) vernier stage at the arm tip, ±10 mm, closed on a camera looking at the dot. The arm's job is to bring the vernier within its reach.

## What carries the loads, what establishes position, what is free or restrained

- **Weight and cable**: spring and arm; friction holds the residual.
- **Position of the dot**: not the arm. The vernier and the camera. The arm sets the neighbourhood (±10 mm).
- **Free**: the arm's angle inside the friction window (moves by hand or a small motor); the swing about the column.
- **Restrained**: by friction only while the residual torque stays inside the window; outside it the arm creeps to the nearest angle where it sticks, or to a stop.
- **Driven**: vernier X and Z; optionally a shoulder motor.
- **Changes over time**: friction can be raised by a brake for the weld (a state); the motor holds, or is released.

## What software could command, observe, and what stays manual

- **Command**: vernier X, Z; the shoulder motor angle in the motor branch; the brake.
- **Observe**: the dot by camera (the arm itself cannot tell: pre-sliding hold error is millimetres); the shoulder angle by encoder (it tells where the arm settled); the payload by a load cell in the vernier (does the spring match?).
- **Manual or unresolved**: choosing and tuning the spring; ballasting the shell; clipping the cable.

## What was tried to break it

**Entry 1. "A monitor arm is too flexible."**
- Conflict: with the illustrative pre-sliding stiffness (40 N·m/rad per joint) a 2 N change in cable pull moves the tip about 10 mm even with the brake engaged (0.9 N·m / 40 N·m/rad × 450 mm).
- Assumption: the arm must locate the gun. It does not; it carries it.
- Change: the vernier (±10 mm) and a camera do the locating; the arm's hold error becomes the vernier's range requirement, not the weld's tolerance.
- Leaves uncertain: real friction and pre-sliding stiffness (never measured); whether a camera can close the loop through the geometry (that is for the seeing explorers).

**Entry 2. The payload is below the spring's minimum.**
- Conflict: the off-the-shelf gas-spring arms read for this study are rated from 4.4 lb (2 kg) upward (HUANUO FlowLift 4.4 to 19.8 lb; Amazon Basics 4.4 to 15.4 lb; both in [sourcing](../../../sourcing/freedom.md)). A 1.2 to 1.5 kg gun and shell is under that floor: the spring wins and, with the illustrative numbers, 1.5 kg on a 2.0 kg setting leaves 2.2 N·m of net torque against 0.4 N·m of friction: the arm rises to its stop.
- Assumption: any monitor arm will do.
- Change: ballast in the shell (0.5 kg here: window from none to −13° to 24°), a lighter spring (a tool balancer rated 0.5 to 1.5 kg fits, sourcing), or a different arm.
- Leaves uncertain: whether a monitor arm's spring can be tuned down below its rating (the listings say "adjustable tension" but not how far).

**Entry 3. The window: where the arm stays put.**
- Conflict: balance is exact at one angle (5° here) and drifts by an error slope (0.15 per radian) elsewhere. With 0.4 N·m of friction, a matched 1.5 kg payload holds between −19° and 32°; raise the error to 0.4 per radian or drop friction to 0.1 N·m and the window narrows to −4° to 14° or −1° to 11°.
- Assumption: a balanced arm stays where it is put anywhere in its travel.
- Change: hand-place inside the window; choose or tune an arm whose balance error is small over the working range.
- Leaves uncertain: the real balance error of a gas-spring arm at 1.5 kg (probably the arm's design geometry is optimised for a higher payload).

**Entry 4. Cable on the arm.**
- Conflict: clipping the umbilical along the arm passes only part of its pull to the gun (25% here) but adds cable weight (0.35 kg) that the spring must also cancel: with a spring matched to the gun alone the arm sinks to its stop.
- Change: re-match the spring to the payload including the cable share; the real fraction is unknown.
- Leaves uncertain: the cable's weight and stiffness ([unknown]); whether the arm's cable channel accepts a QBH umbilical with a 350 mm emitting bend radius [manual p. 20].

**Entry 5. The brake widens the window but does not stiffen the tip.**
- Conflict: a brake at 20× friction makes the window cover the whole travel with a 2 N load change, but the pre-sliding deflection remains (10 mm here).
- Assumption: locking makes it rigid.
- Change: keep the vernier and the camera; the brake is for holding weight, not position.

**Entry 6. A small motor is enough because of the spring.**
- Conflict/opportunity: at the design pose the shoulder torque needed to *move* the arm is 0.40 N·m with the spring against 6.99 N·m for the same 1.5 kg on an unbalanced boom (450 mm reach), 17 times less. A small stepper with a reduction (the STEPPERONLINE 5:1 geared NEMA 17 in sourcing) is the right size class; whether its output torque at the shoulder covers 0.4 N·m plus margin was not checked.
- Assumption: a robot arm has to be strong because the gun is heavy.
- Change: gravity compensation instead of torque.
- Leaves uncertain: motor availability and precision at the shoulder (a hobby geared stepper has backlash), and that a motor doubles what the brake state must do.

**Entry 7 (wave 3, from borrowed's exchange, section 1). The window in kilograms. Decision: revised (scene readout added).**
- Conflict: entry 3 draws the window in degrees and never says what it forgives in mass. The arm stays put while the payload and the spring's setting differ by less than friction / (g L cos θ): 0.4 N·m over 0.45 m at 5 degrees is **±91 g**; ±51 g at a reach of 0.8 m; ±455 g at 2 N·m; ±1.82 kg with the brake (8 N·m). Re-run in `calc/37-arm-window-kg.cjs`: borrowed's figures are right.
- Assumption: a balanced arm stays where it is put anywhere in its travel, and "roughly balanced" is good enough.
- Change: the scene gained the readouts "Mismatch forgiven: free / braked" and "Payload vs spring setting" (in grams) and a badge when the difference is outside the tolerance. A monitor arm is designed for a payload that never changes and is set once with a hex key; here the setting is being asked to be right to a tenth of a kilogram, and the friction that lets it stay is the same friction that sets the tolerance.
- Leaves uncertain: real friction and reach (never measured). Push the tip of a monitor arm or a mic boom with the Newton meter at 0.5, 1 and 2 N and note how far it gives and whether it stays.

**Entry 8 (wave 3, from borrowed's exchange, section 1). Everything on the tip is payload. Decision: revised.**
- Conflict: entry 2 counted the gun, its shell and a share of the cable (1.5 kg) and found the payload under the 2 kg floor of monitor arms. The idea also puts an XZ vernier (two mini rails and motors, about 0.6 kg) and a camera (about 0.15 kg) on the tip: gun 1.2 + vernier 0.6 + camera 0.15 = 1.95 kg, and 2.3 kg with the cable's 0.35 kg share. The floor is met by the parts, the 0.5 kg ballast of entry 2's repair is already there, and what is not met is the ±91 g. Neither the vernier's nor the camera's weight is on any listing (illustrative).
- Assumption: the payload is the gun and its shell.
- Change: the scene's group "Payload counted from parts" (off by default, so the original 1.5 kg reading stays) sums the parts; with them, a gas-spring window matched to the payload narrows: -19 to 32 degrees at 1.5 kg, -13 to 25 at 1.95, -10 to 21 at 2.3, because the error torque scales with the payload. borrowed-14 (a branch of this idea) draws the same with three springs, including a zero-length one that balances at every angle, and the strip of bought arms rated 0.25 to 9 kg.
- Leaves uncertain: whether a monitor arm's spring can be tuned to a payload near its rating's lower end; weigh the gun in its shell, the vernier with its motors and the camera (a kitchen scale to 25 g).

**Entry 9 (wave 3, from borrowed's exchange, section 1). What changes the payload while the arm is used, and the state sequence. Decision: revised, with two things left standing.**
- Conflict: the fibre's share on the arm changing by a quarter is 88 g, all of the ±91 g. The vernier's own travel changes the shoulder torque: moving the 1.2 kg gun 10 mm along the arm is 0.118 N·m, 29 % of the 0.4 N·m band, before the cable does anything. borrowed asked whether the sequence is release, place, brake, weld, and what the mismatch is between placing and welding.
- Assumption: the payload is constant once set.
- Change: yes, that is the sequence. The mismatch that matters between placing and welding is not in mass: it is the force step when the hand lets go (its own holding force, the fibre settling to where its clip point puts it) and at bead start. After the brake those steps are held (1 N at the tip is 0.45 N·m, 6 % of the 8 N·m brake) but not stiffened: pre-sliding lets the tip give 5 mm per newton (40 N·m/rad), which the vernier and the eye take up. The brake removes creep, not deflection. The scene shows the vernier's torque share and the tolerance in both states.
- Left standing: (1) the scene is one joint in a vertical plane; a monitor arm has two swivels with no gravity torque whose pre-sliding decides the yaw of the shell, and a yaw about the vertical moves the dot radially by lever times angle (freedom-04): the vernier closes on position, and the orientation the swivels hold is not observed by it. (2) The rating of a bought arm says nothing about balance error, friction, reach or tip stiffness.

## Branches and combinations

- Motor variant: the scene's "shoulder motor" branch.
- With freedom-05: the vernier follows the runout table (same actuator).
- With freedom-01: the arm can also carry the ring supports; the suspension then only needs to manage the cable.
- With freedom-06: a brake at each joint is the lock-and-release arm.

## Unresolved problems, and questions that need Derek's observation

- Weigh the gun and the cable share; pull the umbilical with a spring scale at the working pose. Weigh the vernier stage with its motors and the camera as well (entry 8).
- Push the tip of a monitor arm or a mic boom with the Newton meter at 0.5, 1 and 2 N and note how far it gives and whether it stays (friction and pre-sliding, entry 7).
- Try a monitor arm on the bench with a 1.5 kg dummy load: at which angles does it stay put? (No purchase required to know the rating floor: listings state it.)
- Camera view of the dot through the bore geometry: is it visible at all? (See the reference scene's line-of-sight inset.)

## Assumptions

- Arm 450 mm, single balanced joint; exact at 5°; error slope 0.15/rad; friction 0.4 N·m; pre-sliding 40 N·m/rad; brake ×20; cable on arm +0.35 kg and 25% of the pull; motor 1.0 N·m: **illustrative**.
- Payload 1.5 kg; gun mass **[unknown]**.
- Monitor-arm ratings: observed on the Amazon listings 2026-09-28 (sourcing).

## Sourcing pointers

`sourcing/freedom.md`: HUANUO FlowLift single arm ($35.99, 16,507 ratings, "4K+ bought"), Amazon Basics gas-spring arm, spring balancers 0.5 to 1.5 kg, NEMA 17 with 5:1 gearbox, mini linear rail (vernier), XYZ manual stage.

## Scene

`freedom-02-balanced-arm`.
