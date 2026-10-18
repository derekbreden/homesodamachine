# Pump-dock magnet columns

The dock uses twelve K&J SB443-IN stepped blocks: six in the lower pump
cartridge and six in the fixed bay wall. Two columns per half stand between
each pump's two fluid ports, at X−52.225 and X52.225 mm. Each column contains
three blocks centered about the tube row at Z186.174 mm.

The [geometry module](dock_retention.py) derives these stations from the four
actual port axes. Its local stocks, cavities, purchased-part models, cured
potting volumes and factory setting gauges share one interface definition.

## Mechanical interface

| Quantity | Nominal geometry |
| --- | ---: |
| Cartridge body aft plane | Y79.269 mm |
| Fixed bay-wall fore plane | Y79.515 mm |
| Body-plane separation away from bearing lands | 0.246 mm |
| Four integral fixed-wall bearing lands | 4.000 × 12.000 mm each |
| Bearing-land X centers | −100.000, 100.000 mm |
| Bearing-land Z centers | 223.925, 266.174 mm |
| Bearing-land fore / embedded aft planes | Y79.269 / Y82.515 mm |
| Bare magnet contact plane | Y81.269 mm |
| Moving magnet projection beyond cartridge body | 2.000 mm |
| Fixed magnet recess behind bay-wall face | 1.754 mm |
| Moving PET-GF guard projection | 1.850 mm |
| Guard-to-fixed-recess running clearance | 0.250 mm |
| Nominal magnet envelope | 6.350 × 6.350 × 4.7625 mm |
| Slot width | 6.650 mm |
| Rail depth from pole face | 1.950–2.550 mm |
| Rail tip distance from column centerline | 2.625 mm |
| Backing and side stock beyond internal potting keys | 3.000 mm |

The moving guard enters a matching recess in the fixed wall. The surrounding
cartridge and bay body planes retain their existing seating datums. Moving the
magnet contact plane into the fixed wall leaves the required backing within
the cartridge's accepted fitted stock. The local fixed-wall back pads extend
to Y89.3458 mm. Their width is 15.85 mm per column, clear of the two adjacent
receiver axes; receiver-keeper webs and assembly paths must also clear these
pads.

Four broad, integral PET-GF lands project across the body air at the retained
outboard lower-cradle edges. Their coplanar fore faces bear directly on its
aft face at Y79.269 mm. Each land embeds 3.000 mm into the continuous fixed
wall; two heights at both X edges establish the rigid seating plane and carry
seating moments. They lie outside the cap lanes and above the stem guards.
The [bounded native review](body-stop-native-review.json) binds their source,
actual contact areas, wall stock and extraction clearance.

Bare pole faces meet when the lower cradle reaches these four lands. The
separate pogo seats retain their
own [compression limits](../../../reference/yyfkgcp-pogo-4p/mounting-audit.md).
An installed magnet that prevents the body stops seating, or requires the
body stops to close farther to obtain contact, fails assembly acceptance.

## Supplier envelope and positive capture

