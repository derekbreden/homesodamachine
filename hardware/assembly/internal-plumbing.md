# Internal Plumbing

The production procedure for closing every internal fluid path inside the assembled enclosure — CO2 line from the front-panel inlet to the carbonator sparge port, filtered tap-water from the rear-panel backflow preventer to the carbonator water-inlet port, the full two-channel flavor manifold (BiB inputs through Y-divider tree, source-select valves, peristaltic pumps, reservoir/nozzle outputs), and the three-tube riser that lands on the back-panel umbilical bulkheads. Comes in after the mechanical chassis is closed up by [`enclosure-mechanical.md`](enclosure-mechanical.md) and feeds [`wiring.md`](wiring.md) and the first powered run at [`firmware-and-commissioning.md`](firmware-and-commissioning.md).

Design intent and the path-by-path enumeration live in [`../future.md`](../future.md) "Carbonation subsystem" + "Flavor subsystem" + "Backflow vent monitoring". The valve / Y-junction / tube-segment truth table this manifold builds to is [`../topology/fluid-topology.md`](../topology/fluid-topology.md) — the manifold matches that file segment-for-segment. Cold-core internal plumbing (everything inside the foam shell) is already complete per [`cold-core.md`](cold-core.md). Refrigerant lines are already brazed and charged per [`refrigerant-loop.md`](refrigerant-loop.md). Above-counter umbilical (faucet body, 3-tube bundle, foam insulation, sleeve) is already built per [`faucet-and-umbilical.md`](faucet-and-umbilical.md).

## Scope

In: mechanical chassis assembled per [`enclosure-mechanical.md`](enclosure-mechanical.md) — cold core seated against the back wall with coil stubs brazed and its seven penetrations (1/4" OD tubing) presented warm-side, back-panel bulkheads (water-inlet PI1208S 1/4" JG QC, BiB connector, 3× PP1208E umbilical) installed plus front-panel CO2 DERPIPE PTC installed, electronics shelf in place but unpowered, internal drip pan with moisture sensor mounted under the future backflow-preventer vent location. Plus the parts listed under "Inputs per appliance" below.

Out: every internal fluid path closed and primed-ready — fully connected, fully torqued, fully clamped, leak-witnessed dry where possible, but **not yet primed with water or CO2**. Fluid charging happens at [`acceptance-and-burn-in.md`](acceptance-and-burn-in.md). Specifically: CO2 path from the back-panel DERPIPE bulkhead through the GASHER check, WR1110 secondary regulator, first PP010822E PTC-to-NPT, into the cold core's +Z penetration, landing on the cold core's internal CO2 sparge stub at the foam-shell boundary; water path from the back-panel PI1208S 1/4" JG QC bulkhead (customer-facing — customer plugs the install-kit 1/4" LLDPE in at install time) → 1/4" LLDPE inside the cabinet → Waterdrop 15UC-UF filter (placement internal-vs-external to the enclosure TBD per [`../bom.md`](../bom.md) §3) → PP010822E 1/4" PTC × 1/4" NPT M → GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling threading onto the ASSE 1022's 3/8" MPT inlet → Multiplex 19-0897 backflow preventer → brewhardware FFL38BARB38 on the 3/8" MFL outlet → JoyTube silicone hose → SeaFlo pump → MAACFLOW barb adapter → GASHER check → first PP010822E → cold core's +Z slot landing on the cold core's internal water-inlet stub; flavor manifold built per [`../topology/fluid-topology.md`](../topology/fluid-topology.md) (BiB inlets through V-K-A/B → Y-divider tree → V-C/D source-select → pumps → reservoir/nozzle valves); three risers (carbonated-water from the cold-core bottom-plate outlet stub, flavor A nozzle, flavor B nozzle) exiting the enclosure top, terminating at the three back-panel PP1208E umbilical bulkheads; Multiplex atmospheric vent terminating in the internal drip pan over the moisture sensor.

