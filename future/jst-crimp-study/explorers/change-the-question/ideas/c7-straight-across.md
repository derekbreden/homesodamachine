# c7 — Straight across: change the pin map, the housing count or the ribbon width, so every XH end lies in ribbon order

A product change on the main board, or a wiring choice. Nothing about the
contact, the crimp or the machine changes; what changes is which conductor has
to land in which cavity. Sketch:
[`../sketches/c7-straight-across.svg`](../sketches/c7-straight-across.svg)
(schematic). Numbers: [`../calc/wave3.out.txt`](../calc/wave3.out.txt) §6
[w3b §6]; [`../calc/on_into_the_housing_w3.out.txt`](../calc/on_into_the_housing_w3.out.txt)
§9 [w3 §9]; [`../calc/order_search.out.txt`](../calc/order_search.out.txt).
Related: [c4](c4-parts-that-mate-the-wafer.md) (change the part),
[c5](c5-ends-as-stock.md) (ends as stock), and every arrangement that hands
J4's and J7's crossings back to the person.

## Picture it

**Today.** Eight of the ten housings take their ribbons in ribbon order: the
five 4P-into-XHP-4 looms, J6, J1 (5P and 4P laid edge to edge) and J2 (with
its trimmed conductor and empty cavity 3). Two do not:
- **J4 SENSORS.** The board's pins 1–7 are 3V3, GND, V5, IO25, IO26, IO27, IO23
  [repo `hardware/pcb/pcba/pcba.tsx`]. The 4P carries the 1-wire pair
  (3V3/IO26) and the flow pair (V5/IO25); the 3P carries the moisture pair
  (IO27/IO23) and the shared GND [repo `hardware/assembly/cable-assemblies.md`].
  Laid edge to edge, GND from the 3P has to reach pin 2 between 4P
  conductors and IO26 from the 4P has to reach pin 5: in one plane that is
  three layers and five crossings; in half-rows, two conductors in the wrong
  plane and two crossings [w3b §6; w3 §9].
- **J7 REEDS B.** Pins are RB1, RB2, RB3, RB4, CLO, CHI, GND. The 5P carries
  reservoir B's column (RB1–RB4) and GND; the 3P carries CLO, CHI and a third
  conductor that is trimmed [repo]. GND, on the 5P, has to cross CLO and CHI to
  reach pin 7: two crossings in one plane, one in half-rows.

Every machine in this study that lays a whole end at once (a comb, a pallet, a
housing preload, a sort) either hands those crossings back to the person or
grows a mechanism for them: c1's per-loom split jaw, a held-back presser tine,
into-the-housing's sort ([i6](../../into-the-housing/ideas/i6-sort-then-push.md))
and loft picker. into-the-housing's own count finds the sort and the loft there
chiefly because of J4 and J7 (its calc A, via
[`../../../exchange/change-the-question--on--into-the-housing-w3.md`](../../../exchange/change-the-question--on--into-the-housing-w3.md)).

**Four ways to make every end straight.**

**(a) Change two pin orders on the board.**
- **J4:** swap pins 2 and 5, so pins 1–7 read 3V3, IO26, V5, IO25, GND, IO27,
  IO23. The 4P lays into cavities 1–4 and the 3P (GND, IO27, IO23) into 5–7, in
  ribbon order.
- **J7:** move GND to pin 5, so pins read RB1, RB2, RB3, RB4, GND, CLO, CHI,
  and lay the 3P as CLO, CHI, then the trimmed conductor on the far edge.
- Both are then one layer with no crossing, and in half-rows every conductor
  is on its own parity plane with no crossing [w3b §6].
- The cost is a board revision. `pcba.tsx` routes IO25, IO26 and IO27 as three
  adjacent south-edge GPIOs dropping to J4, laid out so the present order lands
  uncrossed [repo pcba.tsx comments]. Swapping J4's pins 2 and 5 moves IO26 and
  GND; J7's change rotates GND, CLO and CHI among pins 5–7. How much routing
  that is has not been assessed here [assumption].

