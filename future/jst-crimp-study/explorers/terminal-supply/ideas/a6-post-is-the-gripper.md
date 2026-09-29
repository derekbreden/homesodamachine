# a6 — The post is the gripper: one header pin carries every contact from its supply to the die

An arrangement for loose kit contacts in a fully automated path, which takes
strip contacts just as well. It develops three things:
- [a4](a4-post-held-contacts.md)'s post, the 0.64 mm square pin the female box is
  made to grip, used as a travelling pick tool instead of a magazine;
- the loading nest machine-that-sees-and-learns proposed for a4 (its C2 in
  [its reading of this explorer](../../../exchange/machine-that-sees-and-learns--on--terminal-supply.md)):
  a nozzle cannot push a box onto a post, but a post pushed into a box whose rear
  rests on a wall needs only the wall;
- machine-that-sees-and-learns'
  [v4b pocket plate](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md)
  as the loose supply.

Sketch: [`../sketches/a6-post-is-the-gripper.svg`](../sketches/a6-post-is-the-gripper.svg)
(schematic; pick, open die, and the SN-2549 nest of x1).
Numbers: [`../calc/wave2.py`](../calc/wave2.py) §5, §6, §10, §11 [w2 §n];
[`../calc/w3.py`](../calc/w3.py) §1, §2, §4 [w3 §n]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
calc [ith-w3 X]; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
§4, §7 [mtsl §n].

**Related.**
- [x1](x1-post-feeds-the-hand-tool.md): the same head places a contact in the
  SN-2549's XH nest; its motorless form is the post pen.
- [x2](x2-crown-then-sort.md): the same head, with a fork behind the insulation
  barrel, sorts crimped contacts into a housing's target comb (and in x2's loose
  branch it does both jobs).
- into-the-housing's [i4](../../into-the-housing/ideas/i4-gantry-hand-with-eyes.md)
  picks bare contacts with fingers at 2.5 mm pitch; a post tool picks and
  measures them instead, and a6's float (±0.2 mm sideways and in Z, light
  preload) is a working specification for the lockable wrist i4 lacks.

## Picture it

- **Where things start.** Derek pours about sixty kit contacts from a CQRobot bag
  onto a printed pocket plate lying on an LED light pad, once per unit.
  - The plate has 20–30 parallel channels 2.05 mm wide at the floor, flaring
    above, open at both ends. A **lance groove** 1.0 mm wide and ≥ 1.0 mm deep runs
    the length of each channel floor. A solenoid taps the plate's edge.
  - A contact lying barrels-up sinks into a channel with its floor down, its lance
    in the groove and its wings standing in the flare. Without the groove it would
    rock on its lance 8–22°, nose up or down, and its box entry would stand
    0.9–1.7 mm above where the pin expects it [w3 §2; ith-w3 E]. With the groove
    the box floor rests on two ledges 0.43–0.45 mm wide and the entry stands at
    floor + 1.10–1.18 mm.
  - Barrels-down and side-lying contacts ride on top. This works while the open
    wings are wider than the channel, as on every clone drawing (2.46–3.0 mm)
    [w2 §10].
  - The strip version starts instead from a cut strip or reel in a small indexer,
    contacts pointing toward the front.
- **The post head.** A small gantry (the axes of a secondhand bed-slinger
  printer, or two MGN rails and a Z) carries one post head:
  - a 0.64 mm square hardened pin, its tip ground near-pointed (0.20–0.28 mm
    chamfer a side), standing 1.5–1.8 mm out of a narrow steel holder whose face
    is the datum for the box front. The pin's tip stays inside the 2 mm box, clear
    of the neck and of the strands' brush;
  - the pin can be drawn back through the holder by a micro servo, so the holder
    face strips the contact off, as in a retractable pen;
  - the holder rides a flexure that floats ±0.2 mm sideways and ±0.2 mm in Z,
    preloaded lightly from above, and a small load cell or Hall sensor reads the
    force along the pin;
  - beside the pin, a thin backstop blade on a second micro servo can drop into a
    channel.
- **Picking a loose contact.** The camera over the light pad finds a contact lying
  barrels-up in a channel; the backlit outline gives its position and which end
  its box is at.
  - The head comes down at the box end with the pin on the contact's axis and at
    the entry's height above the channel floor. The backstop blade drops into the
    channel behind the insulation barrel.
  - The pin advances into the box. The force rises to 0.2–2 N as the spring leaves
    open, then climbs steeply when the box front meets the holder face; the head
    stops there. The box entry, 0.60–0.70 mm on clone drawings, captures the
    near-pointed pin ±0.18–0.31 mm, against a placement error of ±0.04–0.07 mm
    [w3 §1].
  - The backstop lifts and the head rises. The contact comes up on the pin: the
    grip is ~500–4,700 times its weight [w2 §5].
