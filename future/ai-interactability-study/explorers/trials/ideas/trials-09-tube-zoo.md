# trials-09-tube-zoo: printed tubes with errors put in on purpose

Shown in `scenes/trials-05-artefact-ladder` (rung 4 with its four sliders; drawn exaggerated, numbers exact).

## Picture it

A shelf of white and grey tubes that look like the real one: some have the plate seated 1 mm deep, some 1 mm shallow, some with the plate offset in the bore, some slightly oval, some with the plate face tilted. The AI knows exactly which error each one carries. It can run every experiment on the whole shelf overnight, with nothing to scratch and nothing to weld.

## The proposal

Print 127 mm OD by 152 mm tall tubes on the existing Bambu printers **[Derek]** with a plate seat at the real recess, and vary the designed errors: plate depth, plate lateral offset, ovality, tilt. Use a small designed experiment (a handful of levels per factor, spread over the space, not a full grid) so that "how does the rig respond to each kind of tube error" has known answers. The tube is a known population with ground truth by construction, and can be pushed beyond what a real tube would do.

## Carries, locates, free

The puck or the nest carries it; the errors are in the tube, not the seating.

## Software

Observe: dot-to-seam at each angle from the judge cameras; compare with the known designed error. Command: the rotator and the positioner. Manual: printing, labelling, measuring one or two printed tubes to check the print's own accuracy.

## Tried to break it

1. **Print accuracy.** Conflict: a printed bore is good to a few tenths of a millimetre at best, so designed errors smaller than that are noise in the truth itself. Change: use steps of 0.3 mm and larger; measure a few printed tubes with the same indicator. Leaves: the truth is known to the print's accuracy, not exactly.
2. **Blind to glare.** A matte plastic tube is far easier for a camera than polished 316L. Change: keep glare questions for the real tube (rung 5); a hybrid (printed wall, real laser-cut stainless plate) puts the reflective plate under the dot. Leaves: the wall's reflectance still differs.
3. **Translucent plastic.** Some filaments scatter the red dot below the surface. Repair: opaque, matte, mid-grey. Leaves: tested on nothing.
4. **Does the population cover the real one?** Real tube-to-tube variation has never been measured **[unknown]**, so the zoo covers a range someone guessed. Repair: measure ten real tubes for length, plate depth and ovality first (calipers).

## Combinations

`trials-05-artefact-ladder` (rung 4), `trials-04-seam-map-replay` (the map can be tested against known wobble), `trials-01-puck-swap` (pucks make swapping the shelf cheap).

## Unresolved

Q: How much do real tubes vary in length, plate seat depth and out-of-round? Ten measurements would size the zoo.

## Assumptions

Tube dimensions **[repo]**; printing capability **[Derek]**; the errors and their ranges **[illustrative]**.
