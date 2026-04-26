# Bill of Materials — One Consumer Unit

Per-unit parts for a single finished appliance built on the **custom-vessel** path specified in [future.md](future.md). Carbonator vessel current plan A: vertical 5" OD × 0.065" wall 316 welded SS round tube (OnlineMetals #12498, MTRs required) capped with 1/4"-thick laser-cut 316 SS circular plates from SendCutSend (`endcap-circular-2hole.dxf`), joined with the XLaserlab X1 Pro handheld laser welder. 1/4" NPT is direct-tapped into the plates (no weld-in bungs). Plan B (racetrack press-formed body in 304 SS + dished racetrack 304 end caps) retained as fallback inventory. Compressor is harvested from a countertop ice-maker; cold core is 3D-printed shells with pour-in-place foam; flavor reservoirs are two 1 L Platypus bladders inside the cold core.

Prototype tools, fabrication equipment (welder, slip roll, shop press, dishing dies), donor parts consumed during teardown, duplicate SKUs, and consumables live in [purchases.md](purchases.md).

First-pass draft. **Pricing convention: delivered cost** (product + shipping + tax) drawn from resolved order history in [purchases.md](purchases.md) wherever the SKU has been ordered or acquired; list price for forward-plan SKUs not yet purchased. Pack-amortized lines show the math in the description (e.g., `$31.08/2`). Expect revisions.

## 1. Controllers + electronics

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | B09MQJWQN2 | 1 | $11.00 | $11.00 |
| [ESP32 DIN Rail Breakout Board](https://www.amazon.com/dp/B0BW4SJ5X2) | B0BW4SJ5X2 | 1 | $25.99 | $25.99 |
| [Waveshare RP2040 Round LCD 0.99"](https://www.amazon.com/dp/B0CTSPYND2) | B0CTSPYND2 | 1 | $23.99 | $23.99 |
| [Meshnology ESP32-S3 1.28" Rotary Display](https://www.amazon.com/dp/B0G5Q4LXVJ) | B0G5Q4LXVJ | 1 | $47.76 | $47.76 |
| [L298N Dual H-Bridge (4-pack)](https://www.amazon.com/dp/B0C5JCF5RS) | B0C5JCF5RS — 1 driver per unit drives both peristaltic pumps (dual H-bridge); 1 of 4 per unit ($10.71/4) | 1 (of 4 pk) | $2.68 | $2.68 |
| [Waveshare MCP23017 I2C GPIO expander](https://www.amazon.com/dp/B07P2H1NZG) | B07P2H1NZG — expands ESP32 I2C into 16 GPIO for solenoid bank | 1 | $12.99 | $12.99 |
| [HiLetgo DS3231 high-precision RTC (5-pk)](https://www.amazon.com/dp/B01N1LZSK3) | B01N1LZSK3 — I2C RTC at 0x68, referenced in `wiring/esp32-pinout.mmd` and `wiring/valve-control.mmd`; 1 of 5 per unit ($16.08/5) | 1 (of 5 pk) | $3.22 | $3.22 |
| [ULN2803A high-current driver module (2-pc)](https://www.amazon.com/dp/B0F872W528) | B0F872W528 — 2 modules drive 12 solenoids from MCP23017 outputs; each module is a small carrier PCB with mounting holes (vs the bare BOJACK B08CX79JSQ DIPs which would need a separate host board); 1 full 2-pack per unit | 1 pk | $6.59 | $6.59 |
| [Mean Well IRM-90-12ST, 80 W / 12 V / 6.7 A, encapsulated](https://www.amazon.com/dp/B0CNRST18V) | B0CNRST18V — firmware serializes pump vs other loads, caps worst case at ~5.4 A; IEC 60335-1 household-appliance safety listed; 190 cm³ vs 288 cm³ for LRS-75 | 1 | $31.66 | $31.66 |

## 2. Carbonator vessel (custom fabrication — plan A: round tube + 1/4" plates, 316L)

Plan A is the current path. Plan B (racetrack body half-sheets + dished racetrack end caps + 4× weld bungs, all 304 SS) remains as fallback if the 1/4"-plate-to-0.065"-tube weld can't be made reliably; plan B parts are tracked in [purchases.md](purchases.md) §1.

| Part | Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| OnlineMetals #12498 — 5" OD × 0.065" wall 316 welded SS round tube, cut to 6.0" length (MTRs required); order 1020857414 placed Apr 24, 2026, 10 pcs @ $67.35 ea + ship + tax = $736.73 delivered ÷ 10 = $73.67/vessel | OnlineMetals.com | 1 | $73.67 | $73.67 |
| SendCutSend 1/4"-thick 316 SS circular endcap plate, 4.860" diameter with 2× 7/16" tap-pilot holes for 1/4" NPT (`endcap-circular-2hole.dxf`); order SG019619 placed Apr 24, 2026 (paid), 20 pcs @ $28.96 ea + tax = $621.19 delivered ÷ 20 = $31.06/plate; 2 plates per vessel | sendcutsend.com | 2 | $31.06 | $62.12 |
| [LTWFITTING 1/4" hose barb × 1/4" MNPT, 316 SS (5-pk)](https://www.amazon.com/dp/B017N4TTMA) | B017N4TTMA — port 1 (CO2 in via internal sparge); threads into bottom plate, barb faces inward to silicone tube → sparge stone; 1 of 5 per unit ($13.65/5) | 1 (of 5 pk) | $2.73 | $2.73 |
| [FERRODAY 0.5 µm sintered 316 SS sparge stone, 1/4" barb input (2-set)](https://www.amazon.com/dp/B091C5Y6L9) | B091C5Y6L9 — internal sparge stone, hangs in water column on silicone tube from port-1 barb adapter; 1 of 2 per unit ($14.97/2) | 1 (of 2) | $7.49 | $7.49 |
| Food-grade silicone tube stub, 1/4" ID × ~3" long (cut from existing Metaland 1/4" silicone B08L1ST6ST stock in §5) | B08L1ST6ST — connects port-1 barb to sparge stone inside vessel | — | ~$0.20 | $0.20 |
| [Millrose 70894 Nickel Guard anti-seize PTFE tape](https://www.amazon.com/dp/B07C9ZV4PG) | B07C9ZV4PG — anti-seize for SS-into-SS NPT joints (4 ports per unit) | 1 | $20.07 | $20.07 |
| [Tap Magic EP-Xtra pipe-tap cutting fluid, 16 oz (size variant on listing B00DHMHSGM)](https://www.amazon.com/dp/B00DHMHSGM) | B00DHMHSGM — required for hand-tapping 1/4" NPT into 1/4"-thick 316 SS plate; ~$0.50 of fluid per vessel | 1 | $0.50 | $0.50 |
| [Control Devices SV-100 safety valve, 1/4" NPT, 100 psi set pressure](https://www.amazon.com/dp/B0D361X97X) | B0D361X97X — Port 4 tank PRV (top plate, dedicated) | 1 | $16.06 | $16.06 |
| [Cambro 6 QT polycarbonate square container](https://www.amazon.com/dp/B001BZEQ44) | B001BZEQ44 — citric acid passivation soak tub, one-time-use per unit | 1 | $20.00 | $20.00 |
| [Viva Doria food-grade citric acid, 2 lb bag](https://www.amazon.com/dp/B0C5NQM8S1) | B0C5NQM8S1 — passivation: ~1 qt of 4% solution per tank; 1/20 of $9.99 bag | 1 | $0.50 | $0.50 |

## 3. Water inlet (tap → backflow → pump → top-plate port)

| Part | ASIN / Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Multiplex 19-0897 ASSE 1022 backflow preventer](https://www.midwestbev.com/products/asse-1022-backflow-preventer); midwestbev order MB11053 placed Apr 24, 2026, qty 4 @ $29.33 = $117.32 + $28.48 UPS Ground + $0.00 tax = $145.80 delivered ÷ 4 = $36.45/unit | midwestbev.com | 1 | $36.45 | $36.45 |
| [Hooshing 3/8" flare × 1/4" FNPT adapter (2-pk)](https://www.amazon.com/dp/B0BNHVV6HT) | B0BNHVV6HT — Multiplex MFL output adapter; 1 of 2 per unit ($10.71/2) | 1 (of 2 pk) | $5.36 | $5.36 |
| [Sealproof 1/4" ID × 3/8" OD clear PVC, 10 ft](https://www.amazon.com/dp/B07D9DK94V) (vent telltale) | B07D9DK94V | 1 | $8.46 | $8.46 |
| [LOKMAN 304 SS worm-gear clamps, 10–16 mm (20-pk)](https://www.amazon.com/dp/B076Q7QVNM) | B076Q7QVNM — vent line clamps; 4 of 20 per unit | 4 (of 20 pk) | $1.80 | $1.80 |
| [SEAFLO 22-Series 12V 1.3 GPM 100 psi diaphragm pump (3/8" hose-barb ports)](https://www.amazon.com/dp/B0166UBJX4) | B0166UBJX4 | 1 | $48.25 | $48.25 |
| [MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4-pk)](https://www.amazon.com/dp/B0DMP77B6S) | B0DMP77B6S — adapts pump 3/8" hose-barb output to 1/4" NPT plumbing for the check valve and top-plate port; 1 of 4 per unit (also used in §8) | 1 (of 4 pk) | $3.24 | $3.24 |
| [GASHER 1/4" NPT SS one-way check valve (2-pk, $15.00)](https://www.amazon.com/dp/B0FV2D2FFX) | B0FV2D2FFX — **water-side check** between SeaFlo pump and top-plate water-inlet port; PTFE soft-seat on metal poppet (confirmed by inspection 2026-04-25; vs the pump's internal elastomer); 1 of 2 valves per unit (the other valve is the CO2-side check in §4) | 1 (of 2) | $7.50 | $7.50 |
| [Lifevant 1/4" OD water tubing 32.8 ft + quick-connects](https://www.amazon.com/dp/B0DKCZ5W66) | B0DKCZ5W66 — water-inlet tubing (filter → pump → vessel) ~8–10 ft + ~5 of 12 quick-connects per unit; ~1/3 of pack | 1 (~1/3 pk) | $3.33 | $3.33 |
| [John Guest 1/4" OD × 1/8" NPT push-fit](https://www.amazon.com/dp/B07V6XKZG9) | B07V6XKZG9 | 1 | $5.00 | $5.00 |
| [John Guest PI1208S acetal bulkhead union, 1/4" QC](https://www.amazon.com/dp/B0C1F3QR7N) | B0C1F3QR7N | 1 | $11.49 | $11.49 |

## 4. CO2 subsystem

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Wellbom dual-gauge CO2 regulator, CGA-320, 0–120 PSI out / 150 PSI PRV](https://www.amazon.com/dp/B0G13P5PMY) | B0G13P5PMY | 1 | $44.99 | $44.99 |
| [5/16" ID beer CO2 line, 10 ft + 4 clamps](https://www.amazon.com/dp/B0D1RB3TF6) | B0D1RB3TF6 — ~2 ft of hose (regulator → bottom-plate barb) + 2 of 4 clamps per unit; ~1/4 of pack value | 1 (~1/4 pk) | $3.50 | $3.50 |
| [DERPIPE 5/16" tube × 1/4" NPT push-to-connect (5-pk)](https://www.amazon.com/dp/B09LXVGPG7) | B09LXVGPG7 — CO2 line entry to vessel; 1 of 5 per unit ($10.71/5). **5/16" variant appears delisted; source replacement ASIN** | 1 (of 5 pk) | $2.14 | $2.14 |
| [GASHER 1/4" NPT SS one-way check valve (2-pk, $15.00) — second of pack](https://www.amazon.com/dp/B0FV2D2FFX) | B0FV2D2FFX — **CO2-side check** between DERPIPE 5/16"-tube × 1/4"-NPT push-to-connect and the LTWFITTING bottom-plate barb adapter; prevents water back-flow into the CO2 regulator if pressures invert under fault. Same 2-pack as the §3 water-side check, second valve of the pair | 1 (of 2) | $7.50 | $7.50 |

## 5. Refrigeration (harvested compressor path)

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Frigidaire EFIC117-SS ice-maker donor (compressor/condenser/cap-tube/drier)](https://www.amazon.com/dp/B07PCZKG94) | B07PCZKG94 | 1 | $78.70 | $78.70 |
| [GOORY 1/4" OD × 50 ft ACR copper coil (evaporator)](https://www.amazon.com/dp/B0DKSW5VL9) | B0DKSW5VL9 — single-layer wrap on 5" OD vessel at 1/8" gap pitch yields ~22 ft of wrap per unit + ~2 ft each end for compressor + suction-line tie-ins ≈ ~24 ft consumed per unit; one 50 ft roll comfortably covers 2 units, so 1/2 roll allocated per unit ($68.63/2) | 1/2 roll | $34.32 | $34.32 |
| [Supco SUD8358 filter-drier, 1/4" sweat × cap-tube outlet, XH-9 molecular sieve, integrated Schrader access port](https://www.amazon.com/dp/B009AX2O5W) | B009AX2O5W — replaces factory drier after venting; 1/4" sweat inlet brazes to condenser outlet; cap-tube outlet accepts the factory capillary tube directly (no reducer needed); Schrader port provides vacuum + recharge access; XH-9 desiccant is hydrocarbon-compatible | 1 | $13.40 | $13.40 |
| [Teyleten 3.3 V relay module, opto-isolated, 10 A @ 250 VAC (5-pk)](https://www.amazon.com/dp/B07XGZSYJV) | B07XGZSYJV — two relays per unit: relay #1 switches the compressor's 120 VAC hot leg (ESP32 GPIO 14), relay #2 gates 12 V to the SeaFlo diaphragm pump for firmware-controlled refill (ESP32 GPIO 4); 2 of 5 per unit | 2 (of 5 pk) | $2.60 | $5.20 |
| [HiLetgo DS18B20 waterproof 1-wire probe, 1 m SS sheath (5-pk)](https://www.amazon.com/dp/B00M1PM55K) | B00M1PM55K — 2 probes per unit: tank wall (compressor cycling setpoint) + evaporator coil (freeze-protect cutout); 2 of 5 per unit ($11.79/5 × 2) | 2 (of 5 pk) | $2.36 | $4.72 |
| [MXR IEC 60320 C14 panel-mount AC inlet, 10 A / 250 VAC (10-pk)](https://www.amazon.com/dp/B07DCXKNXQ) | B07DCXKNXQ — rear-panel mains inlet; accepts standard NEMA 5-15P-to-C13 line cord; 1 of 10 per unit ($6.96/10) | 1 (of 10 pk) | $0.70 | $0.70 |
| [Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed (6-pk)](https://www.amazon.com/dp/B08VS8D4WC) | B08VS8D4WC — ships in the box so the customer can plug the appliance into a standard US wall outlet; 1 of 6 per unit ($24.00/6) | 1 (of 6 pk) | $4.00 | $4.00 |
| [Enviro-Safe R-600a 3-pack + brass charging gauge](https://www.amazon.com/dp/B0CGG1WH1N) | B0CGG1WH1N — pure R-600a (not blend or n-butane); refills the sealed loop after venting factory charge; ~40 g per system × ~12 recharges per 3-can bundle; 1/12 of $72.92 delivered; brass gauge stays with tools (see purchases.md) | 1 | $6.08 | $6.08 |

Fallback path (UL/ETL-retail-friendly): RIGID DV1910E sealed refrigeration module (~$600 + 20–30% import duty). Not selected for this BOM.

## 6. Cold core insulation

| Part | Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Fiberglass Supply Depot 2 lb 2-part closed-cell pour-in-place PU foam, 1 qt kit](https://www.amazon.com/dp/B08R7TX8QJ) | B08R7TX8QJ — 1.25 ft³ yield covers inner + outer shells with margin | 1 kit | $39.99 | $39.99 |
| [3M 425 aluminum foil tape, 2" × 180 ft](https://www.amazon.com/dp/B07BTW7C2N) | B07BTW7C2N — thermally conductive aluminum foil, applied under the coil (continuous aluminum skin on tank OD, coil wraps over it) to bridge the tank ↔ coil thermal interface; replaces the earlier generic "thermal compound" plan which was unsuitable for this macro-scale gap geometry without clamping pressure; one 180 ft roll covers ~12 builds at ~15 ft/build; 1/12 of $88.97 | 1 | $7.41 | $7.41 |

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

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Kamoer KPHM400-SW3B25 12V peristaltic pump](https://www.amazon.com/dp/B09MS6C91D) | B09MS6C91D — paid price per Feb 2026 orders #114-1015191-6799441 + #112-0545074-9805025 (sold by Kamoer Fluid Tech Shanghai); current Amazon listing matches at $32.55 | 2 | $32.55 | $65.10 |
| [Magnetic pogo pin connector, 2-pin (2 pair)](https://www.amazon.com/dp/B0CSX6ZQ1H) | B0CSX6ZQ1H — tool-free pump cartridge electrical connection, one pair per pump | 1 pk | $10.71 | $10.71 |
| [Beduan 12V 1/4" solenoid valve (NC)](https://www.amazon.com/dp/B07NWCQJK9) | B07NWCQJK9 — V-A/B/C/D/E/F/G/H/I/J/KA/KB per fluid-topology-manifold.mmd; lower-bound delivered single-unit cost (range $9.64–$19.28 across user's mixed orders) | 12 | $9.64 | $115.68 |
| [Platypus SoftBottle 1 L bladder](https://www.amazon.com/dp/B08PG3GMQ8) | B08PG3GMQ8 | 2 | $23.49 | $46.98 |
| [Platypus Hoser hydration tube kit](https://www.amazon.com/dp/B07N1T6LNW) | B07N1T6LNW | 1 | $24.95 | $24.95 |
| [Silicone tubing 1/8" ID × 1/4" OD](https://www.amazon.com/dp/B0BM4KQ6RT) | B0BM4KQ6RT — pump-head tube only (line runs are 1/4" LLDPE); per-roll delivered cost ($12.99 pre-tax + allocated tax = $13.93) amortized 1 roll per unit pending real per-unit consumption measurement | 1 | $13.93 | $13.93 |
| [Supply Depot BIB connector, 3/8" red (2-pk)](https://www.amazon.com/dp/B0DMFK9B6P) | B0DMFK9B6P — rear-panel commercial-syrup input | 1 pk | $19.99 | $19.99 |
| [MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4-pk)](https://www.amazon.com/dp/B0DMP77B6S) | B0DMP77B6S | 1 pk | $12.97 | $12.97 |
| [PureSec TWS1414 1/4" push-to-connect Y splitter (10-pk)](https://www.amazon.com/dp/B01N5I1ZJC) | B01N5I1ZJC — manifold Y-A/B/C/D/E/F/G/H/KA/KB per fluid-topology-manifold.mmd; food/water-safe plastic | 1 pk | $7.99 | $7.99 |

## 9. Dispensing (carbonator bottom-plate outlet → faucet)

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [VALVENTO 1/4" OD compression × 1/4" NPT adapter (2-pk)](https://www.amazon.com/dp/B0DXZZBK7D) | B0DXZZBK7D — joins bottom-plate 1/4" NPT outlet port (port 3) to 1/4" tubing run; 1 of 2 per unit (pack delivered $12.85/2) | 1 (of 2) | $6.42 | $6.42 |
| [VALVENTO 1/4" OD 316 SS tube, 12" (5-pk)](https://www.amazon.com/dp/B0F6SYFK48) | B0F6SYFK48 — short rigid stub from compression adapter into the soft 1/4" tubing run; 1 of 5 per unit (pack delivered $18.23/5) | 1 (of 5) | $3.65 | $3.65 |
| [Westbrass R2031-NL-62 8" Touch-Flo dispenser faucet, matte black](https://www.amazon.com/dp/B07KH285GJ) | B07KH285GJ — direct successor to retired A2031 SKU | 1 | $31.28 | $31.28 |
| [DIGITEN G3/8" Hall-effect flow sensor](https://www.amazon.com/dp/B07QQW4C7R) | B07QQW4C7R | 1 | $7.99 | $7.99 |

## 10. User interface

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [KRAUS garbage-disposal air-switch, matte black](https://www.amazon.com/dp/B096319GMV) | B096319GMV | 1 | $39.95 | $39.95 |

## 11. Wiring + fasteners

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Dupont Jumper Wires (120-pack)](https://www.amazon.com/dp/B0BRTJXND9) | B0BRTJXND9 — ~25 jumpers per unit (controller ↔ driver + sensors); 25/120 | 25 (of 120 pk) | $1.33 | $1.33 |
| [Female Spade Crimp Terminals (60-pack)](https://www.amazon.com/dp/B0B9MZJ2ML) | B0B9MZJ2ML — ~30 terminals per unit (12 solenoids × 2 leads + relay + flow sensor + misc); 30/60 = 1/2 pack | 30 (of 60 pk) | $5.36 | $5.36 |
| [Male Quick-Disconnect Spade (100-pack)](https://www.amazon.com/dp/B01MZZGAJP) | B01MZZGAJP — ~30 male spades per unit (harness side, paired with female terminals); 30/100 | 30 (of 100 pk) | $1.93 | $1.93 |
| [Zip Ties (200-pack)](https://www.amazon.com/dp/B0BC1VH4XB) | B0BC1VH4XB — ~15 zip ties per unit (cable management); 15/200 | 15 (of 200 pk) | $0.30 | $0.30 |

## 12. Carbonator level sensing (external reed + internal float on welded SS rod)

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Tandefio 1/8" × 12" 316 SS round rod (5-pk)](https://www.amazon.com/dp/B0CY4DWJFQ) | B0CY4DWJFQ — laser-welded vertically inside vessel between bottom and top plates; carries the magnetic float; cut from 12" to ~6" (one 12" stick yields 2 vessel rods, so 5-pk = 10 vessels) | 1 (of 10) | $0.86 | $0.86 |
| [DEVMO MINI float switch (donor — harvest magnetic donut float, discard switch body)](https://www.amazon.com/dp/B07T18PGJ4) | B07T18PGJ4 — float slides on the welded SS rod; only the float is shipped product, the rest of the donor unit is discarded | 1 | $13.93 | $13.93 |
| [Gebildet reed switches, 14 mm glass body, NO (6-pk)](https://www.amazon.com/dp/B0CW9418F6) | B0CW9418F6 — 2 reeds per unit (low-level refill threshold + high-level full threshold), mounted on the outside of the 0.065" SS tube wall; 316L (and 304) are austenitic and non-magnetic so the float magnet's field passes through ($6.42/6 × 2) | 2 (of 6) | $2.14 | $4.28 |

## Totals

| Section | $ |
|---|---:|
| 1. Controllers + electronics | $165.88 |
| 2. Carbonator vessel (plan A, 316L) | $203.34 |
| 3. Water inlet | $130.88 |
| 4. CO2 subsystem | $58.13 |
| 5. Refrigeration | $147.12 |
| 6. Cold core insulation | $47.40 |
| 7. Printed parts (PETG) | $103.94 |
| 8. Flavor subsystem | $318.30 |
| 9. Dispensing | $49.34 |
| 10. UI | $39.95 |
| 11. Wiring | $8.92 |
| 12. Level sensing | $19.07 |
| **Total** | **$1,292.27** |

## External / user-supplied (not shipped)

- **5 lb CO2 tank** + refills (~$25/refill at welding/homebrew shops)
- **Flavor concentrate** — SodaStream or BIB syrup
- **Water filter** — user's choice of inline filter upstream of the appliance

## Notes / open questions

- **GASHER B0FV2D2FFX check valve seat material — RESOLVED.** Physical inspection 2026-04-25 confirmed PTFE soft-seat insert in metal poppet (off-white waxy disc, not elastomer). PTFE-on-metal is the standard soft-seat construction in commercial beverage/brewery/food-process check valves at this pressure class; suitable for production and long-term field service on both wetted-water and dry-CO2 lines. No substitute needed.
- **Platypus 1 L vs 2 L** — future.md specifies 1 L bladders. README's parts list shows 2 L. Using 1 L per future.md; revisit if cradle geometry forces larger.
- **Refrigeration charge** — Path A vents the factory R-600a charge and recharges from Enviro-Safe cans (§5); ~40 g per system × 12 recharges per 3-can bundle amortizes to ~$5.67/unit. No recovery equipment and no EPA 608 cert required (natural-refrigerant carveout).
- **5" OD tube and 1/4" plate sourcing — RESOLVED.** Tube ordered from OnlineMetals (#12498, 316 welded, MTRs required) on order 1020857414 = $73.67/vessel delivered. End-cap plates ordered from SendCutSend on order SG019619 (1/4" 316 SS, `endcap-circular-2hole.dxf`) = $31.06/plate delivered, 2 plates per vessel.
- **Plan B (racetrack) parts** — half-sheet body blanks (SendCutSend SP54G453), dished racetrack end caps (SV07U813), 4× weld bungs (B07QNV8796), and 4× hex nipples (B0GD1QBLQ3) remain in [purchases.md](purchases.md) §1 as fallback inventory in 304 SS; not on this BOM unless plan A is abandoned.
- **Beduan atomizer B07LGPD3GB** — superseded by the internal sparge architecture; will not ship in the appliance. Bench-test inventory only.
