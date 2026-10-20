# Internal Plumbing

The procedure for closing every internal fluid path inside the assembled enclosure — CO2 line from the inlet on the +Y wall of back-top to the cold core's `co2-in` cap conduit, filtered tap-water from the +Y wall's inlet through the backflow preventer to the `water-in` cap conduit, the full two-channel flavor manifold (source-select valves, peristaltic pumps, reservoir fills and draws, gooseneck outputs), and the three risers that land on the umbilical bulkheads on the +Y wall. **§3's permanent junctions, keepers, fixed returns, valves and tubing are assembled on the bench into `enclosure-front-top` while that piece is still loose.** The rest stages where the slide order puts it ([`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §6): work on `enclosure-back-top`'s own walls — the tap-water chain in its anchor, the water split in its rib — happens on that piece on the bench before its column closes; work on the cold core's lid — the pump's two elbows, the check chain and the tubes between them — happens on the core's open cart before it rides in; the crossing runs and the risers are made up through the open Y-seam mouth after the ride; and only the pump cartridge's connection cycle waits for a fully closed chassis. Feeds [`wiring.md`](/hardware/assembly/wiring.md) and the first powered run at [`firmware-and-commissioning.md`](/hardware/assembly/firmware-and-commissioning.md).

Design intent and the path-by-path enumeration live in [`/hardware/README.md`](/hardware/README.md) "Carbonation" + "Flavor" + "Safety". The valve / Y-junction / tube-segment truth table this manifold builds to is [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) — the manifold matches that file segment-for-segment. Cold-core internal plumbing (everything inside the foam shell) is already complete per [`cold-core.md`](/hardware/assembly/cold-core.md). Refrigerant lines are already brazed and charged per [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md). Above-counter umbilical (faucet, 3-tube bundle, foam insulation, sleeve) is already built per [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md).

## Scope

In: the slide order's stages per [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §6 — `enclosure-back-top` populated on the bench (3× PP1208E umbilical + the water-inlet PP1208E 1/4" JG QC + the CO2 neoFit ABU44 + the 4 mm OVER bulkhead + the RJ11 keystone + the C14; electronics bay on its wall; unpowered), the cold core charged and staged on its cart with its [7](CAP_FLUID_LINES) cap conduits standing proud of the top lid, and — for the runs made up at the mouth and the pump cartridge's connection cycle — the ridden-together chassis. Plus the parts listed under "Inputs per appliance" below. **§3 runs ahead of all of it** — its permanent junctions, keepers, fixed returns and valve rows are assembled on `enclosure-front-top` before that piece joins anything, so what they need off this list is the printed set and the parts, not a chassis.

**Every warm-side fluid termination on the cold core is a cap conduit.** All [7](CAP_FLUID_LINES) of them are Ø[7.5 mm](CAP_CONDUIT_D) bores up the cap's own columns, opening upward on the lid's outer face — so a line reaching one arrives at the deck the electronics bay stands on, not at a body face, and leans into a countersunk lip on the way in. Three are the carbonator's own (`water-in`, `co2-in`, `carb-water-out`) and four are the reservoirs' (`reservoir-a`, `reservoir-a-fill`, `reservoir-b`, `reservoir-b-fill`). No fluid line crosses a shell wall: the core's front face is mated against the refrigeration base — the condenser flush on it, the compressor's plate inset at each end, because the condenser is the deeper of the two and the pair is struck on one centre before it is yawed — so a bore struck there would open into that base rather than into the machine. What is left on that face is the copper/PRV slot on each lane, and neither of the two is this procedure's — both reed cables leave by the lid, each up the channel its own column stands in.

Out: every internal fluid path closed and primed-ready — fully connected, fully torqued, fully clamped, leak-witnessed dry where possible, but **not yet primed with water or CO2**. Fluid charging happens at [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md). Specifically: CO2 path from the +Y wall's ABU44 bulkhead, `co2-0` to the WR1105 secondary regulator, `co2-1` to the downstream GASHER check, and `co2-2` to the `co2-in` cap conduit, with gas-rated adapters and the made-up check placement qualified as described in §1; water path from the +Y wall's PP1208E 1/4" JG QC bulkhead (customer-facing — customer plugs the install-kit 1/4" LLDPE in at install time; the install-kit Waterdrop 15UC-UF filter mounts customer-side, inline upstream of this bulkhead, per [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3) → the ASSE chain's own inlet collet, which the bulkhead's inboard collet meets face to face → PP010822E 1/4" PTC × 1/4" NPT M → GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling threading onto the ASSE 1022's 3/8" MPT inlet → Multiplex 19-0897 backflow preventer → PI4512F6S + PP061208W (3/8" MFL → 1/4" PTC) → `water-2` → water-split PP0208E tee → `water-3` → V-K fill/shutoff → `water-7` → the printed TPU suction elbow on the G Ganen's suction barb → G Ganen pump → the printed TPU discharge elbow on its discharge barb → `water-6` → the made-up check chain (PP010822E → GASHER check → PP450822E) lying fore-and-aft on the pump's west flank → `water-5` → the `water-in` cap conduit; flavor manifold built per [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) (V-C/D source-select → pumps → reservoir fill/draw and dispense valves), including the four runs onto the reservoirs' own fill and draw conduits; three risers (carbonated water off the `carb-water-out` conduit, flavor A, flavor B) climbing to the three PP1208E umbilical bulkheads on the +Y wall; Multiplex atmospheric vent through the black adapter stack and 4 mm OVER bulkhead to the dedicated faucet outlet over the sink bowl.

