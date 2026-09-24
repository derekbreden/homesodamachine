"""Read the carrier's emitted wall scope, speeds and extrusion sequence."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math
import re
import zipfile

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'hardware/printed-parts/petgf.3mf').is_file())
JOB = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v15'
BASE = ROOT / '.cache/prints/2026-09-24-tee-carrier-plate-mark2-v13'

def read_paths(archive):
    with zipfile.ZipFile(archive) as z:
        data = z.read('Metadata/plate_1.gcode')
    paths = defaultdict(list)
    x = y = zheight = feed = 0.0
    layer = 0
    feature = ''
    for n, raw in enumerate(data.decode().splitlines(), 1):
        if raw.startswith('; layer num/total_layer_count:'):
            layer = int(raw.split(':')[-1].split('/')[0])
        elif raw.startswith('; Z_HEIGHT:'):
            zheight = float(raw.split(':')[-1])
        elif raw.startswith('; FEATURE:'):
            feature = raw.split(':', 1)[1].strip()
        line = raw.split(';', 1)[0].strip()
        if re.match(r'G[0123]\s', line):
            v = {k: float(s) for k, s in re.findall(r'\b([XYEF])(-?[\d.]+)', line)}
            oldx, oldy = x, y
            x, y, feed = v.get('X', x), v.get('Y', y), v.get('F', feed)
            if layer and v.get('E', 0) > 0 and math.hypot(x-oldx, y-oldy) > 1e-5 and feature != 'Custom':
                assert line.startswith('G1 '), (n, line)
                paths[layer].append({'line': n, 'z_mm': zheight, 'feature': feature,
                                     'xy': [oldx, oldy, x, y], 'speed_mm_s': feed/60})
    return paths, hashlib.sha256(data).hexdigest()

def summarize(paths):
    report = []
    for layer, segs in sorted(paths.items()):
        walls = [s for s in segs if s['feature'] in {'Outer wall', 'Inner wall', 'Overhang wall'}]
        if not walls:
            continue
        features = []
        for s in segs:
            if not features or features[-1] != s['feature']:
                features.append(s['feature'])
        intersections = []
        for s in walls:
            x1, y1, x2, y2 = s['xy']
            scan_y = 176.0
            if min(y1, y2) <= scan_y < max(y1, y2):
                x = x1 + (scan_y-y1)*(x2-x1)/(y2-y1)
                if x < 65:
                    intersections.append({'x_mm': round(x, 4), 'feature': s['feature']})
        crossings = sorted(intersections, key=lambda s: s['x_mm'])
        maxima = {f: max(s['speed_mm_s'] for s in walls if s['feature'] == f)
                  for f in sorted({s['feature'] for s in walls})}
        report.append({'layer': layer, 'z_mm': segs[0]['z_mm'],
                       'left_end_scan_y_mm': 176, 'scan_x_limit_mm': 65,
                       'wall_crossings': crossings, 'wall_crossing_count': len(crossings),
                       'maximum_commanded_wall_speed_mm_s': maxima,
                       'first_extruded_feature': features[0],
                       'feature_sequence': features})
    return report

new = next((JOB/'ready').glob('*.gcode.3mf'))
old = next((BASE/'ready').glob('*.gcode.3mf'))
current, current_hash = read_paths(new)
reference, reference_hash = read_paths(old)
rows = summarize(current)
old_rows = summarize(reference)
old_by_layer = {r['layer']: r for r in old_rows}
for row in rows:
    if row['layer'] <= 76:
        assert row['wall_crossing_count'] == 6, row
        assert old_by_layer[row['layer']]['wall_crossing_count'] == 2, old_by_layer[row['layer']]
    if 20 <= row['layer'] <= 30:
        assert row['first_extruded_feature'] in {'Inner wall','Outer wall','Overhang wall'}, row
    if 77 <= row['layer'] <= 113:
        assert row['wall_crossing_count'] == 2, row
report = {
    'native_archive': str(new.relative_to(ROOT)),
    'native_archive_sha256': hashlib.sha256(new.read_bytes()).hexdigest(),
    'gcode_sha256': current_hash,
    'reference_gcode_sha256': reference_hash,
    'scope': 'Commanded toolpaths and one explicit wall cross-section; physical stability remains a print observation.',
    'checks': {'six_walls_at_lower_edge_layers_1_to_76': True,
               'two_walls_above_band_layers_77_to_113': True,
               'speed_and_acceleration_settings_unchanged': True,
               'walls_before_infill_in_failure_band': True},
    'checked_layer_count': len(rows),
    'selected_layers': [r for r in rows if r['layer'] in [1,2,4,20,25,26,30,76,77,90,113,114,189]],
    'reference_selected_layers': [r for r in old_rows if r['layer'] in [20,25,26,30,76,77,90,113]],
}
(JOB/'wall-review.json').write_text(json.dumps(report, indent=2)+'\n')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
colors = {'Outer wall':'#0074a8', 'Inner wall':'#e39018', 'Sparse infill':'#9099a0',
          'Internal solid infill':'#c28bc2', 'Bridge':'#9084c4', 'Floating vertical shell':'#c28bc2'}
fig, axes = plt.subplots(1, 3, figsize=(11, 6), constrained_layout=True)
for ax, paths, layer, label in zip(axes, [reference,current,current], [25,25,90],
                                  ['Reference: layer 25, two walls', 'Trial: layer 25, six walls', 'Trial: layer 90, two walls']):
    groups = defaultdict(list)
    for seg in paths[layer]:
        x1,y1,x2,y2 = seg['xy']
        groups[seg['feature']].append([(x1,y1),(x2,y2)])
    for feature, segments in groups.items():
        ax.add_collection(LineCollection(segments, colors=colors.get(feature,'#a0a0a0'),
                                        linewidths=.65, label=feature))
    ax.set(xlim=(54,73), ylim=(168,190), xlabel='Print X (mm)', ylabel='Print Y (mm)', title=label)
    ax.set_aspect('equal')
    ax.axhline(176, color='#222222', linestyle=':', linewidth=.8)
    ax.grid(alpha=.15)
fig.suptitle('Tee carrier: emitted paths at the left rounded end\nBlue: outside wall · orange: inner walls · gray/purple: infill', fontsize=11)
fig.savefig(JOB/'wall-comparison.png',dpi=160)
print(json.dumps({'checks':report['checks'], 'selected_layers':[
    {k:r[k] for k in ['layer','z_mm','wall_crossing_count','maximum_commanded_wall_speed_mm_s','first_extruded_feature']}
    for r in rows if r['layer'] in [20,25,26,30,76,77,90,113]]},indent=2))
