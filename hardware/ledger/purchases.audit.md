# Auditing project purchases

[purchases.md](/hardware/ledger/purchases.md) records project procurement values and fulfillment. [purchases.evidence.json](/hardware/ledger/purchases.evidence.json) links stable purchase and order IDs to sanitized vendor sources and merchant charge/refund events. [purchases.export.json](/hardware/ledger/purchases.export.json) and [purchases.export.csv](/hardware/ledger/purchases.export.csv) are deterministic analytical views. Their totals describe different bases and must not be added together.

The [schema and external private reconciliation contract](/hardware/ledger/purchases.schema.md) defines authoritative fields, date precision, allocation rules and the public/private boundary.

The [ledger-maintenance skill](/tools/ledger-maintenance/SKILL.md) carries the Gmail-to-ledger workflow, private processing checkpoint and publication handoff for the dot and local agents.

## Preserved vendor records

`purchases.orders.json` is a preserved Amazon source archive. Older delivery banners disappear from Amazon; the saved dates and project classifications are irreplaceable evidence. Recorded mixed-order allocations and replacement relationships remain in that archive. A fresh page lacking an older field does not override it.

The archive contains pre-existing nonproject metadata. It is not a project export. New public sources and exports contain project lines and project shares only. Do not copy unrelated items, full mixed-order totals, private receipt links, customer identifiers or payment-instrument details into evidence, generated artifacts, logs, fixtures or commit messages.

A saved order total can corroborate a procurement allocation. It does not establish a completed merchant charge. The order checker compares the recorded project row value with the saved project share using exact arithmetic. Orders split across several rows are checked once per order; a row spanning several orders remains explicitly unresolved until actual line allocations are established.

## Read-only inspection

```sh
tools/run -- cargo build --release --locked -j 2 --manifest-path tools/hsm/Cargo.toml -p hsm-ledger --bin purchases
tools/hsm/target/release/purchases --report
tools/hsm/target/release/purchases --audit
tools/hsm/target/release/purchases --export-json
tools/hsm/target/release/purchases --export-csv
tools/hsm/target/release/purchases --check
```

These paths write nothing to the repository. `--check` fails on mechanical integrity errors or stale generated output. Incomplete historical evidence, unknown payment dates and old open orders are coverage findings; a passing integrity check is not full financial reconciliation.

Regeneration is explicit:

```sh
tools/hsm/target/release/purchases --write
```

The bare invocation regenerates too; it is what the build runs. It updates managed Markdown figures, the figures sidecar and the JSON/CSV exports. Do not hand-edit generated figures or exports.

Evidence readings:

```sh
repo-tools check purchase-evidence
repo-tools check ledger
```

## Source review

Read only relevant project order, invoice, shipment, subscription and refund records. Do not read banking sources or change merchant accounts. Use vendor document references safe to disclose. Keep private access locators outside repository files; an ignored path does not make personal records safe.

Capture a read-only baseline before changing recorded amounts. Record the exact source supporting a correction, retain prior estimated values as noncontributing price history, and preserve unrelated work in the checkout.

A vendor source must prove the fact being recorded:

- An order confirmation proves a placed order and its quoted value when stated.
- A final invoice proves the final vendor amount and invoice date when stated.
- A completed merchant transaction or monetary receipt proves a charge; use a separate event date only when the source supplies it.
- A shipment or delivery confirmation proves fulfillment, without implying payment.
- An issued monetary refund is a distinct event linked to the purchase and original charge where known. Approval of a refund is an expectation.
- A replacement at no charge preserves the original paid purchase and contributes an actual zero purchase value. It does not create another charge.

The machine-readable `coverage` and `gaps` records name examined scopes and missing facts. The newest retrieved receipt is not proof of complete earlier coverage. The current evidence review includes all 81 receipts underlying the six AI legacy groups, later project Anthropic receipts, Render invoices and receipts, selected Amazon order-scoped payment pages, the Bambu account's order records, merchant order pages for named direct-vendor orders, eight named paid SendCutSend invoices, and named direct-vendor documents. Vendor searches remain partial account coverage.
