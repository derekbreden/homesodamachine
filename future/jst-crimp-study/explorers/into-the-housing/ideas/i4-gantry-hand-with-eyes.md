# i4 — A slow gantry hand with a camera and a force wrist that operates the crimper and inserts

- **Numbers:** [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt)
  [calc geometry §n], [`../calc/wave2.out.txt`](../calc/wave2.out.txt) and
  [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w2/w3 X].
- **Coordinates** as in [`../handover.md`](../handover.md).
- **Related:**
  - [k6](k6-one-gantry-crimps-in-the-fan-then-sorts.md), force-and-form's "one
    gantry, two tools" with i6 in place of this hand's direct insertion;
  - [i6b](i6b-post-bed-through-the-housing.md) (the hand can thread onto its
    post bed);
  - [i2d](i2d-locator-the-lance-never-touches.md) (the stub as the crimp
    station's locator);
  - [i6](i6-sort-then-push.md) (the loft uses its placing rule).

## Picture it

**On the bench.**
- A small three-axis gantry: a desktop CNC frame (3018 class) or a printed
  Cartesian frame on lead screws. Lead screws hold position unpowered and step
  in 0.01 mm increments.
- On its Z carriage, a **hand**:
  - two printed fingers with thin steel tips, closed by a hobby servo;
  - a **wrist flexure**: a printed parallelogram with a magnet and a linear Hall
    sensor (or a small bar load cell), reading push and pull along Y, and
    lockable or loose in X and Z;
  - a small camera looking down past the fingertips.
- The ELP camera is fixed above the work area for the wider view.
- Within reach, all fixed to the frame:
  - a **contact tray**: printed pockets, each holding one loose contact lance
    down and box +Y, filled by the person;
  - a **crimp station** that captures a contact before the wire arrives:
    force-and-form's [f3](../../force-and-form/ideas/f3-knee-micropress.md) knee
    press (strip-fed), or the SN-2549 in a cradle
    ([f1](../../force-and-form/ideas/f1-motorised-ratchet-crimper.md)) with
    [i2d](i2d-locator-the-lance-never-touches.md)'s stub as its locator;
  - the **ribbon clamp** with a **loft**: the split conductors wait in ribbon
    order, ~8–10 mm above the plane where inserted conductors will lie;
  - the **housing nest**: printed, or a real header on a small PCB.

**Cycle for cavity n.**
1. **Place the contact in the crimp station** (Derek's priority step).
   - With f3, the strip feeds itself.
   - With the cradle, the hand picks a contact from its pocket by the box's
     sides and seats it against the stub.
   - The station closes to capture, and the fixed camera checks it.
2. **Place the conductor in the contact.**
   - The hand picks conductor n from its loft slot, gripping 2–3 mm behind the
     stripped edge, above and below.
   - It threads the tip axially into the captured barrel through its flared
     rear, as the WC-110 procedure and f3 do. The fingers never enter the die
     from above.
   - The camera checks the insulation edge in the window.
3. **Crimp.** The wrist goes loose in X and Z, stiff in Y, and the station
   closes.
4. **Prove.** The wrist locks and pulls −Y to ~20 N against the station's fork.
5. **Carry.**
   - The hand draws the crimped contact out and re-grips it on the crimped
     barrels.
   - The small camera photographs the contact in the fingers (Cellios measures
     crimp pose after every handling [context prior-art §0]).
   - The gantry corrects its target by what it saw.
6. **Insert.**
   - The hand brings the nose to cavity n's lead-in, tilted ~10–15° nose-down,
     then levels it as it slides in: Sogang's "lean and slide", which took
     insertion from 3/20 to 18/20 ([arXiv 2608.06996](https://arxiv.org/html/2608.06996))
     [source].
   - It pushes with the wrist reading force, lets go at the rear face, and a
     fingertip blade finishes the last 0–1.8 mm [calc w3 H].
7. **Check.** Re-grip behind the housing and pull back at 5 N; under ~0.2 mm of
   travel passes. With a header nest, post continuity names the cavity.

## At a glance

| | |
|---|---|
| **What locates the contact** | The crimp station's locator (f3's strip pilot pin, or the stub) from capture to crimp; the fingers and the hand camera's measurement from carry to lead-in; the cavity after |
| **What locates the conductor** | Its loft slot; then the fingers, corrected by the camera's view of the insulation edge |
| **Reference for "fixed"** | The gantry frame, with tray, station and nest bolted to it. The gantry homes, then touches off a steel pin at each station once per session. The contact in the fingers is not fixed; its pose is measured at every handling |
| **What drives the crimp** | The station's own drive (f3's knee, or the cradle's lead-screw actuator) |
| **What carries the crimp force** | The station. The hand's wrist is loose in X and Z during the stroke |
| **How it knows** | Photos at capture, lay-in and in the fingers; the station's force trace; the proof pull; the wrist's insertion trace; the pull-back; post continuity with a header nest |
| **Steps it covers** | Place the contact into the crimp station, place the conductor into the contact, crimp (by command), proof pull, carry, insert (pin order and crossings in software), latch check |
| **What it hands back** | Filling the contact tray (or loading strip for f3); laying the ribbon into the loft in ribbon order; dropping in a housing; removing the loom end; clearing jams the hand reports. No crossing is made by hand |

## Why this arrangement exists

- Its precision comes from looking and correcting, a trade that suits a machine
  allowed a minute per contact.
- Everything is software: pin order, J4's and J7's crossings, J2's empty cavity,
  both ribbons of a pair, retries.
- It serves any crimp station that captures before threading, and could present
  tips to a stripper.

## Mechanism, references, tolerances

**Precision where it matters.** ±0.1 mm at the capture (the station's locator
does the rest), ±0.1–0.2 mm at the cavity lead-in, coarse elsewhere. A
3018-class frame approaching from one side repeats to a few hundredths
[estimate]; the fingertips' play is larger.

**Crossings with a loft** [calc w2 C; [i6](i6-sort-then-push.md)].
- The conductors wait in the loft in ribbon order. Each one the hand takes goes
  down into the insertion plane and lies there.
- Where a placed conductor's path crosses a waiting one's, the waiting one is
  above it by a fraction f of the loft height.
- With the lower layer first and the order running from the housing's centre
  outward, 8 mm of loft covers every loom. J4 needs 4.9–7.9 mm; J1 and J7 need
  less when placed centre outward.
- So any pin map is a list of moves. J4's 3V3 and GND and J7's GND are simply
  inserted last and lie over the rest.
- Each conductor still needs its ~8 mm of insertion feed. The loft's rise gives
  only ~1.3 mm of it (h²/2L for 8 mm over 25 mm); the rest is a hump in the loft
  slot, as with i2's saddle.

**The wrist.**
- A printed flexure at ~5 N/mm gives 3 mm of travel at 15 N, and a Hall sensor
  over a magnet reads it to a few hundredths [estimate].
- It also limits force, so a jam bends the flexure, not the contact.
- **Loose in X and Z during the crimp** [force-and-form on i4]. A rigid grip
  2–3 mm behind a barrel that the anvil is setting kinks the conductor. The
  jacket takes only 13–52 % of the mismatch at Shore 50–70A [calc w3 G].
- A small solenoid pin locks the parallelogram when the hand carries or pushes.

**The fingers.** They grip the box by its sides (1.85–1.95 mm wide [mfr S1,
source S19–S22]) for the contact pick. For everything after, they grip above and
below the wire or on the crimped barrels; fingers beside the wire hit neighbours
at 2.5 mm pitch.

## Printed and bought parts

| Part | Source |
|---|---|
| Gantry | SainSmart Genmitsu 3018-PROVer V2, $269.00, Prime-confirmed (travel and screw type not read) [sourcing/amazon-prime.md]; or a printed frame on T8 screws; or a Creality Ender 3 V3 SE as a stage ($186–219, Prime-confirmed; machine-that-sees-and-learns v1b) |
| Hand, fingers, tray, loft, nests | Printed; fingertips in stencil steel ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil)) [source] |
| Wrist sensing | ALLECIN SS49E linear Hall sensors ($7.99 for 20, Prime-confirmed) and a magnet; or the ShangHJ 5 kg bar cell with HX711 ($9.99 for 2, Prime-confirmed) [sourcing/amazon-prime.md] |
| Wrist lock | Heschen HS-0530B 12 V push-pull solenoid, $7.99, Prime-confirmed [sourcing/amazon-prime.md] |
| Finger servo | Miuzei MG90S, $13.88 for 4, Prime-confirmed [sourcing/amazon-prime.md] |
| Cameras | ELP 16MP on hand [repo: `tools.md`]. For the hand, a small close-focus board: the Plugable 250× microscope is Prime-confirmed but large for a moving hand [sourcing/amazon-prime.md] |
| Crimp station | f3 knee press, or the SN-2549 in a cradle with i2d's stub |

## Problems met, and how it answers them

1. **Floppy wire, unpredictable pose.** Unpredictable only between looks. The
   grip is 2–3 mm from the crimp, so the pose changes only at a grip or release,
   and the camera looks after each.
2. **Sogang's failures were in transfer.** Transfer failed 7 in 50 and insertion
   1 in 50 [source], with no camera and 33 s cycles. i4 trades speed for a look
   at every transfer. Still uncertain: how often silicone springback moves the
   contact after the fingers let go.
3. **Picking a 0.043 g contact.** Fingers on the box's sides in a pocket that
   exposes them; or a vacuum nozzle on the box's flat top, as LumenPnP confirms
   a pick by vacuum [context prior-art §3].
4. **Too general to finish.** The geometry is frozen: every station bolts at a
   fixed place, and the software is a fixed list of moves with measured
   corrections, not a planner.
5. **The fingers go into the die from above.** They do not: the station captures
   first and the hand threads axially (f3's order).

## Combinations

- **[k6](k6-one-gantry-crimps-in-the-fan-then-sorts.md).** force-and-form's one
  gantry carrying both f4's closed-loop head and this hand. As developed, the
  head crimps each still conductor while a carrier holds it, and the carrier
  then sorts the row for a gang push ([i6](i6-sort-then-push.md)) instead of
  inserting one at a time.
- **i4 + i6b.** The hand threads each contact onto a post of
  [i6b](i6b-post-bed-through-the-housing.md)'s bed instead of into a cavity,
  and the housing slides down the posts onto all of them.
- **With hand-tool-as-press** (this explorer's
  [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md)).
  Their self-closing crimp module (a3) can be one of the tools on i4's kinematic
  mount, so the hand never places a contact into a nest. The loom's far end in
  their terminal block gives the hand touch-off and conductor identity without
  vision.

## Contribution

- The priority step with loose contacts and no feeder (tray and stub), or with
  strip (f3).
- Insertion with the same hand, with crossings and pairs as software, made safe
  by the loft.
- Photos and force traces at every step.
- It leans on work Derek already does: software that moves motors, reads cameras
  and logs every cycle [context shared-context].

## Major unresolved problems

- **Grip design at 2.5 mm pitch** for both the contact pick and the wire push.
- **Silicone springback** after release.
- **The time to make vision corrections dependable.**
- **A lockable wrist flexure.**
- **The loft's hump** for ~6.7 mm of the ~8 mm insertion feed.

## What rests on assumptions

- Gantry repeatability and wrist resolution are estimated.
- "Lean and slide" transfers from Sogang's #26 ribbon in a 2.5 mm housing
  (SMH250) to XH on 22 AWG silicone.
- Loft heights rest on straight-line conductor paths [calc w2 C].
