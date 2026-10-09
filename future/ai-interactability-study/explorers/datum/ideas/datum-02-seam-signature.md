# datum-02-seam-signature: learn the seam by turning, replay it while welding

Scene: `scenes/datum-02-seam-signature/index.html`. Depth: **deep** (five rounds below). Origin: swarm. Framing: the seam is the datum.

## Picture it

The tube turns once with the red dot on and a sensor logging where the seam is against the dot at each table angle. Software fits a small model of this tube's seam (centre offset, tilt, seat height, ovality) and remembers it. In the weld rotation the same angles come back from the rotator's step count, and a fine stage in the gun's shell moves the dot by the fitted amount, so the dot follows this tube's own wobble. The stage barely moves: a few tenths of a millimetre, a few hundredths of a millimetre per second.

## The proposal

Because the seam is a circle, a real tube on the rotator turns it slightly off-centre and slightly tilted. Seen from a fixed dot, the corner moves in and out (radial) and up and down (height) once per revolution, plus a smaller twice-per-revolution part if the bore is oval. For a given tube, seated and tacked, that motion repeats every turn. So it can be measured in a dry rotation and replayed as feed-forward against table angle. The constant term of the fit is the setup error itself (how far off the coarse aim left the dot), which is a free by-product: the operator or a slow stage can correct the coarse aim before welding.

Software's role is small and specific: it records N samples in the dry rotation, fits a least-squares harmonic model, and then drives two proposed fine axes from the model during the weld rotation. What measures dot-versus-seam is open: a camera, a feeler (see datum-04), or plain dial indicators on the outside of the tube near the rim and on the plate face (see below), which is the tool the rig doc already uses for its runout check [repo].

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** nothing new. A passive arm or the hand holds the gun; the fine stage rides in the printed shell between that hold and the gun.
- **Position:** the seam of this tube, learned per tube, indexed by table angle (step count, 0.025 deg per step [repo]). No room reference; the datum-chain scene shows why the room drops out.
- **Free / restrained / driven:** the gun is held by whatever holds it (not addressed); two fine axes (radial, vertical) are *driven* by the replay; the table angle is *driven* by the existing rotator; the tangent position along the seam is free (one degree of freedom is free by symmetry).

## What software could command, observe, and what stays manual

- **Command:** rotator angle and speed (existing); fine stage radial and vertical (proposed). If the laser unit lets software move the red-light/beam centre, that could be the radial axis with no mechanism at all (see datum-13).
- **Observe:** table angle from the step count; dot-versus-seam during the dry rotation from whichever sensor. Nothing observes the hot drift during the weld or the gun-side drift.
- **Manual / unresolved:** coarse aim so the dot is inside the stage's stroke; returning the index to the first tack before each rotation [repo]; re-recording after any re-seat or extra tack.

## What was tried to break it

Numbers from `calc/seam_signature.py` (output in `calc/seam_signature.out`); all noise, offsets and sensor biases are illustrative.

1. **Round 1: is the correction even big?** At the rig's own acceptance limits (0.25 mm radial and 0.30 mm face TIR [repo]) plus a 0.20 mm setup offset and 0.05 mm ovality, the uncompensated dot is off the seam by 0.22 mm RMS and 0.37 mm peak. Replay with a modest sensor (noise 0.05 mm, 24 samples) leaves 0.022 mm RMS, 0.041 mm peak. So the idea has something to do whenever the process window is tighter than about a third of a millimetre, and nothing to do if it is looser: the scene's window slider makes this visible. The window is unknown.
2. **Round 2: is the axis hard to build?** Demand: peak 0.029 mm/s at 8 mm/s bead speed (0.055 mm/s at 15 mm/s), stroke +/-0.37 mm, resolution about 0.01 mm. One pulse of the table is 0.027 mm of seam travel [repo]. This is a small, slow axis; the hard part is not the axis.
3. **Round 3: sensor bias that repeats with the table angle.**
   - *Conflict:* a feeler seated off-centre, or glare that turns with the tube, looks like seam shape.
   - *Assumption:* sensor errors are random and average out with more samples.
   - *What changes:* the fit cannot tell bias from seam; the replay imprints it. A 0.05 mm angle-locked bias takes the residual RMS from 0.007 to 0.036 mm at 36 samples and 0.02 mm noise.
   - *Repair:* verify with a second, unlike sensor, or with a witness pass (datum-11).
   - *Uncertain:* whether real sensors have angle-locked bias at all.
4. **Round 4: thermal drift during the weld.**
   - *Conflict:* the cold dry rotation cannot see the tube move as it heats.
   - *Assumption:* the seam does not move once welding starts.
   - *What changes:* a 0.10 mm drift over the lap leaves 0.061 mm RMS even with a good fit (N=36, noise 0.05).
   - *Repair:* feed-forward carries the repeatable part; a leading feeler (datum-04) or camera closes the loop on the rest.
   - *Uncertain:* drift magnitude [unknown].
