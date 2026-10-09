# room-09: move-only shelf (software moves one axis, watches nothing)

**Origin:** swarm (room framing; a partial arrangement where software moves and observes nothing). **Scene:** the shelf slider in `scenes/room-01-table-opening`. **Depth:** sketch.

## Picture it

Everything about today's day stays: the operator holds the gun and rests it on the table top. The one change is that the rotator hangs under a hole on a shelf that a screw or a linear actuator raises and lowers to a stored height. The height is a recipe number kept beside the speed.

## The proposal

Set the rim's height above the table from a number, not from the operator's eye. Rim flush is the reference, and the actuator makes the per-tube correction (plate seat depth, unknown magnitude) a one-line command. It is the smallest arrangement that already changes a day: it removes one variable (height) that today the operator judges by eye each time.

## What carries, what establishes position, what is free

Carries: the table and its hung box. Position: the table plane for the gun's rest; the actuator for the tube. Free: the gun in the operator's hand. Driven: the shelf only. Escape at the end of a bead: the shelf can drop the tube instead of lifting the head, if fast enough.

## Software

- **Command:** shelf height, rotator speed and direction (existing console).
- **Observe:** nothing new; step counts of the shelf.
- **Manual:** everything else, as today.

## What was tried to break it

1. **Height by open loop.** *Assumption:* a stored number carries over from tube to tube. *Finding:* only if plate seat depth is repeatable; it is **[unknown]** and is the first thing worth measuring: a caliper from rim to plate face over a dozen tubes. *Leaves:* if it varies by more than a millimetre or two, a stored number is the wrong reference and a per-tube touch-off (the dot on the seam, judged by eye) stays.
2. **A 12 V linear actuator has no position feedback** on the page read (sourcing 11) and about 1 mm-class repeatability at best (unchecked). *Change:* a lead screw and stepper (the printer ecosystem, sourcing 10 and 15) for fine Z.
3. **Backlash under load** on a hung box: not measured.

4. **"Height by open loop needs the depth to repeat; a touch-off stays otherwise" (eyes, wave 2 exchange: `eyes-16-measure-the-tube-first`).** *Variant:* the shelf's stored number, with plate seat depth unknown. *Assumption (mine):* the seat depth is found either by assuming it or by the gun. *Finding:* it can be read from a picture before the gun is near the tube, laser off: a camera across the bore, slightly above the rim, sees the far wall from the rim edge down to the plate-wall corner, and the pixel gap times a scale is 6.35 mm plus the seat depth. eyes: about 0.03 mm at 3840 px across with 0.5 px edges (0.06 with a 20-degree lens, 0.08 at 1280 px); the rule is to measure a difference between two features in one frame, not the position of one, because a PTZ camera's pointing error (0.1 degree is 0.86 mm at the far wall) cancels in the difference; the scale is the tube's own inner diameter. In room-01's scene the side camera already sees the corner from about 14 mm above the rim (checked in wave 3: hidden at 8 and 12 mm, seen from 14). *Change:* the shelf's stored number becomes a per-tube number written at loading (with the presetter of use-03 or the side camera of room-01, raised to 30 mm); room-07 gains a row for it. *Answer to eyes's question* (would a number written at loading be enough, or does the shelf need the depth again after the tack?): read it again after the tack. The loading number predicts; the post-tack frame decides, because the tack can move the plate by a fraction of the slip clearance (0.127 mm wide) and the plate is not otherwise held; a second frame costs seconds and no motion. *Leaves:* whether the plate-wall corner is a clean edge on stainless (glare, the slip gap, a burr or a tack), the plate's lateral offset and tilt (not read from one side: two looks 90 degrees apart, or one from above at the two ports), and PTZ repeatability, which no listing states.

## Branches and combinations

The first step of `room-01`; combines with `room-08` (observe) to make an assistant.

## Unresolved, questions for Derek

- **Needs Derek's eyes:** a phone photograph across the bore, 10 to 15 degrees above the rim, on a real tube: is the plate-wall corner a clean edge? And plate seat depth over a dozen tubes, rim to plate face.

Plate seat depth over a dozen tubes; how much Z adjustment he makes by hand today.

## Assumptions

Shelf ±12 mm: **[illustrative]**. Repeatability: **[unknown]**.

## Sourcing pointers

`sourcing/room.md` entries 11 (actuator), 10 (rail), 15 (Klipper).

## Scene

`scenes/room-01-table-opening` (use the shelf slider alone).

## Wave 2

- In `room-15-one-knob-table` the shelf has a second job: the escape motion. A gun standing on a table sled cannot lift along its barrel, so the shelf drops the rotator (26 mm at 60 mm/s is 0.43 s, illustrative; how fast it must leave for the wire to break clean is unmeasured). `use-03`'s cartridge could carry its own rim reading as the number the shelf takes, in place of a printed ring.
