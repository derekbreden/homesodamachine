# A6c — Flags by machine: a tack station places and pins every contact, the foot crimps each flag in the SN-2549

## Picture it

**Where things start.**
- **Station T** is machine-that-sees-and-learns'
  [v8](../../machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md) tack
  station on a bed-slinger printer stage
  ([v1b](../../machine-that-sees-and-learns/ideas/v1b-printer-as-stage.md);
  Ender-3 V3 SE, $219.00 [prime: B0F8J78BN1]):
  - a printed frame with a box slot, a lance relief and a steel insert under
    the insulation barrel;
  - a steel former with an insulation profile, best cut from the insulation
    section of a spare SN-2549 jaw so the tack is the SN's own stroke paused
    ([a4c](a4c-one-nest-behind-a-tack-station.md)), on a 35 kg·cm servo lever
    ($27.99 [prime: B07S9XZYN2]) to a loose screw stop, with a load cell under
    the nest;
  - a camera straight down on the open conductor barrel, and one across at
    wing height.
- **The pallet on the stage** is v1's fan block: the ribbon end flush-cut,
  split, stripped to the length set from the contact lot, fanned to 5 mm pitch,
  each conductor in a hinged key, the waiting ones held 5 mm up. Its far end is
  in the far-end block on the station ESP32.
- **Contacts** come loose from the kit on v4b's pocket plate, picked by a
  nozzle, or on genuine SXH strip.
- **Station C** is [a6](a6-foot-closed-jig-bench.md)'s crimp jig: the
  SN-2549 in its cradle, the cord treadle (single-stage), and
  [a6b](a6b-flags-by-hand-foot-crimp.md)'s **flag seat** (a rear U guide on
  the jacket and a sprung, keyed ledge for the box, both at *h* = 1.1–1.7 mm
  on 1–3 N springs; a wired front-stop leaf for green; wired jaws for amber).

**What moves.**
1. **T runs a whole ribbon end unattended.** For each conductor: a contact into
   T's slot (look: seated, lance standing); key *k* lowered into the open
   contact (hover look, then side look); the former down to its loose stop (the
   forming curve logged); the straight-down look at every strand, the brush and
   the edge in the window. A failed look backs the conductor out through the
   key's grip and costs a contact. A passed one leaves key *k* raised with its
   flag. Every conductor of the end is tacked in turn.
2. **The person takes the pallet to C.** The SN-2549 as sold spans the row
   (the side-entry jaw law), so the ribbon end leaves the stage here. The
   person holds the pallet's body, or unclamps the web, and bends each
   conductor out of the row by hand, 20–30 mm behind its contact.
3. **At C, per flag:** lays the jacket in the rear U, slides the flag forward
   box first until green, stops pushing, presses the treadle (amber, set down
   on the anvil, curl, coin, ratchet release), and draws the crimp out once
   the springs have lifted it back to *h*.
4. **Then** a6's pull-and-look jig and keyhole, on every crimp or on samples,
   and i5 for insertion.

**What locates what.**

| At | Contact located by | Conductor located by | Reference for "fixed" |
|---|---|---|---|
| T | Box slot and stop | Key groove, then the picture | T's frame, seen with fiducials |
| T to C | The tack: axial position and roll on the conductor | The person's hand | The flag itself |
| C | The wired front-stop leaf (axial), the keyed slot (lateral, roll), the sprung ledge then the anvil (vertical) | Carried by the contact | The SN-2549's lower jaw |

At C there is no stage to nudge Y, so the front stop is the axial reference.
It is set once per contact lot by a screw, from the box-front to barrel-rear
distances T's top camera measured on that lot; T refuses to tack a contact
outside the lot's band.

**What drives and carries the force.**
- **The tack:** 33–132 N through T's former, the steel insert and the printed
  frame, from a servo [sl w2 §5].
- **The crimp:** the foot, through the cord and a 2:1 treadle, at most
  ~120 N at the toe for ~220 N at the grip [calc w2 §5]; the tool's linkage
  and dies carry the crimp force inside the head.

**How it knows it worked.**
- T's forming curve and straight-down look, before anything irreversible.
- Green at C: the box at its stop. Amber: die touch.
- The cord cell and pulley AS5600: force against travel for every
  foot-closed crimp.
- The pull-and-look jig (height, bellmouth, window, pull) and the keyhole.
- i5's conductor-to-cavity pairing.

**What the person does.**
- Loads pallets for T (10–30 min a unit [digest]) and fills the pocket plate.
- At C, for each flag: bends it out, slides it to green, presses the treadle,
  draws it out; then the pull, the keyhole and insertion.

**Person time at C** [sl w3 §8, estimates]: 23–37 s a crimp with the pull and
keyhole, 20–33 min a unit; 9–15 min without them; plus pallet loading. Today's
is ~22 min. The minutes do not fall. The fine placement leaves the person,
every contact is placed under a straight-down look, and the machine does the
step Derek most wants automated while the person does the squeeze.

Sketch: the seat is in [`../sketches/flag-seat.svg`](../sketches/flag-seat.svg);
T is machine-that-sees-and-learns'
[`w2-v8-tack-look-crimp.svg`](../../machine-that-sees-and-learns/sketches/w2-v8-tack-look-crimp.svg).

