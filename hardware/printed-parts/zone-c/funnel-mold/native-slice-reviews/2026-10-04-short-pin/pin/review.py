"""Verify one current native forming-mandrel slice and its emitted axial details."""
from pathlib import Path
import argparse, hashlib, json, math, re, sys, xml.etree.ElementTree as ET, zipfile
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from shapely.geometry import LineString
from shapely.ops import unary_union

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
PUBLIC=Path(__file__).resolve().parent
WORK=ROOT/'.cache/funnel-short-pin-2026-10-04/pin'
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'tools/funnel-mold-print'),str(PUBLIC)]
import enclosure_support_audit as support
from profiles import equivalent
from verify_print import embedded_mesh
from read_paths import read,outer_radii
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--version',default='v1')
parser.add_argument('--relief-local-z-min',type=float,required=True)
parser.add_argument('--relief-local-z-max',type=float,required=True)
parser.add_argument('--land-local-z-min',type=float,required=True)
parser.add_argument('--land-local-z-max',type=float,required=True)
args=parser.parse_args()
prep=json.loads((WORK/('preparation-'+args.version+'.json')).read_text())
project=ROOT/prep['project'];ready=ROOT/prep['slice_directory']
archive=ready/(project.stem+'.gcode.3mf')
result=json.loads((ready/'result.json').read_text())
assert result['return_code']==0 and len(result['sliced_plates'])==1,result
plate,=result['sliced_plates'];assert not plate['warning_message'],plate
assert sha(ROOT/prep['source_stl'])==prep['source_stl_sha256']
assert sha(ROOT/prep['source_step'])==prep['source_step_sha256']
with zipfile.ZipFile(project)as z:input_settings=json.loads(z.read('Metadata/project_settings.config'))
with zipfile.ZipFile(archive)as z:
    assert z.testzip() is None
    settings=json.loads(z.read('Metadata/project_settings.config'))
    changes={k:{'input':input_settings.get(k),'sliced':settings.get(k)}for k in input_settings.keys()|settings.keys()if input_settings.get(k)!=settings.get(k)}
    essential={k for k in input_settings if k not in ('filament_prime_volume','filament_map_2','extruder_nozzle_stats','extruder_nozzle_stats_new')}
    assert all(equivalent(k,input_settings[k],settings[k])for k in essential),(changes)
    nozzle=ET.fromstring(z.read('Metadata/slice_info.config')).find('plate').findall('nozzle')
    assert [n.attrib for n in nozzle]==[{'id':'0','extruder_id':'1','nozzle_diameter':'0.4','volume_type':'Standard'}]
    mesh_check=embedded_mesh(z,'2',ROOT/prep['source_stl'])
    raw=z.read('Metadata/plate_1.gcode')
    assert hashlib.md5(raw).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
    gpath=ready/'plate_1.gcode';gpath.write_bytes(raw)
    (PUBLIC/'native-preview.png').write_bytes(z.read('Metadata/plate_1.png'))
gcode=raw.decode()
trims=[line.strip()for line in gcode.splitlines()if line.strip().startswith('G29.1 Z')]
assert 'G29.1 Z0.16'in trims,trims
data=read(gpath)
shape=cq.importers.importStep(str(ROOT/prep['source_step'])).val()
finished_path=(ROOT/prep['source_step']).with_name('forming-mandrel-finished.step')
finished_shape=cq.importers.importStep(str(finished_path)).val()
tool_dir=finished_path.parent
tool_inputs={str(p.relative_to(ROOT)):sha(p) for p in [
    ROOT/prep['source_step'],ROOT/prep['source_stl'],finished_path,
    tool_dir/'forming-mandrel-design.json',tool_dir/'forming-mandrel-check.json']}
tool_check=json.loads((tool_dir/'forming-mandrel-check.json').read_text())
assert all(sha(tool_dir/name)==digest for name,digest in tool_check['sha256'].items()),'Tool check has stale input bindings'
assert tool_check['geometry_forms_complete_finished_funnel']
assert not tool_check['physical_casting_qualified']
tool_design=json.loads((tool_dir/'forming-mandrel-design.json').read_text())
assert tool_design['recommended_fine_band_print_z_mm']==[
    prep['local_fine_band']['bed_z_min_mm'],prep['local_fine_band']['bed_z_max_mm']]
