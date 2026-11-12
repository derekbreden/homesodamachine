# Foam-fill test

Three clear pieces to pour foam into and film. They exist to correct the
[fill model](../../../tools/hsm/foam/README.md): its prediction for each piece is on
[homesodamachine.com/foam](https://homesodamachine.com/foam), and the pour shows where the
prediction is wrong. Each place in a piece stands for a place in the cold core's own pours,
named beside it on that page.

## The pieces

**Column.** One closed square tube on a foot. A weighed pour rises in it alone, so its
height over time is the foam itself: how much a gram becomes, and when. Every other reading
leans on this one.

**Comb.** An L with a pour well at its corner.

- Along one leg stand five cells of different gaps, each open at its foot to a duct along
  the floor that the well feeds. How high the foam stands in each, beside the well, says how
  much a narrow gap holds foam back.
- Along the other leg a stack of rooms opens off the well: one at the floor that liquid runs
  into, the same room higher up with and without a vent, a room whose ceiling is level with
  its mouth, a thin blind slot with and without a vent, a room behind one small hole, and a
  room whose floor lies below its mouth. They say where air is trapped and what a vent does.
- Past the rooms stand two cells closed at their feet. A channel runs from the top of the
  well over their mouths. They say whether foam that spills over a deep narrow cell fills it.

**Tray.** Half of the bottom cap's foam space, with two pour ports and one vent where the
cap has them. Its long walls stand for the cap's centreline and its outer wall. It says how
far foam runs sideways under a ceiling, and what the end without a vent does.

The outsides of the comb's two legs are its windows. The cells' gaps run back from one
window and the rooms' depth from the other, so each camera sees its leg's whole face.

## Printing

Translucent PETG on the 0.8 mm nozzle, thick layers, every wall two lines wide and no
infill: the walls are the windows. The column and the comb print as they stand. The tray
prints on its long edge, as its STL has it, so that its two broad faces are upright walls;
each round port has a peak for its roof in that position. Nothing needs support.

## Pouring

The page gives the grams and the timing each prediction assumes. Times count from the start
of mixing.

1. Note the room's temperature and the two liquids' temperature. Weigh each empty piece.
2. Stand the column and the comb in view of both cameras, one camera square to each leg of
   the comb, with a clock and a ruler in each frame. Start the clock as mixing starts.
3. Mix one batch. Pour the column's share into the column on the scale and note the grams.
   Pour the comb's share down the middle of the well without wetting its walls, and note
   the grams.
4. Lay the tray flat, ports up, on the scale, with a camera looking down on it. Mix a second
   batch and pour each port's share in turn, noting the grams after each.
5. Leave everything until the foam has set. Weigh each piece again.

## Reading

For each place the page names, read what it predicts: how high the foam stands from the
place's floor, how far down it reaches from the place's top, or how much of the place is
full. Photograph both windows of the comb, the column, and both faces of the tray against a
ruler. The footage gives the same readings over time.

Sawing the comb apart between cells and weighing each cell gives the foam's density by gap,
which the windows alone cannot.

## Sources

[`parts.rs`](parts.rs) holds every dimension, the three solids and the places they are read.
[`foam_fill.rs`](foam_fill.rs) writes the printable files and runs the model on each piece:

```sh
tools/run -- cargo build --release --locked -j2 --manifest-path tools/hsm/Cargo.toml -p hsm-foam
tools/run -- tools/hsm/target/release/foam-fill parts hardware/print-tests/foam-fill/parts
tools/run -- tools/hsm/target/release/foam-fill predict web/public/foam
```
