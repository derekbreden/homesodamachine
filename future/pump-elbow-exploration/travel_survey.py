#!/usr/bin/env python3
"""Measure every travel in a native Bambu .gcode.3mf against the material it crosses.

RUN BY HAND:

    tools/cad-venv/bin/python future/pump-elbow-exploration/travel_survey.py LABEL=SLICE.gcode.3mf ...

A travel runs from the end of one extrusion to the start of the next. Each is classed as
within one object, between objects on a layer, or across a layer change, and measured for
the length it spends over open air and over a bore rather than over that layer's printed
material. "Unavoidable air" is the narrowest gap the travel must cross at all: zero when both
ends lie on one connected island of material, else the distance between the two islands.

A layer's material is the union of its extrusion paths at their line widths. Holes smaller
than 5 mm² are gaps between beads; larger ones are bores. On the H2C, `M9711` with U and V
moves the head to the timelapse photo position; the following travel starts there.
These are commanded paths. Whether a strand forms is a physical result.
"""
import json
import math
import re
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

WORD = re.compile(r'([A-Z])([-+]?(?:\d*\.\d+|\d+\.?\d*))')
MIN_BORE_MM2 = 5.0


def arc_xy(start, end, i, j, clockwise, chord=0.3):
    """Points along a G2/G3 move after its start. Without X/Y it is a full circle."""
    cx, cy = start[0] + i, start[1] + j
    r = math.hypot(start[0] - cx, start[1] - cy)
    a0 = math.atan2(start[1] - cy, start[0] - cx)
    if math.dist(start[:2], end[:2]) < 1e-9:
        sweep = -2 * math.pi if clockwise else 2 * math.pi
    else:
        sweep = math.atan2(end[1] - cy, end[0] - cx) - a0
        if clockwise:
            sweep = sweep if sweep < -1e-9 else sweep - 2 * math.pi
        else:
            sweep = sweep if sweep > 1e-9 else sweep + 2 * math.pi
    n = max(1, math.ceil(abs(sweep) * r / chord))
    pts = [(cx + r * math.cos(a0 + sweep * k / n), cy + r * math.sin(a0 + sweep * k / n))
           for k in range(1, n + 1)]
    pts[-1] = (end[0], end[1])
    return pts


def read(path):
    """Extrusion runs per (layer, object), travels, photo stops, and each block's last feature."""
    with zipfile.ZipFile(path) as z:
        lines = z.read('Metadata/plate_1.gcode').decode().splitlines()
    pos = [0.0, 0.0, 0.0]
    layer, obj, width, feature, absolute, in_body = 0, 0, 0.6, None, True, False
    runs = defaultdict(list)
    run, travel, last = None, None, None
    travels, photos, block_ends, shapes = [], 0, Counter(), Counter()
    block_feature, moves = None, []

    def close_run():
        nonlocal run
        if run and len(run['pts']) >= 2:
            runs[(run['layer'], run['obj'])].append((run['pts'], run['width']))
        run = None

    for raw in lines:
        line = raw.strip()
        if line.startswith('; CHANGE_LAYER'):
            in_body = True
        if line.startswith('; layer num/total_layer_count:'):
            layer = int(line.split(':')[1].split('/')[0])
            continue
        if line.startswith('; start printing object, unique label id:'):
            close_run()
            obj, block_feature, moves = int(line.rsplit(':', 1)[1]), None, []
            continue
        if line.startswith('; stop printing object, unique label id:'):
            close_run()
            block_ends[block_feature] += 1
            shapes[block_shape(moves)] += 1
            continue
        if line.startswith('; FEATURE:'):
            feature = line.split(':', 1)[1].strip()
            continue
        if line.startswith('; LINE_WIDTH:'):
            width = float(line.split(':', 1)[1])
            continue
        code = line.split(';')[0].strip()
        if not code:
            continue
        cmd = code.split()[0]
        if cmd in ('G90', 'G91'):
            absolute = cmd == 'G90'
            continue
        if cmd == 'M9711' and ' U' in code:
            w = {k: float(v) for k, v in WORD.findall(code[5:])}
            photos += 1
            if travel is not None:
                travel['photo'] = (w['U'], w['V'])
                travel['photo_idx'] = len(travel['pts'])
            continue
        if cmd not in ('G0', 'G1', 'G2', 'G3'):
            continue
        w = {k: float(v) for k, v in WORD.findall(code[len(cmd):])}
        if absolute:
            nxt = [w.get('X', pos[0]), w.get('Y', pos[1]), w.get('Z', pos[2])]
        else:
            nxt = [pos[0] + w.get('X', 0.0), pos[1] + w.get('Y', 0.0), pos[2] + w.get('Z', 0.0)]
        arc = cmd in ('G2', 'G3') and ('I' in w or 'J' in w)
        seg = arc_xy(pos, nxt, w.get('I', 0.0), w.get('J', 0.0), cmd == 'G2') if arc else [(nxt[0], nxt[1])]
        moves_xy = 'X' in w or 'Y' in w or arc
        e = w.get('E')
        moves.append('ext' if e is not None and e >= 0 and moves_xy else 'xy' if moves_xy
                     else 'e+' if e is not None and e > 0 else 'e-' if e is not None and e < 0
                     else 'z' if 'Z' in w else 'feed')
        if in_body and e is not None and e >= 0 and moves_xy:
            if travel is not None:
                travel['to'] = (layer, obj)
                travel['pts'].append((pos[0], pos[1]))
                travels.append(travel)
                travel = None
            if run is None or (run['layer'], run['obj']) != (layer, obj) or abs(run['width'] - width) > 1e-6:
                close_run()
                run = dict(pts=[(pos[0], pos[1])], width=width, layer=layer, obj=obj)
            run['pts'].extend(seg)
            last, block_feature = (layer, obj), feature
        elif in_body and last is not None:
            if travel is None:
                close_run()
                travel = dict(frm=last, pts=[(pos[0], pos[1])], photo=None)
            if moves_xy:
                travel['pts'].extend(seg)
        pos = nxt
    close_run()
    return runs, travels, photos, block_ends, shapes


