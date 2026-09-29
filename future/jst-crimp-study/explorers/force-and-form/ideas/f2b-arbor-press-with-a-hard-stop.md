# f2b — Branch of f2: an arbor press as the frame, with a hard stop instead of a crank

Explorer: force-and-form. Parent: [`f2-crank-press-for-an-applicator.md`](f2-crank-press-for-an-applicator.md)
(its sketch shows the applicator and carriage; here a bought press replaces the
crank frame).
Numbers: [`../calc/drives.out.txt`](../calc/drives.out.txt) §D,
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt) §3.
**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.

## Picture it

The same applicator and ribbon carriage as f2, in a bought **arbor press**
instead of a built C-frame and crank.

- **Mounting.** The applicator bolts to the arbor press's base. Its shank
  collar is held by a printed-and-steel adapter on the end of the square rack
  ram.
- **Stop.** A steel stop collar clamped on the ram meets the press body at
  exactly the applicator's shut height (135.78 mm for the OTP-standard
  mini-applicator).
- **Drive.** One of three:
  - Derek pulls the handle: a manual applicator press with automated wire
    presentation, usable the day it is assembled;
  - a 12 V linear actuator pulls the handle through a clevis (with a ~250 mm
    handle and the press's ~20:1, a 100 mm actuator stroke moves the ram ~5 mm
    [calc: drives §D, pinion radius assumed]);
  - a worm gearmotor turns the pinion shaft directly.
- **What sets crimp height.** The rack drives through its stroke until the
  collar lands on the stop. The stop sets the shut height, the applicator's
  dials set crimp height, and the extra drive force goes into the stop.
- **What locates what.** Fixed is the applicator's anvil, as in f2; the
  applicator's feed places the contact and the carriage the conductor.
- **How it knows.** A load cell under the applicator's anvil zone reads the
  crimp; the stop force bypasses it. The camera and the grounded-applicator
  identity check are f2's.
- **The person** does what f2 hands back, and pulls the lever in the manual
  form.

Everything f2 carries applies unchanged: the fork entering from the tips or
between planes, the conductor dial set from a copper-corrected reference crimp
at the applicator's own crimp width, the insulation wedge set into this wire's
window ([`f6`](f6-two-blades-two-drives.md)).

## What changes from f2

- **No crank, so no geometric bottom.** A rack follows the handle one to one,
  so the bottom comes from the **hard stop**.
- **The outer frame may be springy.** With the stop in a short steel stack, a
  springy cast-iron body costs only drive travel, ~0.03 mm at 3 kN
  [calc: force_loop §3].
- **Cast iron and a guided ram are bought, not built.**

## Which press opens far enough

A mini-applicator needs its 135.78 mm shut height plus a 30–40 mm stroke above
it: 166–176 mm of opening.

| Press | Opening | Fits? | Evidence |
|---|---|---|---|
| Harbor Freight 1 t, #59766 | 139.7 mm (5-1/2 in) | no | $79.99, 20:1, 2,000 lb [source: harborfreight.com, 2026-09-28] |
| VEVOR AP-1, 1 t | 150 mm | no | [Prime: $61.90, 281 ratings, 300+ bought in past month; throat 81 mm, ram 10 mm] |
| VEVOR AP-3, 3 t | 310 mm | yes | [Prime: $255.90, 28 ratings (thin); throat 130 mm, ram bore 12 mm, plate 166 mm, 86 lb] |
| VEVOR PR-3, 3 t ratchet | 310 mm | yes | [Prime: $262.14, 44 ratings, 50+ bought in past month; throat 130 mm, 99 lb] |

The 1 t presses stay useful for f7's cartridges and f5b's short rows, which
need no applicator height.

## What was tried against it

1. **The drive can crush the stop.** A 1,500 N actuator at 20:1 can put ~30 kN
   into the stop [calc: drives §D]. The Prime-confirmed PA-01-POT (~750 N, with
   a potentiometer, $155.39, thin) could still put ~15 kN there. Limit the
   motor's current, stop on the load cell's signal, or put a spring link in the
   clevis so the stop sees only a few kN more than the crimp.
2. **Direct worm on the pinion.** About 3 kN at an assumed 12.5 mm pinion
   radius needs ~38 N·m, above an NMRV030's 20 N·m. A belt ahead of the worm, a
   larger worm, or the actuator on the handle.
3. **The stop collar has to be set to about ±0.01 mm** against the
   applicator's shut height, because crimp height then depends on it as well as
   on the dial. A fine-thread collar with a lock, set once against a crimp
   micrometer reading.

## Major unresolved problems

- **The 3 t presses' pinion radius, ram guide play and gib wear** are
  unmeasured, and both listings are thin.
- **Setting the stop collar** to ±0.01 mm.
- **Everything f2 leaves open about the applicator.**

## Which conclusions rest on assumptions

- **Pinion radius** is inferred from "20:1 leverage" and an assumed 250 mm
  handle.
- **Cast-iron body stiffness** is estimated from an assumed section
  [calc: force_loop §1].
