"""Front half — the refrigeration stratum with the flavor manifold standing on it.

Three bodies, mated face to face with nothing between them:

    compressor-shroud   its AFT face (+Y) against
    condenser+fan       its WEST face (−X), turned onto the shroud's aft plane
    manifold-layout     its PUMP-HEAD FRONT face laid on the crown of those two

The gaps are 0 by intent. The compressor stands well inside its shroud and its ports go
wherever they are put; the condenser's inlet and outlet are cornered but leave by whichever
of that corner's faces is convenient. So the two bodies touching is what makes the run
between them short, and the same holds for the foam shell when it arrives.

Frame
-----
- X = width, everything centred on x = 0 — the manifold is mirror-symmetric about it.
- Y = depth, 0 at the front. Shroud, then condenser behind it; the manifold's pumps forward
  and its two valve decks aft.
- Z = height, 0 at the floor the shroud stands on.

What the mating does to each body
---------------------------------
The **shroud** keeps the machine's own `SHROUD_YAW`: the compressor is a can whose oil sits
in its bottom and whose pickup is gravity-fed, so upright is the compressor's constraint and
the turn can only be a yaw.

The **condenser** turns a quarter about Z to bring its west face onto the shroud's aft plane.
That carries its `AIRFLOW` axis with it — across the machine before, front-to-back after — so
the air crosses the cabinet the short way and the finstack faces the two side walls.

The **manifold** turns a quarter about X and a half about Z, which is the one pose that lays
its pump-head front face down. Its own +Z — the axis its two valve decks stack on — comes to
+Y, so the decks stand aft of the pumps rather than over them, and every mouth that faced the
back now faces up.

Run it
------
    tools/cad-venv/bin/python hardware/manifold-layout/front_half.py
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts", _here.parent,
           _hw / "cut-parts" / "compressor-shroud",
           _hw / "reference" / "condenser-block",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "enclosure-assembly"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly              # noqa: E402
import condenser_block as _cond                       # noqa: E402
import _contents                                      # noqa: E402
import manifold_layout as ml                          # noqa: E402

SHROUD_STEP = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
SHROUD_YAW = _contents.SHROUD_YAW            # the machine's own turn, and the compressor's

C_SHROUD = cq.Color(0.60, 0.62, 0.66)        # the enclosure pack's own two
C_COND = cq.Color(0.78, 0.55, 0.35)

Z_AXIS = (cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
X_AXIS = (cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))


def box(shape):
    return shape.BoundingBox()


def sit(shape, *, cx=None, y0=None, z0=None, dz=None):
    """Move a shape by whole planes: centre it in X, put its near face at `y0`, its floor at
    `z0`, or step it `dz`. Each argument names where a face of its own box lands."""
    b = box(shape)
    return shape.translate(cq.Vector(
        0.0 if cx is None else cx - (b.xmin + b.xmax) / 2.0,
        0.0 if y0 is None else y0 - b.ymin,
        (0.0 if z0 is None else z0 - b.zmin) + (dz or 0.0)))


# --- The base: two bodies, one plane between them --------------------------

def build_shroud():
    """The shroud as the machine turns it, its front face on y = 0 and its feet on the floor."""
    s = cq.importers.importStep(str(SHROUD_STEP)).val().rotate(*Z_AXIS, SHROUD_YAW)
    return sit(s, cx=0.0, y0=0.0, z0=0.0)


def build_condenser(shroud):
    """The block turned a quarter about Z, which brings the WEST face the mating names round
    onto the shroud's own aft plane, and stood on the same floor."""
    c = _cond.build()
    c = c.toCompound() if hasattr(c, "toCompound") else c
    return sit(c.rotate(*Z_AXIS, 90.0), cx=0.0, y0=box(shroud).ymax, z0=0.0)


