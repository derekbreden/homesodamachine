# i1b — Branch of i1: crimp in the row with narrow stepped dies, no lift

- **Branch of:** [i1](i1-lift-to-the-head.md).
- **Its dies** are [i2](i2-crimp-in-the-cavity.md)'s (K1, with force-and-form's
  f3 knee and f4 steel C), used one step further back from the housing.
- **Numbers:** [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt)
  [calc geometry §n], [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w3 X],
  force-and-form's [`on_into_the_housing.out.txt`](../../force-and-form/calc/on_into_the_housing.out.txt) [f&f §n].
- **Sketches:** i2's [`../sketches/i2-crimp-in-the-cavity.svg`](../sketches/i2-crimp-in-the-cavity.svg)
  for the dies and [`../sketches/insulation-mouth.svg`](../sketches/insulation-mouth.svg)
  for the mouth; both schematic.

**What it changes from i1.**
- i1 lifts each conductor 16–20 mm to an ordinary crimp head.
- i1b leaves the conductor in its row and brings a **purpose-made narrow head**
  to it: an anvil rising from below and a stepped crimper descending from above,
  narrow where they pass the neighbours.
- Feed is stored as a hump on a saddle, as in i2. The contact is crimped with
  its nose ~1 mm behind the housing's rear face, then pushed ~8.2 mm home
  [calc geometry §9].

## Picture it

- The same carriage as i1: housing in front, saddle comb, web clamp.
- A steel C beside the row, throat ~30 mm facing it, holds:
  - a **stepped crimper** coming down: a conductor step 3.1 mm wide with ~0.8 mm
    walls, and an insulation step 2.5–2.7 mm wide with a chamfered,
    polished neighbour-side face;
  - an **anvil** on a **knee** underneath (force-and-form's f3 knee turned upside
    down). Straightening the knee lifts the anvil and carries the load through
    straight links that cannot back-drive;
  - anvil shoulders below the floor, on which the crimper's walls land.
- A contact arrives on the anvil from below the row plane, on a short chute or
  carrier tape, lance down in a lance-grooved channel plate, with the anvil down.
  The anvil rises through the plate.
- **For cavity n:**
  1. The anvil rises with the open contact under conductor n's tip. Spreader
     fingers open the gap between the neighbour wires ~0.5 mm as the open wings
     (up to 3.0–3.25 mm on clones) pass up between them.
  2. The presser foot seats the conductor, and the camera checks the insulation
     edge. The hump presser stays down.
  3. The crimper comes down until its walls land on the anvil shoulders.
  4. Proof pull ~20 N against a backstop on the tab stub.
  5. The anvil drops. A gripper with its fingers above and below the wire,
     1.5–2.5 mm behind the insulation barrel, carries the contact +Y into cavity
     n, and a blade finishes the last 0–1.8 mm.
  6. Load-cell trace, 5 N pull-back, index.

## At a glance

| | |
|---|---|
| **What locates the contact** | The channel plate and anvil (lance groove, box on the anvil) as it rises; the steel dies at first touch and bottom; at insertion, the gripper then the cavity |
| **What locates the conductor** | Saddle comb (X), web clamp and hump presser (Y), presser foot (Z) |
| **Reference for "fixed"** | The C-frame: crimp height is the die pair's geometry, since the walls land on the anvil's own shoulders |
| **What drives the crimp** | A knee lifting the anvil, and the crimper's drive: 0.8–2.6 kN at the dies [digest] |
| **What carries the crimp force** | The steel C, closed around the wire band with its back beyond the housing's end |
| **How it knows** | Force against die gap; crimp height; the lay-in photo; the proof pull; the insertion trace; the pull-back |
| **Steps it covers** | Place the contact (anvil elevator), place the conductor, crimp, proof pull, insert, latch check |
| **What it hands back** | Splitting, stripping, laying over the saddles in order (crossings by hand); feeding contacts from below; loading and unloading housings |

## What it gains and costs

- **Gains.** No lift, and a short hand path (~10 mm). The contact never leaves
  the line of its own cavity, so X is right by construction.
- **Costs.** i2's custom dies, and 8.2 mm of stored feed per conductor against
  i2's ~5 mm (a hump of 5.5–7.7 mm over a 10–20 mm chord [calc geometry §9]).

## Problems met, and how it answers them [force-and-form on i1b]

1. **The rising anvil must lock rigidly and repeat to ±0.02 mm.** It does not
   need to repeat: the crimper's walls land on the anvil's own shoulders, so
   crimp height is the die pair's geometry, and the anvil's lift only carries
   the force. The knee does that.
2. **The anvil scoops an open contact from below.** It carries it lance down, so
   the contact rides on its lance unless the anvil's front edge is behind the
   lance tip or slotted under it (i2's lance condition, calc w2 G).
3. **A narrower punch with 0.3–0.4 mm walls cracks** under compaction's lateral
   pressure. The conductor step is 3.1 mm with ~0.8 mm walls [f&f §3]. At 1 mm
   behind the rear face the neighbour wires at ±2.5 mm are round, so the
   narrowest free width is 3.30 mm at their equator.
4. **Where the loop closes.** In a side-entry C around the wire band, the C's
   back beyond the housing's end.
5. **Contact feed below the row.** The open insulation wings pass a 3.3 mm gap
   between neighbour wires only if the wires are nudged aside. Spreader fingers
   open it ~0.5 mm while the anvil rises [estimate].
6. **The insulation mouth** [calc w3 A]. The insulation step's mouth (≤ ~2.3–2.6
   mm) is narrower than typical clone wings (2.80–3.25 mm). Here both
   neighbours are jackets, so the spreader fingers already hold them ~0.5 mm
   apart as the step comes down. That is more than the 0.33 mm shortfall of the
   widest clone wing, so the mouth swallows every clone spread while the fingers
   stay in. Pre-formed contacts ([k7](k7-pre-formed-contacts-crimped-in-the-cavity.md))
   also remove it.

## Major unresolved problems

- **Die making** (as i2).
- **The knee under a rising anvil** carrying 1–3 kN [context xh-facts §4] inside
  a small C.
- **Spreader fingers at 2.5 mm pitch** that stay in through the first touch of
  the insulation step.
- **The lance condition** t ≥ 0.34–0.74 mm.

## Contribution

The minimum-motion one-at-a-time machine: two pieces of steel, one knee, one
carriage, one gripper. Its difficulty sits in the 3.1 mm stepped dies and the
lance condition.

## What rests on assumptions

- Spreader fingers can hold ~0.5 mm without disturbing the seated neighbour's
  latch [estimate].
- Clone contact dimensions [source S19–S22].
