# Tube bend holders

A free PET-GF sleeve that holds 1/4" LLDPE round the stock's tightest bend. `_routing.STOCKS`
puts that bend at a [14 mm](BEND_R) centreline radius, from the spool bench test, and every
1/4" LLDPE run in the enclosure turns at least one corner there
([tube routes](/web/public/tube-routes.json)). The tube reached that radius only wrapped
tightly round a dense cylinder. The holder is a body round the bend that keeps the tube from
flattening and kinking there. Nothing in the enclosure carries one.

## Section

A D on its back: flat on the plate, straight sides, a dome. Through it runs a teardrop channel,
a [Ø6.8 mm](CHANNEL_D) circle closed above by two 45° flanks that meet at a point. The holder
prints with nothing under its dome or under the channel's roof; a support inside a curved
tunnel could never come out.

The wall is the least material anywhere round the channel. The floor and sides stand off the
channel's circle by it, and the dome is centred [1.41 mm](DOME_LIFT) above the channel's centre
so the point has the same wall over it. A dome centred on the channel would leave
[0.59 mm](CENTRED_POINT_WALL_W2) over the 2 mm holder's point.

The channel is the umbilical organizer's [Ø6.65 mm](ORGANIZER_BORE) accepted straight sliding
bore for this tube ([fit record](/hardware/printed-parts/faucet/umbilical-organizer/physical-acceptance.json))
plus [0.15 mm](CHANNEL_EXTRA) for pushing the tube round the turn. The tube measures about
6.5 mm.

The section is swept a [90°](TURN) turn round the tube's centreline. Each end is square to the
tube, with a [0.5 mm](MOUTH) 45° lead-in. The holder is threaded onto the tube: the tube's end
goes in one mouth, round the turn and out the other.

| Wall | Width | Height | Footprint | PET-GF15 |
| --- | ---: | ---: | --- | ---: |
| 2 mm | [10.8 mm](WIDTH_W2) | [12.2 mm](HEIGHT_W2) | [R8.6–R19.4](BASE_W2) | [2.5 g](MASS_W2) |
| 3 mm | [12.8 mm](WIDTH_W3) | [14.2 mm](HEIGHT_W3) | [R7.6–R20.4](BASE_W3) | [3.9 g](MASS_W3) |
| 4 mm | [14.8 mm](WIDTH_W4) | [16.2 mm](HEIGHT_W4) | [R6.6–R21.4](BASE_W4) | [5.6 g](MASS_W4) |

The beads run along the tube when the holder lies on its back. The tube's push to flatten in
the turn acts across those beads and across the layers, which is the direction a thin wall
splits.

[`tube_bend_holder.py`](tube_bend_holder.py) writes `holder-w2`, `holder-w3` and `holder-w4`,
each as a STEP and the STL the slicer reads.

## Prints

- [2, 3 and 4 mm walls on Mark1](prints/2026-10-23-walls-234-petgf-left04-z018-mark1/README.md),
  task 1366393391.

## Sources
[value](NAME) texts are updated by:
- `/future/tube-bend-holder-exploration/tube_bend_holder.py`
