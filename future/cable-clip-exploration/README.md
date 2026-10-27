# Bare relay-ribbon clip trials

These coupons hold the **bare 22 AWG 4P J5 RELAYS ribbon** beside a wall, with the
four conductors stacked vertically. The modeled ribbon is 7.25 × 1.70 mm: four
1.70 mm insulated conductors on 1.85 mm pitch. That envelope is a layout value;
the actual complete ribbon section has not been measured.

The current one-piece clips have **16 mm and 24 mm spans along the cable** on
**9 mm thick host walls**. Their seat is 2.20 × 7.75 mm, with a 1.45 mm entry
and a 0.75 mm retaining beak. The outer post, cap and 45° corbel use 3 mm stock.
Each wall extends 6 mm below the hook. Wall lengths are 28 and 36 mm, giving
252 and 324 mm² bed footprints. Both coupons print upright, entry up.

The [geometry report](wall9-span-geometry.json) binds the
[generator](wall9_span_trial.py), native single solids and exported parts.
The hook cross-sections match the accepted profile, with zero added or missing
native volume in the common 8 mm reference span. The modeled strands have
zero overlap and 0.25 mm minimum seated clearance.

The [combined Mark2 plate](../snap-fit-tests/2026-10-26-mark2-combined/README.md)
prints both cable variants and the C2 tube-bore comparison. This experiment
uses **100% part cooling after the first three layers** and a **20-second layer
target**, printing all objects by layer. Native upper cable-layer feed-time
lower bounds are approximately 19.77–48.85 seconds; actual elapsed times and
airflow are not measured. There is no generated support or brim.

The [stopped 3 mm-wall coupon's physical result](prints/2026-10-26-mark2-relay-ribbon/physical-result.json)
records visible deformation and cancellation before completion. No cable fit,
grip, release or spring survival result is accepted from that print.

## Proposed J5 site

The [8 mm-span site reading](proposed-site-review.json) places the guide on back-top’s west
inside face, **X−98.5**, across **Y324–332 mm**. The local frame begins at
**(−98.5, 328, 275.925) mm** and the ribbon centre is
**(−97.4, 328, 288) mm**. The installed mouth faces +Z; the cable runs along Y.

This proposal requires dressing the J5 conductors **2.4 mm toward the wall**,
with an **8 mm straight bare window before the relay fan-out**. The ¼-inch PET
braid ends before the clip. It does not represent the current route unchanged
or remove a counted tie. The closest tested native body is V-A, with
**0.846 mm** clip clearance and **4.096 mm** clearance to the loading envelope.
The checked fixtures have no native overlap. Connecting curves, braid transition,
complete quadrant assembly and service remain outside that local reading.
The guide and redressing are a site proposal, not production integration.
The 16 mm and 24 mm trial spans have no production-site clearance reading.

Use the actual bare 4P ribbon to assess insertion, grip, axial slide, release and
layer/root survival. These coupons do not test a braided sleeve or finished
crimp inside the clip, and their print pose does not define a production quadrant's pose.

```sh
tools/cad-venv/bin/python future/cable-clip-exploration/wall9_span_trial.py
tools/cad-venv/bin/python future/snap-fit-tests/2026-10-26-mark2-combined/prepare.py
```
