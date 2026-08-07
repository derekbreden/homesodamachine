"""Front half — the refrigeration stratum, the flavor manifold standing on it, and the cold
core behind the pair.

Four bodies, mated face to face with nothing between them:

    compressor-shroud   its INTAKE-side face against
    condenser+fan       turned onto it, and the pair yawed as one by `BASE_YAW`
    manifold-layout     set down on the crown of those two, on the four SPINE HAIRPINS
    foam-assembly       at the machine's own `FOAM_YAW`, on the floor, its front face on the
                        plane the front half ends at

The gaps are 0 by intent. The compressor stands well inside its shroud and its ports go
wherever they are put; the condenser's inlet and outlet are cornered but leave by whichever
of that corner's faces is convenient; the cold core's ten ports all stand on one column of
its own. So the bodies touching is what makes the runs between them short.

Frame
-----
- X = width, everything centred on x = 0 — the manifold is mirror-symmetric about it.
- Y = depth, 0 at the front. The refrigeration base, then the cold core behind it; on the
  base, the manifold's pumps forward and its two valve decks aft.
- Z = height, 0 at the floor the shroud and the core both stand on.

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

What it then sets down ON is the four spine hairpins, not any body: the fold put them on the
pack's own underside and they reach past the pump-head faces. They sit at the AFT end, under
the valve decks, where the pumps are forward — so the pack rests on four tube arcs and the
pump faces stand clear of the crown by what the hairpins reach.

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
           _hw / "printed-parts" / "enclosure" / "enclosure"):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly              # noqa: E402
import condenser_block as _cond                       # noqa: E402
import enclosure as _enc                              # noqa: E402
import manifold_layout as ml                          # noqa: E402

SHROUD_STEP = _hw / "cut-parts" / "compressor-shroud" / "compressor-shroud.step"
FOAM_STEP = _hw / "printed-parts" / "cold-core" / "foam-assembly" / "foam-assembly.step"
SEAFLO_STEP = _hw / "reference" / "seaflo-22-pump" / "seaflo-22-pump.step"

# The placement anchors. Each is a turn a body is installed at, and the machine holds
# them rather than the bodies: two bodies mating face to face agree about one turn.
#
# `FOAM_YAW` is the whole edition. +90° about Z carries the cold core's local +X onto
# world +Y, so its long axis runs front-to-back and its SHORT axis (181) runs across
# the machine. The face the shell cuts every penetration in is its local −X, and the
# same turn puts that face on world −Y, facing the user.
FOAM_YAW = 90.0
# The compressor stands UPRIGHT in its shroud: the can's oil sits in its bottom and the
# pickup is gravity-fed, so upright is the compressor's constraint and the turn the
# shroud is free in is a yaw.
SHROUD_YAW = -90.0
# The water pump lies flat on the core's crown. Its barbs are molded into the casting
# and leave its ±Y side faces, so this yaw lands them on the machine's ±X, and lays its
# 187 mm long axis front-to-back.
SEAFLO_YAW = 90.0

C_SHROUD = cq.Color(0.60, 0.62, 0.66)        # the enclosure pack's own three
C_COND = cq.Color(0.78, 0.55, 0.35)
C_FOAM = cq.Color(0.55, 0.75, 0.95, 0.55)
C_SEAFLO = cq.Color(0.30, 0.45, 0.70)

Z_AXIS = (cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
X_AXIS = (cq.Vector(0, 0, 0), cq.Vector(1, 0, 0))


def box(shape):
    return shape.BoundingBox()


def sit(shape, *, cx=None, y0=None, y1=None, z0=None, dz=None):
    """Move a shape by whole planes: centre it in X, put its near face at `y0` or its far face
    at `y1`, its floor at `z0`, or step it `dz`. Each argument names where a face of its own box
    lands."""
    b = box(shape)
    return shape.translate(cq.Vector(
        0.0 if cx is None else cx - (b.xmin + b.xmax) / 2.0,
        (0.0 if y0 is None else y0 - b.ymin) + (0.0 if y1 is None else y1 - b.ymax),
        (0.0 if z0 is None else z0 - b.zmin) + (dz or 0.0)))


# --- The base: two bodies, one plane between them --------------------------
#
# The pair is built mated and then turned as ONE body about its own centre, because the mating
# is between the two of them and the turn is about where the air goes. `BASE_YAW` is that turn:
# the condenser's `AIRFLOW` axis is its native X and the fan is on the face the air leaves by,
# so the quarter that brings its west face onto the shroud's aft plane also lays the fan on +Y,
# and this puts it back across the cabinet.
BASE_YAW = -90.0


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


def build_foam(front_y: float):
    """The cold core at the machine's own `FOAM_YAW` and on the machine's own floor, its front
    face on the plane the front half ends at. Its native box hangs 20 mm below its origin, so
    the floor is the box's own bottom and not that origin."""
    f = cq.importers.importStep(str(FOAM_STEP)).val().rotate(*Z_AXIS, FOAM_YAW)
    return sit(f, cx=0.0, y0=front_y, z0=0.0)


