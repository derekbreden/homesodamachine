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
  * --audit reads each row's arithmetic back. THE UNIT COLUMN IS A DISPLAY:
    it holds two decimals, and a row whose true per-unit price has more of
    them bills a line that column cannot reproduce — 32 spade terminals at
    $10.71/60 are $0.1785 each, printed $0.18, and 32 × $0.18 is $5.76
    against a right line of $5.71. So the audit prices each row off the rate
    ITS OWN NOTES STATE — the last `$x/ea`, `/ft`, `/in`, … in that cell —
    and falls back to the printed column wherever the notes state none, or
    state one no finer than the column already shows.
    What it allows is the rounding band of whichever figure it priced from,
    `qty × half-ulp + half a cent`, so a line that closes at full precision
    is silent and a line that does not is a finding. The rows where the
    two-decimal column alone will not multiply out are listed apart, under
    the display note they are — nothing to order differently, nothing to fix.

Run:  python3 hardware/scripts/_bom_totals.py            # recompute + write markers
      python3 hardware/scripts/_bom_totals.py --audit     # + flag rows whose line does not close
      python3 hardware/scripts/_bom_totals.py --check     # exit 1 if a marker is stale
      python3 hardware/scripts/_bom_totals.py --selftest  # known-answer rows, both buckets
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOM = os.path.join(HERE, "..", "ledger", "bom.md")

from pathlib import Path  # noqa: E402
sys.path.insert(
    0, str(next(p for p in Path(HERE).resolve().parents
                if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import cells, substitute_md  # noqa: E402

MONEY = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
NUM = re.compile(r"-?[0-9][0-9,]*(?:\.[0-9]+)?")
# The audit's own money, which reads past two decimals: the Unit column carries
# $2.134 where a bag price divides that way, and truncating it to $2.13 invents
# a three-cent gap on a six-off line that is exactly right.
CASH = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)")
# A rate for ONE of whatever the Qty column counts. `/build`, `/unit` and `/bag`
# are deliberately not in it — those price a whole build or a whole pack, which
# is the Line and the pack, not the Unit. The CARGEN foam row states both
# ("$8.14/roll = $0.113/in × 84" = $9.50/build") and only the middle one is a unit.
PER = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)\s*/\s*"
                 r"(?:ea|each|pc|ft|in|m|board|roll|plate|stick)\b")


def money(cell):
    m = MONEY.search(cell)
    return float(m.group(1).replace(",", "")) if m else 0.0


def figure(text, pat=CASH):
    """The LAST money figure `pat` finds, as `(value, decimals as printed)`.

    Last, because a row states its pre-overhead price before its delivered one
    ("$2.134/ea + 33.46% allocated order overhead = $2.848/ea") and the
    delivered one is what the line bills.
    """
    m = None
    for m in pat.finditer(text):
        pass
    if m is None:
        return None
    s = m.group(1).replace(",", "")
    return float(s), (len(s.split(".")[1]) if "." in s else 0)


def reading(notes, qty_cell, unit_cell, line_cell):
    """What a row's own columns say its line should be, or None if it prices nothing.

    `(line, want, slack, printed_want)` — `want` off the full-precision rate the
    row states, `slack` that rate's own rounding band plus the line's half cent,
    `printed_want` off the two-decimal column, which is the display and not the
    price.

    A stated rate is only read as the price when it carries MORE decimals than
    the column, because that is the whole case: the column is a lossy display of
    it. A rate stated at the column's own precision is already in the column, so
    a different one beside it is a different fact — the GASHER check's pre-tax
    "$7.00/ea + tax ≈ $7.48 delivered", the DS18S20's second-source "$9.30/ea
    landed" — and reading either as this row's unit invents a finding.
    """
    qm = NUM.search(qty_cell.replace(",", ""))
    printed = figure(unit_cell)
    line = money(line_cell)
    if not (qm and printed and line):
        return None
    qty = float(qm.group(0))
    stated = figure(notes, PER)
    price, dec = stated if stated and stated[1] > printed[1] else printed
    return line, qty * price, qty * 0.5 * 10 ** -dec + 0.005, qty * printed[0]


def parse():
    sums, section, audit, notes = {}, None, [], []
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
        sums[section] = sums.get(section, 0.0) + money(c[-1])
        if len(c) >= 5 and "--audit" in sys.argv:
            r = reading(c[1], c[-3], c[-2], c[-1])
            if r is None:
                continue
            line, want, slack, printed_want = r
            where = f"  §{section} {c[0][:46]}"
            if abs(want - line) > slack:
                audit.append(f"{where}: line ${line:.2f}, its own rate gives ${want:.2f}")
            elif abs(printed_want - line) > 0.005:
                notes.append(f"{where}: line ${line:.2f}, printed unit × qty ${printed_want:.2f}")
    return sums, audit, notes


