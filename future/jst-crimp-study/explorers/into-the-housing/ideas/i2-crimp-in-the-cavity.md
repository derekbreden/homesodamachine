# i2 — The housing is the locator: crimp the contact in its own cavity, then push it home (combination K1)

- **Sketches:** [`../sketches/i2-crimp-in-the-cavity.svg`](../sketches/i2-crimp-in-the-cavity.svg)
  and [`../sketches/insulation-mouth.svg`](../sketches/insulation-mouth.svg), both schematic.
- **Numbers:**
  - [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt) [calc geometry §n];
  - [`../calc/wave2.out.txt`](../calc/wave2.out.txt) [calc w2 X];
  - [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w3 X];
  - force-and-form's [`on_into_the_housing.out.txt`](../../force-and-form/calc/on_into_the_housing.out.txt) [f&f §n];
  - change-the-question's [`on_into_the_housing_w3.out.txt`](../../change-the-question/calc/on_into_the_housing_w3.out.txt) [ctq w3 §n].
- **Coordinates:** Y along the contact (+Y toward the mating face), X across the
  row, Z up with barrels open up and windows down ([`../handover.md`](../handover.md)).
- **What it combines.** i2's locator and push, inside force-and-form's closed
  steel C ([f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md)),
  with a knee ([f3](../../force-and-form/ideas/f3-knee-micropress.md)) and
  stepped dies that bottom on each other. force-and-form develops the same pair
  from their side as [f8](../../force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md).
- **Related ideas:**
  - branches: [i2b](i2b-preload-the-whole-housing.md) (load every cavity first),
    [i2c](i2c-cut-down-housing-locator.md) and
    [i2d](i2d-locator-the-lance-never-touches.md) (the locator moved to a cut
    housing);
  - combination: [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md) (the same
    press fed with pre-formed contacts from change-the-question's c6);
  - its dies also appear in [i1b](i1b-narrow-tooling-in-the-row.md) and in
    [k6](k6-one-gantry-crimps-in-the-fan-then-sorts.md)'s 2.5 mm variant.

## Picture it

**On the bench.**
- A fist-sized **steel C-frame** stands beside the row. Its back is beyond the
  housing's end in X and its ~30 mm throat faces the row (XHP-9 is 24.8 mm
  wide [mfr S2]). Inside the C:
  - a **knee** (toggle) drives the **stepped crimper** down. The knee is pushed
    by a NEMA 17 on a Tr8×2 lead screw, and its straight position lands the
    dies just touching;
  - the **anvil block** sits under the row on a small wedge with two positions,
    down for feeding and up for crimping;
  - a 0.001 mm indicator reads across the dies, and a load cell sits under the
    anvil.
- The crimper has two steps:
  - a **conductor step** 3.1 mm wide: a 1.5 mm channel with ~0.8 mm walls and
    a flared mouth;
  - an **insulation step** 2.5–2.7 mm wide. Its neighbour-side outer face
    carries a lead-in chamfer. A sprung **hold-down pad** rides in the middle
    of its channel, leading the walls by ~1 mm.
- In front of the C is a **carriage** on one X rail. It carries the ribbon
  clamp at the back and the **housing nest** at the front. The nest floats in X
  and Z on light springs and is located only in Y.
- The housing sits in the nest with its rear face toward the anvil, windows
  down, Circuit 1 to the left. The carriage steps 2.5 mm to bring each cavity
  onto the die axis.

**What the person does first.**
- Lays the split, stripped ribbon (or two ribbons edge to edge) in the clamp.
  Each conductor goes over its own printed **saddle** in a comb at housing
  pitch, in housing order.
- Each saddle's hump stores the ~5 mm the conductor travels when it is pushed
  home (the feed-length rule, [`../handover.md`](../handover.md)). The hump also
  holds the conductors not yet processed up, out of the working plane.
- Loads contacts: a printed carrier tape of loose kit contacts, or a strip.

**One cycle, cavity n.**
1. **Place the contact.** The anvil is down.
   - A fresh contact slides lance-down along a channel plate with a **lance
     groove** and goes box-first into cavity n's rear entry, about 1.4–2 mm deep.
   - The anvil rises through a slot in the plate, under the barrels.
   - The cavity walls hold the box in X, Z and roll. A **backstop** under the
     wire, bearing on the tab stub, holds −Y.
   - The lance still hangs free, just ahead of the anvil's front edge.
