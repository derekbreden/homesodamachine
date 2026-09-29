# b2b — The pedal-less hand station: the person pokes, the machine holds the contact, keeps the order and crimps

**A combination**, named by its sources:
- [b2](b2-hand-crimper-in-a-frame.md) (this explorer): the SN-2549 on edge in a
  frame; the contact fed, cut and placed by the machine; the captive click; the
  flap blade; the actuator through a spring link.
- **p4** "the person presents, the machine takes" (from
  [procedure-is-the-machine](../../procedure-is-the-machine/ideas/p4-person-presents-machine-takes.md)):
  the division of labour; a soft clamp that takes the conductor so the person
  lets go before the close; the proof pull after the punch lifts; lit conductor
  and lit cavity after Yazaki's light-guided insertion; inserting contact *k*
  while the machine works on *k*+1.
- **a1** "the squeezer" (from
  [hand-tool-as-press](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md)):
  the grounded flap blade as an electrode, with the loom's far end wired to the
  controller, so strands touching the blade say "at depth" and say **which**
  conductor.
- **a6** (from [ribbon-as-pallet](../../ribbon-as-pallet/ideas/a6-housing-as-last-comb.md)):
  pogo pins on the far end's cut face, so the far end needs no stripping.
- **i5** (from [into-the-housing](../../into-the-housing/ideas/i5-person-inserts-on-a-sensing-nest.md)):
  the housing plugged onto a real XH header on a sensing board, lit cavity,
  lever seat, continuity names the cavity, tug test.
- [b7](b7-borrowed-strip-head-one-conductor.md) (this explorer): a strip nozzle
  with die-hole blades, a tip trigger and a twist pull.
- terminal-supply's [a6 post head](../../terminal-supply/ideas/a6-post-is-the-gripper.md)
  and [x1](../../terminal-supply/ideas/x1-post-feeds-the-hand-tool.md): the post
  in the contact's box that places it in the tool, from strip or from loose
  contacts.

It is the arrangement closest to today's bench that takes the contact out of
the person's fingers entirely.

Sketch: [`../sketches/w2-b2b-station.svg`](../sketches/w2-b2b-station.svg).

Labels: [calc wave2 §n], [calc wave3 §n] are this explorer's
[`wave2.out.txt`](../calc/wave2.out.txt) and [`wave3.out.txt`](../calc/wave3.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**The bench.** A plate about 350 × 220 mm in front of Derek, three stations in
a row, and the loom's far end clipped into a pogo block beside it.
- **Left: the strip nozzle** ([b7](b7-borrowed-strip-head-one-conductor.md)).
  A 1.9 mm funnel leads to a steel stop plate set Ls behind a pair of die-hole
  blades, Ls being the strip length for the contact in use.
- **Centre: the crimp station** ([b2](b2-hand-crimper-in-a-frame.md)). The
  dedicated SN-2549 on edge; a funnel facing Derek on the wire side; the
  contact supply across the front (strip with pawl, steel-edge shear and post
  head, or loose contacts picked by the post head, per the build stage); the
  flap blade; and a **soft clamp**: two TPU V-jaws on a servo just behind the
  funnel.
- **Right: the insertion nest** (i5). A small PCB carrying XH headers (B4B, B5B,
  B6B, B7B, B9B-XH-A), each post an input, on a bar load cell. The housing is
  plugged onto its header; an LED under each cavity.
- **The far end.** The loom's other end is still a raw cut; the XH end is made
  first, so a bad crimp costs only a cut-back. Its cut face is clipped into a
  pogo block, one pin on each conductor's strand face at 1.7 mm pitch (P75-E2
  conical pins, $6.49 per 100 [Prime]). Every conductor is now a wire to the
  ESP32.
- **A strip of LEDs** above the station shows the ribbon's cross-section with
  conductor *k* lit.

**One conductor, *k*.**
1. **Strip.** Derek pokes the lit conductor into the strip nozzle until its tip
   touches the stop plate. The stop plate is an electrode: far-end channel *k*
   reads continuous, so the station knows this is conductor *k*. A wrong
   conductor gets a red light and nothing moves. With the right one, a V-clamp
   inside the nozzle holds the insulation, the die-hole blades close to their
   stop, and the head pulls 3 mm back while turning ~90–180°. The slug drops;
   the strands come out lightly twisted. ~4 s [estimate].
2. **Present.** Derek moves the conductor to the crimp funnel and pushes until
   the strands touch the flap blade. Channel *k* reads continuous again, now to
   the blade: the conductor is at depth.