Not in scope: cold-core internal plumbing — the TAISHER carbonator-port elbows, the bottom-plate PTC adapters (PI010822S for CO2, PP010822E for water), and every line run inside the shell between a carbonator port and its cap conduit — all installed inside the cold core during [`cold-core.md`](/hardware/assembly/cold-core.md). The plain bottom CO2 opening and the top water-inlet jet are specified by [`pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) and [`water-inlet-jet.md`](/hardware/assembly/water-inlet-jet.md). Refrigerant lines — already done in [`refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md). Above-counter umbilical — already done in [`faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md). Customer-side tap and CO2 connections — install-time, not assembly. Solenoid and pump wiring — owned by [`wiring.md`](/hardware/assembly/wiring.md); this doc lands every electrical actuator in its plumbed position but leaves the leads loose for the wiring step.

## Inputs per appliance

Per-unit BOM lives in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3 (water inlet), §4 (CO2 subsystem), and §8 (flavor subsystem). Status (ACQUIRED / ON-ORDER / LIKELY-TO-BUY) for every item lives in [`/hardware/ledger/purchases.md`](/hardware/ledger/purchases.md) under the same sections. The table below is the procedure-level summary; bom.md is the source of truth for per-unit allocation and cost.

| Item | Source | Use |
|---|---|---|
| John Guest PP1208E 1/4" OD black PP push-to-connect bulkhead union | B00JYFU8MM | **Customer-facing water inlet on the +Y wall.** Customer plugs the install-kit 1/4" LLDPE into the outboard side at install time; the install-kit Waterdrop 15UC-UF filter mounts customer-side, inline upstream of this bulkhead ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3) |
| John Guest Speedfit ASVPP1LF angle stop adapter valve, 3/8" × 3/8" × 1/4" | B003YKF2JC | Install-kit tee, **scenario B (older home)**; threads between customer's existing 3/8" angle stop and its braided riser, offering a 1/4" push-to-connect branch for the appliance's LLDPE |
| John Guest PP0208E 1/4" × 1/4" × 1/4" union tee, black PP | FWS WEBFWS100677333 (ACQUIRED, see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3) | Install-kit tee, **scenario A (modern home)**; drops inline into an existing 1/4" LLDPE under-sink line, push-to-connect, no tools. Black-PP NSF 51+61 food-cert family for this water connection |
| GAGIRA 316L SS 3/8" NPT F × 1/4" NPT F reducing coupling | B0G2XJGZMQ (5-pk) | Upstream adapter chain — between the customer-side 1/4" LLDPE (downstream of filter, downstream of the PP010822E above) and the ASSE 1022's 3/8" MPT inlet. 316L SS, ships with Teflon tape |
| Multiplex 19-0897 ASSE 1022 backflow preventer | midwestbev | Tap-water backflow preventer; sits between the upstream adapter chain (3/8" MPT inlet side) and the outlet stack → 1/4" LLDPE → split (3/8" MFL outlet side) |
| John Guest PI4512F6S 3/8" FFL × 3/8" PTC + PP061208W 3/8" stem × 1/4" PTC | FWS (`bom.md` §3) | Multiplex 3/8" MFL outlet → 1/4" LLDPE. Two fittings, because no potable single-piece 3/8"-flare × 1/4"-push adapter exists; the 3/8" run starts and ends inside them (modeled as one stack in `reference/flare38-14ptc/`) |
| John Guest PP0208E 1/4" union tee — water split | FWS (`bom.md` §3) | The split one tube-length forward of the ASSE's 1/4" outlet: its run takes `water-2` in at the aft collet and carries the flavor tap out at the forward one, and its downward branch turns V-K's share (modeled in `reference/water-split/`) |
| G Ganen diaphragm pump, received sample | B07F35PTFR; [measured reference](/hardware/reference/g-ganen-pump/README.md) | Selected water pump; mounts on four sliding removable rubber feet. Installed discharge points toward enclosure −X. |
| [Printed diaphragm pump elbow](/hardware/printed-parts/diaphragm-pump-sleeve/README.md), Siraya Tech Flex TPU 85A Clear | Printed in-house | 2 per build — one pushed onto each G Ganen barb, turning the line 90° inside itself onto 1/4" LLDPE |
| YDS butterfly hose clamp, 10–16 mm, 9 mm band | [B07C33VLQ6](https://www.amazon.com/dp/B07C33VLQ6) (10-pk) | 4 per build — one on each elbow socket, flush with its mouth. The fit and pressure trial's clamp; the shipped clamp follows that result (see Open items) |
| GASHER 1/4" NPT check valve, **male × female** | B0FV2D2FFX (2-pk) | One on the water path and one downstream of the CO2 regulator. The documented arrow is female socket → male stub; confirm it on the supplied part. Exact body and seat materials, pressure rating and reverse sealing require source verification for the owned SKU; see Open items. Placement in [`cold-core.md`](/hardware/assembly/cold-core.md) "Warm-side check valves" |
| John Guest PP450822E 1/4" OD × 1/4" NPT **F** connector, black PP | FWS (`bom.md` §3) | The one joint on the water path that faces a male thread: the GASHER's male outlet stub. Same black-PP NSF 51+61 family as the PP010822E |
| Interstate Pneumatics WR1105 fixed 3-bar (43.5 PSI) secondary regulator, 1/4" NPT | B0CGFCJNMG | Secondary on the CO2 path, upstream of the GASHER check; fed and drained by tube and retained in its existing bracket. The same body as the scanned WR1110 the bracket is bored for |
| John Guest PP010822E 1/4" PTC × 1/4" NPT M adapter | FWS, 10-pk | 4 water connections per build: ASSE inlet chain, the water check's inlet, carbonator water-inlet elbow and carbonated-water outlet. Water only. |
| John Guest PI010822S 1/4" PTC × 1/4" NPTF M adapter, gray acetal | Owned FWS stock; [`bom.md`](/hardware/ledger/bom.md) §4 | 4 CO2 connections per build, one in each female NPT port: WR1105 IN, GASHER inlet, bottom carbonator elbow, and the shipped primary regulator's outlet. Two are installed here; the third is inside the cold core, and the fourth goes into the regulator at [acceptance](/hardware/assembly/acceptance-and-burn-in.md) step 1. |
| John Guest PI450822S 1/4" PTC × 1/4" NPTF F adapter, gray acetal | FWS WEBFWS100708594; [`bom.md`](/hardware/ledger/bom.md) §4 | 2 CO2 connections per build, one on each male NPT outlet: WR1105 OUT and GASHER outlet. |
| Beduan 12 V 1/4" NC solenoid valve | B07NWCQJK9 | [10](MANIFOLD_VALVES) valves per build — V-A through V-J per [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) |
| John Guest PP0208E union tee, 1/4", black PP | FWS WEBFWS100681220 (see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §8) | [2](MANIFOLD_TEES) Tees per build — Y-A and Y-B per [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md). Y-A and Y-B stand on the two inner source limbs. Y-C, Y-D, Y-F and Y-G are one-piece printed TPU junctions. Neither reservoir has a junction. Same JG black-PP NSF 51+61 family as the §3 install-kit tee |
| Kamoer KPHM600-SW3B17 12 V peristaltic pump | B09MVPJXFJ | 2 complete pumps per build, located in the fitted cradle wells and retained by the broad `enclosure-pump-cap` ([`printed-parts/enclosure/pump-tray/`](/hardware/printed-parts/enclosure/pump-tray/README.md)); the assembled cartridge slides into the front bay with both pumps aboard |
| Female faston receptacles (pump leads) | [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11 | Pump-lead electrical connection — two differential motor pairs on DC-5's four cartridge leads from the contact pair's female half, kept on the pump tabs through cartridge service |
| 1/4" OD LLDPE tubing — **four spools**, white / blue / red / black | FWS neoFlo, one shelf and one price (see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3, §4) | Every line run in this procedure. Which spool a run is cut off is what it carries: **white** the tap water (+Y wall's bulkhead → ASSE chain → split → V-K → G Ganen → `water-in`, and the split's flavour branch through the flow regulator to V-A), **blue** the carbonated water (`carb-water-out` → DIGITEN → the blue-ringed union), **red** the CO2 (ABU44 → WR1105 → GASHER → `co2-in`), **black** the flavour manifold and the two risers off it. Struck once in [`_routing.SPOOLS`](/hardware/scripts/_routing.py), which reads the rear face's own `port_colors`, so a line and the ring around the hole it leaves by are one colour |
| ASSE sleeve ties, 4-inch nylon, 2.54 mm wide | Owned stock (see [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §11) | Two per sleeve, one on the vent barb and one on the 4 mm tube, in separate recessed lands |
| Zip ties | B0BC1VH4XB (200-pk) | The 4-inch ties on the flow regulator's rib, and the tube-management ties of §5 |
| Anchor cap | Printed PET-GF ([`printed-parts/enclosure/anchor-cap/`](/hardware/printed-parts/enclosure/anchor-cap/README.md)) | Five per build, one on each 1/4" tube rib: `carb-1`'s and `co2-2`'s crossings under back-top's top wall, `fluid-28`'s on its −X wall, and `fluid-14`'s and `fluid-18`'s on the cold core's lid |
| Millrose 70894 PTFE thread-seal tape | B07C9ZV4PG | Anti-seize on every NPT joint cut in this procedure (≥8 joints per build across water + CO2 paths) |

Tooling: Mudder PTFE tubing cutter (the cold kit's own SKU, [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §14, used here at the bench), 5/16" hex-driver and crescent wrench for the NPT joints, and scissor for the clear-PVC vent stub cut-to-length.

## Procedure

The section numbers follow the three fluid systems; the physical build does not. Run §3 steps 1–3 first on loose `enclosure-front-top`, then close the enclosure around that subassembly. Make the CO2 and water paths at the bench/cart stages their bodies expose, complete §3 step 4 when the closed chassis accepts the pump cartridge, and land the three risers last after the manifold and service bay establish their routing space.

### 1. CO2 path: the +Y wall's ABU44 → WR1105 → GASHER → `co2-in` cap conduit

The required flow order puts the check **after the regulator**, with its arrow toward the carbonator. The bottom gas port is below the water line, so the check must stop reverse water flow before it reaches the WR1105. Confirm the ABU44 bulkhead is clamped through the +Y wall per [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md); the customer's red tether enters its outboard collet and `co2-0` enters its inboard collet.

**Use gray-acetal John Guest fittings at all five CO2 NPT-to-tube transitions:** a PI010822S male connector in each female port, a PI450822S female adapter on each male outlet. [John Guest specifies the gray acetal range for CO2 beverage gas, air and inert gases](https://www.johnguest.com/ca/en/od-tube-fittings/acetal-gray/threaded-connectors/male-connector-nptf-thread). The [John Guest catalog](https://www.johnguest.com/sites/default/files/files/JohnGuest-Fluid%20System-Catalog-2025.pdf) excludes the PP range from compressed-air service; PP010822E and PP450822E belong on the water paths here.

Make up the warm components with supported wrench flats and thread sealant applied according to the fitting instructions:

1. A PI010822S into WR1105 **IN**, its female socket, and a PI450822S onto **OUT**, its male stub. The body's flow arrow points from the socket toward the stub.
2. A second PI010822S into the GASHER's female inlet; verify the supplied body's flow arrow points from that socket toward its male outlet.
3. A second PI450822S onto the check's male outlet. The third PI010822S is on the cold-core bottom gas elbow, fitted in [`cold-core.md`](/hardware/assembly/cold-core.md).

**The downstream check placement and three warm red hose routes require a made-up fit record.** The nominal CAD layout keeps the WR1105 in its existing bracket and places the check alongside it above the G Ganen pump, supported at its round inlet boss by a tied ceiling cradle. The regulator-to-check hose turns forward in a U; the check outlet returns through the east lane to `co2-in`. [`_gas_chain.py`](/hardware/manifold-layout/_gas_chain.py) includes the four warm adapters at nominal envelopes. The body's exterior and 9.18 mm outlet stub follow two native scans of the WR1110 ([measurement record](/hardware/reference/wr1110-regulator/README.md)); its cradle is centred on the measured 35.4 mm barrel. The actual PI010822S and PI450822S made-up reaches and received GASHER dimensions remain unmeasured. Verify the completed stack, support, wrench clearance, tube insertion lengths and hose bends against the enclosure before assembly; the CAD clearance checks do not qualify those received parts. Keep the WR1110 bracket and enclosure envelope fixed.

**What holds the regulator is a rib printed off the top wall** (`enclosure._tube_anchors`, [`printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md) "Tube anchors"), bored concentric with the **barrel between its two wrench hexes** and stopped on the barrel's axis plane so its lip is a flat face one wall deep. Thread a **6" zip tie** through the cavity in the middle of that rib and leave it lying open before the regulator goes up — the channel's roof is the rib's own back, and there is no reaching under it afterwards. Lift the barrel into the bore until it beds all the way round, close the tie round barrel and rib together, and flush-cut it — barrel and rib make an [83.2 mm](WR1110_LOOP) loop, past what a 4" tie closes. **Cinch on the barrel only** — never on either wrench hex, which is where a socket has to go to break the joint. The seat opens downward, so **the zip tie is what carries the regulator** and the bore is what it pulls into: tug-test it, the same as the flow meter's two anchors.

