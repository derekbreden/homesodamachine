# trials-24-calibration-graph: what the loop keeps calibrated, and what leans on what

Scene: `scenes/trials-24-calibration-graph/index.html` (developed; a lens). Origin: new, from the framing, in the new direction "calibrating the observation itself"; takes four arrangements from other explorers. Combines `trials-19-fixed-point-cal`, `datum-19-plate-as-target`, `trials-05-artefact-ladder`. Calc: `calc/eye_ledger.py`.

## Picture it

Twelve boxes in three columns: the eye (lens, exposure, camera pose, judge, clock), the arrangement and the rotator (rotator, approach, the arrangement's geometry, the dot in the gun), this tube (seat, seam, dot against the melt). Arrows say what leans on what. Press "camera knocked": the pose box turns red and everything read through it turns amber. Press "run the next trial in order" and the boxes clear from the eye downward; run a downstream box first and it comes out purple, done on a stale eye. Beside the graph, six readings the loop makes and what each leans on; below it, a table of what a scale error, a camera move, a pointing change and a delay cost each reading.

## The proposal

An AI that runs trials for days keeps a **ledger of calibrations**, and they lean on each other: the arrangement's geometry is fitted from where the camera saw the dot land on a board (`trials-19`, `eyes-13`), so it inherits the camera's scale and pose; the dot's place in the gun is found by moving the arrangement (the pivot trial), so it inherits that; the seam on this tube inherits all of them. A calibration made while something upstream is wrong **inherits the error silently**: the fit absorbs it and no residual says so.

Three ideas hold the ledger together.

1. **Stale and suspect are different.** An event makes some calibrations *stale* (the value is known to be wrong: needs a full trial) and everything that leans on them *suspect* (the value may still hold: needs a cheap check first). A check costs seconds (a golden dot, the rim-and-ports fit that runs on every frame, a coupon's knee against its stored value, one sweep pair); a trial costs minutes. The loop wants the cheapest route that leaves everything trustworthy.
2. **Order matters.** Run in dependency order, upstream first, or the result is *tainted*: it will have to be redone. The scene shows it.
3. **Readings differ in what they lean on.** A reading made against something in the same picture does not lean on the camera's pose: the knee (the seam foot is in the frame, zero apart) leans on exposure, the judge, the approach and the clock, and not on the lens or the pose; a reading against the rim edge leans on scale and depth; one against the room leans on everything. While the pose is being redone the knee reading keeps working, so the loop need not stop.

The eye's errors, per reading (`calc/eye_ledger.py`; defaults: scale 1 per cent, camera moved 5 mm, pointing 0.1 degree, camera 300 mm up, 125 ms at 0.5 mm/s), in micrometres:

| reading | scale | camera moved | pointing | latency |
|---|---|---|---|---|
| the knee (0 mm apart) | 3 | 0 | 0 | 62 |
| dot against the rim edge (6.35 mm up) | 23 | 106 | 0 | 62 |
| dot against the two ports (19 mm) | 190 | 0 | 0 | 62 |
| dot in the room frame | 618 | 5000 | 524 | 62 |

Scale grows with how far apart the two things are; a camera move costs parallax only for things at different depths; pointing shifts the whole picture, so it cancels in every comparison made in one picture; time costs the same for all. This is the calibration burden of the eye in one line: **the error of a comparison grows with the separation of what is compared, and the seam foot is at zero.**

**Four arrangements from other explorers**, each adding numbers to the ledger and one thing a board cannot see (numbers from their idea files; times are poses times seconds per pose, illustrative):

| arrangement | numbers to calibrate | trial | check | what a board cannot see | what makes it stale |
|---|---|---|---|---|---|
| table opening and gantry (`room-01`, `room-15`, Derek's) | 6: two scales, squareness, the shelf plane | 5 by 5 grid of the dot on the board puck, 25 poses, 2.5 min | home switch and dock, 10 s | nothing moves the dot along the beam; standoff comes from the shelf height and spot size | lost steps, belt stretch, a binding shelf rod |
| corner cords (`room-06`, `eyes-13`) | 32: 24 anchor offsets, 8 cord zeros | 40 poses, 5 min | cord tension and dock, 20 s | the gun's position along its beam (a board sees a spot, not the gun) | cord creep, drum layering, temperature, the fibre's pull |
| hexapod with a software pivot (`borrowed-13`) | 9: the pivot (3), six leg zeros | 20 tilts about the assumed pivot, 2 min | home and dock, 15 s | the pivot component along the beam; the play of twelve ball joints | joint play, a leg re-homed, a re-seated shell |
| encoded arm, hand-moved (`borrowed-03`, `trials-19`) | 28 | 40 orientations a hand holds, 6.7 min | return to the seat, read the zeros, 10 s | play beyond the encoders (0.02 degrees is 0.3 mm), the along-beam component | a bump, settling joints, a re-seated gun |

The cost of putting an event right (`calc/eye_ledger.py`, part 2; stale nodes and suspect nodes, minimum seconds if every check passes and worst case if every suspect also needs its trial): a knocked camera 1 stale and 7 suspect, 310 s minimum and 1980 to 2230 s worst; a lens refocused 3 and 7, 560 s; a new tube 2 and 0, 360 s; a rotator re-clamped 2 and 4, 290 s; a gun re-seated 1 and 3, 240 s; lost steps 1 and 5, 340 to 620 s by arrangement (the cage and the arm cost most); an afternoon's 5 K of warming 0 and 9, about 260 s of checks. The worst cases are dominated by the 900 s witness pass that relates the dot to the melt: the checks are cheap, the melt is not.

## What carries the loads, what establishes position, what stays free

Not the subject: the graph is about what has to be known. The references it names are the reference pucks (`trials-22`), the corner itself and the rotator's index.

## What software could command, observe, and what stays manual

- **Command:** a check or a full trial for a chosen calibration; which to run next, in dependency order; a reference puck swap.
- **Observe:** the rim-and-ports residual on every frame; a golden dot's brightness and place; a coupon's knee against its stored value; judge against K touches; the dock's seated contact and weigh-in; latency by a step test.
- **Manual:** swapping a puck; the witness pass on a scrap coupon; deciding how far a suspect calibration may be trusted for the next weld.

## What was tried to break it

1. **My first version made a new tube make the judge suspect.** *Assumption:* the judge's bias belongs to the eye. *Change (found while drawing it):* the geometry and the dot were fitted on the matte board, where the tube's surface does not enter; a new tube brings its own angle-locked bias into the seam node only. The event now marks the seat and the seam stale and nothing upstream suspect (360 s instead of 460 to 2170). *Left standing:* whether the judge's gain on steel differs from on the board (that is the coupon puck's question).
2. **Some things have no cheap check.** The judge's angle-locked bias (only touches see it: `datum-14`), the dot against the melt (only a witness pass: `datum-11`), an auto-exposure that creeps (only reading the controls back), two clocks drifting apart (only a step test). They carry a warning mark: the graph cannot mark them suspect until something else fails. *Left standing:* a schedule for them.
3. **A passing check may not license the value.** A check at the level of the noise cannot see a drift below it, and the thresholds have not been set. *Left standing:* this is measured on the bench, not here.
4. **The edges are one reading.** A hexapod's leg zeros do not depend on the judge if it has encoders and a home switch; a cage's cord creep depends on the fibre's pull, which the umbilical event touches. *Change:* the arrangement radio changes the labels, times and unknown counts, not the edges. *Left standing:* per-arrangement edges are not drawn.
5. **A closed loop on a comparator needs only a local calibration.** A loop closed on the knee (`borrowed-05`, `trials-20`) needs the local Jacobian at the corner (command to dot motion, two or three numbers, re-found by nudge and watch), not the arrangement's global geometry; the global fit matters for open-loop replay, a hand, and reach. At weld the dot is off and the melt is glare, so the loop is open, and what the eye calibrated must be *held by the arrangement* through the blind interval (the dock's zeros, the map, the compliance). *Left standing:* how long it holds is not a dry-run quantity.
6. **A PTZ camera** (Derek's vision) adds a pose that changes at every preset and a scale that changes at every zoom: the pose node gets a per-frame check from the rim and ports (`datum-19`, `eyes-16`) and the lens node goes stale at each zoom unless the zoom repeats to about 1 per cent. Not drawn.

## Branches and combinations

- Uses `trials-22` (the pucks the eye is calibrated on), `trials-23` (the clock node), `trials-19` (the fixed-point trial that fits the arrangement), `trials-18` (the golden dot and the coupon's knee), `datum-14` (touches for the judge's bias), `datum-19` (the per-frame pose check), `trials-17` (the trial card records each node's date and check result). Arrangements from `room-01`/`room-15`, `room-06`/`eyes-13`, `borrowed-13`, `borrowed-03`.
- Transferable: calibrations form a graph; stale needs a trial, suspect needs a check; run upstream first; the error of a comparison grows with the separation of what is compared.

## Unresolved problems and questions that need Derek

- Q: how do you want the loop to behave when something is suspect but not stale: stop and ask a person, or continue with provisional readings and mark the trial?
- Q: what actually happens on your bench in a week: is the camera bumped, does the light change through the day, does a cable get re-routed? Notes for a few days would replace the ten events with the three that occur.
- The thresholds that make a check pass; the schedule for the silent nodes; the blind interval at weld.

## Assumptions

Every time is **[illustrative]**; unknown counts from the source ideas (room-06 32 numbers, `eyes-13`; borrowed-03 28, `trials-19`; borrowed-13 pivot 3 and six leg zeros; the gantry's six are mine: two scales, squareness and three for the shelf plane); readings table formulas **[derived, illustrative]** (scale acts on the image separation: 0.3 mm residual for the knee, 6.35 tan(psi) plus 1 mm for the rim edge, 19.05 mm ports, 61.85 mm the room; camera translation t costs t times the depth difference over H against the rim edge, 0 in the plate plane, t against the room; pointing costs H tan(theta) against the room only). The 0.05 mm marker is not a requirement.

## Sourcing pointers

None new beyond `trials-22` and `trials-23`.

## Scene

`trials-24-calibration-graph`. Controls: the arrangement (branch); an event and its apply button (scene edits); run the next trial, run the chosen one, reset (state); a pessimistic toggle for failing checks (scene); four eye errors and the camera height for the table (scene edits). Nothing is an actuator.
