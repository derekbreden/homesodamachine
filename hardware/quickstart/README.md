# Installation planning reference

`00-install.html` is one single-sided landscape 11 x 17 in development sheet for the faucet and
its factory umbilical. It publishes as `quick-start.pdf` on `/drawings` and prints at actual size on
the Epson for in-house review.

This sheet is a planning and identity map, not a field procedure. Its three visual acts are:

1. Identify the complete factory assembly: one faucet, one braided sleeve, one blue `SODA` tube,
   two black `FLAVOR` tubes, and one flat signal ribbon. The four tails stay with the faucet.
2. Reserve a cabinet-space envelope around the current appliance: 60 mm behind the stored unit,
   both side grilles unobstructed, 300 mm service depth to the cabinet face, and a broad detached
   umbilical-clearance volume. No countertop origin, hole, exact route, or movement arrow is shown.
3. Match future label identities without a physical path: detached `S` and `F` badges pair the blue
   `SODA` collar and two black `FLAVOR` collars with the same rear labels. The signal ribbon has no
   released appliance port. `TAP` and CO2 are explicitly excluded.

## Field boundary

The sheet authorizes no field action. It must not be used to drill, mount, trim, connect, terminate,
energize, pressure-test, or commission the machine. In particular, it does not authorize or depict:

- a countertop opening location, thickness range, underside keep-out, or mounting procedure;
- field handling of the factory faucet keeper, plate, washer, nut, blue tube joint, or signal ribbon;
- tube cutting, insertion, or tug testing at `SODA` or `FLAVOR`;
- `TAP` water, regulated CO2, cylinder restraint, or leak testing;
- faucet-signal termination, protective-earth disposition, or AC power;
- filling, priming, refrigeration, carbonation, or dispensing.

The faucet mount is blocked on literal hardware acceptance. The blue supply tube is
compression-connected before shipment, so an ordinary closed washer and nut cannot be added over
the shank in the field. The released architecture requires the final keeper or lock hardware to be
captive on the bare shank before that tube joint, with the open keyhole plate sliding into the
accepted stack. The actual A2031 underside hardware, tightening tool and secure-state test,
countertop envelope, signal-ribbon protection, hand/tool keep-out, and plate electrical
classification all require physical acceptance.

Current CAD establishes only these mount-envelope inputs: the prepared opening is Ø34.93 mm; its
intended seated center is 4.992 mm behind the shank axis; the rigid upper plate is 4.000 mm, the TPU
gasket is 2.000 mm, and the current keyhole plate is 1.524 mm. Thread available below the keyhole
plate is `42.476 mm - countertop thickness`. These inputs do not establish a maximum countertop
thickness or a field procedure.

The rear `SODA` and `FLAVOR` designs use JG PP1208E fittings. The manufacturer's `H` tube-insertion
dimension is [15.7 mm / 0.62 in](https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Polypropylene%20Bulkhead%20Connector%20Data%20Sheet.pdf),
measured with the collet in its release position. That datum belongs to the future procedure
evidence; it is not a cutting instruction. Release requires a receiving witness on an acquired
fitting with the actual tube and collet state.

## Public-sequence evidence gates

Every customer picture is unlocked by observed shipping-hardware behavior. A planned bench
procedure, serial-only result, or recreated screen does not establish product truth.