2. **Place the conductor.**
   - The camera looks down and measures where conductor n's stripped edge will
     land.
   - The **hump presser** pushes the hump down by that amount: 1 mm on the hump
     moves the tip ~2 mm +Y [f&f §12].
   - The **presser foot** lays the conductor into the open barrels, and the
     camera checks the insulation edge between them.
   - The presser foot lifts. **The hump presser stays down** until the crimp is
     finished, so the tip keeps its Y.
3. **Crimp.** The knee closes.
   - The hold-down pad meets the jacket first and keeps the conductor in the
     barrels.
   - The insulation step swallows the insulation wings. Its chamfered outer
     face moves the seated neighbour's jacket aside if the wings are wide
     (below).
   - The conductor step passes between the seated neighbour's wire and the
     empty side, and its walls land on **shoulders** of the anvil block, below
     the floor.
   - The steel dies centre the barrels, and the floating nest lets the housing
     follow.
   - The load cell records force against die gap.
4. **Measure and prove.**
   - The knee re-touches at ~10 N and the indicator reads crimp height.
   - Pads grip conductor n behind the barrels and pull −Y to ~20 N against the
     backstop: the **proof pull**, half of JST's 39.2 N minimum.
5. **Push home.**
   - The hump presser lifts and the anvil drops 1.5 mm.
   - A slotted stencil-steel blade comes down behind the insulation barrel,
     straddling the wire, and drives the contact +Y. The hump straightens as it
     goes.
   - A 5 kg bar cell in the pusher logs force against travel: a rise as the
     lance folds, a drop as it springs out, a wall as the box bottoms.
6. **Latch test.** The pads pull back at 5 N. Less than ~0.2 mm of travel means
   latched.
7. **Index.** The carriage steps to the next cavity. For J2 it skips cavity 3.

## At a glance