- **Picking a strip contact.** The pins of a small strip indexer hold the carrier.
  The post enters the leading contact's box from the front. The carrier, held on
  its pins, reacts the push through the tab, and a flat track under the contact's
  floor (with the same lance groove) carries the moment. With nothing yet over the
  tab, a small flush punch from above cuts it at a line set from the contact's
  rear edge as seen [w2 §6]. The head lifts a free contact with a short, set stub.
- **Looking on the post.** Before the die, the head holds the contact in front of
  a backlight in free space. The silhouette gives the distance from the holder
  face (box front) to the conductor barrel's rear edge, to a few µm by edge fit
  [w2 §5], and U-up, roll, bent or crossed wings, the lance. A contact that fails
  is stripped off into a reject cup.
- **Placing it in the die.** The die is an open one: a2's knife-set anvil and
  punch in an anvil block under a 1-ton arbor press, with the hard stop and disc
  springs ([a2](a2-strip-indexer.md)).
  - The head lowers the contact onto the anvil until the Z float compresses by
    about 0.1 mm; the preload, a few tenths of a newton, presses the floor onto the
    anvil. It is a hold-down that touches only the box. Because the float also
    goes down 0.2 mm, an anvil or nest that sits lower than taught is followed, not
    fought.
  - Along the contact's axis, the head stops at the die's fiducial plus the offset
    measured on the post, so the conductor barrel's rear edge stands where the
    bellmouth wants it.
  - Sideways, the float lets the punch's lead-in centre the barrels. A 2–4 mm
    steel pin is 130–1,000 N/mm stiff, so without the float it would fight [w2 §5].
- **The conductor.** The ribbon carriage brings conductor k in from behind,
  steered by the insulation edge as seen (as a2). No strip lies beside the die, so
  the ribbon's other conductors meet only the punch's footprint and the narrow
  holder; they are held clear as at any single die (fanned beyond the blade,
  lifted or folded back).
- **The look before the stroke.** Across the die, level, at wing height, with a
  backlight on the far side.
- **Crimping.** The press lands on its stop. The pin stays in the box throughout:
  the barrels are in the die, and the box, ahead of the anvil, carries no crimp
  force.
- **Release.** The pin draws back through the holder, and the holder face leaves
  the box free. The ribbon carriage lifts the crimp away. If the contact stays
  with the post, the crimp did not happen; the load cell sees it.
- **Proof pull, optional.** A thin fork on the head drops into the neck between
  the box and the conductor barrel, bearing on the box's rear shoulder, and the
  ribbon carriage pulls ~20 N while the camera watches the insulation edge.
- **What the person does.** Pours a unit's contacts onto the plate (or mounts a
  strip); empties the reject cup; splays, strips and inserts, unless other
  stations do; answers the queue.

## What locates what

| Direction | What sets it | Tolerance | Note |
|---|---|---|---|
| Across the contact | the pin in the box; the float lets the die's lead-in finish | leaves centre the box on the pin to a few hundredths [estimate] | — |
| Along the contact | holder face = box front; head position = die fiducial + measured offset | edge fit 2–5 µm; printer-class axis ±0.02–0.05 mm; look again after the move | box front to barrel edge is 3.65–4.1 mm on clone drawings, ±0.05 within a lot [estimate], up to ±0.25 between brands; measured per contact, so neither matters |
| Height | anvil top; the Z float's preload holds the floor on it | float ±0.2 mm | — |
| Roll | the pin's flat faces against the leaves; U-up checked on the post | — | the channel sets roll at the pick |
| Pin into the box at the pick | channel floor and lance groove (entry height); the outline (entry position) | ±0.04–0.07 needed, ±0.18–0.31 captured [w3 §1] | — |
| Crimp height | a2's hard stop | as a2 | — |

**The reference for "fixed" is the anvil block**, carrying the die fiducials, the
camera and the backlight. The pocket plate and the strip indexer are only
supplies: the head carries the contact's position from the picture on the post,
not from where it was picked.

## What drives and carries the crimp force

a2's press: 0.8–2.6 kN from the arbor press through the punch, barrels and anvil
onto the hard stop on the anvil block. The post head carries none of it. At the
pick, 0.2–2 N along the pin [estimate, unmeasured on kit contacts] is reacted by
the backstop blade or the carrier; at release the stripper pushes the box off
with the same force. The head weighs tens of grams, so any printer-class axis
moves it.

