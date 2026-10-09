# datum-09-preplaced-filler-ring: the corner carries its own filler, and its own datum

No scene (sketch). Depth: sketch. Origin: swarm.

## Picture it

A split ring of 316L filler wire lies in the corner, sprung against the wall and resting on the plate. It is a bright, self-seating line in the pocket that a camera or a feeler can follow; and because the filler is already there, the wire feeder and its approach angle stop constraining how the gun is held.

## The proposal

Lay the filler in first instead of feeding it in. The ring's circle is exactly the seam's circle, it settles into the corner under gravity (the joint is a horizontal corner) and its own spring against the wall, and it turns the invisible corner into a visible, physically placed line. Two things follow. (1) Position: cameras and feelers track a distinct line rather than a corner, and the dot is aimed at the ring. (2) Geometry: the wire approach no longer needs the gun to lie tangent so that the wire is laid down correctly (Derek's own statement of the reason for the tangent approach [Derek, earlier conversation as recorded]); the gun's yaw about the vertical axis becomes free, and so does the wire bracket's position on the shell.

## What carries the loads, what establishes position, what is free or restrained

The ring rests on the plate and the wall; it carries nothing. Position: the ring is the seam. Free: the gun's yaw. The wire feeder disappears from the operating sequence.

## What software could command, observe, and what stays manual

Observe: the ring as a line (camera) or a bump (feeler, datum-04). Command: nothing new; rotator and any fine axes. Manual: forming and placing the ring; joining its ends; the laser sequence without wire feed.

## What was tried to break it

1. **Fusion of a preplaced ring.** *Conflict:* the weld is now a wire-in-corner fusion problem, not a fed-wire fillet. *Not for this study:* weld-process qualification is out of scope. *Recorded numbers* [calc/sketches.py; repo rig doc]: circumference 388.6 mm; the rig doc's calculated fillet leg at 8 mm/s travel and 12 mm/s wire feed is 1.17 mm, i.e. 0.684 mm^2 per unit length; 0.030 in wire is 0.456 mm^2, only 67% of that, and a single strand that supplies it is 0.93 mm in diameter (0.035 in is 0.89 mm).
2. **The ring will not stay put.** *Assumption:* gravity and spring hold it. *Uncertain:* the tube is standing vertical and the corner is horizontal, so it should settle; the 0.13 mm slip gap [derived from repo] is much smaller than the wire. Ring ends, springback and tack-welding it are open.
3. **Tangency.** *What is really established:* the gun's yaw is free only if the wire is the only reason for tangency. Derek's tangent statement is about wire lay-down; the *beam* angle in section (the tilt between plate and wall) still matters and still needs a roll and standoff.
4. **The ring as a datum.** *Conflict:* a bright wire on a shiny plate may glint. *Left standing.*

### From travel's exchange (wave 3: `exchange/travel--on--datum-w2.md` section 4; `scenes/travel-16-radial-plane`)

5. **Round 5: the claim was wrong.** *Conflict (travel):* "the gun's yaw about the vertical becomes free" is not what becomes free. *Assumption:* the wire is the only reason for the tangent attitude and yaw is what it frees. *What travel found:* with everything else held, 15 degrees of yaw moves the in-section beam tilt (the heat split between wall and plate) from 32.5 to 9.9 degrees, so yaw still turns the beam. What the wire ties the gun to is the wire bracket's arrival, and what becomes free is a family of attitudes in which the barrel stands in the radial plane over the bore, plus the direction of the bead and of the end-of-bead departure. *Consequences that make it worth having:* the gun's centre of mass falls from 118 mm to 50 mm (14 in the grip-up attitude), the upper ring needs no gap, a yoke holds the gun near its centre of mass, the fibre hangs straight up near the axis (drag arm 38 mm instead of 234), and the weld can go either way round (two halves of 190 degrees, 3.25 to 3.4 m of fibre). Rotation about the beam axis is free for the beam but twists the fibre 0.91 degree per degree. *Answer to travel's question:* I wanted two different things and named one: a visible, self-seating line to track (only the preplaced ring gives it), and freedom from the wire's arrival direction (a guide carried by the ring gives it, with nothing preplaced and no fusion question). *Smallest test I would accept for fusing a ring:* a scrap L in the laser (a 1/4 in plate on a tube offcut with a recessed corner), a 0.035 in ring laid in the corner, the recorded power and wobble with no wire feed, three passes, then a section: does it wet both sides, and does the ring stay put? *Leaves standing:* fusion (0.62 mm^2 for a 0.035 in ring against the 0.684 mm^2 the recorded fillet needs), two starts and two stops, the proxy's real cable exit, whether the head tolerates grip-up, the wire feeder's bracket on the ring.

## Branches and combinations

With datum-04 (a feeler that rides on the ring), datum-05 (tags) and datum-02 (camera-based signature). Not combined anywhere yet.

## Unresolved problems and questions for Derek

Is a preplaced filler ring a route you would consider at all, or is a fed wire a fixed part of the process? (Fusion qualification is a process question the study does not answer.)

## Assumptions

Circle radius 61.85 mm, wire 0.030 in, fillet leg 1.17 mm at 8 mm/s and 12 mm/s [repo]. Everything about how a preplaced ring would fuse is unverified.

## Sourcing pointers

ER316L wire in 0.035 in is a common MIG size [unchecked in this session]; no Prime listing was looked up.

## Scene id

None.
