#!/usr/bin/env python3
"""Compute labor.md per-unit attended-minute subtotals + their dollar cost from
the minute column, and write them into the [value](NAME) docgen markers — so a
row can be added, split or re-estimated without anyone re-adding a column.
The parts-side companion is _bom_totals.py; this owns the TIME rollups.

  * Each section's subtotal = the sum of its data rows' minute cells (the last
    cell). Header rows, separators, and the bold inline subtotal row are
    skipped.
  * Every ESTIMATE must be one of INCREMENTS below — the steps a person actually
    estimates in. "40 minutes" claims a precision nobody has for work they have
    not timed: it means 30 or it means 45. --check rejects anything else, which
    is what keeps the convention from eroding one plausible-looking row at a
    time. Subtotals and totals are plain sums and land where they land.
  * Markers: LAB_SEC1..N (each section's inline subtotal row and the Totals
    table's minute figure feed off the same sum), LAB_HM1..N / LAB_USD1..N (the
    Totals table), LAB_HM / LAB_USD (per-unit total), LABOR_RATE, BATCH_SIZE.

Run:  python3 hardware/scripts/_labor_totals.py           # recompute + write markers
      python3 hardware/scripts/_labor_totals.py --check    # exit 1 on an
                                                           # off-ladder estimate
                                                           # or a stale marker
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

# The build batch the estimates amortize per-batch setup across — the size the
# ledger already buys in (endcap plates 20 at a time = 10 vessels, tube 10 at a
# time, PCBAs at the qty-10 price).
BATCH_SIZE = 10

# Dollars per hour of attended time. /cost reads this value back out of
# labor.md's [$100](LABOR_RATE) marker rather than carrying its own copy, so
# this line is the one place the rate is set.
LABOR_RATE = 100

# The believable-estimate ladder, in minutes. Fine at the bottom where a person
# can picture the operation, coarse at the top where they can't: 5-minute steps
# to half an hour, then 45m, then quarter-hours to two, then half-hours to
# three, then whole hours. An estimate that isn't on it is asking to be read as
# a measurement.
INCREMENTS = (5, 10, 15, 20, 25, 30, 45, 60, 75, 90, 105, 120, 150, 180, 240, 300, 360)

MINUTES = re.compile(r"^\**\s*\[?([0-9][0-9,]*)\]?")


def hm(mins):
    """Minutes → 'h m' the way a person says it: 45 m, 2 h, 1 h 15 m."""
    h, m = divmod(int(mins), 60)
    if not h:
        return f"{m} m"
    return f"{h} h" if not m else f"{h} h {m} m"


def usd(mins):
    return f"${mins / 60 * LABOR_RATE:,.2f}"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def minutes(cell):
    """A minute cell → int. Reads through both the bold of a subtotal row and
    the [value](NAME) brackets of a docgen marker, so the parse never depends
    on what this script last wrote."""
    m = MINUTES.match(cell)
    return int(m.group(1).replace(",", "")) if m else 0


def parse():
    """({section: minutes}, [off-ladder complaints]) over labor.md's numbered
    sections."""
    sums, offenders, section = {}, [], None
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
        v = minutes(c[-1])
        if v not in INCREMENTS:
            near = min(INCREMENTS, key=lambda i: (abs(i - v), i))
            offenders.append(f"  §{section} {first[:52]}: {v} min — say {hm(near)}")
        sums[section] = sums.get(section, 0) + v
    return sums, offenders


def main():
    sums, offenders = parse()
    grand = sum(sums.values())

    variables = {"BATCH_SIZE": BATCH_SIZE, "LABOR_RATE": f"${LABOR_RATE:,}"}
    counts = {"BATCH_SIZE": 1, "LABOR_RATE": 2}
    for n, v in sums.items():
        variables[f"LAB_SEC{n}"] = f"{v:,}"
        variables[f"LAB_HM{n}"] = hm(v)
        variables[f"LAB_USD{n}"] = usd(v)
        counts[f"LAB_SEC{n}"] = 1        # the section's own subtotal row
        counts[f"LAB_USD{n}"] = 1        # the Totals table
        # The Totals table, plus §6 and §8 cited in "where the next jig pays".
        counts[f"LAB_HM{n}"] = 2 if n in (6, 8) else 1
    variables["LAB_HM"] = hm(grand)
    variables["LAB_USD"] = usd(grand)
    counts.update({"LAB_HM": 2, "LAB_USD": 1})

    if "--check" in sys.argv:
        if offenders:
            print("labor.md estimates off the increment ladder:")
            print("\n".join(offenders))
            return 1
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
        print(f"  §{n:<2} {hm(sums[n]):>10}   {usd(sums[n]):>10}")
    print(f"  ── {hm(grand):>10}   {usd(grand):>10}")
    if offenders:
        print("\noff the increment ladder:")
        print("\n".join(offenders))
    return 0


if __name__ == "__main__":
    sys.exit(main())