| | |
|---|---|
| **What locates the contact** | The product's own cavity walls (X, Z, roll); the backstop on the tab stub (−Y); the anvil (Z under the barrels). At first die touch and at the bottom, the steel dies (conductor flare, insulation mouth, anvil shoulders); the floating nest follows |
| **What locates the conductor** | The saddle comb (X); the web clamp plus the camera-driven hump presser (Y); the presser foot, then the hold-down pad (Z) |
| **Reference for "fixed"** | The C-frame's anvil block for the crimp; the web clamp for everything along the wire |
| **What drives the crimp** | A NEMA 17 on a Tr8×2 screw pushing a knee: 60–160 N at the knee, 0.8–2.6 kN at the dies [digest] |
| **What carries the crimp force** | The steel loop of crimper, knee, C and anvil. The carriage, nest and housing carry none of it |
| **How it knows it worked** | Force against true die gap; re-touched crimp height; a photo of bellmouth, brush and insulation before the push; the proof pull; the insertion trace (whose lance-fold rise proves the lance survived); the 5 N pull-back; post continuity if the nest is a real header ([i5](i5-person-inserts-on-a-sensing-nest.md)) |
| **Steps it covers** | Place the contact on its locator, place the conductor into the contact, hold both, crimp, measure crimp height, proof pull, insert, latch check |
| **What it hands back** | Splitting and stripping; laying conductors over the saddles in housing order (J4 and J7's crossings by hand, unless the loft picker below is built); loading contacts; loading and unloading housings |

## Why this arrangement exists

- **Derek's priority** is placing the contact on the conductor, holding both in
  something that crimps, and crimping [Derek]. The hard part is holding the
  contact still and square in a known place.
- No cheap tool has a locator [repo: `cable-assemblies.md`]. JST's WC-110 has
  one, at $537 [mfr S6, source S26].
- The XHP cavity is a molded locator at 2.5 mm pitch, shaped exactly to the
  box. It costs ~$0.05 a housing [source S26]. This arrangement uses it.
- The contact is never released between crimp and insertion, so the most
  dexterous step, finding the cavity with a floppy wire, never happens.
- The cavity is also the terminal guide an applicator has: it holds the box
  square while the barrels form, so the contact comes out straight [f&f
  transfer].

## Mechanism, references and tolerances

### The lance condition

This is decisive, and it belongs to the contact rather than to the housing
[calc w2 G].
- The lance hangs 0.6–0.9 mm below the floor, its tip 2.44 ±0.20 mm behind the
  contact's front [source S22].
- A flat anvil under the conductor barrel must have its front edge behind the
  lance tip (by ~0.1 mm) and ahead of the conductor barrel's front. Otherwise
  the contact rests on its lance and the crimp flattens it [f&f §1].
- That needs the box-to-barrel transition **t ≥ 0.34–0.74 mm**, whatever the
  box depth.
- If t is shorter, the anvil gets a **lance slot** under the centreline at its
  front. The front 0.1–0.3 mm of the conductor barrel floor then rests only on
  the slot's sides, which leaves a slight front flare on the barrel.
- The same inequality governs the iCrimp SN-2549. If its XH anvil is a plain
  block, today's hand crimps show t is long enough.
- Box depth is limited by the walls (≥ ~1.4 mm to hold square) and by the
  conductor barrel standing ≥ 0.2 mm clear of the rear face. With t ≥ 0.8 mm
  the window is 1.4–2.4 mm [f&f §1e].

### Room for the conductor step

[f&f §3; calc geometry §2]
- Only one side of cavity n has a wire in the plane: seated neighbour n−1.
  Conductor n+1 waits up on its saddle.
- The free width beside the working axis is narrowest at the neighbour's
  equator, Z ≈ 1.05 mm: 3.30 mm. Below Z ≈ 0.6 it is ≥ 3.56 mm, and below
  Z ≈ 0.2 it is 5 mm.
- The conductor step is 3.1 mm: a 1.5 mm channel with ~0.8 mm walls. Thinner
  walls crack under the lateral pressure of compaction: 0.3–0.4 mm walls reach
  2,200–9,450 MPa at a lateral-pressure ratio of 0.3–0.5, and 0.8 mm walls
  490–1,180 MPa [f&f §3].
- That leaves ~0.1 mm a side at the neighbour's equator, less than the
  cavity-to-die X offset (±0.14 mm RSS [f&f §2]). The floating nest takes up
  the offset. Without it, the punch does not fit.
- The walls land on anvil shoulders below the floor (Z < 0, where there is
  5 mm of room). Pinned at their lower ends at peak load, the walls' root
  moments fall by roughly 2–4 [estimate]. The surplus force is capped near
  1 kN (≤ ~450 MPa on the wall ends) [f&f §3] by the knee's straight position,
  a spring stack or a current limit.

### The insulation step's mouth

[calc w3 A; ctq w3 §1; sketch `insulation-mouth.svg`]
- **The condition.** The open insulation wings stand 2.75–3.20 mm tall, above
  the conductor wings (1.50–1.60 mm) [source S19–S22]. So the insulation step
  touches first, before the conductor flare has centred anything.
  - Its mouth must be wider than the wing spread plus a capture margin, and its
    wall needs a land at the mouth.
  - That outer width passes down beside the neighbour to the barrel floor.
  - A wing tip that lands on the wall's end face folds outward. The result is a
    flared insulation barrel that snags the cavity entry and holds the jacket
    on one side.
- **Beside a seated neighbour's jacket**, the half-width available is 1.65 mm.
  - Clone wings of 2.46 mm fit with +0.07 to +0.27 mm to spare.
  - 2.80 mm wings are +0.10 to −0.10 mm, 3.00 mm 0.00 to −0.20 mm, and
    3.25 mm −0.13 to −0.33 mm.
- **Three ways through**, which are not exclusive:
  1. **Push the neighbour's jacket aside.** The insulation step's
     neighbour-side outer face carries a lead-in chamfer and a polished face.
     - The seated neighbour's wire is held only at its crimped insulation
       barrel inside the cavity and at its saddle 10–20 mm back.
     - Moving it 0.10–0.33 mm sideways at contact n's insulation barrel costs
       0.05–1.9 N, less where the jacket simply indents [calc w3 A].
     - The line load, under ~0.7 N/mm, is far below silicone's 15–25 N/mm tear
       strength.
     - When the push is large and close to the housing, the neighbour's wire
       keeps a slight set 2–7 mm behind the rear face, bent away from the
       working cavity.
     - With 0.33 mm allowed, every clone spread up to 3.25 mm fits.
     - force-and-form's 0.1 mm shim-sheath branch covers the low end of the
       same idea. That the silicone tolerates a 0.33 mm push is **untested**.
  2. **Pre-form the insulation barrel** to a keyhole 1.96–2.14 mm wide before
     it reaches the press: [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md),
     with 0.23–0.52 mm to spare. The snap that comes with it also holds the
     conductor in place (below).
  3. **Narrow wings.** If the kit contacts' open insulation wings are ≤ ~2.3 mm
     (or genuine JST contacts sit near JST's 1.95 mm envelope [mfr S1]), the
     mouth swallows them as drawn. One caliper reading decides it.
- The insulation step works at 30–130 N [xh-facts §4], so its walls can be
  thin where they pass the neighbour.

### Holding the tip until the crimper arrives

[calc w3 B]
- The presser foot at the barrels has to leave before the crimper comes down,
  because they occupy the same space. What it held was Z. The conductor's
  elastic lift at the barrels is only 1–44 mN [ctq w3 §2], so it stays roughly
  in the U. The sprung hold-down pad in the insulation step's channel takes
  over Z a millimetre before the walls arrive.
- **Y is held by the hump presser**, which works 5–15 mm behind the dies,
  outside their footprint, so it stays down through the stroke.
  - Nothing recovers elastically, and the tip's Y is geometry: web clamp,
    pressed hump, tip.
  - If the hump presser lifted before the crimp, the hump's elastic share would
    pull the tip back with up to its buckling load: 0.4–5.7 N over a 10–20 mm
    hump. An open U holds nothing against that.
  - The change-the-question reading of this idea
    ([`../../../exchange/change-the-question--on--into-the-housing-w3.md`](../../../exchange/change-the-question--on--into-the-housing-w3.md))
    treats the correction as held only by copper set. Holding the hump presser
    down removes that dependence.
- In [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md) the snap holds Y
  and Z as well (bore grip 0.2–4 N, throat 0.3–10 N).

### Height, loop and push

- **Height.** The floating nest means no one trims the anvil top to each
  housing lot's cavity floor: the box drags the housing to the anvil.
- **The steel loop.** Crimper, knee, C-frame and anvil close around the wire
  band, with the C's back beyond the housing's end. The loop opens microns
  [f&f §4, force_loop].
- **The pusher's last millimetres.** A seated contact's rear lies 0–1.8 mm
  inside the rear face, depending on the contact's length
  (HDGC 5.8 ±0.25 mm to CJT 6.73 ±0.25 mm [source S19–S22]) and an assumed
  0.4–0.8 mm front wall [calc w3 H].
  - So the blade enters the cavity by up to ~2 mm at the end.
  - It is ≤ ~1.95 mm wide with a ~1.45 mm slot and 0.2–0.35 mm tines.
  - It is stacked laser-cut stainless stencil foil ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil),
    from $3 [source]) or a filed feeler-gauge leaf.
