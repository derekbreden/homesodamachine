"""OCCT's volume, area and bounds for the helix sweeps `screw.rs` builds, written to
`screw_reference.json` beside this file. Plain CadQuery: it imports no generator.

    tools/run --cad -- tools/cad-venv/bin/python tools/hsm/kernel/tests/screw_reference.py
"""

import json
from pathlib import Path

import cadquery as cq
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepAdaptor import BRepAdaptor_Surface
from OCP.GeomAbs import GeomAbs_Plane

HERE = Path(__file__).resolve().parent


def props(shape):
    """Volume, area, the tight bounds — a swept surface's control net lies outside it, so the
    bounds are OCCT's optimal box of the exact surfaces, not the box of its poles — and the
    normal of each plane face, lowest first."""
    s = shape.val() if isinstance(shape, cq.Workplane) else shape
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(s.wrapped, box, False, False)
    planes = []
    for f in s.Faces():
        a = BRepAdaptor_Surface(f.wrapped)
        if a.GetType() == GeomAbs_Plane:
            n = f.normalAt()
            planes.append((f.Center().z, [n.x, n.y, n.z]))
    return {
        "volume": s.Volume(),
        "area": s.Area(),
        "bbox": list(box.Get()),
        "plane_normals": [n for _, n in sorted(planes)],
    }


MANDREL_PITCH = 12.325584919167285
MANDREL_TURNS = 119.4 / MANDREL_PITCH


def groove(turns=2.0, z0=0.0, frenet=False, pitch=12.33):
    """The coil mandrel's groove: a 3.175 mm circle in the X-Z plane through the helix's start,
    swept along a 63.675 mm helix — in OCCT's corrected Frenet frame, as the mandrel cuts it, or
    in the Frenet frame."""
    radius = 63.675
    helix = cq.Wire.makeHelix(pitch=pitch, height=pitch * turns, radius=radius).translate((0, 0, z0))
    plane = cq.Plane(origin=helix.startPoint().toTuple(), xDir=(0, 0, 1), normal=(0, 1, 0))
    return cq.Workplane(plane).circle(3.175).sweep(cq.Workplane(obj=helix), isFrenet=frenet)


def thread_left():
    """A 2 x 1.5 mm rectangle on a left-handed 10 mm helix of 4 mm pitch, two turns, in the
    helix's Frenet frame."""
    helix = cq.Wire.makeHelix(pitch=4.0, height=8.0, radius=10.0, lefthand=True)
    plane = cq.Plane(origin=helix.startPoint().toTuple(), xDir=(1, 0, 0), normal=(0, 1, 0))
    return cq.Workplane(plane).rect(2.0, 1.5).sweep(cq.Workplane(obj=helix), isFrenet=True)


def grooved_ring():
    """A 61.5 / 56.5 mm ring 40 mm tall, the groove wound two turns into it from z = 5."""
    ring = cq.Workplane("XY").circle(61.5).circle(56.5).extrude(40.0)
    return ring.cut(groove(2.0, 5.0))


CASES = {
    "helix_groove": groove,
    "helix_groove_mandrel": lambda: groove(MANDREL_TURNS, pitch=MANDREL_PITCH),
    "helix_grooved_ring": grooved_ring,
    "screw_groove": lambda: groove(frenet=True),
    "screw_thread_left": thread_left,
}


def main():
    out = {name: props(build()) for name, build in CASES.items()}
    (HERE / "screw_reference.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    for name, p in out.items():
        print(f"{name:20} volume {p['volume']:.4f}  area {p['area']:.4f}")


if __name__ == "__main__":
    main()
