"""Drop-in PET-GF funnel frame with screw seats and its drain-cradle snap socket.

Construction uses machine coordinates. The exported removable frame is translated
onto its flat underside, with the funnel's plan center at the origin.
"""

import argparse
import math
import sys
from pathlib import Path

import elbow_cradle
import funnel

ROOT = next(p for p in Path(__file__).resolve().parents if any(
    (p / 'hardware/scripts' / helper).is_file()
    for helper in ('_rust_part.py', '_cadq_export.py')))
sys.path[:0] = [str(ROOT / 'hardware/printed-parts/enclosure/enclosure'),
                str(ROOT / 'hardware/scripts')]

if __name__ == '__main__':
    import _rust_part
    _rust_part.start()


# Construction leaves supplied by _enclosure_back_top._frame_leaves while
# recording the enclosure numeric graph; dimensions remain in numbers().
body_blank = roof_blank = receivers = shell_screw_cuts = None


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


def roof_datums(inner=DEFAULT_INNER, centre=(0.0, center_y), seat=349.0,
                y_joint=200.0, full_front_opening=False):
    """Full removable roof surround, with a fixed horizontal underside bearing."""
    cx, cy = centre
    return dict(width=width,
                front=cy - funnel.collar_d / 2 - funnel.brim_overhang,
                back=cy + depth / 2 + rear_roof_access_extension, floor=seat - web,
                top=seat + funnel.brim_thickness,
                taper_floor=seat - web, side_reach=(width - body_width) / 2)


def fastener_datums(inner=DEFAULT_INNER, y_joint=200.0,
                    centre=(0.0, center_y), seat=349.0):
    """Four upward-access M3 x 12 seats and RX-M3x5.7 shell pilots.

    Each dictionary names its owning upper shell, XY axis and vertical seats.
    The rear pair stands outside the silicone brim's rounded corners.
    """
    import _enclosure_interface as enc
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


def body_side_half_width(inner=DEFAULT_INNER, y_joint=200.0,
                         centre=(0.0, center_y), seat=349.0):
    """Plain lower side faces aligned with the front ledge passage."""
    import _enclosure_interface as enc
    return min(abs(row['x']-centre[0])-row['host_radius_mm']-enc.slide_slip
               for row in fastener_datums(inner,y_joint,centre,seat)
               if row['col']=='front')


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


def _document():
    sys.path.insert(0, str(ROOT / 'tools'))
    from docgen import substitute_md
    import _enclosure_interface as enc
    here = Path(__file__).resolve().parent
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
                       f'{elbow_cradle.SLOT_AFT_Y - elbow_cradle.SLOT_FORE_Y + 2 * elbow_cradle.END_SLIP:.1f} mm',
    })


def numbers(inner=DEFAULT_INNER, y_joint=200.0, centre=(0.0, center_y), seat=349.0):
    """Current frame APIs expressed in the exported underside's coordinates."""
    import _enclosure_interface as enc
    from _materials import M_PETGF_BLACK, linear
    from _payload_rules import LINEAR_DEFLECTION_RATIO

    cx, cy = centre
    floor, plug, _rail = datums(seat)
    roof = roof_datums(inner, centre, seat, y_joint)
    rows = fastener_datums(inner, y_joint, centre, seat)
    snap = elbow_cradle.stations()
    half, gap = funnel.plug_width / 2, (socket_width - funnel.plug_width) / 2
    rear_limit = inner[1] - enc.y_stack_high_depth - enc.slide_slip
    return {
        'color': list(linear(M_PETGF_BLACK)),
        'viewer_deflection_ratio': LINEAR_DEFLECTION_RATIO,
        'roof_width': roof['width'], 'body_width': body_width,
        'front': roof['front'] - cy, 'back': roof['back'] - cy,
        'roof_floor': roof['floor'] - floor, 'roof_top': roof['top'] - floor,
        'seat': seat - floor, 'corner_radius': corner_radius,
        'rear_limits': [-rear_limit - cx, rear_limit - cx],
        'rear_start': y_joint - enc.slide_slip - cy,
        'corbel_half_depth': corbel_foot_half_depth, 'corbel_slope': corbel_slope,
        'ledge_pad_half_y': SCREW_PAD_HALF_Y, 'slide_slip': enc.slide_slip,
        'screw_clear_radius': enc.screw_clear_dia / 2,
        'head_radius': enc.head_cbore_dia / 2, 'rear_pad_radius': SCREW_HEAD_D / 2,
        'front_head_inside': funnel.collar_w / 2 + funnel.brim_overhang + enc.funnel_collar_air,
        'screws': [[row['x'] - cx, row['y'] - cy, row['head_seat_z'] - floor,
                    row['host_radius_mm'], row['side'], row['col'] == 'front'] for row in rows],
        'body_half_width': body_side_half_width(inner, y_joint, centre, seat),
        'brim_half_size': [funnel.collar_w / 2 + funnel.brim_overhang + enc.funnel_collar_air,
                           funnel.collar_d / 2 + funnel.brim_overhang + enc.funnel_collar_air],
        'brim_radius': funnel.brim_corner_r + enc.funnel_collar_air,
        'drain_xy': [funnel.neck_dx, funnel.neck_dy],
        'socket_size': [2 * (half + gap), 2 * (elbow_cradle.plug_half_length(half) + gap)],
        'socket_radius': elbow_cradle.SOCKET_CORNER,
        'socket_z': elbow_cradle.WEB, 'socket_height': socket_depth,
        'socket_flare': list(socket_flare),
        'hole_radius': elbow_cradle.HOLE_D / 2, 'web_cut_z': [-1.0, elbow_cradle.WEB + 1.0],
        'slot_x': [snap['slot_in'], snap['slot_out']],
        'slot_y': [elbow_cradle.SLOT_FORE_Y - elbow_cradle.END_SLIP,
                   elbow_cradle.SLOT_AFT_Y + elbow_cradle.END_SLIP],
        'funnel': funnel.numbers(), 'forming_air': forming_air,
        'forming_clip_z': [plug - floor, seat - floor],
    }


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else Path(__file__).resolve().parent
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('funnel', 'funnel-frame', numbers(), out)
    _document()
    print(f'-> funnel-frame STEP, STL and payload; {said["bodies"][0]["volume"]:.1f} mm3; '
          f'floor Z {datums()[0]:g}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    options = parser.parse_args()
    main(options.output)
