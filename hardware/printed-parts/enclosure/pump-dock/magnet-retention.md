# Pump-dock magnet columns

The dock uses sixteen K&J SB443-IN stepped blocks: eight in the lower pump
cartridge and eight in the fixed bay wall. Each pump's own load line carries
one column, midway between that pump's two fluid ports, at X−52.225 and
X52.225 mm. Each column holds four blocks centred on the tube row at
Z186.174 mm, with alternating poles down the column.

The [geometry module](dock_retention.py) derives these stations from the four
actual port axes. Its pockets, backing stock, purchased-part models and cured
bedding volumes share one interface definition.

## Mechanical interface

| Quantity | Nominal geometry |
| --- | ---: |
| Cartridge body aft plane | Y82.265 mm |
| Fixed bay-wall fore plane | Y82.515 mm |
| Body-plane separation away from bearing lands | 0.250 mm |
| Four integral fixed-wall bearing lands | 4.000 × 12.000 mm each |
| Bearing-land X centers | −100.000, 100.000 mm |
| Bearing-land Z centers | 223.925, 266.174 mm |
| Nominal magnet envelope | 6.350 × 6.350 × 4.7625 mm |
| Pocket, each column and part | 6.652 wide × 26.006 mm high |
| Fixed pocket depth, the drawing's thinnest block | 4.674 mm |
| Fixed pole proud of the wall face | 0–0.203 mm |
| Moving pocket depth behind the cartridge back | 5.080 mm |
| Moving pole proud of the cartridge back | 0.047–0.250 mm |
| Bedding behind each moving block | 0.250–0.656 mm |
| Bedding front, behind the pole face | 1.346 mm |
| Backing and side stock around each pocket | 3.000 mm |

Each pocket is one plain rectangular opening in solid stock, open only at
its part's mating face. A drawing-maximum block keeps 0.10 mm of air on each
side and at the ends of the four-block stack. The fixed pockets sit in local
back pads behind the 7 mm bay wall, 12.65 mm wide and reaching Y90.189 mm,
clear of the receiver keepers and their upward removal routes. The moving
pockets stand inside the cartridge's solid body behind its back face, with
4.3 mm of stock to the pump head well.

Four broad, integral PET-GF lands project across the body air at the retained
outboard lower-cradle edges. Their coplanar fore faces bear directly on its
aft face at Y82.265 mm. Each land embeds 3.000 mm into the continuous fixed
wall; two heights at both X edges establish the rigid seating plane and carry
seating moments. They lie outside the tube passages and above the magnet
columns. The [bounded native review](body-stop-native-review.json) binds their
source, actual contact areas, wall stock and extraction clearance.

Bare pole faces meet when the lower cradle reaches these four lands. The
separate pogo seats retain their
own [compression limits](../../../reference/yyfkgcp-pogo-4p/mounting-audit.md).
An installed magnet that prevents the body stops seating, or requires the
body stops to close farther to obtain contact, fails assembly acceptance.

## Supplier envelope and capture

