Derek didn't ask for a Word doc — he asked for a synopsis inline. Let me write it directly.

**Carbonation subsystem**

The carbonator tank is an off-the-shelf VUYOMUA 0.8-gallon (3L) 304 stainless steel pressure tank (ASIN B0BV6FMMJP, ~$56), rated 180 PSI, with 1/4" NPT ports. This replaces the previous custom-fabricated cylinder/endcap/weld-bung approach, eliminating SendCutSend laser-cut end caps, weld bungs, fiber laser welding, and post-weld passivation. The tank is a commercially manufactured and pressure-rated horizontal cylinder. The `cut-parts/carbonator-endcaps/`, `cut-parts/carbonator-endcaps-racetrack/`, and `printed-parts/carbonator-forming-dies/` directories are now obsolete.

Port assignments (all 1/4" NPT — exact port count and placement TBD after inspecting the delivered unit): CO2 in (headspace), water in (atomized into headspace via spiral cone nozzle), carbonated water out (dip tube extending to near-bottom), and a dedicated pressure relief valve port (100 PSI, ASME rated). If the tank has fewer than four usable ports, additional ports can be drilled and tapped into the 304 SS wall.

The tank interior is coated with food-safe epoxy (e.g. MaxCLR A/B, FDA compliant when cured) to protect against long-term corrosion from carbonic acid (carbonated water, pH ~3.5-4). The vessel is hydro-tested to 150 PSI (1.5x working pressure) for 30 minutes before service as a verification step.

CO2 supply is a standard regulated bottle, set to approximately 60-70 PSI, feeding directly into the tank headspace through the CO2 port.

Water is pushed into the tank against CO2 back-pressure by a 100 PSI rated diaphragm pump, fed from a tap water inlet. A check valve prevents backflow from the tank into the pump. Level sensing in the tank (capacitive, FDC1004-based) triggers the pump to refill as carbonated water is dispensed.

Dispensing is a faucet lever. The carbonated water is already cold, carbonated, and under CO2 pressure — opening the valve sends it directly to the nozzle.

**Refrigeration subsystem**

Compressor, condenser + fan, capillary tube, and filter drier are harvested from a countertop ice maker. The evaporator cold plate is discarded and replaced with a custom-wound copper coil around the carbonator tank. Two ice makers purchased for teardown:

- Frigidaire EFIC117-SS (26lb/day) — ASIN B07PCZKG94, $78.70
- Generic countertop (8 cubes/6min, 26lb/day) — ASIN B0F42MT8JX, $63.80

Evaporator coil: GOORY 1/4" OD x 0.187" ID, C12200 ACR (ASTM B280), thick-wall (0.031") — ASIN B0DKSW5VL9. The 0.031" wall resists thinning at bends around the carbonator tank. For production runs, the same product ships in 50 ft rolls (largest thick-wall size on Prime). BELLA BAYS (ASIN B0BXKK62XL) is an equivalent alternative at the same spec.

Requires EPA 608 certification to handle R134a: recover the factory charge during teardown, evacuate the reassembled system, and recharge. Total component cost per unit: ~$100-110.

Fallback: the RIGID DV1910E (~$600 + 20-30% import tax) is a factory-sealed, pre-charged OEM module with a flexible copper coil evaporator that can be reshaped without breaking the refrigerant loop. No EPA 608 required. The cost premium buys a certification shortcut for retail channels (Amazon, big-box) that require UL/ETL listing.


**Cold core assembly (inside out)**

Layer 1: VUYOMUA 0.8-gallon 304 SS carbonator tank (horizontal cylinder — exact dimensions TBD after delivery, estimated ~5-6" diameter x ~10-12" long based on product photos).

Layer 2: Copper evaporator coil wrapped tight around the tank with thermal compound. The horizontal orientation gives a longer wrapping surface than the previous vertical cylinder.

Layer 3: 3D-printed inner shell with ~1/4" gap, filled with two-part closed-cell spray polyurethane foam (Froth-Pak or equivalent). Vent holes in the shell allow excess foam to escape during cure; trimmed flush after hardening.

Layer 4: Two 3D-printed arch-shaped cradles, each holding a 1L Platypus bladder, forming a wrap around the insulated core. The bladders serve as flavor reservoirs and as a thermal mass buffer. Each bladder cap is drilled and fitted with a John Guest bulkhead fitting connecting to 1/4" hard RO tubing that runs to the peristaltic pumps. The bladders are permanent internal plumbing — filled from a user-accessible hopper via the pumps, cleaned in place by a software-controlled rinse cycle (water in, water out to nozzle, air in, air out to nozzle, repeat).

Layer 5: 3D-printed outer shell with ~1/2" to 3/4" gap, filled with spray foam, same process as inner layer.

Total cold core dimensions: TBD after measuring delivered tank. The horizontal cylinder form factor will produce a wider, shorter cold core than the previous vertical design.

The flavor reservoirs passively pre-chill to roughly 8-15°C by sitting in the thermal gradient between the near-freezing inner core and ambient air. The inner foam layer prevents the bladders from freezing against the evaporator.

**Flavor subsystem**

Two peristaltic pumps with food-grade silicone tubing, mounted in the replaceable pump cartridge assembly. The cartridge uses John Guest quick-connects and a palm-squeeze release plate for tool-free swap. The pumps pull flavor from the Platypus bladders and inject it at the dispense nozzle alongside the carbonated water. The same pumps run in reverse for filling the bladders from the hopper and for the clean cycle.

Each flavor has two input paths to the reservoir. The primary path is a funnel on the user-facing side for pouring from SodaStream concentrate bottles. The funnel has a removable dishwasher-safe silicone cover. The secondary path is a bag-in-box adapter on the rear of the enclosure — a barb or quick-connect fitting that connects to a standard BiB line. Both paths feed through the pump into the same internal refrigerated bladder. The BiB adapter is present but not prominently marketed; it serves customers who source their own commercial syrup.

**Enclosure layout (back to front)**

Cold core cylinder sits against the rear wall. Pump cartridge assembly sits in front of it. Condenser and fan sit at top front, venting forward. Compressor tucks beside the cold core. All plumbing and wiring route through the gaps between these assemblies. User-facing elements: faucet lever, flavor hopper, and pump cartridge access on the front.

**Power**

12V DC. The compressor, driver board, diaphragm pump, peristaltic pumps, solenoid valves, and ESP32-S3 controller all run on DC. A 12V AC-DC power supply in the base or external brick provides wall power conversion.