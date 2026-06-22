# Lite Edition Assembly

*Pie-in-the-sky, not roadmap — a first-pass build procedure for the [Lite Edition](/pie-in-the-sky/lite/README.md) flavor-injection module. Companion to [`README.md`](/pie-in-the-sky/lite/README.md) (what the Lite is and the customer experience) and [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md) (per-unit parts).*

The Lite Edition is the flavor half of the main appliance wrapped in a small transparent cabinet — two collapsible flavor bags, two peristaltic pumps, a valve manifold, a faucet, the dispense electronics, and the enclosure that holds them. It does not carbonate, refrigerate, or store water; cold carbonated water comes from the customer's paired Lillium-class carbonator. So this procedure has no pressure vessel, no hydro-test, no refrigerant loop, and no foam-pour cold core — roughly half the [main-appliance assembly set](/hardware/assembly/) does not apply.

## Scope

In: the printed PETG parts ([enclosure halves](/pie-in-the-sky/lite/enclosure/), [reservoir-pockets bag cradle](/pie-in-the-sky/lite/printed-parts/reservoir-pockets/), [funnel / hopper](/pie-in-the-sky/lite/printed-parts/funnel/), the [faucet stack](/hardware/printed-parts/faucet/), and the [pump cases](/hardware/printed-parts/flavor/pump-case/)); the off-the-shelf flavor parts (two Platypus bags, two Kamoer KPHM400 pumps, the manifold valves + John Guest fittings + tubing); the faucet, air switch, and the Waveshare 4.3″ config display; the electronics family (ESP32, MCP23017 expander, ULN2803A drivers, motor driver, 12 V supply); and one 1/8" stainless bag-hanger rod.

Out: a finished Lite Edition unit, ready for under-sink install and pairing to a Lillium-class carbonator.

Not in scope: the Lillium carbonator itself (resold, not manufactured — [`README.md`](/pie-in-the-sky/lite/README.md) "What the customer buys"); the customer-side install, prime, and refill (manual and watched — [`README.md`](/pie-in-the-sky/lite/README.md) "Setup, priming, and refill"); and every carbonation / refrigeration subsystem the Lite omits ([`README.md`](/pie-in-the-sky/lite/README.md) "What the Lite Edition does not contain").

## Inputs per unit

Per-unit parts and cost live in [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md). The build-specific items, with the printed parts that wrap them:

| Item | Source | Notes |
|---|---|---|
| Enclosure halves (printed PETG) | [`enclosure/`](/pie-in-the-sky/lite/enclosure/) | Split front + back, telescoping cross-pinned; display facet + hopper opening |
| Reservoir-pockets bag cradle (printed PETG) | [`reservoir-pockets/`](/pie-in-the-sky/lite/printed-parts/reservoir-pockets/) | Two bag pockets + a rod-hang channel |
| Funnel / hopper (printed PETG) | [`funnel/`](/pie-in-the-sky/lite/printed-parts/funnel/) | Drop-in pour-through funnel; collar from the hopper opening, to V-B |
| Faucet stack (printed PET-CF) | [`faucet/touch-flo-shell/`](/hardware/printed-parts/faucet/touch-flo-shell/) | Touch-Flo shell + plate + gasket + o-ring |
| Pump cases (printed) | [`flavor/pump-case/`](/hardware/printed-parts/flavor/pump-case/) | Houses the Kamoer pumps |
| 1/8" stainless bag-hanger rod, [158 mm](ROD_LENGTH) | Same stock as the carbonator float rod (Tandefio B0CY4DWJFQ) | Threads both bags' top loops |
| Platypus Hoser 1 L bag × 2 | [B002OYMRS8](https://www.amazon.com/dp/B002OYMRS8) | Spout-down flavor reservoirs ([`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md)) |
| Kamoer KPHM400 pump × 2 | [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md) | Valve-locked peristaltic pumps |
| Manifold valves + fittings + tubing | [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md) | Beduan solenoids, John Guest PP-series, clear PVC + LLDPE |

## Procedure

### 1. Print and prep the parts

Print the transparent-PETG parts — the two enclosure halves (front + back), reservoir-pockets cradle, funnel — plus the PET-CF faucet stack and the pump cases. Deburr the ⌀6.5 mm tube exits and the rod-hang channel so the bag spouts and the hanger rod seat clean.

### 2. Hang the bag rod and load the bags

This step is done on the bare cradle, described in its own local frame (doorway on +X, spout exits on −X); when the cradle is seated in the enclosure it is rotated +90° about Z, so its +X doorway becomes the enclosure's +Y (cabinet back) and its −X exit wall becomes the −Y (front) — see [`_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py).

Cut one 1/8" stainless rod to [158 mm](ROD_LENGTH) — tip to tip, the same stock as the carbonator float rod. Thread it through both Platypus bags' centered top loops, slide the rod in from the cradle's +X (doorway) side carrying both bags, roll it down the flared ramp, and let it seat in the center rest pocket against the −X end stop. The bags' own weight holds it down, and the 2 mm plug past each rod-end boss captures it along its own axis so it cannot slide out; the channel stays open at +X for insertion and removal. Route each bag's spout down to the ⌀6.5 mm exit low in the cradle's −X (exit) wall.

Unlike the carbonator and Kitchen-reservoir float rods, this is a **tool-free hang** — no weld, no boss bore — so the same operation is the consumer-serviceable bag swap (through the doorway that faces the cabinet back once installed). Geometry: [`reservoir-pockets/README.md`](/pie-in-the-sky/lite/printed-parts/reservoir-pockets/README.md).

### 3. Build and stack the valve manifold

Assemble the four manifold trays — source-select, bag-circuit, bib-gate, nozzle-gate — the same tray assemblies as the Kitchen build ([`valve-manifold/`](/hardware/printed-parts/valve-manifold/)), populated with the Beduan solenoids and John Guest dividers / tees / stem-barbs from [`lite-bom.md`](/pie-in-the-sky/lite/lite-bom.md). Stack bib-gate and nozzle-gate flat in the front-left corner under the display, lay bag-circuit flat across the front-zone top, and stand source-select vertical in the +X column beside the reservoir (under the hopper), per [`_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py).

### 4. Mount the pumps

Seat the two Kamoer KPHM400 pumps in their printed cases, standing on the floor side by side in the front-right under the hopper, tube barbs facing −Y (front) into the open front air, per [`_contents.py`](/pie-in-the-sky/lite/enclosure-assembly/_contents.py).

### 5. Plumb the flavor circuit

Run the clear-PVC and LLDPE lines per [`fluid-topology-manifold.mmd`](/pie-in-the-sky/lite/fluid-topology-manifold.mmd): bag spouts → manifold, the pump loops, hopper spout → V-B, the optional bag-in-box inputs through the 3/8"→1/4" reducers, the Lillium clean-water feed through the flow-control bulkhead (throttled to the manifold's low working pressure), and the two flavor lines up to the faucet nozzle. The visible clear runs are the "green" segments in the topology; the short rigid jumpers between push-connect fittings are the grey LLDPE hops.

### 6. Mount the funnel

Drop the funnel into the top-wall opening to the right of the display — brim resting on the lid, collar press-fit in the opening — its spout necking above the front trays, where a short flexible tube carries the pour back to V-B on source-select (the spout does not land on V-B directly, same as the Kitchen hopper). Geometry: [`funnel/README.md`](/pie-in-the-sky/lite/printed-parts/funnel/README.md).

### 7. Wire the electronics

Mount the ESP32, MCP23017 expander, ULN2803A drivers, motor driver, and 12 V supply, and wire them to the two pumps, the manifold solenoids, the Waveshare 4.3″ config display, and the air switch — the same parts family and dispense logic as the main appliance, minus every sensor the Lite omits (no level reeds, no moisture telltale). The electronics-shelf housing is undesigned (a placeholder in the +X channel beside the reservoir; see Open items).

### 8. Install the faucet and through-counter UI

Install the Touch-Flo faucet through the counter per its own [`ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md), with the carbonated-water inlet stub fed from the customer's Lillium output and the two flavor lines injecting at the nozzle. Mount the KRAUS air switch through the counter alongside it. (The Waveshare 4.3″ config display lives in the enclosure facet, not through the counter — it is seated when the halves close, step 9.)

### 9. Close the enclosure

Lower the contents (the bag cradle already loaded, step 2) into the back half, seat the Waveshare 4.3″ display in the front half's facet, then telescope the front half onto the back and drive the four corner M3 cross-pins from the ±X exterior. The funnel brim sits flush on the top; the reservoir's +Y doorway faces the cabinet back for rear bag-swap access (the in-cabinet rear-access detail — a removable rear panel or pull-out — is an open item); the −Y wall is the front, carrying the display facet, the front tray stack, and the pumps.

## Output condition

A finished Lite Edition unit:

- Two flavor bags hung on the rod cradle, spouts plumbed to the manifold
- Manifold + pumps assembled and plumbed per the fluid topology
- Electronics wired to pumps, valves, display, and air switch
- Faucet + air switch + display installed through-counter; faucet inlet ready for the Lillium hose
- Contents closed inside the transparent split-half enclosure, display seated in the facet, funnel brim flush on the lid

Ready to install under-sink beside a Lillium-class carbonator; the customer completes the Lillium pairing, prime, and first fill per [`README.md`](/pie-in-the-sky/lite/README.md) "Setup, priming, and refill".

## Open items

The Lite Edition still has open detail ([`README.md`](/pie-in-the-sky/lite/README.md) "Added scope" + "Open questions"). The enclosure shell, bag cradle, and hopper are now designed; remaining before this procedure is fully buildable:

- **Enclosure detail.** Within the [split-half shell](/pie-in-the-sky/lite/enclosure/): mounting feet, a pump-access provision, and the rear faucet-inlet stub that accepts the Lillium hose are not yet drawn.
- **Bag-port fitting.** What mates to the Platypus spout, and whether one low port serves both fill and draw or a second port is needed.
- **Electronics-shelf housing.** A discrete printed part to replace the placeholder box in the +X channel beside the reservoir.
- **Firmware.** The manual-prime, no-sensor build.
- **Iteration lock.** Whether the faucet, pump-case, and cap-sense-sleeve versions on file are the shipping versions.

## Sources
[value](NAME) texts are updated by:
- `/pie-in-the-sky/lite/_assembly_sync.py`