Cut the three runs from the **red 1/4-inch LLDPE reel** using the qualified placement:

- **`co2-0`:** ABU44 inboard collet → WR1105 IN adapter.
- **`co2-1`:** WR1105 OUT adapter → GASHER female-inlet adapter.
- **`co2-2`:** PI450822S on the GASHER outlet → `co2-in` cap conduit → the cold-core gas elbow's PI010822S.

Square-cut every tube end, allow the measured insertion depth at each collet, push fully home and tug-test. The cap conduit guides a continuous tube; it is not a sealing fitting. `co2-2`'s crossing between its two bends under the top wall lies in a rib with a catch window in each flank (`enclosure._capped_anchor`): lay the tube up into its bore and press an [anchor cap](/hardware/printed-parts/enclosure/anchor-cap/README.md) straight onto it, a wing either side, until both lips click into their windows. Tug the tube and the cap. Thread one **6-inch 18 lb zip tie** through the empty local check cradle before placing the made-up check. Seat its round metal inlet boss in the cradle, close the tie and flush-cut it, keeping the adapter and wrench flats clear. The nominal cradle loop exceeds the documented closed-loop reach of a 4-inch tie. Retain the crossing runs without loading a plastic collet, and record clearance with the electronics deck and enclosure closed. The downstream portion must tolerate carbonator pressure and wet reverse exposure. Verify the owned check's materials and reverse sealing per Open items before qualifying it for this duty.

