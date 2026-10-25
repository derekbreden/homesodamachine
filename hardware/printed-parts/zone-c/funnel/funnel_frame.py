"""Drop-in PET-GF funnel frame with screw seats and its drain-cradle snap socket.

Construction uses machine coordinates. The exported removable frame is translated
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
center_y = 182.5 + (funnel.aft_extension - funnel.forward_extension) / 2.0
web = 3.0
width = 196.5               # preserves the shell's complete rounded roof flanks
body_width = 176.5          # vertical passage between the screw-bearing ledges
depth = funnel.collar_d + 24.6
rear_roof_access_extension = 5.0
corner_radius = 6.0
forming_air = 0.3
rail_below_seat = 42.1       # retained drain/assembly datum; no frame rails
receiver_height = 23.3      # retained public dimension for dated review readers
corbel_foot_half_depth = 27.5 + (funnel.forward_extension + funnel.aft_extension) / 2.0
corbel_slope = math.tan(math.radians(30.0))
tube_hole_diameter = elbow_cradle.HOLE_D
socket_width = 2 * elbow_cradle.SOCKET_HALF
socket_depth = 19.0
socket_flare = (2.0, 1.0)
DEFAULT_INNER = (-104.5, 104.5, 0.0, 290.0, 0.0, 352.0)
SCREW_LENGTH = 12.0
SCREW_LENGTH_ALLOWANCE = 0.4
SCREW_GRIP = 5.8
SCREW_HEAD_H = 3.0
SCREW_HEAD_D = 5.5
SCREW_PAD_HALF_Y = 6.0
SCREW_PILOT_RELIEF = 1.5


def datums(seat=349.0):
    return seat - funnel.drop - web, seat - funnel.drop, seat - rail_below_seat


def rail_runs(inner, y_joint, col, centre):
    """Compatibility entry point: the drop-in frame has no sliding rails."""
    return []


def rear_narrowing(inner, y_joint, air=0.0):
    """Keep the complete upper M5 seam blocks outside the removable frame."""
    import enclosure as enc
    limit = inner[1] - enc.y_stack_high_depth - enc.slide_slip + air
    y0 = y_joint - enc.slide_slip + air
    return cq.Compound.makeCompound([
        cq.Solid.makeBox(60.0, 200.0, 200.0, cq.Vector(limit, y0, 250.0)),
        cq.Solid.makeBox(60.0, 200.0, 200.0, cq.Vector(-limit - 60.0, y0, 250.0))])


def corbel_cut(centre, floor, air=0.0):
    """The two full-width 30 degree end planes of the removable lower body."""
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
    """Full removable roof surround, with a fixed horizontal underside bearing."""
    cx, cy = centre
    return dict(width=width,
                front=cy - funnel.collar_d / 2 - funnel.brim_overhang,
                back=cy + depth / 2 + rear_roof_access_extension, floor=seat - web,
                top=seat + funnel.brim_thickness,
                taper_floor=seat - web, side_reach=(width - body_width) / 2)


def _front_square_blank(w, front, back, z0, z1, cx, radius, rear_cut):
    """Square front and seam shoulders, with rounded aft corners."""
    blank = cq.Solid.makeBox(w, back - front, z1 - z0,
                            cq.Vector(cx - w / 2, front, z0))
    blank = blank.cut(rear_cut).clean()
    rear_edges = [edge for edge in blank.Edges()
                  if abs(edge.BoundingBox().ymin - back) < 1e-7
                  and abs(edge.BoundingBox().ymax - back) < 1e-7
                  and edge.BoundingBox().zlen > z1 - z0 - 1e-7]
    return blank.fillet(radius, rear_edges)


def roof_blank(inner, centre, seat, air=0.0, y_joint=200.0,
               full_front_opening=False):
    """Shallow flange/pocket across both upper shells, narrowed beside M5 blocks.

    XY clearance grows the roof pocket. The lower bearing plane does not move:
    tightening the screws seats the frame flush with the roof.
    """
    cx, cy = centre
    r = roof_datums(inner, centre, seat, y_joint, full_front_opening)
    return _front_square_blank(r['width'] + 2 * air, r['front'] - air,
        r['back'] + air, r['floor'], r['top'] + air, cx,
        corner_radius + air, rear_narrowing(inner, y_joint, air))


def fastener_datums(inner=DEFAULT_INNER, y_joint=200.0,
                    centre=(0.0, center_y), seat=349.0):
    """Four upward-access M3 x 12 seats and RX-M3x5.7 shell pilots.

    Each dictionary names its owning upper shell, XY axis and vertical seats.
    The rear pair stands outside the silicone brim's rounded corners.
    """
    import enclosure as enc
    cx, cy = centre
    r = roof_datums(inner, centre, seat, y_joint)
    ledge = r['floor']
    head_seat = ledge + SCREW_GRIP
    bore_bottom = ledge - enc.heatset_long_len - SCREW_PILOT_RELIEF
    rows = []
    for col, x, y in (('front', 93.0, r['front'] + 32.0),
                      ('back', 87.7, r['back'] - rear_roof_access_extension - 11.2)):
        for side in (-1, 1):
            name = 'west' if side < 0 else 'east'
            rows.append(dict(name=f'{col}-{name}', col=col, side=side,
                x=cx + side * x, y=y, ledge_z=ledge,
                head_seat_z=head_seat, head_top_z=head_seat + SCREW_HEAD_H,
                insert_top_z=ledge, insert_bottom_z=ledge - enc.heatset_long_len,
                bore_bottom_z=bore_bottom, host_bottom_z=bore_bottom - enc.wall,
                screw_length=SCREW_LENGTH,
                screw_length_allowance=SCREW_LENGTH_ALLOWANCE,
                tip_z=head_seat - SCREW_LENGTH,
                host_radius_mm=enc.heatset_dia / 2 + enc.wall))
    return tuple(rows)


def _ledge_relief(inner, y_joint, centre, seat, air=0.0):
    """Plain underside notches passing the four ledges through the vertical drop."""
    import enclosure as enc
    floor = datums(seat)[0]
    r = roof_datums(inner, centre, seat, y_joint)
    cuts = []
    for row in fastener_datums(inner, y_joint, centre, seat):
        side = row['side']
        inside = row['x'] - side * (row['host_radius_mm'] + enc.slide_slip - air)
        xa, xb = sorted((inside, centre[0] + side * 150.0))
        start = row['y'] - SCREW_PAD_HALF_Y - enc.slide_slip + air
        end = (r['back'] + air + 1 if row['col'] == 'back' else
               row['y'] + SCREW_PAD_HALF_Y + enc.slide_slip - air)
        cuts.append(cq.Solid.makeBox(xb - xa, end - start,
            r['floor'] - floor + 1, cq.Vector(xa, start, floor - 1)))
    return cq.Compound.makeCompound(cuts)


def body_blank(centre, seat, air=0.0, inner=DEFAULT_INNER, y_joint=200.0):
    cx, cy = centre
    floor, _plug, _rail = datums(seat)
    r = roof_datums(inner, centre, seat, y_joint)
    body = _front_square_blank(body_width + 2 * air, r['front'] - air,
        r['back'] + air, floor - air, seat + air, cx, corner_radius + air,
        rear_narrowing(inner, y_joint, air))
    body = body.cut(_ledge_relief(inner, y_joint, centre, seat, air),
                    corbel_cut(centre, floor, air))
    return body.fuse(roof_blank(inner, centre, seat, air, y_joint)).clean()


@functools.cache
def forming_clearance():
    """Silicone forming air; the plug and brim have their separate seats."""
    return funnel.build_solids(outer_air=forming_air, plug=False, brim=False)[0]


def merge_edges(shape):
    merge = ShapeUpgrade_UnifySameDomain(shape.wrapped, True, False, False)
    merge.Build()
    return cq.Shape.cast(merge.Shape())


def drain_seat_datums(centre=(0.0, center_y), seat=349.0):
    """The removable frame's drain-hole axis and 3 mm snap-web seats."""
    cx, cy = centre
    floor, plug, _rail = datums(seat)
    half = funnel.plug_width / 2
    gap = (socket_width - funnel.plug_width) / 2
    return dict(x=cx + funnel.neck_dx, y=cy + funnel.neck_dy,
                floor_z=floor, socket_floor_z=plug,
                width=socket_width,
                depth=2 * (elbow_cradle.plug_half_length(half) + gap))


