# Bill of Materials — One Consumer Unit

Per-unit parts for a single finished appliance built on the **custom-vessel** path specified in [future.md](future.md). Carbonator vessel: vertical 5" OD × 0.065" wall 316 welded SS round tube (OnlineMetals #12498, MTRs required) capped with 1/4"-thick laser-cut 316 SS circular plates from SendCutSend (`endcap-circular-2hole.dxf`), joined with the XLaserlab X1 Pro handheld laser welder. 1/4" NPT is direct-tapped into the plates (no weld-in bungs). Compressor is harvested from a countertop ice-maker; cold core is 3D-printed shells with pour-in-place foam. Flavor reservoirs are custom printed food-grade PETG hard reservoirs ([printed-parts/cold-core/reservoir/generate_step_cadquery.py](printed-parts/cold-core/reservoir/generate_step_cadquery.py)), two per build.

Tools, fabrication equipment (welder, slip roll, shop press, dishing dies), and duplicate SKUs live in [purchases.md](purchases.md) only. Per-build consumables — anything used up making one unit, regardless of whether it ships in the product (mixing cups, gloves, citric acid, PTFE tape, cutting fluid, etc.) — live in this file with the rest of the per-unit parts.

First-pass draft. **Pricing convention: delivered cost** (product + shipping + tax) drawn from resolved order history in [purchases.md](purchases.md) wherever the SKU has been ordered or acquired; list price for forward-plan SKUs not yet purchased. Pack-amortized lines show the math in the description (e.g., `$31.08/2`). Expect revisions.

## 1. Controllers + electronics

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | | 1 | $11.00 | $11.00 |
| [ESP32 DIN Rail Breakout Board](https://www.amazon.com/dp/B0BW4SJ5X2) | | 1 | $25.99 | $25.99 |
| [Waveshare RP2040 Round LCD 0.99"](https://www.amazon.com/dp/B0CTSPYND2) | | 1 | $23.99 | $23.99 |
| [Meshnology ESP32-S3 1.28" Rotary Display](https://www.amazon.com/dp/B0G5Q4LXVJ) | | 1 | $47.76 | $47.76 |
| [L298N Dual H-Bridge (4-pack)](https://www.amazon.com/dp/B0C5JCF5RS) | 1 driver per unit drives both peristaltic pumps (dual H-bridge); 1 of 4 per unit ($10.71/4) | 1 (of 4 pk) | $2.68 | $2.68 |
| [Waveshare MCP23017 I2C GPIO expander](https://www.amazon.com/dp/B07P2H1NZG) | expands ESP32 I2C into 16 GPIO for solenoid bank | 1 | $12.99 | $12.99 |
| [HiLetgo DS3231 high-precision RTC (5-pk)](https://www.amazon.com/dp/B01N1LZSK3) | I2C RTC at 0x68, referenced in `wiring/esp32-pinout.mmd` and `wiring/valve-control.mmd`; 1 of 5 per unit ($16.08/5) | 1 (of 5 pk) | $3.22 | $3.22 |
| [EDGELEC 4.7 kΩ 1/4 W 1% metal-film resistor (100-pk)](https://www.amazon.com/dp/B07HDFHPP3) | DS18B20 1-wire bus pull-up between DATA and 3.3 V; 1 of 100 per unit ($5.89/100) | 1 (of 100 pk) | $0.06 | $0.06 |
| [Rubycon 470 µF 25 V low-ESR radial electrolytic capacitor, 10×12.5 mm (15-pk)](https://www.amazon.com/dp/B0F8BZVBKF) | bulk decoupling on the 12 V solenoid rail at the ULN2803A driver modules; 1 of 15 per unit ($7.40/15) | 1 (of 15 pk) | $0.49 | $0.49 |
| [ULN2803A high-current driver module (2-pc)](https://www.amazon.com/dp/B0F872W528) | 2 modules drive 12 solenoids from MCP23017 outputs; 1 full 2-pack per unit | 1 pk | $6.59 | $6.59 |
| [Mean Well IRM-90-12ST, 80 W / 12 V / 6.7 A, encapsulated](https://www.amazon.com/dp/B0CNRST18V) | 12 V supply for the low-voltage bus; IEC 60335-1 household-appliance safety listed | 1 | $31.66 | $31.66 |

## 2. Carbonator vessel (custom fabrication — plan A: round tube + 1/4" plates, 316L)

An earlier racetrack-body alternative (304 SS body half-sheets + dished racetrack end caps + 4× weld bungs) is no longer in active development; its parts inventory remains tracked in [purchases.md](purchases.md) §1, and the artifacts are preserved at the `archive-plan-b` git tag, in case the round-tube path is ever blocked.

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| OnlineMetals #12498 — 5" OD × 0.065" wall 316 welded SS round tube | cut to 6.0" length (MTRs required); OnlineMetals #1020857414 Apr 24: 10 @ $67.35 + ship + tax = $736.73 ÷ 10 = $73.67/ea | 1 | $73.67 | $73.67 |
| SendCutSend 1/4"-thick 316 SS circular endcap plate (`endcap-circular-2hole.dxf`) | 4.860" diameter with 2× 7/16" tap-pilot holes for 1/4" NPT; SCS SG019619 Apr 24: 20 @ $28.96 + tax = $621.19 ÷ 20 = $31.06/ea; 2 plates per vessel | 2 | $31.06 | $62.12 |
| [LTWFITTING 1/4" hose barb × 1/4" MNPT, 316 SS (5-pk)](https://www.amazon.com/dp/B017N4TTMA) | port 1 (CO2 in via internal sparge); threads into bottom plate, barb faces inward to silicone tube → sparge stone; 1 of 5 per unit ($13.65/5) | 1 (of 5 pk) | $2.73 | $2.73 |
| [TAISHER 2PCS 316L SS 90° Barstock Street Elbow, 1/4" NPT M × 1/4" NPT F](https://www.amazon.com/dp/B0CZ38MYL1) | all four vessel-port elbows (water inlet + carbonated-water outlet + CO2 inlet + PRV port); design rationale in [`assembly/pressure-vessel.md`](assembly/pressure-vessel.md). 4 elbows per build = 2 packs/build. Amazon 112-6323725 May 13: $20.99 + $1.52 tax = $22.51 ($11.26/ea × 4 = $45.04) | 4 (2 pk) | $11.26 | $45.04 |
| [FERRODAY 0.5 µm sintered 316 SS sparge stone, 1/4" barb input (2-set)](https://www.amazon.com/dp/B091C5Y6L9) | internal sparge stone, hangs in water column on silicone tube from port-1 barb adapter; 1 of 2 per unit ($14.97/2) | 1 (of 2) | $7.49 | $7.49 |
| Food-grade silicone tube stub, 1/4" ID × ~3" long (cut from existing Metaland 1/4" silicone B08L1ST6ST stock in §5) | connects port-1 barb to sparge stone inside vessel | — | ~$0.20 | $0.20 |
| [Millrose 70894 Nickel Guard anti-seize PTFE tape](https://www.amazon.com/dp/B07C9ZV4PG) | anti-seize for SS-into-SS NPT joints (4 ports per unit) | 1 | $20.07 | $20.07 |
| [Tap Magic EP-Xtra pipe-tap cutting fluid, 16 oz (size variant on listing B00DHMHSGM)](https://www.amazon.com/dp/B00DHMHSGM) | required for hand-tapping 1/4" NPT into 1/4"-thick 316 SS plate; ~$0.50 of fluid per vessel | 1 | $0.50 | $0.50 |
| [Control Devices SV-125 safety valve, 1/4" NPT, 125 psi set pressure, 49 SCFM relief, brass](https://www.amazon.com/dp/B01G2F6EMY) | Port 4 tank PRV (top plate, dedicated); sizing rationale in [`assembly/pressure-vessel.md`](assembly/pressure-vessel.md). Amazon 112-6323725 May 13: $7.49 + $0.54 tax = $8.03 | 1 | $8.03 | $8.03 |
| [Cambro 6 QT polycarbonate square container](https://www.amazon.com/dp/B001BZEQ44) | citric acid passivation soak tub, one-time-use per unit | 1 | $20.00 | $20.00 |
| [Viva Doria food-grade citric acid, 2 lb bag](https://www.amazon.com/dp/B0C5NQM8S1) | passivation: ~1 qt of 4% solution per tank; 1/20 of $9.99 bag | 1 | $0.50 | $0.50 |
| [STARTECHWELD ER316L .030 MIG wire, 10-lb spool](https://www.amazon.com/dp/B09BKFBXT9) | filler for the plate-to-tube and float-rod-to-plate laser welds; filler-alloy rationale in [`assembly/pressure-vessel.md`](assembly/pressure-vessel.md); ~12 g of wire per ~32" of weld per vessel × ~378 builds per 10-lb spool; $129.50/378 | 1 (of 378) | $0.34 | $0.34 |

## 3. Water inlet (tap → filter → backflow → pump → top-plate port)

The appliance ships with the water filter included. **Placement (internal vs. external to the enclosure) is TBD** — internal puts the cartridge behind the rear panel (customer-replaceable on a service interval), external lets the customer mount it inline upstream of the rear-panel inlet (familiar fridge-line install pattern). Either way it is in the box, sized to the customer's 1/4" OD line, and on our side of "the kit includes everything you need."

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Waterdrop 15UC-UF 0.01 µm inline water filter, 1/4" QC both ends](https://www.amazon.com/dp/B085G9TZ4L) | Upstream water filter; 1/4" QC fittings on both ends drop straight into the customer-side 1/4" LLDPE run. Same SKU already in `purchases.md §3` (ACQUIRED). Placement internal-vs-external to the enclosure is TBD per the section header above. | 1 | $62.99 | $62.99 |
| [Multiplex 19-0897 ASSE 1022 backflow preventer](https://www.midwestbev.com/products/asse-1022-backflow-preventer) | midwestbev MB11053 Apr 24: 4 @ $29.33 = $117.32 + $28.48 ship = $145.80 ÷ 4 = $36.45/ea | 1 | $36.45 | $36.45 |
| [brewhardware FFL38BARB38 swivel flare adapter, 3/8" FFL × 3/8" OD SS hose barb](https://www.brewhardware.com/product_p/ffl38barb38.htm) | single-piece adapter on the Multiplex 19-0897 MFL outlet; 304 SS wetted barb, chrome-plated brass swivel nut never touches water; brewhardware #156209 May 16: 5 @ $4.99 = $24.95 + $14.47 ship = $39.42 ÷ 5 = $7.88/ea | 1 (of 5 pk) | $7.88 | $7.88 |
| [JoyTube 3/8" ID × 1/2" OD food-grade silicone tubing, 10 ft](https://www.amazon.com/dp/B089YGDB55) | 3/8" ID food-grade silicone hose, ~12" per build between the brewhardware FFL38BARB38 hose-barb adapter (Multiplex 19-0897 MFL outlet side) and the SeaFlo 22-Series pump's 3/8" hose-barb inlet; covers the entire suction-side hose run with no diameter step-down. JoyTube ACQUIRED per `purchases.md:140`: $11.99 + $0.87 tax = $12.86 ÷ 10 builds = $1.286/build (10 ft × ~12"/build) | 1/10 roll (~12") | $1.29 | $1.29 |
| [Sealproof 1/4" ID × 3/8" OD clear PVC, 10 ft](https://www.amazon.com/dp/B07D9DK94V) (vent telltale) | | 1 | $8.46 | $8.46 |
| [LOKMAN 304 SS worm-gear clamps, 10–16 mm (20-pk)](https://www.amazon.com/dp/B076Q7QVNM) | vent line clamps; 4 of 20 per unit | 4 (of 20 pk) | $1.80 | $1.80 |
| [SEAFLO 22-Series 12V 1.3 GPM 100 psi diaphragm pump (3/8" hose-barb ports)](https://www.amazon.com/dp/B0166UBJX4) | | 1 | $48.25 | $48.25 |
| [MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4-pk)](https://www.amazon.com/dp/B0DMP77B6S) | adapts pump 3/8" hose-barb output to 1/4" NPT plumbing for the check valve and top-plate port; 1 of 4 per unit (also used in §8) | 1 (of 4 pk) | $3.24 | $3.24 |
| [GASHER 1/4" NPT SS one-way check valve (2-pk, $15.00)](https://www.amazon.com/dp/B0FV2D2FFX) | water-side check between SeaFlo pump and top-plate water-inlet port; PTFE-on-metal rationale in [`assembly/cold-core.md`](assembly/cold-core.md) "Warm-side check valves"; 1 of 2 valves per unit (the other valve is the CO2-side check in §4) | 1 (of 2) | $7.50 | $7.50 |
| [John Guest PP010822E 1/4" OD × 1/4" NPT male connector, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-male-connector-nptf-black-polypropylene-1-4-x-1-4-nptf) | 1/4" NPT M × 1/4" PTC adapter pair (warm-side + cold-side of the +Z slot transition on the water-inlet path); 2 per build; FWS WEBFWS100675224 May 15: $11.00 + $5.23 ship + $1.18 tax = $17.41 ÷ 10 = $1.741/ea | 2 (of 10 pk) | $1.74 | $3.48 |
| [Lifevant 1/4" OD water tubing 32.8 ft + quick-connects](https://www.amazon.com/dp/B0DKCZ5W66) | water-inlet tubing (filter → pump → vessel) ~8–10 ft + ~5 of 12 quick-connects per unit; ~1/3 of pack. Generic Amazon PE listing with no third-party food cert (vendor doesn't list one) — short-term use without certification | 1 (~1/3 pk) | $3.33 | $3.33 |
| [John Guest 1/4" OD × 1/8" NPT push-fit](https://www.amazon.com/dp/B07V6XKZG9) | | 1 | $5.00 | $5.00 |
| [John Guest PI1208S acetal bulkhead union, 1/4" QC](https://www.amazon.com/dp/B0C1F3QR7N) | | 1 | $11.49 | $11.49 |

## 4. CO2 subsystem

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Wellbom dual-gauge CO2 regulator, CGA-320, 0–120 PSI out / 150 PSI PRV](https://www.amazon.com/dp/B0G13P5PMY) | | 1 | $44.99 | $44.99 |
| [Interstate Pneumatics WR1110 1/4" NPT in-line 90 PSI fixed pre-set pressure regulator, 230 PSI max inlet, aluminum body](https://www.amazon.com/dp/B07J2L8LF3) | in-appliance secondary regulator between the customer's CGA-320 primary regulator (above) and the vessel CO2 inlet; setpoint rationale in [`assembly/pressure-vessel.md`](assembly/pressure-vessel.md) "CO2 supply". Amazon 112-6323725 May 13: $23.93 + $1.73 tax = $25.66 | 1 | $25.66 | $25.66 |
| [John Guest PP010822E 1/4" OD × 1/4" NPT male connector, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-male-connector-nptf-black-polypropylene-1-4-x-1-4-nptf) | 1/4" NPT M × 1/4" PTC adapter pair (WR1110 outlet + TAISHER vessel-port elbow on the CO2-inlet path); 2 per build; FWS WEBFWS100675224 May 15: $11.00 + $5.23 ship + $1.18 tax = $17.41 ÷ 10 = $1.741/ea | 2 (of 10 pk) | $1.74 | $3.48 |
| [John Guest PP0308E 1/4" OD union elbow, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-union-elbow-black-polypropylene-1-4) | 90° PTC × PTC union elbow forming the in-cavity 90° bend in the CO2 path inside the foam shell per [printed-parts/cold-core/foam-shell/README.md](printed-parts/cold-core/foam-shell/README.md); 2 per build; FWS WEBFWS100675224 May 15: $16.87 + $8.02 ship + $1.81 tax = $26.70 ÷ 10 = $2.670/ea | 2 (of 10 pk) | $2.67 | $5.34 |
| [5/16" ID beer CO2 line, 10 ft + 4 clamps](https://www.amazon.com/dp/B0D1RB3TF6) | ~12 in short tether (customer's CGA-320 regulator → front-panel inlet) + 2 of 4 clamps per unit; ~1/4 of pack value | 1 (~1/4 pk) | $3.50 | $3.50 |
| [DERPIPE 5/16" tube × 1/4" NPT push-to-connect (5-pk)](https://www.amazon.com/dp/B09LXVGPG7) | CO2 line entry to vessel; 1 of 5 per unit ($10.71/5). **5/16" variant appears delisted; source replacement ASIN** | 1 (of 5 pk) | $2.14 | $2.14 |
| [GASHER 1/4" NPT SS one-way check valve (2-pk, $15.00) — second of pack](https://www.amazon.com/dp/B0FV2D2FFX) | CO2-side check between DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the LTWFITTING bottom-plate barb adapter; rationale in [`assembly/cold-core.md`](assembly/cold-core.md) "Warm-side check valves". Same 2-pack as the §3 water-side check, second valve of the pair | 1 (of 2) | $7.50 | $7.50 |

## 5. Refrigeration (harvested compressor path)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Frigidaire EFIC117-SS ice-maker donor (compressor/condenser/cap-tube/drier)](https://www.amazon.com/dp/B07PCZKG94) | | 1 | $78.70 | $78.70 |
| [GOORY 1/4" OD × 50 ft ACR copper coil (evaporator)](https://www.amazon.com/dp/B0DKSW5VL9) | single-layer wrap on 5" OD vessel at 1/8" gap pitch yields ~22 ft of wrap per unit + ~2 ft each end for compressor + suction-line tie-ins ≈ ~24 ft consumed per unit; one 50 ft roll comfortably covers 2 units, so 1/2 roll allocated per unit ($68.63/2) | 1/2 roll | $34.32 | $34.32 |
| [Supco SUD8358 filter-drier, 1/4" sweat × cap-tube outlet, XH-9 molecular sieve, integrated Schrader access port](https://www.amazon.com/dp/B009AX2O5W) | replacement filter-drier installed during refrigerant-loop assembly; spec rationale in [`assembly/refrigerant-loop.md`](assembly/refrigerant-loop.md) Inputs | 1 | $13.40 | $13.40 |
| [Teyleten 3.3 V relay module, opto-isolated, 10 A @ 250 VAC (5-pk)](https://www.amazon.com/dp/B07XGZSYJV) | two relays per unit: relay #1 switches the compressor's 120 VAC hot leg (ESP32 GPIO 14), relay #2 gates 12 V to the SeaFlo diaphragm pump for firmware-controlled refill (ESP32 GPIO 4); 2 of 5 per unit | 2 (of 5 pk) | $2.60 | $5.20 |
| [HiLetgo DS18B20 waterproof 1-wire probe, 1 m SS sheath (5-pk)](https://www.amazon.com/dp/B00M1PM55K) | 2 probes per unit: tank wall (compressor cycling setpoint) + evaporator coil (freeze-protect cutout); 2 of 5 per unit ($11.79/5 × 2) | 2 (of 5 pk) | $2.36 | $4.72 |
| [MXR IEC 60320 C14 panel-mount AC inlet, 10 A / 250 VAC (10-pk)](https://www.amazon.com/dp/B07DCXKNXQ) | rear-panel mains inlet; accepts standard NEMA 5-15P-to-C13 line cord; 1 of 10 per unit ($6.96/10) | 1 (of 10 pk) | $0.70 | $0.70 |
| [Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed (6-pk)](https://www.amazon.com/dp/B08VS8D4WC) | ships in the box so the customer can plug the appliance into a standard US wall outlet; 1 of 6 per unit ($24.00/6) | 1 (of 6 pk) | $4.00 | $4.00 |
| [Legrand Radiant 1597BKCCD12 15 A self-test GFCI, decorator duplex, black](https://www.amazon.com/dp/B017HAB4BO) | UL 943 Class A 6 mA personnel-protection device, mounted inside the appliance face-flush with the back of the printed front panel; a cutout in the front panel exposes only the central TEST/RESET/LED band (the two 5-15R receptacle outlets sit behind the printed material, not customer-accessible). Wired inline between C14 inlet LOAD and the AC distribution block — protection lives in the appliance, not in the cord, so the C14 inlet's swappable-C13-cord property is preserved per [`../business/regulatory.md`](../business/regulatory.md) "UL 943 — ground-fault protection". Self-test every 3 seconds (vs industry-standard hours) + SafeLock end-of-life lockout. Amazon 112-6714135 May 20: 2 @ $19.45 + $2.82 tax = $41.72 ÷ 2 = $20.86/ea | 1 | $20.86 | $20.86 |
| [Enviro-Safe R-600a 3-pack + brass charging gauge](https://www.amazon.com/dp/B0CGG1WH1N) | pure R-600a; refills the sealed loop after venting factory charge; ~40 g per system × ~12 recharges per 3-can bundle; 1/12 of $72.92 delivered; brass gauge stays with tools (see purchases.md) | 1 | $6.08 | $6.08 |
| [Supco BPV31 bullet-piercing valve](https://www.amazon.com/dp/B00DM8J3MI) | taps the compressor process tube to vent the factory R-600a charge before brazing in the replacement drier; left clamped on the cut stub after teardown; single-use per build | 1 | $7.37 | $7.37 |
| [BCuP-5 15% Ag silver brazing alloy, 1/16" × 1 troy oz rod](https://www.amazon.com/dp/B0DQ3ZMHK7) | filler for copper-to-copper refrigeration joints; ~10 g per build × ~3 builds per 31 g rod; $18.99/3 | 1 (of 3) | $6.33 | $6.33 |
| [3M Scotch-Brite Maroon General Purpose Hand Pads, 6" × 9" (1-pack of 20)](https://www.amazon.com/dp/B07CGPCTHT) | abrasive pads cut into strips to clean 1/4" ACR copper OD + fitting sockets before flux + braze on the 2–3 refrigeration-loop joints; 2 of 20 per build ($28.85/20 × 2) | 2 (of 20 pk) | $1.44 | $2.89 |
| SendCutSend compressor shroud (`cut-parts/compressor-shroud/`) | 0.059" G90 hot-dipped galvanized steel; design + rationale at [`cut-parts/compressor-shroud/README.md`](cut-parts/compressor-shroud/README.md). Final dimensions TBD pending donor compressor measurement; placeholder estimate for a ~130 × 130 × 100 mm flat-pattern part with 4 bends + hardware insertion: ~$8 ea at qty 5 + ~$5 ship + tax allocated, ~$45 delivered ÷ 5 = $9/shroud. AC pass-through grommet listed separately below (Heyco SB-500-6) | 1 | $9.00 | $9.00 |
| [Heyco SB-500-6 (Heyco part #2053) black 6/6 nylon strain-relief snap bushing, 100-pack](https://www.amazon.com/HEYCO-2053-SB-500-6-Accessories/dp/B01LPBST9G/) | UL Recognized AC pass-through strain-relief bushing for the compressor-shroud 1/2" panel hole; sizing rationale in [`cut-parts/compressor-shroud/README.md`](cut-parts/compressor-shroud/README.md) Penetrations; 100-pack = lifetime supply; per-build cost = $12.60 delivered / 100 | 1 (of 100 pk) | $0.13 | $0.13 |
| [BOJACK SF76E SEFUSE thermal fuse, 77 °C, 10 A / 250 V (10-pack)](https://www.amazon.com/dp/B07Y61YTTK) | hardware thermal cutoff in series with the compressor's AC hot leg inside the shroud; safety rationale in [`assembly/refrigerant-loop.md`](assembly/refrigerant-loop.md) "Safety". 1 of 10 per unit ($6.42/10) | 1 (of 10 pk) | $0.64 | $0.64 |
| [ACEIRMC MQ-6 LPG / iso-butane combustible gas sensor module (5-pack)](https://www.amazon.com/dp/B0978JSCZ8) | combustible-gas sensor mounted low on the rear interior enclosure wall (catches dense R-600a pooling at the cabinet floor); safety rationale in [`assembly/refrigerant-loop.md`](assembly/refrigerant-loop.md) "Safety". 1 of 5 per unit ($11.79/5) | 1 (of 5 pk) | $2.36 | $2.36 |

Fallback path (UL/ETL-retail-friendly): RIGID DV1910E sealed refrigeration module (~$600 + 20–30% import duty). Not selected for this BOM.

## 6. Cold core insulation

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Fiberglass Supply Depot 2 lb 2-part closed-cell pour-in-place PU foam, 1 qt kit](https://www.amazon.com/dp/B08R7TX8QJ) | 1.25 ft³ yield covers inner + outer shells with margin; Amazon 112-5359790 May 15: $39.99 + $2.90 tax = $42.89 | 1 kit | $42.89 | $42.89 |
| [3M 425 aluminum foil tape, 2" × 180 ft](https://www.amazon.com/dp/B07BTW7C2N) | thermally conductive aluminum foil bonding the evaporator coil to the vessel OD; applied during refrigerant-loop assembly step 4; one 180 ft roll covers ~12 builds at ~15 ft/build; 1/12 of $88.97 | 1 | $7.41 | $7.41 |
| [Pouring Masters 5 oz / 150 mL graduated mixing cups (50-pk)](https://www.amazon.com/dp/B08JHH1DBF) | foam-pour consumable; 4 cups per build for batching the 2-part PU foam in measured shots; $20.37/50 × 4 | 4 (of 50 pk) | $0.41 | $1.63 |
| [JMU 6" tongue depressors, individually wrapped (100-pk)](https://www.amazon.com/dp/B09H6ZP447) | foam-pour consumable; 4 stir sticks per build for hand-mixing 2-part PU foam in the graduated cups; $7.50/100 × 4 | 4 (of 100 pk) | $0.08 | $0.30 |
| [SUP powder-free 4 mil nitrile exam gloves, XL, 100-pk = 50 pairs](https://www.amazon.com/dp/B0G8SSMVKW) | foam-pour PPE; 1 pair per build (PU foam isocyanate component is a skin sensitizer); $7.49/50 pairs × 1 | 1 pair (of 50) | $0.15 | $0.15 |

## 7. Printed mechanical parts (PETG @ $12.99/kg)

Rough filament estimates for all printed geometry. Revise once STLs are final and slicer reports actual mass per part.

| Part | Mass (kg) | $ |
|---|---:|---:|
| Cold-core inner shell (retains foam around vessel) | 1.0 | $12.99 |
| Cold-core outer shell (retains outer foam layer) | 1.5 | $19.49 |
| Bladder cradles (2× arch, flavor reservoirs) | 0.5 | $6.50 |
| Outermost enclosure (under-counter cabinet housing) | 3.5 | $45.47 |
| Flavor hopper funnel (top-front, SodaStream-pour sized) | 0.4 | $5.20 |
| Pump cartridge assembly + access door | 0.5 | $6.50 |
| Miscellaneous (condenser grille, fitting bosses, brackets, faucet gooseneck cover, cable-gland mounts) | 0.6 | $7.79 |
| **Printed parts total** | **~8.0** | **$103.94** |

Dishing dies (PA6-CF) for end-cap forming are vessel-fabrication tools, not shipped product — excluded.

## 8. Flavor subsystem

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Kamoer KPHM400-SW3B25 12V peristaltic pump](https://www.amazon.com/dp/B09MS6C91D) | paid price per Feb 2026 Amazon 114-1015191 + 112-0545074 (Kamoer Fluid Tech Shanghai); current listing matches at $32.55 | 2 | $32.55 | $65.10 |
| [Magnetic pogo pin connector, 2-pin (2 pair)](https://www.amazon.com/dp/B0CSX6ZQ1H) | tool-free pump cartridge electrical connection, one pair per pump | 1 pk | $10.71 | $10.71 |
| [Beduan 12V 1/4" solenoid valve (NC)](https://www.amazon.com/dp/B07NWCQJK9) | V-A/B/C/D/E/F/G/H/I/J/KA/KB per fluid-topology-manifold.mmd; lower-bound delivered single-unit cost (range $9.64–$19.28 across user's mixed orders) | 12 | $9.64 | $115.68 |
| [John Guest PP1208E 1/4" OD black polypropylene push-to-connect bulkhead union (10-pk)](https://www.amazon.com/dp/B00JYFU8MM) | two uses, same SKU: (a) **reservoir-cap outlet port** — syrup-side 1/4" QC bulkhead recessed in the printed reservoir floor boss per [printed-parts/cold-core/reservoir/generate_step_cadquery.py](printed-parts/cold-core/reservoir/generate_step_cadquery.py) lines 251–310; 1 per reservoir × 2 = 2/build; (b) **rear-panel umbilical port** — 3 bulkheads on the enclosure back panel accepting the 3-tube under-cabinet-faucet umbilical (1 carbonated water + 2 flavors), one bulkhead marked with a blue accent ring to match the blue-color-coded carbonated-water tube per [printed-parts/enclosure/back-panel/README.md](printed-parts/enclosure/back-panel/README.md); 3/build. Total **5/build**; the in-hand 10-pk now covers 2 builds of stock (was 5 builds at the prior 2/build). Amazon 112-6407862 May 11: $23.11 + $1.68 tax = $24.79 ÷ 10 = $2.479/ea | 5 (of 10 pk) | $2.48 | $12.40 |
| [Silicone tubing 1/8" ID × 1/4" OD](https://www.amazon.com/dp/B0BM4KQ6RT) | pump-head tube only (line runs are 1/4" LLDPE); stretch-fit over the Kamoer KPHM400 BPT barb per [`off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md`](off-the-shelf-parts/kamoer-kphm400/extracted-results/geometry-description.md):34; $13.93 delivered, amortized 1 roll/build pending real per-unit measurement | 1 | $13.93 | $13.93 |
| [Supply Depot BIB connector, 3/8" red (2-pk)](https://www.amazon.com/dp/B0DMFK9B6P) | rear-panel commercial-syrup input | 1 pk | $19.99 | $19.99 |
| [MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4-pk)](https://www.amazon.com/dp/B0DMP77B6S) | | 1 pk | $12.97 | $12.97 |
| [John Guest PP010822E 1/4" OD × 1/4" NPT male connector, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-male-connector-nptf-black-polypropylene-1-4-x-1-4-nptf) | 1/4" NPT M × 1/4" PTC adapter pair (one per BiB-input leg, between MAACFLOW 3/8" barb × 1/4" NPT M and the LLDPE feeding the PP2308E Y-divider below); 2 per build; FWS WEBFWS100675224 May 15: $11.00 + $5.23 ship + $1.18 tax = $17.41 ÷ 10 = $1.741/ea | 2 (of 10 pk) | $1.74 | $3.48 |
| [John Guest PP2308E two-way divider, black polypropylene 1/4"](https://www.freshwatersystems.com/products/john-guest-two-way-divider-black-polypropylene-1-4) | manifold Y-A/B/C/D/E/F/G/H/KA/KB per fluid-topology-manifold.mmd, 10 per unit; FWS WEBFWS100673541 May 9: 2 bags of 10 @ $61.66 = $30.83/bag = $3.083/ea pre-tax/ship | 10 (1 bag) | $3.083 | $30.83 |
| [Siptenk 1/4" OD brass tube stiffener insert (100-pk)](https://www.amazon.com/dp/B0FM77LLM1) | required on the LLDPE side of the carbonated-water tube end that lands in the Westbrass body's upstream compression port (per [`assembly/faucet-and-umbilical.md`](assembly/faucet-and-umbilical.md) step 2) so the brass ferrule does not crush the soft tube; 1 stiffener per build ($8.99/100) | 1 (of 100 pk) | $0.09 | $0.09 |

## 9. Dispensing (carbonator bottom-plate outlet → faucet)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [VALVENTO 1/4" OD compression × 1/4" NPT adapter (2-pk)](https://www.amazon.com/dp/B0DXZZBK7D) | joins bottom-plate 1/4" NPT outlet port (port 3) to 1/4" tubing run; 1 of 2 per unit (pack delivered $12.85/2) | 1 (of 2) | $6.42 | $6.42 |
| [Westbrass R2031-NL-62 8" Touch-Flo dispenser faucet, matte black](https://www.amazon.com/dp/B07KH285GJ) | donor faucet; family-equivalence + interchangeable-finish notes in [`printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](printed-parts/faucet/touch-flo-shell/ASSEMBLY.md) "Adjacent parts" | 1 | $31.28 | $31.28 |
| SendCutSend 0.060" 316 SS under-counter plate (`touch_flo_under_counter_plate.dxf`) | dimensions + role in [`printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](printed-parts/faucet/touch-flo-shell/ASSEMBLY.md) "Adjacent parts"; SCS S064D925 May 10: 10 @ $2.85 + $5.00 ship + $2.79 tax = $36.29 ÷ 10 = $3.63/ea | 1 | $3.63 | $3.63 |
| [DIGITEN G3/8" Hall-effect flow sensor](https://www.amazon.com/dp/B07QQW4C7R) | | 1 | $7.99 | $7.99 |
| [CARGEN Pipe Insulation Foam Tube, 1/4" ID × 3/8" wall × 6 ft, nitrile rubber closed-cell](https://www.amazon.com/dp/B0D2XFK337) | insulates the 1/4" OD LLDPE carbonated-water dispense tube from the foam-shell exit through the countertop to the underside of the Westbrass touch-flo body. ~12" per build, 72"/roll = 6 builds/roll. Amazon 112-3935659 May 15: 2 @ $7.59 + $1.10 tax = $16.28 ÷ 12 builds = $1.36/build | 1/6 roll (~12") | $1.36 | $1.36 |

## 10. User interface

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [KRAUS garbage-disposal air-switch, matte black](https://www.amazon.com/dp/B096319GMV) | | 1 | $39.95 | $39.95 |
| [DIYables Passive Piezo Buzzer Module, 5 V (2-pack)](https://www.amazon.com/dp/B0DYDN31PV) | audible-alarm output driven by ESP32 GPIO; 1 of 2 per unit ($6.42/2) | 1 (of 2 pk) | $3.21 | $3.21 |

## 11. Wiring + fasteners

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Dupont Jumper Wires (120-pack)](https://www.amazon.com/dp/B0BRTJXND9) | ~25 jumpers per unit (controller ↔ driver + sensors); 25/120 | 25 (of 120 pk) | $1.33 | $1.33 |
| [Female Spade Crimp Terminals (60-pack)](https://www.amazon.com/dp/B0B9MZJ2ML) | ~30 terminals per unit (12 solenoids × 2 leads + relay + flow sensor + misc); 30/60 = 1/2 pack | 30 (of 60 pk) | $5.36 | $5.36 |
| [Male Quick-Disconnect Spade (100-pack)](https://www.amazon.com/dp/B01MZZGAJP) | ~30 male spades per unit (harness side, paired with female terminals); 30/100 | 30 (of 100 pk) | $1.93 | $1.93 |
| [Zip Ties (200-pack)](https://www.amazon.com/dp/B0BC1VH4XB) | ~15 zip ties per unit (cable management); 15/200 | 15 (of 200 pk) | $0.30 | $0.30 |
| [CQRobot JST XH 2.54 mm 4-pin connector kit (50 sets)](https://www.amazon.com/dp/B0B2RB524Y) | 4-pin XH housings + headers + crimp terminals; pin-count assignments in [`wiring/ac-wiring-schedule.md`](wiring/ac-wiring-schedule.md) "Inter-module connectors"; ~3/unit; $8.45/50 × 3 | 3 (of 50 pk) | $0.17 | $0.51 |
| [CQRobot JST XH 2.54 mm 6-pin connector kit (50 sets)](https://www.amazon.com/dp/B0B2R8Q1JL) | 6-pin XH; ~1/unit; $9.19/50 | 1 (of 50 pk) | $0.18 | $0.18 |
| [CQRobot JST XH 2.54 mm 9-pin connector kit (30 sets)](https://www.amazon.com/dp/B0B2R73RQB) | 9-pin XH; ~6/unit; $9.19/30 × 6 | 6 (of 30 pk) | $0.31 | $1.84 |
| [CQRobot JST XH 2.54 mm pre-crimped bonded ribbon kit, 15 cm × 12 conductors × 8 ribbons + assorted housings](https://www.amazon.com/dp/B0F6C7X5CR) | short-hop bonded ribbon for module-to-module connections (≤6"); ~2/unit; $15.86/8 × 2 | 2 (of 8 pk) | $1.98 | $3.97 |
| [Keszoox JST XH 2.54 mm pre-crimped wires, 50 cm × 22 AWG silicone (20 wires/pk, 10 colors)](https://www.amazon.com/dp/B0F8HMQRRN) | cabinet-spanning pre-crimped female XH pigtails (ULN→solenoid fan-outs, sensor pigtails); ~1 pk/unit | 1 pk (of 20 wires) | $11.63 | $11.63 |
| 16 AWG stranded silicone-insulated appliance wire (black/white/green) | placeholder pending sourcing decision; AC pigtails for the C14 → distribution → relay → compressor + PSU runs per [`wiring/ac-wiring-schedule.md`](wiring/ac-wiring-schedule.md); ~3 ft total per build across all AC runs (AC-1 through AC-6 in the schedule) | — | ~$1.87 | $1.87 |
| 18 AWG stranded hookup wire (12 V trunk + branch) | placeholder pending sourcing decision; runs DC-1 through DC-9 in [`wiring/ac-wiring-schedule.md`](wiring/ac-wiring-schedule.md) | — | ~$0.50 | $0.50 |
| Wago 221-413 lever-nut connector, 3-conductor | placeholder pending sourcing decision; AC distribution block on the electronics shelf (H, N, G — one connector per conductor); 3 connectors per build, ~$0.85 each at 10-pk pricing | 3 | $0.85 | $2.55 |

## 12. Level sensing (external reed + internal magnetic float on 316L SS rod, shared SKU across carbonator + reservoirs)

The same reed-and-float pattern is used in three places: the carbonator vessel (2 reeds, threshold-only) and each flavor reservoir (4 reeds per reservoir × 2 = 8 reeds, ~13-serving-step granularity / 5-state fuel-gauge display). All three use the same 1/8" 316L SS rod (Tandefio B0CY4DWJFQ) as the float guide. Flavor-reservoir architecture, rod material rationale, and rod-end retention geometry in [`printed-parts/cold-core/reservoir/level-sensing.md`](printed-parts/cold-core/reservoir/level-sensing.md) and [`printed-parts/cold-core/reservoir/generate_step_cadquery.py`](printed-parts/cold-core/reservoir/generate_step_cadquery.py) (`ROD_*` and `BODY_BOSS_*` constants).

### Carbonator (2 reeds, threshold-only)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [DEVMO MINI float switch (donor — harvest magnetic donut float, discard switch body)](https://www.amazon.com/dp/B07T18PGJ4) | float slides on the welded SS rod; only the float is shipped product, the rest of the donor unit is discarded | 1 | $13.93 | $13.93 |

### Flavor reservoirs (4 reeds per reservoir × 2 reservoirs = 8 reeds, ~13-serving-step granularity)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| Pre-soldered reed-and-wire column | 4 Gebildet reeds hand-soldered to a multi-conductor cable, inserted into the foam-shell channel before the body pour. Architecture in [`printed-parts/cold-core/reservoir/level-sensing.md`](printed-parts/cold-core/reservoir/level-sensing.md). Cable candidate KWANGIL 22 AWG 12-conductor UL2464 ([B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21)) under evaluation per [purchases.md](purchases.md). Reeds in shared §12 line below; cable TBD | 2 columns per build | — | — |
| [DEVMO MINI float switch (donor — harvest donut + ferrite magnet)](https://www.amazon.com/dp/B07T18PGJ4) | donor donut + its ferrite magnet kept (switch body / cable discarded); slides on the 1/8" 316L SS rod inside each reservoir. Architecture + magnet-strength rationale in [`printed-parts/cold-core/reservoir/level-sensing.md`](printed-parts/cold-core/reservoir/level-sensing.md) | 2 (1 per reservoir) | $13.93 | $27.86 |

### Float-guide rod (shared SKU across carbonator + flavor reservoirs)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Tandefio 1/8" × 12" 316 SS round rod (5-pk)](https://www.amazon.com/dp/B0CY4DWJFQ) | float-guide rod used in three places per build: (a) carbonator vessel — ~6" cut, laser-welded between plates (1/2 stick per build); (b) each flavor reservoir — ~200 mm rod dropped into a printed BODY boss (1 full stick per reservoir × 2 reservoirs). Total = 2.5 sticks/build; $8.57/5 × 2.5 = $4.29/build. Reservoir-side material rationale in [`printed-parts/cold-core/reservoir/level-sensing.md`](printed-parts/cold-core/reservoir/level-sensing.md) | 2.5 (of 5 pk) | $1.71 | $4.29 |

### Reeds (shared SKU across carbonator + flavor reservoirs)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Gebildet reed switches, 14 mm glass body, NO (6-pk)](https://www.amazon.com/dp/B0CW9418F6) | 10 reeds per build (2 carbonator + 8 flavor reservoir at 4 each × 2 reservoirs). 2 × 6-pack = 12 reeds, 2 spares | 10 (of 2 × 6 = 12) | $1.07 | $10.71 |

### GPIO expansion for the 8 new flavor-reservoir reed inputs

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Waveshare MCP23017 I2C GPIO expander, second instance](https://www.amazon.com/dp/B07P2H1NZG) | same SKU as the existing expander in §1, second instance at I²C address 0x21 for Reservoir B's 4 reeds on PA[0:3] (12 spare bits remain). See [`printed-parts/cold-core/reservoir/level-sensing.md`](printed-parts/cold-core/reservoir/level-sensing.md) "GPIO budget" | 1 | $12.99 | $12.99 |

## 13. Mechanical attach hardware (heat-set inserts + screws + gasket) + reservoir-cap vent filter

Heat-set + screw retention appears in three places:

1. **Touch-flo plate** clamped to the `touch-flo-shell` via 2 ruthex inserts + 2 McMaster ULH screws — assembly + screw rationale in [`printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](printed-parts/faucet/touch-flo-shell/ASSEMBLY.md).
2. **Foam-bag-shell caps** clamped to the `outer_shell` via 12 ruthex inserts + 12 BNUOK M3×25 SHCS, TPU 90A gasket compressing per cap — procedure in [`assembly/cold-core.md`](assembly/cold-core.md).
3. **Reservoir cap** clamped to each reservoir body via 6 ruthex inserts + 6 BNUOK M3×12 SHCS per cap, TPU gasket — geometry + screw spec in [`printed-parts/cold-core/reservoir/generate_step_cadquery.py`](printed-parts/cold-core/reservoir/generate_step_cadquery.py).

Each reservoir cap also carries a ø13 mm hydrophobic PTFE membrane vent filter — see [`printed-parts/cold-core/reservoir/vent.md`](printed-parts/cold-core/reservoir/vent.md) for the splash-baffle architecture; 1 filter per cap × 2 caps per build = 2 per build.

The T18 heat-set tip kit ([B0CS662NVK](https://www.amazon.com/dp/B0CS662NVK)) and the FX-888D iron are tooling — not per-unit. TPU 90A gasket filament is consumed from per-unit-trivial stock; not separately listed.

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [ruthex M3 Threaded Inserts Short, 100 pc, RX-M3Sx4.0 brass heat-set](https://www.amazon.com/dp/B0D39W228K) | M3 × 4 mm L × 4.2 mm OD knurled brass; 26 per build (2 touch-flo + 12 foam-bag-shell + 12 reservoir caps); Amazon 112-4234665 May 10: $9.99 + $0.72 tax = $10.71 ÷ 100 = $0.1071/ea | 26 (of 100 pk) | $0.11 | $2.78 |
| [McMaster-Carr 91223A412 — 316 SS Ultra-Low-Profile Socket Head Screw, M3 × 0.50 mm × 6 mm long](https://www.mcmaster.com/91223A412/) | touch-flo plate clamp screws; 2 per build; supersedes M3 × 8 mm 91223A413 (8 mm bottomed out against the insert's closed top, holding the head 1 mm proud); McMaster 7833043 May 22: 8 @ $4.54 = $36.32 + $11.88 ship + $3.49 tax = $51.69 ÷ 8 = $6.46/ea | 2 (of 8) | $6.46 | $12.92 |
| [BNUOK M3 × 25 mm DIN 912 socket head cap, 12.9 alloy steel, black oxide, 60 pc](https://www.amazon.com/dp/B0DJQGF665) | foam-bag-shell cap clamp screws (6 top + 6 bottom); Amazon 112-2495614 May 10: $7.99 + $0.58 tax = $8.57 ÷ 60 = $0.1428/ea | 12 (of 60 pk) | $0.14 | $1.71 |
| [BNUOK M3 × 12 mm DIN 912 socket head cap, 12.9 alloy steel, black oxide, 120 pc](https://www.amazon.com/dp/B0DJQGVK8S) | reservoir-cap clamp screws (6 per cap × 2 caps); Amazon 112-0144900 May 10: $7.99 + $0.58 tax = $8.57 ÷ 120 = $0.0714/ea | 12 (of 120 pk) | $0.07 | $0.86 |
| [LVDALAB PTFE Membrane Filter, ø13 mm × 0.45 µm, 100 pc, non-sterile](https://www.amazon.com/dp/B0D41KT345) | hydrophobic PTFE membrane in the reservoir-cap vent pocket; architecture + sizing in [`printed-parts/cold-core/reservoir/vent.md`](printed-parts/cold-core/reservoir/vent.md); 2 per build (1 per cap × 2 caps); Amazon 112-4393734 May 11: $12.99 − $0.65 promo + $0.89 tax = $13.23 ÷ 100 = $0.1323/ea | 2 (of 100 pk) | $0.13 | $0.26 |

## 14. Install kit (per-appliance install-kit tools)

Per-appliance tools that ship in the install kit so the field installer can cut the 3-tube umbilical bundle to length and push each tube into its rear-panel PTC bulkhead. Each entry is a tool the installer uses once during install and keeps with the appliance (or returns to the kit) — not consumed into the fluid path, not a fab-shop tool. Future additions expected: printed stubby wrench for the compression nut, foam knife.

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Mudder 3 Pieces PTFE Plastic Tubing Cutter, OD up to 3/4", polyacetal body + 304 SS replaceable blade](https://www.amazon.com/dp/B08VW15TK8) | installer trims the 3-tube umbilical bundle to length at field install before pushing tubes into rear-panel PTC bulkheads; OD range 1/8"–3/4" covers the 1/4" OD LLDPE umbilical easily. 3-pack = 1 cutter per install × 3 installs per pack. Amazon 112-8598924 May 17: $11.99 + $0.87 tax = $12.86 ÷ 3 = $4.29/ea | 1 (of 3 pk) | $4.29 | $4.29 |

## Totals

| Section | $ |
|---|---:|
| 1. Controllers + electronics | $166.43 |
| 2. Carbonator vessel (plan A, 316L) | $240.69 |
| 3. Water inlet | $201.16 |
| 4. CO2 subsystem | $92.61 |
| 5. Refrigeration | $196.70 |
| 6. Cold core insulation | $52.38 |
| 7. Printed parts (PETG) | $103.94 |
| 8. Flavor subsystem | $285.18 |
| 9. Dispensing | $50.68 |
| 10. UI | $43.16 |
| 11. Wiring | $31.97 |
| 12. Level sensing | $69.78 |
| 13. Mechanical attach hardware + reservoir-cap vent filter | $17.55 |
| 14. Install kit | $4.29 |
| **Total** | **$1,556.52** |

## External / user-supplied (not shipped)

- **5 lb CO2 tank** + refills (~$25/refill at welding/homebrew shops)
- **Flavor concentrate** — SodaStream or BIB syrup
- **Tap-water source under the cabinet** — an existing 3/8" or 1/2" angle-stop on a cold-water line (the same prerequisite a dishwasher or under-counter water filter has). The kit includes the tee, the 1/4" LLDPE, and the water filter — the customer brings only the existing angle stop.