**The lance and the knife-set anvil.** A flat anvil's front edge must stand behind
the lance tip and ahead of the conductor barrel; on the clone ranges it fits in
about half the cases [w3 §4]. A knife set sold for "XH2.54" presumably carries the
relief its contact needs [assumption]; one side look at the anvil and one at a
kit contact settle it.

## How it knows it worked

- The pick trace (rise, then wall); a trace that never rises, or rises at once,
  means no box.
- The silhouette on the post (offset, U-up, roll, wings, lance).
- The gate across the die; the stop and force trace; the after-crimp look.
- Whether the contact stays on the post at release.
- The optional proof-pull trace.

## Why a post as the gripper

- **The box is the part made to be gripped.** It centres itself on a 0.64 mm
  square post with its own spring leaves, and the crimp never touches it ("the
  wire crimp section is mechanically decoupled from the post insertion section"
  [mfr S12]). A post enters the box; a vacuum nozzle only lifts it (63 mN
  [mtsl §7]); tweezers squeeze it from outside. The post needs no clearance
  beside the box, and it holds roll by its flat faces.
- **The contact arrives at the die the same way whatever the supply.** Loose kit
  contacts, genuine BXH, strip contacts, a2d's thinning cup and contacts from a3's
  rail all end as "a contact on a post, box front on the holder face, U-up
  checked". Only the pick changes, so the choice between kit and strip stops
  deciding the die.
- **The strip's costs stay at the pick.** At the die there is no next contact one
  pitch away, no tab under the wire and no drop-shear bending the strip. The tab
  is cut before a wire exists, so a flush punch from above works, and the stub is
  set from the contact's own rear edge.
- **Loose contacts become as well located as strip ones.** The axial chain from
  the holder face to the conductor barrel's rear edge is measured on every contact
  before the die, and the head moves by the error.

## Backing out

| When | What the machine does |
|---|---|
| No box found by the pin | lift, tap the plate, look again |
| The contact on the post fails its look | strip it into the reject cup |
| The contact on the anvil fails the gate | lift it back on the post and reject it; no wire has touched it |
| The crimp fails its look after the stroke | stop the ribbon end, queue a cut-back with the photo, move on |
| The contact stays on the post at release | the crimp did not grip; stop the end and ask |

## Problems and repairs

1. **A contact lying reversed in its channel** (box at the far end). Repair: the
   channels are open at both ends; the camera reads which end the box is at, and
   the head approaches from that end with the backstop behind.
2. **A barrels-up contact rocks on its lance** on a flat channel floor [w3 §2;
   ith-w3 E]. Repair: the lance groove along every channel.
3. **Capture is set by the box entry,** 0.60–0.70 mm, not the box inside:
   ±0.08–0.13 mm with a 0.1 mm chamfer, ±0.18–0.31 mm with a near-pointed tip
   [w3 §1]. Repair: the near-pointed tip; the channel's floor sets the height.
4. **A nozzle cannot load a post** [mtsl §7]. Repair: no nozzle; the post goes to
   the contact, and a wall behind it takes the push.
5. **The pin during the crimp.** A rigid pin would fight the die's lead-in and
   bend the box or the transition. Repair: the float.
