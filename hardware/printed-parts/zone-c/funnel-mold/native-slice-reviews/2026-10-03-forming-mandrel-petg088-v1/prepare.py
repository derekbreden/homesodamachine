"""Clone the recorded mould recipe for one current native forming-mandrel mesh."""
from pathlib import Path
import argparse, hashlib, json, sys, xml.etree.ElementTree as ET, zipfile
import numpy as np
import trimesh

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
PUBLIC=Path(__file__).resolve().parent
WORK=ROOT/'.cache/funnel-block-seat/mandrel-readiness'
WORK.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools/funnel-mold-print'))
from profiles import mesh_object, metadata, qn, PROD

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--stl',type=Path,required=True)
parser.add_argument('--step',type=Path,required=True)
parser.add_argument('--fine-z-min',type=float,required=True)
parser.add_argument('--fine-z-max',type=float,required=True)
parser.add_argument('--version',default='v1')
parser.add_argument('--alignment-z-max',type=float)
args=parser.parse_args()
stl=args.stl.resolve();step=args.step.resolve()
template=ROOT/'hardware/printed-parts/zone-c/funnel-mold/funnel-mold.3mf'
mesh=trimesh.load(stl,force='mesh',process=True)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1
centre=mesh.bounds.mean(axis=0)
height=float(mesh.extents[2])
with zipfile.ZipFile(template)as archive:
    assert archive.testzip() is None
    payloads={n:archive.read(n)for n in archive.namelist()}
settings_bytes=payloads['Metadata/project_settings.config']
settings=json.loads(settings_bytes)
assert settings['filament_flow_ratio'][0]=='0.88'
assert settings['initial_layer_print_height']=='0.2' and settings['layer_height']=='0.24'
assert settings['filament_volume_map']==['0']
assert settings['nozzle_volume_type'][0]=='Standard' and settings['nozzle_diameter'][0]=='0.4'
assert settings['min_layer_height'][0]=='0.08'
assert settings['printer_settings_id']=='Bambu Lab H2C 0.4 Standard +0.18 Z trim'
assert 0<=args.fine_z_min<args.fine_z_max<=height+1e-5

model=ET.fromstring(payloads['3D/3dmodel.model'])
resources=model.find(qn('resources'))
for node in list(resources):
    if node.attrib['id']!='2':resources.remove(node)
build=model.find(qn('build'))
for node in list(build):
    if node.attrib['objectid']!='2':build.remove(node)
transform=[1,0,0,0,1,0,0,0,1,149.5,160,height/2]
item=next(iter(build));item.set('transform',' '.join(f'{v:.12g}'for v in transform))
for node in model.findall(qn('metadata')):
    if node.attrib.get('name')=='Title':node.text='Current funnel forming mandrel'
sub=ET.Element(qn('model'),unit='millimeter');subresources=ET.SubElement(sub,qn('resources'))
old=next(ET.fromstring(payloads['3D/Objects/object_1.model']).iter(qn('object')))
mesh_object(subresources,'1',mesh,centre);subresources.find(qn('object')).attrib.update(old.attrib)
payloads['3D/Objects/object_1.model']=ET.tostring(sub,encoding='UTF-8',xml_declaration=True)
payloads.pop('3D/Objects/object_2.model',None)

config=ET.fromstring(payloads['Metadata/model_settings.config'])
for node in list(config):
    if node.tag=='object' and node.attrib['id']!='2':config.remove(node)
    if node.tag=='plate' and node.find("metadata[@key='plater_id']").attrib['value']!='1':config.remove(node)
obj=config.find("object[@id='2']")
metadata(obj,'name','Current funnel forming mandrel')
obj.find('metadata[@face_count]').set('face_count',str(len(mesh.faces)))
part=obj.find('part');part.find('mesh_stat').set('face_count',str(len(mesh.faces)))
for key,value in {'name':'forming-mandrel','source_file':stl.name,
                  'source_offset_x':centre[0],'source_offset_y':centre[1],'source_offset_z':centre[2]}.items():
    metadata(part,key,f'{value:.12g}'if isinstance(value,(float,np.floating))else value)
plate=config.find('plate');metadata(plate,'plater_name','Current funnel forming mandrel')
metadata(plate,'filament_map_mode','Manual')
assemble=config.find('assemble')
for node in list(assemble):
    if node.attrib['object_id']!='2':assemble.remove(node)
    elif 'instance_id'in node.attrib:node.set('transform','1 0 0 0 1 0 0 0 1 0 0 '+f'{height/2:.12g}')
payloads['3D/3dmodel.model']=ET.tostring(model,encoding='UTF-8',xml_declaration=True)
payloads['Metadata/model_settings.config']=ET.tostring(config,encoding='UTF-8',xml_declaration=True)
rels=ET.fromstring(payloads['3D/_rels/3dmodel.model.rels'])
for node in list(rels):
    if node.attrib.get('Target')=='/3D/Objects/object_2.model':rels.remove(node)
