# Inventory

Current-state inventory for items not in [bom.md](/hardware/ledger/bom.md) and not in [tools.md](/hardware/ledger/tools.md). Aggregated counts across multiple [purchases.md](/hardware/ledger/purchases.md) rows where relevant, with the underlying purchase events left on the ledger as-is.

This is a **view** over purchases.md: each entry below points back to its row(s) in the ledger for the buy details (date, vendor, $). The unique value here is *current state* — what category an item falls in now, aggregated on-hand counts across reorders, and the reason something is in this file rather than in bom.md or tools.md.

Categories:
- **[Abandoned](#abandoned)** — purchased and on-hand, but no longer in the current production design. Kept as spare / bench-test stock or because removal isn't cost-effective.
- **[Spare](#spare)** — deliberate extra of a currently-used BOM item. Hedge against supplier drift, install/test consumption, or unit-002 head start.
- **[Diagnostic](#diagnostic)** — bought for a specific test / investigation, not production.
- **[Donor](#donor)** — harvest sources. Disassembled for specific subassemblies; remainder discarded or kept as spare.
- **[Fab fixture](#fab-fixture)** — one-time fabrication-support stock (wood, MDF, glue, clamps) used to build jigs and templates rather than appliance parts.
- **[Consumable (non-per-unit)](#consumable-non-per-unit)** — used during fabrication but not allocated per-unit in bom.md (welding practice stock, recurring gas fills, bench reference materials).
- **[Prototype / test-bench](#prototype--test-bench)** — items used on the running prototype or test bench but not in the shipped BOM. Customer-supplied counterparts in production.

---

## Abandoned

Items purchased and on-hand whose original role has been superseded by a different design decision. Kept as spare / bench-test stock; not in current production path.

| Item | Source | Why abandoned |
|---|---|---|
| **Pysrych 304 SS reducing compression union, 1/4" × 1/8" OD (2-pack)** | [B0BM4394Z4](https://www.amazon.com/dp/B0BM4394Z4), [purchases.md §7](/hardware/ledger/purchases.md) | Originally joined 1/4" LLDPE supply to 1/8" SS spout tube. Spout-tube design replaced by LLDPE-end-to-end through the printed PET-CF gooseneck — no SS-tube transition needed. |
| **Eoiips PE tubing 1/16" ID × 1/8" OD (1 m)** | [B0BWJ3S5NM](https://www.amazon.com/dp/B0BWJ3S5NM), [purchases.md §7](/hardware/ledger/purchases.md) | Soft food-grade liner inside the 1/8" SS flanking flavor-tube spouts. Same supersession as Pysrych — no SS spout. |
| **Beduan 304 SS compression ferrule sleeve, 1/4" OD (5-pk)** | [B07V4K2KKH](https://www.amazon.com/dp/B07V4K2KKH), [purchases.md §7](/hardware/ledger/purchases.md) | Decorative ferrules for dispense-spout tips on the rejected SS-tube spout design. |
| **Beduan 304 SS compression ferrule sleeve, 1/8" OD** | [B07V8RJJYJ](https://www.amazon.com/dp/B07V8RJJYJ), [purchases.md §7](/hardware/ledger/purchases.md) | Same — decorative ferrules for the rejected SS-tube spout. |
| **1/4" OD × 12" 304 SS center spout tube (4 pc)** | [B0F87DJDZW](https://www.amazon.com/dp/B0F87DJDZW), [purchases.md §7](/hardware/ledger/purchases.md) | Carbonated-water center tube on the rejected SS-tube spout. |
| **1/8" OD × 12" 304 SS flanking spout tubes (4 pc)** | [B0F87V8XCB](https://www.amazon.com/dp/B0F87V8XCB), [purchases.md §7](/hardware/ledger/purchases.md) | Flanking flavor tubes on the rejected SS-tube spout. |
| **Hooshing 3/8" flare × 1/4" FNPT brass adapter (2 pk)** | [B0BNHVV6HT](https://www.amazon.com/dp/B0BNHVV6HT), [purchases.md §3](/hardware/ledger/purchases.md) | Was Multiplex MFL outlet adapter; the 1/4" FNPT downsized the SeaFlo suction side and hurt NPSH. Replaced by brewhardware FFL38BARB38 single-piece 3/8". |
| **Control Devices SV-100 safety valve, 100 PSI** | [B0D361X97X](https://www.amazon.com/dp/B0D361X97X), [purchases.md §2](/hardware/ledger/purchases.md) | Production PRV is now SV-125 at 125 PSI (35 PSI margin to the 90 PSI working setpoint). SV-100 retained as spare / bench-fixture PRV. |
| **Beduan 1/4" male spiral-cone atomization nozzle, 316 SS** | [B07LGPD3GB](https://www.amazon.com/dp/B07LGPD3GB), [purchases.md §4](/hardware/ledger/purchases.md) | Required high ΔP to atomize; at our working ΔP it produces a stream not a spray. Replaced by internal sparge stone architecture. |
| **VALVENTO 1/4" OD 316 SS tube, 12" (5-pk)** | [B0F6SYFK48](https://www.amazon.com/dp/B0F6SYFK48), [purchases.md §4](/hardware/ledger/purchases.md) | Bottom-plate-to-faucet rigid tube stub; replaced by LLDPE-direct path through printed PET-CF faucet. |
| **Tynulox 1/8" × 6" 304 SS round rod (10 pk)** | [B0BKGS32KJ](https://www.amazon.com/dp/B0BKGS32KJ), [purchases.md §9](/hardware/ledger/purchases.md) | Internal float rod, 304 grade. Replaced by Tandefio 316 SS rod (B0CY4DWJFQ) to keep all wetted parts at 316/316L. Retained for non-wetted subassemblies. |
| **Comfy Materials PETG-Carbon, 1.75 mm × 1 kg Gray (×2)** | [B0BTLNK74C](https://www.amazon.com/dp/B0BTLNK74C), [purchases.md §13](/hardware/ledger/purchases.md) | Original reservoir filament. Replaced by SunTop food-contact-compliant PETG (B0FP34MJ94) — the SunTop has the explicit FDA 21 CFR 177.1630 compliance. |
| **1/4" NPT female weld bung, 304 SS stepped flange** | [B07QNV8796](https://www.amazon.com/dp/B07QNV8796), [purchases.md §1](/hardware/ledger/purchases.md) | Direct-tap into 1/4"-thick end plates removed the need for weld-in bungs. |
| **SendCutSend SQ65E969 — 304 SS 0.048" body blanks (×2)** | sendcutsend.com, [purchases.md §1](/hardware/ledger/purchases.md) | OLD plan-B single-sheet plan. Superseded by half-sheet plan (SP54G453) and then by plan-A round-tube vessel. Held as spare / practice stock. |
| **SendCutSend SV07U813 — 304 SS 0.060" racetrack end-cap blanks (×4)** | sendcutsend.com, [purchases.md §1](/hardware/ledger/purchases.md) | Plan-B end-cap stock. Plan A 316L round-tube path is current. |
| **SendCutSend SP54G453 — 304 SS 0.048" body half-sheets (×10)** | sendcutsend.com, [purchases.md §1](/hardware/ledger/purchases.md) | Plan-B body half-sheets. Plan A is the current carbonator path. |
| **Fotek SSR-25DA solid-state relay** | [B08FR13GYR](https://www.amazon.com/dp/B08FR13GYR), [purchases.md §9](/hardware/ledger/purchases.md) | Surplus — overspecced for the load. Teyleten 3.3 V opto-isolated relay drives the compressor. |
| **Inline AC fuse holder kit, 5×20 mm + assorted fuses** | [B07BC8DW3L](https://www.amazon.com/dp/B07BC8DW3L), [purchases.md §9](/hardware/ledger/purchases.md) | Surplus — bench-test gear; 5 A fast-blow would nuisance-trip compressor inrush. |
| **Leviton CR020-W 20 A 125 VAC single receptacle** | [B003ATTR8Y](https://www.amazon.com/dp/B003ATTR8Y), [purchases.md §9](/hardware/ledger/purchases.md) | Surplus — wrongly spec'd as AC inlet; a female outlet isn't an inlet. C14 panel-mount inlet is the production AC inlet. |
| **Drill America HSS pipe tap + die kit** | [B0DXN1LDKT](https://www.amazon.com/dp/B0DXN1LDKT), [purchases.md §1](/hardware/ledger/purchases.md) | Die used for thread chasing on test fittings; HSS tap is backup. Production tap is LingGan M35 cobalt. |
| **Drill America DWT64006 HSS pipe tap** | [B01DZD1Y9Y](https://www.amazon.com/dp/B01DZD1Y9Y), [purchases.md §1](/hardware/ledger/purchases.md) | Backup tap. Same supersession as above. |
| **Mean Well LRS-200-12 PSU (204 W / 12 V / 17 A)** | [B0874XQ82F](https://www.amazon.com/dp/B0874XQ82F), [purchases.md §9](/hardware/ledger/purchases.md) | Bench-evaluation alternate to IRM-90-12ST. Production 12 V rail is the IRM-90-12ST. |

## Spare

Deliberate extras of currently-used BOM items.

| Item | On-hand | Notes |
|---|---|---|
| **GASHER 1/4" NPT SS check valve, PTFE soft-seat** | 3 packs / 6 valves total ([B0FV2D2FFX](https://www.amazon.com/dp/B0FV2D2FFX), [purchases.md §4](/hardware/ledger/purchases.md)) | 2 valves per build × 1 unit + 4 spares. SKU-continuity hedge against same-listing supplier drift. |
| **TAISHER 316L SS 1/4" NPT 90° street elbow (M×F)** | 2 packs / 4 elbows ([B0CZ38MYL1](https://www.amazon.com/dp/B0CZ38MYL1), [purchases.md §4](/hardware/ledger/purchases.md)) | 4 elbows per build × 1 unit = exact 1-build allocation. No spares above per-unit need. |
| **Multiplex 19-0897 ASSE 1022 backflow preventer (howdybrewer single-unit)** | 1 ([howdybrewer.com](https://www.howdybrewer.com/products/multiplex-backflow-preventor-assembly-1022-3-8-npt-x-3-8-mfl), [purchases.md §3](/hardware/ledger/purchases.md)) | First-source order that stalled 8 days unshipped, prompting Midwest Beverage second source. Held as install/test spare alongside the 4-pack from Midwest. |
| **ChillWaves 304 SS Siamese check valve (1-pack)** | 1 ([B0DPL88RHC](https://www.amazon.com/dp/B0DPL88RHC), [purchases.md §4](/hardware/ledger/purchases.md)) | Second ChillWaves variant evaluated alongside the split-body B0DPLBYZB4; held as spare / bench-test alternative to the production GASHER. |

## Diagnostic

Bought specifically for a test or investigation, not for production use.

| Item | Source | Test purpose |
|---|---|---|
| **uxcell C14 panel-mount inlet** | [B07PXSLBF4](https://www.amazon.com/dp/B07PXSLBF4), [purchases.md §9](/hardware/ledger/purchases.md) | C13/C14 mating-fit investigation — different-brand reference against MXR inlet to isolate inlet- vs. cord-side contribution to the IEC 60320 gap. |
| **Tripp Lite P006-006 NEMA 5-15P → C13 cord** | [B0000511C0](https://www.amazon.com/dp/B0000511C0), [purchases.md §9](/hardware/ledger/purchases.md) | Same investigation — reference-class cord against Monoprice to isolate cord-side contribution. |
| **VUYOMUA 0.8 gal SS portable air tank** | [B0BV6FMMJP](https://www.amazon.com/dp/B0BV6FMMJP), [purchases.md §2](/hardware/ledger/purchases.md) | Bench test fixture for pressure-testing fittings outside of a real vessel. |

## Donor

Harvest sources. Disassembled for specific subassemblies; remainder discarded or kept as spare stock.

| Donor | Source | Harvested for |
|---|---|---|
| **Frigidaire EFIC117-SS ice maker** | [B07PCZKG94](https://www.amazon.com/dp/B07PCZKG94), [purchases.md §6](/hardware/ledger/purchases.md) | Compressor, condenser + fan, capillary tube, factory drier. R-600a charge mass: 23 g per donor manual. See [reference/ice-maker/README.md](/hardware/reference/ice-maker/README.md). |
| **Generic 8-cube ice maker, 26 lb/day** | [B0F42MT8JX](https://www.amazon.com/dp/B0F42MT8JX), [purchases.md §6](/hardware/ledger/purchases.md) | Same harvest scope. R-600a charge mass: 15 g per donor manual. |
| **Westbrass R2031-NL-12 Touch-Flo faucet, oil-rubbed bronze** | [B01N5LVNQA](https://www.amazon.com/dp/B01N5LVNQA), [purchases.md §7](/hardware/ledger/purchases.md) | Valve body harvest for the printed PET-CF gooseneck. See [reference/touch-flo-faucet/README.md](/hardware/reference/touch-flo-faucet/README.md). |
| **Westbrass A2031-NL-62 8" Touch-Flo faucet (already owned)** | [B0BXFW1J38](https://www.amazon.com/dp/B0BXFW1J38), [purchases.md §7](/hardware/ledger/purchases.md) | Not a harvest donor; pre-existing stock. R2031-NL-12 pattern is the chosen donor. |
| **Westbrass D203-NL-62 6" Touch-Flo faucet (already owned)** | [B01MZ6JPXW](https://www.amazon.com/dp/B01MZ6JPXW), [purchases.md §7](/hardware/ledger/purchases.md) | Same — pre-existing stock, not a harvest donor. |
| **DEVMO MINI vertical float switch** | [B07T18PGJ4](https://www.amazon.com/dp/B07T18PGJ4), [purchases.md §9](/hardware/ledger/purchases.md) | Magnetic donut float harvested; switch body discarded. Float slides on the welded 316L SS rod inside the carbonator vessel. |
| **Lillium under-counter carbonator** | Liliumfaucet order 1566, [purchases.md §2](/hardware/ledger/purchases.md) | Current prototype cold-carbonated water source. Replaced by the integrated cold core in the production design. |

## Fab fixture

One-time fabrication-support stock used to build jigs, templates, and bench fixtures.

| Item | Source | Use |
|---|---|---|
| **Baltic birch plywood, 12 mm 8" × 8" (2 pc)** | [B0DP8597Q2](https://www.amazon.com/dp/B0DP8597Q2), [purchases.md §1](/hardware/ledger/purchases.md) | Stiff fixture stock for the end-cap drilling/tapping jig. |
| **ACXFOND 1/4" MDF boards, 8" × 10" (20 pk)** | [B0F1FJYDQ3](https://www.amazon.com/dp/B0F1FJYDQ3), [purchases.md §1](/hardware/ledger/purchases.md) | Sacrificial drill-press backers + template stock. |
| **Titebond III wood glue, 4 oz** | [B0002YQ378](https://www.amazon.com/dp/B0002YQ378), [purchases.md §1](/hardware/ledger/purchases.md) | Glue-up for laminated wood fixture stock. |
| **Storystore 4" steel C-clamps (4 pk)** | [B0DHX78G97](https://www.amazon.com/dp/B0DHX78G97), [purchases.md §1](/hardware/ledger/purchases.md) | Clamps fixture glue-ups and small workpieces at the drill press. |
| **4pc 1/4" NPT male hex nipple, 316 SS** | [B0GD1QBLQ3](https://www.amazon.com/dp/B0GD1QBLQ3), [purchases.md §1](/hardware/ledger/purchases.md) | Test fittings for hand-tap verification on practice plates. |

## Consumable (non-per-unit)

Used during fabrication but not allocated per-unit in bom.md. Welding practice stock, recurring gas fills, bench reference materials.

| Item | Source | Use |
|---|---|---|
| **Airgas argon fill, 85 SCF (CY-AR 80)** | Airgas #8162013342, [purchases.md §1](/hardware/ledger/purchases.md) | Recurring fill for the argon cylinder. Consumed across welding + braze-purge sessions. |
| **Airgas CO2 fill (prototype cylinder), 5 lb** | Airgas #8160436286, [purchases.md §2](/hardware/ledger/purchases.md) | Recurring fill for the prototype's running CO2 cylinder. |
| **Airgas CO2 fill (testing cylinder), 5 lb** | Airgas #8162013342, [purchases.md §2](/hardware/ledger/purchases.md) | Recurring fill for the test-bench CO2 cylinder. |
| **Blue Demon ER308L .030 MIG wire, 2 lb** | [B0025Q2HIU](https://www.amazon.com/dp/B0025Q2HIU), [purchases.md §1](/hardware/ledger/purchases.md) | Welding practice on 304 SS coupons. Production filler is ER316L. |
| **findmall ER308L .035 MIG wire, 10 lb spool** | [B0C52XQB39](https://www.amazon.com/dp/B0C52XQB39), [purchases.md §1](/hardware/ledger/purchases.md) | Larger ER308L spool for extended welding practice. || **304 SS 1/16" practice coupons (3 pk)** | [B0DFXXQZD3](https://www.amazon.com/dp/B0DFXXQZD3), [purchases.md §1](/hardware/ledger/purchases.md) | Welding practice; matches end-cap thickness. |
| **304 SS 0.04" practice coupons (4 pc)** | [B0C5LWVLCD](https://www.amazon.com/dp/B0C5LWVLCD), [purchases.md §1](/hardware/ledger/purchases.md) | Welding practice; matches body thickness. |
| **ESCO Institute EPA Section 608 Preparatory Manual** | [1930044607](https://www.amazon.com/dp/1930044607), [purchases.md §6](/hardware/ledger/purchases.md) | General refrigeration reference. Section 608 cert not required for R-600a (natural-refrigerant carveout). |
| **Hgnova 1064 nm laser protective lens (15 pc)** | [B0FF38DY1Z](https://www.amazon.com/dp/B0FF38DY1Z), [purchases.md §1](/hardware/ledger/purchases.md) | Replacement protective windows for the X1 Pro welding head; consumable after splatter/contamination. |
| **3M Scotch-Brite Maroon hand pads (20 pk)** | [B07CGPCTHT](https://www.amazon.com/dp/B07CGPCTHT), [purchases.md §6](/hardware/ledger/purchases.md) | Cleaning 1/4" ACR copper OD + fitting sockets prior to braze. |
| **Shineboc wet/dry sanding sponge set (20 pc)** | [B0D8ZC6HKY](https://www.amazon.com/dp/B0D8ZC6HKY), [purchases.md §13](/hardware/ledger/purchases.md) | Foam-backed silicon-carbide; post-print finishing of PET-CF parts at the support-contact zones. |

## Prototype / test-bench

Items used on the running prototype or test bench but not in the shipped BOM. The shipped appliance expects the customer to supply these (CO2 cylinder) or has them embedded differently (the customer's tap water rather than a filtered prototype source).

| Item | Source | Role |
|---|---|---|
| **TAPRITE E-T742 CO2 primary regulator (CGA-320)** | [B00L38DRD0](https://www.amazon.com/dp/B00L38DRD0), [purchases.md §2](/hardware/ledger/purchases.md) | Prototype's primary regulator. Shipped units carry the Wellbom CGA-320 primary (bom.md §4); the in-appliance WR1110 secondary handles setpoint normalization. |
| **Airgas prototype CO2 cylinder, 5 lb aluminum food-grade CGA-320** | Airgas #8160436286, [purchases.md §2](/hardware/ledger/purchases.md) | Prototype's operational cylinder, in service feeding the prototype's dispense. |
| **Airgas testing CO2 cylinder, 5 lb aluminum food-grade CGA-320** | Airgas #8162013342, [purchases.md §2](/hardware/ledger/purchases.md) | Test-bench cylinder; vessel carbonation experiments, sparge/saturation tests. |
| **HAOCHEN brass angle stop add-a-tee, 3/8"×3/8"×1/4"** | [B0DLKHHGL6](https://www.amazon.com/dp/B0DLKHHGL6), [purchases.md §3](/hardware/ledger/purchases.md) | Used as the prototype tap-water source adapter; also committed as **install-kit tee scenario B (older home)** in [`bom.md §3`](/hardware/ledger/bom.md). For older kitchens with a 3/8" angle stop and a braided compression supply line to the faucet, this tee threads between the angle stop and its existing line, exposing a 1/4" compression outlet for the appliance's LLDPE. The matching scenario A tee for modern 1/4"-LLDPE-already-under-sink homes is the JG PP0208E (black, FWS-sourced) — see `bom.md §3`. |
| **SAMSUNG HAF-QIN-3P fridge filter (3-pk)** | [B09HR7H8X7](https://www.amazon.com/dp/B09HR7H8X7), [purchases.md §3](/hardware/ledger/purchases.md) | Prototype-specific filter; production inline filter is the Waterdrop 15UC-UF in bom.md. |
| **SodaStream Diet Mountain Dew concentrate + 4-packs (various)** | various ASINs, [purchases.md §5](/hardware/ledger/purchases.md) | Flavor concentrate stock for prototype dispense and bench tests. Customer-supplied in production. |

## Open items

- **Per-row audit pass.** This file's current contents are the explicitly-marked superseded / spare / surplus / abandoned rows from purchases.md plus the items we discussed during the 2026-05-20 partition. A full per-row audit of every purchases.md line — categorizing each as BOM / TOOL / INVENTORY — hasn't been done. Items not yet in this file may need to land here over time.
- **Pysrych decision.** Pysrych compression unions are listed here as abandoned. If the design changes (or a diagnostic/bench-test use surfaces), revisit — the row in purchases.md itself stays as-is regardless of design churn.
- **Lifevant / Yetaha / Mean Well alt PSU.** These are unclear-state items (could be BOM, could be inventory) flagged for future categorization.
