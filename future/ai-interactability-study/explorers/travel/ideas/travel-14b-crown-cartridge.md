# travel-14b-crown-cartridge: the crown stays on its tube, the gun docks

No scene (sketch). Origin: combination of `datum-03-rim-crown`, `use-03-preset-cartridge`, `trials-02-dock-reset` and my `travel-04-return-seat`, named in `exchange/travel--on--datum-w2.md` section 1. Depth: sketch.

## Picture it

Two tubes on a bench, each wearing its own crown: a lower ring locked on the outside, an upper ring, and a yoke of two legs with an open V-notch at the top of each. A depth gauge on the plinth sets a shim under the yoke for this tube. The rotator turns one tube; the other waits. The gun, one fibre trailing, is lifted out of the first yoke by its two trunnion pins and lowered into the second, where the pins drop into the notches and a stop screw holds its pitch. If the head has to leave the puddle at the end of the bead (the coordinator's shared context says so; guide 46 says only to release the trigger, then the pedal: unconfirmed), the gun lifts straight up out of the notches, and that lift-off is the dock's own motion.

## The proposal

datum-03's crown has to come off the tube for every swap and be seated again, and every seating is a fresh chance for the pads, the rim contacts and the ring float (`travel-14-exact-crown`) to differ. Split it the way `use-03` splits the tube and its nest: **what varies per tube stays with the tube** (ring seat, locked pads, the shim that carries this tube's seat depth from the presetter's depth gauge, a printed number), and **what is constant across tubes stays with the gun** (its beam angle, set by the yoke's pitch stop, once). The gun moves between cartridges on a kinematic dock: two trunnion pins in two V-notches (four constraints), an axial stop (fifth), a pitch stop (sixth). In the radial-plane attitudes of `travel-16-radial-plane` the trunnion axis passes near the centre of mass, so weight seats the pins and a light spring or a magnet does the rest.

This puts the vertical trim where it can be measured well (a depth gauge at a bench, not a plunger in the pocket), removes the plunger and its heat problem, makes the seat's repeatability a one-time acceptance test per crown, and makes the tube swap a hand carrying two objects the person already carries.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the rim (three pads) carries ring, yoke, and (docked) the gun; the tube and lower ring stand in the nest as today.
- **Establishes position:** the outside and rim seat (per tube, set at the presetter), the dock (per docking).
- **Free / restrained / driven:** the gun is restrained by the dock when down, free to lift when up; nothing is driven except the rotator.

## What software could command, observe, and what stays manual

- **Command:** the rotator. **Observe:** a contact at each pin (docked or not: three lines, as `travel-04`), the crown's printed number by camera, the depth gauge and roundness indicator readings at the presetter (`use-03`). **Manual:** docking, locking pads, shimming.

## What was tried to break it

1. **The dock is an amplifier.** *Conflict:* a speck raising one pin by d tilts the gun about the other by d over the pin span; the kit's proxy housing is 34 mm wide, so pins on its sides span about 40 mm and 20 micron is 0.5 mrad, about 0.1 mm at the dot 200 mm from the trunnion axis in attitude B; outriggers to a 100 mm span give about 0.04 mm, plus the 20 micron of translation. *Assumption:* printed V-notches and steel pins repeat to about 20 micron. *Leaves:* unmeasured (`sourcing/travel.md` note on kinematic couplings: micron-class only for ground parts).
2. **The fibre rides the hand between cartridges.** *Change:* none: the fibre has 5 m and a person moves the gun 300 mm. *Leaves:* wrapping and re-laying the wire conduit and gas hose.
3. **Each crown needs its own counterweight in attitude A.** *Change:* attitudes B and B2 (`travel-16-radial-plane`) need none.
4. **Time.** *Leaves:* whether a crown per tube pays: `use-03`'s own finding is that presetting moves time off the station, not off the hand.

**Wave 3 entries, from use's exchange (`exchange/use--on--travel-w2.md` section 3), answered in `exchange/travel--reply-to-use-w3.md`.**

5. **The crown stays on its tube for one closure, not two (use).** *Conflict:* the repo's second closure inverts the tube (first plate down, ports through the service bore); the crown sits on the rim being closed, so for the second closure it is on the wrong end. *Assumption behind it:* a crown per tube. *What the change alters:* a crown per closure: a second printed crown, and the presetter step (seat, lock, depth gauge, shim) per closure, not per tube; the printed count doubles and the depth gauge is per closure (the plate depth differs). *What it leaves uncertain:* printed count and time; a crown seats on the end being closed, so it cannot slide to the other rim.
6. **The dock is a hand action, so there is no state for software to command (use).** *Conflict:* docking, the pad lock and the lift-out are all by hand, so an AI cannot run repeat-dock experiments. *Assumption behind it:* the gun moves between cartridges as an object a person carries. *What the change alters:* an arm branch, `travel-22-arm-docks-then-floats` (a combination of this idea and `use-14-handover-shift`; both originals stay): an arm docks the gun (capture a few millimetres), floats it (gravity compensation), reads the joint angles (they are the seat's pose), re-teaches the dock and holds. The hand-run dock stays the base option. *What it leaves uncertain:* whether a crown seat can take an arm's residual force (the scene computes it; every number is illustrative).
7. **The pivot at its stop has a 200 mm lever (use, `use-16-yoke-escape`).** *Conflict:* in attitude B the trunnion axis is 185 mm from the nozzle and 202 mm from the dot: 0.02 degree at the stop is 0.07 mm at the dot, 0.05 degree 0.18 mm, 0.1 degree 0.35 mm; my own figure (20 micrometres on a 40 mm pin span, about 0.1 mm at the dot) has the same shape. *Assumption behind it:* the seat's error is its contacts' repeatability. *What the change alters:* `travel-22` adds the seat's rocking compliance, the force at the flange times its height times the dot's lever over 1.5 contact stiffnesses times the ball circle squared: 0.16 mm per newton against 0.017 mm per newton of translation at 40 N/mm per ball, a 50 mm ring, a flange 120 mm up and a dot 200 mm out; a seat at the nozzle end (lever 20 mm, ring 80 mm, flange 60 mm up) leaves 3 micrometres per newton, fifty times less; outriggers help the same way. `calc/17-float-release.mjs`. *What it leaves uncertain:* the real contact stiffness of a printed groove and a steel ball.
8. **The last look must come after the dock (use).** *Conflict:* the pads lock at the presetter (cold, off the station, shoe off) and the dock closes at the station; the depth gauge's shim cannot see the dock. *Assumption behind it:* the presetter's result is the weld's. *What the change alters:* adopted: the one-time radial trim is taken after the dock, once per tube, not once per crown; in the arm branch the float-read-re-teach sequence is that look for the arm's own placement. *What it leaves uncertain:* nothing in this arrangement sees the dot.

## Unresolved problems and questions for Derek

- How many tubes in a batch; how long indicating takes today; whether a second crown, printed, is welcome (printing is the fun part).
- **Wave 3, questions for Derek:** would you let a machine put the gun on a dock (`travel-22`)? How many crowns can you print per batch (one per closure)? Weigh the gun with the shell on.

## Assumptions

- Kit proxy geometry and dial poses **illustrative**; seat repeatability **illustrative**.

## Wave 3

Questions from use answered: **who docks the gun?** A hand today; an arm in the branch above. **Second closure?** A crown per closure, not moved. **Depth gauge?** Per closure.

## Scene id

None for the crown cartridge itself; `travel-22-arm-docks-then-floats` draws the arm-docks branch.
