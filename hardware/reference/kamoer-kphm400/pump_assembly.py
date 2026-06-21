"""Pump assembly: the Kamoer KPHM400 pump with a 90° elbow on each outlet.

The bare pump body comes from `kamoer_kphm400` (head, rotor housing, motor),
seated live so the pump geometry stays single-sourced. Onto each of the pump's
two +Y outlet ports sits a 90° union elbow — the `elbow-connector` reference
fitting (a McMaster stand-in for the John Guest PP0308E) — turning each line up
(+Z) off the outlet.

Authored in the same pump-case world frame as `kamoer_kphm400`: origin at the
base-plate bore-opening face, depth axis along +Z. Each elbow's inlet leg is
coaxial with its outlet port (X = `arch_xs`, Z = `arch_plane_z`), its collet
face flush with the pump body's +Y face (`body_y_face`); the bend then turns
the line to +Z.
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

ELBOW_STEP = _hw / "reference" / "elbow-connector" / "elbow-connector.step"
ELBOW_COLOR = cq.Color(0.15, 0.15, 0.16)  # black PP fitting


def _elbow(bx):
    """One 90° elbow seated on the +Y outlet at X = bx. Its inlet leg is
    coaxial with the outlet port, collet face flush with the pump body's +Y
    face; the bend turns the line to +Z."""
    el = cq.importers.importStep(str(ELBOW_STEP)).val()
    leg = el.BoundingBox().ymax                # bend-corner-to-collet-face reach
    # Native frame: one leg runs +Y (collet at +leg), the other +Z, bend at the
    # origin. Spin 180° about Z so the first leg faces the pump (-Y) to mate the
    # outlet, leaving the second leg pointing +Z.
    el = el.rotate((0, 0, 0), (0, 0, 1), 180)
    # Inlet axis now at X=0, Z=0 with its collet at Y=-leg; drop it onto the
    # port so the collet face lands flush on the pump body's +Y face.
    return el.translate((bx, kp.body_y_face + leg, kp.arch_plane_z))


def _elbows():
    return [_elbow(bx) for bx in kp.arch_xs]


def build_assembly():
    a = cq.Assembly(name="pump-assembly")
    for name, builder, color in kp.BODY_PARTS:
        a.add(builder(), name=name, color=color)
    for side, elbow in zip(("pos", "neg"), _elbows()):
        a.add(elbow, name=f"elbow_{side}", color=ELBOW_COLOR)
    return a


def build_scene():
    parts = [builder().val() for _, builder, _ in kp.BODY_PARTS]
    return cq.Compound.makeCompound(parts + _elbows())


def main():
    export_assembly(build_assembly(), str(_here.parent / "pump-assembly.step"))
    bb = build_scene().BoundingBox()
    print("-> pump-assembly.step")
    print("assembly envelope  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (Z = depth axis, motor +Z)"
          % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))


if __name__ == "__main__":
    main()
