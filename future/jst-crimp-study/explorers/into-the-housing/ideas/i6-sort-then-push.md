# i6 — Sort, then push: crimped contacts wait in ribbon order, a carrier lowers each into its housing slot, the housing is pushed onto the row

- **Sketches:** [`../sketches/i6-sort-then-push.svg`](../sketches/i6-sort-then-push.svg) (schematic),
  [`../sketches/pin-map-layers.svg`](../sketches/pin-map-layers.svg) (J4 and J7 as layers).
- **Numbers:**
  - [`../calc/wave2.out.txt`](../calc/wave2.out.txt) sections A–D and I [calc w2 X];
  - [`../calc/wave3.out.txt`](../calc/wave3.out.txt) sections E and G [calc w3 X];
  - change-the-question's [`on_into_the_housing_w3.out.txt`](../../change-the-question/calc/on_into_the_housing_w3.out.txt) §9 [ctq w3 §9].
- **Coordinates** as in [`../handover.md`](../handover.md).
- **Related:**
  - branch: [i6b](i6b-post-bed-through-the-housing.md) (a post bed as the target);
  - combinations: [k6](k6-one-gantry-crimps-in-the-fan-then-sorts.md) (with
    force-and-form f4) and [k8](k8-half-rows-crimped-then-sorted.md) (with
    change-the-question c1c); terminal-supply develops a third,
    [x2](../../terminal-supply/ideas/x2-crown-then-sort.md) (its a2d crown
    station feeding this sort, with its a6 post head as the carrier);
  - the loft in [i2](i2-crimp-in-the-cavity.md) and
    [i4](i4-gantry-hand-with-eyes.md) uses the same placing rule.

## Picture it

**On the bench.**
- A flat base. At the back, the **web clamp** holds one ribbon end, or a pair
  laid edge to edge in one under-width channel. Just in front of it, a **root
  comb** keeps the split conductors in ribbon order.
- The conductors stick out forward from the root comb, straight, in one plane:
  the **staging plane**.
  - Their crimped contacts are at the tips, lance down, in ribbon order, at
    whatever pitch the crimp step left them (2.5 or 5 mm).
  - Copper strands hold that shape; a 10 mm cantilever sags 0.004 mm [digest,
    ribbon-as-pallet calc].
- **8–10 mm below** the staging plane, in front, is the **target row**:
  - a printed **target comb** of U-slots at 2.5 mm pitch, one per cavity plus
    spares, each 1.5–1.6 mm wide so the silicone grips a wire pressed into it.
    It can drop away on its own slide;
  - in front of it, the **housing nest** on a Y slide. A NEMA 17 on a T8 screw
    drives it through a bar load cell, as in [i3](i3-converging-shuttles-gang-push.md).
    A sprung guide comb rises under the contacts' noses.
- A **carrier** on a small X–Y–Z stage:
  - two fingers that close above and below a crimped contact's barrels: a flat
    pad under the floor, and a pad shaped to the crimp's two lobes on top;
  - a presser toe just behind them;
  - a load cell in Y.

  A camera looks down at the target row.
- A **backing blade**: stacked stencil-steel foil, slotted at 2.5 mm, that drops
  in behind every insulation barrel. Its tines are ≤ ~1.95 mm wide with a
  ~1.45 mm slot, so they follow into the cavity mouths as the housing arrives:
  a seated rear lies 0–1.8 mm inside the rear face [calc w3 H].
- A **finishing tine**: one slotted stencil-steel tine on the carrier's stage
  that can enter one cavity's rear by up to ~2 mm.

**One ribbon end (J7 as the example).**
1. **Read the map.** The software reads the loom's pin map and its ribbon order.
   - J7's web order is RB1, RB2, RB3, RB4, GND (5P), then CLO and CHI (3P; its
     third conductor is trimmed short at the split).
   - The target slots are pins 1, 2, 3, 4, 7, 5, 6. Everything except GND is
     already in order; GND rides over CLO and CHI to the end slot [calc w2 A].