def build_seaflo(foam):
    """The water pump at the machine's own `SEAFLO_YAW`, lying flat on the core's crown, centred
    on the mirror plane, its aft face flush with the core's own back."""
    s = cq.importers.importStep(str(SEAFLO_STEP)).val().rotate(*Z_AXIS, SEAFLO_YAW)
    b = box(foam)
    return sit(s, cx=0.0, y1=b.ymax, z0=b.zmax)


def _whole(bodies):
    out = None
    for s in bodies:
        b = box(s)
        out = b if out is None else out.add(b)
    return out


def place_base(bodies):
    """Turn the mated pair `BASE_YAW` about the vertical through their own combined centre, then
    seat the PAIR — centred on x = 0 and its front face on y = 0. Both moves are rigid and taken
    on the pair's own box, so the plane between them rides along and the crown does not change.

    A yaw about a centre is not a placement: the turn leaves the pair's front wherever its own
    width used to reach, which is not the front of the machine."""
    w = _whole(bodies)
    cx, cy = (w.xmin + w.xmax) / 2.0, (w.ymin + w.ymax) / 2.0
    axis = (cq.Vector(cx, cy, 0.0), cq.Vector(cx, cy, 1.0))
    turned = [s.rotate(*axis, BASE_YAW) for s in bodies]
    t = _whole(turned)
    step = cq.Vector(-(t.xmin + t.xmax) / 2.0, -t.ymin, 0.0)
    return [s.translate(step) for s in turned]


# --- The manifold, laid on their crown -------------------------------------
#
# `(x, y, z) → (−x, z, y)`: a quarter about X puts the pack's own front face — the plane the
# pump heads open on — face down, and a half about Z brings the pumps to the front of it and
# the valve decks behind them. X is negated by the pair, which the mirror does not notice.

def pose_manifold(shape):
    return shape.rotate(*X_AXIS, 90.0).rotate(*Z_AXIS, 180.0)


# What the pack actually sets down on is not a body at all — it is the four spine hairpins.
# The fold turned them onto the pack's own underside, and they hang past the pump-head faces,
# so THEY are the mating surface and the pump faces stand off the crown by whatever is left.
PUMP_FACE_Z = -ml.BARB_INSET                 # where that face lands once the pack is turned


def build_pack() -> cq.Assembly:
    """The bodies, with no box around them. `enclosure` sizes itself off this, so it
    cannot be in it."""
    a = cq.Assembly(name="front-half")
    shroud, cond = place_base([build_shroud(), build_condenser(build_shroud())])
    a.add(shroud, name="compressor-shroud", color=C_SHROUD)
    a.add(cond, name="condenser+fan", color=C_COND)

    posed = [(c.name, pose_manifold((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation()))), c.color) for c in ml.build_assembly().children]
    crown = max(box(shroud).zmax, box(cond).zmax)
    lift = crown - min(box(s).zmin for _n, s, _c in posed)
    stood = [(n, s.translate(cq.Vector(0.0, 0.0, lift)), c) for n, s, c in posed]
    for name, solid, color in stood:
        a.add(solid, name=name, color=color)
    # What the core butts is whatever the front half presents AT THE CORE'S OWN HEIGHT. The
    # source valves' quarter turns carry them aft over the core's crown, and a body standing
    # over it is not a body in its way — so the seam is measured against the bodies that reach
    # below that crown, and the ones above it are left to overhang.
    top = box(build_foam(0.0)).zmax
    aft = max([box(shroud).ymax, box(cond).ymax]
              + [box(s).ymax for _n, s, _c in stood if box(s).zmin < top])
    foam = build_foam(aft)
    a.add(foam, name="foam-assembly", color=C_FOAM)
    a.add(build_seaflo(foam), name="seaflo-pump", color=C_SEAFLO)
    return a


def _solids(a: cq.Assembly):
    """The assembly's children as world-placed solids, keyed by name — the shape a box
    reads a pack in."""
    return {c.name: ((c.obj.val() if hasattr(c.obj, "val") else c.obj).moved(
        cq.Location(c.loc.wrapped.Transformation())), c.color) for c in a.children}


def pack() -> "_enc.Pack":
    """What the enclosure stands around: the placed bodies, and the stations they put on
    its walls.

    Every station field is empty. A station is a hole, a boss or a rail the wall carries
    FOR a body, and this pack carries the refrigeration stratum, the flavour manifold, the
    cold core and the water pump — none of which touches a wall. The funnel's throat, the
    drip tray's rails and slot, the mains inlet's bosses and the panel through-holes each
    arrive with the body they are for."""
    return _enc.Pack(placed=_solids(build_pack()))


# --- the box those bodies stand in -----------------------------------------

