# datum-23-wall-clip: the gun's nose stands on the wall at the station

Scene: `scenes/datum-23-wall-clip/index.html`. Depth: developed. Origin: branch and combination of `datum-04-corner-follower` (a feeler that reads the seam ahead of the dot, with no body) and `datum-16-loops-carry-rim-locates` (weight from above, location from the tube), wave 3. Numbers: `calc/wall_clip.js` (`wall_clip.out`), `calc/mate_harmonics.js`.

## Picture it

A printed hook on the gun's nose goes over the rim a few millimetres ahead of the dot, on the side the wire arrives from. A steel roller (blue) rolls on the bore just above the plate; a wheel (blue) rolls on the rim top; a spring-loaded pad (green) rolls on the outside, all on one radial line, so the wall is squeezed at one place and not bent. The gun's weight hangs from a balancer wire in the room (drawn faint). The tube turns; the roller follows the bore; the gun follows the roller. The plate is not known to the hook.

## The proposal

`datum-03` and `datum-16` put the gun on a ring round the whole circle. `datum-21` shows what that costs: a ring follows the tube's motion and none of its shape. A clip at the station reads the wall where the seam is welded, so it follows the tube's motion, its wall eccentricity, its ovality and its lobing, up to the lead between roller and dot. On the default illustrative tube the radial error at the dot is 0.10 to 0.12 mm rms for a room-fixed gun or a three-pad ring and 0.03 for a roller 10 mm ahead. It is the corner follower with a body: instead of a feeler whose reading a fine stage must act on, a stiff hook whose position is the gun's position.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** a balancer wire (or loops, or an arm) carries the gun's weight; the rim wheel carries only the share it is given; the pad spring's preload presses the roller onto the bore. The wall sees a squeeze: roller and pad on one radial line, contact half-width 7 micrometres at 8 N, no net force on the tube.
- **Position:** the bore wall at the station (radial) and the rim under the wheel (height). The plate is not known: seat depth and plate tilt stay in the vertical numbers (pair with `datum-22`).
- **Free / restrained:** along the seam the roller and wheel roll (free); the gun's yaw, roll and pitch about the hook are the holder's; a second wheel a few millimetres along the rim would fix the yaw (not drawn). Radially the wall holds an outward pull rigidly and an inward pull only up to the preload.

## What software could command, observe, and what stays manual

- **Command:** the rotator only. **Observe:** nothing required. A contact or hall sensor on the pad arm would say the clip is seated and preloaded; a hall sensor on the swinging arm would read the wall's shape at the station (that is `datum-04`'s feeler with a body). The dot is not observed.
- **Manual:** hanging the gun and setting the balancer's share; seating the clip on the wall ahead of the dot; the gun's radial trim once so the dot is on the seam; the preload against the pull.

## What was tried to break it

1. **Round 1: a lead is a phase error.** *Assumption:* the roller reads the wall the dot will meet. *What the numbers say:* it reads it s ahead, and a passive clip cannot delay: the gain is 2 sin(n s / 2R) of harmonic n (0.16, 0.32, 0.48 of harmonics 1 to 3 at 10 mm; 0.29, 0.57, 0.85 at 18). *Repair:* keep it short, or put an actuator behind it that delays the reading by s / v (2.1 s at 17 mm and 8 mm/s), which turns the passive hook into `datum-04`'s follower driving a fine stage. *Uncertain:* the sign of the lead's benefit at the harmonic that dominates.
2. **Round 2: gripping a thin wall.** *Assumption:* a clip grips from opposite sides. *What the numbers say* (`wall_clip.js` B): two opposite points ovalise a 1.65 mm wall by about 0.15 mm at 8 N (ring model, order of magnitude); a roller and pad on one radial line load it with a local squeeze. *Change:* pinch one place from both sides.
3. **Round 3: the cable pulls the gun off the wall.** *What the scene shows:* a pull toward the axis above the preload lifts the roller and the gun stops following (LIMIT badge; the trace falls back to the room-fixed one). *Change:* preload well above the pull (8 N against 3 N). *Uncertain:* the pull's size and direction (**[unknown]**); the balancer wire's sideways stiffness adds.
4. **Round 4: room beside the wire and the nozzle** (`wall_clip.js` E, kit proxy). Ahead of the dot the tightest gap is 1.4 mm at 6 mm, 2.2 mm at 10 mm, 3.6 mm at 14 mm. Behind the dot there is room but the bead and its heat. *Uncertain:* the real wire bracket and its outward lean (`datum-20`). *Also:* a bearing roller of the MR105ZZ class is 10 mm across (`sourcing/datum.md`), too big for this gap; the drawn roller is 5 mm.
5. **Round 5: drag.** A dry printed skid on the rim drags 1.25 N along the seam at 5 N of load (mu 0.25), most of the umbilical's margin; a wheel drags 0.05 N.
6. **Round 6: what a hook cannot know.** A longitudinal weld seam on the bore, if the tube is welded tube, is a step under the roller once per revolution that a ring on the outside never sees (slider in the scene). The plate below the rim is not known at all.
7. **Round 7: heat.** *Left standing:* steel only within 20 mm of the pool; a printed roller or wheel near the bead is not credible.

## Branches and combinations

- Branch of `datum-04-corner-follower` and `datum-16-loops-carry-rim-locates`; pairs with `datum-22-setting-ring` (the plate) and `datum-21-mates-on-the-tube` (the chart).
- `travel-15` and named-not-drawn: the follower's second output, yaw from two leads, could be nulled by tangent travel of the work; a hook with two rim wheels fixes yaw passively.

## Unresolved problems and questions for Derek

- Whether the tube is welded tube and has an inside seam; whether a steel roller may touch the bore of a finished tube (a fraction of a newton to 15 N); the umbilical's pull at the gun (a spring scale); where the wire lands and how far it leans (`datum-20`).

## Assumptions

- Kit proxy gun, wire and pose; clip sizes, preload, wall amplitudes, pull: illustrative. Roller radius 2.5 mm, wheel 3 mm, pad 4 mm.

## Sourcing pointers

`sourcing/datum.md` (wave 3): MR105ZZ bearings (weak sales evidence), mini ball transfer units, M6 ball-nose spring plungers, A3144 hall sensors.

## Scene id

`datum-23-wall-clip`.
