Derek didn't ask for a Word doc — he asked for a synopsis inline. Let me write it directly.

**Carbonation subsystem**

The carbonator tank is a custom-fabricated 304 stainless steel cylinder, 1/16" (0.065") wall thickness, 5" outer diameter, 6" length. End caps are 1/4" (0.250") 304 SS flat discs, laser-cut by SendCutSend, sized to slip-fit inside the tube (4.860" diameter into 4.870" bore). The end caps are welded from the outside through the tube wall using an 800W fiber laser welder with ER308L filler wire.

All four ports are on the top end cap, via 1/4" NPT female weld bungs (body OD 0.700", flange OD 1.000") fillet-welded to the disc: CO2 in (headspace), water in (atomized into headspace via spiral cone nozzle), carbonated water out (dip tube extending to near-bottom), and a dedicated pressure relief valve port (100 PSI, ASME rated). The bottom end cap is a solid blank — no penetrations. The 5" diameter keeps it under the ASME Section VIII 6" exemption, eliminating pressure vessel certification requirements.

After welding, the vessel interior is passivated with a citric acid soak (4-10% concentration, warm water, 30-60 minutes) to restore the chromium oxide layer on heat-affected zones. The vessel is then hydro-tested to 105 PSI (1.5x working pressure) for 30 minutes before service.

CO2 supply is a standard regulated bottle, set to approximately 60-70 PSI, feeding directly into the tank headspace through the CO2 port.

Water is pushed into the tank against CO2 back-pressure by a 100 PSI rated diaphragm pump, fed from a tap water inlet. A check valve prevents backflow from the tank into the pump. Level sensing in the tank (capacitive, FDC1004-based) triggers the pump to refill as carbonated water is dispensed.

Dispensing is a faucet lever. The carbonated water is already cold, carbonated, and under CO2 pressure — opening the valve sends it directly to the nozzle.

**Refrigeration subsystem**

The RIGID DV1910E ($420) provides the complete refrigeration loop: a QX1901VDL 12V DC brushless rotary compressor (1.9cc, 720g, variable speed 2000-6000 RPM), driver board, micro-channel condenser (126×240×16mm) with centrifugal fan, capillary tube, filter drier, and a flexible copper coil evaporator — all pre-charged with R134a and factory sealed.

The copper coil ships wound at approximately 4" diameter and is bent open slightly to wrap snugly around the 5" carbonator tank. Thermal compound and clamping straps ensure contact. No refrigerant handling or EPA 608 certification is required because the system is never opened.

The condenser sits at the top front of the enclosure with the fan blowing hot air forward — no rear clearance needed. The compressor tucks beside or below the cold core.

**Cold core assembly (inside out)**

Layer 1: Stainless carbonator tank (5" diameter, 6" tall).

Layer 2: Copper evaporator coil from DV1910E, wrapped tight around the tank with thermal compound.

Layer 3: 3D-printed inner shell with ~1/4" gap, filled with two-part closed-cell spray polyurethane foam (Froth-Pak or equivalent). Vent holes in the shell allow excess foam to escape during cure; trimmed flush after hardening.

Layer 4: Two 3D-printed arch-shaped cradles, each holding a 1L Platypus bladder, forming a complete 360-degree wrap. The bladders serve as flavor reservoirs and as a thermal mass buffer. Each bladder cap is drilled and fitted with a John Guest bulkhead fitting connecting to 1/4" hard RO tubing that runs to the peristaltic pumps. The bladders are permanent internal plumbing — filled from a user-accessible hopper via the pumps, cleaned in place by a software-controlled rinse cycle (water in, water out to nozzle, air in, air out to nozzle, repeat).

Layer 5: 3D-printed outer shell with ~1/2" to 3/4" gap, filled with spray foam, same process as inner layer.

Total cold core diameter: approximately 9 inches. Total height: approximately 8 inches.

The flavor reservoirs passively pre-chill to roughly 8-15°C by sitting in the thermal gradient between the near-freezing inner core and ambient air. The inner foam layer prevents the bladders from freezing against the evaporator.

**Flavor subsystem**

Two peristaltic pumps with food-grade silicone tubing, mounted in the replaceable pump cartridge assembly. The cartridge uses John Guest quick-connects and a palm-squeeze release plate for tool-free swap. The pumps pull flavor from the Platypus bladders and inject it at the dispense nozzle alongside the carbonated water. The same pumps run in reverse for filling the bladders from the hopper and for the clean cycle.

Each flavor has two input paths to the reservoir. The primary path is a funnel on the user-facing side for pouring from SodaStream concentrate bottles. The funnel has a removable dishwasher-safe silicone cover. The secondary path is a bag-in-box adapter on the rear of the enclosure — a barb or quick-connect fitting that connects to a standard BiB line. Both paths feed through the pump into the same internal refrigerated bladder. The BiB adapter is present but not prominently marketed; it serves customers who source their own commercial syrup.

**Enclosure layout (back to front)**

Cold core cylinder sits against the rear wall. Pump cartridge assembly sits in front of it. Condenser and fan sit at top front, venting forward. Compressor tucks beside the cold core. All plumbing and wiring route through the gaps between these assemblies. User-facing elements: faucet lever, flavor hopper, and pump cartridge access on the front.

**Power**

12V DC. The compressor, driver board, diaphragm pump, peristaltic pumps, solenoid valves, and ESP32-S3 controller all run on DC. A 12V AC-DC power supply in the base or external brick provides wall power conversion.