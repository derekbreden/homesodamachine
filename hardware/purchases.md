# Purchases

Capital expenditure ledger for the soda-flavor-injector project. Scope: **2026 calendar year only** (Jan 1 → Jun 2, 2026 YTD). Compiled from Amazon order history, direct-from-vendor receipts (Bambu Lab, XLaserlab, Namecheap), and capitalized contract labor (Anthropic / Claude API + subscription for AI-assisted engineering — CAD, firmware, electrical design, documentation, procurement research). Every item is either already in-hand (**ACQUIRED**), placed but not yet arrived (**ON-ORDER**), or identified as a planned purchase (**LIKELY-TO-BUY**).

This is the **purchase ledger** — every buy event, kept for tax records and complete sourcing history. It is not a per-unit bill of materials. Views over this ledger live in sibling files:

- [bom.md](bom.md) — parts allocated per-unit in the current production design (per-unit qty, unit-cost math).
- [tools.md](tools.md) — active tools with tool-specific metadata (working envelopes, capacities, manufacturer references).
- [inventory.md](inventory.md) — current-state inventory for items not in bom.md or tools.md (consumables, spares, abandoned parts, diagnostic purchases, donor units, fab fixtures, aggregated counts).

Each row below is a purchase event; the same SKU may appear as multiple rows if reordered. Capitalized contract labor (Anthropic / Claude API) is recorded here in §18 as cash outlays.

Price figures on bundled rows reflect the shipment total, not the per-item unit price. Only cash outlays (including contracted labor via Anthropic) are on this ledger.

---

## 1. Pressure vessel / carbonator fabrication