assert tool_design['recommended_fine_layer_height_mm']==prep['local_fine_band']['layer_height_mm']
assert tool_design['recommended_pilot_alignment_layer']['print_z_range_mm']==prep['local_fine_band']['phase_alignment_range_z_mm']
assert tool_design['recommended_pilot_alignment_layer']['layer_height_mm']==prep['local_fine_band']['phase_alignment_layer_height_mm']
b=shape.BoundingBox();axis=np.array([(b.xmin+b.xmax)/2,(b.ymin+b.ymax)/2])
translation=np.array(prep['source_to_bed_translation_mm']);bedaxis=axis+translation[:2]
radial=outer_radii(data,bedaxis)
def native_radius(z,target=shape):
    low=0.;high=max(b.xlen,b.ylen)
    assert target.isInside(cq.Vector(axis[0],axis[1],z),1e-7)
    for _ in range(35):
        mid=(low+high)/2
        if target.isInside(cq.Vector(axis[0]+mid,axis[1],z),1e-7):low=mid
        else:high=mid
    return (low+high)/2
for row in radial.values():
    row['source_centre_z_mm']=row['centre_z_mm']-translation[2]
    row['native_outer_radius_at_layer_centre_mm']=native_radius(row['source_centre_z_mm'])
    row['finished_reference_radius_at_layer_centre_mm']=native_radius(row['source_centre_z_mm'],finished_shape)
    row['nominal_bead_radius_error_min_mm']=row['nominal_outer_surface_radius_min_mm']-row['native_outer_radius_at_layer_centre_mm']
    row['nominal_bead_radius_error_max_mm']=row['nominal_outer_surface_radius_max_mm']-row['native_outer_radius_at_layer_centre_mm']
    row['nominal_radial_growth_to_finished_min_mm']=row['finished_reference_radius_at_layer_centre_mm']-row['nominal_outer_surface_radius_max_mm']
    row['nominal_radial_growth_to_finished_max_mm']=row['finished_reference_radius_at_layer_centre_mm']-row['nominal_outer_surface_radius_min_mm']
def zone(low,high):
    rows=[{'layer':number,**row}for number,row in radial.items()if low+1e-6<row['source_centre_z_mm']<high-1e-6]
    assert rows,(low,high)
    return {'source_z_min_mm':low,'source_z_max_mm':high,'axial_length_mm':high-low,
            'emitted_model_layers':rows,'layer_count':len(rows),
            'max_layer_height_mm':max(r['height_mm']for r in rows),
            'nominal_deposited_z_range_mm':[min(r['top_z_mm']-r['height_mm']for r in rows),max(r['top_z_mm']for r in rows)],
            'nominal_radial_growth_to_finished_range_mm':[min(r['nominal_radial_growth_to_finished_min_mm']for r in rows),max(r['nominal_radial_growth_to_finished_max_mm']for r in rows)],
            'nominal_raw_surface_error_range_mm':[min(r['nominal_bead_radius_error_min_mm']for r in rows),max(r['nominal_bead_radius_error_max_mm']for r in rows)]}
relief=zone(args.relief_local_z_min,args.relief_local_z_max)
land=zone(args.land_local_z_min,args.land_local_z_max)
entry=zone(1.5,3.3)
assert relief['layer_count']>=2 and relief['max_layer_height_mm']<=.08001,relief
assert land['max_layer_height_mm']<=.08001,land
assert max(abs(v)for v in relief['nominal_raw_surface_error_range_mm'])<.065,relief
assert max(abs(v)for v in land['nominal_raw_surface_error_range_mm'])<.065,land
assert min(relief['nominal_radial_growth_to_finished_range_mm'])>0
assert min(land['nominal_radial_growth_to_finished_range_mm'])>0
def entry_underside(target):
    faces=[]
    for face in target.Faces():
        if face.geomType()!='PLANE':continue
        bb=face.BoundingBox();normal=face.normalAt()
        if normal.z<-.999 and bb.xlen>7 and bb.ylen>7 and bb.zmax<3.3:
            faces.append({'z_mm':face.Center().z,'area_mm2':face.Area(),
                          'bounds_mm':[bb.xmin,bb.ymin,bb.zmin,bb.xmax,bb.ymax,bb.zmax]})
    assert len(faces)==1,faces
    return faces[0]
