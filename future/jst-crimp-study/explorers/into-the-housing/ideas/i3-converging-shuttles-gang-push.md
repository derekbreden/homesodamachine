# i3 — Crimp at a wide pitch on shuttles, close them to 2.5 mm, push the housing onto the whole row

- **Sketch:** [`../sketches/i3-converging-shuttles.svg`](../sketches/i3-converging-shuttles.svg) (schematic).
- **Numbers:** [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt)
  [calc geometry §n], [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w3 X],
  force-and-form's [`on_into_the_housing.out.txt`](../../force-and-form/calc/on_into_the_housing.out.txt) [f&f §n].
- **Coordinates** as in [`../handover.md`](../handover.md).
- **Related:**
  - branch: [i3b](i3b-staggered-row-one-push.md) (a staggered push that reports
    each contact);
  - [i6](i6-sort-then-push.md), which keeps the gang push and replaces the fan
    plate by a programmable sort;
  - combinations K2 and K3 with force-and-form (below).

## Picture it

**On the bench.**
- A fixed base carries the web clamp at the back.
- In front of it is a row of **shuttles**, one per conductor, up to nine. Each is
  a thin printed plate riding on two steel rods that run in X, with a V-groove
  and a spring clamp pad.
- A pin under each shuttle runs in its own slanted slot in a **fan plate**
  below. Sliding the fan plate in Y spreads the shuttles to 5 mm pitch (open) or
  closes them to 2.5 mm (closed), all together.
- Beside the row stands one fixed **crimp head** at ordinary width, with a
  **steel docking pin**. It can be:
  - force-and-form's [f3](../../force-and-form/ideas/f3-knee-micropress.md) knee
    press on strip (capture, look, thread, crimp, re-touch height, proof pull,
    tab cut at the bottom of the stroke);
  - the SN-2549 in a cradle with a lead-screw actuator (force-and-form f1,
    hand-tool-as-press a1), with [i2d](i2d-locator-the-lance-never-touches.md)'s
    stub as its locator;
  - an applicator in a slow crank press (force-and-form f2).
- The whole shuttle base rides a carriage in X past the head, and has a short Y
  slide of its own for threading.
- In front of the row is the **housing nest** on a Y slide, driven by a NEMA 17
  on a T8 screw through a bar load cell.

**Loading (the person).**
- Split the ribbon back ~25–35 mm for J1, 9–18 mm for four- and five-way looms
  [calc geometry §7].
- Lay the conductors into the open shuttles in housing order. J4's and J7's
  crossing conductors go over their neighbours on a raised route in the comb
  behind the shuttles. J2's position 3 gets no conductor. Close each clamp.

**Crimping, one shuttle at a time.**
- The carriage brings shuttle n to the head, and the shuttle **docks on the
  head's steel pin**.
- At 5 mm pitch there is 8.3 mm of free width between neighbour wires, room for
  an ordinary head's jaws.
- With f3:
  - the press captures the lead contact on its strip pilot pin, and the camera
    looks;
  - the base moves +Y ~3 mm to thread the conductor through the captured
    barrel;
  - the press crimps and re-touches for crimp height;
  - the base moves −Y to proof-pull ~20 N against the head's fork;
  - the tab is cut at the bottom of a stroke.
- The contact's front now sits at a distance from the shuttle clamp set by the
  head's geometry, ±0.03–0.06 mm on a strip pilot pin [force-and-form
  placement_budget]. The strip's error goes where it belongs, into bellmouth
  and brush inside the barrel window.

**Closing and pushing.**
- The fan plate slides and the shuttles close to 2.5 mm. The contacts form a
  row at housing pitch, fronts on one line, lances down. Their conductors swing
  inward about the web, and their axes stay parallel because the clamps set
  them.
- A spring-loaded **guide comb** rises under the row and squares every box nose.
- The housing nest drives −Y onto the row.
  - The guide comb is pressed down and back, and the cavity lead-ins take over.
  - Lances fold, snap and bottom.
  - The shuttles' clamps, 2–4 mm behind each insulation barrel, carry the
    reaction.
- **No conductor bows.** The housing moves; the contacts do not.

**Checking.**
- The load cell sees the sum.
- Each shuttle clamp is released and re-closed on a spring that pulls back at
  5 N, one at a time. More than ~0.2 mm of travel is an unlatched contact.
- A camera frame of the mating face shows each lance in its window and J2's
  cavity 3 empty.

## At a glance

