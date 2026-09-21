"""Current native front-top, integral fixed cups and complete carrier paths."""
import json
from pathlib import Path
import cadquery as cq
from build_concept import build,box,sha,bounds
from check_joint_motion import swept_overlap,disjoint

HERE=Path(__file__).resolve().parent


def main():
    M,I,plain,blank,L,R,Rrigid,flexwall,lip,*_=build()
    d=HERE/'inputs/current-front-top'
    fm=json.loads((d/'manifest.json').read_text())
    for name,digest in fm['files'].items():assert sha(d/name)==digest
    wall=cq.importers.importStep(str(d/'front-top.step')).val()
    report={'scope':'Current measured-tee native front-top with only the declared integral 8 mm fixed-cup extensions added in memory. Loose shell installation with valves absent. No production edit or print release.',
        'generator_sha256':sha(HERE/'build_concept.py'),'script_sha256':sha(__file__),
        'sweep_script_sha256':sha(HERE/'check_joint_motion.py'),
        'wall_manifest_sha256':sha(d/'manifest.json'),'wall_step_sha256':fm['files']['front-top.step'],
        'fixed_cups':[],'working':[],'rigid_installation':[],'tool_installation':[],
        'pusher_withdrawal':[],'guide_contact_witnesses':[]}
    def save():
        (HERE/'wall-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    def ycyl(x,z,d,y0,y1):
        return cq.Solid.makeCylinder(d/2,y1-y0,cq.Vector(x,y0,z),cq.Vector(0,1,0))
    floor=I['fixed_seat_floor_y'];r=I['spring_bore_d']/2
    extensions=[]
    for station in I['spring_stations']:
        x,z=station['x'],station['z']
        ring=ycyl(x,z,2*r+4,floor+1.9,floor+8).cut(ycyl(x,z,2*r,floor+1.8,floor+8.1))
        root=ring.intersect(wall)
        bore=ycyl(x,z,2*r-.02,floor+.01,floor+8-.01)
        floor_probe=ycyl(x,z,6,floor-.15,floor-.02)
        report['fixed_cups'].append({'x_mm':x,'extension_volume_mm3':ring.Volume(),
            'native_root_overlap_mm3':root.Volume(),'native_bore_overlap_mm3':bore.intersect(wall).Volume(),
            'floor_stock_missing_mm3':floor_probe.cut(wall).Volume()})
        extensions.append(ring)
    wall=wall.fuse(*extensions).clean()
    report['extended_wall']={'valid':wall.isValid(),'solids':len(wall.Solids()),'volume_mm3':wall.Volume()}
    assert wall.isValid() and len(wall.Solids())==1
    for label,dy in (('release',0),('connected',I['connected_offset_y']),('aft_limit',I['aft_limit_offset_y'])):
        for side,body in (('left',L),('right',R)):
            hit=body.translate((0,dy,0)).intersect(wall)
            row={'state':label,'side':side,'overlap_mm3':hit.Volume(),'hit_bounds':bounds(hit)}
            report['working'].append(row);print(json.dumps(row),flush=True)
    save()
    aft=I['aft_limit_offset_y'];stage=I['half_entry_staging_y']
    for side,body in ((-1,L),(1,Rrigid)):
        shift=-side*I['half_entry_shift_x'];shoulder=-side*I['half_entry_shoulder_inset_x']
        poses=[(shift,210,70),(shift,stage,70),(shift,stage,0),(shoulder,stage,0),(shoulder,aft,0),(0,aft,0)]
        # The held spring and flat pusher move together with this half.
        x=abs(I['spring_stations'][1]['x']);z=I['spring_stations'][1]['z']
        tip=I['spring_stations'][1]['bore_floor_y']-12.15
        tool=ycyl(x,z,6.3,tip-.6,tip).fuse(box((x-10,x),(tip-.6,tip),(z-.5,z+.5)))
        spring=ycyl(x,z,6.5,tip,I['spring_stations'][1]['bore_floor_y'])
        if side<0:tool=tool.mirror('YZ');spring=spring.mirror('YZ')
        held=tool.fuse(spring)
        for start,end in zip(poses,poses[1:]):
            row={'side':side,**swept_overlap(body,start,end,wall)}
            report['rigid_installation'].append(row);print(json.dumps(row),flush=True);save()
            toolrow={'side':side,**swept_overlap(held,start,end,wall)}
            report['tool_installation'].append(toolrow);print(json.dumps(toolrow),flush=True);save()
        # Withdraw the temporary pusher to the outer tee well, then lift it.
        withdraw=x-max(M['spec']['tee_xs'])
        path=[(0,aft,0),(-side*withdraw,aft,0),(-side*withdraw,aft,70)]
        moving=body.translate((0,aft,0))
        for start,end in zip(path,path[1:]):
            row={'side':side,**swept_overlap(tool,start,end,wall.fuse(moving))}
            report['pusher_withdrawal'].append(row);print(json.dumps(row),flush=True);save()
        # Opposed actual wall contact remains a geometric capture witness.
        xs=sorted((side*M['spec']['guide_inner_x'],side*I['grip_outer_x']))
        guides=wall.intersect(box(xs,(I['grip_rim_y'][0]-1,I['grip_back_y'][1]+aft+1),
                                 (I['printed_guide_body_z'][0]-1,I['printed_grip_rim_z'][1]+2)))
        for label,dy in (('release',0),('connected',I['connected_offset_y']),('aft_limit',aft)):
            posed=body.translate((0,dy,0))
            center=(0,sum(I['guide_body_y'])/2+dy,sum(I['printed_guide_body_z'])/2)
            for sign in (-1,1):
                hit=posed.rotate(center,(1,center[1],center[2]),sign*3).intersect(guides)
                report['guide_contact_witnesses'].append({'side':side,'state':label,
                    'rotation_about_x_deg':sign*3,'overlap_mm3':hit.Volume(),'hit_bounds':bounds(hit)})
        save()
    # The free wall is unloaded until the last 2 mm of the fore slide. Check
    # its complete nominal path first, then all deflections in that final
    # interval; applying 2.3 mm bend at the lowering station is not its route.
    fb=flexwall.fuse(lip).BoundingBox()
    report['nominal_flex_wall_installation']=[]
    inset=I['half_entry_shoulder_inset_x'];shift=I['half_entry_shift_x']
    poses=[(-shift,210,70),(-shift,stage,70),(-shift,stage,0),(-inset,stage,0),(-inset,aft,0),(0,aft,0)]
    for start,end in zip(poses,poses[1:]):
        report['nominal_flex_wall_installation'].append(swept_overlap(flexwall.fuse(lip),start,end,wall))
    swept_flex=box((fb.xmin-inset,fb.xmax),
                  (fb.ymin+aft,fb.ymax+aft+2+2.3),(fb.zmin,fb.zmax))
    hit=swept_flex.intersect(wall)
    report['flex_wall_full_fore_and_lateral_envelope']={'overlap_mm3':hit.Volume(),'hit_bounds':bounds(hit)}
    groups=('rigid_installation','tool_installation','pusher_withdrawal','nominal_flex_wall_installation')
    report['all_reported_native_clearance_readings_clear']=all(r['overlap_mm3']<1e-5 for r in report['working']) and all(
        r['max_prism_overlap_mm3']<1e-5 and r['initial_overlap_mm3']<1e-5 for key in groups for r in report[key]) and hit.Volume()<1e-5
    report['opposed_guide_contact_at_every_stop']=all(r['overlap_mm3']>1e-5 for r in report['guide_contact_witnesses'])
    report['limitations']=['Boundary-face enclosing boxes are conservative; any positive box reading needs native diagnosis.',
        'Guide contact at a prescribed fixed-center 3 degree rotation is not a stiffness or free-body angular-play measurement.',
        'Spring loading effort, flexible coil behavior, printed sliding fit and actual snap-wall elastic response remain unqualified.']
    save();print(json.dumps({'clear':report['all_reported_native_clearance_readings_clear'],'guide_contact':report['opposed_guide_contact_at_every_stop']}),flush=True)


if __name__=='__main__':main()
