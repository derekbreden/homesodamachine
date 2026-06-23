#!/usr/bin/env python3
"""Maintain the Lite edition BOM's per-row Line cost + per-subsystem totals.

For each parts-table row it computes Line = Qty × Unit and writes it into a
"Line" column (inserting the column after "Unit" the first time it runs), so
every row shows its own delivered cost — no mental math. Unit prices written
"$X/ft" are multiplied by the foot count in the Qty cell; plain "$X" by the
integer count; a "—" unit (shared-stock stub) shows "—" and counts as $0.

Rows then roll up by their Subsystem (first column) into the LITE_<SUBSYSTEM>
markers, and the lot into LITE_TOTAL, in the Totals table. Each subtotal is the
sum of the per-row Line cells (each rounded to the cent), so the visible Line
column adds up to the visible subtotal, and the subtotals to the grand total.

Only the first table (the parts list) is touched; the Totals / Clear-PVC tables
after it are passed through unchanged.

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

# Split-index of the Line cell. `"| a | b |".split("|")` keeps a leading "" at
# index 0, so the columns are Subsystem=1, Item=2, Qty=3, Unit=4, then Line=5
# (inserted just after Unit, before Source/Notes).
LINE_COL = 5


def main():
    raw = open(BOM, encoding="utf-8").read().splitlines()
    out = []
    sums = {}
    state = "pre"
    col_existed = False
    expected = 8  # incoming cell count for a 6-column row (2 empty sentinels)
    for ln in raw:
        if state == "pre":
            if ln.startswith("| Subsystem |"):
                cells = ln.split("|")
                col_existed = "Line" in [c.strip() for c in cells]
                expected = 9 if col_existed else 8
                if not col_existed:
                    cells.insert(LINE_COL, " Line ")
                out.append("|".join(cells))
                state = "sep"
            else:
                out.append(ln)
            continue
        if state == "sep":
            cells = ln.split("|")
            if not col_existed:
                cells.insert(LINE_COL, "---:")
            out.append("|".join(cells))
            state = "rows"
            continue
        if state == "rows":
            if not ln.startswith("|") or set(ln) <= set("|-: "):
                out.append(ln)
                state = "post"
                continue
            cells = ln.split("|")
            if len(cells) != expected:  # malformed row — leave it untouched
                out.append(ln)
                continue
            qty_m = NUM.search(cells[3])
            price_m = MONEY.search(cells[4])
            if qty_m and price_m:
                line = round(
                    float(qty_m.group(0).replace(",", ""))
                    * float(price_m.group(1).replace(",", "")), 2)
                cell = f" ${line:,.2f} "
                sub = cells[1].strip()
                sums[sub] = sums.get(sub, 0.0) + line
            else:
                cell = " — "  # "—" unit (shared-stock stub): no line, $0
            if col_existed:
                cells[LINE_COL] = cell
            else:
                cells.insert(LINE_COL, cell)
            out.append("|".join(cells))
            continue
        out.append(ln)  # state == "post"

    open(BOM, "w", encoding="utf-8").write("\n".join(out) + "\n")

    unmapped = set(sums) - set(MARKERS)
    if unmapped:
        raise SystemExit(
            f"Lite BOM has subsystem(s) with no Totals-table marker: {sorted(unmapped)} "
            "— add a row + marker to the Totals table and MARKERS.")

    grand = round(sum(sums.values()), 2)
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
