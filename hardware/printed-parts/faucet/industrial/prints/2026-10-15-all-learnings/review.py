"""Manual review and packaging of this two-plate complete faucet; never sends."""
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import math
import re
import shutil
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
INDUSTRIAL = HERE.parents[1]
ROOT = next(p for p in HERE.parents if (p/'tools/bambu_print.py').exists())
sys.path[:0] = [str(INDUSTRIAL), str(INDUSTRIAL.parent), str(ROOT/'tools')]
from review_rim_supports import material_review, vertices, longest, segments
import refresh_print_project as writer
from bambu_print_archive import package


def save(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def footprint(paths):
    return unary_union([LineString([p['a'][:2],p['b'][:2]]).buffer(p['width']/2,quad_segs=4) for p in paths])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('printer', choices=('mark1','mark2'))
    args = ap.parse_args()
    folder = HERE/args.printer
    native = ROOT/'.cache/printer-control/faucet-complete-all-learnings-20261015'/(args.printer+'-native')
    report = json.loads((folder/'preparation.json').read_text())
    project = ROOT/report['project']
    base = args.printer == 'mark2'
    transfer = report['base_rim_supports' if base else 'tip_supports']
    target = next(p for p in report['parts'] if p['name'] == transfer['part'])
    origin = json.loads((ROOT/transfer['source_preparation']).read_text())['parts'][0]
    errors = []
    with ZipFile(project) as prepared, ZipFile(INDUSTRIAL/'faucet-industrial-petgf.3mf') as parent, ZipFile(ROOT/transfer['source_project']) as source:
        for part in report['parts']:
            assert prepared.read(part['member']) == parent.read(part['member'])
        for c in transfer['components']:
            a, b = vertices(source.read(c['source_member'])), vertices(prepared.read(c['member']))
            cad_error = float(abs(a+origin['source_center_mm']-b-target['source_center_mm']).max())
            at, bt = np.array(origin['build_transform']),np.array(target['build_transform'])
            aw, bw = a@at[:9].reshape(3,3)+at[9:], b@bt[:9].reshape(3,3)+bt[9:]
            z_error = float(abs(aw[:,2]-bw[:,2]).max())
            assert cad_error < 1e-7 and z_error < 1e-5
            atri = ET.fromstring(source.read(c['source_member'])).findall('.//'+writer.qn('triangle'))
            btri = ET.fromstring(prepared.read(c['member'])).findall('.//'+writer.qn('triangle'))
            assert [t.attrib for t in atri] == [t.attrib for t in btri]
            errors.append(dict(component_id=c['component_id'],maximum_cad_coordinate_error_mm=cad_error,maximum_build_z_error_mm=z_error))
        settings_raw = prepared.read(writer.SETTINGS_MEMBER)
        settings = json.loads(settings_raw)
    assert settings['bridge_flow'] == '1.25'
    assert settings['support_type'] == 'tree(auto)' and settings['support_style'] == 'default'
    gcode = native/'plate_1.gcode'
    material, early = material_review(gcode,report,early_max_z=40 if not base else 16.8)
    save(native/'material-commands.json', material)
    assert [float(v) for v in re.findall(r'^\s*G29\.1 Z([-+.\d]+)',early,re.M)] == [0,.02 if base else .16]
    paths = segments(early)
    t = np.array(target['build_transform'])
    inverse,trans,center = t[:9].reshape(3,3).T,t[9:],np.array(target['source_center_mm'])
    normal = np.array([0,0,1] if base else transfer['joint_plane']['normal'])
    point = np.zeros(3) if base else np.array(transfer['joint_plane']['point'])
    traces,active,layers = [],None,defaultdict(list)
    for p in paths:
        layers[round(p['z'],5)].append(p)
        cad = ((p['a']+p['b'])/2-trans)@inverse+center
        d = float((cad-point)@normal)
        keep = p['object'] == target['identify_id'] and not p['feature'].startswith('Support') and p['feature'] != 'Brim' and .02 <= d <= .70 and (not base or np.linalg.norm(cad[:2])>27.5)
        if not keep:
            active = None
            continue
        if active is None or active['z'] != p['z'] or np.linalg.norm(active['points'][-1]-p['a'][:2])>.005:
            active = dict(z=p['z'],line=p['line'],points=[p['a'][:2]],width=p['width'])
            traces.append(active)
        active['points'].append(p['b'][:2])
    cache = {}
    def at(z):
        if z not in cache:
            cache[z] = footprint(layers[z])
        return cache[z]
    readings = []
    for trace in traces:
        line = LineString(trace['points'])
        if line.length<.1:
            continue
        n = max(2,math.ceil(line.length/.05)+1)
        samples = shapely.line_interpolate_point(line,np.linspace(0,line.length,n))
        bearing = unary_union([at(z) for z in layers if .001<trace['z']-z<=.80001])
        overlap = shapely.intersects(bearing.buffer(trace['width']/2),samples)
        cad = (np.array([*line.interpolate(.5,normalized=True).coords[0],trace['z']])-trans)@inverse+center
        readings.append(dict(z_mm=trace['z'],first_gcode_line=trace['line'],length_mm=line.length,
            no_lower_bead_overlap_run_mm=longest(~overlap,line.length/(n-1)),midpoint_cad_mm=cad.tolist(),
            start_xy_mm=list(line.coords[0]),end_xy_mm=list(line.coords[-1])))
    if base:
        priority = [p for p in readings if p['midpoint_cad_mm'][1]<-26 and abs(p['midpoint_cad_mm'][0])<9]
    else:
        priority = [p for p in readings if p['z_mm']<18 and abs(p['midpoint_cad_mm'][0])<8]
    assert priority
    if base:
        critical = [p for p in priority if abs(p['z_mm']-15.32)<.001]
        assert critical and max(p['no_lower_bead_overlap_run_mm'] for p in critical)<.1
    else:
        critical = priority
        save(native/'tip-rim-diagnostic.json', dict(priority=priority,all_traces=readings))
        print('TIP PRIORITY MAX',max(p['no_lower_bead_overlap_run_mm'] for p in critical),flush=True)
    root = None
    if not base:
        # The accepted anchor centre follows the same rigid translation as its mesh.
        with ZipFile(ROOT/transfer['source_project']) as accepted:
            a = vertices(accepted.read(transfer['components'][-1]['source_member']))[0]
        old_t = np.array(origin['build_transform'])
        old_w = a@old_t[:9].reshape(3,3)+old_t[9:]
        new_local = a+np.array(origin['source_center_mm'])-center
        shift = (new_local@t[:9].reshape(3,3)+t[9:]-old_w)[:2]
        root_center = np.array([162.5,153.15])+shift
        def root_paths(z):
            return [p for p in layers[round(z,5)] if p['object']==target['identify_id'] and not p['feature'].startswith('Support') and p['feature']!='Brim' and abs(((p['a']+p['b'])/2)[0]-root_center[0])<6 and -5.15<((p['a']+p['b'])/2)[1]-root_center[1]<4.85]
        courses = []
        for z in (.2,.44,.68,.92,1.16):
            own = footprint(root_paths(z))
            assert not own.is_empty
            overlap = None if z==.2 else own.intersection(footprint(root_paths(round(z-.24,5)))).area
            assert z==.2 or overlap>1
            courses.append(dict(nozzle_z_mm=z,footprint_area_mm2=own.area,previous_root_course_overlap_area_mm2=overlap))
        assert courses[0]['footprint_area_mm2']>45
        root = dict(center_printer_xy_mm=root_center.tolist(),courses=courses,starting_root_courses_directly_joined=True,contact_scope=transfer['root_contact_scope'])
    archive = project.with_suffix('.gcode.3mf')
    assert not (folder/'launch.json').exists()
    if archive.exists():
        assert archive.read_bytes() == (native/'native.gcode.3mf').read_bytes()
    else:
        shutil.copy2(native/'native.gcode.3mf',archive)
    raw = gcode.read_bytes()
    with ZipFile(archive) as z:
        assert z.read('Metadata/plate_1.gcode') == raw
        assert hashlib.md5(raw).hexdigest() == z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        native_settings_raw = z.read(writer.SETTINGS_MEMBER)
    with ZipFile(ROOT/transfer['source_project'].replace('.3mf','.gcode.3mf')) as accepted:
        assert json.loads(native_settings_raw) == json.loads(accepted.read(writer.SETTINGS_MEMBER)), 'Native settings match the accepted article on this printer'
    fit = json.loads(project.with_suffix('.support-audit.json').read_text())['fit']
    result = dict(recorded_at_utc=datetime.now(timezone.utc).isoformat(),project=report['project'],
        project_sha256=report['project_sha256'],archive=str(archive.relative_to(ROOT)),archive_sha256=writer.digest(archive.read_bytes()),
        gcode_sha256=writer.digest(raw),embedded_md5_matches=True,settings_sha256=writer.digest(settings_raw),
        native_settings_sha256=writer.digest(native_settings_raw),native_settings_match_accepted_article=True,
        material_commands=material,bridge_flow=1.25,component_transfer_errors=errors,
        primary_geometry_and_settings_preserved_from_complete_parent=True,critical_rim_traces=critical,
        priority_region_maximum_no_lower_bead_overlap_run_mm=max(p['no_lower_bead_overlap_run_mm'] for p in priority),
        first_skin_trace_count=len(readings),root_anchor=root,fit=fit,
        physical_reference=transfer['physical_result'],repeat_control=False,
        limits='Manual native command/contact review. First-skin samples at most 0.05 mm apart compare deposited bead footprints within 0.8 mm below. Physical acceptance remains scoped to the identified source articles; this complete faucet requires its own result.')
    save(folder/'native-review.json',result)
    fig,ax = plt.subplots(figsize=(9,7),layout='constrained')
    selected = max(critical,key=lambda p:p['length_mm'])
    z = selected['z_mm']
    for p in paths:
        if 0 <= z-p['z']<=.80001:
            color = '#16866b' if p['feature'].startswith('Support') else '#a1aabb'
            if abs(p['z']-z)<1e-5: color='#df673c'
            ax.plot([p['a'][0],p['b'][0]],[p['a'][1],p['b'][1]],color=color,lw=.7,alpha=.7)
    ax.set(xlim=(trans[0]-18,trans[0]+18),ylim=(selected['start_xy_mm'][1]-10,selected['start_xy_mm'][1]+10),aspect='equal',xlabel='Printer X (mm)',ylabel='Printer Y (mm)',title=f'{args.printer}: native priority rim at Z{z:.2f}')
    fig.savefig(folder/'priority-contact.png',dpi=150)
    plt.close(fig)
    print_only = project.with_name(project.stem+'-print-only.gcode.3mf')
    save(folder/'packaging.json',package(archive,print_only))
    print(json.dumps({k:v for k,v in result.items() if k not in ('critical_rim_traces','material_commands')},indent=2))


if __name__ == '__main__':
    main()
