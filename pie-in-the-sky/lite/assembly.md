# Lite Edition Assembly

*Pie-in-the-sky, not roadmap — a first-pass build procedure for the [Lite Edition](/pie-in-the-sky/lite/README.md) flavor-injection module. Companion to [`README.md`](/pie-in-the-sky/lite/README.md) (what the Lite is and the customer experience) and [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md) (per-unit parts).*

The Lite Edition is the flavor half of the main appliance wrapped in a small transparent cabinet — two collapsible flavor bags, two peristaltic pumps, a valve manifold, a faucet, the dispense electronics, and the enclosure that holds them. It does not carbonate, refrigerate, or store water; cold carbonated water comes from the customer's paired Lillium-class carbonator. So this procedure has no pressure vessel, no hydro-test, no refrigerant loop, and no foam-pour cold core — roughly half the [main-appliance assembly set](/hardware/assembly/) does not apply.

## Scope

In: the printed PETG parts ([enclosure shell](/pie-in-the-sky/lite/enclosure/), [reservoir-pockets bag cradle](/pie-in-the-sky/lite/printed-parts/reservoir-pockets/), [funnel / hopper](/pie-in-the-sky/lite/printed-parts/funnel/), the [faucet stack](/hardware/printed-parts/faucet/), and the [pump cases](/hardware/printed-parts/flavor/pump-case/)); the off-the-shelf flavor parts (two Platypus bags, two Kamoer KPHM400 pumps, the manifold valves + John Guest fittings + tubing); the faucet, air switch, and round display; the electronics family (ESP32, MCP23017 expander, ULN2803A drivers, motor driver, 12 V supply); and one 1/8" stainless bag-hanger rod.

Out: a finished Lite Edition unit, ready for under-sink install and pairing to a Lillium-class carbonator.

Not in scope: the Lillium carbonator itself (resold, not manufactured — [`README.md`](/pie-in-the-sky/lite/README.md) "What the customer buys"); the customer-side install, prime, and refill (manual and watched — [`README.md`](/pie-in-the-sky/lite/README.md) "Setup, priming, and refill"); and every carbonation / refrigeration subsystem the Lite omits ([`README.md`](/pie-in-the-sky/lite/README.md) "What the Lite Edition does not contain").

## Inputs per unit

Per-unit parts and cost live in [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md). The build-specific items, with the printed parts that wrap them:

