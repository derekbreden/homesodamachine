"""Manual one-object TPU projects using the retained Siraya right0.6 recipe.

No printer API, runtime setting, production export, or build-graph mutation.
"""
from pathlib import Path
import hashlib
import argparse
import json
import math
import os
import subprocess
import uuid
from types import SimpleNamespace
import sys
import time
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import trimesh
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_printer.py').is_file())
OUT=HERE/'plates'
# One0.62mm support bead plus0.03mm native-mesh/numeric allowance.
BLOCKER_XY_PAD=.65
BLOCKER_Z_MARGIN=2.
RECIPE_DIR=ROOT/'future/pump-elbow-exploration/prints/2026-10-14-compact-single-siraya85a-overhang10-engineering-z000-mark1'
CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
ET.register_namespace('',CORE);ET.register_namespace('p',PROD)

def q(tag):return '{'+CORE+'}'+tag

def uid(value):return str(uuid.uuid5(uuid.NAMESPACE_URL,'homesodamachine/asymmetric-wet/'+value))

def xml(element):return ET.tostring(element,encoding='UTF-8',xml_declaration=True)

def metadata(parent,key,value):ET.SubElement(parent,'metadata',key=key,value=str(value))

def mesh_object(resources,id_,mesh,name):
    obj=ET.SubElement(resources,q('object'),id=str(id_),type='model',**{'{'+PROD+'}UUID':uid(name)})
    body=ET.SubElement(obj,q('mesh'));vertices=ET.SubElement(body,q('vertices'));triangles=ET.SubElement(body,q('triangles'))
    for vertex in mesh.vertices:ET.SubElement(vertices,q('vertex'),**dict(zip('xyz',(f'{v:.9f}' for v in vertex))))
    for face in mesh.faces:ET.SubElement(triangles,q('triangle'),**dict(zip(('v1','v2','v3'),map(str,face))))

mf=SimpleNamespace(RECIPE=next(p for p in RECIPE_DIR.glob('*.3mf') if not p.name.endswith('.gcode.3mf')),
    SLICER=Path('/Applications/BambuStudio.app/Contents/MacOS/BambuStudio'),SETTINGS='Metadata/project_settings.config',
    PROD=PROD,REL=REL,I='1 0 0 0 1 0 0 0 1 0 0 0',q=q,uid=uid,xml=xml,metadata=metadata,mesh_object=mesh_object)
sys.path.insert(0,str(ROOT/'hardware/printed-parts/enclosure/pump-dock'))
import fixed_returns
import pump_receiver
import pump_return


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalized(value):
    if isinstance(value,list):return [normalized(x) for x in value]
    if isinstance(value,str):
        try:return float(value)
        except ValueError:return value
    return value


def decode(value):
    if isinstance(value,list):return tuple(decode(x) for x in value)
    if isinstance(value,dict):
        if '__hsm_namedtuple__' in value:return dict(zip(value['fields'],map(decode,value['values'])))
        if '__hsm_dict__' in value:return {k:decode(v) for k,v in value['__hsm_dict__']}
        if '__hsm_list__' in value:return list(map(decode,value['__hsm_list__']))
        return {k:decode(v) for k,v in value.items()}
    return value


