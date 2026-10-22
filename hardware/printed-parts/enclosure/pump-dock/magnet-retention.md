# Pump-dock magnet columns

The dock uses eight K&J SB443-IN stepped blocks in four attracting pairs: four
blocks in the lower pump cartridge and four in front-top. Each pump's own load
line carries one column, midway between that pump's two fluid ports, at X−52.225
and X52.225 mm. Each column holds two blocks centred on the tube row at
Z186.174 mm, with alternating poles up the column.

The [geometry module](dock_retention.py) derives these stations from the four
actual port axes. Its slots and purchased-part models share one interface
definition.

## Slot and rails

| Quantity | Nominal geometry |
| --- | ---: |
| Cartridge aft plane | Y82.265 mm |
| Collet plate bay face | Y82.515 mm |
| Frame gap between the two faces | 0.250 mm |
| Plane where the poles meet | Y82.390 mm |
| Pole proud of its face, block pulled onto its rails | 0.125 mm |
| Pole proud of its face, block pushed back onto its rails | 0.025 mm |
| Slot, each column and part | 6.550 wide × 4.989 mm deep |
| Slot floor / roof | Z179.824 / Z192.877 mm |
| Rails | 1.500 mm thick, 1.575–3.075 mm in from the face |
| Gap between the rail tips / rail tip to groove floor | 4.955 / 0.090 mm |
| Air over two nominal / drawing-maximum blocks | 0.353 / 0.150 mm |

Each column is one vertical slot, open at its part's mating face and cut into
solid stock. Front-top's opens in the collet plate's bay face and runs through
the 3.175 mm plate, which carries its rails, into a boss behind the plate; the
boss stands on the seam plane and keeps 3 mm of wall past the slot's floor,
sides and roof. The cartridge's is cut into its aft wall between each pump's two
tube passages, with at least 3 mm of wall around it. The slot's section is wide
at the face for the block's front band, narrowed by a printed rail standing in
each of the block's two side grooves, and wide again for the back band. The
rails hold the blocks in Y, the slot walls in X, and the slot's floor and the
layer printed over it in Z. Pulled toward its mate, a block bears its back band
on the rails' deeper faces; pushed, it bears its front band on their shallower
faces, 0.1 mm further in.

The 1.500 mm rail is a specific functional-section exception. Both parts print
with the column axis vertical. On each layer the rail projects only 0.797 mm
from the slot wall and joins that wall along its whole 1.500 mm depth; the
surrounding wall and root use local solid infill. The slice must show continuous
wall roads joining the rail into that parent stock throughout the column.
The rail's thickness, bead placement, short reach and connection to the wall
are assessed together. This exception applies to these groove-bearing rails.

The [native filament-path reading](printed-capture-native-review.json) binds the
cartridge and front-top STLs, projects and emitted G-code it names, whose slots
each take four blocks. On those jobs each of the four rails connects into its
parent wall on all 191 inspected cartridge layers and all 108 front-top layers,
and the [filament footprints](printed-capture-beads.png) show the perimeter
turning out from the wall around the rail tip and returning to the wall, with
the inner wall path and dense root fill alongside it. These deposited-path
observations are evidence for the rail construction on those recorded jobs. The
two-block slots and front-top's bosses have no native slice reading; physical
fit and retention keep their scope below.

The metal-insert fit retains 0.10 mm beside each block, 0.05 mm at each nominal
groove face and 0.09 mm at each rail tip, matching the umbilical exploration's
interface. The PET-GF frame faces retain their separate 0.25 mm running gap.
Drawing tolerances and physical fit retain the limits below.

## The seat

The pump tubes' tips enter the tees' branch collets 11.5 mm before the cartridge
seats. The poles then meet at Y82.390 mm and draw the cartridge onto them: the
meeting poles are its seat, with 0.250 mm of air between the PET-GF faces and
the contact pair's 0.500 mm face gap
([mounting audit](../../../reference/yyfkgcp-pogo-4p/mounting-audit.md)).
Pushed harder, each block moves 0.1 mm back onto its rails and the frame gap
closes to 0.050 mm; the broad aft face then stops the cartridge.

K&J's [drawing](https://www.kjmagnetics.com/resources/pdfs/SB443-IN.pdf) gives
±0.010 inch on the front band and on the groove height, so a block's pulled-out
pole can stand off nominal by a few tenths of a millimetre; the spread within a
lot is unmeasured. A pair standing proud holds the frame open by its excess: the
contact pair keeps every pin engaged while the frame gap stays under 0.55 mm. A
pair standing short leaves its poles apart by the shortfall while the PET-GF
faces seat. A block that does not slide freely down its rails at the pause is set
aside.

## Retention

In service the tees' branch collets grip the pump tubes and hold them against
pressure; a collet releases its tube only when the collet plate holds it in as
the cartridge is pulled. The magnets seat the cartridge; they do not carry the
blocked-fill load.

K&J rates one SB443-IN at 3.42 lbf, 15.21 N, to thick steel. On that rating a
column's two pairs come to 30.4 N, and straight removal of the whole cartridge,
which parts all four pairs, to 4 × 15.21 = 60.9 N, plus the four collet
releases, the O-ring drags and the upper tubes' and hairpins' spring. These figures are
arithmetic on the catalogue steel rating, not an installed rating.

## Loading at the print pause

Both parts print upright, each slot open at its top until the layer that
bridges over its Z192.877 mm roof. The preparer reads the native layers to place
each job's one pause, an `M400 U1`, before that closing layer's extrusion; the
closing layer's bottom must clear the drawing-maximum two-block stack, which
tops out 0.150 mm under the roof. Local support blockers extend 0.5 mm through
the slot roofs and keep support out of the loading slots.

1. Mark one spare block's north face, the face that draws a compass needle's
   south end, and keep it as the reference.
2. Front-top: drop two blocks down each of the two slots in the collet plate's
   bay face, grooves on the rails, the bottom block's north pole facing the bay
   and the top block's south (N, S from the bottom). The top block snaps flat
   onto the bottom one.
3. Cartridge: the same in the two slots in its flat back, the bottom block's
   south pole facing aft (S, N from the bottom).
4. Present the reference block's marked face to each column's bottom block:
   front-top's must repel it and the cartridge's must attract it. Resume; the
   next layer closes over the blocks.

No adhesive, cure or fixture is involved. The first layer over each slot spans
6.55 mm onto the blocks' top faces. The blocks then sit in the warm part for the
rest of the job; K&J rates N42 to 80°C continuous.

The tees, tee caps and fixed fluid connections remain assembled during a
customer's pump swap; neither magnet column is a customer adjustment or
consumable.

## Evidence and physical scope

The [product page](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet)
identifies N42 material, an 80°C maximum continuous service temperature and a
3.42 lbf pull rating to thick steel. That rating does not establish installed
four-pair force, gap sensitivity or removal effort. These properties belong to
the installed assembly, as does the printed rails' fit: the rail and slot
clearances are geometry, and neither these slots nor the umbilical's printed
rails have been printed.

Physical qualification records the exact blocks, the printed slots and the
full frame. It checks the pause loading, the blocks' capture after printing,
initial and repeated withdrawal force, the meeting poles' seat and pogo
compression, then the docked tees' defined pressure and temperature cases. A
passing CAD check does not establish that the magnets draw the cartridge onto its
seat against the O-ring drag and hold it there against the hairpins' spring, or that its removal is comfortable. The separate packing tape restrains the cartridge in transit.
