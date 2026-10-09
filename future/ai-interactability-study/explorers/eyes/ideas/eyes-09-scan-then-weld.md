# eyes-09 Scan first, weld second (seam map and look-ahead)

Scene: `scenes/eyes-09-scan-then-weld/` (rough sketch; tagged a lens in wave 3: it compares strategies, it is not one arrangement). Origin: swarm (eyes framing). Maturity: sketch, with a working comparison.

**Picture it.** The tube turns once with the laser off while a probe or camera, one that could not stand there during the bead, records how far the seam is from the dot at every angle. During the bead a slow trim axis plays that record back, indexed by the rotator's degrees. Or, instead, a camera 35 degrees upstream watches the seam arrive 4.7 seconds before the dot does. A plot shows the seam's offset against turned angle, the correction, and what is left at the dot.

## The proposal

Use a sequence rather than a position: **observe when and where nothing is in the way, weld later.** Under a fixed gun the seam moves at most 0.016 to 0.019 mm/s at 8 mm/s (radial and face runout at their acceptance limits; 0.030 to 0.036 at 15 mm/s; calc/runout-rates.mjs). That is slow enough to be recorded once per turn or watched a few seconds ahead. Three ways to use an eye: **scan** (dry turn, map by angle), **look-ahead** (a camera upstream), **at the dot** (the gun-borne eye of eyes-01), and combinations.

## What carries loads, what establishes position, what is free or restrained

Not addressed: any support with a slow trim axis (eyes-01) or another idea's positioner. The rotator's turned-so-far degrees (0.025 degrees per step) index a map fixed to the tube; the first tack is the index mark. Free: the tube's angle; driven: the trim axis playing the correction.

## What software could command, observe, and what stays manual

- **Command:** the rotator (existing: pedal and speed); the trim axis from the stored map or a live measurement.
- **Observe:** radial and vertical seam offset against angle (map); the seam ahead of the dot by the look-ahead angle; the offset at the dot.
- **Manual:** seating the tube once and not touching it between scan and bead; calibrating the scan sensor; choosing the index.

## What was tried to break it

Comparison at the opening values (radial TIR 0.25, face TIR 0.30, ovality 0.04, tack bump 0.06, distortion 0.12, bias 0.10, noise 0.03, setup error 0.3 mm; all illustrative), residual at the dot over 380 degrees, radial rms / vertical rms: none 0.254 / 0.196; scan 0.195 / 0.024; look-ahead 0.195 / 0.026; at the dot 0.105 / 0.064; look-ahead plus dot 0.101 / 0.060.

1. **Re-seating the tube between scan and bead.** The map is of a tube that is no longer there. Residual grows with the re-seat error (slider up to 0.3 mm; the nest has 0.2 mm radial clearance). What changes: do not touch the tube; check with a second look-ahead reading that the map still fits.
2. **Thermal distortion.** The 6.35 mm lip is unbacked above the weld and "will distort" (**[repo]** pressure-vessel.md); a cold map cannot contain what the heat does, and a look-ahead camera sees the seam before the heat arrives, so both miss it. Only an eye at the dot sees it. The size is **[unknown]**; the slider (0.12 mm, saturating with a 90 degree time constant) is a guess. In the comparison the distortion and bias, not runout, dominate what is left after scan or look-ahead (radial 0.195 vs 0.254 uncorrected).
3. **A biased sensor.** Every strategy inherits the sensor's bias. Calibrate against a ground-truth view (eyes-07).
4. **Setup error.** A dot 0.3 mm off at the start is a constant that a map made with the same sensor removes, but a look-ahead camera does not see the dot-to-camera offset unless calibrated; in the scene it is assumed calibrated.
5. **Bandwidth.** A 10 frame per second camera sees 0.0016 to 0.0019 mm of seam motion per frame at 8 mm/s. The observation can be slow, averaged, even repeated; the difficulty is accuracy and bias, not speed.

