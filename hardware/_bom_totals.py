#!/usr/bin/env python3
"""Compute bom.md per-unit subtotals + grand total from the line-cost column
and write them into the [value](NAME) docgen markers — so they're never
hand-summed again. Companion to _bom_sync.py (which owns the geometry-derived
QUANTITY markers); this owns the COST rollups.

  * Each section's subtotal = sum of the last ($) cell of its data rows.
    Header rows, separators, and inline subtotal/total rows are skipped.
    §12's subsection tables all roll into §12. A "—" line cost counts as $0.
  * Markers: BOM_SEC1..BOM_SEC14 (the Totals table; §7 also in its inline
    total row), BOM_GRAND (grand total per unit).

Run:  python3 hardware/_bom_totals.py            # recompute + write markers
      python3 hardware/_bom_totals.py --audit     # + flag rows where line$ != qty×unit$
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOM = os.path.join(HERE, "bom.md")

from pathlib import Path  # noqa: E402
sys.path.insert(
    0, str(next(p for p in Path(HERE).resolve().parents
                if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import substitute_md  # noqa: E402

MONEY = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
NUM = re.compile(r"-?[0-9][0-9,]*(?:\.[0-9]+)?")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def money(cell):
    m = MONEY.search(cell)
    return float(m.group(1).replace(",", "")) if m else 0.0


def parse():
    sums, section, audit = {}, None, []
    for ln in open(BOM, encoding="utf-8").read().splitlines():
        if ln.startswith("## "):
            m = re.match(r"## (\d+)\.", ln)
            section = int(m.group(1)) if m else None
            continue
        if section is None or not ln.startswith("|"):
            continue
        c = cells(ln)
        if not c or all(set(x) <= set("-: ") for x in c):
            continue
        first = c[0].replace("*", "").strip().lower()
        if first == "part" or "total" in first:
            continue
        line_cost = money(c[-1])
        sums[section] = sums.get(section, 0.0) + line_cost
        # audit: does line$ ≈ qty × unit$? (qty 3rd-last, unit 2nd-last, 5-col)
        if len(c) >= 5 and "--audit" in sys.argv:
            qm = NUM.search(c[-3].replace(",", ""))
            um = MONEY.search(c[-2])
            if qm and um and line_cost:
                want = float(qm.group(0).replace(",", "")) * float(um.group(1).replace(",", ""))
                if abs(want - line_cost) > 0.02:
                    audit.append(f"  §{section} {c[0][:46]}: line ${line_cost:.2f} vs qty×unit ${want:.2f}")
    return sums, audit


def main():
    sums, audit = parse()
    grand = sum(sums.values())

    def fmt(v):
        return f"${v:,.2f}"
    variables = {f"BOM_SEC{n}": fmt(v) for n, v in sums.items()}
    variables["BOM_GRAND"] = fmt(grand)
    counts = {k: 1 for k in variables}
    counts["BOM_SEC7"] = 2  # Totals table + §7's inline "Printed parts total"
    substitute_md(BOM, variables, counts)

    for n in sorted(sums):
        print(f"  §{n:<2} {fmt(sums[n]):>10}")
    print(f"  {'GRAND':<3} {fmt(grand):>10}")
    if "--audit" in sys.argv and audit:
        print("\nline$ != qty×unit$:")
        print("\n".join(audit))


if __name__ == "__main__":
    main()
