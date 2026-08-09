#!/usr/bin/env python3
"""Compute machine-time.md's print hours off bom.md §7's masses, roll up the
other machine processes, and write every derived figure into the [value](NAME)
docgen markers. Third of the ledger totals scripts, beside _bom_totals.py
(dollars) and _labor_totals.py (attended minutes) — this one owns HOURS A
MACHINE IS OCCUPIED, which is not costed and answers turnaround + throughput.

Why a script rather than typed numbers: the print estimate is a function of the
§7 masses, which are geometry-derived and commit-gated (_bom_masses.py). A part
that changes shape moves its mass, its print hours, the bottleneck's wall clock
and the units-per-year ceiling — all of it, without anyone remembering to.

  * Print hours = each §7 row's mass × its GROUP's hours-per-kg. Groups are the
    four print configurations the build uses; GROUP_OF assigns every row by
    name. --check fails on an unassigned row, so a new printed part cannot
    silently escape the estimate.
  * The §2/§3/§4 process tables are read, not computed — those are datasheet and
    procedure figures. Their subtotals are summed here.
  * The turnaround table is likewise read and summed, except for the print's own
    wall clock: this script writes that cell, so it carries the figure into the
    sum rather than reading it back off the page. One pass settles the file.

Run:  python3 hardware/scripts/_machine_time.py           # recompute + write markers
      python3 hardware/scripts/_machine_time.py --check    # exit 1 on an unassigned
                                                           # §7 row or a stale marker
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOM = os.path.join(HERE, "..", "ledger", "bom.md")
MT = os.path.join(HERE, "..", "ledger", "machine-time.md")

from pathlib import Path  # noqa: E402
sys.path.insert(
    0, str(next(p for p in Path(HERE).resolve().parents
                if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import substitute_md  # noqa: E402

PRINTERS = 2          # Bambu Lab H2C, tools.md
DUTY = 0.65           # machine duty — failed prints, plate changes, maintenance
HOURS_PER_YEAR = 24 * 365

# The one measured slice the whole print estimate stands on: the cold-core inner
# shell, 1142.47 g in 14h22m on an H2C (0.8 nozzle, 0.4 layer, PETG, 21 mm³/s),
# against its 1.325 kg geometry mass in bom.md §7.
MEASURED = ("14 h 22 m", 1.325, 14 + 22 / 60)

# Hours per geometry-kg, by print configuration. Only `bulk` is measured; the
# other three are that rate scaled for a slower setup and are labelled est. in
# the ledger. See machine-time.md "Open items" for what would measure them.
RATES = {
    "bulk":  round(MEASURED[2] / MEASURED[1], 1),   # 10.8 — measured
    "tight": 22,    # 3 mm watertight walls, Arachne, fine nozzle: ~½ the rate
    "small": 30,    # travel + layer-change overhead dominates a small part
    "petcf": 60,    # 0.4 nozzle, fine layers, 50 °C chamber
}

# bom.md §7 part-name fragment -> rate group. Every §7 row must match exactly one.
GROUP_OF = [
    ("Cold-core inner shell",  "bulk"),
    ("Cold-core foam cap",     "bulk"),
    ("Enclosure —",            "bulk"),
    ("Flavor reservoir",       "tight"),
    ("Faucet touch-flo shell", "petcf"),
    ("Faucet mounting plate",  "petcf"),
    ("Copper-plug stack",      "small"),
    ("PRV shroud",             "small"),
    ("Carbonator reed bridge", "small"),
    ("Drip pan",               "small"),
    ("Fuse clamp",             "small"),
    ("Cap-sense sleeve",       "small"),
]

GROUP_MARKER = {"bulk": "BULK", "tight": "TIGHT", "small": "SMALL", "petcf": "PETCF"}


# The turnaround table's one computed cell. Named here because two readers want it:
# the row is written under this marker, and the sum skips the row it is on.
PRINT_WALL_MARK = "(MT_H_PRINT_WALL)"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_data_row(c):
    if len(c) < 2 or all(set(x) <= set("-: ") for x in c):
        return False
    first = c[0].strip().lower()
    return not (first.startswith("**") or first in ("part", "group", "process",
                                                    "stage", "machine", ""))


def number(cell):
    """Last-cell figure → float, reading through bold and [value](NAME)."""
    m = re.match(r"^\**\s*\[?(-?[0-9][0-9,]*(?:\.[0-9]+)?)\]?", cell)
    return float(m.group(1).replace(",", "")) if m else 0.0


def printed_parts():
    """[(name, mass_kg)] over bom.md §7's data rows."""
    out, section = [], None
    for ln in open(BOM, encoding="utf-8").read().splitlines():
        if ln.startswith("## "):
            m = re.match(r"## (\d+)\.", ln)
            section = int(m.group(1)) if m else None
            continue
        if section != 7 or not ln.startswith("|"):
            continue
        c = cells(ln)
        if not is_data_row(c) or len(c) < 5 or "total" in c[0].lower():
            continue
        # §7 is Part | Qty | Material | Mass (kg) | $ — mass is 2nd-last.
        out.append((c[0], float(c[-2])))
    return out


