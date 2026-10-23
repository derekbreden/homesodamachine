"""A PET-GF sleeve that holds 1/4" LLDPE round its tightest bend: a D on its back, swept a
quarter turn round the tube's R14 centreline, with a teardrop channel the tube threads through.

THE BEND IS THE STOCK'S FLOOR. `_routing.STOCKS` gives 1/4" LLDPE a [14 mm](BEND_R) centreline
radius from the spool bench test, and every 1/4" LLDPE run in the enclosure turns at least one
corner at exactly that radius. The tube reached it only wrapped tightly round a dense cylinder,
so the corner needs a body round it that keeps the bent tube from flattening.

THE SECTION PRINTS AS IT STANDS. The holder lies on the D's flat back, so its outside needs
nothing under it; the channel's roof closes in two 45-degree flanks to a point, so the tunnel
needs nothing under it either. A support inside a curved tunnel could never be taken out.

THE WALL IS THE LEAST MATERIAL ANYWHERE ROUND THE CHANNEL. The floor and the sides stand `wall`
off the channel's circle, and the dome is centred `(sqrt(2) - 1) * r` above the circle's
centre, which keeps `wall` over the teardrop's point as well. A dome centred on the circle
would leave `wall - (sqrt(2) - 1) * r` there: [0.59 mm](CENTRED_POINT_WALL_W2) on the 2 mm holder.

Frame: the bend's centre is the origin and its axis is +Z; the holder lies on Z = 0 and runs
from the XZ plane (0 degrees) round to the YZ plane (90 degrees). Run with the CAD venv:

    tools/cad-venv/bin/python future/tube-bend-holder-exploration/tube_bend_holder.py
"""
import math
import sys
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "hardware" / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
from _cadq_export import export_step  # noqa: E402
from _routing import stock_of  # noqa: E402
from docgen import substitute_md, substitute_py_comments  # noqa: E402

TUBE_OD = 6.35
STOCK = stock_of("water", TUBE_OD)
BEND_R = STOCK.min_bend             # the channel centreline
TURN = 90.0                         # the commonest turn among the routes' R14 corners
# The channel's circle. The umbilical organizer's accepted straight sliding bore for this tube
# is 6.65 (`hardware/printed-parts/faucet/umbilical-organizer/physical-acceptance.json`); a
# curved tunnel the tube is pushed round takes [0.15 mm](CHANNEL_EXTRA) more.
ORGANIZER_BORE = 6.65
CHANNEL_D = 6.8
MOUTH = 0.5                         # the 45-degree lead-in at each end
WALLS = (2.0, 3.0, 4.0)
PETGF_DENSITY = 1.43                # g/cm3, Polymaker Fiberon PET-GF15 data sheet

R_C = CHANNEL_D / 2.0
LIFT = (math.sqrt(2.0) - 1.0) * R_C  # dome centre above the channel's centre


def section(wall):
    """The holder's dimensions in its own section: `u` out from the bend's axis, `z` up."""
    outer = R_C + wall
    centre_z = wall + R_C
    return {"wall_mm": wall, "channel_d_mm": CHANNEL_D, "channel_centre_z_mm": centre_z,
            "outer_r_mm": outer, "width_mm": 2.0 * outer,
            "height_mm": centre_z + LIFT + outer,
            "teardrop_point_z_mm": centre_z + math.sqrt(2.0) * R_C,
            "base_inner_r_mm": BEND_R - outer, "base_outer_r_mm": BEND_R + outer}


def _d_face(wall):
    s = section(wall)
    x0, x1 = BEND_R - s["outer_r_mm"], BEND_R + s["outer_r_mm"]
    zd = s["channel_centre_z_mm"] + LIFT
    return (cq.Workplane("XZ").moveTo(x0, 0.0).lineTo(x1, 0.0).lineTo(x1, zd)
            .threePointArc((BEND_R, zd + s["outer_r_mm"]), (x0, zd)).close())


