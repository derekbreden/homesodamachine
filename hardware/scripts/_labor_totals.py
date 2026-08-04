#!/usr/bin/env python3
"""Compute labor.md per-unit attended-minute subtotals + grand totals from the
two minute columns and write them into the [value](NAME) docgen markers — so a
row can be added, split or re-estimated without anyone re-adding a column.
The dollar-side companion is _bom_totals.py; this owns the TIME rollups.

  * Each section's subtotal = the column sums of its data rows. The two minute
    columns are the last two cells: Groove (2nd-last), Today (last). Header
    rows, separators, and the bold inline subtotal row are skipped.
  * Markers: LAB_G_SEC1..9 / LAB_T_SEC1..9 (each section's inline subtotal row
    AND the Totals table), LAB_G_GRAND / LAB_T_GRAND (minutes),
    LAB_G_HOURS / LAB_T_HOURS, LAB_RATIO (Today ÷ Groove), BATCH_SIZE.

Run:  python3 hardware/scripts/_labor_totals.py           # recompute + write markers
      python3 hardware/scripts/_labor_totals.py --check    # exit 1 if a written
                                                           # marker is stale
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LABOR = os.path.join(HERE, "..", "ledger", "labor.md")

from pathlib import Path  # noqa: E402
sys.path.insert(
    0, str(next(p for p in Path(HERE).resolve().parents
                if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import substitute_md  # noqa: E402

# The build batch the Groove column amortizes per-batch setup across — the size
# the ledger already buys in (endcap plates 20 at a time = 10 vessels, tube 10
# at a time, PCBAs at the qty-10 price).
BATCH_SIZE = 10

MINUTES = re.compile(r"^\**\s*\[?([0-9][0-9,]*)\]?")


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def minutes(cell):
    """A minute cell → int. Reads through both the bold of a subtotal row and
    the [value](NAME) brackets of a docgen marker, so the parse never depends
    on what this script last wrote."""
    m = MINUTES.match(cell)
    return int(m.group(1).replace(",", "")) if m else 0


def parse():
    """{section: (groove, today)} over labor.md's numbered sections."""
    sums, section = {}, None
    for ln in open(LABOR, encoding="utf-8").read().splitlines():
        if ln.startswith("## "):
            m = re.match(r"## (\d+)\.", ln)
            section = int(m.group(1)) if m else None
            continue
        if section is None or not ln.startswith("|"):
            continue
        c = cells(ln)
        if len(c) < 2 or all(set(x) <= set("-: ") for x in c):     # separator
            continue
        first = c[0].strip()
        if first.lower() == "operation" or first.startswith("**"):  # header / subtotal
            continue
        g, t = sums.get(section, (0, 0))
        sums[section] = (g + minutes(c[-2]), t + minutes(c[-1]))
    return sums


def main():
    sums = parse()
    g_grand = sum(g for g, _ in sums.values())
    t_grand = sum(t for _, t in sums.values())

    variables = {"BATCH_SIZE": BATCH_SIZE}
    counts = {"BATCH_SIZE": 2}
    for n, (g, t) in sums.items():
        variables[f"LAB_G_SEC{n}"] = f"{g:,}"
        variables[f"LAB_T_SEC{n}"] = f"{t:,}"
        # Two sites each — the section's own subtotal row and the Totals table.
        # §6 and §8 are also cited by groove minutes in "Where the 10-hour
        # target is actually won", the two largest blocks.
        counts[f"LAB_G_SEC{n}"] = 3 if n in (6, 8) else 2
        counts[f"LAB_T_SEC{n}"] = 2
    variables["LAB_G_GRAND"] = f"{g_grand:,}"
    variables["LAB_T_GRAND"] = f"{t_grand:,}"
    variables["LAB_G_HOURS"] = f"{g_grand / 60:.1f}"
    variables["LAB_T_HOURS"] = f"{t_grand / 60:.1f}"
    variables["LAB_RATIO"] = f"{t_grand / g_grand:.1f}"
    counts.update({"LAB_G_GRAND": 1, "LAB_T_GRAND": 1,
                   "LAB_G_HOURS": 2, "LAB_T_HOURS": 2, "LAB_RATIO": 1})

    if "--check" in sys.argv:
        text = open(LABOR, encoding="utf-8").read()
        stale = [f"  [{m.group(1)}]({name}) should be [{v}]({name})"
                 for name, v in variables.items()
                 for m in [re.search(r"\[([^\]]*)\]\(%s\)" % name, text)]
                 if m and m.group(1) != str(v)]
        if stale:
            print("labor.md markers are stale — run _labor_totals.py:")
            print("\n".join(stale))
            return 1
        print("labor.md totals ✓")
        return 0

    substitute_md(LABOR, variables, counts)
    for n in sorted(sums):
        g, t = sums[n]
        print(f"  §{n}  groove {g:>5,} min   today {t:>6,} min   ×{t / g:.1f}")
    print(f"  ──  groove {g_grand:>5,} min   today {t_grand:>6,} min   ×{t_grand / g_grand:.1f}")
    print(f"      groove {g_grand / 60:>5.1f} h     today {t_grand / 60:>6.1f} h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
