"""Pairwise overlap audit for the full Narrow-Edition assembly.

Builds the two enclosure halves + every placed content part + the display +
the hopper funnel in shared coordinates, then reports:
  * the contents bounding box (what drives the enclosure size),
  * each part vs. the front half and the back half (wall/ceiling intrusion),
  * every content↔content pair,
flagging any intersection with Volume() over a small slip-fit threshold.
"""

import sys
from pathlib import Path
from itertools import combinations

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "printed-parts" / "enclosure" / "narrow-enclosure"))
sys.path.insert(0, str(_here.parent))

import narrow_enclosure as enclosure
import narrow_enclosure_assembly as ea
import _contents as contents

THRESH = 5.0  # mm³ — below this is slip-fit / numerical noise


def _vol(a, b):
    try:
        return a.intersect(b).Volume()
    except Exception:
        return 0.0


def main():
    placed = contents.build()
    parts = {n: s for n, (s, _c) in placed.items()}
    parts["display"] = ea._placed_display()
    parts["hopper-funnel"] = ea._placed_funnel()

    front = enclosure.build_front_half().val()
    back = enclosure.build_back_half().val()

    bbs = {n: s.BoundingBox() for n, s in parts.items()}
    xmin = min(b.xmin for b in bbs.values()); xmax = max(b.xmax for b in bbs.values())
    ymin = min(b.ymin for b in bbs.values()); ymax = max(b.ymax for b in bbs.values())
    zmin = min(b.zmin for b in bbs.values()); zmax = max(b.zmax for b in bbs.values())
    print(f"contents bbox: X[{xmin:.1f},{xmax:.1f}]={xmax-xmin:.1f}  "
          f"Y[{ymin:.1f},{ymax:.1f}]={ymax-ymin:.1f}  Z[{zmin:.1f},{zmax:.1f}]={zmax-zmin:.1f}")
    ob = front.BoundingBox(); obk = back.BoundingBox()
    ex0 = min(ob.xmin, obk.xmin); ex1 = max(ob.xmax, obk.xmax)
    ey0 = min(ob.ymin, obk.ymin); ey1 = max(ob.ymax, obk.ymax)
    ez0 = min(ob.zmin, obk.zmin); ez1 = max(ob.zmax, obk.zmax)
    print(f"outer envelope: X{ex1-ex0:.1f}  Y{ey1-ey0:.1f}  Z{ez1-ez0:.1f}")
    print()

    print("part vs. halves (intrusion into wall/ceiling/floor):")
    for n, s in parts.items():
        vf = _vol(s, front)
        vb = _vol(s, back)
        flag = "  <-- OVERLAP" if (vf > THRESH or vb > THRESH) else ""
        if flag:
            print(f"  {n:16s} front {vf:8.1f}   back {vb:8.1f}{flag}")
    print()

    print("content pairs:")
    any_pair = False
    for (na, sa), (nb, sb) in combinations(parts.items(), 2):
        ba, bb = bbs[na], bbs[nb]
        if (ba.xmax < bb.xmin or bb.xmax < ba.xmin or
            ba.ymax < bb.ymin or bb.ymax < ba.ymin or
            ba.zmax < bb.zmin or bb.zmax < ba.zmin):
            continue
        v = _vol(sa, sb)
        if v > THRESH:
            any_pair = True
            ib = sa.intersect(sb).BoundingBox()
            print(f"  {na:16s} ∩ {nb:16s} = {v:8.1f} mm³  <-- OVERLAP")
            print(f"      region: X[{ib.xmin:.1f},{ib.xmax:.1f}] "
                  f"Y[{ib.ymin:.1f},{ib.ymax:.1f}] Z[{ib.zmin:.1f},{ib.zmax:.1f}]")
    if not any_pair:
        print("  (none)")

    print()
    print("placed bounding boxes:")
    for n in sorted(bbs):
        b = bbs[n]
        print(f"  {n:16s} X[{b.xmin:6.1f},{b.xmax:6.1f}] "
              f"Y[{b.ymin:6.1f},{b.ymax:6.1f}] Z[{b.zmin:6.1f},{b.zmax:6.1f}]")


if __name__ == "__main__":
    main()
