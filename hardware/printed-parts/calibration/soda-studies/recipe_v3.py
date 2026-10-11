"""Manual native recipes for the current Service Section's frozen meshes.

Derive paint in each exact manufacturing frame. Production preparations are
source evidence; no producer, printer connection or recurring check is invoked.
"""
from copy import deepcopy
import argparse
import hashlib
import json
import math
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon, box as polygon_box
from shapely.ops import unary_union

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
ENC = ROOT/'hardware/printed-parts/enclosure/enclosure'
PP = ROOT/'hardware/printed-parts'
HERE = Path(__file__).resolve().parent
INDEX_SCOPE = 'trimesh.load(force=mesh,process=True) source STL face order'
BASE = dict(layer_height='0.24', enable_support='1', support_type='tree(auto)',
            support_style='default', wall_generator='classic', wall_loops='2',
            wall_sequence='inner wall/outer wall', infill_wall_overlap='15%',
            seam_position='aligned')


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def anchor(path, function=None):
    path=Path(path)
    return dict(path=str(path.relative_to(ROOT)),sha256=digest(path), **({'function':function} if function else {}))
def mesh(part): return trimesh.load(ROOT/part['stl'],force='mesh',process=True)
def band(low,high,height=.24,walls=None,reason=None):
    options={'layer_height':str(height)}
    if walls is not None:options['wall_loops']=str(walls)
    return dict(min_z_mm=round(float(low),6),max_z_mm=round(float(high),6),options=options,**({'reason':reason} if reason else {}))
def paint_record(part, selected, codes=None, **scope):
    return dict(source_stl_sha256=part['stl_sha256'],index_scope=INDEX_SCOPE,
                block_triangle_indices=np.flatnonzero(selected).tolist(),
                triangle_codes=codes or {},**scope)
def source_triangles(part,m):
    matrix=np.asarray(part['manufacturing_frame']['from_source_matrix_mm'])
    inverse=np.linalg.inv(matrix)
    pts=trimesh.transform_points(m.vertices,inverse)[m.faces]
    normals=m.face_normals@matrix[:3,:3]
    return pts,normals


def flat_contact_codes(points, flat, permitted):
    """Production four-way triangle painting, preserving the 0.8 mm inset."""
    def encode(p, depth=0):
        polygon=Polygon(p[:,:2])
        if permitted.covers(polygon):return '0'
        if not permitted.intersects(polygon) or depth==10:return '8'
        a,b,c=p;ab,bc,ca=(a+b)/2,(b+c)/2,(c+a)/2
        return ''.join(encode(np.array(q),depth+1) for q in
                       ((a,ab,ca),(ab,b,bc),(bc,c,ca),(ab,bc,ca)))+'3'
    return {str(i):encode(points[i]) for i in np.flatnonzero(flat)}


