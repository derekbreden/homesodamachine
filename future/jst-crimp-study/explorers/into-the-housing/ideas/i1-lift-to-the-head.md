# i1 — Lift one conductor to a crimp head above the row, then set it into its cavity

- **Sketch:** [`../sketches/i1-lift-to-the-head.svg`](../sketches/i1-lift-to-the-head.svg) (schematic).
- **Numbers:**
  - [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt) [calc geometry §n];
  - [`../calc/wave2.out.txt`](../calc/wave2.out.txt) and [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w2/w3 X];
  - force-and-form's [`on_into_the_housing.out.txt`](../../force-and-form/calc/on_into_the_housing.out.txt) [f&f §n].
- **Coordinates** as in [`../handover.md`](../handover.md).
- **Related:**
  - branch: [i1b](i1b-narrow-tooling-in-the-row.md) (narrow dies in the row, no
    lift);
  - [i6](i6-sort-then-push.md) (the gripper can hand its contact to i6's target
    row instead of the cavity);
  - [i2d](i2d-locator-the-lance-never-touches.md) (the stub as the head's seat
    for loose contacts).

## Picture it

**On the bench.**
- A carriage on one X rail carries three things, front to back:
  - the housing nest, holding an XHP with its rear face toward the ribbon;
  - a saddle comb with one groove per cavity at 2.5 mm pitch;
  - the web clamp gripping the unsplit ribbon.
- The person has laid the split, stripped conductors over the saddles in
  housing order. Each has a hump that stores its feed. The tips point at their
  cavities and stop ~8 mm short of the rear face.
- The carriage walks the housing and ribbon together past one fixed station,
  2.5 mm per cavity.
- The station's **crimp head** sits 16–20 mm above the row [calc geometry §9]. It
  is an ordinary-width XH head holding one open contact, lance down, box
  pointing +Y. It is one of:
  - **the iCrimp SN-2549 in a cradle, closed by a lead-screw actuator** with a
    load cell on its handle: force-and-form's
    [f1](../../force-and-form/ideas/f1-motorised-ratchet-crimper.md) or
    hand-tool-as-press's [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md).
    - The whole squeeze needs an estimated 40–250 N at the grip [f&f, drives §E],
      more than a hobby servo gives.
    - A servo on the ratchet's release lug lets a failed lay-in back out.
    - i2d's housing stub is its locator for loose contacts;
  - force-and-form's [f3](../../force-and-form/ideas/f3-knee-micropress.md) knee
    press on strip, which captures the contact first and waits for the wire;
  - an OTP side-feed applicator in a slow crank press
    ([f2](../../force-and-form/ideas/f2-crank-press-for-an-applicator.md)). Its
    pre-feed holds the contact open on the anvil and locates it, and one stroke
    crimps both barrels and cuts the tab. The gripper then plays the operator,
    Kurabo's pattern [context prior-art].

**The one moving hand.** A small **transfer gripper** on a two-axis Y–Z slide:
- two printed fingers with steel tips, each ≤ 3 mm wide, that close above and
  below the wire;
- a flexure in the fingers' mount that can be **locked or left loose in X and
  Z**, and is always stiff in Y;
- a hobby servo to close them;
- a 5 kg bar load cell in its Y drive.

**One cycle, cavity n.**
1. **Pick.** The gripper comes down and closes on conductor n's insulation
   2–3 mm behind the stripped edge, fingers locked. It enters from above and
   below, never beside, so it misses the neighbours.
2. **Lift and place on the contact.**
   - It lifts the conductor to the head's height; the hump pays out as the
     conductor rises.
   - It moves +Y, laying the stripped end into the open barrels.
   - The ELP camera, looking down at the head, measures where the insulation
     edge sits between the barrels, and the gripper corrects Y by that amount.
     If it cannot, it backs out and retries.
3. **Crimp.** The fingers go loose in X and Z and stay stiff in Y, and the head
   crimps. The anvil sets the barrel floor, and the loose fingers let the wire
   follow it instead of kinking.
4. **Prove.** The fingers lock and pull −Y to ~20 N against the head's fork or
   neck blade: the proof pull, half of JST's 39.2 N.
5. **Leave the head.**
   - The crimped insulation barrel (1.9–2.0 mm) does not pass the conductor nest
     (~1.5 mm) in +Y. So the contact leaves in Z with the jaws open, with a
     stripper if it sticks in the upper jaw (applicator practice), then moves
     +Y.
   - With an applicator, the terminal stop and strip guide lie on the +Y side,
     so the path is up, over, then down.
