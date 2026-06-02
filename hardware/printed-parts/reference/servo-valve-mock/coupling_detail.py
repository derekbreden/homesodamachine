"""Coupling detail: how the servo output reaches the valve ball, and what is
removed.

The torque path is the valve stem, not the lever. The molded finger lever
presses onto the stem's drive top and pops off; a printed coupler sockets that
drive top and bolts to a servo horn clipped on the spline. Closed/open
endpoints live in the servo's absolute angle, so the lever's mechanical 90-deg
stops are not needed.

Exploded along +Z (bottom to top): valve stem with a double-flat drive blade,
the removed lever set aside, the printed coupler, the servo horn, the spline,
and a stub of the servo body. The double-flat blade and round horn are
representative profiles pending the actual NeoFit stem geometry.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
from _cadq_export import export_assembly


def _zcyl(r, z0, z1):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(0, 0, z0), cq.Vector(0, 0, 1))


def _box(dx, dy, dz, z0, x=0.0, y=0.0):
    return (
        cq.Workplane("XY")
        .box(dx, dy, dz, centered=(True, True, False))
        .translate((x, y, z0))
    )


BLADE_X = 4.0       # across the flats
BLADE_Y = 6.0       # blade width
POCKET = 0.3        # socket clearance over the blade


def build_stem():
    """Valve stem: round shaft + a double-flat drive blade on top."""
    s = cq.Workplane(obj=_zcyl(7.0 / 2.0, 0.0, 11.0))
    s = s.union(_box(BLADE_X, BLADE_Y, 5.0, 11.0))
    return s


def build_lever():
    """The molded finger lever — a flat bar with a socketed hub. Removed."""
    bar = _box(28.0, 9.0, 4.0, 0.0)
    hub = cq.Workplane(obj=_zcyl(10.0 / 2.0, -5.0, 0.0)).translate((10.0, 0, 0))
    lever = bar.union(hub)
    socket = _box(BLADE_X + POCKET, BLADE_Y + POCKET, 5.5, -5.1, x=10.0)
    lever = lever.cut(socket)
    return lever


def build_coupler():
    """Printed coupler: blade socket at the bottom, bolt flange to the horn."""
    c = cq.Workplane(obj=_zcyl(10.0 / 2.0, 21.0, 28.0))
    c = c.union(cq.Workplane(obj=_zcyl(13.0 / 2.0, 28.0, 30.0)))      # flange
    c = c.cut(_box(BLADE_X + POCKET, BLADE_Y + POCKET, 5.5, 20.9))    # blade socket
    for sx in (-1.0, 1.0):
        c = c.cut(cq.Workplane(obj=_zcyl(1.0, 27.5, 30.5).translate((sx * 5.0, 0, 0))))
    return c


def build_horn():
    """Standard servo horn: spline hub + round arm, bolts down to the coupler."""
    h = cq.Workplane(obj=_zcyl(8.0 / 2.0, 31.0, 33.0))               # hub
    h = h.union(cq.Workplane(obj=_zcyl(16.0 / 2.0, 33.0, 35.0)))     # round arm
    h = h.cut(cq.Workplane(obj=_zcyl(2.6, 30.9, 33.5)))              # spline bore
    for sx in (-1.0, 1.0):
        h = h.cut(cq.Workplane(obj=_zcyl(0.9, 32.5, 35.5).translate((sx * 5.0, 0, 0))))
    return h


def build_spline_and_servo():
    s = cq.Workplane(obj=_zcyl(4.8 / 2.0, 35.0, 42.0))               # spline
    s = s.union(_box(22.8, 12.5, 8.0, 42.0))                         # servo body stub
    return s


def build_assembly():
    a = cq.Assembly()
    a.add(build_stem(), name="valve_stem", color=cq.Color(0.80, 0.72, 0.55))
    a.add(build_lever().translate((-32.0, 0.0, 19.0)), name="removed_lever", color=cq.Color(0.85, 0.45, 0.20))
    a.add(build_coupler(), name="printed_coupler", color=cq.Color(0.20, 0.45, 0.75))
    a.add(build_horn(), name="servo_horn", color=cq.Color(0.55, 0.55, 0.58))
    a.add(build_spline_and_servo(), name="servo", color=cq.Color(0.18, 0.18, 0.20))
    return a


def build_scene():
    parts = [
        build_stem().val(),
        build_lever().translate((-32.0, 0.0, 19.0)).val(),
        build_coupler().val(),
        build_horn().val(),
        build_spline_and_servo().val(),
    ]
    return cq.Compound.makeCompound(parts)


def _export_svg(shape, name, out_dir):
    cq.exporters.export(
        cq.Workplane(obj=shape),
        f"{out_dir}/coupling_{name}.svg",
        opt={
            "width": 1000,
            "height": 900,
            "projectionDir": (0, 0, 1),
            "showAxes": False,
            "showHidden": False,
            "strokeWidth": 0.45,
        },
    )


def render(out_dir="/tmp"):
    scene = build_scene()
    _export_svg(scene.rotate((0, 0, 0), (1, 0, 0), -90.0), "front", out_dir)
    iso = scene.rotate((0, 0, 0), (0, 0, 1), 25.0).rotate((0, 0, 0), (1, 0, 0), -68.0)
    _export_svg(iso, "iso", out_dir)


def main():
    export_assembly(build_assembly(), str(_here.parent / "coupling-detail.step"))
    render()
    print("-> coupling-detail.step")


if __name__ == "__main__":
    main()