| | |
|---|---|
| **What locates the contact** | The head's locator during the crimp (strip pilot pin, stub or applicator track); the docking pin locates the shuttle to the head, so every contact's front sits at the head's geometry from its clamp |
| **What locates the conductor** | Its shuttle's V-groove and clamp |
| **Reference for "fixed"** | The head's docking pin during the crimp; the fan plate's slots when closed; the web clamp along the wire |
| **What drives the crimp** | The head's own drive (f3's knee, a lead-screw actuator on the SN-2549, or a crank press) |
| **What carries the crimp force** | The head alone; shuttles and base carry none |
| **How it knows** | The head's force trace, crimp height and proof pull per shuttle; the push's load-cell trace; per-shuttle 5 N pull-back; a mating-face photo |
| **Steps it covers** | Crimp (existing head), proof pull, converge to housing pitch, gang insert, per-contact latch check |
| **What it hands back** | Splitting (23–36 mm on J1), stripping, laying conductors into shuttles in housing order and making the J4/J7 crossings; loading strip or contacts for the head; loading and unloading housings |

## Why this arrangement exists

- It is this view's answer to "one contact at a time or all of a ribbon at
  once". The crimp is one at a time in the open, with room for any head; the
  insertion is all at once.
- The gang push is the only way the housing can truly come to the contacts, and
  the only way no conductor carries extra length, because every contact is
  crimped where it will finally sit relative to the web
  ([`../handover.md`](../handover.md)).

## Mechanism, references, tolerances

**What has to be on a line is the contacts, not the stripped edges** [f&f on
i3]. So each shuttle docks on the head's pin, and the head's locator places the
contact.

**Closing.** The fan plate's slots fix each shuttle's X to ±0.05–0.1 mm printed
[estimate], and the guide comb takes the last 0.1 mm.

**Closing bends set, which helps.** 13 mm of swing over 25–35 mm of free wire
puts a bend of roughly 12–24 mm radius in J1's outer conductors [f&f, L²/4δ].
Copper sets it, so once closed the conductors push nothing back against the
guide comb. The finished loom carries the set fan.

**Gang force** [calc geometry §5].
- 4–9 contacts × 3–25 N = 12–225 N (≤ 88 N at the KONNRA clone spec's ≤ 9.8 N
  per contact).
- It loads each crimp in compression through a clamp 2–4 mm behind the
  insulation barrel, inside the crimp's strength and inside the buckling length
  (3.1–7.0 mm at 14.7 N, nose guided).

**Length spread** [calc w3 E].
- Docking puts each contact where the head's locator puts it.
  - A strip pilot pin locates the contact's rear, where the tab joins, so a
    length spread appears at the fronts.
  - A stub locates the nose, so the fronts line up and the spread appears
    between contact and clamp.
- Clone drawings run 5.8–6.73 mm, each ±0.25 [source S19–S22]; the spread
  within a lot is unknown.
- When the fronts differ, the longest contact bottoms first while the clamps
  hold every conductor rigidly. So the push stops at the first wall. Each
  remaining contact is then finished alone: its clamp opens, and a slotted
  finishing tine (as in [i6](i6-sort-then-push.md)) pushes its rear to its own
  wall.
- Or the clamps ride on constant-force springs ([i3b](i3b-staggered-row-one-push.md)).

**The split it asks for** [calc geometry §7]. J1 at 5 mm pitch needs 23–36 mm of
split at 30–20°; four- and five-way looms 9–18 mm. The finished loom needs
~6–9 mm.

## Printed and bought parts

| Part | Source |
|---|---|
| Shuttles, fan plate, base, housing nest | Printed PETG; fan plate slots on the 0.2 mm nozzle [repo: `tools.md`] |
| Guide comb | Routed FR4 from the repo's PCB fab [repo: `order.md`], printed, or laminated stencil foil ([JLCPCB](https://jlcpcb.com/pcb-stencil)) [source] |
| Shuttle rods | 3 mm ground rod: no Prime listing found [sourcing/amazon-prime.md]. The Prime-confirmed 8 mm h8 case-hardened rods ($6.99 for 2) serve with shuttles that ride on a pair of 8 mm rods below the row instead |
| Clamp springs | Dianrui 300-piece compression spring kit, $6.99, Prime-confirmed [sourcing/amazon-prime.md] |
| Nest drive | Iverntech 42HD6039-05 NEMA 17 with Tr8×2, $27.99, Prime-confirmed [sourcing/amazon-prime.md] |
| Load cell | A 20 kg cell for J1's push: Geekstory 20 kg with HX711, $8.98 [Prime], 64 ratings, bar form not stated on the page ([`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)); ShangHJ 5 kg with HX711 for four-way looms, Prime-confirmed |
| Crimp head with docking pin | f3 (steel, strip-fed), the SN-2549 in a cradle, or an applicator |