Below the conduit, the line and bottom elbow are already installed by [`cold-core.md`](/hardware/assembly/cold-core.md). The elbow feeds the plain Port 1 opening. Gas enters below the water only while the regulator-to-carbonator pressure difference permits flow, and rises toward the headspace. There is no internal barb, silicone hose or stone. Pressure and reverse-leak checks are performed at [`acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md).

### 2. Water path: the +Y wall's PP1208E → adapter chain → ASSE 1022 → split → V-K → G Ganen → `water-in` cap conduit

The customer-facing water inlet on the +Y wall is a **1/4" JG QC bulkhead** (PP1208E — same SKU as the umbilical cluster). At install time the customer plugs the install-kit 1/4" LLDPE into the outboard PTC side — no build work on that side beyond confirming the bulkhead is installed and the wall-side EPDM O-ring is seated. The work below closes everything inboard of the bulkhead. **From the ASSE 1022 outlet on, the path is 1/4" LLDPE, and a printed TPU elbow on each of the G Ganen's barbs takes that tube straight onto the pump.**

**Every length in this section is cut off the white reel** — `water-2`, `water-3` and `water-5` through `water-7`, and the flavour circuit's own tap-water leg `fluid-1`/`fluid-2` below, up to V-A.

**Mount the G Ganen on its four identical purchased rubber feet while the cap is accessible.** Their nominal 7 mm pads slide along the casing rails and can be removed. The slot centres stand at reference X = 9.5 and 67.5 mm, Y = ±38.5 mm, with each clip fully engaged at its rail end. These are selected full-engagement positions, not claimed hard stops. Reference +X runs from the motor/head junction toward the motor rear. Seat the bearing faces on the lid and place each M3 × 20 screw 1.5 mm outward within its slot, so its Ø9 × 0.8 mm washer clears the raised shoulder. Align those screw axes with the printed cap columns. Verify actual screw passage, flat washer seating, engagement and rubber compression as the mount closes. The installed pump sends flow toward **enclosure −X**: suction faces east and discharge faces west. The [installation reference](/hardware/reference/g-ganen-pump/installation/README.md) supplies the measured ports, mounting axes and native checks.

**The whole tap-water head end runs fore and aft in the west lane, on two storeys.** The ASSE chain hangs in the lane west of the pump, hugging the cold core's west face, inlet aft at the +Y wall and flow running forward. `water-2` carries the water forward off its outlet and a step down onto the tap's own storey, where the split stands; the flow regulator stands directly OVER the split on that same column, and `fluid-1` is the hairpin between the two. Both bodies' flows lie fore and aft along the lane, so the only mouth in the head end that is not on that axis is the split's branch, which looks straight down at the storey the pump and the manifold stand on.

The PP010822E → GAGIRA → ASSE 1022 → PI4512F6S → PP061208W run and its vent stub are modeled as one piece in [`/hardware/reference/asse1022-assembly/`](/hardware/reference/asse1022-assembly/) — the stack-up, the three terminals (1/4" PTC in, 1/4" PTC out, vent), and which way the vent has to face.

Confirm the PP1208E is installed on the +Y wall per [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) with the 1/4" QC on both sides (push-to-connect, no tools required at install). The Waterdrop 15UC-UF filter is customer-side hardware — it ships in the install kit and mounts inline on the customer's 1/4" LLDPE upstream of this bulkhead ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3) — so no build work touches it.

**There is no `water-1`.** The chain stands off the +Y wall by exactly what the union reaching through it leaves, so the bulkhead's inboard collet and the ASSE chain's inlet collet meet face to face down one axis with nothing between them to turn. The first tube in the machine is a length of stock cut to the two grips and swallowed whole by them: square-cut both ends, push fully into both collets, tug-test.

The ASSE 1022 inlet stack is made up on the chain at the bench (modeled in the asse1022-assembly reference): the PP010822E's 1/4" NPT M side threads into the 1/4" NPT F side of the GAGIRA 316L SS reducing coupling (PTFE tape, snug + 1 turn past hand-tight); the GAGIRA's 3/8" NPT F side threads onto the ASSE 1022's 3/8" MPT inlet (tape on the MPT threads, snug + 1 turn). Multiplex flow arrow points away from the customer side. On the outlet, two John Guest fittings make up the flare-to-1/4" stack: the **PI4512F6S** 3/8" FFL × 3/8" PTC adapter draws up onto the ASSE 1022's 3/8" MFL outlet via its chrome swivel nut — flat-faced flare seal, no PTFE tape, quarter turn past hand-tight on the swivel only (never turn the body against the flare) — and the **PP061208W** 3/8"-stem × 1/4" PTC reducer pushes into its collet. The 3/8" run begins and ends inside those two fittings; the reducer's 1/4" PTC collet faces **forward** down the west lane, and the water leaves the backflow preventer at 1/4" OD.

**Lay the made-up chain into its anchor.** The −X wall carries a stepped cradle for it (`enclosure._asse_cradle`, [`printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md) "Tap-water cradle") — three 120° V sections, one per section of the chain, cut so the brass barrel sits deepest and the steps either side of it are faces square to the axis. Bring the chain in from the east and press it west into the V until the barrel's two lower flats bed on the anchor's two faces; the barrel's forward end face comes up against the step under the swivel nut with `ASSE_STEP_SLIP` of play, and aft the inlet collet butts the bulkhead's, which is where the run's own length is taken up. **The vent's clock is the fit.** The Multiplex's hex does not spin on the run, so a barrel bedded flat in the V has its vent pointing at the tray by construction — a chain that will not sit down in the anchor is a chain rolled off its flats, and forcing it is how the drip ends up outside the coves.

Then close the mouth with **two 8" 50 lb zip ties** — barrel and anchor make a 105 mm loop, past what a 4" tie closes, and an 8" is a 50 lb tie at 0.19" across the zip tie, which is why this cavity is cut wider than the others on the box — one in each band the vent leaves clear on the barrel, each **threaded down the bore through the anchor's back before the chain goes in**, then laid across the channel the deck's own storey leaves under the top wall, so the chain comes down onto the zip tie rather than the zip tie being fished over it afterwards. Bring each end round under the barrel and up its east flank to buckle. **Brass barrel only** — a tie cinched on the JG acetal flare adapter or the PP reducer takes a collet out of round. Black UV-nylon, flush-cut, no proud tail, per [`cable-assemblies.md`](/hardware/assembly/cable-assemblies.md). They stop the chain leaving the anchor eastward and nothing else: what carries it is the V, on two flats of the fitting's own hex, so a cut tie is a service step and not a failure.

**Set the water split into its rib.** A JG PP0208E 1/4" union tee (modeled in [`/hardware/reference/water-split/`](/hardware/reference/water-split/), using the measured fitting reference shared with the manifold's two purchased source tees). The −X wall of `enclosure-back-top` prints a seat for it, bored for the round barrel between the tee's hub and its supply collet, with a zip tie channel behind the bore ([`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) `BODY_ANCHOR_SITES`). Thread one **6 inch, 18 lb zip tie** through the channel before seating the fixed collar. Close it around the collar and rib, with the lock on the exposed +X crown; the shortest loop is [74.9 mm](SPLIT_LOOP). Keep the complete 2.5 mm tie band on the fixed collar and the terminal collet free to move. Its two run collets lie fore and aft, supply aft and flavor tap forward, and its **branch is rolled to look straight down**.

Cut segment **water-2**: the chain's outlet collet aft on its own level stub, then one lean forward, west and down onto the split's storey, and a level stub into the supply collet — two corners, because the split stands a step under the chain and a lane inboard of it. Both stubs are level and long enough for their own corner to seat in. Square-cut, push fully home, tug-test.