def _teardrop(wp, x, z, r):
    """The channel's section on `wp`, centred at local (x, z): its circle below the 45-degree
    tangents and the two flanks from there to the point."""
    k = r / math.sqrt(2.0)
    return (wp.moveTo(x + k, z + k).lineTo(x, z + math.sqrt(2.0) * r).lineTo(x - k, z + k)
            .threePointArc((x, z - r), (x + k, z + k)).close())


def _mouth(wall):
    """The lead-in at the 0-degree end, as a ruled loft of teardrops along the channel's start
    tangent (+Y): `MOUTH` larger at the face, the channel's own size `MOUTH` in. Its ends run
    past both so no face of it lies on one of the holder's."""
    zc = section(wall)["channel_centre_z_mm"]
    out, past = 0.3, 0.05

    def at(y, r):
        plane = cq.Plane(origin=(0.0, y, 0.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, -1.0, 0.0))
        return _teardrop(cq.Workplane(plane), BEND_R, zc, r).wires().val()

    return cq.Solid.makeLoft([at(-out, R_C + MOUTH + out), at(MOUTH + past, R_C - past)],
                             ruled=True)


def holder(wall):
    zc = section(wall)["channel_centre_z_mm"]
    axis = ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0))     # XZ workplane: local y is world +Z
    body = _d_face(wall).revolve(TURN, *axis)
    channel = _teardrop(cq.Workplane("XZ"), BEND_R, zc, R_C).revolve(TURN, *axis)
    start = _mouth(wall)
    # The holder is symmetric about the plane halfway round the turn.
    half = math.radians(TURN / 2.0)
    end = start.mirror(cq.Vector(math.sin(half), -math.cos(half), 0.0), cq.Vector(0, 0, 0))
    return body.cut(channel).cut(cq.Workplane().add(start)).cut(cq.Workplane().add(end)).clean()


def name(wall):
    return f"holder-w{wall:g}"


def document(volumes):
    """Write the figures the README and this file's own comments quote."""
    figures = {"BEND_R": f"{BEND_R:g} mm", "TURN": f"{TURN:g}°", "CHANNEL_D": f"Ø{CHANNEL_D:g} mm",
               "CHANNEL_EXTRA": f"{CHANNEL_D - ORGANIZER_BORE:.2f} mm",
               "ORGANIZER_BORE": f"Ø{ORGANIZER_BORE:g} mm", "MOUTH": f"{MOUTH:g} mm",
               "DOME_LIFT": f"{LIFT:.2f} mm",
               "CENTRED_POINT_WALL_W2": f"{WALLS[0] - LIFT:.2f} mm"}
    for wall in WALLS:
        s, tag = section(wall), f"W{wall:g}"
        figures |= {f"WIDTH_{tag}": f"{s['width_mm']:.1f} mm",
                    f"HEIGHT_{tag}": f"{s['height_mm']:.1f} mm",
                    f"BASE_{tag}": f"R{s['base_inner_r_mm']:.1f}–R{s['base_outer_r_mm']:.1f}",
                    f"MASS_{tag}": f"{volumes[wall] / 1000.0 * PETGF_DENSITY:.1f} g"}
    substitute_md(HERE / "README.md", variables=figures)
    substitute_py_comments(Path(__file__), variables=figures)


def main():
    volumes = {}
    for wall in WALLS:
        part = holder(wall)
        solid = part.val()
        assert solid.isValid(), name(wall)
        volumes[wall] = solid.Volume()
        export_step(part, str(HERE / f"{name(wall)}.step"))
        cq.exporters.export(part, str(HERE / f"{name(wall)}.stl"),
                            tolerance=0.01, angularTolerance=0.1)
        s = section(wall)
        print(f"{name(wall)}: {s['width_mm']:.1f} wide x {s['height_mm']:.2f} tall, "
              f"base R{s['base_inner_r_mm']:.1f}-R{s['base_outer_r_mm']:.1f}, "
              f"{volumes[wall] / 1000.0:.2f} cm3")
    document(volumes)


if __name__ == "__main__":
    main()
