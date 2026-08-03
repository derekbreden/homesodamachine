"""The pack's boxes on one page, banded — the numbers you choose a pose from.

`need.py` reports what a run connects before what it rides. This reports what a BAND holds
before anything is put in it: how much of the machine's plan each height claims, which bodies
claim it, how much of each claim is material, and whether the pose making the claim is settled
or provisional.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/enclosure-assembly/room.py
    tools/cad-venv/bin/python .../room.py --bands 12
    tools/cad-venv/bin/python .../room.py psu          # the bands one body stands in
    tools/cad-venv/bin/python .../room.py selftest

Emptiest band first.

THIS IS NOT A SEARCH. It ranks no candidate poses, finds no optimum and moves nothing. It is
arithmetic on boxes that already exist, and it runs in the time the pack takes to build. The
move it is built for is: read the table, do the arithmetic, CHOOSE a pose, place it, run the
build — `pack-closes`, `lines-clear` and `bend-radius` are exact and they are the oracle. A
sweep over poses answers the same question slower, and answers it wrong whenever its grid is
coarser than the free window (`calibration/Fences.md`).

Every figure here errs one way. `claimed` is the fraction of the cavity's plan that some
body's BOX covers somewhere in the band, so it over-states what is taken: a box is larger than
its part, and a cell is claimed if the box passes through the band at any height in it. Which
makes `free` a FLOOR — there is always at least this much, and usually more. A band that reads
empty is empty, and a pose put there needs no sweep to confirm it.

`fill` is what turns an over-claim back into room: at 1.0 a body's box is the body, and at 0.05
the box is claiming a rectangle around a rim, a wall and a cone. A band claimed by low-fill
boxes is a band with room in it that no figure here counts.

What this does not answer: the largest rectangle that actually fits a given part — that is
`scripts/fit.py`'s `slab`, which measures exact solids and reports its own field and grid. Nor
whether a body may move: `SETTLED` says whose pose is an input to the work, never whether a
provisional one is cheap. And a band is a slice of the machine, not a room in it — a body
standing across a band boundary is counted in both.
"""

import math
import sys

# The plan grid the claim is rasterized on. Coarser than any clearance in this pack, because
# the figure it produces is an over-claim being reported as a floor: a cell is claimed whole.
GRID = 5.0
BANDS = 8


def _pose_of(name: str) -> str:
    """Pose provenance, imported at the call so `selftest` never loads the pack — importing
    `scorecard` reaches `_contents`, which takes the build lock and supersedes a live build."""
    import scorecard
    return scorecard.pose(name)


def _bands(inner, n):
    """`n` uniform Z bands over the cavity, low to high."""
    z0, z1 = inner[4], inner[5]
    step = (z1 - z0) / n
    return [(z0 + i * step, z0 + (i + 1) * step) for i in range(n)]


def figures(band, boxes, inner, grid=GRID, pose_of=_pose_of) -> dict:
    """One band's record: its extent, the bodies whose boxes reach into it, and the fraction of
    the cavity's plan those boxes claim somewhere in it."""
    z0, z1 = band
    x0, x1, y0, y1 = inner[0], inner[1], inner[2], inner[3]
    nx = max(1, int((x1 - x0) / grid))
    ny = max(1, int((y1 - y0) / grid))

    present, covered = [], set()
    for name, (bb, fill) in sorted(boxes.items()):
        if bb.zmax <= z0 or bb.zmin >= z1:
            continue
        present.append({"name": name, "fill": round(fill, 3),
                        "pose": pose_of(name),
                        "box": [round(bb.xmin, 1), round(bb.ymin, 1),
                                round(bb.xmax, 1), round(bb.ymax, 1)]})
        # ceil, not int+1: a box whose face lands exactly on a cell boundary stops there
        # rather than claiming the cell beyond it.
        ix0 = max(0, int((bb.xmin - x0) / grid))
        ix1 = min(nx, math.ceil((bb.xmax - x0) / grid))
        iy0 = max(0, int((bb.ymin - y0) / grid))
        iy1 = min(ny, math.ceil((bb.ymax - y0) / grid))
        for ix in range(ix0, ix1):
            for iy in range(iy0, iy1):
                covered.add((ix, iy))

    cells = nx * ny
    claimed = len(covered) / cells if cells else 0.0
    prov = [p for p in present if p["pose"] == "provisional"]
    return {
        "z": [round(z0, 1), round(z1, 1)],
        "claimed": round(claimed, 3),
        "free": round(1.0 - claimed, 3),
        "free_mm2": round((1.0 - claimed) * (x1 - x0) * (y1 - y0), 0),
        "bodies": present,
        "provisional": len(prov),
        "settled": len(present) - len(prov),
        "grid": grid,
    }


