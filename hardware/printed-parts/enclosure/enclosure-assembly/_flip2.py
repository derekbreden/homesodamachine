"""Refined flip-nest: add a Y-offset (interleave the two valve rows) + finer dx/dz."""
import sys
from pathlib import Path
import cadquery as cq
_here = Path(__file__).resolve(); sys.path.insert(0, str(_here.parent))
import _contents as c
_raw = {k: c._load(p) for k, p in c.TRAY_STEPS.items()}

def prep(name, flip=None):
    s = _raw[name]
    if flip: s = s.rotate((0,0,0), flip, 180.0)
    return s
def at(s,x,y,z):
    b=s.BoundingBox(); return s.translate((x-b.xmin,y-b.ymin,z-b.zmin))
def ov(a,b):
    ba,bb=a.BoundingBox(),b.BoundingBox()
    if (ba.xmax<bb.xmin or bb.xmax<ba.xmin or ba.ymax<bb.ymin or bb.ymax<ba.ymin or ba.zmax<bb.zmin or bb.zmax<ba.zmin): return 0.0
    try: return a.intersect(b).Volume()
    except Exception: return 0.0

def search(A,B,dx0,tag):
    a=at(prep(A),0,0,0); ab=a.BoundingBox()
    best=None
    for fl in [(1,0,0),(0,1,0)]:
        for dx in [dx0-8,dx0,dx0+8]:
            for dy in [-18,-9,0,9,18]:
                for dz in [3,7]:
                    b=at(prep(B,flip=fl),dx,dy,dz); bb=b.BoundingBox()
                    w=max(ab.xmax,bb.xmax)-min(ab.xmin,bb.xmin)
                    if w>284: continue
                    v=ov(a,b)
                    if best is None or v<best[0]: best=(v,w,fl,dx,dy,dz)
    v,w,fl,dx,dy,dz=best
    print(f"{tag:14s} BEST ov={v:8.0f} width={w:.0f} flip={fl} dx={dx} dy={dy} dz={dz}",flush=True)
    return best

if __name__=="__main__":
    search("source-select","nozzle-gate",70,"src+noz")
    search("source-select","bib-gate",55,"src+bib")
    search("bag-circuit","nozzle-gate",15,"bag+noz")
    search("bag-circuit","bib-gate",18,"bag+bib")
