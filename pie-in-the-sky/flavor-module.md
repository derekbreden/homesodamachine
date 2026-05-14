# Flavor Module — an external satellite unit

*Pie-in-the-sky, not roadmap. Captured 2026-05-14.*

A small external appliance that sits next to the main Kitchen Edition or Shop Edition. It adds **a second dispense point** to the household — its own faucet, its own through-counter penetration, its own flavor-select and display — pouring **four flavors** at that faucet. Two of the four come from new reservoirs that live inside the module; two are routed from the main unit's existing reservoirs. Net new flavors added to the household: two. Net new faucets added to the household: one.

The module does not carbonate. It does not connect to the customer's plumbing or to the customer's CO2 tank. It has exactly two physical interfaces: an umbilical to the main unit, and the flavor-line + carbonated-water bundle that goes up through the counter to its own faucet.

## What the module physically contains

- **Two new flavor reservoirs**, 1 L each, in the same printed hard-reservoir architecture as the main unit's two. PTFE-membrane vented caps, low outlet sump, hopper fill from above.
- **A small refrigerated chamber** holding those two reservoirs at 8–15 °C. The architecture mirrors the main unit's cold core at smaller scale: foam-shell wrap, evaporator coil, harvested compressor / condenser / fan / cap-tube / drier. Setpoint is warmer than the main unit's (no carbonation to keep cold here — just syrup storage), which opens a possible Peltier path as a quieter alternative to the donor-compressor architecture. Side-to-side airflow same as the main unit.
- **Two Kamoer peristaltic pumps** (one per new reservoir), in the same replaceable pump-cartridge pattern as the main unit. Tool-free swap.
- **A top hopper** sized to accept a SodaStream-pour, routed through solenoid-selected valves to the two new reservoirs. Customer fills the two module-side flavors through the module's own hopper, independent of the main unit's hopper.
- **A valve manifold** extension of the main unit's pattern, generalized for the four-line faucet — flavor select, clean-cycle routing, source-selection for hopper fill.
- **Its own electronics shelf** — local microcontroller, MCP23017 expander, ULN2803A drivers, motor driver, 12 V regulation. Subordinate to the main unit's ESP32 for high-level control; runs its own refrigeration cycle and pump timing locally.
- **A small enclosure**, roughly half to two-thirds the volume of the main appliance. No carbonator means no pressure vessel, no hydro-test, no PRV, no level reeds, no WR1110 regulator, no ASSE 1022 backflow preventer, no diaphragm pump, no water-side check valves. The cabinet is meaningfully smaller and cheaper than the main appliance's.

## The new dispense point

A second faucet penetration in the customer's countertop, alongside the main unit's faucet at the back of the sink (or wherever the customer chose to install it). The new faucet is the same PET-CF Touch-Flo design as the main unit's faucet, with the nozzle internal geometry extended to inject **four flavor lines** rather than two. Carbonated water enters the faucet's inlet stub and mixes with flavor at the nozzle, the same way the main unit's faucet works.

Companion through-counter elements at the module's faucet:

- **A second KRAUS-class air switch** for four-flavor select (or a different selector — the module is wide enough at four flavors that a small button panel may be the more natural UI).
- **A second RP2040 round display** showing the active flavor's logo at this faucet.

The household ends up with two faucets, each pouring its own selection. The main faucet pours its native two flavors. The module's faucet pours four — the same two as main (routed through the umbilical), plus two new ones unique to the module.

## The umbilical

A single multi-conduit bundle running from the rear of the main unit to the rear of the module. Carries everything the module needs from the main unit and routes back nothing:

- **12 V power**, tapped off the main unit's Mean Well PSU bus. The module does not have its own AC inlet; it is electrically subordinate to the main unit. One C14 on the household, not two.
- **A control / sensor bus** between the main unit's ESP32 and the module's local microcontroller. Dispense triggers, flavor select state, telemetry, fault propagation.
- **Chilled carbonated water**, T'd off the main unit's carbonator outlet. This is the source of soda at the module's faucet — the main unit's carbonator services both faucets.
- **Tap water**, T'd off the main unit's water inlet downstream of the Multiplex 19-0897 ASSE 1022 backflow preventer. Used by the module's clean cycle for all four of its faucet lines. Because the water has already passed through main's backflow protection, the module needs no ASSE 1022 of its own — a meaningful BOM and complexity saving.
- **Two flavor concentrate lines**, T'd off the main unit's two peristaltic-pump outlets. When the customer selects one of the main's two flavors at the module's faucet, main's pump fires and concentrate flows down the umbilical to inject at the module's nozzle. No duplicate syrup, no duplicate reservoir, no duplicate pump — those flavors physically live in the main unit and are reachable from either faucet.

The umbilical is a fat bundle but its endpoints are short: out the back of main, into the back of module, both under the counter. Route once at install, no service action expected after.

## Plumbing pattern at a glance

