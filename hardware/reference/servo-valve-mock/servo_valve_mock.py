"""Mock-up: an MG90S micro servo actuating a Neo-Pure NeoFit 1/4" ball valve.

A coarse keep-out approximation for judging the packaging of a servo-driven
ball-valve cell: the all-plastic food-grade ball valve is the wetted path, a
9 g micro servo is the dry external actuator coupled to the stem.

Envelopes are catalog-nominal, not manufacturing drawings:
- NeoFit 1/4" acetal/PP quarter-turn ball valve — ~44 mm push-fit end to end,
  ~16 mm round body, 1/4" (6.35 mm) tube ports, a vertical stem.
- MG90S micro servo — 22.8 mm long x 12.5 mm thin x 22.8 mm tall body,
  31.8 mm across the mounting ears, output spline offset 5.5 mm from center.

Flow runs along X; the valve stem and the servo output share the +Z axis. The
servo's thin (12.5 mm) axis lies along Y — the cross-flow stacking direction —
and is centered on the valve, so it adds no width beyond the valve body. The
servo sits inverted above the valve, output spline pointing down into a coupler
on the stem. The mounting ears extend along X (the free port direction).
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
from _cadq_export import export_assembly


def _xcyl(r, x0, x1):
    return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def _zcyl(r, z0, z1):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


# --- NeoFit 1/4" quarter-turn ball valve (flow along X, stem along +Z) -----
bore = 5.0
body_dia = 16.0
body_len = 18.0
collar_dia = 13.0
collar_len = 5.0
collet_dia = 10.0
collet_len = 8.0
port_len = collar_len + collet_len          # 13 mm reach per side
stem_dia = 7.0
stem_top_z = body_dia / 2.0 + 5.0           # 13.0 — stem protrusion above body top


def build_valve():
    v = cq.Workplane(obj=_xcyl(body_dia / 2.0, -body_len / 2.0, body_len / 2.0))
    for sx in (-1.0, 1.0):
        base = sx * body_len / 2.0
        c0, c1 = sorted((base, base + sx * collar_len))
        n0, n1 = sorted((base + sx * collar_len, base + sx * port_len))
        v = v.union(cq.Workplane(obj=_xcyl(collar_dia / 2.0, c0, c1)))
        v = v.union(cq.Workplane(obj=_xcyl(collet_dia / 2.0, n0, n1)))
    v = v.union(cq.Workplane(obj=_zcyl(stem_dia / 2.0, body_dia / 2.0 - 2.0, stem_top_z)))
    span = body_len / 2.0 + port_len + 1.0
    v = v.cut(cq.Workplane(obj=_xcyl(bore / 2.0, -span, span)))
    return v


# --- Coupler: sleeves over the protruding stem, up to the servo spline ------
coupler_top = stem_top_z + 2.0          # short cap above the stem


def build_coupler():
    # Sleeve over the protruding stem (down to the valve body top) instead of
    # stacking on its end, so the servo drops by the stem's protrusion.
    return cq.Workplane(obj=_zcyl(11.0 / 2.0, body_dia / 2.0, coupler_top))


# --- MG90S micro servo (local frame: output axis at origin, spline up) ------
body_l = 22.8       # long axis, along X (free port direction)
body_w = 12.5       # thin axis, along Y (cross-flow stacking pitch)
body_h = 22.8       # tall axis, along Z
out_offset = 5.5    # spline offset from body center
ear_span = 31.8     # ear tip to ear tip, along X
body_cx = -(body_l / 2.0 - out_offset)      # -5.9
spline_tip = body_h + 1.5 + 3.5


def build_servo_local():
    s = (
        cq.Workplane("XY")
        .box(body_l, body_w, body_h, centered=(True, True, False))
        .translate((body_cx, 0.0, 0.0))
    )
    ear_t = 2.5
    ear_z0 = 16.0
    ear_overhang = (ear_span - body_l) / 2.0      # 4.5
    for sx in (1.0, -1.0):
        edge = body_cx + sx * body_l / 2.0
        mid = edge + sx * ear_overhang / 2.0
        ear = (
            cq.Workplane("XY")
            .box(ear_overhang, body_w, ear_t, centered=(True, True, False))
            .translate((mid, 0.0, ear_z0))
        )
        s = s.union(ear)
        s = s.cut(cq.Workplane(obj=_zcyl(1.0, ear_z0 - 1.0, ear_z0 + ear_t + 1.0).translate((mid, 0, 0))))
    s = s.union(cq.Workplane(obj=_zcyl(3.0, body_h, body_h + 1.5)))          # output boss
    s = s.union(cq.Workplane(obj=_zcyl(2.4, body_h + 1.5, spline_tip)))      # spline
    cable = (
        cq.Workplane("XY")
        .box(4.0, 4.0, 4.0, centered=(True, True, False))
        .translate((body_cx - body_l / 2.0 - 2.0, 0.0, 2.0))
    )
    s = s.union(cable)
    return s


def build_servo_placed():
    s = build_servo_local().val()
    s = s.rotate((0, 0, 0), (1, 0, 0), 180.0)          # invert: spline points -Z
    s = s.translate((0, 0, (coupler_top - 2.0) + spline_tip))
    return cq.Workplane(obj=s)


def _cell_solids():
    return [build_valve().val(), build_coupler().val(), build_servo_placed().val()]


def build_scene():
    return cq.Compound.makeCompound(_cell_solids())


def build_strip(n=3, pitch=16.5):
    out = []
    for i in range(n):
        dy = (i - (n - 1) / 2.0) * pitch
        out.extend(s.translate((0, dy, 0)) for s in _cell_solids())
    return cq.Compound.makeCompound(out)


def build_assembly():
    a = cq.Assembly(name="servo-valve-mock")
    a.add(build_valve(), name="neofit_valve", color=cq.Color(0.80, 0.72, 0.55))
    a.add(build_coupler(), name="coupler", color=cq.Color(0.20, 0.45, 0.75))
    a.add(build_servo_placed(), name="mg90s_servo", color=cq.Color(0.18, 0.18, 0.20))
    return a


def _export_svg(shape, name, out_dir):
    cq.exporters.export(
        cq.Workplane(obj=shape),
        f"{out_dir}/servo_valve_{name}.svg",
        opt={
            "width": 1000,
            "height": 820,
            "projectionDir": (0, 0, 1),
            "showAxes": False,
            "showHidden": False,
            "strokeWidth": 0.45,
        },
    )


def render(out_dir="/tmp"):
    # Rotate the model into a top (0,0,1) projection for each deterministic view.
    scene = build_scene()
    _export_svg(scene.rotate((0, 0, 0), (1, 0, 0), -90.0), "front", out_dir)     # X right, Z up

    def _end(shape):
        # Look down the flow axis X: world Y -> horizontal, world Z -> vertical.
        return shape.rotate((0, 0, 0), (0, 1, 0), 90.0).rotate((0, 0, 0), (0, 0, 1), 90.0)

    _export_svg(_end(scene), "end", out_dir)
    _export_svg(_end(build_strip()), "strip", out_dir)


def main():
    export_assembly(build_assembly(), str(_here.parent / "servo-valve-mock.step"))
    render()
    bb = build_scene().BoundingBox()
    print("-> servo-valve-mock.step")
    print(
        "one cell  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]   (Y = stacking pitch axis)"
        % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)
    )


if __name__ == "__main__":
    main()
