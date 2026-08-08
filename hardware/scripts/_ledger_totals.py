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

Run:  python3 hardware/scripts/_ledger_totals.py           # rewrite + summary
      python3 hardware/scripts/_ledger_totals.py --check   # exit 1 if a marker is stale
      python3 hardware/scripts/_ledger_totals.py --audit   # + ambiguous-row report

--check is the commit gate (.githooks/pre-commit, keyed on purchases.md) and it
WRITES NOTHING. A driver that rewrites under --check cannot fail, so the one
instrument that would catch a stale total would report success instead — which
is how the grand total came to understate cash outlay by a whole PCBA batch.
"""
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
from docgen import substitute_md  # noqa: E402

EXCLUDE_SECTIONS = {"Totals"}
STATUS_KEYWORDS = ("ACQUIRED", "ON-ORDER", "LIKELY-TO-BUY", "MISSING",
                   "NOT NEEDED", "alt option")
PRICE = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")


def cells(row):
    parts = row.split("|")
    if parts and parts[0].strip() == "":
        parts = parts[1:]
    if parts and parts[-1].strip() == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def first_price(cell):
    m = PRICE.search(cell)
    return float(m.group(1).replace(",", "")) if m else None


def lead_int(cell):
    m = re.match(r"\s*([0-9]+)", cell)
    return int(m.group(1)) if m else None


def parse(path):
    status_totals, section_acq, labor = {}, {}, 0.0
    ambiguous, section = [], "(preamble)"
    for ln in open(path).read().splitlines():
        if ln.startswith("## "):
            section = ln[3:].strip()
            continue
        if not ln.startswith("|") or section in EXCLUDE_SECTIONS:
            continue
        c = cells(ln)
        if len(c) < 2 or set("".join(c)) <= set("-: "):
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
    return status_totals, section_acq, labor, ambiguous


def main():
    st, sec, labor, amb = parse(LEDGER)
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
        if stale:
            print("purchases.md totals are stale — run _ledger_totals.py:")
            print("\n".join(stale))
            return 1
        print("purchases.md totals ✓")
        return 0

    substitute_md(LEDGER, variables, {k: 1 for k in variables})

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
