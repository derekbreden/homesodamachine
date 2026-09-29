# k7 — Combination: pre-formed contacts, snapped onto the conductor and crimped in their own cavity

- **Sources.**
  - change-the-question [c6](../../change-the-question/ideas/c6-pre-form-the-contact.md):
    each contact's insulation barrel is formed into a keyhole on a mandrel
    before any wire, and the jacket then snaps into it.
  - into-the-housing [i2](i2-crimp-in-the-cavity.md) as it stands (K1, with
    force-and-form's [f3](../../force-and-form/ideas/f3-knee-micropress.md) knee
    and [f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md) steel
    C). The cavity is the locator, the nest floats, and stepped dies bottom on
    anvil shoulders.
  - change-the-question proposed the pairing in
    [`../../../exchange/change-the-question--on--into-the-housing-w3.md`](../../../exchange/change-the-question--on--into-the-housing-w3.md)
    (its S1, S1b, S1c and S4).
- **Sketches:** [`../sketches/k7-snap-in-the-cavity.svg`](../sketches/k7-snap-in-the-cavity.svg)
  and [`../sketches/insulation-mouth.svg`](../sketches/insulation-mouth.svg), both schematic.
- **Numbers:** [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w3 X];
  change-the-question's [`wave2.out.txt`](../../change-the-question/calc/wave2.out.txt)
  [ctq w2 §n] and [`on_into_the_housing_w3.out.txt`](../../change-the-question/calc/on_into_the_housing_w3.out.txt)
  [ctq w3 §n].