def roof_recipe(part, metadata):
    """Three unchanged full native roofs, uniform model grid and object gaps."""
    recipe=metadata['recipes'][part['id']]
    m=mesh(part);p=m.triangles;n=m.face_normals
    roof=recipe['native_contact_probe']['nominal_ceiling_z_mm']
    flat=(np.max(abs(p[:,:,2]-roof),axis=1)<.000001)&(n[:,2]<-.999999) \
        &(p[:,:,0].min(axis=1)>=-34.001)&(p[:,:,0].max(axis=1)<=34.001)
    if flat.any():
        original_depth=recipe['native_contact_probe']['flat_ceiling_bounds_xy_mm'][3]-recipe['native_contact_probe']['flat_ceiling_bounds_xy_mm'][2]
        flat &= p[:,:,1].max(axis=1)<=p[flat,:,1].min()+original_depth+.00001
    if not flat.any():raise ValueError(part['id']+': complete central source flat roof not found')
    face=unary_union([Polygon(v[:,:2]) for v in p[flat]])
    bounds=np.array([p[flat].min(axis=(0,1)),p[flat].max(axis=(0,1))])
    y_shift=bounds[0,1]-recipe['native_contact_probe']['flat_ceiling_bounds_xy_mm'][2]
    exterior=(p[:,:,1].min(axis=1)>=bounds[1,1]-.001) \
        &(p[:,:,2].min(axis=1)>=roof-6.01)&(p[:,:,2].max(axis=1)<=roof+9.05) \
        &(n[:,2]<-.00001)&(n[:,2]>-.99)&~flat
    codes=flat_contact_codes(p,flat,face.buffer(-.8))
    return dict(object_overrides={**BASE,'support_top_z_distance':recipe['support_top_z_distance']},
        layer_ranges=[band(35.,41.5,walls=6,reason='Complete source additive R6 upper handhold transition.')],
        support_paint=paint_record(part,exterior,codes,
            scope='Only outward additive R6 faces and source 0.8 mm flat-contact edge inset; central flat contact remains supportable.',
            exterior_triangle_count=int(exterior.sum()),flat_contact_triangle_count=int(flat.sum()),
            flat_contact_source_bounds_mm=bounds.tolist(),flat_contact_area_mm2=face.area),
        native_review={'ceiling_probes':[dict(name='Complete native handhold central flat contact',
            nominal_ceiling_z_mm=roof,window_xy_mm=[[-30.,-4.+y_shift],[30.,1.+y_shift]],
            requested_support_top_gap_mm=float(recipe['support_top_z_distance']))],
            'wall_probes':[dict(name='Exterior R6 roof land',line_xy_mm=[[0.,2.8+y_shift],[0.,10.+y_shift]],
                               print_z_mm=[38.,40.5],expected_wall_roads=6)]},
        sources=[anchor(ENC/'layer-policy-correction/prepare.py','prepare_bottom'),
                 anchor(PP/'cadlib/overhang_round.py','roof_rim')])


def cabinet_recipe(part, native, box):
    m=mesh(part);p,n=source_triangles(part,m);name=part['id']
    g=native.grip_interface(box.inner);roof=g.ROOF;y0,y1=native._handhold_y()
    selected=np.zeros(len(m.faces),bool);codes={};ranges=[];review={}
    sources=[anchor(ENC/'layer-policy-correction/prepare.py','prepare_bottom')]
    if name.endswith('bottom'):
        flat=(np.max(abs(p[:,:,2]-roof),axis=1)<.0001)&(n[:,2]<-.99) \
            &(p[:,:,0].max(axis=1)<=-g.INNER_FACE+native.handhold_wall+.001) \
            &(p[:,:,1].min(axis=1)>=y0-native.handhold_wall-.12) \
            &(p[:,:,1].max(axis=1)<=y1+native.handhold_wall+.12)
        selected=(p[:,:,0].max(axis=1)<=-g.INNER_FACE+.001) \
            &(p[:,:,1].min(axis=1)>=y0-native.handhold_corner_r-.01) \
            &(p[:,:,1].max(axis=1)<=y1+native.handhold_corner_r+.01) \
            &(p[:,:,2].min(axis=1)>=roof-native.handhold_edge_r-.01) \
            &(p[:,:,2].max(axis=1)<=roof+native.handhold_edge_r+3.05) \
            &(n[:,2]<-.00001)&(n[:,2]>-.99)&~flat
        if flat.any():
            area=unary_union([Polygon(v[:,:2]) for v in p[flat]])
            mouth=y0 if name.startswith('front') else y1
            yl,yh=(mouth-native.handhold_wall-.01,mouth+.01) if name.startswith('front') else (mouth-.01,mouth+native.handhold_wall+.01)
            half=g.WING_SPAN/2+g.WING_END_AIR
            blocked=polygon_box(-g.X_CENTER-half-.001,yl,-g.X_CENTER+half+.001,yh)
            codes=flat_contact_codes(p,flat,area.buffer(-.8).difference(blocked.buffer(1.,join_style=2)))
        ranges=[band(35.,41.5,walls=6,reason='Source additive expanding R6 handhold rim; fixed flat receiver planes retained.')]
    else:
        # Source roof-side strip moves with the actual envelope; horizontal
        # internal fitting ceilings have no outward-X normal and are retained.
        outward=(n[:,0]*np.sign(p[:,:,0].mean(axis=1))>.00001)
        selected=(np.abs(p[:,:,0]).min(axis=1)>=box.outer[1]-7.5-.001) \
            &(p[:,:,2].min(axis=1)>=box.outer[5]-9.31-.001)&outward
        sources=[anchor(ENC/'accepted-fit-integration/prepare_prints.py')]
        if name=='front-top':
            ranges=[band(.20,m.bounds[1,2],.08,
                reason='Complete native swept fore R12 and side R6 inward/top show curves cross the full Z80..140 storey; source roof R18 included.')]
        else:
            ranges=[band(0.,9.4,walls=6,
                reason='Source additive expanding roof-side transition and show-surface runout in native -Z frame.')]
    return dict(object_overrides=dict(BASE),layer_ranges=ranges,
        support_paint=paint_record(part,selected,codes,
            scope='Actual source exterior show transitions; horizontal internal fitting ceilings retain automatic supports. Handhold flat contact keeps its source0.8mm inset and wing-slot halo.',
            exterior_triangle_count=int(selected.sum()),flat_contact_triangle_count=len(codes)),
        native_review=review,sources=sources)


