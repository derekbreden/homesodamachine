# use-16-yoke-escape: the pivot of a yoke or dock, and its stop

Scene: `scenes/use-16-yoke-escape/index.html`. Origin: combination of `travel-16-radial-plane` (yoke, trunnions) and `travel-04-return-seat` (a seat as the return), read with `travel-14b-crown-cartridge` (trunnion pins in V-notches with a pitch stop). Maturity: developed (a section, not the 3D crown). Numbers: `explorers/use/calc/w2_yoke.mjs`.

## Picture it

A radial section at the weld station: the tube wall and plate, the kit's proxy gun in attitude B with its barrel in the radial plane over the bore, and a trunnion 185 mm behind the nozzle. Turn the pivot and the nozzle rises and swings out over the wall; a stop under the barrel at the working angle takes it back.

## The proposal

The pivot of the crown's yoke, or of travel-14b's dock, has three possible jobs: set the beam angle by a stop instead of a clamp, be the dock's pitch axis, and, if a bead must end with the head leaving a wire, be the escape (a crown on the tube cannot be lifted by the room). 10 degrees puts the tip 26 mm above the rim and 37 mm from the puddle point (from 16), which is 21 mm of standoff; 5 degrees gives 7 mm. The stop is travel-04's seat and it has a 200 mm lever: 0.02 degrees is 0.07 mm at the dot, 0.05 is 0.18, 0.1 is 0.35; a stop 120 mm from the trunnion with 20 micron contacts is 0.034 mm.

## What carries the loads, what establishes position, what is free or restrained

- **Carries:** the trunnions (yoke on the ring, ring on the rim); at the working angle a stop with a preload takes the pivot torque.
- **Establishes position:** the crown (rim, outside) and the stop.
- **Free / restrained / driven:** the gun is free about the trunnion axis between the stop and the end of travel; the pivot is the one driven axis.

## What software could command, observe, and what stays manual

- **Command:** seat on the stop, escape angle, return (a small geared stepper, or spring-return and latch). **Observe:** a stop switch and an end switch. Blind: the dot, the ring, the cable.
- **Manual:** setting the working angle at the stop; trigger and firing.

## What was tried to break it

1. **Is there an escape at all?** The shared context says the head leaves with the trigger held; guide 46 says release the trigger, then the pedal; travel-16 and travel-04 note that with no wire at the gun the reason is gone. *Change:* the pivot is also the dock's axis and the angle setter, so it is useful either way. *Leaves:* how far the head must leave.
2. **The stop is an amplifier.** *Change:* a stop far from the trunnion, hardened contacts, preload. *Leaves:* pivot play and printed creep; the preload against cable pull.
3. **A pivot at the housing centre may not be possible on the real gun.** *Leaves:* the real housing.
4. **The beam angle changes with the pivot.** It is only the escape and returns to the stop. *Leaves:* nothing measures it.

## Branches and combinations

- With `use-02-swing-head` (a plunge along the barrel is the same escape by a different axis), `travel-14b-crown-cartridge` (the dock), `use-14-handover-shift` (the seat as the one handover that wipes out the hand).

## Unresolved problems and questions for Derek

- How far does the head go before the wire is free at the end of a bead, along which direction, and does it lift at all?

## Assumptions

- Kit proxy gun and attitude B (roll 0, hole dial 35, vertical -90), 16 mm nozzle clearance, trunnion 185 mm behind the tip, housing back end 253 mm: illustrative. Tube ID 123.70 mm, wall 1.65 mm, plate face 6.35 mm below the rim [repo].

## Sourcing pointers

`sourcing/use.md`: AS5600 encoder module (angle of a printed arc or pivot, 0.088 degrees per count: coarse for a stop).

Scene id: `use-16-yoke-escape`.
