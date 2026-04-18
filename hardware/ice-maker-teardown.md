# Ice Maker Teardowns

Two countertop ice makers were purchased for harvesting refrigeration components (compressor, condenser + fan, capillary tube, filter-drier). The evaporator cold plate and the ice-harvest hardware are discarded — a custom copper coil wound around the carbonator vessel replaces the factory evaporator. See `hardware/future.md` for how the harvested parts fit into the cold core assembly.

EPA 608 Type I certification is required before recovering the factory charge. Both units ship with very small hydrocarbon charges (R600a, isobutane), so recovery equipment must be hydrocarbon-rated / intrinsically safe — R134a-only recovery machines are not appropriate.

---

## Unit A — Generic countertop, 8 cubes / 6 min

- ASIN: **B0F42MT8JX**
- Price: $63.80
- Rated output: 26 lb/day
- First teardown: 2026-04-17

### Refrigerant

**R600a (isobutane).** Flammable. Charge is small (well under the 150 g UL 60335-2-89 limit for small appliances; factory label will list the exact mass). Brazing anywhere in the sealed loop requires the charge to be recovered first — do not heat a pressurized R600a circuit.

Note: `future.md` references R134a for the teardown-and-recharge workflow. That should be reconciled — at minimum this unit uses R600a, and the Frigidaire very likely does too (nearly all current-gen countertop ice makers are R600a). The recharge plan may need to keep the factory refrigerant rather than converting.

### Refrigerant circuit topology (verified by disassembly)

```
    ┌── discharge ──► condenser ──► filter-drier ──► capillary tube ──┐
    │                                                     (bonded to   │
compressor                                                suction line)│
    │                                                                  ▼
    └── suction ◄──────────────────────────────── evaporator ◄─────────┘

    side branch:  compressor discharge ──► hot-gas bypass solenoid ──► evaporator
                  (active only during harvest cycle — delete for our use)

    not in the loop: compressor process tube (factory charge port, dead-end stub)
```

This matches standard R600a small-appliance practice. Verified by tracing the tubing on this unit during teardown, not assumed from reference material.

### Compressor

- Manufacturer: NingBo Anuodan Machinery Co., Ltd
- Model: **HD48Y11**
- Hermetic reciprocating, 1-phase, thermally protected, UL / CSM listed
- Larger than intuition suggests for a $64 appliance — this is normal. R600a hermetic cans have a floor size set by the motor, piston, and oil sump regardless of rated capacity. Freezing cubes in six minutes demands real wattage; this is likely in the 90–120 W cooling-capacity range, which is plenty for holding a carbonator at service temperature.

### Condenser

Finned-tube forced-convection condenser with its own fan shroud (fan not yet separated in photos). Standard wire-and-plate construction. Reuse as-is — orient for front-of-enclosure mounting per the enclosure layout in `future.md`.

### Filter-drier

A fat copper cylinder sits between the condenser outlet and the capillary tube inlet. It holds a molecular-sieve desiccant charge that traps residual moisture and debris — moisture in an R600a system freezes at the capillary tube orifice and causes intermittent loss of cooling, so the drier is load-bearing for reliability, not optional.

Label on this unit's drier:

- `8.05.08.044` (leading digit ambiguous — could be `0`)
- `60-130-05` — almost certainly the drier's model / part number. Useful if sourcing a drop-in replacement from the same supply chain; not confidently decodable without the manufacturer.
- `20251107 A-1` — manufacturing date code, 2025-11-07, line/shift A-1.
- Small stylized logo at left (manufacturer mark, not identified).

**Desiccant replacement rule:** once the refrigerant loop is opened (unbrazing for re-piping), the drier's desiccant has absorbed atmospheric moisture and is spent. Replace the drier before recharging. This is standard practice, not optional — reusing a saturated drier gives a short service life and eventual capillary icing.

### Capillary tube + suction-line heat exchanger

