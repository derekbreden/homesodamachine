"""Manual review of the accepted arc transfer and complete-project native commands."""
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
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
sys.path[:0] = [str(HERE.parent), str(ROOT / 'hardware/print-tests/petgf-fins'), str(ROOT / 'tools/gcode')]
import refresh_print_project as writer
from review import segments
from toolpaths import WORD


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def vertices(raw):
    return np.array([[float(v.get(k)) for k in 'xyz'] for v in ET.fromstring(raw).findall('.//' + writer.qn('vertex'))])


def material_review(gcode, report, early_max_z=16.8, *, localized_cooling=False,
                    first_three_max_z=.68):
    names = {p['identify_id']: p['name'] for p in report['parts']}
    readings = {label:dict(part=name, extruding_commands=0, first_three_fans=set(), later_fans=set(),
        bridge_speeds=set(), overhang_speeds=set(), features=set(), fan_by_feature={}) for label,name in names.items()}
    obj, feature, z, fan, feed = None, '', 0., 0., 0.
    xy = np.zeros(2)
    absolute_xyz, relative_e, e_pos = True, True, 0.
    violations = []
    early = []
    with gcode.open() as stream:
        for number, raw in enumerate(stream, 1):
            if z <= early_max_z + .00001:
                early.append(raw)
            if raw.startswith(';'):
                comment = raw[1:].strip()
                if comment.startswith('Z_HEIGHT:'):
                    z = float(comment.split(':',1)[1])
                elif comment.startswith('FEATURE:'):
                    feature = comment.split(':',1)[1].strip()
                elif comment.startswith('OBJECT_ID:'):
                    obj = int(comment.split(':',1)[1])
                elif comment.startswith('start printing object, unique label id:'):
                    obj = int(comment.rsplit(':',1)[1])
                elif comment.startswith('stop printing object'):
                    obj = None
                continue
            code = raw.split(';',1)[0].strip()
            if not code:
                continue
            cmd = code.split(None,1)[0]
            words = {k:float(v) for k,v in WORD.findall(code[len(cmd):])}
            if cmd in ('G90','G91'):
                absolute_xyz = cmd == 'G90'
            elif cmd in ('M82','M83'):
                relative_e = cmd == 'M83'
            elif cmd == 'G92':
                for axis,k in enumerate('XY'):
                    xy[axis] = words.get(k,xy[axis])
                e_pos = words.get('E',e_pos)
            elif cmd == 'M106' and words.get('P',1) == 1:
                fan = words.get('S',255)
            elif cmd in ('G0','G1','G2','G3'):
                feed = words.get('F',feed*60)/60
                next_xy = xy.copy()
                for axis,k in enumerate('XY'):
                    if k in words:
                        next_xy[axis] = words[k] if absolute_xyz else xy[axis]+words[k]
                de = words.get('E',0) if relative_e else words.get('E',e_pos)-e_pos
                if 'E' in words:
                    e_pos = e_pos+words['E'] if relative_e else words['E']
                if obj in readings and de > 0 and np.linalg.norm(next_xy-xy) > 1e-8:
                    item = readings[obj]
                    item['extruding_commands'] += 1
                    item['features'].add(feature)
                    item['fan_by_feature'].setdefault(feature, set()).add(fan/2.55)
                    first_three = z <= first_three_max_z + .00001
                    item['first_three_fans' if first_three else 'later_fans'].add(fan/2.55)
                    allowed = (0., 178.5) if localized_cooling and not first_three else (0 if first_three else 178.5,)
                    if min(abs(fan-value) for value in allowed) > .001:
                        violations.append(dict(line=number, part=names[obj], feature=feature, z=z, fan=fan))
                    if feature == 'Bridge':
                        item['bridge_speeds'].add(feed)
                        assert abs(feed-15) < .001
                    if feature == 'Overhang wall':
                        item['overhang_speeds'].add(feed)
                        assert feed <= 15.001
                xy = next_xy
    assert not violations, violations[:10]
    result = []
    for item in readings.values():
        assert item['extruding_commands'] > 0
        for key,value in list(item.items()):
            if isinstance(value,set):
                item[key] = sorted(value)
        item['fan_by_feature'] = {k: sorted(v) for k,v in item['fan_by_feature'].items()}
        result.append(item)
    return result, ''.join(early)


