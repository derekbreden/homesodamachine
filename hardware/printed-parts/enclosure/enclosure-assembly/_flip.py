"""Flip-nesting test: a tray flipped 180 deg about a HORIZONTAL axis (floor on
top, valves/elbows pointing DOWN) nests into a normal tray (valves up) so the
two combs interleave through each other's air. Search the nest offset for min
real-solid overlap, keeping both within one back-top row.
"""
import sys
from pathlib import Path
import cadquery as cq
_here = Path(__file__).resolve(); sys.path.insert(0, str(_here.parent))
import _contents as c

_raw = {k: c._load(p) for k, p in c.TRAY_STEPS.items()}

def prep(name, flip=None, zrot=0.0):
    s = _raw[name]
    if zrot: s = s.rotate((0,0,0),(0,0,1),zrot)
    if flip: s = s.rotate((0,0,0), flip, 180.0)
    return s

def at(s, x, y, z):
    b = s.BoundingBox(); return s.translate((x-b.xmin, y-b.ymin, z-b.zmin))

def ov(a, b):
    ba, bb = a.BoundingBox(), b.BoundingBox()
    if (ba.xmax<bb.xmin or bb.xmax<ba.xmin or ba.ymax<bb.ymin or bb.ymax<ba.ymin or ba.zmax<bb.zmin or bb.zmax<ba.zmin):
        return 0.0
    try: return a.intersect(b).Volume()
    except Exception: return 0.0

def search(A, B, flipB, dxs, dzs, tag):
    a = at(prep(A), 0.0, 0.0, 0.0)             # normal, valves up
    ab = a.BoundingBox()
    best = None
    for dx in dxs:
        for dz in dzs:
            b = at(prep(B, flip=flipB), dx, 0.0, dz)   # flipped, nested
            bb = b.BoundingBox()
            w = max(ab.xmax, bb.xmax) - min(ab.xmin, bb.xmin)
            h = max(ab.zmax, bb.zmax) - min(ab.zmin, bb.zmin)
            v = ov(a, b)
            rec = (v, w, h, dx, dz)
            if best is None or v < best[0]:
                best = rec
    v, w, h, dx, dz = best
    print(f"{tag:28s} flip={flipB}  BEST ov={v:8.0f}  width={w:.0f} height={h:.0f}  dx={dx} dz={dz}", flush=True)
    return best

if __name__ == "__main__":
    fX, fY = (1,0,0), (0,1,0)
    # reproduce: bag + nozzle nested
    print("=== reproduce other agent: bag + nozzle nested ===", flush=True)
    search("bag-circuit", "nozzle-gate", fX, range(0,90,15), range(-6,7,3), "bag+noz(flipX)")
    search("bag-circuit", "nozzle-gate", fY, range(0,90,15), range(-6,7,3), "bag+noz(flipY)")
    # wide pairing: source + nozzle (row1), bag + bib (row2)
    print("=== wide pairs ===", flush=True)
    search("source-select", "nozzle-gate", fX, range(40,150,15), range(-6,7,3), "src+noz(flipX)")
    search("source-select", "nozzle-gate", fY, range(40,150,15), range(-6,7,3), "src+noz(flipY)")
    search("bag-circuit", "bib-gate", fX, range(0,60,12), range(-6,7,3), "bag+bib(flipX)")
    search("bag-circuit", "bib-gate", fY, range(0,60,12), range(-6,7,3), "bag+bib(flipY)")
