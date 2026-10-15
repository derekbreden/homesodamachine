"""Apply the established bridge recipe and review the actual wall crossings."""
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import LineString, Point

HERE = Path(__file__).resolve().parent
loader = importlib.util.spec_from_file_location('v4_treatments', HERE.parent/'bonding-and-fins-v4/finish.py')
v4 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v4)
loader = importlib.util.spec_from_file_location('v6_speeds', HERE.parent/'finish-matrix-v6/finish.py')
v6 = importlib.util.module_from_spec(loader)
loader.loader.exec_module(v6)
sys.path.insert(0, str(HERE.parents[3]/'tools'))
from bambu_print_archive import package


def review(raw, spec):
    paths = v4.segments(raw.decode())
    rows, drawing = [], []
    lo, hi = np.full(2, np.inf), np.full(2, -np.inf)
    for p in paths:
        xy = np.asarray([p['a'][:2], p['b'][:2]])
        lo = np.minimum(lo, xy.min(axis=0)-p['width']/2)
        hi = np.maximum(hi, xy.max(axis=0)+p['width']/2)
    for part in spec['parts']:
        own = [v4.local(p, part) for p in paths if p['object'] == part['identify_id']]
        first = [p for p in own if abs(p['z']-part['first_roof_z_mm']) < 1e-4]
        left = [p for p in own if abs(p['z']-part['roof_bottom_z_mm']) < 1e-4
                and (p['a'][0]+p['b'][0])/2 < 3.01]
        right = [p for p in own if abs(p['z']-part['wall_top_z_mm']) < 1e-4
                 and 14.99 < (p['a'][0]+p['b'][0])/2 < 16.01
                 and -.01 < (p['a'][1]+p['b'][1])/2 < 12.01]
        a, b = v4.footprint(left), v4.footprint(right)
        main = [p for p in first if p['feature'] == 'Bridge'
                and abs(p['a'][1]-p['b'][1]) < .005
                and min(p['a'][0], p['b'][0]) < 3.1
                and max(p['a'][0], p['b'][0]) > 14.9]
        other_crossings = [p for p in first if p['feature'].endswith('wall')
                           and abs(p['a'][1]-p['b'][1]) < .005
                           and min(p['a'][0], p['b'][0]) < 3.1
                           and max(p['a'][0], p['b'][0]) > 14.9]
        probes = []
        for p in main:
            e0, e1 = sorted([p['a'][:2], p['b'][:2]], key=lambda q:q[0])
            probes.append({'line': p['line'], 'local_endpoints_mm': [e0.tolist(), e1.tolist()],
                           'left_center_distance_mm': Point(e0).distance(a),
                           'right_center_distance_mm': Point(e1).distance(b),
                           'left_terminal_025mm_missing': LineString([e0,e0+[.25,0]]).difference(a).length,
                           'right_terminal_025mm_missing': LineString([e1-[.25,0],e1]).difference(b).length})
        wall_first = min((p['line'] for p in first if p['feature'].endswith('wall')), default=None)
        row = {'id': part['id'], 'bridge_axis': part['bridge_axis'],
               'vertical_gap_mm': part['vertical_gap_mm'],
               'last_wall_nozzle_z_mm': max((p['z'] for p in right),default=None),
               'first_roof_nozzle_z_mm': part['first_roof_z_mm'],
               'wall_top_bead_count': len(right), 'main_bridge_strokes': len(main),
               'main_bridge_speed_mm_s': sorted({p['speed'] for p in main}),
               'main_bridge_fan_percent': sorted({round(p['fan']/2.55,4) for p in main}),
               'main_bridge_height_mm': sorted({p['height'] for p in main}),
               'first_roof_features_in_order': list(dict.fromkeys(p['feature'] for p in first)),
               'bridge_fill_before_walls': bool(main and wall_first and min(p['line'] for p in main)<wall_first),
               'main_bridge_endpoint_checks': probes,
               'maximum_endpoint_xy_distance_mm': max((max(q['left_center_distance_mm'],q['right_center_distance_mm']) for q in probes),default=None),
               'maximum_missing_terminal_025mm': max((max(q['left_terminal_025mm_missing'],q['right_terminal_025mm_missing']) for q in probes),default=None),
               'long_roof_perimeter_crossings': len(other_crossings),
               'fixed_fan_after_first_three_layers_percent': sorted({round(p['fan']/2.55,4) for p in own if p['z']>.68001}),
               'bearing_scope': 'XY projection over emitted vertical-wall top beads; G specimens retain the named vertical gap, not direct preceding-layer contact'}
        rows.append(row)
        drawing.append((part, first, left, right))
    return {'specimens': rows, 'model_bead_bounds_mm': [lo.tolist(),hi.tolist()],
            'minimum_model_bead_edge_inset_mm': min(lo[0],lo[1],325-hi[0],320-hi[1]),
            'slicer_support_segments': sum(p['feature'].startswith('Support') for p in paths),
            'trim_commands': [s.split(';',1)[0].strip() for s in v4.re.findall(r'^[ \t]*G29\.1[^\n]*',raw.decode(),v4.re.M)],
            'limits': 'Native commanded wall crossings and process settings; physical roof formation, wall removal and retained finish are unmeasured.'}, drawing


