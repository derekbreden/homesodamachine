# travel-16-radial-plane: no wire, gun over the bore, and what that frees

Scene: `scenes/travel-16-radial-plane`. Origin: combination of `datum-03-rim-crown`, `datum-03b-orbiting-crown` and `datum-09-preplaced-filler-ring` (which has no scene), with a branch of my own (the wire guide carried by the ring). Exchange wave 2, section 4. Depth: developed. Numbers: `calc/09-radial-plane.mjs` (`calc/09-radial-plane.out`), reproduced by the scene.

## Picture it

The crown of datum-03 on the tube, but the gun does not lie along the tangent: it stands in the radial plane, nozzle inside the bore near the wall, barrel running up and toward the axis, its housing held between the two legs of a yoke that rises from the upper ring to trunnion pins on the housing's sides. Pivot it in the yoke and the beam angle in the radial section changes; clamp it. The centre of mass is inside the ball ring, so there is no counterweight, and the upper ring is a full circle. In one variant the wire is gone (the filler is in the corner); in another the wire guide stands on the ring and the gun is free of it.

## The proposal

Derek's reason for the tangent handle is the wire: "so that the wirefeed is laid down correctly" **[Derek]**. In the kit's proxy the wire bracket is what ties the gun to the tangent, not the beam. Remove the wire from the gun and the attitude is free to change. Two ways: datum-09's preplaced filler ring (no wire at the gun at all), or a guide carried by the ring that keeps the fed wire's arrival (from the tangent side, about 38 degrees above horizontal) while the gun stands in the radial plane. The kit's own reference scene reaches the radial-plane attitude at the far end of its 'vertical' dial (-90 degrees; roll 0, hole dial 35 = attitude B), so it is inside the range the reference scene already draws.

What it changes (`calc/09`, kit proxy, illustrative):

