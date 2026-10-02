"""Solid PET-GF funnel frame and the enclosure's matching sliding receivers.

Construction uses machine coordinates. The exported individual part is translated
onto its flat underside, with the funnel's plan center at the origin.
"""

import functools
import math
import sys
from pathlib import Path

import cadquery as cq

import funnel

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_cadq_export.py').is_file())
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/enclosure/enclosure'),
                str(ROOT / 'hardware/scripts')]

# Shared by the frame, shell opening, and assembly placement.
center_y = 182.5
web = 3.0
width = 207.0
body_width = 196.5
depth = funnel.collar_d + 24.6
corner_radius = 6.0
rail_below_seat = 42.1
receiver_height = 23.3
corbel_foot_half_depth = 27.5
corbel_slope = math.tan(math.radians(30.0))
tube_hole_diameter = 6.85
socket_diameter = 36.6
DEFAULT_INNER = (-104.5, 104.5, 0.0, 290.0, 0.0, 352.0)


def datums(seat=349.0):
    return seat - funnel.drop - web, seat - funnel.drop, seat - rail_below_seat


def rail_runs(inner, y_joint, col, centre):
    cx, cy = centre
    start, stop = cy - funnel.collar_d / 2 + 6, cy + funnel.collar_d / 2 + 3.3
    # The full-width end planes bound the rail and its receiver. Material beyond
    # their reach cannot engage the frame and would occupy the component bays.
    reach = (corbel_foot_half_depth + corbel_slope *
             (funnel.drop + web - rail_below_seat + receiver_height))
    start, stop = max(start, cy - reach), min(stop, cy + reach)
    y0, lane = (start, y_joint + 14.55) if col == 'front' else (stop, y_joint - 1)
    return [(inner[0], 1.0, y0, y_joint, lane),
            (inner[1], -1.0, y0, y_joint, lane)]


def corbel_cut(centre, floor, air=0.0):
    """The same two planes cut the body and both full-width rail wings."""
    cx, cy = centre
    cuts = []
    for sign in (-1, 1):
        low, high = floor - 2, floor + 80
        foot = corbel_foot_half_depth + air / math.cos(math.radians(30))
        y0 = cy + sign * (foot + corbel_slope * (low - floor))
        y1 = cy + sign * (foot + corbel_slope * (high - floor))
        outside = cy + sign * 400
        wire = cq.Wire.makePolygon(
            [cq.Vector(cx - 150, y, z) for y, z in
             ((y0, low), (outside, low), (outside, high), (y1, high))], close=True)
        cuts.append(cq.Solid.extrudeLinear(wire, [], cq.Vector(300, 0, 0)))
    return cq.Compound.makeCompound(cuts)


def body_blank(centre, seat, air=0.0):
    cx, cy = centre
    floor, _plug, rail = datums(seat)
    body = funnel._rounded_box(body_width + 2 * air, depth + 2 * air,
                               corner_radius + air, floor - air, seat + air, cx, cy)
    foot = funnel._rounded_box(width + 2 * air, depth + 2 * air,
                               corner_radius + air, floor - air, rail, cx, cy)
    return body.fuse(foot).cut(corbel_cut(centre, floor, air)).clean()


@functools.cache
def forming_clearance():
    return funnel.build_solids(outer_air=0.3)[0]


