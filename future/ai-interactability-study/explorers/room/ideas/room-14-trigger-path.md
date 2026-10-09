# room-14: trigger path and lockout, a hand fires and software can only stop

**Origin:** combination of `use-05-gates` and `room-05-drawer-cell`, from the wave 2 exchange (section 5). **Scene:** `scenes/room-14-trigger-path`. **Depth:** developed. Safety-sensitive: read the unresolved list.

## Picture it

Beside the bench, a small pendant with a brake-lever squeeze. A cable in a sheath runs over the bench to a small printed lever on the gun's shell. When the hand squeezes, the lever turns about a lug and its pad presses the gun's trigger. A spring-loaded pin on the shell can block the lever after half its stroke; a coil holds the pin out of the way only while five things are true: door closed, tube dock seated, gun seat closed, software permit, pedal held. Let go, cut the wire, crash the program, drop the door: the pin blocks.

## The proposal

When something other than the hand carries the gun (a seat, a cell, cords, a gantry, a table), "a hand fires, always" needs a path from a hand to the trigger. This idea makes it mechanical, so that (a) the trigger's reaction stays inside the shell, and (b) software's veto can be a fail-safe pin that needs no protocol, port or modification of the laser. The laser's own chain (key, e-stop, the work clip and the conduction between clip and gun [manual pp.19, 32]) stays in series and is not modelled.

## What carries the loads, what establishes position, what is free or restrained

- The lever pivots on a shell lug (amber). The wire and the sheath both end at a ferrule on the shell: the wire pulls the lever's tail, the sheath pushes the ferrule, and the two cancel except for the misalignment residual (wire tension × sine of the angle between the last wire segment and the sheath).
- The pin and coil are on the shell (purple: software could command the coil). The pendant lever is the hand (green).
- It locates nothing. The seat, cords or arm of the arrangement do that.

## What software could command, observe, and what stays manual

- **Command:** the permit relay only (energise to permit). It withholds the lever; it never moves it.
- **Observe:** a pendant lever switch, a lever-travel switch at 8 mm, a pin-position switch, door, dock and seat contacts, rotator degrees and pedal. Not observable: whether the laser thinks it conducts (its alarm screen: unresolved), whether emission occurred.
- **Manual:** the squeeze; goggles, key, e-stop, clip; clearing a hold; snipping a stuck wire.

## What was tried to break it

1. **A finger on the trigger of a supported gun is an external load.** Trigger force [unknown]; the scene uses 6 N. Against 8 N/mm (use-02's T-slot loop) that is 0.7 mm at the dot; 145 N/mm (box column) 0.04 mm; against a 0.1 N/mm friction arm 60 mm. *Change:* cable and lever; residual 0.26 N at 5° misalignment and a 2:1 lever (illustrative). *Leaves:* the real trigger.
2. **The cable is not free of force.** Wire and sheath cancel only where the last wire is in line with the sheath; the sheath's weight and stiffness add a constant like the umbilical's. *Leaves:* measure on the real shell.
3. **Software's veto.** use-05 needs a place for one and the DB25 is documented only as "for PLC integration by customers" [manual p.16]. A pin needs no protocol. Energise-to-permit means a dead coil, a crashed program or a cut wire blocks the lever. It is a layer in front of the laser's chain, not the safety function. *Leaves:* a pin that jams retracted permits.
4. **A stuck lever fires.** A cable that jams pulled leaves the trigger pressed with no hand. Return springs at both ends, a low-friction liner, a pendant switch that drops the permit when the pendant is released while the lever switch still reads pressed. *Leaves:* none of these is a guarantee.
5. **The coil is on for the whole weld.** The open-frame push-pull solenoid found (sourcing 18) says its rod pushes out when powered and that power-on time should stay under 30 s; a cabinet-lock solenoid at 350 mA is more plausible. *Leaves:* duty rating, direction, heating: unchecked.
6. **The trigger is not the kit's proxy.** The manual lists a process switch and a light switch (p.17) and does not say whether firing is one press or two.
7. **The hand no longer feels the gun.** *Leaves:* whether Derek wants that.

## Branches and combinations

- Answers use-05's "where can a veto attach" without the DB25; makes policy C (dry laps alone) a state of the pin.
- With `room-05`/`room-12` the cell's own contacts (door, drawer or carriage, seat continuity) are the permit chain.
- With `room-15` the pendant is the hand's second job beside the knob; with `use-08` the lever switch times the trigger.

## Unresolved problems, and questions that need Derek's observation

- Trigger travel, force and switch count: a spring scale on the real trigger with the gun clamped and the laser disabled; or a mule gun (trials-06).
- Does the trigger do anything with the key out (red dot on? a lamp?), and what part of the gun closes the laser's conduction circuit (nozzle, wire, or both) [manual pp.19, 32]?
- Whether a remote trigger is acceptable for this laser at all: Derek's and the manufacturer's call. Nothing here removes goggles, guarding, extraction or the laser's own interlocks.

## Assumptions

- **[manual]** emission needs a complete circuit between the work clip and the gun (p.19); loss of conduction stops the beam (p.32); DB25 and RS232 documented without pin list or protocol (p.16); process and light switch (p.17).
- **[illustrative]** trigger force 6 N; stroke 10 mm, trigger reached at 8 mm, pin blocks at 4 mm; lever ratio 2:1; kit trigger anchor.

## Sourcing pointers

`sourcing/room.md` 17 (bicycle brake lever and cable set), 18 (two solenoid candidates and what to check).

## Scene

`scenes/room-14-trigger-path`

## Wave 3

- **The permit chain gains a contact.** In a closed cabinet (room-18) argon fills the box in about a minute if nothing takes it out, so "extraction fan airflow proven" joins door, dock, seat, software and pedal as a permit, and the fan is the one part of the chain that is not a position. Like the others it can only withhold. Drawn in `room-18-cabinet-station` (the interlock badge opens with the fan off); not drawn in this scene.
