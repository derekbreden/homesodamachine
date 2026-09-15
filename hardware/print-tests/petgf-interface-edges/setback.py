"""Set back selected interface edges without moving any model or tree path.

This experiment uses rectangular, upright hoods and linear interface paths.
Only positive Support interface extrusion is clipped. The original XYZ route,
feed rates, retractions, temperatures and all other G-code remain unchanged.
The two interface layers are measured independently before clipping.
"""
import argparse
from collections import defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import re
import sys
import zipfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'petgf-support-interface'))
from audit_gcode import TOKEN

EPS = 1e-7


def moves(lines):
    pos = [0., 0., 0.]
    absolute, e_absolute = True, False
    last_e, obj, feature = 0., 0, ''
    width, started = None, False
    for number, line in enumerate(lines, 1):
        if line.startswith('; OBJECT_ID:'):
            obj = int(line.split(':', 1)[1]) - 2000
        elif line.startswith('; FEATURE:'):
            feature = line.split(':', 1)[1].strip()
        elif line.startswith('; LINE_WIDTH:'):
            width = float(line.split(':', 1)[1])
        elif line.startswith('; CHANGE_LAYER'):
            started = True
        code = line.split(';', 1)[0].strip()
        if not code:
            yield number, line, None
            continue
        cmd = code.split()[0]
        args = {k: float(v) for k, v in TOKEN.findall(code[len(cmd):])}
        move = None
        if cmd == 'G90': absolute = True
        elif cmd == 'G91': absolute = False
        elif cmd == 'M82': e_absolute = True
        elif cmd == 'M83': e_absolute = False
        elif cmd == 'G92':
            for i, axis in enumerate('XYZ'):
                if axis in args: pos[i] = args[axis]
            if 'E' in args: last_e = args['E']
        elif cmd in ('G0', 'G1', 'G2', 'G3'):
            start = tuple(pos)
            for i, axis in enumerate('XYZ'):
                if axis in args: pos[i] = args[axis] if absolute else pos[i] + args[axis]
            de = 0.
            if 'E' in args:
                de = args['E'] - last_e if e_absolute else args['E']
                last_e = args['E'] if e_absolute else last_e + args['E']
            if (started and feature == 'Support interface' and de > EPS
                    and math.dist(start[:2], pos[:2]) > EPS):
                assert cmd == 'G1' and absolute and not e_absolute, (number, cmd, absolute, e_absolute)
                assert abs(start[2] - pos[2]) < EPS and set(args) <= set('XYZEF'), (number, args)
                assert width is not None
                move = dict(obj=obj, z=round(pos[2], 5), a=start, b=tuple(pos),
                            width=width, e=de, args=args)
        yield number, line, move


def scan(text, specimens):
    summaries = defaultdict(lambda: defaultdict(lambda: dict(points=[], length=0., e=0., widths=set())))
    protected = hashlib.sha256()
    for _, line, move in moves(io.StringIO(text)):
        if move is None:
            protected.update(line.encode())
            continue
        assert move['obj'] in specimens, move['obj']
        assert 22.5 < move['z'] < 24.2, move['z']
        r = summaries[move['obj']][move['z']]
        r['points'].extend([move['a'][:2], move['b'][:2]])
        r['length'] += math.dist(move['a'][:2], move['b'][:2])
        r['e'] += move['e']
        r['widths'].add(move['width'])
    for layers in summaries.values():
        assert len(layers) == 2, len(layers)
        for r in layers.values():
            ps = r.pop('points')
            r['bbox'] = [min(p[0] for p in ps), min(p[1] for p in ps),
                         max(p[0] for p in ps), max(p[1] for p in ps)]
            r['widths'] = sorted(r['widths'])
    assert set(summaries) == set(specimens)
    return summaries, protected.hexdigest()


def interval(a, b, bounds):
    lo, hi = 0., 1.
    for axis in (0, 1):
        delta = b[axis] - a[axis]
        lower, upper = bounds[axis], bounds[axis+2]
        if abs(delta) < EPS:
            if not lower-EPS <= a[axis] <= upper+EPS: return None
        else:
            t0, t1 = (lower-a[axis])/delta, (upper-a[axis])/delta
            if t0 > t1: t0, t1 = t1, t0
            lo, hi = max(lo, t0), min(hi, t1)
            if hi-lo < EPS: return None
    return max(0., lo), min(1., hi)


