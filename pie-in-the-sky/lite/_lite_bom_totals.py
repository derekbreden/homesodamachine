#!/usr/bin/env python3
"""Compute the Lite edition's estimated delivered parts cost per unit from the
BOM table and write it into the LITE_TOTAL [value](NAME) marker — so it tracks
the table instead of being hand-summed (or, today, missing entirely).

Per row: line = qty × unit price. Unit prices written "$X/ft" are multiplied by
the foot count in the Qty cell; plain "$X" by the integer count. A "—" unit
(shared-stock stub) counts as $0. The CO2 tank, flavor concentrate, and shared
consumables are external/user-supplied and excluded (as the table already is).

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


def main():
    total = 0.0
    in_table = False
    for ln in open(BOM, encoding="utf-8").read().splitlines():
        # Only the first table (the parts list) has the Qty/Unit columns.
        if ln.startswith("## "):
            in_table = False
        if ln.startswith("| Subsystem |"):
            in_table = True
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
        total += float(qty_m.group(0).replace(",", "")) * float(price_m.group(1).replace(",", ""))

    substitute_md(BOM, {"LITE_TOTAL": f"${total:,.2f}"}, {"LITE_TOTAL": 1})
    print(f"  LITE_TOTAL  ${total:,.2f}")


if __name__ == "__main__":
    main()
