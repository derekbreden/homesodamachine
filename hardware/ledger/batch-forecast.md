# Remaining purchases for the first 5, 10 and 20 machines

[`batch-forecast.json`](batch-forecast.json) supplies the inventory-based forecast on [the cost page](https://homesodamachine.com/cost#batch-forecast). Prices, availability and parts inventory are dated October 4, 2026; filament balances run through the prints logged October 6, and quantities follow the October 7 BOM. The columns are alternatives for five, ten or twenty total integrated machines, including unit 1 under development. Each starts with the same stock; the columns are not cumulative.

The forecast subtracts usable on-hand stock and quantities already ordered before calculating new purchases. Existing paid parts, printers, tools, fixtures and reusable filament spools have no new acquisition expense. Each tagged BOM row has a purchase allocation or an explicit exclusion; shared SKUs are combined before supplier lots are rounded. Reed columns use the separately purchased reeds and wires. PCB assembly includes on-board components. The build uses a White faucet and both install-kit tees.

## Opening inventory

Filament balances are the approximate balances reported October 4 (12 kg Black PET-GF15, 4 kg Clear PETG and 10 kg Black PETG) less the prints logged since, through October 6: **about 10.4 kg Black PET-GF15, 3 kg Clear PETG and 10 kg Black PETG**. Purchase totals are not used as remaining filament balances.

| Prints logged after the October 4 report | Filament | Used |
|---|---|---:|
| [Front top and pump cradle C3](../printed-parts/enclosure/enclosure/magnet-retention/selected-fit-v1/README.md), the [funnel frame](../printed-parts/zone-c/funnel/flush-roof-review/mark2-v1/README.md), two [centered coupon plates](../printed-parts/enclosure/enclosure/magnet-retention/fit-coupons/centered-trial-v4/README.md), two cancelled [support-gap trials](../printed-parts/enclosure/enclosure/support-bottom-gap/README.md), and the ends of the [v17 front top](../printed-parts/enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-03-enclosure-front-top-current-h2c-v17/README.md) and [v4 pump cartridge](../printed-parts/enclosure/enclosure/magnet-retention/v4/physical-result.json) jobs running at the report | Black PET-GF15 | ≈ 1.6 kg |
| Three [reservoir ironing-study plates](../printed-parts/cold-core/reservoir/ironing-study/README.md), the failed [funnel-mold cavity](../printed-parts/zone-c/funnel-mold/native-slice-reviews/2026-10-06-h2c-right-gyroid15/README.md), and the [left reservoir and cap](../printed-parts/cold-core/reservoir/print-log.md) and [cavity retry](../printed-parts/zone-c/funnel-mold/native-slice-reviews/2026-10-06-mark1-retry-z004-v2/README.md) still printing | Clear PETG | ≈ 0.9–1.0 kg |

The PET-GF jobs report 1,455 g because their slicer profile inherits Bambu PET-CF's 1.29 g/cm³; at Fiberon's 1.43 g/cm³ that filament is about 1.6 kg. The clear-PETG figure counts the two running jobs in full and the failed cavity at up to 139 g. The loaded clear spools read about 3.5 kg on October 6 with about 0.5 kg of those jobs still to print. No logged print used Black PETG or the White/Blue/Red PET-GF, TPU or ASA Aero stock.

Other stock credits reconcile [purchases.md](purchases.md), [inventory.md](inventory.md) and applicable physical records. Each JSON row carries on-hand quantity, incoming quantity, source locations and a stock-basis note. Acquired pack counts and usable remainders generally lack a current stocktake, so their credits are estimates marked `*`. The website displays those quantities alongside each shortfall.

- Ten batch-2 assembled PCBAs are credited, including the reusable bench board, subject to normal acceptance. The ten batch-1 boards receive no production credit: [the bench log](../pcb/pcba/bench-log.md) records missing vias and rules out rework.
- Ten 6-inch carbonator tube cuts and twenty current 316 endcaps are credited provisionally. The 304 plan-B blanks are excluded. Twenty-three plates from the later under-counter-plate order are credited; current drawing compatibility and remaining quantity are estimated.
- Five 19-0897 backflow preventers, fourteen specified solenoids, six GASHER checks, twenty PP1208E bulkheads and other same-part receipts contribute stock credits. One of the six acquired TAISHER elbows is reserved for the destructive jet coupon.
- Approximate remaining White/Blue/Red PET-GF credits are 0.8/0.9/0.9 kg. White ASA Aero is credited provisionally at 1 kg from the two acquired spools, with the other reserved for development. TPU is credited at a provisional 0.5 kg. These balances are unmeasured estimates.
- Cut stock and non-filament consumables use a visible provisional one-machine consumption reserve against acquired quantities. This is a budgeting assumption, not a claim about measured development usage. Continued development consumption can increase the orders.
- Terminal, ferrule and heat-shrink assortments without usable counts by required size receive no aggregate numerical credit. Two exact-width 100-piece Baomain female-disconnect packs are credited provisionally. The five-colour 16 AWG kit is credited as one kit; remaining colour allocation is unverified.
- The one acquired water filter has unrecorded remaining service life and customer-unit availability; a fresh filter is budgeted for each machine. Ten unidentified NPTF male connectors are not credited as PP010822E without a matching SKU. Finished printed parts without a counted current usable balance receive no additional material credit.

These records establish a traceable estimate, not an assertion that all historical purchases are still available or qualified. Physical acceptance keeps its recorded scope.

## Already-ordered components and payment reserve

Already-ordered quantities are separate from on hand and are deducted to prevent duplicate orders:

| Component | Received credit | Incoming credit | State at October 4 |
|---|---:|---:|---|
| WR1105 regulator | 0 | 3 | Shipped; estimated October 7 arrival. Confirmed $91.56 charge excluded from future spend. |
| PI450822S female adapter | 0 | 30 | Shipped October 1; delivery pending. |
| Taprite 3741 primary regulator | 0 | 1 | Ordered October 5 (Draft Warehouse 244592); delivery pending. Its $75.63 is reserved until a charge is confirmed. |
| Clear PETG 32101 1 kg refills | 0 | 10 | Ordered October 5 (Bambu us783865986561351681); preparing for shipment. Its $120.05 is reserved until a charge is confirmed. |
| Four-pin pogo contact pairs | 4 | 6 | Six delayed and unshipped. Confirmed $21.87 charge for the received portion excluded. |
| M1.4 inserts | 0 | 200 | Ordered; estimated October 7 arrival. |
| M1.4 × 8 screws | 0 | 50 | Ordered; estimated October 7 arrival. |

All three alternatives include a **$351.31 possible-payment reserve** for the ten Clear PETG refills ($120.05), the PI450822S shipment ($94.54), the Taprite 3741 regulator ($75.63), six pending pogo pairs ($43.74), insert pack ($8.57) and screw pack ($8.78). Merchant payment confirmation is incomplete. This is a conservative allowance for a possible remaining balance, not a verified amount owed. Release it when those orders are confirmed paid. Tax is not added again to these delivered order amounts.

Delivery is required before assembly. A delayed order is not physically available stock, and an acquired status alone does not prove payment.

## Supplier quantities

The lot calculation minimizes new purchase cash among the sourced options. It can buy more than the net shortfall when a bag or discounted tier costs less. A lower unit price does not justify an expensive case of unneeded stock. The JSON supplies the exact purchase options, units, per-machine requirements, price basis, inventory credits and uncertainty notes; the website calculates and displays all three order lists.

- Black PET-GF material is planned at 6.01 kg per machine, rounded from the 6.0091 kg BOM colour split, plus a provisional 15% allowance for supports, purge and rejects. After the 10.4 kg stock credit, new orders are **eight 3 kg spools plus one 1 kg spool for five machines**, **nineteen 3 kg spools plus two 1 kg spools for ten** and **forty-two 3 kg spools plus two 1 kg spools for twenty**. The five-machine mix buys 25 kg for $629.91, less than nine 3 kg spools at $674.91. White, Blue and Red have separate requirements and credits.
- Clear PETG needs **no new refills for five or ten machines and eight for twenty**, after its 3 kg credit and the ten refills already ordered. The manufacturer tier is calculated from the replenishment order, so the eight use the 6+ tier. Existing 10 kg Black PETG covers all three alternatives without a new refill order.
- A 50 ft copper coil yields three complete 15.92 ft evaporator cuts. The provisional remaining two usable cuts reduce new coil orders to one / three / six for five / ten / twenty machines. Offcuts cannot be joined to make another evaporator.
- Reservoir rod blanks use one 12-inch rod each; two carbonator blanks share a rod. The selected 316 five-pack is rounded after the usable-equivalent stock allowance. Shorter or different-diameter rods are not assumed interchangeable.
- Soda umbilicals use one 24-inch and five 12-inch insulation cuts per machine. Each six-foot roll is cut into those discrete lengths; the provisional five-foot stock credit reduces new orders to five / eleven / twenty-three rolls for five / ten / twenty machines.
- Red gas tubing includes the external tether and three internal segments, about two feet total per machine. A provisional 25% cut/slack reserve is applied before crediting the acquired red tubing. It covers all three batches without a new order.
- Each silicone funnel uses a provisional 273 g mixed-material allowance. Kits contain approximately 1,098 g. Stock and process yield remain estimates.
- Ribbon cable is purchased by conductor count. The provisional two/three/five gross 16 AWG colour kits for five/ten/twenty machines become one/two/four new kits after the existing kit credit. Terminal and ferrule refills use conservative size-specific allowances while the width/gauge map remains open.
- The acquired reusable bath container serves any batch. Fluids, welding wire, pigment, mold release, foam and refrigerant use explicitly provisional remaining quantities and production yields, rounded to whole containers only when replenishment is required.

Amazon prices come from signed-in Prime-filtered results; conditional coupons and multi-item promotions are not deducted. Other suppliers use their current catalog or marked historical delivered allowances. Supplier availability is a dated observation, not a reservation of the full order.

## Supply and quote limits

Bambu ASA Aero White 46100 is out of stock. The provisional 1 kg on hand covers the approximately 0.243 / 0.485 / 0.971 kg float-feed requirements for five / ten / twenty machines including the 15% allowance, so no replenishment is budgeted. If the actual remainder is below the requirement, a source is needed. No interchangeable foaming filament is assumed.

Ten relief valves are listed; after one credited valve, the twenty-machine plan needs nineteen new valves and exceeds listed stock by nine. The ten credited silicone washers reduce the twenty-machine requirement to three new ten-packs, within the observed stock. The candidate R2031-NL-62 faucet has twelve listed; nineteen new faucets for twenty machines exceed that by seven. Its $52.40 price is an allowance pending confirmation of the handle/body interfaces against the accepted A2031-NL-62.

Exact Prime replenishment sources remain unconfirmed for several plumbing/refrigeration items, the flow meter and short M3 inserts; positive delivered allowances cover their shortfalls. The donor ice maker's current listing names a different suffix, so internal compatibility is unconfirmed.

The exact PP1208E bulkhead union is sourced from Fresh Water Systems, and the exact 1.47-inch display from Waveshare. These are same-part supplier substitutions. Mouser pricing and batch stock remain estimates. Additional JLCPCB assembly, OnlineMetals cuts and SendCutSend parts require current quantity-specific quotes; historical delivered lots supply the allowances. No unquoted volume saving is assumed.

Some electrical terminations remain open. Positive allowances cover them without asserting a selected production procedure or physical acceptance.

## Expense basis

New parts/materials, new inbound freight/import reserves and tax form the delivered replenishment budget. A supplier with no new purchase incurs no new freight. The 7.25% tax reserve, drawn from recorded orders, applies only to merchandise-priced purchases and new inbound reserves; historical delivered allowances are not taxed twice.

The headline additional-cash budget adds the possible pending-payment reserve, $40 per machine for cartons/protective packing/customer guides, $80 per machine for customer delivery and $125 / $200 / $350 per five / ten / twenty-machine batch for shop gases, auxiliary solder/cleaning supplies and production electricity. Packing and delivery are unquoted estimates. Shop allowances use a provisional $50 per batch plus $15 per machine and cover additional usage beyond the explicitly credited BOM supplies; remaining gas and electricity usage are unmeasured.

Build labor uses the existing practiced-operator estimate and rate, shown separately. Paying an operator adds that amount to cash required; owner labor is not automatically a cash payment. Prior development time is excluded. Early-build labor and attended work already completed on unit 1 are not fully quantified, so the labor line is a forward planning allowance rather than an actual unpaid-hours balance. Extra tooling, rent, payment fees, installation, warranty/support and business taxes are outside this forecast.

New excess-stock value uses average new purchase cost before freight/tax. Existing inventory is not assigned a second purchase cost. The per-row stock left after a batch includes both existing and newly acquired remainder; colour, size and offcut constraints can prevent it from supplying another whole machine.

The stored BOM digest marks the public forecast for review if the BOM changes. Refresh opening balances, pending delivery/payment states, prices, lot options, quotes and BOM coverage together. The forecast is not a submitted supplier order.
