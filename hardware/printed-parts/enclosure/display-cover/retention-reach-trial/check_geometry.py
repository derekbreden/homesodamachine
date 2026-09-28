"""Measure the two covers against the fixed, physically tested receiver and cover."""
import hashlib
import json
from pathlib import Path

import cadquery as cq
import trimesh
import retention_reach_trial as trial

base, HERE, ROOT = trial.base, trial.HERE, trial.ROOT
volume = lambda body: abs(body.Volume())
delta = lambda a,b: volume(a.cut(b))+volume(b.cut(a))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()

reference = cq.importers.importStep(str(base.HERE/(base.COVER_NAME+'.step'))).val()
receiver = base.receiver_surround()
unchanged = base.box(-80,80,-60,60,-5,.01)
reference_hook = reference.intersect(base.box(-80,80,-60,60,-20,-base.SHOULDER_DEPTH))
readings = {}
for name, extra in trial.VARIANTS.items():
    body = cq.importers.importStep(str(HERE/(name+'.step'))).val()
    increase = extra-base.EXTRA_REACH
    assert body.isValid() and len(body.Solids()) == 1
    assert delta(body,trial.build_cover(extra)) < 1e-5
    symmetry = {plane:delta(body,body.mirror(plane)) for plane in ('YZ','XZ')}
    assert max(symmetry.values()) < 1e-5
    root_delta = delta(body.intersect(unchanged),reference.intersect(unchanged))
    assert root_delta < 1e-5
    hook = body.intersect(base.box(-80,80,-60,60,-20,-trial.shoulder(extra)))
    hook_delta = delta(hook.translate((0,0,increase)),reference_hook)
    assert hook_delta < 1e-5
    assert volume(body.intersect(receiver)) < 1e-5
    clearance = trial.shoulder(extra)-base.CATCH
    bearings=[]
    for side in (-1,1):
        leaf=trial.skirt(side,extra)
        before=volume(receiver.intersect(leaf.translate((0,0,clearance-.01))))
        caught=volume(receiver.intersect(leaf.translate((0,0,clearance+.01))))
        assert before < 1e-5
        assert abs(caught/.01-base.OVERLAP*base.SPAN) < 1e-4
        bearings.append({'side':side,'engaged_area_mm2':caught/.01})
    mesh=trimesh.load_mesh(HERE/(name+'.stl'))
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.body_count==1
    readings[name]={'extra_arm_reach_mm':extra,'increase_from_tested_cover_mm':increase,
        'shoulder_depth_mm':trial.shoulder(extra),'tip_depth_mm':trial.tip(extra),
        'nominal_bearing_clearance_mm':clearance,'symmetry_difference_mm3':symmetry,
        'bezel_and_root_difference_mm3':root_delta,'translated_hook_difference_mm3':hook_delta,
        'seated_receiver_intersection_mm3':volume(body.intersect(receiver)),
        'hook_bearings':bearings,'watertight':True,'one_body':True,'triangles':len(mesh.faces)}
paths=[Path(__file__),HERE/'retention_reach_trial.py',base.HERE/'retention_trial.py',
       base.HERE/(base.COVER_NAME+'.step'),base.HERE/(base.RECEIVER_NAME+'.step'),
       base.HERE/(base.RECEIVER_NAME+'.stl')]
paths += [HERE/(name+ext) for name in trial.VARIANTS for ext in ('.step','.stl')]
report={'pass':True,'variants':readings,'fixed_receiver':base.RECEIVER_NAME,
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in paths},
        'scope':'Exact arm extension, preserved hook/bezel/root geometry, symmetry and nominal seating/engagement. Printed force and surface roughness require the physical trial.'}
(HERE/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(readings,indent=2))
