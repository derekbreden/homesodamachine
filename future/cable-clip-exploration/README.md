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

The [combined plate's physical result](../snap-fit-tests/2026-10-26-mark2-combined/physical-result.json)
accepts the smaller **16 mm-span** clip with the bare insulated 4P ribbon.
It fits perfectly and stays put. Straight sliding entry is difficult; angling
and pulling the ribbon into the seat succeeds. This is qualitative fit and
retention acceptance of that identified coupon, with no measured force or lifetime.

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

## Production J5 installation

The selected **16 mm-span** profile is integral to back-top's west inside wall.
The [site provider](../../hardware/wiring/installed/retainers.py) defines the
`j5-west-ribbon` frame, conductor order and local dressing; the
[production review](../../hardware/printed-parts/enclosure/enclosure/route-snap-review/README.md)
records installation, print direction and fit scope. The installed mouth faces
−Z. Back-top prints ceiling-down, building in machine −Z.

Keep a full 16 mm straight bare-insulated window through the hook. Finish the
¼-inch PET braid and heat-shrink outside it, and begin the free-lead fan-out
after it. Preserve connector order GND, V5, IO2, IO19 from installed +Z to −Z.
Release the ribbon before sliding back-top for service. Original electrical
junctions and counted body ties retain their assigned roles.

The accepted 4P seat does not establish fit of the DC-1 pair or V-K single-lead
seats. Production-shell cleanup, installed release forces and layer/root
lifetime remain separate from the identified upright coupon result.

```sh
tools/cad-venv/bin/python future/cable-clip-exploration/wall9_span_trial.py
tools/cad-venv/bin/python future/snap-fit-tests/2026-10-26-mark2-combined/prepare.py
```
