# Purchases

Capital expenditure ledger for the soda-flavor-injector project. Scope: **2026 calendar year only** (Jan 1 → Apr 30, 2026 YTD). The project began in early 2026; nothing material predates it, and any pre-2026 spend that might otherwise be tempting to include is deliberately out of scope. Compiled from Amazon order history, direct-from-vendor receipts (Bambu Lab, XLaserlab, Namecheap), and capitalized contract labor (Anthropic / Claude API + subscription for AI-assisted engineering — CAD, firmware, electrical design, documentation, procurement research). Every item is either already in-hand (**ACQUIRED**), placed but not yet arrived (**ON-ORDER**), or identified as a planned purchase (**LIKELY-TO-BUY**). Non-project items (lawn/grass seed, dog products, personal groceries, shoes, etc.) are excluded.

This is **not** a bill of materials — see [bom.md](bom.md) for per-unit shipped-appliance parts. This file includes tools, fabrication equipment, donor parts, duplicates, consumables, PPE, bench fixtures, abandoned/surplus SKUs, and capitalized contract labor alongside the parts that end up in the product.

Price figures on bundled rows reflect the shipment total, not the per-item unit price. Owner / founder time is **not** tracked here — that's sweat equity, un-booked by design. Only cash outlays (including contracted labor via Anthropic) are on this ledger.

---

## 1. Pressure vessel / carbonator fabrication

