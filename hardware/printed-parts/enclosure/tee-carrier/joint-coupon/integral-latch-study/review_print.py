"""Measure the integral wall, open relief and lip in the actual native toolpaths."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from shapely.geometry import LineString,box
from shapely.ops import unary_union
from prepare_print import HERE,ROOT,JOB,JOB_NAME,single_object_segments


def spans(shape,axis):
    if shape.is_empty:return []
    pieces=[shape] if shape.geom_type=='LineString' else list(shape.geoms)
    return sorted((p.bounds[axis],p.bounds[axis+2]) for p in pieces if p.geom_type=='LineString')


def main():
    readiness=json.loads((HERE/'print-readiness.json').read_text())
    report=json.loads((JOB/(JOB_NAME+'-input.print.json')).read_text())
    row,=report['parts']
    gcode=JOB/'ready/plate_1.gcode'
    assert hashlib.sha256(gcode.read_bytes()).hexdigest()==readiness['gcode_sha256']
    rotation=np.array(row['build_transform'][:9]).reshape(3,3).T
    paths=[];layers=defaultdict(list)
    for segment in single_object_segments(gcode,row['identify_id']):
        placed=np.array([segment['a'],segment['b']])
        local=((placed-np.array(row['plate_translation_mm']))@rotation+np.array(row['source_center_mm']))
        item={**segment,'local':local.tolist()}
        paths.append(item);layers[segment['layer']].append(item)
    errors=[];wall_readings=[];side_readings=[];slot_readings=[];lip_readings=[]
    support_in_relief=[];model_roads={};support_roads={}
    for layer,segments in sorted(layers.items()):
        model=[s for s in segments if not s['feature'].startswith('Support') and s['feature'] not in ('','Custom','Brim')]
        supports=[s for s in segments if s['feature'].startswith('Support')]
        roads=unary_union([LineString(np.array(s['local'])[:,:2]).buffer(s['width']/2) for s in model])
        supp=unary_union([LineString(np.array(s['local'])[:,:2]).buffer(s['width']/2) for s in supports])
        model_roads[layer]=roads;support_roads[layer]=supp
        # Print coordinates are the native receiver rotated 180 degrees about X:
        # Xp=X+2.65, Yp=6-Y, Zp=52.82-Z. Probe outside both key openings.
        if 7.0<=layer<=41.5:
            for x in (10.,12.):
                pieces=spans(roads.intersection(LineString(((x,-1),(x,7)))),1)
                wall=next(((lo,hi) for lo,hi in pieces if lo<=1.2<=hi),None)
                fixed=next(((lo,hi) for lo,hi in pieces if lo<=3.0<=hi),None)
                if wall is None or fixed is None:
                    errors.append(f'wall or fixed receiver absent at Z{layer:g}, X{x:g}');continue
                width,gap=wall[1]-wall[0],fixed[0]-wall[1]
                wall_readings.append({'layer_z_mm':layer,'probe_x_mm':x,'wall_road_width_mm':width,
                    'wall_road_bounds_y_mm':list(wall),'open_fore_gap_mm':gap})
                if width<1.20 or gap<.50:errors.append(f'wall/gap below allowance at Z{layer:g}, X{x:g}: {width:.3f}/{gap:.3f}')
            pieces=spans(roads.intersection(LineString(((-1,1.2),(29,1.2)))),0)
            wall_right=next(((lo,hi) for lo,hi in pieces if lo<=12.0<=hi),None)
            fixed_right=next(((lo,hi) for lo,hi in pieces if lo<=14.0<=hi),None)
            if wall_right is None or fixed_right is None:
                errors.append(f'right wall edge or fixed stock absent at Z{layer:g}')
            else:
                gap=fixed_right[0]-wall_right[1]
                side_readings.append({'layer_z_mm':layer,'right_edge_open_gap_mm':gap})
                if gap<.20:errors.append(f'wall edge gap is {gap:.3f} at Z{layer:g}')
            # The long hidden 0.6 mm relief must not acquire a support sheet.
            # Key-window areas are excluded: those supports have an open lane.
            hidden=box(.51,1.86,13.49,2.44)
            native_z=52.82-layer
            if any(abs(native_z-centre)<=7.4 for centre in (9.,37.93)):
                hidden=hidden.difference(box(.70,1.86,9.85,2.44))
            area=supp.intersection(hidden).area
            support_in_relief.append({'layer_z_mm':layer,'area_mm2':area})
            if area>1e-5:errors.append(f'support occupies the hidden wall relief at Z{layer:g}')
        if 31.4<=layer<=34.5:
            pieces=spans(roads.intersection(LineString(((-1,1.2),(15,1.2)))),0)
            a=next(((lo,hi) for lo,hi in pieces if lo<=1.5<=hi),None)
            b=next(((lo,hi) for lo,hi in pieces if lo<=5.0<=hi),None)
            if a is None or b is None:errors.append(f'release slot edges absent at Z{layer:g}')
            else:
                gap=b[0]-a[1];slot_readings.append({'layer_z_mm':layer,'open_slot_width_mm':gap})
                if gap<2.6:errors.append(f'release slot narrows to {gap:.3f} at Z{layer:g}')
        if 37.1<=layer<=39.9:
            pieces=spans(roads.intersection(LineString(((8.15,-1),(8.15,6.1)))),1)
            material=next(((lo,hi) for lo,hi in pieces if lo<=2.8<=hi),None)
            if material is None:errors.append(f'retaining lip absent at Z{layer:g}')
            else:
                engagement=material[1]-2.0
                lip_readings.append({'layer_z_mm':layer,'lip_road_fore_y_mm':material[1],
                    'engagement_past_key_aft_plane_mm':engagement})
                if engagement<1.10:errors.append(f'lip engagement is {engagement:.3f} at Z{layer:g}')
    if len(lip_readings)<11:errors.append('lip does not persist across eleven complete interior layers')
    if len(wall_readings)<280:errors.append('wall readings do not cover the long flexure')
    if len(slot_readings)<12:errors.append('slot readings do not cover the release opening')
    layer_number=0;nozzle_c=bed_c=None;temperatures={}
    for raw in gcode.read_text().splitlines():
        line=raw.strip()
        if line=='; CHANGE_LAYER':layer_number+=1
        code=line.split(';',1)[0].strip()
        if not code:continue
        command=code.split()[0]
        fields={k:float(v) for k,v in re.findall(r'([XYZESD])([-+0-9.]+)',code)}
        if command in ('M104','M109') and 'S' in fields:nozzle_c=fields['S']
        if command in ('M140','M190'):bed_c=fields.get('S',fields.get('D',bed_c))
        if layer_number and command in ('G0','G1') and fields.get('E',0.)>0 and ('X' in fields or 'Y' in fields):
            temperatures.setdefault(layer_number,(nozzle_c,bed_c))
    if temperatures.get(1)!=(265.,80.):errors.append('first-layer temperatures differ from retained profile')
    if any(t!=(280.,80.) for n,t in temperatures.items() if n>1):errors.append('subsequent temperatures differ from retained profile')
    if len(temperatures)!=readiness['layers']:errors.append('temperature readings do not cover every layer')
    messages=[line.split('[error]',1)[1].strip() for line in (JOB/'ready/bambu-cli.log').read_text().splitlines() if '[error]' in line]
    expected={'Invalid T command (T1001).','Invalid T command (T65535).','Invalid T command (T65279).'}
    if set(messages)-expected:errors.append('native slicer emitted a new diagnostic')
    support=json.loads((JOB/(JOB_NAME+'-input.support-audit.json')).read_text())
    part,=support['parts']
    lanes={'key_pockets':'Square receiving shoulders retain the proven key fit. Supports leave the open entry windows before assembly; the long wall must not have a hidden support sheet.',
        'retaining_lip':'The square 1.2 mm retaining lip projects into the open lower key-entry window. Separate its exposed support branch and remove it through the fore opening.',
        'release_slot':'The slot opens directly through the exposed rear wall and has a straight rear removal lane for any roof support.',
        'physical_scope':'Emitted support topology and open lanes are measured here. Actual release effort, surface finish and wall spring force require the coupon.'}
    fig,axes=plt.subplots(1,3,figsize=(15,6),constrained_layout=True)
    ax=axes[0]
    for support_flag,color,width in ((False,'#526272',.35),(True,'#D97706',.75)):
        lines=[np.array(s['local'])[:,[1,2]] for s in paths
               if s['feature'].startswith('Support')==support_flag and s['feature'] not in ('','Custom','Brim')]
        ax.add_collection(LineCollection(lines,colors=color,linewidths=width,alpha=.6,rasterized=True))
    ax.autoscale();ax.set_aspect('equal');ax.set_title('Actual receiver / support paths')
    ax.set_xlabel('Print Y (mm)');ax.set_ylabel('Print Z (mm)')
    for ax,target,title in zip(axes[1:],(25.,38.),('Broad wall and open relief','Square retaining lip')):
        selected=min(model_roads,key=lambda z:abs(z-target))
        for s in layers[selected]:
            if s['feature'] in ('','Custom','Brim'):continue
            pts=np.array(s['local'])[:,:2]
            ax.plot(pts[:,0],pts[:,1],color='#D97706' if s['feature'].startswith('Support') else '#087E8B',
                linewidth=max(.4,s['width']*2))
        ax.set_aspect('equal');ax.set_xlim(-.5,15);ax.set_ylim(-.2,6.5)
        ax.set_title(f'{title}\nActual layer Z={selected:g} mm');ax.set_xlabel('Print X (mm)');ax.set_ylabel('Print Y (mm)')
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('Two-piece integral latch: native extrusion paths · orange is support',fontsize=13)
    fig.savefig(HERE/'toolpath-review.svg',dpi=150)
    svg=HERE/'toolpath-review.svg';svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(JOB/'toolpath-review.png',dpi=150);plt.close(fig)
    result={'status':'pass' if not errors else 'fail','errors':errors,'gcode_sha256':readiness['gcode_sha256'],
        'method':'Actual native extrusion segments buffered by half commanded line width in each layer; no shrinkage, sag, adhesion, force or strength is simulated.',
        'wall':wall_readings,'side_gap':side_readings,'release_slot':slot_readings,'retaining_lip':lip_readings,
        'hidden_relief_support':support_in_relief,
        'minimum_wall_road_width_mm':min((r['wall_road_width_mm'] for r in wall_readings),default=None),
        'minimum_fore_open_gap_mm':min((r['open_fore_gap_mm'] for r in wall_readings),default=None),
        'minimum_side_open_gap_mm':min((r['right_edge_open_gap_mm'] for r in side_readings),default=None),
        'minimum_release_slot_width_mm':min((r['open_slot_width_mm'] for r in slot_readings),default=None),
        'minimum_lip_engagement_mm':min((r['engagement_past_key_aft_plane_mm'] for r in lip_readings),default=None),
        'actual_model_nozzle_bed_c':{'first_layer':temperatures.get(1),'subsequent_layers':[280.,80.],'layers_read':len(temperatures)},
        'support_lanes':lanes,'support_summary':part['summary'],'support_trees':part['trees'],'support_interfaces':part['interfaces'],
        'native_stock_template_parser_diagnostics':messages,
        'diagnostic_scope':'The retained successful PET-GF jobs contain these same three H2C template diagnostics; the native slice reports Success with no geometry warning. No command is removed.',
        'physical_status':'Integral receiver unprinted; automatic engagement, retention, release and fatigue remain unqualified.'}
    output=HERE/'toolpath-review.json';output.write_text(json.dumps(result,indent=2)+'\n')
    readiness['status']='integral_coupon_toolpath_review_failed' if errors else 'ready_for_integral_coupon_trial'
    readiness['toolpath_review']=str(output.relative_to(ROOT))
    readiness['toolpath_review_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
    (HERE/'print-readiness.json').write_text(json.dumps(readiness,indent=2)+'\n')
    (JOB/'readiness.json').write_text(json.dumps(readiness,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ('status','errors') or k.startswith('minimum_')},indent=2))
    return int(bool(errors))


if __name__=='__main__':
    raise SystemExit(main())
