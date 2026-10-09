# DATA plate

The black PET-GF plate uses the nameplate's continuous face and two broad
horizontal wings. The face is 32 × 29.789 mm,
matching OVER's Z height and alignment, with square upper and R2 lower corners.
The complete plate, including both wings, is 1.68 mm deep. Each wing projects
2.4 mm, spans 21.789 mm and has R0.6 ends. A 20.8 × 18.3 mm opening centres on
the RJ11 jack.
White DATA lettering fills a 0.72 mm recess and rises 0.48 mm above the face.

The plate and jack sit on the nameplate pocket's seating datum, 3.36 mm behind
the rear wall. The plate face is 1.68 mm behind that wall; the fixed jack
receptacle carries cable insertion and withdrawal loads. The matching wing
slots use the accepted nameplate's 0.45 mm Y clearance, entry bevel and complete
1.23 mm retaining lands. The three rear rows retain their installed positions.

Print flat-back-down with the lettering facing up. The continuous face and both
wings lie directly on the bed, without supports. The plate uses the black
identification project in the [OVER print set](../../drain-readiness/README.md),
with black PET-GF on Mark2's right nozzle and white PET-GF on its left nozzle.
Bend the plate gently to seat its wings in the side slots, as for the nameplate.

The [native fit check](fit-check.json) reads the saved production wall, shared
nameplate construction, complete wing retaining lands, DATA/OVER alignment
and plug/latch approach. Printed fit, insertion force, pullout capacity and
endurance remain observations on the finished plate and wall. Accepted
nameplate and display results retain their identified print scope.

`data_ring.py` exports the colored plate and lettering. The shared
[`_data_wing_interface.py`](../enclosure/_data_wing_interface.py) calls the
[nameplate construction](../enclosure/_nameplate_wing_interface.py) for both
the plate and its enclosure pocket.
