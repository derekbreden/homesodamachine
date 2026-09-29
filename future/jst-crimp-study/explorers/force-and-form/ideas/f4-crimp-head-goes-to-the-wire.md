# f4 — The head goes to the wire: the ribbon never moves

Explorer: force-and-form. Sketches (schematic): [`../sketches/f4-head-to-wire.svg`](../sketches/f4-head-to-wire.svg)
(top view: board, gantry, dispenser) and
[`../sketches/f4b-head-exit.svg`](../sketches/f4b-head-exit.svg) (the head in
side section, leaving toward the box).
Numbers: [`../calc/drives.out.txt`](../calc/drives.out.txt) §B,
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt),
[`../calc/placement_budget.out.txt`](../calc/placement_budget.out.txt),
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) §4 [calc: wave2 §n],
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) [calc final §n];
change-the-question's [`on_force_and_form.out.txt`](../../change-the-question/calc/on_force_and_form.out.txt)
[change-the-question calc off §n]. **[Prime]** is a row of
[`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md), observed 2026-09-28.
Related: [`f10-lift-once-fin-from-below.md`](f10-lift-once-fin-from-below.md)
(the same steel C fixed at a station, working the flat row with no gantry and
no split into planes).

## Picture it

f1, f2 and f3 bring each conductor to a fixed press. This idea keeps the
ribbon still and moves a small crimp press to it.

- **The ribbon board.** The person lays the ribbon end once into a printed
  board on the bench. A hinged clamp holds the web. A comb holds each split
  conductor in its own slot at ~5 mm pitch, with the insulation gripped to
  within 4–5 mm of the stripped tip, and the tips standing past the comb's
  edge. Laying the ribbon into the comb *is* the splay.
  - At 1.7 mm pitch split conductors touch, so they reach 5 mm slots most
    easily from change-the-question c1's split into two planes: odd
    conductors up into the comb at 3.4 mm, spread to 5.0 mm with moves of
    1.6 mm or less for rows of three or fewer; even conductors folded back
    below [change-the-question calc off §4].
  - J4's and J7's crossings are raised routes in the comb board, laid by hand.
  - If the ribbon was stripped flat while webbed, the spread from 3.4 to
    5.0 mm pulls the outer tips back against the inner ones: 0.02–0.11 mm for
    rows of 2–3, 0.14–0.42 mm for rows of 4–5 (ribbon-as-pallet's figures;
    force-and-form's S-bend model gives 0.03–0.13 and 0.17–0.51). Rows of 4–5
    are stripped after the spread, at the comb face, where the stagger is zero
    by construction. A grooved fan block pressed down from the root, its
    grooves starting at the plane's own 3.4 mm pitch, captures every conductor
    where it lies and spreads it outward, which no straight-descending V-tooth
    comb does for rows of 4–5.
- **The crimp head.** A fist-sized steel C, standing on edge. Its spine is at
  the front, ahead of where the contact's box will be; its two jaws reach back
  toward the comb, and its mouth faces the comb. The upper jaw carries the
  crimper on f3's knee, driven by a NEMA 17 inside the head. The lower jaw
  carries the anvil on a small servo wedge that can drop it 1.5 mm. A load
  cell sits under the anvil. The crimp force starts and ends inside the C, so
  the gantry that carries the head never feels it.
- **The gantry.** A printer-class or small-CNC XYZ gantry carries the head. It
  only positions: a few newtons, about a tenth of a millimetre.
- **A crimp.**
  1. **Pick.** The head goes to a dispenser, a printed track holding a contact
     strip with its contacts pointing toward the head. Crimper up, anvil
     dropped, the head moves back over the lead contact, box first into the
     mouth, until the contact sits over the anvil and only the tab and carrier
     stand outside the mouth. The anvil rises, the crimper closes to capture
     height, and the dispenser's own servo drop-shear cuts the tab outside the
     mouth. The head now carries a captured contact with its open rear facing
     the comb.
  2. **Find the tip.** The head goes to conductor i. A small camera on the
     head, or the ELP looking down at the board, sees where that tip actually
     is and corrects X and Z, and measures its bare length. With the ribbon's
     far end in a pogo port (ribbon-as-pallet a6), the captured contact, on
     grounded steel, is also a touch probe: brushing the barrel mouth's rim
     against the tip's sides and end closes the far-end circuit, which locates
     the tip in X, Z and Y to ~0.01–0.05 mm before threading and names the
     conductor (ribbon-as-pallet K7).
  3. **Thread.** The head moves back along the conductor's own axis toward
     the comb. The captured barrel's flared rear is the funnel: aimed to
     ±0.05 mm by the camera, it takes the tip, and the conductor threads
     through the insulation barrel into the conductor barrel. The conductor
     does not move; the contact slides onto it like a sleeve. Depth is gantry
     travel from the probed tip, set so the measured insulation edge lands
     mid-window (±0.1 mm on each of brush and window [calc final §10]).
  4. **Crimp.** The knee straightens, and the curve is logged.
  5. **Leave.** The crimper opens 5 mm, the anvil drops 1.5 mm, and the head
     moves forward, toward the box, until the crimped contact has passed out
     through the mouth, then rises. The lance, which hangs 0.6–0.9 mm below the
     floor, clears because the anvil has dropped.
- **How it knows.** The tip probe (position and identity), the camera before
  threading, the force curve, and a re-touch at ~10 N with an indicator across
  the head's jaws before the anvil drops.
- **The bore at capture.** The head captures the contact at the dispenser, so
  the jacket must pass the pinched insulation wings: clear for a barrel floor
  of 1.9 mm or more, 0.03–0.17 mm of interference at 1.6–1.7 [calc: wave2 §1].
  The knee can hold anywhere, so the head closes only far enough to hold the
  barrels, chosen from the kit contact's measured floor.
- **The person** lays the ribbon into the board, loads the strip, parks and
  unparks the planes, and inserts the finished contacts or moves a housing onto
  the merged row (below).

## Why the head leaves toward the box

- **Down is closed.** The anvil is under the contact and the crimper over it.
  Moving the head down moves the opened crimper onto the crimp: with a 5 mm
  opening it closes on the contact after 3.3–3.5 mm [change-the-question calc
  off §3].
- **Sideways is closed.** Neighbours sit ±5 mm away.
- **Back along the wire is closed** to anything that surrounds the wire behind
  the insulation barrel. A rear funnel with a 2.0 mm exit cannot pass a crimped
  end of 1.95 × 2.4 mm (3.09 mm diagonal).
- **Forward is open.** The tallest thing to pass between the jaws is the box
  with its lance, 2.8–3.25 mm together; the crimper's 5 mm opening plus the
  anvil's 1.5 mm drop passes it with 3 mm or more to spare [calc: wave2 §4]. So the head's spine stands ahead of the
  box and its mouth faces the comb.
- **The anvil drops because of the lance.** The lance sits under the front of
  the conductor barrel, in an anvil relief during the crimp. Leaving forward
  with the anvil up, it would drag across the anvil's whole top. A relief slot
  running the anvil's length would leave the barrel floor unsupported at its
  centre during compaction, so the anvil drops instead.

## What drives the crimp and carries the force

- **Force loop.** C-frame, knee, crimper, crimp, anvil, wedge, C-frame, closed
  on the head.
  - A steel C of this size stretches microns per kN [calc: force_loop §1,
    the steel C-frame row scaled down].
  - The knee needs only 60–160 N [calc: drives §B], so a NEMA 17 lead screw
    inside the head is enough.
  - The anvil wedge is self-locking at a shallow angle (~5°), so the crimp
    force on the anvil does not back-drive the servo [estimate].
- **Head mass.** About 0.8–1.5 kg: steel C, knee, motor, wedge servo, load
  cell [estimate]. Inside what a printer-class gantry or a desktop CNC frame
  moves.
- **Gantry loads.** Thread friction, a few newtons, and the head's weight.
  None of the crimp force.

## References and tolerances

- **Fixed reference.** The head's anvil. Contact and die are one unit before
  the head ever meets the wire.
- **Contact to die.** Set at the dispenser by a flush pilot pin from below and
  tapered pins in the neighbours' holes (f3's arrangement), then held by the
  capture.
- **Head to conductor.** Gantry repeatability of ±0.05–0.1 mm [estimate]. The
  tip position is known to ±0.3–0.5 mm from the comb, and to about ±0.05 mm
  after the camera look [estimate]. The barrel's flared rear is 1.4–1.9 mm
  across at the conductor's level (f1's bore, [calc: wave2 §1]).
- **Free length.** With the comb gripping 4–5 mm behind the tip, the push of
  0.2–6 N sits inside Euler's ~6 N at 5 mm and ~17 N at 3 mm
  [change-the-question on f4]. Gripping closer shortens it and crowds the
  jaws' rear ends; the mouth's jaw tips end at the insulation barrel's rear,
  about 1–2 mm clear of a comb 4–5 mm back.
- **Axial depth.** Gantry travel from the probed tip plus the camera's bare
  length, about ±0.1 mm on each of brush and window, inside the ±0.2–0.3 mm
  window [calc: placement_budget; calc final §10].
- **Where precision is needed.** At the pick: the pilot pin. At threading:
  camera and the barrel's own flare. At the bottom: the knee, inside the head.
  At leaving: none.

## Printed and bought

| Part | Printed or bought | Evidence |
|---|---|---|
| C-frame, knee links, dies, anvil wedge | steel; dies by the routes in [`f7`](f7-where-the-steel-comes-from.md). An OTP knife set's blades are narrow enough for the nose | see f7 |
| NEMA 17 lead screw, load cell + HX711, wedge servo | bought | [Prime: Iverntech 42HD6039-05, $27.99]; [Prime: 500 kg button load cell, $74.99]; [Prime: SparkFun HX711, $11.50]; [Prime: DS3218MG 20 kg servo, $14.99] |
| XYZ gantry | a desktop CNC frame ("3018" class) or an Ender-class printer with the hot end removed | [Prime: SainSmart Genmitsu 3018-PROVer V2, $269.00, 1,286 ratings; travel and screw type not read]; [Prime: Creality Ender 3 V3 SE, $219.00, 2,112 ratings, 500+ bought in past month] |
| Head camera | a small close-focus USB camera, or the ELP on a fixed mount | [repo: tools.md lists the ELP]; [Prime: Plugable 250× USB microscope, $59.95, 6,580 ratings], larger than a board camera for a moving head |
| Ribbon board, comb, clamp, dispenser track | printed | — |
| Dispenser drop-shear | steel blade on a servo lever | — |

## What was tried against it, and the repairs

1. **Neighbours in the head's way.** The nose engulfs only the last 3–4 mm of
   one conductor; neighbours' tips and crimped neighbours sit ±5 mm beside it,
   leaving 8.3 mm free between neighbour wires and ~8 mm between crimped
   neighbours. Keep the nose, meaning crimper, anvil and their holders over
   the working length, under ~6 mm wide. The crimper channel with its walls is
   3.5–4.4 mm [calc: gang §1], so this fits [estimate].
2. **Where to cut the tab.** Tearing it by pulling the head away would put
   ~100 N or more through the gantry. The dispenser has its own drop-shear,
   and the tab stands outside the mouth when the head has the contact.
3. **The head cannot leave the crimp, and a rear funnel blocks the pick**
   [change-the-question on f4]. Repair: no funnel on the head, the exit toward
   the box, and the dropping anvil, as above. A split funnel (upper half on the
   crimper, lower half on a servo slide) is the alternative if the barrel's
   own flare proves too small a target.
4. **A drooping tip.** A 4–5 mm free length of 22 AWG silicone wanders little:
   gravity sag is ~0.004 mm at 10 mm [ribbon-as-pallet calc §4]; the wander
   comes from set in the copper and from the comb slot. The camera looks first;
   on a snag the head backs out and retries.
5. **Does it need a gantry at all?** The head could stay fixed while the board
   moves, but then the floppy ribbon moves. Sogang's ribbon inserter lost most
   of its trials transferring the floppy cable, not inserting [source:
   prior-art Start here]. Keeping the ribbon still is this idea's reason to
   exist.

## Where it leads: insertion, and the second plane

- **The second plane cannot follow the first.** Every conductor of a ribbon
  end has the same length from the web, so every latched contact sits at the
  same distance D from it. If a housing is moved onto the first plane's
  crimped contacts, it then occupies the comb position where the second plane
  would be crimped, and the second plane's contacts, crimped anywhere else,
  would need 6–9 mm of stored feed to enter (the insertion stroke) while a
  straight lay stores at most ~0.4 mm (ribbon-as-pallet's B1).
- **Crimp every conductor first, then one housing move.** Crimp plane A in the
  comb, lift the crimped plane out of the open-topped comb and park it folded
  back at the clamp face (which must be the split root, ribbon-as-pallet a7's
  tear stop, or the folds peel the web); lay and crimp plane B in the same
  comb; then unpark both into a 2.5 mm comb. Two half-rows spread about the
  ribbon's centre at 5.0 mm interleave at exactly 2.5 mm, and crimped contacts
  fit side by side there (0.45–0.7 mm between insulation crimps [calc final
  §8]). A housing held on the same board is moved onto the whole row in one
  push (into-the-housing i3), with zero stored feed (ribbon-as-pallet K4).
- **Or no planes at all:** [`f10`](f10-lift-once-fin-from-below.md) keeps the
  ribbon flat at 2.5 mm, lifts one conductor 3.5 mm, and the same steel C
  crimps it from a fixed station with a fin rising from below.

## Contribution

- **The ribbon is placed once and never moved** until both planes are
  crimped.
- **A closed-loop crimp head** that any positioner can carry: a printer-class
  gantry, a desktop CNC, or a hobby arm (Kurabo's robot brings wire to a stock
  press; here the arm would bring the press to the wire).
- **Leave forward, drop the anvil:** the exit rule for any head that crimps a
  contact on a wire it did not bring.
- **The captured barrel as its own funnel**, aimed by a camera.

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Cut | the person |
| Splay | the person, by laying the ribbon into the comb (after a split into planes) |
| Strip | before; or a stripping head on the same gantry |
| Pick contact, cut tab | **automated** |
| Thread and crimp | **automated** |
| Insert | after; or both planes crimped, merged into a 2.5 mm comb, and a housing moved onto the whole row |

## Major unresolved problems

- **A narrow nose** carrying a knee-driven crimper and a wedge-dropped anvil in
  ~6 mm width without losing stiffness.
- **The anvil wedge's repeatability** after each drop: it sets the crimp's
  floor, so it has to return to within ~0.01 mm, or the head re-touches every
  crimp.
- **Aiming a 1.4–1.9 mm barrel mouth** at a tip standing 4–5 mm out of a comb.
- **Gantry choice.** Whether a desktop CNC kit's repeatability and Z travel
  suit; unmeasured.
- **Dies.** Everything f3 and f7 leave open about dies applies here.
- **Cycle.** One contact carried per trip, probably one to two minutes a crimp
  [estimate], which slowness allows.
- **Parking the crimped plane** folded back at the clamp face, and unparking
  both planes into a 2.5 mm comb without a pick (straight looms) or with
  into-the-housing i6's sort (J4, J7).
- **The touch probe** needs the far-end port wired on every ribbon end.

## Which conclusions rest on assumptions

- **Head mass, nose width, wedge self-locking and gantry repeatability** are
  estimates.
- **Knee force** rests on the modelled force family.