def _frame_screw_cuts(inner, y_joint, centre, seat):
    import enclosure as enc
    floor = datums(seat)[0]
    cuts = []
    for row in fastener_datums(inner, y_joint, centre, seat):
        x, y, head = row['x'], row['y'], row['head_seat_z']
        shank = cq.Solid.makeCylinder(enc.screw_clear_dia / 2,
            head - floor + 1.01, cq.Vector(x, y, floor - 1))
        head_cut = cq.Solid.makeCylinder(enc.head_cbore_dia / 2,
            seat + funnel.brim_thickness + 1 - head, cq.Vector(x, y, head))
        # Open each counterbore to the side above its complete bearing floor.
        inner = x - row['side'] * enc.head_cbore_dia / 2
        xa, xb = sorted((inner, centre[0] + row['side'] * 150.0))
        head_cut = head_cut.fuse(cq.Solid.makeBox(xb - xa, enc.head_cbore_dia,
            seat + funnel.brim_thickness + 1 - head,
            cq.Vector(xa, y - enc.head_cbore_dia / 2, head)))
        cuts.append(shank.fuse(head_cut).clean())
    return cq.Compound.makeCompound(cuts)


def body_side_half_width(inner=DEFAULT_INNER, y_joint=200.0,
                         centre=(0.0, center_y), seat=349.0):
    """Plain lower side faces aligned with the front ledge passage."""
    import enclosure as enc
    return min(abs(row['x']-centre[0])-row['host_radius_mm']-enc.slide_slip
               for row in fastener_datums(inner,y_joint,centre,seat)
               if row['col']=='front')