## Problems met, and how it answers them

1. **Closing drags the contacts out of line.** The clamp's V-groove keeps each
   contact parallel, and the set bend keeps it there.
2. **The fronts are not on one line.** Each shuttle docks on the head's pin
   during its crimp, and the head's locator places the contact.
3. **One bad contact spoils nine good ones.**
   - Push slowly with a force ceiling; a rise out of sequence stops it; back
     off, lift the guide comb, look.
   - Only an unseated contact can be retried. An extraction pin through the
     window (XJ-06 style [mfr S10]) backs out a seated one.
   - Proof-pulling each crimp before closing keeps bad crimps out of the push.
4. **A wide split looks bad or weakens the loom.** A real cost on J1.
   - Odd-then-even at 5 mm gains nothing: once the odds are in place, the
     evens' tooling has only 2.5 mm to its neighbours again.
   - The alternatives are a narrower head (i1b's or i2's dies), or crimping on a
     cassette at strip pitch and closing only 4P ends (K3 below).
5. **J4 and J7 crossings.** Shuttles on rods cannot pass one another, so the
   row's order is the order the person laid. The crossing conductors are laid by
   hand over raised routes in the comb behind the shuttles. [i6](i6-sort-then-push.md)
   replaces the fan plate by a carrier that places each contact into a fixed
   target row, which makes the crossings software. A board pin order that makes
   every ribbon straight (i6) removes them altogether.

## Combinations

- **K2: shuttles through a knee press, with i2's crown** (i3 + force-and-form f3
  + i2), proposed by force-and-form.
  - f3 stands beside the row at 5 mm pitch, its nose under ~6 mm wide in
    8.3 mm of free width.
  - Threading moves every conductor +Y. The uncrimped neighbours at ±5 and
    ±10 mm would run into the unused contacts on the strip at ±7–9.5 mm.
  - i2's crowned block drops the unused strip 3.6–4 mm away (radius
    6–12.5 mm, strain 0.8–1.6 %, one-way) [f&f §10].
- **K3: cassette, then fan plate** (force-and-form f5 + i3), for the 4P family
  (five housings, 38 % of crimps).
  - f5's cassette crimps a whole 4P end at strip pitch in one stroke of the shop
    press. Its comb is i3's shuttle row. The end closes to 2.5 mm and the
    housing is pushed on.
  - f5's summed force cannot name a failed station; i3's per-shuttle pull-back
    and a 20 N proof pull per shuttle before closing can.
  - A 4P at 7–9.5 mm strip pitch needs 15–24 mm of split.
- **With hand-tool-as-press** (this explorer's
  [exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md)):
  - **C1:** their travelling tool (a3) crimps in place over a fixture that
    carries i3's housing slide, guide comb and pull-back.
  - **C2:** their three-axis head (a2) holds the web and is the shuttle
    carrier. After the last crimp it presents the row to i3's fixed housing
    press.
  - **C4:** the head beside i3's row is their a4: SN jaws in a guided die set
    with a strip pawl and a ram shear.
  - **C6:** the housing rides on a real header whose posts are wired, and the
    loom's far end sits in a terminal block.
    - As each box slides onto its post during the push, the ESP32 logs which
      conductor reached which post and at what housing position.
    - It scans all of them in under 2 ms (< 0.4 µm of push at 0.2 mm/s) [calc:
      exchange_hand_tool_as_press §11].
    - The latch still needs the pull-back, because a box meets its post before
      its lance is home.
    - [i6b](i6b-post-bed-through-the-housing.md) takes this further.
- **Fronts by a front plate** (same exchange): a plate that every box nose
  touches, with the clamps closing late and any excess length going to slack,
  sets the fronts without the strip and clamp sharing one reference.

## Contribution

- The crimp spacious and one at a time; the insertion tight and all at once.
- Zero stored feed.
- Per-contact verification by per-shuttle pull-back, with no camera in the
  insertion loop.

## Major unresolved problems

- **The split length on J1.**
- **Guide-comb retreat** timing, found by trial.
- **Jam recovery** on a nine-contact push.
- **Crossings** stay with the person.

## What rests on assumptions

- Gang force totals rest on 3–25 N per contact.
- "Fronts to ±0.3 mm" assumes a ~0.3 mm entry chamfer.
- The guide comb assumes the boxes can be squared from below by U-slots.
- The mating-face camera check assumes latched lances are visible through the
  windows [context xh-facts §3, assumption].
