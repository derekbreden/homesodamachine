This file describes the appliance. The [prototype](../README.md) on the counter has proven the dispense path: two flavors of real Pepsi-made concentrate injected into cold carbonated water from an external Lillium, press the lever and soda comes out. This integrated build packs everything into one enclosure under the kitchen sink — the carbonator, its refrigeration loop, both flavor reservoirs, the pumps and valves, and the electronics — behind a single 120 VAC cord with the tap-water inlet at the rear and the CO2 cylinder sitting beside the appliance in the cabinet on a short tether to a front-panel inlet. The Lillium goes away. The countertop reservoirs go away. What stays on the counter is a faucet, a flavor switch, and a small display.

The enclosure is built around a **cold core** at the back: a vertical 5" OD × ~6" tall 316L stainless carbonator vessel, a copper evaporator coil wrapped tight around it, and two flavor reservoirs nested between the inner and outer foam shells where they pre-chill passively to 8–15 °C. Forward of the core sits the compressor, with the diaphragm pump, valve manifold, and peristaltic pump cartridges stacked above it. The harvested ice-maker condenser + fan sit on one side wall of the enclosure, oriented so the fan's native airflow direction crosses the enclosure side-to-side: intake grille on one side face, exhaust grille on the opposite side face, straight-through with no redirection. The electronics shelf rides at the top-back behind the rear-panel C14 inlet. The carbonator outlet runs a short insulated path straight up through the countertop to the faucet at the back of the sink. Sections below describe each subsystem in turn, with the cold core read **inside out** and the enclosure read **back to front**.

Companion docs: [`bom.md`](bom.md) (per-unit bill of materials), [`purchases.md`](purchases.md) (every line item with ACQUIRED / ON-ORDER / LIKELY-TO-BUY status), [`handwork.md`](handwork.md) (dev-phase skilled-hand task summary), [`assembly/`](assembly/) (production-procedure docs per subsystem).

**Carbonation subsystem**

Production procedure: [`assembly/pressure-vessel.md`](assembly/pressure-vessel.md).

The carbonator vessel is custom-fabricated from 316L stainless steel and oriented vertically.