def group_masses():
    """({group: kg}, [unassigned §7 rows])."""
    kg = {g: 0.0 for g in RATES}
    orphans = []
    for name, mass in printed_parts():
        hits = [g for frag, g in GROUP_OF if frag in name]
        if len(hits) != 1:
            orphans.append(f"  §7 {name[:60]}: {'no' if not hits else 'ambiguous'} rate group")
            continue
        kg[hits[0]] += mass
    return kg, orphans


def read_sections():
    """({section: summed last column}, [(section, process, hours)]) over
    machine-time.md's numbered sections — the process tables this script reads
    rather than computes. The per-row list is what lets the throughput table
    derive a machine's occupancy from the rows that occupy it, instead of
    carrying its own copy of the figure."""
    sums, rows, section = {}, [], None
    for ln in open(MT, encoding="utf-8").read().splitlines():
        if ln.startswith("## "):
            m = re.match(r"## (\d+)\.", ln)
            section = int(m.group(1)) if m else None
            continue
        if section is None or not ln.startswith("|"):
            continue
        c = cells(ln)
        if not is_data_row(c):
            continue
        sums[section] = sums.get(section, 0.0) + number(c[-1])
        rows.append((section, c[0], number(c[-1])))
    return sums, rows


def read_turnaround(wall):
    """The critical path's hours: every stage this file STATES, plus `wall` — the
    print's own wall clock, which this script computes off §7's masses.

    It lives under a `##` heading with no number, so it is read on its own rather
    than by read_sections(). The print's row is passed in rather than summed off
    the page: this script writes that cell, and a script that sums its own output
    reads the run before's figure, so the total trails a mass change by one pass.
    Keyed on the marker rather than the row's position, so the stage can move up
    or down the path."""
    total, inside = wall, False
    for ln in open(MT, encoding="utf-8").read().splitlines():
        if ln.startswith("## "):
            inside = ln.startswith("## Turnaround")
            continue
        if not inside or not ln.startswith("|"):
            continue
        c = cells(ln)
        if not is_data_row(c) or len(c) < 2:
            continue
        if PRINT_WALL_MARK in c[1]:
            continue                   # carried in `wall`, not read back off the page
        total += number(c[1])          # Stage | Hours | note
    return total


