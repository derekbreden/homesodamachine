# use-17-driven-presetter: what binds, and what the last centring must be

Scene: `scenes/use-17-driven-presetter/index.html`. Origin: combination of `travel-06-nest-driver` and `use-03-preset-cartridge`. Maturity: developed (a budget, not a mechanism). Numbers: `explorers/use/calc/w2_presetter.mjs`.

## Picture it

Four rows, one per way of centring the tube before the weld: by hand on the station (today), by advisor and hand on a presetter (use-03), by driver and probe on the station (travel-06), and the driver on a presetter. For each, minutes per tube for the person, the presetter and the station, which of the three binds a steady cycle, and the radial error left at the weld from three terms: the centring residual, the register error if the last centring was off the station, and the shoe shift if it was done with the ground shoe disengaged.

## The proposal

Presetting frees the station and not the hand; a driver frees the hand and not the station; only one of them is scarce at a time (at the defaults the station binds in all four rows; move the plate seating to the presetter and the person binds in two). The written sequence engages the copper shoe after indicating, so the **last centring and any verify pass belong on the station with the shoe on**; travel-06's driver should run after the shoe is engaged.

## What carries the loads, what establishes position, what is free or restrained

Nothing is drawn. The rows say where the centring happens: the station's rotator and nest, or a presetter's; a cartridge with a three-ball register moves between them.

## What software could command, observe, and what stays manual

- **Command:** jog to an angle and hold, driver engage and turn (a firmware addition: today the pedal is the whole of the control, the console is serviced only while stopped, the driver lets the motor go 10 s after release [repo]).
- **Observe:** probe reading against table angle; the verify pass. **Manual:** loading, screws to contact, seating the plate.

## What was tried to break it

1. **The shoe.** 1 N on contacts of 5 to 50 N/mm moves the tube 0.2 to 0.02 mm (placeholders): as large as the routine's result. *Change:* shoe-on last pass. *Leaves:* the shoe's force and whether it moves the tube.
2. **The interface.** *Leaves:* whether the ESP32 firmware can take go-to-angle-and-hold.
3. **The probe** is still missing (no Prime-listed indicator with a documented data output found).
4. **Register.** *Change:* a station verify pass. *Leaves:* printed register repeatability.

## Branches and combinations

- `travel-06-nest-driver`, `use-03-preset-cartridge`, `room-09-move-only-shelf` (a commanded height from the cartridge record), `trials-01-puck-swap`. The hall index pulse and the AS5600 module of `sourcing/use.md` are the cheap angle references.

## Unresolved problems and questions for Derek

- Read the indicator at the weld circle before and after you engage the shoe.
- The rotator's fastest safe jog; whether the console takes a command while the pedal is held.
- How long indicating takes today and how often it takes more than one attempt.

## Assumptions

- Durations (min): load 1.0, contact 1.5, hand indicating 6.0, advisor 2 rounds of 1.0, driver pass 44 s (a lap at 15 mm/s is 25.9 s [derived] plus three 6 s moves), passes 3, verify 1.0, plate 3.0, rest of the closure 9.0 with 5.0 of a person. Residuals 0.06 / 0.05 / 0.024 mm, register 0.03, shoe 0.05: illustrative.

## Sourcing pointers

`sourcing/use.md`: hall-effect sensor module 5-pack ($5.99, 135 ratings, 100+ bought in past month), AS5600 encoder 3-pack ($7.99).

Scene id: `use-17-driven-presetter`.
