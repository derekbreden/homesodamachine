#!/usr/bin/env python3
"""BOM cost rollups and arithmetic audits, supplied by the Rust ledger reader."""
import re
import sys
from pathlib import Path
from _ledger_rust import call, main as _main

HERE = Path(__file__).resolve().parent
BOM = HERE.parent / 'ledger/bom.md'
MONEY = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")
NUM = re.compile(r"-?[0-9][0-9,]*(?:\.[0-9]+)?")
CASH = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)")
PER = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]+)?)\s*/\s*(?:ea|each|pc|ft|in|m|board|roll|plate|stick)\b")

def money(cell):
    return call('bom.money', text=cell)

def figure(text, pat=CASH):
    result = call('bom.figure', text=text, pattern=pat.pattern)
    return tuple(result) if result is not None else None

def reading(notes, qty_cell, unit_cell, line_cell):
    result = call('bom.reading', notes=notes, qty=qty_cell, unit=unit_cell, line=line_cell)
    return tuple(result) if result is not None else None

def parse():
    sums, audit, notes = call('bom.parse', bom=BOM, audit='--audit' in sys.argv)
    return {int(k):v for k,v in sums.items()}, audit, notes

def main():
    return _main('bom.main', bom=BOM, audit='--audit' in sys.argv, check='--check' in sys.argv)

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


if __name__ == '__main__':
    if '--selftest' in sys.argv:
        for line in selftest():
            print(line)
        print('_bom_totals selftest OK')
        sys.exit(0)
    sys.exit(main())