Not in scope: cold-core internal plumbing — the in-cavity PP0308E elbow, the TAISHER vessel-port elbows, the silicone tube + sparge stone, the bottom-plate VALVENTO compression adapter on the water-outlet port — all installed inside the cold core during [`cold-core.md`](cold-core.md). Refrigerant lines — already done in [`refrigerant-loop.md`](refrigerant-loop.md). Above-counter umbilical — already done in [`faucet-and-umbilical.md`](faucet-and-umbilical.md). Customer-side tap and CO2 connections — install-time, not assembly. Solenoid and pump wiring — owned by [`wiring.md`](wiring.md); this doc lands every electrical actuator in its plumbed position but leaves the leads loose for the wiring step.

## Inputs per appliance

Per-unit BOM lives in [`../bom.md`](../bom.md) §3 (water inlet), §4 (CO2 subsystem), and §8 (flavor subsystem). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`../purchases.md`](../purchases.md) under the same sections. The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

| Item | Source | Use |
|---|---|---|
| Waterdrop 15UC-UF 0.01 µm inline water filter, 1/4" QC both ends | B085G9TZ4L | Upstream water filter on the customer-side run; placement internal-vs-external to the enclosure TBD per [`../bom.md`](../bom.md) §3 |
| John Guest PI1208S acetal bulkhead union, 1/4" QC × 1/4" QC | B0C1F3QR7N | **Customer-facing rear-panel water inlet.** Customer plugs the install-kit 1/4" LLDPE into the outboard side at install time |
| HAOCHEN brass angle-stop add-a-tee, 3/8" × 3/8" × 1/4" | B0DLKHHGL6 | Install-kit tee, **scenario B (older home)**; threads between customer's existing 3/8" angle stop and its braided compression supply line, exposing a 1/4" compression outlet for the appliance's LLDPE |
| John Guest PP0208E 1/4" × 1/4" × 1/4" union tee, black PP | FWS WEBFWS100677333 (ACQUIRED, see [`../bom.md`](../bom.md) §3) | Install-kit tee, **scenario A (modern home)**; drops inline into an existing 1/4" LLDPE under-sink line, push-to-connect, no tools. Black-PP NSF 51+61 food-cert family, matches every other JG fitting we ship |
| GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling | B0G2XJGZMQ (5-pk) | Upstream adapter chain — between the customer-side 1/4" LLDPE (downstream of filter, downstream of the PP010822E above) and the ASSE 1022's 3/8" MPT inlet. 316L SS, ships with Teflon tape |
| Multiplex 19-0897 ASSE 1022 backflow preventer | midwestbev | Tap-water backflow preventer; sits between the upstream adapter chain (3/8" MPT inlet side) and the FFL38BARB38 → silicone → SeaFlo suction (3/8" MFL outlet side) |
| brewhardware FFL38BARB38 3/8" FFL × 3/8" SS hose-barb adapter | brewhardware #156209 | Multiplex MFL outlet → JoyTube silicone hose, single-piece adapter |
| JoyTube 3/8" ID × 1/2" OD food-grade silicone hose | B089YGDB55 | Multiplex outlet → SeaFlo suction, ~12" per build cut from 10 ft roll |
| SEAFLO 22-Series 12 V 1.3 GPM 100 PSI diaphragm pump | B0166UBJX4 | Water transfer against CO2 back-pressure into the carbonator |
| MAACFLOW 1/4" NPT M × 3/8" hose barb | B0DMP77B6S (4-pk) | SeaFlo 3/8" barb outlet → 1/4" NPT plumbing. Used on water path + BiB legs |
| GASHER 1/4" NPT SS PTFE-soft-seat check valve | B0FV2D2FFX (2-pk) | One valve on water path, one on CO2 path. Rationale in [`cold-core.md`](cold-core.md) "Warm-side check valves" |
| Interstate Pneumatics WR1110 fixed-90 PSI secondary regulator, 1/4" NPT | B07J2L8LF3 | Inline secondary on CO2 path, between rear-panel DERPIPE and cold-core CO2 input |
| John Guest PP010822E 1/4" PTC × 1/4" NPT M adapter | FWS, 10-pk | NPT→PTC warm-side transition. 6 per build: 1 water path, 2 CO2 path (WR1110 in/out), 2 BiB legs, 1 spare |
| John Guest PP0308E 1/4" union elbow, PTC × PTC | FWS, 10-pk | Routing-elbow on PTC tubing runs. Spec inventory exact count downstream of routing layout — see Open items |
| Beduan 12 V 1/4" NC solenoid valve | B07NWCQJK9 | 12 valves per build — V-A through V-J + V-K-A + V-K-B per [`../topology/fluid-topology.md`](../topology/fluid-topology.md) |
| John Guest PP2308E two-way Y-divider, 1/4" | FWS, 10-pk | 10 Y-junctions per build — Y-A, Y-B, Y-KA, Y-C, Y-D, Y-E, Y-KB, Y-F, Y-G, Y-H per [`../topology/fluid-topology.md`](../topology/fluid-topology.md) |
| Kamoer KPHM400-SW3B25 12 V peristaltic pump | B09MS6C91D | 2 pumps per build, mounted in the printed pump cartridge |
| Printed pump cartridge | `../printed-parts/flavor/pump-case/` | Holds both Kamoer pumps + pogo-pin electrical interface; tool-free swap via the top-of-Zone-C access door per [`../printed-parts/enclosure/README.md`](../printed-parts/enclosure/README.md) |
| Magnetic pogo-pin connectors, 2-pin (2 pair) | B0CSX6ZQ1H | Pump-cartridge electrical connection — paired with cartridge install |
| Supply Depot 3/8" red BiB connector | B0DMFK9B6P | Back-panel BiB inlet, single connector feeding both flavor legs through the Y-divider tree |
| 1/4" OD LLDPE tubing | FWS bulk reel (see [`../bom.md`](../bom.md) §3) | Every line run not otherwise specified. Standard FWS black LLDPE |
| 1/4" OD blue LLDPE | Sourcing in flight per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification" | Carbonated-water riser to the blue-ringed back-panel PP1208E |
| LOKMAN 304 SS worm-gear clamps, 10–16 mm | B076Q7QVNM (20-pk) | Hose-barb clamps on the 3/8" silicone hose (FFL38BARB38 end + SeaFlo inlet barb). Quantity per build TBD — see Open items |
| Zip ties | B0BC1VH4XB (200-pk) | Cable + tube management throughout, ~15 per build |
| Millrose 70894 PTFE thread-seal tape | B07C9ZV4PG | Anti-seize on every NPT joint cut in this procedure (≥8 joints per build across water + CO2 paths) |

