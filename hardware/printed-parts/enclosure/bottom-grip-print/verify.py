"""Verify production bottom toolpaths and the two unsupported grip-wing slots."""
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timezone
import argparse, hashlib, json, re, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path.insert(0,str(ROOT/'hardware/scripts'))
from enclosure_support_audit import audit, _WORD
from verify_round_layer_band import wall_layers, check_span

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def roads(path):
    x=y=e=width=height=0.;layer=None;feature='';obj=None
    absolute=relative_e=True
    with path.open() as stream:
        for line in stream:
            if line.startswith('; Z_HEIGHT:'):
                layer=float(line.split(':',1)[1]);feature='';obj=None
            elif line.startswith('; FEATURE:'): feature=line.split(':',1)[1].strip()
            elif line.startswith('; LINE_WIDTH:'): width=float(line.split(':',1)[1])
            elif line.startswith('; LAYER_HEIGHT:'): height=float(line.split(':',1)[1])
            elif line.startswith('; OBJECT_ID:'): obj=int(line.split(':',1)[1]);feature=''
            code=line.split(';',1)[0].strip()
            if not code: continue
            command=code.split()[0];v={k:float(n) for k,n in _WORD.findall(code)}
            if command in ('G90','G91'): absolute=command=='G90'
            elif command in ('M82','M83'): relative_e=command=='M83'
            elif command=='G92': x,y,e=(v.get(k,old) for k,old in zip('XYE',(x,y,e)))
            elif command in ('G0','G1','G2','G3'):
                nx,ny=(v.get(k,old) if absolute else old+v.get(k,0) for k,old in zip('XY',(x,y)))
                de=v.get('E',0) if relative_e else v.get('E',e)-e
                if layer is not None and de>1e-9 and (nx!=x or ny!=y):
                    assert command in ('G0','G1'),'Arc fitting must remain disabled'
                    yield {'a':(x,y),'b':(nx,ny),'width':width,'height':height,'layer':layer,'feature':feature,'object':obj}
                x,y=nx,ny
                if 'E' in v: e=e+v['E'] if relative_e else v['E']

def clip(poly,z,above):
    out=[]
    for a,b in zip(poly,np.roll(poly,-1,axis=0)):
        ia=(a[2]>=z) if above else (a[2]<=z)
        ib=(b[2]>=z) if above else (b[2]<=z)
        if ia:out.append(a)
        if ia!=ib:out.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
    return np.array(out)

