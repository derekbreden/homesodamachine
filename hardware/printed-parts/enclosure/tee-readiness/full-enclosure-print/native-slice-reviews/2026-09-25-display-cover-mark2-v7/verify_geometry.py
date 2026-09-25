"""Measure the cover-only snap translation against the fixed native housing."""
from pathlib import Path
import hashlib,json,sys
import cadquery as cq
import numpy as np
import trimesh

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').is_file())
JOB=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'hardware/printed-parts/enclosure/display-cover'),str(ROOT/'hardware/printed-parts/enclosure/enclosure'),str(ROOT/'hardware/scripts')]
import display_cover as cover
import enclosure as enc
import flute_payload as fp
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
paths=json.loads((JOB/'unchanged-housing-inputs.json').read_text())
for p,h in paths.items():assert sha(ROOT/p)==h,p
live=cover.build_display_cover().val()
saved=cq.importers.importStep(str(ROOT/'hardware/printed-parts/enclosure/display-cover/display-cover.step')).val()
old=cq.importers.importStep(str(JOB/'reference/display-cover.step')).val()
diff=lambda a,b:abs(a.cut(b).Volume())+abs(b.cut(a).Volume())
assert live.isValid() and len(live.Solids())==1
assert diff(live,saved)<1e-5
face_region=cq.Solid.makeBox(200,120,2.00001,cq.Vector(-100,-60,-2))
bezel_difference=diff(live.intersect(face_region),old.intersect(face_region))
assert bezel_difference<1e-5,bezel_difference
skirt_checks=[]
for side in (-1,1):
    region=cq.Solid.makeBox(40,40,20,cq.Vector(40 if side>0 else -80,-20,-22.00001))
    before=old.intersect(region).translate((-side*(cover.skirt_inset-0.3),0,0))
    after=live.intersect(region)
    difference=diff(before,after);assert difference<1e-5,difference
    skirt_checks.append({'side':side,'translation_x_mm':-side*(cover.skirt_inset-0.3),'symmetric_difference_mm3':difference})
outer=json.loads((ROOT/'hardware/manifold-layout/enclosure-box.json').read_text())['box']['outer']
plane=enc.display_plane(outer);loc=cq.Location(plane)
print('Reading fixed front-top STEP',flush=True)
housing=cq.importers.importStep(str(ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure-front-top.step')).val()
local_housing=housing.moved(loc.inverse)
region=cq.Solid.makeBox(150,105,25,cq.Vector(-75,-52.5,-23))
near=local_housing.intersect(region)
rows=[]
for lateral in (-cover.cover_slip,0.,cover.cover_slip):
    seated=live.translate((lateral,0,0));seated_volume=abs(near.intersect(seated).Volume())
    assert seated_volume<1e-5,(lateral,seated_volume)
    pulled=seated.translate((0,0,cover.retention.BEARING_SLIP+.01))
    caught=abs(near.intersect(pulled).Volume());assert caught>1e-5,(lateral,caught)
    rows.append({'lateral_shift_mm':lateral,'seated_intersection_mm3':seated_volume,'pull_out_probe_mm':cover.retention.BEARING_SLIP+.01,'retaining_intersection_mm3':caught})
mesh=trimesh.load_mesh(ROOT/'hardware/printed-parts/enclosure/display-cover/display-cover.stl')
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1
# Exact assembly placement carries the revised cover into the appliance viewer.
R=np.array([plane.xDir.toTuple(),plane.yDir.toTuple(),plane.zDir.toTuple()]).T;t=np.array(plane.origin.toTuple())
surface=fp.carried(fp.read_payload(ROOT/'hardware/printed-parts/enclosure/display-cover/display-cover.step.mesh')[0],(R,t))
host=ROOT/'hardware/manifold-layout/enclosure-assembly.step.mesh'
assert fp.payload_names(host).count('display-cover')==1
assert fp.graft(host,{'display-cover':surface},same_frame=True)==1
got=next(e for e in fp.read_payload(host) if e['name']=='display-cover')
assert np.allclose(got['pos'],surface['pos'],atol=.00003,rtol=0)
report={'unchanged_housing_inputs_sha256':paths,'source_export_equivalent':True,'bezel_window_thickness_and_outer_perimeter_unchanged':True,
        'bezel_symmetric_difference_mm3':bezel_difference,'skirt_translations':skirt_checks,'previous_trial_reference_step_sha256':sha(JOB/'reference/display-cover.step'),
        'cover_step_sha256':sha(ROOT/'hardware/printed-parts/enclosure/display-cover/display-cover.step'),
        'cover_stl_sha256':sha(ROOT/'hardware/printed-parts/enclosure/display-cover/display-cover.stl'),
        'bezel_size_mm':[cover.cover_x,cover.cover_slope,cover.dims.display_cover_thickness],
        'perimeter_clearance_mm':cover.cover_slip,'previous_trial_skirt_inset_each_mm':0.3,'additional_skirt_inset_each_mm':cover.skirt_inset-0.3,'skirt_inset_each_mm':cover.skirt_inset,'nominal_catch_overlap_mm':cover.catch_overlap,
        'minimum_catch_overlap_at_full_lateral_float_mm':cover.catch_overlap-cover.cover_slip,'glass_intersection_mm3':cover.glass_shadow(),
        'native_housing_seating_and_retention':rows,'mesh_watertight':True,'mesh_body_count':1,'mesh_triangle_count':len(mesh.faces),
        'appliance_cover_payload_updated':True,'assembly_rotation':R.tolist(),'assembly_translation_mm':t.tolist(),
        'physical_fit_or_retention_force_measured':False,'pass':True}
(JOB/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