def _plain_frame_surround(body,inner,y_joint,centre,seat):
    """Flat rear brim bearing and finite screw pads, with plain lower sides."""
    import enclosure as enc
    floor = datums(seat)[0]
    roof = roof_datums(inner,centre,seat,y_joint)
    half = body_side_half_width(inner,y_joint,centre,seat)
    cuts = [cq.Solid.makeBox(150.-half,400.,roof['floor']-floor+1.,
                cq.Vector(centre[0]+half,centre[1]-200.,floor-1.)),
            cq.Solid.makeBox(150.-half,400.,roof['floor']-floor+1.,
                cq.Vector(centre[0]-150.,centre[1]-200.,floor-1.))]
    rear = cq.Solid.makeBox(300.,200.,roof['top']-seat+1.,
                           cq.Vector(centre[0]-150.,y_joint-enc.slide_slip,seat))
    pads = [cq.Solid.makeCylinder(SCREW_HEAD_D/2.,roof['top']-seat+2.,
                cq.Vector(row['x'],row['y'],seat-0.5))
            for row in fastener_datums(inner,y_joint,centre,seat)
            if row['col']=='back']
    cuts.append(rear.cut(*pads))
    return body.cut(*cuts)


@functools.cache
def build(inner=DEFAULT_INNER, y_joint=200.0, centre=(0.0, center_y), seat=349.0):
    import enclosure as enc
    cx, cy = centre
    floor, plug, _rail = datums(seat)
    body = body_blank(centre, seat, inner=inner, y_joint=y_joint)
    clear = forming_clearance().translate((cx, cy, seat))
    clear = clear.intersect(funnel._box(400, 400, plug, seat, cx, cy))
    brim = funnel.brim_plan(enc.funnel_collar_air, seat,
                            seat + funnel.brim_thickness + 1, cx, cy)
    place = cq.Vector(cx + funnel.neck_dx, cy + funnel.neck_dy, floor)
    half, gap = funnel.plug_width / 2, (socket_width - funnel.plug_width) / 2
    socket = elbow_cradle.socket(half, gap, socket_depth, *socket_flare).translate(place)
    pierce = [c.translate(place) for c in elbow_cradle.web_cuts()]
    for cutter in (socket, clear, brim, *pierce,
                   _frame_screw_cuts(inner, y_joint, centre, seat)):
        body = body.cut(cutter)
    body = _plain_frame_surround(body,inner,y_joint,centre,seat)
    body = merge_edges(body).clean()
    assert body.isValid() and len(body.Solids()) == 1
    assert abs(body.BoundingBox().zmin - floor) < 0.0001
    return body


