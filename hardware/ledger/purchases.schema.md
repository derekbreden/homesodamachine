# Purchase evidence and analytical exports

Schema version **1** extends the project purchase ledger. It separates procurement value, fulfillment and merchant payment evidence. The current reporting period is 2026; identities and precision-preserving dates work across calendar years.

## Authoritative inputs

| Fact | Editable home |
|---|---|
| Purchase description, subsystem section, quantity, current row price, order/receipt/invoice table date, fulfillment | `purchases.md` |
| Persistent purchase identity | The row's `<!--purchase:pur-…-->` comment |
| Canonical vendor, project purpose, price evidence, order relationships, source references, explicit service periods and supplemental dates | `purchases.evidence.json` → `purchases` |
| Order identity and source-backed order facts | `purchases.evidence.json` → `orders` |
| Completed/expected merchant events and exact project allocations | `purchases.evidence.json` → `events`, `allocations` |
| Individual reconstructed amounts underlying frozen legacy aggregates | `purchases.evidence.json` → `details` |
| Source scope, conflicting evidence and missing facts | `purchases.evidence.json` → `sources`, `coverage`, `gaps` |
| Preserved older Amazon facts and classifications | `purchases.orders.json`; retain its irreplaceable evidence |
| Managed figures, reports, machine-readable records | Generated; do not edit directly |

The Markdown cost is a row total unless explicitly marked `ea` or `ea.`. Only that unit-price notation multiplies by the leading quantity. A ten-piece bundle at $12.00 costs $12.00, while ten items at $12.00 ea cost $120.00. Unknown cost is `null` in exports and is distinct from a genuine zero-dollar purchase. Quantity is unknown when the source does not establish a usable quantity; heterogeneous bundles retain their description and row-total basis.

Keep purchase IDs unchanged when editing descriptions, moving rows, changing sections, revising prices or updating fulfillment. New IDs should be opaque project identifiers, for example `pur-` followed by a fresh UUID, rather than row positions, descriptions, dates or amounts. `order_id` uses a stable vendor namespace and a safe order/invoice reference, such as `render:EXAMPLE-0001`; use an opaque identifier if no safe external reference exists. `event_id` and `allocation_id` are persistent opaque project identifiers. Never use a private financial ID, its hash or a payment-instrument fingerprint.

A preserved legacy aggregate is original evidence, rather than a second editable copy of individual current prices. When its `details` are present, the export keeps the parent as `record_role=group_summary`, `contributes=false`, and contributes its details once. A partial reconstruction derives a `legacy_remainder` with the original coverage range; it is not allocated evenly across months. Child amounts must not exceed the original aggregate. Each child's `ledger_purchase_id` traces it to the Markdown aggregate.

`price_history` stores a noncontributing prior estimate or conflicting quoted amount with its source. A later final value updates the same purchase, retaining its ID. A history entry is not another purchase or charge.

## Evidence sidecar

Top-level fields are `schema_version`, `as_of`, `reporting_period`, `currency_scales`, `purchases`, `orders`, `details`, `sources`, `events`, `allocations`, `coverage` and `gaps`. Dates use source calendar dates without unnecessary timezone conversion. Unknown dates are `null`.

```json
{"precision":"day","value":"2026-09-30"}
{"precision":"month","value":"2026-09"}
{"precision":"range","start":"2026-09-28","end":"2026-10-28"}
```

A range contained in one month can enter that month without implying a known day. A range spanning months enters `undated_unallocated`; it is never spread across those months. Order date, invoice date, receipt date, merchant event date, delivery dates and service period remain distinct. `row_date_basis` identifies the Markdown column as `order_date`, `invoice_date`, `receipt_date` or `coverage_period`. The latter three do not manufacture an order date. Receipt and notification dates are distinct source fields; an actual-delivery notification alone does not independently supply its delivery day.

Money in analytical records is nonnegative integer `amount_minor` plus `currency`, with scales declared in `currency_scales` (`USD: 2`). Refund amounts are positive; the net view subtracts them. Decimal arithmetic preserves exact Markdown values and rejects amounts that cannot fit the declared currency scale. Unknown amounts stay `null`.

