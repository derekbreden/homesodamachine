# V-B wall junctions and tube routing

The four core WAGO 221-413 junctions occupy two rows on the PCB-facing back
of V-B’s mounting wall. Their levers open west; the sensor/V12 ports face
fore and the reed/GND ports face aft. Integral blank-backed wells retain
3 mm stock and join the valve wall and lid. Seat the fore-facing connectors
before installing V-B’s inlet plumbing.

The wall and upper wells share the flat Z298.65 mm top plane.

V-B’s native origin is X38/Y244.90434/Z279.41. Its inlet follows an R19.98
minimum S-offset between the stem elbows; its return uses the crowned
R28.66 minimum curve into the fixed Y-B fitting. The reservoir-A tubes
and fore snap occupy the existing lanes at Z258.5, then rise with R14 bends
to Z259.5 before the aft restraint. Their free descending bends sit clear
of the earth terminal stack. The V-A feed follows the low west lane at
X11/Z261.6 between its fixed fitting endpoints.

| Native interface | Clearance, mm |
| --- | ---: |
| WAGO well top to removable funnel frame | 1.250 |
| Reservoir A fill tube to V-B | 1.385 |
| Reservoir A draw tube to V-B | 1.735 |
| Reservoir A draw tube to V-K elbow | 1.023 |
| Fill tube to draw tube | 1.010 |
| Draw tube to earth terminal stack | 1.196 |
| Tube to its retaining half-pipe | 0.150 radial, intended fit |

The fore cap’s spring feet enter two shallow lid pockets with 0.25 mm
nominal floor clearance and 4.75 mm lid backing. Its local print geometry
and print orientation are retained. The aft seat follows the actual tube
curves and retains its narrow tie. The longest unrestrained spans between the modeled
route endpoints, fore snap and aft seat are 176.93 mm for fill and
138.75 mm for draw, below the existing 200 mm span target.

[Native clearances](native-clearances.json) and the
[assembly export receipt](production-export.json) bind the reviewed bodies
to the populated appliance. The export retains the published enclosure
panels, seated pump retainer, pump and board. The
[cap motion reading](../reservoir-a-snap-review/native-review.json) includes
the current installed wire dressing. Its bent section is a geometric space
proxy; physical insertion force and snap retention are unmeasured.

The fourteen affected wire routes terminate at their selected electrical
connections and retain the existing embedded passages. The
[exposed wire reading](wire-clearances.json) checks the redressed sections
against nearby physical bodies. Wire paths describe proposed dressing;
they do not prescribe a physically packed cable bundle.

The [prepared top-lid job](print/2026-10-27-foam-cap-lid-top-mark2-3f287a66/preparation.json)
uses Mark2’s left 0.4 mm Standard nozzle and black PET-GF15, with
Tree(auto)/Default supports. Its
[native path review](print/2026-10-27-foam-cap-lid-top-mark2-3f287a66/review.json)
passes: 211 layers, 21.2 mm minimum full-bead bed margin, matching archived
G-code digest, and at least 99.31% sampled solid coverage through the fore
receiver and lid root. The prepared STL digest matches the current lid.
This is an offline preparation; no print was launched.

The populated export retains the published back-top tube clips. The whole-machine
scorecard remains open. The separate ASSE/drain reading flags the vent tube’s
0.05 mm nominal radial clearance in its back-top clip as an unconnected
clearance; that clip contact needs its finite named-contact treatment.
