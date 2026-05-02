**Carbonation subsystem**

The carbonator vessel is custom-fabricated from 316L stainless steel and oriented vertically (always vertical, regardless of cross-section choice). 316L was chosen over 304 for the wetted pressure boundary because the molybdenum addition gives meaningfully better pitting and crevice-corrosion resistance in the chloride + carbonic-acid environment of long-life carbonated water service; the cost delta on the small per-vessel quantity was acceptable. Two body geometries are in play:

- **Plan A (current plan):** commodity 5" OD × 0.065" wall 316 welded SS round tube (OnlineMetals part #12498, MTRs required), capped at top and bottom with 1/4"-thick laser-cut 316 SS circular plates from SendCutSend (`endcap-circular-2hole.dxf`). Plates are joined to the tube ends with the XLaserlab X1 Pro handheld laser welder. The 1/4" plate is thick enough to direct-tap 1/4" NPT (4.5 turns of engagement) without weld-in bungs. This is the path being pursued.
- **Plan B (still under exploration):** racetrack body formed from two 7.754" × 6.000" half-blanks in 0.048" 304 SS, press-formed into D-halves and butt-welded along both flat sides; press-domed 0.060" 304 SS racetrack end caps. Retained as fallback if the 1/4"-plate-to-0.065"-tube weld can't be made reliably. Plan B inventory remains 304 SS (existing SendCutSend stock) — accepted inconsistency for a fallback that may never be invoked. Blank DXF in `cut-parts/carbonator-body-sheet/generate_dxf.py`; press die specs and CadQuery script in `printed-parts/carbonator-body-press-dies/`. Racetrack end-cap DXF in `cut-parts/carbonator-endcaps-racetrack/generate_dxf.py`; dishing dies in `printed-parts/carbonator-dishing-dies/`.

Both plans target a working pressure of 70 PSI minimum with adequate margin (plan A: 5" OD × 0.065" wall 316L SS gives hoop stress of ~2,690 PSI at 70 PSI, ~7.4× safety factor vs 20,000 PSI allowable; plan B: 4,058 PSI hoop stress, 4.9× safety factor — same allowable for 304/316L for vessel-grade service). Both are hydro-tested to 150 PSI (~2× working pressure) for 30 minutes before service.

The vessel has exactly four ports, all 1/4" NPT, hand-tapped directly into the 1/4" end plates (plan A) or into welded bungs (plan B fallback only). Tap Magic cutting fluid is used on the SS-into-SS tap.

Port 1 — CO2 inlet to internal sparge stone: A 1/4" hose-barb × 1/4" MNPT 316 SS adapter (LTWFITTING B017N4TTMA) threads into the bottom plate. On the inside face, a short length of food-grade silicone tube connects the barb to a 0.5 µm sintered 316 SS sparge stone (FERRODAY B091C5Y6L9, 1/4" barb input) that hangs in the water column. CO2 enters as fine bubbles that rise through the water, dissolving on the way up — high bubble surface area + short residence time = fast Henry's-law equilibration. Sparge replaces the earlier atomizer plan: the Beduan spiral-cone nozzle requires a high pressure differential across the nozzle to atomize, and at our working ΔP (15–25 PSI between pump output and 70 PSI headspace) it produces a stream, not a spray. Sparging is also mechanically simpler — no precision orifice, no custom-machined parts.

Port 2 — Water inlet (top plate): The SeaFlo diaphragm pump pushes filtered tap water against the CO2 back-pressure into the headspace, free-falling onto the water surface. No atomizer, no dip tube on the inlet side. Path: pump 3/8" hose barb → MAACFLOW 3/8" barb × 1/4" NPT SS adapter (B0DMP77B6S) → GASHER 1/4" NPT SS PTFE-soft-seat check valve → 1/4" NPT top plate port.

Port 3 — Carbonated water outlet (bottom plate): Water exits via a short 1/4" NPT stub on the bottom plate — no internal dip tube. Vertical orientation puts the densest, coldest, most carbonated water at the bottom by default, so the bottom port draws the right water without an internal feature. Outlet runs through 1/4" tubing up to the Westbrass Touch-Flo faucet under CO2 pressure.

Port 4 — Pressure relief valve (top plate, dedicated, 100 PSI set pressure, 40 SCFM relief capacity, Control Devices SV-100 B0D361X97X — industrial pneumatic safety valve, brass body, fit-for-purpose for D2C Founder Edition). Not ASME UV-stamped; not required because this project is not pursuing UL/ETL listing (see `regulatory.md`). The PRV must have its own dedicated port with an unobstructed path to the vessel interior at all times. It cannot share a port via a tee — a blockage, fitting failure, or maintenance disconnect on a shared line could compromise the safety relief path.

The tank interior is passivated with citric acid (one-time, 30–60 min soak of ~4% food-grade citric acid solution in a disposable plastic tub, then thorough water rinse) after welding and before first service. Passivation restores the chromium oxide layer at the weld zones, which is what makes 316L SS (and 304) resistant to pitting corrosion from carbonic acid (carbonated water, pH ~3.5–4). This is the same treatment commercial brewery bright tanks and commercial carbonators receive. A food-safe epoxy coating was considered but rejected: commercial carbonators (Lillium, Brio, SodaStream commercial) all run bare passivated 304/316 SS for decades, and epoxy coatings can fail at pinholes and concentrate corrosion where a uniform oxide layer would spread it harmlessly.

CO2 supply is a standard regulated bottle, set to 70 PSI minimum (typically 70–80 PSI), feeding through the CO2 port via the internal sparge architecture above.

Water is pushed into the tank against CO2 back-pressure by the SEAFLO 22-Series 100 PSI diaphragm pump (B0166UBJX4). Full water path: tap → ASSE 1022 carbonated-beverage backflow preventer (Multiplex 19-0897, lead-free brass body with SS internals, dual check with atmospheric vent, 10–200 PSI, 3/8" MPT × 3/8" MFL with 1/4" barb vent) → 3/8" flare × 1/4" FNPT adapter → SeaFlo pump (3/8" hose barbs) → MAACFLOW 3/8" barb × 1/4" NPT SS adapter → external PTFE-soft-seat check valve (GASHER B0FV2D2FFX, 1/4" NPT SS, PTFE disc on metal poppet confirmed by inspection 2026-04-25; not the pump's internal elastomer check) → 1/4" NPT top-plate water-inlet port. The pump's own integrated checks are a redundant layer #3, not the primary seal, because elastomer checks creep under sustained CO2 back-pressure and gas molecules migrate through elastomer seals that would hold liquid indefinitely. PTFE-on-metal is the standard soft-seat construction in commercial beverage/brewery/food-process check valves at this pressure class — chemically inert to carbonic acid and CO2, no gas-permeation problem, suitable for long-term field service. The CO2-side line carries an identical GASHER 1/4" NPT SS check valve installed inline between the DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the LTWFITTING bottom-plate barb adapter — same 2-pack as the water-side check, one valve per side per vessel. This prevents water from back-flowing through the sparge stone, up the silicone tube, and into the CO2 regulator if pressures invert under fault.

ASSE 1022 (not 1024) is the correct standard for this application. 1022 is specifically "Backflow Preventer for Beverage Dispensing Equipment" — required because dissolved CO2 makes carbonic acid at pH ~3.5, which leaches lead from solder joints in household plumbing if it backfeeds. The Multiplex unit's atmospheric vent barb must be routed to an observable drip location (not plumbed into a drain), because the vent is the mechanical telltale: if check #1 leaks, the escaping water/CO2 becomes visible at the vent before anything backfeeds past check #2. The 3/8" MFL outlet connects to downstream 1/4" NPT plumbing via a 3/8" flare × 1/4" FNPT adapter (Hooshing B0BNHVV6HT).

**Level sensing — external reed + internal magnetic float on welded SS rod.** A 1/8" 316L SS rod (Tandefio B0CY4DWJFQ, cut from 12" stock to ~6") is laser-welded vertically to the inside face of the bottom plate, with its top end captured by a small register on the inside face of the top plate. A magnetic donut float (harvested from a DEVMO MINI float switch B07T18PGJ4) slides freely along the rod with the water level. External reed switches (Gebildet B0CW9418F6) are mounted on the outside of the 0.065" 316L SS tube wall (316L is austenitic and non-magnetic — the magnetic field passes through the wall). Two reeds — one at the low-level refill threshold, one at the high-level full threshold. Zero electrical penetrations of the pressure vessel; nothing wetted is anything other than 316/316L SS or food-grade silicone.

Refill is triggered when the faucet is closed and the low-level reed reads empty — never during an active dispense. This is a hard firmware interlock, not a soft preference: introducing 18 °C tap water during a pour raises the dispensed water temperature rapidly (2 °C → ~6 °C after one 12 oz pour under perfect-mix). The tank functions as a thermal reservoir, not a real-time buffer: dispense until the low-level threshold, close the faucet, then the pump refills and the evaporator pulls the new water down to service temperature before the next pour is allowed.

Carbonated water at ~2 °C and pH ~3.5–4 naturally suppresses biofilm and scale formation in the vessel — no scheduled clean cycle is required for the carbonator (the clean cycle in `flavor-subsystem` is for the flavor lines, not the carbonator).

Dispensing is a faucet lever. The carbonated water is already cold, carbonated, and under CO2 pressure — opening the valve sends it directly to the nozzle.

**Refrigeration subsystem**

Compressor, condenser + fan, capillary tube, and filter drier are harvested from a countertop ice maker. The evaporator cold plate is discarded and replaced with a custom-wound copper coil around the carbonator tank. Two ice makers purchased for teardown:

- Frigidaire EFIC117-SS (26lb/day) — ASIN B07PCZKG94, $78.70
- Generic countertop (8 cubes/6min, 26lb/day) — ASIN B0F42MT8JX, $63.80

Evaporator coil: GOORY 1/4" OD x 0.187" ID, C12200 ACR (ASTM B280), thick-wall (0.031") — ASIN B0DKSW5VL9. The 0.031" wall resists thinning at bends around the carbonator tank. For production runs, the same product ships in 50 ft rolls (largest thick-wall size on Prime). BELLA BAYS (ASIN B0BXKK62XL) is an equivalent alternative at the same spec.

Compressor cycling is controlled by firmware, not a mechanical thermostat. Two DS18B20 waterproof 1-wire temperature probes on a shared bus: one clamped to the carbonator tank wall reads water-side temperature for cycle control (target ~2 °C, hysteresis ~2 °C — compressor off at 2 °C, on at 4 °C); a second bonded to the evaporator suction line reads coil temperature for freeze protection (hard cutout at −8 °C to prevent the water in the tank from freezing against the coil). The ESP32 reads both probes and drives the Teyleten relay module on GPIO 14 to switch the compressor's AC hot leg. A minimum off-time enforced in firmware (~3 min) prevents short-cycling and protects the compressor's start capacitor.

Factory charge is R-600a (isobutane) — R-600a is carved out of the EPA Section 608 venting prohibition as a natural refrigerant, so the loop is vented to atmosphere through a piercing valve rather than recovered into a machine. No 608 certification is legally required. Teardown sequence: vent factory charge, cut out old drier and braze in a replacement (Supco D111, integrated Schrader), pull vacuum, recharge from a 6 oz Enviro-Safe pure R-600a can (~40 g per system, metered by mass). Total component cost per unit: ~$100-110.

Fallback: the RIGID DV1910E (~$600 + 20-30% import tax) is a factory-sealed, pre-charged OEM module with a flexible copper coil evaporator that can be reshaped without breaking the refrigerant loop. The cost premium buys a UL/ETL listing for retail channels (Amazon, big-box) that require one.


**Cold core assembly (inside out)**

Layer 1: Custom-fabricated 316L SS carbonator vessel, vertical orientation. Plan A: 5" OD × ~6" tall round tube + 1/4" plates. Plan B: racetrack 5.566" × 3.966" × 6.000" (304 SS, fallback inventory). The vessel is always vertical regardless of cross-section.

Layer 2: Copper evaporator coil wrapped tight around the tank, bonded to the tank OD with 3M 425 aluminum foil tape (thermally conductive, replaces the earlier "thermal compound" plan which didn't suit the macro-scale gap geometry without clamping pressure).

Layer 3: 3D-printed inner shell with ~1/4" gap, filled with two-part closed-cell pour-in-place polyurethane foam (2 lb density, ~R-6/in). Pour-in-place is preferred over spray for this closed annular geometry — two components mix 1:1, get poured through a fill port at the top of the shell, and rise to fill the cavity without overspray. Vent holes in the shell allow excess foam to escape during cure; trimmed flush after hardening.

Layer 4: Flavor reservoirs wrapped around the insulated core, serving as both syrup storage and thermal mass. Flavor-reservoir Plan A is the known-good prototype path: two 3D-printed arch-shaped cradles, each holding a 1L Platypus bladder. Each bladder cap is drilled and fitted with a John Guest bulkhead fitting connecting to 1/4" hard RO tubing that runs to the peristaltic pumps. The bladders are permanent internal plumbing — filled from a user-accessible hopper via the pumps, cleaned in place by a software-controlled rinse cycle (water in, water out to nozzle, air in, air out to nozzle, repeat).

Flavor-reservoir Plan B is a pair of custom printed hard reservoirs, one per flavor, conforming directly to the cold-core envelope instead of forcing off-the-shelf bottle geometry into the under-sink package. The reservoirs are vented, not service-pressure vessels: roughly 1L usable volume, low outlet sump, high filtered vent, fill/dispense/clean paths through the same valve manifold. The test plan and candidate food-contact PET-family filaments live in `printed-parts/plan-b/reservoir/README.md`. Plan B only replaces the bladder/cradle physical package; the user experience and manifold behavior stay the same.

Layer 5: 3D-printed outer shell with ~1/2" to 3/4" gap, filled with the same pour-in-place foam, same process as inner layer.

Total cold core dimensions: TBD after spray foam and shell layers are added around the 5" OD × ~6" tall vessel core.

The flavor reservoirs passively pre-chill to roughly 8-15°C by sitting in the thermal gradient between the near-freezing inner core and ambient air. The inner foam layer prevents either reservoir architecture from freezing against the evaporator.

**Flavor subsystem**

Two peristaltic pumps (food-grade silicone tube inside the pump head; 1/4" LLDPE hard tubing for the line runs in and out), mounted in the replaceable pump cartridge assembly. The cartridge uses John Guest quick-connects and a palm-squeeze release plate for tool-free swap. The pumps pull flavor from the internal flavor reservoirs (Platypus bladders in Plan A, printed hard reservoirs in Plan B) and inject it at the dispense nozzle alongside the carbonated water.

Pump direction is forward-only. Filling, dispensing, and clean-cycle operations are selected by the valve manifold, not by reversing the pump. The canonical valve-state truth table is `topology/fluid-topology.md`: hopper/BiB/tap-water inputs are routed to the pump inlet through source-selection valves, and the pump outlet is routed either back to the selected bag or out to the nozzle.

Each flavor has two input paths to the reservoir. The primary path is the shared hopper funnel on the user-facing side for pouring from SodaStream concentrate bottles, with a solenoid-selected route to the appropriate internal flavor reservoir. The funnel has a removable dishwasher-safe silicone cover. The secondary path is a bag-in-box adapter on the rear of the enclosure — a barb or quick-connect fitting that connects to a standard BiB line. Both paths feed through the pump into the same internal refrigerated reservoir. The BiB adapter is present but not prominently marketed; it serves customers who source their own commercial syrup.

**Enclosure layout**

The enclosure is an under-counter appliance, installed inside the kitchen cabinet beneath the sink. Its front face points toward the kitchen cabinet door; its back sits near the kitchen cabinet's rear wall. All rear-face connections (water inlet, CO2 line, AC inlet, BiB adapter) assume the typical 2–4" working gap between the appliance back and the cabinet rear wall, consistent with under-sink plumbing convention. Front-to-back the internal layout runs: condenser + fan at the front, compressor in the middle-bottom just behind the condenser, valve manifold + 100 PSI diaphragm pump + Kamoer peristaltic pump cartridges stacked above the compressor in the middle, and the cold core occupying the full rear of the enclosure against the back wall.

Thermal zones separate cleanly. Hot side at the front: the condenser vents forward through a grille on the lower front face of the enclosure, drawing cool intake from the kitchen cabinet's toe-kick gap. Cold side at the back: the carbonator, flavor reservoirs, and chilled dispense line, insulated by the cold core's inner and outer foam shells. The compressor bridges the two, positioned for short refrigerant lines to the front-mounted condenser; the longer suction run back to the evaporator coil around the carbonator is not efficiency-critical.

Placing the cold core at the back shortens the chilled dispense run to a minimum. The faucet penetration in the countertop is typically at the back edge (where the sink meets the backsplash), so the carbonated water line runs straight up from the cold core through a short insulated tube — minimizing heat pickup on the most temperature-critical path in the system.

**Backflow vent monitoring**

The Multiplex 19-0897's atmospheric vent terminates inside the kitchen cabinet over a small internal drip pan, not routed up through the counter. A moisture sensor in the pan ties to an ESP32 input — when the vent weeps (the mechanical telltale that check #1 has begun to leak), firmware fires an audible alarm at the device and an iOS app notification. This trades the always-visible drip of a countertop tray for a one-time-loud, persistent-software-flagged alert; in exchange the customer keeps a clean countertop with no extra penetrations.

**User-facing elements, by location**

*Above counter, through-counter fixtures over the sink:* faucet lever, KRAUS air switch for flavor select, RP2040 round display showing the active flavor's logo.

*Enclosure top, front half* (reached by the user opening their kitchen cabinet door — the enclosure itself has no hinged doors, its top is an integral funnel): flavor hopper, a large funnel covering most of the front half of the top face, sized to accept a pour from a SodaStream concentrate bottle without splash, feeding through solenoid-selected valves down to the appropriate internal flavor reservoir.

*Enclosure front face, middle:* pump cartridge access door (this one is on the enclosure itself) for swapping the Kamoer peristaltic pump when its silicone tubing wears out.

*Enclosure front face, lower:* condenser exhaust grille.

**Power**

The appliance is cord-and-plug 120 VAC through the rear C14 inlet. The harvested ice-maker compressor and condenser fan remain 120 VAC loads, switched on the AC hot leg by a firmware-controlled relay. The Mean Well 12 V supply creates the low-voltage bus for the diaphragm pump, peristaltic pumps, solenoid valves, motor driver, valve drivers, controllers, displays, and sensors. Current power topology lives in `wiring/power.mmd`.

**Rear-panel AC inlet**

The AC inlet is an IEC 60320 C14 panel-mount receptacle (MXR B07DCXKNXQ) accepting a standard NEMA 5-15P → C13 line cord. When the outer enclosure rear panel is printed, the C14 inlet is **recessed 3–5 mm into the panel face** with a printed shroud around the inlet perimeter. On insertion, the cord housing nests into the recess and ends flush with the rear panel surface, visually masking the IEC-mandated gap between cord and inlet bezel.

This is purely a fit-and-feel improvement; no electrical or mechanical change to the connector itself. The visible gap between cord housing and inlet face is by design under IEC 60320, which specifies only the male-blade insertion region — not face-to-face mating distance. The C13/C14 cross-test pair (uxcell inlet B07PXSLBF4 + Tripp Lite cord B0000511C0, ordered Apr 24, 2026) confirmed all four parts in the MXR × Monoprice / MXR × TrippLite / uxcell × Monoprice / uxcell × TrippLite matrix mate to spec — the gap is the standard, not the parts. For a hand-built Founder Edition appliance the printed shroud is the cheapest path to a "fully seated" user-facing appearance.

Locking C13 cords (Tripp Lite P-Lock series and similar) were considered and rejected: the design concern is fit/feel feedback at insertion, not mechanical retention, and friction-only retention is sufficient for an under-counter install. A hardwired-cord alternative (KitchenAid / Vitamix pattern, no detachable connector at all) is held under separate consideration and would obviate the bezel-recess solution if pursued.

**Rear-panel nameplate**

A separately-printed serialized plaque mounted on the rear face of the enclosure. Carries regulatory markings (model, serial, 120V 60Hz input rating), the Founder Edition number and signature, and a per-unit QR code linking to `homesodamachine.com/u/NNN`. Printed separately from the enclosure so its fine text and QR can use nameplate-grade print settings without forcing them onto the bulk of the cabinet. Full spec in [`printed-parts/nameplate/README.md`](printed-parts/nameplate/README.md).
