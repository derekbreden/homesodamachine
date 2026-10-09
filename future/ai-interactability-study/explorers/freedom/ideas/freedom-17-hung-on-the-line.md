# freedom-17: hung on the fibre's line (a sled pivot on the roll axis, drawn in the kit's geometry)

Scene: `scenes/freedom-17-hung-on-the-line`. Origin: combination (branch of `freedom-08-gravity-tilt`, combines `freedom-08-gravity-tilt` and `borrowed-15-sled-keel`). Depth: developed. Numbers from `calc/34-pivot-on-line.cjs`; every mass, inertia, stiffness and force is **illustrative** (the gun's mass and centre of mass are **[unknown]**).

## Picture it

A side view of the kit's gun at roll 0, drawn to scale, with the bench, the tube seen from the side and a dashed teal line running from the dot through the grip base and beyond: the roll axis, the fibre's line. An amber ball on that line is the pivot, a brass keel hangs from it on a post, a grey plumb line drops through it, and a white dot marks the gun's centre of mass. A blue arrow at the far end of the line is the cable's weight share at the boot exit, 709 mm from the dot, with its lever to the pivot dashed. Slide the pivot along the line and watch the keel swing from one side of the plumb to the other.

## The proposal

borrowed asked (exchange on freedom-08, section 3) whether the pivot should go on the fibre's line, so that the cable has no lever, and the keel and trim do the rest. The scene answers with the kit's numbers. On the roll axis, a force along the line has no torque about the pivot; the fibre's straight span (freedom-16 route D) lies on that line. The keel sets the gravity spring as in borrowed-15 and here also sets the balance: the pivot on the line is not above the centre of mass, so the keel must hang to the other side of the plumb by as much as the balance needs.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the pivot carries the gun, the keel and the cable's weight share; an arm or balancer (not drawn) carries the pivot.
- **Position of the dot:** the pivot's position plus the pivot-to-dot lever (equal to the distance q along the line) times the tilt.
- **Free:** the vertical-axis turn (no gravity spring), the pivot's friction.
- **Restrained:** pitch, by gravity through the keel; optionally by a tail bridle (the seat of freedom-01b).
- **Driven:** nothing in the scene; the trim mass of freedom-08 is the only actuator.

## What software could command, what it could observe, what stays manual

- **Command:** the trim mass along the shell.
- **Observe:** tilt from an IMU on the shell (eyes-11); the sideways force at the release point from a load cell in the rail cord (freedom-16).
- **Manual:** the pivot bracket, the keel's size and place, the fibre's route.

## What was tried to break it

**Entry 1. The line is not where the centre of mass is (borrowed's question on freedom-08, section 3).**
- Conflict: at roll 0 with the illustrative centre of mass, a pivot 150 mm from the dot on the roll axis has the centre of mass 74 mm above it (an upside-down hang) and 4 mm to the side; at 200 mm it is 49 mm above and 47 mm to the side; at the grip base (279 mm) it is 9 mm above and 116 mm to the side. Without a keel the hang is unstable everywhere below the grip base.
- Assumption: any point on the fibre's line is a usable pivot, and it will hang the gun in the working pose.
- Change: a 0.6 kg keel 200 mm below the pivot makes the hang stable (0.14 N·m/rad at 150 mm, 0.45 at 200, 0.94 at 279) and, hung 42 mm to the tail side (150 mm), 49 to the nose side (200 mm) or 193 (279 mm), balances it. The keel does two jobs: it sets the spring and it cancels the offset.
- Leaves uncertain: the real centre of mass, which moves all of it; the keel's post clashing with the tube or the bench (the scene badges both; it clears at these settings).

**Entry 2. Gravity cannot hold against the cable.**
- Conflict: the S-boot's release point is 709 mm from the dot, about 440 mm of horizontal lever from a pivot at 200 mm. The span's weight share (0.6 N) is a torque of 0.26 N·m that the keel's offset balances; what cannot be balanced is a change. 0.03 N of sideways force at that lever (freedom-16: an anchor that gives 5 mm) is 13 N·mm; against 0.45 N·m/rad it is 1.7 degrees, about 6 mm at the dot.
- Assumption: the plumb-bob's stiffness is enough once the cable's force has no lever. The force along the line has none; the sideways force at the release point has the longest lever in the arrangement.
- Change: to hold 0.1 mm the spring must be about 26 N·m/rad, sixty times what a 0.6 kg keel gives, and a heavier keel does not close the gap (mass grows the payload and the room). So: the plumb-bob is a trim, not a locator, for every route that lets go far from the pivot.
- Leaves uncertain: the size of the step (round number); the fibre's real EI (the step scales with it).

**Entry 3. A fairlead at the pivot would remove the lever, but only where the fibre is.**
- Conflict: if the fibre passes through a hollow ball at the pivot (a pin, so no couple; the force goes through the pivot), the cable's lever about the pivot is zero and so is the step. But the fibre leaves the grip base at 279 mm along the line; a hollow ball at less than that needs the fibre to double back.
- Assumption: the pivot can be where the fibre is.
- Change: beyond the grip base (q 279 to 420 mm) the scene's fairlead switch removes the lever (dot shift 0.00). There the centre of mass is 116 mm or more off the plumb, the keel must hang 190 to 450 mm across, and the lever from pivot to dot is 279 mm or more, so tilt costs 0.28 mm per 0.001 rad and the pivot still has no stiffness of its own beyond gravity.
- Leaves uncertain: whether a printed hollow ball 350 mm from the dot fits the fibre's bend limit (the fibre must enter and leave along the line).

**Entry 4. The tail bridle supplies what gravity cannot, and the pivot on the line then buys little.**
- Conflict: 20 N·m/rad (freedom-01b's seat with its tail wires) brings the same step to about 0.13 mm at 200 mm; 30 to 0.09 mm.
- Assumption: a pivot on the line helps a stiff seat.
- Change: the axial part of the cable's force has no torque about a ball on the line: 36 N·mm per newton at the barrel seat against zero. That is a small gain for a seat that is already stiff; the statics setup for a seat ball off the barrel did not converge in this session (the tail wires' lengths and the cone's apex have to be solved together for a ball 44 mm below the barrel), so the seat on the line is an estimate here, not a result.
- Leaves uncertain: a proper statics run of the seat on the line.

## Branches and combinations

- **freedom-08** stays as drawn (the plumb-bob at the housing top); its scene gained the cable's lever and couple, the period and a damper, so the comparison can be made there.
- **borrowed-15:** the keel, the damper and the anchor at the pivot; this scene adds the kit's geometry and the balance.
- **freedom-16:** the cable's release point and its steps.
- **freedom-01b:** the seat with its ball on the line (entry 4).
- **borrowed-13:** a hexapod's software pivot removes the need for gravity altogether, at the price of six actuators.

## Unresolved problems, and questions that need Derek's observation

1. **Where does the gun balance?** Hang it from a thread at two points on the shell and mark the vertical lines (also needed by every other idea): it moves every number here.
2. **Drop time.** Hang the gun from a thread at the candidate pivot (the point on the line 150 to 200 mm from the dot, measured on the shell) and time ten swings: the period gives K/I directly.
3. Whether a bracket from the barrel collar can reach a point 85 mm below the barrel, in front of the grip, without meeting the hand grip or the wire guide: a fit test with the printed shell.

## Assumptions

- Kit proxy gun at roll 0, hole dial 30, vertical 0 (the gun's plane is vertical); roll axis 279 mm, 30 degrees above horizontal. Gun and shell 1.2 kg, centre of mass (0, -18, 178) local, inertia about it 0.0075 M kg·m²: **illustrative**.
- Keel 0.6 kg, 200 mm below the pivot (borrowed-15). Cable weight share 0.6 N at 709 mm and a step of 0.03 N (freedom-16 route D at EI 0.1): **illustrative**.
- Small-angle statics in one plane: restoring stiffness = g·Σ m·(height of the mass below the pivot); the cable's weight share acts above the pivot and lowers it.

## Sourcing pointers

Nothing new: borrowed-15's FLYCAM HD-3000 (3.5 kg, $178) and fluid heads (borrowed's sourcing) are the bought sleds; a thread is enough for the first test.

## Scene

`freedom-17-hung-on-the-line`.
