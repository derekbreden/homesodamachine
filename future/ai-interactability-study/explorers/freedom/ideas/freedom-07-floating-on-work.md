# freedom-07: floating gun leaned on the work (a preloaded contact as a temporary reference)

Scene: `scenes/freedom-07-floating-on-work`. Origin: swarm original (from the freedom framing; touches the datum framing). Depth: rough (a 2D section with illustrative numbers; four entries).

## Picture it

The gun hangs almost weightless from a balancer. Ahead of the dot, a small amber shoe with two rollers touches the tube: one roller inside the bore against the wall, one on top of the rim. A soft spring, whose force software sets, keeps them touching. The tube turns and the gun rides with it; nothing has to be stiff.

## The proposal

Let the gun *lean* on the work instead of standing in the room. While the shoe is engaged, the wall roller puts the dot at the wall's radius wherever the wall is (runout included), and the rim roller sets the height above the rim. The contact carries precision only while it exists, and only on the axes it touches: it does not know where the plate is, and it leaves the tilts, the tangent and the plate-to-rim relation open. A retract makes the tube swap trivial: lift the shoe, change the tube, lower it.

## What carries the loads, what establishes position, what is free or restrained

- **Weight**: a balancer or bungees (freedom-01, 02); the rollers carry only the preload and sideways cable pull.
- **Position**: radial from the wall roller, vertical from the rim roller: a *datum on the work*, not in the room.
- **Free**: the tangent (if the contact rolls), the tilts, and everything when retracted.
- **Restrained**: two axes, softly, by preload.
- **Driven**: the preload actuator (engage, hold, retract); optionally a vernier for the plate offset.
- **When constraints change**: engaged during the dry-run and the weld; retracted for swaps.

## What software could command, observe, and what stays manual

- **Command**: preload force, engage/retract.
- **Observe**: contact force (a load cell in the shoe), electrical continuity between a metal roller and the tube (the same idea as the laser's work-contact interlock: the manual requires a complete circuit between the clip and the gun [manual p. 19]; whether the nozzle, the wire or a shoe closes it is **[unknown]**), the dot by camera.
- **Manual or unresolved**: fitting the shoe; the floating support's placement.

## What was tried to break it

**Entry 1. A sliding contact drags a soft gun.**
- Conflict: a skid at 2 N preload with μ 0.3 pulls with 0.6 N along the tangent; a gun on a 350 mm pendulum has 0.034 N/mm sideways stiffness and drifts 18 mm. The tangent is nearly free for the dot (freedom-04) but the wire approach turns 0.93° per mm of drift.
- Assumption: the tangent stays free when something touches.
- Change: a wheel or ball-transfer unit (rolling resistance about 1 to 2% instead of 30%: 0.02 to 0.04 N). The scene's contact radio shows all three.
- Leaves uncertain: real rolling resistance on stainless with a preload of a few newtons.

**Entry 2. The rim is not the corner.**
- Conflict: the plate sits 6.35 mm below the rim by design; how much that varies tube to tube and how much the plate face tilts relative to the rim are unknown. The rim roller fixes height from the rim, so those errors reach the dot untouched.
- Assumption: a rim contact locates the corner.
- Change: measure per tube with a dry-run (freedom-05) and trim with a vernier: the shoe removes the periodic runout, the dry-run takes the offset.
- Leaves uncertain: the rim's own quality (a cut edge).

**Entry 3. Pressing bends the reference.**
- Conflict: a 1.65 mm wall gives under the roller; the scene assumes 0.01 mm per newton (a placeholder, not derived), which at 2 N is 0.02 mm.
- Change: lower preload, wider contact, a measurement.
- Leaves uncertain: the real local wall stiffness.

**Entry 4. Room for the shoe.**
- Conflict: the wall roller sits between the nozzle and the wall, next to the beam and the wire guide. The scene draws a 5.6 mm roller to scale against the wall 4.5 mm above the joint; the beam comes down at about 32° from vertical in the reference pose, so the roller has to sit ahead of the puddle along the tangent and stay clear of the wire.
- Change: a shoe ahead of the dot along the arriving side, sized for the beam and the wire.
- Leaves uncertain: whether it fits at all with the gun's real shape (scan).

**Entry 5 (wave 3, from borrowed's exchange, "smaller remarks"). How light can a follower be? Decision: answered (a note, unverified).**
- Conflict: the shoe's preload is 2 N and freedom-12's stylus triggers at 0.18 to 0.36 N. A phono cartridge tracks at about 10 to 20 mN (borrowed-07's tonearm, general knowledge, unchecked): ten to twenty times lighter.
- Assumption: the contact has to press hard enough to follow the wall and rim through runout.
- Change: the shoe, the touch stylus and the tonearm are one contact at different preloads; a light enough follower can be very light. Not verified for a steel corner and a moving tube.
- Leaves uncertain: whether a steel ball or roller at a fraction of a newton marks the 316L bore (Derek's question, below); the follower's own tracking at 8 mm/s over a 0.125 mm runout.

## Branches and combinations

- With freedom-05: contact follows the runout mechanically; the table takes the plate offset.
- With freedom-01, 02: the floating support is a balancer or a suspension.
- With freedom-04: the wheel keeps the tangent free.
- The datum framing (another explorer) owns "the work as reference"; this entry adds force and friction to it.

## Unresolved problems, and questions that need Derek's observation

- Measure the wall's local flexibility: press a 2 N point on the inside wall near the rim and watch an indicator on the outside.
- Does the rim have burrs or a chamfer that a roller would ride badly?
- Does a metal roller marking a 316L bore matter for the vessel (surface, contamination)?

## Assumptions

- Bore wall radius 61.85 mm, wall 1.65 mm, plate 6.35 mm below the rim: **[repo]**. Runout limits: **[repo]**, not measurements.
- Plate seat deviation and plate-to-rim tilt: **[unknown]**, sliders. Wall compliance 0.01 mm/N: **illustrative**. Friction 0.3 / 0.02 / 0.01, tangent stiffness 0.034 N/mm: **illustrative** (12 N on a 350 mm pendulum [derived]).

## Sourcing pointers

`sourcing/freedom.md`: 608 bearings 10-pack (roller stock), 1 inch steel balls (ball-transfer stock), load cell, balancers.

## Scene

`freedom-07-floating-on-work` (rough).

## Wave 2 (after the exchange with eyes)

- **The shoe and the touch probe are one mechanism at two preloads.** A stylus on three contacts (`freedom-12-touch-trigger`) triggers at 0.18 to 0.36 N sideways; left in contact at that force a sliding ball drags 0.054 N, which drifts a 350 mm pendulum 1.6 mm along the tangent (the seam moves 0.02 mm) against 18 mm for the 2 N skid of entry 1. The three switches watch whether the unilateral contact is still there, which the entries above lacked.
- **A contact is a constraint you can read.** eyes-04's pads have an offset a contact at a known geometry can zero (exchange with eyes, section 5); the roller and the pads still want the same 5 to 8 mm beside the nozzle.
