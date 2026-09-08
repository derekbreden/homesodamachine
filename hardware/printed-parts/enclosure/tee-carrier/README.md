# Tee carrier

Two PET-GF halves joined by two M3 × 8 socket-head screws and two short M3 × 4 mm heat-set
inserts. Each half includes a closed service-tab handhold and a spring seat. Eight zip ties hold
Y-C, Y-D, Y-F and Y-G against the common web plane. A filled body in enclosure-front-top
surrounds their run arms, journals their branch collars and carries the spring pockets and
carrier bearings. The joined carrier couples their Y motion.

## The grasp

For insertion, each hand spans the cartridge pocket and the service tab on the same side.
The thumb pushes the cartridge aft while the fingers pull the tab fore: the two bearing faces
move toward that hand's midpoint. Both hands squeeze together to bottom the four tubes, then
relax so the springs settle the carrier at connected.

For removal, pull the cartridge against the enclosure. The fixed collet plate carries the
reaction into the whole box, which can be braced by a hand, foot, cupboard edge or its own
weight. The carrier follows the tubes forward until the fixed plate releases their collets.

The web thickens into a [16 mm](GRIP_BAR_T) front bar at each side. Each handhold has a closed
finger recess [22 mm](FINGER_RUN) fore/aft, [40 mm](FINGER_HEIGHT) high and
[11.855 mm](FINGER_DEPTH) deep, with [5 mm](GRIP_CORNER_R) corners and a
[3 mm](GRIP_EDGE_R) round at the mouth. The fingers
bear on the front bar's aft face, opposing the thumb on the cartridge pocket's aft wall.

The rim stands [3.15 mm](GRIP_PROJECTION) proud of the enclosure on each side; total width
across both grips is [221.3 mm](GRIP_WIDTH). Its outline has [5 mm](GRIP_RIM_CORNER_R) corners
and its exposed edge has a [1.5 mm](GRIP_RIM_EDGE_R) round. It overlaps every edge of its flank opening by
at least [4 mm](GRIP_OVERLAP) throughout the stroke. The recess ends on a continuous
[2.5 mm](GRIP_BACK_T) back, so the opening presents a finger pocket with no view into the
valves.

## Guidance and retention

The fixed body runs continuously between the tee wall and both enclosure flanks. Four
aft-opening cavities follow the tee bodies and their travel, with separate tie channels,
head recesses and flexible-tube passages. Broad flat lands above and below the moving web
continue into the flank guides. The upper center lap passes above the four tee bodies.

Each handhold is a rectangular sliding body behind its rounded exterior rim. The opening's
flat upper and lower faces guide its [42 mm](GUIDE_LENGTH) bearing length, with
[0.15 mm](GUIDE_AIR) running clearance on each side in Z. The opening's fore and aft faces
are the release and park stops. The body stays inside all four faces throughout travel.
The cup bottoms clear the enclosure's seam-rail heads. A short opening below each guide
passes the web during lateral insertion; the outer rim covers that opening throughout
travel. The upper lap passes through its own belt above the tees. The lower guide bears on either side of the web passage, and the closed
enclosure's rail head runs beneath the cup.

The two exterior rims face opposite enclosure flanks. Once the center lap is screwed
together, movement toward either side seats the far rim against its flank. The rims retain
X; the upper/lower guide faces retain Z. Their separated fore/aft contact regions and the
distance between the two handholds constrain pitch, yaw and roll. The rigid-body guide is
complete with the tees, ties and springs absent.

## Frame and motion

The source returns installed geometry: +Y aft, +Z up. The squeeze datum bottoms all four
cartridge tubes in their tee ports. Offsets come from the measured PP0208E insertion depths
in [`tee_connector.py`](/hardware/reference/tee-connector/tee_connector.py).

| State | Carrier Y offset | Contact |
|---|---:|---|
| Release | −3.15 mm | Fore stop; fixed plate depresses the collets |
| Squeeze | 0 mm | Opposed cartridge/tab grasp; tubes bottomed |
| Connected | +1.50 mm | Floating under spring load; tubes gripped |
| Park | +3.00 mm | Aft stop; empty carrier |

