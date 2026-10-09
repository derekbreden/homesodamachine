# trials-04-seam-map-replay: learn the wobble, replay it, keyed to the rotator

Scene: `scenes/trials-04-seam-map-replay/index.html` (developed). Calc: `explorers/trials/calc/seam_rates.py`.

## Picture it

The tube does not spin true, but it is wrong the same way every revolution. In the first turn or two the gun holds still and the judge camera writes down where the seam is at every rotator angle: a seam map. In later turns a small follower moves the dot (or the tube) by exactly that map, keyed to the rotator's angle, so the dot stays on the seam while the tube wobbles under it. The tube no longer needs to be seated to indicator accuracy; it needs to be seated within the follower's range.

## The proposal

Two components of wobble matter, and only two directions: **radial** (eccentricity and ovality: the seam moves toward and away from the gun) and **vertical** (the plate face is not square to the axis: the seam moves up and down). The third direction, along the seam, only slides the dot along the seam (0.008 mm per mm at r = 61.85 mm). Both wobbles repeat every revolution, so they can be learned: per 2° bin, average the judge's dot-to-seam readings over N learning revolutions and remove the mean. Then command a follower with the map, **advanced by the follower's lag** (lead compensation) so the lag does not appear as a phase error.

The numbers are gentle. At bead speed 5 to 15 mm/s a revolution takes 26 to 78 s **[repo]**; the accepted runout 0.25 mm TIR radial and 0.30 mm face **[repo]** means amplitudes of about 0.125 and 0.15 mm if each is a single harmonic **[derived]**. The follower's peak speed is amplitude times harmonic times 2π/T: 0.03 mm/s for the 1× radial component at the fastest speed, 0.36 mm/s even for 0.5 mm at 3× (`seam_rates.py`). Peak acceleration is under 0.3 mm/s². That is a small, slow axis; a hobby stepper on a fine screw is oversized. Rate, not stroke, is where the follower is cheap; stroke (how much seating error it can absorb) is the design choice.

The replay works on the *dry-run* only; whether it can be used during a weld is a welding question (thermal distortion changes the tube, a following dot changes the wire and gas geometry). It is offered as a dry-run contribution and a possible weld-time feed-forward.

## What carries the loads, what establishes position, what stays free

The follower carries whichever mass it moves: gun-side (a small r and z stage between the positioner and the shell) or tube-side (the rotator on a stage; see the branch). Position: the rotator angle (14,400 pulses per revolution, 0.025° **[repo]**) is the clock; the index pulse (trials-01) gives an absolute zero; the judge camera builds the map. Free: the follower's two axes; restrained: tangential (does not matter to first order).

## What software could command, observe, and what stays manual

- Command: rotator speed (existing); follower r and z keyed to angle; learn/replay state.
- Observe: dot-to-seam radial offset per angle (judge camera, trials-03); height offset per angle (dot size or ruler: weaker, drawn 3× noisier); map quality over revolutions; residual after replay.
- Manual: rough seating; deciding when a map is too old.

## Tried to break it