Mount **V-K** — the Beduan 12 V NC fill/shutoff solenoid — in its cradle on the cold core's crown on the machine's east flank, forward of the pump and **firing aft** along `water-7` to the suction elbow; its own frame already runs the flow inlet-forward / outlet-aft, so it takes no turn. Wire its coil per run DC-9 in [`ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md). Normally closed, so a leak alarm or a power loss stops all water reaching the carbonator. Cut segment **water-3** — off the split's **downward branch collet**, falling once on the branch's own column and **past** the lane it feeds, then forward and west in one leg into the channel between the enclosure's west wall and the cold core's shell, rising onto the core's front lane as it goes, east across the machine beneath the funnel frame and through the cap's own side post, and one lean forward onto V-K's column. Four corners, every one at stock. The fall ending under that lane rather than on it is what stands the split and the flow regulator as low as they do: what a fall costs the fitting above it is its corner's tangent and not its length, so a corner that bottoms out low starts low. Square-cut, push fully home, tug-test.

**Fit the pump's two elbows** — the [printed TPU elbow](/hardware/printed-parts/diaphragm-pump-sleeve/README.md), Siraya Tech Flex TPU 85A Clear, one on each barb. Look through both sockets and the corner passage of each against a light and clear any strand first: a loose strand in the suction elbow reaches the pump's own valves, and one in the discharge elbow the water check's seat. Slide one open YDS clamp over each socket, then push the barb socket onto the barb until the barb tip stops on its shelf; warm water eases the stretch, and the barb takes no oil. Clock the **suction elbow** on the **east-facing suction barb** so its tube leg points straight **forward**, at V-K's outlet, and the **discharge elbow** on the **west-facing discharge barb** so its leg points forward and [25°](ELBOW_DIP) **down**, under the gravity drain's route. Seat each barb clamp's band flush with the barb mouth, its housing turned away from the tube leg, and tighten by hand until the cuff grips without being cut.

Cut segment **water-7** from V-K's outlet to the suction elbow: ~[69 mm](SUCTION_TUBE_LEN) of exposed route, plus V-K's collet grip and the elbow's [15 mm](ELBOW_TUBE_DEPTH) socket. The tube leaves V-K's collet straight aft, crosses a column west and a storey up in one lean, and enters the socket on the leg's own axis — two corners, both at stock. Square-cut both ends and mark the elbow end [15 mm](ELBOW_TUBE_DEPTH) back. Push fully home at V-K's collet, push the other end into the elbow until it stops on its shelf with the mark at the mouth, close the tube clamp's band flush with the mouth without ovalizing the tube, and tug-test both ends.

The flavor manifold draws its tap water off the split's **forward run collet**. **Set the flow regulator into the rib over the split's** — the same seat pattern, bored for the barrel between the regulator's hub and its inlet collet, on the same face and the same column, so the two stand one over the other with the knurled adjuster level and facing east where a hand comes in over the cold core's cap. Thread its **4" zip tie** through the channel behind the bore and leave it lying open before the regulator goes in, the same as the split's below it — barrel and rib make a [65.1 mm](FLOWREG_LOOP) loop, inside the ~69 mm a 4" closes. Close it round the barrel and the rib's own back together and flush-cut it. Segment **`fluid-1`** is the hairpin between the two mouths: both face forward off the pair's own column, so the run leaves one, turns through 180° in the room ahead of them and comes back into the other — two stock quarter-turns with no straight anywhere in it. Bend it on a former or off the reel's own set; a hairpin pinched by hand kinks at the crown.

From the regulator's outlet, segment **`fluid-2`** runs aft, turns east and crosses the lane **level, on the outlet's own storey** — `water-2` comes down that same lane from the chain overhead and passes beneath it, and a run that has spent no height yet is the one that clears it — then comes forward and down the strip west of the nozzle-A line in one leg, and leans east into V-A's inlet. Keep this approach clear of the pump and neighboring lines. Four corners ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) tube segments 1 and 2). No 3/8" barb tee, no reducers — the split is already 1/4".

The Multiplex atmospheric vent connects to the dedicated 4 mm OVER circuit. Fit the [printed TPU sleeve](/hardware/printed-parts/asse-drain-adapter/README.md) directly over the vent barb and marked 4 mm tube end, with one four-inch tie on each joint, per [ASSE drain assembly](/hardware/assembly/asse-drain.md). Route the internal white return through two R25 bends into the black ABU44M-E bulkhead. Its open discharge is at the faucet, near the gooseneck joint and over the bowl. Keep that outlet and the complete vent route unobstructed; confirm marked insertion, sleeve retention and bend clearance on the made-up hardware. The sleeve remains an unprinted fit candidate.

Make up the **discharge chain** on the bench as one piece — PP010822E → GASHER → PP450822E, modeled in [`/hardware/reference/seaflo-discharge-chain/`](/hardware/reference/seaflo-discharge-chain/), [73.5 mm](DISCHARGE_CHAIN_LEN) made up. The PP010822E's 1/4" NPT M threads into the GASHER's female socket (PTFE tape, snug + 1) with the check's arrow pointing **away** from the pump; the GASHER's male stub threads into the PP450822E's female (PTFE tape, snug + 1). Thread a **6" zip tie** through the rib on the cold core's cap lid, west of the pump, and leave it lying open across the channel — it goes in before the chain does, because the channel's roof is the rib's own back and there is no reaching under it afterwards. Then lay the chain **fore-and-aft into that rib**, its bore taking the GASHER check's hex — **PP010822E collet aft**, looking back at the discharge elbow; **PP450822E collet forward**, looking down the deck at the cap conduit it feeds. The bore takes any clock, so the check's hex needs no orienting; what it owes is the arrow. Close the tie over the check's hex barrel only — a tie cinched on a PP socket, hex or collet takes it out of round — and flush-cut it. **The rib carries the chain and the tie only holds it down** — cut the tie and the chain still lies where it lies.

Cut segment **water-6** from the discharge elbow to the chain's inlet collet: ~[42 mm](DISCHARGE_TUBE_LEN) of exposed route, plus the elbow's [15 mm](ELBOW_TUBE_DEPTH) socket and the collet's grip. The tube leaves the elbow down its leg's own axis, turns once onto the chain's column and once onto its axis, both at stock. Mark, seat and clamp the elbow end the same way as `water-7`, push the other end fully home at the collet, and tug-test both ends.

Cut segment **water-5**. The chain's PP450822E collet looks **forward** off the far end of the laid-down chain, and the `water-in` cap conduit opens on the lid a short reach ahead of it and a little to the east. The tube leaves the collet straight on its own axis and comes down onto the bore on the vertical it is drilled at — two gentle turns rather than one square one, each taking the full arc 1/4" LLDPE wants, so this line turns at stock, and its height only ever descends. Square-cut both ends, push fully home at the collet, lay the far end into the conduit, tug-test both.

The water path is now closed dry from the +Y wall to the cold core's crown. Everything below that conduit is already inside the shell from [`cold-core.md`](/hardware/assembly/cold-core.md) step 5 — the top-plate TAISHER elbow with its PP010822E made up on the lateral female end, the tube running the shallow band between the top plate and the cap's floor, and the climb up the conduit. The carbonator is **filled high**: the [water-inlet jet](/hardware/assembly/water-inlet-jet.md) is the final passage at the elbow's downward male tip, after the 90° turn. The qualified cap sends water directly through the headspace toward the liquid. Its bore, clearance and weld qualification are recorded before this elbow enters the cold core.

### 3. Flavor manifold: V-A through V-J + Y-A, Y-B, Y-C, Y-D, Y-F, Y-G + pumps

Build to [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) segment-for-segment. The truth table there names every valve, every Y-junction, and every tube segment by number; this step describes the build cadence around that truth table, not its content.

**This step begins on the bench with `enclosure-front-top` open and both valve rows absent.**
The two valve trays and four one-piece TPU pump junctions are stationary. The permanent TPU
junction inlets pass through the bay wall; their recessed collars locate against the wall and three
flat interior keepers capture their rear grooves. The receiver funnels are the only surfaces
the four cartridge tube tips enter. The [pump service procedure](/hardware/service/pump-replacement.md)
describes the separating joints and the complete prepared pumps supplied for a customer swap.

**V-A and V-B stand on the cold core's cap.** Their two forward runs reach Y-A and Y-B across
the Y seam. Build those connections while the core and front-top remain accessible.

Lay out the ten Beduan valves, two PP0208E tees, four TPU junctions and four TPU
compound returns with port directions visible. Cut the
stationary links from the [current manifold geometry](/hardware/manifold-layout/README.md),
including engagement at both real fittings. Exposed path length is not a tube-blank cut
length. Use black LLDPE except for `fluid-3`, V-A's outlet into Y-A, which uses white tube.
Square-cut, deburr without scoring the outside sealing surface, and tag each segment.

1. **Fit the aft valves.** Install the RX-M3Sx4.0 inserts in the three tray-foot
   bosses before fitting TPU.
   Bring V-C, V-D, V-G and V-J through front-top's open underside, align their mounts,
   then seat them along their posts. Match the topology's ports and coil clocks,
   then close the retaining ties. For each return-to-valve link,
   first seat uncut tube fully into the actual valve, mark its collet face, then
   cut 8.5 mm beyond that mark: 2 mm exposed plus 6.5 mm insertion into TPU.

2. **Seat the upper groups and fit the keepers.**
   Inspect each TPU bore and funnel for continuous, clean material. For each fore
   valve, seat uncut tube fully into the actual valve, mark its collet face, then
   cut [21.001 mm](DOCK_UPPER_TAIL) beyond the mark: [14.501 mm](DOCK_FORE_LINK)
   exposed plus 6.5 mm insertion into the TPU upper socket. Connect the junction,
   straight link and corresponding fore valve off the wall. Bring this group
   forward along −Y, seating the valve onto its +Y-facing posts while folding the flexible
   funnel through its wall opening and allow it to recover fully on the pump side. Seat
   the locating body and recessed collar against the wall. From front-top's open
   underside, push each flat keeper into its slot at the seam face, keyholes first,
   and slide it along the wall's interior face until every receiver neck it holds
   snaps through the keyhole's mouth into its grip: one keeper for each outer receiver
   and one for the inner pair. The keeper's foot finishes just inside the seam face.
   Confirm that each funnel has recovered and each receiver remains captured when
   pushed and pulled along Y. The wall locates X/Z. For factory service, a flat blade
   entered through a receiver bay from aft presses the keeper's crown back down off
   its necks.

3. **Assemble the lower returns and fit the return block.** Match each junction and
   compound return to its station. Cut the straight junction-to-return tube from the
   actual mounted stop span, targeting 0.15 mm total axial play. Fit the straight link
   into the junction before seating the return.
   Hold the return 6.5 mm below its final position,
   with the vertical socket coaxial with the valve tail. Start the diagonal tube
   in both sockets, then raise the return straight onto the valve tail. The
   diagonal tube temporarily takes a shallow S during this unpressurized motion;
   the checked minimum radius is 34.2 mm at the outer stations and 79.2 mm at the
   inner stations. It finishes straight. Perform this factory fit with front-top
   loose, before joining it to the condenser/compressor half.
   Keep every link straight and the valve collets
   accessible. Keep all links clear of the wall, keeper, neighboring fittings and
   cartridge envelope. Tug-check
   each push-fit connection without using a valve or receiver as a lever. Confirm
   that the TPU returns recover without visible distortion.
   Bring the one return block onto all four returns from front-top's open underside,
   top face first, until that face seats on the aft tray foot. Each return squeezes
   through its slot and snaps into its seat. Drive the three M3×12 screws through
   the block's counterbores into the tray-foot inserts. Confirm that each return sits
   in its seat and cannot be lifted out by hand.
   Printed-part recovery and seal performance remain
   subject to the pump-dock's physical qualification.

4. **Build and prepare the Kamoer cartridge.** Pull Kamoer's barbed connectors out of
   both pumps' tube ends and push a 26 mm stub of black 1/4" LLDPE into each BPT end
   under the loosened pump-head housing. Lower both complete pumps into their fitted
   wells with the stubs facing +Y through the cradle's open tube passages. Set the
   free tips to the [prepared-pump datum](/hardware/service/pump-replacement.md#factory-preparation-of-replacement-pumps)
   with the printed tube setting jig against the cartridge's flat rear face,
   then tighten each housing so it clamps the tube around its stubs. Keep the exposed
   stubs straight and verify all four tip positions, a firm hand pull on each stub and
   pump-end sealing before closing the clamp. The customer's replacement pumps receive
   this same factory preparation.

5. **Fit the electrical contact and clamp.** Install the cap's two M1.4 inserts with
   their tops [5.125 mm](POGO_INSERT_HOST_DEPTH) inside its aft printed face, [2 mm](POGO_INSERT_SETBACK) behind the recessed ear-bearing datum, using
   the recessed-seat procedure in
   [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) §1. Solder four
   ~100 mm 22 AWG leads to the female contact half and mount it in the cap with its marked
   end at −X. Seat the two M1.4 × 8 screws with the hand-operated 1.3 mm hex driver,
   stopping with the ears flat. Lower the broad cap over both pump bosses and draw its
   [2](CAP_SCREWS) M3×[60](CAP_SCREW_LEN) screws evenly into the cradle's center inserts.
   Verify firm pump retention without vertical play within the
   [accepted holder scope](/hardware/reference/kamoer-kphm400/physical-fit.json).
   Route the +X groove pair to pump A and the −X pair to pump B; the four leads are
   `AM2`, `AM1`, `BM2`, `BM1` from +X to −X. Crimp their female Faston receptacles and
   connect them to the marked motor tabs. Keep all leads below the crown.

6. **Verify the closed dock after chassis assembly.** Inspect both parts' bonded
   magnet columns and their exposed attracting faces. With power disconnected, slide the
   cartridge on its floor and present all four tube ends squarely to the TPU funnels. Push
   evenly until the magnets draw the cartridge onto its seat and it finishes flush. Confirm
   that every receiver remains seated, every tube enters straight and the pogo pair reaches
   its designed compression. The meeting magnet poles establish closure, with
   [0.25 mm](DOCK_BODY_GAP) of air between the broad aft planes. Withdraw and reinsert
   straight to confirm that the four slip joints separate together while the permanent
   junctions, returns and keepers remain fixed. Magnetic attraction alone does not establish
   sealing.

Y-A and Y-B remain on the inner limbs with their branches facing one another across the
mirror plane. V-A's inlet takes the water split through the flow regulator. V-B's inlet
takes `fluid-4` from the fixed PP0308E elbow beneath the funnel frame. No reservoir has a
junction: V-F/V-E reach reservoir A's fill/draw conduits and V-I/V-H reach reservoir B's.

Route and retain fixed spans while the front-top is accessible. The four reservoir lines
land on the cold core's own cap conduits: `fluid-14` to `reservoir-a-fill`, `fluid-24` to
`reservoir-b-fill`, and `fluid-16`/`fluid-26` from the draw conduits into V-E/V-H. Each draw
line is its reservoir's dip tube: cut it long enough to reach the reservoir's floor, cut that
end at 45°, straighten it by hand, and feed it down its draw conduit and the cap's draw bore
until the tip touches the floor
([floor and dip tube](/hardware/printed-parts/cold-core/reservoir/floor-and-dip-tube.md)).
`fluid-14` lies level over its rib on the lid behind V-A's plinth: press it into the bore and
an [anchor cap](/hardware/printed-parts/enclosure/anchor-cap/README.md) down over it until both
lips click, then tug the tube and the cap.
Dress and tag their front-top ends on the bench; land their core ends on the open cart before
the back assembly closes. Maintain the hairpins' relaxed bend radii and access to their
fixed collets.

The carbonated-water riser leaves `carb-water-out` directly for the rear blue-ringed
bulkhead through the DIGITEN meter. Flavor A leaves V-G on `fluid-18`; flavor B leaves
V-J on `fluid-28`. Complete these routes in step 4.

### 4. Risers up to the umbilical bulkheads on the +Y wall

Three risers climb to the three PP1208E umbilical bulkheads on the +Y wall per [`/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md`](/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md). **The three stand on one row** high on the +Y wall, under the umbilical and above the water inlet: flavor B outboard on the west, flavor A beside it, and the **blue-ringed bulkhead** for carbonated water east of the pair.

- **Carbonated-water riser:** 1/4" OD blue LLDPE from the cold core's `carb-water-out` cap conduit to the blue-ringed PP1208E, in two lengths with the **DIGITEN flow meter** made up between them. The conduit opens **up** through the lid on the machine's east flank; segment **`carb-1`** climbs off it and leans inboard and aft over the deck, two corners, closing forward into the meter's inlet collet. The meter lies **fore-and-aft, [3 mm](DIGITEN_WEST_SET) west of the carb union's column**, below the port row so its measured cover clears the ceiling, its pigtail boss facing **+X** toward the main board it plugs into — its two collets are the riser's, so the body splits the run in two rather than hanging off it. It hangs in **two anchors printed off the top wall**, one over each fixed port collar with nothing over the housing between them (`enclosure._flow_meter_anchors`, [`printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md) "Flow-meter anchors"): lift each barrel up into its bore until it beds all the way round, and close each anchor with **one 6" zip tie** threaded through the cavity in the middle of the rib over the bore and round under the barrel — arm and anchor make a [81.2 mm](DIGITEN_LOOP) loop. **Both zip ties carry the meter** — a seat that opens downward holds nothing on its own — so tug-test each one and leave the full [3.7 mm](DIGITEN_COLLET_FREE) movable collet clear of the anchor. Aft of the meter, **`carb-1`'s own crossing is anchored** at the head of its climb, just past the corner where it turns under the top wall: a rib printed off that wall carries a bore concentric with the tube, stopped on the tube's axis plane so its lip is a flat face one wall deep, with a catch window in each flank (`enclosure._capped_anchor`). Lay the tube up into the bore and press an **[anchor cap](/hardware/printed-parts/enclosure/anchor-cap/README.md)** straight onto it, shoulders toward the rib and a wing either side, until both lips click into their windows; the tube then lies in one round pipe. Tug the tube and the cap. The bore is what locates the run; the cap only stops it leaving. Rib and cap close on the bare tube, so the insulation stops at the rib's two ends. Segment **`carb-2`** rises and steps east to the bulkhead through two shallow R14 bends. Its fore/aft gap is 22 mm and its developed length is about 23 mm; keep both ends on the collets' axes. Confirm the housing's physical flow arrow points from `carb-1` toward `carb-2`. Square-cut every end, push fully into all four PTC ports, tug-test each. The CARGEN nitrile-rubber pipe insulation that wraps this line ([`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §9, 1/4" ID × 3/8" wall) goes on cut to each run and slid on from the open ends before either collet goes down (Open #7 below) — not in the 1-ft segments the above-counter umbilical uses. `carb-2` takes one piece; `carb-1` takes two, one each side of its rib, butted against the rib's ends. Insulation continuity from the cap conduit's mouth to the inboard face of the blue-ringed bulkhead, broken only along `carb-1`'s rib, is the target — that mouth is where the thermal mass of the cold core ends and the chilled water enters its multi-meter run to the faucet.
- **Flavor A riser:** segment **`fluid-18`**, 1/4" OD black LLDPE off V-G's outlet. It rises onto the fore cap strip and crosses west over its low lid rib ahead of both cap valves. The west leg passes outside the reservoir-B fill column and discharge-chain rib, returns inboard behind the pump's discharge elbow, over the pump's west-rear foot, and rises onto the rear union's axis. The [9](FLAVOR_A_CORNERS) bends use R14 in the fore approach and R25.4 on the rear return. Bed the crossing's straight in the rib's bore and press an [anchor cap](/hardware/printed-parts/enclosure/anchor-cap/README.md) down over it, its wings into the two slots the lid leaves beside the rib, until both lips click; tug the tube and the cap. The [current fluid review](/hardware/printed-parts/enclosure/pump-dock/fluid-geometry-review.json) records the assembled route. Check the relaxed tube shape and neighboring clearances during the full assembly trial. No insulation is fitted on the flavor line.
- **Flavor B riser:** segment **`fluid-28`**, from V-J's outlet into the west bulkhead. Its [7](FLAVOR_B_CORNERS) bends use R14 in the fore approach and R25.4 on the rear return. Its straight cruise aft lies in a rib off the −X wall ahead of the rear Wago row: press the tube into the rib's bore and an [anchor cap](/hardware/printed-parts/enclosure/anchor-cap/README.md) on over it toward the wall until both lips click, then tug the tube and the cap. The return rises [3.5 mm](FLAVOR_B_RETURN_RISE), passes [16.5 mm](FLAVOR_B_RETURN_WEST) west of the rear union's column above the ASSE drain, then joins the collet on its axis. No insulation.

