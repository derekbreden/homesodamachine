# Bill of Materials — One Consumer Unit

Per-unit parts for a single finished appliance built on the **custom-racetrack-vessel** path specified in [future.md](future.md): in-house fabricated 304 SS carbonator, compressor harvested from a countertop ice-maker, 3D-printed cold-core shells with spray-foam insulation, two 1 L Platypus bladders inside the cold core.

Prototype tools, fabrication equipment (welder, slip roll, shop press, dishing dies), donor parts consumed during teardown, duplicate SKUs, and consumables live in [parts-list.md](parts-list.md).

First-pass draft. Prices from resolved Amazon order history (parts-list.md) or direct-source quotes. Expect revisions.

## 1. Controllers + electronics

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [ESP32-DevKitC-32E](https://www.amazon.com/dp/B09MQJWQN2) | B09MQJWQN2 | 1 | $11.00 | $11.00 |
| [ESP32 DIN Rail Breakout Board](https://www.amazon.com/dp/B0BW4SJ5X2) | B0BW4SJ5X2 | 1 | $25.99 | $25.99 |
| [Waveshare RP2040 Round LCD 0.99"](https://www.amazon.com/dp/B0CTSPYND2) | B0CTSPYND2 | 1 | $23.99 | $23.99 |
| [Meshnology ESP32-S3 1.28" Rotary Display](https://www.amazon.com/dp/B0G5Q4LXVJ) | B0G5Q4LXVJ | 1 | $47.76 | $47.76 |
| [L298N Dual H-Bridge (4-pack)](https://www.amazon.com/dp/B0C5JCF5RS) | B0C5JCF5RS | 1 pk | $9.99 | $9.99 |
| [Mean Well LRS-200-12, 204 W / 12 V / 17 A, fanless](https://www.amazon.com/dp/B0874XQ82F) | B0874XQ82F | 1 | $28.00 | $28.00 |

## 2. Carbonator vessel (custom fabrication)

| Part | Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| SendCutSend-cut 304 SS blanks (body + 2 end caps) | orders SQ65E969 + SV07U813, half of combined total | 1 set | $52.86 | $52.86 |
| [1/4" NPT female weld bung, 304 SS stepped flange](https://www.amazon.com/dp/B07QNV8796) | B07QNV8796 | 4 | $7.99 | $31.96 |
| [4pc 1/4" NPT male hex nipple, 316 SS 5000 psi](https://www.amazon.com/dp/B0GD1QBLQ3) | B0GD1QBLQ3 — one nipple per bung for external plumbing | 1 pk | $15.99 | $15.99 |
| [Beduan 1/4" spiral cone atomization nozzle, 316 SS](https://www.amazon.com/dp/B07LGPD3GB) | B07LGPD3GB | 1 | $9.99 | $9.99 |
| [VALVENTO 1/4" OD 316 SS tube, 12" (5-pk)](https://www.amazon.com/dp/B0F6SYFK48) | B0F6SYFK48 — dip tube + internal rigid lines | 1 pk | $16.99 | $16.99 |
| [VALVENTO 1/4" OD compression × 1/4" NPT adapter (2-pk)](https://www.amazon.com/dp/B0DXZZBK7D) | B0DXZZBK7D | 1 pk | $11.99 | $11.99 |
| [Millrose 70894 Nickel Guard anti-seize PTFE tape](https://www.amazon.com/dp/B07C9ZV4PG) | B07C9ZV4PG — anti-seize for SS-into-SS NPT joints | 1 | $22.22 | $22.22 |
| Food-safe epoxy (MaxCLR A/B or equiv), tank interior coating | estimate | 1 kit | ~$40.00 | $40.00 |

## 3. Water inlet (tap → backflow → pump → atomizer)

| Part | ASIN / Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Multiplex 19-0897 ASSE 1022 backflow preventer](https://www.howdybrewer.com/products/multiplex-backflow-preventor-assembly-1022-3-8-npt-x-3-8-mfl) | howdybrewer | 1 | $38.99 | $38.99 |
| [Hooshing 3/8" flare × 1/4" FNPT adapter (2-pk)](https://www.amazon.com/dp/B0BNHVV6HT) | B0BNHVV6HT | 1 pk | $9.99 | $9.99 |
| [Sealproof 1/4" ID × 3/8" OD clear PVC, 10 ft](https://www.amazon.com/dp/B07D9DK94V) (vent telltale) | B07D9DK94V | 1 | $7.89 | $7.89 |
| [LOKMAN 304 SS worm-gear clamps, 10–16 mm (20-pk)](https://www.amazon.com/dp/B076Q7QVNM) | B076Q7QVNM | 1 pk | $8.99 | $8.99 |
| [SEAFLO 22-Series 12V 1.3 GPM 100 psi diaphragm pump](https://www.amazon.com/dp/B0166UBJX4) | B0166UBJX4 | 1 | $44.99 | $44.99 |
| [ChillWaves 304 SS 1/4" NPT external check valve](https://www.amazon.com/dp/B0DPLBYZB4) | B0DPLBYZB4 (verify metal/PTFE seat; replace if elastomer) | 1 | $16.99 | $16.99 |
| [Lifevant 1/4" OD water tubing 32.8 ft + quick-connects](https://www.amazon.com/dp/B0DKCZ5W66) | B0DKCZ5W66 | 1 | $9.99 | $9.99 |
| [John Guest 1/4" OD × 1/8" NPT push-fit](https://www.amazon.com/dp/B07V6XKZG9) | B07V6XKZG9 | 1 | $5.00 | $5.00 |
| [John Guest PI1208S acetal bulkhead union, 1/4" QC](https://www.amazon.com/dp/B0C1F3QR7N) | B0C1F3QR7N | 1 | $11.49 | $11.49 |

## 4. CO2 subsystem

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [TAPRITE E-T742 dual-gauge CO2 regulator, CGA-320](https://www.amazon.com/dp/B00L38DRD0) | B00L38DRD0 | 1 | $92.95 | $92.95 |
| [5/16" ID beer CO2 line, 10 ft + clamps](https://www.amazon.com/dp/B0D1RB3TF6) | B0D1RB3TF6 | 1 | $12.59 | $12.59 |
| [DERPIPE 5/16" tube × 1/4" NPT push-to-connect (5-pk)](https://www.amazon.com/dp/B09LXVGPG7) | B09LXVGPG7 — **5/16" variant appears delisted; source replacement ASIN** | 1 pk | $10.71 | $10.71 |

## 5. Refrigeration (harvested compressor path)

| Part | ASIN | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| [Frigidaire EFIC117-SS ice-maker donor (compressor/condenser/cap-tube/drier)](https://www.amazon.com/dp/B07PCZKG94) | B07PCZKG94 | 1 | $73.38 | $73.38 |
| [GOORY 1/4" OD × 50 ft ACR copper coil (evaporator)](https://www.amazon.com/dp/B0DKSW5VL9) | B0DKSW5VL9 | 1 | $63.99 | $63.99 |

Fallback path (UL/ETL-retail-friendly): RIGID DV1910E sealed refrigeration module (~$600 + 20–30% import duty). Not selected for this BOM.

## 6. Cold core insulation

| Part | Source | Qty | Unit $ | Line $ |
|---|---|---:|---:|---:|
| Froth-Pak two-part closed-cell spray polyurethane foam (inner + outer shells) | retail estimate | 1 kit | ~$150.00 | $150.00 |
| Thermal compound (evaporator coil ↔ vessel wall) | estimate | 1 tube | ~$10.00 | $10.00 |

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
| [Beduan 12V 1/4" solenoid valve (NC)](https://www.amazon.com/dp/B07NWCQJK9) | B07NWCQJK9 — V-A/B/C/D/E/F/G/H/I/J/KA/KB per fluid-topology-manifold.mmd | 12 | $8.99 | $107.88 |
| [Platypus SoftBottle 1 L bladder](https://www.amazon.com/dp/B08PG3GMQ8) | B08PG3GMQ8 | 2 | $23.49 | $46.98 |
| [Platypus Hoser hydration tube kit](https://www.amazon.com/dp/B07N1T6LNW) | B07N1T6LNW | 1 | $24.95 | $24.95 |
| [Silicone tubing 1/8" ID × 1/4" OD](https://www.amazon.com/dp/B0BM4KQ6RT) | B0BM4KQ6RT — pump heads + cosmetic runs | 1 | $12.99 | $12.99 |
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
| ASME-stamped PRV @ 100 psi, 1/4" NPT | Kunkle / Conbraco Section VIII — current pop-off B0D361X97X is non-ASME | $40.00 |
| 0–150 psi pressure transducer, 1/4" NPT | Headspace monitoring | $30.00 |
| FDC1004 capacitive level-sensor breakout | Tank level sensing per future.md §27 — not yet in parts-list | $10.00 |

## Totals

| Section | $ |
|---|---:|
| 1. Controllers + electronics | $146.73 |
| 2. Carbonator vessel | $202.00 |
| 3. Water inlet | $154.32 |
| 4. CO2 subsystem | $116.25 |
| 5. Refrigeration | $137.37 |
| 6. Cold core insulation | $160.00 |
| 7. Printed parts (PETG) | $103.94 |
| 8. Flavor subsystem | $298.85 |
| 9. Dispensing | $39.27 |
| 10. UI | $39.95 |
| 11. Wiring | $25.94 |
| **Sourced + estimated subtotal** | **$1,424.62** |
| 12. Not yet sourced | $80.00 |
| **Projected total** | **$1,504.62** |

## External / user-supplied (not shipped)

- **5 lb CO2 tank** + refills (~$25/refill at welding/homebrew shops)
- **Flavor concentrate** — SodaStream or BIB syrup
- **Water filter** — user's choice of inline filter upstream of the appliance

## Excluded from this BOM (and why)

- **Welding / fabrication tools** (slip roll, shop press, MIG welder, argon, dishing dies) — tools used to *build* the vessel, not shipped with unit
- **Waterdrop Waterfilter B085G9TZ4L** — user supplies their own
- **7 mm momentary pushbuttons B0F43GYWJ6** — not in final consumer design
- **Neodymium magnets B0BQ3LPGZ1** — from a shelved air-in-system exploration
- **EDGELEC LEDs B07PVVL2S6** — superseded by RP2040 display
- **Laminate shelf + wood screws** — prototype mounting panel, replaced by final enclosure
- **Syrup 4-packs** — consumable, not product
- **Klein crimper, USB flash cables** — assembly/dev tools, not product
- **EPA 608 Type I certification** (~$25 online exam) — required to do refrigeration harvest, not a part
- **RIGID DV1910E** — refrigeration fallback path, not selected
- **Westbrass D203 6" faucet B01MZ6JPXW** — duplicate of 8" variant; one ships

## Notes / open questions

- **ChillWaves check valve B0DPLBYZB4 seat material** — future.md requires metal or PTFE seat (not elastomer); confirm or substitute.
- **Platypus 1 L vs 2 L** — future.md §53 specifies 1 L bladders. README's parts list shows 2 L. Using 1 L per future.md; revisit if cradle geometry forces larger.
- **Refrigeration charge** — ice-maker donor path assumes R-134a recovery/recharge; cost excludes refrigerant loss if harvest fails and a top-up is needed.
