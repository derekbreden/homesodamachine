# Flavor Reservoir Cap Vent

Hydrophobic PTFE membrane filter inside the printed reservoir cap, plus a slotted splash-baffle cylinder hanging below the filter pocket. The vent lets air pass through the cap as the reservoir fills and drains, while blocking syrup splashes from reaching the membrane.

## Architecture

A ø[13 mm](FILTER_D) × [0.5 mm](FILTER_T) hydrophobic PTFE membrane filter (LVDALAB B0D41KT345) sits in a ø[13.3 mm](VENT_POCKET_D) × [2.75 mm](VENT_POCKET_DEPTH) cylindrical pocket at the top of the cap. A press-fit TPU 90A retaining ring holds the filter down. Below the pocket, a slotted splash-baffle cylinder hangs into the cap interior — any syrup that splashes up against the cap ceiling has to take a 90°-turn through one of the cylinder's side slots before it could reach the membrane.

Geometry constants in `reservoir.py` in this directory (`vent_pocket_*`, `vent_cylinder_*`, `vent_slot_*`, `vent_brim_*`). Headline values:

- Filter: ø[13 mm](FILTER_D) × [0.5 mm](FILTER_T), hydrophobic PTFE on PET backing
- Pocket: ø[13.3 mm](VENT_POCKET_D) × [2.75 mm](VENT_POCKET_DEPTH) (filter thickness + retaining ring thickness)
- Vent boss outer: ø[17.3 mm](VENT_BOSS_OD) ([2 mm](VENT_BOSS_WALL) wall around pocket)
- Vent hole through cap: ø[5 mm](VENT_HOLE_D)
- Splash-baffle cylinder: ø[10 mm](VENT_CYL_OD) OD × ø[5 mm](VENT_CYL_ID) ID, ~3 mm long, hanging below the cap ceiling
- Splash-baffle slots: [4](VENT_SLOT_COUNT) slots, [3 mm](VENT_SLOT_W) wide × [2 mm](VENT_SLOT_H) tall, cut into the cylinder wall

## Function

The reservoir is non-pressurized; the vent equalizes the air space
above the liquid as the pump draws syrup up the dip tube and as the
fill cycle refills it from above.

Dry hydrophobic membrane vents pass air in both directions. During filling,
outgoing air replaces the incoming liquid volume; during drawing, incoming air
replaces the outgoing liquid volume. The required airflow is the larger of the
fill and draw rates, as described in [Pall's tank-vent guidance](https://www.pall.com/en/food-beverage/tank-air-vent.html).
No installed airflow or syrup-wetting result is recorded for this particular
LVDALAB disc. Its restriction and fouling life are unqualified.

The splash-baffle cylinder shields the membrane from direct upward splash:
liquid meets its closed bottom or wall, with a lateral turn through a slot
required to reach the vent bore.

## Path through the assembled casing

The filter pocket opens below the top foam-cap floor. Current native geometry
places the reservoir-cap top at Z213.15 mm and that floor's underside at
Z213.5500001 mm: **0.4 mm nominal air clearance**. There is no dedicated
reservoir-air conduit through the foam cap.

The [October 25 review](tube-grip-vent-review.json) traces clear nominal paths
from both vent positions across that gap and up the draw-conduit annuli,
including reservoir B's two bends. With a 6.5 mm tube envelope in the 7.5 mm
passage, the sampled annular paths have approximately 0.25 mm clearance to
both tube and printed passage. These are geometric openings, not measured
airflow. Printed contact, assembly and installed closures affect conductance.
The loose fill/draw tube bores also provide air paths that bypass the membrane.

A dedicated vent line per reservoir is the recommended candidate when defining
the complete air boundary and tube grips. Preserve the splash baffle, route
the line through a protected casing passage to outside the insulation, and
place a hydrophobic filter at a sheltered, dry external termination. The line
must pass air in both directions and remain free of liquid traps.

The existing neoFlo **4 mm OD / 2.5 mm ID** stock is a plausible size for a
short vent route. At an illustrative 0.6 L/min air demand, 0.3 m of straight
dry tubing has a calculated drop of approximately **57 Pa / 0.0082 psi**.
This excludes the membrane, bends, fittings and liquid contamination; it does
not qualify a finished assembly. The [manufacturer sheet](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf)
specifies that tube's ID and 25 mm minimum bend radius. No dedicated vent line
or new tube grip is present in the current printed geometry.

The [3D review proposal](tube-vent-proposal/README.md) provides independent
straight air tubes through integral casing passages, with flush TPU grips in
the reservoir lids and slotted splash baffles below. Its tube ends stand
6 mm above the insulation in the equipment space. This initial candidate
contains no filter; Derek has deferred filtering until the tube and grommet
arrangement is evaluated. Native geometry and assembly clearances are
recorded separately from physical fit and airflow qualification.

The ø[13 mm](FILTER_D) × [0.5 mm](FILTER_T) filter is a standard lab-filter disc; laminated PTFE on PET support, held in 100-packs at $0.13/filter delivered.

## Per-build parts

Tracked in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §13:

- **2 LVDALAB PTFE membrane filters** (B0D41KT345), one per cap × 2 caps
- **TPU 90A retaining rings** printed from the same gasket stock — not separately listed
- **Splash-baffle cylinder** is part of the cap print, not a separate part

## Service

For bench replacement before the core is enclosed, the cap comes off via its
six M3 × 12 screws; the retaining ring lifts out and the filter can be replaced.
No membrane service-life result is recorded.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
