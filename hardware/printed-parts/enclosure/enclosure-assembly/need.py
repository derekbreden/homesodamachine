"""What a run connects, before what it rides.

Every line in the pack is a connection between two ports, and every diagnosis of a
blocked run names what pins the route it currently takes. This reports the other half:
where the run's two ends stand, how far apart that is — split by axis, because a run
that drains a reservoir owes its Z whatever its plan does or doesn't owe — and how much
path the drawn route spends covering it. `detour` is path ÷ span. A run near 1 spends
its length on its own need; a run far above it is riding infrastructure its ends do not
ask for, which no corner-by-corner grade will say. On a high-detour run the move is the
route, not the corner — `calibration/Fences.md`, *The route as requirement*.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure-assembly/need.py
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure-assembly/need.py fluid-25
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure-assembly/need.py selftest

Worst detour first. The same figures ride every build of the sidecar — each
`scorecard.bends` row carries them under `need`, and each bend-radius detail row ends
with its need clause — so the table here and the card never disagree.

What this does not answer: which lanes and shelves the extra path rides, and who else
rides them — a lane's customer count is read where the lane is authored, `_lines.py`.
And a detour near 1 is not health: a short run can be pinned at both ends and still
red. The figure says where to look, not what to do.

`selftest` holds the controls: a straight run's path is its span; a route that goes out
and comes back reports the excursion its ends do not span; the axis split reads off the
endpoints alone; a run whose ends coincide reports no ratio rather than dividing by
zero; and the figures a real `route(...)` reports are the run's own `pts` and `length`,
so the table grades the same centreline the build sweeps.
"""

import math
import sys


def figures(run) -> dict:
    """The need record for one run: `ends` (the two endpoint waypoints), `axis` (the
    endpoint separation split by world axis), `span` (endpoint-to-endpoint distance),
    `path` (developed centreline length, arcs included), `detour` (path ÷ span, None
    when the ends coincide)."""
    a, b = run.pts[0], run.pts[-1]
    span = math.dist(a, b)
    path = run.length
    return {
        "ends": [[round(v, 2) for v in a], [round(v, 2) for v in b]],
        "axis": {ax: round(abs(b[i] - a[i]), 2) for i, ax in enumerate("xyz")},
        "span": round(span, 2),
        "path": round(path, 2),
        "detour": None if span < 1e-9 else round(path / span, 3),
    }


def table(runs, only=()) -> str:
    """The runs as need rows, worst detour first, straights at the bottom."""
    rows = [(r, figures(r)) for r in runs if not only or r.id in only]
    rows.sort(key=lambda rn: -(rn[1]["detour"] or float("inf")))
    lines = [f"{'detour':>7} {'path':>7} {'span':>7} {'Δx':>6} {'Δy':>6} {'Δz':>6}  run"]
    for r, n in rows:
        d = "   ∞  " if n["detour"] is None else f"{n['detour']:5.2f}×"
        ax = n["axis"]
        lines.append(f"{d:>7} {n['path']:7.1f} {n['span']:7.1f} "
                     f"{ax['x']:6.1f} {ax['y']:6.1f} {ax['z']:6.1f}  "
                     f"{r.id}  {r.frm} → {r.to}")
    lines.append(f"{len(rows)} runs off _lines.build_runs(), live from source — straights "
                 f"included. Lanes and their customers are not counted here; a lane is "
                 f"read where it is authored, _lines.py.")
    return "\n".join(lines)


def selftest() -> int:
    import cadquery as cq
    import _routing as R

    failures = 0

    def check(label, ok, detail=""):
        nonlocal failures
        mark = "✓" if ok else "✗"
        if not ok:
            failures += 1
        print(f"  {mark} {label}" + (f" — {detail}" if detail else ""))

    def synthetic(pts):
        return R.Run(id="t", kind="fluid", frm="A.p", to="B.p", pts=list(pts),
                     diam=6.35, bend=25.4)

    print("need (span, axis split, detour)")

    straight = figures(synthetic([(0.0, 0.0, 0.0), (0.0, 130.0, 0.0)]))
    check("a straight run's path is its span", abs(straight["detour"] - 1.0) < 1e-9,
          f"detour {straight['detour']}")

    out_and_back = figures(synthetic([(0.0, 0.0, 0.0), (100.0, 0.0, 0.0),
                                      (100.0, 50.0, 0.0), (0.0, 50.0, 0.0)]))
    check("a route out and back reports the excursion its ends do not span",
          out_and_back["span"] == 50.0 and out_and_back["detour"] > 4.0,
          f"span {out_and_back['span']}, path {out_and_back['path']} = "
          f"{out_and_back['detour']}×")

    climb = figures(synthetic([(10.0, 20.0, 0.0), (10.0, 300.0, 0.0), (10.0, 300.0, 250.0),
                               (10.0, 20.0, 250.0)]))
    check("the axis split reads off the endpoints alone",
          climb["axis"] == {"x": 0.0, "y": 0.0, "z": 250.0},
          f"axis {climb['axis']} on a route spending {climb['path']:.0f} in y")

    loop = figures(synthetic([(0.0, 0.0, 0.0), (50.0, 0.0, 0.0), (50.0, 50.0, 0.0),
                              (0.0, 0.0, 0.0)]))
    check("coincident ends report no ratio rather than dividing by zero",
          loop["detour"] is None and loop["span"] == 0.0, f"span {loop['span']}")

    # A real route: the figures must be the run's own pts and length — the same
    # centreline the build sweeps and the card grades.
    R._frames.clear()
    R.frame("A", cq.Solid.makeBox(10, 10, 10, cq.Vector(0, 0, 0)),
            {"p": ((0.0, 0.0, 0.0), "y+", 6.35)})
    R.frame("B", cq.Solid.makeBox(10, 10, 10, cq.Vector(0, 0, 0)),
            {"p": ((200.0, 130.0, 0.0), "y-", 6.35)})
    run = R.route("t", "A.p", {"x": 200.0}, "B.p", stub=40.0, bend=6.0)
    n = figures(run)
    R._frames.clear()
    check("a real route's figures are its own pts and length",
          n["span"] == round(math.dist(run.pts[0], run.pts[-1]), 2)
          and n["path"] == round(run.length, 2) and n["detour"] > 1.0,
          f"span {n['span']}, path {n['path']} = {n['detour']}×")

    print("PASS" if failures == 0 else f"FAIL — {failures}")
    return 0 if failures == 0 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    import _lines
    print(table(_lines.build_runs(), only=set(argv)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
