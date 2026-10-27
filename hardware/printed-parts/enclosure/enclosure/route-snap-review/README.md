# Integral tube and cable routing clips

Back-top carries simple integral clips for accessible straight tube and cable
runs. Their filled roots join the existing roof or wall, with open mouths for
installation and release. Tube and wire runs seat directly in the printed part.

The [tube-site provider](../_tube_snap_sites.py) supplies each route, straight
segment, host plane, installation order and section. The
[cable-site provider](../../../../wiring/installed/retainers.py) supplies each
hook's frame, retained conductors and local route dressing.
[The enclosure adapter](../_route_snaps.py) constructs these additions with the
shared [native profiles](../../../cadlib/route_snap.py). Positions belong to
those providers rather than a second coordinate table here.

## Selected tube runs

| Route | Host | Nominal tube OD | CAD bore | Functional spring wall | Span along tube |
| --- | --- | ---: | ---: | ---: | ---: |
| Reservoir A fill, `fluid-14` | East wall | 6.35 mm | 6.35 mm | 2.40 mm | 8 mm |
| Flavor A, `fluid-18` | Roof | 4.00 mm | 4.10 mm | 1.52 mm | 8 mm |
| Flavor B, `fluid-28` | Roof | 4.00 mm | 4.10 mm | 1.52 mm | 8 mm |
| `drain-vent` | Roof | 4.00 mm | 4.10 mm | 1.52 mm | 8 mm |

Each seat uses the C2 circular section, rounded noses and 125.421° wrap per wing.
The 4 mm section scales the functional spring thickness from C2's proportions;
its fit and flex are estimates. Each clip spans the full 8 mm along its tube.
Filled roots retain the common simple profile through to the host face.

Seat `fluid-18` before the vent crosses its approach. Seat `fluid-14` before
`fluid-16`. The provider's
`install_before` entries are the installation-order source.

Reservoir A's fore pair uses two integral C2 clips on the
[cold-core lid](../../../cold-core/foam-cap/README.md), with 13.5 mm centre spacing
at X50.5/64.0, Y209.75, Z258.5 mm. Their 6.35 mm bores and 2.40 mm wings span
8 mm along the tubes on one broad common base. Insert each tube downward through
its +Z mouth; release the exposed jaws for upward removal. The aft
curved, tied seat and purchased-body ties retain their assigned roles and
quantities. These new routing clips have no counted tie-removal credit.

## Selected cable runs

| Retained run | Seat depth × height | Span along cable | Hook stock | Retaining beak |
| --- | ---: | ---: | ---: | ---: |
| DC-1 pair, two insulated 16 AWG wires | 3.50 × 7.50 mm | 16 mm | 3 mm | 0.75 mm |
| J5 RELAYS, bare insulated 22 AWG 4P ribbon | 2.20 × 7.75 mm | 16 mm | 3 mm | 0.75 mm |
| V-K positive lead, nominal 1.70 mm insulated OD | 2.20 × 2.20 mm | 8 mm | 3 mm | 0.60 mm |

The seat dimensions describe the clear cavity, not a measured wire section.
Keep the complete insulated ribbon web flat against the wall, with its four
conductors stacked across the seat height. The clip holds insulation; bare
here means unsleeved, not stripped copper. Finish PET braid and heat-shrink
outside the retained straight span and keep the fan-out beyond it. Original
connector, relay and WAGO junctions retain their electrical assignments.
J5 retains connector order through the web: GND, V5, IO2, IO19 from installed
+Z to −Z. The single V-K seat holds `J2-positive-K`; its 1.60 mm mouth is a
provisional entry for the modeled 1.70 mm soft-insulated lead.
The [cable preparation instructions](../../../../assembly/cable-assemblies.md#back-top-clip-preparation-and-service)
cover the harness dressing and release sequence.

## Print direction and service

Back-top prints ceiling-down, building in machine −Z. Roof tube mouths and all
cable mouths face installed −Z; the east-wall `fluid-14` mouth faces −X. That
wall clip has a full 45° root corbel for its hanging edge in this print pose.
The functional spring section is the thin-stock exception; ordinary host stock
and cable hooks retain their specified broad sections.

Use back-top's production print orientation and existing PET-GF preparation,
including Tree(auto)/Default support decisions. The experimental coupon plate's
whole-layer cooling recipe is scoped to that plate. The new production clips'
layer direction, supported surfaces and cleanup require their own print reading;
the coupon archive does not establish those properties for the complete shell.

Release attached tubes and cables from the clips before sliding back-top during
opening. Support the free runs while separating the existing inter-quadrant
connections described in the [wiring sequence](../../../../assembly/wiring.md).
Re-seat the runs in the provider's installation order when assembling. Open
mouths provide the release access; no additional tool pocket is part of these
routing clips.

## Evidence and fit scope

The [combined plate's physical result](../../../../../future/snap-fit-tests/2026-10-26-mark2-combined/physical-result.json)
selects **C2 with the 6.35 mm CAD bore** for present use, retaining its 2.40 mm
wings and 125.421° wrap. A smaller bore is optional future tuning. The selected
**16 mm-span 4P ribbon clip** has accepted fit and qualitative retention: the
ribbon fits perfectly and stays put, with angling and pulling used for entry.

That acceptance belongs to the identified quarter-inch tube and 4P ribbon
coupons. The proportionally scaled 4 mm tube clips, DC-1 pair seat and V-K
single-wire seat remain provisional. The
[stopped cable coupon](../../../../../future/cable-clip-exploration/prints/2026-10-26-mark2-relay-ribbon/physical-result.json)
records deformation and cancellation, with no accepted cable fit or retention.
The complete production back-top's print finish, cleanup and installed service
remain unassessed. Numerical retention force, fatigue and lifetime are unmeasured;
native clearances alone do not establish them.

The manual [construction reading](native-review.json) identifies all seven
additions in the one-solid back-top. The [tube neighborhood reading](tube-clearances.json)
and [accepted fill-clip/lid reading](fill-lid-clearance.json) bind the local tube
clearances; the [cable opening reading](cable-clearances.json) covers the hook
locations and loading space. The [native assembly receipt](native-assemblies.json)
and [wiring reading](wiring-review.json) identify the retained fixture geometry,
seated pump retainer and wire endpoints. The [integration receipt](integration.json)
binds the installed native files and viewer payloads.
The [publication receipt](publication.json) confirms the live viewer's native
source, and the [post-publication geometry reading](post-publication-lint-review.json)
records the working catch/spring faces and the C14 opening's existing
classification answer.
