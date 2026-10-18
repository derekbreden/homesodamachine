"""One-off review of emitted receiver walls, support, travel and bead stack."""
from collections import defaultdict,Counter
import hashlib,json,math,re,sys,zipfile
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString,Point
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_printer.py').is_file())
sys.path.insert(0,str(ROOT/'tools/gcode'))
from toolpaths import arc,read_runs
from prepare import POSES,STEM,SOURCE,RECIPE,RECIPE_DIR
WORD=re.compile(r'([A-Z])([-+]?(?:\d*\.\d+|\d+\.?\d*))')
SUPPORT=('Support','Support interface')
MODEL=('Outer wall','Inner wall','Overhang wall','Gap infill','Top surface','Internal solid infill','Sparse infill','Bottom surface')


def bore(z):
    return (4.5-1.45*z if z<1 else 3.05 if z<7 else 3.4 if z<8 else 2.15 if z<9 else 3.05)


def shape(paths):
    return unary_union([LineString(r['pts']).buffer(r['width']/2,quad_segs=3)
                        for r in paths if len(r['pts'])>1])


def normalized(value):
    if isinstance(value,list):return [normalized(x) for x in value]
    if isinstance(value,str):
        try:return float(value)
        except ValueError:return value
    return value


def bind_sources(prepared,native,report):
    readback=json.loads((HERE/'native-readback.json').read_text())
    keys=('machine_start_gcode','machine_end_gcode','filament_map','filament_nozzle_map',
          'nozzle_diameter','nozzle_temperature','nozzle_temperature_initial_layer',
          'eng_plate_temp','eng_plate_temp_initial_layer','filament_flow_ratio',
          'filament_max_volumetric_speed','filament_density','layer_height',
          'initial_layer_print_height','wall_loops','top_one_wall_type','seam_gap',
          'wall_sequence','sparse_infill_density','sparse_infill_pattern','enable_support',
          'support_type','support_style','support_filament','support_interface_filament',
          'support_top_z_distance','support_bottom_z_distance','support_object_xy_distance',
          'time_lapse_gcode','reduce_crossing_wall','seam_position','outer_wall_speed','inner_wall_speed')
    comparisons={k:normalized(prepared.get(k))==normalized(native.get(k)) for k in keys}
    sources=(SOURCE,ROOT/'hardware/printed-parts/enclosure/pump-dock/pump_receiver.py',
             RECIPE,RECIPE_DIR/'physical-result.json',HERE/'prepare.py',Path(__file__),
             HERE/readback['project'],HERE/readback['archive'],HERE/'native-bead-review.png')
    binding=dict(status='Offline native preparation for review; no printer contact or submission',
        source_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        source_stl_matches_preparation=hashlib.sha256(SOURCE.read_bytes()).hexdigest()==readback['source_geometry_sha256'],
        gcode_sha256=readback['gcode_sha256'],critical_native_settings_preserved=comparisons,
        all_critical_native_settings_preserved=all(comparisons.values()),
        native_gcode_checksum_valid=readback['gcode_md5_matches'],
        support_access=dict(native_top_interface_z_mm=report['support_interface_heights_mm'],
            nominal_rear_flange_underside_z_mm=10.35,
            last_interface_top_to_nominal_underside_gap_mm=10.35-max(report['support_interface_heights_mm']),
            keeper_groove_axial_opening_mm=3.35,
            route='External six-branch trees and annular interface; segment the exterior interface and peel radially before wall assembly. No support occupies the fluid passage.',
            physical_release_result=None),physical_acceptance=None)
    (HERE/'source-bindings.json').write_text(json.dumps(binding,indent=2)+'\n')


