# Reservoir A fore direct C2 snaps

Two quarter-inch tubes press down into integral C2 seats on one broad lid base.
Draw is at X50.5, fill at X64.0, both Y209.75/Z258.5 mm in appliance coordinates.
The 13.5 mm pitch leaves independent free jaws above the equator. The shared
base spans X44.925–69.575 and Y205.75–213.75 mm, embeds 3 mm into the lid and
fills continuously to the two tube equators.

The section uses the accepted quarter-inch C2 coupon: Ø6.35 mm seat, 2.4 mm
spring thickness, 125.421° per wing and 8 mm axial span. See the
[physical fit result](../../../../../future/snap-fit-tests/2026-10-26-mark2-combined/physical-result.json).
The 2.4 mm section is the functional spring exception to ordinary 3 mm stock.
The complete lid station still needs its own printed access and retention trial.

The draw route is exact. The fill approach retains its existing line/arc topology,
R14 bends, endpoints, aft tied seat and east-wall snap. The fore pair uses no
separate cap, axial shoulders or latch-foot relief pockets. Open air above the
jaws provides local release access.

[Fit readings](fit.json) bind the actual pair, complete lid and tube BReps to
published native hardware and wiring. They cover seated stock, fixed base,
changed fill bends, 7 mm local insertion capsules and conservative 1 mm jaw
spread bounds. No new foreign overlap is introduced. These are geometry
readings, not force, fatigue or lifetime qualifications.

[Native parent readings](native-parents.json) cover the lid, foam stack, cold
core and complete appliance. Only the lid and fill tube surfaces change, and the
separate cap component is absent. Other native geometry, hierarchy, poses,
colors and wiring are retained. [Assembly scene readings](assembly-scenes.json)
bind the five guide GLBs; their other triangles, materials and transforms are exact.

[Lid readings](lid.json) bind the four free arms and the unchanged stock outside
the fore site. [Printability readings](geometry-lint.json) identify the specified
2.4 mm spring walls and their narrowly anchored functional exception.
[Publication](publication.json) binds the live appliance and its cap-free mesh set.
