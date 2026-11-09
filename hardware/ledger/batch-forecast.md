# Purchases from available stock

[`batch-forecast.json`](batch-forecast.json) holds supplier offers, lot sizes,
freight and price assumptions for the purchasing forecast on
[the cost page](https://homesodamachine.com/cost#batch-forecast).
[`stock.json`](stock.json) owns the inventory facts and physical planning
allowances. Both the purchasing forecast and [Build from stock](https://homesodamachine.com/build)
read its projected balances.

## Inventory and demand

Each forecast is an alternative request for complete integrated machines and
starts with the same stock. Completed machines and subassemblies reduce their
components before manufacturing inputs are calculated. The website selects the
supported batch sizes.
Usable on-hand stock reduces new purchases. Existing orders reduce duplicate
purchasing; receipt is still required before their material is available to build.
Reservations reduce the stock available to the plan. An unknown balance receives
no numerical credit and remains marked as unknown.

The stock ledger preserves the evidence date, source and uncertainty of each
balance. Purchase receipts, stock counts and completed production update that
shared record. Supplier price and availability observations retain their own
checked dates; an inventory update does not establish a new supplier quote.

## Supplier quantities and cash

The lot calculation compares the sourced purchasable options after stock
credits and can buy useful excess stock when that lowers the new cash required.
The quoted budget lists requirements without an input definition or supplier
quote separately; those requirements are excluded from the quoted amount.
Stock units and supplier lots describe the same physical quantity. Requirements
whose usable cutting yield or size allocation remains unresolved retain their
explicit planning allowance and uncertainty.
Reusable equipment supplies the batch without being consumed. A provisional
purchase reserve scales with unmet material demand before supplier lots are
selected, so completed-stock credits reduce the reserve too.

The forecast separates merchandise, delivered-price allowances, inbound freight,
tax reserves, possible remaining payments, shop supplies and planned attended
labor. The labor figure is a practiced full-batch benchmark, rather than the
remaining effort after stock credits. Actual completion work is recorded with
its material. Acquired stock creates no new acquisition expense. A fulfillment status
alone establishes neither a charge nor a refund; payment evidence belongs to
[`purchases.md`](purchases.md) and its analytical records.

## Evidence and assumptions

The JSON supplier offers carry source links, dated availability observations,
whole-lot quantities and notes for provisional yields and unquoted supplies.
Prime-sourced prices retain their signed-in listing evidence. Other suppliers
retain their catalog or delivered-order basis. Availability is an observation;
a supplier has not reserved that quantity for the plan.

[`stock.md`](stock.md) describes stock evidence, completed assemblies and actual
physical-work records. [`bom.md`](bom.md) and [`labor.md`](labor.md) describe the
material and practiced-work estimates behind a complete machine.