# --- The manifold, laid on their crown -------------------------------------
#
# `(x, y, z) → (−x, z, y)`: a quarter about X puts the pack's own front face — the plane the
# pump heads open on — face down, and a half about Z brings the pumps to the front of it and
# the valve decks behind them. X is negated by the pair, which the mirror does not notice.

def pose_manifold(shape):
    return shape.rotate(*X_AXIS, 90.0).rotate(*Z_AXIS, 180.0)


PUMP_FACE_Z = -ml.BARB_INSET                 # where that face lands once the pack is turned


def build_front_half() -> cq.Assembly:
    a = cq.Assembly(name="front-half")
    shroud = build_shroud()
    cond = build_condenser(shroud)
    a.add(shroud, name="compressor-shroud", color=C_SHROUD)
    a.add(cond, name="condenser+fan", color=C_COND)

    crown = max(box(shroud).zmax, box(cond).zmax)
    lift = crown - PUMP_FACE_Z               # pump-head front face onto the base's crown
    for c in ml.build_assembly().children:
        solid = (c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
            cq.Location(c.loc.wrapped.Transformation()))
        a.add(sit(pose_manifold(solid), dz=lift), name=c.name, color=c.color)
    return a


def report(a: cq.Assembly) -> None:
    placed = [(c.name, (c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation()))) for c in a.children]
    named = dict(placed)
    whole = None
    for _n, s in placed:
        b = box(s)
        whole = b if whole is None else whole.add(b)

    def line(label, b):
        print(f"  {label:20} x[{b.xmin:8.2f},{b.xmax:8.2f}] y[{b.ymin:7.2f},{b.ymax:7.2f}] "
              f"z[{b.zmin:7.2f},{b.zmax:7.2f}]   {b.xlen:6.2f} × {b.ylen:6.2f} × {b.zlen:6.2f}")

    print("\nbodies")
    sh, co = box(named["compressor-shroud"]), box(named["condenser+fan"])
    line("compressor-shroud", sh)
    line("condenser+fan", co)
    pack = None
    for n, s in placed:
        if n in ("compressor-shroud", "condenser+fan"):
            continue
        b = box(s)
        pack = b if pack is None else pack.add(b)
    line("manifold-layout", pack)
    print(f"\nmates (0 by intent)")
    print(f"  shroud aft face  y {sh.ymax:.2f}   condenser west face  y {co.ymin:.2f}   "
          f"gap {co.ymin - sh.ymax:.2f}")
    crown = max(sh.zmax, co.zmax)
    print(f"  base crown       z {crown:.2f}   pump-head front face z {crown:.2f}   gap 0.00")
    print(f"  the base's own two crowns differ by {abs(sh.zmax - co.zmax):.2f}")
    print(f"\nfront half        {whole.xlen:.2f} × {whole.ylen:.2f} × {whole.zlen:.2f}   "
          f"({whole.xlen * whole.ylen * whole.zlen / 1e6:.2f} L)")
    print(f"                  x[{whole.xmin:.2f},{whole.xmax:.2f}] "
          f"y[{whole.ymin:.2f},{whole.ymax:.2f}] z[{whole.zmin:.2f},{whole.zmax:.2f}]")
    print(f"  the pack reaches {crown - pack.zmin:.2f} mm BELOW the plane it is mated on — "
          f"the four spine hairpins hang past the pump faces")

    bad, unanswered = ml.clashes(a)
    print(f"\nclash check: {len(bad)} pair(s) sharing volume, "
          f"{len(unanswered)} the boolean would not answer for")
    for ni, nj, v in bad:
        print(f"  {ni} ∩ {nj}   {v:.1f} mm³")
    for ni, nj, why in unanswered:
        print(f"  {ni} ? {nj}   {why}")


def main():
    a = build_front_half()
    out = _here.parent / "front-half.step"
    export_assembly(a, str(out))
    print(f"-> {out.name}")
    report(a)
    ml.render_elevations(out)


if __name__ == "__main__":
    main()