1. **Drift.** Conflict: anything that creeps is not in the map, so the residual grows. Assumption: the wobble is stationary. Change: raise Drift in the scene; the residual walks. Repair: re-find the seam at the start of each replay block (trials-03), or keep maps short-lived. Leaves: the real drift rate is **[unknown]**.
2. **Follower lag.** A first-order lag turns the wobble into a phase error. Repair: advance the replay by the lag; the software can measure the lag by commanding a step. Leaves: nonlinear lag (stiction) is not modelled.
3. **Height with a tube-side follower.** An X slide under the rotator follows radial wobble but not height. Repair: add a lift (branch 04b). Leaves: the tube-side stack carries several kilograms.
4. **Maps do not survive a re-seat.** Lifting the tube out and back changes the wobble. Repair: the puck (trials-01): a kinematic seat plus a tag keyed to the map. Leaves: whether a real re-seat is repeatable **[unknown]**.
5. **Learning takes time.** N revolutions at 49 s is minutes; noise averages down as 1/√N. Number that changed my mind (`map_learning.py`, 30 simulated trials per cell, the scene's model): with 0.03 mm judge noise the residual after replay is 0.031 mm rms at N = 1, 0.018 at N = 3, 0.014 at N = 5, 0.012 at N = 8, against 0.43 mm rms unmapped for a 0.6 mm eccentricity. Past about four revolutions the gain is small; jitter and drift (the settings tried: 0.02 to 0.05 mm, 0.01 to 0.03 mm/rev) barely move it because the last revolution is judged after the DC is re-found. So the first two or three revolutions do nearly all the work, and the judge's noise, not the count, sets the floor. Leaves: what the judge's real noise is, which nobody has measured; and the model has jitter as slow sinusoids, which is kinder than a real cable.
6. **Where the map starts.** The dot has to be within the follower's range of the seam before learning. That is what the dot probe (trials-03) supplies.

7. **The judge's own bias is replayed as seam (from datum's exchange, wave 2, section 1).** *Conflict, in this variant:* `map_learning.py` scores the replay against the true seam the simulation knows (0.018 mm rms at N = 3). In the rig the score is against the judge, the learned map is the mean of judge readings per angle, and anything the judge gets wrong that repeats with table angle (glare, tint, tack marks, the plate's rolling direction, laser-cut dross) is replayed as seam. A station is a fixed point in the room, so an angle-locked error comes from the tube and turns with it. *Assumption behind it:* judge error is random per reading. *What the change alters* (`calc/map_bias_touch.py`, judge noise 0.03 mm, N = 3, 200 draws, bias in harmonics 1 and 3): no bias 18 micrometres rms; a 0.03 mm bias (25 micrometres rms) 31 true while the judge reads 18; 0.06 mm: 54 true and still 18 read; more laps do not help (N = 8: 28 against 12). The scene now has a bias slider and two rows (true error, what the judge reads with its frame noise averaged out). *What it leaves uncertain:* whether the camera judge has an angle-locked bias at all; its size.
8. **A second opinion from touches, and what it cannot see (from datum's exchange, section 1; `datum-14`, `datum-07`).** K touches at rest (a stylus or the wire) read the corner at the tool with no camera in the reading; the answer to datum's question is yes, the score changes when the reference is touches instead of the simulation's truth. Built from 8 touches (harmonics 1 to 3, touch noise 0.02 mm) the map leaves 17 micrometres when the seam has nothing above harmonic 3, and 35 when harmonics 4 to 6 carry 0.02 mm each: the touches cannot see them, and 8 azimuths alias harmonics 5 and 6 onto 3 and 2 (16 azimuths: 28). The judge-only map leaves 31 at a 0.03 mm bias and 54 at 0.06; the hybrid (the judge's shape with its harmonics 1 to 3 replaced by the touches') leaves about 30 for both. So touches beat the judge only when its bias exceeds the content they cannot reach, and the check (judge minus touch at fresh azimuths, 56 for a truth of 54 at a 0.06 mm bias) is the number that can see the bias at all. The touch noise has to be below the bias: at 0.04 mm the touch map is worse than the judge's. *Left standing:* how a stylus or the wire reaches K chosen azimuths without disturbing the seat.
9. **The map has four owners with different lifetimes (from datum's exchange, section 1; drawn by `datum-14`).** The rig, the seat, the work and the judge's bias. *Answered and kept:* this scene keeps one array keyed to the rotator angle, because the follower needs one number per bin; the ownership belongs in the bookkeeping. It lives in `trials-17` (the trial card rows for the judge's bias and the map's owners) and in `trials-01` (a work index for the tube's own clock). A lift and return leaves the map (27 micrometres stale against 26 relearned); a re-seat, a turn in the nest, a re-clamp, a tack or a new tube does not.
10. **The ownership route saves time only for a lift and return (from datum's exchange, section 1).** A relearn is 146 s at 8 mm/s; the route by diagnosis costs a judge lap (49 s) and then nothing, four touches or K touches. Agreed: what it buys is attribution and a number for the judge's bias, not time. Recorded, not repaired.

## Branches and combinations

- `trials-04b-follower-under-tube` (branch, idea file): the follower is a stage under the rotator; the gun hangs from a passive support.
- Combines with `trials-01` (index, tag), `trials-03` (find the seam first), `trials-05` (the zoo tube tests the map on known errors).
- Transferable: angle-indexed feed-forward; lead compensation; "only r and z matter".
- **Wave 3:** `datum-14-who-owns-the-wobble` (the map's four owners, drawn) is a branch of this idea; the scene here carries its judge-bias and touch check. `trials-16` and `trials-04b` meet `datum-16` (a crown as the passive support: the scene's support radio).
- **Scene revised in wave 3:** a bias slider, a map-source radio (judge, touches, both), K touches, and a support radio (stiff or soft) with the cable's pull; the table shows the true error, the judge's, the touch check and the gun's static offset against the follower's travel.

## Unresolved, and questions for Derek

- Q: How much of the runout you see at the indicator repeats revolution to revolution, and how much is random? (Indicator at the rim, ten revolutions, read the same angle each time.)
- Q: Does the weld tolerate a dot that follows the seam (rather than a seam that moves under a fixed dot)?
- Q: What dot-to-seam error still gives a good weld? This is the number that decides how good a map has to be; the dry run cannot supply it.

## Assumptions

Speeds and accepted runout **[repo]**; amplitudes as half TIR **[derived]**; harmonics, phases, noise, drift, jitter, lag **[illustrative]** (jitter is a sum of slow sinusoids); judge noise **[illustrative]**.