3. **Take.** The soft clamp closes on the insulation just behind the funnel.
   Derek lets go.
4. **Crimp.** The contact is already captive in the die; it was placed while
   Derek was stripping. The actuator closes the handles through the spring
   link; the link's switch says the close reached force; the actuator opens.
5. **Proof pull.** With the jaws open and the flap still down behind the box,
   the soft clamp pulls back 20 N. The camera watches the insulation edge for
   slip. Then the flap lifts and the clamp opens.
6. **Continuity.** Channel *k* to the tool body reads continuous through the
   crimped contact.
7. **Out and in.** Derek lifts the crimped contact out of the open mouth and
   carries it to the lit cavity on the header nest. He starts it into the cavity;
   i5's spring-limited lever seats it; post continuity names the cavity; a 5 N
   tug and a re-touch prove the latch.
8. **Meanwhile** the crimp station supplies, places and captures contact *k*+1
   and drops the flap. The LEDs move to conductor *k*+1.

**What locates what; the reference for "fixed."**
- **Contact:** the tool body (die nest, post holder face with its silhouette
  offset, captive click), as in b2.
- **Conductor:** the person's hand to within the funnel's lead-in, then the
  funnel and the blade. The soft clamp holds what the hand delivered.
- **Strip line:** the nozzle's stop plate, from the conductor's own tip.
- **Order:** the far end's pogo block. Every act (strip, present, crimp,
  insert) is checked against which channel lit.

**What drives the crimp and carries its force.** The SN-2549's own leverage,
closed by an actuator through the spring link (~3.2 kN die cap). With the
Justech 1,500 N actuator ($29.99 [Prime], 7 mm/s loaded, no feedback) an AS5600
on the handle pivot ($7.99 [Prime]) finds the captive click; the
PA-01-POT ($155.39 [Prime], 750 N) has its own potentiometer.

**How it knows it worked.** Identity at the stripper; identity and depth at the
blade; force at the spring link; camera before and after; proof pull with slip
watched; continuity through the crimp; cavity identity and latch at the nest.
Every one is logged against the loom, conductor and cavity.