def main():
    source=HERE/(STEM+'.gcode.3mf')
    with zipfile.ZipFile(source) as z:
        gcode=z.read('Metadata/plate_1.gcode')
        text=gcode.decode()
        native=json.loads(z.read('Metadata/project_settings.config'))
    with zipfile.ZipFile(HERE/(STEM+'.3mf')) as z:
        prepared=json.loads(z.read('Metadata/project_settings.config'))

    # Retain exact native width and modal feed while splitting at travels,
    # extrusion changes, layer/object changes and width changes.
    pos=np.zeros(3);absolute=True;rel_e=True;e_abs=0.;feed=0.
    layer=0;zheight=0.;height=0.;feature='';obj=None;width=.62
    paths=[];run=None;travel=None;travels=[];last=None
    def finish():
        nonlocal run
        if run and len(run['pts'])>1:paths.append(run)
        run=None
    for n,raw in enumerate(text.splitlines(),1):
        if raw.startswith(';'):
            s=raw[1:].strip()
            if s.startswith('Z_HEIGHT:'):
                finish();zheight=float(s.split(':',1)[1])
            elif s.startswith('LAYER_HEIGHT:'):
                height=float(s.split(':',1)[1])
            elif s.startswith('layer num/total_layer_count:'):
                finish();layer=int(s.split(':')[1].split('/')[0])
            elif s.startswith('FEATURE:'):
                finish();feature=s.split(':',1)[1].strip()
            elif s.startswith('LINE_WIDTH:'):
                val=float(s.split(':',1)[1])
                if abs(val-width)>1e-6:finish();width=val
            elif s.startswith('OBJECT_ID:'):
                finish();obj=int(s.split(':')[1])
            elif s.startswith('start printing object, unique label id:'):
                finish();obj=int(s.rsplit(':',1)[1])
            elif s.startswith('stop printing object'):
                finish();obj=None
            continue
        code=raw.split(';',1)[0].strip()
        if not code:continue
        cmd=code.split()[0]
        if cmd in ('G90','G91'):absolute=cmd=='G90';continue
        if cmd in ('M82','M83'):rel_e=cmd=='M83';continue
        if cmd not in ('G0','G1','G2','G3','G92'):continue
        w={k:float(v) for k,v in WORD.findall(code[len(cmd):])}
        if cmd=='G92':
            for idx,key in enumerate('XYZ'):
                if key in w:pos[idx]=w[key]
            e_abs=w.get('E',e_abs);continue
        if 'F' in w:feed=w['F']/60
        nxt=pos.copy()
        for idx,key in enumerate('XYZ'):
            if key in w:nxt[idx]=w[key] if absolute else nxt[idx]+w[key]
        de=(w['E'] if rel_e else w['E']-e_abs) if 'E' in w else None
        if 'E' in w:e_abs=e_abs+w['E'] if rel_e else w['E']
        moved=np.linalg.norm(nxt[:2]-pos[:2])>1e-8 or cmd in ('G2','G3')
        pts=arc(pos,nxt,w,cmd=='G2',chord=.08) if cmd in ('G2','G3') else [tuple(nxt)]
        if layer and moved and de is not None and de>=0 and feature!='Custom':
            if travel is not None and last is not None:
                travel.update(to_layer=layer,to_object=obj)
                travels.append(travel);travel=None
            if run is None:
                run=dict(layer=layer,object=obj,feature=feature,width=width,
                         z=zheight,height=height,pts=[tuple(pos)],feeds=[],line=n)
            run['pts'].extend(pts);run['feeds'].extend([feed]*len(pts))
            last=dict(layer=layer,object=obj)
        else:
            if moved or de is not None and de<0:finish()
            if layer and last is not None:
                if travel is None:travel=dict(from_layer=last['layer'],from_object=last['object'],pts=[tuple(pos)])
                if moved:travel['pts'].extend(pts)
        pos=nxt
    finish()
    by=defaultdict(list);by_obj=defaultdict(list);by_feature=defaultdict(list)
    for r in paths:
        by[(r['layer'],r['object'])].append(r)
        by_obj[r['object']].append(r)
        by_feature[r['feature']].append(r)
    ids=sorted(o for o in by_obj if o is not None)
    centres=dict(zip((2301,2302,2303,2304),POSES))
    print('PARSED',len(paths),'width-specific paths; object IDs',ids,flush=True)
    # A conservative convex projection is inexpensive even when the same wall
    # repeats on 124 layers. First-layer distances below retain the actual
    # disconnected support/brim paths rather than filling their convex hulls.
    footprint={}
    first_footprint={}
    for obj_id,rs in by_obj.items():
        if obj_id is None:continue
        pts=np.concatenate([np.array(r['pts'])[:,:2] for r in rs])
        from shapely.geometry import MultiPoint
        footprint[obj_id]=MultiPoint(pts).convex_hull.buffer(max(r['width'] for r in rs)/2+.001,quad_segs=8)
        first_footprint[obj_id]=shape(by[(1,obj_id)])
    all_beads=unary_union(list(footprint.values()))
    lowx,lowy,highx,highy=all_beads.bounds
    margins=[lowx-25,lowy,330-highx,320-highy]
    separations=[]
    for i,a in enumerate(ids):
        for b in ids[i+1:]:
            separations.append(dict(objects=[a,b],all_height_convex_projection_distance_lower_bound_mm=footprint[a].distance(footprint[b]),
                                    first_layer_actual_bead_distance_mm=first_footprint[a].distance(first_footprint[b]),
                                    first_layer_actual_bead_overlap_mm2=first_footprint[a].intersection(first_footprint[b]).area))
    print('BEAD_PROJECTIONS',json.dumps(separations),flush=True)
    min_support_clear=1e9;support_bore_hits=[]
    support_per_layer=defaultdict(list)
    for feat in SUPPORT:
        for r in by_feature[feat]:
            line=LineString(np.array(r['pts'])[:,:2])
            rz=bore(max(0,r['z']-r['height']/2))
            for idx,(cx,cy) in centres.items():
                gap=line.distance(Point(cx,cy))-r['width']/2-rz
                min_support_clear=min(min_support_clear,gap)
                if gap<0:support_bore_hits.append(dict(layer=r['layer'],object=r['object'],bore=idx,clearance_mm=gap))
            support_per_layer[r['layer']].append(r)

    layer_data=[];stack=[]
    for idx in ids:
        first=shape([r for r in by[(1,idx)] if r['feature'] in MODEL])
        second_paths=[r for r in by[(2,idx)] if r['feature'] in MODEL]
        second=shape(second_paths)
        centrelines=unary_union([LineString(np.array(r['pts'])[:,:2]) for r in second_paths])
        stack.append(dict(object=idx,first_layer_model_area_mm2=first.area,
                          second_layer_bead_area_mm2=second.area,
                          second_layer_area_on_first_fraction=second.intersection(first).area/second.area,
                          second_layer_centerline_outside_first_mm=centrelines.difference(first).length,
                          second_layer_centerline_max_distance_mm=max((Point(p).distance(first) for r in second_paths for p in np.array(r['pts'])[:,:2]),default=0)))
    # Count continuous native circumferential paths rather than assuming the
    # requested wall count equals the roads that fit inside each annulus.
    wall_runs=read_runs(text,features=('Outer wall','Inner wall','Overhang wall'))
    for idx in ids:
        cx,cy=centres[idx]
        for layer_no in sorted({r['layer'] for r in by_obj[idx]}):
            selected=[r for r in wall_runs if r['object']==idx and r['layer']==layer_no-1]
            closed=[]
            for r in selected:
                pts=r['pts'][:,:2]-np.array([cx,cy])
                theta=np.unwrap(np.arctan2(pts[:,1],pts[:,0]))
                sweep=abs(theta[-1]-theta[0])
                if sweep>=2*math.pi-.04:
                    closed.append(dict(mean_radius_mm=float(np.linalg.norm(pts,axis=1).mean()),
                                       end_gap_mm=float(np.linalg.norm(pts[-1]-pts[0])),
                                       angular_sweep_degrees=math.degrees(sweep)))
            sample=by[(layer_no,idx)][0]
            current=[r for r in by[(layer_no,idx)] if r['feature'] in ('Outer wall','Inner wall','Overhang wall')]
            ray_counts=[]
            for angle in (0,math.pi/2,math.pi,3*math.pi/2):
                radii=[]
                ca,sa=math.cos(angle),math.sin(angle)
                for r in current:
                    p=np.array(r['pts'])[:,:2]-np.array([cx,cy])
                    xx=p[:,0]*ca+p[:,1]*sa;yy=-p[:,0]*sa+p[:,1]*ca
                    mask=((yy[:-1]<=0)&(yy[1:]>0))|((yy[:-1]>0)&(yy[1:]<=0))
                    for j in np.flatnonzero(mask):
                        t=-yy[j]/(yy[j+1]-yy[j]);rr=xx[j]+t*(xx[j+1]-xx[j])
                        if rr>0:radii.append(float(rr))
                unique=[]
                for rr in sorted(radii):
                    if not unique or rr-unique[-1]>.15:unique.append(rr)
                ray_counts.append(len(unique))
            layer_data.append(dict(object=idx,layer=layer_no,z_mm=sample['z'],
                                   full_circumferential_wall_paths=len(closed),
                                   radial_ray_wall_roads=ray_counts,
                                   radii_mm=sorted(r['mean_radius_mm'] for r in closed),
                                   maximum_loop_end_gap_mm=max((r['end_gap_mm'] for r in closed),default=None)))
    print('WALL_ROADS_COMPLETE',len(layer_data),'layer/object samples',flush=True)
    layer_zmid={r['layer']:r['z']-r['height']/2 for r in paths}
    travel_counts=defaultdict(lambda:dict(travels=0,bore_crossing_travels=0,bore_crossing_length_mm=0.))
    for t in travels:
        if len(t['pts'])<2:continue
        kind=('within_object' if t['from_layer']==t['to_layer'] and t['from_object']==t['to_object'] else
              'between_objects_same_layer' if t['from_layer']==t['to_layer'] else 'next_layer')
        line=LineString(np.array(t['pts'])[:,:2]);length=0.
        # Both endpoints' current layer cavities are included conservatively.
        zmid=layer_zmid.get(t['to_layer'],0)
        radius=bore(max(0,zmid))
        for cx,cy in centres.values():length+=line.intersection(Point(cx,cy).buffer(radius,quad_segs=48)).length
        row=travel_counts[kind];row['travels']+=1
        if length>.3:row['bore_crossing_travels']+=1;row['bore_crossing_length_mm']+=length

    def selected(zlo,zhi):
        return [r for r in layer_data if zlo<r['z_mm']<=zhi]
    lands={}
    for label,zlo,zhi in (('front_seal',1.,7.),('rear_seal',9.,15.)):
        rs=selected(zlo,zhi)
        lands[label]=dict(layer_object_samples=len(rs),
                         full_circumferential_runs_range=[min(r['full_circumferential_wall_paths'] for r in rs),max(r['full_circumferential_wall_paths'] for r in rs)],
                         radial_ray_wall_roads_range=[min(n for r in rs for n in r['radial_ray_wall_roads']),max(n for r in rs for n in r['radial_ray_wall_roads'])],
                         maximum_loop_end_gap_mm=max(r['maximum_loop_end_gap_mm'] or 0 for r in rs))
    settings_diff={k:dict(prepared=prepared.get(k),emitted=native.get(k)) for k in prepared.keys()|native.keys()
                   if prepared.get(k)!=native.get(k)}
    temperatures=sorted(set(re.findall(r'^M(?:104|109) [^\n]*S(\d+)',text,re.M)))
    speeds={feat:[min(v for r in rs for v in r['feeds']),max(v for r in rs for v in r['feeds'])]
            for feat,rs in by_feature.items() if rs}
    report=dict(status='Native slice reviewed offline; no physical receiver acceptance',
        project_sha256=hashlib.sha256((HERE/(STEM+'.3mf')).read_bytes()).hexdigest(),
        archive_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),gcode_sha256=hashlib.sha256(gcode).hexdigest(),
        layers=max(r['layer'] for r in paths),normal_object_ids=ids,
        feature_path_counts={k:len(v) for k,v in by_feature.items()},
        conservative_model_support_brim_bead_envelope_xy_mm=[[lowx,lowy],[highx,highy]],
        bead_envelope_method='Convex projection of every emitted path per object, expanded by its largest native bead radius and 0.001 mm arc allowance; bounds/insets are conservative',
        usable_bed_insets_mm=dict(left=margins[0],front=margins[1],right=margins[2],back=margins[3]),
        minimum_bed_inset_mm=min(margins),object_bead_separations=separations,
        minimum_support_bead_to_current_wet_bore_mm=min_support_clear,support_bead_wet_bore_hits=support_bore_hits,
        support_layer_range=[min(support_per_layer),max(support_per_layer)],
        support_height_range_mm=[min(r['z'] for feat in SUPPORT for r in by_feature[feat]),max(r['z'] for feat in SUPPORT for r in by_feature[feat])],
        support_interface_heights_mm=sorted(set(r['z'] for r in by_feature['Support interface'])),
        first_two_layer_bead_stack=stack,seal_wall_paths=lands,
        wall_path_layers=layer_data,bore_travels=dict(travel_counts),
        emitted_photo_trip_commands=text.count('M9711'),
        plate_z_trim_commands_mm=[float(x) for x in re.findall(r'^G29\.1 Z([-+.\d]+)',text,re.M)],
        emitted_feature_speed_ranges_mm_s=speeds,native_settings_normalization=settings_diff,
        scope='Commanded paths and bead envelopes only; support release, internal strands, dimensions, sealing and lifetime require the physical article.')
    (HERE/'native-slice-review.json').write_text(json.dumps(report,indent=2)+'\n')

    fig,axes=plt.subplots(1,3,figsize=(15,5))
    colors={'Support':'#a9acb2','Support interface':'#e09f3e','Brim':'#b9dfe4',
            'Outer wall':'#006d77','Inner wall':'#83c5be','Overhang wall':'#e29578',
            'Gap infill':'#bc6c25','Top surface':'#386641'}
    plots=[(axes[0],1,2301,'Layer 1: lip, brim and tree feet'),
           (axes[1],2,2301,'Layer 2: bead overlap'),
           (axes[2],None,2301,'Exterior support projection')]
    for ax,lay,idx,title in plots:
        cx,cy=centres[idx]
        rs=[r for r in by_obj[idx] if (r['layer']==lay if lay is not None else r['feature'] in SUPPORT)]
        for r in rs:
            pts=np.array(r['pts']);ax.plot(pts[:,0]-cx,pts[:,1]-cy,color=colors.get(r['feature'],'#c8ccd0'),lw=.55)
        if lay==2:
            for r in by[(1,idx)]:
                if r['feature'] in MODEL:
                    pts=np.array(r['pts']);ax.plot(pts[:,0]-cx,pts[:,1]-cy,color='#edc9af',alpha=.35,lw=2.5,zorder=0)
        for rad in (3.05,5.85,8.75):ax.add_patch(plt.Circle((0,0),rad,fill=False,color='#333',alpha=.25,lw=.6))
        ax.set_aspect('equal');ax.set_title(title);ax.set_xlabel('mm from bore axis');ax.grid(alpha=.15)
    fig.tight_layout();fig.savefig(HERE/'native-bead-review.png',dpi=180);plt.close(fig)
    bind_sources(prepared,native,report)
    print(json.dumps({k:report[k] for k in ('layers','minimum_bed_inset_mm','object_bead_separations',
          'minimum_support_bead_to_current_wet_bore_mm','support_bead_wet_bore_hits',
          'support_height_range_mm','first_two_layer_bead_stack','seal_wall_paths','bore_travels')},indent=2),flush=True)


if __name__=='__main__':
    main()
