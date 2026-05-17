# Flavor Reservoir Cap Vent

Hydrophobic PTFE membrane filter inside the printed reservoir cap, plus a slotted splash-baffle cylinder hanging below the filter pocket. The vent lets air pass through the cap as the reservoir fills and drains, while blocking syrup splashes from reaching the membrane.

## Architecture

A ø13 mm × 0.5 mm hydrophobic PTFE membrane filter (LVDALAB B0D41KT345) sits in a ø13.2 × 2.5 mm cylindrical pocket at the top of the cap. A press-fit TPU 90A retaining ring holds the filter down. Below the pocket, a slotted splash-baffle cylinder hangs into the cap interior — any syrup that splashes up against the cap ceiling has to take a 90°-turn through one of the cylinder's side slots before it could reach the membrane.

Geometry constants in [`generate_step_cadquery.py`](generate_step_cadquery.py) lines 192–270 (`vent_pocket_*`, `vent_cylinder_*`, `vent_slot_*`, `vent_brim_*`). Headline values:

- Filter: ø13 mm × 0.5 mm, hydrophobic PTFE on PET backing
- Pocket: ø13.2 mm × 2.5 mm (filter thickness + retaining ring thickness)
- Vent boss outer: ø17.2 mm (2 mm wall around pocket)
- Vent hole through cap: ø5 mm
- Splash-baffle cylinder: ø10 mm OD × ø5 mm ID, ~3 mm long, hanging below the cap ceiling
- Splash-baffle slots: 4 slots, 3 mm wide × 2 mm tall, cut into the cylinder wall

## Why a vent at all

The reservoir is non-pressurized. As syrup drains out the bottom outlet (PP1208E bulkhead) the air space above the liquid grows; without a vent, atmospheric pressure could not equalize and the outlet flow would stall. Conversely, as the hopper-fill cycle refills the reservoir from above, displaced air has to leave somewhere.

## Why a hydrophobic membrane (not a simple hole)

The reservoir holds dilute sucralose-syrup that splashes when the hopper pours into it and when the pump cycles draw liquid through the bottom outlet. A bare vent hole would let splashed syrup wick out of the cap and dry on the appliance interior; over the 10-year unmaintained design lifetime, the cumulative residue would be a service problem. The hydrophobic PTFE membrane passes air freely but blocks aqueous syrup at the membrane surface.

## Why a splash baffle below the membrane

Even with a hydrophobic membrane, repeated direct splashes onto the membrane surface would gradually clog its pores with sucralose residue from the evaporating splash. The splash-baffle cylinder forces any upward splash to take a 90° lateral turn before it can reach the membrane — the splash either lands on the closed top of the baffle's inner cavity or on the cylinder wall, and runs back down rather than reaching the filter.

## Why ø13 mm × 0.5 mm

Standard lab-filter disc size. ø13 mm is small enough to fit in the cap's available footprint between the screw-boss positions; large enough for adequate air passage at the slow venting rate the reservoir actually experiences. 0.5 mm thickness is the off-the-shelf laminated-PTFE-on-PET-support spec; cheaper than custom and held in the 100-pack at $0.13/filter delivered.

## Per-build parts

Tracked in [`../../../bom.md`](../../../bom.md) §13:

- **2 LVDALAB PTFE membrane filters** (B0D41KT345), one per cap × 2 caps
- **TPU 90A retaining rings** printed from the same gasket stock — not separately listed
- **Splash-baffle cylinder** is part of the cap print, not a separate part

## Service

If a membrane ever clogs (well past the design lifetime in practice), the cap comes off via the same 6 M3 × 12 SHCS that hold it to the reservoir body; the retaining ring lifts out; the filter swaps. The 100-pack is a lifetime supply at 2/build.