def clip_move(line, move, box):
    keep = interval(move['a'], move['b'], box)
    if keep is not None and keep[0] < EPS and keep[1] > 1-EPS:
        return line, move['e']
    # Keep every original endpoint, feed rate and travel segment. Discarded
    # interface portions become non-extruding G1 moves on the same straight line.
    cuts = [0., 1.] if keep is None else sorted(set([0., *keep, 1.]))
    out, emitted_e = [], 0.
    for k, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
        if hi-lo < EPS: continue
        x, y = [move['a'][i]+hi*(move['b'][i]-move['a'][i]) for i in (0, 1)]
        extrusion = keep is not None and keep[0]-EPS <= (lo+hi)/2 <= keep[1]+EPS
        command = f'G1 X{x:.6f} Y{y:.6f}'
        if extrusion:
            e = round(move['e']*(hi-lo), 7)
            command += f' E{e:.7f}'
            emitted_e += e
        if k == 0 and 'F' in move['args']: command += f" F{move['args']['F']:g}"
        out.append(command+'\n')
    assert out and 0 <= emitted_e <= move['e']+EPS
    return ''.join(out), emitted_e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--experiment', type=Path, default=HERE/'experiment.json')
    args = ap.parse_args()
    experiment = json.loads(args.experiment.read_text())
    specimens = {int(r['id']): r for r in experiment['specimens']}
    with zipfile.ZipFile(args.input) as z:
        contents = {n: z.read(n) for n in z.namelist()}
    gc = 'Metadata/plate_1.gcode'
    raw = contents[gc]
    assert hashlib.md5(raw).hexdigest().upper().encode() == contents[gc+'.md5']
    original = raw.decode()
    before, protected = scan(original, specimens)
    boxes = {}
    for obj, zs in before.items():
        spec = specimens[obj]
        for z, data in zs.items():
            x0, y0, x1, y1 = data['bbox']
            wall, free = spec['wall_setback_mm'], spec['free_edge_setback_mm']
            boxes[obj, z] = [x0+wall, y0+free, x1-wall, y1-wall]
    destination = io.StringIO()
    changes = []
    untouched_hash = hashlib.sha256()
    for number, line, move in moves(io.StringIO(original)):
        replacement = line
        if move is not None:
            replacement, emitted_e = clip_move(line, move, boxes[move['obj'], move['z']])
            if replacement != line:
                changes.append(dict(source_line=number, object_id=move['obj'], z=move['z'],
                                    removed_e=move['e']-emitted_e))
        else:
            untouched_hash.update(replacement.encode())
        destination.write(replacement)
    assert untouched_hash.hexdigest() == protected
    result = destination.getvalue()
    after, _ = scan(result, specimens)
    report = dict(method=experiment['edge_method'],
                  source_bundle_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                  source_gcode_sha256=hashlib.sha256(raw).hexdigest(),
                  protected_source_commands_sha256=protected,
                  all_non_interface_source_commands_unchanged=True,
                  all_original_xyz_routes_and_feed_rates_preserved=True,
                  modified_source_lines=len(changes), layers=[])
    for obj, zs in before.items():
        spec = specimens[obj]
        for z, data in zs.items():
            a = after[obj][z]
            box = boxes[obj, z]
            assert data['widths'] == a['widths'] == [.62]
            assert all(abs(v-w) < .001 for v, w in zip(a['bbox'], box)), (obj, z, a['bbox'], box)
            fraction = a['length']/data['length']
            assert .89 < fraction <= 1.000001, (obj, z, fraction)
            if spec['wall_setback_mm'] == spec['free_edge_setback_mm'] == 0:
                assert a == data
            report['layers'].append(dict(id=spec['id'], z=z, before=data, after=a,
                wall_setback_mm=spec['wall_setback_mm'], free_edge_setback_mm=spec['free_edge_setback_mm'],
                retained_interface_path_fraction=fraction))
    new_raw = result.encode()
    contents[gc] = new_raw
    contents[gc+'.md5'] = hashlib.md5(new_raw).hexdigest().upper().encode()
    # Retain slicer time/material estimates as upper bounds. Their small extrusion
    # overestimate is preferable to inventing a new printer time prediction.
    with zipfile.ZipFile(args.output, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in contents.items(): z.writestr(name, data)
    report.update(gcode_sha256=hashlib.sha256(new_raw).hexdigest(),
                  bundle_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                  removed_filament_mm=sum(c['removed_e'] for c in changes))
    (args.output.parent/'edge-verification.json').write_text(json.dumps(report, indent=2)+'\n')
    (args.output.parent/'edge-changes.json').write_text(json.dumps(changes, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='layers'}, indent=2))


if __name__ == '__main__': main()