The [manufacturer drawing](https://www.kjmagnetics.com/resources/pdfs/SB443-IN.pdf)
specifies 0.188 ± 0.004 inch thickness and ±0.004 inch general three-decimal
tolerances; the front band and groove height each carry ±0.010 inch. The
fixed pocket's depth is the drawing's minimum thickness, so every fixed
block pressed to its floor stands flush with the wall face or proud of it,
never recessed. The body air exceeds the proudest fixed pole. The moving
pocket leaves bedding room behind the thickest block when it meets the
proudest fixed pole.

**The cured bedding is the capture.** It fills each pocket from 1.346 mm
behind the pole faces to the floor, around every block and through both of
its side grooves. A block cannot leave the bedding without shearing it at the
groove's front wall. The bedding holds to the PET-GF pocket by adhesion and
by the printed layer lines it fills. Pulling one column straight off its
mate at contact asks about 0.2 MPa of mean stress over its bedded pocket
walls at the column's modelled 84 N; that bond is unqualified.

Use **3M Scotch-Weld DP420 Off-White**, mixed base:accelerator **2:1 by
volume**, with **24 hours at 23°C** before removing the final assembly
fixture or applying extraction load. The [3M product page](https://www.3m.com/3M/en_US/p/d/b5005321028/)
and [December 2025 technical data sheet](https://multimedia.3m.com/mws/media/2365939O/3m-scotch-weld-epoxy-adhesive-dp420-off-white.pdf)
identify the 20-minute working time and room-temperature cure. The data
sheet's substrate tests do not establish PET-GF-to-nickel adhesion or the
strength of these pockets. Bind cartridge lot, proportioning, surface
preparation, cure time and temperature to the physical qualification
article. K&J's [adhesive guidance](https://www.kjmagnetics.com/blog/sticky-business-how-to-glue-neodymium-magnets)
supports two-part epoxies, clean prepared surfaces and a holding fixture.
Keep all resin off the pole faces, the body air and the wet TPU parts.

## Retention on each pump's line

The [pressure review](pressure-retention-review.json) puts the reachable
single-channel blocked fill at 80 psi on one pump's two ports: 34.94 N on
that pump's column line, against a 1.5× screen of 52.40 N. The lands stand
well above the tube row, so a rigid cartridge loaded on one column tips about
the far column's outboard edge; the far column adds about 8 N to the loaded
column's 61 N. Each column therefore carries its own pump's case.

K&J rates one SB443-IN at 3.42 lbf to thick steel. Four in a column give
**60.85 N, 1.74× the blocked-fill load**, without counting the far column.
A surface-charge model of the actual alternating column (N42 at 1.30 T,
grooves included) gives 84 N at contact, 66 N with 0.25 mm between the poles
and 54 N at 0.50 mm. These figures explain the margin; neither is an
installed retention rating.

Straight withdrawal of the whole cartridge parts both columns at once: 122 N
at the steel rating and about 169 N in the model, plus the four wet seals.
Drawing one hand pocket first parts one column at a time.

## Factory assembly

Both parts print with their pockets empty. Magnets enter after support
removal; no magnet is heated by the PET-GF printing process.

1. Dry-fit the empty cartridge with its lower-cradle aft face seated against
   all four integral fixed-wall lands. Confirm the actual body gap away from
   the lands, unchanged pump seating and installed pogo compression. The retained
   connector coupon result does not establish full-frame compression.
2. Dry-load and mark all sixteen magnets. Alternate the exposed poles down
   each column and use the attracting mirror on its mate. A completed pair
   must attract at every station before any resin is mixed.
3. Prepare the plated surfaces and the four pockets to the epoxy's
   instructions. Bed each fixed pocket's floor and sides, then push each
   fixed block home to the floor, marked pole out, alternating down the
   column. Keep resin behind the front bands and off the wall face. Complete
   the specified cure.
4. Protect the wall face around each fixed column from squeeze-out, leaving
   every fixed pole bare. Bed the moving pockets and insert the moving blocks,
   attracting pole out. Seat the cartridge against all four lands: each
   moving block draws forward out of its bedding onto its fixed mate. Hold the
   cartridge seated through the full cure.
5. Withdraw the cartridge straight, inspect all sixteen faces and check each
   block for movement. Seat the cartridge again and verify all eight face
   contacts, body-stop seating and pogo compression.

The receiver keepers, magnet bedding and fixed fluid connections remain
assembled during a customer's pump swap. None is a customer adjustment or
consumable. The stub tips reach the wall-supported funnels 7.5 mm before
the cartridge seats, so the funnels guide the fluid axes before the poles
meet. The bare
magnet edges still require inspection for chipping and angled insertion in
the installed qualification article.

## Evidence and physical scope

The [product page](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet)
identifies N42 material, an 80°C maximum continuous service temperature and a
3.42 lbf pull rating to thick steel. That rating does not establish installed
eight-pair force, gap sensitivity, bedding strength or removal effort. These
properties belong to the installed assembly.

Physical qualification records the exact magnets, bedding material/cure,
PET-GF print and full frame. It checks initial and repeated withdrawal force,
absence of block or bedding movement, body-stop seating and pogo compression,
then the wet receiver's defined pressure and temperature cases. A passing CAD
check does not establish that the magnets overcome seal insertion friction,
retain the cartridge under hydraulic push-out or remain comfortable to
remove. The separate packing tape restrains the cartridge in transit.
