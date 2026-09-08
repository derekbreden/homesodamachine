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

Each closed cup joins the web through its back, roof and floor. Its fore and aft bars are each
[10 mm](GRIP_BAR_T) thick. The finger recess is centered in Y and Z within the visible
[42 mm](GUIDE_LENGTH) by [52 mm](GRIP_HEIGHT) flush face. The recess is [22 mm](FINGER_RUN) fore/aft, [40 mm](FINGER_HEIGHT) high and
[14.705 mm](FINGER_DEPTH) deep, with [5 mm](GRIP_CORNER_R) corners and a
[3 mm](GRIP_EDGE_R) round at the mouth. The fingers
bear on the front bar's aft face, opposing the thumb on the cartridge pocket's aft wall.

Both outer faces finish flush with the enclosure; total width across the grips is
[215 mm](GRIP_WIDTH). Each retaining rim sits behind the wall, with
[5 mm](GRIP_RIM_CORNER_R) outline corners. It overlaps the opening's fore, aft and upper
edges by at least [3 mm](GRIP_OVERLAP) throughout the stroke. Its lower edge clears the
enclosure seam rail. The recess ends on a continuous
[2.5 mm](GRIP_BACK_T) back, so the opening presents a finger pocket with no view into the
valves.

The outer grip faces carry the enclosure's inward-cut flute profile, aligned with its field
at the connected resting position. The grooves travel with the carrier. Their fade follows
the pocket mouth and the body's exposed edges; the rounded hand contact and internal
bearing surfaces retain their full sections.

## Guidance and retention

The fixed body runs continuously between the tee wall and both enclosure flanks. Four
continuous aft-opening wells each carry a tee, its ties, lower hairpin and upper valve
passage. The body has one common face behind the ties and spring ends, and a second full-width
face that clears the upper lap. The upper land is a continuous bridge into the fore valve
tray. The lower lands share a flat floor with the aft valve tray; four openings admit the
valves from underneath and carry the moving hairpins. Both guide sections join the flanks.

Each handhold is a rectangular sliding body with an internal retaining rim. The opening's
flat upper and lower faces guide its [42 mm](GUIDE_LENGTH) bearing length, with
[0.15 mm](GUIDE_AIR) running clearance on each side in Z. The opening's fore and aft faces
are the release and park stops. The body stays inside all four faces throughout travel.
The opening has one continuous lower edge at the web's insertion height. The handhold's
outer floor extends down to that edge along its complete length. Its inboard underside has
one continuous clearance over the enclosure's seam-rail head. The outer floor is 6 mm thick;
the floor over the rail is 2.295 mm thick. The upper lap passes above the tees.

One broad recess in each flank runs from the outer tee well to the aft valve tray's fore
plane. Its flat ceiling guides the rim and its outer wall forms the retaining shoulder.
The recess leaves room to lower the complete cup inside the enclosure and move it outward
into the opening.

The two internal rims face opposite wall shoulders. Once the center lap is screwed
together, movement toward either side seats that side's rim against its shoulder. The rims retain
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
within the fixed body's full section. Each bore has 9.712 mm of guidance and ends on the
body's common aft face. Compressed springs enter through the inner tee wells and cross
below the uninterrupted upper land. The return pair is
Lee LCM060C12M.

## Assembly

Work with `enclosure-front-top` loose and its pump bay empty.

1. Insert the four bare tees from aft into their cavities and branch journals, then move
   them fore to release. Both valve rows, Y-A/Y-B and the flexible links remain absent.
2. Heat-set the two short M3 inserts into the right half from its fore-facing lap surface.
   Feed the left half through the open rear above the valve supports, with its cup inboard
   of the flank and aligned with the outer tee well. Lower it behind the seated tees.
   Move it outward until the cup is behind the wall shoulder, then fore to the opening's
   release end. Push it outward into the opening until its face is flush with the enclosure.
3. Bring the right half through the same route on the right. While its cup is behind the
   wall shoulder, align it with the opening's aft/park end, then seat it outward. The left
   half stays at release while the right enters.
4. Move the right half forward to release to close the central lap. Feed both M3 × 8 screws
   through the two access bores in the empty cartridge bay and tighten them into the right
   half's inserts. The heads finish flush with the lap's fore face. Check that both web faces share
   one tee-bearing plane and both tabs travel together.
5. Fit the aft valves from the open underside with their posts clear of the tray, then
   press each valve into its sockets. The joined carrier and tees stay at release.
6. Tie each tee twice through its routing channels. Move the carrier to park. With fine bent-nose
   pliers, hold each spring compressed above solid height, its axis along Y. Lower it through
   the inner tee well on the same side, stopping above the bare tee's upper end. Move it
   outward below the upper guide to its spring axis, then down to the seat. Enter its aft end
   into the carrier seat and let its fore end extend into the fixed bore. Check empty return
   and full travel.
   Complete the fore valve row, bowed stubs and hairpins as described in
   [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md).

Each tie crosses the web through two 1.5 × 3.5 mm slots, runs flush in the aft channel, then
closes around the tee arm on the fore side. Clock every head away from the machine center and
flush-cut its tail. No head stands behind the web. The center lap leaves all sixteen slots
and their routing channels open.

## Print and verification

Print both halves upright, +Z up, with the web and outer cup floor on the bed. The internal
rim begins [3.705 mm](RIM_BED_GAP) above the bed; its extensions and the pocket roof take
removable support. The pocket opens directly onto the
side for cleanup. The fixed body's guide ceilings take support, removed
through the open aft cavities before assembly. Its spring bores open into the carrier recess.
All guide and hand-contact faces retain their full bearing sections.

The current production-profile readings are in
[`enclosure-tee-carrier-left.support-audit.json`](enclosure-tee-carrier-left.support-audit.json)
and [`enclosure-tee-carrier-right.support-audit.json`](enclosure-tee-carrier-right.support-audit.json).
Each half has three bed-rooted support bodies: one under the rim and seam-rail relief,
one under the central lap, and one under the finger-pocket roof. Their contact regions and
removal routes are named in the enclosure's [support ledger](../enclosure/support-audit.json).

`build_half(side=-1|1)` makes one valid print; `build_carrier()` compounds both installed
halves. `interface()` supplies the enclosure's openings, stops, spring stations, installation
order and printed inventory. The generator exports `enclosure-tee-carrier-left` and
`enclosure-tee-carrier-right`, each as STEP, STL and viewer payload.

The part selftest checks solids, bed fit, lap contact, fastener stack, tie paths, closed pocket
backs, rim overlap and assembly clearance between halves. The appliance's `tee-carrier-motion`
reading checks tee loading, complete rear-entry, lowering and outward-seating sweeps, aft-valve
entry beside the joined carrier, lap closure, fore screw/driver
access, spring loading, finger space and working
travel against actual front-top, the closed lower enclosure, cartridge and fixed valve
bodies. Both end stops must engage on a
0.001 mm overshoot. At every state, a 0.151 mm transverse displacement and a one-degree
rotation in either sense about every axis must encounter the flank guides alone. These are
rigid-body contact readings. Spring clearance uses the maximum catalog outside diameter
through loading, seating and all four working states. The reading also checks the complete
hardware wells for internal shelves and measures upper and lower web bearing at every state.

The [observed collet action](/hardware/reference/tee-connector/README.md#observed-push-connect-action)
establishes release under continuous restraint, locking after a short separating tug and
insertion against spring-level collet tension. The printed assembly's checks are equal tab
motion, positive capture, empty return to park and leak-free release/reconnection with all
eight flexible tube ends present. The spring loads in the enclosure facts are catalog
estimates; the assembly record holds any measured loads.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py`
