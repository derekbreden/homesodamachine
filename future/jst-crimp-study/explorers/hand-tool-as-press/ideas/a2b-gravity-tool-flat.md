# A2b — Gravity: the tool lies flat, loose contacts drop into the nest, the ribbon hangs into them

## Picture it

**Where things start.**
- **The tool.** The SN-2549 lies flat on a printed stand, jaw plane
  horizontal, ~60–80 mm above the baseplate. The nest axis points straight
  down, and the jaw's front face (the box side) is underneath. The pusher,
  load cell and insulated flap blade are [a1](a1-squeezer-cradle.md)'s.
- **The stop.** A printed stop plate under the front face has a shallow
  pocket where the box's front end lands.
- **The revolver.** Above the tool, on a stepper-turned hub, sits a printed
  disc with pockets round its rim. Each holds one loose kit contact, box down,
  in the one orientation the pocket's shape allows. The person fills it, one
  unit's worth (53 plus spares), whenever convenient, away from any wire.
- **The ribbon** hangs from a clamp on an X–Z carriage, conductor tips down,
  stripped to the length set from one measured contact of the lot (below).
  Its far end is in the far-end block.

**What moves.**
1. **Drop.** When a pocket turns over the drop hole, its contact falls down a
   printed chute and through the open nest, box first. The chute's section
   follows the contact's end view including the lance: a slot on the floor
   side lets the lance ride clear. The chute's lower end is a printed tongue
   that reaches down between the open jaws to just above the anvil, and lifts
   out after the drop. The contact lands in the stop pocket, and the blade
   comes down into the neck behind the box.
2. **Hold.** The pusher closes to hold, and the disc turns on.
3. **Present.** The comb holds the split ends, and the fork stands conductor
   *k* out of the row. A close-fitting printed U-guide just above the tool's
   rear face sets the conductor's line for its last 5–8 mm.
4. **Feed.** Z lowers conductor *k* until amber (the strands enter the
   contact), then green (they reach the blade).
5. **Crimp, unload.** The pusher runs the stroke. It opens to the limiter, and
   the flap lifts. The crimp moves 1–1.7 mm sideways off the anvil, then Z
   draws it up and out.

**What locates what.** "Fixed" is the lower jaw.
- The contact: gravity onto the stop pocket, then the blade in the neck and the
  nest at hold.
- The conductor: the fork and the U-guide set its line; amber and green set
  its depth. Its own weight does not straighten it (below).

**What drives and carries the crimp force.** a1's pusher through the tool's
linkage; the force closes inside the head. The stand carries the pusher's
reaction only.

**How it knows it worked.** a1's force curve on the station ESP32; amber and
green on conductor *k* only; a side frame with the tool open; a proof pull at
a pull slot where the contact's neck allows one, by sample where it does not.

**What the person does.**
- Fills the revolver's pockets (or loads a stick, below).
- Clamps each ribbon end, and takes each finished end out.

The skill today, placing a tiny contact while also holding a wire, becomes
dropping contacts into shaped pockets with nothing else in hand.

Sketch: [`../sketches/a2b-gravity.svg`](../sketches/a2b-gravity.svg) (schematic).

## Steps it covers and what it hands back

**Covers:** placing the contact (gravity, loose piece), placing the conductor,
the crimp, identity, and the proof pull where the neck allows.

**Hands back:** filling the revolver away from any wire; cut, split, strip;
clamping ribbon ends and taking finished ends out; insertion, or the vertical
gang push below.

## How it relates

- Branch of [a2](a2-ribbon-to-fixed-tool.md). It changes two things:
  - **the contact source:** loose contacts (the CQRobot kit contacts on hand,
    or BXH-001T-P0.6) instead of carrier stubs;
  - **the orientation:** the nest axis vertical, so gravity seats the contact.
- The singulator is the Boeing rotating-arm feeder slowed to one pocket per
  crimp [prior-art §3, US 5,702,030]. into-the-housing's printed carrier tape
  and machine-that-sees-and-learns'
  [v4b](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md) pocket
  plate are the same idea laid flat.
- The hanging row can be squared and pushed into a housing from below
  (into-the-housing's [i3](../../into-the-housing/ideas/i3-converging-shuttles-gang-push.md)
  turned vertical, below).
- Pre-formed contacts from [a6b](a6b-flags-by-hand-foot-crimp.md)'s click
  pre-former, or change-the-question's
  [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md), turn the
  revolver into a stick (below).

## Major unresolved problems

- **Kit contacts may not match JST's.** The CQRobot contacts' origin is unknown
  [repo; xh-facts §6]. Clone drawings show wider insulation wings than JST's
  envelope. The pocket and chute shapes follow whatever is loaded, so a mixed
  bag jams. A camera measuring each contact before it is loaded (below) is the
  repair; it is still a jam risk.
- **A contact falling box-first can tumble.** It is 6 mm long, ~2–3 mm across
  and 0.043 g [xh-facts §1]. A chute that fits the end view within a few
  tenths keeps it axial, and also catches burrs and bent wings.
- **The tongue between the jaws** has to reach close to the anvil and retract
  before the jaws close to hold. Whether the open SN jaw has room for a printed
  tongue plus the falling contact (3.35–4.10 mm with the lance) is unmeasured.
- **The neighbours hang too.** The jaw law applies turned vertical: the working
  conductor stands out by *a* + 2.7 mm once neighbours carry crimps
  (8.7–14.7 mm [calc w3 §2]), the copper sets, and a finished row needs
  squaring before any gang insertion.
