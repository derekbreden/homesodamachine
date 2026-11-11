# Production and purchase planning

The [planning workspace](https://homesodamachine.com/cost#batch-forecast) connects
recorded stock, physical material demand and proposed supplier packs. Select a
unit to inspect its place in a cumulative production sequence. Earlier units
consume their requirements before later units can use the remaining stock.

## Stock and demand

[`stock.json`](stock.json) owns available, incoming and reserved balances with
their evidence and uncertainty. The material catalog owns assembly contents;
[`bom.md`](bom.md) supplies physical manufacturing inputs. Completed machines and
subassemblies satisfy demand before their components are expanded. The
[build planner](https://homesodamachine.com/build) reads those same records.

On-hand stock, estimated quantities, existing orders and proposed purchases
have distinct representations. Incoming orders reduce duplicate purchasing but
remain awaiting receipt. Unknown stock receives no numerical credit. An
undefined manufacturing input remains unresolved even when its supplier stock
or purchase price is known. Coverage bars count material lines and describe
material availability; they do not measure assembly progress.

Each unit's detail separates its additional demand from the cumulative demand
through that unit. Reusable equipment remains available across the sequence.
Reservations and completed-stock credits apply before purchasing is calculated.

## Purchase scenarios

[`batch-forecast.json`](batch-forecast.json) records supplier options, pack sizes,
quantity prices, delivery reserves and dated observations. The workspace
compares these options for suggested purchases, credits incoming orders and
retains shortages whose only recorded source is unavailable. Pack counts can
be adjusted individually; custom packs can supply a proposed quantity and price.
An unpriced custom pack retains its unpriced status.

Changing packs updates the material outlook and the quoted purchases still
needed through each production target. A proposal is saved in the current
browser and can be exported. It neither reserves stock nor records an order.
Receipts and actual production belong in the shared stock ledger.

## Dollars and evidence

The proposed-purchase budget separates pack prices, a delivery reserve and a
tax reserve. Delivered-price offers are not taxed again. Delivery uses the next
recorded batch allowance for the selected purchase target. Custom packs use
merchandise pricing and still require a shipping quote. Supplier observations
remain dated evidence rather than a reservation or live availability check.

The remaining-purchases figure includes quoted packs beyond the current
proposal. Requirements without a usable quantity or supplier quote remain
visible and are excluded from quoted dollars. Full build labor, shop allowances,
existing payment commitments and investment recovery retain their separate
meanings in the cost and purchasing records.

[`web/lib/production-planner.js`](../../web/lib/production-planner.js) projects
the shared physical plan into the workspace. The server and browser share
[`production-plan.js`](../../web/contracts/production-plan.js) and
[`purchase-lots.js`](../../web/contracts/purchase-lots.js) for scenario coverage
and supplier-pack arithmetic. [`stock.md`](stock.md) describes actual physical
activity; [`labor.md`](labor.md) describes planned attended work.
