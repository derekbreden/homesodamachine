# datum-20-dot-and-wire: two probes on one corner, and the vector between them

Scene: `scenes/datum-20-dot-and-wire/index.html`. Depth: developed. Origin: combination of `trials-03-dot-touch-probe` (scene), `trials-14-contact-sense` (idea) and `use-10-wire-first` (scene), with `datum-07-touch-off`. Exchange: `exchange/datum--on--trials-w2.md` section 4.

## Picture it

Two pictures at the station, magnified: the section (radial, height), with the plate, the wall, the red dot on the plate where the beam lands, and a gold ring for the wire tip on a line rising back to the upper left; and the plan (radial, tangent), with the wall as a curve receding as y squared over 2R, the dot, and the wire lying along the tangent to a tip a couple of millimetres upstream. Below, two number lines: the radial sweep (where the dot's knee falls, where the wire tip touches the wall) and the height sweep (where the dot is in focus on the plate, where the wire tip touches the plate), and what the AI concludes from them about the tip's offset from the dot, beside the truth.

## The proposal

The red dot is a probe of the wall (`trials-03`): its plate part vanishes from above when the dot's centre crosses the seam. The wire tip is a probe too (`trials-14`, `use-10`): jog it out with the laser off and a touch closes a circuit. The wire is the weld reference, not the dot: the procedure puts the wire on the arriving side of the puddle `[repo]`, and the dot is aligned to the melt only by the red-light adjustment `[manual pp. 25, 39]`. Run both probes on the same corner in one dry run and the difference of their readings, in the same axis coordinates, is the vector from the dot to the wire tip. It is the part of the dot-versus-melt term (a floor under every datum in the study) that a dry run can reach without emitting.

The wire is not at the dot: its line passes the dot by a miss that belongs to the shell and the guide, and the tip moves along the line with the feed.

## What carries the loads, what establishes position, what is free or restrained

Nothing carries anything here; any positioner that sweeps a radial and a height axis in tenths of a millimetre (the dot probe's one axis, plus the height axis of its second sweep). The wire is a springy 0.76 mm rod `[repo]` and carries no positioning load; its tip deflects when pushed.

## What software could command, observe, and what stays manual

- **Command:** radial and height sweeps; the wire's advance and retract (buttons today `[manual p. 18]`; whether software can drive the feeder is `[unknown]`).
- **Observe:** the dot knee and spot size by camera; a contact bit for the wire (continuity to the work lead; the ready lamp by camera, unchecked).
- **Manual:** the guide's aim; the interfaces to the laser box and the feeder; no interlock is defeated.

## What was tried to break it

1. **A straight wire on the tangent meets the wall.** The wall's inner surface at tangent offset y is y squared over 2R further out. A wire body of stick-out L leaning outward by gamma as it approaches clears it when sin(gamma) is at least about (L/2R)/cos(elevation) plus the wire radius term; for the drawn geometry (35 degrees elevation, tip 3 mm upstream, 0.3 mm miss toward the bore) the minimum lean is 4.8 degrees, and at 0 the wire is 0.77 mm inside the wall. `use-10`'s "wire against the wall" limit is this condition without its number.
2. **The tip moves along the wire, not along the seam.** Per millimetre of feed at 35 degrees elevation and 6 degrees lean: 0.57 mm in height, 0.09 mm radially, 0.81 mm along the seam. One millimetre of stick-out error is about 0.6 mm of tip height. Each weld ends with the wire cut or retracted `[repo]`, so the stick-out is reset, not remembered: the vector has to be re-measured (or the feed measured by the same touch) at each start.
3. **The wall touch is the tip's, at the tip's own tangent position.** The wall there is 0.05 mm further out at 2.4 mm upstream, 0.2 at 5 mm. The AI subtracts it from the assumed geometry: an error of 0.5 mm in y costs 0.5 x 5/61.85 = 0.04 mm.
4. **The height reading leans on the focus.** The tip's plate touch is sharp; the dot's focus is not (the spot-size curve is flat near focus, `trials-03`). The scene gives the focus three times the noise; the vertical part of the vector inherits it. A height sweep with dither on both, or a stylus touch of the plate in the same run (`datum-07`), reads it better.
5. **Bend.** A 0.76 mm wire deflects on touching; the scene lets a fraction of a 0.1 mm bend into the readings. `trials-14` gives 0.76 mm as the wire's touch resolution; the double touch (fast then slow, `datum-07`) reduces it.
6. **Left standing:** the wire tip is where the wire is, not where the melt is (the puddle is a couple of millimetres long and the wire enters at its leading edge); whether the ready lamp or a spare pin can serve as a contact sense; the real guide's adjustments; the process effect of a wire that is 0.6 mm too high.

## Branches and combinations

- Uses `trials-03` (the dot probe), `trials-14` (contact sense), `use-10` (the wire in the dry lap), `datum-07` (a stylus in the same run), `datum-15` (the dock coupon can carry this vector at every visit, so a change in the guide or the head shows as a change in it), `trials-06` (the mule could carry a wire stub with its own contact sense, so the vector is found in its shell first), `datum-11` (the witness pass is the only thing that reaches the melt itself).

## Unresolved problems and questions for Derek

- With the clip on and the laser disabled, does anything (a lamp, a beep, the screen) change when the nozzle or the wire touches the tube (`trials-14`)?
- Where does the wire land against the dot on your unit? Jog it onto a sheet of paper under the dot and photograph both (`use-10`). How is the wire's outward lean set today?

## Assumptions

Corner `[repo]`; wire 0.76 mm `[repo]`; beam 32 degrees from vertical `[illustrative]`; elevation, lean, feed, miss, bend, noise: sliders, illustrative. The wire's line is straight; the sweeps are ideal (the height sweep ignores the tan 32 degree shift of the dot along the plate, the confound `trials-03` treats).

## Sourcing pointers

None new: probe class from `datum-07`; the wire is the ER316L on hand `[repo]`.

## Scene id

`datum-20-dot-and-wire`.