6. **A float that only goes up** could not follow a nest that seats the floor
   lower than taught (the SN-2549's nest in x1): the closing die would drive the
   contact down and the pin would bend the box against the transition. Repair:
   ±0.2 mm in Z too, preloaded from above.
7. **Releasing a contact the pin grips hard.** Repair: the stripper sleeve; the
   release does not depend on the grip or on pulling the wire.
8. **Pushing a strip contact onto the pin loads its tab** eccentrically; the tab
   yields at 2.5–14 N out of plane [mtsl §4]. Repair: the contact's floor rests on
   a flat track, which carries the moment, and the push is at most 2 N; or the
   backstop bears on the insulation barrel's rear edge above the tab.
9. **The done neighbours' crimped boxes** lie at ±p beside the station, level with
   the holder. Repair: a holder ≤ 2 mm wide clears them at any fan pitch the punch
   allows.
10. **Genuine JST contacts on the pocket plate.** If genuine wings sit inside JST's
    1.95 mm envelope, barrels-down contacts may drop into a 2.05 mm channel too
    [w2 §10]. Repair within the idea: the camera reads U-up or U-down on the post
    (wing tips, or floor and lance), and a second pick at 180° does the rest; or
    genuine contacts come from strip.

## Steps covered, and what it hands back

- **Covers:** supply (loose, or strip with its tab cut before the wire),
  singulation and orientation (plate, taps, picture), placing the contact (pick,
  carry, set on the anvil with a per-contact axial correction), holding it,
  placing the conductor in it, crimping, release, verifying (silhouette on the
  post, gate across the die, force trace, after-crimp look, optional proof pull).
- **Hands back:** pouring contacts or mounting a strip; splay and strip;
  insertion; the queue. The pin occupies the box's front, the end that enters a
  cavity, so carrying the crimp into a housing needs another hold: a post through
  the housing ([a4b](a4b-through-cavity-post.md), [a4c](a4c-post-bed-one-push.md))
  or a sort station ([x2](x2-crown-then-sort.md)).
- **Machine time** ~115 s per crimp, ~100 min per unit [w2 §11].

## Printed and bought

| Part | Printed / bought | Note |
|---|---|---|
| Pins | hardened 0.64 mm square pins, a few spares, tips ground near-pointed | [`../sourcing-requests.md`](../sourcing-requests.md) #16; 2.54 mm header strips (Prime, $7.99; cross-section not stated) for trials. K&S 0.025 in music wire (Prime, $7.24) is round and would lose the flats that set roll |
| Holder, flexure, stripper linkage, backstop blade arm | holder face steel (a filed feeler-gauge leaf, Hotop set, Prime, $8.99, or stencil steel); flexure printed PETG or 1095 shim; arms printed | — |
| Stripper and backstop actuators | two MG90S micro servos (Prime, $13.88 4-pack) | — |
| Force on the pin | a bar load cell with HX711 (ShangHJ 5 kg, Prime, $9.99, coarse for 0.2–2 N; a 1 kg cell in [`../sourcing-requests.md`](../sourcing-requests.md) #18), or a flexure read by an SS49E Hall sensor (Prime, $7.99 20-pack) | — |
| Gantry | a secondhand bed-slinger printer's axes, or MGN12 rails (Prime, $20.49) with NEMA 17 lead screws | Ender-3 V3 SE $199 [machine-that-sees-and-learns, source] |
| Pocket plate with lance grooves, tapper, light pad | printed plate; Heschen 12 V push-pull solenoid (Prime, $7.99); XIAOSTAR A5 light box (Prime, $16.99) | [sourcing/amazon-prime.md] |
| Die, press, stop | as [a2](a2-strip-indexer.md) | — |
| Camera and backlights | ELP (on hand); small white LED tiles | — |

## Contribution

A single pick tool that uses the contact's own socket. It makes loose kit contacts
as well located at the die as strip contacts, and makes the die the same whatever
the supply. With strip, it moves every strip-related conflict to a pick station
where there is no wire yet. With a fork added, the same head holds a crimped
contact for sorting into a housing.

## Major unresolved problems

- **The grip of a kit contact on a 0.64 mm pin.** 0.2–1.6 N is estimated from a
  secondhand Molex KK figure; a header pin, a kit contact and a 0.1 g scale settle
  it.
- **Pocket plate fill rate and pose odds** for kit contacts (twenty contacts on the
  light pad in one photograph give the odds).
- **Whether a kit contact rests nose-up or nose-down** without a groove (one side
  photo on a card), which confirms the groove's need and depth.
- **The post head's small mechanism:** a pin that retracts through a 2 mm-wide
  holder, a two-way float, a backstop blade and a force reading, in a few cubic
  centimetres.
- **Spear wear** on the pin over ~3,500 picks; each kit contact is speared once.
  Hardened pins, replaced per batch.
- **The die outside an applicator,** and its lance relief (as a2).

## What each conclusion rests on

- **Facts [mfr, source]:** the 0.64 mm post; JST's decoupled sections; clone box,
  entry and lance dimensions [xh-facts §1]; Prime listings.
- **Calculations [calc]:** grip against weight, stiffness, silhouette resolution
  [w2 §5]; tab cut [w2 §6]; wing widths [w2 §10]; time [w2 §11]; capture at the
  entry and the lance groove [w3 §1, §2]; rest angles [ith-w3 E]; lance window
  [w3 §4]; nozzle and tab [mtsl §4, §7].
- **Estimates:** within-lot box-to-barrel tolerance ±0.05 mm (the per-contact
  measurement makes it irrelevant); leaves centring to a few hundredths; lance
  width under the groove.
- **Assumptions:** post grip (secondhand Molex analog); kit contacts are
  clone-shaped with wings wider than 2.05 mm; the knife-set anvil carries a lance
  relief.
