#!/usr/bin/env python3
"""Inspect emitted cartridge/cap roads and name each actual support removal lane."""
from collections import defaultdict
import json
from pathlib import Path
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import trimesh
from shapely.geometry import LineString, box as rectangle
from shapely.ops import unary_union

from prepare_pump_print import HERE, ROOT, JOB, JOB_NAME, GEOMETRY, sha
from prepare_display_print import extrusion_segments


def main():
    readiness = json.loads((HERE/'pump-print-readiness.json').read_text())
    source_before = sha(Path(__file__))
    readiness['status'] = 'native_slice_complete_toolpath_and_support_access_review_pending'
    (HERE/'pump-print-readiness.json').write_text(json.dumps(readiness,indent=2)+'\n')
    (JOB/'readiness.json').write_text(json.dumps(readiness,indent=2)+'\n')
    geometry = json.loads(GEOMETRY.read_text())
    assert sha(GEOMETRY) == readiness['geometry_manifest_sha256']
    for group in ('source_sha256','input_sha256','artifact_sha256'):
        for path,digest in geometry[group].items():
            assert sha(ROOT/path) == digest, path
    report = json.loads((JOB/(JOB_NAME+'-input.print.json')).read_text())
    support = json.loads((JOB/(JOB_NAME+'-input.support-audit.json')).read_text())
    gcode = JOB/'ready/plate_1.gcode'
    assert sha(gcode) == readiness['gcode_sha256']
    assert sha(ROOT/readiness['native_archive']) == readiness['native_archive_sha256']
    parts = {p['identify_id']:p for p in report['parts']}
    rails = geometry['native']['cap_rails']
    rail_z = rails[0]['z_mm']
    support_paths = defaultdict(list)
    cap_layers = defaultdict(list)
    first_layers = defaultdict(list)
    model_counts = defaultdict(int)
    for segment in extrusion_segments(gcode):
        row = parts.get(segment['object'])
        if row is None or segment['feature'] in ('','Custom','Brim'):
            continue
        rotation = np.array(row['build_transform'][:9]).reshape(3,3).T
        local = ((np.array([segment['a'],segment['b']])-row['plate_translation_mm'])@rotation
                 +row['source_center_mm'])
        item = {'local':local,'width':segment['width'],'feature':segment['feature']}
        if segment['feature'].startswith('Support'):
            support_paths[row['name']].append(item)
        else:
            model_counts[row['name']] += 1
            if segment['layer'] <= report['layer_height_mm']+1e-5:
                first_layers[row['name']].append(item)
            if row['name'] == 'enclosure-pump-cap' and rail_z-.3 <= local[:,2].mean() <= rail_z+2.3:
                cap_layers[segment['layer']].append(item)
    errors = []
    for row in parts.values():
        expected = 0. if row['name'].endswith('cartridge') else 180.
        if row['rotation_x_degrees'] != expected:
            errors.append(f'{row["name"]}: unexpected print orientation')
        if not model_counts[row['name']] or not first_layers[row['name']]:
            errors.append(f'{row["name"]}: missing model or first-layer roads')
    rail_readings = []
    model_roads = {}
    # Probe complete layers just behind the four terminal bearing surfaces. The
    # test reads commanded road widths; it does not simulate sag or shrinkage.
    for layer,segments in sorted(cap_layers.items()):
        z = float(np.mean([s['local'][:,2].mean() for s in segments]))
        roads = unary_union([LineString(s['local'][:,:2]).buffer(s['width']/2)
                             for s in segments])
        model_roads[layer] = roads
        if not rail_z+.05 <= z <= rail_z+1.0:
            continue
        for index,rail in enumerate(rails):
            (x0,y0),(x1,y1) = rail['bounds_xy_mm']
            footprint = rectangle(x0,y0,x1,y1)
            area = roads.intersection(footprint).area
            widths = []
            for y in (y0+4,(y0+y1)/2,y1-4):
                hit = roads.intersection(LineString(((x0-.2,y),(x1+.2,y))))
                widths.append(hit.length)
            rail_readings.append({'rail':index+1,'native_layer_z_mm':z,
                                  'print_layer_z_mm':layer,'covered_area_mm2':area,
                                  'three_cross_section_road_widths_mm':widths})
            if area < 90. or min(widths) < 2.8:
                errors.append(f'Rail {index+1} bearing roads incomplete at native Z{z:g}')
    if len(rail_readings) < 12:
        errors.append('Fewer than three complete layer readings per bearing rail')

    # Every actual tree is associated with the working face it supports. Pocket
    # mouths and counterbores are empty during support removal, before hardware.
    lanes = []
    features = geometry['native']['support_features']
    contact_checks = []
    for part in support['parts']:
        interfaces = {row['id']:row for row in part['interfaces']}
        for tree in part['trees']:
            bounds = tree.get('bbox_cad_xyz_mm')
            if not bounds:
                errors.append('Support lacks native coordinates')
                continue
            if part['piece'] == 'enclosure-pump-cartridge':
                side = 'right' if bounds[0] > 0 else 'left'
                lane = f'{side} pull pocket; pull toward {"+X" if side=="right" else "−X"} through its open outer mouth before installing pumps'
                reason = 'The flat pull roof is the working hand-contact face.'
                for identifier in tree['interfaces']:
                    b = interfaces[identifier]['bbox_cad_xyz_mm']
                    near_x = min(abs(b[0]),abs(b[3]))
                    far_x = max(abs(b[0]),abs(b[3]))
                    located = (near_x >= features['pull_inner_abs_x_mm']-.5
                               and far_x <= features['pull_outer_abs_x_mm']+.5
                               and b[1] >= features['pull_y_mm'][0]-.5
                               and b[4] <= features['pull_y_mm'][1]+.5
                               and b[2] >= features['pull_z_mm'][0]
                               and b[5] <= features['pull_z_mm'][1]+.5)
                    contact_checks.append({'piece':part['piece'],'interface':identifier,
                                           'in_open_pull_pocket':located})
                    if not located:errors.append(f'{identifier} is outside a declared open pull pocket')
            else:
                lane = 'clamp screw counterbore; pull toward the crown (+Z in the machine frame), through the bed-facing mouth before screws are installed'
                reason = 'The flat annular head seat locates the M3 screw.'
                radius = features['cap_counterbore_radius_mm']+.5
                for identifier in tree['interfaces']:
                    b = interfaces[identifier]['bbox_cad_xyz_mm']
                    cy = min(features['cap_screw_y_mm'],key=lambda y:abs((b[1]+b[4])/2-y))
                    located = (b[0] >= -radius and b[3] <= radius
                               and b[1] >= cy-radius and b[4] <= cy+radius
                               and abs((b[2]+b[5])/2-features['cap_head_seat_z_mm']) <= 1.)
                    contact_checks.append({'piece':part['piece'],'interface':identifier,
                                           'in_open_screw_counterbore':located})
                    if not located:errors.append(f'{identifier} is outside an open screw counterbore')
            if not tree['interfaces']:
                errors.append(f'{part["piece"]} {tree["id"]} has no explicit interface to locate its removal lane')
            lanes.append({'piece':part['piece'],'tree':tree['id'],
                          'root':tree['root'],'shortest_build_up_mm':tree['shortest_build_up_mm'],
                          'native_bounds_mm':bounds,'interfaces':tree['interfaces'],
                          'reason_face_is_retained':reason,'removal_lane':lane})
    # The cap's new rails terminate print-up; none should acquire a support island.
    cap_support = next(p for p in support['parts'] if p['piece']=='enclosure-pump-cap')
    for interface in cap_support['interfaces']:
        bounds = interface['bbox_cad_xyz_mm']
        if bounds[2] <= rail_z+.5 and bounds[5] >= rail_z-.5:
            errors.append('Support interface reaches a new cap bearing rail')

    layer_number=0;nozzle=bed=None;temperatures={}
    for raw in gcode.open():
        line=raw.strip()
        if line=='; CHANGE_LAYER':layer_number+=1
        code=line.split(';',1)[0].strip()
        if not code:continue
        command=code.split()[0]
        fields={k:float(v) for k,v in re.findall(r'([XYZESD])([-+0-9.]+)',code)}
        if command in ('M104','M109') and 'S' in fields:nozzle=fields['S']
        if command in ('M140','M190'):bed=fields.get('S',fields.get('D',bed))
        if layer_number and command in ('G0','G1') and fields.get('E',0)>0 and ('X' in fields or 'Y' in fields):
            temperatures.setdefault(layer_number,(nozzle,bed))
    if temperatures.get(1)!=(265.,80.) or any(t!=(280.,80.) for n,t in temperatures.items() if n>1):
        errors.append('Actual temperature commands differ from retained PET-GF profile')
    if len(temperatures)!=readiness['layers']:
        errors.append('Temperature reading does not cover every layer')
    diagnostics=[line.split('[error]',1)[1].strip() for line in (JOB/'ready/bambu-cli.log').read_text().splitlines() if '[error]' in line]
    known={'Invalid T command (T1001).','Invalid T command (T65535).','Invalid T command (T65279).'}
    if set(diagnostics)-known:errors.append('New native slicer diagnostic')

    fig,axes=plt.subplots(1,3,figsize=(15,4.5),constrained_layout=True)
    for ax,name in zip(axes[:2],('enclosure-pump-cartridge','enclosure-pump-cap')):
        row=next(p for p in parts.values() if p['name']==name)
        mesh=trimesh.load_mesh(ROOT/row['source'])
        section_y=(sum(features['pull_y_mm'])/2 if name.endswith('cartridge')
                   else features['cap_screw_y_mm'][0])
        section=trimesh.intersections.mesh_plane(mesh,plane_origin=(0,section_y,0),
                                                plane_normal=(0,1,0))
        if not len(section):errors.append(f'{name}: native removal-mouth section is empty')
        else:ax.add_collection(LineCollection(section[:,:,[0,2]],colors='#334155',linewidths=.8))
        lines=[s['local'][:,[0,2]] for s in support_paths[name]]
        if lines:ax.add_collection(LineCollection(lines,colors='#d97706',linewidths=.6,alpha=.7,rasterized=True))
        bed_lines=[s['local'][:,[0,2]] for s in first_layers[name]]
        if bed_lines:ax.add_collection(LineCollection(bed_lines,colors='#64748b',linewidths=.3,rasterized=True))
        ax.autoscale();ax.set_aspect('equal');ax.set_title(name.replace('enclosure-','')+' actual support paths')
        ax.set_xlabel('Machine X (mm)');ax.set_ylabel('Machine Z (mm)')
        if name.endswith('cartridge'):
            for sign in (-1,1):
                ax.annotate('',xy=(sign*138,250),xytext=(sign*108,250),
                            arrowprops={'arrowstyle':'->','color':'#b45309','lw':1.6})
        else:
            ax.annotate('',xy=(0,features['cap_crown_z_mm']+8),
                        xytext=(0,features['cap_head_seat_z_mm']+3),
                        arrowprops={'arrowstyle':'->','color':'#b45309','lw':1.6})
            ax.text(7,features['cap_crown_z_mm']+5,'Pull through crown',fontsize=8)
            ax.set_ylim(rail_z-3,features['cap_crown_z_mm']+12)
    ax=axes[2]
    if cap_layers:
        selected=max(layer for layer in cap_layers if layer in model_roads)
        for s in cap_layers[selected]:
            p=s['local'];ax.plot(p[:,0],p[:,1],color='#087e8b',linewidth=max(.3,s['width']*1.5))
        for rail in rails:
            (x0,y0),(x1,y1)=rail['bounds_xy_mm']
            ax.add_patch(plt.Rectangle((x0,y0),x1-x0,y1-y0,fill=False,color='#dc2626',linewidth=1.2))
        ax.set_title(f'Four bearing rails · actual final layer {selected:g} mm')
    ax.set_aspect('equal');ax.set_xlabel('Machine X (mm)');ax.set_ylabel('Machine Y (mm)')
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('Cartridge upright · cap crown-down · orange paths are removable support')
    picture=HERE/'pump-toolpath-review.svg'
    fig.savefig(picture,dpi=140)
    picture.write_text('\n'.join(line.rstrip() for line in picture.read_text().splitlines())+'\n')
    fig.savefig(JOB/'pump-toolpath-review.png',dpi=140);plt.close(fig)
    result={'status':'pass' if not errors else 'fail','errors':errors,
            'gcode_sha256':sha(gcode),'geometry_manifest_sha256':sha(GEOMETRY),
            'review_source_sha256':sha(Path(__file__)),
            'method':'Actual native G-code model roads buffered by half commanded width, per-layer temperatures, native support topology and exposed removal mouths. Physical cleanup effort and bearing finish remain unmeasured.',
            'cap_bearing_rail_roads':rail_readings,
            'minimum_rail_covered_area_mm2':min((r['covered_area_mm2'] for r in rail_readings),default=None),
            'minimum_rail_road_width_mm':min((min(r['three_cross_section_road_widths_mm']) for r in rail_readings),default=None),
            'orientation':{p['name']:p['rotation_x_degrees'] for p in parts.values()},
            'support_lanes':lanes,
            'support_interface_location_checks':contact_checks,
            'support_topology':{p['piece']:{k:p[k] for k in ('summary','trees','interfaces')} for p in support['parts']},
            'actual_nozzle_bed_c':{'first_layer':temperatures.get(1),'subsequent_layers':[280.,80.],'layers':len(temperatures)},
            'native_template_diagnostics':diagnostics,
            'physical_fit_tested':False,'physical_support_removal_tested':False,
            'assembly_current':False,'production_enclosure_released':False}
    assert sha(Path(__file__)) == source_before, 'Review source changed during execution'
    output=HERE/'pump-toolpath-review.json';output.write_text(json.dumps(result,indent=2)+'\n')
    readiness['status']='cartridge_toolpath_review_failed' if errors else 'ready_for_cartridge_and_cap_bench_fit'
    readiness['toolpath_review']=str(output.relative_to(ROOT))
    readiness['toolpath_review_sha256']=sha(output)
    (HERE/'pump-print-readiness.json').write_text(json.dumps(readiness,indent=2)+'\n')
    (JOB/'readiness.json').write_text(json.dumps(readiness,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','errors','minimum_rail_covered_area_mm2','minimum_rail_road_width_mm')},indent=2))
    return int(bool(errors))


if __name__=='__main__':
    raise SystemExit(main())