Tooling: Mudder PTFE tubing cutter (also shipped in the install kit per [`../bom.md`](../bom.md) §14, used here at the bench), 5/16" hex-driver and crescent wrench for the NPT joints, scissor for silicone hose cut-to-length.

## Procedure

Order of work: CO2 path first (dry, simpler — only two NPT joints inside the enclosure, no soft hose), then the water path (more joints, mixed barb/NPT/PTC, silicone hose to clamp), then the flavor manifold (twelve valves, ten Y-dividers, two pumps — the bulk of the bench labor). Three risers up to the back-panel umbilical bulkheads last, after the manifold is closed so the riser routing has the rest of the enclosure laid out around it.

### 1. CO2 path: front-panel DERPIPE → WR1110 → cold-core CO2 stub

Starting at the front panel: confirm the DERPIPE 5/16"-tube × 1/4" NPT push-to-connect bulkhead is installed per [`enclosure-mechanical.md`](enclosure-mechanical.md) (NPT side facing inboard). Wrap PTFE tape on the inboard NPT threads (2–3 wraps, clockwise as viewed into the thread, leaving the first thread tape-free). Thread the GASHER 1/4" NPT SS check valve onto the DERPIPE inboard NPT — arrow on the check valve body pointing **away** from the bulkhead, i.e. inflow from the rear panel, outflow toward the WR1110. Snug + 1 turn past hand-tight with the wrench backed up on the DERPIPE hex.