raw_shoulder=entry_underside(shape)
finished_shoulder=entry_underside(finished_shape)
expanded_rows=[r for r in radial.values() if r['nominal_outer_surface_radius_max_mm']>3.8]
first_expanded=min(expanded_rows,key=lambda r:r['top_z_mm'])
emitted_shoulder_z=first_expanded['top_z_mm']-first_expanded['height_mm']-translation[2]
shoulder={'raw_native_underside':raw_shoulder,'finished_reference_underside':finished_shoulder,
          'first_expanded_model_layer_top_z_mm':first_expanded['top_z_mm'],
          'first_expanded_model_layer_height_mm':first_expanded['height_mm'],
          'nominal_emitted_underside_source_z_mm':emitted_shoulder_z,
          'nominal_underside_error_to_raw_mm':emitted_shoulder_z-raw_shoulder['z_mm'],
          'nominal_axial_growth_to_finished_mm':emitted_shoulder_z-finished_shoulder['z_mm']}
assert abs(shoulder['nominal_underside_error_to_raw_mm'])<.002,shoulder
bed=np.array([list(map(float,p.split('x')))for p in settings['extruder_printable_area'][0].split(',')])
limits=np.array(data['all_deposited_bounds_xy_mm'])
assert np.all(limits[0]>=bed.min(axis=0)) and np.all(limits[1]<=bed.max(axis=0))
model_segments=[s for s in data['segments']if not s['feature'].startswith('Support') and s['feature']not in ('Skirt','Brim')]
model_layers=sorted({s['layer']for s in model_segments})
assert model_layers[0]==1
assert abs(radial[model_layers[0]]['height_mm']-.20)<1e-6
def footprint(number):
    return unary_union([LineString([s['a'],s['b']]).buffer(s['width_mm']/2,quad_segs=8)for s in model_segments if s['layer']==number])
first=footprint(model_layers[0]);second=footprint(model_layers[1])
overlap=first.intersection(second).area
assert overlap>1,overlap
audit=support.audit(gpath,'funnel-mold/forming-mandrel',model=ROOT/prep['source_stl'],profile=project,coordinate_profile=project,include_unlabelled_support=True)
(PUBLIC/'support-topology.json').write_text(json.dumps(audit,indent=2)+'\n')
if audit['summary']['support_bodies']:
    assert audit['summary']['bed_rooted_bodies']==audit['summary']['support_bodies'],audit['summary']
shoulder['support_trees']=audit['trees']
shoulder['support_interfaces']=audit['interfaces']
shoulder['highest_native_support_interface_z_mm']=max(i['last_z_mm']for i in audit['interfaces'])
shoulder['nominal_emitted_model_to_interface_gap_mm']=emitted_shoulder_z-shoulder['highest_native_support_interface_z_mm']
fig,axes=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
for ax in axes:
    ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlabel('Bed X (mm)');ax.set_ylabel('Bed Y (mm)')
    ax.set_xlim(bedaxis[0]-12,bedaxis[0]+12);ax.set_ylim(bedaxis[1]-12,bedaxis[1]+12)
first_model=[s for s in data['segments']if s['layer']==1 and not s['feature'].startswith('Support') and s['feature']not in ('Skirt','Brim')]
first_support=[s for s in data['segments']if s['layer']==1 and s['feature'].startswith('Support')]
axes[0].add_collection(LineCollection([[s['a'],s['b']]for s in first_model],colors='#356b97',linewidths=.8))
axes[0].add_collection(LineCollection([[s['a'],s['b']]for s in first_support],colors='#e8903c',linewidths=.8))
axes[0].set_title('Complete first layer: model and support')
supports=[s for s in data['segments']if s['feature'].startswith('Support')]
interfaces=[s for s in supports if s['feature']=='Support interface']
axes[1].add_collection(LineCollection([[s['a'],s['b']]for s in supports],colors='#888888',linewidths=.3,alpha=.4))
axes[1].add_collection(LineCollection([[s['a'],s['b']]for s in interfaces],colors='#c04060',linewidths=.7))
axes[1].set_title('All native support paths and interfaces')
fig.savefig(PUBLIC/'native-supports.png',dpi=180);plt.close(fig)
fig,profile_axes=plt.subplots(1,2,figsize=(13,5),constrained_layout=True)
zs=[r['source_centre_z_mm']for r in radial.values()]
for ax in profile_axes:
    ax.plot(zs,[r['native_outer_radius_at_layer_centre_mm']for r in radial.values()],label='Native raw radius at layer centre',color='#222222')
    ax.plot(zs,[r['nominal_outer_surface_radius_max_mm']for r in radial.values()],label='Emitted nominal outer bead radius',color='#356b97',marker='.',ms=3)
    ax.plot(zs,[r['finished_reference_radius_at_layer_centre_mm']for r in radial.values()],label='Finished target radius',color='#777777',linestyle='--')
    ax.axvspan(args.relief_local_z_min,args.relief_local_z_max,alpha=.2,color='#e8903c',label='Relief band')
    ax.set_xlabel('Mandrel source Z (mm)');ax.set_ylabel('Radius (mm)');ax.grid(alpha=.2)
