# Tools

Active tools in service for the project — fabrication equipment, bench instruments, printers, lasers, capture gear. Single-asset, amortized across many units rather than per-unit-allocated.

This is a **view** over [purchases.md](/hardware/ledger/purchases.md), with tool-specific metadata that doesn't belong in the buy ledger: working envelopes, capacities, manufacturer references, calibration notes. For the actual purchase event (date, vendor, $$), follow the §N reference back to purchases.md.

For per-unit BOM parts, see [bom.md](/hardware/ledger/bom.md). For non-BOM/non-tool inventory (consumables, spares, abandoned parts, diagnostic purchases, donor units, fab fixtures), see [inventory.md](/hardware/ledger/inventory.md).

---

## Vessel fabrication

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **VEVOR Slip Roll Machine** | [B0DZP1VBZY](https://www.amazon.com/dp/B0DZP1VBZY), [purchases.md §1](/hardware/ledger/purchases.md) | 24" forming width, 16 ga capacity. Plan-B (racetrack) body forming; idle since plan A 316L round-tube pivot. | [$235.94](T_SLIP_ROLL) |
| **VEVOR 12-ton Hydraulic Shop Press** | [B0BZ7YY3CP](https://www.amazon.com/dp/B0BZ7YY3CP), [purchases.md §1](/hardware/ledger/purchases.md) | For racetrack end-cap dishing dies (plan B); idle since pivot. | [$155.50](T_SHOP_PRESS) |
| **WEN 4208T benchtop drill press** | [B08ZVT5JKC](https://www.amazon.com/dp/B08ZVT5JKC), [purchases.md §1](/hardware/ledger/purchases.md) | 2.3 A 8" 5-speed, drill + tap station for 316 SS end-cap plates. | [$111.54](T_DRILL_PRESS) |
| **Drill America DWT adjustable tap wrench** | [B00DMEYTLW](https://www.amazon.com/dp/B00DMEYTLW), [purchases.md §1](/hardware/ledger/purchases.md) | 1/4"–1-1/8" tap capacity. Production tap driver for the 40-hole vessel batch. | [$33.02](T_TAP_WRENCH) |
| **LingGan 1/4-18 NPT M35 cobalt pipe tap** | [B0D7HM5R3C](https://www.amazon.com/dp/B0D7HM5R3C), [purchases.md §1](/hardware/ledger/purchases.md) | M35 (5% cobalt HSS-E), TiN-coated, 4-flute taper chamfer. Production tap for the 40-hole 316L SS end-cap run. Use with Tap Magic EP-Xtra cutting fluid. | [$13.93](T_M35_TAP) |
| **Brown & Sharpe spring-loaded tap guide** | [B005317ZMC](https://www.amazon.com/dp/B005317ZMC), [purchases.md §1](/hardware/ledger/purchases.md) | 1/2" hardened shank; keeps the pipe tap square while starting threads under the drill press. | [$27.45](T_TAP_GUIDE) |
| **Mollom 124 mm bi-metal hole saw + arbor** | [B0BZQ4J5B1](https://www.amazon.com/dp/B0BZQ4J5B1), [purchases.md §1](/hardware/ledger/purchases.md) | HSS M42, 4-7/8" cut; near-5" fixture pockets and end-cap disc cuts. | [$19.19](T_HOLE_SAW) |
| **Drill Hulk 9/64" M35 cobalt twist drill bits (12-pk)** | [B07XNNNC5Y](https://www.amazon.com/dp/B07XNNNC5Y), [purchases.md §1](/hardware/ledger/purchases.md) | M35 (5% cobalt), 135° split point, jobber length. Blind level-sensing rod register (0.10" deep) in the 316 SS end-cap inside face; slip-fit for the 1/8" float rod. Consumable, 12-pack covers the 20-cap batch. | [$18.43](T_REGISTER_BIT) |
| **WEN BA4555 benchtop metal band saw** | [B09XWQCNGT](https://www.amazon.com/dp/B09XWQCNGT), [purchases.md §1](/hardware/ledger/purchases.md) | 5" round / 5×4-7/8" rect capacity, 0–60° miter vise, variable 125–260 FPM, 56-1/2" blade. Horizontal cutoff with vise + length stop — square, repeatable cuts of the 1/8" 316L level-sensing rods (3 lengths: carbonator + flavor reservoir + lite reservoir pocket). Blade: Imachinist 24 TPI M42 bi-metal ([B0B7GDTX9H](https://www.amazon.com/dp/B0B7GDTX9H)). | [$362.73](T_BANDSAW) |
| **Bosch DSB1013 Daredevil spade bit** | [B001NGPAA0](https://www.amazon.com/dp/B001NGPAA0), [purchases.md §1](/hardware/ledger/purchases.md) | 1" × 6", for 1" through-holes in fixture stock. | [$5.35](T_SPADE_BIT) |
| **MOTOKU 38 mm round die handle** | [B073ZX58PH](https://www.amazon.com/dp/B073ZX58PH), [purchases.md §1](/hardware/ledger/purchases.md) | Companion to Drill America die kit for chasing external threads on test fittings. | [$15.00](T_DIE_HANDLE) |

## Hydro / pressure testing

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **BEAMNOVA hydrostatic test pump** | [B07T45XTD1](https://www.amazon.com/dp/B07T45XTD1), [purchases.md §1](/hardware/ledger/purchases.md) | 0–726 PSI / 0–5 MPa, 3.17 gal reservoir, 4.43 ft × 1/4" hydraulic hose with 1/2" F gasket-swivel end. Copper pump body + check valve. 180 PSI vessel hydro test sits at ~25 % of scale. | [$93.30](T_HYDRO_PUMP) |
| **SENCTRL 0–200 PSI glycerin-filled gauge** | [B0BCHMQLFB](https://www.amazon.com/dp/B0BCHMQLFB), [purchases.md §1](/hardware/ledger/purchases.md) | 2.5" dial, 1/4" NPT lower mount, SS case. Leaves on a vessel port across hour-scale leak soaks for fine-resolution drift. | [$10.72](T_GAUGE) |
| **ChillWaves brass 1/4" NPT outer-hex plugs** | [B0C4LP4B3D](https://www.amazon.com/dp/B0C4LP4B3D), [purchases.md §1](/hardware/ledger/purchases.md) | 12-pack, 1200 PSI rated. Dead-head plugs for unused vessel ports during pressure testing. | [$11.79](T_DEADHEAD_PLUGS) |
| **Milton 727 M-STYLE 1/4" MNPT air plug** | [B000PDWI4S](https://www.amazon.com/dp/B000PDWI4S), [purchases.md §1](/hardware/ledger/purchases.md) | 10-pack, alloy steel. Post-validation pneumatic-leak-check rig for vessels that already passed hydro. Mates with the DeWalt DWFP55130 / Husky 41257HOM coupler at the hose end. | [$15.02](T_MSTYLE_PLUG) |
| **KOOTANS 1/2" × 1/4" NPT hex nipple** | [B07P7ZRZMD](https://www.amazon.com/dp/B07P7ZRZMD), [purchases.md §1](/hardware/ledger/purchases.md) | 4-pack brass. Adapter mating the BEAMNOVA 1/2" F gasket-swivel hose end to a vessel's 1/4" NPT F port. | [$12.86](T_HEX_NIPPLE) |

## Welding

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **XLaserlab X1 Pro** | XLaserlab order #XLaserlab3271, [purchases.md §16](/hardware/ledger/purchases.md) | Handheld 3-in-1 laser welder / cleaner / cutter. Ultimate Pack with single wire feeder. Production weld station for 316L pressure-vessel end-cap-to-tube joins. Vendor: xlaserlab.com. | [$3,899.00](T_X1PRO) |
| **Airgas argon size-80 cylinder + RHP400 regulator** | Airgas #8162013342, [purchases.md §1](/hardware/ledger/purchases.md), [B008HQ6GXO](https://www.amazon.com/dp/B008HQ6GXO) | Owned cylinder (not exchange/lease), CGA-580 fitting. Shielding gas for X1 Pro and braze-loop argon purge. Refill via Airgas Lincoln NE branch. | [$399.31](T_ARGON_CYL) |
| **RX Weld argon regulator / flowmeter** | [B08P5BNHBX](https://www.amazon.com/dp/B08P5BNHBX), [purchases.md §1](/hardware/ledger/purchases.md) | Argon delivery for welding (separate from the RHP400 used for refrigeration brazing purge). | [$31.09](T_RXWELD) |
| **Weldpro 3-Tier Welding Cart** | [B08G5CW3DY](https://www.amazon.com/dp/B08G5CW3DY), [purchases.md §1](/hardware/ledger/purchases.md) | Mobile cart for the X1 Pro welder + argon cylinder. | [$193.04](T_WELD_CART) |
| **Strong Hand magnetic V-pads kit** | [B00JXDSVA6](https://www.amazon.com/dp/B00JXDSVA6), [purchases.md §1](/hardware/ledger/purchases.md) | Welding magnets / clamping aids. | [$29.21](T_MAGNETS) |
| **MAXMAN SS wire brush set** | [B08L7RXVG5](https://www.amazon.com/dp/B08L7RXVG5), [purchases.md §1](/hardware/ledger/purchases.md) | Joint prep on stainless. | [$12.22](T_BRUSH) |
| **YTKavq C110 copper bar (1/4" × 2" × 12")** | [B0DR2PX6TT](https://www.amazon.com/dp/B0DR2PX6TT), [purchases.md §1](/hardware/ledger/purchases.md) | Soft-annealed pure copper; weld backer / heat-sink chill bar. | [$42.89](T_COPPER_BAR) |
| **Caiman premium goat-grain TIG gloves** | [B07T6VLSK3](https://www.amazon.com/dp/B07T6VLSK3) + [B07T1NYXHM](https://www.amazon.com/dp/B07T1NYXHM), [purchases.md §1](/hardware/ledger/purchases.md) | PPE for the laser welder, two pair (variant ASINs). | [$46.10](T_GLOVES) |

## Refrigeration assembly

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **Bernzomatic TS8000 + MAP-Pro 3-can kit** | [B0BPMVTJ1R](https://www.amazon.com/dp/B0BPMVTJ1R), [purchases.md §6](/hardware/ledger/purchases.md) | High-intensity torch head; reaches the ~800 °C (1300–1500 °F) brazing range needed to flow BCuP-5 (liquidus 802 °C). | [$117.96](T_TORCH) |
| **Orion Motor Tech 4 CFM vacuum pump** | [B08P1WRZ1S](https://www.amazon.com/dp/B08P1WRZ1S), [purchases.md §6](/hardware/ledger/purchases.md) | 1/3 HP single-stage, 150 µ ultimate. Refrigerant-loop evacuation post-braze. | [$78.28](T_VAC_PUMP) |
| **Orion Motor Tech HVAC manifold gauge set** | [B07CZB2SHZ](https://www.amazon.com/dp/B07CZB2SHZ), [purchases.md §6](/hardware/ledger/purchases.md) | 1/4" SAE. Paired with the vacuum pump for evacuation + charge. | [$48.24](T_MANIFOLD) |
| **Smart Weigh Pro digital scale** | [B00IZ1YHZK](https://www.amazon.com/dp/B00IZ1YHZK), [purchases.md §6](/hardware/ledger/purchases.md) | 2000 g × 0.1 g. R-600a mass-metered recharge by Δ-mass of the can. Well under the ±1 g recharge tolerance. | [$19.25](T_SCALE) |
| **Toptes PT520A leak detector** | [B0BTM3G8DK](https://www.amazon.com/dp/B0BTM3G8DK), [purchases.md §6](/hardware/ledger/purchases.md) | Refrigerant / hydrocarbon gas leak detector. Post-braze joint inspection. | [$42.89](T_LEAK_DET) |
| **Mastercool 70025 cap-tube cutter** | [B00NY1YHHE](https://www.amazon.com/dp/B00NY1YHHE), [purchases.md §6](/hardware/ledger/purchases.md) | Severs 0.042"/0.050" capillary tubing without crushing the bore. | [$15.74](T_CAP_CUTTER) |
| **RIDGID 31622 Model 150 tubing cutter** | [B0009W6T8G](https://www.amazon.com/dp/B0009W6T8G), [purchases.md §6](/hardware/ledger/purchases.md) | 1/8"–1-1/8" constant-swing. Square cuts on 1/4" ACR before flaring/brazing. | [$34.31](T_TUBE_CUTTER) |
| **RIDGID 23332 Model 345 flaring tool** | [B000X4K9KO](https://www.amazon.com/dp/B000X4K9KO), [purchases.md §6](/hardware/ledger/purchases.md) | 45° SAE. Leak-tight flares on 1/4" ACR for manifold/Schrader connections. | [$107.24](T_FLARE_TOOL) |
| **Klein Tools 51006 tube bender** | [B0DPQX17WM](https://www.amazon.com/dp/B0DPQX17WM), [purchases.md §6](/hardware/ledger/purchases.md) | 3-in-1 (1/4 / 5/16 / 3/8 OD). Forming the evaporator coil around the carbonator tank. | [$23.57](T_TUBE_BENDER) |
| **Wisscool 1/4" tube straightener** | [B0F6BPTW3T](https://www.amazon.com/dp/B0F6BPTW3T), [purchases.md §6](/hardware/ledger/purchases.md) | Handheld; de-coils 1/4" ACR before bending. | [$26.80](T_STRAIGHTENER) |
| **Knipex 86 01 180 Pliers Wrench** | [B07YLFLSJW](https://www.amazon.com/dp/B07YLFLSJW), [purchases.md §6](/hardware/ledger/purchases.md) | 7.25" smooth parallel-jaw. Pinch-swages 1/4" ACR coil inlet down onto 0.031" cap tube via progressive 60° rotation collapse. | [$57.06](T_PLIERS_WRENCH) |
| **Uniweld RHP400 CGA-580 regulator** | [B008HQ6GXO](https://www.amazon.com/dp/B008HQ6GXO), [purchases.md §6](/hardware/ledger/purchases.md) | 1/4" male flare, 0–400 psi delivery. Swaps onto the existing argon cylinder for the brazing-loop purge — no separate nitrogen cylinder needed. | [$96.76](T_RHP400) |

## Soldering & electronics bench

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **Hakko FX-888D soldering station** | [B0D4DJW54S](https://www.amazon.com/dp/B0D4DJW54S), [purchases.md §14](/hardware/ledger/purchases.md) | 70 W, adjustable 120–899 °F. Primary iron for through-hole + wire-to-pad work. Tips: T18-D08/D12/D16 chisels + a VECO-T 10-tip T18 assortment (K knife for connector-row drag-soldering, D32/S3 high-mass for desoldering pre-soldered headers, C2/C5 bevels, plus spares) added for the Dupont→JST connector rework + heat-set insert tip kit (M2–M8). | [$130.27](T_HAKKO) |
| **Hakko FR-301 desoldering tool** | [B07BKSLLG9](https://www.amazon.com/dp/B07BKSLLG9), [purchases.md §14](/hardware/ledger/purchases.md) | 140 W self-contained desoldering gun — heated hollow nozzle + motorized vacuum, trigger-actuated, 110 V. Clears solder-blocked plated through-holes in one pull; through-hole connector rework (Dupont→JST header migration). | [$225.20](T_FR301) |
| **KOTTO solder fume extractor** | [B07VWDN29F](https://www.amazon.com/dp/B07VWDN29F), [purchases.md §14](/hardware/ledger/purchases.md) | 60 W, activated-carbon filter. | [$42.89](T_FUME_EXT) |
| **AstroAI digital multimeter** | [B071JL6LLL](https://www.amazon.com/dp/B071JL6LLL), [purchases.md §14](/hardware/ledger/purchases.md) | 2000-count auto-ranging continuity / V / Ω meter. | [$32.16](T_DMM) |
| **Klein 11063W self-adjusting wire stripper** | [B00CXKOEQ6](https://www.amazon.com/dp/B00CXKOEQ6), [purchases.md §14](/hardware/ledger/purchases.md) | AWG 10–20, primary stripper for 18–24 AWG hookup wire. | [$24.62](T_STRIPPER) |
| **Kaisi heat-resistant silicone mat** | [B07DGVRYL3](https://www.amazon.com/dp/B07DGVRYL3), [purchases.md §14](/hardware/ledger/purchases.md) | 17.7" × 11.8" work surface, magnetic section for screws. | [$12.86](T_MAT) |
| **AORAEM helping-hands w/ magnifier** | [B08DNMT96W](https://www.amazon.com/dp/B08DNMT96W), [purchases.md §14](/hardware/ledger/purchases.md) | 4 flex arms; work holder for wire-to-pad soldering. | [$9.64](T_HELPING_HANDS) |
| **QWORK mini heat gun** | [B09NDCCW29](https://www.amazon.com/dp/B09NDCCW29), [purchases.md §14](/hardware/ledger/purchases.md) | 300 W / 200–450 °C. Heat-shrink activation, light rework. | [$9.62](T_HEAT_GUN) |
| **iFixit precision tweezers set** | [B079K874CQ](https://www.amazon.com/dp/B079K874CQ), [purchases.md §14](/hardware/ledger/purchases.md) | Extra-fine + angled + blunt, ESD coating. Board-level rework, pin extraction, BOOT-pad bridging. | [$12.82](T_TWEEZERS) |
| **KATA micro flush cutters (2-pack)** | [B0BBML9M2V](https://www.amazon.com/dp/B0BBML9M2V), [purchases.md §14](/hardware/ledger/purchases.md) | Precision side cutters: header-strip cutting, lead trimming. Shared with 3D-printing post-processing. | [$8.89](T_FLUSH_CUTTERS) |
| **Haisstronica ratchet crimper** | [B08F3JKDD3](https://www.amazon.com/dp/B08F3JKDD3), [purchases.md §9](/hardware/ledger/purchases.md) | AWG 22–10. | [—](T_CRIMPER) |
| **Taiss Dupont crimp kit + SN-28B** | [B0B11RLGDZ](https://www.amazon.com/dp/B0B11RLGDZ), [purchases.md §9](/hardware/ledger/purchases.md) | Dupont connector terminal crimping. | [$23.58](T_DUPONT_KIT) |
| **iCrimp SN-2549 ratcheting crimper** | [B01N4L8QMW](https://www.amazon.com/dp/B01N4L8QMW), [purchases.md §9](/hardware/ledger/purchases.md) | AWG 28–18 open-barrel ratcheting crimper. Dedicated nests for JST PH 2.0 / ZH 1.5 / XH 2.5 / VH 3.96 + Dupont 2.54 — crimps the JST-PH 2.0 terminals on the MCP23017 I²C link, which the SN-28B's nests fit only loosely. | [$23.91](T_SN2549) |
| **Preciva ferrule crimping tool, AWG 28–5** | [B0DS622GKN](https://www.amazon.com/dp/B0DS622GKN), [purchases.md §9](/hardware/ledger/purchases.md) | Quad-indent (square) ratcheting crimp for bootlace / cord-end wire ferrules, 0.08–16 mm² (28–5 AWG) — the conductor landings into the Wago 221 lever nuts and screw terminals. Kit bundles 950 insulated ferrules (the consumable side lives in [bom.md §11](/hardware/ledger/bom.md)). | $48.25 |
| **P3 Kill-A-Watt P4400 power meter** | [B00009MDBU](https://www.amazon.com/dp/B00009MDBU), [purchases.md §9](/hardware/ledger/purchases.md) | Bench AC power measurement. | [$34.31](T_KILL_A_WATT) |
| **DSD TECH SH-U09B3 USB-C to TTL adapter** | [B09KXT6W46](https://www.amazon.com/dp/B09KXT6W46), [purchases.md §14](/hardware/ledger/purchases.md) | CP2102N, 3 Mbps, 3.3 V logic, 5 V VCC out. ROM-bootloader flashing of the faucet display S3 over UART0 (GPIO 43/44). | [$10.71](T_USB_UART) |
| **3M Virtua CCS safety glasses** | [B00AEXKR4C](https://www.amazon.com/dp/B00AEXKR4C), [purchases.md §14](/hardware/ledger/purchases.md) | PPE for soldering + heat-gun work. | [$12.43](T_GLASSES) |

## 3D printing equipment

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **Bambu Lab H2C (×2)** | Bambu Lab direct orders us712460111015776257 + us728027710789775361, [purchases.md §15](/hardware/ledger/purchases.md) | Production printers, AMS Combo bundles. Founding unit (Mar 22 2026) + second unit (May 4 2026 — ordered after the original's right-side Induction Heating Assembly was damaged during PET-CF clog troubleshooting). | [$4,971.93](T_H2C) |
| **Bambu Lab AMS HT (×2)** | Bambu order us717877837343809537, [purchases.md §15](/hardware/ledger/purchases.md) | High-temperature AMS expansion units. | [$278.00](T_AMS_HT) |
| **Bambu Lab AMS 2 Pro** | Bambu order us718417332286169089, [purchases.md §15](/hardware/ledger/purchases.md) | Second AMS variant. | [$331.99](T_AMS2PRO) |
| **Bambu Vision Encoder / H2 Series** | Founding bundle, [purchases.md §15](/hardware/ledger/purchases.md) | Print monitoring camera. | [$78.75](T_VISION) |
| **Bambu Engineering Plate / H2C** | Founding bundle, [purchases.md §15](/hardware/ledger/purchases.md) | Build plate for engineering filaments. | [$49.49](T_ENG_PLATE) |
| **SUNLU E2 filament dryer** | [B0F5PMMXKD](https://www.amazon.com/dp/B0F5PMMXKD), [purchases.md §13](/hardware/ledger/purchases.md) | Dual-chamber, **110 °C ceiling**, 500 W PTC. Engineering-CF tier: Bambu PET-CF (80 °C × 8–12 h), Polymaker Fiberon PET-CF17 (100 °C × 10 h), Bambu PA-CF / FR-ABS. | [$321.74](T_DRYER_E2) |
| **SUNLU S4 filament dryer** | [B0CQJMV71Z](https://www.amazon.com/dp/B0CQJMV71Z), [purchases.md §13](/hardware/ledger/purchases.md) | 4-spool capacity, **70 °C ceiling**, 350 W PTC, 3 circulation fans. Bulk drying of PLA / PETG / PETG-CF / PETG food-grade stock — frees the E2 for the engineering-CF tier. | [$125.47](T_DRYER_S4) |
| **Polymaker PolyDryer Box ×4** | [B0FHPS82YG](https://www.amazon.com/dp/B0FHPS82YG), [purchases.md §13](/hardware/ledger/purchases.md) | Sealed storage boxes for moisture protection. Compatible with PolyDryer heater base if added later. | [$117.96](T_POLYDRYER) |
| **Hotend stock** | various Bambu + DUROZZLE orders, [purchases.md §13 / §15](/hardware/ledger/purchases.md) | Right-side (Induction) HS: 0.2 SS, 0.4 ×4 HS, 0.6 HS, 0.8 HS, 0.8 HF HS. Left-side (Standard): 0.4 HS ×2, 0.6 TC SF (Bambu), 0.6 TC + 0.6 Diamond PCD (DUROZZLE), 0.8 TC HF. | [$517.09](T_HOTENDS) |
| **4-in-1 PTFE Adapter II (×2)** | Bambu orders us717877837343809537 + us718417332286169089, [purchases.md §15](/hardware/ledger/purchases.md) | Multi-spool feed adapter. | [$15.98](T_PTFE_ADAPTER) |

## Shop / bench infrastructure

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **VEVOR adjustable 48" workbench (×2)** | [B0FCD13KKQ](https://www.amazon.com/dp/B0FCD13KKQ), [purchases.md §12](/hardware/ledger/purchases.md) | Power outlet, wheels, pegboard, 2000 lb load each. | [$345.28](T_WORKBENCH) |
| **NEIKO 01407A digital caliper** | [B000GSLKIW](https://www.amazon.com/dp/B000GSLKIW), [purchases.md §12](/hardware/ledger/purchases.md) | 0–6", stainless, inch/fraction/mm LCD. Bench metrology for CAD reference measurements. | [$27.23](T_CALIPER) |
| **Ultra Duster canned air (10 oz, 4-pack)** | [B07JRBR1MM](https://www.amazon.com/dp/B07JRBR1MM), [purchases.md §1](/hardware/ledger/purchases.md) | Chip blowoff for freshly-tapped NPT threads; general shop use. Consumable. | [$24.51](T_DUSTER) |
| **DeWalt DWFP55130 (200 PSI compressor)** | owned, predates project, *not on ledger* | Air supply for the Milton 727 post-validation pneumatic leak check. | [—](T_DEWALT) |
| **Husky 41257HOM Tru-Match coupler kit** | owned, predates project, *not on ledger* | 19-pc accessory kit; hose-end coupler mating to Milton M-style plugs. | [—](T_HUSKY) |

## Video / marketing capture

| Tool | Source | Notes | $ |
|---|---|---|---:|
| **SanDisk Ultra Fit USB 3.1 256 GB** | [B07857Y17V](https://www.amazon.com/dp/B07857Y17V), [purchases.md §19](/hardware/ledger/purchases.md) | Plugs into H2C front USB for on-device per-print timelapse capture. 256 GB holds dozens of full-print MP4s. | [$45.41](T_SANDISK) |

## Tools total

Total acquired tooling: **[$14,327.47](TOOLS_TOTAL)**

## Open items

- Tools section is current as of the 2026-05-20 reorg; the full per-line audit of every purchases.md row hasn't been done — items not yet listed here either belong in this file (and should be added) or in [bom.md](/hardware/ledger/bom.md) / [inventory.md](/hardware/ledger/inventory.md). When in doubt, the underlying purchases.md row is the source of truth.
- Manufacturer-PDF / spec-sheet links are not yet captured per-tool — add as relevant for the tools whose envelopes constrain design (X1 Pro power range, H2C bed dimensions, etc.).

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_tools_totals.py`
