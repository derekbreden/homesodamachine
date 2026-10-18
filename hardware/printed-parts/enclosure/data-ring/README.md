# Enclosure data-port identification plate

The black PET-GF plate uses the nameplate's continuous face and two broad
horizontal wings. The face is 32 × 29.789 mm,
matching OVER's Z height and alignment, with square upper and R2 lower corners.
The complete plate, including both wings, is 1.68 mm deep. Each wing projects
2.4 mm, spans 21.789 mm and has R0.6 ends. A 20.8 × 18.3 mm opening centres on
the RJ11 jack.
White DATA lettering fills a 0.72 mm recess and rises 0.48 mm above the face.

The plate's nominal back is 3.36 mm behind the rear wall, with 0.15 mm to its
PET-GF receiver. Its face is recessed 1.68 mm. The jack and its complete fixed
receptacle stand another 0.16 mm inboard, retaining a full 3 mm flat aperture lip
behind the plate's back allowance. The receptacle carries cable insertion and
withdrawal loads; its upper swing ease retains the specified 50° profile.
The matching wing
slots use the accepted nameplate's 0.45 mm Y clearance, entry bevel and complete
1.23 mm retaining lands. DATA and OVER share the middle row, which stands where its webs
to the SODA and FLAVOR pockets come out equal.

Print flat-back-down with the lettering facing up. The continuous face and both
wings lie directly on the bed, without supports. The plate uses the black
identification project in the [OVER print set](../../drain-readiness/README.md),
with black PET-GF on Mark2's right nozzle and white PET-GF on its left nozzle.
Bend the plate gently to seat its wings in the side slots, as for the nameplate.
DATA is fixed trim. The jack is installed and serviced from inside the machine, behind
the plate, so the plate is fitted once and not removed; its receiver has no release opening.

The [enclosure fit review](../enclosure/y-seam-fit-review.json) records the current
back and wing gaps, ordinary backing, complete jack lip and insertion-ease profile.
The separate [DATA fit record](fit-check.json) retains its identified wall/plate inputs,
wing lands, DATA/OVER alignment and plug/latch-approach readings. Its input hashes define
that scope. Insertion force, pullout capacity and endurance require their own evidence;
accepted nameplate and display results retain their identified print scope.

`data_ring.py` exports the colored plate and lettering. The shared
[`_data_wing_interface.py`](../enclosure/_data_wing_interface.py) calls the
[nameplate construction](../enclosure/_nameplate_wing_interface.py) for both
the plate and its enclosure pocket.
