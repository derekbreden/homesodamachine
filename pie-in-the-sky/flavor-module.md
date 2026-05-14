# Flavor Module — an external satellite unit

*Pie-in-the-sky, not roadmap. Captured 2026-05-14.*

A small external appliance that sits next to the main Kitchen Edition or Shop Edition and adds **four more flavors to the existing faucet**. It is not a second machine. It carbonates nothing, dispenses no water, and connects to no plumbing. It is, fundamentally, a refrigerated four-reservoir flavor cartridge with its own pumps and its own hopper, wired into the main unit and tapped into the dispense point — and that's the whole architecture.

The main unit still does the hard part: water, CO2, carbonation, refrigeration of the carbonator, the dispense lever, the flow sensor. The module just provides four additional chilled flavor lines that inject at the nozzle alongside the main unit's two existing flavor lines. Six flavors total through one faucet.

## What the module is

- **Four flavor reservoirs** in the same architecture as the main unit's two — printed hard reservoirs, vented through PTFE membranes on their caps, sized roughly 1 L each.
- **Refrigerated to 8–15 °C** in its own enclosure. This is the only refrigeration in the module: it keeps the syrup cold. There is no carbonator, no pressure vessel, no service-temperature target, no freeze-protect cutout. It's a small AC refrigeration loop holding a small insulated chamber at flavor-storage temperature. The donor architecture (harvested compressor + condenser + fan + cap-tube + drier from a countertop appliance) and the foam-shell cold core pattern transfer directly from the main unit, just at smaller scale and warmer setpoint. Side-to-side airflow same as the main unit.
- **Four peristaltic pumps** (Kamoer KPHM400 — same part as the main unit) on a replaceable cartridge identical in pattern to the main unit's pump cartridge. Tool-free swap when the silicone tubing wears.
- **A flavor hopper** on top of the module — same SodaStream-pour-sized funnel architecture as the main unit, but routed via solenoid-selected paths to four reservoirs instead of two. Customer fills the module's flavors through the module's own hopper, independent of the main unit's hopper. No need to share or reroute.
- **A small enclosure**, possibly half to two-thirds the volume of the main unit. The compressor floor, side airflow path, electronics shelf, and pump cartridge access door pattern all transfer. Front face has no faucet, no dispense, no proximity sensor — it's a quiet appliance whose only user-facing surfaces are the top hopper and the cartridge access door.

## What it connects to

Exactly two things. No water inlet. No CO2 inlet. No drain. No tee fittings in the customer's plumbing.

**1. The main unit.** One umbilical carries everything the module needs from the main unit and everything the main unit needs to know about the module:

- 12 V power tapped off the main unit's Mean Well PSU bus, sized for the module's compressor (worst-case ~1 A inrush) plus its peristaltic pumps and solenoids. The module does not have its own wall plug — it is electrically a subordinate to the main unit, which is the cleanest way to keep both appliances on a single AC topology and a single C14 inlet for the household.
- A control / sensor bus from the main unit's ESP32 to the module's local microcontroller. The main unit knows when the customer pulls the lever and which flavor is selected; the module fires the right pump on cue. The flow sensor is in the main unit — the module just pumps when told to, for the duration told to.
- Compressor cycle control either lives in the module's own controller (with its own thermistor on the small evaporator) or is reported up to the main unit's app for unified visibility. Either works; either is invisible to the customer.

**2. The dispense point.** Four 1/4" LLDPE flavor lines run from the module's pump cartridge to the dispense nozzle, joining the main unit's two existing flavor injection points at the same nozzle. The nozzle architecture in the current Kitchen Edition already injects flavor alongside carbonated water at the dispense point ("injected at the dispense nozzle alongside the carbonated water," `hardware/future.md` "Flavor subsystem"); going from two injection ports to six is a parts-count change at the nozzle, not an architectural one.

That's it. Module to main unit: one cable. Module to dispense point: one bundle of four flavor lines.

## Why this is genuinely good

**It scales the flavor count without scaling the hard parts.** The hard part of the main appliance is the carbonator: 90 PSI pressure vessel, hydro-testing, sparging, level sensing, refrigeration loop tied to carbonation setpoint, dual backflow protection, the WR1110 secondary regulator, the SV-125 PRV, the welding and passivation work, the UL 60335-2-89 fire enclosure around the compressor. None of that gets duplicated in the module. The module is the easy half of the main appliance, by itself.

**It reuses what already works.** Foam-shell cold core, harvested-ice-maker refrigeration loop, side-to-side airflow, Kamoer peristaltic pumps, John Guest fittings and bulkheads, Beduan solenoids, MCP23017 expander, printed reservoirs, hopper architecture, pump cartridge swap pattern. Same vendors, same supply chain, same assembly procedures. From a manufacturing-process standpoint, the module is the same build as the main unit minus the carbonator subsystem.

