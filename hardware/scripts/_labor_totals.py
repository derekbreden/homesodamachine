#!/usr/bin/env python3
"""Compute labor.md per-unit attended-minute subtotals + their dollar cost from
the minute column, and write them into the [value](NAME) docgen markers — so a
row can be added, split or re-estimated without anyone re-adding a column.
The parts-side companion is _bom_totals.py; this owns the TIME rollups.

  * Each section's subtotal = the sum of its data rows' minute cells (the last
    cell). Header rows, separators, and the bold inline subtotal row are
    skipped.
  * A row with a Run cell is an operation set up once for many pieces:
    `15 m setup a plate of 30 · 30 s a float · 3 a machine`. Its minute cell is
    arithmetic, written here: the setups a batch of BATCH_SIZE machines needs,
    plus every piece's own time, divided across the batch. A run sized `a batch`
    sets up once for however many machines the batch holds.
  * Every ESTIMATE must be one of INCREMENTS below — the steps a person actually
    estimates in. "40 minutes" claims a precision nobody has for work they have
    not timed: it means 30 or it means 45. --check rejects anything else, which
    is what keeps the convention from eroding one plausible-looking row at a
    time. A run's setup and per-piece time are its estimates, on RUN_INCREMENTS.
    Run rows, subtotals and totals are arithmetic and land where they land.
  * Markers: LAB_SEC1..N (each section's inline subtotal row and the Totals
    table's minute figure feed off the same sum), LAB_HM1..N / LAB_USD1..N (the
    Totals table), LAB_HM / LAB_USD (per-unit total), LAB_HM_PRINTED (the
    printed-parts runs), LABOR_RATE, BATCH_SIZE.

Run:  python3 hardware/scripts/_labor_totals.py           # recompute + write markers
      python3 hardware/scripts/_labor_totals.py --check    # exit 1 on an
                                                           # off-ladder estimate
                                                           # or a stale marker
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LABOR = os.path.join(HERE, "..", "ledger", "labor.md")

from pathlib import Path  # noqa: E402
sys.path.insert(
    0, str(next(p for p in Path(HERE).resolve().parents
                if (p / "tools" / "docgen").is_dir()) / "tools"))
from docgen import cells, substitute_md  # noqa: E402
from _funnel_casting import figures as funnel_figures  # noqa: E402
from _machine_time import print_estimate  # noqa: E402

# The build batch a run row's minutes are worked out for — the size the ledger
# already buys in (endcap plates 20 at a time = 10 carbonators, tube 10 at a
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

# A run's setup and each piece's time, in minutes: seconds and single minutes —
# a plate turned, a magnet seated at a pause — then the row ladder.
RUN_INCREMENTS = (5 / 60, 10 / 60, 15 / 60, 30 / 60, 45 / 60, 1, 2, 3) + INCREMENTS

MINUTES = re.compile(r"^\**\s*\[?([0-9][0-9,]*(?:\.[0-9]+)?)\]?")
# `15 m setup a plate of 30 · 30 s a float · 3 a machine`; `a batch` takes no size.
RUN = re.compile(r"^(?P<setup>[0-9][0-9 hms]*?) setup an? (?P<run>[a-z][a-z-]*)(?: of (?P<cap>[0-9]+))?"
                 r" · (?P<each>[0-9][0-9 hms]*?) an? (?P<piece>[a-z][a-z -]*?)"
                 r" · (?P<per>[0-9]+) an? machine$")
DURATION = re.compile(r"^(?:([0-9]+) h)? ?(?:([0-9]+) m)? ?(?:([0-9]+) s)?$")


def hm(mins):
    """Minutes → 'h m' the way a person says it: 45 m, 2 h, 1 h 15 m."""
    h, m = divmod(math.floor(mins + 0.5), 60)
    if not h:
        return f"{m} m"
    return f"{h} h" if not m else f"{h} h {m} m"


def short(mins):
    """A run estimate → how it is written: 30 s, 15 m, 1 h 15 m."""
    return f"{round(mins * 60)} s" if mins < 1 else hm(mins)


def figure(mins):
    """A computed minute figure → its cell text: 3, 1.5, 101.7."""
    return f"{round(mins + 1e-9, 1):,g}"


def usd(mins):
    return f"${mins / 60 * LABOR_RATE:,.2f}"


def minutes(cell):
    """A minute cell → minutes. Reads through both the bold of a subtotal row
    and the [value](NAME) brackets of a docgen marker, so the parse never
    depends on what this script last wrote."""
    m = MINUTES.match(cell)
    return float(m.group(1).replace(",", "")) if m else 0


def duration(text):
    m = DURATION.match(text.strip())
    if not m or not any(m.groups()):
        return None
    h, mins, s = (int(g or 0) for g in m.groups())
    return h * 60 + mins + s / 60


def run_of(cell):
    """A Run cell → {setup, run, cap, each, piece, per}, or a complaint."""
    m = RUN.match(re.sub(r"\s+", " ", cell.strip()))
    if not m:
        return "is not `<setup> setup a <run> of <n> · <time> a <piece> · <n> a machine`"
    setup, each = duration(m["setup"]), duration(m["each"])
    cap = int(m["cap"]) if m["cap"] else None
    if setup is None or each is None:
        return "has a time that is not `30 s`, `15 m` or `1 h 15 m`"
    if (m["run"] == "batch") != (cap is None):
        return "sizes a batch, or leaves another run unsized"
    return {"setup": setup, "run": m["run"], "cap": cap, "each": each,
            "piece": m["piece"], "per": int(m["per"])}


def per_machine(run, batch=BATCH_SIZE):
    """Attended minutes per machine when `batch` machines are built together:
    every setup the batch's pieces need, plus each piece's own time."""
    pieces = batch * run["per"]
    runs = 1 if run["cap"] is None else math.ceil(pieces / run["cap"])
    return (runs * run["setup"] + pieces * run["each"]) / batch


def on_ladder(v, ladder):
    return any(abs(v - i) < 1e-6 for i in ladder)


def parse(lines):
    """([(index, section, subsection, name, minutes, run)], [complaints]) over
    labor.md's numbered sections. A run row's minutes are what its Run cell
    works out to; every other row's are its cell."""
    rows, offenders, section, subsection, run_col = [], [], None, None, None
    for i, ln in enumerate(lines):
        if ln.startswith("## "):
            m = re.match(r"## (\d+)\.", ln)
            section, subsection = (int(m.group(1)) if m else None), None
            continue
        if ln.startswith("### "):
            subsection = ln[4:].strip()
            continue
        if section is None or not ln.startswith("|"):
            continue
        c = cells(ln)
        if len(c) < 2 or all(set(x) <= set("-: ") for x in c):     # separator
            continue
        first = c[0].strip()
        if first.lower() == "operation":                            # header
            run_col = c.index("Run") if "Run" in c else None
            continue
        if first.startswith("**"):                                  # subtotal
            continue
        where = f"  §{section} {first[:52]}"
        spec = c[run_col] if run_col is not None and run_col < len(c) - 1 else ""
        if spec:
            run = run_of(spec)
            if isinstance(run, str):
                offenders.append(f"{where}: Run cell {run}")
                rows.append((i, section, subsection, first, minutes(c[-1]), None))
                continue
            for label, v in (("setup", run["setup"]), ("each", run["each"])):
                if not on_ladder(v, RUN_INCREMENTS):
                    near = min(RUN_INCREMENTS, key=lambda r: (abs(r - v), r))
                    offenders.append(f"{where}: {label} {short(v)} — say {short(near)}")
            rows.append((i, section, subsection, first, float(figure(per_machine(run)).replace(",", "")), run))
            continue
        v = minutes(c[-1])
        if not on_ladder(v, INCREMENTS):
            near = min(INCREMENTS, key=lambda r: (abs(r - v), r))
            offenders.append(f"{where}: {figure(v)} min — say {hm(near)}")
        rows.append((i, section, subsection, first, v, None))
    return rows, offenders


