"""Mock-up: an MG90S micro servo actuating a Neo-Pure NeoFit 1/4" ball valve.

A coarse keep-out approximation for judging the packaging of a servo-driven
ball-valve cell: the all-plastic food-grade ball valve is the wetted path, a
9 g micro servo is the dry external actuator coupled to the stem.

Envelopes are catalog-nominal, not manufacturing drawings:
- NeoFit 1/4" acetal/PP quarter-turn ball valve — ~44 mm push-fit end to end,
  16 mm body, 1/4" (6.35 mm) tube ports, a vertical stem.
- MG90S micro servo — 22.8 x 12.2 x 22.5 mm body, 32.2 mm across the mounting
  ears, output spline offset 5.5 mm from the body center, spline on top.

Flow runs along X; the valve stem and the servo output share the +Z axis. The
servo sits inverted above the valve, output spline pointing down into a coupler
on the stem. A thin back-plate stands in for the printed bracket.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
from _cadq_export import export_assembly


def _xcyl(r, x0, x1):
    """Cylinder along +X from x0 to x1."""
    return cq.Solid.makeCylinder(r, x1 - x0, cq.Vector(x0, 0, 0), cq.Vector(1, 0, 0))


def _zcyl(r, z0, z1):
    """Cylinder along +Z from z0 to z1."""
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


# --- NeoFit 1/4" quarter-turn ball valve (flow along X, stem along +Z) -----
BORE = 5.0
body_dia = 16.0
body_len = 18.0
collar_dia = 13.0
collar_len = 5.0
collet_dia = 10.0
collet_len = 8.0
port_len = collar_len + collet_len          # 13 mm reach per side
stem_dia = 7.0
stem_top_z = body_dia / 2.0 + 9.0           # 17.0


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
    v = v.cut(cq.Workplane(obj=_xcyl(BORE / 2.0, -span, span)))
    return v


# --- Coupler: stem top up to the servo spline ------------------------------
coupler_top = 29.0


def build_coupler():
    return cq.Workplane(obj=_zcyl(8.0 / 2.0, stem_top_z, coupler_top))


# --- MG90S micro servo (local frame: output axis at origin, spline up) ------
BODY_L = 22.8
BODY_W = 12.2
BODY_H = 22.5
OUT_OFFSET = 5.5
body_cx = -(BODY_L / 2.0 - OUT_OFFSET)      # -5.9
spline_tip = BODY_H + 1.5 + 3.5             # 27.5 local


def build_servo_local():
    s = (
        cq.Workplane("XY")
        .box(BODY_L, BODY_W, BODY_H, centered=(True, True, False))
        .translate((body_cx, 0.0, 0.0))
    )
    ear_t = 2.5
    ear_z0 = 16.0
    ear_overhang = 4.7
    for sx in (1.0, -1.0):
        edge = body_cx + sx * BODY_L / 2.0
        mid = edge + sx * ear_overhang / 2.0
        hole_x = edge + sx * 2.3
        ear = (
            cq.Workplane("XY")
            .box(ear_overhang, BODY_W, ear_t, centered=(True, True, False))
            .translate((mid, 0.0, ear_z0))
        )
        s = s.union(ear)
        s = s.cut(cq.Workplane(obj=_zcyl(1.0, ear_z0 - 1.0, ear_z0 + ear_t + 1.0).translate((hole_x, 0, 0))))
    s = s.union(cq.Workplane(obj=_zcyl(3.0, BODY_H, BODY_H + 1.5)))          # output boss
    s = s.union(cq.Workplane(obj=_zcyl(2.4, BODY_H + 1.5, spline_tip)))      # spline
    cable = (
        cq.Workplane("XY")
        .box(4.0, 4.0, 4.0, centered=(True, True, False))
        .translate((body_cx - BODY_L / 2.0 - 2.0, 0.0, 2.0))
    )
    s = s.union(cable)
    return s


def build_servo_placed():
    s = build_servo_local().val()
    s = s.rotate((0, 0, 0), (1, 0, 0), 180.0)          # invert: spline points -Z
    s = s.translate((0, 0, (coupler_top - 2.0) + spline_tip))  # spline tip into coupler
    return cq.Workplane(obj=s)


# --- Schematic printed bracket (back-plate) --------------------------------
def build_bracket():
    return (
        cq.Workplane("XY")
        .box(24.0, 3.0, 42.0, centered=(True, True, False))
        .translate((-6.0, -8.5, 12.0))
    )


def build_assembly():
    a = cq.Assembly()
    a.add(build_valve(), name="neofit_valve", color=cq.Color(0.80, 0.72, 0.55))
    a.add(build_coupler(), name="coupler", color=cq.Color(0.20, 0.45, 0.75))
    a.add(build_servo_placed(), name="mg90s_servo", color=cq.Color(0.18, 0.18, 0.20))
    a.add(build_bracket(), name="bracket", color=cq.Color(0.75, 0.75, 0.78))
    return a


def build_scene():
    parts = [
        build_valve().val(),
        build_coupler().val(),
        build_servo_placed().val(),
        build_bracket().val(),
    ]
    return cq.Compound.makeCompound(parts)


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
    # Auto camera-up is unreliable for axis-aligned views, so rotate the
    # model into a top (0,0,1) projection for each deterministic view.
    scene = build_scene()
    _export_svg(scene, "top", out_dir)                                   # plan: X right, Y up
    _export_svg(scene.rotate((0, 0, 0), (1, 0, 0), -90.0), "front", out_dir)   # elevation: X right, Z up
    iso = scene.rotate((0, 0, 0), (0, 0, 1), 25.0).rotate((0, 0, 0), (1, 0, 0), -65.0)
    _export_svg(iso, "iso", out_dir)


def main():
    export_assembly(build_assembly(), str(_here.parent / "servo-valve-mock.step"))
    render()
    bb = build_scene().BoundingBox()
    print("-> servo-valve-mock.step")
    print(
        "bbox mm  X[%.1f, %.1f]  Y[%.1f, %.1f]  Z[%.1f, %.1f]"
        % (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)
    )


if __name__ == "__main__":
    main()
