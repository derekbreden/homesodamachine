# eyes-12 The dot lattice (software moves, a person or a video observes)

No scene. Origin: swarm (eyes framing). Maturity: sketch.

**Picture it.** A positioner steps the dot through a scripted grid of offsets over the corner, one point at a time, pausing at each. A phone on a stand records the whole run as one video. Afterwards, Derek, or a reviewer, or later a model, labels each frame: on the plate, on the corner, on the wall. The only signals the software has during the run are step counts.

## The proposal

Two ways of using the equipment differently. **(a) Software moves, observes nothing in the loop.** A scripted lattice (say 9 x 5 offsets radial by vertical, 0.25 mm apart) run with the laser off and the red dot on; the phone video plus the step counts at each pause are the record. Nothing is closed-loop, and nothing needs a calibrated sensor. The labels are made after the fact, by eye or by a model looking at the video. The outcome is a table: axis position (from steps) against what the dot did (plate, corner, wall), which is exactly the dot-to-corner offset in axis units, at lattice resolution. **(b) Software observes, a person moves:** the eyes of other ideas feed an overlay on a screen ("turn the radial knob 0.4 mm toward the wall"); the person turns a micrometer head. Same information, no actuator.

## What carries loads, what establishes position, what is free or restrained

Whatever positions the gun in another idea (a stage, or a hand-turned micrometer head). Position: the steps. The video camera is a fixed phone.

## What software could command, observe, and what stays manual

- **Command:** the lattice (axis steps, pauses). **Observe:** step counts; the video (post hoc). **Manual:** labelling; placing the phone; deciding the lattice.

## What was tried to break it

1. **Open loop drift.** Without feedback the lattice is only as good as the axis; a loose support (eyes-01) moves under it. What changes: put a reference (a printed feature on the tube, or a tag) in the same video frame so drift shows.
2. **The label is a judgement.** "On the corner" at 0.1 mm resolution needs a camera that resolves it; a phone at 20 cm gives about 0.05 mm per pixel (illustrative), the dot's own size is comparable. This is the same view problem as the sweep (`eyes-06-dot-as-probe`): the labels come out as the sweep's kink, found by eye.
3. **Not a control method.** It is a learning-data method: it produces the labelled pairs a model needs, once, for a given gun, tube and finish. Whether the mapping repeats for another tube (seat depth varies, **[unknown]**) is the question the data would answer.
4. **Speed.** A 9 x 5 lattice at 3 s per point is under three minutes: cheap enough to run before every session.

5. **A raster that reverses direction each row folds the lead screw's backlash into the labels** *(from freedom's exchange, smaller remarks)*. Conflict: on a lead screw or a stage with backlash, a serpentine lattice approaches alternate rows from opposite sides, so each label carries plus or minus half the backlash and there is no single map from actuator units to dot position. Assumption behind it: mine, that a scripted grid is a set of points. What the change alters: a lattice with a **unidirectional approach** (every point reached from the same side) costs roughly twice the time (a 9 x 5 lattice under six minutes at 3 s per point plus the return) and turns the backlash into one constant; a spring-loaded axis (freedom-01c's preload against a stop) makes that constant small. What it leaves uncertain: the size of the backlash, and whether a stick-slip axis (entry above in `eyes-06`) adds a second constant.

## Branches and combinations

The scripted version of `eyes-06-dot-as-probe`; the labelled-data half of `eyes-07-sectioned-tube` (which labels automatically with a direct view); a fallback for `eyes-01-gun-borne-eye` while its camera is being calibrated.

## Unresolved problems, questions for Derek

Nothing to build; it needs a positioner. **Question for Derek:** which motion is easiest for you to make repeatable by hand: a micrometer head, a lead-screw slide or a rail with a hand-turned knob?

## Assumptions

Lattice size, spacing, pause and phone resolution are illustrative.

## Sourcing pointers

None.

## Scene

None.