def longest(mask, pitch):
    run = best = 0
    for v in mask:
        run = run+1 if v else 0
        best = max(best,run)
    return max(0,(best-1)*pitch)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--native-directory', type=Path, required=True)
    ap.add_argument('--baseline', type=Path, required=True)
    args = ap.parse_args()
    report = json.loads((HERE/'faucet-industrial-petgf.print.json').read_text())
    project = HERE/Path(report['project']).name
    gcode = args.native_directory/'plate_1.gcode'
    transfer = report['base_rim_supports']
    origin = json.loads((ROOT/transfer['source_preparation']).read_text())['parts'][0]
    target = next(p for p in report['parts'] if p['name'] == transfer['part'])
    errors = []
    with ZipFile(ROOT/transfer['source_project']) as source, ZipFile(project) as prepared, ZipFile(args.baseline) as prior:
        for part in report['parts']:
            current, baseline = prepared.read(part['member']), prior.read(part['member'])
            if part['name'] == 'faucet-shell-tip' and report.get('tip_supports'):
                a, b = ET.fromstring(current), ET.fromstring(baseline)
                assert np.array_equal(vertices(current), vertices(baseline))
                for tree in (a, b):
                    for triangle in tree.findall('.//' + writer.qn('triangle')):
                        triangle.attrib.pop('paint_supports', None)
                assert writer.xml(a) == writer.xml(b), 'Tip changes are confined to support paint'
            else:
                assert current == baseline, part['name']
        for member in ('Metadata/project_settings.config','Metadata/layer_config_ranges.xml'):
            assert prepared.read(member) == prior.read(member), member
        for item in transfer['components']:
            a = vertices(source.read(item['source_member']))
            b = vertices(prepared.read(item['member']))
            cad_a = a+np.array(origin['source_center_mm'])
            cad_b = b+np.array(target['source_center_mm'])
            error = float(abs(cad_a-cad_b).max())
            assert error < 1e-7
            st = np.array(origin['build_transform'])
            tt = np.array(target['build_transform'])
            source_world = a@st[:9].reshape(3,3)+st[9:]
            target_world = b@tt[:9].reshape(3,3)+tt[9:]
            z_error = float(abs(source_world[:,2]-target_world[:,2]).max())
            assert z_error < .00001, z_error
            errors.append(dict(component_id=item['component_id'], kind=item['kind'],
                maximum_cad_coordinate_error_mm=error, maximum_build_z_error_mm=z_error))
        settings_sha = writer.digest(prepared.read(writer.SETTINGS_MEMBER))
    material, early = material_review(gcode,report)
    paths = segments(early)
    t = np.array(target['build_transform'])
    rot, trans, center = t[:9].reshape(3,3).T,t[9:],np.array(target['source_center_mm'])
    traces = []
    active = None
    layers = defaultdict(list)
    for p in paths:
        layers[round(p['z'],5)].append(p)
        cad = ((p['a']+p['b'])/2-trans)@rot+center
        keep = (p['object'] == target['identify_id'] and not p['feature'].startswith('Support')
            and p['feature'] != 'Brim' and .02 <= cad[2] <= .70 and np.linalg.norm(cad[:2]) > 27.5)
        if not keep:
            active = None
            continue
        if active is None or active['z'] != p['z'] or np.linalg.norm(active['points'][-1]-p['a'][:2]) > .005:
            active = dict(z=p['z'], line=p['line'], points=[p['a'][:2]], width=p['width'])
            traces.append(active)
        active['points'].append(p['b'][:2])
    cache = {}
    def at(z):
        if z not in cache:
            cache[z] = unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2,quad_segs=4) for p in layers[z]])
        return cache[z]
    readings = []
    for trace in traces:
        line = LineString(trace['points'])
        if line.length < .1:
            continue
        n = max(2,math.ceil(line.length/.05)+1)
        pitch = line.length/(n-1)
        samples = shapely.line_interpolate_point(line,np.linspace(0,line.length,n))
        bearing = unary_union([at(z) for z in layers if .001 < trace['z']-z <= .80001])
        overlap = shapely.intersects(bearing.buffer(trace['width']/2),samples)
        cad = (np.array([*line.interpolate(.5,normalized=True).coords[0],trace['z']])-trans)@rot+center
        readings.append(dict(z_mm=trace['z'], first_gcode_line=trace['line'], length_mm=line.length,
            no_lower_bead_overlap_run_mm=longest(~overlap,pitch), midpoint_cad_mm=cad.tolist(),
            start_xy_mm=list(line.coords[0]), end_xy_mm=list(line.coords[-1])))
    priority = [p for p in readings if p['midpoint_cad_mm'][1] < -26 and abs(p['midpoint_cad_mm'][0]) < 9]
    critical = [p for p in priority if abs(p['z_mm']-15.32) < .001]
    assert critical
    assert max(p['no_lower_bead_overlap_run_mm'] for p in critical) < .1
    sha = writer.digest(project.read_bytes())
    with gcode.open('rb') as stream:
        gcode_sha = hashlib.file_digest(stream,'sha256').hexdigest()
    save(HERE/'overhang-native-review.json',dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),
        project=str(project.relative_to(ROOT)), project_sha256=sha, gcode_source=str(gcode), gcode_sha256=gcode_sha,
        settings_sha256=settings_sha, bridge_flow='1.25', parts=material, fan_violations=[],
        scope='Manual native command review on all five rigid parts with the selected base-rim arcs, tip fins, lip support paint and hidden-root disc. Local physical records retain their identified short-section scope.'))
    output = dict(project=str(project.relative_to(ROOT)), project_sha256=sha, gcode_sha256=gcode_sha,
        physical_reference=transfer['physical_result'], accepted_source_project=transfer['source_project'],
        primary_part_geometry_and_seam_paint_preserved=True,
        tip_support_paint_only_change=bool(report.get('tip_supports')),
        machine_material_settings_and_layer_ranges_preserved_byte_for_byte=True,
        component_transfer_errors=errors, arc_count=transfer['arc_count'],
        native_rim_trace_count=len(readings), critical_front_traces=critical,
        priority_region_maximum_no_lower_bead_overlap_run_mm=max(p['no_lower_bead_overlap_run_mm'] for p in priority),
        maximum_above_three_bed_courses_no_lower_overlap_run_mm=max(p['no_lower_bead_overlap_run_mm'] for p in readings if p['z_mm'] > .68001),
        scope='Exact accepted seven arc walls and narrow blockers transferred to the full base at unchanged build Z, with the complete placement and support review in faucet-industrial-petgf.support-audit.json.',
        limits='Native first-skin samples are at most0.05mm apart and compare deposited bead footprints within0.8mm below. Geometry and commanded contacts do not establish finish or removal on unprinted features. No new printer job is submitted.')
    save(HERE/'rim-support-native-review.json',output)
    selected = max(critical,key=lambda p:p['length_mm'])
    fig,ax = plt.subplots(figsize=(10,6),layout='constrained')
    for p in paths:
        if 0 <= selected['z_mm']-p['z'] <= .80001:
            color = '#16866b' if p['feature'].startswith('Support') else '#a1aabb'
            if abs(p['z']-selected['z_mm']) < .00001:
                color = '#df673c'
            ax.plot([p['a'][0],p['b'][0]],[p['a'][1],p['b'][1]],color=color,lw=.7,alpha=.75)
    x,y = selected['start_xy_mm']
    ax.set(xlim=(trans[0]-18,trans[0]+18),ylim=(y-6,y+6),aspect='equal',
        xlabel='Printer X (mm)',ylabel='Printer Y (mm)',title='Complete base: front rim at Z15.32; current skin orange, lower beads grey/green')
    fig.savefig(HERE/'rim-support-native-contact.png',dpi=150)
    plt.close(fig)
    print(json.dumps(output,indent=2))


if __name__ == '__main__':
    main()
