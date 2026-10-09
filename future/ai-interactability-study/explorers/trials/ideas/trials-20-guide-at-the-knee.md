# trials-20-guide-at-the-knee: half a dot

Scene: `scenes/trials-20-guide-at-the-knee/index.html` (developed). Origin: branch of `borrowed-05-guide-star`, with the visible fraction of `trials-03-dot-touch-probe`. Exchange: `exchange/trials--on--borrowed-w2.md`, section 4. Calc: `calc/guide_at_knee.py`.

## Picture it

The guide camera looks at the corner from above. The red dot creeps toward the seam: the plate part is red, the part that has crossed onto the wall vanishes behind the wall. A crosshair marks the seam pixel and the loop pulls the dot's centroid toward it, but the centroid never gets there: it stalls and the loop hunts at the edge of visibility, half a spot into the wall. Switch the loop to the visible fraction with a target of 50 per cent and it settles on the seam and stays.

## The proposal

Borrowed-05 guides the dot's centroid to the seam pixel with an astronomy-style nudge-and-watch calibration. At the seam the dot is clipped: from above only the plate part is seen. For a dot of width w along r, the centroid of the visible part moves at slope 1 while the dot is wholly on the plate, 1/2 while it straddles the seam and 0 once it has gone. The **visible fraction** falls smoothly over one dot-width and equals 50 per cent exactly when the dot's centre is on the seam, for any dot size. So: approach with the centroid, close with the fraction, calibrate on the plate side.

## What carries the loads, what establishes position, what stays free

Not a mechanism; the axis is whatever the arrangement provides across the seam (the trim of borrowed-01, a gantry axis of borrowed-02, the pointer of `trials-18`, the swing offset of borrowed-06). The seam is the reference: its edge hides the dot.

## What software could command, observe, and what stays manual

- Command: axis steps (nudge, then loop), calibrate here, guide with centroid or fraction.
- Observe: the centroid of the plate part, the visible fraction (integrated intensity against the full-plate value), star lost.
- Manual: mounting the camera to see the plate side of the corner; having the axis.

## Tried to break it

1. **A centroid target at the seam pixel is unreachable.** Numbers from the scene (0.5 mm dot at 32 degrees, footprint 0.59 mm; centroid noise 0.025 mm; drift 0.3 mm/min): the loop settles 0.26 mm into the wall on average, rms 0.26 mm, out of sight 6 to 11 per cent of the time (scene; `calc/guide_at_knee.py` reproduces it). Assumption: the dot is a star, visible on both sides of the target. Change: the target becomes the 50 per cent point. Leaves: the real dot is a soft round spot on a wall seen at an angle.
2. **Calibrating across the seam.** Nudged from 0.3 mm short of the seam the centroid slope reads 0.53; from 0.5 mm short 0.73; from 0.15 mm short the star is lost and the calibration fails. The guide divides by that slope, so gain 0.6 becomes about 1.1. Change: calibrate one dot-width short of the seam. Leaves: none.
3. **The fraction loop.** Ideal edge, fraction noise 0.02, axis step 0.02 mm: mean 0.005 to 0.009 mm and rms 0.009 to 0.011 mm from the seam over 30 s. Assumption: the fraction curve is as drawn. Leaves: the real curve has soft ends, so the loop's noise and gain need retuning; the reference brightness changes with height and incidence.
4. **The scale bar.** Borrowed-05 takes scale from the wall's 1.65 mm in the image, which is the rim top, 6.35 mm above the seam. Off the axis by an angle, the seam foot and the rim's inner edge are 6.35 tan(angle) apart: 2.1 mm at 18 degrees, and the scale differs by about 2 per cent. Change: take the target and the scale from the seam foot. Leaves: not drawn.

## Branches and combinations

- Branch of `borrowed-05-guide-star`; uses `trials-03-dot-touch-probe`'s fraction and knee.
- On the pointer of `trials-18`: the pointer is the axis and the knee is what its sweep finds; the same 50 per cent target is the label "on the corner".
- Camera B (the wall spot) could hold the same point from the wall side.

## Unresolved, and questions for Derek

- Q: photograph the dot at the corner with a phone at the working angle, once with the dot 1 mm short of the wall and once on the seam: is the visible part clean, and does it fade or cut?
- Whether the camera can see the plate part of the dot right up to the seam without the wall's own reflection confusing it (`eyes`).

## Assumptions

Dot diameter 0.5 mm, footprint 1/cos 32 degrees longer along r, sharp edge, centroid noise 0.025 mm, fraction noise 0.02, axis step 0.02 mm, drift 0.3 mm/min, gain 0.6, loop every 0.5 s **[illustrative]**.

## Sourcing pointers

None (a camera as in `trials-03`).

## Scene

`trials-20-guide-at-the-knee`
