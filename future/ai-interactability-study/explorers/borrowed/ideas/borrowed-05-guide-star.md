# borrowed-05-guide-star: calibrate the trim axes by nudging and watching the dot

Origin: swarm (borrowed from amateur astronomy). Maturity: developed. Scene: `scenes/borrowed-05-guide-star/index.html` (a simulation). Numbers: `calc/guide_star_sim.py`.

## Picture it

A small camera looks at the corner. Software wiggles each of two little trim axes forward and back by a few steps, watches how far the red dot moves in the image, and out of that solves a two-by-two matrix and how much slack each axis has. Then it keeps the dot on the seam target by measuring, inverting the matrix and stepping, while the tube's runout and slow drift try to pull it away. Nobody told it how the camera was rolled or how big a step was.

## The proposal

An autoguider brings up an unknown telescope mount without kinematics: nudge, watch the star, fit, guide. The dot is the star, the seam the target, and any two small motions (the frame trim of borrowed-01, a gantry axis of borrowed-02, the swing offset of borrowed-06) are the mount. The wall's known 1.65 mm thickness in the image is the scale bar. This is a control method and a bring-up procedure for an AI, not a mechanism.

## What carries loads, establishes position, is free or driven

Not a mechanism. Position reference: the target pixel (the seam, where the camera says it is) plus the wall thickness for scale.

## Software: command, observe, manual

- Could command: nudge axis A or B by n steps; guide steps from the inverse matrix; calibration once per setup.
- Could observe: the dot centroid per frame (noise included); the wall thickness in pixels; the fitted matrix, backlash and scale.
- Stays manual: mounting the camera to see the corner; the axes existing; anything the camera cannot see.

## What was tried to break it

1. **Guide before calibrating.** Conflict: a loop that assumes the camera is aligned with the axes rotates every correction by the true roll. Assumption: axes and camera are aligned. Numbers (calc/guide_star_sim.py, 60 s run, runout on, drift 0.3 mm/min, noise 0.6 px, gain 0.6; simulated, illustrative): at 45 degrees of roll the naive guide sits at 0.04 / 0.05 mm RMS, at 65 degrees 0.55 / 0.68 mm, at 75 degrees it runs to the end stops; the calibrated guide sits near 0.03 / 0.02 mm at every roll. Change: calibrate first (about 10 simulated seconds). Uncertain: everything about the plant is idealised.
2. **Backlash.** Conflict: the first steps after a reversal move nothing. Numbers: at the defaults (0.1 to 0.2 mm of slack) compensation makes no measurable difference; at 12 steps of 0.05 mm with runout on, vertical RMS is 0.043 mm without it and 0.018 mm with it. Change: measure the slack from a reversal in calibration and add it when the direction flips. Left standing: real backlash is not a clean dead zone.
3. **Scale.** Conflict: pixels are not millimetres. Change: the wall thickness in the image; at 24 px/mm it is 40 px wide, but at a wide field of view it may be two or three pixels, so the scale is only as good as a pixel is a fraction of 1.65 mm. Uncertain: whether the wall edge can be seen at all.
4. **Disturbances.** Slow drift and the tube's runout (period 48.6 s at 8 mm/s, [derived from the rig speed]) are slower than the loop and are rejected; vibration, the gun's 80 Hz swing and any disturbance faster than the frame rate are not.
5. **Gain.** With the naive matrix a higher gain is worse, not better (gain 0.2: 0.10 mm; 0.8: 4.0 mm at 65 degrees, no runout).

## Branches and combinations

- Combination candidate with borrowed-06-swing-offset (the one-axis version) and borrowed-01 / borrowed-02 (two-axis trims).
- Transferable: nudge-and-watch calibration; backlash from a reversal; a fixed feature as the scale bar; the guide loop.

## Unresolved problems and questions that need Derek

- What the camera actually sees of the dot in a 6.35 mm deep corner (the eyes and datum explorers' question).
- Whether the trims sit on a rotating part (then the camera-to-axis angle changes with rotation).
- Questions for Derek: none for observation; a webcam pointed into the corner with the red dot alone (gun's pilot only, no laser) would say whether a centroid is possible.

## Assumptions

- All parameters illustrative: 24 px/mm, 0.02 and 0.03 mm/step, backlash 4 and 6 steps, noise 0.6 px, drift 0.3 mm/min, 65 degrees of roll, end stops at +-6 mm.
- Runout amplitude is half the rig-doc TIR limits (0.25 / 0.30 mm) [repo]; period derived from 8 mm/s at r = 61.85 mm.
- PHD2's calibration procedure is described from general practice; its manual pages could not be retrieved, so the specifics are unchecked (sourcing/borrowed.md).

## Sourcing pointers

sourcing/borrowed.md: Arducam OV9281 mono global-shutter USB camera ($49.99, Prime, 100+ bought); PHD2 not sourced.

## Scene

`borrowed-05-guide-star`