Wrap PTFE tape on the WR1110 inlet (the side stamped "IN"). Thread it onto the GASHER outlet. Same snug + 1 turn. Both fittings now sit in series on a short rigid NPT stub off the back panel — the WR1110 body hangs off the GASHER, supported by the threads only at this stage. Final mechanical fixturing of the WR1110 body (the regulator weighs enough to stress the NPT stub under transport vibration) is owned by [`enclosure-mechanical.md`](enclosure-mechanical.md) via a printed bracket against the back-panel inner face — see Open items.

Wrap PTFE tape on the WR1110 outlet ("OUT" side). Thread the first PP010822E 1/4" PTC × 1/4" NPT M adapter onto it. The NPT-to-PTC transition has now happened on the warm side of the cold core, consistent with the foam-shell boundary rule from [`../printed-parts/cold-core/foam-shell/README.md`](../printed-parts/cold-core/foam-shell/README.md) "Build decision".

Cut a length of 1/4" OD LLDPE from the bulk reel — long enough to route from the PP010822E outlet, up and over any routing obstacles, and into the cold-core CO2 input on the foam-cap top (the CO2 inlet enters from above through the foam-cap-top boss + lid Ø[6.5](COTWO_TUBE_D) hole at x=0, z=[-68.75](COTWO_INLET_Z) per [`cold-core.md`](cold-core.md) step 4). Cut both tube ends square with the Mudder cutter — square cuts are load-bearing for PTC sealing, no chamfer needed but no angled cut. Push one end fully into the PP010822E PTC port (audible click + tube bottoms against the internal stop). Push the other end into the cold-core CO2 input. Tug-test both ends.

The CO2 path is now closed dry from the back panel to the cold core. Vessel-side everything (the in-cavity PP0308E elbow, the second cold-side PP010822E, the TAISHER vessel-port elbow, the LTWFITTING barb adapter, the silicone tube, the sparge stone) is already inside the foam shell from [`cold-core.md`](cold-core.md) step 4.

### 2. Water path: rear-panel PI1208S → filter → adapter chain → ASSE 1022 → FFL38BARB38 → silicone hose → SeaFlo → cold-core water stub

The customer-facing rear-panel water inlet is a **1/4" JG QC bulkhead** (PI1208S). At install time the customer plugs the install-kit 1/4" LLDPE into the outboard PTC side — no factory work on that side beyond confirming the bulkhead is installed and the panel-side EPDM O-ring is seated. The factory work below closes everything inboard of the bulkhead.

Confirm the PI1208S is installed on the rear panel per [`enclosure-mechanical.md`](enclosure-mechanical.md) with the 1/4" QC on both sides (push-to-connect, no tools required at install). Cut a length of 1/4" OD LLDPE from the bulk reel — long enough to route from the PI1208S's inboard PTC face to the Waterdrop filter's inlet QC. Square-cut both ends with the Mudder cutter. Push fully into both PTC ports, tug-test. (**Filter placement TBD** — internal: filter sits inside the cabinet between the bulkhead and the ASSE 1022; external: the filter ships in the install kit and the customer mounts it inline upstream of the rear-panel bulkhead. The procedure below assumes internal; revisit when the placement decision lands in [`../bom.md`](../bom.md) §3.)

Cut a second length of 1/4" OD LLDPE from the filter outlet QC to the PP010822E 1/4" PTC × 1/4" NPT M adapter ([`../bom.md`](../bom.md) §3). Square cuts, push fully, tug-test. Wrap PTFE tape on the PP010822E's 1/4" NPT M side and thread it into the 1/4" NPT F side of the GAGIRA 316L SS reducing coupling — snug + 1 turn past hand-tight. The GAGIRA's other side is 3/8" NPT F and mates with the ASSE 1022's 3/8" MPT inlet (both pieces have only one MPT side and one FPT side, so the chain is unambiguous: tape goes on the ASSE 1022's MPT threads, then the GAGIRA threads onto the ASSE 1022). Snug + 1 turn. Multiplex flow arrow points away from the customer side (inflow from the GAGIRA at the 3/8" MPT side, outflow toward the SeaFlo pump at the 3/8" MFL side).

