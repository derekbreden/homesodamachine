# room-13: load-change budget, what the weld does after the last adjustment

**Origin:** branch of `use-06-coach-loop` and `use-02-swing-head` (a lens, from the wave 2 exchange, section 2). **Scene:** `scenes/room-13-load-change-budget` (a custom stage; bars on a log axis). **Depth:** developed.

## Picture it

A page of horizontal bars, one per way of carrying the gun, on a log axis from 0.001 mm to 100 mm. A dashed amber line marks a tolerance. Each bar is how far the dot moves for a load change you type in: a friction arm bar lands at millimetres, a bungee suspension at tens of millimetres, a seat on a T-slot post at 0.12 mm, the same seat on its own box column at 0.003 mm, eight taut lines at a few thousandths of a millimetre. One row is empty until you type a mass and a deflection: that row is your own arm.

## The proposal

use-06's rule is that the last adjustment must come after the last thing that shifts. The weld shifts things after the last coach step: the wire feed starts and its conduit pushes on the head, the gas hose stiffens, a finger pulls the trigger, the umbilical settles. Nothing in a dry loop can trim that. What decides the damage is **load change divided by stiffness at the dot**. The lens shows it for the supports the study has numbers for, marks the ones it has none for, and gives Derek a way to fill a row: hang the gun from the support and read the deflection at the dot (stiffness = mass × 9.81 / deflection). The rule that follows: the coach's last round runs with every weld load present except the beam, or the support is stiff by load change over tolerance.

## What carries the loads, what establishes position, what is free or restrained

Not a mechanism. Each row is a different carrier; the number is stiffness at the dot for a load at the cable exit.

## What software could command, observe, and what stays manual

Nothing to command. Observes a deflection typed in. Manual: weighing the gun; hanging it from the support with an indicator at the dot; a spring scale at the grip base for each load (wire jog, gas on and off, trigger).

## What was tried to break it

1. **use-06's loop has no load-change term.** Its terms (camera noise, knob step, hand error, lock shift, stage shift per round, coarse aiming) all act inside the loop. *Change:* one shift after the loop. *Leaves:* the load change is unmeasured and the arm unspecified.
2. **Friction arm.** 0.09 to 0.14 N/mm (freedom-06's illustrative 7 to 11 mm/N): 1 N is 7 to 11 mm. *Leaves:* a real photo arm is not that model.
3. **Seat on a slender carrier.** 8 to 41 N/mm (T-slot down to round steel bars, `calc/seat-loop.mjs`); 172 to 312 N/mm on its own box or steel tube (room-12 layout).
4. **Taut lines.** 56 to 380 N/mm from room-06 with EA 60 kN assumed; creep, drums and guides not in it.
5. **The table plane with a drive.** In plane the stool is friction-limited (about 5 N for a 1.47 kg gun on 0.35 feet), and then the drive's stiffness; 10 N/mm is room-02's illustrative slider.
6. **The tolerance.** The 0.1 mm default is a slider; the recipe's wobble is 2 mm wide [repo] and nobody knows what the melt tolerates.

## Branches and combinations

- Feeds `room-12` (the pull slider), `room-14` (what a cable and lever remove), `room-15` (the sled and screw row is the one to measure).
- Combines with `use-04-the-lap` (a slow drift, not a step), `use-08-flight-recorder` (the record after a real weld shows what changed).

## Unresolved problems, and questions that need Derek's observation

- The load change: three spring-scale readings at the grip base with the gun in the working pose (wire jog, gas flow on and off, and a trigger).
- The gun's mass (kitchen scale) and the deflection of each candidate support under it.
- The tolerance.

## Assumptions

- **[derived]** seat rows from `calc/seat-loop.mjs` (statics, illustrative sections, rigid joints); bungee row from `calc/suspension-stiffness.mjs`; cord row from `corner-cords*.mjs` with EA 60 kN assumed.
- **[illustrative]** freedom-06's friction-arm figure; room-02's 10 N/mm drive; mass 1.5 kg default.
- **[unknown]** every load change; the real stiffness of anything bought.

## Sourcing pointers

None of its own. The indicator is owned [repo tools.md]; a spring scale and a kitchen scale are household items.

## Scene

`scenes/room-13-load-change-budget`
