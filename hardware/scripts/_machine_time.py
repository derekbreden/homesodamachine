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

  * Print hours = each §7 row's mass × its GROUP's hours-per-kg. THE KG IS
    FILAMENT, not geometry — §7 bills what a slice of the part lays, shell and
    infill (_bom_masses.PROFILES), and the rates below are measured against that
    same figure. Groups are the five print configurations the build uses;
    _bom_masses.GROUP_OF assigns every row by name and is imported rather than
    restated, so one list says what plate a part comes off. --check fails on an
    unassigned row, so a new printed part cannot silently escape the estimate.
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
from docgen import cells, substitute_md  # noqa: E402

sys.path.insert(0, HERE)
from _bom_masses import GROUP_OF  # noqa: E402

PRINTERS = 2          # Bambu Lab H2C, tools.md
DUTY = 0.65           # machine duty — failed prints, plate changes, maintenance
HOURS_PER_YEAR = 24 * 365

# The two slices the print estimate stands on, each one a plate whose hours AND
# filament were both read off the same slice.
#
#   bulk — the cold-core inner shell, 379.99 m in 14h22m on an H2C (0.8 nozzle,
#          0.4 layer, PETG, 21 mm³/s). printed-parts/cold-core/foam-shell/print-log.md.
#   ext  — the enclosure front-top, 213.06 m in 20h23m on an H2C (0.4 nozzle,
#          0.24 layer, PET-GF15, 18 mm³/s).
#          printed-parts/enclosure/enclosure/print-log.md holds the profile.
#
# A SLICE IS A PLATE, NOT A ROW. The kg beside each is what _bom_masses' shell-plus-
# infill model bills for THE SOLID THAT PLATE WAS TAKEN FROM, which is the basis this
# file multiplies — not a reading of whatever §7's row says today, so a part that
# changes shape moves its own mass without disturbing the rate it is priced at. The
# slice's own metres are the larger number of the two, by the supports and brim §7
# does not carry; carrying the rate against the model's figure is what puts the
# supports back into the hours.
MEASURED = ("14 h 22 m", 1.126, 14 + 22 / 60)
MEASURED_EXT = ("20 h 23 m", 0.653, 20 + 23 / 60)

# A RATE IN HOURS PER KG DOES NOT SURVIVE A STOCK CHANGE. A nozzle lays grams at
# (volumetric cap × density), so hours per kg move by the inverse of that product —
# the same arithmetic the enclosure's print log states when it prices its own slot.
# The cold core ships in PET-GF15 (`ledger/bom.md` §7) and the plate that was timed
# ran PETG, so `bulk` is CARRIED across that pair and is an estimate until a PET-GF
# plate of the shell is sliced. `ext` needs no carry: it was measured in the stock
# the exterior ships in.
_CAP_PETG, _RHO_PETG = 21.0, 1.27        # foam-shell/print-log.md, bom.md §7
_CAP_PETGF, _RHO_PETGF = 18.0, 1.43      # enclosure/print-log.md, bom.md §7
PETGF_CARRY = (_CAP_PETG * _RHO_PETG) / (_CAP_PETGF * _RHO_PETGF)

# Hours per kg of filament, by print configuration. `ext` is measured; `bulk` is that
# measurement carried across the stock; the other three are the MEASURED PLATE's own
# rate scaled for a slower configuration, which is a scaling of the setup and not of
# the stock — so they hang off `_BULK_PETG` rather than off the carried figure. All
# four are labelled est. in the ledger. See machine-time.md "Open items".
_BULK_PETG = round(MEASURED[2] / MEASURED[1], 1)
RATES = {
    "bulk":  round(_BULK_PETG * PETGF_CARRY, 1),                # 13.3 — carried, est.
    "ext":   round(MEASURED_EXT[2] / MEASURED_EXT[1], 1),       # 31.2 — measured
    "tight": round(_BULK_PETG * 2.0),  # 3 mm watertight walls, Arachne, fine nozzle: ~½ the rate
    "small": round(_BULK_PETG * 2.8),  # travel + layer-change overhead dominates a small part
    "petgf": round(_BULK_PETG * 5.5),  # the faucet: 0.4 TC, fine layers, 50 °C chamber, supported
}

GROUP_MARKER = {"bulk": "BULK", "ext": "EXT", "tight": "TIGHT",
                "small": "SMALL", "petgf": "PETGF"}


# The turnaround table's one computed cell. Named here because two readers want it:
# the row is written under this marker, and the sum skips the row it is on.
PRINT_WALL_MARK = "(MT_H_PRINT_WALL)"


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
        "CARBONATOR": secs.get(3, 0),               # hydro, passivation, vacuum
    }

    def ceiling(h):
        return round(HOURS_PER_YEAR / h) if h else 0

    variables = {
        "MT_PRINTERS": PRINTERS,
        "MT_MEASURED": MEASURED[0],
        "MT_MEASURED_KG": f"{MEASURED[1]:.3f}",
        "MT_RATE_BULK_PETG": f"{_BULK_PETG:g}",
        "MT_PETGF_CARRY": f"{(PETGF_CARRY - 1) * 100:.1f} %",
        "MT_MEASURED_EXT": MEASURED_EXT[0],
        "MT_MEASURED_EXT_KG": f"{MEASURED_EXT[1]:.3f}",
        "MT_PETGF_DRY": "10 h at 100 °C",
        "MT_DUTY": f"{DUTY * 100:.0f} %",
        "MT_KG": f"{sum(kg.values()):.3f}",
        # What a unit still takes off the PETG spool: the two groups that are not
        # PET-GF. Summed from the same masses rather than typed, so it follows §7.
        "MT_KG_PETG_UNIT": f"{kg['tight'] + kg['small']:.2f}",
        "MT_H_PRINT": f"{h_print:.1f}",
        "MT_H_PRINT_WALL": f"{wall:.1f}",
        "MT_H_CURE": f"{secs.get(2, 0):.1f}",
        "MT_H_SOAK": f"{secs.get(3, 0):.1f}",
        "MT_H_RUN": f"{secs.get(4, 0):.1f}",
        "MT_OCC_BENCH": f"{occ['BENCH']:.1f}",
        "MT_OCC_MOLD": f"{occ['MOLD']:.1f}",
        "MT_OCC_CARBONATOR": f"{occ['CARBONATOR']:.1f}",
        "MT_CEIL_PRINT": f"{ceiling(occ['PRINT']):,}",
        "MT_CEIL_BENCH": f"{ceiling(occ['BENCH']):,}",
        "MT_CEIL_MOLD": f"{ceiling(occ['MOLD']):,}",
        "MT_CEIL_CARBONATOR": f"{ceiling(occ['CARBONATOR']):,}",
        "MT_UNITS_YEAR": f"~{round(ceiling(wall) * DUTY):,}",
        "MT_UNITS_YEAR_3": f"~{round(HOURS_PER_YEAR / (h_print / (PRINTERS + 1)) * DUTY):,}",
        "MT_H_TURN": f"{turn:.1f}",
        "MT_DAYS_TURN": f"{turn / 24:.1f}",
    }
    for g, tag in GROUP_MARKER.items():
        variables[f"MT_RATE_{tag}"] = f"{RATES[g]:g}"
        variables[f"MT_KG_{tag}"] = f"{kg[g]:.3f}"
        variables[f"MT_H_{tag}"] = f"{hours[g]:.1f}"

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

    substitute_md(MT, variables)
    for g in ("bulk", "ext", "tight", "small", "petgf"):
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