Thread the brewhardware FFL38BARB38 onto the ASSE 1022's 3/8" MFL outlet via the chrome-plated brass swivel nut — flat-faced FFL/MFL seal, no PTFE tape (the flare gasket seals). Snug + 1 turn against the chrome flat. The 3/8" SS hose barb now faces inboard, ready for the silicone hose.

Cut a length of JoyTube 3/8" ID silicone hose from the 10 ft roll, target ~12" — enough to span FFL38BARB38 barb to SeaFlo inlet with a gentle bend, no kink. Slip a LOKMAN worm-gear clamp onto each end of the hose before fitting. Push one end onto the FFL38BARB38 hose barb; push the other end onto the SeaFlo 22-Series 3/8" hose-barb inlet. Slide each clamp to the middle of its barb-overlap zone (~1/2" inboard of the barb tip, before the first barb ridge) and torque the clamp with the hex driver until the silicone pillows visibly between the clamp band and the barb — past finger-tight, not so much that the band cuts the silicone. The 3/8" diameter is held from the ASSE 1022 MFL outlet through the FFL38BARB38 and the silicone hose all the way to the pump inlet — no diameter step-down on the suction side once we're past the upstream adapter chain.

The Multiplex atmospheric vent (1/4" barb, on the body) gets a short stub of Sealproof 1/4" ID × 3/8" OD clear PVC ([`../bom.md`](../bom.md) §3) routed downward, terminating directly over the internal drip pan + moisture sensor that [`enclosure-mechanical.md`](enclosure-mechanical.md) seated on the cabinet floor. **Vent must drip to atmosphere, not be plumbed into a drain** — the vent is the mechanical telltale per [`../future.md`](../future.md) "Backflow vent monitoring". Two LOKMAN clamps on this run (vent barb + termination, if a termination barb is fitted — bare drip is also acceptable; the receiving pan does not need a tight fit).

Thread the MAACFLOW 1/4" NPT M × 3/8" hose-barb adapter into the SeaFlo's 3/8" outlet — PTFE tape on the NPT side facing the pump. (The SeaFlo outlet uses a barbed-to-NPT fitment; verify the adapter direction against the pump's outlet port type at the bench.) Thread the GASHER 1/4" NPT SS check valve (the second of the pack) onto the MAACFLOW's 1/4" NPT face, PTFE tape, arrow pointing away from the pump. Thread the first PP010822E 1/4" PTC × 1/4" NPT M onto the GASHER outlet, PTFE tape, same convention as the CO2 path.

Cut a length of 1/4" OD LLDPE from the bulk reel — route from the PP010822E outlet up over the SeaFlo, across to the +Z face of the cold core, and into the cold-core water-inlet stub at the +Z slot. Square-cut both ends, push fully into PTC ports at both ends, tug-test.

The water path is now closed dry from the rear panel to the cold core. Vessel-side everything (the second cold-side PP010822E, the TAISHER vessel-port elbow, the top-plate water-inlet NPT joint) is inside the foam shell from [`cold-core.md`](cold-core.md) step 4.

### 3. Flavor manifold: V-A through V-J + V-K-A + V-K-B + Y-A through Y-H + Y-KA + Y-KB + pump cartridge

Build to [`../topology/fluid-topology.md`](../topology/fluid-topology.md) segment-for-segment. The truth table there names every valve, every Y-junction, and every tube segment by number; this step describes the build cadence around that truth table, not its content.

Pre-build sequencing — bench sub-assembly vs. in-place build is **TBD; see Open items**. The remainder of this step is written for a bench sub-assembly that drops in afterward, with the understanding that an in-place build of the same parts list would carry the same ordering arguments.