**(a′) No board change: choose which conductors ride which ribbon.**
- **J4 by pin block:** 4P = pins 1–4 (3V3, GND, V5, IO25), 3P = pins 5–7 (IO26,
  IO27, IO23). Straight in both counts [w3b §6]. What it costs is at the far
  end. The repo groups a ribbon's conductors by where they part, so each
  ribbon is peeled at one place ("a ribbon is peeled at one place rather than
  unpicked at three" [repo cable-assemblies.md]). By pin block, the 1-wire
  probes draw 3V3 and GND from the 4P and their data (IO26) from the 3P, and
  the moisture board draws GND from the 4P.
- **J7 with GND on the 3P** (procedure-is-the-machine's rewire, digest): 5P =
  RB1–RB4 and a trimmed fifth; 3P = CLO, CHI, GND. Straight in one plane. In
  half-rows the three 3P conductors land in the opposite plane from the default
  pattern after the trimmed one, which is a split-jaw pattern for that loom,
  not a crossing [w3b §6]. Reservoir B's reed common then reaches the board
  through the 3P's GND, joined where GND lands today (the 221-420 [repo]);
  whether that suits the 3P's path is Derek's to say.

**(b) One ribbon, one housing.** Split each two-ribbon housing into one
housing per ribbon, on two wafers:

| Loom | Today | Split | Housing row width (C = A + 4.8 [mfr S2]) |
|---|---|---|---|
| J1 | XHP-9 (5P + 4P) | XHP-5 + XHP-4 | 24.8 → 27.1 mm |
| J2 | XHP-6 (3P + 3P, cavity 3 empty) | XHP-2 (COM, FAN; the first 3P's third conductor trimmed) + XHP-3 (OUT3, OUT2, OUT1) | 17.3 → 17.1 mm |
| J4 | XHP-7 (4P + 3P) | XHP-4 + XHP-3 | 19.8 → 22.1 mm |
| J7 | XHP-7 (5P + 3P, one trimmed) | XHP-5 + XHP-2 (CLO, CHI; third trimmed) | 19.8 → 22.1 mm |

- About 7 mm more housing row, ~9–11 mm of board edge with the gaps between
  wafers [w3b §6, estimate].
- Every end is then one ribbon straight into its own housing: 4P into XHP-4
  becomes 7 of 14 ends and 28 of 53 crimps; the rest are 5P into XHP-5 (3),
  3P into XHP-3 (2) and 3P into XHP-2 with one conductor trimmed (2).
- There is no pair to feed edge to edge, so [c5](c5-ends-as-stock.md)'s spool
  runs cover every type.
- J2's empty guard cavity has nothing left to guard: a single ribbon filling
  its own housing cannot land one position off. The risk becomes plugging a
  housing into the wrong wafer.
- J4 and J7 stop sharing an XHP-7 (a swap there is a wiring fault today
  [repo]). More looms share housing sizes instead (seven XHP-4s, two XHP-3s,
  two XHP-2s), so labels, lengths and dress carry the identity, as they do for
  the five 4P looms today.

**(c) One loom, one ribbon.** Buy wider ribbon: 6P for J2, 7P for J4 and J7,
9P for J1 [assumption: whether 22 AWG silicone flat ribbon is sold at 6–10
conductors, and by whom, is unchecked; requested in
[`../sourcing-requests.md`](../sourcing-requests.md)]. Assign
conductor *i* to pin *i* and peel the ribbon into branches at the far end.
Every XH end is then one ribbon in pin order with no board change. The
crossing moves to the far end, which is made by hand anyway, where it becomes
peeling single conductors out of the ribbon instead of pairs (for J4, 3V3 at
position 1 and IO26 at position 5 leave as singles and travel together
unwebbed). The stocked ribbon widths grow from three to six.

**What locates, drives and carries force** stay with whichever arrangement
makes the ends. What c7 changes is that cavity order equals ribbon order, so a
fixed comb per housing size locates every conductor of an end at once, and the
person never routes a crossing.

**How it knows.** The same real-wafer test; with every end straight, "order"
means ribbon order, which the far-end electrode block or a slip ring reads
directly.

**What the person does.** Decides: a board revision (a, b), a wiring change in
`cable-assemblies.md` (a′), or new spools (c). After that, nothing at the
housing end that concerns crossings.

**Steps covered:** it removes the crossing step that every gang, pallet and
preload arrangement hands back for J4 and J7, and in (b) the pair feed.
**Hands back:** the board or wiring decision, and in (a′) and (c) extra
peeling at the far end.

## What question it changes

The five steps take the pin map as given. The pin map was drawn for the
board's routing, and it is the only reason two looms cross. Changing it,
once, removes a mechanism from every machine in the study.

## Problems worked through

1. **A board change for a wiring convenience.** It is a trade: routing work on
   one board revision against a crossing mechanism or a hand step on every J4
   and J7 end, about 120 program ends. (a′) avoids the board change at a far-end
   cost; (c) avoids both at the cost of new ribbon widths.
2. **(b) needs board edge.** ~9–11 mm more along the connector row, which the
   current layout may not have.
3. **(b) multiplies identical housings.** Seven XHP-4s instead of five.
   Labels and loom lengths already carry that burden for the 4P looms.
4. **(c) depends on a ribbon nobody here has sourced**, and on the web zipping
   cleanly into single conductors along a longer peel (repo Open item 5).

## Contribution

- It names the single cause of the study's crossing problem (two pin orders)
  and four ways to remove it, each with its cost.
- With (a) or (a′), every loom lies straight: one comb per housing size, no
  sort, no loft picker, no per-loom split jaw beyond J2's and J7's trims.
- With (b), every end is a single ribbon, which suits c5's spool runs and any
  first machine built for 4P into XHP-4.

## Major unresolved problems

- **Routing cost** of (a) and (b) on the board: not assessed.
- **Far-end cost** of (a′) and (c): extra peels at the sensors and reeds.
- **Board edge** for (b).
- **Availability** of 6P, 7P and 9P 22 AWG silicone ribbon for (c).
- **Whether the reed common** can ride J7's 3P in (a′).

## What rests on assumptions

- Board pin orders and ribbon contents as the repo states them today.
- Housing widths C = A + 4.8 [mfr S2] and a 0.5–1 mm gap between wafers
  [assumption].
- The wider ribbon's existence [assumption].