def modifier(part, identifier, world_bounds, options=None):
    bounds=np.asarray(world_bounds,float).reshape(3,2).T
    return dict(id=identifier,subtype='modifier_part',bounds_mm=bounds.tolist(),
        transform_mm=deepcopy(part['manufacturing_frame']['from_source_matrix_mm']),
        options=options or {'sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag'})


def full_host_modifiers(part,native,box,metadata):
    """Source full seam/root regions and native insert hosts at their new stations."""
    name=part['id'];rows=[]
    def add(label,bounds):rows.append(modifier(part,label,bounds))
    if name in ('front-bottom','front-top','back-bottom','back-top'):
        front=name.startswith('front');top=name.endswith('top');yb=native._y_boss(box.y_joint)
        for xi,xe,sx,z in box.y_bosses:
            if (z>native.z_seam)!=top:continue
            _seat,tip,blind,cap=native._boss_x(xe,sx)
            low=z-native.socket_r if top else native._handhold_levels(box.inner)[1]
            high=box.outer[5] if top else native.z_seam
            xa,xb=sorted((xe,cap if front else tip))
            ya,yc=(box.y_joint-native.wall,yb+native.socket_r) if front else (box.y_joint,box.y_joint+native.lip_len+2.)
            add(f'Native Y seam full host {sx:+g}/{z:g}',[xa,xb,ya,yc,low,high])
        for sx in (-1,1):
            # The source region extends17.5mm from each outer plane and covers
            # the complete retained rail/end-stop section and wall root.
            xa,xb=sorted((sx*(box.outer[1]-17.5),sx*box.outer[1]))
            ya,yc=(box.outer[2],box.y_joint) if front else (box.y_joint,box.outer[3])
            add(f'Native Z rail full root {sx:+g}',[xa,xb,ya,yc,native.z_seam-native.wall,
                                                native.z_seam+native.z_rise+native.wall])
        for feature in metadata['features']:
            if feature['name'] not in ('compressor_M5_post','condenser_M3_corbel','electronics_M3_mount','C14_tunnel'):continue
            for label,record in feature['add'].items():
                b=np.asarray(record['bounds_mm'],float).reshape(3,2)
                owns_front=b[1].mean()<=box.y_joint
                owns_top=b[2].mean()>native.z_seam
                if owns_front!=front or owns_top!=top:continue
                if feature['name']=='compressor_M5_post':b[2,0]=box.outer[4]
                elif feature['name'] in ('condenser_M3_corbel','electronics_M3_mount'):
                    b[0,0]=box.outer[0]
                elif feature['name']=='C14_tunnel':
                    # Source screw hosts, transformed with the complete tunnel.
                    # The rest of the unthreaded tunnel keeps ordinary infill.
                    continue
                add(feature['name']+' full native root',b.reshape(-1).tolist())
        # The intact fixed pogo pair is cropped from the source front-top and
        # lives in the current lower rear docking wall.
        if name=='back-bottom':
            d=metadata['drawer'];x,z=d['pogo_pair']['world_axis_xz_mm'];face=d['fixed_mating_y_mm']
            add('Fixed pogo full hosts and blind caps',[x-15,x+15,face,face+13.5,z-2.75,z+2.75])
    d=metadata['drawer'];move=np.asarray(d['source_translation_mm'])
    source_record=__import__('json').loads((ENC/'heat-set-review/print-regions.json').read_text())
    key={'pump_drawer':'pump-cartridge','pump_cap':'pump-cap'}.get(name)
    if key:
        for row in source_record['pieces'][key]:
            b=np.asarray(row['machine_bounds_mm']).reshape(3,2)+move[:,None]
            add(row['name'],b.reshape(-1).tolist())
    if name=='back-top':
        f=next(f for f in metadata['features'] if f['name']=='C14_tunnel')
        angle=math.radians(f['layout']['rotation_z_deg']);c,s=math.cos(angle),math.sin(angle)
        transform=np.eye(4);transform[:2,:2]=[[c,-s],[s,c]]
        transform[:3,3]=np.asarray(f['layout']['translation_mm'])-transform[:3,:3]@np.asarray(f['layout']['source_origin_mm'])
        for row in source_record['pieces']['back-top']:
            if not row['name'].startswith('C14 host'):continue
            b=np.asarray(row['machine_bounds_mm']).reshape(3,2).T
            v=trimesh.creation.box(extents=b[1]-b[0]);v.apply_translation(b.mean(axis=0));v.apply_transform(transform)
            # These station transforms are axial, so their resulting bounds
            # retain the exact source boxes rather than widening oblique stock.
            add(row['name'],v.bounds.T.reshape(-1).tolist())
    return rows


