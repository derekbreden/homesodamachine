# Antarctic Star HZB-12/Q donor

The black [Antarctic Star HZB-12/Q, ASIN B0F8NKJD6X](https://www.amazon.com/dp/B0F8NKJD6X) supplies the compressor, condenser and fan, capillary, suction-line heat exchanger and filter-drier. The delivered machine's labels and harvest measurements establish the exact compressor, connections and mount fit. The teardown notes below describe the HZB-12/Q that supplies the current CAD reference. [Reference teardown record](https://github.com/derekbreden/homesodamachine/blob/b9dde41eabe7e8a8d633337d70f2eb444ea979c4/hardware/ice-maker-teardown.md) · [Current purchase](/hardware/ledger/purchases.md#6-refrigeration) · [Build procedure](/hardware/assembly/refrigerant-loop.md)

## Cold core architecture

The wrapped copper evaporator cools the fabricated stainless carbonator. Remove the household donor's R-600a charge outdoors and clear residual gas before opening the circuit at the old evaporator's suction and capillary connections. Preserve the factory drier and the bonded heat exchanger through the conversion, then evacuate and recharge the new circuit.

The hot-gas bypass solenoid is deleted.

EPA's R-600a Section 608 exemption applies to specified end-uses. The project's
residential household design basis and its scope are recorded in
[`business/regulatory.md`](/business/regulatory.md). It is a reasoned classification,
not an individual EPA determination; the service route still addresses the actual
appliance and refrigerant handling conditions. Equipment suitability for
flammable refrigerants must be checked against its manufacturer's instructions;
an end-use venting exemption is not a qualification of the pump, manifold or other
service equipment.

---

### Refrigerant

Use the U.S. HZB-12/Q refrigerant rating in Intertek's constructional report as the baseline in the [bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf). Derek reports the inspected nameplate gives no charge mass. The report permits several compressors under this model, so check the actual compressor plate, fan and connections against the reference measurements. [Intertek constructional report, ratings](https://device.report/m/ba17ebc69382c7509ea70d4e77dfa9bc9ae002417ea8c0af0e913a8b8f89de70)

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

This matches standard R600a small-appliance practice.

### Compressor

- Manufacturer: NingBo Anuodan Machinery Co., Ltd (sticker brand: HuaJun)
- Model: **HD48Y11A** (the "A" is a sub-variant suffix on the sticker)
- 110-120 V ~ 60 Hz, 1 PH
- Hermetic reciprocating, thermally protected, UL / CSM listed
- Body cast-stamp: **48.5-2** (mid-housing). **Not** a charge mass. Most likely a compressor displacement or capacity-index code with sub-variant suffix; not decoded.
- Cooling capacity ~90–120 W range (estimated from cube-formation throughput).

### Condenser

Finned-tube forced-convection condenser with its own fan shroud (fan not yet separated in photos). Plate-fin construction: thin aluminum fins on a copper refrigerant tube. Reuse as-is — mount against one side wall of the appliance enclosure with the fan's native flow axis crossing the enclosure side-to-side (intake grille on one side face, exhaust grille on the opposite side face) per the enclosure layout in `hardware/README.md` "Enclosure (back to front)".

### Filter-drier

A fat copper cylinder sits between the condenser outlet and the capillary tube inlet. It holds a molecular-sieve desiccant charge that traps residual moisture and debris.

**Disposition: keep in service.** Keep the factory drier, its brazed-on capillary, the capillary helix and the bonded suction-line heat exchanger together. Protect the drier from moisture throughout the open work. [Refrigerant-loop procedure](/hardware/assembly/refrigerant-loop.md)

Label on this unit's drier:

- `8.05.08.044` (leading digit ambiguous — could be `0`)
- `60-130-05` — almost certainly the drier's model / part number. Useful if sourcing a drop-in replacement from the same supply chain; not confidently decodable without the manufacturer.
- `20251107 A-1` — manufacturing date code, 2025-11-07, line/shift A-1.
- Small stylized logo at left (manufacturer mark, not identified).

**Desiccant preservation.** Protect the drier from atmospheric moisture during open work. Keep the assembly under the dry-inert service method and prove flow through each segment before heating. The refrigerant-loop procedure owns the open-work setup.

### Capillary tube + suction-line heat exchanger

Downstream of the filter-drier, a hair-bore **capillary tube** meters refrigerant. Its inlet state, bore, length and the pressure difference across it determine the flow. Running pressures depend on water load, airflow and refrigerant inventory.

Physical path through this unit, start to finish:

1. **Exits the filter-drier** (cap tube is brazed into the drier's outlet end).
2. **Runs bonded alongside the suction line** for most of its length — this is the passive internal heat exchanger. Cold return gas from the evaporator subcools the liquid refrigerant before it flashes, increasing effective capacity at zero cost.
3. **Coils up in a short helix** right before the evaporator inlet — packaging, to fit the required length into a small area and manage any final pressure trim.
4. **Enters the evaporator.**

Keep the bonded cap-tube-plus-suction-line pair intact when re-piping. The helical coil at the evaporator end is preserved as-is; if total cap length changes (e.g., the evaporator is relocated when swapping the cold plate for the carbonator coil), a refrigeration tech recalculates cap length for the new load.

### Process tube (the "dead-end" copper stub)

A short copper tube with a pinched-and-brazed tip sticks out of the compressor body. Use the process tube for charge removal, evacuation and recharge through qualified low-side access. [Refrigerant-loop procedure](/hardware/assembly/refrigerant-loop.md)

### Hot-gas bypass solenoid (DISCARD for our use)

A small AC solenoid valve is teed into the refrigerant circuit:

- Label: **SOLENOID VALVE — AC 110V 50/60Hz 4/4.5 W — TIANHAQ 25.10.17**
- Function in ice maker: during the harvest cycle, this valve opens and routes hot compressor discharge gas directly into the evaporator (bypassing the condenser and capillary tube), warming the cold fingers so formed cubes release and drop.
- Remove the valve, branch tubing and tee during re-piping.

### Evaporator cold plate

A stainless-finger cold plate, purpose-built for ice-cube formation. **Discarded** — cut out during re-piping; replaced with the custom copper coil wound around the SS carbonator. The suction-side connection point moves to the new coil.

### Powering and control (AC wiring)

The reference compressor is a single-phase AC hermetic with a **combined PTC start relay and overload protector** clipped to its terminal block. Retain the moulded power-box cover and its original retention. The reference teardown found black and white external pigtails. Measure and record the delivered donor's lead function, termination, usable length and earth landing before preparing the mating harness.

For the first start, use the protected appliance feed and the normal warm-wall call after the off guard. The P4400 records standby and running readings at that feed. Follow the [bench guide](/hardware/refrigeration-guide/refrigeration-guide.pdf).

Safety:
- **R600a is flammable.** Do not energize after physical damage, near open flame, or if a butane smell is present near the compressor. The factory loop is sealed from the factory, so there's no leak risk during teardown *inspection* — leak risk only appears once the loop is opened for re-piping.
- **Minimum off-time of 3 minutes** between power-off and power-on is a hard rule. The high-side pressure has to bleed through the capillary tube and equalize with the low side before restart, or the motor stalls against head pressure until the overload trips.

For ESP32 control:
- **Reserved GPIO: IO19** (Relay #1) on the base ESP32 (the main board's WROOM, reaching the relay through the on-board gas-interlock gate). Not a strap pin, not input-only, not reserved for flash/PSRAM. See `hardware/wiring/esp32-pinout.mmd` for the full pin map.
- **Switching element: Teyleten 3.3 V opto-isolated relay module** (10 A @ 250 VAC, ASIN B07XGZSYJV). ESP32 GPIO drives the input pin directly — 3.3 V coil side, opto-coupled, mechanical contact on the AC hot leg. ~$2.60/unit at 5-pack pricing. The same relay model gates 12 V to the G Ganen diaphragm pump (see `hardware/wiring/power.mmd` and `hardware/ledger/bom.md` §5).
- **Firmware enforces the 3-minute minimum-off-time** as a guard. Wrap the ON/OFF call behind a "can I switch right now?" check against the last-transition timestamp. A hysteresis band around the temperature setpoint (e.g., ±1 °C) keeps cycles long.

### Summary — keep vs discard for this unit

| Part | Disposition |
|---|---|
| Compressor | Keep |
| Condenser + fan | Keep |
| Capillary tube (bonded to suction line) | Keep — do not separate |
| Filter-drier | Keep the protected upstream assembly through open work per the [refrigerant-loop procedure](/hardware/assembly/refrigerant-loop.md) |
| Process tube | Keep for qualified low-side service access and final closure |
| Hot-gas bypass solenoid | Remove with its branch and tee |
| Evaporator finger plate | Discard (replaced by custom copper coil around the SS carbonator) |
| Thermostat / harvest-cycle controller | Discard (custom ESP32-S3 firmware replaces it) |