def main():
    kg, orphans = group_masses()
    hours = {g: kg[g] * RATES[g] for g in kg}
    h_print = sum(hours.values())
    wall = h_print / PRINTERS
    secs, rows = read_sections()
    turn = read_turnaround(wall)

    # A machine's occupancy is the sum of the rows that occupy it — never a
    # second copy of those hours typed into the throughput table.
    def occupies(frag, section=None):
        return sum(h for s, name, h in rows
                   if frag in name and (section is None or s == section))

    occ = {
        "PRINT": wall,
        "BENCH": secs.get(4, 0),                    # chill-down + burn-in
        "MOLD": occupies("Silicone funnel", 2),     # room-temp cure + post-cure bake
        "VESSEL": secs.get(3, 0),                   # hydro, passivation, vacuum
    }

    def ceiling(h):
        return round(HOURS_PER_YEAR / h) if h else 0

    variables = {
        "MT_PRINTERS": PRINTERS,
        "MT_MEASURED": MEASURED[0],
        "MT_MEASURED_KG": f"{MEASURED[1]:.3f}",
        "MT_PETCF_DRY": "12 h at 85 °C",
        "MT_DUTY": f"{DUTY * 100:.0f} %",
        "MT_KG": f"{sum(kg.values()):.3f}",
        "MT_H_PRINT": f"{h_print:.1f}",
        "MT_H_PRINT_WALL": f"{wall:.1f}",
        "MT_H_CURE": f"{secs.get(2, 0):.1f}",
        "MT_H_SOAK": f"{secs.get(3, 0):.1f}",
        "MT_H_RUN": f"{secs.get(4, 0):.1f}",
        "MT_OCC_BENCH": f"{occ['BENCH']:.1f}",
        "MT_OCC_MOLD": f"{occ['MOLD']:.1f}",
        "MT_OCC_VESSEL": f"{occ['VESSEL']:.1f}",
        "MT_CEIL_PRINT": f"{ceiling(occ['PRINT']):,}",
        "MT_CEIL_BENCH": f"{ceiling(occ['BENCH']):,}",
        "MT_CEIL_MOLD": f"{ceiling(occ['MOLD']):,}",
        "MT_CEIL_VESSEL": f"{ceiling(occ['VESSEL']):,}",
        "MT_UNITS_YEAR": f"~{round(ceiling(wall) * DUTY):,}",
        "MT_UNITS_YEAR_3": f"~{round(HOURS_PER_YEAR / (h_print / (PRINTERS + 1)) * DUTY):,}",
        "MT_H_TURN": f"{turn:.1f}",
        "MT_DAYS_TURN": f"{turn / 24:.1f}",
    }
    counts = {"MT_PRINTERS": 3, "MT_MEASURED": 1, "MT_MEASURED_KG": 1,
              "MT_PETCF_DRY": 1, "MT_DUTY": 2, "MT_KG": 1, "MT_H_PRINT": 1,
              "MT_H_PRINT_WALL": 4, "MT_H_CURE": 1, "MT_H_SOAK": 1,
              "MT_H_RUN": 1, "MT_CEIL_PRINT": 1, "MT_CEIL_BENCH": 1,
              "MT_CEIL_MOLD": 1, "MT_CEIL_VESSEL": 1, "MT_UNITS_YEAR": 1,
              "MT_OCC_BENCH": 1, "MT_OCC_MOLD": 1, "MT_OCC_VESSEL": 1,
              "MT_UNITS_YEAR_3": 1, "MT_H_TURN": 1, "MT_DAYS_TURN": 2}
    for g, tag in GROUP_MARKER.items():
        variables[f"MT_RATE_{tag}"] = f"{RATES[g]:g}"
        variables[f"MT_KG_{tag}"] = f"{kg[g]:.3f}"
        variables[f"MT_H_{tag}"] = f"{hours[g]:.1f}"
        counts[f"MT_RATE_{tag}"] = 2 if g == "bulk" else 1   # bulk cited in the intro
        counts[f"MT_KG_{tag}"] = 1
        counts[f"MT_H_{tag}"] = 1

    if "--check" in sys.argv:
        if orphans:
            print("bom.md §7 rows with no machine-time rate group:")
            print("\n".join(orphans))
            return 1
        text = open(MT, encoding="utf-8").read()
        stale = [f"  [{m.group(1)}]({name}) should be [{v}]({name})"
                 for name, v in variables.items()
                 for m in [re.search(r"\[([^\]]*)\]\(%s\)" % name, text)]
                 if m and m.group(1) != str(v)]
        if stale:
            print("machine-time.md markers are stale — run _machine_time.py:")
            print("\n".join(stale))
            return 1
        print("machine-time.md totals ✓")
        return 0

    substitute_md(MT, variables, counts)
    for g in ("bulk", "tight", "small", "petcf"):
        print(f"  {g:<6} {kg[g]:6.3f} kg × {RATES[g]:>4} h/kg = {hours[g]:6.1f} h")
    print(f"  {'PRINT':<6} {sum(kg.values()):6.3f} kg{'':14} {h_print:6.1f} h"
          f"   → {wall:.1f} h on {PRINTERS} printers")
    print(f"  cure {secs.get(2, 0):.1f} h · soak {secs.get(3, 0):.1f} h · run {secs.get(4, 0):.1f} h")
    for k, h in occ.items():
        print(f"  {k.lower():<6} occupied {h:5.1f} h/unit → ceiling {ceiling(h):>6,}/yr")
    print(f"  throughput  {round(ceiling(wall) * DUTY):,}/yr at {DUTY:.0%} duty")
    print(f"  turnaround  {turn:.1f} h = {turn / 24:.1f} days")
    if orphans:
        print("\nunassigned §7 rows:")
        print("\n".join(orphans))
    return 0


if __name__ == "__main__":
    sys.exit(main())
