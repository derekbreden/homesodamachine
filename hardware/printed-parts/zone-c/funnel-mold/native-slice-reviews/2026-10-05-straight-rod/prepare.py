"""Read current native mould geometry and clone its frozen recipe without producers."""
from pathlib import Path
import hashlib, json, os, sys, zipfile
import xml.etree.ElementTree as ET

os.environ.setdefault('HSM_NO_BUILD_LOCK', '1')
import cadquery as cq
import numpy as np
import trimesh
from scipy.spatial import cKDTree

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
HERE = ROOT/'.cache/funnel-simple-2026-10-05/shells'
HERE.mkdir(parents=True, exist_ok=True)
MODELS = ROOT/'hardware/printed-parts/zone-c/funnel-mold'
FUNNEL = ROOT/'hardware/printed-parts/zone-c/funnel/funnel.step'
sys.path.insert(0, str(ROOT/'tools/funnel-mold-print'))
from profiles import CORE, PROD, mesh_object, metadata, qn

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def bounds(s):
    b = s.BoundingBox()
    return [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax]

def difference(a, b):
    return {'actual_minus_reference_mm3': a.cut(b).Volume(),
            'reference_minus_actual_mm3': b.cut(a).Volume()}

info = json.loads((MODELS/'design.json').read_text())
containment = json.loads((MODELS/'containment-review.json').read_text())
assert containment['contained']
assert all(sha(MODELS/n) == digest for n, digest in containment['sha256'].items())
shapes = {n:cq.importers.importStep(str(MODELS/(n+'.step'))).val()
          for n in ('cavity','core','funnel','rod')}
finished = cq.importers.importStep(str(FUNNEL)).val()
native = {n:{'sha256':sha(MODELS/(n+'.step')), 'valid':s.isValid(),
             'solids':len(s.Solids()), 'bounds_mm':bounds(s),
             'volume_mm3':s.Volume()} for n,s in shapes.items()}
assert all(row['valid'] and row['solids'] == 1 for row in native.values())
shift_z = shapes['funnel'].BoundingBox().zmin - finished.BoundingBox().zmin
cast = shapes['funnel'].translate((0,0,-shift_z))
cast_diff = difference(cast, finished)
assert max(cast_diff.values()) < 0.0001, cast_diff
print('casting vs finished', cast_diff, 'mould Z shift', shift_z, flush=True)
floor = finished.BoundingBox().zmin
neck = info['rod_support']['guide_top_mm']-shift_z-8.0
probe_rows = []
for label,z in [('lower-bore',floor+.5),('middle-bore',(floor+neck)/2),
                ('upper-bore',neck-.5)]:
    for radius,present in [(2.99,False),(3.10,True)]:
        point = cq.Vector(1.85+radius,0,z)
        actual = bool(finished.isInside(point,1e-7))
        assert actual == present, (label,radius,actual)
        assert bool(cast.isInside(point,1e-7)) == actual
        probe_rows.append({'feature':label,'probe_xyz_mm':point.toTuple(),
                           'finished_silicone_at_point':actual,
                           'casting_silicone_at_point':actual})

template = MODELS/'funnel-mold.3mf'
with zipfile.ZipFile(template) as z:
    payloads = {n:z.read(n) for n in z.namelist()}