On the bench, lay out all twelve Beduan solenoid valves (3 rows × 4) with their inlet/outlet legends visible. Lay out the ten PP2308E two-way Y-dividers between them in the topology positions. Pre-cut every tube segment from the [`../topology/fluid-topology.md`](../topology/fluid-topology.md) "Tube Segments" tables to length from the 1/4" OD LLDPE reel, square-cut both ends with the Mudder cutter, tag each segment with masking tape labelled by segment number from the topology doc.

Build outward from the two channel-A and channel-B pump rosettes:

- For each channel, push the appropriate segment into the pump's inlet PTC (segment 14 for channel A, segment 27 for channel B in the topology doc), then continue building back through Y-C → Y-KA → V-C + V-K-A for channel A (mirror for channel B), and forward from each pump's outlet through Y-D + Y-E + V-F + V-G for channel A (mirror Y-G + Y-H + V-I + V-J for channel B).
- The two BiB legs (V-K-A inlet from BiB-A, V-K-B inlet from BiB-B) terminate at the back-panel side of the manifold. Each leg gets a MAACFLOW 1/4" NPT × 3/8" hose-barb adapter at the rear panel side, threaded into the BiB connector's 3/8" output, then a PP010822E PTC × 1/4" NPT M behind it to transition into the 1/4" LLDPE that feeds V-K-A/V-K-B. Both legs share the single BiB connector on the rear panel via the Y-K topology.
- The shared upstream (tap-water V-A + hopper V-B + their merge through Y-A and Y-B) builds in last. V-A's inlet comes from the MTB-0604WP barb tee inline in the 3/8" silicone hose (between FFL38BARB38 and SeaFlo inlet) — PP450822E female adapter on the 1/4" MNPT branch → 1/4" OD LLDPE → flow regulator → V-A inlet per [`../topology/fluid-topology.md`](../topology/fluid-topology.md) tube segment 1. V-B's inlet is the funnel bottom of the user-facing top-face hopper.

The two Kamoer KPHM400 peristaltic pumps mount inside the printed pump cartridge. Route 1/4" OD LLDPE through each pump's BPT barbs and around the rotor — LLDPE fits the barbs directly, zip-tied tight. Seat each pump into its cartridge pocket. Install the magnetic pogo-pin connector pair to the cartridge's electrical interface — one pair per pump.

Cartridge install method into the enclosure is **TBD; see Open items**. The cartridge has been designed for tool-free swap via the front-face access door per [`../future.md`](../future.md) "Flavor subsystem"; the exact mechanism (push-fit + detent, screwed mounting plate, latch + cam) is not specified in the parts already committed.

Land the assembled flavor manifold into its enclosure position above the compressor and below the cold-core +Y face per the enclosure layout in [`../future.md`](../future.md) "Enclosure layout". Route tube segments through the pre-printed tube channels in the enclosure shell; zip-tie at every bundle pinch-point and at every long unsupported span.

Three manifold outlets exit upward to the back-panel umbilical bulkheads in step 4:

- **Carbonated water riser** comes from the cold-core's bottom-plate carbonated-water outlet stub (already plumbed out of the cold core's water-outlet penetration per [`cold-core.md`](cold-core.md) step 4; bottom-plate Port 3 → VALVENTO compression adapter → 1/4" OD blue LLDPE up out of the cold core). Build does not pick up this line in the flavor manifold step — it goes straight from the cold core to the back-panel blue-ringed PP1208E in step 4 below.
- **Flavor A riser** comes from V-G outlet (the "pump to nozzle A" valve, segment 21 in the topology doc terminating at "Nozzle A").
- **Flavor B riser** comes from V-J outlet (segment 34 terminating at "Nozzle B").

### 4. Risers up to back-panel umbilical bulkheads

Three risers exit the enclosure's top face and land on the three back-panel PP1208E umbilical bulkheads per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md). The bulkheads are arranged in a triangular cluster on the back panel, with the **blue-ringed bulkhead at the top vertex of the triangle** for the carbonated-water tube.

