# Stock and physical work

[`stock.json`](stock.json) owns inventory facts and recorded physical work for
[Build from stock](https://homesodamachine.com/build) and the
[purchasing forecast](https://homesodamachine.com/cost#batch-forecast).
The material explorer reads the same build plan on its Stock tab.

## Definitions and evidence

The material catalog owns identities and assembly contents. The authored
physical quantities in [`bom.md`](bom.md) supply manufacturing inputs through
`web/lib/bom-lines.js` and `web/lib/material-stock.js`. Costing reads those same
BOM lines and material configurations; an input quantity does not depend on its
price. Unmeasured input quantities retain an explicit physical planning
allowance or remain unknown.

`resources` owns the opening on-hand, incoming and reserved balances, physical
units, planning allowances and evidence. `bindings` connects material identities
to supplier stock; `printing` selects stock colors; `kits` states the outputs a
donor supplies together. These identities remain stable when their display names
or supplier offers change. `observations` carries dated opening corrections.
Supplier offers and lot prices belong to [`batch-forecast.json`](batch-forecast.json).
Reusable equipment is required across a batch and stays available after work.
Provisional purchasing reserves, such as an unmeasured wire-color allocation,
belong to the stock definition and shrink with the remaining physical demand.
Shared BOM-line allocations retain their estimated status.

Unknown balances receive no credit. Estimates retain their evidence and uncertainty.
Incoming stock reduces duplicate purchasing and becomes available to build on
receipt. Completed parts and assemblies satisfy demand before their components
and manufacturing inputs are expanded. Each browsed plan starts from the same
balances and reserves nothing.

## Record physical activity

Start the workbench on this Mac from the repository root:

```sh
node tools/stock.mjs serve
```

The command prints the local address. Open Build from stock there and choose
the material and output quantity. The local page offers completion, receipt and
count entry. Recording controls write only through the local workbench.

A completion starts with the listed inputs and ends with the completed output.
Prepared components are consumed as components; printing a component consumes
its manufacturing stock. Standard component quantities are prefilled. Adjust
them to the quantities actually used, remove unused inputs and add other stock
when the work requires it. Estimated usage remains marked until measured.
Record hands-on minutes when known and describe preparation or rework in the note.
Equipment waits belong to machine time.

**Record and publish completion** saves the consumed inputs, completed stock and
measured effort in the same ledger entry, then commits and pushes the stock ledger.
The local plans update immediately; the shared site adopts the published ledger
through its normal deployment. A publication failure leaves the physical record
saved and offers publication retry. Retrying the same record cannot consume
stock again.

Receipts add received stock and reduce incoming quantities. Counts establish
observed on-hand stock and can correct an estimated balance. Use the actual
finish for finish-dependent parts; common components share a balance across
faucet finishes. A purchased material and its supplier stock use the same balance.

## Record structure

`events` holds activity in posting order. Each entry has a stable `id`, `kind`,
`occurredAt`, `recordedAt`, `note` and evidence `sources`.

A `completion` has an `output` with material, quantity and applicable finish;
`inputs` with material or resource, quantity and unit; and nullable
`attendedMinutes`. Its quantities are stored with the work, so a later design
edit does not recalculate past consumption. A `receipt` or `count` identifies
the material or resource and quantity. A count may also establish `incoming`
and `reserved` quantities. The occurrence date describes the physical activity;
posting order determines the current balance.

Measured completion work appears beside the labor allocated to the same scope.
Component work already recorded separately is excluded from that completion's
timing. The complete-unit cost and full-batch labor benchmark retain their
planning meaning.

Recorded consumption beyond an estimated balance remains visible and calls for
a physical count. Consumption from an unknown balance does not invent a remainder.
The ledger writer serializes concurrent entries and replaces the file atomically.
The lock serves stock recording and adds nothing to CAD or normal builds.

## Agent commands

`node tools/stock.mjs plan <material>` prints a completion draft with its stable
record identity and proposed inputs. Edit it to describe the actual work, then
use `node tools/stock.mjs record <event-file> --publish`. The same writer and
projections serve the workbench. `node tools/stock.mjs publish` retries publication
of a saved stock record without creating another physical event.

Stock quantities establish material availability. Fabrication methods, fit and
physical qualification remain in the relevant part and assembly records.
