# freedom-05: runout as a table (feed-forward instead of stiffness)

Scene: `scenes/freedom-05-runout-table`. Origin: swarm original (from the freedom framing). Depth: developed (four break-and-repair entries). Numbers from the scene's model (least-squares fit on noisy dry-run samples); parameters **illustrative** unless tagged.

## Picture it

The tube turns once in about 49 seconds. Watched from a stationary gun, the corner drifts in and out and up and down by a tenth of a millimetre or two, exactly the same way every turn. A camera watches the red dot through one dry-run revolution; software fits a smooth curve; a tiny stage under the gun then moves by minus that curve as the turntable angle advances.

## The proposal

The rig already accepts runout up to 0.25 mm TIR radial and 0.30 mm TIR face at the weld circle [repo]. The proposal is not to remove it with a stiffer or heavier support but to treat it as a **known periodic disturbance**: a per-revolution sine (amplitude and phase) for radial and for vertical, plus a constant per-tube offset, fitted from one dry-run. A vernier stage (±0.5 mm is enough) follows the fitted curve against the rotator angle, which the controller already reports (`turned-so-far degrees`) [repo]. Precision comes from a model and an index, not from stiffness.

Required speed is trivial: at 8 mm/s bead travel (7.4°/s at r = 61.85 mm) an amplitude of 0.14 mm needs 0.018 mm/s and 0.0023 mm/s² [derived]. Almost any small actuator is fast enough; the limit is resolution and the quality of the fit.

## What carries the loads, what establishes position, what is free or restrained

- The support only holds the *mean* position; whatever it is (an arm, a suspension, a hand-placed stand).
- **Position at each moment**: the model + the rotator angle index (feed-forward) with the camera as the check.
- **Free**: the support's stiffness does not matter for this error, only its long-term drift.
- **Driven**: the vernier (radial and vertical), from a table over angle.
- **Changes over time**: one dry-run per tube (setup), then the same table drives the weld pass.

## What software could command, observe, and what stays manual

- **Command**: the rotator for the dry-run (already possible); the vernier as a table over angle (proposed).
- **Observe**: the dot against the seam through the dry-run (a camera; the scene's noise slider stands in for its resolution); rotator angle (exists); nothing during the hot pass here.
- **Manual or unresolved**: mounting the camera and the vernier; the mean position.

## What was tried to break it

**Entry 1. Camera noise makes the fit uncertain.**
- Conflict: with 0.05 mm of noise and 72 samples (2 revolutions at 36 per turn) the fit error is 0.009 mm radial and 0.019 mm vertical (one seeded draw); a noisier camera or a single revolution loosens it. The error falls as 1/√N revolutions.
- Assumption: a dry-run measures the runout exactly.
- Change: average more revolutions (each costs 49 s at 8 mm/s), a better observer.
- Leaves uncertain: what the camera can resolve at the dot through the bore's geometry (the eyes explorers).

**Entry 2. Runout is not a pure sine.**
- Conflict: a twice-per-revolution part (10% of the amplitude here) sets a floor of about 0.014 mm that a sine fit cannot remove.
- Assumption: a once-per-revolution model is enough.
- Change: a table over angle (more parameters, more samples) instead of a sine; or accept the floor.
- Leaves uncertain: the real spectrum of the runout.

**Entry 3. The per-tube offset can exceed the vernier's stroke.**
- Conflict: a plate seat depth off by 0.6 mm and a 0.5 mm stroke: the vernier saturates. The constant term of the fit takes the offset out, but only within the stroke.
- Assumption: the mean position is already right.
- Change: a longer stroke, or the support's mean position set from the fitted offset before the weld (the arm's job), leaving the vernier the periodic part.
- Leaves uncertain: how much plate seat depth varies tube to tube (Derek: the tube length and seat depth vary, magnitude [unknown]).

**Entry 4. Cold dot versus hot weld.**
- Conflict: the dry-run sees the red dot (0.3 mW, 630 to 670 nm) [manual p. 12]. The melt is where the beam is at power. How closely the dot marks the melt at working standoff is [unknown] (the settings screen has a red-light alignment adjustment, manual pp. 25, 39).
- Assumption: the dot marks the weld.
- Change: a one-off calibration against a test bead per configuration.
- Leaves uncertain: whether that offset is constant over the revolution.

## Branches and combinations

- freedom-07 (floating gun on the work): the contact follows the runout mechanically; this idea follows it by table. They can share a vernier for the per-tube offset.
- freedom-02 and freedom-01b: the vernier sits at the arm tip or at the nose stage.
- Trials framing (another explorer): the dry-run is the trial; this is what it teaches the machine.

## Unresolved problems, and questions that need Derek's observation

- Measure the actual runout of a few tubes on the rotator with the 0.0005 in indicator (radial and face at the weld circle): amplitude and phase, and whether it repeats turn to turn.
- Measure plate seat depth for several tubes (a depth gauge from the rim).
- Does the rotator angle count stay accurate over a turn (belt drive, backdrivable)?

## Assumptions

- Runout limits: **[repo]** (acceptance numbers, not measurements). Bead speed 8 mm/s and the 5 to 15 mm/s window: **[repo]**; 7.4°/s and 49 s per turn **[derived]**.
- Camera noise 0.05 mm, 36 samples per turn, ±0.5 mm stroke, ±0.15 mm tolerance: **illustrative**.

## Sourcing pointers

`sourcing/freedom.md`: mini linear rail with a T6×1 lead screw and NEMA 11 (the vernier: 1 mm per turn, 5 µm per full step [derived]), XYZ manual stage.

## Scene

`freedom-05-runout-table`.

## Wave 2 (after the exchange with eyes)

- **The table holds what repeats; a step at bead start is not in it.** The support answers a change of pull with compliance × force: 1.4 / 4.2 mm per newton on eyes-01's elastic with no rotation held, 0.10 / 0.01 mm on the nose seat. `freedom-13-map-and-step` puts the map, a force term (a load cell in the support) and the eye at the dot on one time axis. Entry 4 above (cold dot versus hot weld) is the same question from the dot's side.

**Wave 3 note (from borrowed's exchange).** borrowed had nothing to add from its side: the vernier is a 100 mm mini rail with a T6×1 screw (5 µm per full step, $54.80), as sourced.