def magnet_recipe(part,metadata):
    """Retained source flat magnetic roof, blocked only for insertion and pause."""
    if part['id'] not in ('pump_drawer','back-bottom'):return None
    d=metadata['drawer'];source=__import__('json').loads((ENC/'magnet-retention/geometry-check.json').read_text())['pieces']
    old=source['pump-cartridge' if part['id']=='pump_drawer' else 'front-top']
    move=np.asarray(d['source_translation_mm']);x,z=np.asarray(old['axis_xz_mm'])+move[[0,2]]
    y0,y1=np.asarray(old['pocket_y_mm'])+move[1];roof=old['roof_z_mm']+move[2]
    m=mesh(part);p,n=source_triangles(part,m);radius=old['pocket_radius_mm']
    selected=(np.max(abs(p[:,:,2]-roof),axis=1)<.001)&(n[:,2]<-.99) \
        &(p[:,:,0].min(axis=1)>=x-radius-.001)&(p[:,:,0].max(axis=1)<=x+radius+.001) \
        &(p[:,:,1].min(axis=1)>=y0-.12)&(p[:,:,1].max(axis=1)<=y1+.12)
    if not selected.any():raise ValueError(part['id']+': retained source magnetic roof not found')
    matrix=np.asarray(part['manufacturing_frame']['from_source_matrix_mm']);cad=trimesh.transform_points(np.array([[x-7,y0+.5,roof-.05],[x+7,y1-.5,roof+1.]]),matrix)
    print_roof=matrix[2]@[x,(y0+y1)/2,roof,1.]
    pause=.2+math.ceil((print_roof+.24/2-.2)/.24)*.24
    return dict(block_triangle_indices=np.flatnonzero(selected).tolist(),
        pause=dict(print_z_mm=round(pause,6),message='Insert one RC62 magnet upright with the attracting polarity; fully below both rims, clear of toolhead and passages.',
                   cover_probe_bounds_mm=cad.tolist(),nominal_cover_plane_print_z_mm=print_roof),
        source=anchor(ENC/'magnet-retention/prepare_prints.py','prepare'))


