"""1/4" push-to-connect union tee (John Guest PP0208E) — the water split that
sits on the ASSE 1022's 1/4" outlet and feeds the two valves downstream of the
backflow preventer: the ASSE supply enters the branch and splits along the run to
V-K (the fill/shutoff on the way to the SeaFlo suction) and to the flavor tap
(flow regulator → V-A). All three ports are 1/4" PTC — the split needs no
reducers, because the water reaches it at 1/4" and leaves at 1/4"
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2).

Geometric stand-in: a McMaster-class 1/4" PTC tee, close to the PP0208E — three
collets meeting at the body centre, run half-length and branch reach both
20.07 mm, collet OD 13.7 mm, 1/4" (6.35 mm) bore. Reconcile against a measured
PP0208E as parts come in hand (same note as reference/tee-connector).

Frame: the run along ±Y, the supply at +Y and the flavor tap at −Y, and the branch
along −X at a right angle to both. Centre at the origin, the three collet faces in
the Z = 0 plane. Which of the three ends up pointing where is the enclosure's to
say — it turns this frame on the way in ([`front_half.py`](/hardware/manifold-layout/front_half.py)
`SPLIT_TURN`), and the branch is the port that turn is FOR:
it is the only one of the three that can be given a level of its own.

Run:
    tools/cad-venv/bin/python hardware/reference/water-split/water_split.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

COLLET_D = 13.7      # 1/4" PTC collet OD (McMaster 1/4" tee, close to the PP0208E)
REACH = 20.07        # collet face from the body centre — run half-length and branch alike
TUBE_D = 6.35        # 1/4" OD LLDPE the three ports accept
HUB = 14.0           # central body


def supply():
    """The +Y run collet the 1/4" line from the ASSE 1022 outlet pushes into:
    (position, outward axis)."""
    return (0.0, REACH, 0.0), (0.0, 1.0, 0.0)


def to_vk():
    """The branch collet feeding V-K, on to the SeaFlo suction: (position, axis).
    It takes V-K's share off the run at a right angle — the one port of the three
    the enclosure can point at a level the other two are not on."""
    return (-REACH, 0.0, 0.0), (-1.0, 0.0, 0.0)


def to_flavor():
    """The −Y run collet feeding the flavor tap — flow regulator → V-A: the
    supply's own line carried straight on: (position, axis)."""
    return (0.0, -REACH, 0.0), (0.0, -1.0, 0.0)


def build():
    """Run collets along ±Y, branch collet along −X, meeting at a central hub."""
    run = cq.Solid.makeCylinder(
        COLLET_D / 2.0, 2 * REACH, cq.Vector(0, -REACH, 0), cq.Vector(0, 1, 0))
    branch = cq.Solid.makeCylinder(
        COLLET_D / 2.0, REACH, cq.Vector(0, 0, 0), cq.Vector(-1, 0, 0))
    hub = cq.Workplane("XY").box(HUB, HUB, HUB).val()
    return run.fuse(branch).fuse(hub)


def main():
    part = build()
    bb = part.BoundingBox()
    print("1/4\" PTC union tee — water split (ASSE outlet -> V-K + flavor tap)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    for label, (pos, axis) in (("supply   ", supply()), ("to-vk    ", to_vk()),
                               ("to-flavor", to_flavor())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    out = _here.parent / "water-split.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
