# trials-11-arrangement-yardstick: the station as an instrument for any way of holding the gun

No scene. It is a use of the equipment more than an arrangement.

## Picture it

The rotator, a judge camera above the bore and the dot log stay exactly as they are. What changes from week to week is what holds the gun: Derek's hands, a monitor arm, rings on bungees, a gantry. Each is run through the same short script on the same tube and scored by the same judge: dot-to-seam error over the revolution, drift over ten minutes, how it reacts to a tug on the umbilical, how long it takes to get to the seam from cold. **The first entry is Derek's hands.**

## The proposal

Observe only. The judge (trials-03/-04) logs dot-to-seam error while a person holds the gun on the seam through a revolution, as in a good dry run. That number, from a hand that is known to make acceptable welds, is a real requirement: not a tolerance an agent proposed, but what a competent hold actually delivers. Every other arrangement is then compared with it by the same instrument. It also protects the study from the "requirements" inherited from earlier agent notes (the assignment says they must not silently eliminate ideas).

Metrics that come out of one script: RMS and peak-to-peak dot-to-seam error over a revolution; the same after two minutes (drift); response to a known tug (a hanging weight on the umbilical, or the dock's cell reading); time from "cold start" to on-seam; and the same on a second tube (comparability across tubes).

## Carries, locates, free

Whatever holds the gun; the yardstick adds nothing that carries. Position is the rotator's angle and the judge's seam reading.

## Software

Observe: dot-to-seam offset over time and angle; rotator angle; the umbilical tug (weighed at the dock if there is one). Command: rotator only (existing controller). Manual: everything else: this is the point.

## Tried to break it

1. **The hand's error may not be what makes the weld good.** A dry-run dot error is not weld quality. Assumption: on-seam within the hand's scatter is sufficient. Change: use Derek's welds (with their pass/fail from PT, sections and hydro **[repo]**) to see whether the dry-run error of that hold correlates with outcome. Leaves: a few welds cannot show correlation; it gives a plausible target, not a proof.
2. **The judge needs to work before the yardstick does.** A hand-held gun is in the way of camera A. Leaves: the camera position problem of trials-03 and `eyes`.
3. **Comparability across arrangements.** Different arrangements have different setup times and human roles. Repair: record who and what; keep the script fixed. Leaves: fairness is a judgement.

4. **The requirement needs a judge with nothing in it (from datum's exchange, wave 2, section 3; drawn as `datum-17-yardstick-on-the-twin`).** *Conflict, in this variant:* the first entry is Derek's hands scored by the same camera judge that will score every other arrangement, so the hand's number becomes the requirement. The judge is a camera over the bore that sees the dot on the plate a millimetre from the wall; whatever it gets wrong reads as seam. With a 0.04 mm angle-locked bias and a 15 per cent gain error the hand's true 38 micrometres reads as 68; at 0.10 mm bias 109. And an arrangement built on the judge (a map replayed from its readings, `trials-04`) reproduces the judge's error and then reads as perfect: at a 0.06 mm bias the judge passes a replay the truth fails (52 against 33 to 35 read). *Assumption behind it:* one judge is a neutral yardstick for arrangements whose sensing differs from its own. *Change:* three instruments for three questions. A **clear twin** (a see-through wall over a printed plate at the real recess) lets an outside camera see the dot at the corner all the way round, so the hand is scored with no judge in the number; a **notch tube** (rung 3) does it for 34 degrees (about one memory time of the hand's drift: the hand's rms from it swings from 21 to 40 micrometres, true 38), enough to calibrate a judge's gain by jogging the dot, not to score a hold; **K touches at rest** give a machine arrangement's true error on the real tube (K = 8: the replay at 0.06 mm bias scores 67 and fails correctly). The judge stays dense in time and is used for what does not depend on what it is built on. Adopted as a combination: the twin and the notch are pucks in `trials-22-reference-pucks`, and the first entry of the yardstick becomes the hand on the twin, before any judge exists. *Leaves uncertain:* a clear wall and a printed plate do not reproduce glare on polished 316L, fume or a hot bead; a dry-run hold is not a weld hold (the eye follows the puddle and the wire, not the dot); a raw rms may overstate the tremor if the puddle averages errors faster than about 4 Hz; refraction through 2.5 mm of acrylic shifts a point 0.15 mm at 10 degrees off the wall normal.
5. **Which of my four metrics can be scored on the twin (datum's question).** Hold (rms over a lap), drift after two minutes, and the response to a tug are properties of the arrangement and the hand, not the tube's surface: all three can be scored on the twin with truth and no judge. Cold-start time (how long to get on the seam) depends on the visual task and on the judge's own knee, so it needs the real tube; and a machine arrangement's hold needs the real tube with K touches at rest, since touching cannot score a moving hand. *Left standing:* the twin's stand-in for the hand's visual task (a dot seen through acrylic against a printed plate) differs from a dot on a steel corner from above.

## Combinations

Uses `trials-03/-04/-05`; benefits from `trials-02` (dock weigh-in for the tug) and `trials-10` (human labels as a check on the judge).

## Unresolved

Q: How far off the seam can the dot be, at what angle, and still make a good weld today? This is the number the study most lacks.
Q: Would you hold the gun in a dry run for ten revolutions while the camera watches?

## Assumptions

All **[illustrative]**.