| Entity | Main fields |
|---|---|
| Purchase metadata, keyed by persistent row ID | `vendor`, `purpose`, `amount_evidence`, `order_ids`, `source_ids`, `allocation_status`, supplemental `invoice_date`, `receipt_date`, `delivery_dates`, `service_period`, `stream`, `replacement_for`, `price_history` |
| Order, keyed by vendor-namespaced ID | `vendor`, safe `reference`, `order_date`, `allocation_status`, `source_ids`, optional `replaces` / `replaced_by` |
| Source, keyed by persistent source ID | `vendor`, `document_type`, safe `reference`, `document_date`, `proves`, `verified_at`, optional `receipt_date`, `notification_date`, `merchant_event_date`, `service_period`, `invoice_reference`, sanitized `note` |
| Event | `event_id`, `vendor`, `event_type`, `confirmation`, `event_date`, `amount_minor`, `currency`, `allocation_status`, `source_ids`, `verified_at`, optional `original_event_id`, receipt/invoice dates and service period |
| Allocation | `allocation_id`, `event_id`, `purchase_id`, optional `order_id`, `amount_minor`, `currency` |
| Coverage | `coverage_id`, `vendor`, `stream`, `evidence_type`, `checked_at`, `examined_period`, `complete_period`, `coverage`, `source_ids`, scoped `order_ids`, sanitized `note` |
| Gap | `gap_id`, related purchase/order/event/source ID lists, `missing_fact`, `sources_checked` |

`amount_evidence` is `estimate`, `final_vendor_amount` or `legacy_unverified`. A final invoice establishes price; it does not establish payment. `allocation_status` is `all_project`, `mixed_partial` or `unresolved`. For mixed records, every published amount is the project share, and the full merchant payment is outside the public export. Unrelated item names and personal remainder amounts are omitted.

Fulfillment includes `ACQUIRED`, `ON-ORDER`, `MISSING`, `PARTIAL`, `CANCELLED`, `RETURNED`, `REPLACED`, `REPLACEMENT` and `UNRESOLVED`, alongside existing planning/exclusion labels. A split order can have received and pending rows. A no-charge replacement links to the original purchase using `replacement_for`; the original valuation remains recorded and the replacement has its actual zero value. Current inventory belongs in `inventory.md` and is not computed by adding purchase values.

Events distinguish `charge`, `refund`, `authorization` and `noncash_credit`; `confirmation` is `confirmed` or `expected`. A pending debit is an expected charge unless the vendor explicitly identifies it as an authorization. Issued monetary refunds retain the original charge and link it with `original_event_id` when known. Store-credit issuance and spending are noncash events and do not create bank cash flow. Prepaid usage-credit purchases contribute a payment once; later consumption is a service/usage fact, not a second charge. Subscription service periods stay separate from top-ups.

`proves` states each source's capabilities: price, order date, delivery, charge, refund, authorization, noncash credit, service period, no charge, receipt/invoice/notification date or merchant event date. A confirmed payment requires a source proving that event type. A dated confirmed payment also requires merchant-event-date evidence. Multiple invoice/receipt sources may corroborate one event; duplicating a document must not create another expense. Meaningful contradictory amounts remain in history/gaps for review.

Allocations support split charges, consolidated charges, partial refunds and order-wide payments. Their sums must equal each known published event amount for `all_project` and `mixed_partial` events. An order-only allocation uses `purchase_id=null` and a valid `order_id`; it balances the known project event while leaving item attribution unresolved. It does not silently allocate to a row because amounts happen to match. Unresolved allocations may remain partial and are separately reported. All event allocations are exact; the inherited one-cent rounding allowance for preserved procurement invoices is reported explicitly as a residual, rather than hidden or promoted to a balancing charge.

Purpose tags are `equipment_tooling`, `components`, `consumables_materials`, `engineering_software_services`, `hosting_domains`, `documentation_marketing` and `unclassified`. They describe the purchase, rather than the merchant. Printer accessories and filament remain distinct; a heterogeneous tax/shipping line without evidenced purpose allocation stays unclassified. Subsystem sections answer a separate question. These tags do not assert accounting, tax, capitalization or depreciation treatment.

## Generated views

