#!/usr/bin/env python3
"""Compute the Lite edition's per-subsystem subtotals + grand total from the BOM
table and write them into the Totals-table [value](NAME) markers — so they track
the parts table instead of being hand-summed.

Per row: line = qty × unit price. Unit prices written "$X/ft" are multiplied by
the foot count in the Qty cell; plain "$X" by the integer count. A "—" unit
(shared-stock stub) counts as $0. Rows roll up by their Subsystem (first column)
into the LITE_<SUBSYSTEM> markers, and the lot into LITE_TOTAL. The CO2 tank,
flavor concentrate, and shared consumables are external/user-supplied and
excluded (as the table already is). Only the first table (the parts list) is
read; the Totals table after it is skipped.

Run:  python3 pie-in-the-sky/lite/_lite_bom_totals.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOM = os.path.join(HERE, "lite-bom.md")

from pathlib import Path  # noqa: E402
sys.path.insert(
    0, str(next(p for p in Path(HERE).resolve().parents
                if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import substitute_md  # noqa: E402

MONEY = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)")
NUM = re.compile(r"[0-9][0-9,]*(?:\.[0-9]+)?")


# Subsystem (first column of the parts table) → its Totals-table marker. Order
# is the Totals table's row order.
MARKERS = {
    "Flavor": "LITE_FLAVOR",
    "Faucet": "LITE_FAUCET",
    "Electronics": "LITE_ELECTRONICS",
    "Mechanical": "LITE_MECHANICAL",
    "Printed": "LITE_PRINTED",
    "Wiring": "LITE_WIRING",
    "Fasteners": "LITE_FASTENERS",
}


def main():
    sums = {}
    seen_table = False
    in_table = False
    for ln in open(BOM, encoding="utf-8").read().splitlines():
        # The parts list is the first table; stop at the first heading after it
        # (so the Totals table below — also `| Subsystem |`-ish — is not re-read).
        if ln.startswith("## "):
            if seen_table:
                break
            continue
        if ln.startswith("| Subsystem |"):
            in_table = True
            seen_table = True
            continue
        if not in_table or not ln.startswith("|") or set(ln) <= set("|-: "):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 4:
            continue
        qty_m = NUM.search(c[2])
        price_m = MONEY.search(c[3])
        if not qty_m or not price_m:
            continue  # e.g. the "—" shared-stub row
        line = float(qty_m.group(0).replace(",", "")) * float(price_m.group(1).replace(",", ""))
        sums[c[0]] = sums.get(c[0], 0.0) + line

    unmapped = set(sums) - set(MARKERS)
    if unmapped:
        raise SystemExit(
            f"Lite BOM has subsystem(s) with no Totals-table marker: {sorted(unmapped)} "
            "— add a row + marker to the Totals table and MARKERS.")

    grand = sum(sums.values())
    variables = {"LITE_TOTAL": f"${grand:,.2f}"}
    counts = {"LITE_TOTAL": 1}
    for sub, marker in MARKERS.items():
        variables[marker] = f"${sums.get(sub, 0.0):,.2f}"
        counts[marker] = 1
    substitute_md(BOM, variables, counts)

    for sub, marker in MARKERS.items():
        print(f"  {sub:<12} ${sums.get(sub, 0.0):>9,.2f}")
    print(f"  {'TOTAL':<12} ${grand:>9,.2f}")


if __name__ == "__main__":
    main()