def shutter_members(parts,back_top):
    """Common -Z assembly; independent named bed-start flags and scoped gaps."""
    root_matrix=np.asarray(back_top['manufacturing_frame']['from_source_matrix_mm'])
    objects=[]
    for identifier,cx,gap in [('Q24',-63.,.24),('Q48',0.,.48),('Q72',63.,.72)]:
        row=parts[identifier];local=np.asarray(row['manufacturing_frame']['from_source_matrix_mm'])
        row=deepcopy(row);row['print_transform_mm']=(root_matrix@np.linalg.inv(local)).tolist()
        def pb(x0,x1,y0,y1,z0,z1):
            vertices=np.array([[x,y,z] for x in (x0,x1) for y in (y0,y1) for z in (z0,z1)])
            v=trimesh.transform_points(vertices,root_matrix)
            return [v.min(axis=0).tolist(),v.max(axis=0).tolist()]
        center=-cx;foot=50.12;cap=foot+gap;lower=45.32;moving_floor=46.76
        release=[dict(name='Solid-skin variable cap air',fixed_body_id='back-top',moving_body_id=identifier,
                      fixed_surface='bottom',moving_surface='top',requested_gap_mm=gap,
                      fixed_contact_bounds_mm=[[center-8,57.8,cap-.05],[center+8,58.7,cap+.75]],
                      moving_contact_bounds_mm=[[center-8,57.8,foot-.75],[center+8,58.7,foot+.05]],
                      support_gap_bounds_mm=[[center-8,57.8,foot],[center+8,58.7,cap]]),
                 dict(name='Fixed generous lower air',fixed_body_id='back-top',moving_body_id=identifier,
                      fixed_surface='top',moving_surface='bottom',requested_gap_mm=1.44,
                      fixed_contact_bounds_mm=[[center-8,57.8,lower-.75],[center+8,58.7,lower+.05]],
                      moving_contact_bounds_mm=[[center-8,57.8,moving_floor-.05],[center+8,58.7,moving_floor+.75]],
                      support_gap_bounds_mm=[[center-8,57.8,lower],[center+8,58.7,moving_floor]])]
        lateral=[]
        for name,span,start,end,fixed,moving in [
            ('-Y running face',[47.,49.88],[center,49.],[center,60.],[0.,4.15],[4.5,10.5]),
            ('+Y running foot',[47.,49.88],[center,54.],[center,63.3],[5.85,8.85],[0.,5.5]),
            ('-Y first bed layer',[.19,.21],[center,49.],[center,60.],[0.,4.15],[4.5,10.5]),
            ('+Y first bed layer',[.19,.21],[center,54.],[center,63.3],[2.85,8.85],[0.,2.5])]:
            lateral.append(dict(name=name,fixed_body_id='back-top',moving_body_id=identifier,requested_gap_mm=.35,
                line_xy_mm=[start,end],print_z_mm=span,fixed_interval_mm=fixed,moving_interval_mm=moving))
        row['native_review']={**row.get('native_review',{}),
            'body_window':pb(cx-15,cx+15,216.35,222.35,89.88,140.001),
            'native_release_probes':release,'native_gap_probes':lateral,
            'travel_x_mm':26.,'y_running_air_per_side_mm':.35,'first_layer_chamfer_mm':.35}
        objects.append(row)
    return objects


def shutter_blockers(back_top):
    matrix=back_top['manufacturing_frame']['from_source_matrix_mm'];result=[]
    for identifier,cx,gap in [('Q24',-63.,.24),('Q48',0.,.48),('Q72',63.,.72)]:
        result.append(dict(id=identifier+' swept foot motion air',subtype='support_blocker',
            bounds_mm=[[cx-28.35,216.05,89.88-gap-.05],[cx+28.35,222.65,94.68+.05]],
            transform_mm=deepcopy(matrix),options={}))
    return result


