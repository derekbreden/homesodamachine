#!/usr/bin/env python3
"""Compute purchases.md totals from the table rows — so they never have to be
hand-tallied (or hand-verified) again.

Convention:
  * A row's cash outlay is the $ in its price cell. If the price cell ends in
    "ea", it is multiplied by the leading integer of the Qty cell.
  * Rows are bucketed by the status keyword in their last cell
    (ACQUIRED / ON-ORDER / MISSING / LIKELY-TO-BUY / alt option / NOT NEEDED).
  * The "Totals" block (the summary itself) is excluded from the row sums.
  * §18 (capitalized contract labor) has no status column; its rows are summed
    separately as `labor`.
  * A row's Order # cells join it to purchases.orders.json, the as-scraped
    Amazon record: order date, delivery date, and what the invoice charged.

Run:  python3 hardware/scripts/_ledger_totals.py           # rewrite + summary
      python3 hardware/scripts/_ledger_totals.py --check   # exit 1 on a stale
                                                           #   marker, an order
                                                           #   whose rows miss
                                                           #   its invoice, or a
                                                           #   stale ON-ORDER row
      python3 hardware/scripts/_ledger_totals.py --audit   # + the rows and orders
                                                           #   that need a person

--check writes nothing. A driver that rewrites under --check cannot fail, so the
one instrument that catches a stale total would report success instead.
"""
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "..", "ledger", "purchases.md")

