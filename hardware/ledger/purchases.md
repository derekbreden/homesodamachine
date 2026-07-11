# Purchases

Capital expenditure ledger for the soda-flavor-injector project. Scope: **2026 calendar year only**. Compiled from Amazon order history, direct-from-vendor receipts (Bambu Lab, XLaserlab, Namecheap), and capitalized contract labor (Anthropic / Claude API + subscription for AI-assisted engineering — CAD, firmware, electrical design, documentation, procurement research). Every item is either already in-hand (**ACQUIRED**), placed but not yet arrived (**ON-ORDER**), or identified as a planned purchase (**LIKELY-TO-BUY**).

This is the **purchase ledger** — every buy event, kept for tax records and complete sourcing history. It is not a per-unit bill of materials. Views over this ledger live in sibling files:

- [bom.md](/hardware/ledger/bom.md) — parts allocated per-unit in the current production design (per-unit qty, unit-cost math).
- [tools.md](/hardware/ledger/tools.md) — active tools with tool-specific metadata (working envelopes, capacities, manufacturer references).
- [inventory.md](/hardware/ledger/inventory.md) — current-state inventory for items not in bom.md or tools.md (consumables, spares, abandoned parts, diagnostic purchases, donor units, fab fixtures, aggregated counts).

Each row below is a purchase event; the same SKU may appear as multiple rows if reordered. Capitalized contract labor (Anthropic / Claude API) is recorded here in §18 as cash outlays.

Price figures are the **as-paid** cost — item price plus the order's actual sales tax and shipping (for multi-item orders, the order's tax/shipping is allocated across items by price). Bundled rows carry the shipment total, not the per-item unit price. Only cash outlays (including contracted labor via Anthropic) are on this ledger.

---

## 1. Pressure vessel / carbonator fabrication

