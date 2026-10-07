"""Matched roof pockets and the relocated west-pull pan interface.

Reads the parent structure shell without changing its files. Receiver stock,
rear ports and low fixed geometry stay in their parent-controlled positions.
This post-process restores the obsolete pan aperture, opens the actual new
pan's full nine-millimetre wall bearing, and preserves the accepted C14
ceiling-pocket profile at its translated station.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import cadquery as cq

HERE=Path(__file__).resolve().parent
STUDY=HERE.parent
ROOT=STUDY.parents[1]
OUT=ROOT/'.cache/pump-first-layout/mounts'
sys.path.insert(0,str(STUDY))
import baseline

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def bounds(s):
    b=s.BoundingBox();return[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]

def common(a,b):
    return abs(a.intersect(b,tol=.0001).Volume(tol=1e-9))

def load(r):return cq.Shape.importBrep(str(ROOT/r['brep']))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pan-only',action='store_true')
    args=parser.parse_args()
    source_path=STUDY/'structure/candidate.json'
    source=json.loads(source_path.read_text())
    interfaces=json.loads((STUDY/'funnel/shells.json').read_text())['interfaces']
    mounts=({'parts':{},'expected_devices':{},'replacement_names':[]} if args.pan_only else json.loads((HERE/'candidate.json').read_text()))
    routing=json.loads((STUDY/'routing/candidate.json').read_text())
    # Parent can refresh its placement manifest before reattaching the already
    # published native shell. The exact shell path is stable across that cycle.
    shell_record=source['parts'].get('enclosure-back-top',{'brep':'.cache/pump-first-layout/structure/enclosure-back-top.brep'})
    back=load(shell_record)
    parent_back=back
    parent_shell_sha=hashlib.sha256((ROOT/shell_record['brep']).read_bytes()).hexdigest()
    # Restored obsolete pockets must never leave a fin beyond the original
    # Z355 exterior ceiling. The existing rounded native outline is retained.
    back=back.intersect(box(-150,150,0,500,0,355))
    back=back.cut(load(interfaces['original-c14-ceiling-pocket']).translate((-138,0,0)),tol=.0001)
    frame=json.loads((STUDY/'funnel/candidate.json').read_text())['parts']['funnel-frame']
    aft=frame.get('bounds_world_mm',frame.get('bounds'))[4]
    ceiling=box(-98.5,98.5,aft,465.3,343,352)
    pockets=[]
    for name,r in mounts['expected_devices'].items():
        s=load(r);b=s.BoundingBox()
        explicit=mounts.get('working_envelopes',{}).get(name,{}).get('roof_cutter')
        if explicit:
            p=load(explicit).intersect(ceiling)
            back=back.cut(p,tol=.0001)
            pockets.append({'owner':name,'roof_cutter_bounds':bounds(p),
              'closed_body_top_mm':b.zmax,'minimum_exterior_roof_cover_mm':355-p.BoundingBox().zmax})
            continue
        if name.startswith('relay-'):
            height=b.zmax+1
        elif name=='wago-reeds-b':
            height=b.zmax+1
        else:
            height=b.zmax+6.85+1
        if height>343:
            p=box(b.xmin-1,b.xmax+1,b.ymin-1,b.ymax+1,343,min(height,352)).intersect(ceiling)
            back=back.cut(p,tol=.0001)
            pockets.append({'owner':name,'roof_cutter_bounds':bounds(p),
                            'closed_body_top_mm':b.zmax,
                            'working_lever_envelope_top_mm':b.zmax+6.85 if name!='wago-reeds-b' and not name.startswith('relay-') else None,
                            'minimum_exterior_roof_cover_mm':355-min(height,352)})
    # The old aperture comes from the original native pan's exact bounds and
    # the source running/print-down allowances, rather than a guessed patch.
    old=baseline.read(['asse-drip-pan','enclosure-back-top'])
    o=old['asse-drip-pan'].BoundingBox()
    old_slot=box(-107.5,-98.5,o.ymin+4-.25,o.ymax-4+.25,o.zmin-.5,o.zmax+.25)
    back=back.fuse(old_slot,tol=.0001)
    pan=load(routing['parts']['asse-drip-pan']);b=pan.BoundingBox()
    if b.xmin < -107.501:
        raise ValueError(f'Pan protrudes beyond the215mm appliance envelope: {bounds(pan)}')
    slot=box(-107.51,-98.49,b.ymin+4-.25,b.ymax-4+.25,b.zmin-.5,b.zmax+.25)
    back=back.cut(slot,tol=.0001).clean()
    assert back.isValid() and len(back.Solids())==1
    checks=[{'test':'native back shell','valid':back.isValid(),'solids':len(back.Solids()),'pass_result':back.isValid() and len(back.Solids())==1}]
    joined=back
    for name in mounts.get('shell_fuse_part_names',[]):
        platform=load(mounts['parts'][name])
        joined=joined.fuse(platform,tol=.0001).clean()
        checks.append({'test':'actual platform joined to actual wall','part':name,'valid':joined.isValid(),'solids':len(joined.Solids()),'root_common_mm3':common(back,platform),'pass_result':joined.isValid() and len(joined.Solids())==1})
    for name,r in mounts['expected_devices'].items():
        volume=common(back,load(r))
        checks.append({'test':'roof/wall clears actual mounted device','part':name,'common_mm3':volume,'pass_result':volume<.001})
    for name,records in mounts.get('working_envelopes',{}).items():
        for kind in ['levers','entry_wire']:
            volume=common(back,load(records[kind]))
            checks.append({'test':'matched roof clears explicit working envelope','part':name,'kind':kind,
              'common_mm3':volume,'pass_result':volume<.001})
    c14=load(source['parts']['c14-inlet'])
    volume=common(back,c14)
    checks.append({'test':'translated accepted C14 ceiling profile clears actual inlet','common_mm3':volume,'pass_result':volume<.001})
    fixed_below=box(-150,150,0,500,0,253.4)
    new_low=back.intersect(fixed_below);old_low=parent_back.intersect(fixed_below)
    removed=abs(old_low.cut(new_low,tol=.0001).Volume(tol=1e-9));added=abs(new_low.cut(old_low,tol=.0001).Volume(tol=1e-9))
    checks.append({'test':'post-process preserves supplied lower shell below cold-core lid','added_mm3':added,'removed_mm3':removed,'pass_result':added<.001 and removed<.001})
    baseline_low=old['enclosure-back-top'].intersect(fixed_below)
    inherited_removed=abs(baseline_low.cut(old_low,tol=.0001).Volume(tol=1e-9))
    inherited_added=abs(old_low.cut(baseline_low,tol=.0001).Volume(tol=1e-9))
    poses=[]
    for settle in [0,-.5]:
        for travel in [0,.25,1,2,5,10,20,30,40,60,80,100,110]:
            moved=pan.translate((-travel,0,settle))
            v=common(back,moved)
            poses.append({'west_travel_mm':travel,'gravity_settlement_mm':settle,'common_with_shell_mm3':v,'pass_result':v<.001})
    checks.append({'test':'nominal and loaded west extraction','sampled_poses':len(poses),'pass_result':all(p['pass_result'] for p in poses)})
    OUT.mkdir(parents=True,exist_ok=True)
    suffix='-pan' if args.pan_only else ''
    path=OUT/f'enclosure-back-top{suffix}.brep';back.exportBrep(str(path))
    mesh=OUT/f'enclosure-back-top{suffix}.json';v,t=back.tessellate(.15,.1)
    mesh.write_text(json.dumps({'vertices':[[p.x,p.y,p.z] for p in v],'triangles':[list(q) for q in t]},separators=(',',':'))+'\n')
    joined_path=OUT/f'rear-shell-with-platform{suffix}.brep';joined.exportBrep(str(joined_path))
    record={'brep':str(path.relative_to(ROOT)),'mesh':str(mesh.relative_to(ROOT)),
            'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'role':'walls','bounds':bounds(back),
            'detail':'Native 9 mm west flank and full 6 mm rear wall; matching enlarged funnel, retained C14 profile, local working-connector roof pockets and matched west-pull pan bearing slot.'}
    mounts['parts']['enclosure-back-top']=record
    mounts['replacement_names']=sorted(set(mounts['replacement_names']+['enclosure-back-top']))
    mounts['shell_post']={'source_manifest_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
                         'source_native_shell_sha256':parent_shell_sha,
                         'inherited_parent_lower_shell_vs_baseline_mm3':{'added':inherited_added,'removed':inherited_removed},
                         'roof_pockets':pockets,'pan_brep_sha256':hashlib.sha256((ROOT/routing['parts']['asse-drip-pan']['brep']).read_bytes()).hexdigest(),
                         'pan_bounds':bounds(pan),'slot_cutter_bounds':bounds(slot),
                         'wall_bearing_span_mm':9,'nominal_lower_gap_mm':.5,
                         'gravity_settled_floor_mm':b.zmin-.5,'floor_to_retained_lid_mm':b.zmin-.5-253.4,
                         'pan_motion_poses':poses,'checks':checks,
                         'joined_printable_brep':str(joined_path.relative_to(ROOT)),
                         'pass_result':all(c['pass_result'] for c in checks)}
    mounts.setdefault('source_sha256',{})[str(Path(__file__).relative_to(ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE/('shell-pan-candidate.json' if args.pan_only else 'candidate.json')).write_text(json.dumps(mounts,indent=2)+'\n')
    (HERE/('shell-pan-post.json' if args.pan_only else 'shell-post.json')).write_text(json.dumps(mounts['shell_post'],indent=2)+'\n')
    print(json.dumps(mounts['shell_post']['checks'],indent=2),flush=True)
    assert mounts['shell_post']['pass_result'],[c for c in checks if not c['pass_result']]

if __name__=='__main__':main()