def pump_recipe(part, metadata):
    """Keep the accepted lower fine rim and additive upper side-pull roof."""
    m=mesh(part);p,n=source_triangles(part,m)
    move=np.asarray(metadata['drawer']['source_translation_mm'])
    original=p-move
    flat=(np.max(abs(original[:,:,2]-272.1940001),axis=1)<.00003)&(n[:,2]<-.99)
    region=(original[:,:,0].min(axis=1)>=91.7) \
        &(original[:,:,1].min(axis=1)>=22.19)&(original[:,:,1].max(axis=1)<=61.42) \
        &(original[:,:,2].min(axis=1)>=266.18)&(original[:,:,2].max(axis=1)<=278.21)
    selected=region&(n[:,2]<-.00001)&~flat
    permitted=polygon_box(92.55,34.9325,100.7,49.3325)
    codes=flat_contact_codes(original,flat&region,permitted)
    return dict(object_overrides=dict(BASE),
        layer_ranges=[band(6.,18.4,.08,reason='Complete source inward lower side-pull rim.'),
                      band(100.3,113.2,walls=6,reason='Complete source additive upper side-pull roof.')],
        support_paint=paint_record(part,selected,codes,
            scope='Only source exterior upper rim and source flat contact inset; accessible inner contacts remain supported.'),
        native_review={},sources=[anchor(ENC/'magnet-retention/prepare_prints.py','cartridge_layer_ranges')])


def marking_cohorts(faucet_plan):
    colour=deepcopy(next(c for c in faucet_plan['print_cohorts'] if c['id']=='colour'))
    black=deepcopy(colour);black['id']='markings-black-white'
    red=deepcopy(colour);red.update(id='markings-red-white',settings_source=str((HERE/'inputs/co2-settings.3mf').relative_to(ROOT)))
    red['material_source']={
        'source_native_archive_sha256':'b9f421292f612bc6fdecb25dd82c0615dce4997300c1aa748766eb9962567c3c',
        'source':str((PP/'enclosure/tee-readiness/full-enclosure-print/native-slice-reviews/2026-10-04-bulkhead-co2-raised-mark2-v1/preparation.json').relative_to(ROOT)),
        'scope':'Native CO2 effective settings and filament presets: white left slot1, red right slot2, nominal0.4; right nozzle registration, source geometry unshifted. The editable wrapper restores both process/filament/printer inheritance triplets; no effective source setting is changed.'}
    soft=dict(id='TPU90A-white',settings_source=str((PP/'prototype-gaskets-2026-10-08/white90-faucet/2026-10-08-faucet-counter-gasket-white-tpu90a-right06-engineering-mark2.3mf').relative_to(ROOT)),
        global_overrides={'initial_layer_print_height':'.30','spiral_mode':'0'},requested_z_trim_mm=.04,
        material_source={'durometer':'90A','colour':'white','source_profile_sha256':'79046db4fa341be522e22eef0e367f0edc41829becb6c7a4cbe2402c284cf5b7',
            'scope':'Faithful white90A saved candidate: .30 first/.18 body, Arachne2, 100%zig-zag, right nominal0.6, 225C/35C. Display gasket compression, fit and sealing are unmeasured.'})
    return [black,red,soft]


