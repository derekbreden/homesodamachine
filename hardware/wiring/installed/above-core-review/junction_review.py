"""Manual fine branch-body, rooted-well and wire-mouth study.

Read the explicit current physical/wiring cohort. Query geometry comes from the
same source stock, pocket and driver definitions; no BREP cache or CAD build runs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/manifold-layout')]
from hardware.wiring.installed._fine_contacts import (
    current_fine,fine_arguments,fine_overlap,junction_geometry,selected_hardware,
    production_tube_specs,cylinder_solid,frame_drain_datums)
HERE=Path(__file__).resolve().parent


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    fine_arguments(parser,ROOT)
    parser.add_argument('--only',nargs='+',help='Bounded junction names; default is all nine placed branches')
    parser.add_argument('--obstacles',nargs='+',help='Bounded existing physical/tool names')
    parser.add_argument('--output',type=Path,default=HERE/'junction-review.json')
    args=parser.parse_args(argv);context=current_fine(args)
    geometry=junction_geometry(context,args.only,include_holders=False);poses=geometry['poses'];layout=geometry['layout']
    names=list(poses)if not args.only else args.only
    if set(names)-set(poses):raise ValueError('Unknown source junction names')
    components=selected_hardware(context,poses)
    specs=production_tube_specs(context)
    tubes={}
    for name in specs:
        ref=context.resolve('tube-'+name);tubes[ref[1]]=ref
    for name,ref in geometry['drivers'].items():components['driver-'+name]=ref
    c14=layout.pose('c14-inlet');cx,cy,cz=c14['translation_mm']
    pitch=layout.specification()['rear_wall']['dry_openings']['c14']['mount_pitch_mm']
    for side in(-1,1):
        for label,radius,length,origin in(
            ('c14-outside-driver-',3.,30.,(cx+side*pitch/2.,cy,cz)),
            ('c14-full-insert-stock-',5.,10.25,(cx+side*pitch/2.,cy-3.25-10.25,cz))):
            name=label+str(side)
            components[name]=context.add_aux(name,cylinder_solid(radius,length,origin,(0.,1.,0.)),
                {'src':{'path':str(Path(__file__)),'sha256':context.digest(Path(__file__))},
                 'kind':'Existing nominal C14 access/insert-stock witness','radius_mm':radius,
                 'length_mm':length,'origin_mm':origin,'axis':(0.,1.,0.),'pose':c14})
    targets={**tubes,**components}
    if args.obstacles:
        unknown=set(args.obstacles)-set(targets)
        if unknown:raise ValueError('Unknown qualified obstacle: '+', '.join(sorted(unknown)))
        targets={name:targets[name]for name in args.obstacles}
    partsrows={};pairs=[];owners=[];entry_pairs=[];entry_owners=[];pocket_pairs=[];pocket_owners=[]
    for name in names:
        body=context.resolve(name);well=geometry['wells'][name]
        valid=not context.aux[well[1]].is_empty()
        partsrows[name]={'body_bounds_mm':context.bounds(body),'well_bounds_mm':context.bounds(well),
                         'well_valid':valid,'qualified_body':body[1],'qualified_parent':geometry['hosts'][name][1]}
        for label,own in((name,body),(name+'-well',well)):
            if label.endswith('-well')and not valid:continue
            for other,target in targets.items():
                if label.endswith('-well')and other.startswith('c14-full-insert-stock'):continue
                if fine_overlap(context.bounds(own),context.bounds(target)):
                    pairs.append((own,target));owners.append((label,other))
        pose=poses[name];width,depth,height,poles,rows=geometry['sizes'][pose['size']]
        for i in range(poles):
            count=poles//rows;row=i//count;slot=i%count
            local=(-width/2+(slot+.5)*width/count,depth/2,height*(row+.5)/rows)
            point=layout.point(pose,local);axis=layout.vector(pose['rotation'],(0.,1.,0.))
            length=4. if name in('wago-mana','wago-manb')else 8.
            lead=context.add_aux(name+'-mouth-'+str(i+1),cylinder_solid(1.5,length,point,axis),
                {'src':{'path':str(Path(__file__)),'sha256':context.digest(Path(__file__))},
                 'pose':pose,'port':i+1,'diameter_mm':3.,'length_mm':length,
                 'point_mm':point,'axis':axis,'kind':'Existing conservative wire-mouth witness'})
            for other,target in targets.items():
                if fine_overlap(context.bounds(lead),context.bounds(target)):
                    entry_pairs.append((lead,target));entry_owners.append((name,i+1,other))
        if pose['parent']=='back-top':
            pocket=geometry['pockets'][name]
            for other,target in targets.items():
                if other.startswith('c14-full-insert-stock')and fine_overlap(context.bounds(pocket),context.bounds(target)):
                    pocket_pairs.append((pocket,target));pocket_owners.append((name,other))
    hits=[];entryhits=[];pockethits=[];queries=0
    for(label,other),reading in zip(owners,context.commons(pairs)):
        queries+=reading['entry_common_count'];hit=reading['raw']
        if hit['volume_mm3']>.01:hits.append({'part':label,'obstacle':other,'volume_mm3':hit['volume_mm3'],
                                            'bounds_mm':hit['min']+hit['max']})
    for(name,port,other),reading in zip(entry_owners,context.commons(entry_pairs)):
        queries+=reading['entry_common_count'];hit=reading['raw']
        if hit['volume_mm3']>.01:entryhits.append({'part':name,'port':port,'obstacle':other,
                                                 'volume_mm3':hit['volume_mm3'],'bounds_mm':hit['min']+hit['max']})
    for(name,other),reading in zip(pocket_owners,context.commons(pocket_pairs)):
        queries+=reading['entry_common_count'];hit=reading['raw']
        if hit['volume_mm3']>.001:pockethits.append([name,other,hit['volume_mm3']])
    version={'front_mouth_witness_mm':{'length':4.,'diameter':3.},
             'rear_core_mouth_witness_mm':{'length':8.,'diameter':3.},
             'fixed_parts':sorted(components),'tube_names':sorted(tubes),
             'selected_obstacles':sorted(targets),'c14_insert_stock_removed_by_pockets':pockethits,
             'parts':partsrows,'intersections':hits,'wire_entry_intersections':entryhits}
    record={'final-staggered':version,
        'scope':'Current fine WAGO bodies, actual rooted-well material inside source stock/cutters, conservative source wire-mouth/driver witnesses, selected and retained fine hardware and actual routed tube bodies. No physical or wire-packing qualification.',
        'actual_poses':poses,'actual_pose_sha256':hashlib.sha256(json.dumps(poses,sort_keys=True).encode()).hexdigest(),
        'native_tube_sha256':hashlib.sha256(json.dumps(specs,sort_keys=True).encode()).hexdigest(),
        'frame_drain_datums':frame_drain_datums(context),
        'fine_boolean_count':queries,'front_actual_conductor_od_mm':1.7,
        'source_sha256':{str(Path(__file__).relative_to(ROOT)):context.digest(Path(__file__))},
        'fine_binding':context.finish(),'review_complete':True,
        'geometrically_clear':not(hits or entryhits or pockethits or any(not row['well_valid']for row in partsrows.values()))}
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'junction_count':len(names),'fine_boolean_count':queries,
                      'geometrically_clear':record['geometrically_clear']}),flush=True)
    return record


if __name__=='__main__':main()
