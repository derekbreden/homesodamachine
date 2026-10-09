# datum-10-clear-twin: a see-through replica of the corner gives the true offset

Depth: sketch as an idea; its yardstick use is drawn in `scenes/datum-17-yardstick-on-the-twin` (two sections of the same corner, real tube against twin). Origin: swarm.

## Picture it

A clear acrylic tube with a plate seated at the same recess stands on the rotator, so an ordinary camera outside sees the red dot sitting in the corner through the wall. A second camera looks down the open top. The pair gives the true dot-to-corner offset in three dimensions, so the cheaper estimators (tags, feeler, eddy, touch-off) can be calibrated against it before they are used on steel.

## The proposal

Every scene in this set infers a hidden quantity. A ground-truth rig for that quantity would let each estimator be tested and its systematic error found. The twin only has to be *optically* accessible, not welded: the red reference beam is 0.3 mW, 630 to 670 nm [manual p. 12], harmless to acrylic. Software conducts repeated dry-run experiments on the twin (move the gun, record the estimator, record the truth), which is the AI-conducted dry-run experiment Derek describes [Derek, Codex task].

## What carries the loads, what establishes position, what is free or restrained

As the estimator under test; the twin is a static work piece on the rotator. The truth is established by two cameras and the twin's known geometry.

## What software could command, observe, and what stays manual

Command: the gun's fine axes and the rotator; observe: the twin's two cameras (dot position against the corner) and the estimator's output. Manual: seating the twin, the gun's coarse aim.

## What was tried to break it

1. **The twin is not the tube.** *Numbers* [calc/sketches.py; sourcing]: the shelf tube is 125 mm ID and 130 mm OD, 6 in long: bore 1.3 mm larger than the steel's 123.70 mm and wall 2.5 mm against 1.65 mm. *Change:* calibrations that depend on wall thickness or bore radius carry a known constant; a twin turned or bored to the steel bore would remove it. *Uncertain:* which calibrations depend on it.
2. **Refraction.** *What the numbers say:* through a 2.5 mm acrylic wall a point appears shifted 0.145 mm at 10 degrees off the wall normal, 0.48 mm at 30, 0.82 mm at 45; zero at normal incidence. *Change:* view along the wall normal, or correct for the known shift.
3. **Steel is polished and opaque; acrylic is neither.** *Left standing:* glint, fume and hot bead are not reproduced.
4. **It cannot weld.** *Left standing:* thermal drift and melt position remain unobserved by this rig.

## Branches and combinations

Feeds datum-02 (a bias check for the sensor), datum-04, -05, -06, -07. Its second role is the requirement: a hand (or any arrangement) held over the twin is scored by an outside camera with no judge in the number, which is what `trials-11`'s yardstick needs for its first entry (`datum-17-yardstick-on-the-twin`). A notch tube (`trials-05` rung 3) gives the same for a 34 degree window: about five seconds of a 49 second lap. The twin's outside camera views along the wall normal; through a 2.5 mm acrylic wall a point appears shifted 0.145 mm at 10 degrees off it (below). Neighbours: `eyes-07` (a sectioned tube: one static gun pose), `use-11` (a gauge tube with a window).

## Unresolved problems and questions for Derek

Is a twin worth building before the first estimator exists?

## Assumptions

Refractive index 1.49 (handbook); shelf tube dimensions from the listing.

## Sourcing pointers

`sourcing/datum.md`: clear acrylic tube, 125 mm ID x 130 mm OD, 6 in, $15.99, 76 ratings (Prime filter; product page not opened).

## Scene id

`datum-17-yardstick-on-the-twin` (its use as the requirement's source). The twin itself is not drawn as a 3D part.
