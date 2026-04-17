**Carbonation subsystem**

The carbonator vessel is custom-fabricated from 304 stainless steel. Tube stock was ruled out at ~$80/ft; the vessel is built instead from flat sheet stock cut by SendCutSend and formed in-house.

Body: a 15.509" × 6.000" blank in 0.048" 304 SS, rolled on a slip roll into a racetrack (stadium) cross-section and closed with one longitudinal butt weld on a flat side. Rolled ID: R=1.935", flat=1.600" (5.470" × 3.870"). OD: R=1.983", flat=1.600" (5.566" × 3.966"). Hoop stress at 70 PSI: 4,058 PSI — 4.9× safety factor vs 20,000 PSI allowable for 304 SS. Blank and rolling zone dimensions are in `cut-parts/carbonator-body-sheet/generate_dxf.py`.

End caps: 0.060" 304 SS blanks laser-cut by SendCutSend (racetrack outline R=1.946", flat=1.600"; four 0.710" weld bung holes on top cap), then press-domed to a 0.250" crown using PA6-CF dishing dies. After doming, the rim shrinks to the slip-fit dimension (R=1.930") and drops into the rolled body with 0.005" clearance/side. The dome converts the stress mode from plate bending to membrane — 0.060" sheet passes ASME UG-32 with a 12× margin where a flat 0.060" cap would fail UG-34 by 3×. DXF geometry in `cut-parts/carbonator-endcaps-racetrack/generate_dxf.py`; dishing die specs and CadQuery script in `printed-parts/carbonator-dishing-dies/`.

