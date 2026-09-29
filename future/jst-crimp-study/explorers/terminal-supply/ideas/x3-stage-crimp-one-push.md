# x3 — Stage every other cavity, crimp, leave, one push

**A combination**, named by its sources:
- this explorer's [a5](a5-housing-as-fixture.md): a post through the cavity's
  front opening pulls a bare contact 1.5 mm into the rear mouth; the lit square;
  a per-cavity look before the crimp;
- into-the-housing's [i2b](../../into-the-housing/ideas/i2b-preload-the-whole-housing.md):
  every contact crimped where it is staged, then every contact pushed home at
  once, with odd cavities before even ones;
- into-the-housing's [i2](../../into-the-housing/ideas/i2-crimp-in-the-cavity.md):
  the floating nest located only in Y, the narrow stepped crimper bottoming on
  anvil shoulders, and the lance condition;
- into-the-housing's [i6](../../into-the-housing/ideas/i6-sort-then-push.md):
  layer order, so J4's and J7's crossings need only a lifted wait.

into-the-housing proposed it as T2 in
[its reading of this explorer](../../../exchange/into-the-housing--on--terminal-supply-w3.md).
**What it changes against a5:** a5 stages, crimps and pushes one cavity at a
time, so conductor k must carry the 5.3 mm push as a 6–8 mm hump at its crimp.
x3 stages every other cavity, crimps each where it stands, stages and crimps the
rest, and only then pushes, once, for all. No conductor stores any length.

Sketch: [`../sketches/x3-stage-crimp-one-push.svg`](../sketches/x3-stage-crimp-one-push.svg) (schematic).
Numbers: [`../calc/w3.py`](../calc/w3.py) §2–4, §7, §9 [w3 §n]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
calc [ith-w3 X]; [`../calc/wave2.py`](../calc/wave2.py) §8 [w2 §8].

**Related.** [a4c](a4c-post-bed-one-push.md) uses the same order with the
contacts on posts 9 mm out of the rear face instead of 1.5 mm inside the mouth.

## Picture it

- **One X stage** carries the housing nest and the web clamp with a 2.5 mm root
  comb. The web must ride with the housing: once a contact is staged and its
  conductor laid in, the ribbon is tied to the housing [w3 §3].
  - The nest is located only in Y. It floats ±0.2 mm in X and Z on a printed
    parallelogram flexure (into-the-housing i2). The seated or staged wires
    resist that float with 0.01–0.09 N [ith-w3 G], so a fixed anvil lifts the
    staged box and drags the housing to its own line, with no per-cavity floor
    measurement.
  - A Y drive between web and nest runs through a 20 kg load cell.
- **The fixed station:**
  - a5's staging post, entering through the front post opening from under the
    mating face, with a light behind it so each empty cavity shows the rear
    camera a lit square;
  - a lance-grooved shuttle nest, filled by a nozzle or by hand [w3 §2];
  - the crimp head: a narrow stepped crimper (3.1 mm conductor step with 0.8 mm
    walls, 2.5–2.7 mm insulation step) on a knee in a fist-sized steel C, over an
    anvil whose shoulders below the floor catch the crimper's walls (into-the-
    housing i2, force-and-form [f8](../../force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md));
  - one lift finger with a small clamp;
  - a side camera.
- **Staging the odd cavities.** With the web drawn back so no stripped tip lies
  on the shuttle's path, the machine stages bare contacts 1.5 mm into cavities 1,
  3, 5, …, centre outward. For each, the post spears the contact from the
  grooved shuttle and draws it into the mouth; the side camera measures the
  depth and the lit square confirms the cavity. Open wings of staged odd
  contacts, 5 mm apart, do not touch.
- **The odd pass.** The web advances. The even conductors (and J4's and J7's
  upper-layer conductors) wait lifted ~4 mm on a loft at the root; the odd
  conductors come down into their staged contacts' barrels. Each conductor's
  reach is trimmed by pressing a small saddle hump, because a torn silicone edge
  scatters per conductor and the tip moves 1.7–3 times the press depth
  (force-and-form); the web is set slightly long so the hump only shortens. Each
  odd contact is crimped. With the even lanes empty and their conductors lifted,
  there is room beside the die.
