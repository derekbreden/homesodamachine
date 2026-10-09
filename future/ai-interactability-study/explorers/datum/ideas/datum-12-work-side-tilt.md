# datum-12-work-side-tilt: do one of the three rotations on the work, with a wedge

No scene (sketch). Depth: sketch. Origin: swarm.

## Picture it

The reference orientation scene has three rotations about the laser dot. One of them, the hole-axis roll (about the horizontal line through the dot and both port centres), tilts the whole gun. Doing that one on the *work* instead of the gun means tilting the rotator, and the tube with it, about that same line: a printed wedge under the rotator base, its ridge line running from the tube axis to the station, so the dot stays where it is and the gun stays where it is.

## The proposal

Rotating the tube and its rotator about a line through the dot and the tube axis leaves the dot on the seam. The seam is a circle, so as the tube then spins, the station keeps meeting the same circle: the corner's orientation at the dot is set by the wedge angle and is the same at every table angle. The gun is relieved of that rotation. It is a fixed, set-once adjustment, not a mechanism, and the orientation scene's own note ("the dial reads 35 degrees at the reference mounting inclination" [repo, weld-position.md]) suggests that a mean tilt is normal.

## What carries the loads, what establishes position, what is free or restrained

The wedge carries the rotator (the tube plus rotator mass is [unknown], the rig doc gives 1.40 / 2.01 kg for the rotating mass [repo]). It establishes the corner's orientation relative to the gun by construction. Nothing is driven.

## What software could command, observe, and what stays manual

Nothing new. It changes what the gun-side mechanism has to do: two remaining rotations instead of three. Manual: choosing and fitting the wedge.

## What was tried to break it

1. **The tilt axis must pass through the station.** *Conflict:* tilt about any other line moves the dot up and down as the tube turns. *Change:* the wedge ridge runs from the tube axis to the station azimuth, which is fixed on the bench. *Uncertain:* the bench clamp holes (four 10 mm, [repo]) let the rotator shift; that changes the ridge line by the clamp play.
2. **The rotator on a slope.** *Conflict:* at large angles the printed ball race sees side load and the motor and belt tilt with it. *Assumption:* the race tolerates it [unknown]. *Change:* keep the wedge small (a few degrees to ten); large tilts stay on the gun side.
3. **The full range.** *What the scene dials say:* the hole-dial range is about 120 degrees (-25 to 95 in the reference scene, illustrative); a wedge only replaces the mean of it. A cradle with a range is a bench-scale goniometer, and heavy: the dot is 232 mm above the bench and the rotator base only 36 mm, so the arc radius would be about 200 mm.

### From travel's exchange (wave 3: `exchange/travel--on--datum-w2.md` section 5; `explorers/travel/ideas/travel-17-risley-wedges.md`)

4. **Round 4: a wedge pivots at the bench, not at the dot.** *Conflict (travel):* the seam stands 232.05 mm above the feet [derived: tube bottom 86 mm above the bench, seam 146.05 mm above the tube bottom], so 1 degree of tilt about a bench-level line moves the seam 4.05 mm sideways (20 mm at 5 degrees, 40 at 10) and drops it 3.5 mm at 10 degrees; keeping the station where it is instead moves the seam 15.5 mm radially at 10 degrees. I re-ran it: 232.05 tan(1 degree) = 4.05 mm; travel is right. *Assumption:* "rotating the tube and rotator about a line through the dot and the tube axis leaves the dot on the seam". *Answer:* I meant the ridge at the base, and "the dot stays where it is" was wrong: a wedge under the base cannot pivot about a line through the dot. What stands is the set-once form, with the gun placed after the tilt; a wedge changed between experiments moves the seam 4 mm per degree and needs the gun or a stack to follow. *What travel adds (adopted as reading, not built):* the station azimuth against the lean chooses which rotation the tilt supplies (alpha cos(psi) in the radial section, alpha sin(psi) along the tangent), so one fixed wedge plus where the gun stands gives a mix; two wedge rings on a bearing (a Risley pair) make the tilt adjustable, 0 to 2a in any direction, with a reduction of about 11 to 1. *Leaves uncertain:* what mean inclination Derek actually uses; the printed race under 5 to 17 percent of the weight sideways at 3 to 10 degrees; a virtual pivot at the dot needs an arc (`travel-03b`).

## Branches and combinations

Any gun-side arrangement (datum-03 boom, an arm) gets one fewer degree of freedom to provide.

## Unresolved problems and questions for Derek

What mean inclination do you actually use? Is a fixed wedge acceptable to the rotator's mounting (four bench holes)?

## Assumptions

Dials, opening pose, dial range: the reference scene's, illustrative. Heights: rig doc [repo].

## Sourcing pointers

None; a printed wedge.

## Scene id

None.
