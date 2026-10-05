"""Solid PET-GF funnel frame and the enclosure's matching sliding receivers.

Construction uses machine coordinates. The exported individual part is translated
onto its flat underside, with the funnel's plan center at the origin.
"""

import functools
import math
import sys
from pathlib import Path

import cadquery as cq
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain

import elbow_cradle
import funnel

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/scripts/_cadq_export.py').is_file())
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/enclosure/enclosure'),
                str(ROOT / 'hardware/scripts')]

# Shared by the frame, shell opening, and assembly placement.
center_y = 182.5 - funnel.forward_extension / 2.0
web = 3.0
width = 207.0
body_width = 196.5
depth = funnel.collar_d + 24.6
corner_radius = 6.0
forming_air = 0.3
rail_below_seat = 42.1
receiver_height = 23.3
corbel_foot_half_depth = 27.5 + funnel.forward_extension / 2.0
corbel_slope = math.tan(math.radians(30.0))
tube_hole_diameter = elbow_cradle.HOLE_D
socket_width = 36.6
socket_depth = 19.0
socket_flare = (2.0, 1.0)   # height, outward reach of the plug's lead-in
assert abs(socket_width / 2 - elbow_cradle.SOCKET_HALF) < 1e-9
# the cradle's hooks clear the socket's corner rounds
assert elbow_cradle.hook_corner_clearance(funnel.plug_width / 2) >= 0.1
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


def roof_datums(inner=DEFAULT_INNER, centre=(0.0, center_y), seat=349.0,
                y_joint=200.0, full_front_opening=False):
    """The removable roof surround and its complete 3 mm brim bearing."""
    import enclosure as enc
    cx, cy = centre
    # Front-top carries its 9 mm flank section through the roof. Its inner
    # faces stand 6 mm inboard of the nominal cavity on each side; the
    # removable surround fits those faces with the normal running air.
    flank_growth = enc.front_top_flank_t - enc.wall
    roof_width = inner[1] - inner[0] - 2 * (flank_growth + enc.slide_slip)
    front = (cy - funnel.collar_d / 2 - funnel.brim_overhang
             - enc.funnel_collar_air - web)
    back = (cy + depth / 2 if full_front_opening else
            min(cy + depth / 2, y_joint - enc.slide_slip))
    floor = seat - web
    reach = (roof_width - body_width) / 2
    assert reach >= -1e-9, 'The roof opening is narrower than the frame body.'
    reach = max(0.0, reach)
    return dict(width=roof_width, front=front, back=back, floor=floor,
                top=seat + funnel.brim_thickness,
                taper_floor=floor - reach / 0.5,
                side_reach=reach)


def _front_square_blank(width, front, back, z0, z1, cx, radius):
    """One flat front and two retained rear corner rounds."""
    blank = cq.Solid.makeBox(width, back - front, z1 - z0,
                            cq.Vector(cx - width / 2, front, z0))
    rear_edges = [edge for edge in blank.Edges()
                  if abs(edge.BoundingBox().ymin - back) < 1e-7
                  and abs(edge.BoundingBox().ymax - back) < 1e-7
                  and edge.BoundingBox().zlen > z1 - z0 - 1e-7]
    return blank.fillet(radius, rear_edges)