**What the person does.** Splits the web (by hand, or on
[b6](b6-pierce-at-the-root-pull-to-the-tip.md)'s hand rip board), clips the far
end into the pogo block, then per conductor: pokes into the stripper, pokes into
the funnel, lifts out, inserts. Loads contacts and housings, and labels.

## Steps it covers and what it hands back

- **Covers:** strip (b7 nozzle, tip-triggered), supply contacts, place the
  contact on the conductor, crimp, verify the crimp, and verify insertion and pin
  order: J4's and J7's crossings and J2's skip are enforced electrically at three
  points (stripper, blade, cavity).
- **Hands back:** splitting, presenting twice per conductor, lifting out,
  inserting, loading contacts and housings, labels.

## What it removes, and what it does not

- **Removed from the person:** every contact touch (feeding, placing, holding
  captive); the pedal; holding the ribbon through the close; stripping by hand;
  remembering the order.
- **Minutes:** ~37 attended minutes per unit against 46 for today's hand method,
  both counted with procedure-is-the-machine's task library, or ~33 with a hand
  rip board for the split [calc wave2 §5]. The machine cycle is ~22–26 s with
  the Justech's 7 mm/s [calc wave3 §6] and Derek's share ~17 s (~9 s of poking,
  ~8 s of inserting), so Derek waits a few seconds a conductor. The saving is
  modest; the contact leaving the fingers, the log and the order are the point.

## One contact type from the first week

The first sections and pulls qualify the SN-2549 on one contact, and the
nozzle's stop plate is set for that contact's strip length. A station that
changes contact between stages starts both again, since clone kit contacts are
drawn with 2.46–3.0 mm insulation wings against JST's 1.95 × 2.4 mm envelope
[facts §1] and want a different strip length. So the build order holds one
contact type throughout, by one of these routes:
- **(a) The kit's maker on a reel.** First look at a kit contact's rear for a
  tab stub (terminal-supply's [a7](../../terminal-supply/ideas/a7-if-the-contacts-switch-to-strip.md)).
  If it has one, it was cut from a reel, and a clone reel such as LCSC CJT
  A2501-TP (665,523 at $0.0079 [facts §6]) may be the same contact on strip;
  one caliper comparison says.
- **(b) Loose throughout.** The post head picks loose contacts from a pocket
  plate at every stage (terminal-supply's x1), and no strip is ever used.
- **(c) Genuine from the start.** Genuine BXH-001T-P0.6 loose (Digi-Key 137,303
  at $0.0444 [facts §6]) for the loose stages, and SXH-001T-P0.6 strip for the
  strip stages: the same contact in two supply forms.
- **(d) The thinning cup.** Once [b8b](b8b-flat-spool-line-over-a-crown.md)
  runs, its thinning cup drops loose contacts from the same reel the line
  crimps.

## Build order: useful in its first week

1. **The crimp station, contacts by hand.** A second SN-2549 in the saddle, the
   actuator and spring link, the flap blade, the far-end pogo block. Derek sets
   one contact per crimp on terminal-supply's post pen (a header pin in a pen
   body, motorless), or in a keyed flap (force-and-form f1), from the chosen
   supply. It is already pedal-less and already checks identity and depth.
2. **Add the soft clamp**, so Derek lets go before the close.
3. **Add the post head** with a pocket plate (route b) or the strip track, pawl
   and steel-edge shear (routes a, c). The contact leaves his fingers.
4. **Add the strip nozzle** ([b7](b7-borrowed-strip-head-one-conductor.md)).
5. **Add the header nest** (i5) and the LED strip. The order is now the
   machine's.

Each stage is a working bench tool on its own.

## References and tolerances

| Quantity | Needed | Provided by |
|---|---|---|
| Conductor into funnel | the hand, within a ~3 mm lead-in [estimate] | funnel |
| Strands at depth | strands to the blade, brush visible | flap blade, confirmed electrically |
| Strip length Ls | 2.4 mm for genuine JST [facts §1]; 1.85–2.1 mm for clone contacts [terminal-supply calc w3 §3] | nozzle stop plate, set by shim for the one contact in use |
| Die force | ~3 kN cap | spring link |
| Conductor identity | the recipe's order | far-end pogo channel lit at the stripper, blade and cavity |

## Printed and bought

- **Printed:** base-plate fixtures, saddle, clevis and spring-link housing,
  track or pocket plate, post holder and slide, flap, funnels, soft-clamp jaws
  (TPU), nozzle body, pogo block, LED strip holder.
- **Bought:** SN-2549 ($22.29 [Prime]); an actuator and, for the Justech, an
  AS5600 [Prime]; DS3218 and MG90S servos [Prime]; pogo pins [Prime]; XH headers
  (the CQRobot kit on the bench includes B2B–B4B headers [Prime row]; B4B-XH-A at
  Newark, 171,802 in stock [into-the-housing, source]); bar load cell and HX711
  ($9.99 [Prime]); ESP32; b7's blades; contacts by the chosen route.
- **On hand:** camera, supplies.

## Major unresolved problems

- **The SN-2549 on this ribbon.** Crimp quality, whether the jaws bottom, and
  whether the neck takes a blade.
- **Lifting the crimp out.** Whether a crimped contact lifts out of the open
  mouth with the tool on edge, or must be drawn out another way
  (hand-tool-as-press asked the same).
- **Pogo pins on a cut face.** Contact through tinned strand ends at 1.7 mm pitch
  is plausible [ribbon-as-pallet a6]; reliability over many clip-ins is
  untested, and a skewed cut shorts two pins onto one conductor's strands.
- **The strip nozzle.** Everything open in b7: die-hole blades on this silicone,
  the ligament, the twist.
- **Which contact route.** Whether the kit contacts carry tab stubs, and whether
  any reel matches them.
- **A person-paced station.** It saves ~10 minutes a unit and keeps Derek at the
  bench for the whole run; fully unattended is b1, b1c, b8 or b8b.
- **i5's own open items:** post grip in the tug test, one extra mating cycle
  per contact.

## What rests on what

- **Derek:** placing, holding and crimping is the step he most wants automated;
  the SN-2549 and the CQRobot kits are on the bench [repo].
- **Facts:** contact wing widths by supply, strip lengths, stock and prices
  [facts §1, §6].
- **Calculations:** person minutes [calc wave2 §5]; drive cycle [calc wave3 §6];
  strip length by contact [terminal-supply calc w3 §3].
- **Estimates:** person step times (4 s strip poke, 5 s funnel poke, 8 s insert);
  funnel lead-in.
- **Assumptions:** the far end is a raw square cut when the XH end is made;
  handle-to-die ratio 8–20 for the spring link's preload.