def receivers(inner, outer, y_joint, centre, seat, col):
    """Broad shell-rooted horizontal ledges below the removable flange.

    Fuse these before the final frame clearance. Apply shell_screw_cuts after
    all furniture and clearances so the insert pilots stay open.
    """
    import enclosure as enc
    blocks = []
    for row in fastener_datums(inner, y_joint, centre, seat):
        if row['col'] != col:
            continue
        side = row['side']
        inside = row['x'] - side * row['host_radius_mm']
        xa, xb = sorted((inside, outer[0] if side < 0 else outer[1]))
        blocks.append(cq.Solid.makeBox(xb - xa, 2 * SCREW_PAD_HALF_Y,
            row['ledge_z'] - row['host_bottom_z'],
            cq.Vector(xa, row['y'] - SCREW_PAD_HALF_Y, row['host_bottom_z'])))
    return cq.Compound.makeCompound(blocks) if blocks else None


def shell_screw_cuts(inner, centre, seat, col, y_joint=200.0):
    """Upward-opening RX-M3x5.7 pilots; cut after shell furniture is joined."""
    import enclosure as enc
    cuts = [cq.Solid.makeCylinder(enc.heatset_dia / 2,
            row['insert_top_z'] + 1 - row['bore_bottom_z'],
            cq.Vector(row['x'], row['y'], row['bore_bottom_z']))
            for row in fastener_datums(inner, y_joint, centre, seat)
            if row['col'] == col]
    return cq.Compound.makeCompound(cuts) if cuts else None


def drain_support(inner, outer, y_joint, centre, seat, col):
    """Compatibility shell hook: the drain cradle snaps into the removable frame."""
    return None


def shell_clearance(centre, seat, inner=DEFAULT_INNER, y_joint=200.0):
    """Seated body clearance, preserving the ledges' Z346 bearing plane."""
    import enclosure as enc
    return body_blank(centre, seat, enc.slide_slip, inner, y_joint)


def front_roof_clearance(inner, centre, seat, y_joint):
    """Full stepped roof pocket for BOTH upper shells; no rear roof overhang.

    Below the shallow pocket the narrower body is wholly within this plan, so
    its complete vertical passage remains clear after all quadrants close.
    """
    import enclosure as enc
    return roof_blank(inner, centre, seat, enc.slide_slip, y_joint)


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
    sys.path.insert(0, str(ROOT / 'tools'))
    from docgen import substitute_md
    import enclosure as enc
    s = elbow_cradle.stations()
    half, gap = funnel.plug_width / 2, (socket_width - funnel.plug_width) / 2
    rear = DEFAULT_INNER[1] - enc.y_stack_high_depth - enc.slide_slip
    substitute_md(here / 'README.md', variables={
        'FRAME_WIDTH': f'{width:g} mm',
        'FRAME_BODY_WIDTH': f'{2*body_side_half_width():g} mm',
        'FRAME_REAR_WIDTH': f'{2 * rear:g} mm',
        'FRAME_SCREWS': f'M3 × {SCREW_LENGTH:g} mm',
        'FRAME_HOLE': f'{tube_hole_diameter:g} mm',
        'FRAME_SOCKET': f'{socket_width:g} × '
                        f'{2 * (elbow_cradle.plug_half_length(half) + gap):.1f} mm',
        'FRAME_SLOTS': f'{s["slot_out"] - s["slot_in"]:.2f} × '
                       f'{s["y1"] - s["y0"] + 2 * elbow_cradle.END_SLIP:.1f} mm',
    })


if __name__ == '__main__':
    main()
