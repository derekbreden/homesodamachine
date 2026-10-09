# trials-21-rim-vs-seam: does the rim foot help?

Scene: `scenes/trials-21-rim-vs-seam/index.html` (rough). Origin: branch of `borrowed-07-tonearm`, with the ball of `datum-04-corner-follower`. Exchange: `exchange/trials--on--borrowed-w2.md`, section 5.

## Picture it

Three lines over one revolution of the tube: the dot's height error with the gun locked (grey), with a tonearm foot riding the rim (amber), and with a small ball riding in the inside corner (teal). Move the slider for how far the rim is from parallel to the plate face and the amber line grows until it is taller than the grey one: the foot has stopped removing the tube's wobble and started adding the tube end's squareness.

## The proposal

Borrowed-07 lets the tube's own rim set the dot's height. That removes what the rim and the plate face share (the turntable, the nest and the plate seat tilt the whole tube), and adds what they do not share: the tube end's angle against the plate face. The scene uses one number for the rim-to-plate distance (a constant "recess error" slider); it is a function of angle. A rim that is off parallel to the plate face by an angle e gives a differential of 63.5 tan(e) mm at the station: 0.11 mm for 0.1 degrees, 0.33 mm for 0.3, 0.55 mm for 0.5. The face runout the rig accepts is 0.30 mm TIR, 0.15 mm amplitude **[repo]**. Break-even is atan(0.15 over 63.5) = 0.135 degrees. The corner ball reads the seam itself (radial and vertical) and needs no such assumption.

## What carries the loads, what establishes position, what stays free

The arm (or nothing, in the scene) carries the foot; the contact is the reference. Nothing is driven; the rotating tube moves the arm. The gun is on the arm in borrowed-07, or on another support.

## What software could command, observe, and what stays manual

- Command: nothing.
- Observe: the arm's angle encoder is a free trace of foot height against rotator angle; a second indicator on the plate face (or the judge's dot-height reading) gives the seam's; the difference over one revolution is the number.
- Manual: reading the two indicators on a few tubes.

## Tried to break it

1. **The differential.** Numbers above. Assumption: rim height tracks seam height (the plate depth is a constant). Change: measure the differential per tube before building; if it is under about 0.1 degrees the rim foot helps, otherwise the seam map (`trials-04`) learns the differential the foot leaves. Leaves: the rim's real squareness is unknown.
2. **How the plate is seated decides the sign.** If each plate's recess is set from the rim with a gauge, the plate follows the rim by construction and the differential is small; if it is set from the far plate through the rod or by feel, it is independent of the rim. The rig doc's acceptance step already names "square the tube end or correct the end-cap seat" **[repo]**. Leaves: unknown how it is done.
3. **Everything here is a rigid tilt.** Real rims have burrs and bumps; the foot's wear and friction drag are not drawn.

## Branches and combinations

- The corner ball as the tonearm's stylus (two pivots, a diagonal preload): not drawn; `datum-04` has its clearance and tack numbers.
- Feeds `trials-04` (the seam map learns the differential the foot leaves) and `trials-11` (one more support for the yardstick).

## Unresolved, and questions for Derek

- Q: with two indicators, one on the rim and one on the plate face, read over one revolution on three tubes: does the rim track the plate face? (How big are the two amplitudes, and are they in phase?)
- Q: how is the 6.35 mm recess set: a gauge from the rim, the rod between the plates, or by feel?

## Assumptions

Rim radius 63.5 mm and seam radius 61.85 mm **[repo]**; accepted face runout **[repo]**; the wobbles are single sines and the rim is the plate face plus one differential sine; ball noise 0.02 mm **[illustrative]**.

## Sourcing pointers

None.

## Scene

`trials-21-rim-vs-seam`