def main(printer,revision):
    piece,trim={'H2C':('front',.18),'Mark2':('back',.04)}[printer]
    stem=f'enclosure-{piece}-bottom-grip-bridges-{printer.lower()}-v{revision}'
    job=ROOT/'.cache/prints'/stem;out=HERE/printer.lower();out.mkdir(exist_ok=True)
    prep=json.loads((job/'preparation.json').read_text())
    for name,digest in prep['source_sha256'].items(): assert sha(ROOT/name)==digest,name
    project=job/prep['project'];assert sha(project)==prep['project_sha256']
    assert sha(job/'support-review-geometry.npz')==prep['support_review_geometry_sha256']
    archive=job/'ready'/f'{stem}.gcode.3mf'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        settings=json.loads(z.read('Metadata/project_settings.config'))
        exported_parts=ET.fromstring(z.read('Metadata/model_settings.config')).findall('./object/part')
        assert len(exported_parts)==1 and exported_parts[0].get('subtype')=='normal_part'
        gc=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (out/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
        plate=ET.fromstring(z.read('Metadata/slice_info.config')).find('plate')
        metadata={m.get('key'):m.get('value') for m in plate.findall('metadata')}
        assert metadata['outside']=='false'
        assert {int(o.get('identify_id')):o.get('name') for o in plate.findall('object')}=={1901:f'enclosure-{piece}-bottom'}
        assert [f.get('color') for f in plate.findall('filament')]==['#000000']
        assert [n.get('id') for n in plate.findall('nozzle')]==['0']
    expected={'layer_height':'0.24','initial_layer_print_height':'0.2','wall_loops':'2',
        'enable_support':'1','support_type':'tree(auto)','support_object_xy_distance':'0.4',
        'support_top_z_distance':'0.45','support_bottom_z_distance':'0.3',
        'support_filament':'1','support_interface_filament':'1','flush_into_support':'0',
        'wall_sequence':'inner wall/outer wall','is_infill_first':'0','infill_wall_overlap':'15%',
        'brim_type':'auto_brim','elefant_foot_compensation':'0.15','enable_arc_fitting':'0',
        'filament_colour':['#000000'],'filament_nozzle_map':['0'],'nozzle_diameter':['0.4','0.4']}
    for k,v in expected.items(): assert settings[k]==v,(k,settings[k],v)
    with zipfile.ZipFile(ROOT/'hardware/printed-parts/petgf.3mf') as z: baseline=json.loads(z.read('Metadata/project_settings.config'))
    thermal_speed=[k for k in baseline if any(w in k for w in ('speed','acceleration','temperature','fan'))]
    assert all(settings[k]==baseline[k] for k in thermal_speed)
    with zipfile.ZipFile(project) as z:
        assert hashlib.sha256(z.read('Metadata/project_settings.config')).hexdigest()==prep['settings_sha256']
        ranges=ET.fromstring(z.read('Metadata/layer_config_ranges.xml'))
        native_ranges=[(float(r.get('min_z')),float(r.get('max_z')),{o.get('opt_key'):o.text for o in r}) for r in ranges.findall('./object/range')]
    assert native_ranges==[(35.,41.5,{'layer_height':'0.24','wall_loops':'6'})]
    trims=[float(x) for x in re.findall(rb'^\s*G29\.1 Z([-+\d.]+)',gc,re.M)]
    assert np.allclose(trims,[0.,trim-.02]),trims
    path=job/'ready/plate_1.gcode';path.write_bytes(gc)
    part,=prep['parts'];assert part['rotation_x_degrees']==0 and part['watertight'] and part['body_count']==1
    shift=np.array(part['plate_translation_mm'])-part['source_center_mm']
    slots=[box(*s) for s in prep['slot_bounds_cad_xy_mm']]
    roof=prep['slot_roof_cad_z_mm'];floor=prep['slot_floor_cad_z_mm']
    bounds=np.array([[np.inf,np.inf],[-np.inf,-np.inf]])
    first=[];second=[];roofroads=[];near_support=defaultdict(list);near_model=defaultdict(list);features=defaultdict(int);crossings=defaultdict(list)
    intrusion=[0.,0.];support_count=0
    station_y=(185. if piece=='front' else 235.)+shift[1]
    def bead(r,cad=False,pad=0.):
        delta=shift[:2] if cad else 0.
        return LineString([np.array(r['a'])-delta,np.array(r['b'])-delta]).buffer(r['width']/2+pad)
    for r in roads(path):
        if not r['feature'] or r['feature']=='Custom':continue
        assert r['width']>0,r
        features[r['feature']]+=1
        p=np.array([r['a'],r['b']]);pad=r['width']/2+.05
        bounds[0]=np.minimum(bounds[0],p.min(axis=0)-pad);bounds[1]=np.maximum(bounds[1],p.max(axis=0)+pad)
        z=r['layer']-shift[2]
        if r['feature'].startswith('Support'):
            support_count+=1
            if roof-7<=z<=roof+9.1: near_support[z].append(r)
            if floor+.001<z<roof:
                for i,slot in enumerate(slots):intrusion[i]+=bead(r,True).intersection(slot).area
        elif r['object']==1901:
            if roof-8<=z<=roof+10.5:near_model[z].append(r)
            model_bounds=np.array(part['plate_bounds_mm'])[:,:2]
            assert np.all(p>=model_bounds[0]-.2) and np.all(p<=model_bounds[1]+.2),('extrusion outside source bounds',r)
            if abs(r['layer']-.2)<.001:first.append(r)
            if abs(r['layer']-.44)<.001:second.append(r)
            if roof<z<roof+.30:roofroads.append(r)
            if r['feature'] in ('Inner wall','Outer wall','Overhang wall'):
                x1,y1=r['a'];x2,y2=r['b']
                if min(y1,y2)<=station_y<max(y1,y2):
                    x=x1+(station_y-y1)*(x2-x1)/(y2-y1)-shift[0]
                    if x<-93.5:crossings[r['layer']].append(float(x))
    assert support_count>0
    margin=float(min(*bounds[0],325-bounds[1,0],320-bounds[1,1]));assert margin>0,(margin,bounds)
    roofcheck=[]
    for slot in slots:
        bridge=[r for r in roofroads if r['feature']=='Bridge' and bead(r,True).intersects(slot)]
        assert len(bridge)>=6,len(bridge)
        layer=min(r['layer'] for r in bridge)
        cover=unary_union([bead(r,True) for r in roofroads if abs(r['layer']-layer)<.001])
        fraction=cover.intersection(slot).area/slot.area
        assert fraction>.95,fraction
        roofcheck.append({'bridge_roads':len(bridge),'roof_layer_mm':layer,'coverage_fraction':fraction})
    assert first and second
    firstshape=unary_union([bead(r) for r in first])
    wall_support=[(r,bead(r).intersection(firstshape).area/bead(r).area)
                  for r in second if 'wall' in r['feature'].lower()]
    overlap=min(f for r,f in wall_support)
    reference_foot=None
    if overlap<=.40:
        # The long floor-scarf edge grows outward at layer two. Its inner
        # perimeter prints first. Preserve the established full-bottom path
        # rather than changing the shared elephant-foot setting for it.
        assert printer=='H2C'
        reference=ROOT/'.cache/prints/2026-09-24-enclosure-front-bottom-h2c-v7/ready/plate_1.gcode'
        reference_archive=None
        if reference.exists():
            assert sha(reference)=='55fffac067cb1df96931f5fd8af9e8483a314cf482372d726780c307268091a8'
        else:
            reference_archive=ROOT/'.cache/prints/enclosure-front-bottom-grip-bridges-h2c-v3/ready/enclosure-front-bottom-grip-bridges-h2c-v3.gcode.3mf'
            assert sha(reference_archive)=='f64e85a9c71df200b929f634f0d61f50b4d3d739f0fd5cb900a707ec293ad8cb'
            reference=job/'ready/retained-front-v3-first-layers.gcode'
            with zipfile.ZipFile(reference_archive) as archive_source, archive_source.open('Metadata/plate_1.gcode') as stream, reference.open('wb') as target:
                for raw in stream:
                    if raw.startswith(b'; Z_HEIGHT:') and float(raw.split(b':',1)[1])>.45:break
                    target.write(raw)
        old_first=[];old_second=[]
        for r in roads(reference):
            if r['layer']>.45:break
            if r['object']!=1901 or r['feature'] in ('','Custom'):continue
            if abs(r['layer']-.2)<.001:old_first.append(r)
            if abs(r['layer']-.44)<.001:old_second.append(r)
        old_shape=unary_union([bead(r) for r in old_first])
        low=[r for r,f in wall_support if f<=.40]
        from shapely.affinity import translate
        scarf_rows=[]
        for r in low:
            vector=np.array(r['b'])-r['a']
            candidates=[v for v in old_second if all(v[k]==r[k] for k in ('width','height','layer','feature','object'))
                        and np.allclose(np.array(v['b'])-v['a'],vector,atol=.002,rtol=0)]
            assert candidates,('changed local low-overlap floor-scarf road',r)
            current=bead(r).intersection(firstshape).area/bead(r).area
            matched=None
            for prior in candidates:
                delta=np.array(r['a'])-prior['a']
                aligned=translate(old_shape,xoff=delta[0],yoff=delta[1])
                previous=bead(r).intersection(aligned).area/bead(r).area
                if current>0 and abs(current-previous)<.002:
                    matched=(prior,delta,previous);break
            assert matched is not None,('changed local first-to-second scarf overlap',r,current)
            prior,delta,previous=matched
            earlier=second[:second.index(r)]
            inner=unary_union([bead(q) for q in earlier if q['feature']=='Inner wall'])
            side_bond=bead(r).intersection(inner).area/bead(r).area
            assert side_bond>0,('outer scarf wall lacks preceding inner-wall contact',r)
            scarf_rows.append({'a_mm':r['a'],'b_mm':r['b'],'reference_translation_xy_mm':delta.tolist(),
                               'current_first_layer_overlap_fraction':current,'reference_first_layer_overlap_fraction':previous,
                               'preceding_same_layer_inner_wall_contact_fraction':side_bond})
        reference_foot={'gcode':str(reference.relative_to(ROOT)), 'sha256':sha(reference),
                        'matching_local_floor_scarf_roads':len(low),'local_bead_checks':scarf_rows,
                        'scope':'Same local road vector, width, height and first-layer bead overlap under translation; preceding inner-wall contact is required. This is not whole current mesh parity.'}
        if reference_archive is not None:
            reference_foot.update(retained_archive=str(reference_archive.relative_to(ROOT)),retained_archive_sha256=sha(reference_archive),retained_scope='Local translated floor-scarf bead section; not whole current mesh parity.')
    layers=wall_layers(archive,1901);assert layers[:2]==[(.2,.2),(.44,.24)],layers[:3]
    spans=[check_span(layers,'expanding-grip-transition',35.25,41.25,.24,.001),check_span(layers,'decorative-flute-fade',41.5,44.3,.24,.001)]
    assert all(s['pass'] for s in spans),spans
    samples=[]
    # This station is in the open handhold below its roof; compare the thick
    # transition with the ordinary shell above it, where both have walls.
    # Above 47 mm the fluted outline adds another surface at this section.
    for lo,hi,count in [(37,40,6),(46,47,2)]:
        rows=[(z,len(v)) for z,v in crossings.items() if lo<z<hi]
        assert rows and all(n==count for z,n in rows),(lo,hi,rows)
        samples.append({'print_z_band_mm':[lo,hi],'wall_count':count,'layers_checked':len(rows)})
    print(json.dumps({'printer':printer,'slot_support_intrusion_mm2':intrusion,'slot_roofs':roofcheck,'wall_counts':samples}),flush=True)
    assert max(intrusion)<.001,intrusion
    tri=np.load(job/'support-review-geometry.npz')['exterior_triangles'];low=tri[:,:,2].min(axis=1);high=tri[:,:,2].max(axis=1)
    near_hits=[]
    for z,rr in near_support.items():
        polygons=[]
        for triangle in tri[(high>=z-.00001)&(low<=z+.60)]:
            pp=clip(triangle,z-.00001,True)
            if len(pp)<3:continue
            pp=clip(pp,z+.60,False)
            if len(pp)>=3:
                polygon=Polygon(pp[:,:2])
                if polygon.area>1e-12:polygons.append(polygon)
        region=unary_union(polygons)
        for r in rr:
            overlaparea=region.intersection(bead(r,True,.05)).area
            if overlaparea>1e-8: near_hits.append((z,overlaparea,r))
    # The projected 0.60 mm search slab is a broad-phase proximity check.
    # Passing tree branches can enter it without touching the model. Resolve
    # candidates against actual extrusion widths/heights and verify that they
    # continue upward; interface roads and terminating tips still fail here.
    passing_branches=[]
    for z,area,r in near_hits:
        assert r['feature']=='Support',('interface on excluded curve',z,r)
        shape=bead(r,True)
        next_z=min(q for q in near_support if q>z+.001)
        connected=any(shape.intersects(bead(q,True)) for q in near_support[next_z])
        assert connected,('support tip near excluded curve',z,r)
        search=shape.buffer(1.2);near=[]
        for mz,rr in near_model.items():
            if not z-1.2<mz<z+1.2:continue
            for q in rr:
                # Bounding-box rejection keeps the narrow phase local.
                xy=np.array([q['a'],q['b']])-shift[:2]
                pad=q['width']/2
                if not box(*(xy.min(axis=0)-pad),*(xy.max(axis=0)+pad)).intersects(search):continue
                xy_air=shape.distance(bead(q,True))
                z_air=max(0.,mz-q['height']-z,z-r['height']-mz)
                near.append((float(np.hypot(xy_air,z_air)),float(xy_air),float(z_air),mz))
        assert near,('unresolved branch clearance',z,r)
        distance,xy_air,z_air,model_z=min(near)
        # This is an air gap to a through-going branch, not a support contact
        # interface governed by support_top_z_distance (0.45 mm).
        assert distance>=.30-1e-4,('passing branch too close to model',distance,z,r)
        passing_branches.append({'support_top_cad_z_mm':z,'a_cad_xy_mm':(np.array(r['a'])-shift[:2]).tolist(),
            'b_cad_xy_mm':(np.array(r['b'])-shift[:2]).tolist(),'width_mm':r['width'],
            'broad_phase_overlap_mm2':area,'next_support_top_cad_z_mm':next_z,'connected_to_next_layer':connected,
            'nearest_model_top_cad_z_mm':model_z,'nominal_bead_separation_mm':distance,
            'xy_air_mm':xy_air,'z_air_mm':z_air})
    result=json.loads((job/'ready/result.json').read_text());plate,=result['sliced_plates']
    assert result['return_code']==0 and not plate['warning_message'],plate.get('warning_message')
    support=audit(path,part['name'],ROOT/part['source'],project,include_unlabelled_support=True)
    (out/'support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
    report={'status':'pass','verified_at_utc':datetime.now(timezone.utc).isoformat(),
        'printer':printer,'archive':str(archive.relative_to(ROOT)),'archive_sha256':sha(archive),
        'gcode_sha256':hashlib.sha256(gc).hexdigest(),'preparation':prep,
        'settings_verified':expected,'saved_speeds_accelerations_temperatures_fans_preserved':True,
        'requested_z_trim_mm':trim,'emitted_g29_1_z_mm':trims,'slot_support_intrusion_mm2':intrusion,
        'slot_roof_checks':roofcheck,'first_two_layer_heights_mm':layers[:2],
        'second_layer_minimum_wall_support_fraction':overlap,'layer_spans':spans,'wall_scope_checks':samples,
        'established_floor_scarf_reference':reference_foot,
        'support_roads_near_exterior_count':sum(len(v) for v in near_support.values()),
        'support_interface_or_terminating_tip_on_exterior_transition':0,
        'passing_branch_clearance_review':passing_branches,'support_summary':support['summary'],
        'path_bounds_xy_mm':bounds.tolist(),'minimum_plate_margin_mm':margin,'features':dict(features),
        'estimate_seconds':plate['total_predication'],'layers':len(layers),'filaments':plate['filaments'],
        'launch_options':{'timelapse':'On','bed_leveling':'On','flow_calibration':'Auto','nozzle_offset_calibration':'Auto'},'submitted':False}
    (out/'preflight.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['status','printer','estimate_seconds','layers','slot_support_intrusion_mm2','slot_roof_checks','wall_scope_checks','minimum_plate_margin_mm']}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('printer',choices=('H2C','Mark2'));p.add_argument('--revision',type=int,default=1)
    a=p.parse_args();main(a.printer,a.revision)