Only release and park are physical stops. The guide spans 6.15 mm. At park the web leaves
1.742 mm to the aft coils. The two spring axes lie between coils at X ±49.945, Z 190.245 mm.
Each spring bears in a 6.4 mm teardrop seat, 2 mm deep. Its fore end sits in a round bore
within the fixed body's full section. A vertical loading well behind each bore admits the
compressed spring; its floor and side walls surround the exposed coils. The return pair is
Lee LCM060C12M.

## Assembly

Work with `enclosure-front-top` loose and its pump bay empty.

1. Insert the four bare tees from aft into their cavities and branch journals, then move
   them fore to release. Fit the aft valves from the open underside, with their posts clear
   of the tray, and press each valve into its sockets.
2. Heat-set the two short M3 inserts into the right half from its fore-facing lap surface.
   Feed the right half inward from outside the right flank, web first, with its handhold
   against the opening's fore/release end. Seat its rim against the flank and move it aft
   to park.
3. Feed the left half inward through the left flank at connected, [1.5 mm](ENTRY_FROM_PARK)
   fore of park. Its upper lap passes over the seated tees. Move the left
   half fore to release. The parked right half leaves room for both motions.
4. Move the right half forward to release to close the central lap. Feed both M3 × 8 screws
   through the two access bores in the empty cartridge bay and tighten them into the right
   half's inserts. The heads finish flush with the lap's fore face. Check that both web faces share
   one tee-bearing plane and both tabs travel together.
5. Tie each tee twice through its routing channels. Move the carrier to park. Compress each
   spring above solid height, lower it into its loading well, enter its aft end into the carrier
   seat and let its fore end extend into the fixed bore. Check empty return and full travel.
   Complete the fore valve row, bowed stubs and hairpins as described in
   [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md).

Each tie crosses the web through two 1.5 × 3.5 mm slots, runs flush in the aft channel, then
closes around the tee arm on the fore side. Clock every head away from the machine center and
flush-cut its tail. No head stands behind the web. The center lap leaves all sixteen slots
and their routing channels open.

## Print and verification

Print both halves upright, +Z up, with the lower rim edge on the bed. The web begins
[4.15 mm](WEB_BED_GAP) above that edge and takes removable support beneath it. The cup floor,
pocket roof and rim overhangs also take support; the pocket opens directly onto the
side for cleanup. The fixed body's guide and tie-channel ceilings take support, removed
through the open aft cavities before assembly. Its spring bores open into the loading wells.
All guide and hand-contact faces retain their full bearing sections.

`build_half(side=-1|1)` makes one valid print; `build_carrier()` compounds both installed
halves. `interface()` supplies the enclosure's openings, stops, spring stations, installation
order and printed inventory. The generator exports `enclosure-tee-carrier-left` and
`enclosure-tee-carrier-right`, each as STEP, STL and viewer payload.

The part selftest checks solids, bed fit, lap contact, fastener stack, tie paths, closed pocket
backs, rim overlap and assembly clearance between halves. The appliance's `tee-carrier-motion`
reading checks tee loading, aft-valve entry, complete lateral insertion sweeps, lap closure, fore screw/driver
access, spring loading, finger space and working
travel against actual front-top, the closed lower enclosure, cartridge and fixed valve
bodies. Both end stops must engage on a
0.001 mm overshoot. At every state, a 0.151 mm transverse displacement and a one-degree
rotation in either sense about every axis must encounter the flank guides alone. These are
rigid-body contact readings. Spring clearance uses the maximum catalog outside diameter
through loading, seating and all four working states.

The [observed collet action](/hardware/reference/tee-connector/README.md#observed-push-connect-action)
establishes release under continuous restraint, locking after a short separating tug and
insertion against spring-level collet tension. The printed assembly's checks are equal tab
motion, positive capture, empty return to park and leak-free release/reconnection with all
eight flexible tube ends present. The spring loads in the enclosure facts are catalog
estimates; the assembly record holds any measured loads.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py`
