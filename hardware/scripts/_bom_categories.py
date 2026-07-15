#!/usr/bin/env python3
"""BOM cost-category taxonomy — the single source of truth for the part-TYPE
categories that cut ACROSS the subsystem sections of bom.md.

bom.md is organised by subsystem (§1 electronics, §2 vessel, …) because that's how
the assembly docs navigate it. This file is the orthogonal view: what KIND of thing
each line is (a sensor, a fitting, a printed part), for cost analysis.

Each data row in bom.md carries a hidden tag `<!--@TAG-->` in its last cell — it
renders invisibly and travels with the row, so there is no second file to keep in
sync. This script owns the category set, rolls the per-unit costs up by category,
and validates that every data row is tagged (the pre-commit hook runs `--check`, so
the tags cannot silently drift as rows are added or edited).

  python3 hardware/scripts/_bom_categories.py            # category subtotals
  python3 hardware/scripts/_bom_categories.py --list      # + every line under its category
  python3 hardware/scripts/_bom_categories.py --check     # exit 1 if any row is untagged / mis-tagged

To add a category: add it here. To re-file a line: change its `<!--@TAG-->`.
"""
import os
import re
import sys
from collections import defaultdict

BOM = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ledger", "bom.md")

# tag -> display name.  Order is the canonical listing order.
CATEGORIES = {
    "sensors":        "Sensors",
    "wiring":         "Wires & wire connectors",
    "plumbing":       "Tubes, connectors, adapters & safety",
    "solenoid-valves": "Solenoid valves",
    "pumps":          "Pumps",
    "electronics":    "Electronics",
    "printed":        "FDM printed parts",
    "cut-parts":      "SendCutSend cut parts",
    "pipes":          "Pipes",
    "refrigeration":  "Refrigeration",
    "water-filter":   "Water filter",
    "insulation":     "Insulation & foam",
    "faucet":         "Faucet",
    "fasteners":      "Fasteners",
    "consumables":    "Fab consumables",
    "funnel-casting": "Flavor-funnel casting",
    "ac-mains":       "AC-mains hardware",
    "carbonation":    "Carbonation (sparge stone)",
    "cable-mgmt":     "Cable management",
    "vent-filter":    "Vent filter",
    "welding":        "Welding filler",
    "install-tool":   "Install-kit tool",
}

TAG = re.compile(r"<!--@([a-z][a-z-]*)-->")
MONEY = re.compile(r"\$\s?([0-9][0-9,]*(?:\.[0-9]{1,2})?)")


def _money(cell):
    m = MONEY.search(cell)
    return float(m.group(1).replace(",", "")) if m else 0.0


def data_rows():
    """Yield (section, name, line_cost, [tags]) for every per-unit BOM data row —
    the same row set _bom_totals.py sums (numbered sections only; header /
    separator / totals rows skipped)."""
    section = None
    for ln in open(BOM, encoding="utf-8").read().splitlines():
        if ln.startswith("## "):
            m = re.match(r"## (\d+)\.", ln)
            section = int(m.group(1)) if m else None
            continue
        if section is None or not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip("|").split("|")]
        if not cells or all(set(x) <= set("-: ") for x in cells):   # separator row
            continue
        first = cells[0].replace("*", "").strip().lower()
        if first == "part" or "total" in first:                      # header / totals row
            continue
        yield section, cells[0], _money(cells[-1]), TAG.findall(ln)


def check():
    rows = list(data_rows())
    problems = []
    for sec, name, cost, tags in rows:
        nm = re.sub(r"\]\(.*?\)", "]", name)[:58]
        if not tags:
            problems.append(f"§{sec} UNTAGGED: {nm}")
        elif len(tags) > 1:
            problems.append(f"§{sec} MULTIPLE tags {tags}: {nm}")
        elif tags[0] not in CATEGORIES:
            problems.append(f"§{sec} UNKNOWN tag {tags[0]!r}: {nm}")
    if problems:
        print("BOM category-tag drift — every data row needs exactly one known <!--@TAG-->:", file=sys.stderr)
        for p in problems:
            print("  ✗ " + p, file=sys.stderr)
        print("\nKnown tags: " + ", ".join(CATEGORIES), file=sys.stderr)
        sys.exit(1)
    print(f"✓ all {len(rows)} BOM data rows carry a known category tag")


def rollup(show_list):
    rows = list(data_rows())
    sums, counts, members = defaultdict(float), defaultdict(int), defaultdict(list)
    for sec, name, cost, tags in rows:
        t = tags[0] if tags else "UNTAGGED"
        sums[t] += cost
        counts[t] += 1
        members[t].append((sec, cost, name))
    grand = sum(sums.values())
    for t in sorted(sums, key=lambda k: -sums[k]):
        print(f"  {CATEGORIES.get(t, t):37} ${sums[t]:8.2f}  {sums[t] / grand * 100:5.1f}%  ({counts[t]})")
        if show_list:
            for sec, cost, name in sorted(members[t], key=lambda x: -x[1]):
                nm = re.sub(r"[\[\]]", "", re.sub(r"\]\(.*?\)", "]", name))
                print(f"        §{sec:>2} ${cost:7.2f}  {nm[:64]}")
    print(f"  {'-' * 37} ${grand:8.2f}   per-unit total")


def main():
    if "--check" in sys.argv:
        check()
    else:
        rollup("--list" in sys.argv)


if __name__ == "__main__":
    main()
