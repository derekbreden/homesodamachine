# G Ganen integration boundary

The standalone reference, measured interfaces and native comparison belong to
this folder. Production consumers and shared cap/Box sources are unchanged.
[The consumer map](../pump-comparison/g-ganen-integration.md) identifies their
owners. One agent should own the coupled assembly/cap/route edit after the
current tee correction releases that source lane.

## Placement

`hardware/manifold-layout/enclosure_assembly.py:build_seaflo` uses a positive
90° Z rotation, a rear-face rule and `z0=cap_face(foam)`. That `z0` reads the whole
native bounding box. It cannot directly stand in for this reference's average
bearing datum: the free rubber-foot envelope contains individually inclined and
bent faces below Z=0. Use an explicit bearing-datum translation and keep the
mounted rubber/contact qualification visible. Do not silently lift the ports
by the free-foot bounding-box minimum.

Use the **rigid motor rear** for the rear placement rule; moving a rubber slider
must not reposition the entire pump. Keep the intended rotation: local +X goes
toward enclosure +Y, and local +Y discharge goes toward enclosure −X. Resolve X
from the actual native tray/flavor-lane section clearances, as the current
placement already does. These are independent of the fitted Kamoer cartridge
seats.

`FOOT_T` currently has two roles in `build_seaflo`, `flavor_storey` and the fluid-14
route: clamp/pad stack and height of outboard pump obstruction. They are distinct
for this pump. Pad top observations are around 6.4–7.2 mm in the feet-down view;
the rubber upstands and fixed rails extend higher. Read the actual native bodies
in each neighboring height band rather than carrying SeaFlo's 8 mm scalar into
both uses. A room section with no intersecting pump body needs an explicit empty
case rather than a bounding box of an empty solid.

## Cap mount

Retain the purchased sliding rubber feet. Choose four actual slider positions
that clear the cap's pour/vent/conduit/boss stock, then carry each measured slot
and pad with its own fore/aft translation. A rectangle is a design option if the
chosen foot poses and slot engagement support it; the captured poses do not
impose one. The current `DeckMount(centre, pitch_x, pitch_y, ...)` and
`pump_mount_rows` only compare sorted center pairs. They need explicit selected
mount stations and checks for the complete screw path, pad/washer bearing and
upstand clearance. `mount_slots()` supplies per-foot observations; a compatibility
`mount_holes()` must refer to a separately chosen, qualified mounting pose.

The smallest remaining physical observation is a real M3 screw passing freely
through the full depth of each of the four slots, followed by the selected
washer seating flat without touching an upstand. The purchase ledger offers
M3 washer design candidates Ø7 × 0.5, Ø9 × 0.8 and Ø12 × 1.0 mm, but receipt and
seating are not established by the ledger. A removed-foot scan is unnecessary
for retaining the stock feet; it is needed only if a new hidden rail clip is to
be designed from that shape.

No native filled foot envelope qualifies screw passage or predicts rubber
compression. Final screw reach must include the actual mounted pad/washer stack,
lid crossing, insert length and bottoming clearance. Any intentional rubber
contact/deformation must be distinguished from rigid casing interference.

## Ports, routes and build order

Use each port's own axis, terminal tip and profile. `pan_front_y` currently reads
`PORT_D / 2`; it should read the placed discharge envelope in the direction
bounding the pan. `_tube_export` currently treats `PORT_L` as barb engagement;
this reference's approximately 13.2 mm exterior profile is not an observed hose
insertion/retention test. Do not silently make one common diameter/length from
the two measured profiles. Flow identity is already resolved by direct user
authority and the intended rigid rotation.

Resolve pump pose, selected foot poses and cap stations together; then derive
suction/discharge-chain anchors and check V-K and neighboring routes. Preserve
the independently fitted valve/Kamoer bearing geometry while updating actual
placement dependencies. Regenerate the cap and foam assembly, Box, affected
enclosure parts, combined assembly, tube cut schedule and BOM in that order.
Check pump/printed-cap contact, all rigid neighbors, hose lead/tangent/bend paths,
ASSE pan landing/withdrawal and flavor-port clearance against the same current
native bodies. The full enclosure print remains a separate release decision.

## Query cost

This is a detailed native reference, including shallow facets on measured convex
hulls. [native-query-cost.json](native-query-cost.json) records a native distance
and a room-section query, including current solid/face counts. The exact
reference should remain preserved if a faster integration shape is needed. A
separately named conservative envelope can be derived, with native containment
and maximum excess checked per component; unqualified smoothing or scale changes
must not alter the measured inputs or remove lug/port/rail constraints.