**It is the cleanest possible upsell.** The customer has the main unit and loves it. They want more flavors. They buy a module. They place it next to or under the main unit, plug one cable into the main unit's auxiliary port, run four flavor lines up to their existing faucet (re-using the faucet's existing nozzle assembly or a slightly extended one), prime four new reservoirs from the module's hopper, and now their faucet pours six flavors. No second faucet penetration in the countertop. No second air switch. No second display. The household has one tap and one ritual — and the ritual got better.

**It solves the two-flavor objection without compromising the main unit.** Going to four flavors on the main unit means a bigger enclosure, more manifold complexity, a more crowded electronics shelf, and design rework of a vessel architecture that is currently well-understood and converging. Or you can leave the main unit exactly as it is, and ship a $400-ish add-on that quadruples flavor capacity. The economics overwhelmingly favor the add-on.

**Refrigeration architecture has room to be quieter.** The module doesn't need to hit 2 °C — it needs to hit 10 °C. That opens a path the main unit can't take: a thermoelectric (Peltier) cold plate sized for 30-40 W of heat lift, no compressor, no refrigerant, no UL 60335-2-89 hydrocarbon shroud, no piercing-valve recharge procedure, near-silent operation. The donor-compressor path still works as a fallback if Peltier capacity is insufficient. Either way the module is much quieter than the main unit. The bar shelf next to the dispenser hears it less than the fridge across the room.

**Independent failure domains for the flavor side.** If the module's compressor fails, the main unit still pours its two base flavors. If the main unit's carbonator fails, the module's reservoirs stay cold and the household keeps the syrup until the carbonator's back. Neither failure cascades.

## What the customer sees

Two appliances side by side under the counter or on the shelf. One faucet on the countertop. One air switch — or, more naturally, a richer six-flavor selector that the main unit now drives (the existing KRAUS air switch was already a single-pole rotary; the upgrade path to a six-position selector or a small flavor-select panel is a UI design problem, not a plumbing problem). The RP2040 round display shows the active flavor's logo regardless of which appliance the syrup came from.

From the customer's vantage, the module is just *more flavors on the same faucet*. The fact that the syrup came from a second physical appliance is implementation detail.

## Form factor variants

- **Companion under-counter module.** Mounted in the adjacent cabinet bay or sharing the under-sink bay with the main unit. Invisible. Same install-mood as the main Kitchen Edition.
- **Companion countertop module.** Sits on the bar shelf next to a Shop Edition main unit. Same Shop-Edition front-face aesthetic minus the dispense field — just a clean cabinet face with a top hopper and a cartridge access door. Visually it reads as "second piece of bar equipment," which is exactly right for that audience.

Either variant uses the same internals; only the cabinet outside differs. Same fork logic as Kitchen vs Shop on the main unit.

## Rough BOM hit (per module, not per appliance)

| Item | Approx |
|---|---:|
| Harvested refrigeration (or Peltier) loop | $80–110 |
| Foam shell + insulation + reservoirs (4×) | $80 |
| Kamoer peristaltic pumps (4×) | $130 |
| Beduan solenoids (~12 for the 4-reservoir manifold) | $115 |
| Hopper + cabinet print | $40 |
| Electronics (local µC, MCP23017, ULN2803A, driver, regs, umbilical connector) | $60 |
| Wiring, fittings, fasteners, John Guest hardware | $40 |
| Enclosure cut parts (compressor shroud if compressor path) | $10 |
| **Module total** | **~$555–585** |

Pre-margin module cost lands somewhere around $550-600. A Founder Edition module price of ~$2,500 — or a Standard Edition price of ~$1,800 once batch production is reached — is honest pricing for the value delivered and consistent with the main unit's pricing logic. Customers buy this *after* the main unit, after the trust is established, after they already know they love the product. The upsell narrative practically writes itself.

## What's worth doing next on this

Nothing immediately. The Kitchen Edition ships first. The discipline is to *not* let the module's existence influence the main unit's first 10 builds — no "module-ready" ports, no shared firmware contract, no BOM additions on Kitchen Edition that exist only to anticipate the module. Three light constraints carried in the back of mind during main-unit design:

1. **The main unit's firmware should treat flavor count as a parameter, not a constant.** N=2 today, N=6 with module. Same firmware, same UI grammar, just a configuration value.
2. **The main unit's ESP32 should have one unused UART or I2C bus reserved for an auxiliary device.** No physical connector, no wiring — just a software-level acknowledgment that this bus is unspoken-for and available later.
3. **The dispense nozzle's injection geometry should not assume exactly two flavor lines arrive at it.** A four-line injection collar and a six-line injection collar are different printed parts, swappable later. The plumbing path from the manifold to the nozzle should be a soft assumption, not a baked-in geometry.

None of these add cost or complexity to the main unit today. They just leave a door unblocked.
