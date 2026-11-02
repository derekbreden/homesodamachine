# Installed G Ganen pump

The installed pump has its four complete rubber foot-and-leg assemblies removed.
Each assembly slides out of a fixed casing rail; the raised rail clip belongs to
that removable rubber part. The bare pump retains its casing, motor, fixed rails,
switch and measured barbs. The [purchased-foot reference](../common-foot/README.md)
describes the supplied sliders.

The pump installs at +90° about Z, with discharge toward enclosure −X. Its native
origin is **(−15.181430, 368.068050, 247.947963) mm**. The molded cable cover
projects 1 mm farther down at its front than its rear. Its first modeled station
is at Z251.174013, retaining 0.274013 mm of air above the recessed lid floor at
Z250.9. The forward head tip sits higher.
Production poses
and connected fitting frames belong to [above-core.json](../../../manifold-layout/above-core.json).

The lid-integrated half pipe supports the motor over native X16.75–77.75. Its
continuous 54.5 mm upper clip spans X20–74.5. It is a filled box half-pipe with a
6.2 mm crown, one straight east clearance shoulder, 2.6 mm spring leaves and
2.6 mm flat hook engagement. The upper motor bore clears the largest retained upper
barrel high spot with the shared 0.15 mm per-face static allowance. The lower
seat gives the admitted barrel 0.25 mm running clearance. Open rooms admit the complete fixed rails and molded wire cover
vertically. The straight cover room is recessed 2.5 mm into the lid, leaving a
4.9 mm floor; two fitted lower
planes support each rail without entering its groove. Broad stock flush with the
saddle’s outside wall joins both fixed rails' end stops. The straight
rail channel remains open. The 9.329 mm stop stock has 7.1 mm of continuous
backing outside that channel. The fore stock ends below the head lug; rear
stock meets the saddle top. Both lead exits remain open.
Primary saddle and snap contact stays within the measured motor band. The
stop faces meet only the fixed rail ends; the rough head underside stays
clear throughout axial free play.

The continuous side pockets span X19.75–74.75. The seat retains 3 mm of solid
axial stock at each end. Cover and lead admission remain open through
the complete seat.

Slide all four complete foot-and-leg assemblies off their fixed rails. Complete
the lid's ten M5 clamps while its equipment mounts are empty. Lower
the bare pump vertically into the open cradle. Lower the cap over the motor;
the hooks' leading ramps open the 22.5 mm-long leaves over their ledges.
Both retaining undersides remain flat. Fit the PCB after both hooks seat. The spring pockets remain accessible
with back-top separated from the core. Fit
the two clamped PVC joints and discharge check while the core is open. Keep the
suction elbow and its short inlet link loose for the populated rear-shell
approach, then seat those round joints through the uncovered funnel opening.
For pump removal, separate back-top from the core, disconnect the pump joints
and leads, release both hooks and
lift the pump vertically. The snap cap prints on one axial end, keeping the
filled body, leaves and hooks vertical, with three Classic loops and a solid core.

The discharge group follows the pump datum. The suction PVC bend has a
13.050841 mm free span on two tangent arcs of at least R23.369 and unchanged
receiving lengths. Both water male fittings retain 0.4 mm of exposed shaft
outside their complete receiving depths. Its
connector rolls about its existing V-K stem axis; the opposed sockets retain
a straight 0.25 mm exposed stub. The
check outlet's two opposed bends retain at least **R14.246** and reach the straight water-in guide at
**(−82.5, 420, 253.4) mm**. The regulator, ASSE and large valves
retain their orthogonal placement.

Each square-cut PVC end starts 0.9 mm outward of the first scanned barb
profile station to clear the molded head/root. The complete 9 mm clamp bands
retain at least 1.62 mm to each usable barb end.

`g_ganen_installation.build_parts()` and `rigid_shape()` expose the bare installed
reference. `mount_holes()` and `feet_shapes()` are empty. The stock slider
observations remain independently available in the purchased reference.
Occupied casing solids describe exterior clearance, not mass or wall thickness.
Actual snap retention, vibration and assembled fit remain physical qualification.

The [production block check](../../../print-tests/rear-snap-retention/production-pump-block.json)
records the isolated base and cap's native fit and printable geometry. The
[sample trial](../../../print-tests/rear-snap-retention/README.md) records the
replacement cap and physical test scope.
