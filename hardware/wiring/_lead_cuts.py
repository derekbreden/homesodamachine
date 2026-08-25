"""What to buy from JST's ASXHSXH22K catalogue to terminate this harness, and where to cut it.

Run: tools/cad-venv/bin/python hardware/wiring/_lead_cuts.py

A lead is socket-to-socket: one wire, **two** factory crimps. There are exactly two ways to
spend one, and the second is the whole trick:

    uncut           one conductor crimped at BOTH ends, length locked to a catalogue rung
    cut once at L   two pigtails, L and 305-L-kerf, carrying one factory crimp each

So a lead yields AT MOST TWO TERMINATIONS. That cap, not the wire, is what is being bought —
which is why the ledger below counts orphaned crimps and not scrapped millimetres. A 280 mm
pigtail wastes almost no copper and still throws away half the lead.

A CUT LEAD CANNOT BE CRIMPED AT BOTH ENDS. Cutting is what destroys the second crimp, so a
board-to-junction segment has to be a lead nobody cut, and its length is therefore not a free
variable: it is one of RUNGS. Junctions land on catalogue distances, not on the midpoint of
the run.

Lengths are not typed here. They come from `_run_lengths.py`, which measures them off the
placed machine, so moving a device moves the buy list.
"""

import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _run_lengths  # noqa: E402

# JST's catalogue for the -001T factory-crimped onto black 22 AWG, socket-to-socket. Six rungs
# and no more: nothing longer than 305 mm exists in the line at any distributor.
RUNGS = (51, 102, 152, 203, 254, 305)
LEAD = 305.0
KERF = 3.0
USABLE = LEAD - KERF          # the longest single-crimp pigtail one cut can yield

# A stub is not a cable. Below this a junction is being placed to satisfy arithmetic rather
# than to reach anything, and the honest move is to squeeze the run instead.
MIN_PIGTAIL = 80.0

# 303-330 mm buys at 302 and gives up its service loop. The routed factor in `_run_lengths` is
# calibrated on ONE point, so a run reading 309 is not meaningfully longer than one reading 302
# and does not deserve a connector in the middle of it. Verify these at the bench.
SQUEEZE_CEIL = 330.0

# Per-lead price at DigiKey, single quantity. The ladder falls to ~$0.765 at ten and ~$0.650 at
# a hundred; the cheap rungs track within a nickel, so one number per rung is close enough to
# size an order.
PRICE = {51: 0.76, 102: 0.79, 152: 0.81, 203: 0.82, 254: 0.85, 305: 0.90}


def conductors():
    """Every in-box conductor as (loom, label, measured cut mm). J3 is not here: it is the one
    loom that leaves the enclosure, and it is 28 AWG ribbon, which this catalogue does not sell."""
    rows, _, _, _ = _run_lengths.measure()
    return [(loom, label, mm) for loom, label, n, mm in rows for _ in range(n)]


def pair_up(pigtails):
    """Two pigtails share a lead when they fit in one. Longest-first, matched with the longest
    partner that still fits — the short ones are the flexible ones, so they are spent last."""
    xs = sorted(pigtails, reverse=True)
    used = [False] * len(xs)
    leads = []
    for i, a in enumerate(xs):
        if used[i]:
            continue
        used[i] = True
        for j in range(len(xs) - 1, i, -1):
            if not used[j] and a + xs[j] <= USABLE:
                used[j] = True
                leads.append((a, xs[j]))
                break
        else:
            leads.append((a, None))
    return leads


def rung_options(mm):
    """Which uncut leads can carry the board-to-junction half of a run this long."""
    return [c for c in RUNGS if c <= mm and MIN_PIGTAIL <= mm - c <= USABLE]


def plan():
    rows = conductors()
    direct = [r for r in rows if r[2] <= USABLE]
    squeeze = [r for r in rows if USABLE < r[2] <= SQUEEZE_CEIL]
    junction = [r for r in rows if r[2] > SQUEEZE_CEIL]

    # One rung per distinct long run, not per conductor: four conductors going to the same place
    # break at the same junction. Small enough to enumerate exhaustively, so the answer is
    # deterministic rather than whatever a seeded search happened to land on.
    groups = sorted({(loom, label, mm) for loom, label, mm in junction})
    counts = {g: sum(1 for r in junction if r == g) for g in groups}
    options = [rung_options(mm) for _, _, mm in groups]
    if not all(options):
        raise SystemExit("a run is past 2x the lead and needs two junctions: " +
                         ", ".join(f"{lo} {la} {mm:.0f}" for (lo, la, mm), o
                                   in zip(groups, options) if not o))

    fixed = [r[2] for r in direct] + [USABLE] * len(squeeze)
    n_uncut = sum(counts.values())  # constant: one uncut lead per junctioned conductor

    best = None
    for choice in itertools.product(*options):
        pig = list(fixed)
        for g, c in zip(groups, choice):
            pig += [g[2] - c] * counts[g]
        leads = pair_up(pig)
        # Fewest leads wins. Ties go to the fewest distinct rungs to order, then to the longest
        # uncut segments — which puts each junction as close to its device cluster as the
        # catalogue allows, leaving the shortest unprotected pigtail beyond it.
        key = (len(leads), len(set(choice)), -sum(choice))
        if best is None or key < best[0]:
            best = (key, choice, leads)

    _, choice, leads = best
    return direct, squeeze, groups, counts, choice, leads, n_uncut


def main():
    direct, squeeze, groups, counts, choice, leads, n_uncut = plan()

    buy = {}
    for g, c in zip(groups, choice):
        buy[c] = buy.get(c, 0) + counts[g]
    buy[305] = buy.get(305, 0) + len(leads)   # every lead that gets cut is bought at full length
    total = sum(buy.values())
    cost = sum(n * PRICE[c] for c, n in buy.items())
    served = len(direct) + len(squeeze) + n_uncut
    orphans = sum(1 for a, b in leads if b is None)

    print(f"{served} in-box conductors  =  {len(direct)} bought outright  +  "
          f"{len(squeeze)} squeezed to {USABLE:.0f} mm  +  {n_uncut} broken at a junction")
    print(f"J3's 4 contacts are not here: 28 AWG ribbon, out of the enclosure, hand-crimped.\n")

    print("buy")
    for c in sorted(buy, reverse=True):
        print(f"  ASXHSXH22K{c:<4} x{buy[c]:<3} @ ${PRICE[c]:.2f}")
    print(f"  {total} leads, ${cost:,.2f} at single quantity\n")

    print(f"cut  {len(leads)} leads, yielding {len(leads) * 2 - orphans} pigtails")
    print(f"     {orphans} second crimps orphaned "
          f"({orphans / (total * 2) * 100:.0f}% of what the order carries)\n")

    print("junction placement, routed mm from the board")
    for (loom, label, mm), c in zip(groups, choice):
        alts = "/".join(str(a) for a in rung_options(mm) if a != c)
        print(f"  {loom:<16}{label:<24}{mm:>4.0f} run  =  {c:>3} uncut + {mm - c:>3.0f} pigtail"
              f"  x{counts[(loom, label, mm)]}" + (f"   (or {alts})" if alts else ""))

    if squeeze:
        print("\nsqueezed, verify at the bench")
        for loom, label, mm in sorted(set(squeeze)):
            n = sum(1 for r in squeeze if r == (loom, label, mm))
            print(f"  {loom:<16}{label:<24}{mm:>4.0f} measured, {mm - USABLE:>3.0f} mm over  x{n}")


if __name__ == "__main__":
    main()