- **The force ladder** [f&f §7]: 5 N latch test < 14.7 N lance retention
  (analog; the KONNRA clone spec says ≥ 19.6 N) < 19.6 N proof pull < 39.2 N
  crimp pull-out.
  - A proof load that says anything about the crimp would pull a latched
    contact out of its cavity.
  - So the proof pull sits between the crimp and the push, never after it.

### Contact feed

- **Loose kit contacts** (the CQRobot contacts on hand [repo: `bom.md` §11]).
  - The person drops them into a printed carrier tape of pockets that fit only
    lance-down, box-forward.
  - A servo finger slides the front one along the lance-grooved channel plate
    into the entry.
- **Strip** (SXH-001T-P0.6, 100-piece strips at Digi-Key, $4.71 [source S26]).
  - The carrier joins at the rear of the insulation barrel, so the strip runs
    across the back of the anvil and the lead contact points straight at the
    cavity.
  - The strip wraps over a crowned block so the neighbour contacts drop
    3.6–4.0 mm below the housing: crown radius 6.3–12.5 mm for a 7–9.5 mm
    strip pitch, carrier strain 0.8–1.6 %, plastic and one-way [f&f §10].
    That pitch is xh-facts' range scaled from clone drawings, which are not to
    scale [xh-facts §1]. One 100-piece strip under a caliper fixes it.
  - The tab is sheared while the crimper still holds the barrels at the bottom
    of the stroke. Sheared after, its 50–160 N would pull the rear down with
    only the cavity walls holding the box.
  - **Branch: the housing goes to the strip.** The lead contact stays on a pilot
    pin, and the carriage moves the housing −Y ~2 mm onto its box. The strip
    then gives X, Y and roll. It needs a Y axis on the carriage.
- **Pre-formed contacts** in sticks: [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md).

### The die target

- The closed insulation barrel must fit the cavity: JST's end-view envelope is
  1.95 × 2.4 mm [mfr S1]. On 1.7 mm silicone a narrower insulation crimp grows
  taller ([`../handover.md`](../handover.md) item 3).