Black-into-either-black is unambiguous downstream of the manifold (per [`/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md`](/hardware/printed-parts/enclosure/y-wall-of-back-top/README.md) "Umbilical port — tube identification"): both flavor tubes route through the same wall-side bundle and the user does not need to distinguish them at the wall.

### 5. Witness and tidy

Walk every joint built in this procedure. Tug-test every PTC connection. Check both pump elbows: each cuff seated to its barb's shelf, each tube at its mark, all four clamp bands flush with their mouths and gripping, and no whitening or split in the TPU; the vent sleeve uses two independently snugged four-inch ties. Confirm every NPT joint is past hand-tight and has PTFE tape showing at no more than half of the thread engagement (excess tape past half-engagement is a stress concentration). Confirm the vent sleeve and 4 mm return clear neighboring tubes and fittings, with a continuous open path to the separate faucet outlet. Confirm both pumps sit in the cartridge with all four motor Fastons connected and their moving leads retained in the clamp grooves. Complete the fixed J13 contact wiring at [`wiring.md`](/hardware/assembly/wiring.md).

Zip-tie any tube run with a span over ~6" between fixturing points. The enclosure's printed tube channels carry most of the line, but zip ties at the bend transitions and at the pump-mount boundary stabilize the manifold during transport.

The internal plumbing is now ready for [`wiring.md`](/hardware/assembly/wiring.md) (the wiring step lands every solenoid lead, the fixed J13 pump loom and every sensor lead at the electronics bay, but the plumbing itself does not change after this step).