The body is a commodity 5" OD × 0.065" wall 316 welded SS round tube (OnlineMetals part #12498, MTRs required), capped at top and bottom with 1/4"-thick laser-cut 316 SS circular plates from SendCutSend (`endcap-circular-2hole.dxf`). Plates are joined to the tube ends with the XLaserlab X1 Pro handheld laser welder. The 1/4" plate is thick enough to direct-tap 1/4" NPT (4.5 turns of engagement).

Working pressure target is **90 PSI**. The vessel is hydro-tested to 180 PSI (~2× working pressure) for 30 minutes before service — procedure in [`assembly/pressure-vessel.md`](assembly/pressure-vessel.md) step 6.

The vessel has exactly four ports, all 1/4" NPT, hand-tapped directly into the 1/4" end plates. Tap Magic cutting fluid is used on the SS-into-SS tap.

Port 1 — CO2 inlet to internal sparge stone: A 1/4" hose-barb × 1/4" MNPT 316 SS adapter (LTWFITTING B017N4TTMA) threads into the bottom plate. On the inside face, a short length of food-grade silicone tube connects the barb to a 0.5 µm sintered 316 SS sparge stone (FERRODAY B091C5Y6L9, 1/4" barb input) that hangs in the water column. CO2 enters as fine bubbles that rise through the water, dissolving on the way up — high bubble surface area + short residence time = fast Henry's-law equilibration.

Port 2 — Water inlet (top plate): The SeaFlo diaphragm pump pushes filtered tap water against the CO2 back-pressure into the headspace, free-falling onto the water surface. No atomizer, no dip tube on the inlet side. Path: pump 3/8" hose barb → MAACFLOW 3/8" barb × 1/4" NPT SS adapter (B0DMP77B6S) → GASHER 1/4" NPT SS PTFE-soft-seat check valve → first JG PP010822E 1/4" PTC × 1/4" NPT M adapter (warm-side NPT→PTC transition) → 1/4" OD LLDPE through the foam shell's +Z slot → second JG PP010822E (cold-side PTC → NPT) → TAISHER 316L SS 90° NPT M×F street elbow (B0CZ38MYL1) → 1/4" NPT top plate port → vessel headspace. Upstream of the pump (suction side): Multiplex 19-0897 ASSE 1022 backflow preventer (3/8" MPT in × 3/8" MFL out) → brewhardware FFL38BARB38 3/8" FFL swivel × 3/8" SS hose barb (single-piece, 304 SS wetted barb + chrome-plated brass swivel nut never touches water) → 3/8" ID food-grade silicone hose (JoyTube B089YGDB55, ~12" per build off the in-hand 10 ft roll) → SeaFlo pump 3/8" hose barb inlet.

Port 3 — Carbonated water outlet (bottom plate): Water exits via a short 1/4" NPT stub on the bottom plate. Vertical orientation puts the densest, coldest, most carbonated water at the bottom by default, so the bottom port draws the right water. Outlet runs through 1/4" tubing up to the Westbrass Touch-Flo faucet under CO2 pressure.

Port 4 — Pressure relief valve (top plate, dedicated, **125 PSI set pressure, 49 SCFM relief capacity, Control Devices SV-125 B01G2F6EMY** — industrial pneumatic safety valve, brass body).

The tank interior is passivated with citric acid (one-time, 30–60 min soak of ~4% food-grade citric acid solution in a disposable plastic tub, then thorough water rinse) after welding and before first service. Passivation restores the chromium oxide layer at the weld zones, which is what makes 316L SS (and 304) resistant to pitting corrosion from carbonic acid (carbonated water, pH ~3.5–4). This is the same treatment commercial brewery bright tanks and commercial carbonators receive.

CO2 supply is two-stage: the customer's CGA-320 primary regulator feeds an in-appliance Interstate Pneumatics WR1110 fixed-90 PSI secondary regulator (B07J2L8LF3) between the front-panel CO2 inlet and the vessel CO2 port. Setpoint rationale and customer-setpoint guidance in [`assembly/pressure-vessel.md`](assembly/pressure-vessel.md) "CO2 supply". CO2 then enters the vessel CO2 port via the internal sparge architecture above.

Water is pushed into the tank against CO2 back-pressure by the SEAFLO 22-Series 100 PSI diaphragm pump (B0166UBJX4). Full water path: tap → ASSE 1022 carbonated-beverage backflow preventer (Multiplex 19-0897, lead-free brass body with SS internals, dual check with atmospheric vent, 10–200 PSI, 3/8" MPT × 3/8" MFL with 1/4" barb vent) → brewhardware FFL38BARB38 3/8" FFL swivel × 3/8" SS hose barb (single-piece, 304 SS wetted barb + chrome-plated brass swivel nut never touches water) → 3/8" ID food-grade silicone hose (JoyTube B089YGDB55, ~12" per build off the in-hand 10 ft roll) → SeaFlo pump 3/8" hose barb inlet → SeaFlo pump 3/8" hose barb outlet → MAACFLOW 3/8" barb × 1/4" NPT SS adapter → external PTFE-soft-seat check valve (GASHER B0FV2D2FFX, 1/4" NPT SS) → first JG PP010822E 1/4" PTC × 1/4" NPT M adapter (warm-side NPT→PTC transition, same fitting as the §4 CO2 and §8 flavor BiB paths) → 1/4" OD LLDPE through the foam shell's shared +Z slot → second JG PP010822E (cold-side PTC → NPT) → TAISHER 316L SS 90° NPT M×F street elbow → 1/4" NPT top-plate water-inlet port → vessel headspace. The CO2-side line carries an identical GASHER 1/4" NPT SS check valve installed inline on the dry side between the DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the first JG PP010822E 1/4" PTC × 1/4" NPT M adapter that takes the line into 1/4" OD LLDPE for its run through the cold-core stack (cap-top → in-cavity PP0308E 90° elbow in the foam-shell −Z support-arch doorway → second PP010822E adapter → TAISHER 1/4" NPT 90° vessel-port elbow → vessel Port 1 → LTWFITTING bottom-plate barb on the inside-vessel face) — same 2-pack as the water-side check, one valve per side per vessel. Check-valve material choice and the elastomer-vs-PTFE-on-metal argument live in [`assembly/cold-core.md`](assembly/cold-core.md) "Warm-side check valves".

ASSE 1022 (not 1024) is the correct standard for this application. 1022 is specifically "Backflow Preventer for Beverage Dispensing Equipment" — required because dissolved CO2 makes carbonic acid at pH ~3.5, which leaches lead from solder joints in household plumbing if it backfeeds. The Multiplex unit's atmospheric vent barb must be routed to an observable drip location (not plumbed into a drain), because the vent is the mechanical telltale: if check #1 leaks, the escaping water/CO2 becomes visible at the vent before anything backfeeds past check #2. The 3/8" MFL outlet connects to downstream 3/8" ID food-grade hose via a single-piece **brewhardware FFL38BARB38** 3/8" FFL swivel × 3/8" SS hose-barb adapter (304 SS wetted barb, chrome-plated brass swivel nut never touches water).

**Level sensing — external reed + internal magnetic float on welded SS rod.** A 1/8" 316L SS rod (Tandefio B0CY4DWJFQ, cut from 12" stock to ~6") is laser-welded vertically to the inside face of the bottom plate, with its top end captured by a small register on the inside face of the top plate. A magnetic donut float (harvested from a DEVMO MINI float switch B07T18PGJ4) slides freely along the rod with the water level. External reed switches (Gebildet B0CW9418F6) are mounted on the outside of the 0.065" 316L SS tube wall (316L is austenitic and non-magnetic — the magnetic field passes through the wall). Two reeds — one at the low-level refill threshold, one at the high-level full threshold. Zero electrical penetrations of the pressure vessel; nothing wetted is anything other than 316/316L SS or food-grade silicone.

Refill is triggered when the faucet is closed and the low-level reed reads empty — never during an active dispense. This is a hard firmware interlock, not a soft preference: introducing 18 °C tap water during a pour raises the dispensed water temperature rapidly (2 °C → ~6 °C after one 12 oz pour under perfect-mix). The tank functions as a thermal reservoir, not a real-time buffer: dispense until the low-level threshold, close the faucet, then the pump refills and the evaporator pulls the new water down to service temperature before the next pour is allowed.

Carbonated water at ~2 °C and pH ~3.5–4 naturally suppresses biofilm and scale formation in the vessel — no scheduled clean cycle is required for the carbonator (the clean cycle in `flavor-subsystem` is for the flavor lines, not the carbonator).

Dispensing is a faucet lever. The carbonated water is already cold, carbonated, and under CO2 pressure — opening the valve sends it directly to the nozzle.

**Refrigeration subsystem**

Production procedure: [`assembly/refrigerant-loop.md`](assembly/refrigerant-loop.md).

Compressor, condenser + fan, capillary tube, and filter drier are harvested from a countertop ice maker. The evaporator cold plate is discarded and replaced with a custom-wound copper coil around the carbonator tank. Two ice makers purchased for teardown:

- Frigidaire EFIC117-SS (26lb/day) — ASIN B07PCZKG94, $78.70
- Generic countertop (8 cubes/6min, 26lb/day) — ASIN B0F42MT8JX, $63.80

Evaporator coil: GOORY 1/4" OD x 0.187" ID, C12200 ACR (ASTM B280), thick-wall (0.031") — ASIN B0DKSW5VL9. The 0.031" wall resists thinning at bends around the carbonator tank.

Compressor cycling is controlled by firmware, not a mechanical thermostat. Two DS18B20 waterproof 1-wire temperature probes on a shared bus: one clamped to the carbonator tank wall reads water-side temperature for cycle control (target ~2 °C, hysteresis ~2 °C — compressor off at 2 °C, on at 4 °C); a second bonded to the evaporator suction line reads coil temperature for freeze protection (hard cutout at −8 °C to prevent the water in the tank from freezing against the coil). The ESP32 reads both probes and drives the Teyleten relay module on GPIO 14 to switch the compressor's AC hot leg. A minimum off-time enforced in firmware (~3 min) prevents short-cycling and protects the compressor's start capacitor.

Factory charge is R-600a (isobutane) — R-600a is carved out of the EPA Section 608 venting prohibition as a natural refrigerant, so the loop is vented to atmosphere through a piercing valve rather than recovered into a machine. No 608 certification is legally required. Teardown sequence: vent factory charge through a BPV31 piercing valve clamped on the compressor process tube, cut out only the factory finger-plate evaporator (the factory drier + capillary tube + suction-line heat-exchanger pair are preserved in service under continuous argon flow), pull vacuum and recharge through the same BPV31 flare port (which becomes the appliance's single permanent service-access point), recharge from a 6 oz Enviro-Safe pure R-600a can (target ~20-35 g per system depending on donor, metered by mass — factory is 15 g for Unit A's Antarctic Star HZB-12/Q and 23 g for Unit B's Frigidaire EFIC117-SS per their manuals; new larger evap coil pushes the target above factory; calibrated empirically per [`assembly/refrigerant-loop.md`](assembly/refrigerant-loop.md) step 7 + open items §1). Total component cost per unit: ~$100-110.


**Cold core assembly (inside out)**

Production procedure: [`assembly/cold-core.md`](assembly/cold-core.md).

Layer 1: Custom-fabricated 316L SS carbonator vessel, vertical orientation, 5" OD × ~6" tall round tube + 1/4" end plates.

Layer 2: Copper evaporator coil wrapped tight around the tank, bonded to the tank OD with 3M 425 aluminum foil tape (thermally conductive).

Layer 3: 3D-printed inner shell with ~1/4" gap, filled with two-part closed-cell pour-in-place polyurethane foam (2 lb density, ~R-6/in). Two components mix 1:1, poured through a fill port at the top of the shell, and rise to fill the cavity. Vent holes in the shell allow excess foam to escape during cure; trimmed flush after hardening.

Layer 4: Flavor reservoirs wrapped around the insulated core, serving as both syrup storage and thermal mass. A pair of custom printed hard reservoirs, one per flavor, conform directly to the cold-core envelope instead of forcing off-the-shelf bottle geometry into the under-sink package. The reservoirs are vented, not service-pressure vessels: ~0.88 L usable per refill cycle (sized for 2× SodaStream 0.44 L bottles of concentrate; ~1.18 L total geometric volume each), low outlet sump, high filtered vent, fill/dispense/clean paths through the same valve manifold. The reservoirs are separate printed parts that fit inside the foam shell. Filled from a user-accessible hopper via the pumps, cleaned in place by a software-controlled rinse cycle (water in, water out to nozzle, air in, air out to nozzle, repeat).

Layer 5: 3D-printed outer shell with ~1/2" to 3/4" gap, filled with the same pour-in-place foam, same process as inner layer.

Total cold core dimensions: TBD after spray foam and shell layers are added around the 5" OD × ~6" tall vessel core.

The flavor reservoirs passively pre-chill to roughly 8-15°C by sitting in the thermal gradient between the near-freezing inner core and ambient air. The inner foam layer prevents the reservoirs from freezing against the evaporator.

**Flavor subsystem**

Two peristaltic pumps (food-grade silicone tube inside the pump head; 1/4" LLDPE hard tubing for the line runs in and out), mounted in the replaceable pump cartridge assembly. The cartridge uses John Guest quick-connects and a palm-squeeze release plate for tool-free swap. The pumps pull flavor from the internal printed hard reservoirs around the cold core and inject it at the dispense nozzle alongside the carbonated water.

Pump direction is forward-only. Filling, dispensing, and clean-cycle operations are selected by the valve manifold. The canonical valve-state truth table is `topology/fluid-topology.md`: hopper/BiB/tap-water inputs are routed to the pump inlet through source-selection valves, and the pump outlet is routed either back to the selected bag or out to the nozzle.

Each flavor has two input paths to the reservoir. The primary path is the shared hopper funnel on the user-facing side for pouring from SodaStream concentrate bottles, with a solenoid-selected route to the appropriate internal flavor reservoir. The funnel has a removable dishwasher-safe silicone cover. The secondary path is a bag-in-box adapter on the rear of the enclosure — a barb or quick-connect fitting that connects to a standard BiB line. Both paths feed through the pump into the same internal refrigerated reservoir. The BiB adapter is present but not prominently marketed; it serves customers who source their own commercial syrup.

Level sensing in each flavor reservoir uses the same external-reed + internal-magnetic-float pattern as the carbonator vessel, scaled up to 4 reeds per reservoir (8 reeds total across both) for ~13-serving-step granularity. Architecture, magnet-strength signal-path math, GPIO budget, rod material choice, and open items in [`printed-parts/cold-core/reservoir/level-sensing.md`](printed-parts/cold-core/reservoir/level-sensing.md); per-build parts in `bom.md` §12.

**Enclosure layout**

The enclosure is an under-counter appliance, installed inside the kitchen cabinet beneath the sink. Its front face points toward the kitchen cabinet door; its back sits near the kitchen cabinet's rear wall. All rear-face connections (water inlet, AC inlet, BiB adapter, and the 3-tube umbilical port that lands the carbonated-water + 2 flavor lines coming down from the under-cabinet faucet) assume the typical 2–4" working gap between the appliance back and the cabinet rear wall, consistent with under-sink plumbing convention. Full connection inventory + umbilical-port architecture (3× JG PP1208E PTC bulkheads, blue accent ring on the carbonated-water bulkhead for tube-matching) in [`printed-parts/enclosure/back-panel/README.md`](printed-parts/enclosure/back-panel/README.md). The side faces sit alongside the cabinet's left/right walls with a similar working gap on each side, which is the airflow plenum for the side-to-side condenser path described below. The CO2 cylinder sits **beside** the appliance in the cabinet on the cabinet floor — in the side air-gap between the appliance and one cabinet sidewall, not in front of the appliance where it would block the cabinet door — on a short tether to a front-panel CO2 inlet. The labeled inlet on the front-panel face is direction of travel for "hose connects here."

Front-to-back the internal layout runs: compressor at the middle-bottom, valve manifold + 100 PSI diaphragm pump + Kamoer peristaltic pump cartridges stacked above the compressor in the middle, and the cold core occupying the full rear of the enclosure against the back wall. The condenser + fan, harvested from the donor ice maker together with its own fan shroud, mount against one side wall of the enclosure with the fan's native flow axis crossing the enclosure side-to-side. The front face carries no thermal duty — it is reserved for user-facing surfaces (pump cartridge access, hopper above).

The **electronics shelf** sits at the top-back of the enclosure, immediately behind the rear-panel C14 inlet. It carries the C14 inlet, AC distribution block, Mean Well IRM-90-12ST PSU, both Teyleten relays, ESP32-DevKitC-32E, MCP23017 GPIO expander, two ULN2803A driver modules, the L298N peristaltic-pump driver, and the 5 V + 3.3 V regulators — all on one assembly. The C14 → AC distribution → relay → PSU → 12 V bus path all happens in a short, clean wiring run with one common chassis bond. Heat from the PSU (~5–10 W) sheds via natural convection in the kitchen-ambient air around the shelf; the appliance is not sealed and the condenser fan creates negative pressure that pulls makeup air through every gap, giving slow circulation throughout. See [`wiring/ac-wiring-schedule.md`](wiring/ac-wiring-schedule.md) for run-by-run gauges + lengths.

Thermal zones separate cleanly. Hot side runs side-to-side across the middle of the enclosure: the condenser's harvested fan pulls cabinet air in through the intake-side grille, across the finned condenser, and out through the exhaust-side grille — a straight pass-through with no redirection. Cold side at the back: the carbonator, flavor reservoirs, and chilled dispense line, insulated by the cold core's inner and outer foam shells. The compressor sits at the middle-bottom and bridges the two zones, with short refrigerant lines to the side-mounted condenser; the longer suction run back to the evaporator coil around the carbonator is not efficiency-critical.

Placing the cold core at the back keeps the chilled dispense run to a minimum. The faucet penetration in the countertop is typically at the back edge (where the sink meets the backsplash), so the carbonated water line runs straight up from the cold core through a short insulated tube — the most temperature-critical path in the system.

**Compressor compartment shroud**

A non-combustible sheet-metal shroud encloses the compressor's terminal block + clip-on PTC relay/overload module — the only ignition-risk parts of the AC system in the R-600a refrigerant compartment. Hardware backstops to the firmware cutoff: the SF76E thermal fuse lives inside the shroud (in series with the AC primary feeding the compressor); the MQ-6 hydrocarbon sensor is mounted low on the rear interior enclosure wall, where dense R-600a pools at the cabinet floor from any of the dominant brazed-joint leak sites. Full spec, what's inside vs outside, material rationale, and dimensions at [`cut-parts/compressor-shroud/README.md`](cut-parts/compressor-shroud/README.md); safety procedure at [`assembly/refrigerant-loop.md`](assembly/refrigerant-loop.md) "Safety".

**Backflow vent monitoring**

The Multiplex 19-0897's atmospheric vent terminates inside the kitchen cabinet over a small internal drip pan, not routed up through the counter. A moisture sensor in the pan ties to an ESP32 input — when the vent weeps (the mechanical telltale that check #1 has begun to leak), firmware fires an audible alarm at the device and an iOS app notification.

**User-facing elements, by location**

*Above counter, through-counter fixtures over the sink:* faucet lever, KRAUS air switch for flavor select, RP2040 round display showing the active flavor's logo.

*Enclosure top, front half* (reached by the user opening their kitchen cabinet door — the enclosure itself has no hinged doors, its top is an integral funnel): flavor hopper, a large funnel covering most of the front half of the top face, sized to accept a pour from a SodaStream concentrate bottle without splash, feeding through solenoid-selected valves down to the appropriate internal flavor reservoir.

*Enclosure front face, middle:* pump cartridge access door (this one is on the enclosure itself) for swapping the Kamoer peristaltic pump when its silicone tubing wears out.

*Enclosure front face:* CO2 inlet stub for the short tether from the customer's CO2 cylinder.

*Enclosure front face:* TEST and RESET pushbuttons plus a status LED for the Legrand Radiant 1597BKCCD12 GFCI mounted face-flush behind the printed front panel. The printed face has a small cutout exposing only the device's central button band — the device's two 5-15R receptacle outlets sit behind the printed material and are not customer-accessible. The device self-tests every 3 seconds. Protection architecture in [`../business/regulatory.md`](../business/regulatory.md) "UL 943 — ground-fault protection".

*Enclosure side faces:* condenser intake grille on one side, condenser exhaust grille on the opposite side — straight-through airflow path with the harvested ice-maker fan inline between them.

**Power**

The appliance is cord-and-plug 120 VAC through the rear C14 inlet. The harvested ice-maker compressor remains a 120 VAC load, switched on the AC hot leg by firmware-controlled Teyleten relay #1. The condenser fan is **factory-DC**: the donor ice maker's own PCB regulated mains to 12 V to drive it, so the fan itself was never on AC. We discard the donor PCB on harvest and run the fan from our own Mean Well 12 V bus, low-side-switched by a ULN2803A channel driven from MCP23017 0x21 (same pattern as the solenoid valves), firmware-gated alongside the compressor so the two cycle together. The Mean Well 12 V supply creates the low-voltage bus for the diaphragm pump, peristaltic pumps, solenoid valves, condenser fan, motor driver, valve drivers, controllers, displays, and sensors. Current power topology lives in `wiring/power.mmd`.

**Rear-panel AC inlet**

The AC inlet is an IEC 60320 C14 panel-mount receptacle (MXR B07DCXKNXQ) accepting a standard NEMA 5-15P → C13 line cord, recessed 3–5 mm into the rear panel with a printed shroud so the cord housing nests flush. Inlet placement on the panel and the recess geometry are captured alongside the rest of the panel-mount inventory in [`printed-parts/enclosure/back-panel/README.md`](printed-parts/enclosure/back-panel/README.md).

**Rear-panel nameplate**

A separately-printed serialized plaque mounted on the rear face of the enclosure. Carries regulatory markings (model, serial, 120V 60Hz input rating), the Founder Edition number and signature, and a per-unit QR code linking to `homesodamachine.com/u/NNN`. Printed separately from the enclosure so its fine text and QR can use nameplate-grade print settings without forcing them onto the bulk of the cabinet. Full spec in [`printed-parts/enclosure/nameplate/README.md`](printed-parts/enclosure/nameplate/README.md).