The vessel requires exactly four independent ports (all 1/4" NPT). These serve distinct functions at distinct locations and cannot be combined onto shared fittings without compromising performance or safety.

Port 1 — CO2 inlet (headspace): CO2 enters the gas space above the water line from a regulated bottle at 60–70 PSI. The pressurized CO2 atmosphere drives dissolution into the water surface and into atomized droplets. CO2 must not enter below the water line — submerged injection would bubble through noisily, agitate sediment, and provide less controlled carbonation than headspace pressurization.

Port 2 — Water inlet (atomized, headspace): A spiral cone nozzle atomizes incoming water into fine droplets within the CO2 headspace. The atomization massively increases the surface area of water exposed to CO2, which is what makes carbonation fast. Without atomization, the carbonator would require mechanical agitation or long soak times to reach equivalent carbonation levels. Water is pushed against CO2 back-pressure by a 100 PSI diaphragm pump.

Port 3 — Carbonated water outlet (dip tube to near-bottom): A dip tube extends from this port to near the bottom of the tank. CO2-saturated water is denser than unsaturated water and sinks, so drawing from the bottom dispenses the coldest and most carbonated water first. The dip tube also ensures nearly the full tank volume can be dispensed without pulling CO2 gas into the outlet line. The carbonated water is already under CO2 pressure — opening the faucet valve sends it directly to the nozzle with no pump needed.

Port 4 — Pressure relief valve (dedicated, 100 PSI ASME rated): The PRV must have its own dedicated port with an unobstructed path to the vessel interior at all times. It cannot share a port with CO2 or any other line via a tee — a blockage, fitting failure, or maintenance disconnect on the shared line could compromise the safety relief path. A dedicated port is also a certification consideration for UL/ETL listing.

The tank interior is coated with food-safe epoxy (e.g. MaxCLR A/B, FDA compliant when cured) to protect against long-term corrosion from carbonic acid (carbonated water, pH ~3.5-4). The vessel is hydro-tested to 150 PSI (1.5x working pressure) for 30 minutes before service as a verification step.

CO2 supply is a standard regulated bottle, set to approximately 60-70 PSI, feeding directly into the tank headspace through the CO2 port.

Water is pushed into the tank against CO2 back-pressure by a 100 PSI rated diaphragm pump, fed from a tap water inlet. The water path is: tap → ASSE 1022 carbonated-beverage backflow preventer (Multiplex 19-0897, lead-free brass body with SS internals, dual check with atmospheric vent, 10–200 PSI, 3/8" MPT × 3/8" MFL with 1/4" barb vent) → diaphragm pump → external metal-seat check valve (150 PSI rated, not the pump's internal elastomer check) → atomizer port on tank. The pump's own integrated checks are redundant layer #3, not the primary seal, because elastomer checks creep under sustained CO2 back-pressure and gas molecules migrate through elastomer seals that would hold liquid indefinitely.

ASSE 1022 (not 1024) is the correct standard for this application. 1022 is specifically "Backflow Preventer for Beverage Dispensing Equipment" — required because dissolved CO2 makes carbonic acid at pH ~3.5, which leaches lead from solder joints in household plumbing if it backfeeds. The Multiplex unit's atmospheric vent barb must be routed to an observable drip location (not plumbed into a drain), because the vent is the mechanical telltale: if check #1 leaks, the escaping water/CO2 becomes visible at the vent before anything backfeeds past check #2. The 3/8" MFL outlet connects to downstream 1/4" NPT plumbing via a 3/8" flare × 1/4" FNPT adapter (Hooshing B0BNHVV6HT).

Level sensing in the tank (capacitive, FDC1004-based) triggers the pump to refill **when the faucet is closed and level is below the refill threshold** — never during an active dispense. This is a hard firmware interlock, not a soft preference: introducing 18 °C tap water into the headspace during a pour raises the dispensed water temperature rapidly (2 °C → ~6 °C after one 12 oz pour under perfect-mix, worse in practice because the atomizing spray actively disrupts the thermal stratification the dip tube depends on). The tank functions as a thermal reservoir, not a real-time buffer: dispense until the low-level threshold, close the faucet, then the pump refills and the evaporator pulls the new water down to service temperature before the next pour is allowed.

Dispensing is a faucet lever. The carbonated water is already cold, carbonated, and under CO2 pressure — opening the valve sends it directly to the nozzle.

**Refrigeration subsystem**

Compressor, condenser + fan, capillary tube, and filter drier are harvested from a countertop ice maker. The evaporator cold plate is discarded and replaced with a custom-wound copper coil around the carbonator tank. Two ice makers purchased for teardown:

- Frigidaire EFIC117-SS (26lb/day) — ASIN B07PCZKG94, $78.70
- Generic countertop (8 cubes/6min, 26lb/day) — ASIN B0F42MT8JX, $63.80

Evaporator coil: GOORY 1/4" OD x 0.187" ID, C12200 ACR (ASTM B280), thick-wall (0.031") — ASIN B0DKSW5VL9. The 0.031" wall resists thinning at bends around the carbonator tank. For production runs, the same product ships in 50 ft rolls (largest thick-wall size on Prime). BELLA BAYS (ASIN B0BXKK62XL) is an equivalent alternative at the same spec.

Requires EPA 608 certification to handle R134a: recover the factory charge during teardown, evacuate the reassembled system, and recharge. Total component cost per unit: ~$100-110.

Fallback: the RIGID DV1910E (~$600 + 20-30% import tax) is a factory-sealed, pre-charged OEM module with a flexible copper coil evaporator that can be reshaped without breaking the refrigerant loop. No EPA 608 required. The cost premium buys a certification shortcut for retail channels (Amazon, big-box) that require UL/ETL listing.


**Cold core assembly (inside out)**

Layer 1: Custom-fabricated 304 SS racetrack carbonator vessel. Cross-section OD: 5.566" × 3.966". Length: 6.000". Horizontal orientation.

Layer 2: Copper evaporator coil wrapped tight around the tank with thermal compound. The horizontal orientation gives a longer wrapping surface than the previous vertical cylinder.

Layer 3: 3D-printed inner shell with ~1/4" gap, filled with two-part closed-cell spray polyurethane foam (Froth-Pak or equivalent). Vent holes in the shell allow excess foam to escape during cure; trimmed flush after hardening.

Layer 4: Two 3D-printed arch-shaped cradles, each holding a 1L Platypus bladder, forming a wrap around the insulated core. The bladders serve as flavor reservoirs and as a thermal mass buffer. Each bladder cap is drilled and fitted with a John Guest bulkhead fitting connecting to 1/4" hard RO tubing that runs to the peristaltic pumps. The bladders are permanent internal plumbing — filled from a user-accessible hopper via the pumps, cleaned in place by a software-controlled rinse cycle (water in, water out to nozzle, air in, air out to nozzle, repeat).

Layer 5: 3D-printed outer shell with ~1/2" to 3/4" gap, filled with spray foam, same process as inner layer.

Total cold core dimensions: TBD after spray foam and shell layers are added around the 5.566" × 3.966" × 6.000" vessel core.

The flavor reservoirs passively pre-chill to roughly 8-15°C by sitting in the thermal gradient between the near-freezing inner core and ambient air. The inner foam layer prevents the bladders from freezing against the evaporator.

**Flavor subsystem**

Two peristaltic pumps with food-grade silicone tubing, mounted in the replaceable pump cartridge assembly. The cartridge uses John Guest quick-connects and a palm-squeeze release plate for tool-free swap. The pumps pull flavor from the Platypus bladders and inject it at the dispense nozzle alongside the carbonated water. The same pumps run in reverse for filling the bladders from the hopper and for the clean cycle.

Each flavor has two input paths to the reservoir. The primary path is a funnel on the user-facing side for pouring from SodaStream concentrate bottles. The funnel has a removable dishwasher-safe silicone cover. The secondary path is a bag-in-box adapter on the rear of the enclosure — a barb or quick-connect fitting that connects to a standard BiB line. Both paths feed through the pump into the same internal refrigerated bladder. The BiB adapter is present but not prominently marketed; it serves customers who source their own commercial syrup.

**Enclosure layout**

The enclosure is an under-counter appliance, installed inside the kitchen cabinet beneath the sink. Its front face points toward the kitchen cabinet door; its back sits against the kitchen cabinet's rear wall. Front-to-back the internal layout runs: condenser + fan at the front, compressor in the middle-bottom just behind the condenser, valve manifold + 100 PSI diaphragm pump + Kamoer peristaltic pump cartridges stacked above the compressor in the middle, and the cold core occupying the full rear of the enclosure against the back wall.

Thermal zones separate cleanly. Hot side at the front: the condenser vents forward through a grille on the lower front face of the enclosure, drawing cool intake from the kitchen cabinet's toe-kick gap. Cold side at the back: the carbonator, bladders, and chilled dispense line, insulated by the cold core's inner and outer foam shells. The compressor bridges the two, positioned for short refrigerant lines to the front-mounted condenser; the longer suction run back to the evaporator coil around the carbonator is not efficiency-critical.

Placing the cold core at the back shortens the chilled dispense run to a minimum. The faucet penetration in the countertop is typically at the back edge (where the sink meets the backsplash), so the carbonated water line runs straight up from the cold core through a short insulated tube — minimizing heat pickup on the most temperature-critical path in the system.

**User-facing elements, by location**

*Above counter, through-counter fixtures over the sink:* faucet lever, KRAUS air switch for flavor select, RP2040 round display showing the active flavor's logo.

*Enclosure top, front half* (reached by the user opening their kitchen cabinet door — the enclosure itself has no hinged doors, its top is an integral funnel): flavor hopper, a large funnel covering most of the front half of the top face, sized to accept a pour from a SodaStream concentrate bottle without splash, feeding through solenoid-selected valves down to the appropriate internal bladder.

*Enclosure front face, middle:* pump cartridge access door (this one is on the enclosure itself) for swapping the Kamoer peristaltic pump when its silicone tubing wears out.

*Enclosure front face, lower:* condenser exhaust grille.

**Power**

12V DC. The compressor, driver board, diaphragm pump, peristaltic pumps, solenoid valves, and ESP32-S3 controller all run on DC. A 12V AC-DC power supply in the base or external brick provides wall power conversion.