## Output condition

A finished internally-plumbed appliance:

- CO2 path closed dry from the +Y wall's ABU44 bulkhead, `co2-0` to WR1105 IN, `co2-1` from WR1105 OUT to the downstream GASHER check, and `co2-2` from its outlet PI450822S to the cold core's `co2-in` conduit; made-up placement, support and hose clearances recorded
- Water path closed dry from the +Y wall's PP1208E 1/4" JG QC bulkhead — its inboard collet butted to the ASSE chain's inlet — through the PP010822E + GAGIRA 316L SS reducing coupling, the Multiplex 19-0897 ASSE 1022 backflow preventer, the PI4512F6S + PP061208W outlet stack, `water-2` to the PP0208E water split, `water-3` to V-K, `water-7` to the clamped suction elbow on the G Ganen pump, `water-6` from the clamped discharge elbow to the made-up PP010822E + GASHER + PP450822E chain, and `water-5` onto the `water-in` cap conduit
- Multiplex atmospheric vent through the black adapter stack and 4 mm OVER bulkhead to the dedicated faucet outlet over the sink bowl
- Flavor manifold built segment-for-segment per [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md): [10](MANIFOLD_VALVES) Beduan valves, [2](MANIFOLD_TEES) PP0208E Tees, four permanent TPU junctions captured by the wall and three snapped-on flat keepers, four compound TPU returns seated in the one PET-GF return block, and straight captured pump links, plus 2 Kamoer pumps held in the fitted cradle by the broad cap and its [2](CAP_SCREWS) M3 screws
- Pump stubs 11, 12, 21 and 22 engage their permanent TPU receivers with the cartridge on its meeting magnet poles; all four tips retain 0.50 mm to the internal shoulders, and the fixed junctions and returns remain stationary
- All four reservoir runs closed onto their own cap conduits — `fluid-14` and `fluid-24` onto the two fill bores above the liquid, `fluid-16` and `fluid-26` as the two dip tubes, each down its draw bore to its reservoir's floor
- Three risers landing on the three PP1208E umbilical bulkheads on the +Y wall on one row (blue LLDPE on the blue-ringed bulkhead for carbonated water; black LLDPE on the two flavor bulkheads)
- Carbonated-water riser insulated with CARGEN nitrile-rubber pipe foam in segments from the cold-core exit to the inboard face of the blue-ringed bulkhead, bare only along `carb-1`'s rib; the DIGITEN flow meter, its union and the tube tails at both are wrapped in the same foam, slit over the meter body and its cable, with every seam closed by 3M 425 foil tape
- Every NPT joint PTFE-taped and torqued past hand-tight, no thread tape past half-engagement
- Every PTC joint square-cut and tug-tested
- Every elbow clamp hand-tight with its band flush at its mouth — four on the two pump elbows; snug the two vent-sleeve ties without ovalizing the 4 mm tube
- Zip-tied at all long unsupported tube spans and at all bundle pinch-points
- No water in any line; no CO2 in any line; system is primed-ready, not primed

