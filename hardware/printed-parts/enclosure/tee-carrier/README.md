# Tee carrier

Two PET-GF halves joined by two M3 × 8 socket-head screws and two short M3 × 4 mm heat-set
inserts. Each half includes its service tab, guide ear and spring seat. Eight zip ties hold
Y-C, Y-D, Y-F and Y-G against the common web plane. The fixed tee wall journals their branch
collars in X and Z; the joined carrier couples their Y motion.

## The grasp

For insertion, each hand spans the cartridge pocket and the service tab on the same side.
The thumb pushes the cartridge aft while the fingers pull the tab fore: the two bearing faces
move toward that hand's midpoint. Both hands squeeze together to bottom the four tubes, then
relax so the springs settle the carrier at connected.

For removal, pull the cartridge against the enclosure. The fixed collet plate carries the
reaction into the whole box, which can be braced by a hand, foot, cupboard edge or its own
weight. The carrier follows the tubes forward until the fixed plate releases their collets.

Each tab's outer face is recessed 0.3 mm from the enclosure. Its finger-bearing pad stands
20 mm high, with 18 mm of finger space behind it throughout the stroke. The local flank
openings expose these bearing faces; their gabled roofs and the tabs' lower corbels stand at
45 degrees. The guide ears retain their complete stop faces inboard of the openings.

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
Each spring bears in a 6.4 mm teardrop seat, 2 mm deep, and surrounds the fixed wall's diamond
guide. The Lee LCM060C12M remains the dimensional bench candidate.

## Assembly

Work with `enclosure-front-top` loose, its aft valve row installed and the pump bay empty.

1. Heat-set the two short M3 inserts into the left half from its aft-facing lap surface.
2. Hold the right half at release, displaced 8.85 mm inward. Lower it through the cavity and
   slide it 8.85 mm outward so its integral tab enters the right flank opening. Move it aft
   to park.
3. Lower the left half at release with the same inward displacement, then slide it outward
   into its flank opening. The parked right half leaves room for this motion.
4. Move the right half forward to release to close the central lap. Feed both M3 × 8 screws
   from aft through the gap between the valve coils and tighten them into the left half's
   inserts. The heads finish flush with the web's aft face. Check that both web faces share
   one tee-bearing plane and both tabs travel together.
5. Fit both compression springs between their fixed pilots and recessed carrier seats while
   the bay is open. Insert the four tees through their journals and tie each tee twice.
   Complete the fore valve row, bowed stubs and hairpins as described in
   [`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md).

Each tie crosses the web through two 1.5 × 3.5 mm slots, runs flush in the aft channel, then
closes around the tee arm on the fore side. Clock every head away from the machine center and
flush-cut its tail. No head stands behind the web. The center lap leaves all sixteen slots
and their routing channels open.

## Print and verification

Print both halves upright on their web's lower edge, translated onto the bed. The integral
tabs grow from the web on 45-degree lower faces. The spring rails and center lap reach the
bed. Screw and insert passages open onto accessible faces for cleanup.

`build_half(side=-1|1)` makes one valid print; `build_carrier()` compounds both installed
halves. `interface()` supplies the enclosure's openings, stops, spring stations, installation
order and printed inventory. The generator exports `enclosure-tee-carrier-left` and
`enclosure-tee-carrier-right`, each as STEP, STL and viewer payload.

The part selftest checks solids, bed fit, lap contact, fastener stack, tie paths and assembly
clearance between halves. The appliance's `tee-carrier-motion` reading checks their descent,
outward entry, lap closure, screw/driver access, finger space and working travel against the
actual front-top and fixed valve bodies. Both end stops must engage on a 0.001 mm overshoot.

Physical qualification includes assembly access, comfortable paired squeezing, joint rigidity,
spring force, equal tab motion, empty return to park and leak-free release/reconnection cycles
with all eight flexible tube ends present. CAD clearance does not establish those outcomes.
