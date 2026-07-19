"""Pump assembly: the Kamoer KPHM400 pump, its two outlet ports flush.

The bare pump body comes from `kamoer_kphm400` (head, rotor housing, motor),
seated live so the pump geometry stays single-sourced. No fittings ride the
ports: the pump's two +Y outlets stand as clean flush ports on the body's +Y
face (`body_y_face`), at X = `arch_xs`, Z = `arch_plane_z` — the anchors any
downstream fitting or tube seats on.

Authored in the same pump-case world frame as `kamoer_kphm400`: origin at the
base-plate bore-opening face, depth axis along +Z.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _here.parent):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import kamoer_kphm400 as kp


def build_assembly():
    a = cq.Assembly(name="pump-assembly")
    for name, builder, color in kp.BODY_PARTS:
        a.add(builder(), name=name, color=color)
    return a


def build_scene():
    parts = [builder().val() for _, builder, _ in kp.BODY_PARTS]
    return cq.Compound.makeCompound(parts)


def main():
    export_assembly(build_assembly(), str(_here.parent / "pump-assembly.step"))
    bb = build_scene().BoundingBox()
    print("-> pump-assembly.step")
    print("assembly envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (Z = depth axis, motor +Z)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    print("flush outlet ports: X = %s on the +Y face y = %.3f, Z = %.1f"
          % (kp.arch_xs, kp.body_y_face, kp.arch_plane_z))


if __name__ == "__main__":
    main()
