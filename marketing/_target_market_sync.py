"""Doc-sync driver for marketing/target-market.md.

Run: tools/cad-venv/bin/python marketing/_target_market_sync.py

THE PAGE STATES NO FIGURE OF ITS OWN. What a unit costs in parts, in attended hours, and in
printer time is derived where those things are counted — `hardware/ledger/bom.md`,
`labor.md`, `machine-time.md`, each with its own driver writing its own `.figures.json`. A
market document that retypes any of them is a fourth copy to go stale, and this page went
stale that way once already.

SO IT READS THE LEDGERS' OWN OUTPUT rather than re-deriving anything. `_bom_totals.py`,
`_labor_totals.py` and `_machine_time.py` run against their tables and write the sidecars;
this takes the figures out of those sidecars and substitutes them here. A ledger that moves
moves this page on its next run, and a marker this page names that no ledger writes stops the
run rather than publishing a blank.

THE PRICES ARE NOT DERIVED AND ARE NOT HERE. $7,500 and $5,500 are decisions, not readings,
and they are written in the prose where the decision lives. What is derived is what a unit
costs to build, which is the figure the prices are read against.
"""

import json
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
for _p in (_root / "tools",):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from docgen import substitute_md    # noqa: E402

MD = _here / "target-market.md"
LEDGER = _root / "hardware" / "ledger"

#: Every figure this page takes, and the ledger sidecar that derives it. The sidecar is keyed
#: by the driver that wrote it, so the name is looked up across the file's drivers rather than
#: under one — a figure that moves between drivers is still the same figure.
WANTED = {
    "BOM_GRAND": "bom",              # per-unit parts
    "LAB_HM": "labor",               # attended hours per unit
    "LAB_USD": "labor",              # those hours at the ledger's own rate
    "LABOR_RATE": "labor",
    "MT_H_PRINT": "machine-time",    # printer-hours per unit, both machines summed
    "MT_UNITS_YEAR": "machine-time", # what those hours give in a year at the ledger's duty
    "MT_DUTY": "machine-time",
}


def figures(stem: str) -> dict:
    """Every `[value](NAME)` a ledger's sidecar holds, flattened across its drivers."""
    path = LEDGER / f"{stem}.figures.json"
    if not path.exists():
        raise SystemExit(
            f"  {path.relative_to(_root)} is not there.\n"
            f"  target-market.md takes its figures from the ledgers; run that ledger's driver "
            f"first.")
    out = {}
    for by_driver in json.loads(path.read_text()).values():
        out.update(by_driver)
    return out


def main():
    read = {stem: figures(stem) for stem in set(WANTED.values())}

    variables = {}
    for name, stem in WANTED.items():
        if name not in read[stem]:
            raise SystemExit(
                f"  {stem}.figures.json no longer holds {name}, which target-market.md states.\n"
                f"  Either that ledger stopped deriving it, or the page is asking for a figure "
                f"nothing counts. Say which before this page tells a buyer either.")
        variables[name] = read[stem][name]

    # WHAT PARTS AND HANDS COME TO TOGETHER, which is the figure the two tier prices are read
    # against. Summed here rather than in either ledger: neither one owns the other's column,
    # and the sum is a claim this page makes and no other does.
    parts = float(variables["BOM_GRAND"].lstrip("$").replace(",", ""))
    hands = float(variables["LAB_USD"].lstrip("$").replace(",", ""))
    variables["UNIT_COST"] = f"${round(parts + hands, -2):,.0f}"

    substitute_md(MD, variables=variables)
    print(f"-> {MD.relative_to(_root)}")


if __name__ == "__main__":
    main()
