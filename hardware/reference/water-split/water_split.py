"""1/4" push-to-connect union tee (John Guest PP0208E) — the water split that
sits on the ASSE 1022's 1/4" outlet and feeds the two valves downstream of the
backflow preventer: the ASSE supply enters the branch and splits along the run to
V-K (the fill/shutoff on the way to the SeaFlo suction) and to the flavor tap
(flow regulator → V-A). All three ports are 1/4" PTC — the split needs no
reducers, because the water reaches it at 1/4" and leaves at 1/4"
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2).

The solid is `reference/tee-connector`'s — the same harvested fitting the manifold's six
junctions are built from, turned into the frame below. Its figures are measured off that STEP
and held to it at import, so the barrel a rib closes on and the collet faces a tube pushes into
are the fitting's own and not a drawing of one.

Frame: the run along ±Y, the supply at +Y and the flavor tap at −Y, and the branch along −X at a
right angle to both. Centre at the origin, the three collet faces in the Z = 0 plane. Which of the
three ends up pointing where is the enclosure's to say — it turns this frame on the way in
([`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) `SPLIT_TURN`), and the
branch is the port that turn is FOR: it is the only one of the three that can be given a level of
its own.

Run:
    tools/cad-venv/bin/python hardware/reference/water-split/water_split.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "reference" / "tee-connector"))
from _cadq_export import export_step, import_step
import tee_connector as tee

REACH = tee.RUN_HALF         # collet face from the body centre — run half-length and branch alike
TUBE_D = tee.TUBE_D          # 1/4" OD LLDPE the three ports accept

# What carries the tee's frame into this one: its run from ±Z onto ±Y, and its branch from +Y
# onto −X. A roll about X stands the run up, and a roll about the run swings the branch.
_TURNS = (((1.0, 0.0, 0.0), -90.0), ((0.0, 1.0, 0.0), 90.0))


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


def run_barrel():
    """The barrel on the SUPPLY arm — `(station, radius, length)`.

    The shape a printed seat can close on. The hub is where all three arms meet and the branch is
    the port this fitting is turned for, so what is left is the run, and the supply half of it is
    the half with nothing downstream of it to fight for the joint's position.

    `station` is its mid-point and the run axis through it, in the frame the three ports are
    stated in."""
    near, far = tee.BARREL_NEAR, tee.BARREL_FAR
    return (((0.0, (near + far) / 2.0, 0.0), (0.0, 1.0, 0.0)),
            tee.BARREL_R, far - near)


def build():
    """The harvested fitting, run collets along ±Y and branch collet along −X."""
    solid = import_step(str(tee.STEP)).val()
    for axis, deg in _TURNS:
        solid = solid.rotate(cq.Vector(0, 0, 0), cq.Vector(*axis), deg)
    return solid


def stations_hold():
    """Hold the three ports to the turned solid — each collet face on the body's own box."""
    bb = build().BoundingBox()
    for label, (pos, _axis), actual in (("supply", supply(), bb.ymax),
                                        ("to-flavor", to_flavor(), bb.ymin),
                                        ("to-vk", to_vk(), bb.xmin)):
        claimed = max((c for c in pos), key=abs)
        if abs(actual - claimed) > tee.MEASURE_TOL:
            raise ValueError(
                f"water-split {label} stands at {claimed:g} and the turned solid's own face is "
                f"at {actual:.4f} — the frame this file states is not the frame `_TURNS` builds.")


def main():
    tee.stations_hold()
    stations_hold()
    part = build()
    bb = part.BoundingBox()
    print("1/4\" PTC union tee — water split (ASSE outlet -> V-K + flavor tap)")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    for label, (pos, axis) in (("supply   ", supply()), ("to-vk    ", to_vk()),
                               ("to-flavor", to_flavor())):
        print(f"  {label}: ({pos[0]:7.2f}, {pos[1]:6.2f}, {pos[2]:7.2f})  out {axis}")
    (station, r, length) = run_barrel()
    print(f"  run barrel: r {r:.3f}, {length:g} mm long, centred at {station[0]}")
    out = _here.parent / "water-split.step"
    export_step(part, str(out))
    print(f"-> {out.name}")


if __name__ == "__main__":
    main()