def plot(drawing):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig, axes = plt.subplots(2,3,figsize=(12,7),layout='constrained')
    for ax,(part,roof,left,right) in zip(axes.flat,drawing):
        ax.add_patch(Rectangle((0,0),3,12,facecolor='#d4e8d4',edgecolor='none'))
        ax.add_patch(Rectangle((15,0),1,12,facecolor='#d4e8d4',edgecolor='none'))
        for p in left+right:
            ax.plot([p['a'][0],p['b'][0]],[p['a'][1],p['b'][1]],color='#888888',lw=1.1)
        for p in roof:
            color='#1478c8' if p['feature']=='Bridge' else '#df7c24'
            ax.plot([p['a'][0],p['b'][0]],[p['a'][1],p['b'][1]],color=color,lw=.7)
        ax.set(xlim=(-.7,16.7),ylim=(-.7,12.7),aspect='equal',
               title=f"{part['id']}: {part['vertical_gap_mm']:.2f} mm vertical gap",
               xlabel='Along bridge (mm)',ylabel='Across roof (mm)')
    fig.suptitle('Submitted first roof: blue bridge paths; orange walls; grey bearing beads\nTop view, with Y specimens rotated for comparison. No projecting teeth.',fontsize=12)
    fig.savefig(HERE/'wall-crossings.png',dpi=170)
    plt.close(fig)


def plot_sections(spec):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    fig,axes=plt.subplots(1,3,figsize=(10,3.4),layout='constrained')
    for ax,part in zip(axes,spec['parts'][:3]):
        bottom=part['roof_bottom_z_mm']; top=part['wall_top_z_mm']
        ax.add_patch(Rectangle((14.1,bottom),1.9,1.2,facecolor='#80b8e0',edgecolor='#1478c8'))
        ax.add_patch(Rectangle((15,4.65),1,top-4.65,facecolor='#b5b5b5',edgecolor='#555555'))
        if part['empty_layers']:
            ax.annotate('',xy=(15.5,bottom),xytext=(15.5,top),
                        arrowprops={'arrowstyle':'<->','color':'#a03a20','lw':1.4})
        ax.text(14.18,6.28,'Roof',fontsize=11)
        ax.text(15.12,4.8,'Wall',fontsize=10)
        ax.set(xlim=(14.1,16.3),ylim=(4.65,6.8),aspect='equal',
               title=f"{part['id'][:2]}: {part['vertical_gap_mm']:.2f} mm gap",
               xlabel='Along bridge (mm)',ylabel='Height (mm)')
    fig.suptitle('Right-hand bearing, side section: wall directly beneath roof\nRoof continues left to its permanent model anchor.',fontsize=12)
    fig.savefig(HERE/'bearing-sections.png',dpi=180)
    plt.close(fig)


def main():
    folder = HERE/'mark1'
    project = next(p for p in folder.glob('*.3mf') if '.gcode.' not in p.name)
    spec = json.loads(project.with_suffix('.print.json').read_text())
    source = folder/'native.gcode.3mf'
    with zipfile.ZipFile(source) as z:
        data = {k:z.read(k) for k in z.namelist()}
    native = data['Metadata/plate_1.gcode']
    treated, edits = v4.transform(native,spec)
    final, speed_edits = v6.speeds(treated,spec)
    old, new = v4.segments(native.decode()), v4.segments(final.decode())
    assert len(old)==len(new)
    assert all(p['object']==q['object'] and p['feature']==q['feature'] and p['z']==q['z']
               and all(np.array_equal(p[k],q[k]) for k in ('a','b')) for p,q in zip(old,new))
    report,drawing = review(final,spec)
    metadata = {e.attrib['key']:e.attrib['value'] for e in ET.fromstring(data['Metadata/slice_info.config']).find('plate').findall('metadata')}
    report.update(native_archive=source.name,native_sha256=v4.sha(source),
                  native_gcode_sha256=hashlib.sha256(native).hexdigest(),
                  gcode_sha256=hashlib.sha256(final).hexdigest(),native_model_xyz_paths_unchanged=True,
                  native_estimated_seconds=int(metadata['prediction']),
                  native_estimated_grams=float(metadata['weight']),
                  treatments={**edits,'feed_edits':speed_edits})
    (folder/'review.json').write_text(json.dumps(report,indent=2)+'\n')
    plot(drawing)
    plot_sections(spec)
    bad = [r['id'] for r in report['specimens'] if r['main_bridge_strokes']<20
           or not r['bridge_fill_before_walls'] or r['maximum_endpoint_xy_distance_mm']>.001
           or r['maximum_missing_terminal_025mm']>.005
           or r['main_bridge_speed_mm_s'] != [25.0] or r['main_bridge_fan_percent'] != [70.0]]
    if bad:
        raise ValueError(f'Wall crossing/process review needs correction: {bad}; see review.json')
    assert report['minimum_model_bead_edge_inset_mm']>80
    assert report['slicer_support_segments']==0
    assert report['trim_commands']==['G29.1 Z0','G29.1 Z0.16']
    data['Metadata/plate_1.gcode']=final
    data['Metadata/plate_1.gcode.md5']=hashlib.md5(final).hexdigest().encode()
    output=folder/f'{project.stem}.gcode.3mf'
    with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED) as z:
        for k,v in data.items():z.writestr(k,v)
    packaging=package(output,folder/f'{project.stem}-print-only.gcode.3mf')
    (folder/'packaging.json').write_text(json.dumps(packaging,indent=2)+'\n')
    print(json.dumps({'seconds':report['native_estimated_seconds'],
                      'grams':report['native_estimated_grams']+edits['estimated_added_grams'],
                      'inset_mm':report['minimum_model_bead_edge_inset_mm'],
                      'rows':[{k:r[k] for k in ('id','main_bridge_strokes','maximum_endpoint_xy_distance_mm','maximum_missing_terminal_025mm','bridge_fill_before_walls')} for r in report['specimens']]}))


if __name__=='__main__':
    main()
