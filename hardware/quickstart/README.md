# Installation reference

`00-install.html` is one single-sided landscape 11 x 17 in sheet for the faucet and its factory
umbilical. It publishes as `quick-start.pdf` on `/drawings` and prints at actual size on the Epson.

The sheet has three visual acts:

1. Drop the complete faucet through a 1 3/8 in / 35 mm opening, push it rearward until both black
   flavor tubes touch the opening wall, then install the keyhole plate, washer, and nut from below.
2. Before any field cut, plan the appliance route with 60 mm behind its stored position, both side
   grilles open, room to tip a 440 mL bottle above the hopper, and a 300 mm pull-forward service
   loop to the cabinet face.
3. With the machine pulled forward, route each factory tail to its port, mark the collet face, add the
   PP1208E's 15.7 mm / 0.62 in tube insertion depth, and cut only the excess below the collar. Then
   push and tug-check `SODA`, `FLAVOR`, and `FLAVOR` on the exact rear face. Either black tube can
   land on either `FLAVOR` port.

The field-trim allowance is the manufacturer's `H` tube-insertion dimension for the 1/4 in
PP1208E: [15.7 mm / 0.62 in](https://www.johnguest.com/sites/jg/files/2023-04/JG%20Drinks%20Polypropylene%20Bulkhead%20Connector%20Data%20Sheet.pdf).
The design and BOM use that same fitting at `SODA` and both `FLAVOR` stations. A ship-ready release
also requires a receiving witness on one acquired fitting: bottom a square-cut scrap tube, mark its
fully-out collet face, and confirm the inserted length.

## Procedure boundary

This is a development installation reference, not a commissioning procedure. It stops after the
three factory round tubes are seated and tug-checked. It does not authorize or depict:

- `TAP` water connection;
- CO2 connection, regulation, restraint, or leak testing;
- faucet signal termination;
- AC power;
- filling, priming, refrigeration, carbonation, or dispensing.

Those operations require their own released and validated procedures. The current integrated
appliance firmware does not provide a complete customer first-pour sequence, so this document makes
no owner-interface or ready-to-pour claims.

The faucet-mount panels describe the current dry mechanical stack; they are not a drill-location or
countertop-compatibility approval. Maximum deck thickness, opening setbacks and underside keep-out,
the shank-nut retention handoff, final SIG-6 countertop relief, fastening acceptance, and the steel
plate's bond classification remain release gates.

## Next public sequence: evidence gates

The next customer sheet is a product-evidence backlog, not a copy backlog. A gate closes only when
the named result is observed on assembled shipping hardware and the exact physical or on-device
state can be captured. A planned bench procedure, serial-only result, or recreated screen does not
unlock a public picture.

| Gate | Observable evidence required | Picture unlocked | Owner / workstream |
| --- | --- | --- | --- |
| Installed utility + electrical handoff | Install one carton-state unit with the released hardware and procedure. Verify the prepared-opening envelope, countertop thickness and underside keep-out; reconciled shank-nut retention handoff and faucet fastening acceptance; side-grille clearance and 440 mL bottle sweep; final faucet-signal termination and countertop strain relief; explicit faucet-plate bond or no-bond disposition; water and feasible regulated-CO2 connections leak-tight; power-safe handoff; and a bright-screen faucet selection received, persisted, and mirrored by the controller. | Installer handoff to first power and the verified dry display link. | Faucet/umbilical, Steel Plate, wiring/electrical, installer validation |
| Cold carbonated-water substrate | From the shipped-dry state, the real fill valve and pump stop at the high reed or fault safely; regulation holds; compressor and fan reach the released cold gate; a lever pour produces cold visibly carbonated water without sputter; and refill waits while the lever is open. | Installer hands over a commissioned cold-carbonated-water machine. No `READY` screen is implied. | Firmware, pressure/refrigeration hardware, wet commissioning |
| One bottle reaches one chosen reservoir | A released initiation and destination action routes one 440 mL bottle through the correct valves and pump into only A or B. The hopper drains, the transfer stops in a bounded way, and the product gives a truthful completion observable. Pass both destinations without overflow, cross-fill, or leak. | Choose destination, pour one bottle, observe transfer complete. | Firmware, hopper/level sensing, fluid hardware, wet commissioning |
| Wet prime reaches the matching nozzle | Holding Prime opens the authoritative valve pair and matching pump. Concentrate exits only the selected nozzle tube; release, timeout, or link loss parks the pump and both valves without crossflow or leak. Pass A and B. | Cup under nozzle, hold Prime until flavor appears, release to stop. | Firmware, fluid topology, wet commissioning |
| Lever flow meters the selected flavor | Real water flow starts only the selected flavor path at the committed production ratio. Lever close stops pump and valves without continued drip or crossflow; flavor never runs without water; a queued refill waits until dispensing ends. Pass and log both channels. | Select flavor, lever down, three streams meet in the glass, lever closes and flow stops. | Firmware, flow calibration, wet commissioning |

The verified boot, front-display selection, controller persistence, and faucet-art mirroring remain an
internal release study in `studies/first-power-link/`. They establish a dry interaction, not beverage
readiness. The narrow future owner sequence begins after the installed machine has passed the first
two gates: choose a reservoir, load one bottle, wet-prime that channel, select it at the faucet, and
pour one measured glass.

The gate evidence is anchored by the current-state sources in
[`faucet-and-umbilical.md`](../assembly/faucet-and-umbilical.md),
[`wiring.md`](../assembly/wiring.md),
[`firmware/src_appliance/README.md`](../../firmware/src_appliance/README.md),
[`fluid-topology.md`](../topology/fluid-topology.md),
[`acceptance-and-burn-in.md`](../assembly/acceptance-and-burn-in.md), and
[`finish-pack-ship.md`](../assembly/finish-pack-ship.md).

## Picture contract

Each visual must communicate the object, location, motion, and result before its caption is read.
The recurring grammar is:

- exact CAD for the appliance, faucet, countertop hardware, umbilical tails, and rear ports;
- coral only for a person's motion;
- green only for a verified result;
- product colors and molded words for physical identity;
- crosshatching for the braided sleeve, with one blue and two black tubes visible at both ends;
- the PP1208E side view limited to its published exterior, 6.35 mm tube, and 15.7 mm stop plane;
- ghosting only for the pulled-forward service position in the top-view planning inset;
- stop marks attached directly to connections outside this sheet's scope.

Cabinet, sink, hand, cutter, connector cutaway, dimensions, and motion arrows are simplified
instructional context. The washer and nut are conservative stand-ins because the donor hardware has
no source CAD.

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
