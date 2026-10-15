"""Manual native bead/contact review for the two overnight edge candidates."""
from collections import defaultdict
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import sys
from zipfile import ZipFile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import shapely
from shapely.geometry import LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'tools/bambu_print.py').exists())
sys.path[:0] = [str(ROOT / 'hardware/print-tests/petgf-fins'), str(ROOT / 'tools')]
from review import segments
from bambu_print_archive import package


def longest(mask, pitch):
    run = best = 0
    for value in mask:
        run = run+1 if value else 0
        best = max(best, run)
    return max(0, (best-1)*pitch)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('kind', choices=('base', 'tip'))
    args = ap.parse_args()
    base = args.kind == 'base'
    folder = HERE / ('base-mark2' if base else 'tip-mark1')
    spec = json.loads((folder / 'preparation.json').read_text())
    row = spec['parts'][0]
    archive = ROOT / str(spec['project']).replace('.3mf', '.gcode.3mf')
    with ZipFile(archive) as z:
        raw = z.read('Metadata/plate_1.gcode')
        checksum = z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        settings = json.loads(z.read('Metadata/project_settings.config'))
    assert hashlib.md5(raw).hexdigest() == checksum
    text = raw.decode()
    paths = segments(text)
    assert paths
    trim = .02 if base else .16
    assert [float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)', text, re.M)] == [0, trim]
    assert settings['support_type'] == 'tree(auto)' and settings['support_style'] == 'default'
    assert settings['bridge_flow'] == '1.25'
    assert all(p['fan'] == 0 for p in paths if p['z'] <= .68001)
    assert all(abs(p['fan'] - 178.5) < .001 for p in paths if p['z'] > .68001)
    assert all(abs(p['speed'] - 15) < .001 for p in paths if p['feature'] == 'Bridge' and p['z'] > .68001)
    assert all(p['speed'] <= 15.001 for p in paths if p['feature'] == 'Overhang wall')
    support_count = sum(p['feature'].startswith('Support') for p in paths)
    assert support_count > 0, 'The hybrid needs native automatic support paths'
    low = np.full(2, np.inf)
    high = -low
    for p in paths:
        xy = np.array([p['a'][:2], p['b'][:2]])
        low = np.minimum(low, xy.min(axis=0)-p['width']/2)
        high = np.maximum(high, xy.max(axis=0)+p['width']/2)
    inset = float(min(*low, 325-high[0], 320-high[1]))
    assert inset >= 80, inset
    t = np.array(row['build_transform'])
    rotation, translation, center = t[:9].reshape(3, 3).T, t[9:], np.array(row['source_center_mm'])
    normal = np.array([0, 0, 1] if base else spec['joint_plane']['normal'])
    point = np.zeros(3) if base else np.array(spec['joint_plane']['point'])
    traces = []
    active = None
    for p in paths:
        middle = (p['a']+p['b'])/2
        cad = (middle-translation) @ rotation + center
        distance = float((cad-point) @ normal)
        keep = (p['object'] == row['identify_id'] and not p['feature'].startswith('Support')
                and p['feature'] != 'Brim' and .02 <= distance <= .70
                and (not base or np.linalg.norm(cad[:2]) > 27.5))
        if not keep:
            active = None
            continue
        if active is None or active['z'] != p['z'] or np.linalg.norm(active['points'][-1]-p['a'][:2]) > .005:
            active = dict(z=p['z'], line=p['line'], points=[p['a'][:2]], width=p['width'], features=set())
            traces.append(active)
        active['points'].append(p['b'][:2])
        active['features'].add(p['feature'])
    layers = defaultdict(list)
    for p in paths:
        layers[round(p['z'], 5)].append(p)
    footprints = {}
    support_footprints = {}

    def at(z, supports=False):
        cache = support_footprints if supports else footprints
        if z not in cache:
            cache[z] = unary_union([LineString([p['a'][:2], p['b'][:2]]).buffer(p['width']/2, quad_segs=4)
                for p in layers[z] if not supports or p['feature'].startswith('Support')])
        return cache[z]

    readings = []
    for trace in traces:
        line = LineString(trace['points'])
        if line.length < .1:
            continue
        count = max(2, math.ceil(line.length/.05)+1)
        pitch = line.length/(count-1)
        samples = shapely.line_interpolate_point(line, np.linspace(0, line.length, count))
        lower_z = [z for z in layers if .001 < trace['z']-z <= .80001]
        bearing = unary_union([at(z) for z in lower_z])
        support = unary_union([at(z, True) for z in lower_z])
        overlap = shapely.intersects(bearing.buffer(trace['width']/2), samples)
        tree_overlap = shapely.intersects(support.buffer(trace['width']/2), samples)
        cad = (np.array([*line.interpolate(.5, normalized=True).coords[0], trace['z']])-translation) @ rotation + center
        readings.append(dict(z_mm=trace['z'], first_gcode_line=trace['line'], length_mm=line.length,
            width_mm=trace['width'], features=sorted(trace['features']), midpoint_cad_mm=cad.tolist(),
            start_xy_mm=list(line.coords[0]), end_xy_mm=list(line.coords[-1]),
            no_lower_bead_overlap_run_mm=longest(~overlap, pitch),
            native_tree_overlap_fraction=float(tree_overlap.mean()),
            preceding_deposition_z_mm=sorted(lower_z)))
    assert readings
    if base:
        priority = [p for p in readings if p['midpoint_cad_mm'][1] < -26 and abs(p['midpoint_cad_mm'][0]) < 9]
    else:
        priority = [p for p in readings if p['z_mm'] < 18 and abs(p['midpoint_cad_mm'][0]) < 8]
    assert priority, 'Locate the user-priority rim region'
    worst = max(readings, key=lambda p: p['no_lower_bead_overlap_run_mm'])
    report = dict(archive=str(archive.relative_to(ROOT)), archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),
        gcode_sha256=hashlib.sha256(raw).hexdigest(), embedded_md5_matches=True,
        printer=spec['printer'], specimen_count=1, repeat_control=False,
        angle_x_degrees=row['rotation_x_degrees'], emitted_trim_mm=trim,
        native_layer_count=len(layers), nozzle_z_range_mm=[min(layers), max(layers)],
        full_bead_envelope_mm=[low.tolist(), high.tolist()], minimum_edge_clearance_mm=inset,
        fan_first_three_bed_layers_percent=0, fan_after_three_layers_percent=70,
        bridge_flow=1.25, bridge_speed_mm_s=sorted({p['speed'] for p in paths if p['feature']=='Bridge'}),
        overhang_wall_speed_mm_s=sorted({p['speed'] for p in paths if p['feature']=='Overhang wall'}),
        native_automatic_support_segments=support_count, first_skin_trace_count=len(readings),
        maximum_no_lower_bead_overlap_run_mm=worst['no_lower_bead_overlap_run_mm'], worst_trace=worst,
        priority_region_maximum_no_lower_bead_overlap_run_mm=max(p['no_lower_bead_overlap_run_mm'] for p in priority),
        priority_region_traces=priority, traces=readings,
        limits='Sample pitch at most0.05mm. Actual native bead footprints within0.8mm below each course include independently spaced support layers. Geometric overlap establishes a commanded bearing location, not sag, fusion, removal effort or finish.')
    (folder/'review.json').write_text(json.dumps(report, indent=2)+'\n')
    # Show the actual deposited lower courses and the first lip skin in the priority area.
    selected = max(priority, key=lambda p: p['no_lower_bead_overlap_run_mm'])
    z = selected['z_mm']
    fig, ax = plt.subplots(figsize=(10, 8), layout='constrained')
    for p in paths:
        if -.00001 <= z-p['z'] <= .80001:
            color = '#17836b' if p['feature'].startswith('Support') else '#a3aab8'
            if abs(p['z']-z) < .00001:
                color = '#df673c'
            ax.plot([p['a'][0], p['b'][0]], [p['a'][1], p['b'][1]], color=color, lw=.7,
                    alpha=.8 if color != '#a3aab8' else .35)
    x, y = selected['start_xy_mm']
    ax.set(xlim=(translation[0]-18, translation[0]+18), ylim=(y-10, y+10), aspect='equal',
           xlabel='Printer X (mm)', ylabel='Printer Y (mm)',
           title=f'{args.kind.title()} priority edge, native Z{z:.2f}: orange current skin; green lower trees; grey lower model/fins')
    fig.savefig(folder/'priority-contact.png', dpi=160)
    plt.close(fig)
    print_only = archive.with_name(archive.name.removesuffix('.gcode.3mf')+'-print-only.gcode.3mf')
    if print_only.exists():
        with ZipFile(print_only) as prior:
            unchanged = hashlib.sha256(prior.read('Metadata/plate_1.gcode')).hexdigest() == report['gcode_sha256']
        if not unchanged:
            assert not (folder/'launch.json').exists(), 'Preserve an accepted archive'
            print_only.unlink()
    if not print_only.exists():
        packaging = package(archive, print_only)
        (folder/'packaging.json').write_text(json.dumps(packaging, indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ('traces', 'priority_region_traces')}, indent=2))
    print(json.dumps(dict(priority_region_traces=priority), indent=2))


if __name__ == '__main__':
    main()