```sh
python3 hardware/scripts/_ledger_totals.py --write
python3 hardware/scripts/_ledger_totals.py --report
python3 hardware/scripts/_ledger_totals.py --audit
python3 hardware/scripts/_ledger_totals.py --export-json
python3 hardware/scripts/_ledger_totals.py --export-csv
python3 hardware/scripts/_ledger_totals.py --check
```

Only `--write` and the compatible bare invocation regenerate files. Inspection, export-to-stdout and check modes are read-only. `--ledger`, `--orders` and `--evidence` select explicit input paths. Regeneration writes `purchases.figures.json`, managed Markdown values, `purchases.export.json` and `purchases.export.csv`.

JSON exposes `purchases`, `orders`, `events`, `allocations`, `sources`, `coverage`, `gaps`, `validation` and `summary`. It includes schema version, as-of date, reporting period, currency scales and a deterministic project-input fingerprint. Generated Markdown figures are excluded from the fingerprint. Private bank data and the raw merchant-account archive are not copied into exports.

CSV is one rectangular table with a `record_type` discriminator. Record types include `metadata`, `purchase`, `order`, `event`, `allocation`, `source`, `coverage`, `gap`, `procurement_monthly`, `procurement_undated_unallocated`, `procurement_totals`, corresponding `merchant_payments_*` records, `fulfillment`, `uncertainty` and `validation`. Nested lists and precision dates are JSON cells; integer amounts can be loaded directly. Empty amount cells mean unknown, while `0` means actual zero. The JSON summary defines each analytical basis in full.

The views are independent:

- **Procurement by order month:** current project purchase values, with final, estimated and legacy values separate. Canceled and planned purchases and noncontributing summaries are excluded. Returns retain original acquisition value; monetary refunds remain distinct events. Invoice/receipt/service dates do not substitute for missing order dates.
- **Merchant payments by event month:** confirmed project charges, issued monetary refunds and net. Expected charges, authorizations, noncash credits and unresolved project shares are excluded from those cash/card measures. Apple receipt amounts without a separate charge date enter the undated bucket.
- **Fulfillment:** outstanding and current status by purchase ID, regardless of payment. Paid open orders remain outstanding; returned/canceled purchases requiring refund evidence remain identifiable. These values do not establish unpaid obligations.
- **Coverage and uncertainty:** amounts and IDs for undated records, missing or partial merchant evidence, estimates, legacy price evidence and unresolved allocations. These overlapping categories must not be added together.

Monthly amounts plus the undated/unallocated bucket reconcile exactly to each view's total per currency. IDs in those buckets trace values to purchases, allocations and evidence. A month with no retrieved contributions has `evidence_scope=retrieved_records_only`; zero numeric contributions do not prove zero actual activity. Coverage records separately name which vendor stream and evidence type were examined, what period is actually complete for a stated scope, and what remains partial/unknown.

The legacy `LEDGER_ACQUIRED_HW` display bucket retains acquisition valuations of replaced/returned originals, alongside acquired hardware; section valuations use the same definition. It is not an inventory valuation or a confirmed-payment total. The grand procurement figure includes open commitments and legacy amounts; the merchant-payment figure is separate.

Structural validation fails for broken IDs, unsupported evidence claims, inexact money, duplicate payment evidence, inconsistent event allocations or stale generated output. Missing historical evidence and scoped legacy rounding residuals remain explicit findings. Passing checks is not a claim of full reconciliation.

## External private reconciliation

An analyst can load the exports and join `event_id` → allocations → purchase/order IDs. Safe vendor document references, project amounts, currencies, known dates, source capabilities and split/mixed/replacement relationships supply candidates for matching.

The analyst's private system may independently map **project event ID ↔ private financial transaction ID ↔ matched allocation**, with many-to-many and uncertain matches. The mapping, account identity, funding ownership, bank posting dates and all bank-derived reconciliation results stay outside this repository. Merchant-account ownership does not establish who economically funded a purchase. Vendor, amount and nearby dates suggest candidates; they do not prove a match. A credit-card repayment is not another project purchase.

Do not implement an importer, write bank-derived fields back, or publish a bank-verified flag. Mixed-order full-payment matching happens only in that private system. Keep statements, private exports, receipt images, mailbox locators, authentication material and signed access links outside tracked content and generated artifacts; ignoring a path is not a sufficient privacy boundary.