## Open items

Procedure-level gaps that need answers before unit 1 ships:

1. **Pump enclosure-mount mechanism.** The cartridge has two fitted lower wells and one broad cap, closed by [2](CAP_SCREWS) M3×[60](CAP_SCREW_LEN) screws from above. The raised crown surrounds the motor ends with open terminal wells. Derek confirms firm retention and no vertical play in his accepted assembled pair; the local comparison and current cap checks are linked from the [physical-fit record](/hardware/reference/kamoer-kphm400/physical-fit.json). The cartridge comes out first, the clamp lifts, then each complete pump lifts out of the cradle ([`/hardware/service/pump-replacement.md`](/hardware/service/pump-replacement.md)). [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) owns the printed parts.
2. **The pack's two seam-crossing runs still need a motion gate.** V-A and V-B stand on the cold core's cap while Y-A and Y-B ride in the front-top manifold, so their two runs cross the Y seam. Their assembly moment is the open-cart stage before the back assembly rides over the core, with both mouths still reachable. [`_lines.py`](/hardware/manifold-layout/_lines.py) draws neither run, so the tree still lacks a geometry check that proves the available reach and the closing sweep.
3. ~~**Tap-water tap-point into the flavor manifold (V-A inlet).**~~ **CLOSED.** The flavor tap comes off the **water split** — the JG PP0208E 1/4" union tee one tube-length forward of the ASSE 1022's outlet (`reference/water-split/`): its forward run collet → `fluid-1` → neoFit flow regulator → `fluid-2` → V-A ([`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) tube segments 1 and 2). The ASSE leaves at 1/4", so the split and the tap run are both plain 1/4" PTC — no 3/8"-to-1/4" branch chain. See [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3.
4. **Purchased union elbow.** The funnel drain uses one PP0308E under its frame,
   billed in [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §8. The pump-side
   turns are part of the four printed TPU junctions and four printed TPU returns.
   Three other manifold joints use fully swallowed straight blanks.
5. **Pump elbow qualification and shipped clamp.** Four clamps per build, two on each [printed elbow](/hardware/printed-parts/diaphragm-pump-sleeve/README.md). The owned YDS butterfly clamps carry the fit and pressure trial; their plated carbon-steel screw and low-pressure listing do not suit the wet bay, so the shipped clamp follows the trial's pressure and retention result. Siraya fit on the G Ganen barbs, pressure holding, 24-hour relaxation and the filament's wetted-service suitability have no physical result yet; the elbow README states the acceptance screen. The ASSE sleeve uses two four-inch nylon ties, one per inserted part. [`/hardware/ledger/bom.md`](/hardware/ledger/bom.md) §3 lists the elbows and clamps; §11 lists the ties.
6. ~~**A cradle for the WR1110 body.**~~ **CLOSED.** The regulator lies in a bored rib off the top wall, closed on the scanned ⌀18.87 barrel between its two wrench hexes (`enclosure._tube_anchors` off [`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py)'s `BODY_ANCHOR_SITES`). It crosses the +Y wall one `PORT_PITCH` east of the carb union and on the panel deck's own storey, so the top wall reaches it the way it reaches the flow meter one column west. [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md) owns the part.
7. ~~**Cabinet-internal carbonated-water insulation segment count.**~~ **CLOSED — cut-to-length pieces, not 1-ft segments.** The cold-core-exit → blue-ringed-bulkhead run has a fixed length per build, is closed entirely in-shop and is never field-trimmed, so the 1-ft granularity that serves the above-counter umbilical buys nothing here and would leave up to 12" of bare tube on the coldest part of the line. The riser is authored in [`_lines.py`](/hardware/manifold-layout/_lines.py) as `carb-1` and `carb-2`, and the flow meter between them means **a piece per run, not one** — each cut to its own run's developed length, which the enclosure-assembly build prints per line, and slid on before the collets go down. `carb-1`'s is cut in two at its rib, whose bore and anchor cap close on the bare tube. [`bom.md`](/hardware/ledger/bom.md) §9 carries 84 in of CARGEN per build: the 24 in this riser takes, which covers all three pieces, plus the umbilical's five 1-ft segments.
8. **Stationary fore-link stock lengths.** Each junction-to-valve blank includes
   both fittings’ insertion depths as well as its [14.501 mm](DOCK_FORE_LINK)
   straight exposed path. Step 1 derives the valve engagement from the actual
   received valve rather than using its nominal CAD insertion depth.

9. **Downstream CO2 check fit.** The nominal CAD layout includes the four warm gas adapters and local check cradle. Confirm the received fitting envelopes, thread make-up and physical hose bends, then qualify the support and route clearances while retaining the regulator bracket and enclosure envelope.
10. **Owned GASHER construction and sealing.** The owned ASIN is B0FV2D2FFX. Repository descriptions conflict between stainless/PTFE and nickel-plated copper/unspecified soft seat; the dimensional drawing does not resolve the wetted construction. Record supplier evidence for body and seat material, pressure rating, CO2/carbonated-water compatibility and cracking pressure, and measure reverse leakage under the actual pressure cycle. Do not treat either unsupported material description as qualified.

## Sources
[value](NAME) texts are updated by:
- `/hardware/assembly/_internal_plumbing_sync.py`

[`_lines.py`](/hardware/manifold-layout/_lines.py) draws the runs between bodies placed by [`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py); `enclosure-assembly.scorecard.json` carries developed lengths and corner counts. The three warm CO2 runs require the placement and adapter-envelope qualification in §1 before those generated lengths can be used as gas-line cut lengths.
