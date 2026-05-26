# Flavor Reservoir Cap Vent

Hydrophobic PTFE membrane filter inside the printed reservoir cap, plus a slotted splash-baffle cylinder hanging below the filter pocket. The vent lets air pass through the cap as the reservoir fills and drains, while blocking syrup splashes from reaching the membrane.

## Architecture

A ø[13 mm](FILTER_D) × [0.5 mm](FILTER_T) hydrophobic PTFE membrane filter (LVDALAB B0D41KT345) sits in a ø[13.2 mm](VENT_POCKET_D) × [2.5 mm](VENT_POCKET_DEPTH) cylindrical pocket at the top of the cap. A press-fit TPU 90A retaining ring holds the filter down. Below the pocket, a slotted splash-baffle cylinder hangs into the cap interior — any syrup that splashes up against the cap ceiling has to take a 90°-turn through one of the cylinder's side slots before it could reach the membrane.

Geometry constants in `reservoir.py` in this directory lines 192–270 (`vent_pocket_*`, `vent_cylinder_*`, `vent_slot_*`, `vent_brim_*`). Headline values:

- Filter: ø[13 mm](FILTER_D) × [0.5 mm](FILTER_T), hydrophobic PTFE on PET backing
- Pocket: ø[13.2 mm](VENT_POCKET_D) × [2.5 mm](VENT_POCKET_DEPTH) (filter thickness + retaining ring thickness)
- Vent boss outer: ø[17.2 mm](VENT_BOSS_OD) ([2 mm](VENT_BOSS_WALL) wall around pocket)
- Vent hole through cap: ø[5 mm](VENT_HOLE_D)
- Splash-baffle cylinder: ø[10 mm](VENT_CYL_OD) OD × ø[5 mm](VENT_CYL_ID) ID, ~3 mm long, hanging below the cap ceiling
- Splash-baffle slots: [4](VENT_SLOT_COUNT) slots, [3 mm](VENT_SLOT_W) wide × [2 mm](VENT_SLOT_H) tall, cut into the cylinder wall

## Function

The reservoir is non-pressurized; the vent equalizes the air space
above the liquid as syrup drains out the bottom outlet (PP1208E
bulkhead) and as the hopper-fill cycle refills it from above.

The hydrophobic PTFE membrane passes air freely and blocks aqueous
syrup at the membrane surface. The splash-baffle cylinder forces any
upward splash to take a 90° lateral turn before reaching the
membrane — splash lands on the closed top of the baffle's inner
cavity or on the cylinder wall and runs back down.

The ø[13 mm](FILTER_D) × [0.5 mm](FILTER_T) filter is a standard lab-filter disc; laminated PTFE on PET support, held in 100-packs at $0.13/filter delivered.

## Per-build parts

Tracked in [`../../../bom.md`](../../../bom.md) §13:

- **2 LVDALAB PTFE membrane filters** (B0D41KT345), one per cap × 2 caps
- **TPU 90A retaining rings** printed from the same gasket stock — not separately listed
- **Splash-baffle cylinder** is part of the cap print, not a separate part

## Service

If a membrane ever clogs (well past the design lifetime in practice), the cap comes off via the same 6 M3 × 12 SHCS that hold it to the reservoir body; the retaining ring lifts out; the filter swaps. The 100-pack is a lifetime supply at 2/build.

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
