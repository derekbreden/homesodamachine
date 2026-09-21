"""Complete thicker pusher route against the frozen full carrier/wall fixture."""
import json
from pathlib import Path
import sys

import cadquery as cq
from carrier_spring_pusher import build,installed,sha,THICKNESS,HELD_SPRING_LENGTH
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
STUDY=ROOT/'hardware/printed-parts/enclosure/tee-carrier/simple-carrier-study'
sys.path.insert(0,str(STUDY))
from check_joint_motion import swept_overlap


def main():
    manifest=json.loads((STUDY/'artifact-manifest.json').read_text())
    required=['inputs/manifest.json','inputs/current-front-top/front-top.step',
        'left-concept.step','right-concept.step','fixed-cup-integral-extension.step',
        'inputs/placed-neighbors/manifest.json']
    for name in required:
        if sha(STUDY/name)!=manifest['files'][name]['sha256']:raise ValueError('Frozen fixture changed: '+name)
    I=json.loads((STUDY/'inputs/manifest.json').read_text())['interface']
    I['half_entry_staging_y']=33.0
    wall=cq.importers.importStep(str(STUDY/'inputs/current-front-top/front-top.step')).val()
    extension=cq.importers.importStep(str(STUDY/'fixed-cup-integral-extension.step')).val()
    wall=wall.fuse(extension).fuse(extension.mirror('YZ')).clean()
    halves={-1:cq.importers.importStep(str(STUDY/'left-concept.step')).val(),
             1:cq.importers.importStep(str(STUDY/'right-concept.step')).val()}
    neighbors=json.loads((STUDY/'inputs/placed-neighbors/manifest.json').read_text())
    tees=[]
    for name,row in neighbors['bodies'].items():
        if not name.startswith('tee-'):continue
        path=STUDY/'inputs/placed-neighbors'/row['brep']
        if sha(path)!=row['sha256']:raise ValueError('Native tee changed')
        tees.append(cq.Shape.importBrep(str(path)).translate((0,-I['connected_offset_y'],0)))
    obstacles=wall.fuse(*tees).clean()
    rows=[];lift_clearances=[];aft=I['aft_limit_offset_y'];stage=I['half_entry_staging_y']
    for side in (-1,1):
        tool=installed(I,side)
        shift=-side*I['half_entry_shift_x'];inset=-side*I['half_entry_shoulder_inset_x']
        poses=[(shift,210,70),(shift,stage,70),(shift,stage,0),(inset,stage,0),(inset,aft,0),(0,aft,0)]
        blockers=obstacles
        if side>0:blockers=blockers.fuse(halves[-1].translate((0,aft,0)))
        for a,b in zip(poses,poses[1:]):
            row={'side':side,'stage':'held-tool installation',**swept_overlap(tool,a,b,blockers)}
            rows.append(row);print(json.dumps(row),flush=True)
        withdraw=abs(I['spring_stations'][side>0]['x'])-82.10
        path=[(0,aft,0),(-side*withdraw,aft,0),(-side*withdraw,aft,70)]
        blockers=blockers.fuse(halves[side].translate((0,aft,0)))
        for a,b in zip(path,path[1:]):
            row={'side':side,'stage':'pusher removal',**swept_overlap(tool,a,b,blockers)}
            rows.append(row);print(json.dumps(row),flush=True)
        # The whole rectangular envelope encloses the tool throughout this
        # vertical lift, so its separation is a conservative native air bound.
        bb=tool.translate(path[1]).BoundingBox()
        lift_box=cq.Solid.makeBox(bb.xlen,bb.ylen,bb.zlen+70,
                                 cq.Vector(bb.xmin,bb.ymin,bb.zmin))
        lift_clearances.append({'side':side,'enclosing_lift_box_gap_mm':lift_box.distance(blockers),
                                'enclosing_lift_box_overlap_mm3':lift_box.intersect(blockers).Volume()})
    # The left spring is released before the right half enters. Its conservative
    # whole envelope must remain remote from that complete half/tool motion.
    left=I['spring_stations'][0];floor=left['seat_floor_y'];end=left['bore_floor_y']+aft
    spring=cq.Solid.makeCylinder(3.25,end-floor,cq.Vector(left['x'],floor,left['z']),cq.Vector(0,1,0))
    right=halves[1].fuse(installed(I,1))
    shift=-I['half_entry_shift_x'];inset=-I['half_entry_shoulder_inset_x']
    poses=[(shift,210,70),(shift,stage,70),(shift,stage,0),(inset,stage,0),(inset,aft,0),(0,aft,0)]
    for a,b in zip(poses,poses[1:]):
        row={'side':1,'stage':'right half and tool versus released left spring',**swept_overlap(right,a,b,spring)}
        rows.append(row);print(json.dumps(row),flush=True)
    all_clear=all(r['initial_overlap_mm3']<1e-5 and r['max_prism_overlap_mm3']<1e-5 for r in rows)
    tip=I['spring_stations'][1]['bore_floor_y']+aft-HELD_SPRING_LENGTH
    report={'status':'frozen_native_pusher_route_pass' if all_clear else 'native_route_failure',
        'source_sha256':{str((HERE/'carrier_spring_pusher.py').relative_to(ROOT)):sha(HERE/'carrier_spring_pusher.py'),str(Path(__file__).relative_to(ROOT)):sha(__file__)},
        'frozen_carrier_manifest_sha256':sha(STUDY/'artifact-manifest.json'),
        'frozen_front_top_sha256':sha(STUDY/'inputs/current-front-top/front-top.step'),
        'sweeps':rows,'all_native_sweeps_clear':all_clear,
        'quantity_required':1,'simultaneous_two_spring_tool_hold_required':False,
        'reuse_basis':'Left spring expands into its closed cups at the aft stop before the same pusher loads the right half. Right half/tool motion clears the released left spring envelope.',
        'fixed_cup_front_air_at_removal_mm':tip-THICKNESS-(floor+8),
        'pusher_lift_conservative_native_air':lift_clearances,
        'assembly_order':['Preload left spring','Seat left half','Withdraw and lift pusher','Turn pusher 180 degrees about spring axis','Preload right spring','Seat right half','Withdraw and lift pusher'],
        'limits':['Actual compression force, tool stiffness and hand effort are unmeasured.','Native tool geometry does not model fingers or plier jaws.','Fresh Box-dependent route check remains pending the full enclosure generation.']}
    (HERE/'native-sequence-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'clear':all_clear,'quantity':1,'fore_air_mm':report['fixed_cup_front_air_at_removal_mm']},indent=2))
    if not all_clear:raise SystemExit(1)


if __name__=='__main__':main()