2. **Lower layer first, centre outward.**
   - The carrier takes RB4's contact by its barrels and lowers it 8–10 mm to
     slot 4.
   - With its Y axis it sets the contact's rear 1.5 mm ahead of the comb face,
     and the toe presses the wire into the slot.
   - The camera checks roll and seat.
   - Then CLO, RB3, CHI, RB2, RB1 in turn.
3. **Upper layer last.** GND goes down to slot 7, passing over CLO and CHI,
   which already lie below. It lies on top of them where their paths cross.
4. **Square the row.** The backing blade drops behind all seven insulation
   barrels, straddling the wires, bearing on each contact's rear.
5. **Push to the first wall.**
   - The guide comb rises under the noses. The housing nest advances −Y onto
     the row: lead-ins take the noses, the guide comb is pressed away, and
     lances fold and snap.
   - The blade takes the reaction, and the load cell logs the sum.
   - The push stops when the first box bottoms, a wall in the trace. No
     conductor moves: the housing does.
6. **Finish each contact.**
   - The blade lifts and the target comb drops away.
   - The finishing tine visits each cavity and pushes that contact to its own
     wall, with a force ceiling, logging the rest of its fold, snap and wall.
   - Contacts that were already home show a wall at once.
7. **Check.** The carrier grips each wire behind the housing in turn and pulls
   back at 5 N: under ~0.2 mm of travel is a latch. If the nest carries a real
   header ([i5](i5-person-inserts-on-a-sensing-nest.md)), continuity per post
   names each cavity.
8. The person lifts the finished end out and labels it (J4 and J7 share a
   housing).

## At a glance

| | |
|---|---|
| **What locates each contact** | The carrier's fingers on the crimped barrels, from pick to slot; then the target slot (X) and the backing blade (Y); the guide comb and then the cavity lead-ins during the push |
| **Reference for "fixed"** | The base: web clamp, root comb, target comb and the nest's Y slide all bolt to it. The web clamp is the datum along the wire |
| **Crimp force** | None here. i6 is an insertion module. Its largest force is the housing push (4–9 × ≤ 9.8–25 N), carried by the nest drive and the backing blade |
| **How it knows** | A camera frame of every contact in its slot before the push (roll, seat, order); the push trace to the first wall; each contact's finishing trace; the per-contact pull-back; post continuity when the nest is a header |
| **Steps it covers** | Pin order, including J4's and J7's crossings, pairs and J2's empty cavity (software); roll and seat check at placement; insert (gang push, then per-cavity finish); latch check |
| **What it hands back** | Bringing the crimped ribbon end into the root comb in ribbon order (or it arrives from a crimp station such as [k6](k6-one-gantry-crimps-in-the-fan-then-sorts.md) or [k8](k8-half-rows-crimped-then-sorted.md)); loading a housing; lifting the finished end out; labelling J4 and J7. **No crossing, no pair and no skipped cavity is made by hand**: they are all target slots in the pin map |

## Why this arrangement exists

- Most insertion arrangements in the study hand J4's and J7's crossings back to
  the person: i1–i3 here, procedure-is-the-machine's p1–p3, change-the-question's
  c1, ribbon-as-pallet's a6.
- **A crossing is only an order of placement.** A conductor placed later lies
  over one placed earlier where their paths cross.
  - A machine that places conductors one at a time, from a plane where the
    waiting ones stay out of the way into a lower row where the placed ones
    lie, can make **any** pin map.
- Keeping the insertion itself as a gang push, with the housing moving onto a
  still row, keeps i3's property of storing no feed. Every contact is placed
  where it will finally sit relative to the web.
- Placing is also the one moment every contact is held by its barrels, in the
  open, with a camera on it. The handover's roll and straightness checks happen
  here.

## Mechanism, references and tolerances

**The pin maps as layers** [calc w2 A; sketch `pin-map-layers.svg`].
- The fewest layers a pin map needs is the longest run of conductors whose pins
  decrease in web order.
- **J1, J2 and the six single-ribbon looms are one layer.** J2's cavity 3 is an
  empty target slot, not a crossing.
