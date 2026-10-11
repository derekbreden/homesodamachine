"""The Pour: a working sectional appliance made from native machine interfaces.

Generate the current reference geometry manually. Manufacturing coordinates,
colour registration and assembled display coordinates are distinct. Factory
faucet facets are frozen inputs; source cabinet functions construct native joints.
"""
from __future__ import annotations
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import cadquery as cq
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
sys.path[:0]=[str(HERE),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/cadlib')]
import cabinet_module as cabinet
import enclosure_features
import faucet_module as faucet
import comparison_additions_v3 as comparisons
import captive_shutters
import recipe_v3
from viewer_payload import write_part_payloads
from _cadq_export import export_assembly
import flute_skin
import _mesh_payload
from flute_payload import creased

I=np.eye(4)
BLACK=[.20,.20,.21]; WHITE=[235/255,236/255,234/255]; RED=[228/255,83/255,87/255]
QUADRANTS={'front-bottom':(0,0,1),'front-top':(0,0,1),'back-bottom':(0,0,1),'back-top':(0,0,-1)}
GROUPS={
 'nameplate':['nameplate_black','nameplate_white'],
 'DATA':['DATA_body','DATA_word'],
 'TAP':['port_water_body','port_water_word'],
 'CO2':['port_co2_body','port_co2_word'],
 'OVER':['port_drain_body','port_drain_word'],
}
PART_NAMES={
 'front-bottom':'Lower front shell and plumbing divider',
 'front-top':'Sliding upper front and display facet',
 'back-bottom':'Lower rear shell and fixed cartridge dock',
 'back-top':'Upper rear shell, counter and plumbing ceilings',
 'pump_drawer':'Working cartridge drawer and front nameplate host',
 'pump_cap':'Native pump clamp and pogo lead spine',
 'handhold_grip':'Complete flat-wing handhold liner',
 'moving_tee_carrier':'Native low-force tee carrier',
 'vertical_window_cover':'Native tee window cover',
 'removable_plumbing_lid':'Complete native funnel corner and hooked rail',
 'display_cover':'Full flat-wing display bezel',
 'display_gasket_90A':'Native display gasket, white TPU 90A',
 'display_nominal_backer':'Nominal one-millimetre glass-space backer',
 'nameplate':'Native two-colour unit 001 nameplate',
 'DATA':'Native flat-wing DATA plate',
 'TAP':'Native clamped TAP label', 'CO2':'Native clamped CO2 label', 'OVER':'Native clamped OVER label',
}

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def relative(path):return str(Path(path).resolve().relative_to(ROOT))
def read(path):return json.loads(Path(path).read_text())
def write(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')
def transform(shape,matrix):return faucet.transformed(shape,np.asarray(matrix))
def frame(shape,up):
    rotation=trimesh.geometry.align_vectors(np.asarray(up,float),[0.,0.,1.])
    b=transform(shape,rotation).BoundingBox()
    rotation[:3,3]=[-(b.xmin+b.xmax)/2,-(b.ymin+b.ymax)/2,-b.zmin]
    return rotation

def mesh(shape):
    from _meshes import mesh_shape
    v,f=mesh_shape(shape.copy(mesh=False),.005,.05)
    result=trimesh.Trimesh(vertices=v,faces=f,process=True)
    return result

def canonical(mesh):
    # Manifold performs the source skin union after float32 representation.
    return trimesh.boolean.union([flute_skin.as_written(mesh)],engine='manifold',check_volume=False)

def inscription(shape):
    for words,size,x,y in [('THE POUR',8.,0.,35.),('V3',6.,0.,52.),('BATCH / DATE',4.,-93.,30.)]:
        text=cq.Workplane('XY').text(words,size,.72,font='Helvetica',kind='bold',halign='center',valign='center').val()
        text=text.rotate((0,0,0),(1,0,0),180).translate((x,y,.71))
        shape=shape.cut(text)
    return shape.clean()

def stage_faucet(output):
    record=read(faucet.HERE/'faucet-module.json')
    parts=[]
    for source in record['parts']:
        row=deepcopy(source)
        for key in ('step','stl'):
            old=ROOT/row[key]; new=output/'parts'/old.name
            shutil.copyfile(old,new);row[key]=relative(new);row[key+'_sha256']=digest(new)
        if row.get('seated_display'):
            for key in ('step','stl'):
                old=ROOT/row['seated_display'][key];new=output/'parts'/old.name
                shutil.copyfile(old,new);row['seated_display'][key]=relative(new)
            row['seated_display']['assembly_matrix_mm']=faucet.matrix(faucet.ROOT_POINT).tolist()
        obj=next(x for x in record['print_objects'] if x['id']==row['id'])
        volumes=deepcopy(obj['volumes'])
        if len(volumes)>1:
            for v in volumes:
                old=ROOT/v['stl'];new=output/'parts'/old.name
                shutil.copyfile(old,new);v['stl']=relative(new);v['stl_sha256']=digest(new)
                solid=cq.importers.importStep(str(ROOT/row['step'])).val()
                bodies=sorted(solid.Solids(),key=lambda s:s.Volume(),reverse=True)
                selected=bodies[0] if v['id'].endswith('body') else cq.Compound.makeCompound(bodies[1:])
                vp=output/'parts'/(v['id']+'.step');cq.exporters.export(selected,str(vp));v['step']=relative(vp)
            row['material_volumes']=volumes
        row['assembly']={'matrix_mm':row['assembly_matrix_mm']}
        row['color_rgb']=BLACK if row['material']!='TPU' else WHITE
        row['logical_quantity']=1
        parts.append(row)
    return parts,record

def cabinet_up(name,metadata):
    if name in QUADRANTS:return QUADRANTS[name]
    if name in ('Q24','Q48','Q72'):return (0,0,-1)
    if name.startswith('R'):return (0,0,1)
    if name in ('nameplate','DATA'):return (0,-1,0) if name=='nameplate' else (0,1,0)
    if name=='handhold_grip':return (0,0,-1)
    if name in metadata['drawer']['part_print_up']:return metadata['drawer']['part_print_up'][name]
    aliases={'TAP':'port_water_body','CO2':'port_co2_body','OVER':'port_drain_body'}
    target=aliases.get(name,name)
    for feature in metadata['features']:
        if target in feature['part_print_up']:
            axis=np.asarray(feature['part_print_up'][target],float)
            # Cached reports predating placed-axis serialization have native
            # axes; report layout supplies the rigid source station rotation.
            angle=np.radians(feature.get('layout',{}).get('rotation_z_deg',0.))
            if feature['name'].startswith('port_') and not feature.get('layout',{}).get('axes_rotated'):
                axis=np.array([np.cos(angle)*axis[0]-np.sin(angle)*axis[1],np.sin(angle)*axis[0]+np.cos(angle)*axis[1],axis[2]])
            return axis
    raise KeyError('Native manufacturing direction absent: '+name)

def native_part(identifier,shapes,output,metadata,all_meshes,native,box):
    names=GROUPS.get(identifier,[identifier]);shape=cq.Compound.makeCompound([shapes[n] for n in names]) if len(names)>1 else shapes[names[0]]
    if identifier=='front-bottom':shape=inscription(shape)
    m=frame(shape,cabinet_up(identifier,metadata))
    physical_mesh=mesh(shape)
    if identifier in QUADRANTS:
        rails=native.flute_rails(box,[v for n,v in all_meshes.items() if n!=identifier])
        plains=[]
        for n in ('DATA_body','port_water_body','port_co2_body','port_drain_body'):
            bb=shapes[n].BoundingBox();plains.append((bb.xmin-.25,bb.xmax+.25,bb.ymin-.25,bb.ymax+.25,bb.zmin-.25,bb.zmax+.25))
        rails=[r._replace(plain=r.plain+tuple(plains)) for r in rails]
        physical_mesh=flute_skin.flute(physical_mesh,rails,native.flute_pitch(box.outer),native.flute_depth,native.flute_rise)
        if identifier=='back-bottom':
            physical_mesh=trimesh.boolean.union([flute_skin.as_written(physical_mesh),flute_skin.as_written(mesh(native.disposal_letters(box.outer)))],engine='manifold',check_volume=False)
    elif identifier=='pump_drawer':
        bb=shape.BoundingBox()
        rail=flute_skin.Rail(at=lambda s:((s,0.),(0.,-1.)),length=bb.xmax-bb.xmin,start=bb.xmin,closed=False,band=(6.25,70.),berthed=tuple(all_meshes[n] for n in ('nameplate_black','nameplate_white')),mouth=(0,-1),plain=((-56.,60.,-4.,4.,8.,65.),))
        physical_mesh=flute_skin.flute(physical_mesh,[rail],native.flute_pitch(box.outer),native.flute_depth,native.flute_rise)
    physical_mesh=canonical(physical_mesh)
    physical_mesh.apply_transform(m)
    stl=output/'parts'/(identifier+'.stl');step=output/'parts'/(identifier+'.step')
    physical_mesh.export(stl);cq.exporters.export(transform(shape,m),str(step))
    row={'id':identifier,'name':PART_NAMES.get(identifier,identifier.replace('_',' ')),
         'material':'TPU90A' if identifier=='display_gasket_90A' else 'PET-GF',
         'step':relative(step),'stl':relative(stl),'step_sha256':digest(step),'stl_sha256':digest(stl),
         'manufacturing_frame':{'id':identifier+'-native-print','baked_into_meshes':True,'from_source_matrix_mm':m.tolist(),'authority':'Native production axis retained after rigid service-section placement'},
         'assembly_matrix_mm':np.linalg.inv(m).tolist(),'assembly':{'matrix_mm':np.linalg.inv(m).tolist()},
         'print_bounds_mm':physical_mesh.bounds.tolist(),'native_group_members':names,
         'color_rgb':WHITE if identifier=='display_gasket_90A' else BLACK,'logical_quantity':1}
    if identifier.startswith('Q'):
        row['assembly_matrix_mm']=(faucet.matrix((-13,0,0))@np.linalg.inv(m)).tolist();row['assembly']['matrix_mm']=row['assembly_matrix_mm']
        row['native_review']=captive_shutters.witnesses()[identifier]
        row['print_transform_mm']=I.tolist()
        row['assembly_scope']='Closed display position,13mm left of the as-printed middle position;26mm total travel.'
    if len(names)>1:
        volumes=[]
        for n in names:
            vm=canonical(mesh(shapes[n]));vm.apply_transform(m)
            vp=output/'parts'/(n+'.stl');vs=output/'parts'/(n+'.step')
            vm.export(vp);cq.exporters.export(transform(shapes[n],m),str(vs))
            ink=n.endswith(('white','word'))
            rgb=WHITE if ink else BLACK
            if identifier in ('TAP','OVER'):rgb=BLACK if ink else WHITE
            if identifier=='CO2':rgb=WHITE if ink else RED
            slot=2 if rgb==WHITE else 1
            if identifier=='CO2':slot=1 if rgb==WHITE else 2
            volumes.append({'id':n,'part_id':identifier,'stl':relative(vp),'step':relative(vs),'stl_sha256':digest(vp),'transform_mm':I.tolist(),'filament_slot':slot,'color_rgb':rgb})
        row['material_volumes']=volumes
    return row

def generate(output,*,reuse=False):
    output=Path(output).resolve();(output/'parts').mkdir(parents=True,exist_ok=True)
    if not reuse:
        result=cabinet.build(use_core_cache=False);cabinet.export_cache(result)
        faucet.export_cache()
    source_folder=cabinet.CACHE_DIR;metadata=read(source_folder/'geometry.json')
    native=cabinet.enclosure_core.source_module()
    box=cabinet.enclosure_core.compact_box(native)
    shapes={n:cq.importers.importStep(str(source_folder/(n+'.step'))).val() for n in metadata['parts']}
    all_meshes={n:mesh(s) for n,s in shapes.items()}
    parts,faucet_record=stage_faucet(output)
    grouped={member for group in GROUPS.values() for member in group}
    for name in [*[n for n in shapes if n not in grouped],*GROUPS]:
        print('Emit',name,flush=True)
        parts.append(native_part(name,shapes,output,metadata,all_meshes,native,box))
    necks,_,neck_record=comparisons.neck_controls()
    _,_,stepbytes,stlbytes,_=comparisons.frozen_neck()
    for identifier,z in [('NR00',20.),('NR05',58.)]:
        _,_,_,_,source=comparisons.frozen_neck();origin=source['source_axis_origin_print_frame_mm']
        m=faucet.matrix((-83.,179.,z))@faucet.matrix(rot=(15.,0.,0.))@faucet.matrix(tuple(-v for v in origin))
        stl=output/'parts'/(identifier+'.stl');step=output/'parts'/(identifier+'.step')
        stl.write_bytes(stlbytes);step.write_bytes(stepbytes)
        parts.append({'id':identifier,'name':identifier+' regular seam control on native tubes','material':'PET-GF','step':relative(step),'stl':relative(stl),'step_sha256':digest(step),'stl_sha256':digest(stl),'manufacturing_frame':{'id':identifier+'-native-print','baked_into_meshes':True,'from_source_matrix_mm':I.tolist(),'authority':'Frozen native -15 degree source print pose'},'assembly_matrix_mm':m.tolist(),'assembly':{'matrix_mm':m.tolist()},'color_rgb':BLACK,'print_recipe':neck_record['recipes'][identifier],'notes':neck_record,'logical_quantity':1})
    assembly=cq.Assembly(name='The Pour')
    parent=next(r for r in parts if r['id']=='back-top')
    for row in parts:
        if row['id'] in ('Q24','Q48','Q72'):
            row['print_transform_mm']=(np.asarray(parent['manufacturing_frame']['from_source_matrix_mm']) @ np.linalg.inv(row['manufacturing_frame']['from_source_matrix_mm'])).tolist()
    payload=[];printable=[];bounds=[]
    for row in parts:
        volumes=row.get('material_volumes',[row])
        for volume in volumes:
            stl=ROOT/volume['stl'];step=ROOT/volume.get('step',row['step']);matrix=np.asarray(row['assembly_matrix_mm'])
            if row.get('seated_display'):
                stl=ROOT/row['seated_display']['stl'];step=ROOT/row['seated_display']['step'];matrix=np.asarray(row['seated_display']['assembly_matrix_mm'])
            shaped=transform(cq.importers.importStep(str(step)).val(),matrix)
            name=volume.get('id',row['id']);rgb=volume.get('color_rgb',row['color_rgb'])
            if row['id']=='TC':rgb=[105/255,180/255,247/255] if name.endswith('body') else WHITE
            assembly.add(shaped,name=name,color=cq.Color(*rgb))
            vm=trimesh.load_mesh(stl,process=True);vm.apply_transform(matrix);bounds.append(vm.bounds)
            pos,nrm,idx,fac=creased(vm)
            payload.append({'name':name,'color':rgb,'pos':pos.ravel().tolist(),'nrm':nrm.ravel().tolist(),'idx':idx.ravel().tolist(),'fac':fac.tolist()})
            printable.append({**row,'name':name,'stl':relative(stl),'step':relative(step),'assembly':{'matrix_mm':matrix.tolist()}})
    target=output/'the-pour.step';export_assembly(assembly,str(target))
    _mesh_payload.write(payload,str(target)+'.mesh',src=_mesh_payload.source_digest(target),cut={'dev':0,'bound':0})
    extrema=np.asarray(bounds);low=extrema[:,0,:].min(axis=0);high=extrema[:,1,:].max(axis=0)
    manifest={'schema':3,'version':'V3','title':'The Pour','concept':'Service Section','assembly':target.name,'assembly_sha256':digest(target),'parts':parts,'printable':printable,'bounds_mm':[low.tolist(),high.tolist()],'dimensions_mm':(high-low).tolist(),'logical_printed_parts':len(parts),'viewer_components':len(payload),'cabinet_source':metadata,'faucet_source':faucet_record,'neck_controls':neck_record,'physical_scope':'Unprinted service-section integration. Native source observations retain their recorded scopes; CAD and native slice establish geometry and deposited paths, not release, force, finish, sealing or lifetime.','assembly_hardware':{'native_cartridge':['Two M3 x 60 clamp screws, native M3 inserts, source pogo connector and M1.4 screws','Two RC62 magnets installed at native sealed pause planes'],'roofs':'Six M3 x 8 screws and M3 inserts in the moving floor pads','ports':'Three M3 x 12 draw screws and RX-M3Sx4.0 inserts for declared dry nominal clamps','faucet_counter':'Native three M3 plate/base axes through the perforated85A gasket and counter','seam_controls':'Real9.525mm water, two6.35mm flavors,4mm drain and4.6×1.18mm ribbon in the unchanged shared opening. Nominal1.0×4.8mm real nylon strap loops stop each cut end, enclosing all four round tubes and the full ribbon lane; assembly-review.json records the dimensioned envelope.','retention_scope':'Positive nominal joints and tied controls; unprinted assembly, tie friction, magnet force and repeated handling remain unmeasured.'},'reference_additions':['Three captive print-in-place inspection flags, with independent Z-release gaps','Printed dry fitting envelopes and nominal glass-space backer','Faucet dimensional donor rooted in its actual counter plate','Three native-profile support roofs bolted into the actual moving cartridge drawer']}
    manifest.update(recipe_v3.build_plan(manifest))
    write(output/'manifest.json',manifest)
    write_part_payloads(manifest)
    write(output/'geometry.json',{'parts':{r['id']:{'step_sha256':r['step_sha256'],'stl_sha256':r['stl_sha256'],'manufacturing_frame':r['manufacturing_frame'],'assembly_matrix_mm':r['assembly_matrix_mm']} for r in parts},'native_cabinet':metadata,'faucet_review':faucet_record['review']})
    print('The Pour:',len(parts),'physical parts;',len(payload),'viewer volumes;',manifest['dimensions_mm'],flush=True)
    return manifest

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--reuse-geometry',action='store_true');parser.add_argument('--output',type=Path,default=HERE)
    args=parser.parse_args();generate(args.output,reuse=args.reuse_geometry)