def prepare(name,body,void,bindings,pose,dimensions,*,slice_native=False):
    folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
    shift=-body.BoundingBox().zmin
    pose=dict(pose,ports_print_mm={key:(value[0],value[1],value[2]+shift) for key,value in pose['ports_before_bedding_mm'].items()})
    body=body.translate((0,0,shift));void=void.translate((0,0,shift))
    a,b=map(math.radians,(pose['rotate_z_degrees'],pose['rotate_x_degrees']))
    rz=np.asarray([[math.cos(a),-math.sin(a),0.],[math.sin(a),math.cos(a),0.],[0.,0.,1.]])
    rx=np.asarray([[1.,0.,0.],[0.,math.cos(b),-math.sin(b)],[0.,math.sin(b),math.cos(b)]])
    source_to_print=np.eye(4);source_to_print[:3,:3]=rx@rz;source_to_print[2,3]=shift
    bed_faces=[face for face in body.Faces() if face.geomType()=='PLANE' and abs(face.BoundingBox().zmin)<1e-5 and abs(face.BoundingBox().zmax)<1e-5]
    meshes=[]
    for member,shape in zip(('body','wet-void'),(body,void)):
        target=folder/(member+'.stl')
        cq.exporters.export(shape,str(target),tolerance=.025,angularTolerance=.1)
        meshes.append(trimesh.load(target,force='mesh',process=True))
    blocker=wet_support_shadow(meshes[1],body.BoundingBox().zmax)
    blocker.export(folder/'wet-shadow-blocker.stl')
    model_meshes=(meshes[0],blocker)
    with zipfile.ZipFile(mf.RECIPE) as z:
        recipe=json.loads(z.read(mf.SETTINGS));original=dict(recipe)
        members={n:z.read(n) for n in ('[Content_Types].xml','_rels/.rels')}
    # These are exactly the retained preparation's documented offline changes.
    recipe.update(print_settings_id=name+' offline Siraya85A right06',enable_support='1',
        support_type='tree(auto)',support_style='default',support_filament='1',
        support_interface_filament='1',flush_into_support='0',seam_position='nearest',
        reduce_crossing_wall='1',time_lapse_gcode='',top_one_wall_type='not apply')
    members[mf.SETTINGS]=(json.dumps(recipe,indent=2)+'\n').encode()
    geometry=ET.Element(mf.q('model'),unit='millimeter');resources=ET.SubElement(geometry,mf.q('resources'))
    for i,(member,mesh) in enumerate(zip((name,'wet-passage-support-shadow'),model_meshes),1):
        mf.mesh_object(resources,i,mesh,member)
    member='3D/Objects/'+name+'.model';members[member]=mf.xml(geometry)
    model=ET.Element(mf.q('model'),unit='millimeter',requiredextensions='p')
    ET.SubElement(model,mf.q('metadata'),name='Application').text='BambuStudio-02.08.02.61'
    ET.SubElement(model,mf.q('metadata'),name='BambuStudio:3mfVersion').text='1'
    resources=ET.SubElement(model,mf.q('resources'))
    owner=ET.SubElement(resources,mf.q('object'),id='11',type='model',**{f'{{{mf.PROD}}}UUID':mf.uid(name+'-owner')})
    components=ET.SubElement(owner,mf.q('components'))
    config=ET.Element('config');cfg=ET.SubElement(config,'object',id='11')
    mf.metadata(cfg,'name',name+' offline one-object review');mf.metadata(cfg,'extruder',1)
    for i,(subtype,label,mesh) in enumerate(zip(('normal_part','support_blocker'),(name,'wet-passage-support-shadow'),model_meshes),1):
        ET.SubElement(components,mf.q('component'),objectid=str(i),transform=mf.I,**{f'{{{mf.PROD}}}path':'/'+member,f'{{{mf.PROD}}}UUID':mf.uid(name+'-component-'+str(i))})
        part=ET.SubElement(cfg,'part',id=str(i),subtype=subtype,uuid=mf.uid(name+'-part-'+str(i)))
        for key,value in dict(name=label,matrix='1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1',extruder=1,
            source_file=label,source_object_id=0,source_volume_id=0,source_offset_x=0,source_offset_y=0,source_offset_z=0).items():mf.metadata(part,key,value)
        ET.SubElement(part,'mesh_stat',face_count=str(len(mesh.faces)),edges_fixed='0',degenerate_facets='0',facets_removed='0',facets_reversed='0',backwards_edges='0')
    bounds=body.BoundingBox();dx=177.5-(bounds.xmin+bounds.xmax)/2;dy=160-(bounds.ymin+bounds.ymax)/2
    transform=f'1 0 0 0 1 0 0 0 1 {dx:.9f} {dy:.9f} 0'
    build=ET.SubElement(model,mf.q('build'),**{f'{{{mf.PROD}}}UUID':mf.uid(name+'-build')})
    ET.SubElement(build,mf.q('item'),objectid='11',transform=transform,printable='1',**{f'{{{mf.PROD}}}UUID':mf.uid(name+'-item')})
    plate=ET.SubElement(config,'plate')
    for key,value in dict(plater_id=1,plater_name=name+' offline review',locked='false',filament_map_mode='Auto For Flush',filament_maps='2',filament_volume_maps='0',bed_type=recipe['curr_bed_type']).items():mf.metadata(plate,key,value)
    instance=ET.SubElement(plate,'model_instance')
    for key,value in dict(object_id=11,instance_id=0,identify_id=2341).items():mf.metadata(instance,key,value)
    assemble=ET.SubElement(config,'assemble');ET.SubElement(assemble,'assemble_item',object_id='11',instance_id='0',transform=transform,offset='0 0 0')
    members['3D/3dmodel.model']=mf.xml(model);members['Metadata/model_settings.config']=mf.xml(config)
    rels=ET.Element(f'{{{mf.REL}}}Relationships')
    ET.SubElement(rels,f'{{{mf.REL}}}Relationship',Target='/'+member,Id='rel-1',Type='http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel')
    members['3D/_rels/3dmodel.model.rels']=mf.xml(rels).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
    project=folder/(name+'.3mf')
    with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED) as z:
        for label,data in sorted(members.items()):z.writestr(label,data)
    command=[str(mf.SLICER),'--slice','0','--arrange','0','--orient','0','--export-3mf',name+'.gcode.3mf','--outputdir',str(folder),str(project)]
    (folder/'command.json').write_text(json.dumps(command,indent=2)+'\n')
    if slice_native:
        print('SLICING',name,flush=True)
        native_started=time.monotonic()
        with (folder/'slice.log').open('w') as log:
            result=subprocess.run(command,cwd=folder,stdout=log,stderr=subprocess.STDOUT,env=dict(os.environ,OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1'))
        exit_code=result.returncode
        native_elapsed=time.monotonic()-native_started
    else:
        exit_code=None
        native_elapsed=None
    record={'status':('Offline native slice' if slice_native else 'Prepared offline native project')+'; no printer contacted or launched','slicer_exit_code':exit_code,'native_slice_wall_seconds':native_elapsed,
        'part':name,'normal_object_count':1,'wet_cavity_blocker_count':1,
        'source_to_print_mm':source_to_print.tolist(),'source_frame':'Wet builder local geometry before print rotations; plate XY centering is separate.',
        'preparation_mesh_tolerances':{'deflection_mm':.025,'angular_tolerance_rad':.10},
        'prepared_body_mesh':{'watertight':bool(meshes[0].is_watertight),'vertices':len(meshes[0].vertices),'facets':len(meshes[0].faces)},
        'prepared_wet_void_mesh':{'watertight':bool(meshes[1].is_watertight),'vertices':len(meshes[1].vertices),'facets':len(meshes[1].faces)},
        'native_flat_bed_face_areas_mm2':[face.Area() for face in bed_faces],
        'native_flat_bed_face_area_sum_mm2':sum(face.Area() for face in bed_faces),
        'blocker_strategy':{'definition':'Actual wet-cavity vertical projection plus0.65mmXY allowance, Z−2 to body top+2; local wet-shadow support exclusion only. External Tree(auto)/Default retained.',
            'blocker_stl_sha256':sha(folder/'wet-shadow-blocker.stl')},'source_sha256':bindings,
        'source_recipe':str(mf.RECIPE.relative_to(ROOT)),'source_recipe_sha256':sha(mf.RECIPE),
        'settings_changes':{k:{'source':original.get(k),'prepared':v} for k,v in recipe.items() if original.get(k)!=v},
        'project_sha256':sha(project),'body_stl_sha256':sha(folder/'body.stl'),'wet_void_stl_sha256':sha(folder/'wet-void.stl'),
        'plate_xy_translation_mm':[dx,dy],'body_min_z_to_bed_mm':shift,'pose':pose,'native_geometry_dimensions':dimensions,
        'physical_scope':'Oct14 Siraya single-elbow exterior accepted; internal stringing reported. This junction/return has no physical print, wet, pressure or life acceptance.'}
    archive=folder/(name+'.gcode.3mf')
    if slice_native and exit_code==0 and archive.exists():
        with zipfile.ZipFile(archive) as z:
            gcode=z.read('Metadata/plate_1.gcode');emitted=json.loads(z.read(mf.SETTINGS))
            keys=('machine_start_gcode','machine_end_gcode','filament_map','filament_nozzle_map',
                'nozzle_diameter','extruder_offset','nozzle_temperature','nozzle_temperature_initial_layer',
                'eng_plate_temp','eng_plate_temp_initial_layer','filament_flow_ratio',
                'filament_max_volumetric_speed','layer_height','initial_layer_print_height',
                'wall_loops','wall_sequence','top_one_wall_type','seam_gap','seam_position',
                'sparse_infill_density','enable_support','support_type','support_style',
                'support_top_z_distance','support_bottom_z_distance','support_object_xy_distance',
                'support_filament','support_interface_filament','time_lapse_gcode','reduce_crossing_wall',
                'retraction_length','filament_retraction_length','outer_wall_speed','inner_wall_speed')
            comparisons={k:normalized(recipe.get(k))==normalized(emitted.get(k)) for k in keys}
            record.update(archive_sha256=sha(archive),gcode_sha256=hashlib.sha256(gcode).hexdigest(),
                gcode_md5_matches=hashlib.md5(gcode).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower(),
                all_native_settings_match_prepared=emitted==recipe,
                critical_native_settings_preserved=comparisons,all_critical_native_settings_preserved=all(comparisons.values()),
                native_metadata_normalization_keys=[k for k in sorted(set(recipe)|set(emitted)) if recipe.get(k)!=emitted.get(k)])
        (folder/'plate_1.gcode').write_bytes(gcode)
        native=json.loads((folder/'result.json').read_text())['sliced_plates'][0]
        record.update(estimated_seconds=native['total_predication'],estimated_filament_g=sum(f['total_used_g'] for f in native['filaments']),slicer_warning=native['warning_message'])
    record['bound_sources_unchanged_after_slice']={p:sha(ROOT/p)==digest for p,digest in bindings.items()}
    (folder/'readback.json').write_text(json.dumps(record,indent=2)+'\n')
    print(name,exit_code,record.get('estimated_seconds'),flush=True)
    return record


def wet_support_shadow(wet,top_z):
    """Exclude support contacts in the actual wet passages' vertical shadow.

    A support_blocker controls contact generation; it is not a collision-volume
    promise. The exact emitted support beads still need the manual review.
    """
    triangles=[Polygon(p[:,:2]) for p in wet.triangles
               if abs(np.cross(p[1]-p[0],p[2]-p[0])[2])>1e-10]
    shadow=unary_union(triangles).buffer(BLOCKER_XY_PAD,quad_segs=16)
    solids=[]
    for poly in shadow.geoms if hasattr(shadow,'geoms') else [shadow]:
        outer=cq.Wire.makePolygon([cq.Vector(float(x),float(y),-BLOCKER_Z_MARGIN) for x,y in poly.exterior.coords])
        holes=[cq.Wire.makePolygon([cq.Vector(float(x),float(y),-BLOCKER_Z_MARGIN) for x,y in ring.coords]) for ring in poly.interiors]
        solids.append(cq.Solid.extrudeLinear(outer,holes,cq.Vector(0,0,float(top_z+2*BLOCKER_Z_MARGIN))))
    target=OUT/'_blocker-mesh.stl'
    OUT.mkdir(parents=True,exist_ok=True)
    cq.exporters.export(cq.Compound.makeCompound(solids),str(target),tolerance=.025,angularTolerance=.1)
    mesh=trimesh.load(target,force='mesh',process=True);target.unlink()
    return mesh


def rotate_point(point,z_degrees,x_degrees):
    x,y,z=point;a,b=map(math.radians,(z_degrees,x_degrees))
    u=x*math.cos(a)-y*math.sin(a);v=x*math.sin(a)+y*math.cos(a)
    return (u,v*math.cos(b)-z*math.sin(b),v*math.sin(b)+z*math.cos(b))


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=OUT)
    parser.add_argument('--part',action='append',help='Exact part name; default prepares all eight wet bodies')
    parser.add_argument('--slice',action='append',default=[],help='Exact prepared part to slice offline; repeat as needed')
    parser.add_argument('--slice-all',action='store_true',help='Slice every selected project offline')
    args=parser.parse_args();OUT=args.out.resolve()
    declared=decode(json.loads((ROOT/'hardware/manifold-layout/enclosure-box.json').read_text()))['box']
    plate=declared['pack']['collet_plate'];layouts=fixed_returns.layouts(plate)
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'plate-used.json').write_text(json.dumps(plate,indent=2)+'\n')
    import flow_roof
    sources=[Path(m.__file__) for m in (fixed_returns,pump_receiver,pump_return,flow_roof)]
    sources+=[ROOT/'hardware/manifold-layout/enclosure-box.json',Path(__file__)]
    bindings={str(p.relative_to(ROOT)):sha(p) for p in sources}
    choices=[]
    stations=('west-outer','west-inner','east-inner','east-outer')
    for station,(x,z) in zip(stations,plate['holes']):
        for kind in ('receiver','return'):choices.append(('enclosure-pump-'+kind+'-'+station,kind,x))
    known={name for name,_,_ in choices}
    if set(args.part or [])-known or set(args.slice)-known:parser.error('Unknown part name')
    if args.part and set(args.slice)-set(args.part):parser.error('Each --slice name must also be selected by --part')
    slices=set(args.slice)
    if args.slice_all:slices.update(args.part or known)
    records={}
    for name,kind,x in choices:
        if args.part and name not in args.part:continue
        data=layouts[str(x)]
        if kind=='receiver':
            z=dict(plate['holes'])[x];local=pump_receiver._local_junction(data['junction'],(x,plate['fore_y'],z))
            shape=pump_receiver.geometry(junction=local)
            zrot,xrot=pump_receiver.print_rotations(local)
            ports={key+'-'+field:local[key][field] for key in ('lower','upper') for field in ('point','tube_stop')}
            ports['pump-inlet']=(0.,0.,0.)
        else:
            shape=pump_return.geometry(data['return']);zrot,xrot=0.,-45.
            ports={key+'-'+field:shape['layout'][key][field] for key in ('input','output') for field in ('point','tube_stop')}
        body=shape['body'].rotate((0,0,0),(0,0,1),zrot).rotate((0,0,0),(1,0,0),xrot)
        void=shape['void'].rotate((0,0,0),(0,0,1),zrot).rotate((0,0,0),(1,0,0),xrot)
        records[name]=prepare(name,body,void,bindings,{'rotate_z_degrees':zrot,'rotate_x_degrees':xrot,'bed':'Native body minimum Z to0',
                'ports_before_bedding_mm':{key:rotate_point(value,zrot,xrot) for key,value in ports.items()}},
            pump_receiver.engineering_record() if kind=='receiver' else pump_return.engineering_record(),slice_native=name in slices)
    (OUT/'preparation-index.json').write_text(json.dumps({'scope':'Manual offline preparation, one normal object per plate. No printer API. Native slicing occurs only with --slice or --slice-all. Support and free-strand paths require review; no physical clean-bore acceptance.','plate_snapshot':'plate-used.json','plate_snapshot_sha256':sha(OUT/'plate-used.json'),'parts':records},indent=2)+'\n')

if __name__=='__main__':main()