def build_plan(manifest, faucet_plan=None):
    """Populate an emitted Service Section with explicit native objects/plates.

    Called manually by the geometry emitter. Source support paint is derived
    from the exact emitted STL; this function neither slices nor sends a print.
    """
    import print_plan as plan
    import enclosure_core
    faucet_plan=faucet_plan or json.loads((HERE/'faucet-plan.json').read_text())
    parts={p['id']:p for p in manifest['parts']};metadata=manifest['cabinet_source']
    native=enclosure_core.source_module();box=enclosure_core.compact_box(native)
    cabinets=[];objects=[];plates=[]
    for identifier in plan.QUADRANTS:
        part=parts[identifier];r=cabinet_recipe(part,native,box)
        r['modifiers']=full_host_modifiers(part,native,box,metadata)
        magnetic=magnet_recipe(part,metadata)
        if magnetic:
            r['support_paint']['block_triangle_indices']=sorted(set(r['support_paint']['block_triangle_indices']+magnetic['block_triangle_indices']))
            r['sources'].append(magnetic['source'])
        captives=shutter_members(parts,part) if identifier=='back-top' else []
        obj=plan.cabinet_object(part,quadrant=identifier,source_recipe=r,
            captive_parts=captives,support_blockers=shutter_blockers(part) if captives else [])
        if magnetic:obj['pauses']=[magnetic['pause']]
        if captives:
            # An interior fixed-body witness excludes the three shared-air flags.
            obj['volumes'][0]['native_review']={'body_window':[[-129.,-62.85,0.],[129.,48.15,98.236]]}
            obj['object_overrides']['elefant_foot_compensation']='0'
        cabinets.append(obj)
    def add(identifier, *, options=None, ranges=(), cohort='rigid', modifiers=(), review=None, volumes=None, sources=()):
        obj=plan.native_object(parts[identifier],cohort=cohort,
            object_overrides=options or dict(BASE),layer_ranges=ranges,modifiers=modifiers,native_review=review,volumes=volumes)
        obj['recipe_sources']=list(sources);objects.append(obj);return obj
    def plate(identifier,ids,cohort='rigid',**kwargs):
        plates.append(dict(id=identifier,cohort=cohort,object_ids=ids,filename='the-pour-v3-'+identifier,
            model_border_mm=kwargs.pop('model_border_mm',30.),model_spacing_mm=kwargs.pop('model_spacing_mm',40.),**kwargs))
    p=parts['pump_drawer'];r=pump_recipe(p,metadata);magnetic=magnet_recipe(p,metadata)
    r['support_paint']['block_triangle_indices']=sorted(set(r['support_paint']['block_triangle_indices']+magnetic['block_triangle_indices']))
    obj=add('pump_drawer',options=r['object_overrides'],ranges=r['layer_ranges'],
        modifiers=full_host_modifiers(p,native,box,metadata),sources=[*r['sources'],magnetic['source']])
    obj['volumes'][0]['support_paint']=r['support_paint'];obj['pauses']=[magnetic['pause']]
    plate('drawer',['pump_drawer'],offsets_mm=[[0.,0.]],model_border_mm=40.)
    add('pump_cap',modifiers=full_host_modifiers(parts['pump_cap'],native,box,metadata),
        sources=[anchor(ENC/'heat-set-review/print_regions.py')])
    no_support={**BASE,'enable_support':'0','brim_type':'no_brim','brim_width':'0','elefant_foot_compensation':'0'}
    add('moving_tee_carrier',options=no_support,
        ranges=[band(0.,6.1,walls=6,reason='Source additive expanding R6 foot.'),band(14.8,21.054,.08,reason='Source inward/top R6 nose.')],
        sources=[anchor(PP/'enclosure/tee-carrier/low-force-trial/prepare_print.py')])
    add('vertical_window_cover',sources=[anchor(PP/'enclosure/tee-carrier/tee_carrier.py','_cover')])
    add('removable_plumbing_lid',sources=[anchor(PP/'zone-c/funnel/funnel_frame.py','body_blank')])
    plate('service-parts',['pump_cap','moving_tee_carrier','vertical_window_cover','removable_plumbing_lid'])
    add('display_cover',options={**BASE,'enable_support':'0','brim_type':'no_brim','brim_width':'0'},ranges=[band(.20,.48,.28,reason='Source face-up second layer registration grid.')],
        sources=[anchor(PP/'enclosure/display-cover/face-up-trial/prepare_print.py')])
    plate('display-cover',['display_cover'],offsets_mm=[[0.,0.]],model_border_mm=60.)
    add('handhold_grip',options=no_support,ranges=[band(2.64,3.36,.08,reason='Complete source inward finger-face R0.6.')],
        sources=[anchor(PP/'enclosure/grip-cover/prepare_print.py')])
    add('display_nominal_backer',options={**BASE,'enable_support':'0'},ranges=[band(.92,1.,.08,reason='Close the declared1mm nominal glass-space backer.')])
    hardware=[i for i in parts if i.startswith('nominal_')]
    for i in hardware:add(i)
    plate('dry-hardware',['handhold_grip','display_nominal_backer',*hardware])
    for i in ('R30','R45','R60'):
        r=roof_recipe(parts[i],metadata['comparisons']);obj=add(i,options=r['object_overrides'],ranges=r['layer_ranges'],review=r['native_review'],sources=r['sources'])
        obj['volumes'][0]['support_paint']=r['support_paint']
    plate('support-roofs',['R30','R45','R60'],offsets_mm=[[0.,-48.],[0.,0.],[0.,48.]],model_border_mm=80.)
    for i,gap in [('NR00','0%'),('NR05','5%')]:
        add(i,options={**BASE,'wall_generator':'arachne','seam_gap':gap,'override_filament_scarf_seam_setting':'1','seam_slope_type':'none','seam_slope_inner_walls':'0'},
            ranges=[band(4.04,16.04,.12,reason='Unchanged complete source neck fine finish band.')],
            review={'comparison_bands':[dict(id=i,name='Native regular seam '+gap,print_z_mm=[4.04,16.04],interior_guard_mm=.48,layer_height_mm=.12)]})
    plate('regular-seams',['NR00','NR05'],offsets_mm=[[-40.,0.],[40.,0.]],model_border_mm=80.)
    for i in ('nameplate','DATA','TAP','OVER','CO2'):
        options={**BASE,'enable_support':'0','brim_type':'no_brim','brim_width':'0'}
        ranges=[band(.20,.48,.28,reason='Source flat face-up registration grid.')] if i in ('nameplate','DATA') else [band(1.88,2.,.12,reason='Exact2mm source body closure before the two .24 raised marking layers.')]
        cohort='markings-red-white' if i=='CO2' else 'markings-black-white'
        add(i,cohort=cohort,options=options,ranges=ranges,volumes=plan.registered_volumes(parts[i]))
    plate('nameplate-data',['nameplate','DATA'],'markings-black-white',model_border_mm=50.)
    plate('tap-over',['TAP','OVER'],'markings-black-white',model_border_mm=80.)
    plate('co2',['CO2'],'markings-red-white',offsets_mm=[[0.,0.]],model_border_mm=80.)
    add('display_gasket_90A',cohort='TPU90A-white',options={'layer_height':'.18','enable_support':'0','wall_generator':'arachne',
        'wall_loops':'2','sparse_infill_density':'100%','sparse_infill_pattern':'zig-zag','top_shell_layers':'3','bottom_shell_layers':'3'})
    plate('display-gasket90a',['display_gasket_90A'],'TPU90A-white',offsets_mm=[[0.,0.]],model_border_mm=60.)
    result=plan.build_print_plan(manifest['parts'],faucet_plan=faucet_plan,cabinet_objects=cabinets,small_objects=objects,
        material_sources=marking_cohorts(faucet_plan),small_plates=plates)
    next(p for p in result['print_plates'] if p['id']=='cabinet-front-bottom')['offsets_mm']=[[-11.664,0.]]
    back_top_plate=next(p for p in result['print_plates'] if p['id']=='cabinet-back-top')
    back_top_plate.update(rotation_z_degrees=8.,offsets_mm=[[5.625613376103004,1.5294341455736102]],
        placement_scope='Rigid bed-plane turn of the complete source parent and captive volumes, selected from the emitted automatic-support/model/brim hull. Source meshes, relative transforms, support policy and print-up axis are retained.')
    result['recipe_source_sha256']=digest(__file__)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=HERE/'manifest.json')
    parser.add_argument('--output',type=Path,help='Save only print plan keys here; omit to populate the manifest.')
    args=parser.parse_args();manifest=json.loads(args.manifest.read_text());plan=build_plan(manifest)
    destination=args.output or args.manifest
    destination.write_text(json.dumps(plan if args.output else {**manifest,**plan},indent=2)+'\n')


if __name__=='__main__':main()
