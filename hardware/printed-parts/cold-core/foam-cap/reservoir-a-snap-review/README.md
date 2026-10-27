# Reservoir A fore paired snap

HSM-000337 is one removable PET-GF cap on the integral fore receiver in
HSM-000020, the cold-core top lid. Its two upper half-pipes close over the
continuous ¼-inch fill and draw tubes. The full-width wings spread outward
over the receiver's ledges, then recover beneath them. Both wings and their
hooks span the cap's entire 6 mm Y length. Pull the exposed wings outward
to release the cap.

The receiver spans 12.5 mm in Y, centred at Y209.75. Its two 3 mm end
shoulders capture the cap axially, with 0.25 mm running air at each end.
The lower seats retain 3 mm floors and outer cheeks. The shared seat opening
has a 3 mm central land. The tube centre lines are X50.5/58, Z258.5 mm.

| Interface | Nominal allowance |
| --- | ---: |
| Tube to 3.325 mm-radius seats | 0.15 mm radial |
| Cap ends to axial shoulders | 0.25 mm per end |
| Wing inside faces to receiver ledges | 0.25 mm per side |
| Cap's rigid lower faces to receiver top | 0.25 mm |
| Hook bearing to receiver underside | 0.40 mm, including printed underside allowance |
| Hook overlap beneath receiver | 0.45 mm |

The thinner stock belongs to the spring and its root transition: 1.44 mm
through a 6.7 mm free height. The 3 mm-tall hook includes a 45° entry nose.
That functional taper is part of the spring tip. The cap prints on its Y end
so its bending profiles lie within the deposited layer planes. The ordinary
top lid retains its existing print orientation. The receiver and one 3 mm
wall depth into its lid root receive local solid infill.

The elementary cantilever estimate, `1.5 × thickness × deflection / length²`,
gives 2.17% at the nominal 0.45 mm engagement and 2.89% at 0.60 mm spread.
The second value includes an additional 0.15 mm for printed material standing
proud. These are comparisons of a straight-beam approximation, without a
root stress concentration or material model. They do not establish a safe
material limit, force, repeated-use performance or retained load.

The [native reading](native-review.json), produced manually by
[`review_reservoir_a_snap.py`](../../../../../tools/reviews/review_reservoir_a_snap.py),
binds current source and exported geometry. It includes seated fit, both
axial stops, the 6.65 mm cap approach and a native outward-bending section.
Its bent shape is a geometric motion proxy. The complete cap starts above
the receiver. Its approach is read against the current valve, fittings,
wire dressing and the shallow spring-foot pockets in the top lid.

The inlet earth lug points at 300°. Its PE lead approaches through the fore
lane with R3 bends and an 11.765 mm straight crimp entry. The
[local native route reading](pe-route-review.json) records the actual lug,
conductor and neighboring hardware. The populated appliance export carries
the same terminal and route.

The [offline print reading](print/README.md) binds the prepared cap and lid
jobs and their emitted model/support paths. Physical snap fit, tube restraint,
insertion and release forces, creep, fatigue and load capacity remain unmeasured.
The aft Reservoir A station retains its tied seat.
