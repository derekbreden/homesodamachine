# Pump-dock magnet columns

The dock uses sixteen K&J SB443-IN stepped blocks: eight in the lower pump
cartridge and eight in front-top's receiver wall. Each pump's own load line
carries one column, midway between that pump's two fluid ports, at X−52.225
and X52.225 mm. Each column holds four blocks centred on the tube row at
Z186.174 mm, with alternating poles up the column.

The [geometry module](dock_retention.py) derives these stations from the four
actual port axes. Its slots and purchased-part models share one interface
definition.

## Slot and rails

| Quantity | Nominal geometry |
| --- | ---: |
| Cartridge aft plane | Y82.265 mm |
| Receiver wall bay face | Y82.515 mm |
| Frame gap between the two faces | 0.250 mm |
| Plane where the poles meet | Y82.390 mm |
| Pole proud of its face, block pulled onto its rails | 0.125 mm |
| Pole proud of its face, block pushed back onto its rails | 0.025 mm |
| Slot, each column and part | 6.550 wide × 4.989 mm deep |
| Slot floor / roof | Z173.474 / Z199.430 mm |
| Rails | 1.500 mm thick, 1.575–3.075 mm in from the face |
| Gap between the rail tips / rail tip to groove floor | 4.955 / 0.090 mm |
| Air over four nominal / drawing-maximum blocks | 0.556 / 0.150 mm |

Each column is one vertical slot, open at its part's mating face, cut into solid
wall: front-top's receiver wall between the keeper bays, and the cartridge's aft
wall between each pump's two tube passages, with at least 3 mm of wall around it.
Its section is wide at the face for the block's front band, narrowed by a printed
rail standing in each of the block's two side grooves, and wide again for the
back band. The rails hold the blocks in Y, the slot walls in X, and the slot's
floor and the layer printed over it in Z. Pulled toward its mate, a block bears
its back band on the rails' deeper faces; pushed, it bears its front band on
their shallower faces, 0.1 mm further in.

The 1.500 mm rail is a specific functional-section exception. Both parts print
with the column axis vertical. On each layer the rail projects only 0.797 mm
from the slot wall and joins that wall along its whole 1.500 mm depth; the
surrounding wall and root use local solid infill. The slice must show continuous
wall roads joining the rail into that parent stock throughout the column.
The rail's thickness, bead placement, short reach and connection to the wall
are assessed together. This exception applies to these groove-bearing rails.

The [native filament-path reading](printed-capture-native-review.json) binds the
current STLs, projects and emitted G-code. Each of the four rails connects into
its parent wall on all 191 inspected cartridge layers and all 108 front-top
layers. The [filament footprints](printed-capture-beads.png) show the perimeter
turning out from the wall around the rail tip and returning to the wall, with
the inner wall path and dense root fill alongside it. These are deposited-path
observations; physical fit and retention keep their scope below.

The metal-insert fit retains 0.10 mm beside each block, 0.05 mm at each nominal
groove face and 0.09 mm at each rail tip, matching the original umbilical
interface. The PET-GF frame faces retain their separate 0.25 mm running gap.
Drawing tolerances and physical fit retain the limits below.

## The seat

The stub tips reach the wall-supported funnels 7.5 mm before the cartridge seats,
so the funnels guide the fluid axes first. The poles then meet at Y82.390 mm and
draw the cartridge onto them: the meeting poles are its seat, with 0.250 mm of air
between the PET-GF faces and the contact pair's 0.500 mm face gap
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

## Retention on each pump's line

The [pressure review](pressure-retention-review.json) puts the reachable
single-channel blocked fill at 80 psi on one pump's two ports: 34.94 N on
that pump's column line, against a 1.5× screen of 52.40 N. A rigid cartridge
loaded on one column turns about the far column and the far edge of its aft
face; the far column's share is not credited, so each column carries its own
pump's case.

K&J rates one SB443-IN at 3.42 lbf to thick steel. Four in a column give
**60.85 N, 1.74× the blocked-fill load**. A surface-charge model of the actual
alternating column (N42 at 1.30 T, grooves included) gives 84 N at contact,
66 N with 0.25 mm between the poles and 54 N at 0.50 mm. These figures explain
the margin; neither is an installed retention rating.

Straight withdrawal of the whole cartridge parts both columns at once: 122 N
at the steel rating and about 169 N in the model, plus the four wet seals.
Drawing one hand pocket first parts one column at a time.

## Loading at the print pause

Both parts print upright, each slot open at its top until the layer that
bridges over its source-Z199.430 mm roof. The preparer reads the native layers
to place each job's one pause before that closing layer's extrusion. The
current [native reading](printed-capture-native-review.json) records cartridge
print Z34.360 mm and front-top Z39.320 mm, with 0.1946 and 0.1033 mm respectively
between the closing layer's bottom and the drawing-maximum stack. Both emitted
jobs have one `M400 U1` at that point. Local support blockers extend 0.5 mm
through the slot roofs, and the emitted support beads leave all four loading
slots clear.

1. Mark one spare block's north face, the face that draws a compass needle's
   south end, and keep it as the reference.
2. Front-top: drop four blocks down each of the two slots in the bay wall's
   face, grooves on the rails, the bottom block's north pole facing the bay,
   then alternating (N, S, N, S from the bottom). Each block snaps flat onto the
   one below.
3. Cartridge: the same in the two slots in its flat back, the bottom block's
   south pole facing aft (S, N, S, N from the bottom).
4. Present the reference block's marked face to each column's bottom block:
   front-top's must repel it and the cartridge's must attract it. Resume; the
   next layer closes over the blocks.

No adhesive, cure or fixture is involved. The first layer over each slot spans
6.55 mm onto the blocks' top faces. The blocks then sit in the warm part for the
rest of the job; K&J rates N42 to 80°C continuous.

The receiver keepers and fixed fluid connections remain assembled during a
customer's pump swap; neither magnet column is a customer adjustment or
consumable.

## Evidence and physical scope

The [product page](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet)
identifies N42 material, an 80°C maximum continuous service temperature and a
3.42 lbf pull rating to thick steel. That rating does not establish installed
eight-pair force, gap sensitivity or removal effort. These properties belong to
the installed assembly, as does the printed rails' fit: the rail and slot
clearances are geometry, and neither these slots nor the umbilical's printed
rails have been printed.

Physical qualification records the exact blocks, the printed slots and the
full frame. It checks the pause loading, the blocks' capture after printing,
initial and repeated withdrawal force, the meeting poles' seat and pogo
compression, then the wet receiver's defined pressure and temperature cases. A
passing CAD check does not establish that the magnets overcome seal insertion
friction, retain the cartridge under hydraulic push-out or remain comfortable
to remove. The separate packing tape restrains the cartridge in transit.