6. **A step at the bead start is not periodic, and a dry turn taken idle does not contain it** *(from freedom's exchange, section 3)*. Conflict: the map is indexed by turned angle and holds what repeats each lap; what it does not include is a step in the support's position at the start of the bead. Three sources are in the manual and the repo, each in a different hose: the wire feeder pushes 0.76 mm wire down its conduit beside the fibre at the grip base; the argon starts in a 6 mm tube at 15 to 20 L/min; the fibre is asked to emit at a bend radius of 350 mm rather than the 240 mm at which it may be stored. Size, per newton of pull change at the grip base (freedom's statics, illustrative): 1.44 mm radially and 4.22 mm vertically on eyes-01's elastic with nothing holding the tilt, 0.45 / 1.03 on a rigid base, 0.1 / 0.01 on the nose seat; the fibre's own recoil is 0.4 to 4 N at 350 mm and 0.9 to 8.7 N at 240 mm for a bending stiffness of 0.05 to 0.5 N·m². Assumption behind it: mine ("the setup error is assumed calibrated", scan and bead share the sensor and the support pose); theirs, that the support answers each change of load with a step. What the change alters: `freedom-13-map-and-step` puts three correctors on one time axis (the map for the periodic part, a load-cell force term that moves the trim as the step lands, the eye at the dot for creep and the rest); in this scene a bead-start step, a switch for the state the dry turn was taken in, and a mismatch slider are new. Idle dry turn: the whole step stays in the residual for the rest of the bead (0.6 mm radial: rms 0.41 over the lap, from 0.20); weld-state dry turn: the map holds it and what is left is the mismatch (0.05 rms at 25 %); a fixed look-ahead camera never sees the gun move; the eye at the dot follows the step with its lag (peak 0.24 mm in the first 30 mm, including the 0.3 mm setup error). What it leaves uncertain: whether the support moves at all when the wire feeds or the gas starts (Derek can measure it in five minutes: a dial gauge on the shell, laser disabled, jog the wire, open the gas, read the needle); and a cell in a soft support measures the support, so the force term wants a stiff cell.
7. **Which states is the dry turn taken in, and where does "scan and bead share the same sensor and support pose" stop being true?** *(freedom's question, section 3)* The list the scene now carries: fibre laid at the emitting radius or the stored one (the largest term in the estimate if the dry turn is taken with the fibre at the tighter stored radius); wire fed to the guide or retracted; gas on or off; the operator's hand on the gun or off (in the hand-held arrangements the hand is a load path of its own, and it lets go in a dry turn); tube warm or cold; and the trigger: the laser is off in a dry turn, so the dot is the red pilot and the melt pool, distortion and process light are absent. The statement holds for the sensor (same eye, same camera model, same bias) and for the pose only if every item above matches. It stops holding at the first mismatch, and at thermal distortion whatever else matches.

## Branches and combinations

`freedom-13-map-and-step` (freedom's branch and combination with `freedom-05-runout-table`: the map, a force term, the eye). With `eyes-01-gun-borne-eye` (the at-the-dot eye and its trim axis). With `eyes-06-dot-as-probe`: a sweep at each of several tube angles gives the map without a separate sensor. With `eyes-02-where-can-an-eye-stand`: the look-ahead placement (35 degrees of arc, at least 25 mm above the rim, sees the plate well but the wall face edge-on, 0.05 of square-on).

## Unresolved problems, questions for Derek

Size and shape of thermal distortion; whether tack welds stay put when heated; whether the nest expands or the tube warms enough to change the map between the dry turn and the bead; whether the corner ahead can be seen through melt light and fume (it is cold metal, so probably yes); how to make the scan sensor independent of the one that later closes the loop. Wave 3: with the laser disabled, does the gun's support or shell move when you jog the wire or open the gas? Does it move when you start emitting? (A dial gauge on the shell; the number the scene's step slider asks for.)

**Question for Derek:** with an indicator on the plate face during a hot bead, does the plate face move visibly (tenths of a millimetre) as the bead passes?

## Assumptions

Runout limits **[repo]** weld-rotation-rig.md (acceptance, not measured). Speeds 5 to 15 mm/s, weld radius 61.85 mm **[repo]**. Ovality, tack bump, distortion, re-seat, noise, bias and trim step are illustrative sliders. Wave 3: the bead-start step (radial size, vertical 1.5 times it, a ramp over 3 mm of bead), the dry-turn state and the mismatch are illustrative; the eye at the dot closes a loop at 4 corrections per second with gain 0.6, so it lags a step. The headline comparison above (scan 0.195 / 0.024 and so on) is for a step of 0. The correction is applied instantly (lag ignored: the seam speed is at most 0.02 mm/s).

## Sourcing pointers

None specific. The dry-turn sensor is any of the eyes (`sourcing/eyes.md`); an MLX90640 thermal camera ($68.99 Prime, low volume) could show the OD heating from outside as a post-hoc check; not proposed as a control input.

## Scene

`eyes-09-scan-then-weld` (custom 2D plot). Actuators (existing or proposed): turned angle, bead speed. Scene edits: strategy, look-ahead angle, runout, ovality, tack, distortion, re-seat, setup error, noise, bias, trim step.
