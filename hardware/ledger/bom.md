# Bill of Materials — One Consumer Unit

Per-unit parts for a single finished appliance built on the **custom-vessel** path specified in [future.md](/hardware/future.md). Carbonator vessel: vertical 5" OD × 0.065" wall 316 welded SS round tube (OnlineMetals #12498, MTRs required) capped with 1/4"-thick laser-cut 316 SS circular plates from SendCutSend (`endcap-circular-2hole.dxf`), joined with the XLaserlab X1 Pro handheld laser welder. 1/4" NPT is direct-tapped into the plates (no weld-in bungs). Compressor is harvested from a countertop ice-maker; cold core is 3D-printed shells with pour-in-place foam. Flavor reservoirs are custom printed food-grade PETG hard reservoirs ([printed-parts/cold-core/reservoir/reservoir.py](/hardware/printed-parts/cold-core/reservoir/reservoir.py)), two per build.

Tools, fabrication equipment (welder, slip roll, shop press, dishing dies), and duplicate SKUs live in [purchases.md](/hardware/ledger/purchases.md) only. Per-build consumables — anything used up making one unit, regardless of whether it ships in the product (mixing cups, gloves, citric acid, PTFE tape, cutting fluid, etc.) — live in this file with the rest of the per-unit parts.

First-pass draft. **Pricing convention: delivered cost** (product + shipping + tax) drawn from resolved order history in [purchases.md](/hardware/ledger/purchases.md) wherever the SKU has been ordered or acquired; list price for forward-plan SKUs not yet purchased. Pack-amortized lines show the math in the description (e.g., `$31.08/2`). Expect revisions.

## 1. Controllers + electronics

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | Main controller; its onboard AMS1117 supplies the 3.3 V I²C rail on the 3V3 pin | 1 | $11.00 | $11.00 |
| [ESP32 DIN Rail Breakout Board](https://www.amazon.com/dp/B0BW4SJ5X2) | | 1 | $25.99 | $25.99 |
| [Waveshare ESP32-S3-Touch-LCD-4.3B](https://www.amazon.com/dp/B0D925SBYF) | Enclosure-front config + interaction display: flavor-image/ratio tuning, clean cycles, pump priming, factory reset, screensaver, and the BLE bridge to the iOS app. 4.3" 800×480 IPS RGB capacitive touch (ST7262 RGB + GT911 touch via CH422G I/O expander), ESP32-S3-WROOM-1-N16R8 (Wi-Fi/BLE 5, 16 MB flash / 8 MB PSRAM); 7–36 V screw-terminal input off the 12 V bus. Flavor display + flavor toggle live on the faucet touch LCD (below). Order #112-5620567-3321809 Jun 13: $42.99 + $3.12 tax = $46.11 | 1 | $46.11 | $46.11 |
| [Waveshare ESP32-S3 1.47" Touch LCD, 172×320 (B0FCF1MGT3)](https://www.amazon.com/dp/B0FCF1MGT3) | **Faucet flavor display + touch toggle.** 1.47" IPS capacitive touch (JD9853 driver + AXS5106L touch chip), ESP32-S3R8 (Wi-Fi/BLE 5). Shows the selected flavor and switches flavor by touch — no separate physical button, replacing the prototype RP2040 round display. Mounts on the gooseneck dispense head; its ESP32-S3 talks to the base ESP32 over UART. Order #112-7687617-6094631 Jun 7: 2 @ $23.99 + $3.48 tax = $51.46 ÷ 2 = $25.73/ea | 1 | $25.73 | $25.73 |
| [ALMOCN TTL-to-RS485 module (5-pk)](https://www.amazon.com/dp/B09998FY4X) | RS485 transceiver on the base ESP32 for the link to the 4.3B config display; auto-direction (no DE/RE pin), 3.0–30 V supply, screw-terminal RS485 + JST TTL. 1 of 5 per unit. Order #112-8498962-9414661 Jun 13: $12.58 + $0.91 tax = $13.49 ÷ 5 = $2.70/ea | 1 (of 5 pk) | $2.70 | $2.70 |
| [L298N Dual H-Bridge (4-pack)](https://www.amazon.com/dp/B0C5JCF5RS) | 1 driver per unit drives both peristaltic pumps (dual H-bridge); its onboard 7805/78M05 supplies the 5 V logic rail to the MCUs and relay VCC; 1 of 4 per unit ($10.71/4) | 1 (of 4 pk) | $2.68 | $2.68 |
| [Waveshare MCP23017 I2C GPIO expander](https://www.amazon.com/dp/B07P2H1NZG) | expands ESP32 I2C into 16 GPIO for solenoid bank | 1 | $12.99 | $12.99 |
| [DORHEA DS3231 AT24C32 RTC module (2-pk)](https://www.amazon.com/dp/B09LLMYBM1) | I2C RTC at 0x68, referenced in `wiring/esp32-pinout.mmd` and `wiring/valve-control.mmd`; I²C pins broken out as a single inline VCC/GND/SDA/SCL row for a clean 4-pin XH; 1 of 2 per unit ($7.07/2) | 1 (of 2 pk) | $3.54 | $3.54 |
| [EDGELEC 4.7 kΩ 1/4 W 1% metal-film resistor (100-pk)](https://www.amazon.com/dp/B07HDFHPP3) | DS18B20 1-wire bus pull-up between DATA and 3.3 V; 1 of 100 per unit ($5.89/100) | 1 (of 100 pk) | $0.06 | $0.06 |
| [Chanzon 2.2 kΩ 1/4 W 1% metal-film resistor (100-pk)](https://www.amazon.com/dp/B08QRPRVMJ) | MQ-6 gas-sensor output divider, top leg (carrier R1/R3 in [`pcb/carrier/mini.tsx`](/hardware/pcb/carrier/mini.tsx)): the MQ-6 runs on 5 V so its AOUT/DOUT swing 0–5 V; a 2.2 kΩ/3.3 kΩ divider on each steps them to ~3.0 V before ESP32 GPIO 39/36, which are NOT 5 V tolerant. 2 of 100 per unit ($5.49/100) | 2 (of 100 pk) | $0.05 | $0.11 |
| [Chanzon 3.3 kΩ 1/4 W 1% metal-film resistor (100-pk)](https://www.amazon.com/dp/B08QRG7JBY) | MQ-6 gas-sensor output divider, bottom leg (carrier R2/R4): pairs with the 2.2 kΩ top leg on each MQ-6 output (AOUT→IO39, DOUT→IO36) to step 0–5 V down to ~3.0 V. 2 of 100 per unit ($5.49/100) | 2 (of 100 pk) | $0.05 | $0.11 |
| [Rubycon 470 µF 25 V low-ESR radial electrolytic capacitor, 10×12.5 mm (15-pk)](https://www.amazon.com/dp/B0F8BZVBKF) | bulk (low-frequency) decoupling on the 12 V solenoid rail; soldered across an ULN2803A driver module's COM (12 V) → GND pins at build — the carrier V12 island has no room for a 10 mm radial. Pairs with the on-carrier 0.1 µF HF ceramics (C1/C2 below); 1 of 15 per unit ($7.40/15) | 1 (of 15 pk) | $0.49 | $0.49 |
| [Chanzon 0.1 µF 50 V ceramic disc capacitor, 2.54 mm lead pitch (100-pk)](https://www.amazon.com/dp/B07PTNB3CR) | high-frequency V12-rail decoupling — carrier C1/C2 ([`pcb/carrier/mini.tsx`](/hardware/pcb/carrier/mini.tsx)), one through-hole 0.1 µF in each open pocket of the V12 island, near each ULN, snubbing the fast solenoid-turn-off edge the bulk electrolytic can't. pin1→V12 pour, pin2→GND plane. 2 of 100 per unit | 2 (of 100 pk) | $0.02 | $0.04 |
| [ULN2803A high-current driver module (2-pc)](https://www.amazon.com/dp/B0F872W528) | 2 modules drive 12 solenoids from MCP23017 outputs; 1 full 2-pack per unit | 1 pk | $6.59 | $6.59 |
| [Mean Well IRM-90-12ST, 80 W / 12 V / 6.7 A, encapsulated](https://www.amazon.com/dp/B0CNRST18V) | 12 V supply for the low-voltage bus; IEC 60335-1 household-appliance safety listed | 1 | $31.66 | $31.66 |

## 2. Carbonator vessel (custom fabrication — plan A: round tube + 1/4" plates, 316L)

An earlier racetrack-body alternative (304 SS body half-sheets + dished racetrack end caps + 4× weld bungs) is no longer in active development; its parts inventory remains tracked in [purchases.md](/hardware/ledger/purchases.md) §1, and the artifacts are preserved at the `archive-plan-b` git tag, in case the round-tube path is ever blocked.

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| OnlineMetals #12498 — 5" OD × 0.065" wall 316 welded SS round tube | cut to 6.0" length (MTRs required); OnlineMetals #1020857414 Apr 24: 10 @ $67.35 + ship + tax = $736.73 ÷ 10 = $73.67/ea | 1 | $73.67 | $73.67 |
| SendCutSend 1/4"-thick 316 SS circular endcap plate (`endcap-circular-2hole.dxf`) | 4.860" diameter with 2× 7/16" tap-pilot holes for 1/4" NPT; SCS SG019619 Apr 24: 20 @ $28.96 + tax = $621.19 ÷ 20 = $31.06/ea; [2](END_CAPS) plates per vessel | 2 | $31.06 | $62.12 |
| [LTWFITTING 1/4" hose barb × 1/4" MNPT, 316 SS (5-pk)](https://www.amazon.com/dp/B017N4TTMA) | port 1 (CO2 in via internal sparge); threads into bottom plate, barb faces inward to silicone tube → sparge stone; 1 of 5 per unit ($13.65/5) | 1 (of 5 pk) | $2.73 | $2.73 |
| [TAISHER 2PCS 316L SS 90° Barstock Street Elbow, 1/4" NPT M × 1/4" NPT F](https://www.amazon.com/dp/B0CZ38MYL1) | all four vessel-port elbows (water inlet + carbonated-water outlet + CO2 inlet + PRV port); design rationale in [`assembly/pressure-vessel.md`](/hardware/assembly/pressure-vessel.md). [4](VESSEL_PORTS) elbows per build = 2 packs/build. Amazon 112-6323725 May 13: $20.99 + $1.52 tax = $22.51 ($11.26/ea × 4 = $45.04) | 4 (2 pk) | $11.26 | $45.04 |
| [FERRODAY 0.5 µm sintered 316 SS sparge stone, 1/4" barb input (2-set)](https://www.amazon.com/dp/B091C5Y6L9) | internal sparge stone, hangs in water column on silicone tube from port-1 barb adapter; 1 of 2 per unit ($14.97/2) | 1 (of 2) | $7.49 | $7.49 |
| Food-grade silicone tube stub, 1/4" ID × ~3" long (cut from existing Metaland 1/4" silicone B08L1ST6ST stock in §5) | connects port-1 barb to sparge stone inside vessel | — | ~$0.20 | $0.20 |
| [Millrose 70894 Nickel Guard anti-seize PTFE tape](https://www.amazon.com/dp/B07C9ZV4PG) | anti-seize for SS-into-SS NPT joints ([4](VESSEL_PORTS) ports per unit) | 1 | $20.07 | $20.07 |
| [Tap Magic EP-Xtra pipe-tap cutting fluid, 16 oz (size variant on listing B00DHMHSGM)](https://www.amazon.com/dp/B00DHMHSGM) | required for hand-tapping 1/4" NPT into 1/4"-thick 316 SS plate; ~$0.50 of fluid per vessel | 1 | $0.50 | $0.50 |
| [Control Devices SV-125 safety valve, 1/4" NPT, 125 psi set pressure, 49 SCFM relief, brass](https://www.amazon.com/dp/B01G2F6EMY) | Port 4 tank PRV (top plate, dedicated); sizing rationale in [`assembly/pressure-vessel.md`](/hardware/assembly/pressure-vessel.md). Amazon 112-6323725 May 13: $7.49 + $0.54 tax = $8.03 | 1 | $8.03 | $8.03 |
| [Cambro 6 QT polycarbonate square container](https://www.amazon.com/dp/B001BZEQ44) | citric acid passivation soak tub, one-time-use per unit | 1 | $20.00 | $20.00 |
| [Viva Doria food-grade citric acid, 2 lb bag](https://www.amazon.com/dp/B0C5NQM8S1) | passivation: ~1 qt of 4% solution per tank; 1/20 of $9.99 bag | 1 | $0.50 | $0.50 |
| [STARTECHWELD ER316L .030 MIG wire, 10-lb spool](https://www.amazon.com/dp/B09BKFBXT9) | filler for the plate-to-tube and float-rod-to-plate laser welds; filler-alloy rationale in [`assembly/pressure-vessel.md`](/hardware/assembly/pressure-vessel.md); ~12 g of wire per ~32" of weld per vessel × ~378 builds per 10-lb spool; $129.50/378 | 1 (of 378) | $0.34 | $0.34 |

## 3. Water inlet (tap → filter → backflow → pump → top-plate port)

The appliance ships with the water filter included. **Placement (internal vs. external to the enclosure) is TBD** — internal puts the cartridge behind the rear panel (customer-replaceable on a service interval), external lets the customer mount it inline upstream of the rear-panel inlet (familiar fridge-line install pattern). Either way it is in the box, sized to the customer's 1/4" OD line, and on our side of "the kit includes everything you need."

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Waterdrop 15UC-UF 0.01 µm inline water filter, 1/4" QC both ends](https://www.amazon.com/dp/B085G9TZ4L) | Upstream water filter; 1/4" QC fittings on both ends drop straight into the customer-side 1/4" LLDPE run. Same SKU already in `purchases.md §3` (ACQUIRED). Placement internal-vs-external to the enclosure is TBD per the section header above. | 1 | $62.99 | $62.99 |
| [Multiplex 19-0897 ASSE 1022 backflow preventer](https://www.midwestbev.com/products/asse-1022-backflow-preventer) | midwestbev MB11053 Apr 24: 4 @ $29.33 = $117.32 + $28.48 ship = $145.80 ÷ 4 = $36.45/ea | 1 | $36.45 | $36.45 |
| [brewhardware FFL38BARB38 swivel flare adapter, 3/8" FFL × 3/8" OD SS hose barb](https://www.brewhardware.com/product_p/ffl38barb38.htm) | single-piece adapter on the Multiplex 19-0897 MFL outlet; 304 SS wetted barb, chrome-plated brass swivel nut never touches water; brewhardware #156209 May 16: 5 @ $4.99 = $24.95 + $14.47 ship = $39.42 ÷ 5 = $7.88/ea | 1 (of 5 pk) | $7.88 | $7.88 |
| [JoyTube 3/8" ID × 1/2" OD food-grade silicone tubing, 10 ft](https://www.amazon.com/dp/B089YGDB55) | 3/8" ID food-grade silicone hose, ~12" per build between the brewhardware FFL38BARB38 hose-barb adapter (Multiplex 19-0897 MFL outlet side) and the SeaFlo 22-Series pump's 3/8" hose-barb inlet; covers the entire suction-side hose run with no diameter step-down. JoyTube ACQUIRED per `purchases.md:140`: $11.99 + $0.87 tax = $12.86 ÷ 10 builds = $1.286/build (10 ft × ~12"/build) | 1/10 roll (~12") | $1.29 | $1.29 |
| [Sealproof 1/4" ID × 3/8" OD clear PVC, 10 ft](https://www.amazon.com/dp/B07D9DK94V) (vent telltale) | | 1 | $8.46 | $8.46 |
| [Shutao 6-pc water sensor module, LM393, 3.3–5 V](https://www.amazon.com/dp/B0B2W76MB1) | Backflow drip-pan telltale: the Multiplex 19-0897 vent weeps to the internal drip pan; this module's flat conductivity plate sits in the pan and water bridging it trips the LM393 (a wet pan flags cross-contamination). Run VCC at **3.3 V** (J4.3V3) so DO is ESP-safe; DO is active-low when wet → ESP32 GPIO 13 (SIG-9) per [`wiring/esp32-pinout.mmd`](/hardware/wiring/esp32-pinout.mmd); "drip pan dry" is a required check in [`assembly/acceptance-and-burn-in.md`](/hardware/assembly/acceptance-and-burn-in.md). Bare electrodes electroplate under continuous DC, so firmware should pulse VCC only when sampling; the 6-pack gives spares. Order #112-2621523-2281840 Jun 25: $6.99 + $0.51 tax = $7.50 ÷ 6 = $1.25/ea. Amazon's Choice, Prime. | 1 (of 6 pk) | $1.25 | $1.25 |
| [LOKMAN 304 SS worm-gear clamps, 10–16 mm (20-pk)](https://www.amazon.com/dp/B076Q7QVNM) | vent line clamps; 4 of 20 per unit | 4 (of 20 pk) | $1.80 | $1.80 |
| [SEAFLO 22-Series 12V 1.3 GPM 100 psi diaphragm pump (3/8" hose-barb ports)](https://www.amazon.com/dp/B0166UBJX4) | | 1 | $48.25 | $48.25 |
| [MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4-pk)](https://www.amazon.com/dp/B0DMP77B6S) | adapts pump 3/8" hose-barb output to 1/4" NPT plumbing for the check valve and top-plate port; 1 of 4 per unit (also used in §8) | 1 (of 4 pk) | $3.24 | $3.24 |
| [GASHER 1/4" NPT SS one-way check valve (2-pk, $15.00)](https://www.amazon.com/dp/B0FV2D2FFX) | water-side check between SeaFlo pump and top-plate water-inlet port; PTFE-on-metal rationale in [`assembly/cold-core.md`](/hardware/assembly/cold-core.md) "Warm-side check valves"; 1 of 2 valves per unit (the other valve is the CO2-side check in §4) | 1 (of 2) | $7.50 | $7.50 |
| [John Guest PP010822E 1/4" OD × 1/4" NPT male connector, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-male-connector-nptf-black-polypropylene-1-4-x-1-4-nptf) | 1/4" NPT M × 1/4" PTC adapter pair (warm-side + cold-side of the +Z slot transition on the water-inlet path); 2 per build; FWS WEBFWS100675224 May 15: $11.00 + $5.23 ship + $1.18 tax = $17.41 ÷ 10 = $1.741/ea | 2 (of 10 pk) | $1.74 | $3.48 |
| [GAGIRA 316L SS reducing coupling, 3/8" NPT F × 1/4" NPT F (5-pk, incl. Teflon tape)](https://www.amazon.com/dp/B0G2XJGZMQ) | **Upstream adapter chain — closes the 1/4 JG QC → ASSE 1022 inlet gap.** Threads onto the PP010822E's 1/4" NPT M side (above) on the small end and onto the ASSE 1022's 3/8" MPT inlet (below) on the large end. **316L SS** — food-service gold standard, no lead concerns, matches the TAISHER 316L SS vessel-port elbows (§4) and the 316L pressure-vessel walls themselves (§2); strictly stricter than lead-free brass would have been. Includes Teflon tape (bonus — Millrose PTFE tape is the production tape per `assembly/internal-plumbing.md`). Amazon 114-6677442 May 22: 5 @ $16.99 + $1.23 tax = $18.22 ÷ 5 = $3.644/ea | 1 (of 5 pk) | $3.64 | $3.64 |
| [Basics MTB-0606WP White Barb Tee × Male Branch, 3/8" ID barb × 3/8" ID barb × 3/8" MNPT](https://www.freshwatersystems.com/search?q=MTB-0606WP) | Inline in the 3/8" ID silicone hose between FFL38BARB38 and SeaFlo pump inlet — tees off clean-cycle tap water to the flavor manifold V-A inlet. Both 3/8" barb legs clamped with LOKMAN worm-gear clamps. FWS swapped this in for the discontinued MTB-0604WP on order WEBFWS100677768, shipped Jun 10 2026 (UPS 1ZW0062A0297032825, 10× itemized). 3/8" MNPT branch is adapted to 1/4" OD PTC by the JG PP451223W + PP061208W chain (two rows below; ordered WEBFWS100682118) — NOT the PP450822E, which is 1/4" NPTF. FWS list $1.09/ea but credited the $0.60 upcharge, net $10.30/10 = $1.03/ea × 1.3995 overhead = $1.44/ea | 1 (of 10) | $1.44 | $1.44 |
| [John Guest PP451223W Female Adapter NPTF Polypro, 3/8" NPTF × 3/8" OD PTC](https://www.freshwatersystems.com/products/john-guest-female-adapter-nptf-polypro-3-8-x-3-8-nptf) | **Tap-point branch adapter, 1 of 2.** 3/8" NPTF female threads onto the MTB-0606WP tee's 3/8" MNPT branch (above); 3/8" OD PTC accepts the PP061208W reducer stem (below). White PP, food-grade EPDM O-ring, lead-free, NSF 51 + 61, 150 psi @ 70°F. FWS WEBFWS100682118 Jun 10: $46.14/10 × 1.2998 overhead = $6.00/ea | 1 (of 10 pk) | $6.00 | $6.00 |
| [John Guest PP061208W Reducer Stem Polypro, 3/8" OD stem × 1/4" OD PTC](https://www.freshwatersystems.com/products/john-guest-reducer-stem-polypro-3-8-od-stem-x-1-4) | **Tap-point branch adapter, 2 of 2.** 3/8" OD stem plugs into the PP451223W's 3/8" PTC (above); 1/4" OD PTC accepts the 1/4" LLDPE run to the flow regulator → V-A. White PP, food-grade EPDM O-ring, lead-free, NSF, 150 psi @ 70°F. FWS WEBFWS100682118 Jun 10: $16.44/10 × 1.2998 overhead = $2.14/ea | 1 (of 10 pk) | $2.14 | $2.14 |
| [John Guest PP450822E Female Adapter NPTF Black Polypropylene, 1/4" OD PTC × 1/4" NPTF](https://www.freshwatersystems.com/products/john-guest-female-adapter-nptf-black-polypropylene-1-4-x-1-4-nptf) | General 1/4"-NPT × 1/4"-PTC stock. Originally the tap-point branch adapter for the 1/4"-MNPT MTB-0604WP; the MTB-0606WP swap (3/8" MNPT branch, row above) doesn't take it, so the 10 shipping on WEBFWS100677768 reassign to general use. Black PP, EPDM O-ring, NSF 51 + 61, 150 psi @ 70°F. FWS WEBFWS100677768 May 25: $34.06/10 × 1.3995 overhead = $4.77/ea | 1 (of 10 pk) | $4.77 | $4.77 |
| [neoFit acetal black flow-control bulkhead, 1/4" tube (ABCVU44-E)](https://www.freshwatersystems.com/products/neofit-acetal-black-flow-control-bulkhead-1-4-tube) | **Flow regulator on the V-A clean-water feed** — the "flow regulator → V-A" node in the PP450822E row above and in [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md) (tube segment 1). Adjustable flow-control valve in bulkhead form; the screw throttles the clean/tap-water feed down so the flavor manifold runs at its low (<10 PSI) working pressure (`docs/plumbing.md` "Why a Needle Valve Instead of a Pressure Regulator"). Push-connect 1/4", acetal + food-grade EPDM, NSF 51/61, FDA, 150 psi @ 68°F, black. FWS: $4.39 single / $4.34 per 10. | 1 | $4.39 | $4.39 |
| [Lifevant 1/4" OD water tubing 32.8 ft + quick-connects](https://www.amazon.com/dp/B0DKCZ5W66) | water-inlet tubing (filter → pump → vessel) ~8–10 ft + ~5 of 12 quick-connects per unit; ~1/3 of pack. Generic Amazon PE listing with no third-party food cert (vendor doesn't list one) — short-term use without certification | 1 (~1/3 pk) | $3.33 | $3.33 |
| [John Guest 1/4" OD × 1/8" NPT push-fit](https://www.amazon.com/dp/B07V6XKZG9) | | 1 | $5.00 | $5.00 |
| [John Guest PI1208S acetal bulkhead union, 1/4" QC × 1/4" QC](https://www.amazon.com/dp/B0C1F3QR7N) | **Rear-panel customer-facing water inlet.** The customer plugs the install-kit 1/4" LLDPE into this bulkhead — push-to-connect, no tools. 1/4" QC on both sides (interior side feeds into the in-cabinet run → Waterdrop filter → PP010822E → GAGIRA 316L SS coupling → ASSE 1022 3/8" MPT inlet). NSF cert upgrade path: PP1208E food-cert family already in BOM §8 for the umbilical cluster is the obvious swap when the panel goes to CAD. | 1 | $11.49 | $11.49 |
| [HAOCHEN brass angle-stop add-a-tee, 3/8" × 3/8" × 1/4"](https://www.amazon.com/dp/B0DLKHHGL6) | **Install-kit tee, scenario B (older home).** Threads between the customer's existing 3/8" angle stop and its current compression supply line, exposing a 1/4" compression outlet for the appliance. Wrench install. Already ACQUIRED on the prototype per `purchases.md §3` and `inventory.md`. | 1 | $11.99 | $11.99 |
| [John Guest PP0208E 1/4" × 1/4" × 1/4" union tee, black polypropylene (bag of 10)](https://www.freshwatersystems.com/products/john-guest-union-tee-black-polypropylene-1-4) | **Install-kit tee, scenario A (modern home).** Drops inline into an existing 1/4" LLDPE under-sink line (push-to-connect, no tools) — the configuration shipped in any kitchen new since the late 2010s or any kitchen with a PEX manifold + ice-maker / RO / drinking-water stub-out. **Black PP, NSF 51 + 61, FDA-compliant materials** — same JG black-PP food-cert family as the §3 PP010822E, §4 PP0308E, §8 PP1208E, and §8 PP2308E already in the BOM. FWS WEBFWS100677333 May 22: 1 bag of 10 @ $21.34 + allocated 20.35% overhead = $25.68/bag = $2.57/each × 1/build; bag of 10 = 10 builds of stock | 1 (of 10 pk) | $2.57 | $2.57 |
| [John Guest Blue 1/4" OD LLDPE Polyethylene Tubing, 100 ft](https://www.freshwatersystems.com/products/blue-1-4-od-lldpe-polyethylene-tubing) | **Carbonated-water umbilical riser tube** — color-coded blue to match the blue accent ring on the rear-panel PP1208E bulkhead per [`printed-parts/enclosure/back-panel/README.md`](/hardware/printed-parts/enclosure/back-panel/README.md) "Umbilical port — tube identification". Runs from the cold-core bottom-plate outlet up through the cabinet, through the rear-panel bulkhead, up the under-counter umbilical, to the faucet. ~5 ft per build (cabinet-routing-length-dependent). Same neoFlo LLDPE family + NSF 51 + FDA compliance as the existing black LLDPE roll. FWS WEBFWS100677333 May 22: $14.19 + allocated 20.35% overhead = $17.08 ÷ 100 ft = $0.171/ft × 5 ft = $0.86/build; 100 ft = ~20 builds of stock | ~5 ft (of 100 ft) | $0.17 | $0.86 |

## 4. CO2 subsystem

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Wellbom dual-gauge CO2 regulator, CGA-320, 0–120 PSI out / 150 PSI PRV](https://www.amazon.com/dp/B0G13P5PMY) | | 1 | $44.99 | $44.99 |
| [Interstate Pneumatics WR1110 1/4" NPT in-line 90 PSI fixed pre-set pressure regulator, 230 PSI max inlet, aluminum body](https://www.amazon.com/dp/B07J2L8LF3) | in-appliance secondary regulator between the customer's CGA-320 primary regulator (above) and the vessel CO2 inlet; setpoint rationale in [`assembly/pressure-vessel.md`](/hardware/assembly/pressure-vessel.md) "CO2 supply". Amazon 112-6323725 May 13: $23.93 + $1.73 tax = $25.66 | 1 | $25.66 | $25.66 |
| [Colder 74600 NSF Valved Coupling Body, 1/4" MNPT — CO2 quick-disconnect socket (appliance side)](https://www.freshwatersystems.com/products/74600-nsf-valved-coupling-body-1-4-npt) | **Rear-panel CO2 inlet — appliance half of the quick-disconnect pair.** Threads directly into the WR1110 secondary regulator's 1/4" FNPT inlet. Double shut-off (both halves seal closed when disconnected) — closes the catastrophic-vent failure mode where the customer opens the cylinder valve before the hose is seated. **NSF-listed**, chrome-plated brass body, 316 SS valve spring, Buna-N seal, 250 PSI, Vacuum-to-17.3-bar range. NSF version of the LCD10004 (auto-upgrade target at FWS when LCD10004 is out of stock). FWS WEBFWS100677333 May 22: 2 @ $18.10 = $36.20 + allocated 20.35% overhead = $43.57 ÷ 2 = $21.78/ea × 1/build; 2 units of stock | 1 (of 2) | $21.78 | $21.78 |
| [Colder 70500 NSF Valved In-Line Hose Barb Coupling Insert, 1/4" ID barb — CO2 quick-disconnect plug (hose side)](https://www.freshwatersystems.com/products/70500-nsf-valved-in-line-hose-barb-coupling-insert-1-4-id-barb) | **Customer-facing CO2 hose plug — hose half of the quick-disconnect pair.** Factory-installed on the customer-facing end of the CO2 supply hose; slides onto 1/4" ID hose with a clamp, no NPT-to-barb adapter required on the customer side. Mates with 74600 above to form the rear-panel CO2 quick-disconnect. Same chrome brass / 316 SS valve spring / Buna-N seal / 250 PSI as the socket; **NSF-listed** (alt part # 40CBV-PB2-04). NSF version of the LCD22004. FWS WEBFWS100677333 May 22: 2 @ $18.33 = $36.66 + allocated 20.35% overhead = $44.13 ÷ 2 = $22.06/ea × 1/build; 2 units of stock | 1 (of 2) | $22.06 | $22.06 |
| [John Guest PP010822E 1/4" OD × 1/4" NPT male connector, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-male-connector-nptf-black-polypropylene-1-4-x-1-4-nptf) | 1/4" NPT M × 1/4" PTC adapter pair (WR1110 outlet + TAISHER vessel-port elbow on the CO2-inlet path); 2 per build; FWS WEBFWS100675224 May 15: $11.00 + $5.23 ship + $1.18 tax = $17.41 ÷ 10 = $1.741/ea | 2 (of 10 pk) | $1.74 | $3.48 |
| [John Guest PP0308E 1/4" OD union elbow, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-union-elbow-black-polypropylene-1-4) | 90° PTC × PTC union elbow. Three uses per build: **(1)** the in-cavity 90° bend in the CO2 path inside the foam shell per [foam-shell/README.md](/hardware/printed-parts/cold-core/foam-shell/README.md) — 2; **(2)** one on the outer (unoccupied) port of every [valve-manifold](/hardware/printed-parts/valve-manifold/) valve, turning each line +Z up out of its tray — source-select 4 + bag-circuit 4 + bib-gate 2 + nozzle-gate 2 = 12; **(3)** two on each Kamoer KPHM400 [pump assembly](/hardware/reference/kamoer-kphm400/pump_assembly.py) outlet pair × 2 pumps = 4. 2 + 12 + 4 = 18/build. FWS WEBFWS100684731 Jun 20: $50.61 + $13.25 ship + $4.63 tax = $68.49 ÷ 30 = $2.283/ea (3 bags of 10) | 18 (2 bags of 10) | $2.28 | $41.09 |
| [5/16" ID beer CO2 line, 10 ft + 4 clamps](https://www.amazon.com/dp/B0D1RB3TF6) | ~12 in short tether (customer's CGA-320 regulator → front-panel inlet) + 2 of 4 clamps per unit; ~1/4 of pack value | 1 (~1/4 pk) | $3.50 | $3.50 |
| [DERPIPE 5/16" tube × 1/4" NPT push-to-connect (5-pk)](https://www.amazon.com/dp/B09LXVGPG7) | CO2 line entry to vessel; 1 of 5 per unit ($10.71/5). **5/16" variant appears delisted; source replacement ASIN** | 1 (of 5 pk) | $2.14 | $2.14 |
| [GASHER 1/4" NPT SS one-way check valve (2-pk, $15.00) — second of pack](https://www.amazon.com/dp/B0FV2D2FFX) | CO2-side check between DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the LTWFITTING bottom-plate barb adapter; rationale in [`assembly/cold-core.md`](/hardware/assembly/cold-core.md) "Warm-side check valves". Same 2-pack as the §3 water-side check, second valve of the pair | 1 (of 2) | $7.50 | $7.50 |

## 5. Refrigeration (harvested compressor path)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Frigidaire EFIC117-SS ice-maker donor (compressor/condenser/cap-tube/drier)](https://www.amazon.com/dp/B07PCZKG94) | | 1 | $78.70 | $78.70 |
| [GOORY 1/4" OD × 50 ft ACR copper coil (evaporator)](https://www.amazon.com/dp/B0DKSW5VL9) | single-layer wrap on 5" OD vessel at 1/8" gap pitch yields ~22 ft of wrap per unit + ~2 ft each end for compressor + suction-line tie-ins ≈ ~24 ft consumed per unit; one 50 ft roll comfortably covers 2 units, so 1/2 roll allocated per unit ($68.63/2) | 1/2 roll | $34.32 | $34.32 |
| [Supco SUD8358 filter-drier, 1/4" sweat × cap-tube outlet, XH-9 molecular sieve, integrated Schrader access port](https://www.amazon.com/dp/B009AX2O5W) | replacement filter-drier installed during refrigerant-loop assembly; spec rationale in [`assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) Inputs | 1 | $13.40 | $13.40 |
| [Teyleten 3.3 V relay module, opto-isolated, 10 A @ 250 VAC (5-pk)](https://www.amazon.com/dp/B07XGZSYJV) | two relays per unit: relay #1 switches the compressor's 120 VAC hot leg (ESP32 GPIO 17), relay #2 gates 12 V to the SeaFlo diaphragm pump for firmware-controlled refill (ESP32 GPIO 16); 2 of 5 per unit | 2 (of 5 pk) | $2.60 | $5.20 |
| [HiLetgo DS18B20 waterproof 1-wire probe, 1 m SS sheath (5-pk)](https://www.amazon.com/dp/B00M1PM55K) | 2 probes per unit: tank wall (compressor cycling setpoint) + evaporator coil (freeze-protect cutout); 2 of 5 per unit ($11.79/5 × 2) | 2 (of 5 pk) | $2.36 | $4.72 |
| [MXR IEC 60320 C14 panel-mount AC inlet, 10 A / 250 VAC (10-pk)](https://www.amazon.com/dp/B07DCXKNXQ) | rear-panel mains inlet; accepts standard NEMA 5-15P-to-C13 line cord; 1 of 10 per unit ($6.96/10) | 1 (of 10 pk) | $0.70 | $0.70 |
| [Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed (6-pk)](https://www.amazon.com/dp/B08VS8D4WC) | ships in the box so the customer can plug the appliance into a standard US wall outlet; 1 of 6 per unit ($24.00/6) | 1 (of 6 pk) | $4.00 | $4.00 |
| [Enviro-Safe R-600a 3-pack + brass charging gauge](https://www.amazon.com/dp/B0CGG1WH1N) | pure R-600a; refills the sealed loop after venting factory charge; ~40 g per system × ~12 recharges per 3-can bundle; 1/12 of $72.92 delivered; brass gauge stays with tools (see purchases.md) | 1 | $6.08 | $6.08 |
| [Supco BPV31 bullet-piercing valve](https://www.amazon.com/dp/B00DM8J3MI) | taps the compressor process tube to vent the factory R-600a charge before brazing in the replacement drier; left clamped on the cut stub after teardown; single-use per build | 1 | $7.37 | $7.37 |
| [BCuP-5 15% Ag silver brazing alloy, 1/16" × 1 troy oz rod](https://www.amazon.com/dp/B0DQ3ZMHK7) | filler for copper-to-copper refrigeration joints; ~10 g per build × ~3 builds per 31 g rod; $18.99/3 | 1 (of 3) | $6.33 | $6.33 |
| [3M Scotch-Brite Maroon General Purpose Hand Pads, 6" × 9" (1-pack of 20)](https://www.amazon.com/dp/B07CGPCTHT) | abrasive pads cut into strips to clean 1/4" ACR copper OD + fitting sockets before flux + braze on the 2–3 refrigeration-loop joints; 2 of 20 per build ($28.85/20 × 2) | 2 (of 20 pk) | $1.44 | $2.89 |
| SendCutSend compressor shroud (`cut-parts/compressor-shroud/`) | 0.059" G90 hot-dipped galvanized steel; 5-sided open-bottom box, interior 130 × 175 × 150 mm, 4 bends; design + rationale at [`cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md). SendCutSend quote 2026-06-03: $278.30 / qty 10 = $27.83/part. AC pass-through grommet listed separately below (Heyco SB-500-6) | 1 | $27.83 | $27.83 |
| [Heyco SB-500-6 (Heyco part #2053) black 6/6 nylon strain-relief snap bushing, 100-pack](https://www.amazon.com/HEYCO-2053-SB-500-6-Accessories/dp/B01LPBST9G/) | UL Recognized AC pass-through strain-relief bushing for the compressor-shroud 1/2" panel hole; sizing rationale in [`cut-parts/compressor-shroud/README.md`](/hardware/cut-parts/compressor-shroud/README.md) Penetrations; 100-pack = lifetime supply; per-build cost = $12.60 delivered / 100 | 1 (of 100 pk) | $0.13 | $0.13 |
| [BOJACK SF76E SEFUSE thermal fuse, 77 °C, 10 A / 250 V (10-pack)](https://www.amazon.com/dp/B07Y61YTTK) | hardware thermal cutoff in series with the compressor's AC hot leg inside the shroud; safety rationale in [`assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) "Safety". 1 of 10 per unit ($6.42/10) | 1 (of 10 pk) | $0.64 | $0.64 |
| [ACEIRMC MQ-6 LPG / iso-butane combustible gas sensor module (5-pack)](https://www.amazon.com/dp/B0978JSCZ8) | combustible-gas sensor mounted low on the rear interior enclosure wall (catches dense R-600a pooling at the cabinet floor); safety rationale in [`assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) "Safety". 1 of 5 per unit ($11.79/5) | 1 (of 5 pk) | $2.36 | $2.36 |

Fallback path (UL/ETL-retail-friendly): RIGID DV1910E sealed refrigeration module (~$600 + 20–30% import duty). Not selected for this BOM.

## 6. Cold core insulation

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Fiberglass Supply Depot 2 lb 2-part closed-cell pour-in-place PU foam, 1 qt kit](https://www.amazon.com/dp/B08R7TX8QJ) | 1.25 ft³ yield covers inner + outer shells with margin; Amazon 112-5359790 May 15: $39.99 + $2.90 tax = $42.89 | 1 kit | $42.89 | $42.89 |
| [3M 425 aluminum foil tape, 2" × 180 ft](https://www.amazon.com/dp/B07BTW7C2N) | thermally conductive aluminum foil bonding the evaporator coil to the vessel OD; applied during refrigerant-loop assembly step 4; one 180 ft roll covers ~12 builds at ~15 ft/build; 1/12 of $88.97 | 1 | $7.41 | $7.41 |
| [Pouring Masters 5 oz / 150 mL graduated mixing cups (50-pk)](https://www.amazon.com/dp/B08JHH1DBF) | foam-pour consumable; 4 cups per build for batching the 2-part PU foam in measured shots; $20.37/50 × 4 | 4 (of 50 pk) | $0.41 | $1.63 |
| [JMU 6" tongue depressors, individually wrapped (100-pk)](https://www.amazon.com/dp/B09H6ZP447) | foam-pour consumable; 4 stir sticks per build for hand-mixing 2-part PU foam in the graduated cups; $7.50/100 × 4 | 4 (of 100 pk) | $0.08 | $0.30 |
| [SUP powder-free 4 mil nitrile exam gloves, XL, 100-pk = 50 pairs](https://www.amazon.com/dp/B0G8SSMVKW) | foam-pour PPE; 1 pair per build (PU foam isocyanate component is a skin sensitizer); $7.49/50 pairs × 1 | 1 pair (of 50) | $0.15 | $0.15 |

## 7. Printed mechanical parts

Per-unit filament for every printed part shipped inside one finished appliance, one row per part. PETG throughout except the PET-CF (Polymaker Fiberon PET-CF17) faucet shell and mounting plate. `Mass (kg)` and `$` are per-line totals (quantity included). Masses are geometry-derived — CAD solid volume × density (PETG 1.27 g/cm³, PET-CF 1.30 g/cm³) — not slicer-measured. PETG $11.20/kg (Bambu PETG Basic, $224.04 ÷ 20 kg); PET-CF $39.32/kg (Polymaker Fiberon PET-CF17, $117.96 ÷ 3 kg).

| Part | Qty | Material | Mass (kg) | $ |
|---|---:|---|---:|---:|
| Cold-core inner shell (foam-shell) | 1 | PETG | 1.340 | $15.01 |
| Cold-core foam cap — top | 1 | PETG | 0.171 | $1.92 |
| Cold-core foam cap — bottom | 1 | PETG | 0.170 | $1.91 |
| Copper-plug stack (4 plugs) | 4 | PETG | 0.006 | $0.06 |
| PRV shroud | 1 | PETG | 0.008 | $0.09 |
| Flavor reservoir body — left | 1 | PETG | 0.398 | $4.46 |
| Flavor reservoir body — right | 1 | PETG | 0.398 | $4.46 |
| Flavor reservoir cap — left | 1 | PETG | 0.059 | $0.67 |
| Flavor reservoir cap — right | 1 | PETG | 0.059 | $0.67 |
| Controller tray | 1 | PETG | 0.031 | $0.35 |
| Driver tray | 1 | PETG | 0.025 | $0.28 |
| Power tray | 1 | PETG | 0.055 | $0.61 |
| Enclosure — front half | 1 | PETG | 0.852 | $9.54 |
| Enclosure — back half | 1 | PETG | 1.533 | $17.17 |
| Valve tray — source-select | 1 | PETG | 0.179 | $2.00 |
| Valve tray — bag-circuit | 1 | PETG | 0.133 | $1.49 |
| Valve tray — BiB-gate | 1 | PETG | 0.043 | $0.48 |
| Valve tray — nozzle-gate | 1 | PETG | 0.043 | $0.48 |
| Faucet touch-flo shell (3-piece: bottom + middle + top) | 1 | PET-CF | 0.151 | $5.94 |
| Faucet mounting plate | 1 | PET-CF | 0.013 | $0.51 |
| **Printed parts total** | | | **~5.66** | **[$68.10](BOM_SEC7)** |

By material: PETG ≈ 5.50 kg / $61.65, PET-CF ≈ 0.16 kg / $6.45.

Soft seals print in TPU from per-unit-trivial stock, not costed here: 2× foam-cap gasket, 2× reservoir gasket, 2× reservoir bulkhead dry washer, 2× reservoir vent retaining ring, 1× faucet mounting gasket, 1× faucet TPU o-ring. The hopper funnel is cast platinum-cure silicone (flavor subsystem). Printed tooling does not ship: the coil-winding mandrel, the foam-pour cap lids, the two-piece hopper-funnel silicone mold, and the single-valve cradle.

## 8. Flavor subsystem

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Kamoer KPHM400-SW3B25 12V peristaltic pump](https://www.amazon.com/dp/B09MS6C91D) | paid price per Feb 2026 Amazon 114-1015191 + 112-0545074 (Kamoer Fluid Tech Shanghai); current listing matches at $32.55. Pump-motor leads end in male spade tabs that the DC-5 harness lands on with crimped female faston receptacles (§11). | 2 | $32.55 | $65.10 |
| [Beduan 12V 1/4" solenoid valve (NC)](https://www.amazon.com/dp/B07NWCQJK9) | V-A/B/C/D/E/F/G/H/I/J/KA/KB per fluid-topology-manifold.mmd ([12](SOLENOIDS) per unit); lower-bound delivered single-unit cost (range $9.64–$19.28 across user's mixed orders) | [12](SOLENOIDS) | $9.64 | $115.68 |
| [John Guest PP1208E 1/4" OD black polypropylene push-to-connect bulkhead union (10-pk)](https://www.amazon.com/dp/B00JYFU8MM) | **Rear-panel umbilical port** — [3](PP1208E_PANEL) bulkheads on the enclosure back panel accepting the 3-tube under-cabinet-faucet umbilical (1 carbonated water + 2 flavors), one bulkhead marked with a blue accent ring to match the blue-color-coded carbonated-water tube per [printed-parts/enclosure/back-panel/README.md](/hardware/printed-parts/enclosure/back-panel/README.md). Black PP, NSF 51 + NSF 61, FDA-compliant materials, EPDM O-ring, 150 psi @ 70°F. Amazon 112-6407862 May 11: $23.11 + $1.68 tax = $24.79 ÷ 10 = $2.479/ea; 10-pk = ~3 builds of stock | [3](PP1208E_TOTAL) (of 10 pk) | $2.48 | $7.44 |
| [PureSec 1/4" RO push-to-connect 90° elbow bulkhead, white polypropylene (5-pk)](https://www.amazon.com/dp/B0968K4JRN) | **Reservoir-cap outlet port** — single-piece right-angle PTC bulkhead through the reservoir floor trough per [`printed-parts/cold-core/reservoir/floor-and-bulkhead.md`](/hardware/printed-parts/cold-core/reservoir/floor-and-bulkhead.md); the integral 90° elbow routes the syrup line laterally, so no separate union elbow is needed at the reservoir. White PP, water/RO/beverage-rated; ships without a panel o-ring — the panel seal is sourced separately (purchased silicone wet washer + printed TPU dry washer; see the silicone-washer row below). ⌀16 mm mounting hole. 1 per reservoir × [2](RESERVOIRS) = 2/build. Amazon B0968K4JRN: $10.99 ÷ 5 = $2.198/ea; 5-pk = 2.5 builds of stock | [2](RESERVOIRS) (of 5 pk) | $2.20 | $4.40 |
| [uxcell silicone flat washer, ⌀16 ID × ⌀24 OD × 3 mm, clear (10-pk)](https://www.amazon.com/dp/B07D23JJMR) | **Reservoir bulkhead wet-side face seal** — the primary seal where the PureSec barrel passes up through the reservoir floor; sits in the wet-side counterbore, compressed by the bulkhead hex nut, per [`printed-parts/cold-core/reservoir/floor-and-bulkhead.md`](/hardware/printed-parts/cold-core/reservoir/floor-and-bulkhead.md). Food-reasonable silicone (food-grade implied, not certified) — qualified by the wetted-surface screen, not a cert, per [`printed-parts/cold-core/reservoir/wetted-surface-test.md`](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md). The dry-side washer is printed TPU. 1 per reservoir × 2 reservoirs = 2/build. Amazon 112-8819640-4433810 Jun 7: $7.50 ÷ 10 = $0.75/ea; 10-pk = 5 builds of stock | 2 (of 10 pk) | $0.75 | $1.50 |
| [Supply Depot BIB connector, 3/8" red (2-pk)](https://www.amazon.com/dp/B0DMFK9B6P) | rear-panel commercial-syrup input | 1 pk | $19.99 | $19.99 |
| [MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4-pk)](https://www.amazon.com/dp/B0DMP77B6S) | | 1 pk | $12.97 | $12.97 |
| [John Guest PP010822E 1/4" OD × 1/4" NPT male connector, black polypropylene (10-pk)](https://www.freshwatersystems.com/products/john-guest-male-connector-nptf-black-polypropylene-1-4-x-1-4-nptf) | 1/4" NPT M × 1/4" PTC adapter pair (one per BiB-input leg, between MAACFLOW 3/8" barb × 1/4" NPT M and the LLDPE feeding the manifold junctions below); 2 per build; FWS WEBFWS100675224 May 15: $11.00 + $5.23 ship + $1.18 tax = $17.41 ÷ 10 = $1.741/ea | 2 (of 10 pk) | $1.74 | $3.48 |
| [John Guest PP2308E two-way divider, black polypropylene 1/4"](https://www.freshwatersystems.com/products/john-guest-two-way-divider-black-polypropylene-1-4) | source-select Y-A, Y-B per fluid-topology-trays.mmd (trident, parallel-outlet geometry), [2](Y_DIVIDERS) per unit; FWS WEBFWS100673541 May 9: 2 bags of 10 @ $61.66 = $30.83/bag = $3.083/ea pre-tax/ship; 1 bag = 5 builds of stock | [2](Y_DIVIDERS) (of 1 bag) | $3.083 | $6.17 |
| [John Guest PP0208E 1/4" union tee, black polypropylene (bag of 10)](https://www.freshwatersystems.com/products/john-guest-union-tee-black-polypropylene-1-4) | manifold Tees Y-C/D/E/F/G/H/KA/KB per fluid-topology-trays.mmd (run in-line between butted valves, branch rises to bag/pump/nozzle), [8](TEES) per unit; same JG black-PP NSF 51 + 61 family as the §3 install-kit tee. FWS WEBFWS100681220 Jun 8: 2 bags of 10 @ $42.68 = $21.34/bag = $2.134/ea pre-tax/ship | [8](TEES) (of 2 bags) | $2.134 | $17.07 |
| [Siptenk 1/4" OD brass tube stiffener insert (100-pk)](https://www.amazon.com/dp/B0FM77LLM1) | required on the LLDPE side of the carbonated-water tube end that lands in the Westbrass body's upstream compression port (per [`assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) step 2) so the brass ferrule does not crush the soft tube; 1 stiffener per build ($8.99/100) | 1 (of 100 pk) | $0.09 | $0.09 |
| [BBDINO 40A food-contact platinum silicone, 2.42 lb kit, 1:1](https://www.amazon.com/dp/B0FHHBGSQK) | **Cast silicone hopper funnel** (Zone C, [printed-parts/zone-c/](/hardware/printed-parts/zone-c/README.md)) — the removable, dishwasher-safe flavor-fill funnel, cast in a two-piece printed mold (the vacuum chamber + Orion pump + post-cure oven are tooling, in [purchases.md](/hardware/ledger/purchases.md) §21). ~78 g of mixed silicone per funnel (CAD shell volume 68.8 mL × ~1.13 g/mL) ≈ ~13 funnels per kit. Amazon 112-8255970 Jun 22: $35.16 ÷ 13 | 1 (~78 g) | $2.70 | $2.70 |
| [BBDINO black silicone pigment, 150 g](https://www.amazon.com/dp/B0BVR3R58V) | funnel colorant at ≤2% by weight (~1.5 g/funnel; carbon-black, hides dark-concentrate staining; food contact qualified by the wetted-surface screen, not a cert). $18.97 ÷ ~100 funnels | 1 (~1.5 g) | $0.19 | $0.19 |
| [Mann Ease Release 200, 14 oz aerosol](https://www.amazon.com/dp/B002YEBO1O) | addition-cure release on the funnel-mold cavity and the core's clear-acrylic seal (a release film, not a silicone fluid — trace cleared by the funnel's bake + wetted-surface screen); $21.99 ÷ ~50 pours | 1 (of ~50) | $0.44 | $0.44 |
| [TCP Global 32 oz graduated mixing cups (25-pk)](https://www.amazon.com/dp/B08HNCGY4N) | silicone-degassing batch cup (3–4× headroom for the ~70 mL pour), 1 disposable per pour; $17.99 ÷ 25 | 1 (of 25 pk) | $0.72 | $0.72 |

## 9. Dispensing (carbonator bottom-plate outlet → faucet)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [VALVENTO 1/4" OD compression × 1/4" NPT adapter (2-pk)](https://www.amazon.com/dp/B0DXZZBK7D) | joins bottom-plate 1/4" NPT outlet port (port 3) to 1/4" tubing run; 1 of 2 per unit (pack delivered $12.85/2) | 1 (of 2) | $6.42 | $6.42 |
| [Westbrass A2031-NL-62 8" Touch-Flo dispenser faucet, matte black](https://www.amazon.com/dp/B0BXFW1J38) | donor faucet; family-equivalence + interchangeable-finish notes in [`printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md) "Adjacent parts" | 1 | $32.18 | $32.18 |
| SendCutSend 0.060" 316 SS under-counter plate (`touch_flo_under_counter_plate.dxf`) | dimensions + role in [`printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md) "Adjacent parts"; SCS S064D925 May 10: 10 @ $2.85 + $5.00 ship + $2.79 tax = $36.29 ÷ 10 = $3.63/ea | 1 | $3.63 | $3.63 |
| [DIGITEN G1/4" Hall-effect flow sensor, 0.3–10 L/min](https://www.amazon.com/dp/B07QRXLRTH) | flow detection on the carbonated-water dispense path; ACQUIRED ×4 ([purchases.md](/hardware/ledger/purchases.md) §7) | 1 | $10.18 | $10.18 |
| [CARGEN Pipe Insulation Foam Tube, 1/4" ID × 3/8" wall × 6 ft, nitrile rubber closed-cell](https://www.amazon.com/dp/B0D2XFK337) | insulates the 1/4" OD LLDPE carbonated-water dispense tube from the foam-shell exit through the countertop to the underside of the Westbrass touch-flo body. ~12" per build, 72"/roll = 6 builds/roll. Amazon 112-3935659 May 15: 2 @ $7.59 + $1.10 tax = $16.28 ÷ 12 builds = $1.36/build | 1/6 roll (~12") | $1.36 | $1.36 |
| [BNTECHGO 28 AWG silicone ribbon cable, 4-conductor flat, 50 ft](https://www.amazon.com/dp/B07PNPHWMG) | Umbilical signal cable — the faucet-display harness (SIG-6: TX / RX / 5 V / GND) from the gooseneck 1.47" display down through the countertop and umbilical to the base ESP32. ~2 m per build off the 50 ft (15.2 m) spool; Amazon 112-9860351 Jun 10: $21.43 ÷ ~7 builds = $3.06/build | ~1/7 spool (~2 m) | $3.06 | $3.06 |

## 10. User interface

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [DIYables Passive Piezo Buzzer Module, 5 V (2-pack)](https://www.amazon.com/dp/B0DYDN31PV) | audible-alarm output — PWM tone from ESP32 GPIO 4 (LEDC); plugs into the carrier at U8 (3-pin GND/IO/VCC). 1 of 2 per unit ($6.42/2) | 1 (of 2 pk) | $3.21 | $3.21 |

## 11. Wiring + fasteners

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Dupont Jumper Wires (120-pack)](https://www.amazon.com/dp/B0BRTJXND9) | ~25 jumpers per unit (controller ↔ driver + sensors); 25/120 | 25 (of 120 pk) | $1.33 | $1.33 |
| [Female Spade Crimp Terminals (60-pack)](https://www.amazon.com/dp/B0B9MZJ2ML) | ~30 terminals per unit (12 solenoids × 2 leads + relay + flow sensor + misc); 30/60 = 1/2 pack | 30 (of 60 pk) | $5.36 | $5.36 |
| [Male Quick-Disconnect Spade (100-pack)](https://www.amazon.com/dp/B01MZZGAJP) | ~30 male spades per unit (harness side, paired with female terminals); 30/100 | 30 (of 100 pk) | $1.93 | $1.93 |
| [Zip Ties (200-pack)](https://www.amazon.com/dp/B0BC1VH4XB) | ~15 zip ties per unit (cable management); 15/200 | 15 (of 200 pk) | $0.30 | $0.30 |
| [CQRobot JST XH 2.54 mm 4-pin connector kit (50 sets)](https://www.amazon.com/dp/B0B2RB524Y) | 4-pin XH — the 4-wire I²C / UART hops (DS3231 I²C: VCC/GND/SDA/SCL, and the UART links to both displays (SIG-7 config + SIG-6 faucet)); ESP32 ends land on the DIN-breakout screw terminals, MCP I²C is PH2.0 not XH; ~3/unit; $8.45/50 × 3 | 3 (of 50 pk) | $0.17 | $0.51 |
| [CQRobot JST XH 2.54 mm 6-pin connector kit (50 sets)](https://www.amazon.com/dp/B0B2R8Q1JL) | 6-pin XH — L298N control row (ENA/IN1-4/ENB), the 6 lines driving both peristaltic pumps; ~1/unit; $9.19/50 | 1 (of 50 pk) | $0.18 | $0.18 |
| [CQRobot JST XH 2.54 mm 9-pin connector kit (30 sets)](https://www.amazon.com/dp/B0B2R73RQB) | 9-pin XH — ULN2803A module sides only (8 channels + COM/GND), 2 ULNs × 2 sides; ~4/unit; $9.19/30 × 4 | 4 (of 30 pk) | $0.31 | $1.23 |
| [CQRobot JST XH 2.54 mm 10-pin connector kit (30 sets)](https://www.amazon.com/dp/B0B2R93CV3) | 10-pin XH — MCP23017 GPIO port rows (VCC + GND + 8 GPIO); fills the 10-hole footprint so the header/housing can't seat off-by-one (the 9-pin was sized for the ULN sides, not these); ~4/unit; $8.99/30 × 4 | 4 (of 30 pk) | $0.30 | $1.20 |
| [CQRobot JST XH 2.54 mm pre-crimped bonded ribbon kit, 15 cm × 12 conductors × 8 ribbons + assorted housings](https://www.amazon.com/dp/B0F6C7X5CR) | short-hop bonded ribbon for module-to-module connections (≤6"); ~2/unit; $15.86/8 × 2 | 2 (of 8 pk) | $1.98 | $3.97 |
| [Keszoox JST XH 2.54 mm pre-crimped wires, 50 cm × 22 AWG silicone (20 wires/pk, 10 colors)](https://www.amazon.com/dp/B0F8HMQRRN) | cabinet-spanning pre-crimped female XH pigtails (ULN→solenoid fan-outs, sensor pigtails); ~1 pk/unit | 1 pk (of 20 wires) | $11.63 | $11.63 |
| [BNTECHGO 16 AWG silicone wire, 5-color kit (25 ft ea)](https://www.amazon.com/dp/B06Y557TCL) | AC pigtails for the C14 → distribution → relay → compressor + PSU runs per [`wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md); black line / white neutral / green ground, ~6 ft total per build across AC-1…AC-6. 252-strand silicone, 600 V. $38.29/125 ft = $0.31/ft; ON-ORDER ([purchases.md](/hardware/ledger/purchases.md) §9) | ~6 ft | $0.31/ft | $1.86 |
| [BNTECHGO 18 AWG silicone wire, red 25 ft + black 25 ft](https://www.amazon.com/dp/B07HGTKQ89) | 12 V DC trunk + branches, DC-1…DC-9 per [`wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md); red + / black −. The 12-solenoid fan-out rides the Keszoox pigtails, so this covers the trunk + pump / fan / display branches. 150-strand silicone, 600 V. $14.99/50 ft = $0.30/ft; ON-ORDER ([purchases.md](/hardware/ledger/purchases.md) §9) | ~8 ft | $0.30/ft | $2.40 |
| Wago 221-413 lever-nut connector, 3-conductor | placeholder pending sourcing decision; AC distribution block on the electronics shelf (H, N, G — one connector per conductor); 3 connectors per build, ~$0.85 each at 10-pk pricing | 3 | $0.85 | $2.55 |

## 12. Level sensing (external reed + internal magnetic float on 316L SS rod, shared SKU across carbonator + reservoirs)

The same reed-and-float pattern is used in three places: the carbonator vessel ([2](CARB_REEDS) reeds, threshold-only) and each flavor reservoir ([4](REEDS_PER_RES) reeds per reservoir × [2](RESERVOIRS) = [8](RES_REEDS_TOTAL) reeds, ~13-serving-step granularity / 5-state fuel-gauge display). All three use the same 1/8" 316L SS rod (Tandefio B0CY4DWJFQ) as the float guide. Flavor-reservoir architecture, rod material rationale, and rod-end retention geometry in [`printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) and [`printed-parts/cold-core/reservoir/reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py) (`ROD_*` and `BODY_BOSS_*` constants). The float itself is a commodity ⌀28 mm crimped-stainless capsule common to nearly every SS float switch (hence harvesting it from the cheapest donor). The bare float is available from component makers (e.g. Shenzhen Sunwoald, ~$1–3, MOQ ~10), with OEM/ODM custom (316L, chosen magnet) at the same price if a stronger or food-grade float is ever wanted.

### Carbonator (2 reeds, threshold-only)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [DEVMO MINI float switch (donor — harvest magnetic donut float, discard switch body)](https://www.amazon.com/dp/B07T18PGJ4) | float slides on the welded SS rod; only the float is shipped product, the rest of the donor unit is discarded | 1 | $13.93 | $13.93 |

### Flavor reservoirs ([4](REEDS_PER_RES) reeds per reservoir × [2](RESERVOIRS) reservoirs = [8](RES_REEDS_TOTAL) reeds, ~13-serving-step granularity)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| Pre-soldered reed-and-wire column | [4](REEDS_PER_RES) Gebildet reeds hand-soldered to a multi-conductor cable, inserted into the foam-shell channel before the body pour. Architecture in [`printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md). Cable candidate KWANGIL 22 AWG 12-conductor UL2464 ([B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21)) under evaluation per [purchases.md](/hardware/ledger/purchases.md). Reeds in shared §12 line below; cable TBD | 2 columns per build | — | — |
| [DEVMO MINI float switch (donor — harvest donut + ferrite magnet)](https://www.amazon.com/dp/B07T18PGJ4) | donor donut + its ferrite magnet kept (switch body / cable discarded); slides on the 1/8" 316L SS rod inside each reservoir. Architecture + magnet-strength rationale in [`printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) | 2 (1 per reservoir) | $13.93 | $27.86 |

### Float-guide rod (shared SKU across carbonator + flavor reservoirs)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Tandefio 1/8" × 12" 316 SS round rod (5-pk)](https://www.amazon.com/dp/B0CY4DWJFQ) | float-guide rod used in three places per build: (a) carbonator vessel — ~6" cut, laser-welded between plates (1/2 stick per build); (b) each flavor reservoir — ~200 mm rod dropped into a printed BODY boss (1 full stick per reservoir × 2 reservoirs). Total = 2.5 sticks/build; $8.57/5 × 2.5 = $4.29/build. Reservoir-side material rationale in [`printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) | 2.5 (of 5 pk) | $1.71 | $4.29 |

### Reeds (shared SKU across carbonator + flavor reservoirs)

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Gebildet reed switches, 14 mm glass body, NO (6-pk)](https://www.amazon.com/dp/B0CW9418F6) | [10](REEDS_TOTAL) reeds per build ([2](CARB_REEDS) carbonator + [8](RES_REEDS_TOTAL) flavor reservoir at 4 each × 2 reservoirs). 2 × 6-pack = 12 reeds, 2 spares | [10](REEDS_TOTAL) (of 2 × 6 = 12) | $1.07 | $10.71 |

### GPIO expansion for the 8 new flavor-reservoir reed inputs

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Waveshare MCP23017 I2C GPIO expander, second instance](https://www.amazon.com/dp/B07P2H1NZG) | same SKU as the existing expander in §1, second instance at I²C address 0x21: 4 MANIFOLD-B valves on PA[4:7] + the condenser-fan bit on PA3 (→ ULN U5; the silk-up ULN reverses the bank, so GPA_k drives channel 8-k), Reservoir B's 4 reeds on PB[0:3], and the 2 carbonator reeds on PB[4:5] (5 spare bits remain). See [`printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md) "GPIO budget" | 1 | $12.99 | $12.99 |

## 13. Mechanical attach hardware (heat-set inserts + screws + gasket) + reservoir-cap vent filter

Heat-set + screw retention appears in three places:

1. **Foam-bag-shell caps** clamped to the `outer_shell` via [12](FOAM_INSERTS) ruthex inserts + [12](FOAM_SCREWS) BNUOK M3×25 SHCS, TPU 90A gasket compressing per cap — procedure in [`assembly/cold-core.md`](/hardware/assembly/cold-core.md).
2. **Reservoir cap** clamped to each reservoir body via [6](RES_INSERTS_PER_CAP) ruthex inserts + 6 BNUOK M3×12 304 SS SHCS per cap, TPU gasket — geometry + screw spec in [`printed-parts/cold-core/reservoir/reservoir.py`](/hardware/printed-parts/cold-core/reservoir/reservoir.py).
3. **Touch-flo mounting plate** bolted up into the shell's three base pods via [3](TOUCHFLO_INSERTS) ruthex inserts + [3](TOUCHFLO_SCREWS) BNUOK M3×12 black-oxide SHCS — procedure in [`printed-parts/faucet/touch-flo-shell/ASSEMBLY.md`](/hardware/printed-parts/faucet/touch-flo-shell/ASSEMBLY.md).

Each reservoir cap also carries a ø13 mm hydrophobic PTFE membrane vent filter — see [`printed-parts/cold-core/reservoir/vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md) for the splash-baffle architecture; 1 filter per cap × [2](RESERVOIR_CAP_COUNT) caps per build = [2](VENT_FILTERS) per build.

The T18 heat-set tip kit ([B0CS662NVK](https://www.amazon.com/dp/B0CS662NVK)) and the FX-888D iron are tooling — not per-unit. TPU 90A gasket filament is consumed from per-unit-trivial stock; not separately listed.

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [ruthex M3 Threaded Inserts Short, 100 pc, RX-M3Sx4.0 brass heat-set](https://www.amazon.com/dp/B0D39W228K) | M3 × 4 mm L × 4.2 mm OD knurled brass; [27](TOTAL_M3_INSERTS) per build ([12](FOAM_INSERTS) foam-bag-shell + [12](RES_INSERTS) reservoir caps + [3](TOUCHFLO_INSERTS) touch-flo base pods); Amazon 112-4234665 May 10: $9.99 + $0.72 tax = $10.71 ÷ 100 = $0.1071/ea | [27](TOTAL_M3_INSERTS) (of 100 pk) | $0.11 | $2.89 |
| [BNUOK M3 × 25 mm DIN 912 socket head cap, 12.9 alloy steel, black oxide, 60 pc](https://www.amazon.com/dp/B0DJQGF665) | foam-bag-shell cap clamp screws (6 top + 6 bottom); Amazon 112-2495614 May 10: $7.99 + $0.58 tax = $8.57 ÷ 60 = $0.1428/ea | [12](FOAM_SCREWS) (of 60 pk) | $0.14 | $1.71 |
| [BNUOK M3 × 12 mm DIN 912 socket head cap, 304 stainless steel (18-8), 120 pc](https://www.amazon.com/dp/B0DJQGMQZM) | reservoir-cap clamp screws (reservoir lid/body joint); Amazon 112-3709957 Jun 2: $8.07 + $0.59 tax = $8.66 ÷ 120 = $0.0722/ea | [12](RES_SCREWS) (of 120 pk) | $0.07 | $0.87 |
| [BNUOK M3 × 12 mm DIN 912 socket head cap, 12.9 alloy steel, black oxide, 120 pc](https://www.amazon.com/dp/B0DJQGVK8S) | touch-flo plate-to-shell screws; Amazon 112-0144900 May 10: $7.99 + $0.58 tax = $8.57 ÷ 120 = $0.0714/ea | [3](TOUCHFLO_SCREWS) (of 120 pk) | $0.07 | $0.21 |
| [LVDALAB PTFE Membrane Filter, ø13 mm × 0.45 µm, 100 pc, non-sterile](https://www.amazon.com/dp/B0D41KT345) | hydrophobic PTFE membrane in the reservoir-cap vent pocket; architecture + sizing in [`printed-parts/cold-core/reservoir/vent.md`](/hardware/printed-parts/cold-core/reservoir/vent.md); [2](VENT_FILTERS) per build (1 per cap × 2 caps); Amazon 112-4393734 May 11: $12.99 − $0.65 promo + $0.89 tax = $13.23 ÷ 100 = $0.1323/ea | [2](VENT_FILTERS) (of 100 pk) | $0.13 | $0.26 |

## 14. Install kit (per-appliance install-kit tools)

Per-appliance tools that ship in the install kit so the field installer can cut the 3-tube umbilical bundle to length and push each tube into its rear-panel PTC bulkhead. Each entry is a tool the installer uses once during install and keeps with the appliance (or returns to the kit) — not consumed into the fluid path, not a fab-shop tool. Future additions expected: printed stubby wrench for the compression nut, foam knife.

| Part | Notes | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Mudder 3 Pieces PTFE Plastic Tubing Cutter, OD up to 3/4", polyacetal body + 304 SS replaceable blade](https://www.amazon.com/dp/B08VW15TK8) | installer trims the 3-tube umbilical bundle to length at field install before pushing tubes into rear-panel PTC bulkheads; OD range 1/8"–3/4" covers the 1/4" OD LLDPE umbilical easily. 3-pack = 1 cutter per install × 3 installs per pack. Amazon 112-8598924 May 17: $11.99 + $0.87 tax = $12.86 ÷ 3 = $4.29/ea | 1 (of 3 pk) | $4.29 | $4.29 |

## Totals

| Section | $ |
|---|---:|
| 1. Controllers + electronics | [$169.76](BOM_SEC1) |
| 2. Carbonator vessel (plan A, 316L) | [$240.69](BOM_SEC2) |
| 3. Water inlet | [$240.21](BOM_SEC3) |
| 4. CO2 subsystem | [$172.20](BOM_SEC4) |
| 5. Refrigeration | [$194.67](BOM_SEC5) |
| 6. Cold core insulation | [$52.38](BOM_SEC6) |
| 7. Printed parts (PETG + PET-CF) | [$68.10](BOM_SEC7) |
| 8. Flavor subsystem | [$257.94](BOM_SEC8) |
| 9. Dispensing | [$56.83](BOM_SEC9) |
| 10. UI | [$3.21](BOM_SEC10) |
| 11. Wiring | [$34.45](BOM_SEC11) |
| 12. Level sensing | [$69.78](BOM_SEC12) |
| 13. Mechanical attach hardware + reservoir-cap vent filter | [$5.94](BOM_SEC13) |
| 14. Install kit | [$4.29](BOM_SEC14) |
| **Total** | **[$1,570.45](BOM_GRAND)** |

## External / user-supplied (not shipped)

- **5 lb CO2 tank** + refills (~$25/refill at welding/homebrew shops)
- **Flavor concentrate** — SodaStream or BIB syrup
- **Tap-water source under the cabinet** — an existing 3/8" or 1/2" angle-stop on a cold-water line (the same prerequisite a dishwasher or under-counter water filter has). The kit includes the tee, the 1/4" LLDPE, and the water filter — the customer brings only the existing angle stop.

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_bom_sync.py`
- `/hardware/scripts/_bom_totals.py`