payloads['3D/_rels/3dmodel.model.rels']=ET.tostring(rels,encoding='UTF-8',xml_declaration=True).replace(b'ns0:',b'').replace(b'xmlns:ns0=',b'xmlns=')
payloads['Metadata/filament_sequence.json']=json.dumps({'plate_1':{'nozzle_sequence':[],'optimal_assignment':[],'sequence':[]}}).encode()
payloads['Metadata/cut_information.xml']=b'<?xml version="1.0"?><objects/>'
ranges=ET.Element('objects');r=ET.SubElement(ranges,'object',id='1')
fine_start=args.fine_z_min
if args.alignment_z_max is not None:
    assert args.fine_z_min<args.alignment_z_max<1.0
    alignment=ET.SubElement(r,'range',min_z=f'{args.fine_z_min:.12g}',max_z=f'{args.alignment_z_max:.12g}')
    ET.SubElement(alignment,'option',opt_key='layer_height').text='0.14'
    fine_start=args.alignment_z_max
band=ET.SubElement(r,'range',min_z=f'{fine_start:.12g}',max_z=f'{args.fine_z_max:.12g}')
ET.SubElement(band,'option',opt_key='layer_height').text='0.08'
payloads['Metadata/layer_config_ranges.xml']=ET.tostring(ranges,encoding='UTF-8',xml_declaration=True)
stem='forming-mandrel-petg088-'+args.version
project=WORK/(stem+'.3mf')
with zipfile.ZipFile(project,'w',zipfile.ZIP_DEFLATED,compresslevel=6)as archive:
    for name,data in payloads.items():archive.writestr(name,data)
with zipfile.ZipFile(project)as archive:
    assert archive.testzip() is None
    assert archive.read('Metadata/project_settings.config')==settings_bytes
bed_points=mesh.vertices-centre+np.array(transform[9:12])
bed_bounds=np.vstack([bed_points.min(axis=0),bed_points.max(axis=0)])
assert np.all(bed_bounds[0]>=np.array([0,0,-1e-5])) and np.all(bed_bounds[1]<=[325,320,325])
ready=WORK/('slice-'+args.version);ready.mkdir(exist_ok=True)
command=['/Applications/BambuStudio.app/Contents/MacOS/BambuStudio','--slice','0',
         '--arrange','0','--orient','0','--outputdir',str(ready),'--export-3mf',stem+'.gcode.3mf',str(project)]
record={'status':'prepared_for_native_slice','source_stl':str(stl.relative_to(ROOT)),
    'source_stl_sha256':sha(stl),'source_step':str(step.relative_to(ROOT)),'source_step_sha256':sha(step),
    'source_bounds_mm':mesh.bounds.tolist(),'native_mesh_watertight':bool(mesh.is_watertight),
    'native_mesh_winding_consistent':bool(mesh.is_winding_consistent),'triangles':len(mesh.faces),
    'source_center_mm':centre.tolist(),'project':str(project.relative_to(ROOT)),'project_sha256':sha(project),
    'template':str(template.relative_to(ROOT)),'template_sha256':sha(template),
    'complete_global_settings_byte_identical_to_template':True,
    'global_settings_sha256':hashlib.sha256(settings_bytes).hexdigest(),
    'print_orientation':'Socket pilot down; source +Z up on bed.',
    'source_to_bed_translation_mm':(np.array(transform[9:12])-centre).tolist(),
    'model_bounds_on_bed_mm':bed_bounds.tolist(),
    'local_fine_band':{'bed_z_min_mm':args.fine_z_min,'bed_z_max_mm':args.fine_z_max,'layer_height_mm':.08,
        'phase_alignment_range_z_mm':[args.fine_z_min,args.alignment_z_max]if args.alignment_z_max else None,
        'phase_alignment_layer_height_mm':.14 if args.alignment_z_max else None,
        'phase_alignment_reason':'One layer in the uncoated socket pilot sets the wet-detail lattice so the expanded entry underside starts at native Z1.54 and the raw relief starts at Z3.30.'if args.alignment_z_max else None,
        'reason':'The raw axial relief band is approximately 0.165 mm; local 0.08 mm layers preserve multiple emitted layers across it while retaining the recorded recipe elsewhere.'},
    'requested_z_trim_mm':.18,'expected_textured_emitted_trim_mm':.16,
    'selected_recipe':{k:settings[k]for k in ['printer_settings_id','print_settings_id','filament_settings_id',
        'filament_flow_ratio','filament_max_volumetric_speed','nozzle_diameter','nozzle_volume_type','filament_volume_map',
        'layer_height','initial_layer_print_height','wall_loops','sparse_infill_density','support_type','support_style',
        'support_top_z_distance','support_object_xy_distance']},
    'slice_command':command,'slice_directory':str(ready.relative_to(ROOT)),
    'prepared_script_sha256':sha(__file__),'submitted':False,
    'scope':'Separate current native mandrel preparation; existing mould shell files and frozen print projects retain their scope. Physical forming-surface finish, coating and cast seal are unqualified.'}
(WORK/('preparation-'+args.version+'.json')).write_text(json.dumps(record,indent=2)+'\n')
(PUBLIC/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'project':str(project),'slice_command':command,'bed_bounds':bed_bounds.tolist()},indent=2))
