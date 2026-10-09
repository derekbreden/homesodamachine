# travel-17-risley-wedges: two wedge rings under the rotator (work-side tilt, in two rotations)

No scene (sketch; numbers in `calc/11-wedge-abbe.mjs`). Origin: branch of `datum-12-work-side-tilt`, with my `travel-03-dot-centred` (the work-side cradle). Exchange wave 2, section 5. Depth: sketch. Thin region: the work in another orientation.

## Picture it

Under the rotator's base lie two printed rings, each a wedge of a few degrees, stacked on a 12 in bearing. Turn one ring against the other and the tilt they add is any size from nothing to twice the wedge angle, in any direction. Set once, they tilt the tube, the tilt is the corner's orientation relative to the gun, and the gun stands in a fixed attitude. Motorised, they are two rotary axes with a reduction of about 11 to 1 and no arcs.

## The proposal

datum-12 does the hole-axis rotation on the work with a fixed wedge whose ridge runs from the axis to the station, saying the dot stays where it is. Three corrections and one extension, from `calc/11`:

1. **A wedge under the base tilts the rotator about the bench, not about the dot.** The seam is 232.05 mm above the feet **[derived]**, so 1 degree of tilt moves the seam point 4.05 mm sideways (20 mm at 5 degrees, 40 mm at 10) and drops it 3.5 mm at 10 degrees; keeping the station where it is instead moves the seam 15.5 mm radially at 10 degrees. A wedge set once with the gun placed after does not care; a wedge changed between experiments moves the seam 4 mm per degree and needs the gun or a stack to follow. Only a virtual pivot at the dot (an arc, `travel-03b`) keeps the dot where it is.
2. **The station azimuth chooses which rotation the tilt supplies.** A tilt is a vector: at a station psi from the lean it is alpha cos(psi) in the radial section (the beam-versus-plate angle) and alpha sin(psi) along the tangent (pitch). One fixed wedge plus a choice of where the gun stands gives any mix of the two, not just the hole-axis roll.
3. **Two wedge rings (a Risley pair) make the tilt vector adjustable**: magnitude 2a cos(delta/2), direction the mean. With a = 5 degrees, 0 to 10 degrees in any direction; one ring turned 1 degree changes the tilt by 0.087 degree at most.
4. **Cost.** The seam displacement (4 mm per degree) must be followed, and the printed ball race sees sin(alpha) of the weight sideways (5 to 17 percent at 3 to 10 degrees; 2 to 5 kg unknown).

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the bench through the bearing and rings to the rotator base. **Establishes position:** the wedge angles (by print and by rotation). **Free / driven:** two ring rotations (hand, or a motor with a belt or worm on each ring).

## What software could command, observe, and what stays manual

- **Command:** two ring angles if motorised. **Observe:** ring angles by step count; the dot by whatever sensor. **Manual:** the gun's placement after a tilt change.

## What was tried to break it

1. **The seam runs away.** *Change:* set once, or an XYZ stack of tens of millimetres (`travel-01` ranges are +-12 mm). *Leaves:* range against a 4 mm per degree lever.
2. **The race.** *Assumption:* a printed race tolerates 10 percent side load. *Leaves:* unmeasured.
3. **Process position.** A tilted joint changes the pool's position relative to gravity; a few degrees is small. *Leaves:* Derek's call.

## Branches and combinations

- With `travel-03-dot-centred` (arcs) as the alternative that keeps the dot fixed. With `travel-16-radial-plane`: a fixed radial-plane attitude plus a set-once tilt covers the beam angle without a yoke pivot.

## Unresolved problems and questions for Derek

- What mean inclination is used, and what range of the three orientations does he change between welds? Whether the rotator's four bench clamp holes tolerate a 20 to 40 mm shift of the seam.

## Assumptions

- Feet-to-seam 232.05 mm **[derived]** (tube bottom 86 mm above the bench, seam 146.05 mm above the tube bottom **[repo]**); wedge angles 3 to 5 degrees, masses 2 to 5 kg: illustrative.

## Sourcing pointers

`sourcing/travel.md` 23 (12 in lazy Susan bearing).

## Scene id

None.