- **The even pass.** For each even cavity:
  1. The finger holds even conductor k up.
  2. The shuttle and post stage its contact beneath, 1.5 mm into the mouth. The
     open wings clear the crimped neighbours' insulation barrels by +0.03
     (3.0 mm wings) to +0.30 mm (2.46 mm) [w3 §7].
  3. The finger lays the conductor into the barrels, and the narrow stepped
     crimper crimps it between crimped neighbours: +0.20 mm at the conductor
     step, +0.17–0.28 mm at the insulation step [w3 §7].
  4. After each crimp the post withdraws out the front, and the crimped contact
     stays staged by the mouth's friction and its own conductor.
- **Crossings.** J4's and J7's upper-layer conductors (3V3 and GND; GND) wait on
  the loft until their cavities come last. Those cavities lie at an end of the
  housing [into-the-housing i6], so the lower layer is complete beside them.
- **Proof pull, per wire, before the push.** A slotted blade drops behind every
  insulation barrel. The finger's clamp pulls each wire −Y to 20 N in turn while
  the camera watches its insulation edge. Pulling the web would pull all of them
  and leave each wire's share unknown.
- **One push.** The nest drives −Y by 5.25–5.45 mm onto every staged contact at
  once [w3 §3]. The load cell shows the lance events (39–88 N in all at the
  KONNRA clone's 9.8 N per contact [w3 §7]); the lit squares go dark; a 5 N
  pull-back per wire confirms each latch.
- **What the person does.** Loads the housing and the split, stripped end; keeps
  the shuttle's supply filled; lifts out the finished end and labels it.

## What locates what

| Moment | Reference | Located part |
|---|---|---|
| Staging | the staging post in the box; the side camera measures depth | contact, 1.5 mm into cavity k |
| The crimp | the fixed anvil; the floating nest lets the housing follow it | barrels on the anvil's line |
| Crimp height | the crimper's walls landing on the anvil's shoulders | crimp |
| Proof pull | the slotted blade behind the insulation barrel | contact |
| The push | the keyed nest on its Y slide; the cavities' own walls | every contact |

**The reference for "fixed" is the crimp head** (steel C, knee, anvil,
shoulders), with the staging post and camera beside it. The housing floats to it.

## What drives and carries the crimp force

A knee in a fist-sized steel C (force-and-form f3/f4/f8) closes the crimper onto
the anvil; its walls land on the anvil's shoulders below the floor, which sets
crimp height inside the C. 0.8–2.6 kN goes round the C and nowhere else. The
housing carries none of it: the box sits ahead of the anvil in the mouth, and
the anvil's front edge stands behind the lance or has a lance slot (below). The
push is the nest's lead screw through the 20 kg cell into the housing.

## How it knows it worked

The lit square and the side look for each staging; the crimp's force against die
gap (knee) and the after look; the per-wire proof-pull trace; the push trace;
the squares going dark; the 5 N pull-back per wire.

## The lance and the anvil at the mouth

Staged 1.5 mm deep, the lance tip stands ~0.9 mm outside the face and the
conductor barrel starts ~1.1 mm behind it, so a flat anvil's front edge has
~0.06 mm between the two [ith-w3 D]. Across the clone drawings' ranges the flat
anvil fits in about half the cases: on xh-facts' lance tip of 2.4–2.6 mm the
margin is −0.30 to +0.10 mm; on the 2.24–2.64 mm range into-the-housing used it
is −0.34 to +0.26 mm [w3 §4]. The other half needs a lance slot in the anvil's
front, 0.8–1.0 mm wide, with the conductor barrel's first 0.1–0.3 mm on the
slot's shoulders. One side photo of a kit contact settles which.

## Supply for the staging

- A nozzle into the lance-grooved shuttle, then the staging post (above). Kit
  contacts, loose BXH, or strip contacts cut first.
- [a3](a3-hanging-rail.md)'s rail over a housing lying rear face up: the
  escapement drops each contact box-first into an odd cavity, onto a post
  standing up through the front opening whose tip stops the box 1.5 mm deep.
  Left to gravity alone the contact would slide to its lance's own stop, ~2.4 mm,
  too deep for the anvil.
- Derek at the lit cavity when the machine asks, with the same look run on his
  placement.

## Problems and repairs

1. **Crimped contacts must stay staged at 1.5 mm** with the post gone while their
   neighbours are crimped. Mouth friction is unmeasured. Repair if it is not
   enough: leave a short post in every staged box (a bed of posts from the front,
   as [a4c](a4c-post-bed-one-push.md)), which then guides the push as well.
2. **The waiting conductors beside the die.** Flat at 2.5 mm they clear the
   narrow stepped crimper (+0.10 at the conductor step) but meet a 3.5 mm punch
   by 0.10 mm [w3 §7]. Repair: they wait lifted, which also lets the odd pass use
   an ordinary knife set if one fits within ~1 mm of the housing face. With one
   die set for both passes, the narrow crimper serves throughout.
3. **The lance window at the mouth.** Repair: a lance slot in the anvil (above).
4. **The web's Y sets every conductor's reach at once,** and tear scatter per
   conductor needs the saddle-hump trim, which can only shorten. The web is set
   long by the scatter.
5. **J1** is 5 odd and 4 even stagings; J2 with cavity 3 empty is odd 1, 5, then
   even 2, 4, 6 [w3 §7].
6. **Staging an even contact between crimped neighbours** leaves +0.03 mm per
   side for the widest clone wings. The tongue of the shuttle and the post's pull
   keep it on the cavity's line; the camera watches the wings pass.

## Steps covered, and what it hands back

- **Covers:** placing each bare contact in its own cavity; placing each conductor
  in its contact in pin-map order, crossings included; holding; crimping; a proof
  pull per wire before insertion; insertion by one push; seat checks.
- **Hands back:** splay and strip; housing load and unload; the contact supply;
  the far-end continuity test; labelling.
- **Machine time** ~140 s per contact plus ~90 s per housing, ~2.3 h per unit
  [w3 §7, estimate].

## Printed and bought

| Part | Printed / bought |
|---|---|
| X stage with floating nest (parallelogram flexure) and web clamp, root comb, loft, finger, shuttle with lance groove | printed |
| Staging post | 0.64 mm square pin on a small lead-screw slide (uxcell 25 mm-pin headers, Prime, $15.49, or hardened pins, [`../sourcing-requests.md`](../sourcing-requests.md) #16) |
| Crimp head | fist-sized steel C with a knee and a NEMA 17 (force-and-form f3/f4); narrow stepped crimper and shouldered anvil with a lance slot (made: EDM or ground, force-and-form f7) |
| Nest drive and cell | Iverntech NEMA 17 Tr8×2 (Prime, $27.99); 20 kg bar cell ([`../sourcing-requests.md`](../sourcing-requests.md) #29) |
| Proof-pull blade | laminated stencil-steel foil |
| Light under the mating face | LED and diffuser, or 1 mm PMMA fibre (Prime, $10.89) |

## Contribution

- **From a5:** machine staging of rigid bare contacts into the product's own
  cavities, with the lit square and a per-cavity look.
- **From i2b:** the single push with nothing stored.
- **From i2:** the floating nest, the stepped dies bottoming on anvil shoulders,
  and the lance condition.
- **From i6:** layer order, so crossings need only a lifted wait.
- **Together:** every contact enters its cavity while it is a rigid 0.04 g part,
  is crimped in its final place relative to the web, and is seated by one short
  push.

## Major unresolved problems

- **The narrow stepped dies:** a 3.1 mm step with 0.8 mm walls cut to ±0.05 mm.
- **The lance and the anvil:** a flat anvil fits about half the clone range.
- **Mouth friction** on a staged crimped contact, with the post gone.
- **The web's Y** and the per-conductor hump trim.
- **The front-wall thickness,** which sets the push (assumed 0.8–1.0 mm).

## What each conclusion rests on

- **Facts [mfr, source]:** housing height and pitch [xh-facts §3]; clone contact
  dimensions and lance position [xh-facts §1]; KONNRA's insertion figure (via
  ribbon-as-pallet); Prime listings.
- **Calculations [calc]:** push length and stored feed [w3 §3; ith-w3 A, B];
  clearances in both passes [w3 §7; ith-w3 C]; lance window [w3 §4; ith-w3 D];
  floating nest [ith-w3 G]; lance groove [w3 §2]; force ladder [w3 §9].
- **Estimates:** machine time; the tip-to-hump ratio (force-and-form).
- **Assumptions:** the front wall is 0.8–1.0 mm; the mouth holds a staged,
  crimped contact; the transition length 0.4–0.6 mm read from clone drawings.