profile_axes[0].set_title('Complete emitted axial profile')
profile_axes[1].set_xlim(.9,7.2);profile_axes[1].set_title('Entry, relief and seal land');profile_axes[1].legend(fontsize=8)
fig.savefig(PUBLIC/'axial-profile.png',dpi=180);plt.close(fig)
record={'status':'native_slice_clear','date':'2026-10-04','preparation_sha256':sha(PUBLIC/'preparation.json'),
    'native_archive':str(archive.relative_to(ROOT)),'native_archive_sha256':sha(archive),
    'gcode_sha256':hashlib.sha256(raw).hexdigest(),'source_stl_sha256':prep['source_stl_sha256'],
    'source_step_sha256':prep['source_step_sha256'],'embedded_mesh':mesh_check,
    'finished_reference_step_sha256':sha(finished_path),
    'tooling_input_sha256':tool_inputs,
    'cli_return_code':result['return_code'],'slice_warning':plate['warning_message'],
    'estimated_seconds':plate['total_predication'],'estimated_filament_g':plate['filaments'][0]['total_used_g'],
    'fixed_left_standard_04_nozzle':True,'z_trim_commands':trims,'global_recipe_retained':True,
    'slicer_setting_normalizations':changes,'relief_band':relief,'seal_land':land,'entry_profile':entry,
    'all_layer_nominal_raw_radii':radial,'all_deposited_bounds_xy_mm':data['all_deposited_bounds_xy_mm'],
    'minimum_bed_edge_margin_mm':float(min(*(limits[0]-bed.min(axis=0)),*(bed.max(axis=0)-limits[1]))),
    'feature_segment_counts':data['feature_segment_counts'],
    'first_model_layer':model_layers[0],'first_model_layer_height_mm':radial[model_layers[0]]['height_mm'],
    'local_model_layer_schedule':[{'layer':n,**r}for n,r in radial.items()if r['top_z_mm']<=7.3],
    'first_second_model_deposited_overlap_mm2':overlap,
    'support_topology_summary':audit['summary'],'support_topology_sha256':sha(PUBLIC/'support-topology.json'),
    'entry_shoulder_support_contact':shoulder,
    'source_top_z_mm':prep['source_bounds_mm'][1][2],
    'last_emitted_model_top_z_mm':max(r['top_z_mm']for r in radial.values()),
    'support_removal_scope':'The flat, open raw entry-shoulder underside at native print Z1.54 receives the recorded bed-rooted support tree and exposed annular interface. Cut and detach that support from the radial sides; no enclosed cavity obstructs access. The complete emitted topology includes bodies without interface labels. Physical adhesion, clean removal and finished coating dimensions remain unqualified.',
    'nominal_bead_scope':'Paths are reconstructed with the slicer-reported width and height. They demonstrate feature survival and nominal material placement; calibrated flow, pressure and coating do not establish physical bead dimensions without a print.',
    'scope':'Fresh offline native short PETG pin review bound to the current blind-seat shell geometry. No printer submission or physical finished mandrel/cast-seal qualification.',
    'review_script_sha256':sha(__file__),'path_reader_sha256':sha(PUBLIC/'read_paths.py')}
assert all(sha(ROOT/p)==h for p,h in tool_inputs.items()),'Tooling inputs changed during review'
(PUBLIC/'readiness-review.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:record[k]for k in ['status','estimated_seconds','estimated_filament_g','relief_band','seal_land','support_topology_summary']},indent=2))
