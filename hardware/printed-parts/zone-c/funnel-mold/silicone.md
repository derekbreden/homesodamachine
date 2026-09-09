# The funnel's silicone

BBDINO 40A platinum-cure mold-making silicone, 2.42 lb kit
([B0FHHBGSQK](https://www.amazon.com/dp/B0FHHBGSQK)), cast in
[the funnel mold](README.md) to make the Zone C [funnel](../funnel/README.md). The figures
below are the maker's own, read from the product listing on **2026-09-09**; the mold's geometry
is [`funnel_mold.py`](funnel_mold.py)'s and is not repeated here.

## What the maker states

| | |
|---|---|
| Hardness | 40 ± 2 Shore A |
| Cure system | platinum (addition) |
| Mix ratio | 1A : 1B, **by weight or by volume** |
| Working time | **30 min** at 23 °C / 73 °F |
| Cure to demold | **5 h** at 23 °C / 73 °F |
| Full use | **24 h** after the pour |
| Temperature dependence | warmer shortens both the working time and the cure; cooler lengthens both |
| Degassing | **required** — this grade is not self-degassing; the maker names a vacuum chamber |
| Service temperature, cured | max 230 °C / 446 °F |
| Food contact | food-contact safe for **fat-free** food, skin-contact safe |
| Shelf life | > 12 months, sealed, below 30 °C, out of direct sunlight |

One cast is [about 135 mL](README.md) of mixed silicone including the sacrificial tip, ≈ 153 g
at ~1.13 g/mL, so a kit is about seven funnels. Pigment is BBDINO's own platinum-cure black at
≤ 2 % by weight.

## Two places the listing disagrees with itself

**Cure time.** The product title and its headline bullet say **3 h**. The four usage steps and
the maker's own comparison table both say **5 h**, and the same table gives 5 h for every other
grade in the range. Five hours is the figure to work to, and it is what
[`ledger/machine-time.md`](/hardware/ledger/machine-time.md) books.

**Self-degassing.** The title carries the words *Self Degassing*. The bullets say the opposite
in full — *"this 40A silicone rubber mold making will require degassing equipment during
using unlike the other mold making silicones from BBDINO"* — and the comparison table marks
this grade ✘ where the other grades are ✔. Degas it.

## What the maker does not state

**There is no post-cure schedule.** The listing gives no bake time and no bake temperature.
The project's own reason for baking is the food-contact gate — driving off the volatiles the
[wetted-surface screen](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md)
looks for — and that screen wants the coupon prepared the way production would be. So the bake
is the project's to establish, and the only maker figure bounding it is the cured material's
230 °C ceiling. Any schedule in this tree is a placeholder until that trial is run, and the
oven's own thermometer is what reads it rather than the dial.

Pot life, cure and the post-cure all belong to a batch and a room. Measure the first cast
rather than inheriting these numbers: the working time is stated at a stable 23 °C, and a warm
shop shortens it.