```
   customer's water        Lite-Edition-style hopper
   + CO2                          │
        │                         ▼
        ▼                ┌────────────────┐
   ┌──────────┐          │ MODULE         │
   │ MAIN     ├──────────┤  + 2 new       │
   │ + 2      │ umbilical│    reservoirs  │
   │   flavors│ (power,  │  + refrig only │
   │ + carb.  │  signal, │    on those 2  │
   │ + refrig │  carb H2O│                │
   │          │  tap H2O,│  + new PET-CF  │
   │          │  2 conc. │    faucet      │
   │          │  lines)  │    (4-line)    │
   └────┬─────┘          └──────┬─────────┘
        │                       │
        ▼                       ▼
    main faucet            module faucet
    (2 flavors)            (4 flavors:
                            2 from main +
                            2 module-native)
```

## What the customer sees

Two faucets in the kitchen. The main faucet pours the household's two everyday flavors. The module's faucet pours four — those same two plus two more. Selecting one of the main flavors at the module's faucet works exactly as selecting it at the main faucet does; under the hood, main's pump just runs concentrate down the umbilical instead of straight up to main's nozzle.

From the customer's vantage the module is *one more faucet, two more flavors*. The architectural fact that two of the module's faucet lines are physically piped from main is implementation detail.

## Rough BOM (per module)

| Item | Approx |
|---|---:|
| Harvested refrigeration loop (small donor, 2-reservoir scale) — or Peltier alternative | $80 |
| Foam shell + insulation + 2 reservoirs + caps + membranes | $50 |
| Kamoer peristaltic pumps (×2) | $65 |
| Beduan solenoids (~8 for the module-side manifold) | $80 |
| Hopper + cabinet print | $30 |
| Electronics (local µC, MCP23017, ULN2803A, motor driver, regs) | $60 |
| New PET-CF faucet (extended nozzle internal geometry, 4-line injection) | $40 |
| SS under-counter plate | $4 |
| RP2040 round display | $24 |
| KRAUS air switch (or 4-button panel) | $40 |
| Compressor shroud cut part (if compressor path) | $10 |
| Umbilical — multi-conductor cable + tubing bundle + strain reliefs + connector at each end | $50 |
| Wiring, fittings, fasteners, John Guest hardware | $30 |
| **Module total** | **~$560** |

Pre-margin module cost around $560. A Founder Edition module price of **~$2,500**, or a Standard Edition price of **~$1,800** once batch production is reached, sits naturally in the same pricing logic as the main appliance.

## What makes this work cleanly

**The hard part of the main unit doesn't get duplicated.** Carbonator vessel, 90 PSI pressure service, hydro-test, sparge stone, level reeds, PRV, WR1110 regulator, ASSE 1022 backflow preventer, diaphragm pump, hydrocarbon-refrigerant fire enclosure to UL 60335-2-89 — none of that lives in the module. The module is the easy half of the main unit, at smaller scale.

**The household keeps one CO2 tank, one water tap, one wall outlet.** The customer's install action is "plug umbilical from main into module, run module's faucet bundle up through the counter, mount the second faucet." No second CO2 regulator. No second water tee. No second AC outlet. The plumbing-and-electrical footprint of adding the module is the umbilical and the one new countertop penetration.

**The two-flavor objection is answered without compromising the main unit.** Going to four flavors on the main unit means a bigger main enclosure and a more crowded manifold there. Going to four flavors at a second faucet via a module leaves the main unit exactly as designed and shifts the complexity into a separate appliance that only ships when a customer wants it.

**Independent failure domains for the new flavor side.** If the module's small refrigeration loop fails, the main unit still pours its two flavors at its faucet. If the main unit's carbonator fails, the module's reservoirs stay cold but its faucet stops pouring (no carbonated water source) — same blast radius as the main unit's faucet stopping, which is acceptable since the carbonator is the upstream dependency in either case.

**The upsell narrative is clean.** Existing owner, year into using the main unit, wants a wider flavor selection or a second dispense point in the kitchen island or the bar nook. Buys the module. Plugs it in. Fills two new reservoirs from the module's hopper. Now their household has two faucets and four flavors, and they bought from a company they already trust.

## What's worth doing next on this

Nothing immediately — the Kitchen Edition ships first. Light constraints to carry through main-unit design so the module remains buildable without disturbing the main unit later:

1. **Firmware should treat flavor count and faucet count as parameters, not constants.** N=2 flavors, M=1 faucet today; N=4, M=2 with module. Same firmware, same UI grammar.
2. **One unused UART or I2C bus on the main ESP32 should stay reserved** for the module's control bus. No physical connector today, no wiring, no BOM cost — just leave the bus unspoken-for.
3. **The main unit's two flavor-pump outlets should remain branchable** without redesign — i.e. the pump-to-faucet plumbing should not become so geometrically committed that adding a T off the pump output is a redesign.

None of those add cost or complexity to the main unit. They just leave a door unblocked.