def roof_blank(inner, centre, seat, air=0.0, y_joint=200.0,
               full_front_opening=False):
    """Flush roof surround inside front-top's complete flank section.

    The lower frame and production rails retain their own width. Only the roof
    meets the vertical shell walls, so there is no fixed inward roof ledge
    above the removable frame.
    """
    import enclosure as enc
    cx, cy = centre
    r = roof_datums(inner, centre, seat, y_joint, full_front_opening)
    outline = _front_square_blank(r['width'] + 2 * air,
        r['front'] - air, r['back'] + air,
        r['taper_floor'] - air, r['top'] + air, cx, corner_radius + air)
    if r['side_reach'] <= 1e-9:
        # With a full-thickness shell, the roof and lower body have equal
        # width. A rectangular surround needs no zero-area side polygons.
        return outline
    # Keep the outer clearance face parallel to the nominal taper, and extend
    # its inboard root beneath the rounded ends of the original frame body.
    half = body_width / 2 - air
    roof_half = r['width'] / 2 + air
    strips = [funnel._box(body_width + 2 * air, 400,
                         r['floor'] - air, r['top'] + air, cx, cy)]
    for sign in (-1, 1):
        points = [(cx + sign * half, r['taper_floor'] - air)]
        if air:
            points.append((cx + sign * (body_width / 2 + air),
                           r['taper_floor'] - air))
        points += [(cx + sign * roof_half, r['floor'] - air),
                   (cx + sign * roof_half, r['top'] + air),
                   (cx + sign * half, r['top'] + air)]
        strips.append(enc._xz_prism(cy - 200, cy + 200, points))
    blank = strips[0]
    for strip in strips[1:]:
        blank = blank.fuse(strip)
    return blank.intersect(outline)


def body_blank(centre, seat, air=0.0, inner=DEFAULT_INNER, y_joint=200.0):
    cx, cy = centre
    floor, _plug, rail = datums(seat)
    front = roof_datums(inner, centre, seat, y_joint)['front']
    back = cy + depth / 2
    body = _front_square_blank(body_width + 2 * air, front - air, back + air,
                               floor - air, seat + air, cx, corner_radius + air)
    foot = _front_square_blank(width + 2 * air, front - air, back + air,
                               floor - air, rail, cx, corner_radius + air)
    roof = roof_blank(inner, centre, seat, air, y_joint)
    return body.fuse(foot).fuse(roof).cut(corbel_cut(centre, floor, air)).clean()


@functools.cache
def forming_clearance():
    return funnel.build_solids(outer_air=forming_air)[0]


def merge_edges(shape):
    """Merge redundant edges while retaining the bowl's analytic offset faces."""
    merge = ShapeUpgrade_UnifySameDomain(shape.wrapped, True, False, False)
    merge.Build()
    return cq.Shape.cast(merge.Shape())


@functools.cache
def build(inner=DEFAULT_INNER, y_joint=200.0, centre=(0.0, center_y), seat=349.0):
    import enclosure as enc
    cx, cy = centre
    floor, plug, rail = datums(seat)
    assert abs(web + funnel.plug_lift -
               (elbow_cradle.stations()['hook_top'] - elbow_cradle.CATCH_GAP)) < 1e-6
    body = body_blank(centre, seat, inner=inner, y_joint=y_joint)
    for col in ('front', 'back'):
        body = body.fuse(enc._z_rail_heads(
            inner, y_joint, rail, col, None, runs=rail_runs(inner, y_joint, col, centre)))
    body = body.cut(corbel_cut(centre, floor))
    # The drain hole and the elbow cradle's two wing slots are all that pierce the 3 mm web.
    clear = forming_clearance().translate((cx, cy, seat))
    clear = clear.intersect(funnel._box(400, 400, plug, seat, cx, cy))
    # Forming air expands the silicone brim below its underside. Keep that
    # expansion in the collar opening, so it cannot shave the brim's bearing.
    collar_limit = funnel._rounded_box(
        funnel.collar_w + 2 * forming_air, funnel.collar_d + 2 * forming_air,
        funnel.collar_corner_r + forming_air,
        seat - forming_air - 0.01, seat + 0.01, cx, cy)
    brim_air = funnel._box(400, 400, seat - forming_air - 0.01,
                          seat + 0.01, cx, cy).cut(collar_limit)
    clear = clear.cut(brim_air)
    # The silicone's complete brim bears on the removable frame at the existing
    # seat datum; its top and the frame's surround finish on the same roof plane.
    brim = funnel._rounded_box(
        funnel.collar_w + 2 * (funnel.brim_overhang + enc.funnel_collar_air),
        funnel.collar_d + 2 * (funnel.brim_overhang + enc.funnel_collar_air),
        funnel.brim_corner_r + enc.funnel_collar_air,
        seat, seat + funnel.brim_thickness + 1, cx, cy)
    place = cq.Vector(cx + funnel.neck_dx, cy + funnel.neck_dy, floor)
    half, gap = funnel.plug_width / 2, (socket_width - funnel.plug_width) / 2
    socket = elbow_cradle.socket(half, gap, socket_depth, *socket_flare).translate(place)
    pierce = [c.translate(place) for c in elbow_cradle.web_cuts()]
    body = body.cut(clear.fuse(socket).fuse(brim))
    for c in pierce:
        body = body.cut(c)
    body = merge_edges(body)
    assert body.isValid() and len(body.Solids()) == 1
    assert abs(body.BoundingBox().zmin - floor) < 0.0001
    # The web stands whole under the socket but for those cuts, and no stock stands in the socket.
    plate = elbow_cradle.plug_outline(half, gap, 0.0, web).translate(place)
    for c in pierce:
        plate = plate.cut(c)
    assert plate.cut(body).Volume() < 0.001
    above = elbow_cradle.plug_outline(half, gap, web + 0.01, seat - floor).translate(place)
    assert body.intersect(above).Volume() < 0.001
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