assert not any(n.endswith('.gcode') for n in payloads)
settings_bytes = payloads['Metadata/project_settings.config']
settings = json.loads(settings_bytes)
model = ET.fromstring(payloads['3D/3dmodel.model'])
config = ET.fromstring(payloads['Metadata/model_settings.config'])
prepared = []
for index,name in enumerate(('cavity','core'),1):
    path = MODELS/(name+'.stl')
    mesh = trimesh.load(path, force='mesh', process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count == 1
    center = mesh.bounds.mean(axis=0)
    part_id, object_id = str(index*2-1), str(index*2)
    member = f'3D/Objects/object_{index}.model'
    old_obj = next(ET.fromstring(payloads[member]).iter(qn('object')))
    sub = ET.Element(qn('model'), unit='millimeter')
    resources = ET.SubElement(sub,qn('resources'))
    mesh_object(resources,part_id,mesh,center)
    obj = resources.find(qn('object'))
    obj.attrib.update(old_obj.attrib)
    payloads[member] = ET.tostring(sub,xml_declaration=True,encoding='UTF-8')
    item = model.find(qn('build')).find(f"{qn('item')}[@objectid='{object_id}']")
    transform = [float(v) for v in item.attrib['transform'].split()]
    rotation = np.array(transform[:9]).reshape(3,3)
    local_points = mesh.vertices-center
    transform[11] = -float((local_points@rotation)[:,2].min())
    item.set('transform',' '.join(f'{v:.12g}' for v in transform))
    object_settings = config.find(f"object[@id='{object_id}']")
    part = object_settings.find('part')
    for key,value in zip(('source_offset_x','source_offset_y','source_offset_z'),center):
        metadata(part,key,f'{value:.12g}')
    for node in (object_settings.find('metadata[@face_count]'),part.find('mesh_stat')):
        node.set('face_count',str(len(mesh.faces)))
    for a in config.findall(f"assemble/assemble_item[@object_id='{object_id}'][@instance_id]"):
        t=[float(v) for v in a.attrib['transform'].split()]
        t[11]=transform[11]
        a.set('transform',' '.join(f'{v:.12g}' for v in t))
    plate_points=local_points@rotation+np.array(transform[9:12])
    plate_bounds=np.vstack((plate_points.min(axis=0),plate_points.max(axis=0)))
    bed_bounds = plate_bounds.copy()
    bed_bounds[:,0] -= 396*(index-1)
    inside = np.all(bed_bounds[0]>=np.array([0,0,-1e-6])) and np.all(bed_bounds[1]<=np.array([299,320,325])+1e-6)
    assert inside,bed_bounds
    vertices=np.array([[float(v.attrib[k]) for k in ('x','y','z')]
                       for v in resources.iter(qn('vertex'))])+center
    distance=float(cKDTree(mesh.vertices).query(vertices)[0].max())
    assert distance<1e-6
    prepared.append({'part':name,'plate':index,'stl_sha256':sha(path),
       'mesh_watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),
       'mesh_bodies':int(mesh.body_count),'triangles':int(len(mesh.faces)),
       'embedded_maximum_vertex_distance_mm':distance,'transform':transform,
       'source_center_mm':center.tolist(),'local_bed_bounds_mm':bed_bounds.tolist(),
       'model_within_bed':bool(inside),'orientation':'upright' if name=='cavity' else 'inverted'})
payloads['3D/3dmodel.model']=ET.tostring(model,xml_declaration=True,encoding='UTF-8')
payloads['Metadata/model_settings.config']=ET.tostring(config,xml_declaration=True,encoding='UTF-8')
destination=HERE/'current-funnel-mould-petg088.3mf'
with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as out:
    for n,p in payloads.items():out.writestr(n,p)
with zipfile.ZipFile(destination) as z:
    assert z.read('Metadata/project_settings.config')==settings_bytes
record={'checked_date':'2026-10-05','method':'Current native STEP/STL reads, hash-exact containment binding and separate mesh-refreshed copy of frozen project settings.',
 'native_geometry':native,'design_sha256':sha(MODELS/'design.json'),
 'containment_review_sha256':sha(MODELS/'containment-review.json'),
 'all_containment_bindings_current':True,'containment_pass':containment['contained'],
 'minimum_cavity_backing_mm':info['minimum_cavity_backing_mm'],
 'minimum_core_backing_mm':info['minimum_core_backing_mm'],
 'finished_funnel_step_sha256':sha(FUNNEL),'mould_z_translation_mm':shift_z,
 'casting_vs_finished':cast_diff,'bore_probe_rows':probe_rows,
 'casting_scope':info['casting_scope'],'complete_tooling':True,
 'tooling':'Two PETG shells and a stock straight 6 x 25 mm stainless steel rod.',
 'template_project_sha256':sha(template),'template_project':str(template.relative_to(ROOT)),
 'current_project':str(destination.relative_to(ROOT)),'current_project_sha256':sha(destination),
 'project_settings_payload_sha256':hashlib.sha256(settings_bytes).hexdigest(),
 'settings_byte_identical_to_frozen_template':True,'prepared_plates':prepared,
 'selected_recipe':{k:settings[k] for k in ('printer_settings_id','print_settings_id','filament_settings_id',
    'nozzle_diameter','nozzle_volume_type','filament_volume_map','curr_bed_type','layer_height',
    'initial_layer_print_height','wall_loops','sparse_infill_density','support_type','support_style',
    'support_top_z_distance','support_bottom_z_distance','support_object_xy_distance',
    'filament_flow_ratio','filament_max_volumetric_speed')},
 'physical_scope':'The September 18 cavity print supports the retained PETG recipe and its remaining roughness. Geometry and slice checks cover the current two shells; they do not measure cast release or the silicone seal.',
 'native_slice_pending':True}
(HERE/'preparation-review.json').write_text(json.dumps(record,indent=2)+'\n')
print(destination,flush=True)
print(json.dumps({'native':native,'bores':probe_rows,'plates':prepared},indent=2),flush=True)