6. **Re-grip and carry down.**
   - The fingers re-grip on the crimped barrels: a flat pad on the floor, and a
     pad shaped to the crimp's two lobes on top, which holds roll.
   - The gripper lowers the contact in front of cavity n and advances until the
     box nose sits in the lead-in.
7. **Seat.**
   - The gripper pushes, holding 1.5–2.5 mm behind the insulation barrel, inside
     the no-buckle length [calc geometry §1], until its fingertips reach the rear
     face.
   - A slotted stencil-steel blade finishes the last 0–1.8 mm inside the cavity
     [calc w3 H].
   - The load cell logs lance fold, snap and bottom.
8. **Check and index.** A 5 N pull-back; under ~0.2 mm of travel passes. The
   carriage steps, and J2's cavity 3 is skipped.

## At a glance

| | |
|---|---|
| **What locates the contact** | The head's own locator (the stub in a cradle, the strip's pilot pin in f3, the applicator's track and stop); at insertion, the gripper's lobed pads, then the cavity lead-in and walls |
| **What locates the conductor** | The saddle comb (X, and Y of the grip point); then the gripper, corrected in Y by the camera's view of the insulation edge |
| **Reference for "fixed"** | The station frame carrying the head and the gripper slide; the carriage's detented X for each cavity; the web clamp along the wire |
| **What drives the crimp** | The head's own drive: a lead-screw actuator on the SN-2549 (40–250 N at the grip), f3's knee, or a crank press over an applicator |
| **What carries the crimp force** | The head alone. The gripper's fingers are loose in X and Z and carry none |
| **How it knows** | The camera frame at lay-in; the head's force trace (or the ratchet's release); the proof pull; the insertion trace, whose fold rise also shows the lance survived; the pull-back; post continuity if the nest is a real header ([i5](i5-person-inserts-on-a-sensing-nest.md)) |
| **Steps it covers** | Place the conductor into the contact, hold through the crimp, crimp (existing head), proof pull, carry, insert, latch check |
| **What it hands back** | Splitting, stripping, laying the ribbon over the saddles in order and making J4's and J7's crossings by hand (unless the conductors wait in a raised loft and the gripper gets an X axis); feeding the head (strip, or loose contacts to f1's flap); loading a housing and removing the loom end |

## Why this arrangement exists

- Every crimp tool that exists is too wide to work between neighbours at 2.5 mm
  pitch: 3.3 mm is free between two neighbour wires [calc geometry §2], and a hand
  tool's jaw or an applicator's punch holder is several times that.
- i1 makes no narrow tooling. It moves one conductor out of the row to the
  tooling, as the JCW-2TE ribbon crimper does with its wire fork [context
  prior-art], and brings the finished contact back.

## Mechanism, references, tolerances

**Laying the conductor in.**
- The head's locator fixes the contact. The camera's view of the insulation edge
  between the barrels is the axial reference.
- A wire stop found by touch is too delicate to be the reference.
  - A single 0.08 mm strand 2.1–2.4 mm past the insulation buckles at
    0.10–0.13 N [f&f §5], and drag along the barrel floor is the same size.
  - A ragged cut touches with a few strands first.
- A light twist of the strands (as in f3) stiffens the bundle.

**Why the fingers go loose for the stroke** [f&f §4; calc w3 G].
- The anvil sets the barrel floor, and a rigid grip 2–3 mm behind it sets the
  wire. A mismatch of 0.05–0.4 mm is forced into an S-bend of 2.5–45 mm radius,
  and copper strands set below ~67 mm: JST's bend-up/down fault.
- The silicone jacket is itself compliant. At Shore 50–70A it takes 33–52 % of
  a mismatch over 2 mm of free length and 13–24 % over 3 mm.
- At 0.05 mm the set that remains is small, ~1°; at 0.1–0.2 mm it is a real
  kink. Loose fingers remove it; the jacket alone does not.

**How high the head sits** [calc geometry §9]. The conductor must reach the head,
and later its seated position, with no change in length. With 20–25 mm of free
length and ~8 mm of feed, a straight lift puts the head 16–20 mm above the row.

**Finding the cavity.** The carriage fixes cavity n's X, and the nest fixes Y
and Z. The grip on the crimped barrels holds roll, and the cavity lead-in
corrects the rest.

## Printed and bought parts

| Part | Source |
|---|---|
| Carriage, nest, saddle comb, gripper fingers, flexure, head mount | Printed PETG; comb on the 0.2 mm right-side nozzle [repo: `tools.md`] |
| Crimp head | The iCrimp SN-2549 on hand [repo: `tools.md`]; a second unit $22.29, Prime-confirmed [sourcing/amazon-prime.md]. Or f3's knee press. Or an OTP applicator in a slow crank press (no Prime listing found for OTP applicators [sourcing/amazon-prime.md]) |
| Head actuator (SN-2549 route) | NEMA 17 on Tr8×2 (~280 N at the grip [hand-tool-as-press calc]); release-lug servo |
| Y–Z slide | Iverntech 42HD6039-05 NEMA 17 with Tr8×2 ($27.99) and MGN9 rail ($16.12), Prime-confirmed [sourcing/amazon-prime.md] |
| Gripper servo, flexure lock | Miuzei MG90S ($13.88 for 4) and Heschen HS-0530B 12 V push-pull solenoid ($7.99), Prime-confirmed [sourcing/amazon-prime.md] |
| Load cell, ADC | ShangHJ 5 kg bar cell with HX711 ($9.99 for 2), Prime-confirmed [sourcing/amazon-prime.md]; Adafruit #4541 $3.95, #5974 $9.95 [source] |
| Finishing blade | Stacked stencil foil ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil), from $3 [source]), or a Hotop feeler-gauge leaf ($8.99 set, Prime-confirmed) |
| Camera | ELP 16MP on hand [repo: `tools.md`] |