Stainless pressure-vessel fabrication: 316 SS round-tube body + 1/4" laser-cut 316 SS end-cap plates (direct-tapped 1/4" NPT), welding/forming tools, drill-tap tooling, and the hydro/pressure-test rig. Racetrack 304 SS stock is retained as fallback (see [inventory.md](/hardware/ledger/inventory.md)).

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| VEVOR Slip Roll Machine, 24" forming width, 16 ga. Order #112-4780540-1769027, placed April 16, 2026 | [B0DZP1VBZY](https://www.amazon.com/dp/B0DZP1VBZY) | 1 | $235.94 | ACQUIRED |
| VEVOR 12-ton Hydraulic Shop Press (for dishing dies). Order #112-1627637-9419449, placed April 14, 2026 | [B0BZ7YY3CP](https://www.amazon.com/dp/B0BZ7YY3CP) | 1 | $155.50 | ACQUIRED |
| Weldpro 3-Tier Welding Cart. Order #112-8830635-1424267, placed April 6, 2026 | [B08G5CW3DY](https://www.amazon.com/dp/B08G5CW3DY) | 1 | $193.04 | ACQUIRED |
| Blue Demon ER308L .030 stainless MIG wire, 2 lb. Order #112-8830635-1424267, placed April 6, 2026 | [B0025Q2HIU](https://www.amazon.com/dp/B0025Q2HIU) | 1 | $23.95 | ACQUIRED |
| RX Weld argon regulator / flowmeter. Order #112-8830635-1424267, placed April 6, 2026 | [B08P5BNHBX](https://www.amazon.com/dp/B08P5BNHBX) | 1 | $31.09 | ACQUIRED |
| Airgas #8162013342 — argon size-80 cylinder, CGA-580 (CY-AR 80) | airgas.com (Lincoln NE) | 1 | $399.31 | ACQUIRED |
| Airgas #8162013342 — argon fill, 85 SCF (AR 80) | airgas.com (Lincoln NE) | 1 | $75.20 | ACQUIRED |
| Strong Hand magnetic V-pads welding magnet kit. Order #112-8830635-1424267, placed April 6, 2026 | [B00JXDSVA6](https://www.amazon.com/dp/B00JXDSVA6) | 1 | $29.21 | ACQUIRED |
| MAXMAN stainless steel wire brush set. Order #112-8830635-1424267, placed April 6, 2026 | [B08L7RXVG5](https://www.amazon.com/dp/B08L7RXVG5) | 1 | $12.22 | ACQUIRED |
| 1/4" NPT female weld bung, 304 SS stepped flange. Order #112-0019658-3684217, placed Apr 4, 2026 | [B07QNV8796](https://www.amazon.com/dp/B07QNV8796) | 5 | $8.57 ea | ACQUIRED |
| 4pc 1/4" NPT male hex nipple, 316 SS 5000 psi. Order #112-0019658-3684217, placed April 4, 2026 | [B0GD1QBLQ3](https://www.amazon.com/dp/B0GD1QBLQ3) | 1 pk | $16.29 | ACQUIRED |
| Millrose PTFE thread seal tape. Order #112-0019658-3684217, placed April 4, 2026 | [B07C9ZV4PG](https://www.amazon.com/dp/B07C9ZV4PG) | 1 | $21.52 | ACQUIRED |
| Viva Doria 100% pure food-grade citric acid, fine grain, 2 lb. Order #112-8083402-8740244, placed April 12, 2026 | [B0C5NQM8S1](https://www.amazon.com/dp/B0C5NQM8S1) | 1 | $9.99 | ACQUIRED |
| Cambro 6 QT square polycarbonate food container. Order #112-5291452-2765065, placed Apr 12, 2026 | [B001BZEQ44](https://www.amazon.com/dp/B001BZEQ44) | 1 | $21.45 | ACQUIRED |
| findmall ER308L .035 MIG wire, 10 lb spool. Order #114-6485602-3013015, placed April 19, 2026 | [B0C52XQB39](https://www.amazon.com/dp/B0C52XQB39) | 1 | $90.68 | ACQUIRED |
| PGN ER308L .030 MIG wire, 10 lb spool | [B09WRZDBPN](https://www.amazon.com/dp/B09WRZDBPN) | 1 | — | CANCELLED |
| STARTECHWELD ER316L .030 MIG wire, 10 lb spool, 8" OD / 2" center bore. Order #112-2295053-5101056, placed April 24, 2026 | [B09BKFBXT9](https://www.amazon.com/dp/B09BKFBXT9) | 1 | $129.50 | ACQUIRED |
| Caiman premium goat-grain TIG / multi-task welding gloves. Order #114-0933175-3371439, placed April 19, 2026 | [B07T6VLSK3](https://www.amazon.com/dp/B07T6VLSK3) | 1 | $23.05 | ACQUIRED |
| Caiman premium goat-grain TIG welding gloves. Order #114-5597505-0433853, placed April 17, 2026 | [B07T1NYXHM](https://www.amazon.com/dp/B07T1NYXHM) | 1 | $23.05 | ACQUIRED |
| YTKavq 1/4" × 2" × 12" C110 pure copper flat bar, soft-annealed. Order #112-4953236-4101019, placed April 23, 2026 | [B0DR2PX6TT](https://www.amazon.com/dp/B0DR2PX6TT) | 1 | $42.89 | MISSING (delivered-but-empty 2026-04-23; no refund pursued) |
| YTKavq 1/4" × 2" × 12" C110 pure copper flat bar. Order #112-0935480-2206657, placed April 22, 2026 | [B0DR2PX6TT](https://www.amazon.com/dp/B0DR2PX6TT) | 1 | $42.89 | ACQUIRED |
| 304 SS 4" × 6" × 1/16" (16 ga / 1.5 mm) sheet, 2-pk. Order #112-8776391-7335431, placed April 22, 2026 | [B0DFXXQZD3](https://www.amazon.com/dp/B0DFXXQZD3) | 3 pk | $48.24 | ACQUIRED |
| 304 SS 4" × 4" × 0.04" (19 ga / 1 mm) sheet, 4 pc. Order #112-6588057-9595403, placed April 22, 2026 | [B0C5LWVLCD](https://www.amazon.com/dp/B0C5LWVLCD) | 1 | $13.93 | ACQUIRED |
| Drill America 1/4" NPT HSS pipe tap + 1-1/2" OD round die kit. Order #114-8354589-7380236, placed April 19, 2026 | [B0DXN1LDKT](https://www.amazon.com/dp/B0DXN1LDKT) | 1 | $20.16 | ACQUIRED |
| MOTOKU 38 mm / 1.5" OD heavy-duty round die handle. Order #114-8354589-7380236, placed April 19, 2026 | [B073ZX58PH](https://www.amazon.com/dp/B073ZX58PH) | 1 | $15.00 | ACQUIRED |
| Tap Magic EP-Xtra pipe-tap cutting fluid, 16 oz (size variant on listing B00DHMHSGM). Order #112-3539135-2289004, placed April 24, 2026 | [B00DHMHSGM](https://www.amazon.com/dp/B00DHMHSGM) | 1 | $17.01 | ACQUIRED |
| WEN 4208T 2.3 A 8" 5-speed benchtop drill press. Order #112-2348373-7907448, placed April 29, 2026 | [B08ZVT5JKC](https://www.amazon.com/dp/B08ZVT5JKC) | 1 | $111.54 | ACQUIRED |
| Drill America 1/4"–1-1/8" tap-capacity adjustable tap wrench, DWT series. Order #112-2348373-7907448, placed April 29, 2026 | [B00DMEYTLW](https://www.amazon.com/dp/B00DMEYTLW) | 1 | $33.02 | ACQUIRED |
| Drill America DWT64006 Qualtech HSS pipe tap, 1/4"-18 NPT. Order #112-2348373-7907448, placed April 29, 2026 | [B01DZD1Y9Y](https://www.amazon.com/dp/B01DZD1Y9Y) | 1 | $10.54 | ACQUIRED |
| LingGan 1/4-18 NPT M35 cobalt steel pipe tap, TiN-coated. Order #112-8743279-3935456, placed May 17, 2026 | [B0D7HM5R3C](https://www.amazon.com/dp/B0D7HM5R3C) | 1 | $13.93 | ACQUIRED (delivered May 19) |
| Brown & Sharpe spring-loaded tap guide, 1/2" hardened shank. Order #112-2348373-7907448, placed April 29, 2026 | [B005317ZMC](https://www.amazon.com/dp/B005317ZMC) | 1 | $27.45 | ACQUIRED |
| Mollom 124 mm / 4-7/8" HSS M42 bi-metal hole saw with arbor + pilot bits. Order #112-2348373-7907448, placed April 29, 2026 | [B0BZQ4J5B1](https://www.amazon.com/dp/B0BZQ4J5B1) | 1 | $19.19 | ACQUIRED |
| 12 mm Baltic birch plywood, 1/2" × 8" × 8", B/BB grade (2 pc). Order #112-2348373-7907448, placed April 29, 2026 | [B0DP8597Q2](https://www.amazon.com/dp/B0DP8597Q2) | 1 box | $10.71 | ACQUIRED |
| ACXFOND 1/4" MDF boards, 8" × 10" (20 pk). Order #112-2348373-7907448, placed April 29, 2026 | [B0F1FJYDQ3](https://www.amazon.com/dp/B0F1FJYDQ3) | 1 pk | $25.73 | ACQUIRED |
| Franklin International 1412 Titebond III wood glue, 4 oz. Order #112-2348373-7907448, placed April 29, 2026 | [B0002YQ378](https://www.amazon.com/dp/B0002YQ378) | 1 | $5.34 | ACQUIRED |
| Storystore 4" heavy-duty steel C-clamps (4 pk). Order #112-2348373-7907448, placed April 29, 2026 | [B0DHX78G97](https://www.amazon.com/dp/B0DHX78G97) | 1 pk | $21.44 | ACQUIRED |
| Bosch DSB1013 1" × 6" Daredevil Standard Spade Bit. Order #111-4630388-1572202, placed April 29, 2026 | [B001NGPAA0](https://www.amazon.com/dp/B001NGPAA0) | 1 | $5.35 | ACQUIRED |
| Drill Hulk DHCO26 9/64" (3.57 mm) M35 cobalt jobber twist drill bits, 12-pack — blind rod-register drilling in the 316 SS end-cap plates. Order #112-3161139-1981039, placed June 15, 2026 | [B07XNNNC5Y](https://www.amazon.com/dp/B07XNNNC5Y) | 1 pk (12) | $18.43 | ACQUIRED (delivered Jun 16) |
| WEN BA4555 5" benchtop metal-cutting band saw — horizontal cutoff with vise + length stop, 0–60° miter, variable 125–260 FPM, 56-1/2" blade. Square, repeatable cuts of the 1/8" 316L level-sensing rods (carbonator + flavor reservoir + lite reservoir pocket). Order #112-0741371-9657825, placed June 17, 2026 | [B09XWQCNGT](https://www.amazon.com/dp/B09XWQCNGT) | 1 | $362.73 | ON-ORDER (arriving Jun 24–25) |
| Imachinist S56121224SS 56-1/2" × 1/2" × 24 TPI M42 bi-metal bandsaw blade (stainless) — 1/8" rod cutoff blade for the BA4555. Order #112-3334877-3267411, placed June 17, 2026 | [B0B7GDTX9H](https://www.amazon.com/dp/B0B7GDTX9H) | 1 | $19.83 | ACQUIRED (delivered Jun 21) |
| Ultra Duster Canned Air Industrial Strength 10 oz, 4-pack. Order #112-6571709-7582668, placed May 8, 2026 | [B07JRBR1MM](https://www.amazon.com/dp/B07JRBR1MM) | 1 pk (4× 10 oz) | $24.51 | ACQUIRED (delivered May 12) |
| Hgnova 15-pc 1064 nm laser protective lens, D18 × 2 mm, 1000–3000 W handheld 4-in-1 laser welder. Order #112-3421913-9021801, placed April 30, 2026 | [B0FF38DY1Z](https://www.amazon.com/dp/B0FF38DY1Z) | 1 pk (15) | $19.29 | ACQUIRED |
| SENCTRL 0–200 PSI glycerin-filled pressure gauge, 2.5" dial, 1/4" NPT lower mount, SS case. Order #112-2086169-3211445, placed May 4, 2026 | [B0BCHMQLFB](https://www.amazon.com/dp/B0BCHMQLFB) | 1 | $10.72 | ACQUIRED (delivered Tue May 5) |
| ChillWaves brass 1/4" NPT outer-hex-head pipe plugs, 12-pack. Order #112-2086169-3211445, placed May 4, 2026 | [B0C4LP4B3D](https://www.amazon.com/dp/B0C4LP4B3D) | 1 pk (12) | $11.79 | ACQUIRED (delivered Tue May 5) |
| Milton 727 industrial M-STYLE® 1/4" MNPT air plug, 10-pack, alloy steel. Order #112-2086169-3211445, placed May 4, 2026 | [B000PDWI4S](https://www.amazon.com/dp/B000PDWI4S) | 1 pk (10) | $15.02 | ACQUIRED (delivered Tue May 5) |
| BEAMNOVA hydrostatic test pump, 0–726 PSI / 0–50 bar / 0–5 MPa, 3.17 gal water reservoir, 4.43 ft × 1/4" hydraulic hose with 1/2" female gasket-swivel testpiece end, copper pump body + check valve, built-in 3-unit dial gauge. Order #112-6990924-2823418, placed May 4, 2026 | [B07T45XTD1](https://www.amazon.com/dp/B07T45XTD1) | 1 | $93.30 | ACQUIRED (delivered Tue May 5) |
| KOOTANS 1/2" NPT male × 1/4" NPT male solid brass reducing hex nipple, 4-pack. Order #112-1128563-6922646, placed May 4, 2026 | [B07P7ZRZMD](https://www.amazon.com/dp/B07P7ZRZMD) | 1 pk (4) | $12.86 | ACQUIRED (delivered Tue May 5) |
| OnlineMetals #12498 — 5" OD × 0.065" wall 316 welded SS round tube, cut to 6.0" length, MTRs required | onlinemetals.com | 10 | $736.73 | ACQUIRED |
| SendCutSend order SG019619 — 1/4" 316 SS circular endcap plates | sendcutsend.com | 20 | $621.19 | ACQUIRED |
| SendCutSend order SQ65E969 — 304 SS 0.048" body blanks ×2 (plan-B spare/practice) | sendcutsend.com | 2 | $60.19 | ACQUIRED |
| SendCutSend order SV07U813 — 304 SS 0.060" racetrack end-cap blanks ×4 (plan-B spare) | sendcutsend.com | 4 | $45.52 | ACQUIRED |
| SendCutSend order SP54G453 — 304 SS 0.048" body half-sheets ×10 (plan-B spare) | sendcutsend.com | 10 | $134.38 | ACQUIRED |
| SendCutSend order S064D925 — 0.060" 316 SS Touch-Flo under-counter plates | sendcutsend.com | 10 | $36.29 | ACQUIRED (delivered May 14) |
| SendCutSend order S4177511 — 0.060" 316 SS Touch-Flo under-counter plates | sendcutsend.com | 23 | $34.78 | ON-ORDER (placed Jun 18, 2026; invoice dated Jun 19; paid Visa, in production) |
| Cantesco P101S-A red visible dye penetrant, solvent-removable aerosol — dye-penetrant (PT) leak/crack inspection of the end-cap closure fillet welds before hydro (step 6). Order #112-1089976-3089830, placed June 16, 2026 | [B00T46ZH5E](https://www.amazon.com/dp/B00T46ZH5E) | 1 | $24.45 | ACQUIRED (delivered Jun 19) |
| Cantesco D101-A non-aqueous wet developer, white, 12 oz aerosol — PT developer that draws the penetrant back out of a defect as a visible indication. Order #112-9519199-9509821, placed June 16, 2026 | [B008BJCOLK](https://www.amazon.com/dp/B008BJCOLK) | 1 | $15.88 | ACQUIRED (delivered Jun 16) |
| Cleanroom wipes, 9" × 9", cellulose/polyester Grade A 68 GSM, lint-free (150 pcs) — controlled PT penetrant wipe-off (dampened with the already-owned isopropyl alcohol, not sprayed) + low-lint surface for reading indications. Order #112-1089976-3089830, placed June 16, 2026 | [B0GD16CMYL](https://www.amazon.com/dp/B0GD16CMYL) | 1 pk (150) | $17.15 | ACQUIRED (delivered Jun 16) |

## 2. CO2 subsystem

Cylinders, regulator, CO2 line, push-to-connect adapters for the CO2 side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Lillium under-sink carbonated soda maker + 3-way sparkling-water faucet, black, 110–120 V AC (SKU 102) | [liliumfaucet.com](https://liliumfaucet.com/) | 1 | $1,129.00 | ACQUIRED |
| TAPRITE E-T742 CO2 dual-gauge primary regulator, CGA-320. Order #114-0170640-0334629, placed February 13, 2026 | [B00L38DRD0](https://www.amazon.com/dp/B00L38DRD0) | 1 | $96.47 | ACQUIRED |
| WELLBOM 0–120 PSI CO2 dual-gauge regulator, CGA-320, with pressure-release valve. Order #112-8121022-3791448, placed June 22, 2026 | [B0G13P5PMY](https://www.amazon.com/dp/B0G13P5PMY) | 1 | $49.32 | ON-ORDER (arriving Thu Jun 25) |
| Airgas #8160436286 — prototype CO2 cylinder, 5 lb aluminum food-grade, CGA-320 (CY-CD FG5) | airgas.com (Lincoln NE) | 1 | $133.10 | ACQUIRED |
| Airgas #8160436286 — CO2 fill, 5 lb food-grade (prototype cylinder) | airgas.com (Lincoln NE) | 1 | $47.93 | ACQUIRED |
| Airgas #8162013342 — testing CO2 cylinder, 5 lb aluminum food-grade, CGA-320 (CY-CD FG5) | airgas.com (Lincoln NE) | 1 | $133.10 | ACQUIRED |
| Airgas #8162013342 — CO2 fill, 5 lb food-grade (testing cylinder) | airgas.com (Lincoln NE) | 1 | $67.38 | ACQUIRED |
| 10 ft 5/16" ID beer CO2 line w/ 4 hose clamps. Order #114-7655402-1447440, placed February 13, 2026 | [B0D1RB3TF6](https://www.amazon.com/dp/B0D1RB3TF6) | 1 | $13.50 | ACQUIRED |
| DERPIPE push-to-connect 5/16" tube x 1/4" NPT (5 pk). Order #114-2491581-3257040, placed February 14, 2026 | [B09LXVGPG7](https://www.amazon.com/dp/B09LXVGPG7) | 1 pk | $10.71 | ACQUIRED |
| VUYOMUA 0.8 gal SS portable air tank (bench test fixture). Order #112-5187846-6776238, placed April 16, 2026 | [B0BV6FMMJP](https://www.amazon.com/dp/B0BV6FMMJP) | 1 | $60.05 | ACQUIRED |
| Control Devices SV-100 safety valve, 1/4" NPT, 100 psi (spare PRV; superseded by SV-125). Order #112-7814251-3174665, placed Apr 12, 2026 | [B0D361X97X](https://www.amazon.com/dp/B0D361X97X) | 2 | $8.03 ea | ACQUIRED |
| Interstate Pneumatics WR1110 1/4" NPT in-Line 90 PSI fixed pre-set pressure regulator, 230 PSI max inlet, aluminum body. Order #112-6323725-5423434, placed May 13, 2026 | [B07J2L8LF3](https://www.amazon.com/dp/B07J2L8LF3) | 1 | $25.66 | ACQUIRED (delivered May 17) |
| Control Devices SV-125 safety valve, 1/4" NPT, 125 psi set pressure, 49 SCFM relief, brass. Order #112-6323725-5423434, placed May 13, 2026 | [B01G2F6EMY](https://www.amazon.com/dp/B01G2F6EMY) | 1 | $8.03 | ACQUIRED (delivered May 17) |
| Fresh Water Systems order WEBFWS100675224 — JG 1/4" NPTF male connector (×10) + 1/4" union elbow PP0308E (×10) | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order (2 × bag of 10) | $44.11 | ACQUIRED (delivered May 19) |

## 3. Water supply + backflow prevention

Feed-water inlet, filter, ASSE 1022 backflow preventer and its vent-line hardware, quick-connect tubing for the potable side feeding the carbonator.

| Part | Link | Qty | $ | Status |
|---|---|---|---|---|
| Multiplex 19-0897 ASSE 1022 backflow preventer, 3/8" NPT × 3/8" MFL | [howdybrewer.com](https://www.howdybrewer.com/products/multiplex-backflow-preventor-assembly-1022-3-8-npt-x-3-8-mfl) | 1 | $61.49 | ACQUIRED |
| Multiplex 19-0897 ASSE 1022 backflow preventer, 3/8" NPT × 3/8" MFL | [midwestbev.com](https://www.midwestbev.com/products/asse-1022-backflow-preventer) | 4 | $145.80 | ACQUIRED |
| Hooshing 3/8" flare × 1/4" FNPT brass adapter (2 pk). Order #112-4601641-4469804, placed April 16, 2026 | [B0BNHVV6HT](https://www.amazon.com/dp/B0BNHVV6HT) | 1 pk | $10.71 | ACQUIRED |
| brewhardware FFL38BARB38 Swivel Flare Adapter, 3/8" FFL (UNCOMMON) × 3/8" OD hose barb | [brewhardware.com](https://www.brewhardware.com/product_p/ffl38barb38.htm) | 5 | $39.42 | ACQUIRED (delivered) |
| Sealproof 1/4" ID × 3/8" OD food-grade clear PVC, 10 ft. Order #112-9672770-7349862, placed April 16, 2026 | [B07D9DK94V](https://www.amazon.com/dp/B07D9DK94V) | 1 | $8.46 | ACQUIRED |
| Waterdrop 15UC-UF 0.01 µm inline fridge/ice-maker filter. Order #114-7711911-5865013, placed February 11, 2026 | [B085G9TZ4L](https://www.amazon.com/dp/B085G9TZ4L) | 1 | $67.56 | ACQUIRED |
| HAOCHEN brass angle stop add-a-tee 3/8"×3/8"×1/4". Order #114-7711911-5865013, placed February 11, 2026 | [B0DLKHHGL6](https://www.amazon.com/dp/B0DLKHHGL6) | 1 | $12.86 | ACQUIRED |
| GAGIRA 5Pcs 316L Stainless Steel Coupling, 3/8" NPT Female × 1/4" NPT Female, includes Teflon tape. Order #114-6677442-9807460, placed May 22, 2026 | [B0G2XJGZMQ](https://www.amazon.com/dp/B0G2XJGZMQ) | 1 pk | $18.22 | ACQUIRED |
| LTWFITTING brass 3/8" × 1/4" FNPT reducing coupling (5-pk) | amazon.com (114-9960851-7517853) | 1 pk (5) | $8.56 | ACQUIRED (delivered May 29) |
| Lifevant 32.8 ft 1/4" OD water tubing + 12 quick-connects. Order #114-5825243-4744249, placed February 12, 2026 | [B0DKCZ5W66](https://www.amazon.com/dp/B0DKCZ5W66) | 1 | $10.71 | ACQUIRED |
| Fresh Water Systems order WEBFWS100673540 — black LLDPE tubing: 3/8" OD 25 ft + 1/4" OD 100 ft | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order | $43.29 | ACQUIRED (delivered May 13) |
| John Guest 1/4" OD × 1/8" NPT male push-fit. Order #114-5825243-4744249, placed February 12, 2026 | [B07V6XKZG9](https://www.amazon.com/dp/B07V6XKZG9) | 1 | $5.36 | ACQUIRED |
| John Guest PI1208S acetal bulkhead union (1/4" QC). Order #114-5825243-4744249, placed February 12, 2026 | [B0C1F3QR7N](https://www.amazon.com/dp/B0C1F3QR7N) | 2 | $12.32 ea | ACQUIRED |
| SAMSUNG HAF-QIN-3P carbon block refrigerator filter (3 pk). Order #114-8784211-4965832, placed January 25, 2026 | [B09HR7H8X7](https://www.amazon.com/dp/B09HR7H8X7) | 1 pk | $97.10 | ACQUIRED |
| Yetaha RO 1/4" water flow-adjust valve. Order #114-2734195-8455414, placed March 15, 2026 | [B07GDFWB8R](https://www.amazon.com/dp/B07GDFWB8R) | 1 | $12.86 | ACQUIRED |
| SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand pump. Order #114-4512279-7485822, placed April 1, 2026 | [B0166UBJX4](https://www.amazon.com/dp/B0166UBJX4) | 1 | $48.25 | ACQUIRED |
| Fresh Water Systems order WEBFWS100677333 — Colder 70500 NSF QD insert (×2) + 74600 NSF QD body (×2) + blue 1/4" LLDPE 100 ft + JG PP0208E union tee (×10) | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order (4 items) | $130.45 | ACQUIRED |
| Fresh Water Systems order WEBFWS100677768 — **MTB-0606WP** 3/8"barb × 3/8"MNPT tee (×10, swapped from discontinued MTB-0604WP) + JG PP450822E 1/4" NPTF female adapter (×10) | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order (2 items) | $62.08 | ACQUIRED (delivered Jun 15; UPS 1ZW0062A0297032825; itemized 10× MTB-0606WP + 10× PP450822E. FWS swapped the discontinued MTB-0604WP to MTB-0606WP and credited the $0.60 upcharge, total held at $62.08. 0606's 3/8" MNPT branch ≠ PP450822E 1/4" NPTF — adapters reassign to general stock; branch adapter ordered separately on WEBFWS100682118) |
| Fresh Water Systems order WEBFWS100682118 — JG PP451223W 3/8"NPTF × 3/8"PTC female adapter (bag of 10) + JG PP061208W 3/8"stem × 1/4"PTC reducer stem (bag of 10) | [freshwatersystems.com](https://www.freshwatersystems.com/) | 1 order (2 items) | $81.33 | ACQUIRED (delivered Jun 15; confirmed WEBFWS100682118. Tap-point branch adapter for the MTB-0606WP 3/8" MNPT branch — closes `assembly/internal-plumbing.md` Open items 3) |

## 4. Carbonator plumbing (pressurized side)

Check valves, sparge stone + barb adapter for internal-sparge CO2 carbonation, compression fittings on the water/CO2 pressure side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| ChillWaves 304 SS in-line split check valve 1/4" NPT M×F (silicone seat. Order #112-6570032-9753837, placed April 12, 2026 | [B0DPLBYZB4](https://www.amazon.com/dp/B0DPLBYZB4) | 1 | $18.22 | ACQUIRED |
| ChillWaves 304 SS in-line **Siamese** check valve 1/4" NPT M×F (1-pack). Order #112-0876134-8491423, placed April 24, 2026 | [B0DPL88RHC](https://www.amazon.com/dp/B0DPL88RHC) | 1 | $16.08 | ACQUIRED |
| GASHER 1/4" NPT SS one-way check valve (2 pk). Order #112-9584993-4999458, placed April 24, 2026 | [B0FV2D2FFX](https://www.amazon.com/dp/B0FV2D2FFX) | 1 pk | $15.00 | ACQUIRED |
| GASHER 1/4" NPT SS one-way check valve (2 pk). Order #112-7934476-0257818, placed April 25, 2026 | [B0FV2D2FFX](https://www.amazon.com/dp/B0FV2D2FFX) | 2 pk | $15.00 ea | ACQUIRED |
| LTWFITTING 316 SS 1/4" hose barb × 1/4" MNPT. Order #112-4822227-6802649, placed April 24, 2026 | [B017N4TTMA](https://www.amazon.com/dp/B017N4TTMA) | 1 | $13.65 | ACQUIRED |
| TAISHER 2PCS 316L SS 90° Barstock Street Elbow, 1/4" NPT Male × 1/4" NPT Female. Order #112-2846745-4487464, placed May 13, 2026 | [B0CZ38MYL1](https://www.amazon.com/dp/B0CZ38MYL1) | 1 pk (2) | $22.51 | ACQUIRED (delivered May 17) |
| TAISHER 2PCS 316L SS 90° Barstock Street Elbow, 1/4" NPT M × 1/4" NPT F. Order #112-6323725-5423434, placed May 13, 2026 | [B0CZ38MYL1](https://www.amazon.com/dp/B0CZ38MYL1) | 1 pk (2) | $22.51 | ACQUIRED (delivered May 15) |
| FERRODAY 0.5 µm sintered 316 SS sparge stone, 1/4" barb input (2-set). Order #112-5893072-9403444, placed April 24, 2026 | [B091C5Y6L9](https://www.amazon.com/dp/B091C5Y6L9) | 1 | $14.97 | ACQUIRED |
| ~~Beduan 1/4" male spiral cone atomization nozzle, 316 SS~~. Order #112-0019658-3684217, placed April 4, 2026 | [B07LGPD3GB](https://www.amazon.com/dp/B07LGPD3GB) | 1 | $10.71 | ACQUIRED (superseded) |
| VALVENTO 316 SS 1/4" OD compression × 1/4" NPT adapter (2 pk). Order #112-6216768-3197856, placed April 12, 2026 | [B0DXZZBK7D](https://www.amazon.com/dp/B0DXZZBK7D) | 1 pk | $12.85 | ACQUIRED |
| VALVENTO 1/4" OD 316 SS tube, 12" length (5 pk). Order #112-6216768-3197856, placed April 12, 2026 | [B0F6SYFK48](https://www.amazon.com/dp/B0F6SYFK48) | 1 pk | $18.23 | ACQUIRED |
| TAISHER 304 SS compression square needle valve 1/4". Order #112-4838242-5164262, placed March 14, 2026 | [B0CLXHZZCW](https://www.amazon.com/dp/B0CLXHZZCW) | 1 | $22.51 | ACQUIRED |
| YKEBVPW 1/4" push-connect needle valve flow control. Order #112-4375086-9926652, placed May 30, 2026 | [B0FBFVTNLM](https://www.amazon.com/dp/B0FBFVTNLM) | 1 | $8.03 | ACQUIRED (delivered Jun 1) |

## 5. Flavor subsystem

Peristaltic pumps, solenoids, bag-in-box connector, silicone delivery tubing, barb fittings, bladders, check valves on the flavor side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Kamoer KPHM400-SW3B25 400 ml/min 12 V peristaltic pump (BPT, sold by Kamoer Fluid Tech Shanghai). Orders #114-1015191-6799441 (Feb 18), #112-0545074-9805025 (Feb 23) | [B09MS6C91D](https://www.amazon.com/dp/B09MS6C91D) | 3 | $34.91 ea | ACQUIRED |
| Beduan 12 V 1/4" inlet water solenoid (NC). Orders #114-3476722-1893810 (Feb 22, ×1), #112-0933043-5526613 (Feb 23, ×2), #112-9365343-6646655 (Mar 14, ×2), #112-4838242-5164262 (Mar 14, ×1) | [B07NWCQJK9](https://www.amazon.com/dp/B07NWCQJK9) | 6 | $9.64 ea | ACQUIRED |
| Beduan 12 V 1/4" inlet water solenoid (NC). Order #112-3576572-8551422, placed June 14, 2026 | [B07NWCQJK9](https://www.amazon.com/dp/B07NWCQJK9) | 8 | $9.64 ea | ACQUIRED (delivered Jun 16; with 6 on hand, covers 12-valve flavor manifold) |
| Hosyond 5-pack MG90S 9 g metal-gear micro servo. Order #112-1012254-8551456, placed June 1, 2026 | [B09V5BR7J5](https://www.amazon.com/dp/B09V5BR7J5) | 1 pk (5) | $15.43 | ACQUIRED (delivered Jun 4) |
| NeoFit acetal ball valve — push-fit quarter-turn, food-grade PP body + acetal + EPDM O-ring, 1/4" OD tube (5-pack). Order #112-1012254-8551456, placed June 1, 2026 | [B0DDQC7S3B](https://www.amazon.com/dp/B0DDQC7S3B) | 1 pk (5) | $22.80 | ACQUIRED (delivered Jun 4) |
| Supply Depot Coke-compatible BIB connector, 3/8" red (2 pk). Order #114-4194868-8174607, placed March 2, 2026 | [B0DMFK9B6P](https://www.amazon.com/dp/B0DMFK9B6P) | 1 pk | $21.44 | ACQUIRED |
| Platypus SoftBottle 1 L (bladder donor). Order #114-5256389-4238639, placed March 16, 2026 | [B08PG3GMQ8](https://www.amazon.com/dp/B08PG3GMQ8) | 1 | $25.19 | ACQUIRED |
| Platypus SoftBottle 1 L "Waves" (bladder donor). Order #114-5256389-4238639, placed March 16, 2026 | [B00ZX0ERE2](https://www.amazon.com/dp/B00ZX0ERE2) | 1 | $16.46 | ACQUIRED |
| Platypus Platy 2 L collapsible bottle (bladder donor). Order #114-2469196-8024255, placed Feb 15, 2026 | [B000J2KEGY](https://www.amazon.com/dp/B000J2KEGY) | 1 | $16.13 | ACQUIRED (delivered Feb 16) |
| Platypus Platy 2 L collapsible bottle (bladder donor). Order #112-9869315-7146643, placed Feb 2026 | [B000J2KEGY](https://www.amazon.com/dp/B000J2KEGY) | 2 | $17.33 ea | ACQUIRED |
| Platypus Platy 2 L collapsible bottle (bladder donor). Order #114-3163590-0127432, placed Mar 8, 2026 | [B000J2KEGY](https://www.amazon.com/dp/B000J2KEGY) | 2 | $17.10 ea | ACQUIRED |
| Platypus Hoser hydration tube kit. Orders #114-2469196-8024255 (Feb 15, ×1), #112-0545074-9805025 (Feb 23, ×2) | [B07N1T6LNW](https://www.amazon.com/dp/B07N1T6LNW) | 3 | $26.76 ea | ACQUIRED |
| Platypus Hoser 1 L Hands-Free Hydration Reservoir, Fast Flow Valve. Order #112-4566389-9910625, placed May 30, 2026 | [B002OYMRS8](https://www.amazon.com/dp/B002OYMRS8) | 2 | $51.24 | ACQUIRED |
| JoyTube 3/8" ID food-grade silicone tubing, 10 ft. Order #114-4194868-8174607, placed March 2, 2026 | [B089YGDB55](https://www.amazon.com/dp/B089YGDB55) | 1 | $12.86 | ACQUIRED |
| Metaland 3/8" ID food-grade silicone tubing. Order #112-2018641-1609045, placed March 15, 2026 | [B08L1RS757](https://www.amazon.com/dp/B08L1RS757) | 1 | $8.57 | ACQUIRED |
| Metaland 1/4" ID food-grade silicone tubing. Order #112-2018641-1609045, placed March 15, 2026 | [B08L1ST6ST](https://www.amazon.com/dp/B08L1ST6ST) | 1 | $8.57 | ACQUIRED |
| Metaland 1/2" ID silicone tubing. Order #112-2147768-5852208, placed March 15, 2026 | [B0BC7K5B91](https://www.amazon.com/dp/B0BC7K5B91) | 1 | $10.71 | ACQUIRED |
| Metaland 1/8" ID silicone tubing. Order #114-0818390-2733826, placed February 2, 2026 | [B08XM1V475](https://www.amazon.com/dp/B08XM1V475) | 1 | $9.64 | ACQUIRED |
| Quickun 3/4" ID silicone tubing. Order #112-2018641-1609045, placed March 15, 2026 | [B091SXP7DD](https://www.amazon.com/dp/B091SXP7DD) | 1 | $10.71 | ACQUIRED |
| Pure silicone 3/8" ID × 1/2" OD high-temp tube, 10 ft. Order #112-0019658-3684217, placed April 4, 2026 | [B07XMGHHLK](https://www.amazon.com/dp/B07XMGHHLK) | 1 | $18.22 | ACQUIRED |
| ANPTGHT 1/8" ID × 1/4" OD black silicone tubing. Orders #112-9399398-0475445 (Feb 23, ×2), #114-7711911-5865013 (Feb 11, ×1) | [B0BM4KQ6RT](https://www.amazon.com/dp/B0BM4KQ6RT) | 3 | $13.93 ea | ACQUIRED |
| Rebower brass hose barb 3/8" × 1/8". Order #114-4194868-8174607, placed March 2, 2026 | [B0FP5JX2KS](https://www.amazon.com/dp/B0FP5JX2KS) | 1 | $5.35 | ACQUIRED |
| MAACFLOW SS 1/4" NPT M × 3/8" hose barb (4 pk). Order #112-0019658-3684217, placed April 4, 2026 | [B0DMP77B6S](https://www.amazon.com/dp/B0DMP77B6S) | 1 pk | $13.91 | ACQUIRED |
| YDS butterfly SS W2 hose clamp, 10–16 mm (10 pk). Order #112-0019658-3684217, placed April 4, 2026 | [B07C33VLQ6](https://www.amazon.com/dp/B07C33VLQ6) | 1 pk | $16.30 | ACQUIRED |
| ANPTGHT 1/8" tee fitting, equal barb (5 pk). Order #114-4987669-8550659, placed February 6, 2026 | [B08SBM4DBQ](https://www.amazon.com/dp/B08SBM4DBQ) | 1 pk | $7.50 | ACQUIRED |
| 1/8" plastic check valve, barb one-way (10 pk). Order #114-4987669-8550659, placed February 6, 2026 | [B0CLV9BRL1](https://www.amazon.com/dp/B0CLV9BRL1) | 1 pk | $8.57 | ACQUIRED |
| Green silicone duckbill check valve 6.3 mm (10 pk). Order #114-1207834-4699415, placed February 8, 2026 | [B07TKT9KNL](https://www.amazon.com/dp/B07TKT9KNL) | 1 pk | $13.63 | ACQUIRED |
| Heyous black rubber duckbill check valve (10 pk). Order #114-1468362-6128231, placed February 8, 2026 | [B0FNR51NXN](https://www.amazon.com/dp/B0FNR51NXN) | 1 pk | $8.57 | ACQUIRED |
| Sloan-style duckbill valve, 8 pc. Order #114-1468362-6128231, placed February 8, 2026 | [B0G4MKMG54](https://www.amazon.com/dp/B0G4MKMG54) | 1 pk | $10.71 | ACQUIRED |
| 006 silicone O-ring red 70A, 1/8" ID (100 pk). Order #114-5604599-8333023, placed March 16, 2026 | [B0GFTVQPW3](https://www.amazon.com/dp/B0GFTVQPW3) | 1 pk | $10.57 | ACQUIRED |
| 007 silicone O-ring red 70A, 5/32" ID (20 pk). Order #114-5604599-8333023, placed March 16, 2026 | [B09M86ZCCB](https://www.amazon.com/dp/B09M86ZCCB) | 1 pk | $10.70 | ACQUIRED |
| TAILONZ push-to-connect 1/4" tube × 1/8" NPT (10 pk). Order #114-5604599-8333023, placed March 16, 2026 | [B07P8784D2](https://www.amazon.com/dp/B07P8784D2) | 1 pk | $10.71 | ACQUIRED |
| MALIDA 1/8" NPT × 1/4" tube elbow/straight push-fit. Order #114-5604599-8333023, placed March 16, 2026 | [B09MY72KQ7](https://www.amazon.com/dp/B09MY72KQ7) | 1 pk | $8.57 | ACQUIRED |
| John Guest PP2308E two-way divider, black polypropylene 1/4" | [freshwatersystems.com](https://www.freshwatersystems.com/products/john-guest-two-way-divider-black-polypropylene-1-4) | 2 bags (20 dividers) | $88.43 | ACQUIRED (delivered May 14) |
| John Guest PP0208E union tee, black polypropylene 1/4" (manifold Tees, Y-C/D/E/F/G/H/KA/KB) | [freshwatersystems.com](https://www.freshwatersystems.com/products/john-guest-union-tee-black-polypropylene-1-4) | 2 bags (20 tees) | $59.99 | ACQUIRED (delivered Jun 10, order WEBFWS100681220) |
| John Guest PP0308E union elbow, black polypropylene 1/4" (valve-manifold valve-outlet elbows + Kamoer pump-outlet elbows; see bom.md §4) | [freshwatersystems.com](https://www.freshwatersystems.com/products/john-guest-union-elbow-black-polypropylene-1-4) | 3 bags (30 elbows) | $68.49 | ON-ORDER (placed Jun 20, order WEBFWS100684731) |
| John Guest Speedfit PP1208E 1/4" OD black polypropylene push-to-connect bulkhead union, 10-pack. Order #112-6407862-0653853, placed May 11, 2026 | [B00JYFU8MM](https://www.amazon.com/dp/B00JYFU8MM) | 1 pk (10) | $24.79 | ACQUIRED (delivered May 12) |
| PureSec 1/4" RO push-to-connect 90° elbow bulkhead, white polypropylene, 5-pack. Order #112-0924482-7189013, placed May 28, 2026 | [B0968K4JRN](https://www.amazon.com/dp/B0968K4JRN) | 1 pk (5) | $11.79 | ACQUIRED (delivered May 29) |
| uxcell silicone flat washer, ⌀16 ID × ⌀24 OD × 3 mm, clear, 10-pack — reservoir bulkhead wet-side face seal. Order #112-8819640-4433810, placed Jun 7, 2026 | [B07D23JJMR](https://www.amazon.com/dp/B07D23JJMR) | 1 pk (10) | $7.50 | ACQUIRED (delivered Jun 8) |
| Craft Resin "Arts & Crafts" crystal-clear epoxy, 34 oz kit. Order #112-8801016-4362651, placed May 28, 2026 | [B07YCVVYFK](https://www.amazon.com/dp/B07YCVVYFK) | 1 kit (34 oz) | $26.80 | ACQUIRED (delivered May 29) |
| Pinnacle Mercantile F-style HDPE bottle set. Order #114-5825243-4744249, placed February 12, 2026 | [B0CFP9RRSF](https://www.amazon.com/dp/B0CFP9RRSF) | 1 | $18.22 | ACQUIRED |
| SodaStream Diet Mountain Dew concentrate. Order #114-7739695-9309821, placed February 1, 2026 | [B0CS191QMW](https://www.amazon.com/dp/B0CS191QMW) | 1 | $17.62 | ACQUIRED |
| SodaStream Diet Mountain Dew 4-pack. Orders #114-0084687-6710639 (Apr 26), #114-0749284-0433838 (Feb 24), #114-7016001-0433834 (Jun 10), #114-3163590-0127432 (Mar 8), #114-1990143-8424226 (May 16) | [B0G26HQWBY](https://www.amazon.com/dp/B0G26HQWBY) | 1 | $28.99 | ACQUIRED |
| SodaStream Pepsi Wild Cherry Zero 4-pack. Orders #114-0069643-1757059 (Feb 25), #114-3163590-0127432 (Mar 8) | [B0G4NRDQB8](https://www.amazon.com/dp/B0G4NRDQB8) | 1 | $28.99 | ACQUIRED |
| SodaStream Diet Cola 4-pack. Order #112-0933043-5526613, placed February 23, 2026 | [B01GQ2ZMKI](https://www.amazon.com/dp/B01GQ2ZMKI) | 1 | $18.89 | ACQUIRED |
| SodaStream Diet Pepsi Drink Mix 4-pack (cola syrup, 4 × 14.9 fl oz). Order #114-4609926-1663418, placed June 22, 2026 | [B0G25QRMBP](https://www.amazon.com/dp/B0G25QRMBP) | 1 | $28.80 | ACQUIRED (delivered Jun 22) |
| Magnetic pogo pin connector, 2-pin (2 pair). Order #112-1533167-6762648, placed April 17, 2026 | [B0CSX6ZQ1H](https://www.amazon.com/dp/B0CSX6ZQ1H) | 1 pk | $10.71 | ACQUIRED |

## 6. Refrigeration

Ice-maker donor units and copper coil for the chill loop.

| Part | Link | Qty | $ | Status |
|---|---|---|---|---|
| Frigidaire EFIC117-SS ice maker, 26 lb/day (donor). Order #112-0852106-5758666, placed April 15, 2026 | [B07PCZKG94](https://www.amazon.com/dp/B07PCZKG94) | 1 | $78.70 | ACQUIRED |
| Countertop ice maker 26 lb/day (2nd donor). Order #112-1812715-8813859, placed April 15, 2026 | [B0F42MT8JX](https://www.amazon.com/dp/B0F42MT8JX) | 1 | $63.80 | ACQUIRED |
| GOORY 1/4" OD × 50 ft ACR copper coil. Order #112-4686467-7049865, placed April 15, 2026 | [B0DKSW5VL9](https://www.amazon.com/dp/B0DKSW5VL9) | 1 | $68.63 | ACQUIRED |
| RIGID DV1910E Copper Coil Chiller, 12 V (alt path) | [rigidhvac.com](https://www.rigidhvac.com/) (direct order) | 1 | $580.00 | ACQUIRED |
| Fiberglass Supply Depot 2 lb-density 2-part expanding pour foam, closed-cell PU (quart kit). Order #112-5359790-0932202, placed May 15, 2026 | [B08R7TX8QJ](https://www.amazon.com/dp/B08R7TX8QJ) | 1 kit | $42.89 | ACQUIRED (delivered May 16) |
| HiLetgo DS18B20 waterproof 1-wire temperature probe, 1 m SS sheath (5 pk). Order #112-8868344-2270629, placed April 21, 2026 | [B00M1PM55K](https://www.amazon.com/dp/B00M1PM55K) | 1 pk | $11.79 | ACQUIRED (superseded in the design by the bare-TO-92 probes below — SS-sheath form kept as bench spares) |
| TIEXYE DS18B20 TO-92 1-wire temperature sensor (10-pk) — **tank-wall probe** stock, family 0x28. Order #112-1487355-1949808, placed July 11, 2026 (sold by ZXXP; $8.59 item + $0.62 tax, free Prime ship) | [B0FKG3HT9Q](https://www.amazon.com/dp/B0FKG3HT9Q) | 1 pk (10) | $9.21 | ON-ORDER (arriving Tue Jul 14) |
| DigiKey DS18S20+ TO-92 1-wire temperature sensor (×10) — **evaporator-coil / freeze-protect probe** stock, family 0x10 (distinct from the DS18B20 tank probe so firmware disambiguates by family code). DigiKey Salesorder #100335720 / Web Order #373967986, placed July 11, 2026; DS18S20+-ND @ $7.239 × 10 = $72.39 + $5.79 tariff + $8.49 FedEx Ground + $6.28 tax, Apple Pay | [DS18S20+-ND](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/DS18S20/1017697) | 10 | $92.95 | ON-ORDER (processing) |
| Supco D111 replacement filter-drier, 1/4" × 1/4" sweat, XH-9. Order #112-0442030-7315464, placed April 22, 2026 | [B00DM8KGXS](https://www.amazon.com/dp/B00DM8KGXS) | 1 | $11.95 | ACQUIRED |
| Supco SUD8358 UV-dye filter-drier, 1/4" × 1/4". Order #112-8685000-6226628, placed April 22, 2026 | [B009AX2O5W](https://www.amazon.com/dp/B009AX2O5W) | 1 | $13.40 | ACQUIRED |
| Mastercool 70025 cap-tube cutter. Order #112-5034335-5564260, placed April 22, 2026 | [B00NY1YHHE](https://www.amazon.com/dp/B00NY1YHHE) | 1 | $15.74 | ACQUIRED |
| Orion Motor Tech HVAC A/C manifold gauge set, 1/4" SAE. Order #112-9742741-7165035, placed April 21, 2026 | [B07CZB2SHZ](https://www.amazon.com/dp/B07CZB2SHZ) | 1 | $48.24 | ACQUIRED |
| Orion Motor Tech 4 CFM 1/3 HP single-stage vacuum pump, 110 V, 150 µ ultimate. Order #112-1730165-6930661, placed April 21, 2026 | [B08P1WRZ1S](https://www.amazon.com/dp/B08P1WRZ1S) | 1 | $78.28 | ACQUIRED |
| Supco BPV31 bullet-piercing valve. Order #112-0145136-7037809, placed April 21, 2026 | [B00DM8J3MI](https://www.amazon.com/dp/B00DM8J3MI) | 1 | $7.37 | ACQUIRED |
| Smart Weigh Pro digital pocket scale, 2000 g × 0.1 g. Order #112-7342242-5019446, placed April 21, 2026 | [B00IZ1YHZK](https://www.amazon.com/dp/B00IZ1YHZK) | 1 | $19.25 | ACQUIRED |
| Toptes PT520A refrigerant/hydrocarbon gas leak detector (description fix: ledger previously branded "Elitech", Amazon listing brand is Toptes). Order #112-9126137-7021848, placed April 21, 2026 | [B0BTM3G8DK](https://www.amazon.com/dp/B0BTM3G8DK) | 1 | $42.89 | ACQUIRED |
| Enviro-Safe R-600a 3-pack (3× 6 oz self-sealing cans) + brass charging gauge. Order #112-0223047-4718623, placed April 22, 2026 | [B0CGG1WH1N](https://www.amazon.com/dp/B0CGG1WH1N) | 1 | $72.92 | ACQUIRED |
| Klein Tools 51006 3-in-1 tube bender, 1/4 / 5/16 / 3/8" OD. Order #114-8354589-7380236, placed April 19, 2026 | [B0DPQX17WM](https://www.amazon.com/dp/B0DPQX17WM) | 1 | $23.57 | ACQUIRED |
| Wisscool 1/4" handheld tube straightener. Order #114-8354589-7380236, placed April 19, 2026 | [B0F6BPTW3T](https://www.amazon.com/dp/B0F6BPTW3T) | 1 | $26.80 | ACQUIRED |
| ESCO Institute EPA Section 608 Preparatory Manual. Order #114-6029405-6913037, placed April 21, 2026 | [1930044607](https://www.amazon.com/dp/1930044607) | 1 | $22.47 | ACQUIRED |
| Bernzomatic TS8000 high-intensity torch head + MAP-Pro 3-can kit. Order #112-4778025-6157043, placed April 22, 2026 | [B0BPMVTJ1R](https://www.amazon.com/dp/B0BPMVTJ1R) | 1 | $117.96 | ACQUIRED |
| Harris SSWF7 Stay Silv white brazing flux, 6.5 oz. Order #112-4658706-3333801, placed April 22, 2026 | [B002BYLU52](https://www.amazon.com/dp/B002BYLU52) | 1 | $12.78 | ACQUIRED (not used in build — every refrigerant-loop joint is copper-to-copper; BCuP-5 self-fluxes on copper, so joints are brazed dry) |
| Uniweld RHP400 CGA-580 regulator, 1/4" male flare, 0–400 psi delivery. Order #112-1965509-6778648, placed April 22, 2026 | [B008HQ6GXO](https://www.amazon.com/dp/B008HQ6GXO) | 1 | $96.76 | ACQUIRED |
| RIDGID 31622 Model 150 constant-swing tubing cutter, 1/8"–1-1/8". Order #112-4658706-3333801, placed April 22, 2026 | [B0009W6T8G](https://www.amazon.com/dp/B0009W6T8G) | 1 | $34.31 | ACQUIRED |
| RIDGID 23332 Model 345 flaring tool, 45° SAE. Order #112-4658706-3333801, placed April 22, 2026 | [B000X4K9KO](https://www.amazon.com/dp/B000X4K9KO) | 1 | $107.24 | ACQUIRED |
| BCuP-5 15% silver brazing alloy, 1/16" × 1 troy oz rod. Order #112-4658706-3333801, placed April 22, 2026 | [B0DQ3ZMHK7](https://www.amazon.com/dp/B0DQ3ZMHK7) | 1 | $20.37 | ACQUIRED |
| 3M Scotch-Brite Maroon General Purpose Hand Pads, 6" × 9", 1-pack of 20 pads (3M 07447 equivalent). Order #112-6573046-7656255, placed April 27, 2026 | [B07CGPCTHT](https://www.amazon.com/dp/B07CGPCTHT) | 1 pk | $28.85 | ACQUIRED |
| HVAC 1/4" OD copper slip coupling, ACR-grade, sweat × sweat, 10-pack. Order #112-0837919-8970627, placed April 23, 2026 | [B0FH549N6D](https://www.amazon.com/dp/B0FH549N6D) | 1 pk | $8.56 | ACQUIRED |
| Knipex 86 01 180 Pliers Wrench, 7.25". Order #112-1057208-2782602, placed April 23, 2026 | [B07YLFLSJW](https://www.amazon.com/dp/B07YLFLSJW) | 1 | $57.06 | ACQUIRED |
| Joywayus brass 1/4" SAE 45° flare nut, 7/16"-20 thread, 5-pack. Order #112-5788053-3609032, placed April 23, 2026 | [B0G1XJ2F68](https://www.amazon.com/dp/B0G1XJ2F68) | 1 pk | $8.57 | ACQUIRED |
| 3M 425 aluminum foil tape, 2" × 180 ft, thermally conductive. Order #112-3799575-6647414, placed April 23, 2026 | [B07BTW7C2N](https://www.amazon.com/dp/B07BTW7C2N) | 1 | $95.42 | ACQUIRED |
| Pouring Masters 5 oz / 150 mL graduated plastic mixing cups (50 pk). Order #112-0326855-5540223, placed April 27, 2026 | [B08JHH1DBF](https://www.amazon.com/dp/B08JHH1DBF) | 1 pk | $20.37 | ACQUIRED |
| JMU 6" wood tongue depressors, individually wrapped (100 pk). Order #112-8110646-3335448, placed April 27, 2026 | [B09H6ZP447](https://www.amazon.com/dp/B09H6ZP447) | 1 pk | $7.50 | ACQUIRED |
| SUP powder-free 4 mil nitrile exam gloves, X-Large, 100 ct (= 50 pairs). Order #112-8247392-7531444, placed April 27, 2026 | [B0G8SSMVKW](https://www.amazon.com/dp/B0G8SSMVKW) | 1 pk | $7.49 | ACQUIRED |
| BOJACK SF76E SEFUSE thermal fuse, 77 °C, 10 A / 250 V (10-pack). Order #112-0089456-0822653, placed May 11, 2026 | [B07Y61YTTK](https://www.amazon.com/dp/B07Y61YTTK) | 1 pk (10) | $6.42 | ACQUIRED (delivered May 13) |
| ACEIRMC MQ-6 LPG / iso-butane combustible gas sensor module (5-pack). Order #112-0089456-0822653, placed May 11, 2026 | [B0978JSCZ8](https://www.amazon.com/dp/B0978JSCZ8) | 1 pk (5) | $11.79 | ACQUIRED (delivered May 13) |
| Heyco SB-500-6 (Heyco part #2053) black 6/6 nylon strain-relief snap bushing, 100-pack. Order #112-7723568-0091455, placed May 15, 2026 | [B01LPBST9G](https://www.amazon.com/HEYCO-2053-SB-500-6-Accessories/dp/B01LPBST9G/) | 1 pk (100) | $12.60 | ACQUIRED (delivered May 16) |

## 7. Dispensing end — faucet, flow sensor

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Westbrass A2031-NL-62 8" Touch-Flo cold-water faucet, matte black. Order #114-5534543-4435455, placed February 24, 2026 | [B0BXFW1J38](https://www.amazon.com/dp/B0BXFW1J38) | 1 | $32.18 | ACQUIRED |
| Westbrass D203-NL-62 6" Touch-Flo cold-water faucet, matte black. Order #114-7711911-5865013, placed February 11, 2026 | [B01MZ6JPXW](https://www.amazon.com/dp/B01MZ6JPXW) | 1 | $56.83 | ACQUIRED |
| Westbrass R2031-NL-12 8" Touch-Flo faucet, oil-rubbed bronze. Order #112-5236199-6056258, placed April 23, 2026 | [B01N5LVNQA](https://www.amazon.com/dp/B01N5LVNQA) | 1 | $20.95 | ACQUIRED |
| 1/4" OD × 12" 304 SS straight tube, 4 pc. Order #112-5229510-7593833, placed April 23, 2026 | [B0F87DJDZW](https://www.amazon.com/dp/B0F87DJDZW) | 1 pk | $12.86 | ACQUIRED |
| 1/8" OD × 12" 304 SS straight tube, 4 pc. Order #112-0196430-3061828, placed April 23, 2026 | [B0F87V8XCB](https://www.amazon.com/dp/B0F87V8XCB) | 1 pk | $8.57 | ACQUIRED |
| Beduan 304 SS compression ferrule sleeve, 1/4" OD, 5 pk. Order #112-7179212-4944250, placed April 23, 2026 | [B07V4K2KKH](https://www.amazon.com/dp/B07V4K2KKH) | 1 pk | $6.42 | ACQUIRED |
| Beduan 304 SS compression ferrule sleeve, 1/8" OD. Order #112-4247013-3054647, placed April 23, 2026 | [B07V8RJJYJ](https://www.amazon.com/dp/B07V8RJJYJ) | 1 pk | $5.35 | ACQUIRED |
| Pysrych 304 SS reducing compression union, 1/4" OD × 1/8" OD, 2 pk. Order #112-5173995-8426610, placed April 23, 2026 | [B0BM4394Z4](https://www.amazon.com/dp/B0BM4394Z4) | 1 pk | $9.64 | ACQUIRED |
| Siptenk 1/4" OD brass tube stiffener insert, 100 pk. Order #112-8579175-6021014, placed April 24, 2026 | [B0FM77LLM1](https://www.amazon.com/dp/B0FM77LLM1) | 1 pk | $9.64 | ACQUIRED |
| DIGITEN G1/4" Hall-effect flow sensor 0.3–10 L/min. Orders #114-4838401-4353060 (Feb 12, ×2), #112-9633392-2520236 (Feb 23, ×2) | [B07QRXLRTH](https://www.amazon.com/dp/B07QRXLRTH) | 4 | $10.18 ea | ACQUIRED |
| DIGITEN G1/4" Hall-effect flow meter 0.3–6 L/min. Order #114-0818390-2733826, placed February 2, 2026 | [B07QS17S6Q](https://www.amazon.com/dp/B07QS17S6Q) | 1 | $10.18 | ACQUIRED |
| Eoiips polyethylene tubing 1/16" ID × 1/8" OD, 3.28 ft (1 m). Order #114-9634716-3126657, placed April 29, 2026 | [B0BWJ3S5NM](https://www.amazon.com/dp/B0BWJ3S5NM) | 1 | $8.03 | ACQUIRED |
| CARGEN Pipe Insulation Foam Tube. Order #112-3935659-9563410, placed May 15, 2026 | [B0D2XFK337](https://www.amazon.com/dp/B0D2XFK337) | 2 | $16.28 | ACQUIRED (delivered May 16) |

## 8. Electronics — controllers

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| ESP32-DevKitC-32E. Orders #114-0818390-2733826 (Feb 2, ×1), #112-0933043-5526613 (Feb 23, ×2) | [B09MQJWQN2](https://www.amazon.com/dp/B09MQJWQN2) | 3 | $11.80 ea | ACQUIRED |
| ESP32-DevKitC-32E (repeat ASIN). Order #112-2471492-3870616, placed Jun 7, 2026 | [B09MQJWQN2](https://www.amazon.com/dp/B09MQJWQN2) | 2 | $23.60 | ACQUIRED (delivered Jun 8) |
| Waveshare RP2040 0.99" round touch LCD, CNC case — prototype external flavor display; dropped from the product, superseded by the faucet-mounted Waveshare ESP32-S3 1.47" touch LCD (B0FCF1MGT3 below). Retained as prototype stock.. Orders #114-9973455-6637052 (Mar 8), #114-7373747-7178604 (Mar 9) | [B0CTSPYND2](https://www.amazon.com/dp/B0CTSPYND2) | 2 | ~$25.73 ea | ACQUIRED |
| Meshnology ESP32-S3 round rotary display 1.28" — prototype enclosure-front config display. Order #114-7373747-7178604, placed March 9, 2026 | [B0G5Q4LXVJ](https://www.amazon.com/dp/B0G5Q4LXVJ) | 1 | bundle | ACQUIRED |
| Waveshare ESP32-S3-Touch-LCD-4.3B — 4.3" 800×480 IPS RGB capacitive-touch dev board (ST7262 RGB + GT911 touch, CH422G I/O expander), ESP32-S3-WROOM-1-N16R8; enclosure-front config + interaction display, 7–36 V screw-terminal input off the 12 V bus. Order #112-5620567-3321809, placed Jun 13, 2026 | [B0D925SBYF](https://www.amazon.com/dp/B0D925SBYF) | 1 | $46.11 | ACQUIRED (delivered Jun 15) |
| Waveshare ESP32-S3 1.47" capacitive-touch IPS LCD dev board, 172×320 (JD9853 driver + AXS5106L touch) — faucet-mounted flavor display + touch toggle. Order #112-7687617-6094631, placed Jun 7, 2026 | [B0FCF1MGT3](https://www.amazon.com/dp/B0FCF1MGT3) | 2 | $51.46 | ACQUIRED (delivered Jun 9) |
| JLCPCB order W2026062715518432 — controller carrier PCB (`mini.tsx`), 4-layer, 128 × 99 mm through-hole carrier; gerber set `mini.gerbers_Y2` (sub-order Y2-12927587A). $122.17 as-paid = $48.07 merch + $50.15 shipping + $16.82 customs duties/taxes + $7.13 sales tax. Placed Jun 27, 2026 | [jlcpcb.com](https://jlcpcb.com/) | 10 | $122.17 | ON-ORDER (in production, 3–4 day build) |

## 9. Electronics — I/O, drivers, sensors, power, DIN rail, connectors

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Waveshare MCP23017 I2C I/O expansion board. Order #112-7245467-6557007, placed April 26, 2026 | [B07P2H1NZG](https://www.amazon.com/dp/B07P2H1NZG) | 1 | $13.93 | ACQUIRED |
| BOJACK ULN2803 Darlington driver IC (10 pk). Order #112-2110462-6265038, placed April 15, 2026 | [B08CX79JSQ](https://www.amazon.com/dp/B08CX79JSQ) | 1 pk | $7.50 | ACQUIRED |
| ULN2803A high-current driver module (2 pc). Order #112-7245467-6557007, placed April 26, 2026 | [B0F872W528](https://www.amazon.com/dp/B0F872W528) | 1 pk | $7.07 | ACQUIRED |
| BOJACK L298N dual H-bridge motor driver (4-pack). Order #114-1015191-6799441, placed February 18, 2026 | [B0C5JCF5RS](https://www.amazon.com/dp/B0C5JCF5RS) | 1 pk | $10.71 | ACQUIRED |
| DS3231 AT24C32 RTC module (2 pk). Order #114-2813251-8225805, placed March 16, 2026 | [B09LLMYBM1](https://www.amazon.com/dp/B09LLMYBM1) | 1 pk | $7.07 | ACQUIRED |
| HiLetgo DS3231 high-precision RTC (5 pk). Order #114-5764473-1322614, placed March 16, 2026 | [B01N1LZSK3](https://www.amazon.com/dp/B01N1LZSK3) | 1 pk | $16.08 | ACQUIRED |
| EDGELEC 4.7 kΩ 1/4 W 1% metal-film resistor (100 pk). Order #112-0915506-0821038, placed April 26, 2026 | [B07HDFHPP3](https://www.amazon.com/dp/B07HDFHPP3) | 1 pk | $5.89 | ACQUIRED |
| Chanzon 2.2 kΩ 1/4 W 1% metal-film resistor (100 pk) — MQ-6 gas-sensor output divider top leg (carrier R1/R3), 2 per unit. Order #112-6701248-5105066, placed June 25, 2026 | [B08QRPRVMJ](https://www.amazon.com/dp/B08QRPRVMJ) | 1 pk (100) | $5.49 | ON-ORDER (arriving Jun 27) |
| Chanzon 3.3 kΩ 1/4 W 1% metal-film resistor (100 pk) — MQ-6 gas-sensor output divider bottom leg (carrier R2/R4), 2 per unit. Order #112-6701248-5105066, placed June 25, 2026 | [B08QRG7JBY](https://www.amazon.com/dp/B08QRG7JBY) | 1 pk (100) | $5.49 | ON-ORDER (arriving Jun 27) |
| Rubycon 470 µF 25 V low-ESR (0.08 Ω) radial aluminum electrolytic capacitor, 10×12.5 mm (15 pk). Order #112-0915506-0821038, placed April 26, 2026 | [B0F8BZVBKF](https://www.amazon.com/dp/B0F8BZVBKF) | 1 pk | $7.40 | ACQUIRED |
| HiLetgo NJK-5002C Hall-effect proximity switch (2 pk). Order #112-2147768-5852208, placed March 15, 2026 | [B01MZYYCLH](https://www.amazon.com/dp/B01MZYYCLH) | 1 pk | $9.11 | ACQUIRED |
| Gebildet reed switches, 14 mm glass body, NO (6 pk). Order #112-4347613-6452231, placed April 24, 2026 | [B0CW9418F6](https://www.amazon.com/dp/B0CW9418F6) | 1 pk | $6.42 | ACQUIRED |
| DEVMO MINI vertical float switch. Order #112-4706100-6171430, placed April 24, 2026 | [B07T18PGJ4](https://www.amazon.com/dp/B07T18PGJ4) | 1 | $13.93 | ACQUIRED |
| AplysiaTech N52 neodymium ring magnet, 1" OD × 1/2" ID × 1/8" thick (25.4 × 12.7 × 3.18 mm, 10 pk) — donor magnet for a purpose-printed reservoir float (print-pause embed), alternative to harvesting the DEVMO donut. Order #112-8759475-1611456, placed Jun 14, 2026 | [B0GD15CWCL](https://www.amazon.com/dp/B0GD15CWCL) | 1 pk (10) | $30.02 | ACQUIRED (delivered Jun 15) |
| Stainless-steel float switch, double-ball, 200 mm tube — teardown/donor for the commodity ⌀28 × 28 mm crimped SS float that recurs across nearly all SS float-switch listings. Order #112-7010270-8849812, placed Jun 14, 2026 | [B09JSYMM5G](https://www.amazon.com/dp/B09JSYMM5G) | 1 | $15.22 | ACQUIRED (delivered Jun 16) |
| MECCANIXITY stainless-steel float switch, 45 mm rod, M10 thread (2 pc) — same commodity ⌀28 × 28 mm SS float, teardown/donor. Order #112-7886483-1554622, placed Jun 14, 2026 | [B0FL763VPL](https://www.amazon.com/dp/B0FL763VPL) | 1 pk (2) | $14.79 | ACQUIRED (delivered Jun 16) |
| EC Buying XKC-Y25-V non-contact capacitive liquid-level sensor. Order #112-5459082-8422662, placed May 8, 2026 | [B0C73F96MF](https://www.amazon.com/dp/B0C73F96MF) | 1 | $10.29 | ACQUIRED (delivered May 9) |
| Shutao 6-pc water-sensor module, LM393 comparator, 3.3–5 V — backflow drip-pan wet telltale: conductivity plate sits in the internal drip pan, VCC at 3.3 V keeps DO ESP-safe (active-low when wet) → ESP32 GPIO 13. Order #112-2621523-2281840, placed June 25, 2026 | [B0B2W76MB1](https://www.amazon.com/dp/B0B2W76MB1) | 1 pk (6) | $7.50 | ON-ORDER (arriving Jun 26) |
| HiLetgo MPR121 12-channel I2C capacitive touch breakout (2 pk). Order #112-5503072-4357859, placed May 8, 2026 | [B06XXYZPPX](https://www.amazon.com/dp/B06XXYZPPX) | 1 pk | $6.85 | ACQUIRED (delivered May 10) |
| Kraftex copper foil tape, 1/4" × 66 ft, conductive adhesive. Order #112-5656837-1597066, placed May 8, 2026 | [B0G1TN3JWB](https://www.amazon.com/dp/B0G1TN3JWB) | 1 | $7.50 | ACQUIRED (delivered May 9) |
| ~~Tynulox 1/8" × 6" 304 SS round rod (10 pk)~~. Order #112-8251187-7721036, placed April 24, 2026 | [B0BKGS32KJ](https://www.amazon.com/dp/B0BKGS32KJ) | 1 pk | $8.56 | ACQUIRED (superseded) |
| Tandefio 1/8" × 12" 316 SS round rod (5 pk). Order #112-7391312-2980226, placed April 24, 2026 | [B0CY4DWJFQ](https://www.amazon.com/dp/B0CY4DWJFQ) | 1 pk | $8.57 | ACQUIRED |
| 1/8" (3 mm) × 7.8" (200 mm) 316 SS round rod (10 pk) — level-sensing rod stock. Order #114-7801151-2777012, placed June 17, 2026 | [B0FYC63JCY](https://www.amazon.com/dp/B0FYC63JCY) | 2 pk (20) | $18.22 | ACQUIRED (delivered Jun 21) |
| MECCANIXITY 1/8" (3 mm) × 9.84" (250 mm) 316 SS round rod (10 pk) — level-sensing rod stock. Order #114-2674264-1703446, placed June 17, 2026 | [B0FWZMZBY7](https://www.amazon.com/dp/B0FWZMZBY7) | 2 pk (20) | $17.78 | ACQUIRED (delivered Jun 20) |
| 12 V 2 A DC power supply, 9-tip. Orders #114-1015191-6799441 (Feb 18), #114-9620011-1329056 (Feb 25) | [B0DZGTTBGZ](https://www.amazon.com/dp/B0DZGTTBGZ) | 1 | bundle | ACQUIRED |
| 5 V 3 A AC/DC adapter, 11-tip. Order #114-0818390-2733826, placed February 2, 2026 | [B09NLMVXMZ](https://www.amazon.com/dp/B09NLMVXMZ) | 1 | $9.00 | ACQUIRED |
| Molence C45 PCB DIN-rail adapter clips (10 sets). Order #114-2582317-0018622, placed February 26, 2026 | [B09KZHY8G4](https://www.amazon.com/dp/B09KZHY8G4) | 1 pk | $10.71 | ACQUIRED |
| VAMRONE 35 mm DIN rail, 4" (6 pk). Order #114-2582317-0018622, placed February 26, 2026 | [B0CDPVRY2W](https://www.amazon.com/dp/B0CDPVRY2W) | 1 pk | $7.50 | ACQUIRED |
| ESP32 super breakout DIN-rail mount GPIO expansion. Order #114-2582317-0018622, placed February 26, 2026 | [B0BW4SJ5X2](https://www.amazon.com/dp/B0BW4SJ5X2) | 1 | $27.87 | ACQUIRED |
| naughtystarts ESP32 screw-terminal GPIO breakout board, 3.5 mm terminals, for ESP-WROOM-32 / ESP32-DevKitC module (2 pc). Order #112-0981761-4377858, placed Jun 7, 2026 | [B0BYS6THLF](https://www.amazon.com/dp/B0BYS6THLF) | 1 pk (2) | $12.86 | ACQUIRED (delivered Jun 9) |
| ALMOCN TTL-to-RS485 auto-direction module, 3.0–30 V, screw-terminal RS485 + JST TTL (5 pk) — RS485 transceiver on the base ESP32 for the 4.3B config-display link. Order #112-8498962-9414661, placed Jun 13, 2026 | [B09998FY4X](https://www.amazon.com/dp/B09998FY4X) | 1 pk (5) | $13.49 | ACQUIRED (delivered Jun 16) |
| Baomain 0.11" male quick-disconnect spade (100 pk). Order #114-7897645-5210617, placed February 25, 2026 | [B01MZZGAJP](https://www.amazon.com/dp/B01MZZGAJP) | 1 pk | $6.42 | ACQUIRED |
| Haisstronica ratchet crimper, AWG 22–10. Order #114-9620011-1329056, placed February 25, 2026 | [B08F3JKDD3](https://www.amazon.com/dp/B08F3JKDD3) | 1 | bundle | ACQUIRED |
| Feggizuli 280 pc spade connector kit. Order #114-0182432-7123463, placed February 24, 2026 | [B0B4H54KPS](https://www.amazon.com/dp/B0B4H54KPS) | 1 pk | $8.25 | ACQUIRED |
| 60 pc female spade crimp kit. Order #114-5322942-5213821, placed February 24, 2026 | [B0B9MZJ2ML](https://www.amazon.com/dp/B0B9MZJ2ML) | 1 pk | $10.71 | ACQUIRED |
| Twidec 20 pc 4.8/6.3 mm spade crimp. Order #114-0884594-8630623, placed February 24, 2026 | [B08F784R9W](https://www.amazon.com/dp/B08F784R9W) | 1 pk | $9.64 | ACQUIRED |
| Baomain 1/4" / 6.3 mm female insulated quick-disconnect spade terminals, 22–16 AWG, red (100-pack). Order #112-3443368-0402610, placed June 22, 2026 | [B01G408A4M](https://www.amazon.com/dp/B01G408A4M) | 1 pk (100) | $7.50 | ON-ORDER (arriving Jun 24) |
| Baomain 0.187" / 4.8 mm (3/16") female fully-insulated quick-disconnect spade terminals, 22–16 AWG, red (100-pack). Order #112-3515616-8230610, placed June 22, 2026 | [B01N5APVEE](https://www.amazon.com/dp/B01N5APVEE) | 1 pk (100) | $7.28 | ON-ORDER (arriving Jun 24) |
| smseace #4 (M3) ring terminals, insulated, 22–16 AWG, 150 pc. Order #112-4073443-1219450, placed June 22, 2026 | [B08B5VS8ZR](https://www.amazon.com/dp/B08B5VS8ZR) | 1 pk (150) | $9.64 | ON-ORDER (arriving Jun 25) |
| WAGO 221-415 Lever-Nuts 5-conductor compact splicing connector (25 pk) — 5-way lever nut for the controller-PCB ≤5-conductor connector fan-outs (J6 reed-A GND, J4 sensor GND, J5 driver GND). Not the AC distribution block — that stays on 221-413 per the power tray. Order #112-7409860-0021807, placed June 27, 2026 | [B0107SYYGU](https://www.amazon.com/dp/B0107SYYGU) | 1 pk (25) | $26.76 | ON-ORDER (arriving Jun 30) |
| WAGO 221-420 Lever-Nuts 10-conductor splicing connector (box of 15) — 10-way lever nut for the >5-conductor PCB fan-outs: J1 MANIFOLD-A COM (8 valves), J2 MANIFOLD-B COM (4 valves + fan), J7 REEDS-B GND (6 reeds). Order #112-1321519-4687432, placed June 27, 2026 | [B0H1MW1LCX](https://www.amazon.com/dp/B0H1MW1LCX) | 1 pk (15) | $28.90 | ON-ORDER (arriving Jun 30) |
| WAGO 221-413 Lever-Nuts 3-conductor splicing connector (box of 50) — 3-way lever nut for the power-tray AC mains distribution (H / N / G, one per pole); the Kitchen + Lite power trays are both cut for this part. Order #112-4898292-1807408, placed June 27, 2026 | [B07W7W91FX](https://www.amazon.com/dp/B07W7W91FX) | 1 pk (50) | $27.83 | ON-ORDER (arriving Jun 29) |
| Dupont jumper wires (M/F, M/M, F/F) 20 cm. Order #114-5649971-6455418, placed February 24, 2026 | [B0BRTJXND9](https://www.amazon.com/dp/B0BRTJXND9) | 1 pk | $6.40 | ACQUIRED |
| ELEGOO 120 pc Dupont jumper wire ribbon. Orders #114-0818390-2733826 (Feb 2, ×1), #114-0077226-6463477 (Feb 24, ×1) | [B01EV70C78](https://www.amazon.com/dp/B01EV70C78) | 2 | $7.49 ea | ACQUIRED |
| Taiss Dupont crimp kit + SN-28B. Order #114-3384762-6934634, placed February 22, 2026 | [B0B11RLGDZ](https://www.amazon.com/dp/B0B11RLGDZ) | 1 | $23.58 | ACQUIRED |
| iCrimp SN-2549 ratcheting open-barrel crimper, AWG 28–18 (0.08–1.0 mm²) — dedicated die nests for JST PH 2.0 / ZH 1.5 / XH 2.5 / VH 3.96 / JWPS 4.0 + Dupont 2.54; crimps the JST-PH 2.0 terminals on the MCP23017 I²C link, which the SN-28B's nests fit only loosely. Order #112-6248060-3106636, placed Jun 14, 2026 | [B01N4L8QMW](https://www.amazon.com/dp/B01N4L8QMW) | 1 | $23.91 | ACQUIRED (delivered Jun 15) |
| Waveshare MCP23017 I2C I/O expansion board (repeat ASIN). Order #112-2110462-6265038, placed April 15, 2026 | [B07P2H1NZG](https://www.amazon.com/dp/B07P2H1NZG) | 1 | $13.75 | ACQUIRED (delivered Apr 27) |
| ULN2803A high-current driver module, 2-pc (repeat ASIN). Order #112-2110462-6265038, placed April 15, 2026 | [B0F872W528](https://www.amazon.com/dp/B0F872W528) | 1 pk | $6.97 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 4-pin connector kit (50 sets / 300 pcs). Order #112-7245467-6557007, placed April 26, 2026 | [B0B2RB524Y](https://www.amazon.com/dp/B0B2RB524Y) | 1 pk | $8.45 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 6-pin connector kit (50 sets / 400 pcs). Order #112-7245467-6557007, placed April 26, 2026 | [B0B2R8Q1JL](https://www.amazon.com/dp/B0B2R8Q1JL) | 1 pk | $9.19 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 9-pin connector kit (30 sets / 330 pcs). Order #112-7245467-6557007, placed April 26, 2026 | [B0B2R73RQB](https://www.amazon.com/dp/B0B2R73RQB) | 1 pk | $9.19 | ACQUIRED (delivered Apr 29) |
| CQRobot JST XH 2.54 mm 10-pin connector kit (30 sets / 360 pcs) — for the MCP23017 GPIO port rows (VCC + GND + 8 GPIO = 10 holes; a 10-pin fills the footprint so it can't seat off-by-one, where the 9-pin kit was sized for the ULN2803A sides). Order #112-9768778-8444265, placed Jun 7, 2026 | [B0B2R93CV3](https://www.amazon.com/dp/B0B2R93CV3) | 1 pk | $9.64 | ACQUIRED (delivered Jun 9) |
| CQRobot/Zhansheng JST XH 2.54 mm pre-crimped bonded ribbon kit (15 cm / 5.9", 12-conductor ribbons × 8 + loose housings 2/3/4/5/6/7/8/9/10/12 P). Order #112-7245467-6557007, placed April 26, 2026 | [B0F6C7X5CR](https://www.amazon.com/dp/B0F6C7X5CR) | 1 pk | $15.86 | ACQUIRED (delivered Apr 27) |
| Keszoox JST XH 2.54 mm pre-crimped wires, 50 cm × 22 AWG silicone, 20 pcs/pk in 10 colors. Order #112-7245467-6557007, placed April 26, 2026 | [B0F8HMQRRN](https://www.amazon.com/dp/B0F8HMQRRN) | 2 pk | $11.63 ea | ACQUIRED (delivered Apr 30) |
| Chanzon 3-pin 2.54 mm single-row female header (50 pcs) — carrier (`pcb/carrier/mini.tsx`) hand-assembly module socket: U8 buzzer (1/board). Order #112-7067792-6289059, placed Jun 27, 2026 | [B09MYMD4YS](https://www.amazon.com/dp/B09MYMD4YS) | 1 pk (50) | $6.99 | ON-ORDER (arriving Jun 30) |
| (Pack of 50) 4-pin 2.54 mm single-row female header — carrier module sockets U6I (DS3231 I²C tap) + U7T (RS485 TTL); 2/board. Order #112-7067792-6289059, placed Jun 27, 2026 | [B08T5S54C5](https://www.amazon.com/dp/B08T5S54C5) | 1 pk (50) | $7.99 | ON-ORDER (arriving Jun 30) |
| (Pack of 50) 6-pin 2.54 mm single-row female header — carrier module sockets U2I/U3I (MCP I²C) + U6H (DS3231); 3/board. Order #112-7067792-6289059, placed Jun 27, 2026 | [B08T5SV8BK](https://www.amazon.com/dp/B08T5SV8BK) | 1 pk (50) | $7.99 | ON-ORDER (arriving Jun 30) |
| Dahszhi 9-way 2.54 mm single-row female header (100 pcs) — carrier ULN2803 sockets U4I/U4O/U5I/U5O; 4/board. Order #112-0861785-9553820, placed Jun 27, 2026 | [B0CTKDDR26](https://www.amazon.com/dp/B0CTKDDR26) | 1 pk (100) | $8.99 | ON-ORDER (arriving Jun 29) |
| (Pack of 50, ships 20 pcs) 10-pin 2.54 mm single-row female header — carrier MCP GPA/GPB sockets U2A/U2B/U3A/U3B; 4/board (1 pack ≈ 5 boards, the limiting socket). Order #112-7067792-6289059, placed Jun 27, 2026 | [B08T63F6JV](https://www.amazon.com/dp/B08T63F6JV) | 1 pk (20) | $7.89 | ON-ORDER (arriving Jun 30) |
| 1×19 2.54 mm single-row female header for ESP32-DevKitC (20 pcs) — carrier ESP32 socket U1A/U1B; 2/board (1 pack = 10 boards). Order #112-0861785-9553820, placed Jun 27, 2026 | [B0CFDYMRK2](https://www.amazon.com/dp/B0CFDYMRK2) | 1 pk (20) | $8.99 | ON-ORDER (arriving Jun 29) |
| Yakomon 36 × 40-pin 2.54 mm single-row breakaway male header — carrier module pins, snapped to size (MCP ×2, DS3231, RS485 TTL, buzzer; ESP + ULN bring their own). Order #112-7067792-6289059, placed Jun 27, 2026 | [B0FH2RVG4L](https://www.amazon.com/dp/B0FH2RVG4L) | 1 pk (36) | $5.99 | ON-ORDER (arriving Jun 30) |
| CQRobot JST XH 2.54 mm 3-pin connector kit (50 sets / 250 pcs) — carrier field connector J9 DISPLAY (RS485 A/B/ERTH); 1/board. Order #112-7067792-6289059, placed Jun 27, 2026 | [B0B2R99X99](https://www.amazon.com/dp/B0B2R99X99) | 1 pk | $6.39 | ON-ORDER (arriving Jun 30) |
| CQRobot JST XH 2.54 mm 5-pin connector kit (50 sets / 350 pcs) — carrier field connector J6 REEDS A; 1/board. Order #112-7067792-6289059, placed Jun 27, 2026 | [B0B2R9P2TS](https://www.amazon.com/dp/B0B2R9P2TS) | 1 pk | $8.29 | ON-ORDER (arriving Jun 30) |
| CQRobot JST XH 2.54 mm 7-pin connector kit (50 sets / 450 pcs) — carrier field connector J7 REEDS B; 1/board. Order #112-7067792-6289059, placed Jun 27, 2026 | [B0B2R96VS3](https://www.amazon.com/dp/B0B2R96VS3) | 1 pk | $8.99 | ON-ORDER (arriving Jun 30) |
| ANGSTROM 2-pin 2.54 mm PCB screw terminal block, 150 V / 6 A (20 pcs) — carrier power inlets J8 (5 V) + J10 (12 V), the board's only screw terminals; 2/board (1 pack = 10 boards). Order #112-7067792-6289059, placed Jun 27, 2026 | [B0FHGXX6SK](https://www.amazon.com/dp/B0FHGXX6SK) | 1 pk (20) | $9.99 | ON-ORDER (arriving Jun 30) |
| LuoQiuFa 3-pin 5.08 mm pluggable PCB screw terminal (2EDG-5.08, 10 sets) — carrier RS485 line side U7L: header solders to U7L, screw plug wires to the ALMOCN module's stock 5.08 mm terminal; 1/board (1 pack = 10 boards). Order #112-7067792-6289059, placed Jun 27, 2026 | [B093DL8DKC](https://www.amazon.com/dp/B093DL8DKC) | 1 pk (10) | $6.99 | ON-ORDER (arriving Jun 30) |
| KWANGIL 22AWG 12-Conductor Cable, UL2464, High-Flexible Tinned Copper Unshielded, Matte Black, 25 ft. Order #114-2322598-9184256, placed May 14, 2026 | [B0CSD5QZ21](https://www.amazon.com/dp/B0CSD5QZ21) | 1 | $25.73 | ACQUIRED (delivered May 15) |
| BNTECHGO 28 AWG silicone ribbon cable, 4-conductor flat, black, 50 ft — faucet display harness (5 V / GND / TX / RX) through the faucet shell to the under-counter base. Order #112-9860351-3650618, placed Jun 10, 2026 | [B07PNPHWMG](https://www.amazon.com/dp/B07PNPHWMG) | 1 (50 ft) | $21.43 | ACQUIRED (delivered Jun 11) |
| BNTECHGO 16 AWG silicone wire kit, stranded tinned copper, 5 colors (red/black/white/blue/green) × 25 ft each. Order #112-8448573-3185817, placed Jun 22, 2026 | [B06Y557TCL](https://www.amazon.com/dp/B06Y557TCL) | 1 kit (5× 25 ft) | $38.29 | ON-ORDER (arriving Jun 23) |
| BNTECHGO 18 AWG silicone wire, stranded tinned copper, red 25 ft + black 25 ft. Order #112-8492724-3195462, placed Jun 22, 2026 | [B07HGTKQ89](https://www.amazon.com/dp/B07HGTKQ89) | 1 (2× 25 ft) | $14.99 | ON-ORDER (arriving Jun 23) |
| HS 6" zip ties, black, 18 lb tensile, nylon PA66 UV-resistant, 100-pack — harness/cable management. Order #112-7522816-0777851, placed Jun 22, 2026 | [B0DR8KSVQD](https://www.amazon.com/dp/B0DR8KSVQD) | 1 pk (100) | $6.42 | ON-ORDER (arriving Jun 24) |
| BNTECHGO 22 AWG silicone wire, 250 ft black single-color spool — bulk all-black hookup, cut-to-length at build for the valve branches + low-power DC + signal fan-outs (the cut-to-length workhorse, replaces the pre-crimped pigtails for length-specific runs). Order #112-4343274-7898624, placed June 28, 2026 | [B06Y2PNW41](https://www.amazon.com/dp/B06Y2PNW41) | 1 (250 ft) | $27.86 | ON-ORDER (arriving ~Jun 30) |
| BNTECHGO 24 AWG silicone wire, 100 ft black single-color spool — bulk all-black hookup for the reed + sensor runs (SIG-1/2/3/4/8/9). Order #112-7185180-0909846, placed June 28, 2026 | [B01K4TLR1W](https://www.amazon.com/dp/B01K4TLR1W) | 1 (100 ft) | $13.38 | ON-ORDER (arriving ~Jun 30) |
| Alex Tech 1/2" black PET expandable braided sleeve, 100 ft — primary harness bundling (replaces spiral wrap). Order #112-6043616-7501828, placed June 28, 2026 | [B074GMNW7T](https://www.amazon.com/dp/B074GMNW7T) | 1 (100 ft) | $17.15 | ON-ORDER (arriving ~Jun 30) |
| Alex Tech 3/4" black PET expandable braided sleeve, 100 ft — harness bundling, large trunks (manifold cable). Order #112-9748313-5465028, placed June 28, 2026 | [B074GMCGZX](https://www.amazon.com/dp/B074GMCGZX) | 1 (100 ft) | $22.51 | ON-ORDER (arriving ~Jun 30) |
| Alex Tech 1/4" black PET expandable braided sleeve, 25 ft — harness bundling, thin runs. Order #112-1902778-9631456, placed June 28, 2026 | [B071JH14WZ](https://www.amazon.com/dp/B071JH14WZ) | 1 (25 ft) | $8.57 | ON-ORDER (arriving ~Jun 30) |
| Preciva ferrule crimping tool kit — AWG 28–5 quad-indent ratcheting crimper + 950 pcs insulated bootlace ferrules; for the Wago 221 conductor landings + screw terminals (closes the wire-ferrule gap). Order #112-4262778-1489854, placed June 28, 2026 | [B0DS622GKN](https://www.amazon.com/dp/B0DS622GKN) | 1 kit | $48.25 | ON-ORDER (arriving ~Jun 30) |
| GEARit 25 ft 18/3 SJOOW portable cord, 18 AWG 300 V — rubber-jacketed 3-conductor lead for the compressor-shroud AC pass-through (AC-4/5/6). Order #112-9256032-0146608, placed June 28, 2026 | [B0BKQ2H9BZ](https://www.amazon.com/dp/B0BKQ2H9BZ) | 1 (25 ft) | $20.37 | ON-ORDER (arriving ~Jun 30) |
| Biaungdo 1/2" NPT stainless-steel cable gland, adjustable 6–12 mm, 2-pack — strain relief for the shroud AC pass-through. Order #112-5404430-0862635, placed June 28, 2026 | [B0F2HP5FWB](https://www.amazon.com/dp/B0F2HP5FWB) | 1 pk (2) | $7.63 | ON-ORDER (arriving ~Jun 30) |
| CR2032 3 V cell pack (RTC backup). Order #114-3384762-6934634, placed February 22, 2026 | [B0C15WJXL2](https://www.amazon.com/dp/B0C15WJXL2) | 1 | $12.00 | ACQUIRED |
| Breadboard kit, 2×830 + 2×400 pt. Order #114-0818390-2733826, placed February 2, 2026 | [B07DL13RZH](https://www.amazon.com/dp/B07DL13RZH) | 1 pk | $7.33 | ACQUIRED |
| Gratury IP67 waterproof enclosure. Order #114-6385083-8023407, placed February 2, 2026 | [B08281V2RL](https://www.amazon.com/dp/B08281V2RL) | 1 | $23.58 | ACQUIRED |
| Teyleten 3.3 V relay module, opto-isolated, 10 A @ 250 VAC (5 pk). Order #112-8930099-2982664, placed April 20, 2026 | [B07XGZSYJV](https://www.amazon.com/dp/B07XGZSYJV) | 1 pk | $13.93 | ACQUIRED |
| ~~Fotek SSR-25DA solid state relay~~ (surplus. Order #112-0680575-1213862, placed April 17, 2026 | [B08FR13GYR](https://www.amazon.com/dp/B08FR13GYR) | 1 | $13.92 | ACQUIRED (surplus) |
| ~~Inline AC fuse holder kit, 5×20 mm + assorted fuses~~ (surplus. Order #112-5222697-3918636, placed April 17, 2026 | [B07BC8DW3L](https://www.amazon.com/dp/B07BC8DW3L) | 1 | $12.86 | ACQUIRED (surplus) |
| ~~Leviton CR020-W 20 A 125 VAC single receptacle~~ (surplus. Order #112-2763596-7866631, placed April 17, 2026 | [B003ATTR8Y](https://www.amazon.com/dp/B003ATTR8Y) | 1 | $3.26 | ACQUIRED (surplus) |
| MXR IEC 60320 C14 panel-mount AC inlet, 10 A / 250 VAC (10 pk). Order #112-4054778-9500227, placed April 21, 2026 | [B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ) | 1 pk | $6.96 | ACQUIRED |
| Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed (6 pk). Order #112-9710760-9385027, placed April 21, 2026 | [B08VS8D4WC](https://www.amazon.com/dp/B08VS8D4WC) | 1 pk | $24.00 | ACQUIRED |
| uxcell C14 panel-mount inlet, 10 A, 3-pin straight (single). Order #112-2063260-0973008, placed April 24, 2026 | [B07PXSLBF4](https://www.amazon.com/dp/B07PXSLBF4) | 1 | $7.39 | ACQUIRED |
| Tripp Lite P006-006 NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed. Order #112-2843637-5886607, placed April 24, 2026 | [B0000511C0](https://www.amazon.com/dp/B0000511C0) | 1 | $9.21 | ACQUIRED |
| Legrand Radiant 1597BKCCD12 15 A self-test GFCI, decorator duplex, black. Order #112-6714135-1147434, placed May 20, 2026 | [B017HAB4BO](https://www.amazon.com/dp/B017HAB4BO) | 2 | $41.72 | ACQUIRED (delivered May 21) |
| Mean Well IRM-90-12ST encapsulated 80 W / 12 V / 6.7 A PSU. Order #112-1500299-7944264, placed April 21, 2026 | [B0CNRST18V](https://www.amazon.com/dp/B0CNRST18V) | 1 | $31.66 | ACQUIRED |
| Mean Well IRM-90-12ST encapsulated 80 W / 12 V / 6.7 A PSU. Order #112-9276465-1199416, placed June 20, 2026 | [B0CNRST18V](https://www.amazon.com/dp/B0CNRST18V) | 1 | $32.31 | ACQUIRED (delivered Jun 22) |
| Mean Well LRS-200-12 enclosed 204 W / 12 V / 17 A PSU. Order #112-9091100-8229010, placed April 17, 2026 | [B0874XQ82F](https://www.amazon.com/dp/B0874XQ82F) | 1 | $30.03 | ACQUIRED |
| P3 Kill-A-Watt P4400 power meter (bench). Order #112-0118962-3725825, placed April 17, 2026 | [B00009MDBU](https://www.amazon.com/dp/B00009MDBU) | 1 | $34.31 | ACQUIRED |

## 10. User interface — buttons, LEDs, air switch

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| KRAUS garbage-disposal air-switch kit, matte black. Order #112-0545074-9805025, placed February 23, 2026 | [B096319GMV](https://www.amazon.com/dp/B096319GMV) | 3 | $42.85 ea | ACQUIRED |
| 7 mm 12 V prewired momentary micro pushbutton, 12 pc. Order #114-8283262-7030641, placed February 6, 2026 | [B0F43GYWJ6](https://www.amazon.com/dp/B0F43GYWJ6) | 1 pk | $7.71 | ACQUIRED |
| EDGELEC 120 pc 12 V prewired LED assortment, 5 mm. Order #114-8283262-7030641, placed February 6, 2026 | [B07PVVL2S6](https://www.amazon.com/dp/B07PVVL2S6) | 1 pk | $13.93 | ACQUIRED |
| DIYables Passive Piezo Buzzer Module, 5 V, 2-pack. Order #112-8061650-4642611, placed May 11, 2026 | [B0DYDN31PV](https://www.amazon.com/dp/B0DYDN31PV) | 1 pk (2) | $6.42 | ACQUIRED (delivered May 14) |

## 11. Enclosure hardware

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Probrico 3-3/4" CC solid cabinet pulls, SS round T-bar, black (5 pk). Order #114-3717852-7039428, placed March 7, 2026 | [B0DHHK94Y5](https://www.amazon.com/dp/B0DHHK94Y5) | 1 pk | $13.93 | ACQUIRED |
| Amerock bar pulls 3-3/4" matte-black (10 pk). Order #114-3717852-7039428, placed March 7, 2026 | [B0DLWMV3RM](https://www.amazon.com/dp/B0DLWMV3RM) | 1 pk | $27.05 | ACQUIRED |
| Neodymium disc magnets 3×1 mm. Order #112-2147768-5852208, placed March 15, 2026 | [B0BQ3LPGZ1](https://www.amazon.com/dp/B0BQ3LPGZ1) | 1 | $20.90 | ACQUIRED |
| ruthex M3 Threaded Inserts Short, 100 pc, RX-M3Sx4.0 brass heat-set | [B0D39W228K](https://www.amazon.com/dp/B0D39W228K) | 1 pk (100) | $10.71 | ACQUIRED (delivered May 11) |
| ruthex M2 Threaded Inserts, 70 pc, RX-M2x4 brass heat-set (3.2 mm insert hole). Order #112-2773449-1292200, placed June 22, 2026 | [B088QJG676](https://www.amazon.com/dp/B088QJG676) | 1 pk (70) | $10.71 | ON-ORDER (arriving Jun 24) |
| BNUOK M3 × 25 mm Hex Socket Head Cap Screws, 60 pc, 12.9 alloy steel, black oxide finish. Order #112-2495614-5144234, placed May 10, 2026 | [B0DJQGF665](https://www.amazon.com/dp/B0DJQGF665) | 1 pk (60) | $8.57 | ACQUIRED (delivered May 11) |
| BNUOK M3 × 12 mm Hex Socket Head Cap Screws, 120 pc, 12.9 alloy steel, black oxide finish. Order #112-0144900-5988250, placed May 10, 2026 | [B0DJQGVK8S](https://www.amazon.com/dp/B0DJQGVK8S) | 1 pk (120) | $8.57 | ACQUIRED (delivered May 11, spare stock) |
| BNUOK M3 × 10 mm Hex Socket Head Cap Screws, 120 pc, 12.9 alloy steel, black oxide finish. Order #112-6542724-2528248, placed June 22, 2026 | [B0DJQGGDP2](https://www.amazon.com/dp/B0DJQGGDP2) | 1 pk (120) | $8.57 | ON-ORDER (arriving Jun 24) |
| BNUOK M3 × 12 mm Hex Socket Head Cap Screws, 120 pc, 304 stainless steel (18-8), bright finish. Order #112-3709957-5726619, placed June 2, 2026 | [B0DJQGMQZM](https://www.amazon.com/dp/B0DJQGMQZM) | 1 pk (120) | $8.66 | ACQUIRED (delivered Jun 3) |
| Sutemribor M2 × 6 mm Hex Socket Head Cap Screws, 105 pc, M2-0.4, 12.9 alloy steel, black oxide finish, fully threaded. Order #112-1905695-2405047, placed June 22, 2026 | [B0CXQ7Q7L3](https://www.amazon.com/dp/B0CXQ7Q7L3) | 1 pk (105) | $18.22 | ON-ORDER (arriving Jun 24) |
| LVDALAB PTFE Membrane Filter, ø13 mm × 0.45 µm, 100 pc, non-sterile. Order #112-4393734-6836206, placed May 11, 2026 | [B0D41KT345](https://www.amazon.com/dp/B0D41KT345) | 1 pk (100) | $13.23 | ACQUIRED (delivered May 12) |
| Mudder PTFE / PVC / PU tubing cutter, ≤3/4" OD (3-pk, black). Order #112-8598924-2300214, placed May 17, 2026 | [B08VW15TK8](https://www.amazon.com/dp/B08VW15TK8) | 1 pk (3) | $12.86 | ACQUIRED (delivered May 18) |

## 12. Shop / bench infrastructure

General shop equipment supporting fabrication, assembly, and teardown. Not project-specific but purchased for this build.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| VEVOR adjustable 48" workbench w/ power outlet, wheels, pegboard, 2000 lb load. Order #114-1978684-7068269, placed April 20, 2026 | [B0FCD13KKQ](https://www.amazon.com/dp/B0FCD13KKQ) | 2 | $172.64 ea | ACQUIRED |
| NEIKO 01407A digital caliper, 0–6", stainless, inch/fraction/mm LCD — bench metrology (CAD reference measurements, incl. the faucet display housing/PCB dimensions). Order #114-9764609-4555460, placed Mar 22, 2026 | [B000GSLKIW](https://www.amazon.com/dp/B000GSLKIW) | 1 | $27.23 | ACQUIRED (delivered Mar 24) |

## 13. Printing consumables

3D-printer filament stock used for printed mechanical parts (cold-core shells, bladder cradles, enclosure, hopper, etc.). PETG is the default per bom.md §7; specialty filaments below are for specific parts requiring flexibility or chemical resistance.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| SpoolHaus PEBA Super Bowden 1.75 mm, 1 kg. Order #114-5148466-4469057, placed April 19, 2026 | [B0G1L5XVH2](https://www.amazon.com/dp/B0G1L5XVH2) | 1 | $64.34 | ACQUIRED |
| Siraya Tech Flex 1.75 mm TPU. Order #114-4402537-9406656, placed April 19, 2026 | [B0CVXF33Z1](https://www.amazon.com/dp/B0CVXF33Z1) | 1 | $33.88 | ACQUIRED |
| SUNLU Official 3D Printer Filament Dryer S4. Order #114-9764609-4555460, placed March 22, 2026 | [B0CQJMV71Z](https://www.amazon.com/dp/B0CQJMV71Z) | 1 | $125.47 | ACQUIRED (delivered March 25) |
| Polymaker 3D Printing Filament Storage Box, 4-Pack (PolyDryer Box x4). Order #114-9764609-4555460, placed March 22, 2026 | [B0FHPS82YG](https://www.amazon.com/dp/B0FHPS82YG) | 1 pk (4) | $117.96 | ACQUIRED (delivered March 25) |
| SUNLU Official 3D Printer Filament Dryer E2. Order #114-9662555-0662608, placed April 5, 2026 | [B0F5PMMXKD](https://www.amazon.com/dp/B0F5PMMXKD) | 1 | $321.74 | ACQUIRED (delivered April 7) |
| DUROZZLE 0.6mm Diamond PCD Nozzle Hotend, L-side (H2D/H2S/P2S/A1 series). Order #112-9688188-4729035, placed May 8, 2026 | [B0GWDBQW4G](https://www.amazon.com/dp/B0GWDBQW4G) | 1 | $64.24 | ACQUIRED (delivered May 9 1:27 PM) |
| DUROZZLE 0.6mm Tungsten Carbide Nozzle Hotend, L-side (H2D/H2S/P2S/A1 series). Order #112-7749428-2806629, placed May 8, 2026 | [B0GWDDKG47](https://www.amazon.com/dp/B0GWDDKG47) | 1 | $37.43 | ACQUIRED (delivered May 9 8:37 AM, used on touch-flo-shell PET-CF attempt 7) |
| Comfy Materials FDA-compliant food-grade PETG-Carbon, 1.75 mm × 1 kg, Gray. Order #112-3739807-8848229, placed May 9, 2026 | [B0BTLNK74C](https://www.amazon.com/dp/B0BTLNK74C) | 2 | $75.06 | ACQUIRED (delivered May 9 6:31 PM) |
| Bambu Lab Induction Heating Assembly - Right (H2C and H2C Laser, Bambu SKU 3DPP431) | [innoaddi.com](https://www.innoaddi.com/products/induction-heating-assembly-right) | 1 | $68.98 | ACQUIRED (delivered May 26) |
| Shineboc 20-pc Wet/Dry Sanding Sponge Set, foam-backed silicon-carbide, 3" × 4", 9 grits (180/320/400/600/800/1200/2000/2500/3000). Order #112-0610257-0936212, placed May 11, 2026 | [B0D8ZC6HKY](https://www.amazon.com/dp/B0D8ZC6HKY) | 1 pk (20) | $10.71 | ACQUIRED (delivered May 12) |
| Polymaker Fiberon PET-CF17, 1.75 mm × 1 kg, Black. Order #114-0500457-4192257, placed May 17, 2026 | [B0G2CC2YP8](https://www.amazon.com/dp/B0G2CC2YP8) | 2 | $96.50 | ACQUIRED (delivered May 18) |
| Polymaker Fiberon PET-CF17, 1.75 mm × 3 kg, Black. Order #114-7618665-2979463, placed June 13, 2026 | [B0DJNVQJX9](https://www.amazon.com/dp/B0DJNVQJX9) | 1 | $117.96 | ACQUIRED (delivered June 15) |
| SunTop food-contact-compliant PETG, 1.75 mm × 1 kg, Clear/Transparent. Order #112-1471049-5385066, placed May 17, 2026 | [B0FP34MJ94](https://www.amazon.com/dp/B0FP34MJ94) | 2 | $49.32 | ACQUIRED (delivered May 18) |
| Elmer's disappearing purple school glue sticks, washable, 6 g × 12 — print-bed adhesion/release layer. Order #114-9764609-4555460, placed Mar 22, 2026 | [B003ULCZ7M](https://www.amazon.com/dp/B003ULCZ7M) | 1 pk (12) | $7.38 | ACQUIRED (delivered Mar 24) |

## 14. Soldering + small-signal electrical tools

Bench soldering capability for through-hole, wire-to-pad (pogo pin leads), and general small-signal electrical work. Ordered as a single batch April 22, 2026 (Amazon order # 112-0066205-0960237, 17 line items, $395.31 pre-tax / $423.95 delivered; delivered Apr 23, 2026). Iron tier intentionally chosen at the ~$100 Hakko sweet spot — above the $40 unregulated-tip trap, below the $300+ pro cartridge systems that are overkill for hobby use.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Hakko FX-888D digital soldering station, 70 W, adjustable 120–899 °F. Order #112-0066205-0960237, placed April 22, 2026 | [B0D4DJW54S](https://www.amazon.com/dp/B0D4DJW54S) | 1 | $130.27 | ACQUIRED |
| Kester 24-6337-0027 63/37 Sn/Pb rosin-core solder, 0.031" / 1 lb. Order #112-0066205-0960237, placed April 22, 2026 | [B0149K4JTY](https://www.amazon.com/dp/B0149K4JTY) | 1 | $52.12 | ACQUIRED |
| KOTTO solder fume extractor, 60 W w/ activated-carbon filter. Order #112-0066205-0960237, placed April 22, 2026 | [B07VWDN29F](https://www.amazon.com/dp/B07VWDN29F) | 1 | $42.89 | ACQUIRED |
| AstroAI digital multimeter, 2000-count auto-ranging. Order #112-0066205-0960237, placed April 22, 2026 | [B071JL6LLL](https://www.amazon.com/dp/B071JL6LLL) | 1 | $32.16 | ACQUIRED |
| Klein Tools 11063W Kurve self-adjusting wire stripper, AWG 10–20. Order #112-0066205-0960237, placed April 22, 2026 | [B00CXKOEQ6](https://www.amazon.com/dp/B00CXKOEQ6) | 1 | $24.62 | ACQUIRED |
| MG Chemicals 8341 no-clean rosin flux paste, 49 g (1.7 oz) jar. Order #112-0066205-0960237, placed April 22, 2026 | [B09FWB6L5L](https://www.amazon.com/dp/B09FWB6L5L) | 1 | $21.66 | ACQUIRED |
| MG Chemicals 99.9% anhydrous isopropyl alcohol, 16 oz. Order #112-0066205-0960237, placed April 22, 2026 | [B0BZ21DBJ6](https://www.amazon.com/dp/B0BZ21DBJ6) | 1 | $18.61 | ACQUIRED |
| Kaisi heat-resistant silicone repair mat, 17.7" × 11.8". Order #112-0066205-0960237, placed April 22, 2026 | [B07DGVRYL3](https://www.amazon.com/dp/B07DGVRYL3) | 1 | $12.86 | ACQUIRED |
| Chemtronics Soder-Wick #60-3-5 desoldering braid, 0.075" × 5 ft. Order #112-0066205-0960237, placed April 22, 2026 | [B01I7Q2ULA](https://www.amazon.com/dp/B01I7Q2ULA) | 1 | $12.61 | ACQUIRED |
| 3M Virtua CCS safety glasses, clear anti-fog. Order #112-0066205-0960237, placed April 22, 2026 | [B00AEXKR4C](https://www.amazon.com/dp/B00AEXKR4C) | 1 | $12.43 | ACQUIRED |
| BEEYUIHF no-clean liquid soldering flux, dropper bottle. Order #112-0066205-0960237, placed April 22, 2026 | [B0G2G6WFPZ](https://www.amazon.com/dp/B0G2G6WFPZ) | 1 | $10.71 | ACQUIRED |
| AORAEM helping-hands w/ 4 flex arms + magnifier. Order #112-0066205-0960237, placed April 22, 2026 | [B08DNMT96W](https://www.amazon.com/dp/B08DNMT96W) | 1 | $9.64 | ACQUIRED |
| QWORK mini heat gun, 300 W / 200–450 °C. Order #112-0066205-0960237, placed April 22, 2026 | [B09NDCCW29](https://www.amazon.com/dp/B09NDCCW29) | 1 | $9.62 | ACQUIRED |
| Hakko T18-D16 chisel tip, 1.6 mm. Order #112-0066205-0960237, placed April 22, 2026 | [B004OR9BV4](https://www.amazon.com/dp/B004OR9BV4) | 1 | $9.64 | ACQUIRED |
| Hakko T18-D12 chisel tip, 1.2 mm. Order #112-0066205-0960237, placed April 22, 2026 | [B004OR6BU8](https://www.amazon.com/dp/B004OR6BU8) | 1 | $9.64 | ACQUIRED |
| T18-compatible heat-set insert tip kit, 7-piece, M2/M2.5/M3/M4/M5/M6/M8. Order #112-4234665-4274626, placed May 10, 2026 | [B0CS662NVK](https://www.amazon.com/dp/B0CS662NVK) | 1 kit (7 tips) | $13.93 | ACQUIRED (delivered May 11) |
| Heat-shrink tubing assortment kit, 2:1 ratio, assorted sizes/colors. Order #112-0066205-0960237, placed April 22, 2026 | [B0FRNMXN6Q](https://www.amazon.com/dp/B0FRNMXN6Q) | 1 | $7.50 | ACQUIRED |
| Disposable flux brushes, horsehair, 1/2" × 6" (pack). Order #112-0066205-0960237, placed April 22, 2026 | [B07PHG2DQY](https://www.amazon.com/dp/B07PHG2DQY) | 1 pk | $6.96 | ACQUIRED |
| DSD TECH SH-U09B3 USB-C to TTL serial adapter, CP2102N — service-flash path into the faucet display S3 over UART0 (GPIO 43/44) once its USB-C connector comes off for the gooseneck mount. Order #112-6318240-4305018, placed Jun 10, 2026 | [B09KXT6W46](https://www.amazon.com/dp/B09KXT6W46) | 1 | $10.71 | ACQUIRED (delivered Jun 11) |
| FAST CHIP low-melt SMD removal alloy, 4.5 ft — iron-only removal of the faucet display S3's USB-C connector and TF slot (keeps rework heat away from the panel glued to the far side of the PCB). Order #112-3079158-6326618, placed Jun 10, 2026 | [B00OOBIJ6I](https://www.amazon.com/dp/B00OOBIJ6I) | 1 | $15.00 | ACQUIRED (delivered Jun 11) |
| ELEGOO polyimide high-temp tape, 4-roll bundle (1/8", 1/4", 1/2", 1") — masking around board-level rework. Order #112-0906598-6371411, placed Jun 10, 2026 | [B072Z92QZ2](https://www.amazon.com/dp/B072Z92QZ2) | 1 (4 rolls) | $10.71 | ACQUIRED (delivered Jun 11) |
| iFixit precision tweezers set (extra-fine, angled, blunt; ESD coating) — board-level rework and BOOT-pad bridging on the faucet display S3. Order #112-2746979-9145060, placed Jun 10, 2026 | [B079K874CQ](https://www.amazon.com/dp/B079K874CQ) | 1 set (3) | $12.82 | ACQUIRED (delivered Jun 11) |
| KATA micro flush cutters, 2-pack — precision side cutters for board-level work (header-strip cutting, lead trimming); shared with 3D-printing post-processing. Order #114-9764609-4555460, placed Mar 22, 2026 | [B0BBML9M2V](https://www.amazon.com/dp/B0BBML9M2V) | 1 pk (2) | $8.89 | ACQUIRED (delivered Mar 24) |
| Klein Tools 11057 wire cutter/stripper, 20–30 AWG solid / 22–32 AWG stranded — fine-gauge stripper for the 28 AWG faucet-display harness conductors; the §14 Klein 11063W bottoms out at 20 AWG. Order #112-3574693-0507435, placed Jun 11, 2026 | [B000XEUPMQ](https://www.amazon.com/dp/B000XEUPMQ) | 1 | $23.56 | ACQUIRED (delivered Jun 13) |
| Kester 44 63/37 RMA rosin-core solder, 0.020" / 3/4 oz tube — finer solder for wire-to-pad work on the faucet display S3; the §14 0.031" spool is coarse for the small pads. Order #112-3550632-8904259, placed Jun 11, 2026 | [B00AYJ0B7Y](https://www.amazon.com/dp/B00AYJ0B7Y) | 1 | $14.94 | ACQUIRED (delivered Jun 13) |
| Hakko T18-D08 chisel tip, 0.8 mm — fine FX-888D tip for the faucet display S3's small through-hole pads; complements the T18-D12/D16 already on hand. Order #112-3550632-8904259, placed Jun 11, 2026 | [B004ORB8GK](https://www.amazon.com/dp/B004ORB8GK) | 1 | $9.87 | ACQUIRED (delivered Jun 13) |
| VECO-T T18 10-tip assortment (LB/BR02/D16/D32/B/K/C2/C5/I/S3), FX-888D-compatible aftermarket — adds the K knife for drag-soldering JST-XH connector rows and the high-mass D32/S3 for desoldering the pre-soldered MCP23017 GPIO + L298N control headers in the Dupont→JST migration; not genuine Hakko. Order #112-7486016-3622668, placed Jun 14, 2026 | [B0FWKGXFK7](https://www.amazon.com/dp/B0FWKGXFK7) | 1 kit (10 tips) | $20.37 | ACQUIRED (delivered Jun 15) |
| Hakko FR-301 portable desoldering tool, 140 W — self-contained heated hollow nozzle + motorized vacuum pump, trigger-actuated; clears solder-blocked plated through-holes in one pull. Bought after braid/manual wicking couldn't clear the plated barrels on the pre-soldered MCP23017 GPIO + L298N control headers during the Dupont→JST migration. Order #112-8278354-1449064, placed Jun 14, 2026 | [B07BKSLLG9](https://www.amazon.com/dp/B07BKSLLG9) | 1 | $225.20 | ACQUIRED (delivered Jun 15) |
| No-clean lead-free rosin solder flux paste, 4-pack 10cc syringes w/ assorted blunt dispensing tips — needle-tip paste flux for SMD/wire-to-pad rework; the dispensing-syringe form the jarred §14 8341 lacks. Order #112-4685860-9927453, placed Jun 17, 2026 | [B0GGQNNF98](https://www.amazon.com/dp/B0GGQNNF98) | 1 (4 syringes) | $13.93 | ACQUIRED (delivered Jun 18) |

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
| 2026-06-10 | us741350370718978049 | Induction Heating Assembly - Right ×1 (H2C / H2C Laser) + shipping + tax | $71.83 | ACQUIRED (delivered Jun 15) |
| 2026-06-17 | us743915395468910593 | PETG Basic Black 30105 ×10 + PETG Translucent Clear 32101 ×10 (1 kg refills, bulk) | $224.04 | ACQUIRED (delivered Jun 20) |
| **§15 subtotal — 17 orders (17 ACQUIRED)** | | | **ACQUIRED $8,677.34** | |

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
| SanDisk Ultra Fit USB 3.1 256 GB low-profile flash drive (SDCZ430-256G-G46). Order #112-0147397-3280206, placed May 2, 2026 | [B07857Y17V](https://www.amazon.com/dp/B07857Y17V) | 1 | $45.41 | ACQUIRED (delivered Mon May 4) |
| SanDisk Ultra Fit USB 3.2 Gen 1 256 GB low-profile flash drive, 400 MB/s (SDCZ430-256G-GAM46) — second timelapse-capture drive. Order #112-1916518-0515440, placed Jun 13, 2026 | [B0BY2TT9TD](https://www.amazon.com/dp/B0BY2TT9TD) | 1 | $46.02 | ACQUIRED (delivered Jun 14) |

## 20. McMaster-Carr direct

Industrial-supply orders direct from McMaster-Carr (mcmaster.com). First McMaster line item on the ledger; opens as a new vendor row in the breakdown.

| Order date | McMaster order # | Item | $ | Status |
|---|---|---|---|---|
| 2026-05-10 | 7139410 / 0510DBREDENSTEINER | 316 SS Ultra-Low-Profile SHCS, M3 × 0.50 × 8 mm (P/N 91223A413) — shelf spare (superseded by M3×6, then obsolete) | $59.67 | ACQUIRED (delivered May 13, obsolete) |
| 2026-05-22 | 7833043 / 0522DBREDENSTEINER | 316 SS Ultra-Low-Profile SHCS, M3 × 0.50 × 6 mm (P/N 91223A412) — shelf spare (obsolete on arrival) | $51.69 | ACQUIRED (delivered May 23, obsolete) |

## 21. Silicone molding — Zone C hopper-funnel

Vacuum-degassed silicone casting for the removable, dishwasher-safe Zone C hopper-funnel ([printed-parts/zone-c/](/hardware/printed-parts/zone-c/README.md)): a two-piece printed mold poured with food-grade platinum silicone (BBDINO 40A — ~69 mL / ~78 g per funnel, ~13 funnels per kit), vacuum-degassed in a chamber driven by the §6 Orion 4 CFM vacuum pump (B08P1WRZ1S) + 1/4" SAE manifold, then oven post-cured. Pigmented black to hide concentrate staining; food contact (fat-free) qualified by the wetted-surface screen, not a cert. The printed core's food-contact face is sealed with a clear-acrylic coat that releases the silicone without inhibiting cure; release runs on it and the cavity.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| PB Motor Tech 5-gallon stainless vacuum chamber, 18.9 L, 11.8" × 11.8" interior, tempered-glass lid + glycerin gauge + shutoff valve + hose — degassing chamber for the silicone hopper-funnel pours; mates the §6 Orion 4 CFM vacuum pump via 1/4" SAE flare. Order #112-7063184-8235469, placed June 22, 2026 | [B0D78ZM928](https://www.amazon.com/dp/B0D78ZM928) | 1 | $95.99 | ON-ORDER (arriving Jun 24) |
| Nuwave Bravo 30-QT 12-in-1 convection toaster oven, 50–500 °F, top/bottom heater control — silicone post-cure bake (drives off volatiles + completes the platinum cure for the food-contact funnel). Order #112-7063184-8235469, placed June 22, 2026 | [B00IXBMS6M](https://www.amazon.com/dp/B00IXBMS6M) | 1 | $129.99 | ON-ORDER (arriving Jun 24) |
| Rubbermaid Commercial stainless monitoring thermometer, 60–580 °F — post-cure oven-temperature verification. Order #112-0401256-3893007, placed June 22, 2026 | [B005KDEIZ0](https://www.amazon.com/dp/B005KDEIZ0) | 1 | $9.52 | ACQUIRED (delivered Jun 22) |
| BBDINO 40A food-contact platinum silicone mold-making kit, 2.42 lb, 1:1 by weight — base silicone for the cast hopper-funnel (~78 g/funnel ≈ ~13 funnels per kit). Order #112-8255970-7923460, placed June 22, 2026 | [B0FHHBGSQK](https://www.amazon.com/dp/B0FHHBGSQK) | 1 kit | $35.16 | ON-ORDER (arriving Jun 23) |
| BBDINO black silicone pigment, high-concentrated platinum-cure, 150 g — colorant for the cast hopper-funnel at ≤2% by weight (carbon-black, hides concentrate staining; food-contact qualified by the wetted-surface screen per [reservoir/wetted-surface-test.md](/hardware/printed-parts/cold-core/reservoir/wetted-surface-test.md), not a cert). Order #112-7063184-8235469, placed June 22, 2026 | [B0BVR3R58V](https://www.amazon.com/dp/B0BVR3R58V) | 1 | $18.97 | ON-ORDER (arriving Jun 24) |
| Mann Ease Release 200, 14 oz aerosol — addition-cure-compatible mold release for the printed hopper-funnel mold; used on the cavity and on the core's clear-acrylic seal (it is a release film, not a silicone fluid, so it does not add siloxane to the food face — any trace is cleared by the funnel's post-cure bake + wetted-surface screen). Order #112-0411698-8891425, placed June 22, 2026 | [B002YEBO1O](https://www.amazon.com/dp/B002YEBO1O) | 1 | $21.99 | ON-ORDER (arriving Jun 23) |
| TCP Global 32 oz / 1000 mL graduated mixing cups (25-pk) — silicone-degassing batch cups, sized for the 3–4× vacuum rise of a ~70 mL pour. Order #112-0401256-3893007, placed June 22, 2026 | [B08HNCGY4N](https://www.amazon.com/dp/B08HNCGY4N) | 1 pk (25) | $17.99 | ACQUIRED (delivered Jun 22) |
| Krylon K01303 Crystal Clear Acrylic, 11 oz gloss — clear-acrylic seal for the printed core's food-contact face: seals the print porosity and releases the platinum silicone without inhibiting the cure (acrylic, not enamel); finished + coupon-tested per [funnel-mold/README.md](/pie-in-the-sky/lite/printed-parts/funnel-mold/README.md) "Finish the core". Order #112-5591371-7092233, placed June 23, 2026 | [B00023JE7K](https://www.amazon.com/dp/B00023JE7K) | 1 | $9.89 | ON-ORDER (arriving Jun 25) |

---

## Still needed — LIKELY-TO-BUY

| Part | Notes |
|---|---|
| **Google Pixel 10a unlocked Android phone, 128 GB Obsidian (2026 model)** | Android development handset for the soda-machine app's Android side (`android/`). [B0GHRHXVN1](https://www.amazon.com/dp/B0GHRHXVN1). |
| **Smooth-On XTC-3D 3D-print smoothing epoxy, 6.4 oz (~$19.99) — optional** | Self-leveling epoxy base coat under the §21 core's clear-acrylic seal, only if the 0.08 mm core texture still telegraphs through the acrylic alone. Fills/seals; not the release face. [B01BKSLI9M](https://www.amazon.com/dp/B01BKSLI9M). |

---

## Totals

| Status | $ |
|---|---|
| ACQUIRED — hardware, tools & infra (§§1–17, 19, 20) | [$27,226.23](LEDGER_ACQUIRED_HW) |
| ACQUIRED — capitalized contract labor (§18) | [$2,607.92](LEDGER_LABOR) |
| ACQUIRED (combined) | [$29,834.15](LEDGER_ACQUIRED_COMBINED) |
| ON-ORDER | [$1,089.58](LEDGER_ON_ORDER) |
| MISSING — paid, not received (§1 copper bar) | [$42.89](LEDGER_MISSING) |
| LIKELY-TO-BUY | $0.00 |
| **Grand total — cash outlay** | [$30,966.62](LEDGER_GRAND_TOTAL) |

ACQUIRED hardware by section:

| § | Section | $ |
|---|---|---|
| 1 | Pressure vessel / carbonator fabrication | [$3,892.84](LEDGER_SEC1) |
| 2 | CO2 subsystem (incl. Lillium prototype carbonator $1,129) | [$1,785.10](LEDGER_SEC2) |
| 3 | Water supply + backflow prevention | [$889.15](LEDGER_SEC3) |
| 4 | Carbonator plumbing | [$225.27](LEDGER_SEC4) |
| 5 | Flavor subsystem | [$1,175.20](LEDGER_SEC5) |
| 6 | Refrigeration | [$1,882.74](LEDGER_SEC6) |
| 7 | Dispensing end | [$237.65](LEDGER_SEC7) |
| 8 | Electronics — controllers | [$208.03](LEDGER_SEC8) |
| 9 | Electronics — I/O, drivers, sensors, power | [$876.17](LEDGER_SEC9) |
| 10 | User interface | [$156.61](LEDGER_SEC10) |
| 11 | Enclosure hardware | [$124.48](LEDGER_SEC11) |
| 12 | Shop / bench infrastructure | [$372.51](LEDGER_SEC12) |
| 13 | Printing consumables | [$1,190.97](LEDGER_SEC13) |
| 14 | Soldering + small-signal tools | [$803.87](LEDGER_SEC14) |
| 15 | 3D printing equipment + filaments (Bambu direct) | [$8,677.34](LEDGER_SEC15) |
| 16 | Laser welding / cleaning / cutting | [$3,899.00](LEDGER_SEC16) |
| 17 | Domain / infrastructure | [$599.00](LEDGER_SEC17) |
| 19 | Video / marketing capture | [$91.43](LEDGER_SEC19) |
| 20 | McMaster-Carr direct | [$111.36](LEDGER_SEC20) |
| 21 | Silicone molding — Zone C hopper-funnel | [$27.51](LEDGER_SEC21) |

Notes:
- **MISSING** = paid but never received (no refund pursued) — a real cash outlay, tracked apart from ACQUIRED.
- **ON-ORDER** is the sum of in-transit rows (filter the tables by status); the figure above stays current via the script.

## Sources
[value](NAME) texts are updated by:
- `/hardware/scripts/_ledger_totals.py`