- Two references exist to copy:
  - today's SN-2549 crimps, which enter the housing;
  - JST's own factory crimp on the 22 AWG lead ASXHSXH22K305, $0.90 at
    Digi-Key [source, via change-the-question
    [c2](../../change-the-question/ideas/c2-buy-the-crimp.md)].
- The JST lead carries JST's closed insulation width and height, the tab stub
  the backstop bears on, and a genuine insertion trace for the pusher. Its
  wire is probably UL1007 PVC [assumption, via change-the-question], so its
  insulation height is for a different jacket.

### Crossings by machine

- i2 processes cavities in order. The person can lay J4's and J7's crossing
  conductors over a raised saddle groove.
- Or the conductors wait in a raised **loft** in ribbon order instead of on
  saddles in housing order. A picker with X travel takes the conductor for
  cavity k from its loft slot down to the saddle line.
  - Any order works when the waiting conductors are staged high: ≥ 4.9 mm for
    J4 ([i6](i6-sort-then-push.md), calc w2 C).
  - That turns J4 and J7 into software, at the cost of an X axis on the picker.
- If the board's pin order changes so that every ribbon runs straight across
  (J4 = 3V3, IO26, V5, IO25, GND, IO27, IO23; J7 = RB1–RB4, GND, CLO, CHI
  [ctq w3 §9]), the saddle comb is fixed per loom and no picker is needed.
  That is a board revision and Derek's choice.

## Printed and bought parts