| Item | Source | Notes |
|---|---|---|
| Enclosure shell (printed PETG) | [`enclosure/`](/pie-in-the-sky/lite/enclosure/) | Six-wall box; lid hole clears the funnel inlet |
| Reservoir-pockets bag cradle (printed PETG) | [`reservoir-pockets/`](/pie-in-the-sky/lite/printed-parts/reservoir-pockets/) | Two bag pockets + a rod-hang channel |
| Funnel / hopper (printed PETG) | [`funnel/`](/pie-in-the-sky/lite/printed-parts/funnel/) | Square-to-round pour-through guide to V-B |
| Faucet stack (printed PET-CF) | [`faucet/touch-flo-shell/`](/hardware/printed-parts/faucet/touch-flo-shell/) | Touch-Flo shell + plate + gasket + o-ring |
| Pump cases (printed) | [`flavor/pump-case/`](/hardware/printed-parts/flavor/pump-case/) | Houses the Kamoer pumps |
| 1/8" stainless bag-hanger rod, [158 mm](ROD_LENGTH) | Same stock as the carbonator float rod (Tandefio B0CY4DWJFQ) | Threads both bags' top loops |
| Platypus Hoser 1 L bag × 2 | [B002OYMRS8](https://www.amazon.com/dp/B002OYMRS8) | Spout-down flavor reservoirs ([`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md)) |
| Kamoer KPHM400 pump × 2 | [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md) | Valve-locked peristaltic pumps |
| Manifold valves + fittings + tubing | [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md) | Beduan solenoids, John Guest PP-series, clear PVC + LLDPE |

## Procedure

### 1. Print and prep the parts

Print the transparent-PETG parts — enclosure shell, reservoir-pockets cradle, funnel — plus the PET-CF faucet stack and the pump cases. Deburr the ⌀6.5 mm tube exits and the rod-hang channel so the bag spouts and the hanger rod seat clean.

### 2. Hang the bag rod and load the bags

Cut one 1/8" stainless rod to [158 mm](ROD_LENGTH) — tip to tip, the same stock as the carbonator float rod. Thread it through both Platypus bags' centered top loops, slide the rod in from the cradle's +X (rear) doorway carrying both bags, roll it down the flared ramp, and let it seat in the center rest pocket against the −X end stop. The bags' own weight holds it down, and the 2 mm plug past each rod-end boss captures it along its own axis so it cannot slide out; the channel stays open at +X for insertion and removal. Route each bag's spout down to the ⌀6.5 mm exit low in the cradle's −X (front) wall.

Unlike the carbonator and Kitchen-reservoir float rods, this is a **tool-free hang** — no weld, no boss bore — so the same operation is the consumer-serviceable bag swap (load through the rear doorway). Geometry: [`reservoir-pockets/README.md`](/pie-in-the-sky/lite/printed-parts/reservoir-pockets/README.md).

### 3. Build and stack the valve manifold

Assemble the four manifold trays — source-select, bag-circuit, bib-gate, nozzle-gate — the same tray assemblies as the Kitchen build ([`valve-manifold/`](/hardware/printed-parts/valve-manifold/)), populated with the Beduan solenoids and John Guest dividers / tees / stem-barbs from [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md). Stack bag-circuit / bib-gate / nozzle-gate against the cradle's −X face at their designed tray pitch, and stand source-select vertical against the +Y face, per [`_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py).

### 4. Mount the pumps

Seat the two Kamoer KPHM400 pumps in their printed cases, stacked end to end in front of (−X of) the tray stack, tube barbs facing out into the open +Y space, per [`_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py).

### 5. Plumb the flavor circuit

Run the clear-PVC and LLDPE lines per [`fluid-topology-manifold.mmd`](/pie-in-the-sky/lite/fluid-topology-manifold.mmd): bag spouts → manifold, the pump loops, hopper spout → V-B, the optional bag-in-box inputs through the 3/8"→1/4" reducers, the Lillium clean-water feed through the flow-control bulkhead (throttled to the manifold's low working pressure), and the two flavor lines up to the faucet nozzle. The visible clear runs are the "green" segments in the topology; the short rigid jumpers between push-connect fittings are the grey LLDPE hops.

### 6. Mount the funnel

Seat the funnel on the front (−X), inlet flush with the enclosure lid, spout reaching back to V-B on source-select. Geometry: [`funnel/README.md`](/pie-in-the-sky/lite/printed-parts/funnel/README.md).

### 7. Wire the electronics

Mount the ESP32, MCP23017 expander, ULN2803A drivers, motor driver, and 12 V supply, and wire them to the two pumps, the manifold solenoids, the round display, and the air switch — the same parts family and dispense logic as the main appliance, minus every sensor the Lite omits (no level reeds, no moisture telltale). The electronics-shelf housing is undesigned (see Open items).

### 8. Install the faucet and through-counter UI

Install the Touch-Flo faucet through the counter per its own [`ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md), with the carbonated-water inlet stub fed from the customer's Lillium output and the two flavor lines injecting at the nozzle. Mount the KRAUS air switch and the RP2040 round display through the counter alongside it.

### 9. Close the enclosure

Lower the assembled contents into the enclosure shell, the funnel inlet rising through the lid hole flush with the cabinet top, and close it. The +X doorway faces the cabinet back for bag-swap access; the −X wall is the front, carrying the manifold ports and the pump column.

## Output condition

A finished Lite Edition unit:

- Two flavor bags hung on the rod cradle, spouts plumbed to the manifold
- Manifold + pumps assembled and plumbed per the fluid topology
- Electronics wired to pumps, valves, display, and air switch
- Faucet + air switch + display installed through-counter; faucet inlet ready for the Lillium hose
- Contents closed inside the transparent enclosure, funnel inlet flush with the lid

Ready to install under-sink beside a Lillium-class carbonator; the customer completes the Lillium pairing, prime, and first fill per [`README.md`](/pie-in-the-sky/lite/README.md) "Setup, priming, and refill".

## Open items

The Lite Edition is still substantially undesigned ([`README.md`](/pie-in-the-sky/lite/README.md) "Not designed" + "Open questions"). Before this procedure is buildable:

- **Enclosure detail.** Mounting feet, the pump-access door, and the rear faucet-inlet stub that accepts the Lillium hose are not designed.
- **Bag-port fitting.** What mates to the Platypus spout, and whether one low port serves both fill and draw or a second port is needed.
- **Electronics-shelf housing.** A discrete printed part or a feature of the enclosure shell.
- **Hopper mounting.** Part of the enclosure shell or a separate mounted part.
- **Firmware.** The manual-prime, no-sensor build.
- **Iteration lock.** Whether the faucet, pump-case, and cap-sense-sleeve versions on file are the shipping versions.

## Sources
[value](NAME) texts are updated by:
- `/pie-in-the-sky/lite/_assembly_sync.py`
