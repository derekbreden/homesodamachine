# room-04: orbit the gun, park the tube

**Origin:** swarm (room framing; a different body moves). **Scene:** `scenes/room-04-orbit-the-gun`. **Depth:** rough, with one design error found and repaired while drawing.

## Picture it

The tube stands still on the rotator, which is now just a stand. A frame over the bench carries a vertical spindle on the tube's axis; three pads on the tube's outside (a steady ring) pull the tube onto that axis. A boom on the spindle carries the printed shell and the gun on the same opening pose as the other scenes, and turns it 380° around the tube. A camera on the boom looks at the dot from the same place all the way round. A fibre hangs from a swivel above the axis.

## The proposal

Reverse who moves. The reason the tube turns today is that the gun's umbilical would otherwise wind around it. If the fibre could come down the axis through a rotary path, then rotation symmetry would do what the rotator does: every point on the seam sees the same approach, angle and standoff, with no per-position setup, and the work clip can be a plain clip. The boom's slides (radial, height) are the only per-tube adjustments; the tube's own variation (plate depth, wall thickness) still needs them.

## What carries, what establishes position, what is free

- **Carries:** a frame over the bench carries the spindle bearing; the boom and shell carry the gun; the tube and the rotator carry only the tube.
- **Establishes position:** the steady ring puts the tube axis on the spindle axis (0.08 mm, illustrative). Everything else is symmetry.
- **Driven:** orbit angle (a motor on the spindle: a belt drive like the rotator's own), the two boom slides, the ring open and close. **Restrained:** the gun's three rotations (boom geometry). **Free:** none.
- **Escape at the end of a bead:** lift the boom slide (Z) or retract along the boom (radial): the gun leaves straight up or out.

## Software

- **Command:** orbit angle and speed (7.4°/s is 8 mm/s at the weld radius, the rig doc's starting value [repo]); boom slides; steady ring.
- **Observe:** boom camera (a constant view: the dot at one pixel, the seam edge moving); room camera coverage (the scene counts the fraction of the orbit for which a fixed camera sees the dot: 64 % at the default position, 53 to 72 % over the four positions I tried, because the tube hides the far side; drawn-scene line of sight, not optics); orbit encoder.
- **Manual/unresolved:** the fibre's rotary path; seating the tube and closing the steady ring; routing wire conduit and gas.

## Tried to break

1. **The fibre.** *Variant:* fibre tied to a swivel on the axis above the spindle. *Assumption:* a swivel lets it turn. *Finding:* the manual forbids twisting the fibre; a gun turning 380° about an axis with the fibre arriving along that axis twists it by the angle it turns (the scene's badge). *Options:* a rotary joint that passes the fibre (not established); a wrap-unwrap around a large drum (a 700 mm drum for the 350 mm emitting radius) with a return sweep; laser and feeder riding on the boom. *Leaves:* the main open problem; ask the manufacturer (Derek).
2. **The first version drew a plug in the bore.** *Assumption:* a pilot plug centres the spindle on the bore. *Finding (from the camera inset):* the plug fills the bore's top, exactly where the nozzle and beam go, blocks every camera, and cannot pass a plate already in the tube for the second closure. *Change:* a steady ring on the OD just below the rim; it stays out of the beam path. *Leaves:* the ring references the OD while the seam is on the ID; wall-thickness variation (**[unknown]**) enters as eccentricity (`calc/drawer-rollup.mjs` uses 0.16 mm, illustrative).
3. **Eccentricity.** Without the ring, an axis offset e turns into a radial error e·cos θ once per orbit; the scene shows it in the corner inset. The rig doc already accepts 0.25 mm TIR of runout **[repo]**; the offset adds to it.
4. **A room camera cannot follow.** The dot is against the far wall for part of the orbit; the coverage readout counts the visible fraction. The boom camera never loses it.
5. **What the rotator was for.** The rotator also holds the ground shoe (the work-contact interlock) and the deadman pedal gate. With a parked tube a fixed clip suffices; the pedal now gates the boom.

## Wave 3 note (from eyes, wave 2)

The boom camera is eyes-01's gun-borne eye with a constant view, and because the tube is parked a fixed camera can watch the whole seam instead. A dry lap with a stripe painted along the fibre (eyes-11b) would show whether the 380 degrees of wrap twists it before anyone tries the laser; the twist is the open problem of this idea and the stripe costs a marker pen. Not built.

## Branches and combinations

- **Lazy-susan ring** instead of an overhead spindle: a 12-inch turntable bearing around the tube carries the gun on a bracket (sourcing 3, the highest-volume part in this file; its runout and play are unchecked).
- Combination with `room-02-ceiling-carries`: the umbilical festoon is the natural home for the wrap-unwrap.

## Unresolved, questions for Derek

- Would the manufacturer say whether a fibre rotary path exists for this head?
- Is a parked tube really easier? The rotator's runout acceptance (0.25 / 0.30 mm TIR) would move to the orbit bearing.

## Assumptions

Steady-ring centring 0.08 mm, wall eccentricity 0.16 mm, boom geometry, slide ranges: **[illustrative]**. 7.4°/s: **[derived]** from 8 mm/s at r 61.85 mm. Fibre twist rule and bend radii: **[manual]** p. 20.

## Sourcing pointers

`sourcing/room.md` entry 3 (lazy susan bearing), entry 12 (extrusion).

## Scene

`scenes/room-04-orbit-the-gun`