- **J7 is two layers**: GND rides over CLO and CHI to pin 7. That holds for any
  5P order that keeps RB1–RB4 in order [assumption: the 5P's order follows the
  reed column]. In one plane it does not matter which 3P conductor is trimmed
  (2 crossings either way) [ctq w3 §9].
- **J4 is two layers** when the 4P is laid V5, IO25, 3V3, IO26 (both of its
  pairs still adjacent for the far-end peel) and the 3P GND, IO27, IO23, with
  the 4P on the left. Then 3V3 and GND ride over the rest to pins 1 and 2.
  - The 4P order 3V3, IO26, V5, IO25 makes J4 three layers. Both have 5
    crossings, the fewest with pairs adjacent. Splitting the 1-wire pair
    around the flow pair gives 3.
  - V5, IO25, 3V3, IO26 is also a least-crossing order for change-the-question's
    half-rows: 2 off-parity conductors and 2 crossings, by that family's own
    count [ctq w3 §9]. So one 4P order, fixed in `cable-assemblies.md`, suits
    every family. That is Derek's choice.
- In both J4 and J7 the upper layer lands **at an end of the housing**, beside
  the lower layer, never in a gap inside it.
- **If the board's pin order changes**, every ribbon becomes one layer. The
  orders are J4 = 3V3, IO26, V5, IO25, GND, IO27, IO23 (or V5, IO25, 3V3, IO26,
  GND, IO27, IO23) and J7 = RB1, RB2, RB3, RB4, GND, CLO, CHI [ctq w3 §9].
  - Then a fixed comb per loom places the whole unit, and i6's programmable
    order is needed only for rework and spares.
  - The J4 change costs routing work on the board: `pcba.tsx` routes IO25, IO26
    and IO27 so the present order lands uncrossed [repo]. It is Derek's choice.
  - J7 can be made straight without touching the board: GND moves onto the 3P
    with CLO and CHI, and the 5P's fifth conductor is the trimmed one
    (procedure-is-the-machine's rewire, a wiring choice for Derek).
- For i6 itself any placing order works; the layering only decides which
  conductors lie flat in the finished split. Arrangements with fixed levels
  (combs with a loft, shuttle rails) need as many levels as layers.

**Why the waiting conductors are never trapped** [calc w2 C].
- A placed conductor bends down from the root comb to the target row. A waiting
  one stays straight in the staging plane.
- Where their plan views cross, a fraction f of the way from the root, the
  placed one is f·h below. They clear by 0.3 mm when h ≥ 2.0 / f.
- Staged at 2.5 mm pitch, J4's tightest crossing is at f = 0.40 (h ≥ 4.9 mm),
  and J7 has none while the lower layer goes first.
- Staged at 5 mm pitch the order inside a layer matters. Placing from the
  housing's centre outward, the worst loom needs h ≥ 7.9 mm (J4); in web order
  J4 would need 10.8 mm and J1 7.9 mm.
- So the carrier places lower layer first, centre outward, and an 8–10 mm drop
  covers every loom at either pitch.

**Sideways travel and length** [calc w2 B].
- The largest sideways moves are 6.7 mm (J4's GND), 5.8 mm (J7's GND) and
  3.2 mm (J1's outer conductors), from web positions at 1.7 mm pitch to cavities
  at 2.5 mm, with the web centred on the housing.
- A conductor that moves 6.7 mm reaches 0.6–1.1 mm less far forward over a
  20–35 mm span.
- The carrier sets every contact's rear on one line, so conductors that moved
  less carry that length as a slight bow behind the comb: sag ≈ 0.43 ×
  √(largest travel² − own travel²), ~2.9 mm at most on J4, whatever the span.
- With the 8–10 mm drop the split is ~25–30 mm long during the build, and the
  finished loom keeps a set step of that height between web and housing
  [assumption: copper sets below ~67 mm radius, digest].

**Holding and pushing** [calc w2 D; calc w3 E, G].
- **The slot.** An under-width slot holds a placed contact where the carrier
  left it: 1.4–20 N axially for silicone of Shore 50–70A (E 2.5–5.5 MPa by
  Gent's relation [ctq w2 §4]; BNTECHGO states no hardness). That is enough to
  stay put. At the stiff end it approaches a clone insertion force, but it is
  not relied on to react one.
- **The backing blade** reacts the push.
  - 9.8–25 N per contact (the KONNRA clone spec's ≤ 9.8 N insertion [source,
    via ribbon-as-pallet]; 25 N a margin) on 0.16–0.38 mm² of tab stub or
    barrel edge is 26–156 MPa, below bronze's yield.
  - A tine 0.25–0.4 mm wide, stacked 1.0 mm deep and standing 1.5 mm proud,
    sees ~560–900 MPa at 25 N and ~220–350 MPa at 9.8 N; 304 half-hard
    stainless yields at ~1,000 MPa [calc w2 D, estimate].
  - The tines enter the cavity mouths by up to ~2 mm at the end of the push,
    since the housing's rear face passes the contacts' rears.
  - There is no free wire between the contact and the blade, so nothing
    buckles.
- **Length spread.** The blade sets every rear on one line, so the longest
  contact bottoms first.
  - Clone drawings run 5.8–6.73 mm, each ±0.25 [source S19–S22], and the spread
    within a lot is unknown. A 0.1–0.25 mm spread is about the size of a lance's
    catch travel [assumption].
  - Hence the push stops at the first wall and the finishing tine brings each
    contact to its own wall. The extra travel (≤ ~0.5 mm) comes out of the
    conductor's bow.
  - The target comb drops away first, so its slot grip is not added to the
    tine's push.
  - **Alternative:** the blade's tines ride on constant-force springs at
    1.25 × single insertion ([i3b](i3b-staggered-row-one-push.md)). Each
    contact then seats under its own force and rides back once bottomed: 49–75 N
    on the nest for XHP-4 and 110–169 N for XHP-9. Each ride-back stores
    0.1–0.5 mm as a 0.9–2.4 mm bow. Flat constant-force coils are wider than
    2.5 mm [assumption], so they stagger in 3–4 rows or act through push-wires.
- **The proof pull belongs upstream.**
  - The force ladder puts a ~20 N proof pull before insertion.
  - In i6 a grip behind the target comb is cramped on J4: its last crossing
    (V5 under GND) is at 73 % of the span, which leaves ~7–8 mm of uncrossed wire
    next to the comb on a 25–30 mm span [ctq w3 check of calc w2 B].
  - So the proof pull runs at the crimp station (k6's head, k8's pallet, a
    hand crimp in [i5](i5-person-inserts-on-a-sensing-nest.md)'s fork). i6's
    blade can still take a pull on straight looms if one is wanted.

**Roll between placing and pushing.** A contact cantilevered ~6.7 mm in front of
its slot keeps the roll its wire gives it. The camera checks it, and the guide
comb squares the noses in the last millimetres.

## Printed and bought parts

| Part | Source |
|---|---|
| Web clamp, root comb, target comb, housing nest, guide comb, carrier fingers | Printed PETG; combs on the 0.2 mm nozzle [repo: `tools.md`] |
| Carrier stage (X, Y, Z) | NEMA 17 steppers on T8 screws (Iverntech 42HD6039-05 with Tr8×2, $27.99) and MGN9 rails ($16.12), both Prime-confirmed [sourcing/amazon-prime.md] |
| Finger servo | Miuzei MG90S 4-pack, $13.88, Prime-confirmed [sourcing/amazon-prime.md] |
| Backing blade, finishing tine, finger tips | Laser-cut stainless stencil foil, stacked ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil), from $3 [source]) |
| Nest drive and cell | NEMA 17 on a T8 screw. A 5 kg bar cell with HX711 is Prime-confirmed (ShangHJ, $9.99 for 2 [sourcing/amazon-prime.md]) and suits the finishing tine; the gang push on XHP-9 (up to ~90–170 N) wants a 20 kg cell: Geekstory 20 kg with HX711, $8.98 [Prime], 64 ratings, bar form not stated on the page ([`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)). Adafruit #4541 lists 1/5/10/20 kg variants [source] |
| Camera | ELP 16MP on hand [repo: `tools.md`] |
| Controller | Klipper on a BTT SKR Pico ($35.99, 4 × TMC2209, Prime-confirmed [sourcing/amazon-prime.md]) or an ESP32; Python on the Mac sequencing moves and pictures |

## Problems met, and how it answers them

1. **The carrier drags the moving wire across its neighbours.** The carrier
   lifts only the contact end. Near the root the conductor pivots and barely
   moves. Placed neighbours are below; waiting ones are above [calc w2 C].
2. **Two ribbons in one clamp slip against each other.** In an under-width
   channel the pair registers as one row of 7–9 conductors [ribbon-as-pallet].
   A flush cut after clamping squares both ends. For the sort only the
   conductor-to-slot map matters, and the root comb holds it.
3. **Which conductor is which?** Ribbon order is known only if the ribbon's
   marked edge is known. The camera finds the marked edge if it is visible
   (Derek's question). Or the far-end electrode array (hand-tool-as-press's
   terminal block) names each conductor by continuity when the carrier touches
   its contact.
4. **A stuck contact in the gang push.** Slow push with a force ceiling, back
   off, look (as i3). The finishing tine then finds any contact short of its
   wall.
5. **The crimped end has to arrive in a staging plane.** It does if the crimp
   step leaves the conductors fanned in a comb, contacts cantilevered in front.
   - Sources: force-and-form f4's comb board ([k6](k6-one-gantry-crimps-in-the-fan-then-sorts.md)),
     f5's cassette, ribbon-as-pallet a2, hand-tool-as-press a3, i3's shuttles,
     change-the-question c1c's pallets ([k8](k8-half-rows-crimped-then-sorted.md)),
     terminal-supply a2d's crown station.
   - Hand crimps from today's SN-2549 are laid into the root comb by the person,
     in ribbon order, with no pin-order thinking.
6. **The bows spoil the finished loom.** Up to ~3 mm of sag on J4 and J7, and
   none on straight looms beyond J1's 1.4 mm. If it matters, the flush cut is
   stepped per loom so each conductor is cut to its own length (a recipe cut),
   or the bows are pressed flat after release.

## Contribution

- J4's and J7's crossings, the four two-ribbon housings and J2's empty cavity
  become entries in a pin map. Nothing about them is left to the person.
- The rule that makes it work: **wait high, place low, lower layers first,
  centre outward.** It transfers to every one-at-a-time arrangement (i2, i4)
  and to any comb with a loft.
- The pin-map calc: every loom is one layer except J4 and J7, each of which
  carries one or two conductors over the rest to an end of the housing; and
  the board orders that would make them one layer too.
- Zero stored feed at insertion, as in i3, with a programmable order instead of
  a fixed fan plate.

## Major unresolved problems

- **Gripping a 0.043 g crimped contact by its barrels** and letting go without
  it rolling. The crimp's lobed top is unmeasured. terminal-supply's
  [a6](../../terminal-supply/ideas/a6-post-is-the-gripper.md) post head is
  another grip: a pin spears the box from the front, and the pin's flats set
  roll.
- **Gang-push risks** carried over from i3: guide-comb timing and jam recovery.
- **The staging plane** depends on the crimp arrangement upstream.
- **Split length** of ~25–30 mm during the build, and the set step and bows it
  leaves.
- **Ribbon identity**: the marked edge, or an electrode array at the far end.

## What rests on assumptions

- Pin maps and ribbon assignments are the repo's today [repo: `pcba.tsx`,
  `cable-assemblies.md`]; J4's 4P order is a choice (above).
- Insertion force per contact ≤ 9.8 N is a clone spec; 25 N is a margin.
- Silicone at Shore 50–70A and friction 0.5–1.0 for the slot grip [estimate].
- Contact length spread within a lot [assumption].
