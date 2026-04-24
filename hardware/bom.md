# Bill of Materials — One Consumer Unit

Per-unit parts for a single finished appliance built on the **custom-racetrack-vessel** path specified in [future.md](future.md): in-house fabricated 304 SS carbonator, compressor harvested from a countertop ice-maker, 3D-printed cold-core shells with spray-foam insulation, two 1 L Platypus bladders inside the cold core.

Prototype tools, fabrication equipment (welder, slip roll, shop press, dishing dies), donor parts consumed during teardown, duplicate SKUs, and consumables live in [purchases.md](purchases.md).

First-pass draft. Prices from resolved Amazon order history (purchases.md) or direct-source quotes. Expect revisions.

## 1. Controllers + electronics

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | B09MQJWQN2 | 1 | $11.00 | $11.00 |
| [ESP32 DIN Rail Breakout Board](https://www.amazon.com/dp/B0BW4SJ5X2) | B0BW4SJ5X2 | 1 | $25.99 | $25.99 |
| [Waveshare RP2040 Round LCD 0.99"](https://www.amazon.com/dp/B0CTSPYND2) | B0CTSPYND2 | 1 | $23.99 | $23.99 |
| [Meshnology ESP32-S3 1.28" Rotary Display](https://www.amazon.com/dp/B0G5Q4LXVJ) | B0G5Q4LXVJ | 1 | $47.76 | $47.76 |
| [L298N Dual H-Bridge (4-pack)](https://www.amazon.com/dp/B0C5JCF5RS) | B0C5JCF5RS | 1 pk | $9.99 | $9.99 |
| [Waveshare MCP23017 I2C GPIO expander](https://www.amazon.com/dp/B07P2H1NZG) | B07P2H1NZG — expands ESP32 I2C into 16 GPIO for solenoid bank | 1 | $12.99 | $12.99 |
| [BOJACK ULN2803APG Darlington driver IC (10-pk)](https://www.amazon.com/dp/B08CX79JSQ) | B08CX79JSQ — 2 ICs drive 12 solenoids from MCP23017 outputs | 1 pk | $6.99 | $6.99 |
| [Mean Well IRM-90-12ST, 80 W / 12 V / 6.7 A, encapsulated](https://www.amazon.com/dp/B0CNRST18V) | B0CNRST18V — firmware serializes pump vs other loads, caps worst case at ~5.4 A; IEC 60335-1 household-appliance safety listed; 190 cm³ vs 288 cm³ for LRS-75 | 1 | $29.52 | $29.52 |

## 2. Carbonator vessel (custom fabrication)

| Part | Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| SendCutSend-cut 304 SS body half-sheets, 7.754" × 6" × 0.048" (`carbonator_body_half_blank.dxf`) | order SP54G453, qty 10 @ $134.38 delivered = $13.44/ea; 2 per vessel | 2 | $13.44 | $26.87 |
| SendCutSend-cut 304 SS end-cap blanks, 5.492" × 3.892" × 0.060" (`endcap_racetrack_domed_top.dxf` + `endcap_racetrack_domed_bottom_blank.dxf`) | order SV07U813 (Apr 16, 2026): top qty 2 @ $10.91 + bottom qty 2 @ $10.31 subtotal = $42.44 + $3.08 tax = $45.52 delivered for 2 vessels = $22.76/vessel; 1 top + 1 bottom per vessel | 2 | $11.38 | $22.76 |
| [1/4" NPT female weld bung, 304 SS stepped flange](https://www.amazon.com/dp/B07QNV8796) | B07QNV8796 | 4 | $7.99 | $31.96 |
| [4pc 1/4" NPT male hex nipple, 316 SS 5000 psi](https://www.amazon.com/dp/B0GD1QBLQ3) | B0GD1QBLQ3 — one nipple per bung for external plumbing | 1 pk | $15.99 | $15.99 |
| [Beduan 1/4" spiral cone atomization nozzle, 316 SS](https://www.amazon.com/dp/B07LGPD3GB) | B07LGPD3GB | 1 | $9.99 | $9.99 |
| [VALVENTO 1/4" OD 316 SS tube, 12" (5-pk)](https://www.amazon.com/dp/B0F6SYFK48) | B0F6SYFK48 — dip tube + internal rigid lines | 1 pk | $16.99 | $16.99 |
| [VALVENTO 1/4" OD compression × 1/4" NPT adapter (2-pk)](https://www.amazon.com/dp/B0DXZZBK7D) | B0DXZZBK7D | 1 pk | $11.99 | $11.99 |
| [Millrose 70894 Nickel Guard anti-seize PTFE tape](https://www.amazon.com/dp/B07C9ZV4PG) | B07C9ZV4PG — anti-seize for SS-into-SS NPT joints | 1 | $22.22 | $22.22 |
| [Control Devices SV-100 ASME safety valve, 1/4" NPT, 100 psi](https://www.amazon.com/dp/B0D361X97X) | B0D361X97X — Port 4 tank PRV | 1 | $16.06 | $16.06 |
| [Cambro 6 QT polycarbonate square container](https://www.amazon.com/dp/B001BZEQ44) | B001BZEQ44 — citric acid passivation soak tub, one-time-use per unit | 1 | $20.00 | $20.00 |
| [Viva Doria food-grade citric acid, 2 lb bag](https://www.amazon.com/dp/B0C5NQM8S1) | B0C5NQM8S1 — passivation: ~1 qt of 4% solution per tank; 1/20 of $9.99 bag | 1 | $0.50 | $0.50 |

## 3. Water inlet (tap → backflow → pump → atomizer)

| Part | ASIN / Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Multiplex 19-0897 ASSE 1022 backflow preventer](https://www.howdybrewer.com/products/multiplex-backflow-preventor-assembly-1022-3-8-npt-x-3-8-mfl) | howdybrewer | 1 | $38.99 | $38.99 |
| [Hooshing 3/8" flare × 1/4" FNPT adapter (2-pk)](https://www.amazon.com/dp/B0BNHVV6HT) | B0BNHVV6HT | 1 pk | $9.99 | $9.99 |
| [Sealproof 1/4" ID × 3/8" OD clear PVC, 10 ft](https://www.amazon.com/dp/B07D9DK94V) (vent telltale) | B07D9DK94V | 1 | $7.89 | $7.89 |
| [LOKMAN 304 SS worm-gear clamps, 10–16 mm (20-pk)](https://www.amazon.com/dp/B076Q7QVNM) | B076Q7QVNM | 1 pk | $8.99 | $8.99 |
| [SEAFLO 22-Series 12V 1.3 GPM 100 psi diaphragm pump](https://www.amazon.com/dp/B0166UBJX4) | B0166UBJX4 | 1 | $44.99 | $44.99 |
| [GASHER 1/4" NPT SS one-way check valve (2-pk, $13.99)](https://www.amazon.com/dp/B0FV2D2FFX) | B0FV2D2FFX — 1 of 2 per unit; half of pack price | 1 | $7.00 | $7.00 |
| [Lifevant 1/4" OD water tubing 32.8 ft + quick-connects](https://www.amazon.com/dp/B0DKCZ5W66) | B0DKCZ5W66 | 1 | $9.99 | $9.99 |
| [John Guest 1/4" OD × 1/8" NPT push-fit](https://www.amazon.com/dp/B07V6XKZG9) | B07V6XKZG9 | 1 | $5.00 | $5.00 |
| [John Guest PI1208S acetal bulkhead union, 1/4" QC](https://www.amazon.com/dp/B0C1F3QR7N) | B0C1F3QR7N | 1 | $11.49 | $11.49 |

## 4. CO2 subsystem

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Wellbom dual-gauge CO2 regulator, CGA-320, 0–120 PSI out / 150 PSI PRV](https://www.amazon.com/dp/B0G13P5PMY) | B0G13P5PMY | 1 | $44.99 | $44.99 |
| [5/16" ID beer CO2 line, 10 ft + clamps](https://www.amazon.com/dp/B0D1RB3TF6) | B0D1RB3TF6 | 1 | $12.59 | $12.59 |
| [DERPIPE 5/16" tube × 1/4" NPT push-to-connect (5-pk)](https://www.amazon.com/dp/B09LXVGPG7) | B09LXVGPG7 — **5/16" variant appears delisted; source replacement ASIN** | 1 pk | $10.71 | $10.71 |

## 5. Refrigeration (harvested compressor path)

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Frigidaire EFIC117-SS ice-maker donor (compressor/condenser/cap-tube/drier)](https://www.amazon.com/dp/B07PCZKG94) | B07PCZKG94 | 1 | $73.38 | $73.38 |
| [GOORY 1/4" OD × 50 ft ACR copper coil (evaporator)](https://www.amazon.com/dp/B0DKSW5VL9) | B0DKSW5VL9 | 1 | $63.99 | $63.99 |
| [Supco SUD8358 filter-drier, 1/4" sweat × cap-tube outlet, XH-9 molecular sieve, integrated Schrader access port](https://www.amazon.com/dp/B009AX2O5W) | B009AX2O5W — replaces factory drier after venting; 1/4" sweat inlet brazes to condenser outlet; cap-tube outlet accepts the factory capillary tube directly (no reducer needed); Schrader port provides vacuum + recharge access; XH-9 desiccant is hydrocarbon-compatible | 1 | $12.49 | $12.49 |
| [Teyleten 3.3 V relay module, opto-isolated, 10 A @ 250 VAC (5-pk)](https://www.amazon.com/dp/B07XGZSYJV) | B07XGZSYJV — compressor AC switching; ESP32 GPIO 14 drives input directly; 1 of 5 per unit | 1 (of 5 pk) | $2.60 | $2.60 |
| [HiLetgo DS18B20 waterproof 1-wire probe, 1 m SS sheath (5-pk)](https://www.amazon.com/dp/B00M1PM55K) | B00M1PM55K — 2 probes per unit: tank wall (compressor cycling setpoint) + evaporator coil (freeze-protect cutout); 2 of 5 per unit | 2 (of 5 pk) | $2.20 | $4.40 |
| [MXR IEC 60320 C14 panel-mount AC inlet, 10 A / 250 VAC (10-pk)](https://www.amazon.com/dp/B07DCXKNXQ) | B07DCXKNXQ — rear-panel mains inlet; accepts standard NEMA 5-15P-to-C13 line cord; 1 of 10 per unit | 1 (of 10 pk) | $0.65 | $0.65 |
| [Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed (6-pk)](https://www.amazon.com/dp/B08VS8D4WC) | B08VS8D4WC — ships in the box so the customer can plug the appliance into a standard US wall outlet; 1 of 6 per unit | 1 (of 6 pk) | $3.73 | $3.73 |
| [Enviro-Safe R-600a 3-pack + brass charging gauge](https://www.amazon.com/dp/B0CGG1WH1N) | B0CGG1WH1N — pure R-600a (not blend or n-butane); refills the sealed loop after venting factory charge; ~40 g per system × ~12 recharges per 3-can bundle; 1/12 of $67.99; brass gauge stays with tools (see purchases.md) | 1 | $5.67 | $5.67 |

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
| [Kamoer KPHM400-SW3B25 12V peristaltic pump](https://www.amazon.com/dp/B09MS6C91D) | B09MS6C91D | 2 | $32.55 | $65.10 |
| [Magnetic pogo pin connector, 2-pin (2 pair)](https://www.amazon.com/dp/B0CSX6ZQ1H) | B0CSX6ZQ1H — tool-free pump cartridge electrical connection, one pair per pump | 1 pk | $9.99 | $9.99 |
| [Beduan 12V 1/4" solenoid valve (NC)](https://www.amazon.com/dp/B07NWCQJK9) | B07NWCQJK9 — V-A/B/C/D/E/F/G/H/I/J/KA/KB per fluid-topology-manifold.mmd | 12 | $8.99 | $107.88 |
| [Platypus SoftBottle 1 L bladder](https://www.amazon.com/dp/B08PG3GMQ8) | B08PG3GMQ8 | 2 | $23.49 | $46.98 |
| [Platypus Hoser hydration tube kit](https://www.amazon.com/dp/B07N1T6LNW) | B07N1T6LNW | 1 | $24.95 | $24.95 |
| [Silicone tubing 1/8" ID × 1/4" OD](https://www.amazon.com/dp/B0BM4KQ6RT) | B0BM4KQ6RT — pump-head tube only (line runs are 1/4" LLDPE) | 1 | $12.99 | $12.99 |
| [Supply Depot BIB connector, 3/8" red (2-pk)](https://www.amazon.com/dp/B0DMFK9B6P) | B0DMFK9B6P — rear-panel commercial-syrup input | 1 pk | $19.99 | $19.99 |
| [MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4-pk)](https://www.amazon.com/dp/B0DMP77B6S) | B0DMP77B6S | 1 pk | $12.97 | $12.97 |
| [PureSec TWS1414 1/4" push-to-connect Y splitter (10-pk)](https://www.amazon.com/dp/B01N5I1ZJC) | B01N5I1ZJC — manifold Y-A/B/C/D/E/F/G/H/KA/KB per fluid-topology-manifold.mmd; food/water-safe plastic | 1 pk | $7.99 | $7.99 |

## 9. Dispensing

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Westbrass R2031-NL-62 8" Touch-Flo dispenser faucet, matte black](https://www.amazon.com/dp/B07KH285GJ) | B07KH285GJ — direct successor to retired A2031 SKU | 1 | $31.28 | $31.28 |
| [DIGITEN G3/8" Hall-effect flow sensor](https://www.amazon.com/dp/B07QQW4C7R) | B07QQW4C7R | 1 | $7.99 | $7.99 |

## 10. User interface

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [KRAUS garbage-disposal air-switch, matte black](https://www.amazon.com/dp/B096319GMV) | B096319GMV | 1 | $39.95 | $39.95 |

## 11. Wiring + fasteners

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Dupont Jumper Wires (120-pack)](https://www.amazon.com/dp/B0BRTJXND9) | B0BRTJXND9 | 1 pk | $5.97 | $5.97 |
| [Female Spade Crimp Terminals (60-pack)](https://www.amazon.com/dp/B0B9MZJ2ML) | B0B9MZJ2ML | 1 pk | $9.99 | $9.99 |
| [Male Quick-Disconnect Spade (100-pack)](https://www.amazon.com/dp/B01MZZGAJP) | B01MZZGAJP | 1 pk | $5.99 | $5.99 |
| [Zip Ties (200-pack)](https://www.amazon.com/dp/B0BC1VH4XB) | B0BC1VH4XB | 1 pk | $3.99 | $3.99 |

## 12. Required but not yet sourced

| Part | Notes | Est. $ |
|---|---|---:|
| FDC1004 capacitive level-sensor breakout | Tank level sensing per future.md §27 — not yet in purchases.md | $10.00 |

## Totals

| Section | $ |
|---|---:|
| 1. Controllers + electronics | $168.23 |
| 2. Carbonator vessel | $195.33 |
| 3. Water inlet | $144.33 |
| 4. CO2 subsystem | $68.29 |
| 5. Refrigeration | $166.91 |
| 6. Cold core insulation | $47.40 |
| 7. Printed parts (PETG) | $103.94 |
| 8. Flavor subsystem | $308.84 |
| 9. Dispensing | $39.27 |
| 10. UI | $39.95 |
| 11. Wiring | $25.94 |
| **Sourced + estimated subtotal** | **$1,308.43** |
| 12. Not yet sourced | $10.00 |
| **Projected total** | **$1,318.43** |

## External / user-supplied (not shipped)

- **5 lb CO2 tank** + refills (~$25/refill at welding/homebrew shops)
- **Flavor concentrate** — SodaStream or BIB syrup
- **Water filter** — user's choice of inline filter upstream of the appliance

## Notes / open questions

- **ChillWaves check valve B0DPLBYZB4 seat material** — future.md requires metal or PTFE seat (not elastomer); confirm or substitute.
- **Platypus 1 L vs 2 L** — future.md §53 specifies 1 L bladders. README's parts list shows 2 L. Using 1 L per future.md; revisit if cradle geometry forces larger.
- **Refrigeration charge** — Path A vents the factory R-600a charge and recharges from Enviro-Safe cans (§5); ~40 g per system × 12 recharges per 3-can bundle amortizes to ~$5.67/unit. No recovery equipment and no EPA 608 cert required (natural-refrigerant carveout).
