# Pump-dock magnet columns

The dock uses sixteen K&J SB443-IN stepped blocks: eight in the lower pump
cartridge and eight in front-top's receiver wall. Each pump's own load line
carries one column, midway between that pump's two fluid ports, at X−52.225
and X52.225 mm. Each column holds four blocks centred on the tube row at
Z186.174 mm, with alternating poles up the column.

The [geometry module](dock_retention.py) derives these stations from the four
actual port axes. Its pockets, purchased-part models and cured bedding volumes
share one interface definition.

## Pockets

| Quantity | Nominal geometry |
| --- | ---: |
| Cartridge aft plane | Y82.265 mm |
| Receiver wall bay face | Y82.515 mm |
| Frame gap between the two faces | 0.250 mm |
| Plane where nominal poles meet | Y82.390 mm |
| Pocket, each column and part | 6.850 wide × 4.788 mm deep |
| Pocket floor / eaves, below a 45° ridge rising 3.425 mm | Z173.021 / Z199.327 mm |
| Air at the pocket's sides and ends | 0.250 mm |
| Air at the pocket floor | 0.150 mm |
| Pole stand-out of a bottomed block, nominal | 0.125 mm |
| Pole stand-out over the drawing's ±0.004 in thickness | 0.023–0.227 mm |
| Bedding front, behind the pole face | 1.346 mm |

Each column is one plain pocket, open only at its part's mating face and roofed
by a 45° ridge standing on both side walls, so the part prints it without
support. Both pockets are cut into solid wall with at least 3 mm round them:
front-top's receiver wall between the keeper bays, and the cartridge's aft wall
between each pump's two tube passages. Every printed face of the pocket keeps
its printed-fit allowance from [fits.py](../../cadlib/fits.py): 0.25 mm running
air at the sides and ends, which a block slides past as it is pushed home, and
0.15 mm static air at the floor it seats on.

**The cured bedding is the capture.** It fills each pocket from 1.346 mm behind
the pole faces to the floor, around every block, through both of its side
grooves and into the ridge above the stack. A block cannot leave the bedding
without shearing it at the groove's front wall. The bedding holds to the PET-GF
pocket by adhesion and by the printed layer lines it fills; that bond is
unqualified.

## The seat

Each block is pushed home to its pocket floor, so its pole stands out of its
face by its own thickness less the pocket depth: 0.125 mm for a nominal block.
The stub tips reach the wall-supported funnels 7.5 mm before the cartridge
seats, so the funnels guide the fluid axes first. The bare poles then meet and
draw the cartridge onto them: the meeting poles are its seat, with 0.250 mm of
air between the PET-GF faces at nominal and the contact pair's 0.500 mm face
gap ([mounting audit](../../../reference/yyfkgcp-pogo-4p/mounting-audit.md)).
Over K&J's ±0.004 inch thickness the frame gap runs 0.05–0.45 mm, and every
contact pin stays engaged below 0.55 mm.

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

## Factory bonding

Both parts print with their pockets empty and without a pause; the blocks go in
after support removal.

1. Dry-load and mark all sixteen magnets: alternate the exposed poles up each
   column, front-top's bottom block north out and the cartridge's bottom block
   south out, so every facing pair attracts.
2. Prepare the plated surfaces and the four pockets to the epoxy's
   instructions. Use **3M Scotch-Weld DP420 Off-White**, mixed base:accelerator
   **2:1 by volume**.
3. Bed each pocket's floor and sides, then push each block home to the floor,
   marked pole out, alternating up the column. Keep resin behind the front
   bands and off the mating faces and pole faces.
4. Cure both parts together, faces up, for **24 hours at 23°C** before the
   cartridge is seated or loaded. No fixture or seated cartridge is needed.

The [3M product page](https://www.3m.com/3M/en_US/p/d/b5005321028/) and
[December 2025 technical data sheet](https://multimedia.3m.com/mws/media/2365939O/3m-scotch-weld-epoxy-adhesive-dp420-off-white.pdf)
identify the 20-minute working time and room-temperature cure. The data
sheet's substrate tests do not establish PET-GF-to-nickel adhesion or the
strength of these pockets. K&J's [adhesive guidance](https://www.kjmagnetics.com/blog/sticky-business-how-to-glue-neodymium-magnets)
supports two-part epoxies, clean prepared surfaces and holding the magnet while
it cures. Keep all resin off the pole faces, the frame gap and the wet TPU parts.

The receiver keepers and fixed fluid connections remain assembled during a
customer's pump swap; neither magnet column is a customer adjustment or
consumable. The bare magnet edges require inspection for chipping in the
installed qualification article.

## Evidence and physical scope

The [product page](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet)
identifies N42 material, an 80°C maximum continuous service temperature and a
3.42 lbf pull rating to thick steel. That rating does not establish installed
eight-pair force, gap sensitivity, bedding strength or removal effort. These
properties belong to the installed assembly.

Physical qualification records the exact magnets, bedding material and cure,
the PET-GF prints and the full frame. It checks initial and repeated withdrawal
force, absence of block or bedding movement, the meeting poles' seat and pogo
compression, then the wet receiver's defined pressure and temperature cases. A
passing CAD check does not establish that the magnets overcome seal insertion
friction, retain the cartridge under hydraulic push-out or remain comfortable
to remove. The separate packing tape restrains the cartridge in transit.
