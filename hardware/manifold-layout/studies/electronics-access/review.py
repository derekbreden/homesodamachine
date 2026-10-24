"""Manually query the fastened panel and moved inlet against installed bodies.

This is an on-demand arrangement question, not a build/commit gate. The screw
threads, heatset press fits and integral back-top stock joins are named mates.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

import fcl
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('access_fit_scene',HERE/'study.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)


def obj(mesh):
    v,f=mesh;model=fcl.BVHModel();model.beginModel(len(v),len(f))
    model.addSubModel(v,f.astype(np.int32));model.endModel()
    return fcl.CollisionObject(model)


def overlaps(a,b):
    return not np.any(np.minimum(a.max(0),b.max(0))-np.maximum(a.min(0),b.min(0))<.001)


def main():
    g=study.library();scene=study.pose(g);meshes=study.base.world_meshes(scene,g)
    rows={m['name']:m for m in scene['instances'] if not m.get('render_only')}
    objects={name:obj(meshes[name]) for name in rows}
    intended={frozenset((m['a'],m['b'])) for m in scene['mates']}
    intended|={frozenset(('ceiling',name)) for name in ('left-wall','right-wall','back-wall')}
    changed={'ceiling','back-wall','c14-inlet','electronics-access-panel',
             *[n for n in rows if n.startswith(('access-screw-','access-insert-'))]}
    checked=set();hits=[]
    for a in sorted(changed):
        for b in rows:
            pair=frozenset((a,b))
            if a==b or pair in checked or pair in intended:continue
            checked.add(pair)
            if overlaps(meshes[a][0],meshes[b][0]) and fcl.collide(objects[a],objects[b],fcl.CollisionRequest(),fcl.CollisionResult()):hits.append([a,b])
    motion=[];v,f=meshes['electronics-access-panel']
    for lift in (0.,.1,1.,3.,9.,30.,70.):
        moved=(v+[0,0,lift],f);moving=obj(moved);blocked=[]
        for name in rows:
            if name=='electronics-access-panel' or name.startswith('access-screw-'):continue
            if lift==0 and frozenset(('electronics-access-panel',name)) in intended:continue
            if overlaps(moved[0],meshes[name][0]) and fcl.collide(moving,objects[name],fcl.CollisionRequest(),fcl.CollisionResult()):blocked.append(name)
        motion.append({'lift_mm':lift,'equipment_intersections':blocked})
    c14=meshes['c14-inlet'][0];boss=obj(meshes['access-boss-highlight-2'])
    report={'scope':'Only changed panel, integral bosses, rear-wall opening, C14 and fasteners against the complete stationary selected arrangement. Threads/press fits and integral wall joins are intended mates.',
        'hard_interferences':[pair for pair in hits if not any(n.startswith('local-lead-') for n in pair)],
        'flexible_lead_estimate_interferences':[pair for pair in hits if any(n.startswith('local-lead-') for n in pair)],
        'panel_removal_order':'Remove the four M3 screws, then lift the empty panel',
        'panel_lift':motion,'equipment_assigned_to_panel':[],
        'front_right_boss_to_vent_adapter_mm':float(fcl.distance(obj(meshes['access-boss-highlight-1']),objects['vent-sleeve'],fcl.DistanceRequest(),fcl.DistanceResult())),
        'c14':{'flange_centre_mm':study.plan()['c14']['flange_centre_mm'],
               'translation_from_parent_mm':study.plan()['c14']['translation_from_parent_mm'],
               'left_wall_gap_mm':float(c14[:,0].min()+98.5),
               'ordinary_ceiling_gap_mm':float(346-c14[:,2].max()),
               'rear_left_boss_gap_mm':float(fcl.distance(objects['c14-inlet'],boss,fcl.DistanceRequest(),fcl.DistanceResult()))},
        'study_meshes_sha256':{str(path.relative_to(HERE)):hashlib.sha256(path.read_bytes()).hexdigest()
                                for path in sorted((HERE/'parts').glob('*.npz'))},
        'input_scene_sha256':hashlib.sha256((HERE.parent/'funnel-gate/study.json').read_bytes()).hexdigest()}
    (HERE/'arrangement-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='study_meshes_sha256'},indent=2))


if __name__=='__main__':main()