## Problems met, and how it answers them

1. **The tip lands short or long in the barrel.** The saddle sets the grip point
   to ~±0.5 mm [estimate]. The camera measures the insulation edge against the
   barrels, and the gripper's Y corrects it.
2. **Roll is lost in the lift.** Silicone twists easily; a 20 mm free conductor
   can roll a contact 20–30° [estimate]. Before the crimp the head's locator
   holds the contact's roll; after it, the fingers re-grip on the crimped
   barrels.
3. **The push buckles.** Held 1.5–2.5 mm behind the barrel, the no-buckle limit
   is ≥ 1.56 mm at 14.7 N with the nose free [calc geometry §1], marginal at the
   top of the force range. The cavity lead-in takes the nose first (K ≈ 1),
   which doubles the allowed length to ~3.1–3.5 mm.
4. **The fingertips cannot follow into the cavity.** They stop at the rear face
   with the contact 0–1.8 mm short. Hence the finishing blade.
5. **The ratchet cannot reopen if the lay-in fails.** Once one click captures
   the contact, the SN-2549 cannot reopen without completing [f&f on i1].
   Answered by a servo on the release lug, the pawl removed (hand-tool-as-press
   a1b), or f3's knee, which has no ratchet.
6. **The applicator's base may be in the way.** An applicator's base plate and
   body sit below its anvil. A row only 16–20 mm below the anvil top may collide
   with them, so the lift grows or the row comes in from the side.
7. **J4 and J7.** The crossing conductors are laid by hand over raised saddle
   grooves. Or the conductors wait in a raised loft in ribbon order, and the
   gripper, given an X axis, takes them in any order ([i6](i6-sort-then-push.md):
   wait high, place low).

## Combinations

- **With [i6](i6-sort-then-push.md).** The gripper hands its crimped contact to
  i6's target row instead of the cavity. The insertion feed then disappears (the
  housing is pushed onto the row), and the lift is set only by the head's
  clearance.
- **With hand-tool-as-press a4** (this explorer's
  [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md), C4
  and C5). SN jaws in a guided die set, with a strip pawl and a ram shear, make
  a head with its own contact feed. In a small C-frame with the barrels opening
  up, the clearance lift drops to ~5–7 mm. The 8–12 mm of feed for a
  one-at-a-time insertion is then a hump, not the lift.

## Contribution

- An existing crimp head, unchanged, so the crimp itself is the hand tool's or
  the applicator's.
- The geometric price: a lift of 16–20 mm, a finishing blade, loose fingers.
- One gripper does Derek's priority step (placing the conductor into the
  contact and holding it through the crimp), the proof pull, the carry and the
  insertion, from one grip point.

## Major unresolved problems

- **Carrying a conductor's contact to a 2.0 mm cavity.** Sogang's end-to-end
  failures were in cable transfer, not insertion
  ([arXiv 2608.06996](https://arxiv.org/html/2608.06996): transfer 43/50,
  insertion 49/50) [source]. The grip 1.5–2.5 mm behind the barrels is the
  answer here; whether it is enough is untested.
- **The head's own contact feed.**
- **A flexure that locks and unlocks in X and Z.**
- **The applicator's base** against a row 16–20 mm below its anvil.

## What rests on assumptions

- Lift height rests on the assumed free length (20–25 mm) and feed (~8 mm).
- Buckling margins rest on EI from free strands plus silicone.
- Insertion force 3–25 N is bracketed, not measured (KONNRA clone spec ≤ 9.8 N).
- The roll behaviour of a lifted conductor is a guess.