Downstream of the filter-drier, the metering device is a hair-bore **capillary tube** (not a TXV — cheaper, no moving parts, fine for fixed-load systems like ours). ID is roughly 0.03″ (well under 1 mm) — visibly thinner than you'd think anything could flow through, and that is the entire point. This single tube drops pressure from condenser side (~100 PSI) to evaporator side (~5–10 PSI for R600a) across its length. Mass flow for a 100 W-class system is a fraction of a gram per second, so the tiny bore passes the full charge just fine.

Physical path through this unit, start to finish:

1. **Exits the filter-drier** (cap tube is brazed into the drier's outlet end).
2. **Runs bonded alongside the suction line** for most of its length — this is the passive internal heat exchanger. Cold return gas from the evaporator subcools the liquid refrigerant before it flashes, increasing effective capacity at zero cost.
3. **Coils up in a short helix** right before the evaporator inlet — packaging, to fit the required length into a small area and manage any final pressure trim.
4. **Enters the evaporator.**

Keep the bonded cap-tube-plus-suction-line pair intact when re-piping — separating them hurts efficiency for zero benefit. The helical coil at the evaporator end is also worth preserving as-is; if total cap length changes (e.g., the evaporator is relocated when we swap the cold plate for our carbonator coil), a refrigeration tech recalculates cap length for the new load, rather than guessing.

### Process tube (the "dead-end" copper stub)

A short (~2″) copper tube closed with a pinched-and-brazed tip **sticks straight out of the compressor body** and connects to nothing else — it is genuinely a dead end. This is the factory charging port. The process is: evacuate the system through this tube, inject the refrigerant charge, then crimp and braze the tip shut. It has no flow during operation. This is where recovery and recharge will tap in during reassembly — either by cutting the crimped tip and brazing on a piercing saddle / access port, or by installing a bolt-on Schrader saddle over the tube.

Do not confuse with the capillary tube. Process tube = fat short stub on the compressor, pinched shut, goes nowhere. Capillary tube = long hair-thin line threading through the main loop between filter-drier and evaporator.

### Hot-gas bypass solenoid (DISCARD for our use)

A small AC solenoid valve is teed into the refrigerant circuit:

- Label: **SOLENOID VALVE — AC 110V 50/60Hz 4/4.5 W — TIANHAQ 25.10.17**
- Function in ice maker: during the harvest cycle, this valve opens and routes hot compressor discharge gas directly into the evaporator (bypassing the condenser and capillary tube), warming the cold fingers so formed cubes release and drop. Without it, an ice maker has no way to get cubes off the evaporator.
- Function in our build: **none.** We want continuous steady cold around the carbonator, not a harvest cycle. Remove the valve entirely when re-piping, or (if it's more convenient to leave physically in place) never energize it and verify the bypass path is sealed.

### Evaporator cold plate (DISCARD)

The stainless-finger cold plate is purpose-built for cube formation and has no role in our cold core. Cut it out during re-piping. The suction-side connection point moves to the new coil wound around the carbonator vessel.

### Summary — keep vs discard for this unit

| Part | Disposition |
|---|---|
| Compressor | Keep |
| Condenser + fan | Keep |
| Capillary tube (bonded to suction line) | Keep — do not separate |
| Filter-drier | Keep in place; replace with fresh drier before recharge if the loop is opened |
| Process tube | Keep — recovery/recharge access point |
| Hot-gas bypass solenoid | Discard / bypass |
| Evaporator finger plate | Discard |
| Thermostat / harvest-cycle controller | Discard (custom ESP32-S3 firmware replaces it) |

### Open items

- Factory refrigerant charge mass (read from the nameplate once fully exposed)
- Compressor rated cooling capacity in W — confirm against expected load of holding ~1.5 L of carbonated water at 2 °C against cabinet-ambient
- Physical dimensions of compressor + condenser pair, for enclosure layout
- Decide whether to save photos to `hardware/ice-maker-teardowns/unit-a-b0f42mt8jx/raw-images/` alongside this doc

---

## Unit B — Frigidaire EFIC117-SS

- ASIN: **B07PCZKG94**
- Price: $78.70
- Rated output: 26 lb/day
- Teardown: pending

To be filled in after teardown.
