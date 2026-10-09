# room-17: tipped tube, plumb gun

**Origin:** wave 3 new direction (the work in another orientation), a combination of travel-16 (the radial-plane gun with the wire off it), travel-03 (tilt the work, not the gun), room-12 (one axis is the plunge, the seat and the lift) and room-02 (the cable owned from above). **Scene:** `scenes/room-17-tipped-tube`. **Lens behind it:** `scenes/room-16-which-way-is-down`. **Depth:** taken past the first sketch: numbers, a sweep check, break and repair below.

## Picture it

The rotator sits on a plate hinged along one edge on the bench (a pair of door hinges) and rests on an adjustable stop under the other end. Level, it is today's rotator: the tube is loaded, seated, indicated and tacked exactly as now. Tipped 30 degrees toward the station, the tube leans over the gun and the corner is at the bottom of a tilted bowl. The gun stands **plumb** over the corner, its grip pointing sideways, on a vertical rail with a spring balancer taking its whole weight; the wire arrives from a guide on a post that rides on the tilted plate. The umbilical leaves the grip base 65 degrees above horizontal and goes straight up to a hook.

## The proposal

Tipping the work about the seam's tangent line changes what gravity does at the corner and leaves the gun's pose on the work alone (`room-16` draws the family: 0 is today, 90 a horizontal tube with the station at the bottom, 180 inverted). Two facts decide whether that is worth anything:

1. **With the reference gun (wire on the gun, barrel leaning 32 degrees along the seam) tipping cannot make the barrel plumb.** The best is 32.4 degrees from vertical at 32.5 degrees of tilt: the weight lever about the dot falls from 148 to 125 mm and the moment from 2.13 to 1.80 N m. A sixth. [derived, `calc/orientation-family.mjs`; gun proxy, 1.47 kg, centre of mass local (0, -23, 181), all illustrative]
2. **With the wire off the gun (travel-16's attitude B, barrel in the radial plane) the barrel is exactly plumb at 30 degrees of tilt**, the lever is 23 mm (the centre of mass's offset from the barrel axis) and the moment 0.33 N m: a sixth of the reference gun's 2.13. [derived, same script]

So the arrangement is B at 30 degrees, with the wire delivered by a separate guide on the tilted frame.

## What carries, what locates, what is free, what is restrained

