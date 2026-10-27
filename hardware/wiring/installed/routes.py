"""Installed conductors in the selected above-core arrangement.

The board is flat, with its long axis fore-aft. Fore looms leave above its
headers, use the clear strip ahead of the pump, and cross the quadrant joint
below the funnel frame and its snapped drain. Retained local hardware keeps
its individually dressed override stations.
"""
from __future__ import annotations

import json
from pathlib import Path

from .model import STOCK, add, mul, finish

OVERRIDES = Path(__file__).with_name('route-overrides.json')

# Both front-top ribbons cross the same rear mouth. The channel stations come
# from the exact integral mount geometry through Attachments.cable_passages.
RIBBON_PITCH_MM = 1.85


def station(spec, attachments):
    return attachments.station(spec)


def routed(connections, attachments):
    from .bundles import core_route
    overrides = json.loads(OVERRIDES.read_text())
    groups = {}
    for connection in connections:
        groups.setdefault(connection.harness, []).append(connection.id)
    result = []
    for c in connections:
        shared = core_route(c, attachments)
        if shared is not None:
            result.append(shared)
            continue
        a, b = (attachments.terminals[k] for k in (c.start, c.end))
        saved = overrides.get(c.id, {})
        guides = ([station(s, attachments) for s in saved['stations']]
                  if 'stations' in saved else guide_points(c, attachments, groups, saved))
        if saved.get('front_top_passage') == 'pump':
            guides.extend(pump_terminal_guides(c, attachments, groups[c.harness].index(c.id)))
        elif saved.get('front_top_passage') == 'display':
            guides.extend(display_internal_guides(attachments, groups[c.harness].index(c.id)))
        from .retainers import dress_guides
        guides = dress_guides(c, guides, attachments, saved)
        lead = 6. if STOCK[c.stock]['awg'] == 22 else 8.
        start_lead, end_lead = saved.get('end_lands_mm', [lead, lead])
        # PSU side wire entries and vertical screw approaches are separate.
        if c.start.startswith('psu.') and 'end_lands_mm' not in saved:
            start_lead = 6.
        if c.end.startswith('psu.') and 'end_lands_mm' not in saved:
            end_lead = 6.
        if c.start.startswith(('wago-mana.','wago-manb.')):
            start_lead = 4.
        if c.end.startswith(('wago-mana.','wago-manb.')):
            end_lead = 4.
        if c.harness in ('J9', 'J13') and 'end_lands_mm' not in saved:
            end_lead = 3.
        route = finish(c, [a.point, add(a.point, mul(a.outward, start_lead)),
                           *guides, add(b.point, mul(b.outward, end_lead)), b.point],
                       saved.get('note', 'Above-core native terminal poses; proposed installed dressing.'),
                       saved.get('bend_radius_mm'),
                       endpoint_tangent_fraction=saved.get('endpoint_tangent_fraction',.44))
        route.status = saved.get('route_status', 'proposed')
        result.append(route)
    return result