- **Carbonated-water riser:** 1/4" OD blue LLDPE from the cold-core bottom-plate outlet → up through the routing channel on the +Z side of the cold core → into the blue-ringed PP1208E from the inboard PTC face. Square-cut both ends, push fully into both PTC ports, tug-test. The CARGEN nitrile-rubber pipe insulation that wraps this line ([`../bom.md`](../bom.md) §9, 1/4" ID × 3/8" wall) is installed in segments along this run inside the cabinet, butted along the length — same install-by-segment ergonomics as the above-counter umbilical per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical bundle construction", scaled to the cabinet-internal portion of the run. Insulation continuity from the cold-core foam-shell exit to the inboard face of the blue-ringed bulkhead is the target — the cold-core foam exit is where the thermal mass of the cold core ends and the chilled water enters its multi-meter run to the faucet.
- **Flavor A riser:** 1/4" OD black LLDPE from V-G outlet up to the second (left vertex, by convention) PP1208E. No insulation — flavor lines run warm-in, warm-out at low duty cycle.
- **Flavor B riser:** 1/4" OD black LLDPE from V-J outlet up to the third (right vertex) PP1208E. No insulation.

Black-into-either-black is unambiguous downstream of the manifold (per [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification"): both flavor tubes route through the same panel-side bundle and the user does not need to distinguish them at the panel.

### 5. Witness and tidy

Walk every joint built in this procedure. Tug-test every PTC connection. Confirm every clamp on the silicone hose is past finger-tight and the silicone has pillowed. Confirm every NPT joint is past hand-tight and has PTFE tape showing at no more than half of the thread engagement (excess tape past half-engagement is a stress concentration). Confirm the Multiplex atmospheric vent stub terminates over the drip pan and the drip path has no obstruction. Confirm the pump cartridge sits in its enclosure position with both pogo-pin pairs mating.

Zip-tie any tube run with a span over ~6" between fixturing points. The enclosure's printed tube channels carry most of the line, but zip-ties at the bend transitions and at the pump cartridge boundary stabilize the manifold during transport.

The internal plumbing is now ready for [`wiring.md`](wiring.md) (the wiring step lands every solenoid lead, every pump lead, every sensor lead in its electrical termination on the electronics shelf, but the plumbing itself does not change after this step).

## Output condition

A finished internally-plumbed appliance:

- CO2 path closed dry from the back-panel DERPIPE bulkhead through the GASHER check, WR1110 regulator, first PP010822E, into the cold-core CO2 input
- Water path closed dry from the back-panel PI1208S 1/4" JG QC bulkhead through the Waterdrop 15UC-UF filter (placement TBD), the PP010822E + GAGIRA 316L SS reducing coupling, the Multiplex 19-0897 ASSE 1022 backflow preventer, the brewhardware FFL38BARB38 on its MFL outlet, the JoyTube silicone hose (LOKMAN clamps both ends), the SeaFlo pump, MAACFLOW barb adapter, GASHER check, first PP010822E, into the cold-core water-inlet
- Multiplex atmospheric vent terminating in the internal drip pan over the moisture sensor
- Flavor manifold built segment-for-segment per [`../topology/fluid-topology.md`](../topology/fluid-topology.md): 12 Beduan valves, 10 PP2308E Y-dividers, 2 Kamoer pumps in the printed pump cartridge, both BiB legs terminating at the shared rear-panel BiB connector through MAACFLOW + PP010822E adapters
- Three risers exiting the enclosure top, landing on the three back-panel PP1208E umbilical bulkheads (blue LLDPE on the blue-ringed bulkhead for carbonated water; black LLDPE on the two flavor bulkheads)
- Carbonated-water riser insulated with CARGEN nitrile-rubber pipe foam in segments from the cold-core exit to the inboard face of the blue-ringed bulkhead
- Every NPT joint PTFE-taped and torqued past hand-tight, no thread tape past half-engagement
- Every PTC joint square-cut and tug-tested
- Every silicone hose clamp past finger-tight with the hose pillowed at the band
- Zip-tied at all long unsupported tube spans and at all bundle pinch-points
- No water in any line; no CO2 in any line; system is primed-ready, not primed

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Pump cartridge install method into the enclosure.** Tool-free swap via the front-face access door is the design intent per [`../future.md`](../future.md) "Flavor subsystem", but the exact mechanism is not specified in any parts list. Plausible candidates: (a) push-fit + detent against a printed seat in the cartridge access door's inboard face — relies on detent geometry alone; (b) screwed mounting plate inside the access door with M3 SHCS + heat-set inserts — defeats the tool-free claim; (c) cam-latch or lever that engages a printed feature on the cartridge — requires a TBD off-the-shelf latch. Pick after the cartridge geometry reaches a CAD generator and the pogo-pin contact force budget is in hand.
2. **Flavor manifold: bench sub-assembly vs. in-place build.** Procedure as written assumes bench sub-assembly; pre-cut every segment per [`../topology/fluid-topology.md`](../topology/fluid-topology.md), build outward from the pump rosettes on the bench, then drop the assembled manifold into the enclosure. Plausibility: the manifold's footprint is ~150 × 200 mm above the compressor; the enclosure has access from the front face (cartridge door) and the top face (open during this step, before the hopper funnel installs). An in-place build of the same parts list is geometrically defensible — every joint is reachable from the front or top access faces — and avoids the lift-and-place step that a bench manifold requires (the manifold has 22 PTC tube terminations and 12 valves; the lift puts every termination at risk of an unseat). Decision is downstream of the first unit's bench cycle time vs in-place cycle time.
3. ~~**Tap-water tap-point into the flavor manifold (V-A inlet).**~~ **CLOSED.** MTB-0604WP barb tee (3/8" ID barb × 3/8" ID barb × 1/4" MNPT, FWS WEBFWS100677768) inserts inline in the 3/8" silicone hose between FFL38BARB38 and SeaFlo inlet; PP450822E (JG black PP female adapter, 1/4" NPTF × 1/4" OD PTC) threads onto the 1/4" MNPT branch and connects via 1/4" OD LLDPE to the flow regulator → V-A. Both 3/8" barb legs clamped with LOKMAN worm-gear clamps. See [`../bom.md`](../bom.md) §3 and `purchases.md` WEBFWS100677768.
4. **PP0308E elbow count in the warm-side line runs.** [`../bom.md`](../bom.md) §4 commits 2 PP0308E elbows per build for the CO2 path (cold-core internal use only). The warm-side line runs in this procedure may benefit from additional PP0308E elbows for sharp routing turns (water path at the cold-core +Z slot exit, manifold-to-riser transitions). Quantity not enumerated against a routing layout. Pick after the enclosure's internal tube-channel geometry reaches CAD.
5. **LOKMAN clamp quantity per build.** [`../bom.md`](../bom.md) §3 commits 4 LOKMAN clamps per build but assigns them to "vent line clamps". This procedure also wants 2 clamps for the 3/8" silicone hose between Multiplex outlet and SeaFlo inlet (one per barb), plus possibly 1–2 for the vent stub if a termination barb is fitted. The 4-clamp budget may be tight; recount once the vent stub mechanical detail is final.
6. **Mechanical fixturing of the WR1110 body.** The regulator hangs off the back-panel NPT stub via thread engagement alone after step 1, which is adequate for ship + sit but stresses the NPT stub under transport vibration. [`enclosure-mechanical.md`](enclosure-mechanical.md) should add a printed bracket against the back-panel inner face that captures the WR1110 body. Flagged here because this procedure is downstream of that mechanical step but depends on its existence; coordinate with the mechanical doc.
7. **Cabinet-internal carbonated-water insulation segment count.** [`../printed-parts/enclosure/back-panel/README.md`](../printed-parts/enclosure/back-panel/README.md) "Umbilical bundle construction" specifies 1-ft CARGEN segments for the above-counter umbilical, with field-install ergonomics. The cabinet-internal portion of the same insulated line (cold-core exit → blue-ringed bulkhead inboard face) has a fixed length per build and could use a single cut-to-length segment in-shop. Pick once the cabinet-internal run length is pinned by the cold-core position + back-panel position.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_internal_plumbing_sync.py`
