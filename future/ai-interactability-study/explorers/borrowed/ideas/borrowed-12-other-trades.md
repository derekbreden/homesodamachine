# borrowed-12-other-trades: take the axis, not the product

Origin: swarm. Maturity: sketch (a list of donors with what to take from each; nothing sourced or drawn).

## Picture it

A shelf of mass-produced motion products from other trades, each doing one thing an arrangement needs: a stage-light moving head's pan/tilt yoke; a car's power-window regulator; a windshield wiper motor and linkage; a standing-desk lift column; a car's power-mirror actuator; a welding-trade tilt-and-rotate positioner; a laser-engraver roller or chuck rotary; a garage-door opener rail.

## The proposal

Each item is a high-volume, low-price, easy-to-get motion or holding module whose interface is usually a plain motor and often a position feedback. What to take, and what breaks:

| Donor | What it does | Where it could fit | What breaks (unchecked) |
|---|---|---|---|
| Moving-head stage light yoke (DMX-512, 16-bit pan/tilt, homing) | two axes with a heavy head at speed | pan and tilt of a gun about a point | the axes intersect inside the head, not at the dot; the fork spans the payload; the borrowed-04 map applies |
| Car power-window regulator | a 12 V motor lifting several kilograms along a cable rail, often with a Hall sensor for pinch detection | the Z lift of a frame or a trim stage | stroke and stiffness; the Hall counts are not an accuracy figure |
| Wiper motor and linkage | a cheap high-torque geared motor sweeping an arc | one rotation axis | backlash; no position feedback unless added |
| Standing-desk column | a stiff motorised height column with presets | setup height for the tube-length variation | resolution of a millimetre or worse |
| Welding positioner (tilt and rotate) | tilts and turns a heavy workpiece | tilting the tube instead of the gun | the joint moves up and down by r sin(tilt) around the circle: 5.4 mm at 5 degrees on r = 61.85 mm [derived] |
| Roller or chuck rotary (laser engraver accessory) | turns a cylinder | an alternative to the existing rotator | the rotator already exists |

## What carries loads, establishes position, is free, restrained, driven

Per donor; not developed.

## Software: command, observe, manual

A moving-head yoke is commanded over DMX-512 (a serial protocol microcontrollers speak); a window regulator, wiper motor and desk column are plain motors with, at most, a Hall or limit signal. None was studied.

## What was tried to break it

Only the tilted-tube arithmetic above was computed: tilting the tube about a horizontal axis by an angle t moves the joint circle up and down by r sin t, so a fixed gun would have to follow.

## Unresolved problems and questions that need Derek

- None specific; each donor needs a price and a stroke check before it means anything.

## Assumptions

- No prices or lead times were observed for any of these; the table is from general knowledge and is unchecked.

## Sourcing pointers

None.

## Scene

None (sketch).

## Wave 2

Two more donors, both on Prime, both about holding a load where it is put and letting it go on command:

| Donor | What it does | Where it could fit | What breaks (unchecked) |
|---|---|---|---|
| Locking gas spring (Bansbach B-locking, 28 in, 135 N, $71.57, "rigidly lock in both directions") | a balanced lift that locks rigid at any stroke and releases by a pin | a Z axis that balances the gun, locks under load and releases on a solenoid: freedom-06's lock on the one axis where the load acts, and freedom-10's retract (unlock and the spring's excess force lifts) | stiffness of the lock, release force, oil creep, guidance (it needs a rail); the force ratings start well above the gun's weight |
| Office chair gas lift (class 4 cylinder, $22.99, 2,200 ratings, "800+ bought") | a pneumatic column holding any height under compression and releasing by a valve pin | the same, in high volume and at $23 | locks in compression only; lateral stiffness of a thin tube; travel 100 to 150 mm |

Also: camera-stabiliser sled (FLYCAM HD-3000, $178: a 3-axis ball-bearing gimbal, balance knobs, weights) is a donor for freedom-08 (`borrowed-15-sled-keel`); a video fluid head (V504 $56.99, SIRUI VA-5 $99: a rotary viscous damper with stepped drag, 5 kg) is the damper; a telescope mount (AZ-GTi, $525) is two encoded, motorised rotations with a public protocol; a CNC router or printer (PROVerXL 4030 $659; Ender-3 V3 SE $219) is a gantry with G-code, homing and probing.
