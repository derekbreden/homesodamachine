# Ice Maker Teardowns

Two countertop ice makers were purchased for harvesting refrigeration components (compressor, condenser + fan, capillary tube, filter-drier). See `hardware/future.md` for how the harvested parts fit into the cold core assembly, and [`../../assembly/refrigerant-loop.md`](../../assembly/refrigerant-loop.md) for the production procedure that uses the components identified below.

## Cold core architecture

Custom SS carbonator + new evaporator coil. The factory finger-plate evaporator is discarded; a custom copper coil is wound around the fabricated 316L SS carbonator (vertical 5" OD × 0.065" wall 316 welded round tube with 1/4"-thick 316 circular end plates, per [`hardware/future.md`](../../future.md)). The refrigerant loop is opened (cut into the suction and cap-tube sides of the factory evaporator), the factory charge is vented, the drier is replaced, the system is evacuated, and it is recharged.

The hot-gas bypass solenoid is deleted — we want steady cold, not harvest cycles.

R-600a is carved out of the EPA Section 608 venting prohibition as a natural refrigerant, so no 608 certification is legally required. Standard (non-hydrocarbon-rated) HVAC vacuum pump and manifold are fine — we vent to atmosphere rather than recover, so recovery-equipment hydrocarbon compatibility is moot.

(An alternative architecture was briefly considered: keep the factory finger-plate evaporator wired in-circuit and surround it with an FDM-printed pressure vessel — PA6-CF structural shell lined with TPU as the pressure boundary, with the cold fingers becoming the vessel's internal geometry. Sealed loop, no vent or recharge. Not in active development; the custom-coil path is what's being built. Full pre-removal description preserved at the `archive-plan-b-2` git tag — `git show archive-plan-b-2:hardware/harvested/ice-maker/README.md` for the side-by-side discussion.)

---

## Unit A — Generic countertop, 8 cubes / 6 min

- ASIN: **B0F42MT8JX**
- Price: $63.80
- Rated output: 26 lb/day
- First teardown: 2026-04-17

### Refrigerant

**R600a (isobutane).** Flammable. Charge is small (well under the 150 g UL 60335-2-89 limit for small appliances; factory label will list the exact mass). Brazing anywhere in the sealed loop requires the charge to be vented first — do not heat a pressurized R600a circuit.

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

Finned-tube forced-convection condenser with its own fan shroud (fan not yet separated in photos). Standard wire-and-plate construction. Reuse as-is — mount against one side wall of the appliance enclosure with the fan's native flow axis crossing the enclosure side-to-side (intake grille on one side face, exhaust grille on the opposite side face). The point of this orientation is that the donor fan + shroud are doing exactly the job they were designed for — no airflow redirection, no shared intake/exhaust face — per the enclosure layout in `future.md`.

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

### Evaporator cold plate

A stainless-finger cold plate, purpose-built for ice-cube formation. **Discarded** — cut out during re-piping; replaced with the custom copper coil wound around the SS carbonator. The suction-side connection point moves to the new coil.

### Powering and control (AC wiring)

The compressor is a single-phase AC hermetic with a **combined PTC start relay + overload protector** clipped to its terminal block. External connection is **two wires (black + white) coming out of that module**, not directly from the compressor pins. Believed to be **110–120 VAC** based on US market origin and the 110 V rating on the hot-gas bypass solenoid — verify the compressor nameplate before energizing.

For bench testing, plug into standard 120 VAC through an **inline fuse** (5 A fast-blow is comfortable for expected ~1 A running + LRA inrush). A Kill-A-Watt inline lets you observe the LRA spike, steady running draw, and confirm the compressor is doing real work rather than just humming.

Safety:
- **R600a is flammable.** Do not energize after physical damage, near open flame, or if a butane smell is present near the compressor. The factory loop is sealed from the factory, so there's no leak risk during teardown *inspection* — leak risk only appears once the loop is opened for re-piping.
- **Minimum off-time of 3 minutes** between power-off and power-on is a hard rule. The high-side pressure has to bleed through the capillary tube and equalize with the low side before restart, or the motor stalls against head pressure until the overload trips. Repeated hot-restart is a textbook way to burn out a hermetic compressor.

For ESP32 control:
- **Reserved GPIO: pin 14** on the main ESP32-DevKitC-32E. Not a strap pin, not input-only, not reserved for flash/PSRAM. See `hardware/wiring/esp32-pinout.mmd` for the full pin map.
- **Switching element: Teyleten 3.3 V opto-isolated relay module** (10 A @ 250 VAC, ASIN B07XGZSYJV). ESP32 GPIO drives the input pin directly — 3.3 V coil side, opto-coupled, mechanical contact on the AC hot leg. ~$2.60/unit at 5-pack pricing. Audibly clicks, finite cycle life, but at this duty (minutes-per-cycle, 3-minute minimum off-time enforced in firmware) a 100,000-cycle relay lasts decades. The same relay model is used a second time per appliance to gate 12 V to the SeaFlo diaphragm pump (see `hardware/wiring/power.mmd` and `hardware/bom.md` §5).
- A 25 A solid-state relay (Fotek SSR-25 DA / Crydom class, zero-crossing, also opto-isolated) was the original plan but was rejected: at ~1 A running current the SSR's required heatsink and ~5× price weren't justified, and the cycle-life advantage doesn't matter when the duty cycle is already minutes-long.
- **Firmware must enforce the 3-minute minimum-off-time** as a guard — the relay will switch every loop iteration if told to, and that will destroy the compressor within days. Wrap the ON/OFF call behind a "can I switch right now?" check against the last-transition timestamp. A hysteresis band around the temperature setpoint (e.g., ±1 °C) is needed for the same reason — you want long cycles, not rapid thrash.

### Summary — keep vs discard for this unit

| Part | Disposition |
|---|---|
| Compressor | Keep |
| Condenser + fan | Keep |
| Capillary tube (bonded to suction line) | Keep — do not separate |
| Filter-drier | Keep in place; replace with fresh drier before recharge if the loop is opened |
| Process tube | Keep — vent/recharge access point |
| Hot-gas bypass solenoid | Discard / bypass |
| Evaporator finger plate | Discard (replaced by custom copper coil around the SS carbonator) |
| Thermostat / harvest-cycle controller | Discard (custom ESP32-S3 firmware replaces it) |

### Open items

- Factory refrigerant charge mass (read from the nameplate once fully exposed)
- Compressor rated cooling capacity in W — confirm against expected load of holding ~1.5 L of carbonated water at 2 °C against cabinet-ambient
- Physical dimensions of compressor + condenser pair, for enclosure layout
- Decide whether to save photos to `hardware/harvested/ice-maker/unit-a-b0f42mt8jx/raw-images/` alongside this doc

---

## Unit B — Frigidaire EFIC117-SS

- ASIN: **B07PCZKG94**
- Price: $78.70
- Rated output: 26 lb/day
- Teardown: pending

To be filled in after teardown.