Stainless pressure-vessel fabrication: 316 SS round-tube body + 1/4" laser-cut 316 SS end-cap plates (direct-tapped 1/4" NPT), welding/forming tools, drill-tap tooling, and the hydro/pressure-test rig. Racetrack 304 SS stock is retained as fallback (see [inventory.md](inventory.md)).

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| VEVOR Slip Roll Machine, 24" forming width, 16 ga | [B0DZP1VBZY](https://www.amazon.com/dp/B0DZP1VBZY) | 1 | $235.94 | ACQUIRED |
| VEVOR 12-ton Hydraulic Shop Press (for dishing dies) | [B0BZ7YY3CP](https://www.amazon.com/dp/B0BZ7YY3CP) | 1 | $155.50 | ACQUIRED |
| Weldpro 3-Tier Welding Cart | [B08G5CW3DY](https://www.amazon.com/dp/B08G5CW3DY) | 1 | $179.99 | ACQUIRED |
| Blue Demon ER308L .030 stainless MIG wire, 2 lb | [B0025Q2HIU](https://www.amazon.com/dp/B0025Q2HIU) | 1 | $22.33 | ACQUIRED |
| RX Weld argon regulator / flowmeter | [B08P5BNHBX](https://www.amazon.com/dp/B08P5BNHBX) | 1 | $28.99 | ACQUIRED |
| Airgas #8162013342 — argon size-80 cylinder, CGA-580 (CY-AR 80) | airgas.com (Lincoln NE) | 1 | $399.31 | ACQUIRED |
| Airgas #8162013342 — argon fill, 85 SCF (AR 80) | airgas.com (Lincoln NE) | 1 | $75.20 | ACQUIRED |
| Strong Hand magnetic V-pads welding magnet kit | [B00JXDSVA6](https://www.amazon.com/dp/B00JXDSVA6) | 1 | $27.24 | ACQUIRED |
| MAXMAN stainless steel wire brush set | [B08L7RXVG5](https://www.amazon.com/dp/B08L7RXVG5) | 1 | $11.39 | ACQUIRED |
| 1/4" NPT female weld bung, 304 SS stepped flange | [B07QNV8796](https://www.amazon.com/dp/B07QNV8796) | 1 pk | $7.99 | ACQUIRED |
| 4pc 1/4" NPT male hex nipple, 316 SS 5000 psi | [B0GD1QBLQ3](https://www.amazon.com/dp/B0GD1QBLQ3) | 1 pk | $15.19 | ACQUIRED |
| Millrose PTFE thread seal tape | [B07C9ZV4PG](https://www.amazon.com/dp/B07C9ZV4PG) | 1 | $20.07 | ACQUIRED |
| Viva Doria 100% pure food-grade citric acid, fine grain, 2 lb | [B0C5NQM8S1](https://www.amazon.com/dp/B0C5NQM8S1) | 1 | $9.99 | ACQUIRED |
| Cambro 6 QT square polycarbonate food container | [B001BZEQ44](https://www.amazon.com/dp/B001BZEQ44) | 1 | $20.00 | ACQUIRED |
| findmall ER308L .035 MIG wire, 10 lb spool | [B0C52XQB39](https://www.amazon.com/dp/B0C52XQB39) | 1 | $90.68 | ACQUIRED |
| PGN ER308L .030 MIG wire, 10 lb spool | [B09WRZDBPN](https://www.amazon.com/dp/B09WRZDBPN) | 1 | — | CANCELLED |
| STARTECHWELD ER316L .030 MIG wire, 10 lb spool, 8" OD / 2" center bore | [B09BKFBXT9](https://www.amazon.com/dp/B09BKFBXT9) | 1 | $129.50 | ACQUIRED |
| Caiman premium goat-grain TIG / multi-task welding gloves | [B07T6VLSK3](https://www.amazon.com/dp/B07T6VLSK3) | 1 | $23.05 | ACQUIRED |
| Caiman premium goat-grain TIG welding gloves | [B07T1NYXHM](https://www.amazon.com/dp/B07T1NYXHM) | 1 | $23.05 | ACQUIRED |
| YTKavq 1/4" × 2" × 12" C110 pure copper flat bar, soft-annealed | [B0DR2PX6TT](https://www.amazon.com/dp/B0DR2PX6TT) | 1 | $42.89 | MISSING (delivered-but-empty 2026-04-23; no refund pursued) |
| YTKavq 1/4" × 2" × 12" C110 pure copper flat bar | [B0DR2PX6TT](https://www.amazon.com/dp/B0DR2PX6TT) | 1 | $42.89 | ACQUIRED |
| 304 SS 4" × 6" × 1/16" (16 ga / 1.5 mm) sheet, 2-pk | [B0DFXXQZD3](https://www.amazon.com/dp/B0DFXXQZD3) | 3 pk | $48.24 | ACQUIRED |
| 304 SS 4" × 4" × 0.04" (19 ga / 1 mm) sheet, 4 pc | [B0C5LWVLCD](https://www.amazon.com/dp/B0C5LWVLCD) | 1 | $13.93 | ACQUIRED |
| Drill America 1/4" NPT HSS pipe tap + 1-1/2" OD round die kit | [B0DXN1LDKT](https://www.amazon.com/dp/B0DXN1LDKT) | 1 | $18.80 | ACQUIRED |
| MOTOKU 38 mm / 1.5" OD heavy-duty round die handle | [B073ZX58PH](https://www.amazon.com/dp/B073ZX58PH) | 1 | $13.99 | ACQUIRED |
| Tap Magic EP-Xtra pipe-tap cutting fluid, 16 oz (size variant on listing B00DHMHSGM) | [B00DHMHSGM](https://www.amazon.com/dp/B00DHMHSGM) | 1 | $17.01 | ACQUIRED |
| WEN 4208T 2.3 A 8" 5-speed benchtop drill press | [B08ZVT5JKC](https://www.amazon.com/dp/B08ZVT5JKC) | 1 | $111.54 | ACQUIRED |
| Drill America 1/4"–1-1/8" tap-capacity adjustable tap wrench, DWT series | [B00DMEYTLW](https://www.amazon.com/dp/B00DMEYTLW) | 1 | $33.02 | ACQUIRED |
| Drill America DWT64006 Qualtech HSS pipe tap, 1/4"-18 NPT | [B01DZD1Y9Y](https://www.amazon.com/dp/B01DZD1Y9Y) | 1 | $10.54 | ACQUIRED |
| LingGan 1/4-18 NPT M35 cobalt steel pipe tap, TiN-coated | [B0D7HM5R3C](https://www.amazon.com/dp/B0D7HM5R3C) | 1 | $13.93 | ACQUIRED (delivered May 19) |
| Brown & Sharpe spring-loaded tap guide, 1/2" hardened shank | [B005317ZMC](https://www.amazon.com/dp/B005317ZMC) | 1 | $27.45 | ACQUIRED |
| Mollom 124 mm / 4-7/8" HSS M42 bi-metal hole saw with arbor + pilot bits | [B0BZQ4J5B1](https://www.amazon.com/dp/B0BZQ4J5B1) | 1 | $19.19 | ACQUIRED |
| 12 mm Baltic birch plywood, 1/2" × 8" × 8", B/BB grade (2 pc) | [B0DP8597Q2](https://www.amazon.com/dp/B0DP8597Q2) | 1 box | $10.71 | ACQUIRED |
| ACXFOND 1/4" MDF boards, 8" × 10" (20 pk) | [B0F1FJYDQ3](https://www.amazon.com/dp/B0F1FJYDQ3) | 1 pk | $25.73 | ACQUIRED |
| Franklin International 1412 Titebond III wood glue, 4 oz | [B0002YQ378](https://www.amazon.com/dp/B0002YQ378) | 1 | $5.34 | ACQUIRED |
| Storystore 4" heavy-duty steel C-clamps (4 pk) | [B0DHX78G97](https://www.amazon.com/dp/B0DHX78G97) | 1 pk | $21.44 | ACQUIRED |
| Bosch DSB1013 1" × 6" Daredevil Standard Spade Bit | [B001NGPAA0](https://www.amazon.com/dp/B001NGPAA0) | 1 | $5.35 | ACQUIRED |
| Ultra Duster Canned Air Industrial Strength 10 oz, 4-pack | [B07JRBR1MM](https://www.amazon.com/dp/B07JRBR1MM) | 1 pk (4× 10 oz) | $24.51 | ACQUIRED (delivered May 12) |
| Hgnova 15-pc 1064 nm laser protective lens, D18 × 2 mm, 1000–3000 W handheld 4-in-1 laser welder | [B0FF38DY1Z](https://www.amazon.com/dp/B0FF38DY1Z) | 1 pk (15) | $19.29 | ACQUIRED |
| SENCTRL 0–200 PSI glycerin-filled pressure gauge, 2.5" dial, 1/4" NPT lower mount, SS case | [B0BCHMQLFB](https://www.amazon.com/dp/B0BCHMQLFB) | 1 | $10.72 | ACQUIRED (delivered Tue May 5) |
| ChillWaves brass 1/4" NPT outer-hex-head pipe plugs, 12-pack | [B0C4LP4B3D](https://www.amazon.com/dp/B0C4LP4B3D) | 1 pk (12) | $11.79 | ACQUIRED (delivered Tue May 5) |
| Milton 727 industrial M-STYLE® 1/4" MNPT air plug, 10-pack, alloy steel | [B000PDWI4S](https://www.amazon.com/dp/B000PDWI4S) | 1 pk (10) | $15.02 | ACQUIRED (delivered Tue May 5) |
| BEAMNOVA hydrostatic test pump, 0–726 PSI / 0–50 bar / 0–5 MPa, 3.17 gal water reservoir, 4.43 ft × 1/4" hydraulic hose with 1/2" female gasket-swivel testpiece end, copper pump body + check valve, built-in 3-unit dial gauge | [B07T45XTD1](https://www.amazon.com/dp/B07T45XTD1) | 1 | $93.30 | ACQUIRED (delivered Tue May 5) |
| KOOTANS 1/2" NPT male × 1/4" NPT male solid brass reducing hex nipple, 4-pack | [B07P7ZRZMD](https://www.amazon.com/dp/B07P7ZRZMD) | 1 pk (4) | $12.86 | ACQUIRED (delivered Tue May 5) |
| OnlineMetals #12498 — 5" OD × 0.065" wall 316 welded SS round tube, cut to 6.0" length, MTRs required | onlinemetals.com | 10 | $736.73 | ACQUIRED |
| SendCutSend order SG019619 — 1/4" 316 SS circular endcap plates | sendcutsend.com | 20 | $621.19 | ACQUIRED |
| SendCutSend order SQ65E969 — 304 SS 0.048" body blanks ×2 (plan-B spare/practice) | sendcutsend.com | 2 | $60.19 | ACQUIRED |
| SendCutSend order SV07U813 — 304 SS 0.060" racetrack end-cap blanks ×4 (plan-B spare) | sendcutsend.com | 4 | $45.52 | ACQUIRED |
| SendCutSend order SP54G453 — 304 SS 0.048" body half-sheets ×10 (plan-B spare) | sendcutsend.com | 10 | $134.38 | ACQUIRED |
| SendCutSend order S064D925 — 0.060" 316 SS Touch-Flo under-counter plates | sendcutsend.com | 10 | $36.29 | ACQUIRED (delivered May 14) |

## 2. CO2 subsystem

Cylinders, regulator, CO2 line, push-to-connect adapters for the CO2 side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Lillium under-sink carbonated soda maker + 3-way sparkling-water faucet, black, 110–120 V AC (SKU 102) | [liliumfaucet.com](https://liliumfaucet.com/) | 1 | $1,129.00 | ACQUIRED |
| TAPRITE E-T742 CO2 dual-gauge primary regulator, CGA-320 | [B00L38DRD0](https://www.amazon.com/dp/B00L38DRD0) | 1 | $96.47 | ACQUIRED |
| Airgas #8160436286 — prototype CO2 cylinder, 5 lb aluminum food-grade, CGA-320 (CY-CD FG5) | airgas.com (Lincoln NE) | 1 | $133.10 | ACQUIRED |
| Airgas #8160436286 — CO2 fill, 5 lb food-grade (prototype cylinder) | airgas.com (Lincoln NE) | 1 | $47.93 | ACQUIRED |
| Airgas #8162013342 — testing CO2 cylinder, 5 lb aluminum food-grade, CGA-320 (CY-CD FG5) | airgas.com (Lincoln NE) | 1 | $133.10 | ACQUIRED |
| Airgas #8162013342 — CO2 fill, 5 lb food-grade (testing cylinder) | airgas.com (Lincoln NE) | 1 | $67.38 | ACQUIRED |
| 10 ft 5/16" ID beer CO2 line w/ 4 hose clamps | [B0D1RB3TF6](https://www.amazon.com/dp/B0D1RB3TF6) | 1 | $13.50 | ACQUIRED |
| DERPIPE push-to-connect 5/16" tube x 1/4" NPT (5 pk) | [B09LXVGPG7](https://www.amazon.com/dp/B09LXVGPG7) | 1 pk | $10.71 | ACQUIRED |
| VUYOMUA 0.8 gal SS portable air tank (bench test fixture) | [B0BV6FMMJP](https://www.amazon.com/dp/B0BV6FMMJP) | 1 | $60.05 | ACQUIRED |
| Control Devices SV-100 safety valve, 1/4" NPT, 100 psi (spare PRV; superseded by SV-125) | [B0D361X97X](https://www.amazon.com/dp/B0D361X97X) | 1 | $16.06 | ACQUIRED |
| Interstate Pneumatics WR1110 1/4" NPT in-Line 90 PSI fixed pre-set pressure regulator, 230 PSI max inlet, aluminum body | [B07J2L8LF3](https://www.amazon.com/dp/B07J2L8LF3) | 1 | $25.66 | ACQUIRED (delivered May 17) |
| Control Devices SV-125 safety valve, 1/4" NPT, 125 psi set pressure, 49 SCFM relief, brass | [B01G2F6EMY](https://www.amazon.com/dp/B01G2F6EMY) | 1 | $8.03 | ACQUIRED (delivered May 17) |
| Fresh Water Systems order WEBFWS100675224 — JG 1/4" NPTF male connector (×10) + 1/4" union elbow PP0308E (×10) | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order (2 × bag of 10) | $44.11 | ACQUIRED (delivered May 19) |

## 3. Water supply + backflow prevention

Feed-water inlet, filter, ASSE 1022 backflow preventer and its vent-line hardware, quick-connect tubing for the potable side feeding the carbonator.

| Part | Link | Qty | $ | Status |
|---|---|---|---|---|
| Multiplex 19-0897 ASSE 1022 backflow preventer, 3/8" NPT × 3/8" MFL | [howdybrewer.com](https://www.howdybrewer.com/products/multiplex-backflow-preventor-assembly-1022-3-8-npt-x-3-8-mfl) | 1 | $61.49 | ACQUIRED |
| Multiplex 19-0897 ASSE 1022 backflow preventer, 3/8" NPT × 3/8" MFL | [midwestbev.com](https://www.midwestbev.com/products/asse-1022-backflow-preventer) | 4 | $145.80 | ACQUIRED |
| Hooshing 3/8" flare × 1/4" FNPT brass adapter (2 pk) | [B0BNHVV6HT](https://www.amazon.com/dp/B0BNHVV6HT) | 1 pk | $10.71 | ACQUIRED |
| brewhardware FFL38BARB38 Swivel Flare Adapter, 3/8" FFL (UNCOMMON) × 3/8" OD hose barb | [brewhardware.com](https://www.brewhardware.com/product_p/ffl38barb38.htm) | 5 | $39.42 | ACQUIRED (delivered) |
| Sealproof 1/4" ID × 3/8" OD food-grade clear PVC, 10 ft | [B07D9DK94V](https://www.amazon.com/dp/B07D9DK94V) | 1 | $8.46 | ACQUIRED |
| LOKMAN 304 SS worm-gear hose clamps, 10–16 mm (20 pk) | [B076Q7QVNM](https://www.amazon.com/dp/B076Q7QVNM) | 1 pk | $8.99 | ACQUIRED |
| Waterdrop 15UC-UF 0.01 µm inline fridge/ice-maker filter | [B085G9TZ4L](https://www.amazon.com/dp/B085G9TZ4L) | 1 | $62.99 | ACQUIRED |
| HAOCHEN brass angle stop add-a-tee 3/8"×3/8"×1/4" | [B0DLKHHGL6](https://www.amazon.com/dp/B0DLKHHGL6) | 1 | $11.99 | ACQUIRED |
| GAGIRA 5Pcs 316L Stainless Steel Coupling, 3/8" NPT Female × 1/4" NPT Female, includes Teflon tape | [B0G2XJGZMQ](https://www.amazon.com/dp/B0G2XJGZMQ) | 5 | $18.22 | ACQUIRED |
| LTWFITTING brass 3/8" × 1/4" FNPT reducing coupling (5-pk) | amazon.com (114-9960851-7517853) | 1 pk (5) | $8.56 | ACQUIRED (delivered May 29) |
| Lifevant 32.8 ft 1/4" OD water tubing + 12 quick-connects | [B0DKCZ5W66](https://www.amazon.com/dp/B0DKCZ5W66) | 1 | $9.99 | ACQUIRED |
| Fresh Water Systems order WEBFWS100673540 — black LLDPE tubing: 3/8" OD 25 ft + 1/4" OD 100 ft | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order | $43.29 | ACQUIRED (delivered May 13) |
| John Guest 1/4" OD × 1/8" NPT male push-fit | [B07V6XKZG9](https://www.amazon.com/dp/B07V6XKZG9) | 1 | $5.00 | ACQUIRED |
| John Guest PI1208S acetal bulkhead union (1/4" QC) | [B0C1F3QR7N](https://www.amazon.com/dp/B0C1F3QR7N) | 2 | $11.49 ea | ACQUIRED |
| SAMSUNG HAF-QIN-3P carbon block refrigerator filter (3 pk) | [B09HR7H8X7](https://www.amazon.com/dp/B09HR7H8X7) | 1 pk | $97.10 | ACQUIRED |
| Yetaha RO 1/4" water flow-adjust valve | [B07GDFWB8R](https://www.amazon.com/dp/B07GDFWB8R) | 1 | $12.86 | ACQUIRED |
| SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand pump | [B0166UBJX4](https://www.amazon.com/dp/B0166UBJX4) | 1 | $48.25 | ACQUIRED |
| Fresh Water Systems order WEBFWS100677333 — Colder 70500 NSF QD insert (×2) + 74600 NSF QD body (×2) + blue 1/4" LLDPE 100 ft + JG PP0208E union tee (×10) | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order (4 items) | $130.45 | ACQUIRED |
| Fresh Water Systems order WEBFWS100677768 — MTB-0604WP 3/8"barb × 1/4"MNPT tee (×10) + JG PP450822E 1/4" NPTF female adapter (×10) | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order (2 items) | $62.08 | ACQUIRED |

## 4. Carbonator plumbing (pressurized side)

Check valves, sparge stone + barb adapter for internal-sparge CO2 carbonation, compression fittings on the water/CO2 pressure side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| ChillWaves 304 SS in-line split check valve 1/4" NPT M×F (silicone seat | [B0DPLBYZB4](https://www.amazon.com/dp/B0DPLBYZB4) | 1 | $18.22 | ACQUIRED |
| ChillWaves 304 SS in-line **Siamese** check valve 1/4" NPT M×F (1-pack) | [B0DPL88RHC](https://www.amazon.com/dp/B0DPL88RHC) | 1 | $16.08 | ACQUIRED |
| GASHER 1/4" NPT SS one-way check valve (2 pk) | [B0FV2D2FFX](https://www.amazon.com/dp/B0FV2D2FFX) | 1 pk | $15.00 | ACQUIRED |
| GASHER 1/4" NPT SS one-way check valve (2 pk) | [B0FV2D2FFX](https://www.amazon.com/dp/B0FV2D2FFX) | 2 pk | $15.00 ea | ACQUIRED |
| LTWFITTING 316 SS 1/4" hose barb × 1/4" MNPT | [B017N4TTMA](https://www.amazon.com/dp/B017N4TTMA) | 1 | $13.65 | ACQUIRED |
| TAISHER 2PCS 316L SS 90° Barstock Street Elbow, 1/4" NPT Male × 1/4" NPT Female | [B0CZ38MYL1](https://www.amazon.com/dp/B0CZ38MYL1) | 1 pk (2) | $22.51 | ACQUIRED (delivered May 17) |
| TAISHER 2PCS 316L SS 90° Barstock Street Elbow, 1/4" NPT M × 1/4" NPT F | [B0CZ38MYL1](https://www.amazon.com/dp/B0CZ38MYL1) | 1 pk (2) | $22.51 | ACQUIRED (delivered May 15) |
| FERRODAY 0.5 µm sintered 316 SS sparge stone, 1/4" barb input (2-set) | [B091C5Y6L9](https://www.amazon.com/dp/B091C5Y6L9) | 1 | $14.97 | ACQUIRED |
| ~~Beduan 1/4" male spiral cone atomization nozzle, 316 SS~~ | [B07LGPD3GB](https://www.amazon.com/dp/B07LGPD3GB) | 1 | $9.99 | ACQUIRED (superseded) |
| VALVENTO 316 SS 1/4" OD compression × 1/4" NPT adapter (2 pk) | [B0DXZZBK7D](https://www.amazon.com/dp/B0DXZZBK7D) | 1 pk | $12.85 | ACQUIRED |
| VALVENTO 1/4" OD 316 SS tube, 12" length (5 pk) | [B0F6SYFK48](https://www.amazon.com/dp/B0F6SYFK48) | 1 pk | $18.23 | ACQUIRED |
| TAISHER 304 SS compression square needle valve 1/4" | [B0CLXHZZCW](https://www.amazon.com/dp/B0CLXHZZCW) | 1 | $32.15 | ACQUIRED |
| YKEBVPW 1/4" push-connect needle valve flow control | [B0FBFVTNLM](https://www.amazon.com/dp/B0FBFVTNLM) | 1 | $7.49 | ACQUIRED |
| YKEBVPW 1/4" needle valve | amazon.com (112-4375086-9926652) | 1 | $8.03 | ACQUIRED (delivered Jun 1) |

## 5. Flavor subsystem

Peristaltic pumps, solenoids, bag-in-box connector, silicone delivery tubing, barb fittings, bladders, check valves on the flavor side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Kamoer KPHM400-SW3B25 400 ml/min 12 V peristaltic pump (BPT, sold by Kamoer Fluid Tech Shanghai) | [B09MS6C91D](https://www.amazon.com/dp/B09MS6C91D) | 3 | $32.55 ea | ACQUIRED |
| Beduan 12 V 1/4" inlet water solenoid (NC) | [B07NWCQJK9](https://www.amazon.com/dp/B07NWCQJK9) | 3–4 lines | $9.64 ea | ACQUIRED (short vs 12-valve manifold) |
| Hosyond 5-pack MG90S 9 g metal-gear micro servo | [B09V5BR7J5](https://www.amazon.com/dp/B09V5BR7J5) | 1 pk (5) | $15.43 | ON-ORDER |
| NeoFit acetal ball valve — push-fit quarter-turn, food-grade PP body + acetal + EPDM O-ring, 1/4" OD tube (5-pack) | [B0DDQC7S3B](https://www.amazon.com/dp/B0DDQC7S3B) | 1 pk (5) | $22.80 | ON-ORDER |
| Supply Depot Coke-compatible BIB connector, 3/8" red (2 pk) | [B0DMFK9B6P](https://www.amazon.com/dp/B0DMFK9B6P) | 1 pk | $19.99 | ACQUIRED |
| Platypus SoftBottle 1 L (bladder donor) | [B08PG3GMQ8](https://www.amazon.com/dp/B08PG3GMQ8) | 1 | $23.49 | ACQUIRED |
| Platypus SoftBottle 1 L "Waves" (bladder donor) | [B00ZX0ERE2](https://www.amazon.com/dp/B00ZX0ERE2) | 1 | $15.35 | ACQUIRED |
| Platypus Platy 2 L collapsible bottle (bladder donor) | [B000J2KEGY](https://www.amazon.com/dp/B000J2KEGY) | 1 | $15.94 | ACQUIRED |
| Platypus Hoser hydration tube kit | [B07N1T6LNW](https://www.amazon.com/dp/B07N1T6LNW) | 2 | $24.95 ea | ACQUIRED |
| Platypus Hoser 1 L Hands-Free Hydration Reservoir, Fast Flow Valve | [B002OYMRS8](https://www.amazon.com/dp/B002OYMRS8) | 2 | $51.24 | ACQUIRED |
| JoyTube 3/8" ID food-grade silicone tubing, 10 ft | [B089YGDB55](https://www.amazon.com/dp/B089YGDB55) | 1 | $11.99 | ACQUIRED |
| Metaland 3/8" ID food-grade silicone tubing | [B08L1RS757](https://www.amazon.com/dp/B08L1RS757) | 1 | $7.99 | ACQUIRED |
| Metaland 1/4" ID food-grade silicone tubing | [B08L1ST6ST](https://www.amazon.com/dp/B08L1ST6ST) | 1 | $7.99 | ACQUIRED |
| Metaland 1/2" ID silicone tubing | [B0BC7K5B91](https://www.amazon.com/dp/B0BC7K5B91) | 1 | $9.99 | ACQUIRED |
| Metaland 1/8" ID silicone tubing | [B08XM1V475](https://www.amazon.com/dp/B08XM1V475) | 1 | $8.99 | ACQUIRED |
| Quickun 3/4" ID silicone tubing | [B091SXP7DD](https://www.amazon.com/dp/B091SXP7DD) | 1 | $9.99 | ACQUIRED |
| Pure silicone 3/8" ID × 1/2" OD high-temp tube, 10 ft | [B07XMGHHLK](https://www.amazon.com/dp/B07XMGHHLK) | 1 | $16.99 | ACQUIRED |
| ANPTGHT 1/8" ID × 1/4" OD black silicone tubing | [B0BM4KQ6RT](https://www.amazon.com/dp/B0BM4KQ6RT) | 2 | $13.93 ea | ACQUIRED |
| Rebower brass hose barb 3/8" × 1/8" | [B0FP5JX2KS](https://www.amazon.com/dp/B0FP5JX2KS) | 1 | $4.99 | ACQUIRED |
| MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4 pk) | [B0DMP77B6S](https://www.amazon.com/dp/B0DMP77B6S) | 1 pk | $12.97 | ACQUIRED |
| YDS butterfly SS W2 hose clamp, 10–16 mm (10 pk) | [B07C33VLQ6](https://www.amazon.com/dp/B07C33VLQ6) | 1 pk | $15.20 | ACQUIRED |
| ANPTGHT 1/8" tee fitting, equal barb (5 pk) | [B08SBM4DBQ](https://www.amazon.com/dp/B08SBM4DBQ) | 1 pk | $6.99 | ACQUIRED |
| 1/8" plastic check valve, barb one-way (10 pk) | [B0CLV9BRL1](https://www.amazon.com/dp/B0CLV9BRL1) | 1 pk | $7.99 | ACQUIRED |
| Green silicone duckbill check valve 6.3 mm (10 pk) | [B07TKT9KNL](https://www.amazon.com/dp/B07TKT9KNL) | 1 pk | $13.63 | ACQUIRED |
| Heyous black rubber duckbill check valve (10 pk) | [B0FNR51NXN](https://www.amazon.com/dp/B0FNR51NXN) | 1 pk | $7.99 | ACQUIRED |
| Sloan-style duckbill valve, 8 pc | [B0G4MKMG54](https://www.amazon.com/dp/B0G4MKMG54) | 1 pk | $9.99 | ACQUIRED |
| 006 silicone O-ring red 70A, 1/8" ID (100 pk) | [B0GFTVQPW3](https://www.amazon.com/dp/B0GFTVQPW3) | 1 pk | $9.86 | ACQUIRED |
| 007 silicone O-ring red 70A, 5/32" ID (20 pk) | [B09M86ZCCB](https://www.amazon.com/dp/B09M86ZCCB) | 1 pk | $9.98 | ACQUIRED |
| TAILONZ push-to-connect 1/4" tube × 1/8" NPT (10 pk) | [B07P8784D2](https://www.amazon.com/dp/B07P8784D2) | 1 pk | $9.99 | ACQUIRED |
| MALIDA 1/8" NPT × 1/4" tube elbow/straight push-fit | [B09MY72KQ7](https://www.amazon.com/dp/B09MY72KQ7) | 1 pk | $7.99 | ACQUIRED |
| John Guest PP2308E two-way divider, black polypropylene 1/4" | [freshwatersystems.com](https://www.freshwatersystems.com/products/john-guest-two-way-divider-black-polypropylene-1-4) | 2 bags (20 dividers) | $88.43 | ACQUIRED (delivered May 14) |
| John Guest Speedfit PP1208E 1/4" OD black polypropylene push-to-connect bulkhead union, 10-pack | [B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM) | 1 pk (10) | $24.79 | ACQUIRED (delivered May 12) |
| PureSec 1/4" RO push-to-connect 90° elbow bulkhead, white polypropylene, 5-pack | [B0968K4JRN](https://www.amazon.com/dp/B0968K4JRN) | 1 pk (5) | $11.79 | ACQUIRED (delivered May 29) |
| uxcell silicone flat washer, ⌀16 ID × ⌀24 OD × 3 mm, clear, 10-pack — reservoir bulkhead wet-side face seal | [B07D23JJMR](https://www.amazon.com/dp/B07D23JJMR) | 1 pk (10) | $7.50 | ON-ORDER (placed Jun 7, order 112-8819640-4433810) |
| Craft Resin "Arts & Crafts" crystal-clear epoxy, 34 oz kit | [B07YCVVYFK](https://www.amazon.com/dp/B07YCVVYFK) | 1 kit (34 oz) | $26.80 | ACQUIRED (delivered May 29) |
| Cambro food storage container 6 qt | [B001BZEQ44](https://www.amazon.com/dp/B001BZEQ44) | 1 | $21.45 | ACQUIRED |
| Pinnacle Mercantile F-style HDPE bottle set | [B0CFP9RRSF](https://www.amazon.com/dp/B0CFP9RRSF) | 1 | $16.99 | ACQUIRED |
| SodaStream Diet Mountain Dew concentrate | [B0CS191QMW](https://www.amazon.com/dp/B0CS191QMW) | 1 | $17.62 | ACQUIRED |
| SodaStream Diet Mountain Dew 4-pack | [B0G26HQWBY](https://www.amazon.com/dp/B0G26HQWBY) | 1 | $28.99 | ACQUIRED |
| SodaStream Pepsi Wild Cherry Zero 4-pack | [B0G4NRDQB8](https://www.amazon.com/dp/B0G4NRDQB8) | 1 | $28.99 | ACQUIRED |
| SodaStream Diet Cola 4-pack | [B01GQ2ZMKI](https://www.amazon.com/dp/B01GQ2ZMKI) | 1 | $18.89 | ACQUIRED |
| Magnetic pogo pin connector, 2-pin (2 pair) | [B0CSX6ZQ1H](https://www.amazon.com/dp/B0CSX6ZQ1H) | 1 pk | $10.71 | ACQUIRED |

## 6. Refrigeration

Ice-maker donor units and copper coil for the chill loop.

| Part | Link | Qty | $ | Status |
|---|---|---|---|---|
| Frigidaire EFIC117-SS ice maker, 26 lb/day (donor) | [B07PCZKG94](https://www.amazon.com/dp/B07PCZKG94) | 1 | $78.70 | ACQUIRED |
| Countertop ice maker 26 lb/day (2nd donor) | [B0F42MT8JX](https://www.amazon.com/dp/B0F42MT8JX) | 1 | $63.80 | ACQUIRED |
| GOORY 1/4" OD × 50 ft ACR copper coil | [B0DKSW5VL9](https://www.amazon.com/dp/B0DKSW5VL9) | 1 | $68.63 | ACQUIRED |
| RIGID DV1910E Copper Coil Chiller, 12 V (alt path) | [rigidhvac.com](https://www.rigidhvac.com/) (direct order) | 1 | $580.00 | ACQUIRED |
| Fiberglass Supply Depot 2 lb-density 2-part expanding pour foam, closed-cell PU (quart kit) | [B08R7TX8QJ](https://www.amazon.com/dp/B08R7TX8QJ) | 1 kit | $42.89 | ACQUIRED (delivered May 16) |
| HiLetgo DS18B20 waterproof 1-wire temperature probe, 1 m SS sheath (5 pk) | [B00M1PM55K](https://www.amazon.com/dp/B00M1PM55K) | 1 pk | $11.79 | ACQUIRED |
| Supco D111 replacement filter-drier, 1/4" × 1/4" sweat, XH-9 | [B00DM8KGXS](https://www.amazon.com/dp/B00DM8KGXS) | 1 | $11.95 | ACQUIRED |
| Supco SUD8358 UV-dye filter-drier, 1/4" × 1/4" | [B009AX2O5W](https://www.amazon.com/dp/B009AX2O5W) | 1 | $13.40 | ACQUIRED |
| Mastercool 70025 cap-tube cutter | [B00NY1YHHE](https://www.amazon.com/dp/B00NY1YHHE) | 1 | $15.74 | ACQUIRED |
| Orion Motor Tech HVAC A/C manifold gauge set, 1/4" SAE | [B07CZB2SHZ](https://www.amazon.com/dp/B07CZB2SHZ) | 1 | $48.24 | ACQUIRED |
| Orion Motor Tech 4 CFM 1/3 HP single-stage vacuum pump, 110 V, 150 µ ultimate | [B08P1WRZ1S](https://www.amazon.com/dp/B08P1WRZ1S) | 1 | $78.28 | ACQUIRED |
| Supco BPV31 bullet-piercing valve | [B00DM8J3MI](https://www.amazon.com/dp/B00DM8J3MI) | 1 | $7.37 | ACQUIRED |
| Smart Weigh Pro digital pocket scale, 2000 g × 0.1 g | [B00IZ1YHZK](https://www.amazon.com/dp/B00IZ1YHZK) | 1 | $19.25 | ACQUIRED |
| Toptes PT520A refrigerant/hydrocarbon gas leak detector (description fix: ledger previously branded "Elitech", Amazon listing brand is Toptes) | [B0BTM3G8DK](https://www.amazon.com/dp/B0BTM3G8DK) | 1 | $42.89 | ACQUIRED |
| Enviro-Safe R-600a 3-pack (3× 6 oz self-sealing cans) + brass charging gauge | [B0CGG1WH1N](https://www.amazon.com/dp/B0CGG1WH1N) | 1 | $72.92 | ACQUIRED |
| Klein Tools 51006 3-in-1 tube bender, 1/4 / 5/16 / 3/8" OD | [B0DPQX17WM](https://www.amazon.com/dp/B0DPQX17WM) | 1 | $21.98 | ACQUIRED |
| Wisscool 1/4" handheld tube straightener | [B0F6BPTW3T](https://www.amazon.com/dp/B0F6BPTW3T) | 1 | $24.99 | ACQUIRED |
| ESCO Institute EPA Section 608 Preparatory Manual | [1930044607](https://www.amazon.com/dp/1930044607) | 1 | $22.47 | ACQUIRED |
| Bernzomatic TS8000 high-intensity torch head + MAP-Pro 3-can kit | [B0BPMVTJ1R](https://www.amazon.com/dp/B0BPMVTJ1R) | 1 | $117.96 | ACQUIRED |
| Harris SSWF7 Stay Silv white brazing flux, 6.5 oz | [B002BYLU52](https://www.amazon.com/dp/B002BYLU52) | 1 | $11.92 | ACQUIRED |
| Uniweld RHP400 CGA-580 regulator, 1/4" male flare, 0–400 psi delivery | [B008HQ6GXO](https://www.amazon.com/dp/B008HQ6GXO) | 1 | $96.76 | ACQUIRED |
| RIDGID 31622 Model 150 constant-swing tubing cutter, 1/8"–1-1/8" | [B0009W6T8G](https://www.amazon.com/dp/B0009W6T8G) | 1 | $31.99 | ACQUIRED |
| RIDGID 23332 Model 345 flaring tool, 45° SAE | [B000X4K9KO](https://www.amazon.com/dp/B000X4K9KO) | 1 | $99.99 | ACQUIRED |
| BCuP-5 15% silver brazing alloy, 1/16" × 1 troy oz rod | [B0DQ3ZMHK7](https://www.amazon.com/dp/B0DQ3ZMHK7) | 1 | $18.99 | ACQUIRED |
| 3M Scotch-Brite Maroon General Purpose Hand Pads, 6" × 9", 1-pack of 20 pads (3M 07447 equivalent) | [B07CGPCTHT](https://www.amazon.com/dp/B07CGPCTHT) | 1 pk | $28.85 | ACQUIRED |
| HVAC 1/4" OD copper slip coupling, ACR-grade, sweat × sweat, 10-pack | [B0FH549N6D](https://www.amazon.com/dp/B0FH549N6D) | 1 pk | $8.56 | ACQUIRED |
| Knipex 86 01 180 Pliers Wrench, 7.25" | [B07YLFLSJW](https://www.amazon.com/dp/B07YLFLSJW) | 1 | $57.06 | ACQUIRED |
| Joywayus brass 1/4" SAE 45° flare nut, 7/16"-20 thread, 5-pack | [B0G1XJ2F68](https://www.amazon.com/dp/B0G1XJ2F68) | 1 pk | $8.57 | ACQUIRED |
| 3M 425 aluminum foil tape, 2" × 180 ft, thermally conductive | [B07BTW7C2N](https://www.amazon.com/dp/B07BTW7C2N) | 1 | $95.42 | ACQUIRED |
| Pouring Masters 5 oz / 150 mL graduated plastic mixing cups (50 pk) | [B08JHH1DBF](https://www.amazon.com/dp/B08JHH1DBF) | 1 pk | $20.37 | ACQUIRED |
| JMU 6" wood tongue depressors, individually wrapped (100 pk) | [B09H6ZP447](https://www.amazon.com/dp/B09H6ZP447) | 1 pk | $7.50 | ACQUIRED |
| SUP powder-free 4 mil nitrile exam gloves, X-Large, 100 ct (= 50 pairs) | [B0G8SSMVKW](https://www.amazon.com/dp/B0G8SSMVKW) | 1 pk | $7.49 | ACQUIRED |
| BOJACK SF76E SEFUSE thermal fuse, 77 °C, 10 A / 250 V (10-pack) | [B07Y61YTTK](https://www.amazon.com/dp/B07Y61YTTK) | 1 pk (10) | $6.42 | ACQUIRED (delivered May 13) |
| ACEIRMC MQ-6 LPG / iso-butane combustible gas sensor module (5-pack) | [B0978JSCZ8](https://www.amazon.com/dp/B0978JSCZ8) | 1 pk (5) | $11.79 | ACQUIRED (delivered May 13) |
| Heyco SB-500-6 (Heyco part #2053) black 6/6 nylon strain-relief snap bushing, 100-pack | [B01LPBST9G](https://www.amazon.com/HEYCO-2053-SB-500-6-Accessories/dp/B01LPBST9G/) | 1 pk (100) | $12.60 | ACQUIRED (delivered May 16) |

## 7. Dispensing end — faucet, flow sensor

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Westbrass A2031-NL-62 8" Touch-Flo cold-water faucet, matte black | [B0BXFW1J38](https://www.amazon.com/dp/B0BXFW1J38) | 1 | $32.18 | ACQUIRED |
| Westbrass D203-NL-62 6" Touch-Flo cold-water faucet, matte black | [B01MZ6JPXW](https://www.amazon.com/dp/B01MZ6JPXW) | 1 | $52.99 | ACQUIRED |
| Westbrass R2031-NL-12 8" Touch-Flo faucet, oil-rubbed bronze | [B01N5LVNQA](https://www.amazon.com/dp/B01N5LVNQA) | 1 | $20.95 | ACQUIRED |
| 1/4" OD × 12" 304 SS straight tube, 4 pc | [B0F87DJDZW](https://www.amazon.com/dp/B0F87DJDZW) | 1 pk | $12.86 | ACQUIRED |
| 1/8" OD × 12" 304 SS straight tube, 4 pc | [B0F87V8XCB](https://www.amazon.com/dp/B0F87V8XCB) | 1 pk | $8.57 | ACQUIRED |
| Beduan 304 SS compression ferrule sleeve, 1/4" OD, 5 pk | [B07V4K2KKH](https://www.amazon.com/dp/B07V4K2KKH) | 1 pk | $6.42 | ACQUIRED |
| Beduan 304 SS compression ferrule sleeve, 1/8" OD | [B07V8RJJYJ](https://www.amazon.com/dp/B07V8RJJYJ) | 1 pk | $5.35 | ACQUIRED |
| Pysrych 304 SS reducing compression union, 1/4" OD × 1/8" OD, 2 pk | [B0BM4394Z4](https://www.amazon.com/dp/B0BM4394Z4) | 1 pk | $8.99 | ACQUIRED |
| Siptenk 1/4" OD brass tube stiffener insert, 100 pk | [B0FM77LLM1](https://www.amazon.com/dp/B0FM77LLM1) | 1 pk | $8.99 | ACQUIRED |
| DIGITEN G1/4" Hall-effect flow sensor 0.3–10 L/min | [B07QRXLRTH](https://www.amazon.com/dp/B07QRXLRTH) | 1 | $20.36 | ACQUIRED |
| DIGITEN G1/4" Hall-effect flow meter 0.3–6 L/min | [B07QS17S6Q](https://www.amazon.com/dp/B07QS17S6Q) | 1 | $9.49 | ACQUIRED |
| Eoiips polyethylene tubing 1/16" ID × 1/8" OD, 3.28 ft (1 m) | [B0BWJ3S5NM](https://www.amazon.com/dp/B0BWJ3S5NM) | 1 | $8.03 | ACQUIRED |
| CARGEN Pipe Insulation Foam Tube | [B0D2XFK337](https://www.amazon.com/dp/B0D2XFK337) | 2 | $16.28 | ACQUIRED (delivered May 16) |

## 8. Electronics — controllers

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| ESP32-DevKitC-32E | [B09MQJWQN2](https://www.amazon.com/dp/B09MQJWQN2) | 1+ | $11.00 | ACQUIRED |
| Waveshare RP2040 0.99" round touch LCD, CNC case | [B0CTSPYND2](https://www.amazon.com/dp/B0CTSPYND2) | 2 | ~$25.73 ea | ACQUIRED |
| Meshnology ESP32-S3 round rotary display 1.28" | [B0G5Q4LXVJ](https://www.amazon.com/dp/B0G5Q4LXVJ) | 1 | bundle | ACQUIRED |

## 9. Electronics — I/O, drivers, sensors, power, DIN rail, connectors

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Waveshare MCP23017 I2C I/O expansion board | [B07P2H1NZG](https://www.amazon.com/dp/B07P2H1NZG) | 1 | $12.99 | ACQUIRED |
| BOJACK ULN2803 Darlington driver IC (10 pk) | [B08CX79JSQ](https://www.amazon.com/dp/B08CX79JSQ) | 1 pk | $6.99 | ACQUIRED |
| ULN2803A high-current driver module (2 pc) | [B0F872W528](https://www.amazon.com/dp/B0F872W528) | 1 pk | $6.59 | ACQUIRED |
| BOJACK L298N dual H-bridge motor driver (4-pack) | [B0C5JCF5RS](https://www.amazon.com/dp/B0C5JCF5RS) | 1 pk | $10.71 | ACQUIRED |
| DS3231 AT24C32 RTC module (2 pk) | [B09LLMYBM1](https://www.amazon.com/dp/B09LLMYBM1) | 1 pk | $7.07 | ACQUIRED |
| HiLetgo DS3231 high-precision RTC (5 pk) | [B01N1LZSK3](https://www.amazon.com/dp/B01N1LZSK3) | 1 pk | $16.08 | ACQUIRED |
| EDGELEC 4.7 kΩ 1/4 W 1% metal-film resistor (100 pk) | [B07HDFHPP3](https://www.amazon.com/dp/B07HDFHPP3) | 1 pk | $5.89 | ACQUIRED |
| Rubycon 470 µF 25 V low-ESR (0.08 Ω) radial aluminum electrolytic capacitor, 10×12.5 mm (15 pk) | [B0F8BZVBKF](https://www.amazon.com/dp/B0F8BZVBKF) | 1 pk | $7.40 | ACQUIRED |
| HiLetgo NJK-5002C Hall-effect proximity switch (2 pk) | [B01MZYYCLH](https://www.amazon.com/dp/B01MZYYCLH) | 1 pk | $8.49 | ACQUIRED |
| Gebildet reed switches, 14 mm glass body, NO (6 pk) | [B0CW9418F6](https://www.amazon.com/dp/B0CW9418F6) | 1 pk | $6.42 | ACQUIRED |
| DEVMO MINI vertical float switch | [B07T18PGJ4](https://www.amazon.com/dp/B07T18PGJ4) | 1 | $13.93 | ACQUIRED |
| EC Buying XKC-Y25-V non-contact capacitive liquid-level sensor | [B0C73F96MF](https://www.amazon.com/dp/B0C73F96MF) | 1 | $10.29 | ACQUIRED (delivered May 9) |
| HiLetgo MPR121 12-channel I2C capacitive touch breakout (2 pk) | [B06XXYZPPX](https://www.amazon.com/dp/B06XXYZPPX) | 1 pk | $6.85 | ACQUIRED (delivered May 10) |
| Kraftex copper foil tape, 1/4" × 66 ft, conductive adhesive | [B0G1TN3JWB](https://www.amazon.com/dp/B0G1TN3JWB) | 1 | $7.50 | ACQUIRED (delivered May 9) |
| ~~Tynulox 1/8" × 6" 304 SS round rod (10 pk)~~ | [B0BKGS32KJ](https://www.amazon.com/dp/B0BKGS32KJ) | 1 pk | $8.56 | ACQUIRED (superseded) |
| Tandefio 1/8" × 12" 316 SS round rod (5 pk) | [B0CY4DWJFQ](https://www.amazon.com/dp/B0CY4DWJFQ) | 1 pk | $8.57 | ACQUIRED |
| 12 V 2 A DC power supply, 9-tip | [B0DZGTTBGZ](https://www.amazon.com/dp/B0DZGTTBGZ) | 1 | bundle | ACQUIRED |
| 5 V 3 A AC/DC adapter, 11-tip | [B09NLMVXMZ](https://www.amazon.com/dp/B09NLMVXMZ) | 1 | $8.39 | ACQUIRED |
| Molence C45 PCB DIN-rail adapter clips (10 sets) | [B09KZHY8G4](https://www.amazon.com/dp/B09KZHY8G4) | 1 pk | $9.99 | ACQUIRED |
| VAMRONE 35 mm DIN rail, 4" (6 pk) | [B0CDPVRY2W](https://www.amazon.com/dp/B0CDPVRY2W) | 1 pk | $6.99 | ACQUIRED |
| ESP32 super breakout DIN-rail mount GPIO expansion | [B0BW4SJ5X2](https://www.amazon.com/dp/B0BW4SJ5X2) | 1 | $25.99 | ACQUIRED |
| Baomain 0.11" male quick-disconnect spade (100 pk) | [B01MZZGAJP](https://www.amazon.com/dp/B01MZZGAJP) | 1 pk | $6.42 | ACQUIRED |
| Haisstronica ratchet crimper, AWG 22–10 | [B08F3JKDD3](https://www.amazon.com/dp/B08F3JKDD3) | 1 | bundle | ACQUIRED |
| Feggizuli 280 pc spade connector kit | [B0B4H54KPS](https://www.amazon.com/dp/B0B4H54KPS) | 1 pk | $8.25 | ACQUIRED |
| 60 pc female spade crimp kit | [B0B9MZJ2ML](https://www.amazon.com/dp/B0B9MZJ2ML) | 1 pk | $10.71 | ACQUIRED |
| Twidec 20 pc 4.8/6.3 mm spade crimp | [B08F784R9W](https://www.amazon.com/dp/B08F784R9W) | 1 pk | $9.64 | ACQUIRED |
| Dupont jumper wires (M/F, M/M, F/F) 20 cm | [B0BRTJXND9](https://www.amazon.com/dp/B0BRTJXND9) | 1 pk | $6.40 | ACQUIRED |
| ELEGOO 120 pc Dupont jumper wire ribbon | [B01EV70C78](https://www.amazon.com/dp/B01EV70C78) | 1 pk | $7.49 | ACQUIRED |
| Taiss Dupont crimp kit + SN-28B | [B0B11RLGDZ](https://www.amazon.com/dp/B0B11RLGDZ) | 1 | $21.99 | ACQUIRED |
| Waveshare MCP23017 I2C I/O expansion board (repeat ASIN) | [B07P2H1NZG](https://www.amazon.com/dp/B07P2H1NZG) | 1 | $13.75 | ACQUIRED (delivered Apr 27) |
| ULN2803A high-current driver module, 2-pc (repeat ASIN) | [B0F872W528](https://www.amazon.com/dp/B0F872W528) | 1 pk | $6.97 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 4-pin connector kit (50 sets / 300 pcs) | [B0B2RB524Y](https://www.amazon.com/dp/B0B2RB524Y) | 1 pk | $8.45 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 6-pin connector kit (50 sets / 400 pcs) | [B0B2R8Q1JL](https://www.amazon.com/dp/B0B2R8Q1JL) | 1 pk | $9.19 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 9-pin connector kit (30 sets / 330 pcs) | [B0B2R73RQB](https://www.amazon.com/dp/B0B2R73RQB) | 1 pk | $9.19 | ACQUIRED (delivered Apr 29) |
| CQRobot JST XH 2.54 mm 10-pin connector kit (30 sets / 360 pcs) — for the MCP23017 GPIO port rows (VCC + GND + 8 GPIO = 10 holes; a 10-pin fills the footprint so it can't seat off-by-one, where the 9-pin kit was sized for the ULN2803A sides). Order #112-9768778-8444265, placed Jun 7, 2026 | [B0B2R93CV3](https://www.amazon.com/dp/B0B2R93CV3) | 1 pk | $8.99 | ON-ORDER (arriving Tue Jun 9) |
| CQRobot/Zhansheng JST XH 2.54 mm pre-crimped bonded ribbon kit (15 cm / 5.9", 12-conductor ribbons × 8 + loose housings 2/3/4/5/6/7/8/9/10/12 P) | [B0F6C7X5CR](https://www.amazon.com/dp/B0F6C7X5CR) | 1 pk | $15.86 | ACQUIRED (delivered Apr 27) |
| Keszoox JST XH 2.54 mm pre-crimped wires, 50 cm × 22 AWG silicone, 20 pcs/pk in 10 colors | [B0F8HMQRRN](https://www.amazon.com/dp/B0F8HMQRRN) | 2 pk | $11.63 ea | ACQUIRED (delivered Apr 30) |
| KWANGIL 22AWG 12-Conductor Cable, UL2464, High-Flexible Tinned Copper Unshielded, Matte Black, 25 ft | [B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21) | 1 | $25.73 | ACQUIRED (delivered May 15) |
| CR2032 3 V cell pack (RTC backup) | [B0C15WJXL2](https://www.amazon.com/dp/B0C15WJXL2) | 1 | $11.19 | ACQUIRED |
| Breadboard kit, 2×830 + 2×400 pt | [B07DL13RZH](https://www.amazon.com/dp/B07DL13RZH) | 1 pk | $6.83 | ACQUIRED |
| Gratury IP67 waterproof enclosure | [B08281V2RL](https://www.amazon.com/dp/B08281V2RL) | 1 | $23.58 | ACQUIRED |
| Teyleten 3.3 V relay module, opto-isolated, 10 A @ 250 VAC (5 pk) | [B07XGZSYJV](https://www.amazon.com/dp/B07XGZSYJV) | 1 pk | $12.99 | ACQUIRED |
| Teyleten Robot DC 1-channel optocoupler 3.3 V relay module (repeat ASIN, variant listing) | [B07XGZSYJV](https://www.amazon.com/dp/B07XGZSYJV) | 1 | $13.93 | ACQUIRED |
| ~~Fotek SSR-25DA solid state relay~~ (surplus | [B08FR13GYR](https://www.amazon.com/dp/B08FR13GYR) | 1 | $13.92 | ACQUIRED (surplus) |
| ~~Inline AC fuse holder kit, 5×20 mm + assorted fuses~~ (surplus | [B07BC8DW3L](https://www.amazon.com/dp/B07BC8DW3L) | 1 | $12.86 | ACQUIRED (surplus) |
| ~~Leviton CR020-W 20 A 125 VAC single receptacle~~ (surplus | [B003ATTR8Y](https://www.amazon.com/dp/B003ATTR8Y) | 1 | $3.26 | ACQUIRED (surplus) |
| MXR IEC 60320 C14 panel-mount AC inlet, 10 A / 250 VAC (10 pk) | [B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ) | 1 pk | $6.96 | ACQUIRED |
| Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed (6 pk) | [B08VS8D4WC](https://www.amazon.com/dp/B08VS8D4WC) | 1 pk | $24.00 | ACQUIRED |
| uxcell C14 panel-mount inlet, 10 A, 3-pin straight (single) | [B07PXSLBF4](https://www.amazon.com/dp/B07PXSLBF4) | 1 | $7.39 | ACQUIRED |
| Tripp Lite P006-006 NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed | [B0000511C0](https://www.amazon.com/dp/B0000511C0) | 1 | $9.21 | ACQUIRED |
| Legrand Radiant 1597BKCCD12 15 A self-test GFCI, decorator duplex, black | [B017HAB4BO](https://www.amazon.com/dp/B017HAB4BO) | 2 | $41.72 | ACQUIRED (delivered May 21) |
| Mean Well IRM-90-12ST encapsulated 80 W / 12 V / 6.7 A PSU | [B0CNRST18V](https://www.amazon.com/dp/B0CNRST18V) | 1 | $31.66 | ACQUIRED |
| Mean Well LRS-200-12 enclosed 204 W / 12 V / 17 A PSU | [B0874XQ82F](https://www.amazon.com/dp/B0874XQ82F) | 1 | $30.03 | ACQUIRED |
| P3 Kill-A-Watt P4400 power meter (bench) | [B00009MDBU](https://www.amazon.com/dp/B00009MDBU) | 1 | $34.31 | ACQUIRED |

## 10. User interface — buttons, LEDs, air switch

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| KRAUS garbage-disposal air-switch kit, matte black | [B096319GMV](https://www.amazon.com/dp/B096319GMV) | 3 | $39.95 ea | ACQUIRED |
| 7 mm 12 V prewired momentary micro pushbutton, 12 pc | [B0F43GYWJ6](https://www.amazon.com/dp/B0F43GYWJ6) | 1 pk | $7.19 | ACQUIRED |
| EDGELEC 120 pc 12 V prewired LED assortment, 5 mm | [B07PVVL2S6](https://www.amazon.com/dp/B07PVVL2S6) | 1 pk | $12.99 | ACQUIRED |
| DIYables Passive Piezo Buzzer Module, 5 V, 2-pack | [B0DYDN31PV](https://www.amazon.com/dp/B0DYDN31PV) | 1 pk (2) | $6.42 | ACQUIRED (delivered May 14) |

## 11. Enclosure hardware

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Probrico 3-3/4" CC solid cabinet pulls, SS round T-bar, black (5 pk) | [B0DHHK94Y5](https://www.amazon.com/dp/B0DHHK94Y5) | 1 pk | $12.99 | ACQUIRED |
| Amerock bar pulls 3-3/4" matte-black (10 pk) | [B0DLWMV3RM](https://www.amazon.com/dp/B0DLWMV3RM) | 1 pk | $25.22 | ACQUIRED |
| Neodymium disc magnets 3×1 mm | [B0BQ3LPGZ1](https://www.amazon.com/dp/B0BQ3LPGZ1) | 1 | $19.49 | ACQUIRED |
| ruthex M3 Threaded Inserts Short, 100 pc, RX-M3Sx4.0 brass heat-set | [B0D39W228K](https://www.amazon.com/dp/B0D39W228K) | 1 pk (100) | $10.71 | ACQUIRED (delivered May 11) |
| BNUOK M3 × 25 mm Hex Socket Head Cap Screws, 60 pc, 12.9 alloy steel, black oxide finish | [B0DJQGF665](https://www.amazon.com/dp/B0DJQGF665) | 1 pk (60) | $8.57 | ACQUIRED (delivered May 11) |
| BNUOK M3 × 12 mm Hex Socket Head Cap Screws, 120 pc, 12.9 alloy steel, black oxide finish | [B0DJQGVK8S](https://www.amazon.com/dp/B0DJQGVK8S) | 1 pk (120) | $8.57 | ACQUIRED (delivered May 11, spare stock) |
| BNUOK M3 × 12 mm Hex Socket Head Cap Screws, 120 pc, 304 stainless steel (18-8), bright finish | [B0DJQGMQZM](https://www.amazon.com/dp/B0DJQGMQZM) | 1 pk (120) | $8.66 | ON-ORDER (arriving June 3) |
| LVDALAB PTFE Membrane Filter, ø13 mm × 0.45 µm, 100 pc, non-sterile | [B0D41KT345](https://www.amazon.com/dp/B0D41KT345) | 1 pk (100) | $13.23 | ACQUIRED (delivered May 12) |
| Mudder PTFE / PVC / PU tubing cutter, ≤3/4" OD (3-pk, black) | [B08VW15TK8](https://www.amazon.com/dp/B08VW15TK8) | 1 pk (3) | $12.86 | ACQUIRED (delivered May 18) |

## 12. Shop / bench infrastructure

General shop equipment supporting fabrication, assembly, and teardown. Not project-specific but purchased for this build.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| VEVOR adjustable 48" workbench w/ power outlet, wheels, pegboard, 2000 lb load | [B0FCD13KKQ](https://www.amazon.com/dp/B0FCD13KKQ) | 2 | $172.64 ea | ACQUIRED |

## 13. Printing consumables

3D-printer filament stock used for printed mechanical parts (cold-core shells, bladder cradles, pump cartridge, enclosure, hopper, etc.). PETG is the default per bom.md §7; specialty filaments below are for specific parts requiring flexibility or chemical resistance.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| SpoolHaus PEBA Super Bowden 1.75 mm, 1 kg | [B0G1L5XVH2](https://www.amazon.com/dp/B0G1L5XVH2) | 1 | $64.34 | ACQUIRED |
| Siraya Tech Flex 1.75 mm TPU | [B0CVXF33Z1](https://www.amazon.com/dp/B0CVXF33Z1) | 1 | $33.88 | ACQUIRED |
| SUNLU Official 3D Printer Filament Dryer S4 | [B0CQJMV71Z](https://www.amazon.com/dp/B0CQJMV71Z) | 1 | $125.47 | ACQUIRED (delivered March 25) |
| Polymaker 3D Printing Filament Storage Box, 4-Pack (PolyDryer Box x4) | [B0FHPS82YG](https://www.amazon.com/dp/B0FHPS82YG) | 1 pk (4) | $117.96 | ACQUIRED (delivered March 25) |
| SUNLU Official 3D Printer Filament Dryer E2 | [B0F5PMMXKD](https://www.amazon.com/dp/B0F5PMMXKD) | 1 | $321.74 | ACQUIRED (delivered April 7) |
| DUROZZLE 0.6mm Diamond PCD Nozzle Hotend, L-side (H2D/H2S/P2S/A1 series) | [B0GWDBQW4G](https://www.amazon.com/dp/B0GWDBQW4G) | 1 | $64.24 | ACQUIRED (delivered May 9 1:27 PM) |
| DUROZZLE 0.6mm Tungsten Carbide Nozzle Hotend, L-side (H2D/H2S/P2S/A1 series) | [B0GWDDKG47](https://www.amazon.com/dp/B0GWDDKG47) | 1 | $37.43 | ACQUIRED (delivered May 9 8:37 AM, used on touch-flo-shell PET-CF attempt 7) |
| Comfy Materials FDA-compliant food-grade PETG-Carbon, 1.75 mm × 1 kg, Gray | [B0BTLNK74C](https://www.amazon.com/dp/B0BTLNK74C) | 2 | $75.06 | ACQUIRED (delivered May 9 6:31 PM) |
| Bambu Lab Induction Heating Assembly - Right (H2C and H2C Laser, Bambu SKU 3DPP431) | [innoaddi.com](https://www.innoaddi.com/products/induction-heating-assembly-right) | 1 | $68.98 | ACQUIRED (delivered May 26) |
| Shineboc 20-pc Wet/Dry Sanding Sponge Set, foam-backed silicon-carbide, 3" × 4", 9 grits (180/320/400/600/800/1200/2000/2500/3000) | [B0D8ZC6HKY](https://www.amazon.com/dp/B0D8ZC6HKY) | 1 pk (20) | $10.71 | ACQUIRED (delivered May 12) |
| Polymaker Fiberon PET-CF17, 1.75 mm × 1 kg, Black | [B0G2CC2YP8](https://www.amazon.com/dp/B0G2CC2YP8) | 2 | $96.50 | ACQUIRED (delivered May 18) |
| SunTop food-contact-compliant PETG, 1.75 mm × 1 kg, Clear/Transparent | [B0FP34MJ94](https://www.amazon.com/dp/B0FP34MJ94) | 2 | $49.32 | ACQUIRED (delivered May 18) |

## 14. Soldering + small-signal electrical tools

Bench soldering capability for through-hole, wire-to-pad (pogo pin leads), and general small-signal electrical work. Ordered as a single batch April 22, 2026 (Amazon order # 112-0066205-0960237, 17 line items, $395.31 pre-tax / $423.95 delivered; delivered Apr 23, 2026). Iron tier intentionally chosen at the ~$100 Hakko sweet spot — above the $40 unregulated-tip trap, below the $300+ pro cartridge systems that are overkill for hobby use.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Hakko FX-888D digital soldering station, 70 W, adjustable 120–899 °F | [B0D4DJW54S](https://www.amazon.com/dp/B0D4DJW54S) | 1 | $121.47 | ACQUIRED |
| Kester 24-6337-0027 63/37 Sn/Pb rosin-core solder, 0.031" / 1 lb | [B0149K4JTY](https://www.amazon.com/dp/B0149K4JTY) | 1 | $48.60 | ACQUIRED |
| KOTTO solder fume extractor, 60 W w/ activated-carbon filter | [B07VWDN29F](https://www.amazon.com/dp/B07VWDN29F) | 1 | $39.99 | ACQUIRED |
| AstroAI digital multimeter, 2000-count auto-ranging | [B071JL6LLL](https://www.amazon.com/dp/B071JL6LLL) | 1 | $29.99 | ACQUIRED |
| Klein Tools 11063W Kurve self-adjusting wire stripper, AWG 10–20 | [B00CXKOEQ6](https://www.amazon.com/dp/B00CXKOEQ6) | 1 | $22.96 | ACQUIRED |
| MG Chemicals 8341 no-clean rosin flux paste, 10 mL syringe | [B09FWB6L5L](https://www.amazon.com/dp/B09FWB6L5L) | 1 | $20.20 | ACQUIRED |
| MG Chemicals 99.9% anhydrous isopropyl alcohol, 16 oz | [B0BZ21DBJ6](https://www.amazon.com/dp/B0BZ21DBJ6) | 1 | $17.35 | ACQUIRED |
| Kaisi heat-resistant silicone repair mat, 17.7" × 11.8" | [B07DGVRYL3](https://www.amazon.com/dp/B07DGVRYL3) | 1 | $11.99 | ACQUIRED |
| Chemtronics Soder-Wick #60-3-5 desoldering braid, 0.075" × 5 ft | [B01I7Q2ULA](https://www.amazon.com/dp/B01I7Q2ULA) | 1 | $11.76 | ACQUIRED |
| 3M Virtua CCS safety glasses, clear anti-fog | [B00AEXKR4C](https://www.amazon.com/dp/B00AEXKR4C) | 1 | $11.59 | ACQUIRED |
| BEEYUIHF no-clean liquid soldering flux, dropper bottle | [B0G2G6WFPZ](https://www.amazon.com/dp/B0G2G6WFPZ) | 1 | $9.99 | ACQUIRED |
| AORAEM helping-hands w/ 4 flex arms + magnifier | [B08DNMT96W](https://www.amazon.com/dp/B08DNMT96W) | 1 | $8.99 | ACQUIRED |
| QWORK mini heat gun, 300 W / 200–450 °C | [B09NDCCW29](https://www.amazon.com/dp/B09NDCCW29) | 1 | $8.97 | ACQUIRED |
| Hakko T18-D16 chisel tip, 1.6 mm | [B004OR9BV4](https://www.amazon.com/dp/B004OR9BV4) | 1 | $8.99 | ACQUIRED |
| Hakko T18-D12 chisel tip, 1.2 mm | [B004OR6BU8](https://www.amazon.com/dp/B004OR6BU8) | 1 | $8.99 | ACQUIRED |
| T18-compatible heat-set insert tip kit, 7-piece, M2/M2.5/M3/M4/M5/M6/M8 | [B0CS662NVK](https://www.amazon.com/dp/B0CS662NVK) | 1 kit (7 tips) | $13.93 | ACQUIRED (delivered May 11) |
| Heat-shrink tubing assortment kit, 2:1 ratio, assorted sizes/colors | [B0FRNMXN6Q](https://www.amazon.com/dp/B0FRNMXN6Q) | 1 | $6.99 | ACQUIRED |
| Disposable flux brushes, horsehair, 1/2" × 6" (pack) | [B07PHG2DQY](https://www.amazon.com/dp/B07PHG2DQY) | 1 pk | $6.49 | ACQUIRED |

## 15. 3D printing equipment and filaments (Bambu Lab direct)

All purchased direct from us.store.bambulab.com (not via Amazon). Covers the printer itself (H2C AMS Combo), AMS expansion units (AMS HT × 2, AMS 2 Pro), hotends / nozzles / build plate, vision encoder, PTFE adapters, and every filament refill since the printer arrived. §13 holds the separate Amazon-sold filaments (SpoolHaus PEBA, Siraya Tech Flex TPU) — kept separate because the vendor and receipt trail are distinct.

Receipts grouped by order; each line in the table is one shipment. See Bambu Lab order history for the per-SKU breakdown.

| Order date | Bambu order # | Contents | $ | Status |
|---|---|---|---|---|
| 2026-03-22 | us712460111015776257 | Bambu Lab H2C — H2C AMS Combo (printer + integrated AMS) | $2,399.00 | ACQUIRED |
| 2026-03-22 | us712460111015776257 | Vision Encoder (H2 Series) | $78.75 | ACQUIRED |
| 2026-03-22 | us712460111015776257 | Bambu Engineering Plate (H2C) | $49.49 | ACQUIRED |
| 2026-03-22 | us712460111015776257 | Hotends + nozzles — 0.4 TC nozzle ×2, 0.4 hotend (L) ×2, 0.2 induction hotend (R) ×2 | $203.64 | ACQUIRED |
| 2026-03-22 | us712460111015776257 | Filament — TPU 95A HF ×2, ABS ×2, PA6-CF ×2, PLA Matte ×2, PETG Basic ×2 (1 kg ea) | $349.70 | ACQUIRED |
| 2026-03-22 | us712460111015776257 | NE sales tax (5.5% state + 1.75% city) | $223.33 | ACQUIRED |
| 2026-03-23 | us712597240994926592 | Liquid glue + shipping + tax | $25.71 | ACQUIRED |
| 2026-04-01 | us715792490246602753 | H2C Induction Hotend (R) 0.8mm HS ×1, H2C Induction Hotend (R) 0.4mm HS ×1, ASA Blue ×1, PLA Matte Marine Blue refill ×2, PLA Matte Charcoal ×4 (bulk) | $217.00 | ACQUIRED |
| 2026-04-03 | us716485517830578177 | PETG Basic Black refill ×4 (bulk), ABS Black refill ×4 (bulk) | $120.06 | ACQUIRED |
| 2026-04-06 | us717877837343809537 | Bambu Lab AMS HT ×2 | $278.00 | ACQUIRED |
| 2026-04-06 | us717877837343809537 | Bambu 4-in-1 PTFE Adapter ×1 | $7.99 | ACQUIRED |
| 2026-04-06 | us717877837343809537 | Shipping + NE tax | $28.23 | ACQUIRED |
| 2026-04-08 | us718417332286169089 | Bambu Lab AMS 2 Pro ×1 | $299.00 | ACQUIRED |
| 2026-04-08 | us718417332286169089 | AMS 2 Pro Switching Adapter ×1 | $32.99 | ACQUIRED |
| 2026-04-08 | us718417332286169089 | Bambu 4-in-1 PTFE Adapter ×1 | $7.99 | ACQUIRED |
| 2026-04-08 | us718417332286169089 | ASA Aero filament, White 46100, 1 kg ×2 | $99.98 | ACQUIRED |
| 2026-04-08 | us718417332286169089 | NE tax | $31.90 | ACQUIRED |
| 2026-04-13 | us720254914668109825 | TPU for AMS Black refill ×2 + shipping + tax | $82.54 | ACQUIRED |
| 2026-04-19 | us722538751263612929 | TPU 90A Black ×2, TPU 85A Black ×2 | $186.57 | ACQUIRED |
| 2026-04-21 | us722988823976337409 | PETG Translucent Clear ×4 (bulk) + shipping + tax | $81.46 | ACQUIRED |
| 2026-04-27 | us725322381210451969 | PETG Basic Black 30105 refill 1 kg ×10 (bulk) | $139.36 | ACQUIRED |
| 2026-04-28 | us725539918437957633 | PET-CF Black 71100 filament 1 kg ×2 | $182.30 | ACQUIRED |
| 2026-04-30 | us726560430730719233 | PET-CF nozzle kit: R 0.8mm HF HS hotend + L 0.8mm HF TC nozzle + L 0.6mm SF TC nozzle | $211.78 | ACQUIRED (delivered May 18) |
| 2026-05-04 | us728013517860630529 | Dual Extruder Unit (H2C) ×1 — replacement extruder | $193.05 | ACQUIRED |
| 2026-05-04 | us728027710789775361 | Bambu Lab H2C (AMS Combo) — second printer | $2,572.93 | ACQUIRED |
| 2026-05-25 | us735568811268960257 | PETG Basic Black 30105 ×10 + PETG Translucent Clear 32101 ×10 (1 kg refills, bulk) | $278.72 | ACQUIRED (delivered May 29) |
| **§15 subtotal — 15 orders (15 ACQUIRED)** | | | **ACQUIRED $8,381.47** | |

## 16. Laser welding / cleaning / cutting

Handheld 3-in-1 laser system (welding, cleaning, cutting) used on the stainless pressure vessel and related SS fabrication. Purchased direct from the manufacturer; not on Amazon.

| Order date | Vendor / order # | Item | $ | Status |
|---|---|---|---|---|
| 2026-04-06 | XLaserlab (xlaserlab.com) — order #XLaserlab3271 | XLaserlab X1 Pro 3-in-1 Laser Welder / Cleaner / Cutter — X1 Pro Ultimate Pack (incl. single wire feeder) | $3,899.00 | ACQUIRED |

## 17. Domain / infrastructure

Internet infrastructure purchases. Currently just the product domain; additional infra (web hosting, email, SSL etc.) will land here as it's added.

| Order date | Vendor / order # | Item | $ | Status |
|---|---|---|---|---|
| 2026-03-22 | Namecheap — order #197680608 | homesodamachine.com — premium domain, 1-year term | $599.00 | ACQUIRED |

## 18. Capitalized contract labor — AI-assisted engineering

Not a physical part — direct cash outlay to Anthropic (Claude) for engineering design services specific to this asset: CAD / CadQuery STEP generation, firmware (ESP32 / RP2040 / S3), electrical design, documentation, BOM research and procurement, regulatory analysis. Under GAAP, contracted labor that produces a specific capital asset is capitalized into the asset's cost basis — same line as paying a mechanical-engineering firm for drawings. Booked here at the actual invoice amount, not at any implied hourly rate.

Scope reminder: 2026 YTD only (Jan 1 → Apr 22, 2026). Pre-2026 Claude spend is out of scope per ledger conventions (see intro). Owner / founder time is also NOT on this ledger — sweat equity, un-booked.

| Date range | Type | # of receipts | $ |
|---|---|---|---|
| 2026-01-17 → 2026-04-18 | Claude Pro subscription (via Apple iOS in-app purchase) | 4 × $20.00 | $80.00 |
| 2026-03-03 | Anthropic API — one-time prepaid credit | 1 | $50.00 |
| 2026-03-12 → 2026-04-22 | Anthropic API — auto-recharges + prepaid top-ups (ramp-up to ~$60/day by mid-April) | 49 | $2,477.92 |
| **§18 subtotal** | | **54 receipts** | **$2,607.92** |

## 19. Video / marketing capture equipment

Storage and capture gear used to record print runs, fab work, and assembled-product footage for marketing material. Distinct from §15 (printer + filaments) and §14 (bench tools) because the spend is for documentation and content output rather than parts that go into the appliance.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| SanDisk Ultra Fit USB 3.1 256 GB low-profile flash drive (SDCZ430-256G-G46) | [B07857Y17V](https://www.amazon.com/dp/B07857Y17V) | 1 | $45.41 | ACQUIRED (delivered Mon May 4) |

## 20. McMaster-Carr direct

Industrial-supply orders direct from McMaster-Carr (mcmaster.com). First McMaster line item on the ledger; opens as a new vendor row in the breakdown.

| Order date | McMaster order # | Item | $ | Status |
|---|---|---|---|---|
| 2026-05-10 | 7139410 / 0510DBREDENSTEINER | 316 SS Ultra-Low-Profile SHCS, M3 × 0.50 × 8 mm (P/N 91223A413) — shelf spare (superseded by M3×6, then obsolete) | $59.67 | ACQUIRED (delivered May 13, obsolete) |
| 2026-05-22 | 7833043 / 0522DBREDENSTEINER | 316 SS Ultra-Low-Profile SHCS, M3 × 0.50 × 6 mm (P/N 91223A412) — shelf spare (obsolete on arrival) | $51.69 | ACQUIRED (delivered May 23, obsolete) |

---

## Still needed — LIKELY-TO-BUY

| Part | Notes |
|---|---|
| **Additional flavor-manifold solenoids** | Manifold diagram needs 12 valves (V-A through V-J plus V-K-A and V-K-B); current Beduan B07NWCQJK9 count across orders is short. Verify qty per order, then top up. |
| **Google Pixel 10a unlocked Android phone, 128 GB Obsidian (2026 model)** | Android development handset for the soda-machine app's Android side (`android/`). [B0GHRHXVN1](https://www.amazon.com/dp/B0GHRHXVN1). |

---

## Totals

| Status | $ |
|---|---|
| ACQUIRED — hardware, tools & infra (§§1–17, 19, 20) | [$25,307.76](LEDGER_ACQUIRED_HW) |
| ACQUIRED — capitalized contract labor (§18) | [$2,607.92](LEDGER_LABOR) |
| ACQUIRED (combined) | [$27,915.68](LEDGER_ACQUIRED_COMBINED) |
| ON-ORDER | [$46.89](LEDGER_ON_ORDER) |
| MISSING — paid, not received (§1 copper bar) | [$42.89](LEDGER_MISSING) |
| LIKELY-TO-BUY | $0.00 |
| **Grand total — cash outlay** | [$28,005.46](LEDGER_GRAND_TOTAL) |

ACQUIRED hardware by section:

| § | Section | $ |
|---|---|---|
| 1 | Pressure vessel / carbonator fabrication | [$3,736.30](LEDGER_SEC1) |
| 2 | CO2 subsystem (incl. Lillium prototype carbonator $1,129) | [$1,785.10](LEDGER_SEC2) |
| 3 | Water supply + backflow prevention | [$808.63](LEDGER_SEC3) |
| 4 | Carbonator plumbing | [$241.68](LEDGER_SEC4) |
| 5 | Flavor subsystem | [$817.29](LEDGER_SEC5) |
| 6 | Refrigeration | [$1,867.53](LEDGER_SEC6) |
| 7 | Dispensing end | [$211.46](LEDGER_SEC7) |
| 8 | Electronics — controllers | [$62.46](LEDGER_SEC8) |
| 9 | Electronics — I/O, drivers, sensors, power | [$662.83](LEDGER_SEC9) |
| 10 | User interface | [$146.45](LEDGER_SEC10) |
| 11 | Enclosure hardware | [$111.64](LEDGER_SEC11) |
| 12 | Shop / bench infrastructure | [$345.28](LEDGER_SEC12) |
| 13 | Printing consumables | [$1,065.63](LEDGER_SEC13) |
| 14 | Soldering + small-signal tools | [$409.24](LEDGER_SEC14) |
| 15 | 3D printing equipment + filaments (Bambu direct) | [$8,381.47](LEDGER_SEC15) |
| 16 | Laser welding / cleaning / cutting | [$3,899.00](LEDGER_SEC16) |
| 17 | Domain / infrastructure | [$599.00](LEDGER_SEC17) |
| 19 | Video / marketing capture | [$45.41](LEDGER_SEC19) |
| 20 | McMaster-Carr direct | [$111.36](LEDGER_SEC20) |

Notes:
- **MISSING** = paid but never received (no refund pursued) — a real cash outlay, tracked apart from ACQUIRED.
- **ON-ORDER** is the sum of in-transit rows (filter the tables by status); the figure above stays current via the script.

## Sources
[value](NAME) texts are updated by:
- `/hardware/_ledger_totals.py`
