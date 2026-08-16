# Auditing purchases

Reconciling [purchases.md](/hardware/ledger/purchases.md) against what Amazon
charged. Two files join on the order number:

- `purchases.md` — the ledger rows, each carrying `Order #`, `Ordered`, `Delivered`.
- `purchases.orders.json` — the Amazon record, keyed by order number: order date,
  delivery date, invoice grand total, a `project` flag, and `nonproject_amount`
  on a mixed order.

The row-cost convention and the totals rewrite live in
[_ledger_totals.py](/hardware/scripts/_ledger_totals.py).

## purchases.orders.json holds data Amazon will not serve again

Amazon shows a delivery date in the order-list shipment banner for roughly four
months back. Past that the banner is gone, and the detail page never carried the
date either. `orders.json` is the only record of 212 delivery dates. For that
field it is primary source, not a cache.

The same applies to judgement already recorded in it: the `project` / `why`
classifications, and the two `nonproject_amount` values, each of which cost an
invoice fetch and a human call.

## Pulling the Amazon record

### The walk

```
https://www.amazon.com/your-orders/orders?timeFilter=year-2026&startIndex=N
```

`N` steps by 10. Fully query-param navigable. 2026 is 32 pages × 10 = 318 orders.
A `startIndex` past the end returns HTTP 200 with zero order cards — that, not
the pagination widget's page count, is the terminator.

`purchases.md` is scoped to one calendar year, which the `timeFilter` matches. A
run after year rollover walks both `year-2026` and `year-2027`.

Order history is not filtered by Prime. The Prime rule in
[CLAUDE.md](/CLAUDE.md) governs what to consider when shopping; order history is
what was actually bought, and a tax record drops no cash outlay.

### The order cards are encrypted and decrypt client-side

`fetch()` + `DOMParser` returns markup whose `.order-card` holds only inline
script — `window.SiegeClientSideDecryption`. The parse succeeds, the card count
is right, and every extracted field is `null`. **A scrape reporting plausible row
counts with empty fields has hit this.**

Rendering the page runs the decryption. From an already-open Amazon tab, append
a hidden same-origin `<iframe>`, set `.src` per page, wait for `onload` plus
~1.2 s settle, then read `iframe.contentDocument`. Same-origin framing is
allowed.

Read text with `innerText`, on a rendered document. The order header reads
"ORDER PLACED" through CSS `text-transform`; `textContent` returns the
untransformed source, and on a non-rendered document `innerText` returns
nothing. A regex written against what the screen shows fails against a parsed
document.

### What each surface carries

| | Order-list page | Invoice / detail page |
|---|---|---|
| Order number, placed date, grand total | ✓ | ✓ |
| Every item's title and ASIN | ✓ | ✓ |
| Delivery date | shipment banner, recent orders only | — never |
| Subtotal, shipping, tax, per-item price | — | ✓ |

The list page carries the full item inventory, untruncated — a 17-line order
lists all 17. A list-only walk is enough to find purchases no ledger row names.

Delivery-date coverage frays across a week rather than cutting cleanly: the
latest order without a banner is 2026-04-21, the earliest with one is
2026-04-14. As of the 2026-08-15 walk, 212 of 318 orders carry a date; of the
106 without, 3 are cancelled and 1 in transit, leaving 102 permanent gaps.

### Walk the list; open an invoice only when the check complains

32 list-page loads buy every order with its grand total, items and ASINs —
everything `--check` compares against, since it tests a row's allocated sum
against the invoice **grand total**.

An invoice buys one thing: splitting a single invoice across several ledger
rows. It is needed only where an order carries two or more rows **and** their
sum disagrees. The 2026-08-15 walk opened 21 of 318. Opening all of them costs
~300 further loads at ~2.5 s each.

### Getting the data out

Accumulate into `window.__*` in the page, reduce to one compact line per order
*in the browser*, chunk, and append each chunk to disk. 318 orders reduced to 13
chunks.

- `javascript_tool` truncates its return near ~1000 characters. Measure the limit
  before sizing chunks.
- CDP `Runtime.evaluate` times out at 45 s — batch 6–8 page loads per call. The
  JS keeps running past the timeout and its `window` state survives, so a
  timed-out batch is resumable rather than lost.
- No rate limiting, CAPTCHA, or session expiry appeared across ~340 page loads.

Indexing `purchases.md` into JSON runs as a subagent in parallel with the scrape.
No contention.

Exporting every order is what produces `orders.json`. Running only the check
needs less: inject the ledger's order numbers into the page and return the
disagreements.

### What a re-run skips

Scrape only orders whose placed date is newer than the newest `ordered` already
in `orders.json`. Classify only order numbers the file does not contain. Every
`project` / `why` judgement, both `nonproject_amount` values, and all 212
`delivered` dates carry forward untouched.

## Running the checks

```bash
python3 hardware/scripts/_ledger_totals.py --check
```

Exits 1 on a stale totals marker, on an order whose rows allocate a sum other
than what its invoice charged, or on an ON-ORDER row older than
`STALE_ON_ORDER_DAYS`.

```bash
python3 hardware/scripts/_ledger_totals.py --audit
```

Prints the rows and orders that need a person:

| Group | Closed by |
|---|---|
| Ambiguous / multiplied / priceless rows | Nothing — qty-multiplied rows are listed so their arithmetic is visible. A `no-price` row contributes $0 to every total. |
| Orders a row names that no invoice covers | Adding the order to `purchases.orders.json`. |
| Orders shared by a row that names several | Splitting the row, one order per cell, each priced from its own invoice. |
| ON-ORDER rows with no order date | Entering the date. A row without one is reachable by no age. |
| Project orders no row names | Adding the ledger row, or setting `"project": false` with a `why`. |

An order's expected ledger sum is `total - nonproject_amount`, so an invoice
carrying household items alongside project ones closes by recording that amount.

## Verifying a bulk edit

An edit that moves fields between cells leaves every section total and the grand
total where they were.

```bash
python3 hardware/scripts/_ledger_totals.py > /tmp/before.txt
# ... the edit ...
python3 hardware/scripts/_ledger_totals.py > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt
```

A price, quantity, or status cell altered by accident moves a total, and the
diff names the section it happened in.