WALL_COLORS = {"front-bottom": cq.Color(0.72, 0.74, 0.78, 0.30),
               "front-top": cq.Color(0.80, 0.82, 0.86, 0.30),
               "back-bottom": cq.Color(0.66, 0.68, 0.72, 0.30),
               "back-top": cq.Color(0.74, 0.76, 0.80, 0.30)}


def build_front_half() -> cq.Assembly:
    """The pack, and the four printable pieces of the box around it."""
    a = build_pack()
    box = _enc.box_around(_enc.Pack(placed=_solids(a)))
    for name, piece in _enc.build_pieces(box)[0].items():
        a.add(piece, name=f"enclosure-{name}", color=WALL_COLORS[name])
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
    fo, sf = box(named["foam-assembly"]), box(named["seaflo-pump"])
    line("compressor-shroud", sh)
    line("condenser+fan", co)
    pack = None
    for n, s in placed:
        if n in ("compressor-shroud", "condenser+fan", "foam-assembly", "seaflo-pump"):
            continue
        if n.startswith("enclosure-"):
            continue
        b = box(s)
        pack = b if pack is None else pack.add(b)
    line("manifold-layout", pack)
    line("foam-assembly", fo)
    line("seaflo-pump", sf)
    walls = None
    for n, s in placed:
        if not n.startswith("enclosure-"):
            continue
        b = box(s)
        walls = b if walls is None else walls.add(b)
    if walls is not None:
        line("enclosure", walls)
    print(f"\nmates (0 by intent)")
    seam = "y" if abs(BASE_YAW) % 180.0 < 1e-9 else "x"
    lo, hi = (sh.ymax, co.ymin) if seam == "y" else (sh.xmax, co.xmin)
    print(f"  shroud face      {seam} {lo:.2f}   condenser intake face {seam} {hi:.2f}   "
          f"gap {hi - lo:.2f}")
    crown = max(sh.zmax, co.zmax)
    pump_face = min(box(s).zmin for n, s in placed if n.endswith("-head"))
    print(f"  base crown       z {crown:.2f}   spine hairpins       z {pack.zmin:.2f}   "
          f"gap {pack.zmin - crown:.2f}")
    print(f"  the pump-head faces stand z {pump_face:.2f}, {pump_face - crown:.2f} mm over the "
          f"crown — that band is what the hairpins reach, and they are aft of the pumps")
    print(f"  the base's own two crowns differ by {abs(sh.zmax - co.zmax):.2f}")
    base_aft = max(sh.ymax, co.ymax)
    print(f"  base aft face    y {base_aft:.2f}   foam front face      y {fo.ymin:.2f}   "
          f"gap {fo.ymin - base_aft:.2f}")
    print(f"  core crown       z {fo.zmax:.2f}   seaflo floor         z {sf.zmin:.2f}   "
          f"gap {sf.zmin - fo.zmax:.2f}")
    print(f"  core aft face    y {fo.ymax:.2f}   seaflo aft face      y {sf.ymax:.2f}   "
          f"flush by {sf.ymax - fo.ymax:.2f}; it clears the pack by {sf.ymin - pack.ymax:.2f} mm")
    over = [(n, box(s)) for n, s in placed
            if n not in ("compressor-shroud", "condenser+fan", "foam-assembly", "seaflo-pump")
            and not n.startswith("enclosure-")
            and box(s).ymax > fo.ymin + 1e-6]
    if over:
        reach = max(b.ymax for _n, b in over) - fo.ymin
        floor = min(b.zmin for _n, b in over)
        print(f"  {len(over)} pack bodies overhang the core by up to {reach:.2f} mm, "
              f"clearing its crown by {floor - fo.zmax:.2f}: "
              + ", ".join(sorted(n for n, _b in over)))
    # Which body each hairpin sets down on, and whether it reaches — the two crowns are not
    # level, so a hairpin over the lower one is bearing on nothing.
    for n, s in sorted(placed):
        if not n.startswith("tube-fluid-"):
            continue
        b = box(s)
        if b.zmin - pack.zmin > 1e-6:
            continue
        on = "shroud" if sh.xmin <= (b.xmin + b.xmax) / 2 <= sh.xmax else "condenser"
        under = sh.zmax if on == "shroud" else co.zmax
        print(f"  {n:16} x {(b.xmin + b.xmax) / 2:7.2f} sets down on the {on:9} "
              f"crown z {under:.2f}  gap {b.zmin - under:.2f}")
    print(f"\nfront half        {whole.xlen:.2f} × {whole.ylen:.2f} × {whole.zlen:.2f}   "
          f"({whole.xlen * whole.ylen * whole.zlen / 1e6:.2f} L)")
    print(f"                  x[{whole.xmin:.2f},{whole.xmax:.2f}] "
          f"y[{whole.ymin:.2f},{whole.ymax:.2f}] z[{whole.zmin:.2f},{whole.zmax:.2f}]")


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
    ml.render_elevations(out, xray="enclosure*")


if __name__ == "__main__":
    main()