- **Carries.** The hinged plate and the stop carry the rotator and the tube (4 to 6 kg, illustrative). A spring balancer above a vertical rail carries the gun's whole weight down its own barrel axis; the arm from the carriage to a lug on the housing back only locates. The cable hangs from a fixed hook.
- **Locates.** The stop sets the tilt (a switch says it is reached, an inclinometer reads it); a mistake of 0.05 degrees is 0.2 mm at the dot 232 mm above the hinge and is nulled by the dot loop each tube. The seam is found by the dot, as in room-01 and room-05. The wire guide is located on the plate by its post; its tip's place against the pool is a separate, unsolved alignment.
- **Free / restrained / driven.** Driven: gun X (across the trough) and Z (the barrel axis, which is now also gravity's), the rotator, a small height trim on the wire guide. Hand-set states: level to load, tipped to weld. Restrained: the gun's attitude by the printed shell on the arm.
- **The vertical axis is four jobs.** Plunge to seat, seating stroke, standoff, and the lift that ends the bead (trigger held, wire broken in air [repo]) are one stroke along one axis, with gravity taken by the balancer so the axis moves inertia and friction only.

## What software could command, observe, and what stays manual

- **Command:** gun X and Z; wire guide height; rotator; the fan and lamps if the tube is in room-18's cabinet. The tilt is a hand-set state with a stop switch; a linear actuator on the stop (the 12 V class of sourcing 11) is the proposed way to command it.
- **Observe:** tilt (an IMU or the stop's switch); the corner in cameras that stand where the tilted cone points (the far-side low camera loses it by about 9 degrees of tilt; the overhead one keeps it to about 65); the balancer line's load (the gun's weight, a hose or a stuck wire changes it); the corner inset in the scene is exact geometry and not a sensor. **Blind:** the wire tip against the pool, the argon pocket, the plume.
- **Manual:** loading, seating, indicating and tacking with the tube level (unchanged from today); setting the stop and the wire guide; snipping a stuck wire with the tube tipped away and the gun lifted.

## What was tried to break it

1. **"Tipping about the tangent plumbs the gun."** *Variant:* the reference gun (attitude A, roll 45, hole dial 30, vertical -15). *Assumption:* the tilt removes the barrel's lean. *Finding:* it removes the 45 degrees in the section and leaves the 32 degrees along the seam, which the wire's tangential approach imposes: at best 32.4 degrees from plumb, lever 125 mm against 148. *Change:* take the wire off the gun (B). *Leaves:* B needs a separate wire guide; whether the real gun's wire bracket can simply go unused, and how the real gun feeds the wire, are unknown.
2. **"Tipping in will run the rim through the barrel."** I expected so and built a sweep check (scene readout: smallest clearance while the tube tips in from level with the gun where it is). *Finding:* with the hinge on the station side the tube's corner rises to the nozzle from below and to the side: the smallest clearance is at the end, 8.8 mm at 30 degrees for B (6.2 for the reference gun, 5.3 at 45). So the gun can stay at its working height while the tube tips in and away. *Change:* none needed; the tilt is a free parking motion. *Leaves:* a hinge on the far edge would swing the wall through the barrel and put the base into the bench (the sign of the rotation fixes the hinge side).
3. **"The plume rises up the barrel."** *Finding:* plumb, the nozzle tip is 0 mm off the vertical line through the dot (11.2 mm at the reference pose). *Change:* none proposed; at 25 degrees with B the barrel leans 5 degrees and the nozzle is 1.4 mm off the line. *Leaves:* the real gun's gas flow, lens drawer and nozzle in a vertical plume are unmeasured; a cross-jet may be needed.
4. **"The argon pocket goes."** *Finding:* the pond the pocket can hold at the station is 6.35 mm at 0, 5.5 at 30, 4.5 at 45, none at 90 [derived: the lowest point of the rim sets the level]. *Leaves:* whether the pond mattered next to the nozzle's own 15 to 20 L/min [manual].
5. **"The printed race is gravity-seated."** *Finding:* tipped, the tube's weight across its axis is 6.9 N at 30 degrees (1.4 kg first closure [repo]); the upper race lifts on its uphill side when tan(tilt) passes the race radius (82.5 mm [repo]) over the rotating centre of mass's height above it: 118 to 151 mm gives 35 to 29 degrees (illustrative heights). At 30 degrees it is at the limit and the spool's 1 mm retaining gap [repo] would catch it. The sideways load also presses the tube against the low nest adjusters and puts a once-per-turn term into the seam signature. *Change:* magnets or springs preloading the race, a lower centre of mass, or 25 degrees with B. *Leaves:* untested.
6. **"Cameras stand where they stood."** *Finding:* the visible cone is fixed in the work's frame and only turns (43 % of the room's upper hemisphere from 0 to 90 degrees of tilt toward the station, 0 at -90 and at 180): tipped toward the station a far-side bench-height camera 12 degrees up loses the corner by about 9 degrees of tilt, one 30 degrees up by 27, the overhead one by about 65. In the scene the overhead camera has the grip in its way unless it stands off to +Y. *Leaves:* where the nozzle-height camera of eyes-13 stands.
7. **"The wire is the price."** The gun's own bracket held the wire to the beam by construction; a guide 176 mm out on a post has to be held to a few tenths of a millimetre, must follow the seam's 0.25 mm runout, and needs a height trim. Drawn as a rigid post with one trim axis; not analysed. *Leaves:* this is the largest open problem of the arrangement.

## Branches and combinations

- **The gun stays as it is (attitude A) and only the pool changes:** the same plate tipped to 45 degrees for a symmetric trough; the gun is then 34.5 degrees from plumb. A process experiment, not a mechanism.
- **Ceiling port (room-03's rod through a ball, plumb):** with gravity along the rod its bend falls from 2.4 mm to 0.6 mm at 20 x 2 mm and 0.05 mm at 38 x 3 mm (`calc/rod-under-tilt.mjs`); named, not drawn. What remains is the cable's pull.
- **Room-18's cabinet around it:** the plate and mast fit a drawer or a fixed base in the same box.
- **A bought positioner for the tilt:** VEVOR 0 to 90 degree rotary welding positioners exist on Prime (sourcing 26) but with thin volume evidence and a chuck, not the printed rotator.
- **The horizontal tube on roller stands** (`room-16` at 90 degrees) is drawn as the limit in the lens only: it loses the argon, worsens the lever and needs a new rotator.

## Unresolved problems, and questions that need Derek's observation

- **Whether the melt cares.** A coupon welded by hand on an incline (the seam level, the plate tipped 30 degrees) answers it without any machine. This is the first thing to try.
- The real gun's behaviour plumb (plume, lens drawer, gas), its wire bracket, mass, centre of mass and umbilical pull.
- The wire guide: rigidity, tolerance, following the runout.
- The rotator's tip-over on a real tilted plate; the centre of mass of the rotating parts over the race.
- How much the operator would give up: a tilting rotator is 4 to 6 kg on a hinge.

## Assumptions

Gun proxy, 1.47 kg, centre of mass, attitude dials (B: roll 0, hole 35, vertical -90): **[illustrative]**, from the kit and travel-16. Hinge at the bench, plate 330 x 270 x 8 mm, stop under the far end, hook 590 mm along the exit line: **[illustrative]**. Tube and rotator dimensions, rotating mass 1.40 kg, race pitch circle 165 mm, retaining gap 1 mm: **[repo]** (`hardware/assembly/weld-rotation-rig.md`). Fibre bend radius 350 mm emitting: **[manual]** p. 20. Argon flow 15 to 20 L/min: **[manual]** p. 19. Everything else is **[derived]** by `explorers/room/calc/orientation-family.mjs` and the scene's own geometry. Camera views are drawn geometry.

## Sourcing pointers

`sourcing/room.md` entries 22 (IMU), 23 (hinges), 11 (linear actuator for the stop), 10 (MGN12H rail), 1 (spring balancer), 26 (bought positioners).

## Scene

`scenes/room-17-tipped-tube`