def shell_clearance(centre, seat, inner=DEFAULT_INNER, y_joint=200.0):
    """Body clearance through shell furniture; rail clearance has its own exact cutter."""
    import enclosure as enc
    return body_blank(centre, seat, enc.slide_slip, inner, y_joint)


def front_roof_clearance(inner, centre, seat, y_joint):
    """Open front-top's roof tongue over the frame and existing rear ceiling.

    Back-top retains its complete roof. The frame's raised front surround stops
    one running clearance before that rear roof, while the front shell gives up
    the fixed inward ledge and roof tongue above the rear frame envelope.
    """
    import enclosure as enc
    floor = datums(seat)[0]
    return roof_blank(inner, centre, seat, enc.slide_slip, y_joint,
                      full_front_opening=True).cut(corbel_cut(centre, floor, enc.slide_slip))


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
    from _cadq_export import export_assembly, import_assembly
    from _materials import M_PETGF_BLACK, one_body
    from flute_payload import cut
    from print_mesh import write_print_stl
    shape = build()
    floor, _plug, _rail = datums()
    print_shape = shape.translate((0, -center_y, -floor))
    here = Path(__file__).resolve().parent
    step, stl = here / 'funnel-frame.step', here / 'funnel-frame.stl'
    export_assembly(one_body(cq.Workplane(obj=print_shape), 'funnel-frame', M_PETGF_BLACK), str(step))
    write_print_stl(import_assembly(step)['funnel-frame'][0], stl, tol=0.02, angle=0.08)
    cut(step, stl)
    print(f'-> {step.name}, {stl.name}; {shape.Volume():.1f} mm3; floor Z {floor:g}')
    sys.path.insert(0, str(next(p for p in here.parents if (p / 'tools' / 'docgen').is_dir())
                           / 'tools'))
    from docgen import substitute_md
    s = elbow_cradle.stations()
    half, gap = funnel.plug_width / 2, (socket_width - funnel.plug_width) / 2
    substitute_md(here / 'README.md', variables={
        'FRAME_HOLE': f'{tube_hole_diameter:g} mm',
        'FRAME_SOCKET': f'{socket_width:g} × '
                        f'{2 * (elbow_cradle.plug_half_length(half) + gap):.1f} mm',
        'FRAME_SLOTS': f'{s["slot_out"] - s["slot_in"]:.2f} × '
                       f'{s["y1"] - s["y0"] + 2 * elbow_cradle.END_SLIP:.1f} mm',
    })


if __name__ == '__main__':
    main()