- **Coordinates** as in [`../handover.md`](../handover.md).
- **Related:** [i2b](i2b-preload-the-whole-housing.md) (its two-pass version
  runs on pre-formed contacts, below);
  [i2d](i2d-locator-the-lance-never-touches.md) (a housing stub as the
  pre-former's box pocket).

## Why the pairing does something neither does alone

- **i2's insulation step cannot swallow the kit's open wings.**
  - The stepped crimper that fits beside a seated neighbour at 2.5 mm has an
    insulation step 2.5–2.7 mm wide, so its mouth is at most ~2.3–2.6 mm.
  - Kit clone wings open 2.46–3.25 mm [source S19–S22]. i2 gets past them only
    by pushing the neighbour's jacket aside, which is untested.
  - A pre-formed keyhole is 1.96–2.14 mm outside and fits with 0.23–0.52 mm to
    spare [calc w3 A, J].
- **c6 has no host that crimps at housing pitch.** In c6's preloaded housing the
  narrow conductor step misses by up to 0.2 mm beside open conductor barrels
  [ctq w2 §2].
  - i2's order, one contact per cycle crimped and pushed home before the next
    is loaded, is such a host. The only neighbour in the plane is a seated
    contact's round wire.
- **The snap holds the conductor through the stroke.** Once the jacket is in the
  bore, the throat resists lift at ~0.3–10 N and the bore grips along the wire
  at 0.2–4 N [ctq w2 §4].

## Picture it

**On the bench, left to right.**
1. **The pre-former**, c6's palm-sized steel station, away from any wire.
   - A kit contact sits box-first in a nest. The nest can be a kit XHP stub
     ([i2d](i2d-locator-the-lance-never-touches.md)'s cut housing) used only as
     a box pocket: box fit at product tolerance, lance never touched.
   - A Ø1.55–1.60 mm pin slides into the open insulation barrel from behind.
   - A jaw closes the wings around the pin to a keyhole: a 1.3–1.5 mm throat
     and 1.96–2.14 mm outside. That takes ~10–80 N [ctq w2 §3], from a servo
     lever or a POWERTEC 305CM push-pull toggle clamp.
   - The jaw is a **second cut of the same wire-EDM profile as the press's
     insulation step**, stopped where the arch meets the pin. So the final
     stroke starts on its own profile.
   - Out come contacts that cannot nest into each other: a box does not enter a
     1.3–1.5 mm throat [ctq w2 §5]. They are pushed nose to tail into a printed
     **stick**, a 2.1 × 2.6 mm channel with a lance groove. One housing's worth
     is 23–61 mm long. J2's stick carries a blank spacer at position 3.
2. **The press** is i2's:
   - a fist-sized steel C beside the row, throat ~30 mm facing the row;
   - a knee driven by a NEMA 17 on a Tr8×2 screw;
   - the stepped crimper: a 3.1 mm conductor step with ~0.8 mm walls, and an
     insulation step 2.5–2.7 mm wide whose mouth is ~2.2–2.4 mm. That is
     narrower than i2's ~2.3–2.6 mm, because a keyhole needs less, and the
     walls keep the difference;
   - an anvil with a lance relief, rising through a lance-grooved channel plate,
     long enough to sit under both barrels;
   - a 0.001 mm indicator across the dies and a load cell under the anvil.
3. **The carriage** on one X rail: the web clamp at the back, a saddle comb at
   2.5 mm in housing order, and the floating housing nest in front, located
   only in Y.

**One cycle, cavity n.**
1. **Contact in.**
   - An escapement finger takes the lead contact from the stick's mouth, one
     position upstream of the cavity. The stick never feeds the cavity
     directly: nose to tail, the next contact's box would sit against the lead
     contact's keyhole, inside the crimper's rear footprint.
   - A servo finger slides the contact lance-down along the channel plate,
     box-first, 1.4–2 mm into cavity n.
   - The anvil rises under both barrels, its front edge behind the hanging
     lance. The backstop bears on the tab stub for −Y.
2. **Tip set.** The camera measures where conductor n's stripped tip lies over
   the open conductor U. The hump presser corrects it: 1 mm on the hump moves
   the tip ~2 mm +Y [force-and-form §12].
3. **Snap.** The presser foot carries two tines.
   - The rear tine pushes the jacket down through the keyhole's throat into its
     bore: ~0.5–20 N, a few newtons at central values [ctq w2 §4]. The anvil's
     rear section takes the reaction.
   - The front tine lays the strands into the open conductor U.
   - The keyhole's rounded top is the lead-in in X (±0.3–0.5 mm), which the
     saddle comb meets.
4. **Look.** Before any crimp force exists, the camera checks the jacket in the
   bore, the insulation edge in the window, the strands in the U, and no strand
   over a wing tip.
5. **Foot up.** The conductor stays down: the throat holds against lift, and the
   conductor's own lift force is only 1–44 mN [ctq w3 §2]. The hump presser
   stays down (below).
6. **Crimp.** The knee straightens.
   - The insulation step's mouth meets a keyhole narrower than itself.
   - The conductor step's flare takes the conductor wings (1.43–2.15 mm wide
     open [source S19–S22]) and centres the conductor barrel.
   - The walls land on the anvil shoulders. The nest floats, and the steel is
     the master.
   - The press logs force against the true die gap.
7. **Height and proof.** The knee re-touches at ~10 N for crimp height. Pads grip
   conductor n behind the barrels and pull −Y to ~20 N against the backstop.
8. **Home.**
   - The hump presser lifts and the anvil drops 1.5 mm.
   - A slotted stencil-steel blade drives the contact in. The insertion trace
     shows the lance fold, the snap and the bottom.
   - A 5 N pull-back follows, then the carriage indexes. J2's cavity 3 is
     skipped.

## At a glance

| Stage | Located by |
|---|---|
| Pre-form | Box in the nest pocket; bore set by the pin, throat by the jaw profile |
| Contact at the press | Cavity walls (X, Z, roll), backstop on the tab stub (−Y), anvil (Z under both barrels) |
| Conductor | Saddle comb (X); camera plus hump presser (Y), held by the hump presser and then by the bore; throat (Z) |
| First touch and bottom | Steel: conductor flare, insulation mouth, anvil shoulders. The printed nest follows |
| Push | Cavity walls |

| | |
|---|---|
| **Reference for "fixed"** | The C-frame's anvil block for the crimp; the web clamp along the wire; the pre-former's nest and pin for the keyhole |
| **What drives the crimp** | The knee inside the C: 60–160 N at the knee, 0.8–2.6 kN at the dies [digest] |
| **What carries the crimp force** | The C. The carriage and nest carry none; the pre-former carries only 10–80 N of forming |
| **How it knows** | Pre-former silhouette (throat and outside width), with a Ø1.50 mm go pin that must enter the bore from behind; the camera after the snap; force against die gap; re-touch height; proof pull; insertion trace; pull-back |
| **Steps it covers** | Contact supply (sticks from the pre-former), place the contact (escapement into the cavity), place the conductor (the snap), hold, crimp, crimp height, proof pull, insert, latch check |
| **What it hands back** | Pre-forming at the lever in bulk (or a servo pre-former fed by the person or from strip); dropping sticks into the feed; splitting and stripping each ribbon end and laying it over the saddles in housing order (J4's and J7's crossings by hand, or by i2's loft picker); loading and unloading housings |

## Mechanism, references and tolerances

**The keyhole taken from the tool.** c6 leaves one problem open: a pre-formed
barrel meets the arch already closed, so an open mouth cannot centre it.
- Here the keyhole is cut from this crimper's own profile.
- The conductor step's flare centres the contact before the insulation step
  closes. The keyhole's top stands ~2.0 mm above the barrel floor's underside
  [estimate], against 1.50–1.60 mm for the conductor wings, and it lies inside
  a mouth 0.23–0.52 mm wider than itself. So it is not a competing locator
  until the arch closes on it.
- What stays unmeasured is what the jacket, already squeezed 6–9 % in the bore
  [ctq w2 §4], does under the rest of the stroke.

**The snap's load path.**
- The rear tine's 0.5–20 N goes into the anvil, never into the lance.
- The anvil's front edge is behind the lance tip, so t ≥ 0.34–0.74 mm or a
  lance slot ([i2](i2-crimp-in-the-cavity.md), calc w2 G).
- The insulation barrel is ~4.3–5.7 mm behind the contact's front [estimate],
  so the snap lands 1.7–3.5 mm behind the anvil's front edge [calc w3 J].

**Holding Y: a disagreement with the proposal, in part.**
- The proposal lets the hump presser lift after the snap, since the bore now
  grips.
- The bore grips 0.2–4 N [ctq w2 §4]. A released hump can push or pull along
  the wire with up to its elastic buckling load: 0.4–1.4 N pinned, 1.4–5.7 N
  clamped, over a 10–20 mm hump [calc w3 B]. At the low end of the grip the tip
  would still slide.
- So the hump presser stays down until the crimp is done, as in i2, and the
  snap is a second hold rather than the only one. The snap's own contribution
  is Z (the throat) and resistance to disturbance at first touch.

**The pre-former's nest can be a housing stub.** The only force against its
front wall is the friction of the 10–80 N forming load. So conductor-barrel
growth against a nose stop, the problem in
[i2d](i2d-locator-the-lance-never-touches.md), does not arise here.

**Supply.**
- 53 contacts a unit at 5–10 s each is 5–9 minutes at the lever while a print
  runs [c6 estimate].
- The sticks carry count and J2's blank; for identical contacts their order
  carries nothing else.

## Branches

### Two passes on pre-formed contacts (with [i2b](i2b-preload-the-whole-housing.md))

- **Pass 1: odd cavities.** Pre-formed contacts are loaded, snapped and crimped
  with empty neighbours.
- **Pass 2: even cavities, between crimped odds.**
  - **Loading.** Pre-formed contacts leave +0.43 to +0.52 mm to the crimped
    neighbours. Open clone wings leave −0.12 to +0.27 mm [calc w3 J].
  - **Crimping.** The insulation mouth has +0.08 to +0.37 mm to spare beside
    crimped barrels, where typical and wide clone wings are 0.05–0.48 mm short
    [calc w3 A].
  - The conductor step clears the crimped conductor barrels by ~0.2 mm a side
    [force-and-form on i2b].
- **A one-pass preload** of a whole pre-formed housing still does not crimp. The
  conductor step's half-width (1.55 mm) against an open conductor-barrel
  neighbour has 1.32–1.50 mm of room, up to 0.23 mm short [ctq w2 §2].

### On strip

- SXH strip indexes through an in-line pre-former on its pilot holes. The pin
  passes above the tab, which joins the barrel floor at the rear
  [assumption from the side-feed geometry, xh-facts §1].
- The strip then wraps over i2's crowned block to the cavity, and the tab is
  sheared at the bottom of the crimp stroke.
- No sticks, and orientation is never lost. A 100-piece strip covers ~1.9 units
  [digest].

### T4 spool runs (with change-the-question [c5](../../change-the-question/ideas/c5-ends-as-stock.md))

- T4 ends (4P into XHP-4: J3, J5, J9, J11, J13) are one layer and straight. So a
  fixed 1.7 → 2.5 mm saddle comb replaces the person's lay-in.
- A long run is 21 ends: 84 contacts and 21 XHP-4 [ctq w2 §7]. That is one
  100-piece strip through the in-line pre-former, and a 120–163 mm housing
  stick escaping into the floating nest: one visit per run.
- Missing: unattended split, strip and hump-forming of each spool end.

## Printed and bought parts

| Part | Source |
|---|---|
| Pre-former jaw | Second wire-EDM cut of the press's insulation-step profile; or c6's route, two jaws stoned from a 3 mm HSS blank (5-piece 3 × 3 × 200 mm, $9.99, Prime-confirmed [sourcing/amazon-prime.md]) |
| Mandrel pin, Ø1.55–1.60 mm | Gauge pin or drill blank. The Prime-confirmed Accusize set stops at 1.52 mm [sourcing/amazon-prime.md]; the larger pin is a sourcing request ([`../sourcing-requests.md`](../sourcing-requests.md), Wave 3) |
| Go pin, Ø1.50 mm | Accusize 50-piece plug pin gage set, 0.28–1.52 mm, $45.58, Prime-confirmed [sourcing/amazon-prime.md] |
| Pre-former drive (by hand) | POWERTEC 305CM push-pull toggle clamp, $18.25 a pair, 605 ratings, Prime-confirmed [sourcing/amazon-prime.md] |
| Pre-former nest | A cut kit XHP-2 stub, or stacked stencil steel ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil), from $3 [source]) |
| Sticks, escapement finger, two-tine presser foot | Printed PETG on the 0.2 mm nozzle; tine tips in stencil steel |
| Press, dies, carriage, drives, indicator, cells | As [i2](i2-crimp-in-the-cavity.md): Iverntech 42HD6039-05 NEMA 17 with Tr8×2 ($27.99), MGN9 rail ($16.12), Clockwise Tools DITR-0105 indicator ($52.99), ShangHJ 5 kg cells with HX711 ($9.99), all Prime-confirmed [sourcing/amazon-prime.md] |

