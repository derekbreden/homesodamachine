# v4b — Branch of v4: a pocket plate that tapping fills, and a camera that checks every pocket

Explorer: machine-that-sees-and-learns. Parent: [`v4-tap-look-pick.md`](v4-tap-look-pick.md).

Numbers: [`../calc/on_terminal_supply.out.txt`](../calc/on_terminal_supply.out.txt) §11;
terminal-supply's slot calc (via this view's
[exchange on terminal-supply](../../../exchange/machine-that-sees-and-learns--on--terminal-supply.md)).
**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
Feeds: [v8](v8-tack-look-crimp.md)'s tack nest, [v1](v1-watched-nest.md)'s nest,
hand-tool-as-press's [a4c](../../hand-tool-as-press/ideas/a4c-one-nest-behind-a-tack-station.md),
and borrowed-machines' [b3](../../borrowed-machines/ideas/b3-gantry-carries-the-crimp-head.md)
head (branch below).

## Picture it

**Where things start.**
- A printed plate, ~60 × 60 mm, sits on v4's tapping tray and light pad, with
  20–30 pockets in rows. Each pocket is a channel:
  - **≥2.05 mm wide at the floor.** The box is 1.85 ±0.10 mm across on clone
    drawings, so 2.05 mm passes every box and still stops a box lying on its side
    (2.2–2.35 mm) [terminal-supply slot calc];
  - flaring wider above, so the open wings clear;
  - a lance relief under the box position at one end only.
- The person pours contacts over the plate. With the light pad under a white
  printed plate, an empty pocket reads brighter than a filled one.

**What moves.** The tapper taps; contacts slide over the plate and some drop in:
- **Barrels up:** the box bottom and barrel floor fit the floor, the wings rise
  into the flare, and with the box over the lance relief the contact sinks fully
  and **lies flat**.
- **Barrels up, reversed:** the lance meets the floor at the end with no relief,
  and the contact sits tilted on it. The camera sees the tilt; the tapper shakes
  it out, or a rotating head picks it and turns it 180°.
- **Barrels down:** the wing tips, 2.46–3.0 mm apart open [xh-facts §1], cannot
  enter a 2.05 mm floor. It rests high.
- **On its side:** 2.2–3.2 mm across. It rests on top.

After a few dozen taps most pockets are full. The camera finds each pocket's
state, and the head picks from full pockets in order. Because a seated contact
lies flat, a rigid nozzle seals on its box top (Juki 503, $14.99 [Prime]) with
no bellows and no tilt-cut face.

**What locates what.** The pocket locates the contact to a few tenths of a
millimetre and fixes its pose; the nest locates it finally. The reference for
"fixed" is the nest.

**What drives the crimp and carries its force.** Not this idea's business.

**How it knows it worked.** Each pocket's picture: full and flat, full and
tilted, or empty. Then the nest's picture.

**What the person does.** Either pours contacts and lets tapping fill the plate,
or fills the plate by hand, brushing contacts across it like a pill-counting
tray, while the printers run. Manual fill with automatic pick is a mode on its
own; so is manual fill with manual pick: a plate of flat, oriented contacts
beside today's SN-2549, picked with curved tweezers (Best Tool, $12.76 [Prime]).

**Steps it covers:** supply contacts, oriented and flat, to a nest or a head;
in the cassette branch, placement of every contact by docking. **What it hands
back:** pouring or hand-filling, and everything after the pick.

## What it changes from v4

In v4 contacts lie in random poses and the picture
chooses among them. Here the tray has **shaped pockets**, one contact each, cut
so that only the barrels-up pose fits down into them and lies flat. Tapping walks
contacts round until they drop in. The camera only confirms which pockets hold a
seated contact, and the head picks from known coordinates. Tapping, lighting and
nest are v4's.

## Branches, not in their own files

**The hanging plate** (this view's exchange on terminal-supply, with
terminal-supply's [a3](../../terminal-supply/ideas/a3-hanging-rail.md) slot
geometry).
- Stepped through-slots, 2.05 mm at the box and 2.4 mm at the barrels, in a
  static plate, filled by tapping or brushing. A contact hangs box-down by its
  wide insulation wings, like a screw by its head.
- A backlight under the plate shows each hanging contact's U direction by its
  notch [calc: on_terminal_supply §11]. A post on a small stage under the plate
  rises into the chosen box and turns 180° if needed.
- It removes a3's vibrating rail, escapement and turn pocket.
- **Uncertain:** whether a contact lying on a flat plate finds a slot and tips
  box-first into it; whether genuine contacts have a "head" at all (JST's
  1.95 × 2.4 mm envelope suggests they may not), so this may be for kit contacts
  only.

**The tap-filled plate as the crimp cassette** (with ribbon-as-pallet's
[a2c](../../ribbon-as-pallet/ideas/a2c-loose-contact-cassette.md)).
- One row of N pockets at a free crimp pitch of 4–5 mm (loose contacts need not
  follow a carrier's 7.1–9.5 mm), tap-filled, every pocket photographed.
- The ribbon pallet docks on the plate and every conductor drops into every
  contact in one motion. Far-end continuity confirms each conductor is in its
  contact.
- **Uncertain:** steel under each contact for the crimp (anvils rising through
  windows in the plate's floor as in ribbon-as-pallet's a2b, or a walking head's
  lower jaw from the pocket's open front); a pocket's rear shoulder as a pull
  reaction meets the lance and brush behind the box, so the lance relief
  continues under the shoulder ≥0.9 mm deep and the shoulder fits the measured
  neck; tapping may pop seated contacts out.

**The plate as a travelling head's supply** (with borrowed-machines'
[b3](../../borrowed-machines/ideas/b3-gantry-carries-the-crimp-head.md)).
- b3's head on a printer carriage takes contacts from an SMT-style strip feeder,
  which takes strip only. A pocket plate at the frame's side gives the same head
  loose kit contacts: the head's pick moves to a known pocket, lifts a flat
  contact, and carries it to the conductor.
- **Uncertain:** whether b3's head, built round a strip-fed anvil and a drop
  blade at the tab root, can hold a loose contact on its anvil without a carrier
  (a box slot and front stop in its lower arm, as v1's nest).

## Problems, and what answers them

- **Pocket clearances on printed parts.** A 2.05 mm channel printed with a
  0.4 mm nozzle comes out a little under or over [estimate]. Print coupons at
  1.95–2.20 mm in 0.05 steps and keep the size that admits barrels-up and
  rejects the others; box widths vary between makers, so the plate may be
  lot-specific. The H2C's 0.2 mm hotends are on hand for finer walls [repo:
  tools.md].
- **Tapping may pop seated contacts back out.** Pocket depth close to the
  barrels-up height, and gentler taps once most pockets are full.
- **Whether vibration fills shaped pockets reliably at this size** is an
  assumption; industrial vibratory pallet loaders for small parts exist in
  principle but are not sourced here.

## Contribution

- It moves the orientation work from software odds into a printed shape, and
  hands every contact over lying flat, which is what a simple nozzle needs.
- It gives a person a way to prepare contacts ahead, in batches, at any time.
- As a cassette, it is a placement fixture; as a head's supply, it opens a
  strip-fed head to kit contacts.

## Major unresolved problems

- Pocket geometry that admits only the barrels-up pose across clone variation.
- Fill rate by tapping; whether filled pockets stay filled.
- Cassette branch: anvils through a printed plate, and the pull reaction against
  the lance.
- Head-supply branch: a loose contact on a head built for strip.
