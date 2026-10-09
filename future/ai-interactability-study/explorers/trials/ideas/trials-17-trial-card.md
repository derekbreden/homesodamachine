# trials-17-trial-card: what makes one trial comparable to the next

No scene. It is the answer to the framing's second question, kept as a table so ideas can be checked against it.

## Picture it

Every trial writes one card. The card names the tube, the puck, the artefact rung, the approach direction, the dock baseline, the lighting frame, the rotator zero, the software version, and what was randomised. Two trials are comparable when their cards agree on everything not being varied.

## The nuisance factors

| Factor | How it is handled | Idea |
|---|---|---|
| Gun start pose | reset by design: the dock's kinematic seats | trials-02 |
| Positioner drift, backlash, missed steps | reset by design: discarded at every dock | trials-02 |
| Friction hysteresis of a compliant support | reset by design: one-sided final approach | trials-02 |
| Umbilical shape and drag | recorded: dock weigh-in vs baseline; re-exercise if it moved | trials-02 |
| Tube identity | recorded: tag or label | trials-01 |
| Tube seating in the nest | recorded and re-measured: judge sees eccentricity; seam map | trials-01/-04 |
| Puck seating | reset by design: kinematic seats; seat certificate | trials-01 |
| Rotational phase after a swap | reset by design: asymmetric seats; index magnet | trials-01 |
| Seam location in axis coordinates | measured each trial: dot probe | trials-03 |
| Camera pose and lighting | recorded: a golden-target frame each session on the board | trials-05 |
| The dot itself (alignment, standoff, size) | recorded: pivot trial on the board when it may have changed | trials-13 |
| Tube-to-tube variation | randomised and blocked: zoo and real tubes, golden tube every session | trials-09/-15 |
| Judge error | recorded: notch tube ground truth; human labels | trials-05/-10 |
| Slow drift over hours | uncontrolled except by re-anchoring | trials-02/-03 |
| The gun's real mass and cable | not controllable with a mule; confirmed with the real gun | trials-06 |
| Ambient (light, vibration, temperature) | recorded where cheap; otherwise uncontrolled | none |
| Human operator (loader) | recorded: who and when | trials-08 |
| Camera drift across a session | recorded: a golden dot (a fixed pointer command) and the puck's tag ring seen every frame | trials-18, trials-01 |
| Arrangement calibration (encoded arm, gimbal formula) | recorded: the session's fixed-point calibration id and its held-out error | trials-19 |
| Whole-rig baseline each morning | recorded: a golden tube runs the dry cycle first and is compared with a stored trace (from use-12) | use-12, trials-15 |
| The dot in the shell and the camera (change detector) | recorded: a coupon under the docked dot or a coupon puck at the trial's station, its knee against the stored value (from `datum-15`, wave 3) | trials-02, trials-22 |
| Judge's angle-locked bias | recorded: judge minus K touches at fresh azimuths after a replay; a new tube brings a new one (from `datum-14`) | trials-04 |
| Which owner a map belongs to (rig, seat, work, judge) | recorded: the map's date, the event that last changed each piece (lift and return, re-seat, turn, re-clamp, tack, new tube) | trials-04, trials-01 |
| Camera pose, scale and lens | recorded: the last board puck run and its date; the rim-and-ports residual every frame | trials-22 |
| Latency of the frame chain, and clock offsets | recorded: the last step test (about a minute); re-run hourly | trials-23 |
| Each calibration's state (ok, suspect, stale) and when it was last checked | recorded: the ledger of what leans on what | trials-24 |
| Laser and weld effects (heat, fume, spatter) | not in a dry run: outside this idea | none |

## Tried to break it

1. **A card is only as good as the factors on it.** Repair: run a repeated identical trial twenty times and see whether the spread is what the card says it should be. Leaves: unknown factors.
2. **Dry-run comparability is not weld comparability.** The card ends where the laser begins.

3. **A card row for "the dot itself" (from datum's exchange, wave 2, combinations list).** *Conflict:* the pivot trial on the board records the dot "when it may have changed", which says nothing about when it did. *Change:* the coupon (at the dock, or as a puck at the trial's station) says at every visit whether the dot or the camera moved; the row above records it. *Left standing:* one shift in one number cannot say which of the two moved.
4. **The card is only as good as its rows for the eye (wave 3).** Camera pose, scale, lens, latency and the ledger state are now rows; each needs a date and a check result so two trials with the same card really did share an eye.

## Assumptions

All **[illustrative]**; the table is a structure, not measured.
