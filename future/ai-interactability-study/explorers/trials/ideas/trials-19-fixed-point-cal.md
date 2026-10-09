# trials-19-fixed-point-cal: one cross, many orientations

Scene: `scenes/trials-19-fixed-point-cal/index.html` (developed). Origin: combination of `borrowed-03-encoded-arm`, `borrowed-02-gimbal-on-gantry` and `trials-05-artefact-ladder` (rung 1), using the method of `trials-13-pivot-calibration`. Exchange: `exchange/trials--on--borrowed-w2.md`, sections 1 and 2. Calc: `calc/arm_touch_cal.py`, `calc/gimbal_fixed_point.py`. Sourcing: `sourcing/trials.md`, wave 2 (14-bit encoders).

## Picture it

A printed board with one cross sits at plate-face height on the rotator. A hand holding the encoded arm's gun (or, in the other branch, a gimbal and gantry running by themselves) puts the red dot near the cross in forty different orientations. For each, the camera above the board reads where the dot landed and the software logs six joint angles (or the commanded angles). The arm's own idea of where the beam met the board should be one point; the spread is its error. The plot shows that spread before and after a least-squares fit, on poses the fit never saw.

## The proposal

Any arrangement that reports its own pose carries an error the arrangement's makers cannot remove: encoder zeros and per-turn linearity error, link lengths, where the gun sits in a cradle. Most of it repeats from touch to touch. Putting the beam on one fixed point from many orientations turns that repetition into a calibration, the pivot calibration of `trials-13` with the arrangement's own pose in place of a tilt about a supposed pivot. Two branches, one method:

- **Encoded arm** (borrowed-03): 28 numbers fitted from about 40 touches: per-joint zero and one cosine and one sine of linearity error (18), two link lengths and the wrist offset (3), where the beam leaves the gun and its tilt (4), the camera-to-arm shift (2), the board height (1). The hand does not need to be accurate; the camera reads where the dot fell.
- **Gimbal and gantry** (borrowed-02): the formula `C = J + t g(v, h)` assumes C sits at t along the roll line in the gun's frame. A cradle error of 3 numbers, gimbal angle zeros (3), the board height and the camera shift (3) are fitted from 20 to 40 orientations the gantry runs by itself; software runs it unattended.

## What carries the loads, what establishes position, what stays free

Not the subject. The arm's spring or the gantry carries the gun; the board (rung 1 of `trials-05`) sits on the rotator and carries nothing. Position is established by the cross and the camera. The result is a correction to the arrangement's own numbers, valid for a session.

## What software could command, observe, and what stays manual

- Command: the arm branch, nothing (a list of orientations is shown to the hand); the gimbal branch, the angles and the gantry move for each touch, then the fit.
- Observe: the dot's board xy per touch (camera A); six joint readings or the commanded angles; the spread on held-out poses.
- Manual: placing the board and camera; the hand moving the arm; re-running after a bump.

## Tried to break it

1. **What the fit removes (arm).** Numbers: dials varied plus or minus 15 degrees about the opening pose, linearity error 1 degree, zeros up to 0.3 degrees, links off by up to 2 mm: 1.5 mm rms after a one-point touch-off (0.5 to 0.7 at plus or minus 5, 2.6 to 2.7 at plus or minus 25). After a fit on 100 touches: 0.03 mm (16 bit, no play), 0.28 (12 bit, 0.01 degrees of play), 0.32 (16 bit, 0.02 degrees), 0.79 (16 bit, 0.05 degrees). Assumption behind the idea: over a working window an encoder's per-turn error looks like an offset and a gain. What it leaves: the model is matched to the truth, so the best case; unmodelled harmonics and a leaning post cost at most 0.06 mm more in calc; real error unknown.
2. **The floors.** Quantisation (0.088 degrees per count at 12 bit is 0.28 mm at these lever arms; 14 bit 0.10, 16 bit 0.03) and play the encoders cannot read (0.02 degrees is 0.3 mm). Leaves: the play of a real monitor-arm joint is unknown.
3. **Window and touches.** 20 touches give 0.43 mm, 40 give 0.34, 100 give 0.32. Fit at plus or minus 10 and use at plus or minus 25 and the error is 1.2 mm against 0.34 fitted at plus or minus 25. Leaves: nothing; the touches must span the use.
4. **The gimbal formula's silent term.** 1 mm of cradle error costs 0.19, 0.37 and 0.54 mm rms at plus or minus 10, 20 and 30 degrees (worst 0.35, 0.70, 1.0), against 0.17 mm for 0.05 degrees of angle error (the only error borrowed-02's sliders show). The fit finds the two components across the beam to 0.05 mm from 20 poses (camera 0.05 mm); fresh-pose error falls from 0.43 to 0.018 mm. Leaves: 0.15 mm camera noise needs 40 poses for 0.11 mm.
5. **The component along the beam is invisible.** It moves the nozzle along its own beam and the spot does not move. Change: none for a board; spot size (`trials-03`) is its sensor. It matters for focus and the wire, not for where the beam meets the seam.
6. **Drift.** Joints settle, a gantry gets bumped; the calibration is per session. Change: a kinematic seat that the arm or gun returns to (`trials-02`) as the cheap zero check. Leaves: how often.

## Branches and combinations

- Joins `borrowed-03` and `borrowed-02`; its board and cross are rung 1 of `trials-05`; its method is `trials-13`.
- The pointer of `trials-18` supplies the same fixed point without a hand: a steered dot at a known place.
- Feeds `trials-11` (the arm as the yardstick's recorder), `trials-04` (the coach can be told the seam per angle), `trials-17` (session calibration id on the card).

## Unresolved, and questions for Derek

- Q: the play in the joints of the arm, under 1 kg at a 500 mm lever (push at the wrist with a dial gauge across the joint); and the gun's mass and centre of mass.
- Whether camera A can read a dot on a matte board to 0.05 mm; on polished steel it is a different question (`eyes`).
- Whether a cross-and-camera calibration done laser-off holds with a laser-on hand.

## Assumptions

The arm is borrowed-03's (post 260 mm, links 260 + 260, wrist centre 150 mm behind the tip) with a random truth (per-joint phase, amplitude 0.5 to 1 times the slider, random-sign zeros, links off up to the slider); hand scatter 0.3 mm, standoff scatter 2 mm, camera noise 0.05 mm, play, cradle error and gimbal angle zeros are sliders **[illustrative]**. The scene runs a JavaScript port; the Python scripts are the independent check (same structure, different random draws).

## Sourcing pointers

`sourcing/trials.md`, wave 2: AS5047P and AS5048A 14-bit modules ($11.99 to $14.99, thin ratings) against AS5600 12-bit ($9.99, 41 ratings, 100+ a month).

## Scene

`trials-19-fixed-point-cal`