def main():
    sums, audit, notes = parse()
    grand = sum(sums.values())

    def fmt(v):
        return f"${v:,.2f}"
    variables = {f"BOM_SEC{n}": fmt(v) for n, v in sums.items()}
    variables["BOM_GRAND"] = fmt(grand)

    # --check compares the markers with the row sums without rewriting them.
    if "--check" in sys.argv:
        text = open(BOM, encoding="utf-8").read()
        stale = [f"  [{m.group(1)}]({name}) should be [{v}]({name})"
                 for name, v in variables.items()
                 for m in [re.search(r"\[([^\]]*)\]\(%s\)" % name, text)]
                 if m and m.group(1) != v]
        if stale:
            print("bom.md totals are stale — run _bom_totals.py:")
            print("\n".join(stale))
            return 1
        print("bom.md totals ✓")
        return 0

    substitute_md(BOM, variables)

    for n in sorted(sums):
        print(f"  §{n:<2} {fmt(sums[n]):>10}")
    print(f"  {'GRAND':<3} {fmt(grand):>10}")
    if "--audit" in sys.argv:
        if audit:
            print("\nthe line does not close against the row's own rate:")
            print("\n".join(audit))
        if notes:
            print(f"\ndisplay only — the two-decimal Unit column will not multiply out "
                  f"({len(notes)} rows; every line below is right):")
            print("\n".join(notes))
        if not audit:
            print("\nevery priced row closes against its own rate ✓")
    return 0


# --- controls -----------------------------------------------------------------
#
# The two buckets, held apart on rows this file bills.

def selftest():
    """Known answers: a line that closes at full precision, and one that does not."""
    out = []

    def close(notes, qty, unit, line, why):
        r = reading(notes, qty, unit, line)
        assert r, why
        assert abs(r[1] - r[0]) <= r[2], f"{why}: ${r[0]:.2f} vs ${r[1]:.4f} ± {r[2]:.4f}"
        return r

    def broken(notes, qty, unit, line, why):
        r = reading(notes, qty, unit, line)
        assert r, why
        assert abs(r[1] - r[0]) > r[2], f"{why}: ${r[0]:.2f} vs ${r[1]:.4f} ± {r[2]:.4f}"
        return r

    # 32 spade terminals out of a 60-pack: $10.71/60 is $0.1785, printed $0.18,
    # and 32 × $0.18 = $5.76 against a line of $5.71 that is exactly right.
    r = close("$10.71/60 = $0.1785/ea", "32 (of 60 pk)", "$0.18", "$5.71 <!--@wiring-->",
              "the display's half cent is not an error")
    assert abs(r[3] - r[0]) > 0.005, "and the printed column is what will not multiply out"
    out.append("  a two-decimal Unit column that will not multiply out is a display note")

    # 61 inserts at $0.1071 is $6.53. A line of $7.18 is 67 of them, a quantity
    # the row's own marker does not carry and an order for six too many.
    broken("$10.71 ÷ 100 = $0.1071/ea", "[61](TOTAL_M3_INSERTS) (of 100 pk)", "$0.11",
           "$7.18 <!--@fasteners-->", "a line billing more inserts than the box takes")
    close("$10.71 ÷ 100 = $0.1071/ea", "[61](TOTAL_M3_INSERTS) (of 100 pk)", "$0.11",
          "$6.53 <!--@fasteners-->", "the same row at the count the box takes")
    out.append("  a line the row's own rate will not reach is a finding")

    # No rate stated: the printed column IS the price, and its own band is the slack.
    close("foam-pour consumable; $7.50/100 × 4", "4 (of 100 pk)", "$0.08",
          "$0.30 <!--@consumables-->", "the printed column priced at its own precision")
    out.append("  a row stating no rate is priced off the column, at the column's precision")

    # A rate per foot against a Qty in feet.
    close("$38.29/125 ft = $0.306/ft; ~14 ft/build", "~14 ft", "$0.31/ft",
          "$4.29 <!--@wiring-->", "a per-foot rate against a Qty in feet")
    out.append("  a /ft rate prices a Qty in ft")

    # The LAST rate wins: delivered, not pre-overhead.
    close("pack of 10 @ $21.34 = $2.134/ea + 33.46% allocated order overhead = $2.848/ea",
          "4 (of 10 pk)", "$2.85", "$11.39 <!--@plumbing-->", "the delivered rate, not the first")
    out.append("  the last rate in the notes is the delivered one, and the one that bills")

    # /build is not a unit — the CARGEN foam row states it right beside the one that is.
    close("$16.28 ÷ 2 = $8.14/roll = $0.113/in × 84\" = $9.50/build", "~84\" (of 72\" roll)",
          "$0.113/in", "$9.50 <!--@insulation-->", "a per-inch rate, not the per-build total")
    out.append("  /build prices a build, so it is never read as a unit")

    # A two-decimal rate in the notes is not a finer reading of a two-decimal
    # column — it is the pre-tax price standing next to the delivered one.
    close("Prime, ships from Amazon; $7.00/ea + tax ≈ $7.48 delivered", "1 (of 2)", "$7.50",
          "$7.50 <!--@plumbing-->", "a pre-tax rate is not this row's unit")
    out.append("  a rate no finer than the column is a different fact, not a finer one")

    # A row with no money in the Unit column prices nothing and is not audited.
    assert reading("~45 collars/build", "~45 collars", "—", "$1.25 <!--@wiring-->") is None
    out.append("  a row with no Unit price is not a row with a wrong one")

    return out


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        for _line in selftest():
            print(_line)
        print("_bom_totals selftest OK")
        sys.exit(0)
    sys.exit(main())
