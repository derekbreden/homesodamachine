# Remaining purchases for the first 5, 10 and 20 machines

[`batch-forecast.json`](batch-forecast.json) supplies the inventory-based forecast on [the cost page](https://homesodamachine.com/cost#batch-forecast). Prices and availability are dated October 4, 2026, except where an item notes a later check. Inventory, deliveries and payment states are dated October 13; filament balances run through the prints logged October 13, and quantities follow the current BOM. The columns are alternatives for five, ten or twenty total integrated machines, including unit 1 under development. Each starts with the same stock; the columns are not cumulative.

The forecast subtracts usable on-hand stock and quantities already ordered before calculating new purchases. Existing paid parts, printers, tools, fixtures and reusable filament spools have no new acquisition expense. Each tagged BOM row has a purchase allocation or an explicit exclusion; shared SKUs are combined before supplier lots are rounded. Reed columns use the separately purchased reeds and wires. The printed TPU 85A drain sleeve draws on the TPU seal stock. The printed install guide is inside the packaging allowance. PCB assembly includes on-board components. The build uses a White faucet and both install-kit tees.

## Opening inventory

Filament balances are the approximate balances reported October 4 (12 kg Black PET-GF15, 4 kg Clear PETG and 10 kg Black PETG) less the prints logged since, through October 13, plus the filament delivered since: **about 14.3 kg Black PET-GF15, 12.3 kg Clear PETG and 10 kg Black PETG**. Three 3 kg Black spools arrived October 10 and ten 1 kg Clear refills October 8. Purchase totals are not used as remaining filament balances.

| Prints logged after the October 4 report | Filament | Used |
|---|---|---:|
| [Front top and pump cradle C3](../printed-parts/enclosure/enclosure/magnet-retention/selected-fit-v1/README.md), the [funnel frame](../printed-parts/zone-c/funnel/flush-roof-review/mark2-v1/README.md), two [centered coupon plates](../printed-parts/enclosure/enclosure/magnet-retention/fit-coupons/centered-trial-v4/README.md), two cancelled [support-gap trials](../printed-parts/enclosure/enclosure/support-bottom-gap/README.md), and the ends of the [v17 front top](../printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/README.md) and [v4 pump cradle](../printed-parts/enclosure/enclosure/magnet-retention/v4/physical-result.json) jobs running at the report | Black PET-GF15 | ≈ 1.6 kg |
| Three [reservoir ironing-study plates](../printed-parts/cold-core/reservoir/ironing-study/README.md), the failed [funnel-mold cavity](../printed-parts/zone-c/funnel-mold/native-slice-reviews/2026-10-06-h2c-right-gyroid15/README.md), and the [left reservoir and cap](../printed-parts/cold-core/reservoir/print-log.md) and [cavity retry](../printed-parts/zone-c/funnel-mold/native-slice-reviews/2026-10-06-mark1-retry-z004-v2/README.md) still printing | Clear PETG | ≈ 0.9–1.0 kg |
| Three [back-top trials](../printed-parts/drain-readiness/README.md), the [faucet trials](../printed-parts/faucet/industrial/print-log.md) and [finish coupons](../printed-parts/faucet/finish-coupons/2026-10-10/README.md), the [umbilical organizer](../printed-parts/faucet/umbilical-organizer/README.md) and its [fit trials](../../future/umbilical-organizer-exploration/README.md), the [tube-insertion tool base](../printed-parts/fixtures/tube-insertion/prints/2026-10-11-base-mark1/README.md) and [rigid parts](../printed-parts/fixtures/tube-insertion/prints/2026-10-12-rigid-parts-mark1/README.md), and seam swatch plates: 35 jobs, October 7–13 | Black PET-GF15 | ≈ 5.1 kg |
| The [funnel-mold core](../printed-parts/zone-c/funnel-mold/print-log.md) and the [right reservoir and cap](../printed-parts/cold-core/reservoir/print-log.md), October 7 | Clear PETG | ≈ 0.65 kg |

PET-GF slicer grams use the profile's inherited Bambu PET-CF density of 1.29 g/cm³; at Fiberon's 1.43 g/cm³ the 1,455 g through October 6 is about 1.6 kg and the 4,590 g of October 7–13 is about 5.1 kg. Failed and stopped jobs count their extrusion to the latest possible stop, and jobs still printing count in full; unlogged swatch plates, an estimated 10–40 g, are not counted. The clear-PETG figure through October 6 counts the failed cavity at up to 139 g. No logged print used Black PETG or the White/Blue/Red PET-GF. The TPU jobs of October 8–13 (about 0.1 kg, nearly all TPU 85A) and the three-float ASA Aero print of October 8 (42 g) draw down those provisional credits.

Other stock credits reconcile [purchases.md](purchases.md), [inventory.md](inventory.md) and applicable physical records. Each JSON row carries on-hand quantity, incoming quantity, source locations and a stock-basis note. Acquired pack counts and usable remainders generally lack a current stocktake, so their credits are estimates marked `*`. The website displays those quantities alongside each shortfall.

- Ten batch-2 assembled PCBAs are credited, including the reusable bench board, subject to normal acceptance. The ten batch-1 boards receive no production credit: [the bench log](../pcb/pcba/bench-log.md) records missing vias and rules out rework.
- Ten 6-inch carbonator tube cuts and twenty current 316 endcaps are credited provisionally. The 304 plan-B blanks are excluded. Twenty-three plates from the later under-counter-plate order are credited; current drawing compatibility and remaining quantity are estimated.
- Five 19-0897 backflow preventers, fourteen specified solenoids, six GASHER checks, twenty PP1208E bulkheads, forty PP0308E elbows and other same-part receipts contribute stock credits. Ten PP010822E connectors are credited from the May 15 order confirmation that names their bag. One of the six acquired TAISHER elbows is reserved for the destructive jet coupon.
- Approximate remaining White/Blue/Red PET-GF credits are 0.8/0.9/0.9 kg. White ASA Aero is credited provisionally at 0.96 kg: one of the two spools acquired in April, less the October 8 float print, with the other reserved for development; two more spools are in transit. The TPU 90A/85A seal and sleeve stock is credited at a provisional 0.4 kg. These balances are unmeasured estimates.
- FWS order WEBFWS100711469, delivered October 9, credits ten ABU44M-E bulkheads and eleven 8 ft cuts of white 4 mm LLDPE: four 25 ft lengths yield twelve, less a one-build reserve for the drain fit trials. Nine of the ten delivered ARD4M4-E reducers are credited after a provisional one-piece development reserve; the current flavor path uses two per machine. The AEU44-E elbows and ATBC44-E barbs of WEBFWS100711471 receive no credit. Nor do the thirty neoFit AFA4-N2-G adapters of WEBFWS100708929, which are not the BOM's PI450822S.
- Cut stock and non-filament consumables use a visible provisional one-machine consumption reserve against acquired quantities. This is a budgeting assumption, not a claim about measured development usage. Continued development consumption can increase the orders.
- Terminal, ferrule and heat-shrink assortments without usable counts by required size receive no aggregate numerical credit. Two exact-width 100-piece Baomain female-disconnect packs are credited provisionally. The five-colour 16 AWG kit is credited as one kit; remaining colour allocation is unverified.
- The one acquired water filter has unrecorded remaining service life and customer-unit availability; a fresh filter is budgeted for each machine. Finished printed parts without a counted current usable balance receive no additional material credit.

These records establish a traceable estimate, not an assertion that all historical purchases are still available or qualified. Physical acceptance keeps its recorded scope.

## Already-ordered components and payment reserve

Already-ordered quantities are separate from on hand and are deducted to prevent duplicate orders:

| Component | Received credit | Incoming credit | State at October 13 |
|---|---:|---:|---|
| Kamoer KPHM600-SW3B17 pump | 2 | 5 | Ordered October 11 (Amazon 114-5708094-2581869); $212.45 charged October 12; arriving October 13. |
| Beduan 12 V solenoid valve | 14 | 10 | Ordered October 11 (Amazon 114-5870152-3334654); $96.40 charged October 12; arriving October 13. |
| ASA Aero White 46100 | 0.96 kg | 2 kg | Ordered and paid October 8 (Bambu us784775952755326977, $107.23); shipped October 9, in transit. |

Delivered orders are counted on hand: three WR1105 regulators (October 7), thirty PI450822S adapters (October 5), the Taprite 3741 (October 7), ten Clear PETG refills (October 8) and the FWS drain-line parts (October 9).

All three alternatives include a **$94.54 possible-payment reserve** for the PI450822S order: its account order page link has expired and Gmail holds no payment record. Confirmed charges for the WR1105, Taprite 3741, PET-GF15 Black, Clear PETG, ASA Aero, Kamoer, Beduan and FWS drain-line orders are excluded. This is a conservative allowance for a possible remaining balance, not a verified amount owed. Release it when those orders are confirmed paid. Tax is not added again to these delivered order amounts.

Delivery is required before assembly. A delayed order is not physically available stock, and an acquired status alone does not prove payment.

## Supplier quantities

The lot calculation minimizes new purchase cash among the sourced options. It can buy more than the net shortfall when a bag or discounted tier costs less. A lower unit price does not justify an expensive case of unneeded stock. The JSON supplies the exact purchase options, units, per-machine requirements, price basis, inventory credits and uncertainty notes; the website calculates and displays all three order lists.

- Black PET-GF material is planned at 6.02 kg per machine, rounded from the 6.0165 kg BOM colour split, plus a provisional 15% allowance for supports, purge and rejects. After the 14.3 kg stock credit, new orders are **seven 3 kg spools for five machines**, **eighteen 3 kg spools plus one 1 kg spool for ten** and **forty-one 3 kg spools plus two 1 kg spools for twenty**. The ten-machine mix buys 55 kg for $1,379.81, less than nineteen 3 kg spools at $1,424.81. The October 7 order paid a $59.99 sale price per 3 kg spool; the forecast keeps the October 4 Prime listing of $74.99.
- White PET-GF is planned at 0.1425 kg per machine: the white faucet, the two white ring-and-collar stations and half the nameplate. After its 0.8 kg credit it needs one 1 kg spool for five or ten machines and three for twenty. Blue and Red are covered by their credits.
- Clear PETG needs **no new refills for five or ten machines and ten for twenty**, after its 12.3 kg balance. The manufacturer tier is calculated from the replenishment order: nine refills cover the shortfall, but ten at the 10-roll tier cost less. Existing 10 kg Black PETG covers all three alternatives without a new refill order.
- A 50 ft copper coil yields three complete 15.92 ft evaporator cuts. The provisional remaining two usable cuts reduce new coil orders to one / three / six for five / ten / twenty machines. Offcuts cannot be joined to make another evaporator.
- Reservoir rod blanks use one 12-inch rod each; two carbonator blanks share a rod. The selected 316 five-pack is rounded after the usable-equivalent stock allowance. Shorter or different-diameter rods are not assumed interchangeable.
- Soda umbilicals use one 24-inch and five 12-inch insulation cuts per machine. Each six-foot roll is cut into those discrete lengths; the provisional five-foot stock credit reduces new orders to five / eleven / twenty-three rolls for five / ten / twenty machines.
- The 4 mm drain tube is bought in 25 ft lengths, three 8 ft drain cuts each; 5 ft lengths cannot supply the continuous 1,871 mm faucet drain. The eleven credited cuts cover five and ten machines; twenty buy three lengths.
- Red gas tubing includes the external tether and three internal segments, about two feet total per machine. A provisional 25% cut/slack reserve is applied before crediting the acquired red tubing. It covers all three batches without a new order.
- Each silicone funnel uses a provisional 273 g mixed-material allowance. Kits contain approximately 1,098 g. Stock and process yield remain estimates.
- Ribbon cable is purchased by conductor count. The provisional two/three/five gross 16 AWG colour kits for five/ten/twenty machines become one/two/four new kits after the existing kit credit. Terminal and ferrule refills use conservative size-specific allowances while the width/gauge map remains open.
- The acquired reusable bath container serves any batch. Fluids, welding wire, pigment, mold release, foam and refrigerant use explicitly provisional remaining quantities and production yields, rounded to whole containers only when replenishment is required.

Amazon prices come from signed-in Prime-filtered results; conditional coupons and multi-item promotions are not deducted. Other suppliers use their current catalog or marked historical delivered allowances. Supplier availability is a dated observation, not a reservation of the full order.

## Supply and quote limits

Bambu ASA Aero White 46100 is listed and orderable on October 13. The float-feed requirements are approximately 0.243 / 0.485 / 0.971 kg for five / ten / twenty machines including the 15% allowance. The provisional 0.96 kg on hand covers five and ten machines, and the two spools in transit cover twenty, so no replenishment is budgeted. No interchangeable foaming filament is assumed.

Ten relief valves are listed; after one credited valve, the twenty-machine plan needs nineteen new valves and exceeds listed stock by nine. The ten credited silicone washers reduce the twenty-machine requirement to three new ten-packs, within the observed stock. The candidate R2031-NL-62 faucet has twelve listed; nineteen new faucets for twenty machines exceed that by seven. Its $52.40 price is an allowance pending confirmation of the handle/body interfaces against the accepted A2031-NL-62.

Exact Prime replenishment sources remain unconfirmed for several plumbing/refrigeration items, the flow meter and short M3 inserts; positive delivered allowances cover their shortfalls. The donor ice maker's current listing names a different suffix, so internal compatibility is unconfirmed.

The exact PP1208E bulkhead union is sourced from Fresh Water Systems, and the exact 1.47-inch display from Waveshare. These are same-part supplier substitutions. Mouser pricing and batch stock remain estimates. Additional JLCPCB assembly, OnlineMetals cuts and SendCutSend parts require current quantity-specific quotes; historical delivered lots supply the allowances. No unquoted volume saving is assumed.

Some electrical terminations remain open. Positive allowances cover them without asserting a selected procedure or physical acceptance.

## Expense basis

New parts/materials, new inbound freight/import reserves and tax form the delivered replenishment budget. A supplier with no new purchase incurs no new freight. The 7.25% tax reserve, drawn from recorded orders, applies only to merchandise-priced purchases and new inbound reserves; historical delivered allowances are not taxed twice.

The headline additional-cash budget adds the possible pending-payment reserve, $40 per machine for cartons/protective packing/customer guides, $80 per machine for customer delivery and $125 / $200 / $350 per five / ten / twenty-machine batch for shop gases, auxiliary solder/cleaning supplies and production electricity. Packing and delivery are unquoted estimates. Shop allowances use a provisional $50 per batch plus $15 per machine and cover additional usage beyond the explicitly credited BOM supplies; remaining gas and electricity usage are unmeasured.

Build labor uses the labor ledger's deliberately ideal estimate of Derek's time and its rate, shown separately; it is not a cash payment. Prior development time is excluded. Early-build labor and attended work already completed on unit 1 are not fully quantified, so the labor line is a forward planning allowance rather than an actual unpaid-hours balance. Extra tooling, rent, payment fees, installation, warranty/support and business taxes are outside this forecast.

New excess-stock value uses average new purchase cost before freight/tax. Existing inventory is not assigned a second purchase cost. The per-row stock left after a batch includes both existing and newly acquired remainder; colour, size and offcut constraints can prevent it from supplying another whole machine.

The stored BOM digest marks the public forecast for review if the BOM changes. Refresh opening balances, pending delivery/payment states, prices, lot options, quotes and BOM coverage together. The forecast is not a submitted supplier order.

The October 21 flavor allocation uses continuous black 4 mm tubing, two ARD4M4-E reducers and three ABU44M-E fittings including OVER. PP1208E allocation is two, for SODA and TAP; no PP0408W or white quarter-inch faucet-flavor stock is required. Black 4 mm purchases reserve 18 ft per machine in whole-length allocations. These quantity changes do not refresh the other dated stock estimates or price observations. [Unit 1](unit-1-shopping.md) has the current single-machine purchase links and recent receipt credits.
