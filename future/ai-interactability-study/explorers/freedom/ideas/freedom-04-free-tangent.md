# freedom-04: the tangent is free, and the pivot sets the lever

Scene: `scenes/freedom-04-free-tangent`. Origin: swarm original (from the freedom framing). Depth: developed (a principle, with numbers). Arithmetic in the scene; the geometry is from `shared-context.md`.

## Picture it

A plan view of the tube's seam circle with the gun's dot on it. Slide the dot along the tangent and it hardly leaves the circle: 5 mm along costs 0.2 mm across. Tilt the gun about a pivot and the dot swings by the pivot's distance from it. A table lists, for each of the gun's six motions, how accurately it has to be held for a tolerance you choose.

## The proposal

Not an arrangement: a way of deciding **where an arrangement may be soft**. For a circular seam under a rotator [repo]:

- **Radial** and **vertical** motion of the dot go straight into the error, 1 : 1. These need the stiffest, best-observed elements.
- **Tangent** motion is second order: a slide *s* leaves the circle by s²/2r, r = 61.85 mm: 0.008 mm at 1 mm, 0.2 mm at 5 mm, 0.8 mm at 10 mm [derived]. A pendulum or long bungee along the tangent is nearly free.
- **Tilts** (pitch and yaw) about a pivot at distance ℓ from the dot move the dot by ℓ × angle: 0.28 mm/° at 16 mm (a pivot at the nozzle), 1.3 mm/° at 76 mm, 4.9 mm/° at the grip base 279 mm away [derived from the kit proxy].
- **Roll about the barrel axis** moves the dot not at all (it is on the axis); it turns the wire approach around the beam.

At a tolerance of ±0.3 mm at the dot (illustrative) the allowed errors come out as: radial 0.30 mm, vertical 0.30 mm, pitch and yaw 0.23° at a 76 mm pivot (0.06° at a 279 mm pivot, 1.1° at a 16 mm pivot), tangent slide 6.1 mm. The lesson for arrangements: hold r and z, put the pivot near the dot, let the tangent wander.

## What carries the loads, what establishes position, what is free or restrained

Nothing is carried here. The diagram says what to restrain: r, z, and the tilts through the lever; what to leave free: the tangent slide and the roll about the barrel.

## What software could command, observe, and what stays manual

- Commands: none.
- What it asks of the observer: the dot's radial and vertical position to a fraction of the tolerance, its tangent position only to a few millimetres, the tilt to whatever the lever converts to the tolerance. This is a specification for the camera or probe of the seeing explorers, by direction.
- Manual: choosing the pivot location on the shell.

## What was tried to break it

**Entry 1. "A hanging gun will sway."**
- Conflict: a pendulum's tangent sway is harmless for the dot, but a 5 mm sway of a 350 mm wire tilts the gun 0.8°, and 0.8° at a 279 mm pivot moves the dot about 4 mm. So the wire's tangent freedom is harmless only if the pivot is near the dot (or the tilt is restrained otherwise).
- Assumption: sway along the tangent is only a translation.
- Change: the nose seat of freedom-01b (pivot 56 to 126 mm from the dot) makes the same sway cost 2.2 to 5 times less.

**Entry 2. Tangent alignment (Derek's note).**
- Conflict: Derek's note that the handle must be tangent so the wire lays down correctly [Derek] means the tangent slide is not free for the wire: 5 mm of slide turns the seam direction 4.6° under a fixed gun.
- Assumption: the dot is all that matters.
- Change: the gun yaws with the slide (the scene's toggle) at no radial cost; or the slide is kept within the wire's tolerance.
- Leaves uncertain: how much approach angle the wire tolerates ([unknown]).

**Entry 3. The tolerance is a slider.**
- The ±0.3 mm and ±5° are not requirements; nobody has measured what the weld needs. The table is a relation between a tolerance and an allowed error, not a target.

**Entry 4 (wave 3, from borrowed's exchange, "smaller remarks"). A software pivot at zero lever costs stroke, not accuracy. Decision: answered (a note).**
- Conflict: the plot of dot displacement per degree against the pivot's distance from the dot (4.87 mm/° at the grip base down to 0.28 at the nozzle) assumes a pivot is a place on the gun.
- Assumption: the lever is geometry.
- Change: a hexapod's centre of rotation is a number set in software: its lever is 0 mm/° for any tilt, and the cost moves to the leg stroke, lever times angle: 5.5 mm for 10 degrees with the ring 18 mm above the dot, 19 mm with it at 140 mm (borrowed-13). The tangent slide can then carry a yaw at no radial cost, which is this scene's toggle done by the actuators instead of the geometry.
- Leaves uncertain: six actuators and a gap for the gun's body; not drawn here.

## Branches and combinations

- Feeds every arrangement: freedom-01 (where a soft axis is harmless), freedom-01b (pivot near the dot), freedom-05 (which errors need feed-forward).
- Transferable: the specification for the observer (finely in r and z, coarsely along the tangent).

## Unresolved problems, and questions that need Derek's observation

- The real tolerance at the dot (radial, vertical): how far off can the dot be before the weld visibly changes?
- The wire approach tolerance.
- Whether the red dot sits on the melt position at working standoff (manual: red-light alignment adjustment).

## Assumptions

- Seam radius 61.85 mm, rim 6.35 mm above the joint: **[repo]** `pressure-vessel.md`, `weld-rotation-rig.md`.
- s²/2r, s/r, ℓ × angle: **[derived]**.
- Pivot distances 16 to 279 mm: kit proxy geometry, **not measured**.
- Tolerance 0.3 mm and wire tolerance 5°: **illustrative**.

## Sourcing pointers

None needed.

## Scene

`freedom-04-free-tangent`.
