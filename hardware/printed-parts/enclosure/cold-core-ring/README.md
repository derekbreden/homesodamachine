# Cold-core support ring

The printed seat the cold core lands on at the back of the enclosure floor —
[`/hardware/assembly/enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md)
step 4, "the cold core lands on the printed support ring". One PETG part,
dropped in before the core, spanning the enclosure's Y seam.

## Why a part and not a floor feature

The enclosure floor is not one part under the cold core. The box's Y seam falls
at y = 223.3 in the pack's frame, inside the core's own 200–381 footprint, so a
rail cast into the floor prints in two pieces and the core's bearing plane
inherits the seam's Z tolerance and the shiplap's fit. Dropped in whole, the
bearing plane is one print, and the ring ties the two bottom pieces together
under the heaviest single mass in the cabinet.

## What it is for

The cold core's bottom foam cap is fastened to the outer shell by six M3 × 25
DIN 912 SHCS driven up from below
([`/hardware/printed-parts/cold-core/foam-shell/README.md`](/hardware/printed-parts/cold-core/foam-shell/README.md)
"Cap-to-outer-shell joinery"). The bottom foam-cap lid passes them on plain
clearance holes — no counterbore, and at 2 mm it has no room for one. So the
assembly's lowest surface is not its lid: it is six screw heads standing
[3 mm](HEAD_LEN) proud of it. Set straight on the floor, the core rests on those
six heads.

The ring is the plane they are missing:

- a closed **bearing rail**, [20 mm](RAIL_W) wide, its outer edge on the
  footprint edge — the line the bottom cap's own perimeter wall stands on.
  Everywhere inboard of that the lid is an unsupported plate over pour foam.
- six **head wells**, ⌀[11 mm](WELL_DIA) through the rail at the cap-screw
  stations, each opening outward as a notch where the boss sits nearer its edge
  than the bore's radius (every corner station does — the boss is tangent to the
  footprint's corner arc). A head hangs its full length in a well and still
  clears the enclosure floor by 2 mm.
- two front **lugs** standing to [13 mm](LUG_Z) at the footprint's front edge —
  the core's only fence that is not already in the box.
- two **ears** at seat height reaching into the enclosure's side bands, the
  ring's own fore-and-aft key.

## Geometry

| | |
|---|---|
| Footprint captured | [283](FOOTPRINT_X) × [181](FOOTPRINT_Y) mm, r12 corners — the foam shell's own outer shadow |
| Seat height (the lift) | [5 mm](SEAT_Z) |
| Lug height | [13 mm](LUG_Z) |
| Part envelope | [310 × 184 × 13 mm](RING_ENVELOPE) |
| Mass, solid PETG | [128 g](RING_MASS) |

Frame: +X right, +Y back, +Z up, origin at the footprint's front-left corner on
the enclosure floor. That is the same point the foam assembly's own origin lands
on, so the ring places at the core's (x, y) and the core places one
[5 mm](SEAT_Z) above it.

## How it is held, and how it holds the core

Nothing fastens the ring. Every axis is closed by geometry already in the box:

- **X, both the ring and the core.** The enclosure's Y-seam corner posts and
  Z-seam pin pods stand in the [14 mm](SIDE_BAND) side bands with their inboard
  faces on the footprint's own ±X edges, at three Y stations per wall. They are
  the X fence for both, which is why the ring is the footprint's shadow in X.
- **+Y, the core.** Its rear face already seats on the back Z-seam lip's inner
  face. There is no curb in the rear standoff band and there cannot be one: the
  box's rear wall is placed one standoff behind the *rearmost content*, so a curb
  standing in that band pushes the wall back off itself.
- **−Y, the core.** The two front lugs. They are discontinuous on purpose: the
  band ahead of the core at floor height is the machine corridor's aft mouth,
  where the evaporator stubs and the water-in line cross to the core's front
  face, and a wall the footprint's full width would stand in it. The lugs sit
  outboard of that traffic and clear of the corner wells.
- **±Y, the ring.** The two ears run the window the back column's Z-seam pin pods
  leave open in the side bands, with 4 mm of clearance at each end. The ring can
  travel that far and no further, which keeps its head wells over the screws.
- **−Z.** The enclosure floor, flat at z = 0 across the Y seam (the seam's floor
  overlap is a shiplap inside the slab, not a proud tongue).

## Printing

PETG, flat on the floor face, no supports — every feature is a vertical wall or
a vertical bore off the first layers. Brim recommended: the bearing rail is the
core's datum plane, and a 283 mm open frame is the shape most likely to lift a
corner.

## Open

- Bearing-plane flatness off a real print is unmeasured. If the frame will not
  lie flat, the answer is cross ribs at the mid-side screw stations, not a
  thicker rail.
- The M3 head's [3 mm](HEAD_LEN) is the DIN 912 nominal. It has not been measured
  on a seated screw with the TPU gasket under compression, and it is the number
  the seat height is built on.
- The ear window is written here as a pair of Y numbers, not read from the box
  that sets them: reading it live would make the ring's build depend on a pack
  that loads the ring. If the enclosure's Y seam or its back-column Z stations
  move, this part has to be told.
- The lift carries the whole water deck up with the foam-cap top, so every deck
  Z that is written as an absolute number rides `RING_SEAT` too. The appliance
  grows ~4 mm taller; no wall of the box moves.
- No [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §7 row yet.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/cold-core-ring/cold_core_ring.py`