@functools.cache
def build(inner=DEFAULT_INNER, y_joint=200.0, centre=(0.0, center_y), seat=349.0):
    import enclosure as enc
    cx, cy = centre
    floor, plug, rail = datums(seat)
    body = body_blank(centre, seat)
    for col in ('front', 'back'):
        body = body.fuse(enc._z_rail_heads(
            inner, y_joint, rail, col, None, runs=rail_runs(inner, y_joint, col, centre)))
    body = body.cut(corbel_cut(centre, floor))
    # Only the tube hole pierces the 3 mm bottom web.
    clear = forming_clearance().translate((cx, cy, seat))
    clear = clear.intersect(funnel._box(400, 400, plug, seat + 10, cx, cy))
    nx, ny = cx + funnel.neck_dx, cy + funnel.neck_dy
    socket = cq.Solid.makeCylinder(socket_diameter / 2, 19, cq.Vector(nx, ny, plug))
    socket = socket.fuse(cq.Solid.makeCone(socket_diameter / 2, socket_diameter / 2 + 1,
                                         2, cq.Vector(nx, ny, plug + 17)))
    hole = cq.Solid.makeCylinder(tube_hole_diameter / 2, seat - floor + 2,
                                 cq.Vector(nx, ny, floor - 1))
    body = body.cut(clear.fuse(socket).fuse(hole)).clean()
    assert body.isValid() and len(body.Solids()) == 1
    assert abs(body.BoundingBox().zmin - floor) < 0.0001
    web_ring = (cq.Workplane('XY', origin=(nx, ny, floor))
                .circle(17.5).circle(3.5).extrude(web).val())
    assert web_ring.cut(body).Volume() < 0.001
    return body


def receivers(inner, outer, y_joint, centre, seat, col):
    """Shell-rooted bands, cut by the production rail's complete mating profile."""
    import enclosure as enc
    _floor, _plug, rail = datums(seat)
    runs = rail_runs(inner, y_joint, col, centre)
    y0 = runs[0][2]
    ya, yb = (y0 - 3, y_joint) if col == 'front' else (y_joint, y0 + 3)
    bands = []
    for side in (-1, 1):
        x0, x1 = sorted((centre[0] + side * (body_width / 2 + enc.slide_slip),
                          outer[0] if side < 0 else outer[1]))
        bands.append(cq.Solid.makeBox(x1 - x0, yb - ya, receiver_height,
                                      cq.Vector(x0, ya, rail)))
    channel = enc._z_rail_channels(inner, y_joint, rail, col, None, runs=runs)
    return cq.Compound.makeCompound([b.cut(channel) for b in bands])


def shell_clearance(centre, seat):
    """Body clearance through shell furniture; rail clearance has its own exact cutter."""
    import enclosure as enc
    return body_blank(centre, seat, enc.slide_slip)


def front_seam_relief(outer, y_joint, centre, seat):
    """Open the front tongue for the frame foot and rear receiver's flat roof.

    The rail section remains complete between these two openings. The lower
    entry extends through the tongue's outside face so it leaves no thin fin.
    """
    import enclosure as enc
    floor, _plug, rail = datums(seat)
    cuts = []
    for side in (-1, 1):
        x0, x1 = sorted((centre[0] + side * (body_width / 2 + enc.slide_slip),
                         outer[0] - 1 if side < 0 else outer[1] + 1))
        cuts.append(cq.Solid.makeBox(x1 - x0, outer[3] - y_joint + 2,
            receiver_height + enc.slide_slip - enc.z_rise,
            cq.Vector(x0, y_joint - enc.slide_slip, rail + enc.z_rise)))
        cuts.append(cq.Solid.makeBox(x1 - x0, outer[3] - y_joint + 2,
            rail - floor + 2 * enc.slide_slip,
            cq.Vector(x0, y_joint, floor - enc.slide_slip)))
    return cq.Compound.makeCompound(cuts)


def main():
    from _cadq_export import export_assembly
    from _materials import M_PETGF_BLACK, one_body
    from flute_payload import cut
    shape = build()
    floor, _plug, _rail = datums()
    print_shape = shape.translate((0, -center_y, -floor))
    here = Path(__file__).resolve().parent
    step, stl = here / 'funnel-frame.step', here / 'funnel-frame.stl'
    export_assembly(one_body(cq.Workplane(obj=print_shape), 'funnel-frame', M_PETGF_BLACK), str(step))
    cq.exporters.export(print_shape.copy(mesh=False), str(stl), tolerance=0.05, angularTolerance=0.15)
    cut(step, stl)
    print(f'-> {step.name}, {stl.name}; {shape.Volume():.1f} mm3; floor Z {floor:g}')


if __name__ == '__main__':
    main()