Stainless sheet body, weld bungs, end-cap material, welding + forming tools. Originally specced for the racetrack pressure vessel (plan B, 304 SS); plan A has since pivoted to a vertical 5" OD × 0.065" wall **316 welded SS** round tube (OnlineMetals #12498, MTRs required, order 1020857414) + 1/4"-thick laser-cut **316 SS** circular end-cap plates from SendCutSend (`endcap-circular-2hole.dxf`, order SG019619) with 1/4" NPT direct-tapped (no weld bungs). Joining is done with the XLaserlab X1 Pro handheld laser welder. Racetrack inventory below is retained as plan-B fallback stock in 304 SS — plan B remains 304 even after the plan A 316 upgrade, accepted inconsistency for a fallback.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| VEVOR Slip Roll Machine, 24" forming width, 16 ga | [B0DZP1VBZY](https://www.amazon.com/dp/B0DZP1VBZY) | 1 | $235.94 | ACQUIRED |
| VEVOR 12-ton Hydraulic Shop Press (for dishing dies) | [B0BZ7YY3CP](https://www.amazon.com/dp/B0BZ7YY3CP) | 1 | $155.50 | ACQUIRED |
| Weldpro 3-Tier Welding Cart | [B08G5CW3DY](https://www.amazon.com/dp/B08G5CW3DY) | 1 | $179.99 | ACQUIRED |
| Blue Demon ER308L .030 stainless MIG wire, 2 lb | [B0025Q2HIU](https://www.amazon.com/dp/B0025Q2HIU) | 1 | $22.33 | ACQUIRED |
| RX Weld argon regulator / flowmeter | [B08P5BNHBX](https://www.amazon.com/dp/B08P5BNHBX) | 1 | $28.99 | ACQUIRED |
| Strong Hand magnetic V-pads welding magnet kit | [B00JXDSVA6](https://www.amazon.com/dp/B00JXDSVA6) | 1 | $27.24 | ACQUIRED |
| MAXMAN stainless steel wire brush set | [B08L7RXVG5](https://www.amazon.com/dp/B08L7RXVG5) | 1 | $11.39 | ACQUIRED |
| 1/4" NPT female weld bung, 304 SS stepped flange | [B07QNV8796](https://www.amazon.com/dp/B07QNV8796) | 1 pk | $7.99 | ACQUIRED |
| 4pc 1/4" NPT male hex nipple, 316 SS 5000 psi | [B0GD1QBLQ3](https://www.amazon.com/dp/B0GD1QBLQ3) | 1 pk | $15.19 | ACQUIRED |
| Millrose PTFE thread seal tape | [B07C9ZV4PG](https://www.amazon.com/dp/B07C9ZV4PG) | 1 | $20.07 | ACQUIRED |
| Viva Doria 100% pure food-grade citric acid, fine grain, 2 lb — post-weld passivation soak | [B0C5NQM8S1](https://www.amazon.com/dp/B0C5NQM8S1) | 1 | $9.99 | ACQUIRED |
| Cambro 6 QT square polycarbonate food container — citric-acid soak tub (one-time-use per unit, ships with tank) | [B001BZEQ44](https://www.amazon.com/dp/B001BZEQ44) | 1 | $20.00 | ACQUIRED |
| findmall ER308L .035 MIG wire, 10 lb spool — higher-volume follow-on to Blue Demon 2 lb (description fix: ledger previously said .030, actual product is .035 per Amazon listing) | [B0C52XQB39](https://www.amazon.com/dp/B0C52XQB39) | 1 | $90.68 | ACQUIRED |
| PGN ER308L .030 MIG wire, 10 lb spool — second stainless MIG wire spool (alt brand to findmall) | [B09WRZDBPN](https://www.amazon.com/dp/B09WRZDBPN) | 1 | — | ACQUIRED (price pending — order total not yet posted) |
| **STARTECHWELD ER316L .030 MIG wire, 10 lb spool, 8" OD / 2" center bore** — correct filler for the 316L plan-A vessel welds (308L would lose the molybdenum across the joint, defeating the point of the 316L upgrade); same form factor as the existing 308L spools so it drops into the X1 Pro wire feeder without a drive-roll change. Order 112-2295053-5101056, Apr 24, 2026, delivered Apr 27 | [B09BKFBXT9](https://www.amazon.com/dp/B09BKFBXT9) | 1 | $129.50 | ACQUIRED |
| Caiman premium goat-grain TIG / multi-task welding gloves — PPE for laser welder | [B07T6VLSK3](https://www.amazon.com/dp/B07T6VLSK3) | 1 | $23.05 | ACQUIRED |
| Caiman premium goat-grain TIG welding gloves — second pair (variant ASIN, Large, white/gold) | [B07T1NYXHM](https://www.amazon.com/dp/B07T1NYXHM) | 1 | $23.05 | ACQUIRED |
| YTKavq 1/4" × 2" × 12" C110 pure copper flat bar, soft-annealed — weld backer / heat-sink chill bar (order 112-0935480-2206657, Apr 22, $39.99 + $2.90 tax) | [B0DR2PX6TT](https://www.amazon.com/dp/B0DR2PX6TT) | 1 | $42.89 | MISSING — Amazon marked delivered 2026-04-23 but item never in box (co-shipped in tracking TBA330422235762 with gauge kit from order 112-9742741-7165035; only gauge kit received). No self-service refund path available; would require live chat. Refund not pursued. |
| YTKavq 1/4" × 2" × 12" C110 pure copper flat bar — replacement buy after 112-0935480-2206657 went missing. Order 112-4953236-4101019, Apr 23, 2026, delivered Apr 24 | [B0DR2PX6TT](https://www.amazon.com/dp/B0DR2PX6TT) | 1 | $42.89 | ACQUIRED |
| 304 SS 4" × 6" × 1/16" (16 ga / 1.5 mm) sheet, 2-pk — welding practice coupons, matches end-cap thickness | [B0DFXXQZD3](https://www.amazon.com/dp/B0DFXXQZD3) | 3 pk | $48.24 | ACQUIRED |
| 304 SS 4" × 4" × 0.04" (19 ga / 1 mm) sheet, 4 pc — welding practice coupons, matches body thickness | [B0C5LWVLCD](https://www.amazon.com/dp/B0C5LWVLCD) | 1 | $13.93 | ACQUIRED |
| Drill America 1/4" NPT HSS pipe tap + 1-1/2" OD round die kit — thread chasing / direct-tapping 1/4" 316 SS plates for plan A vessel | [B0DXN1LDKT](https://www.amazon.com/dp/B0DXN1LDKT) | 1 | $18.80 | ACQUIRED |
| MOTOKU 38 mm / 1.5" OD heavy-duty round die handle — companion to Drill America die | [B073ZX58PH](https://www.amazon.com/dp/B073ZX58PH) | 1 | $13.99 | ACQUIRED |
| Tap Magic EP-Xtra pipe-tap cutting fluid, 16 oz (size variant on listing B00DHMHSGM) — required for hand-tapping 1/4" NPT into 1/4"-thick 316 SS plate (plan A direct-tap path eliminates weld bungs B07QNV8796) | [B00DHMHSGM](https://www.amazon.com/dp/B00DHMHSGM) | 1 | $17.01 | ACQUIRED |
| WEN 4208T 2.3 A 8" 5-speed benchtop drill press — drill/tap station for 316 SS end-cap plates and fixture work. Order 112-2348373-7907448, Apr 29, 2026; line $104.00 + $7.54 allocated tax = **$111.54 delivered** | [B08ZVT5JKC](https://www.amazon.com/dp/B08ZVT5JKC) | 1 | $111.54 | ON-ORDER (delivers Sat May 2) |
| Drill America 1/4"–1-1/8" tap-capacity adjustable tap wrench, DWT series — hand driver for starting/finishing 1/4"-18 NPT threads in the 316 SS end-cap plates. Same order 112-2348373-7907448; line $30.79 + $2.23 allocated tax = **$33.02 delivered** | [B00DMEYTLW](https://www.amazon.com/dp/B00DMEYTLW) | 1 | $33.02 | ON-ORDER (delivers Sat May 2) |
| Drill America DWT64006 Qualtech HSS pipe tap, 1/4"-18 NPT — spare / known-good single pipe tap for direct-tapped end-cap ports. Same order 112-2348373-7907448; line $9.83 + $0.71 allocated tax = **$10.54 delivered** | [B01DZD1Y9Y](https://www.amazon.com/dp/B01DZD1Y9Y) | 1 | $10.54 | ON-ORDER (delivers Sat May 2) |
| Brown & Sharpe spring-loaded tap guide, 1/2" hardened shank — keeps pipe tap square while starting threads under the drill press / jig-bore setup. Same order 112-2348373-7907448; line $25.59 + $1.86 allocated tax = **$27.45 delivered** | [B005317ZMC](https://www.amazon.com/dp/B005317ZMC) | 1 | $27.45 | ON-ORDER (delivers Sat May 2) |
| Mollom 124 mm / 4-7/8" HSS M42 bi-metal hole saw with arbor + pilot bits — cuts near-5" fixture pockets/discs for vessel/end-cap jig stock. Same order 112-2348373-7907448; line $17.89 + $1.30 allocated tax = **$19.19 delivered** | [B0BZQ4J5B1](https://www.amazon.com/dp/B0BZQ4J5B1) | 1 | $19.19 | ON-ORDER (delivers Sat May 2) |
| 12 mm Baltic birch plywood, 1/2" × 8" × 8", B/BB grade (2 pc) — stiff fixture stock for the end-cap drilling/tapping jig. Same order 112-2348373-7907448; line $9.99 + $0.72 allocated tax = **$10.71 delivered** | [B0DP8597Q2](https://www.amazon.com/dp/B0DP8597Q2) | 1 box | $10.71 | ON-ORDER (delivers Sat May 2) |
| ACXFOND 1/4" MDF boards, 8" × 10" (20 pk) — sacrificial drill-press backers and template stock for fixture iteration. Same order 112-2348373-7907448; line $23.99 + $1.74 allocated tax = **$25.73 delivered** | [B0F1FJYDQ3](https://www.amazon.com/dp/B0F1FJYDQ3) | 1 pk | $25.73 | ON-ORDER (delivers Sat May 2) |
| Franklin International 1412 Titebond III wood glue, 4 oz — glue-up for laminated wood fixture stock. Same order 112-2348373-7907448; line $4.98 + $0.36 allocated tax = **$5.34 delivered** | [B0002YQ378](https://www.amazon.com/dp/B0002YQ378) | 1 | $5.34 | ON-ORDER (delivers Sat May 2) |
| Storystore 4" heavy-duty steel C-clamps (4 pk) — clamps fixture glue-ups and small workpieces at the drill press. Same order 112-2348373-7907448; line $19.99 + $1.45 allocated tax = **$21.44 delivered** | [B0DHX78G97](https://www.amazon.com/dp/B0DHX78G97) | 1 pk | $21.44 | ON-ORDER (delivers Sat May 2) |
| Bosch DSB1013 1" × 6" Daredevil Standard Spade Bit — 1" through-hole capability for fixture/jig stock and any 1" pass-throughs required during vessel fab. Order 111-4630388-1572202, Apr 29, 2026, $4.99 + $0.36 tax = **$5.35 delivered**, arriving Sat May 2 | [B001NGPAA0](https://www.amazon.com/dp/B001NGPAA0) | 1 | $5.35 | ON-ORDER |
| **OnlineMetals #12498 — 5" OD × 0.065" wall 316 welded SS round tube, cut to 6.0" length, MTRs required**; order 1020857414, Apr 24, 2026; qty 10 @ $67.35 ea = $673.50 + $13.43 ship + $49.80 tax = **$736.73 delivered** ($73.67/vessel × 10 vessels of stock); UPS Ground in process | onlinemetals.com | 10 | $736.73 | ON-ORDER |
| **SendCutSend order SG019619 — 1/4" 316 SS circular endcap plates** (`endcap-circular-2hole.dxf`, 4.860" disc with 2× 7/16" tap-pilot holes; SendCutSend bills bounding box 4.86" × 4.86"); order placed + paid Apr 24, 2026; qty 20 @ $28.96 ea = $579.20 + FREE ship + $41.99 tax = **$621.19 delivered** ($31.06/plate × 2 plates/vessel = $62.12/vessel × 10 vessels of stock); deburring included; in production queue | sendcutsend.com | 20 | $621.19 | ON-ORDER |
| SendCutSend order SQ65E969 — 304 SS 0.048" body blanks (`carbonator_body_blank.dxf`, 15.509" × 6"), qty 2 × $28.06 = $56.12 subtotal + FREE ship + $4.07 tax = $60.19; invoice Apr 16, 2026. OBSOLETE: old single-sheet plan, superseded by half-sheet plan (see SP54G453) — blanks held as spare/practice stock | sendcutsend.com | 2 | $60.19 | ACQUIRED |
| SendCutSend order SV07U813 — 304 SS 0.060" end-cap blanks: top (`endcap_racetrack_domed_top.dxf`) qty 2 × $10.91 + bottom (`endcap_racetrack_domed_bottom_blank.dxf`) qty 2 × $10.31 = $42.44 subtotal + FREE ship + $3.08 tax = $45.52; invoice Apr 16, 2026. Covers 2 vessels (1 top + 1 bottom per vessel) | sendcutsend.com | 4 | $45.52 | ACQUIRED |
| SendCutSend order SP54G453 — 304 SS 0.048" laser-cut + deburred body half-sheets (`carbonator_body_half_blank.dxf`, 7.754" × 6"), qty 10; invoice Apr 24, 2026; $125.30 subtotal + FREE ship + $9.08 tax = $134.38 on Visa x5607 | sendcutsend.com | 10 | $134.38 | ON-ORDER (in production; parts entered production 2026-04-23) |

## 2. CO2 subsystem

Regulator, CO2 line, push-to-connect adapters for the CO2 side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| TAPRITE E-T742 CO2 dual-gauge primary regulator, CGA-320 | [B00L38DRD0](https://www.amazon.com/dp/B00L38DRD0) | 1 | $96.47 | ACQUIRED |
| 10 ft 5/16" ID beer CO2 line w/ 4 hose clamps | [B0D1RB3TF6](https://www.amazon.com/dp/B0D1RB3TF6) | 1 | $13.50 | ACQUIRED |
| DERPIPE push-to-connect 5/16" tube x 1/4" NPT (5 pk) | [B09LXVGPG7](https://www.amazon.com/dp/B09LXVGPG7) | 1 pk | $10.71 | ACQUIRED |
| VUYOMUA 0.8 gal SS portable air tank (bench test fixture) | [B0BV6FMMJP](https://www.amazon.com/dp/B0BV6FMMJP) | 1 | $60.05 | ACQUIRED |
| Control Devices SV-100 safety valve, 1/4" NPT, 100 psi set pressure | [B0D361X97X](https://www.amazon.com/dp/B0D361X97X) | 1 | $16.06 | ACQUIRED |

## 3. Water supply + backflow prevention

Feed-water inlet, filter, ASSE 1022 backflow preventer and its vent-line hardware, quick-connect tubing for the potable side feeding the carbonator.

| Part | Link | Qty | $ | Status |
|---|---|---|---|---|
| Multiplex 19-0897 ASSE 1022 backflow preventer, 3/8" NPT × 3/8" MFL — howdybrewer order #6779764932824, Apr 16, 2026; qty 1 @ $38.99 + $9.99 standard shipping + $3.54 tax = **$52.52 delivered**; still unshipped 8 days later, prompted Midwest Beverage second-source buy below | [howdybrewer.com](https://www.howdybrewer.com/products/multiplex-backflow-preventor-assembly-1022-3-8-npt-x-3-8-mfl) | 1 | $52.52 | ON-ORDER |
| **Multiplex 19-0897 ASSE 1022 backflow preventer, 3/8" NPT × 3/8" MFL** — midwestbev order MB11053, Apr 24, 2026; qty 4 @ $29.33 = $117.32 + $28.48 UPS Ground + $0.00 tax = **$145.80 delivered** ($36.45/unit × 4 units of stock); cheaper second-source after the howdybrewer order above stalled | [midwestbev.com](https://www.midwestbev.com/products/asse-1022-backflow-preventer) | 4 | $145.80 | ON-ORDER |
| Hooshing 3/8" flare × 1/4" FNPT brass adapter (2 pk) — for Multiplex MFL outlet | [B0BNHVV6HT](https://www.amazon.com/dp/B0BNHVV6HT) | 1 pk | $10.71 | ACQUIRED |
| Sealproof 1/4" ID × 3/8" OD food-grade clear PVC, 10 ft — for atmospheric vent telltale | [B07D9DK94V](https://www.amazon.com/dp/B07D9DK94V) | 1 | $8.46 | ACQUIRED |
| LOKMAN 304 SS worm-gear hose clamps, 10–16 mm (20 pk) — for vent line | [B076Q7QVNM](https://www.amazon.com/dp/B076Q7QVNM) | 1 pk | $8.99 | ACQUIRED |
| Waterdrop 15UC-UF 0.01 µm inline fridge/ice-maker filter | [B085G9TZ4L](https://www.amazon.com/dp/B085G9TZ4L) | 1 | $62.99 | ACQUIRED |
| HAOCHEN brass angle stop add-a-tee 3/8"×3/8"×1/4" | [B0DLKHHGL6](https://www.amazon.com/dp/B0DLKHHGL6) | 1 | $11.99 | ACQUIRED |
| Lifevant 32.8 ft 1/4" OD water tubing + 12 quick-connects | [B0DKCZ5W66](https://www.amazon.com/dp/B0DKCZ5W66) | 1 | $9.99 | ACQUIRED |
| John Guest 1/4" OD × 1/8" NPT male push-fit | [B07V6XKZG9](https://www.amazon.com/dp/B07V6XKZG9) | 1 | $5.00 | ACQUIRED |
| John Guest PI1208S acetal bulkhead union (1/4" QC) | [B0C1F3QR7N](https://www.amazon.com/dp/B0C1F3QR7N) | 2 | $11.49 ea | ACQUIRED |
| SAMSUNG HAF-QIN-3P carbon block refrigerator filter (3 pk) | [B09HR7H8X7](https://www.amazon.com/dp/B09HR7H8X7) | 1 pk | $97.10 | ACQUIRED |
| Yetaha RO 1/4" water flow-adjust valve | [B07GDFWB8R](https://www.amazon.com/dp/B07GDFWB8R) | 1 | $12.86 | ACQUIRED |
| SEAFLO 22-Series 12V 1.3 GPM 100 psi on-demand pump | [B0166UBJX4](https://www.amazon.com/dp/B0166UBJX4) | 1 | $48.25 | ACQUIRED |

## 4. Carbonator plumbing (pressurized side)

Check valves, sparge stone + barb adapter for internal-sparge CO2 carbonation, compression fittings on the water/CO2 pressure side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| ChillWaves 304 SS in-line split check valve 1/4" NPT M×F (silicone seat — bench only) | [B0DPLBYZB4](https://www.amazon.com/dp/B0DPLBYZB4) | 1 | $18.22 | ACQUIRED |
| ChillWaves 304 SS in-line **Siamese** check valve 1/4" NPT M×F (1-pack) — second ChillWaves variant (different listing/ASIN from B0DPLBYZB4 above; this is the Siamese-body geometry, evaluated alongside the split-body unit + the GASHER PTFE soft-seat valves). Order #112-0876134-8491423, Apr 24, 2026, $14.99 + $1.09 tax = **$16.08 delivered**, delivered Apr 26 | [B0DPL88RHC](https://www.amazon.com/dp/B0DPL88RHC) | 1 | $16.08 | ACQUIRED |
| GASHER 1/4" NPT SS one-way check valve (2 pk) — production water-side and CO2-side check valves; PTFE soft-seat on metal poppet confirmed by inspection 2026-04-25; suitable for production and long-term field service. Order #112-9584993-4999458, Apr 24, 2026, qty 1 pack @ $15.00 delivered Apr 25 (the inspected pack) | [B0FV2D2FFX](https://www.amazon.com/dp/B0FV2D2FFX) | 1 pk | $15.00 | ACQUIRED |
| GASHER 1/4" NPT SS one-way check valve (2 pk) — install/test spares + SKU-continuity hedge against the production order above; same ASIN, same listing, qty 2 packs = 4 valves. Order #112-7934476-0257818, Apr 25, 2026, qty 2 packs @ $15.00 ea = **$30.00**, delivered Apr 27 | [B0FV2D2FFX](https://www.amazon.com/dp/B0FV2D2FFX) | 2 pk | $15.00 ea | ACQUIRED |
| LTWFITTING 316 SS 1/4" hose barb × 1/4" MNPT — port-1 (CO2 in via internal sparge) bottom-plate adapter; barb faces inward to silicone tube → sparge stone | [B017N4TTMA](https://www.amazon.com/dp/B017N4TTMA) | 1 | $13.65 | ACQUIRED |
| FERRODAY 0.5 µm sintered 316 SS sparge stone, 1/4" barb input (2-set) — internal sparge stone, hangs in vessel water column on silicone tube from port-1 barb adapter; replaces the atomizer carbonation path | [B091C5Y6L9](https://www.amazon.com/dp/B091C5Y6L9) | 1 | $14.97 | ACQUIRED |
| ~~Beduan 1/4" male spiral cone atomization nozzle, 316 SS~~ — SUPERSEDED by internal sparge architecture; the spiral-cone nozzle requires a high pressure differential to atomize and at our working ΔP (~15–25 PSI between pump output and 70 PSI headspace) it produces a stream not a spray. Bench-test inventory only, not in shipped BOM | [B07LGPD3GB](https://www.amazon.com/dp/B07LGPD3GB) | 1 | $9.99 | ACQUIRED (superseded) |
| VALVENTO 316 SS 1/4" OD compression × 1/4" NPT adapter (2 pk) — joins bottom-plate 1/4" NPT outlet (port 3) to 1/4" tubing run to faucet (order 112-6216768-3197856 covers BOTH this and the SS tube 5-pk B0F6SYFK48 below; line price $11.99 pre-tax + $0.86 allocated tax = $12.85 delivered) | [B0DXZZBK7D](https://www.amazon.com/dp/B0DXZZBK7D) | 1 pk | $12.85 | ACQUIRED |
| VALVENTO 1/4" OD 316 SS tube, 12" length (5 pk) — same order 112-6216768-3197856 as the compression adapter B0DXZZBK7D above; line price $16.99 pre-tax + $1.24 allocated tax = $18.23 delivered. Earlier ledger duplicated the $31.08 order grand total onto BOTH lines, double-counting by $31.08; corrected during the post-Kamoer audit pass | [B0F6SYFK48](https://www.amazon.com/dp/B0F6SYFK48) | 1 pk | $18.23 | ACQUIRED |
| TAISHER 304 SS compression square needle valve 1/4" | [B0CLXHZZCW](https://www.amazon.com/dp/B0CLXHZZCW) | 1 | $32.15 | ACQUIRED |

## 5. Flavor subsystem

Peristaltic pumps, solenoids, bag-in-box connector, silicone delivery tubing, barb fittings, bladders, check valves on the flavor side.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Kamoer KPHM400-SW3B25 400 ml/min 12 V peristaltic pump (BPT, sold by Kamoer Fluid Tech Shanghai) — order #114-1015191-6799441 (Feb 18, 2026, qty 1 @ $32.55) + order #112-0545074-9805025 (Feb 23, 2026, qty 2 @ $32.55) = 3 pumps total at $32.55/ea delivered. Earlier ledger entry recorded "qty 2 @ $99.40 ea" — neither figure matches Amazon's current or historical listing ($32.55 then and now), so most likely a previous editor folded the 3-pump line-item total ($97.65) into a single-unit price by mistake. | [B09MS6C91D](https://www.amazon.com/dp/B09MS6C91D) | 3 | $32.55 ea | ACQUIRED |
| Beduan 12 V 1/4" inlet water solenoid (NC) — flavor/manifold valve; per-unit delivered $9.64 ($8.99 pre-tax + tax). Earlier ledger range "$9.64–$19.28 ea" had the high end wrong — $19.28 was a 2-unit order grand total mistakenly recorded per-unit (Kamoer-style); BOM impact nil since BOM already uses $9.64 | [B07NWCQJK9](https://www.amazon.com/dp/B07NWCQJK9) | 3–4 lines | $9.64 ea | ACQUIRED (short vs 12-valve manifold) |
| Supply Depot Coke-compatible BIB connector, 3/8" red (2 pk) | [B0DMFK9B6P](https://www.amazon.com/dp/B0DMFK9B6P) | 1 pk | $19.99 | ACQUIRED |
| Platypus SoftBottle 1 L (bladder donor) | [B08PG3GMQ8](https://www.amazon.com/dp/B08PG3GMQ8) | 1 | $23.49 | ACQUIRED |
| Platypus SoftBottle 1 L "Waves" (bladder donor) | [B00ZX0ERE2](https://www.amazon.com/dp/B00ZX0ERE2) | 1 | $15.35 | ACQUIRED |
| Platypus Platy 2 L collapsible bottle (bladder donor) | [B000J2KEGY](https://www.amazon.com/dp/B000J2KEGY) | 1 | $15.94 | ACQUIRED |
| Platypus Hoser hydration tube kit | [B07N1T6LNW](https://www.amazon.com/dp/B07N1T6LNW) | 2 | $24.95 ea | ACQUIRED |
| JoyTube 3/8" ID food-grade silicone tubing, 10 ft | [B089YGDB55](https://www.amazon.com/dp/B089YGDB55) | 1 | $11.99 | ACQUIRED |
| Metaland 3/8" ID food-grade silicone tubing | [B08L1RS757](https://www.amazon.com/dp/B08L1RS757) | 1 | $7.99 | ACQUIRED |
| Metaland 1/4" ID food-grade silicone tubing | [B08L1ST6ST](https://www.amazon.com/dp/B08L1ST6ST) | 1 | $7.99 | ACQUIRED |
| Metaland 1/2" ID silicone tubing | [B0BC7K5B91](https://www.amazon.com/dp/B0BC7K5B91) | 1 | $9.99 | ACQUIRED |
| Metaland 1/8" ID silicone tubing | [B08XM1V475](https://www.amazon.com/dp/B08XM1V475) | 1 | $8.99 | ACQUIRED |
| Quickun 3/4" ID silicone tubing | [B091SXP7DD](https://www.amazon.com/dp/B091SXP7DD) | 1 | $9.99 | ACQUIRED |
| Pure silicone 3/8" ID × 1/2" OD high-temp tube, 10 ft | [B07XMGHHLK](https://www.amazon.com/dp/B07XMGHHLK) | 1 | $16.99 | ACQUIRED |
| ANPTGHT 1/8" ID × 1/4" OD black silicone tubing — actually qty 2 ordered @ $12.99 ea pre-tax = $25.98 + $1.88 tax = $27.86 delivered ($13.93/roll). Earlier ledger entry recorded "qty 1 @ $27.86" — Kamoer-style fold-up of the 2-roll grand total into a single-unit price (BOM impact nil since BOM consumes 1 roll/unit; qty fix reflects actual stock) | [B0BM4KQ6RT](https://www.amazon.com/dp/B0BM4KQ6RT) | 2 | $13.93 ea | ACQUIRED |
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
| Cambro food storage container 6 qt | [B001BZEQ44](https://www.amazon.com/dp/B001BZEQ44) | 1 | $21.45 | ACQUIRED |
| Pinnacle Mercantile F-style HDPE bottle set | [B0CFP9RRSF](https://www.amazon.com/dp/B0CFP9RRSF) | 1 | $16.99 | ACQUIRED |
| SodaStream Diet Mountain Dew concentrate | [B0CS191QMW](https://www.amazon.com/dp/B0CS191QMW) | 1 | $17.62 | ACQUIRED |
| SodaStream Diet Mountain Dew 4-pack | [B0G26HQWBY](https://www.amazon.com/dp/B0G26HQWBY) | 1 | $28.99 | ACQUIRED |
| SodaStream Pepsi Wild Cherry Zero 4-pack | [B0G4NRDQB8](https://www.amazon.com/dp/B0G4NRDQB8) | 1 | $28.99 | ACQUIRED |
| SodaStream Diet Cola 4-pack | [B01GQ2ZMKI](https://www.amazon.com/dp/B01GQ2ZMKI) | 1 | $18.89 | ACQUIRED |
| Magnetic pogo pin connector, 2-pin (2 pair) — pump cartridge | [B0CSX6ZQ1H](https://www.amazon.com/dp/B0CSX6ZQ1H) | 1 pk | $10.71 | ACQUIRED |

## 6. Refrigeration

Ice-maker donor units and copper coil for the chill loop.

| Part | Link | Qty | $ | Status |
|---|---|---|---|---|
| Frigidaire EFIC117-SS ice maker, 26 lb/day (donor) | [B07PCZKG94](https://www.amazon.com/dp/B07PCZKG94) | 1 | $78.70 | ACQUIRED |
| Countertop ice maker 26 lb/day (2nd donor) | [B0F42MT8JX](https://www.amazon.com/dp/B0F42MT8JX) | 1 | $63.80 | ACQUIRED |
| GOORY 1/4" OD × 50 ft ACR copper coil | [B0DKSW5VL9](https://www.amazon.com/dp/B0DKSW5VL9) | 1 | $68.63 | ACQUIRED |
| RIGID DV1910E Copper Coil Chiller, 12 V (alt path) — Lanxi Lizhide Refrigeration Equipment Co., Ltd (vendor brand "RIGID HVAC", Zhejiang, China; do not confuse with the American RIDGID plumbing-tool brand). Order #2604018778275 / RG-1264, placed Apr 1, 2026; one PayPal payment $580.00 to ann@rigidhvac.com via VISA x5607 (= $420 chiller + $160 standard shipping; customs declared low-value so $0 import duty under US $800 de minimis, no postage-due collected on receipt). ChinaPost tracking ZC64524933899 delivered to LINCOLN NE 68520 on 2026-04-27 11:26; physical receipt confirmed in mailbox 2026-04-30 | [rigidhvac.com](https://www.rigidhvac.com/) (direct order) | 1 | $580.00 | ACQUIRED |
| Fiberglass Supply Depot 2 lb 2-part closed-cell pour-in-place PU foam, 1 qt kit — cold-core insulation | [B08R7TX8QJ](https://www.amazon.com/dp/B08R7TX8QJ) | 1 kit | $39.99 | LIKELY-TO-BUY |
| HiLetgo DS18B20 waterproof 1-wire temperature probe, 1 m SS sheath (5 pk) — tank wall + evap coil sensors for compressor control | [B00M1PM55K](https://www.amazon.com/dp/B00M1PM55K) | 1 pk | $11.79 | ACQUIRED |
| Supco D111 replacement filter-drier, 1/4" × 1/4" sweat, XH-9 — wrong part, retained as spare drier (same XH-9 desiccant, own Schrader; useful if loop has to be reopened later) | [B00DM8KGXS](https://www.amazon.com/dp/B00DM8KGXS) | 1 | $11.95 | ACQUIRED |
| Supco SUD8358 UV-dye filter-drier, 1/4" × 1/4" — correct replacement drier, brazed in after venting to replace spent factory drier | [B009AX2O5W](https://www.amazon.com/dp/B009AX2O5W) | 1 | $13.40 | ACQUIRED |
| Mastercool 70025 cap-tube cutter — cleanly severs 0.042"/0.050" capillary tubing at the process-tube junction without crushing the bore | [B00NY1YHHE](https://www.amazon.com/dp/B00NY1YHHE) | 1 | $15.74 | ACQUIRED |
| Orion Motor Tech HVAC A/C manifold gauge set, 1/4" SAE | [B07CZB2SHZ](https://www.amazon.com/dp/B07CZB2SHZ) | 1 | $48.24 | ACQUIRED |
| Orion Motor Tech 4 CFM 1/3 HP single-stage vacuum pump, 110 V, 150 µ ultimate | [B08P1WRZ1S](https://www.amazon.com/dp/B08P1WRZ1S) | 1 | $78.28 | ACQUIRED |
| Supco BPV31 bullet-piercing valve — taps compressor process tube for initial vent + recharge access | [B00DM8J3MI](https://www.amazon.com/dp/B00DM8J3MI) | 1 | $7.37 | ACQUIRED |
| Smart Weigh Pro digital pocket scale, 2000 g × 0.1 g — refrigerant charge metering by mass | [B00IZ1YHZK](https://www.amazon.com/dp/B00IZ1YHZK) | 1 | $19.25 | ACQUIRED |
| Toptes PT520A refrigerant/hydrocarbon gas leak detector (description fix: ledger previously branded "Elitech", Amazon listing brand is Toptes) | [B0BTM3G8DK](https://www.amazon.com/dp/B0BTM3G8DK) | 1 | $42.89 | ACQUIRED |
| Enviro-Safe R-600a 3-pack (3× 6 oz self-sealing cans) + brass charging gauge — CME Biz / Enviro-Safe Refrigerants Inc., 22+ year hydrocarbon refrigerant mfr; brass gauge replaces need for separate 7/16" adapter and replaces the earlier notched-canister piercing kit | [B0CGG1WH1N](https://www.amazon.com/dp/B0CGG1WH1N) | 1 | $72.92 | ACQUIRED |
| Klein Tools 51006 3-in-1 tube bender, 1/4 / 5/16 / 3/8" OD — for forming the 1/4" ACR evaporator coil around the carbonator tank | [B0DPQX17WM](https://www.amazon.com/dp/B0DPQX17WM) | 1 | $21.98 | ACQUIRED |
| Wisscool 1/4" handheld tube straightener — de-coils 1/4" ACR copper before bending | [B0F6BPTW3T](https://www.amazon.com/dp/B0F6BPTW3T) | 1 | $24.99 | ACQUIRED |
| ESCO Institute EPA Section 608 Preparatory Manual — bought under the earlier assumption that recovery/recharge would hit HFC-regulated refrigerant; R-600a is Section 608-exempt (natural-refrigerant carveout) so the cert is NOT required for this build. Retained as general refrigeration reference / for any future non-hydrocarbon work. | [1930044607](https://www.amazon.com/dp/1930044607) | 1 | $22.47 | ACQUIRED |
| Bernzomatic TS8000 high-intensity torch head + MAP-Pro 3-can kit — silver-brazing heat source for 1/4" ACR copper joints (reaches ~650 °C+ needed for BCuP-5) | [B0BPMVTJ1R](https://www.amazon.com/dp/B0BPMVTJ1R) | 1 | $117.96 | ACQUIRED |
| Harris SSWF7 Stay Silv white brazing flux, 6.5 oz — protects joint from oxidation during brazing; required for BCuP-5 on copper-to-brass transitions | [B002BYLU52](https://www.amazon.com/dp/B002BYLU52) | 1 | $11.92 | ACQUIRED |
| Uniweld RHP400 nitrogen regulator, CGA-580 × 1/4" male flare, 0–400 psi delivery — dry-N2 purge during brazing to prevent internal scale | [B008HQ6GXO](https://www.amazon.com/dp/B008HQ6GXO) | 1 | $96.76 | ACQUIRED |
| RIDGID 31622 Model 150 constant-swing tubing cutter, 1/8"–1-1/8" — clean square cuts on 1/4" ACR before flaring/brazing | [B0009W6T8G](https://www.amazon.com/dp/B0009W6T8G) | 1 | $31.99 | ACQUIRED |
| RIDGID 23332 Model 345 flaring tool, 45° SAE — produces leak-tight flares on 1/4" ACR for manifold-gauge and Schrader tap connections | [B000X4K9KO](https://www.amazon.com/dp/B000X4K9KO) | 1 | $99.99 | ACQUIRED |
| BCuP-5 15% silver brazing alloy, 1/16" × 1 troy oz rod — low-flux-temp filler for copper-to-copper and copper-to-brass refrigeration joints | [B0DQ3ZMHK7](https://www.amazon.com/dp/B0DQ3ZMHK7) | 1 | $18.99 | ACQUIRED |
| 3M Scotch-Brite Maroon General Purpose Hand Pads, 6" × 9", 1-pack of 20 pads (3M 07447 equivalent) — abrasive pads cut into strips for cleaning 1/4" ACR copper OD and fitting sockets prior to flux + braze; ~2 pads per build across the 2–3 brazed joints in the refrigeration loop. Order 112-6573046-7656255, Apr 27, 2026, $26.90 + $0.00 ship + $1.95 tax = **$28.85 delivered**, delivered Apr 29, 20 pads/pack | [B07CGPCTHT](https://www.amazon.com/dp/B07CGPCTHT) | 1 pk | $28.85 | ACQUIRED |
| HVAC 1/4" OD copper slip coupling, ACR-grade, sweat × sweat, 10-pack — joins new evaporator coil outlet to factory suction line (both 1/4" OD). Order 112-0837919-8970627, Apr 23, 2026, $7.98 + $0.58 tax = **$8.56 delivered**, delivered Apr 24 | [B0FH549N6D](https://www.amazon.com/dp/B0FH549N6D) | 1 pk | $8.56 | ACQUIRED |
| Knipex 86 01 180 Pliers Wrench, 7.25" — smooth parallel-jaw pliers for pinch-swaging 1/4" ACR copper inlet down onto 0.031" capillary tube (progressive 60° rotation collapse technique, no reducer fitting required). Order 112-1057208-2782602, Apr 23, 2026, $53.20 + $3.86 tax = **$57.06 delivered**, delivered Apr 24 | [B07YLFLSJW](https://www.amazon.com/dp/B07YLFLSJW) | 1 | $57.06 | ACQUIRED |
| Joywayus brass 1/4" SAE 45° flare nut, 7/16"-20 thread, 5-pack — clamps flared 1/4" ACR copper stub onto RHP400 regulator outlet + HVAC charging hose for argon purge rig (reuses existing argon cylinder, no new gas purchase needed). Order 112-5788053-3609032, Apr 23, 2026, $7.99 + $0.58 tax = **$8.57 delivered**, delivered Apr 27 | [B0G1XJ2F68](https://www.amazon.com/dp/B0G1XJ2F68) | 1 pk | $8.57 | ACQUIRED |
| 3M 425 aluminum foil tape, 2" × 180 ft, thermally conductive — bridges tank ↔ coil thermal interface (applied under the coil, full lateral coverage of tank outer surface), replaces the generic "thermal compound" line originally specced for coil-to-tank interface; one 180 ft roll covers ~12 builds at ~15 ft/build. Order 112-3799575-6647414, Apr 23, 2026, $88.97 + $6.45 tax = **$95.42 delivered**, delivered Apr 26 | [B07BTW7C2N](https://www.amazon.com/dp/B07BTW7C2N) | 1 | $95.42 | ACQUIRED |
| Pouring Masters 5 oz / 150 mL graduated plastic mixing cups (50 pk) — foam-pour consumable for batching 2-part PU foam in measured shots; 4 cups per build. Order 112-0326855-5540223, Apr 27, 2026, $18.99 + $1.38 tax = **$20.37 delivered**, delivered Apr 29 | [B08JHH1DBF](https://www.amazon.com/dp/B08JHH1DBF) | 1 pk | $20.37 | ACQUIRED |
| JMU 6" wood tongue depressors, individually wrapped (100 pk) — foam-pour consumable; stir sticks for hand-mixing 2-part PU foam in graduated cups; 4 sticks per build. Order 112-8110646-3335448, Apr 27, 2026, $6.99 + $0.51 tax = **$7.50 delivered**, delivered Apr 29 | [B09H6ZP447](https://www.amazon.com/dp/B09H6ZP447) | 1 pk | $7.50 | ACQUIRED |
| SUP powder-free 4 mil nitrile exam gloves, X-Large, 100 ct (= 50 pairs) — foam-pour PPE (PU foam isocyanate component is a skin sensitizer); 1 pair per build. Variant ASIN B0G8SSMVKW (XL) replaces the earlier B0G8TRBJX7 (Large) which was placed and immediately cancelled (order 112-3159250-4061051, $0.00, no charge). Live order 112-8247392-7531444, Apr 27, 2026, $6.99 + $0.50 tax = **$7.49 delivered**, delivered Apr 29 | [B0G8SSMVKW](https://www.amazon.com/dp/B0G8SSMVKW) | 1 pk | $7.49 | ACQUIRED |

## 7. Dispensing end — faucet, flow sensor

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Westbrass A2031-NL-62 8" Touch-Flo cold-water faucet, matte black | [B0BXFW1J38](https://www.amazon.com/dp/B0BXFW1J38) | 1 | $32.18 | ACQUIRED |
| Westbrass D203-NL-62 6" Touch-Flo cold-water faucet, matte black | [B01MZ6JPXW](https://www.amazon.com/dp/B01MZ6JPXW) | 1 | $52.99 | ACQUIRED |
| Westbrass R2031-NL-12 8" Touch-Flo faucet, oil-rubbed bronze — third donor (harvest valve body for 3-tube dispense spout). Order 112-5236199-6056258, Apr 23, 2026; was delayed at Humble TX facility (Apr 26 expected slipped), ultimately delivered Apr 26 | [B01N5LVNQA](https://www.amazon.com/dp/B01N5LVNQA) | 1 | $20.95 | ACQUIRED |
| 1/4" OD × 12" 304 SS straight tube, 4 pc — center tube for 3-tube dispense spout (carbonated water path) | [B0F87DJDZW](https://www.amazon.com/dp/B0F87DJDZW) | 1 pk | $12.86 | ACQUIRED |
| 1/8" OD × 12" 304 SS straight tube, 4 pc — flanking tubes for 3-tube dispense spout (flavor injection paths) | [B0F87V8XCB](https://www.amazon.com/dp/B0F87V8XCB) | 1 pk | $8.57 | ACQUIRED |
| Beduan 304 SS compression ferrule sleeve, 1/4" OD, 5 pk — decorative compression ferrules for dispense spout tips | [B07V4K2KKH](https://www.amazon.com/dp/B07V4K2KKH) | 1 pk | $6.42 | ACQUIRED |
| Beduan 304 SS compression ferrule sleeve, 1/8" OD — decorative compression ferrules for dispense spout tips | [B07V8RJJYJ](https://www.amazon.com/dp/B07V8RJJYJ) | 1 pk | $5.35 | ACQUIRED |
| Pysrych 304 SS reducing compression union, 1/4" OD × 1/8" OD, 2 pk — joins 1/4" LLDPE supply to 1/8" SS spout tube for each flavor line inside the shroud | [B0BM4394Z4](https://www.amazon.com/dp/B0BM4394Z4) | 1 pk | $8.99 | ACQUIRED |
| Siptenk 1/4" OD brass tube stiffener insert, 100 pk — required on the LLDPE side of the 1/4" compression joint so the ferrule does not crush the soft tube | [B0FM77LLM1](https://www.amazon.com/dp/B0FM77LLM1) | 1 pk | $8.99 | ACQUIRED |
| DIGITEN G1/4" Hall-effect flow sensor 0.3–10 L/min | [B07QRXLRTH](https://www.amazon.com/dp/B07QRXLRTH) | 1 | $20.36 | ACQUIRED |
| DIGITEN G1/4" Hall-effect flow meter 0.3–6 L/min | [B07QS17S6Q](https://www.amazon.com/dp/B07QS17S6Q) | 1 | $9.49 | ACQUIRED |
| Eoiips polyethylene tubing 1/16" ID × 1/8" OD, 3.28 ft (1 m) — sized to slip inside the 1/8" OD SS flanking flavor-tube spouts (B0F87V8XCB) as a soft food-grade liner so pump-side flavor flow contacts PE rather than the SS spout wall, simplifying cleaning. Order 114-9634716-3126657, Apr 29, 2026, $7.49 + $0.54 tax = **$8.03 delivered**, delivered Apr 30 | [B0BWJ3S5NM](https://www.amazon.com/dp/B0BWJ3S5NM) | 1 | $8.03 | ACQUIRED |

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
| BOJACK L298N dual H-bridge motor driver (4-pack) — actual line $9.99 pre-tax + $0.72 allocated tax = $10.71 delivered (order 114-1015191-6799441, Feb 18, 2026, was a 3-line order: L298N $9.99 + Kamoer $32.55 + 12V PSU $9.99 = $52.53 subtotal + $3.80 tax = $56.33 grand total). Earlier ledger entry recorded "$56.33" against the L298N line — Kamoer-style fold-up of the entire mixed-order grand total into a single line, double-counted alongside the same order's Kamoer entry | [B0C5JCF5RS](https://www.amazon.com/dp/B0C5JCF5RS) | 1 pk | $10.71 | ACQUIRED |
| DS3231 AT24C32 RTC module (2 pk) | [B09LLMYBM1](https://www.amazon.com/dp/B09LLMYBM1) | 1 pk | $7.07 | ACQUIRED |
| HiLetgo DS3231 high-precision RTC (5 pk) | [B01N1LZSK3](https://www.amazon.com/dp/B01N1LZSK3) | 1 pk | $16.08 | ACQUIRED |
| EDGELEC 4.7 kΩ 1/4 W 1% metal-film resistor (100 pk) — DS18B20 1-wire bus pull-up between DATA and 3.3 V; 1 of 100 per unit. Order #112-0915506-0821038, Apr 26, 2026, $5.49 + $0.40 allocated tax = **$5.89 delivered** (co-shipped with Rubycon cap below; tax allocated pro-rata across the 2-line order) | [B07HDFHPP3](https://www.amazon.com/dp/B07HDFHPP3) | 1 pk | $5.89 | ACQUIRED |
| Rubycon 470 µF 25 V low-ESR (0.08 Ω) radial aluminum electrolytic capacitor, 10×12.5 mm (15 pk) — bulk decoupling on the 12 V solenoid rail at the ULN2803A driver modules; 25 V is the 2× derating standard for a 12 V rail (lifetime + headroom for inductive kickback transients above the rail); 1 of 15 per unit. Same order #112-0915506-0821038, Apr 26, 2026, $6.90 + $0.50 allocated tax = **$7.40 delivered** | [B0F8BZVBKF](https://www.amazon.com/dp/B0F8BZVBKF) | 1 pk | $7.40 | ACQUIRED |
| HiLetgo NJK-5002C Hall-effect proximity switch (2 pk) | [B01MZYYCLH](https://www.amazon.com/dp/B01MZYYCLH) | 1 pk | $8.49 | ACQUIRED |
| Gebildet reed switches, 14 mm glass body, NO (6 pk) — carbonator level sensing: 2 reeds per unit (low-level refill threshold + high-level full threshold) mounted externally on the 0.065" 304 SS tube wall (austenitic 304 is non-magnetic so the float magnet's field passes through) | [B0CW9418F6](https://www.amazon.com/dp/B0CW9418F6) | 1 pk | $6.42 | ACQUIRED |
| DEVMO MINI vertical float switch — donor; harvest the magnetic donut float, discard switch body. Float slides on a 1/8" 316L SS rod laser-welded vertically inside the carbonator vessel between the bottom and top end-cap plates | [B07T18PGJ4](https://www.amazon.com/dp/B07T18PGJ4) | 1 | $13.93 | ACQUIRED |
| ~~Tynulox 1/8" × 6" 304 SS round rod (10 pk)~~ — SUPERSEDED for production by Tandefio 316 SS rod B0CY4DWJFQ to keep all wetted parts at 316/316L. Retained as harvest stock for non-wetted sub-assemblies | [B0BKGS32KJ](https://www.amazon.com/dp/B0BKGS32KJ) | 1 pk | $8.56 | ACQUIRED (superseded) |
| Tandefio 1/8" × 12" 316 SS round rod (5 pk) — laser-welded vertically inside the carbonator vessel; cut from 12" to ~6" (yields 2 vessel rods per stick, 5-pk = 10 vessels of stock); carries the magnetic float for the external-reed level-sensing scheme. Replaces the Tynulox 304 rod B0BKGS32KJ for production so all wetted parts are 316/316L matching the new 316L vessel pivot. Order 112-7391312-2980226, Apr 24, 2026, delivered Apr 26 | [B0CY4DWJFQ](https://www.amazon.com/dp/B0CY4DWJFQ) | 1 pk | $8.57 | ACQUIRED |
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
| Waveshare MCP23017 I2C I/O expansion board (repeat ASIN) — second board for soldering experiments / one extra unit's worth beyond what's on hand. Order #112-7245467-6557007, Apr 26, 2026, $12.99 + $0.93 allocated tax − $0.17 allocated promo = **$13.75 delivered**. (Same 7-line order as the rest of the JST XH connector experimentation buy below; subtotal $81.92, tax $5.87, promo −$1.10, grand total $86.69, all allocations pro-rata) | [B07P2H1NZG](https://www.amazon.com/dp/B07P2H1NZG) | 1 | $13.75 | ACQUIRED (delivered Apr 27) |
| ULN2803A high-current driver module, 2-pc (repeat ASIN) — second pack for soldering experiments; with the existing pack on hand, total 4 modules = enough for 2 BOMs at the per-unit qty of 2. Same order #112-7245467-6557007, Apr 26, 2026, $6.59 + $0.47 allocated tax − $0.09 allocated promo = **$6.97 delivered** | [B0F872W528](https://www.amazon.com/dp/B0F872W528) | 1 pk | $6.97 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 4-pin connector kit (50 sets / 300 pcs) — 50× male PCB headers + 50× female 4-pin housings + 200× loose female crimp T-terminals; for I2C and UART hops between modules (per-unit qty needed: 2–4). Same order #112-7245467-6557007, Apr 26, 2026, $7.99 + $0.57 allocated tax − $0.11 allocated promo = **$8.45 delivered** | [B0B2RB524Y](https://www.amazon.com/dp/B0B2RB524Y) | 1 pk | $8.45 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 6-pin connector kit (50 sets / 400 pcs) — 50× male PCB headers + 50× female 6-pin housings + 300× loose female crimp T-terminals; for DS3231 RTC connections and any 6-conductor module hops (per-unit qty needed: 1–2). Same order #112-7245467-6557007, Apr 26, 2026, $8.69 + $0.62 allocated tax − $0.12 allocated promo = **$9.19 delivered** | [B0B2R8Q1JL](https://www.amazon.com/dp/B0B2R8Q1JL) | 1 pk | $9.19 | ACQUIRED (delivered Apr 27) |
| CQRobot JST XH 2.54 mm 9-pin connector kit (30 sets / 330 pcs) — 30× male PCB headers + 30× female 9-pin housings + 270× loose female crimp T-terminals; for ULN2803A module sides (8 channels + GND or COM = 9 pins per side; 2 modules × 2 sides per unit = 4 connectors per unit) and MCP23017 Port A/B rows (2 per unit). Same order #112-7245467-6557007, Apr 26, 2026, $8.69 + $0.62 allocated tax − $0.12 allocated promo = **$9.19 delivered** | [B0B2R73RQB](https://www.amazon.com/dp/B0B2R73RQB) | 1 pk | $9.19 | ACQUIRED (delivered Apr 29) |
| CQRobot/Zhansheng JST XH 2.54 mm pre-crimped bonded ribbon kit (15 cm / 5.9", 12-conductor ribbons × 8 + loose housings 2/3/4/5/6/7/8/9/10/12 P) — short-hop bonded-ribbon option: factory pre-crimped female XH terminals on both ends of a 12-wire bonded ribbon, user inserts the pre-crimped pins into housings of their choice (e.g. 9 of the 12 conductors into a 9-pin housing for ULN sides). 15 cm length only; for cable runs ≤ 6". Same order #112-7245467-6557007, Apr 26, 2026, $14.99 + $1.07 allocated tax − $0.20 allocated promo = **$15.86 delivered** | [B0F6C7X5CR](https://www.amazon.com/dp/B0F6C7X5CR) | 1 pk | $15.86 | ACQUIRED (delivered Apr 27) |
| Keszoox JST XH 2.54 mm pre-crimped wires, 50 cm × 22 AWG silicone, 20 pcs/pk in 10 colors — medium-length pre-crimped female XH pigtails (loose round wires, NOT bonded ribbon) for cable runs that span the cabinet; bundle into harness with zip ties at install. Qty 2 packs ordered for a total of 40 wires. Same order #112-7245467-6557007, Apr 26, 2026, qty 2 @ $10.99 = $21.98 + $1.58 allocated tax − $0.30 allocated promo = **$23.26 delivered** ($11.63/pack × 2) | [B0F8HMQRRN](https://www.amazon.com/dp/B0F8HMQRRN) | 2 pk | $11.63 ea | ACQUIRED (delivered Apr 30) |
| CR2032 3 V cell pack (RTC backup) | [B0C15WJXL2](https://www.amazon.com/dp/B0C15WJXL2) | 1 | $11.19 | ACQUIRED |
| Breadboard kit, 2×830 + 2×400 pt | [B07DL13RZH](https://www.amazon.com/dp/B07DL13RZH) | 1 pk | $6.83 | ACQUIRED |
| Gratury IP67 waterproof enclosure | [B08281V2RL](https://www.amazon.com/dp/B08281V2RL) | 1 | $23.58 | ACQUIRED |
| Teyleten 3.3 V relay module, opto-isolated, 10 A @ 250 VAC (5 pk) | [B07XGZSYJV](https://www.amazon.com/dp/B07XGZSYJV) | 1 pk | $12.99 | ACQUIRED |
| Teyleten Robot DC 1-channel optocoupler 3.3 V relay module (repeat ASIN, variant listing) — additional stock | [B07XGZSYJV](https://www.amazon.com/dp/B07XGZSYJV) | 1 | $13.93 | ACQUIRED |
| ~~Fotek SSR-25DA solid state relay~~ (surplus — overspecced for the load, not used) | [B08FR13GYR](https://www.amazon.com/dp/B08FR13GYR) | 1 | $13.92 | ACQUIRED (surplus) |
| ~~Inline AC fuse holder kit, 5×20 mm + assorted fuses~~ (surplus — bench-test gear, not production; 5 A fast-blow would nuisance-trip compressor inrush) | [B07BC8DW3L](https://www.amazon.com/dp/B07BC8DW3L) | 1 | $12.86 | ACQUIRED (surplus) |
| ~~Leviton CR020-W 20 A 125 VAC single receptacle~~ (surplus — wrongly spec'd as AC inlet; a female outlet isn't an inlet) | [B003ATTR8Y](https://www.amazon.com/dp/B003ATTR8Y) | 1 | $3.26 | ACQUIRED (surplus) |
| MXR IEC 60320 C14 panel-mount AC inlet, 10 A / 250 VAC (10 pk) — rear-panel mains inlet for standard computer-style line cord | [B07DCXKNXQ](https://www.amazon.com/dp/B07DCXKNXQ) | 1 pk | $6.96 | ACQUIRED |
| Monoprice NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed (6 pk) — ships in the box with the appliance | [B08VS8D4WC](https://www.amazon.com/dp/B08VS8D4WC) | 1 pk | $24.00 | ACQUIRED |
| uxcell C14 panel-mount inlet, 10 A, 3-pin straight (single) — diagnostic cross-test part, different-brand reference against MXR inlet to isolate whether the tight mating fit observed on the MXR + Monoprice pair comes from the inlet or the cord (order 112-2063260-0973008, Apr 24, delivered Apr 25) | [B07PXSLBF4](https://www.amazon.com/dp/B07PXSLBF4) | 1 | $7.39 | ACQUIRED |
| Tripp Lite P006-006 NEMA 5-15P → IEC C13 line cord, 18 AWG, 6 ft, UL-listed — diagnostic cross-test part, reference-class cord against Monoprice to isolate whether the tight mating fit is cord-side (order 112-2843637-5886607, Apr 24, delivered Apr 25) | [B0000511C0](https://www.amazon.com/dp/B0000511C0) | 1 | $9.21 | ACQUIRED |
| Mean Well IRM-90-12ST encapsulated 80 W / 12 V / 6.7 A PSU — primary appliance 12 V rail (per bom.md §1) | [B0CNRST18V](https://www.amazon.com/dp/B0CNRST18V) | 1 | $31.66 | ACQUIRED |
| Mean Well LRS-200-12 enclosed 204 W / 12 V / 17 A PSU — alternate/higher-capacity 12 V rail (bench evaluation vs IRM-90) | [B0874XQ82F](https://www.amazon.com/dp/B0874XQ82F) | 1 | $30.03 | ACQUIRED |
| P3 Kill-A-Watt P4400 power meter (bench) | [B00009MDBU](https://www.amazon.com/dp/B00009MDBU) | 1 | $34.31 | ACQUIRED |

## 10. User interface — buttons, LEDs, air switch

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| KRAUS garbage-disposal air-switch kit, matte black | [B096319GMV](https://www.amazon.com/dp/B096319GMV) | 3 | $39.95 ea | ACQUIRED |
| 7 mm 12 V prewired momentary micro pushbutton, 12 pc | [B0F43GYWJ6](https://www.amazon.com/dp/B0F43GYWJ6) | 1 pk | $7.19 | ACQUIRED |
| EDGELEC 120 pc 12 V prewired LED assortment, 5 mm | [B07PVVL2S6](https://www.amazon.com/dp/B07PVVL2S6) | 1 pk | $12.99 | ACQUIRED |

## 11. Enclosure hardware

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Probrico 3-3/4" CC solid cabinet pulls, SS round T-bar, black (5 pk) | [B0DHHK94Y5](https://www.amazon.com/dp/B0DHHK94Y5) | 1 pk | $12.99 | ACQUIRED |
| Amerock bar pulls 3-3/4" matte-black (10 pk) | [B0DLWMV3RM](https://www.amazon.com/dp/B0DLWMV3RM) | 1 pk | $25.22 | ACQUIRED |
| Neodymium disc magnets 3×1 mm | [B0BQ3LPGZ1](https://www.amazon.com/dp/B0BQ3LPGZ1) | 1 | $19.49 | ACQUIRED |

## 12. Shop / bench infrastructure

General shop equipment supporting fabrication, assembly, and teardown. Not project-specific but purchased for this build.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| VEVOR adjustable 48" workbench w/ power outlet, wheels, pegboard, 2000 lb load — actually qty 2 ordered (order 114-1978684-7068269, Apr 20, 2026) @ $160.97 ea = $321.94 + $23.34 tax = $345.28 delivered ($172.64/unit). Earlier ledger recorded "qty 1 @ $345.28" — Kamoer-style fold-up of the 2-unit grand total into a single-unit price | [B0FCD13KKQ](https://www.amazon.com/dp/B0FCD13KKQ) | 2 | $172.64 ea | ACQUIRED |

## 13. Printing consumables

3D-printer filament stock used for printed mechanical parts (cold-core shells, bladder cradles, pump cartridge, enclosure, hopper, etc.). PETG is the default per bom.md §7; specialty filaments below are for specific parts requiring flexibility or chemical resistance.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| SpoolHaus PEBA Super Bowden 1.75 mm, 1 kg — high-performance elastomer, candidate for gasket/seal prints | [B0G1L5XVH2](https://www.amazon.com/dp/B0G1L5XVH2) | 1 | $64.34 | ACQUIRED |
| Siraya Tech Flex 1.75 mm TPU — flexible filament for compliant prints (hopper silicone cover, pogo-pin gaskets, etc.) | [B0CVXF33Z1](https://www.amazon.com/dp/B0CVXF33Z1) | 1 | $33.88 | ACQUIRED |

## 14. Soldering + small-signal electrical tools

Bench soldering capability for through-hole, wire-to-pad (pogo pin leads), and general small-signal electrical work. Ordered as a single batch April 22, 2026 (Amazon order # 112-0066205-0960237, 17 line items, $395.31 pre-tax / $423.95 delivered; delivered Apr 23, 2026). Iron tier intentionally chosen at the ~$100 Hakko sweet spot — above the $40 unregulated-tip trap, below the $300+ pro cartridge systems that are overkill for hobby use.

| Part | ASIN link | Qty | $ | Status |
|---|---|---|---|---|
| Hakko FX-888D digital soldering station, 70 W, adjustable 120–899 °F — primary iron | [B0D4DJW54S](https://www.amazon.com/dp/B0D4DJW54S) | 1 | $121.47 | ACQUIRED |
| Kester 24-6337-0027 63/37 Sn/Pb rosin-core solder, 0.031" / 1 lb — leaded rosin-core for through-hole and wire joints | [B0149K4JTY](https://www.amazon.com/dp/B0149K4JTY) | 1 | $48.60 | ACQUIRED |
| KOTTO solder fume extractor, 60 W w/ activated-carbon filter — bench fume pull | [B07VWDN29F](https://www.amazon.com/dp/B07VWDN29F) | 1 | $39.99 | ACQUIRED |
| AstroAI digital multimeter, 2000-count auto-ranging — continuity / voltage / resistance bench meter | [B071JL6LLL](https://www.amazon.com/dp/B071JL6LLL) | 1 | $29.99 | ACQUIRED |
| Klein Tools 11063W Kurve self-adjusting wire stripper, AWG 10–20 — primary stripper for 18–24 AWG hookup wire | [B00CXKOEQ6](https://www.amazon.com/dp/B00CXKOEQ6) | 1 | $22.96 | ACQUIRED |
| MG Chemicals 8341 no-clean rosin flux paste, 10 mL syringe — paste flux for stubborn joints / rework | [B09FWB6L5L](https://www.amazon.com/dp/B09FWB6L5L) | 1 | $20.20 | ACQUIRED |
| MG Chemicals 99.9% anhydrous isopropyl alcohol, 16 oz — post-solder flux cleanup | [B0BZ21DBJ6](https://www.amazon.com/dp/B0BZ21DBJ6) | 1 | $17.35 | ACQUIRED |
| Kaisi heat-resistant silicone repair mat, 17.7" × 11.8" — bench work surface, magnetic-section screw organizer | [B07DGVRYL3](https://www.amazon.com/dp/B07DGVRYL3) | 1 | $11.99 | ACQUIRED |
| Chemtronics Soder-Wick #60-3-5 desoldering braid, 0.075" × 5 ft — solder removal | [B01I7Q2ULA](https://www.amazon.com/dp/B01I7Q2ULA) | 1 | $11.76 | ACQUIRED |
| 3M Virtua CCS safety glasses, clear anti-fog — PPE for soldering + heat-gun work | [B00AEXKR4C](https://www.amazon.com/dp/B00AEXKR4C) | 1 | $11.59 | ACQUIRED |
| BEEYUIHF no-clean liquid soldering flux, dropper bottle — wicks into joints via capillary action (complements paste) | [B0G2G6WFPZ](https://www.amazon.com/dp/B0G2G6WFPZ) | 1 | $9.99 | ACQUIRED |
| AORAEM helping-hands w/ 4 flex arms + magnifier — work holder for wire-to-pad soldering | [B08DNMT96W](https://www.amazon.com/dp/B08DNMT96W) | 1 | $8.99 | ACQUIRED |
| QWORK mini heat gun, 300 W / 200–450 °C — heat-shrink activation, light rework | [B09NDCCW29](https://www.amazon.com/dp/B09NDCCW29) | 1 | $8.97 | ACQUIRED |
| Hakko T18-D16 chisel tip, 1.6 mm — general-purpose tip for FX-888D | [B004OR9BV4](https://www.amazon.com/dp/B004OR9BV4) | 1 | $8.99 | ACQUIRED |
| Hakko T18-D12 chisel tip, 1.2 mm — fine-pitch tip for FX-888D | [B004OR6BU8](https://www.amazon.com/dp/B004OR6BU8) | 1 | $8.99 | ACQUIRED |
| Heat-shrink tubing assortment kit, 2:1 ratio, assorted sizes/colors — wire insulation post-solder | [B0FRNMXN6Q](https://www.amazon.com/dp/B0FRNMXN6Q) | 1 | $6.99 | ACQUIRED |
| Disposable flux brushes, horsehair, 1/2" × 6" (pack) — flux application, general cleanup | [B07PHG2DQY](https://www.amazon.com/dp/B07PHG2DQY) | 1 pk | $6.49 | ACQUIRED |

## 15. 3D printing equipment and filaments (Bambu Lab direct)

All purchased direct from us.store.bambulab.com (not via Amazon). Covers the printer itself (H2C AMS Combo), AMS expansion units (AMS HT × 2, AMS 2 Pro), hotends / nozzles / build plate, vision encoder, PTFE adapters, and every filament refill since the printer arrived. §13 holds the separate Amazon-sold filaments (SpoolHaus PEBA, Siraya Tech Flex TPU) — kept separate because the vendor and receipt trail are distinct.

Receipts grouped by order; each line in the table is one shipment. See Bambu Lab order history for the per-SKU breakdown.

| Order date | Bambu order # | Contents | $ | Status |
|---|---|---|---|---|
| 2026-03-22 | us712460111015776257 | **Bambu Lab H2C** (H2C AMS Combo) — founding purchase. Includes: H2C printer, initial filament assortment (PA6-CF Black ×2, TPU 95A HF Black ×2, ABS Black ×2, PLA Matte Ash Gray ×1, PLA Matte Charcoal ×1, PETG Basic Reflex Blue ×1, PETG Basic Black ×1), Vision Encoder / H2 Series, Bambu Engineering Plate / H2C, tungsten carbide nozzles 0.4mm ×2, H2C Induction Hotend (R) 0.2mm SS ×2, Bambu Hotend H2/P2S (L) 0.4mm HS ×2. Subtotal $3,080.58 + NE tax $223.33 | $3,303.91 | ACQUIRED |
| 2026-03-23 | us712597240994926592 | Liquid glue + shipping + tax | $25.71 | ACQUIRED |
| 2026-04-01 | us715792490246602753 | H2C Induction Hotend (R) 0.8mm HS ×1, H2C Induction Hotend (R) 0.4mm HS ×1, ASA Blue ×1, PLA Matte Marine Blue refill ×2, PLA Matte Charcoal ×4 (bulk) | $217.00 | ACQUIRED |
| 2026-04-03 | us716485517830578177 | PETG Basic Black refill ×4 (bulk), ABS Black refill ×4 (bulk) | $120.06 | ACQUIRED |
| 2026-04-06 | us717877837343809537 | **Bambu Lab AMS HT ×2**, Bambu 4-in-1 PTFE Adapter ×1 + shipping + tax | $314.22 | ACQUIRED |
| 2026-04-08 | us718417332286169089 | **Bambu Lab AMS 2 Pro ×1**, ASA Aero White ×2, AMS 2 Pro Switching Adapter ×1, Bambu 4-in-1 PTFE Adapter ×1 | $471.86 | ACQUIRED |
| 2026-04-13 | us720254914668109825 | TPU for AMS Black refill ×2 + shipping + tax | $82.54 | ACQUIRED |
| 2026-04-19 | us722538751263612929 | TPU 90A Black ×2, TPU 85A Black ×2 | $186.57 | ACQUIRED |
| 2026-04-21 | us722988823976337409 | PETG Translucent Clear ×4 (bulk) + shipping + tax | $81.46 | ACQUIRED |
| **§15 subtotal — 9 orders** | | | **$4,803.33** | |

## 16. Laser welding / cleaning / cutting

Handheld 3-in-1 laser system (welding, cleaning, cutting) used on the stainless pressure vessel and related SS fabrication. Purchased direct from the manufacturer; not on Amazon.

| Order date | Vendor / order # | Item | $ | Status |
|---|---|---|---|---|
| 2026-04-06 | XLaserlab (xlaserlab.com) — order #XLaserlab3271 | **XLaserlab X1 Pro** 3-in-1 Laser Welder / Cleaner / Cutter — **X1 PRO Ultimate Pack**, US plug. Ultimate Pack includes single wire feeder (confirmed in writing by vendor rep "Nina" 2026-04-08). Free shipping, no tax collected, card ending 5607. Arrived 2026-04-13. | $3,899.00 | ACQUIRED |

## 17. Domain / infrastructure

Internet infrastructure purchases. Currently just the product domain; additional infra (web hosting, email, SSL etc.) will land here as it's added.

| Order date | Vendor / order # | Item | $ | Status |
|---|---|---|---|---|
| 2026-03-22 | Namecheap — order #197680608 | **homesodamachine.com** — Premium domain, 1-year term. Privacy is via Namecheap's `WithheldForPrivacy` proxy, applied post-order (not a paid add-on). No SSL / hosting / WhoisGuard add-ons bundled. | $599.00 | ACQUIRED |

## 18. Capitalized contract labor — AI-assisted engineering

Not a physical part — direct cash outlay to Anthropic (Claude) for engineering design services specific to this asset: CAD / CadQuery STEP generation, firmware (ESP32 / RP2040 / S3), electrical design, documentation, BOM research and procurement, regulatory analysis. Under GAAP, contracted labor that produces a specific capital asset is capitalized into the asset's cost basis — same line as paying a mechanical-engineering firm for drawings. Booked here at the actual invoice amount, not at any implied hourly rate.

Scope reminder: 2026 YTD only (Jan 1 → Apr 22, 2026). Pre-2026 Claude spend is out of scope per ledger conventions (see intro). Owner / founder time is also NOT on this ledger — sweat equity, un-booked.

| Date range | Type | # of receipts | $ |
|---|---|---|---|
| 2026-01-17 → 2026-04-18 | Claude Pro subscription (via Apple iOS in-app purchase) | 4 × $20.00 | $80.00 |
| 2026-03-03 | Anthropic API — one-time prepaid credit | 1 | $50.00 |
| 2026-03-12 → 2026-04-22 | Anthropic API — auto-recharges + prepaid top-ups (ramp-up to ~$60/day by mid-April) | 49 | $2,477.92 |
| **§18 subtotal** | | **54 receipts** | **$2,607.92** |

---

## Non-Amazon / external sources

| Part | Source | $ | Status |
|---|---|---|---|
| Multiplex 19-0897 ASSE 1022 backflow preventer (qty 1 @ $38.99 + $9.99 ship + $3.54 tax = $52.52 delivered) | [howdybrewer.com](https://www.howdybrewer.com/products/multiplex-backflow-preventor-assembly-1022-3-8-npt-x-3-8-mfl) | $52.52 | ON-ORDER (order #6779764932824, Apr 16, 2026; still unshipped 8 days later) |
| Multiplex 19-0897 ASSE 1022 backflow preventer (qty 4 @ $29.33 + $28.48 UPS Ground + $0.00 tax = $145.80 delivered, $36.45/unit) | [midwestbev.com](https://www.midwestbev.com/products/asse-1022-backflow-preventer) | $145.80 | ON-ORDER (order MB11053, Apr 24, 2026) |
| Taprite 09T07105 ASSE 1022 backflow preventer (alternate, same spec) | [howdybrewer.com](https://www.howdybrewer.com/products/backflow-preventer-3-8inmpt3-8inmfl-x-1-4inb-vent-09t07105) | $49.99 | alt option |
| Lillium under-counter carbonator (current prototype cold + carbonated source) | direct import (see [how-this-got-built.md](../how-this-got-built.md)) | — | ACQUIRED |
| RIGID DV1910E Copper Coil Chiller, 12 V (Lanxi Lizhide / "RIGID HVAC", Zhejiang — not the US RIDGID brand) — order #2604018778275 / RG-1264, single PayPal payment $580 ($420 + $160 ship, $0 customs, $0 postage-due) on Apr 1, 2026; ChinaPost ZC64524933899 delivered LINCOLN NE 2026-04-27, in hand 2026-04-30 | [rigidhvac.com](https://www.rigidhvac.com/) direct | $580.00 | ACQUIRED |
| ~~Nitrogen cylinder from Airgas~~ | — | — | NOT NEEDED — argon purge uses existing argon cylinder currently feeding laser welder; RHP400 regulator (CGA-580) swaps onto argon cylinder for the braze job, HVAC manifold charging hose + flared 1/4" copper stub completes the rig. No new gas purchase required. |

---

## Still needed — LIKELY-TO-BUY

| Part | Notes |
|---|---|
| **CO2 cylinder** | 5 lb or 10 lb aluminum, CGA-320. Regulator in hand; tank not yet on Amazon. |
| **Additional flavor-manifold solenoids** | Manifold diagram needs 12 valves (V-A through V-J plus V-K-A and V-K-B); current Beduan B07NWCQJK9 count across orders is short. Verify qty per order, then top up. |

---

## Totals

| Status | $ |
|---|---|
| ACQUIRED — hardware (§§1–13, 15, 16, 17) | $15,699.62 |
| ACQUIRED — capitalized contract labor (§18) | $2,607.92 |
| ACQUIRED (combined) | $18,307.54 |
| ON-ORDER | ~$1,960.93 |
| LIKELY-TO-BUY | $39.99 |
| **Grand total** | ~$20,308.46 |

ACQUIRED-hardware breakdown: Amazon (§§1–13) $5,712.58 + SendCutSend (§1, orders SQ65E969 + SV07U813) $105.71 + RIGID HVAC direct (§6, DV1910E coil chiller, Lanxi Lizhide) $580.00 + Bambu Lab direct (§15) $4,803.33 + XLaserlab X1 Pro (§16) $3,899.00 + Namecheap homesodamachine.com (§17) $599.00 = $15,699.62. Post-Kamoer audit pass (Apr 24, 2026, two parallel agents over 46 high-impact line items) found 4 confirmed Kamoer-style fold-up errors and corrected them: (a) Kamoer KPHM400 — 3 pumps total @ $32.55 ea = $97.65, was wrongly $99.40 ea × 2 = $198.80; (b) VALVENTO compression 2-pk B0DXZZBK7D and (c) VALVENTO 1/4" tube 5-pk B0F6SYFK48 — both lines wrongly recorded the $31.08 shared order grand total instead of their separate line prices ($12.85 + $18.23 = $31.08), double-counting by $31.08; (d) ANPTGHT silicone B0BM4KQ6RT — actually qty 2 @ $13.93 ea, was qty 1 @ $27.86 (no $ impact since line $ stays at $27.86); (e) VEVOR Workbench B0FCD13KKQ — actually qty 2 @ $172.64 ea, was qty 1 @ $345.28 (no $ impact). Plus cosmetic fixes: Beduan range tightened, findmall .030 → .035, Elitech → Toptes brand. The remaining 42 audited line items verified as MATCH against actual order history.

ON-ORDER breakdown: RIGID DV1910E Copper Coil Chiller from Lanxi Lizhide / "RIGID HVAC" Zhejiang (single PayPal payment $580 = $420 chiller + $160 standard shipping; $0 customs; ChinaPost ZC64524933899 marks delivered LINCOLN NE 2026-04-27 11:26 — awaiting physical confirmation in mailbox; the previous "~$600 + import" placeholder was an over-estimate of memory by ~$20 and the import line was nil) + Amazon orders placed Apr 23, 2026: HVAC 1/4" ACR copper slip coupling 10-pk B0FH549N6D ($7.98) + Knipex 86 01 180 Pliers Wrench B07YLFLSJW ($53.20) + Joywayus 1/4" SAE flare nut 5-pk B0G1XJ2F68 ($7.99) + 3M 425 aluminum foil tape 2" × 180 ft B07BTW7C2N ($88.97) = $158.14 new refrigeration spend. Apr 24, 2026 diagnostic cross-test pair for C14/C13 mating-fit investigation: uxcell C14 inlet B07PXSLBF4 ($7.39, order 112-2063260-0973008) + Tripp Lite P006-006 cord B0000511C0 ($9.21, order 112-2843637-5886607) = $16.60, both delivering Apr 25; cheaper premium-brand references (Schurter, Qualtek) are non-Prime only and were rejected under Prime-only sourcing rule. SendCutSend order SP54G453 ($134.38 delivered, invoice Apr 24, 2026) adds 10× 304 SS 0.048" body half-sheets; parts entered production 2026-04-23, supersedes the body portion of the earlier SQ65E969 + SV07U813 combined runs in BOM §2 (end-cap portion of those orders remains valid). **Apr 24, 2026 carbonator vessel-stock burst — plan-A 316L pivot:** OnlineMetals order 1020857414 (10× 5" OD × 0.065" wall × 6" cut 316 welded SS round tube, MTRs required, $736.73 delivered) + SendCutSend order SG019619 (20× 1/4" 316 SS endcap plates, `endcap-circular-2hole.dxf`, $621.19 delivered) + Tandefio 1/8" × 12" 316 SS rod 5-pk B0CY4DWJFQ ($8.57) = **$1,366.49** vessel raw stock for 10 production units. **Apr 29, 2026 pressure-vessel drill/tap + wood-fixture tooling batch:** Amazon order 112-2348373-7907448, 9 line items, $247.05 pre-tax + $17.91 tax = **$264.96 delivered**, arriving Sat May 2; includes WEN drill press, Drill America tap wrench + 1/4"-18 NPT tap, Brown & Sharpe tap guide, 124 mm hole saw, Baltic birch, MDF, Titebond III, and C-clamps. Plan A vessel cost-per-unit jumps from the earlier 304 placeholder estimate (~$39/vessel) to $135.79/vessel raw stock (tube $73.67 + 2× plates $62.12), reflecting both the 304 → 316L grade upgrade and accurate post-quote pricing. The earlier Airgas nitrogen cylinder plan was dropped — argon purge reuses the existing argon cylinder currently feeding the laser welder, no new gas purchase needed. The foil tape replaces the generic "thermal compound" line in BOM §6 as the tank ↔ coil thermal interface; 180 ft roll covers ~12 builds at ~15 ft/build. The Amazon brazing/refrigeration tools batch placed April 22, 2026 (delivered Apr 23 at $418.70: Supco D111 $11.95, Supco SUD8358 $13.40, Mastercool 70025 $15.74, Bernzomatic TS8000+MAP-Pro $117.96, Harris SSWF7 flux $11.92, Uniweld RHP400 N2 regulator $96.76, RIDGID 31622 cutter $31.99, RIDGID 23332 flare tool $99.99, BCuP-5 rod $18.99) and the soldering/small-signal electrical tools batch (order # 112-0066205-0960237, $423.95 delivered; 17 line items — see §14) both arrived April 23, 2026 and have moved from ON-ORDER → ACQUIRED. **ASSE 1022 backflow preventer — both orders now tracked.** Howdybrewer order #6779764932824 (Apr 16, 2026, $52.52 delivered: 1× Multiplex 19-0897 @ $38.99 + $9.99 ship + $3.54 tax) was placed first and remains ON-ORDER, unshipped 8 days later, prompting the second-source pivot. Midwest Beverage order MB11053 (Apr 24, 2026, $145.80 delivered: 4× Multiplex 19-0897 @ $29.33 = $117.32 + $28.48 UPS Ground + $0.00 tax) was placed as the active production source going forward. Combined backflow-preventer ON-ORDER spend is $198.32 for 5 units of stock. The BOM uses the Midwest allocated unit cost ($145.80/4 = $36.45/unit), dropping BOM §3 from $147.57 → $145.03/unit and the BOM grand total from $1,360.50 → $1,357.96/unit. **GASHER check valve spares — Apr 25, 2026.** After physical inspection of the first pack (order #112-9584993-4999458, ACQUIRED) confirmed PTFE soft-seat construction suitable for production, ordered 2 additional packs (order #112-7934476-0257818, $30.00, arriving Apr 27) as install/test spares + SKU-continuity hedge against same-listing supplier drift on a no-name Amazon brand. Total inventory: 3 packs / 6 valves = 1 unit's production allocation (2 valves) + 4 spares. BOM §3 and §4 unit costs unchanged at $7.50/valve (same SKU, same listing price); per-unit BOM total unaffected.

**2026-04-30 Amazon delivery sweep.** Verified delivery status for every Amazon line that was ON-ORDER in the previous revision; 14 lines moved ON-ORDER → ACQUIRED, 4 of those had their listed prices upgraded from line-price to delivered (post-tax) totals to match ledger convention. Moves (delivered date in parens): STARTECHWELD ER316L MIG wire $129.50 (Apr 27), YTKavq copper bar replacement $42.89 (Apr 24), GASHER check valve spares 2 pk × $15.00 = $30.00 (Apr 27), Westbrass R2031-NL-12 $20.95 (Apr 26 — was delayed at Humble TX, ultimately delivered), Tandefio 316 SS rod $8.57 (Apr 26), JST XH connector experimentation batch (order 112-7245467-6557007 partial) — Waveshare MCP23017 $13.75 + ULN2803A $6.97 + JST 4-pin $8.45 + JST 6-pin $9.19 + JST 9-pin $9.19 + CQRobot bonded ribbon $15.86 = $63.41 (Apr 27 except JST 9-pin Apr 29), 3M Scotch-Brite Hand Pads $28.85 (Apr 29), HVAC 1/4" copper slip coupling $7.98 → **$8.56** delivered (Apr 24), Knipex 86 01 180 Pliers Wrench $53.20 → **$57.06** delivered (Apr 24), Joywayus brass flare nut 5-pk $7.99 → **$8.57** delivered (Apr 27), 3M 425 aluminum foil tape $88.97 → **$95.42** delivered (Apr 26), Pouring Masters mixing cups $20.37 (Apr 29), JMU tongue depressors $7.50 (Apr 29), SUP nitrile gloves XL $7.49 (Apr 29). Net ACQUIRED-hardware delta: **+$529.14**, lifting Amazon (§§1–13) from $5,136.07 → $5,665.21 and combined ACQUIRED hardware from $14,543.11 → $15,072.25. Two new ON-ORDER Amazon lines added during the sweep: Bosch DSB1013 1" × 6" Daredevil Spade Bit B001NGPAA0 ($5.35 delivered, order 111-4630388-1572202, Apr 29, arriving Sat May 2) added to §1 fab tooling, and Eoiips PE tubing 1/16" ID × 1/8" OD B0BWJ3S5NM ($8.03 delivered, order 114-9634716-3126657, Apr 29, arriving Apr 30) added to §7 as soft food-grade liner inside the 1/8" OD SS flanking flavor-tube spouts. Items still ON-ORDER after the sweep: WEN drill press batch 112-2348373-7907448 ($264.96, arriving Sat May 2), Keszoox JST XH 50 cm pre-crimped 22 AWG silicone wires 2-pack subset of 112-7245467-6557007 ($23.26, Amazon shows "arriving today" 2026-04-30 — leave ON-ORDER until physical receipt), plus the new Bosch + Eoiips lines, plus the unchanged non-Amazon ON-ORDER lines (RIGID DV1910E $580 — see Gmail audit below, OnlineMetals tube $736.73, SendCutSend SG019619 endcap plates $621.19, SendCutSend SP54G453 body half-sheets $134.38, Multiplex howdybrewer $52.52, Multiplex midwestbev $145.80). Updated ON-ORDER total: ~$2,572.22 (down from ~$2,995.99).

**2026-04-30 same-day Gmail confirmation + bundled-line dig.** Cross-checked Gmail "Delivered:" notices from `order-update@amazon.com` over the past 5 days against ledger ON-ORDER lines. Two same-day deliveries confirmed Apr 30 (both at 2:03 PM): Eoiips PE tubing 1/16" ID × 1/8" OD ($8.03, order 114-9634716-3126657) and Keszoox JST XH 50 cm pre-crimped wires 2-pack ($23.26, partial of order 112-7245467-6557007). Both moved ON-ORDER → ACQUIRED (+$31.29). The Apr 26–29 Gmail "Delivered:" notices (Chemtronics Soder-Wick, RIDGID 23332 flaring tool, Westbrass R2031-NL-12, 3M 425 foil tape, GASHER check valve spares 2pk, Siptenk brass stiffeners, Joywayus flare nut, ER316L MIG wire, VEVOR Workbench, JST XH connectors batch) all verified as already ACQUIRED in the prior 2026-04-30 sweep. **One bundled-line discovery during the dig:** the Apr 26 Gmail email "Delivered: ChillWaves… and 1 more item" used the Tandefio order # (112-7391312-2980226), but Amazon's order-detail page for that order shows ONLY the Tandefio rod ($8.57 grand total). The ChillWaves was actually a separate order #112-0876134-8491423 (Apr 24, 2026, ChillWaves 304 SS Siamese check valve 1-pack, ASIN B0DPL88RHC, $14.99 + $1.09 tax = $16.08 delivered Apr 26) that Gmail merged into one notice. This was a previously untracked line — added to §4 as a second ChillWaves variant alongside the existing B0DPLBYZB4 split-body unit, since the two are different listings/geometries (Siamese vs split). Net new-line add: **+$16.08**. Combined Apr 30 net effect (Eoiips + Keszoox flip + ChillWaves new line): Amazon (§§1–13) $5,665.21 → $5,712.58, combined ACQUIRED hardware $15,652.25 → $15,699.62, ON-ORDER ~$1,992.22 → ~$1,960.93, grand total ~$20,292.38 → ~$20,308.46. **Audit-trail correction note:** the prior-sweep claim that order #112-0066205-0960237 (soldering tools batch) and order #112-4658706-3333801 (brazing/refrigeration tools batch) "both arrived April 23, 2026" is inaccurate — Amazon's order-detail page shows both orders shipped in multiple sub-shipments delivered Apr 23–26: in the soldering batch, the Hakko station/Kaisi mat/Hakko T18-D12 tip arrived Apr 23, Kester solder Apr 24, BEEYUIHF flux + heat-shrink kit Apr 25, Chemtronics Soder-Wick Apr 26; in the brazing/refrigeration batch, BCuP-5 silver solder arrived Apr 24, Harris SSWF7 brazing flux Apr 25, RIDGID 23332 flaring tool Apr 26. All sub-line items remain correctly ACQUIRED, the only error was the rolled-up "delivered Apr 23" claim — left here as a note since per-line statuses are unaffected.

**2026-04-30 RIGID DV1910E Gmail audit.** Pulled the original Apr 1 order trail to replace the long-standing "~$600 + import" memory placeholder with the actual money out. Vendor is **Lanxi Lizhide Refrigeration Equipment Co., Ltd** (兰溪市立志德制冷设备有限公司, Zhejiang, China) trading as "RIGID HVAC" — a Chinese refrigeration-component supplier, distinct from the US plumbing-tool brand RIDGID; the previous `ridgid.com` link in the ledger was wrong and is corrected to `rigidhvac.com`. Order #2604018778275 (RIGID HVAC site reference) / RG-1264 (their internal SKU). One PayPal payment Apr 1, 2026, **$580.00** total to ann@rigidhvac.com via VISA x5607 (PayPal txn 7T226484A7083323D, statement descriptor PAYPAL *LIZHIDEB7SS): $420 Copper Coil Chiller DV1910E (12 V) + $160 standard shipping. Lydia at RIGID HVAC offered to declare the customs value as USD 200 to minimise duty; either way the shipment was below the US $800 de minimis so import duty was $0. **No second invoice / no second payment** anywhere in Gmail (verified via broad search across `LIZHIDEB7SS`, `ann@rigidhvac`, `lizhide`, `lanxi`, `兰溪`). ChinaPost-handed-to-USPS tracking ZC64524933899 shows the parcel transited Shenzhen → HK → Chicago IL → Omaha NE → Lincoln NE distribution centers and was final-scanned **delivered to LINCOLN, NE 68520 on 2026-04-27 at 11:26 AM** ("已投" / out-for-delivery → delivered). Physical receipt not yet confirmed at user's mailbox as of 2026-04-30 (mailbox check pending). Net effect on totals: ON-ORDER drops by $20 (from the $600 placeholder to the actual $580), grand total drops by $20.

Excluded from totals (price unresolved, still marked "bundle" or "—"): Meshnology ESP32-S3 display, 12 V 2 A DC power supply, Haisstronica ratchet crimper, PGN ER308L 10 lb MIG wire B09WRZDBPN (order placed 2026-04-19 but total not yet posted). Beduan flavor-manifold solenoid counted at $9.64 × 4; actual qty across orders may differ.