def table(boxes, inner, n=BANDS, grid=GRID, only=(), pose_of=_pose_of) -> str:
    """The bands as rows, emptiest first."""
    rows = [figures(b, boxes, inner, grid, pose_of) for b in _bands(inner, n)]
    if only:
        rows = [r for r in rows
                if any(b["name"] in only for b in r["bodies"])]
    rows.sort(key=lambda r: -r["free"])
    x0, x1, y0, y1 = inner[0], inner[1], inner[2], inner[3]

    out = [f"{'free':>6} {'claimed':>8} {'free mm²':>9} {'bodies':>7} {'prov':>5}  z band"]
    for r in rows:
        out.append(f"{r['free']:6.0%} {r['claimed']:8.0%} {r['free_mm2']:9.0f} "
                   f"{len(r['bodies']):7d} {r['provisional']:5d}  "
                   f"z[{r['z'][0]:.0f},{r['z'][1]:.0f}]")
        for b in r["bodies"]:
            mark = " " if b["pose"] == "provisional" else "*"
            out.append(f"         {mark} {b['name']:<24} fill {b['fill']:.2f}  "
                       f"x[{b['box'][0]:.0f},{b['box'][2]:.0f}] "
                       f"y[{b['box'][1]:.0f},{b['box'][3]:.0f}]")
    out.append(f"{n} uniform bands over the cavity z[{inner[4]:.0f},{inner[5]:.0f}], plan "
               f"x[{x0:.0f},{x1:.0f}] y[{y0:.0f},{y1:.0f}] on a {grid:g} mm grid — the band "
               f"count and the grid are CHOSEN; pass --bands to re-cut.")
    out.append("`claimed` is boxes, not parts, and a cell is claimed whole — so `free` is a "
               "FLOOR and `fill` says how much of a claim is air. * = pose settled "
               "(scorecard.SETTLED); every other body's pose, and every route, is provisional.")
    return "\n".join(out)


def selftest() -> int:
    failures = 0

    def check(label, ok, detail=""):
        nonlocal failures
        mark = "✓" if ok else "✗"
        if not ok:
            failures += 1
        print(f"  {mark} {label}" + (f" — {detail}" if detail else ""))

    class BB:
        def __init__(self, xmin, ymin, zmin, xmax, ymax, zmax):
            self.xmin, self.ymin, self.zmin = xmin, ymin, zmin
            self.xmax, self.ymax, self.zmax = xmax, ymax, zmax

    # An explicit stub, so the selftest never imports the pack.
    def pose_of(name):
        return "settled" if name == "display" else "provisional"

    print("room (band claim, floor semantics)")

    inner = (0.0, 100.0, 0.0, 100.0, 0.0, 100.0)

    empty = figures((0.0, 10.0), {}, inner, GRID, pose_of)
    check("an empty band is wholly free", empty["free"] == 1.0 and empty["claimed"] == 0.0,
          f"free {empty['free']}")

    full = figures((0.0, 10.0), {"b": (BB(0, 0, 0, 100, 100, 100), 1.0)}, inner, GRID, pose_of)
    check("a box spanning the plan claims all of it", full["claimed"] == 1.0,
          f"claimed {full['claimed']}")

    # The floor property: a body that is mostly air claims its whole box anyway, so the figure
    # under-reports room and never over-reports it.
    airy = figures((0.0, 10.0), {"b": (BB(0, 0, 0, 50, 100, 100), 0.05)}, inner, GRID, pose_of)
    check("a 0.05-fill body claims its whole box", airy["claimed"] == 0.5,
          f"claimed {airy['claimed']} at fill {airy['bodies'][0]['fill']}")

    above = figures((0.0, 10.0), {"b": (BB(0, 0, 50, 100, 100, 60), 1.0)}, inner, GRID, pose_of)
    check("a body outside the band is not in it", above["claimed"] == 0.0 and not above["bodies"],
          f"claimed {above['claimed']}")

    straddle = figures((0.0, 10.0), {"b": (BB(0, 0, 5, 100, 100, 60), 1.0)}, inner, GRID, pose_of)
    check("a body straddling the boundary is counted in the band", straddle["claimed"] == 1.0)

    # Overlapping boxes are a union, not a sum — two halves that overlap do not claim 150%.
    both = figures((0.0, 10.0), {"a": (BB(0, 0, 0, 60, 100, 100), 1.0),
                                 "b": (BB(40, 0, 0, 100, 100, 100), 1.0)}, inner, GRID, pose_of)
    check("overlapping claims union rather than sum", both["claimed"] == 1.0,
          f"claimed {both['claimed']} from two 60% boxes")

    mixed = figures((0.0, 10.0), {"display": (BB(0, 0, 0, 10, 10, 10), 1.0),
                                  "psu": (BB(20, 20, 0, 30, 30, 10), 1.0)}, inner, GRID, pose_of)
    check("pose provenance rides each body", mixed["settled"] == 1 and mixed["provisional"] == 1,
          f"{mixed['settled']} settled, {mixed['provisional']} provisional")

    bands = _bands((0, 100, 0, 100, 0, 80), 8)
    check("bands tile the cavity without gap or overlap",
          bands[0][0] == 0.0 and bands[-1][1] == 80.0
          and all(abs(bands[i][1] - bands[i + 1][0]) < 1e-9 for i in range(len(bands) - 1)),
          f"{len(bands)} bands of {bands[0][1] - bands[0][0]:g}")

    print("PASS" if failures == 0 else f"FAIL — {failures}")
    return 0 if failures == 0 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()

    n = BANDS
    if "--bands" in argv:
        i = argv.index("--bands")
        n = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]

    # This reads the pack and writes nothing, so it takes no build lock — a reader that takes
    # one supersedes whatever build is running and kills it (`scripts/_run_lock.py`).
    import os
    os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

    import enclosure_assembly as ea
    import _boxes
    import _contents as contents
    import enclosure
    import scorecard

    pack = ea._build_pack(contents._moves())
    boxes = {name: (_boxes.boxed(s), scorecard.box_fill(s))
             for name, (s, _c) in pack.solids.items()}
    print(table(boxes, enclosure._dims().inner, n=n, only=set(argv)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