## Contribution

- Derek's priority step at the housing's mouth, with the kit contacts on hand:
  - the contact is placed by the product's own cavity;
  - the conductor is placed by a light snap;
  - both are held by the snap and the cavity while a steel C crimps.
- It removes the insulation-mouth conflict of every narrow crimper at 2.5 mm
  pitch without pushing a neighbour, and turns the loose kit contacts into a
  stick supply that cannot tangle.
- The same pre-former serves i2b's two passes, strip, and T4 spool runs.

## Major unresolved problems

- **The insulation crimp over a pre-curl** on 1.7 mm silicone: sectioning and
  pull tests of pre-formed against open contacts crimped in the same dies.
- **The snap force band** (0.5–20 N) and the bore grip (0.2–4 N) on real kit
  contacts.
- **The press's dies:** 0.8 mm walls by quick-turn EDM at ±0.05 mm, and the
  insulation-step profile the pre-former copies.
- **The transition t** on kit contacts (the lance condition).
- **Crimping 0.2–0.4 mm from PA6.**
- **Whether the pre-form is needed for the mouth at all.** If the kit contacts'
  open wings are ≤ ~2.3 mm, the mouth swallows them as they come, and the
  pre-form is kept only for the snap. Derek's caliper settles it.

## What rests on assumptions

- Contact dimensions are clone drawings [source S19–S22]; the kit contacts are
  unmeasured.
- The snap and grip figures are order-of-magnitude estimates from silicone at
  Shore 50–70A [ctq w2 §4].
- The hump's elastic push is bounded by a buckling load with EI 14.5 N·mm²
  [calc w3 B].
- The strip's tab leaves the insulation barrel's rear open to a mandrel
  [assumption].