def guide_points(c, at, groups, saved=None):
    saved = saved or {}
    a, b = (at.terminals[k] for k in (c.start, c.end))
    p, q = a.point, b.point
    idx = groups[c.harness].index(c.id)
    lane = (idx % 4 - 1.5) * 1.8

    def board_escape(index=0):
        # Preserve the pin-pitch ribbon above the flat board, then turn in the
        # free fore strip below the reservoir draw and above the fore feed.
        bank = 0 if c.harness == 'J1' else 2
        y = 179. + 2.*(bank+index//5)
        z = 282. + (index % 5)*1.85
        return [(p[0], p[1], 275.), (p[0], y, 275.),
                (p[0], y, z), (70.+index*1.85, y, z)]

    if c.harness in ('J1', 'J2'):
        if c.start.startswith(('J1.', 'J2.')):
            labels = (['COM']+[f'OUT{i}' for i in range(1, 9)] if c.harness == 'J1'
                      else ['COM', 'OUT1', 'OUT2', 'FAN', 'OUT3'])
            n = labels.index(c.start.split('.')[1])
            pts = board_escape(n)
            if c.end.startswith('wago-'):
                return pts+[(76., pts[-1][1], pts[-1][2]), (76., q[1], q[2])]
        else:
            n = idx % 9
            z = 281.5+n*1.4
            trunk_x=30.5 if c.id=='J1-positive-A' else 32.3 if c.id=='J1-positive-B' else 24.+lane
            pts = [(p[0]-6., p[1], p[2]), (75., p[1], p[2]),
                   (75., 190., z), (trunk_x, 190., z)]
        if c.end.startswith('V-'):
            letter = c.end[2]
            if 'tail_stations' in saved:
                return pts+[station(s,at) for s in saved['tail_stations']]
            if letter == 'B':
                return pts+[(96., pts[-1][1], pts[-1][2]),
                            (96., q[1]+8., pts[-1][2]), (q[0], q[1]+8., q[2])]
            if letter in 'AK':
                x = -62.+lane if letter == 'A' else 98.+lane
                z = 337.+(idx % 2)*2.
                return pts+[(x, 276., pts[-1][2]), (x, 276., z),
                            (x, q[1], z), (q[0], q[1], z)]
            x = 68.+(idx % 5)*2.
            if letter in 'GJ':
                return pts+[(x, 190., pts[-1][2]), (x, q[1]+12., pts[-1][2]),
                            (x, q[1]+12., q[2]), (q[0], q[1]+12., q[2])]
            z = q[2]+b.outward[2]*(11.+(idx % 2)*2.)
            return pts+[(x, 190., pts[-1][2]), (x, q[1]+12., pts[-1][2]),
                        (x, q[1]+12., z), (x, q[1], z), (q[0], q[1], z)]
        return pts+[(70.+lane, 190., 280.), (70.+lane, 80., 165.+lane),
                    (q[0], 80., 165.+lane), (q[0], q[1]+12., q[2])]

    if c.harness == 'J13':
        return pump_lead_guides(c, at, idx % 4)

    if c.harness == 'J9':
        n = idx % 4
        x = 4.+n*RIBBON_PITCH_MM
        return [(p[0], p[1], 298.), (x, p[1], 298.), (x, 208., 298.),
                (x, 184., 298.), *display_internal_guides(at, n)]

    if c.harness == 'J11':
        x = -92.+lane
        return [(p[0], p[1], 283.+lane), (x, p[1], 283.+lane),
                (x, 178., 283.+lane), (x, 178., 30.+lane),
                (x, q[1]+10., 30.+lane), (q[0]+8., q[1]+10., q[2])]

    if c.harness in ('J6', 'J7'):
        if c.start.startswith('reed-'):
            return [(p[0]+4., p[1], p[2]-8.), (q[0]+4., q[1], q[2]-10.)]
        if c.end.startswith('wago-'):
            return [(p[0], p[1], 282.+lane), (28.+lane, p[1], 282.+lane),
                    (28.+lane, q[1], 282.+lane), (28.+lane, q[1], q[2])]
        raise ValueError('Reed lead missing its cap bundle: '+c.id)

    if c.harness == 'J4':
        if c.end.startswith('wago-'):
            return [(p[0], p[1], 282.+lane), (29.+lane, p[1], 282.+lane),
                    (29.+lane, q[1], 282.+lane), (29.+lane, q[1], q[2])]
        if c.end.startswith('flow.'):
            n={'flow.V':0,'flow.PULSE':1,'flow.GND':2}[c.end]
            x=40.-n*2.5
            fore=278.+n*2.5
            turn_y=353.+n*2.5
            east_lane=101.5-n*1.85
            meter_lane=q[0]+2.5*n
            # Cross above V-K, descend east of the pump and approach the
            # meter's downward native pigtail from below its two collars.
            if c.start.startswith('wago-'):
                departure=p[0]-8.
                escape=[(departure,p[1],274.),(departure,fore,274.),(x,fore,274.)]
            else:
                departure=5.-n*2.5
                escape=[(p[0],p[1],278.),(departure,p[1],278.),
                        (departure,fore,278.),(x,fore,278.)]
            return escape+[(x,fore,337.),(east_lane,fore,337.),(east_lane,turn_y,337.),
                           (east_lane,turn_y,268.),(meter_lane,turn_y,268.),
                           (meter_lane,q[1],268.),(q[0],q[1],268.)]
        raise ValueError('Sensor lead missing its cap bundle: '+c.id)

    if c.harness == 'J3':
        z = 303.+lane
        return [(p[0], p[1], 282.+lane), (p[0], 280.5, 282.+lane),
                (-49.+lane, 280.5, 282.+lane), (-49.+lane, 280.5, z),
                (-49.+lane, 434., z), (q[0], 434., z), (q[0], q[1]-6., q[2])]

    if c.harness == 'J5':
        if c.start.startswith('relay-'):
            return [(-70.+lane, p[1], p[2]), (-70.+lane, q[1], q[2])]
        return [(p[0], p[1], 283.+lane), (p[0], 280.5, 283.+lane),
                (-49.+lane, 280.5, 283.+lane), (-49.+lane, 280.5, q[2]),
                (-49.+lane, q[1], q[2])]

    if c.harness == 'AC inlet':
        y = 437.-(idx % 3)*3.2
        return [(p[0], y, p[2]), (-44., y, p[2]),
                (-44., y, q[2]), (q[0], y, q[2])]

    if c.harness == 'PSU primary':
        x = -41.5
        return [(p[0], 437., p[2]), (x, 437., p[2]),
                (x, q[1]+6., p[2]), (q[0], q[1]+6., p[2])]

    if c.harness == '12V power':
        if c.start.startswith('psu.'):
            return [(p[0], 342., p[2]), (-49.+lane, 342., p[2]),
                    (-49.+lane, 342., 282.+lane), (-49.+lane, 280.5, 282.+lane),
                    (29.+lane, 280.5, 282.+lane), (29.+lane, q[1], 282.+lane),
                    (29.+lane, q[1], q[2])]
        return [(31.+lane, p[1], p[2]), (31.+lane, p[1], 284.+lane),
                (31.+lane, q[1]+9., 284.+lane), (q[0], q[1]+9., 284.+lane),
                (q[0], q[1]+9., q[2])]

    if c.harness == 'Diaphragm pump':
        if c.end.startswith('relay-'):
            return [(31., p[1], p[2]), (31., 280.5, 282.),
                    (-49., 280.5, 282.), (-49., 280.5, 338.),
                    (-49., q[1], 338.), (q[0]+8., q[1], 338.)]
        if c.start.startswith('wago-'):
            return [(31., p[1], p[2]), (31., p[1], 284.), (31., 280.5, 284.),
                    (-49., 280.5, 284.), (-49., 280.5, 300.),
                    (-49., 457., 300.), (q[0], 457., 300.), (q[0], 457., q[2])]
        return [(p[0]+8., p[1], p[2]), (-49.+lane, p[1], p[2]),
                (-49.+lane, 457., p[2]), (q[0], 457., p[2]), (q[0], 457., q[2])]

    if c.harness == 'Compressor':
        if c.start.startswith('fuse.'):
            return [(p[0]+7., p[1], p[2]), (q[0]+7., q[1], q[2])]
        return [(p[0], 435., p[2]), (-52., 435., p[2]),
                (-52., q[1], p[2]), (q[0]+8., q[1], p[2]),
                (q[0]+8., q[1], q[2])]

    if c.harness == 'Earth bonds':
        return [(p[0], 435., p[2]), (-49., 435., 340.),
                (-49., 280., 340.), (28., 280., 340.), (28., 240., 340.),
                (28., 240., 282.), (28., q[1], 282.), (q[0], q[1], 282.)]
    raise ValueError('No installed route family for '+c.id)


def pump_lead_guides(c, at, n):
    """One J13 conductor through the common mouth and transverse terminal channel."""
    p = at.terminals[c.start].point
    z = 277.3+n*1.9
    return [(p[0], p[1], z), (-36., 157., z), *pump_terminal_guides(c, at, n)]


def pump_terminal_guides(c, at, n):
    tab = at.terminals[c.end].point
    bank = c.end.split('.')[0]
    axis_x = sum(at.terminals[f'{bank}.{i}'].point[0] for i in (1, 2))/2
    x = (1.5-n)*RIBBON_PITCH_MM
    lane = RIBBON_PITCH_MM/2 if abs(tab[0]) > abs(axis_x) else -RIBBON_PITCH_MM/2
    return pump_internal_guides(at, x, tab[0], lane, n)


def pump_internal_guides(at, x, terminal_x, lane, n):
    """Bare 4P ribbon below the display ribbon, then one pair to either motor."""
    rear, fore = at.passages['front-top-electrical']['points_mm']
    cross = at.passages['front-top-pump-cross']['points_mm'][1]
    return [(x, rear[1]+14.5, rear[2]-2.7+n*1.9),
            (x, rear[1]+5.5, rear[2]-4.5),
            (x, fore[1]+22., rear[2]-4.5),
            (x, cross[1]+8., cross[2]),
            (x, cross[1]+lane, cross[2]),
            (terminal_x, cross[1]+lane, cross[2])]


def display_internal_guides(at, n):
    """Bare display ribbon from the shared mouth up to the display pocket."""
    x = (n-1.5)*RIBBON_PITCH_MM
    rear = at.passages['front-top-electrical']['points_mm'][0]
    low, high = at.passages['front-top-display-chimney']['points_mm']
    # The link's fore mouth is centred on the module rear plane plus the
    # terminal approach. routed() appends that per-terminal end land directly,
    # letting the four conductors fan out without a short lateral kink.
    return [(x, rear[1], rear[2]+4.5),
            (x, low[1], rear[2]+4.5),
            (x, high[1], high[2])]