- **Balance.** The gun's centre of mass is 118 mm from the axis in the opening pose (A), 50 mm in B, 14 mm in B2 (grip up, over the axis). datum-03's round 3 needs a counterweight as heavy as the gun; B does not (the scene's assembly figure, with yoke and ring masses, is 39 mm against the 66 mm ball ring).
- **The ring.** The barrel is over the bore, so the upper ring needs no gap for it and the clash test passes with a full circle.
- **Holding.** A yoke with trunnions on the housing sides holds the gun near its centre of mass, and its pivot sets the beam angle in the radial section (the heat split between wall and plate). A bipod or bridge is stiffer than a boom 118 mm out.
- **The cable.** B2 hangs the fibre straight up from near the axis (drag arm 38 mm instead of 234 in the tube-turns crown); in the orbiting crown the same exit twists the fibre 1:1 with the orbit. B leaves radially outward at r = 167 mm, like A (r = 234 mm).
- **Orbit.** The exit direction is not the fix: A and B both leave radially outward and need a 142 to 155 degree turn before the fibre can run round the tube at bend radius 350 mm; the G1 route gives 5.6 m (A) and 5.8 m (B) for a continuous 380 degrees against a 5 m fibre (datum-03b's own figure for A: 5.6 m and 262 mm at a 700 mm track). **What the missing wire does buy is a weld that can go either way round**: each half is 190 degrees from the first tack, 3.25 m (A pose) or 3.39 m (B), inside the 5 m, with every bend at or above 350 mm by construction. A quarter turn does not end tangent to a concentric track, so a 90 degree route cannot close on a circle round the axis; the construction is in `calc/09` section 4.
- **Lift-off and swap.** If the sequence has an end-of-bead lift-off at all (unconfirmed: guide 46 says only to release the trigger, then the pedal), then with no wire there is no wire break-off, so the head may leave in any direction at the end of the bead. For a room-fixed gun (not a crown) B's barrel lies in the x-z plane with the tip 7.5 mm above the rim, so the tube can slide out either way along y; in A the barrel lies along -y and only the slide away from it is free (`calc/05`, `calc/07`). In a crown the gun rides with the tube, so the swap is the crown's (`travel-14b-crown-cartridge`).

What is not freed: **yaw about the vertical still turns the beam** (with the other dials held, 15 degrees of yaw moves the in-section tilt from 32.5 to 9.9 degrees). Rotation about the beam axis is free for the beam and for the wobble to within a cosine (94 percent of the swing width across the seam at 20 degrees) but twists the fibre 0.91 degree per degree, because the kit's cable exit leaves along the dot-to-grip line, which is 25 degrees from anti-parallel to the beam; the grip base swings 2.06 mm per degree.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** rim, lower ring (turns with the tube), balls, upper ring, yoke, gun; the gallows or track carries the umbilical.
- **Establishes position:** as datum-03 (rim and outside), plus the yoke's pivot and clamp for the beam angle.
- **Free / restrained / driven:** the ring's azimuth is free (tether, `travel-14`); in orbit mode a proposed drive turns the ring; the beam angle is hand-set.

## What software could command, observe, and what stays manual

- **Command:** the rotator (turns mode) or the ring drive (orbit mode). **Observe:** ring angle by step count. Blind: the dot, twist, wrap.
- **Manual:** the yoke angle and clamp; laying the filler (datum-09) or setting the ring-carried guide; re-laying the cable as a mirror image between halves; unwinding.

## What was tried to break it

1. **Assumption: the exit direction decides the orbit's cable.** *What the scene shows:* it does not (above). *Leaves:* the real exit direction (unknown).
2. **Assumption: yaw becomes free.** *What the numbers say:* it does not; the beam turns.
3. **The wire guide on the ring.** *Conflict:* the manual lists a wire-feeding bracket that mounts on the gun; the conduit's drag now loads the ring; the wire-to-dot alignment is a hand trim on the ring. *Change:* the scene draws it: about 30 mm of arm because the reference guide already sits just above the ring. *Leaves:* all three.
4. **The preplaced ring is not fused by this idea.** datum-09 records the numbers (0.62 mm^2 for a 0.035 in ring against the 0.684 mm^2 the recorded fillet needs at 8 mm/s and 12 mm/s; `sourcing/travel.md` 22). Nothing here depends on how; it depends on there being no wire at the gun.
5. **A two-part bead has two starts and two stops and a double-crater joint.** *Leaves:* a process question.
6. **Does the head tolerate B2 (grip up)?** Gas, lens drawer, cooling. *Leaves:* unknown.

**Wave 3 entry, from use's exchange (section 3, `use-16-yoke-escape`).** **The yoke's pivot at its stop has a long lever, and the reason to lift may not exist (use).** *Conflict:* rotating the gun about the trunnions is the beam-angle setter, the dock's pitch seat and, if a bead must end with the head leaving, an escape (10 degrees puts the tip 26 mm above the rim and 21 mm of standoff gained); the stop is a seat with a 200 mm lever to the dot (0.02 degree is 0.07 mm). With no wire at the gun the reason to lift is gone, so for that variant the pivot is only the dock's axis and the angle setter. *Assumption behind it:* the pivot is a hinge. *What the change alters:* recorded here; `use-16` (theirs) stays the drawing. The seat's rocking term and the nose-seat idea are in `travel-22-arm-docks-then-floats` and `calc/17`. *What it leaves uncertain:* whether the housing takes trunnions; the pivot's play and printed creep; the preload against cable pull.

## Branches and combinations

- `travel-14b-crown-cartridge`: the trunnion dock. `travel-14-exact-crown`: the seat under the lighter load.
- With `freedom-01b-nose-seat`: a collar sphere in a cone at the nose is another exact way to hold this attitude; the free rotation about the beam axis is the roll that seat leaves free.
- With `travel-04-return-seat`: no wire retract means the return seat's lift is not constrained by the wire.

## Unresolved problems and questions for Derek

- Weigh the gun and find its balance point; note the direction the umbilical leaves the grip base; is there a reason other than the wire for the gun to lie along the tangent? How far and in what direction does the head travel at the end of the bead today?

## Assumptions

- Gun geometry, the 0.15 / 0.55 / 0.30 mass split, the cable exit along the dot-to-grip line, the nozzle clearance: kit proxy, **illustrative**. Fibre 5 m, bend radii 350 / 240 mm, no twisting: **[manual]** p. 20. Yoke, boom, ring masses: illustrative.

## Sourcing pointers

`sourcing/travel.md` 22 (ER316L 0.035 in wire).

## Scene id

`travel-16-radial-plane`