# Import the repo's docgen so the computed figures can be written straight
# back into purchases.md's [value](NAME) markers (same path shim _bom_sync.py
# uses). The totals are never hand-edited — this script owns them.
from pathlib import Path  # noqa: E402
sys.path.insert(
    0, str(next(p for p in Path(HERE).resolve().parents
                if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import cells, substitute_md  # noqa: E402

ORDERS = os.path.join(HERE, "..", "ledger", "purchases.orders.json")

EXCLUDE_SECTIONS = {"Totals"}
STATUS_KEYWORDS = ("ACQUIRED", "ON-ORDER", "LIKELY-TO-BUY", "MISSING",
                   "NOT NEEDED", "alt option")
PRICE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
ORDER_NO = re.compile(r"\b\d{3}-\d{7}-\d{7}\b")
ISO = re.compile(r"(\d{4})-(\d{2})-(\d{2})")
EM = "—"
STALE_ON_ORDER_DAYS = 45
RECONCILE_TOLERANCE = 0.011


def first_price(cell):
    m = PRICE.search(cell)
    return float(m.group(1).replace(",", "")) if m else None


def lead_int(cell):
    m = re.match(r"\s*([0-9]+)", cell)
    return int(m.group(1)) if m else None


def parse(path):
    status_totals, section_acq, labor = {}, {}, 0.0
    ambiguous, section, rows, colmap = [], "(preamble)", [], {}
    for ln in open(path).read().splitlines():
        if ln.startswith("## "):
            section, colmap = ln[3:].strip(), {}
            continue
        if not ln.startswith("|") or section in EXCLUDE_SECTIONS:
            continue
        c = cells(ln)
        if len(c) < 2 or set("".join(c)) <= set("-: "):
            continue
        # Header row, naming this table's columns. The order date is "Ordered"
        # in the Amazon sections and "Order date" in §§15-17 and 20.
        if "Status" in c and ("$" in c or "Item" in c or "Contents" in c):
            colmap = {name: i for i, name in enumerate(c)}
            continue
        # §18 labor has no status column; sum its data rows (skip header +
        # the bolded subtotal row).
        if section.startswith("18."):
            joined = " ".join(c).lower()
            if "subtotal" not in joined and not c[0].lower().startswith("date range"):
                p = first_price(c[-1])
                if p:
                    labor += p
            continue
        status = status_idx = None
        for i in range(len(c) - 1, -1, -1):
            for kw in STATUS_KEYWORDS:
                if kw in c[i]:
                    status, status_idx = kw, i
                    break
            if status:
                break
        if status is None:
            continue
        dollar_cell = dollar_idx = None
        for i in range(status_idx - 1, -1, -1):
            if "$" in c[i]:
                dollar_cell, dollar_idx = c[i], i
                break
        if dollar_cell is None:
            ambiguous.append((status, "no-price", " | ".join(c)[:88]))
            continue
        price = first_price(dollar_cell)
        if price is None:
            continue
        cost, toks = price, dollar_cell.split()
        if toks and toks[-1] == "ea":
            qty = lead_int(c[dollar_idx - 1]) if dollar_idx else None
            if qty is None:
                ambiguous.append((status, f"ea-no-qty (${price})", " | ".join(c)[:70]))
            else:
                cost = price * qty
                ambiguous.append((status, f"ea {qty}×{price}={cost:.2f}", " | ".join(c)[:60]))
        status_totals[status] = status_totals.get(status, 0.0) + cost
        if status == "ACQUIRED":
            section_acq[section] = section_acq.get(section, 0.0) + cost

        def col(*names):
            for n in names:
                i = colmap.get(n)
                if i is not None and i < len(c) and c[i] not in ("", EM):
                    return c[i]
            return ""

        rows.append({
            "section": section, "status": status, "cost": cost,
            "orders": ORDER_NO.findall(col("Order #")),
            "ordered": col("Ordered", "Order date"),
            "delivered": col("Delivered"),
            "part": c[0][:64],
        })
    return status_totals, section_acq, labor, ambiguous, rows


def load_orders():
    with open(ORDERS, encoding="utf-8") as f:
        return json.load(f)["orders"]


def days_since(iso_date, today):
    m = ISO.match(iso_date or "")
    if not m:
        return None
    d = datetime.date(*(int(g) for g in m.groups()))
    return (today - d).days


def reconcile_orders(rows, orders):
    """Each order's ledger rows against what its invoice charged."""
    grouped = {}
    for r in rows:
        if r["status"] in ("ACQUIRED", "ON-ORDER", "MISSING"):
            for o in set(r["orders"]):
                grouped.setdefault(o, []).append(r)

    mismatch, unverifiable, split = [], [], []
    for order_no, group in sorted(grouped.items()):
        if any(len(set(r["orders"])) > 1 for r in group):
            split.append(order_no)
            continue
        inv = orders.get(order_no)
        if inv is None or inv.get("total") is None:
            unverifiable.append((order_no, sum(r["cost"] for r in group)))
            continue
        charged = inv["total"] - (inv.get("nonproject_amount") or 0.0)
        allocated = sum(r["cost"] for r in group)
        if abs(allocated - charged) > RECONCILE_TOLERANCE:
            mismatch.append((order_no, allocated, charged, len(group)))
    return mismatch, unverifiable, split


def stale_on_order(rows, today):
    aged, undated = [], []
    for r in rows:
        if r["status"] != "ON-ORDER":
            continue
        n = days_since(r["ordered"], today)
        if n is None:
            undated.append(r)
        elif n >= STALE_ON_ORDER_DAYS:
            aged.append((n, r))
    aged.sort(reverse=True)
    return aged, undated


def unrecorded_orders(rows, orders):
    named = {o for r in rows for o in r["orders"]}
    return sorted((k, v) for k, v in orders.items()
                  if v.get("project") is not False and k not in named)


def main():
    st, sec, labor, amb, rows = parse(LEDGER)
    orders = load_orders()
    today = datetime.date.today()
    mismatch, unverifiable, split = reconcile_orders(rows, orders)
    aged, undated = stale_on_order(rows, today)
    acq = st.get("ACQUIRED", 0.0)
    onorder = st.get("ON-ORDER", 0.0)
    missing = st.get("MISSING", 0.0)

    # Write the figures back into purchases.md's [value](NAME) markers.
    def money(v):
        return f"${v:,.2f}"
    variables = {
        "LEDGER_ACQUIRED_HW": money(acq),
        "LEDGER_LABOR": money(labor),
        "LEDGER_ACQUIRED_COMBINED": money(acq + labor),
        "LEDGER_ON_ORDER": money(onorder),
        "LEDGER_MISSING": money(missing),
        "LEDGER_GRAND_TOTAL": money(acq + labor + onorder + missing),
    }
    for title, v in sec.items():
        m = re.match(r"(\d+)", title)
        if m:
            variables[f"LEDGER_SEC{m.group(1)}"] = money(v)
    if "--check" in sys.argv:
        text = open(LEDGER, encoding="utf-8").read()
        stale = [f"  [{m.group(1)}]({name}) should be [{v}]({name})"
                 for name, v in variables.items()
                 for m in [re.search(r"\[([^\]]*)\]\(%s\)" % name, text)]
                 if m and m.group(1) != v]
        rc = 0
        if stale:
            print("purchases.md totals are stale — run _ledger_totals.py:")
            print("\n".join(stale))
            rc = 1
        else:
            print("purchases.md totals ✓")
        for order_no, allocated, charged, n in mismatch:
            print(f"  {order_no}: {n} row(s) allocate ${allocated:,.2f}, "
                  f"invoice charged ${charged:,.2f} "
                  f"(off by ${charged - allocated:+,.2f})")
            rc = 1
        if not mismatch:
            print(f"per-order allocation ✓ ({len(rows)} rows)")
        for n, r in aged:
            print(f"  ON-ORDER {n} days (ordered {r['ordered']}): {r['part']}")
            rc = 1
        if not aged:
            print(f"no ON-ORDER row past {STALE_ON_ORDER_DAYS} days ✓")
        return rc

    substitute_md(LEDGER, variables)

    print("ACQUIRED by section:")
    for s, v in sec.items():
        print(f"  ${v:>10,.2f}  {s}")
    print()
    print(f"  ACQUIRED — hardware      ${acq:>11,.2f}")
    print(f"  ACQUIRED — labor (§18)   ${labor:>11,.2f}")
    print(f"  ACQUIRED — combined      ${acq + labor:>11,.2f}")
    print(f"  ON-ORDER                 ${onorder:>11,.2f}")
    print(f"  MISSING (paid, unrecv'd) ${missing:>11,.2f}")
    print(f"  GRAND TOTAL (cash out)   ${acq + labor + onorder + missing:>11,.2f}")
    if "--audit" in sys.argv:
        print("\nAmbiguous / multiplied / priceless rows:")
        for status, kind, txt in amb:
            print(f"  [{status:9s}] {kind:20s} | {txt}")

        print("\nOrders a row names that no invoice covers:")
        for order_no, allocated in unverifiable:
            print(f"  {order_no}  ${allocated:,.2f} allocated")

        print("\nOrders shared by a row that names several, so no row's cost "
              "ties to one invoice:")
        for order_no in split:
            print(f"  {order_no}")

        print("\nON-ORDER rows with no order date, which no age can reach:")
        for r in undated:
            print(f"  [{r['section'][:24]:26s}] {r['part']}")

        print("\nProject orders no row names:")
        for order_no, inv in unrecorded_orders(rows, orders):
            flag = "" if inv.get("project") else "  (unclassified)"
            print(f"  {order_no}  {inv.get('ordered', '?')}  "
                  f"${inv.get('total') or 0:,.2f}{flag}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