def write_runs(lines, rows):
    """The lines with each run row's minute cell set to what its run works out
    to; the parts tag and everything else on the line stays as written."""
    out = list(lines)
    for i, *_, v, run in rows:
        if run is None:
            continue
        head, last = out[i].rstrip().removesuffix("|").rsplit("|", 1)
        out[i] = head + "|" + re.sub(r"^(\s*)[0-9][0-9.,]*", lambda m: m.group(1) + figure(v), last, count=1) + "|"
    return out


def main():
    lines = open(LABOR, encoding="utf-8").read().splitlines()
    rows, offenders = parse(lines)
    sums = {}
    for _, section, _, _, v, _ in rows:
        sums[section] = sums.get(section, 0) + v
    grand = sum(sums.values())
    printed = sum(v for _, _, sub, _, v, _ in rows if sub == "Printed parts")

    variables = {"BATCH_SIZE": BATCH_SIZE, "LABOR_RATE": f"${LABOR_RATE:,}",
                 "LAB_HM_PRINTED": hm(printed)}
    printing = print_estimate()
    if printing["unassigned"]:
        print("bom.md §7 rows with no machine-time rate group:")
        print("\n".join(printing["unassigned"]))
        return 1
    variables.update({"LAB_PRINT_KG": f"{printing['total_kg']:.3f}",
                      "LAB_PRINT_H": f"{printing['total_hours']:.1f}"})
    variables.update(funnel_figures())
    for n, v in sums.items():
        variables[f"LAB_SEC{n}"] = figure(v)
        variables[f"LAB_HM{n}"] = hm(v)
        variables[f"LAB_USD{n}"] = usd(v)
    variables["LAB_HM"] = hm(grand)
    variables["LAB_USD"] = usd(grand)
    written = write_runs(lines, rows)

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
        stale += [f"  {cells(lines[i])[0][:52]}: {figure(minutes(cells(lines[i])[-1]))} min should be {figure(v)}"
                  for i, *_, v, run in rows if run and written[i] != lines[i]]
        if stale:
            print("labor.md markers are stale — run _labor_totals.py:")
            print("\n".join(stale))
            return 1
        print("labor.md totals ✓")
        return 0

    if written != lines:
        with open(LABOR, "w", encoding="utf-8") as fh:
            fh.write("\n".join(written) + "\n")
    substitute_md(LABOR, variables)
    for n in sorted(sums):
        print(f"  §{n:<2} {hm(sums[n]):>10}   {usd(sums[n]):>10}")
    print(f"  ── {hm(grand):>10}   {usd(grand):>10}")
    if offenders:
        print("\noff the increment ladder:")
        print("\n".join(offenders))
    return 0


if __name__ == "__main__":
    sys.exit(main())