5. **Round 5: a cheaper, independent way to get the signature.**
   - *Idea:* the rig doc's own indicating step already puts a 0.0005 in test indicator on the tube [repo]. If the indicator's reading were logged against table angle (the ESP32 already knows the angle), the radial signature at the working end and, with a second indicator on the plate face at the weld circle, the face signature come for free, with no line of sight into the pocket.
   - *Conflict:* the indicators read the OD near the rim and the plate face, not the corner; wall-thickness variation and rim-to-plate tilt are then model errors that act as a bias (see the scene's "Indicators" sensor preset: low noise, 0.06 mm bias, all illustrative).
   - *Repair:* a one-off comparison against a corner-level sensor per tube type.
   - *Uncertain:* whether the bias is stable across tubes.
   - *What else falls out:* the indicator log tells the operator which of the three adjuster screws to turn and how far, turning the manual indicating step into a guided one (software moves nothing).

Also examined and left standing: the replay trusts the step count as the angle (no encoder; the rig doc's own gate checks for skipped steps [repo]); the signature is stale if the tube is re-seated or an extra tack pulls the plate; the stage runs out of stroke if the coarse aim is poor (the scene shows a LIMIT badge and leaves the excess in the error).

### From travel's exchange (wave 3: `exchange/travel--on--datum-w2.md` section 2; `scenes/travel-18-signature-parity`)

6. **Round 6: the hold between the dry turn and the weld turn.** *Conflict (travel):* the replay applies the dry turn's constant term to a gun that has to be in the same place in the weld turn. It is not: the wire feeder starts and its conduit pulls on the bracket, the gas hose pressurises, the hand leaves, the fibre emits. The error is the change of force times the compliance of the chain from gun to room: 6 micron per newton (20 mm steel post, 300 mm), 44 (12 mm steel rod), 128 (12 mm aluminium rod); a friction joint also creeps regardless of force (0.02 degrees at 250 mm is 0.087 mm). A stage in the shell is in series (20 N/mm adds 0.05 mm per newton). *Assumption:* the gun does not move between the turns; the idea said the hold was "not addressed". *What the change alters:* the scene has `What holds the gun between the two turns` (the hold, the change of force) and a warning when the term exceeds 0.02 mm; one newton against the rod is 0.044 mm, twice the fit residual, the same sign every lap. *Repair, adopted:* record the dry turn in the weld's mechanical state (feeder jogging at weld speed, gas on, laser off; `use-10-wire-first` as a check): the two turns' constants differ by exactly the parity term and the replay uses the second. It is the first thing the routine does. *Leaves uncertain:* what only an emitting head does (vibration motor, heat), the real change of force, hot drift.
7. **Round 7: which axes, and where the stage lives.** *Conflict (travel):* in the crown branch the crown has no radial slide. *Answer:* correct: with the crown the replay drives height only (the crown's vertical stage); the radial 1x is what the nest screws, the seat or the head's own beam-centre adjustment would take (if the laser lets software command it: `datum-13`, unknown). A follow stage under the work takes the constants out of the gun's chain altogether (`travel-02`). And the constants are two thirds of the uncompensated rms (0.29 mm): a static trim leaves 0.146 rms, nest screws taking 90 percent of the radial 1x leave 0.114, a Z follow taking the vertical 1x leaves 0.043 (`travel/calc/10`): a replay stage earns its place below a window of about 0.2 mm, vertical first. *Leaves uncertain:* the real window.

## Branches and combinations

- Sensor choice is the branch inside the scene (camera, feeler, indicators); no separate scene.
- Natural combinations (not built): feeler for the signature and the closed loop (datum-04); the crown's Z stage as the vertical axis (datum-03); the plate-face plunger as the height signature sensor (datum-03).
- Transferable: the harmonic model and dry-rotation recording to any arrangement where the tube turns under the gun.
- The signature is one curve with four owners (rig, seat, work, judge bias) and lifetimes; `datum-14-who-owns-the-wobble` splits it and adds an unlike-sensor check (K touches).

## Unresolved problems and questions for Derek

- Which sensor. Where the fine stage lives. Whether the head's own beam-centre adjustment is commandable (datum-13).
- What accuracy does the dot need against the corner for a good bead? Every conclusion moves with the window.
- Does the continuity-proof dry rotation already in the sequence [repo] leave room to record a signature at the same time?
- Would you accept logging the existing indicator against table angle as a first step (no new hardware except a data-out path)?

## Assumptions

- Runout limits 0.25 mm radial and 0.30 mm face TIR [repo]; used as amplitudes of half each. Bead speed 5-15 mm/s, 0.772-2.316 rpm, 0.025 deg per step [repo].
- Sensor noise, bias, ovality (0.05 mm), setup offsets (0.20, -0.15 mm), stage stroke, drift, window: illustrative.
- Nothing about the fibre, the gun or the weld pool is modelled.

## Sourcing pointers

`sourcing/datum.md`: mini linear stage with NEMA 11 (fine axis class), Hall sensor (feeler class), Arducam global-shutter camera (camera class). Digital indicators with data output were not looked up.

## Scene id

`datum-02-seam-signature`.