- **The per-crimp pull on loose contacts** needs the same neck as the blade, or
  a stepped plate ([a6](a6-foot-closed-jig-bench.md), [calc w3 §3]).

## Gravity against the lance, and against copper

**The contact side stands, with the lance kept off everything.**
- A 0.043 g contact weighs 0.42 mN.
- Folding a lance takes 1–5 N [estimate], 2,400–12,000× that [ith ex §3].
- So a falling contact cannot fold its own lance, and any edge the lance
  touches stops the drop. The chute's lance slot, and the tongue carrying it
  through the open jaw, are the repair.

**The wire side: its own weight does not straighten a hanging conductor.**
- 25–35 mm of split conductor weighs 1.2–1.7 mN. Its weight makes 2–13 % of
  the moment that holds a 20–67 mm bend elastically. A bend the copper has
  already set has no restoring moment at all [ith ex §14].
- A hanging tip therefore goes where its history puts it. The fork and the
  U-guide set its line.

## The strip length follows the kit contact

The kit contacts are the loose ones on hand, and their barrel lengths are
unmeasured. On the clone drawings' conductor barrel (1.25–1.5 mm) and window
(0.5–0.8 mm), JST's own rule S = E + A/2 + brush gives 1.60–2.10 mm, which is
the KONNRA clone spec; 2.4 mm fits a genuine barrel of ~1.8–2.05 mm
[calc w3 §7; sl w3 §4]. A 2.4 mm strip on a clone-shaped contact puts bare
strands into the insulation barrel. So the strip stop for a2b is set from one
kit contact photographed from the side under the ELP.

## Measuring each contact before it is loaded

A camera looks at each contact on the light pad before it goes into a pocket:
box length, wing width and pose (machine-that-sees-and-learns'
[v4](../../machine-that-sees-and-learns/ideas/v4-tap-look-pick.md) /
[v4b](../../machine-that-sees-and-learns/ideas/v4b-pocket-plate.md)).
- The chute is sized to the lot's measured end view, not the clone drawings'
  ±0.25 mm.
- Outliers never reach the chute.
- The same five-contact measurement at the start of a lot sets the strip stop.

## Contact supply: revolver, or a stick of pre-formed contacts

- **Revolver (loose, open contacts).** Open contacts cannot share a tube: a box
  (1.95 × 2.4) drops into the open insulation wings of the contact below
  (2.5–3.0 × 2.75–3.2 [xh-facts §1]). The disc keeps them apart.
- **Stick (pre-formed contacts).** A contact whose insulation barrel is already
  narrowed to about die width (1.8–2.05 mm, by [a6b](a6b-flags-by-hand-foot-crimp.md)'s
  click in a second SN-2549 or by change-the-question's
  [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md) pre-former)
  cannot take a box, so pre-formed contacts stack nose to tail in a
  2.1 × 2.6 mm channel with a lance groove. Stood vertical over the nest, a
  loom-order stick is the chute, and an escapement at its foot replaces the
  revolver. J2's stick carries a blank spacer at position 3, so the stick is
  the build list [htq, K3].
  - The passage through the open jaw drops a little: the box governs with c6's
    round keyhole (2.8–3.3 mm with the lance); the tool-made pre-form stands
    2.3–3.0 mm plus the lance.
  - c6's closed-ring sub-variant (ID 1.75–1.8 mm, flared rear) would also be
    the conductor guide: the hanging conductor threads axially into its own
    contact's ring. Whether the SN die re-forms a closed ring properly is
    untested.

## The hanging row, pushed into a housing from below

After the last crimp, the X–Z carriage holds every crimped conductor in a
2.5 mm comb, tips down.
- A front plate squares the noses, and a rear clamp closes behind the
  insulation crimps.
- Z lowers the row onto a housing held rear-face-up in a nest on a load cell.
  That is into-the-housing's
  [i3](../../into-the-housing/ideas/i3-converging-shuttles-gang-push.md) gang
  push turned vertical, and a2b already has the Z axis.
- It needs what [a2d](a2d-batch-then-gang-push.md) needs: squared fronts, a
  rear clamp, and the crossings laid by the person.

## Parts

- **Printed:** stand, stop plate, revolver disc and hub, chute and tongue,
  U-guide, comb and fork, sticks.
- **Bought:** a second SN-2549 ($22.29 [prime: B01N4L8QMW]); a1's pusher
  parts; a 28BYJ-48 geared stepper for the revolver ($14.99 for five [prime:
  B01CP18J4A]); a coin vibration motor to settle a contact that lands on an
  edge ($12.99 for 20 [prime: B07Q1ZV4MJ]); servos for the flap, fork and
  tongue; the X–Z carriage (a2's routes).
- **Contacts:** the kit's loose ones on hand; BXH-001T-P0.6, Digi-Key 137,303
  at $0.0444 [xh-facts §6].

## Rests on

- **[assumption]** The open nest's gap passes a falling contact on its tongue
  without snagging.
- **[assumption]** The flap's servo holds the blade up during the drop and
  lowers it into the neck after.
- **[assumption]** Kit contacts are uniform within a bag; the per-contact
  measurement makes this checkable rather than assumed.
- **[estimate]** Lance fold force 1–5 N.

---

Citation keys: **[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[sl w3 §n]** is machine-that-sees-and-learns'
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[htq, K3]** is a combination in
[`hand-tool-as-press--on--change-the-question-w3.md`](../../../exchange/hand-tool-as-press--on--change-the-question-w3.md);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