| Part | Printed / bought | Evidence |
|---|---|---|
| Housing nest (floating), saddle comb, carrier tape, presser foot, hump presser | Printed PETG. Comb teeth at 2.5 mm pitch on the right-side 0.2 mm nozzle | 0.2 mm right-side hotends on hand [repo: `hardware/ledger/tools.md`] |
| Crimper (conductor and insulation steps) and anvil with shoulders | Hardened tool steel, by quick-turn wire EDM (JLCCNC states ±0.05 mm [source, via force-and-form]) | Die making is an open problem (below); force-and-form's [f7](../../force-and-form/ideas/f7-where-the-steel-comes-from.md) lays out the steel sources |
| Hold-down pad and its spring | Stencil-steel pad; a spring from the Dianrui 300-piece assortment | Prime-confirmed, $6.99 [sourcing/amazon-prime.md] |
| C-frame, knee links | Laser-cut steel plate (SendCutSend, mild steel to 12.7 mm, 2–4 days [source, via borrowed-machines]) | f4's head |
| Pusher blade, backstop, feed channel plate | Laser-cut stainless stencil foil, stacked | [JLCPCB stencil](https://jlcpcb.com/pcb-stencil): 304 stainless, from $3 [source] |
| Knee drive | Iverntech 42HD6039-05 NEMA 17 with integrated Tr8×2 screw and anti-backlash nut, $27.99 (~280–377 N at the screw, enough for a knee's 60–160 N [digest]) | Prime-confirmed, thin listing [sourcing/amazon-prime.md] |
| Carriage rail | MGN9 200 mm rail with MGN9H carriage, $16.12 | Prime-confirmed [sourcing/amazon-prime.md] |
| Presser and feed servos | Miuzei MG90S 4-pack, $13.88 | Prime-confirmed, 794 ratings [sourcing/amazon-prime.md] |
| Load cells + ADC | ShangHJ 5 kg bar cell with HX711, 2 sets, $9.99 (pusher); a button cell under the anvil | Prime-confirmed [sourcing/amazon-prime.md]; Adafruit #4541 $3.95 and #5974 $9.95 [source] |
| Die-gap indicator | Clockwise Tools DITR-0105, 0.001 mm, RS232 port, $52.99. Its DTCR-01 data cable had no Prime listing | Prime-confirmed [sourcing/amazon-prime.md]; the Mitutoyo ID-C SPC ($451–668 [source, via force-and-form]) is the other route |
| Reference crimp | JST ASXHSXH22K305 lead, $0.90 | Digi-Key, 26,279 in stock [source, via change-the-question c2] |

## Problems met, and how the arrangement answers them

1. **The lance sits where the anvil's front edge is** [f&f Break 1]. Answered
   by the lance condition: the anvil's front edge sits behind the lance tip, or
   it has a lance slot. Or the entry folds the lance when the box sits deeper.
2. **Two locators for one contact in X** [f&f Break 2].
   - The nest floats in X and Z, and steel is the master. The presser's few
     newtons drag a housing whose other resistance is the seated wires' bending
     stiffness (~3EI/L³ ≈ 0.005 N/mm each over 20 mm [calc geometry §1 EI])
     plus the nest springs.
   - Alternative: the camera measures each cavity's X at load and the carriage
     steps to it.
3. **A narrow punch fails at its walls** [f&f Break 3]. Answered by the 3.1 mm
   stepped crimper with walls bottoming on anvil shoulders.
4. **A set bottom through a screw** [f&f Break 4]. Answered by the knee in a
   steel C, die-on-die bottoming, and a re-touched crimp height every crimp.
5. **The saddle cannot correct the tip's Y** [f&f Break 5]. Answered by the
   camera-driven hump presser, held down through the stroke. Still uncertain:
   whether silicone slides in the saddle groove as the hump flattens.
6. **A contact slid along the anvil top rides on its lance** [f&f Break 6].
   Answered by feeding with the anvil down, along a lance-grooved channel
   plate, and raising the anvil through it.
7. **The box falls out of the entry before the crimp.** The backstop holds −Y,
   and the presser foot and then the hold-down pad hold it down once the wire
   is in. The backstop bears on the tab stub from under the wire; the crimped
   insulation barrel is too close to the wire's width (1.9 against 1.7 mm) to
   bear on from behind.
8. **Open insulation wings against the neighbour and the mouth.** Answered by
   the insulation-step section above: push-aside, pre-form, or narrow wings.
9. **J4 and J7 cross.** Laid by the person over a raised saddle groove, or
   taken from a raised loft by a picker, or removed by a board pin order.

## Contribution

- The product's own cavity as the contact locator, for the least money.
- No transfer between crimp and insertion: the contact is placed once and never
  let go.
- The feed-length problem at its minimum (~5 mm).
- The proof pull, crimp height and insertion trace of every contact, logged at
  one station.
- The insulation-mouth condition, which every narrow crimper at 2.5 mm pitch
  shares with it (i1b, i2b, k6, k7).

## Major unresolved problems

- **The lance condition.** Transition t and lance tip position on the kit
  contacts. One side photograph of a kit contact under the ELP camera settles
  it; so does a look at the SN-2549's anvil for a lance slot.
- **Die making.** A 3.1 mm stepped crimper with 0.8 mm walls around a 1.5 mm
  B-profile, landing on anvil shoulders, is custom tooling. Quick-turn EDM at
  ±0.05 mm is coarse for 0.8 mm walls around a 1.5 mm channel [f&f K1].
- **The insulation mouth against the kit's open wings.** Pushing the
  neighbour's jacket 0.33 mm aside is untested, and the kit's wing width is
  unmeasured.
- **~0.1 mm per side** at the neighbour's equator for the conductor step, with
  the floating nest doing the rest.
- **Crimping 0.2–0.4 mm from a PA6 face.** Any flash or bellmouth tooling that
  reaches forward marks the housing.
- **Clone against genuine.** The kit contacts' transition and lance may differ
  from JST's [context xh-facts §6].

## What rests on assumptions

- The lance condition rests on the CJT drawing's lance tip (2.44 ±0.20 mm) and
  an assumed 0.1 mm margin.
- Wall stresses rest on an assumed lateral-pressure ratio of 0.3–1.0 [f&f §3].
- The seated rear depth (0–1.8 mm) rests on an assumed front wall of
  0.4–0.8 mm.
- The push-aside forces rest on EI 14.5 N·mm² for the conductor and a beam
  held at the neighbour's barrel and saddle [calc w3 A].
- Latch sensing assumes a snap of ~0.1–0.3 mm with a measurable drop.
- The 5 N latch test rests on retention ≥ 14.7 N (Molex Mini-SPOX analog) or
  ≥ 19.6 N (KONNRA clone spec [source, via ribbon-as-pallet]).

**Measurements that settle it.**
- One kit contact side-on under the ELP camera: lance root, lance tip, box
  rear, conductor-barrel front.
- The kit contact's open insulation-wing width, by caliper, on three contacts.
- The SN-2549's XH anvil: a plain block, or a slot or step where the lance
  hangs?
- One contact pushed into one kit housing to 1.4–2 mm, photographed from the
  side.
- A flush-cut or Revopoint section of one housing: entry chamfer and floor.
- One JST ASXHSXH22K305 lead: closed insulation width and height by caliper.
