# freedom-09: observe only (a pose logger on a hand-positioned floating gun)

Scene: shown as the *sense* branch of `scenes/freedom-03-cable-platform` (no separate scene yet). Origin: swarm original (from the freedom framing). Depth: sketch with numbers (from that scene's model).

## Picture it

Nothing in the arrangement moves by itself. The gun is in its shell, carried by something passive (a balancer, the ring-and-bungee suspension), and Derek positions it by hand. Six thin lines run from the shell to a frame, each ending on an encoder that reads how much line has been drawn out. A screen shows the dot's position against the seam. Software does nothing to the machine; it watches and writes down.

## The proposal

The smallest *software observes and moves nothing* arrangement: six draw-wire encoders (a spool, a return spring and a magnetic angle sensor) on the shell's lugs, a camera on the dot, and the rotator's own angle count. From six lengths, forward kinematics gives the gun's pose; from the camera, the dot. Every hand-positioned attempt is logged as a pose, a dot position and an outcome (the weld observed afterwards). What an AI can do with it: correlate the pose the hand used with the result, then say what to change ("pull the tail down 3 mm", "the dot sits 0.4 mm too far in"). The same six lugs and lines are the first stage of freedom-03: the encoders can be replaced by winches later without touching the frame.

## What carries the loads, what establishes position, what is free or restrained

- **Weight**: not the lines: a balancer or suspension carries it. The encoders' own return springs, if they are 2 N each, carry about 72% of it (net 8.9 N up) and pull the gun sideways a little (0.4 / 2.4 N).
- **Position**: the hand, then reported by the lines.
- **Free**: the gun in all six degrees, held only by the support's compliance and the encoders' spring tension.
- **Driven**: nothing.

## What software could command, observe, and what stays manual

- **Command**: nothing (the existing rotator controller, if desired).
- **Observe**: six line lengths (0.05 mm resolution with a 12-bit magnetic encoder on a small spool: about 0.015 mm of line per count on a 20 mm spool [derived]); pose by forward kinematics; the scene's layout gives dot uncertainty of about 0.09 / 0.06 / 0.07 mm (radial / tangent / vertical) for a 0.05 mm length step at a pose 4 / −3 / 2 mm from the reference; the camera; rotator angle.
- **Manual**: everything else: positioning, running the weld, judging it.

## What was tried to break it

**Entry 1. Measuring loads what is measured.**
- Conflict: six 2 N return springs pull the gun with a net 8.9 N and a torque, and change with the pose.
- Assumption: sensing is free.
- Change: use it as part of the support; calibrate it out (the net force is a function of pose and computable); use weaker return springs.
- Leaves uncertain: the real return force of a home-made or bought encoder (the CALT listing does not state it).

**Entry 2. Geometry decides the accuracy, not the encoder.**
- Conflict: a 0.05 mm quantisation becomes 0.06 to 0.09 mm at the dot here; a narrower frame spreads the lines less and worsens it (freedom-03 entry 4).
- Change: a wider frame; finer encoders (0.005 mm is easy).

**Entry 3. It observes the gun, not the seam.**
- The lines say where the shell is relative to the frame; the seam belongs to each tube. The camera is what ties them together; calibration of the frame to the rotator is manual.

## Branches and combinations

- Stage 1 of freedom-03.
- With freedom-05: the logged dry-run gives the runout table.
- With freedom-02 or freedom-01: the passive support.

## Unresolved problems, and questions that need Derek's observation

- Is a hand-positioned gun with a screen enough to teach anything? Try it before building.
- Frame-to-rotator calibration.

## Assumptions

- Encoder resolution 0.05 mm, return force 2 N: **illustrative**. Geometry: freedom-03's layout (illustrative). Gun 1.2 kg (**[unknown]**).

## Sourcing pointers

`sourcing/freedom.md`: AS5600 3-pack ($7.99, 70 ratings, "100+ bought"), CALT draw-wire encoder for comparison ($118, 6 ratings), UHMWPE cord, load cell.

## Scene

Sense mode of `freedom-03-cable-platform`.

## Wave 2 (after the exchange with eyes)

- **Tags instead of draw-wire encoders** (eyes-03): the six encoders' return springs pull the gun with a net 8.9 N (entry 1); tags load nothing. The trade is eyes-03's 0.14 to 0.21 mm at the dot (cube 40 to 80 mm behind the tip, two cameras) against this idea's 0.06 to 0.09 mm from encoders, and a place on the barrel the camera also wants. Not drawn.

**Wave 3 note (from borrowed's exchange, "smaller remarks"). Decision: answered (a note).** The pose logger and the nudge box (freedom-10) are sold as one product for two of the rotations: a Sky-Watcher AZ-GTi ($525, 117 ratings, two-day, Prime) has motors and output-shaft encoders that follow a hand slew ("Freedom Find dual encoders ... manual slewing without losing alignment"), a 5 kg rating, a Wi-Fi interface and a public command set on UDP 11880 with open Python and INDI drivers (search summary, unchecked); a step of 0.625 arcsecond is 0.0008 mm at a 250 mm lever. It has to be balanced, its pivot is not the dot, and backlash and periodic error are on no listing. `borrowed-17-positioner-shelf` puts it beside the other bought positioners.