def block_shape(moves):
    """Whether an object block opens with travel, lower, unretract and closes with a retraction."""
    moves = [m for m in moves if m != 'feed']
    if 'ext' not in moves:
        return 'no extrusion'
    first = moves.index('ext')
    last = len(moves) - 1 - moves[::-1].index('ext')
    opening, closing = moves[:first], moves[last + 1:]
    k = len(opening) - 1
    opens = k >= 2 and opening[k] == 'e+' and opening[k - 1] == 'z'
    while opens and k > 0 and opening[k - 1] == 'z':
        k -= 1
    opens = opens and k >= 1 and all(m == 'xy' for m in opening[:k])
    closes = bool(closing) and closing[0] == 'e-'
    return ('travel, lower, unretract' if opens else 'other opening') + ' / ' + \
           ('retraction' if closes else 'other closing')


def material(paths):
    union = unary_union([LineString(p).buffer(wd / 2 + 0.03, quad_segs=4) for p, wd in paths if len(p) >= 2])
    return unary_union([Polygon(g.exterior, [r for r in g.interiors if Polygon(r).area >= MIN_BORE_MM2])
                        for g in getattr(union, 'geoms', [union])])


def survey(path):
    runs, travels, photos, block_ends, shapes = read(path)
    mat = {k: material(v) for k, v in runs.items()}
    cache = {}

    def footprint(ka, kb):
        if (ka, kb) not in cache:
            here = unary_union([g for g in (mat.get(ka), mat.get(kb)) if g is not None])
            islands = list(getattr(here, 'geoms', [here]))
            cache[(ka, kb)] = here, islands, unary_union([Polygon(i.exterior) for i in islands])
        return cache[(ka, kb)]

    rows = []
    for t in travels:
        (la, oa), (lb, ob) = t['frm'], t['to']
        kind = 'within object' if (la, oa) == (lb, ob) else ('between objects' if la == lb else 'layer change')
        start, pts = t['pts'][0], t['pts']
        if t['photo']:
            pts = [t['photo']] + pts[t['photo_idx']:]
        pts = [pts[0]] + [q for p, q in zip(pts, pts[1:]) if math.dist(p, q) > 1e-6]
        here, islands, solid = footprint((la, oa), (lb, ob))
        row = dict(kind=kind, layer=lb, length=0.0, air=0.0, bore=0.0, unavoidable=0.0)
        if len(pts) >= 2:
            line = LineString(pts)
            row['length'] = line.length
            if not here.contains(line):
                off = line.difference(here)
                row['bore'] = off.intersection(solid).length
                row['air'] = off.length - row['bore']
                near = lambda p: min(range(len(islands)), key=lambda k: islands[k].distance(Point(p)))
                a, b = near(start), near(pts[-1])
                row['unavoidable'] = 0.0 if a == b else islands[a].distance(islands[b])
        rows.append(row)

    out = {'photo_stops': photos, 'block_shapes': dict(shapes.most_common()),
           'block_last_feature': dict(block_ends.most_common())}
    for kind in ('within object', 'between objects', 'layer change'):
        rs = [r for r in rows if r['kind'] == kind]
        if rs:
            out[kind] = dict(
                travels=len(rs),
                travel_mm=round(sum(r['length'] for r in rs)),
                over_open_air_mm=round(sum(r['air'] for r in rs)),
                over_a_bore_mm=round(sum(r['bore'] for r in rs)),
                travels_over_a_bore=sum(r['bore'] > 0.3 for r in rs),
                unavoidable_air_mm=round(sum(r['unavoidable'] for r in rs)),
                travels_that_must_cross_air=sum(r['unavoidable'] > 0.3 for r in rs),
            )
    return out


if __name__ == '__main__':
    report = {}
    for arg in sys.argv[1:]:
        label, _, p = arg.partition('=')
        report[label] = survey(Path(p))
    print(json.dumps(report, indent=1))