| Gate | Observable evidence required | Picture unlocked | Owner / workstream |
| --- | --- | --- | --- |
| Installed mechanical, utility, and electrical handoff | Install one carton-state unit with the released captive underside hardware. Coupon the actual A2031/S4177511/counter stack; accept maximum countertop thickness, keyhole slide, tightening tool, lever-rock/gasket-creep result, underside keep-out, and protected signal-ribbon route. Resolve plate PE classification and test. Verify side-grille and service clearances, actual PP1208E insertion witnesses, `TAP` and restrained regulated-CO2 connections, leak tests, and a qualified power-last handoff. | Literal dry installation and installer handoff. | Faucet/umbilical, Steel Plate, wiring/electrical, installer validation |
| Cold carbonated-water substrate | From shipped-dry state, the real fill path stops at the released level or faults safely; regulation holds; compressor and fan reach the released cold gate; a lever pour produces cold visibly carbonated water without sputter; refill waits while the lever is open. | Commissioned cold-carbonated-water handoff. No `READY` screen is implied. | Firmware, pressure/refrigeration hardware, wet commissioning |
| One bottle reaches one chosen reservoir | A released initiation and destination action routes one 440 mL bottle through the correct valves and pump into only A or B. The hopper drains, transfer stops in a bounded way, and the product exposes a truthful completion observable. Pass both destinations without overflow, cross-fill, or leak. | Choose destination, pour one bottle, observe the literal completion state. | Firmware, hopper/level sensing, fluid hardware, wet commissioning |
| Wet prime reaches the matching nozzle | Holding Prime opens the authoritative valve pair and matching pump. Concentrate exits only the selected nozzle tube; release, timeout, or link loss parks the pump and both valves without crossflow or leak. Pass A and B. | Cup under nozzle, hold Prime until flavor appears, release to stop. | Firmware, fluid topology, wet commissioning |
| Lever flow meters the selected flavor | Real water flow starts only the selected flavor path at the committed production ratio. Lever close stops pump and valves without continued drip or crossflow; flavor never runs without water; queued refill waits until dispensing ends. Pass and log both channels. | Select flavor, lever down, three streams meet in the glass, lever closes and flow stops. | Firmware, flow calibration, wet commissioning |

The verified boot, front-display selection, controller persistence, and faucet-art mirroring remain an
internal dry study in `studies/first-power-link/`. They do not establish a power-safe installation,
beverage readiness, or first-pour behavior.

Evidence is anchored by the current-state sources in
[`faucet-and-umbilical.md`](../assembly/faucet-and-umbilical.md),
[`wiring.md`](../assembly/wiring.md),
[`firmware/src_appliance/README.md`](../../firmware/src_appliance/README.md),
[`fluid-topology.md`](../topology/fluid-topology.md),
[`acceptance-and-burn-in.md`](../assembly/acceptance-and-burn-in.md), and
[`finish-pack-ship.md`](../assembly/finish-pack-ship.md).

## Picture contract

Each visual must establish the object and spatial relationship before its caption is read. The
planning sheet uses:

- exact product-derived artwork for the appliance, faucet, umbilical tails, and rear ports;
- crosshatching for the braided sleeve, with one blue tube, two black tubes, and the flat ribbon
  separated at the tail end;
- detached matching badges with visible gaps between every factory tail and rear connector;
- one lock boundary over the complete rear connector field, including `SODA` and both `FLAVOR`
  ports, so identity matching cannot read as current connection permission;
- coral only for unreleased boundaries and the complete locked rear connector field;
- explicit stop language on the same visual plane as every potentially actionable scene;
- no hand, tool, cut line, fastener stack, insertion depth, fictitious connector, or recreated UI.

Cabinet and sink outlines are simplified spatial context. The broad hatched umbilical zone is a
clearance envelope, not a field route. The 60 mm and 300 mm values are current design reservations,
not validated installation acceptance dimensions.

## Build

From the repository root:

```sh
# Rebuild product-derived PNGs after CAD or rear-port changes.
tools/cad-venv/bin/python hardware/quickstart/quickstart_art.py

# Rebuild the PDF after an HTML or CSS edit.
tools/cad-venv/bin/python hardware/quickstart/_build.py
```

The two steps are separate build targets. A layout iteration consumes the checked-in artwork and
does not regenerate CAD.

The pinned Linux CAD image is the byte authority for generated artwork and the bound PDF. Local
macOS runs are visual previews because native OCCT tessellation differs by host. The derive workflow
regenerates and commits the canonical Linux result.

`out/00-install.png` and `out/00-install.pdf` are the full-resolution sheet render. The bound PDF is
one 17 x 11 in page at 150 px/in. Inspect the page at actual size and in grayscale before publication.