## Steps it covers and what it hands back

**Covers (by machine):** supplying contacts, placing the contact on the
conductor, holding them together (the tack), the strictest look before any
irreversible act; (by jig and electronics) the crimp's axial reference, die
touch, the force log, pull, height and fit checks, and pin-order pairing.

**Hands back:** loading pallets and contacts, carrying the pallet to C,
bending each conductor out, every crimp squeeze (by foot), the pull and gauge,
insertion, the label; cut, split and strip.

## How it relates

- Branch of [a6](a6-foot-closed-jig-bench.md), with
  [a6b](a6b-flags-by-hand-foot-crimp.md)'s seat.
- Combines machine-that-sees-and-learns'
  [v8](../../machine-that-sees-and-learns/ideas/v8-tack-look-crimp.md) (T),
  [v1](../../machine-that-sees-and-learns/ideas/v1-watched-nest.md) (pallet and
  keys) and [v1b](../../machine-that-sees-and-learns/ideas/v1b-printer-as-stage.md)
  (stage). Proposed as W2 in its
  [exchange](../../../exchange/machine-that-sees-and-learns--on--hand-tool-as-press-w3.md);
  it is the first motorised rung [v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md)
  names for v8 ("the tack station with the crimp by hand"), with the hand
  replaced by the foot and the seat.
- With C motorised, it becomes [a4c](a4c-one-nest-behind-a-tack-station.md).

## What the seat changes at C

- **The blade goes.** The conductor's depth in the contact was set and
  photographed at T, so nothing has to find it at the tool. a6's first open
  problem, whether the kit contact's neck (0.2–0.5 mm [estimate]) holds a
  0.13–0.15 mm blade plus a brush, stops mattering for the crimp.
- **The first tooth stops mattering.** No conductor has to enter a contact
  held at the first tooth, because it is already in it. The treadle is
  single-stage.
- **The opening limiter closes further.** A tacked contact carried at *h*
  needs 3.6–4.4 mm of jaw opening, against 4.0–5.1 mm for an open contact
  carried the same way [calc w3 §5].
- **The person's fine act becomes a coarse one.** Steering a stripped
  conductor into a 1.8 mm barrel becomes sliding a contact already on its wire
  along a guide until a lamp lights.
- **Why a seat and not a hand-held set-down.** The tack's grip is 0.2–1.5 N
  wanted (0.4–9 N estimated) [v8], less than the 1–5 N that folds a lance
  dragged over the jaw's edge [ith ex §3]. A flag slid box-first on the anvil
  loses its place on the wire without any sign; carried at *h* it does not.

## What T has to do for a whole ribbon end

Tacking every conductor before any crimp asks one thing of T that one-at-a-time
tacking does not: T's former, its guide and its lever must pass between tacked
neighbours hanging at 5 mm pitch, which occupy 3.05–6.5 mm above T's floor.
Everything of T at that height must be no wider than ~7.3 mm, a little under
the 7.45 mm free between crimped neighbours, because a tacked insulation barrel
is ~2.0–2.1 mm wide [sl w3 §7, estimate].

## Major unresolved problems

- **The tack's grip window on silicone:** 0.2–1.5 N wanted, 0.4–9 N estimated
  across squeezes [v8]. A pliers-and-scale afternoon.
- **Roll in handling.** A person carrying a pallet of tacked contacts may roll
  one past the tack's ~0.34 N·mm roll resistance [sl w2 §5]. The keyed slot
  squares a small roll; a large one shows as the box not entering the slot.
- **Tacked, then re-formed, against one pass,** for the insulation crimp. A
  former cut from the SN's own insulation section narrows the question to
  re-registration (a4c).
- **The jaw opening at the nest** for a flag at *h* (3.6–4.4 mm) is unmeasured
  on the SN-2549.
- **Set copper.** Each conductor carries the key's root kink (5–12°, 20–30 mm
  behind its contact [sl w3 §4]) and the hand's bend at C. One-at-a-time
  insertion at i5 tolerates both.
- **Pallet loading** is the person's time, as everywhere.

## Parts

T, the pallet and the stage are machine-that-sees-and-learns' (v8, v1, v1b)
with their own sourcing. C is a6's crimp jig with a6b's seat. Beyond those: a
second spare SN jaw set if T's former is cut from one (icrimptools.com
$4.99–9.99 [source]; the IWS-0723K kit on Prime [prime: B09CP8RV94]).

## Rests on

- **[estimate]** The tack's grip and roll resistance [v8; sl w2 §5].
- **[estimate]** A tacked insulation barrel 2.3–2.5 mm tall and ~2.0–2.1 mm
  wide.
- **[estimate]** The jaw openings for a carried flag [calc w3 §5].
- **[assumption]** A person can bend each tacked conductor out of the row
  without rolling its contact past the keyed slot's capture.

---

Citation keys: **[calc w2 §n]** is [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[sl w2 §n]** and **[sl w3 §n]** are machine-that-sees-and-learns'
[`wave2.out.txt`](../../machine-that-sees-and-learns/calc/wave2.out.txt) and
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