The [manufacturer drawing](https://www.kjmagnetics.com/resources/pdfs/SB443-IN.pdf)
specifies ±0.004 inch general three-decimal tolerances. The front band and
groove height each have the larger explicit ±0.010 inch tolerance. Their
common permitted groove interval, measured from a pole face, is
1.8542–2.6924 mm. The 0.60 mm rail lies inside that interval, with 0.0958 mm
front and 0.1424 mm rear allowance before print error. The rail tips have
0.1104 mm clearance to the largest permitted groove neck. The cavity depth
uses the drawing's maximum 4.8768 mm thickness and 0.20 mm rear allowance.

The rails provide geometric capture, with room to load the whole drawing
envelope. **The cured keyed fill is part of the retention joint.** It fills
the clearance between each actual groove and its rail while the bare pole
is held on its final datum. The fill extends into 1.60 mm side undercuts
behind each rail. Its pull-out reaction therefore passes through the magnet
groove, cured fill, printed rail and key shoulders into the PET-GF body;
nickel-to-resin or PET-GF-to-resin adhesion is additional, not the sole axial
capture. The closed key cavities also restrain the cured fill in Z.

Use **3M Scotch-Weld DP420 Off-White**, mixed base:accelerator **2:1 by
volume**, with **24 hours at 23°C** before removing the final assembly
fixture or applying extraction load. The [3M product page](https://www.3m.com/3M/en_US/p/d/b5005321028/)
and [December 2025 technical data sheet](https://multimedia.3m.com/mws/media/2365939O/3m-scotch-weld-epoxy-adhesive-dp420-off-white.pdf)
identify the 20-minute working time and room-temperature cure. The magnets
use that room-temperature schedule. The data sheet's substrate tests do not
establish PET-GF-to-nickel adhesion or strength of these actual thick keys.
Bind cartridge lot, proportioning, surface preparation, cure time and
temperature to the physical qualification article. K&J's
[adhesive guidance](https://www.kjmagnetics.com/blog/sticky-business-how-to-glue-neodymium-magnets)
supports two-part epoxies, clean prepared surfaces and a holding fixture;
it also identifies the tendency of steel-filled products to migrate around
strong magnets. Keep all resin off the pole faces and out of the wet TPU
parts.

## Factory assembly

The parts print empty. Magnets enter after support removal; no magnet is
heated by the PET-GF printing process. The front-loading mouth above each
column admits a complete block along Y. Each block then lowers along Z onto
the rails. The nominal stack occupies Z176.649–195.699 mm; the loading mouth
and headroom accommodate the drawing's full three-block height stack.

1. Dry-fit the empty cartridge with its lower-cradle aft face seated against
   all four integral fixed-wall lands. Confirm the actual body gap away from
   the lands, unchanged pump seating and installed pogo compression. The retained
   connector coupon result does not establish full-frame compression.
2. Dry-load and mark all twelve magnets. Alternate the exposed poles down
   each column and use the attracting mirror on its mate. A completed pair
   must attract at every station before any resin is mixed.
3. Prepare the plated surfaces and keyed cavities to the selected epoxy's
   instructions. Place controlled material in both magnet grooves and the
   side keys; leave the front bands and mating faces clean. Use a removable
   dam around the loading mouth so excess material cannot enter the bay.
4. Set the fixed poles with the factory gauge. Verify the gauge's actual
   step, accounting for any release-film thickness. Printed nominal gauge
   dimensions do not establish its accuracy. Hold the poles and complete
   the specified cure before removing the gauge.
5. Match-set the moving poles against the cured fixed poles with the
   lower cradle fully seated against all four fixed-wall lands. Keep resin behind the front bands and
   protect the surrounding mating surfaces from squeeze-out; every pole
   face stays bare. This actual installed mate establishes the final pole
   position. A separate nominal moving gauge is an assembly aid, not a
   substitute for match-setting to the installed frame.
6. After the specified full cure, withdraw the cartridge straight, remove
   the dams, inspect all twelve faces and check each filled key for voids or
   movement. Seat the cartridge again and verify all six face contacts,
   body-stop seating and pogo compression. Inspect the visible loading
   mouths and confirm the cured fill closes each column's upward route.

The receiver keeper, magnet keys and fixed fluid connections remain assembled
during a customer's pump swap. None is a customer adjustment or consumable.

## Evidence and physical scope

The local native review covers both mating stocks and cutouts, the full
supplier size/common-groove envelope, front loading and downward installation,
factory-gauge clearance, guard insertion and nominal bare-face contact. The
moving stock behind its body plane lies entirely inside the retained
cartridge's fitted stock. Translating each nominal cured key by 0.01 mm along
either Y direction encounters printed material, establishing the intended
geometric capture rather than a friction-only pocket. The complete assembly
must still establish neighboring keeper and plumbing clearances.

The [product page](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet)
identifies N42 material, an 80°C maximum continuous service temperature and a
3.42 lbf pull rating to thick steel. That rating does not establish installed
six-pair force, an array force multiplier, pressure capacity or removal
effort. These properties belong to the installed assembly.

Physical qualification records the exact magnets, keyed-fill material/cure,
PET-GF print and full frame. It checks initial and repeated withdrawal force,
absence of key or rail movement, body-stop seating and pogo compression, then
the wet receiver's defined pressure and temperature cases. A passing CAD
check does not establish that the magnets overcome seal insertion friction,
retain the cartridge under hydraulic push-out or remain comfortable to
remove. The separate packing tape restrains the cartridge in transit.
