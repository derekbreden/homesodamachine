# Installed G Ganen pump

The installed pump has its four complete rubber foot-and-leg assemblies removed.
Each assembly slides out of a fixed casing rail; the raised rail clip belongs to
that removable rubber part. The bare pump retains its casing, motor, fixed rails,
switch and measured barbs. The [purchased-foot reference](../common-foot/README.md)
describes the supplied sliders.

The pump installs at +90° about Z, with discharge toward enclosure −X. Its native
origin is **(−15.368269, 368.317761, 251.439035) mm**. The front of the
fixed lower casing bears directly on the plain lid at Z253.4. Production poses
and connected fitting frames belong to [above-core.json](../../../manifold-layout/above-core.json).

A **20 × 12 mm rear bearing land**, nominally **0.685486 mm** above the lid,
supports the lower casing while keeping the motor aligned. Two loops retain the
motor at native X9.5 and X67.5; **each loop uses two joined purchased 8-inch,
50 lb, 0.19-inch-wide nylon ties**, four ties total. The **5.6 × 1.6 mm** lanes
open along the lid's underside and end in through-slots outside the fixed rails.
The plate retains **3.8 mm** of roof above each lane. A conservative 1.6 mm
strap envelope clears the PSU by at least 0.75 mm across both complete bands. There are no pump-foot
screws, washers or internal cup columns.

Thread both joined loops through the empty lid before seating the pump. Keep both joined-loop
buckles beside the motor below its equator, clear of the PSU; flush-cut their
tails. Mask the grooves against the foam pour. During pump service, use each old
strap as a draw leader for its replacement before withdrawing it. Complete the cap-clamp screws before fitting the PCB. Fit the two clamped
PVC joints and discharge check while the core is open. Keep the suction elbow
and its short inlet link loose for the populated rear-shell approach, then seat
those round joints through the uncovered funnel opening.

The discharge group follows the pump datum. The suction PVC bend has a
13.125051 mm free span on two tangent arcs of at least R39.968 and unchanged
receiving lengths. Both water male fittings retain 0.4 mm of exposed shaft
outside their complete receiving depths. Its
connector rolls about its existing V-K stem axis; the opposed sockets retain
a straight 0.25 mm exposed stub. The
check outlet's two opposed bends retain at least **R14.923** and reach the straight water-in guide at
**(−82.5, 420, 253.4) mm**. The regulator, ASSE and large valves
retain their orthogonal placement.

`g_ganen_installation.build_parts()` and `rigid_shape()` expose the bare installed
reference. `mount_holes()` and `feet_shapes()` are empty. The stock slider
observations remain independently available in the purchased reference.
Occupied casing solids describe exterior clearance, not mass or wall thickness.
Actual strap retention, vibration and assembled fit remain physical qualification.
